"""DSCLOG2's RG_TWO in Wake of the Ravager (site 78, run in an emulated CPU): Shattered Lands' ranger part of
AD&D's two weapons (DSCLOG's RG_TWO, game.GameData.two_weapons): a ranger has no two-weapon penalty only in
light armour (leather, or of no material); in armour that isn't light, ZF set as for anyone else, on to
PROBE_TWO's penalty; with the rule's bit clear a ranger keeps the game's ease in any armour. And the patch at
the sequel's test for a ranger (5DE67h). Needs nasm and unicorn, else skipped; the patch's bytes in the game's
own program with DSUN_WOTR."""

import os
import shutil
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dsloader import game, ravager  # noqa: E402

try:
    from unicorn import Uc, UC_ARCH_X86, UC_MODE_16
    from unicorn import x86_const as r
except ImportError:
    Uc = None

ASM = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dos", "dsclog2.asm")
WOTR = os.environ.get("DSUN_WOTR")
TSR, GAME_DS, SS = 0x1000, 0x5000, 0x4000
SHEETS, CREATURES, ITEMS, TYPES = 0x6000, 0x6800, 0x7000, 0x7800
BP = 0x600
RANGER = 0x200          # (the sheet's +10h)
NO_ITEM = 9999
CREATURE, THING, ITEM, TYPE = 3, 0x201, 5, 2
METAL, LEATHER, NONE = 4, 5, 0x40  # (an item type's +4: its material)


@unittest.skipIf(Uc is None or not shutil.which("nasm"), "needs unicorn and nasm")
class RangerTwoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from test_dsclog_drawing import build
        exe, cls.sym = build(ASM)
        cls.image = exe[struct.unpack_from("<H", exe, 8)[0] * 16:]

    def machine(self, rules, ranger=True, material=METAL, worn=True):
        mu = Uc(UC_ARCH_X86, UC_MODE_16)
        mu.mem_map(0, 0x100000)
        mu.mem_write(TSR * 16, self.image)
        mu.mem_write(TSR * 16 + 0xFFF0, bytes((0xF4,)))
        mu.mem_write(TSR * 16 + self.sym["rules"], struct.pack("<H", rules))
        ds = GAME_DS * 16
        for ptr, seg in ((0x19C9, CREATURES), (0x19C1, ITEMS), (0x19CD, TYPES), (0x19C5, SHEETS)):
            mu.mem_write(ds + ptr, struct.pack("<HH", 0, seg))
        mu.mem_write(SHEETS * 16 + CREATURE * 0x48 + 0x10, struct.pack("<H", RANGER if ranger else 0x10))
        creature = CREATURES * 16 + CREATURE * 0x31
        mu.mem_write(creature + 4, struct.pack("<H", CREATURE))
        mu.mem_write(creature + 8, struct.pack("<HHH", THING if worn else NO_ITEM, NO_ITEM, NO_ITEM))
        fighters = (GAME_DS + 0x3F49 - 0x47E0) * 16 + 0x0C33 + THING * 3
        mu.mem_write(fighters, bytes((1,)) + struct.pack("<H", ITEM))
        item = ITEMS * 16 + ITEM * 0x17
        mu.mem_write(item + 4, struct.pack("<H", NO_ITEM))
        mu.mem_write(item + 0x0A, struct.pack("<H", TYPE))
        mu.mem_write(item + 0x13, bytes((9,)))  # (worn on the chest)
        typ = bytearray(0x0F)
        typ[4], typ[5], typ[0x0B] = material, 9, 0x80  # (armour, worn on the chest)
        mu.mem_write(TYPES * 16 + TYPE * 0x0F, bytes(typ))
        return mu

    def zf(self, mu):
        """RG_TWO as the game's INT reaches it (the sheet ES:BX, the creature [BP-2]): ZF as it gives back
        (set: on to PROBE_TWO's penalty; clear: the game's jump to none)."""
        mu.mem_write(SS * 16 + BP - 2, struct.pack("<H", CREATURE))
        mu.mem_write(SS * 16 + 0x7F0, struct.pack("<HHH", 0xFFF0, TSR, 0x2))
        regs = dict(cs=TSR, ds=GAME_DS, ss=SS, esp=0x7F0, ebp=BP, eflags=0x2, es=SHEETS, ebx=CREATURE * 0x48,
                    edx=0x1234)
        for name, value in regs.items():
            mu.reg_write(getattr(r, "UC_X86_REG_" + name.upper()), value)
        mu.emu_start(TSR * 16 + self.sym["rg_two"], TSR * 16 + 0xFFF0, count=100000)
        self.assertEqual((mu.reg_read(r.UC_X86_REG_SP), mu.reg_read(r.UC_X86_REG_BX),
                          mu.reg_read(r.UC_X86_REG_DX), mu.reg_read(r.UC_X86_REG_ES)),
                         (0x7F0 + 6, CREATURE * 0x48, 0x1234, SHEETS))
        return bool(mu.reg_read(r.UC_X86_REG_EFLAGS) & 0x40)

    def count(self, mu):
        return struct.unpack("<H", mu.mem_read(TSR * 16 + self.sym["rg_heavy"], 2))[0]

    def test_ranger_in_heavy_armour_takes_the_penalty(self):
        mu = self.machine(game.RULE_TWO_WEAPONS)
        self.assertTrue(self.zf(mu))
        self.assertEqual(self.count(mu), 1)

    def test_ranger_in_light_armour_or_none_has_none(self):
        for kw in (dict(material=LEATHER), dict(material=NONE), dict(worn=False)):
            mu = self.machine(game.RULE_TWO_WEAPONS, **kw)
            self.assertFalse(self.zf(mu), kw)
            self.assertEqual(self.count(mu), 0)

    def test_rule_off_the_games_ease(self):
        self.assertFalse(self.zf(self.machine(0)))

    def test_not_a_ranger(self):
        """Anyone else: ZF set, as the game's test gives it, in any armour."""
        for material in (METAL, LEATHER):
            self.assertTrue(self.zf(self.machine(game.RULE_TWO_WEAPONS, ranger=False, material=material)))

    def test_patch(self):
        p = next(p for p in ravager.PATCHES if p.name == "ranger_two")
        self.assertEqual((p.offset, p.original.hex()), (0x5DE67, "26f747100002"))
        self.assertEqual(p.replacement, bytes((0xCD, ravager.VEC_SITE, 78, 0x90, 0x90, 0x90)))

    @unittest.skipUnless(WOTR, "DSUN_WOTR (the sequel's folder) not given")
    def test_patch_in_the_game(self):
        with open(os.path.join(WOTR, "DSUN.EXE"), "rb") as f:
            exe = f.read()
        p = next(p for p in ravager.PATCHES if p.name == "ranger_two")
        self.assertEqual(exe[p.offset:p.offset + len(p.original)], p.original)
        # (the routine's: its test, "jnz 5DE86h" to no penalty, then two weapons ready? CAH_TWO's site)
        self.assertEqual(exe[p.offset + 6:p.offset + 8], bytes.fromhex("7517"))


if __name__ == "__main__":
    unittest.main()
