import os
import re
import struct
import sys
import unittest
import zlib

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dsloader import docicons  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class DocIconsTests(unittest.TestCase):
    def test_png(self):
        """Twice the size, a palette number's colour opaque, None transparent."""
        data = docicons.png([[1, None]], [(0, 0, 0), (10, 20, 30)])
        self.assertEqual(data[:8], b"\x89PNG\r\n\x1a\n")
        width, height = struct.unpack_from(">II", data, 16)
        self.assertEqual((width, height), (4, 2))
        at = data.index(b"IDAT")
        size, = struct.unpack_from(">I", data, at - 4)
        raw = zlib.decompress(data[at + 4:at + 4 + size])
        self.assertEqual(raw[:17], b"\0" + bytes((10, 20, 30, 255)) * 2 + bytes(8))

    def test_guide_icons_there(self):
        """Every icon the item tables show is in docs/items, and has a picture to draw it from."""
        with open(os.path.join(ROOT, "ITEMS.md"), encoding="utf-8") as f:
            names = set(re.findall(r"docs/items/([a-z0-9-]+)\.png", f.read()))
        self.assertTrue(names)
        for name in names:
            self.assertIn(name, docicons.ICONS)
            self.assertTrue(os.path.exists(os.path.join(ROOT, "docs", "items", name + ".png")), name)

    def test_no_unused_icons(self):
        """Every picture in docs/items is shown by the README, the features page, the item tables or the player's guide."""
        shown = set()
        for doc in ("README.md", "FEATURES.md", "ITEMS.md", "PLAYER-GUIDE.md"):
            with open(os.path.join(ROOT, doc), encoding="utf-8") as f:
                shown |= set(re.findall(r"docs/items/([a-z0-9-]+)\.png", f.read()))
        for png in os.listdir(os.path.join(ROOT, "docs", "items")):
            self.assertIn(png[:-4], shown, png)


if __name__ == "__main__":
    unittest.main()
