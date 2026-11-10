"""The DOS programs the release ships are built from their source (nasm): DSCLOG.EXE from
dsclog.asm, GAMEEND.COM from gameend.asm, UMBPLUS.COM from umbplus.asm, and the least_scores patch
(gamepatch's, DSUN.EXE 67399h) from least_scores.asm; and DSCLOG's tables that have to be the
Loader's are, whole and byte for byte: large_dice (sizes.LARGE_DICE), kind_of_type
(specialize.KIND_OF_TYPE) and conjured_kinds (specialize.CONJURED_KINDS), read at their symbols in
a fresh build.

Skipped without nasm, unless DSUN_REQUIRE_NASM is set (the workflows set it: there a missing nasm
fails the run, so a DSCLOG.EXE not rebuilt from its source can't go into a release)."""

import os
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest

TESTS = os.path.dirname(os.path.abspath(__file__))
HERE = os.path.dirname(TESTS)
DOS = os.path.join(HERE, "dos")
sys.path.insert(0, HERE)
sys.path.insert(0, TESTS)

from dsloader import gamepatch, sizes, specialize  # noqa: E402

# (source, what it builds: a file in dos/, or None for the least_scores patch's bytes)
PROGRAMS = (("dsclog.asm", "DSCLOG.EXE"), ("gameend.asm", "GAMEEND.COM"), ("umbplus.asm", "UMBPLUS.COM"),
            ("least_scores.asm", None))


def _need_nasm(case: unittest.TestCase) -> None:
    if shutil.which("nasm"):
        return
    if os.environ.get("DSUN_REQUIRE_NASM"):
        case.fail("nasm is not on the PATH (DSUN_REQUIRE_NASM is set)")
    case.skipTest("needs nasm")


def assemble(source: str) -> bytes:
    """SOURCE (in dos/) as nasm builds it (its includes from dos/)."""
    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, "out.bin")
        subprocess.run(["nasm", "-f", "bin", "-I", DOS + os.sep, "-o", out, source], check=True, cwd=DOS)
        with open(out, "rb") as f:
            return f.read()


class BuiltFromSourceTests(unittest.TestCase):
    def setUp(self):
        _need_nasm(self)

    def test_each_program(self):
        for source, built in PROGRAMS:
            with self.subTest(source=source):
                got = assemble(source)
                if built is None:
                    want = next(p for p in gamepatch.PATCHES if p.name == "least_scores").replacement
                else:
                    with open(os.path.join(DOS, built), "rb") as f:
                        want = f.read()
                self.assertEqual(got, want, f"{built or 'the least_scores patch'} not rebuilt from {source}")


class TableTests(unittest.TestCase):
    """DSCLOG's tables, at their symbols in a build with a symbol map (test_dsclog_drawing.build),
    each the length the Loader's has: the next symbol starts where it ends."""

    @classmethod
    def setUpClass(cls):
        if not shutil.which("nasm"):
            cls.image = None
            return
        from test_dsclog_drawing import build
        exe, cls.sym = build()
        cls.image = exe[struct.unpack_from("<H", exe, 8)[0] * 16:]  # (past the MZ header: as loaded)

    def setUp(self):
        _need_nasm(self)

    def table(self, name: str) -> bytes:
        """The bytes from symbol NAME to the next symbol."""
        at = self.sym[name]
        end = min(v for v in self.sym.values() if v > at)
        return self.image[at:end]

    def test_large_dice(self):
        """sizes.LARGE_DICE (count, sides, the bonus's change by kind, None as 0, 0, 0) is DSCLOG's
        large_dice, all 16 kinds."""
        self.assertEqual(len(sizes.LARGE_DICE), len(specialize.KINDS))
        want = b"".join(struct.pack("<BBb", *(dice or (0, 0, 0))) for dice in sizes.LARGE_DICE)
        self.assertEqual(self.table("large_dice"), want)

    def test_kind_of_type(self):
        """specialize.KIND_OF_TYPE (a kind + 1 by item type, 0 for none) is DSCLOG's kind_of_type,
        to its last type."""
        got = self.table("kind_of_type")
        self.assertEqual(max(specialize.KIND_OF_TYPE) + 1, len(got))
        want = bytearray(len(got))
        for t, k in specialize.KIND_OF_TYPE.items():
            want[t] = k + 1
        self.assertEqual(got, bytes(want))

    def test_conjured_kinds(self):
        """specialize.CONJURED_KINDS (the spells' weapons, by type from 28) is DSCLOG's
        conjured_kinds (kind + 1)."""
        got = self.table("conjured_kinds")
        first = min(specialize.CONJURED_KINDS)
        self.assertEqual(sorted(specialize.CONJURED_KINDS), list(range(first, first + len(got))))
        self.assertEqual(got, bytes(specialize.CONJURED_KINDS[first + i] + 1 for i in range(len(got))))


if __name__ == "__main__":
    unittest.main()
