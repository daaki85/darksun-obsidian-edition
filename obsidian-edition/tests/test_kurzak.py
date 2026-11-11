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
        """The call's line becomes a jump to the test: Legcrusher alive (DEAD clear), the game's
        line; dead, Kurzak's own; then back to the click after it."""
        script = call()
        out = k.with_notice(script, FIELDS, k.CALL_SCRIPT)
        ops = gpl.decode(out, FIELDS)
        line = gpl.decode(script, FIELDS)[1]
        jump = next(o for o in ops if o.at == line.at)
        self.assertEqual(jump.code, 0x64)
        self.assertEqual(jump.args, [("n", len(script))])
        added = [o for o in ops if o.at >= len(script)]
        self.assertEqual(added[0].code, 0x18)
        self.assertEqual(added[0].args[0], k.HERE)  # (the flag read, not whether he is on the map)
        self.assertIn(("var", 0x8D, k.DEAD), added[0].args[0][1])
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


class FountainTests(unittest.TestCase):
    """Legcrusher's fetching speech (script 136) asks first whether he is at the fountain."""

    def speech(self):
        s = _Script()
        s.op(0x4F, ("n", 115), ("str", "Bad gladiators! "))
        s.op(0x4F, ("n", 115), ("str", k.FOUNTAIN_LINE))
        s.op(0x4F, ("n", 115), ("str", "there'll be trouble for ya."))
        s.op(0x4F, ("n", 115), MORE)
        return s.bytes(end=True)

    def test_the_branch(self):
        script = self.speech()
        out = k.with_fountain(script, FIELDS)
        ops = gpl.decode(out, FIELDS)
        line = gpl.decode(script, FIELDS)[1]
        self.assertEqual(next(o for o in ops if o.at == line.at).code, 0x64)
        added = [o for o in ops if o.at >= len(script)]
        self.assertEqual((added[0].code, added[0].args), (k.LOCATE, [("n", -k.LEGCRUSHER)]))
        said = strings(added)
        self.assertIn("Gladiators out of cells! Bad gladiators! Guards! GUARDS! ", said)
        self.assertIn(k.FOUNTAIN_LINE, said)  # (elsewhere: the game's words)
        sets = [o.args for o in added if o.code == 0x40]
        self.assertEqual(sets, [[("field", k.LEGCRUSHER, [k.SIDE]), ("n", 2)],
                                [("field", k.LEGCRUSHER, [k.ATTITUDE]), ("n", 2)]])
        self.assertIn(0x08, [o.code for o in added])  # (his hunt)
        self.assertEqual(added[-1].code, 0x64)  # (back to the game's script after its lines)
        self.assertEqual(added[-1].args, [("n", gpl.decode(script, FIELDS)[3].at)])
        self.assertEqual(k.with_fountain(out, FIELDS, script), out)  # (once)

    def test_left_alone_when_not_the_games(self):
        s = _Script()
        s.op(0x4F, ("n", 115), ("str", "Something else. "))
        script = s.bytes(end=True)
        self.assertEqual(k.with_fountain(script, FIELDS), script)


class WatchTests(unittest.TestCase):
    """DEAD set once Legcrusher is seen dead; not while he lives, nor without the flags."""

    def _gd(self, hp, ready=True):
        import struct
        from dsloader import game
        size = game.CREATURE_SIZE
        rec = bytearray(size)
        struct.pack_into("<h", rec, 0, hp)
        rec[game.CREATURE_NAME:game.CREATURE_NAME + 11] = b"Legcrusher\0"

        class GD:
            table, flags = bytes(size * game.PARTY_SIZE) + bytes(rec), set()

            def creatures(self, count):
                return self.table

            def flags_ready(self):
                return ready

            def flag(self, n):
                return n in self.flags

            def set_flag(self, n, on=True):
                self.flags.add(n)
        return GD()

    def test_watch(self):
        self.assertFalse(k.watch(self._gd(40)))
        gd = self._gd(0)
        self.assertTrue(k.watch(gd))
        self.assertIn(k.DEAD, gd.flags)
        self.assertFalse(k.watch(gd))  # (once)
        self.assertFalse(k.watch(self._gd(0, ready=False)))
