"""The item box's INFO for a Spellarcher's spell arrows (DSCLOG's INFO_ONLY): SPELLARCHER ONLY under
the game's USEABLE BY list, run in Unicorn at the game's bytes (gamepatch's info_only)."""
import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import gamepatch, spellarrows  # noqa: E402

import test_cahulaks as tc  # noqa: E402
import test_dsclog as td  # noqa: E402

SS, BP = td.SS, td.BP


def load_tests(loader, tests, pattern):  # (only this file's: not the cahulaks', inherited, again)
    suite = unittest.TestSuite()
    suite.addTests(InfoOnlyTests(name) for name in sorted(vars(InfoOnlyTests)) if name.startswith("test_"))
    return suite


@unittest.skipIf(td.Uc is None, "unicorn not installed")
class InfoOnlyTests(tc.CahulaksTests):
    STUB = 0x7000  # the game's text routine here: counts its calls, keeps its y, x and text

    def info(self, name, row=0x1B, names=1):
        """INFO_ONLY for an item named NAME, the list's next row ROW, NAMES members drawn: (the text
        routine's calls, its y, its x, the text drawn, AX after)."""
        stub = self.STUB
        # push bp / mov bp,sp / [bp+10h] y, [bp+0Eh] x, [bp+0Ah] the text's offset to cs:102h...
        # / inc word cs:[100h] / pop bp / retf
        self.mu.mem_write(stub * 16, bytes.fromhex(
            "5589e5" "8b4610" "2ea30201" "8b460e" "2ea30401" "8b460a" "2ea30601" "8b460c" "2ea30801"
            "2eff060001" "5d" "cb"))
        self.mu.mem_write(stub * 16 + 0x100, bytes(10))
        self.mu.mem_write(td.CALLER * 16 + self.at + 0x100 + 3 - 10, struct.pack("<HH", 0, stub))
        self.mu.mem_write(tc.ITEMS * 16 + 5 * 0x15 + 0x12, struct.pack("<H", name))
        self.frame(p6=5, p8=0x1234, pA=0x5678, m2=names)
        self.assertEqual(self.where("info_only", (), esi=row, eax=0x9999), "end")
        calls, y, x, off, seg = struct.unpack("<5H", self.mu.mem_read(stub * 16 + 0x100, 10))
        text = bytes(self.mu.mem_read(seg * 16 + off, 24)).split(b"\0")[0].decode() if calls else None
        return calls, y, x, text, self.mu.reg_read(td.r.UC_X86_REG_AX)

    def test_patch(self):
        p = tc.tg.patch("info_only")
        self.assertEqual((p.offset, p.original.hex()), (0x8C282, "8b46fe"))
        self.assertEqual(p.replacement, bytes((0xCD, 0x98, gamepatch.INFO_ONLY_SITE)))

    def test_spell_arrows(self):
        """Each of the four spell arrows' names: SPELLARCHER ONLY in the list's next row, at x 0Dh, and
        AX the names drawn ([BP-2]), as the game's own "mov ax,[bp-2]"."""
        for name in sorted(spellarrows.ARROW_NAMES):
            with self.subTest(name=hex(name)):
                self.assertEqual(self.info(name), (1, 0x1B, 0x0D, "SPELLARCHER ONLY", 1))

    def test_no_one(self):
        """With no member allowed the game drew NO ONE in SI's row and left SI there: the line goes
        under it."""
        self.assertEqual(self.info(0x16D, row=0x13, names=0), (1, 0x1B, 0x0D, "SPELLARCHER ONLY", 0))

    def test_other_items(self):
        """Plain arrows (name 36h), the Fine Bow and anything else: nothing drawn, AX as the game's."""
        for name in (0x36, spellarrows.ARROWS[0].name - 1, spellarrows.ARROWS[-1].name + 1, 2):
            with self.subTest(name=hex(name)):
                self.assertEqual(self.info(name, names=2)[0::4], (0, 2))

    def test_full_box(self):
        """Four names drawn (the row of the box's INFO button next): nothing more."""
        self.assertEqual(self.info(0x16D, row=0x0B + 8 * 5, names=4)[0::4], (0, 4))
        self.assertEqual(self.info(0x16D, row=0x0B + 8 * 4, names=3)[:2], (1, 0x2B))


if __name__ == "__main__":
    unittest.main()
