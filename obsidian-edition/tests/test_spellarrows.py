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

    def no_spells(self, member):  # (in armour: ARMOURED)
        return getattr(self, "armoured", False)

    def _worn(self, member):  # (what's in the quiver: QUIVER, or nothing)
        if getattr(self, "quiver", None) is not None:  # (True: plain arrows; else the arrow's name, a count)
            rec = bytearray(game.ITEM_SIZE)
            rec[game.ITEM_SLOT] = weaponchoice.AMMO_SLOT
            if self.quiver is not True:
                struct.pack_into("<H", rec, game.ITEM_NAME, self.quiver[0])
                struct.pack_into("<H", rec, weaponchoice.ITEM_COUNT, self.quiver[1])
            yield 9, bytes(rec), b""


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

    def test_make(self):
        """A Spellarcher's button: a slot of the spell's level used, 5 arrows a preserver level in
        its quiver (then the bow put ahead of them); as often as slots are left; none for a spell it
        doesn't know or without a slot."""
        gd = FakeGame()
        known = {1, 3, 39}
        arrows = spellarrows.SpellArrows()
        with mock.patch.object(spellarrows, "is_spellarcher", lambda gd, m: m == 0), \
                mock.patch.object(spellarrows, "knows", lambda gd, m, s: s in known), \
                mock.patch.object(spellarrows.weaponchoice, "bow_ahead") as ahead, \
                mock.patch.object(spellarrows.npcitems, "add_to", return_value=True) as add:
            done = arrows.make(gd, 0, 1)
            self.assertEqual(done.text, "")  # (no window)
            self.assertIn("20 chill arrows", done.log[0])
            rec = add.call_args[0][2]
            self.assertEqual(struct.unpack_from("<HH", rec, 0)[1], 20)
            self.assertEqual(add.call_args[0][3], weaponchoice.AMMO_SLOT)  # (in the quiver)
            ahead.assert_called_with(gd, 0)
            self.assertEqual(gd.written[-1][1], bytes((1,)))  # (a 1st-level slot used: 2 to 1)
            self.assertIn("20 burning arrows", arrows.make(gd, 0, 0).log[0])  # (again: a slot left)
            self.assertIn("can't weave Shocking Grasp", arrows.make(gd, 0, 2).text)  # (not known)
            self.assertIn("no 3rd-level spell left", arrows.make(gd, 0, 3).text)
            self.assertIn("can't weave", arrows.make(gd, 1, 1).text)  # (not a Spellarcher)
            self.assertEqual(add.call_count, 2)

    def test_make_more_of_the_same(self):
        """The same spell's arrows in the quiver: as many more added to their count, a slot used;
        another spell's arrows: none, the slot kept."""
        gd = FakeGame()
        chill = spellarrows.ARROWS[1]
        gd.quiver = (chill.name, 7)
        arrows = spellarrows.SpellArrows()
        with mock.patch.object(spellarrows, "is_spellarcher", return_value=True), \
                mock.patch.object(spellarrows, "knows", return_value=True), \
                mock.patch.object(spellarrows, "item_address", lambda gd, index: 0x50000 + index * game.ITEM_SIZE), \
                mock.patch.object(spellarrows.npcitems, "add_to", return_value=True) as add:
            done = arrows.make(gd, 0, 1)
            self.assertEqual(done.text, "")
            self.assertIn("makes 20 chill arrows (5 a preserver level, 4), 27 in the quiver now", done.log[0])
            self.assertIn((0x50000 + 9 * game.ITEM_SIZE + weaponchoice.ITEM_COUNT, struct.pack("<H", 27)), gd.written)
            self.assertEqual(gd.written[-1][1], bytes((1,)))  # (a 1st-level slot used)
            self.assertEqual(add.call_count, 0)
            gd.written.clear()
            other = arrows.make(gd, 0, 0)  # (Burning Hands, with chill arrows in the quiver)
            self.assertIn("must be empty, or hold burning arrows", other.text)
            self.assertEqual(gd.written, [])
            gd.quiver = (chill.name, spellarrows.MOST_ARROWS - 5)
            self.assertIn("holds no more chill arrows", arrows.make(gd, 0, 1).text)
            self.assertEqual(gd.written, [])

    def test_make_quiver_full(self):
        """Anything else in the quiver: no arrows, and the slot kept."""
        gd = FakeGame()
        gd.quiver = True
        arrows = spellarrows.SpellArrows()
        with mock.patch.object(spellarrows, "is_spellarcher", return_value=True), \
                mock.patch.object(spellarrows, "knows", return_value=True), \
                mock.patch.object(spellarrows.npcitems, "add_to", return_value=True) as add:
            done = arrows.make(gd, 0, 1)
        self.assertIn("quiver must be empty", done.text)
        self.assertEqual(add.call_count, 0)
        self.assertEqual(gd.written, [])

    def test_make_in_armour(self):
        """In armour a Spellarcher casts nothing (restrict.no_spells), so it weaves no arrows: the
        slot kept."""
        gd = FakeGame()
        gd.armoured = True
        arrows = spellarrows.SpellArrows()
        with mock.patch.object(spellarrows, "is_spellarcher", return_value=True), \
                mock.patch.object(spellarrows, "knows", return_value=True), \
                mock.patch.object(spellarrows.npcitems, "add_to", return_value=True) as add:
            done = arrows.make(gd, 0, 1)
        self.assertIn("in armour", done.text)
        self.assertEqual(add.call_count, 0)
        self.assertEqual(gd.written, [])


if __name__ == "__main__":
    unittest.main()
