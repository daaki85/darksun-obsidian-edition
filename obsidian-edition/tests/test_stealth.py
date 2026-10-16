"""Hiding in shadows and moving silently to backstab (RULE_STEALTH)."""

import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import game, stealth
from test_dicelog import CREATURES, DS, HDR, SHEETS, STALKER, far, set_clock


def game_sheet():
    return SHEETS
from test_now import ThiefTests

MAP = 0x60000


def rolls(*faces):
    it = iter(faces)
    return lambda: next(it)


class StealthTests(unittest.TestCase):
    def setUp(self):
        """Dag (combatant 0), a 4th level thief: hide in shadows and move silently 16 each.
        The Mountain Stalker (combatant 0x29) is on the other side, three squares away. In the
        arena unless a test says otherwise."""
        thief = ThiefTests()
        thief.setUp()
        self.log = thief.log
        self.gd = self.log.game
        self.m = self.log.guest.mem
        self.place(0, 10, 10)
        self.place(0x29, 13, 10)
        self.m[CREATURES + STALKER * game.CREATURE_SIZE + game.CREATURE_STATUS] = game.STATUS_OKAY
        struct.pack_into("<h", self.m, CREATURES + STALKER * game.CREATURE_SIZE, 30)
        self.region(0x2A)
        self.m[DS * 16 + stealth.MAP_PTR:DS * 16 + stealth.MAP_PTR + 4] = far(MAP)

    def place(self, combatant, x, y):
        struct.pack_into("<HH", self.m, DS * 16 + stealth.POSITIONS + combatant * stealth.POSITION_SIZE,
                         x * 16 + 8, y * 16 + 8)

    def region(self, number):
        struct.pack_into("<H", self.m, DS * 16 + 0x117C, number)

    def test_outdoors_halved(self):
        lines, hidden = stealth.turn(self.gd, 0, rolls(8, 16))
        self.assertTrue(hidden)
        self.assertEqual(lines[0], "Dag hides in shadows: d100 = 8, needs 8 or less (16, halved in daylight) -> hidden")
        self.assertTrue(lines[1].startswith("  Dag moves silently: d100 = 16, needs 16 or less -> unheard"))

    def test_not_halved_by_the_sun(self):
        """A Military Scout, and Cilla (the game's own party's elf, the Elven Wanderer: kits.own_race),
        hide with their whole chance in daylight (the Scout with its +10 under the open sky)."""
        from unittest import mock
        from dsloader import kits
        with mock.patch.object(self.gd, "kit_ids", lambda creature: [kits.SCOUT]):
            lines, _ = stealth.turn(self.gd, 0, rolls(16, 99))
        self.assertEqual(lines[0], "Dag hides in shadows: d100 = 16, needs 26 or less (26, a Military Scout: "
                                   "not halved in daylight) -> hidden")
        with mock.patch.object(self.gd, "own_race", lambda creature: kits.ELF):
            lines, _ = stealth.turn(self.gd, 0, rolls(16, 99))
        self.assertIn("(16, the Elven Wanderer: not halved in daylight) -> hidden", lines[0])
        with mock.patch.object(self.gd, "own_race", lambda creature: kits.THRI_KREEN):
            lines, _ = stealth.turn(self.gd, 0, rolls(16, 99))
        self.assertIn("halved in daylight) -> seen", lines[0])

    def test_cloak_and_boots(self):
        """Worn, a cloak adds 10 to hiding in shadows (before daylight halves it) and boots 10 to
        moving silently; carried, nothing."""
        cloak, boots = bytearray(game.ITEM_SIZE), bytearray(game.ITEM_SIZE)
        cloak[game.ITEM_SLOT], boots[game.ITEM_SLOT] = game.CLOAK_SLOT, game.FOOT
        worn = [(1, bytes(cloak), b""), (2, bytes(boots), b"")]
        self.gd._worn = lambda member: iter(worn)
        lines, hidden = stealth.turn(self.gd, 0, rolls(13, 26))
        self.assertTrue(hidden)
        self.assertEqual(lines[0], "Dag hides in shadows: d100 = 13, needs 13 or less "
                                   "(16 +10 cloak = 26, halved in daylight) -> hidden")
        self.assertTrue(lines[1].startswith("  Dag moves silently: d100 = 26, needs 26 (16 +10 boots) or less -> unheard"))
        worn[:] = []
        self.assertIn("needs 8 or less (16, halved in daylight)", stealth.turn(self.gd, 0, rolls(99))[0][0])

    def elven(self, cloak=True, boots=True):
        worn = []
        for on, type_, slot in ((cloak, game.ELVEN_CLOAK_TYPE, game.CLOAK_SLOT), (boots, game.ELVEN_BOOTS_TYPE, game.FOOT)):
            if on:
                rec = bytearray(game.ITEM_SIZE)
                rec[game.ITEM_SLOT] = slot
                struct.pack_into("<H", rec, game.ITEM_TYPE, type_)
                worn.append((len(worn), bytes(rec), b""))
        self.gd._worn = lambda member: iter(worn)

    def test_elvenkind(self):
        """The Cloak of Elvenkind: 95 to hide under the open sky (no halving), 90 under a roof; the
        Boots of Elvenkind: 95 to move silently; the switch for plain gear makes no difference."""
        self.elven()
        lines, hidden = stealth.turn(self.gd, 0, rolls(95, 95), gear=False)
        self.assertTrue(hidden)
        self.assertEqual(lines[0], "Dag hides in shadows: d100 = 95, needs 95 or less "
                                   "(Cloak of Elvenkind, under the open sky) -> hidden")
        self.assertTrue(lines[1].startswith("  Dag moves silently: d100 = 95, needs 95 (Boots of Elvenkind) or less "
                                            "-> unheard: their next attack this turn is from behind (a backstab"))
        self.region(0x29)
        self.assertIn("needs 90 or less (Cloak of Elvenkind, under a roof)", stealth.turn(self.gd, 0, rolls(99))[0][0])

    def test_elvenkind_not_a_thief(self):
        """No thief or ranger (who couldn't put them on in the game): nothing."""
        self.m[game_sheet() + game.SHEET_CLASSES + 1] = 0  # (a fighter only)
        self.elven()
        self.assertEqual(stealth.turn(self.gd, 0, rolls()), ([], False))

    def test_elvenkind_ranger(self):
        """A ranger in the cloak indoors: 90, not their halved chance."""
        self.m[game_sheet() + game.SHEET_CLASSES + 1] = 13
        self.m[game_sheet() + game.SHEET_LEVELS + 1] = 10
        self.region(0x29)
        self.elven()
        lines, hidden = stealth.turn(self.gd, 0, rolls(90, 95))
        self.assertTrue(hidden)
        self.assertIn("needs 90 or less (Cloak of Elvenkind, under a roof)", lines[0])
        self.assertTrue(lines[1].endswith("their next attack this turn is from behind"))

    def test_cloak_and_boots_switched_off(self):
        """With the Options tab's switch off, a worn cloak and boots add nothing."""
        cloak, boots = bytearray(game.ITEM_SIZE), bytearray(game.ITEM_SIZE)
        cloak[game.ITEM_SLOT], boots[game.ITEM_SLOT] = game.CLOAK_SLOT, game.FOOT
        self.gd._worn = lambda member: iter([(1, bytes(cloak), b""), (2, bytes(boots), b"")])
        lines, hidden = stealth.turn(self.gd, 0, rolls(8, 16), gear=False)
        self.assertEqual(lines[0], "Dag hides in shadows: d100 = 8, needs 8 or less (16, halved in daylight) -> hidden")
        self.assertNotIn("boots", lines[1])

    def test_seen(self):
        self.assertEqual(stealth.turn(self.gd, 0, rolls(9)),
                         (["Dag hides in shadows: d100 = 9, needs 8 or less (16, halved in daylight) -> seen"], False))

    def test_heard(self):
        lines, hidden = stealth.turn(self.gd, 0, rolls(3, 17))
        self.assertFalse(hidden)
        self.assertEqual(lines[1], "  Dag moves silently: d100 = 17, needs 16 or less -> heard")

    def test_indoors(self):
        self.region(0x29)  # the slave pens
        lines, hidden = stealth.turn(self.gd, 0, rolls(16, 1))
        self.assertTrue(hidden)
        self.assertIn("needs 16 or less (16, out of the sun)", lines[0])

    def test_by_the_floor(self):
        """On a map with buildings (0Bh), the tile under the thief: an indoor floor, or not."""
        self.region(0x0B)
        self.m[MAP + 10 * stealth.MAP_WIDTH + 10] = 66
        self.assertFalse(stealth.daylight(self.gd, 0))
        self.m[MAP + 10 * stealth.MAP_WIDTH + 10] = 1
        self.assertTrue(stealth.daylight(self.gd, 0))

    def test_enemy_beside(self):
        self.place(0x29, 11, 11)
        self.assertEqual(stealth.turn(self.gd, 0, rolls()),
                         (["Dag can't hide in shadows: Mountain Stalker is right beside them"], False))

    def test_shadowblade_beside(self):
        """A Shadowblade (a half-elf fighter/thief's kit) hides with an enemy right beside them."""
        from dsloader import kits
        self.place(0x29, 11, 11)
        self.gd.kit_ids = lambda creature: [kits.SHADOWBLADE] if creature == 0 else []
        lines, hidden = stealth.turn(self.gd, 0, rolls(1, 1))
        self.assertTrue(hidden)
        self.assertIn("a Shadowblade, with Mountain Stalker beside them", lines[0])

    def test_fallen_enemy_beside(self):
        self.place(0x29, 11, 11)
        struct.pack_into("<h", self.m, CREATURES + STALKER * game.CREATURE_SIZE, 0)
        self.assertTrue(stealth.turn(self.gd, 0, rolls(1, 1))[1])

    def test_friend_beside(self):
        self.place(1, 10, 11)
        self.m[CREATURES + game.CREATURE_SIZE + game.CREATURE_SIDE] = self.m[CREATURES + game.CREATURE_SIDE]
        self.assertTrue(stealth.turn(self.gd, 0, rolls(1, 1))[1])

    def ranger(self, level=10, cls=13):
        """Dag a ranger (air) instead of a thief: AD&D's 63 to hide and 78 to move silently at
        10th level (no race or DEX adjustment in these tables)."""
        self.m[game_sheet() + game.SHEET_CLASSES + 1] = cls
        self.m[game_sheet() + game.SHEET_LEVELS + 1] = level

    def test_ranger_outdoors(self):
        """Under the open sky a ranger hides with the full chance; their attack is from behind,
        no backstab."""
        self.ranger()
        lines, hidden = stealth.turn(self.gd, 0, rolls(63, 78))
        self.assertTrue(hidden)
        self.assertEqual(lines, ["Dag hides in shadows: d100 = 63, needs 63 or less (63, a ranger under the open sky) "
                                 "-> hidden",
                                 "  Dag moves silently: d100 = 78, needs 78 or less -> unheard: their next attack "
                                 "this turn is from behind"])

    def test_ranger_indoors(self):
        self.ranger(level=1)
        self.region(0x29)
        lines, hidden = stealth.turn(self.gd, 0, rolls(6))
        self.assertEqual(lines, ["Dag hides in shadows: d100 = 6, needs 5 or less (10, halved indoors for a ranger) -> seen"])
        self.assertFalse(hidden)

    def test_stalker_indoors(self):
        """A Stalker (kits.py) hides with its full chance indoors too."""
        from unittest import mock
        from dsloader import kits
        self.ranger(level=1)
        self.region(0x29)
        with mock.patch.object(self.gd, "kit_ids", lambda creature: [kits.STALKER]):
            lines, _ = stealth.turn(self.gd, 0, rolls(99))
        self.assertIn("a Stalker: not halved indoors", lines[0])
        need = int(lines[0].split("needs ")[1].split(" ")[0])
        self.assertEqual(need, int(lines[0].split("(")[1].split(",")[0].split(" = ")[-1]))

    def test_ranger_effects(self):
        """Not Okay: no hiding for a ranger either."""
        self.ranger()
        self.m[CREATURES + game.CREATURE_STATUS] = 3
        self.assertEqual(self.gd.ranger_skill_now(0, stealth.HIDE), 0)

    def test_thief_and_ranger(self):
        """Thief levels too: hiding as a thief (halved outdoors, the backstab)."""
        self.m[game_sheet() + game.SHEET_CLASSES + 2] = 13
        self.m[game_sheet() + game.SHEET_LEVELS + 2] = 10
        lines, _ = stealth.turn(self.gd, 0, rolls(8, 16))
        self.assertIn("halved in daylight", lines[0])
        self.assertIn("backstab", lines[1])

    def test_not_a_thief(self):
        self.assertEqual(stealth.turn(self.gd, 1, rolls()), ([], False))
        self.assertEqual(stealth.turn(self.gd, 0x29, rolls()), ([], False))

    def test_in_the_log(self):
        """On Dag's turn in a fight: the rolls, and DSCLOG told; the next turn ends it."""
        log = self.log
        log.rules = game.RULE_STEALTH
        log.stealth_roll = rolls(2, 5)
        set_clock(log, 600)
        log._round_time = 600
        struct.pack_into("<h", self.m, DS * 16 + game.WHOSE_TURN, 0)
        lines = log.turn_lines()
        self.assertEqual(lines[0], "Dag's turn")
        self.assertIn("-> hidden", lines[1])
        self.assertEqual(struct.unpack_from("<H", self.m, HDR + stealth.TSR_STEALTH)[0], 1)
        struct.pack_into("<h", self.m, DS * 16 + game.WHOSE_TURN, 0x29)
        self.assertEqual(log.turn_lines(), ["Mountain Stalker's turn"])
        self.assertEqual(struct.unpack_from("<H", self.m, HDR + stealth.TSR_STEALTH)[0], 0)

    def test_rule_off(self):
        log = self.log
        log.rules = 0
        set_clock(log, 600)
        log._round_time = 600
        struct.pack_into("<h", self.m, DS * 16 + game.WHOSE_TURN, 0)
        self.assertEqual(log.turn_lines(), ["Dag's turn"])


class GearPriceTests(unittest.TestCase):
    def test_cloaks_boots_and_belts(self):
        """Plain ones worn as a cloak, on the feet or as a belt cost GEAR_VALUE (an earlier
        version's 100 too); magic ones (a plus, or dearer) and other things keep their prices."""
        from dsloader import ring
        from test_dicelog import ITEM_TYPES, ITEMS
        from test_ring import arena
        log = arena()
        m, gd = log.guest.mem, log.game
        kinds = ((50, stealth.WORN_CLOAK), (51, stealth.WORN_FEET), (52, 5), (53, stealth.WORN_BELT))
        for typ, worn in kinds:
            m[ITEM_TYPES + typ * game.ITEM_TYPE_SIZE + stealth.TYPE_WORN] = worn
        # item, type, price, plus
        items = ((90, 50, 20, 0), (91, 51, 1, 0), (92, 50, 5000, 1), (93, 52, 10, 0), (94, 53, 2, 0),
                 (95, 51, 100, 0), (96, 50, 3000, 0), (97, 53, 20, 1))
        for n, (item, typ, value, plus) in enumerate(items):
            rec = ITEMS + item * game.ITEM_SIZE
            nxt = items[n + 1][0] if n + 1 < len(items) else game.NO_ITEM
            struct.pack_into("<h", m, rec + game.ITEM_NEXT, nxt)
            struct.pack_into("<H", m, rec + game.ITEM_TYPE, typ)
            struct.pack_into("<H", m, rec + stealth.ITEM_VALUE, value)
            m[rec + game.ITEM_PLUS] = plus
        struct.pack_into("<Bh", m, ring.Items(gd).things + 410 * 3, game.THING_ITEM, 90)
        self.assertEqual(stealth.reprice(gd), 4)
        price = lambda item: struct.unpack_from("<H", m, ITEMS + item * game.ITEM_SIZE + stealth.ITEM_VALUE)[0]
        self.assertEqual([price(item) for item, *_ in items], [24, 24, 5000, 10, 24, 24, 3000, 20])
        self.assertEqual(stealth.reprice(gd), 0)

if __name__ == "__main__":
    unittest.main()
