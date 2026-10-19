"""Offline Task020 resource/reproduction checks, imports no candidate model."""
import argparse,collections,gzip,hashlib,json,tempfile
from pathlib import Path
from research.reports.task019.verify_evidence import check_results,check_trace

def resources(data):
    stable,holds=check_results(data)
    for r in data['runs']:
        if r['status']!='PASS':continue
        assert r['total_state_bytes']==r['native_state_bytes']+r['registry_bytes']<=256*1024**2
        assert r['aggregate_process_cpu_seconds']<=120
        assert r['wire_wall_seconds']<=180 and r['end_to_end_wall_seconds']<=180
        assert r['max_wire_envelope_bytes']<=65536 and r['max_transport_bytes']<=65536
        assert r['harness_peak_rss_bytes']>0 and r['harness_cpu_seconds']>=0
        assert r['worker_components'] and r['client_components']
        assert r['operations'].get('hash_calls',0)>0
        assert r['checked_barriers']>0
        assert r['hard_memory_affinity_enforced'],'reference resource profile unavailable'
    return stable,holds

def trace_with_boundaries(path):
    diagnostics=[];active=None;steps=0
    with tempfile.TemporaryDirectory() as directory:
        filtered=Path(directory)/'compatible-trace.gz'
        with gzip.open(path,'rt') as source,gzip.open(filtered,'wt') as target:
            for line in source:
                row=json.loads(line);key=(row['model'],row['case'])
                if 'initial_ledger' in row:assert active is None;active=key;steps=0
                elif 'ledger_delta' in row:assert active==key and row['step']==steps;steps+=1
                elif 'boundary_failure' in row:
                    assert active==key and row['boundary_failure']['checked_barriers']==steps
                    diagnostics.append(row);continue
                elif 'failure' in row or 'native_final' in row:assert active==key;active=None
                target.write(line)
        assert active is None,'unclosed trace: incomplete run is not acceptance'
        result=check_trace(filtered)
    assert len(diagnostics)==len(result['partial_runs']),'missing failure-boundary evidence'
    result['boundary_diagnostics']=diagnostics
    result['sha256']=hashlib.sha256(Path(path).read_bytes()).hexdigest()
    return result


def main():
    p=argparse.ArgumentParser();p.add_argument('first');p.add_argument('--second');p.add_argument('--trace');p.add_argument('--output',required=True);a=p.parse_args()
    first=json.loads(Path(a.first).read_text());stable,holds=resources(first)
    out=dict(full_plan=True,complete_configurations=len(stable),holds=holds)
    if a.second:
        second=json.loads(Path(a.second).read_text());other,oh=resources(second)
        assert first['source_lock']==second['source_lock']
        # Two separately provisioned CI jobs may have identical OS/version strings.
        e,f=first['environment'],second['environment']
        assert e['isolation']['replica']!=f['isolation']['replica'] and e['isolation']['ci_run_id']==f['isolation']['ci_run_id']
        assert e['isolation']['host_sha256']!=f['isolation']['host_sha256'],'host identity matches; independent isolation not established'
        assert stable==other,'deterministic completed configurations differ'
        out['reproduction']=dict(equal_complete_configurations=len(stable),first_isolation=e['isolation'],second_isolation=f['isolation'],second_holds=oh,scope='shared-source runs in two fresh CI VMs; no independent implementation audit')
    if a.trace:
        # Boundary diagnostic rows are additional to the frozen lossless format.
        # For completed batches none should be present. Preserve failures rather
        # than filtering any partial trace into a complete one.
        out['trace']=trace_with_boundaries(a.trace)
        expected=collections.Counter(r['model']+':'+r['case'] for r in first['runs'] if r['status']=='PASS')
        assert dict(expected)==out['trace']['complete_runs']
        for r in first['runs']:
            if r['status']=='PASS':assert out['trace']['final_projection_sha256'][r['model']+':'+r['case']]==r['final_projection_sha256']
    Path(a.output).write_text(json.dumps(out,indent=2)+'\n')
if __name__=='__main__':main()
