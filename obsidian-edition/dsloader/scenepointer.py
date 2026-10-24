"""The game's own pointer in the scenes (DSCLOG's CP_DRAW): the arrow the game shows on its
screens (RESOURCE.GFF's ICON 6001) and its colours (GPLDATA.GFF's palette, PAL 1), read from the
player's game at each start into POINTER.BIN, which DSCLOG reads as it loads. In a scene each of
the arrow's colours is drawn as the scene's palette's nearest. Without the file DSCLOG draws a
plain arrow of its own."""

import os
from typing import List, Optional

from . import art, gff

POINTER_FILE = "POINTER.BIN"
POINTER_ICON = 6001  # (ICON: the game's pointer, as the first screens show it)
PALETTE = 1
ROWS, COLOURS, SHAPE = 16, 11, 88  # DSCLOG's room: CP_MAX_ROWS, CP_COLS, CP_SHAPE_BYTES
PIXELS = 76  # (CP_PIXELS: a byte kept for each pixel, drawn or clear)
END, CLEAR = 0, 0xFF  # (a row's end; a pixel not drawn)


def pointer_data(icon: bytes, palette: bytes) -> bytes:
    """POINTER.BIN: the rows (a byte), the colours (a byte), each colour's red, green, blue (6 bits,
    COLOURS of them), then each row's pixels from its left (a colour's number from 1, or CLEAR),
    ending with END, the rest END. ValueError if the arrow doesn't fit DSCLOG's room."""
    _, _, rows = art.decode_frame(icon)
    while rows and all(p is None for p in rows[-1]):
        rows = rows[:-1]
    colours: List[int] = sorted({p for row in rows for p in row if p is not None})
    shape, pixels = bytearray(), 0
    for row in rows:
        while row and row[-1] is None:
            row = row[:-1]
        shape += bytes(CLEAR if p is None else colours.index(p) + 1 for p in row) + bytes((END,))
        pixels += len(row)
    if len(rows) > ROWS or len(colours) > COLOURS or len(shape) > SHAPE or pixels > PIXELS:
        raise ValueError("the game's pointer is bigger than DSCLOG's room for it")
    rgb = b"".join(bytes(v & 0x3F for v in palette[c * 3:c * 3 + 3]) for c in colours)
    return bytes((len(rows), len(colours))) + rgb.ljust(COLOURS * 3, b"\0") + bytes(shape).ljust(SHAPE, b"\0")


def write_pointer(resources: Optional[str], gpldata: Optional[str], dest: str) -> bool:
    """POINTER.BIN at DEST from the game's files; without them (or the arrow), none: DSCLOG's own."""
    try:
        with open(resources, "rb") as f:
            icon = gff.read_gff(f.read())[("ICON", POINTER_ICON)]
        with open(gpldata, "rb") as f:
            palette = gff.read_gff(f.read())[("PAL ", PALETTE)]
        data = pointer_data(icon, palette)
    except (TypeError, OSError, KeyError, ValueError, IndexError, gff.GffError):
        try:
            os.remove(dest)
        except OSError:
            pass
        return False
    with open(dest, "wb") as f:
        f.write(data)
    return True
