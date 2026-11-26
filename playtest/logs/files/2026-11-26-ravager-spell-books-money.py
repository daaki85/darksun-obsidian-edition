# 2026-11-26-ravager-spell-books-money.py [N] (from playtest/): the sequel party's money (the dword at (load + 3C13h):357h), set to N if given - a test edit, never saved
import argparse, os, struct, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'obsidian-edition'))
from dsloader.__main__ import connect
from dsloader import game
g = connect(argparse.Namespace(pid=int(open('/tmp/playtest/rav.pid').read()), host_base=None))
ds = game.find_data_segment(g); at = (ds - 0x47E0 + 0x3C13) * 16 + 0x357
if len(sys.argv) > 1: g.write(at, struct.pack('<I', int(sys.argv[1])))
print('money', struct.unpack('<I', g.read(at, 4))[0])
