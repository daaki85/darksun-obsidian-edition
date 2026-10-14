"""No manual check (manualcheck.py): the dragon's question, script 20, made what the right answer
leaves, on a script shaped as the game's."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import gpl, manualcheck as m

FIELDS = bytes(72) + b"\x10" + bytes(16)


def dragons():
    """The question's lines, as the game's script 20 has them (and its end)."""
    return gpl.encode([(m.START, []), (0x4F, [("n", 115), ("str", "You will go no further unless you answer my question....")]),
                       (0x4F, [("n", 115), ("str", "The ")]), (0x4F, [("n", 115), m.QUESTION]),
                       (0x4F, [("n", 115), ("str", "'. What is that word?")]), (m.END, [])])


class ManualCheckTests(unittest.TestCase):
    def test_answered(self):
        """Its entry point (1) on the right answer's settings: 255 in (7, 4); in the warrens,
        the bit that asks once; then the end. Every jump on a command."""
        ops = gpl.decode(m.answered(), FIELDS)
        self.assertEqual([(o.code, o.args) for o in ops], [
            (m.START, []), (m.SET, [("n", 255), ("var", 7, 4)]), (m.SWITCH, [("var", 137, 36)]),
            (m.CASE, [("n", 0x28), ("n", ops[5].at)]), (m.SET_BIT, [("var", 135, 73), ("n", 12)]),
            (m.END_SWITCH, []), (m.END, [])])
        self.assertEqual(ops[1].at, 1)

    def test_only_the_dragon(self):
        key = ("GPL ", m.SCRIPT)
        self.assertEqual(m.script_chunks({key: dragons()}, FIELDS), {key: m.answered()})
        self.assertEqual(m.script_chunks({key: m.answered()}, FIELDS), {})  # (done already)
        other = gpl.encode([(m.START, []), (0x4F, [("n", 115), ("str", "Something else. ")]), (m.END, [])])
        self.assertEqual(m.script_chunks({key: other}, FIELDS), {})
        self.assertEqual(m.script_chunks({}, FIELDS), {})


if __name__ == "__main__":
    unittest.main()
