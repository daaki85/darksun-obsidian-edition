"""What Kalzith leaves when killed: one of his scrolls (kalzith.loot), with whatever else he still
carries; his shop sold out (kalzith.sold_out)."""

import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import game, kalzith, ring
from test_dicelog import CREATURES, DS, ITEMS, LOAD_SEG
from test_now import ThiefTests

THINGS = (LOAD_SEG + game.COMBATANTS_SEG) * 16 + game.COMBATANTS_OFF
PILE, BAG = 450, 451


class LootTests(unittest.TestCase):
    def setUp(self):
        """His pile (object 450): three of his scrolls (items 80-82: Magic Missile, Blur, Lightning
        Bolt); the party's leader holds a fourth (83, Color Spray, bought); free item records 90-92."""
        thief = ThiefTests()
        thief.setUp()
        self.gd, m = thief.log.game, thief.log.guest.mem
        self.m = m
        self.flags = {kalzith.DIED}
        self.gd.flag = lambda n: n in self.flags
        self.gd.set_flag = lambda n, on=True: self.flags.add(n) if on else self.flags.discard(n)
        struct.pack_into("<Bh", m, THINGS + PILE * 3, game.THING_ITEM, 80)
        struct.pack_into("<Bh", m, THINGS + BAG * 3, game.THING_ITEM, 83)
        struct.pack_into("<hhh", m, CREATURES + 8, BAG, game.NO_ITEM, game.NO_ITEM)
        for item, k, nxt in ((80, 0, 81), (81, 2, 82), (82, 4, game.NO_ITEM), (83, 1, game.NO_ITEM)):
            rec = kalzith.scroll(kalzith.SCROLLS[k][0], kalzith.SCROLLS[k][2], k)
            m[ITEMS + item * game.ITEM_SIZE:ITEMS + (item + 1) * game.ITEM_SIZE] = rec
            struct.pack_into("<h", m, ITEMS + item * game.ITEM_SIZE + game.ITEM_NEXT, nxt)
        for item, nxt in ((90, 91), (91, 92), (92, game.NO_ITEM)):
            struct.pack_into("<h", m, ITEMS + item * game.ITEM_SIZE + game.ITEM_NEXT, nxt)
        struct.pack_into("<H", m, DS * 16 + ring.FREE_ITEMS, 90)

    def objects(self, thing):
        return [-struct.unpack_from("<h", rec, 0)[0] for _, rec in ring.Items(self.gd).chain(thing)]

    def test_loot(self):
        """One scroll kept (here Blur), the other two taken back to the free list; the party's
        own scroll untouched; once only."""
        left = kalzith.loot(self.gd, choose=lambda items: 81)
        self.assertEqual(left, ["Scroll of Blur"])
        self.assertEqual(self.objects(PILE), [kalzith.SCROLL_OBJECT + 2])
        self.assertEqual(self.objects(BAG), [kalzith.SCROLL_OBJECT + 1])
        free, = struct.unpack_from("<H", self.m, DS * 16 + ring.FREE_ITEMS)
        self.assertIn(free, (80, 82))  # (both given back)
        self.assertIn(kalzith.LOOTED, self.flags)
        self.assertEqual(kalzith.loot(self.gd), [])

    def test_kept_first(self):
        """The kept scroll first in the pile: the others after it go."""
        kalzith.loot(self.gd, choose=lambda items: 80)
        self.assertEqual(self.objects(PILE), [kalzith.SCROLL_OBJECT])

    def test_alive(self):
        self.flags.discard(kalzith.DIED)
        self.assertEqual(kalzith.loot(self.gd), [])
        self.assertEqual(self.objects(PILE), [kalzith.SCROLL_OBJECT + k for k in (0, 2, 4)])

    def test_nothing_left(self):
        """All bought: nothing of his anywhere but with the party; nothing left, nothing added."""
        struct.pack_into("<Bh", self.m, THINGS + PILE * 3, 0, game.NO_ITEM)
        self.assertEqual(kalzith.loot(self.gd), [])
        self.assertIn(kalzith.LOOTED, self.flags)


class SoldOutTests(unittest.TestCase):
    """All he carries bought: no more shop (SOLD_OUT) (kalzith.sold_out)."""

    def setUp(self):
        LootTests.setUp(self)  # (his three scrolls in PILE, here the list he carries)
        self.flags = {kalzith.STOCKED}
        self.gd.region = lambda: kalzith.REGION
        self.him = game.PARTY_SIZE + 3
        rec = CREATURES + self.him * game.CREATURE_SIZE
        struct.pack_into("<h", self.m, rec, 16)
        name = kalzith.NAME.encode() + b"\0"
        self.m[rec + game.CREATURE_NAME:rec + game.CREATURE_NAME + len(name)] = name
        struct.pack_into("<hhh", self.m, rec + game.CREATURE_ITEM_LISTS[0], PILE, game.NO_ITEM, game.NO_ITEM)

    def worn(self):
        return {-struct.unpack_from("<h", rec, 0)[0]: rec[game.ITEM_SLOT]
                for _, rec in ring.Items(self.gd).chain(PILE)}

    def test_some_left(self):
        self.assertEqual(kalzith.sold_out(self.gd, True), [])
        self.assertNotIn(kalzith.SOLD_OUT, self.flags)

    def test_sold_out(self):
        struct.pack_into("<Bh", self.m, THINGS + PILE * 3, game.THING_ITEM, game.NO_ITEM)
        self.gd.talk_target = lambda: None
        self.assertEqual(kalzith.sold_out(self.gd, False), [])  # (a game loading: nothing)
        self.assertNotIn(kalzith.SOLD_OUT, self.flags)
        self.gd.talk_target = lambda: kalzith.NAME
        self.assertEqual(kalzith.sold_out(self.gd, False), [])  # (his talk or shop open: later)
        self.assertIn(kalzith.SOLD_OUT, self.flags)
        self.assertEqual(kalzith.sold_out(self.gd, True), [])
        self.assertIn(kalzith.SOLD_OUT, self.flags)

    def test_gear_left(self):
        """His scrolls all bought but his robe still on him: still a shop."""
        from dsloader import robes
        rec = bytearray(robes.item(robes.ASHEN))
        struct.pack_into("<h", rec, game.ITEM_NEXT, game.NO_ITEM)
        self.m[ITEMS + 90 * game.ITEM_SIZE:ITEMS + 91 * game.ITEM_SIZE] = rec
        struct.pack_into("<Bh", self.m, THINGS + PILE * 3, game.THING_ITEM, 90)
        self.assertEqual(kalzith.sold_out(self.gd, True), [])
        self.assertNotIn(kalzith.SOLD_OUT, self.flags)

    def test_marked_by_mistake(self):
        """Marked sold out while he still has scrolls (a game loading with another's people, or
        an earlier build's numbers): his shop back, once the map's main loop runs; an earlier
        build's scrolls count as his."""
        items = ring.Items(self.gd)
        for index, _ in list(items.chain(PILE)):  # (all three by an earlier build's numbers)
            at = items.items + index * game.ITEM_SIZE
            k = -struct.unpack_from("<h", self.m, at)[0] - kalzith.SCROLL_OBJECT
            struct.pack_into("<h", self.m, at, -(kalzith.OLD_SCROLL_OBJECT + k))
        self.flags.add(kalzith.SOLD_OUT)
        self.gd.talk_target = lambda: None
        self.assertEqual(kalzith.sold_out(self.gd, False), [])
        self.assertIn(kalzith.SOLD_OUT, self.flags)  # (not during a load)
        self.assertEqual(kalzith.sold_out(self.gd, True), [])
        self.assertNotIn(kalzith.SOLD_OUT, self.flags)

    def test_dead(self):
        struct.pack_into("<Bh", self.m, THINGS + PILE * 3, game.THING_ITEM, game.NO_ITEM)
        self.flags.add(kalzith.DIED)
        self.assertEqual(kalzith.sold_out(self.gd, True), [])
        self.assertNotIn(kalzith.SOLD_OUT, self.flags)


class LookTests(unittest.TestCase):
    def test_past_256(self):
        """Kalzith's thing in the pens is the 285th: found (the Look box's HP, AC and THAC0)."""
        thief = ThiefTests()
        thief.setUp()
        gd, m = thief.log.game, thief.log.guest.mem
        struct.pack_into("<Bh", m, THINGS + 285 * 3, 2, 33)  # (a creature, record 33)
        self.assertEqual(gd.combatant_creature(285), 33)
        self.assertIsNone(gd.combatant_creature(game.THINGS))


if __name__ == "__main__":
    unittest.main()
