"""Line-delimited JSON worker protocol; candidate and client are separate processes."""
import copy
import json
import os
import platform
import resource
import sys
import time
from pathlib import Path
from .common import packed
from .devcheck import MODELS
from .client import Client


def main():
    folder=Path(sys.argv[2]); folder.mkdir(parents=True,exist_ok=True)
    client_mode=sys.argv[1]=='client'
    limit=128*1024**2 if client_mode else 1024**3
    # RLIMIT_AS is stricter than RSS on Linux; macOS reports RSS and marks hard
    # memory/affinity enforcement unavailable rather than claiming equivalence.
    if sys.platform=='linux':
        resource.setrlimit(resource.RLIMIT_AS,(limit,limit))
        os.sched_setaffinity(0,{min(os.sched_getaffinity(0))})
    resource.setrlimit(resource.RLIMIT_CPU,(120,120))
    model=None; checkpoint=None; client=None; high=0; max_state=0
    for line in sys.stdin:
        try:
            msg=json.loads(line); start=time.perf_counter(); cpu=time.process_time(); command=msg['command']
            result=None; wrapper=None
            if command=='init':
                if client_mode: client=Client(msg['initial'],folder/'journal.json',msg.get('actors'))
                else:
                    model=MODELS[sys.argv[1]](msg['manifest'],msg['initial']); checkpoint=copy.deepcopy(model)
            elif command=='build': wrapper=model.build(msg['intent'])
            elif command=='include': result=model.include(msg['intent'],msg['wrapper'],msg['tick'])
            elif command=='rollback':
                metrics=model.ctx.metrics.copy(); model=copy.deepcopy(checkpoint); model.ctx.metrics=metrics
                result='orphaned'
            elif command=='client': result=client.event(msg['event'],msg.get('intents',{}),msg.get('observation'),msg.get('known'),msg.get('wrapper'))
            elif command=='finish': pass
            else: raise RuntimeError('worker command')
            if not client_mode and command in ('init','include','rollback'):
                raw=packed(model.native()); max_state=max(max_state,len(raw))
                if len(raw)>256*1024**2: raise RuntimeError('state storage cap')
                with (folder/'native.json').open('wb') as f:
                    f.write(raw); f.flush(); os.fsync(f.fileno())
            elapsed=time.perf_counter()-start; used=time.process_time()-cpu
            # Projection/assertion serialization is outside candidate transition time.
            projection=copy.deepcopy(client.state) if client_mode else model.project()
            rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            if sys.platform!='darwin': rss*=1024
            high=max(high,rss)
            if high>limit: raise RuntimeError('peak RSS cap')
            answer=dict(ok=True,result=result,wrapper=wrapper,projection=projection,seconds=elapsed,cpu_seconds=used,peak_rss_bytes=high,state_bytes=max_state,memory_limit_enforced=sys.platform=='linux',affinity_enforced=sys.platform=='linux')
            if client_mode: answer.update(flushes=client.flushes,journal_bytes=client.journal_bytes,signature_verifications=client.verifications)
            else: answer['operations']=dict(model.ctx.metrics)
            if command=='finish' and not client_mode: answer['native']=model.native()
            print(json.dumps(answer,separators=(',',':')),flush=True)
            if command=='finish': break
        except Exception as error:
            print(json.dumps(dict(ok=False,error=type(error).__name__+': '+str(error))),flush=True)
            return 1
    return 0


if __name__=='__main__': sys.exit(main())
