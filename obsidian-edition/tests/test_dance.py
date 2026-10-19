"""A Battle Dancer's dance (dance.py): rolled as a fight's first round begins, counted down."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from types import SimpleNamespace  # noqa: E402

from dsloader import dance, dicelog, game, kits, wild  # noqa: E402


class FakeGd:
    """Party member 1 a Battle Dancer with DEX 17, member 0 none."""

    def __init__(self):
        self.dance = {}
        self.written = {}
        gd = self

        class Guest:
            def write(self, at, data):
                gd.written[at] = data

        self.guest = Guest()

    def creature(self, member):
        rec = bytearray(game.CREATURE_SIZE)
        if member in (0, 1):
            rec[game.CREATURE_NAME] = ord("A") + member
            rec[game.CREATURE_STATUS] = game.STATUS_OKAY
            rec[game.CREATURE_ABILITIES + 1] = 17
        return bytes(rec)

    def creature_name(self, member):
        return "Dancer" if member == 1 else "Other"

    def kit_ids(self, member):
        return [kits.BATTLE_DANCER] if member == 1 else []


class DanceTests(unittest.TestCase):
    def test_danced_well(self):
        """d20 = 8 against DEX 17 - 4: +1 for 5 rounds (the first counted), DSCLOG's byte set; over
        before the 6th round."""
        gd, d = FakeGd(), dance.Dances()
        rolls = iter([8, 3])
        out = d.round(gd, 0x100, 1, lambda a, b: next(rolls))
        self.assertEqual(out, ["Dancer dances: d20 = 8, needs 13 or less (DEX 17 -4) -> +1 to hit, damage and AC "
                               "for 5 rounds"])
        self.assertEqual((gd.dance, gd.written[0x100 + dance.TSR_DANCE + 1]), ({1: 1}, b"\x01"))
        for number in range(2, 6):
            self.assertEqual(d.round(gd, 0x100, number), [])
        self.assertEqual(d.round(gd, 0x100, 6), ["Dancer's dance is over"])
        self.assertEqual((gd.dance, gd.written[0x100 + dance.TSR_DANCE + 1]), ({}, b"\x00"))

    def test_stumbled(self):
        """d20 = 14 against DEX 17 - 4 (danced without the -4): -1 for the d8's rounds; the fight's end stops it."""
        gd, d = FakeGd(), dance.Dances()
        rolls = iter([14, 2])
        out = d.round(gd, 0x100, 1, lambda a, b: next(rolls))
        self.assertIn("stumbles: -1 to hit, damage and AC for 2 rounds (d8 = 2)", out[0])
        self.assertEqual(gd.dance, {1: -1})
        d.stop(gd, 0x100)
        self.assertEqual((gd.dance, d.left), ({}, {}))
        self.assertEqual(kits.dance(17, 13, 4), (1, 1))  # (the roll DEX - 4 itself: danced, one round)
        self.assertEqual(kits.dance(10, 1, 4), (1, 5))
        self.assertEqual([kits.dance(25, d, 4) for d in (19, 20)], [(1, 2), (-1, 4)])  # (a natural 20 always fails)

    def test_kept_through_a_break(self):
        """Out of the fight with the game's clock within FIGHT_GAP of the last round (round 1's
        initiative, a break between the arena's waves): the dance is kept; past it, it ends."""
        gd, d = FakeGd(), dance.Dances()
        gd.rules, gd.clock = game.RULE_KITS, 1000
        gd.in_combat = lambda: False
        gd.outdoors = lambda member: False
        gd.game_time = lambda: gd.clock
        d.round(gd, 0x100, 1, lambda a, b: 12)
        log = self.log(gd, d)
        tick = lambda now: dicelog.DiceLog._kit_tick(log, now)
        gd.clock = 1000 + dicelog.FIGHT_GAP
        tick(1.0)
        tick(9.0)  # (the flag down, but never seen up since the roll: round 1's initiative)
        self.assertEqual(gd.dance, {1: 1})
        gd.clock += 1
        tick(10.0)
        self.assertEqual((gd.dance, d.left), ({}, {}))
        self.assertTrue(log._kits_due)

    @staticmethod
    def log(gd, d, w=None):
        return SimpleNamespace(game=gd, tsr_hdr=0x100, _kit_check=0.0, guest=gd.guest, _dances=d,
                               _wild=w or wild.WildFights(), _round_time=1000, _round=1,
                               _out_of_fight=None, _fight_seen=False, _kits_due=False)

    def test_over_with_the_fight(self):
        """The game's fight flag up in the fight, then down FIGHT_OVER: the dance and Wild Fighting
        end at once, whatever came of them, and the next round rolls them again."""
        gd, d, w = FakeGd(), dance.Dances(), wild.WildFights()
        gd.rules, gd.clock, fighting = game.RULE_KITS, 1000, [True]
        gd.in_combat = lambda: fighting[0]
        gd.outdoors = lambda member: False
        gd.game_time = lambda: gd.clock
        d.round(gd, 0x100, 1, lambda a, b: 12)
        w.fighting[1] = True
        log = self.log(gd, d, w)
        tick = lambda now: dicelog.DiceLog._kit_tick(log, now)
        tick(1.0)
        fighting[0] = False
        tick(2.0)
        tick(3.5)  # (down 1.5 seconds: not yet)
        self.assertEqual((gd.dance, log._kits_due), ({1: 1}, False))
        tick(4.5)
        self.assertEqual((gd.dance, d.left, w.fighting, log._kits_due), ({}, {}, {}, True))
        # (the next fight's first round seen as round 7, its clock within FIGHT_GAP: rolled anyway)
        out = d.round(gd, 0x100, 7, lambda a, b: 3, start=log._kits_due)
        self.assertTrue(out and "dances" in out[0], out)
        self.assertEqual(w.round(gd, 0x100, 7, lambda a, b: 3), [])  # (round 7 of a fight: no check)

    def test_a_game_loaded(self):
        """The game's clock gone back (a save loaded): the dance is over, and the round count new."""
        gd, d = FakeGd(), dance.Dances()
        gd.rules, gd.clock = game.RULE_KITS, 1000
        gd.in_combat = lambda: False
        gd.outdoors = lambda member: False
        gd.game_time = lambda: gd.clock
        d.round(gd, 0x100, 1, lambda a, b: 12)
        log = self.log(gd, d)
        gd.clock = 400
        dicelog.DiceLog._kit_tick(log, 1.0)
        self.assertEqual((gd.dance, log._kits_due), ({}, True))
        log.last_ac, log.ac_detail = {}, {}
        self.assertEqual(dicelog.DiceLog._round_number(log), 1)


if __name__ == "__main__":
    unittest.main()
