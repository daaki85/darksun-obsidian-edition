"""The patch notes' web page (patchnotes.py): up to date with PATCH-NOTES.md, every tagged line of
the notes on it, every link within the page has its target, and the Markdown comes out as HTML."""

import os
import re
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import patchnotes  # noqa: E402


def read(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


@unittest.skipUnless(os.path.exists(patchnotes.NOTES), "the patch notes (the repository's root)")
class PatchNotesTests(unittest.TestCase):
    def test_up_to_date(self):
        self.assertEqual(read(patchnotes.PAGE), patchnotes.build(),
                         "patch-notes.html is behind PATCH-NOTES.md: run python -m dsloader.patchnotes")

    def test_every_tagged_line(self):
        tagged = re.findall(r"^- \*\*\[(New|Changed|Fixed)\]\*\* ", read(patchnotes.NOTES), re.M)
        shown = re.findall(r'<li><span class="tag (new|chg|fix)">', patchnotes.build())
        self.assertGreater(len(tagged), 50)
        self.assertEqual([patchnotes.TAGS[t] for t in tagged], shown)

    def test_page(self):
        page = patchnotes.build()
        shown = re.sub(r'<script type="text/markdown".*?</script>', "", page, flags=re.S)
        self.assertTrue(page.startswith("<!doctype html>"))
        self.assertIn('<meta charset="utf-8">', page)
        ids = set(re.findall(r' id="([^"]+)"', page))
        self.assertEqual(set(re.findall(r'href="#([^"]+)"', page)) - ids, set())
        self.assertNotIn("**", shown)
        self.assertNotIn("](", shown)
        self.assertIn('<span class="was">(was 10)</span>', page)
        self.assertIn('<div class="dev"><b>Developers\' Notes</b>', page)
        self.assertIn(read(patchnotes.NOTES), page)  # (the Markdown the copy button gives)


if __name__ == "__main__":
    unittest.main()
