# itemedit.py MEMBER SLOT [slot=N] [e=N] [f=N]: show (and change) the item party member MEMBER
# has in slot SLOT: its slot byte (+11h), +0Eh (an ability item's amount) and +0Fh (its ability
# byte, FAh-FFh STR-CHA, or a spell). Memory only: never save the game with a change in.
import os, sys, struct
HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, 'live.py')).read())
from dsloader import game
member, slot = int(sys.argv[1]), int(sys.argv[2])
items = game.far_pointer(g, ds, game.ITEMS_PTR)
for index, item, typ in gd._worn(member):
    if item[game.ITEM_SLOT] == slot:
        at = items + index * game.ITEM_SIZE
        for arg in sys.argv[3:]:
            k, v = arg.split('='); v = int(v, 0)
            g.write(at + {'slot': game.ITEM_SLOT, 'e': 0x0E, 'f': 0x0F}[k], bytes([v]))
        item = g.read(at, game.ITEM_SIZE)
        print(f'item {index} at {at:X}: slot {item[game.ITEM_SLOT]} +0E {item[0x0E]} +0F {item[0x0F]:#x}')
        break
else:
    print('no item in that slot'); sys.exit(1)
rec = gd.creature(member)
print('scores', list(rec[game.CREATURE_ABILITIES:game.CREATURE_ABILITIES + 6]))
