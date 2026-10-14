"""Half-elves' own colours (halfelf.py), and the Ledger's pictures of them (sprites.Pictures)."""

import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dscompanion import art, halfelf as he, sprites, spritegear as sg

N = None


def man():
    """A small man: dark hair (69, 50) on top, a black tunic with its sheen (23, 48), green
    wristbands, and dark boots (69, 29) at his feet."""
    return [[N, 69, 50, 69, N],
            [N, 69, 70, 69, N],
            [N, 140, 140, 140, N],
            [N, 140, 140, 140, N],
            [N, 140, 140, 140, N],
            [N, 140, 140, 140, N],
            [250, 254, 23, 254, 249],
            [N, 254, 48, 254, N],
            [N, 254, 254, 254, N],
            [N, 140, N, 140, N],
            [N, 140, N, 140, N],
            [N, 140, N, 140, N],
            [N, 140, N, 140, N],
            [N, 140, N, 140, N],
            [N, 140, N, 140, N],
            [N, 69, N, 29, N]]


def woman():
    """A small woman: brown hair (128, 129, 134) from the top of her head down her back, a green
    cloak (188, 53), green wristbands and blue boots; skin (140) and the outline (254)."""
    return [[N, 128, 129, 128, N],
            [134, 129, 129, 129, 134],
            [134, 140, 140, 140, 134],
            [134, 140, 140, 140, 134],
            [188, 53, 254, 53, 188],
            [249, 188, 254, 188, 250],
            [N, 140, N, 140, N],
            [N, 159, N, 160, N],
            [N, 158, N, 158, N]]


class RecolourTests(unittest.TestCase):
    def test_others_unchanged(self):
        self.assertEqual(he.recolour(man(), 300), man())
        self.assertEqual(he.recolour(woman(), 301), woman())

    def test_man(self):
        out = he.recolour(man(), he.MAN)
        self.assertEqual(out[0][1:4], [179, 200, 179])  # (fair hair)
        self.assertEqual(out[6], [180, 254, 189, 254, 182])  # (a green tunic, bronze bands)
        self.assertEqual(out[7][2], 188)
        self.assertEqual(out[-1][1], 204)  # (brown boots: his darkest, not the hair's 179)
        self.assertEqual(out[-1][3], 168)
        self.assertEqual(out[3], man()[3])  # (his face as it was)

    def test_woman(self):
        out = he.recolour(woman(), he.WOMAN)
        self.assertEqual(out[0][1:4], [181, 180, 181])  # (golden hair)
        self.assertEqual(out[2][0], 181)  # (down her back too)
        self.assertEqual(out[4], [174, 175, 254, 175, 174])  # (a purple cloak)
        self.assertEqual(out[5][0], 176)  # (purple wristbands)
        self.assertEqual(out[7][1:4:2], [202, 76])  # (red boots)
        self.assertEqual(out[8][1], 195)
        self.assertEqual(out[2][2], 140)  # (her face as it was)

    def test_hair_under_an_arm(self):
        """Something over her head (an arm, in the top rows): the hair is still found."""
        rows = [[140] * 5, [140] * 5] + woman()
        out = he.recolour(rows, he.WOMAN)
        self.assertEqual(out[2][1:4], [181, 180, 181])

    def test_gear_kept(self):
        """Pixels the gear changed keep the gear's colours; the rest are the half-elf's."""
        rows = woman()
        dressed = sg.padded(rows, 2)
        dressed[4 + 2][0 + 2] = 204  # (a cloak worn: its colour on her own cloak)
        out = he.over(dressed, rows, he.WOMAN, 2)
        self.assertEqual(out[4 + 2][0 + 2], 204)
        self.assertEqual(out[4 + 2][1 + 2], 175)
        self.assertEqual(out[0 + 2][1 + 2], 181)

    def test_only_party_colours(self):
        """Every colour put on is one the party's pictures already have (the regions' palettes
        change the rest)."""
        party = set(range(11, 14)) | {16} | set(range(19, 32)) | {38, 41, 42, 43, 45, 47} | \
            set(range(48, 57)) | set(range(58, 67)) | {68, 69, 70, 72, 73, 75, 76, 77} | \
            set(range(102, 112)) | set(range(128, 155)) | set(range(156, 187)) | \
            set(range(188, 192)) | set(range(194, 218)) | {240, 242, 243, 249, 250, 254}
        for table in (he.MAN_HAIR, he.MAN_TUNIC, he.MAN_BOOTS, he.MAN_BANDS, he.HAIR, he.BODY):
            self.assertLessEqual(set(table.values()), party)


class PictureTests(unittest.TestCase):
    def setUp(self):
        walk = sprites.encode_frames([man()] * 15)
        fight = sprites.encode_frames([man()] * 14)
        self.chunks = {("BMP ", 2095): walk, ("BMP ", 2096): fight,
                       ("BMP ", sg.CLOAK_MODEL): walk, ("BMP ", sg.CLOAK_MODEL + 1): fight}
        for obj in (300, he.MAN):
            self.chunks[("OJFF", obj)] = bytes(12) + struct.pack("<H", 2095) + b"\0\0"

    def test_half_elf_pictures(self):
        """The half-elf's object (or a spare drawn as one) in his colours, the human's not."""
        pics = sprites.Pictures(self.chunks)
        human = art.decode_frame(pics.build(300, False, {}, ()), 0)[2]
        half = art.decode_frame(pics.build(he.MAN, False, {}, ()), 0)[2]
        spare = art.decode_frame(pics.build(sprites.SPARES[0], False, {}, (), 2095, he.MAN), 0)[2]
        colours = lambda rows: {p for r in rows for p in r if p is not None}
        self.assertIn(69, colours(human))
        self.assertNotIn(69, colours(half))
        self.assertIn(179, colours(half))
        self.assertEqual(spare, half)


if __name__ == "__main__":
    unittest.main()
