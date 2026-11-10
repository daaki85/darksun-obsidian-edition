# effects.py: every active effect (owner, caster, effect id), its charges and game seconds left
# (60 a round), as the Loader reads them. effects.py OWNER FROM TO [SPELL]: rewrite OWNER's effect
# FROM into TO (e.g. a Stuck, 51, into Paralyzed 34 or Slowed 47, to test a cure): memory only.
import os, sys, struct
HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, 'live.py')).read())
from dsloader import game
if len(sys.argv) > 3:
    owner, old, new = map(int, sys.argv[1:4])
    base = (gd.load_seg + game.EFFECTS_SEG) * 16 + game.EFFECTS_OFF
    for i in range(gd._word(game.EFFECT_COUNT)):
        rec = g.read(base + i * 10, 10)
        if struct.unpack_from('<h', rec)[0] == owner and rec[6] == old:
            if len(sys.argv) > 4: g.write(base + i * 10 + 4, struct.pack('<h', int(sys.argv[4])))
            g.write(base + i * 10 + 6, bytes([new])); print('changed', rec.hex()); break
for e, charges, secs in gd.effects_left():
    print(e, 'charges', charges, 'secs', secs, '|', game.effect_text(e, charges, secs))
