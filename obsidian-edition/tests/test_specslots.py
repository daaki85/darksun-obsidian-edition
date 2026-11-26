"""The sheet's weapon specs, a byte each up to 2.12 or packed with the age beside them (game.py)."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import game, specialize  # noqa: E402


def sheet_with(specs: bytes) -> bytes:
    return bytes(game.SPEC_SLOTS) + specs + bytes(game.SHEET_SIZE - game.SPEC_SLOTS - 4)


def v2(kinds, age=0, roll=31) -> bytes:
    """+14h..+17h in the SPEC_V2 layout (2.14 to now: base 17), as a sheet from then has them."""
    value = sum(k * 17 ** i for i, k in enumerate(kinds)) | roll << 17 | 0xC00000
    return value.to_bytes(3, "little") + bytes((age,))


class SpecSlotTests(unittest.TestCase):
    def test_layouts_read_alike(self):
        """A gladiator's four kinds (16 the most), a Myrmidon's two, none: the same from a byte
        each (no age), base 17 (V2) and V3 (the first, the others ascending, then the empty), the
        age kept."""
        for kinds, v3 in (((9, 16, 1, 2), (9, 1, 2, 16)), ((6, 1, 0, 0), (6, 1, 0, 0)), ((0, 0, 0, 0), (0, 0, 0, 0))):
            with self.subTest(kinds=kinds):
                old, base17, new = sheet_with(bytes(kinds)), sheet_with(v2(kinds, 30)), sheet_with(game.packed_specs(kinds, 30))
                self.assertFalse(game.spec_packed(old))
                self.assertTrue(game.spec_packed(new))
                self.assertEqual(game.spec_kinds(old), bytes(kinds))
                self.assertEqual(game.spec_kinds(base17), bytes(kinds))
                self.assertEqual(game.spec_kinds(new), bytes(v3))
                self.assertEqual((game.sheet_age(old), game.sheet_age(base17), game.sheet_age(new)), (0, 30, 30))

    def test_packing(self):
        """V3: bits 0-16 17^4 (past every base 17 number) and then the first spec times REST_SETS plus
        the others' rank as a set, the starting roll in bits 17-21 (31: none kept), +16h's two top bits
        set, +17h the age. Every pick of up to four of the 22 kinds, in every order, read back as the
        first and the others ascending, and the number of each such its own; a kind twice counted once."""
        import itertools
        value = game.V3_BASE + game.spec_rank((4, 1, 2, 3)) | 31 << 17 | 0xC00000
        self.assertEqual(game.packed_specs((4, 2, 3, 1), 9), value.to_bytes(3, "little") + bytes((9,)))
        self.assertEqual(game.packed_specs(()), bytes((0x41, 0x46, 0xFF, 0)))
        self.assertEqual(game.packed_specs((), 3, 0), bytes((0x41, 0x46, 0xC1, 3)))
        self.assertEqual(len(specialize.KINDS), game.KIND_COUNT)
        self.assertEqual(game.V3_BASE, 16 * (1 + 17 + 17 ** 2 + 17 ** 3) + 1)  # (V2's greatest, + 1)
        numbers = {}
        for count in range(5):
            for kinds in itertools.permutations(range(1, game.KIND_COUNT + 1), count):
                packed = game.packed_specs(kinds, 5, 3)
                number = int.from_bytes(packed[:3], "little") & game.SPEC_KINDS_MASK
                want = bytes(kinds[:1] + tuple(sorted(kinds[1:])) + (0,) * (4 - count))
                self.assertEqual(numbers.setdefault(number, want), want)
                self.assertEqual(game.spec_kinds(sheet_with(packed)), want)
        self.assertEqual(len(numbers), 1 + 22 + 22 * 21 + 22 * 210 + 22 * 1330)
        self.assertEqual(game.spec_kinds(sheet_with(game.packed_specs((5, 5, 2)))), bytes((5, 2, 0, 0)))

    def test_rolls(self):
        """The starting roll: none kept in the older layouts or as 31; else 0 to 20."""
        self.assertIsNone(game.sheet_roll(sheet_with(game.packed_specs((1,), 9))))
        self.assertIsNone(game.sheet_roll(sheet_with(bytes((0x41, 0x0C, 0x82, 9)))))  # (2.13's)
        self.assertEqual(game.sheet_roll(sheet_with(game.packed_specs((1, 2), 9, 20))), 20)
        self.assertEqual(game.spec_kinds(sheet_with(game.packed_specs((2, 1), 9, 20))), bytes((2, 1, 0, 0)))
        self.assertEqual(game.sheet_roll(sheet_with(v2((1, 2), 9, 20))), 20)

    def test_older_layouts_read(self):
        """2.13's packed specs (5 bits each, no roll), 2.12's bytes and V2's base 17 read as they were."""
        self.assertEqual(game.spec_kinds(sheet_with(v2((9, 1, 16), 9, 4))), bytes((9, 1, 16, 0)))
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
