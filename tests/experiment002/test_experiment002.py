"""Independent negative oracles and disposable local E002 integration; no keys persisted."""

import copy
import json
import os
import signal
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, Mock
import requests
from eth_account import Account
from web3 import Web3
from genesis_experiment.protocol import (
    Rejected as ChainRejected,
    Inconclusive as ChainInconclusive,
)
from genesis_experiment002.protocol import (
    Signing,
    Rejected,
    Inconclusive,
    SERVICE,
    POLICY,
    PRICE,
    TYPES,
    normalize,
    wire,
    tuple_for,
    encode,
    decode,
    read,
    write,
)
from genesis_experiment002.chain import Budget, Chain, GAS, FEE, PRIORITY, RESERVATION
from genesis_experiment002.runner import Fixture, run as execute, ROOT


RUN_EVIDENCE = []


def run(*args, **kwargs):
    result = execute(*args, **kwargs)
    RUN_EVIDENCE.append(result)
    return result


def tearDownModule():
    if RUN_EVIDENCE:
        folder = ROOT / "internal/task012"
        folder.mkdir(exist_ok=True)
        (folder / "agent-runs.json").write_text(
            json.dumps(RUN_EVIDENCE, indent=2, sort_keys=True) + "\n"
        )


class Codec002Tests(unittest.TestCase):
    def setUp(self):
        self.a = Account.create()
        self.b = Account.create()
        self.s = Signing("0x" + "11" * 20, "0x" + "22" * 32)
        self.t = wire(
            "Terms",
            requester=self.a.address,
            provider=self.b.address,
            serviceId=SERVICE,
            policyId=POLICY,
            x=7,
            y=11,
            price=PRICE,
            fundBefore=1120,
            claimBefore=1300,
            salt="0x" + "33" * 32,
            runId=self.s.run_id,
        )

    def test_exact_upfront_envelope_and_no_acceptance_schema(self):
        e = self.s.envelope(
            "terms",
            self.t,
            {
                "requester": self.s.sign(self.a, "Terms", self.t),
                "provider": self.s.sign(self.b, "Terms", self.t),
            },
        )
        self.s.open(
            e, "terms", {"requester": self.a.address, "provider": self.b.address}
        )
        self.assertNotIn("Acceptance", TYPES)
        for change in (
            {**e, "domain": {}},
            {**e, "kind": "termsProposal"},
            {**e, "signatures": {"requester": e["signatures"]["requester"]}},
        ):
            with self.subTest(change=list(change)):
                with self.assertRaises(Rejected):
                    self.s.open(
                        change,
                        "terms",
                        {"requester": self.a.address, "provider": self.b.address},
                    )

    def test_all_terms_fields_tamper(self):
        sig = self.s.sign(self.a, "Terms", self.t)
        for field in TYPES["Terms"]:
            m = dict(self.t)
            name = field["name"]
            typ = field["type"]
            m[name] = (
                str(int(m[name]) + 1)
                if typ.startswith("uint")
                else (
                    self.b.address.lower()
                    if name == "requester"
                    else "0x" + "55" * (20 if typ == "address" else 32)
                )
            )
            with self.subTest(field=name):
                with self.assertRaises(Rejected):
                    self.s.verify("Terms", m, sig, self.a.address)

    def test_signature_lengths_high_s_v_and_wrong_identity(self):
        good = self.s.sign(self.a, "Terms", self.t)
        raw = bytes.fromhex(good[2:])
        n = int("fffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141", 16)
        high = (
            raw[:32]
            + (n - int.from_bytes(raw[32:64], "big")).to_bytes(32, "big")
            + bytes([55 - raw[64]])
        )
        for sig in (
            "0x" + "00" * 65,
            good[:-2],
            good + "00",
            "0x" + high.hex(),
            "0x" + (raw[:64] + b"\x00").hex(),
        ):
            with self.subTest(size=len(sig)):
                with self.assertRaises(Rejected):
                    self.s.verify("Terms", self.t, sig, self.a.address)
        with self.assertRaises(Rejected):
            self.s.verify("Terms", self.t, good, self.b.address)

    def test_domain_chain_contract_version_name_and_run(self):
        sig = self.s.sign(self.a, "Terms", self.t)
        for field, val in (
            ("chainId", "31338"),
            ("verifyingContract", "0x" + "aa" * 20),
            ("name", "GenesisExperiment001"),
            ("version", "2"),
        ):
            other = Signing("0x" + "11" * 20, self.s.run_id)
            other.domain[field] = val
            with self.subTest(field=field):
                with self.assertRaises(Rejected):
                    other.verify("Terms", self.t, sig, self.a.address)
        other = Signing("0x" + "11" * 20, "0x" + "44" * 32)
        with self.assertRaises(Rejected):
            other.verify("Terms", self.t, sig, self.a.address)

    def test_wire_scalar_boundaries_and_unknown_fields(self):
        for value in (True, 1, 1.2, "01", "-1", str(2**64), "1e3", ""):
            with self.subTest(value=value):
                with self.assertRaises(Rejected):
                    normalize("Terms", {**self.t, "x": value})
        for m in (
            {**self.t, "unexpected": True},
            {**self.t, "price": {}},
            {**self.t, "runId": self.s.run_id.upper()},
        ):
            with self.assertRaises(Rejected):
                normalize("Terms", m)
        self.assertEqual(
            normalize("Terms", {**self.t, "x": str(2**64 - 1)})["x"], 2**64 - 1
        )

    def test_oversize_truncation_duplicate_json_and_nonregular_files(self):
        import time
        from genesis_experiment002.protocol import wait

        with self.assertRaises(Inconclusive):
            wait(
                ROOT / "internal/task012/nonexistent-message.json", time.monotonic() - 1
            )
        for raw in (b"x" * 16385, b'{"a":1,"a":2}', b'{"a":', b'{"a":NaN}'):
            with self.assertRaises(Rejected):
                decode(raw)
        with tempfile.TemporaryDirectory(dir=ROOT / "internal") as d:
            p = Path(d) / "message.json"
            write(p, self.t)
            with self.assertRaises(Rejected):
                write(p, self.t)
            self.assertEqual(read(p), self.t)
            fifo = Path(d) / "fifo"
            os.mkfifo(fifo)
            with self.assertRaises(Rejected):
                read(fifo)
            link = Path(d) / "link"
            link.symlink_to(p)
            with self.assertRaises(Rejected):
                read(link)

    def test_public_frozen_vectors(self):
        v = json.loads(
            (ROOT / "docs/experiments/EXPERIMENT_002_SIGNING_VECTORS.json").read_text()
        )
        for f in v["fixtures"]:
            for key, kind in (
                ("terms", "Terms"),
                ("authorization", "Authorization"),
                ("claim", "Claim"),
            ):
                artifact = f[key]
                m = artifact["typedData"]["message"]
                self.assertEqual(self.s.digest(kind, m), artifact["digest"])
                for role, sig in artifact["signatures"].items():
                    self.s.verify(kind, m, sig, v[role])


class Budget002Tests(unittest.TestCase):
    def charge(self, b, **changes):
        args = dict(
            method="fund" if b.role == "requester" else "claim",
            value=PRICE if b.role == "requester" else 0,
            principal=PRICE,
            balance=10**18,
        )
        args.update(changes)
        b.charge(**args)

    def test_exact_gas_fee_priority_ceiling(self):
        b = Budget("requester")
        self.charge(b)
        self.assertEqual(b.reserved, RESERVATION)

    def test_over_gas_fee_priority_and_nonintegers(self):
        for changes in (
            {"gas": GAS + 1},
            {"fee": FEE + 1},
            {"priority": PRIORITY + 1},
            {"fee": 0, "priority": 1},
            {"gas": 0},
            {"gas": True},
            {"value": PRICE + 1},
            {"principal": 10**15 + 1},
            {"method": "transfer"},
        ):
            b = Budget("requester")
            with self.subTest(changes=changes):
                with self.assertRaises(ChainRejected):
                    self.charge(b, **changes)
                self.assertEqual(b.used, 0)

    def test_insufficient_balance_one_wei_and_exact(self):
        b = Budget("requester")
        with self.assertRaises(ChainRejected):
            self.charge(b, balance=PRICE + RESERVATION - 1)
        self.charge(b, balance=PRICE + RESERVATION)

    def test_requester_closing_reserves_and_attempt_exhaustion(self):
        b = Budget("requester")
        for _ in range(6):
            self.charge(b)
        with self.assertRaises(ChainRejected):
            self.charge(b)
        self.charge(b, method="refund", value=0)
        self.charge(b, method="withdraw", value=0)
        self.assertEqual(b.reserved, 48 * 10**15)
        with self.assertRaises(ChainRejected):
            self.charge(b, method="withdraw", value=0)

    def test_provider_and_deployer_reserves(self):
        b = Budget("provider")
        for _ in range(7):
            self.charge(b)
        with self.assertRaises(ChainRejected):
            self.charge(b)
        self.charge(b, method="withdraw")
        d = Budget("deployer")
        self.charge(d, method="constructor")
        with self.assertRaises(ChainRejected):
            self.charge(d, method="constructor")
        self.assertEqual(d.reserved + b.reserved + 48 * 10**15, 102 * 10**15)

    def test_no_restoration_of_conservative_reservations(self):
        b = Budget("provider")
        self.charge(b)
        self.assertEqual(b.reserved, RESERVATION)
        b.reserved = 8 * RESERVATION  # inconsistent/corrupt budget also fails closed
        with self.assertRaises(ChainRejected):
            self.charge(b)


class Process002Tests(unittest.TestCase):
    def assert_completed(self, r, state):
        self.assertEqual(r["state"], state)
        self.assertTrue(r["childrenStopped"])
        self.assertLess(r["cleanupSeconds"], 15)
        self.assertNotEqual(
            r["agents"]["requester"]["pid"], r["agents"]["provider"]["pid"]
        )
        self.assertNotEqual(
            r["agents"]["requester"]["address"], r["agents"]["provider"]["address"]
        )
        self.assertLess(r["elapsedSeconds"], 120)
        for receipt in r["deployment"] + r.get("transactions", []):
            self.assertLessEqual(int(receipt["gasUsed"]), GAS)
            self.assertLessEqual(int(receipt["effectiveGasPrice"]), FEE)
            self.assertLessEqual(int(receipt["fee"]), RESERVATION)

    def test_two_fresh_success_runs_nominal_and_maximum(self):
        first = run()
        second = run(x=str(2**64 - 1), y=str(2**64 - 1))
        for r in (first, second):
            self.assert_completed(r, 2)
            self.assertEqual(r["value"], r["expectedValue"])
            self.assertEqual(r["providerCredit"], 0)
        self.assertNotEqual(first["manifest"]["runId"], second["manifest"]["runId"])

    def test_untrusted_claim_messages_reject_and_refund(self):
        from genesis_experiment002.runner import BAD_MESSAGES

        for scenario in BAD_MESSAGES:
            with self.subTest(scenario=scenario):
                r = run(scenario)
                self.assert_completed(r, 3)
                self.assertTrue(r["resultObserved"]["rejectedEvidence"])
                self.assertEqual(r["providerCredit"], 0)
                self.assertNotIn("claim", r["ledger"]["gasUsed"])

    def test_requester_refusal_cannot_veto(self):
        r = run("requester_refusal")
        self.assert_completed(r, 2)
        self.assertEqual(len(r["reports"]["requester"]["receipts"]), 1)

    def test_requester_offline_provider_collects(self):
        r = run("requester_offline")
        self.assert_completed(r, 2)
        self.assertNotIn("requester", r["reports"])

    def test_wrong_result_rejected_then_refunded(self):
        r = run("invalid_result")
        self.assert_completed(r, 3)
        self.assertTrue(r["reports"]["provider"]["rejected"])
        self.assertEqual(r["providerCredit"], 0)
        self.assertEqual(r["reports"]["provider"]["budget"], RESERVATION)
        self.assertEqual(r["ledger"]["inclusion"]["claim"][0]["status"], 0)
        self.assertEqual(r["ledger"]["attempts"]["provider"], 1)

    def test_provider_crash_before_computation_refunds(self):
        self.assert_completed(run("provider_crash_before"), 3)

    def test_provider_crash_after_computation_refunds(self):
        self.assert_completed(run("provider_crash_after"), 3)

    def test_public_disclosure_without_inclusion_is_not_fair_exchange(self):
        self.assert_completed(run("early_disclosure"), 3)

    def test_no_actor_remains_funded_until_resumed_refund(self):
        self.assert_completed(run("no_actor"), 3)

    def test_late_funding_does_not_guarantee_collection(self):
        self.assert_completed(run("late_funding"), 3)

    def test_requester_crash_before_funding_creates_no_obligation(self):
        self.assert_completed(run("requester_crash_before"), 0)

    def test_provider_crash_after_claim_leaves_exact_unwithdrawn_credit(self):
        r = run("provider_crash_after_claim")
        self.assert_completed(r, 2)
        self.assertEqual(r["providerCredit"], PRICE)
        self.assertEqual(r["totalCredits"], PRICE)

    def test_rollback_is_inconclusive_and_stops_signer(self):
        r = run("reorg")
        self.assert_completed(r, 1)
        self.assertEqual(r["outcome"], "inconclusive")


class Chain002Tests(unittest.TestCase):
    def setUp(self):
        self.fixture = Fixture().__enter__()
        self.addCleanup(self.fixture.__exit__, None, None, None)
        f = self.fixture
        self.a = Account.create()
        self.b = Account.create()
        f.rpc_call("anvil_setBalance", [self.a.address, hex(8 * RESERVATION + PRICE)])
        f.rpc_call("anvil_setBalance", [self.b.address, hex(8 * RESERVATION)])
        self.chain = Chain(f.rpc, self.a, f.artifact, "requester", PRICE, f.manifest)
        self.s = self.chain.signing
        now = f.w3.eth.get_block("latest")["timestamp"]
        self.t = wire(
            "Terms",
            requester=self.a.address,
            provider=self.b.address,
            serviceId=SERVICE,
            policyId=POLICY,
            x=7,
            y=11,
            price=PRICE,
            fundBefore=now + 120,
            claimBefore=now + 300,
            salt="0x" + "33" * 32,
            runId=f.run_id,
        )
        self.id = self.s.digest("Terms", self.t)
        self.auth = wire(
            "Authorization",
            requester=self.a.address,
            provider=self.b.address,
            agreementId=self.id,
            nonce=0,
            maxAmount=2 * PRICE,
            expiresAt=now + 120,
            runId=f.run_id,
        )

    def funding_function(self):
        return self.chain.contract.functions.fund(
            tuple_for("Terms", self.t),
            tuple_for("Authorization", self.auth),
            bytes.fromhex(self.s.sign(self.a, "Terms", self.t)[2:]),
            bytes.fromhex(self.s.sign(self.b, "Terms", self.t)[2:]),
            bytes.fromhex(self.s.sign(self.a, "Authorization", self.auth)[2:]),
        )

    def fund(self):
        return self.chain.transact(self.funding_function(), value=PRICE)

    def test_insufficient_wallet_refuses_before_transaction_signature_or_send(self):
        self.fixture.rpc_call(
            "anvil_setBalance", [self.a.address, hex(PRICE + RESERVATION - 1)]
        )
        with patch.object(
            self.a, "sign_transaction", wraps=self.a.sign_transaction
        ) as sign, patch.object(self.chain.w3.eth, "send_raw_transaction") as send:
            with self.assertRaises(ChainRejected):
                self.fund()
            sign.assert_not_called()
            send.assert_not_called()
        self.assertEqual(self.chain.record(self.id)[2], 0)

    def test_exhausted_budget_refuses_before_signature_or_send(self):
        self.chain.budget.used = 6
        with patch.object(
            self.a, "sign_transaction", wraps=self.a.sign_transaction
        ) as sign, patch.object(self.chain.w3.eth, "send_raw_transaction") as send:
            with self.assertRaises(ChainRejected):
                self.fund()
            sign.assert_not_called()
            send.assert_not_called()
        self.assertEqual(self.chain.record(self.id)[2], 0)

    def test_revert_charged_replay_and_no_nonce_restoration(self):
        self.fund()
        with self.assertRaises(ChainRejected):
            self.fund()
        self.assertEqual(self.chain.budget.reserved, 2 * RESERVATION)
        self.assertEqual(self.chain.record(self.id)[2], 1)
        self.assertEqual(self.chain.contract.functions.lockedPrincipal().call(), PRICE)

    def test_timeout_after_broadcast_reconciles_exact_hash(self):
        original = self.chain.w3.eth.send_raw_transaction

        def drop(raw):
            original(raw)
            raise requests.Timeout()

        with patch.object(self.chain.w3.eth, "send_raw_transaction", side_effect=drop):
            self.fund()
        self.assertEqual(self.chain.record(self.id)[2], 1)
        self.assertEqual(self.chain.submissions, 1)

    def test_timeout_before_broadcast_latches_unknown_and_blocks_retry(self):
        with patch.object(
            self.chain.w3.eth, "send_raw_transaction", side_effect=requests.Timeout
        ):
            with self.assertRaises(ChainInconclusive):
                self.fund()
        with patch.object(
            self.a, "sign_transaction", wraps=self.a.sign_transaction
        ) as sign:
            with self.assertRaises(ChainInconclusive):
                self.fund()
            sign.assert_not_called()
        self.assertEqual(self.chain.budget.reserved, RESERVATION)
        self.assertEqual(self.chain.record(self.id)[2], 0)

    def test_wrong_returned_hash_stops_even_if_mined(self):
        original = self.chain.w3.eth.send_raw_transaction

        def alter(raw):
            original(raw)
            return b"\xff" * 32

        with patch.object(self.chain.w3.eth, "send_raw_transaction", side_effect=alter):
            with self.assertRaises(ChainInconclusive):
                self.fund()
        self.assertIsNotNone(self.chain.pending_hash)
        self.assertEqual(self.chain.record(self.id)[2], 1)

    def test_mutated_event_and_receipt_rejected(self):
        receipt = self.fund()
        bad = dict(receipt)
        bad["blockHash"] = b"\xff" * 32
        with self.assertRaises(ChainInconclusive):
            self.chain.canonical_receipt(bad, receipt["transactionHash"])
        with self.assertRaises(ChainInconclusive):
            self.chain.check_event(receipt, "Funded", {"price": PRICE + 1})

    def test_snapshot_revert_invalidates_previous_evidence(self):
        snap = self.fixture.rpc_call("evm_snapshot", [])
        self.fund()
        self.fixture.rpc_call("evm_revert", [snap])
        with self.assertRaises(ChainInconclusive):
            self.chain.preflight()

    def test_wrong_code_and_run_stops_before_signing(self):
        self.fixture.rpc_call(
            "anvil_setCode", [self.fixture.manifest["contract"], "0x00"]
        )
        with patch.object(
            self.a, "sign_transaction", wraps=self.a.sign_transaction
        ) as sign:
            with self.assertRaises(ChainInconclusive):
                self.fund()
            sign.assert_not_called()

    def test_base_fee_spike_aborts_without_escalation(self):
        for fee in (0, 10**9, 2 * 10**9, 3 * 10**9, 3 * 10**9 + 1):
            with self.subTest(fee=fee):
                self.fixture.rpc_call("anvil_setNextBlockBaseFeePerGas", [hex(fee)])
                self.fixture.rpc_call("evm_mine", [])
                if fee > FEE:
                    with patch.object(
                        self.a, "sign_transaction", wraps=self.a.sign_transaction
                    ) as sign:
                        with self.assertRaises(ChainRejected):
                            self.chain.transact(
                                self.chain.contract.functions.revokeUnused(fee)
                            )
                        sign.assert_not_called()
                else:
                    r = self.chain.transact(
                        self.chain.contract.functions.revokeUnused(fee)
                    )
                    self.assertLessEqual(r["effectiveGasPrice"], FEE)

    def test_loopback_only_no_proxy_redirect_or_ccip(self):
        from genesis_experiment.chain import connect, LocalSession

        for url in (
            "https://127.0.0.1:8545",
            "http://localhost:8545",
            "http://example.com:8545",
            "http://127.0.0.1:8545/path",
        ):
            with self.assertRaises(ChainRejected):
                connect(url)
        self.assertFalse(self.chain.w3.provider.global_ccip_read_enabled)
        with patch.dict(os.environ, {"HTTPS_PROXY": "http://127.0.0.1:1"}):
            with self.assertRaises(ChainRejected):
                connect(self.fixture.rpc)


if __name__ == "__main__":
    unittest.main()
