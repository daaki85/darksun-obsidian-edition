"""The Loader's game flags, found rather than listed: every module-level constant of dsloader's
modules in the Loader's flags (756 to game.FLAG_COUNT), the pens' questions', aging's count and the
most Alagorn's menus can keep past their locals (alagorn.FLAGS on, one per new item a kind's menu
has no local for). No two share a number, so Alagorn's never reach Pehtucl's chest's (795, 796) or
Legcrusher's (797) and a new module's constant can't take another's (test_flagrange checks the
modules it lists; this finds them).

Alagorn's locals free in each of the game's menus (FREE_LOCALS) are the GOG scripts'; with the
game's GPLDATA.GFF (DSUN_GPLDATA) they are checked, and so is the scripts copy: it sets or reads
no Loader flag the modules don't have, and Alagorn tells of every new item."""

import ast
import glob
import os
import sys
import unittest
from unittest import mock

TESTS = os.path.dirname(os.path.abspath(__file__))
HERE = os.path.dirname(TESTS)
sys.path.insert(0, HERE)
sys.path.insert(0, TESTS)

from dsloader import aging, alagorn, game, gpl, kurzak, pehtuclchest, pensasks  # noqa: E402

GPLDATA = os.environ.get("DSUN_GPLDATA")
FIRST = 756  # (the game's flags run to 755)
# where a range starts, not a flag of its own: (module, constant)
RANGE_STARTS = {("alagorn", "FLAGS"), ("aging", "COUNT_FIRST")}
# the locals the game's scripts leave free in each of Alagorn's menus (by its first reply): a
# menu's new items past these keep their flag in alagorn.FLAGS on
FREE_LOCALS = {alagorn.SWORDS[0]: 9, alagorn.WEAPONS[0]: 9, alagorn.RINGS[0]: 9, alagorn.ARMOUR[0]: 11,
               alagorn.SHIELDS[0]: 13, alagorn.CLOTHES[0]: 9, alagorn.OTHER[0]: 12}
TRIAL = 16  # (items in a trial menu that finds a menu's free locals: more than any has)


def module_constants():
    """(module, name, value) of each module-level int constant of dsloader in FIRST..FLAG_COUNT-1
    (plain and tuple assignments)."""
    out = []
    for path in sorted(glob.glob(os.path.join(HERE, "dsloader", "*.py"))):
        module = os.path.splitext(os.path.basename(path))[0]
        with open(path, encoding="utf-8") as f:
            tree = ast.parse(f.read())
        for node in tree.body:
            if isinstance(node, ast.Assign):
                pairs = [(t, node.value) for t in node.targets]
            elif isinstance(node, ast.AnnAssign) and node.value is not None:
                pairs = [(node.target, node.value)]
            else:
                continue
            for target, value in pairs:
                if isinstance(target, ast.Tuple) and isinstance(value, ast.Tuple):
                    named = zip(target.elts, value.elts)
                else:
                    named = [(target, value)]
                for t, v in named:
                    if isinstance(t, ast.Name) and isinstance(v, ast.Constant) and type(v.value) is int \
                            and FIRST <= v.value < game.FLAG_COUNT:
                        out.append((module, t.id, v.value))
    return out


def alagorn_last() -> int:
    """The highest flag Alagorn's menus can keep (FLAGS - 1: none), all the new items on."""
    past = [len(kind.items) - FREE_LOCALS[kind.first_reply]
            for script in (alagorn.SCRIPT, alagorn.OTHER_SCRIPT) for kind in alagorn.kinds(script=script)]
    return alagorn.FLAGS + max(past + [0]) - 1


def loader_flags():
    """(label, flag) of each of the Loader's flags."""
    out = [(f"{m}.{n}", v) for m, n, v in module_constants() if (m, n) not in RANGE_STARTS]
    out += [(f"pensasks {ask.text.strip()!r}", ask.flag)
            for ask in pensasks.DINOS_ASKS + pensasks.TRUSTEE_ASKS if ask.flag is not None]
    out += [(f"aging.COUNT_FIRST+{i}", aging.COUNT_FIRST + i) for i in range(aging.COUNT_BITS)]
    out += [(f"alagorn.FLAGS+{n - alagorn.FLAGS}", n) for n in range(alagorn.FLAGS, alagorn_last() + 1)]
    return out


class FlagTests(unittest.TestCase):
    def test_found(self):
        """The scan finds the flags it should (it isn't finding nothing)."""
        found = {(m, n) for m, n, _ in module_constants()}
        for want in (("pehtuclchest", "DISARMED"), ("pehtuclchest", "UNLOCKED"), ("kurzak", "DEAD"),
                     ("alagorn", "FLAGS"), ("champions", "FOUGHT"), ("semyon", "TOLD")):
            self.assertIn(want, found)

    def test_in_range_and_unshared(self):
        seen = {}
        for label, n in loader_flags():
            self.assertTrue(FIRST <= n < game.FLAG_COUNT, f"{label} = {n}")
            self.assertFalse(n in seen, f"{label} = {n}, also {seen.get(n)}")
            seen[n] = label

    def test_alagorn_below_the_chest_and_kurzak(self):
        """Alagorn's overflow ends below Pehtucl's chest's flags and Legcrusher's."""
        last = alagorn_last()
        self.assertLess(last, min(pehtuclchest.DISARMED, pehtuclchest.UNLOCKED, kurzak.DEAD))
        self.assertEqual(set(FREE_LOCALS), {kind[0] for kind in alagorn.SCRIPT_OF})


def _flags_in(ops):
    """The flags a script's commands set or read (vars 13 and 141)."""
    out = set()

    def walk(x):
        if isinstance(x, tuple):
            if len(x) == 3 and x[0] == "var" and x[1] in (13, 141) and isinstance(x[2], int):
                out.add(x[2])
            for y in x:
                walk(y)
        elif isinstance(x, (list, dict)):
            for y in (x.values() if isinstance(x, dict) else x):
                walk(y)
        elif isinstance(x, gpl.Op):
            walk(x.args)

    for op in gpl.walk(ops):
        walk(op.args)
    return out


@unittest.skipUnless(GPLDATA and os.path.isfile(GPLDATA), "needs the game's GPLDATA.GFF (DSUN_GPLDATA)")
class GameScriptsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from dsloader import kalzith
        from dsloader.gff import read_gff
        with open(GPLDATA, "rb") as f:
            cls.data = f.read()
        cls.chunks = read_gff(cls.data)
        cls.field_types = next((v for k, v in cls.chunks.items() if k[0] == "GPLX"), b"")[gpl.FIELD_TYPES_AT:]
        cls.copy = kalzith.script_chunks(cls.data, True, True, True, True, True, True, True, True, True, True, True)

    def test_free_locals(self):
        """FREE_LOCALS are the game's scripts': a trial menu of TRIAL items keeps the rest in flags."""
        for script in (alagorn.SCRIPT, alagorn.OTHER_SCRIPT):
            for kind in alagorn.kinds(script=script):
                with self.subTest(kind=kind.first_reply):
                    trial = alagorn.Kind(kind.first_reply, kind.none_text, (kind.items[0],) * TRIAL)
                    with mock.patch.object(alagorn, "LONGEST", 0x7FFF):  # (only the numbers matter here)
                        out = alagorn.with_items(self.chunks[("GPL ", script)], self.field_types, (trial,))
                    self.assertNotEqual(out, self.chunks[("GPL ", script)])
                    flags = {f for f in _flags_in(gpl.decode(out, self.field_types)) if f >= alagorn.FLAGS}
                    self.assertEqual(TRIAL - len(flags), FREE_LOCALS[kind.first_reply])

    def test_copy_flags_known(self):
        """Every Loader flag the scripts copy sets or reads is one of the modules'."""
        known = {n for _, n in loader_flags()}
        for key, script in self.copy.items():
            if key[0] != "GPL ":
                continue
            with self.subTest(script=key[1]):
                used = {f for f in _flags_in(gpl.decode(script, self.field_types)) if f >= FIRST}
                self.assertLessEqual(used, known)

    def test_alagorn_tells_every_item(self):
        """Each new item of Alagorn's menus is in the scripts copy (a script grown past the buffer
        would drop the kind's whole part without a word: alagorn.with_items)."""
        told = b"".join(v for k, v in self.copy.items() if k[0] == "GPL ")
        missing = [f"{kind.first_reply.strip()}: {item}"
                   for script in (alagorn.SCRIPT, alagorn.OTHER_SCRIPT) for kind in alagorn.kinds(script=script)
                   for item, _ in kind.items if gpl.encode_expr(("str", f"  {item}")) not in told]
        self.assertEqual(missing, [], "Alagorn doesn't tell of these")


if __name__ == "__main__":
    unittest.main()
