# sheetbyte.py MEMBER OFFSET [VALUE|orVALUE]: party member MEMBER's character sheet byte at OFFSET read,
# or set (orVALUE ORs bits in), with its three classes printed. For a test or a picture: +45h's 40h
# knows Fogbolt (game.NEW_KNOWN), +22h a second class (5 an air druid, who casts Whirlwind), +18h the
# race. Memory only: never save after (logs/2026-11-27-outfit-screenshots.md).
import os, sys, struct
HERE = os.path.dirname(os.path.abspath(__file__))
args = sys.argv[1:]; sys.argv = sys.argv[:1]
exec(open(os.path.join(HERE, 'live.py')).read())
from dsloader import game
m, off = int(args[0]), int(args[1], 0)
rec = gd.creature(m)
at = game.far_pointer(g, ds, 0x1661) + struct.unpack_from('<H', rec, 4)[0] * game.SHEET_SIZE
old = g.read(at + off, 1)[0]
if len(args) > 2:
    v = args[2]
    g.write(at + off, bytes([old | int(v[2:], 0) if v.startswith('or') else int(v, 0)]))
print(m, hex(off), old, '->', g.read(at + off, 1)[0], 'classes', list(g.read(at + game.SHEET_CLASSES, 3)))
