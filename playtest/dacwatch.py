# dacwatch.py SECONDS: DSCLOG's copy of the palette (TSR_DAC) watched: each change, hashed whole and for colours 16-223 only.
import sys, struct, time, hashlib
import os; PT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, PT); __file__ = os.path.join(PT, 'live.py')
exec(open(__file__).read())
from dsloader import ghost, shadows
mem = g.read(0, 0x110000)
hdr = next(i for i in range(0, 0x100000, 16) if mem[i:i+8] == b'DSCLOGva')
base = hdr - struct.unpack('<H', g.read(hdr + ghost.TSR_HDR_OFF, 2))[0]
seen = []
t0 = time.time()
while time.time() - t0 < float(sys.argv[1]):
    off, = struct.unpack('<H', g.read(hdr + ghost.TSR_DAC, 2))
    dac = g.read(base + off, 768)
    h = hashlib.md5(dac).hexdigest()[:8]; h2 = hashlib.md5(dac[48:672]).hexdigest()[:8]
    if not seen or seen[-1][1] != h:
        seen.append((round(time.time()-t0), h, h2)); print(seen[-1], flush=True)
    time.sleep(1)
print('distinct whole', len({s[1] for s in seen}), 'distinct 16-223', len({s[2] for s in seen}))
