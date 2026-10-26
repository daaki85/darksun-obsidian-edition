"""Tests for the dice log's line for a shot at the Bowyer's archery target (dsloader/bowyer.py)."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import bowyer


class BowyerTests(unittest.TestCase):
    def test_distance(self):
        """The game's squares: along a row, the count; across, its rounded square root."""
        self.assertEqual(bowyer.distance(41, 69, 56, 69), 15)
        self.assertEqual(bowyer.distance(0, 0, 3, 4), 5)
        self.assertEqual(bowyer.distance(0, 0, 10, 10), 14)
        self.assertEqual(bowyer.distance(5, 5, 5, 5), 0)
        self.assertEqual(bowyer.distance(0, 0, 300, 0), bowyer.FAR_AWAY)

    def test_need(self):
        self.assertEqual(bowyer.need(21, 15), 14)
        self.assertEqual(bowyer.need(12, 15), 2)  # (DEX under the distance)

    def test_results(self):
        line = bowyer.describe(3, 21, 15, 9, False, "Daaki")[0]
        self.assertEqual(line, "Daaki shoots at the archery target (15 squares from the target, 9 from the Bowyer): "
                               "0-20 = 3, needs under 14 (DEX 21 - 15 / 2), the centre 4 or less "
                               "-> the centre: the Bowyer's reward, 6 Arrows +2")
        self.assertTrue(bowyer.describe(14, 21, 15, 9, False, "D")[0].endswith("-> miss"))
        self.assertTrue(bowyer.describe(12, 21, 15, 9, False, "D")[0].endswith("-> the outer ring"))
        self.assertTrue(bowyer.describe(6, 21, 15, 9, False, "D")[0].endswith("-> the inner ring"))
        self.assertIn("13 squares or closer", bowyer.describe(0, 21, 12, 9, False, "D")[0])
        self.assertIn("once", bowyer.describe(0, 21, 15, 9, True, "D")[0])
        self.assertIn("25 squares or more", bowyer.describe(0, 21, 15, 25, False, "D")[0])


if __name__ == "__main__":
    unittest.main()
