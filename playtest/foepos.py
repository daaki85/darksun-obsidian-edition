# foepos.py: each combatant past the party: its name, HP and figure on screen (feet x, y - 10)
import os, sys, struct
PT=os.path.dirname(os.path.abspath(sys.argv[0])); sys.path.insert(0, PT)
__file__=os.path.join(PT,'live.py'); exec(open(__file__).read())
from dsloader import game
cx, cy = struct.unpack('<hh', g.read(ds * 16 + CAMERA, 4))
for n in range(4, 60):
    c = gd.combatant_creature(n)
    if c is None: continue
    rec = gd.creature(c)
    if len(rec) < game.CREATURE_SIZE: continue
    hp = struct.unpack_from('<h', rec, 0)[0]
    x, y = struct.unpack('<HH', g.read(ds * 16 + game.POSITIONS + n * 32, 4))
    if hp > 0: print(n, gd.creature_name(c), hp, x - cx, y - cy - 10)
