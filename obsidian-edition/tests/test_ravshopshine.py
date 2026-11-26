"""A shop's magic items shine in the sequel (DSCLOG2's SHOP_SHINE, site 163, and SHINE_TURN in SHOP_LOOP): the
wait's test, with no event, makes the game's jump and turns the colour cycles as the map's loop does, only on a
shop's screen and when the timer asked; with an event it is the game's. Emulated (nasm and unicorn, else
skipped); with DSUN_WOTR the sequel's own bytes where it patches and calls."""

import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dsloader import ravager  # noqa: E402

try:
    from unicorn import x86_const as r
    from test_dsclog_drawing import Scene, TSR, GAME_DS, SS
except ImportError:
    Scene = None

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASM = os.path.join(HERE, "dos", "dsclog2.asm")
WOTR = os.environ.get("DSUN_WOTR")
SHINE_TURNS = 1982
SHOP_SCREEN, SHINE_DUE = 0x143D, 0x1424
CYCLER = (GAME_DS - (0x47E0 - 0x2796)) if Scene else 0


@unittest.skipIf(Scene is None, "nasm or unicorn not installed")
class ShopShineTests(unittest.TestCase):
    def run_site(self, di, screen=1, due=1):
        s = Scene(ASM)
        s.word("pointer_ds", GAME_DS)
        s.ds(SHOP_SCREEN, bytes((screen,)))
        s.ds(SHINE_DUE, bytes((due,)))
        s.mu.mem_write(CYCLER * 16 + 0x047C, bytes.fromhex("2ec6067a0477cb"))  # (mov byte cs:[047Ah],77h / retf)
        sp = 0x700
        s.mu.mem_write(SS * 16 + sp, struct.pack("<HHH", 0xFFF0, TSR, 0x2))
        s.mu.mem_write(TSR * 16 + 0xFF00, b"\xf4" * 0x100)
        for reg, value in dict(cs=TSR, ds=0x1111, ss=SS, esp=sp, ebp=0x900, edi=di, eflags=0x2).items():
            s.mu.reg_write(getattr(r, "UC_X86_REG_" + reg.upper()), value)
        try:
            s.mu.emu_start(TSR * 16 + s.sym["shop_shine"], 0, count=2000)
        except Exception:
            pass
        ip = s.mu.reg_read(r.UC_X86_REG_IP) - 1
        turned = s.mu.mem_read(CYCLER * 16 + 0x047A, 1)[0] == 0x77
        regs = (s.mu.reg_read(r.UC_X86_REG_DS), s.mu.reg_read(r.UC_X86_REG_BP), s.mu.reg_read(r.UC_X86_REG_SP))
        return s, ip, turned, regs

    def test_no_event_turns_and_jumps(self):
        s, ip, turned, regs = self.run_site(0)
        self.assertEqual(ip, 0xFFF0 - 0x4A)  # (the jz's target: 4Bh back from the instruction after it)
        self.assertTrue(turned)
        self.assertEqual(s.mu.mem_read(GAME_DS * 16 + SHINE_DUE, 1)[0], 0)
        self.assertEqual(struct.unpack("<H", s.get("hdr", 2, SHINE_TURNS))[0], 1)
        self.assertEqual(regs, (0x1111, 0x900, 0x700 + 6))

    def test_an_event_is_the_games(self):
        _, ip, turned, _ = self.run_site(5)
        self.assertEqual(ip, 0xFFF0)
        self.assertFalse(turned)

    def test_not_asked_or_no_shop(self):
        for kw in ({"due": 0}, {"screen": 0}):
            s, ip, turned, _ = self.run_site(0, **kw)
            self.assertEqual(ip, 0xFFF0 - 0x4A, kw)
            self.assertFalse(turned, kw)

    def test_site(self):
        src = open(ASM).read()
        self.assertRegex(src, r"\n        dw shop_shine +; 163 SITE_SHOP_SHINE")


class PatchTests(unittest.TestCase):
    def test_patch(self):
        p = next(p for p in ravager.PATCHES if p.name == "shop_shine")
        self.assertEqual((p.offset, p.original, p.replacement), (0x2F7BE, bytes.fromhex("0bff74b5"),
                                                                 bytes((0xCD, 0xF5, 163, 0x90))))

    @unittest.skipUnless(WOTR, "DSUN_WOTR: the player's Wake of the Ravager")
    def test_the_games_bytes(self):
        data = open(os.path.join(WOTR, "DSUN.EXE"), "rb").read()
        self.assertEqual(data[0x2F7BE:0x2F7C2], bytes.fromhex("0bff74b5"))
        # (the map's loop: "cmp byte [1424h],0 / jz / call far 2796:047C / mov byte [1424h],0"; the cycler's start)
        self.assertEqual(data[0x1CF0E:0x1CF1F], bytes.fromhex("803e241400740a9a7c049627c606241400"))
        self.assertEqual(data[0x2CFDC:0x2CFE6], bytes.fromhex("558bec83ec021e065756"))
        self.assertEqual(data[0x2F7C2 - 0x4B:0x2F7C2 - 0x4B + 5], bytes.fromhex("9a03009730"))


if __name__ == "__main__":
    unittest.main()
