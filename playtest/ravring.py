# ravring.py OUT SECONDS [PID]: follows Wake of the Ravager's helper (DSCLOG2, header "DSCLOGR1") and appends
# every new ring entry (192 bytes, DSCLOG's ENTRY LAYOUT) to OUT as a hex line, polling 5 times a second,
# for SECONDS. For collecting the sequel's rolls (a fight, a rest) to label them (dsloader/ravlog.py).
import sys, os, time, re, struct, argparse
PT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(PT, '..', 'obsidian-edition'))
from dsloader.__main__ import connect
WORK = os.environ.get('PLAYTEST_WORK', '/tmp/playtest')
out, secs = sys.argv[1], float(sys.argv[2])
pid = int(sys.argv[3]) if len(sys.argv) > 3 else int(open(os.path.join(WORK, 'rav.pid')).read())
g = connect(argparse.Namespace(pid=pid, host_base=None))
low = g.read(0, 0x110000)
h = next(x.start() for x in re.finditer(b'DSCLOGR1', low) if x.start() % 16 == 0)
nent, esize, ring_off = struct.unpack_from('<3H', low, h + 12)
last, n, end = struct.unpack_from('<H', low, h + 8)[0], 0, time.time() + secs
with open(out, 'a') as f:
    while time.time() < end:
        seq = struct.unpack('<H', g.read(h + 8, 2))[0]
        far = struct.unpack('<H', g.read(h + 142, 2))[0]
        if seq != last:
            ring = g.read(far * 16 + ring_off, nent * esize)
            got = sorted((struct.unpack_from('<H', ring, i * esize)[0], i) for i in range(nent))
            for s, i in got:
                if 0 < (s - last) & 0xFFFF <= nent:
                    f.write(ring[i * esize:(i + 1) * esize].hex() + '\n'); n += 1
            if (seq - last) & 0xFFFF > nent: print('lost', ((seq - last) & 0xFFFF) - nent, 'entries', flush=True)
            last = seq
        time.sleep(0.2)
print('entries', n)
