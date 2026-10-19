"""Expose the current eUTXO recipient-pool assumption using frozen signed inputs."""
import json
from pathlib import Path
from research.native_l1.models.eutxo import EUTXO

root=Path(__file__).resolve().parents[3]
data=json.loads((root/'research/fixtures/native_l1/v1/corpus.json').read_text())
m=EUTXO(data,data['vectors'][0]['initial_state'])
for label,tick in [('pay12',1),('pay8',2)]:
    i=data['intents'][label];assert m.include(i,m.build(i),tick)=='success'
native=m.native();last=native['transactions'][-1]
old=[dict(id=i,**native['outputs'][i]) for i in last['inputs'] if native['outputs'][i]['table']=='balances' and native['outputs'][i]['key']=='S']
new=[dict(id=i,**native['outputs'][i]) for i in last['outputs'] if native['outputs'][i]['table']=='balances' and native['outputs'][i]['key']=='S']
assert len(old)==len(new)==1 and old[0]['value']==12 and new[0]['value']==20
print(json.dumps(dict(source_commit='6872f4b2a208f70074b67bbd47e9095043e0dc18',signed_inputs=['pay12','pay8'],second_intent_actor='D2',recipient='S',recipient_input=old[0],recipient_successor=new[0],recipient_signature_supplied=False,interpretation='The typed adapter consumes a recipient balance-pool output on top-up. Value/owner are preserved, but this is not a conventional recipient-signature coin spend. A public top-up covenant would need explicit specification and independent output-condition validation; do not credit ordinary owner-locked UTXO behavior from this result.'),indent=2))
