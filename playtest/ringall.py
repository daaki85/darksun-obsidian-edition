# ringall.py [N | all | still | clear] [KIND]: for measuring the rings' cost (framerate.py): a ring (DSCLOG's RING_TAB,
# kind 1) under every one of the game's things on the screen now, whatever it is (N: under the N
# nearest the screen's middle; KIND 2: the Tab ring's thicker one, about 2.3 times the pixels), or all but the party's four (still), or none (clear). The Loader writes its own table only when that
# changes, so these stay until Alt is pressed or a fight's Tab ring moves. Prints how many.
import os, sys, struct
PT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, PT)
arg = sys.argv[1] if len(sys.argv) > 1 else 'all'; kind = int(sys.argv[2]) if len(sys.argv) > 2 else 1; sys.argv = sys.argv[:1]
exec(open(os.path.join(PT, 'live.py')).read())
from dsloader import dicelog, rings, shadows, usable
import re
mem = g.read(0, 0x110000); hdr = next(m.start() for m in re.finditer(re.escape(dicelog.HDR_SIG), mem) if m.start() % 16 == 0)
far = struct.unpack('<H', g.read(hdr + rings.TSR_FAR_SEG, 2))[0] * 16
off, = struct.unpack('<H', g.read(hdr + rings.TSR_RING_TAB, 2))
cx, cy = struct.unpack('<hh', g.read(ds * 16 + CAMERA, 4))
seen = sorted((abs(x - cx - 160) + abs(y - cy - 100), t) for t, x, y in usable.draw_list(gd)
              if 0 <= x - cx < 320 and 0 <= y - cy < 200)
table = bytearray(rings.THINGS)
if arg != 'clear':
    for _, t in seen[:len(seen) if arg in ('all', 'still') else int(arg)]:
        if arg != 'still' or t > 3:
            table[t] = kind
g.write(far + off, bytes(table)); shadows.redraw(gd, hdr)
print('rings on', sum(1 for b in table if b), 'of', len(seen), 'things on screen; rings_on', struct.unpack('<H', g.read(hdr + rings.TSR_RINGS_ON, 2))[0])
