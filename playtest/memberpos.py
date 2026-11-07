# memberpos.py N: party member N's figure on screen, to click (its feet x, and y - 12), from its map position and the camera; a figure off the screen gives numbers outside 0-319 x 0-199
import os, sys, struct
PT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, PT)
exec(open(os.path.join(PT, 'live.py')).read())
from dsloader import game
n = int(sys.argv[1])
x, y = struct.unpack('<HH', g.read(ds * 16 + game.POSITIONS + n * 32, 4))
cx, cy = struct.unpack('<hh', g.read(ds * 16 + CAMERA, 4))
print(x - cx, y - cy - 12)
