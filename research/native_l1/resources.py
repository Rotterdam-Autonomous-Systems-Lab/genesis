"""External sampled aggregate child CPU + wall watchdog; no caps increased."""
import os,sys,time,threading,resource
from pathlib import Path

class RunMonitor:
    def __init__(self,processes):
        self.processes=processes;self.start=min(p.start for p in processes)
        self.reason=None;self.aggregate_cpu=0;self.done=threading.Event()
        self.thread=threading.Thread(target=self.watch,daemon=True);self.thread.start()
    def sample(self):
        if sys.platform=='linux':
            ticks=os.sysconf('SC_CLK_TCK');total=0
            for process in self.processes:
                try:
                    fields=Path('/proc/'+str(process.p.pid)+'/stat').read_text().rsplit(')',1)[1].split()
                    total+=(int(fields[11])+int(fields[12]))/ticks
                except FileNotFoundError:total+=process.last.get('process_cpu_seconds',0)
            self.aggregate_cpu=max(self.aggregate_cpu,total)
        else:self.aggregate_cpu=max(self.aggregate_cpu,sum(p.last.get('process_cpu_seconds',0) for p in self.processes))
    def watch(self):
        while not self.done.wait(.02):
            self.sample()
            if self.aggregate_cpu>=120:self.reason='aggregate CPU cap (120s; 20ms sampled watchdog)'
            if time.monotonic()-self.start>=180:self.reason='180-second run watchdog'
            if self.reason:
                for process in self.processes:
                    if process.p.poll() is None:process.p.kill()
                return
    def close(self):
        self.done.set();self.thread.join(timeout=1);self.sample()
        if self.reason:raise RuntimeError(self.reason)
        if time.monotonic()-self.start>=180:raise RuntimeError('180-second run watchdog')
        if self.aggregate_cpu>120:raise RuntimeError('aggregate CPU cap')

def rss_bytes():
    value=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return value if sys.platform=='darwin' else value*1024
