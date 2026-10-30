"""The sheet's weapon specs, a byte each up to 2.12 or packed with the age beside them (game.py)."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import game, specialize  # noqa: E402


def sheet_with(specs: bytes) -> bytes:
    return bytes(game.SPEC_SLOTS) + specs + bytes(game.SHEET_SIZE - game.SPEC_SLOTS - 4)


class SpecSlotTests(unittest.TestCase):
    def test_both_layouts_read_alike(self):
        """A gladiator's four kinds (16 the most), a Myrmidon's two, none: the same from a byte
        each (no age) as packed (the age kept)."""
        for kinds in ((1, 16, 9, 2), (6, 1, 0, 0), (0, 0, 0, 0)):
            with self.subTest(kinds=kinds):
                old, new = sheet_with(bytes(kinds)), sheet_with(game.packed_specs(kinds, 30))
                self.assertFalse(game.spec_packed(old))
                self.assertTrue(game.spec_packed(new))
                self.assertEqual(game.spec_kinds(old), bytes(kinds))
                self.assertEqual(game.spec_kinds(new), bytes(kinds))
                self.assertEqual((game.sheet_age(old), game.sheet_age(new)), (0, 30))

    def test_packing(self):
        """5 bits each in +14h to +16h, +16h's top bit set, +17h the age; room for 31 kinds."""
        self.assertEqual(game.packed_specs((1, 2, 3, 4), 9), bytes((0x41, 0x0C, 0x82, 9)))
        self.assertEqual(game.spec_kinds(sheet_with(game.packed_specs((31, 31, 31, 31)))), bytes((31,) * 4))
        self.assertEqual(game.packed_specs(()), bytes((0, 0, 0x80, 0)))
        self.assertLessEqual(len(specialize.KINDS), 31)

    def test_with_specs_keeps_the_age(self):
        sheet = sheet_with(game.packed_specs((1,), 12))
        changed = game.with_specs(sheet, (1, 5))
        self.assertEqual((game.spec_kinds(changed), game.sheet_age(changed)), (bytes((1, 5, 0, 0)), 12))
        self.assertEqual(len(changed), game.SHEET_SIZE)
        old = game.with_specs(sheet_with(bytes((1, 0, 0, 0))), (1, 5))
        self.assertEqual((game.spec_kinds(old), game.sheet_age(old)), (bytes((1, 5, 0, 0)), 0))


if __name__ == "__main__":
    unittest.main()
