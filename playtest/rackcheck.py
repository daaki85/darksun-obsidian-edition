# rackcheck.py: the slave pens' weapon rack (object 2599; the old 2563 and the game's 1647 too): its map
# thing, place, item type and the list of what's in it; and wherever a Thornwall is. Read-only.
import os, struct; HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, 'live.py')).read())
from dsloader import ring, game, worldgear
it = ring.Items(gd)
print('rack things', gd.things_of(worldgear.PENS_RACK_OBJECT), 'old 2563', gd.things_of(2563), 'game rack 1647', gd.things_of(1647))
for obj in (worldgear.PENS_RACK_OBJECT, 2563, 1647):
    for t in gd.things_of(obj):
        kind, first = it.thing(t)
        x, y = struct.unpack('<HH', g.read(ds*16 + 0x669D + t*32, 4))
        print(' obj', obj, 'thing', t, 'kind', kind, 'first', first, 'at', x, y)
        if kind == game.THING_ITEM and 0 <= first < game.NO_ITEM:
            rec = it.item(first)
            print('  type', struct.unpack_from('<H', rec, game.ITEM_TYPE)[0], 'contents', struct.unpack_from('<H', rec, ring.ITEM_CONTENTS)[0])
            c = struct.unpack_from('<H', rec, ring.ITEM_CONTENTS)[0]
            if 0 <= c < ring.THING_COUNT:
                print('  in it', [(i, gd.item_name(struct.unpack_from('<H', r, game.ITEM_NAME)[0])) for i, r in it.chain(c)])
n = 0
for t in range(ring.THING_COUNT):
    for i, rec in it.chain(t):
        if struct.unpack_from('<H', rec, game.ITEM_NAME)[0] == worldgear.THORNWALL:
            print('Thornwall at thing', t, 'item', i)
print('RACK_TYPE', worldgear.RACK_TYPE)
