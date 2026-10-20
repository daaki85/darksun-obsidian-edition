"""Defilers' scrolls: a defiler in a fight may carry a scroll of a preserver spell, dropped where it dies.

The game puts all a creature carries in a pile where it falls, in the same step as its hit points
reach 0 (seen in the arena's opening fight: the Defiler's lists emptied and its things on the
ground before the Loader's next look), so a scroll can't be added at the death itself. Instead,
each defiler (a creature of one of the game's objects whose record has the defiler's class, 18:
DEFILER_OBJECTS) is rolled for once in each fight it is seen in,
alive: d100, CHANCE or less and it carries a scroll of a random preserver spell, which the game
drops with the rest of its things when it dies. Kalzith keeps his own loot (kalzith.loot).

The roll is remembered for the session (by area, creature and name) and forgotten when a game is
loaded: a fight played again from a save is rolled again, as the death is a new one. A defiler
already carrying such a scroll (a save made mid-fight) gets no second. The dice log doesn't show
the roll: what a defiler carries is for the party to find on its body.

The scroll is the game's own kind of item (kalzith.scroll), of the game's first scroll object, 1400
(one the game teaches from when right-clicked: 1400-1499): the spell is the item's own, so one
object serves every spell; priced as the game prices its scrolls, 3000 a spell level.
"""

import random
import struct
from typing import Callable, Iterable, List, Optional, Set, Tuple

from . import game, itemgate, kalzith, npcitems

CHANCE = 5  # percent
DEFILER_CLASS = 18  # (a sheet's classes, SHEET_CLASSES: the defilers', which no party member has)
# The game's objects whose records (SEGOBJEX.GFF's RDFF) have that class: Balkazar (14, 72), the
# Troop Leader (18), Tara (24), Wyrmias (32), the thri-kreen Click-tu, Cheee-sm and Churr-te (38,
# 40, 52), the Dark Spiders (53, 54, 147, 255), the Hermit (81), the Spider Mother (161) and the
# arena's Defilers (258, 296). Known by a creature's object (CREATURE_OBJECT), not the class on its
# character sheet: the game hands sheets on from one creature to the next, so a sheet can still be
# a defiler's under another (one of Scar's henchmen was given a scroll so).
DEFILER_OBJECTS = frozenset((14, 18, 24, 32, 38, 40, 52, 53, 54, 72, 81, 147, 161, 255, 258, 296))
CREATURE_OBJECT = 0x06  # (a creature record's object, negated: the record's copy of RDFF's +10h)
SCROLL_OBJECT = kalzith.SCROLL_FROM  # (the game's first scroll object, whose picture all scrolls share)
PRICE_PER_LEVEL = 3000
WIZARD_SPELLS = range(0, 69)  # (the game's wizard spells: 0-68, of levels 1 to 5)
SEEN = 128  # creature records looked at (as kalzith.CREATURES_SEEN)
DEAD_STATUS = kalzith.DEAD_STATUS


def scroll(spell: int, level: int) -> bytes:
    """A scroll item teaching SPELL (of spell level LEVEL), of the game's scroll object."""
    rec = bytearray(kalzith.scroll(spell, PRICE_PER_LEVEL * max(level, 1)))
    struct.pack_into("<h", rec, kalzith.ITEM_OBJECT, -SCROLL_OBJECT)
    return bytes(rec)


def is_ours(rec: bytes) -> bool:
    """An item record of a defiler's scroll (the game's scroll object)."""
    return len(rec) >= 2 and struct.unpack_from("<h", rec, kalzith.ITEM_OBJECT)[0] == -SCROLL_OBJECT


def spells(levels: Callable[[int], int], new_spells: bool) -> List[int]:
    """The preserver spells a scroll may be of: the game's wizard spells and, with their rule on,
    the new ones the game has set up (a spell level of 1 to 5 in its table)."""
    pool: Iterable[int] = list(WIZARD_SPELLS) + (sorted(game.NEW_SPELLS) if new_spells else [])
    return [spell for spell in pool if 1 <= levels(spell) <= 5]


class DefilerScrolls:
    def __init__(self, chance: int = CHANCE):
        self.chance = chance
        self.rolled: Set[Tuple[int, int, bytes]] = set()  # (area, creature, name) rolled for
        self.defilers: dict = {}  # (area, creature, name) -> whether its sheet is a defiler's
        self.given: List[Tuple[str, str]] = []  # (defiler, spell) given a scroll, for tests

    def reset(self) -> None:
        """Forget the rolls (a game was loaded)."""
        self.rolled.clear()
        self.defilers.clear()
        self.given.clear()

    def _is_defiler(self, gd, index: int, key) -> bool:
        if key not in self.defilers:
            rec = gd.creature(index)
            obj = -struct.unpack_from("<h", rec, CREATURE_OBJECT)[0] if len(rec) >= CREATURE_OBJECT + 2 else 0
            self.defilers[key] = obj in DEFILER_OBJECTS
        return self.defilers[key]

    def _carries_one(self, gd, index: int) -> bool:
        from . import ring
        it = ring.Items(gd)
        rec = gd.creature(index)
        return any(is_ours(item) for offset in game.CREATURE_ITEM_LISTS
                   for _, item in it.chain(struct.unpack_from("<h", rec, offset)[0]))

    def watch(self, gd, new_spells: bool, roll: Optional[Callable[[], int]] = None,
              choose: Optional[Callable[[List[int]], int]] = None) -> List[str]:
        """In a fight, each living defiler not yet rolled for: d100 (ROLL), and at CHANCE or less a
        scroll of a spell (CHOOSE among spells()) put in its pack (noted in GIVEN). No lines for the
        log: the roll would tell the player what the body holds before the fight is won."""
        if not gd.in_combat():
            return []
        roll = roll or (lambda: random.randint(1, 100))
        choose = choose or random.choice
        area = gd.region()
        table = gd.creatures(SEEN)
        size = game.CREATURE_SIZE
        for index in range(game.PARTY_SIZE, len(table) // size):
            rec = table[index * size:(index + 1) * size]
            name = rec[game.CREATURE_NAME:game.CREATURE_NAME + 16].split(b"\0", 1)[0]
            if not name or name == kalzith.NAME.encode("ascii"):
                continue
            if struct.unpack_from("<h", rec, 0)[0] <= 0 or rec[game.CREATURE_STATUS] in DEAD_STATUS:
                continue
            key = (area, index, name)
            if key in self.rolled or not self._is_defiler(gd, index, key):
                continue
            who = name.decode("cp437", "replace")
            if self._carries_one(gd, index):
                self.rolled.add(key)
                continue  # (given one before this game was saved)
            itemgate.hold(gd)  # (before the roll: the game busy with its lists, rolled for in a later pass)
            self.rolled.add(key)
            if roll() > self.chance:
                continue
            pool = spells(gd.spell_level, new_spells)
            if pool:
                spell = choose(pool)
                if npcitems.add_to(gd, index, scroll(spell, gd.spell_level(spell))):
                    self.given.append((who, gd.spell_name(spell)))
        return []  # (the log keeps quiet: what a defiler carries is found on its body)
