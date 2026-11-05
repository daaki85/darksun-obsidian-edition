# scrolltest.py [shinobi] [give]: member 0 made an 8th-level Shinobi (memory only: never save after) and
# the defilers' scrolls (defilerscrolls.scroll) given to members 0 and 2. Run from playtest/.
import os, sys, struct; HERE = os.path.dirname(os.path.abspath(__file__)); exec(open(os.path.join(HERE, "live.py")).read())
from dsloader import game, defilerscrolls, npcitems, kitpages
def sheet_at(m):
    index = struct.unpack_from('<H', gd.creature(m), 4)[0]
    return game.far_pointer(g, ds, 0x1661) + index * game.SHEET_SIZE
at = sheet_at(0)
s = g.read(at, game.SHEET_SIZE)
print('before', s[0x21:0x24].hex(), s[0x24:0x27].hex(), hex(s[0x43]), hex(struct.unpack_from('<H', s, 0x12)[0]), 'race', s[0x18])
if 'shinobi' in sys.argv:
    g.write(at + 0x21, bytes([17])); g.write(at + 0x24, bytes([8])); g.write(at + 0x43, bytes([3]))
    g.write(at + 0x12, struct.pack('<H', 0x400))
s = g.read(at, game.SHEET_SIZE)
print('after', s[0x21:0x24].hex(), s[0x24:0x27].hex(), hex(s[0x43]), 'kits', gd.kit_ids(0), gd.kit(0))
gifts = {0: [game.FOG_SPELL, game.SPOOK_SPELL, game.REFLECT_SPELL, 8], 2: [game.FOG_SPELL, game.SPOOK_SPELL, game.REFLECT_SPELL]}
if 'give' in sys.argv:
    for m, spells in gifts.items():
        for sp in spells:
            print(m, sp, gd.spell_level(sp), npcitems.add_to(gd, m, defilerscrolls.scroll(sp, gd.spell_level(sp))))
