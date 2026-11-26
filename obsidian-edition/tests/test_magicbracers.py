import os
import unittest
from pathlib import Path

from dsloader import art, classoutfits as co, game, spritegear as sg, sprites


@unittest.skipUnless(os.environ.get("DSUN_OBJECTS"), "needs the player's SEGOBJEX.GFF")
class MagicBracersTests(unittest.TestCase):
    def setUp(self):
        self.addCleanup(sg.set_palette, list(sg._RGB))
        dresser = sprites.Dresser.for_game(None, str(Path(os.environ["DSUN_OBJECTS"]).parent))
        if dresser is None:
            self.skipTest("needs the retail objects and palette in the game directory")
        self.pictures = dresser.pics

    def worn(self, obj, role, pose, enchanted=True, gear=None, armor=()):
        combat, f = divmod(pose, 15)
        piece = game.BRACERS_TYPE | (sg.MAGIC_ARMOUR if enchanted else 0)
        gear = gear or {}
        plain = self.pictures.build(obj, combat, gear, armor, role=role)
        equipped = self.pictures.build(obj, combat, gear, (*armor, piece), role=role)
        empty = art.decode_frame(plain, f)[2]
        worn = art.decode_frame(equipped, f)[2]
        sx, sy = sprites.room(combat)
        changes = {(x - sx, y - sy): color for y, row in enumerate(worn)
                   for x, color in enumerate(row) if color != empty[y][x]}
        self.assertTrue(all(value is not None and empty[y + sy][x + sx] is not None
                            for (x, y), value in changes.items()))
        return changes

    def test_dwarf_bracers_wrap_the_two_wristbands_and_clear_the_shoulder_caps(self):
        plain = self.worn(302, "Cleric/Fighter", 0, enchanted=False)
        magic = self.worn(302, "Cleric/Fighter", 0)
        self.assertEqual(set(plain), set(magic))
        self.assertTrue(any(value in sg.GLOWS[sg.FIRE_GLOW] for value in magic.values()))
        self.assertEqual(set(magic), {(1, 10), (2, 9), (3, 9), (17, 9), (18, 9), (19, 9)})
        shoulders = co.frames("Cleric/Fighter", False, 2055)[0].regions[co.ARMS]
        self.assertTrue(set(magic).isdisjoint(shoulders))

    def test_shield_occludes_the_off_hand_bracer_during_a_strike(self):
        bare_wrists = self.worn(302, "Cleric/Fighter", 16)
        armed = self.worn(302, "Cleric/Fighter", 16,
                          gear={"left": (4, 0), "right": (45, 4), "cloak": (65, 0)}, armor=(88,))
        self.assertTrue(armed)
        self.assertLess(set(armed), set(bare_wrists))

    def test_woman_rear_stride_shows_reconstructed_wrists_only_above_uncovered_arms(self):
        self.assertEqual(self.worn(301, None, 7), {})
        self.assertEqual(self.worn(301, "Thief", 7), {})
        warrior = self.worn(301, "Warrior", 7)
        self.assertEqual(set(warrior), {(3, 9), (4, 9), (13, 13), (14, 13)})
        half_elf = self.worn(307, "Fighter", 7)
        self.assertEqual(set(half_elf), {(3, 9), (4, 9), (12, 13), (13, 13)})

    def test_half_giant_magic_stays_under_the_hands_in_the_second_front_strike(self):
        for obj, cuffs in ((308, ((7, 6), (29, 23))), (309, ((7, 10), (29, 27)))):
            with self.subTest(obj=obj):
                visible = self.worn(obj, None, 16)
                self.assertTrue(all(any(abs(x-cx) <= 1 and abs(y-cy) <= 1 for cx, cy in cuffs)
                                    for x, y in visible))
                self.assertTrue(all(any(abs(x-cx) <= 1 and abs(y-cy) <= 1 for x, y in visible)
                                    for cx, cy in cuffs))
        self.assertEqual(self.worn(313, None, 16), {})
