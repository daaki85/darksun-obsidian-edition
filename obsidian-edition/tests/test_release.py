"""The release: its zip is the obsidian-edition folder with the patch notes' web page added
(.github/workflows/release.yml, .github/add_to_zip.py), and that page works from inside the zip."""

import os
import re
import unittest

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(HERE)
WORKFLOW = os.path.join(ROOT, ".github", "workflows", "release.yml")


@unittest.skipUnless(os.path.exists(WORKFLOW), "the repository's root")
class ReleaseTests(unittest.TestCase):
    def test_patch_notes_page_in_the_release(self):
        """The workflow adds patch-notes.html to the zip's folder and attaches it to the release."""
        with open(WORKFLOW, encoding="utf-8") as f:
            text = f.read()
        self.assertIn('python .github/add_to_zip.py "Dark-Sun-Shattered-Lands-Obsidian-Edition-$VERSION.zip"', text)
        self.assertIn('"Dark-Sun-Shattered-Lands-Obsidian-Edition-$VERSION/patch-notes.html" patch-notes.html', text)
        self.assertRegex(text, r'gh release create "v\$VERSION" "[^"]+\.zip" patch-notes\.html')
        self.assertTrue(os.path.exists(os.path.join(ROOT, ".github", "add_to_zip.py")))

    def test_patch_notes_page_works_from_the_zip(self):
        """Every link of the page is a web address or one of its own anchors: in the zip's folder,
        away from the repository's root, none points at a file that isn't there."""
        with open(os.path.join(ROOT, "patch-notes.html"), encoding="utf-8") as f:
            page = f.read()
        local = [h for h in re.findall(r'href="([^"]+)"', page) if not h.startswith(("http", "#", "mailto"))]
        self.assertEqual(local, [])


if __name__ == "__main__":
    unittest.main()
