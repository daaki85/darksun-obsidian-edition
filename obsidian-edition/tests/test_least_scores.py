"""The least each score may be at creation (gamepatch's least_scores, DSUN.EXE 67399h): the
manual's requirements for each class, the highest of a character's classes, 3 for none; run in
the emulator. The patch's bytes are dos/least_scores.asm's, and the overlay manager's two
"mov dx,338h" stay where the game has them."""

import os
import shutil
import subprocess
import struct
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import game, gamepatch  # noqa: E402

try:
    import unicorn
    from unicorn import x86_const as r
except ImportError:  # (DSCLOG's tests need it too)
    unicorn = None

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATCH = next(p for p in gamepatch.PATCHES if p.name == "least_scores")
CODE, DS, SHEET, SS = 0x2000, 0x3000, 0x4000, 0x5000
SP = 0x0F00
STR, DEX, CON, INT, WIS, CHA = range(6)
CLERIC, DRUID, FIGHTER, GLADIATOR, PRESERVER, PSIONICIST, RANGER, THIEF = range(1, 9)  # (the creation sheet's)


class BytesTests(unittest.TestCase):
    def test_same_size_and_fixed_words(self):
        """104 bytes, as the routine it replaces; "mov dx,338h" at +1Eh and +42h in both."""
        self.assertEqual(len(PATCH.replacement), len(PATCH.original))
        for at in (0x1E, 0x42):
            self.assertEqual(PATCH.original[at:at + 3], bytes.fromhex("ba3803"))
            self.assertEqual(PATCH.replacement[at:at + 3], bytes.fromhex("ba3803"))

    @unittest.skipUnless(shutil.which("nasm"), "needs nasm")
    def test_built_from_the_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, "least.bin")
            subprocess.run(["nasm", "-f", "bin", "-o", out, "least_scores.asm"], check=True,
                           cwd=os.path.join(HERE, "dos"))
            with open(out, "rb") as f:
                self.assertEqual(f.read(), PATCH.replacement)


@unittest.skipIf(unicorn is None, "needs unicorn")
class LeastTests(unittest.TestCase):
    def least(self, classes, ability):
        mu = unicorn.Uc(unicorn.UC_ARCH_X86, unicorn.UC_MODE_16)
        mu.mem_map(0, 0x100000)
        mu.mem_write(CODE * 16, PATCH.replacement)
        mu.mem_write(CODE * 16 + 0x100, b"\x90")  # (where the RETF goes)
        mu.mem_write(DS * 16 + 0x119C, struct.pack("<HH", 0, SHEET))
        sheet = bytearray(0x47)
        sheet[0x21:0x21 + len(classes)] = bytes(classes)
        mu.mem_write(SHEET * 16, bytes(sheet))
        # far return to CODE:0100h, then the classes and the ability (as 6490Dh pushes them)
        mu.mem_write(SS * 16 + SP, struct.pack("<HHHH", 0x100, CODE, len(classes), ability))
        for reg, value in ((r.UC_X86_REG_CS, CODE), (r.UC_X86_REG_DS, DS), (r.UC_X86_REG_SS, SS),
                           (r.UC_X86_REG_SP, SP), (r.UC_X86_REG_BP, 0x1234), (r.UC_X86_REG_SI, 0x5678),
                           (r.UC_X86_REG_DI, 0x9ABC)):
            mu.reg_write(reg, value)
        mu.emu_start(CODE * 16, CODE * 16 + 0x100)
        self.assertEqual([mu.reg_read(x) for x in (r.UC_X86_REG_BP, r.UC_X86_REG_SI, r.UC_X86_REG_DI)],
                         [0x1234, 0x5678, 0x9ABC])  # (the caller's kept)
        return mu.reg_read(r.UC_X86_REG_AX)

    def test_the_manual(self):
        """Each class's requirements in the manual; 3 where it has none."""
        want = {CLERIC: {WIS: 9}, DRUID: {WIS: 12, CHA: 15}, FIGHTER: {STR: 9},
                GLADIATOR: {STR: 13, DEX: 12, CON: 15}, PRESERVER: {INT: 9},
                PSIONICIST: {CON: 11, INT: 12, WIS: 15}, RANGER: {STR: 13, DEX: 13, CON: 14, WIS: 14},
                THIEF: {DEX: 9}}
        for cls, needs in want.items():
            for ability in range(6):
                with self.subTest(cls=cls, ability=ability):
                    self.assertEqual(self.least([cls], ability), needs.get(ability, 3))
        self.assertEqual(game.CREATION_MINIMUMS, want)  # (the dice log's)

    def test_several_classes(self):
        """The highest of the classes' (a fighter/thief: STR 9, DEX 9; a ranger/cleric: WIS 14,
        CHA none)."""
        self.assertEqual([self.least([FIGHTER, THIEF], a) for a in range(6)], [9, 9, 3, 3, 3, 3])
        self.assertEqual([self.least([RANGER, CLERIC], a) for a in range(6)], [13, 13, 14, 3, 14, 3])
        self.assertEqual([self.least([FIGHTER, DRUID, PSIONICIST], a) for a in range(6)], [9, 3, 11, 12, 15, 15])

    def test_no_class(self):
        self.assertEqual(self.least([], STR), 3)


if __name__ == "__main__":
    unittest.main()
