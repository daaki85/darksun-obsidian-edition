# ghostwatch.py SECONDS: DSCLOG's GHOST_ON and its palette copy watched every 20 ms: each change of GHOST_ON, and how many samples had it 0.
import sys, struct, time
import os; PT = os.path.dirname(os.path.abspath(sys.argv[0])); sys.path.insert(0, PT); __file__ = os.path.join(PT, 'live.py')
exec(open(__file__).read())
from dsloader import ghost
mem = g.read(0, 0x110000)
hdr = next(i for i in range(0, 0x100000, 16) if mem[i:i+8] == b'DSCLOGva')
far = struct.unpack('<H', g.read(hdr + ghost.TSR_FAR_SEG, 2))[0] * 16  # (DAC: the far block's, since 2026-11-08)
t0 = time.time(); zeros = samples = 0; last = None; dacs = set()
while time.time() - t0 < float(sys.argv[1]):
    on, = struct.unpack('<H', g.read(hdr + ghost.TSR_GHOST_ON, 2))
    off, = struct.unpack('<H', g.read(hdr + ghost.TSR_DAC, 2))
    dacs.add(g.read(far + off, 768))
    samples += 1; zeros += on == 0
    if on != last: print('%.1f s GHOST_ON %d' % (time.time() - t0, on), flush=True); last = on
    time.sleep(0.02)
print('samples', samples, 'with GHOST_ON 0:', zeros, 'palettes seen', len(dacs))
