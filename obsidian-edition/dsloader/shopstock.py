"""The sellers' new items in a Wake of the Ravager game saved before the Loader had them (ravgear.py).

ravgear puts the new items into OBJEX.GFF's copy, from which the game makes its people when a new game
starts: a saved game keeps the people it has already made, so its sellers (Notaku, the weaponer, the stalls)
would never stock them. Here the Loader's dice log tops them up in memory, once a seller is loaded (its
region's, or a Limbo seller copied in for a talk) and the game's item lists are still (as fuller starting
gear does: npcitems.add_to, from the game's free list of item records, into a backpack cell of its own):

- a seller: a person (a thing of kind 2) whose creature's object (its record's +6, negated, as OBJEX.GFF
  has it) is one of SELLERS;
- its new items: the records of ravgear's items that OBJEX.GFF's copy gives that object (its RDFF's pack
  items whose picture is one of ravgear's), each it doesn't hold already (by picture);
- once: the creature's MARK byte (the last of its 16-byte name, a NUL after any seller's name) set, which
  the save keeps, so what the party buys isn't put back. A seller with all its items already (a new game's)
  is only marked.

A pack has 12 cells: an item with no free cell is left out (npcitems.add_to)."""

import os
import struct
from typing import Callable, Dict, List, Optional, Sequence

from . import dataitems, gff, ravgear

CREATURE_OBJECT, CREATURE_MARK = 0x06, 0x30  # (the creature record's object, negated; its name's last byte)
MARKED = 0x01
THING_PERSON = 2
# the sellers ravgear stocks: the weaponers, the armourers, the salespersons, the receptionist (picks), Notaku
SELLERS = (153, 323, 152, 322, 155, 320, 321, 142, 58)


def seller_items(objects: gff.Chunks, sellers: Sequence[int] = SELLERS) -> Dict[int, List[bytes]]:
    """Each seller's new item records (23 bytes, no slot) from OBJEX.GFF's copy OBJECTS: its RDFF's items whose
    picture is one of ravgear's."""
    mine = {ravgear.picture_object(k) for k in ravgear.GEAR}
    out: Dict[int, List[bytes]] = {}
    for obj in sellers:
        rdff = objects.get(("RDFF", obj))
        if rdff is None:
            continue
        recs, _ = dataitems.records(rdff)
        out[obj] = [r.data for r in recs if r.kind == dataitems.ITEM and len(r.data) >= 2
                    and -struct.unpack_from("<h", r.data, 0)[0] in mine]
    return out


def from_file(path: str) -> Dict[int, List[bytes]]:
    """seller_items() of the OBJEX.GFF copy at PATH ({} if there is none)."""
    try:
        with open(path, "rb") as f:
            return seller_items(gff.read_gff(f.read()))
    except (OSError, gff.GffError):
        return {}


def default_path() -> str:
    from . import launch, ravager
    return os.path.join(launch.DOS_DIR, ravager.OBJECTS_COPY)


def due(gd, stock: Dict[int, List[bytes]]) -> List[int]:
    """The creatures (numbers) loaded as people that are sellers of STOCK not yet marked."""
    from . import ring
    it = ring.Items(gd)
    out: List[int] = []
    for t in range(ring.THING_COUNT):
        kind, first = it.thing(t)
        if kind != THING_PERSON or not 0 <= first < 512 or first in out:
            continue
        rec = gd.creature(first)
        if len(rec) <= CREATURE_MARK or rec[CREATURE_MARK]:
            continue
        if -struct.unpack_from("<h", rec, CREATURE_OBJECT)[0] in stock:
            out.append(first)
    return out


def held_pictures(gd, creature: int) -> set:
    """The pictures of the items CREATURE holds in its three lists."""
    from . import game, ring
    it = ring.Items(gd)
    rec = gd.creature(creature)
    out = set()
    for o in game.CREATURE_ITEM_LISTS:
        thing = struct.unpack_from("<h", rec, o)[0]
        if 0 <= thing < ring.THING_COUNT:
            for _, data in it.chain(thing, inside=False):
                out.add(-struct.unpack_from("<h", data, 0)[0])
    return out


def top_up(gd, creature: int, stock: Dict[int, List[bytes]], mark: Callable[[int], None],
           add: Optional[Callable] = None) -> List[str]:
    """CREATURE's missing new items given (ADD: npcitems.add_to), then MARK(creature). Lines for the log."""
    from . import npcitems
    add = add or npcitems.add_to
    rec = gd.creature(creature)
    obj = -struct.unpack_from("<h", rec, CREATURE_OBJECT)[0]
    have = held_pictures(gd, creature)
    given, left = 0, 0
    for item in stock.get(obj, ()):
        if -struct.unpack_from("<h", item, 0)[0] in have:
            continue
        if add(gd, creature, item):
            given += 1
        else:
            left += 1
    mark(creature)
    if not given and not left:
        return []
    line = f"{gd.creature_name(creature)} stocks {given} of the mod's new items"
    return [line + (f" ({left} with no room)" if left else "")]
