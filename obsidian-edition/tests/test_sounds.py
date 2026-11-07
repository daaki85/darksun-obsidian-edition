"""The mod's sounds (sounds.py): RESOURCE.GFF's BVOC chunks in the game's own form, under numbers
the game leaves free, and the Loader asking DSCLOG for them (the hiding's, a picked pocket's)."""

import os
import struct
import unittest
import wave

from dsloader import gff, gpl, sounds

GPLDATA = os.environ.get("DSUN_GPLDATA")
RESOURCE = os.path.join(os.path.dirname(GPLDATA), "RESOURCE.GFF") if GPLDATA else None


class ChunkTests(unittest.TestCase):

    def test_two_sounds(self):
        chunks = sounds.chunks()
        self.assertEqual(set(chunks), {("BVOC", sounds.HIDE_SOUND), ("BVOC", sounds.PICK_SOUND)})
        for (_, number), data in chunks.items():
            self.assertTrue(data.startswith(b"Creative Voice File\x1a"))
            self.assertEqual(struct.unpack_from("<HHH", data, 20), (26, 0x010A, 0x1129))
            size = data[27] | data[28] << 8 | data[29] << 16
            self.assertEqual((data[26], data[30], data[31]), (1, 0x83, 0))  # (8000 a second, 8-bit)
            self.assertEqual(len(data), 26 + 4 + size + 1)
            self.assertEqual(data[-1], 0)
            self.assertLess(len(data), sounds.MOST)
            self.assertLess(number, 255)  # (the game's routine takes a byte; FFh plays nothing)

    def test_samples_are_the_files(self):
        with wave.open(os.path.join(sounds.FOLDER, "hide.wav"), "rb") as w:
            samples = w.readframes(w.getnframes())
        self.assertEqual(sounds.chunks()[("BVOC", sounds.HIDE_SOUND)][32:-1], samples)

    def test_other_kinds_left_out(self):
        import tempfile
        with tempfile.TemporaryDirectory() as folder:
            with wave.open(os.path.join(folder, "x.wav"), "wb") as w:
                w.setnchannels(2), w.setsampwidth(1), w.setframerate(8000), w.writeframes(b"\x80" * 8)
            with self.assertRaises(ValueError):
                sounds.read_wav(os.path.join(folder, "x.wav"))


@unittest.skipUnless(RESOURCE and os.path.exists(RESOURCE), "DSUN_GPLDATA (the game's files) not given")
class GameTests(unittest.TestCase):

    def test_like_the_games(self):
        """The game's own sounds have the same header and blocks (its BVOC 53, the quest's)."""
        with open(RESOURCE, "rb") as f:
            chunks = gff.read_gff(f.read())
        own = chunks[("BVOC", 53)]
        mine = sounds.chunks()[("BVOC", sounds.PICK_SOUND)]
        self.assertEqual(own[:26], mine[:26])
        self.assertEqual((own[26], own[30], own[31], own[-1]), (mine[26], mine[30], mine[31], mine[-1]))
        numbers = {n for k, n in chunks if k == "BVOC"}
        self.assertTrue(numbers.isdisjoint({sounds.HIDE_SOUND, sounds.PICK_SOUND}))
        self.assertLess(max(numbers), sounds.HIDE_SOUND)

    def test_no_script_plays_them(self):
        with open(GPLDATA, "rb") as f:
            scripts, types = gpl.load_scripts(f.read())
        played = set()
        for data in scripts.values():
            try:
                ops = gpl.decode(data, types)
            except (ValueError, IndexError, struct.error):
                continue
            played |= {op.args[0][1] for op in ops if op.code == 0x5D and op.args and op.args[0][0] == "n"}
        self.assertTrue(played)
        self.assertTrue(played.isdisjoint({sounds.HIDE_SOUND, sounds.PICK_SOUND}))


if __name__ == "__main__":
    unittest.main()
