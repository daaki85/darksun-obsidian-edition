"""Mirlon's tools for a thief leader who takes his deal (mirlon.py): his script's reply "It's a
deal!" goes first to his words and the Loader's flag, while the Loader's OFFER is set; the Loader
keeps OFFER and, once the flag is set, moves his own set into the leader's pack."""

import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import gpl, mirlon as m

FIELDS = bytes(72) + b"\x10" + bytes(16)
ESCAPE = "  Let's talk escape."


def his():
    """A script shaped as his: the menu (two replies), "Good luck!" and its return."""
    def menu(good):
        return (0x48, [{"before": [], "title": ("var", 134, 1), "replies": [
            {"text": ("str", ESCAPE), "goto": ("n", good), "if": ("var", 142, 4), "before": [], "after": []},
            {"text": ("str", m.DEAL), "goto": ("n", good), "if": ("var", 142, 16), "before": [], "after": []}]}])
    good = len(gpl.encode_op(menu(0)))
    return gpl.encode_op(menu(good)) + gpl.encode_op((0x4F, [("n", 115), ("str", "Good luck! ")])) \
        + gpl.encode_op((0x15, [])), good


class ScriptTests(unittest.TestCase):
    def setUp(self):
        self.script, self.good = his()
        self.out = m.with_tools(self.script, FIELDS)

    def test_the_deal_goes_to_the_new_code(self):
        menu = gpl.decode(self.out, FIELDS)[0].args[0]
        gotos = {r["text"][1]: r["goto"] for r in menu["replies"]}
        self.assertEqual(gotos, {ESCAPE: ("n", self.good), m.DEAL: ("n", len(self.script))})
        self.assertEqual(self.out[self.good:len(self.script)], self.script[self.good:])

    def test_the_new_code(self):
        """While OFFER: his words, a click, GIVEN set; then on to "Good luck!"."""
        r = gpl._Reader(self.out, FIELDS)
        r.i = len(self.script)
        ops = []
        while r.i < len(self.out):
            ops.append(gpl._op(r))
        self.assertEqual((ops[0].code, ops[0].args), (0x18, [("expr", [("var", m.FLAG_READ, m.OFFER), "==", ("n", 1)])]))
        said = " ".join(o.args[1][1] for o in ops if o.code == 0x4F and o.args[1][0] == "str")
        self.assertEqual(" ".join(said.split()), m.WORDS)
        self.assertIn((0x16, [("n", 1), ("var", 13, m.GIVEN)]), [(o.code, o.args) for o in ops])
        self.assertEqual((ops[-1].code, ops[-1].args), (0x64, [("n", self.good)]))
        self.assertEqual(ops[-2].code, 0x67)

    def test_once_and_only_his(self):
        self.assertEqual(m.with_tools(self.out, FIELDS), self.out)
        other = gpl.encode_op((0x4F, [("n", 115), ("str", "Hello. ")]))
        self.assertEqual(m.with_tools(other, FIELDS), other)


class FakeGame:
    def __init__(self, leader=0, talking=m.NAME):
        self.flags = set()
        self.leader, self.talking = leader, talking

    def region(self):
        return m.PENS

    def whose_turn(self):
        return self.leader

    def talk_target(self):
        return self.talking

    def flag(self, n):
        return n in self.flags

    def set_flag(self, n, on=True):
        (self.flags.add if on else self.flags.discard)(n)

    def creature_name(self, index):
        return "Kage"


class WatchTests(unittest.TestCase):
    def watch(self, gd, thief=True, held=(0, 7, -1), cell=15):
        moved = []
        with mock.patch.object(m, "_mirlon", lambda gd: 9), mock.patch.object(m.ring, "Items", lambda gd: None), \
                mock.patch.object(m, "_his_tools", lambda gd, it, c: held), mock.patch.object(m, "is_thief", lambda gd, n: thief), \
                mock.patch.object(m.pickpocket, "free_cell", lambda gd, it, n: cell), \
                mock.patch.object(m.pickpocket, "_take", lambda gd, it, c, l, i, b: moved.append(("take", c, i))), \
                mock.patch.object(m.pickpocket, "give", lambda gd, it, n, i, c: moved.append(("give", n, i, c)) or True):
            return m.watch(gd), moved

    def test_offer(self):
        """OFFER while the leader is a thief and he holds the tools."""
        gd = FakeGame()
        self.assertEqual(self.watch(gd), ([], []))
        self.assertTrue(gd.flag(m.OFFER))
        self.watch(gd, thief=False)
        self.assertFalse(gd.flag(m.OFFER))
        self.watch(gd, held=None)
        self.assertFalse(gd.flag(m.OFFER))

    def test_given(self):
        """GIVEN: his set moved to the leader's pack, once, while he talks."""
        gd = FakeGame(leader=2)
        gd.flags |= {m.OFFER, m.GIVEN}
        lines, moved = self.watch(gd)
        self.assertEqual(lines, ["Mirlon gives Kage his Thieves' Tools"])
        self.assertEqual(moved, [("take", 9, 7), ("give", 2, 7, 15)])
        self.assertTrue(gd.flag(m.MOVED))
        self.assertFalse(gd.flag(m.OFFER))
        self.assertEqual(self.watch(gd), ([], []))

    def test_not_while_he_isnt_talking_or_no_room(self):
        gd = FakeGame(talking=None)
        gd.flags.add(m.GIVEN)
        self.assertEqual(self.watch(gd), ([], []))
        gd.talking = m.NAME
        self.assertEqual(self.watch(gd, cell=None), ([], []))
        self.assertFalse(gd.flag(m.MOVED))


if __name__ == "__main__":
    unittest.main()
