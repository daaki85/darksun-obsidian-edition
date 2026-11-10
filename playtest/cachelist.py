# cachelist.py [all]: the game's picture cache (the table at load segment + 3E60h, 16 bytes a slot:
# +0 the picture's number, FFFEh one the Loader took out (sprites.STALE), +2 its length, +6 its place
# (negative: none), +0Ah its far pointer, +0Eh flags, 2 in memory) and how many slots are taken
# (DS:1F84h; at most 300 (12Ch): the game's loader, 25FA6h, then gives no slot, and a thing it
# can't give one to isn't drawn). Prints the count, the STALE ones, and with "all" every slot.
import os, sys, struct
PT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, PT)
exec(open(os.path.join(PT, 'live.py')).read())
n = struct.unpack('<H', g.read(ds * 16 + 0x1F84, 2))[0]
tab = g.read((gd.load_seg + 0x3E60) * 16, 300 * 16)
ents = [struct.unpack_from('<HIiIBB', tab, k * 16)[:6] for k in range(min(n, 300))]
stale = [k for k, e in enumerate(ents) if e[0] == 0xFFFE]
inmem = sum(1 for e in ents if e[4] & 2)
print(f'slots taken {n} of 300; in memory {inmem}; stale (FFFEh) {len(stale)}: {stale[:40]}')
if sys.argv[1:] == ['all']:
    for k, e in enumerate(ents):
        print(k, e[0], e[1], e[2], f'{e[4]:02X}')
