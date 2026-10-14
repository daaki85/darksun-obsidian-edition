"""Magical items sold kept to buy back (buyback.py): what DSCLOG queued (SELL_KEEP) put in the
merchant's pack, and the thing that held it given back to the game's free list."""

import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dscompanion import buyback, game, ring
from test_dicelog import CREATURES, DS, ITEMS, LOAD_SEG
from test_now import ThiefTests

THINGS = (LOAD_SEG + game.COMBATANTS_SEG) * 16 + game.COMBATANTS_OFF
SOLD, BAG, MERCHANT, HDR = 330, 451, 77, 0x80000


class BuybackTests(unittest.TestCase):
    def setUp(self):
        """The item sold (40, a ring +1) alone in thing 330; the merchant, combatant 77, creature 5,
        carrying item 41 in its list (thing 451); one sale queued in a header at HDR."""
        thief = ThiefTests()
        thief.setUp()
        self.gd, m = thief.log.game, thief.log.guest.mem
        self.m = m
        struct.pack_into("<Bh", m, THINGS + SOLD * 3, game.THING_ITEM, 40)
        struct.pack_into("<Bh", m, THINGS + BAG * 3, game.THING_ITEM, 41)
        struct.pack_into("<Bh", m, THINGS + MERCHANT * 3, 2, 5)
        struct.pack_into("<hhh", m, CREATURES + 5 * game.CREATURE_SIZE + 8, BAG, game.NO_ITEM, game.NO_ITEM)
        for item in (40, 41):
            at = ITEMS + item * game.ITEM_SIZE
            m[at:at + game.ITEM_SIZE] = bytes(game.ITEM_SIZE)
            struct.pack_into("<h", m, at + game.ITEM_NEXT, game.NO_ITEM)
            m[at + game.ITEM_SLOT] = 0x20
        m[ITEMS + 40 * game.ITEM_SIZE + game.ITEM_PLUS] = 1
        struct.pack_into("<H", m, DS * 16 + ring.FREE_THINGS, 500)
        struct.pack_into("<H", m, DS * 16 + ring.THINGS_USED, 10)
        self.gd.item_name = lambda n: "Ring +1"
        self.gd.creature_name = lambda c: "Kel"
        struct.pack_into("<HHH", m, HDR + buyback.SOLD_SEQ, 0, 0, 0)

    def chain(self, thing):
        return [index for index, _ in ring.Items(self.gd).chain(thing)]

    def test_kept(self):
        """Into the merchant's list, first, in a backpack cell; thing 330 back on the free list."""
        b = buyback.Buyback()
        self.assertEqual(b.watch(self.gd, HDR), [])  # (the first look: from now on)
        struct.pack_into("<HHH", self.m, HDR + buyback.SOLD_SEQ, 1, SOLD, MERCHANT)
        self.assertEqual(b.watch(self.gd, HDR), [])  # (nothing in the log)
        self.assertEqual(b.kept, ["Ring +1"])
        self.assertEqual(self.chain(BAG), [40, 41])
        self.assertEqual(ring.Items(self.gd).thing(SOLD), (0, 500))
        self.assertEqual(struct.unpack_from("<H", self.m, DS * 16 + ring.FREE_THINGS)[0], SOLD)
        self.assertEqual(struct.unpack_from("<H", self.m, DS * 16 + ring.THINGS_USED)[0], 9)
        self.assertEqual(b.watch(self.gd, HDR), [])  # (done once)

    def test_no_merchant(self):
        """Sold to no creature: gone, as the game has it (the record freed, the thing too)."""
        b = buyback.Buyback()
        b.watch(self.gd, HDR)
        struct.pack_into("<HHH", self.m, HDR + buyback.SOLD_SEQ, 1, SOLD, 499)
        self.assertEqual(b.watch(self.gd, HDR), [])
        self.assertEqual(self.chain(BAG), [41])
        self.assertEqual(struct.unpack_from("<H", self.m, DS * 16 + ring.FREE_ITEMS)[0], 40)
        self.assertEqual(ring.Items(self.gd).thing(SOLD)[0], 0)


if __name__ == "__main__":
    unittest.main()
