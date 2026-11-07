"""The Loader's own game flags (DEVELOPMENT.md's The Loader's game flags): each module's in 756-807,
the 808 a save keeps, and no two modules sharing one."""

import importlib
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import game

# (module, its flag constants: the table's)
FLAGS = {
    "semyon": ["PLACED", "MET", "LEFT", "DIED", "CLEARED", "SETTLED", "ESCAPING"],
    "kalzith": ["MET", "FRIENDLY", "COLD", "STOCKED", "DIED", "LOOTED", "DRESSED", "SOLD_OUT"],
    "champions": ["KING", "FOUGHT"],
    "vulture": ["MEAL", "EATEN"],
    "ring": ["XP_GIVEN"],
    "pehtuclchest": ["DISARMED", "UNLOCKED"],
    "kurzak": ["DEAD"],
    "aging": ["COUNTING"],
}


class FlagRangeTests(unittest.TestCase):
    def test_in_range_and_unshared(self):
        seen = {}
        for name, constants in FLAGS.items():
            module = importlib.import_module("dsloader." + name)
            for c in constants:
                n = getattr(module, c)
                self.assertTrue(756 <= n < game.FLAG_COUNT, f"{name}.{c} = {n}")
                self.assertNotIn(n, seen, f"{name}.{c} = {n}, also {seen.get(n)}")
                seen[n] = f"{name}.{c}"
        aging = importlib.import_module("dsloader.aging")
        self.assertLessEqual(aging.COUNT_FIRST + aging.COUNT_BITS, game.FLAG_COUNT)

    def test_set_flag_refuses_past_them(self):
        gd = game.GameData.__new__(game.GameData)
        with self.assertRaises(ValueError):
            gd.set_flag(game.FLAG_COUNT)


if __name__ == "__main__":
    unittest.main()
