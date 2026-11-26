# 2026-11-25-ravager-blast-log-side.py MEMBER [SIDE]: a test edit: the creature's side (+15h in the sequel; 7 the Draxans'), so a power can be aimed at a party member
import sys, os, struct, argparse
import os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'obsidian-edition'))
from dsloader.__main__ import connect
from dsloader import game, ravager
g = connect(argparse.Namespace(pid=int(open('/tmp/playtest/rav.pid').read()), host_base=None))
ds = game.find_data_segment(g)
off, seg = struct.unpack('<HH', g.read(ds * 16 + ravager.CREATURES_PTR, 4))
m = int(sys.argv[1]); at = seg * 16 + off + m * ravager.CREATURE_SIZE + 0x15
print('side was', g.read(at, 1)[0])
if len(sys.argv) > 2: g.write(at, bytes((int(sys.argv[2]),))); print('now', g.read(at, 1)[0])
