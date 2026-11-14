"""The Spellarcher's spell arrows (kits.py: the half-elf fighter/preserver's kit).

Outside a fight, the USE screen gives a Spellarcher a button for each touch spell it knows (Burning
Hands, Chill Touch and Shocking Grasp at 1st level, Vampiric Touch at 3rd), with Turn Undead's and
Pick Pockets' (DSCLOG's PP_SHOW: in Turn Undead's place when no priest's element has it, then the
slots beside it). Pressed, it comes here as an item used on the map does (dicelog's _answer_use:
USE_ITEM ARROWS_BY and the member, USE_WHO the spell's place in ARROWS): a slot of that spell's
level is used up for ARROWS_A_SLOT arrow, as the Complete Book of Elves's Spellarcher casts one
spell onto one arrow. The Spellarcher keeps one stack of each spell's arrows, of STACK_MOST at
most: the arrow joins that spell's stack wherever it is (the quiver or the pack); with none, a new
stack goes in the quiver if it is empty, else in the pack. A full stack takes no more (no slot
used). The arrows are worth nothing (no merchant pays for them), last until shot (no fading at a
rest), may be readied and put away as any arrows, and only a Spellarcher may carry them: DSCLOG's
ARROWS_FORBID keeps anyone else from readying them, and as the game asks nothing of an item put in
a backpack, those another member is found carrying go back to the party's Spellarcher
(`return_strays`).

An arrow casts its spell on what it hits, shot from a bow (DSCLOG's ARROW_HIT: the game casts only
a bow's own spell; the arrow's, told by its name, takes its place), at the archer's caster level as
the game reckons it for that spell: the Spellarcher's preserver level.
"""

import struct
from typing import List, NamedTuple

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
ARROWS_A_SLOT = 1     # an arrow for each slot used
STACK_MOST = 24       # a spell's stack, at most
ARROWS_TYPE = weaponchoice.ARROWS[1]  # (the game's Arrows)
TEMPLATE = npcitems._item("0cfc000000002d000000510000000000" "04ff1c0000")  # (worldgear's)
ARROWS_BY = 0xFE00      # USE_ITEM for an arrow button's click (DSCLOG's ARROWS_BY): the member its low byte
KNOWN_FROM_DS, KNOWN_OFF, KNOWN_STRIDE = 0x4356 - 0x3800, 0x168, 0x8A  # (DSCLOG's KNOWN_*)
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


def item_address(gd: GameData, index: int) -> int:
    """Where item INDEX's record is in the guest's memory."""
    return game.far_pointer(gd.guest, gd.ds, game.ITEMS_PTR) + index * game.ITEM_SIZE


def is_spellarcher(gd: GameData, member: int) -> bool:
    rec = gd.creature(member)
    return (len(rec) >= game.CREATURE_SIZE and bool(rec[game.CREATURE_NAME])
            and kits.SPELLARCHER in gd.kit_ids(member))


def knows(gd: GameData, member: int, spell: int) -> bool:
    at = (gd.ds - KNOWN_FROM_DS) * 16 + KNOWN_OFF + member * KNOWN_STRIDE + spell
    return gd.guest.read(at, 1)[0] & 0x0F != 0


def slots_left(gd: GameData, member: int, level: int) -> int:
    return gd.guest.read(gd.ds * 16 + game.SLOTS_LEFT["Wizard"] + member * game.SLOTS_STRIDE + level, 1)[0]


CAST_SOUND = 0x0F  # a spell record's byte: the sound that goes with its cast glow


def cast_sound(gd: GameData, row: int) -> int:
    """The game's sound for ARROWS[ROW]'s spell as it is cast (0: none), played as the arrows are made."""
    if not 0 <= row < len(ARROWS):
        return 0
    rec = gd.spell_record(ARROWS[row].spell)
    return rec[CAST_SOUND] if len(rec) > CAST_SOUND else 0


class SpellArrows:
    def make(self, gd: GameData, member: int, row: int) -> "pickpocket.Attempt":
        """Party member MEMBER's button for ARROWS[ROW]: a slot used for an arrow, on the spell's stack
        or a new one (no text: the game shows none), or why not."""
        if not 0 <= row < len(ARROWS) or not 0 <= member < game.PARTY_SIZE:
            return pickpocket.Attempt("No spell arrows can be made now.", [])
        arrow = ARROWS[row]
        who = gd.creature_name(member)
        if not is_spellarcher(gd, member) or not knows(gd, member, arrow.spell):
            return pickpocket.Attempt(f"{who} can't weave {arrow.spell_name} into arrows.", [])
        if gd.no_spells(member):  # (a multiclass preserver in armour casts nothing: restrict.no_spells)
            return pickpocket.Attempt(f"{who} can't weave spell arrows in armour.", [])
        name = NAMES[arrow.name].decode().lower()
        stack = next(((index, item) for index, item, _ in gd._worn(member)
                      if struct.unpack_from("<H", item, game.ITEM_NAME)[0] == arrow.name), None)
        had = struct.unpack_from("<H", stack[1], weaponchoice.ITEM_COUNT)[0] if stack is not None else 0
        if had + ARROWS_A_SLOT > STACK_MOST:
            return pickpocket.Attempt(f"{who}'s {name} are a full stack ({STACK_MOST}).", [])
        if slots_left(gd, member, arrow.level) <= 0:
            return pickpocket.Attempt(f"{who} has no {_nth(arrow.level)}-level spell left for "
                                      f"{arrow.spell_name}'s arrows.", [])
        where = ""
        if stack is not None:  # (the spell's own stack, wherever it is)
            gd.guest.write(item_address(gd, stack[0]) + weaponchoice.ITEM_COUNT,
                           struct.pack("<H", had + ARROWS_A_SLOT))
        else:
            empty = not any(item[game.ITEM_SLOT] == weaponchoice.AMMO_SLOT for _, item, _ in gd._worn(member))
            if not npcitems.add_to(gd, member, arrows_item(arrow, ARROWS_A_SLOT),
                                   weaponchoice.AMMO_SLOT if empty else None):
                return pickpocket.Attempt("No spell arrows can be made now.", [])
            if empty:
                weaponchoice.bow_ahead(gd, member)
            where = " in the quiver" if empty else " in the pack"
        at = gd.ds * 16 + game.SLOTS_LEFT["Wizard"] + member * game.SLOTS_STRIDE + arrow.level
        gd.guest.write(at, bytes((slots_left(gd, member, arrow.level) - 1,)))
        total = had + ARROWS_A_SLOT
        log = f"{who} makes one of the {name}{where} ({total} of {STACK_MOST} now): a " \
              f"{_nth(arrow.level)}-level slot used; it casts {arrow.spell_name} on what it hits, " \
              f"and lasts until shot"
        return pickpocket.Attempt("", [log])  # (no window: only a refusal is shown)


def _nth(level: int) -> str:
    return {1: "1st", 2: "2nd", 3: "3rd"}.get(level, f"{level}th")


INVENTORY_SLOTS = 0x540C  # DS: the inventory screen's slot table, a far pointer (null with no inventory up)


def inventory_up(gd: GameData) -> bool:
    """Whether the game's inventory screen is up (it writes its copy of the items back as it shuts)."""
    return gd.guest.read(gd.ds * 16 + INVENTORY_SLOTS, 4) != bytes(4)


def return_strays(gd: GameData) -> List[str]:
    """Spell arrows a party member who isn't a Spellarcher carries (the game asks nothing of an item
    put in a backpack) go back to the party's Spellarcher: onto its stack of that spell where the two
    come to STACK_MOST or fewer, else into its pack as they are. Out of fights, the inventory shut;
    left where they are with no Spellarcher in the party, or no room in its pack. Lines for the log."""
    if gd.in_combat() or inventory_up(gd):
        return []
    archers = [m for m in range(game.PARTY_SIZE) if is_spellarcher(gd, m)]
    if not archers:
        return []
    to, out = archers[0], []
    for member in range(game.PARTY_SIZE):
        if member in archers or len(gd.creature(member)) < game.CREATURE_SIZE:
            continue
        for index, rec, _ in list(gd._worn(member)):
            if not is_arrow(rec):
                continue
            name = struct.unpack_from("<H", rec, game.ITEM_NAME)[0]
            count = struct.unpack_from("<H", rec, weaponchoice.ITEM_COUNT)[0]
            label = NAMES.get(name, b"spell arrows").decode().lower()
            stack = next(((i, item) for i, item, _ in gd._worn(to)
                          if struct.unpack_from("<H", item, game.ITEM_NAME)[0] == name), None)
            had = struct.unpack_from("<H", stack[1], weaponchoice.ITEM_COUNT)[0] if stack is not None else 0
            if stack is not None and had + count <= STACK_MOST:
                if not ring.unlink(gd, ring.Items(gd), index, "spell arrows back to the Spellarcher", empty=True):
                    continue
                gd.guest.write(item_address(gd, stack[0]) + weaponchoice.ITEM_COUNT, struct.pack("<H", had + count))
            elif npcitems.add_to(gd, to, bytes(rec)):
                ring.unlink(gd, ring.Items(gd), index, "spell arrows back to the Spellarcher", empty=True)
            else:
                continue
            out.append(f"The {label} go back to {gd.creature_name(to)} from {gd.creature_name(member)}: "
                       f"only a Spellarcher carries them ({count})")
    return out
