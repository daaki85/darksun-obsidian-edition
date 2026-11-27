"""Shattered Lands' fixes of the game's own bugs carried to Wake of the Ravager (GAME-BUGS.md's sequel table):
DSCLOG2's GL_ARMOUR (site 242: the gladiator's armour optimisation only with armour on) run in an emulated CPU
on a party member's items in fake memory, and the Loader's data fixes (an archer's pointer, the roster's
DELETE, Slay Living's description, CHOOSE A SPELL's grid) against the sequel's files (DSUN_WOTR). Needs nasm
and unicorn for the helper's part."""

import os
import shutil
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dsloader import gff, ravager, spelltexts  # noqa: E402
from test_ravkits import ASM  # noqa: E402

try:
    from unicorn import Uc, UC_ARCH_X86, UC_MODE_16
    from unicorn import x86_const as r
except ImportError:
    Uc = None

TSR, GDS, SS = 0x1000, 0x6000, 0x7000
CREATURES, ITEMS, TYPES, SHEETS = 0x4800, 0x4900, 0x4A00, 0x4B00
FIGHTERS = GDS + 0x3F49 - 0x47E0  # (the combatants' segment: DSCLOG2's FIGHTERS_SEG)
HLT = 0xFFF0
WOTR = os.environ.get("DSUN_WOTR")


@unittest.skipIf(Uc is None or not shutil.which("nasm"), "needs unicorn and nasm")
class GladiatorArmourTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from test_dsclog_drawing import build
        exe, cls.sym = build(ASM)
        cls.image = exe[struct.unpack_from("<H", exe, 8)[0] * 16:]

    def setUp(self):
        mu = self.mu = Uc(UC_ARCH_X86, UC_MODE_16)
        mu.mem_map(0, 0x100000)
        mu.mem_write(TSR * 16, self.image)
        mu.mem_write(TSR * 16 + HLT, b"\xF4")
        mu.mem_write(GDS * 16 + 0x19C1, struct.pack("<HH", 0, ITEMS))
        mu.mem_write(GDS * 16 + 0x19C9, struct.pack("<HH", 0, CREATURES))
        mu.mem_write(GDS * 16 + 0x19CD, struct.pack("<HH", 0, TYPES))
        for c in range(4):  # (every creature's item lists empty: 9999)
            mu.mem_write(CREATURES * 16 + c * 0x31 + 8, struct.pack("<HHH", 9999, 9999, 9999))

    def wear(self, creature: int, slot: int, kind_flags: int = 0x80, worn: int = 2) -> None:
        """CREATURE's first list holding one item (thing 10, kind 1: an item), item 0 of type 5 in SLOT."""
        mu = self.mu
        mu.mem_write(CREATURES * 16 + creature * 0x31 + 8, struct.pack("<H", 10))
        mu.mem_write(FIGHTERS * 16 + 0xC33 + 10 * 3, struct.pack("<BH", 1, 0))
        rec = bytearray(0x17)
        struct.pack_into("<H", rec, 4, 9999)  # (no next)
        struct.pack_into("<H", rec, 0x0A, 5)
        rec[0x13] = slot
        mu.mem_write(ITEMS * 16, bytes(rec))
        typ = bytearray(15)
        typ[0x0B], typ[0x05], typ[0x04] = kind_flags, worn, 0x05  # (armour, worn on the chest, leather)
        mu.mem_write(TYPES * 16 + 5 * 15, bytes(typ))

    def ac_test(self, gladiator: bool, thing: int = 2) -> bool:
        """The AC routine's test at site 242 (ES:BX the sheet, SI the thing): True where it gives the bonus."""
        mu = self.mu
        mu.mem_write(SHEETS * 16 + 0x10, struct.pack("<H", 0x40 if gladiator else 0x01))
        mu.mem_write(FIGHTERS * 16 + 0xC33 + thing * 3, struct.pack("<BH", 2, thing))
        sp = 0x7F0  # (INT's frame, the game's flags in it: RETF 2 gives back GL_ARMOUR's own)
        mu.mem_write(SS * 16 + sp - 6, struct.pack("<HHH", HLT, TSR, 0x2))
        for reg, value in dict(cs=TSR, ds=GDS, es=SHEETS, ss=SS, esp=sp - 6, ebx=0, esi=thing, eflags=0x2).items():
            mu.reg_write(getattr(r, "UC_X86_REG_" + reg.upper()), value)
        mu.emu_start(TSR * 16 + self.sym["gl_armour"], TSR * 16 + HLT, count=100000)
        self.assertEqual(mu.reg_read(r.UC_X86_REG_ESP) & 0xFFFF, sp)
        self.assertEqual(mu.reg_read(r.UC_X86_REG_ES), SHEETS)
        return not mu.reg_read(r.UC_X86_REG_EFLAGS) & 0x40

    def test_a_gladiator_in_armour(self):
        self.wear(2, 9)  # (chest)
        self.assertTrue(self.ac_test(True))

    def test_a_gladiator_with_none(self):
        self.assertFalse(self.ac_test(True))
        self.assertEqual(struct.unpack_from("<H", self.mu.mem_read(TSR * 16 + self.sym["hdr"] + 2118, 2))[0], 1)

    def test_not_a_gladiator(self):
        self.wear(2, 9)
        self.assertFalse(self.ac_test(False))

    def test_a_shield_or_pack_is_none(self):
        self.wear(2, 1)  # (the off hand: a shield's place)
        self.assertFalse(self.ac_test(True))
        self.wear(2, 14)  # (the backpack)
        self.assertFalse(self.ac_test(True))
        self.wear(2, 9, worn=3)  # (bracers of no material: not armour)
        self.mu.mem_write(TYPES * 16 + 5 * 15 + 4, bytes((0x40,)))
        self.assertFalse(self.ac_test(True))


@unittest.skipUnless(WOTR, "needs the sequel's files (DSUN_WOTR)")
class FileTests(unittest.TestCase):
    def test_the_patches_find_the_sequels_bytes(self):
        with open(os.path.join(WOTR, "DSUN.EXE"), "rb") as f:
            exe = f.read()
        for name in ("shots_left", "roster_delete", "gladiator_armour", "lock_site"):
            p = next(p for p in ravager.PATCHES if p.name == name)
            self.assertEqual(exe[p.offset:p.offset + len(p.original)], p.original, name)
        # (the roster's "mov ax,2F8h" where the game's were: the loader fixes their segment up)
        p = next(p for p in ravager.PATCHES if p.name == "roster_delete")
        self.assertEqual([p.replacement[i:i + 3] for i in (7, 30)], [bytes.fromhex("b8f802")] * 2)

    def test_slay_living_and_the_grid(self):
        with open(os.path.join(WOTR, "RESOURCE.GFF"), "rb") as f:
            data = f.read()
        self.assertEqual(gff.read_gff(data)[("SPIN", 205)], ravager.SLAY_TEXT_OLD)
        out, done = ravager.resources_fixed(data)
        chunks = gff.read_gff(out)
        self.assertIn(ravager.SLAY_TEXT, done)
        self.assertEqual(chunks[("SPIN", 205)], spelltexts.TEXTS[137].encode() + b"\r\n")
        self.assertIn(ravager.SPELL_GRID, done)
        from dsloader import spellgrid
        self.assertEqual(chunks[("WIND", spellgrid.WINDOW)], spellgrid.relaid(gff.read_gff(data)[("WIND", spellgrid.WINDOW)]))
        out, done = ravager.resources_fixed(data, skip={ravager.SLAY_TEXT, ravager.SPELL_GRID})
        self.assertEqual(gff.read_gff(out)[("SPIN", 205)], ravager.SLAY_TEXT_OLD)


if __name__ == "__main__":
    unittest.main()
