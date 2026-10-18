"""The patch notes' web page (patch-notes.html) says what PATCH-NOTES.md says: each tagged line of
the notes is on the page, in the same order, and the page has as many."""

import html
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MD, PAGE = os.path.join(ROOT, "PATCH-NOTES.md"), os.path.join(ROOT, "patch-notes.html")


def read(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def plain(text: str) -> str:
    """Text without markup or tags, its spaces made one."""
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\*\*|\*|`", "", html.unescape(text))
    return " ".join(text.split())


@unittest.skipUnless(os.path.exists(MD) and os.path.exists(PAGE), "the patch notes (the repository's root)")
class PatchNotesTests(unittest.TestCase):
    def notes(self):
        tagged = re.findall(r"^- \*\*\[(New|Changed|Fixed)\]\*\* (.+)$", read(MD), re.M)
        return [(tag, plain(text)) for tag, text in tagged]

    def page(self):
        items = re.findall(r'<li><span class="tag (new|chg|fix)">\w+</span>(.+?)</li>',
                           read(PAGE), re.S)
        names = {"new": "New", "chg": "Changed", "fix": "Fixed"}
        return [(names[tag], plain(text)) for tag, text in items]

    def test_same_lines(self):
        self.assertGreater(len(self.notes()), 50)
        self.assertEqual(self.notes(), self.page())

    def test_page_is_whole(self):
        page = read(PAGE)
        self.assertTrue(page.startswith("<!doctype html>"))
        self.assertIn('<meta charset="utf-8">', page)


if __name__ == "__main__":
    unittest.main()
