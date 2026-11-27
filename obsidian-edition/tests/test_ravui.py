"""Shattered Lands' interface in the sequel (ravui): the pictures and icons wanted, the colour table's targets, a
chunk put in only where the Loader's copy still has the game's own, the MORE and scroll buttons kept; with
DSUN_SL and DSUN_WOTR the player's files: every picture and icon made, each decoding, in the colours every
region keeps, and the Loader's RESOURC2.GFF holding them after the mod's own chunks."""

import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import art, gff, icons, ravager, ravui  # noqa: E402

SL = os.environ.get("DSUN_SL")
WOTR = os.environ.get("DSUN_WOTR")


def palette(colours):
    """A PAL chunk (6 bits a channel) of COLOURS (256 RGB, 0-63 each)."""
    return bytes(v for rgb in colours for v in rgb)


class TableTests(unittest.TestCase):
    def test_the_pictures_and_icons_wanted(self):
        wanted = ravui.wanted()
        self.assertEqual(len(ravui.PICTURES), 45)
        self.assertEqual(len(ravui.ICONS), 221)
        self.assertEqual(sum(w != s for w, s in ravui.ICONS.items()), 130)
        self.assertEqual(len(wanted), 266)
        self.assertFalse(set(ravui.ICON_KEEP) & set(ravui.ICONS))

    def test_the_colour_table_never_takes_a_cycled_or_system_colour(self):
        stable = [(c, (c, c, c)) for c in range(1, 256)]
        table = ravui.colour_table([(c, c, c) for c in range(256)], stable)
        self.assertEqual(len(table), 256)
        self.assertFalse(set(table.values()) & ravui.KEPT)
        self.assertEqual(table[100], 100)
        self.assertEqual(table[5], 32)  # (the nearest that isn't cycled)
        with self.assertRaises(ValueError):
            ravui.colour_table([(0, 0, 0)] * 256, [(c, (0, 0, 0)) for c in range(1, 32)])


class SwitchTests(unittest.TestCase):
    def test_the_options_box_leaves_it_out_only_when_unticked(self):
        self.assertNotIn(ravui.SKIP, ravager.skipped({}))
        self.assertNotIn(ravui.SKIP, ravager.skipped({ravui.SETTING: True}))
        self.assertIn(ravui.SKIP, ravager.skipped({ravui.SETTING: False}))


class MadeTests(unittest.TestCase):
    def setUp(self):
        grey = [(c // 4, c // 4, c // 4) for c in range(256)]
        self.region = palette(grey)
        sl_pal = list(grey)
        sl_pal[7] = (0, 0, 63)  # (Shattered Lands' colour 7 a blue the sequel has at 200)
        seq_pal = list(grey)
        seq_pal[200] = (0, 0, 63)
        self.sequel = {ravui.PALETTE: palette(seq_pal), ("BMP ", 10000): icons.encode([[1, 2]]),
                       ("ICON", 18101): icons.encode([[3]]), ("ICON", 12100): icons.encode([[4]]),
                       ("ICON", 2002): icons.encode([[5]])}
        self.sl = {ravui.PALETTE: palette(sl_pal), ("BMP ", 10000): icons.encode([[7, 7]]),
                   ("ICON", 6030): icons.encode([[7]]), ("ICON", 12100): icons.encode([[7]])}
        regions = [palette(seq_pal)] * 2
        self.made = ravui.made(self.sequel, self.sl, regions)

    def test_pictures_and_icons_by_their_pairs_recoloured(self):
        self.assertEqual(set(self.made), {("BMP ", 10000), ("ICON", 18101)})
        self.assertEqual(art.decode_frame(self.made[("BMP ", 10000)], 0)[2], [[200, 200]])
        self.assertEqual(art.decode_frame(self.made[("ICON", 18101)], 0)[2], [[200]])

    def test_the_buttons_kept_and_an_icon_shattered_lands_lacks_left(self):
        self.assertNotIn(("ICON", 12100), self.made)
        self.assertNotIn(("ICON", 2002), self.made)

    def test_a_chunk_the_loader_changed_stays_the_mods(self):
        stock = dict(self.sequel)
        changed = {**self.sequel, ("ICON", 18101): icons.encode([[9]])}
        made = ravui.made(changed, self.sl, [self.region], stock)
        self.assertNotIn(("ICON", 18101), made)
        self.assertIn(("BMP ", 10000), made)

    def test_no_files_no_chunks(self):
        self.assertEqual(ravui.chunks(self.sequel, None, "/nowhere"), {})
        self.assertEqual(ravui.chunks(self.sequel, "/nowhere", None), {})
        self.assertEqual(ravui.chunks(self.sequel, "/nowhere", "/nowhere"), {})


@unittest.skipUnless(SL and WOTR, "DSUN_SL and DSUN_WOTR: the player's two games' folders")
class GameFileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(ravager._find_file(WOTR, ravager.RESOURCE_FILE), "rb") as f:
            cls.data = f.read()
        cls.stock = gff.read_gff(cls.data)
        cls.made = ravui.chunks(cls.stock, SL, WOTR)

    def test_every_picture_and_icon_made_and_decoding(self):
        self.assertEqual(len(self.made), 266)
        for key, chunk in self.made.items():
            for i in range(struct.unpack_from("<H", chunk, 4)[0]):
                w, h, rows = art.decode_frame(chunk, i)
                self.assertEqual(len(rows), h, key)

    def test_in_the_colours_every_region_keeps(self):
        from dsloader import ravitems
        stable = {c for c, _ in ravitems.stable_colours(self.stock, ravui.region_palettes(WOTR))} - ravui.KEPT
        for key, chunk in self.made.items():
            for i in range(struct.unpack_from("<H", chunk, 4)[0]):
                used = {p for row in art.decode_frame(chunk, i)[2] for p in row if p is not None}
                self.assertLessEqual(used, stable, key)

    def test_the_loaders_copy_holds_them_after_the_mods_own(self):
        out, done = ravager.resources_fixed(self.data, frozenset(), None, SL, WOTR)
        self.assertEqual(done[-1], ravui.SKIP)
        copy = gff.read_gff(out)
        for key, chunk in self.made.items():
            self.assertEqual(copy[key], chunk, key)
        off, done_off = ravager.resources_fixed(self.data, frozenset({ravui.SKIP}), None, SL, WOTR)
        self.assertNotIn(ravui.SKIP, done_off)
        self.assertEqual(gff.read_gff(off)[("BMP ", 10000)], self.stock[("BMP ", 10000)])


if __name__ == "__main__":
    unittest.main()
