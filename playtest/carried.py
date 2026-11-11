# carried.py NAME: what the creature named NAME carries, list by list: item, name as the game shows it,
# type, slot, value, plus, name entry and the +02h word (2026-11-11: guavas named "Brgnd.Chst Armor").
import os, sys, struct; HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, 'live.py')).read())
from dsloader import ring, game
it = ring.Items(gd)
for c in range(512):
    rec = gd.creature(c)
    if len(rec) < game.CREATURE_SIZE or gd.creature_name(c) != sys.argv[1]:
        continue
    print('creature', c)
    for off in game.CREATURE_ITEM_LISTS:
        thing, = struct.unpack_from('<h', rec, off)
        for i, d in it.chain(thing, inside=False):
            print(' ', hex(off), i, gd.item_label(d, gd.item_type_record(d)), 'type', struct.unpack_from('<H', d, 0x0A)[0],
                  'slot', d[0x11], 'value', struct.unpack_from('<H', d, 6)[0], 'plus', struct.unpack_from('b', d, 0x14)[0],
                  'name#', struct.unpack_from('<H', d, 0x12)[0], '+2', struct.unpack_from('<H', d, 2)[0])
    break
