import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dsloader import ring, stuckwalk  # noqa: E402

LOAD, DS = 0x100, 0x2000
BASE = (LOAD + stuckwalk.TABLE_SEG) * 16 + stuckwalk.TABLE_OFF
TRUSTEE = 43


class Guest:
    def __init__(self):
        self.mem = bytearray(0x100000)

    def read(self, at, n):
        return bytes(self.mem[at:at + n])

    def write(self, at, data):
        self.mem[at:at + len(data)] = data


class Game:
    def __init__(self):
        self.guest, self.load_seg, self.ds = Guest(), LOAD, DS
        self.clock, self.fight = 1000, False

    def game_time(self):
        return self.clock

    def in_combat(self):
        return self.fight

    def creature_name(self, who):
        return {20: "Trustee"}.get(who, "?")

    def entry(self, thing, order, script):
        at = BASE + thing * stuckwalk.ENTRY
        self.guest.write(at, struct.pack("<H", order))
        self.guest.write(at + stuckwalk.FILE, struct.pack("<H", script))

    def order(self, thing):
        return struct.unpack("<H", self.guest.read(BASE + thing * stuckwalk.ENTRY, 2))[0]

    def place(self, thing, x, y):
        self.guest.write(DS * 16 + ring.POSITIONS + thing * ring.POSITION_SIZE, struct.pack("<HH", x, y))


class Items:
    def __init__(self, gd):
        pass

    def thing(self, t):
        return (2, 20) if t == TRUSTEE else (2, 5) if t == 10 else (0, 0)


class StuckWalkerTests(unittest.TestCase):
    def setUp(self):
        from unittest import mock
        patch = mock.patch.object(ring, "Items", Items)
        patch.start()
        self.addCleanup(patch.stop)
        self.gd = Game()
        self.gd.entry(TRUSTEE, stuckwalk.WALK, 8)
        self.gd.place(TRUSTEE, 1464, 1400)
        self.w = stuckwalk.StuckWalkers()

    def test_stuck_walk_taken_back(self):
        """A walk his script gave that hasn't moved him in STILL_FOR game seconds: no order."""
        self.assertEqual(self.w.check(self.gd), [])
        self.gd.clock += stuckwalk.STILL_FOR - 1
        self.assertEqual(self.w.check(self.gd), [])
        self.gd.clock += 1
        self.assertEqual(self.w.check(self.gd), ["Trustee"])
        self.assertEqual(self.gd.order(TRUSTEE), 0)

    def test_walking_left_alone(self):
        self.w.check(self.gd)
        for step in range(1, 6):
            self.gd.clock += 10
            self.gd.place(TRUSTEE, 1464, 1400 - 16 * step)
            self.assertEqual(self.w.check(self.gd), [])
        self.assertEqual(self.gd.order(TRUSTEE), stuckwalk.WALK)

    def test_not_in_fights_nor_without_a_script(self):
        self.gd.entry(10, stuckwalk.WALK, 0)  # (a walk of no script's: someone else's doing)
        self.w.check(self.gd)
        self.gd.fight = True
        self.gd.clock += 100
        self.assertEqual(self.w.check(self.gd), [])
        self.gd.fight = False
        self.assertEqual(self.w.check(self.gd), [])  # (the fight started the count again)
        self.gd.clock += 100
        self.assertEqual(self.w.check(self.gd), ["Trustee"])
        self.assertEqual(self.gd.order(10), stuckwalk.WALK)

    def test_clock_back(self):
        """A save loaded (the clock gone back): counted again from then."""
        self.w.check(self.gd)
        self.gd.clock -= 500
        self.assertEqual(self.w.check(self.gd), [])
        self.gd.clock += stuckwalk.STILL_FOR
        self.assertEqual(self.w.check(self.gd), ["Trustee"])


if __name__ == "__main__":
    unittest.main()
