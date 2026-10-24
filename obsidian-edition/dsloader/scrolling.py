"""Scrolling the map with the mouse (DSCLOG's SCROLLING), switched by the Loader.

DSCLOG does the dragging: holding the wheel pressed (the middle button) and moving scrolls the
map with the pointer. (DSCLOG's PAN_X and PAN_Y, which also scroll the map, are the
Tab-chosen enemy's: targeting.py.)
"""

import struct
from typing import Optional

TSR_SCROLL_ON = 228  # DSCLOG's header
DRAG_MIDDLE = 1  # (TSR_SCROLL_ON's bit: the wheel drags the map)


class Scrolling:
    def __init__(self):
        self._on: Optional[int] = None

    def forget(self) -> None:
        """A new DSCLOG (the game started again): the switch is written again."""
        self._on = None

    def update(self, gd, tsr_hdr: int, on: bool) -> None:
        """ON: dragging with the wheel pressed scrolls the map."""
        bits = DRAG_MIDDLE if on else 0
        if bits != self._on:
            gd.guest.write(tsr_hdr + TSR_SCROLL_ON, struct.pack("<H", bits))
            self._on = bits
