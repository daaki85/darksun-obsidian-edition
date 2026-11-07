# bigthings.py: the map's things with their walking picture (+18h), its frames' most runs (from the Loader's SEGOBJEX.GFF) and where they stand, the most runs first: for a test of drawing a big frame
import os, sys, struct
PT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, PT)
exec(open(os.path.join(PT, 'live.py')).read())
sys.path.insert(0, os.path.join(PT, '..', 'obsidian-edition'))
from dsloader import gff
ch = gff.read_gff(open(os.path.join(PT, '..', 'obsidian-edition', 'dos', 'SEGOBJEX.GFF'), 'rb').read())
def most(n):
    c = ch.get(('BMP ', n))
    if not c: return None
    out = 0; count, = struct.unpack_from('<H', c, 4)
    for i in range(count):
        off, = struct.unpack_from('<I', c, 6 + 4 * i); pos = off + 4; r = 0
        while c[pos] != 0xFF:
            pos += 1
            while True:
                x, fl, cnt, ln = struct.unpack_from('<BBBB', c, pos); pos += 4 + ln; r += 1
                if fl & 0x80: break
        out = max(out, r)
    return out
data = g.read(ds * 16 + 0x6694, 520 * 32)
cam = struct.unpack('<hh', g.read(ds * 16 + CAMERA, 4))
rows = []
for t in range(520):
    e = data[t * 32:t * 32 + 32]
    x, y = struct.unpack('<HH', g.read(ds * 16 + game.POSITIONS + t * 32, 4))
    pic, = struct.unpack_from('<H', e, 0x18)
    if pic and pic < 0xFFFF and x:
        rows.append((t, pic, most(pic), x, y))
for r in sorted(rows, key=lambda r: -(r[2] or 0))[:12]: print(r)
print('camera', cam)
