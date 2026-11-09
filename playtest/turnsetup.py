# turnsetup.py MEMBER LEVEL [COMBATANT=HD ...]: memory only, never save after (2026-11-09). Makes party
# member MEMBER a fire cleric of LEVEL (its sheet's second class, +22h, 3; +25h the level; +12h OR 4,
# the cleric element the TURN UNDEAD button shows for), and each COMBATANT's creature undead (its
# sheet's race +18h 9) of HD hit dice (+24h). Creatures of a kind share a sheet: all of them change.
# Prints each combatant on the map with its creature, sheet, race and HD.
# e.g. python3 turnsetup.py 3 4 25=1
import os, sys, struct
HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, 'live.py')).read())
from dsloader import game
sheets = game.far_pointer(g, ds, game.SHEETS_PTR)
def sheet_at(creature):
    return sheets + struct.unpack_from('<H', gd.creature(creature), 4)[0] * game.SHEET_SIZE
member, level = int(sys.argv[1]), int(sys.argv[2])
at = sheet_at(member)
g.write(at + game.SHEET_CLASSES + 1, bytes([3]))
g.write(at + game.SHEET_LEVELS + 1, bytes([level]))
flags = struct.unpack('<H', g.read(at + game.SHEET_FLAGS, 2))[0] | 4
g.write(at + game.SHEET_FLAGS, struct.pack('<H', flags))
combatants = gd.combatants()
for arg in sys.argv[3:]:
    c, hd = (int(x) for x in arg.split('='))
    s = sheet_at(combatants[c])
    g.write(s + game.SHEET_RACE, bytes([9]))
    g.write(s + game.SHEET_LEVELS, bytes([hd]))
sh = g.read(at, game.SHEET_SIZE)
print(f"member {member}: classes {list(sh[0x21:0x24])} levels {list(sh[0x24:0x27])} flags {flags:04x}")
for c, creature in sorted(combatants.items()):
    s = g.read(sheet_at(creature), game.SHEET_SIZE)
    hp = struct.unpack_from('<h', gd.creature(creature), 0)[0]
    print(f"  combatant {c}: creature {creature} {gd.creature_name(creature)}, sheet "
          f"{struct.unpack_from('<H', gd.creature(creature), 4)[0]}, race {s[0x18]}, HD {s[0x24]}, HP {hp}")
