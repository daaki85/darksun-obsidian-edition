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
            "  Guard takes 7 from Magic Missile, now 3/10 HP",
        ])
        self.assertEqual(t.end(), [
            "Fight over: 2 rounds, 1 kill; the party dealt 28 damage and took 6",
            "    Seneca: 1 of 1 attacks hit, 21 dealt, 1 kill",
            "    Jenna: 0 of 1 attacks hit, took 6",
        ])
        self.assertEqual(t.end(), [])  # (afresh: nothing until a round)

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
