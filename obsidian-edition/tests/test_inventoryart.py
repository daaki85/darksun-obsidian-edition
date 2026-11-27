"""Human inventory keys, native pose layers and the stock fallback."""

import os
import sys
import unittest
from pathlib import Path
from zipfile import ZipFile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from dsloader import art, icons, inventoryart


class InventoryArtTests(unittest.TestCase):
    def test_every_race_and_legal_build(self):
        from dsloader import classoutfits
        sizes = [(48, 95), (44, 88), (64, 70), (48, 70), (71, 92), (70, 89), (45, 93), (50, 94),
                 (78, 88), (66, 87), (45, 69), (33, 61), (62, 106), (79, 95)]
        human = {(c,) for c in range(1, 9)}
        legal = [human, human] + [set(roles) for roles in (
            classoutfits.DWARF_ROLES, classoutfits.ELF_ROLES, classoutfits.HALF_ELF_ROLES,
            classoutfits.HALF_GIANT_ROLES, classoutfits.HALFLING_ROLES) for _ in (0, 1)]
        legal += [set(classoutfits.MUL_ROLES), set(inventoryart.THRI_KREEN)]
        resources = {}
        for figure, (w, h) in enumerate(sizes):
            resources["BMP ", art.FIGURE_FIRST + figure] = icons.encode([[16] * w for _ in range(h)])
        with ZipFile(Path(inventoryart.__file__).with_name("inventory-garments.zip")) as archive:
            builds = inventoryart.builds(archive.namelist())
        self.assertEqual(set(builds), set(range(14)))
        for figure, wanted in builds.items():
            self.assertEqual(set(wanted), legal[figure], f"figure {figure}")
        pictures = inventoryart.chunks(resources)
        expected = {("BMP ", inventoryart.picture_id(f, c)) for f, wanted in builds.items() for c in wanted}
        self.assertEqual(set(pictures), expected)
        self.assertEqual(len(pictures), 306)
        for f, dims in enumerate(sizes):
            for c in builds[f]:
                w, h, rows = art.decode_frame(pictures["BMP ", inventoryart.picture_id(f, c)])
                self.assertEqual((w, h), dims)
        rows = art.decode_frame(pictures["BMP ", inventoryart.picture_id(0, (1,))])[2]
        self.assertIsNone(rows[7][15])  # Old horn cut back to parchment.

    def test_entry_names_round_trip(self):
        self.assertEqual(inventoryart.entry(4, (6, 3, 1)), "4/body1-3-6")
        self.assertEqual(inventoryart.builds(["4/body1-3-6", "0/body2"]), {4: [(1, 3, 6)], 0: [(2,)]})

    def test_missing_or_differently_sized_source_uses_game_portrait(self):
        custom = {("BMP ", 20000): icons.encode([[42]])}
        self.assertEqual(inventoryart.chunks(custom), {})

    def test_layers_use_only_colours_no_area_changes(self):
        from dsloader.spritegear import REGIONAL
        with ZipFile(inventoryart.ARCHIVE) as archive:
            for name in archive.namelist():
                _, _, rows = art.decode_frame(archive.read(name))
                with self.subTest(layer=name):
                    self.assertFalse({p for row in rows for p in row} & REGIONAL)

    def test_whole_picture_becomes_layer_keeping_the_head(self):
        from dsloader.spritegear import STEADY
        colours = [(i, i, i) for i in range(256)]
        stock = [[50, 60, 70], [50, 60, 70], [None, 60, None]]
        picture = [[(200, 200, 200), (90, 90, 90), (70, 70, 70)],
                   [(50, 50, 50), None, (100, 100, 100)],
                   [None, (60, 60, 60), (61, 61, 61)]]
        layer = inventoryart.layer_from_picture(picture, stock, colours, head=(0, 1, 0, 2))
        self.assertEqual(layer[0][:2], [None, None])  # The head stays stock.
        self.assertIsNone(layer[0][2])  # The stock colour is kept as it is.
        self.assertEqual(layer[1][:2], [None, inventoryart.CLEAR])  # Unpainted stock goes.
        self.assertIn(layer[1][2], STEADY)  # A new colour is drawn from the fixed ones.
        self.assertEqual(layer[2][0], None)
        self.assertIn(layer[2][2], STEADY)
        with self.assertRaises(ValueError):
            inventoryart.layer_from_picture(picture[:2], stock, colours)

    @unittest.skipUnless(os.getenv("DSUN_SL"), "needs the Shattered Lands inventory figures")
    def test_no_detached_pixels_on_retail_figures(self):
        art_data = art.GameArt(os.environ["DSUN_SL"])
        resources = {("BMP ", k): v for k, v in art_data.figures.items()}
        # The humans only: the other races' roster of 2026-11-27 has background-keyed pinholes in
        # its light cloth, which leave specks apart.
        for key, frame in inventoryart.chunks(resources).items():
            if (key[1] - inventoryart.FIRST) >> 8 > 1:
                continue
            with self.subTest(picture=key):
                _, _, rows = art.decode_frame(frame)
                visible = {(x, y) for y, row in enumerate(rows) for x, p in enumerate(row) if p is not None}
                pending = [visible.pop()]
                while pending:
                    x, y = pending.pop()
                    for point in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                        if point in visible:
                            visible.remove(point)
                            pending.append(point)
                self.assertFalse(visible)
