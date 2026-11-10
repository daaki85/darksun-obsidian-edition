"""The spells' descriptions changed with the rules (spelltexts.py): the manual's only with "Spells and
psionics as the manual describes them", Hold and Charm Person's only with "Creature size as in AD&D",
each short enough for the description box (no longer than the game's own longest, 163 characters:
seven lines fill the box, an eighth spills over its edge)."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import spelltexts  # noqa: E402

GAME_LONGEST = 163  # (the longest of the game's own descriptions, RESOURCE.GFF's SPIN chunks)


class RuleTextsTests(unittest.TestCase):
    def test_by_switch(self):
        plain = spelltexts.chunks(False, False)
        manual = spelltexts.chunks(True, False)
        size = spelltexts.chunks(False, True)
        for n in spelltexts.MANUAL_TEXTS:
            self.assertIn(("SPIN", n), manual)
            self.assertEqual(size.get(("SPIN", n)), plain.get(("SPIN", n)))
        for n in spelltexts.SIZE_TEXTS:
            self.assertIn(("SPIN", n), size)
            self.assertNotIn(("SPIN", n), manual)
        self.assertIn(b"man-sized", size[("SPIN", 31)])  # (Hold Person)

    def test_fit_the_box(self):
        for texts in (spelltexts.MANUAL_TEXTS, spelltexts.SIZE_TEXTS):
            for n, text in texts.items():
                self.assertLessEqual(len(text), GAME_LONGEST, (n, text))
                self.assertTrue(text.isascii(), n)


if __name__ == "__main__":
    unittest.main()
