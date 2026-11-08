# spellsetup.py [MEMBER=LEVEL ...] [hp=N] [SPELL ...]: memory only, never save after. Teaches each
# MEMBER the spells (the known byte at segment DS-B56h, 168h + member x 8Ah + spell), fills its
# wizard and priest slots (9 at every level, DS:4B08h / 4B11h + 1Eh x member), and sets its class
# in the sheet's second place (+level index 1) to LEVEL. hp=N: every party member's HP and most.
# Default spells: the ones the 2026-11-08 test of the manual's spells cast.
# e.g. python3 spellsetup.py 0=9 2=9 hp=200
# A spell outside all the caster's spheres (a fire cleric's Ironskin) is cast at level 0, counted
# as 1, by the game (5E25Ch): durations and charges ignore the level set here. Each such spell is
# named after the slots ("cast at level 0"): set a class whose sphere has it (2026-11-08).
import os, sys, struct
HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, 'live.py')).read())
from dsloader import game
members, spells, hp = {}, [], None
for a in sys.argv[1:]:
    if a.startswith('hp='): hp = int(a[3:])
    elif '=' in a: m, v = a.split('='); members[int(m)] = int(v)
    else: spells.append(int(a))
spells = spells or [14, 21, 22, 24, 33, 48, 51, 53, 56, 73, 75, 78, 104, 105, 108, 117, 133, 134]
known = (ds - 0xB56) * 16 + 0x168
sheets = game.far_pointer(g, ds, game.SHEETS_PTR); creatures = game.far_pointer(g, ds, game.CREATURES_PTR)
for m in range(4):
    sheet = struct.unpack_from('<H', gd.creature(m), 4)[0]
    if m in members:
        for s in spells: g.write(known + m * 0x8A + s, b'\x01')
        for kind in ('Wizard', 'Priest'):
            g.write(ds * 16 + game.SLOTS_LEFT[kind] + m * game.SLOTS_STRIDE + 1, bytes([9] * 9))
        g.write(sheets + sheet * game.SHEET_SIZE + game.SHEET_LEVELS + 1, bytes([members[m]]))
    if hp:
        g.write(creatures + m * game.CREATURE_SIZE, struct.pack('<H', hp))
        g.write(sheets + sheet * game.SHEET_SIZE + game.SHEET_MAX_HP, struct.pack('<H', hp))
for m in members: print(m, gd.spell_slots(m))
def sphere_level(m, s):
    """The level the game casts spell S at for member M (5E25Ch): its best class level whose class
    mask shares a sphere bit with the spell's, bits 0-1 (any wizard, any priest) left out; 0 if none."""
    if not 0 < s < game.PSIONIC_FIRST:
        return None
    mask = lambda seg, off: struct.unpack('<I', g.read((gd.load_seg + seg) * 16 + off, 4))[0]
    spell = mask(game.SPELL_SPHERES_SEG, game.SPELL_SPHERES_OFF + s * game.SPELL_SPHERES_SIZE)
    sh = gd.sheet(m)
    return max([sh[game.SHEET_LEVELS + n] for n in range(3) if sh[game.SHEET_CLASSES + n]
                and mask(game.CLASS_MAGIC_SEG, game.CLASS_MAGIC_OFF + 4 * sh[game.SHEET_CLASSES + n]) & spell & 0x1FFFFC]
               or [0])
for m in members:
    off = [s for s in spells if sphere_level(m, s) == 0]
    if off: print(m, 'cast at level 0 (not its spheres):', ', '.join(f'{s} {gd.spell_name(s)}' for s in off))
