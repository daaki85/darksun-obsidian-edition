# usable.py [all]: what the Loader would mark as usable while Alt is held (dsloader/usable.py): each
# thing's number, kind, name, map place and screen place, those in the view only unless "all"; then
# the four it would name (the nearest the pointer), the triggers' lists, and whether Alt reads held.
import os, sys, struct
PT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, PT)
exec(open(os.path.join(PT, 'live.py')).read())
from dsloader import usable
cam = struct.unpack('<hh', g.read(ds * 16 + CAMERA, 4)); ptr = struct.unpack('<hh', g.read(ds * 16 + POINTER, 4))
found = usable.marks(gd)
print(f'camera {cam} pointer {ptr} alt held {usable.alt_held(g)} fight {gd.in_combat()} marks {len(found)}')
for m in found:
    sx, sy = m.x - cam[0], m.y - cam[1]
    if sys.argv[1:] == ['all'] or (0 <= sx < 320 and 0 <= sy < 200):
        print(f'  thing {m.thing:3} {m.kind:9} {m.name!r:24} map {m.x},{m.y} screen {sx},{sy} up {m.up}')
print('named:', [(m.thing, m.name) for m in usable.nearest(found, cam, ptr)])
print('triggers:', {hex(k): len(v) for k, v in usable.triggers(gd).items()})
