# pastblock.py save|cmp FILE: the 4 KB past GHOST's block (GHOST_SEG + 885 paragraphs), kept or compared
import os, sys, struct
PT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, PT)
exec(open(os.path.join(PT, 'live.py')).read())
mem = g.read(0xC0000, 0x30000)
hdr = 0xC0000 + next(i for i in range(0, len(mem), 16) if mem[i:i + 8] == b'DSCLOGva')
seg, = struct.unpack('<H', g.read(hdr + 1826, 2))
end = (seg + 885) * 16
now = g.read(end, 4096)
if sys.argv[1] == 'save':
    open(sys.argv[2], 'wb').write(now); print('kept 4096 bytes at %X' % end)
else:
    old = open(sys.argv[2], 'rb').read()
    diff = [i for i in range(4096) if old[i] != now[i]]
    print('at %X: %d bytes changed' % (end, len(diff)), [hex(end + i) for i in diff[:8]])
