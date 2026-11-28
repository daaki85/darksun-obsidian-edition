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


RAVAGER = "## Wake of the Ravager"


def page(sequel: bool = False):
    """CREATURES.md's lines: Shattered Lands' part, or (SEQUEL) Wake of the Ravager's."""
    with open(os.path.join(ROOT, "CREATURES.md"), encoding="utf-8") as f:
        text = f.read()
    head, _, tail = text.partition(RAVAGER + "\n")
    return (tail if sequel else head).splitlines()


# the sequel's rows: its figure (or "none"), name, race (people), size, the tangle column, how it's drawn
RAV_ROW = re.compile(r"^\| (?:!\[\]\(docs/creatures/ravager/([a-z0-9-]+)\.png\)|none) \| ([^|]+?) \| (?:([a-z -]+) \| )?"
                     r"([TSMLHG])( \?)? \| (yes|no: [^|]+?) \| (redrawn[^|]*|the game's(?: \(kept\))?|none) \|$")


def rav_rows():
    """(figure or None, name, race or None, size letter, unsure, the tangle column, drawn) for each sequel row."""
    return [m.groups() for m in map(RAV_ROW.match, page(True)) if m]


def rows():
    """(figure, name, race, size letter, the tangle column) for each of Shattered Lands' rows."""
    lines = page()
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
        unused = {f[:-4] for f in os.listdir(os.path.join(ROOT, "docs", "creatures")) if f.endswith(".png")} - names
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


class RavagerCreaturesTests(unittest.TestCase):
    """The sequel's part of the page (doccreatures.write_ravager)."""

    def test_rows_and_figures(self):
        found = rav_rows()
        self.assertGreater(len(found), 150)
        self.assertEqual(len(found), sum(1 for line in page(True) if line.startswith("| ") and "---" not in line
                                         and not line.startswith("| Figure")))  # (every row read)
        figures = [f for f, *_ in found if f]
        self.assertEqual(len(set(figures)), len(figures))
        folder = os.path.join(ROOT, "docs", "creatures", doccreatures.RAV_FOLDER)
        self.assertEqual({f[:-4] for f in os.listdir(folder)}, set(figures))  # (none missing, none unused)
        self.assertFalse({name for _, name, *_ in found} & {"Terrannus", "Thy-rohk", "Gerrakis", "Ar'Anda"})

    def test_size_and_tangle(self):
        """Each row's size is the sequel's table's (sizes.RAV_NAMES by name for the rest, people by race), and
        its tangle answer DSCLOG2's: no for a half-giant or anything large or bigger, else yes."""
        from dsloader import sizes
        races = {v: k for k, v in doccreatures.RAV_RACES.items() if k <= 8}
        names = set()
        for _, name, race, size, unsure, answer, _ in rav_rows():
            names.add(name)
            want = sizes.RACES[races[race]] if race else sizes.RAV_NAMES.get(name, "M")
            self.assertEqual(size, want, name)
            if race == "half-giant":
                self.assertEqual(answer, "no: too big (a half-giant)", name)
            else:
                self.assertEqual(answer, "no: too big" if size in "LHG" else "yes", name)
        self.assertLessEqual(set(sizes.RAV_NAMES), names)  # (no slip of a name in the sequel's table)

    def test_redrawn_marked(self):
        """The redrawn figures are marked so, and most of the sequel's figures are; the Tarrasque has its fight's
        figure; a row with no figure says none."""
        found = rav_rows()
        drawn = [d for *_, d in found]
        self.assertGreater(sum(d.startswith("redrawn") for d in drawn), len(drawn) * 3 // 4)
        self.assertTrue(all((f is None) == (d == "none") for f, *_, d in found))
        self.assertTrue(any(f and name == "Tarrasque" for f, name, *_ in found))

    def test_standing_frame(self):
        """rav_standing draws the frame the picture's script stands in (slot 16's first step), from the combat
        picture where that step says so, and the first frame with no script: a redraw that adds its frames after
        the game's is drawn by its own."""
        import struct
        from dsloader import art
        frames = [[[n + 1, None], [None, n + 1]] for n in range(3)]
        def script(frame, flags=0):
            slots = [0xFFFF] * doccreatures.RAV_SLOTS
            slots[doccreatures.RAV_STANDING] = 1
            return (struct.pack(f"<{doccreatures.RAV_SLOTS}H", *slots) + bytes(8)
                    + bytes((frame, 0, flags, 0, 0, 0, 0, 0)))
        chunks = {("BMP ", 7): art.plnr_frames(frames), ("CBMP", 7): art.plnr_frames(frames[::-1])}
        self.assertEqual(doccreatures.rav_standing(chunks, 7), frames[0])
        chunks[("SCMD", 7)] = script(2)
        self.assertEqual(doccreatures.rav_standing(chunks, 7), frames[2])
        chunks[("SCMD", 7)] = script(2, doccreatures.RAV_COMBAT)
        self.assertEqual(doccreatures.rav_standing(chunks, 7), frames[0])
        self.assertIsNone(doccreatures.rav_standing(chunks, 8))


if __name__ == "__main__":
    unittest.main()
