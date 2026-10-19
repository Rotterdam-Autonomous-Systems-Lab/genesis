"""Unscored S09 service-wire arithmetic; excludes IPC/persistence/timing claims."""
import json,sys,hashlib
from pathlib import Path
from research.native_l1.devcheck import MODELS

def size(value):return len(json.dumps(value,sort_keys=True,separators=(',',':')).encode())

def main():
    c=next(c for c in json.loads(Path('research/native_l1/evidence/stress-input-v1.json').read_text())['cases'] if c['id']=='S09')
    results=[]
    for kind,cls in MODELS.items():
        model=cls(c['manifest'],c['initial_state']);total=0;components=dict(build_requests=0,wrapper_replies=0,signed_submissions=0,receipts=0,recovery=0)
        for label in c['operations']:
            i=c['manifest']['intents'][label];build=dict(preimage_hex=i['preimage_hex']);wrapper=model.build(build)
            outcome=model.include(i,wrapper,1);assert outcome=='success'
            observation=dict(kind='oracle',intent=label,outcome='success',final=True,fenced=False)
            components['build_requests']+=size(dict(build=build));components['wrapper_replies']+=size(dict(wrapper=wrapper))
            components['signed_submissions']+=size(dict(preimage_hex=i['preimage_hex'],signature=i['signature'],wrapper=wrapper))
            components['receipts']+=size(dict(outcome=outcome,intent=i['intent_id']))
            components['recovery']+=size(dict(query=label))+size(dict(observation=observation))
        total=sum(components.values())
        results.append(dict(model=kind,actions=len(c['operations']),proxy_bytes=total,minimum_link_seconds=total/10240,component_bytes=components))
        print(kind,total,total/10240,file=sys.stderr,flush=True)
    print(json.dumps(dict(scope='unscored wire-footprint diagnostic; all input operations executed but no persistence/IPC/client timing benchmark',source_lock_sha256=hashlib.sha256(Path('research/native_l1/evidence/source-lock.json').read_bytes()).hexdigest(),models=results),indent=2))
if __name__=='__main__':main()
