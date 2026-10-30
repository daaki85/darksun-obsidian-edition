"""The new spells (game.NEW_SPELLS): the dice log's line for Cat's Grace's 1d6, their names, who knows
them (the sheet's bits), and the rule's setting under its earlier name."""

import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import dicelog, game, kits
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

    def test_cha_for_friends(self):
        log = make_game()
        log.rules = game.RULE_NEW_SPELLS
        args = words(0, 0, 0, 0, 0, 0, game.FRIENDS_SPELL)
        for face in (3, 4):  # (Strength's code rolls Friends' 2d4)
            lines = log.describe(entry(raw_for(face, 4), dicelog.DICE_SITE, words(0, 0, 2, 4), args,
                                       parent_code=dicelog.STRENGTH_ROLL_RETURN), now=1.0)
        self.assertTrue(lines[-1].startswith("Friends: 2d4 = [3 + 4] = 7 -> ")
                        and lines[-1].endswith("'s CHA +7 while it lasts (at most 25)"), lines)


class NewSpellTests(unittest.TestCase):
    def test_names(self):
        log = make_game()
        self.assertEqual([log.game.spell_name(s) for s in range(196, 202)],
                         ["Cat's Grace", "Erdlu Claw", "Fogbolt", "Reflected Image", "Spook", "Friends"])
        self.assertTrue(game.cast_spell(197) and game.cast_spell(201) and game.cast_spell(5)
                        and game.cast_spell(202) and game.cast_spell(211)  # (the 6th-level priest spells)
                        and not game.cast_spell(180) and not game.cast_spell(212))
        self.assertEqual([log.game.spell_name(s) for s in (202, 206, 210)], ["Heal", "Sunstroke", "Whirlwind"])

    def test_known_bits(self):
        """Each new spell's bit: +45h's (but its low three bits, the second sphere), Friends' the kit
        byte's top one, none while that byte is 0FFh (no kit chosen)."""
        sheet = bytearray(game.SHEET_SIZE)
        sheet[0x45], sheet[0x43] = 0x10 | 0x08 | 0x80 | 3, 0x80 | 1
        self.assertEqual([game.knows_new_spell(bytes(sheet), n) for n in range(196, 202)],
                         [True, False, False, True, True, True])
        sheet[0x43] = 0xFF
        self.assertFalse(game.knows_new_spell(bytes(sheet), game.FRIENDS_SPELL))
        self.assertEqual(sheet[0x45] & kits.SPHERE2_MASK, 3)

    def test_spook_penalty(self):
        self.assertEqual([kits.spook_penalty(n) for n in (0, 1, 2, 5, 11, 12, 20)], [0, 0, -1, -2, -5, -6, -6])
        self.assertEqual(kits.spook_penalty(0, 10), -2)  # (a Shinobi of thief level 10 casts at 5th)
        self.assertEqual(kits.spook_penalty(6, 10), -3)

    def test_shinobi_spells(self):
        self.assertIn((game.REFLECT_SPELL, 1), kits.SHINOBI_SPELLS)
        self.assertIn((game.SPOOK_SPELL, 1), kits.SHINOBI_SPELLS)
        self.assertIn((game.FRIENDS_SPELL, 1), kits.SHINOBI_SPELLS)

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
