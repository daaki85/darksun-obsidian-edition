import os
import unittest
from pathlib import Path
from zipfile import ZipFile

from dsloader import art, classoutfits, game, gff, spritegear as sg, sprites


class WornMaterialTests(unittest.TestCase):
    def test_breastplate_highlight_moves_with_a_translated_torso(self):
        shades = tuple(range(16, 26))
        cells = [(x, y) for y in range(6) for x in range(7)]
        rows = [[64] * 17 for _ in range(12)]

        def sample(dx, dy):
            canvas = [row[:] for row in rows]
            sg.paint_breastplate(canvas, [(x + dx, y + dy) for x, y in cells], shades, 1, rows)
            return [canvas[y + dy + 1][x + dx + 1] for x, y in cells]

        first = sample(0, 0)
        self.assertGreater(first[2 * 7 + 2], first[-1])
        self.assertEqual(first, sample(3, 2))

    @unittest.skipUnless(os.environ.get("DSUN_OBJECTS"), "needs the player's SEGOBJEX.GFF")
    def test_elf_woman_profile_plate_keeps_near_arm_and_belt_visible(self):
        pictures = sprites.Pictures(gff.read_gff(Path(os.environ["DSUN_OBJECTS"]).read_bytes()))
        side, top = sprites.room(False)
        plain = pictures.build(305, False, {}, (), role="Fighter")
        # Trace one upper-arm pixel in each native profile drawing.
        arm = {2: (4, 8), 11: (6, 9), 12: (9, 8), 13: (4, 9), 14: (8, 9)}
        for kind in (88, 88 | sg.MAGIC_ARMOUR):
            plate = pictures.build(305, False, {}, (kind,), role="Fighter")
            for pose, (ax, ay) in arm.items():
                with self.subTest(kind=kind, pose=pose):
                    bare = art.decode_frame(plain, pose)[2]
                    worn = art.decode_frame(plate, pose)[2]
                    changed = {(x - side, y - top) for y, row in enumerate(worn)
                               for x, c in enumerate(row) if c != bare[y][x]}
                    self.assertTrue(changed)
                    self.assertTrue(all(6 <= y < 13 for x, y in changed))
                    self.assertNotIn((ax, ay), changed)
                    self.assertIn(bare[ay + top][ax + side], range(128, 154))

    def test_thief_profile_keeps_a_visible_cloak_below_the_waist(self):
        for model, waists in ((2095, (16, 15, 16, 15, 16)), (2099, (15, 14, 15, 15, 15)),
                              (2053, (12, 12, 11, 12, 12)), (2055, (12, 12, 11, 12, 12)),
                              (2059, (14, 14, 14, 15, 14)), (2061, (15, 14, 15, 15, 15))):
            walk = classoutfits.frames("Thief", False, model)
            for pose, waist in zip((2, 11, 12, 13, 14), waists):
                with self.subTest(model=model, pose=pose):
                    hem = [(x, y) for x, y, _ in walk[pose].cloak if y >= waist]
                    # The male elf lifts his trailing corner above the bent knee in step two.
                    if model == 2061 and pose == 12:
                        self.assertEqual(len(hem), 15)
                        self.assertEqual(max(y for x, y in hem), waist + 2)
                    else:
                        self.assertGreaterEqual(len(hem), 20)
                        self.assertGreaterEqual(max(y for x, y in hem), waist + 3)

    def test_profile_hems_leave_exposed_feet_and_ground_clear(self):
        for obj, model in classoutfits.MODELS.items():
            roles = (classoutfits.CLASSES[1:] if obj < 302 else classoutfits.DWARF_ROLES.values()
                     if obj < 304 else classoutfits.ELF_ROLES.values())
            for role in roles:
                walk = classoutfits.frames(role, False, model)
                for f in (2, 11, 12, 13, 14):
                    with self.subTest(model=model, role=role, pose=f):
                        frame = walk[f]
                        cloth = {(x, y) for x, y, _ in frame.cloak}
                        for foot in (classoutfits.LEFT_FOOT, classoutfits.RIGHT_FOOT):
                            self.assertTrue(cloth.isdisjoint(frame.regions[foot]))
                        if model == 2059 and f == 14:
                            self.assertNotIn((7, 16), cloth)
                            if role in ("Preserver", "Thief", "Ranger"):
                                self.assertIsNone(frame.image[16 + 4][7 + 4])
                        if model == 2095 and f == 12:
                            strip = {(6, 18), (7, 18), (5, 19), (6, 19), (7, 19), (4, 20), (5, 20), (3, 21)}
                            self.assertTrue(cloth.isdisjoint(strip))
                            if role in ("Mage", "Thief", "Ranger"):
                                self.assertTrue(all(frame.image[y + 6][x + 6] is None for x, y in strip))

    def test_actual_robe_items_select_distinct_visuals(self):
        from dsloader import robes

        class Wearing:
            def __init__(self, name):
                self.record = bytearray(robes.item(name))
                self.record[game.ITEM_SLOT] = robes.CHEST_SLOT

            def _worn(self, member):
                return [(0, self.record, bytes(game.ITEM_TYPE_SIZE))]

        for name, dye in ((robes.ASHEN, 0), (robes.VEILED, sg.VEILED_DYE)):
            _, (piece,) = sprites.worn(Wearing(name), 0)
            self.assertEqual(piece & (sg.MAGIC_ARMOUR - 1), game.ROBE_TYPE)
            self.assertEqual(piece & sg.VEILED_DYE, dye)
            self.assertTrue(piece & sg.MAGIC_ARMOUR)

    @unittest.skipUnless(os.environ.get("DSUN_OBJECTS"), "needs the player's SEGOBJEX.GFF")
    def test_glove_tracks_striking_hand_and_robe_keeps_the_mantle(self):
        pictures = sprites.Pictures(gff.read_gff(Path(os.environ["DSUN_OBJECTS"]).read_bytes()))
        for obj, model in classoutfits.MODELS.items():
            role = "Mage" if obj < 302 else "Thief" if obj < 304 else "Preserver"
            pose = classoutfits.frames(role, True, model)[1]
            side, top = sprites.room(True)

            def render(items, armour):
                return art.decode_frame(pictures.build(obj, True, items, armour, role=role), 1)[2]

            plain = render({}, ())
            glove = render({"right": (113, 5, sg.MAGIC, sg.BLUE_GLOW)}, ())
            changes = {(x - side, y - top) for y, row in enumerate(glove)
                       for x, color in enumerate(row) if color != plain[y][x]}
            with self.subTest(model=model):
                self.assertTrue(changes)
                self.assertTrue(changes.issubset(pose.regions[classoutfits.FOREARM]))
                robed = render({}, (game.ROBE_TYPE | sg.MAGIC_ARMOUR | sg.VEILED_DYE,))
                self.assertTrue(all(robed[y+top][x+side] == plain[y+top][x+side]
                                    for x, y, _ in pose.cloak))
                self.assertEqual(render({}, ()), plain)


class PsionicistColorTests(unittest.TestCase):
    def test_psionicist_tunics_and_multiclass_hoods_use_teal_in_every_pose(self):
        green = {53, 188, 225, 226}
        teal = {69, 70, 71, 72, 73}
        outfits = (("Psionicist", (2095, 2099, *classoutfits.DWARVES)),
                 ("Psionicist/Thief", classoutfits.DWARVES + classoutfits.ELVES))
        for role, models in outfits:
            for model in models:
                for combat in (False, True):
                    for pose, frame in enumerate(classoutfits.frames(role, combat, model)):
                        colors = {color for row in frame.image for color in row}
                        with self.subTest(role=role, model=model, combat=combat, pose=pose):
                            self.assertTrue(colors & teal)
                            self.assertTrue(colors.isdisjoint(green))


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

    @unittest.skipUnless(os.environ.get("DSUN_OBJECTS"), "needs the player's SEGOBJEX.GFF")
    def test_male_psionicist_collar_follows_the_native_shoulders(self):
        pictures = sprites.Pictures(gff.read_gff(Path(os.environ["DSUN_OBJECTS"]).read_bytes()))
        for combat in (False, True):
            side, top = sprites.room(combat)
            dressed = pictures.build(300, combat, {}, (), role="Psionicist")
            for f, source in enumerate(pictures.own(2095 + combat)):
                pose = f + 15 * combat
                if pose == 28:  # The fallen figure has no upright waist line.
                    continue
                waist = classoutfits.LANDMARKS[pose][-1]
                upper = art.decode_frame(dressed, f)[2][top:top + waist]
                with self.subTest(pose=pose):
                    self.assertTrue(any(c in range(69, 74) for row in upper for c in row))
                    for y, row in enumerate(upper):
                        body = {side + x for x, c in enumerate(source[y]) if c is not None}
                        self.assertLessEqual({x for x, c in enumerate(row) if c is not None}, body)

    def test_psionicist_wrap_reaches_the_belt_in_the_turning_poses(self):
        # Follow the two central ribs in each pose, down the formerly bare midriff.
        for pose, x, y in ((1, 10, 11), (2, 3, 12), (5, 8, 10),
                           (7, 6, 11), (18, 5, 15), (19, 7, 18)):
            combat, index = divmod(pose, 15)
            frame = classoutfits.frames("Psionicist", combat, 2095)[index]
            with self.subTest(pose=pose):
                for row in frame.image[y + 6:y + 9]:
                    self.assertTrue(all(c in range(69, 74) for c in row[x + 6:x + 8]))

    def test_male_priest_side_walk_keeps_cloth_behind_the_arm(self):
        # At full stride the ground used to show through these folds.
        cream_fold = {208, 204, 207, 205, 194, 206, 120, 121, 61, 123, 199, 125, 62, 155, 63,
                      92, 95, 97, 118, 119, 122, 124, 214, 215, 126}
        poses = classoutfits.frames("Priest", False, 2095)
        for f, cells in ((12, ((4, 10), (4, 11), (3, 12), (4, 12), (3, 13), (3, 14), (4, 14))),
                         (13, ((1, 12), (1, 13), (1, 14)))):
            pose = poses[f]
            left = 8 if f == 13 else 6
            for x, y in cells:
                with self.subTest(frame=f, x=x, y=y):
                    self.assertIn(pose.image[y + 6][x + left], cream_fold)

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

    def test_woman_thief_hood_has_a_crown_and_leaves_free_hair_below_it(self):
        # Crown above the stock hairline; a visible lock below the turned rim.
        cases = ((False, 0, (8, -1), (1, 8)),
                 (False, 2, (5, -1), (0, 8)), (True, 1, (10, -1), (8, 9)))
        for combat, index, crown, lock in cases:
            with self.subTest(combat=combat, frame=index):
                hood = classoutfits.frames("Thief", combat, 2099)[index]
                bare_head = classoutfits.frames("Gladiator", combat, 2099)[index]
                dye = {(x, y) for x, y, _ in hood.cloak}
                self.assertIn(crown, dye)
                self.assertNotIn(crown, hood.head)
                self.assertIn(lock, hood.head)
                self.assertNotIn(lock, dye)
                x, y = lock
                self.assertEqual(hood.image[y + 6][x + 6], bare_head.image[y + 6][x + 6])

    def test_thief_rear_panel_and_moving_crown_take_cloak_dye(self):
        # Previously these pixels exposed a dark wedge on the back or hair above the brim.
        for pose, point in ((1, (9, 12)), (7, (8, 12)), (8, (10, 12)), (9, (10, 11)),
                            (10, (9, 11)), (18, (5, 14)), (19, (5, 20)), (20, (20, 5)),
                            (16, (17, 2)), (27, (5, 0))):
            combat, frame = divmod(pose, 15)
            hood = classoutfits.frames("Thief", combat, 2099)[frame]
            self.assertIn(point, {(x, y) for x, y, _ in hood.cloak}, pose)

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

    def test_short_recoil_hems_leave_ground_visible_beside_the_raised_leg(self):
        for model in classoutfits.DWARVES:
            for role in ("Gladiator", "Psionicist"):
                with self.subTest(model=model, role=role):
                    recoil = classoutfits.frames(role, True, model)[12]
                    for y in (12, 13, 14):
                        self.assertIsNone(recoil.image[y + 4][12 + 4])
                        self.assertNotIn((12, y), recoil.regions[classoutfits.LEGS])

    def test_fighter_details_remain_visible_at_map_size(self):
        for model in classoutfits.DWARVES:
            for role in ("Fighter", "Fighter/Thief", "Fighter/Psionicist", "Fighter/Psionicist/Thief"):
                idle = classoutfits.frames(role, False, model)[0]
                # The near-black square occupied the four rows at the right belt end.
                hip = [idle.image[y + 4][x + 4] for y in range(12, 16) for x in range(11, 16)]
                self.assertNotIn(208, hip, (model, role))
            fighter = classoutfits.frames("Fighter", False, model)
            for f in (2, 11, 12, 13, 14):
                pose = fighter[f]
                panels = [pose.image[y + 4][x + 4] for x, y in pose.regions[classoutfits.CHEST]]
                self.assertTrue({168, 199}.intersection(panels), (model, f))
            for role in ("Cleric/Fighter", "Cleric/Fighter/Psionicist"):
                pose = classoutfits.frames(role, False, model)[0]
                caps = [pose.image[y + 4][x + 4] for x, y in pose.regions[classoutfits.ARMS]]
                self.assertIn(199, caps)
                self.assertNotIn(92, caps)
            for f in (0, 1):
                pose = classoutfits.frames("Fighter/Psionicist", False, model)[f]
                # The diagonal is two pixels wide on the lower rib cage.
                for y in (9, 11):
                    self.assertEqual(sum(c in (70, 71, 73) for c in pose.image[4 + y]), 2,
                                     (model, f, y))

    # The open hood can be slate, stitched leather or teal. Include the
    # intermediate VGA threads as well as the old crown and rim colors.
    slate = {208, 17, 18, 19, 20, 21, 22, 49, 23, 24, 25, 50, 26, 27, 28, 29}
    leather = {208, 88, 204, 89, 90, 207, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100}
    teal = {208, 17, 69, 188, 53, 70, 225, 71, 40, 72, 73, 209, 18, 48, 210, 49,
            211, 160, 212, 226, 213, 215}
    hood_fabrics = {"Thief": slate, "Fighter/Thief": leather, "Psionicist/Thief": teal,
                    "Fighter/Psionicist/Thief": leather | {71, 73}}

    def test_thief_crown_stays_visible_in_every_pose(self):
        for model in classoutfits.DWARVES:
            for role in classoutfits.DWARF_ROLES.values():
                if "Thief" not in role:
                    continue
                for combat in (False, True):
                    for f, pose in enumerate(classoutfits.frames(role, combat, model)):
                        fallen = combat and f == 13
                        crown = (max if fallen else min)(y for x, y in pose.head)
                        tips = [x for x, y in pose.head if y == crown]
                        center = (min(tips) + max(tips)) // 2
                        brow = crown - 1 if fallen else crown + 1
                        with self.subTest(model=model, role=role, combat=combat, frame=f):
                            fabric = [pose.image[y + 4][x + 4] for y in (crown, brow)
                                      for x in range(center - 4, center + 5)]
                            self.assertGreaterEqual(sum(c in self.hood_fabrics[role] for c in fabric), 8)

    @unittest.skipUnless(os.environ.get("DSUN_OBJECTS"), "needs the player's SEGOBJEX.GFF")
    def test_profile_hood_reaches_the_shoulder(self):
        pictures = sprites.Pictures(gff.read_gff(Path(os.environ["DSUN_OBJECTS"]).read_bytes()))
        # Frame, visible side of the head (inclusive x bounds), crown and collar rows.
        profiles = ((2, 0, 7, 1, 7), (11, 0, 6, 1, 7), (12, 3, 11, 1, 6),
                    (13, 0, 7, 1, 7), (14, 2, 10, 1, 6), (21, 9, 14, 1, 6),
                    (22, 5, 13, 1, 6), (23, 4, 12, 1, 6), (24, 0, 7, 1, 6),
                    (25, 0, 4, 4, 9), (26, 8, 14, 4, 9))
        for model in classoutfits.DWARVES:
            for role, fabric in self.hood_fabrics.items():
                for k, left, right, top, collar in profiles:
                    combat, f = divmod(k, 15)
                    pose = classoutfits.frames(role, combat, model)[f]
                    native = pictures.own(model + combat)[f]
                    image = pose.canvas(native, 4)
                    cloth = {(x, y) for y in range(top, collar + 1)
                             for x in range(left, right + 1) if image[y + 4][x + 4] in fabric}
                    # In the turned wind-up the bone plate overlaps the fold.
                    if k == 21:
                        cloth.update((x, y) for x, y in pose.regions[classoutfits.ARMS]
                                     if left <= x <= right and top < y <= collar)
                    path = {(x, top) for x in range(left, right + 1)} & cloth
                    pending = list(path)
                    while pending:
                        x, y = pending.pop()
                        for point in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                            if point in cloth and point not in path:
                                path.add(point)
                                pending.append(point)
                    self.assertTrue(any(y == collar for x, y in path), (model, role, k))

    def test_front_hoods_leave_the_jaw_open(self):
        for model in classoutfits.DWARVES:
            for role in classoutfits.DWARF_ROLES.values():
                if "Thief" not in role:
                    continue
                for f, cx in ((0, 10), (3, 9), (4, 9), (5, 9), (6, 10)):
                    pose = classoutfits.frames(role, False, model)[f]
                    with self.subTest(model=model, role=role, frame=f):
                        # These five points across the jaw keep the native skin pixels.
                        self.assertTrue(all(pose.image[4 + 5][4 + x] is None
                                            for x in range(cx - 2, cx + 3)))
                        if role == "Fighter/Psionicist/Thief":
                            self.assertEqual(pose.image[4][4 + cx - 1], 73)

    def test_cleric_front_fold_tracks_the_rib_cage_in_profile(self):
        # The visible fold changes sides relative to the crossing wrist.
        # Include the two oblique bow poses along with the nine side views.
        samples = ((False, 2, 7, 7), (False, 11, 6, 7), (False, 12, 10, 7),
                   (False, 13, 7, 7), (False, 14, 9, 7), (True, 6, 10, 7),
                   (True, 7, 12, 7), (True, 8, 11, 7), (True, 9, 7, 7),
                   (True, 10, 6, 11), (True, 11, 9, 10))
        for model in classoutfits.DWARVES:
            for role in classoutfits.DWARF_ROLES.values():
                if "Cleric" not in role:
                    continue
                for combat, f, x, y in samples:
                    pose = classoutfits.frames(role, combat, model)[f]
                    with self.subTest(model=model, role=role, combat=combat, frame=f):
                        self.assertIn((x, y), pose.regions[classoutfits.CHEST])
                        self.assertNotIn((x, y), pose.head)
                        if role == "Cleric":
                            self.assertIn(pose.image[y + 4][x + 4],
                                          (61, 62, 63, 120, 121, 122, 123, 124, 125, 126, 155, 199, 214, 215))

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


class ElfOutfitTests(unittest.TestCase):
    def test_rear_psionicist_tunic_breaks_up_flat_cloth(self):
        for model in classoutfits.ELVES:
            poses = classoutfits.frames("Psionicist", False, model)
            for f in (1, 8, 9):
                cloth = poses[f]
                torso = set(cloth.regions[classoutfits.CHEST]) - set(cloth.regions[classoutfits.FOREARM])
                squares = []
                for x, y in torso:
                    points = ((x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1))
                    if torso.issuperset(points):
                        squares.append({cloth.image[py + 4][px + 4] for px, py in points})
                with self.subTest(model=model, frame=f):
                    self.assertGreaterEqual(len(squares), 8)
                    self.assertLess(sum(len(colors) == 1 for colors in squares), len(squares) / 8)

    def test_elf_roster_reads_all_three_slots_in_any_order(self):
        from itertools import permutations
        from dsloader import kitpages

        sheet = bytearray(game.SHEET_SIZE)
        sheet[game.SHEET_RACE] = game.ELF
        raw = {group: slot for slot, group in kitpages.CREATION_CLASS.items()}
        counts = [sum(len(c) == n for c in classoutfits.ELF_ROLES) for n in (1, 2, 3)]
        self.assertEqual(counts, [7, 14, 16])
        slots = slice(game.SHEET_CLASSES, game.SHEET_CLASSES + 3)
        for combo, role in classoutfits.ELF_ROLES.items():
            for order in permutations(combo):
                sheet[slots] = bytes(raw[c] for c in order).ljust(3, b"\0")
                for model in classoutfits.ELVES:
                    self.assertEqual(classoutfits.for_sheet(sheet, model), role)
                self.assertIsNone(classoutfits.for_sheet(sheet, 2099))
        for illegal in ((9, 13, 0), (10, 17, 0), (5, 0, 0), (9, 9, 0), (0, 0, 0)):
            sheet[slots] = bytes(illegal)
            self.assertIsNone(classoutfits.for_sheet(sheet, 2059))

    def test_cleaned_faces_and_necklines_keep_the_original_mouth(self):
        # Native coordinates inspected against the retail sprites. In the second
        # forward strike the woman's head drops much farther than the man's.
        mouths = {2059: [(0, 7, 8), (3, 6, 9), (15, 10, 14), (16, 10, 10),
                         (17, 15, 8), (21, 12, 13), (22, 13, 5), (26, 8, 8)],
                  2061: [(0, 7, 6), (3, 6, 6), (15, 10, 15), (16, 10, 7),
                         (17, 13, 8), (21, 16, 12), (22, 13, 6), (27, 7, 6)]}
        for model, markers in mouths.items():
            for role in classoutfits.ELF_ROLES.values():
                for pose, x, y in markers:
                    cb, f = divmod(pose, 15)
                    frame = classoutfits.frames(role, cb, model)[f]
                    with self.subTest(model=model, role=role, pose=pose):
                        self.assertIsNone(frame.image[y + 4][x + 4])
                        self.assertIn((x, y), frame.head)
                        self.assertNotIn((x, y), {(a, b) for a, b, _ in frame.cloak})
                        for cells in frame.regions.values():
                            self.assertNotIn((x, y), cells)

    def test_mantle_closes_under_bow_arm_and_recoil_preserves_fingers(self):
        for role in classoutfits.ELF_ROLES.values():
            for model in classoutfits.ELVES:
                with self.subTest(role=role, model=model):
                    poses = classoutfits.frames(role, True, model)
                    if model == 2059:
                        self.assertIn((4, 19), poses[12].regions[classoutfits.FOREARM])
                        self.assertIsNone(poses[12].image[19 + 4][4 + 4])
                    if {"Preserver", "Ranger", "Thief"}.intersection(role.split("/")):
                        bow = poses[11]
                        folds = {(x, y) for x, y, _ in bow.cloak}
                        for y in (13, 14):
                            self.assertIn((11, y), folds)
                            self.assertNotIn((11, y), bow.regions[classoutfits.CHEST])
                            self.assertIsNotNone(bow.image[y + 4][11 + 4])

    def test_profile_capes_continue_behind_the_swinging_elbow(self):
        # Both intermediate steps used to expose the ground at these seams.
        for role in classoutfits.ELF_ROLES.values():
            if not {"Preserver", "Ranger", "Thief"}.intersection(role.split("/")):
                continue
            for model, index, x in ((2061, 12, 0), (2061, 13, -1), (2059, 13, -1)):
                with self.subTest(model=model, role=role, step=index):
                    frame = classoutfits.frames(role, False, model)[index]
                    self.assertIn((x, 14), {(a, b) for a, b, _ in frame.cloak})
                    self.assertIsNotNone(frame.image[14 + 4][x + 4])
                    self.assertNotIn((x, 14), frame.regions[classoutfits.CHEST])

    def test_profile_cloak_lifts_clear_of_the_elfs_bent_leg(self):
        for role in classoutfits.ELF_ROLES.values():
            walk = classoutfits.frames(role, False, 2061)
            for f, y, tip in ((12, 17, {-6, -5, -4}), (13, 18, {-6, -5, -4, -3})):
                with self.subTest(role=role, pose=f):
                    folds = {(x, row) for x, row, _ in walk[f].cloak}
                    self.assertEqual({x for x, row in folds if row == y}, tip)
                    self.assertTrue(all(row <= y for x, row in folds))

    def test_hood_covers_the_moving_crown_and_releases_the_fallen_lock(self):
        for role in classoutfits.ELF_ROLES.values():
            if "Thief" not in role.split("/"):
                continue
            for model, x, y in ((2059, 8, 0), (2061, 10, 3)):
                with self.subTest(model=model, role=role):
                    rear = classoutfits.frames(role, False, model)[1]
                    self.assertIn((x, y), {(a, b) for a, b, _ in rear.cloak})
                    self.assertIsNotNone(rear.image[y + 4][x + 4])
            for index, point in ((5, (11, 4)), (5, (11, 5)), (8, (0, 8)), (12, (11, 1)),
                                 (13, (6, 1)), (13, (7, 1)), (13, (8, 1)), (13, (4, 2))):
                frame = classoutfits.frames(role, False, 2059)[index]
                self.assertIn(point, {(a, b) for a, b, _ in frame.cloak})
            for index, crown in ((1, ((7, 0), (5, 2), (7, 2), (7, 6))),
                                 (12, ((6, 0), (2, 3), (1, 6), (2, 8)))):
                with self.subTest(role=role, frame=index):
                    frame = classoutfits.frames(role, True, 2059)[index]
                    dye = {(x, y) for x, y, _ in frame.cloak}
                    self.assertTrue(set(crown) <= dye)
                    self.assertTrue(all(frame.image[y + 4][x + 4] is not None for x, y in crown))
            fallen = classoutfits.frames(role, True, 2059)[13]
            self.assertNotIn((2, 15), {(a, b) for a, b, _ in fallen.cloak})
            self.assertIsNone(fallen.image[15 + 4][2 + 4])

    def test_moving_mantle_keeps_underfold_and_fighter_fastening(self):
        for role in classoutfits.ELF_ROLES.values():
            if "Preserver" in role.split("/"):
                walk = classoutfits.frames(role, False, 2061)[5]
                folds = {(x, y) for x, y, _ in walk.cloak}
                self.assertTrue({(11, y) for y in range(13, 19)} <= folds, role)
        for model in classoutfits.ELVES:
            single = classoutfits.frames("Preserver", True, model)
            pair = classoutfits.frames("Fighter/Preserver", True, model)
            for index in (3, 4, 5):
                with self.subTest(model=model, strike=index - 2):
                    self.assertTrue(any(pair[index].image[y + 4][x + 4] != single[index].image[y + 4][x + 4]
                                        for x, y, _ in pair[index].cloak))

    @unittest.skipUnless(os.environ.get("DSUN_OBJECTS"), "needs the player's SEGOBJEX.GFF")
    def test_elf_weapons_fit_the_picture_on_all_four_edges(self):
        from unittest.mock import patch

        pictures = sprites.Pictures(gff.read_gff(Path(os.environ["DSUN_OBJECTS"]).read_bytes()))
        canvas = classoutfits.Frame.canvas

        def with_floor(frame, rows, pad):
            result = canvas(frame, rows, pad)
            return result + [[None] * len(result[0]) for _ in range(20)]

        # A larger normal pad alone cannot reveal a tip cut off below the feet.
        weapons = {shape: item for item, shape in sg.WEAPON_SHAPES.items()
                   if shape not in (sg.BOW, sg.SLING, sg.CHATKCHA)}
        with patch.object(classoutfits.Frame, "canvas", with_floor):
            for model in classoutfits.ELVES:
                for combat in (False, True):
                    side, top = sprites.room(combat)
                    poses = classoutfits.frames("Fighter/Preserver/Thief", combat, model)
                    for index, frame in enumerate(poses):
                        rows = pictures.own(model + combat)[index]
                        left, right = 32 - side, 32 + len(rows[0]) + side
                        ceiling, floor = 32 - top, 32 + len(rows)
                        for hand in ("right", "left"):
                            for shape, item in weapons.items():
                                with self.subTest(model=model, combat=combat, frame=index,
                                                  hand=hand, shape=shape):
                                    out = sg.armed(rows, model, index, combat, {hand: (item, 4)},
                                                   pad=32, costume=frame)
                                    for y, row in enumerate(out):
                                        outside = row if y < ceiling or y >= floor else row[:left] + row[right:]
                                        self.assertTrue(all(c is None for c in outside))

    @unittest.skipUnless(os.environ.get("DSUN_OBJECTS"), "needs the player's SEGOBJEX.GFF")
    def test_final_bow_helm_sits_on_the_elf_crown(self):
        chunks = gff.read_gff(Path(os.environ["DSUN_OBJECTS"]).read_bytes())
        pictures = sprites.Pictures(chunks)
        helm = {"helm": (game.BONE_HELM_TYPE, 1)}
        for obj, crown in ((304, 4), (305, 3)):
            self.assertTrue(pictures.supports_outfits(obj, pictures.model(obj)))
            regular, wearing = [art.decode_frame(pictures.build(obj, True, gear, (), role="Thief"), 11)[2]
                                for gear in ({}, helm)]
            side, top = sprites.room(True)
            # The bow tip at y=0 previously put a helmet spike in the air at x=12.
            self.assertEqual(wearing[:top + crown - 1], regular[:top + crown - 1])
            changed = {(x-side, y-top) for y, row in enumerate(wearing) for x, c in enumerate(row)
                       if c != regular[y][x]}
            self.assertTrue(changed)
            self.assertTrue(all(3 <= x <= 11 and crown-1 <= y <= crown+2 for x, y in changed))
