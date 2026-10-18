"""Characterization tests, not readiness acceptance; defective receipts must reject."""
import copy
import unittest

from fee_evidence import EvidenceContradiction, quantity, measurements, require_reconciled
from investigate_fee_receipts import CASES, collect


class FeeOracleTests(unittest.TestCase):
    def sample(self, base=1_000_000_000, priority=1_000_000_000):
        # Independent hand-calculated 21,000 gas zero-value transaction fixture.
        price = min(3_000_000_000, base + priority)
        block_hash, parent_hash, tx_hash = "0x"+"11"*32, "0x"+"22"*32, "0x"+"33"*32
        return {
            "transaction":{"type":"0x2","value":"0x0","gas":hex(2_000_000),"maxFeePerGas":hex(3_000_000_000),
                "maxPriorityFeePerGas":hex(priority),"gasPrice":hex(price),"hash":tx_hash,"blockHash":block_hash,"blockNumber":"0x2"},
            "receipt":{"status":"0x1","gasUsed":hex(21000),"effectiveGasPrice":hex(price),"transactionHash":tx_hash,"blockHash":block_hash,"blockNumber":"0x2"},
            "block":{"hash":block_hash,"parentHash":parent_hash,"number":"0x2","baseFeePerGas":hex(base),"transactions":[tx_hash]},
            "balanceBefore":hex(48*10**15),"balanceAfter":hex(48*10**15-21000*price),
            "parentNumber":"0x1","parentHash":parent_hash,"blockReceiptEffectiveGasPrice":hex(price),
            "witnessGasPrice":hex(price),"witnessBaseFee":hex(base),
        }

    def test_exact_eip1559_boundary_values(self):
        for base, priority, expected in ((0,10**9,10**9),(10**9,10**9,2*10**9),
            (2*10**9-1,10**9,3*10**9-1),(2*10**9,10**9,3*10**9),
            (2*10**9+1,10**9,3*10**9),(2_625_000_000,10**9,3*10**9),
            (3*10**9,10**9,3*10**9),(3*10**9,0,3*10**9)):
            with self.subTest(base=base,priority=priority):
                v=require_reconciled(self.sample(base,priority))
                self.assertEqual(v["expectedPrice"],expected)
                self.assertEqual(v["actualDebit"],21000*expected)

    def test_one_wei_receipt_difference_is_not_tolerated(self):
        e=self.sample();e["receipt"]["effectiveGasPrice"]=hex(2*10**9+1)
        with self.assertRaises(EvidenceContradiction):require_reconciled(e)

    def test_cap_clamping_is_diagnostic_not_a_receipt_repair(self):
        e=self.sample(2_625_000_000);bad=hex(3_625_000_000)
        e["receipt"]["effectiveGasPrice"]=bad;e["transaction"]["gasPrice"]=bad;e["blockReceiptEffectiveGasPrice"]=bad
        original=copy.deepcopy(e)
        with self.assertRaises(EvidenceContradiction):require_reconciled(e)
        self.assertEqual(e,original)
        self.assertEqual(measurements(e)["actualDebit"],63_000_000_000_000)

    def test_mutated_rpc_balance_execution_and_canonical_fields_fail(self):
        mutations=(("receipt","gasUsed","0x1"),("receipt","effectiveGasPrice","0x0"),
            ("transaction","gasPrice","0x0"),("transaction","type","0x0"),("transaction","maxFeePerGas",hex(3*10**9+1)),
            ("transaction","maxPriorityFeePerGas",hex(10**9+1)),("transaction","value","0x1"),
            ("transaction","hash","0x"+"44"*32),("receipt","blockHash","0x"+"44"*32),
            ("block","baseFeePerGas",hex(3*10**9+1)),("block","parentHash","0x"+"44"*32))
        for section,field,value in mutations:
            e=self.sample();e[section][field]=value
            with self.subTest(section=section,field=field):
                with self.assertRaises(EvidenceContradiction):require_reconciled(e)
        for field in ("balanceAfter","witnessGasPrice","witnessBaseFee","blockReceiptEffectiveGasPrice","parentNumber"):
            e=self.sample();e[field]="0x0"
            with self.subTest(field=field):
                with self.assertRaises(EvidenceContradiction):require_reconciled(e)

    def test_noncanonical_or_oversized_integer_rejection(self):
        for value in (True,1,1.1,"1","0x00","0xA","-0x1",hex(2**256)):
            with self.subTest(value=value):
                with self.assertRaises(EvidenceContradiction):quantity(value)

    def test_reverted_transaction_still_requires_exact_fee_reconciliation(self):
        e=self.sample();e["receipt"]["status"]="0x0";e.pop("witnessGasPrice");e.pop("witnessBaseFee")
        require_reconciled(e)
        e["balanceAfter"]=e["balanceBefore"]
        with self.assertRaises(EvidenceContradiction):require_reconciled(e)


class PinnedAnvilCharacterizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.evidence=collect(2)
        cls.results=cls.evidence["results"]

    def test_two_clean_runs_for_every_case(self):
        self.assertEqual(len(self.results),2*len(CASES))
        for case in CASES:
            rows=[r for r in self.results if r["case"]==case[0]]
            self.assertEqual(len(rows),2)
            if "transaction" in rows[0]:
                self.assertNotEqual(rows[0]["transaction"]["from"],rows[1]["transaction"]["from"])
                self.assertNotEqual(rows[0]["transaction"]["hash"],rows[1]["transaction"]["hash"])
                self.assertEqual(rows[0]["measurements"],rows[1]["measurements"])

    def test_raw_receipt_transaction_and_block_receipt_share_missing_cap(self):
        for r in self.results:
            if r["receipt"] is None:continue
            uncapped=r["requestedBaseFee"]+r["requestedPriorityFee"]
            self.assertEqual(quantity(r["receipt"]["effectiveGasPrice"]),uncapped)
            self.assertEqual(quantity(r["transaction"]["gasPrice"]),uncapped)
            self.assertEqual(quantity(r["blockReceiptEffectiveGasPrice"]),uncapped)

    def test_execution_opcode_and_wallet_debit_respect_signed_cap(self):
        for r in self.results:
            if r["receipt"] is None:continue
            v=r["measurements"]
            self.assertEqual(v["actualDebit"],v["expectedFee"])
            self.assertLessEqual(v["actualDebit"],v["maxReservation"])
            if r["receipt"]["status"]=="0x1":
                self.assertEqual(quantity(r["witnessGasPrice"]),v["expectedPrice"])
                self.assertEqual(quantity(r["witnessBaseFee"]),r["requestedBaseFee"])

    def test_every_contradiction_remains_blocking(self):
        blocked=[r for r in self.results if r["classification"].startswith("BLOCKED")]
        self.assertEqual(len(blocked),8)
        for r in blocked:
            with self.assertRaises(EvidenceContradiction):require_reconciled(r)
        self.assertEqual(sum(r["classification"]=="reconciled" for r in self.results),12)

    def test_above_cap_not_included_has_no_wallet_debit(self):
        rows=[r for r in self.results if r["case"]=="above-fee-cap"]
        self.assertEqual(len(rows),2)
        for r in rows:
            self.assertEqual(r["classification"],"not included")
            self.assertIsNone(r["receipt"])
            self.assertEqual(r["balanceBefore"],r["balanceAfter"])
            self.assertEqual(r["nonceAfter"],"0x0")

    def test_reverts_are_not_exempt_from_the_bug(self):
        for r in self.results:
            if r["case"]=="revert-clamped":
                self.assertEqual(r["receipt"]["status"],"0x0")
                self.assertGreater(r["measurements"]["receiptOverstatement"],0)
                self.assertGreater(r["measurements"]["actualDebit"],0)

    def test_one_wei_above_clamp_fails_without_rounding(self):
        for r in self.results:
            if r["case"]=="above-tip-clamp":
                self.assertEqual(r["measurements"]["reportedPrice"]-r["measurements"]["expectedPrice"],1)
                self.assertEqual(r["measurements"]["receiptOverstatement"],quantity(r["receipt"]["gasUsed"]))

    def test_cleanup_and_original_caps_unchanged(self):
        for r in self.results:
            self.assertTrue(r["childrenStopped"])
            if r["receipt"] is not None:
                self.assertEqual(quantity(r["transaction"]["maxFeePerGas"]),3*10**9)
                self.assertLessEqual(quantity(r["transaction"]["maxPriorityFeePerGas"]),10**9)
                self.assertEqual(quantity(r["transaction"]["gas"]),2_000_000)


if __name__=="__main__":
    unittest.main()
