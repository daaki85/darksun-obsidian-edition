# 2026-11-26-ravager-new-spells-scroll.py [list | ITEM POWER [FROM] | slot ITEM SLOT]: the sequel's item records (far DS:19C1h, 17h each: +0 the
# entity, +0Ah the type, +10h the power, +13h the slot, +14h the name): list the wizard scrolls (type 77) and
# the party's first items; or make item ITEM a wizard scroll of power POWER (the spell + 1: 321-326 the new
# spells) by copying item FROM's entity, type, one-use flag (+0Eh) and name (default the first one-use type-77 record), the
# spell (+2) and the power both written - a test edit, never saved
import argparse, os, struct, sys
PT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
sys.path.insert(0, os.path.join(PT, '..', 'obsidian-edition'))
from dsloader.__main__ import connect
from dsloader import game
g = connect(argparse.Namespace(pid=int(open('/tmp/playtest/rav.pid').read()), host_base=None))
ds = game.find_data_segment(g)
off, seg = struct.unpack('<HH', g.read(ds * 16 + 0x19C1, 4)); it = seg * 16 + off
rec = lambda i: bytearray(g.read(it + i * 0x17, 0x17))
def show(i):
    r = rec(i); print(i, 'entity %d type %d power %d slot %d +0Eh %d' % (struct.unpack_from('<h', r, 0)[0],
          struct.unpack_from('<H', r, 0x0A)[0], struct.unpack_from('<H', r, 0x10)[0], r[0x13], r[0x0E]), r.hex(' '))
scrolls = [i for i in range(1, 300) if struct.unpack_from('<H', rec(i), 0x0A)[0] == 77]
if len(sys.argv) > 1 and sys.argv[1] == 'slot':
    i = int(sys.argv[2]); r = rec(i); r[0x13] = int(sys.argv[3]); g.write(it + i * 0x17, bytes(r)); show(i)
elif len(sys.argv) < 2 or sys.argv[1] == 'list':
    for i in range(1, 8): show(i)
    print('wizard scrolls:'); [show(i) for i in scrolls]
else:
    i, p = int(sys.argv[1]), int(sys.argv[2]); f = int(sys.argv[3]) if len(sys.argv) > 3 else [i for i in scrolls if rec(i)[0x0E]][0]
    r, s = rec(i), rec(f)
    r[0:2] = s[0:2]; r[0x0A:0x0C] = s[0x0A:0x0C]; r[0x0E] = s[0x0E]; r[0x14:0x17] = s[0x14:0x17]
    struct.pack_into('<H', r, 0x10, p); struct.pack_into('<H', r, 2, p)
    g.write(it + i * 0x17, bytes(r)); show(i)
