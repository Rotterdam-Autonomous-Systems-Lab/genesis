"""Bounded threat-driven regressions; no production keys or external endpoints."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

from eth_account import Account
from web3 import Web3

from genesis_experiment import protocol
from genesis_experiment.protocol import (
    Inconclusive,
    Rejected,
    Signing,
    TYPES,
    read,
    write,
)
from genesis_experiment.chain import Chain
from genesis_experiment.runner import ROOT, Fixture


class TransportAdversaries(unittest.TestCase):
    def test_fifo_message_cannot_block_read(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "internal") as directory:
            path = Path(directory) / "result.json"
            os.mkfifo(path)
            child = subprocess.Popen(
                [
                    sys.executable,
                    "-c",
                    "from pathlib import Path; from genesis_experiment.protocol import read,Rejected; "
                    "\ntry: read(Path(__import__('sys').argv[1]))\nexcept Rejected: raise SystemExit(0)\nraise SystemExit(1)",
                    str(path),
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            try:
                try:
                    code = child.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    self.fail("FIFO bypassed the bounded transport read")
                self.assertEqual(code, 0)
            finally:
                if child.poll() is None:
                    child.kill()
                child.wait(timeout=2)

    def test_publication_race_preserves_first_message(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "internal") as directory:
            path = Path(directory) / "result.json"
            original = protocol.encode

            def competing_writer(value):
                path.write_bytes(b'{"first":"writer"}')
                return original(value)

            with patch.object(protocol, "encode", side_effect=competing_writer):
                with self.assertRaises(Rejected):
                    write(path, {"second": "writer"})
            self.assertEqual(read(path), {"first": "writer"})

    def test_truncation_oversize_duplicates_and_nonregular(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "internal") as directory:
            path = Path(directory) / "result.json"
            for raw in (b'{"message":', b'{"value":"1","value":"2"}', b" " * 16385):
                path.write_bytes(raw)
                with self.assertRaises(Rejected):
                    read(path)
            with self.assertRaises(Rejected):
                read(Path(directory))


class TypedMutationTests(unittest.TestCase):
    def setUp(self):
        vectors = json.loads((ROOT / "tests/python/typed_vectors.json").read_text())
        self.messages = {k: v["message"] for k, v in vectors["vectors"].items()}
        self.signing = Signing(vectors["domain"]["verifyingContract"], vectors["runId"])
        self.owner, self.stranger = Account.create(), Account.create()

    def test_each_signed_field_of_all_five_types(self):
        for kind, msg in self.messages.items():
            signature = self.signing.sign(self.owner, kind, msg)
            self.signing.verify(kind, msg, signature, self.owner.address)
            for field in TYPES[kind]:
                changed = dict(msg)
                name, typ = field["name"], field["type"]
                changed[name] = (
                    str(int(msg[name]) + 1)
                    if typ.startswith("uint")
                    else (
                        self.stranger.address if typ == "address" else "0x" + "ab" * 32
                    )
                )
                with self.subTest(kind=kind, field=name), self.assertRaises(Rejected):
                    self.signing.verify(kind, changed, signature, self.owner.address)

    def test_wrong_domains_signers_purposes_and_formats_all_types(self):
        for kind, msg in self.messages.items():
            envelope = self.signing.envelope(self.owner, kind, msg)
            for field, value in (
                ("chainId", "1"),
                ("verifyingContract", self.stranger.address),
                ("name", "Other"),
                ("version", "2"),
            ):
                with self.subTest(kind=kind, field=field), self.assertRaises(Rejected):
                    self.signing.open(
                        {**envelope, "domain": {**envelope["domain"], field: value}},
                        kind,
                        self.owner.address,
                    )
                other = Signing(
                    self.signing.domain["verifyingContract"], self.signing.run_id
                )
                other.domain[field] = value
                signature = other.sign(self.owner, kind, msg)
                with self.assertRaises(Rejected):
                    self.signing.verify(kind, msg, signature, self.owner.address)
            with self.assertRaises(Rejected):
                self.signing.open(envelope, kind, self.stranger.address)
            for signature in (
                "0x",
                "0x" + "00" * 65,
                envelope["signature"][:-2] + "01",
                "0x" + "11" * 64,
            ):
                with self.subTest(kind=kind, format=len(signature)), self.assertRaises(
                    Rejected
                ):
                    self.signing.verify(kind, msg, signature, self.owner.address)
            data = bytes.fromhex(envelope["signature"][2:])
            high_s = int(
                "fffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141", 16
            ) - int.from_bytes(data[32:64], "big")
            malleable = (
                "0x"
                + (
                    data[:32] + high_s.to_bytes(32, "big") + bytes([55 - data[64]])
                ).hex()
            )
            with self.assertRaises(Rejected):
                self.signing.verify(kind, msg, malleable, self.owner.address)
            for purpose in TYPES:
                if purpose != kind:
                    with self.assertRaises(Rejected):
                        self.signing.open(
                            {**envelope, "primaryType": purpose},
                            kind,
                            self.owner.address,
                        )

    def test_schema_flag_code_and_noncanonical_numeric_mutations(self):
        for kind, msg in self.messages.items():
            for changed in (
                {**msg, "verified": True},
                {**msg, "execute": "arbitrary code"},
                {},
            ):
                with self.assertRaises(Rejected):
                    self.signing.sign(self.owner, kind, changed)
            for f in TYPES[kind]:
                if f["type"].startswith("uint"):
                    for bad in (True, -1, "01", "1e2", str(2 ** int(f["type"][4:]))):
                        with self.assertRaises(Rejected):
                            self.signing.sign(self.owner, kind, {**msg, f["name"]: bad})


class LiveAdversaries(unittest.TestCase):
    def setUp(self):
        import test_integration

        self.case = test_integration.ContractInteropTests("runTest")
        self.case.setUp()
        self.addCleanup(self.case.doCleanups)
        self.f = self.case.fixture
        self.a = self.case.a
        self.b = self.case.b
        self.chain = self.case.chain
        self.s = self.case.s

    def via_proxy(self, mode):
        from rpc_faults import FaultProxy

        proxy = FaultProxy(self.f.rpc, mode).__enter__()
        self.addCleanup(proxy.__exit__, None, None, None)
        self.case.chain = Chain(proxy.url, self.a, self.f.artifact, self.f.manifest)
        return proxy

    def settle(self):
        from genesis_experiment.protocol import wire, tuple_for

        result = wire("Result", agreementId=self.case.id, value=18, runId=self.s.run_id)
        acceptance = wire(
            "Acceptance",
            agreementId=self.case.id,
            resultDigest=self.s.digest("Result", result),
            authorizationNonce=0,
            runId=self.s.run_id,
        )
        b = Chain(self.f.rpc, self.b, self.f.artifact, self.f.manifest)
        function = b.contract.functions.settle(
            self.case.id,
            tuple_for("Result", result),
            self.s.sign(self.b, "Result", result),
            tuple_for("Acceptance", acceptance),
            self.s.sign(self.a, "Acceptance", acceptance),
        )
        b.transact(
            function, "Settled", {"agreementId": self.case.id, "price": protocol.PRICE}
        )
        return b, function, result, acceptance

    def test_network_loss_before_broadcast_latches_and_blocks_duplicate_retry(self):
        proxy = self.via_proxy("before_send")
        with self.assertRaises(Inconclusive):
            self.case.fund()
        with self.assertRaises(Inconclusive):
            self.case.fund()
        self.assertEqual(proxy.calls.count("eth_sendRawTransaction"), 1)
        self.assertEqual(self.f.contract.functions.totalDeposited().call(), 0)
        self.assertEqual(
            self.f.contract.functions.nonceStatus(self.a.address, 0).call(), 0
        )

    def test_network_loss_after_broadcast_reconciles_and_replay_rejects(self):
        proxy = self.via_proxy("after_send")
        self.case.fund()
        self.assertEqual(proxy.calls.count("eth_sendRawTransaction"), 1)
        self.assertEqual(
            self.f.contract.functions.totalDeposited().call(), protocol.PRICE
        )
        self.case.unchanged_rejection(self.case.fund)
        self.assertEqual(
            self.f.contract.functions.totalDeposited().call(), protocol.PRICE
        )

    def test_mutated_transaction_hash_does_not_claim_success(self):
        self.via_proxy("wrong_hash")
        with self.assertRaises(Inconclusive):
            self.case.fund()
        # A transaction may have executed despite false diagnostics; no automatic retry.
        self.assertEqual(
            self.f.contract.functions.totalDeposited().call(), protocol.PRICE
        )
        with self.assertRaises(Inconclusive):
            self.case.fund()

    def test_mutated_receipt_hash_rejected(self):
        self.via_proxy("receipt_hash")
        with self.assertRaises(Inconclusive):
            self.case.fund()

    def test_mutated_receipt_status_rejected(self):
        self.via_proxy("receipt_status")
        with self.assertRaises(Inconclusive):
            self.case.fund()

    def test_mutated_event_price_rejected(self):
        self.via_proxy("event_price")
        with self.assertRaises(Inconclusive):
            self.case.fund()

    def test_mutated_event_emitter_rejected(self):
        self.via_proxy("event_emitter")
        with self.assertRaises(Inconclusive):
            self.case.fund()

    def test_ccip_lookup_cannot_make_hidden_http_request(self):
        from eth_abi import encode
        from web3.exceptions import OffchainLookup

        proxy = self.via_proxy("offchain")
        # Controlled loopback target: a malicious OffchainLookup must not contact it.
        payload = encode(
            ["address", "string[]", "bytes", "bytes4", "bytes"],
            [self.f.contract.address, [proxy.url + "/forbidden"], b"", b"\0" * 4, b""],
        )
        proxy.error_payload = "0x556f1830" + payload.hex()
        before = proxy.calls.count("eth_call")
        with self.assertRaises(OffchainLookup):
            self.case.chain.w3.eth.call({"to": self.f.contract.address, "data": "0x"})
        self.assertFalse(self.case.chain.w3.provider.global_ccip_read_enabled)
        self.assertEqual(proxy.calls.count("eth_call"), before + 1)
        # No secondary CCIP HTTP request (which would not be a JSON RPC method).
        self.assertNotIn("/forbidden", proxy.paths)
        # Reproduce the dependency's old default against a controlled loopback target only.
        self.case.chain.w3.provider.global_ccip_read_enabled = True
        try:
            with self.assertRaises(Exception):
                self.case.chain.w3.eth.call(
                    {"to": self.f.contract.address, "data": "0x"}
                )
            self.assertIn("/forbidden", proxy.paths)
        finally:
            self.case.chain.w3.provider.global_ccip_read_enabled = False

    def test_revoked_nonce_and_funding_first_race(self):
        self.chain.transact(
            self.f.contract.functions.revokeUnused(0),
            "NonceRevoked",
            {"requester": self.a.address, "nonce": 0},
        )
        self.case.unchanged_rejection(self.case.fund)
        self.assertEqual(
            self.f.contract.functions.nonceStatus(self.a.address, 0).call(), 2
        )
        self.case.auth = {**self.case.auth, "nonce": "1"}
        self.case.fund()
        with self.assertRaises(Rejected):
            self.chain.transact(self.f.contract.functions.revokeUnused(1))
        self.assertEqual(
            self.f.contract.functions.getAgreement(self.case.id).call()[2], 1
        )

    def test_terminal_transitions_and_unauthorized_withdrawal(self):
        self.case.fund()
        b, settlement, _, _ = self.settle()
        self.case.unchanged_rejection(lambda: b.transact(settlement))
        self.case.unchanged_rejection(
            lambda: self.chain.transact(self.f.contract.functions.refund(self.case.id))
        )
        self.case.unchanged_rejection(
            lambda: self.chain.transact(self.f.contract.functions.withdraw())
        )
        self.assertEqual(
            self.f.contract.functions.credits(self.b.address).call(), protocol.PRICE
        )
        b.transact(
            self.f.contract.functions.withdraw(),
            "Withdrawn",
            {"account": self.b.address, "amount": protocol.PRICE},
        )
        with self.assertRaises(Rejected):
            b.transact(self.f.contract.functions.withdraw())
        self.assertEqual(
            self.f.contract.functions.totalWithdrawn().call(), protocol.PRICE
        )

    def test_settlement_after_refund_rejected(self):
        self.case.fund()
        self.f.advance(int(self.case.terms["settlementDeadline"]))
        self.chain.transact(self.f.contract.functions.refund(self.case.id))
        with self.assertRaises(Rejected):
            self.settle()
        self.assertEqual(
            self.f.contract.functions.credits(self.a.address).call(), protocol.PRICE
        )
        self.assertEqual(self.f.contract.functions.credits(self.b.address).call(), 0)

    def test_missing_and_forged_provider_report_rejected(self):
        from genesis_experiment.agent import verify_provider_report

        self.case.fund()
        b, _, result, acceptance = self.settle()
        report = {
            "outcome": "settled",
            "agreementId": self.case.id,
            "settlementTx": b.evidence()[0]["hash"],
            "address": self.b.address,
            "pid": "1",
            "receipts": [],
        }
        with self.assertRaises(Inconclusive):
            verify_provider_report(
                self.chain,
                report,
                self.b.address,
                self.case.id,
                acceptance["resultDigest"],
            )
        report["receipts"] = b.evidence()
        with self.assertRaises(Inconclusive):
            verify_provider_report(
                self.chain,
                report,
                self.b.address,
                self.case.id,
                acceptance["resultDigest"],
            )
        b.transact(
            self.f.contract.functions.withdraw(),
            "Withdrawn",
            {"account": self.b.address, "amount": protocol.PRICE},
        )
        report["receipts"] = b.evidence()
        verify_provider_report(
            self.chain, report, self.b.address, self.case.id, acceptance["resultDigest"]
        )
        for field, value in (
            ("agreementId", "0x" + "aa" * 32),
            ("address", self.a.address),
            ("settlementTx", "0x" + "bb" * 32),
        ):
            with self.assertRaises(Inconclusive):
                verify_provider_report(
                    self.chain,
                    {**report, field: value},
                    self.b.address,
                    self.case.id,
                    acceptance["resultDigest"],
                )

    def test_unauthorized_local_client_cannot_use_peer_signatures(self):
        from genesis_experiment.protocol import tuple_for

        self.case.fund()
        stranger = Account.create()
        self.f.balance(stranger.address)
        c = Chain(self.f.rpc, stranger, self.f.artifact, self.f.manifest)
        terms = self.case.terms
        auth = self.case.auth
        with self.assertRaises(Rejected):
            c.transact(
                c.contract.functions.fund(
                    tuple_for("Agreement", terms),
                    self.s.sign(self.a, "Agreement", terms),
                    self.s.sign(self.b, "Agreement", terms),
                    tuple_for("Authorization", auth),
                    self.s.sign(self.a, "Authorization", auth),
                ),
                value=protocol.PRICE,
            )
        with self.assertRaises(Rejected):
            c.transact(c.contract.functions.refund(self.case.id))
        with self.assertRaises(Rejected):
            c.transact(c.contract.functions.withdraw())
        self.assertEqual(self.f.contract.functions.totalLocked().call(), protocol.PRICE)


class ProcessFaultTests(unittest.TestCase):
    def test_malformed_evidence_refunds_without_acceptance(self):
        from genesis_experiment.runner import run

        for scenario in (
            "malformed_evidence",
            "oversized_evidence",
            "truncated_evidence",
            "unexpected_evidence",
        ):
            with self.subTest(scenario=scenario):
                r = run(scenario)
                self.assertEqual(r["outcome"], "refunded")
                self.assertFalse(r["requester"]["acceptanceSigned"])
                self.assertEqual(r["provider"]["receipts"], [])
                self.assertTrue(r["childrenStopped"])

    def test_deadline_expires_during_computation(self):
        from genesis_experiment.runner import run

        r = run("deadline_during_work")
        self.assertEqual(r["outcome"], "refunded")
        self.assertEqual(r["requester"]["reason"], "late_result")
        self.assertFalse(r["requester"]["acceptanceSigned"])
        self.assertTrue(r["childrenStopped"])

    def test_crashes_abort_with_no_payment_and_clean_resources(self):
        from genesis_experiment.runner import run

        for scenario in (
            "provider_crash_after_result",
            "requester_crash_before_acceptance",
            "requester_tampers_terms",
        ):
            captured = []
            states = []

            def observe(fixture, agents):
                captured[:] = fixture.processes
                states.append(
                    (
                        fixture.contract.functions.totalCredits().call(),
                        fixture.contract.functions.totalWithdrawn().call(),
                    )
                )

            with self.subTest(scenario=scenario), self.assertRaises(Inconclusive):
                run(scenario, observe=observe)
            self.assertTrue(captured)
            self.assertTrue(all(process.poll() is not None for process in captured))
            self.assertTrue(
                all(credits == 0 and withdrawn == 0 for credits, withdrawn in states)
            )

    def test_interrupted_fixture_startup_terminates_node(self):
        processes = []
        original = subprocess.Popen

        def track(*args, **kwargs):
            child = original(*args, **kwargs)
            processes.append(child)
            return child

        with patch(
            "genesis_experiment.runner.subprocess.Popen", side_effect=track
        ), patch("genesis_experiment.runner.Chain", side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt):
                with Fixture():
                    self.fail("interrupted startup entered fixture")
        self.assertTrue(processes)
        self.assertTrue(all(p.poll() is not None for p in processes))

    def test_process_reorg_aborts_without_refund_or_acceptance(self):
        from genesis_experiment.runner import run

        captured = []
        forbidden = []
        injected = []

        def observe(fixture, agents):
            captured[:] = fixture.processes
            if (fixture.folder / "resume-requester.json").exists():
                injected.append(True)
            forbidden.extend(
                name
                for name in ("acceptance.json", "refund-wait.json")
                if (fixture.folder / name).exists()
            )

        with self.assertRaises(Inconclusive):
            run("chain_reorg_before_acceptance", observe=observe)
        self.assertTrue(captured)
        self.assertEqual(forbidden, [])
        self.assertTrue(injected, "snapshot/revert fault was not injected")
        self.assertTrue(all(p.poll() is not None for p in captured))
