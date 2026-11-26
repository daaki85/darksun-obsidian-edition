"""Legally equipped off-hand weapons stay with their palm or scabbard."""

import os
from pathlib import Path
import unittest
from unittest.mock import patch

from dsloader import art, spritegear as sg, spritegiantgrips, sprites


@unittest.skipUnless(os.environ.get("DSUN_OBJECTS"), "needs the retail picture archives")
class DualWeaponTests(unittest.TestCase):
    def setUp(self):
        self.addCleanup(sg.set_palette, list(sg._RGB))
        dresser = sprites.Dresser.for_game(None, str(Path(os.environ["DSUN_OBJECTS"]).parent))
        if dresser is None:
            self.skipTest("needs the retail objects and palette")
        self.pics = dresser.pics

    def test_both_giant_staffs_follow_the_fists_through_the_entire_walk(self):
        for obj, model in ((308, 2072), (309, 2074)):
            for role in (None, "Fighter"):
                main = self.pics.build(obj, False, {"right": (3, 0)}, (), role=role)
                with patch.object(sg, "draw_weapon", wraps=sg.draw_weapon) as held:
                    both = self.pics.build(obj, False, {"right": (3, 0), "left": (3, 0)}, (), role=role)
                self.assertEqual(held.call_count, 30)
                for pose, (right, left) in enumerate(spritegiantgrips.WALK[model]):
                    with self.subTest(obj=obj, role=role, pose=pose):
                        for hand, (x, y), call in zip(("left", "right"), (left, right),
                                                      held.call_args_list[2*pose:2*pose+2]):
                            self.assertEqual(call.args[2], (x+sprites.PAD, y+sprites.PAD))
                            self.assertEqual(call.args[4], sg.STAFF)
                            if spritegiantgrips.HIDDEN.get(pose) == hand:
                                self.assertTrue(call.args[6])
                        off = art.decode_frame(main, pose)[2]
                        on = art.decode_frame(both, pose)[2]
                        self.assertTrue(any(a != b for old, worn in zip(off, on) for a, b in zip(old, worn)))

    def test_far_sheath_uses_its_hip_even_when_the_walking_hand_is_hidden(self):
        with patch.object(sg, "draw_weapon", wraps=sg.draw_weapon) as blades:
            self.pics.build(300, False, {"right": (45, 4), "left": (sg.game.SHORT_SWORD_TYPE, 3)}, ())
        self.assertEqual(blades.call_count, 30)
        for pose in range(15):
            offhand, main = blades.call_args_list[2*pose:2*pose+2]
            self.assertEqual(offhand.args[4], sg.SHORT_SWORD)
            self.assertEqual(main.args[4], sg.SWORD)
            left, right = offhand.args[2], main.args[2]
            if pose in (2, 11, 12, 13, 14):
                self.assertTrue(offhand.args[6])  # behind the near leg
                self.assertNotEqual(left, right)
            elif pose in (1, 7, 8, 9, 10):
                self.assertLess(left[0], right[0])
            else:
                self.assertGreater(left[0], right[0])

    def test_right_loop_is_the_same_native_hip_alone_or_with_a_second_item(self):
        # The giant's front step used to select a hand or the outer edge of
        # the jerkin. Follow the same anatomical point through three loadouts.
        for second in ({}, {"left": (17, 3)}, {"left": (4, 5)}):
            with self.subTest(second=second):
                with patch.object(sg, "draw_weapon", wraps=sg.draw_weapon) as held:
                    self.pics.build(308, False, {"right": (63, 4), **second}, (), role="Fighter")
                swords = [call for call in held.call_args_list if call.args[4] == sg.SWORD]
                self.assertEqual(len(swords), 15)
                self.assertEqual(swords[4].args[2], (sprites.PAD + 9, sprites.PAD + 21))

    def test_automatic_second_cahulak_and_explicit_pair_match_for_walks_and_strikes(self):
        for obj in (300, 309, 313):
            for combat in (False, True):
                kit = {"right": (21, 1)}
                single = self.pics.build(obj, combat, kit, ())
                pair = self.pics.build(obj, combat, {**kit, "left": (21, 1)}, ())
                self.assertEqual(single, pair)
                if combat:
                    base = self.pics.build(obj, True, {}, ())
                    for f in (9, 10, 11, 13):
                        self.assertEqual(art.decode_frame(base, f)[2], art.decode_frame(pair, f)[2])
