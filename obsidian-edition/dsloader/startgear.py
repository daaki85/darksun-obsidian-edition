"""New characters' starting gear filled out (the Options tab's "Fuller starting gear").

The game gives a character of several classes one class's gear only (a fighter's or ranger's,
else a cleric's, a thief's, a psionicist's, a preserver's, a druid's), and the class rules
(restrict.py) then take away what its classes can't use: a thief/psionicist was left with no
melee weapon, an air or fire cleric with no weapon at all. Before a New character is first played,
once the game has given its gear (and the class, weapon and kit rules have had theirs: weaponchoice.py),
the Loader:

- puts a melee weapon in its right hand if that is empty: one from its backpack (a cleric's club),
  else a plain one it can use (its weapon spec's kind first; then a short sword, club, mace,
  dagger or quarterstaff, a cleric the club and mace first; else a chatkcha), of a material it
  can use (a fire cleric's obsidian mace, an air cleric's obsidian dagger);
- with the class restrictions, takes a multiclass preserver's armour off into the backpack (it
  can't cast in it; the shield stays);
- gives a sling for the missile slot to one with no missile weapon (a fire cleric, who can't use
  one, an obsidian chatkcha for the backpack);
- fills its empty chest, arm and leg slots with leather armour, where it may wear it (not a
  multiclass preserver, for its spells);
- gives it a plain belt and boots, a Stalker or a ranger a plain cloak, and a dagger for the
  backpack.

Each item only where the character can use it (its classes' lists, the class restrictions if in
force, its kit's) and has nothing of the kind already: so given once.
"""

import struct
from typing import Callable, List, Optional, Tuple

from . import game, npcitems, restrict, specialize, weaponchoice

KIND = specialize.KINDS.index
SLOT = game.EQUIP_SLOTS.index
RIGHT, LEFT = game.WEAPON_HANDS
BACKPACK = 14  # (the first backpack cell: 0-13 are worn)
# the game's own plain items (SEGOBJEX's templates): leather chest, arm and leg armour, a belt,
# boots, a cloak; and the bone long sword the plain weapons are made from (worldgear.TEMPLATE)
LEATHER = ((SLOT("chest"), npcitems._item("02fc000000000a00000006000000000004ff070000")),
           (SLOT("arm"), npcitems._item("01fc000000001400000007000000000004ff080000")),
           (SLOT("legs"), npcitems._item("fefb000000001400000008000000000004ff090000")))
BELT = npcitems._item("e6fb00000000010000002a000000000005ff2a0000")
BOOTS = npcitems._item("e5fb000000000100000044000000000005ff2b0000")
CLOAK = npcitems._item("e3fb000000001400000041003500000003ff0e0000")
WEAPON = npcitems._item("0cfc000000002d000000510000000000" "04ff1c0000")
# the right hand's weapon, kind by kind, after the weapon spec's
# (the chatkcha last, thrown from the hand, for one that can use no melee weapon at all)
HAND_ORDER = tuple(KIND(k) for k in ("short sword", "club", "mace", "dagger", "quarterstaff", "chatkcha"))
CLERIC_HAND_ORDER = tuple(KIND(k) for k in ("club", "mace", "dagger", "short sword", "quarterstaff", "chatkcha"))


def _type(rec: bytes) -> int:
    return struct.unpack_from("<H", rec, game.ITEM_TYPE)[0]


def can_use(gd, sheet: bytes, type_: int, typ: bytes) -> bool:
    """Whether the character can use an item type: the game's class lists (or its kit allowing it)
    and, the class restrictions in force, theirs; never what its kit forbids."""
    if len(typ) < game.ITEM_TYPE_SIZE:
        return False
    if gd.rules & game.RULE_RESTRICT:
        return restrict.usable(sheet, type_, typ)
    flags = int.from_bytes(sheet[game.SHEET_FLAGS:game.SHEET_FLAGS + 2], "little")
    lets = int.from_bytes(typ[restrict.TYPE_CLASSES:restrict.TYPE_CLASSES + 2], "little") & flags
    return (bool(lets) or restrict.kit_allows(sheet, type_, typ)) and not restrict.kit_forbids(sheet, type_, typ)


def preserver_bare(sheet: bytes) -> bool:
    """A multiclass preserver: no spells while it wears armour (restrict.no_spells)."""
    classes = [c for c in sheet[game.SHEET_CLASSES:game.SHEET_CLASSES + 3] if c]
    return sheet[game.SHEET_RACE] != game.HUMAN and len(classes) > 1 and restrict.PRESERVER in classes


def _weapon(gd, sheet: bytes, kind: int, read) -> Optional[Tuple[bytes, Tuple[int, int, int, int]]]:
    """A plain weapon of a kind in the first material the character can use: (record, weapon)."""
    for weapon in (weaponchoice.PLAIN[kind],) + weaponchoice.OTHERS.get(kind, ()):
        if can_use(gd, sheet, weapon[0], read(weapon[0])):
            return weaponchoice.plain_weapon(WEAPON, kind, weapon)[0], weapon
    return None


def fill(gd) -> List[str]:
    """The party's New characters' starting gear filled out (the module's notes): lines for the log."""
    from . import pickpocket, ring
    out: List[str] = []
    sheets = game.far_pointer(gd.guest, gd.ds, game.SHEETS_PTR)
    items = game.far_pointer(gd.guest, gd.ds, game.ITEMS_PTR)
    types = game.far_pointer(gd.guest, gd.ds, game.ITEM_TYPES_PTR)
    read: Callable[[int], bytes] = lambda t: gd.guest.read(types + t * game.ITEM_TYPE_SIZE, game.ITEM_TYPE_SIZE)
    name = lambda rec: gd.item_name(struct.unpack_from("<H", rec, game.ITEM_NAME)[0])
    for member in range(game.PARTY_SIZE):
        rec = gd.creature(member)
        if len(rec) < game.CREATURE_SIZE or not rec[game.CREATURE_NAME] or rec[game.CREATURE_STATUS] != game.STATUS_NEW:
            continue
        index = struct.unpack_from("<H", rec, game.CREATURE_SHEET_INDEX)[0]
        sheet = gd.guest.read(sheets + index * game.SHEET_SIZE, game.SHEET_SIZE)
        owned = list(gd._worn(member))
        if len(sheet) < game.SHEET_SIZE or not owned:
            continue  # (no gear yet: the game gives it when the character is made)
        who = gd.creature_name(member)
        classes = [c for c in sheet[game.SHEET_CLASSES:game.SHEET_CLASSES + 3] if c]
        given: List[str] = []

        def mine():
            return list(gd._worn(member))

        def slot_free(slot: int) -> bool:
            return not any(item[game.ITEM_SLOT] == slot for _, item, _ in mine())

        def give(rec_: bytes, slot: Optional[int], where: str = "") -> bool:
            if slot is not None and not slot_free(slot):
                return False
            if not npcitems.add_to(gd, member, rec_, slot):
                return False
            given.append(f"{gd.item_name(struct.unpack_from('<H', rec_, game.ITEM_NAME)[0])}{where}")
            return True

        # a multiclass preserver's armour off, into the backpack
        if gd.rules & game.RULE_RESTRICT and preserver_bare(sheet):
            for item_index, item, _ in owned:
                if item[game.ITEM_SLOT] < BACKPACK and restrict.is_armour(read(_type(item))):
                    cell = pickpocket.free_cell(gd, ring.Items(gd), member)
                    if cell is None:
                        break
                    gd.guest.write(items + item_index * game.ITEM_SIZE + game.ITEM_SLOT, bytes((cell,)))
                    out.append(f"{who}'s {name(item)} goes into the backpack: a multiclass preserver can't "
                               f"cast in armour")

        # a melee weapon in the right hand
        melee = lambda item: bool(read(_type(item))[0] & restrict.MELEE) and can_use(gd, sheet, _type(item), read(_type(item)))
        both = lambda t: weaponchoice.two_handed(gd, sheet, t) and not slot_free(LEFT)
        if slot_free(RIGHT):
            spare = next(((i, item) for i, item, _ in mine() if item[game.ITEM_SLOT] >= BACKPACK and melee(item)
                          and not both(_type(item))), None)
            if spare is not None:
                gd.guest.write(items + spare[0] * game.ITEM_SIZE + game.ITEM_SLOT, bytes((RIGHT,)))
                out.append(f"{who} takes the {name(spare[1])} from the backpack in hand")
            else:
                cleric = any(c in restrict.CLERICS for c in classes)
                chosen = [k - 1 for k in sheet[game.SPEC_SLOTS:game.SPEC_SLOTS + game.SPEC_COUNT]
                          if k and k - 1 not in weaponchoice.MISSILE_KINDS]
                for kind in chosen + list(CLERIC_HAND_ORDER if cleric else HAND_ORDER):
                    new = _weapon(gd, sheet, kind, read)
                    if new is not None and read(new[1][0])[0] & (restrict.MELEE | restrict.THROWN) \
                            and not both(new[1][0]):
                        give(new[0], RIGHT, " (in hand)")
                        break

        # a missile weapon
        if not any(specialize.kind_of(_type(item)) in weaponchoice.MISSILE_KINDS for _, item, _ in mine()):
            sling = _weapon(gd, sheet, KIND("sling"), read)
            if sling is not None:
                give(sling[0], weaponchoice.MISSILE_SLOT)
            elif not any(specialize.kind_of(_type(item)) == KIND("chatkcha") for _, item, _ in mine()):
                chatkcha = _weapon(gd, sheet, KIND("chatkcha"), read)
                if chatkcha is not None:
                    give(chatkcha[0], None)

        # leather armour, a belt, boots, a cloak
        wear = [] if gd.rules & game.RULE_RESTRICT and preserver_bare(sheet) else list(LEATHER)
        wear += [(SLOT("waist"), BELT), (SLOT("foot"), BOOTS)]
        from . import kitpages, kits
        stalker = bool(game.RULES_IN_FORCE & game.RULE_KITS) and kits.STALKER in kitpages.kit_ids(sheet)
        if stalker or any(c in restrict.RANGERS for c in classes):
            wear.append((SLOT("cloak"), CLOAK))
        for slot, item in wear:
            if not any(_type(i) == _type(item) for _, i, _ in mine()) and can_use(gd, sheet, _type(item), read(_type(item))):
                give(item, slot)

        # a dagger for the backpack
        if not any(specialize.kind_of(_type(item)) == KIND("dagger") for _, item, _ in mine()):
            dagger = _weapon(gd, sheet, KIND("dagger"), read)
            if dagger is not None:
                give(dagger[0], None, " (in the backpack)")
        if given:
            out.append(f"{who} starts with more gear: {', '.join(given)}")
    return out
