"""Wake of the Ravager's weapon icons in Shattered Lands (sequelicons.py), on pictures made here:
nothing from either game."""

import os
import struct
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import art, icons, sequelicons, sprites, wotrart
from test_core import build_gff
from test_wotrart import palette, plnr


def plan(width, height, bits, colours, codes):
    """A PLAN picture: as PLNR's, "PLAN" its tag and the codes plain (0 none)."""
    chunk = bytearray(plnr(width, height, bits, colours, codes))
    chunk[15:19] = b"PLAN"
    return bytes(chunk)


# the sequel's colours here: a wood, two steels, a gold, a magenta gem, an outline's black
THEIRS = {1: (150, 90, 40), 2: (90, 90, 110), 3: (200, 200, 215), 4: (255, 200, 20), 5: (200, 0, 200),
          6: (4, 4, 8)}


class DecodeTests(unittest.TestCase):
    def test_plan(self):
        """PLAN: each code a colour of the map, code 0 none."""
        self.assertEqual(sequelicons.decode(plan(3, 2, 4, [0, 40, 41], [1, 0, 2, 2, 1, 0])),
                         [[40, None, 41], [41, 40, None]])

    def test_plnr(self):
        """PLNR as wotrart reads it, its colour 0 none."""
        self.assertEqual(sequelicons.decode(plnr(2, 1, 4, [0, 9], [1, 0, 0])), [[9, None]])

    def test_shattered_lands_kind(self):
        self.assertEqual(sequelicons.decode(sprites.encode_frames([[[7, None]]])), [[7, None]])


def lone(ramp):
    """A kind's only colour: three quarters up its ramp."""
    return ramp[round(0.75 * (len(ramp) - 1))]


class LookTests(unittest.TestCase):
    STABLE = [(30, (0, 0, 0)), (31, (255, 210, 30))]

    def test_kinds(self):
        self.assertEqual([sequelicons.kind_of(THEIRS[p]) for p in sorted(THEIRS)],
                         ["wood", "steel", "steel", "gold", "gem", "other"])
        self.assertEqual(sequelicons.kind_of((68, 141, 214)), "steel")  # (a blade's blue edge)

    def test_colours(self):
        """The wood the game's staves' (a lone colour three quarters up), the steel the material's by brightness (the darkest its
        darkest, the brightest its brightest), the gem the cycled green, the rest the nearest stable;
        the head's colours the steel's and the gold's."""
        rows = [[1, 2, 3, None], [4, 5, 6, 3]]
        out, head = sequelicons.in_shattered_lands(rows, THEIRS, "obsidian", self.STABLE)
        ramp = sequelicons.MATERIALS["obsidian"]
        self.assertEqual(out, [[lone(sequelicons.WOOD), ramp[0], ramp[-1], None],
                               [31, lone(icons.GREEN), 30, ramp[-1]]])
        self.assertEqual(head, tuple(sorted((ramp[0], ramp[-1], 31))))

    def test_magic_burns_the_head(self):
        """A +1's head every other pixel in the fire colours, the wood kept; a stronger one's all."""
        rows = [[2, 2, 1, 1]]
        half = sequelicons.look(rows, THEIRS, "metal", (icons.FIRE, True), self.STABLE)
        full = sequelicons.look(rows, THEIRS, "metal", (icons.FIRE, False), self.STABLE)
        self.assertIn(half[0][0], icons.FIRE)
        self.assertNotIn(half[0][1], icons.FIRE)
        self.assertTrue(all(p in icons.FIRE for p in full[0][:2]))
        self.assertEqual(full[0][2:], [lone(sequelicons.WOOD)] * 2)

    def test_great_sword_longer(self):
        """The sequel's great sword (its long sword's size) three steps longer."""
        rows = [[2 if x == y else None for x in range(15)] for y in range(15)]
        out = sequelicons.look(rows, THEIRS, "metal", None, self.STABLE, "great sword")
        self.assertEqual((len(out), len(out[0])), (18, 18))

    def test_every_name_an_icon(self):
        """Each of SEQUEL's names is one of ICONS', of one of PICTURES' kinds, its material known."""
        names = {name for name, *_ in icons.ICONS}
        for name, (kind, material, _) in sequelicons.SEQUEL.items():
            self.assertIn(name, names)
            self.assertIn(kind, sequelicons.PICTURES)
            self.assertIn(material, sequelicons.MATERIALS)


class ChunkTests(unittest.TestCase):
    """The pictures put in the Loader's SEGOBJEX.GFF (chunks)."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = self.tmp.name
        sl = {30: (0, 0, 0), 31: (255, 210, 30), 32: (200, 0, 200)}
        self.gpldata = os.path.join(self.dir, "GPLDATA.GFF")
        with open(self.gpldata, "wb") as f:
            f.write(build_gff({("PAL ", 1): palette(sl), ("PAL ", 2): palette(sl)}))
        self.sl = {("OJFF", sequelicons.GAME_GREAT_AXE): struct.pack("<8H", 0, 0, 0, 0, 0, 0, 2084, 0)}

    def tearDown(self):
        self.tmp.cleanup()

    def sequel(self):
        wotr = os.path.join(self.dir, "wotr")
        os.mkdir(wotr)
        resources = os.path.join(wotr, "RESOURCE.GFF")
        with open(resources, "wb") as f:
            f.write(build_gff({sequelicons.PALETTE: palette(THEIRS)}))
        pictures = {("BMP ", n): plan(20, 20, 4, [0, 1, 2, 3], [1, 2, 3] * 140) for n in sequelicons.PICTURES.values()}
        with open(os.path.join(wotr, wotrart.OBJECTS_FILE), "wb") as f:
            f.write(build_gff(pictures))
        return resources

    def test_without_the_sequel(self):
        self.assertEqual(sequelicons.chunks(None, self.sl, {}, self.gpldata), {})

    def test_with_the_sequel(self):
        """Each SEQUEL item's picture (ICONS' number), the game's Great Axe +3's (one of its own),
        and the item box's copies of those that are tall."""
        out = sequelicons.chunks(self.sequel(), self.sl, {}, self.gpldata)
        own = {icon for name, _, _, icon, _ in icons.ICONS if name in sequelicons.SEQUEL}
        axe = sequelicons.GAME_GREAT_AXE_PICTURE
        self.assertEqual({n for k, n in out if k == "BMP " and n < icons.BOX_SMALL}, own | {axe})
        for i, icon in enumerate(icons.BOX_TALL):
            if icon in own | {axe}:
                small = art.decode_frame(out[("BMP ", icons.BOX_SMALL + i)])[2]
                self.assertLessEqual(max(len(small), len(small[0])), icons.BOX_PICTURE)
        rows = art.decode_frame(out[("BMP ", axe)])[2]
        self.assertEqual((len(rows), len(rows[0])), (20, 20))
        # (its object pointed at it; the game's 2084, Soulcrusher's too, left as it is)
        self.assertEqual(struct.unpack_from("<H", out[("OJFF", sequelicons.GAME_GREAT_AXE)], icons.OJFF_ICON),
                         (axe,))
        self.assertNotIn(("BMP ", 2084), out)

    def test_unreadable_sequel(self):
        """An OBJEX.GFF without the pictures: nothing (ICONS' own kept)."""
        resources = self.sequel()
        with open(os.path.join(os.path.dirname(resources), wotrart.OBJECTS_FILE), "wb") as f:
            f.write(build_gff({("BMP ", 1): plan(1, 1, 4, [0, 1], [1])}))
        self.assertEqual(sequelicons.chunks(resources, self.sl, {}, self.gpldata), {})

    def test_every_tall_one_boxed(self):
        """The great axes' and darts' icons among BOX_TALL (the sequel's great axe 23 tall; the
        Loader's darts 17 wide), and those of every long staff."""
        for name in ("Great Axe", "Metal Great Axe", "Bone Great Axe", "Obsidian Great Axe", "Headsman",
                     "Darts", "Darts +1", "Double Spear", "Trikal"):
            icon = next(i for n, _, _, i, _ in icons.ICONS if n == name)
            self.assertIn(icon, icons.BOX_TALL, name)
        self.assertIn(sequelicons.GAME_GREAT_AXE_PICTURE, icons.BOX_TALL)


class DrawnTests(unittest.TestCase):
    """The Loader's own double spear, trikal and darts (without the sequel), drawn as the sequel's."""

    def test_sizes(self):
        self.assertEqual(len(icons.double_spear_icon()), icons.POLEARM_SIZE)
        self.assertEqual(len(icons.trikal_icon()), 33)
        darts = icons.darts_icon()
        self.assertEqual((len(darts), len(darts[0])), (16, 17))

    def test_heads_at_both_ends(self):
        rows = icons.double_spear_icon()
        self.assertEqual((rows[0][0], rows[-1][-1]), (214, 214))

    def test_magic_darts_burn_their_points(self):
        plus = next(make for n, _, _, _, make in icons.ICONS if n == "Darts +1")([])
        points = [p for row in plus for p in row if p is not None and p in icons.FIRE]
        self.assertEqual(len(points), 2 * sum(line.count("G") + line.count("g") for line in icons.DART))


if __name__ == "__main__":
    unittest.main()
