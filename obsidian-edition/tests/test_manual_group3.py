"""Group 3 of the spells and psionics as the manual describes them (gamepatch.SPELLS_MANUAL): DSCLOG's
BLUR_SITE, FSHIELD_SITE, CLOUD_SAVE_SITE, CLOUD_KILL_SITE, LOWRES_SITE, STRENGTH_SITE, RAINBOW_SITE,
PSI_SITE, BIO_SITE and CELL_SITE run in Unicorn at the game's bytes, with the game's routines they
call as stand-ins; Chill Touch on an undead (HOLD_HD's CHILL_UNDEAD), Lower Resistance's level kept
(ACID_ROUNDS), Cell Adjustment's disease noted (ACID_ONCE), Strength and Cat's Grace not added up
(PROBE_GRACE_ABILITY's GR_SHADOWED) and Heal's cure of Feeblemind (PROBE_CURE); and the Loader's side:
the dice log's lines, the save modifiers, the descriptions."""
import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import game, gamepatch, spelltexts  # noqa: E402

import test_dsclog as td  # noqa: E402

try:
    from unicorn import x86_const as r
except ImportError:  # pragma: no cover
    r = None

GAME_DS, SS, CALLER, TSR, BP, IF = td.GAME_DS, td.SS, td.CALLER, td.TSR, td.BP, td.IF
EFFECTS = (GAME_DS - (0x4356 - 0x3BF6)) * 16  # (the active effects' segment, as DSCLOG finds it)
RECORDS = (GAME_DS - (0x4356 - 0x3CB4)) * 16 + 0x30  # (the spell records)
THINGS = (GAME_DS + 0x3972 - 0x4356) * 16 + 0xC36
CREATURES, SHEETS = 0x9000, 0xA000
SEED = 0x4122  # (DS: the game's rand() seed, GAME_DIE's)
# a far routine's stand-in: its first COUNT words of arguments kept at DS:600h, the calls counted at
# DS:5FEh (push bp / mov bp,sp / push si,di,cx,es / push ds / pop es / lea si,[bp+6] / mov di,600h /
# mov cx,COUNT / rep ss movsw / inc word [5FEh] / pops / retf)
ARGS_STUB = "5589e5565751061e078d7606bf0006b9%02x00f336a5ff06fe0507595f5e5dcb"


def patch(name):
    return next(p for p in gamepatch.PATCHES if p.name == name)


def game_die(seed, sides):
    """GAME_DIE's roll from SEED (the game's own rand(): Borland's)."""
    seed, value, _ = td.borland_rand(seed)
    return value * sides // 0x8000 + 1


def seed_for(roll, sides):
    """A seed that makes GAME_DIE roll ROLL of SIDES."""
    return next(s for s in range(100000) if game_die(s, sides) == roll)


@unittest.skipIf(td.Uc is None, "unicorn not installed")
class Group3Tests(unittest.TestCase):
    THINGS_SEG, CREATURES, ITEMS, TYPES = td.RingTests.THINGS_SEG, CREATURES, td.RingTests.ITEMS, td.RingTests.TYPES
    run_at = td.RingTests.run_at

    def setUp(self):
        td.RingTests.setUp(self)
        image = td.load_image()
        self.image = image
        at = td.install_at(image, 0x98)
        self.mu.mem_write(0x98 * 4, struct.pack("<HH", struct.unpack_from("<H", image, at + 4)[0], TSR))
        for vector, start in ((td.VEC_GRACE_ABILITY, "8946f6b90700"),):
            found = image.find(bytes.fromhex(start))
            self.assertGreater(found, 0)
            self.mu.mem_write(vector * 4, struct.pack("<HH", found, TSR))
        mu = self.mu
        mu.mem_write(GAME_DS * 16 + 0x1665, struct.pack("<HH", 0, CREATURES))
        mu.mem_write(GAME_DS * 16 + 0x1661, struct.pack("<HH", 0, SHEETS))
        for thing, creature in ((2, 5), (40, 7), (41, 8)):
            mu.mem_write(THINGS + thing * 3, struct.pack("<BH", 2, creature))
            mu.mem_write(CREATURES * 16 + creature * 0x3A + 4, struct.pack("<H", creature))  # (sheet = creature)
        self.manual(True)
        self.hdr_off, self.ring = struct.unpack_from("<H", image, 20)[0], struct.unpack_from("<H", image, 16)[0]

    # ---- the game's memory ------------------------------------------------------------------------

    def manual(self, on):
        """Stinking Cloud's record's dice: 1d4 with the spells as the manual has them (MANUAL_ON)."""
        self.mu.mem_write(RECORDS + 22 * 0x20 + 4, bytes((0x41 if on else 0x61,)))

    def effects(self, *entries):
        """The table of active effects: (owner, caster, spell, effect, handle, charges, amount)."""
        data = b"".join(struct.pack("<hhhBBBb", *e) for e in entries)
        self.mu.mem_write(EFFECTS + 0x106, data + bytes(40))
        self.mu.mem_write(GAME_DS * 16 + 0x1E24, struct.pack("<H", len(entries)))

    def table(self):
        n, = struct.unpack("<H", self.mu.mem_read(GAME_DS * 16 + 0x1E24, 2))
        data = bytes(self.mu.mem_read(EFFECTS + 0x106, n * 10))
        return [struct.unpack_from("<hhhBBBb", data, i * 10) for i in range(n)]

    def sheet(self, creature, classes, levels, race=4):
        self.mu.mem_write(SHEETS * 16 + creature * 0x47 + 0x18, bytes((race,)))
        self.mu.mem_write(SHEETS * 16 + creature * 0x47 + 0x21, bytes(classes) + bytes(levels))

    def stub(self, seg, off, count):
        """The game's far routine SEG:OFF (its stub segment in DSUN.EXE) as ARGS_STUB."""
        at = ((GAME_DS - (0x4356 - seg)) & 0xFFFF) * 16 + off
        self.mu.mem_write(at, bytes.fromhex(ARGS_STUB % count))
        self.mu.mem_write(GAME_DS * 16 + 0x5FE, bytes(2))

    def called(self, count):
        """The stand-in's arguments, None if it wasn't called."""
        if not struct.unpack("<H", self.mu.mem_read(GAME_DS * 16 + 0x5FE, 2))[0]:
            return None
        return struct.unpack(f"<{count}H", self.mu.mem_read(GAME_DS * 16 + 0x600, 2 * count))

    def seq(self):
        return struct.unpack("<H", self.mu.mem_read(TSR * 16 + self.hdr_off + 8, 2))[0]

    def entry(self):
        n = struct.unpack("<HHH", self.mu.mem_read(TSR * 16 + self.hdr_off + 8, 6))
        e = td.Entry.parse(bytes(self.mu.mem_read(td.RING_SEG * 16 + self.ring + ((n[0] - 1) % n[2]) * td.Entry.SIZE,
                                                  td.Entry.SIZE)))
        return (e.kind, e.raw) + tuple(e.arg(at) for at in (6, 8, 0x0A, 0x0C))

    def frame(self, **words):
        """Words of the game's frame: {"p6": value} at BP+6, {"m6": value} at BP-6."""
        for key, value in words.items():
            at = BP + int(key[1:], 16) * (1 if key[0] == "p" else -1)
            self.mu.mem_write(SS * 16 + at, struct.pack("<H", value & 0xFFFF))

    def word(self, offset):
        return struct.unpack("<h", self.mu.mem_read(SS * 16 + BP + offset, 2))[0]

    def run_site(self, name, ways=(), count=50000, **regs):
        """PATCH NAME's bytes run, a HLT after them and at each of WAYS (from the patch's start): where
        it stopped (from the start), and the registers."""
        p = patch(name)
        mu = self.mu
        self.at += 0x100
        start = CALLER * 16 + self.at
        mu.mem_write(start, p.replacement + b"\xf4")
        for way in ways:
            mu.mem_write(CALLER * 16 + ((self.at + way) & 0xFFFF), b"\xf4")
        for reg, value in dict(cs=CALLER, ds=GAME_DS, ss=SS, esp=0x800, ebp=BP, eflags=IF | 2, **regs).items():
            mu.reg_write(getattr(r, "UC_X86_REG_" + reg.upper()), value)
        mu.emu_start(start, 0, count=count)
        self.assertEqual((mu.reg_read(r.UC_X86_REG_SP), mu.reg_read(r.UC_X86_REG_BP)), (0x800, BP))
        return (mu.reg_read(r.UC_X86_REG_IP) - self.at - 1) & 0xFFFF

    def run_code(self, code, **regs):
        """CODE run to a HLT after it (a site's INT and number: back past them)."""
        mu = self.mu
        self.at += 0x40
        start = CALLER * 16 + self.at
        mu.mem_write(start, code + b"\xf4")
        for reg, value in dict(cs=CALLER, ds=GAME_DS, ss=SS, esp=0x800, ebp=BP, eflags=IF | 2, **regs).items():
            mu.reg_write(getattr(r, "UC_X86_REG_" + reg.upper()), value)
        mu.emu_start(start, 0, count=20000)
        self.assertEqual(mu.reg_read(r.UC_X86_REG_IP) - self.at, len(code) + 1)

    def reg(self, name):
        value = self.mu.reg_read(getattr(r, "UC_X86_REG_" + name.upper()))
        return value - 0x10000 if name in ("si", "dx") and value >= 0x8000 else value

    # ---- the sites --------------------------------------------------------------------------------

    def test_patches_are_the_switchs(self):
        """Each patch at DSUN.EXE's bytes (the test's copy of them), in the switch, its site's number
        DSCLOG's."""
        for name, offset, original, site in (
                ("blur_save", 0x79DC0, "c45e0a26f6470702740146", gamepatch.BLUR_SITE),
                ("fire_shield_save", 0x79E03, "f746fc0400740dc45e0a26f6470410740383c603", gamepatch.FSHIELD_SITE),
                ("cloudkill_save", 0x79F95, "837e14397509837efa067f0383ee64", gamepatch.CLOUD_SAVE_SITE),
                ("cloudkill_kills", 0x79830, "807e10007560", gamepatch.CLOUD_KILL_SITE),
                ("lower_resistance_manual", 0x7A507,
                 "f646f980740b8b46f4992bc2d1f88946f483fe40750b8a460ab400051e002946f4", gamepatch.LOWRES_SITE),
                ("strength_dice", 0x79483, "666801000600", gamepatch.STRENGTH_SITE),
                ("rainbow_pattern_damage", 0x585A2, "8b7e068b5608", gamepatch.RAINBOW_SITE),
                ("feeblemind_psionics", 0x5D5B4, "0bc07505b000", gamepatch.PSI_SITE),
                ("biofeedback_least", 0x79C83, "83ee02", gamepatch.BIO_SITE),
                ("cell_adjustment_heal", 0x795A2, "6a02eb72", gamepatch.CELL_SITE)):
            p = patch(name)
            self.assertIn(name, gamepatch.SPELLS_MANUAL)
            self.assertEqual((p.offset, p.original.hex()), (offset, original))
            self.assertEqual(p.replacement, bytes((0xCD, gamepatch.VEC_CR_SPELLS, site)) + b"\x90" * (len(original) // 2 - 3))
        signed = patch("save_signed")  # (the saving throw's compare: "jae" made "jge")
        self.assertEqual((signed.offset, signed.original.hex(), signed.replacement.hex()), (0x79BBD, "73a6", "7da6"))
        self.assertIn("save_signed", gamepatch.SPELLS_MANUAL)
        rainbow = patch("rainbow_pattern_time")
        self.assertEqual((rainbow.offset, rainbow.original.hex(), rainbow.replacement.hex()),
                         (0x41F70 + 50 * 32 + 4, "3100", "1001"))
        self.assertIn("rainbow_pattern_time", gamepatch.SPELLS_MANUAL)
        asm = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dos", "dsclog.asm")
        with open(asm, encoding="latin-1") as f:
            text = f.read()
        for name, number in (("BLUR_SITE", 78), ("FSHIELD_SITE", 79), ("CLOUD_SAVE_SITE", 80),
                             ("CLOUD_KILL_SITE", 81), ("LOWRES_SITE", 82), ("STRENGTH_SITE", 83),
                             ("RAINBOW_SITE", 84), ("PSI_SITE", 85), ("BIO_SITE", 86), ("CELL_SITE", 87)):
            self.assertIn(f"{name} equ NS_IMAGE + {number}", text)
            self.assertEqual(getattr(gamepatch, name), gamepatch.NS_IMAGE + number)

    def bits(self, *effects):
        """The target's effects' bits at 0:7000h, far at [BP+0Ah]."""
        data = bytearray(10)
        for e in effects:
            data[e // 8] |= 1 << (e % 8)
        self.mu.mem_write(0x7000, bytes(data))
        self.frame(p0A=0x7000, p0C=0)

    def test_blur_and_barkskin(self):
        """BLUR_SITE (79DC0h): Barkskin's (57) +1, the game's, and Blur's (55) +1, past the 11 bytes."""
        for effects, want in (((), 0), ((57,), 1), ((55,), 1), ((55, 57), 2), ((56,), 0)):
            self.bits(*effects)
            self.assertEqual(self.run_site("blur_save", esi=3), 11)
            self.assertEqual(self.reg("si"), 3 + want, effects)

    def test_fire_shield(self):
        """FSHIELD_SITE (79E03h, [BP-4] the spell's damage kinds): Protection from Cold's (36) +3 against
        cold (4), the game's; Fire Shield's (20) +2 against fire (2) or cold, once."""
        for kinds, effects, want in ((4, (36,), 3), (2, (36,), 0), (4, (20,), 2), (2, (20,), 2), (6, (20,), 2),
                                     (0x80, (20,), 0), (4, (20, 36), 5), (0, (20, 36), 0)):
            self.bits(*effects)
            self.frame(m4=kinds)
            self.assertEqual(self.run_site("fire_shield_save", esi=0), 20)
            self.assertEqual(self.reg("si"), want, (kinds, effects))

    def test_cloudkill_save(self):
        """CLOUD_SAVE_SITE (79F95h, [BP+14h] the spell, [BP-6] the target's level): Cloudkill (57) at
        a level under 4: -100; 4 and up, or another spell, none (the game's was 6 or less)."""
        for spell, level, want in ((57, 0, -100), (57, 3, -100), (57, 4, 0), (57, 6, 0), (56, 1, 0)):
            self.frame(p14=spell, m6=level)
            self.assertEqual(self.run_site("cloudkill_save", esi=0), 15)
            self.assertEqual(self.reg("si"), want)

    def test_cloudkill_kills(self):
        """CLOUD_KILL_SITE (79830h, the handler's tail: [BP+10h] saved, [BP+0Eh] the spell, DI the
        target, SI its flags): an unsaved Cloudkill on a living creature of 5 levels or fewer (hit dice
        for one with no class): 4E0:61h (target, 1000), the flags' 1, recorded (kind 14, 2); then the
        way on to the tail's table (79836h); saved, past it (79896h)."""
        on, past = 0x79836 - 0x79830, 0x79896 - 0x79830
        self.stub(0x41BE, 0x61, 2)
        flags = 0x7100
        def kill(saved=0, spell=57, sheet=((9, 0, 0), (5, 0, 0)), hp=10):
            self.sheet(7, *sheet)
            self.mu.mem_write(CREATURES * 16 + 7 * 0x3A, struct.pack("<h", hp))
            self.mu.mem_write(GAME_DS * 16 + flags, bytes(1))  # (DS-relative, as the game's [si]: its DS is SS)
            self.frame(p10=saved, p0E=spell)
            before = self.seq()
            way = self.run_site("cloudkill_kills", (on, past), edi=40, esi=flags)
            self.assertEqual((self.reg("di"), self.reg("si")), (40, flags))
            entry = self.entry() if self.seq() != before else None
            return way, self.called(2), self.mu.mem_read(GAME_DS * 16 + flags, 1)[0], entry
        self.assertEqual(kill(), (on, (40, 1000), 1, (14, 2, 40, 5, 0, 0)))
        self.stub(0x41BE, 0x61, 2)
        self.assertEqual(kill(saved=1), (past, None, 0, None))
        self.assertEqual(kill(spell=56)[:2], (on, None))
        self.assertEqual(kill(sheet=((9, 0, 0), (6, 0, 0)))[:2], (on, None))  # (6th level: the damage only)
        self.assertEqual(kill(sheet=((0, 0, 0), (3, 0, 0)))[1], (40, 1000))  # (no class: its 3 HD)
        self.stub(0x41BE, 0x61, 2)
        self.assertEqual(kill(hp=0)[1], None)  # (the 1d10 killed it already)
        self.assertEqual(kill(sheet=((9, 12, 0), (2, 6, 0)))[1], None)  # (its best class's level, 6)

    def test_lower_resistance(self):
        """LOWRES_SITE (7A507h-7A527h; [BP+6] the target, SI the spell, [BP+0Ah] the cast's level, [BP-0Ch]
        the resistance, [BP-7]'s 80h Low Resistance): less 30 + the effect's level (its amount) or, for a
        Lower Resistance (64) being cast, 30 + the cast's, the bigger; ACID_ROUNDS keeps the cast's level
        (CAST_SITE's [BP+0Ch]) in the effect's amount as it is added."""
        self.effects((41, 2, 64, 31, 1, 0, 9), (40, 2, 64, 31, 1, 0, 12))
        def resist(mr, on, spell=27, level=5):
            self.frame(p6=40, p0A=level, m0C=mr)
            self.mu.mem_write(SS * 16 + BP - 7, bytes((0x80 if on else 0,)))
            self.assertEqual(self.run_site("lower_resistance_manual", esi=spell), 33)
            return self.word(-0x0C)
        self.assertEqual(resist(80, True), 38)  # (80 - 42)
        self.assertEqual(resist(30, True), -12)  # (made 0 by the game's next test)
        self.assertEqual(resist(80, False), 80)
        self.assertEqual(resist(80, False, 64, 10), 40)  # (the cast's own)
        self.assertEqual(resist(80, True, 64, 10), 38)  # (the bigger: the effect's 42)
        self.assertEqual(resist(80, True, 64, 15), 35)  # (this cast's 45)
        # ACID_ROUNDS (76525h, its "cmp dword [bp+0Eh],-9999"; ES:BX the entry less 106h)
        mu = self.mu
        mu.mem_write(SS * 16 + BP + 6, struct.pack("<4H", 2, 40, 64, 11))
        self.run_code(bytes((0xCD, 0x98, gamepatch.CAST_SITE)))
        acid = bytes((0xCD, 0x98, gamepatch.ACID_SITE)) + b"\x90" * 5
        for effect, spell, want in ((31, 64, 11), (31, 27, 0), (30, 64, 0)):
            mu.mem_write(EFFECTS + 0x10F + 10, bytes(1))
            self.frame(p0A=spell, p0C=effect, p0E=600, p10=0)
            self.run_code(acid, es=EFFECTS // 16, ebx=10)
            self.assertEqual(mu.mem_read(EFFECTS + 0x10F + 10, 1)[0], want)

    def test_strength_dice(self):
        """STRENGTH_SITE (79483h, "push dword 60001h"; DI the target, [BP+0Eh] the spell): the dice
        pushed under the INT's frame, back past the 6 bytes: Strength (23) and Cat's Grace (196) by the
        target's classes, the best of them; Adrenalin Control (148) and a classless creature 1d6."""
        p = patch("strength_dice")
        mu = self.mu
        def dice(spell, classes, thing=40):
            self.sheet(7, classes, (5, 5, 5))
            self.frame(p0E=spell)
            self.at += 0x40
            start = CALLER * 16 + self.at
            mu.mem_write(start, p.replacement + b"\xf4")
            for reg, value in dict(cs=CALLER, ds=GAME_DS, ss=SS, esp=0x800, ebp=BP, eflags=IF | 2, edi=thing,
                                   eax=0x1111, ebx=0x2222, es=0x3333).items():
                mu.reg_write(getattr(r, "UC_X86_REG_" + reg.upper()), value)
            mu.emu_start(start, 0, count=5000)
            self.assertEqual((mu.reg_read(r.UC_X86_REG_IP) - self.at, mu.reg_read(r.UC_X86_REG_SP)), (7, 0x7FC))
            self.assertEqual([mu.reg_read(x) for x in (r.UC_X86_REG_AX, r.UC_X86_REG_BX, r.UC_X86_REG_ES,
                                                       r.UC_X86_REG_DI, r.UC_X86_REG_BP)],
                             [0x1111, 0x2222, 0x3333, thing, BP])
            count, sides = struct.unpack("<HH", mu.mem_read(SS * 16 + 0x7FC, 4))
            self.assertEqual(count, 1)
            return sides
        self.assertEqual([dice(23, (c, 0, 0)) for c in (9, 10, 13, 1, 5, 17, 11, 12)], [8, 8, 8, 6, 6, 6, 4, 6])
        self.assertEqual([dice(196, (c, 0, 0)) for c in (17, 11, 9, 13, 12, 2, 6)], [8, 6, 6, 6, 6, 4, 4])
        self.assertEqual(dice(23, (11, 17, 0)), 6)  # (a preserver/thief: the thief's d6)
        self.assertEqual(dice(196, (9, 17, 0)), 8)
        self.assertEqual(dice(23, (0, 0, 0)), 6)
        self.assertEqual(dice(0x94, (9, 0, 0)), 6)  # (Adrenalin Control)
        self.assertEqual(dice(23, (9, 0, 0), thing=44), 6)  # (not a creature)
        for c in range(18):  # (game.manual_die, the dice log's, the same)
            sheet = bytearray(0x47)
            sheet[0x21] = c
            self.assertEqual(dice(23, (c, 0, 0)), game.manual_die(23, bytes(sheet))[0])
            self.assertEqual(dice(196, (c, 0, 0)), game.manual_die(196, bytes(sheet))[0])

    def test_not_added_up(self):
        """PROBE_GRACE_ABILITY (7B7D7h; AX the effect, ES:BX its entry less 106h): with the spells as the
        manual has them a Strength (67) or Adrenalin Control (66) under a bigger one of either counts for
        nothing ([BP-0Ah] 0), a Cat's Grace (54) under a bigger one (or as big, earlier) adds no DEX;
        without, each counts as the game's."""
        mu = self.mu
        self.effects((40, 2, 23, 67, 1, 0, 5), (40, 2, 148, 66, 2, 0, 3), (40, 2, 196, 54, 3, 0, 4),
                     (40, 2, 196, 54, 4, 0, 4), (41, 2, 23, 67, 5, 0, 8), (40, 2, 196, 54, 6, 0, 2))
        def look(index, on=True):
            self.manual(on)
            eid = self.table()[index][3]
            self.frame(m0A=0x7777)
            mu.mem_write(SS * 16 + BP - 0x340, struct.pack("<h", 15))
            self.run_at(bytes((0xCD, td.VEC_GRACE_ABILITY)), eax=eid, ebx=index * 10, es=EFFECTS // 16, ecx=0)
            return self.word(-0x0A), self.word(-0x340)
        self.assertEqual(look(0), (67, 15))  # (Strength 5 over Adrenalin Control's 3: counts)
        self.assertEqual(look(1), (0, 15))  # (Adrenalin Control under it: nothing)
        self.assertEqual(look(1, on=False), (66, 15))
        self.assertEqual(look(2), (54, 19))  # (the first of two 4s)
        self.assertEqual(look(3), (0, 15))
        self.assertEqual(look(5), (0, 15))
        self.assertEqual(look(5, on=False), (54, 17))
        self.assertEqual(look(4), (67, 15))  # (another creature's: its own)

    def test_rainbow_damage(self):
        """RAINBOW_SITE (585A2h, "mov di,[bp+6] / mov dx,[bp+8]"; the creature, the damage): any damage
        to a creature Paralyzed (34) by Rainbow Pattern (50) ends it through 598:48h (the creature, the
        entry's handle), recorded (kind 14, 4); Hold Person's (31) Paralyzed stays. DI and DX set."""
        self.effects((40, 2, 31, 34, 5, 0, 0), (40, 2, 50, 34, 7, 0, 0), (41, 2, 50, 34, 9, 0, 0))
        def hurt(thing, damage):
            self.stub(0x428F, 0x48, 2)
            self.frame(p6=thing, p8=damage)
            before = self.seq()
            self.assertEqual(self.run_site("rainbow_pattern_damage", edi=0x1234, edx=0x5678), 6)
            self.assertEqual((self.reg("di"), self.reg("dx")), (thing, damage))
            return self.called(2), self.entry() if self.seq() != before else None
        self.assertEqual(hurt(40, 3), ((40, 7), (14, 4, 40, 3, 0, 0)))
        self.assertEqual(hurt(40, 0), (None, None))
        self.assertEqual(hurt(41, 1)[0], (41, 9))
        self.effects((40, 2, 31, 34, 5, 0, 0))
        self.assertEqual(hurt(40, 6), (None, None))

    def test_feeblemind_psionics(self):
        """PSI_SITE (5D5B4h, "or ax,ax / jnz 5D5BDh / mov al,0"; SI the user, DI the power): a user that
        has the power (AX not 0) goes on (5D5BDh) unless Feebleminded (19): then AL 0 and the check fails
        (5D5BAh), recorded (kind 14, 6)."""
        on, no = 0x5D5BD - 0x5D5B4, 0x5D5BA - 0x5D5B4
        self.effects((40, 2, 62, 19, 1, 0, 0))
        for user, ax, want in ((40, 1, no), (41, 1, on), (41, 0, no), (40, 0, no)):
            before = self.seq()
            self.assertEqual(self.run_site("feeblemind_psionics", (on, no), eax=ax, esi=user, edi=11), want)
            self.assertEqual((self.reg("si"), self.reg("di")), (user, 11))
            if want == no:
                self.assertEqual(self.reg("ax") & 0xFF, 0)
            self.assertEqual(self.entry() if self.seq() != before else None,
                             (14, 6, 40, 11, 0, 0) if (user, ax) == (40, 1) else None)

    def test_biofeedback(self):
        """BIO_SITE (79C83h, the game's own Biofeedback "sub si,2"; SI the damage): 2 less, at least 1 of
        a blow that did any; none stays none."""
        for damage, want in ((7, 5), (3, 1), (2, 1), (1, 1), (0, 0), (-1, -1)):
            self.assertEqual(self.run_site("biofeedback_least", esi=damage & 0xFFFF), 3)
            self.assertEqual(self.reg("si"), want)

    def test_cell_adjustment(self):
        """CELL_SITE (795A2h, "push 2 / jmp 79618h"; DI the target, [BP+8] the user): AX 1d4 (GAME_DIE),
        back at 79617h's "push ax"; recorded (kind 14, 3) with whether ACID_ONCE (78DEFh, [BP+0Ah] the
        spell, DI the target) found the target Diseased (13) as the record's cure came."""
        heal = 0x79617 - 0x795A2
        mu = self.mu
        self.effects((40, 2, 97, 13, 1, 0, 0))
        once = bytes((0xCD, 0x98, gamepatch.ONCE_SITE, 0x90))
        for target, roll, cured in ((40, 3, 1), (41, 4, 0)):
            self.frame(p0A=151, m1E=0xF3)
            self.run_code(once, edi=target)
            mu.mem_write(GAME_DS * 16 + SEED, struct.pack("<I", seed_for(roll, 4)))
            self.frame(p8=2)
            self.assertEqual(self.run_site("cell_adjustment_heal", (heal,), edi=target, ebx=0x2222), heal)
            self.assertEqual((self.reg("ax"), self.reg("di"), self.reg("bx")), (roll, target, 0x2222))
            self.assertEqual(self.entry(), (14, 3, target, 2, roll, cured))

    def test_chill_touch_undead(self):
        """HOLD_HD (7A345h, the undead's test; SI the spell, DI the target): Chill Touch (3) on an undead
        is immune (7A1F0h: no damage, no STR lost) and Afraid (17) 1d4 rounds through 598:3Eh (target,
        the last caster CAST_SITE saw, 3, 17, rounds x 60, 0), recorded (kind 14, 1)."""
        p = patch("hold_undead_level")
        immune = (0x7A1F0 - 0x7A345) & 0xFFFF
        mu = self.mu
        self.stub(0x428F, 0x3E, 7)
        mu.mem_write(SS * 16 + BP + 6, struct.pack("<4H", 2, 40, 3, 5))
        self.run_code(bytes((0xCD, 0x98, gamepatch.CAST_SITE)))
        mu.mem_write(GAME_DS * 16 + SEED, struct.pack("<I", seed_for(3, 4)))
        self.at += 0x100
        start = CALLER * 16 + self.at
        mu.mem_write(start, p.replacement)
        mu.mem_write(CALLER * 16 + ((self.at + immune) & 0xFFFF), b"\xf4")
        for reg, value in dict(cs=CALLER, ds=GAME_DS, ss=SS, esp=0x800, ebp=BP, eflags=IF | 2, esi=3,
                               edi=40, eax=0x1234).items():
            mu.reg_write(getattr(r, "UC_X86_REG_" + reg.upper()), value)
        mu.emu_start(start, 0, count=50000)
        self.assertEqual((mu.reg_read(r.UC_X86_REG_IP) - self.at - 1) & 0xFFFF, immune)
        self.assertEqual([self.reg(x) for x in ("sp", "si", "di", "ax")], [0x800, 3, 40, 0x1234])
        self.assertEqual(self.called(7), (40, 2, 3, 17, 180, 0, 0))
        self.assertEqual(self.entry(), (14, 1, 40, 2, 3, 0))

    def test_heal_cures_feeblemind(self):
        """PROBE_CURE (79619h, "nop / push cs"; [BP+0Ah] DI pushed, the target) for Heal (202): with the
        spells as the manual has them its Feeblemind (19) entries taken out of the table, the handler's
        flags' 1 set ([BP-15h]: INT and WIS worked out again), recorded (kind 14, 5); without, kept."""
        mu = self.mu
        image = self.image
        at = td.install_at(image, 0xB1)  # (VEC_CURE: PROBE_CURE)
        self.assertGreater(at, 0)
        mu.mem_write(0xB1 * 4, struct.pack("<HH", struct.unpack_from("<H", image, at + 4)[0], TSR))
        for on, left in ((True, [(41, 2, 62, 19, 2, 0, 0)]), (False, None)):
            self.manual(on)
            entries = [(40, 2, 62, 19, 1, 0, 0), (41, 2, 62, 19, 2, 0, 0), (40, 2, 97, 13, 3, 0, 0)]
            self.effects(*entries)
            self.frame(p0E=202, p8=2, m15=0)
            self.at += 0x40
            start = CALLER * 16 + self.at
            mu.mem_write(start, bytes.fromhex("6a2857cdb1f4"))  # (push 28h (the healing) / push di / the INT)
            for reg, value in dict(cs=CALLER, ds=GAME_DS, ss=SS, esp=0x800, ebp=BP, eflags=IF | 2, edi=40).items():
                mu.reg_write(getattr(r, "UC_X86_REG_" + reg.upper()), value)
            mu.emu_start(start, 0, count=20000)
            self.assertEqual(mu.reg_read(r.UC_X86_REG_SP), 0x800 - 6)
            self.assertEqual(self.table(), [entries[1], entries[2]] if on else entries)
            self.assertEqual(mu.mem_read(SS * 16 + BP - 0x15, 1)[0] & 1, 1 if on else 0)


class LoaderTests(unittest.TestCase):
    """The Loader's side: the dice log's lines, the dice by class, the descriptions."""

    def test_manual_die(self):
        sheet = lambda *classes: bytes(0x21) + bytes(classes) + bytes(0x47 - 0x24)
        self.assertEqual(game.manual_die(23, sheet(9, 0, 0)), (8, "fighter"))
        self.assertEqual(game.manual_die(23, sheet(11, 17, 0)), (6, "thief"))
        self.assertEqual(game.manual_die(196, sheet(11, 17, 0)), (8, "thief"))
        self.assertEqual(game.manual_die(196, sheet(3, 0, 0)), (4, "cleric"))
        self.assertEqual(game.manual_die(23, sheet(0, 0, 0)), (6, ""))
        self.assertEqual(game.manual_die(148, sheet(9, 0, 0)), (6, ""))

    def test_texts(self):
        plain, manual = spelltexts.chunks(False), spelltexts.chunks(True)
        self.assertNotIn(("SPIN", 45), plain)
        self.assertIn(b"+2", manual[("SPIN", 45)])
        self.assertIn(b"1 to 8", manual[("SPIN", 197)])
        self.assertTrue(all(len(t) + 2 < 195 for t in spelltexts.MANUAL_TEXTS.values()))

    def test_effect_rules(self):
        self.assertIn("(at least 1)", game.effect_rule(4, True))
        self.assertNotIn("at least", game.effect_rule(4, False))
        self.assertIn("psionic", game.effect_rule(19, True))
        self.assertNotIn("psionic", game.effect_rule(19, False))


if __name__ == "__main__":
    unittest.main()
