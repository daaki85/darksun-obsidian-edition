# addeffect.py OWNER EFFECT [SPELL] [CHARGES]: give combatant OWNER (0-3 the party) the effect EFFECT
# (35 Poisoned, 13 Diseased, 34 Paralyzed...) in memory, untimed: a 10-byte record put into the game's
# effect table (load segment + 3BF6h:0106h, DS:1E24h the count) where the game keeps it, in rising
# owner order (76A99h finds an owner's first record by a binary search on +0), after the owner's
# other records. +0 owner, +2 caster (the owner), +4 the spell (default 0), +6 the effect, +7 the
# handle (0: no timer in the event queue), +8 charges. Memory only: never save after.
# addeffect.py del OWNER EFFECT takes every such record out again.
import os, sys, struct
HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, 'live.py')).read())
from dsloader import game
base = (gd.load_seg + game.EFFECTS_SEG) * 16 + game.EFFECTS_OFF
count = gd._word(game.EFFECT_COUNT)
recs = [g.read(base + i * 10, 10) for i in range(count)]
if sys.argv[1] == 'del':
    owner, eff = int(sys.argv[2]), int(sys.argv[3])
    keep = [r for r in recs if not (struct.unpack_from('<h', r)[0] == owner and r[6] == eff)]
    g.write(base, b''.join(keep) + bytes(10 * (count - len(keep))))
    g.write(ds * 16 + game.EFFECT_COUNT, struct.pack('<H', len(keep)))
    print('removed', count - len(keep))
else:
    owner, eff = int(sys.argv[1]), int(sys.argv[2])
    spell = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    charges = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    at = 0
    while at < count and struct.unpack_from('<h', recs[at])[0] <= owner:
        at += 1
    rec = struct.pack('<hhhBBBB', owner, owner, spell, eff, 0, charges, 0)
    recs.insert(at, rec)
    g.write(base, b''.join(recs))
    g.write(ds * 16 + game.EFFECT_COUNT, struct.pack('<H', count + 1))
    print('added at', at, rec.hex())
for e, charges, secs in gd.effects_left():
    print(e, 'charges', charges, 'secs', secs, '|', game.effect_text(e, charges, secs))
