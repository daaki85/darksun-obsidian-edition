# hp.py HP: every combatant past the party (index 4 and up) to HP hit points, its sheet's most too.
# hp.py 1 before finishing a fight with real attacks (fightout.sh); a high number keeps a test fight
# alive. The arena's tied-up prisoners are combatants too, and are left as they are.
import sys, os, struct
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'live.py')).read())
hp = int(sys.argv[1]); far = game.far_pointer(g, ds, game.SHEETS_PTR)
cbase = game.far_pointer(g, ds, game.CREATURES_PTR)
for index in sorted(set(gd.combatants().values())):
    if index < game.PARTY_SIZE or 'Prisoner' in gd.creature_name(index): continue  # (story people)
    cr = gd.creature(index); sheetno = struct.unpack_from('<H', cr, 4)[0]
    g.write(cbase + index * game.CREATURE_SIZE, struct.pack('<H', hp))
    g.write(far + sheetno * game.SHEET_SIZE + game.SHEET_MAX_HP, struct.pack('<H', hp))
    print(index, gd.creature_name(index), hp)
