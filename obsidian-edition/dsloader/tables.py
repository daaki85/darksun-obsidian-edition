"""AD&D's class tables (game.RULE_ADND_TABLES; DSCLOG's RULE_HI_TABLES, XP_NEED, PROBE_XP,
PROBE_PRIEST_THAC0, PROBE_ADND_SLOTS): the XP each class needs, priests' THAC0, and clerics',
druids' and preservers' spell slots by level, as AD&D's Player's Handbook and Dark Sun have them.
The game's own: a gladiator on the fighter's XP, a ranger's and a thief's 2nd level 2,200 and 1,200
(its table is in hundreds), priests' THAC0 2/3 a level, slot tables of its own."""

from typing import Optional, Sequence, Tuple

# the game's class rows (its XP table, View Character's copy of a sheet): 1-8
ROWS = ("cleric", "druid", "fighter", "gladiator", "preserver", "psionicist", "ranger", "thief")
# by row, the XP needed for each level 1-14 (DSCLOG's ADND_XP: an entry is the next level's)
XP = {
    "cleric": (0, 1500, 3000, 6000, 13000, 27500, 55000, 110000, 225000, 450000, 675000, 900000, 1125000, 1350000),
    "druid": (0, 2000, 4000, 7500, 12500, 20000, 35000, 60000, 90000, 125000, 200000, 300000, 750000, 1500000),
    "fighter": (0, 2000, 4000, 8000, 16000, 32000, 64000, 125000, 250000, 500000, 750000, 1000000, 1250000, 1500000),
    "gladiator": (0, 2250, 4500, 9000, 18000, 36000, 75000, 150000, 300000, 600000, 900000, 1200000, 1500000, 1800000),
    "preserver": (0, 2500, 5000, 10000, 20000, 40000, 60000, 90000, 135000, 250000, 375000, 750000, 1125000, 1500000),
    "psionicist": (0, 2200, 4400, 8800, 16500, 30000, 55000, 100000, 200000, 400000, 600000, 800000, 1000000, 1200000),
    "ranger": (0, 2250, 4500, 9000, 18000, 36000, 75000, 150000, 300000, 600000, 900000, 1200000, 1500000, 1800000),
    "thief": (0, 1250, 2500, 5000, 10000, 20000, 40000, 70000, 110000, 160000, 220000, 440000, 660000, 880000),
}
# spell slots at spell levels 1-5, by class level 1-12 (DSCLOG's ADND_SLOTS; a priest's 6th: slots())
PRIEST_SLOTS = ((1, 0, 0, 0, 0), (2, 0, 0, 0, 0), (2, 1, 0, 0, 0), (3, 2, 0, 0, 0), (3, 3, 1, 0, 0),
                (3, 3, 2, 0, 0), (3, 3, 2, 1, 0), (3, 3, 3, 2, 0), (4, 4, 3, 2, 1), (4, 4, 3, 3, 2),
                (5, 4, 4, 3, 2), (6, 5, 5, 3, 2))
WIZARD_SLOTS = ((1, 0, 0, 0, 0), (2, 0, 0, 0, 0), (2, 1, 0, 0, 0), (3, 2, 0, 0, 0), (4, 2, 1, 0, 0),
                (4, 2, 2, 0, 0), (4, 3, 2, 1, 0), (4, 3, 3, 2, 0), (4, 3, 3, 2, 1), (4, 4, 3, 2, 2),
                (4, 4, 4, 3, 3), (4, 4, 4, 4, 4))
PRESERVER = 11
PRIESTS = range(1, 9)  # (the sheet's classes: clerics 1-4, druids 5-8)
# the row of each of the sheet's classes (1-17: game.CLASS_NAMES), as the game's table at the level
# up's segment +0CAh has them
CLASS_ROWS = {**{c: "cleric" for c in range(1, 5)}, **{c: "druid" for c in range(5, 9)}, 9: "fighter",
              10: "gladiator", 11: "preserver", 12: "psionicist", **{c: "ranger" for c in range(13, 17)},
              17: "thief"}


def xp_needed(row: str, level: int) -> Optional[int]:
    """The XP a character of class ROW and LEVEL needs for the next level (None past 13th)."""
    table = XP[row]
    return table[level] if 0 <= level < len(table) else None


def xp_share(classes, levels, human: bool, cap: int) -> int:
    """The XP a character may gather under the XP cap CAP (DSCLOG's LEVEL_ROOM, which no class's next
    level may need more than): CLASSES and LEVELS the sheet's three of each. One class: all of it.
    Several (not a human): CAP divided between them, as the game shares out XP. A human who changed
    class: CAP less the XP each old class's level needed (slots 1 and 2: the game starts the new
    class at 0), never below 0. An old class past the tables' 14th level counts all of CAP (none
    gets there under it)."""
    if not human:
        count = sum(1 for c in classes[:3] if c)
        return cap // count if count else cap
    share = cap
    for cls, level in zip(classes[1:3], levels[1:3]):
        row = CLASS_ROWS.get(cls)
        if not level or row is None:
            continue
        need = xp_needed(row, level - 1)
        share = max(share - (cap if need is None else need), 0)
    return share


def slots(cls: int, level: int, spell_level: int) -> Optional[int]:
    """AD&D's slots for the class levels of sheet class CLS at SPELL_LEVEL (1-6: the 6th a priest's
    alone, AD&D's 1 at 11th level and 2 at 12th; a wizard has no 6th-level spells to cast), None
    for a class whose slots stay the game's (rangers')."""
    if cls == PRESERVER:
        table = WIZARD_SLOTS
    elif cls in PRIESTS:
        table = PRIEST_SLOTS
    else:
        return None
    if spell_level == 6 and table is PRIEST_SLOTS:
        return min(max(level - 10, 0), 2)
    if level < 1 or not 1 <= spell_level <= 5:
        return 0
    return table[min(level, len(table)) - 1][spell_level - 1]


def priest_thac0(level: int) -> int:
    """A priest's THAC0 at LEVEL, AD&D's: 2 better every 3 levels."""
    return 20 - 2 * ((max(level, 1) - 1) // 3)


# Wake of the Ravager (ravager.py; DSCLOG2's XP_NEED, PRIEST_THAC0 and ADND_SLOTS): its XP table
# runs to index 19 (20 levels, in hundreds as SL's), the same as AD&D's but for the thief's,
# gladiator's and ranger's 2nd levels (1,200 and 2,200), the druid's from 11th (the cleric's
# copied), the gladiator's 16th and up (the fighter's) and the psionicist's 18th and 19th (1,400,000
# and 1,700,000 for 2,400,000 and 2,700,000). AD&D's past 14th: each level the same step more (the
# druid's Dark Sun's, 500,000 from 16th). Levels 21-30 (DSCLOG2's RAV_XP, past the game's table): the
# owner's AD&D tables (2026-11-25), each the same step more again; the druid's the hierophant's count
# on top of 20th's 3,500,000 (6,000,000 at 21st), the gladiator's the ranger's, the psionicist's its own.
def _steps(last: int, step: int, n: int = 6) -> tuple:
    return tuple(last + step * k for k in range(1, n + 1))


RAV_XP = {
    "cleric": XP["cleric"] + _steps(1350000, 225000, 16),
    "druid": XP["druid"] + (3000000, 3500000, 4000000, 4500000, 5000000, 5500000) + _steps(5500000, 500000, 10),
    "fighter": XP["fighter"] + _steps(1500000, 250000, 16),
    "gladiator": XP["gladiator"] + _steps(1800000, 300000, 16),
    "preserver": XP["preserver"] + _steps(1500000, 375000, 16),
    "psionicist": XP["psionicist"] + _steps(1200000, 300000) + (
        3300000, 3600000, 4000000, 4400000, 4800000, 5200000, 5600000, 6000000, 6500000, 7000000),
    "ranger": XP["ranger"] + _steps(1800000, 300000, 16),
    "thief": XP["thief"] + _steps(880000, 220000, 16),
}
RAV_XP_LEVELS = 30  # (DSCLOG2's RAV_LEVELS: entries 0-29, the XP a level 1-30 needs)
# the sequel's spell slots by class level 1-30 (more is 30th's), spell levels 1-9 (a priest's 1-7):
# the Player's Handbook's tables in full to 20th, then the owner's (2026-11-25: High Level Campaigns'
# without a wizard's 10th level and a priest's true dweomers)
RAV_PRIEST_SLOTS = PRIEST_SLOTS[:10] + (
    (5, 4, 4, 3, 2, 1), (6, 5, 5, 3, 2, 2), (6, 6, 6, 4, 2, 2), (6, 6, 6, 5, 3, 2, 1),
    (6, 6, 6, 6, 4, 2, 1), (7, 7, 7, 6, 4, 3, 1), (7, 7, 7, 7, 5, 3, 2), (8, 8, 8, 8, 6, 4, 2),
    (9, 9, 8, 8, 6, 4, 2), (9, 9, 9, 8, 7, 5, 2),
    (9, 9, 9, 9, 8, 6, 2), (9, 9, 9, 9, 9, 6, 3), (9, 9, 9, 9, 9, 7, 3), (9, 9, 9, 9, 9, 8, 3),
    (9, 9, 9, 9, 9, 8, 4), (9, 9, 9, 9, 9, 9, 4), (9, 9, 9, 9, 9, 9, 5), (9, 9, 9, 9, 9, 9, 6),
    (9, 9, 9, 9, 9, 9, 7), (9, 9, 9, 9, 9, 9, 8))
RAV_WIZARD_SLOTS = WIZARD_SLOTS[:11] + (
    (4, 4, 4, 4, 4, 1), (5, 5, 5, 4, 4, 2), (5, 5, 5, 4, 4, 2, 1), (5, 5, 5, 5, 5, 2, 1),
    (5, 5, 5, 5, 5, 3, 2, 1), (5, 5, 5, 5, 5, 3, 3, 2), (5, 5, 5, 5, 5, 3, 3, 2, 1),
    (5, 5, 5, 5, 5, 3, 3, 3, 1), (5, 5, 5, 5, 5, 4, 3, 3, 2),
    (5, 5, 5, 5, 5, 4, 4, 4, 2), (5, 5, 5, 5, 5, 5, 4, 4, 3), (5, 5, 5, 5, 5, 5, 5, 5, 3),
    (5, 5, 5, 5, 5, 5, 5, 5, 4), (5, 5, 5, 5, 5, 5, 5, 5, 5), (6, 6, 6, 6, 5, 5, 5, 5, 5),
    (6, 6, 6, 6, 6, 6, 6, 5, 5), (6, 6, 6, 6, 6, 6, 6, 6, 6), (7, 7, 7, 7, 6, 6, 6, 6, 6),
    (7, 7, 7, 7, 7, 7, 7, 6, 6))
# a druid's: the cleric's to 15th, then 15th's (the owner's table, 2026-11-25: a druid's slots stop growing)
RAV_DRUID_SLOTS = RAV_PRIEST_SLOTS[:15] + (RAV_PRIEST_SLOTS[14],) * 15
# a ranger's priest spells (8th level on; the game's own formula gave 3 2 1 at 12th, 3 2 2 at 13th, 3 3 2
# at 14th): the Player's Handbook's, as the owner's table has them
RAV_RANGER_SLOTS = ((),) * 7 + ((1,), (2,), (2, 1), (2, 2), (2, 2, 1), (3, 2, 1), (3, 2, 2), (3, 3, 2)) \
    + ((3, 3, 3),) * 15
RAV_SLOT_LEVELS = 30
DRUIDS, RANGERS = range(5, 9), range(13, 17)


def rav_slots(cls: int, level: int, spell_level: int) -> Optional[int]:
    """The sequel's: AD&D's slots for the class levels of sheet class CLS at SPELL_LEVEL (1-9), None
    for a class whose slots stay the game's."""
    if cls == PRESERVER:
        table = RAV_WIZARD_SLOTS
    elif cls in DRUIDS:
        table = RAV_DRUID_SLOTS
    elif cls in PRIESTS:
        table = RAV_PRIEST_SLOTS
    elif cls in RANGERS:
        table = RAV_RANGER_SLOTS
    else:
        return None
    if level < 1:
        return 0
    row = table[min(level, RAV_SLOT_LEVELS) - 1]
    return row[spell_level - 1] if 1 <= spell_level <= len(row) else 0


# The saving throws in both games (DSCLOG's and DSCLOG2's SAVE_BASE, RULE_HI_TABLES): the Player's
# Handbook's (2nd edition, Table 60) by the game's class groups (0 priest, 1 warrior, 2 wizard, 3 rogue)
# and level, and the psionicists' own (Dark Sun's Table 8: SAVE_PSIONICIST, a fifth band set), each band
# (first level, the five saves: paralysis, poison and death; rod, staff and wand; petrification and
# polymorph; breath; spell). The games' own (SL's 877EBh, the sequel's 954D2h: the 1st level's save
# less (level - 1) x a rate / 100) took the table's last row as the most a save could improve by, so a
# warrior stayed at 11/11/11/13/11 from 10th level and no save of any class went below 8; and they put
# psionicists with thieves (group 3, at the best level of either).
RAV_SAVE_BANDS = (
    ((1, (10, 14, 13, 16, 15)), (4, (9, 13, 12, 15, 14)), (7, (7, 11, 10, 13, 12)), (10, (6, 10, 9, 12, 11)),
     (13, (5, 9, 8, 11, 10)), (16, (4, 8, 7, 10, 9)), (19, (2, 6, 5, 8, 7))),
    ((1, (14, 16, 15, 17, 17)), (3, (13, 15, 14, 16, 16)), (5, (11, 13, 12, 13, 14)), (7, (10, 12, 11, 12, 13)),
     (9, (8, 10, 9, 9, 11)), (11, (7, 9, 8, 8, 10)), (13, (5, 7, 6, 5, 8)), (15, (4, 6, 5, 4, 7)),
     (17, (3, 5, 4, 4, 6))),
    ((1, (14, 11, 13, 15, 12)), (6, (13, 9, 11, 13, 10)), (11, (11, 7, 9, 11, 8)), (16, (10, 5, 7, 9, 6)),
     (21, (8, 3, 5, 7, 4))),
    ((1, (13, 14, 12, 16, 15)), (5, (12, 12, 11, 15, 13)), (9, (11, 10, 10, 14, 11)), (13, (10, 8, 9, 13, 9)),
     (17, (9, 6, 8, 12, 7)), (21, (8, 4, 7, 11, 5))),
    ((1, (13, 15, 10, 16, 15)), (5, (12, 13, 9, 15, 14)), (9, (11, 11, 8, 13, 12)), (13, (10, 9, 7, 12, 11)),
     (17, (9, 7, 6, 11, 9)), (21, (8, 5, 5, 9, 7))),
)
SAVE_PSIONICIST = 4  # (RAV_SAVE_BANDS' psionicists' set)
RAV_SAVE_LEVELS = 21  # (the tables' last band starts at 21st at most: more is the last's)


def rav_saves(group: int, level: int, psionicist: bool = False) -> tuple:
    """The five saves of class group GROUP (0-3) at LEVEL (1 and up), the Player's Handbook's; a
    psionicist's (PSIONICIST, in group 3) Dark Sun's."""
    bands = RAV_SAVE_BANDS[SAVE_PSIONICIST if psionicist else group]
    out = bands[0][1]
    for first, saves in bands:
        if level >= first:
            out = saves
    return out


def class_saves(classes: Sequence[Tuple[int, int]]) -> tuple:
    """A character's five saves from its (class, level) pairs (the game's class numbers: 1-8 priests,
    9, 10 and 13-16 warriors, 11 the preserver, 12 the psionicist, 17 the thief): the best of each
    class's, as SAVE_BASE makes them (the game keeps the best of its groups)."""
    rows = [rav_saves(CLASS_GROUPS[c], level, c == PSIONICIST_CLASS) for c, level in classes
            if c in CLASS_GROUPS and level > 0]
    return tuple(min(row[k] for row in rows) for k in range(5))


PSIONICIST_CLASS = 12
THIEF_CLASS = 17
# the games' class groups (SL's 420h:10h + the class, the sequel's 4D0h:10h): clerics and druids (1-8)
# priests 0, fighters, gladiators and rangers (9, 10, 13-16) warriors 1, the preserver (11) wizards 2, the
# psionicist and the thief (12, 17) rogues 3
CLASS_GROUPS = {**{c: 0 for c in range(1, 9)}, 9: 1, 10: 1, 11: 2, 12: 3, **{c: 1 for c in range(13, 17)}, 17: 3}
