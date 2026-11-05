# ghostchk.py [THING...]: DSCLOG's see-through figures: its block (GHOST_SEG), GHOST_ON, the first
# REP and BLEND bytes and GHOST_TAB; with THINGs, those marked see-through (GHOST_TAB) and the view
# drawn again. Memory only (the Loader writes the table again when the game's effects change).
import os, sys, struct; HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, 'live.py')).read())
mem = g.read(0, 0x110000)
hdr = next(i for i in range(0, len(mem), 16) if mem[i:i + 8] == b'DSCLOGva')
seg, on = struct.unpack('<HH', g.read(hdr + 1826, 4))
print('ghost_seg %04X on %d' % (seg, on))
if seg:
    print('rep', g.read(seg * 16 + 8192, 32).hex(), 'blend row0', g.read(seg * 16, 16).hex())
    print('tab', g.read(seg * 16 + 8192 + 256, 8).hex())
    if len(sys.argv) > 1:
        bits = bytearray(65)
        for t in map(int, sys.argv[1:]): bits[t // 8] |= 1 << t % 8
        g.write(seg * 16 + 8192 + 256, bytes(bits))
        g.write(hdr + 242, struct.pack('<H', 1))
        print('marked', sys.argv[1:])
