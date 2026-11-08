"""The spells as the manual has them (gamepatch.SPELLS_MANUAL): the record patches, Stinking Cloud's
round more (DSCLOG's STINK_SITE, and the Loader's duration texts), Chaos's INT exception
(CHAOS_SITE), Free Action's loop over the effects it removes."""
import os
import struct
import unittest

from dsloader import game, gamepatch

try:
    from unicorn import Uc, UC_ARCH_X86, UC_MODE_16
    from unicorn import x86_const as r
except ImportError:  # pragma: no cover
    Uc = None


class DurationBonusTests(unittest.TestCase):
    def test_stinking_cloud_round_more(self):
        manual = bytes(4) + bytes((0x41,)) + bytes(27)
        plain = bytes(4) + bytes((0x61,)) + bytes(27)
        self.assertEqual(game.duration_bonus(game.STINKING_CLOUD, manual), 1)
        self.assertEqual(game.duration_bonus(game.STINKING_CLOUD, plain), 0)
        self.assertEqual(game.duration_bonus(21, manual), 0)

    def test_the_patches_are_the_switchs(self):
        names = {p.name for p in gamepatch.PATCHES}
        self.assertTrue(set(gamepatch.SPELLS_MANUAL) <= names)


@unittest.skipIf(Uc is None, "unicorn is not installed")
class FreeActionLoopTests(unittest.TestCase):
    """The patched handler (79406h-79432h) run with its far calls as stand-ins: the effects removed,
    in order, by spell and by whether the creature is Poisoned."""
    BASE = 0x79406

    def run_from(self, entry: int, poisoned: bool):
        code = bytearray(0x2D)
        for p in gamepatch.PATCHES:
            if p.offset >= self.BASE and p.offset + len(p.replacement) <= self.BASE + len(code) and p.name.startswith("free_action"):
                code[p.offset - self.BASE:p.offset - self.BASE + len(p.replacement)] = p.replacement
        # (the two far calls made near calls to a stand-in at +100h, which notes [sp+4], the
        # effect's id, in a list at 0:5000h, its count at 0:4FFEh; the end, 79430h, an HLT)
        code += bytes(0x100 - len(code))
        for at in (0x79409, 0x79425):
            o = at - self.BASE
            code[o:o + 5] = bytes((0xE8,)) + struct.pack("<H", 0x100 - (o + 3)) + b"\x90\x90"
        code[0x79430 - self.BASE] = 0xF4
        code += bytes.fromhex("5589e58b46068b1efe4f88870050ff06fe4f5dc3")
        mu = Uc(UC_ARCH_X86, UC_MODE_16)
        mu.mem_map(0, 0x100000)
        cs = 0x1000
        mu.mem_write(cs * 16, bytes(code))
        # the effect bitset: a far pointer at [bp+0Ah] (bp 0x7F00), its +4 bit 8 Poisoned
        mu.mem_write(0x7F0A, struct.pack("<HH", 0x7E00, 0))
        mu.mem_write(0x7E04, bytes((0x08 if poisoned else 0,)))
        for name, value in dict(cs=cs, ds=0, es=0, ss=0, esp=0x7000, ebp=0x7F00, edi=5).items():
            mu.reg_write(getattr(r, "UC_X86_REG_" + name.upper()), value)
        mu.emu_start(cs * 16 + entry - self.BASE, cs * 16 + 0x79430 - self.BASE, count=500)
        n = struct.unpack("<H", mu.mem_read(0x4FFE, 2))[0]
        self.assertEqual(mu.reg_read(r.UC_X86_REG_SP), 0x7000)
        return list(mu.mem_read(0x5000, n))

    def test_free_action(self):
        self.assertEqual(self.run_from(0x79422, False), [0x33, 0x2F, 0x22])
        self.assertEqual(self.run_from(0x79422, True), [0x33, 0x2F])

    def test_remove_paralysis(self):
        self.assertEqual(self.run_from(0x7942C, False), [0x2F, 0x22])
        self.assertEqual(self.run_from(0x7942C, True), [0x2F])


if __name__ == "__main__":
    unittest.main()
