"""The creatures' table (CREATURES.md, made by dsloader.doccreatures): every row's figure there, no
figure unused, and its tangle column as the cahulaks' rule has it (cahulaks.why_not)."""
import os
import re
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dsloader import cahulaks, doccreatures  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROW = re.compile(r"^\| !\[\]\(docs/creatures/([a-z0-9-]+)\.png\) \| (.+?) \| ([a-z -]+) \| ([TSMLHG]) \(([a-z-]+)\)( \?)? "
                 r"\| (yes|no: .+?) \|$")


def rows():
    with open(os.path.join(ROOT, "CREATURES.md"), encoding="utf-8") as f:
        return [(m[1], m[2], m[3], m[7]) for m in map(ROW.match, f.read().splitlines()) if m]


class CreaturesTableTests(unittest.TestCase):
    def test_figures_there(self):
        found = rows()
        self.assertGreater(len(found), 150)
        names = {f for f, _, _, _ in found}
        self.assertEqual(len(names), len(found))  # (a figure each)
        for figure in names:
            self.assertTrue(os.path.exists(os.path.join(ROOT, "docs", "creatures", figure + ".png")), figure)
        unused = {f[:-4] for f in os.listdir(os.path.join(ROOT, "docs", "creatures"))} - names
        self.assertEqual(unused, set())

    def test_tangle_column(self):
        """Each row's answer is cahulaks.why_not's, by name and race; every name on the cahulaks' lists
        is a creature of the game (no slip of a name)."""
        races = {v: k for k, v in doccreatures.RACES.items()}
        names = set()
        for _, name, race, answer in rows():
            names.add(name)
            why = cahulaks.why_not(name, races.get(race, 99))
            self.assertEqual(answer, f"no: {why}" if why else "yes", name)
        self.assertEqual(cahulaks.BIG_NAMES - names, set())

    def test_sizes(self):
        """Every row has its size (sizes.size), every monster name on sizes.py's list is a creature of the
        game's, and the size's word is its letter's."""
        from dsloader import sizes
        with open(os.path.join(ROOT, "CREATURES.md"), encoding="utf-8") as f:
            found = [m for m in map(ROW.match, f.read().splitlines()) if m]
        races = {v: k for k, v in doccreatures.RACES.items()}
        for m in found:
            self.assertEqual(m[4], sizes.size(m[2], races.get(m[3], 99)), m[2])
            self.assertEqual(m[5], sizes.SIZE_NAMES[m[4]])
        self.assertEqual(set(sizes.NAMES) - {m[2] for m in found}, set())
        self.assertLessEqual(sizes.UNSURE, set(sizes.NAMES))

    def test_party_left_out(self):
        self.assertFalse({name for _, name, _, _ in rows()} & doccreatures.PARTY)


if __name__ == "__main__":
    unittest.main()
