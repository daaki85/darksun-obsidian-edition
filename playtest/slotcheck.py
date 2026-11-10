# slotcheck.py [LABEL]: every map thing with a picture slot (+0Fh) finds its own picture's number in
# that slot (+18h, the walking picture, or +18h + 1 for its fighting one), and every wall's slot is
# taken: the check that reusing slots (DSCLOG's PIC_REUSE) never left a thing pointing at another's
# picture (2026-11-09, logs/2026-11-09-picture-slot-reuse.md).
import os, sys, struct
PT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, PT)
exec(open(os.path.join(PT, 'live.py')).read())
n = struct.unpack('<H', g.read(ds * 16 + 0x1F84, 2))[0]
tab = g.read((gd.load_seg + 0x3E60) * 16, 300 * 16)
num = [struct.unpack_from('<H', tab, k * 16)[0] for k in range(300)]
bad, ok = [], 0
for t in range(520):
    e = g.read(ds * 16 + 0x6694 + t * 32, 32)
    slot = struct.unpack_from('<H', e, 0x0F)[0]
    pic = struct.unpack_from('<H', e, 0x18)[0]
    if slot >= 300 or not pic:  # (FFFFh none; past 300 an unused entry's old bytes)
        continue
    if slot >= n or num[slot] not in (pic, pic + 1):
        bad.append((t, pic, slot, num[slot] if slot < 300 else None))
    else:
        ok += 1
walls = [struct.unpack('<H', g.read(ds * 16 + 0x574E + 4 * i, 2))[0] for i in range(31)]
wbad = [(i, s) for i, s in enumerate(walls) if s != 0xFFFF and (s >= n or num[s] in (0xFFFE, 0xFFFF))]
print(f'{sys.argv[1] if len(sys.argv) > 1 else ""}: things with their own picture {ok}, wrong {bad[:10]}{"..." if len(bad) > 10 else ""} ({len(bad)}); walls wrong {wbad}')
