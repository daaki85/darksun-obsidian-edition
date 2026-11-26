# 2026-11-26-ravager-new-spells-known.py [MEMBER]: a member's known wizard spells by level in the running sequel (the
# bitset at DS+(3D62h-47E0h):39Ch + 15 a member, the levels' first spells at DS:0656h) and its creature's INT (+1Ch)
import argparse, os, struct, sys
PT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
sys.path.insert(0, os.path.join(PT, '..', 'obsidian-edition'))
from dsloader.__main__ import connect
from dsloader import game
g = connect(argparse.Namespace(pid=int(open('/tmp/playtest/rav.pid').read()), host_base=None))
ds = game.find_data_segment(g); m = int(sys.argv[1]) if len(sys.argv) > 1 else 0
bits = g.read((ds + 0x3D62 - 0x47E0) * 16 + 0x39C + 15 * m, 15)
starts = g.read(ds * 16 + 0x656, 11)
cr = game.far_pointer(g, ds, game.CREATURES_PTR)
print('member', m)
for lv in range(1, 10):
    a, b = starts[lv - 1], starts[lv]
    known = [s for s in range(a, b) if bits[s >> 3] >> (s & 7) & 1]
    print('level', lv, 'spells %d-%d' % (a, b - 1), 'known', len(known), known)
