# poolfree.py [SECONDS]: the game's picture memory (the blocks at DS:8E94h, 8 bytes each: +0 the
# bytes free in it (dword), +4 its far pointer; DS:1F74h the last block's number), the free bytes
# in each and in all, with the picture slots in memory (cachelist.py's count); every second for
# SECONDS. A picture the game can't read back from its store (25D6Ah) keeps the block it took for
# it: the free bytes then fall with each drawing of it (2026-11-09, logs/2026-11-09-missing-figures.md).
import os, sys, struct, time
PT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, PT)
exec(open(os.path.join(PT, 'live.py')).read())
secs = float(sys.argv[1]) if len(sys.argv) > 1 else 0
end = time.time() + secs
while True:
    last = struct.unpack('<H', g.read(ds * 16 + 0x1F74, 2))[0]
    blocks = [struct.unpack('<I', g.read(ds * 16 + 0x8E94 + k * 8, 4))[0] for k in range(min(last + 1, 64))]
    n = struct.unpack('<H', g.read(ds * 16 + 0x1F84, 2))[0]
    tab = g.read((gd.load_seg + 0x3E60) * 16, n * 16)
    inmem = sum(1 for k in range(n) if tab[k * 16 + 0x0E] & 2)
    print(time.strftime('%T'), 'free', sum(blocks), 'blocks', blocks, 'in memory', inmem, flush=True)
    if time.time() >= end: break
    time.sleep(1)
