"""Four finite post-implementation controls, outside the measured run plan.

Reuse existing signed inputs; never alter frozen fixtures or prototype sources.
"""
import copy
import json
from pathlib import Path
from research.native_l1.devcheck import MODELS
from research.native_l1.checks import invariants

ROOT=Path(__file__).resolve().parents[3]


def run():
    data=json.loads((ROOT/'research/fixtures/native_l1/v1/corpus.json').read_text())
    initial=data['vectors'][0]['initial_state'];supply=data['vectors'][0]['initial_supply'];records=[]
    for cls in MODELS.values():
        def execute(m,label,tick):
            i=data['intents'][label];result=m.include(i,m.build(i),tick)
            invariants(m.project(),supply,data)
            return result
        m=cls(data,initial)
        assert execute(m,'pay12',1)=='success'
        assert execute(m,'rotate_grant',2)=='success'
        assert execute(m,'version1_pay',3)=='revert:principal_budget'
        g=m.project()['grants']['G'];assert (g['principal_used'],g['principal_pool'],g['fee_used'])==(12,8,2)
        records.append(dict(model=cls.kind,control='rotation_after_nonzero_spend',status='PASS'))
        m=cls(data,initial)
        assert execute(m,'pay10',1)=='success';assert execute(m,'revoke',2)=='success'
        before=m.project();assert execute(m,'pay10',30)=='duplicate';assert m.project()==before
        records.append(dict(model=cls.kind,control='duplicate_after_revoke_and_expiry',status='PASS'))
        m=cls(data,initial)
        assert execute(m,'fee_ceiling2',1)=='success'
        assert (m.project()['grants']['G']['fee_pool'],m.project()['fee_sink'])==(4,1)
        records.append(dict(model=cls.kind,control='unused_fee_ceiling_released',status='PASS'))
        m=cls(data,initial)
        for name,tick in [('fund',9),('claim18',19),('collect',19)]: assert execute(m,name,tick)=='success'
        paid=m.project()['balances']['B']
        assert execute(m,'collect_again',19)=='revert:credit_state'
        assert m.project()['balances']['B']==paid-1
        before=m.project();assert execute(m,'collect',19)=='duplicate';assert m.project()==before
        records.append(dict(model=cls.kind,control='collected_credit_new_sequence_and_duplicate',status='PASS'))
    return dict(scope='local supplemental controls, not timed comparative runs or extra frozen configurations',results=records)


if __name__=='__main__': print(json.dumps(run(),indent=2))
