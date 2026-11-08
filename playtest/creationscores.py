# creationscores.py: the creation screen's scores, classes and race, and the least and most the game last worked out
import os, sys, struct
PLAYTEST = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PLAYTEST)
__file__ = os.path.join(PLAYTEST, "live.py")
exec(open(__file__).read())
from dsloader import game as G
rec = G.far_pointer(g, ds, 0x11A0)
sheet = G.far_pointer(g, ds, 0x119C)
print("scores", list(g.read(rec + 0x22, 6)), "classes", list(g.read(sheet + 0x21, 3)), "race", g.read(sheet + 0x18, 1)[0],
      "least", struct.unpack("<h", g.read(ds * 16 + 0x4994, 2))[0], "most", struct.unpack("<h", g.read(ds * 16 + 0x4992, 2))[0])
