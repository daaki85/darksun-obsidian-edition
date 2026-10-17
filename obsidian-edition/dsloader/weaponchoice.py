"""New characters' weapon kinds and starting weapon (weapon specialization).

A character is chosen its kinds on the creation panel (weaponpages.py); before it is first
played (its status New) the Loader makes them whole:

- a fighter or ranger has one kind, the long sword if none was marked (a Myrmidon, kits.py, a
  second if marked; a Battle Mage, kits.py, one of its own); a gladiator two, the long sword and the club if none were; any other class
  none (marked as a warrior, then made something else);
- the game's starting weapon, the bone long sword in the right hand, becomes a plain weapon of
  the first kind, of bone or obsidian where the game has one, in a material the character can use
  (a fire cleric's long sword obsidian), with its picture and name; the short sword and the axe
  are the Loader's own, of bone (the game has no short sword but Kurzak's, Shadowseeker, and only
  a metal axe). A bow, sling or staff sling goes to the missile slot, and a bow comes with
  arrows; a weapon in both hands sends the starting shield to the backpack.

With kits (kit_gear), the game's starting gear fitted to the kit, whatever the weapon rules: a
weapon the kit forbids becomes one it allows (a Shinobi's long sword a short sword, a Brute's a
great axe, a Seeker's of its sphere's material), a shield it forbids is taken away (a Ravager's),
an off-hand weapon it forbids goes to the backpack (a Brute's club), an Arena Champion's off-hand club becomes a
shield, and a Battle Mage's quarterstaff its chosen weapon spec's weapon.
"""

import struct
from typing import List, Optional, Tuple

from . import game, restrict, specialize

FIGHTER, GLADIATOR = 9, 10
RANGERS = range(13, 17)
START_TYPE, START_NAME = 81, 0x1C  # the bone long sword the game starts warriors with
MISSILE_SLOT = game.EQUIP_SLOTS.index("missile")
AMMO_SLOT = game.EQUIP_SLOTS.index("ammo")
LEFT_HAND = game.EQUIP_SLOTS.index("left hand")
MATERIALS = {0x00: "wooden ", 0x01: "bone ", 0x02: "stone ", 0x03: "obsidian ", 0x04: "metal ", 0x05: "leather "}  # (type +8)
TWO_HANDED = 0x40  # a weapon type's +0Fh: it takes both hands (the inventory screen's test)
ITEM_PICTURE, ITEM_COUNT, ITEM_VALUE = 0x00, 0x02, 0x06
ARROWS = (0xFBD2, 62, 0x36, 1, 20)  # (picture, type, name, price, how many)

# By kind (specialize.KINDS): the plain weapon's type, name entry, picture (an item's +0: the
# object's number negated) and price
PLAIN: Tuple[Tuple[int, int, int, int], ...] = (
    (81, 0x1C, 0xFC0C, 45),    # long sword (bone)
    (18, 0x11, 0xFB5F, 1),     # club
    (17, 0x10, 0xFB60, 2),     # dagger (obsidian)
    (game.BONE_SHORT_SWORD_TYPE, 0x144, 0x10000 - 2419, 10),  # short sword (the Loader's, of bone)
    (20, 0x13, 0xFB5D, 8),     # mace (bone)
    (game.BONE_AXE_TYPE, 0x1A, 0x10000 - 2421, 8),  # axe (the Loader's, of bone: the game's is metal)
    (game.BONE_GREAT_AXE_TYPE, 0x03, 0x10000 - 2574, 12),  # great axe (the Loader's, of bone: the game's only one is +3)
    (112, 0xAD, 0xFB46, 8),    # pick (stone)
    (3, 0x04, 0xFC05, 1),      # quarterstaff
    (19, 0x12, 0xFB5E, 7),     # polearm (bone)
    (44, 0x3A, 0xFC0D, 6),     # gythka (bone)
    (21, 0x14, 0xFB5C, 10),    # cahulaks (bone)
    (48, 0x39, 0xFC0E, 2),     # chatkcha (obsidian)
    (1, 0x02, 0xFC07, 30),     # bow
    (64, 0x00, 0xFC09, 1),     # sling
    (0, 0x01, 0xFC08, 2),      # staff sling
)
# Other plain weapons of a kind in the game, for a character who can't use PLAIN's (a fire cleric's
# long sword obsidian, an earth cleric's metal or obsidian; SEGOBJEX's templates)
OTHERS = {
    specialize.KINDS.index("long sword"): ((45, 0x1C, 0xFC0B, 75), (63, 0x1C, 0xFC0A, 500)),  # obsidian, metal
    specialize.KINDS.index("dagger"): ((33, 0x10, 0xFB5A, 1), (game.BONE_DAGGER_TYPE, 0x10, 0x10000 - 2578, 2)),  # stone; bone (water)
    specialize.KINDS.index("mace"): ((46, 0x13, 0x10000 - 2486, 15),),  # obsidian (the game's type: Blackmace's)
    specialize.KINDS.index("short sword"): ((game.OBSIDIAN_SHORT_SWORD_TYPE, 0x144, 0x10000 - 2488, 20),),
    specialize.KINDS.index("axe"): ((game.OBSIDIAN_AXE_TYPE, 0x1A, 0x10000 - 2490, 15),
                                    (22, 0x1A, 0xFB61, 100)),  # obsidian (a fire cleric's), metal
    # the Loader's obsidian great axe (a fire or earth cleric's), and its metal ones (worldgear.py)
    specialize.KINDS.index("great axe"): ((game.OBSIDIAN_GREAT_AXE_TYPE, 0x03, 0x10000 - 2576, 25),
                                          (game.METAL_GREAT_AXE_TYPE, 0x03, 0x10000 - 2508, 300)),
    specialize.KINDS.index("polearm"): ((game.METAL_POLEARM_TYPE, 0x12, 0x10000 - 2512, 250),),
}
MISSILE_KINDS = frozenset(specialize.KINDS.index(k) for k in ("bow", "sling", "staff sling"))
BOW = specialize.KINDS.index("bow")


def pick_word(sheet: bytes, kind: int) -> str:
    """The weapon window's first line for a kind pointed at, as DSCLOG's PK_WORD: "EXPERT IN" when
    the character would have expertise with it once picked (into its first empty slot: a ranger,
    a Battle Mage, a fighter's second kind), else "SPECIALIZE IN"."""
    s = bytearray(sheet)
    slots = game.SPEC_SLOTS
    for i in range(slots, slots + game.SPEC_COUNT):
        if not s[i]:
            s[i] = kind + 1
            if specialize.skill(bytes(s), PLAIN[kind][0]) == specialize.EXPERT:
                return "EXPERT IN"
            break
    return "SPECIALIZE IN"


def kinds_for(sheet: bytes, allowed: Optional[List[int]] = None) -> List[int]:
    """The kinds (+1 each, as in the sheet) a new character ends up with; ALLOWED: the kinds its
    classes let it choose (restrict.allowed_kinds; None: all), the first of them the default
    where the long sword (and the club) isn't."""
    allowed = list(range(len(PLAIN))) if allowed is None else allowed
    ok = [k + 1 for k in allowed]
    classes = set(sheet[game.SHEET_CLASSES:game.SHEET_CLASSES + 3])
    chosen = [k if k in ok else 0 for k in sheet[game.SPEC_SLOTS:game.SPEC_SLOTS + game.SPEC_COUNT]]
    if not ok:
        return [0, 0, 0, 0]
    defaults = [k for k in (1, 2) if k in ok] + [k for k in ok if k not in (1, 2)]
    if GLADIATOR in classes:
        first = chosen[0] or defaults[0]
        seconds = [k for k in (2, 1) if k in ok] + defaults  # (the club, as the panel puts in)
        second = chosen[1] if chosen[1] and chosen[1] != first else next((k for k in seconds if k != first), 0)
        return [first, second, 0, 0]
    if FIGHTER in classes and specialize.myrmidon(sheet):  # (a second kind, if one was marked)
        first = chosen[0] or defaults[0]
        return [first, chosen[1] if chosen[1] != first else 0, 0, 0]
    if FIGHTER in classes or classes & set(RANGERS) or specialize.battle_mage(sheet):
        return [chosen[0] or defaults[0], 0, 0, 0]
    return [0, 0, 0, 0]


def start_weapon(sheet: bytes, kinds: List[int], type_record) -> Optional[Tuple[int, Tuple[int, int, int, int]]]:
    """(kind, plain weapon) a new character starts with: of its first kind (KINDS as the sheet has
    them), in a material it can use, else of the first of its kinds (then of any kind its classes
    allow) that has one; None for none. TYPE_RECORD(type) gives an item type's record."""
    from . import restrict
    order = [k - 1 for k in kinds if k] + restrict.allowed_kinds(sheet, type_record)
    for kind in order:
        for weapon in (PLAIN[kind],) + OTHERS.get(kind, ()):
            if restrict.usable(sheet, weapon[0], type_record(weapon[0])):
                return kind, weapon
    return None


def plain_weapon(start: bytes, kind: int, weapon: Optional[Tuple[int, int, int, int]] = None) -> Tuple[bytes, Optional[int]]:
    """The starting weapon's record made the kind's plain weapon (WEAPON, else PLAIN's), and the
    slot it goes to (None: where it is)."""
    type_, name, picture, price = weapon or PLAIN[kind]
    rec = bytearray(start)
    struct.pack_into("<H", rec, ITEM_PICTURE, picture)
    struct.pack_into("<H", rec, ITEM_VALUE, price)
    struct.pack_into("<H", rec, game.ITEM_TYPE, type_)
    struct.pack_into("<H", rec, game.ITEM_NAME, name)
    struct.pack_into("<H", rec, 0x0C, 0)  # (the game's cache of the item's icon: loaded anew)
    rec[game.ITEM_PLUS] = 0
    slot = MISSILE_SLOT if kind in MISSILE_KINDS else None
    if slot is not None:
        rec[game.ITEM_SLOT] = slot
    return bytes(rec), slot


def bow_ahead(gd, member: int) -> None:
    """A party member's missile weapon put ahead of its ammunition in its item list, where the
    ammunition came first (given after it: an item is added at the list's head): the game's weapon
    lines (the inventory screen) show the first of the two it meets, so the bow was listed as its
    arrows ("Arrows 1D6") until it was taken off and put on again. The two records' contents are
    swapped, each keeping its place in the list."""
    worn = [(index, item) for index, item, _ in gd._worn(member)]
    order = [item[game.ITEM_SLOT] for _, item in worn]
    if AMMO_SLOT not in order or MISSILE_SLOT not in order or order.index(AMMO_SLOT) > order.index(MISSILE_SLOT):
        return
    (ammo, ammo_rec), (bow, bow_rec) = worn[order.index(AMMO_SLOT)], worn[order.index(MISSILE_SLOT)]
    items = game.far_pointer(gd.guest, gd.ds, game.ITEMS_PTR)
    link = slice(game.ITEM_NEXT, game.ITEM_NEXT + 2)
    first, second = bytearray(bow_rec), bytearray(ammo_rec)
    first[link], second[link] = ammo_rec[link], bow_rec[link]
    gd.guest.write(items + ammo * game.ITEM_SIZE, bytes(first))
    gd.guest.write(items + bow * game.ITEM_SIZE, bytes(second))


def arrows(template: bytes) -> bytes:
    picture, type_, name, price, count = ARROWS
    rec = bytearray(template)
    struct.pack_into("<HH", rec, ITEM_PICTURE, picture, count)
    struct.pack_into("<H", rec, ITEM_VALUE, price)
    struct.pack_into("<H", rec, game.ITEM_TYPE, type_)
    struct.pack_into("<H", rec, game.ITEM_NAME, name)
    struct.pack_into("<H", rec, 0x0C, 0)
    rec[game.ITEM_PLUS] = 0
    return bytes(rec)


def two_handed(gd, sheet: bytes, type_: int) -> bool:
    """Whether a weapon type takes both hands (its type's +0Fh, 40h), as the game has it, for this
    character: not for a half-giant with RULE_HALF_GIANT."""
    if sheet[game.SHEET_RACE] == game.RACE_HALF_GIANT and gd.rules & game.RULE_HALF_GIANT:
        return False
    types = game.far_pointer(gd.guest, gd.ds, game.ITEM_TYPES_PTR)
    return bool(gd.guest.read(types + type_ * game.ITEM_TYPE_SIZE, game.ITEM_TYPE_SIZE)[0x0F] & TWO_HANDED)


def _shield_off(gd, member: int, owned, items: int) -> List[str]:
    """What the left hand holds (the game's starting shield) into a backpack cell, for a weapon
    in both hands."""
    from . import pickpocket, ring
    for item_index, item, _ in owned:
        if item[game.ITEM_SLOT] == LEFT_HAND:
            cell = pickpocket.free_cell(gd, ring.Items(gd), member)
            if cell is None:
                return []
            pickpocket.place(gd, member, item_index, cell)
            name = gd.item_name(struct.unpack_from("<H", item, game.ITEM_NAME)[0])
            return [f"    {gd.creature_name(member)}'s {name} goes into the backpack: "
                    f"the weapon takes both hands"]
    return []


def finish_new(gd) -> List[str]:
    """The party's New characters' kinds made whole, and their starting weapons changed: lines
    for the log."""
    from . import npcitems
    out: List[str] = []
    sheets = game.far_pointer(gd.guest, gd.ds, game.SHEETS_PTR)
    items = game.far_pointer(gd.guest, gd.ds, game.ITEMS_PTR)
    for member in range(game.PARTY_SIZE):
        rec = gd.creature(member)
        if len(rec) < game.CREATURE_SIZE or not rec[game.CREATURE_NAME] or rec[game.CREATURE_STATUS] != game.STATUS_NEW:
            continue
        index = struct.unpack_from("<H", rec, game.CREATURE_SHEET_INDEX)[0]
        sheet = gd.guest.read(sheets + index * game.SHEET_SIZE, game.SHEET_SIZE)
        if len(sheet) < game.SHEET_SIZE:
            continue
        types = game.far_pointer(gd.guest, gd.ds, game.ITEM_TYPES_PTR)
        kinds = kinds_for(sheet, restrict.allowed_kinds(
            sheet, lambda t: gd.guest.read(types + t * game.ITEM_TYPE_SIZE, game.ITEM_TYPE_SIZE)))
        if bytes(kinds) != sheet[game.SPEC_SLOTS:game.SPEC_SLOTS + game.SPEC_COUNT]:
            gd.guest.write(sheets + index * game.SHEET_SIZE + game.SPEC_SLOTS, bytes(kinds))
        read = lambda t: gd.guest.read(types + t * game.ITEM_TYPE_SIZE, game.ITEM_TYPE_SIZE)
        start = start_weapon(sheet, kinds, read) if kinds[0] else None
        if start is None or start[1][0] == START_TYPE:
            continue  # (the game's bone long sword is the one)
        kind, weapon = start
        owned = list(gd._worn(member))
        if any(struct.unpack_from("<H", item, game.ITEM_TYPE)[0] == weapon[0] for _, item, _ in owned):
            continue  # (made already: a long sword handed over later stays one)
        for item_index, item, _ in owned:
            if struct.unpack_from("<H", item, game.ITEM_TYPE)[0] == START_TYPE \
                    and struct.unpack_from("<H", item, game.ITEM_NAME)[0] == START_NAME \
                    and item[game.ITEM_SLOT] in game.WEAPON_HANDS and item[game.ITEM_PLUS] == 0:
                new, slot = plain_weapon(item, kind, weapon)
                gd.guest.write(items + item_index * game.ITEM_SIZE, new)
                if kind == BOW:
                    npcitems.add_to(gd, member, arrows(new), AMMO_SLOT)
                    bow_ahead(gd, member)
                # (a two-handed weapon in a hand needs the other free; the game asks nothing of a
                # bow or a staff sling in the missile slot: the shield stays)
                if slot is None and two_handed(gd, sheet, weapon[0]):
                    out += _shield_off(gd, member, owned, items)
                material = MATERIALS.get(read(weapon[0])[8] & 0x4F, "")
                why = "" if kind == kinds[0] - 1 else f" (no {specialize.KINDS[kinds[0] - 1]} it can use to start with)"
                out.append(f"{gd.creature_name(member)} starts with a plain {material}{specialize.KINDS[kind]} "
                           f"for the weapon specialization chosen, in place of the bone long sword{why}")
                break
    return out


def class_gear(gd) -> List[str]:
    """The party's New characters' starting weapons, armour and shields that their classes can't
    use (restrict.usable: a druid's leather armour, given for its fighter class) left behind:
    lines for the log; armour its kit forbids too (a Shadowblade's that isn't light). A weapon or
    shield only the kit forbids is kit_gear's, fitted to the kit (a Brute's long sword made a
    two-handed weapon). The game gives a character of several classes the gear of each and puts
    what it may not wear in the backpack, where it would only weigh."""
    from . import kitpages, ring
    out: List[str] = []
    sheets = game.far_pointer(gd.guest, gd.ds, game.SHEETS_PTR)
    types = game.far_pointer(gd.guest, gd.ds, game.ITEM_TYPES_PTR)
    read = lambda t: gd.guest.read(types + t * game.ITEM_TYPE_SIZE, game.ITEM_TYPE_SIZE)
    for member in range(game.PARTY_SIZE):
        rec = gd.creature(member)
        if len(rec) < game.CREATURE_SIZE or not rec[game.CREATURE_NAME] or rec[game.CREATURE_STATUS] != game.STATUS_NEW:
            continue
        index = struct.unpack_from("<H", rec, game.CREATURE_SHEET_INDEX)[0]
        sheet = gd.guest.read(sheets + index * game.SHEET_SIZE, game.SHEET_SIZE)
        if len(sheet) < game.SHEET_SIZE:
            continue
        for item_index, item, _ in list(gd._worn(member)):
            type_ = struct.unpack_from("<H", item, game.ITEM_TYPE)[0]
            typ = read(type_)
            if len(typ) < game.ITEM_TYPE_SIZE or not (restrict.is_weapon(typ) or restrict.is_armour(typ)
                                                      or restrict.is_shield(typ)):
                continue
            classes_let = restrict.usable(sheet, type_, typ, kit=False)
            if restrict.usable(sheet, type_, typ) or classes_let and not restrict.is_armour(typ):
                continue  # (a weapon or shield only the kit forbids: kit_gear's)
            if not ring.unlink(gd, ring.Items(gd), item_index, "class gear", empty=True):
                continue
            name = gd.item_name(struct.unpack_from("<H", item, game.ITEM_NAME)[0])
            why = f"a {kitpages.name_of(kitpages.kit_at(sheet, 0))} can't wear it" if classes_let \
                else "their classes can't use it"
            out.append(f"{gd.creature_name(member)}'s {name} is left behind: {why}")
    return out


SHIELD = (4, 0x05, 0xFC04, 10)  # the game's starting (leather) shield: type, name, picture, price
# the kinds a forbidden starting weapon becomes, the nearest to the long sword first (a Shinobi's
# short sword, a Brute's great axe); then any other kind, in KINDS' order
REPLACE_ORDER = tuple(specialize.KINDS.index(k) for k in ("long sword", "short sword", "axe", "mace", "great axe",
                                                          "gythka", "polearm"))


def _replacement(sheet: bytes, kinds: List[int], read) -> Optional[Tuple[int, Tuple[int, int, int, int]]]:
    """(kind, plain weapon) for a hand's weapon its kit forbids: of the first of KINDS (else any
    kind its classes allow) with a melee weapon, in a material it may use, that the kit allows."""
    allowed = restrict.allowed_kinds(sheet, read)
    order = sorted(allowed, key=lambda k: REPLACE_ORDER.index(k) if k in REPLACE_ORDER else len(REPLACE_ORDER) + k)
    for kind in kinds + order:
        if kind in MISSILE_KINDS:
            continue
        for weapon in (PLAIN[kind],) + OTHERS.get(kind, ()):
            typ = read(weapon[0])
            if typ[0] & 0x01 and restrict.usable(sheet, weapon[0], typ) \
                    and not restrict.kit_forbids(sheet, weapon[0], typ):
                return kind, weapon
    return None


def kit_gear(gd) -> List[str]:
    """The party's New characters' starting gear fitted to their kits (the module's notes): lines
    for the log. A change is made where the gear doesn't fit, so made once."""
    from . import kitpages, kits, pickpocket, ring
    out: List[str] = []
    sheets = game.far_pointer(gd.guest, gd.ds, game.SHEETS_PTR)
    items = game.far_pointer(gd.guest, gd.ds, game.ITEMS_PTR)
    types = game.far_pointer(gd.guest, gd.ds, game.ITEM_TYPES_PTR)
    read = lambda t: gd.guest.read(types + t * game.ITEM_TYPE_SIZE, game.ITEM_TYPE_SIZE)
    right, left = game.WEAPON_HANDS
    for member in range(game.PARTY_SIZE):
        rec = gd.creature(member)
        if len(rec) < game.CREATURE_SIZE or not rec[game.CREATURE_NAME] or rec[game.CREATURE_STATUS] != game.STATUS_NEW:
            continue
        index = struct.unpack_from("<H", rec, game.CREATURE_SHEET_INDEX)[0]
        sheet = gd.guest.read(sheets + index * game.SHEET_SIZE, game.SHEET_SIZE)
        kid = kitpages.kit_at(sheet, 0) if len(sheet) >= game.SHEET_SIZE else 0  # (a new character's one)
        if not kid:
            continue
        who, kit = gd.creature_name(member), kitpages.name_of(kid)
        chosen = [k - 1 for k in sheet[game.SPEC_SLOTS:game.SPEC_SLOTS + game.SPEC_COUNT] if k]
        owned = list(gd._worn(member))
        name = lambda item: gd.item_name(struct.unpack_from("<H", item, game.ITEM_NAME)[0])
        for item_index, item, _ in owned:
            slot, type_ = item[game.ITEM_SLOT], struct.unpack_from("<H", item, game.ITEM_TYPE)[0]
            typ = read(type_)
            if slot not in (right, left) or not restrict.kit_forbids(sheet, type_, typ, off_hand=slot == left):
                continue
            at = items + item_index * game.ITEM_SIZE
            new = _replacement(sheet, chosen, read) if slot == right and typ[0] & 0x01 else None
            if new is None:
                if typ[0] & kits.SHIELD and ring.unlink(gd, ring.Items(gd), item_index, "kit gear", empty=True):
                    out.append(f"{who}'s {name(item)} is left behind: a {kit} fights without a shield")
                    continue  # (a shield the kit forbids: no use in the backpack)
                cell = pickpocket.free_cell(gd, ring.Items(gd), member)
                if cell is not None:
                    pickpocket.place(gd, member, item_index, cell)
                    out.append(f"{who}'s {name(item)} goes into the backpack: a {kit} can't use it")
                continue
            kind, weapon = new
            gd.guest.write(at, plain_weapon(item, kind, weapon)[0])
            material = MATERIALS.get(read(weapon[0])[8] & 0x4F, "")
            out.append(f"{who} starts with a plain {material}{specialize.KINDS[kind]} in place of the "
                       f"{name(item)}: a {kit} can't use it")
            if two_handed(gd, sheet, weapon[0]):
                out += _shield_off(gd, member, list(gd._worn(member)), items)
        owned = list(gd._worn(member))
        if kid == kits.CHAMPION and not any(read(struct.unpack_from("<H", i, game.ITEM_TYPE)[0])[0] & kits.SHIELD
                                            for _, i, _ in owned):
            for item_index, item, _ in owned:
                if item[game.ITEM_SLOT] == left:  # (the gladiator's club)
                    rec_ = bytearray(item)
                    type_, name_, picture, price = SHIELD
                    struct.pack_into("<H", rec_, ITEM_PICTURE, picture)
                    struct.pack_into("<H", rec_, ITEM_VALUE, price)
                    struct.pack_into("<H", rec_, game.ITEM_TYPE, type_)
                    struct.pack_into("<H", rec_, game.ITEM_NAME, name_)
                    struct.pack_into("<H", rec_, 0x0C, 0)
                    rec_[game.ITEM_PLUS] = 0
                    gd.guest.write(items + item_index * game.ITEM_SIZE, bytes(rec_))
                    out.append(f"{who} starts with a shield in place of the {name(item)}: an Arena Champion "
                               f"fights with one")
                    break
        if kid == kits.BRUTE:  # (the gladiator's club: no use to it, in the backpack or a hand)
            for item_index, item, _ in list(gd._worn(member)):
                type_ = struct.unpack_from("<H", item, game.ITEM_TYPE)[0]
                typ = read(type_)
                if typ[0] & 0x01 and restrict.kit_forbids(sheet, type_, typ) \
                        and ring.unlink(gd, ring.Items(gd), item_index, "kit gear", empty=True):
                    out.append(f"{who}'s {name(item)} is left behind: a Brute fights with two-handed weapons only")
        owned = list(gd._worn(member))
        out += _kit_second_weapon(gd, member, sheet, kid, chosen, owned, read)
        if kid == kits.POISONER:
            out += _poisoner_daggers(gd, member, sheet, read)
        if kid == kits.GHETTO:
            out += _ghetto_dagger(gd, member, sheet, read)
        if kid == kits.BATTLE_MAGE and chosen and gd.rules & game.RULE_SPECIALIZE \
                and not any(specialize.kind_of(struct.unpack_from("<H", i, game.ITEM_TYPE)[0]) == chosen[0]
                            for _, i, _ in owned):
            for item_index, item, _ in owned:
                if item[game.ITEM_SLOT] == right:  # (the preserver's quarterstaff)
                    new = start_weapon(sheet, [chosen[0] + 1], read)
                    if new is None or new[0] != chosen[0]:
                        break
                    gd.guest.write(items + item_index * game.ITEM_SIZE, plain_weapon(item, *new)[0])
                    material = MATERIALS.get(read(new[1][0])[8] & 0x4F, "")
                    out.append(f"{who} starts with a plain {material}{specialize.KINDS[chosen[0]]} for the Battle "
                               f"Mage's weapon spec, in place of the {name(item)}")
                    break
    return out


def _kit_second_weapon(gd, member: int, sheet: bytes, kid: int, chosen: List[int], owned, read) -> List[str]:
    """A Myrmidon's plain weapon of its second weapon spec (in the left hand in place of the shield,
    for a one-handed melee weapon; else the missile slot, a bow with arrows, or the backpack), and a
    Ravager's or Battle Dancer's second weapon for the left hand (a plain one of its right hand's
    kind, unless that takes both hands; a Battle Dancer's in place of its shield): lines for the
    log. Given once: not while the character has a weapon of that kind (the Myrmidon's), or a
    weapon in the left hand or two of its right hand's kind (the Ravager's and the Battle Dancer's)."""
    from . import kits, npcitems
    right, left = game.WEAPON_HANDS
    kind_of = lambda item: specialize.kind_of(struct.unpack_from("<H", item, game.ITEM_TYPE)[0])
    hand = next((item for _, item, _ in owned if item[game.ITEM_SLOT] == right), None)
    who = gd.creature_name(member)
    if kid == kits.MYRMIDON and len(chosen) > 1 and gd.rules & game.RULE_SPECIALIZE and hand is not None:
        if any(kind_of(item) == chosen[1] for _, item, _ in owned):
            return []
        new = start_weapon(sheet, [chosen[1] + 1], read)
        if new is None or new[0] != chosen[1]:
            return []
        rec, slot = plain_weapon(hand, *new)
        material = MATERIALS.get(read(new[1][0])[8] & 0x4F, "")
        if slot is None and not two_handed(gd, sheet, new[1][0]) and not two_handed(
                gd, sheet, struct.unpack_from("<H", hand, game.ITEM_TYPE)[0]):
            shield = _shield_away(gd, owned)
            if not any(item[game.ITEM_SLOT] == left for _, item, _ in list(gd._worn(member))) \
                    and npcitems.add_to(gd, member, rec, left):
                instead = f", in place of the {shield}" if shield else ""
                return [f"{who} starts with a plain {material}{specialize.KINDS[new[0]]} in the left hand"
                        f"{instead}: a Myrmidon's second weapon spec"]
        if not npcitems.add_to(gd, member, rec, slot):
            return []
        if new[0] == BOW:
            npcitems.add_to(gd, member, arrows(rec), AMMO_SLOT)
            bow_ahead(gd, member)
        where = "" if slot is not None else " in the backpack"
        return [f"{who} starts with a plain {material}{specialize.KINDS[new[0]]}{where} too: a Myrmidon's "
                f"second weapon spec"]
    if kid in (kits.RAVAGER, kits.BATTLE_DANCER) and hand is not None:
        kind, type_ = kind_of(hand), struct.unpack_from("<H", hand, game.ITEM_TYPE)[0]
        if kind is None or kind in MISSILE_KINDS or two_handed(gd, sheet, type_) \
                or any(item[game.ITEM_SLOT] == left and kind_of(item) is not None for _, item, _ in owned) \
                or sum(kind_of(item) == kind for _, item, _ in owned) > 1:
            return []  # (a weapon in the left hand already, or two of the kind anywhere: given, or its own)
        shield = _shield_away(gd, owned) if kid == kits.BATTLE_DANCER else None
        if any(item[game.ITEM_SLOT] == left for _, item, _ in list(gd._worn(member))) \
                or not npcitems.add_to(gd, member, hand, left):
            return []
        name = gd.item_name(struct.unpack_from("<H", hand, game.ITEM_NAME)[0])
        if kid == kits.RAVAGER:
            return [f"{who} starts with a second {name} in the left hand: a Ravager fights without a shield"]
        instead = f", in place of the {shield}" if shield else ""
        return [f"{who} starts with a second {name} in the left hand{instead}: a Battle Dancer fights with two"]
    return []


def _poisoner_daggers(gd, member: int, sheet: bytes, read) -> List[str]:
    """A Poisoner's two daggers, one in each hand: the right hand's weapon made a plain dagger (of a
    material it can use), and a second in the left hand, in place of its shield: lines for the
    log. Made once: not while it holds a dagger in the left hand."""
    from . import kits, npcitems, ring
    right, left = game.WEAPON_HANDS
    items = game.far_pointer(gd.guest, gd.ds, game.ITEMS_PTR)
    kind_of = lambda item: specialize.kind_of(struct.unpack_from("<H", item, game.ITEM_TYPE)[0])
    name = lambda item: gd.item_name(struct.unpack_from("<H", item, game.ITEM_NAME)[0])
    owned = list(gd._worn(member))
    if any(item[game.ITEM_SLOT] == left and kind_of(item) == kits.DAGGER for _, item, _ in owned):
        return []
    new = start_weapon(sheet, [kits.DAGGER + 1], read)
    if new is None or new[0] != kits.DAGGER:
        return []
    who, out = gd.creature_name(member), []
    material = MATERIALS.get(read(new[1][0])[8] & 0x4F, "")
    hand = next(((i, item) for i, item, _ in owned if item[game.ITEM_SLOT] == right), None)
    if hand is None:
        return []  # (no weapon to make a dagger of: the starting gear's fill gives one)
    if kind_of(hand[1]) != kits.DAGGER:
        gd.guest.write(items + hand[0] * game.ITEM_SIZE, plain_weapon(hand[1], *new)[0])
        out.append(f"{who} starts with a plain {material}dagger in place of the {name(hand[1])}: a "
                   f"Poisoner fights with two daggers")
    dagger = next(item for _, item, _ in gd._worn(member) if item[game.ITEM_SLOT] == right)
    shield = None
    for item_index, item, _ in list(gd._worn(member)):  # (its shield left behind)
        if item[game.ITEM_SLOT] == left and read(struct.unpack_from("<H", item, game.ITEM_TYPE)[0])[0] & kits.SHIELD \
                and ring.unlink(gd, ring.Items(gd), item_index, "kit gear", empty=True):
            shield = name(item)
    if any(item[game.ITEM_SLOT] == left for _, item, _ in gd._worn(member)) \
            or not npcitems.add_to(gd, member, dagger, left):
        return out
    instead = f", in place of the {shield}" if shield else ""
    return out + [f"{who} starts with a second {name(dagger)} in the left hand{instead}: a Poisoner fights "
                  f"with two daggers"]


def _ghetto_dagger(gd, member: int, sheet: bytes, read) -> List[str]:
    """A Ghetto Fighter's dagger: the right hand's weapon made a plain dagger (of a material it can
    use), whatever its weapon spec, as its +1 is with a dagger: lines for the log. Made once: not
    while it holds a dagger there."""
    from . import kits
    right = game.WEAPON_HANDS[0]
    items = game.far_pointer(gd.guest, gd.ds, game.ITEMS_PTR)
    hand = next(((i, item) for i, item, _ in gd._worn(member) if item[game.ITEM_SLOT] == right), None)
    if hand is None or specialize.kind_of(struct.unpack_from("<H", hand[1], game.ITEM_TYPE)[0]) == kits.DAGGER:
        return []
    new = start_weapon(sheet, [kits.DAGGER + 1], read)
    if new is None or new[0] != kits.DAGGER:
        return []
    name = gd.item_name(struct.unpack_from("<H", hand[1], game.ITEM_NAME)[0])
    gd.guest.write(items + hand[0] * game.ITEM_SIZE, plain_weapon(hand[1], *new)[0])
    material = MATERIALS.get(read(new[1][0])[8] & 0x4F, "")
    return [f"{gd.creature_name(member)} starts with a plain {material}dagger in place of the {name}: a "
            f"Ghetto Fighter fights best with one"]


def _shield_away(gd, owned) -> Optional[str]:
    """A shield in the left hand left behind (for a second weapon): its name, or None."""
    from . import kits, ring
    left = game.WEAPON_HANDS[1]
    for item_index, item, typ in owned:
        if item[game.ITEM_SLOT] == left and len(typ) > 0 and typ[0] & kits.SHIELD \
                and ring.unlink(gd, ring.Items(gd), item_index, "kit gear", empty=True):
            return gd.item_name(struct.unpack_from("<H", item, game.ITEM_NAME)[0])
    return None
