import unittest
import json
from pathlib import Path
import tempfile
import time
from unittest.mock import Mock

from eth_account import Account
from genesis_experiment.agent import discover, result_acceptance, agreement_envelope, open_agreement
from genesis_experiment.chain import connect
from genesis_experiment.protocol import (LIMIT, PRICE, Rejected, SERVICE, Signing,
    decode, encode, hex_value, integer, normalize, wire, read, write, wait, Inconclusive)


class CodecTests(unittest.TestCase):
    def test_fixed_public_golden_vectors(self):
        fixture = json.loads(Path(__file__).with_name("typed_vectors.json").read_text())
        signing = Signing(fixture["domain"]["verifyingContract"], fixture["runId"])
        for kind, vector in fixture["vectors"].items():
            self.assertEqual(signing.digest(kind, vector["message"]), vector["digest"])

    def test_transport_bounds_immutability_timeout_and_symlink(self):
        with tempfile.TemporaryDirectory(dir="internal") as directory:
            path = Path(directory) / "message.json"
            write(path, {"id": "public"})
            self.assertEqual(read(path), {"id": "public"})
            with self.assertRaises(Rejected):
                write(path, {})
            link = Path(directory) / "link.json"
            link.symlink_to(path)
            with self.assertRaises(Rejected):
                read(link)
            large = Path(directory) / "large.json"
            large.write_bytes(b" " * (LIMIT+1))
            with self.assertRaises(Rejected):
                read(large)
            with self.assertRaises(Inconclusive):
                wait(Path(directory) / "missing.json", time.monotonic()+0.05)

    def test_integer_boundaries(self):
        self.assertEqual(integer(str(2**64-1), 64), 2**64-1)
        self.assertEqual(integer("0", 64), 0)
        for bad in ("00", "01", "-1", "+1", " 1", "1.0", "1e2", "1\n", 1, True, str(2**64)):
            with self.subTest(bad=bad), self.assertRaises(Rejected):
                integer(bad, 64)

    def test_json_ambiguity_and_size(self):
        for raw in (b'{"x":1,"x":2}', b'\xff', b'{"x":NaN}', b'['*10000, b' '* (LIMIT+1)):
            with self.assertRaises(Rejected):
                decode(raw)
        self.assertEqual(decode(b'"' + b'a'*(LIMIT-2) + b'"'), 'a'*(LIMIT-2))
        with self.assertRaises(Rejected):
            encode({"x": "a"*LIMIT})

    def test_hex_and_unknown_fields(self):
        for bad in ("0x00", "a"*64, "0x"+"g"*64):
            with self.assertRaises(Rejected):
                hex_value(bad, 32)
        with self.assertRaises(Rejected):
            normalize("Result", {"agreementId":"0x"+"11"*32,"value":"1","runId":"0x"+"22"*32,"execute":"shell"})

    def test_remote_rpc_rejected_before_connection(self):
        for url in ("https://example.com", "http://localhost:8545", "http://127.0.0.1:1/?fork=x", "http://user@127.0.0.1:1", "http://127.0.0.2:8545"):
            with self.assertRaises(Rejected):
                connect(url)


class SigningTests(unittest.TestCase):
    def setUp(self):
        self.provider = Account.create()
        self.requester = Account.create()
        self.signing = Signing("0x"+"12"*20, "0x"+"34"*32)
        self.result = wire("Result", agreementId="0x"+"56"*32, value=18, runId=self.signing.run_id)

    def test_result_signature_and_domains(self):
        env = self.signing.envelope(self.provider, "Result", self.result)
        self.signing.open(env, "Result", self.provider.address)
        with self.assertRaises(Rejected):
            self.signing.open(env, "Result", self.requester.address)
        for field, value in (("chainId", 1), ("verifyingContract", "0x"+"78"*20), ("name", "Other"), ("version", "2")):
            changed = {**env, "domain": {**env["domain"], field: value}}
            with self.assertRaises(Rejected):
                self.signing.open(changed, "Result", self.provider.address)
        with self.assertRaises(Rejected):
            self.signing.open({**env, "primaryType": "Acceptance"}, "Result", self.provider.address)

    def test_invalid_result_never_creates_acceptance(self):
        chain = Mock(signing=self.signing, manifest={"runId": self.signing.run_id})
        terms = {"provider": self.provider.address, "x": 7, "y": 11}
        good = self.signing.envelope(self.provider, "Result", self.result)
        acceptance = result_acceptance(chain, good, terms, self.result["agreementId"], 0)
        self.assertEqual(acceptance["resultDigest"], self.signing.digest("Result", self.result))
        bad = self.signing.envelope(self.provider, "Result", {**self.result, "value": "19"})
        with self.assertRaises(Rejected):
            result_acceptance(chain, bad, terms, self.result["agreementId"], 0)
        with self.assertRaises(Rejected):
            result_acceptance(chain, good, terms, "0x"+"99"*32, 0)

    def test_discovery_bounds_and_expiry(self):
        chain = Mock(signing=self.signing)
        chain.w3.eth.get_block.return_value = {"timestamp": 100}
        msg = wire("Advertisement", provider=self.provider.address, serviceId=SERVICE, price=PRICE, expiresAt=101, runId=self.signing.run_id)
        offer = self.signing.envelope(self.provider, "Advertisement", msg)
        discover(chain, {"offers": [offer]}, self.provider.address)
        for offers in ([], [offer]*17):
            with self.assertRaises(Rejected):
                discover(chain, {"offers": offers}, self.provider.address)
        expired = self.signing.envelope(self.provider, "Advertisement", {**msg, "expiresAt": "100"})
        with self.assertRaises(Rejected):
            discover(chain, {"offers": [expired]}, self.provider.address)

    def test_signature_encoding_and_run_rejected(self):
        env = self.signing.envelope(self.provider, "Result", self.result)
        for signature in ("0x"+"00"*65, env["signature"][:-2]+"00", "0x"+"11"*64):
            with self.assertRaises(Rejected):
                self.signing.open({**env, "signature": signature}, "Result", self.provider.address)
        with self.assertRaises(Rejected):
            self.signing.envelope(self.provider, "Result", {**self.result, "runId": "0x"+"99"*32})

    def test_agreement_tampering_rejected_before_countersigning(self):
        msg = wire("Agreement", requester=self.requester.address, provider=self.provider.address,
                   serviceId=SERVICE, x=7, y=11, price=PRICE, fundingDeadline=160,
                   settlementDeadline=220, salt="0x"+"55"*32, runId=self.signing.run_id)
        envelope = agreement_envelope(self.signing, msg, self.signing.sign(self.requester, "Agreement", msg))
        open_agreement(self.signing, envelope, self.requester.address, self.provider.address, 100)
        for field, value in (("x", "8"), ("price", str(PRICE+1)), ("provider", self.requester.address), ("fundingDeadline", "100")):
            with self.subTest(field=field), self.assertRaises(Rejected):
                open_agreement(self.signing, {**envelope, "message": {**msg, field: value}},
                               self.requester.address, self.provider.address, 100)
