"""F10's move back mended (dsloader/moveback.py): the "can walk" bit set again only after the last
step and F10, seen in that order in one turn; never after an attack, an effect or the turn's end."""
import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import game, moveback
from test_squares import DS, LOAD, Game

FULL, SPENT = 0x3EF, 0x3EE  # the turn's flags with "can walk" and as the last step leaves them
START = (50, 50)


class Fight(Game):
    """test_squares' fight (party member 1's turn on square 50,50), the turn begun there with 120
    points: DS:4964h-4968h as the game keeps them for F10."""

    def __init__(self):
        super().__init__(points=120, flags=FULL)
        self.begin(120, *START)

    def begin(self, points, col, row):
        struct.pack_into("<hHH", self.guest.mem, DS * 16 + moveback.START_POINTS, points, row * 16 + 8, col * 16 + 8)

    def flags(self):
        at = (LOAD + moveback.POINTS_SEG) * 16 + self.turn * 2
        return struct.unpack("<H", self.guest.read(at + moveback.FLAGS_OFF, 2))[0]

    def attacks(self, made, commands=0):
        self.guest.mem[(LOAD + moveback.POINTS_SEG) * 16 + moveback.ATTACKS_OFF + self.turn] = made
        self.guest.mem[(LOAD + moveback.POINTS_SEG) * 16 + moveback.COMMANDS_OFF + self.turn] = commands

    def walking(self, on):
        self.guest.mem[DS * 16 + moveback.MAP_RECORD + self.turn * 32] = moveback.WALKING if on else 0

    def creature_name(self, creature):
        return "Ester"

    def last_step(self, col=58, row=50):
        """The step that leaves under 10 points: the points zeroed, the bit cleared (59106h)."""
        self.place(self.turn, col, row)
        self.points(0, SPENT)

    def f10(self):
        """The game's F10: the member back on the turn's square with the turn's points; the flags
        as they were."""
        self.place(self.turn, *START)
        at = (LOAD + moveback.POINTS_SEG) * 16 + self.turn * 2
        struct.pack_into("<h", self.guest.mem, at + moveback.POINTS_OFF, 120)

    def pending(self, step=3, left=7):
        at = (LOAD + moveback.WALK_SEG) * 16
        self.guest.mem[at + moveback.WALK_STEP + self.turn * moveback.WALK_STEP_SIZE] = step
        struct.pack_into("<H", self.guest.mem, at + moveback.WALK_LEFT + self.turn * moveback.WALK_LEFT_SIZE, left)

    def pending_now(self):
        at = (LOAD + moveback.WALK_SEG) * 16
        return (self.guest.mem[at + moveback.WALK_STEP + self.turn * moveback.WALK_STEP_SIZE],
                struct.unpack_from("<H", self.guest.mem, at + moveback.WALK_LEFT + self.turn * moveback.WALK_LEFT_SIZE)[0])


class MoveBackTests(unittest.TestCase):
    def setUp(self):
        self.gd, self.mend = Fight(), moveback.MoveBack()

    def look(self, on=True):
        self.gd.guest.writes.clear()
        return self.mend.update(self.gd, on)

    def test_after_the_last_step(self):
        """The turn seen with the bit, then the last step, then F10: the bit set again, the walk
        the points ran out on forgotten, and a line for the dice log."""
        gd = self.gd
        self.assertIsNone(self.look())
        gd.last_step()
        gd.pending()
        self.assertIsNone(self.look())
        self.assertEqual(gd.guest.writes, [])  # (nothing until F10)
        gd.f10()
        self.assertEqual(self.look(), "F10: Ester's move taken back (can walk again)")
        self.assertEqual(gd.flags(), FULL)
        self.assertEqual(gd.pending_now(), (0xFF, 0))
        self.assertIsNone(self.look())  # (once)
        self.assertEqual(gd.guest.writes, [])
        # and again in the same turn: walked out a second time, F10 again
        gd.last_step()
        self.look()
        gd.f10()
        self.assertIsNotNone(self.look())
        self.assertEqual(gd.flags(), FULL)

    def test_with_movement_left_is_the_games(self):
        """F10 while some movement is left never cleared the bit: nothing is written."""
        gd = self.gd
        self.look()
        gd.place(gd.turn, 54, 50)
        gd.points(80, FULL)
        self.look()
        gd.f10()
        self.assertIsNone(self.look())
        self.assertEqual(gd.guest.writes, [])

    def test_not_after_an_attack(self):
        """An attack made in the turn, before the walk or after it: F10 gets no walk from the
        Loader."""
        gd = self.gd
        self.look()
        gd.last_step()
        self.look()
        gd.attacks(1)  # (the last step, then a swing, then F10)
        self.look()
        gd.f10()
        self.assertIsNone(self.look())
        self.assertEqual((gd.flags(), gd.guest.writes), (SPENT, []))
        gd.attacks(0)  # (even if the count went back, what was seen is forgotten)
        self.assertIsNone(self.look())
        self.assertEqual(gd.flags(), SPENT)
        # an attack that killed and left the member its turn: the swings' count 0 again, the
        # commands' 1 (seen in the game: Ester, the Templar on 4 HP)
        gd3, mend = Fight(), moveback.MoveBack()
        mend.update(gd3, True)
        gd3.last_step()
        gd3.attacks(0, commands=1)  # (the whole attack between two looks)
        mend.update(gd3, True)
        gd3.f10()
        self.assertIsNone(mend.update(gd3, True))
        self.assertEqual((gd3.flags(), gd3.guest.writes), (SPENT, []))
        # a swing first, then the walk to its last step, then F10
        gd2, mend = Fight(), moveback.MoveBack()
        gd2.attacks(1)
        mend.update(gd2, True)
        gd2.last_step()
        mend.update(gd2, True)
        gd2.f10()
        self.assertIsNone(mend.update(gd2, True))
        self.assertEqual(gd2.flags(), SPENT)

    def test_only_the_last_steps_clearing(self):
        """The bit cleared with the points left (an effect that pins the member), the whole word
        zeroed (the turn over), or other flags changed since the last step (a spell cast): not
        mended."""
        gd = self.gd
        self.look()
        gd.points(120, SPENT)  # (pinned: the points untouched, on the turn's square)
        self.assertIsNone(self.look())
        self.assertIsNone(self.look())
        self.assertEqual(gd.flags(), SPENT)
        gd = self.gd = Fight()
        self.mend = moveback.MoveBack()
        self.look()
        gd.points(120, 0)  # (the turn lost)
        self.assertIsNone(self.look())
        self.assertEqual(gd.flags(), 0)
        gd = self.gd = Fight()
        self.mend = moveback.MoveBack()
        self.look()
        gd.last_step()
        self.look()
        gd.points(0, SPENT & ~0x40)  # (another of the turn's bits gone since)
        self.look()
        gd.f10()
        self.assertIsNone(self.look())
        self.assertEqual(gd.flags(), SPENT & ~0x40)

    def test_only_what_f10_does(self):
        """The points back but not the turn's own, the member not on the turn's square, or still
        walking: not F10's doing, nothing mended (until it is)."""
        gd = self.gd
        self.look()
        gd.last_step()
        self.look()
        at = (LOAD + moveback.POINTS_SEG) * 16 + gd.turn * 2
        struct.pack_into("<h", gd.guest.mem, at + moveback.POINTS_OFF, 60)  # (points from elsewhere)
        self.assertIsNone(self.look())
        struct.pack_into("<h", gd.guest.mem, at + moveback.POINTS_OFF, 120)  # (the turn's, but not on its square)
        self.assertIsNone(self.look())
        gd.place(gd.turn, *START)
        gd.walking(True)
        self.assertIsNone(self.look())
        self.assertEqual((gd.flags(), gd.guest.writes), (SPENT, []))
        gd.walking(False)
        self.assertIsNotNone(self.look())
        # a turn that began with no movement worth a step: nothing to give back
        gd = self.gd = Fight()
        self.mend = moveback.MoveBack()
        gd.begin(5, *START)
        gd.points(5, FULL)
        self.look()
        gd.points(0, SPENT)
        self.look()
        struct.pack_into("<h", gd.guest.mem, (LOAD + moveback.POINTS_SEG) * 16 + gd.turn * 2 + moveback.POINTS_OFF, 5)
        self.assertIsNone(self.look())

    def test_one_turn_one_member(self):
        """The last step seen in one member's turn mends nothing in another's, nor after the fight,
        nor for a foe, nor with the switch off; a Loader that didn't see the bit set mends nothing."""
        gd = self.gd
        self.look()
        gd.last_step()
        self.look()
        gd.turn = 2  # (the next member, as the last step left the first: flags of its own)
        gd.place(2, *START)
        gd.points(120, SPENT)
        self.assertIsNone(self.look())
        self.assertEqual(gd.flags(), SPENT)
        gd.turn = 1
        gd.f10()
        self.assertIsNone(self.look())  # (the turn came back: nothing remembered)
        for change in ("fight", "foe", "switch"):
            gd = self.gd = Fight()
            self.mend = moveback.MoveBack()
            self.look()
            gd.last_step()
            self.look()
            if change == "fight":
                gd.fight = False
                self.look()
                gd.fight = True
            elif change == "foe":
                gd.turn = game.PARTY_SIZE + 2
                self.look()
                gd.turn = 1
            else:
                self.look(on=False)
            gd.f10()
            self.assertIsNone(self.look(), change)
            self.assertEqual(gd.flags(), SPENT, change)
        gd = self.gd = Fight()  # (the Loader started after the last step)
        self.mend = moveback.MoveBack()
        gd.last_step()
        self.look()
        gd.f10()
        self.assertIsNone(self.look())


if __name__ == "__main__":
    unittest.main()
