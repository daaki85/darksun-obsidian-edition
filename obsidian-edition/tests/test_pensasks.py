import unittest

from dsloader import gamepatch, gpl, kalzith, pensasks, semyon, vulture
from dsloader.kalzith import _Script


def _game_like() -> bytes:
    """A talk laid out as Dinos's: a part (a subroutine) clearing the menu's local and showing a
    question, the menu in a loop while the local is 0, the answers as subroutines."""
    s = _Script()
    s.op(kalzith.BEGIN)
    s.op(0x13, ("label", "part"))
    s.op(0x31)
    s.label("part")
    s.op(0x16, ("n", 0), ("var", 14, 18))
    s.op(0x16, ("n", 1), ("var", 14, 19))
    s.label("loop")
    s.op(0x18, ("expr", [("var", 0x8E, 18), "==", ("n", 0)]))
    s.op(0x63, ("label", "out"))
    s.op(0x48, {"before": [], "title": ("var", 0x86, 1), "replies": [
        {"text": ("str", "  What do you know about Gilal?"), "goto": ("label", "gilal"),
         "if": ("var", 0x8E, 19), "before": [], "after": []},
        {"text": ("str", "  Let's change the subject."), "goto": ("label", "bye"), "if": ("n", 1), "before": [], "after": []},
        {"text": ("str", "Goodbye."), "goto": ("label", "bye"), "if": ("n", 1), "before": [], "after": []}]})
    s.op(0x64, ("label", "loop"))
    s.label("out")
    s.op(0x15)
    s.label("gilal")
    s.op(0x4F, ("n", 115), ("str", "Gilal was a gladiator. "))
    s.op(0x16, ("n", 0), ("var", 14, 19))
    s.op(0x15)
    s.label("bye")
    s.op(0x16, ("n", 1), ("var", 14, 18))
    s.op(0x15)
    return s.bytes(end=False)


def _ifs_closed(ops) -> bool:
    depth = 0
    for o in ops:
        depth += o.code == 0x3E
        depth -= o.code == 0x67
        if depth < 0:
            return False
    return depth == 0


class PensAsksTests(unittest.TestCase):
    FIRST = "  What do you know about Gilal?"

    def setUp(self):
        self.script = _game_like()
        self.ops = gpl.decode(self.script, b"")
        self.out = pensasks.with_asks(self.script, b"", self.FIRST, pensasks.DINOS_ASKS)
        self.start = next(o for o in self.ops if o.code == 0x16 and o.args == [("n", 0), ("var", 14, 18)])
        self.menu = next(o for o in self.ops if o.code == 0x48)

    def _op_at(self, at):
        r = gpl._Reader(self.out, b"")
        r.i = at
        return gpl._op(r)

    def _ops_from(self, at):
        return [gpl.Op(o.at + at, o.code, o.args) for o in gpl.decode(self.out[at:], b"")]

    def test_game_bytes_kept(self):
        """Only two of the game's commands change, each to a jump (64h) as long as or shorter than
        itself; everything else of the game's is where it was, the new code after it."""
        n = len(self.script)
        self.assertGreater(len(self.out), n)
        changed = {i for i in range(n) if self.out[i] != self.script[i]}
        self.assertLessEqual(changed, {*range(self.start.at, self.start.at + 3), *range(self.menu.at, self.menu.at + 3)})
        for at in (self.start.at, self.menu.at):
            self.assertEqual(self._op_at(at).code, pensasks.GOTO)
            self.assertGreaterEqual(self._op_at(at).args[0][1], n)

    def test_start(self):
        """The menu's part, as before (its local cleared), then the questions' flags, then back to
        the game's next command."""
        ops = self._ops_from(self._op_at(self.start.at).args[0][1])
        self.assertEqual((ops[0].code, ops[0].args), (self.start.code, self.start.args))
        back = next(o for o in ops if o.code == pensasks.GOTO)
        nxt = self.ops[self.ops.index(self.start) + 1]
        self.assertEqual(back.args, [("n", nxt.at)])
        part = ops[:ops.index(back)]
        self.assertTrue(_ifs_closed(part))
        for ask in pensasks.DINOS_ASKS:
            self.assertIn((0x16, [("n", 0), ("var", 13, ask.flag)]), [(o.code, o.args) for o in part])
            self.assertIn((0x16, [("n", 1), ("var", 13, ask.flag)]), [(o.code, o.args) for o in part])
        tests = " ".join(str(o.args) for o in part if o.code == 0x18)
        self.assertIn(str(kalzith.STOCKED), tests)
        self.assertIn(str(-semyon.SEMYON), tests)
        self.assertIn(str(semyon.PLACED), tests)

    def test_menu(self):
        """The game's questions as they were, the new ones after the last about someone (before
        "Let's change the subject." and "Goodbye."), each shown by its flag; after the menu, on to
        what followed the game's."""
        at = self._op_at(self.menu.at).args[0][1]
        ops = self._ops_from(at)
        menu = ops[0]
        self.assertEqual(menu.code, 0x48)
        old, new = self.menu.args[0]["replies"], menu.args[0]["replies"]
        asks = pensasks.DINOS_ASKS
        added = new[1:1 + len(asks)]
        self.assertEqual(new[:1] + new[1 + len(asks):], old)
        self.assertEqual([r["text"] for r in added], [("str", a.text) for a in asks])
        self.assertEqual([r["if"] for r in added], [("var", 0x8D, a.flag) for a in asks])
        self.assertEqual(menu.args[0]["title"], self.menu.args[0]["title"])
        after = self.ops[self.ops.index(self.menu) + 1]
        self.assertEqual((ops[1].code, ops[1].args), (pensasks.GOTO, [("n", after.at)]))
        for reply, ask in zip(added, asks):
            body = self._ops_from(reply["goto"][1])
            body = body[:next(i for i, o in enumerate(body) if o.code == 0x15) + 1]
            said = "".join(t for t in gpl.strings(body)).replace("  ", " ")
            self.assertEqual(said.split(), (ask.dead_answer + " " + ask.answer).split())  # (dead, else alive)
            self.assertIn((0x16, [("n", 0), ("var", 13, ask.flag)]), [(o.code, o.args) for o in body])

    def test_once(self):
        self.assertEqual(pensasks.with_asks(self.out, b"", self.FIRST, pensasks.DINOS_ASKS), self.out)

    def test_other_menus_untouched(self):
        self.assertEqual(pensasks.with_asks(self.script, b"", "  Something else?", pensasks.DINOS_ASKS), self.script)

    def test_dead(self):
        """As the game's people do for the dead: the Trustee asks "What was X like?" instead (each
        question shown only alive, or only dead), Dinos keeps the question with another answer."""
        trustee = {a.text.strip(): a for a in pensasks.TRUSTEE_ASKS}
        self.assertEqual(trustee["What can you tell me about Kalzith?"].shown, (pensasks.KALZITH_ALIVE,))
        self.assertEqual(trustee["What was Kalzith like?"].shown, (pensasks.KALZITH_DEAD,))
        self.assertEqual(trustee["What can you tell me about Semyon?"].shown, (pensasks.SEMYON_ALIVE,))
        self.assertEqual(trustee["What was Semyon like?"].shown, (pensasks.SEMYON_DEAD,))
        for ask in pensasks.DINOS_ASKS:
            self.assertEqual(len(ask.shown), 2)
            self.assertIs(ask.dead, ask.shown[1])
            self.assertTrue(ask.dead_answer)
        self.assertIn(("var", 0x8D, kalzith.DIED), pensasks.KALZITH_DEAD[1])
        self.assertIn(("var", 0x8D, semyon.DIED), pensasks.SEMYON_DEAD[1])

    def test_text_sizes(self):
        """Questions fit the reply window; no narration (the speakers' own words)."""
        for ask in pensasks.DINOS_ASKS + pensasks.TRUSTEE_ASKS:
            self.assertLessEqual(len(ask.text), kalzith.REPLY)
            self.assertTrue(ask.text.startswith("  "))

    def test_flags(self):
        """Flags of their own: past Kalzith's and Semyon's (760-765), within what a save keeps."""
        flags = [a.flag for a in pensasks.DINOS_ASKS + pensasks.TRUSTEE_ASKS]
        self.assertEqual(len(set(flags)), len(flags))
        self.assertTrue(all(semyon.MET < f < 808 for f in flags))

    def test_too_long(self):
        """Unchanged if it would be longer than the (bigger) buffer runs."""
        long = self.script + b"\x31" * (pensasks.LONGEST - len(self.script) - 10)
        self.assertEqual(pensasks.with_asks(long, b"", self.FIRST, pensasks.DINOS_ASKS), long)

    def test_vulture(self):
        """In Dinos's first menu, just before "Goodbye.", shown while the party carries the cooked
        vulture (the game's 33h test on the party, as the reply's own condition: the menu has no
        part start to set a flag at); chosen: his answer, the vulture taken, the quest's sound,
        MEAL set, and the XP given by the game's routine for it (its window and the quest's sound)."""
        first = _game_like().replace(gpl.encode_expr(("str", "  What do you know about Gilal?")),
                                     gpl.encode_expr(("str", "<name>")))
        out = pensasks.with_asks(first, b"", "<name>", (pensasks.VULTURE,), "Goodbye.")
        self.assertNotEqual(out, first)
        types = bytes(72) + b"\x12"  # (field 72, an object, carries a number: as the game's)
        ops = gpl.decode(out[len(first):], types)
        menu = next(o for o in ops if o.code == 0x48)
        texts = [r["text"] for r in menu.args[0]["replies"]]
        self.assertEqual(texts[-2:], [("str", pensasks.VULTURE.text), ("str", "Goodbye.")])
        shown = menu.args[0]["replies"][-2]["if"]
        self.assertEqual(shown[0], "op")
        self.assertEqual((shown[1].code, shown[1].args),
                         (0x33, [("n", pensasks.PARTY), 77, 80, [(72, 4, ("n", -vulture.COOKED))]]))
        codes = [(o.code, o.args) for o in ops]
        self.assertIn((pensasks.TAKE, [("n", 1), ("n", -vulture.COOKED), ("n", pensasks.PARTY), ("n", 9999)]), codes)
        self.assertIn((0x16, [("n", 1), ("var", 13, vulture.MEAL)]), codes)
        said = " ".join(gpl.strings(ops)).replace("  ", " ")
        self.assertIn("A vulture! Give it here.", said)
        self.assertIn("Each party member receives 100 experience points!", said)
        self.assertIn((pensasks.SOUND, [("n", pensasks.QUEST_SOUND)]), codes)
        self.assertIn((pensasks.GIVE_XP, [("n", pensasks.PARTY), ("n", vulture.XP_REWARD)]), codes)
        # (after the XP's narration, Dinos's portrait and a word of his again: the upper box)
        xp = codes.index((pensasks.GIVE_XP, [("n", pensasks.PARTY), ("n", vulture.XP_REWARD)]))
        self.assertIn((pensasks.PORTRAIT, [("n", pensasks.DINOS_PORTRAIT)]), codes[xp:])
        self.assertIn(pensasks.AFTER_MEAL, said)
        # (not through the game's routine in script 74: its narration window ended the talk's menu)
        self.assertFalse([c for c in codes if c[0] == 0x14 and c[1][-1] == ("n", 74)])
        self.assertEqual([m[1] for m in pensasks.MENUS if pensasks.VULTURE in m[2]], ["<name>"])

    def test_buffer(self):
        """The Loader's game has room for the Trustee's script with the questions (10540 bytes)."""
        self.assertGreaterEqual(pensasks.LONGEST, 10540)
        self.assertGreater(gamepatch.SCRIPT_BUFFER, 10000)

    def test_script_chunks(self):
        """Only the two talks, and only where their menus are."""
        chunks = {("GPL ", pensasks.DINOS_SCRIPT): self.script, ("GPL ", 5): self.script}
        out = pensasks.script_chunks(chunks, b"")
        self.assertEqual(set(out), {("GPL ", pensasks.DINOS_SCRIPT)})

    def test_vulture_switched_off(self):
        """With the vulture quest off, Dinos's first menu is the game's."""
        first = _game_like().replace(gpl.encode_expr(("str", "  What do you know about Gilal?")),
                                     gpl.encode_expr(("str", "<name>")))
        number = next(m[0] for m in pensasks.MENUS if pensasks.VULTURE in m[2])
        chunks = {("GPL ", number): first}
        self.assertIn(("GPL ", number), pensasks.script_chunks(chunks, b""))
        out = pensasks.script_chunks(chunks, b"", vulture=False)
        self.assertEqual(out.get(("GPL ", number), first), first)


def _busy_like() -> bytes:
    """The Trustee's greeting as the game has it: busy (flag 51), the line and the end; else on."""
    s = _Script()
    s.op(0x18, ("expr", [("var", 0x8D, pensasks.BUSY), "==", ("n", 1)]))
    s.op(0x3E, ("label", "else"))
    s.op(0x4F, ("n", 115), ("str", "I'd love to talk more, but I have to get back to work -- they "))
    s.op(0x4F, ("n", 115), ("str", "don't feed you for nothin' around here! "))
    s.op(0x31)
    s.label("else")
    s.op(0x3F, ("label", "end"))
    s.op(0x4F, ("n", 115), ("str", "So you're the new gladiators. "))
    s.label("end")
    s.op(0x67)
    s.op(0x15)
    return s.bytes(end=False)


class BusyOnceTests(unittest.TestCase):

    def test_line_clears_busy(self):
        """The busy line jumps to a piece clearing the flag, saying it and going back on; every
        other byte is the game's."""
        script = _busy_like()
        ops = gpl.decode(script, b"")
        line, after = ops[2], ops[3]
        out = pensasks.busy_once(script, b"")
        jump = gpl.encode_op((0x64, [("n", len(script))]))
        self.assertEqual(out[line.at:line.at + len(jump)], jump)
        self.assertEqual(out[:line.at], script[:line.at])
        self.assertEqual(out[line.at + len(jump):len(script)], script[line.at + len(jump):])
        added = [(o.code, o.args) for o in gpl.decode(out[len(script):], b"")]
        self.assertEqual(added, [(0x16, [("n", 0), ("var", 13, pensasks.BUSY)]),
                                 (0x14, [("n", pensasks.ROUNDS_AT), ("n", pensasks.ROUNDS_SCRIPT)]),
                                 (line.code, line.args), (0x64, [("n", after.at)])])

    def test_once_and_elsewhere(self):
        script = _busy_like()
        out = pensasks.busy_once(script, b"")
        self.assertEqual(pensasks.busy_once(out, b"", script), out)  # (done once)
        self.assertEqual(pensasks.busy_once(_game_like(), b""), _game_like())  # (no busy line)

    def test_script_chunks(self):
        chunks = {("GPL ", pensasks.TRUSTEE_SCRIPT): _busy_like()}
        self.assertIn(("GPL ", pensasks.TRUSTEE_SCRIPT), pensasks.script_chunks(chunks, b""))


def _rounds_like() -> bytes:
    """The end of the Trustee's rounds as the game has it: his key stolen and lying near, he
    makes for it."""
    s = _Script()
    s.op(0x18, ("expr", ["(", ("var", 0x8D, pensasks.KEY_STOLEN), "==", ("n", 1), ")"]))
    s.op(0x3E, ("label", "end"))
    s.op(0x18, ("op", (16, [("var", 137, 39), ("n", pensasks.KEY), ("n", 9)])))
    s.op(0x3E, ("label", "end2"))
    s.op(0x14, ("n", 0), ("n", 8))
    s.label("end2")
    s.op(0x67)
    s.label("end")
    s.op(0x67)
    s.op(0x31)
    return s.bytes(end=False)


class KeyChaseTests(unittest.TestCase):

    def test_never(self):
        """The test asks for a value the flag never has; nothing else changes, nothing moves."""
        script = _rounds_like()
        out = pensasks.no_key_chase(script, b"")
        self.assertEqual(len(out), len(script))
        first = gpl.decode(out, b"")[0]
        self.assertEqual(first.args[0][1][3], ("n", pensasks.NEVER))
        self.assertEqual(out[gpl.decode(script, b"")[1].at:], script[gpl.decode(script, b"")[1].at:])

    def test_elsewhere(self):
        self.assertEqual(pensasks.no_key_chase(_game_like(), b""), _game_like())
        chunks = {("GPL ", pensasks.ROUNDS_SCRIPT): _rounds_like()}
        self.assertIn(("GPL ", pensasks.ROUNDS_SCRIPT), pensasks.script_chunks(chunks, b""))


def _steps_like() -> bytes:
    """The Trustee's rounds' corners as the game has them: a case per step (27h: the step, then
    where the next case is), steps 1 and 5 none, 6 and 7 never reached."""
    s = _Script()
    s.op(0x17, pensasks.STEP)
    for step, corner in ((0, (111, 42)), (2, (91, 87)), (3, (91, 42)), (4, (91, 87)), (6, (111, 87)),
                         (7, None), (8, None)):
        s.op(pensasks.CASE, ("n", step), ("label", f"after {step}"))
        if corner:
            s.op(0x16, ("n", corner[0]), pensasks.CORNER[0])
            s.op(0x16, ("n", corner[1]), pensasks.CORNER[1])
        else:
            s.op(0x62, ("n", -89))
            s.op(0x16, ("n", 1), ("var", 14, 15))
        s.label(f"after {step}")
    s.op(0x31)
    return s.bytes(end=False)


class RoundsPausesTests(unittest.TestCase):

    def corners(self, script: bytes) -> dict:
        """{step: (x, y)} as the script runs it, the step's case followed through its jumps."""
        ops = gpl.decode(script, b"")
        at = {o.at: i for i, o in enumerate(ops)}
        out = {}
        for step in range(9):
            i, x, y = at[ops[0].at] + 1, None, None
            for _ in range(200):
                o = ops[i]
                if o.code == pensasks.CASE:
                    i = i + 1 if o.args[0] == ("n", step) else at[o.args[1][1]]
                    continue
                if o.code == 0x16 and o.args[1] == pensasks.CORNER[0]:
                    x = o.args[0][1]
                elif o.code == 0x16 and o.args[1] == pensasks.CORNER[1]:
                    y = o.args[0][1]
                elif o.code == 0x64:
                    i = at[o.args[0][1]]
                    continue
                elif o.code == 0x31:
                    break
                i += 1
            if x is not None:
                out[step] = (x, y)
        return out

    def test_pauses_have_corners(self):
        """Steps 1 and 5 stay at the corner before them (0's, and 4's), of their own: nothing
        another script leaves in the shared words sends him off; the others go where they did."""
        script = _steps_like()
        before = self.corners(script)
        self.assertNotIn(1, before)
        self.assertNotIn(5, before)
        out = pensasks.rounds_pauses(script, b"")
        self.assertNotEqual(out, script)
        after = self.corners(out)
        self.assertEqual(after[1], before[0])
        self.assertEqual(after[5], before[4])
        for step in (0, 2, 3, 4):
            self.assertEqual(after[step], before[step])
        self.assertEqual(pensasks.rounds_pauses(out, b"", script), out)  # (done once)
        self.assertEqual(pensasks.rounds_pauses(_game_like(), b""), _game_like())

    def test_script_chunks(self):
        chunks = {("GPL ", pensasks.ROUNDS_SCRIPT): _steps_like()}
        out = pensasks.script_chunks(chunks, b"")[("GPL ", pensasks.ROUNDS_SCRIPT)]
        self.assertEqual(self.corners(out)[1], (111, 42))


if __name__ == "__main__":
    unittest.main()
