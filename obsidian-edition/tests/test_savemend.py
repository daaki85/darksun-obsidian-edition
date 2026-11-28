"""The party's saves worked out again at a load (savemend.py), in both games' layouts: the game's routine
as the plays saw it put the saves, and mend putting them in a loaded party's sheets."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import game, ravlog, savemend  # noqa: E402

HUMAN, DWARF, ELF, HALF_GIANT, THRI_KREEN = 1, 2, 3, 5, 8
CLERIC, FIGHTER, GLADIATOR, PRESERVER, PSIONICIST, THIEF = 1, 9, 10, 11, 12, 17


def sheet(race, classes, levels, saves=(99,) * 5):
    s = bytearray(game.SHEET_SIZE)
    s[game.SHEET_RACE] = race
    s[game.SHEET_CLASSES:game.SHEET_CLASSES + 3] = bytes(list(classes) + [0] * (3 - len(classes)))
    s[game.SHEET_LEVELS:game.SHEET_LEVELS + 3] = bytes(list(levels) + [0] * (3 - len(levels)))
    s[game.SHEET_SAVES:game.SHEET_SAVES + 5] = bytes(saves)
    return s


class Guest:
    def __init__(self):
        self.mem = bytearray(0x40000)

    def read(self, at, n):
        return bytes(self.mem[at:at + n])

    def write(self, at, data):
        self.mem[at:at + len(data)] = data


class FakeGame:
    """Four creatures and their sheets (sheet N the creature's), the far pointers at DS 0."""
    SHEETS, CREATURES = 0x10000, 0x20000

    def __init__(self, members):
        self.guest, self.ds = Guest(), 0
        for ptr, at in ((game.SHEETS_PTR, self.SHEETS), (game.CREATURES_PTR, self.CREATURES)):
            self.guest.write(ptr, (at & 0xF).to_bytes(2, "little") + (at >> 4).to_bytes(2, "little"))
        self.names = []
        for m, (name, con, s) in enumerate(members):
            rec = bytearray(game.CREATURE_SIZE)
            rec[game.CREATURE_NAME] = 1
            rec[game.CREATURE_SHEET_INDEX] = m
            rec[game.CREATURE_ABILITIES + 2] = con
            self.guest.write(self.CREATURES + m * game.CREATURE_SIZE, rec)
            self.guest.write(self.SHEETS + m * game.SHEET_SIZE, s)
            self.names.append(name)

    def creature(self, m):
        return self.guest.read(self.CREATURES + m * game.CREATURE_SIZE, game.CREATURE_SIZE) \
            if m < len(self.names) else b""

    def sheet(self, m):
        return self.guest.read(self.SHEETS + m * game.SHEET_SIZE, game.SHEET_SIZE)

    def creature_name(self, m):
        return self.names[m]

    def saves(self, m):
        return list(self.sheet(m)[game.SHEET_SAVES:game.SHEET_SAVES + 5])


class RoutineTests(unittest.TestCase):
    layouts = (("Shattered Lands", lambda: None, lambda: None),
               ("Wake of the Ravager", ravlog.apply_layout, ravlog.restore_layout))

    def each_layout(self, check):
        for name, apply, restore in self.layouts:
            with self.subTest(name):
                apply()
                try:
                    check()
                finally:
                    restore()

    def test_as_the_game_put_them(self):
        """The game's routine with SAVE_BASE, as plays saw it: the 2026-11-25 level cap's (Ar'Anda, an elf
        fighter/cleric/thief 15/16/18, 4/6/5/4/7; Terrannus, a human fighter 19th after a cleric 20th,
        2/5/4/4/6; Thy'rokh, a thri-kreen thief 10th, 11/10/10/14/11) and the 2026-11-28 new 7th-level
        human fighter's 10/12/11/12/13."""
        def check():
            for race, classes, levels, want in (
                    (ELF, (FIGHTER, CLERIC, THIEF), (15, 16, 18), [4, 6, 5, 4, 7]),
                    (HUMAN, (CLERIC, FIGHTER), (20, 19), [2, 5, 4, 4, 6]),
                    (THRI_KREEN, (THIEF,), (10,), [11, 10, 10, 14, 11]),
                    (HUMAN, (FIGHTER,), (7,), [10, 12, 11, 12, 13])):
                self.assertEqual(list(savemend.routine_saves(sheet(race, classes, levels), 15)), want)
        self.each_layout(check)

    def test_rogues_and_race(self):
        """A psionicist/thief the better of each class's; a dwarf's CON off the warriors' alone, 2 at least."""
        def check():
            self.assertEqual(list(savemend.routine_saves(sheet(ELF, (PRESERVER, PSIONICIST, THIEF), (6, 6, 7)), 17)),
                             [12, 9, 9, 13, 10])
            self.assertEqual(list(savemend.routine_saves(sheet(DWARF, (FIGHTER,), (7,)), 18)), [5, 7, 6, 7, 8])
            self.assertEqual(list(savemend.routine_saves(sheet(DWARF, (CLERIC,), (7,)), 18)), [7, 11, 10, 13, 12])
            self.assertEqual(list(savemend.routine_saves(sheet(DWARF, (FIGHTER,), (17,)), 18)), [2, 2, 2, 2, 2])
            self.assertIsNone(savemend.routine_saves(sheet(HUMAN, (), ()), 15))
        self.each_layout(check)


class MendTests(unittest.TestCase):
    def test_a_loaded_party(self):
        """The sequel's party as 2026-11-28's save had it: a new fighter's nonsense (81/2/235/0/208) put
        right, the game's own old table's numbers (a gladiator's 11/12/11/13/13) made the Handbook's, one
        already right left alone; a line for each changed."""
        ravlog.apply_layout()
        try:
            gd = FakeGame([("Kel", 15, sheet(HUMAN, (FIGHTER,), (7,), (81, 2, 235, 0, 208))),
                           ("Gorr", 22, sheet(HALF_GIANT, (GLADIATOR,), (7,), (11, 12, 11, 13, 13))),
                           ("Ana", 15, sheet(HUMAN, (FIGHTER,), (7,), (10, 12, 11, 12, 13)))])
            lines = savemend.mend(gd)
            self.assertEqual([gd.saves(m) for m in range(3)], [[10, 12, 11, 12, 13]] * 3)
            self.assertEqual(lines, ["Kel's saving throws worked out again: PPD 81 to 10, RSW 2 to 12, PP 235 to 11, "
                                     "BW 0 to 12, SP 208 to 13.",
                                     "Gorr's saving throws worked out again: PPD 11 to 10, BW 13 to 12."])
            self.assertEqual(savemend.mend(gd), [])
            self.assertEqual(len(savemend.save_ranges(gd)), 3)
        finally:
            ravlog.restore_layout()

    def test_shattered_lands(self):
        gd = FakeGame([("Dwarf", 18, sheet(DWARF, (FIGHTER,), (13,), (254, 0, 255, 255, 1)))])
        self.assertEqual(len(savemend.mend(gd)), 1)
        self.assertEqual(gd.saves(0), [2, 2, 2, 2, 3])


if __name__ == "__main__":
    unittest.main()
