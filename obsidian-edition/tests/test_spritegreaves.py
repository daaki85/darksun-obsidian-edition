"""Registered leg armor follows each calf below the garment and above the boots."""
import os
from pathlib import Path
import unittest

from dsloader import art, classoutfits as co, game, spritegear as sg, spritegreaves, sprites


@unittest.skipUnless(os.environ.get("DSUN_OBJECTS"), "needs the retail picture archive and palette")
class GreaveTests(unittest.TestCase):
    def setUp(self):
        self.addCleanup(sg.set_palette, list(sg._RGB))
        dresser = sprites.Dresser.for_game(None, str(Path(os.environ["DSUN_OBJECTS"]).parent))
        if dresser is None:
            self.skipTest("needs the retail figures and game palette")
        self.pictures = dresser.pics

    def test_plate_and_enchantment_follow_the_exposed_calf_in_profile(self):
        tier = game.PLATE_LEGS_TYPE
        magic = tier | sg.MAGIC_ARMOUR | (sg.BLUE_GLOW << sg.GLOW_SHIFT)
        side, top = sprites.room(False)
        for obj, role, anchors in ((309, "Psionicist", ((7, 30), (7, 32), (6, 34))),
                                   (312, "Druid/Fighter", ((4, 22), (4, 23))),
                                   (300, "Warrior", ((4, 21), (4, 22)))):
            with self.subTest(obj=obj):
                model = self.pictures.model(obj)
                fit = co.frames(role, False, model)[13]
                boots = set(fit.regions[co.LEFT_FOOT]) | set(fit.regions[co.RIGHT_FOOT])
                def render(slot, gear):
                    chunk = self.pictures.build(obj, False, gear, slot, role=role)
                    return art.decode_frame(chunk, 13)[2]
                for gear in ({}, {"boots": (game.SPEED_BOOTS_TYPE, 5)}):
                    bare, plate, shine = (render(slot, gear) for slot in ((), (tier,), (magic,)))
                    if obj == 309:
                        # The teal hem now covers the pixel immediately above the shin.
                        self.assertEqual(bare[29+top][7+side], 69)
                        self.assertEqual(plate[29+top][7+side], bare[29+top][7+side])
                    for x, y in anchors:
                        self.assertNotEqual(bare[y+top][x+side], plate[y+top][x+side])
                        self.assertIn(plate[y+top][x+side], sg.METAL_SHADES)
                    for x, y in boots:
                        self.assertEqual(bare[y+top][x+side], plate[y+top][x+side])
                        self.assertEqual(plate[y+top][x+side], shine[y+top][x+side])
                    lower = [(x, y) for y in range(min(y for x, y in anchors), len(plate)-top)
                             for x in range(len(plate[0])-side) if shine[y+top][x+side] != plate[y+top][x+side]]
                    self.assertTrue(lower)
                    self.assertTrue(all(shine[y+top][x+side] in sg.GLOWS[sg.BLUE_GLOW] for x, y in lower))

    def test_full_length_hem_hides_the_greave_underneath(self):
        for obj, role, pose in ((309, "Cleric", 1), (301, "Priest", 13)):
            with self.subTest(obj=obj):
                model, rows, owners = self.pictures.base(self.pictures.model(obj), obj, False)
                fit = co.frames(role, False, model)[pose]
                source = fit.canvas(rows[pose], sprites.PAD)
                self.assertFalse(spritegreaves.visible(rows[pose], model, pose, False, owners[pose],
                                                       fit, source, sprites.PAD))
