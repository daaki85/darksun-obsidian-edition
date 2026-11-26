"""Waist equipment on the Loader's registered poses and on unmodified party outfits."""

import os
from pathlib import Path
import struct
import unittest

from dsloader import art, dataitems, game, icons, spritegear as sg, sprites, worldgear


@unittest.skipUnless(os.environ.get("DSUN_OBJECTS"), "needs the player's SEGOBJEX.GFF")
class MagicBeltsTests(unittest.TestCase):
    def setUp(self):
        self.addCleanup(sg.set_palette, list(sg._RGB))
        dresser = sprites.Dresser.for_game(None, str(Path(os.environ["DSUN_OBJECTS"]).parent))
        if dresser is None:
            self.skipTest("needs the retail objects and palette in the game directory")
        self.pictures = dresser.pics
        self.catalog = {**dresser.items, **icons.new_chunks(dresser.items)}

    def equipped(self, record, slot="waist"):
        rec = bytearray(record)
        rec[game.ITEM_SLOT] = game.EQUIP_SLOTS.index(slot)
        name = icons.which(rec)
        if name:
            struct.pack_into("<H", rec, 0, icons.picture(name, True))

        class Worn:
            def _worn(self, member):
                return [(0, rec, bytes(game.ITEM_TYPE_SIZE))]

        return sprites.worn(Worn(), 0, self.catalog)[0]

    def difference(self, obj, role, pose, gear):
        combat, f = divmod(pose, 15)
        def rendered(items):
            chunk = self.pictures.build(obj, combat, items, (), role=role)
            return art.decode_frame(chunk, f)[2]

        plain, equipped = rendered({}), rendered(gear)
        sx, sy = sprites.room(combat)
        changes = {(x-sx, y-sy): v for y, row in enumerate(equipped) for x, v in enumerate(row)
                   if v != plain[y][x]}
        self.assertTrue(all(plain[y+sy][x+sx] is not None and v is not None
                            for (x, y), v in changes.items()))
        return changes

    def test_named_girdles_use_their_inventory_materials_and_glint_only_on_the_band(self):
        back = self.equipped(worldgear.BACK_GIRDLE_ITEM)
        gold = self.equipped(worldgear.URNST_GIRDLE_ITEM)
        self.assertEqual(back["belt"], (game.BACK_GIRDLE_TYPE, 0, sg.MAGIC, sg.BLUE_GLOW))
        self.assertEqual(gold["belt"], (game.URNST_GIRDLE_TYPE, 0, sg.MAGIC, sg.BLUE_GLOW))
        a, b = [self.difference(300, "Warrior", 0, gear) for gear in (back, gold)]
        band = {(x, 14) for x in range(5, 15)}
        for points in (a, b):
            self.assertEqual(set(points), band)
            self.assertEqual(sum(v in sg.GLOWS[sg.BLUE_GLOW] for v in points.values()), 1)
        self.assertIn(37, a.values())  # violet stitch on the brown hide
        self.assertEqual(b[10, 14], 183)  # gold clasp on the red silk

    def test_retail_belt_of_might_resolves_through_waist_slot_and_uses_fire(self):
        records, _ = dataitems.records(self.catalog["RDFF", 30017])
        item = next(r.data for r in records if r.kind == dataitems.ITEM and
                    len(r.data) == game.ITEM_SIZE and
                    struct.unpack_from("<H", r.data, game.ITEM_TYPE)[0] == sg.MIGHT_BELT)
        gear = self.equipped(item)
        self.assertEqual(gear["belt"], (sg.MIGHT_BELT, 0, sg.MAGIC, sg.FIRE_GLOW))
        values = self.difference(300, "Warrior", 0, gear).values()
        self.assertIn(sg.BUCKLE, values)
        self.assertTrue(set(values).intersection(sg.GLOWS[sg.FIRE_GLOW]))
        self.assertNotIn("belt", self.equipped(item, "right hand"))

    def test_cloak_and_crossing_hand_hide_their_part_of_the_band(self):
        gear = self.equipped(worldgear.BACK_GIRDLE_ITEM)
        for obj, role, pose in ((301, None, 7), (301, "Thief", 7), (307, None, 1),
                               (302, "Cleric/Fighter", 1), (313, None, 0)):
            with self.subTest(obj=obj, role=role):
                self.assertFalse(self.difference(obj, role, pose, gear))
        self.assertEqual(set(self.difference(300, "Warrior", 13, gear)), {(2, 14), (3, 14), (4, 14)})
        self.assertEqual({y for x, y in self.difference(300, "Warrior", 14, gear)}, {15})
        self.assertEqual({y for x, y in self.difference(300, "Warrior", 28, gear)}, {7})
        self.assertTrue(self.difference(307, "Fighter", 28, gear))

    def test_all_fitted_study_models_can_equip_the_named_girdle(self):
        gear = self.equipped(worldgear.URNST_GIRDLE_ITEM)
        for obj in (308, 309, 310, 311, 312):
            with self.subTest(obj=obj):
                changes = self.difference(obj, "Fighter", 0, gear)
                self.assertTrue(set(changes.values()).intersection(sg.GLOWS[sg.BLUE_GLOW]))
