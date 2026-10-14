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


if __name__ == "__main__":
    unittest.main()
