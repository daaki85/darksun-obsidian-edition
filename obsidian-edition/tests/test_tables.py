"""AD&D's class tables (tables.py), as the Player's Handbook and Dark Sun have them."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import tables


class TablesTests(unittest.TestCase):
    def test_xp(self):
        self.assertEqual(tables.xp_needed("gladiator", 1), 2250)
        self.assertEqual(tables.xp_needed("ranger", 1), 2250)
        self.assertEqual(tables.xp_needed("thief", 1), 1250)
        self.assertEqual(tables.xp_needed("preserver", 9), 250000)
        self.assertEqual(tables.xp_needed("cleric", 10), 675000)
        self.assertEqual(tables.xp_needed("thief", 12), 660000)
        self.assertEqual(tables.xp_needed("druid", 12), 750000)
        self.assertIsNone(tables.xp_needed("fighter", 14))
        for row in tables.ROWS:
            xp = tables.XP[row]
            self.assertEqual(len(xp), 14)
            self.assertEqual(list(xp), sorted(xp))

    def test_xp_share(self):
        """The XP cap's share (DSCLOG's LEVEL_ROOM; test_dsclog's test_level_room_is_the_xp_share
        runs both): all of it for one class, divided for several, less the old classes' for a human."""
        cap = 749_999
        self.assertEqual(tables.xp_share((9, 0, 0), (12, 0, 0), False, cap), cap)
        self.assertEqual(tables.xp_share((9, 17, 0), (8, 9, 0), False, cap), 374_999)
        self.assertEqual(tables.xp_share((9, 17, 11), (8, 9, 8), False, cap), 249_999)
        self.assertEqual(tables.xp_share((0, 0, 0), (0, 0, 0), False, cap), cap)
        self.assertEqual(tables.xp_share((9, 0, 0), (12, 0, 0), True, cap), cap)  # (never changed class)
        self.assertEqual(tables.xp_share((17, 9, 0), (1, 7, 0), True, cap), cap - 64_000)  # (fighter 7th)
        self.assertEqual(tables.xp_share((11, 17, 13), (1, 9, 5), True, cap), cap - 110_000 - 18_000)
        self.assertEqual(tables.xp_share((11, 1, 0), (1, 10, 0), True, cap), cap - 450_000)  # (cleric 10th)
        self.assertEqual(tables.xp_share((11, 5, 9), (1, 13, 12), True, cap), 0)  # (more than all of it)
        self.assertEqual(tables.xp_share((11, 9, 0), (1, 15, 0), True, cap), 0)  # (past the tables)
        self.assertEqual(sorted(tables.CLASS_ROWS), list(range(1, 18)))

    def test_slots(self):
        self.assertEqual([tables.slots(1, 5, s) for s in range(1, 6)], [3, 3, 1, 0, 0])  # cleric
        self.assertEqual([tables.slots(6, 9, s) for s in range(1, 6)], [4, 4, 3, 2, 1])  # druid
        self.assertEqual([tables.slots(11, 5, s) for s in range(1, 6)], [4, 2, 1, 0, 0])  # preserver
        self.assertEqual([tables.slots(5, 12, s) for s in range(1, 6)], [6, 5, 5, 3, 2])  # druid 12th
        self.assertEqual(tables.slots(11, 14, 5), 4)  # (12th's past it)
        self.assertEqual(tables.slots(1, 0, 1), 0)
        self.assertEqual(tables.slots(1, 3, 6), 0)
        for cls in (9, 13, 17):  # fighter, ranger, thief: the game's
            self.assertIsNone(tables.slots(cls, 9, 1))

    def test_priest_thac0(self):
        self.assertEqual([tables.priest_thac0(level) for level in range(1, 11)],
                         [20, 20, 20, 18, 18, 18, 16, 16, 16, 14])


if __name__ == "__main__":
    unittest.main()
