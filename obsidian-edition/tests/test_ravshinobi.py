"""The Shinobi's wizard spells in Wake of the Ravager: DSCLOG2's THE SHINOBI'S SPELLS (sites 209 and 210, and
the Shinobi's parts of EL_SPHERE's sites 90-92, RANGER_LEVEL, PICK_ANY, PICK_LIST, PICK_PAGE, PICK_TOP,
SCROLL_LEARN and CR_PICKS' SH_FILL), run in an emulated CPU, against Shattered Lands' rules (kits.shinobi_cast,
kits.shinobi_pick_level, kits.rav_pick_top on kits.RAV_SHINOBI_SPELLS) on the transferred party's sheets
(test_ravkits.wotr_sheet): a Shinobi thief at each level, the kit asleep after DUAL, other thieves and
classes as controls, the kits' rule on and off. And RAV_SHINOBI_SPELLS against Shattered Lands' list by the
spells' names (with both games' files: DSUN_SL, DSUN_WOTR). Needs nasm and unicorn, else skipped."""

import os
import shutil
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dsloader import game, kitpages, kits, ravager, ravlog, ravspells  # noqa: E402
from test_ravkits import ASM, wotr_sheet  # noqa: E402

try:
    from unicorn import Uc, UC_ARCH_X86, UC_MODE_16
    from unicorn import x86_const as r
except ImportError:
    Uc = None

TSR, GDS, SS = 0x1000, 0x6000, 0x7000
SHEETS, CREATURES = 0x4800, 0x4900  # (segments of the test's sheets and creatures)
FIGHTERS_SEG, KNOWN_SEG, USE_WHO_SEG = 0x3F49 - 0x47E0, 0x3D62 - 0x47E0, 0x3E71 - 0x47E0  # (DSCLOG2's, less DS's)
THIEF_TABLE = 0x449B - 0x47E0
GAME_CS, GAME_IP = 0x5555, 0x1233  # (a site's byte there, the way back after it)
HLT = 0xFFF0  # (a HLT in the helper's segment: the way back of a near call or an IRET the test makes)
RULES, RULES_HI = 170, 270
RULE_NEW_SPELLS, RULE_HI_KITS, RULE_HI_INT, RULE_THIEF_TABLE = 32, 1, 4, 256
SEED = 0x384A
THIEF, PRESERVER = 17, 11
SHINOBI_BYTE = 3  # (a thief's third kit: kitpages.kit_ids gives kits.SHINOBI)
NEW_KNOWN = {322: (0x3F, 0x40), 323: (0x3F, 0x08), 324: (0x3F, 0x80), 325: (0x3D, 0x80)}  # (NS_KNOWN_AT, _BIT)
OWN = dict(kits.RAV_SHINOBI_SPELLS)


@unittest.skipIf(Uc is None or not shutil.which("nasm"), "needs unicorn and nasm")
class ShinobiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from test_dsclog_drawing import build
        exe, cls.sym = build(ASM)
        cls.image = exe[struct.unpack_from("<H", exe, 8)[0] * 16:]
        assert cls.sym["tail_mid"] <= HLT  # (the HLT past the segment and the tail's tables: test_dsclog2_room)

    def setUp(self):
        mu = self.mu = Uc(UC_ARCH_X86, UC_MODE_16)
        mu.mem_map(0, 0x100000)
        mu.mem_write(TSR * 16, self.image)
        mu.mem_write(TSR * 16 + HLT, b"\xF4")
        mu.mem_write(0xF5 * 4, struct.pack("<HH", self.sym["site_int"], TSR))
        mu.mem_write(GDS * 16 + 0x19C5, struct.pack("<HHHH", 0, SHEETS, 0, CREATURES))
        for member in range(4):  # (combatant N, creature N, sheet N)
            mu.mem_write((GDS + FIGHTERS_SEG) * 16 + 0xC33 + 3 * member, struct.pack("<BH", 2, member))
            mu.mem_write(CREATURES * 16 + member * 0x31 + 4, struct.pack("<H", member))
        self.rules(0, RULE_HI_KITS)
        ravlog.apply_layout()
        self.addCleanup(ravlog.restore_layout)

    # ---- the set-up
    def rules(self, lo: int, hi: int) -> None:
        self.mu.mem_write(TSR * 16 + self.sym["hdr"] + RULES, struct.pack("<H", lo))
        self.mu.mem_write(TSR * 16 + self.sym["hdr"] + RULES_HI, struct.pack("<H", hi))

    def member(self, n: int, sheet: bytes, known=(), intelligence: int = 18) -> None:
        """Party member N with SHEET, knowing the spells KNOWN (wizard spells' bits, the new ones' sheet bits)."""
        sheet = bytearray(sheet)
        bits = bytearray(15)
        for spell in known:
            if spell in NEW_KNOWN:
                at, bit = NEW_KNOWN[spell]
                sheet[at] |= bit
            else:
                bits[spell // 8] |= 1 << (spell % 8)
        self.mu.mem_write(SHEETS * 16 + n * ravager.SHEET_SIZE, bytes(sheet))
        self.mu.mem_write((GDS + KNOWN_SEG) * 16 + 0x39C + 15 * n, bytes(bits))
        self.mu.mem_write(CREATURES * 16 + n * 0x31 + 0x1C, bytes((intelligence,)))

    def known(self, n: int):
        bits = self.mu.mem_read((GDS + KNOWN_SEG) * 16 + 0x39C + 15 * n, 15)
        sheet = self.mu.mem_read(SHEETS * 16 + n * ravager.SHEET_SIZE, ravager.SHEET_SIZE)
        out = {s for s in range(115) if bits[s // 8] >> (s % 8) & 1}
        return out | {s for s, (at, bit) in NEW_KNOWN.items() if sheet[at] & bit}

    def reader(self, n: int) -> None:
        self.mu.mem_write((GDS + USE_WHO_SEG) * 16 + 0xB44, struct.pack("<H", n))

    def header(self, at: int, size: int = 1) -> int:
        return int.from_bytes(self.mu.mem_read(TSR * 16 + self.sym["hdr"] + at, size), "little")

    def var(self, name: str, size: int = 1) -> int:
        return int.from_bytes(self.mu.mem_read(TSR * 16 + self.sym[name], size), "little")

    def regs(self, **values) -> None:
        base = dict(cs=TSR, ds=GDS, es=0x1234, ss=SS, esp=0x7F0, ebp=0x900, eflags=0x2)
        for reg, value in dict(base, **values).items():
            self.mu.reg_write(getattr(r, "UC_X86_REG_" + reg.upper()), value)

    def reg(self, name: str) -> int:
        return self.mu.reg_read(getattr(r, "UC_X86_REG_" + name.upper())) & 0xFFFF

    def call(self, label: str, **values) -> None:
        """Near call LABEL (back to a HLT)."""
        sp = values.pop("esp", 0x7F0)
        self.mu.mem_write(SS * 16 + sp - 2, struct.pack("<H", HLT))
        self.regs(esp=sp - 2, **values)
        self.mu.emu_start(TSR * 16 + self.sym[label], TSR * 16 + HLT, count=200000)

    def interrupt(self, label: str, flags: int = 0x2, **values) -> int:
        """LABEL as INT's handler (its frame back to a HLT); the flags IRET gives back."""
        sp = values.pop("esp", 0x7F0)
        self.mu.mem_write(SS * 16 + sp - 6, struct.pack("<HHH", HLT, TSR, flags))
        self.regs(esp=sp - 6, **values)
        self.mu.emu_start(TSR * 16 + self.sym[label], TSR * 16 + HLT, count=200000)
        self.assertEqual(self.reg("esp"), sp)
        return self.mu.reg_read(r.UC_X86_REG_EFLAGS)

    def site(self, number: int, words=(), **values) -> int:
        """Site NUMBER as the game reaches it (INT F5h, SITE's way in reading its byte), WORDS on the stack
        under the INT's frame; the way back past the byte checked. Returns the flags IRET gave back."""
        mu = self.mu
        mu.mem_write(GAME_CS * 16 + GAME_IP, bytes((0xCD, 0xF5, number, 0xF4)))
        sp = 0x7F0
        mu.mem_write(SS * 16 + sp - 6 - 2 * len(words), struct.pack("<HHH", GAME_IP + 2, GAME_CS, 0x2)
                     + b"".join(struct.pack("<H", w) for w in words))
        self.regs(esp=sp - 6 - 2 * len(words), **values)
        mu.emu_start(TSR * 16 + self.sym["site_int"], GAME_CS * 16 + GAME_IP + 3, count=200000)
        self.assertEqual(mu.reg_read(r.UC_X86_REG_IP), GAME_IP + 3)
        return mu.reg_read(r.UC_X86_REG_EFLAGS)

    @staticmethod
    def thieves():
        """(sheet, a Shinobi's thief level or 0): a Shinobi thief at levels 1-20, the other thief kits and a
        thief with none; a Shinobi turned fighter (its kit asleep, then awake again); a preserver and a
        fighter."""
        out = [(wotr_sheet((THIEF,), (level,), 1, SHINOBI_BYTE), level) for level in range(1, 21)]
        out += [(wotr_sheet((THIEF,), (9,), 1, byte), 0) for byte in (0, 1, 2)]
        out += [(wotr_sheet((9, THIEF), (3, 8), 1, SHINOBI_BYTE), 0), (wotr_sheet((9, THIEF), (9, 8), 1, SHINOBI_BYTE), 8)]
        out += [(wotr_sheet((PRESERVER,), (9,), 1, 1), 0), (wotr_sheet((9,), (9,), 1, 1), 0)]
        for sheet, level in out:
            assert (kits.SHINOBI in kitpages.kit_ids(sheet)) == bool(level), (sheet.hex(), level)
        return out

    # ---- casting
    def test_sphere_yes(self):
        """EL_SPHERE's three sites (SH_SPHERE_DI, SH_SPHERE_BP): the game's no made yes for a Shinobi's thief
        class and a wizard spell (a new one with its rule), the game's answer kept for every other class, spell
        and character, and with the kits' rule off."""
        made = 0
        for n, (sheet, level) in enumerate(self.thieves()):
            member = n % 4
            self.member(member, sheet)
            for rules_lo, rules_hi in ((RULE_NEW_SPELLS, RULE_HI_KITS), (0, RULE_HI_KITS), (RULE_NEW_SPELLS, 0)):
                self.rules(rules_lo, rules_hi)
                for cls in (THIEF, PRESERVER, 9):
                    for spell in (0, 8, 0x40, 0x72, 0x73, 0x90, 322, 325):
                        for site in (90, 91, 92):
                            for answer in (0, 1):
                                new = spell >= 320
                                want = answer or int(bool(level) and bool(rules_hi) and cls == THIEF
                                                     and (spell < 0x73 or (new and bool(rules_lo))))
                                self.mu.mem_write(SS * 16 + 0x900 + 6, struct.pack("<H", member))
                                self.site(site, (spell, cls), eax=0xAB00 | answer, edi=member, esi=0x5555)
                                with self.subTest(n=n, rules=(rules_lo, rules_hi), cls=cls, spell=spell, site=site):
                                    self.assertEqual(self.reg("eax"), 0xAB00 | want)
                                    self.assertEqual(self.reg("esp"), 0x7F0)  # (the call's two words gone)
                                made += want and not answer
        self.assertGreater(made, 0)

    def test_cast_level(self):
        """SHINOBI_CAST_LEVEL (site 209): the caster level routine's class level, for a Shinobi's thief class
        kits.shinobi_cast's (its thief level less 5, 0 at least, 11 at most); any other class's, a thief's of
        no kit and with the rule off, kept; the call's two words taken off."""
        for n, (sheet, level) in enumerate(self.thieves()):
            member = n % 4
            self.member(member, sheet)
            for rules_hi in (RULE_HI_KITS, 0):
                self.rules(0, rules_hi)
                for cls in (THIEF, PRESERVER):
                    game_level = sheet[0x1E + 1] if len(set(sheet[0x1B:0x1E])) > 2 and cls == THIEF else 9
                    for got in (game_level, 0, 3, 14):
                        self.mu.mem_write(SS * 16 + 0x900 + 6, struct.pack("<H", member))
                        self.site(209, (member, cls), eax=got, esi=cls, ebx=0x2222)
                        want = kits.shinobi_cast(got) if level and rules_hi and cls == THIEF else got
                        with self.subTest(n=n, rules=rules_hi, cls=cls, got=got):
                            self.assertEqual(self.reg("eax"), want)
                            self.assertEqual(self.reg("esp"), 0x7F0)
                            self.assertEqual((self.reg("esi"), self.reg("ebx")), (cls, 0x2222))

    def test_duration_level(self):
        """RANGER_LEVEL (the cast's level for duration and damage, ES:BX the sheet + the class's place): a
        Shinobi's thief class's kits.shinobi_cast, a ranger's as before, any other class's whole."""
        for n, (sheet, level) in enumerate(self.thieves()):
            member = n % 4
            self.member(member, sheet)
            for place in range(3):
                cls, lvl = sheet[0x1B + place], sheet[0x1E + place]
                if not cls:
                    continue
                self.interrupt("ranger_level", es=SHEETS, ebx=member * ravager.SHEET_SIZE + place, eax=0xFFFF)
                own = level and cls == THIEF and kitpages.kit_class_of(sheet, kits.SHINOBI) == THIEF
                with self.subTest(n=n, place=place):
                    self.assertEqual(self.reg("eax"), kits.shinobi_cast(lvl) if own else lvl)

    def test_spook(self):
        """Spook's save (NS_SPOOK_SAVE): 1 worse for each 2 levels of a Shinobi's casting level too
        (kits.spook_penalty), none for a thief of no kit nor with the kits' rule off."""
        for n, (sheet, level) in enumerate(self.thieves()):
            for rules_hi in (RULE_HI_KITS, 0):
                self.rules(RULE_NEW_SPELLS, rules_hi)
                self.member(0, sheet)
                self.mu.mem_write(SS * 16 + 0x900 + 8, struct.pack("<H", 0))
                self.mu.mem_write(SS * 16 + 0x900 + 0x14, struct.pack("<H", ravspells.SPOOK))
                self.call("ns_spook_save", edi=100)
                pres = max([sheet[0x1E + i] for i in range(3) if sheet[0x1B + i] in (11, 18)], default=0)
                want = kits.spook_penalty(pres, level if rules_hi else 0)
                with self.subTest(n=n, rules=rules_hi):
                    self.assertEqual(self.reg("edi"), 100 + want)

    # ---- learning: the level up, CHOOSE A SPELL, creation
    def test_level_up(self):
        """SHINOBI_LEVEL_UP (site 210): ZF as "cmp word [bp+8],0Bh" (set for a preserver's level up), set too
        for a Shinobi's thief class from thief level 6 (the rule on), clear at 1st-5th and for others."""
        for n, (sheet, level) in enumerate(self.thieves()):
            member = n % 4
            self.member(member, sheet)
            for rules_hi in (RULE_HI_KITS, 0):
                self.rules(0, rules_hi)
                for cls in (THIEF, PRESERVER, 9, 12):
                    self.mu.mem_write(SS * 16 + 0x900 + 8, struct.pack("<H", cls))
                    flags = self.site(210, esi=member)
                    want = cls == PRESERVER or (cls == THIEF and level >= 6 and bool(rules_hi)
                                                and not (set(sheet[0x1B:0x1E]) & {11, 18}))
                    with self.subTest(n=n, rules=rules_hi, cls=cls):
                        self.assertEqual(bool(flags & 0x40), want)

    def test_scholar_pick(self):
        """SHINOBI_LEVEL_UP's way in (SCHOLAR_LEVEL_UP): a party member's new preserver level ([BP+8] 0Bh,
        [BP-6] not 0) with the Scholar kit awake (kits.SCHOLAR, the rule on) calls CHOOSE A SPELL (688h:66h
        through its stub, here a RETF) once more, SCHOLAR_PICKS counted, every register kept; ZF as the
        compare's for all (the game's own pick next); nobody else's calls it."""
        from dsloader import kitpages
        stub = (GDS + self.sym.get("CR_STUB", -0x30)) * 16 + 0x66
        self.mu.mem_write(stub, bytes((0xCB,)))  # (CHOOSE A SPELL: back at once)
        picks = TSR * 16 + self.sym["scholar_picks"]
        seen = 0
        sheets = [(wotr_sheet((PRESERVER,), (9,), 1, byte), byte) for byte in (0, 1, 2, 3)]
        sheets += [(wotr_sheet((9, PRESERVER), (5, 5), 3, byte), byte) for byte in (0, 1)]
        for sheet, byte in sheets:
            for rules_hi in (RULE_HI_KITS, 0):
                self.rules(0, rules_hi)
                for member in (0, 3, 5):
                    if member < 4:
                        self.member(member, sheet)
                    for cls, new in ((PRESERVER, 1), (PRESERVER, 0), (THIEF, 1), (9, 1)):
                        self.mu.mem_write(SS * 16 + 0x900 + 8, struct.pack("<H", cls))
                        self.mu.mem_write(SS * 16 + 0x900 - 6, bytes((new,)))
                        before = struct.unpack("<H", self.mu.mem_read(picks, 2))[0]
                        flags = self.site(210, esi=member, ebx=0x1234, edi=0x5678, eax=0x9ABC)
                        after = struct.unpack("<H", self.mu.mem_read(picks, 2))[0]
                        want = bool(rules_hi) and member < 4 and cls == PRESERVER and new \
                            and kits.SCHOLAR in kitpages.kit_ids(sheet)
                        with self.subTest(byte=byte, rules=rules_hi, member=member, cls=cls, new=new):
                            self.assertEqual(after - before, int(want))
                            self.assertEqual(bool(flags & 0x40), cls == PRESERVER)
                            for reg, value in (("EBX", 0x1234), ("EDI", 0x5678), ("EAX", 0x9ABC), ("ESI", member)):
                                self.assertEqual(self.mu.reg_read(getattr(r, "UC_X86_REG_" + reg)) & 0xFFFF, value)
                        seen += want
        self.assertTrue(seen)

    def known_sets(self, level: int):
        mine = [s for s, _ in kits.RAV_SHINOBI_SPELLS]
        return [(), tuple(mine[:5]), tuple(mine[:9]), tuple(mine[:14]), tuple(mine[:18]), tuple(mine), (3, 8, 20)]

    def test_pick_any(self):
        """PICK_ANY for a Shinobi (no preserver level, AX 0): AX and [BP-2] kits.rav_pick_top up to
        kits.shinobi_pick_level, 0 (the window not opened) with nothing left; a preserver's AX kept."""
        for level in range(1, 21):
            sheet = wotr_sheet((THIEF,), (level,), 1, SHINOBI_BYTE)
            for known in self.known_sets(level):
                for new_rule in (RULE_NEW_SPELLS, 0):
                    self.rules(new_rule, RULE_HI_KITS)
                    self.member(1, sheet, known)
                    self.mu.mem_write(SS * 16 + 0x900 - 2, struct.pack("<H", 0x7777))
                    flags = self.interrupt("pick_any", eax=0, esi=1)
                    want = kits.rav_pick_top(lambda s: s in known, kits.shinobi_pick_level(level), bool(new_rule))
                    with self.subTest(level=level, known=known, new=new_rule):
                        self.assertEqual(self.reg("eax"), want)
                        self.assertEqual(struct.unpack("<H", self.mu.mem_read(SS * 16 + 0x900 - 2, 2))[0], want)
                        self.assertEqual(bool(flags & 0x40), want == 0)
        self.member(1, wotr_sheet((PRESERVER,), (9,), 1, 1))
        self.interrupt("pick_any", eax=9, esi=1)
        self.assertEqual(self.reg("eax") and struct.unpack("<H", self.mu.mem_read(SS * 16 + 0x900 - 2, 2))[0] > 0, True)

    def test_page(self):
        """PICK_LIST: a Shinobi reader's page its own spells alone, in the game's order, DI their count; a
        preserver's page kept. PICK_PAGE: a Shinobi's first page kits.rav_pick_top (its own level if none
        left). PICK_TOP: the level button no higher than kits.shinobi_pick_level."""
        page = [0, 2, 3, 6, 8, 9, 11, 17, 19, 12, 25, 35, 36, 44, 40, 50, 60]
        for level in (6, 9, 12, 13, 16):
            sheet = wotr_sheet((THIEF,), (level,), 1, SHINOBI_BYTE)
            most = kits.shinobi_pick_level(level)
            for known in self.known_sets(level):
                self.member(2, sheet, known)
                self.reader(2)
                self.rules(0, RULE_HI_KITS)
                self.mu.mem_write((GDS + USE_WHO_SEG) * 16 + 7, b"".join(struct.pack("<H", s) for s in page))
                self.interrupt("pick_list", eax=len(page), es=0x1234)
                got = [struct.unpack_from("<H", self.mu.mem_read((GDS + USE_WHO_SEG) * 16 + 7, 40), 2 * i)[0]
                       for i in range(self.reg("edi"))]
                with self.subTest(level=level, known=known):
                    self.assertEqual(got, [s for s in page if s in OWN])
                    self.interrupt("pick_page", eax=0x1105)
                    top = kits.rav_pick_top(lambda s: s in known, most, False)
                    self.assertEqual(self.reg("eax"), 0x1100 | (top or most))
                    for button in range(1, 6):
                        self.mu.mem_write(SS * 16 + 0x900 - 2, struct.pack("<H", 5))
                        flags = self.interrupt("pick_top", eax=button)
                        self.assertEqual(bool(flags & 1), button < most, button)  # (CF: below the highest)
                        self.assertEqual(bool(flags & 0x40), button == most, button)
        self.member(2, wotr_sheet((PRESERVER,), (9,), 1, 1))
        self.mu.mem_write((GDS + USE_WHO_SEG) * 16 + 7, b"".join(struct.pack("<H", s) for s in page))
        self.interrupt("pick_list", eax=len(page))
        self.assertEqual(self.reg("edi"), len(page))

    def test_fill(self):
        """SH_FILL (creation's EXIT): CX more of the Shinobi's spells it doesn't know, the first in its list's
        order of a level up to kits.shinobi_pick_level; a new one only with its rule."""
        for level in (6, 10, 13):
            for new_rule in (RULE_NEW_SPELLS, 0):
                for count in (1, 3, 30):
                    self.rules(new_rule, RULE_HI_KITS)
                    self.member(0, wotr_sheet((THIEF,), (level,), 1, SHINOBI_BYTE), (6, 17))
                    self.call("sh_fill", ecx=count, esi=0)
                    most = kits.shinobi_pick_level(level)
                    want = [s for s, lvl in kits.RAV_SHINOBI_SPELLS if lvl <= most and s not in (6, 17)
                            and (new_rule or s < 320)][:count]
                    with self.subTest(level=level, new=new_rule, count=count):
                        self.assertEqual(self.known(0), {6, 17} | set(want))

    # ---- scrolls
    def scroll(self, reader: int, spell: int):
        """SCROLL_LEARN for READER and wizard spell SPELL (the game's ES:BX its known bits' byte, [BP-4] the
        spell, AX 0: not known): (AX, the message due, LEARN_RESULT)."""
        self.reader(reader)
        self.mu.mem_write(SS * 16 + 0x900 - 4, struct.pack("<H", spell))
        flags = self.interrupt("scroll_learn", eax=0, es=GDS + KNOWN_SEG, ebx=reader * 15 + spell // 8)
        ax = self.reg("eax")
        self.assertEqual(bool(flags & 0x40), ax == 0)
        return ax, self.var("learn_msg"), self.header(279)

    def test_scroll(self):
        """A Shinobi's scroll (SCROLL_LEARN's SH_SCROLL): another spell refused (AX 1, LEARN_NOT_ITS: the scroll
        kept); its own read against its read languages (LEARN_READ_CHANCE: AD&D's for its thief level and race,
        SH_READ_LANG), unread LEARN_UNREAD, then INT's chance (LEARN_FAILED), AX 0 (the game teaches it, the
        message then taking it back). The d100s from the game's seed, the dice log told (+2076, +2077)."""
        self.rules(RULE_THIEF_TABLE, RULE_HI_KITS | RULE_HI_INT)
        table = bytearray(8 + 8 * 8)
        for race in range(8):
            table[8 + 8 * race + 7] = (race * 5) & 0xFF
        self.mu.mem_write((GDS + THIEF_TABLE) * 16, bytes(table))
        results = set()
        for level in (6, 10, 13):
            for race in (1, 3):
                sheet = wotr_sheet((THIEF,), (level,), race, SHINOBI_BYTE)
                self.member(3, sheet, intelligence=12)
                ax, msg, result = self.scroll(3, 8)  # (Magic Missile: not its own)
                self.assertEqual((ax, msg, result), (1, 4, 4))
                self.mu.mem_write(TSR * 16 + self.sym["learn_msg"], b"\0")
                read = min(95, game.AD_D_THIEF[7][level - 1] + race * 5)
                for seed in range(0, 4000, 97):
                    self.mu.mem_write(GDS * 16 + SEED, struct.pack("<I", seed))
                    ax, msg, result = self.scroll(3, 17)  # (Invisibility)
                    roll = self.header(2076)
                    with self.subTest(level=level, race=race, seed=seed):
                        self.assertEqual(ax, 0)
                        self.assertEqual(self.header(2077), read)
                        self.assertEqual(result == 3, roll > read)  # (LEARN_UNREAD)
                        self.assertEqual(msg, result if result else 0)
                        if result != 3:
                            self.assertEqual(self.header(277), 50)  # (INT 12's chance)
                            self.assertEqual(result == 1, self.header(278) > 50)
                    results.add(result)
                    self.mu.mem_write(TSR * 16 + self.sym["learn_msg"], b"\0")
        self.assertEqual(results, {0, 1, 3})

    def test_scroll_others(self):
        """A preserver's and a plain thief's scroll as before: no read roll, no refusal."""
        self.rules(0, RULE_HI_KITS | RULE_HI_INT)
        self.member(0, wotr_sheet((THIEF,), (9,), 1, 1))
        self.assertEqual(self.scroll(0, 8)[0], 0)
        self.assertEqual(self.header(2076, 2), 0)
        self.member(0, wotr_sheet((THIEF,), (9,), 1, SHINOBI_BYTE))
        self.rules(0, RULE_HI_INT)
        self.assertEqual(self.scroll(0, 8)[0], 0)  # (the kits' rule off: no Shinobi)

    def test_patches(self):
        """The two sites' patches and table entries; EL_SPHERE's three entries the Shinobi's way in."""
        by_name = {p.name: p for p in ravager.PATCHES}
        for name, number, original in (("shinobi_cast_level", 209, "83c404"), ("shinobi_level_up", 210, "837e080b")):
            p = by_name[name]
            self.assertEqual(p.original, bytes.fromhex(original))
            self.assertEqual(p.replacement[:3], bytes((0xCD, 0xF5, number)))
            self.assertEqual(len(p.replacement), len(p.original))
            self.assertEqual(struct.unpack_from("<H", self.image, self.sym["site_table"] + 2 * number)[0],
                             self.sym[{209: "sh_cast_level", 210: "scholar_level_up"}[number]])
        for number, label in ((90, "sh_sphere_di"), (91, "sh_sphere_bp"), (92, "sh_sphere_bp")):
            self.assertEqual(struct.unpack_from("<H", self.image, self.sym["site_table"] + 2 * number)[0], self.sym[label])


class ShinobiListTests(unittest.TestCase):
    def test_rav_list(self):
        """RAV_SHINOBI_SPELLS: SHINOBI_SPELLS' spells and levels, the new ones as ravspells numbers them, the
        sequel's others the same as Shattered Lands' but Protection from Normal Missiles, Improved
        Invisibility, Solid Fog and Confusion (the sequel's 35, 44, 50, 40); and, with both games' files, by
        their names (ravtransfer.spell_map)."""
        new = {game.FOG_SPELL: ravspells.FOG, game.REFLECT_SPELL: ravspells.REFLECT,
               game.SPOOK_SPELL: ravspells.SPOOK, game.FRIENDS_SPELL: ravspells.FRIENDS}
        moved = {36: 35, 46: 44, 51: 50, 41: 40}
        self.assertEqual(kits.RAV_SHINOBI_SPELLS,
                         tuple((new.get(s, moved.get(s, s)), lvl) for s, lvl in kits.SHINOBI_SPELLS))
        sl, wotr = os.environ.get("DSUN_SL"), os.environ.get("DSUN_WOTR")
        if not (sl and ravager.is_wotr_dir(wotr) and os.path.isfile(os.path.join(sl, "RESOURCE.GFF"))):
            self.skipTest("needs both games' files (DSUN_SL, DSUN_WOTR)")
        from dsloader import gff, ravtransfer
        sl_chunks = gff.read_gff(open(os.path.join(sl, "RESOURCE.GFF"), "rb").read())
        _, names = ravlog.spell_table(open(os.path.join(wotr, "RESOURCE.GFF"), "rb").read())
        for (sl_spell, _), (spell, _) in zip(kits.SHINOBI_SPELLS, kits.RAV_SHINOBI_SPELLS):
            if spell < 320:  # (by name: Hold Person is a priest spell too, 136, which spell_map would take)
                name = sl_chunks[("SPIN", sl_spell + 1)].split(b":", 1)[0].decode("latin1").strip().upper()
                self.assertEqual(names[spell].upper(), ravtransfer.SPELL_ALIASES.get(name, name), sl_spell)

if __name__ == "__main__":
    unittest.main()
