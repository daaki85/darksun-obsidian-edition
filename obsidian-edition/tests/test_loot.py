"""Looting a container in one go (loot.py): T takes everything into the party's backpacks, Shift+T
all but plain weapons; what has no room stays."""
import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import game, loot, ring  # noqa: E402
from test_dicelog import CREATURES, ITEM_TYPES, ITEMS  # noqa: E402
from test_pickpocket import BOOTS, CLUB, GUARD, KEY, SWORD, THINGS, PickTests  # noqa: E402

BODY, BODY_ITEM, LIST = 300, 90, 450  # (the container's map thing, its item, its list's thing)


def load_tests(loader, tests, pattern):
    return loader.loadTestsFromTestCase(LootTests)


class LootTests(unittest.TestCase):
    def setUp(self):
        """The pickpocket tests' Guard's four things (a bag, a long sword, a key, boots) in a body
        (map thing 300, item 90, its list thing 450) instead of on him; Dag (member 0) alone in the
        party, his backpack empty."""
        pick = PickTests()
        pick.setUp()
        self.m, self.gd = pick.m, pick.log.game
        m = self.m
        struct.pack_into("<hhh", m, CREATURES + GUARD * game.CREATURE_SIZE + 8, game.NO_ITEM, game.NO_ITEM, game.NO_ITEM)
        struct.pack_into("<Bh", m, THINGS + BODY * 3, game.THING_ITEM, BODY_ITEM)
        body = bytearray(game.ITEM_SIZE)
        struct.pack_into("<H", body, game.ITEM_NEXT, game.NO_ITEM)
        struct.pack_into("<H", body, ring.ITEM_CONTENTS, LIST)
        struct.pack_into("<H", body, game.ITEM_TYPE, 66)
        m[ITEMS + BODY_ITEM * game.ITEM_SIZE:ITEMS + (BODY_ITEM + 1) * game.ITEM_SIZE] = body
        m[ITEM_TYPES + 45 * game.ITEM_TYPE_SIZE] = 1  # (the long sword's type: a melee weapon)
        for member in (1, 2, 3):  # (no one else in the party)
            m[CREATURES + member * game.CREATURE_SIZE + game.CREATURE_NAME] = 0

    def contents(self):
        item = ring.Items(self.gd).thing(BODY)[1]
        thing = struct.unpack_from("<H", ring.Items(self.gd).item(item), ring.ITEM_CONTENTS)[0]
        return [i for i, _ in ring.Items(self.gd).chain(thing, inside=False)] if thing < ring.THING_COUNT else None

    def dags(self):
        rec = self.gd.creature(0)
        out = []
        for offset in game.CREATURE_ITEM_LISTS:
            thing, = struct.unpack_from("<h", rec, offset)
            out += [i for i, _ in ring.Items(self.gd).chain(thing, inside=False)]
        return out

    def test_take_all(self):
        lines, took = loot.take(self.gd, BODY, loot.ALL)
        self.assertTrue(took)
        self.assertEqual(lines, ["Dag takes Bag, Wooden Long Sword, Cell Key, Wooden Boots"])
        self.assertIsNone(self.contents())  # (the body's list given back: +08h 9999)
        for item in (CLUB, SWORD, KEY, BOOTS):
            self.assertIn(item, self.dags())
        cells = {ring.Items(self.gd).item(i)[game.ITEM_SLOT] for i in (CLUB, SWORD, KEY, BOOTS)}
        self.assertEqual(len(cells), 4)  # (each in a cell of its own)

    def test_no_plain_weapons(self):
        lines, took = loot.take(self.gd, BODY, loot.NO_PLAIN_WEAPONS)
        self.assertTrue(took)
        self.assertEqual(lines, ["Dag takes Bag, Cell Key, Wooden Boots", "Plain weapons left: Wooden Long Sword"])
        self.assertEqual(self.contents(), [SWORD])
        self.assertNotIn(SWORD, self.dags())

    def test_a_magic_weapon_is_taken(self):
        self.m[ITEMS + SWORD * game.ITEM_SIZE + game.ITEM_PLUS] = 1
        loot.take(self.gd, BODY, loot.NO_PLAIN_WEAPONS)
        self.assertIsNone(self.contents())

    def test_no_room(self):
        """Two cells free: the first two taken, the rest stay, in order."""
        from dsloader import pickpocket
        free = list(pickpocket.BACKPACK)
        orig = loot._used
        loot._used = lambda gd, it, member: set(free[:-2])
        try:
            lines, took = loot.take(self.gd, BODY, loot.ALL)
        finally:
            loot._used = orig
        self.assertTrue(took)
        self.assertEqual(lines, ["Dag takes Bag, Wooden Long Sword", "No room in the backpacks for: Cell Key, Wooden Boots"])
        self.assertEqual(self.contents(), [KEY, BOOTS])

    def test_listed(self):
        self.assertEqual(loot._listed(["Grapes", "Guava", "Guava", "Bloodwrath", "Guava"]),
                         "Grapes, Guava (3), Bloodwrath")

    def test_not_a_container(self):
        self.assertEqual(loot.take(self.gd, 5, loot.ALL), ([], False))


if __name__ == "__main__":
    unittest.main()
