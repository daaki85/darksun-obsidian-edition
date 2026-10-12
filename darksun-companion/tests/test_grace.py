"""The new spells (game.NEW_SPELLS): the dice log's line for Cat's Grace's 1d6, their names, who knows
them (the sheet's bits), and the rule's setting under its earlier name."""

import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dscompanion import dicelog, game, kits
from test_dicelog import entry, make_game, raw_for, words


class LogTests(unittest.TestCase):
    def roll(self, log, spell, face):
        # Strength's code rolls 1d6; its caller's arguments: target at +6, spell at +0Eh
        return log.describe(entry(raw_for(face, 6), dicelog.DICE_SITE, words(0, 0, 1, 6),
                                  words(0, 0, 0, 0, 0, 0, spell), parent_code=dicelog.STRENGTH_ROLL_RETURN),
                            now=1.0)

    def test_dex_for_cats_grace(self):
        log = make_game()
        log.rules = game.RULE_NEW_SPELLS
        line = self.roll(log, game.GRACE_SPELL, 4)[-1]
        self.assertTrue(line.endswith("'s DEX +4 while it lasts (at most 24)"), line)
        self.assertIn("Cat's Grace", line)
        line = self.roll(log, game.STRENGTH_SPELL, 5)[-1]
        self.assertTrue(line.endswith("'s STR +5 while it lasts (at most 24)"), line)


class NewSpellTests(unittest.TestCase):
    def test_names(self):
        log = make_game()
        self.assertEqual([log.game.spell_name(s) for s in (196, 197, 198)], ["Cat's Grace", "Erdlu Claw", "Fogbolt"])
        self.assertTrue(game.cast_spell(197) and game.cast_spell(5) and not game.cast_spell(180))

    def test_old_setting(self):
        self.assertFalse(game.rules_from_settings({"cats_grace": False}) & game.RULE_NEW_SPELLS)
        self.assertTrue(game.rules_from_settings({}) & game.RULE_NEW_SPELLS)
        self.assertTrue(game.rules_from_settings({"cats_grace": False, "new_spells": True}) & game.RULE_NEW_SPELLS)

    def test_second_sphere_beside_the_bits(self):
        sheet = bytearray(game.SHEET_SIZE)
        sheet[kits.SPHERE2] = 0x50 | 3
        self.assertEqual(kits.second_sphere(kits.ELEMENTALIST, bytes(sheet)), 2)


if __name__ == "__main__":
    unittest.main()
