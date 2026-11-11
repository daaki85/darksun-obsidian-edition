"""The player's guide's Options tab at a glance (PLAYER-GUIDE.md): each row's Loader label is the
Options tab's own text (viewer.py's strings, read without Tk), and every rule change and new
content switch has its row."""

import ast
import os
import re
import unittest

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # obsidian-edition


def viewer_texts() -> set:
    """Every string of viewer.Viewer._build_options."""
    with open(os.path.join(HERE, "dsloader", "viewer.py"), encoding="utf-8") as f:
        tree = ast.parse(f.read())
    build = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "_build_options")
    return {n.value for n in ast.walk(build) if isinstance(n, ast.Constant) and isinstance(n.value, str)}


def switch_texts() -> list:
    """The labels of the switches listed as (key, group, text) or (key, text) in _build_options."""
    with open(os.path.join(HERE, "dsloader", "viewer.py"), encoding="utf-8") as f:
        tree = ast.parse(f.read())
    build = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "_build_options")
    out = []
    for loop in (n for n in ast.walk(build) if isinstance(n, ast.For)):
        if not isinstance(loop.iter, ast.Tuple):
            continue
        for item in loop.iter.elts:
            if isinstance(item, ast.Tuple) and isinstance(item.elts[-1], ast.Constant):
                text = item.elts[-1].value
                if isinstance(text, str) and len(text) > 20:
                    out.append(text)
    return out


def table_labels() -> list:
    """The first cell of each table row in the guide's Options tab at a glance."""
    with open(os.path.join(HERE, "PLAYER-GUIDE.md"), encoding="utf-8") as f:
        text = f.read()
    part = text.split("\n## The Options tab at a glance\n", 1)[1].split("\n## ", 1)[0]
    rows = [line for line in part.splitlines() if line.startswith("| ")]
    return [cells(row)[0] for row in rows if not row.startswith("| Loader label |")]


def cells(row: str) -> list:
    """A table row's cells, stripped."""
    return [cell.strip() for cell in row.strip().strip("|").split("|")]


def made_of(cell: str, texts: set) -> bool:
    """CELL is one of TEXTS, or several of them one after another (a heading and its choice)."""
    if cell in texts:
        return True
    return any(cell.startswith(t + " ") and made_of(cell[len(t) + 1:], texts) for t in texts if t)


class OptionsTableTests(unittest.TestCase):
    def test_labels_are_the_loaders(self):
        texts = viewer_texts()
        labels = table_labels()
        self.assertGreater(len(labels), 50)
        for label in labels:
            self.assertTrue(made_of(label, texts), label)

    def test_every_switch_has_its_row(self):
        labels = table_labels()
        for text in switch_texts():  # (a choice under a heading: the heading, then it)
            self.assertTrue(any(label == text or label.endswith(" " + text) for label in labels), text)

    def test_takes_effect_given(self):
        with open(os.path.join(HERE, "PLAYER-GUIDE.md"), encoding="utf-8") as f:
            part = f.read().split("\n## The Options tab at a glance\n", 1)[1]
        for row in (line for line in part.splitlines() if line.startswith("| ") and "(a button)" not in line):
            if row.startswith("| Loader label |"):
                continue
            when = cells(row)[2]
            self.assertRegex(when, r"^(at once|next start|new characters|first visit)", row)


if __name__ == "__main__":
    unittest.main()
