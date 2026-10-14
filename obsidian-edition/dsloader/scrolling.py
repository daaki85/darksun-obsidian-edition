"""Scrolling the map with the mouse (DSCLOG's SCROLLING), switched by the Loader.

DSCLOG does the dragging: holding the wheel pressed (the middle button) and moving scrolls the
map with the pointer; so, if switched on, does holding the right button, a right click still
being the game's (walk, use, look). (DSCLOG's PAN_X and PAN_Y, which also scroll the map, are the
Tab-chosen enemy's: targeting.py.)
"""

import struct
from typing import Optional

TSR_SCROLL_ON = 228  # DSCLOG's header
DRAG_MIDDLE, DRAG_RIGHT = 1, 2  # (TSR_SCROLL_ON's bits: the buttons that drag the map)


class Scrolling:
    def __init__(self):
        self._on: Optional[int] = None

    def forget(self) -> None:
        """A new DSCLOG (the game started again): the switch is written again."""
        self._on = None

    def update(self, gd, tsr_hdr: int, on: bool, right: bool = False) -> None:
        """ON: dragging with the wheel pressed scrolls the map; RIGHT: so does a drag with the
        right button."""
        bits = (DRAG_MIDDLE | (DRAG_RIGHT if right else 0)) if on else 0
        if bits != self._on:
            gd.guest.write(tsr_hdr + TSR_SCROLL_ON, struct.pack("<H", bits))
            self._on = bits
