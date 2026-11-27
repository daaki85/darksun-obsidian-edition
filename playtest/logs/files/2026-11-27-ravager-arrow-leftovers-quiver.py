# 2026-11-27-ravager-arrow-leftovers-quiver.py: test-only memory edit (never saved): swap the slots of item A (to the quiver, slot 1) and item B (to pack cell N, default 16): python3 THIS A B [N]
import sys, os, struct, argparse
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'obsidian-edition'))
from dsloader.__main__ import connect
from dsloader import game
g = connect(argparse.Namespace(pid=int(open('/tmp/playtest/rav.pid').read()), host_base=None))
ds = game.find_data_segment(g)
off, seg = struct.unpack('<HH', g.read(ds*16 + 0x19C1, 4)); it = seg*16 + off
a, b = int(sys.argv[1]), int(sys.argv[2])
g.write(it + b*0x17 + 0x13, bytes([int(sys.argv[3]) if len(sys.argv) > 3 else 16])); g.write(it + a*0x17 + 0x13, bytes([1]))
for i in (a, b):
    r = g.read(it + i*0x17, 0x17); print(i, 'count', struct.unpack_from('<H', r, 2)[0], 'slot', r[0x13])
