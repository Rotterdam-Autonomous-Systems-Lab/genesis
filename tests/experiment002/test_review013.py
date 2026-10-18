"""Task 014 fail-closed regressions retaining every Task 013 fault scenario."""

import json
import time
import unittest
from unittest.mock import Mock, patch
from web3 import Web3
from web3.exceptions import ContractLogicError
from genesis_experiment.protocol import Inconclusive, Rejected
from genesis_experiment002.chain import Chain, RESERVATION
from genesis_experiment002.protocol import PRICE
from genesis_experiment002.protocol import wire, tuple_for, write
from genesis_experiment002.runner import ROOT, audit_ledger
import test_experiment002 as fixtures


class ReviewRegressions(unittest.TestCase):
    # Reuse only disposable setup/signing; all review expectations are new.
    setUp = fixtures.Chain002Tests.setUp
    funding_function = fixtures.Chain002Tests.funding_function
    fund = fixtures.Chain002Tests.fund

    def settle(self):
        self.fund()
        b = Chain(
            self.fixture.rpc,
            self.b,
            self.fixture.artifact,
            "provider",
            PRICE,
            self.fixture.manifest,
        )
        c = wire(
            "Claim",
            requester=self.a.address,
            provider=self.b.address,
            agreementId=self.id,
            authorizationNonce=0,
            value=18,
            runId=self.s.run_id,
        )
        function = b.contract.functions.claim(
            tuple_for("Claim", c), bytes.fromhex(self.s.sign(self.b, "Claim", c)[2:])
        )
        b.transact(function)
        write(self.fixture.folder / "terms.json", {"message": self.t})
        ready = {
            "requester": {"address": self.a.address},
            "provider": {"address": self.b.address},
        }
        config = {"x": "7", "y": "11", "claimBefore": int(self.t["claimBefore"])}
        return b, ready, config

    def test_R013_01_swapped_credit_owners_and_states_are_rejected(self):
        b, ready, config = self.settle()
        actual = self.fixture.contract.functions.credits
        self.assertEqual(actual(self.a.address).call(), 0)
        self.assertEqual(actual(self.b.address).call(), PRICE)
        audit_ledger(self.fixture, ready, self.id, config)  # valid control

        def swapped(address):
            # Preserve total liabilities and every real wallet/receipt/state.
            return Mock(
                call=Mock(return_value=PRICE if address == self.a.address else 0)
            )

        with patch.object(
            self.fixture.contract.functions, "credits", side_effect=swapped
        ):
            with self.assertRaises(Inconclusive):
                audit_ledger(self.fixture, ready, self.id, config)
        # No real theft: honest ledger continues to credit only B.
        self.assertEqual(actual(self.a.address).call(), 0)
        self.assertEqual(actual(self.b.address).call(), PRICE)
        # A real Claim event/credit also fails to anchor the audit's terminal state.
        inconsistent = list(self.fixture.contract.functions.getRecord(self.id).call())
        inconsistent[2] = 1  # falsely report Funded after canonical Claim
        inconsistent[3] = 0
        with patch.object(self.fixture.contract.functions, "getRecord") as record:
            record.return_value.call.return_value = inconsistent
            with self.assertRaises(Inconclusive):
                audit_ledger(self.fixture, ready, self.id, config)
        self.assertEqual(
            self.fixture.contract.functions.getRecord(self.id).call()[2], 2
        )

    def test_R013_02_changed_current_receipt_fee_fields_are_rejected(self):
        receipt = self.fund()
        for field in ("gasUsed", "effectiveGasPrice"):
            with self.subTest(field=field):
                probe = Chain(
                    self.fixture.rpc,
                    self.a,
                    self.fixture.artifact,
                    "requester",
                    PRICE,
                    self.fixture.manifest,
                )
                probe.receipts = [receipt]
                bad = dict(receipt)
                bad[field] += 1
                with patch.object(
                    probe.w3.eth, "get_transaction_receipt", return_value=bad
                ):
                    with self.assertRaises(Inconclusive):
                        probe.preflight()
                # A later good response does not grant fresh signing permission.
                with patch.object(
                    self.a, "sign_transaction", wraps=self.a.sign_transaction
                ) as sign, patch.object(probe.w3.eth, "send_raw_transaction") as send:
                    with self.assertRaises(Inconclusive):
                        probe.transact(probe.contract.functions.revokeUnused(1))
                    sign.assert_not_called()
                    send.assert_not_called()
                self.assertTrue(probe.halted)
                self.assertEqual(probe.budget.used, 0)

    def test_R013_02_wrong_transaction_identity_is_rejected(self):
        receipt = self.fund()
        for field in ("hash", "blockNumber"):
            with self.subTest(field=field):
                tx = dict(self.chain.w3.eth.get_transaction(receipt["transactionHash"]))
                tx[field] = b"\xff" * 32 if field == "hash" else tx[field] + 1
                with patch.object(
                    self.chain.w3.eth, "get_transaction", return_value=tx
                ):
                    with self.assertRaises(Inconclusive):
                        self.chain.canonical_receipt(
                            receipt, receipt["transactionHash"]
                        )

    def test_R013_03_ready_barrier_and_signer_check_wall_deadline(self):
        barrier = self.fixture.folder / "review-ready.json"
        write(barrier, {})
        with patch("time.monotonic", return_value=time.monotonic() + 121):
            with self.assertRaises(Inconclusive):
                self.fixture.guard()
            with self.assertRaises(Inconclusive):
                self.fixture.wait(barrier.name)
            with patch.object(
                self.a, "sign_transaction", wraps=self.a.sign_transaction
            ) as sign:
                with self.assertRaises(Inconclusive):
                    self.fund()
                sign.assert_not_called()
        self.assertEqual(self.chain.record(self.id)[2], 0)
        self.assertEqual(self.chain.budget.used, 0)

    def test_R013_04_last_second_funding_can_expire_at_inclusion(self):
        self.fixture.advance(int(self.t["fundBefore"]) - 1)
        self.assertEqual(
            self.fixture.w3.eth.get_block("latest")["timestamp"],
            int(self.t["fundBefore"]) - 1,
        )
        # Deterministic controlled inclusion, not proof of the failed CI's timestamp.
        self.fixture.rpc_call("evm_setNextBlockTimestamp", [int(self.t["fundBefore"])])
        with self.assertRaises(Rejected):
            self.fund()
        receipt = self.chain.receipts[-1]
        self.assertEqual(receipt["status"], 0)
        self.assertEqual(
            self.fixture.w3.eth.get_block(receipt["blockNumber"])["timestamp"],
            int(self.t["fundBefore"]),
        )
        self.assertEqual(self.chain.record(self.id)[2], 0)
        self.assertEqual(
            self.fixture.contract.functions.nonceStatus(self.a.address, 0).call(), 0
        )
        self.assertEqual(self.fixture.contract.functions.lockedPrincipal().call(), 0)
        self.assertEqual(self.chain.budget.reserved, RESERVATION)

    def test_contract_rejects_copied_claim_wrong_result_and_duplicate(self):
        self.fund()
        c = wire(
            "Claim",
            requester=self.a.address,
            provider=self.b.address,
            agreementId=self.id,
            authorizationNonce=0,
            value=18,
            runId=self.s.run_id,
        )

        def claim(value):
            message = {**c, "value": str(value)}
            return self.fixture.contract.functions.claim(
                tuple_for("Claim", message),
                bytes.fromhex(self.s.sign(self.b, "Claim", message)[2:]),
            )

        with self.assertRaises(ContractLogicError):
            claim(18).call({"from": self.a.address})
        with self.assertRaises(ContractLogicError):
            claim(19).call({"from": self.b.address})
        self.assertEqual(self.chain.record(self.id)[2], 1)
        b = Chain(
            self.fixture.rpc,
            self.b,
            self.fixture.artifact,
            "provider",
            PRICE,
            self.fixture.manifest,
        )
        b.transact(claim(18))
        with self.assertRaises(ContractLogicError):
            claim(18).call({"from": self.b.address})
        self.assertEqual(self.chain.record(self.id)[2], 2)
        self.assertEqual(
            self.fixture.contract.functions.credits(self.b.address).call(), PRICE
        )


class ArchivedEvidenceReview(unittest.TestCase):
    def test_public_archive_arithmetic_and_limits(self):
        runs = json.loads(
            (
                ROOT / "research/experiments/experiment002/task012-agent-runs.json"
            ).read_text()
        )
        self.assertEqual(len(runs), 18)
        for r in runs:
            with self.subTest(scenario=r["scenario"]):
                self.assertTrue(r["childrenStopped"])
                self.assertLess(r["elapsedSeconds"], 120)
                self.assertLess(r["cleanupSeconds"], 15)
                self.assertEqual(
                    r["manifest"]["nodeCommit"],
                    "b272ce3366987406406e9eb1b82596653a3ad628",
                )
                self.assertEqual(r["manifest"]["hardfork"], "cancun")
                for receipt in r["deployment"] + r.get("transactions", []):
                    self.assertLessEqual(int(receipt["gasUsed"]), 2_000_000)
                    self.assertLessEqual(
                        int(receipt["effectiveGasPrice"]), 3_000_000_000
                    )
                    self.assertEqual(
                        int(receipt["fee"]),
                        int(receipt["gasUsed"]) * int(receipt["effectiveGasPrice"]),
                    )
                if "ledger" not in r:
                    self.assertIn(r["outcome"], ("unfunded", "inconclusive"))
                    continue
                ledger = r["ledger"]
                self.assertEqual(ledger["principalFundings"], 1)
                for role, ceiling in (
                    ("deployer", 1),
                    ("requester", 8),
                    ("provider", 8),
                ):
                    self.assertLessEqual(ledger["attempts"][role], ceiling)
                    self.assertEqual(
                        ledger["reservedFees"][role],
                        ledger["attempts"][role] * 6_000_000_000_000_000,
                    )
                    self.assertLessEqual(
                        ledger["fees"][role], ledger["reservedFees"][role]
                    )
                supply = 102_000_000_000_000_000 + 1_000_000_000_000
                outstanding = r["lockedPrincipal"] + r["totalCredits"]
                self.assertEqual(
                    supply - sum(ledger["balances"].values()) - outstanding,
                    sum(ledger["fees"].values()),
                )
                if r["outcome"] == "settled":
                    self.assertEqual(r["value"], r["expectedValue"])
                    self.assertEqual(r["state"], 2)
                else:
                    self.assertEqual(r["state"], 3)
                    self.assertEqual(r["providerCredit"], 0)


if __name__ == "__main__":
    unittest.main()
