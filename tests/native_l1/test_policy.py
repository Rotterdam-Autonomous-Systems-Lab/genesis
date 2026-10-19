"""Adversarial spending-policy checks, outside measured run counts."""
import copy,json,unittest
from pathlib import Path
from research.native_l1.balance_policy import validate,lock
from research.native_l1.models.eutxo import EUTXO
from research.native_l1.runner import native_audit
from research.native_l1.checks import audit_pool_transactions,ComparisonFailure

class Policy(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads(Path('research/fixtures/native_l1/v1/corpus.json').read_text())

    def test_topup_preserves_claim_and_duplicates_never_merge(self):
        d=self.data;m=EUTXO(d,d['vectors'][0]['initial_state'])
        for name in ['pay12','pay8']:
            i=d['intents'][name];w=m.build(i)
            self.assertEqual(m.include(i,w,1),'success')
            before=copy.deepcopy(m.native())
            self.assertEqual(m.include(i,m.build(i),1),'duplicate')
            self.assertEqual(m.native(),before)
        self.assertEqual(m.read('balances','S'),20)
        native_audit('eutxo',m.native(),d['vectors'][0]['initial_supply'],d)
        self.assertEqual(sum(o['value'] for i,o in m.outputs.items() if i not in m.spent and o['table']=='balances' and o['key']=='S'),20)

    def test_arbitrary_pool_successors_reject_debit_theft_merge_and_overcredit(self):
        old=dict(table='balances',key='S',value=12,datum=12,lock=lock('S'))
        new=dict(old,value=20,datum=20)
        validate({'S':old},{'S':new},{'S':8})
        for field,value in [('key','D2'),('lock',lock('D2')),('value',19),('datum',19),('value',21)]:
            bad=dict(new);bad[field]=value
            with self.subTest(field=field,value=value),self.assertRaises(AssertionError):validate({'S':old},{'S':bad},{'S':8})
        with self.assertRaises(AssertionError):validate({'S':old},{},{'S':8})
        with self.assertRaises(AssertionError):validate({'S':old},{'S':dict(new,value=4,datum=4)},{'S':8})
        with self.assertRaises(AssertionError):validate({'S':old,'B':old},{'S':new},{'S':8})

    def test_independent_audit_catches_conserving_theft(self):
        d=self.data;m=EUTXO(d,d['vectors'][0]['initial_state']);i=d['intents']['pay12']
        self.assertEqual(m.include(i,m.build(i),1),'success');n=copy.deepcopy(m.native())
        out=next(n['outputs'][i] for i in n['transactions'][0]['outputs'] if n['outputs'][i]['table']=='balances')
        out['value']-=1;out['datum']-=1
        fee=next(n['outputs'][i] for i in n['transactions'][0]['outputs'] if n['outputs'][i]['table']=='fee')
        fee['value']+=1;fee['datum']+=1
        with self.assertRaises(ComparisonFailure):audit_pool_transactions(n,d)

    def test_full_width_references_and_stale_input_rejection(self):
        import base64
        d=self.data;m=EUTXO(d,d['vectors'][0]['initial_state']);i=d['intents']['pay12'];w=m.build(i)
        for r in w['references']:
            if r:self.assertEqual(len(base64.urlsafe_b64decode(r+'=')),32)
        broken=copy.deepcopy(w);broken['references'].pop()
        before=copy.deepcopy(m.native());self.assertEqual(m.include(i,broken,1),'structural_reject');self.assertEqual(before,m.native())
        self.assertEqual(m.include(i,w,1),'success')
        self.assertEqual(m.include(i,w,1),'structural_reject')
        self.assertEqual(m.include(i,m.build(i),1),'duplicate')

    def test_external_watchdog_kills_at_wall_boundary(self):
        import subprocess,sys,time
        from types import SimpleNamespace
        from research.native_l1.resources import RunMonitor
        p=subprocess.Popen([sys.executable,'-c','import time;time.sleep(10)'])
        handle=SimpleNamespace(p=p,start=time.monotonic()-181,last={})
        monitor=RunMonitor([handle]);monitor.thread.join(timeout=2)
        try:
            with self.assertRaisesRegex(RuntimeError,'180-second'):monitor.close()
            p.wait(timeout=2);self.assertNotEqual(p.returncode,0)
        finally:
            if p.poll() is None:p.kill();p.wait()

    def test_external_watchdog_aggregate_cpu_threshold(self):
        import subprocess,sys,time
        from types import SimpleNamespace
        from research.native_l1.resources import RunMonitor
        p=subprocess.Popen([sys.executable,'-c','import time;time.sleep(10)'])
        monitor=RunMonitor([SimpleNamespace(p=p,start=time.monotonic(),last={})])
        monitor.aggregate_cpu=121 # deterministic meter fault injection, no120s burn
        monitor.thread.join(timeout=2)
        try:
            with self.assertRaisesRegex(RuntimeError,'CPU cap'):monitor.close()
            p.wait(timeout=2);self.assertNotEqual(p.returncode,0)
        finally:
            if p.poll() is None:p.kill();p.wait()

    def test_proxy_charges_actual_build_preimage(self):
        import tempfile,gzip
        from unittest.mock import patch
        from research.native_l1.runner import Process,run_case
        calls=[];original=Process.call
        def capture(process,command,**fields):
            reply=original(process,command,**fields)
            if command in ('build','include'):calls.append((command,fields,reply))
            return reply
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory)
            with gzip.open(folder/'trace.gz','wt') as trace,patch.object(Process,'call',capture):
                result=run_case('eutxo',self.data['vectors'][0],self.data,folder/'case',trace)
        size=lambda value:len(json.dumps(value,sort_keys=True,separators=(',',':')).encode())
        expected=0;old_shortcut=0
        for command,fields,reply in calls:
            if command=='build':
                self.assertEqual(set(fields['intent']),{'preimage_hex'})
                actual=size({'build':fields['intent']})+size({'wrapper':reply['wrapper']})
                expected+=actual;old_shortcut+=size({'build':reply['wrapper']['intent_id']})+size({'wrapper':reply['wrapper']})
            else:
                i=fields['intent'];w=fields['wrapper']
                amount=size({'preimage_hex':i['preimage_hex'],'signature':i['signature'],'wrapper':w})+size({'outcome':reply['result'],'intent':i['intent_id']})
                expected+=amount;old_shortcut+=amount
        self.assertEqual(sum(result['client_network_bytes'].values()),expected)
        self.assertLess(old_shortcut,expected)

if __name__=='__main__':unittest.main()
