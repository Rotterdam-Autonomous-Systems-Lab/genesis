"""Summarize retained evidence without interpreting a model family as a winner."""
import argparse
import collections
import json
from pathlib import Path


def render(data):
    lines=['# Task 019 environment result','',f"Decision: **{data['decision']}**",'',f"Environment: `{data['environment']['platform']}` / `{data['environment']['machine']}`; Python {data['environment']['python']}.",'','| Model | Measured runs PASS / HOLD | Worker CPU seconds range | Peak worker RSS MiB | Peak native state KiB |','| --- | --- | --- | --- | --- |']
    for model in ('accounts','objects','eutxo'):
        runs=[r for r in data['runs'] if r['model']==model and not r.get('warmup')]
        passed=[r for r in runs if r['status']=='PASS'];hold=len(runs)-len(passed)
        cpu=[r['worker_cpu_seconds'] for r in passed]
        lines.append(f"| {model} | {len(passed)} / {hold} | {min(cpu,default=0):.4f}–{max(cpu,default=0):.4f} | {max((r['worker_peak_rss_bytes'] for r in passed),default=0)/1048576:.2f} | {max((r['native_state_bytes'] for r in passed),default=0)/1024:.2f} |")
    lines+=['','Timings and RSS are environment-specific. Fresh-reference stress does not measure parallel throughput. No architecture selection or family elimination follows.','']
    for r in data['runs']:
        if r['status']!='PASS': lines.append(f"- Retained HOLD {r['model']} {r['case']}: {r.get('error','unknown')}")
    return '\n'.join(lines)+'\n'


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('results');p.add_argument('--output',required=True);a=p.parse_args()
    Path(a.output).write_text(render(json.loads(Path(a.results).read_text())))
