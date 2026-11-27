# 2026-11-27-ravager-spell-arrows-quiver.py: test-only memory edit (never saved): the plain +1 arrows (item 2) to pack cell 20, the chill arrows (212) to the quiver (slot 1); prints counts
import sys, os, struct, argparse
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'obsidian-edition'))
from dsloader.__main__ import connect
from dsloader import game
g = connect(argparse.Namespace(pid=int(open('/tmp/playtest/rav.pid').read()), host_base=None))
ds = game.find_data_segment(g)
far = lambda o: (lambda a: a[1]*16 + a[0])(struct.unpack('<HH', g.read(ds*16 + o, 4)))
it = far(0x19C1)
if '--write' in sys.argv:
    g.write(it + 2*0x17 + 0x13, bytes([20])); g.write(it + 212*0x17 + 0x13, bytes([1]))
for i in (2, 212):
    r = g.read(it + i*0x17, 0x17); print(i, 'count', struct.unpack_from('<H', r, 2)[0], 'slot', r[0x13], r.hex())
