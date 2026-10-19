"""Offline checker mutations, never published as measured model results."""
import argparse,copy,gzip,json,tempfile
from pathlib import Path
from research.reports.task020.verify_evidence import resources,trace_with_boundaries

def rejects(work):
    try:work()
    except (AssertionError,KeyError):return True
    raise AssertionError('corrupt evidence was accepted')

def main():
    p=argparse.ArgumentParser();p.add_argument('results');p.add_argument('trace');p.add_argument('--output',required=True);a=p.parse_args()
    data=json.loads(Path(a.results).read_text());resources(data);out={}
    for name in ('missing_run','duplicate_run','excess_cpu','excess_total_storage','oversized_envelope','unsupported_memory_profile'):
        bad=copy.deepcopy(data)
        if name=='missing_run':bad['runs'].pop()
        elif name=='duplicate_run':bad['runs'].append(copy.deepcopy(bad['runs'][1]))
        else:
            r=next(r for r in bad['runs'] if r['status']=='PASS' and not r.get('warmup'))
            field,value={'excess_cpu':('aggregate_process_cpu_seconds',121),'excess_total_storage':('total_state_bytes',257*1024**2),'oversized_envelope':('max_wire_envelope_bytes',65537),'unsupported_memory_profile':('hard_memory_affinity_enforced',False)}[name]
            r[field]=value
        out[name]=rejects(lambda:resources(bad))
    rows=[]
    with gzip.open(a.trace,'rt') as stream:
        for line in stream:
            row=json.loads(line);rows.append(row)
            if 'ledger_delta' in row:break
    # A synthetic failed prefix is a checker control, not experiment evidence.
    key={k:rows[0][k] for k in ('model','case')}
    boundary=dict(key,boundary_failure=dict(checked_barriers=1,error='synthetic checker control'))
    failure=dict(key,failure=dict(status='HOLD',error='synthetic checker control'))
    with tempfile.TemporaryDirectory() as directory:
        path=Path(directory)/'mutant.gz'
        def write(values):
            with gzip.open(path,'wt') as stream:
                for value in values:stream.write(json.dumps(value)+'\n')
        write(rows+[boundary,failure]);trace_with_boundaries(path);out['valid_partial_prefix']=True
        altered=copy.deepcopy(boundary);altered['boundary_failure']['checked_barriers']=2
        write(rows+[altered,failure]);out['wrong_boundary']=rejects(lambda:trace_with_boundaries(path))
        write(rows);out['truncated_trace']=rejects(lambda:trace_with_boundaries(path))
        bad=copy.deepcopy(rows);owner=next(iter(bad[0]['initial_ledger']['balances']));bad[0]['initial_ledger']['balances'][owner]+=1
        write(bad+[boundary,failure]);out['forged_ledger']=rejects(lambda:trace_with_boundaries(path))
    Path(a.output).write_text(json.dumps(dict(scope='checker fault injections, no performance evidence',controls=out),indent=2)+'\n')
if __name__=='__main__':main()
