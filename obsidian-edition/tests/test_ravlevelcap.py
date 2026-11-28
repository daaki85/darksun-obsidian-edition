"""DSCLOG2's LEVEL CAP BY XP, A THIEF'S HIT DICE and SAVING THROWS AS IN AD&D in Wake of the Ravager (run in
an emulated CPU): Shattered Lands' RULE_LEVEL_10 ported with the owner's cap (ravager.RAV_XP_CAP, 5,625,000,
shared between a character's classes) in place of the game's 15th level, up to RAV_XP's 30th (the game's
table 20 entries, XP_NEED answering past them); the level up's hold on XP never past the table; View Character's next XP naming its class; a thief's d6 to 10th
(a psionicist's to 9th); and the Player's Handbook's saves (tables.rav_saves) where the game held them at
its table's last row. Needs nasm and unicorn, else skipped."""

import os
import shutil
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dsloader import game, ravager, tables  # noqa: E402

try:
    from unicorn import Uc, UC_ARCH_X86, UC_MODE_16
    from unicorn import x86_const as r
except ImportError:
    Uc = None

ASM = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dos", "dsclog2.asm")
TSR, GAME_DS, SS, SHEET_SEG, GROUPS = 0x1000, 0x5000, 0x4000, 0x7000, 0x6000
BP, SHEET = 0x600, 0x100
CF, ZF = 1, 0x40
ON = game.RULE_LEVEL_10
HUMAN, ELF = 1, 3
FIGHTER, PRESERVER, PSIONICIST, THIEF, CLERIC = 9, 11, 12, 17, 1


def expected_levels():
    """The owner's (2026-11-25): the highest level of each class alone, of two and of three."""
    return {"cleric": (30, 20, 16), "druid": (20, 14, 14), "fighter": (30, 19, 15), "gladiator": (26, 17, 14),
            "preserver": (25, 17, 15), "psionicist": (27, 19, 16), "ranger": (26, 17, 14), "thief": (30, 22, 18)}


@unittest.skipIf(Uc is None or not shutil.which("nasm"), "needs unicorn and nasm")
class LevelCapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from test_dsclog_drawing import build
        exe, cls.sym = build(ASM)
        cls.image = exe[struct.unpack_from("<H", exe, 8)[0] * 16:]

    def machine(self, rules=ON, rules_hi=0):
        mu = Uc(UC_ARCH_X86, UC_MODE_16)
        mu.mem_map(0, 0x100000)
        mu.mem_write(TSR * 16, self.image)
        mu.mem_write(TSR * 16 + 0xFFF0, bytes((0xF4,)))
        mu.mem_write(TSR * 16 + self.sym["rules"], struct.pack("<H", rules))
        mu.mem_write(TSR * 16 + self.sym["rules_hi"], struct.pack("<H", rules_hi))
        tail = TSR + self.sym["TAIL_PARAS"]  # (the tail, where SAVE_BASE reads its bands: TAIL_SEG as installed)
        mu.mem_write(TSR * 16 + self.sym["tail_seg"], struct.pack("<H", tail))
        return mu

    def call(self, mu, site, frame=b"", **regs):
        """Run SITE as SITE_INT would reach it (an IRET frame to a HLT, FRAME's words after it)."""
        mu.mem_write(SS * 16 + 0x7F0, struct.pack("<HHH", 0xFFF0, TSR, 0x2) + frame)
        values = dict(cs=TSR, ds=GAME_DS, ss=SS, esp=0x7F0, ebp=BP, eflags=0x2)
        values.update(regs)
        for name, value in values.items():
            mu.reg_write(getattr(r, "UC_X86_REG_" + name.upper()), value)
        mu.emu_start(TSR * 16 + self.sym[site], TSR * 16 + 0xFFF0, count=200000)
        return mu.reg_read(r.UC_X86_REG_EFLAGS)

    def sheet(self, mu, race, classes, levels):
        data = bytearray(0x48)
        data[0x12] = race
        data[0x1B:0x1E] = bytes(classes)
        data[0x1E:0x21] = bytes(levels)
        mu.mem_write(SHEET_SEG * 16 + SHEET, bytes(data))

    def level_up(self, race, classes, levels, slot, rules=ON):
        """LV_UP at the level up (DI the place, ES:BX the sheet + it): True if the game's "jb" goes on to
        the new level (CF), with every register kept."""
        mu = self.machine(rules)
        self.sheet(mu, race, classes, levels)
        flags = self.call(mu, "lv_up", es=SHEET_SEG, ebx=SHEET + slot, edi=slot, esi=2, edx=0x1234)
        self.assertEqual([mu.reg_read(x) for x in (r.UC_X86_REG_BX, r.UC_X86_REG_DI, r.UC_X86_REG_DX)],
                         [SHEET + slot, slot, 0x1234])
        return bool(flags & CF)

    def view(self, race, rows, levels, slot):
        """LV_VIEW on View Character's copy (rows, SI the place): True if the next level is shown (no "je")."""
        mu = self.machine()
        self.sheet(mu, race, rows, levels)
        flags = self.call(mu, "lv_view", es=SHEET_SEG, ebx=SHEET + slot, esi=slot)
        return not flags & ZF

    def test_site_table(self):
        """Sites 110-118 are this port's, as ravager's patches name them; 100-109 left to other branches."""
        table = self.sym["site_table"]
        names = {110: "lv_up", 111: "lv_view", 112: "lv_clamp", 113: "hd_roll", 114: "hd_con", 115: "hd_clamp",
                 116: "save_base", 117: "xp_suffix_site", 118: "lv_ordinal"}
        for number, name in names.items():
            self.assertEqual(struct.unpack_from("<H", self.image, table + 2 * number)[0], self.sym[name])
        sites = {p.name: p.replacement[2] for p in ravager.PATCHES if p.replacement[:2] == bytes((0xCD, 0xF5))}
        self.assertEqual([sites[n] for n in ("level_cap_up", "level_cap_view", "level_clamp", "thief_hd_roll",
                                             "thief_hd_con", "thief_hd_clamp", "save_table", "xp_suffix",
                                             "level_ordinal")],
                         list(range(110, 119)))
        self.assertTrue(game.RULE_LEVEL_10 & ravager.RULES_PORTED)

    def test_levels_most(self):
        """The owner's highest levels, from tables.RAV_XP and the cap (ravager.level_most)."""
        for row, most in expected_levels().items():
            self.assertEqual(tuple(ravager.level_most(row, n) for n in (1, 2, 3)), most, row)

    def test_level_up_as_the_model(self):
        """LV_UP answers as ravager.level_room: one class, two, three, at every level 1-30."""
        combos = [(FIGHTER, 0, 0), (THIEF, 0, 0), (FIGHTER, THIEF, 0), (5, PSIONICIST, 0),
                  (FIGHTER, PRESERVER, THIEF), (CLERIC, 13, PSIONICIST), (10, 5, 17)]
        for classes in combos:
            n = sum(1 for c in classes if c)
            for slot in range(n):
                for level in range(1, 31):
                    levels = [5] * 3
                    levels[slot] = level
                    levels = [lv if c else 0 for lv, c in zip(levels, classes)]
                    with self.subTest(classes=classes, slot=slot, level=level):
                        self.assertEqual(self.level_up(ELF, classes, levels, slot),
                                         ravager.level_room(classes, levels, False, slot))

    def test_single_past_twenty(self):
        """One class goes on to its highest (the owner's, 2026-11-25: no stop at 20th; 30th at most); three
        stop at the owner's levels."""
        for cls, row, most in ((FIGHTER, "fighter", 30), (THIEF, "thief", 30), (11, "preserver", 25),
                               (5, "druid", 20), (12, "psionicist", 27), (13, "ranger", 26)):
            for level in range(15, most):
                self.assertTrue(self.level_up(ELF, (cls, 0, 0), (level, 0, 0), 0), (row, level))
            self.assertFalse(self.level_up(ELF, (cls, 0, 0), (most, 0, 0), 0), row)
        # a fighter/preserver/thief: 15/15/18
        for slot, cls, most in ((0, FIGHTER, 15), (1, PRESERVER, 15), (2, THIEF, 18)):
            levels = [10, 10, 10]
            levels[slot] = most - 1
            self.assertTrue(self.level_up(ELF, (FIGHTER, PRESERVER, THIEF), levels, slot))
            levels[slot] = most
            self.assertFalse(self.level_up(ELF, (FIGHTER, PRESERVER, THIEF), levels, slot))

    def test_human(self):
        """A human who changed class: the cap less what its old class's level needed (a cleric 7's 55,000)."""
        share = ravager.RAV_XP_CAP - tables.RAV_XP["cleric"][6]
        self.assertEqual(ravager.xp_share((FIGHTER, CLERIC, 0), (1, 7, 0), True), share)
        for level in range(1, 31):
            want = level < 30 and tables.RAV_XP["fighter"][level] <= share
            self.assertEqual(self.level_up(HUMAN, (FIGHTER, CLERIC, 0), (level, 7, 0), 0), want, level)
        # an old class high enough leaves the new one less: a thief 20 (2,200,000) then a preserver
        share = ravager.RAV_XP_CAP - tables.RAV_XP["thief"][19]
        most = max(lv for lv in range(1, 31) if lv == 1 or tables.RAV_XP["preserver"][lv - 1] <= share)
        self.assertTrue(self.level_up(HUMAN, (PRESERVER, THIEF, 0), (most - 1, 20, 0), 0))
        self.assertFalse(self.level_up(HUMAN, (PRESERVER, THIEF, 0), (most, 20, 0), 0))

    def test_rule_off(self):
        """Without the rule, the game's own: below 15."""
        for level in (1, 14, 15, 16):
            self.assertEqual(self.level_up(ELF, (FIGHTER, 0, 0), (level, 0, 0), 0, rules=0), level < 15)

    def test_view(self):
        """LV_VIEW on the copy's rows: the same answers, none at 30th or at a triple's cap."""
        self.assertTrue(self.view(ELF, (3, 0, 0), (29, 0, 0), 0))
        self.assertFalse(self.view(ELF, (3, 0, 0), (30, 0, 0), 0))
        self.assertTrue(self.view(ELF, (3, 5, 8), (14, 10, 10), 0))
        self.assertFalse(self.view(ELF, (3, 5, 8), (15, 10, 10), 0))
        self.assertFalse(self.view(ELF, (3, 5, 8), (10, 10, 18), 2))
        self.assertTrue(self.view(HUMAN, (3, 1, 0), (12, 7, 0), 0))

    def test_clamp(self):
        """LV_CLAMP: level + 3, no more than 29 (RAV_XP's last entry), and then XP_NEED's next answer the
        most (no hold); without the rule the game's level + 3."""
        for level, want, top in ((5, 8, 0), (16, 19, 0), (26, 29, 0), (27, 29, 1), (30, 29, 1)):
            mu = self.machine()
            self.sheet(mu, ELF, (FIGHTER, 0, 0), (level, 0, 0))
            self.call(mu, "lv_clamp", eax=level, es=SHEET_SEG, ebx=SHEET, edi=0)
            self.assertEqual((mu.reg_read(r.UC_X86_REG_AX), mu.mem_read(TSR * 16 + self.sym["xp_top"], 1)[0]),
                             (want, top), level)
        mu = self.machine(0)
        self.call(mu, "lv_clamp", eax=17)
        self.assertEqual(mu.reg_read(r.UC_X86_REG_AX), 20)
        # XP_NEED after it: the most, once
        mu = self.machine(rules_hi=8)
        mu.mem_write(TSR * 16 + self.sym["xp_top"], b"\x01")
        self.call(mu, "xp_need", frame=struct.pack("<HHH", 0x3E8, 2, 19), eax=30000)
        self.assertEqual(mu.reg_read(r.UC_X86_REG_EAX), 0xFFFFFFFF)
        self.call(mu, "xp_need", frame=struct.pack("<HHH", 0x3E8, 2, 19), eax=30000)
        self.assertEqual(mu.reg_read(r.UC_X86_REG_EAX), 3000000)

    def test_xp_held_at_the_share(self):
        """XP_HOLD at LV_CLAMP (the owner's, 2026-11-25: XP stops growing at the cap): the sheet's XP no more
        than its share (ES:BX the sheet + DI), whatever the level; below it kept; without the rule kept."""
        cases = (((ELF, (FIGHTER, 0, 0), (30, 0, 0)), 9000000, ravager.RAV_XP_CAP),
                 ((ELF, (FIGHTER, PRESERVER, THIEF), (15, 15, 18)), 4000000, ravager.RAV_XP_CAP // 3),
                 ((ELF, (FIGHTER, THIEF, 0), (5, 5, 0)), 100000, 100000),
                 ((HUMAN, (FIGHTER, CLERIC, 0), (17, 20, 0)), 3100000,
                  ravager.RAV_XP_CAP - tables.RAV_XP["cleric"][19]))
        for (race, classes, levels), xp, want in cases:
            self.assertEqual(min(xp, ravager.xp_share(classes, levels, race == HUMAN)), want)
            for slot in range(sum(1 for c in classes if c)):
                for rules in (ON, 0):
                    mu = self.machine(rules)
                    self.sheet(mu, race, classes, levels)
                    mu.mem_write(SHEET_SEG * 16 + SHEET, struct.pack("<I", xp))
                    self.call(mu, "lv_clamp", es=SHEET_SEG, ebx=SHEET + slot, edi=slot, eax=levels[slot])
                    got = struct.unpack("<I", mu.mem_read(SHEET_SEG * 16 + SHEET, 4))[0]
                    self.assertEqual(got, want if rules else xp, (classes, slot, rules))
                    self.assertEqual((mu.reg_read(r.UC_X86_REG_BX), mu.reg_read(r.UC_X86_REG_DI)),
                                     (SHEET + slot, slot))

    def test_rav_xp_at(self):
        """RAV_XP_AT: tables.RAV_XP at every row and index 0-29 (XP_FIXES' among them)."""
        mu = self.machine()
        for row, name in enumerate(tables.ROWS):
            self.assertEqual(len(tables.RAV_XP[name]), tables.RAV_XP_LEVELS)
            for index in range(tables.RAV_XP_LEVELS):
                mu.reg_write(r.UC_X86_REG_EDX, row | index << 8)
                mu.mem_write(SS * 16 + 0x7F0, struct.pack("<H", 0xFFF0))
                mu.reg_write(r.UC_X86_REG_CS, TSR)
                mu.reg_write(r.UC_X86_REG_SS, SS)
                mu.reg_write(r.UC_X86_REG_ESP, 0x7F0)
                mu.emu_start(TSR * 16 + self.sym["rav_xp_at"], TSR * 16 + 0xFFF0, count=10000)
                self.assertEqual(mu.reg_read(r.UC_X86_REG_EAX), tables.RAV_XP[name][index], (name, index))

    def test_xp_need_past_the_table(self):
        """XP_NEED past the game's 20 entries (which run on into the next row): RAV_XP's to index 29, then
        the most; without the rule the game's word x 100; below 20 as before (AD&D's fixes off here)."""
        for rules in (ON, 0):
            mu = self.machine(rules)
            for row, name in enumerate(tables.ROWS):
                for index in range(18, 32):
                    self.call(mu, "xp_need", frame=struct.pack("<HHH", 0x3E8, row, index), eax=7)
                    got = mu.reg_read(r.UC_X86_REG_EAX)
                    if not rules or index < 20:
                        want = 700
                    else:
                        want = tables.RAV_XP[name][index] if index < 30 else 0xFFFFFFFF
                    self.assertEqual(got, want, (rules, name, index))

    def test_ordinal(self):
        """LV_ORDINAL: the level up's message's ending at DS:2B7Eh, English's ("21st", "112th"), AX its place."""
        want = {4: "th", 11: "th", 12: "th", 13: "th", 20: "th", 21: "st", 22: "nd", 23: "rd", 24: "th", 30: "th",
                101: "st", 111: "th"}
        for level, ending in want.items():
            mu = self.machine()
            self.call(mu, "lv_ordinal", eax=level, ebx=0x1111, ecx=0x2222, edx=0x3333)
            self.assertEqual(bytes(mu.mem_read(GAME_DS * 16 + 0x2B7E, 2)).decode(), ending, level)
            self.assertEqual([mu.reg_read(x) for x in (r.UC_X86_REG_AX, r.UC_X86_REG_BX, r.UC_X86_REG_CX,
                                                       r.UC_X86_REG_DX)], [0x2B7E, 0x1111, 0x2222, 0x3333])

    def test_thac0_most(self):
        """PRIEST_THAC0 with the rule (the owner's, 2026-11-26: Table 39's limits): what a group takes off 20
        no more than 12 (a priest's 8), 19 (a warrior's 1), 6 (a wizard's 14), 9 (a rogue's 11); below, and
        without the rule, as given. With RULE_HI_TABLES a priest's at 30th, 2 x 29 // 3 = 18, held at 12."""
        for group, most in enumerate((12, 19, 6, 9)):
            for taken in (0, most - 1, most, most + 1, 29):
                for rules in (ON, 0):
                    mu = self.machine(rules)
                    self.call(mu, "priest_thac0", eax=taken, ecx=group)
                    got = struct.unpack("<h", mu.mem_read(SS * 16 + BP - 2, 2))[0]
                    self.assertEqual(got, min(taken, most) if rules else taken, (group, taken, rules))
        mu = self.machine(ON, rules_hi=8)
        mu.mem_write(SS * 16 + BP - 0x0A, bytes((30,)))
        self.call(mu, "priest_thac0", eax=0, ecx=0)
        self.assertEqual(struct.unpack("<h", mu.mem_read(SS * 16 + BP - 2, 2))[0], 12)

    def test_spell_pick_most(self):
        """PICK_MOST (the owner's, 2026-11-26: no 10th-level wizard slots): a preserver's CHOOSE A SPELL at a
        level up stops at 9th with the rule: PICK_ANY's level, PICK_PAGE's first page, PICK_TOP's last; without
        it the game's 10th (level / 2 from 20th)."""
        for rules, most in ((ON, 9), (0, 10)):
            mu = self.machine(rules)
            self.call(mu, "pick_any", eax=21, esi=0)
            self.assertEqual(struct.unpack("<h", mu.mem_read(SS * 16 + BP - 2, 2))[0], 9 if rules else 21)
            mu = self.machine(rules)
            self.call(mu, "pick_page", eax=10)
            self.assertEqual(mu.mem_read(GAME_DS * 16 + 0x43EC, 1)[0], most)
            for nxt in (9, 10):
                mu = self.machine(rules)
                mu.mem_write(SS * 16 + BP - 2, struct.pack("<H", 10))
                flags = self.call(mu, "pick_top", eax=nxt)
                self.assertEqual(bool(flags & CF) or bool(flags & ZF), nxt <= most, (rules, nxt))
                self.assertEqual(mu.reg_read(r.UC_X86_REG_AX), nxt)

    def test_thief_hit_dice(self):
        """A thief's group (the rogues', 9 levels of dice) counts 10 for a thief, 9 for a psionicist, at the
        hit die (HD_ROLL, [BP+8] the class) and the most hit points (HD_CON's compare, HD_CLAMP)."""
        for rules, cls, want in ((ON, THIEF, 10), (ON, PSIONICIST, 9), (0, THIEF, 9)):
            mu = self.machine(rules)
            mu.mem_write(GROUPS * 16 + 12, bytes((6, 9, 2, 6)))
            mu.mem_write(SS * 16 + BP + 8, struct.pack("<H", cls))
            self.call(mu, "hd_roll", es=GROUPS, ebx=12)
            self.assertEqual(mu.reg_read(r.UC_X86_REG_AL), want, (rules, cls))
            # the sheet's classes (place CX) through [BP-4]
            self.sheet(mu, ELF, (FIGHTER, cls, 0), (8, 10, 0))
            mu.mem_write(SS * 16 + BP - 4, struct.pack("<HH", SHEET, SHEET_SEG))
            flags = self.call(mu, "hd_con", es=GROUPS, ebx=12, ecx=1, eax=10)
            self.assertEqual(bool(flags & ZF), want == 10, (rules, cls))  # (10 vs 10: "jle" taken, kept)
            self.call(mu, "hd_clamp", es=GROUPS, ebx=12, ecx=1, eax=0x77)
            self.assertEqual(mu.reg_read(r.UC_X86_REG_AL), want)

    def save(self, rules_hi, group, level, save, race_bonus=0, classes=()):
        """SAVE_BASE and the game's sum after it (AL - [BP-2], [BP-2] the game's improvement + the race's);
        CLASSES the sheet's (class, level) pairs (creature 0, DI)."""
        game_table = ((10, 45, 2), (14, 45, 6), (13, 45, 5), (16, 45, 8), (15, 45, 7),
                      (14, 69, 3), (16, 69, 5), (15, 69, 4), (17, 82, 4), (17, 69, 6),
                      (14, 30, 8), (11, 40, 3), (13, 40, 5), (15, 40, 7), (12, 40, 4),
                      (13, 25, 8), (14, 50, 4), (12, 25, 7), (16, 25, 11), (15, 50, 5))
        mu = self.machine(rules_hi=rules_hi)
        mu.mem_write(GROUPS * 16 + 0x6C, bytes(b for row in game_table for b in row))
        mu.mem_write(SS * 16 + BP - 0x0A + 2 * group, bytes((level,)))
        pairs = list(classes) + [(0, 0)] * (3 - len(classes))
        self.sheet(mu, ELF, [c for c, _ in pairs], [lv for _, lv in pairs])
        mu.mem_write(GAME_DS * 16 + 0x19C5, struct.pack("<HH", SHEET, SHEET_SEG))
        base, rate, last = game_table[group * 5 + save]
        improve = min((level - 1) * rate // 100, last) + race_bonus
        self.call(mu, "save_base", es=GROUPS, ebx=group * 15 + save * 3, ecx=group, esi=save, edi=0)
        self.assertEqual((mu.reg_read(r.UC_X86_REG_CX), mu.reg_read(r.UC_X86_REG_SI)), (group, save))
        return struct.unpack("b", bytes((mu.reg_read(r.UC_X86_REG_AL),)))[0] - improve

    def test_saves(self):
        """With AD&D's tables the Player's Handbook's, less a dwarf's CON bonus as the game takes it; without,
        the game's, a warrior at 11/11/11/13/11 from 10th."""
        for group in range(4):
            for level in range(1, 25):
                for save in range(5):
                    with self.subTest(group=group, level=level, save=save):
                        self.assertEqual(self.save(8, group, level, save), tables.rav_saves(group, level)[save])
        self.assertEqual(self.save(8, 1, 12, 0, race_bonus=5), tables.rav_saves(1, 12)[0] - 5)
        self.assertEqual([self.save(0, 1, 12, s) for s in range(5)], [11, 11, 11, 13, 11])

    def test_psionicist_saves(self):
        """A psionicist's saves Dark Sun's (Table 8) at its psionicist level, to 30th; a psionicist/thief the
        better of each save of its two classes; the rule off, the game's (a psionicist as a thief)."""
        for level in range(1, 31):
            with self.subTest(level=level):
                self.assertEqual([self.save(8, 3, level, s, classes=((PSIONICIST, level),)) for s in range(5)],
                                 list(tables.rav_saves(3, level, psionicist=True)))
        for psi, thief in ((9, 13), (13, 9), (25, 2)):
            got = [self.save(8, 3, max(psi, thief), s, classes=((PSIONICIST, psi), (THIEF, thief))) for s in range(5)]
            self.assertEqual(got, list(tables.class_saves([(PSIONICIST, psi), (THIEF, thief)])), (psi, thief))
        self.assertEqual([self.save(0, 3, 12, s, classes=((PSIONICIST, 12),)) for s in range(5)], [11, 10, 10, 14, 10])

    def test_xp_suffix(self):
        """XP_SUFFIX: for two classes whose next XP is the fighter's, " F)" (CS:xp_suffix pushed for the
        game's DS:1386h); a human, or the rule off, the game's ")"."""
        def run(race, rows, levels, least, rules=ON):
            mu = self.machine(rules)
            self.sheet(mu, race, rows, levels)
            mu.mem_write(SS * 16 + BP + 0x0A, struct.pack("<HH", SHEET, SHEET_SEG))
            mu.mem_write(SS * 16 + BP - 6, struct.pack("<I", least))
            self.call(mu, "xp_suffix_site", frame=struct.pack("<H", GAME_DS))
            sp = mu.reg_read(r.UC_X86_REG_SP)
            off, seg = struct.unpack("<HH", mu.mem_read(SS * 16 + sp, 4))
            if seg == TSR and off == self.sym["xp_suffix"]:
                text = bytes(mu.mem_read(TSR * 16 + off, 12))
                return text[:text.index(0)].decode()
            self.assertEqual(off, 0x1386)
            return ")"
        fighter_next = tables.RAV_XP["fighter"][10]
        self.assertEqual(run(ELF, (3, 8, 0), (10, 9, 0), fighter_next), " F)")
        self.assertEqual(run(ELF, (5, 6, 0), (16, 9, 0), tables.RAV_XP["preserver"][16]), " Pr)")
        self.assertEqual(run(HUMAN, (3, 8, 0), (10, 9, 0), fighter_next), ")")
        self.assertEqual(run(ELF, (3, 8, 0), (10, 9, 0), fighter_next, rules=0), ")")


if __name__ == "__main__":
    unittest.main()
