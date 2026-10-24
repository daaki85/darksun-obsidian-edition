import struct
import unittest

from dsloader import game, shadows

HDR, BASE, TABLE_OFF = 0x9000, 0x8000, 0x200
DS, LOAD = 0x2000, 0x100


class Guest:
    def __init__(self):
        self.mem = bytearray(0x110000)

    def read(self, at, n):
        return bytes(self.mem[at:at + n])

    def write(self, at, data):
        self.mem[at:at + len(data)] = data


class Game:
    """Things 0 (a living creature), 1 (a dead one), 2 (an item), 300 (a living creature), 301 (a
    dying one)."""

    def __init__(self):
        self.guest, self.ds, self.load_seg, self.area = Guest(), DS, LOAD, 0x29
        things = (LOAD + game.COMBATANTS_SEG) * 16 + game.COMBATANTS_OFF
        for thing, kind, index in ((0, 2, 0), (1, 2, 1), (2, 1, 5), (300, 2, 2), (301, 2, 3)):
            self.guest.write(things + thing * 3, struct.pack("<Bh", kind, index))
        self.records = {i: bytearray(game.CREATURE_SIZE) for i in range(4)}
        for i, rec in self.records.items():
            rec[game.CREATURE_NAME] = ord("A")
        self.records[1][game.CREATURE_STATUS] = shadows.STATUS_DEAD
        self.records[3][game.CREATURE_STATUS] = shadows.STATUS_DYING
        self.guest.write(HDR + shadows.TSR_HDR_OFF, struct.pack("<H", HDR - BASE))
        self.guest.write(HDR + shadows.TSR_TABLE, struct.pack("<H", TABLE_OFF))

    def creature(self, i):
        return bytes(self.records.get(i, b""))

    def region(self):
        return self.area

    def word(self, at):
        return struct.unpack("<H", self.guest.read(at, 2))[0]

    def redrawn(self):
        """The view asked to be drawn again (and the request taken, as DSCLOG does)."""
        asked = self.word(HDR + shadows.TSR_VIEW_REDRAW)
        self.guest.write(HDR + shadows.TSR_VIEW_REDRAW, b"\0\0")
        return bool(asked)


class ShadowsTests(unittest.TestCase):
    def test_casting(self):
        """The living creatures among all 520 things: not the dying or dead, not items."""
        table = shadows.casting(Game())
        self.assertEqual(len(table), (shadows.THINGS + 7) // 8)
        self.assertEqual([t for t in range(shadows.THINGS) if table[t // 8] >> t % 8 & 1], [0, 300])

    def test_update(self):
        """On: DSCLOG's switch, its table, the darker colours asked for (and again after an area
        change), the view drawn again (DSCLOG asked: no figure marked changed); off: drawn again
        without."""
        gd, s = Game(), shadows.Shadows()
        s.update(gd, HDR, True, 100.0)
        self.assertEqual(gd.word(HDR + shadows.TSR_ON), 1)
        self.assertEqual(gd.word(HDR + shadows.TSR_BUILD), 1)
        self.assertEqual(gd.guest.read(BASE + TABLE_OFF, 3), b"\x01\x00\x00")
        self.assertEqual(gd.guest.read(BASE + TABLE_OFF + 300 // 8, 1), bytes((1 << 300 % 8,)))
        gd.guest.write(HDR + shadows.TSR_BUILD, struct.pack("<H", 0))  # (DSCLOG made them)
        s.update(gd, HDR, True, 100.3)
        self.assertFalse(gd.redrawn())
        s.update(gd, HDR, True, 101.0)
        self.assertTrue(gd.redrawn())
        self.assertEqual(s.palettes, 1)
        self.assertEqual(gd.word(HDR + shadows.TSR_BUILD), 0)
        gd.area = 0x2A  # (another area: its palette)
        s.update(gd, HDR, True, 102.0)
        self.assertEqual(gd.word(HDR + shadows.TSR_BUILD), 0)
        s.update(gd, HDR, True, 102.0 + shadows.BUILD_AFTER[0])
        self.assertEqual(gd.word(HDR + shadows.TSR_BUILD), 1)
        s.update(gd, HDR, False, 110.0)
        self.assertEqual(gd.word(HDR + shadows.TSR_ON), 0)
        self.assertTrue(gd.redrawn())  # (drawn again: the shadows gone)


if __name__ == "__main__":
    unittest.main()


class ShadowGoneTests(unittest.TestCase):
    """DSCLOG's SHADOW_GONE, as it draws: a creature dying or dead casts no shadow (and its new
    pictures aren't loaded from the floor routine), whatever SHADOW_TAB still says."""

    def test_shadow_gone(self):
        try:
            from unicorn import Uc, UC_ARCH_X86, UC_MODE_16
            from unicorn import x86_const as r
        except ImportError:
            self.skipTest("unicorn is not installed")
        import os
        here = os.path.dirname(__file__)
        with open(os.path.join(here, "..", "dos", "DSCLOG.EXE"), "rb") as f:
            image = f.read()[32:]
        at = image.find(bytes.fromhex("50560 68cd8".replace(" ", "")))
        self.assertGreater(at, 0)
        tsr, ds, ss, creatures = 0x1000, 0x5000, 0x9000, 0x7000
        things_seg = (ds + 0x3972 - 0x4356) & 0xFFFF
        mu = Uc(UC_ARCH_X86, UC_MODE_16)
        mu.mem_map(0, 0x110000)
        mu.mem_write(tsr * 16, image)
        mu.mem_write(ds * 16 + 0x1665, struct.pack("<HH", 0, creatures))
        for thing, kind, index, status in ((5, 2, 1, 1), (6, 2, 2, 4), (7, 2, 3, 5), (8, 1, 5, 0), (9, 2, 4, 0)):
            mu.mem_write(things_seg * 16 + 0xC36 + thing * 3, struct.pack("<Bh", kind, index))
            mu.mem_write(creatures * 16 + index * 0x3A + 0x1C, bytes((status,)))
        mu.mem_write(ss * 16 + 0x7FC, struct.pack("<H", 0xFFF0))
        for thing, gone in ((5, False), (6, True), (7, True), (8, False), (9, False)):
            with self.subTest(thing=thing):
                for name, value in dict(cs=tsr, ds=ds, ss=ss, esp=0x7FC, ebx=thing, es=0x1234, esi=0x5678,
                                        eax=0x9ABC, eflags=2).items():
                    mu.reg_write(getattr(r, "UC_X86_REG_" + name.upper()), value)
                mu.emu_start(tsr * 16 + at, tsr * 16 + 0xFFF0)
                self.assertEqual(bool(mu.reg_read(r.UC_X86_REG_EFLAGS) & 1), gone)
                self.assertEqual([mu.reg_read(x) for x in (r.UC_X86_REG_BX, r.UC_X86_REG_ES, r.UC_X86_REG_SI,
                                                           r.UC_X86_REG_AX)], [thing, 0x1234, 0x5678, 0x9ABC])
