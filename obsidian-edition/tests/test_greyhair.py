"""Grey hair on the party's map figures by age category (greyhair.py)."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import greyhair  # noqa: E402


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
