"""Offline evidence completeness/reproduction checks; imports no candidate code."""
import argparse
import collections
import gzip
import hashlib
import json
from pathlib import Path

EXPECTED={f'V{i:02}' for i in range(1,22)}|{f'S{i:02}' for i in range(1,10)}
MODELS={'accounts','objects','eutxo'}


def check_results(data):
    assert data['environment']['python']=='3.12.1'
    assert data['environment']['pycryptodome']=='3.24.1'
    counts=collections.Counter(); stable={}; holds=[]; pass_counts=collections.Counter()
    for run in data['runs']:
        assert run['model'] in MODELS and run['case'] in EXPECTED
        if run.get('warmup'):
            counts[(run['model'],'warmup')]+=1; continue
        key=(run['model'],run['case'],run['repetition']); counts[key]+=1
        if run['status']!='PASS': holds.append(run); continue
        assert run['worker_peak_rss_bytes']<=1024**3
        assert run['client_peak_rss_bytes']<=128*1024**2
        assert run['native_state_bytes']<=256*1024**2
        assert run['journal_bytes']<=1024**2
        assert all(n<=16*1024**2 for n in run['client_network_bytes'].values())
        signature=(run['final_projection_sha256'],run['operations'],run['counters'])
        pair=(run['model'],run['case'])
        assert pair not in stable or stable[pair]==signature,('unstable repeated metrics',pair)
        stable[pair]=signature;pass_counts[pair]+=1
    for model in MODELS:
        assert counts[(model,'warmup')]==1
        for case in EXPECTED:
            for rep in range(3): assert counts[(model,case,rep)]==1,('missing/duplicate run',model,case,rep)
    assert len(data['runs'])==273
    return {k:v for k,v in stable.items() if pass_counts[k]==3},holds



def supply_of(state):
    total=sum(state['balances'].values())+state['fee_sink']
    total+=sum(g['principal_pool']+g['fee_pool'] for g in state['grants'].values())
    total+=sum(a['price'] for a in state['agreements'].values() if a['state']=='Funded')
    total+=sum(c['amount'] for c in state['credits'].values() if c['status']=='outstanding')
    return total


def normalize(state,manifest):
    answer=dict(state)
    answer['grants']={k:dict(g,delegates=sorted(g['delegates']),recipients=sorted(g['recipients'])) for k,g in state['grants'].items()}
    answer['consumed']={k:dict(r,intent=manifest['intents'][r['intent']]['intent_id']) for k,r in state['consumed'].items()}
    return answer


def check_trace(path, golden=True):
    completed=collections.Counter(); partial=[]; state=None; active=None; steps=0; total=0
    root=Path(__file__).resolve().parents[3]
    corpus=json.loads((root/'research/fixtures/native_l1/v1/corpus.json').read_text())
    core={v['id']:v for v in corpus['vectors']}
    stress={v['id']:v for v in json.loads((root/'research/native_l1/evidence/stress-input-v1.json').read_text())['cases']}
    golden_steps=0;final_hashes={}
    with gzip.open(path,'rt') as stream:
        for line in stream:
            row=json.loads(line); key=(row['model'],row['case'])
            if 'initial_ledger' in row:
                assert active is None,('unfinished trace before next initialization',active)
                active=key;state=row['initial_ledger'];steps=0;initial_supply=supply_of(state)
                if golden:
                    fixture=core.get(key[1],stress.get(key[1]));assert fixture is not None
                    manifest=corpus if key[1] in core else fixture['manifest']
                    assert normalize(state,manifest)==normalize(fixture['initial_state'],manifest)
            elif 'ledger_delta' in row:
                assert key==active
                d=row['ledger_delta']
                for table,keys in d['remove'].items():
                    for k in keys: del state[table][k]
                for table,values in d['put'].items():
                    if isinstance(values,dict): state[table].update(values)
                    else: state[table]=values
                assert row['step']==steps; steps+=1;total+=1
                # Independent arithmetic/state checks on the reconstructed trace.
                supply=sum(state['balances'].values())+state['fee_sink']
                for grant in state['grants'].values():
                    for prefix in ('principal','fee'):
                        assert grant[prefix+'_cap']==sum(grant[prefix+'_'+x] for x in ('used','pool','returned'))
                    supply+=grant['principal_pool']+grant['fee_pool']
                supply+=sum(a['price'] for a in state['agreements'].values() if a['state']=='Funded')
                supply+=sum(c['amount'] for c in state['credits'].values() if c['status']=='outstanding')
                assert supply==initial_supply
                if golden and key[1] in core:
                    expected=core[key[1]]['steps'][row['step']]
                    assert row['event']==expected['event'] and row['result']==expected['expect']['result']
                    assert normalize(state,manifest)==normalize(expected['expect']['ledger'],manifest)
                    assert row['client']==expected['expect']['client']
                    golden_steps+=1
                elif golden:
                    label=stress[key[1]]['operations'][row['step']]
                    assert row['event']==dict(type='include',intent=label,tick=1) and row['result']=='success'
            elif 'native_final' in row:
                assert key==active
                if golden:
                    expected_count=len(core[key[1]]['steps']) if key[1] in core else len(stress[key[1]]['operations'])
                    assert steps==expected_count,'incomplete run promoted to native_final'
                    h=hashlib.sha256(json.dumps(normalize(state,manifest),sort_keys=True,separators=(',',':')).encode()).hexdigest()
                    label=':'.join(key)
                    assert label not in final_hashes or final_hashes[label]==h,'trace repeat mismatch'
                    final_hashes[label]=h
                completed[key]+=1;active=None
            elif 'failure' in row:
                assert key==active
                partial.append(dict(model=key[0],case=key[1],completed_steps=steps,failure=row['failure']))
                active=None
            else: raise AssertionError('unknown trace record')
    assert active is None,'truncated trace'
    return dict(complete_runs={m+':'+c:n for (m,c),n in completed.items()},partial_runs=partial,checked_transition_steps=total,checked_core_golden_steps=golden_steps,final_projection_sha256=final_hashes,sha256=hashlib.sha256(Path(path).read_bytes()).hexdigest())


def compare_environments(first,second):
    assert first['source_lock']==second['source_lock'],'different frozen source/input identities'
    assert first['environment']['platform']!=second['environment']['platform'],'same platform is insufficient independent-host evidence'
    a,ah=check_results(first);b,bh=check_results(second)
    equal=[]
    for key in sorted(a.keys()&b.keys()):
        assert a[key]==b[key],('cross-environment deterministic disagreement',key)
        equal.append(':'.join(key))
    return dict(source_and_input_identity_match=True,deterministic_successful_configurations_equal=equal,first_holds=ah,second_holds=bh,interpretation='finite shared-source reproduction; timings and unsupported resource controls are not equivalent')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('first');p.add_argument('--second');p.add_argument('--trace');p.add_argument('--output',required=True);a=p.parse_args()
    first=json.loads(Path(a.first).read_text());stable,holds=check_results(first)
    result=dict(complete_run_plan=True,successful_configurations=len(stable),holds=holds)
    if a.second: result['reproduction']=compare_environments(first,json.loads(Path(a.second).read_text()))
    if a.trace:
        result['trace']=check_trace(a.trace)
        expected=collections.Counter(r['model']+':'+r['case'] for r in first['runs'] if r['status']=='PASS')
        assert dict(expected)==result['trace']['complete_runs'],'trace/result run count mismatch'
        assert len(result['trace']['partial_runs'])==len(holds),'missing resource-failure trace'
        for r in first['runs']:
            if r['status']=='PASS': assert result['trace']['final_projection_sha256'][r['model']+':'+r['case']]==r['final_projection_sha256'],'trace/result hash mismatch'
    Path(a.output).write_text(json.dumps(result,indent=2)+'\n')
