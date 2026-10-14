"""Tests for the dice log's item checks against the acid and corroding touch (KIND_ITEM)."""

import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import dicelog, game


class FakeGame:
    def __init__(self, rules, saves):
        self.rules, self.saves = rules, saves

    def item_save(self, item, armour):
        return self.saves[item]

    def combatant_name(self, who):
        return {3: "Gerakis", 44: "Rampager"}[who]


def entry(roll, needed, item, armour=False, attack=game.ACID):
    frame = struct.pack("<HHH", 0, 0, 3).ljust(32, b"\0")  # [BP+6]: the target
    parent = struct.pack("<HHHHHHH", 0, 0, 3, 44, 0, 0, attack).ljust(32, b"\0")  # [BP'+8], [BP'+0Eh]
    return dicelog.Entry(0, 0, 0, roll | (needed & 0xFF) << 8, 0, 0, 0, 0, frame, parent, (0, 0, 0, 0),
                         bytes(16), bytes(24), bytes(16), bytes(40), dicelog.KIND_ITEM,
                         item | (dicelog.ITEM_ARMOUR if armour else 0))


SAVES = {1: game.ItemSave("Leather Chest Armor", "leather", None, 10, 0, False),
         2: game.ItemSave("Bone Long Sword", "bone", 8, 11, 0, False),
         3: game.ItemSave("Obsidian Dagger", "obsidian", 8, 5, 0, False),
         4: game.ItemSave("Drake Armor +1", "leather", -79, 8, 1, True)}


def lines(rules, e):
    log = dicelog.DiceLog.__new__(dicelog.DiceLog)
    log.game = FakeGame(rules, SAVES)
    log._names = {}
    return log._item_check(e)


class ItemCheckTests(unittest.TestCase):
    def test_the_games_no_roll(self):
        self.assertEqual(lines(0, entry(0, 21, 1, True)),
                         ["  Rampager's acid on Gerakis's Leather Chest Armor: no magical power, destroyed "
                          "without a roll (the game's rule) -> CORRODED"])

    def test_adnds_number(self):
        self.assertEqual(lines(game.RULE_ITEM_SAVES, entry(12, 10, 1, True)),
                         ["  Rampager's acid on Gerakis's Leather Chest Armor: d20 = 12, needs 10 (AD&D's, 10 "
                          "for leather; the game's: destroyed without a roll) -> safe"])
        self.assertEqual(lines(game.RULE_ITEM_SAVES, entry(4, 5, 3, attack=game.TOUCH_WEAPON)),
                         ["  Rampager's corroding touch on Gerakis's Obsidian Dagger: d20 = 4, needs 5 (AD&D's, "
                          "5 for obsidian; the game's: 8) -> CORRODED"])

    def test_the_games_number(self):
        self.assertEqual(lines(game.RULE_ITEM_SAVES, entry(9, 8, 2)),
                         ["  Rampager's acid on Gerakis's Bone Long Sword: d20 = 9, needs 8 (the game's; AD&D's: "
                          "11 for bone) -> safe"])
        self.assertEqual(lines(0, entry(7, 8, 2)),
                         ["  Rampager's acid on Gerakis's Bone Long Sword: d20 = 7, needs 8 (the game's) -> CORRODED"])

    def test_a_plus(self):
        SAVES[5] = game.ItemSave("Leather Chest Armor +1", "leather", None, 9, 1, False)
        self.assertEqual(lines(game.RULE_ITEM_SAVES, entry(15, 9, 5, True)),
                         ["  Rampager's acid on Gerakis's Leather Chest Armor +1: d20 = 15, needs 9 (AD&D's, 9 (10 "
                          "for leather, -1 for its plus); the game's: destroyed without a roll) -> safe"])

    def test_never(self):
        self.assertEqual(lines(game.RULE_ITEM_SAVES, entry(3, -79, 4, True)),
                         ["  Rampager's acid on Gerakis's Drake Armor +1: d20 = 3, safe whatever the roll (the "
                          "game's; AD&D's: 8 (10 for leather, -1 for its plus, -1 for its power)) -> safe"])


if __name__ == "__main__":
    unittest.main()
