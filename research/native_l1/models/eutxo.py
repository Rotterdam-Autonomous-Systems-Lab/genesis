"""Extended UTXO: explicit value/datum outputs, input consumption and successors.

An actor replay-registry UTXO and grant-state UTXO serialize shared authority.
This is an illustrative script profile, not Bitcoin Script or a deployed EUTXO VM.
"""
import copy
import base64
from ..balance_policy import lock as pool_lock, validate as validate_pools, authorized_deltas
from ..common import Context, Reject, DOMAIN, digest, packed


class EUTXO:
    kind='eutxo'

    def __init__(self,manifest,initial):
        self.ctx=Context(manifest)
        self.labels={v['intent_id']:k for k,v in reversed(list(manifest['intents'].items()))}
        self.outputs={}; self.live={}; self.spent={}; self.transactions=[]
        for table,rows in initial.items():
            if table in ('fee_sink','consumed'): continue
            for key,data in rows.items(): self.create('genesis',table,key,data)
        for actor in manifest['actors']:
            registry={}
            for key,r in initial['consumed'].items():
                if key.startswith(actor+':'):
                    registry[key.split(':')[1]]=dict(intent_id=manifest['intents'][r['intent']]['intent_id'],outcome=r['outcome'])
            self.create('genesis','registry',actor,registry)
        if initial['fee_sink']: self.create('genesis','fee','initial',initial['fee_sink'])

    @staticmethod
    def amount(table,data):
        if table in ('balances','fee'): return data
        if table=='grants': return data['principal_pool']+data['fee_pool']
        if table=='agreements': return data['price'] if data['state']=='Funded' else 0
        if table=='credits': return data['amount'] if data['status']=='outstanding' else 0
        return 0

    def create(self,tx,table,key,data):
        outid=self.ctx.hash_bytes(packed([tx,table,key]))
        if outid in self.outputs: raise AssertionError('output identity reuse')
        lock=pool_lock(key) if table=='balances' else key if table in ('epochs','registry') else data.get('owner') if table=='credits' else 'script:'+table
        self.outputs[outid]=dict(table=table,key=key,value=self.amount(table,data),datum=copy.deepcopy(data),lock=lock)
        self.live[table+':'+key]=outid
        return outid

    def read(self,table,key):
        self.ctx.metrics['reads']+=1
        if table=='fee_sink': return sum(o['value'] for i,o in self.outputs.items() if i not in self.spent and o['table']=='fee')
        if table=='consumed':
            actor,seq=key.split(':'); registry=self.read('registry',actor)
            return registry.get(seq)
        outid=self.live.get(table+':'+key)
        return copy.deepcopy(self.outputs[outid]['datum']) if outid else None

    def build(self,intent):
        p=self.ctx.parse(intent); op,a=p['op'],p['args']; actor=p['actor']
        keys=[('epochs',actor),('registry',actor)]
        # A delegated payment uses grant reserves, never the delegate's own coins.
        if op not in (1,5) or a[0]==bytes(32): keys.append(('balances',actor))
        if op in (1,3,4,5,9) and a[0]!=bytes(32): keys.append(('grants',self.ctx.alias('grants',a[0])))
        if op==1: keys.append(('balances',self.ctx.actor(a[-3])))
        if op in (6,7): keys.append(('agreements',self.ctx.alias('agreements',a[0])))
        if op==8: keys.append(('credits',self.ctx.alias('credits',a[0])))
        if op==2: keys.append(('grants',self.ctx.alias('grants',a[0])))
        if op==5:
            aid,_=self.ctx.terms_record(a[2]); keys.append(('agreements',aid))
        if op in (6,7):
            cid=self.ctx.alias('credits',bytes.fromhex(self.ctx.digest([a[0],2 if op==6 else 3])))
            keys.append(('credits',cid))
        if op in (1,5) and a[0]!=bytes(32):
            g=self.read('grants',self.ctx.alias('grants',a[0]))
            if g: keys.append(('epochs',g['owner']))
        # Ordered dependencies are implicit in the signed operation; full hashes, no truncation.
        refs=[self.live.get(t+':'+k) for t,k in sorted(set(keys))]
        return dict(kind=self.kind,intent_id=p['id'],references=[base64.urlsafe_b64encode(bytes.fromhex(i)).decode().rstrip('=') if i else None for i in refs])

    def include(self,intent,wrapper,tick):
        try:
            p=self.ctx.parse(intent)
            if wrapper!=self.build(intent): return 'structural_reject'
            self.ctx.authenticate(p,intent,self.read,tick)
        except Reject as e: return str(e)
        actor,a,op=p['actor'],p['args'],p['op']; successors={}; outcome='success'
        def datum(table,key):
            return copy.deepcopy(successors[(table,key)]) if (table,key) in successors else self.read(table,key)
        def successor(table,key,data): successors[(table,key)]=copy.deepcopy(data)
        def coin(owner,change): successor('balances',owner,datum('balances',owner)+change)
        budget=datum('grants',p['grant']) if 'grant' in p else None
        if op==1 or op==5:
            amount=a[-2] if op==1 else a[2][7]
            if budget is not None and amount>budget['principal_pool']: outcome='revert:principal_budget'
            if budget is None and datum('balances',actor)-p['ceiling']<amount: outcome='revert:balance'
            if outcome=='success' and op==5:
                aid,escrow=self.ctx.terms_record(a[2])
                if tick>=escrow['fund_before']: outcome='revert:fund_deadline'
                elif datum('agreements',aid) is not None: outcome='revert:agreement_state'
            if outcome=='success':
                if budget is None: coin(actor,-amount)
                else:
                    budget['principal_pool']-=amount; budget['principal_used']+=amount
                if op==1: coin(self.ctx.actor(a[-3]),amount)
                else: successor('agreements',aid,escrow)
        elif op==2:
            gid=self.ctx.alias('grants',a[0])
            if a[0].hex()!=self.ctx.digest([DOMAIN,2,p['u'][1],p['u'][2],p['sequence']]) or datum('grants',gid) is not None:
                outcome='revert:grant_identity'
            elif datum('balances',actor)-p['ceiling']<a[4]+a[5]: outcome='revert:balance'
            else:
                coin(actor,-a[4]-a[5])
                successor('grants',gid,dict(owner=actor,owner_epoch=p['epoch'],status='active',version=0,delegates=[self.ctx.actor(d[0]) for d in a[1]],recipients=[self.ctx.actor(r) for r in a[3]],actions=a[2],expires=a[6],principal_pool=a[4],principal_cap=a[4],principal_used=0,principal_returned=0,fee_pool=a[5],fee_cap=a[5],fee_used=0,fee_returned=0))
        elif op in (3,4,9):
            gid=self.ctx.alias('grants',a[0]); old=datum('grants',gid)
            if op==3: old['status']='revoked'
            elif op==4:
                if old['status']!='active': outcome='revert:grant_state'
                else:
                    old['version']+=1; old['delegates']=[self.ctx.actor(d[0]) for d in a[2]]
            elif old['status']=='returned' or (old['status']=='active' and tick<old['expires']): outcome='revert:grant_state'
            else:
                coin(actor,old['principal_pool']+old['fee_pool'])
                for field in ('principal','fee'):
                    old[field+'_returned']+=old[field+'_pool']; old[field+'_pool']=0
                old['status']='returned'
            if outcome=='success': successor('grants',gid,old)
        elif op in (6,7):
            aid=self.ctx.alias('agreements',a[0]); escrow=datum('agreements',aid)
            if escrow['state']!='Funded': outcome='revert:agreement_state'
            elif op==6 and tick>=escrow['claim_before']: outcome='revert:claim_deadline'
            elif op==7 and tick<escrow['claim_before']: outcome='revert:refund_deadline'
            else:
                t=self.ctx.manifest['terms'][escrow['terms']]['array']; answer=t[5]+t[6]
                self.ctx.metrics['predicates']+=int(op==6)
                if op==6 and int.from_bytes(a[1],'big')!=answer: outcome='revert:result'
                else:
                    escrow['state']='Settled' if op==6 else 'Refunded'; escrow['result']=answer if op==6 else 0
                    cid=self.ctx.alias('credits',bytes.fromhex(self.ctx.digest([a[0],2 if op==6 else 3])))
                    successor('agreements',aid,escrow)
                    successor('credits',cid,dict(agreement=aid,owner=actor,amount=escrow['price'],status='outstanding'))
        elif op==8:
            cid=self.ctx.alias('credits',a[0]); credit=datum('credits',cid)
            if credit['status']!='outstanding': outcome='revert:credit_state'
            else:
                coin(actor,credit['amount']); credit['status']='collected'; successor('credits',cid,credit)
        if budget is not None:
            budget['fee_pool']-=1; budget['fee_used']+=1; successor('grants',p['grant'],budget)
        else: coin(actor,-1)
        registry=datum('registry',actor)
        registry[str(p['sequence'])]=dict(intent_id=p['id'],outcome='success' if outcome=='success' else 'revert')
        successor('registry',actor,registry)
        inputs=[self.live[t+':'+k] for t,k in successors if t+':'+k in self.live]
        if len(set(inputs))!=len(inputs) or any(i in self.spent for i in inputs): raise AssertionError('double input')
        input_value=sum(self.outputs[i]['value'] for i in inputs)
        output_value=sum(self.amount(t,d) for (t,k),d in successors.items())+1
        if input_value!=output_value: raise AssertionError('script conservation')
        for (table,key),data in successors.items():
            if not 0<=self.amount(table,data)<=2**64-1: raise ArithmeticError('output value range')
        # Validate arbitrary proposed balance successors before changing any index.
        policy=dict(p)
        if op==1: policy['recipient']=self.ctx.actor(a[-3])
        if op==8: policy['credit']=self.ctx.alias('credits',a[0])
        if op==9: policy['return_grant']=self.ctx.alias('grants',a[0])
        deltas=authorized_deltas(policy,outcome,self.read)
        before={k:self.outputs[self.live['balances:'+k]] for t,k in successors if t=='balances'}
        after={k:dict(table='balances',key=k,lock=pool_lock(k),value=d,datum=d) for (t,k),d in successors.items() if t=='balances'}
        validate_pools(before,after,deltas)
        # Atomic validate/consume/create. Read references may be retained; write inputs cannot.
        tx=p['id']; created=[]
        for outid in inputs:
            self.spent[outid]=tx
            old=self.outputs[outid]; del self.live[old['table']+':'+old['key']]
        for (table,key),data in successors.items(): created.append(self.create(tx,table,key,data))
        created.append(self.create(tx,'fee',tx,1))
        self.transactions.append(dict(id=tx,inputs=inputs,outputs=created,outcome=outcome,tick=tick))
        self.ctx.metrics['scripts']+=len(inputs)
        self.ctx.metrics['consumed_outputs']+=len(inputs); self.ctx.metrics['created_outputs']+=len(created)
        self.ctx.metrics['writes']+=len(inputs)+len(created)
        return outcome

    def project(self):
        s={t:{} for t in ('balances','epochs','grants','agreements','credits','consumed')}; s['fee_sink']=0
        for outid in self.live.values():
            o=self.outputs[outid]; t,k,d=o['table'],o['key'],copy.deepcopy(o['datum'])
            if t=='fee': s['fee_sink']+=o['value']
            elif t=='registry':
                for seq,r in d.items(): s['consumed'][k+':'+seq]=dict(intent=self.labels[r['intent_id']],outcome=r['outcome'])
            else: s[t][k]=d
        return s

    def native(self): return dict(outputs=self.outputs,live=self.live,spent=self.spent,transactions=self.transactions)
