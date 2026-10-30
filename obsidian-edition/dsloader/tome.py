"""The Tome of Understanding: +1 Wisdom for whoever reads it, used as a scroll is.

A scroll is an item of the game's type 96 whose spell byte (+0Fh) is one past its spell's
number. Right-clicked, its box shows the spell's icon; clicked, the icon has the game (its
routine at DSUN.EXE 8B690h) teach the spell to the one whose scroll it is when the scroll's
object is 1400 to 1499 (the game's own scrolls), and use it up; any other object it casts. A
number of 138 to 171 is a psionic power, taught the same way; one of 172 to 195 the game has no
use for: it shows a message ("CANNOT LEARN FROM THIS ITEM") and keeps the scroll. (From 196 on, the
box's icon can't be clicked at all.)

The tome is such a scroll (object TOME_OBJECT, in the scrolls' numbers), its spell byte one past
TOME_SPELL. DSCLOG's PROBE_TOME, where the game would show that message, raises the reader's
WIS by one (in the sheet and the creature record; at most 25) and goes on as for a power taught:
the game uses the tome up and shows the helper's message ("Cilla reads the tome: WIS 19.").

Its object and pictures, in the Loader's copy of SEGOBJEX: object TOME_OBJECT, the game's
scroll's (1400: the box's icon is clicked only for an object of a scroll's kind, +4) with an icon
of its own, the game's book's (Jasmine's Book, 1128) with its cover night steel and its emblem in
the fire colours the game cycles on its magic items (icons.py's); its picture on the map the
book's. Picture TOME_OBJECT was the game's, an icon of other objects: they get it as MOVED, as
Kalzith's scrolls' do (kalzith.py). Its item record, which Father Garyn's script gives (garyn.py),
is the object's own record (dataitems.item_object).
"""

import struct
from typing import Dict, List, Tuple

from . import dataitems, game, icons

TOME_OBJECT = 1446  # (the game's scrolls 1400-1432, Kalzith's 1440-1445)
MOVED = 2552  # where picture TOME_OBJECT goes
ICON = 2553
BOOK = 1128  # Jasmine's Book: the game's book
SCROLL = 1400  # the game's first scroll object
TOME_SPELL = 0xB0  # a "spell" the game has none of (172 or more; below 196, or its box's icon can't be
# clicked): DSCLOG's TOME_SPELL
SCROLL_TYPE = 96
NAME = 0x157  # a name entry DSCLOG adds
NAMES = {NAME: b"Tome/Understand"}  # (the game's 15 letters: "Tome of Understanding" on the Loader's screens)
VALUE = 43500  # AD&D's 43,500 gp
COVER = {74: 18, 75: 20, 76: 22, 77: 24, 78: 27}  # the book's reds to night steel, light for light
EMBLEM = (182, 45)  # its golds


def item() -> bytes:
    """The tome's record (as an item's in memory, in no list and no slot)."""
    rec = bytearray(game.ITEM_SIZE)
    struct.pack_into("<h", rec, 0, -TOME_OBJECT)
    struct.pack_into("<H", rec, 0x02, TOME_SPELL + 1)  # (the spell its box's icon shows)
    struct.pack_into("<h", rec, game.ITEM_NEXT, game.NO_ITEM)
    struct.pack_into("<H", rec, 0x06, VALUE)
    struct.pack_into("<h", rec, 0x08, game.NO_ITEM)
    struct.pack_into("<H", rec, game.ITEM_TYPE, SCROLL_TYPE)
    rec[0x0F] = TOME_SPELL + 1
    rec[0x10] = 5  # (as the game's scrolls)
    rec[game.ITEM_SLOT] = 0xFF
    struct.pack_into("<H", rec, game.ITEM_NAME, NAME)
    return bytes(rec)


def is_tome(rec: bytes) -> bool:
    return len(rec) >= game.ITEM_SIZE and struct.unpack_from("<h", rec, 0)[0] == -TOME_OBJECT \
        and rec[0x0F] == TOME_SPELL + 1


def icon(rows: icons.Rows) -> icons.Rows:
    return icons.glow(icons.recolour(rows, COVER), lambda p, x, y: p in EMBLEM, icons.FIRE)


def object_chunks(chunks, header_number: int = 0) -> Dict[Tuple[str, int], bytes]:
    """For the Loader's copy of SEGOBJEX: the tome's object, pictures and record, and picture
    TOME_OBJECT's owners pointed to MOVED. Nothing if a number of its is taken (KeyError)."""
    if ("OJFF", TOME_OBJECT) in chunks or ("RDFF", TOME_OBJECT) in chunks \
            or any(key[1] in (MOVED, ICON) for key in chunks):
        raise KeyError(f"object {TOME_OBJECT} or picture {MOVED} or {ICON} taken")
    old_icon, = struct.unpack_from("<H", chunks[("OJFF", BOOK)], icons.OJFF_ICON)
    scroll = bytearray(chunks[("OJFF", SCROLL)])
    out: Dict[Tuple[str, int], bytes] = {}
    if ("BMP ", TOME_OBJECT) in chunks:
        out[("BMP ", MOVED)] = chunks[("BMP ", TOME_OBJECT)]
        for (kind, number), data in chunks.items():
            if kind == "OJFF" and len(data) >= icons.OJFF_ICON + 2 \
                    and struct.unpack_from("<H", data, icons.OJFF_ICON)[0] == TOME_OBJECT:
                rec = bytearray(data)
                struct.pack_into("<H", rec, icons.OJFF_ICON, MOVED)
                out[("OJFF", number)] = bytes(rec)
    struct.pack_into("<H", scroll, icons.OJFF_ICON, ICON)
    out[("OJFF", TOME_OBJECT)] = bytes(scroll)
    out[("BMP ", TOME_OBJECT)] = chunks[("BMP ", BOOK)]  # its picture on the map: the book's
    out[("BMP ", ICON)] = icons.encode(icon(icons.decode(chunks[("BMP ", old_icon)])))
    out[("RDFF", TOME_OBJECT)] = dataitems.item_object(item(), header_number)
    return out


def owners(chunks) -> List[int]:
    """The objects whose icon is picture TOME_OBJECT (the game's)."""
    return sorted(n for (k, n), d in chunks.items() if k == "OJFF" and len(d) >= icons.OJFF_ICON + 2
                  and struct.unpack_from("<H", d, icons.OJFF_ICON)[0] == TOME_OBJECT)
