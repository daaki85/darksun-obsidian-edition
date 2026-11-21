"""The spells' descriptions changed with the rules (spelltexts.py): the manual's (Spells and psionics
as the manual describes them) and Hold and Charm Person's (Creature size as in AD&D), each short enough for the description box (no longer than the game's own longest, 163 characters:
seven lines fill the box, an eighth spills over its edge)."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import spelltexts  # noqa: E402

GAME_LONGEST = 163  # (the longest of the game's own descriptions, RESOURCE.GFF's SPIN chunks)


class RuleTextsTests(unittest.TestCase):
    def test_each_its_own(self):
        """Every text in the chunks, each rule's in its spell's place: the two rules' texts for
        different spells, so neither hides the other."""
        chunks = spelltexts.chunks()
        self.assertFalse(set(spelltexts.MANUAL_TEXTS) & set(spelltexts.SIZE_TEXTS))
        for texts in (spelltexts.MANUAL_TEXTS, spelltexts.SIZE_TEXTS):
            for n, text in texts.items():
                self.assertEqual(chunks[("SPIN", n)], text.encode("ascii") + b"\r\n")
        self.assertTrue(set(spelltexts.TEXTS) <= {n for _, n in chunks})
        self.assertIn(b"man-sized", chunks[("SPIN", 31)])  # (Hold Person)

    def test_fit_the_box(self):
        for texts in (spelltexts.MANUAL_TEXTS, spelltexts.SIZE_TEXTS):
            for n, text in texts.items():
                self.assertLessEqual(len(text), GAME_LONGEST, (n, text))
                self.assertTrue(text.isascii(), n)

    def test_under_the_byte_limit(self):
        """Every SPIN chunk the copy has under the box's 195 bytes (it reads 200, from its 5th
        byte), as TEXTS' and MANUAL_TEXTS' own tests check theirs."""
        for key, chunk in spelltexts.chunks().items():
            self.assertLess(len(chunk), 195, key)
        self.assertTrue(all(len(t.encode("ascii")) + 2 < 195 for t in spelltexts.SIZE_TEXTS.values()))


if __name__ == "__main__":
    unittest.main()
