"""Targeted independent fee, signing and boundary mutations on verified Cancun."""

import copy
import os
import unittest
from unittest.mock import patch
from web3 import Web3
from genesis_experiment.protocol import Rejected, Inconclusive
from genesis_experiment002.protocol import (
    TYPES,
    wire,
    tuple_for,
    Rejected as WireRejected,
)
from genesis_experiment002.chain import Chain
from genesis_experiment002.protocol import PRICE
from genesis_experiment002.runner import Fixture, run
import test_experiment002 as baseline


class SigningSecurityTests(unittest.TestCase):
    setUp = baseline.Codec002Tests.setUp

    def test_every_authorization_claim_advertisement_field_mutation(self):
        messages = {
            "Authorization": wire(
                "Authorization",
                requester=self.a.address,
                provider=self.b.address,
                agreementId=self.s.digest("Terms", self.t),
                nonce=0,
                maxAmount=2 * PRICE,
                expiresAt=1120,
                runId=self.s.run_id,
            ),
            "Claim": wire(
                "Claim",
                requester=self.a.address,
                provider=self.b.address,
                agreementId=self.s.digest("Terms", self.t),
                authorizationNonce=0,
                value=18,
                runId=self.s.run_id,
            ),
            "Advertisement": wire(
                "Advertisement",
                provider=self.b.address,
                serviceId=self.t["serviceId"],
                policyId=self.t["policyId"],
                price=PRICE,
                offerExpiresAt=1120,
                runId=self.s.run_id,
            ),
        }
        for kind, message in messages.items():
            signature = self.s.sign(self.a, kind, message)
            for field in TYPES[kind]:
                changed = dict(message)
                name = field["name"]
                typ = field["type"]
                changed[name] = (
                    str(int(changed[name]) + 1)
                    if typ.startswith("uint")
                    else "0x" + "66" * (20 if typ == "address" else 32)
                )
                with self.subTest(kind=kind, field=name):
                    with self.assertRaises(WireRejected):
                        self.s.verify(kind, changed, signature, self.a.address)


class LedgerSecurityTests(unittest.TestCase):
    setUp = baseline.Chain002Tests.setUp
    funding_function = baseline.Chain002Tests.funding_function
    fund = baseline.Chain002Tests.fund

    def provider(self):
        return Chain(
            self.fixture.rpc,
            self.b,
            self.fixture.artifact,
            "provider",
            PRICE,
            self.fixture.manifest,
        )

    def claim_function(self, chain, value=18):
        claim = wire(
            "Claim",
            requester=self.a.address,
            provider=self.b.address,
            agreementId=self.id,
            authorizationNonce=0,
            value=value,
            runId=self.s.run_id,
        )
        return chain.contract.functions.claim(
            tuple_for("Claim", claim),
            bytes.fromhex(self.s.sign(self.b, "Claim", claim)[2:]),
        )

    def test_receipt_temporarily_lost_reconciles_without_new_nonce(self):
        from web3.exceptions import TransactionNotFound

        original = self.chain.w3.eth.get_transaction_receipt
        calls = 0

        def delayed(digest):
            nonlocal calls
            calls += 1
            if calls < 3:
                raise TransactionNotFound("injected")
            return original(digest)

        with patch.object(
            self.chain.w3.eth, "get_transaction_receipt", side_effect=delayed
        ):
            self.fund()
        self.assertEqual(self.chain.budget.used, 1)
        self.assertEqual(len(self.chain.intents), 1)
        self.assertEqual(self.chain.intents[0]["nonce"], 0)

    def test_valid_event_cannot_override_corrupted_record_or_credit(self):
        from genesis_experiment002.agent import observe
        from genesis_experiment002.protocol import (
            Inconclusive as AgentInconclusive,
            write,
        )
        from genesis_experiment002.runner import audit_ledger

        self.fund()
        corrupted = list(self.chain.record(self.id))
        corrupted[2] = 2
        with patch.object(self.chain, "record", return_value=corrupted):
            with self.assertRaises(AgentInconclusive):
                observe(self.chain, self.t, self.id, 1)
        write(self.fixture.folder / "terms.json", {"message": self.t})
        roles = {
            "requester": {"address": self.a.address},
            "provider": {"address": self.b.address},
        }
        config = {"x": "7", "y": "11", "claimBefore": int(self.t["claimBefore"])}
        with patch.object(self.fixture.contract.functions, "credits") as credits:
            credits.return_value.call.return_value = 1
            with self.assertRaises(Inconclusive):
                audit_ledger(self.fixture, roles, self.id, config)

    def test_new_principal_intent_rejected_before_second_signature(self):
        self.fund()
        self.t["salt"] = "0x" + "44" * 32
        with patch.object(
            self.a, "sign_transaction", wraps=self.a.sign_transaction
        ) as sign:
            with self.assertRaises(Rejected):
                self.fund()
            sign.assert_not_called()
        self.assertEqual(self.chain.budget.used, 1)

    def test_exact_fee_fields_and_wallet_mutations_reject(self):
        receipt = self.fund()
        digest = receipt["transactionHash"]
        for field, change in (("effectiveGasPrice", 1), ("gasUsed", 1)):
            altered = dict(receipt)
            altered[field] += change
            with self.subTest(field=field):
                with self.assertRaises(Inconclusive):
                    self.chain.canonical_receipt(altered, digest)
        original = self.chain.w3.eth.get_balance

        def corrupt(address, block_identifier="latest"):
            value = original(address, block_identifier)
            return value + 1 if block_identifier == receipt["blockNumber"] else value

        with patch.object(self.chain.w3.eth, "get_balance", side_effect=corrupt):
            with self.assertRaises(Inconclusive):
                self.chain.canonical_receipt(receipt, digest)

    def test_mutated_transaction_price_and_block_receipt_reject(self):
        receipt = self.fund()
        digest = receipt["transactionHash"]
        transaction = dict(self.chain.w3.eth.get_transaction(digest))
        transaction["gasPrice"] += 1
        with patch.object(
            self.chain.w3.eth, "get_transaction", return_value=transaction
        ):
            with self.assertRaises(Inconclusive):
                self.chain.canonical_receipt(receipt, digest)
        block_receipt = dict(receipt)
        block_receipt["effectiveGasPrice"] += 1
        with patch.object(
            self.chain.w3.eth, "get_block_receipts", return_value=[block_receipt]
        ):
            with self.assertRaises(Inconclusive):
                self.chain.canonical_receipt(receipt, digest)

    def test_final_calldata_nonce_or_fee_mutation_never_signed(self):
        for field in ("data", "nonce", "maxFeePerGas"):
            function = self.funding_function()
            original = function.build_transaction

            def alter(params):
                tx = original(params)
                tx[field] = "0x1234" if field == "data" else tx[field] + 1
                return tx

            with patch.object(
                function, "build_transaction", side_effect=alter
            ), patch.object(
                self.a, "sign_transaction", wraps=self.a.sign_transaction
            ) as sign:
                with self.assertRaises(Rejected):
                    self.chain.transact(function, value=PRICE)
                sign.assert_not_called()
        self.assertEqual(self.chain.record(self.id)[2], 0)

    def test_revocation_before_funding_and_after_consumption(self):
        self.chain.transact(self.chain.contract.functions.revokeUnused(0))
        with self.assertRaises(Rejected):
            self.fund()
        self.assertEqual(self.chain.record(self.id)[2], 0)
        self.assertEqual(
            self.chain.contract.functions.nonceStatus(self.a.address, 0).call(), 2
        )

    def test_funded_revocation_cannot_cancel_and_provider_still_collects(self):
        self.fund()
        with self.assertRaises(Rejected):
            self.chain.transact(self.chain.contract.functions.revokeUnused(0))
        provider = self.provider()
        provider.transact(self.claim_function(provider))
        self.assertEqual(provider.record(self.id)[2], 2)
        self.assertEqual(
            provider.contract.functions.credits(self.b.address).call(), PRICE
        )

    def test_refund_equality_rejects_claim_and_preserves_consumed_nonce(self):
        self.fund()
        provider = self.provider()
        self.fixture.advance(int(self.t["claimBefore"]))
        with self.assertRaises(Rejected):
            provider.transact(self.claim_function(provider))
        self.chain.transact(self.chain.contract.functions.refund(self.id))
        with self.assertRaises(Rejected):
            provider.transact(self.claim_function(provider))
        self.assertEqual(provider.record(self.id)[2], 3)
        self.assertEqual(provider.contract.functions.credits(self.b.address).call(), 0)
        self.assertEqual(
            provider.contract.functions.nonceStatus(self.a.address, 0).call(), 1
        )

    def test_unauthorized_claim_refund_and_duplicate_terminal_actions(self):
        self.fund()
        with self.assertRaises(Rejected):
            self.chain.transact(self.chain.contract.functions.refund(self.id))
        provider = self.provider()
        # A has no claim method in its signing policy, independently of contract caller checks.
        with patch.object(
            self.a, "sign_transaction", wraps=self.a.sign_transaction
        ) as sign:
            with self.assertRaises(Rejected):
                self.chain.transact(self.claim_function(self.chain))
            sign.assert_not_called()
        provider.transact(self.claim_function(provider))
        with self.assertRaises(Rejected):
            provider.transact(self.claim_function(provider))
        with self.assertRaises(Rejected):
            self.chain.transact(self.chain.contract.functions.refund(self.id))
        provider.transact(provider.contract.functions.withdraw())
        with self.assertRaises(Rejected):
            provider.transact(provider.contract.functions.withdraw())
        self.assertEqual(provider.contract.functions.totalCredits().call(), 0)
        self.assertEqual(provider.w3.eth.get_balance(provider.contract.address), 0)

    def test_expiry_boundary_rejects_funding_without_consumption(self):
        self.fixture.advance(int(self.auth["expiresAt"]))
        with self.assertRaises(Rejected):
            self.fund()
        self.assertEqual(self.chain.record(self.id)[2], 0)
        self.assertEqual(
            self.chain.contract.functions.nonceStatus(self.a.address, 0).call(), 0
        )


class SupervisorSecurityTests(unittest.TestCase):
    def test_cleanup_after_interrupt_and_startup_failure(self):
        fixture = Fixture()
        with self.assertRaises(KeyboardInterrupt):
            with fixture:
                raise KeyboardInterrupt()
        self.assertTrue(fixture.children_stopped)
        self.assertFalse(fixture.folder.exists())
        with patch(
            "genesis_experiment002.runner.candidate_path",
            side_effect=RuntimeError("unverified"),
        ):
            bad = Fixture()
            with self.assertRaises(RuntimeError):
                bad.__enter__()
            self.assertFalse(bad.folder.exists())

    def test_resource_watchdog_stops_and_cleans(self):
        fixture = Fixture()
        with self.assertRaises(Inconclusive):
            with fixture:
                with patch(
                    "genesis_experiment002.runner.subprocess.check_output",
                    return_value=str(3 * 1024**2),
                ):
                    fixture.guard()
        self.assertTrue(fixture.children_stopped)

    def test_disclosure_and_late_inclusion_are_recorded_counterexamples(self):
        disclosed = run("early_disclosure")
        self.assertTrue(disclosed["resultObserved"]["verified"])
        self.assertEqual(disclosed["providerCredit"], 0)
        self.assertEqual(disclosed["resultObserved"]["postFundingSignatures"], 0)
        late = run("late_funding")
        self.assertLessEqual(late["fundingSlack"], 2)
        self.assertEqual(late["state"], 3)
        self.assertEqual(late["ledger"]["inclusion"]["claim"][0]["status"], 0)


if __name__ == "__main__":
    unittest.main()
