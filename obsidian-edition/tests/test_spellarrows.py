import struct
import unittest
from unittest import mock

from dsloader import game, names, spellarrows, weaponchoice


class FakeGame:
    """The bits of GameData SpellArrows asks for: party member 0 a 4th-level Spellarcher."""
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

    def test_cast_makes_arrows(self):
        """An arrow spell cast by a party member: 5 arrows a preserver level in its backpack in the
        next pass (the game has used the slot); others' casts, and other spells, nothing."""
        gd = FakeGame()
        arrows = spellarrows.SpellArrows()
        arrows.cast(0, 203)
        arrows.cast(7, 203)  # (not a party member)
        arrows.cast(0, 3)  # (Chill Touch itself)
        with mock.patch.object(spellarrows.npcitems, "add_to", return_value=True) as add:
            lines = arrows.made(gd)
            self.assertEqual(len(lines), 1)
            self.assertIn("Daaki makes 20 chill arrows", lines[0])
            self.assertEqual(add.call_args[0][1], 0)
            rec = add.call_args[0][2]
            self.assertEqual(struct.unpack_from("<HH", rec, 0)[1], 20)
            self.assertEqual(struct.unpack_from("<H", rec, game.ITEM_NAME)[0], 0x16D)
            self.assertEqual(arrows.made(gd), [])
        arrows.cast(0, 205)
        with mock.patch.object(spellarrows.npcitems, "add_to", return_value=False):
            self.assertIn("no room", arrows.made(gd)[0])

    def test_arrow_spells(self):
        """The arrow spells' numbers and names as the game has them (game.ARROW_SPELLS)."""
        self.assertEqual({a.cast: game.ARROW_SPELLS[a.cast] for a in spellarrows.ARROWS},
                         {202: "Burning Arrows", 203: "Chill Arrows", 204: "Shocking Arrows", 205: "Vampiric Arrows"})
        self.assertEqual([a.level for a in spellarrows.ARROWS], [1, 1, 1, 3])


if __name__ == "__main__":
    unittest.main()
