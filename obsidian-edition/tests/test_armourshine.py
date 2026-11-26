"""A worn piece shines on its visible slot and keeps the neighbouring equipment intact."""

import os
from pathlib import Path
import unittest
from unittest.mock import patch

from dsloader import art, classoutfits as co, game, spritegear as sg, sprites


def magic(kind, group):
    return kind | sg.MAGIC_ARMOUR | (group << sg.GLOW_SHIFT)


@unittest.skipUnless(os.environ.get("DSUN_OBJECTS"), "needs the player's SEGOBJEX.GFF")
class ArmourShineTests(unittest.TestCase):
    def setUp(self):
        self.addCleanup(sg.set_palette, list(sg._RGB))
        dresser = sprites.Dresser.for_game(None, str(Path(os.environ["DSUN_OBJECTS"]).parent))
        if dresser is None:
            self.skipTest("needs the retail objects and palette in the game directory")
        self.pictures = dresser.pics

    def changes(self, obj, role, pose, before, after, equipment=None):
        combat, frame = divmod(pose, 15)
        equipment = equipment or {}
        def render(pieces):
            chunk = self.pictures.build(obj, combat, equipment, pieces, role=role)
            return art.decode_frame(chunk, frame)[2]
        old, new = render(before), render(after)
        sx, sy = sprites.room(combat)
        diff = {(x-sx, y-sy): value for y, row in enumerate(new) for x, value in enumerate(row)
                if value != old[y][x]}
        self.assertTrue(all(value is not None and old[y+sy][x+sx] is not None
                            for (x, y), value in diff.items()))
        return diff

    def test_distinct_cycle_phases_on_both_visible_arm_guards(self):
        # Bare upper arms on these classes still have visible wrists, including the
        # Mul's small blue-toned guards, which used to remain completely bare.
        for obj, role, left, right, y in ((309, "Psionicist", 2, 26, 17),
                                         (312, "Druid", 2, 21, 13),
                                         (312, "Fighter", 2, 21, 13),
                                         (300, None, 1, 19, 12)):
            with self.subTest(obj=obj, role=role):
                glow = self.changes(obj, role, 0, (25,), (magic(25, sg.BLUE_GLOW),))
                for cx in (left, right):
                    self.assertTrue(any(abs(a-cx) <= 2 and abs(b-y) <= 2 for a, b in glow))
                self.assertGreaterEqual(len(set(glow.values())), 2)
                self.assertTrue(set(glow.values()).issubset(sg.GLOWS[sg.BLUE_GLOW]))
                plain = self.changes(obj, role, 0, (), (25,))
                self.assertTrue(all(any(abs(x-cx) <= 2 and abs(yy-y) <= 2 for x, yy in plain)
                                    for cx in (left, right)))
        self.assertFalse(self.changes(313, None, 0, (25,), (magic(25, sg.BLUE_GLOW),)))

    def test_long_narrow_gladiator_straps_have_two_phases_with_leather_between(self):
        for obj in (300, 301):
            original = self.changes(obj, "Gladiator", 0, (), (88,))
            shine = self.changes(obj, "Gladiator", 0, (88,), (magic(88, sg.BLUE_GLOW),))
            self.assertEqual(len(set(shine.values())), 2)
            self.assertGreaterEqual(max(y for x, y in shine) - min(y for x, y in shine), 3)
            self.assertTrue(set(original)-set(shine))

    def test_chest_arms_and_legs_cycle_independently_in_the_same_suit(self):
        # Using different real DAC runs lets this check detect a slot's shine
        # even if the neighbouring chest and pauldron dyes share a plate shade.
        pieces = (88, 25, 26)
        groups = (sg.BLUE_GLOW, sg.VIOLET_GLOW, sg.GREEN_GLOW)
        enchanted = tuple(magic(k, g) for k, g in zip(pieces, groups))
        for obj, role in ((303, "Fighter"), (309, "Psionicist"), (300, None)):
            with self.subTest(obj=obj):
                joined = {}
                for k, g in zip(pieces, groups):
                    diff = self.changes(obj, role, 0, (k,), (magic(k, g),))
                    self.assertTrue(diff)
                    self.assertFalse(joined.keys() & diff.keys())
                    joined.update(diff)
                self.assertEqual(self.changes(obj, role, 0, pieces, enchanted), joined)
                with_shield = self.changes(obj, role, 0, pieces, enchanted,
                                           {"left": (4, 0), "cloak": (65, 5)})
                self.assertLessEqual(with_shield.items(), joined.items())

    def test_bent_knee_cannot_reposition_the_other_slots_wrist_glint(self):
        for obj, pose in ((300, 17), (312, 17), (301, 16), (304, 16), (307, 16)):
            with self.subTest(obj=obj, pose=pose):
                arms = magic(25, sg.BLUE_GLOW)
                alone = self.changes(obj, None, pose, (25,), (arms,))
                suited = self.changes(obj, None, pose, (88, 25, 26), (88, arms, 26))
                self.assertEqual(alone, suited)

    def test_stock_giant_charcoal_cuffs_in_front_of_the_chest_keep_their_own_material(self):
        for obj in (308, 309):
            with self.subTest(obj=obj):
                chest = self.changes(obj, None, 12, (), (magic(88, sg.BLUE_GLOW),))
                arms = self.changes(obj, None, 12, (25,), (magic(25, sg.GREEN_GLOW),))
                self.assertTrue(arms)
                self.assertTrue(set(arms).isdisjoint(chest))
                # Three cells on the cuff used to take the chest dye because
                # their original charcoal is shared with the black harness.
                protected = {(19, 13), (8, 16), (9, 17)} if obj == 308 else {(19, 14), (8, 17), (9, 18)}
                self.assertTrue(protected.isdisjoint(chest))

    def test_fitted_native_drape_face_trim_and_bow_do_not_take_plate_shine(self):
        for obj, model, role, pose in ((302, 2055, "Cleric/Fighter", 7),
                                      (305, 2059, "Preserver/Thief", 12),
                                      (309, 2074, "Ranger", 25)):
            with self.subTest(role=role):
                combat, frame = divmod(pose, 15)
                fit = co.frames(role, combat, model)[frame]
                protected = {(x, y) for x, y, _ in fit.cloak} | set(fit.head) | fit.armor_trim
                protected.update(fit.regions[co.BOW])
                worn = tuple(magic(k, sg.BLUE_GLOW) for k in (88, 25, 26))
                self.assertTrue(protected.isdisjoint(self.changes(obj, role, pose, (), worn)))

    def test_stock_magic_still_shows_when_the_material_matches_the_native_clothing(self):
        native = sg.CLOTHES[2095]
        with patch.dict(sg.ARMOUR, {88: (sg.ARMOUR_CHEST, native, sg.PLAIN)}):
            self.assertFalse(self.changes(300, None, 0, (), (88,)))
            self.assertGreater(len(self.changes(300, None, 0, (88,), (magic(88, sg.BLUE_GLOW),))), 2)

    def test_robe_with_plain_greaves_only_shines_on_its_exposed_upper_cloth(self):
        robe = magic(game.ROBE_TYPE, sg.VIOLET_GLOW)
        for obj, role, model in ((300, "Priest", 2095), (303, "Cleric", 2053)):
            with self.subTest(obj=obj):
                with_greaves = self.changes(obj, role, 0, (game.ROBE_TYPE, 26), (robe, 26))
                frame = co.frames(role, False, model)[0]
                self.assertTrue(with_greaves)
                self.assertTrue(set(with_greaves) <= set(frame.regions[co.CHEST]))

    def test_stock_leg_material_stays_above_the_human_boots_and_off_the_retail_bow(self):
        shine = self.changes(300, None, 0, (26,), (magic(26, sg.FIRE_GLOW),))
        self.assertTrue(shine)
        self.assertTrue(all(y == 15 for x, y in shine))
        # Where a retail hem has vanished behind a raised leg, plate can still
        # appear on the exposed calf, without painting the boots or a closed cloak.
        for obj, pose, exposed in ((300, 15, {(11, 25), (11, 26), (12, 25), (12, 26)}),
                                   (311, 12, {(2, 13), (2, 14), (3, 12), (11, 14), (11, 15)})):
            changed = self.changes(obj, None, pose, (), (magic(26, sg.BLUE_GLOW),))
            self.assertEqual(set(changed), exposed)
        self.assertFalse(self.changes(301, None, 28, (), (magic(26, sg.FIRE_GLOW),)))
        for obj, model in ((300, 2095), (310, 2070)):
            for pose in (24, 25, 26):
                role = "Warrior" if obj == 300 else "Fighter"
                bow = co.frames(role, True, model)[pose-15].regions[co.BOW]
                covered = self.changes(obj, None, pose, (), tuple(magic(k, sg.BLUE_GLOW) for k in (88, 25, 26)))
                self.assertTrue(set(bow).isdisjoint(covered))
