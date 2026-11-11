"""The manual (manual.py): each page up to date with its Markdown, every link landing on a file of
the release zip and an anchor that page has, no two ids the same on a page, the Help button's page,
and the Markdown the pages use coming out as HTML."""

import ast
import os
import re
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import guidepage, manual  # noqa: E402

HERE = manual.HERE
MADE = "the manual is behind its Markdown: run python -m dsloader.manual (in obsidian-edition)"


def read(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def ids(page: str) -> list:
    return re.findall(r' id="([^"]+)"', page)


def shown(page: str) -> str:
    """The page's text as a reader sees it: no tags, no code."""
    body = page[page.index("<body>"):]
    body = re.sub(r"<pre>.*?</pre>|<code>.*?</code>", "", body, flags=re.S)
    return re.sub(r"<[^>]+>", " ", body)


@unittest.skipUnless(os.path.exists(os.path.join(manual.ROOT, "PATCH-NOTES.md")), "the patch notes (the repository's root)")
class ManualPagesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.made = manual.outputs()
        cls.pages = {os.path.basename(p): t for p, t in cls.made.items() if p.endswith(".html")}

    def test_up_to_date(self):
        """Each page (and the style they share) is what its Markdown makes now."""
        for path, text in self.made.items():
            with self.subTest(page=os.path.basename(path)):
                self.assertTrue(os.path.exists(path), f"{path} is missing: {MADE}")
                self.assertEqual(read(path), text, f"{os.path.relpath(path, HERE)}: {MADE}")
        extra = set(os.listdir(manual.MANUAL)) - {os.path.basename(p) for p in self.made}
        self.assertEqual(extra, set(), "files in manual/ the manual doesn't make")

    def test_every_page(self):
        """The ten pages, the start page first, each from its Markdown, each with the bar of all ten
        (itself marked) and its own index; the spoiler pages marked so in the bar."""
        self.assertEqual(manual.PAGES[0][0], "index.html")
        self.assertEqual(len(manual.PAGES), 10)
        for page, source, name, _ in manual.PAGES:
            self.assertTrue(os.path.exists(os.path.join(manual.ROOT, source)), source)
            html = self.pages[page]
            with self.subTest(page=page):
                bar = html[html.index('<nav class="manual"'):html.index("</nav>")]
                for other, _, _, _ in manual.PAGES:
                    self.assertIn(f'href="{other}"', bar)
                self.assertEqual(re.findall(r'href="([^"]+)" aria-current="page"', bar), [page])
                self.assertIn('<nav class="index" id="contents"', html)
                self.assertIn(f'<link rel="stylesheet" href="{manual.CSS}">', html)
        bar = self.pages["index.html"]
        for page in ("items.html", "creatures.html"):
            self.assertRegex(bar, re.escape(f'href="{page}"') + r'>[^<]+</a> <span class="spoil">\(spoilers\)')
        self.assertRegex(bar, r'href="game-bugs.html">[^<]+</a> <span class="spoil">\(some spoilers\)')
        for page in ("items.html", "game-bugs.html"):  # (the pages' own warnings, at their top)
            intro = self.pages[page].split('<div class="intro">', 1)[1].split("</header>", 1)[0]
            self.assertIn("Spoilers:", intro)

    def test_links_land(self):
        """Every relative link and picture is a file of the release zip (inside obsidian-edition), a
        page's anchor is one that page has, no link is to a Markdown file of its own, and no page has
        two ids the same."""
        anchors = {page: set(ids(html)) for page, html in self.pages.items()}
        bad = []
        for page, html in self.pages.items():
            dup = sorted({i for i in ids(html) if ids(html).count(i) > 1})
            if dup:
                bad.append(f"{page}: ids twice: {dup}")
            for target in re.findall(r'(?:href|src)="([^"]+)"', html):
                target = target.replace("&amp;", "&")
                if re.match(r"^[a-z]+:", target):
                    continue
                name, _, frag = target.partition("#")
                if name.endswith(".md"):
                    bad.append(f"{page}: {target} (a Markdown file)")
                    continue
                dest = os.path.normpath(os.path.join(manual.MANUAL, name)) if name else os.path.join(manual.MANUAL, page)
                if not dest.startswith(HERE + os.sep):
                    bad.append(f"{page}: {target} (outside the zip)")
                elif not os.path.exists(dest) and not name.endswith(".html"):
                    bad.append(f"{page}: {target} (no file)")
                elif name.endswith(".html") and os.path.basename(dest) not in self.pages:
                    bad.append(f"{page}: {target} (no such page)")
                elif frag and frag not in anchors[os.path.basename(dest) if name else page]:
                    bad.append(f"{page}: {target} (no anchor)")
        self.assertEqual(bad, [])

    def test_links_between_pages(self):
        """A link to another of the pages goes to its HTML file, the anchor kept; to a development
        page, its GitHub address."""
        guide, start = self.pages["player-guide.html"], self.pages["index.html"]
        self.assertIn('href="kits.html#', guide)
        self.assertIn('href="index.html#running-it-windows"', guide)
        self.assertIn('href="player-guide.html#glossary"', start)
        self.assertIn('href="changes.html"', start)  # (the patch notes, by their GitHub address)
        self.assertIn('href="items.html#every-magic-item"', self.pages["changes.html"])
        self.assertIn(f'href="{manual.DOCS}DEVELOPMENT-RULES.md#', self.pages["features.html"])
        self.assertIn('src="../docs/creatures/', self.pages["creatures.html"])

    def test_markdown_comes_out(self):
        """No Markdown left showing on any page: bold, links, table rows, headings, escapes."""
        for page, html in self.pages.items():
            text = shown(html)
            with self.subTest(page=page):
                for left in ("**", "](", "|---", "\x00", "\\*", "\\|", "&lt;http"):
                    self.assertNotIn(left, text)
                self.assertIsNone(re.search(r"^\s*#{1,6} ", text, re.M))
                self.assertIsNone(re.search(r"(^|\s)\|\s.*\s\|(\s|$)", text, re.M), "a table not made")

    def test_changes(self):
        """The patch notes in the manual: their tags, the old values and the developers' notes, as on
        the root's page."""
        page = self.pages["changes.html"]
        self.assertIn('<span class="tag new">New</span>', page)
        self.assertIn('<span class="was">(was 10)</span>', page)
        self.assertIn('<div class="dev"><b>Developers\' Notes</b>', page)
        self.assertNotIn("github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/KITS.md", page)


class HelpButtonTests(unittest.TestCase):
    def test_help_opens_the_start_page(self):
        """The Loader's Help button opens manual/index.html (viewer.HELP_PAGE, manual.START): read
        from viewer.py's source, so this runs without tkinter."""
        self.assertEqual(manual.START, os.path.join(HERE, "manual", "index.html"))
        self.assertTrue(os.path.isfile(manual.START))
        tree = ast.parse(read(os.path.join(HERE, "dsloader", "viewer.py")))
        assigned = {t.id: node.value for node in tree.body if isinstance(node, ast.Assign)
                    for t in node.targets if isinstance(t, ast.Name)}
        value = assigned.get("HELP_PAGE")
        self.assertIsInstance(value, ast.Attribute)
        self.assertEqual((value.value.id, value.attr), ("manual", "START"))
        self.assertFalse(os.path.exists(os.path.join(HERE, "player-guide.html")))  # (now in manual/)

    def test_old_name(self):
        """python -m dsloader.guidepage still writes the manual."""
        self.assertIs(guidepage.write, manual.write)
        self.assertTrue(callable(guidepage.main))


class MarkdownTests(unittest.TestCase):
    def test_inline(self):
        self.assertEqual(manual.inline("**A** *b* `c*d` [e](#f) \\* x"),
                         '<strong>A</strong> <em>b</em> <code>c*d</code> <a href="#f">e</a> * x')
        self.assertEqual(manual.inline("***T*** and <https://a.b/c>"),
                         '<strong><em>T</em></strong> and <a href="https://a.b/c">https://a.b/c</a>')
        self.assertEqual(manual.inline("a < b & `<v>`"), "a &lt; b &amp; <code>&lt;v&gt;</code>")

    def test_title_escaped_once(self):
        """A heading's "&" is "&amp;" once in the page's <title>, not "&amp;amp;"."""
        page = manual._page("index.html", "README.md", manual.inline("AD&D rules"), "", "", "", "x")
        self.assertIn("<title>AD&amp;D rules ·", page)
        self.assertEqual(manual.slug("Kits' spell slots"), "kits-spell-slots")
        self.assertEqual(manual.slug("AD&D's [table](x.md)"), "adds-table")

    def test_lists(self):
        listed, _ = manual._list(["1. one", "   more", "", "   ![p](q.png)", "", "2. two", "  - sub"], 0)
        self.assertEqual(listed, '<ol><li><p>one more</p><p><img src="q.png" alt="p"></p></li>'
                                 '<li>two<ul><li>sub</li></ul></li></ol>')
        listed, _ = manual._list(["- a:", "", "  | x | y |", "  |---|---|", "  | 1 | 2 |", "",
                                  "  after", "- b", "lazy"], 0)
        self.assertEqual(listed, '<ul><li><p>a:</p><div class="tablewrap"><table><thead><tr><th>x</th><th>y</th>'
                                 '</tr></thead><tbody><tr><td>1</td><td>2</td></tr></tbody></table></div>'
                                 '<p>after</p></li><li>b lazy</li></ul>')
        listed, _ = manual._list(["3. c", "4. d"], 0)
        self.assertTrue(listed.startswith('<ol start="3">'))

    def test_blocks(self):
        self.assertEqual(manual._blocks(["```", "# not a heading", "a <b>", "```"]),
                         ["<pre><code># not a heading\na &lt;b&gt;</code></pre>"])
        self.assertEqual(manual._blocks(["> one", ">", "> *two*"]),
                         ["<blockquote><p>one</p><p><em>two</em></p></blockquote>"])
        self.assertEqual(manual._blocks(["text", "1993. on"]), ["<p>text 1993. on</p>"])
        self.assertEqual(manual._blocks(["| a | `b\\|c` |", "|---|:-:|", "| 1 | 2 |"]),
                         ['<div class="tablewrap"><table><thead><tr><th>a</th><th style="text-align: center">'
                          '<code>b|c</code></th></tr></thead><tbody><tr><td>1</td><td style="text-align: center">2</td>'
                          '</tr></tbody></table></div>'])

    def test_page(self):
        """GitHub's anchors, a repeated heading's with -1; the Contents section left out (the index is
        that); a heading inside code isn't one."""
        page = manual.Page("# T\n\nOpening.\n\n## Contents\n\n- [A](#a)\n\n## A\n\n### Same\n\n## B\n\n"
                           "### Same\n\n```\n## code\n```\n")
        self.assertEqual(page.title, "T")
        self.assertEqual(page.opening, "<p>Opening.</p>")
        self.assertEqual(page.sections, [("a", "A", [("same", "Same")]), ("b", "B", [("same-1", "Same")])])
        self.assertNotIn("Contents", page.body)
        self.assertIn("<pre><code>## code</code></pre>", page.body)

    def test_links(self):
        to = manual.linker("obsidian-edition/PLAYER-GUIDE.md")
        self.assertEqual(to("KITS.md#thief-kits"), "kits.html#thief-kits")
        self.assertEqual(to("README.md"), "index.html")
        self.assertEqual(to("PLAYER-GUIDE.md#glossary"), "#glossary")
        self.assertEqual(to("../PATCH-NOTES.md#combat"), "changes.html#combat")
        self.assertEqual(to(manual.BLOB + "PATCH-NOTES.md"), "changes.html")
        self.assertEqual(to(manual.DOCS + "ITEMS.md#x"), "items.html#x")
        self.assertEqual(to("docs/combat-log.png"), "../docs/combat-log.png")
        self.assertEqual(to("DEVELOPMENT.md#build"), manual.DOCS + "DEVELOPMENT.md#build")
        self.assertEqual(to("../CHANGELOG.md"), manual.BLOB + "CHANGELOG.md")
        self.assertEqual(to("https://example.org/x.md"), "https://example.org/x.md")
        self.assertEqual(to("#a"), "#a")
        notes = manual.linker("PATCH-NOTES.md")
        self.assertEqual(notes("patch-notes.html"), "changes.html")
        self.assertEqual(notes("obsidian-edition/KITS.md"), "kits.html")
        self.assertEqual(manual.href("KITS.md#x"), manual.DOCS + "KITS.md#x")  # (outside the manual)


if __name__ == "__main__":
    unittest.main()
