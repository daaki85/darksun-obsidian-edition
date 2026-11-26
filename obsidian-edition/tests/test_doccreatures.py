"""The creatures' table (CREATURES.md, made by dsloader.doccreatures): every row's figure there, no
figure unused, and its tangle column as the cahulaks' rule has it (cahulaks.why_not)."""
import os
import re
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dsloader import cahulaks, doccreatures  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# a person's row (with its race) and a monster's (its race the figure's name's last word); a name
# may have where it is met in brackets after it (doccreatures.NOTES)
PERSON = re.compile(r"^\| !\[\]\(docs/creatures/([a-z0-9-]+)\.png\) \| ([^|]+?) \| ([a-z -]+) \| ([TSMLHG])( \?)? "
                    r"\| (yes|no: [^|]+?) \|$")
MONSTER = re.compile(r"^\| !\[\]\(docs/creatures/([a-z0-9-]+)\.png\) \| ([^|]+?) \| ([TSMLHG])( \?)? "
                     r"\| (yes|no: [^|]+?) \|$")


def rows():
    """(figure, name, race, size letter, the tangle column) for each row."""
    with open(os.path.join(ROOT, "CREATURES.md"), encoding="utf-8") as f:
        lines = f.read().splitlines()
    out = []
    for line in lines:
        m = PERSON.match(line)
        if m:
            out.append((m[1], m[2], m[3], m[4], m[6]))
            continue
        m = MONSTER.match(line)
        if m:
            out.append((m[1], m[2], m[1].rsplit("-", 1)[1], m[3], m[5]))
    return [(f, re.sub(r" \(.*\)$", "", name), race, size, answer) for f, name, race, size, answer in out]


class CreaturesTableTests(unittest.TestCase):
    def test_figures_there(self):
        found = rows()
        self.assertGreater(len(found), 150)
        names = {f for f, _, _, _, _ in found}
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
        for _, name, race, _, answer in rows():
            names.add(name)
            why = cahulaks.why_not(name, races.get(race, 99))
            self.assertEqual(answer, f"no: {why}" if why else "yes", name)
        self.assertEqual(cahulaks.BIG_NAMES - names, set())

    def test_sizes(self):
        """Every row has its size (sizes.size), and every monster name on sizes.py's list is a creature
        of the game's."""
        from dsloader import sizes
        found = rows()
        races = {v: k for k, v in doccreatures.RACES.items()}
        for _, name, race, size, _ in found:
            self.assertEqual(size, sizes.size(name, races.get(race, 99)), name)
        self.assertEqual(set(sizes.NAMES) - {name for _, name, _, _, _ in found}, set())
        self.assertLessEqual(sizes.UNSURE, set(sizes.NAMES))

    def test_notes(self):
        """A name more than one kind of creature has says where each is met (doccreatures.NOTES), and
        no note is for a creature the game hasn't."""
        kinds = {(name, race) for _, name, race, _, _ in rows()}
        self.assertLessEqual({(name, doccreatures.race_name(race)) for name, race in doccreatures.NOTES}, kinds)
        for name in ("Guard", "Slave", "Worker"):
            self.assertTrue(any(n == name for n, _ in doccreatures.NOTES), name)

    def test_party_left_out(self):
        self.assertFalse({name for _, name, _, _, _ in rows()} & doccreatures.PARTY)


if __name__ == "__main__":
    unittest.main()
