"""Group 4 (2026-11-09): the monsters as the manual describes them (gamepatch.SPELLS_MANUAL), dual-classing
as the manual has it (game.RULE_DUAL_CLASS: DSCLOG's DUAL_LEVEL, DUAL_PRIMES) and resting
(game.RULE_REST and the rest's order fixed): DSCLOG's sites run in Unicorn at the game's bytes, and the
Loader's side."""
import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import game, gamepatch, tracker  # noqa: E402

import test_dsclog as td  # noqa: E402

try:
    from unicorn import x86_const as r
except ImportError:  # pragma: no cover
    r = None

GAME_DS, SS, CALLER, TSR, BP, IF = td.GAME_DS, td.SS, td.CALLER, td.TSR, td.BP, td.IF
CREATURES, SHEETS = 0x9000, 0xA000


def patch(name):
    return next(p for p in gamepatch.PATCHES if p.name == name)


@unittest.skipIf(td.Uc is None, "unicorn not installed")
class SiteTests(unittest.TestCase):
    THINGS_SEG, CREATURES, ITEMS, TYPES = td.RingTests.THINGS_SEG, CREATURES, td.RingTests.ITEMS, td.RingTests.TYPES

    def setUp(self):
        td.RingTests.setUp(self)
        image = td.load_image()
        self.image = image
        at = td.install_at(image, 0x98)
        self.mu.mem_write(0x98 * 4, struct.pack("<HH", struct.unpack_from("<H", image, at + 4)[0], TSR))
        self.mu.mem_write(GAME_DS * 16 + 0x1665, struct.pack("<HH", 0, CREATURES))
        self.mu.mem_write(GAME_DS * 16 + 0x1661, struct.pack("<HH", 0, SHEETS))
        self.hdr = TSR * 16 + image.find(td.HDR_SIG)

    def rules_hi(self, value):
        self.mu.mem_write(self.hdr + 270, struct.pack("<H", value))

    def jumps(self, name, jump="7c", **regs):
        """PATCH NAME's bytes run, then the game's jump (JUMP, "jl" or "jnl") over a HLT: whether it
        was taken. The registers back as they were."""
        p = patch(name)
        mu = self.mu
        self.at += 0x40
        start = CALLER * 16 + self.at
        mu.mem_write(start, p.replacement + bytes.fromhex(jump + "01f4f4"))
        regs = dict(cs=CALLER, ds=GAME_DS, ss=SS, esp=0x800, ebp=BP, eflags=IF | 2, **regs)
        for reg, value in regs.items():
            mu.reg_write(getattr(r, "UC_X86_REG_" + reg.upper()), value)
        mu.emu_start(start, 0, count=20000)
        for reg in ("sp", "bx", "si", "di", "es"):
            if reg in regs or reg == "sp":
                self.assertEqual(mu.reg_read(getattr(r, "UC_X86_REG_" + reg.upper())), regs.get(reg, 0x800), reg)
        stopped = mu.reg_read(r.UC_X86_REG_IP) - self.at - len(p.replacement)
        self.assertIn(stopped, (3, 4))
        return stopped == 4

    # ---- dual-classing ----------------------------------------------------------------------------

    def test_dual_patches(self):
        """The five compares at DSUN.EXE's bytes, each a site of DSCLOG's (in no switch: the rule is
        DSCLOG's, RULE_HI_DUAL)."""
        for name, offset, original, site in (
                ("dual_level_menu", 0x70CE4, "26807f2402", gamepatch.DUAL_LEVEL_SITE),
                ("dual_level_view", 0x70F03, "26807f2402", gamepatch.DUAL_LEVEL_SITE),
                ("dual_level_window", 0x86F58, "26807f2402", gamepatch.DUAL_LEVEL_SITE),
                ("dual_old_prime", 0x86EFC, "26807f220f", gamepatch.DUAL_OLD_SITE),
                ("dual_new_prime", 0x86F31, "26807f2211", gamepatch.DUAL_NEW_SITE)):
            p = patch(name)
            self.assertEqual((p.offset, p.original.hex()), (offset, original))
            self.assertEqual(p.replacement, bytes((0xCD, 0x98, site, 0x90, 0x90)))
            self.assertNotIn(name, gamepatch.SPELLS_MANUAL)
        self.assertEqual(game.RULE_DUAL_CLASS >> 16, 2048)
        self.assertIn(("dual_class", game.RULE_DUAL_CLASS), game.RULE_SETTINGS)

    def test_dual_level(self):
        """DUAL_LEVEL: "cmp byte [es:bx+24h],2" (the sheet's first level), 3 with RULE_HI_DUAL; the
        menus' "jl" (no DUAL) and the window's "jnl" (on)."""
        sheet = SHEETS * 16 + 0x100
        for rule, level, menu in ((0, 1, False), (0, 2, True), (0, 3, True), (2048, 2, False), (2048, 3, True),
                                  (2048, 9, True)):
            self.rules_hi(rule)
            self.mu.mem_write(sheet + 0x24, bytes((level,)))
            for name in ("dual_level_menu", "dual_level_view"):
                self.assertEqual(self.jumps(name, es=SHEETS, ebx=0x100), not menu, (rule, level))
            self.assertEqual(self.jumps("dual_level_window", "7d", es=SHEETS, ebx=0x100), menu, (rule, level))

    def scores(self, member, *values):
        self.mu.mem_write(CREATURES * 16 + member * 0x3A + 0x22, bytes(values))

    def test_dual_primes(self):
        """DUAL_PRIMES: the game's one compare at ES:BX + 22h without the rule; with it every prime
        requisite of the class (tracker.PRIME_REQUISITES): the old class's (the sheet's +21h) all 15+,
        the new one's (DI) all 17+, on the creature's scores; "jl" taken when one is short."""
        member = 2
        self.mu.mem_write(SHEETS * 16 + member * 0x47 + 0x21, bytes((13, 0, 0)))  # (a ranger)
        creature = member * 0x3A
        # without the rule: the byte the game's table points at (here WIS, +4)
        self.rules_hi(0)
        self.scores(member, 3, 3, 3, 3, 15, 3)
        self.assertFalse(self.jumps("dual_old_prime", es=CREATURES, ebx=creature + 4, esi=member))
        self.scores(member, 3, 3, 3, 3, 14, 3)
        self.assertTrue(self.jumps("dual_old_prime", es=CREATURES, ebx=creature + 4, esi=member))
        self.scores(member, 3, 3, 3, 3, 17, 3)
        self.assertFalse(self.jumps("dual_new_prime", es=CREATURES, ebx=creature + 4, esi=member, edi=12))
        # with the rule: a ranger's STR, DEX and WIS all 15+
        self.rules_hi(2048)
        for values, short in (((15, 15, 3, 3, 15, 3), False), ((14, 15, 3, 3, 15, 3), True),
                              ((15, 14, 3, 3, 15, 3), True), ((15, 15, 3, 3, 14, 3), True),
                              ((25, 20, 3, 3, 18, 3), False)):
            self.scores(member, *values)
            self.assertEqual(self.jumps("dual_old_prime", es=CREATURES, ebx=creature + 4, esi=member), short, values)
        # the new class's (DI) all 17+: psionicist CON and WIS, druid WIS and CHA, thief DEX
        for cls, values, short in ((12, (3, 3, 17, 3, 17, 3), False), (12, (3, 3, 16, 3, 18, 3), True),
                                   (12, (3, 3, 18, 3, 16, 3), True), (5, (3, 3, 3, 3, 17, 17), False),
                                   (5, (3, 3, 3, 3, 17, 16), True), (17, (3, 17, 3, 3, 3, 3), False),
                                   (11, (3, 3, 3, 16, 3, 3), True), (9, (17, 3, 3, 3, 3, 3), False)):
            self.scores(member, *values)
            self.assertEqual(self.jumps("dual_new_prime", es=CREATURES, ebx=creature + 4, esi=member, edi=cls),
                             short, (cls, values))

    def test_dual_primes_table(self):
        """DSCLOG's DUAL_PRIMES_OF is tracker.PRIME_REQUISITES (the manual's), a bit an ability."""
        table = bytes([0] + [sum(1 << a for a in tracker.PRIME_REQUISITES[c]) for c in range(1, 18)])
        self.assertIn(b"\x00" + table[1:], self.image)
        asm = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dos", "dsclog.asm")
        with open(asm, encoding="latin-1") as f:
            text = f.read()
        self.assertIn("dual_primes_of db " + ", ".join(str(b) for b in table), text)

    # ---- the monsters as the manual describes them ---------------------------------------------------

    THINGS = (GAME_DS + 0x3972 - 0x4356) * 16 + 0xC36
    RECORDS = (GAME_DS - (0x4356 - 0x3CB4)) * 16 + 0x30
    SEED = 0x4122

    def manual(self, on=True):
        """Stinking Cloud's record's dice: 1d4 with the spells as the manual has them (MANUAL_ON)."""
        self.mu.mem_write(self.RECORDS + 22 * 0x20 + 4, bytes((0x41 if on else 0x61,)))

    def combatant(self, thing, creature, kind=0):
        self.mu.mem_write(self.THINGS + thing * 3, struct.pack("<BH", 2, creature))
        self.mu.mem_write(CREATURES * 16 + creature * 0x3A + 0x16, struct.pack("<H", kind))

    def log_stub(self, seg, off, count, base, counter):
        """The game's far routine SEG:OFF (its stub segment in DSUN.EXE): each call's first COUNT words of
        arguments kept at DS:BASE + 20h x the calls before it, the calls counted at DS:COUNTER."""
        code = ("5589e5565751061e078d76068b3e" + struct.pack("<H", counter).hex() + "c1e70581c7"
                + struct.pack("<H", base).hex() + "b9" + struct.pack("<H", count).hex() + "f336a5ff06"
                + struct.pack("<H", counter).hex() + "07595f5e5dcb")
        at = ((GAME_DS - (0x4356 - seg)) & 0xFFFF) * 16 + off
        self.mu.mem_write(at, bytes.fromhex(code))
        self.mu.mem_write(GAME_DS * 16 + counter, bytes(2))

    def logged(self, base, counter, count):
        n, = struct.unpack("<H", self.mu.mem_read(GAME_DS * 16 + counter, 2))
        return [struct.unpack(f"<{count}h", self.mu.mem_read(GAME_DS * 16 + base + 0x20 * i, 2 * count))
                for i in range(n)]

    def seed_for(self, *rolls):
        """A seed that makes GAME_DIE roll ROLLS (each (roll, sides)) in turn."""
        for seed in range(200000):
            s, ok = seed, True
            for roll, sides in rolls:
                s, value, _ = td.borland_rand(s)
                if value * sides // 0x8000 + 1 != roll:
                    ok = False
                    break
            if ok:
                return seed
        raise AssertionError("no seed")

    def entry(self):
        hdr_off, ring = struct.unpack_from("<H", self.image, 20)[0], struct.unpack_from("<H", self.image, 16)[0]
        n = struct.unpack("<HHH", self.mu.mem_read(TSR * 16 + hdr_off + 8, 6))
        e = td.Entry.parse(bytes(self.mu.mem_read(td.RING_SEG * 16 + ring + ((n[0] - 1) % n[2]) * td.Entry.SIZE,
                                                  td.Entry.SIZE)))
        return (e.kind, e.raw) + tuple(e.arg(at) for at in (6, 8, 0x0A, 0x0C))

    def seq(self):
        hdr_off = struct.unpack_from("<H", self.image, 20)[0]
        return struct.unpack("<H", self.mu.mem_read(TSR * 16 + hdr_off + 8, 2))[0]

    def site(self, name, count=50000, **regs):
        """PATCH NAME's bytes run to a HLT after them; SP and BP checked back."""
        p = patch(name)
        mu = self.mu
        self.at += 0x100
        start = CALLER * 16 + self.at
        mu.mem_write(start, p.replacement + b"\xf4")
        for reg, value in dict(cs=CALLER, ds=GAME_DS, ss=SS, esp=0x800, ebp=BP, eflags=IF | 2, **regs).items():
            mu.reg_write(getattr(r, "UC_X86_REG_" + reg.upper()), value)
        mu.emu_start(start, 0, count=count)
        self.assertEqual((mu.reg_read(r.UC_X86_REG_SP), mu.reg_read(r.UC_X86_REG_BP)), (0x800, BP))
        self.assertEqual(mu.reg_read(r.UC_X86_REG_IP) - self.at, len(p.replacement) + 1)

    def reg(self, name):
        return self.mu.reg_read(getattr(r, "UC_X86_REG_" + name.upper()))

    def test_monster_patches(self):
        """The kinds' data at DSUN.EXE's bytes (KINDS_FILE: the load segment's 3E45h), all in the switch."""
        k = gamepatch.KINDS_FILE
        for name, offset, original, replacement in (
                ("babau_poison", k + 3 * 4, 0x01400400, 0x00408400),  # (bit 15 for bit 24)
                ("blue_slaad_poison", k + 17 * 4, 0x12000400, 0x10008400),  # (bit 15 for bit 25)
                ("styr_kind", k + 38 * 4, 0x00000601, 0x80000400),  # (bit 31, the 3d6 breath)
                ("djinn_kind", k + 39 * 4, 0x00800020, 0),
                ("tari_kind", k + 40 * 4, 0x00000020, 0x02000000)):  # (bit 25, disease)
            p = patch(name)
            self.assertEqual((p.offset, p.original, p.replacement),
                             (offset, struct.pack("<I", original), struct.pack("<I", replacement)))
            self.assertIn(name, gamepatch.SPELLS_MANUAL)
        self.assertEqual(k, 0x43850)
        cold, cls = patch("shadow_cold"), patch("greater_shadow_class")
        self.assertEqual((cold.offset, cold.original.hex(), cold.replacement.hex()), (0x43952, "3901", "3d01"))
        self.assertEqual((cls.offset, cls.original, cls.replacement), (0x43905, bytes((11,)), bytes((4,))))
        for name, offset, original, site in (("shadow_drain", 0x7A9AB, "8b76088a460a", gamepatch.DRAIN_SITE),
                                             ("tari_bite", 0x7A747, "3d0100", gamepatch.TARI_SITE)):
            p = patch(name)
            self.assertEqual((p.offset, p.original.hex()), (offset, original))
            self.assertEqual(p.replacement[:3], bytes((0xCD, 0x98, site)))
            self.assertIn(name, gamepatch.SPELLS_MANUAL)
        from dsloader import monsters
        # the Look box's kinds as the patches make them: the shadows' class 4 now immune to cold
        rules = [monsters.Rule(0x13D, 0), monsters.Rule(0xB000, 100)]
        d = monsters.defences(rules, 0x628, True, 13, True)
        self.assertEqual((d.weapon_plus, d.immune), (1, ["poison", "cold", "draining"]))
        self.assertEqual(d.special, [monsters.DRAIN_TEXT])
        self.assertEqual(monsters.defences(rules, 0x624, True, 15, True).special, [monsters.DRAIN_TEXT])
        self.assertEqual(monsters.defences(rules, 0x624, True, 15, False).special, ["2d6 cold"])
        self.assertEqual(monsters.defences([], 0x02000000, False, 40, True).special, ["disease (1 bite in 20)"])
        self.assertIn(monsters.DJINN_NOTE, monsters.defences([], 0, False, 39, True).notes)
        self.assertIn("Breathes fire for 3d6", " ".join(monsters.describe(monsters.defences([], 0x80000400, False, 38, True))))
        self.assertEqual(monsters.defences([], 0x00408400, False, 3, True).special, ["deadly poison"])

    def test_shadow_drain(self):
        """SHADOW_DRAIN (7A9ABh, in 7A9A7h(target, attacker, bit, power)): the moves made; a shadow's
        (kind 15) 172 and a greater shadow's (13) 173 are 598:3Eh(target, the shadow, the power, Weakened
        68, 2d4 x 600 seconds, -1: the ability routine adds it) and 5B8:7Fh(target), AL 8 (no power of the game's), recorded (kind 14,
        7: target, shadow, turns, power); any other the game's."""
        self.log_stub(0x428F, 0x3E, 7, 0x600, 0x5FE)
        self.log_stub(0x42AB, 0x7F, 1, 0x700, 0x5FC)
        self.combatant(40, 7)
        for kind, power, drains in ((15, 172, True), (13, 173, True), (15, 173, False), (13, 172, False),
                                    (3, 172, False), (0, 172, False)):
            self.combatant(41, 8, kind)
            self.mu.mem_write(GAME_DS * 16 + 0x5FE, bytes(2))
            self.mu.mem_write(GAME_DS * 16 + 0x5FC, bytes(2))
            self.mu.mem_write(SS * 16 + BP + 6, struct.pack("<HHIH", 40, 41, 3, power))
            self.mu.mem_write(GAME_DS * 16 + self.SEED, struct.pack("<I", self.seed_for((3, 4), (2, 4))))
            before = self.seq()
            self.site("shadow_drain", esi=0x1234, eax=0xFFFF, ebx=0x2222)
            self.assertEqual((self.reg("si"), self.reg("bx")), (41, 0x2222), (kind, power))
            if drains:
                self.assertEqual(self.reg("ax") & 0xFF, 8)
                self.assertEqual(self.logged(0x600, 0x5FE, 7), [(40, 41, power, 68, 5 * 600, 0, -1)])
                self.assertEqual(self.logged(0x700, 0x5FC, 1), [(40,)])
                self.assertEqual(self.entry(), (14, 7, 40, 41, 5, power))
            else:
                self.assertEqual(self.reg("ax") & 0xFF, 3)
                self.assertEqual(self.logged(0x600, 0x5FE, 7), [])
                self.assertEqual(self.seq(), before)

    def test_tari_bite(self):
        """TARI_BITE (7A747h, "cmp ax,1" after the disease's d10): a Tari's (kind 40, [BP-0Eh] its
        creature) 1 needs a d2 of 1 as well, recorded (kind 14, 8); others the game's compare."""
        creature = 8 * 0x3A
        self.mu.mem_write(SS * 16 + BP - 0x0E, struct.pack("<HH", creature, CREATURES))
        for kind, roll, d2, disease in ((40, 1, 1, True), (40, 1, 2, False), (40, 2, 1, False), (0, 1, 2, True),
                                        (17, 1, 2, True), (17, 3, 1, False)):
            self.mu.mem_write(CREATURES * 16 + creature + 0x16, struct.pack("<H", kind))
            self.mu.mem_write(GAME_DS * 16 + self.SEED, struct.pack("<I", self.seed_for((d2, 2))))
            before = self.seq()
            self.assertEqual(self.jumps("tari_bite", "75", eax=roll, esi=40, edi=41), not disease, (kind, roll, d2))
            if kind == 40 and roll == 1:
                self.assertEqual(self.entry()[:5], (14, 8, 40, 41, d2))
            else:
                self.assertEqual(self.seq(), before)

    def test_djinn_turn(self):
        """DJINN_TURN (PROBE_MOVE's end, a turn's start: DI the combatant, SI its creature): with the
        manual's monsters, a djinn's (kind 39) first turn of a fight puts Invisible (23, spell 46) for 14
        rounds and Mirror Images (25, spell 19) 1d4 + 3 on it (598:3Eh), recorded (kind 14, 9); its next
        turns nothing, nor anyone else's, nor without the switch; a fight's first round (ACID_ROUND) starts
        it again."""
        image = self.image
        at = td.install_at(image, 0xFB)
        self.mu.mem_write(0xFB * 4, struct.pack("<HH", struct.unpack_from("<H", image, at + 4)[0], TSR))
        self.log_stub(0x428F, 0x3E, 7, 0x600, 0x5FE)
        self.manual(True)
        self.mu.mem_write(CREATURES * 16 + 9 * 0x3A + 0x16, struct.pack("<H", 39))
        self.mu.mem_write(CREATURES * 16 + 10 * 0x3A + 0x16, struct.pack("<H", 0))
        def turn(thing, creature):
            self.mu.mem_write(GAME_DS * 16 + 0x5FE, bytes(2))
            self.at += 0x40
            start = CALLER * 16 + self.at
            self.mu.mem_write(start, bytes.fromhex("cdfb90909090f4"))
            for reg, value in dict(cs=CALLER, ds=GAME_DS, ss=SS, esp=0x800, ebp=BP, eflags=IF | 2, es=0x8800,
                                   ebx=creature * 2, esi=creature, edi=thing, eax=90).items():
                self.mu.reg_write(getattr(r, "UC_X86_REG_" + reg.upper()), value)
            self.mu.emu_start(start, 0, count=50000)
            self.assertEqual((self.reg("sp"), self.reg("si"), self.reg("di")), (0x800, creature, thing))
            return self.logged(0x600, 0x5FE, 7)
        self.mu.mem_write(GAME_DS * 16 + self.SEED, struct.pack("<I", self.seed_for((2, 4))))
        self.assertEqual(turn(12, 9), [(12, 12, 46, 23, 14 * 60, 0, 0), (12, 12, 19, 25, -5, -1, 0)])
        self.assertEqual(self.entry(), (14, 9, 12, 5, 14, 0))
        self.assertEqual(turn(12, 9), [])  # (its next turn)
        self.assertEqual(turn(13, 10), [])  # (not a djinn)
        self.mu.mem_write(GAME_DS * 16 + 0x55A, struct.pack("<H", 1))  # (a fight's first round)
        self.at += 0x40
        start = CALLER * 16 + self.at
        self.mu.mem_write(start, bytes((0xCD, 0x98, gamepatch.ROUND_SITE, 0x90, 0x90, 0xF4)))
        for reg, value in dict(cs=CALLER, ds=GAME_DS, ss=SS, esp=0x800, ebp=BP, eflags=IF | 2).items():
            self.mu.reg_write(getattr(r, "UC_X86_REG_" + reg.upper()), value)
        self.mu.emu_start(start, 0, count=200000)
        self.manual(False)
        self.assertEqual(turn(12, 9), [])  # (without the switch)
        self.manual(True)
        self.assertEqual(len(turn(12, 9)), 2)  # (a new fight)
        # combatants past 64 (map things up to 520: the people the Loader adds are past 256), each its own
        self.assertEqual(len(turn(300, 9)), 2)
        self.assertEqual(turn(300, 9), [])
        self.assertEqual(len(turn(44, 9)), 2)  # (not 300's bit)
        self.assertEqual(len(turn(519, 9)), 2)
        self.assertEqual(turn(519, 9), [])
        self.assertEqual(len(turn(520, 9)), 0)  # (past the map things: none)

    def test_whirlwind_swept(self):
        """Whirlwind's damage after a failed save (ACID_ONCE, 78DEFh: [BP+0Ah] the spell, [BP+6] the
        combatant) out of the combatant's turn marks it SWEPT (a bit per map thing, up to 520): its next
        turn's start (PROBE_MOVE: DI the combatant, BX its creature x 2, AX its movement) has no movement
        and initiative -1, once; others' turns as ever."""
        image = self.image
        at = td.install_at(image, 0xFB)
        self.mu.mem_write(0xFB * 4, struct.pack("<HH", struct.unpack_from("<H", image, at + 4)[0], TSR))
        self.manual(False)
        def swept(thing):
            self.mu.mem_write(td.SS * 16 + BP + 6, struct.pack("<H", thing))
            self.mu.mem_write(td.SS * 16 + BP + 0x0A, struct.pack("<H", game.WHIRLWIND_SPELL))
            self.site("acid_once")
        def turn(thing, creature=9):
            self.mu.mem_write(0x8800 * 16 + creature * 2 + 0x22B, bytes(2))
            self.mu.mem_write(0x8800 * 16 + creature * 4 + 0xD9, struct.pack("<H", 5))
            self.at += 0x40
            start = CALLER * 16 + self.at
            self.mu.mem_write(start, bytes.fromhex("cdfb90909090f4"))
            for reg, value in dict(cs=CALLER, ds=GAME_DS, ss=SS, esp=0x800, ebp=BP, eflags=IF | 2, es=0x8800,
                                   ebx=creature * 2, esi=creature, edi=thing, eax=90).items():
                self.mu.reg_write(getattr(r, "UC_X86_REG_" + reg.upper()), value)
            self.mu.emu_start(start, 0, count=50000)
            self.assertEqual((self.reg("sp"), self.reg("bx"), self.reg("si"), self.reg("di"), self.reg("ax")),
                             (0x800, creature * 2, creature, thing, 90))
            return struct.unpack("<Hh", self.mu.mem_read(0x8800 * 16 + creature * 2 + 0x22B, 2)
                                 + self.mu.mem_read(0x8800 * 16 + creature * 4 + 0xD9, 2))
        for thing in (12, 64, 300, 519):
            self.assertEqual(turn(thing), (90, 5))
            swept(thing)
            self.assertEqual(self.entry()[:2], (11, thing))
            self.assertEqual(turn(thing - 8 if thing > 12 else 13), (90, 5), thing)  # (another's: as ever)
            self.assertEqual(turn(thing), (0, -1), thing)
            self.assertEqual(turn(thing), (90, 5), thing)  # (once)
        swept(300)
        self.assertEqual(turn(44), (90, 5))  # (not 300's bit)
        self.assertEqual(turn(300), (0, -1))
        swept(520)  # (past the map things: not marked)
        self.assertEqual(turn(520), (90, 5))

    # ---- resting ------------------------------------------------------------------------------------

    CAST_STUB = ("5589e55657510653501e078d76068b3efe05c1e70581c70006b90d00f336a5ff06fe058b5e0ad1e38b870008c41e65"
                 "168b76066bf63a260100585b07595f5e5dcb")  # (13 words logged at DS:600h + 20h a call; the
    # target's HP + DS:800h's word for the spell, a cure's stand-in)
    LEVEL_STUB = "5589e5538b5e068a87%02x065b5dcb"  # (AL the byte at DS:6xxh + the member)

    def test_rest_patches(self):
        """The two sites at DSUN.EXE's bytes, in no switch (the rule is DSCLOG's, RULE_HI_REST 4096)."""
        for name, offset, original, site in (("rest_spells", 0x80675, "c746f00000", gamepatch.REST_PRE_SITE),
                                             ("rest_hp", 0x808AF, "268907", gamepatch.REST_HP_SITE)):
            p = patch(name)
            self.assertEqual((p.offset, p.original.hex()), (offset, original))
            self.assertEqual(p.replacement[:3], bytes((0xCD, 0x98, site)))
            self.assertNotIn(name, gamepatch.SPELLS_MANUAL)
        self.assertEqual(game.RULE_REST >> 16, 4096)
        self.assertIn(("rest_heal", game.RULE_REST), game.RULE_SETTINGS)

    def party(self):
        """Four members, things 0-3 = creatures 0-3 = sheets 0-3: (status, HP, most, CON, class)."""
        mu = self.mu
        members = ((1, 30, 30, 12, 1), (1, 20, 40, 16, 9), (1, 30, 30, 15, 12), (3, -2, 30, 10, 17))
        for m, (status, hp, most, con, cls) in enumerate(members):
            mu.mem_write(self.THINGS + m * 3, struct.pack("<BH", 2, m))
            c = CREATURES * 16 + m * 0x3A
            mu.mem_write(c, struct.pack("<h", hp))
            mu.mem_write(c + 2, struct.pack("<H", 12 if m == 2 else 0))  # (PSP)
            mu.mem_write(c + 4, struct.pack("<H", m))
            mu.mem_write(c + 0x1C, bytes((status, 1 + m)))  # (status, side)
            mu.mem_write(c + 0x24, bytes((con,)))
            sh = SHEETS * 16 + m * 0x47
            mu.mem_write(sh + 8, struct.pack("<h", most))
            mu.mem_write(sh + 0x21, bytes((cls, 0, 0)))
        hp_table = (GAME_DS - (0x4356 - 0x40B1)) * 16
        groups = bytearray(32)
        for cls in (9, 10, 13, 14, 15, 16):
            groups[cls] = 1  # (warriors)
        mu.mem_write(hp_table + 0x10, bytes(groups))
        mu.mem_write(hp_table + 0x52, bytes((0,) * 15 + (1, 2, 2, 3, 4, 5, 5, 6, 6, 7, 7)))  # (CON 0-25)
        return members

    def priests(self):
        mu = self.mu
        levels = (GAME_DS - (0x4356 - 0x3FB9)) * 16 + 0x19C
        for spell, level in ((71, 1), (112, 4), (127, 5), (118, 4), (94, 3), (96, 3)):
            mu.mem_write(levels + spell * 7, bytes((level,)))
        known = (GAME_DS - (0x4356 - 0x3800)) * 16 + 0x168
        for spell in (71, 112, 127, 118, 94, 96):
            mu.mem_write(known + spell, bytes((1,)))  # (member 0 knows them)
        mu.mem_write(GAME_DS * 16 + 0x4B11, bytes((0, 2, 0, 0, 2, 1, 0)))  # (member 0's slots: 1st 2, 4th 2, 5th 1)
        powers = (GAME_DS - (0x4356 - 0x37F0)) * 16 + 0x77
        mu.mem_write(powers + 2 * 0x22 + 13, bytes((8,)))  # (member 2 knows Cell Adjustment)
        heal = bytearray(0x200)
        for spell, amount in ((71, 4), (112, 10), (127, 16), (151, 3)):
            struct.pack_into("<H", heal, spell * 2, amount)
        mu.mem_write(GAME_DS * 16 + 0x800, bytes(heal))
        mu.mem_write(GAME_DS * 16 + 0x6F0, bytes((7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)))  # (cleric 7)
        stub_at = lambda off: ((GAME_DS - (0x4356 - 0x42AB)) & 0xFFFF) * 16 + off
        for entry, code, table in ((0xB1, 0x300, 0xF0), (0xB6, 0x320, 0xF8)):  # (the entries 5 bytes apart)
            mu.mem_write(stub_at(entry), b"\xe9" + struct.pack("<h", code - entry - 3))
            mu.mem_write(stub_at(code), bytes.fromhex(self.LEVEL_STUB % table))
        mu.mem_write(stub_at(0x20), bytes.fromhex(self.CAST_STUB))
        mu.mem_write(GAME_DS * 16 + 0x5FE, bytes(2))

    def effects(self, *entries):
        """The table of active effects: (owner, effect), in owner order."""
        table = (GAME_DS - (0x4356 - 0x3BF6)) * 16 + 0x106
        data = b"".join(struct.pack("<hhhBBBb", owner, 0, 0, effect, k + 1, 0, 0) for k, (owner, effect) in enumerate(entries))
        self.mu.mem_write(table, data + bytes(40))
        self.mu.mem_write(GAME_DS * 16 + 0x1E24, struct.pack("<H", len(entries)))

    def test_rest_spells(self):
        """REST_PRE (80675h, the rest's first move: [BP+6] the mode): with RULE_HI_REST, mode 0 and no
        fight, the casts through 5B8:20h with 809A2h's arguments: Neutralize Poison on the Poisoned, Cell
        Adjustment on the Diseased, then the most wounded after natural healing, the cure that fits;
        slots and PSP taken; the move made either way; nothing with the rule off or mode 1."""
        self.party()
        self.priests()
        self.effects((1, 35), (3, 13))  # (member 1 Poisoned, member 3 Diseased)
        fight = (GAME_DS - (0x4356 - 0x377E)) * 16 + 0x19
        self.mu.mem_write(fight, bytes(2))
        for rules, mode in ((0, 0), (4096, 1)):
            self.rules_hi(rules)
            self.mu.mem_write(SS * 16 + BP + 6, struct.pack("<H", mode))
            self.mu.mem_write(SS * 16 + BP - 0x10, struct.pack("<H", 0x5555))
            self.site("rest_spells")
            self.assertEqual(struct.unpack("<H", self.mu.mem_read(SS * 16 + BP - 0x10, 2))[0], 0)
            self.assertEqual(self.logged(0x600, 0x5FE, 3), [])
        self.rules_hi(4096)
        self.mu.mem_write(SS * 16 + BP + 6, struct.pack("<H", 0))
        kept = bytes(self.mu.mem_read(CREATURES * 16 + 3 * 0x3A, 0x3A))
        self.mu.mem_write(CREATURES * 16 + 3 * 0x3A + 0x24, bytes((17,)))
        self.site("rest_hp", es=CREATURES, ebx=3 * 0x3A, eax=40, esi=3)  # (a heal first: its CON, 17, recorded)
        self.mu.mem_write(CREATURES * 16 + 3 * 0x3A, kept)
        self.site("rest_spells", count=2000000, esi=0x1111, edi=0x2222)
        self.assertEqual((self.reg("si"), self.reg("di")), (0x1111, 0x2222))
        casts = self.logged(0x600, 0x5FE, 13)
        self.assertEqual([(c[0], c[1], c[2]) for c in casts],
                         [(1, 0, 118), (3, 2, 151), (3, 0, 127), (1, 0, 112), (3, 0, 71), (3, 0, 71), (1, 2, 151)])
        # (0, far &[BP-2] of REST_PRE's frame, under the INT's, 0, 0, 0, 8, 63h, the cleric level 7, its side 1)
        self.assertEqual((casts[0][3],) + casts[0][5:], (0, SS, 0, 0, 0, 8, 0x63, 7, 1))
        self.assertLess(casts[0][4], 0x800)
        self.assertEqual(casts[1][11:], (1, 3))  # (the psionicist's: level 1, its side)
        self.assertEqual(bytes(self.mu.mem_read(GAME_DS * 16 + 0x4B11, 7)), bytes(7))  # (every slot spent)
        self.assertEqual(struct.unpack("<H", self.mu.mem_read(CREATURES * 16 + 2 * 0x3A + 2, 2))[0], 2)  # (PSP 12 - 10)
        self.assertEqual(self.entry()[:2], (15, 1))
        hdr_off, ring = struct.unpack_from("<H", self.image, 20)[0], struct.unpack_from("<H", self.image, 16)[0]
        n = struct.unpack("<HHH", self.mu.mem_read(TSR * 16 + hdr_off + 8, 6))
        e = td.Entry.parse(bytes(self.mu.mem_read(td.RING_SEG * 16 + ring + ((n[0] - 1) % n[2]) * td.Entry.SIZE,
                                                  td.Entry.SIZE)))
        self.assertEqual(e.arg(0x10), 0)  # (a cast's last word 0, not the heal's CON left over)

    def test_rest_hp(self):
        """REST_HP (808AFh, "mov [es:bx],ax": ES:BX the creature, AX the most, SI the member): the most
        without the rule or in mode 1; with it 3 + CON's part (a warrior's, else at most +2), at most the
        most, no less than before nor 1; recorded (kind 15, 2)."""
        self.party()
        mu = self.mu
        def rest(rules, mode, member, hp, most=40, con=16, cls=9):
            self.rules_hi(rules)
            mu.mem_write(SS * 16 + BP + 6, struct.pack("<H", mode))
            c = CREATURES * 16 + member * 0x3A
            mu.mem_write(c, struct.pack("<h", hp))
            mu.mem_write(c + 0x24, bytes((con,)))
            mu.mem_write(SHEETS * 16 + member * 0x47 + 0x21, bytes((cls, 0, 0)))
            self.site("rest_hp", es=CREATURES, ebx=member * 0x3A, eax=most, esi=member)
            self.assertEqual((self.reg("ax"), self.reg("bx"), self.reg("si")), (most, member * 0x3A, member))
            return struct.unpack("<h", mu.mem_read(c, 2))[0]
        self.assertEqual(rest(0, 0, 1, 20), 40)
        self.assertEqual(rest(4096, 1, 1, 20), 40)
        self.assertEqual(rest(4096, 0, 1, 20), 25)  # (3 + 2 at CON 16)
        self.assertEqual(self.entry(), (15, 2, 1, 20, 2, 25))
        self.assertEqual(rest(4096, 0, 1, 20, con=19), 27)  # (a warrior's +4 at 19, this table's)
        self.assertEqual(rest(4096, 0, 1, 20, con=19, cls=11), 25)  # (a preserver's at most +2)
        self.assertEqual(rest(4096, 0, 1, 38), 40)  # (no more than the most)
        self.assertEqual(rest(4096, 0, 1, 45), 45)  # (no less than before: Extra Hitpoints)
        self.assertEqual(rest(4096, 0, 3, -4, con=10), 1)  # (out cold: at least 1)
        self.assertEqual(rest(4096, 0, 2, 10, con=3), 13)  # (CON 3: +3 + 0 in this table)


class ManualMonsterTests(unittest.TestCase):
    """The Loader's side: the Styr's, Djinn's and Tari's records in the copy of SEGOBJEX and in a
    running game (monsters.object_chunks, mend)."""

    def record(self, name, race, kind=0, thac0=0, level=0, ac=0, sides=0):
        from dsloader import monsters
        rec = bytearray(monsters.RDFF_SHEET + game.SHEET_SIZE)
        struct.pack_into("<H", rec, 0x08, game.CREATURE_SIZE)
        struct.pack_into("<H", rec, 0x4C, game.SHEET_SIZE)
        c, s = monsters.RDFF_CREATURE, monsters.RDFF_SHEET
        rec[c + game.CREATURE_NAME:c + game.CREATURE_NAME + len(name)] = name
        struct.pack_into("<H", rec, c + 0x16, kind)
        rec[c + 0x1F], rec[s + 0x18], rec[s + 0x24], rec[s + 0x27], rec[s + 0x31] = thac0, race, level, ac, sides
        return bytes(rec)

    def test_object_chunks(self):
        from dsloader import monsters
        chunks = {("RDFF", 99): self.record(b"Styr", 12, 0, 11, 10, 0, 10),
                  ("RDFF", 60): self.record(b"Tari", 1, 0, 18, 2, 10, 2),
                  ("RDFF", 65): self.record(b"Tari", 1, 0, 17, 2, 10, 2),  # (not the game's: left)
                  ("RDFF", 122): self.record(b"Djinn", 14, 0, 11, 10, 4, 8),
                  ("RDFF", 243): self.record(b"Rat", 1, 0, 18, 2, 10, 2)}
        out = monsters.object_chunks(chunks)
        self.assertEqual(sorted(out), [("RDFF", 60), ("RDFF", 99), ("RDFF", 122)])
        c, s = monsters.RDFF_CREATURE, monsters.RDFF_SHEET
        styr = out[("RDFF", 99)]
        self.assertEqual((struct.unpack_from("<H", styr, c + 0x16)[0], styr[c + 0x1F], styr[s + 0x24]), (38, 7, 14))
        tari = out[("RDFF", 60)]
        self.assertEqual((struct.unpack_from("<H", tari, c + 0x16)[0], tari[c + 0x1F], tari[s + 0x24], tari[s + 0x27],
                          tari[s + 0x31]), (40, 17, 3, 6, 3))
        self.assertEqual(struct.unpack_from("<H", out[("RDFF", 122)], c + 0x16)[0], 39)

    def test_real_objects(self):
        """In the game's SEGOBJEX (DSUN_OBJECTS), all five records are the game's: each changed."""
        path = os.environ.get("DSUN_OBJECTS") or "/tmp/playtest/inst/SEGOBJEX.GFF"
        if not os.path.exists(path):
            self.skipTest("no SEGOBJEX.GFF")
        from dsloader import gff, monsters
        with open(path, "rb") as f:
            chunks = gff.read_gff(f.read())
        self.assertEqual(sorted(monsters.object_chunks(chunks)), [("RDFF", n) for n in (60, 65, 99, 122, 243)])

    def test_mend(self):
        """A running game's Tari made the manual's with the switch, and back without it; one neither
        way (its THAC0 changed) left."""
        from dsloader import monsters

        class Guest:
            def __init__(self):
                self.mem = bytearray(0x100000)

            def read(self, at, n):
                return bytes(self.mem[at:at + n])

            def write(self, at, data):
                self.mem[at:at + len(data)] = data

        class Gd:
            ds = 0x1000

            def __init__(self):
                self.guest = Guest()
                struct.pack_into("<HH", self.guest.mem, 0x10000 + game.CREATURES_PTR, 0, 0x2000)
                struct.pack_into("<HH", self.guest.mem, 0x10000 + game.SHEETS_PTR, 0, 0x3000)

            def combatants(self):
                return {20: 5, 21: 6}

            def creatures(self, n):
                return self.guest.read(0x20000, n * game.CREATURE_SIZE)

            def creature_name(self, i):
                return "Tari"

        gd = Gd()
        for index, sheet, thac0 in ((5, 9, 18), (6, 10, 15)):
            at = 0x20000 + index * game.CREATURE_SIZE
            gd.guest.write(at + game.CREATURE_NAME, b"Tari\0")
            gd.guest.write(at + game.CREATURE_SHEET_INDEX, struct.pack("<H", sheet))
            gd.guest.write(at + 0x1F, bytes((thac0,)))
            s = 0x30000 + sheet * game.SHEET_SIZE
            gd.guest.write(s + 0x18, bytes((1,)))
            gd.guest.write(s + 0x24, bytes((2,)))
            gd.guest.write(s + 0x27, bytes((10,)))
            gd.guest.write(s + 0x31, bytes((2,)))
        self.assertEqual(monsters.mend(gd, True), ["(Tari: as the manual describes it)"])
        at, s = 0x20000 + 5 * game.CREATURE_SIZE, 0x30000 + 9 * game.SHEET_SIZE
        self.assertEqual((struct.unpack_from("<H", gd.guest.mem, at + 0x16)[0], gd.guest.mem[at + 0x1F],
                          gd.guest.mem[s + 0x24], gd.guest.mem[s + 0x27], gd.guest.mem[s + 0x31]), (40, 17, 3, 6, 3))
        self.assertEqual(struct.unpack_from("<H", gd.guest.mem, 0x20000 + 6 * game.CREATURE_SIZE + 0x16)[0], 0)
        self.assertEqual(monsters.mend(gd, True), [])
        self.assertEqual(monsters.mend(gd, False), ["(Tari: as the game has it)"])
        self.assertEqual((struct.unpack_from("<H", gd.guest.mem, at + 0x16)[0], gd.guest.mem[at + 0x1F],
                          gd.guest.mem[s + 0x24], gd.guest.mem[s + 0x27], gd.guest.mem[s + 0x31]), (0, 18, 2, 10, 2))
        self.assertEqual(monsters.mend(gd, False), [])  # (the game's already: nothing more)


if __name__ == "__main__":
    unittest.main()
