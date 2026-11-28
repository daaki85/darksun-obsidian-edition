# 2026-11-27-ravager-defiler-finditem.py ITEM: which thing's item list holds sequel item ITEM, and the thing's map object if any
import sys, struct, argparse
import os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'obsidian-edition'))
from dsloader.__main__ import connect
from dsloader import game
g = connect(argparse.Namespace(pid=int(open(os.path.join(os.environ.get('PLAYTEST_WORK', '/tmp/playtest'), 'rav.pid')).read()), host_base=None))
ds = game.find_data_segment(g)
o, s = struct.unpack('<HH', g.read(ds*16 + 0x19C1, 4)); it = s*16 + o
fig = (ds - 0x47E0 + 0x3F49)*16 + 0xC33
want = int(sys.argv[1])
print('item', want, g.read(it + want*0x17, 0x17).hex(' '))
for t in range(0, 1200):
    kind, first = g.read(fig + 3*t, 1)[0], struct.unpack('<H', g.read(fig + 3*t + 1, 2))[0]
    if kind != 1: continue
    n, seen = first, 0
    while n < 9999 and seen < 200:
        if n == want: print('in thing', t)
        n = struct.unpack('<H', g.read(it + n*0x17 + 4, 2))[0]; seen += 1
