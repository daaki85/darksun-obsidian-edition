# click.py X Y [left|right|none]: move the game's pointer to game pixel X,Y (320x200) and click.
# DOSBox captures the mouse, so absolute moves don't work: it moves relatively until the game's own
# pointer (DS:A133) reads X,Y. Right-click on the map cycles the pointer mode (arrow = Walk/use,
# then a red sword = attack, then another red one); the plain arrow walks.
import sys, os, time, subprocess, struct
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'live.py')).read())
x, y = int(sys.argv[1]), int(sys.argv[2]); how = sys.argv[3] if len(sys.argv) > 3 else 'left'
def at(): return struct.unpack('<HH', g.read(ds * 16 + POINTER, 4))
for _ in range(12):
    px, py = at()
    if abs(px - x) <= 1 and abs(py - y) <= 1: break
    subprocess.run(['xdotool', 'mousemove_relative', '--', str(x - px), str(y - py)]); time.sleep(0.15)
print('pointer', at())
if how != 'none':
    b = '3' if how == 'right' else '1'
    subprocess.run(['xdotool', 'mousedown', b]); time.sleep(0.12); subprocess.run(['xdotool', 'mouseup', b])
