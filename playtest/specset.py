# specset.py MEMBER KIND...: party member MEMBER's weapon specs made KIND... in memory (specialize.KINDS'
# names, "_" for a space: two_handed_sword; the first kept first, the V3 layout), its age and roll kept.
# Memory only: never save the game after.
import os, sys
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'live.py')).read())
from dsloader import specialize
m = int(sys.argv[1])
kinds = [specialize.KINDS.index(k.replace('_', ' ')) + 1 for k in sys.argv[2:]]
at = game.far_pointer(g, ds, game.SHEETS_PTR) + m * game.SHEET_SIZE  # (a party member's sheet: its number)
sheet = g.read(at, game.SHEET_SIZE)
print('before', [specialize.KINDS[k - 1] for k in game.spec_kinds(sheet) if k])
g.write(at + game.SPEC_SLOTS, game.packed_specs(kinds, game.sheet_age(sheet), game.sheet_roll(sheet)))
print('after', [specialize.KINDS[k - 1] for k in game.spec_kinds(g.read(at, game.SHEET_SIZE)) if k])
