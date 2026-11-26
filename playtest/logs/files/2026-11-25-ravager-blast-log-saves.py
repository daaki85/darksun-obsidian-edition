# 2026-11-25-ravager-blast-log-saves.py MEMBER [VALUE]: the member's sheet's five save numbers (+30h, the sequel's: the save routine's [bp-1]); VALUE a test edit
import sys, struct, argparse
import os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'obsidian-edition'))
from dsloader.__main__ import connect
from dsloader import game, ravager
g = connect(argparse.Namespace(pid=int(open('/tmp/playtest/rav.pid').read()), host_base=None))
ds = game.find_data_segment(g)
off, seg = struct.unpack('<HH', g.read(ds * 16 + ravager.CREATURES_PTR, 4))
m = int(sys.argv[1]); idx = struct.unpack('<H', g.read(seg * 16 + off + m * ravager.CREATURE_SIZE + 4, 2))[0]
so, ss = struct.unpack('<HH', g.read(ds * 16 + ravager.SHEETS_PTR, 4))
at = ss * 16 + so + idx * ravager.SHEET_SIZE + 0x30
print('sheet', idx, 'saves', list(g.read(at, 5)))
if len(sys.argv) > 2: g.write(at, bytes([int(sys.argv[2])] * 5)); print('now', list(g.read(at, 5)))
