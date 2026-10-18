"""Mutable account tables with a serial, atomic write transaction."""
import copy
from ..common import Context, Reject, DOMAIN, digest, packed


class Accounts:
    kind = 'accounts'

    def __init__(self, manifest, initial):
        self.ctx=Context(manifest)
        self.labels={v['intent_id']:k for k,v in reversed(list(manifest['intents'].items()))}
        self.tables=copy.deepcopy(initial)
        for record in self.tables['consumed'].values():
            record['intent_id']=manifest['intents'][record.pop('intent')]['intent_id']
        self.history=[]

    def read(self, table, key):
        self.ctx.metrics['reads']+=1
        return copy.deepcopy(self.tables[table].get(key))

    def build(self, intent):
        p=self.ctx.parse(intent)
        return dict(kind=self.kind,intent_id=p['id'],actor=p['actor'],epoch=p['epoch'])

    def include(self, intent, wrapper, tick):
        try:
            p=self.ctx.parse(intent)
            if wrapper != dict(kind=self.kind,intent_id=p['id'],actor=p['actor'],epoch=p['epoch']):
                return 'structural_reject'
            self.ctx.authenticate(p,intent,self.read,tick)
        except Reject as e:
            return str(e)
        # Serial isolation; abort never exposes partially updated balances/authority.
        next_state=copy.deepcopy(self.tables)
        a,op,actor=p['args'],p['op'],p['actor']
        g=next_state['grants'].get(p.get('grant'))
        result='success'
        if op in (1,5):
            price=a[-2] if op==1 else a[2][7]
            if g and g['principal_pool'] < price:
                result='revert:principal_budget'
            elif not g and next_state['balances'][actor] < price+p['ceiling']:
                result='revert:balance'
            if op==5 and result=='success':
                name,agreement=self.ctx.terms_record(a[2])
                if tick>=agreement['fund_before'] or name in next_state['agreements']:
                    result='revert:fund_deadline' if tick>=agreement['fund_before'] else 'revert:agreement_state'
            if result=='success':
                if g:
                    g['principal_pool']-=price; g['principal_used']+=price
                else:
                    next_state['balances'][actor]-=price
                if op==1:
                    recipient=self.ctx.actor(a[-3]); next_state['balances'][recipient]+=price
                else:
                    next_state['agreements'][name]=agreement
        elif op==2:
            name=self.ctx.alias('grants',a[0])
            correct=digest([DOMAIN,2,p['u'][1],p['u'][2],p['sequence']])
            if a[0].hex()!=correct or name in next_state['grants']:
                result='revert:grant_identity'
            elif next_state['balances'][actor] < a[4]+a[5]+p['ceiling']:
                result='revert:balance'
            else:
                next_state['balances'][actor]-=a[4]+a[5]
                next_state['grants'][name]=dict(owner=actor,owner_epoch=p['epoch'],version=0,delegates=[self.ctx.actor(d[0]) for d in a[1]],actions=a[2],recipients=[self.ctx.actor(r) for r in a[3]],expires=a[6],principal_cap=a[4],fee_cap=a[5],principal_pool=a[4],fee_pool=a[5],principal_used=0,fee_used=0,principal_returned=0,fee_returned=0,status='active')
        elif op in (3,4,9):
            target=next_state['grants'][self.ctx.alias('grants',a[0])]
            if op==3:
                target['status']='revoked'
            elif op==4:
                if target['status']!='active': result='revert:grant_state'
                else:
                    target['version']+=1; target['delegates']=[self.ctx.actor(d[0]) for d in a[2]]
            elif target['status']=='returned' or (target['status']=='active' and tick<target['expires']):
                result='revert:grant_state'
            else:
                next_state['balances'][actor]+=target['principal_pool']+target['fee_pool']
                for pool in ('principal','fee'):
                    target[pool+'_returned']+=target[pool+'_pool']; target[pool+'_pool']=0
                target['status']='returned'
        elif op in (6,7):
            name=self.ctx.alias('agreements',a[0]); target=next_state['agreements'][name]
            if target['state']!='Funded': result='revert:agreement_state'
            elif op==6 and tick>=target['claim_before']: result='revert:claim_deadline'
            elif op==7 and tick<target['claim_before']: result='revert:refund_deadline'
            else:
                terms=self.ctx.manifest['terms'][target['terms']]['array']
                expected=terms[5]+terms[6]
                self.ctx.metrics['predicates']+=int(op==6)
                if op==6 and int.from_bytes(a[1],'big')!=expected: result='revert:result'
                else:
                    target['state']='Settled' if op==6 else 'Refunded'
                    target['result']=expected if op==6 else 0
                    raw_credit=bytes.fromhex(digest([a[0],2 if op==6 else 3]))
                    credit=self.ctx.alias('credits',raw_credit)
                    next_state['credits'][credit]=dict(agreement=name,owner=actor,amount=target['price'],status='outstanding')
        elif op==8:
            target=next_state['credits'][self.ctx.alias('credits',a[0])]
            if target['status']!='outstanding': result='revert:credit_state'
            else:
                next_state['balances'][actor]+=target['amount']; target['status']='collected'
        if g:
            g['fee_pool']-=1; g['fee_used']+=1
        else:
            next_state['balances'][actor]-=1
        next_state['fee_sink']+=1
        next_state['consumed'][actor+':'+str(p['sequence'])]=dict(intent_id=p['id'],outcome='success' if result=='success' else 'revert')
        if any(v<0 or v>2**64-1 for v in next_state['balances'].values()):
            raise ArithmeticError('account balance range')
        self.ctx.metrics['writes']+=sum(next_state[k]!=self.tables[k] for k in next_state)
        self.tables=next_state
        self.history.append(dict(intent=p['id'],result=result))
        return result

    def project(self):
        s=copy.deepcopy(self.tables)
        for r in s['consumed'].values(): r['intent']=self.labels[r.pop('intent_id')]
        return s

    def native(self):
        return dict(tables=self.tables,history=self.history)
