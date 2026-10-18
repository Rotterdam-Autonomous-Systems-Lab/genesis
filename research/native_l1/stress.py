"""Expand frozen deterministic stress rules once, before measurements.

Keys are ephemeral and never serialized. The signed public artifact is the replay
input; regenerate only for an explicitly new research run, not each repetition.
"""
import copy
import hashlib
import json
from pathlib import Path
from Crypto.PublicKey import ECC
from Crypto.Signature import eddsa
from .common import codec, DOMAIN, digest, packed


def portable(v):
    if isinstance(v,bytes): return {'bytes':v.hex()}
    if isinstance(v,list): return [portable(x) for x in v]
    return v


def expand(corpus,plan):
    roles=['H','B','S']+[f'D{i:02}' for i in range(32)]
    keys={r:ECC.generate(curve='Ed25519') for r in roles}
    actors={r:dict(id=hashlib.sha256(('genesis-lab018-stress:'+r).encode()).hexdigest(),public_key=keys[r].public_key().export_key(format='raw').hex()) for r in roles}
    raw=lambda r:bytes.fromhex(actors[r]['id'])
    sign=lambda r,h:eddsa.new(keys[r],'rfc8032').sign(bytes.fromhex(h))
    cases=[]
    ordered=sorted(roles[3:],key=lambda r:actors[r]['id'])
    for case in plan['cases']:
        n,c=case['delivered_actions'],case['active_clients']; clients=ordered[:c]
        groups=([[r] for r in clients] if case['sharing']=='disjoint' or c==1 else [clients] if case['sharing']=='shared' else [clients[:c//2]]+[[r] for r in clients[c//2:]])
        state=dict(balances={r:100 if r not in ('H','S') else 10000 if r=='H' else 0 for r in roles},epochs={r:0 for r in roles},grants={},agreements={},credits={},consumed={},fee_sink=0)
        manifest=dict(network_id=corpus['network_id'],service_id=corpus['service_id'],actors=actors,aliases=dict(grants={},agreements={},credits={}),terms={},intents={})
        operations=[]; assignment={}
        def intent(label,actor,seq,op,args):
            u=[1,bytes.fromhex(corpus['network_id']),raw(actor),0,seq,30,1,op,args]
            pre=codec.encode([DOMAIN,u]); h=hashlib.sha256(pre).hexdigest()
            manifest['intents'][label]=dict(unsigned=portable(u),preimage_hex=pre.hex(),intent_id=h,signature=sign(actor,h).hex(),signer=actor)
            operations.append(label)
        for index,group in enumerate(groups):
            seq=index+1; gid=bytes.fromhex(digest([DOMAIN,2,bytes.fromhex(corpus['network_id']),raw('H'),seq])); label='G'+str(index)
            manifest['aliases']['grants'][label]=gid.hex()
            P=sum(3000//c+(clients.index(r)<3000%c) for r in group); F=P
            for r in group: assignment[r]=gid
            intent('setup'+str(index),'H',seq,2,[gid,[[raw(r),0] for r in group],[1,5],sorted([raw('B'),raw('S')]),P,F,40])
        for i in range(n-len(groups)):
            actor=clients[i%c]; amount=1+i%3; salt=hashlib.sha256((case['id']+':'+str(i)).encode()).digest()
            if i%2==0: op,args=1,[assignment[actor],0,raw('S'),amount,salt]
            else:
                terms=[bytes.fromhex(corpus['network_id']),raw('H'),raw('B'),salt,bytes.fromhex(corpus['service_id']),7,11,amount,10,20]
                h=digest([DOMAIN,5,terms]); name='A'+str(i)
                manifest['terms'][name]=dict(array=portable(terms),agreement_id=h,requester_signature=sign('H',h).hex(),provider_signature=sign('B',h).hex())
                manifest['aliases']['agreements'][name]=h
                op,args=5,[assignment[actor],0,terms,sign('H',h),sign('B',h)]
            intent('action'+str(i),actor,1+i//c,op,args)
        cases.append(dict(id=case['id'],initial_state=state,initial_supply=sum(state['balances'].values()),manifest=manifest,operations=operations))
    return dict(version=1,source_plan_sha256=hashlib.sha256(packed(plan)).hexdigest(),cases=cases)


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(); p.add_argument('--output',required=True); a=p.parse_args()
    dest=Path(a.output)
    if dest.exists(): raise SystemExit('Refusing to overwrite signed run input')
    corpus=json.loads(Path('research/fixtures/native_l1/v1/corpus.json').read_text())
    plan=json.loads(Path('research/fixtures/native_l1/v1/stress_plan.json').read_text())
    dest.write_bytes(packed(expand(corpus,plan))+b'\n')
    print(hashlib.sha256(dest.read_bytes()).hexdigest(),str(dest))
