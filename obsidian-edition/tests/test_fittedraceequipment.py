import unittest
from itertools import permutations

from dsloader import classoutfits as co, game, kitpages


class FittedRaceEquipmentTests(unittest.TestCase):
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
