"""Ages from Dark Sun's tables (aging.py): the starting roll, the categories' changes, old age."""

import os
import random
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import aging, game, kalzith  # noqa: E402
from test_dicelog import CREATURES, DS, SHEETS, set_effects  # noqa: E402

FLAGS_AT = 0x58000  # (the fake game's flags: a place nothing else uses)
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
        """A starting age for the member with none, Table 7's dice rolled, the roll kept on the sheet
        (its true age: start_age) and in the line; then none again."""
        lines = aging.give_ages(self.g, random.Random(5))
        self.assertEqual(len(lines), 1)
        age = aging.age_of(self.g.sheet(0))
        self.assertTrue(16 <= age <= 23)
        self.assertEqual((game.sheet_roll(self.g.sheet(0)), aging.start_age(self.g.sheet(0), "Dag")), (age - 16, age))
        self.assertIn(f"Dag is {age} (a human: 15 + 1d8 = [{age - 15}]); middle-aged at 40.", lines)
        self.assertEqual(aging.give_ages(self.g), [])

    def test_an_age_from_before_keeps_its_start(self):
        """A member given an age before the roll was kept (2.13's layout): its age as it is, its
        roll put in from the name's (natural_start), silently; the true age the same as before."""
        start = aging.natural_start("Dag", HUMAN)[0]
        five = (1 | 0x800000).to_bytes(3, "little") + bytes((aging.stored(HUMAN, start + 4),))
        self.m[SHEETS + game.SPEC_SLOTS:SHEETS + game.SPEC_SLOTS + 4] = five
        self.assertEqual(aging.start_age(self.g.sheet(0), "Dag"), start)
        self.assertEqual(aging.give_ages(self.g), [])
        sheet = self.g.sheet(0)
        self.assertEqual((aging.age_of(sheet), game.sheet_roll(sheet), aging.start_age(sheet, "Dag"), game.spec_kinds(sheet)),
                         (start + 4, start - 16, start, bytes((1, 0, 0, 0))))

    def test_true_age_from_the_roll(self):
        """Restore Youth's floor from the roll on the sheet, however many years magic added."""
        self.m[SHEETS + game.SPEC_SLOTS:SHEETS + game.SPEC_SLOTS + 4] = game.packed_specs((), aging.stored(HUMAN, 61), 2)
        self.m[CREATURES + game.CREATURE_ABILITIES + 2] = 18
        self.assertEqual(aging.start_age(self.g.sheet(0), "Dag"), 18)
        lines = aging.restore(self.g, 0, 50, random.Random(1))
        self.assertIn("now 18", lines[-1])

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

    def test_scores_never_cut_the_wrong_way(self):
        """A score past 25 (magic) keeps it when middle age adds 1; a thri-kreen made young again
        is no longer venerable (it has no middle age)."""
        self.m[SHEETS + game.SPEC_SLOTS:SHEETS + game.SPEC_SLOTS + 4] = game.packed_specs((), aging.stored(HUMAN, 39))
        self.m[CREATURES + game.CREATURE_ABILITIES + 3] = 26
        aging.age_by(self.g, 0, 1, "Haste")
        self.assertEqual(self.m[CREATURES + game.CREATURE_ABILITIES + 3], 26)
        self.m[SHEETS + game.SHEET_RACE] = THRI_KREEN
        self.m[SHEETS + game.SPEC_SLOTS:SHEETS + game.SPEC_SLOTS + 4] = game.packed_specs((), aging.stored(THRI_KREEN, 25))
        lines = aging.age_by(self.g, 0, -3, "Restore Youth")
        self.assertIn("no longer venerable: STR +1, DEX +1", lines[0])

    def test_natural_years(self):
        """A year of age for each 365 days of the game's clock, put in the stored age as it passes;
        a year across middle age changes the scores as Haste's would; the dead don't age."""
        self.m[SHEETS + game.SPEC_SLOTS:SHEETS + game.SPEC_SLOTS + 4] = game.packed_specs((), aging.stored(HUMAN, 39))
        self.g.game_time = lambda: aging.YEAR * 2 - 1
        self.assertEqual(aging.natural_years(self.g), 1)
        before = self.scores()
        lines = aging.natural_tick(self.g, 1)
        self.assertEqual(lines, ["A year has passed: Dag is 40, middle-aged: STR -1, CON -1, INT +1, WIS +1."])
        self.assertEqual(self.scores()[0][0], before[0][0] - 1)
        self.assertEqual(aging.age_of(self.g.sheet(0)), 40)  # (in the save with the scores)
        self.m[CREATURES + game.CREATURE_STATUS] = kalzith.DEAD_STATUS[1]
        self.assertEqual(aging.natural_tick(self.g, 1), [])
        self.assertEqual(aging.age_of(self.g.sheet(0)), 40)

    def test_restore_counts_the_games_years(self):
        """Restore Youth takes back magic's years only: the game's years are part of the true age;
        at it, nothing to take back and no line of 0 years."""
        start = aging.natural_start("Dag", HUMAN)[0]
        self.g.game_time = lambda: aging.YEAR * 3
        self.m[SHEETS + game.SPEC_SLOTS:SHEETS + game.SPEC_SLOTS + 4] = game.packed_specs((), aging.stored(HUMAN, start + 5))
        self.m[CREATURES + game.CREATURE_ABILITIES + 2] = 18
        lines = aging.restore(self.g, 0, 12, random.Random(1))
        self.assertIn(f"now {start + 3}", lines[-1])
        self.assertIn("no magical years", aging.restore(self.g, 0, 12, random.Random(1))[0])
        self.m[SHEETS + game.SPEC_SLOTS:SHEETS + game.SPEC_SLOTS + 4] = game.packed_specs((), aging.stored(HUMAN, 15))
        self.assertEqual(aging.age_by(self.g, 0, -1, "Restore Youth"), [])  # (the race's base: no "0 years")

    def flags(self):
        """The game's flags at FLAGS_AT, as a save keeps them (game.FLAGS_PTR)."""
        self.m[DS * 16 + game.FLAGS_PTR:DS * 16 + game.FLAGS_PTR + 4] = struct.pack("<HH", FLAGS_AT & 0xF, FLAGS_AT >> 4)
        return FLAGS_AT

    def test_the_log_counts_each_year_once(self):
        """The dice log's look: a year passed, each a year older once, the count kept in the game's
        flags; a game saved before the count begins it there; nothing while the flags have no place;
        each step only once two looks agree on it."""
        self.m[SHEETS + game.SPEC_SLOTS:SHEETS + game.SPEC_SLOTS + 4] = game.packed_specs((), aging.stored(HUMAN, 20))
        clock = [aging.YEAR - 3600]
        self.g.game_time = lambda: clock[0]
        self.assertEqual(self.log._natural_aging(), [])  # (no flags in memory: waits)
        self.flags()
        self.assertEqual(self.log._natural_aging(), [])  # (the first look with them: seen once)
        self.assertIsNone(aging.counted_years(self.g))
        self.assertEqual(self.log._natural_aging(), [])  # (seen twice: the count begun, 0 years)
        self.assertEqual(aging.counted_years(self.g), 0)
        clock[0] = aging.YEAR + 60
        self.assertEqual([self.log._natural_aging() for _ in range(4)],
                         [[], ["A year has passed: Dag is 21."], [], []])
        self.assertEqual(aging.counted_years(self.g), 1)

    def test_a_long_jump_waits_and_loses_nothing(self):
        """Two years passed in one jump of the clock (more than NATURAL_JUMP: maybe a game being
        loaded): nothing on that look, both years on the next steady one."""
        self.m[SHEETS + game.SPEC_SLOTS:SHEETS + game.SPEC_SLOTS + 4] = game.packed_specs((), aging.stored(HUMAN, 20))
        self.flags()
        clock = [aging.YEAR - 3600]
        self.g.game_time = lambda: clock[0]
        for _ in range(3):  # (the count begun)
            self.log._natural_aging()
        clock[0] = aging.YEAR * 2 + 60
        self.assertEqual(self.log._natural_aging(), [])
        clock[0] += 60
        self.assertEqual(self.log._natural_aging(), ["A year has passed: Dag is 22."])
        self.assertEqual(aging.age_of(self.g.sheet(0)), 22)

    def test_a_load_caught_halfway_ages_no_one(self):
        """A save from a year before loaded, the look catching its flags (its lower count) with the
        old clock still there: not acted on, as the next look finds the clock moved too; the
        save's own count and clock then agree, and no one is older."""
        self.m[SHEETS + game.SPEC_SLOTS:SHEETS + game.SPEC_SLOTS + 4] = game.packed_specs((), aging.stored(HUMAN, 23))
        self.flags()
        aging.set_counted(self.g, 3)
        clock = [aging.YEAR * 3 + 100]
        self.g.game_time = lambda: clock[0]
        for _ in range(2):
            self.assertEqual(self.log._natural_aging(), [])
        aging.set_counted(self.g, 1)  # (the save's flags in, its clock not yet)
        self.assertEqual(self.log._natural_aging(), [])
        clock[0] = aging.YEAR + 50  # (its clock)
        self.assertEqual([self.log._natural_aging() for _ in range(3)], [[], [], []])
        self.assertEqual((aging.counted_years(self.g), aging.age_of(self.g.sheet(0))), (1, 23))

    def test_a_save_is_as_old_as_its_count(self):
        """A save loaded: its flags hold its own count, so its years are neither counted again nor
        lost; one whose count is past its clock (an edited save) is mended, aging no one."""
        self.m[SHEETS + game.SPEC_SLOTS:SHEETS + game.SPEC_SLOTS + 4] = game.packed_specs((), aging.stored(HUMAN, 23))
        self.flags()
        aging.set_counted(self.g, 3)
        self.assertEqual(aging.natural_years_due(self.g, 3), [])
        self.assertEqual(aging.natural_years_due(self.g, 1), [])
        self.assertEqual(aging.counted_years(self.g), 1)
        self.assertEqual(aging.age_of(self.g.sheet(0)), 23)

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


class Fixed(random.Random):
    """A d100 that comes up ROLL."""

    def __init__(self, roll):
        super().__init__(0)
        self.roll = roll

    def randint(self, a, b):
        return self.roll


class HasteTests(unittest.TestCase):
    def setUp(self):
        self.log = dag()
        self.g = self.log.game
        self.m = self.log.guest.mem
        self.m[SHEETS + game.SHEET_RACE] = HUMAN
        self.m[SHEETS + game.SPEC_SLOTS:SHEETS + game.SPEC_SLOTS + 4] = game.packed_specs((), aging.stored(HUMAN, 39))
        self.m[CREATURES + game.CREATURE_ABILITIES:CREATURES + game.CREATURE_ABILITIES + 6] = bytes((18, 15, 13, 12, 11, 10))
        self.m[SHEETS + game.SHEET_ABILITIES:SHEETS + game.SHEET_ABILITIES + 6] = bytes((18, 15, 13, 12, 11, 10))
        struct.pack_into("<h", self.m, CREATURES, 30)
        self.log.rules |= game.RULE_AGING

    def test_system_shock_table(self):
        self.assertEqual([aging.system_shock(c) for c in (1, 13, 14, 18, 24, 25, 30)], [25, 85, 88, 99, 99, 100, 100])

    def test_survives_and_ages(self):
        """A roll at or under the chance (CON 13: 85): a year older, the categories' changes."""
        lines = aging.hasted(self.g, 0, Fixed(85))
        self.assertEqual(lines, ["Dag's system shock (Haste's aging): d100 = 85, needs 85 or less (CON 13) -> survives",
                                 "  Dag ages 1 year (Haste): now 40, middle-aged: STR -1, CON -1, INT +1, WIS +1."])
        self.assertEqual(aging.age_of(self.g.sheet(0)), 40)

    def test_fails_and_dies(self):
        lines = aging.hasted(self.g, 0, Fixed(86))
        self.assertEqual(lines, ["Dag's system shock (Haste's aging): d100 = 86, needs 85 or less (CON 13) -> fails: Dag dies"])
        self.assertEqual(self.m[CREATURES + game.CREATURE_STATUS], 5)
        self.assertEqual(aging.age_of(self.g.sheet(0)), 39)
        self.assertEqual(aging.hasted(self.g, 0, Fixed(1)), [])  # (dead: nothing more)

    def test_in_the_dice_log(self):
        """A new Haste on Dag, once: its line, then his system shock and his year; none again for
        the same Haste, nor with the rule off."""
        self.assertEqual(self.log.effect_changes(10.0), [])
        set_effects(self.log, [(0, 0, game.HASTED_EFFECT)])
        lines = self.log.effect_changes(20.0)
        self.assertTrue(lines[0].startswith("Hasted on Dag"))
        self.assertTrue(lines[1].startswith("Dag's system shock (Haste's aging): d100 = "))
        self.assertEqual(self.log.effect_changes(30.0), [])
        set_effects(self.log, [])
        self.log.effect_changes(40.0)
        self.log.rules &= ~game.RULE_AGING
        set_effects(self.log, [(0, 0, game.HASTED_EFFECT)])
        self.assertEqual(len(self.log.effect_changes(50.0)), 1)


class RestoreYouthTests(unittest.TestCase):
    def setUp(self):
        self.log = dag()
        self.g = self.log.game
        self.m = self.log.guest.mem
        self.m[SHEETS + game.SHEET_RACE] = HUMAN
        self.true = aging.natural_start("Dag", HUMAN)[0]
        self.m[CREATURES + game.CREATURE_ABILITIES:CREATURES + game.CREATURE_ABILITIES + 6] = bytes((18, 15, 13, 12, 11, 10))
        struct.pack_into("<h", self.m, CREATURES, 30)

    def aged(self, years):
        self.m[SHEETS + game.SPEC_SLOTS:SHEETS + game.SPEC_SLOTS + 4] = game.packed_specs((), aging.stored(HUMAN, self.true + years))

    def test_takes_back_a_year_a_level(self):
        self.aged(12)
        lines = aging.restore(self.g, 0, 9, Fixed(1))
        self.assertTrue(lines[0].startswith("Dag's system shock (Restore Youth): d100 = 1, needs 85 or less (CON 13) -> survives"))
        self.assertEqual(lines[1], f"  Dag grows younger 9 years (Restore Youth): now {self.true + 3}.")
        self.assertEqual(aging.age_of(self.g.sheet(0)), self.true + 3)

    def test_never_below_the_true_age(self):
        self.aged(2)
        aging.restore(self.g, 0, 9, Fixed(1))
        self.assertEqual(aging.age_of(self.g.sheet(0)), self.true)
        self.assertEqual(aging.restore(self.g, 0, 9, Fixed(1)),
                         [f"Restore Youth: Dag has no magical years to take back ({self.true}, Dag's true age)."])

    def test_system_shock_kills(self):
        self.aged(5)
        lines = aging.restore(self.g, 0, 9, Fixed(86))
        self.assertTrue(lines[0].endswith("-> fails: Dag dies"))
        self.assertEqual(self.m[CREATURES + game.CREATURE_STATUS], 5)

    def test_spell(self):
        """Restore Youth is the 6th-level priest spells' tenth (211), the cosmos's."""
        self.assertEqual(game.PRIEST6_SPELLS[game.RESTORE_YOUTH_SPELL], "Restore Youth")
        self.assertEqual(game.RESTORE_YOUTH_SPELL, 211)
        self.assertEqual(game.PRIEST6_MASKS[game.RESTORE_YOUTH_SPELL], game.COSMOS_MASK)


if __name__ == "__main__":
    unittest.main()
