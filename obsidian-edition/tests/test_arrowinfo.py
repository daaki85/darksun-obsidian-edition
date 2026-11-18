"""The item box's INFO for a Spellarcher's spell arrows (DSCLOG's INFO_HEAD): the heading SPELLARCHERS:
in place of the game's USEABLE BY:, run in Unicorn at the game's bytes (gamepatch's info_head)."""
import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import gamepatch, spellarrows  # noqa: E402

import test_cahulaks as tc  # noqa: E402
import test_dsclog as td  # noqa: E402

SS, BP, CALLER, GAME_DS = td.SS, td.BP, td.CALLER, td.GAME_DS
USEABLE_BY = 0x3493  # DS: the game's heading


def load_tests(loader, tests, pattern):  # (only this file's: not the cahulaks', inherited, again)
    suite = unittest.TestSuite()
    suite.addTests(InfoHeadTests(name) for name in sorted(vars(InfoHeadTests)) if name.startswith("test_"))
    return suite


@unittest.skipIf(td.Uc is None, "unicorn not installed")
class InfoHeadTests(tc.CahulaksTests):
    def head(self, name):
        """INFO_HEAD for an item named NAME: (the far pointer it pushed, as a segment and an offset;
        the text there; SP, BP, AX, BX after)."""
        mu, r = self.mu, td.r
        self.mu.mem_write(tc.ITEMS * 16 + 5 * 0x15 + 0x12, struct.pack("<H", name))
        self.mu.mem_write(GAME_DS * 16 + USEABLE_BY, b"USEABLE BY:\0")
        self.frame(p6=5)
        p = tc.tg.patch("info_head")
        self.at += 0x100
        start = CALLER * 16 + self.at
        mu.mem_write(start, p.replacement + b"\xf4")
        for reg, value in dict(cs=CALLER, ds=GAME_DS, ss=SS, esp=0x800, ebp=BP, eflags=td.IF | 2, eax=0x1111,
                               ebx=0x2222, es=0x3333).items():
            mu.reg_write(getattr(r, "UC_X86_REG_" + reg.upper()), value)
        mu.emu_start(start, 0, count=200000)
        self.assertEqual(mu.reg_read(r.UC_X86_REG_IP), self.at + len(p.replacement) + 1)
        sp = mu.reg_read(r.UC_X86_REG_SP)
        off, seg = struct.unpack("<HH", mu.mem_read(SS * 16 + sp, 4))
        text = bytes(mu.mem_read(seg * 16 + off, 20)).split(b"\0")[0].decode()
        return (seg, off, text, sp, mu.reg_read(r.UC_X86_REG_BP), mu.reg_read(r.UC_X86_REG_AX),
                mu.reg_read(r.UC_X86_REG_BX), mu.reg_read(r.UC_X86_REG_ES))

    def test_patch(self):
        p = tc.tg.patch("info_head")
        self.assertEqual((p.offset, p.original.hex()), (0x8C1E0, "1e689334"))
        self.assertEqual(p.replacement, bytes((0xCD, 0x98, gamepatch.INFO_HEAD_SITE, 0x90)))

    def test_spell_arrows(self):
        """Each of the four spell arrows' names: the heading SPELLARCHERS: (DSCLOG's own text), pushed
        where the game pushes its far pointer, the registers kept."""
        for name in sorted(spellarrows.ARROW_NAMES):
            with self.subTest(name=hex(name)):
                got = self.head(name)
                self.assertEqual(got[2:], ("SPELLARCHERS:", 0x7FC, BP, 0x1111, 0x2222, 0x3333))
                self.assertEqual(got[0], td.TSR)

    def test_other_items(self):
        """Plain arrows (name 36h), the names either side of the four, and anything else: the game's
        own DS:3493h, USEABLE BY:."""
        for name in (0x36, spellarrows.ARROWS[0].name - 1, spellarrows.ARROWS[-1].name + 1, 2):
            with self.subTest(name=hex(name)):
                self.assertEqual(self.head(name)[:4], (GAME_DS, USEABLE_BY, "USEABLE BY:", 0x7FC))


if __name__ == "__main__":
    unittest.main()
