"""The mod's new items in Wake of the Ravager: its plain weapons and the Bone Helm, and magic weapons for
the weapon specs the sequel has too few of (Daaki, 2026-11-25).

The sequel has no short sword at all and no magic pick, and one magic great axe, cahulaks, staff sling
and polearm each, found late or only as random loot (FEATURES.md's "Magic weapons for every spec" has where). Of
the mod's new plain items in Shattered Lands (ITEMS.md's "new" rows) it has only an obsidian axe and an
obsidian great axe of its own. Here:

- PLAIN: the mod's plain weapons the sequel lacks (bone, metal and obsidian short swords, bone and metal
  daggers, metal and obsidian maces, a bone axe, bone and metal great axes, a metal pick and polearm,
  metal and obsidian cahulaks) and the Bone Helm, of the mod's item types the Loader already adds to the
  sequel (ravager.mod_type) or the sequel's own (its obsidian mace's, 74);
- MAGIC: fourteen magic weapons, named as the sequel names its own (the game adds the material: "Metal
  Short Sword"; its own plus shows in no name), from early Tyr to its late regions;
- WHERE: the people and things that carry or sell them. A shop's stock is its seller's items (the
  Weaponer, the Armorers, the Salespersons, Notaku), a person's loot their items, a body's or a crate's
  its contents: each such object's record (OBJEX.GFF's RDFF) has the new items after its own, in its pack
  (the list whose first item's header flags are PACK; the sequel's people hold their weapon in a list of
  17 and wear armour in one of 16), so the game makes them with the object.

Their pictures are Shattered Lands' (the Loader's own icons, icons.new_chunks, made from the player's
SEGOBJEX.GFF; the magic ones a few pixels of the blade or head in the fire colours, as the mod's
own), each colour the nearest of the sequel's stable ones (ravitems.picture): nothing from either game is
in the repository. Each picture is an object of its own: the party transfer's number for the same
Shattered Lands object (ravitems.own_object, so a transfer that brings one makes the same), or OWN_ICONS'
for the magic ones drawn here. New games only: a saved game keeps the people and things it has made (shopstock.py tops up its sellers).

BOOKS: spellbooks of the mod's six new wizard spells (ravspells, 320-325), with the new spells' switch. In
Shattered Lands Kalzith sells Cat's Grace (kalzith.SCROLLS, 6000) and a defiler's body may hold a scroll of any
of them (defilerscrolls, champions.SCROLL_SPELLS: Fogbolt, Spook, Reflected Image); the sequel's one seller of
spellbooks is Notaku in Tyr (his own a 3rd-level book), so he sells all six, at the sequel's and Shattered Lands'
price, 3000 a level, and three of the sequel's wizards who carry a spellbook carry one more (BOOK_WHERE). Each
book is an object of its own (BOOK_OBJECT on, as a shop shows items of one object as one), a copy of the
sequel's spellbook of its level (31002, 31010: the book's picture, BMP 1969, its OJFF's), in the numbers the
game teaches from (31000-31199: a 313xx object is a one-use scroll, cast); its power, the spell + 1, is what it
teaches (DSCLOG2's NS_SCROLL).
"""

import struct
from typing import Callable, Dict, List, NamedTuple, Optional, Sequence, Tuple

from . import dataitems, game, gff, icons, ravitems, ravspells

PACK, NEXT_FLAGS = 4, 2  # (the item lists' first record's header flags: the pack's; each next item's)
ITEM_SPELL, ITEM_VALUE, ITEM_POWER, ITEM_PLUS = 0x02, 0x06, 0x10, 0x16  # (the sequel's item record: words, a byte)
OWN_ICONS = 19900  # (the pictures drawn here: objects 19900 on, free: ravitems' OWN_HIGH range ends at 16003 for
# Shattered Lands' highest, 32003; 13000 on drew another picture in the game, a grey ring)
SHORT_SWORD_NAME = 0x144  # (the mod's "Short Sword", names.NAMES: ravager.mod_name)
MELEE_PLUS = 20800  # (the mod's price of a magic melee weapon, a plus: ITEMS.md's Prices)


class Picture(NamedTuple):
    """An item's picture: Shattered Lands object SL's (as icons.new_chunks makes the Loader's), or, with
    MAKE, that picture drawn over (its own object, OWN_ICONS + its place in DRAWN)."""
    sl: int
    make: Optional[Callable] = None


class Gear(NamedTuple):
    """An item: its sequel type, its name (the sequel's own, by its letters, or the mod's entry), its
    value, its plus, its picture and the sequel object whose item record it is made from."""
    type: int
    name: object  # (bytes: the sequel's name of those letters; int: the mod's name entry)
    value: int
    plus: int
    picture: Picture
    like: int


def _mod(sl_type: int) -> int:
    from . import ravager
    return ravager.mod_type(sl_type)


def _blade(p, x, y):
    return p in icons.BLADE


def _every_other(test):
    return lambda p, x, y: test(p, x, y) and (x + y) % 2 == 0


def _fire(test):
    return lambda rows: icons.glow(rows, test, icons.FIRE)


# The plain items: (its key, Gear). The pictures: the Loader's Shattered Lands objects (icons.ICONS).
OBSIDIAN_MACE_TYPE = 74  # (the sequel's: its Mace +1 of Shocking Grasp's; ravager._RAV_OWN_KINDS)
PLAIN: Dict[str, Gear] = {
    "bone short sword": Gear(_mod(game.BONE_SHORT_SWORD_TYPE), SHORT_SWORD_NAME, 10, 0, Picture(2419), 614),
    "metal short sword": Gear(_mod(game.METAL_SHORT_SWORD_TYPE), SHORT_SWORD_NAME, 300, 0, Picture(2427), 614),
    "obsidian short sword": Gear(_mod(game.OBSIDIAN_SHORT_SWORD_TYPE), SHORT_SWORD_NAME, 20, 0, Picture(2488), 614),
    "bone dagger": Gear(_mod(game.BONE_DAGGER_TYPE), b"DAGGER", 2, 0, Picture(2578), 612),
    "metal dagger": Gear(_mod(game.METAL_DAGGER_TYPE), b"DAGGER", 50, 0, Picture(2504), 612),
    "metal mace": Gear(_mod(game.METAL_MACE_TYPE), b"MACE", 200, 0, Picture(2506), 610),
    "obsidian mace": Gear(OBSIDIAN_MACE_TYPE, b"MACE", 15, 0, Picture(2486), 610),
    "bone axe": Gear(_mod(game.BONE_AXE_TYPE), b"AXE", 8, 0, Picture(2421), 629),
    "bone great axe": Gear(_mod(game.BONE_GREAT_AXE_TYPE), b"GREAT AXE", 12, 0, Picture(2574), 608),
    "metal great axe": Gear(_mod(game.METAL_GREAT_AXE_TYPE), b"GREAT AXE", 300, 0, Picture(2508), 608),
    "metal pick": Gear(_mod(game.METAL_PICK_TYPE), b"PICK", 150, 0, Picture(2510), 628),
    "metal polearm": Gear(_mod(game.METAL_POLEARM_TYPE), b"POLEARM", 250, 0, Picture(2512), 606),
    "metal cahulaks": Gear(_mod(game.METAL_CAHULAKS_TYPE), b"CAHULAKS", 200, 0, Picture(2670), 611),
    "obsidian cahulaks": Gear(_mod(game.OBSIDIAN_CAHULAKS_TYPE), b"CAHULAKS", 15, 0, Picture(2674), 611),
    "bone helm": Gear(_mod(game.BONE_HELM_TYPE), b"HELM", 20, 0, Picture(2437), 830),
}

# The magic weapons: the plain ones' (or the sequel's own) with a plus. Their pictures: the mod's
# Shattered Lands magic weapons of the same kind and material where there is one (Headsman's metal
# great axe, Linebreaker's metal polearm, Thornwall's bone polearm, Emberlash's obsidian cahulaks,
# Deepbiter's stone pick, Windlash's staff sling), else the plain one's, every other pixel of its blade
# or head in the fire colours (a +3's whole blade).
_PICK_METAL = set(icons.PICK_TO_METAL.values())
_TEAL_BONE = set(icons.TEAL_TO_BONE.values())
_CAHULAKS = range(210, 214)
SEQUEL_STONE_PICK, SEQUEL_CAHULAKS, SEQUEL_STAFF_SLING = 79, 24, 98  # (the sequel's own types)
MAGIC: Dict[str, Gear] = {
    "short sword +1": PLAIN["metal short sword"]._replace(
        plus=1, value=MELEE_PLUS, picture=Picture(2427, _fire(_every_other(_blade)))),
    "short sword +2": PLAIN["obsidian short sword"]._replace(
        plus=2, value=2 * MELEE_PLUS,
        picture=Picture(2488, _fire(_every_other(lambda p, x, y: p in icons.BLADE or p in (208, 209, 210))))),
    "short sword +3": PLAIN["metal short sword"]._replace(
        plus=3, value=3 * MELEE_PLUS, picture=Picture(2427, _fire(_blade))),
    "pick +1": PLAIN["metal pick"]._replace(
        plus=1, value=MELEE_PLUS, picture=Picture(2510, _fire(_every_other(lambda p, x, y: p in _PICK_METAL)))),
    "pick +2": Gear(SEQUEL_STONE_PICK, b"PICK", 2 * MELEE_PLUS, 2, Picture(2496), 628),
    "pick +3": PLAIN["metal pick"]._replace(
        plus=3, value=3 * MELEE_PLUS, picture=Picture(2510, _fire(lambda p, x, y: p in _PICK_METAL))),
    "great axe +1": PLAIN["metal great axe"]._replace(plus=1, value=MELEE_PLUS, picture=Picture(2558)),
    "great axe +2": PLAIN["bone great axe"]._replace(
        plus=2, value=2 * MELEE_PLUS, picture=Picture(2574, _fire(_every_other(lambda p, x, y: p in _TEAL_BONE)))),
    "cahulaks +1": Gear(SEQUEL_CAHULAKS, b"CAHULAKS", 11600, 1,
                        Picture(0x10000 - 0xFB5C, _fire(_every_other(lambda p, x, y: p in _CAHULAKS))), 611),
    "cahulaks +2": PLAIN["obsidian cahulaks"]._replace(plus=2, value=2 * MELEE_PLUS, picture=Picture(2676)),
    "polearm +1": PLAIN["metal polearm"]._replace(plus=1, value=MELEE_PLUS, picture=Picture(2570)),
    "polearm +2": Gear(80, b"POLEARM", 2 * MELEE_PLUS, 2, Picture(2572), 606),
    "staff sling +1": Gear(SEQUEL_STAFF_SLING, b"STAFF SLING", 2800, 1, Picture(2498), 706),
    "staff sling +2": Gear(SEQUEL_STAFF_SLING, b"STAFF SLING", 3500, 2, Picture(2498), 706),
}
GEAR: Dict[str, Gear] = {**PLAIN, **MAGIC}

# Who carries or sells what: {the sequel's object: keys}. The shops (their sellers, in Limbo until their
# scripts bring them out): the Weaponer (153, Tyr's melee-weapon stall), the ranged-weapon stall (323),
# the Armorers (152, 322), the Salespersons with weapons in their stock (155, 320, 321), the mines' shop
# (142, the Receptionist, who sells the party its pick), Notaku (58) and Sureshot (103, Humbleton forest).
# People met once: Draxans 107 and 202 (Tyr), 502 (the Pyramid), 209 (Volcano 3), Alhena (8, the Jann),
# the Runner (7, Yuan-ti Tunnels), a Veiled Alliance guard (166), the silt giants' Leader (195). Bodies and
# a crate: the dead team from Urik (3087-3089, the Crypt), a body in the Mosaic (2217), one in the Pyramid
# (3124), a crate in the deepest mine (5164). And people of a kind who fight with the like.
WEAPONS_ALL = ("bone short sword", "metal short sword", "obsidian short sword", "bone dagger", "metal dagger",
               "metal mace", "obsidian mace", "bone axe", "bone great axe", "metal great axe", "metal polearm",
               "metal cahulaks", "obsidian cahulaks")
WHERE: Dict[int, Tuple[str, ...]] = {
    # shops
    153: WEAPONS_ALL,
    323: ("staff sling +1",),
    152: ("bone helm",),
    322: ("bone helm",),
    155: ("metal pick",),
    320: ("bone short sword", "metal short sword", "bone axe", "metal cahulaks", "metal pick"),
    321: ("obsidian short sword", "obsidian mace", "bone great axe", "obsidian cahulaks"),
    142: ("metal pick", "pick +1"),
    58: ("short sword +1",),
    103: ("staff sling +2",),
    # magic weapons' carriers
    202: ("short sword +2",),
    3087: ("short sword +3",),
    5164: ("pick +2",),
    195: ("pick +3",),
    107: ("great axe +1",),
    502: ("great axe +2",),
    8: ("cahulaks +1",),
    7: ("cahulaks +2",),
    166: ("polearm +1",),
    209: ("polearm +2",),
    # plain carriers
    98: ("bone short sword",),       # the Halfling (in Limbo: Humbleton's)
    100: ("bone dagger",),           # Irma, El's Temple
    102: ("bone axe",),              # Strongrip, Humbleton forest
    87: ("bone great axe",),         # Axestopper, Humbleton forest
    83: ("metal great axe",),        # Cleave
    263: ("metal short sword",),     # Jumah, the Crypt
    143: ("metal dagger",),          # Dhukkar, Tyr
    141: ("metal pick",),            # Arslan, Tyr (the Veiled Alliance's miner)
    122: ("metal mace",),            # a Templar in Tyr
    506: ("obsidian mace",),         # a Templar in the Pyramid
    207: ("metal polearm",),         # a Draxan with a polearm, Tyr
    516: ("metal cahulaks",),        # a Gladiator with cahulaks, the Pyramid
    203: ("obsidian cahulaks",),     # a Draxan with cahulaks
    60: ("obsidian short sword",),   # a Thief
    201: ("bone helm",),             # Draxans in the Crypt
    3088: ("metal dagger",),
    3089: ("bone helm",),
    2217: ("bone short sword",),
    3124: ("obsidian short sword",),
}


class Book(NamedTuple):
    """A spellbook of SPELL (the sequel's number): its own OBJECT, a copy of the sequel's spellbook LIKE,
    priced VALUE."""
    spell: int
    object: int
    like: int
    value: int


BOOK_OBJECT = 31190  # (free in the sequel; in its taught numbers, 31000-31199: SPELLBOOKS)
SPELLBOOKS = range(31000, 31200)
BOOK_LIKE = {1: 31002, 2: 31010}  # (the sequel's spellbooks of 1st and 2nd level, 3000 and 6000)
BOOK_PRICE = 3000  # (a level: the sequel's books and Shattered Lands' scrolls, kalzith.SCROLLS)
BOOK_LEVELS = {ravspells.GRACE: 2}  # (the others 1st: DSCLOG2's NS_LEVEL)
BOOKS: Dict[str, Book] = {
    f"{name} book": Book(spell, BOOK_OBJECT + k, BOOK_LIKE[BOOK_LEVELS.get(spell, 1)],
                         BOOK_PRICE * BOOK_LEVELS.get(spell, 1))
    for k, (spell, name) in enumerate(ravspells.SPELLS.items())}
# Notaku (Tyr's Shadow Square) sells them; three of the sequel's wizards who carry a spellbook carry one more,
# as a defiler's body in Shattered Lands may (its arena champion's Fogbolt, Spook or Reflected Image)
BOOK_WHERE: Dict[int, Tuple[str, ...]] = {
    58: tuple(BOOKS),
    160: ("Reflected Image book",),  # Fermin
    290: ("Spook book",),            # Kalaobuta
    496: ("Fogbolt book",),          # Raenika
}


def placed(books: bool = True) -> Dict[int, Tuple[str, ...]]:
    """WHERE, with BOOK_WHERE's spellbooks after each object's gear if BOOKS."""
    out = dict(WHERE)
    if books:
        for obj, keys in BOOK_WHERE.items():
            out[obj] = out.get(obj, ()) + keys
    return out


def book_record(key: str, objects: gff.Chunks) -> bytes:
    """Spellbook KEY's item record (23 bytes, in no list and no slot), made from its Book.like's."""
    b = BOOKS[key]
    recs, _ = dataitems.records(objects[("RDFF", b.like)])
    item = bytearray(recs[0].data)
    struct.pack_into("<h", item, 0, -b.object)
    struct.pack_into("<H", item, ITEM_VALUE, b.value)
    struct.pack_into("<H", item, ITEM_SPELL, b.spell + 1)
    struct.pack_into("<H", item, ITEM_POWER, b.spell + 1)
    return bytes(item)


def book_chunks(key: str, objects: gff.Chunks) -> gff.Chunks:
    """Spellbook KEY's object: its OJFF (its Book.like's: the same picture) and RDFF (the like's, its item
    record book_record's)."""
    b = BOOKS[key]
    recs, end = dataitems.records(objects[("RDFF", b.like)])
    recs = [r._replace(data=book_record(key, objects)) if i == 0 else r for i, r in enumerate(recs)]
    return {("OJFF", b.object): objects[("OJFF", b.like)], ("RDFF", b.object): dataitems.chunk(recs, end)}


def drawn() -> List[str]:
    """The keys of the items whose pictures are drawn here, in order (their objects OWN_ICONS on)."""
    return [k for k, g in GEAR.items() if g.picture.make is not None]


def picture_object(key: str) -> int:
    """The sequel object whose picture item KEY shows (a spellbook's its own object)."""
    if key in BOOKS:
        return BOOKS[key].object
    pic = GEAR[key].picture
    if pic.make is not None:
        return OWN_ICONS + drawn().index(key)
    own = ravitems.own_object(pic.sl)
    if own is None:
        raise ValueError(f"no object number for Shattered Lands' {pic.sl}")
    return own


def name_number(name, sequel_text: bytes) -> int:
    """The sequel's name number for NAME (Gear.name)."""
    from . import ravager
    if isinstance(name, int):
        return ravager.mod_name(name)
    numbers = ravitems.sequel_names(sequel_text)
    if name not in numbers:
        raise ValueError(f"the sequel has no item name {name.decode('latin1')!r}")
    return numbers[name]


def item_record(key: str, objects: gff.Chunks, sequel_text: bytes) -> bytes:
    """Item KEY's record (23 bytes, in no list and no slot), made from its Gear.like's (a Book's: book_record)."""
    if key in BOOKS:
        return book_record(key, objects)
    g = GEAR[key]
    recs, _ = dataitems.records(objects[("RDFF", g.like)])
    item = bytearray(recs[0].data)
    struct.pack_into("<h", item, 0, -picture_object(key))
    struct.pack_into("<H", item, ITEM_VALUE, g.value)
    struct.pack_into("<H", item, ravitems.ITEM_TYPE, g.type)
    struct.pack_into("<H", item, ITEM_POWER, 0)
    struct.pack_into("<H", item, ravitems.ITEM_NAME, name_number(g.name, sequel_text))
    item[ITEM_PLUS] = g.plus & 0xFF
    return bytes(item)


def with_pack_items(rdff: bytes, items: Sequence[bytes]) -> bytes:
    """An object's record with ITEMS after the last item of its pack (a person's list of PACK, a
    container's contents), or as a new pack if it has none."""
    recs, end = dataitems.records(rdff)
    recs = list(recs)
    for item in items:
        heads = [i for i, r in enumerate(recs) if r.kind == dataitems.ITEM and r.level == dataitems.FIRST
                 and r.of == 0 and r.flags == PACK]
        if heads:
            last = heads[0]
            while True:
                nxt = next((i for i, r in enumerate(recs) if r.kind == dataitems.ITEM and r.level == dataitems.NEXT
                            and r.of == last), None)
                if nxt is None:
                    break
                last = nxt
            recs.append(dataitems.Record(dataitems.NEXT, last, dataitems.ITEM, 0, NEXT_FLAGS, item))
        else:
            recs.append(dataitems.Record(dataitems.FIRST, 0, dataitems.ITEM, 0, PACK, item))
    return dataitems.chunk(recs, end)


def picture_chunks(key: str, sl_objects: gff.Chunks, sl_palette, stable, item: bytes, type_table: bytes
                   ) -> gff.Chunks:
    """Item KEY's picture object: its OJFF (Shattered Lands' with its picture its own number), its BMP
    and an RDFF of ITEM (its record) and its type's (TYPE_TABLE's), as the party transfer's objects have."""
    from . import ravager
    pic = GEAR[key].picture
    obj = picture_object(key)
    oj = sl_objects.get(("OJFF", pic.sl))
    if oj is None:
        raise ValueError(f"Shattered Lands has no object {pic.sl}")
    icon, = struct.unpack_from("<H", oj, ravitems.OJFF_ICON)
    bmp = sl_objects.get(("BMP ", icon))
    if bmp is None:
        raise ValueError(f"Shattered Lands' object {pic.sl} has no picture")
    if pic.make is not None:
        bmp = icons.encode(pic.make(icons.decode(bmp)))
    record = bytearray(oj)
    struct.pack_into("<H", record, ravitems.OJFF_ICON, obj)
    kind, = struct.unpack_from("<H", item, ravitems.ITEM_TYPE)
    rdff = ravitems.item_records(obj, 0, type_table[kind * ravager.TYPE_SIZE:(kind + 1) * ravager.TYPE_SIZE], kind,
                                 struct.unpack_from("<H", item, ravitems.ITEM_NAME)[0], 0)
    return {("OJFF", obj): bytes(record), ("BMP ", obj): ravitems.picture(bmp, sl_palette, stable),
            ("RDFF", obj): rdff}


def chunks(objects: gff.Chunks, sl_objects: gff.Chunks, sl_palette, stable, sequel_text: bytes,
           where: Optional[Dict[int, Tuple[str, ...]]] = None, books: bool = True) -> gff.Chunks:
    """OBJEX.GFF's chunks to add or replace: the items' pictures, the spellbooks' objects (with BOOKS) and the
    objects of WHERE (default placed(BOOKS)) with their new items. OBJECTS: the sequel's OBJEX.GFF; SL_OBJECTS:
    Shattered Lands' SEGOBJEX.GFF with the Loader's own (icons.new_chunks); SEQUEL_TEXT: RESOURCE.GFF's TEXT 1000."""
    from . import ravager
    where = placed(books) if where is None else where
    out: gff.Chunks = {}
    used = {k for keys in where.values() for k in keys}
    table = ravager.mod_types_table(objects[ravager.TYPES_CHUNK][:ravager.GAME_TYPES * ravager.TYPE_SIZE])
    for key in GEAR:
        if key in used:
            out.update(picture_chunks(key, sl_objects, sl_palette, stable, item_record(key, objects, sequel_text),
                                      table))
    for key in BOOKS:
        if key in used:
            out.update(book_chunks(key, objects))
    for obj, keys in sorted(where.items()):
        rdff = objects.get(("RDFF", obj))
        if rdff is None:
            raise ValueError(f"the sequel has no object {obj}")
        out[("RDFF", obj)] = with_pack_items(rdff, [item_record(k, objects, sequel_text) for k in keys])
    return out


def from_files(objects: gff.Chunks, sl_dir: str, sequel_dir: str, books: bool = True) -> gff.Chunks:
    """chunks() from the Shattered Lands in SL_DIR and the sequel in SEQUEL_DIR (its RESOURCE.GFF and region
    palettes, for the pictures' colours and the names), the spellbooks with BOOKS."""
    import os
    from . import art, ravager

    def read(path):
        with open(path, "rb") as f:
            return gff.read_gff(f.read())
    sl_objects = read(os.path.join(sl_dir, icons.OBJECTS_FILE))
    sl_objects.update(icons.new_chunks(sl_objects))
    gpl = read(os.path.join(sl_dir, "GPLDATA.GFF"))
    sl_palette = next(art.palette_colours(v) for k, v in sorted(gpl.items()) if k[0] == "PAL " and len(v) >= 768)
    resources = read(os.path.join(sequel_dir, ravager.RESOURCE_FILE))
    regions = ravitems.region_palettes(sequel_dir)
    return chunks(objects, sl_objects, sl_palette, ravitems.stable_colours(resources, regions),
                  resources[("TEXT", 1000)], books=books)
