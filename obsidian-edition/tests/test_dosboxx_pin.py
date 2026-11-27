"""The DOSBox-X the Windows zip brings is the same in the release and in the test package: release.yml
and test-package.yml each pin DOSBOX_X_VERSION and DOSBOX_X_SHA256 (.github/scripts/add_dosbox_x.py reads
them), and a test download is only the release's package while the two agree (the follow-up code audit,
2026-11-27). Skipped where the workflows aren't (a release zip has no .github folder)."""

import os
import re
import unittest

WORKFLOWS = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                         ".github", "workflows")
FILES = ("release.yml", "test-package.yml")
NAMES = ("DOSBOX_X_VERSION", "DOSBOX_X_SHA256")


@unittest.skipUnless(all(os.path.isfile(os.path.join(WORKFLOWS, f)) for f in FILES), "no .github/workflows")
class PinTests(unittest.TestCase):
    def test_same_dosbox_x(self):
        found = {}
        for f in FILES:
            with open(os.path.join(WORKFLOWS, f), encoding="utf-8") as fh:
                text = fh.read()
            found[f] = tuple(re.search(r'^\s*%s:\s*"([^"]+)"' % n, text, re.M).group(1) for n in NAMES)
        self.assertEqual(found[FILES[0]], found[FILES[1]])
        self.assertRegex(found[FILES[0]][1], r"^[0-9a-f]{64}$")


if __name__ == "__main__":
    unittest.main()
