"""The sequel's still magic items made to shine (ravshine): a picture's pixels in a cycled run, every other one;
with DSUN_WOTR the sequel's own OBJEX.GFF: each SHINE object an item with a plus or a power, its icon its own and
without cycled pixels in what SHINE takes, and the Loader's copy with them shining."""

import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import dataitems, gff, icons, ravager, ravshine, sequelicons  # noqa: E402

WOTR = os.environ.get("DSUN_WOTR")


def objects(rows):
    """A GFF's chunks with object 675's icon 2326 ROWS (Shattered Lands' kind of picture)."""
    rec = bytearray(16)
    struct.pack_into("<H", rec, icons.OJFF_ICON, 2326)
    return {("OJFF", 675): bytes(rec), ("BMP ", 2326): icons.encode(rows)}


class ShineTests(unittest.TestCase):
    def test_every_other_pixel_in_the_run(self):
        rows = [[None, 232, 241, 50], [232, 241, 50, None]]
        out = ravshine.chunks(objects(rows))
        got = sequelicons.decode(out[("BMP ", 2326)])
        for y, row in enumerate(rows):
            for x, p in enumerate(row):
                if p in (232, 241) and (x + y) % 2 == 0:
                    self.assertIn(got[y][x], ravshine.FIRE)
                else:
                    self.assertEqual(got[y][x], p)

    def test_another_picture_left(self):
        """An icon with none of SHINE's colours (another release's) is left as it is; so is a missing object."""
        self.assertEqual(ravshine.chunks(objects([[50, 51]])), {})
        self.assertEqual(ravshine.chunks({}), {})

    def test_runs(self):
        runs = (ravshine.BLUE, ravshine.VIOLET, ravshine.GREEN, ravshine.FIRE, ravshine.WATER)
        self.assertEqual(sorted(c for r in runs for c in r), list(range(1, 32)))
        self.assertTrue(all(s.run in runs for s in ravshine.SHINE))


@unittest.skipUnless(WOTR, "DSUN_WOTR: the player's Wake of the Ravager")
class GameTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = open(os.path.join(WOTR, ravager.OBJECTS_FILE), "rb").read()
        cls.chunks = gff.read_gff(cls.data)

    def test_still_magic_items(self):
        icon_users = {}
        for (kind, n), rec in self.chunks.items():
            if kind == "OJFF":
                icon_users.setdefault(struct.unpack_from("<H", rec, icons.OJFF_ICON)[0], []).append(n)
        magic = set()
        for (kind, n), data in self.chunks.items():
            if kind != "RDFF":
                continue
            try:
                recs, _ = dataitems.records(data)
            except ValueError:
                continue
            for r in recs:
                if len(r.data) >= 23 and (r.data[0x16] or struct.unpack_from("<H", r.data, 0x10)[0]):
                    magic.add(-struct.unpack_from("<h", r.data, 0)[0])
        for s in ravshine.SHINE:
            icon = ravshine.icon_of(self.chunks, s.obj)
            self.assertIsNotNone(icon, s.name)
            self.assertEqual(icon_users[icon], [s.obj], s.name)  # (its own: no other object changes with it)
            self.assertIn(s.obj, magic, s.name)
            rows = sequelicons.decode(self.chunks[("BMP ", icon)])
            self.assertLessEqual(sum(1 for r in rows for p in r if p in ravshine.CYCLED), 2, s.name)

    def test_the_copy(self):
        copy, done = ravager.objects_fixed(self.data)
        self.assertIn("item_shine", done)
        out = gff.read_gff(copy)
        for s in ravshine.SHINE:
            rows = sequelicons.decode(out[("BMP ", ravshine.icon_of(out, s.obj))])
            self.assertGreaterEqual(sum(1 for r in rows for p in r if p in s.run), 3, s.name)
        _, done = ravager.objects_fixed(self.data, frozenset({"item_shine"}))
        self.assertNotIn("item_shine", done)


if __name__ == "__main__":
    unittest.main()
