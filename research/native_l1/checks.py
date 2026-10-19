"""Harness assertions, independent of candidate admission and mutation code."""
import copy
import hashlib
import json


class ComparisonFailure(AssertionError):
    pass


def require(ok,message):
    if not ok: raise ComparisonFailure(message)


def canonical(state,manifest):
    # Read-only canonical view: copy only rows whose presentation changes.
    answer=dict(state)
    answer['grants']={k:dict(g,delegates=sorted(g['delegates']),recipients=sorted(g['recipients'])) for k,g in state['grants'].items()}
    answer['consumed']={k:dict(entry,intent=manifest['intents'][entry['intent']]['intent_id']) for k,entry in state['consumed'].items()}
    return answer



def invariants(state,initial_supply,manifest,previous=None,rollback=False):
    require(set(state['balances'])==set(manifest['actors'])==set(state['epochs']),'principal identities')
    total=state['fee_sink']+sum(state['balances'].values())
    require(all(type(v)is int and 0<=v<2**64 for v in state['balances'].values()),'balance range')
    for key,g in state['grants'].items():
        require(g['owner'] in state['balances'],'grant root')
        for prefix in ('principal','fee'):
            require(all(type(g[prefix+'_'+f])is int and 0<=g[prefix+'_'+f]<2**64 for f in ('cap','used','pool','returned')),'grant numeric range')
            require(g[prefix+'_cap']==g[prefix+'_used']+g[prefix+'_pool']+g[prefix+'_returned'],'grant cap identity')
            if previous and key in previous['grants'] and not rollback:
                require(g[prefix+'_used']>=previous['grants'][key][prefix+'_used'],'renewed lifetime authority')
        total+=g['principal_pool']+g['fee_pool']
    for key,a in state['agreements'].items():
        require(a['requester'] in state['balances'] and a['provider'] in state['balances'],'agreement parties')
        terms=manifest['terms'][a['terms']]['array']
        require(a['price']==terms[7] and a['fund_before']==terms[8] and a['claim_before']==terms[9],'immutable financial terms')
        if a['state']=='Funded':
            total+=a['price']; require(a['result']==0,'nonterminal result')
        else:
            require(a['state'] in ('Settled','Refunded'),'terminal code')
            expected_owner=a['provider'] if a['state']=='Settled' else a['requester']
            credits=[c for c in state['credits'].values() if c['agreement']==key]
            require(len(credits)==1 and credits[0]['owner']==expected_owner and credits[0]['amount']==a['price'],'terminal beneficiary')
            require(a['result']==(terms[5]+terms[6] if a['state']=='Settled' else 0),'work predicate')
        if previous and key in previous['agreements'] and not rollback:
            old=previous['agreements'][key]
            if old['state']!='Funded': require(a==old,'terminal rewrite')
    for c in state['credits'].values():
        require(c['owner'] in state['balances'] and c['agreement'] in state['agreements'],'credit identity')
        if c['status']=='outstanding': total+=c['amount']
        else: require(c['status']=='collected','credit status')
    require(total==initial_supply,'supply conservation')
    if previous and not rollback:
        for key,entry in previous['consumed'].items(): require(state['consumed'].get(key)==entry,'replay record erased')


def compare(result,state,client,expected,manifest):
    require(result==expected['result'],f"outcome {result} != {expected['result']}")
    require(canonical(state,manifest)==canonical(expected['ledger'],manifest),'ledger projection mismatch')
    require(client==expected['client'],'client projection mismatch')


def audit_pool_transactions(native, manifest):
    """Independent arithmetic check; never imports the model covenant."""
    by_id={i['intent_id']:i for i in manifest['intents'].values()}
    names={a['id']:n for n,a in manifest['actors'].items()}
    outputs=native['outputs']
    for tx in native['transactions']:
        require(tx['id'] in by_id,'unknown native authorization')
        u=by_id[tx['id']]['unsigned']; actor=names[u[2]['bytes']]; op,args=u[7:]
        ins=[outputs[i] for i in tx['inputs']]; outs=[outputs[i] for i in tx['outputs']]
        old={o['key']:o for o in ins if o['table']=='balances'}
        new={o['key']:o for o in outs if o['table']=='balances'}
        require(len(old)==sum(o['table']=='balances' for o in ins),'duplicate pool input owner')
        require(len(new)==sum(o['table']=='balances' for o in outs),'duplicate pool successor owner')
        delegated=op in (1,5) and args[0]['bytes']!='00'*32
        expected={}
        def add(owner,amount): expected[owner]=expected.get(owner,0)+amount
        if not delegated: add(actor,-1)
        if tx['outcome']=='success':
            if op==1:
                if not delegated:add(actor,-args[-2])
                add(names[args[-3]['bytes']],args[-2])
            elif op==2:add(actor,-args[4]-args[5])
            elif op==5 and not delegated:add(actor,-args[2][7])
            elif op==8:
                credit=next(o['datum'] for o in ins if o['table']=='credits')
                require(credit['owner']==actor,'collection signer/owner');add(actor,credit['amount'])
            elif op==9:
                grant=next(o['datum'] for o in ins if o['table']=='grants')
                require(grant['owner']==actor,'return signer/root');add(actor,grant['principal_pool']+grant['fee_pool'])
        require(set(old)==set(new)==set(expected),'pool authorization input/successor set')
        for owner in old:
            require(new[owner]['value']-old[owner]['value']==expected[owner],'unauthorized native pool debit/topup')
            for o in (old[owner],new[owner]):
                require(o['lock']=='script:balance-pool-v1:'+owner and o['datum']==o['value'],'native pool covenant continuity')
