"""Visible fold and class color regressions in the actual equipped pictures."""
import os
from pathlib import Path
import unittest

from dsloader import art, classoutfits, spritegear, sprites


@unittest.skipUnless(os.environ.get("DSUN_OBJECTS"), "needs the player's SEGOBJEX.GFF and palette")
class ArmorDyeTests(unittest.TestCase):
    def setUp(self):
        self.addCleanup(spritegear.set_palette, list(spritegear._RGB))
        dresser = sprites.Dresser.for_game(None, str(Path(os.environ["DSUN_OBJECTS"]).parent))
        if dresser is None:
            self.skipTest("needs both the retail picture archive and the game palette")
        self.pictures = dresser.pics

    def test_woman_druid_exposed_green_bodice_can_take_chest_armor(self):
        armor = (88 | spritegear.MAGIC_ARMOUR,)
        empty = self.pictures.build(301, False, {}, (), role="Druid")
        worn = self.pictures.build(301, False, {}, armor, role="Druid")
        side, top = sprites.room(False)
        for pose in (0, 1, 11, 12, 13, 14):
            bare = art.decode_frame(empty, pose)[2]
            dressed = art.decode_frame(worn, pose)[2]
            changes = {(x-side, y-top) for y, row in enumerate(dressed)
                       for x, color in enumerate(row) if color != bare[y][x]}
            frame = classoutfits.frames("Druid", False, 2099)[pose]
            self.assertEqual(bool(changes), pose != 1)
            self.assertTrue(changes.issubset(frame.regions[classoutfits.CHEST]))
            self.assertTrue(changes.isdisjoint((x, y) for x, y, _ in frame.cloak))
            self.assertTrue(changes.isdisjoint(frame.armor_trim))

    def test_full_armor_leaves_original_class_color_on_visible_garments(self):
        cream = {61, 62, 63, 121, 123, 125, 126, 155, 199}
        teal = {40, 69, 70, 71, 72, 73}
        hide = {*range(88, 105), 168, 169, 199, 204, 205, 207}
        cases = ((300, "Priest", 0, cream), (301, "Priest", 1, cream),
                 (302, "Fighter/Psionicist", 1, teal), (303, "Fighter/Psionicist", 1, teal),
                 (304, "Fighter/Psionicist", 1, teal), (305, "Fighter/Psionicist", 1, teal),
                 (306, "Fighter", 0, hide), (307, "Fighter", 0, hide))
        sx, sy = sprites.room(False)
        for obj, role, pose, pigments in cases:
            layer = obj if obj in classoutfits.HALF_ELF_SOURCES else self.pictures.model(obj)
            frame = classoutfits.frames(role, False, layer)[pose]
            cloth = {point for region in (classoutfits.CHEST, classoutfits.ARMS, classoutfits.LEGS)
                     for point in frame.regions[region]}
            cloth.update((x, y) for x, y, _ in frame.cloak)
            base = art.decode_frame(self.pictures.build(obj, False, {}, (), role=role), pose)[2]
            for kit in ((6, 7, 8), (88, 25, 26)):
                with self.subTest(figure=obj, role=role, pose=pose, armor=kit):
                    worn = art.decode_frame(self.pictures.build(obj, False, {}, kit, role=role), pose)[2]
                    original_tones = {(x+sx, y+sy) for x, y in cloth if base[y+sy][x+sx] in pigments}
                    self.assertGreaterEqual(sum(base[y][x] == worn[y][x] for x, y in original_tones), 3)
                    # Metal also shows on the fitted cuff beyond the Priest's sleeve.
                    surface = cloth.union(frame.regions[classoutfits.FOREARM])
                    self.assertGreater(sum(base[y+sy][x+sx] != worn[y+sy][x+sx] for x, y in surface), 5)

    def test_enchanted_robes_keep_class_fabric_and_limit_the_cycling_thread(self):
        from dsloader import game

        cases = ((308, "Cleric", {61, 62, 63, 155, 199}),
                 (309, "Psionicist", {69, 70, 71, 72, 73}))
        for obj, role, pigments in cases:
            for combat, pose in ((False, 0), (False, 12), (True, 7)):
                empty = self.pictures.build(obj, combat, {}, (), role=role)
                base = art.decode_frame(empty, pose)[2]
                cloth = {(x, y) for y, row in enumerate(base) for x, c in enumerate(row) if c in pigments}
                self.assertTrue(cloth)
                for dye, glow in ((0, spritegear.FIRE_GLOW), (spritegear.VEILED_DYE, spritegear.BLUE_GLOW)):
                    kind = game.ROBE_TYPE | spritegear.MAGIC_ARMOUR | dye | (glow << spritegear.GLOW_SHIFT)
                    with self.subTest(obj=obj, pose=pose, dye=dye):
                        dressed = self.pictures.build(obj, combat, {}, (kind,), role=role)
                        worn = art.decode_frame(dressed, pose)[2]
                        retained = sum(worn[y][x] == base[y][x] for x, y in cloth)
                        self.assertGreaterEqual(retained, 0.75 * len(cloth))
                        glints = sum(c in spritegear.GLOWS[glow] and c != base[y][x]
                                     for y, row in enumerate(worn) for x, c in enumerate(row))
                        self.assertGreater(glints, 0)
                        self.assertLessEqual(glints, 12)

    def test_robe_lights_exposed_fabric_beneath_the_mul_fighters_cloak(self):
        from dsloader import game

        gear = {"cloak": (65, 5)}
        empty = self.pictures.build(312, False, gear, (), role="Fighter")
        worn = self.pictures.build(312, False, gear, (game.ROBE_TYPE | spritegear.MAGIC_ARMOUR,), role="Fighter")
        side, top = sprites.room(False)
        for pose in (0, 1, 2):
            cloak, robed = (art.decode_frame(chunk, pose)[2] for chunk in (empty, worn))
            cape = classoutfits.frames("Fighter", False, 2093)[pose].equipped_cape
            with self.subTest(pose=pose):
                self.assertTrue(cape)
                self.assertTrue(all(cloak[y+top][x+side] == robed[y+top][x+side] for x, y, _ in cape))
                self.assertTrue(any(c in spritegear.GLINT and c != cloak[y][x]
                                    for y, row in enumerate(robed) for x, c in enumerate(row)))

    def test_robe_stitch_survives_on_stock_muls_dark_cloth(self):
        from dsloader import game

        base = self.pictures.build(312, True, {}, ())
        worn = self.pictures.build(312, True, {}, (game.ROBE_TYPE | spritegear.MAGIC_ARMOUR,))
        # Only interior black fabric remains visible in the wind-up and two bow poses.
        for pose in (0, 9, 10):
            empty, dressed = (art.decode_frame(chunk, pose)[2] for chunk in (base, worn))
            changes = [(c, dressed[y][x]) for y, row in enumerate(empty) for x, c in enumerate(row)
                       if c != dressed[y][x]]
            with self.subTest(pose=pose):
                self.assertTrue(changes)
                self.assertTrue(all(c == 254 for c, _ in changes))
                self.assertTrue(any(mark in spritegear.GLINT for _, mark in changes))

    def test_full_plate_preserves_hanging_linen_and_reaches_exposed_limbs(self):
        from dsloader import game

        cases = ((301, "Priest", 3), (305, "Cleric/Psionicist", 0))
        side, top = sprites.room(False)
        for obj, role, pose in cases:
            model = self.pictures.model(obj)
            fit = classoutfits.frames(role, False, model)[pose]
            def picture(slots):
                chunk = self.pictures.build(obj, False, {}, slots, role=role)
                return art.decode_frame(chunk, pose)[2]
            base = picture(())
            for slots in ((88, 25, 26), (game.PLATE_CHEST_TYPE, game.PLATE_ARMS_TYPE, game.PLATE_LEGS_TYPE)):
                with self.subTest(obj=obj, slots=slots):
                    full, arms, greaves = (picture(parts) for parts in (slots, slots[1:2], slots[2:]))
                    self.assertNotEqual(full, base)
                    self.assertNotEqual(arms, base)
                    self.assertEqual(greaves == base, obj == 301)
                    self.assertTrue(all(full[y+top][x+side] == base[y+top][x+side]
                                        for x, y in fit.regions[classoutfits.LEGS]))

    def test_half_giant_psionicist_wrap_covers_the_thigh_beneath_chest_armor(self):
        side, top = sprites.room(False)
        for role in ("Psionicist", "Psionicist/Ranger"):
            base, chest = (art.decode_frame(self.pictures.build(309, False, {}, kit, role=role), 0)[2]
                           for kit in ((), (88,)))
            for x, y in ((7, 25), (18, 29), (19, 29)):
                with self.subTest(role=role, x=x, y=y):
                    self.assertNotIn(base[y+top][x+side], range(128, 154))
                    self.assertIsNotNone(base[y+top][x+side])
                    self.assertEqual(base[y+top][x+side], chest[y+top][x+side])

    def test_robe_dyes_red_leather_and_plate_leaves_the_ranger_feather(self):
        from dsloader import game

        sx, sy = sprites.room(False)
        cases = ((301, "Gladiator", (5, 17), game.ROBE_TYPE, 135, True),
                 (300, "Ranger", (14, 1), 88, 169, False))
        for obj, role, (x, y), kind, original, should_change in cases:
            with self.subTest(role=role):
                plain = self.pictures.build(obj, False, {}, (), role=role)
                worn = self.pictures.build(obj, False, {}, (kind,), role=role)
                self.assertEqual(art.decode_frame(plain, 0)[2][sy+y][sx+x], original)
                self.assertEqual(art.decode_frame(worn, 0)[2][sy+y][sx+x] != original, should_change)

    def test_fallen_stock_figures_keep_armor_over_the_exposed_torso(self):
        for obj in range(300, 314):
            empty = self.pictures.build(obj, True, {}, ())
            enchanted = self.pictures.build(obj, True, {}, (15 | spritegear.MAGIC_ARMOUR,))
            original, worn = (art.decode_frame(picture, 13)[2] for picture in (empty, enchanted))
            changed = [(x, y) for y, row in enumerate(original) for x, color in enumerate(row)
                       if color != worn[y][x]]
            with self.subTest(figure=obj):
                # The original human and half-elf women fall with the cape
                # over the torso. The thri-kreen cannot wear body armor.
                self.assertEqual(bool(changed), obj not in (301, 307, 313))
                self.assertTrue(all(original[y][x] is not None for x, y in changed))
                self.assertTrue(all(worn[y][x] is not None for x, y in changed))
                if changed:
                    self.assertTrue(any(worn[y][x] in spritegear.GLINT for x, y in changed))

    def test_leather_preserves_the_half_elf_jerkin_fold_edges(self):
        role, obj = "Fighter", 307
        frame = classoutfits.frames(role, False, obj)[0]
        sx, sy = sprites.room(False)
        cloth = {(x+sx, y+sy) for region in (classoutfits.ARMS, classoutfits.CHEST, classoutfits.LEGS)
                 for x, y in frame.regions[region]}
        base = art.decode_frame(self.pictures.build(obj, False, {}, (), role=role), 0)[2]
        leather = art.decode_frame(self.pictures.build(obj, False, {}, (6, 7, 8), role=role), 0)[2]
        palette = spritegear._RGB
        edges = [(x, y, nx, ny) for x, y in cloth for nx, ny in ((x+1, y), (x, y+1))
                 if (nx, ny) in cloth and palette[base[y][x]] != palette[base[ny][nx]]]
        self.assertGreater(len(edges), 100)
        kept = sum(palette[leather[y][x]] != palette[leather[ny][nx]] for x, y, nx, ny in edges)
        self.assertGreaterEqual(kept / len(edges), 0.9)
