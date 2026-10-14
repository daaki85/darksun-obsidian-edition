"""The Elven Leader gives the Cloak of Elvenkind after his Gythka (elvenleader.py), on a script
shaped as his: the gift's lines, the give or the drop, the click, the talk going on."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import elvenleader as e, gpl
from dsloader.kalzith import MORE, _Script

FIELDS = bytes(72) + b"\x10" + bytes(16)


def his():
    s = _Script()
    s.op(0x4F, ("n", 115), ("str", "You are true warriors! "))
    s.op(0x4F, ("n", 115), e.GIFT)
    give = ("op", gpl.Op(0, e.GIVE, [("n", 1), ("n", -2534), e.ACTOR, ("n", -e.LEADER)]))
    s.op(e.TEST, ("expr", ["(", give, ")", "==", ("n", 0)]))
    s.op(e.IF_NOT, ("label", "given"))
    s.op(0x4F, ("n", 115), ("str", "You can't carry it, so I'll leave it here for you. "))
    s.op(e.HERE, ("n", -e.LEADER))
    s.op(e.DROP, ("n", -2534), ("n", 1), e.AT_X, e.AT_Y, ("n", 6), ("n", 0))
    s.label("given")
    s.op(e.END_IF)
    s.op(0x4F, ("n", e.NARRATE), MORE)
    s.label("on")
    s.op(0x4F, ("n", 115), ("str", "Well, now that that is out of the way... "))
    return s.bytes(end=True)


def added(script, out):
    r = gpl._Reader(out, FIELDS)
    r.i = len(script)
    ops = []
    while r.i < len(out):
        ops.append(gpl._op(r))
    return ops


class ElvenLeaderTests(unittest.TestCase):
    def setUp(self):
        self.script = his()
        self.out = e.with_cloak(self.script, FIELDS)
        self.ops = gpl.decode(self.script, FIELDS)
        self.added = added(self.script, self.out)

    def test_the_click_jumps_to_the_cloak(self):
        click = next(o for o in self.ops if o.code == 0x4F and o.args == [("n", e.NARRATE), MORE])
        r = gpl._Reader(self.out, FIELDS)
        r.i = click.at
        jump = gpl._op(r)
        self.assertEqual((jump.code, jump.args), (0x64, [("n", len(self.script))]))
        self.assertEqual(self.out[:click.at], self.script[:click.at])

    def test_the_cloak_given_or_left(self):
        gives = [o for o in self.added if o.code == e.TEST]
        self.assertEqual(len(gives), 1)
        self.assertIn("Op(at=", str(gives[0].args))
        self.assertIn("('n', -2546), ('var', 137, 37), ('n', 9999)", str(gives[0].args))
        drop = next(o for o in self.added if o.code == e.DROP)
        self.assertEqual(drop.args[0], ("n", -e.CLOAK))
        lines = " ".join(gpl.strings(self.added))
        self.assertIn("And take this cloak", lines)
        self.assertIn("You can't carry this either", lines)

    def test_back_after_the_click(self):
        """Then the click, and back to where the game's goes on."""
        on = next(o for o in self.ops if o.code == 0x4F and o.args[1] == ("str", "Well, now that that is out of the way... "))
        self.assertEqual([(o.code, o.args) for o in self.added[-2:]], [(0x4F, [("n", e.NARRATE), MORE]), (0x64, [("n", on.at)])])

    def test_once(self):
        self.assertEqual(e.with_cloak(self.out, FIELDS), self.out)

    def test_other_script_unchanged(self):
        s = _Script()
        s.op(0x4F, ("n", 115), ("str", "Hello. "))
        script = s.bytes(end=True)
        self.assertEqual(e.with_cloak(script, FIELDS), script)
        self.assertEqual(e.script_chunks({("GPL ", 45): script}, FIELDS), {})


if __name__ == "__main__":
    unittest.main()
