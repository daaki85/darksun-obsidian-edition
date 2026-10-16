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
- gives a sling for the missile slot to one with no missile weapon (a Battle Dancer or Spellarcher a bow and
  arrows; a fire cleric, who can't use one, an obsidian chatkcha for the backpack);
- fills its empty chest, arm and leg slots with leather armour, where it may wear it (not a
  multiclass preserver, for its spells);
- gives a Stalker, Assassin or Shinobi a plain cloak.

A thri-kreen is given nothing more than the game's own starting gear (K'ratchek keeps her
chatkcha): its claws serve it better than another weapon, and it wears no armour or cloak.

The game's own party (Gerakis, K'ratchek, Cermak, Cilla: already Okay) has it too, once, as the
game starts (defaultparty.py).

Each item only where the character can use it (its classes' lists, the class restrictions if in
force, its kit's) and has nothing of the kind already: so given once.
"""

import struct
from typing import Callable, List, Optional, Tuple

from . import game, kits, npcitems, restrict, specialize, weaponchoice

KIND = specialize.KINDS.index
SLOT = game.EQUIP_SLOTS.index
RIGHT, LEFT = game.WEAPON_HANDS
BACKPACK = 14  # (the first backpack cell: 0-13 are worn)
THRI_KREEN = 8  # (the race: given nothing, its claws better than a weapon; it wears no armour
                #   or cloak)
# the game's own plain items (SEGOBJEX's templates): leather chest, arm and leg armour, a cloak;
# and the bone long sword the plain weapons are made from (worldgear.TEMPLATE)
LEATHER = ((SLOT("chest"), npcitems._item("02fc000000000a00000006000000000004ff070000")),
           (SLOT("arm"), npcitems._item("01fc000000001400000007000000000004ff080000")),
           (SLOT("legs"), npcitems._item("fefb000000001400000008000000000004ff090000")))
CLOAK = npcitems._item("e3fb000000001400000041003500000003ff0e0000")
CLOAK_KITS = frozenset((kits.STALKER, kits.ASSASSIN, kits.SHINOBI))  # (given a cloak)
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
    out: List[str] = []
    for member in range(game.PARTY_SIZE):
        rec = gd.creature(member)
        if len(rec) < game.CREATURE_SIZE or not rec[game.CREATURE_NAME] or rec[game.CREATURE_STATUS] != game.STATUS_NEW:
            continue
        out += fill_member(gd, member)
    return out


def fill_member(gd, member: int) -> List[str]:
    """Party member MEMBER's starting gear filled out, if it has some (the game's own party too:
    defaultparty.py): lines for the log."""
    from . import pickpocket, ring
    out: List[str] = []
    sheets = game.far_pointer(gd.guest, gd.ds, game.SHEETS_PTR)
    items = game.far_pointer(gd.guest, gd.ds, game.ITEMS_PTR)
    types = game.far_pointer(gd.guest, gd.ds, game.ITEM_TYPES_PTR)
    read: Callable[[int], bytes] = lambda t: gd.guest.read(types + t * game.ITEM_TYPE_SIZE, game.ITEM_TYPE_SIZE)
    name = lambda rec: gd.item_name(struct.unpack_from("<H", rec, game.ITEM_NAME)[0])
    rec = gd.creature(member)
    index = struct.unpack_from("<H", rec, game.CREATURE_SHEET_INDEX)[0]
    sheet = gd.guest.read(sheets + index * game.SHEET_SIZE, game.SHEET_SIZE)
    owned = list(gd._worn(member))
    if len(sheet) < game.SHEET_SIZE or not owned:
        return out  # (no gear yet: the game gives it when the character is made)
    if sheet[game.SHEET_RACE] == THRI_KREEN:
        return out  # (its claws serve it better than a weapon, and it wears none of the rest)
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
                pickpocket.place(gd, member, item_index, cell)
                out.append(f"{who}'s {name(item)} goes into the backpack: a multiclass preserver can't "
                           f"cast in armour")

    # a melee weapon in the right hand
    melee = lambda item: bool(read(_type(item))[0] & restrict.MELEE) and can_use(gd, sheet, _type(item), read(_type(item)))
    both = lambda t: weaponchoice.two_handed(gd, sheet, t) and not slot_free(LEFT)
    if slot_free(RIGHT):
        spare = next(((i, item) for i, item, _ in mine() if item[game.ITEM_SLOT] >= BACKPACK and melee(item)
                      and not both(_type(item))), None)
        if spare is not None:
            pickpocket.place(gd, member, spare[0], RIGHT)
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

    # a missile weapon (a Battle Dancer's or Spellarcher's the bow, with arrows: kits.DANCER_KINDS)
    if not any(specialize.kind_of(_type(item)) in weaponchoice.MISSILE_KINDS for _, item, _ in mine()):
        from . import kitpages
        dancer = bool(game.RULES_IN_FORCE & game.RULE_KITS) \
            and bool({kits.BATTLE_DANCER, kits.SPELLARCHER} & set(kitpages.kit_ids(sheet)))
        bow = _weapon(gd, sheet, KIND("bow"), read) if dancer else None
        sling = _weapon(gd, sheet, KIND("sling"), read)
        if bow is not None:
            if give(bow[0], weaponchoice.MISSILE_SLOT):
                give(weaponchoice.arrows(bow[0]), weaponchoice.AMMO_SLOT)
        elif sling is not None:
            give(sling[0], weaponchoice.MISSILE_SLOT)
        elif not any(specialize.kind_of(_type(item)) == KIND("chatkcha") for _, item, _ in mine()):
            chatkcha = _weapon(gd, sheet, KIND("chatkcha"), read)
            if chatkcha is not None:
                give(chatkcha[0], None)

    # leather armour, and a cloak for the kits that hide
    wear = [] if gd.rules & game.RULE_RESTRICT and preserver_bare(sheet) else list(LEATHER)
    from . import kitpages
    if game.RULES_IN_FORCE & game.RULE_KITS and set(kitpages.kit_ids(sheet)) & CLOAK_KITS:
        wear.append((SLOT("cloak"), CLOAK))
    for slot, item in wear:
        if not any(_type(i) == _type(item) for _, i, _ in mine()) and can_use(gd, sheet, _type(item), read(_type(item))):
            give(item, slot)

    if given:
        out.append(f"{who} starts with more gear: {', '.join(given)}")
    return out
