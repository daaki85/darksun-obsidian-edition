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
    "semyon": ["TOLD", "SHIPPED", "FOUND", "PLACED", "MET", "LEFT", "DIED", "CLEARED", "SETTLED", "ESCAPING"],
    "kalzith": ["MET", "FRIENDLY", "COLD", "STOCKED", "DIED", "LOOTED", "DRESSED", "SOLD_OUT"],
    "champions": ["KING", "FOUGHT"],
    "vulture": ["MEAL", "EATEN"],
    "ring": ["XP_GIVEN"],
    "pehtuclchest": ["DISARMED", "UNLOCKED"],
    "kurzak": ["DEAD"],
    "aging": ["COUNTING"],
}

# Alagorn's menus' overflow runs from alagorn.FLAGS to this at most (test_pehtuclchest checks the
# game's scripts reach no further, with GPLDATA.GFF)
ALAGORN_LAST = 794


def _ranges():
    """The flags kept in ranges or tables rather than one constant each: (name, number)."""
    from dsloader import aging, alagorn, pensasks
    out = [(f"pensasks {ask.text.strip()!r}", ask.flag)
           for ask in pensasks.DINOS_ASKS + pensasks.TRUSTEE_ASKS if ask.flag is not None]
    out += [(f"alagorn.FLAGS+{n - alagorn.FLAGS}", n) for n in range(alagorn.FLAGS, ALAGORN_LAST + 1)]
    out += [(f"aging.COUNT_FIRST+{n - aging.COUNT_FIRST}", n)
            for n in range(aging.COUNT_FIRST, aging.COUNT_FIRST + aging.COUNT_BITS)]
    return out


class FlagRangeTests(unittest.TestCase):
    def test_in_range_and_unshared(self):
        seen = {}
        named = [(f"{name}.{c}", getattr(importlib.import_module("dsloader." + name), c))
                 for name, constants in FLAGS.items() for c in constants]
        for label, n in named + _ranges():
            self.assertTrue(756 <= n < game.FLAG_COUNT, f"{label} = {n}")
            self.assertNotIn(n, seen, f"{label} = {n}, also {seen.get(n)}")
            seen[n] = label

    def test_set_flag_refuses_past_them(self):
        gd = game.GameData.__new__(game.GameData)
        with self.assertRaises(ValueError):
            gd.set_flag(game.FLAG_COUNT)


if __name__ == "__main__":
    unittest.main()
