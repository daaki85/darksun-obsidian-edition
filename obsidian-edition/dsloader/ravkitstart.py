"""New characters' starting gear fitted to their kits in Wake of the Ravager (Daaki, 2026-11-26).

Shattered Lands' Loader fits a new character's starting gear to its class and kit (weaponchoice.class_gear,
weaponchoice.kit_gear, KITS.md's "Starts with"); this is the same for the sequel's gear (its starting gear's
table, ravager.GEAR_TABLE: mostly +1 weapons and shields), on DSCLOG2's GEAR_DONE while DONE waits (ravlog's
_gear_pass), after a warrior's first pick has made its weapon (ravfirstweapon.fill) and before the fuller
starting gear (startgear.fill):

- **the kit's** (kit_gear here), first: Shattered Lands' class step comes first there, but in the sequel it would
  leave behind the armour a kit forbids before it could be made leather (a Ravager's ring armour, 2026-11-26);
- **the classes'** (weaponchoice.class_gear, as it is: it reads only the rules): a weapon, armour or shield the
  character's classes can't use left behind (an earth or water cleric's club, which the sequel gives no
  material), and armour its kit forbids that kit_gear couldn't make leather.

The kit's: a weapon in hand (or in the backpack with the right hand empty: the game's give
routine drops there what the equip test refuses, DSCLOG2's KIT_FORBIDS) that the kit forbids becomes one it
allows, the nearest kind to the long sword first (weaponchoice.REPLACE_ORDER: a Shinobi's long sword a short
sword); a shield it forbids is left behind (a Ravager's), armour it forbids becomes the sequel's leather where
the kit allows that (a Ravager's ring armour: Shattered Lands' fighter starts in leather), else is left behind
(a Spellarcher's); a weapon it forbids in the off hand or the missile slot goes to the backpack; then each
kit's own, as Shattered Lands': an Arena Champion's left-hand weapon becomes a shield, a Brute's one-handed
weapons are left behind, a Myrmidon has a plain polearm in the backpack, a Ravager and a Battle Dancer a second
of the right hand's weapon in the left (weaponchoice._kit_second_weapon, as it is), a Poisoner two blades of its
weapon spec, a Ghetto Fighter a dagger, a Battle Mage its weapon spec's weapon.

**What a weapon is made** (made_like): a weapon made in place keeps its grade. The sequel's gear is magic where
Shattered Lands' is plain, so one made from a +1 weapon (a thief's long sword +1, a gladiator's) is the kind's
+1 (ravfirstweapon.PLUS_ONE, by ravfirstweapon.choice), one made from a plain one is plain (the sequel's plain
weapons, ravlog.rav_weapon: RAV_PLAIN), as is a weapon given anew (the Myrmidon's polearm, as Shattered Lands').
An Arena Champion's shield is the sequel's Shield +1 (the fighter's, object 842) in place of a +1 weapon, else its
plain Shield (840). Each in a material the character can use (restrict.usable: the kit's limits too).

A Spellarcher's bow (ravfirstweapon's, of its weapon spec) is made its **Fine Bow** (fine_bow: named
FINE_BOW_NAME, the sequel's mod_name of Shattered Lands', +1 to hit by DSCLOG2's FINE_HIT), its arrows the ones
ravfirstweapon gives, made its starting spell arrows as Shattered Lands' (spellarrows.starting_gear's rule:
ravarrows.starting_arrows): 24 of each touch spell's it picked, in place of those arrows; knowing none, it keeps
them.
"""

import struct
from typing import Callable, List, Optional

from . import game, ravfirstweapon, restrict, specialize, weaponchoice

Weapon = ravfirstweapon.Weapon
KIND = specialize.KINDS.index
BACKPACK = 14  # (the first backpack cell: 0-13 are worn)
SHIELD = Weapon(91, bytes.fromhex("b8fc00000f270a000f275b0000000000000004ff250000"))  # (840: Shield)
SHIELD_PLUS_ONE = Weapon(91, bytes.fromhex("b6fc00000f2734210f275b0000000000000005ff250001"))  # (842: the fighter's)
TYPE_WORN = 9  # (an item type's place on the body as the dice log's view serves the types, the sequel's +5: 1 the
# chest, 3 the arms, 0Ah the legs, 5 a hand)


def _type(item: bytes) -> int:
    return struct.unpack_from("<H", item, game.ITEM_TYPE)[0]


def plain(gd, sheet: bytes, kind: int, read) -> Optional[Weapon]:
    """The sequel's plain weapon of KIND the character can use (ravlog.rav_weapon: startgear's), or None."""
    from . import ravlog
    found = ravlog.rav_weapon(gd, sheet, kind, read)
    return None if found is None else Weapon(found[1][0], found[0])


def made_like(gd, sheet: bytes, kind: int, read, old: Optional[bytes], new_items: bool = True) -> Optional[Weapon]:
    """The weapon of KIND made in place of OLD (the module's notes): the kind's +1 for a magic one, else (or with
    no +1 it can use) a plain one; None if it can use neither."""
    if old is not None and old[game.ITEM_PLUS] >= 1 and kind != weaponchoice.BOW:
        weapon = ravfirstweapon.choice(gd, sheet, kind, read, new_items)
        if weapon is not None:
            return weapon
    return plain(gd, sheet, kind, read)


def called(kind: int, weapon: Weapon) -> str:
    """A weapon made, for the log: "a long sword +1", "a plain polearm"."""
    return f"a {specialize.KINDS[kind]} +1" if weapon.record[game.ITEM_PLUS] else f"a plain {specialize.KINDS[kind]}"


def replacement(gd, sheet: bytes, chosen: List[int], read, old: bytes, new_items: bool = True):
    """(kind, weapon) for a hand's weapon its kit forbids (weaponchoice._replacement's order: its weapon specs'
    kinds, then the nearest to the long sword, then any it may use): a melee weapon the kit allows; or None."""
    allowed = restrict.allowed_kinds(sheet, read)
    order = weaponchoice.REPLACE_ORDER
    for kind in chosen + sorted(allowed, key=lambda k: order.index(k) if k in order else len(order) + k):
        if kind in ravfirstweapon.MISSILE_KINDS:
            continue
        weapon = made_like(gd, sheet, kind, read, old, new_items)
        if weapon is not None and read(weapon.type)[0] & restrict.MELEE \
                and not restrict.kit_forbids(sheet, weapon.type, read(weapon.type)):
            return kind, weapon
    return None


def kit_gear(gd, new_items: bool = True) -> List[str]:
    """The party's New characters' starting gear fitted to their kits (the module's notes): lines for the log.
    A change is made where the gear doesn't fit, so made once. NEW_ITEMS: whether the mod's new items are in."""
    from . import kitpages
    out: List[str] = []
    for member in range(game.PARTY_SIZE):
        rec = gd.creature(member)
        if len(rec) < game.CREATURE_SIZE or not rec[game.CREATURE_NAME] or not game.being_new(gd, rec):
            continue
        sheets = game.table_pointer(gd.guest, gd.ds, game.SHEETS_PTR)
        index = struct.unpack_from("<H", rec, game.CREATURE_SHEET_INDEX)[0]
        sheet = gd.guest.read(sheets + index * game.SHEET_SIZE, game.SHEET_SIZE)
        if len(sheet) < game.SHEET_SIZE or not kitpages.kit_at(sheet, 0) or not list(gd._worn(member)):
            continue  # (no kit; no gear yet: the game gives it at DONE)
        out += kit_member(gd, member, sheet, new_items)
    return out


def kit_member(gd, member: int, sheet: bytes, new_items: bool = True) -> List[str]:
    """Party member MEMBER's starting gear fitted to its kit (SHEET its sheet): lines for the log."""
    from . import kitpages, kits, pickpocket, ravlog, ring
    types = game.far_pointer(gd.guest, gd.ds, game.ITEM_TYPES_PTR)
    items = game.far_pointer(gd.guest, gd.ds, game.ITEMS_PTR)
    read: Callable[[int], bytes] = lambda t: gd.guest.read(types + t * game.ITEM_TYPE_SIZE, game.ITEM_TYPE_SIZE)
    name = lambda item: gd.item_name(struct.unpack_from("<H", item, game.ITEM_NAME)[0])
    right, left = game.WEAPON_HANDS
    kid = kitpages.kit_at(sheet, 0)
    who, kit = gd.creature_name(member), kitpages.name_of(kid)
    chosen = [k - 1 for k in game.spec_kinds(sheet) if k]
    worn = lambda: list(gd._worn(member))
    at = lambda slot: next(((i, item) for i, item, _ in worn() if item[game.ITEM_SLOT] == slot), None)
    write = lambda i, rec_: gd.guest.write(items + i * game.ITEM_SIZE, rec_)
    leather = ravlog.RAV_LEATHER
    out: List[str] = []

    for item_index, item, _ in worn():
        slot, type_ = item[game.ITEM_SLOT], _type(item)
        typ = read(type_)
        if len(typ) < game.ITEM_TYPE_SIZE:
            continue
        packed = slot >= BACKPACK and bool(typ[0] & restrict.MELEE) and at(right) is None  # (the game put it there)
        shield = bool(typ[0] & kits.SHIELD)  # (in a hand or the backpack: left behind if forbidden)
        armour = bool(typ[0x0F] & kits.ARMOUR) and not shield  # (armour or a helm)
        if slot not in (right, left, weaponchoice.MISSILE_SLOT) and not packed and not shield and not armour \
                or not restrict.kit_forbids(sheet, type_, typ, off_hand=slot == left):
            continue
        new = replacement(gd, sheet, chosen, read, item, new_items) \
            if (slot == right or packed) and typ[0] & restrict.MELEE else None
        if new is None and packed:
            continue
        if new is None:
            if shield and ring.unlink(gd, ring.Items(gd), item_index, "kit gear", empty=True):
                out.append(f"{who}'s {name(item)} is left behind: a {kit} fights without a shield")
                continue
            if armour:  # (worn, or in the backpack where the game's give routine dropped it: the leather of its
                # type's place on the body, TYPE_WORN)
                worn_at, light = next(((s, rec_) for s, rec_ in leather
                                       if s == slot or read(_type(rec_))[TYPE_WORN] == typ[TYPE_WORN]), (None, None))
                if light is not None and restrict.usable(sheet, _type(light), read(_type(light))):
                    write(item_index, ravfirstweapon.made_over(item, Weapon(_type(light), light)))
                    if slot >= BACKPACK and at(worn_at) is None:
                        pickpocket.place(gd, member, item_index, worn_at)
                    out.append(f"{who} starts with leather armour in place of the {name(item)}: a {kit} wears "
                               f"light armour only")
                elif ring.unlink(gd, ring.Items(gd), item_index, "kit gear", empty=True):
                    out.append(f"{who}'s {name(item)} is left behind: a {kit} wears no armour")
                continue
            cell = pickpocket.free_cell(gd, ring.Items(gd), member)
            if cell is not None and pickpocket.place(gd, member, item_index, cell):
                out.append(f"{who}'s {name(item)} goes into the backpack: a {kit} can't use it")
            continue
        kind, weapon = new
        write(item_index, ravfirstweapon.made_over(item, weapon))
        if packed:
            pickpocket.place(gd, member, item_index, right)
        out.append(f"{who} starts with {called(kind, weapon)} in place of the {name(item)}: a {kit} can't use it")
        if weaponchoice.two_handed(gd, sheet, weapon.type):
            out += weaponchoice._shield_off(gd, member, worn(), items)

    if kid == kits.CHAMPION and not any(read(_type(i))[0] & kits.SHIELD for _, i, _ in worn()):
        held = at(left)  # (the gladiator's second long sword)
        if held is not None:
            shield = SHIELD_PLUS_ONE if held[1][game.ITEM_PLUS] >= 1 else SHIELD
            write(held[0], ravfirstweapon.made_over(held[1], shield))
            plus = " +1" if shield.record[game.ITEM_PLUS] else ""
            out.append(f"{who} starts with a shield{plus} in place of the {name(held[1])}: an Arena Champion "
                       f"fights with one")
    if kid == kits.BRUTE:  # (the gladiator's one-handed weapons: no use to it, in the backpack or a hand)
        for item_index, item, _ in worn():
            typ = read(_type(item))
            if typ[0] & restrict.MELEE and restrict.kit_forbids(sheet, _type(item), typ) \
                    and ring.unlink(gd, ring.Items(gd), item_index, "kit gear", empty=True):
                out.append(f"{who}'s {name(item)} is left behind: a Brute fights with two-handed weapons only")
    if kid == kits.MYRMIDON:
        out += _myrmidon_polearm(gd, member, sheet, read, chosen)
    elif kid in (kits.RAVAGER, kits.BATTLE_DANCER):  # (a second of the right hand's weapon: Shattered Lands')
        out += weaponchoice._kit_second_weapon(gd, member, sheet, kid, chosen, worn(), read)
    if kid == kits.POISONER:
        out += _poisoner_blades(gd, member, sheet, read, chosen, new_items)
    if kid == kits.SPELLARCHER:
        out += fine_bow(gd, member)
    if kid == kits.GHETTO:
        out += _in_hand(gd, member, sheet, read, kits.DAGGER, new_items, "a Ghetto Fighter fights best with one")
    if kid == kits.BATTLE_MAGE and chosen \
            and not any(specialize.kind_of(_type(i)) == chosen[0] for _, i, _ in worn()):
        out += _in_hand(gd, member, sheet, read, chosen[0], new_items, "the Battle Mage's weapon spec")
    return out


def fine_bow(gd, member: int) -> List[str]:
    """A Spellarcher's bow made its Fine Bow (the module's notes), once: none while it has one; with it, its
    starting spell arrows (ravarrows.starting_arrows). Lines for the log."""
    from . import ravager
    fine = ravager.FINE_BOW_NAME
    bows = [(i, item) for i, item, _ in gd._worn(member) if specialize.kind_of(_type(item)) == weaponchoice.BOW]
    if not bows or any(struct.unpack_from("<H", item, game.ITEM_NAME)[0] == fine for _, item in bows):
        return []
    index, item = bows[0]
    rec = bytearray(item)
    struct.pack_into("<H", rec, game.ITEM_NAME, fine)
    items = game.far_pointer(gd.guest, gd.ds, game.ITEMS_PTR)
    gd.guest.write(items + index * game.ITEM_SIZE, bytes(rec))
    from . import ravarrows
    return [f"{gd.creature_name(member)} starts with a Fine Bow (+1 to hit): a Spellarcher's"] \
        + ravarrows.starting_arrows(gd, member)


def _in_hand(gd, member: int, sheet: bytes, read, kind: int, new_items: bool, why: str) -> List[str]:
    """The right hand's weapon made one of KIND (made_like), unless it is one: lines for the log."""
    right = game.WEAPON_HANDS[0]
    hand = next(((i, item) for i, item, _ in gd._worn(member) if item[game.ITEM_SLOT] == right), None)
    if hand is None or specialize.kind_of(_type(hand[1])) == kind:
        return []
    weapon = made_like(gd, sheet, kind, read, hand[1], new_items)
    if weapon is None:
        return []
    items = game.far_pointer(gd.guest, gd.ds, game.ITEMS_PTR)
    gd.guest.write(items + hand[0] * game.ITEM_SIZE, ravfirstweapon.made_over(hand[1], weapon))
    was = gd.item_name(struct.unpack_from("<H", hand[1], game.ITEM_NAME)[0])
    return [f"{gd.creature_name(member)} starts with {called(kind, weapon)} in place of the {was}: {why}"]


def _myrmidon_polearm(gd, member: int, sheet: bytes, read, chosen: List[int]) -> List[str]:
    """A Myrmidon's plain weapon of its second weapon spec (the polearm, two-handed: into the backpack; a one-handed
    one in the left hand in place of the shield, as Shattered Lands'), given once: not while it has one of that
    kind."""
    from . import npcitems
    if len(chosen) < 2 or any(specialize.kind_of(_type(i)) == chosen[1] for _, i, _ in gd._worn(member)):
        return []
    weapon = plain(gd, sheet, chosen[1], read)
    if weapon is None:
        return []
    who, left = gd.creature_name(member), game.WEAPON_HANDS[1]
    what = specialize.KINDS[chosen[1]]
    hand = next((i for _, i, _ in gd._worn(member) if i[game.ITEM_SLOT] == game.WEAPON_HANDS[0]), None)
    if chosen[1] not in ravfirstweapon.MISSILE_KINDS and not weaponchoice.two_handed(gd, sheet, weapon.type) \
            and not (hand is not None and weaponchoice.two_handed(gd, sheet, _type(hand))):
        shield = weaponchoice._shield_away(gd, list(gd._worn(member)))
        if not any(i[game.ITEM_SLOT] == left for _, i, _ in gd._worn(member)) \
                and npcitems.add_to(gd, member, weapon.record, left):
            instead = f", in place of the {shield}" if shield else ""
            return [f"{who} starts with a plain {what} in the left hand{instead}: a Myrmidon's second weapon spec"]
    slot = weaponchoice.MISSILE_SLOT if chosen[1] in ravfirstweapon.MISSILE_KINDS \
        and not any(i[game.ITEM_SLOT] == weaponchoice.MISSILE_SLOT for _, i, _ in gd._worn(member)) else None
    if not npcitems.add_to(gd, member, weapon.record, slot):
        return []
    where = "" if slot is not None else " in the backpack"
    return [f"{who} starts with a plain {what}{where} too: a Myrmidon's second weapon spec"]


def _poisoner_blades(gd, member: int, sheet: bytes, read, chosen: List[int], new_items: bool) -> List[str]:
    """A Poisoner's two blades of its weapon spec (the dagger or the short sword; the dagger if none is picked),
    one in each hand (weaponchoice._poisoner_daggers'): the right hand's weapon made one (made_like), and a second
    in the left in place of its shield (or of the other blade): lines for the log. Made once: not while it holds
    one of that kind in the left hand."""
    from . import kits, npcitems, ring
    right, left = game.WEAPON_HANDS
    kind = chosen[0] if chosen and chosen[0] in kits.POISONER_KINDS else kits.DAGGER
    kind_of = lambda item: specialize.kind_of(_type(item))
    if any(i[game.ITEM_SLOT] == left and kind_of(i) == kind for _, i, _ in gd._worn(member)):
        return []
    out = _in_hand(gd, member, sheet, read, kind, new_items, "a Poisoner fights with two of its weapon spec")
    blade = next((i for _, i, _ in gd._worn(member) if i[game.ITEM_SLOT] == right), None)
    if blade is None or kind_of(blade) != kind:
        return out
    who, name = gd.creature_name(member), lambda item: gd.item_name(struct.unpack_from("<H", item, game.ITEM_NAME)[0])
    items = game.far_pointer(gd.guest, gd.ds, game.ITEMS_PTR)
    for item_index, item, _ in gd._worn(member):  # (the other blade, given before its spec was changed)
        if item[game.ITEM_SLOT] == left and kind_of(item) in kits.POISONER_KINDS:
            gd.guest.write(items + item_index * game.ITEM_SIZE, ravfirstweapon.made_over(item, Weapon(_type(blade), blade)))
            return out + [f"{who} starts with a second {name(blade)} in the left hand in place of the {name(item)}: a "
                          f"Poisoner fights with two of its weapon spec"]
    shield = None
    for item_index, item, _ in list(gd._worn(member)):
        if item[game.ITEM_SLOT] == left and read(_type(item))[0] & kits.SHIELD \
                and ring.unlink(gd, ring.Items(gd), item_index, "kit gear", empty=True):
            shield = name(item)
    if any(i[game.ITEM_SLOT] == left for _, i, _ in gd._worn(member)) or not npcitems.add_to(gd, member, blade, left):
        return out
    instead = f", in place of the {shield}" if shield else ""
    return out + [f"{who} starts with a second {name(blade)} in the left hand{instead}: a Poisoner fights with two "
                  f"of its weapon spec"]
