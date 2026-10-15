"""New characters' starting gear filled out (startgear.py)."""

import os
import struct
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dsloader import game, restrict, specialize, startgear, weaponchoice  # noqa: E402
from test_specialize import FinishNewTests, sheet  # noqa: E402

KIND = specialize.KINDS.index
SLOT = game.EQUIP_SLOTS.index
CHEST, ARM, LEGS, BELT, BOOTS, CLOAK = 6, 7, 8, 42, 68, 65
CLUB, SLING, CHATKCHA = 18, 64, 48
DAGGER = weaponchoice.PLAIN[KIND("dagger")][0]
SHORT_SWORD = weaponchoice.PLAIN[KIND("short sword")][0]
OBSIDIAN_MACE = weaponchoice.OTHERS[KIND("mace")][0][0]


class FillTests(FinishNewTests):
    """startgear.fill on a party of one New character."""

    def setUp(self):
        super().setUp()
        rules = game.RULES_IN_FORCE
        game.RULES_IN_FORCE = 0
        self.addCleanup(setattr, game, "RULES_IN_FORCE", rules)
        self.type_at = lambda t: self.TYPES + t * game.ITEM_TYPE_SIZE
        for t in range(game.GAME_TYPES + 25):  # (every class may use every type, as far as the game's lists go)
            self.mem[self.type_at(t) + 0x10:self.type_at(t) + 0x12] = b"\xff\xff"
        for kind, plain in enumerate(weaponchoice.PLAIN):
            for weapon in (plain,) + weaponchoice.OTHERS.get(kind, ()):
                at = self.type_at(weapon[0])
                self.mem[at] = 0x02 if kind in weaponchoice.MISSILE_KINDS else 0x01
        for material, types in ((restrict.OBSIDIAN, (DAGGER, OBSIDIAN_MACE, CHATKCHA)),
                                (restrict.BONE, (weaponchoice.PLAIN[KIND("mace")][0], SHORT_SWORD)),
                                (restrict.LEATHER, (CHEST, ARM, LEGS))):
            for t in types:
                self.mem[self.type_at(t) + 8] = material
        for t, worn in ((CHEST, 1), (ARM, 3), (LEGS, 4)):  # (armour, worn on the chest, arms, legs)
            self.mem[self.type_at(t) + 0x0F] = restrict.ARMOUR
            self.mem[self.type_at(t) + 9] = worn
        self.given = []
        patch = mock.patch("dsloader.npcitems.add_to", self.add_to)
        patch.start()
        self.addCleanup(patch.stop)
        self.gd.item_name = lambda n: f"item {n:X}"

    def add_to(self, gd, creature, rec, slot=None):  # (the harness has no lists: the next record)
        self.given.append(struct.unpack_from("<H", rec, game.ITEM_TYPE)[0])
        at = self.ITEMS + self.items * game.ITEM_SIZE
        rec = bytearray(rec)
        rec[game.ITEM_SLOT] = 20 + self.items if slot is None else slot
        self.mem[at:at + game.ITEM_SIZE] = rec
        self.items += 1
        return True

    def character(self, classes, race=7):
        s = bytearray(sheet((), classes=classes))
        s[game.SHEET_RACE] = race
        s[game.SHEET_FLAGS:game.SHEET_FLAGS + 2] = b"\xff\xff"
        self.mem[self.SHEETS:self.SHEETS + game.SHEET_SIZE] = s

    def worn(self):
        return {self.item(n)[0]: self.item(n)[1] for n in range(self.items)}

    def test_a_thief_gets_a_weapon_in_hand_and_the_rest(self):
        """A thief/psionicist's long sword left behind: a short sword in hand; leather arm and leg
        armour to go with its chest armour; a belt, boots and a dagger; its sling kept."""
        self.character((17, 12, 0))
        self.give(CHEST, 0x07, SLOT("chest"))
        self.give(SLING, 0x00, weaponchoice.MISSILE_SLOT)
        out = startgear.fill(self.gd)
        worn = self.worn()
        self.assertEqual(worn[SHORT_SWORD], game.WEAPON_HANDS[0])
        self.assertEqual((worn[ARM], worn[LEGS], worn[BELT], worn[BOOTS]),
                         (SLOT("arm"), SLOT("legs"), SLOT("waist"), SLOT("foot")))
        self.assertGreaterEqual(worn[DAGGER], startgear.BACKPACK)
        self.assertNotIn(CLOAK, worn)  # (a ranger's or a Stalker's)
        self.assertEqual(self.given.count(SLING), 0)
        self.assertIn("starts with more gear", out[0])
        self.assertEqual(startgear.fill(self.gd), [])  # (once)

    def test_a_cleric_takes_its_club_in_hand(self):
        self.character((2, 0, 0), race=game.HUMAN)
        self.give(CLUB, 0x11, 20)
        out = startgear.fill(self.gd)
        self.assertEqual(self.item(0), (CLUB, game.WEAPON_HANDS[0]))
        self.assertIn("from the backpack in hand", out[0])
        self.assertEqual(self.worn()[SLING], weaponchoice.MISSILE_SLOT)

    def test_a_fire_cleric_gets_an_obsidian_mace(self):
        """With the class restrictions: obsidian weapons only, so a mace in hand, a chatkcha in place
        of a sling, an obsidian dagger."""
        self.gd.rules = game.RULE_RESTRICT
        self.character((3, 0, 0), race=game.HUMAN)
        self.give(4, 0x05, game.WEAPON_HANDS[1])  # (its shield)
        startgear.fill(self.gd)
        worn = self.worn()
        self.assertEqual(worn[OBSIDIAN_MACE], game.WEAPON_HANDS[0])
        self.assertNotIn(SLING, worn)
        self.assertGreaterEqual(worn[CHATKCHA], startgear.BACKPACK)
        self.assertGreaterEqual(worn[DAGGER], startgear.BACKPACK)

    def test_a_multiclass_preserver_takes_its_armour_off(self):
        """With the class restrictions, a fighter/preserver's armour goes in the backpack (it can't
        cast in it), and none is given; the shield stays."""
        self.gd.rules = game.RULE_RESTRICT
        self.character((9, 11, 0))
        self.give(weaponchoice.START_TYPE, weaponchoice.START_NAME, game.WEAPON_HANDS[0])
        self.give(CHEST, 0x07, SLOT("chest"))
        self.give(4, 0x05, game.WEAPON_HANDS[1])
        out = startgear.fill(self.gd)
        self.assertEqual(self.item(1), (CHEST, 30))  # (pickpocket.free_cell, as the harness has it)
        self.assertEqual(self.item(2), (4, game.WEAPON_HANDS[1]))
        self.assertNotIn(ARM, self.given)
        self.assertNotIn(LEGS, self.given)
        self.assertIn("can't cast in armour", out[0])

    def test_a_ranger_gets_a_cloak(self):
        self.character((13, 0, 0), race=game.HUMAN)
        self.give(weaponchoice.START_TYPE, weaponchoice.START_NAME, game.WEAPON_HANDS[0])
        startgear.fill(self.gd)
        self.assertEqual(self.worn()[CLOAK], SLOT("cloak"))

    def test_no_gear_yet(self):
        """Before the game gives a character its gear: nothing."""
        self.character((9, 0, 0))
        self.assertEqual(startgear.fill(self.gd), [])
        self.assertEqual(self.given, [])


if __name__ == "__main__":
    unittest.main()
