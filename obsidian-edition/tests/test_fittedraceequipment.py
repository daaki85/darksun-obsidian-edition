import unittest
from itertools import permutations

from dsloader import classoutfits as co, game, kitpages


class FittedRaceEquipmentTests(unittest.TestCase):
    def test_halfgiant_arm_armor_has_two_guards_when_both_arms_are_visible(self):
        for model in (2072, 2074):
            for role in co.FITTED_ROLES[co.FITTED_RACES[model]].values():
                walk = co.frames(role, False, model)
                combat = co.frames(role, True, model)
                for frame in walk + combat:
                    self.assertTrue(frame.regions[co.ARMS], (model, role))
                if role == "Psionicist":
                    for pose, split in ((0, 13), (1, 13), (7, 10), (8, 12), (9, 10), (10, 10)):
                        arms = walk[pose].regions[co.ARMS]
                        self.assertGreaterEqual(sum(x < split for x, _ in arms), 3)
                        self.assertGreaterEqual(sum(x > split for x, _ in arms), 3)

    def test_halfgiant_equipped_cloak_follows_the_ranger_under_the_rear_hair(self):
        rear_poses = (1, 7, 8, 9, 10, 18, 19, 20, 25, 28)
        for model in (2072, 2074):
            ranger = co.frames("Ranger", False, model) + co.frames("Ranger", True, model)
            for role in co.FITTED_ROLES[co.FITTED_RACES[model]].values():
                outfit = co.frames(role, False, model) + co.frames(role, True, model)
                for pose in rear_poses:
                    with self.subTest(model=model, role=role, pose=pose):
                        frame = outfit[pose]
                        native_cloth = {(x, y) for x, y, _ in ranger[pose].cloak}
                        for part in (co.FOREARM, co.BOW, co.LEFT_FOOT, co.RIGHT_FOOT):
                            native_cloth.difference_update(frame.regions[part])
                        surface = frame.cloak if frame.native_cloak else frame.equipped_cape
                        self.assertTrue(native_cloth <= {(x, y) for x, y, _ in surface})

    def test_both_halflings_keep_the_worn_cloak_over_their_rear_belt_and_kilt(self):
        for model in (2068, 2070):
            for role in ("Druid/Fighter", "Psionicist/Ranger", "Fighter/Psionicist/Thief"):
                walk = co.frames(role, False, model)
                reference = co.frames("Ranger", False, model)
                for pose in (1, 7, 8, 9, 10):
                    with self.subTest(model=model, role=role, pose=pose):
                        cape = {(x, y) for x, y, _ in walk[pose].equipped_cape}
                        # The belt and short kilt used to cut across the outer
                        # cloak here. The long panel follows the Ranger hem.
                        hem = {(x, y) for x, y, _ in reference[pose].equipped_cape if y >= 13}
                        self.assertTrue(hem)
                        self.assertTrue(hem.issubset(cape))
                        self.assertTrue(cape.isdisjoint(walk[pose].regions[co.FOREARM]))

    def test_creation_selects_only_registered_outfits_on_the_matching_figure(self):
        creation = {group: key for key, group in kitpages.CREATION_CLASS.items()}
        for obj, model in co.FITTED_MODELS.items():
            race = co.FITTED_RACES[model]
            sheet = bytearray(game.SHEET_SIZE)
            sheet[game.SHEET_RACE] = race
            for groups, role in co.FITTED_ROLES[race].items():
                for arranged in permutations(groups):
                    slots = bytes([creation[g] for g in arranged]).ljust(3, b"\0")
                    sheet[game.SHEET_CLASSES:game.SHEET_CLASSES+3] = slots
                    self.assertEqual(co.for_sheet(sheet, model), role, (obj, arranged))
            self.assertIsNone(co.for_sheet(sheet, 2095))
            sheet[game.SHEET_CLASSES:game.SHEET_CLASSES+3] = bytes((creation[4], creation[3], 0))
            self.assertIsNone(co.for_sheet(sheet, model))

    def test_every_pose_has_native_ownership_and_keeps_equipment_off_the_bow(self):
        for model in co.FITTED_MODELS.values():
            race = co.FITTED_RACES[model]
            for role in co.FITTED_ROLES[race].values():
                frames = co.frames(role, False, model) + co.frames(role, True, model)
                self.assertEqual(len(frames), 29)
                for pose, frame in enumerate(frames):
                    with self.subTest(model=model, role=role, pose=pose):
                        regions = frame.regions
                        bow = set(regions[co.BOW])
                        self.assertIsNotNone(frame.belt)
                        self.assertTrue(bow.isdisjoint(frame.belt))
                        cloak = {(x, y) for x, y, _ in frame.cloak}
                        cape = {(x, y) for x, y, _ in frame.equipped_cape}
                        self.assertTrue(bow.isdisjoint(cloak | cape))
                        for foot in (co.LEFT_FOOT, co.RIGHT_FOOT):
                            self.assertTrue(bow.isdisjoint(regions[foot]))
                        self.assertTrue(set(regions[co.LEFT_FOOT]).isdisjoint(regions[co.RIGHT_FOOT]))
                        for slot in (co.CHEST, co.ARMS, co.LEGS):
                            self.assertTrue(bow.isdisjoint(regions[slot]))
