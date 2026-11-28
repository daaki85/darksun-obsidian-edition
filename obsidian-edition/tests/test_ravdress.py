"""The class outfits on the sequel's party (ravdress): Shattered Lands' scripts in the sequel's form, the
colours mapped, the party's pictures found, and the running game's copy rewritten in place with the
pictures taken out of the cache and the party's map things given no slot; with DSUN_SL and DSUN_WOTR the
copy's party pictures made from Shattered Lands' objects."""

import os
import struct
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dsloader import gff, icons, ravdress  # noqa: E402
from test_ravtransfer import _gff  # noqa: E402

SL = os.environ.get("DSUN_SL")
WOTR = os.environ.get("DSUN_WOTR")


def _script(slots, steps):
    return struct.pack("<36H", *(slots + [0] * (36 - len(slots)))) + b"".join(bytes(s) for s in steps)


class ScriptTests(unittest.TestCase):
    def test_empty_slots_and_flag(self):
        sl = _script([0, 1, 0, 2], [[1, 0, 0, 0, 0, 0, 0, 0], [2, 0, 0x20, 0, 0, 0, 0, 0]])
        flagged = _script([0], [[1, 0, 0x40, 0, 0, 0, 0, 0]])
        got = ravdress.wr_script(sl, flagged)
        slots = struct.unpack_from("<36H", got)
        self.assertEqual(slots[:4], (0, 1, 0xFFFF, 2))
        self.assertEqual(got[72 + 2], 0x40)
        self.assertEqual(got[80 + 2], 0x60)
        self.assertEqual(ravdress.wr_script(sl, _script([0], [[1, 0, 0, 0, 0, 0, 0, 0]]))[72:], sl[72:])


class SmallTests(unittest.TestCase):
    def test_first_frame(self):
        from dsloader import art, sprites
        pic = sprites.encode_frames([[[1, None], [2, 3]], [[4]]])
        one = ravdress.first_frame(pic)
        self.assertEqual(struct.unpack_from("<H", one, 4)[0], 1)
        self.assertEqual(art.decode_frame(one, 0)[2], [[1, None], [2, 3]])


class ColourTests(unittest.TestCase):
    def test_nearest_stable(self):
        palette = [(0, 0, 0)] * 256
        palette[5], palette[6] = (60, 0, 0), (0, 0, 60)
        colours = ravdress.Colours(palette, [(10, (63, 0, 0)), (11, (0, 0, 63))])
        self.assertEqual((colours(0), colours(5), colours(6)), (0, 10, 11))


class PicturesTests(unittest.TestCase):
    def test_party_pictures(self):
        rec = bytearray(16)
        struct.pack_into("<H", rec, ravdress.PICTURE, 599)
        got = ravdress.party_pictures({("OJFF", 300): bytes(rec), ("OJFF", 299): bytes(rec), ("OJFF", 301): b"x"})
        self.assertEqual(got, {300: 599})


class _Guest:
    def __init__(self):
        self.mem = bytearray(0x60000)

    def read(self, at, n):
        return bytes(self.mem[at:at + n])

    def write(self, at, data):
        self.mem[at:at + len(data)] = data


class _Game:
    ds, load_seg = 0x1000, 0

    def __init__(self, figures):
        self.guest = _Guest()
        self.figures = figures

    def creature(self, member):
        rec = bytearray(0x31)
        if member < len(self.figures):
            struct.pack_into("<H", rec, ravdress.CREATURE_FIGURE, self.figures[member])
            rec[0] = 1
        return bytes(rec)

    def sheet(self, member):
        return bytes([member])


class _Sources:
    def __init__(self):
        self.asked = []

    def role(self, obj, sheet):
        return ("fighter", "mage", "thief", "cleric")[sheet[0]]

    def pictures(self, obj, role=None):
        self.asked.append((obj, role))
        size = {"fighter": 30, "mage": 20}.get(role, 10)
        return bytes([1]) * size, bytes([2]) * size


class DresserTests(unittest.TestCase):
    def setUp(self):
        rec = bytearray(16)
        struct.pack_into("<H", rec, ravdress.PICTURE, 25)
        rec2 = bytearray(16)
        struct.pack_into("<H", rec2, ravdress.PICTURE, 599)
        base = _gff({("OJFF", 300): bytes(rec), ("OJFF", 305): bytes(rec2), ("BMP ", 1): b"x", ("CBMP", 1): b"y"})
        data = icons.with_chunks(base, {("BMP ", 25): b"a" * 10, ("CBMP", 25): b"b" * 10,
                                        ("BMP ", 599): b"c" * 10, ("CBMP", 599): b"d" * 10},
                                 {("BMP ", 25): 30, ("CBMP", 25): 30, ("BMP ", 599): 5, ("CBMP", 599): 5})
        fd, self.path = tempfile.mkstemp(suffix=".GFF")
        os.write(fd, data)
        os.close(fd)
        self.addCleanup(os.remove, self.path)

    def _game(self, figures):
        gd = _Game(figures)
        g, ds = gd.guest, gd.ds * 16
        cache = (gd.load_seg + ravdress.CACHE_SEG) * 16 + ravdress.CACHE_OFF
        g.write(ds + ravdress.CACHE_COUNT, struct.pack("<H", 3))
        for k, number in enumerate((7, 25, 25)):
            g.write(cache + k * ravdress.CACHE_ENTRY, struct.pack("<H", number))
        for n, picture in enumerate((25, 599)):
            at = ds + ravdress.THINGS + n * ravdress.THING_SIZE
            g.write(at + ravdress.THING_PICTURE, struct.pack("<H", picture))
            g.write(at + ravdress.THING_SLOT, struct.pack("<H", 4))
        return gd

    def test_dressed_in_place(self):
        gd = self._game([0, 5, 0])
        sources = _Sources()
        dresser = ravdress.RavDresser(gd, sources, self.path)
        # (the second member with figure 0 is not drawn; figure 5's mage picture has no room, so it stays)
        self.assertEqual(dresser.update(), [300])
        self.assertEqual(sources.asked, [(300, "fighter"), (305, "mage")])
        with open(self.path, "rb") as f:
            got = gff.read_gff(f.read())
        self.assertEqual(got[("BMP ", 25)], bytes([1]) * 30)
        self.assertEqual(got[("CBMP", 25)], bytes([2]) * 30)
        self.assertEqual(got[("BMP ", 599)], b"c" * 10)
        g, ds = gd.guest, gd.ds * 16
        cache = (gd.load_seg + ravdress.CACHE_SEG) * 16 + ravdress.CACHE_OFF
        numbers = [struct.unpack("<H", g.read(cache + k * 16, 2))[0] for k in range(3)]
        self.assertEqual(numbers, [7, ravdress.STALE, ravdress.STALE])
        slots = [struct.unpack("<H", g.read(ds + ravdress.THINGS + n * ravdress.THING_SIZE + ravdress.THING_SLOT,
                                            2))[0] for n in range(2)]
        self.assertEqual(slots, [0xFFFF, 4])
        # (nothing changed: nothing written again)
        self.assertEqual(dresser.update(), [])

    def test_a_reconnect_loads_nothing_anew(self):
        """A new RavDresser (the dice log connected again) finding the copy already dressed so: nothing written
        and no cache slot made stale, as Shattered Lands' Dresser (_same_in_copy)."""
        gd = self._game([0])
        self.assertEqual(ravdress.RavDresser(gd, _Sources(), self.path).update(), [300])
        gd2 = self._game([0])
        with open(self.path, "rb") as f:
            before = f.read()
        self.assertEqual(ravdress.RavDresser(gd2, _Sources(), self.path).update(), [])
        with open(self.path, "rb") as f:
            self.assertEqual(f.read(), before)
        cache = (gd2.load_seg + ravdress.CACHE_SEG) * 16 + ravdress.CACHE_OFF
        self.assertEqual(struct.unpack("<H", gd2.guest.read(cache + ravdress.CACHE_ENTRY, 2))[0], 25)

    def test_no_copy(self):
        dresser = ravdress.RavDresser(self._game([0]), _Sources(), self.path + ".none")
        self.assertEqual(dresser.update(), [])

    def test_writable_covers_writes(self):
        gd = self._game([0])
        spans = ravdress.RavDresser(gd, _Sources(), self.path).writable()
        cache = (gd.load_seg + ravdress.CACHE_SEG) * 16 + ravdress.CACHE_OFF
        self.assertIn((cache, ravdress.CACHE_MOST * ravdress.CACHE_ENTRY), spans)


@unittest.skipUnless(SL and WOTR, "needs DSUN_SL and DSUN_WOTR")
class FilesTests(unittest.TestCase):
    def test_copy_chunks(self):
        from dsloader import art, ravager
        sources = ravdress.Sources.from_files(SL, WOTR)
        self.assertIsNotNone(sources)
        with open(art._find(WOTR, ravager.OBJECTS_FILE), "rb") as f:
            objects = gff.read_gff(f.read())
        chunks, room = ravdress.copy_chunks(objects, sources)
        pictures = set(ravdress.party_pictures(objects).values())
        self.assertTrue(pictures)
        for n in pictures:
            for kind in ("BMP ", "CBMP", "SCMD"):
                self.assertIn((kind, n), chunks)
            self.assertGreater(room[("BMP ", n)], 0)
        small = [k for k in chunks if k[0] == "BMP " and k[1] >= ravdress.SMALL_BASE]
        self.assertEqual(len(small), 290)  # (every outfit: 13 figures' class combinations)
        self.assertIn(("BMP ", ravdress.SMALL_BASE + 0x04), chunks)  # (the human man fighter: group 3)
        for key in small:
            self.assertEqual(struct.unpack_from("<H", chunks[key], 4)[0], 1)  # (frame 0 alone)


if __name__ == "__main__":
    unittest.main()
