"""The Spellarcher's spell arrows (kits.py: the half-elf fighter/preserver's kit).

Four wizard spells of the Loader's, Burning, Chill, Shocking and Vampiric Arrows (spells 202-205,
DSCLOG's ARROW SPELLS), each of its touch spell's level, on the caster alone: a Spellarcher who
knows the touch spell has its arrows' spell too, its icon on the USE screen with the other spells
of that level. One click casts it, the game using up the slot as for any spell; DSCLOG records the
cast (CAST_SITE, the dice log's KIND_CAST) and leaves the rest out, and here (`cast`, then `made`
in the next pass) a stack of ARROWS_PER_LEVEL arrows for each of the caster's preserver levels
goes in its backpack, worth nothing (no merchant pays for them). Slots are the only limit.

At a rest (a script's rest request, as at a fire ring, or the vulture meal) every spell arrow left
anywhere fades (`vanish`).

An arrow casts its spell on what it hits, shot from a bow (DSCLOG's ARROW_HIT: the game casts only
a bow's own spell; the arrow's, told by its name, takes its place), at the archer's caster level as
the game reckons it for that spell: the Spellarcher's preserver level.
"""

import struct
from typing import Dict, List, NamedTuple, Set, Tuple

from . import game, npcitems, ring, weaponchoice
from .game import GameData


class Arrow(NamedTuple):
    spell: int          # the touch spell (its record's number)
    spell_name: str
    name: int           # the arrows' name entry (DSCLOG's ARROW_NAMES)
    level: int          # the spell's level: the slot its arrows' spell takes
    cast: int           # the arrows' own spell (game.ARROW_SPELLS), cast to make them


ARROWS = (
    Arrow(1, "Burning Hands", 0x16C, 1, 202),
    Arrow(3, "Chill Touch", 0x16D, 1, 203),
    Arrow(10, "Shocking Grasp", 0x16E, 1, 204),
    Arrow(39, "Vampiric Touch", 0x16F, 3, 205),
)
BY_CAST = {a.cast: a for a in ARROWS}
NAMES = {0x16C: b"Burning Arrows", 0x16D: b"Chill Arrows", 0x16E: b"Shocking Arrows", 0x16F: b"Vampiric Arrows"}
ARROW_NAMES = {a.name for a in ARROWS}
# their pictures (icons.py: the game's Arrows', tinted for each spell), objects 2614-2621
PICTURES = {0x16C: 0x10000 - 2614, 0x16D: 0x10000 - 2616, 0x16E: 0x10000 - 2618, 0x16F: 0x10000 - 2620}
ARROWS_PER_LEVEL = 5
ARROWS_TYPE = weaponchoice.ARROWS[1]  # (the game's Arrows)
TEMPLATE = npcitems._item("0cfc000000002d000000510000000000" "04ff1c0000")  # (worldgear's)
REST_REQUESTS = (1, 4)  # a script's REQUEST that rests the party (dicelog.REQUEST_NAMES)


def is_arrow(rec: bytes) -> bool:
    return len(rec) >= game.ITEM_SIZE and struct.unpack_from("<H", rec, game.ITEM_NAME)[0] in ARROW_NAMES


def arrows_item(arrow: Arrow, count: int) -> bytes:
    """A stack of COUNT arrows of ARROW's spell: the game's Arrows, its own name and picture, worth
    nothing."""
    rec = bytearray(weaponchoice.arrows(TEMPLATE))
    struct.pack_into("<HH", rec, weaponchoice.ITEM_PICTURE, PICTURES[arrow.name], count)
    struct.pack_into("<H", rec, weaponchoice.ITEM_VALUE, 0)
    struct.pack_into("<H", rec, game.ITEM_NAME, arrow.name)
    return bytes(rec)


class SpellArrows:
    def __init__(self):
        self.due: List[Tuple[int, Arrow]] = []  # (arrow spells cast, their arrows not made yet)

    def cast(self, member: int, spell: int) -> None:
        """Party member MEMBER cast arrow spell SPELL: its arrows are made in the next pass."""
        if 0 <= member < game.PARTY_SIZE and spell in BY_CAST:
            self.due.append((member, BY_CAST[spell]))

    def made(self, gd: GameData) -> List[str]:
        """The arrows of the spells cast since the last pass, in their casters' backpacks: lines
        for the log (itemgate.ItemsBusy passed on, the casts kept for the next pass)."""
        out: List[str] = []
        while self.due:
            member, arrow = self.due[0]
            out.append(make(gd, member, arrow))
            self.due.pop(0)
        return out

    def rest(self, gd: GameData) -> List[str]:
        """The party rested: every spell arrow fades."""
        return vanish(gd)


def make(gd: GameData, member: int, arrow: Arrow) -> str:
    """A stack of ARROW's arrows, ARROWS_PER_LEVEL for each of party member MEMBER's preserver
    levels, in its backpack: the line for the log."""
    level = gd.class_level(member, game.PRESERVER)
    count = ARROWS_PER_LEVEL * max(level, 1)
    who = gd.creature_name(member)
    name = NAMES[arrow.name].decode().lower()
    if not npcitems.add_to(gd, member, arrows_item(arrow, count)):
        return f"{who} casts {arrow.spell_name} into arrows, but has no room for them: none made"
    return (f"{who} makes {count} {name} ({ARROWS_PER_LEVEL} a preserver level, {level}): a "
            f"{_nth(arrow.level)}-level slot used; each casts {arrow.spell_name} on what it hits")


def _nth(level: int) -> str:
    return {1: "1st", 2: "2nd", 3: "3rd"}.get(level, f"{level}th")


def vanish(gd: GameData) -> List[str]:
    """Every spell arrow, wherever it is, given back to the game's free list: lines for the log."""
    party_lists: Set[int] = set()
    for member in range(game.PARTY_SIZE):
        rec = gd.creature(member)
        if len(rec) >= game.CREATURE_SIZE:
            party_lists.update(struct.unpack_from("<h", rec, o)[0] for o in game.CREATURE_ITEM_LISTS)
    counts: Dict[int, int] = {}
    stuck: Set[int] = set()  # (a container's only item, left: the game's containers aren't empty)
    for _ in range(ring.THING_COUNT):  # (one at a time: each unlink changes the lists)
        it = ring.Items(gd)
        found = next(((thing, index, rec) for thing in range(ring.THING_COUNT)
                      for index, rec in it.chain(thing, inside=False) if is_arrow(rec) and index not in stuck), None)
        if found is None:
            break
        thing, index, rec = found
        name = struct.unpack_from("<H", rec, game.ITEM_NAME)[0]
        if not ring.unlink(gd, it, index, "spell arrows faded at a rest", empty=thing in party_lists):
            stuck.add(index)
            continue
        counts[name] = counts.get(name, 0) + struct.unpack_from("<H", rec, weaponchoice.ITEM_COUNT)[0]
    return [f"The {NAMES[name].decode().lower()} fade with the rest ({count})" for name, count in counts.items()]
