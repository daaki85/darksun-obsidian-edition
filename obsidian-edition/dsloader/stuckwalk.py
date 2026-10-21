"""People who walk by a script of their own, set walking again when a walk has stopped for good.

A person the region's script gives a "no orders" script (CREATE_NOORDERS_TRIGGER, 6Fh: the
Trustee's rounds of the slave pens, GPL 8 at 3767) runs it whenever they have no order; a walk
is an order (15) that ends when they get there, and the script then sends them on. A save made
while one walks keeps the order but not the way: loaded, they stand with it for good, and the
script never runs again (the game's own way too: the Trustee of one save stood at a corner of
his rounds, busy for good after a talk). The Loader takes such an order back (0, no order) once
the person has stood still for STILL_FOR game seconds with it, out of fights; their script then
sends them on, as it would have.

The table (DSUN's 3972:08AAh, a 13h-byte entry for each of the first 48 objects: +00h the order,
+04h the script's address, +08h its file) is the game's per-creature scripts'."""

import struct
from typing import Dict, List, Tuple

from . import ring

TABLE_SEG, TABLE_OFF, ENTRY, PEOPLE = 0x3972, 0x08AA, 0x13, 48  # (+ the game's load segment)
ORDER, ADDRESS, FILE = 0x00, 0x04, 0x08
WALK = 15  # the order a walk is
PARTY = 4  # (objects 0-3: the party, never theirs)
THING_CREATURE = 2  # (a thing's kind: a creature)
STILL_FOR = 30  # game seconds (about 20 s): a walk not moved on in that long has stopped


class StuckWalkers:
    def __init__(self):
        self._still: Dict[int, Tuple[Tuple[int, int], int]] = {}  # object: (place, since)

    def forget(self) -> None:
        self._still.clear()

    def check(self, gd) -> List[str]:
        """The people set walking again this time (by name)."""
        now = gd.game_time()
        if now is None or gd.in_combat():
            self._still.clear()
            return []
        base = (gd.load_seg + TABLE_SEG) * 16 + TABLE_OFF
        table = gd.guest.read(base, PEOPLE * ENTRY)
        places = gd.guest.read(gd.ds * 16 + ring.POSITIONS, PEOPLE * ring.POSITION_SIZE)
        it = ring.Items(gd)
        out = []
        for thing in range(PARTY, PEOPLE):
            entry = table[thing * ENTRY:(thing + 1) * ENTRY]
            order, = struct.unpack_from("<H", entry, ORDER)
            script, = struct.unpack_from("<H", entry, FILE)
            kind, who = it.thing(thing)
            if order != WALK or not script or kind != THING_CREATURE:
                self._still.pop(thing, None)
                continue
            place = struct.unpack_from("<HH", places, thing * ring.POSITION_SIZE)
            was = self._still.get(thing)
            if was is None or was[0] != place or now < was[1]:
                self._still[thing] = (place, now)
                continue
            if now - was[1] >= STILL_FOR:
                gd.guest.write(base + thing * ENTRY + ORDER, struct.pack("<H", 0))
                del self._still[thing]
                out.append(gd.creature_name(who) or f"object {thing}")
        return out


def stopped_line(name: str) -> str:
    return f"{name} walks on (a walk saved halfway had left them standing)"
