"""Versioned owned/shared resources; transactions replace a checked read/write set."""
import copy
from ..common import Context, Reject, DOMAIN, digest, packed


class Objects:
    kind='objects'

    def __init__(self, manifest, initial):
        self.ctx=Context(manifest)
        self.labels={v['intent_id']:k for k,v in reversed(list(manifest['intents'].items()))}
        self.objects={}; self.history=[]
        for table,rows in initial.items():
            for key,value in (rows.items() if isinstance(rows,dict) else [('sink',rows)]):
                value=copy.deepcopy(value)
                if table=='consumed': value=dict(intent_id=manifest['intents'][value['intent']]['intent_id'],outcome=value['outcome'])
                self.objects[table+':'+key]=self.resource(table,key,value,0)

    @staticmethod
    def resource(table,key,value,version):
        owner = key if table in ('balances','epochs') else value.get('owner') if table=='credits' else 'shared'
        return dict(table=table,key=key,owner=owner,version=version,data=copy.deepcopy(value))

    def read(self, table,key):
        self.ctx.metrics['reads']+=1
        resource=self.objects.get(table+':'+key)
        return copy.deepcopy(resource['data']) if resource else None

    def build(self,intent):
        p=self.ctx.parse(intent); op,a=p['op'],p['args']
        # Precise target refs plus payer/epoch/outcome; no global object-version shortcut.
        targets=[('epochs',p['actor']),('consumed',p['actor']+':'+str(p['sequence'])),('balances',p['actor'])]
        if op in (1,3,4,5,9) and a[0]!=bytes(32): targets.append(('grants',self.ctx.alias('grants',a[0])))
        if op in (6,7): targets.append(('agreements',self.ctx.alias('agreements',a[0])))
        if op==8: targets.append(('credits',self.ctx.alias('credits',a[0])))
        targets.append(('fee_sink','sink'))
        if op==1: targets.append(('balances',self.ctx.actor(a[-3])))
        if op==2: targets.append(('grants',self.ctx.alias('grants',a[0])))
        if op==5:
            aid,_=self.ctx.terms_record(a[2]); targets.append(('agreements',aid))
        if op in (6,7):
            cid=self.ctx.alias('credits',bytes.fromhex(digest([a[0],2 if op==6 else 3])))
            targets.append(('credits',cid))
        if op in (1,5) and a[0]!=bytes(32):
            g=self.read('grants',self.ctx.alias('grants',a[0]))
            if g: targets.append(('epochs',g['owner']))
        refs={t+':'+k:self.objects[t+':'+k]['version'] if t+':'+k in self.objects else -1 for t,k in targets}
        return dict(kind=self.kind,intent_id=p['id'],versions=refs)

    def include(self,intent,wrapper,tick):
        try:
            p=self.ctx.parse(intent)
            if wrapper!=self.build(intent): return 'structural_reject'
            self.ctx.authenticate(p,intent,self.read,tick)
        except Reject as e: return str(e)
        actor,op,a=p['actor'],p['op'],p['args']; writes={}; result='success'
        def get(t,k):
            return copy.deepcopy(writes[(t,k)]) if (t,k) in writes else self.read(t,k)
        def put(t,k,v): writes[(t,k)]=copy.deepcopy(v)
        def add(owner,amount): put('balances',owner,get('balances',owner)+amount)
        grant=get('grants',p['grant']) if 'grant' in p else None
        if op in (1,5):
            value=a[-2] if op==1 else a[2][7]
            if grant and value>grant['principal_pool']: result='revert:principal_budget'
            elif not grant and value+p['ceiling']>get('balances',actor): result='revert:balance'
            if result=='success' and op==5:
                agreement_id,agreement=self.ctx.terms_record(a[2])
                if tick>=agreement['fund_before']: result='revert:fund_deadline'
                elif get('agreements',agreement_id): result='revert:agreement_state'
            if result=='success':
                if grant:
                    grant['principal_used']+=value; grant['principal_pool']-=value
                else: add(actor,-value)
                if op==1: add(self.ctx.actor(a[-3]),value)
                else: put('agreements',agreement_id,agreement)
        elif op==2:
            key=self.ctx.alias('grants',a[0]); identity=digest([DOMAIN,2,p['u'][1],p['u'][2],p['sequence']])
            if get('grants',key) or identity!=a[0].hex(): result='revert:grant_identity'
            elif get('balances',actor)<a[4]+a[5]+p['ceiling']: result='revert:balance'
            else:
                add(actor,-a[4]-a[5])
                put('grants',key,dict(owner=actor,owner_epoch=p['epoch'],delegates=[self.ctx.actor(x[0]) for x in a[1]],actions=a[2],recipients=[self.ctx.actor(x) for x in a[3]],version=0,status='active',expires=a[6],principal_cap=a[4],principal_pool=a[4],principal_used=0,principal_returned=0,fee_cap=a[5],fee_pool=a[5],fee_used=0,fee_returned=0))
        elif op in (3,4,9):
            key=self.ctx.alias('grants',a[0]); resource=get('grants',key)
            if op==3: resource['status']='revoked'
            elif op==4:
                if resource['status']!='active': result='revert:grant_state'
                else:
                    resource['version']+=1; resource['delegates']=[self.ctx.actor(x[0]) for x in a[2]]
            elif resource['status']=='returned' or (resource['status']=='active' and tick<resource['expires']): result='revert:grant_state'
            else:
                add(actor,resource['principal_pool']+resource['fee_pool'])
                resource['principal_returned']+=resource['principal_pool']; resource['principal_pool']=0
                resource['fee_returned']+=resource['fee_pool']; resource['fee_pool']=0; resource['status']='returned'
            if result=='success': put('grants',key,resource)
        elif op in (6,7):
            key=self.ctx.alias('agreements',a[0]); agreement=get('agreements',key)
            if agreement['state']!='Funded': result='revert:agreement_state'
            elif op==6 and tick>=agreement['claim_before']: result='revert:claim_deadline'
            elif op==7 and tick<agreement['claim_before']: result='revert:refund_deadline'
            else:
                t=self.ctx.manifest['terms'][agreement['terms']]['array']; answer=t[5]+t[6]
                self.ctx.metrics['predicates']+=int(op==6)
                if op==6 and int.from_bytes(a[1],'big')!=answer: result='revert:result'
                else:
                    agreement.update(state='Settled' if op==6 else 'Refunded',result=answer if op==6 else 0)
                    credit=self.ctx.alias('credits',bytes.fromhex(digest([a[0],2 if op==6 else 3])))
                    put('agreements',key,agreement)
                    put('credits',credit,dict(agreement=key,owner=actor,amount=agreement['price'],status='outstanding'))
        elif op==8:
            key=self.ctx.alias('credits',a[0]); credit=get('credits',key)
            if credit['status']!='outstanding': result='revert:credit_state'
            else:
                add(actor,credit['amount']); credit['status']='collected'; put('credits',key,credit)
        if grant:
            grant['fee_used']+=1; grant['fee_pool']-=1; put('grants',p['grant'],grant)
        else: add(actor,-1)
        put('fee_sink','sink',get('fee_sink','sink')+1)
        put('consumed',actor+':'+str(p['sequence']),dict(intent_id=p['id'],outcome='success' if result=='success' else 'revert'))
        # Commit a replacement set atomically; every object increments its own version.
        replacements={}
        for (table,key),value in writes.items():
            old=self.objects.get(table+':'+key)
            if table=='balances' and not 0<=value<=2**64-1: raise ArithmeticError('object coin range')
            replacements[table+':'+key]=self.resource(table,key,value,old['version']+1 if old else 0)
        self.objects.update(replacements)
        self.ctx.metrics['writes']+=len(replacements)
        self.history.append(dict(intent=p['id'],objects=sorted(replacements)))
        return result

    def project(self):
        s={t:{} for t in ('balances','epochs','grants','agreements','credits','consumed')}
        for r in self.objects.values():
            if r['table']=='fee_sink': s['fee_sink']=r['data']
            else: s[r['table']][r['key']]=copy.deepcopy(r['data'])
        for r in s['consumed'].values(): r['intent']=self.labels[r.pop('intent_id')]
        return s

    def native(self): return dict(objects=self.objects,history=self.history)
