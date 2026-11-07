"""The game's people in their gear from the start (people.py): which slot each backpack item goes
to, as the game puts them on at a person's first action (seen in DOSBox, 2026-11-06)."""

import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import game, people, restrict


def typ(flags: int, worn: int) -> bytes:
    rec = bytearray(game.ITEM_TYPE_SIZE)
    rec[people.TYPE_FLAGS], rec[people.TYPE_WORN] = flags, worn
    return bytes(rec)


def item(plus: int = 0) -> bytes:
    rec = bytearray(game.ITEM_SIZE)
    struct.pack_into("b", rec, game.ITEM_PLUS, plus)
    return bytes(rec)


SWORD = typ(restrict.MELEE, people.HAND)
CLUB = SWORD
BOW = typ(restrict.MISSILE | 0x08, people.MISSILE_WORN)
SHIELD = typ(restrict.SHIELD, people.HAND)
CHEST, ARM, LEGS, HELM, ARROWS = typ(0, 1), typ(0, 3), typ(0, 10), typ(0, 6), typ(0, 11)
KEY, RING, CLOAK = typ(0, 0), typ(0, 9), typ(0, 8)


class PlanTests(unittest.TestCase):
    def test_arena_guard(self):
        """As the game put an Arena Guard's on: arm armour 0, the sword 3, chest armour 9, the bow 2,
        the arrows 1."""
        pack = [(1, item(), ARM), (2, item(), SWORD), (3, item(), CHEST), (4, item(), BOW), (5, item(), ARROWS)]
        self.assertEqual(sorted(people.plan(pack, set())), [(1, people.ARM), (2, people.RIGHT), (3, people.CHEST),
                                                           (4, people.MISSILE), (5, people.AMMO)])

    def test_two_weapons_the_better_in_the_main_hand(self):
        """Kurzak's: Shadowseeker +1 in the right hand, the plain sword in the left (the game's main
        and off hand); his helm on, his key left in the pack."""
        pack = [(1, item(), SWORD), (2, item(), KEY), (3, item(1), SWORD), (4, item(), HELM)]
        self.assertEqual(sorted(people.plan(pack, set())), [(1, people.LEFT), (3, people.RIGHT), (4, people.HEAD)])

    def test_two_clubs(self):
        self.assertEqual(sorted(people.plan([(1, item(), CLUB), (2, item(), CLUB)], set())),
                         [(1, people.RIGHT), (2, people.LEFT)])

    def test_shield_before_a_second_weapon(self):
        """A Gladiator's club and shield: the club in the right hand, the shield in the left; a
        second club stays in the pack."""
        pack = [(1, item(), CLUB), (2, item(), SHIELD), (3, item(), CLUB), (4, item(), LEGS)]
        self.assertEqual(sorted(people.plan(pack, set())), [(1, people.RIGHT), (2, people.LEFT), (4, people.LEGS)])

    def test_slots_taken_left_alone(self):
        """What the game (or an earlier pass) has put on already keeps its slot; nothing moves into
        it, and a weapon with no hand free stays in the pack."""
        pack = [(1, item(), SWORD), (2, item(), CHEST), (3, item(), SWORD)]
        self.assertEqual(people.plan(pack, {people.RIGHT, people.CHEST, people.LEFT}), [])
        self.assertEqual(people.plan(pack, {people.RIGHT, people.CHEST}), [(1, people.LEFT)])

    def test_rings_cloaks_worn_keys_stay(self):
        """A ring and a cloak go on (a finger, the cloak slot); a second ring the other finger,
        a third stays; boots, a belt and an amulet theirs; a key stays packed."""
        pack = [(1, item(1), RING), (2, item(1), CLOAK), (3, item(), KEY), (4, item(), RING), (5, item(), RING),
                (6, item(), typ(0, 4)), (7, item(), typ(0, 2)), (8, item(), typ(0, 7))]
        self.assertEqual(sorted(people.plan(pack, set())),
                         [(1, people.FINGER), (2, people.CLOAK), (4, people.FINGER2), (6, people.FOOT),
                          (7, people.WAIST), (8, people.NECK)])
        self.assertEqual(people.plan([(1, item(), RING)], {people.FINGER}), [(1, people.FINGER2)])

    def test_two_handed_alone(self):
        """A great axe takes both hands: the shield and a second weapon stay in the pack."""
        axe = bytearray(typ(restrict.MELEE, people.HAND))
        axe[people.TYPE_HANDS] = people.TWO_HANDED
        pack = [(1, item(), bytes(axe)), (2, item(), SHIELD), (3, item(), CLUB)]
        self.assertEqual(people.plan(pack, set()), [(1, people.RIGHT)])

    def test_two_handed_already_held(self):
        """A great axe already in the right hand (dressed at an earlier visit, or by the game): the
        shield stays in the pack."""
        self.assertEqual(people.plan([(2, item(), SHIELD)], {people.RIGHT}, both_held=True), [])
        self.assertEqual(people.plan([(2, item(), SHIELD)], {people.RIGHT}), [(2, people.LEFT)])

    def test_two_hander_never_second(self):
        """A +1 one-hander and a two-hander: the one-hander in the right hand, the two-hander not in
        the left."""
        axe = bytearray(typ(restrict.MELEE, people.HAND))
        axe[people.TYPE_HANDS] = people.TWO_HANDED
        self.assertEqual(people.plan([(1, item(1), SWORD), (2, item(), bytes(axe))], set()), [(1, people.RIGHT)])

    def test_two_hander_not_beside_a_held_shield(self):
        """The left hand filled already (a shield): a one-hander in the right, never the great axe;
        with only the axe, nothing."""
        axe = bytearray(typ(restrict.MELEE, people.HAND))
        axe[people.TYPE_HANDS] = people.TWO_HANDED
        self.assertEqual(people.plan([(1, item(1), bytes(axe)), (2, item(), SWORD)], {people.LEFT}), [(2, people.RIGHT)])
        self.assertEqual(people.plan([(1, item(), bytes(axe))], {people.LEFT}), [])

    def test_only_one_of_each(self):
        """Two chest armours (one bought, one found): the first worn, the other kept."""
        self.assertEqual(people.plan([(1, item(), CHEST), (2, item(), CHEST)], set()), [(1, people.CHEST)])


if __name__ == "__main__":
    unittest.main()
