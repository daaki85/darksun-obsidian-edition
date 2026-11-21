# picmove.py DX DY: move the hand DX, DY screen pixels (xdotool, relative: DOSBox has the mouse) and
# print how far the game's pointer (DS:A133, game pixels) went. In a window SCALE times the game's
# the Loader's sensitivity (100/SCALE) makes that DX/SCALE across and DY/SCALE down, less a pixel
# or so of rounding; at an edge of the screen the pointer stops.
import sys, os, time, subprocess, struct
dx, dy = sys.argv[1], sys.argv[2]
sys.argv = sys.argv[:1]
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'live.py')).read())
def at(): return struct.unpack('<HH', g.read(ds * 16 + POINTER, 4))
a = at()
subprocess.run(['xdotool', 'mousemove_relative', '--', dx, dy]); time.sleep(0.5)
b = at()
print('hand', dx, dy, 'screen pixels: pointer', a, '->', b, 'moved', (b[0] - a[0], b[1] - a[1]))
