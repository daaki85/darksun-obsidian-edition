"""A Blood-Fury's Wild Fighting (wild.py): checked as a fight's first round begins, kept for the
fight, an hour's rest after it."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import game, kits, wild  # noqa: E402

HDR = 0x100


class FakeGd:
    """Party member 2 a Blood-Fury with CON 18, member 0 none."""

    def __init__(self):
        self.wild = {}
        self.written = {}
        gd = self

        class Guest:
            def write(self, at, data):
                gd.written[at] = data

        self.guest = Guest()

    def creature(self, member):
        rec = bytearray(game.CREATURE_SIZE)
        if member in (0, 2):
            rec[game.CREATURE_NAME] = ord("A") + member
            rec[game.CREATURE_STATUS] = game.STATUS_OKAY
            rec[game.CREATURE_ABILITIES + 2] = 18
        return bytes(rec)

    def creature_name(self, member):
        return "Mul" if member == 2 else "Other"

    def kit_ids(self, member):
        return [kits.BLOOD_FURY] if member == 2 else []

    def bits(self):
        return self.written[HDR + wild.TSR_WILD][0]


class WildTests(unittest.TestCase):
    def test_passed(self):
        """d20 = 12 against CON 18: passed, its bit N + 4 set (1 more attack, 3 more damage), for the
        fight; cleared as it ends."""
        gd, w = FakeGd(), wild.WildFights()
        out = w.round(gd, HDR, 1, 1000, lambda a, b: 12)
        self.assertEqual(out, ["Mul fights wild: d20 = 12, needs 18 or less (CON 18) -> 1 more attack a round "
                               "and +3 damage for the fight"])
        self.assertEqual((gd.wild, gd.bits()), ({2: True}, 0x40))
        self.assertEqual(w.round(gd, HDR, 2, 1060), [])
        self.assertEqual(gd.bits(), 0x40)
        w.stop(gd, HDR, 1120)
        self.assertEqual((gd.wild, gd.bits(), w.ended), ({}, 0, {2: 1120}))

    def test_failed(self):
        """d20 = 19 against CON 18: failed, its bit N set (3 worse to hit, AC 3 worse)."""
        gd, w = FakeGd(), wild.WildFights()
        out = w.round(gd, HDR, 1, 1000, lambda a, b: 19)
        self.assertEqual(out, ["Mul fights wild: d20 = 19, needs 18 or less (CON 18) -> fails: -3 to hit and AC "
                               "3 worse for the fight"])
        self.assertEqual((gd.wild, gd.bits()), ({2: False}, 0x04))

    def test_rest(self):
        """A fight within an hour of the game's clock of the last wild fight's end: no check, no bits;
        an hour on, a check again."""
        gd, w = FakeGd(), wild.WildFights()
        w.round(gd, HDR, 1, 1000, lambda a, b: 12)
        w.stop(gd, HDR, 1200)
        out = w.round(gd, HDR, 1, 1200 + 1800, lambda a, b: 12)
        self.assertEqual(out, ["Mul is too tired to fight wild: rested 30 of 60 minutes since the last wild "
                               "fight (30 more)"])
        self.assertEqual((gd.wild, gd.bits()), ({}, 0))
        out = w.round(gd, HDR, 1, 1200 + kits.WILD_REST, lambda a, b: 12)
        self.assertEqual((len(out), gd.wild), (1, {2: True}))

    def test_unseen_end(self):
        """A new fight's first round with the last one's end unseen: that fight over at its last
        round, the rest counted from there."""
        gd, w = FakeGd(), wild.WildFights()
        w.round(gd, HDR, 1, 1000, lambda a, b: 12)
        w.round(gd, HDR, 2, 1060)
        out = w.round(gd, HDR, 1, 1060 + 600, lambda a, b: 12)
        self.assertEqual((w.ended, gd.wild), ({2: 1060}, {}))
        self.assertIn("too tired", out[0])

    def test_kits(self):
        self.assertEqual([kits.wild_check(15, d) for d in (1, 15, 16, 20)], [True, True, False, False])
        self.assertEqual([kits.wild_ac(a) for a in (-3, 0, 7, 8, 10, 11)], [0, 3, 10, 10, 10, 11])


if __name__ == "__main__":
    unittest.main()
