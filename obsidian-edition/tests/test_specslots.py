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
        """The four a number base 17 in bits 0-16 (kind + 1 each: 16 kinds and none), the starting
        roll in bits 17-21 (31: none kept), +16h's two top bits set, +17h the age."""
        value = 1 + 2 * 17 + 3 * 17 ** 2 + 4 * 17 ** 3 | 31 << 17 | 0xC00000
        self.assertEqual(game.packed_specs((1, 2, 3, 4), 9), value.to_bytes(3, "little") + bytes((9,)))
        self.assertEqual(game.spec_kinds(sheet_with(game.packed_specs((16, 16, 16, 16)))), bytes((16,) * 4))
        self.assertEqual(game.packed_specs(()), bytes((0, 0, 0xFE, 0)))
        self.assertEqual(game.packed_specs((), 3, 0), bytes((0, 0, 0xC0, 3)))
        self.assertLessEqual(len(specialize.KINDS), 16)
        self.assertLessEqual(17 ** 4 - 1, game.SPEC_KINDS_MASK)

    def test_rolls(self):
        """The starting roll: none kept in the older layouts or as 31; else 0 to 20."""
        self.assertIsNone(game.sheet_roll(sheet_with(game.packed_specs((1,), 9))))
        self.assertIsNone(game.sheet_roll(sheet_with(bytes((0x41, 0x0C, 0x82, 9)))))  # (2.13's)
        self.assertEqual(game.sheet_roll(sheet_with(game.packed_specs((1, 2), 9, 20))), 20)
        self.assertEqual(game.spec_kinds(sheet_with(game.packed_specs((1, 2), 9, 20))), bytes((1, 2, 0, 0)))

    def test_older_layouts_read(self):
        """2.13's packed specs (5 bits each, no roll) and 2.12's bytes read as they were."""
        self.assertEqual(game.spec_kinds(sheet_with(bytes((0x41, 0x0C, 0x82, 9)))), bytes((1, 2, 3, 4)))
        self.assertEqual(game.sheet_age(sheet_with(bytes((0x41, 0x0C, 0x82, 9)))), 9)
        self.assertEqual(game.spec_kinds(sheet_with(bytes((1, 0, 0, 0)))), bytes((1, 0, 0, 0)))

    def test_with_specs_keeps_the_age(self):
        sheet = sheet_with(game.packed_specs((1,), 12, 4))
        changed = game.with_specs(sheet, (1, 5))
        self.assertEqual((game.spec_kinds(changed), game.sheet_age(changed), game.sheet_roll(changed)),
                         (bytes((1, 5, 0, 0)), 12, 4))
        self.assertEqual(len(changed), game.SHEET_SIZE)
        old = game.with_specs(sheet_with(bytes((1, 0, 0, 0))), (1, 5))
        self.assertEqual((game.spec_kinds(old), game.sheet_age(old)), (bytes((1, 5, 0, 0)), 0))


if __name__ == "__main__":
    unittest.main()
