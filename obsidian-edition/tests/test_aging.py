"""Ages from Dark Sun's tables (aging.py): the starting roll, the categories' changes, old age."""

import os
import random
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import aging, game  # noqa: E402
from test_dicelog import CREATURES, SHEETS  # noqa: E402
from test_now import dag  # noqa: E402

HUMAN, DWARF, MUL, THRI_KREEN = 1, 2, 7, 8


class TableTests(unittest.TestCase):
    def test_categories(self):
        """Table 8: a human middle-aged at 40, old at 53, venerable at 80; a thri-kreen only
        venerable, at 25."""
        self.assertEqual([aging.category(HUMAN, a) for a in (39, 40, 52, 53, 79, 80)],
                         [aging.YOUNG, aging.MIDDLE, aging.MIDDLE, aging.OLD, aging.OLD, aging.VENERABLE])
        self.assertEqual([aging.category(THRI_KREEN, a) for a in (6, 24, 25)],
                         [aging.YOUNG, aging.YOUNG, aging.VENERABLE])
        self.assertEqual(aging.next_category(HUMAN, 20), (aging.MIDDLE, 40))
        self.assertEqual(aging.next_category(THRI_KREEN, 14), (aging.VENERABLE, 25))
        self.assertIsNone(aging.next_category(HUMAN, 80))

    def test_changes_add_up(self):
        """Each category reached once: middle -1 STR and CON, +1 INT and WIS; old -2 STR and DEX,
        -1 CON, +1 WIS; venerable -1 STR, DEX and CON, +1 INT and WIS. Younger again undoes them;
        a thri-kreen's venerable age only -1 STR and DEX."""
        S, D, C, I, W = aging.STR, aging.DEX, aging.CON, aging.INT, aging.WIS
        self.assertEqual(aging.changes(HUMAN, 39, 40), {S: -1, C: -1, I: 1, W: 1})
        self.assertEqual(aging.changes(HUMAN, 30, 80), {S: -4, D: -3, C: -3, I: 2, W: 3})
        self.assertEqual(aging.changes(HUMAN, 80, 30), {S: 4, D: 3, C: 3, I: -2, W: -3})
        self.assertEqual(aging.changes(HUMAN, 41, 52), {})
        self.assertEqual(aging.changes(THRI_KREEN, 24, 25), {S: -1, D: -1})

    def test_start_and_most(self):
        """Table 7's starting ages (a thri-kreen always 6), and a maximum age the same each time
        for the same character, within its race's range."""
        rng = random.Random(1)
        for _ in range(200):
            self.assertTrue(16 <= aging.roll_start(HUMAN, rng)[0] <= 23)
            self.assertTrue(29 <= aging.roll_start(DWARF, rng)[0] <= 49)
        self.assertEqual(aging.roll_start(THRI_KREEN, rng), (6, []))
        most = aging.most_age("K'ratchek", THRI_KREEN)
        self.assertTrue(26 <= most <= 35)
        self.assertEqual(aging.most_age("K'ratchek", THRI_KREEN), most)

    def test_stored(self):
        """+17h: the age less the race's base, plus 1 (0 none); a dwarf's most fits."""
        self.assertEqual(aging.stored(THRI_KREEN, 6), 1)
        self.assertEqual(aging.stored(DWARF, 260), 236)
        sheet = bytearray(game.SHEET_SIZE)
        sheet[game.SHEET_RACE] = MUL
        self.assertIsNone(aging.age_of(bytes(sheet)))
        sheet[game.SPEC_SLOTS:game.SPEC_SLOTS + 4] = game.packed_specs((), aging.stored(MUL, 19))
        self.assertEqual(aging.age_of(bytes(sheet)), 19)


class PartyTests(unittest.TestCase):
    def setUp(self):
        self.log = dag()
        self.g = self.log.game
        self.m = self.log.guest.mem
        self.m[SHEETS + game.SHEET_RACE] = HUMAN
        self.m[SHEETS + game.SHEET_ABILITIES:SHEETS + game.SHEET_ABILITIES + 6] = bytes((17, 15, 16, 12, 11, 10))
        self.m[CREATURES + game.CREATURE_ABILITIES:CREATURES + game.CREATURE_ABILITIES + 6] = bytes((18, 15, 16, 12, 11, 10))
        self.log.rules |= game.RULE_AGING

    def scores(self):
        return list(self.m[SHEETS + game.SHEET_ABILITIES:SHEETS + game.SHEET_ABILITIES + 6]), \
            list(self.m[CREATURES + game.CREATURE_ABILITIES:CREATURES + game.CREATURE_ABILITIES + 6])

    def test_give_ages_once(self):
        """A starting age for the member with none, its roll in the line; then none again."""
        lines = aging.give_ages(self.g, random.Random(4))
        self.assertEqual(len(lines), 1)
        age = aging.age_of(self.g.sheet(0))
        self.assertTrue(16 <= age <= 23)
        self.assertIn(f"Dag is {age} (a human: 15 + 1d8 = [{age - 15}]); middle-aged at 40.", lines)
        self.assertEqual(aging.give_ages(self.g, random.Random(4)), [])

    def test_age_by_changes_the_scores(self):
        """Aged past middle age: the sheet's scores and the creature's both change; younger again,
        back as they were."""
        self.m[SHEETS + game.SPEC_SLOTS:SHEETS + game.SPEC_SLOTS + 4] = game.packed_specs((), aging.stored(HUMAN, 38))
        before = self.scores()
        lines = aging.age_by(self.g, 0, 3, "Haste")
        self.assertEqual(lines, ["Dag ages 3 years (Haste): now 41, middle-aged: STR -1, CON -1, INT +1, WIS +1."])
        sheet, creature = self.scores()
        self.assertEqual(sheet[0], before[0][0] - 1)
        self.assertEqual(creature[2], before[1][2] - 1)
        aging.age_by(self.g, 0, -3, "Restore Youth")
        self.assertEqual(self.scores(), before)
        self.assertEqual(aging.age_of(self.g.sheet(0)), 38)

    def test_death_at_the_most(self):
        """Reaching the most its race lives, the member dies: no hit points, dead."""
        most = aging.most_age("Dag", HUMAN)
        self.m[SHEETS + game.SPEC_SLOTS:SHEETS + game.SPEC_SLOTS + 4] = game.packed_specs((), aging.stored(HUMAN, most - 1))
        lines = aging.age_by(self.g, 0, 1, "Haste")
        self.assertIn("Dag dies of old age", lines[0])
        self.assertEqual(struct.unpack_from("<h", self.m, CREATURES)[0], 0)
        self.assertEqual(self.m[CREATURES + game.CREATURE_STATUS], 5)

    def test_in_stats(self):
        """STATS' age bytes (DSCLOG's AGE_TEXT): the age, its category, the next and its age."""
        self.m[SHEETS + game.SPEC_SLOTS:SHEETS + game.SPEC_SLOTS + 4] = game.packed_specs((), aging.stored(HUMAN, 45))
        self.assertEqual(struct.unpack_from("<HBBH", self.log.stats_entry(0), 28), (45, aging.MIDDLE, aging.OLD, 53))
        self.log.rules &= ~game.RULE_AGING
        self.assertEqual(self.log.stats_entry(0)[28:34], bytes(6))
        self.assertEqual(aging.describe(self.g.sheet(0)), "45, middle-aged; old at 53")


if __name__ == "__main__":
    unittest.main()
