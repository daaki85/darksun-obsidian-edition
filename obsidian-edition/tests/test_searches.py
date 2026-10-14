"""The dice log's lines for searching junk, haystacks and wardrobes (searches.py)."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import searches


class SearchTests(unittest.TestCase):
    def test_haystack_find(self):
        self.assertEqual(searches.describe(7, 10, 2116, (0, 1, 0)),
                         ["Haystack searched: 0-10 = 7, an old, soiled loincloth (the party's 2nd find of 6 in hay)"])

    def test_low_roll_finds_nothing(self):
        self.assertEqual(searches.describe(2, 10, 2116, (0, 0, 0)),
                         ["Haystack searched: 0-10 = 2, nothing (0-2 finds nothing)"])
        self.assertEqual(searches.describe(1, 14, 544, (0, 0, 0)),
                         ["Junk pile searched: 0-14 = 1, nothing (0-1 finds nothing)"])

    def test_six_finds_and_no_more(self):
        """Junk and hay count finds; at 6 every search finds nothing, whatever the roll."""
        line = searches.describe(13, 14, 544, (6, 0, 0))[0]
        self.assertTrue(line.startswith("Junk pile searched: 0-14 = 13, nothing: the party has already found 6 things in junk"))
        self.assertIn("some arrows (the party's 6th find of 6 in junk)", searches.describe(13, 14, 544, (5, 0, 0))[0])
        self.assertIn("nothing: the party has already found 6 things in hay", searches.describe(10, 10, 2116, (0, 7, 0))[0])

    def test_wardrobe_counts_searches(self):
        """Wardrobes count every search, before the roll: the count is this search's number."""
        self.assertEqual(searches.describe(8, 10, 2946, (0, 0, 3)),
                         ["Wardrobe searched: 0-10 = 8, a small gem (the 3rd wardrobe search of 6; after that they are empty)"])
        self.assertEqual(searches.describe(0, 10, 2946, (0, 0, 6)),
                         ["Wardrobe searched: 0-10 = 0, nothing (0-2 finds nothing)"])  # (6 or not: it rolls)

    def test_damage(self):
        self.assertEqual(searches.describe(3, 4, 2452, (0, 0, 0)), ["  The rat's bite: 0-4 = 3 damage"])
        self.assertEqual(searches.describe(5, 5, 3562, (0, 0, 0)), ["  The pot: 0-5 = 5 damage"])

    def test_other_scripts(self):
        """Any other random command, or one at a search's place with another N, isn't a search."""
        self.assertEqual(searches.describe(3, 10, 1234, (0, 0, 0)), [])
        self.assertEqual(searches.describe(3, 9, 2116, (0, 0, 0)), [])
        self.assertEqual(searches.describe(3, 4, 2116, (0, 0, 0)), [])

    def test_every_outcome_named(self):
        for search in (searches.JUNK, searches.HAY, searches.WARDROBE):
            self.assertEqual(sorted(search.outcomes), list(range(search.most + 1)), search.name)


if __name__ == "__main__":
    unittest.main()
