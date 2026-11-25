"""AD&D's class tables (game.RULE_ADND_TABLES; DSCLOG's RULE_HI_TABLES, XP_NEED, PROBE_XP,
PROBE_PRIEST_THAC0, PROBE_ADND_SLOTS): the XP each class needs, priests' THAC0, and clerics',
druids' and preservers' spell slots by level, as AD&D's Player's Handbook and Dark Sun have them.
The game's own: a gladiator on the fighter's XP, a ranger's and a thief's 2nd level 2,200 and 1,200
(its table is in hundreds), priests' THAC0 2/3 a level, slot tables of its own."""

from typing import Optional

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


def xp_needed(row: str, level: int) -> Optional[int]:
    """The XP a character of class ROW and LEVEL needs for the next level (None past 13th)."""
    table = XP[row]
    return table[level] if 0 <= level < len(table) else None


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
# druid's Dark Sun's, 500,000 from 16th).
def _steps(last: int, step: int) -> tuple:
    return tuple(last + step * n for n in range(1, 7))


RAV_XP = {
    "cleric": XP["cleric"] + _steps(1350000, 225000),
    "druid": XP["druid"] + (3000000, 3500000, 4000000, 4500000, 5000000, 5500000),
    "fighter": XP["fighter"] + _steps(1500000, 250000),
    "gladiator": XP["gladiator"] + _steps(1800000, 300000),
    "preserver": XP["preserver"] + _steps(1500000, 375000),
    "psionicist": XP["psionicist"] + _steps(1200000, 300000),
    "ranger": XP["ranger"] + _steps(1800000, 300000),
    "thief": XP["thief"] + _steps(880000, 220000),
}
# the sequel's spell slots by class level 1-20 (more is 20th's), spell levels 1-9 (a priest's 1-7):
# the Player's Handbook's tables in full
RAV_PRIEST_SLOTS = PRIEST_SLOTS[:10] + (
    (5, 4, 4, 3, 2, 1), (6, 5, 5, 3, 2, 2), (6, 6, 6, 4, 2, 2), (6, 6, 6, 5, 3, 2, 1),
    (6, 6, 6, 6, 4, 2, 1), (7, 7, 7, 6, 4, 3, 1), (7, 7, 7, 7, 5, 3, 2), (8, 8, 8, 8, 6, 4, 2),
    (9, 9, 8, 8, 6, 4, 2), (9, 9, 9, 8, 7, 5, 2))
RAV_WIZARD_SLOTS = WIZARD_SLOTS[:11] + (
    (4, 4, 4, 4, 4, 1), (5, 5, 5, 4, 4, 2), (5, 5, 5, 4, 4, 2, 1), (5, 5, 5, 5, 5, 2, 1),
    (5, 5, 5, 5, 5, 3, 2, 1), (5, 5, 5, 5, 5, 3, 3, 2), (5, 5, 5, 5, 5, 3, 3, 2, 1),
    (5, 5, 5, 5, 5, 3, 3, 3, 1), (5, 5, 5, 5, 5, 4, 3, 3, 2))
# a druid's: the cleric's to 15th, then 15th's (the owner's table, 2026-11-25: a druid's slots stop growing)
RAV_DRUID_SLOTS = RAV_PRIEST_SLOTS[:15] + (RAV_PRIEST_SLOTS[14],) * 5
# a ranger's priest spells (8th level on; the game's own formula gave 3 2 1 at 12th, 3 2 2 at 13th, 3 3 2
# at 14th): the Player's Handbook's, as the owner's table has them
RAV_RANGER_SLOTS = ((),) * 7 + ((1,), (2,), (2, 1), (2, 2), (2, 2, 1), (3, 2, 1), (3, 2, 2), (3, 3, 2)) \
    + ((3, 3, 3),) * 5
RAV_SLOT_LEVELS = 20
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


# The sequel's saving throws (DSCLOG2's SAVE_BASE, RULE_HI_TABLES): the Player's Handbook's (2nd
# edition, Table 60) by the game's class groups (0 priest, 1 warrior, 2 wizard, 3 rogue: thieves and
# psionicists, as Dark Sun has them) and level, each band (first level, the five saves: paralysis,
# poison and death; rod, staff and wand; petrification and polymorph; breath; spell). The game's own
# (954D2h: the 1st level's save less (level - 1) x a rate / 100) took the table's last row as the most
# a save could improve by, so a warrior stayed at 11/11/11/13/11 from 10th level and a priest's
# paralysis save at 8 from 9th; no save of any class went below 8.
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
)
RAV_SAVE_LEVELS = 21  # (DSCLOG2's SAVE_TABLE: a row a level 1-21, more is 21st's)


def rav_saves(group: int, level: int) -> tuple:
    """The five saves of class group GROUP (0-3) at LEVEL (1 and up), the Player's Handbook's."""
    out = RAV_SAVE_BANDS[group][0][1]
    for first, saves in RAV_SAVE_BANDS[group]:
        if level >= first:
            out = saves
    return out
