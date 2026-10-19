"""Restricted balance-pool covenant, not a general script VM.

Admission authenticates the signed operation before this module runs. All balance
successors are untrusted here. Non-balance scripts retain their typed transition
checks; this covenant grants no right to spend a grant, credit or registry.
"""
from collections import Counter


class PolicyViolation(AssertionError):
    pass


def require(condition,message):
    if not condition:raise PolicyViolation(message)


def lock(owner):
    return 'script:balance-pool-v1:'+owner


def validate(before, after, deltas):
    """One continuing pool per touched owner; exact authorized delta, no merging.

    before/after map owners to full output records. deltas is the amount approved
    by the authenticated typed operation, including the actor's exact fee.
    Inputs with zero delta may be absent, but no unrelated pool may be consumed.
    """
    require(set(before)==set(after)==set(deltas), 'balance pool input/successor set')
    for owner,old in before.items():
        new=after[owner]
        for out in (old,new):
            require(set(out)=={'table','key','lock','value','datum'}, 'pool schema')
            require(out['table']=='balances' and out['key']==owner, 'pool owner')
            require(out['lock']==lock(owner), 'pool covenant continuity')
            require(type(out['value']) is int and 0<=out['value']<2**64, 'pool range')
            require(type(out['datum']) is int and out['datum']==out['value'], 'pool datum/value')
        require(new['value']-old['value']==deltas[owner], 'unauthorized pool delta')


def authorized_deltas(p, outcome, read):
    """Authorize exact pool changes from an already admitted operation.

    Third-party additions are possible only for its named transfer recipient.
    The signer funds direct spending and fees; grant spending never debits a
    recipient or the root's unreserved balance. No merge/transfer owner rewrite.
    """
    actor,op,a=p['actor'],p['op'],p['args']; changes=Counter()
    if 'grant' not in p: changes[actor]-=1
    if outcome=='success':
        if op==1:
            if 'grant' not in p: changes[actor]-=a[-2]
            changes[p['recipient']]+=a[-2]
        elif op==2: changes[actor]-=a[4]+a[5]
        elif op==5 and 'grant' not in p: changes[actor]-=a[2][7]
        elif op==8: changes[actor]+=read('credits',p['credit'])['amount']
        elif op==9:
            grant=read('grants',p['return_grant'])
            changes[actor]+=grant['principal_pool']+grant['fee_pool']
    return dict(changes)
