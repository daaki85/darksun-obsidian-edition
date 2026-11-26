"""The kits' casting levels, cures and spells known in Wake of the Ravager: DSCLOG2's KIT_CAST_LEVEL (site 205),
KIT_CURE (206), AVENGER_AREA and AVENGER_ONE (207, 208), run in an emulated CPU through SITE's INT F5h way in,
and CELL_MORE, against Shattered Lands' rules in the sequel's spell numbers (kits.arc_level, sky_level,
cure_bonus, cure_die, harm_bonus with ravlog's layout: ravager.RAV_*) on the transferred party's sheets
(test_ravkits.wotr_sheet, characters); EL_SPHERE's Healer's cosmos and the spells a kit never knows (sites
90-92) against ravager.casts for the druids' kits too (test_ravsphere has the clerics'). And each site's
patch on the sequel's own bytes. Needs nasm and unicorn, else skipped; the program's bytes need the sequel
(DSUN_WOTR)."""

import os
import shutil
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dsloader import game, kitpages, kits, ravager, ravlog  # noqa: E402
from test_ravkits import ASM, characters, wotr_sheet  # noqa: E402
from test_ravsphere import sphere_bytes  # noqa: E402

try:
    from unicorn import Uc, UC_ARCH_X86, UC_MODE_16
    from unicorn import x86_const as r
except ImportError:
    Uc = None

WOTR = os.environ.get("DSUN_WOTR")
TSR, GDS, SS = 0x1000, 0x6000, 0x7000
SHEETS, CREATURES = 0x4800, 0x4900
FIGHTERS_SEG, SPHERES_SEG = 0x3F49 - 0x47E0, 0x41F1 - 0x47E0
GAME_CS, GAME_IP = 0x5555, 0x1233
RULES_HI, KIT_OUTDOORS = 270, 350  # (the header's: the kits' rule word, the Loader's open-sky bits)
SEED = 0x384A
SITES = {"kit_cast_level": (205, 0x629FE), "kit_cure": (206, 0x66545), "avenger_cause_area": (207, 0x7E7A6),
         "avenger_cause_one": (208, 0x7F727)}
CURE_BACK = 0x65811 - (0x66545 + 3)
SPELLS = (0, 8, 27, 0x72, 0x73, ravager.RAV_CURE_LIGHT, ravager.RAV_CAUSE_SERIOUS, 0xD2, 0xEA, 0xEB, 0x10A)


def game_die(seed: int, sides: int):
    """DSCLOG2's GAME_DIE: (the roll, the seed after)."""
    seed = (seed * 0x015A4E35 + 1) & 0xFFFFFFFF
    return ((((seed >> 16) & 0x7FFF) * sides) >> 15) + 1, seed


@unittest.skipIf(Uc is None or not shutil.which("nasm"), "needs unicorn and nasm")
class KitCastTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from test_dsclog_drawing import build
        exe, cls.sym = build(ASM)
        cls.image = exe[struct.unpack_from("<H", exe, 8)[0] * 16:]
        cls.spheres = sphere_bytes()

    def setUp(self):
        mu = self.mu = Uc(UC_ARCH_X86, UC_MODE_16)
        mu.mem_map(0, 0x100000)
        mu.mem_write(TSR * 16, self.image)
        mu.mem_write(0xF5 * 4, struct.pack("<HH", self.sym["site_int"], TSR))
        mu.mem_write(GDS * 16 + 0x19C5, struct.pack("<HHHH", 0, SHEETS, 0, CREATURES))
        mu.mem_write((GDS + SPHERES_SEG) * 16 + 0x7D3, self.spheres)
        for combatant in range(6):  # (combatant N: creature N, its sheet N; 4 and 5 not party members)
            mu.mem_write((GDS + FIGHTERS_SEG) * 16 + 0xC33 + 3 * combatant, struct.pack("<BH", 2, combatant))
            mu.mem_write(CREATURES * 16 + combatant * 0x31 + 4, struct.pack("<H", combatant))
        self.rules(1)
        ravlog.apply_layout()
        self.addCleanup(ravlog.restore_layout)
        old = game.RULES_IN_FORCE
        game.RULES_IN_FORCE = old | game.RULE_KITS
        self.addCleanup(setattr, game, "RULES_IN_FORCE", old)

    def rules(self, hi: int) -> None:
        self.mu.mem_write(TSR * 16 + self.sym["hdr"] + RULES_HI, struct.pack("<H", hi))

    def put(self, combatant: int, sheet: bytes) -> None:
        self.mu.mem_write(SHEETS * 16 + combatant * ravager.SHEET_SIZE, sheet)

    def counter(self, name: str) -> int:
        return struct.unpack("<H", self.mu.mem_read(TSR * 16 + self.sym[name], 2))[0]

    def site(self, number: int, frame: dict, back: int = 3, **regs) -> dict:
        """Site NUMBER run as the game reaches it (INT F5h's frame, SITE's way in reading its byte), the game's
        BP frame FRAME ({offset from BP: word}; a negative offset's byte is the low one). Returns the
        registers, IP and SP after the IRET, run until the way back GAME_IP + BACK."""
        mu = self.mu
        mu.mem_write(GAME_CS * 16 + GAME_IP, bytes((0xCD, 0xF5, number, 0x90, 0xF4)))
        sp, bp = 0x7F0, 0x900
        mu.mem_write(SS * 16 + sp, struct.pack("<HHH", GAME_IP + 2, GAME_CS, 0x2))
        for at, word in frame.items():
            mu.mem_write(SS * 16 + bp + at, struct.pack("<H", word & 0xFFFF))
        base = dict(cs=TSR, ds=GDS, es=0x1234, ss=SS, esp=sp, ebp=bp, eax=0x1111, ebx=0x2222, ecx=0x3333,
                    edx=0x4444, esi=0x5555, edi=0x7777, eflags=0x2)
        for reg, value in dict(base, **regs).items():
            mu.reg_write(getattr(r, "UC_X86_REG_" + reg.upper()), value)
        mu.emu_start(TSR * 16 + self.sym["site_int"], GAME_CS * 16 + ((GAME_IP + back) & 0xFFFF), count=3000)
        got = {reg: mu.reg_read(getattr(r, "UC_X86_REG_" + reg.upper())) & 0xFFFF
               for reg in ("eax", "ebx", "ecx", "edx", "esi", "edi", "ebp", "esp", "ip", "cs", "ds", "es")}
        self.assertEqual(got["cs"], GAME_CS)
        return got

    def word(self, at: int) -> int:
        return struct.unpack("<H", self.mu.mem_read(SS * 16 + at, 2))[0]

    # ---- KIT_CAST_LEVEL ----

    def want_level(self, sheet: bytes, combatant: int, spell: int, level: int, outdoors: bool) -> int:
        """The level 628AFh gives with the kits: kits.arc_level and sky_level (the sequel's spell numbers), for a
        party member whose classes cast the spell; the own party's thri-kreen psionicist a Wasteland Seer."""
        if level <= 0 or combatant > 3:
            return level
        kids = kitpages.kit_ids(sheet)
        if kits.own_features(sheet) == kits.OWN_FEATURES[kits.THRI_KREEN]:
            kids = kids + [kits.WASTE_SEER]
        for kid in kids:
            if kid == kits.ARCANIST:
                return kits.arc_level(kid, spell, level)
            if kid in kits.SKY_KITS:
                return kits.sky_level(kid, spell, level, outdoors)
        return level

    def cast_level(self, combatant: int, spell: int, level: int, place: int = 2) -> dict:
        return self.site(205, {6: combatant, 8: spell, -2: place << 8}, edi=level & 0xFFFF)

    def test_cast_level(self):
        """KIT_CAST_LEVEL's DI after the loop's last place is want_level (kits.arc_level, sky_level): an
        Arcanist's wizard spells 1 higher, a Spirit Caller's and Wasteland Seer's (and the own thri-kreen's)
        priest spells 2 higher under the open sky, 1 lower under a roof but not below 1; only for a party
        member, a level above 0; [BP-1] stepped as the game's INC; every other kit and spell kept."""
        own = [((9, 7, 12), (6, 6, 6), 8, 0x40), ((9, 7), (6, 9), 8, 0x40), ((9, 7, 12), (6, 6, 6), 8, 0x00)]
        changed = set()
        for n, (classes, levels, race, byte) in enumerate(own + characters()):
            sheet = wotr_sheet(classes, levels, race, byte)
            combatant = n % 4  # (not a party member: test_cast_level_loop_and_rule)
            self.put(combatant, sheet)
            for outdoors in (False, True):
                self.mu.mem_write(TSR * 16 + self.sym["hdr"] + KIT_OUTDOORS, bytes((0x3F if outdoors else 0,)))
                for spell in SPELLS:
                    for level in (0, 1, 2, 7):
                        want = self.want_level(sheet, combatant, spell, level, outdoors)
                        with self.subTest(classes=classes, byte=byte, combatant=combatant, spell=spell, level=level,
                                          outdoors=outdoors):
                            got = self.cast_level(combatant, spell, level)
                            self.assertEqual(got["edi"], want)
                            self.assertEqual(self.mu.mem_read(SS * 16 + 0x900 - 1, 1)[0], 3)
                            self.assertEqual((got["ip"], got["esp"]), (GAME_IP + 3, 0x7F6))
                            self.assertEqual((got["eax"], got["ebx"], got["es"]), (0x1111, 0x2222, 0x1234))
                        if want != level:
                            changed.update(k for k in kitpages.kit_ids(sheet) if k in (kits.ARCANIST, *kits.SKY_KITS))
                            if byte == 0x40:
                                changed.add("own")
        self.assertEqual(changed, {kits.ARCANIST, kits.SPIRIT_CALLER, kits.WASTE_SEER, "own"})

    def test_cast_level_loop_and_rule(self):
        """Before the loop's third place DI stays (only [BP-1] stepped); with the kits' rule off nothing."""
        sheet = wotr_sheet((11,), (7,), 1, 3)
        self.assertIn(kits.ARCANIST, kitpages.kit_ids(sheet))
        self.put(0, sheet)
        self.put(4, sheet)
        self.assertEqual(self.cast_level(4, 27, 7)["edi"], 7)  # (not a party member)
        before = self.counter("kc_levels")
        self.assertEqual(self.cast_level(0, 27, 7, place=0)["edi"], 7)
        self.assertEqual(self.mu.mem_read(SS * 16 + 0x900 - 1, 1)[0], 1)
        self.assertEqual(self.cast_level(0, 27, 7)["edi"], 8)
        self.assertEqual(self.counter("kc_levels"), before + 1)
        self.rules(0)
        self.assertEqual(self.cast_level(0, 27, 7)["edi"], 7)

    # ---- KIT_CURE ----

    def cure(self, combatant: int, spell: int, healing: int) -> tuple:
        """KIT_CURE at 66545h with AX the healing: (the word it pushed, the way back's IP, the seed before)."""
        seed = 0x12345678
        self.mu.mem_write(GDS * 16 + SEED, struct.pack("<I", seed))
        got = self.site(206, {8: combatant, 0x0E: spell}, back=3 + CURE_BACK, eax=healing)
        self.assertEqual(got["esp"], 0x7F6 - 2)
        self.assertEqual((got["eax"], got["ebx"], got["ecx"], got["edx"], got["esi"], got["edi"], got["ebp"]),
                         (healing, 0x2222, 0x3333, 0x4444, 0x5555, 0x7777, 0x900))
        return self.word(0x7F4), (got["ip"] - (GAME_IP + 3)) & 0xFFFF, seed

    def test_cure(self):
        """KIT_CURE pushes the healing with the caster's kit's (kits.cure_bonus, cure_die in the sequel's numbers:
        a Healer's and Rescuer's Cure Light, Serious and Critical Wounds 1 more a die, a Lifebinder's those and
        Blood Flow a die more, GAME_DIE's roll from the game's seed) and goes on at 65811h, for any caster;
        Cell Adjustment (248, its more CELL_HEAL's) and any other spell kept."""
        seen = set()
        cures = sorted(ravager.RAV_CURE_DICE) + [248, ravager.RAV_CAUSE_LIGHT, 0x10A]
        for n, (classes, levels, race, byte) in enumerate(characters()):
            sheet = wotr_sheet(classes, levels, race, byte)
            combatant = n % 6
            self.put(combatant, sheet)
            kid = next((k for k in kitpages.kit_ids(sheet) if k in (kits.HEALER, kits.RESCUER, kits.LIFEBINDER)), 0)
            for spell in cures:
                healing = 9
                pushed, back, seed = self.cure(combatant, spell, healing)
                want = healing + kits.cure_bonus(kid, spell)
                if kits.cure_die(kid, spell):
                    want += game_die(seed, kits.cure_die(kid, spell))[0]
                with self.subTest(classes=classes, byte=byte, spell=spell):
                    self.assertEqual(back, CURE_BACK & 0xFFFF)
                    self.assertEqual(pushed, want)
                if want != healing:
                    seen.add(kid)
        self.assertEqual(seen, {kits.HEALER, kits.RESCUER, kits.LIFEBINDER})
        self.assertEqual(kits.cure_bonus(kits.HEALER, ravager.RAV_BLOOD_FLOW), 0)
        self.rules(0)
        self.put(0, wotr_sheet((4,), (7,), 1, 2))
        self.assertEqual(self.cure(0, ravager.RAV_CURE_LIGHT, 5)[0], 5)

    # ---- AVENGER_AREA, AVENGER_ONE ----

    def test_avenger_cause(self):
        """Each site stores the damage with a Wilderness Avenger's Cause Wounds more (kits.harm_bonus in the
        sequel's numbers) on the damage and on the most a helpless target takes, when the last cast (CAST_WHO,
        CAST_SPELL) is the Avenger's of that spell; none for another caster, another spell, a spell not the
        last cast, or with the rule off."""
        avenger = next(c for c in characters() if kits.AVENGER in kitpages.kit_ids(wotr_sheet(*c)))
        druid = wotr_sheet((5, 9), (5, 5), 6, 0)
        self.put(0, wotr_sheet(*avenger))
        self.put(1, druid)
        made = 0
        for number, at, most in ((207, -0x14, -0x16), (208, -6, -8)):
            for who in (0, 1):
                for spell in (ravager.RAV_CAUSE_LIGHT, ravager.RAV_CAUSE_SERIOUS, ravager.RAV_CAUSE_CRITICAL,
                              ravager.RAV_CURE_LIGHT, 27):
                    for cast in (spell, 8):
                        self.mu.mem_write(TSR * 16 + self.sym["cast_who"], struct.pack("<H", who))
                        self.mu.mem_write(TSR * 16 + self.sym["cast_spell"], struct.pack("<H", cast))
                        got = self.site(number, {most: 20}, eax=12, edi=spell)
                        more = kits.harm_bonus(kits.AVENGER, spell) if who == 0 and cast == spell else 0
                        with self.subTest(site=number, who=who, spell=spell, cast=cast):
                            self.assertEqual(self.word(0x900 + at), 12 + more)
                            self.assertEqual(self.word(0x900 + most), 20 + more)
                            self.assertEqual((got["eax"], got["ebx"], got["ip"], got["esp"]),
                                             (12 + more, 0x2222, GAME_IP + 3, 0x7F6))
                        made += bool(more)
        self.assertEqual(made, 6)
        self.rules(0)
        self.mu.mem_write(TSR * 16 + self.sym["cast_who"], struct.pack("<H", 0))
        self.mu.mem_write(TSR * 16 + self.sym["cast_spell"], struct.pack("<H", ravager.RAV_CAUSE_LIGHT))
        self.site(208, {-8: 20}, eax=12, edi=ravager.RAV_CAUSE_LIGHT)
        self.assertEqual(self.word(0x900 - 6), 12)

    # ---- CELL_MORE ----

    def test_cell_more(self):
        """CELL_MORE's CX: a Lifebinder's d4 (GAME_DIE), a Healer's or Rescuer's 1, else 0 (kits.CELL_MORE,
        CELL_PLUS); AX kept."""
        for n, (classes, levels, race, byte) in enumerate(characters()):
            sheet = wotr_sheet(classes, levels, race, byte)
            combatant = n % 6
            self.put(combatant, sheet)
            seed = 0x2468ACE1
            self.mu.mem_write(GDS * 16 + SEED, struct.pack("<I", seed))
            kids = kitpages.kit_ids(sheet)
            want = (game_die(seed, kits.CELL_MORE)[0] if kits.LIFEBINDER in kids
                    else kits.CELL_PLUS if {kits.HEALER, kits.RESCUER} & set(kids) else 0)
            mu = self.mu
            mu.mem_write(SS * 16 + 0x7FC, struct.pack("<H", 0xFFF0))
            mu.mem_write(TSR * 16 + 0xFFF0, b"\xF4")
            for reg, value in dict(cs=TSR, ds=GDS, ss=SS, esp=0x7FC, eax=combatant, ecx=0x3333, eflags=2).items():
                mu.reg_write(getattr(r, "UC_X86_REG_" + reg.upper()), value)
            mu.emu_start(TSR * 16 + self.sym["cell_more"], TSR * 16 + 0xFFF0, count=2000)
            with self.subTest(classes=classes, byte=byte):
                self.assertEqual(mu.reg_read(r.UC_X86_REG_CX), want)
                self.assertEqual(mu.reg_read(r.UC_X86_REG_AX), combatant)

    # ---- the spells known: EL_SPHERE ----

    def test_spells_known(self):
        """EL_SPHERE's answer (sites 90-92) is ravager.casts for every kit with a priest class (the druids'
        Lifebinder and Wilderness Avenger, the cleric's Healer): a Healer's cleric casts the sphere of the
        cosmos's spells (the druids' 20h) but no harming one, a Lifebinder knows no harming spell and an
        Avenger no healing one, though the game says yes; the cosmos's extra spells (COSMOS_MORE) none yet."""
        from test_ravsphere import ElSphereTests
        runner = ElSphereTests("test_el_sphere")
        runner.mu, runner.sym = self.mu, self.sym
        for combatant in range(4):  # (ElSphereTests' combatants: N is creature N + 5, its sheet N)
            self.mu.mem_write((GDS + FIGHTERS_SEG) * 16 + 0xC33 + 3 * combatant, struct.pack("<BH", 2, combatant + 5))
            self.mu.mem_write(CREATURES * 16 + (combatant + 5) * 0x31 + 4, struct.pack("<H", combatant))
        self.assertEqual(self.mu.mem_read(TSR * 16 + self.sym["cosmos_more"], 4), b"\xff" * 4)
        self.assertEqual(set(ravager.RAV_COSMOS_MORE), {"Whirlwind", "Restore Youth"})
        spells = sorted({s for s in ravager.PRIEST_SPELLS if self.spheres[s] & ravager.DRUIDS}
                        | ravager.RAV_NO_HARM | ravager.RAV_AVENGER_NO_HEAL | {0x73, 0x79, 0x86})
        barred, cosmos = 0, 0
        for n, (classes, levels, race, byte) in enumerate(characters()):
            sheet = wotr_sheet(classes, levels, race, byte)
            kids = kitpages.kit_ids(sheet)
            if not {kits.HEALER, kits.LIFEBINDER, kits.AVENGER} & set(kids):
                continue
            member = n % 4
            self.mu.mem_write(SHEETS * 16 + member * ravager.SHEET_SIZE, sheet)
            for cls in set(c for c in classes) | {4, 5}:
                for spell in spells:
                    byte_ = self.spheres[spell]
                    game_says = int(bool(byte_ & ravager.class_spheres(cls)))
                    want = int(ravager.casts(sheet, cls, spell, byte_))
                    site = (90, 91, 92)[(cls + spell) % 3]
                    with self.subTest(classes=classes, byte=byte, cls=cls, spell=spell, site=site):
                        self.assertEqual(runner.site(site, member, spell, cls, game_says), want)
                    barred += game_says and not want
                    cosmos += want and not game_says
        self.assertGreater(barred, 0)
        self.assertGreater(cosmos, 0)
        self.assertGreater(self.counter("kc_barred"), 0)
        self.assertGreater(self.counter("kc_cosmos"), 0)

    def test_rules_in_python(self):
        """ravager.casts in the sequel's numbers: a water Healer casts Cure Serious Wounds (a druid's 20h) and
        never Cause Light Wounds; a Lifebinder never Harm; a Wilderness Avenger never Cure Light Wounds."""
        healer = next(wotr_sheet(*c) for c in characters() if kits.HEALER in kitpages.kit_ids(wotr_sheet(*c)))
        cls = kitpages.kit_class_of(healer, kits.HEALER)
        self.assertTrue(ravager.casts(healer, cls, ravager.RAV_CURE_SERIOUS, ravager.DRUIDS))
        self.assertFalse(ravager.casts(healer, cls, ravager.RAV_CAUSE_LIGHT, 0x30))
        self.assertFalse(ravager.casts(healer, cls, ravager.RAV_CAUSE_SERIOUS, ravager.DRUIDS))
        life = next(wotr_sheet(*c) for c in characters() if kits.LIFEBINDER in kitpages.kit_ids(wotr_sheet(*c)))
        self.assertFalse(ravager.casts(life, 5, ravager.RAV_HARM, ravager.DRUIDS))
        self.assertTrue(ravager.casts(life, 5, ravager.RAV_CURE_LIGHT, 0x30))
        avenger = next(wotr_sheet(*c) for c in characters() if kits.AVENGER in kitpages.kit_ids(wotr_sheet(*c)))
        self.assertFalse(ravager.casts(avenger, 5, ravager.RAV_CURE_LIGHT, 0x30))
        self.assertTrue(ravager.casts(avenger, 5, ravager.RAV_CAUSE_LIGHT, 0x30))


@unittest.skipUnless(ravager.is_wotr_dir(WOTR), "needs the sequel (DSUN_WOTR)")
class SequelBytesTests(unittest.TestCase):
    def test_sites(self):
        """Each site's patch is SITE's bytes on the sequel's own: 629FEh the loop's "inc byte [bp-1]" in 628AFh
        (before its "cmp byte [bp-1],3", the "mov ax,di" after the loop), 66545h "push ax / jmp 65811h", 7E7A6h
        and 7F727h the store after a call to the spell damage routine (80278h)."""
        exe = open(os.path.join(WOTR, "DSUN.EXE"), "rb").read()
        by_name = {p.name: p for p in ravager.PATCHES}
        for name, (number, at) in SITES.items():
            p = by_name[name]
            self.assertEqual(p.offset, at)
            self.assertEqual(exe[at:at + len(p.original)], p.original, name)
            self.assertEqual(p.replacement[:3], bytes((0xCD, 0xF5, number)))
            self.assertEqual(len(p.replacement), len(p.original))
        self.assertEqual(exe[0x62A01:0x62A0C], bytes.fromhex("807eff037d03e9b6fe8bc7"))
        self.assertEqual(exe[0x65811:0x65817], bytes.fromhex("579a43002806"))
        for at in (0x7E7A6, 0x7F727):
            call = at - 6
            self.assertEqual(exe[call], 0xE8)
            self.assertEqual(call + 3 + struct.unpack_from("<h", exe, call + 1)[0], 0x80278)
        names = ravlog.spell_table(open(os.path.join(WOTR, "RESOURCE.GFF"), "rb").read())[1]
        self.assertEqual([names[s] for s in sorted(ravager.RAV_CURE_DICE)],
                         ["Cure Light Wounds", "Blood Flow", "Cure Serious Wounds", "Cure Critical Wounds"])
        self.assertEqual({names[s] for s in ravager.RAV_NO_HARM},
                         {"Cause Light Wounds", "Cause Serious Wounds", "Cause Critical Wounds", "Cause Disease",
                          "Poison", "Slay Living", "Harm"})
        self.assertEqual({names[s] for s in ravager.RAV_AVENGER_NO_HEAL},
                         {"Cure Light Wounds", "Blood Flow", "Cure Serious Wounds", "Cure Critical Wounds", "Heal",
                          "Waters of Life"})
        self.assertEqual(names[ravager.RAV_WIZARD_LAST], "Wall of Ash")
        self.assertEqual(names[ravager.RAV_WIZARD_LAST + 1], "Bless")


if __name__ == "__main__":
    unittest.main()
