"""The rest of the bone scale armour, in the slave pens' chest with its chest piece (the
objects' data: worldgear.data_chunks)."""

import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import bonescale, game, icons


class BoneScaleTests(unittest.TestCase):
    def test_pieces(self):
        """The game's arm and leg pieces, and a Bone Helm of the Loader's type; each tells
        which it is."""
        self.assertEqual([bonescale.which_piece(p) for p in bonescale.PIECES], list(bonescale.PIECES))
        self.assertEqual(struct.unpack_from("<H", bonescale.HELM, game.ITEM_TYPE)[0], game.BONE_HELM_TYPE)
        self.assertEqual(bonescale.CHEST_OBJECT, 1564)

    def test_helm_icon(self):
        self.assertEqual(icons.which(bonescale.HELM), "Bone Helm")
        self.assertEqual(icons.recolour([[129, 140, None, 208]], icons.BONE), [[207, 61, None, 208]])


if __name__ == "__main__":
    unittest.main()
