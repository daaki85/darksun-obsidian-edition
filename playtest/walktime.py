# walktime.py N X Y [DIR]: a click at screen X, Y (game pixels), then party member N's map position every 50 ms until it has stood still for 1.5 s: each step's time (the walking pace), and with DIR a window grab at each step (DIR/wNN.png)
import os, sys, struct, time, subprocess
PT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, PT)
exec(open(os.path.join(PT, 'live.py')).read())
from dsloader import game
n, X, Y = map(int, sys.argv[1:4])
out = sys.argv[4] if len(sys.argv) > 4 else None
def pos(): return struct.unpack('<HH', g.read(ds * 16 + game.POSITIONS + n * 32, 4))
wid = subprocess.run(['xdotool', 'search', '--class', 'dosbox'], capture_output=True, text=True).stdout.split()[0]
p0 = pos(); subprocess.run(['python3', os.path.join(PT, 'click.py'), str(X), str(Y), 'left'], capture_output=True)
t0 = time.time(); last, still, first, k = p0, t0, None, 0
trail = []
while time.time() - still < 1.5 and time.time() - t0 < 20:
    p = pos()
    if p != last:
        trail.append((round(time.time() - t0, 2), p)); last, still = p, time.time()
        if first is None: first = time.time()
        if out and k < 30:
            subprocess.run(['import', '-window', wid, f'{out}/w{k:02d}.png']); k += 1
    time.sleep(0.05)
print('from', p0, 'to', last, 'moves', len(trail))
if trail: print('first move %.2f s after the click, last at %.2f s' % (trail[0][0], trail[-1][0]))
for t, p in trail: print(t, p)
