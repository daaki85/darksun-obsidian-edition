"""DSCLOG2's Poisoner's poison, Spellarcher's arrows' plus and Fine Bow in Wake of the Ravager (POISON_HIT,
PLAIN_ARROW's poison, ARROW_PLUS and FINE_HIT, run in an emulated CPU) against Shattered Lands' rules
(kits.arrow_plus, spellarrows.archer_level; DSCLOG's PROBE_POISON's hands and doses) on the transferred
party's sheets (test_ravkits.wotr_sheet, ravlog's layout), and the Loader's side: the sites' patches,
the transfer keeping a Fine Bow's name, the dice log's sequel poison. Needs nasm and unicorn for the
emulated part, else skipped."""

import os
import shutil
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dsloader import game, kitpages, kits, ravager, ravlog, ravtransfer, specialize, spellarrows  # noqa: E402
import test_ravkits  # noqa: E402

try:
    from unicorn import Uc, UC_ARCH_X86, UC_MODE_16
    from unicorn import x86_const as r
except ImportError:
    Uc = None

ASM = test_ravkits.ASM
TSR, SS, GDS = 0x1000, 0x4000, 0x6000
CREATURES_AT, SHEETS_AT, ITEMS_AT = 0x8000, 0x9000, 0xA000  # (in the test's game segment)
AMMO_SEG = 0x308  # (the attack's ammunition record: 308h:[7] its power, [9] its plus)
FIGHTERS = (GDS + 0x3F49 - 0x47E0) * 16 + 0x0C33  # (DSCLOG2's FIGHTERS_SEG, FIGHTERS_OFF: 3 bytes a combatant)
FRAME = 0x600  # (the game's BP: the weapon attack routine's frame)
POISONER = ((9, 17), 6, 1)  # (a halfling fighter/thief, its kit byte: the Poisoner)
SPELLARCHER = ((9, 11), 4, 1)  # (a half-elf fighter/preserver: the Spellarcher)
PLAIN = ((9, 17), 6, 0)
RIGHT, LEFT = 3, 10  # (the sequel's item slots: SL's)


@unittest.skipIf(Uc is None or not shutil.which("nasm"), "needs unicorn and nasm")
class PoisonArrowTests(unittest.TestCase):
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
        ravlog.apply_layout()
        self.addCleanup(ravlog.restore_layout)
        old = game.RULES_IN_FORCE
        game.RULES_IN_FORCE = old | game.RULE_KITS
        self.addCleanup(setattr, game, "RULES_IN_FORCE", old)
        self.rules(game.RULE_KITS >> 16)
        for ptr, at in ((ravager.CREATURES_PTR, CREATURES_AT), (ravager.SHEETS_PTR, SHEETS_AT),
                        (ravager.ITEMS_PTR, ITEMS_AT)):
            self.mu.mem_write(GDS * 16 + ptr, struct.pack("<HH", at, GDS))

    def rules(self, hi: int) -> None:
        self.mu.mem_write(TSR * 16 + self.sym["hdr"] + test_ravkits.RULES_HI, struct.pack("<H", hi))

    def word(self, name: str) -> int:
        return struct.unpack("<H", self.mu.mem_read(TSR * 16 + self.sym[name], 2))[0]

    def byte(self, name: str) -> int:
        return self.mu.mem_read(TSR * 16 + self.sym[name], 1)[0]

    def member(self, creature: int, who, levels=(5, 5)) -> bytes:
        """Creature CREATURE (sheet CREATURE) made WHO: (classes, race, kit byte) at LEVELS."""
        classes, race, byte = who
        sheet = test_ravkits.wotr_sheet(classes, levels, race, byte)
        rec = bytearray(ravager.CREATURE_SIZE)
        struct.pack_into("<H", rec, 4, creature)
        self.mu.mem_write(GDS * 16 + CREATURES_AT + creature * ravager.CREATURE_SIZE, bytes(rec))
        self.mu.mem_write(GDS * 16 + SHEETS_AT + creature * ravager.SHEET_SIZE, sheet)
        return sheet

    def item(self, index: int, slot: int = RIGHT, power: int = 0, name: int = 1, plus: int = 0) -> int:
        rec = bytearray(ravager.ITEM_SIZE)
        struct.pack_into("<H", rec, 0x10, power)
        rec[0x13] = slot
        struct.pack_into("<H", rec, 0x14, name)
        rec[0x16] = plus & 0xFF
        at = ITEMS_AT + index * ravager.ITEM_SIZE
        self.mu.mem_write(GDS * 16 + at, bytes(rec))
        return at

    def site(self, name: str, frame: dict, **regs) -> dict:
        """NAME as SITE runs it (an INT's frame under it, the game's BP FRAME with FRAME's words)."""
        for off, value in frame.items():
            self.mu.mem_write(SS * 16 + FRAME + off, struct.pack("<h", value))
        self.mu.mem_write(SS * 16 + 0x7F8, struct.pack("<HHH", 0xFFF0, TSR, 0x2))
        regs = dict(dict(cs=TSR, ds=GDS, ss=SS, esp=0x7F8, ebp=FRAME, eflags=0x2), **regs)
        for reg, value in regs.items():
            self.mu.reg_write(getattr(r, "UC_X86_REG_" + reg.upper()), value)
        self.mu.emu_start(TSR * 16 + self.sym[name], TSR * 16 + 0xFFF0)
        return {reg: self.mu.reg_read(getattr(r, "UC_X86_REG_" + reg.upper())) for reg in ("eax", "eflags", "esp")}

    def hit(self, creature: int, item: int, missile: int = 1) -> bool:
        """POISON_HIT for CREATURE's hit with ITEM: whether it answers "a spell" (ZF clear)."""
        at = ITEMS_AT + item * ravager.ITEM_SIZE
        got = self.site("poison_hit", {0x0E: creature, 0x12: item, 0x16: missile}, es=GDS, ebx=at)
        self.assertEqual(got["esp"], 0x7FE)
        return not got["eflags"] & 0x40

    def test_poison_hit(self):
        """A Poisoner's first melee hit of a fight with each hand's weapon is a spell (its dose used, marked in
        POISON_USED's bit N and N + 4); a second, a shot, a weapon of its own spell, another kit, a creature
        outside the party, the kits off: as the game has it."""
        self.member(0, POISONER)
        self.member(1, PLAIN)
        self.member(5, POISONER)
        self.item(1, RIGHT)
        self.item(2, LEFT)
        self.item(3, RIGHT, power=11)
        self.assertTrue(self.hit(0, 1))
        self.assertEqual(self.byte("pz_armed"), 1)
        self.assertEqual(self.word("poison_used"), 0x01)
        self.mu.mem_write(TSR * 16 + self.sym["pz_armed"], b"\0")
        self.assertFalse(self.hit(0, 1))  # (that hand's dose used)
        self.assertEqual(self.byte("pz_armed"), 0)
        self.assertTrue(self.hit(0, 2))  # (the off hand's)
        self.assertEqual(self.word("poison_used"), 0x11)
        self.mu.mem_write(TSR * 16 + self.sym["poison_used"], b"\0\0")
        self.mu.mem_write(TSR * 16 + self.sym["pz_armed"], b"\0")
        self.assertFalse(self.hit(0, 1, missile=2))  # (a throw)
        self.assertTrue(self.hit(0, 3))  # (its own spell: cast, no dose)
        self.assertEqual(self.byte("pz_armed"), 0)
        self.assertFalse(self.hit(1, 1))  # (a plain fighter/thief)
        self.assertFalse(self.hit(5, 1))  # (not in the party)
        self.rules(0)
        self.assertFalse(self.hit(0, 1))
        self.assertEqual(self.word("poison_used"), 0)
        self.assertEqual(self.word("poison_doses"), 2)

    def test_plain_arrow_casts_the_poison(self):
        """PLAIN_ARROW with a dose armed makes the hit's spell the sequel's poison (273, Shattered Lands' 176 by
        its record) and disarms; unarmed, a melee hit casts the weapon's own spell as before."""
        self.item(1, RIGHT, power=11)
        self.mu.mem_write(TSR * 16 + self.sym["pz_armed"], b"\1")
        self.site("plain_arrow", {0x16: 1}, eax=0, esi=1)
        self.assertEqual(struct.unpack("<h", self.mu.mem_read(SS * 16 + FRAME - 0x18, 2))[0], ravlog.RAV_POISON_POWER)
        self.assertEqual(self.byte("pz_armed"), 0)
        self.assertEqual(self.word("poison_casts"), 1)
        self.site("plain_arrow", {0x16: 1}, eax=11, esi=1)
        self.assertEqual(struct.unpack("<h", self.mu.mem_read(SS * 16 + FRAME - 0x18, 2))[0], 10)

    def test_poison_record(self):
        """The sequel's 273 is Shattered Lands' 176, the monsters' "poison (10 damage)", by its record (its
        name aside), and the dice log names it so in the sequel."""
        wotr = os.environ.get("DSUN_WOTR")
        path = os.path.join(wotr, ravager.RESOURCE_FILE) if wotr else None
        if not path or not os.path.isfile(path):
            self.skipTest("needs the sequel (DSUN_WOTR)")
        table, _ = ravlog.spell_table(open(path, "rb").read())
        rec = table[ravlog.RAV_POISON_POWER * 32:(ravlog.RAV_POISON_POWER + 1) * 32]
        self.assertEqual(rec[0x1C], 10)  # (its damage)
        self.assertEqual(game.POISON_POWERS[ravlog.RAV_POISON_POWER], "Poison (10 damage)")
        self.assertEqual(kits.POISON_POWER, ravlog.RAV_POISON_POWER)

    def arrow(self, creature: int, who, level: int, name: int, plus: int, bow: bool = True) -> int:
        self.member(creature, who, (level, level))
        self.mu.mem_write(GDS * 16 + ravager.WHOSE_TURN, struct.pack("<H", 7))
        self.mu.mem_write(FIGHTERS + 7 * 3, struct.pack("<BH", 2, creature))
        self.item(4, 1, name=name, plus=plus)
        bow_type = next(t for t in range(ravager.GAME_TYPES) if specialize.kind_of(t) == specialize.KINDS.index("bow"))
        sword = next(t for t in range(ravager.GAME_TYPES) if specialize.kind_of(t) == specialize.KINDS.index("long sword"))
        self.mu.mem_write(AMMO_SEG * 16 + 9, b"\x7f")
        self.site("arrow_plus", {0x0C: bow_type if bow else sword}, es=AMMO_SEG, edi=4, eax=plus & 0xFF)
        return struct.unpack("<b", self.mu.mem_read(AMMO_SEG * 16 + 9, 1))[0]

    def test_arrow_plus(self):
        """ARROW_PLUS keeps kits.arrow_plus: a Spellarcher's spell arrows (by name, ravager.mod_name of
        spellarrows' names) from a bow +1 from its 5th preserver level, +2 from its 9th, +3 from its 13th; its
        plain arrows, another kit's, a sling's as they are; anyone outside the party's by its highest level."""
        first = ravager.NAMES_GAME + 42
        self.assertEqual(first, ravager.mod_name(0x16C))
        for level in (1, 4, 5, 8, 9, 12, 13, 20):
            for plus in (-1, 0, 1, 2):
                for name in (first + 1, first + 3, 7):
                    with self.subTest(level=level, plus=plus, name=name):
                        sheet = test_ravkits.wotr_sheet(SPELLARCHER[0], (level, level), *SPELLARCHER[1:])
                        want = kits.arrow_plus(kits.SPELLARCHER, plus, name != 7, spellarrows.archer_level(sheet, True))
                        self.assertEqual(self.arrow(0, SPELLARCHER, level, name, plus), want)
                        self.assertEqual(self.arrow(1, PLAIN, level, name, plus), plus)
                        self.assertEqual(self.arrow(0, SPELLARCHER, level, name, plus, bow=False), plus)
                        want = kits.arrow_plus(kits.SPELLARCHER, plus, name != 7, level)
                        self.assertEqual(self.arrow(6, PLAIN, level, name, plus), want)
        self.rules(0)
        self.assertEqual(self.arrow(0, SPELLARCHER, 13, first + 1, 0), 0)

    def test_fine_hit(self):
        """FINE_HIT: the THAC0 one better for an attack with the Fine Bow (named ravager.FINE_BOW_NAME), any
        other weapon or none as it is; whatever the rules."""
        self.assertEqual(ravager.FINE_BOW_NAME, ravager.mod_name(game.FINE_BOW_NAME if not ravlog._SAVED
                                                                  else ravager.SL_FINE_BOW_NAME))
        self.rules(0)
        for item, name, want in ((1, ravager.FINE_BOW_NAME, 13), (2, ravager.FINE_BOW_NAME - 1, 14), (9999, 0, 14)):
            if item < 9999:
                self.item(item, name=name)
            self.mu.mem_write(SS * 16 + FRAME + 0x0A, struct.pack("<h", 14))
            self.mu.mem_write(SS * 16 + FRAME + 0x12, struct.pack("<H", item))
            self.mu.mem_write(SS * 16 + 0x7FC, struct.pack("<H", 0xFFF0))
            for reg, value in dict(cs=TSR, ds=GDS, ss=SS, esp=0x7FC, ebp=FRAME, eflags=0x2).items():
                self.mu.reg_write(getattr(r, "UC_X86_REG_" + reg.upper()), value)
            self.mu.emu_start(TSR * 16 + self.sym["fine_hit"], TSR * 16 + 0xFFF0)
            self.assertEqual(struct.unpack("<h", self.mu.mem_read(SS * 16 + FRAME + 0x0A, 2))[0], want)
        self.assertEqual(self.word("fine_hits"), 1)

    def test_site_table(self):
        """Sites 214 and 215 are POISON_HIT and ARROW_PLUS in SITE_TABLE and in ravager.PATCHES."""
        table = self.sym["site_table"]
        for number, name in ((214, "poison_hit"), (215, "arrow_plus")):
            self.assertEqual(struct.unpack_from("<H", self.image, table + 2 * number)[0], self.sym[name])
            p = next(p for p in ravager.PATCHES if p.name == name)
            self.assertEqual(p.replacement[:3], bytes((0xCD, ravager.VEC_SITE, number)))
        hdr = self.sym["hdr"]
        self.assertEqual([self.sym[n] - hdr for n in ("poison_used", "poison_doses", "poison_casts", "arrow_pluses",
                                                      "fine_hits")], [2088, 2090, 2092, 2094, 2096])


class LoaderTests(unittest.TestCase):
    def test_transfer_keeps_the_fine_bow(self):
        """The party transfer's item keeps a Fine Bow's name (the sequel's FINE_BOW_NAME) on the sequel's bow,
        and leaves another bow's the sequel's."""
        class Sequel:
            loader, spells, counterparts, objects = False, None, {300: 301}, {("RDFF", 301)}

            @staticmethod
            def record(obj):
                rec = bytearray(ravager.ITEM_SIZE)
                struct.pack_into("<H", rec, 0x14, 77)
                return bytes(rec)
        sl = bytearray(game.ITEM_SIZE if not ravlog._SAVED else 0x15)
        struct.pack_into("<h", sl, 0, -300)
        struct.pack_into("<H", sl, ravtransfer.SL_ITEM_NAME, ravager.SL_FINE_BOW_NAME)
        out, obj = ravtransfer.item(bytes(sl), Sequel)
        self.assertEqual(obj, 301)
        self.assertEqual(struct.unpack_from("<H", out, 0x14)[0], ravager.FINE_BOW_NAME)
        struct.pack_into("<H", sl, ravtransfer.SL_ITEM_NAME, 0x20)
        out, _ = ravtransfer.item(bytes(sl), Sequel)
        self.assertEqual(struct.unpack_from("<H", out, 0x14)[0], 77)

    def test_layout(self):
        """The dice log in the sequel names the poison and knows the Fine Bow by the sequel's numbers."""
        ravlog.apply_layout()
        try:
            self.assertEqual(game.FINE_BOW_NAME, ravager.FINE_BOW_NAME)
            self.assertEqual(game.POISON_DAMAGE[kits.POISON_POWER], 10)
        finally:
            ravlog.restore_layout()
        self.assertEqual(kits.POISON_POWER, 176)
        self.assertEqual(game.FINE_BOW_NAME, 0x173)


if __name__ == "__main__":
    unittest.main()
