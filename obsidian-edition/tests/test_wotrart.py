"""Wake of the Ravager's icons (wotrart.py), on pictures made here: nothing from either game."""

import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import wotrart


def plnr(width, height, bits, colours, codes):
    """A PLNR picture: Shattered Lands' frame header, then 0FFh "PLNR", BITS, the colour map and
    CODES packed BITS a code, the highest bits first."""
    acc = n = 0
    data = bytearray()
    for code in codes:
        acc, n = (acc << bits) | code, n + bits
        while n >= 8:
            n -= 8
            data.append((acc >> n) & 0xFF)
    if n:
        data.append((acc << (8 - n)) & 0xFF)
    body = (struct.pack("<HH", width, height) + wotrart.PLNR + bytes([bits])
            + bytes(colours).ljust(1 << bits, b"\0") + bytes(data))
    return struct.pack("<IHI", 10 + len(body), 1, 10) + body


class PlnrTests(unittest.TestCase):
    def test_codes_and_escapes(self):
        """Codes through the colour map; 0 0 is colour 0, 0 k the last pixel k + 2 more times."""
        colours = [9, 40, 41, 42]
        chunk = plnr(4, 2, 4, colours, [1, 2, 0, 0, 3,   # 40 41 9 42
                                        2, 0, 1])        # 41, then 3 more
        self.assertEqual(wotrart.decode_plnr(chunk), [[40, 41, 9, 42], [41, 41, 41, 41]])

    def test_five_bits(self):
        colours = list(range(100, 132))
        chunk = plnr(2, 2, 5, colours, [31, 17, 0, 0, 5])
        self.assertEqual(wotrart.decode_plnr(chunk), [[131, 117], [100, 105]])

    def test_short_data_pads_with_colour_0(self):
        self.assertEqual(wotrart.decode_plnr(plnr(3, 1, 4, [7, 8], [1])), [[8, 7, 7]])

    def test_not_plnr(self):
        chunk = bytearray(plnr(1, 1, 4, [0, 1], [1]))
        chunk[15:19] = b"PLAN"
        with self.assertRaises(ValueError):
            wotrart.decode_plnr(bytes(chunk))

    def test_nearest_stable_colour(self):
        stable = [(5, (0, 0, 0)), (40, (250, 10, 10)), (41, (10, 10, 250))]
        palette = {0: (20, 20, 20), 1: (200, 30, 30), 2: (30, 30, 200)}
        self.assertEqual(wotrart.to_shattered_lands([[0, 1, 2, 1]], palette, stable), [[5, 40, 41, 40]])

    def test_every_spell_has_an_icon(self):
        self.assertEqual(len(wotrart.ICONS), 9)
        self.assertEqual(len(set(wotrart.ICONS.values())), 9)
        self.assertIn("Whirlwind", wotrart.ICONS)


if __name__ == "__main__":
    unittest.main()
