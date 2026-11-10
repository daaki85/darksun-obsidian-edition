"""The cahulaks' rule (game.RULE_CAHULAKS; DSCLOG's CAHULAKS): its three sites run in Unicorn at the
game's bytes (CAH_TWO, CAH_SWING, CAH_HIT), the off head's attack (CAH_MORE in OFF_HAND_HALVES), and
the Loader's list of the creatures too big to tangle (cahulaks.py)."""
import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import cahulaks, game, gamepatch  # noqa: E402

import test_dsclog as td  # noqa: E402
import test_group4 as tg  # noqa: E402
import test_dsclog_drawing as tdd  # noqa: E402

try:
    from unicorn import x86_const as r
except ImportError:  # pragma: no cover
    r = None

GAME_DS, SS, CALLER, TSR, BP, IF = td.GAME_DS, td.SS, td.CALLER, td.TSR, td.BP, td.IF
CREATURES = tg.CREATURES
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
        self.assertIn(("cahulaks", game.RULE_CAHULAKS), game.RULE_SETTINGS)

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
        jle, 5963Eh); one weapon, the cahulaks, on too with the rule."""
        skip = 0x5963E - 0x5962A
        self.item(4, CAH)
        self.item(7, 81)
        for rules, ready, item, want in ((0, 2, 7, "end"), (0, 1, 7, skip), (0, 1, 4, skip),
                                        (RULE, 1, 4, "end"), (RULE, 1, 7, skip), (RULE, 2, 7, "end"),
                                        (RULE, 1, 0x270F, skip)):
            self.rules_hi(rules)
            self.frame(p6=ready, pA=item)
            self.assertEqual(self.where("cahulaks_two", (skip,)), want, (rules, ready, item))

    def test_off_head_swing(self):
        """CAH_SWING: [BP-4] zeroed as the game's; the round's last swing ([BP-14h] = [BP-8] - 1, of 2
        or more) with the cahulaks in melee, by the attacker PROBE_TWO worked out (CAH_WHO), pays
        CAH_EXTRA more in [BP+0Ah], once; any other swing, weapon or attacker as it was."""
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
        self.assertEqual(swing(extra=1, index=2, swings=3), 13)
        for change in (dict(rules=0), dict(index=0), dict(swings=1, index=0), dict(kind=81), dict(reach=2),
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
        blow felled, nor without the rule, another weapon or a missile."""
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
        for thing, change, setup in ((23, dict(rules=0), {}), (24, dict(kind=81), {}), (25, dict(reach=2), {}),
                                     (26, {}, dict(race=game.RACE_HALF_GIANT)), (27, {}, dict(hp=0))):
            self.target(thing=thing, pp=12, **setup)
            self.assertFalse(self.hit(2, **change), (change, setup))
            self.assertFalse(self.swept(thing))
        self.target(thing=28, pp=12)
        self.big(28)
        self.assertFalse(self.hit(2))
        self.assertFalse(self.swept(28))
        self.big(28, False)
        self.assertTrue(self.hit(2))
        self.assertTrue(self.swept(28))

    def test_off_head_attacks(self):
        """CAH_MORE (OFF_HAND_HALVES's first): 2 more halves (one attack a round) for the cahulaks with the
        rule; other weapons, and without it, as they were (the two-weapon rule off: its own cap none)."""
        hdr = self.hdr
        self.mu.mem_write(hdr + 170, struct.pack("<H", 0))  # (RULES: two weapons off)
        self.item(4, CAH)
        self.item(7, 81)
        at = self.sym["off_hand_halves"]
        stub = TSR * 16 + 0xFFF0  # (a far stub in the helper's segment: a near call to it, RETF)
        self.mu.mem_write(stub, bytes((0xE8,)) + struct.pack("<H", (at - (0xFFF0 + 3)) & 0xFFFF) + b"\xcb")
        for rules, item, halves, want in ((RULE, 4, 2, 4), (RULE, 4, 3, 5), (RULE, 7, 2, 2), (0, 4, 2, 2)):
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
