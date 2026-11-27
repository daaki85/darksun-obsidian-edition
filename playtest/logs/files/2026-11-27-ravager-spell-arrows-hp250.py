# 2026-11-27-ravager-spell-arrows-hp250.py: test-only memory edit: the party's creature records' HP (+0) to 250 (never saved)
import sys, os, struct, argparse
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'obsidian-edition'))
from dsloader.__main__ import connect
from dsloader import game
pid = int(open('/tmp/playtest/rav.pid').read())
g = connect(argparse.Namespace(pid=pid, host_base=None)); ds = game.find_data_segment(g)
off, seg = struct.unpack('<HH', g.read(ds*16 + 0x19C9, 4))
for i in range(4):
    g.write(seg*16 + off + i*0x31, struct.pack('<h', 250))
print('done')
