import struct
import unittest

from dsloader import game, gpl, kalzith, semyon


def _ifs_closed(ops) -> bool:
    depth = 0
    for o in ops:
        depth += o.code == 0x3E
        depth -= o.code == 0x67
        if depth < 0:
            return False
    return depth == 0


def menu_replies(script: bytes):
    """{reply text: its "if"} for every reply menu in SCRIPT."""
    out = {}
    for op in gpl.walk(gpl.decode(script, b"")):
        if op.code == 0x48:
            for reply in op.args[0]["replies"]:
                out[reply["text"][1].strip()] = reply["if"]
    return out


class AskedOnceTests(unittest.TestCase):
    """A reply that stays in the menu is shown once a talk (its own local, cleared as the menu
    starts); one that leaves the menu, and Kalzith's shop, are shown as before."""

    def test_semyon(self):
        replies = menu_replies(semyon.conversation())
        self.assertEqual(replies["Why did they tie you up out there?"],
                         ("expr", ["(", ("var", 0x8E, 2), "==", ("n", 0), ")"]))
        self.assertEqual(replies["Tell me about the Alliance."][1][1], ("var", 0x8E, 5))
        self.assertEqual(replies["Farewell."], ("n", 1))

    def test_kalzith(self):
        replies = menu_replies(kalzith.conversation())
        self.assertEqual(replies["Who are you?"][1][1][:2], ("var", 0x8E))
        self.assertEqual(replies["Show us what you have."][0], "expr")
        self.assertNotIn(("var", 0x8E), [t[:2] for t in replies["Show us what you have."][1] if isinstance(t, tuple)])
        why = replies["Why would a defiler help a preserver?"]
        self.assertEqual(why[1][1][:2], ("var", 0x8E))
        left = replies["Anything left to sell?"]  # (its own test, and the local's)
        self.assertEqual(left[1][-4:], [("var", 0x8E, left[1][-4][2]), "==", ("n", 0), ")"])
        self.assertEqual(replies["We mean no harm. We're slaves too."], ("n", 1))

    def test_bodies_set_their_local(self):
        """Each such reply's subroutine sets its local to 1, and the menu clears them first."""
        ops = list(gpl.walk(gpl.decode(semyon.conversation(), b"")))
        sets = [op.args for op in ops if op.code == 0x16 and op.args[1][:2] == ("var", 14)]
        for local in (2, 3, 4, 5):
            self.assertIn([("n", 0), ("var", 14, local)], sets)
            self.assertIn([("n", 1), ("var", 14, local)], sets)


class SemyonTests(unittest.TestCase):
    MASTER = gpl.encode([(0x18, [("expr", [("var", 0x8D, 503), "==", ("n", 1)])]), (0x3E, [("n", 21)]),
                         (0x6F, [("n", 38), ("n", 145), ("n", -37)]), (0x67, []),
                         (0x6E, [("n", 1), ("n", 218), ("n", -1000)]), (0x31, [])])

    def test_placement(self):
        """In the pens' master script, just before its end: the game's bytes unmoved (its "if"
        skips to a fixed offset); him made in his pen once he has gone there, once; his talk."""
        out = semyon.with_semyon(self.MASTER)
        self.assertEqual(out[:len(self.MASTER) - 1], self.MASTER[:-1])
        ops = gpl.decode(out, b"")
        self.assertEqual(ops[-1].code, 0x31)
        self.assertTrue(_ifs_closed(ops))
        made = [o for o in ops if o.code == 0x25]
        self.assertEqual(made[0].args[:4], [("n", -semyon.SEMYON), ("n", 1), ("n", semyon.CELL[0]), ("n", semyon.CELL[1])])
        test = next(o for o in ops if o.code == 0x18 and o.at >= len(self.MASTER) - 1)
        self.assertIn(("var", 0x8D, semyon.LEFT), test.args[0][1])  # (left after the fight only)
        self.assertNotIn(("var", 0x8D, semyon.GONE), test.args[0][1])
        self.assertIn(("var", 0x8D, semyon.DIED), test.args[0][1])
        self.assertIn(("var", 0x8D, semyon.PLACED), test.args[0][1])
        skip = next(o for o in ops if o.code == 0x3E and o.at > test.at)
        end_if = next(o for o in ops if o.code == 0x67 and o.at > skip.at)
        self.assertEqual(skip.args[0], ("n", end_if.at))  # (onto its own end, in the whole script)
        self.assertIn((0x6E, [("n", kalzith.START), ("n", semyon.SCRIPT), ("n", -semyon.SEMYON)]),
                      [(o.code, o.args) for o in ops])
        self.assertEqual(semyon.with_semyon(out), out)

    def test_conversation(self):
        """His own portrait; every "if" closed; a greeting for the first meeting and after; a
        menu whose last reply ends the talk."""
        ops = gpl.decode(semyon.conversation(), b"")
        self.assertEqual(ops[0].code, kalzith.BEGIN)
        self.assertEqual((ops[1].code, ops[1].args), (0x54, [("n", semyon.PORTRAIT)]))
        self.assertTrue(_ifs_closed(ops))
        menu = next(o for o in ops if o.code == 0x48)
        self.assertEqual(menu.args[0]["replies"][-1]["text"][1].strip(), "Farewell.")
        text = " ".join(gpl.strings(ops))
        self.assertIn("holding pens", text)
        self.assertIn("I'm right behind you", text)  # (breaking out with Scar)
        tests = [o.args[0][1] for o in ops if o.code == 0x18 and o.args[0][0] == "expr"]
        self.assertIn(["(", ("var", 0x8D, semyon.ESCAPING), "==", ("n", 1), ")", "and",
                       "(", ("var", 0x8D, semyon.ESCAPED), "==", ("n", 0), ")"], tests)

    def test_numbers(self):
        """None of the game's: script past 217 (Kalzith's 218), flags past 755 (Kalzith's
        760-763), his own entry point in the game's table after Kalzith's."""
        self.assertGreater(semyon.SCRIPT, kalzith.SCRIPT)
        self.assertTrue(all(f > 763 for f in (semyon.PLACED, semyon.MET)))
        e = kalzith.ENTRY
        table = kalzith.with_entry(kalzith.with_entry(e.pack(0, 0, 0)), semyon.SCRIPT)
        rows = [e.unpack_from(table, i) for i in range(0, len(table), e.size)]
        self.assertEqual(rows[-1], (2, kalzith.START, semyon.SCRIPT))

    def _arena(self) -> bytes:
        """A script laid out as his arena talk: the command taking him off the map at EXIT."""
        sets, ends = divmod(semyon.EXIT - 1, 5)  # (5-byte commands, then 1-byte ones)
        pad = gpl.encode([(kalzith.BEGIN, [])] + [(0x16, [("n", 0), ("var", 14, 1)])] * sets + [(0x31, [])] * ends)
        self.assertEqual(len(pad), semyon.EXIT)
        return pad + gpl.encode([(semyon.REMOVE, [("n", -semyon.SEMYON), ("n", 255), ("n", 30), ("n", 30), ("n", 0)]),
                                 (0x31, [])])

    def test_exit(self):
        """Where he is taken off the map after the fight: a jump to LEFT set, the same command,
        and back; nothing of the game's moves; once only; other scripts unchanged."""
        arena = self._arena()
        out = semyon.with_exit(arena)
        self.assertEqual(out[:semyon.EXIT], arena[:semyon.EXIT])
        self.assertEqual(out[semyon.EXIT + 3:len(arena)], arena[semyon.EXIT + 3:])
        r = gpl._Reader(out, b"")
        r.i = semyon.EXIT
        jump = gpl._op(r)
        self.assertEqual((jump.code, jump.args), (semyon.GOTO, [("n", len(arena))]))
        added = gpl.decode(out[len(arena):], b"")
        self.assertEqual((added[0].code, added[0].args), (0x16, [("n", 1), ("var", 13, semyon.LEFT)]))
        self.assertEqual(added[1].code, semyon.REMOVE)
        self.assertEqual((added[2].code, added[2].args), (semyon.GOTO, [("n", semyon.EXIT + 12)]))
        self.assertEqual(semyon.with_exit(out), out)
        other = arena[:semyon.EXIT] + gpl.encode([(0x31, [])] * 13)
        self.assertEqual(semyon.with_exit(other), other)

    def _escape(self) -> bytes:
        """A script laid out as the arena's breakout (script 3): Scar's move to the pens, then
        his henchman's at ESCAPE_AT."""
        def move(obj):
            return (semyon.REMOVE, [("n", -obj), ("n", 41), ("n", 76), ("n", 68), ("n", 0)])
        before = gpl.encode([(kalzith.BEGIN, [])])
        pad_to = semyon.ESCAPE_AT - len(gpl.encode([move(87)]))  # (Scar's move just before)
        sets, ends = divmod(pad_to - len(before), 5)
        pad = before + gpl.encode([(0x16, [("n", 0), ("var", 14, 1)])] * sets + [(0x31, [])] * ends)
        self.assertEqual(len(pad), pad_to)
        return pad + gpl.encode([move(87), move(semyon.HENCHMAN), (0x67, []), (0x31, [])])

    def test_escape(self):
        """At the henchman's move to the pens: a jump to that move, then Semyon's to the same
        place with ESCAPING set if he is recruited, alive, in the arena and not against the
        party, and back; nothing of the game's moves; once only; other scripts unchanged."""
        script = self._escape()
        out = semyon.with_escape(script)
        at = semyon.ESCAPE_AT
        self.assertEqual(out[:at], script[:at])
        self.assertEqual(out[at + 3:len(script)], script[at + 3:])
        r = gpl._Reader(out, b"")
        r.i = at
        jump = gpl._op(r)
        self.assertEqual((jump.code, jump.args), (semyon.GOTO, [("n", len(script))]))
        added = gpl.decode(out[len(script):], b"")
        codes = [(o.code, o.args) for o in added]
        place = [("n", 41), ("n", 76), ("n", 68), ("n", 0)]
        self.assertEqual(codes[0], (semyon.REMOVE, [("n", -semyon.HENCHMAN)] + place))
        tests = [o.args[0][1] for o in added if o.code == 0x18]
        first, second = tests
        for flag, value in ((semyon.RECRUITED, 1), (semyon.DIED, 0)):
            self.assertIn(["(", ("var", 0x8D, flag), "==", ("n", value), ")"],
                          [first[i:i + 5] for i in range(len(first) - 4)])
        self.assertIn(0x80, [a[1].code for a in first if isinstance(a, tuple) and a[0] == "op"])
        self.assertNotIn(("field", semyon.SEMYON, [semyon.SIDE]), first)  # (read only once he's there)
        self.assertIn(("field", semyon.SEMYON, [semyon.SIDE]), second)
        self.assertIn((semyon.SET_FIELD, [("field", semyon.SEMYON, [semyon.SIDE]), ("n", semyon.WITH_US)]), codes)
        self.assertIn((semyon.REMOVE, [("n", -semyon.SEMYON), ("n", 41), ("n", 76 + semyon.BESIDE),
                                       ("n", 68), ("n", 0)]), codes)
        self.assertIn((0x16, [("n", 1), ("var", 13, semyon.ESCAPING)]), codes)
        moved = len(gpl.encode([codes[0]]))
        self.assertEqual(codes[-1], (semyon.GOTO, [("n", at + moved)]))
        self.assertTrue(_ifs_closed(added))
        self.assertEqual(semyon.with_escape(out), out)
        other = script[:at] + gpl.encode([(0x31, [])] * 14)
        self.assertEqual(semyon.with_escape(other), other)

    def test_watch(self):
        """DIED once a creature named Semyon is dead; not for a living one."""
        size = game.CREATURE_SIZE

        class GD:
            def __init__(self, hp):
                rec = bytearray(size)
                struct.pack_into("<h", rec, 0, hp)
                rec[game.CREATURE_NAME:game.CREATURE_NAME + 7] = b"Semyon\0"
                self.table, self.flags = bytes(size * 3) + bytes(rec), set()

            def creatures(self, count):
                return self.table

            def flag(self, n):
                return n in self.flags

            def set_flag(self, n, on=True):
                self.flags.add(n)

        alive, dead = GD(20), GD(0)
        self.assertFalse(semyon.watch(alive))
        self.assertNotIn(semyon.DIED, alive.flags)
        self.assertTrue(semyon.watch(dead))
        self.assertIn(semyon.DIED, dead.flags)
        self.assertFalse(semyon.watch(dead))  # (once)

    def test_after_escape(self):
        """After the party's escape (the game's flag 503): never put in his pen; Kalzith and he
        taken off the map once, as the game takes the pens' people, Kalzith only if there."""
        ops = gpl.decode(semyon.with_semyon(self.MASTER), b"")
        tests = [o for o in ops if o.code == 0x18]
        self.assertIn(["(", ("var", 0x8D, semyon.ESCAPED), "==", ("n", 0), ")"],
                      [tests[1].args[0][1][i:i + 5] for i in range(len(tests[1].args[0][1]) - 4)])
        removed = [o.args[0] for o in ops if o.code == semyon.REMOVE]
        self.assertEqual(removed, [("n", -kalzith.OBJECT), ("n", -semyon.SEMYON)])
        self.assertTrue(all(o.args[1:] == [("n", v) for v in semyon.GONE_AT] for o in ops if o.code == semyon.REMOVE))
        sets = [(o.args[1][2], o.args[0][1]) for o in ops if o.code == 0x16]
        self.assertIn((semyon.CLEARED, 1), sets)
        self.assertTrue(_ifs_closed(ops))
        # (broke out with the party and lived: the game's flag for a Semyon who got away)
        got_away = next(i for i, o in enumerate(ops) if o.code == 0x16 and o.args[1] == ("var", 13, semyon.GOT_AWAY))
        test = max((o for o in ops[:got_away] if o.code == 0x18), key=lambda o: o.at).args[0][1]
        self.assertEqual(test, ["(", ("var", 0x8D, semyon.ESCAPING), "==", ("n", 1), ")", "and",
                                "(", ("var", 0x8D, semyon.DIED), "==", ("n", 0), ")"])

    def test_settled(self):
        """In his pen, once (SETTLED), before the escape: as the pens' slaves are, on their side
        and with their 12 (his object is the arena's, on the party's side)."""
        ops = gpl.decode(semyon.with_semyon(self.MASTER), b"")
        fields = [o for o in ops if o.code == semyon.SET_FIELD]
        self.assertEqual([(o.args[0], o.args[1]) for o in fields],
                         [(("field", semyon.SEMYON, [semyon.SIDE]), ("n", semyon.NEUTRAL)),
                          (("field", semyon.SEMYON, [semyon.STEADY]), ("n", semyon.SLAVES_STEADY))])
        test = max((o for o in ops if o.code == 0x18 and o.at < fields[0].at), key=lambda o: o.at)
        for flag, value in ((semyon.SETTLED, 0), (semyon.ESCAPED, 0), (semyon.PLACED, 1)):
            self.assertIn(["(", ("var", 0x8D, flag), "==", ("n", value), ")"],
                          [test.args[0][1][i:i + 5] for i in range(len(test.args[0][1]) - 4)])
        self.assertIn(0x80, [a[1].code for a in test.args[0][1] if isinstance(a, tuple) and a[0] == "op"])
        sets = [(o.args[1][2], o.args[0][1]) for o in ops if o.code == 0x16 and o.at > fields[-1].at]
        self.assertEqual(sets[0], (semyon.SETTLED, 1))

    def test_flags(self):
        flags = (semyon.LEFT, semyon.DIED, semyon.CLEARED, semyon.SETTLED, semyon.ESCAPING, kalzith.DIED, kalzith.DRESSED, kalzith.SOLD_OUT)
        self.assertTrue(all(765 < f < 808 for f in flags))
        self.assertEqual(len(set(flags)), len(flags))


if __name__ == "__main__":
    unittest.main()
