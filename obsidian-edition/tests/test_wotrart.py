"""Wake of the Ravager's icons (wotrart.py), on pictures made here: nothing from either game."""

import os
import struct
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import art, sprites, wotrart
from test_core import build_gff


def plnr(width, height, bits, colours, codes):
    """A PLNR picture: Shattered Lands' frame header, then 0FFh "PLNR", BITS, the colour map and
    CODES packed BITS a code, the highest bits first."""
    acc = n = 0
    data = bytearray()
    for code in codes:
        acc, n = (acc << bits) | code, n + bits
        while n >= 8:
            n -= 8
            data.append((acc >> n) & 0xFF)
    if n:
        data.append((acc << (8 - n)) & 0xFF)
    body = (struct.pack("<HH", width, height) + wotrart.PLNR + bytes([bits])
            + bytes(colours).ljust(1 << bits, b"\0") + bytes(data))
    return struct.pack("<IHI", 10 + len(body), 1, 10) + body


class PlnrTests(unittest.TestCase):
    def test_codes_and_escapes(self):
        """Codes through the colour map; 0 0 is colour 0, 0 k the last pixel k + 2 more times."""
        colours = [9, 40, 41, 42]
        chunk = plnr(4, 2, 4, colours, [1, 2, 0, 0, 3,   # 40 41 9 42
                                        2, 0, 1])        # 41, then 3 more
        self.assertEqual(wotrart.decode_plnr(chunk), [[40, 41, 9, 42], [41, 41, 41, 41]])

    def test_five_bits(self):
        colours = list(range(100, 132))
        chunk = plnr(2, 2, 5, colours, [31, 17, 0, 0, 5])
        self.assertEqual(wotrart.decode_plnr(chunk), [[131, 117], [100, 105]])

    def test_short_data_pads_with_colour_0(self):
        self.assertEqual(wotrart.decode_plnr(plnr(3, 1, 4, [7, 8], [1])), [[8, 7, 7]])

    def test_not_plnr(self):
        chunk = bytearray(plnr(1, 1, 4, [0, 1], [1]))
        chunk[15:19] = b"PLAN"
        with self.assertRaises(ValueError):
            wotrart.decode_plnr(bytes(chunk))

    def test_nearest_stable_colour(self):
        stable = [(5, (0, 0, 0)), (40, (250, 10, 10)), (41, (10, 10, 250))]
        palette = {0: (20, 20, 20), 1: (200, 30, 30), 2: (30, 30, 200)}
        self.assertEqual(wotrart.to_shattered_lands([[0, 1, 2, 1]], palette, stable), [[5, 40, 41, 40]])

    def test_every_spell_has_an_icon(self):
        self.assertEqual(len(wotrart.ICONS), 9)
        self.assertEqual(len(set(wotrart.ICONS.values())), 9)
        self.assertIn("Whirlwind", wotrart.ICONS)


def palette(colours):
    """A VGA palette chunk (6 bits a channel) with COLOURS {index: (r, g, b)}, black elsewhere."""
    out = bytearray(768)
    for i, rgb in colours.items():
        out[3 * i:3 * i + 3] = bytes(v * 63 // 255 for v in rgb)
    return bytes(out)


class AreaTests(unittest.TestCase):
    """Blade Barrier's and Wall of Thorns' pictures on the ground (area_chunks)."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = self.tmp.name
        sl_colours = {1: (255, 0, 0), 2: (255, 255, 0), 3: (200, 210, 235), 4: (120, 80, 35), 5: (0, 255, 0)}
        self.gpldata = os.path.join(self.dir, "GPLDATA.GFF")
        with open(self.gpldata, "wb") as f:  # (two regions' palettes, alike: every colour stable)
            f.write(build_gff({("PAL ", 1): palette(sl_colours), ("PAL ", 2): palette(sl_colours)}))
        wall = struct.pack("<8H", 16, 12, 33, 176, 1104, 0, 100, 0)  # (the fire wall: picture 100)
        self.sl = {("OJFF", wotrart.FIRE_WALL_OBJECT): wall,
                   ("BMP ", 100): sprites.encode_frames([[[1, 2], [2, None]]])}

    def tearDown(self):
        self.tmp.cleanup()

    def frame(self, chunks, name):
        number, picture = wotrart.AREA_OBJECTS[name]
        record = chunks[("OJFF", number)]
        self.assertEqual(struct.unpack_from("<H", record, 12)[0], picture)
        return record, art.decode_frame(chunks[("BMP ", picture)])[2]

    def test_without_wake_of_the_ravager(self):
        """The fire wall's picture in each spell's colour, its object's anchor the fire wall's."""
        out = wotrart.area_chunks(None, self.sl, self.gpldata)
        self.assertEqual(len(out), 4)
        record, rows = self.frame(out, "Blade Barrier")
        self.assertEqual(record[2:6], self.sl[("OJFF", wotrart.FIRE_WALL_OBJECT)][2:6])
        self.assertEqual(rows[1][1], None)
        self.assertNotIn(1, sum(rows, []))  # (no red left)

    def test_wake_of_the_ravager(self):
        """Its own pictures, in Shattered Lands' nearest colours, and their anchors."""
        wotr = os.path.join(self.dir, "wotr")
        os.mkdir(wotr)
        resources = os.path.join(wotr, "RESOURCE.GFF")
        with open(resources, "wb") as f:
            f.write(build_gff({wotrart.PALETTE: palette({7: (0, 250, 0), 9: (250, 250, 0)})}))
        objects = {}
        for i, (number, _) in enumerate(wotrart.AREA_OBJECTS.values()):
            objects[("OJFF", number)] = struct.pack("<8H", 0, 17 + i, 33, 0, 0, 0, 500 + i, 0)
            objects[("BMP ", 500 + i)] = sprites.encode_frames([[[7, 9, None]]])
        with open(os.path.join(wotr, wotrart.OBJECTS_FILE), "wb") as f:
            f.write(build_gff(objects))
        out = wotrart.area_chunks(resources, self.sl, self.gpldata)
        record, rows = self.frame(out, "Wall of Thorns")
        self.assertEqual(struct.unpack_from("<HH", record, 2), (18, 33))
        self.assertEqual(record[6:12], self.sl[("OJFF", wotrart.FIRE_WALL_OBJECT)][6:12])
        self.assertEqual(rows, [[5, 2, None]])

    def test_no_fire_wall(self):
        self.assertEqual(wotrart.area_chunks(None, {}, self.gpldata), {})


class FindTests(unittest.TestCase):
    """Where the Loader looks for Wake of the Ravager's RESOURCE.GFF (find_resources)."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name
        self.sl = os.path.join(self.root, "Dark Sun Shattered Lands")
        os.makedirs(self.sl)
        self.chosen, self.own = None, wotrart._chosen
        wotrart._chosen = lambda: self.chosen  # (not the Loader's own settings)

    def tearDown(self):
        wotrart._chosen = self.own
        self.tmp.cleanup()

    def install(self, *parts, heal=wotrart.HEAL_SPIN[1]):
        folder = os.path.join(self.root, *parts)
        os.makedirs(folder, exist_ok=True)
        with open(os.path.join(folder, "RESOURCE.GFF"), "wb") as f:
            f.write(build_gff({("SPIN", wotrart.HEAL_SPIN[0]): heal + b"  Cures..."}))
        return os.path.join(folder, "RESOURCE.GFF")

    def test_beside_by_either_name(self):
        self.assertIsNone(wotrart.find_resources(self.sl))
        path = self.install("Dark Sun 2 Wake")
        self.assertEqual(wotrart.find_resources(self.sl), path)

    def test_a_folder_inside(self):
        path = self.install("Dark Sun Wake of the Ravager", "DARKSUN2")
        self.assertEqual(wotrart.find_resources(self.sl), path)

    def test_chosen_folder(self):
        path = self.install("Games", "Elsewhere")
        self.assertIsNone(wotrart.find_resources(self.sl))
        self.chosen = os.path.dirname(path)
        self.assertEqual(wotrart.find_resources(self.sl), path)
        self.assertEqual(wotrart.find_resources(None, os.path.dirname(path)), path)

    def test_not_shattered_lands_own(self):
        self.install("Wake of the Ravager", heal=b"BLESS:")
        self.assertIsNone(wotrart.find_resources(self.sl))


if __name__ == "__main__":
    unittest.main()
