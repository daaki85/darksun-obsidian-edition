"""quiver.py: the arrows a party archer has left floating over it after a shot."""

import struct
import unittest

from dsloader import game, quiver, weaponchoice

ARROWS, STONES = 62, 63


def stack(slot: int, count: int, kind: int = ARROWS, name: int = 0x36, plus: int = 0) -> bytearray:
    rec = bytearray(game.ITEM_SIZE)
    struct.pack_into("<H", rec, weaponchoice.ITEM_COUNT, count)
    struct.pack_into("<H", rec, game.ITEM_TYPE, kind)
    struct.pack_into("<H", rec, game.ITEM_NAME, name)
    rec[game.ITEM_PLUS] = plus
    rec[game.ITEM_SLOT] = slot
    return rec


BOW = stack(weaponchoice.MISSILE_SLOT, 0, kind=1, name=1)


class FakeGd:
    """A member's items by number, and the counts written."""

    def __init__(self, items):
        self.items = dict(items)

    def _worn(self, member):
        return [(index, bytes(rec), b"") for index, rec in self.items.items()]

    def creature_name(self, member):
        return "Ester"

    def item_type_record(self, rec):
        return b""

    def item_label(self, rec, typ):
        return "Wooden Arrows" if struct.unpack_from("<H", rec, game.ITEM_TYPE)[0] == ARROWS else "Sling Stones"


class LabelTests(unittest.TestCase):
    def test_left(self):
        """What the quiver holds, after a shot (the pack's arrows aren't counted: they can't be shot
        until readied); "Out of arrows" at none, the kind named by the stack last shot from when the
        game has taken the quiver's away."""
        gd = FakeGd({10: BOW, 18: stack(weaponchoice.AMMO_SLOT, 17), 30: stack(20, 68)})
        self.assertEqual(quiver.left_label(gd, 2), "Arrows: 17 left")
        gd = FakeGd({10: BOW, 18: stack(weaponchoice.AMMO_SLOT, 0)})
        self.assertEqual(quiver.left_label(gd, 2), "Out of arrows")
        gd = FakeGd({10: BOW})
        self.assertEqual(quiver.left_label(gd, 2, bytes(stack(weaponchoice.AMMO_SLOT, 0))), "Out of arrows")
        self.assertEqual(quiver.left_label(gd, 2, bytes(stack(weaponchoice.AMMO_SLOT, 0, kind=STONES))), "Out of stones")
        self.assertIsNone(quiver.left_label(FakeGd({18: stack(weaponchoice.AMMO_SLOT, 3)}), 2))  # (no bow)
        self.assertIsNone(quiver.left_label(gd, 7))  # (a monster)


if __name__ == "__main__":
    unittest.main()
