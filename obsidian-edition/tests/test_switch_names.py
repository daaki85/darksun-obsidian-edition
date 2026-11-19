"""The Loader's window asks only for switches it has: every rule_vars["..."] in viewer.py names a
rule that still has a switch (game.RULE_SETTINGS). After "Fewer switches" two lines still asked
for "stealth" and "aging", gone from the tab: with a game attached the Characters tab stayed
empty ("Loader error in the party table: KeyError: 'stealth'"), which no test without a game saw."""

import os
import re
import sys
import unittest

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)

from dsloader import game  # noqa: E402


class SwitchNameTests(unittest.TestCase):
    def test_rule_switches_asked_for_exist(self):
        with open(os.path.join(HERE, "dsloader", "viewer.py"), encoding="utf-8") as f:
            asked = set(re.findall(r'rule_vars\["(\w+)"\]', f.read()))
        kept = {key for key, _ in game.RULE_SETTINGS}
        self.assertEqual(asked - kept, set())
        self.assertEqual(asked & set(game.ALWAYS_ON), set())


if __name__ == "__main__":
    unittest.main()
