"""Unscored non-coalesced recipient-claim control, NOT a fourth full model.

Recipient payment outputs cannot be consumed without the owner in this control.
It isolates the top-up representation trade-off; no general script/fee model.
"""
def append(claims, output_id, owner, amount):
    assert output_id not in claims and type(amount) is int and amount>0
    return dict(claims,**{output_id:dict(owner=owner,amount=amount)})

def spend(claims, identifiers, signer):
    assert len(set(identifiers))==len(identifiers)
    assert all(claims[i]['owner']==signer for i in identifiers)
    return {i:c for i,c in claims.items() if i not in identifiers}

if __name__=='__main__':
    import json
    claims=append({},'pay12','S',12);claims=append(claims,'pay8','S',8)
    assert sum(c['amount'] for c in claims.values())==20
    try:spend(claims,['pay12'],'D2')
    except AssertionError:pass
    else:raise AssertionError('unauthorized consumption')
    print(json.dumps(dict(scope='two-payment append-only control; not full comparison',claims=claims,independent_recipient_claims=2,recipient_inputs_on_topup=0,unauthorized_spend_rejected=True),indent=2))
