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
        class or Terrannus's (kits.slot_level with own_behind), SB_BEHIND set; BEHIND_LEAST then puts the
        level back and makes no slots 1 where the class's own level reaches the spell level (kits.slots)."""
        cases = [((2,), 0x40, 1), ((2,), 0x43, 1), ((2,), 0x00, 1), ((3,), 0x01, 1), ((3,), 0x03, 1), ((1, 9), 0x04, 1),
                 ((9, 1), 0x01, 1), ((11,), 0x40, 1), ((17, 9), 0x40, 1)]
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
                        behind = bool(rules) and 1 <= cls <= 4 and (kid is not None or (byte != 0xFF and byte & 0x40 and race == 1))
                        self.frame(cls, 1)
                        got = self.run_routine("slot_behind", sheet, ecx=0x1100 | levels[place], ebp=0x600,
                                               edi=place, ebx=0x500 + place)
                        want = kits.slot_level(kits.ELEMENTALIST if behind else 0, levels[place])
                        with self.subTest(classes=classes, byte=byte, level=level, place=place, rules=rules):
                            self.assertEqual(self.mu.mem_read(TSR * 16 + self.sym["sb_behind"], 1)[0], int(behind))
                            self.assertEqual(self.mu.reg_read(r.UC_X86_REG_CX), 0x1100 | want)
                            self.assertEqual(got["ebx"] & 0xFFFF, 0x500 + place)
        for adnd in (True, False):  # (RULE_HI_TABLES, 8, on and off)
            self.rules(game.RULE_KITS >> 16 | (8 if adnd else 0))
            for level in range(1, 20):
                for spell in range(1, 8):
                    for given in (0, 1, 3):
                        self.frame(2, spell)
                        self.mu.mem_write(SS * 16 + 0x700, bytes((max(0, level - 1), 17)))
                        self.mu.mem_write(TSR * 16 + self.sym["sb_behind"], b"\1")
                        self.mu.mem_write(TSR * 16 + self.sym["sb_level"], bytes((level,)))
                        got = self.run_routine("behind_least", bytes(8), eax=given, esi=0x700, ebp=0x600)["eax"] & 0xFFFF
                        with self.subTest(level=level, spell=spell, given=given, adnd=adnd):
                            self.assertEqual(got, kits.slots(kits.ELEMENTALIST, kits.PRIEST, level, spell, given, adnd))
                            self.assertEqual(self.mu.mem_read(SS * 16 + 0x700, 1)[0], level)
        self.assertEqual([kits.slots(kits.CRUSADER, kits.PRIEST, 7, 4, n, behind=True) for n in (0, 2)], [1, 2])
        self.assertEqual(kits.slots(kits.CRUSADER, kits.PRIEST, 7, 4, 2), 1)


if __name__ == "__main__":
    unittest.main()
