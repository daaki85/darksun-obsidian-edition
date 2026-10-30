"""Grey hair on the party's map figures by age category (greyhair.py)."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import greyhair  # noqa: E402


class DataTests(unittest.TestCase):
    def test_every_haired_look_has_its_greys(self):
        """Each figure with hair (spriteparts' hair colours, or greyhair's own), the half-elves'
        own figures and the thri-kreen's antennae have all three categories (the thri-kreen only
        venerable); dwarves and muls (hairless on Athas) none."""
        from dsloader import halfelf, spriteparts as sp
        for model, (_, _, colours) in sp.MODELS.items():
            if model == sp.KREEN:
                self.assertEqual(set(greyhair.MAPS[model]), {greyhair.VENERABLE})
            elif colours or model in greyhair.COLOURS:
                self.assertEqual(set(greyhair.MAPS[model]), {1, 2, 3}, model)
            else:
                self.assertNotIn(model, greyhair.MAPS)
        for figure in (halfelf.MAN, halfelf.WOMAN):
            self.assertEqual(set(greyhair.MAPS[figure]), {1, 2, 3})

    def test_greys_only(self):
        """Every hair colour becomes one of the palette's stable greys (208-217) or its white (46)."""
        for look, stages in greyhair.MAPS.items():
            for stage, colours in stages.items():
                self.assertLessEqual(set(colours.values()), set(range(208, 218)) | {46}, (look, stage))

    def test_lighter_with_age(self):
        """Each hair colour as light or lighter from old to venerable (the greys 208-217 dark to
        light, white 46 the lightest)."""
        light = lambda c: 218 if c == 46 else c  # noqa: E731
        for look, stages in greyhair.MAPS.items():
            for colour, grey in stages.get(greyhair.OLD, {}).items():
                if colour in stages[greyhair.VENERABLE]:
                    self.assertGreaterEqual(light(stages[greyhair.VENERABLE][colour]), light(grey), (look, colour))


class AgedTests(unittest.TestCase):
    def setUp(self):
        self.maps, self.speckle = dict(greyhair.MAPS), dict(greyhair.SPECKLE)
        greyhair.MAPS.clear()
        greyhair.SPECKLE.clear()
        greyhair.MAPS[1] = {greyhair.OLD: {5: 9, 6: 10}, greyhair.MIDDLE: {5: 9, 6: 10}}

    def tearDown(self):
        greyhair.MAPS.clear()
        greyhair.MAPS.update(self.maps)
        greyhair.SPECKLE.clear()
        greyhair.SPECKLE.update(self.speckle)

    def rows(self):  # (padded by 1: the hair at (0, 0), (1, 0) and (0, 1) of the frame)
        return [[None, None, None, None], [None, 5, 6, None], [None, 7, None, None]]

    def test_only_the_hair_in_its_colours(self):
        """The hair's pixels in the map's colours are recoloured; another colour there (a helm's,
        7) and the rest of the figure stay."""
        out = greyhair.aged(self.rows(), {(0, 0), (1, 0), (0, 1)}, 1, greyhair.OLD, 1)
        self.assertEqual(out[1][1:3], [9, 10])
        self.assertEqual(out[2][1], 7)

    def test_young_or_unknown_look_unchanged(self):
        self.assertEqual(greyhair.aged(self.rows(), {(0, 0)}, 1, 0, 1), self.rows())
        self.assertEqual(greyhair.aged(self.rows(), {(0, 0)}, 2, greyhair.OLD, 1), self.rows())

    def test_speckle_greys_some(self):
        """(period 2, count 1): only where (x + 2y) % 2 < 1, the even columns."""
        greyhair.SPECKLE[1] = {greyhair.MIDDLE: (2, 1)}
        out = greyhair.aged(self.rows(), {(0, 0), (1, 0)}, 1, greyhair.MIDDLE, 1)
        self.assertEqual(out[1][1:3], [9, 6])

    def test_look(self):
        from dsloader import halfelf
        self.assertEqual(greyhair.look(2061, halfelf.MAN), halfelf.MAN)
        self.assertEqual(greyhair.look(2095, 300), 2095)

    def test_stage_needs_the_rule(self):
        class G:
            rules = 0
        self.assertEqual(greyhair.stage_of(G(), 0), 0)


if __name__ == "__main__":
    unittest.main()
