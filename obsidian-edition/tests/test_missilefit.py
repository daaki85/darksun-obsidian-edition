"""Missile slots on the registered party cels, including the native firing bow."""
import os
from itertools import combinations
from pathlib import Path
import struct
from types import SimpleNamespace
import unittest

from dsloader import art, game, spritegear as sg, sprites


class QuiverStateTests(unittest.TestCase):
    def test_a_depleted_retail_arrow_stack_leaves_the_case_empty(self):
        rec = bytearray(game.ITEM_SIZE)
        rec[game.ITEM_SLOT] = game.EQUIP_SLOTS.index("ammo")
        struct.pack_into("<H", rec, game.ITEM_TYPE, 62)
        member = SimpleNamespace(_worn=lambda _: [(0, rec, bytes(game.ITEM_TYPE_SIZE))])
        self.assertEqual(sprites.worn(member, 0), ({}, ()))
        struct.pack_into("<H", rec, 2, 1)
        self.assertIn("ammo", sprites.worn(member, 0)[0])


@unittest.skipUnless(os.environ.get("DSUN_OBJECTS"), "needs the retail figures and game palette")
class MissileFitTests(unittest.TestCase):
    def setUp(self):
        self.addCleanup(sg.set_palette, list(sg._RGB))
        dresser = sprites.Dresser.for_game(None, str(Path(os.environ["DSUN_OBJECTS"]).parent))
        if dresser is None:
            self.skipTest("needs the game palette and objects archive")
        self.pictures = dresser.pics

    def frame(self, obj, role, pose, gear):
        combat, f = divmod(pose, 15)
        chunk = self.pictures.build(obj, bool(combat), gear, (), role=role)
        return art.decode_frame(chunk, f)[2]

    def test_arrows_only_add_exposed_fletching_to_bow_and_quiver(self):
        bow = {"missile": (1, 0)}
        for obj, role in ((300, "Warrior"), (310, "Fighter"), (309, "Psionicist")):
            with self.subTest(obj=obj):
                plain = self.frame(obj, role, 1, bow)
                loaded = self.frame(obj, role, 1, {**bow, "ammo": (62, 0)})
                enchanted = self.frame(obj, role, 1, {**bow, "ammo": (62, 0, sg.MAGIC, sg.BLUE_GLOW)})
                tips = [b for arow,brow in zip(plain,loaded) for a,b in zip(arow,brow) if a != b]
                self.assertGreater(len(tips), 0)
                self.assertTrue(set(tips) <= set(sg.FLETCHING + sg.STAVE))
                self.assertTrue(any(c in sg.GLOWS[sg.BLUE_GLOW] for row in enchanted for c in row))

    def test_quivered_blade_shows_a_hilt_and_non_arrow_ammo_shows_a_pouch(self):
        def carry(kind, material):
            return self.frame(300, "Warrior", 1, {"ammo": (kind, material)})
        empty = self.frame(300, "Warrior", 1, {})
        arrows, dagger, pouch = carry(62, 0), carry(17, 3), carry(255, 2)
        for first, second in combinations((empty, arrows, dagger, pouch), 2):
            self.assertNotEqual(first, second)
        self.assertEqual(carry(game.SHORT_SWORD_TYPE, 3), dagger)

    def test_womans_stowed_gear_contacts_her_moving_profile_shoulder(self):
        for role in ("Warrior", "Gladiator"):
            for pose in (11, 12):
                plain = self.frame(301, role, pose, {})
                silhouette = {(x,y) for y,row in enumerate(plain) for x,c in enumerate(row) if c is not None}
                for kind in (1, game.STAFF_SLING_TYPE):
                    with self.subTest(role=role, pose=pose, kind=kind):
                        worn = self.frame(301, role, pose, {"missile": (kind,0)})
                        outer = {(x,y) for y,row in enumerate(worn) for x,c in enumerate(row)
                                 if c is not None and (x,y) not in silhouette}
                        self.assertTrue(outer)
                        attached = {p for p in outer if any((p[0]+dx,p[1]+dy) in silhouette
                                    for dx in (-1,0,1) for dy in (-1,0,1))}
                        fringe = list(attached)
                        while fringe:
                            x,y = fringe.pop()
                            for dx in (-1,0,1):
                                for dy in (-1,0,1):
                                    q = x+dx,y+dy
                                    if q in outer and q not in attached:
                                        attached.add(q)
                                        fringe.append(q)
                        self.assertEqual(outer, attached)

    def test_staff_sling_and_hand_sling_fit_differently_on_the_back(self):
        for pose in (1, 25, 28):
            with self.subTest(pose=pose):
                plain = self.frame(308, "Fighter", pose, {})
                hand = self.frame(308, "Fighter", pose, {"missile": (64,5)})
                staff = self.frame(308, "Fighter", pose, {"missile": (game.STAFF_SLING_TYPE,5)})
                self.assertNotEqual(plain, hand)
                self.assertNotEqual(plain, staff)
                self.assertNotEqual(hand, staff)

    def test_hip_throwing_blade_stays_behind_the_stock_bow(self):
        for obj, pose, cells in ((313, 24, ((9,21),(10,21))), (310, 25, ((3,5),)),
                                 (309, 26, ((29,23),))):
            with self.subTest(obj=obj, pose=pose):
                plain = self.frame(obj, None, pose, {})
                side, above = sprites.room(True)
                for gear in ({"missile": (48,3)}, {"missile": (1,0), "ammo": (62,0)}):
                    worn = self.frame(obj, None, pose, gear)
                    for x,y in cells:
                        self.assertIn(plain[above+y][side+x], (179, 180, 181, 182, 183))
                        self.assertEqual(worn[above+y][side+x], plain[above+y][side+x])
