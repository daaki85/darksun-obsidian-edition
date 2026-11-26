# nsweapon.py MEMBER [TYPE] [--pack-left]: party creature MEMBER's right-hand item (slot 3) and its type; with TYPE a
# test edit (never saved): that item's type made TYPE; --pack-left moves a left-hand item (slot 10) to the pack (14).
import sys, os, struct, argparse
sys.path.insert(0, '/home/claude/wt-ravager-new-specs/obsidian-edition')
from dsloader.__main__ import connect
from dsloader import game
WORK = os.environ.get('PLAYTEST_WORK', '/tmp/playtest')
g = connect(argparse.Namespace(pid=int(open(os.path.join(WORK, 'rav.pid')).read()), host_base=None))
ds = game.find_data_segment(g)
far = lambda o: (lambda a: a[1]*16 + a[0])(struct.unpack('<HH', g.read(ds*16 + o, 4)))
fig = (ds - 0x47E0 + 0x3F49)*16 + 0xC33
def entry(n): b = g.read(fig + 3*n, 3); return b[0], struct.unpack('<H', b[1:])[0]
cr, it = far(0x19C9), far(0x19C1)
args = [a for a in sys.argv[1:] if not a.startswith('--')]
m = int(args[0]); new = int(args[1]) if len(args) > 1 else None
rec = g.read(cr + m*0x31, 0x31)
for off in range(8, 0x0E, 2):
    h = struct.unpack_from('<H', rec, off)[0]
    if h >= 9999 or entry(h)[0] != 1: continue
    i, n = entry(h)[1], 0
    while i < 9999 and n < 100:
        r = g.read(it + i*0x17, 0x17); t = struct.unpack_from('<H', r, 0x0A)[0]; slot = r[0x13]
        if slot == 3:
            print('member', m, 'right hand item', i, 'type', t, 'plus', struct.unpack('b', r[0x16:0x17])[0])
            if new is not None:
                g.write(it + i*0x17 + 0x0A, struct.pack('<H', new)); print('  type now', new)
        if slot == 10:
            print('member', m, 'left hand item', i, 'type', t)
            if '--pack-left' in sys.argv:
                g.write(it + i*0x17 + 0x13, bytes([14])); print('  moved to the pack')
        i = struct.unpack_from('<H', r, 4)[0]; n += 1
