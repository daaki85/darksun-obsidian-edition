"""The inventory reader's figure/class keys and the installed garment layers."""

import sys
import unittest
from pathlib import Path
from zipfile import ZipFile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from dsloader import art, icons, inventoryart


class InventoryArtTests(unittest.TestCase):
    def test_every_build_fits_and_differs(self):
        # Stand-ins with the native dimensions keep this check independent of game files.
        with ZipFile(Path(inventoryart.__file__).with_name("inventory-garments.zip")) as archive:
            originals = {}
            for figure, builds in enumerate(inventoryart.BUILDS):
                name = inventoryart.pieces(figure, next(iter(builds)))[0]
                w, h, _ = art.decode_frame(archive.read(f"{figure}/{name}"))
                originals["BMP ", 20000 + figure] = icons.encode([[16] * w for _ in range(h)])
        made = inventoryart.chunks(originals)
        self.assertEqual(len(made), 308)
        for figure, builds in enumerate(inventoryart.BUILDS):
            stock = originals["BMP ", 20000 + figure]
            portraits = []
            for classes in builds:
                key = inventoryart.picture_id(figure, classes)
                self.assertEqual(key, inventoryart.picture_id(figure, reversed(classes)))
                picture = made["BMP ", key]
                self.assertEqual(art.decode_frame(picture)[:2], art.decode_frame(stock)[:2])
                self.assertNotEqual(picture, stock)
                portraits.append(picture)
            self.assertEqual(len(set(portraits)), len(portraits))

    def test_missing_or_differently_sized_source_uses_game_portrait(self):
        custom = {("BMP ", 20000): icons.encode([[42]])}
        self.assertEqual(inventoryart.chunks(custom), {})
