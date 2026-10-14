"""Items of the Loader's own on people in the slave pens.

- Kurzak, the leader of the guards: a metal Short Sword (Shadowseeker, a short sword +1, with the
  magic weapons' switch: arms.py; a thief can lift it) and a leather Helm.
- Legcrusher, the half-giant monster trainer: Inixhide, his Leather Chest Armor +1 (a name of its
  own, as the magic items Alagorn tells of have: alagorn.py).
- Pehtucl, the head templar (the Templar in the pens' south-west corner, who carries the
  Obsidian Bloodwrath): a Cloak of Protection +1 (+1 AC, +1 on saves) and a Ring of
  Protection +1 (a thief can lift it).

The game has no short sword, and no cloak whose plus counts, so those two have item types of
the Loader's own: DSCLOG adds TYPES after the game's 115 each time it reads its type table
in, as it adds names after its 322 (names.py). The items are in their people's objects in the
Loader's copy of SEGOBJEX (PENS: dataitems.py, worldgear.data_chunks), so the game makes the
three with them.
"""

import struct
from typing import List, Optional, Tuple

from . import game, pickpocket, ring
from .game import GameData

SHORT_SWORD, CLOAK, RING = 0x144, 0x145, 0x146  # name entries DSCLOG adds
INIXHIDE = 0x158  # (Legcrusher's leather)
# as DSCLOG's EXTRA_NAMES has them. Pehtucl's ring is named as the arena's, in an entry of its own
# so that each keeps its own icon (icons.py)
NAMES = {SHORT_SWORD: b"Short Sword", CLOAK: b"Cloak/Protectn", RING: ring.NAME, INIXHIDE: b"Inixhide"}
GAME_TYPES, SHORT_SWORD_TYPE, CLOAK_TYPE = game.GAME_TYPES, game.SHORT_SWORD_TYPE, game.CLOAK_TYPE
BONE_HELM_TYPE = game.BONE_HELM_TYPE
TYPES = (  # as DSCLOG's EXTRA_TYPES has them
    bytes.fromhex("010030001e00fa00040501010601000072160001"),  # the metal long sword's (63), 1d6
    bytes.fromhex("000000000a000a00400800000000008" "0ff1f0001"),  # the Cloak's (65): its plus counts for AC
    # the Helm's (5), of bone, worn by those who can wear the bone scale armour (+10h, the classes:
    # 126Fh, no thieves, where the Helm has 166Fh) (bonescale.py)
    bytes.fromhex("000000000f00fa0001060000000000806f120000"),
    # a bone short sword and a bone axe, a new warrior's (weaponchoice.py)
    bytes.fromhex("010030000f00fa0001050101060100007817" "0001"),
    bytes.fromhex("010010001e00fa0001050101080100007817" "0001"),
    # an obsidian short sword and an obsidian axe
    bytes.fromhex("010030001e00fa0003050101060100007e17" "0001"),
    bytes.fromhex("010010001e00fa0003050101080100007e17" "0001"),
    # a plain metal short sword (worldgear.py): the first's
    bytes.fromhex("010030001e00fa00040501010601000072160001"),
    # bracers of defense (bracers.py): the cloak of protection's, worn on the arms
    bytes.fromhex("000000000a000a00400300000000008" "0ff1f0001"),
    # metal versions (worldgear.py): the Dagger's, the Mace's, the Great Axe's, the pick's, the
    # Polearm's, of metal, for the metal long sword's clerics
    bytes.fromhex("010020000a00fa000405010104010000f21f0000"),
    bytes.fromhex("010008006400fa00040501010601010072160001"),
    bytes.fromhex("010010004600fa00040501010a01004062160002"),
    bytes.fromhex("010020002800fa00040501010401010072170000"),
    bytes.fromhex("010030009600fa00040501010a01004072160006"),
    # a circlet and a crown (worldgear.py): the Necklace's, worn on the head, not armour
    bytes.fromhex("000000000100fa00" "4006000000000000" "ff1f0000"),
    bytes.fromhex("000000000500fa00" "4006000000000000" "ff1f0000"),
    # plate mail's chest, arm and leg armour (worldgear.py): the Chain's, heavier, AC 3, 2, 2
    bytes.fromhex("00000000fa00fa00040100000000008" "06f120301"),
    bytes.fromhex("000000004b00fa00040300000000008" "06f120200"),
    bytes.fromhex("000000004b00fa00040a00000000008" "06f120200"),
    # the Cloak and Boots of Elvenkind (worldgear.py, stealth.py): the Cloak's (65), the Boots' (68),
    # for thieves and rangers (their class bits, 600h)
    bytes.fromhex("000000000a000a00050800000000000" "000060001"),
    bytes.fromhex("0000000001000a00850400000000000" "000060000"),
    # a metal dagger air clerics may use too (worldgear.py's Galefang): the metal Dagger's, its
    # classes' air cleric bit (1) set; fire and water clerics still not, as the game's daggers
    bytes.fromhex("010020000a00fa000405010104010000f31f0000"),
    # bone and obsidian great axes (weaponchoice.py, worldgear.py): the metal one's, of bone
    # (lighter, 50, still too heavy to backstab with; for water clerics) and of obsidian (for earth,
    # fire and water clerics)
    bytes.fromhex("010010003200fa00010501010a01004068160002"),
    bytes.fromhex("010010004600fa00030501010a0100406e160002"),
    # a bone dagger (weaponchoice.py, worldgear.py): the obsidian Dagger's (17), of bone, for water
    # clerics and not fire ones (the game's daggers are for neither)
    bytes.fromhex("010020000a00fa000105010104010000fa1f0000"),
    # a robe (robes.py): the cloak of protection's, worn on the chest, not armour, for preservers,
    # psionicists and druids
    bytes.fromhex("000000000a000a00400100000000008" "090010001"),
    # a metal shield (worldgear.py's Ironbulwark): the game's leather Shield's (4), of metal, for the
    # classes of its wooden one (126Fh: no thieves)
    bytes.fromhex("040000003200fa0004050000000000806f120100"),
)
TSR_TYPES_OFF, TSR_TYPES_COUNT, TSR_TYPES_FIRST, TSR_TYPES_PTR = 208, 210, 212, 214


ITEM_VALUE = 0x06  # an item's price (a word, in the game's coins)


def _item(template: str, plus: int = 0, type_: Optional[int] = None, name: Optional[int] = None,
          value: Optional[int] = None) -> bytes:
    """An item record from one of the game's templates (SEGOBJEX), in no list and no slot."""
    rec = bytearray.fromhex(template)
    struct.pack_into("<H", rec, game.ITEM_NEXT, game.NO_ITEM)
    struct.pack_into("<H", rec, ring.ITEM_CONTENTS, game.NO_ITEM)
    rec[game.ITEM_SLOT] = 0xFF
    if type_ is not None:
        struct.pack_into("<H", rec, game.ITEM_TYPE, type_)
    if name is not None:
        struct.pack_into("<H", rec, game.ITEM_NAME, name)
    rec[0x0C] = 0  # (the game's cache of the item's picture; the Cloak's template has 35h)
    rec[game.ITEM_PLUS] = plus & 0xFF
    if value is not None:
        struct.pack_into("<H", rec, ITEM_VALUE, value)
    return bytes(rec)


# pictures and the rest from the game's own: the metal long sword, the Helm, Leather Chest
# Armor, the Cloak
SWORD = _item("0afc00000000f40100003f000000000006ff1c0000", type_=SHORT_SWORD_TYPE, name=SHORT_SWORD)
HELM = _item("03fc000000000500000005000000000004ff060000")
# priced as magic items (the templates have the plain ones' 10 and 20: the game's Drake Armor +1 is
# 8000, Silk Armor +2 4000, Chain Chest Armor 1500, its magic rings 30000-50000, the Living Cloak
# 20000): the leather +1 6000, the cloak 15000, as the Rings of Protection (ring.VALUE)
CHEST_VALUE, CLOAK_VALUE = 6000, 15000
CHEST_ARMOR = _item("02fc000000000a00000006000000000004ff070000", plus=1, name=INIXHIDE, value=CHEST_VALUE)
CLOAK_ITEM = _item("e3fb000000001400000041003500000003ff0e0000", plus=1, type_=CLOAK_TYPE, name=CLOAK, value=CLOAK_VALUE)
RING_ITEM = ring.RING[:game.ITEM_NAME] + struct.pack("<H", RING) + ring.RING[game.ITEM_NAME + 2:]
KURZAK, LEGCRUSHER, PEHTUCL = 29, 326, 37  # their objects (Pehtucl's: the Templar with the Bloodwrath)


def pens(magic_arms: bool = True) -> List[Tuple[int, Tuple[bytes, ...]]]:
    """(object, items) for each of the three: Kurzak's sword Shadowseeker with MAGIC_ARMS."""
    from . import arms
    sword = arms.shadowseeker(SWORD) if magic_arms else SWORD
    return [(KURZAK, (sword, HELM)), (LEGCRUSHER, (CHEST_ARMOR,)), (PEHTUCL, (CLOAK_ITEM, RING_ITEM))]


def types_ready(gd: GameData, tsr_hdr) -> bool:
    """The game's type table has DSCLOG's types, numbered from GAME_TYPES."""
    if tsr_hdr is None:
        return False
    first, off, seg = struct.unpack("<HHH", gd.guest.read(tsr_hdr + TSR_TYPES_FIRST, 6))
    return first == GAME_TYPES and seg * 16 + off == game.far_pointer(gd.guest, gd.ds, game.ITEM_TYPES_PTR)


def _new_list(gd: GameData, it, creature: int, lists) -> Optional[int]:
    """An empty item list for the creature, from the game's free objects, in its last list word."""
    free = it.word(ring.FREE_THINGS)
    if free >= ring.THING_COUNT or game.NO_ITEM not in lists:
        return None
    ds = gd.ds * 16
    gd.guest.write(ds + ring.FREE_THINGS, struct.pack("<H", it.thing(free)[1] & 0xFFFF))
    gd.guest.write(ds + ring.THINGS_USED, struct.pack("<H", it.word(ring.THINGS_USED) + 1))
    gd.guest.write(it.things + free * 3, struct.pack("<BH", game.THING_ITEM, game.NO_ITEM))
    offset = game.CREATURE_ITEM_LISTS[len(lists) - 1 - lists[::-1].index(game.NO_ITEM)]
    base = game.far_pointer(gd.guest, gd.ds, game.CREATURES_PTR) + creature * game.CREATURE_SIZE
    gd.guest.write(base + offset, struct.pack("<H", free))
    return free


def add_to(gd: GameData, creature: int, rec: bytes, slot: Optional[int] = None) -> bool:
    """An item from the game's free list, made `rec`, put first in the creature's (last
    non-empty) item list, or a new one if they have none: worn in `slot` if given and free,
    else in a backpack cell of its own. False if there's nowhere (or no item record) for it."""
    it = ring.Items(gd)
    lists = [struct.unpack_from("<h", gd.creature(creature), o)[0] for o in game.CREATURE_ITEM_LISTS]
    thing = next((t for t in reversed(lists) if 0 <= t < ring.THING_COUNT), None)
    used = {data[game.ITEM_SLOT] for t in lists for _, data in it.chain(t, inside=False)}
    cell = slot if slot is not None and slot not in used else pickpocket.free_cell(gd, it, creature)
    item = it.word(ring.FREE_ITEMS)
    if cell is None or item >= game.NO_ITEM:
        return False
    if thing is None:  # no list yet (no things of their own): one, as the game's allocator gives it
        thing = _new_list(gd, it, creature, lists)
        if thing is None:
            return False
        it = ring.Items(gd)  # (read again: the list is new)
    kind, first = it.thing(thing)
    if kind != game.THING_ITEM:
        return False
    gd.guest.write(gd.ds * 16 + ring.FREE_ITEMS, it.item(item)[game.ITEM_NEXT:game.ITEM_NEXT + 2])
    ring.took(item, f"an item (picture {struct.unpack_from('<H', rec, 0)[0]:04X}h) for creature {creature}")
    rec = bytearray(rec)
    struct.pack_into("<h", rec, game.ITEM_NEXT, first)
    rec[game.ITEM_SLOT] = cell
    gd.guest.write(it.items + item * game.ITEM_SIZE, bytes(rec))
    gd.guest.write(it.things + thing * 3, struct.pack("<Bh", game.THING_ITEM, item))
    return True
