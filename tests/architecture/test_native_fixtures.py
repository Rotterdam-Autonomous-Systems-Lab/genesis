"""Fixture integrity and negative controls only; no architecture model execution."""
import copy
import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from Crypto.Signature import eddsa

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location('native_fixture_validation', ROOT/'research/fixtures/native_l1/validate.py')
fixtures = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(fixtures)
DIR = ROOT/'research/fixtures/native_l1/v1'


class FrozenCorpusTests(unittest.TestCase):
    def setUp(self):
        self.data = fixtures.load_json(DIR/'corpus.json')

    def test_all_frozen_vectors_and_artifact_hashes(self):
        self.assertEqual(fixtures.validate(self.data), 21)

    def test_schema_rejects_unknown_fields_and_boolean_amount(self):
        for mutation in ('field','amount','missing'):
            with self.subTest(mutation=mutation):
                bad = copy.deepcopy(self.data)
                if mutation == 'field':
                    bad['vectors'][0]['initial_state']['admin_override'] = True
                elif mutation == 'amount':
                    bad['vectors'][0]['initial_state']['balances']['H'] = True
                else:
                    del bad['vectors'][0]['steps'][0]['expect']['client']
                with self.assertRaises(ValueError):
                    fixtures.validate(bad, check_hash=False)

    def test_duplicate_json_keys_fail(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder)/'bad.json'
            p.write_text('{"version":1,"version":2}')
            with self.assertRaises(ValueError):
                fixtures.load_json(p)

    def test_independent_wire_examples_and_rfc_public_signature(self):
        public = fixtures.load_json(DIR/'codec_vectors.json')
        for item in public['cbor']:
            value = fixtures.unpack(item['value'])
            raw = bytes.fromhex(item['hex'])
            self.assertEqual(fixtures.encode(value), raw)
            self.assertEqual(fixtures.decode(raw), value)
        v = public['ed25519']
        eddsa.new(eddsa.import_public_key(bytes.fromhex(v['public_key'])), 'rfc8032').verify(bytes.fromhex(v['message_hex']), bytes.fromhex(v['signature']))

    def test_noncanonical_truncated_or_disallowed_wire_rejected(self):
        for raw in (b'\x18\x00', b'\x19\x00\x18', b'\x80\x00', b'\x9f\xff', b'\xa0', b'\xf4', b'\x20', b'\xfb'+bytes(8), b'\x58\x20\x00', b'\x9b'+b'\xff'*8):
            with self.subTest(raw=raw.hex()):
                with self.assertRaises(ValueError):
                    fixtures.decode(raw)

    def test_signature_is_bound_to_actor_and_exact_digest(self):
        intent = self.data['intents']['pay10']; digest = bytes.fromhex(intent['intent_id'])
        key = eddsa.import_public_key(bytes.fromhex(self.data['actors']['D1']['public_key']))
        sig = bytes.fromhex(intent['signature'])
        eddsa.new(key, 'rfc8032').verify(digest, sig)
        with self.assertRaises(ValueError):
            eddsa.new(key, 'rfc8032').verify(hashlib.sha256(digest).digest(), sig)
        wrong = self.data['intents']['wrong_key']
        with self.assertRaises(ValueError):
            eddsa.new(key, 'rfc8032').verify(bytes.fromhex(wrong['intent_id']), bytes.fromhex(wrong['signature']))
        bad = copy.deepcopy(self.data)
        bad['intents']['pay10']['signature'] = '00'*64
        with self.assertRaises(ValueError):
            fixtures.validate(bad, check_hash=False)

    def test_wrong_owner_budget_and_fee_snapshots_rejected(self):
        for mutation in ('owner','budget','fee'):
            bad = copy.deepcopy(self.data)
            if mutation == 'owner':
                v = next(v for v in bad['vectors'] if v['id']=='V12')
                v['steps'][1]['expect']['ledger']['credits']['C']['owner'] = 'H'
            elif mutation == 'budget':
                bad['vectors'][0]['steps'][0]['expect']['ledger']['grants']['G']['principal_used'] += 1
            else:
                bad['vectors'][0]['steps'][0]['expect']['ledger']['fee_sink'] += 1
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                fixtures.validate(bad, check_hash=False)

    def test_event_binding_and_rejection_immutability(self):
        bad = copy.deepcopy(self.data)
        bad['vectors'][0]['steps'][0]['event']['intent'] = 'wrong_recipient'
        with self.assertRaises(ValueError):
            fixtures.validate(bad, check_hash=False)
        bad = copy.deepcopy(self.data)
        v = next(v for v in bad['vectors'] if v['id']=='V07')
        v['steps'][0]['expect']['ledger']['balances']['H'] -= 1
        v['steps'][0]['expect']['ledger']['balances']['X'] += 1
        with self.assertRaises(ValueError):
            fixtures.validate(bad, check_hash=False)

    def test_frozen_recovery_and_resource_plan_coverage(self):
        statuses = {st['expect']['result'] for v in self.data['vectors'] for st in v['steps']}
        self.assertTrue({'same_intent_retry_allowed','halted:unknown','halted:contradiction','halted:assumption_breach','orphaned','duplicate','structural_reject'} <= statuses)
        self.assertEqual({v['oracle'] for v in self.data['vectors']}, {'O1','O2','O3'})
        self.assertEqual(3*(21+9)+1, self.data['run_plan']['max_runs_per_candidate'])
        for v in self.data['vectors']:
            for st in v['steps']:
                client = st['expect']['client']
                self.assertLessEqual(client['submissions'], 3)
                self.assertLessEqual(client['queries'], 8)
                if st['expect']['result'] == 'client_blocked':
                    self.assertEqual(client['status'], 'halted')
                    self.assertGreater(client['fee_reserved'], 0)


if __name__ == '__main__':
    unittest.main()
