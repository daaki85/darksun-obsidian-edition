# ravsites.py [NAME...]: where Shattered Lands' patch sites (dsloader.gamepatch.PATCHES) are in Wake of the
# Ravager's DSUN.EXE, by likeness: SL's 64 bytes round each site (the patch's own bytes left out) scored
# against every place in WotR's (bytes alike), and the best place taken when the patch's original bytes are
# there, it scores at least 60%, and the next best is clearly behind (5 bytes). Prints, for each patch: the
# WotR offset or why none ("no likeness", "unclear", "other bytes" with what is there), and DONE for one
# already in dsloader.ravager.PATCHES. Without names, every patch. Its finds are leads, each read by hand
# before it goes into ravager.PATCHES (logs/2026-11-20-ravager-fixes-step4.md).
import os, sys
import numpy as np
PT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(PT, '..', 'obsidian-edition'))
from dsloader import gamepatch, ravager
sl = open(os.path.join(os.environ.get('DS_GAME', '/tmp/playtest/inst'), 'DSUN.EXE'), 'rb').read()
rv = open(os.path.join(os.environ.get('RAV', '/tmp/playtest/rav'), 'DSUN.EXE'), 'rb').read()
RV = np.frombuffer(rv, np.uint8); W = 64
done = {p.name for p in ravager.PATCHES}
names = set(sys.argv[1:])


def find(p):
    n = len(p.original); a = p.offset - (W - n) // 2
    win = np.frombuffer(sl[a:a + W], np.uint8); N = len(RV) - W
    eq = np.zeros(N + 1, np.int16)
    for k in range(W):
        if not p.offset - a <= k < p.offset - a + n:
            eq += (RV[k:k + N + 1] == win[k])
    b = int(eq.argmax()); s = int(eq[b]); eq[max(0, b - 8):b + 8] = 0; nxt = int(eq.max())
    at = b + (p.offset - a)
    if s < 0.6 * (W - n):
        return None, f"no likeness ({s}/{W - n})"
    if s - nxt < 5:
        return None, f"unclear ({s} vs {nxt}, best {at:#x})"
    if rv[at:at + n] != p.original:
        return None, f"other bytes at {at:#x} ({s}/{W - n}): {rv[at:at + n].hex()} for {p.original.hex()}"
    return at, f"{at:#x} ({s}/{W - n})"


for p in gamepatch.PATCHES:
    if (names and p.name not in names) or p.offset >= len(sl):
        continue
    at, why = find(p)
    kind = 'probe' if p.replacement[:1] == b'\xcd' else 'bytes'
    print(f"{p.name:28} {kind:5} SL {p.offset:#07x}  {why}{'  DONE' if p.name in done else ''}", flush=True)
