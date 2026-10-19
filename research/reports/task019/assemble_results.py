"""Derive explicitly labeled report metrics from retained complete batches."""
import argparse
import collections
import hashlib
import json
from pathlib import Path


def packed(v):return json.dumps(v,sort_keys=True,separators=(',',':')).encode()


def registry_bytes(manifest):
    public={k:manifest[k] for k in ('actors','aliases','terms','network_id','service_id')}
    term_names={v['agreement_id']:k for k,v in manifest['terms'].items()}
    labels={v['intent_id']:k for k,v in reversed(list(manifest['intents'].items()))}
    return len(packed(dict(public_registry=public,term_names=term_names,intent_labels=labels)))


def summarize(data,corpus,stress):
    contexts={v['id']:corpus for v in corpus['vectors']}
    contexts.update({v['id']:v['manifest'] for v in stress['cases']})
    rows=[]
    for model in ('accounts','objects','eutxo'):
        runs=[r for r in data['runs'] if r['model']==model and not r.get('warmup')]
        passing=[r for r in runs if r['status']=='PASS']
        pass_counts=collections.Counter(r['case'] for r in passing)
        rows.append(dict(model=model,passed_runs=len(passing),holds=[r for r in runs if r['status']!='PASS'],successful_configurations=sum(n==3 for n in pass_counts.values()),executed_ledger_actions=sum(r['counters'].get('delivered_actions',0) for r in passing),native_structural_rejects=sum(r['counters'].get('native_structural_rejects',0) for r in passing),injected_structural_rejects=sum(r['counters'].get('injected_structural_rejects',0) for r in passing),worker_cpu_seconds_range=[min((r['worker_cpu_seconds'] for r in passing),default=0),max((r['worker_cpu_seconds'] for r in passing),default=0)],peak_worker_rss_bytes=max((r['worker_peak_rss_bytes'] for r in passing),default=0),peak_client_rss_bytes=max((r['client_peak_rss_bytes'] for r in passing),default=0),max_native_serialized_bytes=max((r['native_state_bytes'] for r in passing),default=0),max_native_plus_common_registry_serialized_bytes=max((r['native_state_bytes']+registry_bytes(contexts[r['case']]) for r in passing),default=0),all_hard_controls_supported=all(r['hard_memory_affinity_enforced'] for r in passing)))
    return dict(platform=data['environment']['platform'],models=rows,metric_notes=['Added common registry size is a derived compact serialization, not an observed filesystem high-water mark.','Native storage includes different archival detail; no state-model family ranking follows.','Executed actions exclude partial resource-HOLD traces; trace index records those separately.','Worker/client timed CPU excludes debug projection encoding; hard per-process limits are not a measured aggregate CPU-group limit.','Harness peak RSS is unavailable in the frozen instrumentation.'])


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--local',required=True);p.add_argument('--ci',required=True);p.add_argument('--output',required=True);a=p.parse_args()
    root=Path(__file__).resolve().parents[3]
    corpus=json.loads((root/'research/fixtures/native_l1/v1/corpus.json').read_text())
    stress=json.loads((root/'research/native_l1/evidence/stress-input-v1.json').read_text())
    result={name:summarize(json.loads(Path(path).read_text()),corpus,stress) for name,path in (('local',a.local),('ci',a.ci))}
    Path(a.output).write_text(json.dumps(result,indent=2)+'\n')
