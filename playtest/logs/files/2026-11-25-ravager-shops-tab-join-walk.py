# 2026-11-25-ravager-shops-tab-join-walk.py KEY AXIS TARGET (run from playtest/): in the running sequel
# ($WORK/rav.pid), presses the arrow KEY until the leader (map thing 2: DS:67BBh + 25h x 2, its feet +0Ah,
# +0Ch) has passed TARGET on AXIS (x|y); stops when six presses don't move it. Notaku's from
# ravager-after-ambush: Up y 1224, Left x 296, Up y 936.
import sys, os, struct, argparse, subprocess, time
PIDF = os.path.join(os.environ.get('PLAYTEST_WORK', '/tmp/playtest'), 'rav.pid')
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'obsidian-edition'))
from dsloader.__main__ import connect
from dsloader import game
g = connect(argparse.Namespace(pid=int(open(PIDF).read()), host_base=None))
ds = game.find_data_segment(g)
W = subprocess.check_output(['xdotool','search','--pid',open(PIDF).read().strip()]).split()[-1]
key, axis, tgt = sys.argv[1], sys.argv[2], int(sys.argv[3])
def feet():
    return struct.unpack('<hh', g.read(ds*16 + 0x67BB + 0x25*2 + 0x0A, 4))
start = feet(); last = start; same = 0
for i in range(200):
    x, y = feet(); v = x if axis == 'x' else y
    if (key in ('Up','Left') and v <= tgt) or (key in ('Down','Right') and v >= tgt): break
    subprocess.run(['xdotool','key','--window',W,key]); time.sleep(0.45)
    if feet() == last: same += 1
    else: same = 0
    last = feet()
    if same >= 6: print('blocked'); break
print('from', start, 'now', feet())
