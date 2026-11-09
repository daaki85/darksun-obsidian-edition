# setmem.py [hp=M:V psp=M:V status=M:V ruleshi=+N|-N power=M:P slots=M:L:N]: the party's HP, PSP and
# status (creature +0, +2, +1Ch), DSCLOG's rules_hi (the header's +270: +N sets bits, -N clears them;
# 2048 dual-classing, 4096 resting), a psionic power known (P from 138: 13 Cell Adjustment; its byte at
# selector 2F0h +77h + 22h x member, 8), a priest slot count (DS:4B11h + 1Eh x member + level); then
# each member's HP, PSP, status, STR, CON and priest slots. Memory only: never save after
# (2026-11-09, logs/2026-11-09-group-4.md).
import os, sys, struct
HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, 'live.py')).read())
from dsloader import game
cr = game.far_pointer(g, ds, game.CREATURES_PTR); sh = game.far_pointer(g, ds, game.SHEETS_PTR)
hdr = next(i for i in range(0xA0000, 0x100000, 16) if g.read(i, 8) == b'DSCLOGva')
def show():
    for m in range(4):
        rec = g.read(cr + m * 0x3A, 0x3A); s = g.read(sh + m * 0x47, 0x47)
        name = rec[0x28:0x38].split(b'\0')[0].decode()
        pri = list(g.read(ds * 16 + 0x4B11 + m * 0x1E, 8))
        print(f"#{m} {name:10} HP {struct.unpack_from('<h', rec, 0)[0]}/{struct.unpack_from('<h', s, 8)[0]} PSP {struct.unpack_from('<H', rec, 2)[0]} status {rec[0x1C]} STR {rec[0x22]} CON {rec[0x24]} priest slots {pri[1:7]}")
    print('rules_hi', struct.unpack('<H', g.read(hdr + 270, 2))[0])
for a in sys.argv[1:]:
    k, v = a.split('=') if '=' in a else (a, '')
    if k == 'hp':
        m, x = map(int, v.split(':')); g.write(cr + m * 0x3A, struct.pack('<h', x))
    elif k == 'psp':
        m, x = map(int, v.split(':')); g.write(cr + m * 0x3A + 2, struct.pack('<H', x))
    elif k == 'status':
        m, x = map(int, v.split(':')); g.write(cr + m * 0x3A + 0x1C, bytes((x,)))
    elif k == 'ruleshi':
        r = struct.unpack('<H', g.read(hdr + 270, 2))[0]
        n = int(v); r = (r | n) if n > 0 else (r & ~(-n))
        g.write(hdr + 270, struct.pack('<H', r))
    elif k == 'power':
        m, p = map(int, v.split(':'))
        seg, = struct.unpack('<H', g.read((gd.load_seg + game.SEGMENT_TABLE) * 16 + game.POWER_OWN_SELECTOR, 2))
        g.write(seg * 16 + 0x77 + m * 0x22 + p, bytes((8,)))
    elif k == 'slots':
        m, l, n = map(int, v.split(':')); g.write(ds * 16 + 0x4B11 + m * 0x1E + l, bytes((n,)))
show()
