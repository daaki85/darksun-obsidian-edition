import os
import unittest
from pathlib import Path
from zipfile import ZipFile

from dsloader import art, classoutfits, game, gff, spritegear as sg, sprites


class HumanOutfitTests(unittest.TestCase):
    def test_class_uses_current_slot_of_human_sheet(self):
        sheet = bytearray(game.SHEET_SIZE)
        sheet[game.SHEET_RACE] = game.HUMAN
        sheet[game.SHEET_CLASSES:game.SHEET_CLASSES + 2] = (11, 9)
        self.assertEqual(classoutfits.for_sheet(sheet), "Mage")
        sheet[game.SHEET_CLASSES] = 17
        self.assertEqual(classoutfits.for_sheet(sheet), "Thief")
        sheet[game.SHEET_RACE] = game.HALFLING
        self.assertIsNone(classoutfits.for_sheet(sheet))
        self.assertIsNone(classoutfits.for_sheet(b""))

    def test_both_feet_repaint_independently_of_the_clothing_palette(self):
        # A lifted foot ends three rows above the planted one. The robe between them
        # and the stock picture (used for locating hands) must retain their colours.
        stock = [[None, 69, 69, None] for _ in range(8)]
        costume = classoutfits.Frame([[None, 130, 58, 130] for _ in stock],
                                     {classoutfits.LEFT_FOOT: [(1, 7)], classoutfits.RIGHT_FOOT: [(3, 4)]})
        plain = sg.armed(stock, 2095, 0, False, {}, costume=costume)
        boots = sg.armed(stock, 2095, 0, False, {"boots": (68, 5)}, costume=costume)
        changed = {(x - 10, y - 10) for y, row in enumerate(boots) for x, p in enumerate(row) if plain[y][x] != p}
        self.assertEqual(changed, {(1, 7), (3, 4)})
        self.assertEqual(sg.armed(stock, 2095, 0, False, {}, costume=costume), plain)

    def test_art_and_masks_register_to_the_same_native_pixels(self):
        for role in classoutfits.CLASSES[1:]:
            for combat in (False, True):
                poses = classoutfits.frames(role, combat)
                self.assertEqual(len(poses), 14 if combat else 15)
                for f, pose in enumerate(poses):
                    side = 8 if not combat and f == 13 else 6
                    w = len(pose.image[0]) - 2 * side
                    source = [[42] * w for _ in pose.image[6:]]
                    canvas = pose.canvas(source, 10)
                    for cells in pose.regions.values():
                        for x, y in cells:
                            self.assertIsNotNone(canvas[10 + y][10 + x], (role, combat, f, x, y))
                    left = set(pose.regions[classoutfits.LEFT_FOOT])
                    right = set(pose.regions[classoutfits.RIGHT_FOOT])
                    self.assertFalse(left & right)
                    if role == "Mage":
                        self.assertTrue(left and right, (combat, f))

    def test_plate_and_cloak_have_independent_colours_and_magic(self):
        magic_plate = 88 | sg.MAGIC_ARMOUR | (sg.BLUE_GLOW << sg.GLOW_SHIFT)
        magic_cloak = (65, 5, sg.MAGIC, sg.GREEN_GLOW)
        for combat in (False, True):
            for f, pose in enumerate(classoutfits.frames("Mage", combat)):
                side = 8 if not combat and f == 13 else 6
                stock = [row[side:-side] for row in pose.image[6:]]
                chest = set(pose.regions[classoutfits.CHEST])
                mantle = {(x, y) for x, y, _ in pose.cloak}
                self.assertTrue(mantle.isdisjoint(chest))
                for item in (None, (65, 5), magic_cloak):
                    gear = {"cloak": item} if item else {}
                    baseline, plain, enchanted = (
                        sg.armed(stock, 2095, f, combat, gear, armour=armour, costume=pose)
                        for armour in ((), (88,), (magic_plate,)))
                    for x, y, shade in pose.cloak:
                        expected = baseline[y + 10][x + 10]
                        self.assertEqual(plain[y + 10][x + 10], expected)
                        self.assertEqual(enchanted[y + 10][x + 10], expected)
                        if item == (65, 5):
                            self.assertEqual(expected, sg.CLOAK_COLOURS[65][shade])
                    if item == magic_cloak:
                        self.assertTrue(any(enchanted[y + 10][x + 10] in sg.GLOWS[sg.GREEN_GLOW]
                                            for x, y in mantle))
                    changed = {(x - 10, y - 10) for y, row in enumerate(enchanted)
                               for x, pixel in enumerate(row) if pixel != plain[y][x]}
                    self.assertLessEqual(changed, chest)
                    self.assertEqual(bool(changed), bool(chest))
                    for x, y in changed:
                        self.assertIn(enchanted[y + 10][x + 10], sg.GLOWS[sg.BLUE_GLOW])

    def test_sewn_in_cloaks_do_not_share_armour_masks(self):
        for role in ("Mage", "Thief", "Druid", "Ranger", "Psionicist"):
            for combat in (False, True):
                for pose in classoutfits.frames(role, combat):
                    cape = {(x, y) for x, y, _ in pose.cloak}
                    for bit in (classoutfits.CHEST, classoutfits.ARMS, classoutfits.LEGS):
                        self.assertTrue(cape.isdisjoint(pose.regions[bit]))

    def test_shield_is_on_the_raised_wrist_in_melee_follow_through(self):
        pose = classoutfits.frames("Mage", True)[2]
        stock = [row[6:-6] for row in pose.image[6:]]
        geared = sg.armed(stock, 2095, 2, True, {"left": (4, 0)}, costume=pose)
        # The free hand crosses above the crown. The boss must cover that wrist.
        self.assertEqual(geared[10 + 1][10 + 10], sg.MATERIAL_COLOURS[0][2])
        self.assertEqual(geared[10 + 8][10 + 13], stock[8][13])

    def test_side_bow_is_the_foreground_with_helm_and_quiver(self):
        pose = classoutfits.frames("Priest", True)[11]
        stock = [row[6:-6] for row in pose.image[6:]]
        geared = sg.armed(stock, 2095, 11, True, {"helm": (game.BONE_HELM_TYPE, 1),
                           "ammo": (62, 0), "cloak": (65, 5)}, costume=pose)
        for x, y in pose.regions[classoutfits.BOW]:
            self.assertEqual(geared[y + 10][x + 10], stock[y][x])
        self.assertIsNone(geared[10][10 + 13])  # the old spike was on the tip of the bow

    def test_open_necklines_clear_native_jaw_and_ponytail(self):
        runs = [(False, 0, 8, 6, 5), (False, 1, 10, 6, 4), (True, 2, 12, 9, 5)]
        for combat, f, left, y, length in runs:
            for role in ("Priest", "Warrior", "Psionicist"):
                with self.subTest(role=role, combat=combat, frame=f):
                    pose = classoutfits.frames(role, combat)[f]
                    cells = {(x, y) for x in range(left, left + length)}
                    # These cells retain whatever is in the player's original picture.
                    self.assertTrue(all(pose.image[yy + 6][x + 6] is None for x, yy in cells))
                    self.assertTrue(cells.isdisjoint((x, y) for x, y, _ in pose.cloak))
                    for bit in (classoutfits.CHEST, classoutfits.ARMS, classoutfits.LEGS):
                        self.assertTrue(cells.isdisjoint(pose.regions[bit]))

    def test_woman_has_independent_outfit_layers(self):
        for combat, count in ((False, 15), (True, 14)):
            for role in classoutfits.CLASSES[1:]:
                poses = classoutfits.frames(role, combat, 2099)
                self.assertEqual(len(poses), count)
                self.assertIsNot(poses, classoutfits.frames(role, combat, 2095))
                for f, pose in enumerate(poses):
                    bow = set(pose.regions[classoutfits.BOW])
                    self.assertEqual(bool(bow), combat and f in (9, 10, 11))
                    cloak = {(x, y) for x, y, _ in pose.cloak}
                    self.assertTrue(bow.isdisjoint(cloak))
                    if role in ("Mage", "Thief", "Druid", "Ranger", "Psionicist"):
                        for part in (classoutfits.CHEST, classoutfits.ARMS, classoutfits.LEGS):
                            self.assertTrue(cloak.isdisjoint(pose.regions[part]))

    @unittest.skipUnless(os.environ.get("DSUN_OBJECTS"), "needs the player's SEGOBJEX.GFF")
    def test_human_woman_picture_and_cloak_in_the_loader(self):
        chunks = gff.read_gff(Path(os.environ["DSUN_OBJECTS"]).read_bytes())
        pictures = sprites.Pictures(chunks)
        self.assertTrue(pictures.supports_outfits(301, pictures.model(301)))
        self.assertFalse(pictures.supports_outfits(301, 2095))
        self.assertFalse(pictures.supports_outfits(303, 2099))
        self.assertFalse(classoutfits.supports({("BMP ", 2099): chunks["BMP ", 2099]}, 2099))
        magic = (88 | sg.MAGIC_ARMOUR | (sg.BLUE_GLOW << sg.GLOW_SHIFT),)
        for combat in (False, True):
            side, top = sprites.room(combat)
            plain = pictures.build(301, combat, {}, (), role="Mage")
            plate = pictures.build(301, combat, {}, magic, role="Mage")
            cloaked = pictures.build(301, combat, {"cloak": (65, 5)}, magic, role="Mage")
            self.assertNotEqual(plain, plate)
            for f, pose in enumerate(classoutfits.frames("Mage", combat, 2099)):
                original = pictures.own(2099 + combat)[f]
                base, wearing, covered = [art.decode_frame(chunk, f)[2] for chunk in (plain, plate, cloaked)]
                for x, y, rank in pose.cloak:
                    self.assertEqual(wearing[y + top][x + side], base[y + top][x + side])
                    self.assertEqual(covered[y + top][x + side], sg.CLOAK_COLOURS[65][rank])
                for x, y in pose.regions[classoutfits.BOW]:
                    self.assertEqual(covered[y + top][x + side], original[y][x])

    def test_woman_recoil_boots_follow_the_kick(self):
        for role in classoutfits.CLASSES[1:]:
            pose = classoutfits.frames(role, True, 2099)[12]
            raised = pose.regions[classoutfits.LEFT_FOOT]
            grounded = pose.regions[classoutfits.RIGHT_FOOT]
            self.assertTrue(raised and grounded, role)
            self.assertGreater(min(x for x, y in raised), max(x for x, y in grounded), role)
            self.assertLess(max(y for x, y in raised), min(y for x, y in grounded), role)

    def test_long_back_capes_extend_below_the_braid(self):
        for role in ("Thief", "Mage", "Ranger"):
            poses = classoutfits.frames(role, False, 2099)
            for f in (1, 7, 8, 9, 10):
                hem = [x for x, y, _ in poses[f].cloak if y >= 17]
                self.assertTrue(hem, (role, f))
                self.assertGreaterEqual(max(hem) - min(hem), 10, (role, f))

    def test_woman_fighters_and_psionicist_keep_shared_head_and_rebuilt_rear_arms(self):
        with ZipFile(Path(classoutfits.__file__).with_name("woman_outfit_layers.zip")) as archive:
            for combat, tag in ((False, "walk"), (True, "combat")):
                body = archive.read(f"Base/{tag}")
                for role in ("Warrior", "Gladiator", "Psionicist"):
                    for f, pose in enumerate(classoutfits.frames(role, combat, 2099)):
                        base = art.decode_frame(body, f)[2]
                        self.assertTrue(pose.head)
                        for x, y in pose.head:
                            self.assertEqual(pose.image[y + 6][x + 6], base[y + 6][x + 6], (role, f))
                        if not combat and f in (1, 7, 8, 9, 10):
                            arms = [x for x, y in pose.regions[classoutfits.FOREARM] if y == 10]
                            self.assertTrue(any(x <= 5 for x in arms), (role, f))
                            self.assertTrue(any(x >= 14 for x in arms), (role, f))

    def test_druid_rear_idle_and_walk_have_a_draped_hem(self):
        poses = classoutfits.frames("Druid", False, 2099)
        hems = []
        for f in (1, 7, 8, 9, 10):
            hem = {}
            for x, y, _ in poses[f].cloak:
                hem[x] = max(y, hem.get(x, 0))
            bottom = max(hem.values())
            self.assertGreaterEqual(bottom, 16, f)
            self.assertGreaterEqual(len({y for y in hem.values() if y >= bottom - 2}), 3, f)
            hems.append(bottom)
        self.assertLessEqual(max(hems) - min(hems), 2)

    def test_woman_raised_hands_remain_in_front_of_clothing(self):
        for role in classoutfits.CLASSES[1:]:
            poses = classoutfits.frames(role, True, 2099)
            for f, cells in ((2, {(11, 0), (12, 0), (13, 1)}), (11, {(2, 8), (6, 7), (7, 7)})):
                pose = poses[f]
                self.assertTrue(cells.issubset(pose.regions[classoutfits.FOREARM]), (role, f))
                self.assertTrue(cells.isdisjoint((x, y) for x, y, shade in pose.cloak), (role, f))

    def test_woman_front_bow_mask_leaves_the_ankle_and_face_free(self):
        for role in classoutfits.CLASSES[1:]:
            pose = classoutfits.frames(role, True, 2099)[9]
            bow = pose.regions[classoutfits.BOW]
            self.assertIn((16, 6), bow)
            self.assertNotIn((10, 6), bow)
            self.assertNotIn((1, 21), bow)
            # The priest's hem covers the ankle in this pose.
            region = classoutfits.LEGS if role == "Priest" else classoutfits.LEFT_FOOT
            self.assertIn((1, 21), pose.regions[region])

    def test_woman_rear_idle_boots_rest_side_by_side(self):
        for role in classoutfits.CLASSES[1:]:
            pose = classoutfits.frames(role, False, 2099)[1]
            left = pose.regions[classoutfits.LEFT_FOOT]
            right = pose.regions[classoutfits.RIGHT_FOOT]
            self.assertTrue(left and right, role)
            self.assertLess(max(x for x, _ in left), min(x for x, _ in right), role)
            self.assertLessEqual(abs(max(y for _, y in left) - max(y for _, y in right)), 1, role)


class DwarfOutfitTests(unittest.TestCase):
    def test_legal_builds_resolve_independently_of_slot_order(self):
        sheet = bytearray(game.SHEET_SIZE)
        sheet[game.SHEET_RACE] = game.DWARF
        for slots, expected in (
            ((4, 0, 0), "Cleric"), ((17, 9, 12), "Fighter/Psionicist/Thief"),
            ((12, 4, 9), "Cleric/Fighter/Psionicist"), ((17, 12, 0), "Psionicist/Thief"),
            ((11, 0, 0), None), ((10, 9, 0), None), ((9, 255, 0), None),
        ):
            sheet[game.SHEET_CLASSES:game.SHEET_CLASSES + 3] = slots
            self.assertEqual(classoutfits.for_sheet(sheet, 2053), expected)
            self.assertEqual(classoutfits.for_sheet(sheet, 2055), expected)
            self.assertIsNone(classoutfits.for_sheet(sheet, 2099))

    def test_front_faces_stay_open_in_every_build(self):
        # These coordinates follow the original brow down through the cheek.
        # The woman stands upright in the opening strike while the man leans.
        for model in classoutfits.DWARVES:
            opening = (10, 2) if model == 2053 else (7, 4)
            for combat, landmarks in (
                (False, {0: (10, 2), 3: (9, 2), 4: (9, 2), 5: (9, 2), 6: (10, 2)}),
                (True, {0: opening, 1: (11, 2), 2: (8, 6), 9: (8, 2), 12: (3, 6)}),
            ):
                for role in classoutfits.DWARF_ROLES.values():
                    poses = classoutfits.frames(role, combat, model)
                    for f, (x, brow) in landmarks.items():
                        with self.subTest(model=model, role=role, combat=combat, frame=f):
                            pose = poses[f]
                            for y in range(brow, brow + 3):
                                self.assertIn((x, y), pose.head)
                                self.assertIsNone(pose.image[y + 4][x + 4])
                                self.assertNotIn((x, y), pose.regions[classoutfits.CHEST])
                                self.assertFalse(any((x, y) == (u, v) for u, v, _ in pose.cloak))

    @unittest.skipUnless(os.environ.get("DSUN_OBJECTS"), "needs the player's SEGOBJEX.GFF")
    def test_shoulder_guards_follow_original_arm_silhouettes(self):
        pictures = sprites.Pictures(gff.read_gff(Path(os.environ["DSUN_OBJECTS"]).read_bytes()))
        for model in classoutfits.DWARVES:
            for combat in (False, True):
                originals = pictures.own(model + combat)
                fighters = classoutfits.frames("Fighter", combat, model)
                for role in classoutfits.DWARF_ROLES.values():
                    if "Fighter" not in role and role != "Gladiator":
                        continue
                    for f, pose in enumerate(classoutfits.frames(role, combat, model)):
                        with self.subTest(model=model, role=role, combat=combat, frame=f):
                            guard = set(pose.regions[classoutfits.ARMS])
                            self.assertTrue(guard.isdisjoint(pose.head))
                            self.assertTrue(all(originals[f][y][x] is not None for x, y in guard))
                            if "Fighter" in role:
                                self.assertTrue(guard)
                                self.assertTrue(guard.issubset(fighters[f].regions[classoutfits.ARMS]))

    def test_raised_foot_and_hit_hood_follow_native_landmarks(self):
        for model in classoutfits.DWARVES:
            feet = classoutfits.frames("Gladiator", False, model)[0].regions
            self.assertLess(max(y for x, y in feet[classoutfits.RIGHT_FOOT]),
                            min(y for x, y in feet[classoutfits.LEFT_FOOT]))
            steps = classoutfits.frames("Gladiator", False, model)
            self.assertFalse(steps[11].regions[classoutfits.RIGHT_FOOT])
            self.assertTrue(steps[13].regions[classoutfits.RIGHT_FOOT])
            hit = classoutfits.frames("Fighter/Thief", True, model)[12]
            self.assertIn((3, 5), hit.head)
            self.assertNotIn((8, 5), hit.head)


class HumanClothContinuityTests(unittest.TestCase):
    def test_woman_second_profile_step_has_continuous_shoulder_cloth(self):
        for role in ("Priest", "Druid", "Thief", "Mage", "Psionicist"):
            pose = classoutfits.frames(role, False, 2099)[12]
            folds = {(x, y): rank for x, y, rank in pose.cloak}
            for x in (6, 7):
                self.assertEqual(folds[x, 8], folds[x, 9], role)
                self.assertNotIn(pose.image[6 + 8][6 + x], (None, 255), role)
