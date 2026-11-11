"""Tests for scriptfixes.py: the game's own script bugs mended in the Loader's copy of GPLDATA."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import gpl, scriptfixes as sf

GPLDATA = os.environ.get("DSUN_GPLDATA")


def script_with(script: int, size: int = 0x800) -> bytes:
    """A made-up script holding the bytes each repair of SCRIPT expects, where it expects them
    (SIZE long, or longer for the last of them)."""
    code = bytearray(max([size] + [r.at + len(r.was) + 0x10 for r in sf.REPAIRS if r.script == script]))
    for r in sf.REPAIRS:
        if r.script == script:
            code[r.at:r.at + len(r.was)] = r.was
    return bytes(code)


def _value(parts, values, at=0):
    """An expression's value (its parts as gpl.decode gives them, VALUES for its variables), read
    as the game does: left to right, brackets first. With AT, (value, where it stopped)."""
    ops = {">": lambda a, b: a > b, "<": lambda a, b: a < b, "and": lambda a, b: bool(a and b),
           "or": lambda a, b: bool(a or b)}
    value, op, i = None, None, at
    while i < len(parts):
        p = parts[i]
        if p == ")":
            break
        if p == "(":
            term, i = _value(parts, values, i + 1)
        elif isinstance(p, str):
            op = p
            i += 1
            continue
        else:
            term = values.get(p, p[1] if p[0] == "n" else None)
        value = term if op is None else ops[op](value, term)
        i += 1
    return (value, i) if at else value


class RepairTests(unittest.TestCase):
    def test_each_repair_lands(self):
        for script in {r.script for r in sf.REPAIRS}:
            code = script_with(script)
            fixed = sf.repaired(script, code)
            for r in sf.REPAIRS:
                if r.script != script:
                    continue
                if len(r.now) == len(r.was):
                    self.assertEqual(fixed[r.at:r.at + len(r.now)], r.now)
                    continue
                # a jump to the detour, past the script's end and its exit, then exits to WAS's length
                self.assertEqual(fixed[r.at], sf.JUMP)
                start = int.from_bytes(fixed[r.at + 1:r.at + 3], "big")
                self.assertGreater(start, len(code))
                self.assertEqual(fixed[len(code)], sf.EXIT)
                self.assertEqual(set(fixed[r.at + 3:r.at + len(r.was)]), {sf.EXIT} if len(r.was) > 3 else set())
                detour = fixed[start:start + len(r.now) + 3]
                for i in range(len(r.now)):  # (relocated addresses aside)
                    if not any(j <= i < j + 2 for j in r.relocate):
                        self.assertEqual(detour[i], r.now[i])
                for j in r.relocate:
                    self.assertEqual(int.from_bytes(detour[j:j + 2], "big"),
                                     int.from_bytes(r.now[j:j + 2], "big") + start)
                # and back to the bytes after WAS
                self.assertEqual(detour[len(r.now):], bytes((sf.JUMP,)) + (r.at + len(r.was)).to_bytes(2, "big"))

    def test_same_length_repairs_keep_the_length(self):
        self.assertEqual(len(sf.repaired(100, script_with(100))), 0x800)
        self.assertTrue(all(len(r.now) >= len(r.was) >= 3 or len(r.now) == len(r.was) for r in sf.REPAIRS))

    def test_lengthened_checks_read_through_the_character_record(self):
        # .71 before race, sex or the flags word, where the game read them from the combat record
        for r in sf.REPAIRS:
            if len(r.now) > len(r.was) and r.script in (31, 42, 80, 203):
                self.assertIn(bytes.fromhex("80250247"), r.now)
                self.assertNotIn(bytes.fromhex("802501"), r.now)

    def test_grate_hack_wants_a_melee_weapon(self):
        """The weapon search (137 at A79h): an item in either hand (slot field 85: 3 or 10) whose
        kind (field 72) is none of NOT_MELEE; on a find the game's flag and naming (41h), then out
        of the loop to its RETURN, not round again (that copied the next item over the found)."""
        search = next(r for r in sf.REPAIRS if (r.script, r.at) == (137, 0xA79))
        ops = gpl.decode(search.now, b"")
        parts = ops[0].args[0][1]
        self.assertEqual(ops[0].code, sf.TEST)
        self.assertEqual(parts.count(sf.HELD), 2)
        for kind in sf.NOT_MELEE:
            self.assertIn(("n", kind), parts)
            self.assertEqual(parts[parts.index(("n", kind)) - 2], sf.KIND)
        self.assertEqual([(o.code, o.args) for o in ops[1:]],
                         [(sf.IF, [("n", 0xA8F)]), (0x16, [("n", 1), ("var", 14, 3)]),
                          (0x41, [("var", 137, 43)]), (sf.JUMP, [("n", 0xA96)])])

    def test_grate_attack_rolls_strength_and_award_once(self):
        grate = next(r for r in sf.REPAIRS if (r.script, r.at) == (137, 0xB5C))
        self.assertTrue(grate.now.startswith(bytes.fromhex("18e28c528f1ee1da")))  # TEST (RAND(30)) <
        self.assertIn(bytes.fromhex("b180250117"), grate.now)  # the member's STR (field 17h)
        self.assertEqual(grate.now[-3:], grate.was[-3:])  # its IF, to "fails to damage the lock", kept
        award = next(r for r in sf.REPAIRS if r.script == 204)
        self.assertTrue(award.now.startswith(bytes.fromhex("18cd02b7d78f00")))  # TEST flag 695 == 0
        self.assertEqual(award.now[7], sf.IF)
        self.assertEqual(int.from_bytes(award.now[8:10], "big"), len(award.now) - 1)  # to its ENDIF
        self.assertEqual(award.now[10:-1], award.was)
        self.assertEqual(award.now[-1], sf.ENDIF)
        self.assertEqual(award.relocate, (8,))

    def test_messenger_trigger_as_mas_9_registers_it(self):
        # MAS 9 at 6Ch: while flag 339 is 0, the sight trigger, entry 1 of GPL 133 on -1297, range 15
        messenger = [r for r in sf.REPAIRS if r.script == 58]
        self.assertEqual([r.at for r in messenger], [0x1A, 0x99, 0xCC])
        for r in messenger:
            self.assertTrue(r.now.startswith(r.was))  # the flag still set first
            self.assertIn(bytes.fromhex("18cd0153d78f003e"), r.now)
            self.assertIn(bytes.fromhex("1b000100859105118f0f"), r.now)
            self.assertEqual(int.from_bytes(r.now[13:15], "big"), len(r.now) - 1)  # to its ENDIF
        serf = next(r for r in sf.REPAIRS if r.script == 60)
        self.assertEqual((serf.was[-1], serf.now[-1], serf.now[:-1]), (14, 127, serf.was[:-1]))

    def test_ambush_orders_its_own_guards(self):
        # each guard made alone, then the orders to the one made (local big number 40); no kind of
        # guard ordered as a whole; Pehtucl's by his kind
        ambush = next(r for r in sf.REPAIRS if (r.script, r.at) == (145, 0xE7D))
        ops = gpl.decode(ambush.now, b"")
        made = [o.args[:2] for o in ops if o.code == sf.CREATE]
        self.assertEqual(made, [[("n", -90), ("n", 1)]] * 4 + [[("n", -293), ("n", 1)]])
        ordered = [o.args[-1] if o.code == sf.HUNT else o.args[2] for o in ops if o.code in (sf.HUNT, sf.NO_ORDERS, sf.SIGHT)]
        self.assertEqual(ordered, [sf.MADE] * 15 + [("n", -37)] * 3)
        for kind in (-90, -293):
            self.assertNotIn(("n", kind), [a for o in ops if o.code != sf.CREATE for a in o.args])
        was = gpl.decode(ambush.was, b"")
        self.assertEqual([o.args[2] for o in was if o.code == sf.SIGHT], [("n", -90), ("n", -293), ("n", -37)])
        self.assertEqual(sorted({tuple(o.args[2:]) for o in ops if o.code == sf.CREATE}),
                         sorted({tuple(o.args[2:]) for o in was if o.code == sf.CREATE}))  # (where, as the game's)

    def test_fountain_masks_the_passage_too(self):
        fountain = next(r for r in sf.REPAIRS if (r.script, r.at) == (137, 0xFB5))
        test, = [o for o in gpl.decode(fountain.now, b"") if o.code == sf.TEST]
        self.assertEqual(fountain.now[-3:], bytes.fromhex("3e1081"))  # (its IF, to the alarm, kept)
        masked = lambda x, y: _value(test.args[0][1], {sf.X: x, sf.Y: y})
        for x, y in ((54, 74), (80, 95), (60, 94), (55, 93), (53, 93), (42, 95), (42, 91)):
            self.assertTrue(masked(x, y), (x, y))  # the room, as the game's, and the passage west of it
        for x, y in ((41, 94), (35, 94), (53, 80), (46, 86), (81, 94), (60, 73), (50, 90)):
            self.assertFalse(masked(x, y), (x, y))  # the alarm, as the game's
        game, = [o for o in gpl.decode(fountain.was, b"") if o.code == sf.TEST]
        for x in range(30, 90):
            for y in range(60, 97):
                if _value(game.args[0][1], {sf.X: x, sf.Y: y}):
                    self.assertTrue(masked(x, y))

    def test_too_long_a_script_left_alone(self):
        code = script_with(31, sf._longest())
        self.assertEqual(sf.repaired(31, code), code)

    def test_other_bytes_left_alone(self):
        # (another release, or a script the Loader changed there)
        code = bytes(0x800)
        self.assertEqual(sf.repaired(100, code), code)
        self.assertEqual(sf.repaired(5, script_with(100)), script_with(100))

    def test_chunks_from_the_loaders_changes_first(self):
        game = {("GPL ", 68): script_with(68), ("GPL ", 100): bytes(0x700)}
        out = {("GPL ", 100): script_with(100, 0x700)}
        changed = sf.script_chunks(game, out)
        self.assertEqual(set(changed), {("GPL ", 68), ("GPL ", 100)})
        self.assertEqual(sf.script_chunks({}, {}), {})


@unittest.skipUnless(GPLDATA and os.path.isfile(GPLDATA), "needs the game's GPLDATA.GFF (DSUN_GPLDATA)")
class FountainTests(unittest.TestCase):
    """In the Loader's copy of the game's scripts: Pehtucl's ambush (GPL 145) orders only the
    guards it makes, and the fountain (GPL 137) masks a yell in the passage before it."""

    @classmethod
    def setUpClass(cls):
        from dsloader import kalzith
        with open(GPLDATA, "rb") as f:
            data = f.read()
        cls.game, cls.types = gpl.load_scripts(data)
        cls.out = kalzith.script_chunks(data)

    def ops(self, script):
        return gpl.decode(self.out[("GPL ", script)], self.types)

    def test_ambush(self):
        game = gpl.decode(self.game[("GPL ", 145)], self.types)
        ops = self.ops(145)
        at = {o.at: o for o in ops}
        self.assertEqual((at[0xE7D].code, at[0xEDB].args), (sf.JUMP, [("n", 0), ("var", 13, 555)]))
        detour = [o for o in ops if o.at >= at[0xE7D].args[0][1]]
        self.assertEqual(detour[-1].code, sf.JUMP)
        self.assertEqual(detour[-1].args, [("n", 0xEDB)])
        ordered = lambda o: o.code in (sf.HUNT, sf.NO_ORDERS, sf.SIGHT)
        self.assertEqual(sum(1 for o in detour if o.code == sf.CREATE), 5)
        self.assertEqual({(o.args[-1] if o.code == sf.HUNT else o.args[2]) for o in detour if ordered(o)},
                         {sf.MADE, ("n", -37)})
        # the kinds ordered as a whole now only where the alarm is up (Pehtucl's other cases)
        kinds = lambda ops: sorted(o.at for o in ops if o.code == sf.HUNT and o.args[0] in (("n", -90), ("n", -293)))
        self.assertEqual(kinds(game), [0x169, 0x16D, 0xE99, 0xE9D])
        self.assertEqual(kinds(ops), [0x169, 0x16D])

    def test_fountain(self):
        ops = self.ops(137)
        at = {o.at: o for o in ops}
        self.assertEqual(at[0xFB2].code, 0x09)  # (the one yelling located)
        self.assertEqual(at[0xFB5].code, sf.JUMP)
        start = at[0xFB5].args[0][1]
        test = at[start]
        self.assertEqual(test.code, sf.TEST)
        self.assertTrue(_value(test.args[0][1], {sf.X: 53, sf.Y: 94}))
        self.assertFalse(_value(test.args[0][1], {sf.X: 35, sf.Y: 94}))
        after = [o for o in ops if o.at > start]
        self.assertEqual((after[0].code, after[0].args), (sf.IF, [("n", 0x1081)]))
        self.assertEqual((after[1].code, after[1].args), (sf.JUMP, [("n", 0xFD0)]))


if __name__ == "__main__":
    unittest.main()


OBJECTS = os.environ.get("DSUN_OBJECTS")


@unittest.skipUnless(GPLDATA and os.path.isfile(GPLDATA) and OBJECTS and os.path.isfile(OBJECTS),
                     "needs the game's GPLDATA.GFF and SEGOBJEX.GFF (DSUN_GPLDATA, DSUN_OBJECTS)")
class NotMeleeTests(unittest.TestCase):
    def test_not_melee_kinds(self):
        """Every kind of item in the Loader's objects (the game's and its own) whose type is held in
        a hand (missile, shield or thrown: +00h & 16h) but has no melee bit is in NOT_MELEE, and
        nothing in NOT_MELEE is a melee weapon."""
        import struct
        import tempfile
        from dsloader import dataitems, game, gff, icons
        with open(GPLDATA, "rb") as f:
            types = gff.read_gff(f.read())[("IT1R", 1)]
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, icons.OBJECTS_FILE)
            icons.write_objects(OBJECTS, out, {})
            with open(out, "rb") as f:
                chunks = gff.read_gff(f.read())
        kinds = {}
        for (ctype, _), data in chunks.items():
            if ctype != "RDFF":
                continue
            try:
                items = dataitems.items_of(data)
            except ValueError:
                continue
            for rec in items:
                if len(rec) == game.ITEM_SIZE:
                    t = struct.unpack_from("<H", rec, game.ITEM_TYPE)[0]
                    if t * 20 < len(types):
                        kinds.setdefault(struct.unpack_from("<h", rec, 0)[0], set()).add(types[t * 20])
        hand = {k for k, flags in kinds.items() if all(f & 0x16 and not f & 1 for f in flags)}
        self.assertLessEqual(hand, set(sf.NOT_MELEE))
        self.assertFalse({k for k in sf.NOT_MELEE if any(f & 1 for f in kinds.get(k, ()))})
