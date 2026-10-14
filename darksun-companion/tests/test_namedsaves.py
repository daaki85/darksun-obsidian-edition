"""The saves kept under their names in the game (namedsaves.py)."""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dscompanion import namedsaves
from test_core import build_gff


def save(name: str) -> bytes:
    """A save as the game writes one: its name in STXT 1 (the rest of the 45 bytes old text)."""
    text = name.encode("cp437") + b"\0ded game\0s"
    return build_gff({("SAVE", 1): b"party", ("STXT", 1): text.ljust(45, b"\0")})


class NamedSavesTests(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.game = os.path.join(self.tmp.name, "game")
        self.named = os.path.join(self.tmp.name, "Named saves")
        os.makedirs(self.game)

    def tearDown(self):
        self.tmp.cleanup()

    def put(self, folder: str, file: str, data: bytes, stamp: float) -> None:
        path = os.path.join(folder, file)
        with open(path, "wb") as f:
            f.write(data)
        os.utime(path, (stamp, stamp))

    def test_name(self):
        self.assertEqual(namedsaves.save_name(save("Before Scar's battle")), "Before Scar's battle")
        self.assertIsNone(namedsaves.save_name(b"not a save"))

    def test_slot_files(self):
        self.assertEqual(namedsaves.slot_file(1, 10), "SAVE10.SAV")
        self.assertEqual(namedsaves.slot_file(2, 1), "SAVB01.SAV")
        self.assertEqual(namedsaves.slot_file(4, 5), "SAVD05.SAV")

    def test_copy_name(self):
        self.assertEqual(namedsaves.copy_name(2, 5, 'Is it "done"? a/b'), 'Page 2 slot 05 - Is it _done__ a_b.SAV')
        self.assertEqual(namedsaves.copy_name(1, 1, ""), "Page 1 slot 01 - no name.SAV")

    def test_sync(self):
        self.put(self.game, "SAVE01.SAV", save("Pens"), 1000)
        self.put(self.game, "SAVD02.SAV", save("Before Dinos"), 1000)
        made = namedsaves.sync(self.game, self.named)
        self.assertEqual(sorted(made), ["Page 1 slot 01 - Pens.SAV", "Page 4 slot 02 - Before Dinos.SAV"])
        with open(os.path.join(self.named, "Page 4 slot 02 - Before Dinos.SAV"), "rb") as f:
            self.assertEqual(f.read(), save("Before Dinos"))
        self.assertEqual(namedsaves.sync(self.game, self.named), [])  # (nothing new)

    def test_slot_saved_over(self):
        """A slot saved over: its copy under the old name goes, the new one comes."""
        self.put(self.game, "SAVE01.SAV", save("Pens"), 1000)
        namedsaves.sync(self.game, self.named)
        self.put(self.game, "SAVE01.SAV", save("Arena"), 2000)
        self.assertEqual(namedsaves.sync(self.game, self.named), ["Page 1 slot 01 - Arena.SAV"])
        self.assertEqual(os.listdir(self.named), ["Page 1 slot 01 - Arena.SAV"])

    def test_cloud_saves_first(self):
        """GOG's cloud_saves (mounted over the folder) before the game folder's own."""
        cloud = os.path.join(self.game, "cloud_saves")
        os.makedirs(cloud)
        self.put(self.game, "SAVE01.SAV", save("Old"), 1000)
        self.put(cloud, "SAVE01.SAV", save("New"), 1000)
        self.put(self.game, "SAVE02.SAV", save("Only here"), 1000)
        self.assertEqual(sorted(namedsaves.sync(self.game, self.named)),
                         ["Page 1 slot 01 - New.SAV", "Page 1 slot 02 - Only here.SAV"])

    def test_restore(self):
        copy = os.path.join(self.tmp.name, "Page 2 slot 05 - Trustee.SAV")
        self.put(self.tmp.name, os.path.basename(copy), save("Trustee"), 1000)
        self.assertIsNone(namedsaves.slot_name(self.game, 3, 7))
        self.assertEqual(namedsaves.restore(copy, self.game, 3, 7), "Trustee")
        self.assertEqual(namedsaves.slot_name(self.game, 3, 7), "Trustee")
        bad = os.path.join(self.tmp.name, "x.SAV")
        self.put(self.tmp.name, "x.SAV", b"nothing", 1000)
        with self.assertRaises(ValueError):
            namedsaves.restore(bad, self.game, 1, 1)


if __name__ == "__main__":
    unittest.main()
