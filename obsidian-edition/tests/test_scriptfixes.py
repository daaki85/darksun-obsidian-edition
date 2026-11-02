"""Tests for scriptfixes.py: the game's own script bugs mended in the Loader's copy of GPLDATA."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import scriptfixes as sf


def script_with(script: int, size: int = 0x800) -> bytes:
    """A made-up script holding the bytes each repair of SCRIPT expects, where it expects them
    (SIZE long, or longer for the last of them)."""
    code = bytearray(max([size] + [r.at + len(r.was) + 0x10 for r in sf.REPAIRS if r.script == script]))
    for r in sf.REPAIRS:
        if r.script == script:
            code[r.at:r.at + len(r.was)] = r.was
    return bytes(code)


class RepairTests(unittest.TestCase):
    def test_each_repair_lands(self):
        for script in {r.script for r in sf.REPAIRS}:
            code = script_with(script)
            fixed = sf.repaired(script, code)
            for r in sf.REPAIRS:
                if r.script != script:
                    continue
                if len(r.now) == len(r.was):
                    self.assertEqual(fixed[r.at:r.at + len(r.now)], r.now)
                    continue
                # a jump to the detour, past the script's end and its exit, then exits to WAS's length
                self.assertEqual(fixed[r.at], sf.JUMP)
                start = int.from_bytes(fixed[r.at + 1:r.at + 3], "big")
                self.assertGreater(start, len(code))
                self.assertEqual(fixed[len(code)], sf.EXIT)
                self.assertEqual(set(fixed[r.at + 3:r.at + len(r.was)]), {sf.EXIT} if len(r.was) > 3 else set())
                detour = fixed[start:start + len(r.now) + 3]
                for i in range(len(r.now)):  # (relocated addresses aside)
                    if not any(j <= i < j + 2 for j in r.relocate):
                        self.assertEqual(detour[i], r.now[i])
                for j in r.relocate:
                    self.assertEqual(int.from_bytes(detour[j:j + 2], "big"),
                                     int.from_bytes(r.now[j:j + 2], "big") + start)
                # and back to the bytes after WAS
                self.assertEqual(detour[len(r.now):], bytes((sf.JUMP,)) + (r.at + len(r.was)).to_bytes(2, "big"))

    def test_same_length_repairs_keep_the_length(self):
        self.assertEqual(len(sf.repaired(100, script_with(100))), 0x800)
        self.assertTrue(all(len(r.now) >= len(r.was) >= 3 or len(r.now) == len(r.was) for r in sf.REPAIRS))

    def test_lengthened_checks_read_through_the_character_record(self):
        # .71 before race, sex or the flags word, where the game read them from the combat record
        for r in sf.REPAIRS:
            if len(r.now) > len(r.was) and r.script in (31, 42, 80, 203):
                self.assertIn(bytes.fromhex("80250247"), r.now)
                self.assertNotIn(bytes.fromhex("802501"), r.now)

    def test_grate_attack_rolls_strength_and_award_once(self):
        grate = next(r for r in sf.REPAIRS if (r.script, r.at) == (137, 0xB5C))
        self.assertTrue(grate.now.startswith(bytes.fromhex("18e28c528f1ee1da")))  # TEST (RAND(30)) <
        self.assertIn(bytes.fromhex("b180250117"), grate.now)  # the member's STR (field 17h)
        self.assertEqual(grate.now[-3:], grate.was[-3:])  # its IF, to "fails to damage the lock", kept
        award = next(r for r in sf.REPAIRS if r.script == 204)
        self.assertTrue(award.now.startswith(bytes.fromhex("18cd02b7d78f00")))  # TEST flag 695 == 0
        self.assertEqual(award.now[7], sf.IF)
        self.assertEqual(int.from_bytes(award.now[8:10], "big"), len(award.now) - 1)  # to its ENDIF
        self.assertEqual(award.now[10:-1], award.was)
        self.assertEqual(award.now[-1], sf.ENDIF)
        self.assertEqual(award.relocate, (8,))

    def test_messenger_trigger_as_mas_9_registers_it(self):
        # MAS 9 at 6Ch: while flag 339 is 0, the sight trigger, entry 1 of GPL 133 on -1297, range 15
        messenger = [r for r in sf.REPAIRS if r.script == 58]
        self.assertEqual([r.at for r in messenger], [0x1A, 0x99, 0xCC])
        for r in messenger:
            self.assertTrue(r.now.startswith(r.was))  # the flag still set first
            self.assertIn(bytes.fromhex("18cd0153d78f003e"), r.now)
            self.assertIn(bytes.fromhex("1b000100859105118f0f"), r.now)
            self.assertEqual(int.from_bytes(r.now[13:15], "big"), len(r.now) - 1)  # to its ENDIF
        serf = next(r for r in sf.REPAIRS if r.script == 60)
        self.assertEqual((serf.was[-1], serf.now[-1], serf.now[:-1]), (14, 127, serf.was[:-1]))

    def test_too_long_a_script_left_alone(self):
        code = script_with(31, sf._longest())
        self.assertEqual(sf.repaired(31, code), code)

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
