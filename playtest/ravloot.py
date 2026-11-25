"""ravloot.py: looting with T, selling with S and M/U/I in the running sequel ($WORK/rav.pid): DSCLOG2's LOOT_KEY and
SELL_KEY fields (its header's +1846 to +1859, DSCLOG's), the shop loop's passes and OVERHEAD (from `nasm -l`'s
symbols: the helper rebuilt into a map), and the game's words they read and the Loader writes: the container whose
window is open (DS:05D6h), a merchant's shop open (DS:143Dh) and its merchant (DS:1A30h), the character on show
(selector 370h:0B44h), the party's money (2E8h:357h), the free things' list and count (DS:56EFh, 55C6h, walked)
and the free item records (DS:5AF3h, walked).
  python3 ravloot.py             all of that
  python3 ravloot.py thing T     map thing T: its kind and first item, a container's contents, each item's
                                 type, slot, price, plus, power and name number"""
import argparse, os, re, struct, subprocess, sys, tempfile
PT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(PT, '..', 'obsidian-edition'))
from dsloader.__main__ import connect
from dsloader import game
WORK = os.environ.get('PLAYTEST_WORK', '/tmp/playtest')
g = connect(argparse.Namespace(pid=int(open(os.path.join(WORK, 'rav.pid')).read()), host_base=None))
seg = struct.unpack('<H', g.read(0xF5 * 4 + 2, 2))[0]
low = g.read(seg * 16, 0x10000)
hdr = seg * 16 + low.find(b'DSCLOGR1')
w = lambda at, n=1: struct.unpack('<%dH' % n, g.read(at, 2 * n))
ds = game.find_data_segment(g)
load = ds - 0x47E0
far = lambda off: (lambda o, s: s * 16 + o)(*struct.unpack('<HH', g.read(ds * 16 + off, 4)))
ITM, THINGS = far(0x19C1), (load + 0x3F49) * 16 + 0x0C33
thing = lambda t: struct.unpack('<Bh', g.read(THINGS + t * 3, 3))


def chain(first, most=400):
    out = []
    while 0 <= first < 400 and len(out) < most and first not in out:
        out.append(first)
        first = struct.unpack('<h', g.read(ITM + first * 0x17 + 4, 2))[0]
    return out


def show(i):
    r = g.read(ITM + i * 0x17, 0x17)
    return 'item %d type %d slot %d price %d plus %d power %d name %d contents %d' % (
        i, *struct.unpack_from('<H', r, 0x0A), r[0x13], *struct.unpack_from('<H', r, 6),
        struct.unpack_from('b', r, 0x16)[0], *struct.unpack_from('<H', r, 0x10), *struct.unpack_from('<H', r, 0x14),
        *struct.unpack_from('<H', r, 8))


if len(sys.argv) > 2 and sys.argv[1] == 'thing':
    t = int(sys.argv[2], 0)
    kind, first = thing(t)
    print('thing %d kind %d first %d' % (t, kind, first))
    if kind == 1:
        for i in chain(first):
            print(' ', show(i))
            c = struct.unpack('<H', g.read(ITM + i * 0x17 + 8, 2))[0]
            if c < 520 and thing(c)[0] == 1:
                for j in chain(thing(c)[1]):
                    print('    in it:', show(j))
    sys.exit()

sym = {}
with tempfile.TemporaryDirectory() as tmp:
    asm = os.path.join(PT, '..', 'obsidian-edition', 'dos', 'dsclog2.asm')
    src, mp = os.path.join(tmp, 'm.asm'), os.path.join(tmp, 'm.map')
    open(src, 'w').write('[map symbols %s]\n' % mp + open(asm).read())
    subprocess.run(['nasm', '-f', 'bin', '-I', os.path.dirname(asm) + '/', '-o', os.path.join(tmp, 'x'), src], check=True)
    for line in open(mp).read().split('Section image')[1].splitlines():
        p = line.split()
        if len(p) == 3 and re.fullmatch('[0-9A-F]+', p[1]):
            sym[p[2]] = int(p[1], 16)
base = hdr - sym['hdr']
print('loot seq %d thing %04X mode %d  sell seq %d member %d merchant %d shop_at %d  (BIOS tick %d)' % (
    *w(hdr + 1846, 3), *w(hdr + 1852, 4), *w(0x46C)))
print('shop passes %d  overhead %r  pages_back %d  quick loads %d' % (
    *w(base + sym['shop_passes']), g.read(base + sym['overhead'], 1), *w(base + sym['pages_back']), *w(base + sym['quick_loads'])))
print('container open %d  shop open %d  merchant %d  on show %d  money %d' % (
    *w(ds * 16 + 0x05D6), g.read(ds * 16 + 0x143D, 1)[0], *w(ds * 16 + 0x1A30), *w((load + 0x3E71) * 16 + 0x0B44),
    struct.unpack('<I', g.read((load + 0x3C13) * 16 + 0x357, 4))[0]))
free, n = w(ds * 16 + 0x56EF)[0], 0
seen = set()
while free < 520 and free not in seen and n < 600:
    seen.add(free); n += 1
    free = thing(free)[1] & 0xFFFF
print('free things: first %d, %d on the list, count out %d;  free items: first %d, %d on the list' % (
    *w(ds * 16 + 0x56EF), n, *w(ds * 16 + 0x55C6), *w(ds * 16 + 0x5AF3), len(chain(w(ds * 16 + 0x5AF3)[0]))))
