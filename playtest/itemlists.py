# itemlists.py: each party member's three item lists (+08h worn, +0Ah held weapons, +0Ch the
# backpack) as (item, slot byte, type). The game's AC counts the +08h list only (PLAYTESTING.md).
import os, struct
HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, 'live.py')).read())
from dsloader import game
for n in range(4):
    print(n, {hex(f): [(i, item[game.ITEM_SLOT], struct.unpack_from('<H', item, game.ITEM_TYPE)[0]) for i, item, t in gd._worn(n, (f,))] for f in game.CREATURE_ITEM_LISTS})
