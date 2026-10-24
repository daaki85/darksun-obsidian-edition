"""Tests for spellbook.py: the Spells tab's text, from hand-made spell records."""

import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import game, kits, spellbook
from dsloader.game import SpellDamage, SpellRules


class StubGame:
    def __init__(self, damage=None, rules=None, negates=False, name="Spell", game_rules=0):
        self.damage, self.spell, self.negates, self.name = damage, rules, negates, name
        self.rules = game_rules  # the Loader's rule changes (game.RULE_*)

    def spell_damage(self, spell):
        return self.damage

    def spell_rules(self, spell):
        return self.spell

    def save_negates_damage(self, spell):
        return self.negates

    def spell_name(self, spell):
        return self.name


def record(dice=0, per_level=0, unit=0, effect=0, kinds=0, save=0):
    rec = bytearray(32)
    rec[4] = dice
    struct.pack_into("<Hh", rec, 5, per_level, unit)
    struct.pack_into("b", rec, 0x19, effect)
    struct.pack_into("<H", rec, 0x1A, kinds)
    rec[0x1F] = save
    return bytes(rec)


class PriestSixStub(StubGame):
    def spell_record(self, spell):
        return record(dice=4, kinds=0x900, save=(3 << 5) | 1)  # (Slay Living's kind: 4d8 draining/death)

    def effect_caster_level(self, creature, spell):
        return 0


class TextTests(unittest.TestCase):
    def test_sixth_level_lines_by_hand(self):
        # Heartseeker's record (Slay Living's) would read as dice halved by a save, not the death on
        # a failed one: its own lines say both, the rest are still read from the record
        gd = PriestSixStub(SpellDamage(0, 4, 0, 1, 0, 8), SpellRules(True, 0, "spell"), name="Heartseeker")
        info = spellbook.spell_info(gd, game.HEARTSEEKER_SPELL, [])
        self.assertEqual((info.magic, info.level, info.damage), ("Priest", 6, "half of 4d8 (2 to 16) to one that saves"))
        self.assertIn("one that fails it dies", info.save)
        self.assertTrue(set(spellbook.OWN_LINES) <= set(game.PRIEST6_SPELLS))
        for lines in spellbook.OWN_LINES.values():
            self.assertTrue(set(lines) <= {"damage", "save", "effect", "lasts"})

    def test_fireball(self):
        gd = StubGame(SpellDamage(0, 1, 0, 1, 0, 6), SpellRules(True, 0, "fire"))
        rec = record(kinds=0x202, save=(4 << 5) | 1)
        self.assertEqual(spellbook.damage_text(gd, 27, rec),
                         "1d6 for each caster level, counting at most level 10 [fire]")
        self.assertEqual(spellbook.save_text(gd, 27, rec, True),
                         "petrification/polymorph, d20 doubled (against fire); saving halves the damage")
        self.assertEqual(spellbook.lasts_text(gd, 27, rec), "")  # instant

    def test_spell_save_rule(self):
        """Kind 5, what almost every spell has: petrification/polymorph, or with the Loader's
        rule the spell save. Kind 1 stays paralysis/poison/death."""
        rec = record(save=(5 << 5) | 1)
        self.assertEqual(spellbook.save_text(StubGame(), 1, rec, False), "petrification/polymorph")
        self.assertEqual(spellbook.save_text(StubGame(game_rules=game.RULE_SPELL_SAVE), 1, rec, False), "spell")
        self.assertEqual(spellbook.save_text(StubGame(game_rules=game.RULE_SPELL_SAVE), 1,
                                             record(save=(1 << 5) | 1), False), "paralysis/poison/death")

    def test_durations_and_charges(self):
        gd = StubGame(SpellDamage(0, 0, 0, 1, 0, 0))
        self.assertEqual(spellbook.lasts_text(gd, 1, record(per_level=5, unit=60)), "5 rounds for each caster level")
        self.assertEqual(spellbook.lasts_text(gd, 1, record(dice=0x42, unit=60)), "2d4 rounds")
        self.assertEqual(spellbook.lasts_text(gd, 1, record(per_level=1, dice=0x41, unit=-1)),
                         "1 charge for each caster level + 1d4 charges")
        self.assertEqual(spellbook.lasts_text(gd, 1, record(per_level=1, unit=600)),
                         "(1 for each caster level) x 10 rounds")
        self.assertEqual(spellbook.lasts_text(gd, 1, record(unit=-9999)), "until removed")

    def test_effects_and_no_save(self):
        self.assertEqual(spellbook.effect_text(record(effect=7)), "Blessed: +1 to hit, +1 on saves")
        self.assertEqual(spellbook.effect_text(record(effect=-17)), "removes Afraid")
        self.assertEqual(spellbook.save_text(StubGame(), 1, record(save=(6 << 5) | 1), False), "none")

    def test_flat_bonus(self):
        """A step of a flat bonus that comes once whatever the level (the patched Cause Serious and
        Critical Wounds, gamepatch's cause_*): shown as the dice plus the bonus."""
        from dsloader import gamepatch
        for name, want in (("cause_serious", "2d8+1"), ("cause_critical", "3d8+3")):
            b0, b1, b2 = next(p for p in gamepatch.PATCHES if p.name == name).replacement
            rule = SpellDamage(b1 >> 3, b0 >> 5, b0 & 0x1F, (b1 & 7) or 1, b2 >> 4, b2 & 0x0F)
            self.assertTrue(rule.flat())
            self.assertEqual([rule.steps(level) for level in (1, 6, 7, 10, 15)], [1] * 5)
            self.assertEqual(spellbook.damage_text(StubGame(rule), 113, record()), want)
        self.assertFalse(SpellDamage(1, 0, 1, 2, 0, 4).flat())  # (Magic Missile's +1 a step: grows)

    def test_own_dice_noted(self):
        gd = StubGame(SpellDamage(1, 1, 1, 2, 0, 4), name="Magic Missile")
        self.assertIn("its own code", spellbook.damage_text(gd, 3, record(kinds=0x200)))


class PowerNameTests(unittest.TestCase):
    """A monster's power has no name in the game: the log names it by the effect it puts on, else
    its damage dice and kinds."""

    def gd(self, damage, kinds, effect=0):
        gd = object.__new__(game.GameData)
        gd.spell_damage = lambda spell: damage
        gd.spell_record = lambda spell: bytes(0x19) + struct.pack("<bH", effect, kinds)
        return gd

    def test_dice_and_kinds(self):
        gd = self.gd(SpellDamage(1, 0, 0, 1, 0, 10), 0x08)
        self.assertEqual(gd.spell_name(195), "Detonate's blast (1d10 crushing)")
        self.assertEqual(gd.spell_name(194), "Crushing attack (1d10 crushing)")
        gd = self.gd(SpellDamage(1, 0, 0, 1, 0, 6), 0x20)
        self.assertEqual(gd.spell_name(180), "Piercing attack (1d6 pointed)")

    def test_effect(self):
        # (the Red Slaad's: paralysed for 2d4 rounds unless saved against; its dice are the time)
        gd = self.gd(SpellDamage(2, 0, 0, 1, 0, 4), 0, effect=34)
        self.assertEqual(gd.spell_name(182), "Paralysing attack")
        self.assertEqual(self.gd(None, 0, effect=13).spell_name(184), "Disease attack")

    def test_no_dice(self):
        gd = self.gd(None, 0)
        self.assertEqual(gd.spell_name(190), "special attack 190")
        gd = self.gd(SpellDamage(1, 1, 0, 1, 0, 6), 0x02)  # grows with level: no fixed dice to show
        self.assertEqual(gd.spell_name(190), "special attack 190")


class DamageHalvedTests(unittest.TestCase):
    """Resist Fire and the like halve a spell's damage when it is all of their kind (7B4C0h)."""

    def gd(self, kinds, effects, kit=None):
        gd = object.__new__(game.GameData)
        gd.combatant_creature = lambda combatant: combatant
        gd.kit_ids = lambda index: [kit] if kit is not None and index == 3 else []
        gd.spell_record = lambda spell: bytes(0x1A) + struct.pack("<H", kinds) + bytes(game.SPELL_SIZE - 0x1C)
        gd.effects = lambda: [game.Effect(owner, 0, eff) for owner, eff in effects]
        return gd

    def test_halved(self):
        fire = [(3, game.EFFECT_PROT_FIRE)]
        self.assertEqual(self.gd(0x02, fire).damage_halved_by(3, 27), "Prot Fire")
        self.assertEqual(self.gd(0x202, fire).damage_halved_by(3, 27), "Prot Fire")  # (magic aside)
        self.assertIsNone(self.gd(0x02, fire).damage_halved_by(4, 27))  # someone else's
        self.assertIsNone(self.gd(0x04, fire).damage_halved_by(3, 27))  # cold
        self.assertIsNone(self.gd(0x0A, fire).damage_halved_by(3, 27))  # fire and crushing
        both = [(3, game.EFFECT_FIRE_SHIELD)]
        self.assertEqual(self.gd(0x06, both).damage_halved_by(3, 27), "Fire Shield")
        # a Wanderer, as by Resist Fire and Resist Cold (the patched game's WANDER_DMG)
        self.assertEqual(self.gd(0x04, [], kits.WANDERER).damage_halved_by(3, 27), "Wanderer")
        self.assertIsNone(self.gd(0x80, [], kits.WANDERER).damage_halved_by(3, 27))


if __name__ == "__main__":
    unittest.main()
