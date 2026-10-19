"""Descriptive metrics only; no architecture rank and no candidate imports."""
import argparse,json,statistics
from pathlib import Path

def summarize(data):
    models=[]
    for kind in ('accounts','objects','eutxo'):
        measured=[r for r in data['runs'] if r['model']==kind and not r.get('warmup')]
        good=[r for r in measured if r['status']=='PASS'];bad=[r for r in measured if r['status']!='PASS']
        def bounds(key):
            values=[r[key] for r in good];return [min(values),max(values)] if values else None
        m=dict(model=kind,passed_runs=len(good),holds=bad,completed_configurations=len({r['case'] for r in good if sum(x['case']==r['case'] for x in good)==3}),delivered_ledger_actions=sum(r['counters'].get('delivered_actions',0) for r in good),admitted_successes=sum(r['counters'].get('success',0) for r in good),admitted_reverts=sum(sum(v for k,v in r['counters'].items() if k.startswith('revert:')) for r in good),native_conflicts=sum(r['counters'].get('native_structural_rejects',0) for r in good),injected_conflicts=sum(r['counters'].get('injected_structural_rejects',0) for r in good),max_state_bytes=max((r['total_state_bytes'] for r in good),default=None),max_worker_rss_bytes=max((r['worker_peak_rss_bytes'] for r in good),default=None),max_client_rss_bytes=max((r['client_peak_rss_bytes'] for r in good),default=None),harness_lifetime_peak_rss_upper_bound_bytes=max((r['harness_peak_rss_bytes'] for r in good),default=None),aggregate_cpu_seconds_range=bounds('aggregate_process_cpu_seconds'),end_to_end_wall_seconds_range=bounds('end_to_end_wall_seconds'),max_transport_bytes=max((r['max_transport_bytes'] for r in good),default=None),max_wire_envelope_bytes=max((r['max_wire_envelope_bytes'] for r in good),default=None))
        m['S09']=[dict(repetition=r['repetition'],wall_seconds=r['end_to_end_wall_seconds'],aggregate_cpu_seconds=r['aggregate_process_cpu_seconds'],worker_cpu_seconds=r['worker_process_cpu_seconds'],client_cpu_seconds=r['client_process_cpu_seconds'],harness_cpu_seconds=r['harness_cpu_seconds'],proxy_bytes=sum(r['client_network_bytes'].values()),proxy_floor_seconds=sum(r['client_network_bytes'].values())/10240,total_state_bytes=r['total_state_bytes'],native_state_bytes=r['native_state_bytes'],registry_bytes=r['registry_bytes'],verification_operations=r['operations'],worker_component_cpu={k:v['cpu_seconds'] for k,v in r['worker_components'].items()},verification_timing_cpu={k:v['cpu_seconds'] for k,v in r['verification_timings'].items()}) for r in good if r['case']=='S09']
        models.append(m)
    return dict(environment=data['environment'],source_lock=data['source_lock'],models=models,interpretation='Descriptive finite prototype costs. Different archival detail and Python/runtime overhead prohibit state-model family rankings. Opaque signature internals are counted as signature operations; context parsing timers overlap operation totals.')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('first');p.add_argument('second');p.add_argument('--output',required=True);a=p.parse_args()
    Path(a.output).write_text(json.dumps(dict(environment_1=summarize(json.loads(Path(a.first).read_text())),environment_2=summarize(json.loads(Path(a.second).read_text()))),indent=2)+'\n')
