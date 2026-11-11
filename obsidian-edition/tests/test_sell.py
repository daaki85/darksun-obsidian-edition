"""Selling a member's plain gear in one go (sell.py): what counts, what it fetches."""
import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import game, pickpocket, ring, sell  # noqa: E402
from test_dicelog import CREATURES, ITEM_TYPES, ITEMS  # noqa: E402
from test_pickpocket import THINGS, PickTests  # noqa: E402

PACK = 460  # (Dag's backpack list's thing)


def load_tests(loader, tests, pattern):
    return loader.loadTestsFromTestCase(SellTests)


class SellTests(unittest.TestCase):
    def setUp(self):
        """Dag (member 0) with a backpack of four: a plain long sword (value 50), a long sword +1, a
        bag (worn nowhere, no weapon: not gear) and plain arrows, a stack of 20 at 2 each."""
        pick = PickTests()
        pick.setUp()
        self.m, self.gd = pick.m, pick.log.game
        m = self.m
        struct.pack_into("<h", m, CREATURES + 0 * game.CREATURE_SIZE + pickpocket.PACK_LIST, PACK)
        struct.pack_into("<Bh", m, THINGS + PACK * 3, game.THING_ITEM, 90)
        m[ITEM_TYPES + 45 * game.ITEM_TYPE_SIZE] = 1  # (long sword: melee)
        m[ITEM_TYPES + 70 * game.ITEM_TYPE_SIZE + sell.WORN_AT] = sell.AMMUNITION  # (arrows: ammunition ...
        m[ITEM_TYPES + 70 * game.ITEM_TYPE_SIZE + 0x0F] = sell.STACKS  # ... in a stack)
        m[ITEM_TYPES + 71 * game.ITEM_TYPE_SIZE] = 1  # (a plain club, stacked: priced times its count)
        m[ITEM_TYPES + 71 * game.ITEM_TYPE_SIZE + 0x0F] = sell.STACKS
        for item, nxt, typ, value, plus, slot, count in ((90, 91, 45, 50, 0, 14, 0), (91, 92, 45, 900, 1, 15, 0),
                                                        (92, 93, 66, 5, 0, 16, 0), (93, game.NO_ITEM, 70, 2, 0, 17, 20)):
            rec = bytearray(game.ITEM_SIZE)
            struct.pack_into("<H", rec, sell.COUNT, count)
            struct.pack_into("<h", rec, game.ITEM_NEXT, nxt)
            struct.pack_into("<H", rec, sell.VALUE, value)
            struct.pack_into("<H", rec, game.ITEM_TYPE, typ)
            struct.pack_into("<H", rec, game.ITEM_NAME, 21 if typ == 45 else 20)
            rec[game.ITEM_PLUS], rec[game.ITEM_SLOT] = plus, slot
            m[ITEMS + item * game.ITEM_SIZE:ITEMS + (item + 1) * game.ITEM_SIZE] = rec
        self.money = self.gd.money()

    def pack(self):
        return [i for i, _ in ring.Items(self.gd).chain(PACK, inside=False)]

    def test_sells_the_plain_gear(self):
        """The plain sword sold; the sword +1, the bag and the arrows (ammunition: never) kept."""
        self.gd.rules &= ~game.RULE_CHA_PRICES
        lines, paid = sell.sell(self.gd, 0)
        self.assertEqual(paid, 50)
        self.assertEqual(self.pack(), [91, 92, 93])
        self.assertEqual(self.gd.money(), self.money + 50)
        self.assertTrue(lines[0].startswith("Dag sells 1 things for 50 ceramic pieces"))

    def test_shops_as_in_add(self):
        self.gd.rules |= game.RULE_CHA_PRICES
        _, paid = sell.sell(self.gd, 0)
        self.assertEqual(paid, 30)  # (60% of 50)

    def test_a_stack_times_its_count(self):
        self.gd.rules &= ~game.RULE_CHA_PRICES
        struct.pack_into("<H", self.m, ITEMS + 93 * game.ITEM_SIZE + game.ITEM_TYPE, 71)
        _, paid = sell.sell(self.gd, 0)
        self.assertEqual(paid, 50 + 2 * 20)

    def test_nothing_to_sell(self):
        self.m[ITEMS + 90 * game.ITEM_SIZE + game.ITEM_PLUS] = 1
        lines, paid = sell.sell(self.gd, 0)
        self.assertEqual((paid, lines), (0, ["Dag has no plain gear in the backpack to sell."]))
        self.assertEqual(self.pack(), [90, 91, 92, 93])

    def test_metal_kept(self):
        m = self.m
        m[ITEM_TYPES + 45 * game.ITEM_TYPE_SIZE + 0x08] = 4  # (the long sword's material: metal)
        lines, paid = sell.sell(self.gd, 0)
        self.assertEqual(paid, 0)
        self.assertIn(90, self.pack())

    def test_a_body_slot_kept(self):
        """An item whose slot is one of the body's (3, the weapon hand), even in the backpack's list,
        isn't sold (plain_gear's slot test)."""
        self.m[ITEMS + 90 * game.ITEM_SIZE + game.ITEM_SLOT] = 3
        sell.sell(self.gd, 0)
        self.assertIn(90, self.pack())

    def test_worn_and_held_lists_untouched(self):
        """What is worn (+08h) or held (+0Ah) is in lists of its own, which S never reads: a plain
        sword in each stays, whatever is sold from the backpack."""
        m = self.m
        for offset, thing, item, slot in ((0x08, 461, 94, 10), (0x0A, 462, 95, 3)):
            struct.pack_into("<h", m, CREATURES + 0 * game.CREATURE_SIZE + offset, thing)
            struct.pack_into("<Bh", m, THINGS + thing * 3, game.THING_ITEM, item)
            m[ITEMS + item * game.ITEM_SIZE:ITEMS + (item + 1) * game.ITEM_SIZE] = \
                m[ITEMS + 90 * game.ITEM_SIZE:ITEMS + 91 * game.ITEM_SIZE]
            struct.pack_into("<h", m, ITEMS + item * game.ITEM_SIZE + game.ITEM_NEXT, game.NO_ITEM)
            m[ITEMS + item * game.ITEM_SIZE + game.ITEM_SLOT] = slot
        self.gd.rules &= ~game.RULE_CHA_PRICES
        _, paid = sell.sell(self.gd, 0)
        self.assertEqual(paid, 50)  # (the backpack's plain sword alone)
        for thing, item in ((461, 94), (462, 95)):
            self.assertEqual([i for i, _ in ring.Items(self.gd).chain(thing, inside=False)], [item])


if __name__ == "__main__":
    unittest.main()
