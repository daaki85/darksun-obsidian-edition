"""The robes (robes.py)."""

import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import game, kits, restrict, robes


class RobesTests(unittest.TestCase):
    def test_items(self):
        for name, plus, value in ((robes.ASHEN, 1, 6000), (robes.VEILED, 2, 40000)):
            rec = robes.item(name)
            self.assertEqual(struct.unpack_from("<H", rec, game.ITEM_TYPE)[0], game.ROBE_TYPE)
            self.assertEqual(struct.unpack_from("<H", rec, game.ITEM_NAME)[0], name)
            self.assertEqual(rec[game.ITEM_PLUS], plus)
            self.assertEqual(struct.unpack_from("<H", rec, 6)[0], value)

    def test_saves(self):
        self.assertEqual([robes.save(2, s) for s in (0, 137, 200, 0xFFFF)], [1, 1, 1, 1])
        self.assertEqual([robes.save(1, s) for s in (0, 137, 138, 200)], [1, 1, 0, 0])
        self.assertEqual(robes.save(0, 10), 0)

    def test_slots(self):
        self.assertEqual([robes.slots(2, kits.WIZARD, level, 3) for level in range(1, 6)], [4, 4, 4, 3, 3])
        self.assertEqual(robes.slots(2, kits.WIZARD, 2, 0), 0)  # (none at that level: none more)
        self.assertEqual(robes.slots(2, kits.PRIEST, 1, 3), 3)
        self.assertEqual(robes.slots(1, kits.WIZARD, 1, 3), 3)

    def test_worn(self):
        rec = bytearray(robes.item(robes.VEILED))
        rec[game.ITEM_SLOT] = robes.CHEST_SLOT
        self.assertEqual(robes.worn_plus([(0, bytes(rec), b"")]), 2)
        rec[game.ITEM_SLOT] = 20  # (in the backpack)
        self.assertEqual(robes.worn_plus([(0, bytes(rec), b"")]), 0)

    def test_not_armour(self):
        """The type as DSCLOG has it (its EXTRA_TYPES): worn on the chest, counting for AC, but
        not armour; for preservers, psionicists and druids."""
        typ = bytes.fromhex("00000000" "0a000a00" "40010000" "00000080" "90010001")
        self.assertTrue(restrict.is_robe(typ))
        self.assertFalse(restrict.is_armour(typ))
        silk = bytearray(typ)
        silk[0x10:0x12] = (0x176F).to_bytes(2, "little")
        self.assertTrue(restrict.is_armour(bytes(silk)))


if __name__ == "__main__":
    unittest.main()
