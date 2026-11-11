"""A lock a thief failed is out of reach until the thief gains a level (locks.py, DSCLOG's
LOCK_SITE), and a fumbled pocket the same for that thief (pickpocket.fumble_key), with Thieves as in
AD&D."""
import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import game, gamepatch, locks, pickpocket  # noqa: E402
import test_dsclog as td  # noqa: E402
import test_dsclog_drawing as tdd  # noqa: E402


def load_tests(loader, tests, pattern):
    suite = loader.loadTestsFromTestCase(LoaderTests)
    suite.addTests(LockSiteTests(name) for name in sorted(vars(LockSiteTests)) if name.startswith("test_"))
    return suite


class FakeGame:
    def __init__(self, names, levels, region=0x29):
        self.names, self.levels, self._region = names, levels, region

    def creature_name(self, n):
        return self.names[n]

    def region(self):
        return self._region


class LoaderTests(unittest.TestCase):
    def setUp(self):
        self.level = pickpocket.thief_level
        pickpocket.thief_level = lambda gd, m: gd.levels[m]

    def tearDown(self):
        pickpocket.thief_level = self.level

    def test_patch(self):
        p = next(x for x in gamepatch.PATCHES if x.name == "lock_retry")
        self.assertEqual((p.offset, p.original.hex()), (0x803D3, "8946fe"))
        self.assertEqual(p.replacement, bytes((0xCD, 0x98, gamepatch.LOCK_SITE)))
        self.assertEqual(gamepatch.LOCK_SITE, gamepatch.NS_IMAGE + 112)

    def test_barred_at_the_level_failed_only(self):
        gd = FakeGame(["Cilla", "Gerakis", "K'ratchek", "Cermak"], [4, 1, 1, 1])
        tried = {locks.key("Cilla", 0x29, 200, "Cilla", 4), locks.key("Cilla", 0x29, 201, "Cilla", 3),
                 locks.key("Cilla", 0x1A, 202, "Cilla", 4), locks.key("Cilla", 0x29, 203, "Gerakis", 1),
                 locks.key("Ester", 0x29, 204, "Cilla", 4), "Cilla|0x29|30|Kurzak"}
        rows = locks.barred(gd, tried)
        self.assertEqual(rows, [[(0x29, 200)], [(0x29, 203)], [], []])
        gd.levels[0] = 5  # (a level gained: the lock can be tried again)
        self.assertEqual(locks.barred(gd, tried)[0], [])

    def test_table(self):
        data = locks.table([[(0x29, 200)], [], [(1, 2), (3, 4), (5, 6), (7, 8)], []])
        self.assertEqual(len(data), 4 * locks.LOCK_MAX * 4)
        self.assertEqual(struct.unpack_from("<4H", data, 0), (0x29, 200, 0xFFFF, 0xFFFF))
        self.assertEqual(struct.unpack_from("<8H", data, 32), (1, 2, 3, 4, 5, 6, 7, 8))
        self.assertEqual(set(data[16:32]), {0xFF})

    def test_fumble_key_has_the_level(self):
        self.assertNotEqual(pickpocket.fumble_key("a|41|30|Kurzak", "Cilla", 4),
                            pickpocket.fumble_key("a|41|30|Kurzak", "Cilla", 5))


@unittest.skipIf(td.Uc is None, "unicorn not installed")
class LockSiteTests(td.NewSpellTests):
    """LOCK_SITE (803D3h's "mov [bp-2],ax"): the chance stored, and LOCK_NEVER for open locks by a
    party member on a lock (the region, the thing the script was started on) in its LOCK_BARRED."""

    def setUp(self):
        super().setUp()
        _, self.sym = tdd.build()
        mu = self.mu
        mu.mem_write(td.GAME_DS * 16 + 0x117C, struct.pack("<H", 0x29))
        mu.mem_write((td.GAME_DS - (0x4356 - game.TALK_SEG)) * 16 + game.TALK_TARGET, struct.pack("<H", 200))
        rows = [[], [(0x29, 200)], [(0x1A, 200), (0x29, 201)], []]
        mu.mem_write(td.TSR * 16 + self.sym["lock_barred"], locks.table(rows))

    def check(self, who, skill, chance=40):
        mu = self.mu
        mu.mem_write(td.SS * 16 + td.BP - 2, struct.pack("<h", 7))
        mu.mem_write(td.SS * 16 + td.BP + 6, struct.pack("<HH", who, skill))
        self.site(gamepatch.LOCK_SITE, eax=chance)
        return struct.unpack("<h", mu.mem_read(td.SS * 16 + td.BP - 2, 2))[0]

    def test_header_offset(self):
        self.assertEqual(struct.unpack("<H", self.mu.mem_read(td.TSR * 16 + self.sym["hdr"] + locks.TSR_LOCK_OFF, 2))[0],
                         self.sym["lock_barred"])

    def test_barred(self):
        self.assertEqual(self.check(1, locks.OPEN_LOCKS), locks.NEVER)

    def test_others_as_rolled(self):
        self.assertEqual(self.check(0, locks.OPEN_LOCKS), 40)  # (another member)
        self.assertEqual(self.check(2, locks.OPEN_LOCKS), 40)  # (that thing in another region; another thing here)
        self.assertEqual(self.check(1, 2), 40)  # (find/remove traps)
        self.assertEqual(self.check(30, locks.OPEN_LOCKS), 40)  # (not a party member)


if __name__ == "__main__":
    unittest.main()
