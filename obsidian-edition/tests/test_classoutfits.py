import unittest

from dsloader import classoutfits, game, spritegear as sg


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

    def test_priest_neckline_clears_native_jaw_and_ponytail(self):
        runs = [(False, 0, 8, 6, 5), (False, 1, 10, 6, 4), (True, 2, 12, 9, 5)]
        for combat, f, left, y, length in runs:
            pose = classoutfits.frames("Priest", combat)[f]
            cells = {(x, y) for x in range(left, left + length)}
            # These cells retain whatever is in the player's original picture.
            self.assertTrue(all(pose.image[yy + 6][x + 6] is None for x, yy in cells))
            self.assertTrue(cells.isdisjoint((x, y) for x, y, _ in pose.cloak))
            for bit in (classoutfits.CHEST, classoutfits.ARMS, classoutfits.LEGS):
                self.assertTrue(cells.isdisjoint(pose.regions[bit]))
