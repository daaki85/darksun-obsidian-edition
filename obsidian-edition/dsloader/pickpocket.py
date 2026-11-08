"""Picking pockets: a thief's Pick Pockets button, then someone clicked on.

The game has one pickpocket of its own, the Trustee's key in the slave pens, in his script.
With the dice log's patched game, a character with thief levels has a Pick Pockets button on
the USE screen, where a priest's Turn Undead is, outside fights (a cleric/thief has it beside
Turn Undead). Pressed, the screen closes and the pointer is the one for talking; the next
person it is clicked on (DSCLOG's PP_HAND, instead of the conversation) has the Loader roll that
thief's pick pockets chance as it stands now (thief_skills_now). On a success the
thief lifts one small thing (weight 10 or less, and nothing worn on the body) from the
person into the backpack. On a failure, a move silently roll decides whether they got away
unnoticed. With nothing else on them, the thief takes coins (party money: 2 to 5 for each thief level), and that is
the last try on them. A thief can go on trying the same person until caught (both rolls
failed) or until they take the coins; after that, their pockets are out of reach.

Lifting Kurzak's Short Sword (npcitems.py), Churrr's Gutterknot or Maris's Mindshard (worldgear.py) is worth SWORD_XP
to the thief, given as the game gives
a quest's XP to one person ("Cilla receives 200 experience points!", and the quest's sound): the
Loader has DSCLOG call the game's own routine for it, which also sees to a level gained.
"""

import random
import struct
from dataclasses import dataclass
from typing import Callable, List, Optional, Tuple

from . import game, itemgate, restrict, ring
from .game import GameData

PICK_POCKETS, MOVE_SILENTLY = 0, 3  # thief skill numbers
BACKPACK = range(14, 26)  # the backpack's 12 cells, as the inventory screen shows them (0-13: the body's)
# A party member's items are in three lists: what it wears in the +08h one (armour, a shield,
# rings, a cloak, ammunition: whatever is on the body and isn't a weapon), the weapons it holds in
# the +0Ah one, and its backpack in the +0Ch one. The inventory screen moves an item from one to
# another as it's put on or away, by its type's kind (+00h): a melee, missile or thrown weapon to
# +0Ah, anything else to +08h (seen 2026-11-02: chest and leg armour, a shield in the left hand
# and arrows went to +08h; a long sword, a gythka and a bow to +0Ah). The game fights with every
# weapon in the +0Ah list whatever its slot byte says, and its AC routine (58DD3h) counts only
# what is in the +08h one (armour in +0Ah or +0Ch counts for nothing), so the Loader puts what
# it gives and moves in the list the screen would (list_for, party_list, place).
WEAR_LIST, HOLD_LIST, PACK_LIST = 0x08, 0x0A, 0x0C
WEAPON_KINDS = restrict.MELEE | restrict.MISSILE | restrict.THROWN
TYPE_WEIGHT, TYPE_WORN = 0x04, 0x09  # in an item type's record: its weight; where it's worn
LIFTABLE_TYPES = (game.SHORT_SWORD_TYPE,)  # lifted whatever their weight: Kurzak's short sword
# ... and these by their name entry, with what the conversation says was lifted: Churrr's club
# (worldgear.GUTTERKNOT), Maris's short sword (worldgear.MINDSHARD)
LIFTABLE_NAMES = {0x14A: "a knotted club", 0x15D: "an obsidian short sword"}
MAX_WEIGHT = 10  # a bag, a quiver of arrows: pocket-sized (a long sword is 30, a helm 15)
# where on the body (TYPE_WORN) things can't be lifted from: chest, belt, arms, feet, head,
# cloak, legs (a pair of boots weighs 1). Hands (a dagger), fingers, neck and ammunition can.
ON_THE_BODY = (0x01, 0x02, 0x03, 0x04, 0x06, 0x08, 0x0A)
SCENERY = 0x60  # in its +08h: doors, haystacks, walls...
OWN_POCKETS = ("Trustee",)  # people whose script has its own pickpocket
SWORD_XP = 200  # for lifting Kurzak's Short Sword, Churrr's club or Maris's Mindshard
SWORD_SEEN = "a metal short sword"  # what the conversation says was lifted
MAX_ITEMS = 200
NOT_IN_A_FIGHT = "No time to pick pockets in the middle of a fight."


@dataclass
class Attempt:
    text: str  # for the game's dialogue window
    log: List[str]  # for the dice log
    key: Optional[str] = None  # the person's pockets, now out of reach (the thief was caught)
    xp_to: Optional[int] = None  # a party member given XP for what was lifted (the game's routine)
    xp: int = 0
    lifted: bool = False  # something (or the coins) taken: the purse's sound (sounds.PICK_SOUND)
    paid: Optional[str] = None  # SWORD_XP given for this weapon: remembered with the tries, once a game


def _seen(data: bytes) -> Optional[str]:
    """What the conversation says of a thing lifted whatever its weight, worth SWORD_XP (None: an
    ordinary thing)."""
    if struct.unpack_from("<H", data, game.ITEM_TYPE)[0] in LIFTABLE_TYPES:
        return SWORD_SEEN
    return LIFTABLE_NAMES.get(struct.unpack_from("<H", data, game.ITEM_NAME)[0])


def thief_level(gd: GameData, member: int) -> int:
    """MEMBER's level in the thief class (at least 1)."""
    sheet = gd.sheet(member)
    for i in range(3):
        if len(sheet) > game.SHEET_LEVELS + i and sheet[game.SHEET_CLASSES + i] == game.THIEF:
            return max(1, sheet[game.SHEET_LEVELS + i])
    return 1


def _skill(gd: GameData, member: int, name: str) -> Optional[int]:
    return next((n for skill, n in gd.thief_skills_now(member) if skill == name), None)


def _chain(it: ring.Items, thing: int) -> List[Tuple[int, bytes]]:
    """The item numbers and records of one list (not what's inside containers)."""
    return list(it.chain(thing, inside=False))


def _carried(gd: GameData, it: ring.Items, creature: int) -> List[Tuple[int, int, int]]:
    """What a thief can lift from a creature: (list, item, the item before it or -1), from any of
    its lists (people outside the party carry their gear in the backpack's, worn and held once
    put on: people.py), so it goes by the item's type: MAX_WEIGHT or less, nothing worn ON_THE_BODY, no keys (scripts
    may need them) and no scenery."""
    rec = gd.creature(creature)
    out = []
    for list_no, offset in enumerate(game.CREATURE_ITEM_LISTS):
        thing, = struct.unpack_from("<h", rec, offset)
        before = -1
        for item, data in _chain(it, thing):
            typ = gd.item_type_record(data)
            name = gd.item_name(struct.unpack_from("<H", data, game.ITEM_NAME)[0])
            liftable = _seen(data) is not None
            if len(typ) == game.ITEM_TYPE_SIZE and typ[TYPE_WORN] not in ON_THE_BODY \
                    and (struct.unpack_from("<H", typ, TYPE_WEIGHT)[0] <= MAX_WEIGHT or liftable) \
                    and typ[0x08] & SCENERY != SCENERY and "key" not in name.lower():
                out.append((list_no, item, before))
            before = item
    return out


def free_cell(gd: GameData, it: ring.Items, member: int) -> Optional[int]:
    used = set()
    rec = gd.creature(member)
    for offset in game.CREATURE_ITEM_LISTS:
        thing, = struct.unpack_from("<h", rec, offset)
        used.update(data[game.ITEM_SLOT] for _, data in _chain(it, thing))
    return next((cell for cell in BACKPACK if cell not in used), None)


def _take(gd: GameData, it: ring.Items, creature: int, list_no: int, item: int, before: int) -> None:
    """Unlink ITEM from the creature's list (freeing the list's object if it was the only one)."""
    ds = gd.ds * 16
    offset = game.CREATURE_ITEM_LISTS[list_no]
    base = game.far_pointer(gd.guest, gd.ds, game.CREATURES_PTR) + creature * game.CREATURE_SIZE
    thing, = struct.unpack_from("<h", gd.creature(creature), offset)
    after = it.item(item)[game.ITEM_NEXT:game.ITEM_NEXT + 2]
    if before >= 0:
        gd.guest.write(it.items + before * game.ITEM_SIZE + game.ITEM_NEXT, after)
    elif struct.unpack("<h", after)[0] >= 0 and struct.unpack("<H", after)[0] != game.NO_ITEM:
        gd.guest.write(it.things + thing * 3 + 1, after)  # the list now starts at the next one
    else:  # it was all the list held: the list's object goes back on the free list
        gd.guest.write(it.things + thing * 3, struct.pack("<BH", 0, it.word(ring.FREE_THINGS)))
        gd.guest.write(ds + ring.FREE_THINGS, struct.pack("<H", thing))
        gd.guest.write(ds + ring.THINGS_USED, struct.pack("<H", max(0, it.word(ring.THINGS_USED) - 1)))
        gd.guest.write(base + offset, struct.pack("<H", game.NO_ITEM))


def list_for(slot: int, typ: bytes) -> int:
    """The list (its offset in the creature record) the inventory screen keeps an item of type
    record TYP in SLOT in: the backpack's for a cell; for a slot of the body, the held one for a
    weapon, else the worn one."""
    if slot in BACKPACK:
        return PACK_LIST
    return HOLD_LIST if typ and typ[0] & WEAPON_KINDS else WEAR_LIST


def party_list(gd: GameData, it: ring.Items, member: int, slot: int, typ: bytes = b"") -> Optional[int]:
    """The list (its object) that party member MEMBER keeps an item of type record TYP in SLOT
    in (list_for); a new one, as the game's allocator gives it, if it has none. None if there's
    none to be had."""
    offset = list_for(slot, typ)
    thing, = struct.unpack_from("<h", gd.creature(member), offset)
    if 0 <= thing < ring.THING_COUNT and it.thing(thing)[0] == game.THING_ITEM:
        return thing
    if thing != game.NO_ITEM:
        return None
    free = it.word(ring.FREE_THINGS)
    if free >= ring.THING_COUNT or not it.spare_things():  # (the game's own left some: ring.RESERVE)
        return None
    ds = gd.ds * 16
    gd.guest.write(ds + ring.FREE_THINGS, struct.pack("<H", it.thing(free)[1] & 0xFFFF))
    gd.guest.write(ds + ring.THINGS_USED, struct.pack("<H", it.word(ring.THINGS_USED) + 1))
    gd.guest.write(it.things + free * 3, struct.pack("<BH", game.THING_ITEM, game.NO_ITEM))
    base = game.far_pointer(gd.guest, gd.ds, game.CREATURES_PTR) + member * game.CREATURE_SIZE
    gd.guest.write(base + offset, struct.pack("<H", free))
    return free


def _link(gd: GameData, it: ring.Items, member: int, item: int, slot: int) -> bool:
    """ITEM (in no list) put first in the party member's list for SLOT and its kind, in SLOT."""
    data = it.item(item)
    typ = gd.item_type_record(data) if struct.unpack_from("<H", data, game.ITEM_TYPE)[0] < game.NO_ITEM else b""
    thing = party_list(gd, it, member, slot, typ)
    if thing is None:
        return False
    it = ring.Items(gd)  # (read again: the list may be new)
    at = it.items + item * game.ITEM_SIZE
    gd.guest.write(at + game.ITEM_SLOT, bytes((slot,)))
    gd.guest.write(at + game.ITEM_NEXT, struct.pack("<h", it.thing(thing)[1]))
    gd.guest.write(it.things + thing * 3 + 1, struct.pack("<h", item))
    from . import icons
    icons.fit(gd, item)  # (the Loader's own icon at once: the arena's ring)
    return True


def place(gd: GameData, member: int, item: int, slot: int) -> bool:
    """One of the party member's items put in SLOT (a slot of the body or a backpack cell) and
    into the list that goes with it, as the inventory screen would: a weapon put away in the
    backpack is no longer fought with, one taken from it is. Nothing moves (False) if there is no
    list to be had for it: the list is found or made first, then the item taken out of its own
    (taken out first, it was in no list when the game's things had none left, and lost)."""
    it = ring.Items(gd)
    rec = gd.creature(member)
    for list_no, offset in enumerate(game.CREATURE_ITEM_LISTS):
        thing, = struct.unpack_from("<h", rec, offset)
        before = -1
        for index, data in _chain(it, thing):
            if index == item:
                typ = gd.item_type_record(data) if struct.unpack_from("<H", data, game.ITEM_TYPE)[0] < game.NO_ITEM else b""
                if party_list(gd, it, member, slot, typ) is None:
                    return False
                it = ring.Items(gd)  # (read again: the list may be new)
                _take(gd, it, member, list_no, item, before)
                return _link(gd, ring.Items(gd), member, item, slot)
            before = index
    return False


def mend_lists(gd: GameData) -> List[str]:
    """What earlier versions left in the held list put where the inventory screen keeps it:
    lines for the log. A backpack item goes to the backpack's list (they gave the backpack's
    dagger, Thieves' Tools and such to the held list, where a weapon is fought with); something
    worn that isn't a weapon to the worn list (they gave starting armour, a cloak, a shield, a
    ring to the held list, where it counted for no AC; arrows given with a bow, swapped into the
    held list by an earlier bow_ahead); a weapon in the worn list to the held one (that swap's bow,
    which the game didn't shoot with until it was put on again). Nothing else: a worn item in the
    backpack's list is left as the game has it."""
    out: List[str] = []
    for member in range(game.PARTY_SIZE):
        rec = gd.creature(member)
        if len(rec) < game.CREATURE_SIZE or not rec[game.CREATURE_NAME]:
            continue
        wrong = []
        for offset in (HOLD_LIST, WEAR_LIST):
            thing, = struct.unpack_from("<h", rec, offset)
            for item, data in _chain(ring.Items(gd), thing):
                slot = data[game.ITEM_SLOT]
                typ = gd.item_type_record(data) if struct.unpack_from("<H", data, game.ITEM_TYPE)[0] < game.NO_ITEM else b""
                if offset == HOLD_LIST and (slot in BACKPACK or (len(typ) == game.ITEM_TYPE_SIZE
                                                                 and list_for(slot, typ) == WEAR_LIST)):
                    wrong.append((item, data, typ))
                elif offset == WEAR_LIST and slot not in BACKPACK and len(typ) == game.ITEM_TYPE_SIZE \
                        and list_for(slot, typ) == HOLD_LIST:
                    wrong.append((item, data, typ))
        for item, data, typ in wrong:
            if place(gd, member, item, data[game.ITEM_SLOT]):
                name = gd.item_name(struct.unpack_from("<H", data, game.ITEM_NAME)[0])
                who = gd.creature_name(member)
                if data[game.ITEM_SLOT] in BACKPACK:
                    out.append(f"{who}'s {name} is put away in the backpack (it had been counted as held)")
                elif list_for(data[game.ITEM_SLOT], typ) == HOLD_LIST:
                    out.append(f"{who}'s {name} is now held, ready to use (it had been counted as worn)")
                elif restrict.is_armour(typ) or restrict.is_shield(typ):
                    out.append(f"{who}'s {name} is now counted as worn (it had been counted as held, and gave no AC)")
                else:
                    out.append(f"{who}'s {name} is now counted as worn (it had been counted as held)")
    return out


def give(gd: GameData, it: ring.Items, member: int, item: int, cell: int) -> bool:
    """Put ITEM (in no list) first in the party member's backpack list, in backpack cell CELL."""
    return _link(gd, it, member, item, cell)


COINS = (2, 5)  # ceramic pieces in a purse with nothing else worth taking, for each of the thief's levels


def attempt(gd: GameData, tried: set, roll: Callable[[], int] = lambda: random.randint(1, 100),
            coin_roll: Callable[[], int] = lambda: random.randint(*COINS),
            who: Optional[int] = None, thief: Optional[int] = None) -> Optional[Attempt]:
    """Party member THIEF (the one whose Pick Pockets button was pressed; not given, the leader)
    tries the pocket of creature WHO (clicked on), or of whoever is talked to (WHO not given). None
    when there's no one to rob (a narration, someone in the party, a dead body)."""
    if who is None:
        who = gd.talk_target_creature()
    elif not gd.living_npc(who):
        return None
    if who is None:
        return None
    npc = gd.creature_name(who)
    leader = gd.whose_turn() if thief is None else thief
    if leader is None or not 0 <= leader < game.PARTY_SIZE:  # (no one's turn: between areas)
        return None
    thief = gd.creature_name(leader)
    chance = _skill(gd, leader, "pick pockets")
    if chance is None:
        return Attempt(f"{thief} is no thief.", [])
    if npc in OWN_POCKETS:
        return Attempt(f"(Try the {npc}'s pocket with what you say to him.)", [])
    key = f"{gd.creature_name(0)}|{gd.region()}|{who}|{npc}"  # (the party's first name: another game's)
    if key in tried:
        return Attempt(f"{npc} keeps a close hand on their purse now: {thief} won't get another chance.", [])
    it = ring.Items(gd)
    cell = free_cell(gd, it, leader)
    if cell is None:
        return Attempt(f"{thief}'s backpack is full.", [])
    itemgate.hold(gd)  # (before the roll: the game busy with its lists, the try waits for the next look)
    d100 = roll()
    lines = [f"{thief} picks {npc}'s pocket: d100 = {d100}, needs {chance} or less -> "
             + ("success" if d100 <= chance else "failed")]
    if d100 <= chance:
        loot = _carried(gd, it, who)
        if not loot:  # nothing else: coins, 2 to 5 for each thief level, and that was the last try on them
            level = thief_level(gd, leader)
            rolls = [coin_roll() for _ in range(level)]
            coins = sum(rolls)
            gd.add_money(coins)
            text = f"{thief} lifts {coins} ceramic pieces from {npc}'s purse, all there was to take."
            lines.append(f"  coins: {level}d4+{level} (2 to 5 for each of {level} thief levels) = {coins}")
            lines.append("  " + text)
            return Attempt(text, lines, key, lifted=True)
        else:
            list_no, item, before = random.choice(loot)
            data = it.item(item)
            name = gd.item_label(data, gd.item_type_record(data))
            if party_list(gd, it, leader, cell) is None:  # (the thief's backpack list first: the item is
                return Attempt(f"{thief} can't take anything now.", lines)  #   never left in no list)
            _take(gd, it, who, list_no, item, before)
            if not give(gd, ring.Items(gd), leader, item, cell):
                return Attempt(f"{thief} can't take anything now.", lines)
            text = f"{thief} lifts {name} from {npc} unnoticed."
            special = _seen(data)
            # (paid once a game: a weapon sold and lifted back again is worth nothing more)
            paid = f"{gd.creature_name(0)}|paid|{special}" if special is not None else None
            if special is not None and paid not in tried:  # Kurzak's sword, Churrr's club, Maris's Mindshard
                # (what it is, Shadowseeker, Gutterknot or Mindshard, is for the inventory screen to show: the log says)
                seen = f"{thief} lifts {special} from {npc} unnoticed."
                reward = f"{thief} receives {SWORD_XP} experience points!"
                lines += ["  " + text, "  " + reward]
                return Attempt(f"{seen} {reward}", lines, xp_to=leader, xp=SWORD_XP, lifted=True, paid=paid)
        lines.append("  " + text)
        return Attempt(text, lines, lifted=True)  # free to try again
    quiet = _skill(gd, leader, "move silently") or 0
    d100 = roll()
    lines.append(f"  {thief} moves silently to get away: d100 = {d100}, needs {quiet} or less -> "
                 + ("success" if d100 <= quiet else "failed"))
    if d100 <= quiet:
        text = f"{thief} fumbles {npc}'s pockets, but slips away unnoticed."
        lines.append("  " + text)
        return Attempt(text, lines)  # free to try again
    text = f"{npc} catches {thief}'s hand! {npc} will be too wary for {thief} to try again."
    lines.append("  " + text)
    return Attempt(text, lines, key)
