# award.py N: N XP as the game's award gives it: each member's sheet XP += N / its classes (a human: N)
import os, sys, struct
PLAYTEST = os.path.dirname(os.path.abspath(__file__))
n = int(sys.argv[1]); sys.argv = sys.argv[:1]
sys.path.insert(0, PLAYTEST)
__file__ = os.path.join(PLAYTEST, "live.py")
exec(open(__file__).read())
from dsloader import game as G, aging as A
for i in range(4):
    s = gd.sheet(i)
    k = 1 if s[0x18] == G.HUMAN else max(1, sum(1 for c in s[0x21:0x24] if c))
    at = A.sheet_address(gd, i)
    xp = struct.unpack("<I", g.read(at, 4))[0]
    g.write(at, struct.pack("<I", xp + n // k))
    print(gd.creature_name(i), xp, "->", xp + n // k)
