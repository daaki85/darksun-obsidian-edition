"""Hiding in shadows and moving silently in a fight (RULE_STEALTH): a way to backstab.

The game never rolls hide in shadows, and a backstab needs the thief to stand behind a target
that has turned to face someone else. With the rule on, a thief whose turn comes with no enemy
next to them tries to hide in shadows (the chance halved in daylight: on open ground under
Athas's sun; a Shadowblade even with an enemy beside them), and if they do, to move silently
up to someone. Both succeeding, the thief's next
attack this turn counts as one from behind (DSCLOG's PROBE_STEALTH), and so as a backstab with
a weapon that can backstab; attacking gives them away, and the turn ending ends the hiding.
Worn, a cloak adds CLOAK_HIDE to hiding in shadows and boots BOOTS_QUIET to moving silently
(at most MOST), before the light halves it.

The Cloak and Boots of Elvenkind (worldgear.py, worn by thieves and rangers only) do more: the
cloak makes its wearer all but invisible, ELVEN_HIDE_OUT under the open sky and ELVEN_HIDE_IN
under a roof, whatever the light (AD&D's: 95-100% in the wild, 90% among buildings, 95%
underground by torchlight), unless their own chance is better; the boots make them silent,
ELVEN_QUIET (AD&D's 95% in the worst conditions).

Rangers do it too, with AD&D's chances for a ranger (the game gives them no thief skills;
game.ranger_skill_parts), but the other way round for the light: outdoorsmen, they hide with
the full chance under the open sky and half of it indoors (a Stalker, kits.py, the full chance
indoors too). Their attack from behind is no
backstab (DSCLOG's own check keeps that to thieves). Someone with thief levels hides as a thief.

Daylight goes by the region (the map) the party is in: open desert, rock and the arena are
outdoors; the slave pens, the sewers, the caverns and the other underground or roofed places
are not. A few maps have both: buildings with floors of their own on open ground. There, it
goes by the floor under the thief: the game's map of the region (its RMAP, one tile number a
square) says which, and the tile numbers of those maps' indoor floors are below.
"""

import struct
from typing import Callable, List, Optional, Tuple

from . import game, kits
from .game import GameData

HIDE, MOVE = 4, 3  # thief skill numbers (game.THIEF_SKILLS)
# Regions (RGNxx.GFF) by their maps: open ground, and maps with buildings on open ground (each
# with the tile numbers of its indoor floors); every other map is underground or roofed
OUTDOORS = frozenset((0x02, 0x04, 0x05, 0x07, 0x08, 0x09, 0x0A, 0x0F, 0x12, 0x14, 0x1A, 0x1D, 0x1F,
                      0x21, 0x22, 0x23, 0x2A, 0xFF))
INDOOR_TILES = {
    0x03: frozenset((163, 164, 165, 166, 168, 169, 170, 171, 179, 182, 183, 185, 186, 187, 188, 190, 191,
                     192, 193, 194, 195, 198, 199, 200, 201, 202, 204, 205, 206, 207)),
    0x0B: frozenset((66, 70, 71, 72, 73, 74, 75, 76, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91,
                     92, 93, 97, 98, 99, 100, 101, 105, 106, 107, 108, 109, 110, 112, 113, 121, 122, 123,
                     125, 139, 140, 162, 168, 189, 190, 191, 192, 193, 194)),
    0x0D: frozenset((13, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 45, 46, 47,
                     48, 54, 55, 57, 58, 60, 61, 62, 63, 64, 65, 66, 67, 69, 76, 77, 78, 79, 81, 87, 143,
                     144, 145, 146, 147)),
}
MAP_PTR = 0x2F4A  # DS: far pointer to the region's map: a tile number a square, MAP_WIDTH to a row
MAP_WIDTH, MAP_HEIGHT = 128, 98
POSITIONS, POSITION_SIZE = 0x669D, 32  # DS: each object's x, y, in 16ths of a square
TSR_STEALTH, TSR_STEALTH_USED = 204, 206  # in DSCLOG's header
STATUS_GONE = (4, 5)  # Dying, Dead: no threat


def square(gd: GameData, combatant: int) -> Tuple[int, int]:
    x, y = struct.unpack("<HH", gd.guest.read(gd.ds * 16 + POSITIONS + combatant * POSITION_SIZE, 4))
    return x >> 4, y >> 4


def daylight(gd: GameData, combatant: int) -> bool:
    """The thief stands under the open sky: an outdoor map, or open ground on a map with
    buildings."""
    region = gd.region()
    if region in OUTDOORS:
        return True
    floors = INDOOR_TILES.get(region)
    if floors is None:
        return False
    x, y = square(gd, combatant)
    if not (0 <= x < MAP_WIDTH and 0 <= y < MAP_HEIGHT):
        return True
    tile = gd.guest.read(game.far_pointer(gd.guest, gd.ds, MAP_PTR) + y * MAP_WIDTH + x, 1)[0]
    return tile not in floors


def enemy_beside(gd: GameData, combatant: int) -> Optional[str]:
    """The name of an enemy standing next to the combatant (any of the eight squares around),
    if one is: someone up and about on another side."""
    me = gd.combatant_creature(combatant)
    if me is None:
        return None
    side = gd.creature(me)[game.CREATURE_SIDE]
    x, y = square(gd, combatant)
    for other, index in gd.combatants().items():
        if other == combatant:
            continue
        rec = gd.creature(index)
        if len(rec) < game.CREATURE_SIZE or rec[game.CREATURE_SIDE] == side:
            continue
        if struct.unpack_from("<h", rec, 0)[0] <= 0 or rec[game.CREATURE_STATUS] in STATUS_GONE:
            continue
        ox, oy = square(gd, other)
        if max(abs(ox - x), abs(oy - y)) <= 1:
            return gd.creature_name(index)
    return None


def chance(gd: GameData, creature: int, skill: int) -> Optional[int]:
    """A thief's chance before what it wears (turn adds that, and says so), at most MOST (even
    without RULE_THIEF_TABLE: these rolls are the rule's own)."""
    skills = gd.thief_skills_now(creature, (skill,), gear=False)
    return min(MOST, skills[0][1]) if skills else None


def ranger_chance(gd: GameData, creature: int, skill: int) -> Optional[int]:
    return gd.ranger_skill_now(creature, skill, gear=False)


CLOAK_HIDE, BOOTS_QUIET = 10, 10  # worn, a cloak helps hide in shadows and boots move silently
MOST = game.THIEF_MOST  # (AD&D's most for a thief skill)
ELVEN_HIDE_OUT, ELVEN_HIDE_IN, ELVEN_QUIET = 95, 90, 95  # the Cloak and Boots of Elvenkind
# what's worn as a cloak, on the feet and as a belt (an item type's +09h); the plain ones cost
# GEAR_VALUE while they help (the game's Leather Cloak is 20). Magic ones (a plus, or a price above
# PLAIN_MOST: the game's own magic gear) keep theirs; PLAIN_MOST takes in what an earlier version
# priced plain ones at (100)
WORN_CLOAK, WORN_FEET, WORN_BELT, TYPE_WORN = 8, 4, 2, 0x09
GEAR_VALUE, PLAIN_MOST, ITEM_VALUE = 24, 100, 0x06


def reprice(gd: GameData) -> int:
    """Plain cloaks, boots and belts anywhere in the region (carried, in a container, on the
    ground, in a shop) priced GEAR_VALUE. How many were changed."""
    from . import ring
    it = ring.Items(gd)
    done = set()
    for thing in range(ring.THING_COUNT):
        for index, rec in it.chain(thing):
            if index in done or len(rec) < game.ITEM_SIZE \
                    or struct.unpack_from("<H", rec, game.ITEM_TYPE)[0] >= game.GAME_TYPES + 8:
                continue  # (past the game's types and the Loader's: no type record)
            value, = struct.unpack_from("<H", rec, ITEM_VALUE)
            if gd.item_type_record(rec)[TYPE_WORN] in (WORN_CLOAK, WORN_FEET, WORN_BELT) \
                    and rec[game.ITEM_PLUS] == 0 and value <= PLAIN_MOST and value != GEAR_VALUE:
                gd.guest.write(it.items + index * game.ITEM_SIZE + ITEM_VALUE, struct.pack("<H", GEAR_VALUE))
                done.add(index)
    return len(done)


def worn_bonus(gd: GameData, creature: int, slot: int, bonus: int, name: str) -> Tuple[int, str]:
    """BONUS (and its note) when the character wears something in SLOT, else nothing."""
    if any(item[game.ITEM_SLOT] == slot for _, item, _ in gd._worn(creature)):
        return bonus, f" +{bonus} {name}"
    return 0, ""


def wears(gd: GameData, creature: int, type_: int, slot: int) -> bool:
    return any(item[game.ITEM_SLOT] == slot and struct.unpack_from("<H", item, game.ITEM_TYPE)[0] == type_
               for _, item, _ in gd._worn(creature))


def turn(gd: GameData, combatant: int, roll: Callable[[], int], gear: bool = True) -> Tuple[List[str], bool]:
    """A party member's turn has come in a fight: if a thief or a ranger, the hiding and moving
    silently, with a worn cloak's and boots' bonuses if GEAR.
    (log lines, whether their next attack is from behind)."""
    creature = gd.combatant_creature(combatant)
    if creature is None or creature >= game.PARTY_SIZE:
        return [], False
    hide = chance(gd, creature, HIDE)
    of = chance
    ranger = hide is None
    if ranger:
        hide, of = ranger_chance(gd, creature, HIDE), ranger_chance
    if hide is None:
        return [], False
    elven_cloak = wears(gd, creature, game.ELVEN_CLOAK_TYPE, game.CLOAK_SLOT)
    extra, note = worn_bonus(gd, creature, game.CLOAK_SLOT, CLOAK_HIDE, "cloak") \
        if gear and not elven_cloak else (0, "")
    shown = f"{hide}{note} = {max(hide, min(MOST, hide + extra))}" if extra else f"{hide}"
    hide = max(hide, min(MOST, hide + extra))  # (as gd.gear_skill)
    who = gd.creature_name(creature)
    enemy = enemy_beside(gd, combatant)
    if enemy and kits.SHADOWBLADE not in gd.kit_ids(creature):  # (a Shadowblade hides even so: kits.py)
        return [f"{who} can't hide in shadows: {enemy} is right beside them"], False
    sun = daylight(gd, combatant)
    if ranger and not sun and kits.STALKER in gd.kit_ids(creature):  # (kits.py: not halved indoors)
        need, why = hide, f"{shown}, a Stalker: not halved indoors"
    elif ranger:  # at home under the open sky (a Wilderness Avenger too: game.ranger_skill_parts)
        need = hide if sun else hide // 2
        kind = "a ranger" if gd.ranger_level(creature) else "a Wilderness Avenger"
        why = f"{shown}, {kind} under the open sky" if sun else f"{shown}, halved indoors for {kind}"
    elif sun and kits.not_halved_by_sun(gd.kit_ids(creature), gd.own_race(creature)):  # (kits.py)
        need, why = hide, f"{shown}, {kits.not_halved_by_sun(gd.kit_ids(creature), gd.own_race(creature))}: not halved in daylight"
    else:
        need = hide // 2 if sun else hide
        why = f"{shown}, halved in daylight" if sun else f"{shown}, out of the sun"
    elven = ELVEN_HIDE_OUT if sun else ELVEN_HIDE_IN
    if elven_cloak and elven > need:  # all but invisible, whatever the light
        need, why = elven, f"Cloak of Elvenkind, {'under the open sky' if sun else 'under a roof'}"
    if enemy:
        why += f"; a Shadowblade, with {enemy} beside them"
    d100 = roll()
    hidden = d100 <= need
    lines = [f"{who} hides in shadows: d100 = {d100}, needs {need} or less ({why}) -> "
             + ("hidden" if hidden else "seen")]
    if not hidden:
        return lines, False
    quiet = of(gd, creature, MOVE) or 0
    if wears(gd, creature, game.ELVEN_BOOTS_TYPE, game.FOOT):
        boots = " (Boots of Elvenkind)"
        quiet = max(quiet, ELVEN_QUIET)
    else:
        extra, note = worn_bonus(gd, creature, game.FOOT, BOOTS_QUIET, "boots") if gear else (0, "")
        boots = f" ({quiet}{note})" if extra else ""
        quiet = max(quiet, min(MOST, quiet + extra))
    d100 = roll()
    unheard = d100 <= quiet
    stabs = all(kits.backstabs(k) for k in gd.kit_ids(creature))  # (a Military Scout never backstabs)
    behind = "from behind" if ranger or not stabs else "from behind (a backstab with a weapon that can)"
    lines.append(f"  {who} moves silently: d100 = {d100}, needs {quiet}{boots} or less -> "
                 + (f"unheard: their next attack this turn is {behind}" if unheard else "heard"))
    return lines, unheard
