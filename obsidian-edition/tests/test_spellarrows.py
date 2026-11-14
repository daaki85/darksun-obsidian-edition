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

    def _worn(self, member):  # (what's in the quiver: QUIVER, or nothing; and the pack: PACK)
        if getattr(self, "quiver", None) is not None:  # (True: plain arrows; else the arrow's name, a count)
            rec = bytearray(game.ITEM_SIZE)
            rec[game.ITEM_SLOT] = weaponchoice.AMMO_SLOT
            if self.quiver is not True:
                struct.pack_into("<H", rec, game.ITEM_NAME, self.quiver[0])
                struct.pack_into("<H", rec, weaponchoice.ITEM_COUNT, self.quiver[1])
            else:
                struct.pack_into("<H", rec, game.ITEM_NAME, 0x36)
            yield 9, bytes(rec), b""
        for index, (name, count) in getattr(self, "pack", {}).items():  # (item number: the arrow's name, a count)
            rec = bytearray(game.ITEM_SIZE)
            rec[game.ITEM_SLOT] = 20
            struct.pack_into("<H", rec, game.ITEM_NAME, name)
            struct.pack_into("<H", rec, weaponchoice.ITEM_COUNT, count)
            yield index, bytes(rec), b""


class CastSoundTests(unittest.TestCase):
    def test_cast_sound_is_the_spells_own(self):
        gd = mock.Mock()
        gd.spell_record = lambda spell: bytes(range(32)) if spell == spellarrows.ARROWS[1].spell else b""
        self.assertEqual(spellarrows.cast_sound(gd, 1), spellarrows.CAST_SOUND)  # (byte 0Fh of the record)
        self.assertEqual(spellarrows.cast_sound(gd, 0), 0)  # (no record: none)
        self.assertEqual(spellarrows.cast_sound(gd, 9), 0)  # (no such arrows)


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

    def patched(self, add_to=True):
        return (mock.patch.object(spellarrows, "is_spellarcher", lambda gd, m: m == 0),
                mock.patch.object(spellarrows, "knows", lambda gd, m, s: s in {1, 3, 10, 39}),
                mock.patch.object(spellarrows, "item_address", lambda gd, index: 0x50000 + index * game.ITEM_SIZE),
                mock.patch.object(spellarrows.weaponchoice, "bow_ahead"),
                mock.patch.object(spellarrows.npcitems, "add_to", return_value=add_to))

    def count_written(self, gd, index, n):
        return (0x50000 + index * game.ITEM_SIZE + weaponchoice.ITEM_COUNT, struct.pack("<H", n)) in gd.written

    def test_make(self):
        """A Spellarcher's button, its quiver empty: a slot of the spell's level used for one arrow,
        a new stack of it in the quiver (the bow put ahead of it); none for a spell it doesn't know,
        without a slot, or for one not a Spellarcher."""
        gd = FakeGame()
        arrows = spellarrows.SpellArrows()
        a, b, c, ahead, add = self.patched()
        with a, b, c, ahead as ahead, add as add:
            done = arrows.make(gd, 0, 1)
            self.assertEqual(done.text, "")  # (no window)
            self.assertIn("makes one of the chill arrows in the quiver (1 of 24 now)", done.log[0])
            self.assertIn("lasts until shot", done.log[0])
            rec = add.call_args[0][2]
            self.assertEqual(struct.unpack_from("<HH", rec, 0)[1], spellarrows.ARROWS_A_SLOT)
            self.assertEqual(add.call_args[0][3], weaponchoice.AMMO_SLOT)  # (in the quiver)
            ahead.assert_called_with(gd, 0)
            self.assertEqual(gd.written[-1][1], bytes((1,)))  # (a 1st-level slot used: 2 to 1)
            self.assertIn("no 3rd-level spell left", arrows.make(gd, 0, 3).text)
            self.assertIn("can't weave", arrows.make(gd, 1, 1).text)  # (not a Spellarcher)
            self.assertEqual(add.call_count, 1)

    def test_make_onto_the_stack(self):
        """The spell's own stack, in the quiver or the pack: one more on it, a slot used; at
        STACK_MOST none, the slot kept."""
        for where in ("quiver", "pack"):
            gd = FakeGame()
            chill = spellarrows.ARROWS[1]
            if where == "quiver":
                gd.quiver, index = (chill.name, 7), 9
            else:
                gd.quiver, gd.pack, index = True, {30: (chill.name, 7)}, 30
            arrows = spellarrows.SpellArrows()
            a, b, c, ahead, add = self.patched()
            with self.subTest(where=where), a, b, c, ahead, add as add:
                done = arrows.make(gd, 0, 1)
                self.assertEqual(done.text, "")
                self.assertIn("makes one of the chill arrows (8 of 24 now)", done.log[0])
                self.assertTrue(self.count_written(gd, index, 8))
                self.assertEqual(gd.written[-1][1], bytes((1,)))  # (a 1st-level slot used)
                self.assertEqual(add.call_count, 0)
                gd.written.clear()
                if where == "quiver":
                    gd.quiver = (chill.name, spellarrows.STACK_MOST)
                else:
                    gd.pack = {30: (chill.name, spellarrows.STACK_MOST)}
                self.assertIn("chill arrows are a full stack (24)", arrows.make(gd, 0, 1).text)
                self.assertEqual(gd.written, [])

    def test_make_into_the_pack(self):
        """No stack of the spell's and something else in the quiver (other arrows, another spell's):
        a new stack in the pack, the quiver as it is."""
        for quiver in (True, (spellarrows.ARROWS[1].name, 5)):
            gd = FakeGame()
            gd.quiver = quiver
            arrows = spellarrows.SpellArrows()
            a, b, c, ahead, add = self.patched()
            with self.subTest(quiver=quiver), a, b, c, ahead as ahead, add as add:
                done = arrows.make(gd, 0, 0)  # (Burning Hands)
                self.assertIn("makes one of the burning arrows in the pack (1 of 24 now)", done.log[0])
                self.assertIsNone(add.call_args[0][3])  # (a backpack cell)
                ahead.assert_not_called()

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
