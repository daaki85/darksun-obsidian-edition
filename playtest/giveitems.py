# giveitems.py MEMBER N [FIRST]: memory only, never save after. Gives party member MEMBER up to N
# items of different objects (SEGOBJEX.GFF's item records, each object once, from the FIRSTth on: each
# its own picture on the ground), into free backpack cells, the
# way the Loader gives the arena's ring (ring.give_ring). For filling the ground with items (DROP) in
# a test of the picture cache (2026-11-09, logs/2026-11-09-picture-slot-reuse.md).
import os, sys, struct
PT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, PT)
exec(open(os.path.join(PT, 'live.py')).read())
from dsloader import game, gff, champions, ring, pickpocket
member, n = int(sys.argv[1]), int(sys.argv[2])
first = int(sys.argv[3]) if len(sys.argv) > 3 else 1
chunks = gff.read_gff(open(os.path.join(os.environ.get('DS_GAME', '/tmp/playtest/inst'), 'SEGOBJEX.GFF'), 'rb').read())
# every item record in the objects file with its own object (so its own picture), in object order
from dsloader import dataitems
pool, seen = [], set()
for (ck, num), data in sorted(chunks.items()):
    if ck != 'RDFF':
        continue
    try:
        recs = dataitems.items_of(data)
    except ValueError:
        continue
    for r in recs:
        if len(r) == game.ITEM_SIZE and bytes(r[0:2]) not in seen:
            seen.add(bytes(r[0:2])); pool.append(r)
given, kind, objects = 0, first, set()
while given < n and kind < len(pool):
    rec = pool[kind]
    kind += 1
    if bytes(rec[0:2]) in objects:
        continue
    it = ring.Items(gd)
    cell = pickpocket.free_cell(gd, it, member)
    if cell is None or not it.spare_items():
        print('no room: cell', cell); break
    if pickpocket.party_list(gd, it, member, cell) is None:
        print('no list'); break
    it = ring.Items(gd)
    item = it.word(ring.FREE_ITEMS)
    if item >= game.NO_ITEM:
        print('no item record'); break
    gd.guest.write(gd.ds * 16 + ring.FREE_ITEMS, it.item(item)[game.ITEM_NEXT:game.ITEM_NEXT + 2])
    rec = bytearray(rec)
    rec[8:10] = struct.pack('<H', game.NO_ITEM)  # (no contents: the objects file has 0 there, which in
    rec[0x0C:0x0E] = bytes(2)                    #   memory names item 0: the inventory drew no icons)
    gd.guest.write(it.items + item * game.ITEM_SIZE, bytes(rec))
    if pickpocket.give(gd, ring.Items(gd), member, item, cell):
        objects.add(bytes(rec[0:2])); given += 1
        print('gave item', item, 'type', kind - 1, 'object', -struct.unpack_from('<h', rec, 0)[0], 'cell', cell)
print('given', given, 'next', kind)
