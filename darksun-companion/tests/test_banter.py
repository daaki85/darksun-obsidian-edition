"""Banter between recruits (banter.py): its tests, its lines, its place in scripts, and the
Ledger's in-the-party flags."""

import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))

from dscompanion import banter, game, gpl, recruits
from dscompanion.kalzith import _Script
from test_dicelog import CREATURES, DS, LOAD_SEG, make_game

FLAGS = 0x60000


def ops(data: bytes):
    return gpl.decode(data, b"")


class ScriptTests(unittest.TestCase):
    def test_play(self):
        """Once (its flag), only with its recruits in the party; each line with its speaker's
        portrait and name, then the talk's portrait back."""
        s = _Script()
        banter.play(s, banter.KALZITH, 61)
        out = ops(s.bytes())
        test = out[0].args[0][1]
        self.assertEqual(test[:5], ["(", ("var", 0x8D, banter.KALZITH.flag), "==", ("n", 0), ")"])
        for r in (recruits.SEMYON, recruits.TORVAK):
            self.assertIn(("var", 0x8D, banter.IN_PARTY[r.number]), test)
        portraits = [o.args[0][1] for o in out if o.code == 0x54]
        self.assertEqual(portraits, [banter.PORTRAITS[w.number] for w, _ in banter.KALZITH.lines] + [61])
        self.assertIn(gpl.encode_op((0x16, [("n", 1), ("var", 13, banter.KALZITH.flag)])), s.bytes())
        text = " ".join(str(a[1]) for o in out if o.code == 0x4F for a in o.args if a[0] == "str")
        self.assertIn("Torvak:", text)
        self.assertIn("Semyon:", text)

    def test_meeting_needs_only_torvak(self):
        """Semyon's joining banter: Semyon has just joined (no flag yet), so only Torvak's."""
        self.assertEqual(banter.MEETING.needs, (recruits.TORVAK,))

    def test_with_banter_once(self):
        master = gpl.encode([(0x16, [("n", 0), ("var", 7, 3)]), (0x31, [])])
        once = banter.with_banter(master, banter.PENS)
        self.assertEqual(banter.with_banter(once, banter.PENS), once)
        self.assertEqual(ops(once)[-1].code, 0x31)
        self.assertTrue(any(o.code == 0x18 for o in ops(once)))

    def test_flags_free(self):
        flags = list(banter.IN_PARTY.values()) + [b.flag for b in banter.BANTERS]
        self.assertEqual(len(set(flags)), len(flags))
        from dscompanion import semyon, torvak
        taken = {semyon.PLACED, semyon.MET, semyon.LEFT, semyon.DIED, torvak.PLACED, torvak.MET}
        self.assertFalse(taken & set(flags))


class PartyTests(unittest.TestCase):
    def setUp(self):
        self.log = make_game()
        m = self.log.guest.mem
        struct.pack_into("<HH", m, (LOAD_SEG + game.FLAGS_SEG) * 16 + game.FLAGS_PTR, FLAGS & 0xF, FLAGS >> 4)
        self.m = m

    def tag(self, slot: int, tag: int, status: int = 1) -> None:
        struct.pack_into("<H", self.m, CREATURES + slot * game.CREATURE_SIZE + 6, tag)
        self.m[(LOAD_SEG + banter.PARTY_SEG) * 16 + banter.STATUS + slot] = status

    def test_in_party_by_tag(self):
        self.tag(1, recruits.TAGS + recruits.TORVAK.number)
        self.tag(2, recruits.TAGS + recruits.SEMYON.number, banter.GONE)  # (dropped)
        self.assertEqual(banter.in_party(self.log.game),
                         {recruits.SEMYON.number: False, recruits.TORVAK.number: True})
        banter.watch(self.log.game)
        self.assertTrue(self.log.game.flag(banter.IN_PARTY[recruits.TORVAK.number]))
        self.assertFalse(self.log.game.flag(banter.IN_PARTY[recruits.SEMYON.number]))
        self.tag(1, 0x8001)  # (gone: the flag cleared)
        banter.watch(self.log.game)
        self.assertFalse(self.log.game.flag(banter.IN_PARTY[recruits.TORVAK.number]))


if __name__ == "__main__":
    unittest.main()
