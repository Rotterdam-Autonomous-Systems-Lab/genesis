"""Independent bounded runner; public JSON summaries and compressed full traces."""
import argparse
import copy
import gzip
import gc
import hashlib
import json
import os
import platform
import selectors
import shutil
import subprocess
import sys
import tempfile
import time
from collections import Counter
from pathlib import Path
from .common import ROOT,codec,packed
from .checks import require,invariants,compare,canonical,audit_pool_transactions
from .verify_stress import verify as verify_stress
from .resources import RunMonitor,rss_bytes

EVIDENCE=ROOT/'research/native_l1/evidence'
CORE=ROOT/'research/fixtures/native_l1/v1/corpus.json'


class Process:
    def __init__(self,kind,folder):
        self.p=subprocess.Popen([sys.executable,'-m','research.native_l1.worker',kind,str(folder)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,bufsize=1)
        self.start=time.monotonic(); self.metrics=Counter(); self.last={}; self.ipc=0
    def call(self,command,**fields):
        raw=json.dumps(dict(command=command,**fields),separators=(',',':'))+'\n'
        self.p.stdin.write(raw); self.p.stdin.flush(); self.ipc+=len(raw.encode())
        selector=selectors.DefaultSelector(); selector.register(self.p.stdout,selectors.EVENT_READ)
        ready=selector.select(max(0,180-(time.monotonic()-self.start))); selector.close()
        if not ready:
            self.p.kill(); raise RuntimeError('180-second run watchdog')
        line=self.p.stdout.readline(); self.ipc+=len(line.encode())
        if not line: raise RuntimeError('worker exited: '+self.p.stderr.read()[:1000])
        reply=json.loads(line); require(reply.get('ok'),str(reply))
        if command=='finish':
            meter_line=self.p.stdout.readline();self.ipc+=len(meter_line.encode())
            meter=json.loads(meter_line);require(meter.pop('final_meter',False),'missing final resource meter')
            reply.update(meter)
        self.metrics['seconds']+=reply['seconds']; self.metrics['cpu_seconds']+=reply['cpu_seconds']
        self.last=reply; return reply
    def close(self,deadline=None):
        if self.p.poll() is None:
            self.p.stdin.close()
            try: self.p.wait(timeout=max(0,deadline-time.monotonic()) if deadline is not None else 15)
            except subprocess.TimeoutExpired: self.p.kill(); self.p.wait(); raise RuntimeError('cleanup timeout')
        self.p.stdout.close(); self.p.stderr.close()


def native_audit(kind,native,initial_supply,manifest=None):
    if kind=='objects':
        for obj in native['objects'].values():
            expected=obj['key'] if obj['table'] in ('balances','epochs') else obj['data'].get('owner') if obj['table']=='credits' else 'shared'
            require(obj['owner']==expected and obj['version']>=0,'native object ownership/version')
    if kind=='eutxo':
        outputs,spent,live=native['outputs'],native['spent'],native['live']
        require(set(outputs)-set(spent)==set(live.values()),'live output index completeness')
        require(sum(outputs[i]['value'] for i in live.values())==initial_supply,'native output supply')
        seen=set()
        for tx in native['transactions']:
            require(len(set(tx['inputs']))==len(tx['inputs']) and not seen.intersection(tx['inputs']),'double consumed output')
            seen.update(tx['inputs'])
            require(sum(outputs[i]['value'] for i in tx['inputs'])==sum(outputs[i]['value'] for i in tx['outputs']),'native transaction conservation')
            for i in tx['inputs']: require(spent.get(i)==tx['id'],'spent attribution')
        require(seen==set(spent),'hidden consumed output')
        for out in outputs.values():
            t,d=out['table'],out['datum']
            expected='script:balance-pool-v1:'+out['key'] if t=='balances' else out['key'] if t in ('epochs','registry') else d.get('owner') if t=='credits' else 'script:'+t
            require(out['lock']==expected,'native output lock')
            value=d if t in ('balances','fee') else d['principal_pool']+d['fee_pool'] if t=='grants' else d['price'] if t=='agreements' and d['state']=='Funded' else d['amount'] if t=='credits' and d['status']=='outstanding' else 0
            require(out['value']==value,'datum/value binding')
        if manifest is not None: audit_pool_transactions(native,manifest)


def known_outcome(state,manifest,label):
    i=manifest['intents'][label]; u=i['unsigned']
    actor=next(n for n,a in manifest['actors'].items() if a['id']==u[2]['bytes'])
    r=state['consumed'].get(actor+':'+str(u[4]))
    return r['outcome'] if r and manifest['intents'][r['intent']]['intent_id']==i['intent_id'] else None



def state_delta(previous,current):
    """Lossless row delta; complete reconstruction from the preceding snapshot."""
    put={}; remove={}
    for table,rows in current.items():
        if not isinstance(rows,dict):
            if rows!=previous[table]: put[table]=rows
        else:
            changed={k:v for k,v in rows.items() if previous[table].get(k)!=v}
            deleted=sorted(set(previous[table])-set(rows))
            if changed: put[table]=changed
            if deleted: remove[table]=deleted
    return dict(put=put,remove=remove)


def run_case(kind,case,manifest,folder,trace,stress=False):
    harness_cpu_start=time.process_time()
    worker=Process(kind,folder/'worker'); client=Process('client',folder/'client')
    monitor=RunMonitor([worker,client]);checked=0;logical_rows=0;max_transport=0;max_wrapper=0;logical_bytes=0;max_envelope=0
    counters=Counter(); network=Counter(); wrapper_bytes=0; rate=10240 if case['id'] in ('V10','V16','S09') else None
    link_start=time.monotonic(); wire=0; peak_pending=0
    def traffic(actor,request,reply):
        nonlocal wire,max_envelope
        max_envelope=max(max_envelope,len(packed(request)),len(packed(reply)))
        require(max_envelope<=65536,'transport envelope cap')
        count=len(packed(request))+len(packed(reply)); network[actor]+=count; wire+=count
        require(network[actor]<=16*1024**2,'client bandwidth cap')
        if time.monotonic()-link_start>180: raise RuntimeError('180-second run watchdog cap')
        if rate:
            target=link_start+wire/rate
            if target>time.monotonic(): time.sleep(target-time.monotonic())
    try:
        state=worker.call('init',manifest={k:manifest[k] for k in ('actors','aliases','terms','intents','network_id','service_id')},initial=case['initial_state'])['projection']
        initial_native_bytes=worker.last['state_bytes'];previous_operations=worker.last.get('operations',{})
        initial_client=case.get('initial_client',dict(status='idle',principal_reserved=0,fee_reserved=0,queries=0,submissions=0,unresolved=[]))
        c=client.call('init',initial=initial_client,actors=manifest['actors'])['projection']
        invariants(state,case['initial_supply'],manifest)
        if stress:
            steps=[dict(event=dict(type='include',intent=n,tick=1)) for n in case['operations']]
        else: steps=case['steps']
        trace.write(json.dumps(dict(model=kind,case=case['id'],initial_ledger=state,initial_client=c),separators=(',',':'))+'\n')
        previous=state; expected_stress=copy.deepcopy(case['initial_state'])
        for index,step in enumerate(steps):
            event=step['event']; typ=event['type']; wrapper=None
            if typ=='include':
                label=event['intent']; intent=manifest['intents'][label]
                wrapper=worker.call('build',intent=intent)['wrapper']
                actor=next(n for n,a in manifest['actors'].items() if a['id']==intent['unsigned'][2]['bytes'])
                traffic(actor,dict(build=intent['intent_id']),dict(wrapper=wrapper))
                logical_size=len(bytes.fromhex(intent['preimage_hex']))+64
                size=len(packed(wrapper))+logical_size
                max_transport=max(max_transport,size);max_wrapper=max(max_wrapper,len(packed(wrapper)));logical_bytes+=logical_size
                require(size<=65536,'transport ceiling'); wrapper_bytes+=size
                if stress:
                    client.call('client',event=dict(type='prepare',intent=label),intents={label:intent})
                    client.call('client',event=dict(type='submit',intent=label),intents={label:intent},wrapper=wrapper)
                reply=worker.call('include',intent=intent,wrapper=wrapper,tick=event['tick'])
                result=reply['result']; state=reply['projection']
                actor=next(n for n,a in manifest['actors'].items() if a['id']==intent['unsigned'][2]['bytes'])
                # Proxy traffic is the actual signed logical input + wrapper and receipt,
                # never the independent harness's full projection/debug channel.
                traffic(actor,dict(preimage_hex=intent['preimage_hex'],signature=intent['signature'],wrapper=wrapper),dict(outcome=result,intent=intent['intent_id']))
                c=client.call('client',event=event)['projection']
                if stress:
                    obs=dict(kind='oracle',intent=label,outcome='success',final=True,fenced=False)
                    response=client.call('client',event=dict(type='recover'),observation=obs,known=known_outcome(state,manifest,label))
                    c=response['projection']
                    require(response['result']=='reconciled','stress recovery')
                    traffic(actor,dict(query=label),dict(observation=obs))
                counters[result]+=1; counters['delivered_actions']+=1
            elif typ=='rollback':
                state=worker.call('rollback')['projection']; reply=client.call('client',event=event); result=reply['result']; c=reply['projection']
            else:
                obs=manifest['observations'].get(event.get('observation'))
                known=known_outcome(state,manifest,obs['intent']) if obs and 'intent' in obs else None
                if typ in ('submit','attempt'):
                    wrapper=worker.call('build',intent=manifest['intents'][event['intent']])['wrapper']
                intents={event['intent']:manifest['intents'][event['intent']]} if 'intent' in event else {}
                reply=client.call('client',event=event,intents=intents,observation=obs,known=known,wrapper=wrapper)
                result=reply['result']; c=reply['projection']
                traffic(case['client_actor'],dict(event=event,wrapper=wrapper,intents=intents),dict(result=result,observation=obs))
                counters[typ]+=1
                if result=='structural_reject': counters['injected_structural_rejects']+=1
            peak_pending=max(peak_pending,len(c['unresolved'])); require(peak_pending<=32,'pending cap')
            invariants(state,case['initial_supply'],manifest,previous,typ=='rollback')
            if stress:
                require(result=='success','stress transition did not succeed')
                stress_oracle(expected_stress,manifest,event['intent'])
                require(canonical(state,manifest)==canonical(expected_stress,manifest),'stress independent projection mismatch')
            else: compare(result,state,c,step['expect'],manifest)
            trace.write(json.dumps(dict(model=kind,case=case['id'],step=index,event=event,result=result,ledger_delta=state_delta(previous,state),client=c,verification_delta={k:v-previous_operations.get(k,0) for k,v in worker.last.get('operations',{}).items()},client_meter={k:client.last.get(k) for k in ('flushes','signature_verifications','hash_calls','hashed_bytes','journal_bytes')}),separators=(',',':'))+'\n')
            logical_rows+=sum(len(v) if isinstance(v,dict) else 1 for v in state_delta(previous,state)['put'].values())
            checked+=1;previous=state;previous_operations=worker.last.get('operations',{})
        final=worker.call('finish'); final_client=client.call('finish')
        native_audit(kind,final['native'],case['initial_supply'],manifest)
        trace.write(json.dumps(dict(model=kind,case=case['id'],native_final=final['native']),separators=(',',':'))+'\n')
        counters['native_structural_rejects']+=counters['structural_reject']
        monitor.sample()
        require(monitor.aggregate_cpu<=120,'aggregate CPU cap')
        return dict(initial_native_state_bytes=initial_native_bytes,end_to_end_wall_seconds=time.monotonic()-monitor.start,checked_barriers=checked,logical_rows_written=logical_rows,worker_components=final['components'],client_components=final_client['components'],verification_timings=final['verification_timings'],worker_process_cpu_seconds=final['process_cpu_seconds'],client_process_cpu_seconds=final_client['process_cpu_seconds'],aggregate_process_cpu_seconds=monitor.aggregate_cpu,harness_cpu_seconds=time.process_time()-harness_cpu_start,harness_peak_rss_bytes=rss_bytes(),harness_rss_scope='process-lifetime upper bound, includes instrument/harness state',registry_bytes=final['registry_bytes'],total_state_bytes=final['total_state_bytes'],max_wire_envelope_bytes=max_envelope,max_transport_bytes=max_transport,max_wrapper_bytes=max_wrapper,logical_signed_bytes=logical_bytes,client_hash_calls=final_client['hash_calls'],client_hashed_bytes=final_client['hashed_bytes'],resource_sampler_seconds=.02,case=case['id'],model=kind,status='PASS',counters=dict(counters),operations=final['operations'],transition_wall_seconds=worker.metrics['seconds'],worker_cpu_seconds=worker.metrics['cpu_seconds'],client_cpu_seconds=client.metrics['cpu_seconds'],client_wall_seconds=client.metrics['seconds'],worker_peak_rss_bytes=final['peak_rss_bytes'],client_peak_rss_bytes=final_client['peak_rss_bytes'],native_state_bytes=final['state_bytes'],journal_bytes=final_client['journal_bytes'],journal_flushes=final_client['flushes'],client_signature_verifications=final_client['signature_verifications'],client_network_bytes=dict(network),wire_wall_seconds=time.monotonic()-link_start,transport_bytes=wrapper_bytes,worker_harness_ipc_bytes=worker.ipc,client_harness_ipc_bytes=client.ipc,hard_memory_affinity_enforced=final['memory_limit_enforced'],final_projection_sha256=hashlib.sha256(packed(canonical(state,manifest))).hexdigest())
    except Exception as error:
        trace.write(json.dumps(dict(model=kind,case=case['id'],boundary_failure=dict(error=str(error),checked_barriers=checked,network_bytes=dict(network),wire_bytes=wire,aggregate_cpu_seconds=monitor.aggregate_cpu,last_worker_cpu=worker.last.get('process_cpu_seconds'),last_client=client.last.get('projection'),interpretation='last attempted transition may be unobserved; no non-inclusion inference')))+'\n')
        raise
    finally:
        try:monitor.close()
        finally:
            deadline=time.monotonic()+15
            worker.close(deadline); client.close(deadline)
            require(time.monotonic()<=deadline,'cleanup cap')


def stress_oracle(state,manifest,label):
    """Independent arithmetic-only oracle for frozen stress's Grant/Transfer/Fund.

    No candidate parser, admission, store or state-mutation helper is imported.
    """
    i=manifest['intents'][label]; u=i['unsigned']; args=u[8]
    name=lambda raw:next(n for n,a in manifest['actors'].items() if a['id']==raw['bytes'])
    actor=name(u[2]); op=u[7]
    gname=lambda raw:next(n for n,v in manifest['aliases']['grants'].items() if v==raw['bytes'])
    if op==2:
        gid=gname(args[0]); P,F=args[4:6]
        state['balances'][actor]-=P+F+1
        state['grants'][gid]=dict(owner=actor,owner_epoch=0,version=0,delegates=[name(d[0]) for d in args[1]],actions=args[2],recipients=[name(r) for r in args[3]],expires=args[6],principal_cap=P,fee_cap=F,principal_pool=P,fee_pool=F,principal_used=0,fee_used=0,principal_returned=0,fee_returned=0,status='active')
    else:
        grant=state['grants'][gname(args[0])]; amount=args[-2] if op==1 else args[2][7]
        grant['principal_pool']-=amount; grant['principal_used']+=amount; grant['fee_pool']-=1; grant['fee_used']+=1
        if op==1: state['balances'][name(args[-3])]+=amount
        else:
            t=args[2]; tn=next(n for n,v in manifest['terms'].items() if v['array']==t)
            state['agreements'][tn]=dict(requester=name(t[1]),provider=name(t[2]),price=t[7],fund_before=t[8],claim_before=t[9],result=0,state='Funded',terms=tn)
    state['fee_sink']+=1; state['consumed'][actor+':'+str(u[4])]=dict(intent=label,outcome='success')


def source_identity():
    files=sorted((ROOT/'research/native_l1').rglob('*.py'))+sorted((ROOT/'tests/native_l1').rglob('*.py'))
    return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}


def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--output',required=True); parser.add_argument('--repetitions',type=int,default=3); parser.add_argument('--models',nargs='+',default=['accounts','objects','eutxo']); parser.add_argument('--cases',nargs='*'); a=parser.parse_args()
    require(sys.flags.optimize==0,'optimized Python disables offline assertion controls')
    require(a.repetitions in (1,3),'bounded repetition count')
    out=Path(a.output); out.mkdir(parents=True,exist_ok=False)
    corpus=json.loads(CORE.read_text()); codec.validate()
    stress=json.loads((EVIDENCE/'stress-input-v1.json').read_text())
    verify_stress(stress,corpus,json.loads((CORE.parent/'stress_plan.json').read_text()))
    lock=json.loads((EVIDENCE/'source-lock.json').read_text())
    require(source_identity()==lock['sources'],'source freeze mismatch')
    import Crypto
    require(platform.python_version()==lock['python'] and Crypto.__version__==lock['pycryptodome'],'runtime pin mismatch')
    require(hashlib.sha256(CORE.read_bytes()).hexdigest()==lock['corpus_sha256'],'corpus freeze mismatch')
    require(hashlib.sha256((ROOT/'sdk/python/requirements.lock').read_bytes()).hexdigest()==lock['requirements_sha256'],'dependency lock changed')
    require(hashlib.sha256((EVIDENCE/'stress-input-v1.json').read_bytes()).hexdigest()==lock['stress_sha256'],'stress artifact changed')
    summary=dict(version=2,source_lock=lock,environment=dict(platform=platform.platform(),isolation=dict(ci_run_id=os.getenv('GITHUB_RUN_ID'),replica=os.getenv('GENESIS_REPLICA'),host_sha256=hashlib.sha256(platform.node().encode()).hexdigest()),machine=platform.machine(),python=platform.python_version(),pycryptodome=Crypto.__version__,cpu_count=os.cpu_count(),processor=platform.processor(),affinity=sorted(os.sched_getaffinity(0)) if hasattr(os,'sched_getaffinity') else None,gc=dict(enabled=gc.isenabled(),thresholds=gc.get_threshold()),instrumentation='Task020; external20ms aggregate CPU/wall watchdog; separate harness RSS upper bound',command=sys.argv,cache_policy='one fresh-process warm-up; OS page cache uncontrolled and disclosed'),runs=[],decision='HOLD until complete validated evidence and independent environment reproduction')
    all_cases=[(v,corpus,False) for v in corpus['vectors']]+[(v,v['manifest'],True) for v in stress['cases']]
    if a.cases: all_cases=[entry for entry in all_cases if entry[0]['id'] in a.cases]
    start=time.monotonic()
    try:
        with gzip.open(out/'traces.jsonl.gz','wt',compresslevel=1) as trace:
            for kind in a.models:
                batch=time.monotonic()
                # Exactly one warm-up/model; retained and labeled, not a measured repeat.
                warm=all_cases[0]
                with tempfile.TemporaryDirectory(prefix='native-l1-warm-') as folder:
                    r=run_case(kind,*warm[:2],Path(folder),trace,warm[2]);r['warmup']=True;summary['runs'].append(r)
                for repetition in range(a.repetitions):
                    for case,manifest,is_stress in all_cases:
                        require(time.monotonic()-batch<1800,'model batch ceiling')
                        with tempfile.TemporaryDirectory(prefix='native-l1-run-') as folder:
                            try:
                                r=run_case(kind,case,manifest,Path(folder),trace,is_stress)
                            except Exception as error:
                                message=str(error)
                                if not any(word in message.lower() for word in ('cap','watchdog','worker exited','cleanup timeout')): raise
                                r=dict(case=case['id'],model=kind,status='HOLD',error=type(error).__name__+': '+message)
                                trace.write(json.dumps(dict(model=kind,case=case['id'],failure=r))+'\n')
                        r['repetition']=repetition; summary['runs'].append(r)
                        (out/'results.json').write_bytes(packed(summary)+b'\n')
                        print(kind,case['id'],repetition,r['status'],flush=True)
        grouped={}
        for r in summary['runs']:
            if not r.get('warmup') and r['status']=='PASS':
                signature=(r['final_projection_sha256'],r['counters'],r['operations'])
                key=(r['model'],r['case'])
                if key in grouped: require(grouped[key]==signature,'nondeterministic repeat')
                grouped[key]=signature
        full=len(all_cases)==30 and len(a.models)==3 and a.repetitions==3
        summary['decision']=('HOLD: retained resource failures' if any(r['status']!='PASS' for r in summary['runs']) else 'LOCAL CONFORMANCE PASS; hard memory/affinity unsupported on this platform' if not all(r.get('hard_memory_affinity_enforced') for r in summary['runs']) else 'ENVIRONMENT CONFORMANCE AND RESOURCE PASS; independent reproduction still required') if full else 'INCOMPLETE DEVELOPMENT RUN; NOT COMPARATIVE ACCEPTANCE'
    except Exception as error:
        summary['failure']=dict(type=type(error).__name__,message=str(error)); summary['decision']='FAIL / HOLD: invalid comparison stopped'
        raise
    finally:
        summary['elapsed_seconds']=time.monotonic()-start
        (out/'results.json').write_bytes(packed(summary)+b'\n')
    if full and any(r['status']!='PASS' for r in summary['runs']): raise SystemExit(2)


if __name__=='__main__': main()
