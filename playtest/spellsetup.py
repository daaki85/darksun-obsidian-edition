# spellsetup.py [MEMBER=LEVEL ...] [hp=N] [SPELL ...]: memory only, never save after. Teaches each
# MEMBER the spells (the known byte at segment DS-B56h, 168h + member x 8Ah + spell), fills its
# wizard and priest slots (9 at every level, DS:4B08h / 4B11h + 1Eh x member), and sets each of its
# casting classes (a class whose magic mask has the wizard or priest bit, in any of the sheet's three
# places) to LEVEL. hp=N: every party member's HP and most.
# Default spells: the ones the 2026-11-08 test of the manual's spells cast.
# e.g. python3 spellsetup.py 0=9 2=9 hp=200
# Then it prints, for each member set, the pages the USE screen's LEVEL button will offer, by the
# game's own rule (88A94h -> 81664h): a spell level is offered when the member knows a spell of it
# (500:2F, 5DE88h), its classes give a slot there (500:52, 5E0ACh: the slots on resting, not those
# left) and it is no more than (caster level + 1) / 2, the caster level being 81B16h's for spell 0
# (wizard) or 69 (priest): the best level of a class sharing a sphere with that spell, by 508:25
# (5E7CFh). A HUMAN's later (dual) class counts 0 there, and gives no slots, unless its level is
# below the first class's: so a human's casting class in place 2 or 3 raised to or past the first
# class's level leaves LEVEL on 1 (2026-11-09, logs/2026-11-09-level-button.md). The tool warns of it.
# A spell outside all the caster's spheres (a fire cleric's Ironskin) is cast at level 0, counted
# as 1, by the game (5E25Ch): durations and charges ignore the level set here. Each such spell is
# named after the slots ("cast at level 0"): set a class whose sphere has it (2026-11-08).
import os, sys, struct
HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, 'live.py')).read())
from dsloader import game
try:
    from dsloader import launch
    gd.rules = game.rules_from_settings(launch.load_settings())  # (slots by AD&D's tables when on)
except Exception:
    pass
members, spells, hp = {}, [], None
for a in sys.argv[1:]:
    if a.startswith('hp='): hp = int(a[3:])
    elif '=' in a: m, v = a.split('='); members[int(m)] = int(v)
    else: spells.append(int(a))
spells = spells or [14, 21, 22, 24, 33, 48, 51, 53, 56, 73, 75, 78, 104, 105, 108, 117, 133, 134]
known = (ds - 0xB56) * 16 + 0x168
sheets = game.far_pointer(g, ds, game.SHEETS_PTR); creatures = game.far_pointer(g, ds, game.CREATURES_PTR)
def seg_dword(seg, off):
    return struct.unpack('<I', g.read((gd.load_seg + seg) * 16 + off, 4))[0]
def class_mask(cls):
    return seg_dword(game.CLASS_MAGIC_SEG, game.CLASS_MAGIC_OFF + 4 * cls) if 0 < cls < 32 else 0
for m in range(4):
    sheet = struct.unpack_from('<H', gd.creature(m), 4)[0]
    if m in members:
        for s in spells: g.write(known + m * 0x8A + s, b'\x01')
        for kind in ('Wizard', 'Priest'):
            g.write(ds * 16 + game.SLOTS_LEFT[kind] + m * game.SLOTS_STRIDE + 1, bytes([9] * 9))
        sh = gd.sheet(m)
        places = [n for n in range(3) if class_mask(sh[game.SHEET_CLASSES + n]) & 3]
        if not places:
            print(m, 'has no casting class: none raised (set one in the sheet, +21h..23h)')
        for n in places:
            g.write(sheets + sheet * game.SHEET_SIZE + game.SHEET_LEVELS + n, bytes([members[m]]))
    if hp:
        g.write(creatures + m * game.CREATURE_SIZE, struct.pack('<H', hp))
        g.write(sheets + sheet * game.SHEET_SIZE + game.SHEET_MAX_HP, struct.pack('<H', hp))
for m in members: print(m, gd.spell_slots(m))

def game_level(sh, cls):
    """508:25 (5E7CFh): the sheet's level in CLS; a human's later class 0 unless below the first's."""
    for n in range(3):
        if sh[game.SHEET_CLASSES + n] == cls:
            lv = sh[game.SHEET_LEVELS + n]
            if n and sh[game.SHEET_RACE] == game.HUMAN and lv >= sh[game.SHEET_LEVELS]:
                return 0
            return lv
    return 0
def level_pages(m, bit):
    """The spell levels the LEVEL button offers member M for magic BIT (81664h), and the cap."""
    sh = gd.sheet(m)
    spell = 0 if bit == 1 else 0x45
    smask = seg_dword(game.SPELL_SPHERES_SEG, game.SPELL_SPHERES_OFF + spell * game.SPELL_SPHERES_SIZE)
    best = 0
    for cls in range(1, 20):  # (81B16h; rangers' 7 less, as the game)
        if class_mask(cls) & smask:
            lv = game_level(sh, cls) - (7 if 13 <= cls <= 16 else 0)
            best = max(best, lv)
    cap = (best + 1) // 2
    kb = g.read(known + m * 0x8A, 0x8A)
    have = set()
    for s in range(0x8A):
        if kb[s] & 0xF:
            rec = g.read((gd.load_seg + game.SPELL_LEVELS_SEG) * 16 + game.SPELL_LEVELS_OFF + s * 7, 2)
            if rec[1] & bit: have.add(rec[0])
    pages = [lv for lv in sorted(have) if lv <= cap and gd.max_spell_slots(m, bit, lv)]
    return pages, cap, sorted(have)
for m in members:
    sh = gd.sheet(m)
    for kind, bit in game.MAGIC_KINDS:
        if not any(class_mask(sh[game.SHEET_CLASSES + n]) & bit for n in range(3)):
            continue
        pages, cap, have = level_pages(m, bit)
        print(f'{m} {kind}: LEVEL pages {pages or [1]} (known at {have}; up to {cap} by the caster level)')
    for n in range(1, 3):
        cls, lv = sh[game.SHEET_CLASSES + n], sh[game.SHEET_LEVELS + n]
        if sh[game.SHEET_RACE] == game.HUMAN and class_mask(cls) & 3 and lv >= sh[game.SHEET_LEVELS]:
            print(f'{m} WARNING: a human, its casting class in place {n + 1} at level {lv} >= the first'
                  f" class's {sh[game.SHEET_LEVELS]}: the game counts it 0 (no slots, LEVEL stays on 1)")

def sphere_level(m, s):
    """The level the game casts spell S at for member M (5E25Ch): its best class level whose class
    mask shares a sphere bit with the spell's, bits 0-1 (any wizard, any priest) left out; 0 if none."""
    if not 0 < s < game.PSIONIC_FIRST:
        return None
    spell = seg_dword(game.SPELL_SPHERES_SEG, game.SPELL_SPHERES_OFF + s * game.SPELL_SPHERES_SIZE)
    sh = gd.sheet(m)
    return max([sh[game.SHEET_LEVELS + n] for n in range(3) if sh[game.SHEET_CLASSES + n]
                and class_mask(sh[game.SHEET_CLASSES + n]) & spell & 0x1FFFFC]
               or [0])
for m in members:
    off = [s for s in spells if sphere_level(m, s) == 0]
    if off: print(m, 'cast at level 0 (not its spheres):', ', '.join(f'{s} {gd.spell_name(s)}' for s in off))
