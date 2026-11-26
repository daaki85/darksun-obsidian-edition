"""AD&D's class tables (tables.py), as the Player's Handbook and Dark Sun have them."""

import os
import re
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import game, tables


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
        """The sequel's: SL's to 14th, then each level a step more, to 30th (the owner's AD&D tables past 20th,
        2026-11-25); DSCLOG2's XP_FIXES AD&D's."""
        for row in tables.ROWS:
            xp = tables.RAV_XP[row]
            self.assertEqual(len(xp), 30)
            self.assertEqual(xp[:14], tables.XP[row])
            self.assertEqual(list(xp), sorted(xp))
        self.assertEqual(tables.RAV_XP["druid"][19], 5500000)
        self.assertEqual(tables.RAV_XP["psionicist"][17], 2400000)
        self.assertEqual({row: (tables.RAV_XP[row][20], tables.RAV_XP[row][29]) for row in tables.ROWS},
                         {"cleric": (2925000, 4950000), "druid": (6000000, 10500000), "fighter": (3250000, 5500000),
                          "gladiator": (3900000, 6600000), "preserver": (4125000, 7500000),
                          "psionicist": (3300000, 7000000), "ranger": (3900000, 6600000),
                          "thief": (2420000, 4400000)})
        asm = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dos",
                                "dsclog2.asm")).read()
        fixes = re.findall(r"^\s+XP_FIX (\d+), (\d+), (\d+)", asm, re.M)
        self.assertEqual(len(fixes), 20)
        for row, index, xp in fixes:
            self.assertEqual(tables.RAV_XP[tables.ROWS[int(row)]][int(index)], int(xp))

    def test_ravager_slots(self):
        """The Player's Handbook's to 20th level, the owner's to 30th; DSCLOG2's RAV_SLOTS the same."""
        self.assertEqual([tables.rav_slots(11, 20, s) for s in range(1, 10)], [5, 5, 5, 5, 5, 4, 3, 3, 2])
        self.assertEqual([tables.rav_slots(1, 20, s) for s in range(1, 10)], [9, 9, 9, 8, 7, 5, 2, 0, 0])
        self.assertEqual([tables.rav_slots(11, 25, s) for s in range(1, 10)], [5] * 9)
        self.assertEqual([tables.rav_slots(11, 30, s) for s in range(1, 10)], [7, 7, 7, 7, 7, 7, 7, 6, 6])
        self.assertEqual([tables.rav_slots(1, 21, s) for s in range(1, 8)], [9, 9, 9, 9, 8, 6, 2])
        self.assertEqual([tables.rav_slots(1, 30, s) for s in range(1, 8)], [9, 9, 9, 9, 9, 9, 8])
        self.assertEqual(tables.rav_slots(1, 35, 7), 8)
        self.assertEqual(tables.rav_slots(1, 0, 1), 0)
        self.assertIsNone(tables.rav_slots(12, 9, 1))  # (a psionicist)
        self.assertIsNone(tables.rav_slots(17, 9, 1))
        for level in range(1, 13):  # (SL's to 12th)
            for spell in range(1, 6):
                self.assertEqual(tables.rav_slots(1, level, spell), tables.slots(1, level, spell))
                self.assertEqual(tables.rav_slots(11, level, spell), tables.slots(11, level, spell))
        asm = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dos",
                                "dsclog2.asm")).read()
        body = asm[asm.index("\nrav_slots:"):]
        rows = [tuple(int(n) for n in line.split(";")[0].replace("db", "").split(","))
                for line in body.splitlines()[2:92]]
        want = [(r + (0,) * 9)[:9] for r in tables.RAV_PRIEST_SLOTS + tables.RAV_WIZARD_SLOTS
                + tables.RAV_RANGER_SLOTS]
        self.assertEqual(rows, want)
        self.assertIn("DRUID_SLOT_LEVELS equ 15", asm)  # (ADND_SLOTS: a druid's rows stop at 15th's)

    def test_ravager_druid_slots(self):
        """The owner's table (2026-11-25): a druid's slots the cleric's to 15th, then 15th's, 6 6 6 6 4 2 1."""
        for level in range(1, 16):
            for spell in range(1, 10):
                self.assertEqual(tables.rav_slots(5, level, spell), tables.rav_slots(1, level, spell))
        for cls in tables.DRUIDS:
            for level in range(15, 31):
                self.assertEqual([tables.rav_slots(cls, level, s) for s in range(1, 10)],
                                 [6, 6, 6, 6, 4, 2, 1, 0, 0])
        self.assertEqual([tables.rav_slots(1, 16, s) for s in range(1, 8)], [7, 7, 7, 6, 4, 3, 1])

    def test_ravager_ranger_slots(self):
        """A ranger's priest spells, the Player's Handbook's (the owner's table): none to 7th, 1 at 8th, 3 3 3
        from 16th; the game's formula gave more at 12th to 14th."""
        got = {level: tuple(tables.rav_slots(14, level, s) for s in (1, 2, 3)) for level in range(1, 31)}
        self.assertEqual(got[7], (0, 0, 0))
        self.assertEqual([got[level] for level in range(8, 17)],
                         [(1, 0, 0), (2, 0, 0), (2, 1, 0), (2, 2, 0), (2, 2, 1), (3, 2, 1), (3, 2, 2), (3, 3, 2),
                          (3, 3, 3)])
        self.assertEqual(got[20], (3, 3, 3))
        self.assertEqual(got[30], (3, 3, 3))
        self.assertEqual(tables.rav_slots(14, 20, 4), 0)

    def test_ravager_saves(self):
        """The Player's Handbook's Table 60 by group; DSCLOG2's SAVE_TABLE the same, a row a level 1-21."""
        self.assertEqual(tables.rav_saves(1, 9), (8, 10, 9, 9, 11))
        self.assertEqual(tables.rav_saves(1, 20), (3, 5, 4, 4, 6))
        self.assertEqual(tables.rav_saves(0, 19), (2, 6, 5, 8, 7))
        self.assertEqual(tables.rav_saves(2, 21), (8, 3, 5, 7, 4))
        self.assertEqual(tables.rav_saves(3, 13), (10, 8, 9, 13, 9))
        for group in range(4):
            for level in range(2, 30):
                self.assertTrue(all(a <= b for a, b in zip(tables.rav_saves(group, level),
                                                          tables.rav_saves(group, level - 1))))
        asm = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dos",
                                "dsclog2.asm")).read()
        body = asm[asm.index("\nsave_table:"):]
        rows = [tuple(int(n) for n in line.split(";")[0].replace("db", "").split(","))
                for line in body.splitlines()[2:2 + 4 * tables.RAV_SAVE_LEVELS]]
        self.assertEqual(rows, [tables.rav_saves(g, level) for g in range(4)
                                for level in range(1, tables.RAV_SAVE_LEVELS + 1)])

    def test_ravager_thief_table(self):
        """DSCLOG2's THIEF_TABLE: game.AD_D_THIEF, 17 levels (the owner's table, SL's to 13th)."""
        asm = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dos",
                                "dsclog2.asm")).read()
        body = asm[asm.index("\nthief_table:"):]
        rows = [tuple(int(n) for n in line.split(";")[0].replace("db", "").split(","))
                for line in body.splitlines()[2:10]]
        self.assertEqual(rows, [tuple(r) for r in game.AD_D_THIEF])
        self.assertIn("THIEF_LEVELS equ 17", asm)
        sl = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dos",
                               "dsclog.asm")).read()
        body = sl[sl.index("\nthief_table:"):]
        rows = [tuple(int(n) for n in line.split(";")[0].replace("db", "").split(","))
                for line in body.splitlines()[2:10]]
        self.assertEqual(rows, [tuple(r[:13]) for r in game.AD_D_THIEF])


if __name__ == "__main__":
    unittest.main()
