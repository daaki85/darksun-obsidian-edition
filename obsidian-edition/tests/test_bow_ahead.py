"""weaponchoice.bow_ahead: a missile weapon put ahead of its ammunition in the item list."""

import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import game, weaponchoice  # noqa: E402

ITEMS = 0x2000


class FakeGd:
    """Items 5, 6, 7 in that list order (the links at +4): the arrows (ammo slot), the bow
    (missile slot), a sword."""

    def __init__(self, slots):
        self.mem = bytearray(0x10000)
        self.ds = 0x100
        struct.pack_into("<HH", self.mem, self.ds * 16 + game.ITEMS_PTR, 0, ITEMS // 16)
        self.order = (5, 6, 7)
        for n, (index, slot) in enumerate(zip(self.order, slots)):
            rec = bytearray(game.ITEM_SIZE)
            struct.pack_into("<H", rec, game.ITEM_NEXT, self.order[n + 1] if n + 1 < len(self.order) else game.NO_ITEM)
            rec[game.ITEM_SLOT], rec[0] = slot, index  # (+0: a mark of which item it was)
            self.mem[ITEMS + index * game.ITEM_SIZE:ITEMS + (index + 1) * game.ITEM_SIZE] = rec
        gd = self

        class Guest:
            def read(self, at, n):
                return bytes(gd.mem[at:at + n])

            def write(self, at, data):
                gd.mem[at:at + len(data)] = data

        self.guest = Guest()

    def rec(self, index):
        return bytes(self.mem[ITEMS + index * game.ITEM_SIZE:ITEMS + (index + 1) * game.ITEM_SIZE])

    def _worn(self, member):
        index = self.order[0]
        while index != game.NO_ITEM:
            rec = self.rec(index)
            yield index, rec, b""
            index = struct.unpack_from("<H", rec, game.ITEM_NEXT)[0]


class BowAheadTests(unittest.TestCase):
    def test_swapped(self):
        """The arrows first: the two records' contents swapped, each keeping its link."""
        gd = FakeGd((weaponchoice.AMMO_SLOT, weaponchoice.MISSILE_SLOT, 3))
        weaponchoice.bow_ahead(gd, 0)
        self.assertEqual([rec[game.ITEM_SLOT] for _, rec, _ in gd._worn(0)],
                         [weaponchoice.MISSILE_SLOT, weaponchoice.AMMO_SLOT, 3])
        self.assertEqual([rec[0] for _, rec, _ in gd._worn(0)], [6, 5, 7])

    def test_kept(self):
        """The bow first already, or no arrows: as it is."""
        for slots in ((weaponchoice.MISSILE_SLOT, weaponchoice.AMMO_SLOT, 3), (weaponchoice.MISSILE_SLOT, 3, 10)):
            gd = FakeGd(slots)
            before = bytes(gd.mem)
            weaponchoice.bow_ahead(gd, 0)
            self.assertEqual(bytes(gd.mem), before)


if __name__ == "__main__":
    unittest.main()
