"""Picking pockets in Wake of the Ravager (DSCLOG2's PICK POCKETS, sites 180-186; pickpocket.py through
ravlog's RavDiceLog._answer_pick): the header's words, the site table, the patches' bytes at the sequel's
addresses (with DSUN_WOTR), the purse's icon, the modules' names rebound for the sequel, and DSCLOG2's
routines run in an emulated CPU (needs nasm and unicorn, else skipped)."""

import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dsloader import dicelog, gff, icons, pickpocket, ravager, ravlog  # noqa: E402

try:
    from unicorn import Uc, UC_ARCH_X86, UC_MODE_16
    from unicorn import x86_const as r
except ImportError:
    Uc = None

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASM = os.path.join(HERE, "dos", "dsclog2.asm")
WOTR = os.environ.get("DSUN_WOTR")
DS = 0x5000
LOAD = DS - ravager.DGROUP
SITES = {"pp_show": 180, "pp_click": 181, "pp_lit": 182, "pp_arm": 183, "pp_text_hover": 184,
         "pp_text_info": 184, "pp_info": 185, "pp_hand": 186}


def built():
    from test_dsclog_drawing import build
    exe, sym = build(ASM)
    return exe[struct.unpack_from("<H", exe, 8)[0] * 16:], sym


class TableTests(unittest.TestCase):
    def test_patches_are_sites(self):
        """Each patch is DSCLOG2's SITE with its number, padded with NOPs over the bytes it replaces."""
        patches = {p.name: p for p in ravager.PATCHES if p.name in SITES}
        self.assertEqual(set(patches), set(SITES))
        for name, p in patches.items():
            self.assertEqual(p.replacement[:3], bytes((0xCD, ravager.VEC_SITE, SITES[name])), name)
            self.assertEqual(len(p.replacement), len(p.original), name)

    @unittest.skipUnless(WOTR, "DSUN_WOTR not set")
    def test_the_sequels_bytes(self):
        exe = open(os.path.join(WOTR, "DSUN.EXE"), "rb").read()
        for p in ravager.PATCHES:
            if p.name in SITES:
                self.assertEqual(exe[p.offset:p.offset + len(p.original)], p.original, p.name)

    @unittest.skipUnless(WOTR, "DSUN_WOTR not set")
    def test_purse_icon(self):
        """ICON 3048 in the copy: the earth Turn Undead's tile, its glyph off, a purse in its lines and a gold coin."""
        from dsloader import wotrart
        res = gff.read_gff(open(os.path.join(WOTR, ravager.RESOURCE_FILE), "rb").read())
        self.assertNotIn(("ICON", icons.PICK_ICON), res)
        out, done = ravager.resources_fixed(open(os.path.join(WOTR, ravager.RESOURCE_FILE), "rb").read())
        self.assertIn(ravager.PICK_BUTTON_ICON, done)
        purse = wotrart.decode_plnr(gff.read_gff(out)[("ICON", icons.PICK_ICON)])
        self.assertEqual((len(purse), len(purse[0])), (16, 16))
        self.assertEqual(purse[9][7], 100)
        self.assertEqual(purse[2][6], icons.RAV_TURN_DARK)  # (the purse's tie)
        out, done = ravager.resources_fixed(open(os.path.join(WOTR, ravager.RESOURCE_FILE), "rb").read(),
                                            skip={ravager.PICK_BUTTON_ICON})
        self.assertNotIn(("ICON", icons.PICK_ICON), gff.read_gff(out))

    def test_layout(self):
        """Shattered Lands' people and weapons worth XP aren't the sequel's: none while it is attached."""
        try:
            ravlog.apply_layout()
            self.assertEqual((pickpocket.LIFTABLE_TYPES, pickpocket.LIFTABLE_NAMES, pickpocket.OWN_POCKETS),
                             ((), {}, ()))
        finally:
            ravlog.restore_layout()
        self.assertEqual(pickpocket.OWN_POCKETS, ("Trustee",))
        self.assertTrue(pickpocket.LIFTABLE_NAMES)


@unittest.skipIf(Uc is None, "unicorn not installed")
class HelperTests(unittest.TestCase):
    TSR, SS = 0x1000, 0x4000

    @classmethod
    def setUpClass(cls):
        cls.image, cls.sym = built()

    def test_header_and_sites(self):
        hdr = self.sym["hdr"]
        for name, at in (("pick_on", ravlog.PP_ON), ("pick_seq", ravlog.PP_SEQ), ("pick_reply", ravlog.PP_REPLY),
                         ("pick_who", ravlog.PP_WHO), ("pick_thief", ravlog.PP_THIEF), ("pick_taken", ravlog.PP_TAKEN),
                         ("pick_off", ravlog.PP_TEXT_OFF), ("pick_shown", ravlog.PP_SHOWN),
                         ("pick_armed", ravlog.PP_ARMED), ("pick_late", ravlog.PP_LATE)):
            self.assertEqual(self.sym[name] - hdr, at, name)
        self.assertEqual(struct.unpack_from("<H", self.image, hdr + ravlog.PP_TEXT_OFF)[0], self.sym["pick_text"])
        table = self.sym["site_table"]
        for number, routine in ((180, "pp_show"), (181, "pp_click"), (182, "pp_lit"), (183, "pp_arm"),
                                (184, "pp_text"), (185, "pp_info"), (186, "pp_hand")):
            self.assertEqual(struct.unpack_from("<H", self.image, table + 2 * number)[0], self.sym[routine], number)
        for number in (130, 179, 187, 189):
            self.assertEqual(struct.unpack_from("<H", self.image, table + 2 * number)[0], self.sym["site_none"])
        self.assertLess(self.sym["pick_text"], self.sym["resident_end"])
        self.assertEqual(dicelog.PICK_BUTTON, 2)

    def emulate(self, routine, classes=(17, 0, 0), element=0, fight=0, pick_on=2, stack=()):
        mu = Uc(UC_ARCH_X86, UC_MODE_16)
        mu.mem_map(0, 0x100000)
        image = bytearray(self.image)
        struct.pack_into("<H", image, self.sym["hdr"] + ravlog.PP_ON, pick_on)
        mu.mem_write(self.TSR * 16, bytes(image))
        mu.mem_write(self.TSR * 16 + 0xFFF0, b"\xf4" * 16)
        sheet = 0x6000 * 16
        mu.mem_write(sheet + 0x1B, bytes(classes))
        mu.mem_write(DS * 16 + 0x1429, struct.pack("<HH", 0, 0x6000))
        mu.mem_write(DS * 16 + 0x9C1C, struct.pack("<H", element))
        mu.mem_write(DS * 16 + 0x9D77, struct.pack("<H", 0xBE5))
        mu.mem_write((LOAD + 0x3C10) * 16 + 0x19, struct.pack("<H", fight))
        mu.mem_write((LOAD + 0x3E71) * 16 + 0xB44, struct.pack("<H", 2))  # (the character on show)
        mu.mem_write(DS * 16 + 0x445A, struct.pack("<H", 0x1234))
        mu.mem_write(DS * 16 + 0x4265 + 4, struct.pack("<H", 1))
        sp = 0x7F0 - 2 * len(stack)
        mu.mem_write(self.SS * 16 + sp, b"".join(struct.pack("<H", w) for w in stack))
        sp -= 6
        mu.mem_write(self.SS * 16 + sp, struct.pack("<HHH", 0xFFF0, self.TSR, 0x2))  # (the INT's IP, CS, flags)
        for name, value in dict(cs=self.TSR, ds=DS, ss=self.SS, esp=sp, eflags=0x2, ebp=0x7F8).items():
            mu.reg_write(getattr(r, "UC_X86_REG_" + name.upper()), value)
        try:
            mu.emu_start(self.TSR * 16 + self.sym[routine], 0, count=5000)
        except Exception:
            pass
        word = lambda at: struct.unpack("<H", mu.mem_read(at, 2))[0]
        ip = mu.reg_read(r.UC_X86_REG_IP) - 1
        return mu, word, ip

    def test_show_a_thief(self):
        """A thief outside a fight: the purse (element 9, icon 3048), the compare's ZF clear (a button)."""
        mu, word, ip = self.emulate("pp_show")
        self.assertEqual(ip, 0xFFF0)
        self.assertEqual((word(DS * 16 + 0x9C1C), word(DS * 16 + 0x9D77)), (9, 3048))
        self.assertFalse(mu.reg_read(r.UC_X86_REG_EFLAGS) & 0x40)
        self.assertEqual(mu.mem_read(self.TSR * 16 + self.sym["pp_shown"], 1)[0], 1)

    def test_show_none(self):
        """Not a thief, a fight, the Loader not asking, or a priest: the game's own button (or none)."""
        for kwargs in (dict(classes=(11, 0, 0)), dict(fight=1), dict(pick_on=0)):
            mu, word, ip = self.emulate("pp_show", **kwargs)
            self.assertEqual(word(DS * 16 + 0x9C1C), 0, kwargs)
            self.assertTrue(mu.reg_read(r.UC_X86_REG_EFLAGS) & 0x40, kwargs)  # (ZF: no button)
            self.assertEqual(mu.mem_read(self.TSR * 16 + self.sym["pp_shown"], 1)[0], 0, kwargs)
        mu, word, ip = self.emulate("pp_show", element=2)  # (a cleric/thief: Turn Undead)
        self.assertEqual(word(DS * 16 + 0x9C1C), 2)
        self.assertFalse(mu.reg_read(r.UC_X86_REG_EFLAGS) & 0x40)

    def test_arm_the_game(self):
        """Turn Undead's own: "push dword 132FFFFh" under the INT's frame."""
        mu, word, ip = self.emulate("pp_arm", stack=(0, 0))
        self.assertEqual(ip, 0xFFF0)
        sp = mu.reg_read(r.UC_X86_REG_SP)
        self.assertEqual((word(self.SS * 16 + sp), word(self.SS * 16 + sp + 2)), (0xFFFF, 0x0132))
