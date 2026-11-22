"""The party transfer's items the sequel lacks: every one comes across (Daaki's ask, 2026-11-22).

SSI's transfer (ravtransfer.py, CHARTRAN's work) gives an item the sequel's object that ITEMS.BIN pairs
with its Shattered Lands object, and a money bag where there is none: the mod's items, and some of
Shattered Lands' own (its quest items, two of its bags). Here each of those becomes an object of the
Loader's instead, made from the player's own files (nothing from either game is in the repository):

- its number: OWN_FIRST + the SL object below 10000, OWN_HIGH + (the SL object - 30000) for SL's
  30000 on (the sequel's objects stop at 13000 and start again at 30000; 14000-29999 are free);
- its OJFF record: Shattered Lands' (the two games' are alike), its picture the object's own number;
- its picture (BMP): Shattered Lands' as it is (the sequel draws that format too), each colour the
  nearest of the sequel's stable ones (RESOURCE.GFF's PAL 1000 entries no region palette changes;
  playtest/logs/2026-11-22-ravager-item-names.md);
- its RDFF records: the item (as the sequel's objects have it, 17h bytes) and its type (15 bytes);
- its type: the mod's (SL 115 on: ravager.mod_type, the types the Loader adds); else the sequel type
  most of SL's objects of that type are paired with (ITEMS.BIN: SL's bags with the sequel's bag);
  else KEEPSAKE_TYPE, a plain carried thing (SL's quest items: keepsakes, which the sequel's story
  doesn't know; a scroll of a spell the sequel lacks too);
- its name: the mod's own (ravager.mod_name); else the sequel's name of the same letters; else one
  of KEEPSAKE names, after the mod's in DSCLOG2's ITEM_NAMES.

The objects are kept in the mod's dos folder (ADDED_FILE, each transfer's added to the last's), and
the Loader's copy of OBJEX.GFF takes them in (ravager.objects_fixed).
"""

import collections
import struct
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from . import dataitems, gff

OWN_FIRST, OWN_HIGH, SL_HIGH = 20000, 14000, 30000
KEEPSAKE_TYPE = 9  # (the sequel's type of its money bag, its fruit and its plain things)
ADDED_FILE = "RAVITEMS.GFF"  # (in the mod's dos folder)
NAMES_CHUNK = ("TEXT", 1)  # (in ADDED_FILE: the keepsakes' names, a line each)
OBJECT_KINDS = ("OJFF", "RDFF", "BMP ")
OJFF_ICON = 0x0C
SL_ITEM_TYPE, SL_ITEM_NAME = 0x0A, 0x12
ITEM_TYPE, ITEM_NAME = 0x0A, 0x14
ITEM_RECORD = bytes.fromhex("0000" "0000" "0f27" "0100" "0f27" "0000" "0000" "0000" "0000" "04ff" "0000" "00")
ITEM_NUMBER_FIRST = 2000  # (the RDFF item records' numbers: the sequel's go to 1316)


def own_object(sl_object: int) -> Optional[int]:
    """The Loader's sequel object for Shattered Lands' SL_OBJECT (None for one it can't number)."""
    if 0 < sl_object < 10000:
        return OWN_FIRST + sl_object
    if SL_HIGH <= sl_object < SL_HIGH + (OWN_FIRST - OWN_HIGH):
        return OWN_HIGH + sl_object - SL_HIGH
    return None


def _first_record(chunks: gff.Chunks, obj: int) -> Optional[bytes]:
    try:
        recs, _ = dataitems.records(chunks[("RDFF", obj)])
    except (KeyError, gff.GffError, struct.error):
        return None
    return recs[0].data if recs and len(recs[0].data) >= SL_ITEM_TYPE + 2 else None


def type_map(pairs: Dict[int, int], sl_objects: gff.Chunks, sequel_objects: gff.Chunks) -> Dict[int, int]:
    """Each SL item type, the sequel type most of its paired objects have (ITEMS.BIN's PAIRS)."""
    seen: Dict[int, collections.Counter] = collections.defaultdict(collections.Counter)
    for sl, wotr in pairs.items():
        a, b = _first_record(sl_objects, sl), _first_record(sequel_objects, wotr)
        if a is not None and b is not None:
            seen[struct.unpack_from("<H", a, SL_ITEM_TYPE)[0]][struct.unpack_from("<H", b, ITEM_TYPE)[0]] += 1
    return {t: c.most_common(1)[0][0] for t, c in seen.items()}


def sequel_type(sl_type: int, types: Dict[int, int]) -> int:
    from . import game, ravager, ravtransfer
    if sl_type in (ravtransfer.SL_WIZARD_SCROLL, ravtransfer.SL_PRIEST_SCROLL):
        return KEEPSAKE_TYPE  # (the scrolls made here are of spells the sequel lacks: ravtransfer.item)
    if game.GAME_TYPES <= sl_type < game.GAME_TYPES + ravager.MOD_TYPES:
        return ravager.mod_type(sl_type)
    return types.get(sl_type, KEEPSAKE_TYPE)


def sequel_names(text: bytes) -> Dict[bytes, int]:
    """The sequel's item names (RESOURCE.GFF's TEXT 1000, a line a name: line k is name k + 1), by
    their letters in capitals."""
    out: Dict[bytes, int] = {}
    for i, line in enumerate(text.split(b"\n")):
        line = line.rstrip(b"\r")
        if line:
            out.setdefault(line.upper(), i + 1)
    return out


class Names:
    """Names for the added items: the mod's, the sequel's own, or keepsakes' (KEPT, added in turn)."""

    def __init__(self, sl_names: bytes, sequel_text: bytes, kept: Sequence[bytes] = ()):
        self.sl_names, self.sequel = sl_names, sequel_names(sequel_text)
        self.kept: List[bytes] = list(kept)

    def sl_name(self, entry: int) -> bytes:
        from . import game, names
        if entry >= names.OWN:
            return names.NAMES.get(entry, b"")
        return self.sl_names[entry * game.ITEM_NAME_SIZE:(entry + 1) * game.ITEM_NAME_SIZE].split(b"\0")[0]

    def number(self, entry: int) -> int:
        from . import names, ravager
        if entry in names.NAMES:
            return ravager.mod_name(entry)
        text = self.sl_name(entry)
        if text.upper() in self.sequel:
            return self.sequel[text.upper()]
        if text not in self.kept:
            self.kept.append(text)
        return ravager.KEEPSAKE_NAMES_FIRST + self.kept.index(text)


def stable_colours(resources: gff.Chunks, region_palettes: Iterable[bytes]) -> List[Tuple[int, Tuple[int, int, int]]]:
    """The sequel's palette numbers no region changes (PAL 1000's, as every region palette has them)."""
    from . import art
    base = resources[("PAL ", 1000)]
    palettes = [p for p in region_palettes if len(p) >= 768]
    colours = art.palette_colours(base)
    return [(c, colours[c]) for c in range(1, 256) if all(p[c * 3:c * 3 + 3] == base[c * 3:c * 3 + 3] for p in palettes)]


def picture(sl_picture: bytes, sl_palette, stable) -> bytes:
    """A Shattered Lands picture, each colour the nearest of the sequel's STABLE ones (0 kept)."""
    from . import icons
    cache: Dict[int, int] = {}

    def nearest(p):
        if not p:
            return p
        if p not in cache:
            rgb = sl_palette[p]
            cache[p] = min(stable, key=lambda e: sum((a - b) ** 2 for a, b in zip(e[1], rgb)))[0]
        return cache[p]
    return icons.encode([[nearest(p) for p in row] for row in icons.decode(sl_picture)])


def item_records(obj: int, number: int, type_record: bytes, wotr_type: int, name: int, power: int) -> bytes:
    """An added object's RDFF chunk: its item record and its type's, as the sequel's objects have them."""
    item = bytearray(ITEM_RECORD)
    struct.pack_into("<h", item, 0, -obj)
    struct.pack_into("<H", item, ITEM_TYPE, wotr_type)
    struct.pack_into("<H", item, 0x10, power)
    struct.pack_into("<H", item, ITEM_NAME, name)
    recs = [dataitems.Record(1, 0, 1, number, 0, bytes(item)),
            dataitems.Record(3, 0, 4, wotr_type, 5, type_record)]
    return dataitems.chunk(recs, dataitems.HEADER.pack(dataitems.END, 0, 0, 0, 0, 0))


def make(sl_items: Dict[int, bytes], sl_objects: gff.Chunks, sequel_objects: gff.Chunks, types: Dict[int, int],
         names: Names, sl_palette, stable, type_table: bytes, number: int = ITEM_NUMBER_FIRST
         ) -> Tuple[Dict[int, int], gff.Chunks, List[Tuple[int, str]]]:
    """For each SL object in SL_ITEMS (a save's item record of it), the Loader's object: the pairs
    (SL object -> its own), their chunks, and those that couldn't be made, with why."""
    from . import ravager
    pairs: Dict[int, int] = {}
    chunks: gff.Chunks = {}
    failed: List[Tuple[int, str]] = []
    for sl, rec in sorted(sl_items.items()):
        own = own_object(sl)
        oj = sl_objects.get(("OJFF", sl))
        if own is None or oj is None:
            failed.append((sl, "no number for it" if own is None else "no object of it in Shattered Lands"))
            continue
        icon, = struct.unpack_from("<H", oj, OJFF_ICON)
        pic = sl_objects.get(("BMP ", icon))
        if pic is None:
            failed.append((sl, "no picture"))
            continue
        wotr_type = sequel_type(struct.unpack_from("<H", rec, SL_ITEM_TYPE)[0], types)
        t = type_table[wotr_type * ravager.TYPE_SIZE:(wotr_type + 1) * ravager.TYPE_SIZE]
        if len(t) != ravager.TYPE_SIZE:
            failed.append((sl, f"no type {wotr_type}"))
            continue
        name = names.number(struct.unpack_from("<H", rec, SL_ITEM_NAME)[0])
        record = bytearray(oj)
        struct.pack_into("<H", record, OJFF_ICON, own)
        chunks[("OJFF", own)] = bytes(record)
        chunks[("BMP ", own)] = picture(pic, sl_palette, stable)
        chunks[("RDFF", own)] = item_records(own, number, t, wotr_type, name, 0)
        pairs[sl] = own
        number += 1
    return pairs, chunks, failed
