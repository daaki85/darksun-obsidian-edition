# ravitems.py N... [--worn]: Wake of the Ravager's combatant N's items, as its helper reads them: the
# item number, type, worn slot (+13h), plus (+16h), power (the word at +10h) and the type's material
# (+4), flags (+0) and armour byte (+0Bh). --worn (a test edit, never saved): every item in slots 14,
# 15, 16 (where the street's thieves had their armour at the fight's start) moved to the party's worn
# chest 9, arm 0 and legs 6, which the acid check's armour loop takes. --fine (a test edit, never saved):
# every bow (the sequel's type 18) named the Fine Bow (ravager.FINE_BOW_NAME: DSCLOG2's FINE_HIT); each
# item's name number (+14h) is shown too. Run from playtest/.
import sys, os, struct, argparse
PT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(PT, '..', 'obsidian-edition'))
from dsloader.__main__ import connect
from dsloader import game
WORK = os.environ.get('PLAYTEST_WORK', '/tmp/playtest')
g = connect(argparse.Namespace(pid=int(open(os.path.join(WORK, 'rav.pid')).read()), host_base=None))
ds = game.find_data_segment(g)
far = lambda o: (lambda a: a[1]*16 + a[0])(struct.unpack('<HH', g.read(ds*16 + o, 4)))
fig = (ds - 0x47E0 + 0x3F49)*16 + 0xC33          # the combatants: 3 bytes each, the kind and a number
def entry(n): b = g.read(fig + 3*n, 3); return b[0], struct.unpack('<H', b[1:])[0]
cr, it, ty = far(0x19C9), far(0x19C1), far(0x19CD)
WORN = '--worn' in sys.argv
FINE = '--fine' in sys.argv
from dsloader import ravager
for a in [a for a in sys.argv[1:] if a not in ('--worn', '--fine')]:
    k, c = entry(int(a))
    if k != 2: print(a, 'not a creature (kind %d)' % k); continue
    rec = g.read(cr + c*0x31, 0x31)
    print('combatant', a, 'creature', c, 'sheet', struct.unpack_from('<H', rec, 4)[0])
    for off in range(8, 0x0E, 2):                 # (its item lists, as DSCLOG2's ARMOUR_WORN reads them)
        h = struct.unpack_from('<H', rec, off)[0]
        if h >= 9999 or entry(h)[0] != 1: continue
        i, n = entry(h)[1], 0
        while i < 9999 and n < 100:
            r = g.read(it + i*0x17, 0x17); t = struct.unpack_from('<H', r, 0x0A)[0]; tr = g.read(ty + t*15, 15)
            slot = r[0x13]
            if WORN and slot in (14, 15, 16):
                slot = {14: 9, 15: 0, 16: 6}[slot]; g.write(it + i*0x17 + 0x13, bytes([slot]))
            if FINE and t == 18:
                g.write(it + i*0x17 + 0x14, struct.pack('<H', ravager.FINE_BOW_NAME)); r = g.read(it + i*0x17, 0x17)
            print('  item', i, 'type', t, 'slot', slot, 'name', struct.unpack_from('<H', r, 0x14)[0], 'plus', struct.unpack('b', r[0x16:0x17])[0],
                  'power', struct.unpack_from('<H', r, 0x10)[0], 'material', hex(tr[4]), 'flags', hex(tr[0]), 'armour', hex(tr[0x0B]))
            i = struct.unpack_from('<H', r, 4)[0]; n += 1
