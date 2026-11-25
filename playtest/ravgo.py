# ravgo.py [x|y TARGET]... [PID]: walk Wake of the Ravager's leader with the arrow keys until its world x (or y) is
# within 10 of each TARGET in turn (the leader: the party's map object 0-3 on screen; its place the map record's +3,
# +5 from DS:67BBh, as ravfight.py reads; out of a fight only the leader is on the map). Stops a leg after 6 presses
# that don't move it (a wall, a stall: go round). Prints where the leader ends; with no targets, only that. The
# pointer must be the walk arrow (the sword ignores the arrow keys). Run from playtest/.
import sys, os, time, struct, argparse, subprocess
PT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(PT, '..', 'obsidian-edition'))
from dsloader.__main__ import connect
from dsloader import game
WORK = os.environ.get('PLAYTEST_WORK', '/tmp/playtest'); os.environ.setdefault('DISPLAY', ':55')
a = sys.argv[1:]
pid = int(a.pop()) if len(a) % 2 else int(open(os.path.join(WORK, 'rav.pid')).read())
g = connect(argparse.Namespace(pid=pid, host_base=None)); ds = game.find_data_segment(g)
win = subprocess.run(['xdotool', 'search', '--pid', str(pid)], capture_output=True, text=True).stdout.split()[-1]
def leader():
    cx, cy = struct.unpack('<HH', g.read(ds * 16 + 0x1408, 4))
    for i in range(4):
        x, y = struct.unpack_from('<HH', g.read(ds * 16 + 0x67BB + 0x25 * i, 0x25), 3)
        if 0 <= x - cx < 330 and 0 <= y - cy < 210:
            return x, y
    return None
for axis, target in zip(a[::2], map(int, a[1::2])):
    last, stuck = None, 0
    for _ in range(300):
        at = leader(); v = at[0] if axis == 'x' else at[1]
        if abs(v - target) < 10:
            break
        k = ('Right' if v < target else 'Left') if axis == 'x' else ('Down' if v < target else 'Up')
        subprocess.run(['xdotool', 'key', '--window', win, k]); time.sleep(0.35)
        stuck = stuck + 1 if at == last else 0
        if stuck > 5:
            print('stuck at', at); break
        last = at
print('at', leader())
