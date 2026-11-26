"""A new warrior's starting weapon in Wake of the Ravager: a +1 weapon of its first weapon-spec pick (Daaki,
2026-11-26).

Shattered Lands' Loader makes the game's bone long sword in hand a plain weapon of a new character's first
weapon kind (weaponchoice.finish_new). The sequel starts its warriors with magic weapons already (its starting
gear's table, ravager.GEAR_TABLE: a fighter's and a gladiator's long sword +1, a thri-kreen's gythka +1 and
chatkcha +1; a ranger's plain long sword), so here the weapon becomes a **+1 weapon of the first pick's kind**:

- a melee pick: the weapon in hand (the right hand's, as ravager.GEAR_HANDS puts it; else the left's) made it,
  or one put in the right hand where neither holds a weapon; a two-handed one sends what the other hand
  holds to the backpack (a fighter's shield, a gladiator's second long sword); a gladiator's left-hand long
  sword stays otherwise;
- a missile pick (the bow, sling, staff sling, javelin and darts, and the chatkcha, which the sequel's own
  thri-kreen carries in the missile slot): the missile slot's weapon made it, or one put there; a bow with
  the sequel's +1 arrows (as its ranger starts); the weapon in hand stays as it is;
- a weapon that is that already (a fighter's or gladiator's long sword +1 for a long sword pick, a
  thri-kreen's gythka or chatkcha for its own kind) stays as it is.

Only those with a first pick (the warriors and the warrior kits that the weapon window asks: DSCLOG2's
WP_ASK). It runs on DSCLOG2's GEAR_DONE while DONE waits (ravlog's _gear_pass), after the weapon window
(CR_WEAPONS) and the game's gear (6F197h, with GEAR_HANDS), before startgear.fill, which then finds the hands
filled.

**The +1 weapons** (PLUS_ONE): the sequel's own +1 item of the kind where it has one (OBJEX.GFF's objects:
its first item record), else the mod's (ravgear.MAGIC's "+1", made only with the new items: NEW), else the
sequel's plain weapon of the kind with a plus of 1 (MADE: its own picture and name; the sequel's names show no
plus, the game adds it). By kind: long sword 633, dagger 631 (stone), mace 634 (bone), axe 635 (metal),
quarterstaff 632, gythka 630, chatkcha 733, sling 734, lotulis 637, double spear 636, darts 732 (the
sequel's); short sword, great axe, pick and polearm (metal) and cahulaks and staff sling +1 (the mod's); club
609, two-handed sword 604, trikal 601 and javelin 702 made +1 (none in either); the bow the plain 700 with the
+1 arrows 730 (none). Then the same kind in other materials made +1 (a fire cleric/fighter's obsidian long
sword), for one who can't use the first (restrict.usable).
"""

import struct
from typing import Callable, Dict, List, NamedTuple, Optional, Tuple

from . import game, restrict, specialize, weaponchoice

KIND = specialize.KINDS.index
MADE_VALUE = 20800  # (a plain weapon made +1: the mod's price of a magic melee weapon's plus, ravgear.MELEE_PLUS)
ITEM_PICTURE, ITEM_COUNT, ITEM_VALUE, ITEM_ICON, ITEM_POWER, ITEM_SIZE_BYTE = 0x00, 0x02, 0x06, 0x0C, 0x10, 0x12
# (the sequel's item record, 17h bytes: the picture (the object, negated), the count, the value, the type
# (+0Ah), the game's cache of its icon, the spell (+10h), a byte the game's records vary by weapon, the slot
# (+13h), the name (+14h) and the plus (+16h))


class Weapon(NamedTuple):
    """A +1 weapon for a pick: its type, its item record, whether it is the mod's (ravgear's: only with the
    new items) and whether it is a plain one made +1 here."""
    type: int
    record: bytes
    new: bool = False
    made: bool = False


def _rec(hexed: str) -> bytes:
    return bytes.fromhex(hexed)


def _made(type_: int, hexed: str) -> Weapon:
    rec = bytearray(_rec(hexed))
    struct.pack_into("<H", rec, ITEM_VALUE, MADE_VALUE)
    rec[0x16] = 1
    return Weapon(type_, bytes(rec), made=True)


# By kind (specialize.KINDS), in the order tried. The sequel's records: OBJEX.GFF's object's first item record
# (in no list, no slot; test_ravfirstweapon checks them against the player's file); the mod's: ravgear.item_record's
PLUS_ONE: Dict[int, Tuple[Weapon, ...]] = {
    KIND("long sword"): (Weapon(97, _rec("87fd00000f2730750f27610000000000000005ff1a0001")),   # 633, metal
                         _made(73, "9afd00000f274b000f27490000000000000004ff1a0000")),          # 614, obsidian
    KIND("club"): (_made(29, "9ffd00000f2701000f271d0000000000000004ff210000"),),                # 609
    KIND("dagger"): (Weapon(37, _rec("89fd00000f2710270f27250000000000000005ff1d0001")),       # 631, stone
                     _made(72, "9cfd00000f270a000f27480000000000000004ff1d0000")),              # 612, obsidian
    KIND("short sword"): (Weapon(109, _rec("44b200000f2740510f276d0000000000000004ff020101"), new=True),),  # metal
    KIND("mace"): (Weapon(67, _rec("86fd00000f27204e0f27430000000000000005ff1c0001")),         # 634, bone
                   Weapon(74, _rec("2aa800000f2740510f274a0000000000000004ff1c0001"), new=True, made=True)),  # obsidian
    KIND("axe"): (Weapon(8, _rec("85fd00000f27204e0f27080000000000000005ff1f0001")),           # 635, metal
                  _made(48, "8bfd00000f270f000f27300000000000000005ff1f0000")),                 # 629, obsidian
    KIND("great axe"): (Weapon(113, _rec("e2a700000f2740510f27710000000000000005ff200001"), new=True),  # metal
                        _made(51, "a0fd00000f27f4010f27330000000000000005ff200000")),           # 608, obsidian
    KIND("pick"): (Weapon(114, _rec("41b200000f2740510f27720000000000000006ff220001"), new=True),  # metal
                   _made(79, "8cfd00000f2732000f274f0000000000000006ff220000")),                # 628, stone
    KIND("quarterstaff"): (Weapon(85, _rec("88fd00000f27983a0f27550000000000000005ff320001")),  # 632
                           ),
    KIND("polearm"): (Weapon(115, _rec("d6a700000f2740510f27730000000000000004ff190001"), new=True),  # metal
                      _made(80, "a2fd00000f2707000f27500000000000000004ff190000")),             # 606, bone
    KIND("gythka"): (Weapon(52, _rec("8afd00000f2740510f27340000000000000005ff160001")),       # 630
                     ),
    KIND("cahulaks"): (Weapon(24, _rec("3eb200000f27502d0f27180000000000000004ff310001"), new=True),  # bone
                       _made(24, "9dfd00000f2701000f27180000000000000004ff310000")),            # 611
    KIND("chatkcha"): (Weapon(25, _rec("23fd00000f27fa000f27190000000000000005ff170001")),     # 733
                       ),
    KIND("bow"): (Weapon(18, _rec("44fd00000f271e000f27120000000000000004ff340000")),          # 700 (+1 arrows)
                  ),
    KIND("sling"): (Weapon(93, _rec("22fd00000f27f00a0f275d0000000000000005ff350001")),        # 734
                    ),
    KIND("staff sling"): (Weapon(98, _rec("1ea800000f27f00a0f27620000000000000004ff330001"), new=True),
                          _made(98, "3efd00000f2702000f27620000000000000004ff330000")),         # 706
    KIND("two-handed sword"): (_made(101, "a4fd00000f27dc050f27650000000000000005ff380000"),),  # 604
    KIND("lotulis"): (Weapon(61, _rec("83fd00000f27983a0f273d0000000000000005ff180001")),      # 637
                      ),
    KIND("double spear"): (Weapon(39, _rec("84fd00000f27983a0f27270000000000000005ff370001")),  # 636
                           ),
    KIND("trikal"): (_made(100, "a7fd00000f2718000f27640000000000000006ff360000"),),            # 601
    KIND("javelin"): (_made(59, "42fd00000f2732000f273b0000000000000004ff1b0000"),),             # 702
    KIND("darts"): (Weapon(38, _rec("24fd0a000f27d0070f27260000000000000005ff230001")),        # 732
                    ),
}
ARROWS_PLUS_ONE = _rec("26fd0c000f2778000f27060000000000000005ff1e0001")  # (730: a ranger's, 12)
# The kinds that go to the missile slot: Shattered Lands' missile kinds, and the chatkcha (the sequel's
# thri-kreen carries its own there)
MISSILE_KINDS = weaponchoice.MISSILE_KINDS | {KIND("chatkcha")}
NEW_PLUS_ONE = frozenset(w.type for ws in PLUS_ONE.values() for w in ws if w.new)


def choice(gd, sheet: bytes, kind: int, read: Callable[[int], bytes], new_items: bool = True) -> Optional[Weapon]:
    """The +1 weapon of KIND the character can use (PLUS_ONE's first; the mod's only with NEW_ITEMS), or None."""
    for weapon in PLUS_ONE.get(kind, ()):
        if weapon.new and not new_items:
            continue
        typ = read(weapon.type)
        if len(typ) >= game.ITEM_TYPE_SIZE and restrict.usable(sheet, weapon.type, typ):
            return weapon
    return None


def made_over(old: bytes, weapon: Weapon) -> bytes:
    """Item record OLD made WEAPON: its picture, count, value, type, spell, name and plus WEAPON's, the icon
    cache cleared (the game loads it anew); its place in its list and its slot kept."""
    rec = bytearray(old)
    new = weapon.record
    for at, size in ((ITEM_PICTURE, 2), (ITEM_COUNT, 2), (ITEM_VALUE, 2), (game.ITEM_TYPE, 2), (ITEM_POWER, 2),
                     (ITEM_SIZE_BYTE, 1), (game.ITEM_NAME, 2), (game.ITEM_PLUS, 1)):
        rec[at:at + size] = new[at:at + size]
    struct.pack_into("<H", rec, ITEM_ICON, 0)
    return bytes(rec)


def fill(gd, new_items: bool = True) -> List[str]:
    """The party's New characters with a first weapon pick given a +1 weapon of its kind (the module's
    notes): lines for the log. NEW_ITEMS: whether the mod's new items are in the game (ravgear's)."""
    out: List[str] = []
    for member in range(game.PARTY_SIZE):
        rec = gd.creature(member)
        if len(rec) < game.CREATURE_SIZE or not rec[game.CREATURE_NAME] or not game.being_new(gd, rec):
            continue
        out += fill_member(gd, member, new_items)
    return out


def fill_member(gd, member: int, new_items: bool = True) -> List[str]:
    """Party member MEMBER's weapon made a +1 of its first pick's kind, if it has a pick: lines for the log."""
    from . import npcitems, pickpocket, ring
    sheets = game.table_pointer(gd.guest, gd.ds, game.SHEETS_PTR)
    types = game.far_pointer(gd.guest, gd.ds, game.ITEM_TYPES_PTR)
    items = game.far_pointer(gd.guest, gd.ds, game.ITEMS_PTR)
    read: Callable[[int], bytes] = lambda t: gd.guest.read(types + t * game.ITEM_TYPE_SIZE, game.ITEM_TYPE_SIZE)
    rec = gd.creature(member)
    index = struct.unpack_from("<H", rec, game.CREATURE_SHEET_INDEX)[0]
    sheet = gd.guest.read(sheets + index * game.SHEET_SIZE, game.SHEET_SIZE)
    owned = list(gd._worn(member))
    if len(sheet) < game.SHEET_SIZE or not owned:
        return []  # (no gear yet: the game gives it at DONE)
    first = game.spec_kinds(sheet)[0]
    if not first:
        return []
    kind = first - 1
    who, what = gd.creature_name(member), specialize.KINDS[kind]
    weapon = choice(gd, sheet, kind, read, new_items)
    if weapon is None:
        return [f"{who} keeps the starting weapon: no {what} +1 it can use"]
    type_of = lambda item: struct.unpack_from("<H", item, game.ITEM_TYPE)[0]
    at = lambda slot: next(((i, item) for i, item, _ in owned if item[game.ITEM_SLOT] == slot), None)
    right, left = game.WEAPON_HANDS
    out: List[str] = []
    if kind in MISSILE_KINDS:
        hold = [(weaponchoice.MISSILE_SLOT, at(weaponchoice.MISSILE_SLOT))]
    else:
        melee = lambda found: found is not None and bool(read(type_of(found[1]))[0] & restrict.MELEE)
        hold = [(h, at(h)) for h in (right, left) if melee(at(h))][:1] or [(right, at(right))]
    slot, held = hold[0]
    if held is not None and type_of(held[1]) == weapon.type and held[1][game.ITEM_PLUS] >= 1:
        return []  # (that already: a fighter's long sword +1, a thri-kreen's gythka)
    name = lambda item: gd.item_name(struct.unpack_from("<H", item, game.ITEM_NAME)[0])
    given = what if kind == weaponchoice.BOW else f"{what} +1"  # (no bow +1: +1 arrows with it)
    if held is not None:
        was = name(held[1])
        gd.guest.write(items + held[0] * game.ITEM_SIZE, made_over(held[1], weapon))
        line = f"{who} starts with a {given} for the weapon specialization chosen, in place of the {was}"
    elif npcitems.add_to(gd, member, weapon.record, slot):
        line = f"{who} starts with a {given} for the weapon specialization chosen"
    else:
        return [f"{who} keeps the starting weapon: no room for a {what} +1"]
    if weapon.made:
        line += " (a plain one made +1: the game has no " + what + " +1)"
    out.append(line)
    if kind == weaponchoice.BOW:
        if at(weaponchoice.AMMO_SLOT) is None and npcitems.add_to(gd, member, ARROWS_PLUS_ONE, weaponchoice.AMMO_SLOT):
            out.append(f"    {who} has +1 arrows with it")
        weaponchoice.bow_ahead(gd, member)
    if slot in (right, left) and weaponchoice.two_handed(gd, sheet, weapon.type):
        other = at(left if slot == right else right)
        if other is not None:
            cell = pickpocket.free_cell(gd, ring.Items(gd), member)
            if cell is not None and pickpocket.place(gd, member, other[0], cell):
                out.append(f"    {who}'s {name(other[1])} goes into the backpack: the weapon takes both hands")
    return out
