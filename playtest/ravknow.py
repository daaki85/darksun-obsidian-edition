# ravknow.py SPELL [LEVEL]: a test edit (never saved): Wake of the Ravager's first party member (Ar'anda
# in the opening party; the only member whose bitset address is known) knows wizard spell SPELL (its bit in the 15-byte bitset at
# 3F3DCh, which holds after a load too), 3 wizard casts at every level (DS:446Ah + 22h a member), and,
# with LEVEL, the first class level (sheet +1Eh) made LEVEL, so the USE screen offers the spell's level
# (Crystal Brittle, 103, is level 9: LEVEL 18; a level
# 6 preserver was offered levels 1-3 only). Run from playtest/.
import sys, os, struct, argparse
PT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(PT, '..', 'obsidian-edition'))
from dsloader.__main__ import connect
from dsloader import game
WORK = os.environ.get('PLAYTEST_WORK', '/tmp/playtest')
g = connect(argparse.Namespace(pid=int(open(os.path.join(WORK, 'rav.pid')).read()), host_base=None))
ds = game.find_data_segment(g)
spell, member = int(sys.argv[1]), 0
KNOWN = 0x3F3DC
b = bytearray(g.read(KNOWN, 15)); b[spell // 8] |= 1 << (spell % 8); g.write(KNOWN, bytes(b))
g.write(ds*16 + 0x446A + 0x22*member, bytes([3] * 9))
if len(sys.argv) > 2:
    o, s = struct.unpack('<HH', g.read(ds*16 + 0x19C5, 4)); g.write(s*16 + o + member*0x42 + 0x1E, bytes([int(sys.argv[2])]))
print('known', [i for i in range(120) if g.read(KNOWN, 15)[i // 8] >> (i % 8) & 1])
