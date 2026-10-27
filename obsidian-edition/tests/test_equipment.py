"""A creature's items: the lists that start in its record, and each item's slot, material and plus."""

import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import game
from test_dicelog import CREATURES, DS, ITEM_TYPES, ITEMS, LOAD_SEG, SHEETS, STALKER, make_game


class EquipmentTests(unittest.TestCase):
    def test_lists(self):
        """Dag holds item 5 (metal long sword +1) in his right hand and carries item 6 (a plain
        wooden long sword), chained from item 5; the list starts at object 40."""
        log = make_game()
        m = log.guest.mem
        things = (LOAD_SEG + game.COMBATANTS_SEG) * 16 + game.COMBATANTS_OFF
        struct.pack_into("<Bh", m, things + 40 * 3, game.THING_ITEM, 5)
        struct.pack_into("<h", m, CREATURES + game.CREATURE_ITEM_LISTS[1], 40)
        struct.pack_into("<h", m, CREATURES + game.CREATURE_ITEM_LISTS[0], 9999)
        sword, spare = ITEMS + 5 * game.ITEM_SIZE, ITEMS + 6 * game.ITEM_SIZE
        struct.pack_into("<h", m, sword + game.ITEM_NEXT, 6)
        struct.pack_into("<h", m, spare + game.ITEM_NEXT, game.NO_ITEM)
        m[sword + game.ITEM_SLOT], m[spare + game.ITEM_SLOT] = 3, 255
        g = game.GameData(log.guest, DS)
        self.assertEqual(g.equipment(0), [("right hand", "Metal Long Sword +1"), (None, "Wooden Long Sword")])

    def test_noise_before_the_tables(self):
        """Before the game loads its item tables (the main menu, character creation) a sheet's items
        read as noise: not readable, so the Loader shows no equipment and no attacks by weapon."""
        log = make_game()
        m = log.guest.mem
        things = (LOAD_SEG + game.COMBATANTS_SEG) * 16 + game.COMBATANTS_OFF
        struct.pack_into("<Bh", m, things + 40 * 3, game.THING_ITEM, 5)
        struct.pack_into("<h", m, CREATURES + game.CREATURE_ITEM_LISTS[1], 40)
        struct.pack_into("<h", m, CREATURES + game.CREATURE_ITEM_LISTS[0], 9999)
        struct.pack_into("<h", m, ITEMS + 5 * game.ITEM_SIZE + game.ITEM_NEXT, game.NO_ITEM)
        g = game.GameData(log.guest, DS)
        self.assertTrue(g.items_readable(0))
        name = struct.unpack_from("<H", m, ITEMS + 5 * game.ITEM_SIZE + game.ITEM_NAME)[0]
        names = game.far_pointer(log.guest, DS, game.ITEM_NAMES_PTR) + name * game.ITEM_NAME_SIZE
        m[names:names + 8] = b"GF\xd0\xa2\xd0\xa6\x01\0"
        self.assertFalse(g.items_readable(0))
        self.assertEqual(g.item_name(name), f"item {name}")

    def test_nothing(self):
        log = make_game()
        struct.pack_into("<hhh", log.guest.mem, CREATURES + 8, 9999, 9999, 9999)
        self.assertEqual(game.GameData(log.guest, DS).equipment(0), [])


class CountedAcTests(unittest.TestCase):
    """A creature's AC as the game's AC routine counts it (the Look box's before any attack on it,
    and DSCLOG's Wall of Thorns'): base, armour worn, a gladiator's levels and DEX."""

    def setUp(self):
        self.log = make_game()
        m = self.m = self.log.guest.mem
        self.rec = CREATURES + STALKER * game.CREATURE_SIZE
        self.sheet = SHEETS + STALKER * game.SHEET_SIZE
        struct.pack_into("b", m, self.sheet + game.SHEET_BASE_AC, 10)
        m[self.rec + game.CREATURE_ABILITIES + 1] = 17
        struct.pack_into("b", m, DS * 16 + game.DEX_AC + 17, -3)
        things = (LOAD_SEG + game.COMBATANTS_SEG) * 16 + game.COMBATANTS_OFF
        struct.pack_into("<Bh", m, things + 50 * 3, game.THING_ITEM, 20)  # leather chest armour
        struct.pack_into("<Bh", m, things + 51 * 3, game.THING_ITEM, 21)  # a sword
        for item, typ, plus in ((20, 30, 1), (21, 31, 2)):
            at = ITEMS + item * game.ITEM_SIZE
            struct.pack_into("<HhB", m, at + game.ITEM_TYPE, typ, 0, 0)
            struct.pack_into("<h", m, at + game.ITEM_NEXT, game.NO_ITEM)
            m[at + game.ITEM_PLUS] = plus
        m[ITEM_TYPES + 30 * game.ITEM_TYPE_SIZE + 0x0F] = 0x80  # counts for AC: AC 1
        m[ITEM_TYPES + 30 * game.ITEM_TYPE_SIZE + 0x12] = 1
        self.lists(9999, 51, 50)  # the armour carried, not worn (as before a fight)

    def lists(self, *things):
        struct.pack_into("<3h", self.m, self.rec + game.CREATURE_ITEM_LISTS[0], *things)

    def ac(self):
        return game.GameData(self.log.guest, DS).counted_ac(STALKER)

    def test_carried_armour_doesnt_count(self):
        self.assertEqual(self.ac(), 7)  # 10, DEX -3; the sword's plus never counts

    def test_worn_armour_and_its_plus(self):
        """Put on (moved to +8, whatever its slot byte): AC 1 and its +1."""
        self.lists(50, 51, 9999)
        self.assertEqual(self.ac(), 5)

    def test_gladiator(self):
        """A fifth of a gladiator's level (10th: 2); not without the sheet's gladiator flag."""
        self.m[self.sheet + game.SHEET_CLASSES] = game.GLADIATOR_CLASS
        self.m[self.sheet + game.SHEET_LEVELS] = 10
        self.assertEqual(self.ac(), 7)
        struct.pack_into("<H", self.m, self.sheet + game.SHEET_FLAGS, game.SHEET_FLAG_GLADIATOR)
        self.assertEqual(self.ac(), 5)


class EffectsLeftTests(unittest.TestCase):
    def test_time_and_charges(self):
        """Blur on Dag, due at 1772 with the clock at 392: 23 rounds; a Stoneskin with 5 charges."""
        log = make_game()
        m = log.guest.mem
        struct.pack_into("<h", m, DS * 16 + game.EFFECT_COUNT, 2)
        effects = (LOAD_SEG + game.EFFECTS_SEG) * 16 + game.EFFECTS_OFF
        m[effects:effects + 10] = struct.pack("<hhhBBBB", 0, 0, 12, 55, 0, 0, 0)
        m[effects + 10:effects + 20] = struct.pack("<hhhBBBB", 0, 0, 52, 48, 1, 5, 0)
        clock, queue = 0x60000, 0x60100
        m[DS * 16 + game.GAME_TIME_PTR:DS * 16 + game.GAME_TIME_PTR + 4] = struct.pack("<HH", clock & 0xF, clock >> 4)
        m[DS * 16 + game.GAME_TIME_SCALE] = 1
        struct.pack_into("<i", m, clock, 392)
        m[DS * 16 + game.EVENT_QUEUE:DS * 16 + game.EVENT_QUEUE + 4] = struct.pack("<HH", queue & 0xF, queue >> 4)
        struct.pack_into("<h", m, DS * 16 + game.EVENT_COUNT, 1)
        struct.pack_into("<iBhB", m, queue, 1772, game.EVENT_EFFECT_ENDS, 0, 0)
        records = (LOAD_SEG + game.SPELLS_SEG) * 16 + game.SPELLS_OFF - 0x10
        struct.pack_into("<h", m, records + 52 * game.SPELL_SIZE + 7, -1)  # (Stoneskin: lasts a number of blows)
        got = [game.effect_text(*x) for x in game.GameData(log.guest, DS).effects_left()]
        self.assertEqual(got, ["Blur (23 rounds)", "Stoneskin (5 charges)"])

    def test_item_power_has_no_charges(self):
        """An item's power (a helm's Gaze Reflection, Shadowseeker's Detect Invisibility), cast for
        -9999 while it is readied: no timer, its spell neither permanent nor counted in uses, and a
        stray 15 (9999's low byte) at +8, not charges."""
        log = make_game()
        m = log.guest.mem
        struct.pack_into("<h", m, DS * 16 + game.EFFECT_COUNT, 1)
        effects = (LOAD_SEG + game.EFFECTS_SEG) * 16 + game.EFFECTS_OFF
        m[effects:effects + 10] = struct.pack("<hhhBBBB", 0, 0, 12, 55, 1, 15, 0)
        records = (LOAD_SEG + game.SPELLS_SEG) * 16 + game.SPELLS_OFF - 0x10
        struct.pack_into("<h", m, records + 12 * game.SPELL_SIZE + 7, 60)  # (timed when cast)
        (effect, charges, seconds), = game.GameData(log.guest, DS).effects_left()
        self.assertEqual((charges, seconds), (None, None))


if __name__ == "__main__":
    unittest.main()
