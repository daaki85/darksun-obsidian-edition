"""Every description the Loader writes for the game's spell box fits it: seven lines (an eighth
spills over the box's edge, as Chaos's did, 2026-11-10). The box wraps at word breaks to 128 pixels
of the game's font, the first line less the spell's icon (19 to 28 pixels: both are tried); measured
from Chaos's and Strength's boxes in the game."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dsloader import art, gff, spelltexts  # noqa: E402

BOX_WIDTH, ICON_WIDTHS, BOX_LINES = 128, (19, 28), 7


def wrap(text, width, font, indent):
    def size(s):
        return sum(font.glyph(c)[0] for c in s)
    lines, line = [], ""
    for word in text.split(" "):
        longer = f"{line} {word}" if line else word
        if line and size(longer) > width - (0 if lines else indent):
            lines.append(line)
            line = word
        else:
            line = longer
    return lines + [line]


@unittest.skipUnless(os.environ.get("DSUN_RESOURCE"), "DSUN_RESOURCE (the game's RESOURCE.GFF) not given")
class FitTests(unittest.TestCase):
    def setUp(self):
        with open(os.environ["DSUN_RESOURCE"], "rb") as f:
            self.font = art.Font(gff.read_gff(f.read())[("FONT", art.FONT_ID)])

    def test_the_measure(self):
        """The two boxes seen in the game, wrapped as they were."""
        chaos = ("CHAOS:  Affects 1 to 4 creatures plus 1 per caster level: only warriors and the very "
                 "clever or very dull may save. They may stand confused, go berserk, or flee.")
        for indent in ICON_WIDTHS:
            self.assertEqual(wrap(chaos, BOX_WIDTH, self.font, indent)[-2:], ["confused, go berserk, or", "flee."])
            self.assertEqual(wrap(spelltexts.MANUAL_TEXTS[24], BOX_WIDTH, self.font, indent)[4],
                             "psionicists 1 to 6, wizards")

    def test_every_text_fits(self):
        for table in (spelltexts.TEXTS, spelltexts.MANUAL_TEXTS, spelltexts.SIZE_TEXTS):
            for key, text in table.items():
                for indent in ICON_WIDTHS:
                    with self.subTest(key=key, indent=indent):
                        self.assertLessEqual(len(wrap(text, BOX_WIDTH, self.font, indent)), BOX_LINES, text)


if __name__ == "__main__":
    unittest.main()
