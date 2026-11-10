"""AD&D's held target (game.RULE_HELD; DSCLOG's HELD): a blow on a Paralyzed or Out Cold target hits
automatically (HELD_HIT, 589E9h) and does normal damage (HELD_DAMAGE, 58B0Dh), where the game rolls the
d20 as ever and doubles the damage; both sites run in Unicorn at the game's bytes."""
import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import game, gamepatch  # noqa: E402

import test_cahulaks as tc  # noqa: E402
import test_dsclog as td  # noqa: E402

try:
    from unicorn import x86_const as r
except ImportError:  # pragma: no cover
    r = None

SS, BP = td.SS, td.BP
RULE = 32768  # RULES_HI's RULE_HI_HELD
PARALYZED, OUT_COLD = 34, 3


def load_tests(loader, tests, pattern):
    suite = loader.loadTestsFromTestCase(LoaderTests)
    suite.addTests(HeldTests(name) for name in sorted(vars(HeldTests)) if name.startswith("test_"))
    return suite


class LoaderTests(unittest.TestCase):
    def test_rule(self):
        self.assertEqual(game.RULE_HELD >> 16, RULE)
        self.assertIn(("held_hit", game.RULE_HELD), game.RULE_SETTINGS)
        self.assertTrue(game.rules_from_settings({}) & game.RULE_HELD)  # (on unless unticked)
        self.assertEqual(game.PARALYZED_EFFECT, PARALYZED)

    def test_patches(self):
        for name, offset, original, site in (("held_hit", 0x589E9, "837efa14", gamepatch.HELD_HIT_SITE),
                                             ("held_damage", 0x58B0D, "8b46fcd1e0", gamepatch.HELD_DAMAGE_SITE)):
            p = next(x for x in gamepatch.PATCHES if x.name == name)
            self.assertEqual((p.offset, p.original.hex()), (offset, original))
            self.assertEqual(p.replacement, bytes((0xCD, 0x98, site)) + b"\x90" * (len(original) // 2 - 3))
        self.assertEqual((gamepatch.HELD_HIT_SITE, gamepatch.HELD_DAMAGE_SITE),
                         (gamepatch.NS_IMAGE + 108, gamepatch.NS_IMAGE + 109))


@unittest.skipIf(td.Uc is None, "unicorn not installed")
class HeldTests(tc.CahulaksTests):
    def held(self, d20, rules=RULE, effects=(), out_cold=False, thing=20, creature=9):
        """HELD_HIT with the d20 at [BP-6]: whether the JE after it goes to the hit (ZF)."""
        self.rules_hi(rules)
        self.target(thing=thing, creature=creature)
        self.effects(*effects)
        self.mu.mem_write(tc.CREATURES * 16 + creature * 0x3A + 0x1C, bytes([OUT_COLD if out_cold else 1]))
        self.frame(m6=d20)
        self.assertEqual(self.where("held_hit", ()), "end")
        return bool(self.mu.reg_read(r.UC_X86_REG_EFLAGS) & 0x40)

    def test_the_games_twenty(self):
        """The game's own test kept: a 20 goes to the hit, anything else on, rule or not."""
        for rules in (0, RULE):
            self.assertTrue(self.held(20, rules))
            for d20 in (1, 2, 19):
                self.assertFalse(self.held(d20, rules), (rules, d20))

    def test_held_hit_automatically(self):
        """With the rule a Paralyzed target (its effect 34) or an Out Cold one (its creature's +1Ch 3) is
        hit whatever the d20, a 1 too; another's Paralyzed or another effect doesn't count; nothing
        without the rule."""
        held = ((20, PARALYZED),)
        for d20 in (1, 7, 19):
            self.assertTrue(self.held(d20, effects=held), d20)
            self.assertTrue(self.held(d20, out_cold=True), d20)
            self.assertFalse(self.held(d20, rules=0, effects=held), d20)
            self.assertFalse(self.held(d20, rules=0, out_cold=True), d20)
        self.assertFalse(self.held(5, effects=((21, PARALYZED),)))  # (someone else held)
        self.assertFalse(self.held(5, effects=((20, 16),)))         # (Enlarged: not helpless)
        self.assertTrue(self.held(5, effects=((3, 4), (20, 2), (20, PARALYZED), (22, PARALYZED))))

    def test_damage(self):
        """HELD_DAMAGE: AX what a helpless target takes, the damage x2 the game's way, the damage with the
        rule; [BP-4] unchanged."""
        for rules, want in ((0, 26), (RULE, 13)):
            self.rules_hi(rules)
            self.frame(m4=13)
            self.assertEqual(self.where("held_damage", (), eax=0xBEEF), "end")
            self.assertEqual(self.mu.reg_read(r.UC_X86_REG_AX), want)
            self.assertEqual(struct.unpack("<h", self.mu.mem_read(SS * 16 + BP - 4, 2))[0], 13)


if __name__ == "__main__":
    unittest.main()
