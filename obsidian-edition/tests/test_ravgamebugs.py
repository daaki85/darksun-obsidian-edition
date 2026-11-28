"""Shattered Lands' fixes of the game's own bugs carried to Wake of the Ravager (GAME-BUGS.md's sequel table):
DSCLOG2's GL_ARMOUR (site 242: the gladiator's armour optimisation only with armour on) run in an emulated CPU
on a party member's items in fake memory, its PSP_SCORES (site 198's: the most PSP from the member's own CON,
INT and WIS), its AI_WALL (site 243: the computer's wall across the line of fire), its KREEN_CLAWS (site 244: a party
thri-kreen's claws and bite edged), and the Loader's data fixes (an archer's pointer, the roster's
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


@unittest.skipIf(Uc is None or not shutil.which("nasm"), "needs unicorn and nasm")
class PspScoresTests(unittest.TestCase):
    """KIT_MAX_PSP's PSP_SCORES (site 198, 95172h): the game's CON, INT and WIS bonuses taken off SI and the
    member's own put in, as DSCLOG's (test_dsclog's test_max_psp_scores) with the sequel's places: the
    creature's scores at +1Bh, the tables' segment in the word 7Dh back from the INT's way back (the
    routine's "mov dx,seg" at 950F7h), CON's, INT's and WIS's tables at EFh, F7h, FFh + the score, the
    creation screen's record at DS:142Dh."""
    CODE, BACK, TABLES, MADE = 0x2000, 0x0200, 0x5000, 0x5800

    @classmethod
    def setUpClass(cls):
        from test_dsclog_drawing import build
        exe, cls.sym = build(ASM)
        cls.image = exe[struct.unpack_from("<H", exe, 8)[0] * 16:]

    def run_scores(self, con, intel, wis, made_wis, si=200):
        mu = Uc(UC_ARCH_X86, UC_MODE_16)
        mu.mem_map(0, 0x100000)
        mu.mem_write(TSR * 16, self.image)
        mu.mem_write(self.CODE * 16 + self.BACK, b"\xF4")
        mu.mem_write(self.CODE * 16 + self.BACK - (0x95175 - 0x950F8), struct.pack("<H", self.TABLES))
        tables = bytes(range(8)) + bytes(range(7)) + b"\0" + bytes(range(20, 35, 2)) + bytes(range(8)) + bytes((8, 8, 10))
        mu.mem_write(self.TABLES * 16 + 0xEF + 15, tables)
        mu.mem_write(self.TABLES * 16 + 0xFF + 183 - 256, struct.pack("b", -100))  # (a stray WIS of 183: signed)
        bp = 0x600
        mu.mem_write(SS * 16 + bp - 4, struct.pack("<HH", 5 * 0x31, CREATURES))
        mu.mem_write(SS * 16 + bp - 8, struct.pack("<HH", 0x40, SHEETS))
        mu.mem_write(CREATURES * 16 + 5 * 0x31 + 0x1B, bytes((con, intel, wis)))
        mu.mem_write(GDS * 16 + 0x142D, struct.pack("<HH", 0, self.MADE))
        mu.mem_write(self.MADE * 16 + 0x1D, bytes((made_wis,)))
        sp = 0x7F0
        mu.mem_write(SS * 16 + sp - 6, struct.pack("<HHH", self.BACK, self.CODE, 0x2))
        for reg, value in dict(cs=TSR, ds=GDS, es=0, ss=SS, esp=sp - 6, ebp=bp, ebx=0, esi=si, eax=0x1111,
                               ecx=0x3333, edx=0x4444, eflags=0x2).items():
            mu.reg_write(getattr(r, "UC_X86_REG_" + reg.upper()), value)
        mu.emu_start(TSR * 16 + self.sym["kit_max_psp"], self.CODE * 16 + self.BACK, count=100000)
        self.assertEqual([mu.reg_read(x) & 0xFFFF for x in (r.UC_X86_REG_AX, r.UC_X86_REG_BX, r.UC_X86_REG_CX,
                                                             r.UC_X86_REG_DX, r.UC_X86_REG_ES, r.UC_X86_REG_SP)],
                         [0x1111, 0x40, 0x3333, 0x4444, SHEETS, sp])
        return (mu.reg_read(r.UC_X86_REG_SI) & 0xFFFF) - si

    def test_the_members_own_scores(self):
        whole = bytes(14) + bytes(range(8)) + bytes(range(7)) + b"\0" + bytes(range(20, 35, 2)) + bytes(range(8)) \
            + bytes((8, 8, 10)) + bytes(16)
        game_term = lambda off, score: struct.unpack("b", whole[off + score - 1:off + score])[0] if score >= 15 else 0
        own = lambda score: max(min(score, 25) - 15, 0) if score >= 15 else 0
        for con, intel, wis, made_wis in ((10, 10, 10, 18), (16, 16, 16, 16), (16, 16, 16, 22), (22, 22, 20, 14),
                                          (23, 23, 23, 15), (25, 25, 25, 25), (14, 15, 14, 25), (16, 16, 16, 183)):
            with self.subTest(con=con, intel=intel, wis=wis, made_wis=made_wis):
                made = -100 if made_wis == 183 else game_term(16, made_wis)
                game_sum = game_term(0, con) + game_term(8, intel) + (made if wis >= 15 else 0)
                own_sum = own(con) + own(intel) + (2 * min(wis, 25) - 10 if wis >= 15 else 0)
                self.assertEqual(self.run_scores(con, intel, wis, made_wis), own_sum - game_sum)


@unittest.skipIf(Uc is None or not shutil.which("nasm"), "needs unicorn and nasm")
class AiWallTests(unittest.TestCase):
    """AI_WALL (site 243, 5EE6Bh: the computer's cast pushing its two points, the cell [BP-2], [BP-4]): a wall
    (WALL_SPELLS) across the line from the caster (DS:67C5h + SI x 25h, in sixteenths) WALL_HALF either way
    (23 each way on the slant); anything else both points at the cell's middle, as the game had them. Point 1
    on top: x, y, then point 2 (DSCLOG's NS_WALL, test_dsclog's test_ai_wall)."""
    CODE = 0x3000  # (past the helper at TSR: its image and tail run past 2000:0000)

    @classmethod
    def setUpClass(cls):
        from test_dsclog_drawing import build
        exe, cls.sym = build(ASM)
        cls.image = exe[struct.unpack_from("<H", exe, 8)[0] * 16:]

    def cast(self, spell, caster_x, caster_y, cell=(10, 20)):
        mu = Uc(UC_ARCH_X86, UC_MODE_16)
        mu.mem_map(0, 0x100000)
        mu.mem_write(TSR * 16, self.image)
        start, bp = self.CODE * 16 + 0x100, 0x600
        mu.mem_write(start, ravager._site(243, 0x28))
        mu.mem_write(0xF5 * 4, struct.pack("<HH", self.sym["site_int"], TSR))
        mu.mem_write(GDS * 16 + 0x67C5 + 5 * 0x25, struct.pack("<HH", caster_x, caster_y))
        mu.mem_write(SS * 16 + bp - 4, struct.pack("<HH", cell[1], cell[0]))
        for name, value in dict(cs=TSR, ds=GDS, ss=SS, esp=0x800, ebp=bp, eflags=0x202, esi=5, edi=spell,
                                eax=0x1111, ebx=0x2222, ecx=0x3333, edx=0x4444).items():
            mu.reg_write(getattr(r, "UC_X86_REG_" + name.upper()), value)
        # (unicorn runs no INT: the INT's frame pushed by hand, the way back past the site's byte)
        sp = 0x800 - 6
        mu.mem_write(SS * 16 + sp, struct.pack("<HHH", 0x102, self.CODE, 0x202))
        mu.reg_write(r.UC_X86_REG_ESP, sp)
        mu.emu_start(TSR * 16 + self.sym["site_int"], start + 0x28, count=100000)
        self.assertEqual([mu.reg_read(x) & 0xFFFF for x in (r.UC_X86_REG_SP, r.UC_X86_REG_SI, r.UC_X86_REG_DI,
                                                             r.UC_X86_REG_BP, r.UC_X86_REG_AX, r.UC_X86_REG_BX,
                                                             r.UC_X86_REG_CX, r.UC_X86_REG_DX, r.UC_X86_REG_DS)],
                         [0x7F8, 5, spell, bp, 0x1111, 0x2222, 0x3333, 0x4444, GDS])
        return struct.unpack("<4h", bytes(mu.mem_read(SS * 16 + 0x7F8, 8)))

    def test_walls_across_the_line(self):
        mid = (10 * 16 + 8, 20 * 16 + 8)
        self.assertEqual(self.cast(27, 0, 0), mid + mid)
        self.assertEqual(self.cast(54, mid[0] - 100, mid[1] + 10), (mid[0], mid[1] + 32, mid[0], mid[1] - 32))
        self.assertEqual(self.cast(208, mid[0] + 5, mid[1] - 90), (mid[0] + 32, mid[1], mid[0] - 32, mid[1]))
        self.assertEqual(self.cast(11, mid[0] - 50, mid[1] - 50), (mid[0] - 23, mid[1] + 23, mid[0] + 23, mid[1] - 23))
        self.assertEqual(self.cast(222, mid[0] - 50, mid[1] + 50), (mid[0] + 23, mid[1] + 23, mid[0] - 23, mid[1] - 23))

    def test_the_wall_spells_are_the_records_walls(self):
        """WALL_SPELLS is every record whose target (+0Ch) is 2, a wall (RESOURCE.GFF's: ravlog.spell_table)."""
        if not WOTR:
            self.skipTest("needs the sequel's files (DSUN_WOTR)")
        from dsloader import ravlog
        table, names = ravlog.spell_table(open(os.path.join(WOTR, "RESOURCE.GFF"), "rb").read())
        at, words = self.sym["wall_spells"], []
        while struct.unpack_from("<h", self.image, at)[0] != -1:
            words.append(struct.unpack_from("<H", self.image, at)[0])
            at += 2
        self.assertEqual(words, [s for s in range(len(names)) if table[s * 32 + 0x0C] == 2])


@unittest.skipIf(Uc is None or not shutil.which("nasm"), "needs unicorn and nasm")
class KreenClawsTests(unittest.TestCase):
    """KREEN_CLAWS (site 244, 5C86Dh): a party member's natural attack ([BP-2] -1, SI below 4) whose sheet
    ([BP-12h], 48h bytes) has race 8, a thri-kreen, slashing (10h) in place of crushing (8) in the damage
    kinds ([BP-14h]); a weapon's, a foe's or another race's kept. Then "cmp word [bp-0Ch],0", its flags."""

    @classmethod
    def setUpClass(cls):
        from test_dsclog_drawing import build
        exe, cls.sym = build(ASM)
        cls.image = exe[struct.unpack_from("<H", exe, 8)[0] * 16:]

    def hit(self, race, si=1, item=-1, kinds=0x08, magic=0):
        mu = Uc(UC_ARCH_X86, UC_MODE_16)
        mu.mem_map(0, 0x100000)
        mu.mem_write(TSR * 16, self.image)
        mu.mem_write(TSR * 16 + HLT, b"\xF4")
        mu.mem_write(GDS * 16 + 0x19C5, struct.pack("<HH", 0, SHEETS))
        mu.mem_write(SHEETS * 16 + 3 * 0x48 + 0x12, bytes((race,)))
        bp = 0x600
        mu.mem_write(SS * 16 + bp - 0x14, struct.pack("<HHHHHHHHHH", kinds, 3, 0, 0, magic & 0xFFFF, 0, 0, 0, 0, item & 0xFFFF))
        sp = 0x7F0
        mu.mem_write(SS * 16 + sp - 6, struct.pack("<HHH", HLT, TSR, 0x2))
        for reg, value in dict(cs=TSR, ds=GDS, es=0x1234, ss=SS, esp=sp - 6, ebp=bp, esi=si, eax=0x1111,
                               ebx=0x2222, eflags=0x2).items():
            mu.reg_write(getattr(r, "UC_X86_REG_" + reg.upper()), value)
        mu.emu_start(TSR * 16 + self.sym["kreen_claws"], TSR * 16 + HLT, count=100000)
        self.assertEqual([mu.reg_read(x) & 0xFFFF for x in (r.UC_X86_REG_SP, r.UC_X86_REG_ES, r.UC_X86_REG_AX,
                                                             r.UC_X86_REG_BX)], [sp, 0x1234, 0x1111, 0x2222])
        flags = mu.reg_read(r.UC_X86_REG_EFLAGS)
        self.assertEqual(bool(flags & 0x40), magic == 0)
        return struct.unpack("<H", bytes(mu.mem_read(SS * 16 + bp - 0x14, 2)))[0]

    def test_a_party_kreen_cuts(self):
        self.assertEqual(self.hit(8), 0x10)
        self.assertEqual(self.hit(8, kinds=0x1008, magic=1), 0x1010)

    def test_others_kept(self):
        self.assertEqual(self.hit(1), 0x08)           # (a human's fists)
        self.assertEqual(self.hit(8, si=5), 0x08)     # (a foe)
        self.assertEqual(self.hit(8, item=12), 0x08)  # (a weapon)
        self.assertEqual(self.hit(8, kinds=0x20), 0x20)


@unittest.skipIf(Uc is None or not shutil.which("nasm"), "needs unicorn and nasm")
class BerserkTests(unittest.TestCase):
    """BERSERK (sites 245, 246): the add check's "no case" (822A1h, back to 0F1Eh) keeps a Berserk's (7) side in
    the far word [BP+0Ch] points at (the record's +9 to come: the thing SI's creature's +15h, or an older
    Berserk's kept side); the end's "no case" (827D6h, back to 12E9h) sends Berserk to Controlled's case (120Dh)."""
    CODE = 0x3000  # (past the helper; the effect routines' segment: HLT throughout, the way back read from IP)
    EFFECTS = GDS - (0x47E0 - 0x3E71)  # (DSCLOG2's EFFECTS_GAP)

    @classmethod
    def setUpClass(cls):
        from test_dsclog_drawing import build
        exe, cls.sym = build(ASM)
        cls.image = exe[struct.unpack_from("<H", exe, 8)[0] * 16:]

    def add(self, effect, side=0, records=()):
        bp = 0x600
        mu = Uc(UC_ARCH_X86, UC_MODE_16)
        mu.mem_map(0, 0x100000)
        mu.mem_write(TSR * 16, self.image)
        mu.mem_write(self.CODE * 16, b"\xF4" * 0x2000)
        mu.mem_write(GDS * 16 + 0x19C9, struct.pack("<HH", 0, CREATURES))
        mu.mem_write(FIGHTERS * 16 + 0xC33 + 6 * 3, struct.pack("<BH", 2, 5))  # (thing 6: creature 5)
        mu.mem_write(CREATURES * 16 + 5 * 0x31 + 0x15, bytes((side,)))
        mu.mem_write(SS * 16 + bp + 0x0A, struct.pack("<HHH", effect, 0x700, SS))  # (+9's word at SS:700h)
        mu.mem_write(SS * 16 + 0x700, struct.pack("<H", 0xEEEE))
        mu.mem_write(GDS * 16 + 0x2100, struct.pack("<H", len(records)))
        for k, (owner, eff, extra) in enumerate(records):
            rec = bytearray(10)
            struct.pack_into("<H", rec, 0, owner)
            rec[6], rec[9] = eff, extra
            mu.mem_write(self.EFFECTS * 16 + 0x24D + k * 10, bytes(rec))
        sp = 0x7F0
        mu.mem_write(SS * 16 + sp - 6, struct.pack("<HHH", 0x0B34, self.CODE, 0x2))
        for reg, value in dict(cs=TSR, ds=GDS, es=0x1234, ss=SS, esp=sp - 6, ebp=bp, esi=6, eax=0x1111,
                               ebx=0x2222, eflags=0x2).items():
            mu.reg_write(getattr(r, "UC_X86_REG_" + reg.upper()), value)
        mu.emu_start(TSR * 16 + self.sym["berserk_add"], self.CODE * 16 + 0x1FFF, count=100000)
        self.assertEqual((mu.reg_read(r.UC_X86_REG_EIP) & 0xFFFF) - 1, 0x0F1E)  # (on to the add's tail)
        self.assertEqual(mu.reg_read(r.UC_X86_REG_SP) & 0xFFFF, sp)
        return struct.unpack("<H", bytes(mu.mem_read(SS * 16 + 0x700, 2)))[0]

    def test_the_side_kept(self):
        self.assertEqual(self.add(7, side=0), 0)
        self.assertEqual(self.add(7, side=9), 9)

    def test_an_older_berserks_side(self):
        self.assertEqual(self.add(7, side=2, records=((3, 7, 5), (6, 21, 1), (6, 7, 0))), 0)

    def test_other_effects_untouched(self):
        self.assertEqual(self.add(9, side=2), 0xEEEE)

    def end(self, effect):
        bp = 0x600
        mu = Uc(UC_ARCH_X86, UC_MODE_16)
        mu.mem_map(0, 0x100000)
        mu.mem_write(TSR * 16, self.image)
        mu.mem_write(self.CODE * 16, b"\xF4" * 0x2000)
        mu.mem_write(SS * 16 + bp + 8, struct.pack("<H", effect))
        sp = 0x7F0
        mu.mem_write(SS * 16 + sp - 6, struct.pack("<HHH", 0x1069, self.CODE, 0x2))
        for reg, value in dict(cs=TSR, ds=GDS, es=0x1234, ss=SS, esp=sp - 6, ebp=bp, esi=6, edx=3, eax=0x1111,
                               ebx=0x2222, eflags=0x2).items():
            mu.reg_write(getattr(r, "UC_X86_REG_" + reg.upper()), value)
        mu.emu_start(TSR * 16 + self.sym["berserk_end"], self.CODE * 16 + 0x1FFF, count=100000)
        self.assertEqual([mu.reg_read(x) & 0xFFFF for x in (r.UC_X86_REG_SP, r.UC_X86_REG_BX, r.UC_X86_REG_BP,
                                                             r.UC_X86_REG_DX)], [sp, 0x2222, bp, 3])
        return (mu.reg_read(r.UC_X86_REG_EIP) & 0xFFFF) - 1

    def test_berserk_given_back(self):
        self.assertEqual(self.end(7), 0x120D)

    def test_others_on(self):
        for effect in (102, 1, 35):
            self.assertEqual(self.end(effect), 0x12E9)


@unittest.skipUnless(WOTR, "needs the sequel's files (DSUN_WOTR)")
class FileTests(unittest.TestCase):
    def test_the_patches_find_the_sequels_bytes(self):
        with open(os.path.join(WOTR, "DSUN.EXE"), "rb") as f:
            exe = f.read()
        for name in ("shots_left", "roster_delete", "gladiator_armour", "lock_site", "ai_wall", "kreen_claws",
                     "berserk_add", "berserk_end"):
            p = next(p for p in ravager.PATCHES if p.name == name)
            self.assertEqual(exe[p.offset:p.offset + len(p.original)], p.original, name)
        # (the roster's "mov ax,2F8h" where the game's were: the loader fixes their segment up)
        p = next(p for p in ravager.PATCHES if p.name == "roster_delete")
        self.assertEqual([p.replacement[i:i + 3] for i in (7, 30)], [bytes.fromhex("b8f802")] * 2)

    def test_the_most_psp_routine_is_as_psp_scores_takes_it(self):
        """PSP_SCORES' places in the sequel's routine: the tables' "mov dx,seg" (950F7h), the creature's CON,
        INT, WIS read at +1Bh-1Dh from their tables at EFh, F7h, FFh + the score, WIS from DS:142Dh's record."""
        with open(os.path.join(WOTR, "DSUN.EXE"), "rb") as f:
            exe = f.read()
        self.assertEqual(exe[0x950F7], 0xBA)
        for at, code in ((0x950D2, "268a471b"), (0x950DF, "268a87ef00"), (0x950F1, "268a471c"),
                         (0x950FE, "268a87f700"), (0x95110, "c41e2d14268a471d"), (0x95121, "268a87ff00")):
            self.assertEqual(exe[at:at + len(code) // 2].hex(), code, hex(at))

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
