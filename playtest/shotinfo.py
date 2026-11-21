# shotinfo.py: the camera, member 2's map and screen place, whose turn it is, and each foe on the
# screen with its place and distance (for a shot: click about 10 pixels above the foe's feet).
# Usage: python3 shotinfo.py [MEMBER]
import os, sys, struct
HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, 'live.py')).read())
cx, cy = struct.unpack('<hh', g.read(ds*16 + CAMERA, 4))
def pos(c): return struct.unpack('<hh', g.read(ds*16 + 0x669D + 32*c, 4))
m = int(sys.argv[1]) if len(sys.argv) > 1 else 2
seg = (ds - (0x4356 - 0x37BD)) * 16
print('camera', cx, cy, 'member', m, '+181h =', g.read(seg + 0x181 + m, 1)[0], 'turn', struct.unpack('<h', g.read(ds*16+0x4979,2))[0])
ex, ey = pos(m); print('member map', ex, ey, 'screen', ex-cx, ey-cy)
for c in range(17, 48):
    x, y = pos(c)
    if x <= 0: continue
    sx, sy = x-cx, y-cy
    d = max(abs(x-ex), abs(y-ey))
    if 10 < sx < 300 and 20 < sy < 160: print(c, gd.creature_name(gd.combatant_creature(c)) if hasattr(gd,'combatant_creature') else '', 'screen', sx, sy, 'dist', d)
