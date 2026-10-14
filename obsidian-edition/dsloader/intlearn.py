"""A preserver's INT and the spells it learns (the rule for it: game.RULE_INT_LEARN; DSCLOG's
INT_LEARN). As AD&D's table for INT: the chance to learn a wizard spell from a scroll, and the most
spells of each spell level a preserver may know. A failed try uses the scroll up; a spell level
already full can't take the scroll's spell (the scroll is kept) and isn't offered on CHOOSE A SPELL
at a level up."""
from typing import Optional

FIRST = 9  # the table's first INT (a preserver's least; below it, as 9)
# the chance (%) and the most spells a level (None: all), INT 9 to 25 (DSCLOG's INT_CHANCE, INT_MOST)
CHANCE = (35, 40, 45, 50, 55, 60, 65, 70, 75, 85, 95, 96, 97, 98, 99, 100, 100)
MOST = (6, 7, 7, 7, 9, 9, 11, 11, 14, 18, None, None, None, None, None, None, None)
LEARNT, FAILED, FULL = 0, 1, 2  # DSCLOG's LEARN_RESULT

ORDINALS = {1: "1st", 2: "2nd", 3: "3rd"}


def row(intelligence: int) -> int:
    return min(max(intelligence - FIRST, 0), len(CHANCE) - 1)


def chance(intelligence: int) -> int:
    return CHANCE[row(intelligence)]


def most(intelligence: int) -> Optional[int]:
    return MOST[row(intelligence)]


def ordinal(n: int) -> str:
    return ORDINALS.get(n, f"{n}th")


def line(who: str, spell: str, intelligence: int, rate: int, roll: int, result: int, level: int) -> str:
    """The dice log's line for a try at a scroll's spell (ROLL the d100, or for FULL the spells of
    the level known)."""
    if result == FULL:
        return (f"{who} can't learn {spell} from the scroll: knows {roll} {ordinal(level)}-level spells, "
                f"the most for INT {intelligence} (the scroll is kept)")
    verdict = "learnt" if result == LEARNT else "not learnt (the scroll is used up)"
    return f"{who} reads the scroll of {spell}: d100 = {roll}, needs {rate} or less (INT {intelligence}) -> {verdict}"
