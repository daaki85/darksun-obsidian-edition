# thief.py MEMBER LEVEL | MEMBER off: a party member made a thief of LEVEL in memory (class 17 in a
# free class place of the sheet, its level, the thief flag 400h), or no thief (off). Never save after.
import os, sys, struct; HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, 'live.py')).read())
from dsloader import game
m = int(sys.argv[1])
index = struct.unpack_from('<H', gd.creature(m), 4)[0]
at = game.far_pointer(g, ds, 0x1661) + index * game.SHEET_SIZE
cl, lv = list(g.read(at + 0x21, 3)), list(g.read(at + 0x24, 3))
flags = struct.unpack('<H', g.read(at + 0x12, 2))[0]
if sys.argv[2] == 'off':
    for i in range(3):
        if cl[i] == 17:
            cl[i] = lv[i] = 0
    flags &= ~0x400
else:
    slot = cl.index(17) if 17 in cl else (cl.index(0) if 0 in cl else 2)
    cl[slot], lv[slot] = 17, int(sys.argv[2])
    flags |= 0x400
g.write(at + 0x21, bytes(cl)); g.write(at + 0x24, bytes(lv)); g.write(at + 0x12, struct.pack('<H', flags))
print(gd.creature_name(m), 'classes', cl, 'levels', lv, 'flags %04X' % flags, 'skills', gd.thief_skills_now(m)[:3])
