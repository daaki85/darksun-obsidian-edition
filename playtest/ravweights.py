# ravweights.py [N...] [--str N=S]: Wake of the Ravager's item weights as the running game has them: the type
# table's +2 byte (DS:19CDh, 15 bytes a type) for each item combatant N carries (default 0-3), their total, the
# creature's STR (+19h, the index of the STR table 20186h reads) and that STR's maximum press (DS:07B0h, the
# table's second column: "Too heavy a load to carry" past it). --str N=S (a test edit, never saved): combatant N's
# STR in memory made S. --types: the whole table's weights (the Loader's RAV_WEIGHTS seen loaded). Run from playtest/.
import sys, os, struct, argparse
PT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(PT, '..', 'obsidian-edition'))
from dsloader.__main__ import connect
from dsloader import game
WORK = os.environ.get('PLAYTEST_WORK', '/tmp/playtest')
g = connect(argparse.Namespace(pid=int(open(os.path.join(WORK, 'rav.pid')).read()), host_base=None))
ds = game.find_data_segment(g)
far = lambda o: (lambda a: a[1]*16 + a[0])(struct.unpack('<HH', g.read(ds*16 + o, 4)))
fig = (ds - 0x47E0 + 0x3F49)*16 + 0xC33          # the combatants: 3 bytes each, the kind and a number (ravitems.py)
def entry(n): b = g.read(fig + 3*n, 3); return b[0], struct.unpack('<H', b[1:])[0]
cr, it, ty = far(0x19C9), far(0x19C1), far(0x19CD)
press = struct.unpack('<52H', g.read(ds*16 + 0x7B0, 104))
args = sys.argv[1:]
if '--types' in args:
    print('weights:', ' '.join('%d:%d' % (k, g.read(ty + k*15 + 2, 1)[0]) for k in range(135)))
    args.remove('--types')
edits = {}
while '--str' in args:
    i = args.index('--str'); n, s = args[i + 1].split('='); edits[int(n)] = int(s); del args[i:i + 2]
for who in [int(a) for a in args] or sorted(edits) or ([] if '--types' in sys.argv else [0, 1, 2, 3]):
    k, c = entry(who)
    if k != 2: print(who, 'not a creature (kind %d)' % k); continue
    base = cr + c*0x31
    if who in edits: g.write(base + 0x19, bytes([edits[who]])); print('  (test edit: STR %d)' % edits[who])
    rec = g.read(base, 0x31); st = rec[0x19]
    total, items = 0, []
    for off in range(8, 0x0E, 2):
        h = struct.unpack_from('<H', rec, off)[0]
        if h >= 9999 or entry(h)[0] != 1: continue
        i, n = entry(h)[1], 0
        while i < 9999 and n < 100:
            r = g.read(it + i*0x17, 0x17); t = struct.unpack_from('<H', r, 0x0A)[0]; w = g.read(ty + t*15 + 2, 1)[0]
            total += w; items.append('%d:t%d/s%d/w%d' % (i, t, r[0x13], w))
            i = struct.unpack_from('<H', r, 4)[0]; n += 1
    print('combatant %d creature %d STR %d press %d (%.1f lb), carried %d (%.1f lb): %s'
          % (who, c, st, press[st*2 + 1] if st < 26 else -1, (press[st*2 + 1] if st < 26 else 0) / 10, total, total / 10,
             ' '.join(items)))
