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
