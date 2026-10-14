"""AD&D's class tables (game.RULE_ADND_TABLES; DSCLOG's RULE_HI_TABLES, XP_NEED, PROBE_XP,
PROBE_PRIEST_THAC0, PROBE_ADND_SLOTS): the XP each class needs, priests' THAC0, and clerics',
druids' and preservers' spell slots by level, as AD&D's Player's Handbook and Dark Sun have them.
The game's own: a gladiator on the fighter's XP, a ranger's and a thief's 2nd level 2,200 and 1,200
(its table is in hundreds), priests' THAC0 2/3 a level, slot tables of its own."""

from typing import Optional

# the game's class rows (its XP table, View Character's copy of a sheet): 1-8
ROWS = ("cleric", "druid", "fighter", "gladiator", "preserver", "psionicist", "ranger", "thief")
# by row, the XP needed for each level 1-11 (DSCLOG's ADND_XP: an entry is the next level's)
XP = {
    "cleric": (0, 1500, 3000, 6000, 13000, 27500, 55000, 110000, 225000, 450000, 675000),
    "druid": (0, 2000, 4000, 7500, 12500, 20000, 35000, 60000, 90000, 125000, 200000),
    "fighter": (0, 2000, 4000, 8000, 16000, 32000, 64000, 125000, 250000, 500000, 750000),
    "gladiator": (0, 2250, 4500, 9000, 18000, 36000, 75000, 150000, 300000, 600000, 900000),
    "preserver": (0, 2500, 5000, 10000, 20000, 40000, 60000, 90000, 135000, 250000, 375000),
    "psionicist": (0, 2200, 4400, 8800, 16500, 30000, 55000, 100000, 200000, 400000, 600000),
    "ranger": (0, 2250, 4500, 9000, 18000, 36000, 75000, 150000, 300000, 600000, 900000),
    "thief": (0, 1250, 2500, 5000, 10000, 20000, 40000, 70000, 110000, 160000, 220000),
}
# spell slots at spell levels 1-5, by class level 1-10 (DSCLOG's ADND_SLOTS)
PRIEST_SLOTS = ((1, 0, 0, 0, 0), (2, 0, 0, 0, 0), (2, 1, 0, 0, 0), (3, 2, 0, 0, 0), (3, 3, 1, 0, 0),
                (3, 3, 2, 0, 0), (3, 3, 2, 1, 0), (3, 3, 3, 2, 0), (4, 4, 3, 2, 1), (4, 4, 3, 3, 2))
WIZARD_SLOTS = ((1, 0, 0, 0, 0), (2, 0, 0, 0, 0), (2, 1, 0, 0, 0), (3, 2, 0, 0, 0), (4, 2, 1, 0, 0),
                (4, 2, 2, 0, 0), (4, 3, 2, 1, 0), (4, 3, 3, 2, 0), (4, 3, 3, 2, 1), (4, 4, 3, 2, 2))
PRESERVER = 11
PRIESTS = range(1, 9)  # (the sheet's classes: clerics 1-4, druids 5-8)


def xp_needed(row: str, level: int) -> Optional[int]:
    """The XP a character of class ROW and LEVEL needs for the next level (None past 10th)."""
    table = XP[row]
    return table[level] if 0 <= level < len(table) else None


def slots(cls: int, level: int, spell_level: int) -> Optional[int]:
    """AD&D's slots for the class levels of sheet class CLS at SPELL_LEVEL (1-5), None for a
    class whose slots stay the game's (rangers')."""
    if cls == PRESERVER:
        table = WIZARD_SLOTS
    elif cls in PRIESTS:
        table = PRIEST_SLOTS
    else:
        return None
    if level < 1 or not 1 <= spell_level <= 5:
        return 0
    return table[min(level, 10) - 1][spell_level - 1]


def priest_thac0(level: int) -> int:
    """A priest's THAC0 at LEVEL, AD&D's: 2 better every 3 levels."""
    return 20 - 2 * ((max(level, 1) - 1) // 3)
