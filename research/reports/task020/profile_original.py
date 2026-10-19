"""Unscored diagnostic of original frozen adapter; no cap or corpus modification."""
import cProfile,io,json,pstats,time
from pathlib import Path
from research.native_l1.models.eutxo import EUTXO
from research.native_l1.common import packed

def main():
 c=next(c for c in json.loads(Path('research/native_l1/evidence/stress-input-v1.json').read_text())['cases'] if c['id']=='S09')
 m=EUTXO(c['manifest'],c['initial_state']); wire=0; checkpoints=[]; prof=cProfile.Profile();prof.enable();start=time.monotonic()
 for n,label in enumerate(c['operations'],1):
  i=c['manifest']['intents'][label];w=m.build(i)
  wire+=len(packed(dict(build=i['intent_id'])))+len(packed(dict(wrapper=w)))
  result=m.include(i,w,1);assert result=='success'
  obs=dict(kind='oracle',intent=label,outcome='success',final=True,fenced=False)
  wire+=len(packed(dict(preimage_hex=i['preimage_hex'],signature=i['signature'],wrapper=w)))+len(packed(dict(outcome=result,intent=i['intent_id'])))
  wire+=len(packed(dict(query=label)))+len(packed(dict(observation=obs)))
  if n in (10,100,500,1000):checkpoints.append(dict(actions=n,wire_bytes=wire,link_lower_bound_seconds=wire/10240,native_bytes=len(packed(m.native()))))
 prof.disable();out=io.StringIO();pstats.Stats(prof,stream=out).sort_stats('cumulative').print_stats(18)
 print(json.dumps(dict(profile='original-memory-only; excludes fsync, subprocess, client and harness',elapsed_seconds=time.monotonic()-start,checkpoints=checkpoints,cprofile=out.getvalue()),indent=2))
if __name__=='__main__':main()
