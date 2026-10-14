"""The elves' ears and the half-elves' own figures (figures.py), and the Ledger's pictures with them
(sprites.Pictures). With DSUN_OBJECTS (the game's SEGOBJEX.GFF, its GPLDATA.GFF beside it), each
party figure built from the game's own pictures."""

import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dscompanion import art, figures as fg, gff, halfelf as he, sprites, spritegear as sg, spriteparts as sp

N = None


class EarTests(unittest.TestCase):
    def test_shape(self):
        # (tip first, a pixel out past the rim and two rows up; salmon inside, rose outside)
        self.assertEqual(fg.ear_shape(5, 4, -1), [(3, 2, fg.RIM), (5, 3, fg.LIT), (4, 3, fg.RIM),
                                                  (5, 4, fg.LIT), (4, 4, fg.RIM)])
        self.assertEqual(fg.ear_shape(5, 4, 1, 1)[0], (7, 6, fg.RIM))  # (lying head down)

    def test_over_what_is_worn(self):
        """Ears go where the picture is as the game's, never over what is worn (a helm)."""
        rows = [[N] * 6 for _ in range(6)]
        rows[3][2] = 140
        dressed = [[N] * 10 for _ in range(10)]
        dressed[3 + 2][2 + 2] = 140  # (the game's own pixel: drawn over)
        dressed[2 + 2][2 + 2] = 211  # (a helm's: kept)
        fg.EAR_PLAN[(9999, False, 0)] = [(2, 3, -1)]
        try:
            fg.ears_over(dressed, rows, 9999, 0, False, 2)
        finally:
            del fg.EAR_PLAN[(9999, False, 0)]
        self.assertEqual(dressed[5][4], fg.LIT)
        self.assertEqual(dressed[4][4], 211)
        self.assertEqual(dressed[3][2], fg.RIM)  # (the tip)

    def test_no_plan_no_ears(self):
        rows = [[N] * 4 for _ in range(4)]
        self.assertEqual(fg.ear_plan(rows, fg.ELF_MAN, 0, False), [])


class ShapeTests(unittest.TestCase):
    def test_slim(self):
        """A column out below the neck, the one whose loss changes the picture least."""
        rows = [[N, 1, 1, N],
                [2, 3, 3, 4],
                [2, 3, 3, 4]]
        out, x = fg._slim(rows, 1)
        self.assertEqual(out[0], [N, 1, 1, N])
        self.assertEqual(out[1], [2, 3, 4, N])
        self.assertEqual(x, 2)

    def test_moved(self):
        """The game's frame's parts where they are on a half-elf's: past the column, from the
        neck down, a column on; hair only where it is still golden."""
        parts = sp.Parts(sp.FRONT, sp.Head(0, 1, 4, 1), {(1, 0), (3, 0), (3, 3)}, (2, 0, 5),
                         {"right": (0, 4), "left": (5, 4)}, 4, [(6, 1, 2), (6, 4, 5)], 6)
        rows = [[N, 179, N, 128, N, N, N], [N] * 7, [N] * 7, [N, N, N, N, 180, N, N]]
        out = fg.moved(parts, (2, 2, 1), rows)
        self.assertEqual(out.shoulders, (2, 0, 6))
        self.assertEqual(out.hands, {"right": (0, 4), "left": (6, 4)})
        self.assertEqual(out.feet, [(6, 1, 2), (6, 5, 6)])
        self.assertEqual(out.hair, {(1, 0), (4, 3)})  # ((3, 0) brown: not hers any more)
        self.assertEqual(fg.moved(parts, None, rows).hands, parts.hands)


class GearTests(unittest.TestCase):
    """What a half-elf's frame tells the gear (spritegear.Own) that its colours can't."""

    def test_mover_back(self):
        for cut in ((2, 2, 1), (2, 2, -1), None):
            at, back = fg.mover(cut), fg.mover_back(cut)
            for x in range(6):
                if cut and cut[2] < 0 and x == cut[1]:
                    continue  # (the column taken out: nowhere on hers)
                self.assertEqual(back(at(x, 3), 3), x)

    def test_belt_not_over_own_cloak(self):
        rows = [[N] * 7 for _ in range(4)] + [[N, 174, 175, 140, 175, 174, N]] + [[N] * 7 for _ in range(4)]
        parts = sp.Parts(sp.BACK, sp.Head(0, 2, 4, 1), set(), (2, 1, 5), {}, 4, [(8, 2, 4)], 8)
        out = sg.padded(rows, 2)
        sg.draw_belt(out, parts, 42, 2, frozenset((174, 175, 176)))
        self.assertEqual(out[6][2 + 1:2 + 6], [174, 175, sg._by_light(140, sg.BELTS[42]), 175, 174])

    def test_armour_only_where_worn(self):
        """Armour recolours the figure's own clothes (Own.clothes), only where it wore them."""
        rows = [[N, 140, 140, N]] * 3 + [[N, 204, 205, N]] * 4
        parts = sp.Parts(sp.FRONT, sp.Head(0, 1, 2, 1), set(), (3, 0, 3), {}, 5, [(6, 1, 2)], 6)
        own = sg.Own(parts, rows, parts, lambda x, y: x, clothes=(254, 204, 205), worn=frozenset({(1, 4), (2, 4)}))
        out = sg.padded(rows, 0)
        sg.draw_armour(out, 2061, parts, 9, 0, own)
        self.assertNotEqual(out[4][1:3], [204, 205])  # (worn: armour)
        self.assertEqual(out[3][1:3], [204, 205])  # (not)


class PictureTests(unittest.TestCase):
    def test_human_figure_without_the_elf(self):
        """No elf man's pictures in the file (or no palette): the half-elf man is the human's
        figure in his colours, as before."""
        frame = [[N, 69, 69, N], [N, 140, 140, N], [N, 140, 140, N], [N, 254, 254, N]]
        chunk = sprites.encode_frames([frame])
        pics = sprites.Pictures({("BMP ", 2095): chunk, ("BMP ", 2096): chunk})
        model, frames, owns = pics.base(2095, he.MAN, False)
        self.assertEqual((model, owns), (2095, [None]))
        self.assertEqual(frames[0], frame)


@unittest.skipUnless(os.environ.get("DSUN_OBJECTS"), "DSUN_OBJECTS (the game's SEGOBJEX.GFF) not given")
class GameTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = os.environ["DSUN_OBJECTS"]
        with open(path, "rb") as f:
            cls.chunks = gff.read_gff(f.read())
        icons_palette = art._find(os.path.dirname(os.path.abspath(path)), "GPLDATA.GFF")
        with open(icons_palette, "rb") as f:
            sg.set_palette(art.palette_colours(gff.read_gff(f.read())[("PAL ", art.PORTRAIT_PALETTE)]))

    def test_figures(self):
        pics = sprites.Pictures(self.chunks)
        for figure, source in ((he.MAN, fg.ELF_MAN), (he.WOMAN, fg.HUMAN_WOMAN)):
            for combat in (False, True):
                model, frames, owns = pics.base(pics.model(figure), figure, combat)
                self.assertEqual(model, source)
                self.assertEqual(len(frames), len(pics.own(source + combat)))
                self.assertTrue(all(o is not None and o.worn for o in owns))
        for obj in (304, 305, he.MAN, he.WOMAN):
            for combat in (False, True):
                chunk = pics.build(obj, combat, {"right": (115, 4), "helm": (5, 4), "cloak": (65, 4)}, (9, 10, 11))
                self.assertLessEqual(len(chunk), pics.room(obj, combat))
                n, = struct.unpack_from("<H", chunk, 4)
                self.assertEqual(n, len(pics.own(pics.model(obj) + combat)))


if __name__ == "__main__":
    unittest.main()
