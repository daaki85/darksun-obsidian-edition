# kinds.py [CREATURE=KIND ...]: a creature record's monster kind (+16h: 0 people; 15 the shadow's, 13 the
# greater shadow's, 3 the babau's, 38-40 the Styr's, Djinn's and Tari's with the manual's monsters), then
# every creature 4-39 with a kind. Memory only: never save after (2026-11-09, logs/2026-11-09-group-4.md:
# the ambush's Guards made shadows to see the STR drain; the game's hit powers come with melee hits only).
import os, sys, struct
HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, 'live.py')).read())
from dsloader import game
cr = game.far_pointer(g, ds, game.CREATURES_PTR)
for a in sys.argv[1:]:
    c, k = map(int, a.split('='))
    g.write(cr + c * 0x3A + 0x16, struct.pack('<H', k))
for c in range(4, 40):
    rec = g.read(cr + c * 0x3A, 0x3A)
    k = struct.unpack_from('<H', rec, 0x16)[0]
    if k: print(c, rec[0x28:0x38].split(b'\0')[0].decode(), 'kind', k, 'HP', struct.unpack_from('<h', rec, 0)[0])
