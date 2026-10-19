"""The version is the same wherever it is said: dsloader's __version__, the patch notes' "Current
version", the front page's "is out", and a release-notes file of its own."""

import os
import re
import sys
import unittest

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import dsloader  # noqa: E402


def read(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


@unittest.skipUnless(os.path.exists(os.path.join(ROOT, "PATCH-NOTES.md")), "the repository's root")
class VersionTests(unittest.TestCase):
    def test_one_version(self):
        version = dsloader.__version__
        notes = re.search(r"Current version (\d+\.\d+\.\d+)", read(os.path.join(ROOT, "PATCH-NOTES.md")))
        front = re.search(r"\*\*Obsidian Edition (\d+\.\d+\.\d+)\*\* is out", read(os.path.join(ROOT, "README.md")))
        self.assertEqual((notes.group(1), front.group(1)), (version, version))
        self.assertTrue(os.path.exists(os.path.join(ROOT, "release-notes", f"v{version}.md")))


if __name__ == "__main__":
    unittest.main()
