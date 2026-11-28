"""What the outfits and gear add is drawn in palette entries no area changes (spritegear.steadied)."""
import os
import sys
import unittest
from pathlib import Path
from zipfile import ZipFile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import art, spritegear as sg


def _palette():
    # a grey ramp, with a few regional entries made to look like fixed ones
    colours = [(i, i, i) for i in range(256)]
    colours[120] = (60, 61, 60)  # (nearest fixed: 60 or 61)
    colours[225] = (140, 141, 139)
    return colours


class SteadyColours(unittest.TestCase):
    def setUp(self):
        self.saved = list(sg._RGB)
        sg.set_palette(_palette())

    def tearDown(self):
        sg.set_palette(self.saved)  # (an empty one leaves no palette set, as before)

    def test_regional_entries_are_the_ones_areas_change(self):
        for c in (19, 21, 29, 80, 100, 127, 223, 225, 239):
            self.assertIn(c, sg.REGIONAL)
        for c in (1, 15, 30, 79, 128, 222, 240, 248):  # (the cycled glows and the fixed ranges)
            self.assertNotIn(c, sg.REGIONAL)
        self.assertFalse(set(sg.STEADY) & sg.REGIONAL)

    def test_authored_material_layers_paint_only_steady_colours_on_existing_cloth(self):
        entries = 0
        for path in Path(sg.__file__).parent.glob("*_outfit_layers.zip"):
            with ZipFile(path) as archive:
                for name in archive.namelist():
                    if not name.endswith("-material"):
                        continue
                    entries += 1
                    finish = archive.read(name)
                    paint = archive.read(name[:-len("-material")])
                    for f in range(14 if "/combat-" in name else 15):
                        rows = art.decode_frame(finish, f)[2]
                        base = art.decode_frame(paint, f)[2]
                        self.assertEqual((len(rows), len(rows[0])), (len(base), len(base[0])))
                        edits = [(ink, base[y][x]) for y, row in enumerate(rows)
                                 for x, ink in enumerate(row) if ink is not None]
                        self.assertTrue(all(ink in sg.STEADY and old not in (None, 255)
                                            for ink, old in edits), (path.name, name, f))
        self.assertGreater(entries, 0)

    def test_a_regional_colour_moves_to_the_nearest_fixed_one(self):
        self.assertIn(sg.steady_colour(120), (60, 61))
        self.assertIn(sg.steady_colour(225), (140, 141, 139))
        self.assertEqual(sg.steady_colour(150), 150)  # (a fixed one stays)

    def test_the_figures_own_pixels_stay(self):
        source = [[29, 120], [None, 5]]
        pad = 1
        drawn = [[None, None, None, None],
                 [None, 29, 120, 225],     # (its own 29 and 120 kept; 225 added beside them)
                 [None, 120, 5, None]]     # (120 drawn where it had none)
        out = sg.steadied(drawn, source, pad)
        self.assertEqual(out[1][1], 29)
        self.assertEqual(out[1][2], 120)
        self.assertEqual(out[1][3], sg.steady_colour(225))
        self.assertEqual(out[2][1], sg.steady_colour(120))
        self.assertEqual(out[2][2], 5)
        self.assertNotIn(out[2][1], sg.REGIONAL)


if __name__ == "__main__":
    unittest.main()
