import copy
import unittest
from unittest.mock import patch

import requests
from eth_account import Account
from web3 import Web3

from genesis_experiment.chain import Chain, LocalSession
from genesis_experiment.protocol import (Inconclusive, PRICE, Rejected, SERVICE, tuple_for, wire)
from genesis_experiment.runner import Fixture, run


class ProcessTests(unittest.TestCase):
    def test_success_separate_processes_and_two_clean_runs(self):
        results = [run(), run()]
        for r in results:
            self.assertEqual(r["outcome"], "settled")
            self.assertTrue(r["childrenStopped"])
            self.assertTrue(r["requester"]["acceptanceSigned"])
            self.assertNotEqual(r["agents"]["provider"]["pid"], r["agents"]["requester"]["pid"])
            self.assertNotEqual(r["agents"]["provider"]["address"], r["agents"]["requester"]["address"])
            self.assertEqual(len(r["provider"]["receipts"]), 2)
        self.assertNotEqual(results[0]["manifest"]["runId"], results[1]["manifest"]["runId"])

    def test_maximum_operands(self):
        r = run(x=str(2**64-1), y=str(2**64-1))
        self.assertEqual(r["expectedResult"], str(2**65-2))

    def test_invalid_result_rejected_and_refunded(self):
        r = run("invalid_result")
        self.assertEqual(r["requester"]["reason"], "invalid_result")
        self.assertFalse(r["requester"]["acceptanceSigned"])
        self.assertEqual(r["outcome"], "refunded")
        self.assertEqual(r["provider"]["receipts"], [])
        self.assertTrue(r["childrenStopped"])

    def test_requester_veto_valid_work_timeout_refund(self):
        r = run("requester_refusal")
        self.assertEqual(r["requester"]["reason"], "requester_refusal")
        self.assertFalse(r["requester"]["acceptanceSigned"])
        self.assertEqual(r["outcome"], "refunded")
        self.assertEqual(r["provider"]["outcome"], "no_acceptance")

    def test_provider_process_termination(self):
        r = run("provider_killed")
        self.assertEqual(r["provider"]["outcome"], "terminated")
        self.assertEqual(r["requester"]["reason"], "provider_timeout")
        self.assertEqual(r["outcome"], "refunded")
        self.assertTrue(r["childrenStopped"])


class ContractInteropTests(unittest.TestCase):
    def setUp(self):
        self.fixture = Fixture().__enter__()
        self.addCleanup(self.fixture.__exit__, None, None, None)
        self.a, self.b = Account.create(), Account.create()  # trusted adversarial test actors, not agent identities
        for acct in (self.a, self.b):
            self.fixture.balance(acct.address)
        self.chain = Chain(self.fixture.rpc, self.a, self.fixture.artifact, self.fixture.manifest)
        self.s = self.chain.signing
        now = self.fixture.w3.eth.get_block("latest")["timestamp"]
        self.terms = wire("Agreement", requester=self.a.address, provider=self.b.address, serviceId=SERVICE,
            x=7, y=11, price=PRICE, fundingDeadline=now+60, settlementDeadline=now+120,
            salt="0x"+"55"*32, runId=self.s.run_id)
        self.id = self.s.digest("Agreement", self.terms)
        self.auth = wire("Authorization", requester=self.a.address, provider=self.b.address, agreementId=self.id,
                         nonce=0, maxAmount=2*PRICE, validUntil=now+60, runId=self.s.run_id)

    def fund(self, terms=None, auth=None, signature=None):
        terms, auth = terms or self.terms, auth or self.auth
        return self.chain.transact(self.chain.contract.functions.fund(tuple_for("Agreement", terms),
            signature or self.s.sign(self.a, "Agreement", terms), self.s.sign(self.b, "Agreement", terms),
            tuple_for("Authorization", auth), self.s.sign(self.a, "Authorization", auth)),
            "Funded", {"agreementId": self.s.digest("Agreement", terms), "price": PRICE}, value=PRICE)

    def unchanged_rejection(self, callback):
        c = self.chain.contract
        before = (c.functions.totalDeposited().call(), c.functions.totalLocked().call(),
                  c.functions.totalCredits().call(), self.fixture.w3.eth.get_balance(c.address),
                  c.functions.nonceStatus(self.a.address, 0).call(), c.functions.getAgreement(self.id).call())
        with self.assertRaises(Rejected):
            callback()
        after = (c.functions.totalDeposited().call(), c.functions.totalLocked().call(),
                 c.functions.totalCredits().call(), self.fixture.w3.eth.get_balance(c.address),
                 c.functions.nonceStatus(self.a.address, 0).call(), c.functions.getAgreement(self.id).call())
        self.assertEqual(before, after)

    def test_all_five_python_solidity_digest_vectors(self):
        result = wire("Result", agreementId=self.id, value=18, runId=self.s.run_id)
        values = {"Agreement": self.terms, "Authorization": self.auth, "Result": result,
            "Advertisement": wire("Advertisement", provider=self.b.address, serviceId=SERVICE, price=PRICE, expiresAt=123, runId=self.s.run_id),
            "Acceptance": wire("Acceptance", agreementId=self.id, resultDigest=self.s.digest("Result", result), authorizationNonce=0, runId=self.s.run_id)}
        for kind, msg in values.items():
            with self.subTest(kind=kind):
                actual = getattr(self.chain.contract.functions, "hash"+kind)(tuple_for(kind, msg)).call()
                self.assertEqual(Web3.to_hex(actual), self.s.digest(kind, msg))

    def test_replay_consumed_nonce_new_agreement(self):
        self.fund()
        self.unchanged_rejection(lambda: self.fund())
        changed = {**self.terms, "salt": "0x"+"66"*32}
        self.unchanged_rejection(lambda: self.fund(changed, {**self.auth, "agreementId": self.s.digest("Agreement", changed)}))

    def test_spending_above_cap(self):
        self.unchanged_rejection(lambda: self.fund(auth={**self.auth, "maxAmount": str(PRICE-1)}))

    def test_wrong_participant_and_agreement_binding(self):
        for field, value in (("provider", self.a.address), ("requester", self.b.address), ("agreementId", "0x"+"88"*32)):
            with self.subTest(field=field):
                self.unchanged_rejection(lambda: self.fund(auth={**self.auth, field: value}))

    def test_altered_signed_terms(self):
        signature = self.s.sign(self.a, "Agreement", self.terms)
        changed = {**self.terms, "x": "8"}
        self.unchanged_rejection(lambda: self.fund(changed, {**self.auth, "agreementId": self.s.digest("Agreement", changed)}, signature))

    def test_expired_authorization_equality_and_plus_one(self):
        for delta in (0, 1):
            until = int(self.auth["validUntil"]) - 10
            self.fixture.rpc_call("evm_setNextBlockTimestamp", [until + delta])
            self.unchanged_rejection(lambda: self.fund(auth={**self.auth, "validUntil": str(until)}))
            self.assertEqual(self.fixture.w3.eth.get_block(self.chain.receipts[-1]["blockNumber"])["timestamp"], until + delta)

    def test_funding_immediately_before_expiry(self):
        until = int(self.auth["validUntil"]) - 10
        self.fixture.rpc_call("evm_setNextBlockTimestamp", [until-1])
        receipt = self.fund(auth={**self.auth, "validUntil": str(until)})
        self.assertEqual(self.fixture.w3.eth.get_block(receipt["blockNumber"])["timestamp"], until-1)

    def test_refund_boundary_and_duplicate(self):
        self.fund()
        self.unchanged_rejection(lambda: self.chain.transact(self.chain.contract.functions.refund(self.id)))
        self.fixture.advance(int(self.terms["settlementDeadline"]))
        self.chain.transact(self.chain.contract.functions.refund(self.id), "Refunded", {"agreementId": self.id, "price": PRICE})
        self.assertEqual(self.chain.contract.functions.credits(self.a.address).call(), PRICE)
        self.unchanged_rejection(lambda: self.chain.transact(self.chain.contract.functions.refund(self.id)))

    def test_dropped_send_response_reconciles_exact_funding(self):
        original = self.chain.w3.eth.send_raw_transaction
        def dropped(raw):
            original(raw)
            raise requests.ConnectionError("fixture dropped response")
        with patch.object(self.chain.w3.eth, "send_raw_transaction", side_effect=dropped) as send:
            self.fund()
        self.assertEqual(send.call_count, 1)
        self.assertEqual(self.chain.contract.functions.totalDeposited().call(), PRICE)
        self.assertEqual(len(self.chain.receipts), 1)

    def test_rpc_interruption_aborts_without_new_authorization(self):
        with patch.object(self.chain.w3.eth, "send_raw_transaction", side_effect=requests.ConnectionError):
            with self.assertRaises(Inconclusive):
                self.fund()
        self.assertEqual(self.chain.contract.functions.nonceStatus(self.a.address, 0).call(), 0)
        self.assertEqual(self.chain.contract.functions.totalDeposited().call(), 0)

    def test_changed_deployment_refused(self):
        manifest = {**self.fixture.manifest, "codeHash": "0x"+"00"*32}
        with self.assertRaises(Inconclusive):
            Chain(self.fixture.rpc, self.a, self.fixture.artifact, manifest)

    def test_reorg_after_funding_is_inconclusive(self):
        snapshot = self.fixture.rpc_call("evm_snapshot", [])
        self.fund()
        self.fixture.rpc_call("evm_revert", [snapshot])
        self.fixture.rpc_call("evm_mine", [])
        with self.assertRaises(Inconclusive):
            self.chain.preflight()

    def test_proxy_and_redirect_refused(self):
        from genesis_experiment.chain import connect
        with patch.dict("os.environ", {"HTTPS_PROXY": "http://127.0.0.1:1"}):
            with self.assertRaises(Rejected):
                connect(self.fixture.rpc)
        response = requests.Response()
        response.status_code = 302
        with patch("requests.Session.request", return_value=response):
            with self.assertRaises(Inconclusive):
                LocalSession().get(self.fixture.rpc)

    def test_transaction_budget(self):
        self.chain.submissions = 8
        with self.assertRaises(Rejected):
            self.fund()
