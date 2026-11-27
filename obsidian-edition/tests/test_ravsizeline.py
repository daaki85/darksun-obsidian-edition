"""DSCLOG2's SIZE_LINE and SIZE_PRE (sites 249, 250: DSCLOG's, Shattered Lands' item box), run in an emulated
CPU: an item box's damage line in Wake of the Ravager drawn again with the dice against a large foe after it
("1D8+4/1D12+4", as Shattered Lands' box: the user's both-games rule, 2026-11-27), and Shillelagh's line
1D6+1. Needs nasm and unicorn, else skipped."""

import os
import shutil
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dsloader import ravager  # noqa: E402
import test_ravkits  # noqa: E402

try:
    from unicorn import Uc, UC_ARCH_X86, UC_MODE_16
    from unicorn import x86_const as r
except ImportError:
    Uc = None

ASM = test_ravkits.ASM
TSR, SS, GDS, CODE, STUB = 0x1000, 0x4000, 0x6000, 0x3000, 0x7000
WAY_BACK, BP = 0x0100, 0x600
LONG_SWORD, TWOHAND_SWORD, DARTS, SHILLELAGH = 16, 101, 38, 90
BONE_GREAT_SWORD = 145  # (the mod's type: SL's 158, a two-handed sword)


@unittest.skipIf(Uc is None or not shutil.which("nasm"), "needs unicorn and nasm")
class SizeLineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from test_dsclog_drawing import build
        exe, cls.sym = build(ASM)
        cls.image = exe[struct.unpack_from("<H", exe, 8)[0] * 16:]

    def machine(self, text, creature):
        mu = Uc(UC_ARCH_X86, UC_MODE_16)
        mu.mem_map(0, 0x100000)
        mu.mem_write(TSR * 16, self.image)
        mu.mem_write(CODE * 16, b"\xF4" * 0x400)
        # the text routine: push bp / mov bp,sp / mov ax,[bp+10h] (the y) / mov cs:[0102h],ax /
        # inc word cs:[0100h] / pop bp / retf
        mu.mem_write(STUB * 16, bytes.fromhex("5589e58b46102ea302012eff0600015dcb"))
        mu.mem_write(STUB * 16 + 0x100, bytes(4))
        mu.mem_write(CODE * 16 + WAY_BACK - 10, struct.pack("<HH", 0, STUB))  # (the game's call's far address)
        mu.mem_write(SS * 16 + BP - 0x2E, text.encode() + bytes(40 - len(text)))
        mu.mem_write(SS * 16 + BP - 6, struct.pack("<I", creature))
        mu.mem_write(SS * 16 + BP - 2, struct.pack("<H", 1))
        mu.mem_write(SS * 16 + BP + 6, struct.pack("<HHHHHHHH", 0x1234, 0x5678, 0, 0xEC, 0, 50, 0xB5, 0xC2))  # (x +0Ch, y +10h)
        return mu

    def run_site(self, mu, label, kind, sp=0x7F0):
        mu.mem_write(SS * 16 + sp, struct.pack("<HHH", WAY_BACK, CODE, 0x202))
        for reg, value in dict(cs=TSR, ds=GDS, es=0x1111, ss=SS, esp=sp, ebp=BP, eax=0xAAAA, ebx=0xBBBB,
                               esi=kind, edi=0xD1D1, eflags=0x2).items():
            mu.reg_write(getattr(r, "UC_X86_REG_" + reg.upper()), value)
        mu.emu_start(TSR * 16 + self.sym[label], CODE * 16 + WAY_BACK, count=200000)
        self.assertEqual([mu.reg_read(x) & 0xFFFF for x in (r.UC_X86_REG_BP, r.UC_X86_REG_AX, r.UC_X86_REG_BX,
                                                             r.UC_X86_REG_SI, r.UC_X86_REG_DI, r.UC_X86_REG_ES)],
                         [BP, 0xAAAA, 0xBBBB, kind, 0xD1D1, 0x1111])

    def line(self, text, kind, box=True):
        """SIZE_LINE after the line TEXT for a weapon of type KIND (the box's: no creature): (the line after,
        [BP-2], the text routine's calls, the y it was given)."""
        mu = self.machine(text, 0 if box else 0x10000030)
        self.run_site(mu, "size_line", kind)
        got = bytes(mu.mem_read(SS * 16 + BP - 0x2E, 40)).split(b"\0")[0].decode()
        calls, y = struct.unpack("<HH", mu.mem_read(STUB * 16 + 0x100, 4))
        return got, struct.unpack("<h", mu.mem_read(SS * 16 + BP - 2, 2))[0], calls, y

    def test_box_lines(self):
        """A long sword's 1D8+4 is 1D8+4/1D12+4, as Shattered Lands' box; the sequel's own two-handed sword
        (RAV_LARGE) and the mod's bone great sword (by kind) 3D6; Shillelagh's 1D6+1 its 2D4."""
        self.assertEqual(self.line("1D8+4", LONG_SWORD), ("1D8+4/1D12+4", 2, 1, 50))
        self.assertEqual(self.line("1D8", 73)[0], "1D8/1D12")
        self.assertEqual(self.line("1D10+1", TWOHAND_SWORD)[0], "1D10+1/3D6+1")
        self.assertEqual(self.line("1D10+1", BONE_GREAT_SWORD)[0], "1D10+1/3D6+1")
        self.assertEqual(self.line("1D6+1", SHILLELAGH)[0], "1D6+1/2D4")

    def test_left_alone(self):
        """No second line for a weapon of the same dice on any size (the sequel's darts 38), a thing of no
        weapon kind, nor on the inventory screen or the Look box (a creature's)."""
        self.assertEqual(self.line("1D2", DARTS), ("1D2", 2, 0, 0))
        self.assertEqual(self.line("1D4", 9), ("1D4", 2, 0, 0))
        self.assertEqual(self.line("1D8+7", LONG_SWORD, box=False), ("1D8+7", 2, 0, 0))

    def pre(self, text, kind):
        """SIZE_PRE on the line TEXT: (the line, the word it pushed, SP after)."""
        mu = self.machine(text, 0)
        sp = 0x7F0
        self.run_site(mu, "size_pre", kind, sp)
        got = bytes(mu.mem_read(SS * 16 + BP - 0x2E, 40)).split(b"\0")[0].decode()
        new_sp = mu.reg_read(r.UC_X86_REG_SP) & 0xFFFF
        return got, struct.unpack("<H", mu.mem_read(SS * 16 + new_sp, 2))[0], new_sp

    def test_shillelagh_before(self):
        """Shillelagh's 2D4 made 1D6+1 (the rate kept); another weapon's line as it was; the push made (the
        game's [BP+14h])."""
        self.assertEqual(self.pre("2D4", SHILLELAGH), ("1D6+1", 0xC2, 0x7F0 - 2 + 6))
        self.assertEqual(self.pre("1.5x2D4+2", SHILLELAGH)[0], "1.5x1D6+3")
        self.assertEqual(self.pre("1D8+7", LONG_SWORD)[0], "1D8+7")

    def test_patches(self):
        for name, offset, original, site in (("size_line", 0x7B1CF, "ff46fe", 249), ("size_pre", 0x7B1B2, "ff7614", 250)):
            p = next(p for p in ravager.PATCHES if p.name == name)
            self.assertEqual((p.offset, p.original.hex()), (offset, original))
            self.assertEqual(p.replacement, bytes((0xCD, ravager.VEC_SITE, site)))
            at = self.sym["site_table"] + 2 * site
            self.assertEqual(struct.unpack_from("<H", self.image, at)[0], self.sym[name])


if __name__ == "__main__":
    unittest.main()
