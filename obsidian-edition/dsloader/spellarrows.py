"""The Spellarcher's spell arrows (kits.py: the half-elf fighter/preserver's kit).

Outside a fight, the USE screen gives a Spellarcher a button for each touch spell it knows (Burning
Hands, Chill Touch and Shocking Grasp at 1st level, Vampiric Touch at 3rd), with Turn Undead's and
Pick Pockets' (DSCLOG's PP_SHOW: in Turn Undead's place when no priest's element has it, then the
slots beside it). Pressed, it comes here as an item used on the map does (dicelog's _answer_use:
USE_ITEM ARROWS_BY and the member, USE_WHO the spell's place in ARROWS): a slot of that spell's
level is used up and a stack of ARROWS_PER_LEVEL arrows for each of the Spellarcher's preserver
levels goes in its backpack, worth nothing (no merchant pays for them). Slots are the only limit.

At a rest (the game's own, from its menu or a script, as at a fire ring; a script's other rest
request; or the vulture meal) every spell arrow left anywhere fades (`vanish`).

An arrow casts its spell on what it hits, shot from a bow (DSCLOG's ARROW_HIT: the game casts only
a bow's own spell; the arrow's, told by its name, takes its place), at the archer's caster level as
the game reckons it for that spell: the Spellarcher's preserver level.
"""

import struct
from typing import Dict, List, NamedTuple, Set

from . import game, kits, npcitems, pickpocket, ring, weaponchoice
from .game import GameData


class Arrow(NamedTuple):
    spell: int          # the game's spell (its record's number)
    spell_name: str
    name: int           # the arrows' name entry (DSCLOG's ARROW_NAMES)
    level: int          # the spell's level: the slot it takes


ARROWS = (
    Arrow(1, "Burning Hands", 0x16C, 1),
    Arrow(3, "Chill Touch", 0x16D, 1),
    Arrow(10, "Shocking Grasp", 0x16E, 1),
    Arrow(39, "Vampiric Touch", 0x16F, 3),
)
NAMES = {0x16C: b"Burning Arrows", 0x16D: b"Chill Arrows", 0x16E: b"Shocking Arrows", 0x16F: b"Vampiric Arrows"}
ARROW_NAMES = {a.name for a in ARROWS}
# their pictures (icons.py: the game's Arrows', tinted for each spell), objects 2614-2621
PICTURES = {0x16C: 0x10000 - 2614, 0x16D: 0x10000 - 2616, 0x16E: 0x10000 - 2618, 0x16F: 0x10000 - 2620}
ARROWS_PER_LEVEL = 5
ARROWS_TYPE = weaponchoice.ARROWS[1]  # (the game's Arrows)
TEMPLATE = npcitems._item("0cfc000000002d000000510000000000" "04ff1c0000")  # (worldgear's)
ARROWS_DROP = 3         # USE_TAKEN: PICK_TEXT holds an item record for DSCLOG's ARROWS_DROP
ARROWS_BY = 0xFE00      # USE_ITEM for an arrow button's click (DSCLOG's ARROWS_BY): the member its low byte
KNOWN_FROM_DS, KNOWN_OFF, KNOWN_STRIDE = 0x4356 - 0x3800, 0x168, 0x8A  # (DSCLOG's KNOWN_*)
REST_REQUESTS = (0, 1, 4)  # a REQUEST that rests the party (dicelog.REQUEST_NAMES; 0 the game's rest, DSCLOG's REST_SITE)
NOT_IN_A_FIGHT = "Spell arrows can't be made in a fight."


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


def is_spellarcher(gd: GameData, member: int) -> bool:
    rec = gd.creature(member)
    return (len(rec) >= game.CREATURE_SIZE and bool(rec[game.CREATURE_NAME])
            and kits.SPELLARCHER in gd.kit_ids(member))


def knows(gd: GameData, member: int, spell: int) -> bool:
    at = (gd.ds - KNOWN_FROM_DS) * 16 + KNOWN_OFF + member * KNOWN_STRIDE + spell
    return gd.guest.read(at, 1)[0] & 0x0F != 0


def slots_left(gd: GameData, member: int, level: int) -> int:
    return gd.guest.read(gd.ds * 16 + game.SLOTS_LEFT["Wizard"] + member * game.SLOTS_STRIDE + level, 1)[0]


class SpellArrows:
    def make(self, gd: GameData, member: int, row: int) -> "pickpocket.Attempt":
        """Party member MEMBER's button for ARROWS[ROW]: a slot used, the arrows in its backpack, or on
        the ground at the party's feet when there's no room (no text: the game shows none), or why
        not."""
        if not 0 <= row < len(ARROWS) or not 0 <= member < game.PARTY_SIZE:
            return pickpocket.Attempt("No spell arrows can be made now.", [])
        arrow = ARROWS[row]
        who = gd.creature_name(member)
        if not is_spellarcher(gd, member) or not knows(gd, member, arrow.spell):
            return pickpocket.Attempt(f"{who} can't weave {arrow.spell_name} into arrows.", [])
        if slots_left(gd, member, arrow.level) <= 0:
            return pickpocket.Attempt(f"{who} has no {_nth(arrow.level)}-level spell left for "
                                      f"{arrow.spell_name}'s arrows.", [])
        level = gd.class_level(member, game.PRESERVER)
        count = ARROWS_PER_LEVEL * max(level, 1)
        item = arrows_item(arrow, count)
        carried = npcitems.add_to(gd, member, item)
        at = gd.ds * 16 + game.SLOTS_LEFT["Wizard"] + member * game.SLOTS_STRIDE + arrow.level
        gd.guest.write(at, bytes((slots_left(gd, member, arrow.level) - 1,)))
        name = NAMES[arrow.name].decode().lower()
        log = f"{who} makes {count} {name} ({ARROWS_PER_LEVEL} a preserver level, {level}): a " \
              f"{_nth(arrow.level)}-level slot used; each casts {arrow.spell_name} on what it hits; " \
              f"they fade at the next rest"
        if not carried:  # (DSCLOG leaves them on the ground, at the party's feet)
            return pickpocket.Attempt("", [log + "; no room in the backpack: left on the ground"], drop=item)
        return pickpocket.Attempt("", [log])  # (no window: only a refusal is shown)

    def rest(self, gd: GameData) -> List[str]:
        """The party rested: every spell arrow fades."""
        return vanish(gd)


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
