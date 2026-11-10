"""The Loader's own scripts in its copy of GPLDATA: one number each (kalzith.LOADER_SCRIPTS), entry
points that don't move with the switches, and every call into a script landing inside it (the
chest's script once took Alagorn's 220, and his clothes menu called past its end)."""

import itertools
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import alagorn, gpl, kalzith, pehtuclchest, semyon

GPLDATA = os.environ.get("DSUN_GPLDATA")
CALL = 0x14  # (place, script): a call into another script


class NumbersTests(unittest.TestCase):
    def test_each_module_its_own(self):
        """Each module's script numbers are the ones LOADER_SCRIPTS gives it, none shared."""
        self.assertEqual(kalzith.SCRIPT, 218)
        self.assertEqual(semyon.SCRIPT, 219)
        self.assertEqual(sorted(set(alagorn.COPY_OF.values())), [220, 221, 222])
        self.assertEqual(pehtuclchest.SCRIPT, 223)
        self.assertEqual(alagorn.TOLD_IN, {222: 224})  # (the weapons' stories, the copy calls)
        self.assertEqual(sorted(kalzith.LOADER_SCRIPTS), list(range(218, 225)))
        self.assertTrue(set(kalzith.ENTRY_SCRIPTS) <= set(kalzith.LOADER_SCRIPTS))


@unittest.skipUnless(GPLDATA and os.path.isfile(GPLDATA), "needs the game's GPLDATA.GFF (DSUN_GPLDATA)")
class CopyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from dsloader.gff import read_gff
        with open(GPLDATA, "rb") as f:
            cls.data = f.read()
        cls.chunks = read_gff(cls.data)
        cls.field_types = next((v for k, v in cls.chunks.items() if k[0] == "GPLX"), b"")[gpl.FIELD_TYPES_AT:]

    def test_numbers_free_in_the_game(self):
        self.assertFalse({("GPL ", n) for n in kalzith.LOADER_SCRIPTS} & set(self.chunks))

    def test_modules_dont_overlap(self):
        """The new scripts each module makes, made on their own: no two make the same one."""
        made = {
            "alagorn": alagorn.script_chunks(self.chunks, self.field_types, True, True, True),
            "chest": pehtuclchest.script_chunks(self.chunks, self.field_types, {}),
            "kalzith": {("GPL ", kalzith.SCRIPT): b""},
            "semyon": {("GPL ", semyon.SCRIPT): b""},
        }
        new = {name: {k for k in out if k[0] == "GPL " and k not in self.chunks} for name, out in made.items()}
        for (a, x), (b, y) in itertools.combinations(new.items(), 2):
            self.assertFalse(x & y, f"{a} and {b} both make {sorted(x & y)}")

    def test_entries_whatever_the_switches(self):
        """The entry points' table is the same with any of the switches off."""
        tables = set()
        for kz, sy, pens in itertools.product((True, False), repeat=3):
            out = kalzith.script_chunks(self.data, kalzith=kz, semyon=sy, pens=pens)
            tables.add(out[kalzith.ENTRIES])
        self.assertEqual(len(tables), 1)
        table = tables.pop()
        entries = [kalzith.ENTRY.unpack_from(table, i) for i in range(0, len(table), kalzith.ENTRY.size)]
        self.assertEqual([e[2] for e in entries[-3:]], list(kalzith.ENTRY_SCRIPTS))

    def test_calls_land_inside(self):
        """Every call in every script of the copy (all switches on) goes to a place inside a script
        there."""
        out = kalzith.script_chunks(self.data, cloak=True, tome=True, hay=True, champions=True)
        scripts = {**self.chunks, **out}
        for key, data in scripts.items():
            if key[0] not in ("GPL ", "MAS "):
                continue
            for op in gpl.walk(gpl.decode(data, self.field_types)):
                if op.code != CALL or len(op.args) != 2 or any(a[0] != "n" for a in op.args):
                    continue
                place, script = op.args[0][1], op.args[1][1]
                target = scripts.get(("GPL ", script))
                self.assertIsNotNone(target, f"{key} calls script {script}, not there")
                self.assertLess(place, len(target), f"{key} calls {script} at {place}, past its end")

    def test_alagorn_every_kind_written(self):
        """With every switch on, each of Alagorn's copies is written (no kind left out for length:
        the weapons' copy once grew past the buffer and was dropped without a word), each new item's
        reply in it, and the weapons' stories script decodes, each call into it landing on a
        command just after a 19h (where a called part starts)."""
        from dsloader import pensasks
        out = kalzith.script_chunks(self.data, cloak=True, tome=True, hay=True, champions=True)
        self.assertEqual(alagorn.LEFT_OUT, [])
        for number in sorted(set(alagorn.COPY_OF.values()) | set(alagorn.TOLD_IN.values())):
            self.assertIn(("GPL ", number), out)
        for number in (alagorn.SCRIPT, alagorn.OTHER_SCRIPT):
            for kind in alagorn.kinds(script=number):
                target = alagorn.COPY_OF.get((kind.first_reply, kind.none_text), number)
                for item, _ in kind.items:
                    self.assertIn(gpl.encode_expr(("str", f"  {item}")), out[("GPL ", target)], (target, item))
        for key, data in out.items():
            if key[0] == "GPL ":
                self.assertLessEqual(len(data), pensasks.LONGEST, key)
        for copy, number in alagorn.TOLD_IN.items():
            told = gpl.decode(out[("GPL ", number)], self.field_types)
            starts = {o.at for i, o in enumerate(told) if i and told[i - 1].code == alagorn.START}
            calls = [o.args[0][1] for o in gpl.walk(gpl.decode(out[("GPL ", copy)], self.field_types))
                     if o.code == CALL and o.args[1] == ("n", number)]
            self.assertEqual(len(calls), sum(len(k.items) for k in alagorn.kinds(script=alagorn.SCRIPT)
                                             if alagorn.COPY_OF.get((k.first_reply, k.none_text)) == copy))
            self.assertTrue(set(calls) <= starts, sorted(set(calls) - starts))

    def test_loader_calls_on_commands(self):
        """Every call in the Loader's own scripts goes to the start of a command of its target."""
        out = kalzith.script_chunks(self.data, cloak=True, tome=True, hay=True, champions=True)
        scripts = {**self.chunks, **out}
        starts = {}
        for key in out:
            if key[0] not in ("GPL ", "MAS "):
                continue
            for op in gpl.walk(gpl.decode(out[key], self.field_types)):
                if op.code != CALL or len(op.args) != 2 or any(a[0] != "n" for a in op.args):
                    continue
                place, script = op.args[0][1], op.args[1][1]
                if script not in starts:
                    starts[script] = {o.at for o in gpl.decode(scripts[("GPL ", script)], self.field_types)}
                self.assertIn(place, starts[script], f"{key} calls {script} at {place}, not a command's start")

    def test_each_fits_the_buffer(self):
        """Every script of the copy (all switches on) fits the game's script buffer, as the longest
        the scripts' writers allow (pensasks.LONGEST)."""
        from dsloader import pensasks
        out = kalzith.script_chunks(self.data, cloak=True, tome=True, hay=True, champions=True)
        for key, data in out.items():
            if key[0] == "GPL ":
                self.assertLessEqual(len(data), pensasks.LONGEST, key)


if __name__ == "__main__":
    unittest.main()
