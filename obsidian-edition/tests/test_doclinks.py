"""The documentation's links: every relative link and anchor goes somewhere, and every README or
features page section that DEVELOPMENT.md explains links to its explanation."""

import collections
import fnmatch
import glob
import os
import re
import unittest

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # obsidian-edition
REPO = os.path.dirname(HERE)


def slug(heading: str) -> str:
    """GitHub's anchor for a heading."""
    heading = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", heading)  # (a link: its text, as GitHub's anchor has it)
    text = re.sub(r"[*`_]", "", heading).strip().lower()
    return re.sub(r"[^\w\- ]", "", text).replace(" ", "-")


def export_ignored() -> list:
    """The patterns obsidian-edition/.gitattributes leaves out of the release zip (export-ignore)."""
    with open(os.path.join(HERE, ".gitattributes"), encoding="utf-8") as f:
        return [line.split()[0] for line in f if re.match(r"^[^#\s]\S*\s.*\bexport-ignore\b", line)]


def ships(path: str) -> bool:
    """Whether the file at PATH (in obsidian-edition) goes into the release zip."""
    rel = os.path.relpath(path, HERE).replace(os.sep, "/")
    for pattern in export_ignored():
        name = pattern.lstrip("/")
        if fnmatch.fnmatchcase(rel, name) or rel.startswith(name + "/"):
            return False
    return True


def anchors(path: str) -> set:
    seen, out = collections.Counter(), set()
    with open(path, encoding="utf-8") as f:
        for line in f:
            m = re.match(r"^#+\s+(.*)", line)
            if m:
                s = slug(m.group(1))
                out.add(s if not seen[s] else f"{s}-{seen[s]}")
                seen[s] += 1
    return out


def sections(path: str):
    """(heading, text) for each heading of level 2 to 4, its text up to the next heading."""
    with open(path, encoding="utf-8") as f:
        text = f.read()
    parts = re.split(r"\n(?=#{2,4} )", text)
    return [(p.split("\n", 1)[0].lstrip("#").strip(), p) for p in parts if p.startswith("#")]


def doc_files():
    out = [os.path.join(REPO, f) for f in ("README.md", "CHANGELOG.md", "PATCH-NOTES.md")]
    out += glob.glob(os.path.join(REPO, "release-notes", "*.md"))
    out += glob.glob(os.path.join(HERE, "*.md"))
    return [f for f in out if os.path.exists(f)]


class DocLinkTests(unittest.TestCase):
    def test_links_resolve(self):
        """Every relative link names a file that's there, and an anchor that heading has."""
        found = {}
        bad = []
        for path in doc_files():
            with open(path, encoding="utf-8") as f:
                for n, line in enumerate(f, 1):
                    for target in re.findall(r"\]\(([^)\s]+)\)", line):
                        if target.startswith(("http", "mailto")):
                            continue
                        name, _, frag = target.partition("#")
                        dest = os.path.normpath(os.path.join(os.path.dirname(path), name)) if name else path
                        if not os.path.exists(dest):
                            bad.append(f"{os.path.relpath(path, REPO)}:{n} {target} (no file)")
                        elif frag and dest.endswith(".md"):
                            if dest not in found:
                                found[dest] = anchors(dest)
                            if frag not in found[dest]:
                                bad.append(f"{os.path.relpath(path, REPO)}:{n} {target} (no anchor)")
        self.assertEqual(bad, [])

    def test_shipped_pages_stay_in_the_zip(self):
        """The release zip holds the obsidian-edition folder alone, less what its .gitattributes marks
        export-ignore (the developer pages, tests/, docs/viewer.png): the shipped pages' relative
        links never leave it (what is outside goes by its GitHub address), and the GitHub links to
        files of the repository name files that are there. A shipped page's relative link to a
        developer page is let be: the manual, the zip's readable copy, sends it to GitHub at the
        release's tag."""
        self.assertEqual(export_ignored(), ["/DEVELOPMENT*.md", "/tests", "docs/viewer.png"])
        bad = []
        base = re.compile(r"https://github\.com/daaki85/darksun-obsidian-edition/blob/(?:main|v[0-9.]+)/")
        pages = glob.glob(os.path.join(HERE, "*.md")) + glob.glob(os.path.join(HERE, "docs", "**", "*.md"), recursive=True)
        for path in pages:
            if not ships(path):
                continue
            with open(path, encoding="utf-8") as f:
                for n, line in enumerate(f, 1):
                    for target in re.findall(r"\]\(([^)\s]+)\)", line):
                        rel = os.path.relpath(path, REPO)
                        github = base.match(target)
                        if github:
                            name = target[github.end():].partition("#")[0]
                            if name and not os.path.exists(os.path.join(REPO, name)):
                                bad.append(f"{rel}:{n} {target} (no such file in the repository)")
                        elif not target.startswith(("http", "mailto", "#")):
                            dest = os.path.normpath(os.path.join(os.path.dirname(path), target.partition("#")[0]))
                            if not dest.startswith(HERE + os.sep) and dest != HERE:
                                bad.append(f"{rel}:{n} {target} (outside the zip)")
                            elif not ships(dest) and not re.match(r"DEVELOPMENT[A-Z-]*\.md$", os.path.basename(dest)):
                                bad.append(f"{rel}:{n} {target} (left out of the zip)")
        self.assertEqual(bad, [])

    def test_readme_links_how_it_works(self):
        """The development pages on how each part works (DEVELOPMENT-INTERNALS, -SCREENS, -RULES, -KITS
        and -CONTENT)
        name sections of the README, the features page and the pages split from it (items, kits, the
        game's bugs, how the game works) by their headings; each such section links to its
        explanation, on the page that has it."""
        explained = {}
        for page in ("DEVELOPMENT-INTERNALS.md", "DEVELOPMENT-SCREENS.md", "DEVELOPMENT-RULES.md",
                     "DEVELOPMENT-KITS.md", "DEVELOPMENT-CONTENT.md"):
            with open(os.path.join(HERE, page), encoding="utf-8") as f:
                for h in re.findall(r"^## (.+)$", f.read(), re.M):
                    if h != "Contents":
                        explained[h] = f"{page}#{slug(h)}"
        explained["Kits"] = "DEVELOPMENT-KITS.md"  # (the rules' "Kits" is a stub: the kits have their own page)
        self.assertGreater(len(explained), 60)
        missing = [heading for page in ("README.md", "FEATURES.md", "ITEMS.md", "KITS.md",
                                        "GAME-BUGS.md", "HOW-THE-GAME-WORKS.md")
                   for heading, body in sections(os.path.join(HERE, page))
                   if heading in explained and explained[heading] not in body]
        self.assertEqual(missing, [])

if __name__ == "__main__":
    unittest.main()
