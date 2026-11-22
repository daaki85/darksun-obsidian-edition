"""AD&D's class tables (tables.py), as the Player's Handbook and Dark Sun have them."""

import os
import re
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

    def test_ravager_xp(self):
        """The sequel's: SL's to 14th, then each level a step more; DSCLOG2's XP_FIXES AD&D's."""
        for row in tables.ROWS:
            xp = tables.RAV_XP[row]
            self.assertEqual(len(xp), 20)
            self.assertEqual(xp[:14], tables.XP[row])
            self.assertEqual(list(xp), sorted(xp))
        self.assertEqual(tables.RAV_XP["druid"][19], 5500000)
        self.assertEqual(tables.RAV_XP["psionicist"][17], 2400000)
        asm = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dos",
                                "dsclog2.asm")).read()
        fixes = re.findall(r"^\s+XP_FIX (\d+), (\d+), (\d+)", asm, re.M)
        self.assertEqual(len(fixes), 20)
        for row, index, xp in fixes:
            self.assertEqual(tables.RAV_XP[tables.ROWS[int(row)]][int(index)], int(xp))

    def test_ravager_slots(self):
        """The Player's Handbook's to 20th level; DSCLOG2's RAV_SLOTS the same."""
        self.assertEqual([tables.rav_slots(11, 20, s) for s in range(1, 10)], [5, 5, 5, 5, 5, 4, 3, 3, 2])
        self.assertEqual([tables.rav_slots(1, 20, s) for s in range(1, 10)], [9, 9, 9, 8, 7, 5, 2, 0, 0])
        self.assertEqual(tables.rav_slots(5, 25, 1), 9)
        self.assertEqual(tables.rav_slots(1, 0, 1), 0)
        self.assertIsNone(tables.rav_slots(13, 9, 1))
        for level in range(1, 13):  # (SL's to 12th)
            for spell in range(1, 6):
                self.assertEqual(tables.rav_slots(1, level, spell), tables.slots(1, level, spell))
                self.assertEqual(tables.rav_slots(11, level, spell), tables.slots(11, level, spell))
        asm = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dos",
                                "dsclog2.asm")).read()
        body = asm[asm.index("\nrav_slots:"):]
        rows = [tuple(int(n) for n in line.split(";")[0].replace("db", "").split(","))
                for line in body.splitlines()[2:42]]
        want = [(r + (0,) * 9)[:9] for r in tables.RAV_PRIEST_SLOTS + tables.RAV_WIZARD_SLOTS]
        self.assertEqual(rows, want)


if __name__ == "__main__":
    unittest.main()
