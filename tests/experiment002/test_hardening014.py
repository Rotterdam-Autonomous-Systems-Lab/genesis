"""Conflicting observations, monotonic boundaries and controlled timing evidence."""

import copy
import json
import time
import unittest
from unittest.mock import patch
from genesis_experiment.protocol import Inconclusive, Rejected
from genesis_experiment002.chain import Chain, RESERVATION
from genesis_experiment002.limits import check_deadline
from genesis_experiment002.runner import ROOT, audit_ledger, run
import test_review013 as review


class EvidenceHardeningTests(unittest.TestCase):
    setUp = review.ReviewRegressions.setUp
    funding_function = review.ReviewRegressions.funding_function
    fund = review.ReviewRegressions.fund
    settle = review.ReviewRegressions.settle

    def test_conflicting_pinned_record_latches_signer(self):
        self.fund()
        good = self.chain.record(self.id)
        bad = copy.deepcopy(good)
        bad = list(bad)
        bad[2] = 0
        with patch.object(self.chain.contract.functions, "getRecord") as record:
            record.return_value.call.side_effect = [good, bad]
            with self.assertRaises(Inconclusive):
                self.chain.record(self.id)
        with patch.object(
            self.a, "sign_transaction", wraps=self.a.sign_transaction
        ) as sign:
            with self.assertRaises(Inconclusive):
                self.chain.transact(self.chain.contract.functions.revokeUnused(1))
            sign.assert_not_called()
        self.assertEqual(self.chain.budget.used, 1)

    def test_consistent_stale_terminal_record_rejected(self):
        b, _, _ = self.settle()
        bad = list(b.record(self.id))
        bad[2] = 1
        bad[3] = 0
        with patch.object(b.contract.functions, "getRecord") as record:
            record.return_value.call.return_value = bad
            with self.assertRaises(Inconclusive):
                b.record(self.id)
        self.assertTrue(b.halted)
        with patch.object(
            self.b, "sign_transaction", wraps=self.b.sign_transaction
        ) as sign:
            with self.assertRaises(Inconclusive):
                b.transact(b.contract.functions.withdraw())
            sign.assert_not_called()

    def test_conflicting_owner_snapshot_and_wrong_parties_reject(self):
        _, ready, config = self.settle()
        wrong = copy.deepcopy(ready)
        wrong["provider"]["address"] = self.a.address
        with self.assertRaises(Inconclusive):
            audit_ledger(self.fixture, wrong, self.id, config)
        original = self.fixture.contract.functions.credits
        calls = 0

        def changed(address):
            nonlocal calls
            calls += 1
            fn = original(address)
            if calls > 3:
                from unittest.mock import Mock

                return Mock(call=Mock(return_value=1))
            return fn

        with patch.object(
            self.fixture.contract.functions, "credits", side_effect=changed
        ):
            with self.assertRaises(Inconclusive):
                audit_ledger(self.fixture, ready, self.id, config)

    def test_block_receipt_fields_and_own_intent_mutations_reject(self):
        receipt = self.fund()
        for field in ("gasUsed", "status", "blockNumber", "transactionIndex"):
            bad = dict(receipt)
            bad[field] += 1
            with self.subTest(field=field), patch.object(
                self.chain.w3.eth, "get_block_receipts", return_value=[bad]
            ):
                with self.assertRaises(Inconclusive):
                    self.chain.canonical_receipt(receipt, receipt["transactionHash"])
        for field in ("nonce", "input"):
            tx = dict(self.chain.w3.eth.get_transaction(receipt["transactionHash"]))
            tx[field] = tx[field] + 1 if field == "nonce" else b"\x12\x34"
            with self.subTest(field=field), patch.object(
                self.chain.w3.eth, "get_transaction", return_value=tx
            ):
                with self.assertRaises(Inconclusive):
                    self.chain.canonical_receipt(receipt, receipt["transactionHash"])

    def test_rpc_finishing_at_deadline_stops_before_signing(self):
        clock = [time.monotonic()]
        original = self.chain.w3.provider.make_request

        def delayed(method, params):
            response = original(method, params)
            clock[0] = self.chain.deadline
            return response

        with patch("time.monotonic", side_effect=lambda: clock[0]), patch.object(
            self.chain.w3.provider, "make_request", side_effect=delayed
        ), patch.object(
            self.a, "sign_transaction", wraps=self.a.sign_transaction
        ) as sign:
            # Public onion mutation rebuilds Web3's cached RPC pipeline so the
            # injected transport delay actually executes inside the deadline layer.
            from web3.middleware.base import Web3Middleware

            self.chain.w3.middleware_onion.add(Web3Middleware)
            with self.assertRaises(Inconclusive):
                self.fund()
            sign.assert_not_called()
        self.assertTrue(self.chain.halted)
        self.assertEqual(self.chain.budget.used, 0)

    def test_expiry_during_build_keeps_reservation_but_never_signs(self):
        clock = [time.monotonic()]
        function = self.funding_function()
        original = function.build_transaction

        def delayed(params):
            result = original(params)
            clock[0] = self.chain.deadline
            return result

        with patch("time.monotonic", side_effect=lambda: clock[0]), patch.object(
            function, "build_transaction", side_effect=delayed
        ), patch.object(
            self.a, "sign_transaction", wraps=self.a.sign_transaction
        ) as sign:
            with self.assertRaises(Inconclusive):
                self.chain.transact(function, value=10**12)
            sign.assert_not_called()
        self.assertEqual(self.chain.budget.reserved, RESERVATION)
        self.assertEqual(self.chain.w3.eth.get_transaction_count(self.a.address), 0)

    def test_expiry_after_broadcast_retains_unknown_hash_and_stops(self):
        clock = [time.monotonic()]
        original = self.chain.w3.eth.send_raw_transaction

        def included(raw):
            digest = original(raw)
            clock[0] = self.chain.deadline
            return digest

        with patch("time.monotonic", side_effect=lambda: clock[0]), patch.object(
            self.chain.w3.eth, "send_raw_transaction", side_effect=included
        ):
            with self.assertRaises(Inconclusive):
                self.fund()
        self.assertIsNotNone(self.chain.pending_hash)
        self.assertTrue(self.chain.halted)
        self.assertEqual(
            self.fixture.contract.functions.getRecord(self.id).call()[2], 1
        )
        with patch.object(
            self.a, "sign_transaction", wraps=self.a.sign_transaction
        ) as sign:
            with self.assertRaises(Inconclusive):
                self.fund()
            sign.assert_not_called()

    def test_old_automatic_clock_delay_reproduces_funding_expiry(self):
        f = self.fixture
        f.advance(int(self.t["fundBefore"]) - 1)
        before = f.w3.eth.get_balance(self.a.address)
        time.sleep(1.1)  # deliberate bounded host scheduling delay, not a new timeout
        with self.assertRaises(Rejected):
            self.fund()
        receipt = self.chain.receipts[-1]
        observed = self.chain.observations[next(iter(self.chain.observations))]
        self.assertGreaterEqual(int(observed["timestamp"]), int(self.t["fundBefore"]))
        self.assertEqual(receipt["status"], 0)
        self.assertEqual(self.chain.record(self.id)[2], 0)
        self.assertEqual(
            before - f.w3.eth.get_balance(self.a.address), int(observed["fee"])
        )
        folder = ROOT / "internal/task014"
        folder.mkdir(exist_ok=True)
        (folder / "old-clock-probe.json").write_text(
            json.dumps(
                {
                    "profile": f.manifest["nodeCommit"],
                    "hardfork": "cancun",
                    "mode": "old-auto-delayed",
                    "delaySeconds": 1.1,
                    "fundBefore": self.t["fundBefore"],
                    "claimBefore": self.t["claimBefore"],
                    "receipt": observed,
                    "state": 0,
                    "nonceConsumed": False,
                    "reservedFees": self.chain.budget.reserved,
                },
                indent=2,
            )
            + "\n"
        )


class DeadlineAndTimingTests(unittest.TestCase):
    def test_expected_error_barrier_publication_race_is_observed(self):
        from pathlib import Path
        from genesis_experiment002.runner import Fixture
        from genesis_experiment002.protocol import write

        with Fixture() as f:
            target = f.folder / "provider-error.json"
            write(target, {"classification": "Inconclusive"})
            original = Path.exists
            calls = 0

            def interleaved(path):
                nonlocal calls
                if path == target:
                    calls += 1
                    if calls == 1:
                        return False
                return original(path)

            with patch.object(Path, "exists", new=interleaved):
                self.assertEqual(f.wait(target.name)["classification"], "Inconclusive")

    def test_monotonic_exact_boundary_and_signature_deadline(self):
        from genesis_experiment002.protocol import Signing
        from eth_account import Account

        with patch("time.monotonic", return_value=100):
            check_deadline(100.001)
            for value in (100, 99.999, float("nan"), float("inf"), True):
                with self.assertRaises(Inconclusive):
                    check_deadline(value)
            signing = Signing("0x" + "11" * 20, "0x" + "22" * 32, deadline=100)
            account = Account.create()
            with patch.object(
                account, "sign_message", wraps=account.sign_message
            ) as sign:
                with self.assertRaises(Inconclusive):
                    signing.sign(account, "Terms", {})
                sign.assert_not_called()
        clock = [99.0]

        def late_encoding(*args):
            clock[0] = 100.0
            return None

        with patch("time.monotonic", side_effect=lambda: clock[0]), patch.object(
            signing, "typed", side_effect=late_encoding
        ), patch.object(account, "sign_message", wraps=account.sign_message) as sign:
            with self.assertRaises(Inconclusive):
                signing.sign(account, "Terms", {})
            sign.assert_not_called()

    def test_controlled_last_valid_inclusion_repeatability(self):
        evidence = []
        for _ in range(2):
            r = run("late_funding")
            self.assertEqual(r["state"], 3)
            self.assertEqual(r["fundingSlack"], 2)
            self.assertEqual(r["ledger"]["inclusion"]["fund"][0]["status"], 1)
            self.assertEqual(r["ledger"]["inclusion"]["claim"][0]["status"], 0)
            self.assertTrue(r["childrenStopped"])
            evidence.append(r)
        folder = ROOT / "internal/task014"
        folder.mkdir(exist_ok=True)
        (folder / "controlled-runs.json").write_text(
            json.dumps(evidence, indent=2, sort_keys=True) + "\n"
        )


if __name__ == "__main__":
    unittest.main()
