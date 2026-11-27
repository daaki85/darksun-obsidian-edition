"""The Spellarcher's spell arrows made in Wake of the Ravager (spellarrows.py's, on the sequel).

DSCLOG2's SPELL ARROWS (site 240 and PICK POCKETS' 180-185) gives a Spellarcher on the USE screen, outside a
fight, a button for each touch spell it knows, as Shattered Lands does: CHILL ARROWS, SHOCKING ARROWS,
VAMPIRIC ARROWS, the first where Turn Undead is, the rest in the row's spare places to its right. Let go
of, the helper asks the Loader (its header's ARROWS_SEQ, +2100: the member, the spell's place in
spellarrows.ARROWS), and `make` here does what SpellArrows.make does in Shattered Lands: a slot of the
spell's level used for one arrow, on that spell's stack wherever it is (STACK_MOST at most), or a new
stack (in the quiver if it is empty, else in the pack); refused (not known, in armour, no slot, a full
stack), its words are shown.

The arrows are the Loader's objects (OBJECTS: Shattered Lands' spell arrows' pictures, objects 2614-2620,
numbered as the party transfer numbers them, ravitems.own_object: so transferred and made arrows are one
kind and stack), in every copy of OBJEX.GFF the Loader writes, a party transferred or not (`chunks`).
An arrow item is the sequel's plain Arrows (object 701's record: type 6) with the arrows' own picture, the
mod's name (ravager.mod_name of spellarrows.NAMES': DSCLOG2's ARROW_PLUS knows them by it), the spell
(its +10h, the sequel's spell + 1: DSCLOG2's WEAPON_CAST casts it at the archer's preserver level, Daaki's
rule) and no worth.

The buttons' icons (ICON 3050-3052 in the Loader's RESOURC2.GFF, PP_ICON - 1 + the kind) are Shattered
Lands' (icons.arrow_spell_icon, from the player's own RESOURCE.GFF) brought into the sequel's palette as
the new spells' are (ravspells.in_sequel); without Shattered Lands' files, the sequel's own touch spells'
icons (`resource_chunks`)."""

import struct
from typing import Dict, List, NamedTuple, Optional, Tuple

from . import game, gff, pickpocket, spellarrows, weaponchoice
from .game import GameData


class SequelArrow(NamedTuple):
    row: int        # its place in spellarrows.ARROWS (DSCLOG2's ARROWS_ROW)
    spell: int      # the sequel's spell (its record's number: DSCLOG2's WC_ARROWS)


ARROWS = (SequelArrow(1, 3), SequelArrow(2, 10), SequelArrow(3, 38))  # Chill Touch, Shocking Grasp, Vampiric Touch
BY_ROW = {a.row: a for a in ARROWS}
KNOWN_SEG, KNOWN_OFF, KNOWN_SIZE = 0x3D62, 0x39C, 15  # (selector 320h: the load + 3D62h, a bitset a member)
DGROUP = 0x47E0  # (the game's DS less its load segment: ravager.DGROUP)
PLAIN_ARROWS = bytes.fromhex("43fd18000f2714000f27060000000000000004ff1e0000")  # (the sequel's Arrows, object 701)
ITEM_POWER = 0x10  # (the sequel's: a word, the spell + 1)
ICON_FIRST = 3049  # (PP_ICON - 1 + PP_ARROWS + the row: 3050-3052; DSCLOG2's PP_PUT)
SEQUEL_SPELL_ICON = 21000  # (the sequel's spell icons: ICON 21000 + its spell)
SKIP = "spell_arrows"  # (objects_fixed's and resources_fixed's name for them, a SKIP's to leave them out)


def sl_object(row: int) -> int:
    """The Shattered Lands object of ARROWS[ROW]'s picture (spellarrows.PICTURES: the Loader's own there)."""
    return 0x10000 - spellarrows.PICTURES[spellarrows.ARROWS[row].name]


def own_object(row: int) -> int:
    """The Loader's sequel object for that spell's arrows (the party transfer's number for it)."""
    from . import ravitems
    return ravitems.own_object(sl_object(row))


def name_number(row: int) -> int:
    from . import ravager
    return ravager.mod_name(spellarrows.ARROWS[row].name)


def arrows_item(row: int, count: int) -> bytes:
    """A stack of COUNT arrows of ARROWS' row ROW: the sequel's Arrows, their own picture, name and spell,
    worth nothing."""
    arrow = BY_ROW[row]
    rec = bytearray(PLAIN_ARROWS)
    struct.pack_into("<hH", rec, weaponchoice.ITEM_PICTURE, -own_object(row), count)
    struct.pack_into("<H", rec, weaponchoice.ITEM_VALUE, 0)
    struct.pack_into("<H", rec, ITEM_POWER, arrow.spell + 1)
    struct.pack_into("<H", rec, 0x14, name_number(row))
    return bytes(rec)


def is_arrows_of(rec: bytes, row: int) -> bool:
    return len(rec) >= 0x16 and struct.unpack_from("<H", rec, 0x14)[0] == name_number(row)


def known_at(gd: GameData, member: int) -> int:
    """Where party member MEMBER's known wizard spells are (a bit a spell, spell n bit n)."""
    return (gd.ds - DGROUP + KNOWN_SEG) * 16 + KNOWN_OFF + member * KNOWN_SIZE


def knows(gd: GameData, member: int, spell: int) -> bool:
    return bool(gd.guest.read(known_at(gd, member) + spell // 8, 1)[0] & (1 << (spell % 8)))


def make(gd: GameData, member: int, row: int) -> pickpocket.Attempt:
    """Party member MEMBER's button for spellarrows.ARROWS[ROW], in the sequel: a slot used for an arrow,
    on the spell's stack or a new one (no text), or why not (spellarrows.SpellArrows.make's words)."""
    if row not in BY_ROW or not 0 <= member < game.PARTY_SIZE:
        return pickpocket.Attempt("No spell arrows can be made now.", [])
    arrow, sl = BY_ROW[row], spellarrows.ARROWS[row]
    who = gd.creature_name(member)
    if not spellarrows.is_spellarcher(gd, member) or not knows(gd, member, arrow.spell):
        return pickpocket.Attempt(f"{who} can't weave {sl.spell_name} into arrows.", [])
    try:
        armoured = gd.no_spells(member)
    except (AttributeError, KeyError, IndexError, struct.error):
        armoured = False
    if armoured:
        return pickpocket.Attempt(f"{who} can't weave spell arrows in armour.", [])
    name = spellarrows.NAMES[sl.name].decode().lower()
    most = spellarrows.STACK_MOST
    stack = next(((index, item) for index, item, _ in gd._worn(member) if is_arrows_of(item, row)), None)
    had = struct.unpack_from("<H", stack[1], weaponchoice.ITEM_COUNT)[0] if stack is not None else 0
    if had + spellarrows.ARROWS_A_SLOT > most:
        return pickpocket.Attempt(f"{who}'s {name} are a full stack ({most}).", [])
    if spellarrows.slots_left(gd, member, sl.level) <= 0:
        return pickpocket.Attempt(f"{who} has no {spellarrows._nth(sl.level)}-level spell left for "
                                  f"{sl.spell_name}'s arrows.", [])
    from . import npcitems
    where = ""
    if stack is not None:
        gd.guest.write(spellarrows.item_address(gd, stack[0]) + weaponchoice.ITEM_COUNT,
                       struct.pack("<H", had + spellarrows.ARROWS_A_SLOT))
    else:
        empty = not any(item[game.ITEM_SLOT] == weaponchoice.AMMO_SLOT for _, item, _ in gd._worn(member))
        if not npcitems.add_to(gd, member, arrows_item(row, spellarrows.ARROWS_A_SLOT),
                               weaponchoice.AMMO_SLOT if empty else None):
            return pickpocket.Attempt("No spell arrows can be made now.", [])
        if empty:
            weaponchoice.bow_ahead(gd, member)
        where = " in the quiver" if empty else " in the pack"
    at = gd.ds * 16 + game.SLOTS_LEFT["Wizard"] + member * game.SLOTS_STRIDE + sl.level
    gd.guest.write(at, bytes((spellarrows.slots_left(gd, member, sl.level) - 1,)))
    total = had + spellarrows.ARROWS_A_SLOT
    log = f"{who} makes one of the {name}{where} ({total} of {most} now): a {spellarrows._nth(sl.level)}-level " \
          f"slot used; it casts {sl.spell_name} on what it hits, at {who}'s preserver level, and lasts until shot"
    return pickpocket.Attempt("", [log])


STARTING = spellarrows.STARTING  # (a new Spellarcher's: a stack of each touch spell's it picked)

_objects_seen: Dict[Tuple[str, float], bool] = {}  # (objects_ready's answers, by the copy's path and time)


def objects_ready(dos_dir: Optional[str] = None) -> bool:
    """Whether the Loader's copy of OBJEX.GFF (ravager.OBJECTS_COPY, in DOS_DIR: launch.DOS_DIR) has every one of
    ARROWS' objects (chunks): without them a spell arrow would be an item of no object. Read once a copy."""
    import os
    from . import launch, ravager
    path = os.path.join(dos_dir or launch.DOS_DIR, ravager.OBJECTS_COPY)
    try:
        key = (path, os.path.getmtime(path))
    except OSError:
        return False
    if key not in _objects_seen:
        try:
            with open(path, "rb") as f:
                chunks = gff.read_gff(f.read())
            _objects_seen[key] = all(("OJFF", own_object(a.row)) in chunks for a in ARROWS)
        except (OSError, gff.GffError, struct.error):
            _objects_seen[key] = False
    return _objects_seen[key]


def _picks(gd: GameData, member: int) -> List[SequelArrow]:
    """The touch spells MEMBER picked as it was made (knows), in ARROWS' order."""
    return [a for a in ARROWS if knows(gd, member, a.spell)]


def _has_spell_arrows(gd: GameData, member: int) -> bool:
    return any(is_arrows_of(item, a.row) for _, item, _ in gd._worn(member) for a in ARROWS)


def arrows_due(gd: GameData, member: int) -> bool:
    """Whether MEMBER's starting spell arrows are still to come: it picked a touch spell, has no spell arrows, and
    the arrows' objects are there (objects_ready). Its Fine Bow waits on them (ravkitstart.fine_bow)."""
    return bool(_picks(gd, member)) and not _has_spell_arrows(gd, member) and objects_ready()


def starting_arrows(gd: GameData, member: int) -> List[str]:
    """A new Spellarcher's arrows (spellarrows.starting_gear's rule on the sequel's gear), made once with its Fine
    Bow (ravkitstart.fine_bow): for each touch spell it picked as it was made (knows), STARTING of that spell's
    arrows, the first in the quiver; the plain arrows the sequel gave with the bow (ravfirstweapon's +1 arrows)
    go once a stack of them is in (no room for any: they stay). Knowing none, or the arrows' objects not in the
    Loader's OBJEX copy (objects_ready: RAV_SKIP's spell_arrows), it keeps those (the sequel's own +1 arrows,
    not Shattered Lands' 24 plain ones). Lines for the log."""
    from . import npcitems, ring
    picks = _picks(gd, member)
    if not picks or _has_spell_arrows(gd, member) or not objects_ready():
        return []
    who, out = gd.creature_name(member), []
    plain_type = struct.unpack_from("<H", PLAIN_ARROWS, 0x0A)[0]
    plain = [(index, item) for index, item, _ in gd._worn(member)
             if struct.unpack_from("<H", item, game.ITEM_TYPE)[0] == plain_type]
    # the spell arrows first (the quiver if it is free, else the pack), the plain arrows taken only once one
    # stack is in: a full pack keeps them (the review of #229: taken first, a full pack left the archer none)
    added = []
    for arrow in picks:
        quiver = not any(item[game.ITEM_SLOT] == weaponchoice.AMMO_SLOT for _, item, _ in gd._worn(member))
        if npcitems.add_to(gd, member, arrows_item(arrow.row, STARTING), weaponchoice.AMMO_SLOT if quiver else None):
            added.append((arrow, quiver))
    if not added:
        return []
    for index, _ in plain:
        ring.unlink(gd, ring.Items(gd), index, "a Spellarcher's starting arrows", empty=True)
    first, quiver = added[0]
    if not quiver and not any(item[game.ITEM_SLOT] == weaponchoice.AMMO_SLOT for _, item, _ in gd._worn(member)):
        # (the plain arrows held the quiver: the first stack moved there from the pack, or left there)
        stack = next((index for index, item, _ in gd._worn(member) if is_arrows_of(item, first.row)), None)
        rec = arrows_item(first.row, STARTING)
        if stack is not None and ring.unlink(gd, ring.Items(gd), stack, "a Spellarcher's arrows to the quiver",
                                             empty=True):
            quiver = npcitems.add_to(gd, member, rec, weaponchoice.AMMO_SLOT)
            if not quiver:
                npcitems.add_to(gd, member, rec)
            added[0] = (first, quiver)
    for arrow, quiver in added:
        sl = spellarrows.ARROWS[arrow.row]
        out.append(f"{who} starts with {STARTING} {spellarrows.NAMES[sl.name].decode().lower()}"
                   f"{' in the quiver' if quiver else ' in the pack'}: {sl.spell_name} picked")
    weaponchoice.bow_ahead(gd, member)
    return out


def arrow_names() -> Dict[int, bytes]:
    """The sequel's spell arrows' name numbers -> their names (spellarrows.NAMES')."""
    return {name_number(a.row): spellarrows.NAMES[spellarrows.ARROWS[a.row].name] for a in ARROWS}


def map_screen_off(gd: GameData) -> bool:
    """Whether the sequel's map isn't the screen up (quicksave.SCREEN_IS, DS:0DABh in ravlog's layout: 1 the
    map): the inventory, which writes its copy of the items back as it shuts, among the rest."""
    from . import quicksave
    return gd._word(quicksave.SCREEN_IS) != quicksave.ON_MAP


def return_strays(gd: GameData) -> List[str]:
    """spellarrows.return_strays on the sequel (its names, the map up): spell arrows a party member who isn't a
    Spellarcher carries back to the Spellarcher, or out of its quiver: a backstop to DSCLOG2's ARROWS_FORBID, which
    keeps the others from readying them, for arrows readied before it (an old save) or moved past it. Lines for
    the log."""
    return spellarrows.return_strays(gd, arrow_names(), map_screen_off)


def slots_range(gd: GameData, member: int) -> Tuple[int, int]:
    """The wizard slots left of MEMBER (each level's byte), as a writable range."""
    return gd.ds * 16 + game.SLOTS_LEFT["Wizard"] + member * game.SLOTS_STRIDE, game.SPELL_LEVELS + 1


def chunks(sequel_objects: gff.Chunks, sl_objects: gff.Chunks, sl_palette, stable, type_table: bytes) -> gff.Chunks:
    """OBJEX.GFF's chunks for the arrows' objects (OJFF, its picture, RDFF): SL_OBJECTS Shattered Lands'
    SEGOBJEX.GFF with the Loader's own (icons.new_chunks); its pictures each colour the nearest of the
    sequel's STABLE ones (ravitems.picture)."""
    from . import ravager, ravitems
    out: gff.Chunks = {}
    kind = struct.unpack_from("<H", PLAIN_ARROWS, ravitems.ITEM_TYPE)[0]
    record_type = type_table[kind * ravager.TYPE_SIZE:(kind + 1) * ravager.TYPE_SIZE]
    for arrow in ARROWS:
        sl, obj = sl_object(arrow.row), own_object(arrow.row)
        oj = sl_objects.get(("OJFF", sl))
        if oj is None:
            raise ValueError(f"Shattered Lands has no object {sl}")
        icon, = struct.unpack_from("<H", oj, ravitems.OJFF_ICON)
        bmp = sl_objects[("BMP ", icon)]
        record = bytearray(oj)
        struct.pack_into("<H", record, ravitems.OJFF_ICON, obj)
        out[("OJFF", obj)] = bytes(record)
        out[("BMP ", obj)] = ravitems.picture(bmp, sl_palette, stable)
        out[("RDFF", obj)] = ravitems.item_records(obj, 0, record_type, kind, name_number(arrow.row), arrow.spell + 1)
    return out


def from_files(sequel_objects: gff.Chunks, sl_dir: str, sequel_dir: str) -> gff.Chunks:
    """chunks() from the Shattered Lands in SL_DIR and the sequel in SEQUEL_DIR (its palettes, as ravgear's)."""
    import glob
    import os
    from . import art, icons, ravager, ravitems

    def read(path):
        with open(path, "rb") as f:
            return gff.read_gff(f.read())
    sl_objects = read(os.path.join(sl_dir, icons.OBJECTS_FILE))
    sl_objects.update(icons.new_chunks(sl_objects))
    gpl = read(os.path.join(sl_dir, "GPLDATA.GFF"))
    sl_palette = next(art.palette_colours(v) for k, v in sorted(gpl.items()) if k[0] == "PAL " and len(v) >= 768)
    resources = read(os.path.join(sequel_dir, ravager.RESOURCE_FILE))
    regions = [v for f in sorted(glob.glob(os.path.join(sequel_dir, "RGN*.GFF")))
               for k, v in read(f).items() if k[0] == "PAL "]
    return chunks(sequel_objects, sl_objects, sl_palette, ravitems.stable_colours(resources, regions),
                  sequel_objects[ravager.TYPES_CHUNK])


def resource_chunks(resource: gff.Chunks, sl_dir: Optional[str]) -> Dict[Tuple[str, int], bytes]:
    """The arrows buttons' icons (ICON ICON_FIRST + the row) for the copy of the sequel's RESOURCE.GFF: Shattered
    Lands' (icons.ARROW_BUTTONS, from SL_DIR's RESOURCE.GFF) in the sequel's palette, else its touch spells' own."""
    from . import art, icons, ravspells
    out = {("ICON", ICON_FIRST + a.row): resource[("ICON", SEQUEL_SPELL_ICON + a.spell)] for a in ARROWS
           if ("ICON", SEQUEL_SPELL_ICON + a.spell) in resource}
    sl_resources = sl_dir and art._find(sl_dir, "RESOURCE.GFF")
    if not sl_resources:
        return out
    try:
        with open(sl_resources, "rb") as f:
            sl = gff.read_gff(f.read())
        sl_palette = ravspells._sl_palette(sl_dir)
        palette = art.palette_colours(resource[("PAL ", 1000)])
        colours = ravspells._icon_colours(resource)
        if not colours:
            return out
        for a in ARROWS:
            touch, *how = icons.ARROW_BUTTONS[ICON_FIRST + a.row]
            rows = icons.arrow_spell_icon(icons.decode(sl[("ICON", 21000 + touch)]), *how)
            out[("ICON", ICON_FIRST + a.row)] = art.plnr_frames([ravspells.in_sequel(rows, sl_palette, palette, colours)])
    except (OSError, TypeError, KeyError, ValueError, IndexError, StopIteration, struct.error, gff.GffError):
        pass  # (Shattered Lands' files unreadable: the sequel's touch spells' icons)
    return out


def lines_for(result: Optional[pickpocket.Attempt]) -> List[str]:
    return (result.log or [result.text]) if result else []
