"""The combat log's panel in the game (DSCLOG's PANEL), kept up by the Ledger.

DSCLOG draws the panel over the map, bottom right, from the game's main loop, again whenever the
game has drawn the floor since (the map is drawn straight into the screen on show, a rectangle at a
time). The Ledger turns it on in a fight (TSR_PANEL_ON) and off after, when DSCLOG has the view
drawn again without it, and picks its colours: the game's stone (palette.py) matched to the
nearest of the area's palette, once DSCLOG has read it (for the shadows: shadows.Shadows.palettes),
among the colours the game doesn't animate. Stage 1 of the design (docs/combat-log/HANDOFF.md):
the frame alone.
"""

import struct
from typing import Optional, Sequence, Tuple

from . import palette, shadows

TSR_HDR_OFF = 20  # DSCLOG's header: where it is in DSCLOG's segment
TSR_DAC = 238  # ... the offset of DAC, the palette as DSCLOG last read it (768 values, 0-63)
TSR_PANEL_ON, TSR_PANEL_COL = 326, 328  # ... the panel shown; its ten colours
FIRST, LAST = 16, 223  # the palette's colours the game doesn't animate (DSCLOG's DARK_FIRST, DARK_LAST)
# the frame's colours, in DSCLOG's order (P_OUTLINE to P_WELL_LO): outline, light, stone, dark, well,
# handle, and the stone's grain, a lighter and a darker speckle (as the game's own status box has)
# and the well's, fainter (the log's text goes on it)
GRAIN_HI, GRAIN_LO = "#8A8AA2", "#5F5F78"
WELL_HI, WELL_LO = "#3C3C5C", "#262640"
FRAME = (palette.SHADOW, palette.EDGE_LIT, palette.BUTTON, palette.STONE, palette.DEEP, palette.EDGE_LIT,
         GRAIN_HI, GRAIN_LO, WELL_HI, WELL_LO)


def rgb(colour: str) -> Tuple[int, int, int]:
    return tuple(int(colour[i:i + 2], 16) for i in (1, 3, 5))


def nearest(dac: bytes, colour: Tuple[int, int, int]) -> int:
    """The palette index (FIRST to LAST) nearest to COLOUR (0-255 a channel) in DAC (0-63 a
    channel, as the VGA's)."""
    def distance(index: int) -> int:
        return sum((dac[index * 3 + c] * 4 + dac[index * 3 + c] // 16 - colour[c]) ** 2 for c in range(3))
    return min(range(FIRST, LAST + 1), key=distance)


def frame_colours(dac: bytes, colours: Sequence[str] = FRAME) -> bytes:
    return bytes(nearest(dac, rgb(c)) for c in colours)


class Panel:
    def __init__(self):
        self._on: Optional[bool] = None
        self._palettes = 0

    def update(self, gd, tsr_hdr: int, on: bool, palettes: int) -> None:
        """ON: the panel shown (once its colours are picked from a palette DSCLOG has read:
        PALETTES counts the reads)."""
        guest = gd.guest
        if on and palettes and palettes != self._palettes:
            base = tsr_hdr - struct.unpack("<H", guest.read(tsr_hdr + TSR_HDR_OFF, 2))[0]
            dac_off, = struct.unpack("<H", guest.read(tsr_hdr + TSR_DAC, 2))
            guest.write(tsr_hdr + TSR_PANEL_COL, frame_colours(guest.read(base + dac_off, 768)))
            self._palettes = palettes
            if self._on:  # (the view drawn again, and the panel over it in the new colours)
                shadows.redraw(gd, tsr_hdr)
        want = on and self._palettes > 0
        if want != self._on:
            guest.write(tsr_hdr + TSR_PANEL_ON, struct.pack("<H", int(want)))
            self._on = want
