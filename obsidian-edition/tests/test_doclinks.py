"""The documentation's links: every relative link and anchor goes somewhere, and every README or
features page section that DEVELOPMENT.md explains links to its explanation."""

import collections
import glob
import os
import re
import unittest

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # obsidian-edition
REPO = os.path.dirname(HERE)


def slug(heading: str) -> str:
    """GitHub's anchor for a heading."""
    text = re.sub(r"[*`_]", "", heading).strip().lower()
    return re.sub(r"[^\w\- ]", "", text).replace(" ", "-")


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

    def test_readme_links_how_it_works(self):
        """DEVELOPMENT's "How each part works" names README and features page sections by their
        headings; each such section links to its explanation."""
        dev = os.path.join(HERE, "DEVELOPMENT.md")
        with open(dev, encoding="utf-8") as f:
            text = f.read()
        part = text[text.index("## How each part works"):]
        explained = {h: slug(h) for h in re.findall(r"^### (.+)$", part, re.M)}
        missing = [heading for page in ("README.md", "FEATURES.md")
                   for heading, body in sections(os.path.join(HERE, page))
                   if heading in explained and f"DEVELOPMENT.md#{explained[heading]}" not in body]
        self.assertEqual(missing, [])


if __name__ == "__main__":
    unittest.main()
