"""quiver.py: a party archer's quiver topped up from its pack as its turn starts in a fight, and
the arrows it has left floating over it after a shot."""

import struct
import unittest
from unittest import mock

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


def run_top_up(gd, member=2):
    removed = []

    def write(gd_, index, n):
        struct.pack_into("<H", gd.items[index], weaponchoice.ITEM_COUNT, n)

    with mock.patch.object(quiver, "_set_count", write), \
            mock.patch.object(quiver.ring, "unlink", lambda gd_, it, index, what, empty=False: removed.append(index) or True), \
            mock.patch.object(quiver.ring, "Items", lambda gd_: None):
        lines = quiver.top_up(gd, member)
    for index in removed:
        del gd.items[index]
    return lines, removed


def counts(gd):
    return {index: quiver.count(rec) for index, rec in gd.items.items()}


class TopUpTests(unittest.TestCase):
    def test_from_the_pack(self):
        """A quiver under TOP_UP_UNDER takes from the pack's stacks of its kind up to TOP_UP_TO; a
        stack emptied so is taken away; another kind (sling stones, a spell's arrows: another name,
        or another plus) is left."""
        gd = FakeGd({10: BOW, 18: stack(weaponchoice.AMMO_SLOT, 1), 30: stack(20, 12), 31: stack(21, 40),
                     32: stack(22, 50, kind=STONES), 33: stack(23, 50, name=0x16C), 34: stack(24, 50, plus=1)})
        lines, removed = run_top_up(gd)
        self.assertEqual(removed, [30])
        self.assertEqual(counts(gd), {10: 0, 18: 20, 31: 33, 32: 50, 33: 50, 34: 50})
        self.assertEqual(lines, ["Ester fills the quiver from the pack: +19, 20 Wooden Arrows ready"])

    def test_left_alone(self):
        """No top-up with TOP_UP_UNDER or more in the quiver, with the quiver empty (the game took
        the stack: one put there in a fight isn't shot), with nothing of its kind in the pack, for a
        member with no missile weapon, or for a monster."""
        cases = ({10: BOW, 18: stack(weaponchoice.AMMO_SLOT, quiver.TOP_UP_UNDER), 30: stack(20, 40)},
                 {10: BOW, 30: stack(20, 40)},
                 {10: BOW, 18: stack(weaponchoice.AMMO_SLOT, 2), 30: stack(20, 40, kind=STONES)},
                 {18: stack(weaponchoice.AMMO_SLOT, 2), 30: stack(20, 40)})
        for items in cases:
            gd = FakeGd(items)
            before = counts(gd)
            with self.subTest(items=sorted(items)):
                self.assertEqual(run_top_up(gd), ([], []))
                self.assertEqual(counts(gd), before)
        self.assertEqual(run_top_up(FakeGd(cases[2]), member=5), ([], []))


class LabelTests(unittest.TestCase):
    def test_left(self):
        """The quiver and the pack's stacks of its kind, after a shot; "Out of arrows" at none, the
        kind named by the stack last shot from when the game has taken the quiver's away."""
        gd = FakeGd({10: BOW, 18: stack(weaponchoice.AMMO_SLOT, 1), 30: stack(20, 68), 32: stack(22, 9, kind=STONES)})
        self.assertEqual(quiver.left_label(gd, 2), "Arrows: 69 left")
        gd = FakeGd({10: BOW})
        self.assertEqual(quiver.left_label(gd, 2, bytes(stack(weaponchoice.AMMO_SLOT, 0))), "Out of arrows")
        self.assertEqual(quiver.left_label(gd, 2, bytes(stack(weaponchoice.AMMO_SLOT, 0, kind=STONES))), "Out of stones")
        self.assertIsNone(quiver.left_label(FakeGd({18: stack(weaponchoice.AMMO_SLOT, 3)}), 2))  # (no bow)
        self.assertIsNone(quiver.left_label(gd, 7))  # (a monster)


if __name__ == "__main__":
    unittest.main()
