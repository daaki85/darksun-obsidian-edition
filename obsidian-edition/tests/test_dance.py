"""A Battle Dancer's dance (dance.py): rolled as a fight's first round begins, counted down."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from types import SimpleNamespace  # noqa: E402

from dsloader import dance, dicelog, game, kits  # noqa: E402


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
        """d20 = 12 against DEX 17: +1 for 5 rounds (the first counted), DSCLOG's byte set; over
        before the 6th round."""
        gd, d = FakeGd(), dance.Dances()
        rolls = iter([12, 3])
        out = d.round(gd, 0x100, 1, lambda a, b: next(rolls))
        self.assertEqual(out, ["Dancer dances: d20 = 12, needs 17 or less (DEX 17) -> +1 to hit, damage and AC "
                               "for 5 rounds"])
        self.assertEqual((gd.dance, gd.written[0x100 + dance.TSR_DANCE + 1]), ({1: 1}, b"\x01"))
        for number in range(2, 6):
            self.assertEqual(d.round(gd, 0x100, number), [])
        self.assertEqual(d.round(gd, 0x100, 6), ["Dancer's dance is over"])
        self.assertEqual((gd.dance, gd.written[0x100 + dance.TSR_DANCE + 1]), ({}, b"\x00"))

    def test_stumbled(self):
        """d20 = 19 against DEX 17: -1 for the d8's rounds; the fight's end stops it."""
        gd, d = FakeGd(), dance.Dances()
        rolls = iter([19, 2])
        out = d.round(gd, 0x100, 1, lambda a, b: next(rolls))
        self.assertIn("stumbles: -1 to hit, damage and AC for 2 rounds (d8 = 2)", out[0])
        self.assertEqual(gd.dance, {1: -1})
        d.stop(gd, 0x100)
        self.assertEqual((gd.dance, d.left), ({}, {}))
        self.assertEqual(kits.dance(17, 17, 4), (1, 1))  # (the roll DEX itself: danced, one round)
        self.assertEqual(kits.dance(10, 1, 4), (1, 9))

    def test_kept_through_a_break(self):
        """Out of the fight with the game's clock within FIGHT_GAP of the last round (round 1's
        initiative, a break between the arena's waves): the dance is kept; past it, it ends."""
        gd, d = FakeGd(), dance.Dances()
        gd.rules, gd.clock = game.RULE_KITS, 1000
        gd.in_combat = lambda: False
        gd.outdoors = lambda member: False
        gd.game_time = lambda: gd.clock
        d.round(gd, 0x100, 1, lambda a, b: 12)
        log = SimpleNamespace(game=gd, tsr_hdr=0x100, _kit_check=0.0, guest=gd.guest, _dances=d,
                              _round_time=1000)
        tick = lambda now: dicelog.DiceLog._kit_tick(log, now)
        gd.clock = 1000 + dicelog.FIGHT_GAP
        tick(1.0)
        self.assertEqual(gd.dance, {1: 1})
        gd.clock += 1
        tick(2.0)
        self.assertEqual((gd.dance, d.left), ({}, {}))


if __name__ == "__main__":
    unittest.main()
