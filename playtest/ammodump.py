# ammodump.py: Jenna's and Ester's quiver, bow and backpack item records (item number, list, address,
# the record in hex: count +2, link +4, type +0Ah, name +12h, plus +14h, slot +11h).
import os, sys, struct
HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, 'live.py')).read())
from dsloader import weaponchoice, spellarrows
for m in (1, 2):
    rec = gd.creature(m)
    print(gd.creature_name(m), 'lists', [struct.unpack_from('<h', rec, o)[0] for o in game.CREATURE_ITEM_LISTS])
    for idx, item, w in gd._worn(m):
        if item[game.ITEM_SLOT] in (1, 2) or item[game.ITEM_SLOT] >= 14:
            print('   idx %4d list %s addr %x  %s' % (idx, w, spellarrows.item_address(gd, idx), item.hex()))
