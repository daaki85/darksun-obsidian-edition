"""Psionic Blast's imagined wounds given back as the fight ends (psiblast.py)."""

import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dsloader import game, psiblast
from test_dicelog import CREATURES, HDR, SHEETS, make_game


class BlastTests(unittest.TestCase):
    def setUp(self):
        self.log = make_game()
        self.gd, self.m = self.log.game, self.log.guest.mem
        for member, hp, most in ((0, 8, 40), (1, 3, 15), (2, 5, 30)):
            struct.pack_into("<h", self.m, CREATURES + member * game.CREATURE_SIZE, hp)
            self.m[CREATURES + member * game.CREATURE_SIZE + game.CREATURE_STATUS] = game.STATUS_OKAY
            struct.pack_into("<h", self.m, SHEETS + member * game.SHEET_SIZE + game.SHEET_MAX_HP, most)

    def blast(self, *lost):
        struct.pack_into("<4h", self.m, HDR + psiblast.TSR_BLAST, *lost)

    def hp(self, member):
        return struct.unpack_from("<h", self.m, CREATURES + member * game.CREATURE_SIZE)[0]

    def test_given_back(self):
        """Each standing member's loss given back, no more than its most; one Out Cold wakes with
        it; one dead keeps what it has; the field cleared, so nothing is given twice."""
        self.blast(24, 20, 6, 0)
        self.m[CREATURES + 2 * game.CREATURE_SIZE + game.CREATURE_STATUS] = game.OUT_COLD
        out = psiblast.give_back(self.gd, HDR)
        self.assertEqual((self.hp(0), self.hp(1), self.hp(2)), (32, 15, 11))
        self.assertEqual(len(out), 3)
        self.assertIn("Dag shakes off Psionic Blast's imagined wounds", out[0])
        self.assertIn("+24 HP, now 32/40", out[0])
        self.assertIn("+12 HP, now 15/15", out[1])
        self.assertIn("+6 HP, now 11/30", out[2])  # (Out Cold: woken)
        self.assertIn("wakes and shakes off", out[2])
        self.assertEqual(self.m[CREATURES + 2 * game.CREATURE_SIZE + game.CREATURE_STATUS], game.STATUS_OKAY)
        self.assertEqual(struct.unpack_from("<4h", self.m, HDR + psiblast.TSR_BLAST), (0, 0, 0, 0))
        self.assertEqual(psiblast.give_back(self.gd, HDR), [])

    def test_dead_keeps_nothing(self):
        self.blast(6, 0, 0, 0)
        self.m[CREATURES + game.CREATURE_STATUS] = 5  # (Dead)
        out = psiblast.give_back(self.gd, HDR)
        self.assertEqual(self.hp(0), 8)
        self.assertIn("don't come back: Dag is dead", out[0])

    def test_at_the_fight_end(self):
        """BlastWatch gives them back once the fight has been over FIGHT_OVER seconds, not before
        nor during it; a game loaded (the clock back) clears them with nothing given."""
        watch, fighting = psiblast.BlastWatch(), [True]
        tick = lambda now: watch.tick(self.gd, HDR, now, lambda: fighting[0])
        self.blast(10, 0, 0, 0)
        self.assertEqual(tick(0.0), [])
        fighting[0] = False
        self.assertEqual(tick(1.0), [])
        self.assertEqual(tick(2.5), [])
        self.assertEqual(len(tick(3.1)), 1)
        self.assertEqual(self.hp(0), 18)
        self.assertEqual(tick(9.0), [])  # (no fight since)

    def test_loaded_game_clears(self):
        watch, fighting = psiblast.BlastWatch(), [True]
        clock = [5000]
        self.gd.game_time = lambda: clock[0]
        tick = lambda now: watch.tick(self.gd, HDR, now, lambda: fighting[0])
        self.blast(10, 0, 0, 0)
        tick(0.0)
        fighting[0], clock[0] = False, 100  # (loaded: the clock back, no fight on)
        self.assertEqual(tick(1.0), [])
        self.assertEqual(tick(5.0), [])
        self.assertEqual(self.hp(0), 8)
        self.assertEqual(struct.unpack_from("<4h", self.m, HDR + psiblast.TSR_BLAST), (0, 0, 0, 0))


if __name__ == "__main__":
    unittest.main()
