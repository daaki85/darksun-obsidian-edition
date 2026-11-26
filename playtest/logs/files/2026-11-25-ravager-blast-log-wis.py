# 2026-11-25-ravager-blast-log-wis.py MEMBER [WIS]: the creature's abilities, a test edit of WIS
import sys, struct, argparse
import os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'obsidian-edition'))
from dsloader.__main__ import connect
from dsloader import game, ravager
g = connect(argparse.Namespace(pid=int(open('/tmp/playtest/rav.pid').read()), host_base=None))
ds = game.find_data_segment(g)
off, seg = struct.unpack('<HH', g.read(ds * 16 + ravager.CREATURES_PTR, 4))
at = seg*16 + off + int(sys.argv[1]) * ravager.CREATURE_SIZE + 0x19
print('abilities', list(g.read(at, 6)))
if len(sys.argv) > 2: g.write(at + 4, bytes((int(sys.argv[2]),))); print('now', list(g.read(at, 6)))
