"""Tests for GameData.protection: rings and cloaks of protection on saves, the game's way and
AD&D's (RULE_PROTECTION)."""

import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import game

LEATHER, BONE, METAL = (game.MATERIALS.index(m) for m in ("Leather", "Bone", "Metal"))
HEAD, CHEST, LEFT = (game.EQUIP_SLOTS.index(s) for s in ("head", "chest", "left hand"))


def item(kind, slot, plus=0):
    rec = bytearray(game.ITEM_SIZE)
    struct.pack_into("<H", rec, game.ITEM_TYPE, kind)
    rec[game.ITEM_SLOT] = slot
    rec[game.ITEM_PLUS] = plus & 0xFF
    return rec


def armour(material, slot=CHEST, plus=0, kind=6):
    typ = bytearray(game.ITEM_TYPE_SIZE)
    typ[0x08], typ[0x0F] = material, 0x80
    return item(kind, slot, plus), bytes(typ)


def shield(slot=LEFT):
    typ = bytearray(game.ITEM_TYPE_SIZE)
    typ[0], typ[0x0F] = game.TYPE_SHIELD, 0x80
    return item(4, slot), bytes(typ)


RING_LEFT = (item(game.RING_TYPE, game.FINGERS[0], 1), bytes(game.ITEM_TYPE_SIZE))
RING_RIGHT = (item(game.RING_TYPE, game.FINGERS[1], 2), bytes(game.ITEM_TYPE_SIZE))
CLOAK = (item(game.CLOAK_TYPE, game.CLOAK_SLOT, 1), bytes(game.ITEM_TYPE_SIZE))


class Wearing(game.GameData):
    def __init__(self, rules, *worn):
        self.rules = rules
        self.worn = worn

    def _worn(self, creature):
        return [(n, rec, typ) for n, (rec, typ) in enumerate(self.worn)]


class ProtectionTests(unittest.TestCase):
    def test_the_games_way(self):
        """Without the rule every worn one counts, whatever the armour, as Ring of Protection."""
        g = Wearing(0, RING_LEFT, RING_RIGHT, CLOAK, armour(METAL, plus=2), shield())
        self.assertEqual(g.protection(0), [(4, "Ring of Protection")])

    def test_the_better_ring(self):
        g = Wearing(game.RULE_PROTECTION, RING_LEFT, RING_RIGHT)
        self.assertEqual(g.protection(0), [(2, "Ring of Protection")])

    def test_ring_saves_with_magical_armour(self):
        """(A ring loses only its AC to magical armour: the saves stay.)"""
        g = Wearing(game.RULE_PROTECTION, RING_LEFT, armour(LEATHER, plus=1))
        self.assertEqual(g.protection(0), [(1, "Ring of Protection")])

    def test_cloak_with_natural_armour(self):
        for material in (LEATHER, BONE):
            g = Wearing(game.RULE_PROTECTION, RING_LEFT, CLOAK, armour(material))
            self.assertEqual(g.protection(0), [(1, "Ring of Protection"), (1, "Cloak of Protection")])

    def test_cloak_blocked(self):
        """Metal armour, magical armour (helms too) or a shield: the cloak does nothing."""
        for worn in (armour(METAL), armour(LEATHER, plus=1), armour(METAL, HEAD, kind=89),
                     armour(LEATHER, HEAD, plus=1, kind=5), shield(), shield(game.WEAPON_HANDS[0])):
            g = Wearing(game.RULE_PROTECTION, CLOAK, worn)
            self.assertEqual(g.protection(0), [], worn)

    def test_carried_doesnt_block(self):
        g = Wearing(game.RULE_PROTECTION, CLOAK, armour(METAL, slot=0xFF), shield(0xFF))
        self.assertEqual(g.protection(0), [(1, "Cloak of Protection")])

    def test_plain_helm_and_bone_fine(self):
        g = Wearing(game.RULE_PROTECTION, CLOAK, armour(LEATHER, HEAD, kind=5), armour(BONE, kind=15))
        self.assertEqual(g.protection(0), [(1, "Cloak of Protection")])


if __name__ == "__main__":
    unittest.main()
