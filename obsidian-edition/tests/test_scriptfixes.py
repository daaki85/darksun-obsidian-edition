"""Tests for scriptfixes.py: the game's own script bugs mended in the Loader's copy of GPLDATA."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import scriptfixes as sf


def script_with(script: int, size: int = 0x800) -> bytes:
    """A made-up script holding the bytes each repair of SCRIPT expects, where it expects them."""
    code = bytearray(size)
    for r in sf.REPAIRS:
        if r.script == script:
            code[r.at:r.at + len(r.was)] = r.was
    return bytes(code)


class RepairTests(unittest.TestCase):
    def test_each_repair_lands_and_keeps_the_length(self):
        for script in {r.script for r in sf.REPAIRS}:
            code = script_with(script)
            fixed = sf.repaired(script, code)
            self.assertEqual(len(fixed), len(code))
            for r in sf.REPAIRS:
                if r.script == script:
                    self.assertEqual(fixed[r.at:r.at + len(r.now)], r.now)
                    self.assertEqual(len(r.was), len(r.now))

    def test_other_bytes_left_alone(self):
        # (another release, or a script the Loader changed there)
        code = bytes(0x800)
        self.assertEqual(sf.repaired(100, code), code)
        self.assertEqual(sf.repaired(5, script_with(100)), script_with(100))

    def test_chunks_from_the_loaders_changes_first(self):
        game = {("GPL ", 68): script_with(68), ("GPL ", 100): bytes(0x700)}
        out = {("GPL ", 100): script_with(100, 0x700)}
        changed = sf.script_chunks(game, out)
        self.assertEqual(set(changed), {("GPL ", 68), ("GPL ", 100)})
        self.assertEqual(sf.script_chunks({}, {}), {})


if __name__ == "__main__":
    unittest.main()
