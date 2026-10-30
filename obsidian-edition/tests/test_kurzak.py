"""Kurzak's lines about Legcrusher ask whether he is on the map (kurzak.py), on scripts shaped as
the game's: his call to the arena, and his talk's cases as the party comes."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import gpl, kurzak as k
from dsloader.kalzith import CLEAR, MORE, _Script

FIELDS = bytes(72) + b"\x10" + bytes(16)
STEP = ("var", 135, 136)


def call():
    """Script 136's call: Kurzak's line, the click and clear, and on."""
    s = _Script()
    s.op(0x4F, ("n", 115), ("str", "You summoned me, so it's time to fight! "))
    s.op(0x4F, ("n", 115), ("str", k.LINES[0][1]))
    s.op(0x4F, ("n", 115), MORE)
    s.op(0x4F, ("n", 115), CLEAR)
    return s.bytes(end=True)


def talk():
    """Script 141's cases: 2 and 3 each two lines, then the crowd waiting."""
    s = _Script()
    s.op(0x17, STEP)
    s.op(0x27, ("n", 2), ("label", "case 3"))
    s.op(0x4F, ("n", 115), ("str", k.LINES[1][1]))
    s.op(0x4F, ("n", 115), ("str", "Legcrusher. "))
    s.label("case 3")
    s.op(0x27, ("n", 3), ("label", "end"))
    s.op(0x4F, ("n", 115), ("str", k.LINES[2][1]))
    s.op(0x4F, ("n", 115), ("str", "I found you. "))
    s.label("end")
    s.op(0x61)
    s.op(0x4F, ("n", 115), ("str", "The crowd is waiting! Get moving!"))
    return s.bytes(end=True)


def strings(ops):
    return [o.args[1][1] for o in ops if o.code == 0x4F and o.args[1][0] == "str"]


class KurzakTests(unittest.TestCase):
    def test_the_call_asks_first(self):
        """The call's line becomes a jump to the test: Legcrusher there, the game's line; gone,
        Kurzak's own; then back to the click after it."""
        script = call()
        out = k.with_notice(script, FIELDS, k.CALL_SCRIPT)
        ops = gpl.decode(out, FIELDS)
        line = gpl.decode(script, FIELDS)[1]
        jump = next(o for o in ops if o.at == line.at)
        self.assertEqual(jump.code, 0x64)
        self.assertEqual(jump.args, [("n", len(script))])
        added = [o for o in ops if o.at >= len(script)]
        self.assertEqual(added[0].code, 0x18)
        where = next(o for o in gpl.walk(added[0].args) if o.code == k.WHERE)
        self.assertEqual(where.args, [("n", -k.KURZAK), ("n", -k.LEGCRUSHER)])
        self.assertEqual(strings(added), [k.LINES[0][1], "Legcrusher! ... Legcrusher? Where has that lump got to? ",
                                          "Gladiators! Get up here yourselves! "])
        self.assertEqual(added[-1].args, [("n", gpl.decode(script, FIELDS)[2].at)])  # (back to the click)
        self.assertTrue(all(o.code == 0x67 for o in ops if line.at < o.at < gpl.decode(script, FIELDS)[2].at))

    def test_the_talk_asks_in_both_cases(self):
        """Cases 2 and 3: each run of the game's lines said again when he's there, back to the
        next case either way; and once done, done (the copy left as it is)."""
        script = talk()
        out = k.with_notice(script, FIELDS, k.TALK_SCRIPT)
        game = gpl.decode(script, FIELDS)
        added = [o for o in gpl.decode(out, FIELDS) if o.at >= len(script)]
        said = strings(added)
        self.assertEqual(said[:2], [k.LINES[1][1], "Legcrusher. "])
        self.assertIn("I sent Legcrusher after you, and he never came back. You ", said)
        backs = [o.args[0][1] for o in added if o.code == 0x64]
        self.assertEqual(backs, [game[4].at, game[7].at])  # (case 3's test, the switch's end)
        self.assertEqual(k.with_notice(out, FIELDS, k.TALK_SCRIPT), out)

    def test_the_half_giant_asked_about(self):
        """"Who is the half-giant?": his answer asks too, then back to the question's clearing."""
        s = _Script()
        s.op(0x4F, ("n", 115), ("str", k.LINES[3][1]))
        s.op(0x4F, ("n", 115), ("str", "He's not too bright, but he's good with monsters. "))
        s.op(0x16, ("n", 0), ("var", 14, 9))
        s.op(0x15)
        script = s.bytes(end=True)
        out = k.with_notice(script, FIELDS, k.TALK_SCRIPT)
        added = [o for o in gpl.decode(out, FIELDS) if o.at >= len(script)]
        self.assertIn("That was Legcrusher, the monster trainer. He's gone missing. ", strings(added))
        self.assertEqual(added[-1].args, [("n", gpl.decode(script, FIELDS)[2].at)])

    def test_left_alone_when_not_the_games(self):
        """Another script, or the lines not there: unchanged."""
        self.assertEqual(k.with_notice(call(), FIELDS, k.TALK_SCRIPT), call())
        s = _Script()
        s.op(0x4F, ("n", 115), ("str", "Legcrusher! Get them!"))
        other = s.bytes(end=True)
        self.assertEqual(k.with_notice(other, FIELDS, k.CALL_SCRIPT), other)


if __name__ == "__main__":
    unittest.main()
