"""Class restrictions (restrict.py)."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import game, restrict

# Item types as the game has them (DSUN's IT1R): flags, material, +0Fh, the classes' mask
TYPES = {
    0: (0x02, 0x05, 0x40, 0x1EF1),    # staff sling
    1: (0x0A, 0x80, 0x40, 0x177B),    # bow
    3: (0x01, 0x80, 0x40, 0x1EFA),    # quarterstaff
    4: (0x04, 0x05, 0x80, 0x166F),    # shield (leather)
    5: (0x00, 0x05, 0x80, 0x166F),    # helm (leather)
    6: (0x00, 0x05, 0x80, 0x176F),    # leather chest armour
    9: (0x00, 0x01, 0x80, 0x126F),    # bone ring chest armour
    16: (0x04, 0x00, 0x80, 0x126F),   # shield (wooden)
    17: (0x01, 0x03, 0x00, 0x1FF6),   # obsidian dagger
    18: (0x01, 0x80, 0x00, 0x177A),   # club
    20: (0x01, 0x01, 0x00, 0x167A),   # bone mace
    22: (0x01, 0x04, 0x00, 0x177A),   # axe (metal)
    29: (0x01, 0x04, 0x00, 0x1776),   # Flame Blade (no kind)
    37: (0x01, 0x05, 0x00, 0x1FFF),   # Chameleon Gloves (no kind)
    45: (0x01, 0x03, 0x00, 0x167E),   # obsidian long sword
    48: (0x12, 0x83, 0x00, 0x1F77),   # chatkcha
    57: (0x00, 0x04, 0x80, 0x126F),   # chain chest armour
    62: (0x00, 0x80, 0x02, 0x177B),   # arrows
    65: (0x00, 0x05, 0x00, 0x1FFF),   # cloak
    81: (0x01, 0x01, 0x00, 0x1678),   # bone long sword
    89: (0x00, 0x84, 0x84, 0x1FFF),   # Helm of Contemplation (metal)
    90: (0x00, 0x40, 0x80, 0x176F),   # silk armour (no material)
    112: (0x01, 0x02, 0x00, 0x177A),  # stone pick
}
FLAGS = {1: 0x1, 2: 0x2, 3: 0x4, 4: 0x8, 5: 0x10, 6: 0x10, 7: 0x10, 8: 0x10, 9: 0x20, 10: 0x40,
         11: 0x80, 12: 0x100, 13: 0x200, 14: 0x200, 15: 0x200, 16: 0x200, 17: 0x400}


def record(t):
    flags, mat, kind, mask = TYPES[t]
    r = bytearray(game.ITEM_TYPE_SIZE)
    r[0], r[8], r[0x0F] = flags, mat, kind
    r[0x10:0x12] = mask.to_bytes(2, "little")
    return bytes(r)


def sheet(*classes, race=2):
    s = bytearray(game.SHEET_SIZE)
    s[game.SHEET_RACE] = race
    s[game.SHEET_CLASSES:game.SHEET_CLASSES + len(classes)] = bytes(classes)
    flags = 0
    for c in classes:
        flags |= FLAGS[c]
    s[game.SHEET_FLAGS:game.SHEET_FLAGS + 2] = flags.to_bytes(2, "little")
    return bytes(s)


def ok(s, t):
    return restrict.allowed(s, t, record(t))


def usable(s, t):
    """Both the game's mask and the restrictions."""
    mask = TYPES[t][3] & int.from_bytes(s[game.SHEET_FLAGS:game.SHEET_FLAGS + 2], "little")
    return bool(mask) and ok(s, t)


class RestrictTests(unittest.TestCase):
    def test_kinds_of_item(self):
        self.assertTrue(restrict.is_armour(record(5)))
        self.assertTrue(restrict.is_armour(record(89)))
        self.assertFalse(restrict.is_armour(record(4)))
        self.assertTrue(restrict.is_shield(record(16)))
        self.assertEqual([restrict.is_light(record(t)) for t in (6, 90, 9, 57, 89)], [True, True, False, False, False])
        self.assertEqual(restrict.material(record(90)), -1)
        self.assertEqual(restrict.material(record(1)), restrict.WOOD)

    def test_fighter_as_the_game(self):
        self.assertTrue(all(ok(sheet(9), t) for t in TYPES))

    def test_psionicist(self):
        psi = sheet(12)
        self.assertEqual([t for t in TYPES if not ok(psi, t)], [0, 3, 9, 16, 22, 45, 57, 81, 89, 112])
        # whatever the other class allows
        self.assertFalse(ok(sheet(9, 12), 57))
        self.assertFalse(ok(sheet(9, 12), 45))
        self.assertTrue(ok(sheet(9, 12), 4))

    def test_multiclass_thief(self):
        self.assertTrue(ok(sheet(17), 57))  # (one class: the game's own lists)
        self.assertFalse(ok(sheet(9, 17), 57))
        self.assertTrue(ok(sheet(9, 17), 6))
        self.assertTrue(ok(sheet(9, 17), 90))
        self.assertTrue(ok(sheet(9, 17), 4))   # a leather shield the fighter may use
        self.assertFalse(ok(sheet(9, 17), 16))  # wooden
        self.assertFalse(ok(sheet(11, 17), 4))  # no other class may
        self.assertTrue(usable(sheet(17), 4))  # (the game lets a thief alone)

    def test_preserver(self):
        self.assertFalse(ok(sheet(11), 89))
        self.assertFalse(ok(sheet(11), 4))
        self.assertTrue(ok(sheet(11), 65))
        self.assertTrue(ok(sheet(9, 11), 57))  # multiclass: the fighter's armour
        self.assertTrue(ok(sheet(9, 11), 16))

    def test_druid(self):
        for druid in range(5, 9):
            self.assertFalse(ok(sheet(druid), 89))
            self.assertFalse(ok(sheet(druid, 9), 6))
            self.assertFalse(ok(sheet(druid, 9), 4))
            self.assertTrue(ok(sheet(druid, 9), 65))

    def test_cloak_of_protection(self):
        # its type counts for AC (+0Fh 80h) but is worn as a cloak: no armour, for anyone
        from dsloader import npcitems
        cloak = npcitems.TYPES[1]
        self.assertFalse(restrict.is_armour(cloak))
        for classes in ((5,), (9, 5, 17), (11,), (12,), (9, 17)):
            self.assertTrue(restrict.usable(sheet(*classes), game.CLOAK_TYPE, cloak), classes)

    def test_cleric_spheres(self):
        allowed = lambda cls: [t for t in TYPES if TYPES[t][0] & 3 and ok(sheet(cls), t)]
        self.assertEqual(allowed(1), [0, 1, 17, 29, 37, 48])   # air: missile, thrown, daggers
        self.assertEqual(allowed(2), [1, 3, 17, 18, 22, 29, 37, 45, 48, 112])  # earth (the chatkcha obsidian)
        self.assertEqual(allowed(3), [17, 29, 37, 45, 48])   # fire: obsidian
        self.assertEqual(allowed(4), [1, 3, 18, 20, 29, 37, 81])   # water: bone, wood
        self.assertFalse(ok(sheet(9, 3), 81))  # multiclass too
        self.assertTrue(ok(sheet(3), 57))  # (armour as the game has it)

    def test_dual_class(self):
        human = dict(race=game.HUMAN)
        self.assertTrue(ok(sheet(3, 16, **human), 81))   # ranger (water) then cleric (fire): both spheres
        self.assertTrue(ok(sheet(3, 16, **human), 45))
        self.assertFalse(ok(sheet(3, 16, **human), 22))
        self.assertTrue(ok(sheet(9, 3, **human), 81))  # a cleric now a fighter: the fighter's rules
        self.assertFalse(ok(sheet(12, 9, **human), 57))  # a fighter now a psionicist


    def test_no_spells_in_armour(self):
        worn = [record(5)]  # a helm
        self.assertTrue(restrict.no_spells(sheet(9, 11), worn))
        self.assertTrue(restrict.no_spells(sheet(11, 17), [record(6)]))
        self.assertFalse(restrict.no_spells(sheet(9, 11), [record(4), record(65)]))  # shield, cloak
        self.assertFalse(restrict.no_spells(sheet(11), worn))
        self.assertFalse(restrict.no_spells(sheet(11, 9, race=game.HUMAN), worn))
        self.assertFalse(restrict.no_spells(sheet(9, 17), worn))


    def test_dual_class_keeps_specialized_weapons(self):
        """A fighter turned psionicist keeps the long sword it specialized in, once its new level
        passes its fighter level; never another kind."""
        s = bytearray(sheet(12, 9, race=game.HUMAN))
        s[game.SPEC_SLOTS] = 1  # (the long sword)
        s[game.SHEET_LEVELS:game.SHEET_LEVELS + 2] = bytes((4, 5))
        self.assertFalse(ok(bytes(s), 45))
        s[game.SHEET_LEVELS] = 6
        self.assertTrue(ok(bytes(s), 45))
        self.assertTrue(ok(bytes(s), 81))  # (any long sword)
        self.assertFalse(ok(bytes(s), 22))  # an axe: not its kind
        self.assertFalse(ok(bytes(s), 57))  # (armour: the psionicist's limits as before)

    def test_rangers_bow(self):
        """A ranger's bow is its own: a fire cleric/fire ranger may use it (the fire sphere alone
        forbids it), and a human fire ranger turned fire cleric once its cleric level passes."""
        self.assertFalse(ok(sheet(3), 1))  # a fire cleric: no bow
        self.assertTrue(ok(sheet(3, 15), 1))  # with fire ranger: the bow
        self.assertTrue(ok(sheet(15, 3), 1))
        self.assertFalse(ok(sheet(3, 15), 22))  # (the axe: still the cleric's rule)
        s = bytearray(sheet(3, 15, race=game.HUMAN))
        s[game.SHEET_LEVELS:game.SHEET_LEVELS + 2] = bytes((4, 5))
        self.assertFalse(ok(bytes(s), 1))  # a cleric not yet past its ranger level
        s[game.SHEET_LEVELS] = 6
        self.assertTrue(ok(bytes(s), 1))
        self.assertTrue(ok(sheet(15, 3, race=game.HUMAN), 1))  # a ranger now


if __name__ == "__main__":
    unittest.main()
