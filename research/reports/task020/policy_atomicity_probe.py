"""Local supplemental covenant fault injection; outside scored corpus/run plan."""
import copy,json
from pathlib import Path
from unittest.mock import patch
from research.native_l1.models.eutxo import EUTXO
from research.native_l1.balance_policy import validate,PolicyViolation

def main():
    d=json.loads(Path('research/fixtures/native_l1/v1/corpus.json').read_text());out=[]
    mutations=[('value',-1),('value',2**64),('value',True),('datum',True),('value',11),('value',13),('key','D2'),('lock','D2')]
    for field,value in mutations:
        m=EUTXO(d,d['vectors'][0]['initial_state']);i=d['intents']['pay12'];before=copy.deepcopy(m.native())
        def hostile(old,new,delta):
            proposed=copy.deepcopy(new);proposed['S'][field]=value
            validate(old,proposed,delta)
        with patch('research.native_l1.models.eutxo.validate_pools',hostile):
            try:m.include(i,m.build(i),1)
            except PolicyViolation:pass
            else:raise AssertionError('hostile pool successor accepted')
        assert before==m.native(),'partial value/fee/replay commit on policy failure'
        out.append(dict(field=field,value=value,rejected=True,native_state_unchanged=True))
    print(json.dumps(dict(scope='local fault injection, not scored comparison',source='dc589ba660e374e3f775790dd4be82fc24c4e2bf',cases=out),indent=2))
if __name__=='__main__':main()
