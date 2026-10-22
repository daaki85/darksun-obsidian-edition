import struct
import unittest
from unittest import mock

from dsloader import game, names, spellarrows, weaponchoice


class FakeGame:
    """The bits of GameData SpellArrows asks for: party member 0 a 4th-level Spellarcher."""
    def __init__(self):
        self.slots = {1: 2, 3: 0}
        self.written = []
        self.guest = mock.Mock()
        self.guest.write = lambda at, data: self.written.append((at, data))
        self.guest.read = lambda at, size: bytes((self.slots.get((at - 0x10000 - game.SLOTS_LEFT["Wizard"]) % 0x1E, 0),))
        self.ds = 0x1000

    def class_level(self, member, cls):
        return 4 if cls == game.PRESERVER else 5

    def creature_name(self, member):
        return "Daaki"


class SpellArrowsTests(unittest.TestCase):
    def test_arrows_item(self):
        """A stack of the game's Arrows (type 62) with the spell's name and picture, worth nothing."""
        rec = spellarrows.arrows_item(spellarrows.ARROWS[1], 20)
        self.assertEqual(struct.unpack_from("<H", rec, game.ITEM_TYPE)[0], 62)
        self.assertEqual(struct.unpack_from("<H", rec, game.ITEM_NAME)[0], 0x16D)
        self.assertEqual(struct.unpack_from("<HH", rec, 0), (0x10000 - 2616, 20))
        self.assertEqual(struct.unpack_from("<H", rec, weaponchoice.ITEM_VALUE)[0], 0)
        self.assertTrue(spellarrows.is_arrow(rec))
        self.assertFalse(spellarrows.is_arrow(weaponchoice.arrows(spellarrows.TEMPLATE)))

    def test_names(self):
        """The four names, 15 letters at most, after the amulet's in DSCLOG's table."""
        self.assertEqual([names.NAMES[a.name] for a in spellarrows.ARROWS],
                         [b"Burning Arrows", b"Chill Arrows", b"Shocking Arrows", b"Vampiric Arrows"])
        self.assertTrue(all(len(n) <= 15 for n in spellarrows.NAMES.values()))
        self.assertEqual(max(names.NAMES), names.OWN + names.EXTRA - 1)

    def test_offers_and_make(self):
        """Offered: the touch spells known with a slot of their level left, once till a rest; made:
        5 arrows a preserver level, a slot used."""
        gd = FakeGame()
        known = {1, 3, 39}
        arrows = spellarrows.SpellArrows()
        with mock.patch.object(spellarrows, "is_spellarcher", lambda gd, m: m == 0), \
                mock.patch.object(spellarrows, "knows", lambda gd, m, s: s in known), \
                mock.patch.object(spellarrows, "carries_arrows", lambda gd, m: False), \
                mock.patch.object(spellarrows.npcitems, "add_to", return_value=True) as add:
            self.assertEqual(arrows.offers(gd, 0), 0b0011)  # (Vampiric Touch: no 3rd-level slot left)
            self.assertEqual(arrows.offers(gd, 1), 0)
            done = arrows.make(gd, 0, 1)
            self.assertIn("20 chill arrows", done.text)
            rec = add.call_args[0][2]
            self.assertEqual(struct.unpack_from("<HH", rec, 0)[1], 20)
            self.assertEqual(gd.written[-1][1], bytes((1,)))  # (a 1st-level slot used: 2 to 1)
            self.assertEqual(arrows.offers(gd, 0), 0)  # (once till a rest)
            self.assertIn("No spell arrows", arrows.make(gd, 0, 0).text)
            with mock.patch.object(spellarrows, "vanish", return_value=[]):
                arrows.rest(gd)
            self.assertEqual(arrows.offers(gd, 0), 0b0011)
            self.assertIn("No spell arrows", arrows.make(gd, 0, 3).text)  # (not offered)

    def test_made_before_a_load(self):
        """A Spellarcher already carrying spell arrows counts as having made them."""
        gd = FakeGame()
        arrows = spellarrows.SpellArrows()
        with mock.patch.object(spellarrows, "is_spellarcher", lambda gd, m: True), \
                mock.patch.object(spellarrows, "knows", lambda gd, m, s: True), \
                mock.patch.object(spellarrows, "carries_arrows", lambda gd, m: True):
            self.assertEqual(arrows.offers(gd, 0), 0)


if __name__ == "__main__":
    unittest.main()
