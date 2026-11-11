"""Kurzak's door, open but barring the way, opened on the walk map too.

Kurzak's door is the slave pens' entryway (squares 99,33-34; its two leaves objects 2145 and
2146). His call to the arena opens it, and the party walks through it to him, or Legcrusher
through it to fetch them; it is the only way between his stop and the pens' south passages. A
user's save (2026-11-11, "error doorway blocked") had both leaves open, drawn open, but the
game's live walk map (far pointer DS:0556h, 128 x 98 bytes, a byte a square: 0 floor, 192 and up
a closed door) still had square 99,34 shut: the party could not step into the doorway, and
Legcrusher, sent for them, stood still with nowhere to walk. How the two came apart the save
doesn't show (the door's swing is the game's own, and its saves keep the map as it was).

The Loader puts that square right: in the pens, out of fights, when both leaves are open (their
map records' +12h, bit 08h; a shut leaf has 10h or 20h there) and the square has stood shut for
SHUT_FOR game seconds (longer than a door's swing, so never in the middle of one), it is floor
again (0, the region file's own). The game's scripts then go on as they would: in the user's
save Legcrusher walked through at once and said his line.
"""

import struct
from typing import Optional

from . import game

REGION = 0x29  # the slave pens
LEAVES = (2145, 2146)
SQUARE = (99, 34)  # (the doorway's other square, 99,33, is floor whether open or shut)
WALK_MAP, MAP_WIDTH = 0x0556, 128  # DS: far pointer to the live walk map
SHUT = 192  # (a closed door, or more: 193, 204, 205)
FLOOR = 0
THINGS, THING_SIZE = 0x6694, 32  # DS: the map's things (sprites.MAP_ENTRIES)
LEAF_STATE, LEAF_OPEN = 0x12, 0x08
SHUT_FOR = 10  # game seconds


class DoorMend:
    def __init__(self):
        self._since: Optional[int] = None  # the game time the open door was first seen shut

    def forget(self) -> None:
        self._since = None

    def check(self, gd) -> bool:
        """True when the doorway was opened on the walk map this time."""
        now = gd.game_time()
        if now is None or gd.in_combat() or gd.region() != REGION or not self._open(gd):
            self._since = None
            return False
        at = game.far_pointer(gd.guest, gd.ds, WALK_MAP) + SQUARE[1] * MAP_WIDTH + SQUARE[0]
        if gd.guest.read(at, 1)[0] < SHUT:
            self._since = None
            return False
        if self._since is None or now < self._since:
            self._since = now
            return False
        if now - self._since < SHUT_FOR:
            return False
        gd.guest.write(at, bytes([FLOOR]))
        self._since = None
        return True

    @staticmethod
    def _open(gd) -> bool:
        things = [t for obj in LEAVES for t in gd.things_of(obj)]
        if len(things) != len(LEAVES):
            return False
        for t in things:
            state = gd.guest.read(gd.ds * 16 + THINGS + t * THING_SIZE + LEAF_STATE, 1)[0]
            if not state & LEAF_OPEN:
                return False
        return True


def opened_line() -> str:
    return "Kurzak's door: open, but its doorway was barred on the map; opened"
