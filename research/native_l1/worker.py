"""JSON-lines worker with separately measured operation/persistence/observation."""
import copy,json,os,resource,sys,time
from pathlib import Path
from collections import defaultdict
from .common import packed
from .devcheck import MODELS
from .client import Client


def main():
    folder=Path(sys.argv[2]);folder.mkdir(parents=True,exist_ok=True)
    client_mode=sys.argv[1]=='client';limit=128*1024**2 if client_mode else 1024**3
    if sys.platform=='linux':
        resource.setrlimit(resource.RLIMIT_AS,(limit,limit))
        os.sched_setaffinity(0,{min(os.sched_getaffinity(0))})
    resource.setrlimit(resource.RLIMIT_CPU,(120,120))
    model=None;checkpoint=None;client=None;high=0;max_state=0;registry_bytes=0
    components=defaultdict(lambda:dict(calls=0,wall_seconds=0,cpu_seconds=0))
    def measure(name,work):
        w=time.perf_counter();c=time.process_time()
        try:return work()
        finally:
            t=components[name];t['calls']+=1;t['wall_seconds']+=time.perf_counter()-w;t['cpu_seconds']+=time.process_time()-c
    for line in sys.stdin:
        try:
            start=time.perf_counter();cpu=time.process_time();msg=measure('ipc_decode',lambda:json.loads(line));command=msg['command']
            result=None;wrapper=None
            def operation():
                nonlocal model,checkpoint,client,result,wrapper,registry_bytes
                if command=='init':
                    if client_mode:client=Client(msg['initial'],folder/'journal.json',msg.get('actors'))
                    else:
                        model=MODELS[sys.argv[1]](msg['manifest'],msg['initial']);checkpoint=copy.deepcopy(model)
                        raw=packed(dict(manifest=model.ctx.manifest,term_names=model.ctx.term_names,labels=model.labels,actor_index={k.hex():v for k,v in model.ctx.actors.items()},alias_index={kind:{k.hex():v for k,v in values.items()} for kind,values in model.ctx.aliases.items()}))
                        registry_bytes=len(raw)
                        with (folder/'registry.json').open('wb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
                elif command=='build':wrapper=model.build(msg['intent'])
                elif command=='include':result=model.include(msg['intent'],msg['wrapper'],msg['tick'])
                elif command=='rollback':
                    metrics=model.ctx.metrics.copy();timings=copy.deepcopy(model.ctx.timings)
                    model=copy.deepcopy(checkpoint);model.ctx.metrics=metrics;model.ctx.timings=timings;result='orphaned'
                elif command=='client':result=client.event(msg['event'],msg.get('intents',{}),msg.get('observation'),msg.get('known'),msg.get('wrapper'))
                elif command!='finish':raise RuntimeError('worker command')
            measure(command,operation)
            if not client_mode and command in ('init','include','rollback'):
                def persist():
                    nonlocal max_state
                    raw=packed(model.native());max_state=max(max_state,len(raw))
                    if len(raw)+registry_bytes>256*1024**2:raise RuntimeError('state storage cap')
                    with (folder/'native.json').open('wb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
                measure('native_persistence',persist)
            elapsed=time.perf_counter()-start;used=time.process_time()-cpu
            projection=measure('observation_projection',lambda:copy.deepcopy(client.state) if client_mode else model.project())
            rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            if sys.platform!='darwin':rss*=1024
            high=max(high,rss)
            if high>limit:raise RuntimeError('peak RSS cap')
            answer=dict(ok=True,result=result,wrapper=wrapper,projection=projection,seconds=elapsed,cpu_seconds=used,peak_rss_bytes=high,state_bytes=max_state,memory_limit_enforced=sys.platform=='linux',affinity_enforced=sys.platform=='linux',process_cpu_seconds=time.process_time(),components=dict(components),registry_bytes=registry_bytes,total_state_bytes=max_state+registry_bytes)
            if client_mode:answer.update(flushes=client.flushes,journal_bytes=client.journal_bytes,signature_verifications=client.verifications,hash_calls=client.hash_calls,hashed_bytes=client.hashed_bytes)
            else:answer.update(operations=dict(model.ctx.metrics),verification_timings=model.ctx.timings)
            if command=='finish' and not client_mode:answer['native']=model.native()
            encoded=measure('ipc_encode',lambda:json.dumps(answer,separators=(',',':')))
            print(encoded,flush=True)
            if command=='finish':
                # A second tiny envelope measures the large final response AFTER
                # encoding/flush, so the reported HWM includes native audit IPC.
                peak=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
                if sys.platform!='darwin':peak*=1024
                print(json.dumps(dict(final_meter=True,peak_rss_bytes=peak,process_cpu_seconds=time.process_time(),components=dict(components)),separators=(',',':')),flush=True)
                break
        except Exception as error:
            print(json.dumps(dict(ok=False,error=type(error).__name__+': '+str(error))),flush=True);return 1
    return 0

if __name__=='__main__':sys.exit(main())
