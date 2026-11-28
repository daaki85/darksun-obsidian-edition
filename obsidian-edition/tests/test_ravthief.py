"""DSCLOG2's THIEVES AS IN AD&D in Wake of the Ravager (run in an emulated CPU): Shattered Lands'
RULE_THIEF_TABLE (its RULE_BACKSTAB) ported. THIEF_SKILL (site 52) makes a thief skill AD&D's average for
the thief level plus the race's and Dark Sun's DEX adjustment, as game.thief_skill_parts has it (the game's
own sum without the rule); BELT_SITE keeps the chance to THIEF_MOST; the inventory's C_THIEF shows the
same numbers; STAB_TIMES (site 53) multiplies a backstab's weapon dice only, on the round's first attack,
an Assassin's (the kits' rule, SL's kits.backstab_times) one more time, and STAB_FIRST takes back a party
member's later backstab in the same round.
With DSUN_WOTR naming the player's Wake of the Ravager folder, the patched sites also run in the game's
own code. Needs nasm and unicorn, else skipped."""

import os
import shutil
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dsloader import game, kitpages, kits, ravager, ravlog  # noqa: E402

try:
    from unicorn import Uc, UC_ARCH_X86, UC_MODE_16, UC_HOOK_CODE, UC_HOOK_INTR
    from unicorn import x86_const as r
except ImportError:
    Uc = None

ASM = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dos", "dsclog2.asm")
WOTR = os.environ.get("DSUN_WOTR")
TSR, GAME_DS, SS, TABLES = 0x1000, 0x5000, 0x4000, 0x6000
BP = 0x600
ON = game.RULE_THIEF_TABLE
BASE = bytes((30, 25, 20, 15, 10, 10, 85, 0))  # (the game's bases, any: the handler takes them out)


def adnd(skill: int, level: int, race: int, dex: int) -> int:
    """What THIEF_SKILL makes of it: game.py's AD&D table and Dark Sun's DEX (game.thief_skill_parts)."""
    return game.AD_D_THIEF[skill][min(level, len(game.AD_D_THIEF[0])) - 1] + race + game.dex_adjustment(dex, skill)


@unittest.skipIf(Uc is None or not shutil.which("nasm"), "needs unicorn and nasm")
class ThiefTableTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from test_dsclog_drawing import build
        exe, cls.sym = build(ASM)
        cls.image = exe[struct.unpack_from("<H", exe, 8)[0] * 16:]

    def machine(self, rules):
        mu = Uc(UC_ARCH_X86, UC_MODE_16)
        mu.mem_map(0, 0x100000)
        mu.mem_write(TSR * 16, self.image)
        mu.mem_write(TSR * 16 + 0xFFF0, bytes((0xF4,)))
        mu.mem_write(TSR * 16 + self.sym["rules"], struct.pack("<H", rules))
        return mu

    def call(self, mu, site, frame=b"", **regs):
        """Run SITE as the game's INT would reach it (an IRET frame to a HLT, FRAME's words after it);
        BP 600h in SS."""
        mu.mem_write(SS * 16 + 0x7F0, struct.pack("<HHH", 0xFFF0, TSR, 0x2) + frame)
        values = dict(cs=TSR, ds=GAME_DS, ss=SS, esp=0x7F0, ebp=BP, eflags=0x2)
        values.update(regs)
        for name, value in values.items():
            mu.reg_write(getattr(r, "UC_X86_REG_" + name.upper()), value)
        mu.emu_start(TSR * 16 + self.sym[site], TSR * 16 + 0xFFF0, count=100000)

    def word(self, mu, at):
        return struct.unpack("<h", mu.mem_read(at, 2))[0]

    def skill(self, rules, skill, level, race, dex):
        """THIEF_SKILL for SKILL at thief LEVEL (SI), the race's adjustment RACE, DEX ([BP-2]): (SI, CF)."""
        mu = self.machine(rules)
        mu.mem_write(TABLES * 16, BASE)
        mu.mem_write(SS * 16 + BP + 8, struct.pack("<I", skill))
        mu.mem_write(SS * 16 + BP - 2, struct.pack("<h", dex))
        self.call(mu, "thief_skill", es=TABLES, esi=level, edx=(BASE[skill] + race) & 0xFFFF, ebx=0x1234,
                  ecx=0x5678)
        self.assertEqual((mu.reg_read(r.UC_X86_REG_BX), mu.reg_read(r.UC_X86_REG_CX)), (0x1234, 0x5678))
        si = struct.unpack("<h", struct.pack("<H", mu.reg_read(r.UC_X86_REG_SI)))[0]
        return si, mu.reg_read(r.UC_X86_REG_EFLAGS) & 1

    def test_site_table(self):
        """Sites 52 and 53 are THIEF_SKILL and STAB_TIMES, as ravager's patches name them."""
        table = self.sym["site_table"]
        for number, name in ((52, "thief_skill"), (53, "stab_times")):
            self.assertEqual(struct.unpack_from("<H", self.image, table + 2 * number)[0], self.sym[name])
        sites = {p.name: p.replacement[2] for p in ravager.PATCHES if p.replacement[:2] == bytes((0xCD, 0xF5))}
        self.assertEqual((sites["thief_table"], sites["backstab_dice"]), (52, 53))

    def test_adnd_table(self):
        """With the rule, every skill at levels 1-20 (past 17 as 17), DEX 3-25 (9 and 22 the ends), a race's
        adjustment either way: AD&D's average + race + Dark Sun's DEX, CF set (past the game's DEX formula)."""
        for skill in range(8):
            for level in range(1, 21):
                for dex in (3, 9, 10, 12, 15, 16, 17, 18, 19, 20, 21, 22, 25):
                    for race in (-10, 0, 5):
                        with self.subTest(skill=skill, level=level, dex=dex, race=race):
                            self.assertEqual(self.skill(ON, skill, level, race, dex),
                                             (adnd(skill, level, race, dex), 1))

    def test_game_sum(self):
        """Without the rule, or without a thief level, the game's: base + race + 4 a level, CF clear (on to
        its DEX formula)."""
        for rules, level in ((0, 1), (0, 9), (0, 20), (ON, 0)):
            for skill in range(8):
                with self.subTest(rules=rules, level=level, skill=skill):
                    self.assertEqual(self.skill(rules, skill, level, -5, 17), (BASE[skill] - 5 + 4 * level, 0))

    def test_most(self):
        """BELT_SITE (the routine's end): with the rule, no more than THIEF_MOST (95); else as it is. The
        replaced "pop di" done (DI the word under the INT's frame)."""
        for rules, chance, want in ((ON, 120, 95), (ON, 95, 95), (ON, 60, 60), (ON, -20, -20), (0, 120, 120)):
            with self.subTest(rules=rules, chance=chance):
                mu = self.machine(rules)
                self.call(mu, "belt_site", frame=struct.pack("<H", 0x4321), esi=chance & 0xFFFF, edi=999)
                ax = struct.unpack("<h", struct.pack("<H", mu.reg_read(r.UC_X86_REG_AX)))[0]
                self.assertEqual((ax, mu.reg_read(r.UC_X86_REG_DI)), (want, 0x4321))

    def test_inventory(self):
        """C_THIEF (the inventory's thief skills, C_VALS: the six shown, climb walls in hear noise's
        place): with the rule AD&D's average + race + DEX, no more than 95, no less than 0; else the game's
        base + 4 a level + race + its DEX formula."""
        thief_seg = GAME_DS + 0x449B - 0x47E0
        races = bytes((0xFB, 0, 5, 0, 0, 0, 0, 0))  # (race 2's row: -5 pick pockets, +5 traps)
        limits = (bytes((9,) * 8), bytes((15,) * 8), bytes((17,) * 8))
        for rules in (ON, 0):
            for level, dex in ((1, 9), (4, 17), (12, 22), (15, 19)):
                mu = self.machine(rules)
                mu.mem_write(thief_seg * 16, BASE + bytes(16) + races)  # (race R's row at 8 + 8R)
                for at, row in zip((0xA0, 0xA8, 0xB0), limits):
                    mu.mem_write(thief_seg * 16 + at, row)
                sheet, creature = 0x7000, 0x7100
                mu.mem_write(sheet * 16 + 0x12, bytes((2,)))
                mu.mem_write(creature * 16 + 0x1A, bytes((dex,)))
                values = dict(cs=TSR, ds=GAME_DS, ss=SS, esp=0x7F0, ebp=BP, eflags=0x2, es=sheet, esi=0,
                              fs=creature, edi=0, eax=level)
                for name, value in values.items():
                    mu.reg_write(getattr(r, "UC_X86_REG_" + name.upper()), value)
                mu.emu_start(TSR * 16 + self.sym["c_thief"], TSR * 16 + self.sym["c_cells"], count=100000)
                got = list(mu.mem_read(TSR * 16 + self.sym["c_vals"], 8))
                race = [struct.unpack("b", races[s:s + 1])[0] for s in range(8)]
                if rules:
                    want = [max(0, min(95, adnd(s, level, race[s], dex))) for s in range(8)]
                else:
                    want = [max(0, BASE[s] + 4 * level + race[s] - max(0, 9 - dex) * 5 + max(0, dex - 15) * 5
                                - max(0, dex - 17) * 3) for s in range(8)]
                want[5] = want[6]
                with self.subTest(rules=rules, level=level, dex=dex):
                    self.assertEqual(got[:7], want[:7])

    def stab(self, rules, times, damage, dice, made):
        """STAB_TIMES: multiplier AX, [BP-4] the damage, ENL_DICE the dice, [BP-16h] the attacks made."""
        mu = self.machine(rules)
        mu.mem_write(TSR * 16 + self.sym["enl_dice"], struct.pack("<h", dice))
        mu.mem_write(SS * 16 + BP - 4, struct.pack("<h", damage))
        mu.mem_write(SS * 16 + BP - 0x16, struct.pack("<h", made))
        mu.mem_write(SS * 16 + BP - 0x14, struct.pack("<h", 7))  # (the roll's bonus: not the count)
        self.call(mu, "stab_times", eax=times, esi=0x1111, edi=0x2222)
        self.assertEqual((mu.reg_read(r.UC_X86_REG_SI), mu.reg_read(r.UC_X86_REG_DI)), (0x1111, 0x2222))
        return self.word(mu, SS * 16 + BP - 4)

    def test_backstab(self):
        """With the rule, the dice x the multiplier, the rest (STR, the weapon's plus) once, on the round's
        first attack only; a miss none. Without it the game's: the whole damage multiplied."""
        for rules, times, damage, dice, made, want in (
                (ON, 2, 9, 6, 0, 15), (ON, 3, 9, 6, 0, 21), (ON, 5, 4, 4, 0, 20), (ON, 4, 12, 3, 0, 21),
                (ON, 2, 9, 6, 1, 9), (ON, 2, 0, 6, 0, 0),
                (0, 2, 9, 6, 0, 18), (0, 3, 9, 6, 1, 27), (0, 2, 0, 6, 0, 0)):
            with self.subTest(rules=rules, times=times, damage=damage, dice=dice, made=made):
                self.assertEqual(self.stab(rules, times, damage, dice, made), want)

    def test_assassin(self):
        """With the kits (RULES_HI's RULE_HI_KITS), an Assassin's backstab one more time (kits.backstab_times:
        x3 to x6), with the rule on its dice, without it on the whole; a Swashbuckler, a foe (attacker [BP+0Eh]
        past 3) or the kits off: the game's multiplier. The round's second attack: no backstab either way."""
        ravlog.apply_layout()
        self.addCleanup(ravlog.restore_layout)
        from test_ravkits import wotr_sheet
        assassin, swash = wotr_sheet((17,), (9,), 1, 2), wotr_sheet((17,), (9,), 1, 1)
        self.assertEqual((kitpages.kit_ids(assassin), kitpages.kit_ids(swash)), ([kits.ASSASSIN], [kits.SWASHBUCKLER]))
        creatures, sheets = 0x7000, 0x7200
        for rules in (ON, 0):
            for hi in (game.RULE_KITS >> 16, 0):
                for sheet, kid in ((assassin, kits.ASSASSIN), (swash, kits.SWASHBUCKLER)):
                    for attacker in (1, 5):
                        for times, made in ((2, 0), (4, 0), (5, 0), (3, 1)):
                            mu = self.machine(rules)
                            mu.mem_write(TSR * 16 + self.sym["rules_hi"], struct.pack("<H", hi))
                            mu.mem_write(GAME_DS * 16 + 0x19C9, struct.pack("<HH", 0, creatures))
                            mu.mem_write(GAME_DS * 16 + 0x19C5, struct.pack("<HH", 0, sheets))
                            mu.mem_write(creatures * 16 + attacker * 0x31 + 4, struct.pack("<H", 2))
                            mu.mem_write(sheets * 16 + 2 * ravager.SHEET_SIZE, sheet)
                            mu.mem_write(SS * 16 + BP + 0x0E, struct.pack("<H", attacker))
                            mu.mem_write(TSR * 16 + self.sym["enl_dice"], struct.pack("<h", 6))
                            mu.mem_write(SS * 16 + BP - 4, struct.pack("<h", 9))
                            mu.mem_write(SS * 16 + BP - 0x16, struct.pack("<h", made))
                            self.call(mu, "stab_times", eax=times, esi=0x1111, edi=0x2222)
                            n = kits.backstab_times(kid, times) if hi and attacker <= 3 else times
                            if made:
                                want = 9 if rules else 9 * n
                            else:
                                want = 6 * n + 3 if rules else 9 * n
                            with self.subTest(rules=rules, hi=hi, kit=kid, attacker=attacker, times=times, made=made):
                                self.assertEqual(self.word(mu, SS * 16 + BP - 4), want)
                                self.assertEqual((mu.reg_read(r.UC_X86_REG_SI), mu.reg_read(r.UC_X86_REG_DI)),
                                                 (0x1111, 0x2222))

    def test_first_attack_only(self):
        """STAB_FIRST (from MISSILE_REAR): with the rule, a party member's later attack at the same game clock
        (DS:9C0Ch's far pointer) has its backstab ([BP-21h]) taken back and its 2 off THAC0 ([BP-1Eh]) given
        back; a new clock, another member, a foe or the rule off: as it is."""
        clock = 0x7800
        for rules in (ON, 0):
            mu = self.machine(rules)
            mu.mem_write(GAME_DS * 16 + 0x9C0C, struct.pack("<HH", 0x10, clock))
            for member, time, want in ((0, 100, (1, 8)), (0, 100, (0, 10) if rules else (1, 8)), (1, 100, (1, 8)),
                                       (0, 101, (1, 8)), (5, 101, (1, 8)), (5, 101, (1, 8))):
                mu.mem_write(clock * 16 + 0x10, struct.pack("<I", time))
                mu.mem_write(SS * 16 + BP - 0x21, bytes((1,)))
                mu.mem_write(SS * 16 + BP - 0x1E, struct.pack("<h", 8))
                self.call(mu, "stab_first", esi=member)
                with self.subTest(rules=rules, member=member, time=time):
                    self.assertEqual((mu.mem_read(SS * 16 + BP - 0x21, 1)[0], self.word(mu, SS * 16 + BP - 0x1E)),
                                     want)
                    self.assertEqual(mu.reg_read(r.UC_X86_REG_SI), member)

    def test_enlarged_dice_backstabbed(self):
        """ENL_ROLL keeps the dice, ENL_SITE (Enlarge's, RULE_HI_ENLARGE) makes them the enlarged ones, and a
        backstab multiplies those: 2d4 = 6 + 3 STR, Enlarge level 1 (x110%, 7), x2 = 7 x2 + 3 = 17."""
        mu = self.machine(ON)
        mu.mem_write(TSR * 16 + self.sym["rules_hi"], struct.pack("<H", 512))
        mu.mem_write(SS * 16 + BP - 0x14, struct.pack("<h", 0))  # (the roll's bonus)
        mu.mem_write(SS * 16 + BP + 0x16, struct.pack("<h", 1))  # (melee)
        self.call(mu, "enl_roll", eax=6)
        self.call(mu, "enl_site", eax=1, esi=9)
        self.assertEqual(mu.reg_read(r.UC_X86_REG_SI), 10)
        self.assertEqual(self.word(mu, TSR * 16 + self.sym["enl_dice"]), 7)
        mu.mem_write(SS * 16 + BP - 4, struct.pack("<h", 10))
        mu.mem_write(SS * 16 + BP - 0x16, struct.pack("<h", 0))
        self.call(mu, "stab_times", eax=2)
        self.assertEqual(self.word(mu, SS * 16 + BP - 4), 17)


def real_mode_interrupt(mu, intno, _):
    """A real-mode INT: FLAGS, CS, IP pushed, CS:IP from the vector table."""
    sp, ss = mu.reg_read(r.UC_X86_REG_SP), mu.reg_read(r.UC_X86_REG_SS)
    flags = mu.reg_read(r.UC_X86_REG_EFLAGS) & 0xFFFF
    mu.mem_write(ss * 16 + sp - 6, struct.pack("<HHH", mu.reg_read(r.UC_X86_REG_IP), mu.reg_read(r.UC_X86_REG_CS),
                                               flags))
    mu.reg_write(r.UC_X86_REG_SP, sp - 6)
    mu.reg_write(r.UC_X86_REG_EFLAGS, flags & ~0x300)
    off, seg = struct.unpack("<HH", mu.mem_read(intno * 4, 4))
    mu.reg_write(r.UC_X86_REG_CS, seg)
    mu.reg_write(r.UC_X86_REG_IP, off)


@unittest.skipUnless(WOTR and Uc is not None and shutil.which("nasm"), "DSUN_WOTR, unicorn and nasm")
class InGameCodeTests(unittest.TestCase):
    """The patched sites in the game's own code (DSUN.EXE's bytes, the Loader's patches on), INT F5h
    dispatched through DSCLOG2's SITE."""
    CODE = 0x3000  # Place the game code beyond the helper and its interrupt dispatch tables.

    @classmethod
    def setUpClass(cls):
        from test_dsclog_drawing import build
        exe, cls.sym = build(ASM)
        cls.image = exe[struct.unpack_from("<H", exe, 8)[0] * 16:]
        with open(os.path.join(WOTR, "DSUN.EXE"), "rb") as f:
            game_exe = bytearray(f.read())
        for p in ravager.PATCHES:
            if p.name in ("thief_table", "backstab_dice") or p.name.startswith("sheet_stride_"):
                assert game_exe[p.offset:p.offset + len(p.original)] == p.original
                game_exe[p.offset:p.offset + len(p.replacement)] = p.replacement
        cls.exe = bytes(game_exe)

    def run_game(self, rules, start, stops, setup, **regs):
        """The game's code from file offset START (as CODE:0) to the first of STOPS (file offsets),
        SETUP(mu) first: (the machine, the stop reached)."""
        mu = Uc(UC_ARCH_X86, UC_MODE_16)
        mu.mem_map(0, 0x100000)
        mu.mem_write(TSR * 16, self.image)
        mu.mem_write(TSR * 16 + self.sym["rules"], struct.pack("<H", rules))
        mu.hook_add(UC_HOOK_INTR, real_mode_interrupt)
        mu.mem_write(0xF5 * 4, struct.pack("<HH", self.sym["site_int"], TSR))
        self.assertLessEqual(TSR * 16 + len(self.image), self.CODE * 16)
        mu.mem_write(self.CODE * 16, self.exe[start:start + 0x200])
        setup(mu)
        values = dict(cs=self.CODE, ds=GAME_DS, ss=SS, esp=0x5C0, ebp=BP, eflags=0x202)
        values.update(regs)
        for name, value in values.items():
            mu.reg_write(getattr(r, "UC_X86_REG_" + name.upper()), value)
        ends = {self.CODE * 16 + s - start: s for s in stops}
        mu.hook_add(UC_HOOK_CODE, lambda uc, address, size, data: uc.emu_stop() if address in ends else None)
        mu.emu_start(self.CODE * 16, 0, count=10000)
        self.assertEqual(mu.reg_read(r.UC_X86_REG_SP), 0x5C0)
        return mu, ends[mu.reg_read(r.UC_X86_REG_CS) * 16 + mu.reg_read(r.UC_X86_REG_IP)]

    def test_thief_routine(self):
        """The thief skill routine from 8C6C6h (a thief level found) with the sequel's own tables (file
        49BB0h: the game's segment 4A0h, its race rows 8 bytes from +8): with the rule, on at 8C795h (its
        armour and effects) with AD&D's chance; without it, on at 8C71Fh (its DEX formula) with base + race
        + 4 a level."""
        tables = self.exe[0x49BB0:0x49BB0 + 0xE0]
        combatant, creature, sheet, creatures, sheets = 5, 3, 2, 0x7000, 0x7200
        for rules in (ON, 0):
            for skill, level, race, dex in ((0, 1, 1, 17), (1, 7, 2, 19), (3, 13, 3, 12), (4, 15, 1, 22),
                                            (2, 4, 4, 9), (6, 10, 2, 16)):
                def setup(mu):
                    mu.mem_write(0x4A0 * 16, tables)
                    mu.mem_write(0x388 * 16 + 0xC34 + combatant * 3, struct.pack("<H", creature))
                    mu.mem_write(GAME_DS * 16 + 0x19C9, struct.pack("<HH", 0, creatures))
                    mu.mem_write(GAME_DS * 16 + 0x19C5, struct.pack("<HH", 0, sheets))
                    mu.mem_write(creatures * 16 + creature * 0x31 + 4, struct.pack("<H", sheet))
                    mu.mem_write(sheets * 16 + sheet * ravager.SHEET_SIZE + 0x12, bytes((race,)))
                    mu.mem_write(SS * 16 + BP + 8, struct.pack("<I", skill))
                    mu.mem_write(SS * 16 + BP - 2, struct.pack("<h", dex))
                mu, stop = self.run_game(rules, 0x8C6C6, (0x8C795, 0x8C71F), setup, esi=level, edi=combatant)
                adjust = struct.unpack_from("b", tables, 8 + race * 8 + skill)[0]
                want = (adnd(skill, level, adjust, dex), 0x8C795) if rules else \
                    (tables[skill] + adjust + 4 * level, 0x8C71F)
                with self.subTest(rules=rules, skill=skill, level=level, race=race, dex=dex):
                    self.assertEqual((mu.reg_read(r.UC_X86_REG_SI), stop), want)

    def test_backstab_site(self):
        """The attack's backstab multiply (5D11Bh, the multiplier in AX) goes on at 5D125h with [BP-4] the
        dice x AX + the rest with the rule, the whole x AX without."""
        for rules, want in ((ON, 6 * 3 + 2), (0, 8 * 3)):
            def setup(mu):
                mu.mem_write(TSR * 16 + self.sym["enl_dice"], struct.pack("<h", 6))
                mu.mem_write(SS * 16 + BP - 4, struct.pack("<h", 8))
                mu.mem_write(SS * 16 + BP - 0x16, struct.pack("<h", 0))
            mu, stop = self.run_game(rules, 0x5D11B, (0x5D125,), setup, eax=3)
            with self.subTest(rules=rules):
                self.assertEqual((struct.unpack("<h", mu.mem_read(SS * 16 + BP - 4, 2))[0], stop), (want, 0x5D125))
