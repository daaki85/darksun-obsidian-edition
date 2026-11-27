"""Human inventory keys, native pose layers and the stock fallback."""

import os
import sys
import unittest
from pathlib import Path
from zipfile import ZipFile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from dsloader import art, icons, inventoryart


class InventoryArtTests(unittest.TestCase):
    def test_human_classes_only(self):
        human_sizes = [(48, 95), (44, 88)]
        resources = {}
        for figure in range(14):
            w, h = human_sizes[figure % 2]
            resources["BMP ", art.FIGURE_FIRST + figure] = icons.encode([[16] * w for _ in range(h)])
        with ZipFile(Path(inventoryart.__file__).with_name("inventory-garments.zip")) as archive:
            self.assertEqual(set(archive.namelist()), {f"{f}/body{c}" for f in (0, 1) for c in range(1, 9)})
        pictures = inventoryart.chunks(resources)
        expected = {("BMP ", 0x6000 + 256 * f + (1 << c)) for f in (0, 1) for c in range(8)}
        self.assertEqual(set(pictures), expected)
        self.assertEqual(len(set(pictures.values())), 16)
        for f, dims in enumerate(human_sizes):
            for c in range(1, 9):
                w, h, rows = art.decode_frame(pictures["BMP ", inventoryart.picture_id(f, (c,))])
                self.assertEqual((w, h), dims)
                self.assertEqual(rows[-1][0], 16)  # Unpainted pixels retain the installation's colors.
                if f == 0 and c != 8:
                    self.assertIsNone(rows[7][15])  # Old horn cut back to parchment.

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
        for key, frame in inventoryart.chunks(resources).items():
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
