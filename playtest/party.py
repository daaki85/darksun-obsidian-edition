# party.py: each party member's classes and levels, the gladiator flag, the scores the game
# uses now (the creature record's), and every item with its slot, +0Eh and +0Fh (ability bytes)
import os, struct
HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, 'live.py')).read())
from dsloader import game
for n in range(4):
    rec, sheet = gd.creature(n), gd.sheet(n)
    if len(rec) < game.CREATURE_SIZE: continue
    classes = [(sheet[game.SHEET_CLASSES + i], sheet[game.SHEET_LEVELS + i]) for i in range(3)]
    flags = struct.unpack_from('<H', sheet, game.SHEET_FLAGS)[0]
    scores = list(rec[game.CREATURE_ABILITIES:game.CREATURE_ABILITIES + 6])
    print(f'#{n} {gd.name(n) if hasattr(gd, "name") else ""} classes {classes} flags {flags:04x} '
          f'gladiator {bool(flags & game.SHEET_FLAG_GLADIATOR)} base AC {struct.unpack_from("b", sheet, game.SHEET_BASE_AC)[0]} scores {scores} counted AC {gd.counted_ac(n)}')
    for lst, item, typ in gd._worn(n):
        num = None
        print(f'     item slot {item[game.ITEM_SLOT]:3d} type {struct.unpack_from("<H", item, game.ITEM_TYPE)[0]:4d} +0E {item[0x0E]:3d} +0F {item[0x0F]:3d}  {gd.item_name(struct.unpack_from("<H", item, game.ITEM_NAME)[0]) if hasattr(gd, "item_name") else ""}')
