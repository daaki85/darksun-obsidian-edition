# dosmem.py [PID]: DOS memory in any running DOSBox, no helper needed (so either game, modded or not,
# or Wake of the Ravager): every block of the conventional chain and the upper memory chain (owner's
# name, size), the largest free piece of each, the program's Borland far heap (first/last/rover at its
# load segment + 0FE7h in Shattered Lands, + 135Bh in Wake of the Ravager) and DOS memory free after it, and the HMA.
import sys, os, struct, argparse
PT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(PT, '..', 'obsidian-edition'))
from dsloader.__main__ import connect
from dsloader.process import find_dosbox_processes
from dsloader import heapcheck
pid = int(sys.argv[1]) if len(sys.argv) > 1 else max(p for p, _ in find_dosbox_processes())
g = connect(argparse.Namespace(pid=pid, host_base=None))
mem = g.read(0, 0x110000)
w = lambda a: struct.unpack_from('<H', mem, a)[0]
def chain(start):
    rows, s = [], start
    for _ in range(200):
        if mem[s*16] not in (0x4D, 0x5A): rows.append((s, None, 0, 0, '(broken)')); break
        sig, owner, size = mem[s*16], w(s*16+1), w(s*16+3)
        rows.append((s, chr(sig), owner, size, mem[s*16+8:s*16+16].split(b'\0')[0].decode('latin1', 'replace')))
        if sig == 0x5A: break
        s += size + 1
    return rows
# the first MCB: DOS's list of lists (INT 21h AH=52h) isn't reachable from here; take the lowest
# segment whose chain walks, link by link, to its 'Z' (upper memory, when DOS hasn't linked it, has its own chain from 9FFFh)
first = next(s for s in range(0x40, 0x2000) if mem[s*16] == 0x4D and len(chain(s)) > 3 and chain(s)[-1][1] == 'Z')
names = {}
def show(rows, title):
    print(title)
    free = []
    for s, sig, owner, size, name in rows:
        if sig is None: print('  (broken at %04X)' % s); break
        if owner > 8: names.setdefault(owner, mem[(owner-1)*16+8:(owner-1)*16+16].split(b'\0')[0].decode('latin1', 'replace'))
        who = 'free' if owner == 0 else 'DOS' if owner == 8 else '%04X %s' % (owner, names.get(owner, ''))
        print('  MCB %04X %s %7d bytes (%5d paras)  owner %-14s %s' % (s, sig, size*16, size, who, name))
        if owner == 0: free.append(size*16)
    print('  free: %d bytes in %d pieces, the largest %d' % (sum(free), len(free), max(free, default=0)))
conv = chain(first)
show(conv, 'conventional memory, from MCB %04X:' % first)
if mem[0x9FFF*16] in (0x4D, 0x5A):
    show(chain(0x9FFF), 'upper memory, from MCB 9FFF:')
# the program: the biggest block owned by a PSP whose MCB name isn't COMMAND
prog = max((r for r in conv if r[2] > 8 and r[4] not in ('COMMAND', 'SC', 'SD')), key=lambda r: r[3])
ls = prog[2] + 0x10
print('the program: %s, PSP %04X, load segment %04X, its block %d bytes' % (prog[4], prog[2], ls, prog[3]*16))
m = None
for at in (0x0FE7, 0x135B):  # (Shattered Lands' runtime, Wake of the Ravager's)
    heapcheck.HEAP_VARS = at
    m = heapcheck.sample(g.read, ls)
    if m: break
print('its far heap (load + %04Xh):' % at, heapcheck.describe(m) if m else 'not found at load + 0FE7h or 135Bh')
print('HMA (FFFF:0010 not a mirror of 0:0, A20 on):', g.read(0xFFFF*16+0x10, 16) != g.read(0, 16))
