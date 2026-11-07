# markmember.py THING|none CHANGED: GHOST_TAB with only THING marked see-through (or none), and
# GH_CHANGED set to CHANGED (1: DSCLOG's GHOST_UNION draws the whole view at the next step). Memory only.
import os, sys, struct; HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, 'live.py')).read())
mem = g.read(0, 0x110000)
hdr = next(i for i in range(0, len(mem), 16) if mem[i:i + 8] == b'DSCLOGva')
seg = struct.unpack('<H', g.read(hdr + 1826, 2))[0]
bits = bytearray(65)
if sys.argv[1] != 'none':
    t = int(sys.argv[1]); bits[t // 8] |= 1 << t % 8
g.write(seg * 16 + 8192 + 256, bytes(bits))
g.write(seg * 16 + 8192 + 256 + 79, bytes((int(sys.argv[2]),)))
print('marked', sys.argv[1], 'changed', sys.argv[2])
