"""A fight's tally (fighttally.py): the summary the dice log writes as a fight ends."""
import unittest

from dsloader.fighttally import FightTally

PARTY = {"Seneca", "Jenna", "Lex"}


class FightTallyTests(unittest.TestCase):
    def test_summary(self):
        t = FightTally(PARTY.__contains__)
        t.feed([
            "Round 1: Seneca 29, Guard 24",
            "Seneca attacks Arena Guard BACKSTAB with Bone Hayneedle +1 (1d4+1): d20 = 15, needs 4+ (85%), hits AC -3, target AC 8 -> HIT",
            "    THAC0 19 = 12",
            "  Seneca hits Arena Guard for 11: 1d4 = [3]",
            "Arena Guard's saving throw vs Poison (10 damage) from Seneca (paralysis/poison/death): d20 = 7, needs 13 (40% to save) -> failed",
            "  Arena Guard takes 10 from Poison (10 damage), now 0/30 HP",
            "Arena Guard is killed",
            "Round 2: Jenna 32, Guard 20",
            "Guard attacks Jenna with Bone Spear (1d8): d20 = 15, needs 13+ (40%), hits AC 1, target AC 3 -> HIT",
            "  Guard hits Jenna for 6: 1d8 = [6]",
            "Jenna attacks Guard: d20 = 3, needs 9+ (60%), hits AC 15, target AC 5 -> miss",
            "  Guard takes 7 from Magic Missile, now 3/10 HP",  # (no cast or line named its caster: no one's)
        ])
        self.assertEqual(t.end(), [
            "Fight over: 2 rounds, 1 kill; the party dealt 21 damage and took 6",
            "    Seneca: 1 of 1 attacks hit, 21 dealt, 1 kill",
            "    Jenna: 0 of 1 attacks hit, took 6",
        ])
        self.assertEqual(t.end(), [])  # (afresh: nothing until a round)

    def test_monsters_spells_not_the_partys(self):
        """A monster's spell on its own side (its caster named on a save) is not damage the party
        dealt, nor does a member who cast the same spell earlier get it; a kill after it is no
        member's."""
        t = FightTally(PARTY.__contains__)
        t.feed([
            "Round 1: Lex 20, Mage 18",
            "Guard's saving throw vs Fireball from Lex (petrification/polymorph): d20 = 3, needs 13 -> failed",
            "  Guard takes 12 from Fireball, now 8/20 HP",
            "Guard's saving throw vs Fireball from Mage (petrification/polymorph): d20 = 3, needs 13 -> failed",
            "  Guard takes 9 from Fireball, now 0/20 HP",
            "Guard is killed",
            "Jenna's saving throw vs Fireball from Mage (petrification/polymorph): d20 = 3, needs 13 -> failed",
            "  Jenna takes 5 from Fireball, now 20/25 HP",
        ])
        self.assertEqual(t.end(), [
            "Fight over: 1 round, 1 kill; the party dealt 12 damage and took 5",
            "    Lex: 12 dealt",
            "    Jenna: took 5",
        ])

    def test_spell_attack_names_its_caster(self):
        """A spell's attack roll names its caster: its damage the caster's."""
        t = FightTally(PARTY.__contains__)
        t.feed([
            "Round 1: Lex 20",
            "Lex's Acid Arrow at Templar: attack d20 = 12, needs 4+ (85%) (THAC0 12 (a fighter's of the "
            "caster's level), +4 DEX; target AC 4) -> HIT",
            "  Templar takes 3 from Acid Arrow, now 7/10 HP",
            "Mage's Magical Stone at Templar: attack d20 = 12, needs 4+ (85%) (THAC0 19; target AC 4) -> HIT",
            "  Templar takes 4 from Magical Stone, now 3/10 HP",
        ])
        self.assertEqual(t.end()[:2], ["Fight over: 1 round, 0 kills; the party dealt 3 damage and took 0",
                                       "    Lex: 3 dealt"])

    def test_cast_names_its_caster(self):
        """A cast's record names its caster (cast()): a spell with no save or attack roll, Magic
        Missile, is its caster's; a monster's cast of it is not the party's."""
        t = FightTally(PARTY.__contains__)
        t.feed(["Round 1: Lex 20, Mage 18"])
        t.cast("Lex", "Magic Missile")
        t.feed(["  Guard takes 7 from Magic Missile, now 3/10 HP"])
        t.cast("Mage", "Magic Missile")
        t.feed(["  Templar takes 5 from Magic Missile, now 5/10 HP"])
        t.cast("?", "Magic Missile")  # (a caster with no name now: the last one kept)
        t.feed(["  Jenna takes 4 from Magic Missile, now 21/25 HP"])
        self.assertEqual(t.end(), ["Fight over: 1 round, 0 kills; the party dealt 7 damage and took 4",
                                   "    Lex: 7 dealt", "    Jenna: took 4"])

    def test_spell_named_from(self):
        """A spell whose name has " from " in it: its caster after the last one, or none."""
        t = FightTally(PARTY.__contains__)
        t.feed([
            "Round 1: Lex 20",
            "Guard's saving throw vs Protection from Evil from Lex (spell): d20 = 3, needs 13 -> failed",
            "  Guard takes 2 from Protection from Evil, now 8/10 HP",
            "Guard's saving throw vs Protection from Fire (spell): d20 = 3, needs 13 -> failed",
            "  Guard takes 1 from Protection from Fire, now 7/10 HP",
        ])
        self.assertEqual(t.end()[:2], ["Fight over: 1 round, 0 kills; the party dealt 2 damage and took 0",
                                       "    Lex: 2 dealt"])

    def test_nothing_before_a_round(self):
        t = FightTally(PARTY.__contains__)
        t.feed(["Seneca attacks Guard: d20 = 15, needs 4+ (85%), hits AC -3, target AC 8 -> HIT"])
        self.assertEqual(t.end(), [])

    def test_a_new_fight_untold(self):
        """Round 1 again after later rounds with no end said: the tally starts afresh."""
        t = FightTally(PARTY.__contains__)
        t.feed(["Round 1: Seneca 29", "Round 2: Seneca 29", "Guard is killed", "Round 1: Seneca 30"])
        self.assertEqual(t.end()[0], "Fight over: 1 round, 0 kills; the party dealt 0 damage and took 0")


if __name__ == "__main__":
    unittest.main()
