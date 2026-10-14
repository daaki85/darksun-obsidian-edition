"""The Loader's new items written into the game's own data: each in the object it belongs to (a
person's, a chest's) in the Loader's copy of SEGOBJEX.GFF, so that the game makes it with them.

An object's record (an RDFF chunk) is a list of records, each a header and its data:

- the object itself (level 1: a person, type 2; or an item, type 1, a chest);
- its items: the first a child of the object (level 2, its "of" the object's index, 0), each
  next one after the one before (level 4, its "of" that one's index), each an item record (type
  1, its 21 bytes as an item's in memory, its next item and contents left 0);
- after each item, its attributes (level 3, "of" the item's index): its item type (type 5, the
  number in the header's word) and its name (type 3);
- an end (level FFh).

The header's other word (the item's: the game's own items reuse a few hundred numbers, the same
for the same kind of item) is copied from an item of the same type, which the game does no more
with than carry along.

People of a kind share one object (six Castle Guards, four Undermountain miners), and so can things
(the slave pens' weapon rack and the Lower Castle's): an item for one of them alone needs an object
of their own, a copy of the kind's under a new number (its record naming itself), and the region's
entity for that person (its ETAB entry) pointing to it, in the Loader's copy of the region's file.
"""

import struct
from typing import Dict, List, NamedTuple, Optional, Sequence, Tuple

from . import game

HEADER = struct.Struct("<BBHHHH")  # level, of, type, number, flags, length
FIRST, ATTRIBUTE, NEXT, END = 2, 3, 4, 0xFF
ITEM, NAME, TYPE = 1, 3, 5
FIRST_FLAGS, NEXT_FLAGS, TYPE_FLAGS, NAME_FLAGS = 79, 1, 4, 2  # (as the game's own records have them)
SELF = 6  # an object's record's own number (negated), in its first record's data
ENTITY = struct.Struct("<HHBBh")  # an ETAB entry: x, y, height, flags, object (negated)
ITEM_LINKS = ((game.ITEM_NEXT, 2), (0x08, 2))  # an item's next and contents: 0 in the data


class Record(NamedTuple):
    level: int
    of: int
    kind: int
    number: int
    flags: int
    data: bytes


def records(chunk: bytes) -> Tuple[List[Record], bytes]:
    """The records of an RDFF chunk, and its end (the end record's bytes, kept as they are)."""
    out, at = [], 0
    while at + HEADER.size <= len(chunk):
        level, of, kind, number, flags, length = HEADER.unpack_from(chunk, at)
        if level == END:
            return out, chunk[at:]
        out.append(Record(level, of, kind, number, flags, chunk[at + HEADER.size:at + HEADER.size + length]))
        at += HEADER.size + length
    raise ValueError("an object's record without its end")


def chunk(recs: Sequence[Record], end: bytes) -> bytes:
    return b"".join(HEADER.pack(r.level, r.of, r.kind, r.number, r.flags, len(r.data)) + r.data
                    for r in recs) + end


def top_items(recs: Sequence[Record]) -> List[int]:
    """The indexes of the object's own items (not those inside them), in order."""
    out = []
    first = next((i for i, r in enumerate(recs) if r.level == FIRST and r.of == 0 and r.kind == ITEM), None)
    while first is not None:
        out.append(first)
        first = next((i for i, r in enumerate(recs) if r.level == NEXT and r.of == first and r.kind == ITEM), None)
    return out


def placed(item: bytes) -> bytes:
    """An item record as an object's data has it: its next item and contents 0, in no slot."""
    data = bytearray(item)
    for at, size in ITEM_LINKS:
        data[at:at + size] = bytes(size)
    data[game.ITEM_SLOT] = 0xFF
    return bytes(data)


def with_items(rdff: bytes, items: Sequence[bytes], numbers: Optional[Dict[int, int]] = None) -> bytes:
    """The object's record (RDFF) with ITEMS (item records) after its own items. NUMBERS: the
    header number for an item type (else the last item's)."""
    recs, end = records(rdff)
    recs = list(recs)
    numbers = numbers or {}
    for item in items:
        mine = top_items(recs)
        data = placed(item)
        kind, = struct.unpack_from("<H", data, game.ITEM_TYPE)
        name, = struct.unpack_from("<H", data, game.ITEM_NAME)
        number = numbers.get(kind, recs[mine[-1]].number if mine else 0)
        if mine:
            recs.append(Record(NEXT, mine[-1], ITEM, number, NEXT_FLAGS, bytes(data)))
        else:
            recs.append(Record(FIRST, 0, ITEM, number, FIRST_FLAGS, bytes(data)))
        at = len(recs) - 1
        recs.append(Record(ATTRIBUTE, at, TYPE, kind, TYPE_FLAGS, b""))
        recs.append(Record(ATTRIBUTE, at, NAME, name, NAME_FLAGS, b""))
    return chunk(recs, end)


def with_item_changed(rdff: bytes, test, change) -> bytes:
    """The object's record with each of its own items for which TEST(record) holds made
    CHANGE(record) (its name attribute following the record's name)."""
    recs, end = records(rdff)
    recs = list(recs)
    for i in top_items(recs):
        if not test(recs[i].data):
            continue
        data = change(recs[i].data)
        recs[i] = recs[i]._replace(data=data)
        name, = struct.unpack_from("<H", data, game.ITEM_NAME)
        for j, r in enumerate(recs):
            if r.level == ATTRIBUTE and r.of == i and r.kind == NAME:
                recs[j] = r._replace(number=name)
    return chunk(recs, end)


def with_item_replaced(rdff: bytes, test, item: bytes, numbers: Optional[Dict[int, int]] = None) -> bytes:
    """The object's record with the first of its own items for which TEST(record) holds made
    ITEM (its type and name attributes, and its header number, following it); unchanged if none."""
    recs, end = records(rdff)
    recs = list(recs)
    at = next((i for i in top_items(recs) if test(recs[i].data)), None)
    if at is None:
        return rdff
    data = placed(item)
    kind, = struct.unpack_from("<H", data, game.ITEM_TYPE)
    name, = struct.unpack_from("<H", data, game.ITEM_NAME)
    recs[at] = recs[at]._replace(number=(numbers or {}).get(kind, recs[at].number), data=data)
    for j, r in enumerate(recs):
        if r.level == ATTRIBUTE and r.of == at and r.kind in (TYPE, NAME):
            recs[j] = r._replace(number=kind if r.kind == TYPE else name)
    return chunk(recs, end)


def items_of(rdff: bytes) -> List[bytes]:
    """The item records of the object's own items."""
    recs, _ = records(rdff)
    return [recs[i].data for i in top_items(recs)]


def item_object(item: bytes, number: int) -> bytes:
    """An object of its own for an item (a game's script makes one from it: the Elven Leader's
    gift), its record ITEM, its header number NUMBER."""
    data = bytearray(item)
    for at, size in ITEM_LINKS:
        data[at:at + size] = bytes(size)
    data[game.ITEM_SLOT] = 0xFF
    kind, = struct.unpack_from("<H", data, game.ITEM_TYPE)
    name, = struct.unpack_from("<H", data, game.ITEM_NAME)
    recs = [Record(1, 0, ITEM, number, 71, bytes(data)), Record(ATTRIBUTE, 0, TYPE, kind, TYPE_FLAGS, b""),
            Record(ATTRIBUTE, 0, NAME, name, NAME_FLAGS, b"")]
    return chunk(recs, bytes((END,)) + bytes(9))


def renumbered(rdff: bytes, obj: int) -> bytes:
    """A copy of an object's record naming itself object OBJ (a person's at SELF, an item's, a
    chest's or a rack's, first)."""
    out = bytearray(rdff)
    kind = HEADER.unpack_from(rdff)[2]
    struct.pack_into("<h", out, HEADER.size + (0 if kind == ITEM else SELF), -obj)
    return bytes(out)


def numbers(chunks) -> Dict[int, int]:
    """{item type: the header number the game's items of that type have (the first seen)}."""
    out: Dict[int, int] = {}
    for (kind, _), data in sorted(chunks.items()):
        if kind != "RDFF":
            continue
        try:
            recs, _ = records(data)
        except ValueError:
            continue
        for r in recs:
            if r.kind == ITEM and len(r.data) == game.ITEM_SIZE:
                out.setdefault(struct.unpack_from("<H", r.data, game.ITEM_TYPE)[0], r.number)
    return out


def with_entity_object(etab: bytes, index: int, obj: int, was: int) -> bytes:
    """A region's entity table with entry INDEX (an entity of object WAS) made object OBJ's;
    unchanged if that entry isn't WAS's."""
    at = index * ENTITY.size
    if at + ENTITY.size > len(etab) or ENTITY.unpack_from(etab, at)[4] != -was:
        return etab
    out = bytearray(etab)
    struct.pack_into("<h", out, at + 8 - 2, -obj)
    return bytes(out)
