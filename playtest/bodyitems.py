# bodyitems.py: each Dead Body on the map (object 1101 or the thri-kreen's 2666), its things: item, name,
# type, plus, power, value, name number and +02h, and the type's worn place, weight and flags.
import os, struct; HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, 'live.py')).read())
from dsloader import ring, game
it = ring.Items(gd)
cx, cy = struct.unpack('<HH', g.read(ds*16 + 0x1178, 4))
for t in range(520):
    obj, = struct.unpack('<h', g.read(ds*16 + 0x66AE + t*32, 2))
    if abs(obj) not in (1101, 2666):
        continue
    x, y = struct.unpack('<HH', g.read(ds*16 + 0x669D + t*32, 4))
    kind, item = it.thing(t)
    c = struct.unpack_from('<H', it.item(item), 8)[0]
    print('body thing', t, 'screen', x - cx, y - cy)
    for i, d in (it.chain(c, inside=False) if c < 520 else []):
        tr = gd.item_type_record(d)
        print('  ', i, gd.item_label(d, tr), 'type', struct.unpack_from('<H', d, 0x0A)[0], 'plus', struct.unpack_from('b', d, 0x14)[0],
              'power', d[0x0F], 'value', struct.unpack_from('<H', d, 6)[0], 'name#', struct.unpack_from('<H', d, 0x12)[0],
              '+2', struct.unpack_from('<H', d, 2)[0], '| worn', tr[9], 'weight', struct.unpack_from('<H', tr, 4)[0], 'flags', hex(tr[0]))
