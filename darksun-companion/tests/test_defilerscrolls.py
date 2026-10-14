"""Defilers' scrolls (defilerscrolls.py): a defiler in a fight carries a preserver scroll at CHANCE in
100, rolled once a fight; the scroll is the game's own kind, of its first scroll object."""

import os
import struct
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dscompanion import defilerscrolls as ds, game, kalzith


def creature(name: bytes, hp: int = 20, status: int = 1) -> bytes:
    rec = bytearray(game.CREATURE_SIZE)
    struct.pack_into("<h", rec, 0, hp)
    rec[game.CREATURE_STATUS] = status
    rec[game.CREATURE_NAME:game.CREATURE_NAME + len(name) + 1] = name + b"\0"
    return bytes(rec)


class FakeGame:
    """Creatures after the party: 4 a Defiler, 5 a Slig, 6 Kalzith, 7 a dead Dark Spider, 8 a Dark
    Spider; their sheets' classes (18 the defilers')."""

    def __init__(self):
        self.fighting = True
        self.area = 0x2F
        recs = [creature(b"Party")] * game.PARTY_SIZE + [
            creature(b"Defiler"), creature(b"Slig"), creature(b"Kalzith"),
            creature(b"Dark Spider", hp=0, status=5), creature(b"Dark Spider")]
        self.table = b"".join(recs)
        self.classes = {4: 18, 5: 0, 6: 18, 7: 18, 8: 18}

    def in_combat(self):
        return self.fighting

    def region(self):
        return self.area

    def creatures(self, count):
        return self.table[:count * game.CREATURE_SIZE]

    def sheet(self, index):
        sheet = bytearray(game.SHEET_SIZE)
        sheet[game.SHEET_CLASSES] = self.classes.get(index, 9)
        return bytes(sheet)

    def creature(self, index):
        return self.table[index * game.CREATURE_SIZE:(index + 1) * game.CREATURE_SIZE]

    def spell_level(self, spell):
        return {9: 1, 36: 3}.get(spell, 2) if spell < 69 else (1 if spell in (196, 197, 198) else 0)

    def spell_name(self, spell):
        return {9: "Shield", 36: "Hold Person"}.get(spell, f"spell {spell}")


class Watch(ds.DefilerScrolls):
    carrying = ()

    def _carries_one(self, gd, index):
        return index in self.carrying


class DefilerScrollTests(unittest.TestCase):
    def setUp(self):
        self.gd = FakeGame()
        self.given = []
        patch = mock.patch.object(ds.npcitems, "add_to", lambda gd, index, rec, slot=None: self.given.append((index, rec)) or True)
        patch.start()
        self.addCleanup(patch.stop)

    def test_scroll_item(self):
        """The game's scroll kind: its first scroll object (1400, which teaches), the spell one past
        its number, 3000 a level."""
        rec = ds.scroll(36, 3)
        self.assertEqual(struct.unpack_from("<h", rec, kalzith.ITEM_OBJECT)[0], -1400)
        self.assertEqual(struct.unpack_from("<H", rec, kalzith.ITEM_SPELL)[0], 37)
        self.assertEqual(struct.unpack_from("<H", rec, kalzith.ITEM_VALUE)[0], 9000)
        self.assertTrue(ds.is_ours(rec))
        self.assertFalse(ds.is_ours(kalzith.scroll(9, 3000, 0)))  # (Kalzith's own)

    def test_spells(self):
        """The game's 69 wizard spells, and the new ones the game has set up while their rule is on."""
        levels = self.gd.spell_level
        self.assertEqual(ds.spells(levels, False), list(range(69)))
        self.assertEqual(ds.spells(levels, True), list(range(69)) + [196, 197, 198])

    def test_roll_once_a_fight(self):
        """In a fight: the Defiler and the living Dark Spider rolled for, once; not the Slig, nor
        Kalzith, nor the dead one; a roll of 5 or less gives a scroll."""
        rolls = iter([5, 6])
        w = Watch()
        lines = w.watch(self.gd, False, roll=lambda: next(rolls), choose=lambda pool: 36)
        self.assertEqual(lines, ["Defiler's scroll: d100 = 5, needs 5 or less -> a scroll of Hold Person, "
                                 "dropped where Defiler falls",
                                 "Dark Spider's scroll: d100 = 6, needs 5 or less -> none"])
        self.assertEqual([index for index, _ in self.given], [4])
        self.assertEqual(struct.unpack_from("<H", self.given[0][1], kalzith.ITEM_SPELL)[0], 37)
        self.assertEqual(w.watch(self.gd, False, roll=lambda: 1), [])  # (rolled: not again)

    def test_not_out_of_a_fight(self):
        self.gd.fighting = False
        self.assertEqual(Watch().watch(self.gd, False, roll=lambda: 1), [])

    def test_again_after_a_load(self):
        """A game loaded: rolled again (a death played again)."""
        w = Watch()
        w.watch(self.gd, False, roll=lambda: 50)
        w.reset()
        self.assertEqual(len(w.watch(self.gd, False, roll=lambda: 50)), 2)

    def test_one_already(self):
        """One already carried (a save made mid-fight): no roll, no second."""
        w = Watch()
        w.carrying = (4,)
        lines = w.watch(self.gd, False, roll=lambda: 1, choose=lambda pool: 9)
        self.assertEqual([line.split("'s")[0] for line in lines], ["Dark Spider"])
        self.assertEqual([index for index, _ in self.given], [8])


if __name__ == "__main__":
    unittest.main()
