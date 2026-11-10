"""setcount.py [N]: read (and with N, write) the arena's visit count, the game's number 12 (4: the next
trip is Scar's). In the pens; in the arena the numbers often have no place in memory (it read 4 there once the bout was over, 2026-11-10)."""
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
__file__ = os.path.join(HERE, "live.py")
exec(open(__file__).read())
from dsloader.game import NUMBERS_PTR, far_pointer  # noqa: E402

at = far_pointer(g, ds, NUMBERS_PTR)
if not at:
    sys.exit("the numbers have no place in memory here (the arena?)")
if len(sys.argv) > 1:
    g.write(at + 2 * 12, struct.pack("<h", int(sys.argv[1])))
print("arena count", gd.number(12))
