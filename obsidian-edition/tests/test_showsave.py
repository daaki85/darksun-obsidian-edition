"""Show Save.bat (python -m dsloader save FILE): a Shattered Lands save's party, and a Wake of the
Ravager save's (its layout, its sheets the game's 42h made the Loader's 48h first), from the play kit's
saves (playtest/saves, beside the mod; skipped where they aren't)."""

import argparse
import io
import os
import sys
import unittest
from contextlib import redirect_stdout

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import __main__ as cli, ravlog  # noqa: E402

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAVES = os.path.join(HERE, "..", "playtest", "saves")
LAYOUT = os.path.join(HERE, "layouts", "shattered_lands.json")


def shown(path):
    out = io.StringIO()
    with redirect_stdout(out):
        cli.cmd_save(argparse.Namespace(file=path, layout=LAYOUT))
    rows = {}
    for line in out.getvalue().splitlines():
        label = line.split("  ")[0]
        rows[label] = line[len(label):].split()
    return rows


class ShowSaveTests(unittest.TestCase):
    def save(self, name):
        path = os.path.join(SAVES, name, "SAVE01.SAV")
        if not os.path.isfile(path):
            self.skipTest(f"no {path}")
        return path

    def test_shattered_lands(self):
        rows = shown(self.save("pens-after-arena"))
        self.assertEqual(rows["Name"], ["Gerakis", "K'ratchek", "Cermak", "Cilla"])
        self.assertEqual(rows["Max HP"], ["54", "19", "45", "15"])

    def test_wake_of_the_ravager(self):
        self.addCleanup(ravlog.restore_layout)  # (the sequel's layout, which the command leaves on)
        rows = shown(self.save("ravager-after-ambush"))
        self.assertEqual(rows["Name"], ["Ar'Anda", "Terrannus", "Thy'rokh", "Gerakis"])
        self.assertEqual(rows["Max HP"], ["48", "64", "75", "165"])
        self.assertEqual(rows["HP"], ["48", "1", "75", "143"])
        self.assertIn("Half-giant", " ".join(rows["Race"]))


if __name__ == "__main__":
    unittest.main()
