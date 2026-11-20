# ravdice.py SECONDS [OUT]: the Loader's dice log for Wake of the Ravager (dsloader.ravlog.RavDiceLog: the
# sequel's layout, its memory read only) attached to the running sequel ($WORK/rav.pid), its lines printed
# (and appended to OUT) as they come, for SECONDS; then how many writes the read-only view dropped.
import sys, os, time, argparse
PT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(PT, '..', 'obsidian-edition'))
from dsloader.__main__ import connect
from dsloader import ravlog
WORK = os.environ.get('PLAYTEST_WORK', '/tmp/playtest')
secs = float(sys.argv[1]); out = open(sys.argv[2], 'a') if len(sys.argv) > 2 else None
g = connect(argparse.Namespace(pid=int(open(os.path.join(WORK, 'rav.pid')).read()), host_base=None))
log = ravlog.RavDiceLog(g)
print(log.attach(), flush=True)
end = time.time() + secs
while time.time() < end:
    for line in log.lines():
        print(line, flush=True)
        if out: out.write(line + '\n'); out.flush()
    time.sleep(0.05)
print('writes dropped:', log.guest.dropped)
