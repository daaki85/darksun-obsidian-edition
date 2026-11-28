"""Shattered Lands' engine fixes found missing in Wake of the Ravager by the engine fixes' audit (2026-11-28,
GAME-BUGS.md): the Loader's patches at the sequel's addresses (with DSUN_WOTR, its DSUN.EXE's bytes) and
DSCLOG2's sites run in an emulated CPU (needs nasm and unicorn, else skipped): a natural 20 and "can't save"
(SAVE_SUM, SAVE_NAT, sites 220-221) and the quiver's last arrow (AMMO_CAP, AMMO_TURN, AMMO_OKAY, 217-219)."""

import os
import shutil
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dsloader import gamepatch, ravager  # noqa: E402
import test_ravkits  # noqa: E402

try:
    from unicorn import Uc, UC_ARCH_X86, UC_MODE_16
    from unicorn import x86_const as r
except ImportError:
    Uc = None

WOTR = os.environ.get("DSUN_WOTR")
TSR, SS = 0x1000, 0x4000
HALT = 0xFFF0
BP = 0x7F0  # (the game's frame in SS: its locals under, its arguments over)
ZF, CF, SF, OF = 0x40, 0x01, 0x80, 0x800
FIXES = ("scare_elves", "save_natural", "save_sum", "save_nat", "ammo_cap", "ammo_turn", "ammo_okay_1",
         "ammo_okay_2", "ammo_okay_3", "script_buffer")


class PatchTests(unittest.TestCase):
    def test_new_as_okay(self):
        """23 of SL's 24 tests for Okay, each a jz made jbe or a jnz ja; the attack command's three AMMO_OKAY's."""
        patches = {p.name: p for p in ravager.PATCHES}
        okay = [p for p in ravager.PATCHES if p.name.startswith(("new_okay_", "ammo_okay_"))]
        self.assertEqual(len(okay), 23)
        for p in okay:
            self.assertEqual(p.original[:5], bytes.fromhex("26807f1401"), p.name)
            self.assertEqual(p.replacement[-1], {0x74: 0x76, 0x75: 0x77}[p.original[-1]], p.name)
        for name in FIXES:
            self.assertIn(name, patches)
        self.assertEqual(patches["script_buffer"].replacement[2:], struct.pack("<I", gamepatch.SCRIPT_BUFFER))

    @unittest.skipUnless(WOTR, "needs DSUN_WOTR (Wake of the Ravager's folder)")
    def test_the_sequels_bytes(self):
        with open(os.path.join(WOTR, "DSUN.EXE"), "rb") as f:
            exe = f.read()
        for p in ravager.PATCHES:
            if p.name in FIXES or p.name.startswith("new_okay_"):
                self.assertEqual(exe[p.offset:p.offset + len(p.original)], p.original, p.name)


@unittest.skipUnless(Uc and shutil.which("nasm"), "needs unicorn and nasm")
class SiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from test_dsclog_drawing import build
        exe, cls.sym = build(test_ravkits.ASM)
        cls.image = exe[struct.unpack_from("<H", exe, 8)[0] * 16:]

    def setUp(self):
        self.mu = Uc(UC_ARCH_X86, UC_MODE_16)
        self.mu.mem_map(0, 0x100000)
        self.mu.mem_write(TSR * 16, self.image)
        self.mu.mem_write(TSR * 16 + HALT, b"\xf4" * 16)

    def frame(self, at, value, size=2):
        self.mu.mem_write(SS * 16 + BP + at, struct.pack("<h" if size == 2 else "<b", value))

    def local(self, at, size=2):
        data = bytes(self.mu.mem_read(SS * 16 + BP + at, size))
        return struct.unpack("<h" if size == 2 else "<b", data)[0]

    def word(self, name):
        return struct.unpack("<h", bytes(self.mu.mem_read(TSR * 16 + self.sym[name], 2)))[0]

    def site(self, routine, **regs):
        """ROUTINE entered as SITE leaves it (the INT's frame on the stack, the game's BP); its flags as it returns."""
        sp = BP - 0x40
        self.mu.mem_write(SS * 16 + sp, struct.pack("<HHH", HALT, TSR, 0x2))
        for name, value in dict(cs=TSR, ds=SS, es=SS, ss=SS, esp=sp, eflags=0x2, ebp=BP, **regs).items():
            self.mu.reg_write(getattr(r, "UC_X86_REG_" + name.upper()), value)
        self.mu.emu_start(TSR * 16 + self.sym[routine], TSR * 16 + HALT, count=2000)
        self.assertEqual(self.mu.reg_read(r.UC_X86_REG_IP), HALT)
        return self.mu.reg_read(r.UC_X86_REG_EFLAGS)

    def save(self, d20, modifiers, bonus, needed):
        """A save's total as the sequel's routine leaves it: the d20 in [BP-2], SAVE_SUM with the modifiers,
        SAVE_NAT with the race's or CON's bonus; the number needed in [BP-1]."""
        self.frame(-2, d20, 1)
        self.frame(-1, needed, 1)
        self.site("save_sum", eax=modifiers & 0xFF)
        self.assertEqual(self.mu.reg_read(r.UC_X86_REG_DL), self.local(-2, 1) & 0xFF)
        self.site("save_nat", eax=bonus & 0xFF)
        return self.local(-2, 1)

    def test_a_natural_20_saves(self):
        self.assertEqual(self.save(20, -3, 0, 18), 18)  # (short of it: made the number needed)
        self.assertEqual(self.save(20, 2, 1, 18), 23)  # (over it: kept)
        self.assertEqual(self.save(19, -3, 0, 18), 16)  # (not a natural 20: as rolled)

    def test_cant_save_isnt_saved_on_a_20(self):
        self.assertEqual(self.save(20, -100, 0, 10), -80)
        self.assertEqual(self.save(20, -100, 7, 10), -73)

    def test_the_sum_stays_in_its_byte(self):
        self.assertEqual(self.save(19, 100, 7, 10), 117)  # (110 then the bonus: not 126 wrapped)
        self.assertEqual(self.save(1, -120, 0, 10), -110)
        self.assertEqual(self.word("sv_nat") & 0xFF, 0)

    def shot(self, attacker, attacks, arrows):
        """AMMO_CAP: a shot of ATTACKS a round by ATTACKER ([BP+0Eh]), ARROWS left ([BP-8])."""
        self.frame(0x0E, attacker)
        self.frame(-0x0A, attacks)
        self.frame(-8, arrows)
        self.site("ammo_cap")
        self.assertEqual(self.local(-0x0A), arrows)  # (cut as the game cuts it)
        self.assertEqual(self.word("ammo_real"), attacks)

    def turn(self, made):
        """AMMO_TURN with MADE attacks made: whether the game's "jl" (round not spent) is taken."""
        flags = self.site("ammo_turn", eax=made)
        return bool(flags & SF) != bool(flags & OF)

    def okay(self, attacker, status):
        """AMMO_OKAY in the attack command (its attacker [BP-0Eh]) for a target of STATUS: whether the jbe
        (Okay, or New) is taken."""
        self.mu.mem_write(SS * 16 + 0x100 + 0x14, bytes((status,)))
        self.frame(-0x0E, attacker)
        flags = self.site("ammo_okay", ebx=0x100)
        return bool(flags & (ZF | CF))

    def test_a_party_archer_keeps_the_turn(self):
        self.shot(0, 2, 1)
        self.assertTrue(self.turn(1))  # (one of two made: not spent)
        self.assertEqual(self.word("ammo_out"), 0)
        self.assertFalse(self.okay(0, 1))  # (its target, Okay, answers as fallen: the turn goes on)
        self.assertTrue(self.okay(1, 1))  # (another's: the game's)
        self.assertEqual(self.word("ammo_real"), -1)

    def test_a_monster_and_a_shot_not_cut(self):
        self.shot(5, 2, 1)
        self.assertFalse(self.turn(1))  # (the game's way: against the cut)
        self.assertEqual(self.word("ammo_out"), -1)
        self.assertTrue(self.okay(5, 1))
        self.frame(0x0E, 0)
        self.frame(-0x0A, 2)
        self.assertTrue(self.turn(1))  # (no cut: against [BP-0Ah])
        self.assertFalse(self.turn(2))
        self.assertEqual(self.word("ammo_out"), -1)

    def test_a_round_spent(self):
        self.shot(1, 2, 1)
        self.assertFalse(self.turn(2))
        self.assertEqual(self.word("ammo_out"), -1)
        self.assertFalse(self.okay(1, 2))  # (a fallen target: the game's answer, fallen)
        self.assertTrue(self.okay(1, 0))  # (New counts as Okay)


if __name__ == "__main__":
    unittest.main()
