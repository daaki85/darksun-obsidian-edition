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
