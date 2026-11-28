"""DSCLOG2's kits in Wake of the Ravager (KIT_IS, KIT_LEVEL, MULTI_GROUP, SPEC_OF_SHEET's kit parts,
KIT_MELEE, EXPERT_HALVES, run in an emulated CPU), against Shattered Lands' rules (kitpages.kit_ids,
kit_level, sheet_group, specialize.skill, kits.melee, specialize.expert_attacks) on the transferred
party's sheets (ravtransfer.sheet: the kit byte at +3Dh, the specs at +42h..+44h) with ravlog's layout:
every class's kits, the multiclass groups' and a dual-classed human's, awake and asleep. And its tables
(KIT_SKILLS, the charms, the fire and cold spells, the Ravager's AC) against kits.py and the sequel's
spell records. Needs nasm and unicorn, else skipped; the spell records need the sequel (DSUN_WOTR)."""

import os
import shutil
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dsloader import game, kitpages, kits, ravager, ravlog, ravtransfer, specialize  # noqa: E402
import test_restrict  # noqa: E402

try:
    from unicorn import Uc, UC_ARCH_X86, UC_MODE_16
    from unicorn import x86_const as r
except ImportError:
    Uc = None

ASM = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dos", "dsclog2.asm")
TSR, SS, GDS = 0x1000, 0x4000, 0x6000
K = specialize.KINDS.index
RULES_HI = 270  # (the header's second rules word: RULE_KITS its bit 0)
TYPES_AT = 0x7000  # (the item types' table in the test's game segment)


def wotr_sheet(classes, levels, race, kit_byte, kinds=()) -> bytes:
    """A transferred sheet (the sequel's layout) of CLASSES at LEVELS, its kit byte KIT_BYTE (made in
    Shattered Lands' layout, put back for it while the sequel's is on)."""
    if ravlog._SAVED:
        ravlog.restore_layout()
        try:
            return wotr_sheet(classes, levels, race, kit_byte, kinds)
        finally:
            ravlog.apply_layout()
    sl = bytearray(test_restrict.sheet(*classes, race=race))
    sl[game.SHEET_LEVELS:game.SHEET_LEVELS + len(levels)] = bytes(levels)
    sl = bytearray(game.with_specs(bytes(sl) + bytes(ravtransfer.SL_SHEET - len(sl)), [k + 1 for k in kinds]))
    sl[0x43] = kit_byte  # (Shattered Lands' KIT_BYTE: the transfer carries it to +3Dh)
    return ravtransfer.sheet(bytes(sl), loader=True).ljust(ravager.SHEET_SIZE, b"\0")


def characters():
    """(classes, levels, race, kit byte): each class (1-17) alone with no kit and each of its three at
    levels 1, 6 and 12; each multiclass group's kits; dual-classed humans, the old class's kit asleep and
    awake, with and without a kit for the new class."""
    out = []
    for cls in range(1, 18):
        for kit in range(4):
            for level in (1, 6, 12):
                out.append(((cls,), (level,), 1 if cls < 9 or cls > 12 else 2, kit))
    for group, (race, classes) in kitpages.MULTI.items():
        sheet_classes = [next(c for c in range(1, 18) if kitpages.CREATION_CLASS.get(c) == k) for k in sorted(classes)]
        for kit in range(4):
            out.append((tuple(sheet_classes), (5,) * len(sheet_classes), race, kit))
    for old, new in ((9, 11), (17, 9), (13, 9), (11, 1)):
        for levels in ((3, 7), (8, 7)):
            for byte in (0x01, 0x04, 0x05, 0x06, 0x0B, 0x40 | 0x02, 0xFF):
                out.append(((new, old), levels, 1, byte))
    for classes in ((9, 11, 13), (1, 9, 17)):  # (a human with three classes: 0FFh is its kits, OWN_BIT and Friends)
        for byte in (0x3F, 0xFF):
            out.append((classes, (5, 5, 5), 1, byte))
    return out


@unittest.skipIf(Uc is None or not shutil.which("nasm"), "needs unicorn and nasm")
class KitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from test_dsclog_drawing import build
        exe, cls.sym = build(ASM)
        cls.image = exe[struct.unpack_from("<H", exe, 8)[0] * 16:]

    def setUp(self):
        self.mu = Uc(UC_ARCH_X86, UC_MODE_16)
        self.mu.mem_map(0, 0x100000)
        self.mu.mem_write(TSR * 16, self.image)
        self.mu.mem_write(TSR * 16 + 0xFFF0, bytes((0xF4,)))  # (hlt: where the routine returns)
        self.rules(game.RULE_KITS >> 16)
        ravlog.apply_layout()
        self.addCleanup(ravlog.restore_layout)
        old = game.RULES_IN_FORCE
        game.RULES_IN_FORCE = old | game.RULE_KITS | game.RULE_SPECIALIZE
        self.addCleanup(setattr, game, "RULES_IN_FORCE", old)

    def rules(self, hi: int) -> None:
        self.mu.mem_write(TSR * 16 + self.sym["hdr"] + RULES_HI, struct.pack("<H", hi))

    def run_routine(self, name: str, sheet: bytes, **regs) -> dict:
        self.mu.mem_write(SS * 16 + 0x500, sheet)
        self.mu.mem_write(SS * 16 + 0x7FC, struct.pack("<H", 0xFFF0))
        for reg, value in dict(dict(cs=TSR, ds=GDS, es=SS, ebx=0x500, ss=SS, esp=0x7FC, eflags=0x2), **regs).items():
            self.mu.reg_write(getattr(r, "UC_X86_REG_" + reg.upper()), value)
        self.mu.emu_start(TSR * 16 + self.sym[name], TSR * 16 + 0xFFF0)
        return {reg: self.mu.reg_read(getattr(r, "UC_X86_REG_" + reg.upper()))
                for reg in ("eax", "edx", "esi", "ebx", "eflags")}

    def test_kit_is(self):
        """KIT_IS's ZF is kitpages.kit_ids (awake), KIT_HAS's kitpages.kits_of (asleep too), KIT_LEVEL after
        it kitpages.kit_level, MULTI_GROUP's AL kitpages.sheet_group, for every kit on every sheet; none
        with the rule off."""
        seen = set()
        for classes, levels, race, byte in characters():
            sheet = wotr_sheet(classes, levels, race, byte)
            self.assertEqual(sheet[0x3D], byte)
            awake, held = kitpages.kit_ids(sheet), [k for k, _, _ in kitpages.kits_of(sheet)]
            group = self.run_routine("multi_group", sheet, eax=0xFF)["eax"] & 0xFF
            self.assertEqual(group, kitpages.sheet_group(sheet), (classes, race))
            for kid in sorted(set(kitpages.KIT_IDS.values())):
                with self.subTest(classes=classes, levels=levels, race=race, byte=byte, kit=kid):
                    got = self.run_routine("kit_is", sheet, eax=kid)
                    self.assertEqual(bool(got["eflags"] & 0x40), kid in awake)
                    self.assertEqual(got["eax"] & 0xFF, kid)
                    if kid in awake:
                        level = self.run_routine("kit_level", sheet)["eax"] & 0xFF
                        self.assertEqual(level, kitpages.kit_level(sheet, kid))
                        seen.add(kid)
                    self.assertEqual(bool(self.run_routine("kit_has", sheet, eax=kid)["eflags"] & 0x40), kid in held)
        self.assertEqual(seen, set(kitpages.KIT_IDS.values()))
        self.rules(0)
        sheet = wotr_sheet((9,), (5,), 2, 3)
        self.assertEqual(kitpages.kit_ids(sheet), [kits.RAVAGER])
        self.assertFalse(self.run_routine("kit_is", sheet, eax=kits.RAVAGER)["eflags"] & 0x40)

    def test_skill(self):
        """SPEC_OF_SHEET's DL is specialize.skill with the kits for every warrior and expertise kit (and a
        plain warrior's for a control), every weapon type: a Battle Mage's, Crusader's, Mind Warrior's
        expertise, a Justifier's specialization, a Myrmidon's second kind on to mastery, a Seeker's bow."""
        cases = [((9,), (9,), 2, 0), ((9,), (9,), 2, 1), ((9,), (5,), 2, 1), ((13,), (8,), 1, 2),
                 ((13,), (8,), 1, 3), ((13,), (8,), 1, 0), ((11,), (7,), 1, 2), ((11,), (5,), 1, 2),
                 ((1,), (7,), 1, 3), ((12,), (8,), 1, 2), ((17, 11), (8, 3), 1, 0x08), ((17, 11), (2, 3), 1, 0x08)]
        specs = ([K("long sword"), K("polearm")], [K("bow"), K("dagger")], [K("mace")])
        seen = set()
        for classes, levels, race, byte in cases:
            for kinds in specs:
                sheet = wotr_sheet(classes, levels, race, byte, kinds)
                for t in range(ravager.GAME_TYPES + ravager.MOD_TYPES):
                    want = specialize.skill(sheet, t)
                    got = self.run_routine("spec_of_sheet", sheet, esi=t, edx=0xFF)["edx"] & 0xFF
                    with self.subTest(classes=classes, levels=levels, kit=byte, kinds=kinds, type=t):
                        self.assertEqual(got, want)
                    seen.add((kitpages.kit_ids(sheet)[0] if kitpages.kit_ids(sheet) else 0, want))
        for kit_skill in ((kits.MYRMIDON, specialize.GRAND), (kits.JUSTIFIER, specialize.SPECIAL),
                          (kits.BATTLE_MAGE, specialize.EXPERT), (kitpages.KIT_IDS["Crusader"], specialize.EXPERT),
                          (kits.MIND_WARRIOR, specialize.EXPERT), (kits.SEEKER, specialize.PLAIN)):
            self.assertIn(kit_skill, seen)

    def test_expert_halves(self):
        """EXPERT_HALVES (after KIT_IS found the kit) is specialize.expert_attacks: 3/2 a round, 2 from the
        kit's class's 7th level; a warrior's halves and other skills kept."""
        for level in (1, 6, 7, 12):
            sheet = wotr_sheet((11,), (level,), 1, 2)  # (a Battle Mage)
            self.run_routine("kit_is", sheet, eax=kits.BATTLE_MAGE)
            for skill in (specialize.PLAIN, specialize.EXPERT, specialize.SPECIAL):
                for halves in (2, 3):
                    got = self.run_routine("expert_halves", sheet, eax=halves, edx=skill)["eax"] & 0xFFFF
                    want = (4 if level >= 7 else 3) if skill == specialize.EXPERT and halves <= 2 else halves
                    self.assertEqual(got, want, (level, skill, halves))

    def test_ranger_drop(self):
        """RANGER_DROP's CL is kits.ranger_cast_drop's: a Seeker's 5, a Justifier's 9 with the kits, else 7
        with the rangers' casting level rule (0 without), for a ranger's class at each place of its sheet."""
        self.mu.mem_write(GDS * 16 + 0x19C5, struct.pack("<HH", 0x500, SS))
        for byte, kits_on, want in ((0, 1, 7), (1, 1, 7), (2, 1, 9), (3, 1, 5), (3, 0, 7)):
            sheet = wotr_sheet((13,), (8,), 1, byte)
            self.rules(kits_on | 2)  # (RULE_HI_RANGER on)
            got = self.run_routine("ranger_drop", sheet, ecx=0xFF)["edx"]
            cl = self.mu.reg_read(r.UC_X86_REG_ECX) & 0xFF
            self.assertEqual(cl, want, (byte, kits_on))
            if kits_on:
                drop = max((kits.ranger_cast_drop(k) for k in kitpages.kit_ids(sheet)), default=7)
                self.assertEqual(cl, drop)
        self.rules(1)
        self.assertEqual(self.run_routine("ranger_drop", wotr_sheet((13,), (8,), 1, 0)) and
                         self.mu.reg_read(r.UC_X86_REG_ECX) & 0xFF, 0)

    def test_melee(self):
        """KIT_MELEE's AX is kits.melee summed over the sheet's kits, for every weapon type (the sequel's
        types' missile flag, +0, and two-handed bit, +0Bh 40h; none for a missile weapon)."""
        types = bytearray(15 * (ravager.GAME_TYPES + ravager.MOD_TYPES))
        for t in range(ravager.GAME_TYPES + ravager.MOD_TYPES):
            types[t * 15] = 2 if t % 7 == 0 else 0
            types[t * 15 + 0x0B] = 0x40 if t % 3 == 0 else 0
        self.mu.mem_write(GDS * 16 + TYPES_AT, bytes(types))
        self.mu.mem_write(GDS * 16 + 0x19CD, struct.pack("<HH", TYPES_AT, GDS))
        kinds = specialize.KIND_OF_TYPE
        for classes, byte in (((9,), 3), ((10,), 3), ((9, 17), 1), ((9,), 0), ((9, 17), 2)):
            race = 7 if len(classes) > 1 else 2  # (a dwarf fighter/thief: the Ghetto Fighter, Wayfinder)
            sheet = wotr_sheet(classes, (5,) * len(classes), race, byte)
            ids = kitpages.kit_ids(sheet)
            for t in range(ravager.GAME_TYPES + ravager.MOD_TYPES):
                missile, two = types[t * 15] & 2, types[t * 15 + 0x0B] & 0x40
                want = 0 if missile else sum(kits.melee(k, bool(two), kinds.get(t)) for k in ids)
                got = self.run_routine("kit_melee", sheet, esi=t)["eax"] & 0xFFFF
                self.assertEqual(got, want, (classes, byte, ids, t))

    def test_tables(self):
        """KIT_SKILLS is kits.SKILLS (the Swashbuckler's none: its bad luck), SCOUT_SKILLS kits.SCOUT_SKILLS,
        RAVAGER_AC kits.RAVAGER_AC, the charms kits.CHARMS in ravlog's layout."""
        at, got = self.sym["kit_skills"], {}
        while self.image[at]:
            got[self.image[at]] = tuple(struct.unpack_from("8b", self.image, at + 1))
            at += 9
        self.assertEqual(got, {k: v for k, v in kits.SKILLS.items() if any(v)})
        self.assertEqual(struct.unpack_from("<H", self.image, self.sym["scout_bits"])[0],
                         sum(1 << s for s in kits.SCOUT_SKILLS))
        at = self.sym["ravager_ac"]
        self.assertEqual(tuple(self.image[at:at + len(kits.RAVAGER_AC)]), kits.RAVAGER_AC)
        self.assertEqual(self.words("kit_charms"), list(kits.CHARMS))  # (ravlog.RAV_CHARMS)

    def words(self, name):
        at, out = self.sym[name], []
        while struct.unpack_from("<h", self.image, at)[0] != -1:
            out.append(struct.unpack_from("<H", self.image, at)[0])
            at += 2
        return out

    @unittest.skipUnless(ravager.is_wotr_dir(os.environ.get("DSUN_WOTR")), "needs the sequel (DSUN_WOTR)")
    def test_wanderer_spells(self):
        """WANDER_SPELLS are the sequel's spells whose records' +1Ah have fire or cold (2 or 4), as
        kits.save reads the record; the charms are named so in the sequel."""
        path = os.path.join(os.environ["DSUN_WOTR"], "RESOURCE.GFF")
        table, names = ravlog.spell_table(open(path, "rb").read())
        want = [s for s in range(len(names)) if struct.unpack_from("<H", table, s * 32 + 0x1A)[0] & (kits.FIRE | kits.COLD)]
        self.assertEqual(self.words("wander_spells"), want)
        self.assertTrue(all("Charm" in names[s] or "Domin" in names[s] for s in kits.CHARMS))


    OWN = [((9, 7), (6, 6), 8), ((9, 7), (6, 9), 8), ((9, 7, 12), (6, 6, 6), 8), ((11, 12, 17), (6, 6, 7), 3),
           ((11, 6, 17), (5, 5, 5), 3), ((2,), (7,), 1), ((2,), (14,), 1), ((10,), (7,), 5), ((9,), (5,), 1)]

    def test_kit_open(self):
        """0FFh is KIT_OPEN on every sheet but a human's with three classes, where it is a legal byte (kits
        3/3/3, OWN_BIT and Friends): game.kit_open and the helper's KIT_OPEN_AT agree on both."""
        for classes, levels, race, want in (((9,), (5,), 1, True), ((9, 11), (3, 7), 1, True), ((9, 11, 13), (5, 5, 5), 2, True),
                                            ((9, 11, 13), (5, 5, 5), 1, False), ((1, 9, 17), (5, 5, 5), 1, False)):
            sheet = wotr_sheet(classes, levels, race, 0xFF)
            with self.subTest(classes=classes, race=race):
                self.assertEqual(game.kit_open(sheet), want)
                got = self.run_routine("kit_open_at", sheet)
                self.assertEqual(bool(got["eflags"] & 0x40), want)
                self.assertEqual(kitpages.kit_ids(sheet) == [], want)
            if want:
                self.assertFalse(game.kit_open(wotr_sheet(classes, levels, race, 0x3F)))

    def test_own_party(self):
        """The sequel's own party's features (kits.own_features): OWN_DRUID's AL is kits.own_warden_level
        (Thy'rokh's druid level, not K'ratchek's), OWN_LIGHT sets AW_HEAVY as kits.own_light_cast (Ar'Anda,
        not Cilla); none without OWN_BIT, with KIT_OPEN or with the kits' rule off."""
        heavy = self.sym["aw_heavy"]
        for rules in (game.RULE_KITS >> 16, 0):
            self.rules(rules)
            for classes, levels, race in self.OWN:
                for byte in (0x40, 0x00, 0xFF, 0x41):
                    sheet = wotr_sheet(classes, levels, race, byte)
                    own = rules and byte != 0xFF and byte & 0x40
                    with self.subTest(classes=classes, race=race, byte=byte, rules=rules):
                        got = self.run_routine("own_druid", sheet, eax=0x1234)["eax"] & 0xFF
                        self.assertEqual(got, kits.own_warden_level(sheet) if own else 0)
                        self.mu.mem_write(TSR * 16 + heavy, b"\0")
                        self.run_routine("own_light", sheet)
                        self.assertEqual(self.mu.mem_read(TSR * 16 + heavy, 1)[0], int(bool(own) and kits.own_light_cast(sheet)))
        sheet = wotr_sheet((9, 7), (6, 9), 8, 0x40)
        self.assertEqual((kits.own_warden_level(sheet), kits.own_features(sheet)), (9, kits.OWN_WARDEN))
        self.assertEqual(kits.own_features(wotr_sheet((9, 7, 12), (6, 6, 6), 8, 0x40)), kits.OWN_FEATURES[kits.THRI_KREEN])
        self.assertEqual(kits.own_features(wotr_sheet((11, 6, 17), (5, 5, 5), 3, 0x40)), ("Elven Shadow-walker",))

    def frame(self, cls: int, spell: int) -> None:
        """A frame for SLOT_BEHIND and BEHIND_LEAST at SS:600h: [BP+8] the class, [BP+0Ch] the spell level."""
        self.mu.mem_write(SS * 16 + 0x608, struct.pack("<HHH", cls, 0, spell))

    def test_slot_behind(self):
        """SLOT_BEHIND (ADND_SLOTS's: the sheet + DI in ES:BX) makes CL one less for an Elementalist's cleric
        class (kits.slot_level), SB_BEHIND set, and sets SB_FEWER for a Crusader's priest class; BEHIND_LEAST
        then takes one slot off with SB_FEWER, and with SB_BEHIND puts the level back and makes no slots 1
        where the class's own level reaches the spell level (kits.slots). Terrannus (OWN_BIT, a human) is a
        plain Crusader: one fewer, not a level behind."""
        cases = [((2,), 0x40, 1), ((2,), 0x43, 1), ((2,), 0x00, 1), ((3,), 0x01, 1), ((3,), 0x03, 1), ((1, 9), 0x04, 1),
                 ((9, 1), 0x01, 1), ((9, 1), 0x0C, 1), ((11,), 0x40, 1), ((17, 9), 0x40, 1), ((2,), 0xFF, 1),
                 ((11,), 0x02, 1), ((11, 9), 0x02, 1), ((9, 11), 0x08, 1)]
        for rules in (game.RULE_KITS >> 16, 0):
            self.rules(rules)
            for classes, byte, race in cases:
                for level in (1, 2, 7, 13, 14):
                    for place in range(len(classes)):
                        levels = (level,) + (3,) * (len(classes) - 1)
                        sheet = wotr_sheet(classes, levels, race, byte)
                        cls = sheet[0x1B + place]
                        kid = kits.ELEMENTALIST if kits.ELEMENTALIST in kitpages.kit_ids(sheet) \
                            and kitpages.kit_place_of(sheet, kits.ELEMENTALIST) == place else None
                        behind = bool(rules) and 1 <= cls <= 4 and kid is not None
                        fewer = bool(rules) and (1 <= cls <= 8 and kits.CRUSADER in kitpages.kit_ids(sheet)
                                                 or cls == 11 and kits.BATTLE_MAGE in kitpages.kit_ids(sheet))
                        self.frame(cls, 1)
                        got = self.run_routine("slot_behind", sheet, ecx=0x1100 | levels[place], ebp=0x600,
                                               edi=place, ebx=0x500 + place)
                        want = kits.slot_level(kits.ELEMENTALIST if behind else 0, levels[place])
                        with self.subTest(classes=classes, byte=byte, level=level, place=place, rules=rules):
                            self.assertEqual(self.mu.mem_read(TSR * 16 + self.sym["sb_behind"], 1)[0], int(behind))
                            self.assertEqual(self.mu.mem_read(TSR * 16 + self.sym["sb_fewer"], 1)[0], int(fewer))
                            self.assertEqual(self.mu.reg_read(r.UC_X86_REG_CX), 0x1100 | want)
                            self.assertEqual(got["ebx"] & 0xFFFF, 0x500 + place)
        for adnd in (True, False):  # (RULE_HI_TABLES, 8, on and off)
            self.rules(game.RULE_KITS >> 16 | (8 if adnd else 0))
            for level in range(1, 20):
                for spell in range(1, 8):
                    for given in (0, 1, 3):
                        self.frame(2, spell)
                        self.mu.mem_write(SS * 16 + 0x700, bytes((max(0, level - 1), 17)))
                        self.mu.mem_write(TSR * 16 + self.sym["sb_behind"], b"\1\0")
                        self.mu.mem_write(TSR * 16 + self.sym["sb_level"], bytes((level,)))
                        got = self.run_routine("behind_least", bytes(8), eax=given, esi=0x700, ebp=0x600)["eax"] & 0xFFFF
                        with self.subTest(level=level, spell=spell, given=given, adnd=adnd):
                            self.assertEqual(got, kits.slots(kits.ELEMENTALIST, kits.PRIEST, level, spell, given, adnd))
                            self.assertEqual(self.mu.mem_read(SS * 16 + 0x700, 1)[0], level)
        self.mu.mem_write(TSR * 16 + self.sym["sb_behind"], b"\0\1")  # (a Crusader's: one fewer, 0 kept)
        for given in range(5):
            self.frame(2, 1)
            got = self.run_routine("behind_least", bytes(8), eax=given, esi=0x700, ebp=0x600)["eax"] & 0xFFFF
            self.assertEqual(got, kits.slots(kits.CRUSADER, kits.PRIEST, 7, 1, given))
        self.assertEqual(kitpages.kit_ids(wotr_sheet((2,), (7,), 1, 0x43)), [kits.CRUSADER])  # (Terrannus's byte)

    def test_kit_table(self):
        """SLOT_BEHIND sets SB_TABLE for a Seeker's or Justifier's own ranger class and a Shinobi's own
        thief class, awake, the kits' rule on (and for no other class or sheet); KIT_TABLE then gives
        kits.slots's own tables for the class's level CL at every spell level, whatever the game gave, and
        keeps AX with no table. A Justifier of 8th or 9th ranger level has none (the ranger's first slot
        would cast at level 0: the caster level routine's "sub dx,9"). A Battle Mage's wizard slots are 1
        fewer through BEHIND_LEAST (kits.slots), its other classes' kept."""
        tables = {kits.SEEKER: 1, kits.JUSTIFIER: 2, kits.SHINOBI: 3}
        cases = [((13,), 3), ((14,), 2), ((15,), 1), ((16,), 0), ((17,), 3), ((17,), 2), ((11,), 2), ((1,), 3),
                 ((13, 9), 0x0C), ((9, 13), 0x03), ((9, 17), 0x03), ((17, 9), 0x0C), ((13,), 0xFF), ((13,), 0x43)]
        seen = set()
        for rules in (game.RULE_KITS >> 16, 0):
            self.rules(rules)
            for classes, byte in cases:
                for level in (1, 5, 6, 8, 9, 10, 13, 14, 15, 16, 20, 30):
                    for place in range(len(classes)):
                        levels = tuple(level if p == place else 4 for p in range(len(classes)))
                        sheet = wotr_sheet(classes, levels, 1, byte)
                        cls = sheet[0x1B + place]
                        kid = next((k for k in tables if k in kitpages.kit_ids(sheet)
                                    and kitpages.kit_place_of(sheet, k) == place), None)
                        if not rules or kid == kits.SHINOBI and cls != 17 or kid in (kits.SEEKER, kits.JUSTIFIER) and not 13 <= cls <= 16:
                            kid = None
                        self.frame(cls, 1)
                        self.run_routine("slot_behind", sheet, ecx=0x1100 | level, ebp=0x600, edi=place, ebx=0x500 + place)
                        with self.subTest(classes=classes, byte=byte, level=level, place=place, rules=rules):
                            self.assertEqual(self.mu.mem_read(TSR * 16 + self.sym["sb_table"], 1)[0], tables.get(kid, 0))
                        magic = kits.WIZARD if cls in (11, 17) else kits.PRIEST
                        for spell in range(1, 10):
                            for given in (0, 1, 4):
                                self.frame(cls, spell)
                                got = self.run_routine("kit_table", bytes(8), eax=given, ecx=0x1100 | level, ebp=0x600)
                                want = kits.slots(kid, magic, level, spell, given) if kid else given
                                with self.subTest(classes=classes, byte=byte, level=level, spell=spell, given=given):
                                    self.assertEqual(got["eax"] & 0xFFFF, want)
                                    self.assertEqual(self.mu.reg_read(r.UC_X86_REG_CX), 0x1100 | level)
                                if kid and want:
                                    seen.add(kid)
        self.assertEqual(seen, set(tables))
        self.assertEqual([kits.slots(kits.JUSTIFIER, kits.PRIEST, lv, 1, 1) for lv in (8, 9, 10)], [0, 0, 1])
        self.mu.mem_write(TSR * 16 + self.sym["sb_behind"], b"\0\1")  # (a Battle Mage's: one fewer, 0 kept)
        for given in range(5):
            self.frame(11, 1)
            got = self.run_routine("behind_least", bytes(8), eax=given, esi=0x700, ebp=0x600)["eax"] & 0xFFFF
            self.assertEqual(got, kits.slots(kits.BATTLE_MAGE, kits.WIZARD, 7, 1, given))

    # ---- PSP costs and PSP, hit dice, casting after a hit (sites 191-199) ----
    CREATURES, SHEETS, POWERS = 0x8000, 0x1000, 0x3000  # (the game's creature records, sheets, powers' table)

    def party(self, sheets) -> None:
        """Creatures 0..N-1 (DS:19C9h, 31h bytes each, +4 the sheet) on SHEETS (DS:19C5h, 48h each), each
        combatant N its creature N (the combatants' records, FIGHTERS_OFF + 1)."""
        self.mu.mem_write(GDS * 16 + 0x19C5, struct.pack("<HH", self.SHEETS, SS))
        self.mu.mem_write(GDS * 16 + 0x19C9, struct.pack("<HH", self.CREATURES, GDS))
        fighters = (GDS - 0x897) * 16 + 0x0C33
        for n, sheet in enumerate(sheets):
            self.mu.mem_write(SS * 16 + self.SHEETS + n * ravager.SHEET_SIZE, sheet)
            self.mu.mem_write(GDS * 16 + self.CREATURES + n * 0x31 + 4, struct.pack("<H", n))
            self.mu.mem_write(fighters + n * 3, struct.pack("<BH", 2, n))

    def run_int(self, name: str, **regs) -> dict:
        """Site routine NAME as the INT runs it (IP, CS, FLAGS on the stack), the game's BP at SS:600h."""
        self.mu.mem_write(SS * 16 + 0x7F8, struct.pack("<HHH", 0xFFF0, TSR, 0x2))
        for reg, value in dict(dict(cs=TSR, ds=GDS, ss=SS, esp=0x7F8, ebp=0x600, eflags=0x2), **regs).items():
            self.mu.reg_write(getattr(r, "UC_X86_REG_" + reg.upper()), value)
        self.mu.emu_start(TSR * 16 + self.sym[name], TSR * 16 + 0xFFF0)
        return {reg: self.mu.reg_read(getattr(r, "UC_X86_REG_" + reg.upper()))
                for reg in ("eax", "edx", "esi", "edi", "ebx", "ecx", "esp")}

    PSI = [((12,), 1, 1, kits.MIND_BENDER), ((12,), 1, 3, kits.KINETICIST), ((12,), 1, 2, kits.MIND_WARRIOR),
           ((9, 12), 5, 1, kits.TITAN_MIND), ((7, 9, 12), 8, 1, kits.WASTE_SEER), ((12,), 1, 0, None),
           ((7, 9, 12), 8, 0x40, "own"), ((9, 7), 8, 0x40, None), ((12,), 1, 0xFF, None)]

    def test_psp_cost(self):
        """PSP_TABLE's AL (the powers' table, 3 bytes a power, BX the power x 3), PSP_KEEP's and PSP_KEEP_DX's
        (63h none kept), PSP_USE's DI (no less than 0) and PSP_DEFENCE's cost (telepathy) are kits.psp_cost
        for each psionicist kit, every power and cost, the party member under the open sky or a roof
        (KIT_OUTDOORS) or a foe; a thri-kreen of the games' own party with a psionicist class is a
        Wasteland Seer (SL's K'ratchek); none with the kits' rule off."""
        outdoors = self.sym["kit_outdoors"]
        seen = set()
        for rules in (game.RULE_KITS >> 16, 0):
            self.rules(rules)
            for classes, race, byte, kid in self.PSI:
                sheet = wotr_sheet(classes, (6,) * len(classes), race, byte)
                for member, sky in ((0, True), (2, False), (5, None)):
                    self.party([sheet if n == member else wotr_sheet((9,), (3,), 1, 0) for n in range(6)])
                    self.mu.mem_write(TSR * 16 + outdoors, bytes((1 << member if sky else 0,)))
                    want_kid = None if not rules else kits.WASTE_SEER if kid == "own" else kid
                    if want_kid == kits.WASTE_SEER and sky is None:
                        want_kid = None
                    for power in range(34):
                        for cost in (0, 1, 2, 3, 7, 0x63):
                            self.mu.mem_write(self.POWERS * 16 + 0x7E0 + power * 3, bytes((0, cost, cost)))
                            want = kits.psp_cost(want_kid, power, cost, sky) if want_kid else cost
                            with self.subTest(classes=classes, byte=byte, member=member, power=power, cost=cost, rules=rules):
                                got = self.run_int("psp_table", es=self.POWERS, ebx=power * 3, esi=member, eax=0xAB00)
                                self.assertEqual(got["eax"] & 0xFFFF, 0xAB00 | want)
                                self.assertEqual(got["ebx"] & 0xFFFF, power * 3)
                                keep = cost if cost == 0x63 else want
                                self.assertEqual(self.run_int("psp_keep", es=self.POWERS, ebx=power * 3, esi=member)["eax"] & 0xFF, keep)
                                self.assertEqual(self.run_int("psp_keep_dx", es=self.POWERS, ebx=power * 3, edx=member, esi=9)["eax"] & 0xFF, keep)
                                self.mu.mem_write(SS * 16 + 0x60A, struct.pack("<H", power))
                                got = self.run_int("psp_use", edi=cost, esi=member)
                                self.assertEqual(got["edi"] & 0xFFFF, want)
                            if want != cost:
                                seen.add(want_kid)
                    for cost in (0, 1, 3, 9):  # (a defence: creature [BP-6] pays AX, telepathy's cost)
                        self.mu.mem_write(SS * 16 + 0x5FA, struct.pack("<H", member))
                        self.mu.mem_write(self.POWERS * 16 + 2, struct.pack("<H", 50))
                        self.run_int("psp_defence", es=self.POWERS, ebx=0, eax=cost)
                        left = struct.unpack("<H", self.mu.mem_read(self.POWERS * 16 + 2, 2))[0]
                        want = kits.psp_cost(want_kid, kits.TP_FIRST, cost, sky) if want_kid else cost
                        self.assertEqual(left, 50 - want, (classes, byte, member, cost, rules))
        self.assertEqual(seen, {kits.MIND_BENDER, kits.KINETICIST, kits.TITAN_MIND, kits.WASTE_SEER})

    def test_max_psp(self):
        """KIT_MAX_PSP's SI (the level up's most PSP) is kits.max_psp: a Mind Warrior's a fifth fewer, asleep
        too (a human turned fighter); ES:BX the sheet ([BP-8]) as the game's LES; none with the rule off."""
        cases = [((12,), (6,), 2), ((12,), (6,), 1), ((9, 12), (3, 7), 0x02), ((9, 12), (8, 7), 0x02), ((12,), (6,), 0)]
        for rules in (game.RULE_KITS >> 16, 0):
            self.rules(rules)
            for classes, levels, byte in cases:
                sheet = wotr_sheet(classes, levels, 1, byte)
                self.mu.mem_write(SS * 16 + 0x5F8, struct.pack("<HH", 0x500, SS))
                self.mu.mem_write(SS * 16 + 0x500, sheet)
                kid = kits.MIND_WARRIOR if rules and kits.MIND_WARRIOR in [k for k, _, _ in kitpages.kits_of(sheet)] else None
                for psp in (0, 4, 5, 23, 61, 120):
                    got = self.run_int("kit_max_psp", esi=psp, es=0, ebx=0)
                    with self.subTest(classes=classes, levels=levels, byte=byte, psp=psp, rules=rules):
                        self.assertEqual(got["esi"] & 0xFFFF, kits.max_psp(kid, psp))
                        self.assertEqual((got["ebx"] & 0xFFFF, self.mu.reg_read(r.UC_X86_REG_ES)), (0x500, SS))
        self.assertEqual(kits.max_psp(kits.MIND_WARRIOR, 61), 49)

    def test_hit_dice(self):
        """KIT_HIT_DIE's AL (the class's group's die, ES:BX's +0) is kits.hit_die and KIT_HIT_GAIN's (+2, the
        gain past the dice) kits.hit_gain for the class levelled ([BP+8]) when it is the kit's own, awake: a
        Battle Mage's d6 and 2, an Arcanist's d3 and 1, a preserver's d4 and 1; a human Battle Mage turned
        fighter rolls the fighter's; none with the rule off."""
        cases = [((11,), 2, 11), ((11,), 3, 11), ((11,), 1, 11), ((11,), 0, 11), ((9, 11), 0x08, 11),
                 ((9, 11), 0x08, 9), ((11, 9), 0x02, 11), ((11, 9), 0x02, 9), ((11,), 0xFF, 11)]
        groups = {9: (10, 9, 3), 11: (4, 10, 1)}
        seen = set()
        for rules in (game.RULE_KITS >> 16, 0):
            self.rules(rules)
            for classes, byte, cls in cases:
                for levels in ((5,) * len(classes), (12, 3)[:len(classes)], (3, 12)[:len(classes)]):
                    sheet = wotr_sheet(classes, levels, 1, byte)
                    self.mu.mem_write(SS * 16 + 0x500, sheet)
                    self.mu.mem_write(SS * 16 + 0x5FC, struct.pack("<HH", 0x500, SS))
                    self.mu.mem_write(SS * 16 + 0x608, struct.pack("<H", cls))
                    self.mu.mem_write(self.POWERS * 16 + 0x40, bytes(groups[cls]))
                    awake = kitpages.kit_ids(sheet)
                    kid = next((k for k in (kits.BATTLE_MAGE, kits.ARCANIST) if k in awake
                                and sheet[0x1B + kitpages.kit_place_of(sheet, k)] == cls), None) if rules else None
                    die = self.run_int("kit_hit_die", es=self.POWERS, ebx=0x40, eax=0x1200)
                    gain = self.run_int("kit_hit_gain", es=self.POWERS, ebx=0x40, eax=0x1200, ecx=0x5678)
                    with self.subTest(classes=classes, byte=byte, cls=cls, levels=levels, rules=rules):
                        self.assertEqual(die["eax"] & 0xFFFF, 0x1200 | kits.hit_die(kid, groups[cls][0]))
                        self.assertEqual(gain["eax"] & 0xFFFF, 0x1200 | kits.hit_gain(kid, groups[cls][2]))
                        self.assertEqual((gain["ecx"] & 0xFFFF, gain["ebx"] & 0xFFFF, gain["esp"]), (0x5678, 0x40, 0x7FE))
                    seen.add(kid)
        self.assertEqual(seen, {kits.BATTLE_MAGE, kits.ARCANIST, None})
        self.assertEqual([kits.hit_die(k, 4) for k in (kits.BATTLE_MAGE, kits.ARCANIST, None)], [6, 3, 4])
        self.assertEqual([kits.hit_gain(k, 1) for k in (kits.BATTLE_MAGE, kits.ARCANIST, None)], [2, 1, 1])

    def test_scholar_thac0(self):
        """SCHOLAR_THAC0's AX (the THAC0 routine's end: 20 less SI, the best class group's cut, of sheet [BP+6])
        is kits.thac0's: a Scholar's 1 worse, awake, the kits' rule on; every other sheet's 20 less SI."""
        seen = 0
        for rules in (game.RULE_KITS >> 16, 0):
            self.rules(rules)
            for classes, levels, race, byte in characters():
                sheet = wotr_sheet(classes, levels, race, byte)
                kid = kits.SCHOLAR if rules and kits.SCHOLAR in kitpages.kit_ids(sheet) else None
                self.party([wotr_sheet((9,), (3,), 1, 0), sheet])
                self.mu.mem_write(SS * 16 + 0x606, struct.pack("<H", 1))
                for cut, who in ((0, 0), (4, 1), (11, 1)):
                    flag = TSR * 16 + self.sym["cr_thac0_scholar"]
                    self.mu.mem_write(flag, bytes((7,)))
                    self.mu.mem_write((GDS + 0x3E71 - 0x47E0) * 16 + 0xB44, struct.pack("<H", who))
                    with self.subTest(classes=classes, byte=byte, rules=rules, cut=cut):
                        got = self.run_int("scholar_thac0", esi=cut, eax=0xBEEF, edx=0x1234)
                        self.assertEqual(got["eax"] & 0xFFFF, kits.thac0(kid, levels[0], 20 - cut))
                        self.assertEqual(got["esi"] & 0xFFFF, cut)
                        self.assertEqual(got["edx"] & 0xFFFF, 0x1234)
                        self.assertEqual(got["esp"] & 0xFFFF, 0x7FE)
                        self.assertEqual(self.mu.mem_read(flag, 1)[0], (kid == kits.SCHOLAR) if who == 1 else 7)
                    seen += kid == kits.SCHOLAR
        self.assertTrue(seen)

    def test_scholar_made(self):
        """CR_SCHOLAR (the creation's spells, CR_SPELLS): a new member SI with the Scholar kit awake (the rule on)
        has one more 1st-level pick for each of its preserver levels (kitpages.kit_level), in CR_DUE's first
        byte and CR_LEFT; anyone else none. Registers kept."""
        due, left = TSR * 16 + self.sym["cr_due"], TSR * 16 + self.sym["cr_left"]
        seen = 0
        for rules in (game.RULE_KITS >> 16, 0):
            self.rules(rules)
            for classes, levels, race, byte in characters():
                sheet = wotr_sheet(classes, levels, race, byte)
                self.party([wotr_sheet((9,), (3,), 1, 0), sheet])
                self.mu.mem_write(due, bytes((2, 0)))
                self.mu.mem_write(left, struct.pack("<H", 2))
                got = self.run_routine("cr_scholar", b"", esi=1, eax=0x1357, ebx=0x2468)
                awake = bool(rules) and kits.SCHOLAR in kitpages.kit_ids(sheet)
                more = kitpages.kit_level(sheet, kits.SCHOLAR) if awake else 0
                with self.subTest(classes=classes, levels=levels, byte=byte, rules=rules):
                    self.assertEqual(self.mu.mem_read(due, 2)[0], 2 + more)
                    self.assertEqual(struct.unpack("<H", self.mu.mem_read(left, 2))[0], 2 + more)
                    self.assertEqual((got["eax"] & 0xFFFF, got["ebx"] & 0xFFFF, got["esi"] & 0xFFFF), (0x1357, 0x2468, 1))
                seen += bool(more)
        self.assertTrue(seen)

    def test_hit_round(self):
        """HIT_ROUND marks creature SI hit this round (ES:SI+0B2h 1, the game's) unless it is a Battle Mage,
        awake, the kits' rule on."""
        cases = [((11,), 2), ((11,), 1), ((11,), 3), ((9, 11), 0x08), ((9, 11), 0x02), ((9,), 0)]
        for rules in (game.RULE_KITS >> 16, 0):
            self.rules(rules)
            for classes, byte in cases:
                sheet = wotr_sheet(classes, (5, 7)[:len(classes)] if len(classes) > 1 else (5,), 1, byte)
                self.party([wotr_sheet((9,), (3,), 1, 0), sheet])
                self.mu.mem_write(self.POWERS * 16 + 0xB0, bytes(8))
                self.run_int("hit_round", es=self.POWERS, esi=1, eax=0x4321)
                bm = bool(rules) and kits.BATTLE_MAGE in kitpages.kit_ids(sheet)
                with self.subTest(classes=classes, byte=byte, rules=rules):
                    self.assertEqual(self.mu.mem_read(self.POWERS * 16 + 0xB0, 4), bytes((0, 0, 0, 0 if bm else 1)))
                    self.assertEqual(self.mu.reg_read(r.UC_X86_REG_AX), 0x4321)

    # ---- a kit's own hit die and PSP at creation (sites 200, 201; KIT_REROLL's choice) ----
    MADE = 0x200  # (the sheet being made, SS:200h, far at DS:1429h)
    CR = [(5, 2, kits.BATTLE_MAGE), (5, 3, kits.ARCANIST), (5, 1, None), (6, 2, kits.MIND_WARRIOR),
          (6, 1, None), (6, 3, None), (5, 0, None), (5, 0xFF, None), (5, 0x82, kits.BATTLE_MAGE), (3, 2, None)]

    def made(self, classes, byte, seen) -> None:
        """The creation screen's sheet: CLASSES (1-8, the screen's numbers), its kit byte BYTE; KP_CLASS's
        classes seen SEEN (None: as the sheet's; -1: none yet). Party member 2 (USE_WHO) is being made,
        its party sheet with the same kit byte."""
        sheet = bytearray(ravager.SHEET_SIZE)
        sheet[0x1B:0x1B + len(classes)] = bytes(classes)
        sheet[0x3D] = byte
        self.mu.mem_write(SS * 16 + self.MADE, bytes(sheet))
        self.mu.mem_write(GDS * 16 + 0x1429, struct.pack("<HH", self.MADE, SS))
        cls3 = struct.unpack("<I", bytes(sheet[0x1B:0x1E]) + b"\0")[0]
        self.mu.mem_write(TSR * 16 + self.sym["wp_classes_seen"],
                          struct.pack("<I", cls3 if seen is None else seen & 0xFFFFFFFF))
        self.party([bytes(ravager.SHEET_SIZE)] * 2 + [bytes(sheet)])
        self.mu.mem_write((GDS + 0x3E71 - 0x47E0) * 16 + 0xB44, struct.pack("<H", 2))

    def test_cr_die(self):
        """CR_DIE's AL (the class's die for the creation hit points' most, 360h:11Dh by the screen's class
        BX) is kits.hit_die for the kit chosen: a Battle Mage's 6, an Arcanist's 3, a preserver's 4; none
        for a kit left over from other classes (taken away, from the party's sheet too), nor with the rule
        off; before the screen's first look (an EDIT's) the kit as it is."""
        dice = {3: 10, 5: 4, 6: 6}
        for rules in (game.RULE_KITS >> 16, 0):
            self.rules(rules)
            for cls, byte, kid in self.CR:
                for seen in (None, -1, 0x0101):
                    self.made((cls,), byte, seen)
                    self.mu.mem_write(self.POWERS * 16 + 0x11D + cls, bytes((dice[cls],)))
                    got = self.run_int("cr_die", es=self.POWERS, ebx=cls, eax=0xAB00, ecx=0x1234)
                    want_kid = kid if rules and seen != 0x0101 else None
                    stale = rules and seen == 0x0101
                    with self.subTest(cls=cls, byte=byte, seen=seen, rules=rules):
                        self.assertEqual(got["eax"] & 0xFFFF, 0xAB00 | kits.hit_die(want_kid, dice[cls]))
                        self.assertEqual((got["ecx"] & 0xFFFF, got["ebx"] & 0xFFFF), (0x1234, cls))
                        kept = 0 if stale else byte
                        self.assertEqual(self.mu.mem_read(SS * 16 + self.MADE + 0x3D, 1)[0], kept)
                        party = SS * 16 + self.SHEETS + 2 * ravager.SHEET_SIZE + 0x3D
                        self.assertEqual(self.mu.mem_read(party, 1)[0], kept)

    def test_cr_psp(self):
        """CR_PSP (the creation PSP routine's end): the WIS bonus AX added to the sheet being made's +0Ch,
        then a Mind Warrior's a fifth fewer (kits.max_psp); then the routine's own "pop bp / retf", the
        INT's frame dropped and its flags (IF) put back; ES:BX the sheet as the game's."""
        for rules in (game.RULE_KITS >> 16, 0):
            self.rules(rules)
            for cls, byte, kid in self.CR:
                for psp, bonus in ((0, 0), (25, 0), (61, 3), (104, 0), (4, 1)):
                    self.made((cls,), byte, None)
                    self.mu.mem_write(SS * 16 + self.MADE + 0x0C, struct.pack("<H", psp))
                    self.mu.mem_write(SS * 16 + 0x7F8, struct.pack("<HHHHHH", 0x4444, 0x5555, 0x202, 0x1234, 0xFFF0, TSR))
                    for reg, value in dict(cs=TSR, ds=GDS, ss=SS, esp=0x7F8, ebp=0x600, eflags=0x2, eax=bonus).items():
                        self.mu.reg_write(getattr(r, "UC_X86_REG_" + reg.upper()), value)
                    self.mu.emu_start(TSR * 16 + self.sym["cr_psp"], TSR * 16 + 0xFFF0)
                    got = struct.unpack("<H", self.mu.mem_read(SS * 16 + self.MADE + 0x0C, 2))[0]
                    want = kits.max_psp(kid if rules and kid == kits.MIND_WARRIOR else None, psp + bonus)
                    with self.subTest(cls=cls, byte=byte, psp=psp, bonus=bonus, rules=rules):
                        self.assertEqual(got, want)
                        self.assertEqual([self.mu.reg_read(getattr(r, "UC_X86_REG_" + n)) & 0xFFFF
                                          for n in ("BP", "SP", "AX", "BX", "ES")],
                                         [0x1234, 0x804, bonus, self.MADE, SS])
                        self.assertTrue(self.mu.reg_read(r.UC_X86_REG_EFLAGS) & 0x200)
        self.assertEqual(kits.max_psp(kits.MIND_WARRIOR, 129), 104)

    def test_cr_kit_thac0(self):
        """CR_KIT_THAC0 (the creation screen's THAC0 line): CL a new character's THAC0 1 worse with the Scholar
        kit chosen (kits.thac0; KIT_MADE: none left over from other classes, none with the rule off); an
        EDIT's (CR_EDITING a member) kept, its kit in its own. The creature's THAC0 already with a Scholar's in it
        (CR_THAC0_SCHOLAR, SCHOLAR_THAC0's at a roll): taken out if the kit is no longer chosen, else kept. Other
        registers kept."""
        flag = TSR * 16 + self.sym["cr_thac0_scholar"]
        seen = set()
        for rules in (game.RULE_KITS >> 16, 0):
            self.rules(rules)
            for cls, byte, _ in self.CR:
                for edit in (-1, 1):
                    for stale in (None, 0x0101):
                        for have in (0, 1):
                            self.made((cls,), byte, stale)
                            self.mu.mem_write(GDS * 16 + 0x112E, struct.pack("<h", edit))
                            self.mu.mem_write(flag, bytes((have,)))
                            got = self.run_routine("cr_kit_thac0", b"", ecx=18, eax=0x1357, ebx=0x2468)
                            made = rules and stale is None and byte not in (0, 0xFF) and cls * 4 + (byte & 3) == kits.SCHOLAR
                            base = 18 - have if edit == -1 else 18  # (the creature's without the kit)
                            kid = kits.SCHOLAR if made and edit == -1 else None
                            want = kits.thac0(kid, 7, base) if edit == -1 else 18
                            with self.subTest(cls=cls, byte=byte, edit=edit, stale=stale, rules=rules, have=have):
                                self.assertEqual(self.mu.reg_read(r.UC_X86_REG_ECX) & 0xFF, want)
                                self.assertEqual((got["eax"] & 0xFFFF, got["ebx"] & 0xFFFF), (0x1357, 0x2468))
                            seen.add((kid, have, want))
        self.assertTrue({(kits.SCHOLAR, 0, 19), (kits.SCHOLAR, 1, 18), (None, 1, 17)} <= seen)

    def test_dam_kits(self):
        """The DAM lines' kits (DAM_KIT_MELEE, DAM_EXPERT) are the attack's: KIT_MELEE's damage with the kits'
        rule (none without), and EXPERT_HALVES' attacks for one who isn't a warrior, the attack's KIT_RATES
        count kept."""
        types = bytearray(15 * (ravager.GAME_TYPES + ravager.MOD_TYPES))
        for t in range(ravager.GAME_TYPES + ravager.MOD_TYPES):
            types[t * 15 + 0x0B] = 0x40 if t % 3 == 0 else 0
        self.mu.mem_write(GDS * 16 + TYPES_AT, bytes(types))
        self.mu.mem_write(GDS * 16 + 0x19CD, struct.pack("<HH", TYPES_AT, GDS))
        for rules in (game.RULE_KITS >> 16, 0):
            self.rules(rules)
            for classes, byte in (((9,), 3), ((9,), 0), ((10,), 3)):
                sheet = wotr_sheet(classes, (5,), 2, byte)
                ids = kitpages.kit_ids(sheet) if rules else []
                for t in (0, 1, 3):
                    want = sum(kits.melee(k, t % 3 == 0, specialize.KIND_OF_TYPE.get(t)) for k in ids)
                    got = self.run_routine("dam_kit_melee", sheet, esi=t, eax=0xBEEF)["eax"] & 0xFFFF
                    self.assertEqual(got, want, (classes, byte, rules, t))
        self.rules(game.RULE_KITS >> 16)
        rates = TSR * 16 + self.sym["kit_rates"]
        for level in (1, 7):
            sheet = wotr_sheet((11,), (level,), 1, 2)  # (a Battle Mage)
            self.run_routine("kit_is", sheet, eax=kits.BATTLE_MAGE)
            for skill in (specialize.PLAIN, specialize.EXPERT):
                self.mu.mem_write(rates, struct.pack("<H", 5))
                got = self.run_routine("dam_expert", sheet, eax=0xAB02, edx=skill)["eax"] & 0xFFFF
                want = (4 if level >= 7 else 3) if skill == specialize.EXPERT else 2
                self.assertEqual(got, want, (level, skill))
                self.assertEqual(struct.unpack("<H", self.mu.mem_read(rates, 2))[0], 5)

    def test_kit_rolls_due(self):
        """KIT_ROLLS_DUE: KIT_REROLL due for the sheet being made's Battle Mage, Arcanist or Mind Warrior
        (KIT_ROW calls it with the kit before and after the click), not for another kit or none."""
        for cls, byte, kid in self.CR:
            self.made((cls,), byte, None)
            self.mu.mem_write(TSR * 16 + self.sym["kit_reroll_due"], b"\0")
            self.run_routine("kit_rolls_due", bytes(8), eax=0x1357)
            with self.subTest(cls=cls, byte=byte):
                self.assertEqual(self.mu.mem_read(TSR * 16 + self.sym["kit_reroll_due"], 1)[0], 1 if kid else 0)
                self.assertEqual(self.mu.reg_read(r.UC_X86_REG_AX), 0x1357)


if __name__ == "__main__":
    unittest.main()
