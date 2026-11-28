"""The party's saving throws worked out again when a game is loaded (both games, RULE_ADND_TABLES).

The games keep a character's five saves in the sheet (game.SHEET_SAVES) and work them out only on the
creation screen and at a level up (SL's 877EBh, the sequel's 954D2h, with DSCLOG's and DSCLOG2's
SAVE_BASE giving the Player's Handbook's table). A save made while the numbers were wrong keeps them
until the next level: Wake of the Ravager's from 2026-11-27 to 2026-11-28, whose SAVE_BASE read its
table from the wrong segment (a new fighter's 81/2/235/0/208); a party made before the tables were
the Handbook's keeps the game's own. So, once each time a game is loaded, each party member's saves
are put as the game's routine would put them now, and the dice log says whose changed.

The routine, as both games have it: each save starts at 99; for each class group (0 priest, 1 warrior,
2 wizard, 3 rogue: tables.CLASS_GROUPS) at the best level of the character's classes in it (a human's
dual-class old class too: the routine asks for every class), the Handbook's save for that level (the
rogues: the better of a thief's at its thief level and a psionicist's, Dark Sun's table, at its
psionicist level: SAVE_BASE), less, for the warriors, a dwarf's or halfling's CON x 2 / 7 (2 at least:
SAVE_BASE's SAVE_LEAST; before 2026-11-28 a byte under 0, 254 for a dwarf fighter at 17th); the sheet
keeps the lowest, compared as the game does (the sheet's byte unsigned against the new number signed,
the new number put as a byte)."""

from typing import List, Optional, Sequence, Tuple

from . import game, tables

SAVE_NAMES = ("PPD", "RSW", "PP", "BW", "SP")
START = 99  # (the routine's first value of each save: 63h)
LEAST = 2  # (SAVE_BASE's SAVE_LEAST: no save under it, a dwarf's or halfling's CON bonus taken off)
WARRIORS = 1


def group_levels(classes: Sequence[int], levels: Sequence[int]) -> List[int]:
    """Each class group's level (0 none): the best of the character's classes in it (953A9h, SL's 876C3h)."""
    out = [0, 0, 0, 0]
    for cls, level in zip(classes, levels):
        group = tables.CLASS_GROUPS.get(cls)
        if group is not None and level > out[group]:
            out[group] = level
    return out


def rogue_saves(classes: Sequence[int], levels: Sequence[int], group_level: int) -> Tuple[int, ...]:
    """SAVE_BASE's rogues: the better of the thief's save at its thief level and the psionicist's at its
    psionicist level; with neither (it can't be) the group's level, as a thief."""
    thief = max((lv for c, lv in zip(classes, levels) if c == tables.THIEF_CLASS), default=0)
    psi = max((lv for c, lv in zip(classes, levels) if c == tables.PSIONICIST_CLASS), default=0)
    if not thief and not psi:
        thief = group_level
    rows = [tables.rav_saves(3, thief)] if thief else []
    rows += [tables.rav_saves(3, psi, True)] if psi else []
    return tuple(min(row[k] for row in rows) for k in range(5))


def routine_saves(sheet: bytes, con: int) -> Optional[bytes]:
    """The five saves the game's routine puts in SHEET (with SAVE_BASE's Handbook tables), CON the
    creature's; None for one with no class."""
    classes = sheet[game.SHEET_CLASSES:game.SHEET_CLASSES + 3]
    levels = sheet[game.SHEET_LEVELS:game.SHEET_LEVELS + 3]
    groups = group_levels(classes, levels)
    if not any(level and level < 0x80 for level in groups):
        return None
    out = [START] * 5
    for group, level in enumerate(groups):
        if not 0 < level < 0x80:  # (the routine's "cmp byte [bx],0 / jg": a signed byte)
            continue
        row = rogue_saves(classes, levels, level) if group == 3 else tables.rav_saves(group, level)
        bonus = con * 2 // 7 if group == WARRIORS and sheet[game.SHEET_RACE] in (game.DWARF, game.HALFLING) else 0
        for k in range(5):
            value = max(row[k] - bonus, LEAST)
            if out[k] > value:  # (the sheet's byte, unsigned, against the word: "jle" keeps the lower)
                out[k] = value & 0xFF
    return bytes(out)


def mend(gd: "game.GameData") -> List[str]:
    """Each party member's saves put as the routine would put them now: a line for each one changed."""
    from . import aging
    out = []
    for member in range(game.PARTY_SIZE):
        rec, sheet = gd.creature(member), gd.sheet(member)
        if len(rec) < game.CREATURE_SIZE or len(sheet) < game.SHEET_SIZE or not rec[game.CREATURE_NAME]:
            continue
        want = routine_saves(sheet, rec[game.CREATURE_ABILITIES + 2])
        have = bytes(sheet[game.SHEET_SAVES:game.SHEET_SAVES + 5])
        if want is None or want == have:
            continue
        gd.guest.write(aging.sheet_address(gd, member) + game.SHEET_SAVES, want)
        said = ", ".join(f"{name} {a} to {b}" for name, a, b in zip(SAVE_NAMES, have, want) if a != b)
        out.append(f"{gd.creature_name(member)}'s saving throws worked out again: {said}.")
    return out


def save_ranges(gd: "game.GameData") -> List[Tuple[int, int]]:
    """The party's sheets' saves, (address, size): what mend writes."""
    from . import aging
    return [(aging.sheet_address(gd, m) + game.SHEET_SAVES, 5) for m in range(game.PARTY_SIZE)
            if len(gd.creature(m)) >= game.CREATURE_SIZE]
