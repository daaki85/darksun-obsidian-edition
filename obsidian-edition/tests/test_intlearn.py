import unittest

from dsloader import intlearn


class IntLearnTests(unittest.TestCase):
    def test_table(self):
        """AD&D's table for INT: the chance to learn a spell, the most spells a level (None: all)."""
        self.assertEqual([intlearn.chance(i) for i in range(9, 26)],
                         [35, 40, 45, 50, 55, 60, 65, 70, 75, 85, 95, 96, 97, 98, 99, 100, 100])
        self.assertEqual([intlearn.most(i) for i in range(9, 20)], [6, 7, 7, 7, 9, 9, 11, 11, 14, 18, None])
        self.assertEqual((intlearn.chance(5), intlearn.most(5), intlearn.chance(30)), (35, 6, 100))

    def test_lines(self):
        self.assertEqual(intlearn.line("Dreamwalker", "Magic Missile", 9, 35, 43, intlearn.FAILED, 1),
                         "Dreamwalker reads the scroll of Magic Missile: d100 = 43, needs 35 or less (INT 9) -> "
                         "not learnt (the scroll is used up)")
        self.assertEqual(intlearn.line("Dreamwalker", "Magic Missile", 19, 95, 44, intlearn.LEARNT, 1),
                         "Dreamwalker reads the scroll of Magic Missile: d100 = 44, needs 95 or less (INT 19) -> learnt")
        self.assertEqual(intlearn.line("Dreamwalker", "Fireball", 9, 35, 6, intlearn.FULL, 3),
                         "Dreamwalker can't learn Fireball from the scroll: knows 6 3rd-level spells, the most for "
                         "INT 9 (the scroll is kept)")


    def test_shinobi_lines(self):
        """A Shinobi's: read languages first, then INT's d100 (none with the rule for INT off)."""
        line = lambda rate, roll, result, read, read_rate: intlearn.line("Kage", "Blur", 12, rate, roll, result, 2,
                                                                          read, read_rate)
        self.assertEqual(line(50, 0, intlearn.UNREAD, 61, 30),
                         "Kage reads the scroll of Blur: read languages d100 = 61, needs 30 or less -> "
                         "can't read it (the scroll is used up)")
        self.assertEqual(line(50, 20, intlearn.LEARNT, 12, 30),
                         "Kage reads the scroll of Blur: read languages d100 = 12, needs 30 or less -> read; "
                         "d100 = 20, needs 50 or less (INT 12) -> learnt")
        self.assertEqual(line(50, 77, intlearn.FAILED, 12, 30),
                         "Kage reads the scroll of Blur: read languages d100 = 12, needs 30 or less -> read; "
                         "d100 = 77, needs 50 or less (INT 12) -> not learnt (the scroll is used up)")
        self.assertEqual(line(0, 0, intlearn.LEARNT, 12, 30),
                         "Kage reads the scroll of Blur: read languages d100 = 12, needs 30 or less -> read, learnt")
        self.assertEqual(intlearn.line("Kage", "Fireball", 12, 50, 0, intlearn.NOT_ITS, 3),
                         "Kage can't learn Fireball from the scroll: not one of a Shinobi's spells (the scroll is kept)")


if __name__ == "__main__":
    unittest.main()
