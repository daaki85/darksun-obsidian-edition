"""A Wild Fury's Wild Fighting (wild.py): checked as each fight's first round begins, kept for
the fight."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import game, kits, wild  # noqa: E402

HDR = 0x100


class FakeGd:
    """Party member 2 a Wild Fury with CON 18, member 0 none."""

    def __init__(self):
        self.wild = {}
        self.written = {}
        self.own = {}
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
        return [kits.WILD_FURY] if member == 2 else []

    def own_race(self, member):
        return self.own.get(member, 0)

    def bits(self):
        return self.written[HDR + wild.TSR_WILD][0]


class WildTests(unittest.TestCase):
    def test_passed(self):
        """d20 = 12 against CON 18 - 4: passed, its bit N + 4 set (1 more attack, 3 more damage), for the
        fight; cleared as it ends."""
        gd, w = FakeGd(), wild.WildFights()
        out = w.round(gd, HDR, 1, lambda a, b: 12)
        self.assertEqual(out, ["Mul fights wild: d20 = 12, needs 14 or less (CON 18 -4) -> 1 more attack a round "
                               "and +3 damage for the fight"])
        self.assertEqual((gd.wild, gd.bits()), ({2: True}, 0x40))
        self.assertEqual(w.round(gd, HDR, 2), [])
        self.assertEqual(gd.bits(), 0x40)
        w.stop(gd, HDR)
        self.assertEqual((gd.wild, gd.bits()), ({}, 0))

    def test_failed(self):
        """d20 = 15 against CON 18 - 4 (passed without the -4): failed, its bit N set (3 worse to hit, AC 3 worse)."""
        gd, w = FakeGd(), wild.WildFights()
        out = w.round(gd, HDR, 1, lambda a, b: 15)
        self.assertEqual(out, ["Mul fights wild: d20 = 15, needs 14 or less (CON 18 -4) -> fails: -3 to hit and AC "
                               "3 worse for the fight"])
        self.assertEqual((gd.wild, gd.bits()), ({2: False}, 0x04))

    def test_every_fight(self):
        """No rest between wild fights: the next fight, right after, checks again (a new roll)."""
        gd, w = FakeGd(), wild.WildFights()
        w.round(gd, HDR, 1, lambda a, b: 19)
        w.stop(gd, HDR)
        out = w.round(gd, HDR, 1, lambda a, b: 12)
        self.assertEqual((len(out), gd.wild, gd.bits()), (1, {2: True}, 0x40))

    def test_unseen_end(self):
        """A new fight's first round with the last one's end unseen: the last fight's result dropped,
        a new check."""
        gd, w = FakeGd(), wild.WildFights()
        w.round(gd, HDR, 1, lambda a, b: 19)
        w.round(gd, HDR, 2)
        w.round(gd, HDR, 1, lambda a, b: 12)
        self.assertEqual(gd.wild, {2: True})

    def test_gerakis(self):
        """Gerakis (the game's own party's half-giant: kits.own_race) fights wild, with no kit."""
        gd, w = FakeGd(), wild.WildFights()
        gd.own = {0: kits.HALF_GIANT}
        out = w.round(gd, HDR, 1, lambda a, b: 12)
        self.assertEqual(len(out), 2)
        self.assertEqual(gd.wild, {0: True, 2: True})
        gd, w = FakeGd(), wild.WildFights()
        gd.own = {0: kits.THRI_KREEN}
        w.round(gd, HDR, 1, lambda a, b: 12)
        self.assertEqual(gd.wild, {2: True})

    def test_kits(self):
        self.assertEqual([kits.wild_check(15, d) for d in (1, 11, 12, 15, 20)], [True, True, False, False, False])
        self.assertEqual([kits.wild_check(25, d) for d in (19, 20)], [True, False])  # (a natural 20 always fails)
        self.assertEqual([kits.wild_ac(a) for a in (-3, 0, 7, 8, 10, 11)], [0, 3, 10, 10, 10, 11])


if __name__ == "__main__":
    unittest.main()
