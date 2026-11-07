# orderwatch.py SECONDS: fight_on and whose turn, with each new dice-log line, timed every 10 ms (which
# came first: a blow or the fight's start).
import os, sys, struct; HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, 'live.py')).read())
import time
f = open(os.path.join(os.environ.get('PLAYTEST_WORK', '/tmp/playtest'), 'dice.txt')); f.seek(0, 2)
t0, last = time.time(), None
while time.time() - t0 < float(sys.argv[1]):
    st = (gd.fight_on(), gd.whose_turn())
    if st != last:
        print('%.3f state fight_on=%s turn=%s' % (time.time() - t0, *st), flush=True); last = st
    for line in f.readlines():
        print('%.3f LOG %s' % (time.time() - t0, line.rstrip()), flush=True)
    time.sleep(0.01)
