"""The cahulaks' rule (game.RULE_CAHULAKS; DSCLOG's CAHULAKS): its three sites run in Unicorn at the
game's bytes (CAH_TWO, CAH_SWING, CAH_HIT), the off head's attack (CAH_MORE in OFF_HAND_HALVES), and
the Loader's list of the creatures too big to tangle (cahulaks.py)."""
import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import cahulaks, game, gamepatch, specialize  # noqa: E402

import test_dsclog as td  # noqa: E402
import test_group4 as tg  # noqa: E402
import test_dsclog_drawing as tdd  # noqa: E402

try:
    from unicorn import x86_const as r
except ImportError:  # pragma: no cover
    r = None

GAME_DS, SS, CALLER, TSR, BP, IF = td.GAME_DS, td.SS, td.CALLER, td.TSR, td.BP, td.IF
CREATURES, SHEETS = tg.CREATURES, tg.SHEETS
CAH = 21                    # the cahulaks' item type
ITEMS = 0xC000              # (the items here: group 4's sheets are where RingTests' items are)
RULE = 8192                 # RULES_HI's RULE_HI_CAHULAKS


def load_tests(loader, tests, pattern):  # (only this file's: not group 4's, inherited, again)
    suite = loader.loadTestsFromTestCase(LoaderTests)
    suite.addTests(CahulaksTests(name) for name in sorted(vars(CahulaksTests)) if name.startswith("test_"))
    return suite


class LoaderTests(unittest.TestCase):
    def test_rule(self):
        self.assertEqual(game.RULE_CAHULAKS >> 16, RULE)
        self.assertIn(("cahulaks", game.RULE_CAHULAKS), game.RULE_SETTINGS_GONE)  # (always on: game.RULES_ALWAYS)

    def test_big_table(self):
        """A bit for each combatant that can't be tangled: too big by sizes.py (by race and name: the
        monster Guard, not a human one), shapeless, or kept from it; a half-giant too."""
        names = ["Cermak", "Bulette", "Slig", "Tyrian Slime", "Wyvern", "Djinn", "Guard", "Guard", "Gerakis", "Xorn"]
        races = [1, 12, 14, 12, 13, 14, 12, 1, 5, 12]
        class Gd:
            def combatants(self):
                return {0: 0, 5: 1, 9: 2, 300: 3, 519: 4, 520: 5, 30: 6, 31: 7, 1: 8, 40: 9}
            def creature_name(self, creature):
                return names[creature]
            def sheet(self, creature):
                return bytes(0x18) + bytes([races[creature]]) + bytes(0x2E)
        table = cahulaks.big_table(Gd())
        self.assertEqual(len(table), cahulaks.BIG_BYTES)
        bits = {n for n in range(cahulaks.MAP_COUNT) if table[n // 8] >> (n % 8) & 1}
        self.assertEqual(bits, {5, 300, 519, 30, 1, 40})  # (520: past the map things)
        self.assertTrue(cahulaks.UNTANGLED.isdisjoint(cahulaks.SHAPELESS))

    def test_shadows_shapeless(self):
        """The Shadow and the greater shadows, the same kind of being, have nothing to tangle."""
        for name in ("Shadow", "Shadow Guard", "Shadow King", "Shadow Prince", "Shadow Worker", "Cragg",
                     "Tanelyv", "Tristram", "Tynan"):
            self.assertEqual(cahulaks.why_not(name, 9), "nothing to tangle", name)

    @unittest.skipUnless(os.environ.get("DSUN_OBJECTS"), "DSUN_OBJECTS (the game's SEGOBJEX.GFF) not given")
    def test_shadow_kinds_in_data(self):
        """Every creature of the shadows' kinds (monsters.SHADOW_KIND, GREATER_SHADOW_KIND) with a figure
        in the creatures' table is shapeless."""
        from dsloader import doccreatures, gff, monsters
        with open(os.environ["DSUN_OBJECTS"], "rb") as f:
            chunks = gff.read_gff(f.read())
        shown = {c.obj for c in doccreatures.creatures(chunks)}
        found = set()
        for (kind, obj), data in chunks.items():
            if kind != "RDFF" or obj not in shown:
                continue
            if struct.unpack_from("<H", data, monsters.RDFF_CREATURE + monsters.CREATURE_KIND)[0] in (
                    monsters.SHADOW_KIND, monsters.GREATER_SHADOW_KIND):
                at = monsters.RDFF_CREATURE + game.CREATURE_NAME
                found.add(data[at:at + 16].split(b"\0", 1)[0].decode("cp437").strip())
        self.assertGreater(len(found), 5)
        self.assertEqual(found - cahulaks.SHAPELESS, set())


@unittest.skipIf(td.Uc is None, "unicorn not installed")
class CahulaksTests(tg.SiteTests):
    def setUp(self):
        super().setUp()
        _, self.sym = tdd.build()
        self.mu.mem_write(GAME_DS * 16 + 0x165D, struct.pack("<HH", 0, ITEMS))

    def item(self, number, kind):
        self.mu.mem_write(ITEMS * 16 + number * 0x15 + 0x0A, struct.pack("<H", kind))

    def word(self, name, value=None):
        at = TSR * 16 + self.sym[name]
        if value is not None:
            self.mu.mem_write(at, struct.pack("<h", value))
        return struct.unpack("<h", self.mu.mem_read(at, 2))[0]

    def frame(self, **words):
        """[BP+X] words (x as a key: 'p6', 'm8' for +6, -8...)."""
        for key, value in words.items():
            off = int(key[1:], 16) * (1 if key[0] == "p" else -1)
            self.mu.mem_write(SS * 16 + BP + off, struct.pack("<h", value))

    def where(self, name, stops, **regs):
        """PATCH NAME's bytes at a place of their own, HLTs after them and at each of STOPS (offsets on
        from after the site's number): which it stopped at."""
        p = tg.patch(name)
        mu = self.mu
        self.at += 0x100
        start = CALLER * 16 + self.at
        mu.mem_write(start, p.replacement + b"\xf4")
        for stop in stops:
            mu.mem_write(start + 3 + stop, b"\xf4")
        for reg, value in dict(cs=CALLER, ds=GAME_DS, ss=SS, esp=0x800, ebp=BP, eflags=IF | 2, **regs).items():
            mu.reg_write(getattr(r, "UC_X86_REG_" + reg.upper()), value)
        mu.emu_start(start, 0, count=200000)
        self.assertEqual((mu.reg_read(r.UC_X86_REG_SP), mu.reg_read(r.UC_X86_REG_BP)), (0x800, BP))
        at = mu.reg_read(r.UC_X86_REG_IP) - self.at - 1
        return "end" if at == len(p.replacement) else at - 3

    def test_patches(self):
        for name, offset, original, site in (
                ("cahulaks_two", 0x59627, "837e06017e11", gamepatch.CAH_TWO_SITE),
                ("cahulaks_swing", 0x589B6, "c746fc0000", gamepatch.CAH_SWING_SITE),
                ("cahulaks_hit", 0x58B54, "c646eb00", gamepatch.CAH_HIT_SITE)):
            p = tg.patch(name)
            self.assertEqual((p.offset, p.original.hex()), (offset, original))
            self.assertEqual(p.replacement[:3], bytes((0xCD, 0x98, site)))
            self.assertEqual(len(p.replacement), len(p.original))
        self.assertEqual(gamepatch.CAH_HIT_SITE, gamepatch.NS_IMAGE + 105)

    def test_two_weapons_ready(self):
        """CAH_TWO: on (the game's "two weapons ready") with two, else its "none" way (595ECh's
        jle, 5963Eh); one weapon, the cahulaks, on too (the rule always on: its bit clear the same)."""
        skip = 0x5963E - 0x5962A
        self.item(4, CAH)
        self.item(7, 81)
        for rules, ready, item, want in ((0, 2, 7, "end"), (0, 1, 7, skip), (0, 1, 4, "end"),
                                        (RULE, 1, 4, "end"), (RULE, 1, 7, skip), (RULE, 2, 7, "end"),
                                        (RULE, 1, 0x270F, skip)):
            self.rules_hi(rules)
            self.frame(p6=ready, pA=item)
            self.assertEqual(self.where("cahulaks_two", (skip,)), want, (rules, ready, item))

    def test_off_head_swing(self):
        """CAH_SWING: [BP-4] zeroed as the game's; the round's last swing ([BP-14h] = [BP-8] - 1, of 2
        or more) with the cahulaks in melee, by the attacker PROBE_TWO worked out (CAH_WHO), pays
        CAH_EXTRA more in [BP+0Ah], once (the rule's bit clear the same); any other swing, weapon or
        attacker as it was."""
        def swing(rules=RULE, index=1, swings=2, kind=CAH, reach=1, attacker=6, who=6, extra=2):
            self.rules_hi(rules)
            self.word("cah_who", who)
            self.word("cah_extra", extra)
            self.frame(m4=99, m14=index, m8=swings, p14=kind, p16=reach, p18=attacker, pA=12)
            self.assertEqual(self.where("cahulaks_swing", ()), "end")
            self.assertEqual(struct.unpack("<h", self.mu.mem_read(SS * 16 + BP - 4, 2))[0], 0)
            return struct.unpack("<h", self.mu.mem_read(SS * 16 + BP + 0x0A, 2))[0]
        self.assertEqual(swing(), 14)
        self.assertEqual(self.word("cah_who"), -1)  # (once)
        self.assertEqual(swing(rules=0), 14)
        self.assertEqual(swing(extra=1, index=2, swings=3), 13)
        for change in (dict(index=0), dict(swings=1, index=0), dict(kind=81), dict(reach=2),
                       dict(attacker=7), dict(extra=0)):
            self.assertEqual(swing(**change), 12, change)

    def target(self, thing=20, creature=9, hp=10, race=1, pp=12):
        self.combatant(thing, creature)
        self.mu.mem_write(GAME_DS * 16 + 0x494A, struct.pack("<H", thing))
        rec = CREATURES * 16 + creature * 0x3A
        self.mu.mem_write(rec, struct.pack("<h", hp))
        self.mu.mem_write(rec + 4, struct.pack("<H", creature))
        sheet = tg.SHEETS * 16 + creature * 0x47
        self.mu.mem_write(sheet + 0x18, bytes([race]))
        self.mu.mem_write(sheet + 0x39, bytes([pp]))

    def swept(self, thing):
        far, = struct.unpack("<H", self.mu.mem_read(self.hdr + 142, 2))
        byte = self.mu.mem_read(far * 16 + self.sym["FAR_SWEPT"] + thing // 8, 1)[0]
        return bool(byte >> (thing % 8) & 1)

    def big(self, thing, on=True):
        far, = struct.unpack("<H", self.mu.mem_read(self.hdr + 142, 2))
        at = far * 16 + self.sym["FAR_BIG"] + thing // 8
        byte = self.mu.mem_read(at, 1)[0]
        byte = byte | 1 << (thing % 8) if on else byte & ~(1 << (thing % 8))
        self.mu.mem_write(at, bytes([byte]))

    def hit(self, d20, rules=RULE, kind=CAH, reach=1, attacker=6):
        self.rules_hi(rules)
        self.mu.mem_write(GAME_DS * 16 + self.SEED, struct.pack("<I", self.seed_for((d20, 20))))
        self.frame(p14=kind, p16=reach, p18=attacker)
        self.mu.mem_write(SS * 16 + BP - 0x15, b"\x63")
        before = self.seq()
        self.assertEqual(self.where("cahulaks_hit", ()), "end")
        self.assertEqual(self.mu.mem_read(SS * 16 + BP - 0x15, 1)[0], 0)
        return self.seq() != before

    def test_tangle(self):
        """CAH_HIT: a hit with the cahulaks that did damage: the target saves against petrification (its
        sheet's +39h, a d20; a 20 saves), recorded (kind 14, 10: target, attacker, d20, needed), and a
        failure marks it SWEPT (its next turn lost); not a half-giant, one the Loader marks BIG, one the
        blow felled, nor an Enlarged one (large, as the size rule has it), nor another weapon or a
        missile; the rule's bit clear the same."""
        self.manual(False)
        self.target(pp=12)
        self.assertTrue(self.hit(11))
        self.assertEqual(self.entry(), (14, 10, 20, 6, 11, 12))
        self.assertTrue(self.swept(20))
        self.target(thing=21, pp=12)
        self.assertTrue(self.hit(12))
        self.assertFalse(self.swept(21))  # (12: saved)
        self.target(thing=22, pp=21)
        self.assertTrue(self.hit(20))
        self.assertFalse(self.swept(22))  # (a 20 saves, whatever is needed)
        self.target(thing=23, pp=12)
        self.assertTrue(self.hit(2, rules=0))
        self.assertTrue(self.swept(23))
        for thing, change, setup in ((24, dict(kind=81), {}), (25, dict(reach=2), {}),
                                     (26, {}, dict(race=game.RACE_HALF_GIANT)), (27, {}, dict(hp=0))):
            self.target(thing=thing, pp=12, **setup)
            self.assertFalse(self.hit(2, **change), (change, setup))
            self.assertFalse(self.swept(thing))
        self.target(thing=29, pp=12, creature=10)
        self.effects((29, 16))  # (Enlarged: large, as the size rule has it)
        self.assertFalse(self.hit(2))
        self.assertFalse(self.swept(29))
        self.effects()
        self.target(thing=28, pp=12)
        self.big(28)
        self.assertFalse(self.hit(2))
        self.assertFalse(self.swept(28))
        self.big(28, False)
        self.assertTrue(self.hit(2))
        self.assertTrue(self.swept(28))

    # ---- the Wake of the Ravager weapons' traits (DSCLOG's TRIKAL AND THE TWO-HEADED WEAPONS) ----

    TRIKAL, LOTULIS, DOUBLE_SPEAR = game.TRIKAL_TYPE, game.LOTULIS_TYPE, game.DOUBLE_SPEAR_TYPE
    SHEET = 3  # (the attacker's sheet: [BP+10h])

    def specialist(self, *kinds):
        """The attacker's sheet: a 3rd-level gladiator specialized in KINDS (kind + 1 each)."""
        sheet = SHEETS * 16 + self.SHEET * 0x47
        self.mu.mem_write(sheet, bytes(0x47))
        self.mu.mem_write(sheet + 0x12, struct.pack("<H", 0x40))
        self.mu.mem_write(sheet + 0x14, game.packed_specs(kinds, 9, 3))
        self.mu.mem_write(sheet + 0x18, bytes((1,)))
        self.mu.mem_write(sheet + 0x21, bytes((game.GLADIATOR_CLASS, 0, 0, 3, 0, 0)))

    def test_trip(self):
        """CAH_HIT: a trikal specialist's hit that did damage trips the target as the cahulaks tangle
        it, but its save is against paralysis (the sheet's +37h): recorded (kind 14, 13: target,
        attacker, d20, needed), a failure SWEPT; not without the trikal spec, nor with another weapon."""
        self.manual(False)
        trikal = 1 + specialize.KINDS.index("trikal")
        self.specialist(trikal)
        self.frame(p10=self.SHEET, p12=0)
        for thing, pp, d20, tripped in ((20, 12, 11, True), (21, 12, 12, False), (22, 21, 20, False)):
            self.target(thing=thing, pp=3)
            self.mu.mem_write(tg.SHEETS * 16 + 9 * 0x47 + 0x37, bytes((pp,)))
            self.assertTrue(self.hit(d20, kind=self.TRIKAL))
            self.assertEqual(self.entry(), (14, 13, thing, 6, d20, pp))
            self.assertEqual(self.swept(thing), tripped, thing)
        self.specialist(1 + specialize.KINDS.index("lotulis"))  # (not the trikal's specialist)
        self.target(thing=23, pp=3)
        self.mu.mem_write(tg.SHEETS * 16 + 9 * 0x47 + 0x37, bytes((12,)))
        self.assertFalse(self.hit(2, kind=self.TRIKAL))
        self.assertFalse(self.swept(23))
        self.specialist(trikal)
        self.target(thing=24, pp=3)
        self.assertFalse(self.hit(2, kind=self.TRIKAL, reach=2))  # (a missile: none)
        self.assertFalse(self.swept(24))

    def foe(self, thing, creature, side, hp=8, status=1):
        self.combatant(thing, creature)
        rec = CREATURES * 16 + creature * 0x3A
        self.mu.mem_write(rec, struct.pack("<h", hp))
        self.mu.mem_write(rec + 0x1C, bytes((status, side)))

    def distance_stub(self, *near):
        """The game's distance routine (1A0A:2BA5h): 1 from the attacker to each of NEAR, else 4 (a
        table the stub reads: its code written once, as Unicorn keeps code it has run)."""
        seg = (GAME_DS - (0x4356 - 0x1A0A)) & 0xFFFF
        at = seg * 16 + 0x2BA5
        # push bp / mov bp,sp / push bx / mov bx,[bp+8] / movzx ax,byte [cs:bx+2BC5h] / pop bx / pop bp / retf
        self.mu.mem_write(at, bytes.fromhex("5589e5538b5e08") + bytes.fromhex("2e0fb687") + struct.pack("<H", 0x2BA5 + 0x20)
                          + bytes.fromhex("5b5dcb"))
        self.mu.mem_write(at + 0x20, bytes(1 if thing in near else 4 for thing in range(64)))

    def swing_at(self, kind, index=1, swings=2, ac=5):
        self.frame(m4=99, m14=index, m8=swings, p14=kind, p16=1, p12=0, pE=6, p10=self.SHEET, pC=ac, pA=12, p18=6)
        self.assertEqual(self.where("cahulaks_swing", ()), "end")
        target, = struct.unpack("<H", self.mu.mem_read(GAME_DS * 16 + 0x494A, 2))
        ac, = struct.unpack("<h", self.mu.mem_read(SS * 16 + BP + 0x0C, 2))
        return target, ac

    def test_second_foe(self):
        """CAH_SWING: a lotulis or double spear specialist's last swing of two or more turns on a second
        foe: the first combatant, other than the target, on the target's side, standing and Okay, the
        game's distance 1 from the attacker; TARGET that foe and [BP+0Ch] its AC (THORNS_AC's: a party
        member's as last seen), recorded (kind 14, 14: foe, attacker, first target, 1 the double spear);
        AMMO_TURN's site puts both back. The double spear's swing at it does 1 less (STAB_ROLL: [BP-4],
        at least 1). Any other swing, weapon, spec or no foe beside: as it was."""
        self.rules_hi(RULE)
        self.manual(False)
        self.mu.mem_write(TSR * 16 + self.sym["ac_seen"] + 2, bytes((3,)))
        self.target(thing=20, creature=9)
        self.mu.mem_write(CREATURES * 16 + 9 * 0x3A + 0x1C, bytes((1, 1)))
        self.foe(1, 10, side=0)              # (beside, but the attacker's own side)
        self.foe(2, 11, side=1)              # (beside, on the target's: the second foe)
        self.foe(30, 12, side=1)             # (on its side, not beside)
        self.distance_stub(1, 2, 20)
        lotulis, spear = 1 + specialize.KINDS.index("lotulis"), 1 + specialize.KINDS.index("double spear")
        self.specialist(lotulis, spear)
        self.assertEqual(self.swing_at(self.LOTULIS), (2, 3))
        self.assertEqual(self.entry(), (14, 14, 2, 6, 20, 0))
        self.assertEqual(self.word("sf_target"), 20)
        self.mu.mem_write(SS * 16 + BP - 4, struct.pack("<h", 5))
        self.assertEqual(self.where("stab_roll", ()), "end")
        self.assertEqual(struct.unpack("<h", self.mu.mem_read(SS * 16 + BP - 4, 2))[0], 5)  # (the lotulis: all of it)
        self.where("ammo_turn", (), eax=2)
        self.assertEqual(struct.unpack("<H", self.mu.mem_read(GAME_DS * 16 + 0x494A, 2))[0], 20)
        self.assertEqual(struct.unpack("<h", self.mu.mem_read(SS * 16 + BP + 0x0C, 2))[0], 5)
        self.assertEqual(self.word("sf_target"), -1)
        # the double spear: the same foe, and 1 less (at least 1)
        self.assertEqual(self.swing_at(self.DOUBLE_SPEAR, index=2, swings=3), (2, 3))
        self.assertEqual(self.entry(), (14, 14, 2, 6, 20, 1))
        for rolled, want in ((5, 4), (1, 1)):
            self.mu.mem_write(SS * 16 + BP - 4, struct.pack("<h", rolled))
            self.assertEqual(self.where("stab_roll", ()), "end")
            self.assertEqual(struct.unpack("<h", self.mu.mem_read(SS * 16 + BP - 4, 2))[0], want)
        self.where("ammo_turn", (), eax=3)
        self.assertEqual(struct.unpack("<H", self.mu.mem_read(GAME_DS * 16 + 0x494A, 2))[0], 20)
        # the metal lotulis (by its kind): as the lotulis
        self.assertEqual(self.swing_at(game.METAL_LOTULIS_TYPE), (2, 3))
        self.assertEqual(self.entry(), (14, 14, 2, 6, 20, 0))
        self.where("ammo_turn", (), eax=2)
        # none of these: the first target kept (a type past the kinds' table too)
        for change in (dict(index=0), dict(swings=1, index=0), dict(kind=81), dict(kind=self.TRIKAL),
                       dict(kind=game.METAL_TWOHAND_SWORD_TYPE), dict(kind=200)):
            self.assertEqual(self.swing_at(**dict(dict(kind=self.LOTULIS), **change)), (20, 5), change)
        self.specialist(1 + specialize.KINDS.index("trikal"))
        self.assertEqual(self.swing_at(self.LOTULIS), (20, 5))  # (not its specialist)
        self.specialist(lotulis)
        self.distance_stub(1, 20)
        self.assertEqual(self.swing_at(self.LOTULIS), (20, 5))  # (no foe beside)
        self.foe(2, 11, side=1, status=2)
        self.distance_stub(1, 2, 20)
        self.assertEqual(self.swing_at(self.LOTULIS), (20, 5))  # (the one beside not Okay)

    def test_off_head_attacks(self):
        """CAH_MORE (OFF_HAND_HALVES's first): 2 more halves (one attack a round) for the cahulaks (the
        rule always on, its bit clear too); other weapons as they were (the two-weapon rule's bit clear)."""
        hdr = self.hdr
        self.mu.mem_write(hdr + 170, struct.pack("<H", 0))  # (RULES: two weapons off)
        self.item(4, CAH)
        self.item(7, 81)
        at = self.sym["off_hand_halves"]
        stub = TSR * 16 + 0xFFF0  # (a far stub in DSCLOG's segment: a near call to it, RETF)
        self.mu.mem_write(stub, bytes((0xE8,)) + struct.pack("<H", (at - (0xFFF0 + 3)) & 0xFFFF) + b"\xcb")
        for rules, item, halves, want in ((RULE, 4, 2, 4), (RULE, 4, 3, 5), (RULE, 7, 2, 2), (0, 4, 2, 4)):
            self.rules_hi(rules)
            self.at += 0x40
            start = CALLER * 16 + self.at
            self.mu.mem_write(start, bytes((0x9A,)) + struct.pack("<HH", 0xFFF0, TSR) + b"\xf4")
            for reg, value in dict(cs=CALLER, ds=GAME_DS, ss=SS, esp=0x800, ebp=BP, eflags=IF | 2,
                                   eax=halves, ebx=item).items():
                self.mu.reg_write(getattr(r, "UC_X86_REG_" + reg.upper()), value)
            self.mu.emu_start(start, 0, count=2000)
            self.assertEqual((self.reg("ax"), self.reg("bx")), (want, item), (rules, item, halves))


if __name__ == "__main__":
    unittest.main()
