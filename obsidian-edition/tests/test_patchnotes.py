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


class BodyTests(unittest.TestCase):
    def test_a_plain_quote_is_text(self):
        """A "> " line that isn't a developer's note is a paragraph, not a line never taken (a hang)."""
        html, _, _ = patchnotes.body("# T: x\n\n## S\n\n> quote without colon\n")
        self.assertIn("quote without colon", html)

    def test_the_status_is_kept(self):
        """The italic notes after the subtitle (that the notes can hold changes not yet released)
        reach the page's header; a plain paragraph after the lede (the Markdown's note on the page
        itself) does not."""
        _, _, head = patchnotes.body("# T: x\n\n*Current version 1.0.0*\n\nThe lede.\n\n"
                                     "*Not yet *released* changes.*\n\nAlso a web page.\n\n## S\n")
        self.assertEqual(head["subtitle"], "Current version 1.0.0")
        self.assertEqual(head["lede"], "The lede.")
        self.assertEqual(len(head["status"]), 1)
        self.assertIn("Not yet", head["status"][0])


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
        banner = page.split('<header class="banner">', 1)[1].split("</header>", 1)[0]
        self.assertIn("not yet in a release", banner)  # (the notes' caveat, with the version)


if __name__ == "__main__":
    unittest.main()
