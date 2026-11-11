import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dsloader import kurzakdoor as kd  # noqa: E402

DS, MAP_SEG = 0x2000, 0x5000
SQUARE_AT = MAP_SEG * 16 + kd.SQUARE[1] * kd.MAP_WIDTH + kd.SQUARE[0]
LEAF_THINGS = {2145: 96, 2146: 225}  # (where the user's save had them)


class Guest:
    def __init__(self):
        self.mem = bytearray(0x100000)

    def read(self, at, n):
        return bytes(self.mem[at:at + n])

    def write(self, at, data):
        self.mem[at:at + len(data)] = data


class Game:
    def __init__(self):
        self.guest, self.ds = Guest(), DS
        self.clock, self.fight, self.where = 31500, False, kd.REGION
        self.guest.write(DS * 16 + kd.WALK_MAP, struct.pack("<HH", 0, MAP_SEG))
        self.square(192)
        for obj in kd.LEAVES:
            self.leaf(obj, 0x08)

    def game_time(self):
        return self.clock

    def in_combat(self):
        return self.fight

    def region(self):
        return self.where

    def things_of(self, obj):
        return [LEAF_THINGS[obj]] if obj in LEAF_THINGS else []

    def leaf(self, obj, state):
        self.guest.write(DS * 16 + kd.THINGS + LEAF_THINGS[obj] * kd.THING_SIZE + kd.LEAF_STATE, bytes([state]))

    def square(self, value=None):
        if value is not None:
            self.guest.write(SQUARE_AT, bytes([value]))
        return self.guest.read(SQUARE_AT, 1)[0]


class DoorMendTests(unittest.TestCase):
    def setUp(self):
        self.gd, self.m = Game(), kd.DoorMend()

    def test_open_door_barred_on_the_map_opened(self):
        """Both leaves open, the square shut for SHUT_FOR game seconds: floor."""
        self.assertFalse(self.m.check(self.gd))
        self.gd.clock += kd.SHUT_FOR - 1
        self.assertFalse(self.m.check(self.gd))
        self.assertEqual(self.gd.square(), 192)
        self.gd.clock += 1
        self.assertTrue(self.m.check(self.gd))
        self.assertEqual(self.gd.square(), kd.FLOOR)
        self.gd.clock += kd.SHUT_FOR
        self.assertFalse(self.m.check(self.gd))  # (already floor)

    def test_shut_door_left_shut(self):
        """A leaf shut (10h or 20h there): the door is shut, as the map says."""
        for state in (0x10, 0x20):
            self.gd.leaf(2146, state)
            self.assertFalse(self.m.check(self.gd))
            self.gd.clock += kd.SHUT_FOR * 3
            self.assertFalse(self.m.check(self.gd))
            self.assertEqual(self.gd.square(), 192)

    def test_a_swing_never_cut_short(self):
        """The map shut only for a moment (a door closing as it should, its leaves then shut)."""
        self.m.check(self.gd)
        self.gd.clock += kd.SHUT_FOR - 1
        self.gd.leaf(2145, 0x20)
        self.assertFalse(self.m.check(self.gd))
        self.gd.leaf(2145, 0x08)
        self.gd.clock += 1
        self.assertFalse(self.m.check(self.gd))  # (counting starts again)
        self.assertEqual(self.gd.square(), 192)

    def test_not_in_a_fight_or_elsewhere(self):
        self.m.check(self.gd)
        self.gd.fight = True
        self.gd.clock += kd.SHUT_FOR * 2
        self.assertFalse(self.m.check(self.gd))
        self.gd.fight, self.gd.where = False, 0x2A
        self.gd.clock += kd.SHUT_FOR * 2
        self.assertFalse(self.m.check(self.gd))
        self.assertEqual(self.gd.square(), 192)

    def test_leaves_not_on_the_map(self):
        """The leaves not found (another region's things, or the map loading): nothing."""
        self.gd.things_of = lambda obj: []
        self.m.check(self.gd)
        self.gd.clock += kd.SHUT_FOR * 2
        self.assertFalse(self.m.check(self.gd))
        self.assertEqual(self.gd.square(), 192)


if __name__ == "__main__":
    unittest.main()
