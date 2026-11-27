"""DSCLOG2's weapon traits for the sequel's own Lotulis, Double Spear and Trikal (THE TRIKAL AND THE TWO-HEADED
WEAPONS, run in an emulated CPU), as Shattered Lands' (DSCLOG's, tests/test_cahulaks.py): a lotulis or double
spear specialist's last swing of a round of two or more turned on a second foe beside it (SF_SWING, from
CAH_SWING), its AC the game's AC routine's, both put back after the swing (SF_SITE, site 202), the double
spear's swing 1 less (SF_LESS, from ENL_ROLL); a trikal specialist's hit tripping a man-sized target that
fails a save against paralysis (CAH_HIT); the trikal reaching two squares as a polearm (REACH_HANDS). And the
Loader's double spear of range 1 (ravager.RAV_RANGES), and the site's patch in the game's own program with
DSUN_WOTR. Needs nasm and unicorn, else skipped."""

import os
import shutil
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dsloader import gff, ravager, ravlog, specialize  # noqa: E402

try:
    from unicorn import Uc, UC_ARCH_X86, UC_MODE_16
    from unicorn import x86_const as r
except ImportError:
    Uc = None

ASM = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dos", "dsclog2.asm")
WOTR = os.environ.get("DSUN_WOTR")
TSR, GAME_DS, SS, RING = 0x1000, 0x5000, 0x4000, 0x9000
SHEETS, CREATURES, ITEMS, TYPES = 0x6000, 0x6800, 0x7000, 0x7800
OVERLAY, WAY_BACK = 0x8000, 0x0100          # (the combat overlay's CS and CAH_SWING's way back in it)
BP = 0x600
FIGHTERS = (GAME_DS + 0x3F49 - 0x47E0) * 16 + 0x0C33
DISTANCE = GAME_DS + 0x1D40 - 0x47E0         # (the distance routine's segment: 35EFh in it)
DIST_TABLE = 0x4000                          # (the stub's distances, a word a combatant)
TARGET, SEED = 0x4206, 0x384A
RULE_HI_CAHULAKS, RULE_HI_SIZE = 0x2000, 0x4000
LOTULIS, DOUBLE_SPEAR, TRIKAL, LONG_SWORD, POLEARM = 61, 39, 100, 16, 80
NO_ITEM = 9999
ATTACKER, FIRST, SECOND, THIRD = 2, 20, 21, 22   # (combatants: each creature its number)
SHEET = 1                                         # (the attacker's sheet)
K = specialize.KINDS.index
MN_TRIP, MN_SECOND = 13, 14


def game_die(seed: int, sides: int):
    seed = (seed * 0x015A4E35 + 1) & 0xFFFFFFFF
    return seed, (((seed >> 16) & 0x7FFF) * sides >> 15) + 1


@unittest.skipIf(Uc is None or not shutil.which("nasm"), "needs unicorn and nasm")
class TraitsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from test_dsclog_drawing import build
        from test_ravspecialize import wotr_sheet
        exe, cls.sym = build(ASM)
        cls.image = exe[struct.unpack_from("<H", exe, 8)[0] * 16:]
        cls.sheets = {kinds: wotr_sheet((9,), (3,), 2, [K(k) for k in kinds])
                      for kinds in (("lotulis", "double spear", "trikal"), ("long sword",))}

    def machine(self, kinds=("lotulis", "double spear", "trikal"), rules_hi=RULE_HI_CAHULAKS):
        mu = Uc(UC_ARCH_X86, UC_MODE_16)
        mu.mem_map(0, 0x100000)
        mu.mem_write(TSR * 16, self.image)
        mu.mem_write(TSR * 16 + 0xFFF0, bytes((0xF4,)))
        mu.mem_write(TSR * 16 + self.sym["rules_hi"], struct.pack("<H", rules_hi))
        mu.mem_write(TSR * 16 + self.sym["ring_seg"], struct.pack("<H", RING))
        ds = GAME_DS * 16
        for ptr, seg in ((0x19C9, CREATURES), (0x19C1, ITEMS), (0x19CD, TYPES), (0x19C5, SHEETS)):
            mu.mem_write(ds + ptr, struct.pack("<HH", 0, seg))
        mu.mem_write(SHEETS * 16 + SHEET * 0x48, self.sheets[kinds])
        for c in range(40):  # (every combatant a creature of its number, standing, Okay, on the foes' side 8)
            mu.mem_write(FIGHTERS + c * 3, bytes((2,)) + struct.pack("<H", c))
            self.creature(mu, c, hp=10, status=1, side=8 if c >= 10 else 0)
            mu.mem_write(DISTANCE * 16 + DIST_TABLE + 2 * c, struct.pack("<H", 5))
        mu.mem_write(CREATURES * 16 + ATTACKER * 0x31 + 4, struct.pack("<H", SHEET))
        # the distance routine (attacker [BP+6], the other [BP+8]): its distance from the table
        mu.mem_write(DISTANCE * 16 + 0x35EF, bytes.fromhex("558bec8b5e08d1e32e8b87") + struct.pack("<H", DIST_TABLE)
                     + bytes.fromhex("5dcb"))
        # the AC routine at the way back + SF_AC_GAP (target [BP+6]): 100 + the target
        ac = OVERLAY * 16 + WAY_BACK + 0x5D520 - 0x5D054
        mu.mem_write(ac, bytes.fromhex("558bec8b46060564005dcb"))
        mu.mem_write(OVERLAY * 16 + WAY_BACK, bytes((0xF4,)))
        mu.mem_write(ds + TARGET, struct.pack("<H", FIRST))
        return mu

    def creature(self, mu, c, hp=None, status=None, side=None):
        at = CREATURES * 16 + c * 0x31
        if hp is not None:
            mu.mem_write(at, struct.pack("<h", hp))
        if status is not None:
            mu.mem_write(at + 0x14, bytes((status,)))
        if side is not None:
            mu.mem_write(at + 0x15, bytes((side,)))

    def frame(self, mu, type_, swings=2, swing=1, item=0, distance=1, ac=7):
        words = {0x0C: ac, 0x10: SHEET, 0x12: item, 0x14: type_, 0x16: distance, 0x18: ATTACKER, 0x20: 0,
                 -0x0A: swings, -0x16: swing, -4: 0}
        for off, v in words.items():
            mu.mem_write(SS * 16 + BP + off, struct.pack("<h", v))

    def regs(self, mu, ip, esp=0x7F0):
        for name, value in dict(cs=TSR, ds=GAME_DS, ss=SS, esp=esp, ebp=BP, eflags=0x2).items():
            mu.reg_write(getattr(r, "UC_X86_REG_" + name.upper()), value)

    def word(self, mu, at):
        return struct.unpack("<h", mu.mem_read(at, 2))[0]

    def header(self, mu, field):
        return self.word(mu, TSR * 16 + self.sym["hdr"] + field)

    def swing(self, mu):
        """CAH_SWING as the game's INT reaches it (its way back the overlay's WAY_BACK): the second foe, if any."""
        mu.mem_write(SS * 16 + 0x7F0, struct.pack("<HHH", WAY_BACK, OVERLAY, 0x2))
        self.regs(mu, 0)
        regs = {n: mu.reg_read(getattr(r, "UC_X86_REG_" + n)) for n in ("EAX", "EBX", "ECX", "EDX", "ESI", "EDI", "ES")}
        mu.emu_start(TSR * 16 + self.sym["cah_swing"], OVERLAY * 16 + WAY_BACK, count=200000)
        self.assertEqual(mu.reg_read(r.UC_X86_REG_SP), 0x7F0 + 6)
        self.assertEqual({n: mu.reg_read(getattr(r, "UC_X86_REG_" + n)) for n in regs}, regs)  # (all kept)
        return self.word(mu, GAME_DS * 16 + TARGET)

    def back(self, mu, ax=2):
        """SF_SITE (site 202) after a swing: AX the swings so far, the flags of "cmp ax,[bp-0Ah]"."""
        mu.mem_write(SS * 16 + 0x7F0, struct.pack("<HHH", 0xFFF0, TSR, 0x2))
        self.regs(mu, 0)
        mu.reg_write(r.UC_X86_REG_EAX, ax)
        mu.emu_start(TSR * 16 + self.sym["sf_site"], TSR * 16 + 0xFFF0, count=100000)
        self.assertEqual(mu.reg_read(r.UC_X86_REG_AX), ax)
        return mu.reg_read(r.UC_X86_REG_EFLAGS)

    def test_site_table(self):
        table = self.sym["site_table"]
        self.assertEqual(struct.unpack_from("<H", self.image, table + 2 * 202)[0], self.sym["sf_site"])
        for number in (191, 200, 201):
            self.assertEqual(struct.unpack_from("<H", self.image, table + 2 * number)[0], self.sym["site_none"])
        hdr = self.sym["hdr"]
        for name, at in (("sf_swings", ravlog.SF_SWINGS), ("sf_lesses", ravlog.SF_LESSES), ("sf_backs", ravlog.SF_BACKS),
                         ("trip_saves", ravlog.TRIP_SAVES), ("trips", ravlog.TRIPS)):
            self.assertEqual(self.sym[name] - hdr, at, name)

    def test_second_foe(self):
        """The round's last swing goes to the first standing foe on the target's side at distance 1, its AC the
        AC routine's; put back by SF_SITE with the compare's flags; recorded and counted."""
        for type_ in (LOTULIS, DOUBLE_SPEAR):
            mu = self.machine()
            mu.mem_write(DISTANCE * 16 + DIST_TABLE + 2 * THIRD, struct.pack("<H", 1))
            mu.mem_write(DISTANCE * 16 + DIST_TABLE + 2 * 5, struct.pack("<H", 1))  # (a friend beside: not a foe)
            self.frame(mu, type_)
            seq = self.header(mu, 8)
            with self.subTest(type=type_):
                self.assertEqual(self.swing(mu), THIRD)
                self.assertEqual(self.word(mu, SS * 16 + BP + 0x0C), 100 + THIRD)
                self.assertEqual(self.header(mu, ravlog.SF_SWINGS), 1)
                self.assertEqual(self.header(mu, 8), seq + 1)
                frame = [self.word(mu, TSR * 16 + self.sym["mn_frame"] + 2 * i) for i in range(4)]
                self.assertEqual(frame, [THIRD, ATTACKER, FIRST, int(type_ == DOUBLE_SPEAR)])
                flags = self.back(mu, ax=2)
                self.assertTrue(flags & 0x40)  # (ZF: 2 swings of 2)
                self.assertEqual(self.word(mu, GAME_DS * 16 + TARGET), FIRST)
                self.assertEqual(self.word(mu, SS * 16 + BP + 0x0C), 7)
                self.assertEqual(self.header(mu, ravlog.SF_BACKS), 1)
                self.assertFalse(self.back(mu, ax=1) & 0x40)  # (again: nothing to put back, the compare's flags)
                self.assertEqual(self.header(mu, ravlog.SF_BACKS), 1)

    def test_no_second_foe(self):
        """None: a swing not the round's last, a round of one, a weapon of another kind, no specialist, a missile,
        the rule off, the foe beside down, out cold or on another side; and none beside at all."""
        cases = {"not the last": dict(swing=0), "one swing": dict(swings=1, swing=0), "long sword": dict(type_=LONG_SWORD),
                 "no item": dict(item=NO_ITEM)}
        for name, kw in cases.items():
            mu = self.machine()
            mu.mem_write(DISTANCE * 16 + DIST_TABLE + 2 * THIRD, struct.pack("<H", 1))
            self.frame(mu, **dict(dict(type_=LOTULIS), **kw))
            with self.subTest(name):
                self.assertEqual(self.swing(mu), FIRST)
        for name, edit in {"down": dict(hp=0), "out cold": dict(status=3), "friend": dict(side=0),
                           "neutral": dict(side=2)}.items():
            mu = self.machine()
            mu.mem_write(DISTANCE * 16 + DIST_TABLE + 2 * THIRD, struct.pack("<H", 1))
            self.creature(mu, THIRD, **edit)
            self.frame(mu, LOTULIS)
            with self.subTest(name):
                self.assertEqual(self.swing(mu), FIRST)
        for name, mu in {"not a specialist": self.machine(kinds=("long sword",)),
                         "rule off": self.machine(rules_hi=0), "none beside": self.machine()}.items():
            if name != "none beside":
                mu.mem_write(DISTANCE * 16 + DIST_TABLE + 2 * THIRD, struct.pack("<H", 1))
            self.frame(mu, LOTULIS)
            with self.subTest(name):
                self.assertEqual(self.swing(mu), FIRST)
                self.assertEqual(self.header(mu, ravlog.SF_SWINGS), 0)

    def test_double_spear_less(self):
        """ENL_ROLL's SF_LESS: the double spear's swing at a second foe 1 less, at least 1; the lotulis' and a
        swing at the first target as rolled."""
        for type_, second, damage, want in ((DOUBLE_SPEAR, True, 6, 5), (DOUBLE_SPEAR, True, 1, 1),
                                            (DOUBLE_SPEAR, False, 6, 6), (LOTULIS, True, 6, 6)):
            mu = self.machine()
            self.frame(mu, type_)
            mu.mem_write(SS * 16 + BP - 4, struct.pack("<h", damage))
            mu.mem_write(TSR * 16 + self.sym["sf_target"], struct.pack("<h", FIRST if second else -1))
            mu.mem_write(SS * 16 + 0x7F0, struct.pack("<HHH", 0xFFF0, TSR, 0x2))
            self.regs(mu, 0)
            mu.reg_write(r.UC_X86_REG_EAX, damage)
            mu.emu_start(TSR * 16 + self.sym["enl_roll"], TSR * 16 + 0xFFF0, count=100000)
            with self.subTest(type=type_, second=second, damage=damage):
                self.assertEqual(self.word(mu, SS * 16 + BP - 4), want)
                self.assertEqual(self.header(mu, ravlog.SF_LESSES), int(want != damage))
                self.assertTrue(mu.reg_read(r.UC_X86_REG_EFLAGS) & 0x40)  # (ENL_ROLL's own compare: 1 with 1)

    def hit(self, mu, type_=TRIKAL, item=0):
        self.frame(mu, type_, item=item)
        mu.mem_write(SS * 16 + 0x7F0, struct.pack("<HHH", 0xFFF0, TSR, 0x2))
        self.regs(mu, 0)
        mu.emu_start(TSR * 16 + self.sym["cah_hit"], TSR * 16 + 0xFFF0, count=200000)
        self.assertEqual(mu.reg_read(r.UC_X86_REG_SP), 0x7F0 + 6)

    def test_trip(self):
        """A trikal specialist's hit: the target (sheet 4) saves against paralysis (+31h; the d20 from the game's
        seed, a 20 always saves); a failure trips it (its next turn lost: TANGLED), recorded MN_TRIP."""
        for need in (21, 1):
            mu = self.machine()
            mu.mem_write(CREATURES * 16 + FIRST * 0x31 + 4, struct.pack("<H", 4))
            save = bytearray(5)
            save[0] = need                   # (paralysis; petrification at +33h left 0)
            mu.mem_write(SHEETS * 16 + 4 * 0x48 + 0x31, bytes(save))
            mu.mem_write(GAME_DS * 16 + SEED, struct.pack("<I", 12345))
            self.hit(mu)
            _, d20 = game_die(12345, 20)
            tripped = d20 != 20 and d20 < need
            frame = [self.word(mu, TSR * 16 + self.sym["mn_frame"] + 2 * i) for i in range(4)]
            bits = bytes(mu.mem_read(TSR * 16 + self.sym["tangled"], 4))
            with self.subTest(need=need):
                self.assertEqual(frame, [FIRST, ATTACKER, d20, need])
                self.assertEqual((self.header(mu, ravlog.TRIP_SAVES), self.header(mu, ravlog.TRIPS)), (1, int(tripped)))
                self.assertEqual(bool(bits[FIRST // 8] & 1 << FIRST % 8), tripped)
                self.assertEqual(self.word(mu, TSR * 16 + self.sym["tangles"]), 0)

    def test_no_trip(self):
        """No save asked: not a specialist, the rule off, another weapon, no item, a target felled."""
        for name, mu, kw in (("not a specialist", self.machine(kinds=("long sword",)), {}),
                             ("rule off", self.machine(rules_hi=0), {}), ("lotulis", self.machine(), dict(type_=LOTULIS)),
                             ("no item", self.machine(), dict(item=NO_ITEM)), ("felled", self.machine(), {})):
            if name == "felled":
                self.creature(mu, FIRST, hp=0)
            self.hit(mu, **kw)
            with self.subTest(name):
                self.assertEqual(self.header(mu, ravlog.TRIP_SAVES), 0)

    def test_trikal_reach(self):
        """REACH_HANDS: ZF with a trikal in the right hand, as with a polearm; not with a long sword or a trikal
        beside another weapon."""
        for types, want in (((TRIKAL,), True), ((POLEARM,), True), ((LONG_SWORD,), False), ((TRIKAL, LONG_SWORD), False)):
            mu = self.machine()
            creature = CREATURES * 16 + ATTACKER * 0x31
            mu.mem_write(creature + 8, struct.pack("<HHH", 0x201, NO_ITEM, NO_ITEM))
            mu.mem_write(FIGHTERS + 0x201 * 3, bytes((1,)) + struct.pack("<H", 5))
            for i, t in enumerate(types):
                item = ITEMS * 16 + (5 + i) * 0x17
                mu.mem_write(item + 4, struct.pack("<H", 6 + i if i + 1 < len(types) else NO_ITEM))
                mu.mem_write(item + 0x0A, struct.pack("<H", t))
                mu.mem_write(item + 0x13, bytes((3 if i == 0 else 10,)))
                mu.mem_write(TYPES * 16 + t * 0x0F, bytes((1,)) + bytes(14))
            mu.mem_write(SS * 16 + 0x7F0, struct.pack("<H", 0xFFF0))
            self.regs(mu, 0)
            mu.reg_write(r.UC_X86_REG_EAX, ATTACKER)
            mu.emu_start(TSR * 16 + self.sym["reach_hands"], TSR * 16 + 0xFFF0, count=100000)
            with self.subTest(types=types):
                self.assertEqual(bool(mu.reg_read(r.UC_X86_REG_EFLAGS) & 0x40), want)


class RangeTests(unittest.TestCase):
    def test_double_spear_range(self):
        """RAV_RANGES: the double spear's +6 2 made 1 in ALL 4 and the objects' copies; RAV_SKIP=melee_range,
        or a byte not SSI's, leaves it."""
        from dsloader import dataitems
        from test_ravtransfer import _gff
        table = bytearray(ravager.GAME_TYPES * ravager.TYPE_SIZE)
        for k, (ssi, _) in ravager.RAV_WEIGHTS.items():
            table[k * 15 + ravager.TYPE_WEIGHT] = ssi
        table[39 * 15 + ravager.TYPE_RANGE] = 2
        table[22 * 15 + ravager.TYPE_RANGE] = 2   # (another type's 2 kept: not a weapon of the Loader's)
        recs = [dataitems.Record(3, 0, 4, 39, 5, bytes(table[39 * 15:40 * 15]))]
        chunk = dataitems.chunk(recs, dataitems.HEADER.pack(dataitems.END, 0, 0, 0, 0, 0))
        data = _gff({("ALL ", 4): bytes(table), ("RDFF", 5): chunk})
        out, done = ravager.objects_fixed(data, {"mod_types"})
        got = gff.read_gff(out)
        self.assertIn("melee_range", done)
        self.assertEqual((got[("ALL ", 4)][39 * 15 + 6], got[("ALL ", 4)][22 * 15 + 6]), (1, 2))
        self.assertEqual(dataitems.records(got[("RDFF", 5)])[0][0].data[6], 1)
        out, done = ravager.objects_fixed(data, {"mod_types", "melee_range"})
        self.assertEqual(gff.read_gff(out)[("ALL ", 4)][39 * 15 + 6], 2)
        self.assertNotIn("melee_range", done)
        self.assertEqual(ravager.ranged(bytes(15), 39), bytes(15))

    @unittest.skipUnless(WOTR and os.path.isfile(os.path.join(WOTR or "", "DSUN.EXE")), "DSUN_WOTR not set")
    def test_in_the_game(self):
        """The site's bytes at 5D308h in the game's program, the double spear's range 2 and the trikal's 1 in its
        OBJEX.GFF, the lotulis', double spear's and trikal's kinds in DSCLOG2's table."""
        exe = open(os.path.join(WOTR, "DSUN.EXE"), "rb").read()
        self.assertEqual(exe[0x5D308:0x5D30B], bytes.fromhex("3b46f6"))
        self.assertEqual(exe[0x5D520:0x5D523], bytes.fromhex("558bec"))   # (the AC routine)
        self.assertEqual(exe[0x5C9A7:0x5C9AA], bytes.fromhex("e8760b"))   # (the set-up's call of it)
        types = gff.read_gff(open(os.path.join(WOTR, ravager.OBJECTS_FILE), "rb").read())[ravager.TYPES_CHUNK]
        self.assertEqual([types[t * 15 + 6] for t in (39, 61, 100)], [2, 1, 1])
        kinds = ravager.rav_kinds()
        self.assertEqual([kinds[t] for t in (61, 39, 100)], [K("lotulis"), K("double spear"), K("trikal")])


if __name__ == "__main__":
    unittest.main()
