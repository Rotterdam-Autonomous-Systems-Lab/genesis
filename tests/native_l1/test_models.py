"""Bounded security controls; deliberately independent of measured run counts."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from research.native_l1.common import codec
from research.native_l1.devcheck import MODELS,core
from research.native_l1.checks import compare, invariants,ComparisonFailure
from research.native_l1.runner import native_audit

ROOT=Path(__file__).resolve().parents[2]


class Models(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        codec.validate()
        cls.data=json.loads((ROOT/'research/fixtures/native_l1/v1/corpus.json').read_text())

    def test_all_canonical_cases(self):
        for model in MODELS.values():
            for v in self.data['vectors']:
                with self.subTest(model=model.kind,vector=v['id']),tempfile.TemporaryDirectory() as folder:
                    core(self.data,model,v,folder)

    def test_native_stale_wrapper_conflicts_and_safe_rebuild(self):
        initial=self.data['vectors'][0]['initial_state']
        for cls in MODELS.values():
            with self.subTest(model=cls.kind):
                m=cls(self.data,initial); stale=m.build(self.data['intents']['pay10'])
                i=self.data['intents']['pay12_d2']; self.assertEqual(m.include(i,m.build(i),1),'success')
                result=m.include(self.data['intents']['pay10'],stale,2)
                if cls.kind=='accounts': self.assertEqual(result,'revert:principal_budget')
                else:
                    self.assertEqual(result,'structural_reject')
                    fresh=m.build(self.data['intents']['pay10'])
                    self.assertEqual(m.include(self.data['intents']['pay10'],fresh,2),'revert:principal_budget')
                self.assertEqual(m.project()['fee_sink'],2)
                invariants(m.project(),self.data['vectors'][0]['initial_supply'],self.data)
                native_audit(cls.kind,m.native(),self.data['vectors'][0]['initial_supply'])

    def test_harness_catches_false_success_and_wrong_owner(self):
        v=next(v for v in self.data['vectors'] if v['id']=='V12'); e=v['steps'][1]['expect']
        bad=copy.deepcopy(e['ledger']);bad['credits']['C']['owner']='H'
        with self.assertRaises(ComparisonFailure): invariants(bad,v['initial_supply'],self.data)
        with self.assertRaises(ComparisonFailure): compare('success',v['initial_state'],e['client'],e,self.data)

    def test_bad_wire_and_wrong_signature_never_debit(self):
        for cls in MODELS.values():
            m=cls(self.data,self.data['vectors'][0]['initial_state']); before=m.project()
            i=self.data['intents']['wrong_key']
            self.assertEqual(m.include(i,m.build(i),1),'reject:signature'); self.assertEqual(m.project(),before)
            broken=copy.deepcopy(self.data['intents']['pay10']);broken['preimage_hex']+='00'
            with self.assertRaises(Exception): m.build(broken)
            self.assertEqual(m.project(),before)

    def test_native_owner_and_value_audit_is_independent(self):
        initial=self.data['vectors'][0]['initial_state']; supply=self.data['vectors'][0]['initial_supply']
        m=MODELS['eutxo'](self.data,initial); native=m.native()
        first=next(iter(native['outputs'])); native['outputs'][first]['value']+=1
        with self.assertRaises(ComparisonFailure): native_audit('eutxo',native,supply)
        m=MODELS['objects'](self.data,initial);native=m.native()
        native['objects']['balances:H']['owner']='X'
        with self.assertRaises(ComparisonFailure): native_audit('objects',native,supply)

    def test_crash_journal_and_contradiction_latch(self):
        from research.native_l1.client import Client
        v=next(v for v in self.data['vectors'] if v['id']=='V11')
        with tempfile.TemporaryDirectory() as folder:
            c=Client(v['initial_client'],Path(folder)/'j.json',self.data['actors'])
            for event in [dict(type='prepare',intent='pay10'),dict(type='submit',intent='pay10'),dict(type='crash')]:
                c.event(event,self.data['intents'],wrapper={'intent_id':self.data['intents']['pay10']['intent_id']})
            self.assertEqual(c.state['principal_reserved'],10)
            self.assertEqual(c.event(dict(type='recover'),{},self.data['observations']['conflicting_pay10']), 'halted:contradiction')
            self.assertEqual(c.event(dict(type='recover'),{},self.data['observations']['final_pay10'],'success'),'halted:contradiction')
            self.assertEqual(c.state['principal_reserved'],10)

    def test_all_signed_stress_artifacts(self):
        from research.native_l1.verify_stress import verify
        stress=json.loads((ROOT/'research/native_l1/evidence/stress-input-v1.json').read_text())
        plan=json.loads((ROOT/'research/fixtures/native_l1/v1/stress_plan.json').read_text())
        verify(stress,self.data,plan)
        self.assertEqual(sum(len(c['operations']) for c in stress['cases']),3330)


if __name__=='__main__': unittest.main()
