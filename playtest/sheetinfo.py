# sheetinfo.py: each party member's name, classes, levels, race, kits and weapon specs (by name), status (0 New)
import os, sys; HERE = os.path.dirname(os.path.abspath(sys.argv[0]))
__file__ = os.path.join(HERE, 'live.py'); exec(open(__file__).read())
from dsloader import game, kitpages, specialize, kits
game.RULES_IN_FORCE = gd.rules if hasattr(gd, 'rules') else game.RULES_IN_FORCE
for m in range(4):
    rec = gd.creature(m)
    if len(rec) < game.CREATURE_SIZE or not rec[game.CREATURE_NAME]:
        continue
    s = gd.sheet(m)
    specs = [specialize.KINDS[k - 1] for k in game.spec_kinds(s) if k]
    print(m, gd.creature_name(m), 'classes', list(s[0x21:0x24]), 'levels', list(s[0x24:0x27]), 'race', s[0x18],
          'kits', kitpages.kit_names(s), 'specs', specs, 'status', rec[game.CREATURE_STATUS])
