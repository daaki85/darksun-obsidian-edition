"""Held weapons and shields on the hands in the decoded map cels."""
import os
from pathlib import Path
import unittest

from dsloader import art, spritegear as sg, sprites


@unittest.skipUnless(os.environ.get("DSUN_OBJECTS"), "needs the retail figure drawings")
class WeaponGripTests(unittest.TestCase):
    def setUp(self):
        self.addCleanup(sg.set_palette, list(sg._RGB))
        dresser = sprites.Dresser.for_game(None, str(Path(os.environ["DSUN_OBJECTS"]).parent))
        if dresser is None:
            self.skipTest("requires both retail archives")
        self.pictures = dresser.pics

    def test_visible_weapon_in_each_striking_hand_and_both_bare_in_bow_cels(self):
        for obj in range(300, 314):
            roles = (None,) if obj == 313 else (None, "Warrior" if obj < 302 else "Fighter")
            for role in roles:
                empty, sword, offhand = [self.pictures.build(obj, True, gear, (), role=role) for gear in
                                         ({}, {"right": (45, 4)}, {"left": (17, 3)})]
                for f in range(14):
                    base, right, left = [art.decode_frame(p, f)[2] for p in (empty, sword, offhand)]
                    active = f not in (9, 10, 11, 13)
                    self.assertEqual(base != right, active, (obj, role, f, "right"))
                    self.assertEqual(base != left, active, (obj, role, f, "left"))

    def test_carried_staff_tracks_walking_hands_as_cuffs_vanish(self):
        for obj, poses in ((301, (1, 7, 8, 9, 10)), (307, (1, 7, 8, 9, 10)), (302, (13,)),
                           (305, (12,)), (310, (2, 13)), (311, (13,)), (313, (12,))):
            empty = self.pictures.build(obj, False, {}, ())
            staff = self.pictures.build(obj, False, {"right": (3, 0)}, ())
            for f in poses:
                body, worn = [art.decode_frame(c, f)[2] for c in (empty, staff)]
                cells = {(x, y) for y, row in enumerate(worn) for x, p in enumerate(row)
                         if p != body[y][x]}
                self.assertTrue(cells, (obj, f))
                self.assertTrue(any(body[y][x] is not None for x, y in cells)
                                or any((x+dx, y+dy) in cells
                                       for y, row in enumerate(body) for x, p in enumerate(row) if p is not None
                                       for dx in (-1, 0, 1) for dy in (-1, 0, 1)), (obj, f))

    def test_half_giant_shield_follows_the_raised_arm_in_recoil(self):
        for obj in (308, 309):
            empty, shield = [self.pictures.build(obj, True, gear, ()) for gear in
                             ({}, {"left": (4, 5)})]
            body, worn = [art.decode_frame(c, 12)[2] for c in (empty, shield)]
            sx, sy = sprites.room(True)
            points = {(x-sx, y-sy) for y, row in enumerate(worn) for x, p in enumerate(row)
                      if p != body[y][x]}
            self.assertTrue(points)
            self.assertGreater(min(x for x, y in points), 16)
            self.assertLess(max(y for x, y in points), 13)
