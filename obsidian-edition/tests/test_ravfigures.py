"""The sequel's redrawn figures (ravfigures): the Loader's file of them read whole, every drawing decoded and
every script step on a drawing its picture has, Notaku's combat drawings with no box round them, the moved
objects; a file not the game's left as it is; with DSUN_WOTR the sequel's own files, every chunk the figures
replace there (ravager's copies: test_ravager's test_copy_made)."""

import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import art, gff, ravfigures  # noqa: E402

WOTR = os.environ.get("DSUN_WOTR")
COMBAT = 0x20  # (a script step's flag: a drawing of the combat picture, CBMP)
SLOTS, STEP = 36, 8  # (SCMD: 36 words, the step each animation starts at, then 8-byte steps)


def frame_count(chunk):
    return struct.unpack_from("<H", chunk, 4)[0]


def drawn(chunk, i):
    """True if frame I is the run-length kind art.decode_frame reads (the cinematic's packed and planar frames aren't)."""
    off, = struct.unpack_from("<I", chunk, 6 + 4 * i)
    return chunk[off + 4:off + 9] not in (b"\xffPLNR", b"\xffPLAN")


class FigureFileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = ravfigures.load()

    def test_the_files_and_their_counts(self):
        files = self.data["files"]
        self.assertEqual(set(files), set(ravfigures.FILES))
        self.assertEqual(len(self.data["objects"]), 32)
        self.assertEqual(set(files["RGN03A.GFF"]), {("ETAB", 58)})
        self.assertEqual({k[1] for k in files["RESOURCE.GFF"]}, {11001, 11002, 11005, 11006, 11007, 11012, 11013, 11014})
        pictures = {k[1] for k in files["OBJEX.GFF"] if k[0] == "BMP "}
        self.assertGreaterEqual(len(pictures), 260)
        self.assertTrue(self.data["source"])

    def test_every_drawing_decodes_and_every_step_has_its_drawing(self):
        for name in ("OBJEX.GFF", "RESOURCE.GFF"):
            chunks = self.data["files"][name]
            for (kind, pic), chunk in chunks.items():
                if kind in ("BMP ", "CBMP"):
                    for i in range(frame_count(chunk)):
                        if drawn(chunk, i):
                            w, h, rows = art.decode_frame(chunk, i)
                            self.assertEqual((len(rows), len(rows[0]) if rows else 0), (h, w), (name, kind, pic, i))
                if kind == "SCMD":
                    steps = [struct.unpack_from("<BBBBHBB", chunk, 2 * SLOTS + STEP * k)
                             for k in range((len(chunk) - 2 * SLOTS) // STEP)]
                    for k, st in enumerate(steps):  # (a bank the figures leave is the game's: GameFileTests)
                        bank = ("CBMP" if st[2] & COMBAT else "BMP ", pic)
                        if bank in chunks:
                            self.assertLess(st[0], frame_count(chunks[bank]), (name, pic, k))

    def test_notaku_fights_with_no_box(self):
        chunk = self.data["files"]["OBJEX.GFF"][("CBMP", 2409)]
        for i in range(frame_count(chunk)):
            w, h, rows = art.decode_frame(chunk, i)
            edge = [rows[y][x] for x in range(w) for y in (0, h - 1)] + [rows[y][x] for y in range(h) for x in (0, w - 1)]
            self.assertLess(sum(c is not None for c in edge) * 5, len(edge), i)  # (his feet and weapon may touch it)

    def test_objects_moved_only_from_the_games_picture(self):
        obj, old, new = self.data["objects"][0]
        rec = bytearray(16)
        game = {k: b"x" for k in self.data["files"]["OBJEX.GFF"] if k not in self.data["added"]["OBJEX.GFF"]}
        struct.pack_into("<H", rec, ravfigures.PICTURE, old)
        out = ravfigures.object_chunks({**game, ("OJFF", obj): bytes(rec)}, self.data)
        self.assertEqual(struct.unpack_from("<H", out[("OJFF", obj)], ravfigures.PICTURE)[0], new)
        struct.pack_into("<H", rec, ravfigures.PICTURE, old + 1)  # (another picture: the object left)
        out = ravfigures.object_chunks({**game, ("OJFF", obj): bytes(rec)}, self.data)
        self.assertNotIn(("OJFF", obj), out)

    def test_a_file_not_the_games_left_alone(self):
        self.assertEqual(ravfigures.object_chunks({("BMP ", 25): b"x"}, self.data), {})
        self.assertEqual(ravfigures.resource_chunks({}, self.data), {})
        self.assertEqual(ravfigures.region_chunks("RGN03A.GFF", {}, self.data), {})

    def test_cleared_edges(self):
        from dsloader import sprites
        rows = [[5, 5, 5, 5], [5, 1, 5, 5], [5, 2, 3, 5], [5, 5, 5, 5]]
        out = ravfigures.cleared_edges(sprites.encode_frames([rows]))
        self.assertEqual(art.decode_frame(out, 0)[2],
                         [[None] * 4, [None, 1, None, None], [None, 2, 3, None], [None] * 4])


@unittest.skipUnless(WOTR, "DSUN_WOTR: the sequel's folder")
class GameFileTests(unittest.TestCase):
    def test_every_replaced_chunk_is_the_games(self):
        data = ravfigures.load()
        for name in ravfigures.FILES:
            with open(os.path.join(WOTR, name), "rb") as f:
                own = gff.read_gff(f.read())
            added = data["added"].get(name, set())
            for k in data["files"][name]:
                self.assertEqual(k in own, k not in added, (name, k))
        with open(os.path.join(WOTR, "OBJEX.GFF"), "rb") as f:
            own = gff.read_gff(f.read())
        made = ravfigures.object_chunks(own, data)
        self.assertEqual(sum(k[0] == "OJFF" for k in made), 32)
        merged = {**own, **made}
        bad = []
        for (kind, pic), script in merged.items():  # (every step of a script the figures bring, on a drawing there is)
            if kind != "SCMD" or ("SCMD", pic) not in made:
                continue
            for k in range((len(script) - 2 * SLOTS) // STEP):
                st = struct.unpack_from("<BBBBHBB", script, 2 * SLOTS + STEP * k)
                bank = merged.get(("CBMP" if st[2] & COMBAT else "BMP ", pic))
                if bank is None or st[0] >= frame_count(bank):
                    bad.append((pic, k))
        self.assertEqual(bad, [])


if __name__ == "__main__":
    unittest.main()
