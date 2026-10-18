"""Quick semantic checks; not a measured or independent reproduction run."""
import copy
import json
import tempfile
from pathlib import Path
from .models.accounts import Accounts
from .models.objects import Objects
from .models.eutxo import EUTXO
from .client import Client
from .checks import compare,invariants

MODELS={c.kind:c for c in (Accounts,Objects,EUTXO)}


def core(manifest,cls,vector,folder):
    m=cls(manifest,vector['initial_state']); checkpoint=copy.deepcopy(m)
    c=Client(vector['initial_client'],Path(folder)/'journal.json')
    last=vector['initial_state']; trace=[]
    for index,step in enumerate(vector['steps']):
        e=step['event']; typ=e['type']; known=None
        if typ=='include':
            intent=manifest['intents'][e['intent']]
            result=m.include(intent,m.build(intent),e['tick'])
            c.event(e,manifest['intents'])
        elif typ=='rollback':
            m=copy.deepcopy(checkpoint); result=c.event(e,manifest['intents'])
        else:
            obs=manifest['observations'].get(e.get('observation'))
            if obs and 'intent' in obs:
                label=obs['intent']; u=manifest['intents'][label]['unsigned']
                actor=next(n for n,v in manifest['actors'].items() if v['id']==u[2]['bytes'])
                entry=m.project()['consumed'].get(actor+':'+str(u[4]))
                if entry and manifest['intents'][entry['intent']]['intent_id']==manifest['intents'][label]['intent_id']: known=entry['outcome']
            wrapper=m.build(manifest['intents'][e['intent']]) if typ in ('submit','attempt') else None
            result=c.event(e,manifest['intents'],obs,known,wrapper)
        state=m.project()
        try:
            invariants(state,vector['initial_supply'],manifest,last,typ=='rollback')
            compare(result,state,c.state,step['expect'],manifest)
        except AssertionError as error:
            raise AssertionError(f'{cls.kind} {vector["id"]} step {index}: {error}') from error
        last=state; trace.append(dict(index=index,event=e,result=result,state=state,client=copy.deepcopy(c.state)))
    return trace


if __name__=='__main__':
    x=json.loads(Path('research/fixtures/native_l1/v1/corpus.json').read_text())
    for cls in MODELS.values():
        for v in x['vectors']:
            with tempfile.TemporaryDirectory() as d: core(x,cls,v,d)
        print(cls.kind, '21 core vectors PASS (development check only)')
