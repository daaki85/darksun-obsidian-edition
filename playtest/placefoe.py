# placefoe.py THING DX DY [MEMBER]: map thing THING (a foe's combatant number) put DX, DY squares from party
# member MEMBER (default 1) in memory (DS:669Dh + 20h a thing, in sixteenths): a foe beside a member for a
# melee test, or two squares off for a reach test. Memory only: never save after (logs/2026-11-23-ravager-weapons.md).
import os, sys, struct
PT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, PT)
exec(open(os.path.join(PT, 'live.py')).read())
t, dx, dy = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]); m = int(sys.argv[4]) if len(sys.argv) > 4 else 1
x, y = struct.unpack('<HH', g.read(ds * 16 + 0x669D + 32 * m, 4))
print('member', m, 'at', x, y, 'square', x // 16, y // 16)
g.write(ds * 16 + 0x669D + 32 * t, struct.pack('<HH', x + 16 * dx, y + 16 * dy))
print('thing', t, 'now', struct.unpack('<HH', g.read(ds * 16 + 0x669D + 32 * t, 4)))
