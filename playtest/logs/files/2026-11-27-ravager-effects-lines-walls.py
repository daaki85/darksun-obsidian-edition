# walls.py [SPELL...]: a test edit (never saved): Ar'Anda knows only the wizard SPELLs (default 54 55: Wall of Fire and
# Wall of Ice, the two wizard walls the AI's weights (selector 310h, a signed byte a spell) don't give 0), 3 casts at
# every level, her first class level 9 (4th-level spells), and her weapons (slots 2, 3, 10) moved to backpack cells
# 29-31. Prints her creature's INT (+1Ch: the AI casts only above 9) and the weights of the known spells.
import argparse, os, struct, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'obsidian-edition'))
from dsloader.__main__ import connect
from dsloader import game
g = connect(argparse.Namespace(pid=int(open(os.path.join(os.environ.get('PLAYTEST_WORK', '/tmp/playtest'), 'rav.pid')).read()), host_base=None))
ds = game.find_data_segment(g); load = ds - 0x47E0
spells = [int(a) for a in sys.argv[1:]] or [54, 55]
b = bytearray(15)
for s in spells:
    b[s // 8] |= 1 << (s % 8)
g.write(0x3F3DC, bytes(b)); g.write(ds * 16 + 0x446A, bytes([3] * 9))
off, seg = struct.unpack('<HH', g.read(ds * 16 + 0x19C5, 4)); g.write(seg * 16 + off + 0x1E, bytes([9]))
co, cs = struct.unpack('<HH', g.read(ds * 16 + 0x19C9, 4)); rec = g.read(cs * 16 + co, 0x31)
print('known', [i for i in range(120) if g.read(0x3F3DC, 15)[i // 8] >> (i % 8) & 1], 'INT', rec[0x1C])
w = struct.unpack('<320b', g.read((load + 0x3C78) * 16, 320)); print('weights', {s: w[s] for s in spells})
io, iseg = struct.unpack('<HH', g.read(ds * 16 + 0x19C1, 4)); it = iseg * 16 + io
moved = {2: 29, 3: 30, 10: 31}
for lst in (8, 10, 12):
    h = struct.unpack_from('<H', rec, lst)[0]
    tab = (load + 0x3F49) * 16 + 0xC33
    if h >= 9999 or g.read(tab + h * 3, 1)[0] != 1:
        continue
    i = struct.unpack('<H', g.read(tab + h * 3 + 1, 2))[0]; n = 0
    while i < 9999 and n < 100:
        r = g.read(it + i * 0x17, 0x17)
        if r[0x13] in moved:
            print('item', i, 'slot', r[0x13], '->', moved[r[0x13]]); g.write(it + i * 0x17 + 0x13, bytes([moved[r[0x13]]]))
        i = struct.unpack_from('<H', r, 4)[0]; n += 1
