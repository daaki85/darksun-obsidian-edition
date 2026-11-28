# 2026-11-28-ravager-camera.py [set] (from playtest/): the sequel's camera (DS:1408h) and the party's map records; 'set' puts the camera on the first at (x-152, y-88), then open and close USE to redraw (ravjump.py's note)
import sys, os, struct, argparse
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'obsidian-edition'))
from dsloader.__main__ import connect
from dsloader import game
g = connect(argparse.Namespace(pid=int(open('/tmp/playtest/rav.pid').read()), host_base=None)); ds = game.find_data_segment(g)
print('camera', struct.unpack('<HH', g.read(ds*16+0x1408, 4)))
recs = [struct.unpack_from('<HH', g.read(ds*16+0x67BB+0x25*i, 0x25), 3) for i in range(4)]
print('party', recs)
if len(sys.argv) > 1:
    x, y = recs[0]; g.write(ds*16+0x1408, struct.pack('<HH', max(0, x-152), max(0, y-88))); print('set')
