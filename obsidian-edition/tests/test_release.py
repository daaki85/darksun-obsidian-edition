"""The release (.github/workflows/release.yml): its zip is the obsidian-edition folder as git archive
makes it, less what the folder's .gitattributes marks export-ignore (the developer pages, tests/,
docs/viewer.png); the patch notes' web page is an asset of its own beside the zip, and works away
from the repository."""

import io
import os
import re
import subprocess
import tarfile
import unittest

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(HERE)
WORKFLOW = os.path.join(ROOT, ".github", "workflows", "release.yml")


def archived(treeish: str) -> list:
    """The files git archive puts in the zip from TREEISH (the workflow's form: commit:obsidian-edition)."""
    out = subprocess.run(["git", "archive", "--format=tar", treeish], cwd=ROOT, capture_output=True, check=True).stdout
    with tarfile.open(fileobj=io.BytesIO(out)) as tar:
        return [m.name for m in tar.getmembers() if m.isfile()]


@unittest.skipUnless(os.path.exists(WORKFLOW), "the repository's root")
def importers_of(module: str) -> list:
    """The Loader's modules that import MODULE of dsloader (a module left out of the zip must
    have none: the Loader would not start)."""
    import ast
    out = []
    folder = os.path.join(HERE, "dsloader")
    for name in sorted(os.listdir(folder)):
        if not name.endswith(".py") or name == module + ".py":
            continue
        with open(os.path.join(folder, name), encoding="utf-8") as f:
            tree = ast.parse(f.read())
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and (node.module or "").split(".")[-1] == module:
                out.append(name)
            elif isinstance(node, (ast.Import, ast.ImportFrom)) and any(a.name.split(".")[-1] == module
                                                                         for a in node.names):
                out.append(name)
    return out


class ReleaseTests(unittest.TestCase):
    def test_patch_notes_page_in_the_release(self):
        """The workflow zips the folder alone (the patch notes' page no longer added to it: the zip's
        copy is the manual's changes.html) and attaches patch-notes.html to the release beside it."""
        with open(WORKFLOW, encoding="utf-8") as f:
            text = f.read()
        self.assertIn('git archive --format=zip --prefix="Dark-Sun-Shattered-Lands-Obsidian-Edition-$VERSION/"', text)
        self.assertIn('"$GITHUB_SHA":obsidian-edition', text)
        self.assertNotIn("add_to_zip", text)
        self.assertRegex(text, r'gh release create "v\$VERSION" "[^"]+\.zip" patch-notes\.html')

    def test_patch_notes_page_works_from_the_zip(self):
        """Every link of the page is a web address or one of its own anchors: downloaded on its own,
        away from the repository's root, none points at a file that isn't there."""
        with open(os.path.join(ROOT, "patch-notes.html"), encoding="utf-8") as f:
            page = f.read()
        local = [h for h in re.findall(r'(?:href|src)="([^"]+)"', page)
                 if not h.startswith(("http", "#", "mailto", "data:"))]
        self.assertEqual(local, [])

    @unittest.skipUnless(os.path.exists(os.path.join(ROOT, ".git")), "a git checkout")
    def test_what_the_zip_holds(self):
        """git archive of the committed folder (the workflow's form) leaves out the developer pages,
        tests/, docs/viewer.png and the developers' tool dsloader/questdraft.py, and keeps the
        player's pages, the manual, the Loader and the .bat files. No module that ships imports
        one that doesn't."""
        try:
            names = archived("HEAD:obsidian-edition")
        except (OSError, subprocess.CalledProcessError) as e:
            self.skipTest(f"git archive: {e}")
        left = [n for n in names
                if re.match(r"(DEVELOPMENT[A-Z-]*\.md|tests/|docs/viewer\.png|dsloader/questdraft\.py)", n)]
        self.assertEqual(left, [])
        self.assertIn("dsloader/quests.py", names)  # (the quest table itself ships)
        self.assertEqual(importers_of("questdraft"), [])
        for kept in ("README.md", "PLAYER-GUIDE.md", "FEATURES.md", "KITS.md", "manual/index.html",
                     "manual/changes.html", "manual/manual.css", "dsloader/__init__.py", "dsloader/viewer.py",
                     "Start Obsidian Edition.bat", "LICENSE"):
            self.assertIn(kept, names)
        self.assertNotIn("patch-notes.html", names)


if __name__ == "__main__":
    unittest.main()
