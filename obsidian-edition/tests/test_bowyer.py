"""Tests for the dice log's line for a shot at the Bowyer's archery target (dsloader/bowyer.py)."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import bowyer, gpl

FIELDS = bytes(72) + b"\x12" + bytes(12) + b"\x10" + bytes(170)  # (the game's types of fields 72 and 85)


def target_script() -> bytes:
    """A script laid out as the Bowyer's (178) where it counts the bows: filler commands up to
    PHRAIN, Phrain's Bow counted, the three counts added, then a return."""
    five = gpl.encode_op((bowyer.SET, [("expr", [("n", 0)]), ("var", 2, 6)]))
    lead = five * ((bowyer.PHRAIN - 3) // 5) + gpl.encode_op((bowyer.GOTO, [("n", 0)]))
    assert len(lead) == bowyer.PHRAIN
    return lead + bowyer.PHRAIN_COUNT + bowyer.SUM_THREE + bytes([0x15])


class BowyerTests(unittest.TestCase):
    def test_distance(self):
        """The game's squares: along a row, the count; across, its rounded square root."""
        self.assertEqual(bowyer.distance(41, 69, 56, 69), 15)
        self.assertEqual(bowyer.distance(0, 0, 3, 4), 5)
        self.assertEqual(bowyer.distance(0, 0, 10, 10), 14)
        self.assertEqual(bowyer.distance(5, 5, 5, 5), 0)
        self.assertEqual(bowyer.distance(0, 0, 300, 0), bowyer.FAR_AWAY)

    def test_need(self):
        self.assertEqual(bowyer.need(21, 15), 14)
        self.assertEqual(bowyer.need(12, 15), 2)  # (DEX under the distance)

    def test_results(self):
        line = bowyer.describe(3, 21, 15, 9, False, "Daaki")[0]
        self.assertEqual(line, "Daaki shoots at the archery target (15 squares from the target, 9 from the Bowyer): "
                               "0-20 = 3, needs under 14 (DEX 21 - 15 / 2), the centre 4 or less "
                               "-> the centre: the Bowyer's reward, 6 Arrows +2")
        self.assertTrue(bowyer.describe(14, 21, 15, 9, False, "D")[0].endswith("-> miss"))
        self.assertTrue(bowyer.describe(12, 21, 15, 9, False, "D")[0].endswith("-> the outer ring"))
        self.assertTrue(bowyer.describe(6, 21, 15, 9, False, "D")[0].endswith("-> the inner ring"))
        self.assertIn("13 squares or closer", bowyer.describe(0, 21, 12, 9, False, "D")[0])
        self.assertIn("once", bowyer.describe(0, 21, 15, 9, True, "D")[0])
        self.assertIn("25 squares or more", bowyer.describe(0, 21, 15, 25, False, "D")[0])


class DunesongTests(unittest.TestCase):
    def test_counted_with_the_bows(self):
        """The sum jumps to code at the end that counts Dunesong too, adds the four and comes back;
        the script still reads command by command, and nothing before the end moves."""
        old = target_script()
        new = bowyer.with_dunesong(old)
        ops = {o.at: o for o in gpl.walk(gpl.decode(new, FIELDS))}
        self.assertEqual(ops[bowyer.SUM].code, bowyer.GOTO)
        self.assertEqual(ops[bowyer.SUM].args, [("n", len(old))])
        count = ops[len(old)].args
        self.assertEqual(count[1], ("var", 2, 5))
        self.assertIn((72, 4, ("n", -bowyer.DUNESONG)), count[0][1].args[3])
        last = max(ops)
        self.assertEqual((ops[last].code, ops[last].args), (bowyer.GOTO, [("n", bowyer.SUM_NEXT)]))
        self.assertEqual(new[bowyer.SUM_NEXT:len(old)], old[bowyer.SUM_NEXT:])
        self.assertEqual(new[:bowyer.SUM], old[:bowyer.SUM])

    def test_once_and_only_as_expected(self):
        new = bowyer.with_dunesong(target_script())
        self.assertEqual(bowyer.with_dunesong(new), new)
        other = bytearray(target_script())
        other[bowyer.PHRAIN + 10] ^= 1
        self.assertEqual(bowyer.with_dunesong(bytes(other)), bytes(other))
        self.assertEqual(bowyer.script_chunks({}), {})


if __name__ == "__main__":
    unittest.main()
