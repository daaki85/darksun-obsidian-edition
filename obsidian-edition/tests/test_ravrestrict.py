"""DSCLOG2's class restrictions on the mod's item types in Wake of the Ravager (CLASS_FORBIDS, run in an
emulated CPU): for each of the mod's 33 types (OBJEX2.GFF's 102-134, ravager.mod_type) and the classes
alone and together, the same answer as Shattered Lands' rules (restrict.allowed, its kits aside: the
sequel has none). Its kinds come from DSCLOG2's kind_of_type, which goes on past the sequel's 102
types (test_ravager.ItemTypeTests.test_mod_kinds_in_dsclog2). Needs nasm and unicorn, else skipped."""

import os
import shutil
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dsloader import game, npcitems, ravager, ravtransfer, restrict  # noqa: E402
import test_restrict  # noqa: E402

try:
    from unicorn import Uc, UC_ARCH_X86, UC_MODE_16
    from unicorn import x86_const as r
except ImportError:
    Uc = None

ASM = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dos", "dsclog2.asm")
TSR, GAME_DS, SS, TYPES = 0x1000, 0x3000, 0x4000, 0x8000
CLASSES = [(c,) for c in range(1, 18)] + [(9, 12), (9, 17), (9, 11), (13, 5), (13, 12), (12, 17), (1, 12),
                                          (9, 1), (9, 2), (9, 3), (9, 4), (17, 1), (11, 12)]


@unittest.skipIf(Uc is None or not shutil.which("nasm"), "needs unicorn and nasm")
class ModTypeRestrictionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from test_dsclog_drawing import build
        exe, cls.sym = build(ASM)
        cls.image = exe[struct.unpack_from("<H", exe, 8)[0] * 16:]

    def run_forbids(self, mu, sheet: bytes, item_type: int) -> bool:
        mu.mem_write(SS * 16 + 0x500, sheet)
        mu.mem_write(SS * 16 + 0x7FC, struct.pack("<H", 0xFFF0))
        for name, value in dict(cs=TSR, ds=GAME_DS, es=SS, ebx=0x500, edx=item_type, ss=SS, esp=0x7FC,
                                eflags=0x2).items():
            mu.reg_write(getattr(r, "UC_X86_REG_" + name.upper()), value)
        mu.emu_start(TSR * 16 + self.sym["class_forbids"], TSR * 16 + 0xFFF0)
        return bool(mu.reg_read(r.UC_X86_REG_EFLAGS) & 1)

    def test_as_shattered_lands(self):
        mu = Uc(UC_ARCH_X86, UC_MODE_16)
        mu.mem_map(0, 0x100000)
        mu.mem_write(TSR * 16, self.image)
        mu.mem_write(TSR * 16 + 0xFFF0, bytes((0xF4,)))  # (hlt: where CLASS_FORBIDS returns)
        mu.mem_write(GAME_DS * 16 + ravager_types_ptr(), struct.pack("<HH", 0, TYPES))
        table = bytes(ravager.TYPE_SIZE * ravager.GAME_TYPES) + b"".join(
            ravager.wotr_type(bytes.fromhex(t) if isinstance(t, str) else t) for t in npcitems.TYPES)
        mu.mem_write(TYPES * 16, table)
        refused = 0
        for classes in CLASSES:
            for race in (1, 2):
                sl = bytearray(test_restrict.sheet(*classes, race=race))
                if race == 1 and len(classes) > 1:
                    continue  # (a human's classes come one at a time: dual-class)
                wotr = ravtransfer.sheet(bytes(sl) + bytes(ravtransfer.SL_SHEET - len(sl)))
                for k, typ in enumerate(npcitems.TYPES):
                    sl_type = game.GAME_TYPES + k
                    record = bytes.fromhex(typ) if isinstance(typ, str) else typ
                    want = not restrict.allowed(bytes(sl), sl_type, record)
                    with self.subTest(classes=classes, race=race, type=sl_type):
                        self.assertEqual(self.run_forbids(mu, wotr, ravager.mod_type(sl_type)), want)
                    refused += want
        self.assertGreater(refused, 50)  # (the test means something: many refused)

    def test_armour_type(self):
        """ARMOUR_TYPE (CLASS_FORBIDS's and ARMOUR_WORN's: a multiclass preserver's casting) is
        restrict.is_armour on every one of the mod's types: its bracers, robes and Cloak of Protection
        not armour."""
        mu = Uc(UC_ARCH_X86, UC_MODE_16)
        mu.mem_map(0, 0x100000)
        mu.mem_write(TSR * 16, self.image)
        mu.mem_write(TSR * 16 + 0xFFF0, bytes((0xF4,)))
        kinds = []
        for k, typ in enumerate(npcitems.TYPES):
            mu.mem_write(TYPES * 16, ravager.wotr_type(typ))
            mu.mem_write(SS * 16 + 0x7FC, struct.pack("<H", 0xFFF0))
            for name, value in dict(cs=TSR, es=TYPES, ebx=0, ss=SS, esp=0x7FC, eflags=0x2).items():
                mu.reg_write(getattr(r, "UC_X86_REG_" + name.upper()), value)
            mu.emu_start(TSR * 16 + self.sym["armour_type"], TSR * 16 + 0xFFF0)
            got = bool(mu.reg_read(r.UC_X86_REG_EFLAGS) & 1)
            with self.subTest(type=game.GAME_TYPES + k):
                self.assertEqual(got, restrict.is_armour(typ))
            kinds.append((restrict.is_bracers(typ), restrict.is_robe(typ), typ[9] == restrict.CLOAK_SLOT, got))
        self.assertTrue(any(b for b, _, _, _ in kinds) and any(r_ for _, r_, _, _ in kinds)
                        and any(c for _, _, c, _ in kinds) and any(g for _, _, _, g in kinds))


def ravager_types_ptr() -> int:
    with open(ASM) as f:
        for line in f:
            if line.startswith("ITEM_TYPES_PTR equ"):
                return int(line.split()[2], 16)
    raise AssertionError("no ITEM_TYPES_PTR")


if __name__ == "__main__":
    unittest.main()
