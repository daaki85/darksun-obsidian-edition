"""Ownership and fold detail of boots and cloaks in the encoded map pictures."""
import os
from pathlib import Path
import unittest

from dsloader import art, classoutfits, game, spritegear as sg, sprites


@unittest.skipUnless(os.environ.get("DSUN_OBJECTS"), "needs retail objects and palette")
class MagicClothTests(unittest.TestCase):
    def setUp(self):
        self.addCleanup(sg.set_palette, list(sg._RGB))
        dresser = sprites.Dresser.for_game(None, str(Path(os.environ["DSUN_OBJECTS"]).parent))
        if dresser is None:
            self.skipTest("needs both retail archives")
        self.pictures = dresser.pics

    def picture(self, obj, combat, slot, kind, glow=None, role=None):
        item = (kind, 5) if glow is None else (kind, 5, sg.MAGIC, glow)
        gear = {slot: item} if slot else {}
        return self.pictures.build(obj, combat, gear, (), role=role)

    def test_each_visible_fitted_foot_shines_within_its_boot(self):
        for obj, role in ((300, "Mage"), (301, "Thief"), (304, "Cleric/Fighter"), (307, "Fighter")):
            model = obj if obj in classoutfits.HALF_ELF_SOURCES else self.pictures.model(obj)
            for combat in (False, True):
                sx, sy = sprites.room(combat)
                ordinary = self.picture(obj, combat, "boots", game.SPEED_BOOTS_TYPE, role=role)
                enchanted = self.picture(obj, combat, "boots", game.SPEED_BOOTS_TYPE, sg.FIRE_GLOW, role)
                for i, cloth in enumerate(classoutfits.frames(role, combat, model)):
                    plain, worn = (art.decode_frame(p, i)[2] for p in (ordinary, enchanted))
                    sparks = {(x-sx, y-sy) for y, row in enumerate(worn)
                              for x, shade in enumerate(row) if shade != plain[y][x]}
                    visible = set()
                    for side in (classoutfits.LEFT_FOOT, classoutfits.RIGHT_FOOT):
                        foot = {(x, y) for x, y in cloth.regions[side]
                                if plain[y+sy][x+sx] not in (None, 254)}
                        if foot:
                            self.assertTrue(foot & sparks, (obj, role, i, side))
                            visible.update(foot)
                    self.assertLessEqual(sparks, visible)

    def test_male_psionicist_dons_a_full_cape_without_dyeing_the_teal_wrap(self):
        teal = {40, 69, 70, 71, 72, 73}
        for combat in (False, True):
            sx, sy = sprites.room(combat)
            empty = self.picture(300, combat, None, 0, role="Psionicist")
            magic = self.picture(300, combat, "cloak", game.ELVEN_CLOAK_TYPE, sg.GREEN_GLOW, "Psionicist")
            for f, frame in enumerate(classoutfits.frames("Psionicist", combat)):
                pose = f + 15 * combat
                body, worn = (art.decode_frame(p, f)[2] for p in (empty, magic))
                cape = {(x+sx, y+sy) for x, y, color in frame.equipped_cape}
                touched = {(x, y) for y, row in enumerate(worn) for x, shade in enumerate(row)
                           if shade != body[y][x]}
                protected = {(x+sx, y+sy) for slot in (classoutfits.FOREARM, classoutfits.BOW,
                             classoutfits.LEFT_FOOT, classoutfits.RIGHT_FOOT) for x, y in frame.regions[slot]}
                self.assertTrue(touched <= cape and touched.isdisjoint(protected), pose)
                self.assertTrue(any(worn[y][x] in sg.GLOWS[sg.GREEN_GLOW] for x, y in cape), pose)
                self.assertTrue(any(body[y][x] is None for x, y in cape), pose)
                native_teal = sum(c in teal and c == worn[y][x] for y, row in enumerate(body)
                                  for x, c in enumerate(row))
                self.assertGreaterEqual(native_teal, 8, pose)
                self.assertTrue(all(any((x+dx, y+dy) in cape for dx in (-1, 0, 1) for dy in (-1, 0, 1)
                                        if dx or dy) for x, y in cape), pose)
                if pose in (1, 7, 8, 9, 10, 18, 19, 20):
                    self.assertGreater(len(cape), 120, pose)
                    self.assertGreaterEqual(max(y for x, y in cape) - min(y for x, y in cape), 10, pose)
            self.assertEqual(empty, self.picture(300, combat, None, 0, role="Psionicist"))

    def test_rear_thief_cloak_keeps_colored_folds_and_sparse_surface_shine(self):
        obj, role, i = 301, "Thief", 8
        cloth = classoutfits.frames(role, False, self.pictures.model(obj))[i]
        sx, sy = sprites.room(False)
        bare, ordinary, magic = (art.decode_frame(p, i)[2] for p in (
            self.picture(obj, False, None, 0, role=role),
            self.picture(obj, False, "cloak", game.ELVEN_CLOAK_TYPE, role=role),
            self.picture(obj, False, "cloak", game.ELVEN_CLOAK_TYPE, sg.GREEN_GLOW, role)))
        mantle = {(x+sx, y+sy) for x, y, rank in cloth.cloak}
        unlike = [(x, y, xx, yy) for x, y in mantle for xx, yy in ((x+1, y), (x, y+1))
                  if (xx, yy) in mantle and bare[y][x] != bare[yy][xx]]
        self.assertGreater(len(unlike), 300)
        self.assertGreater(sum(ordinary[y][x] != ordinary[yy][xx] for x, y, xx, yy in unlike),
                           0.90 * len(unlike))
        sparks = {(x, y) for y, row in enumerate(magic) for x, shade in enumerate(row)
                  if shade != ordinary[y][x]}
        self.assertTrue(sparks <= mantle)
        self.assertGreater(len(sparks), 0)
        self.assertLess(len(sparks), len(mantle) // 5)

    def test_stock_cloak_catches_the_shoulders_and_stays_behind_the_bow(self):
        sx, sy = sprites.room(False)
        for obj in (308, 309, 310, 311, 312):
            base = self.picture(obj, False, None, 0)
            magic = self.picture(obj, False, "cloak", game.ELVEN_CLOAK_TYPE, sg.GREEN_GLOW)
            for i in (3, 4, 5, 6):
                original, worn = (art.decode_frame(p, i)[2] for p in (base, magic))
                sparks = {(x-sx, y-sy) for y, row in enumerate(worn) for x, shade in enumerate(row)
                          if shade in sg.GLOWS[sg.GREEN_GLOW] and shade != original[y][x]}
                self.assertTrue(sparks, (obj, i))
        for obj, bow_pixels in ((305, ((5, 7), (7, 5), (6, 6))),
                                (310, ((2, 8), (3, 9))),
                                (311, ((4, 9), (5, 5)))):
            sx, sy = sprites.room(True)
            plain, magic = (art.decode_frame(p, 10)[2] for p in (
                self.picture(obj, True, None, 0),
                self.picture(obj, True, "cloak", game.ELVEN_CLOAK_TYPE, sg.GREEN_GLOW)))
            for x, y in bow_pixels:
                self.assertIn(plain[y+sy][x+sx], {179, 180, 181, 182, 183})
                self.assertEqual(plain[y+sy][x+sx], magic[y+sy][x+sx], (obj, x, y))

    def test_original_cloak_and_both_boot_toes_remain_visible_in_the_fall(self):
        for obj in range(300, 314):
            empty, boots, cloak, both = (art.decode_frame(p, 13)[2] for p in (
                self.picture(obj, True, None, 0),
                self.picture(obj, True, "boots", game.SPEED_BOOTS_TYPE, sg.FIRE_GLOW),
                self.picture(obj, True, "cloak", game.ELVEN_CLOAK_TYPE, sg.GREEN_GLOW),
                self.pictures.build(obj, True, {
                    "boots": (game.SPEED_BOOTS_TYPE, 5, sg.MAGIC, sg.FIRE_GLOW),
                    "cloak": (game.ELVEN_CLOAK_TYPE, 5, sg.MAGIC, sg.GREEN_GLOW)}, ())))
            boot_cells = {(x, y) for y, row in enumerate(boots) for x, shade in enumerate(row)
                          if shade != empty[y][x]}
            if obj == 313:
                self.assertEqual(empty, both)
                continue
            self.assertGreaterEqual(sum(boots[y][x] in sg.GLOWS[sg.FIRE_GLOW]
                                        for x, y in boot_cells), 2, obj)
            self.assertTrue(any(shade in sg.GLOWS[sg.GREEN_GLOW] and shade != empty[y][x]
                                for y, row in enumerate(cloak) for x, shade in enumerate(row)), obj)
            self.assertTrue(all(boots[y][x] == both[y][x] for x, y in boot_cells), obj)
