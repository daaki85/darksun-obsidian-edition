# memaudit.py: DOS memory now: the chain from the game's block (each block, owner, size), the upper memory chain from
# 9FFFh (DSCLOG, the overlay buffer, the see-through tables, the music buffer, free), the game's heap and DSCLOG's header figures.
# memaudit.py: DOS's memory chain from the first MCB DOSBox makes (scanned for), every block's owner and size;
# the game's heap; the HMA (DSCLOG's far block); DSCLOG's header figures; the map's flag.
import sys, struct
import os; PT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, PT); __file__ = os.path.join(PT, 'live.py')
exec(open(__file__).read())
from dsloader import heapcheck
mem = g.read(0, 0x110000)
ls = gd.load_seg
hdr = next(i for i in range(0, 0x100000, 16) if mem[i:i+8] == b'DSCLOGva')
dseg = hdr // 16
def w(a): return struct.unpack_from('<H', mem, a)[0]
# first MCB: DOS's list of lists is at the segment in INT 21h... find by walking from a low MCB:
first = None
game_mcb = ls - 0x11
for seg in range(0x40, game_mcb + 1):
    if mem[seg*16] != 0x4D: continue
    s = seg
    for _ in range(64):
        if s == game_mcb: first = seg; break
        if mem[s*16] not in (0x4D, 0x5A) or s > game_mcb: break
        s += w(s*16+3) + 1
    if first is not None: break
print('load segment %04X, DS %04X, DSCLOG header at %05X (segment %04X)' % (ls, gd.ds, hdr, dseg))
print('map open flag', w(gd.ds*16 + heapcheck.MAP_OPEN))
s = first; rows = []
while True:
    sig, owner, size = mem[s*16], w(s*16+1), w(s*16+3)
    name = mem[s*16+8:s*16+16].split(b'\0')[0].decode('latin1', 'replace')
    rows.append((s, sig, owner, size, name))
    if sig == 0x5A: break
    s += size + 1
tot_free_conv = 0
for s, sig, owner, size, name in rows:
    who = 'free' if owner == 0 else ('DOS' if owner == 8 else '%04X' % owner)
    region = 'UMB' if s >= 0xA000 else 'conv'
    print('  MCB %04X %s %-6s owner %-5s %6d bytes  %s' % (s, chr(sig), region, who, size*16, name))
m = heapcheck.sample(g.read, ls)
print('heap:', heapcheck.describe(m) if m else None)
# DSCLOG header values
hv = lambda off: w(hdr + off)
print('DSCLOG: far_seg %04X ring_seg %04X ovr_given %04X umb_need %d paras ghost_seg %04X ghost_on %d' % (
    hv(142), hv(268), hv(368), hv(372), hv(1826), hv(1828)))
print('HMA test: FFFF:0010 vs 0:0 differ:', g.read(0xFFFF*16+0x10, 16) != g.read(0, 16))
print('upper memory chain:')
for start in (0x9FFF, 0xC900, 0xD000):
    if mem[start*16] in (0x4D, 0x5A):
        s = start
        for _ in range(64):
            sig, owner, size = mem[s*16], w(s*16+1), w(s*16+3)
            if sig not in (0x4D, 0x5A): print('  (broken at %04X)' % s); break
            name = mem[s*16+8:s*16+16].split(b'\0')[0].decode('latin1', 'replace')
            who = 'free' if owner == 0 else ('DOS' if owner == 8 else '%04X' % owner)
            print('  MCB %04X %s owner %-5s %6d bytes (%5d paras)  %s' % (s, chr(sig), who, size*16, size, name))
            if sig == 0x5A: break
            s += size + 1
        break
