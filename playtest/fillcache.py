# fillcache.py MEMBER SLOT UNTIL: fills the game's picture slots (cachelist.py) the way a change of
# gear does, fast: the slot byte (+11h) of the item MEMBER has in SLOT (itemedit.py's) set to 50
# (no place: not drawn on the figure) and back, so what it wears changes and the Loader dresses its
# figure anew each time (sprites.py: its old pictures marked FFFEh, the new one given a new slot),
# until UNTIL slots are taken (at most 300). Ends with the slot byte as it was. Memory edit: never
# save after (2026-11-09, logs/2026-11-09-missing-figures.md).
import os, sys, struct, time
PT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, PT)
exec(open(os.path.join(PT, 'live.py')).read())
from dsloader import game
m, slot, until = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
items = game.far_pointer(g, ds, game.ITEMS_PTR)
at = next(items + i * game.ITEM_SIZE for i, item, t in gd._worn(m) if item[game.ITEM_SLOT] == slot)
def taken(): return struct.unpack('<H', g.read(ds * 16 + 0x1F84, 2))[0]
n = 0
try:
    while taken() < until:
        before = taken(); n += 1
        g.write(at + game.ITEM_SLOT, bytes([50 if n % 2 else slot]))
        t0 = time.time()
        while taken() == before and time.time() - t0 < 4: time.sleep(0.1)
        print(n, taken(), flush=True)
finally:
    g.write(at + game.ITEM_SLOT, bytes([slot]))
time.sleep(1.5); print('done', taken())
