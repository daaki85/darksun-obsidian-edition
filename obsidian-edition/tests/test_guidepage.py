"""The player's guide as a web page (guidepage.py): up to date with PLAYER-GUIDE.md, every link
within the page has its target, and the Markdown it uses comes out as HTML."""

import os
import re
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import guidepage


class GuidePageTests(unittest.TestCase):
    def test_up_to_date(self):
        with open(guidepage.PAGE, encoding="utf-8") as f:
            self.assertEqual(f.read(), guidepage.build(),
                             "player-guide.html is behind PLAYER-GUIDE.md: run python -m dsloader.guidepage")

    def test_links_inside_the_page(self):
        page = guidepage.build()
        ids = set(re.findall(r' id="([^"]+)"', page))
        self.assertEqual(set(re.findall(r'href="#([^"]+)"', page)) - ids, set())

    def test_markdown(self):
        self.assertEqual(guidepage.inline("**A** *b* `c*d` [e](#f) \\* x"),
                         '<strong>A</strong> <em>b</em> <code>c*d</code> <a href="#f">e</a> * x')
        self.assertEqual(guidepage.slug("Kits' spell slots"), "kits-spell-slots")
        listed, _ = guidepage._list(["1. one", "   more", "", "   ![p](q.png)", "", "2. two", "  - sub"], 0)
        self.assertEqual(listed, '<ol><li><p>one more</p><p><img src="q.png" alt="p"></p></li>'
                                 '<li>two<ul><li>sub</li></ul></li></ol>')
        page = guidepage.build()
        self.assertNotIn("**", page)
        self.assertNotIn("](", page)


if __name__ == "__main__":
    unittest.main()
