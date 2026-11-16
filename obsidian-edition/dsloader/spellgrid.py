"""CHOOSE A SPELL's icons in a centred grid, six to a row (the Loader's copy of RESOURCE.GFF).

The game's window for it (WIND 17500) has 21 places for the spells on offer, APFM 2BCDh-2BE1h, in
seven columns 19 pixels apart (x 28 to 142) and three rows 20 apart (y 24, 44, 64). The game
fills them in that order, and the order isn't the columns': the first 15 are the middle five
columns, row by row (x 47 to 123), the next three the right-hand column (142), the last three the
left-hand one (28). Up to 15 spells the grid is centred; past that the right-hand column fills while
the left-hand one stays empty, and the grid sits right of centre. The game's own 4th level has 16
wizard spells; with the new spells (game.NEW_SPELLS) the 1st has 18 (the user's report, 2026-11-16).

Here the first 18 places are six columns 19 apart, filled row by row, centred where the game's
seven columns were (x 38 to 133, the middle at 94 as before); no level offers more than 18, and
the last three places stay where the game has them.
"""

import struct
from typing import Dict, Tuple

from . import gff

WINDOW = 17500  # CHOOSE A SPELL's window (WIND)
FIRST = 0x2BCD  # its first place (APFM), the spells on offer in order
COLUMNS, PLACES = 6, 18  # the new grid: six to a row, three rows
LEFT, TOP, STEP_X, STEP_Y = 38, 24, 19, 20
WIND_COUNT, ITEM_AT, ITEM_SIZE = 243, 0x105, 30  # (weaponpages': a window's items)


def place(n: int) -> Tuple[int, int]:
    """Where the Nth spell on offer (from 0) goes: (x, y) in the window."""
    return LEFT + STEP_X * (n % COLUMNS), TOP + STEP_Y * (n // COLUMNS)


def relaid(window: bytes) -> bytes:
    """WINDOW's items with the first PLACES spell places moved to the grid (the rest as they are)."""
    out = bytearray(window)
    count, = struct.unpack_from("<H", out, WIND_COUNT)
    for i in range(count):
        at = ITEM_AT + i * ITEM_SIZE
        if bytes(out[at + 4:at + 8]) != b"APFM":
            continue
        n = struct.unpack_from("<I", out, at + 8)[0] - FIRST
        if 0 <= n < PLACES:
            struct.pack_into("<HH", out, at + 12, *place(n))
    return bytes(out)


def chunks(resource: gff.Chunks) -> Dict[Tuple[str, int], bytes]:
    """For the Loader's copy of RESOURCE.GFF: CHOOSE A SPELL's window, its grid centred."""
    return {("WIND", WINDOW): relaid(resource[("WIND", WINDOW)])}
