"""Tests for the scripts' ability checks made with their random command (dsloader/scriptchecks.py),
on hand-made scripts."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import gpl, scriptchecks

FIELDS = bytes(256)
CHA = ("field", scriptchecks.ACTING, [28])
INT = ("field", scriptchecks.ACTING, [26])


def rand(most: int) -> tuple:
    return ("op", gpl.Op(0, scriptchecks.RANDOM, [("n", most)]))


def script(*conditions) -> bytes:
    """An "if" (18h) for each condition, then a return (15h)."""
    return b"".join(gpl.encode_op((0x18, [("expr", c)])) for c in conditions) + bytes([0x15])


# Chahl's (script 181): "(random(19)) <= CHA", and "(random(19)) <= (CHA - 4)"
SCARS = ["(", rand(19), ")", "<=", CHA]
OTHERS = ["(", rand(19), ")", "<=", "(", CHA, "-", ("n", 4), ")"]
# a secret door (script 69): "((random(19)) + 1) <= (INT - 10)"
DOOR = ["(", "(", rand(19), ")", "+", ("n", 1), ")", "<=", "(", INT, "-", ("n", 10), ")"]
# a guard (script 92): "(((random(10)) + 10) > CHA)", true when the talk fails
GUARD = ["(", "(", "(", rand(10), ")", "+", ("n", 10), ")", ">", CHA, ")"]


class ScriptCheckTests(unittest.TestCase):
    def test_found_by_position(self):
        """Each condition by the position DSCLOG records: past its random command and the N."""
        data = script(SCARS, DOOR)
        found = scriptchecks.find({("GPL ", 181): data}, FIELDS)
        ops = gpl.decode(data, FIELDS)
        rolls = [o.at + scriptchecks.PAST for o in gpl.walk(ops) if o.code == scriptchecks.RANDOM]
        self.assertEqual(sorted(found), sorted(rolls))
        self.assertEqual([(found[at].script, found[at].most, scriptchecks.ABILITIES[found[at].ability])
                          for at in sorted(found)], [("GPL 181", 19, "CHA"), ("GPL 181", 19, "INT")])

    def test_shared_position_left_out(self):
        """Two scripts with a random command at the same position: neither is named."""
        found = scriptchecks.find({("GPL ", 1): script(SCARS), ("GPL ", 2): script(OTHERS)}, FIELDS)
        self.assertEqual(found, {})

    def test_describe(self):
        check = scriptchecks.Check("GPL 181", 19, 5, SCARS)
        self.assertEqual(scriptchecks.describe(check, 12, 14, "Daaki"),
                         ["Daaki CHA check: 0-19 = 12, needs 14 or less (CHA 14) -> success"])
        self.assertEqual(scriptchecks.describe(check, 15, 14, "Daaki")[0][-7:], "failure")
        check = scriptchecks.Check("GPL 181", 19, 5, OTHERS)
        self.assertEqual(scriptchecks.describe(check, 11, 14, "Daaki"),
                         ["Daaki CHA check: 0-19 = 11, needs 10 or less (CHA 14 - 4) -> failure"])
        self.assertIn("always made", scriptchecks.describe(scriptchecks.Check("GPL 181", 19, 5, SCARS), 3, 20, "D")[0])

    def test_die_and_failing_condition(self):
        """A roll plus 1 is a d20; a condition true when the talk fails still says success for a
        roll the score beats."""
        door = scriptchecks.Check("GPL 69", 19, 3, DOOR)
        self.assertEqual(scriptchecks.describe(door, 2, 14, "Cilla"),
                         ["Cilla INT check: d20 = 3, needs 4 or less (INT 14 - 10) -> success"])
        guard = scriptchecks.Check("GPL 92", 10, 5, GUARD)
        self.assertEqual(scriptchecks.describe(guard, 3, 16, "Cilla"),
                         ["Cilla CHA check: 10-20 = 13, needs 16 or less (CHA 16) -> success"])
        self.assertTrue(scriptchecks.describe(guard, 9, 16, "Cilla")[0].endswith("failure"))


if __name__ == "__main__":
    unittest.main()
