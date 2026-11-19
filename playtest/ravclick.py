# ravclick.py X Y [left|right|none] [PID]: Wake of the Ravager's click.py: moves the pointer to game pixel
# X,Y (320x200) by relative moves until the game's own pointer (DS:A109h x, A10Bh y; SL's is DS:A133h)
# reads it, then a slow press (0.3 s: the USE screen's portraits and buttons lose a quick one). PID: the
# DOSBox (default $WORK/rav.pid's, else the newest). The first click of a run only captures the mouse.
import sys, os, time, struct, subprocess, argparse
PT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(PT, '..', 'obsidian-edition'))
from dsloader.__main__ import connect
from dsloader import game
from dsloader.process import find_dosbox_processes
POINTER = 0xA109
x, y = int(sys.argv[1]), int(sys.argv[2]); how = sys.argv[3] if len(sys.argv) > 3 else 'left'
work = os.environ.get('PLAYTEST_WORK', '/tmp/playtest'); pf = os.path.join(work, 'rav.pid')
pid = int(sys.argv[4]) if len(sys.argv) > 4 else int(open(pf).read()) if os.path.exists(pf) else max(p for p, _ in find_dosbox_processes())
g = connect(argparse.Namespace(pid=pid, host_base=None)); ds = game.find_data_segment(g)
os.environ.setdefault('DISPLAY', ':55')
at = lambda: struct.unpack('<HH', g.read(ds * 16 + POINTER, 4))
for _ in range(15):
    px, py = at()
    if abs(px - x) <= 1 and abs(py - y) <= 1: break
    # DOSBox's mouse moves about 1 game pixel for 1 X pixel across and less down: small steps, read again
    subprocess.run(['xdotool', 'mousemove_relative', '--', str(int((x - px) * 0.9)), str(int((y - py) * 1.4))]); time.sleep(0.25)
print('pointer', at())
if how != 'none':
    b = '3' if how == 'right' else '1'
    subprocess.run(['xdotool', 'mousedown', b]); time.sleep(0.3); subprocess.run(['xdotool', 'mouseup', b])
