"""Picking pockets: the thieving tools used on someone (pickpocket.py)."""

import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import game, pickpocket, ring, tools
from test_dicelog import CREATURES, DS, ITEM_TYPES, ITEMS, LOAD_SEG, NAMES
from test_now import ThiefTests

THINGS = (LOAD_SEG + game.COMBATANTS_SEG) * 16 + game.COMBATANTS_OFF
GUARD, GUARD_COMBATANT = 5, 43
CLUB, SWORD, KEY, BOOTS = 80, 81, 82, 83


class PickTests(unittest.TestCase):
    def setUp(self):
        """Dag, a 4th level thief (pick pockets 11, move silently 16 with his sword in hand),
        leads, talking to a Guard (creature 5) who has a bag (item 80, type 66: weight 10, worn
        nowhere), a long sword (81, type 45: weight 30, in a hand) and a key (82); then boots
        (83, type 68: weight 1, on the feet)."""
        thief = ThiefTests()
        thief.setUp()
        self.log, m = thief.log, thief.log.guest.mem
        self.m = m
        guard = CREATURES + GUARD * game.CREATURE_SIZE
        m[guard + game.CREATURE_NAME:guard + game.CREATURE_NAME + 6] = b"Guard\0"
        struct.pack_into("<h", m, guard, 30)
        struct.pack_into("<hhh", m, guard + 8, 450, game.NO_ITEM, game.NO_ITEM)
        struct.pack_into("<Bh", m, THINGS + GUARD_COMBATANT * 3, 2, GUARD)
        struct.pack_into("<Bh", m, THINGS + 450 * 3, game.THING_ITEM, CLUB)
        for item, nxt, slot, name, typ in ((CLUB, SWORD, 14, 20, 66), (SWORD, KEY, 15, 21, 45),
                                           (KEY, BOOTS, 16, 22, 66), (BOOTS, game.NO_ITEM, 17, 23, 68)):
            rec = ITEMS + item * game.ITEM_SIZE
            struct.pack_into("<h", m, rec + game.ITEM_NEXT, nxt)
            m[rec + game.ITEM_SLOT] = slot
            struct.pack_into("<H", m, rec + game.ITEM_NAME, name)
            struct.pack_into("<H", m, rec + game.ITEM_TYPE, typ)
        for typ, weight, worn in ((66, 10, 0), (45, 30, 5), (68, 1, 4)):
            struct.pack_into("<H", m, ITEM_TYPES + typ * game.ITEM_TYPE_SIZE + pickpocket.TYPE_WEIGHT, weight)
            m[ITEM_TYPES + typ * game.ITEM_TYPE_SIZE + pickpocket.TYPE_WORN] = worn
        m[ITEM_TYPES + 66 * game.ITEM_TYPE_SIZE + 0x08] = game.NO_MATERIAL
        for entry, text in ((20, b"Bag"), (21, b"Long Sword"), (22, b"Cell Key"), (23, b"Boots")):
            at = NAMES + 3 + entry * game.ITEM_NAME_SIZE
            m[at:at + len(text)] = text
        struct.pack_into("<h", m, (LOAD_SEG + game.TALK_SEG) * 16 + game.TALK_TARGET, GUARD_COMBATANT)
        struct.pack_into("<H", m, DS * 16 + game.WHOSE_TURN, 0)
        struct.pack_into("<H", m, DS * 16 + ring.FREE_THINGS, 505)
        self.tried = set()

    def attempt(self, *rolls):
        rolls = list(rolls)
        return pickpocket.attempt(self.log.game, self.tried, lambda: rolls.pop(0), lambda: 3)

    def guard_items(self):
        return [i for i, _ in ring.Items(self.log.game).chain(450, inside=False)]

    def dag_items(self):
        """Dag's items: his backpack's list (pickpocket.PACK_LIST), then his first."""
        out = []
        for offset in (pickpocket.PACK_LIST, 8):
            thing, = struct.unpack_from("<h", self.m, CREATURES + offset)
            if 0 <= thing < ring.THING_COUNT:
                out += [(i, rec[game.ITEM_SLOT]) for i, rec in ring.Items(self.log.game).chain(thing, inside=False)]
        return out

    def test_lifts_what_is_small(self):
        """Not the sword (too heavy), the key or the boots (on his feet): the bag, into Dag's
        backpack's first cell. He may try again, and then finds nothing more: that ends it."""
        result = self.attempt(11)
        self.assertEqual(result.text, "Dag lifts Bag from Guard unnoticed.")
        self.assertEqual(self.guard_items(), [SWORD, KEY, BOOTS])
        self.assertEqual(self.dag_items()[0], (CLUB, 14))
        self.assertIn("d100 = 11, needs 11 or less -> success", result.log[0])
        self.assertIsNone(result.key)
        money = self.log.game.money()
        again = self.attempt(1)
        self.assertEqual(again.text, "Dag lifts 3 ceramic pieces from Guard's purse, all there was to take.")
        self.assertEqual(self.log.game.money(), money + 3)
        self.assertIsNotNone(again.key)

    def test_kurzaks_sword(self):
        """Kurzak's short sword lifted (whatever its weight): SWORD_XP to the thief, in the text
        and for DSCLOG to give through the game's own routine."""
        m = self.m
        struct.pack_into("<H", m, ITEMS + CLUB * game.ITEM_SIZE + game.ITEM_TYPE, 45)  # (too heavy now)
        struct.pack_into("<H", m, ITEMS + SWORD * game.ITEM_SIZE + game.ITEM_TYPE, game.SHORT_SWORD_TYPE)
        typ = ITEM_TYPES + game.SHORT_SWORD_TYPE * game.ITEM_TYPE_SIZE
        struct.pack_into("<H", m, typ + pickpocket.TYPE_WEIGHT, 30)
        m[typ + pickpocket.TYPE_WORN] = 5  # (in a hand)
        result = self.attempt(11)
        self.assertEqual(result.text, "Dag lifts a metal short sword from Guard unnoticed. "
                                      f"Dag receives {pickpocket.SWORD_XP} experience points!")
        self.assertIn("Long Sword", result.log[1])  # (the log names it)
        self.assertEqual((result.xp_to, result.xp), (0, pickpocket.SWORD_XP))
        self.assertEqual(self.guard_items(), [CLUB, KEY, BOOTS])
        self.assertEqual(self.attempt(11).xp_to, None)  # (the bag's too heavy: just coins now)

    def test_churrrs_club(self):
        """Churrr's Gutterknot lifted (whatever its weight), by its name: SWORD_XP to the thief."""
        from dsloader import worldgear
        self.assertEqual(set(pickpocket.LIFTABLE_NAMES), {worldgear.GUTTERKNOT, worldgear.MINDSHARD})
        m = self.m
        struct.pack_into("<H", m, ITEMS + CLUB * game.ITEM_SIZE + game.ITEM_TYPE, 45)  # (too heavy now)
        struct.pack_into("<H", m, ITEMS + SWORD * game.ITEM_SIZE + game.ITEM_NAME, worldgear.GUTTERKNOT)
        result = self.attempt(11)
        self.assertEqual(result.text, "Dag lifts a knotted club from Guard unnoticed. "
                                      f"Dag receives {pickpocket.SWORD_XP} experience points!")
        self.assertEqual((result.xp_to, result.xp), (0, pickpocket.SWORD_XP))
        self.assertEqual(self.guard_items(), [CLUB, KEY, BOOTS])

    def test_maris_mindshard(self):
        """Maris's Mindshard (an obsidian short sword, weight 30) lifted by its name: SWORD_XP too."""
        from dsloader import worldgear
        m = self.m
        struct.pack_into("<H", m, ITEMS + CLUB * game.ITEM_SIZE + game.ITEM_TYPE, 45)  # (too heavy now)
        struct.pack_into("<H", m, ITEMS + SWORD * game.ITEM_SIZE + game.ITEM_NAME, worldgear.MINDSHARD)
        result = self.attempt(11)
        self.assertEqual(result.text, "Dag lifts an obsidian short sword from Guard unnoticed. "
                                      f"Dag receives {pickpocket.SWORD_XP} experience points!")
        self.assertEqual((result.xp_to, result.xp), (0, pickpocket.SWORD_XP))

    def test_caught(self):
        result = self.attempt(12, 17)  # pick pockets 11, move silently 16
        self.assertEqual(result.text, "Guard catches Dag's hand! Guard will be too wary for Dag to try again.")
        self.assertEqual(self.guard_items(), [CLUB, SWORD, KEY, BOOTS])
        self.assertIn("moves silently to get away: d100 = 17, needs 16 or less -> failed", result.log[1])
        self.tried.add(result.key)  # (as the dice log does)
        self.assertEqual(self.attempt(1).text, "Guard keeps a close hand on their purse now: Dag won't get another chance.")

    def test_slips_away(self):
        """Unnoticed: he may try again."""
        result = self.attempt(50, 16)
        self.assertEqual(result.text, "Dag fumbles Guard's pockets, but slips away unnoticed.")
        self.assertIsNone(result.key)
        self.assertEqual(self.attempt(5).text, "Dag lifts Bag from Guard unnoticed.")

    def test_not_a_thief(self):
        from test_dicelog import SHEETS
        self.m[SHEETS + game.SHEET_CLASSES + 1] = 0
        self.assertEqual(self.attempt().text, "Dag is no thief.")

    def test_no_one_to_rob(self):
        struct.pack_into("<h", self.m, (LOAD_SEG + game.TALK_SEG) * 16 + game.TALK_TARGET, 2)  # a party member
        self.assertIsNone(self.attempt())

    def test_no_ones_turn(self):
        """Between areas no one leads (the turn out of range): no try, and no error."""
        struct.pack_into("<H", self.m, DS * 16 + game.WHOSE_TURN, 0xFFFF)
        self.assertIsNone(self.log.game.whose_turn())
        self.assertIsNone(self.attempt())

    def test_the_buttons_thief(self):
        """The Pick Pockets button's thief tries, whoever leads (no one, here)."""
        struct.pack_into("<H", self.m, DS * 16 + game.WHOSE_TURN, 0xFFFF)
        struct.pack_into("<h", self.m, (LOAD_SEG + game.TALK_SEG) * 16 + game.TALK_TARGET, -1)
        result = pickpocket.attempt(self.log.game, set(), lambda: 11, lambda: 3, who=GUARD, thief=0)
        self.assertEqual(result.text, "Dag lifts Bag from Guard unnoticed.")


if __name__ == "__main__":
    unittest.main()


class ToolsTests(unittest.TestCase):
    """Thieves' Tools an earlier version gave: kept by their name and picture (they pick nothing now)."""
    def setUp(self):
        self.pick = PickTests()
        self.pick.setUp()
        self.gd = self.pick.log.game
        struct.pack_into("<HH", self.pick.m, DS * 16 + ring.FREE_ITEMS, 90, 0)
        struct.pack_into("<h", self.pick.m, ITEMS + 90 * game.ITEM_SIZE + game.ITEM_NEXT, 91)

    def give(self):
        """A set of tools put in Dag's backpack (item 90, from the free list), as an earlier
        version's Kel or Mirlon gave."""
        gd = self.gd
        member = next(m for m in range(game.PARTY_SIZE) if gd.creature_name(m) == "Dag")
        it = ring.Items(gd)
        cell = pickpocket.free_cell(gd, it, member)
        gd.guest.write(gd.ds * 16 + ring.FREE_ITEMS, it.item(90)[game.ITEM_NEXT:game.ITEM_NEXT + 2])
        gd.guest.write(it.items + 90 * game.ITEM_SIZE, tools.ITEM)
        self.assertTrue(pickpocket.give(gd, ring.Items(gd), member, 90, cell))

    def test_earlier_tools_renamed(self):
        """Tools an earlier version gave (named "pick") get today's name entry."""
        self.give()
        m = self.pick.m
        struct.pack_into("<H", m, ITEMS + 90 * game.ITEM_SIZE + game.ITEM_NAME, 0xAD)
        self.assertTrue(tools.is_tools(ring.Items(self.gd).item(90)))
        tools.repaint(self.gd)
        self.assertEqual(struct.unpack_from("<H", m, ITEMS + 90 * game.ITEM_SIZE + game.ITEM_NAME)[0],
                         tools.NAME_ENTRY)

    def test_tools_on_someone(self):
        """Used on the Guard (creature 5)."""
        struct.pack_into("<h", self.pick.m, (LOAD_SEG + game.TALK_SEG) * 16 + game.TALK_TARGET, -1)
        result = pickpocket.attempt(self.gd, set(), lambda: 11, lambda: 3, who=GUARD)
        self.assertEqual(result.text, "Dag lifts Bag from Guard unnoticed.")
        self.assertIsNone(pickpocket.attempt(self.gd, set(), lambda: 11, lambda: 3, who=0))  # the party


class SwitchTests(unittest.TestCase):
    def test_switch(self):
        """The helper's switch: items used on the map asked about (bit 0) either way, the Pick
        Pockets button (bit 1) with picking pockets on."""
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from test_dicelog import HDR, make_game
        from dsloader import dicelog
        log = make_game()
        flags = lambda: struct.unpack("<H", log.guest.read(HDR + dicelog.TSR_PICK_ON, 2))[0]
        log.set_pickpockets(True)
        self.assertEqual(flags(), dicelog.USE_ASK | dicelog.PICK_BUTTON)
        log.set_pickpockets(False)
        self.assertEqual(flags(), dicelog.USE_ASK)


class ListTests(unittest.TestCase):
    """A party member's worn list and backpack list (pickpocket.place, mend_lists; npcitems.add_to)."""

    def setUp(self):
        self.pick = PickTests()
        self.pick.setUp()
        self.gd, self.m = self.pick.log.game, self.pick.m
        struct.pack_into("<Bh", self.m, THINGS + 505 * 3, 0, 506)  # (two free objects for new lists)

    def items_in(self, offset):
        thing, = struct.unpack_from("<h", self.m, CREATURES + offset)
        if not 0 <= thing < ring.THING_COUNT:
            return []
        return [(i, rec[game.ITEM_SLOT]) for i, rec in ring.Items(self.gd).chain(thing, inside=False)]

    def test_put_away_and_taken_out(self):
        """Dag's sword put in the backpack goes to the backpack's list (a new one), and back in
        his hand to the worn list (a new one too: his first list emptied of it)."""
        self.assertTrue(pickpocket.place(self.gd, 0, 5, 14))
        self.assertEqual(self.items_in(pickpocket.PACK_LIST), [(5, 14)])
        self.assertEqual(self.items_in(8), [(6, game.MISSILE_SLOT)])
        self.assertTrue(pickpocket.place(self.gd, 0, 5, game.WEAPON_HANDS[0]))
        self.assertEqual(self.items_in(pickpocket.WORN_LIST), [(5, game.WEAPON_HANDS[0])])
        self.assertEqual(self.items_in(pickpocket.PACK_LIST), [])

    def test_mend(self):
        """A backpack item in the worn list (as earlier versions gave it) is put in the backpack's
        list, once; what is worn stays."""
        thing, = struct.unpack_from("<h", self.m, CREATURES + 8)
        struct.pack_into("<h", self.m, CREATURES + pickpocket.WORN_LIST, thing)  # (his list as the worn one)
        struct.pack_into("<h", self.m, CREATURES + 8, game.NO_ITEM)
        self.m[ITEMS + 6 * game.ITEM_SIZE + game.ITEM_SLOT] = 15  # (the bow in the backpack, in the worn list)
        out = pickpocket.mend_lists(self.gd)
        self.assertEqual(len(out), 1)
        self.assertIn("put away in the backpack", out[0])
        self.assertEqual(self.items_in(pickpocket.PACK_LIST), [(6, 15)])
        self.assertEqual(self.items_in(pickpocket.WORN_LIST), [(5, game.WEAPON_HANDS[0])])
        self.assertEqual(pickpocket.mend_lists(self.gd), [])

    def test_add_to(self):
        """npcitems.add_to gives a party member an item for the backpack in the backpack's list,
        one to wear in the worn list."""
        from dsloader import npcitems
        struct.pack_into("<HH", self.m, DS * 16 + ring.FREE_ITEMS, 60, 0)
        struct.pack_into("<h", self.m, ITEMS + 60 * game.ITEM_SIZE + game.ITEM_NEXT, 61)
        struct.pack_into("<h", self.m, ITEMS + 61 * game.ITEM_SIZE + game.ITEM_NEXT, game.NO_ITEM)
        rec = bytes(game.ITEM_SIZE)
        self.assertTrue(npcitems.add_to(self.gd, 0, rec))
        self.assertEqual(self.items_in(pickpocket.PACK_LIST), [(60, 14)])
        self.assertTrue(npcitems.add_to(self.gd, 0, rec, game.CLOAK_SLOT))
        self.assertEqual(self.items_in(pickpocket.WORN_LIST), [(61, game.CLOAK_SLOT)])
