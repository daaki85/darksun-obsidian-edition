"""The combat log's panel in the game (DSCLOG's PANEL), drawn and kept up by the Ledger.

The Ledger draws the panel, a picture of PANEL_W x PANEL_H palette indices (render), and puts it
in the memory block DSCLOG keeps for it (TSR_PANEL_SEG); DSCLOG puts the picture over the map,
bottom right, from the game's main loop and after each rectangle of the view the game draws again
(the map is drawn straight into the screen on show, a rectangle at a time). The Ledger turns it on
in a fight (TSR_PANEL_ON) and off after, when DSCLOG has the view drawn again without it.

The picture is in the area's own colours: the game's stone (palette.py) matched to the nearest of
the palette DSCLOG last read (for the shadows: shadows.Shadows.palettes), among the colours the
game doesn't animate, and drawn again when that palette changes. The frame is the stone of the
game's status box, speckled; the well, where the log's lines will go, mottled like the game's
dialogue window, in darker shades. Stage 1 of the design (docs/combat-log/HANDOFF.md): no lines yet.
"""

import struct
from typing import Dict, List, Optional, Tuple

from . import palette

TSR_HDR_OFF = 20  # DSCLOG's header: where it is in DSCLOG's segment
TSR_DAC = 238  # ... the offset of DAC, the palette as DSCLOG last read it (768 values, 0-63)
TSR_PANEL_ON, TSR_PANEL_SEG, TSR_PANEL_NEW = 326, 328, 330  # ... the panel shown; its picture; a new one
PANEL_W, PANEL_H = 180, 68  # (DSCLOG's PANEL_W, PANEL_H)
PANEL_X0, PANEL_Y0 = 136, 128  # (DSCLOG's: where on the screen)
FIRST, LAST = 16, 223  # the palette's colours the game doesn't animate (DSCLOG's DARK_FIRST, DARK_LAST)

RGB = Tuple[int, int, int]
# the picture's colours
COLOURS = {
    "outline": palette.SHADOW, "light": palette.EDGE_LIT, "stone": palette.BUTTON, "dark": palette.STONE,
    "grain_hi": "#8A8AA2", "grain_lo": "#5F5F78",  # the stone's speckles, as the status box's
    "handle": palette.EDGE_LIT,
    # the well: four shades of the deep blue-grey, mottled (palette.DEEP the most of it)
    "well0": "#262640", "well1": "#2C2C48", "well2": palette.DEEP, "well3": "#3A3A5A",
}
WELL = (4, 15, PANEL_W - 5, PANEL_H - 5)  # x0, y0, x1, y1 (inclusive), in the picture
GRAIN_HI_N, GRAIN_LO_N = 32, 32  # (of 256: the stone's pixels speckled lighter, darker)


def rgb(colour: str) -> RGB:
    return tuple(int(colour[i:i + 2], 16) for i in (1, 3, 5))


def nearest(dac: bytes, colour: RGB) -> int:
    """The palette index (FIRST to LAST) nearest to COLOUR (0-255 a channel) in DAC (0-63 a
    channel, as the VGA's)."""
    def distance(index: int) -> int:
        return sum((dac[index * 3 + c] * 4 + dac[index * 3 + c] // 16 - colour[c]) ** 2 for c in range(3))
    return min(range(FIRST, LAST + 1), key=distance)


def _speckle(x: int, y: int) -> int:
    """A pattern fixed by x and y, 0-255 (the stone's grain, the well's dither)."""
    v = (x * 29 + y * 71) & 0xFFFF
    v ^= v >> 4
    return (v * 0x6D) & 0xFF


def _lattice(i: int, j: int) -> int:
    v = (i * 113 + j * 197 + 0x55) & 0xFFFF
    v ^= v >> 5
    return ((v * 0x9D) & 0xFFFF) >> 3 & 0xFF


def _smooth(x: int, y: int, shift: int) -> int:
    """Value noise, cells of 1 << SHIFT pixels: 0-255."""
    size = 1 << shift
    i, j, fx, fy = x >> shift, y >> shift, x & (size - 1), y & (size - 1)
    top = _lattice(i, j) * (size - fx) + _lattice(i + 1, j) * fx
    bottom = _lattice(i, j + 1) * (size - fx) + _lattice(i + 1, j + 1) * fx
    return (top * (size - fy) + bottom * fy) >> (2 * shift)


def mottle(x: int, y: int) -> int:
    """The well's shade at x, y (0 darkest to 3): blotches of 4 and 8 pixels, their edges
    dithered, as the game's dialogue window's stone."""
    v = (_smooth(x, y, 3) * 2 + _smooth(x + 37, y + 11, 2)) // 3 + (_speckle(x, y) & 31) - 16
    return 0 if v < 92 else 1 if v < 118 else 2 if v < 160 else 3


def render(dac: bytes) -> bytes:
    """The panel's picture, PANEL_W x PANEL_H palette indices row by row, in the colours of DAC."""
    ink: Dict[str, int] = {name: nearest(dac, rgb(c)) for name, c in COLOURS.items()}
    w, h = PANEL_W, PANEL_H
    rows: List[bytearray] = [bytearray(w) for _ in range(h)]

    def fill(x0: int, y0: int, x1: int, y1: int, colour: int) -> None:
        for y in range(y0, y1 + 1):
            rows[y][x0:x1 + 1] = bytes((colour,)) * (x1 - x0 + 1)

    fill(0, 0, w - 1, h - 1, ink["outline"])
    for y in range(1, h - 1):  # the stone, speckled
        for x in range(1, w - 1):
            n = _speckle(x + PANEL_X0, y + PANEL_Y0)
            rows[y][x] = ink["grain_hi"] if n < GRAIN_HI_N else ink["grain_lo"] if n < GRAIN_HI_N + GRAIN_LO_N \
                else ink["stone"]
    fill(1, 1, w - 2, 1, ink["light"])  # the bevel, lit from the upper left
    fill(1, 1, 1, h - 2, ink["light"])
    fill(2, h - 2, w - 2, h - 2, ink["dark"])
    fill(w - 2, 2, w - 2, h - 2, ink["dark"])
    fill(3, 12, w - 4, 12, ink["dark"])  # the header's groove
    fill(3, 13, w - 4, 13, ink["light"])
    x0, y0, x1, y1 = WELL
    shades = [ink["well0"], ink["well1"], ink["well2"], ink["well3"]]
    for y in range(y0, y1 + 1):  # the well, mottled
        for x in range(x0, x1 + 1):
            rows[y][x] = shades[mottle(x, y)]
    fill(x1 - 6, y0 + 1, x1 - 1, y1 - 1, ink["dark"])  # the scrollbar ...
    fill(x1 - 5, y1 - 17, x1 - 2, y1 - 2, ink["handle"])  # ... and its handle
    return b"".join(bytes(r) for r in rows)


class Panel:
    def __init__(self):
        self._on: Optional[bool] = None
        self._palettes = 0

    def update(self, gd, tsr_hdr: int, on: bool, palettes: int) -> None:
        """ON: the panel shown (once it is drawn in a palette DSCLOG has read: PALETTES counts the
        reads)."""
        guest = gd.guest
        seg, = struct.unpack("<H", guest.read(tsr_hdr + TSR_PANEL_SEG, 2))
        if not seg:  # (no memory for it: no panel)
            on = False
        if on and palettes and palettes != self._palettes:
            base = tsr_hdr - struct.unpack("<H", guest.read(tsr_hdr + TSR_HDR_OFF, 2))[0]
            dac_off, = struct.unpack("<H", guest.read(tsr_hdr + TSR_DAC, 2))
            guest.write(seg * 16, render(guest.read(base + dac_off, 768)))
            guest.write(tsr_hdr + TSR_PANEL_NEW, struct.pack("<H", 1))
            self._palettes = palettes
        want = on and self._palettes > 0
        if want != self._on:
            guest.write(tsr_hdr + TSR_PANEL_ON, struct.pack("<H", int(want)))
            self._on = want
