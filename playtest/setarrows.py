# setarrows.py MEMBER N: the member's quiver stack's count made N, in memory (never save after;
# set it before a fight starts: logs/2026-11-14-quiver-turn.md).
import os, sys, struct
HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, 'live.py')).read())
from dsloader import weaponchoice, spellarrows
for idx, item, _ in gd._worn(int(sys.argv[1])):
    if item[game.ITEM_SLOT] == weaponchoice.AMMO_SLOT:
        a = spellarrows.item_address(gd, idx) + weaponchoice.ITEM_COUNT
        gd.guest.write(a, struct.pack('<H', int(sys.argv[2]))); print('arrows', struct.unpack('<H', g.read(a, 2))[0], 'item', idx)
