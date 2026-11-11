"""The manual: the player's pages as web pages that link to each other, in obsidian-edition/manual/,
for the release zip. Each page is made from its Markdown, which stays the source (and reads the
same on GitHub): README.md is the start page (index.html), then the player's guide, the features
and rules, the kits, the items, the creatures, the game's bugs fixed, the dice log, how the original
game works, and the patch notes (../PATCH-NOTES.md, as changes.html). The Loader's Help button
opens the start page.

Every page shares the manual's bar of pages (the one on show marked, the spoiler pages marked so)
and the patch notes' look (pagestyle.css, with the fonts from pagefonts.py, in one manual.css the
pages share), and has its own index of its sections and their subsections. A link to another of
these pages goes to its HTML file with the same anchor (KITS.md#x is kits.html#x; the README is
index.html; the patch notes, here or by their GitHub address, changes.html); a picture goes to
../docs/; a link to anything else of the repository (the development pages, the changelog) goes to
its GitHub address. Headings have GitHub's anchors, a repeated one with -1, -2..., so the
Markdown's own links keep working.

`python -m dsloader.manual` (or `python -m dsloader.guidepage`, its older name) writes the whole
manual; tests/test_manual.py checks each page is up to date and that its links all land.

The Markdown the pages use: headings, paragraphs, lists (nested, numbered, loose, with tables,
pictures, code and paragraphs inside, and lazy continuation lines), tables (with pictures, and \\|
in a cell), fenced code, block quotes, pictures, links and <https://...> addresses, code, bold,
italic and both at once, and backslash escapes. The patch notes go through patchnotes.py, whose
tags and developers' notes they use."""

import collections
import html
import os
import re
from typing import Callable, Dict, List, Optional, Tuple

from . import pagefonts

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # obsidian-edition
ROOT = os.path.dirname(HERE)  # the repository
MANUAL = os.path.join(HERE, "manual")
START = os.path.join(MANUAL, "index.html")  # (what the Loader's Help button opens)
CSS = "manual.css"  # (the pages' shared style and fonts, beside them)
STYLE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pagestyle.css")
REPO = "https://github.com/daaki85/darksun-obsidian-edition"
BLOB = REPO + "/blob/main/"
DOCS = BLOB + "obsidian-edition/"

# (page, its Markdown from the repository's root, its name in the manual's bar, its spoiler mark)
PAGES = (
    ("index.html", "obsidian-edition/README.md", "Start here", ""),
    ("player-guide.html", "obsidian-edition/PLAYER-GUIDE.md", "Player's guide", ""),
    ("features.html", "obsidian-edition/FEATURES.md", "Features and rules", ""),
    ("kits.html", "obsidian-edition/KITS.md", "Kits", ""),
    ("items.html", "obsidian-edition/ITEMS.md", "Items", "spoilers"),
    ("creatures.html", "obsidian-edition/CREATURES.md", "Creatures", "spoilers"),
    ("game-bugs.html", "obsidian-edition/GAME-BUGS.md", "The game's bugs, fixed", "some spoilers"),
    ("dice-log.html", "obsidian-edition/DICE-LOG.md", "The dice log", ""),
    ("how-the-game-works.html", "obsidian-edition/HOW-THE-GAME-WORKS.md", "How the original game works", ""),
    ("changes.html", "PATCH-NOTES.md", "Changes from the original game", ""),
)
BY_SOURCE = {source: page for page, source, _, _ in PAGES}

EXTRA_STYLE = """
main { max-width: 80ch; }
ol { padding-left: 24px; margin: 6px 0; }
li > p { margin: 6px 0; }
main img { max-width: 100%; height: auto; image-rendering: pixelated; vertical-align: middle; }
main p > img, main li > img { display: block; margin: 12px 0; border: 1px solid var(--line); }
td img { image-rendering: pixelated; }
h5 { font: 700 15px var(--font-body); margin: 14px 0 4px; }
.banner .intro > p { max-width: 64ch; font-size: 19px; margin: 18px 0; }
.banner .intro > p.meta { font-size: 14px; margin: 6px 0; }
.banner .intro em { color: var(--muted); }
.banner .intro ul { max-width: 64ch; }
pre { background: var(--panel); border: 1px solid var(--line); border-radius: 3px; padding: 10px 14px;
      overflow-x: auto; font-size: 14px; line-height: 1.45; margin: 12px 0; }
pre code { font-size: inherit; white-space: pre; }
blockquote { margin: 14px 0; padding: 4px 18px; border-left: 3px solid var(--sun-deep); background: var(--panel); }
blockquote p { margin: 8px 0; }
nav.manual { max-width: 1080px; margin: 0 auto; padding-block: 14px 10px; border-bottom: 1px solid var(--line);
             display: flex; flex-wrap: wrap; align-items: baseline; gap: 6px 18px; font-size: 15px; }
nav.manual .home { font-family: var(--font-display); font-size: 18px; color: var(--fg); text-decoration: none; margin-right: 6px; }
nav.manual ol { list-style: none; padding: 0; margin: 0; display: flex; flex-wrap: wrap; gap: 4px 16px; }
nav.manual li { margin: 0; }
nav.manual a { color: var(--fg); text-decoration: none; }
nav.manual a:hover { color: var(--sun); }
nav.manual a[aria-current="page"] { color: var(--sun); text-decoration: underline; text-decoration-thickness: 2px; }
nav.manual .spoil { color: var(--muted); font-size: 13px; }
.banner { padding-block: 40px 32px; }
nav.index { max-height: calc(100vh - 40px); overflow-y: auto; }
nav.index ol ol { gap: 3px; margin: 4px 0 4px 12px; font-size: 13px; }
@media (max-width: 900px) { nav.index { max-height: none; } nav.index ol ol { display: none; } }
"""


def slug(text: str) -> str:
    """GitHub's anchor for a heading: a link's text only, lower case, punctuation but hyphens gone,
    spaces hyphens (as tests/test_doclinks.py has it)."""
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"[`*_\[\]()]", "", text).strip().lower()
    return re.sub(r"[^\w\- ]", "", text).replace(" ", "-")


def href(target: str) -> str:
    """A link's target on a page outside the manual (the root's patch-notes.html): another of the
    mod's Markdown pages (KITS.md#...) is GitHub's copy, whose headings' anchors a browser can follow
    (a local .md opens as plain text, or not at all); anchors, pictures and web addresses as they are."""
    if re.match(r"^[A-Z][A-Z0-9-]*\.md(#|$)", target):
        return DOCS + target
    return target


def linker(source: str) -> Callable[[str], str]:
    """How a link on the manual's page made from SOURCE (a Markdown file, from the repository's root)
    goes: to another page of the manual, to a picture in ../docs/, or to GitHub."""
    page = BY_SOURCE.get(source)

    def to(target: str) -> str:
        if target.startswith("#"):
            return target
        path, hashed, frag = target.partition("#")
        frag = hashed + frag
        if path.startswith(BLOB):
            rel = path[len(BLOB):]
        elif re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", path):
            return target  # (any other web address, mailto)
        else:
            rel = os.path.normpath(os.path.join(os.path.dirname(source), path)).replace(os.sep, "/")
        if rel in BY_SOURCE:
            return frag if BY_SOURCE[rel] == page and frag else BY_SOURCE[rel] + frag
        if rel == "patch-notes.html":  # (the root's page: the manual has the notes itself)
            return BY_SOURCE["PATCH-NOTES.md"] + frag
        if path.startswith(BLOB):
            return target
        if rel.startswith("obsidian-edition/") and not rel.endswith(".md") \
                and os.path.exists(os.path.join(ROOT, rel)):
            return "../" + rel[len("obsidian-edition/"):] + frag  # (a picture, in the zip beside the manual)
        return BLOB + rel + frag
    return to


def inline(text: str, link: Optional[Callable[[str], str]] = None) -> str:
    """One line or paragraph of Markdown as HTML; LINK says where a link's target goes (href, for a
    page outside the manual)."""
    link = link or href
    out, keep_ = text, []

    def keep(fragment: str) -> str:
        keep_.append(fragment)
        return f"\x00{len(keep_) - 1}\x00"
    out = re.sub(r"(`+)(.+?)\1", lambda m: keep("<code>" + html.escape(m.group(2).strip(), quote=False) + "</code>"), out)
    out = re.sub(r"<(https?://[^>\s]+)>",
                 lambda m: keep(f'<a href="{html.escape(link(m.group(1)))}">{html.escape(m.group(1), quote=False)}</a>'),
                 out)
    out = re.sub(r"\\([\\`*_\[\]()#|!.<>{}+-])", lambda m: keep(html.escape(m.group(1), quote=False)), out)
    out = html.escape(out, quote=False)
    out = re.sub(r"!\[([^\]]*)\]\(([^)\s]+)\)",
                 lambda m: f'<img src="{html.escape(link(html.unescape(m.group(2))))}" alt="{html.escape(html.unescape(m.group(1)))}">', out)
    out = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)",
                 lambda m: f'<a href="{html.escape(link(html.unescape(m.group(2))))}">{m.group(1)}</a>', out)
    out = re.sub(r"\*\*\*(?!\s)(.+?)(?<!\s)\*\*\*", r"<strong><em>\1</em></strong>", out)
    out = re.sub(r"\*\*(?!\s)(.+?)(?<!\s)\*\*", r"<strong>\1</strong>", out)
    out = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", out)
    while "\x00" in out:
        out = re.sub(r"\x00(\d+)\x00", lambda m: keep_[int(m.group(1))], out)
    return out


ITEM = re.compile(r"^( *)([-*+]|\d+[.)]) +(.*)$")
FENCE = re.compile(r"^ *(```|~~~)")
HEADING = re.compile(r"^ {0,3}(#{1,6}) +(.*?)(?: +#+)? *$")
SEPARATOR = re.compile(r"^ *\|? *:?-+:? *(\| *:?-+:? *)*\|? *$")


def _indent(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def _table_at(lines: List[str], i: int) -> bool:
    return (lines[i].lstrip().startswith("|") and i + 1 < len(lines) and "-" in lines[i + 1]
            and bool(SEPARATOR.match(lines[i + 1])))


def _interrupts(lines: List[str], i: int) -> bool:
    """Whether line I ends a paragraph: a heading, code, a quote, a table, or a list (a numbered one
    only from 1, as GitHub has it, so a line that happens to start "1993. " doesn't)."""
    line = lines[i]
    m = ITEM.match(line)
    return bool(HEADING.match(line) or FENCE.match(line) or line.lstrip().startswith(">") or _table_at(lines, i)
                or (m and (not m.group(2)[0].isdigit() or m.group(2)[:-1] == "1")))


def _cells(line: str) -> List[str]:
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|") and not line.endswith("\\|"):
        line = line[:-1]
    return [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", line)]


def table(rows: List[str], link: Optional[Callable[[str], str]] = None) -> str:
    """A table's rows (its head, the separator, its body) as HTML."""
    aligns = []
    for c in _cells(rows[1]):
        aligns.append(' style="text-align: center"' if c.startswith(":") and c.endswith(":")
                      else ' style="text-align: right"' if c.endswith(":") else "")
    width = len(_cells(rows[0]))
    aligns += [""] * width

    def row(line: str, tag: str) -> str:
        cells = (_cells(line) + [""] * width)[:width]
        return "<tr>" + "".join(f"<{tag}{a}>{inline(c, link)}</{tag}>" for c, a in zip(cells, aligns)) + "</tr>"
    return ('<div class="tablewrap"><table><thead>' + row(rows[0], "th") + "</thead><tbody>"
            + "".join(row(r, "td") for r in rows[2:]) + "</tbody></table></div>")


def _list(lines: List[str], i: int, link: Optional[Callable[[str], str]] = None) -> Tuple[str, int]:
    """The list starting at line I (and any nested in it): its HTML, and the line after it. An item
    of more than one paragraph (a blank line inside it) has each in <p>; one of one paragraph, its
    text alone."""
    first = ITEM.match(lines[i])
    base = len(first.group(1))
    ordered = first.group(2)[0].isdigit()
    start = int(first.group(2)[:-1]) if ordered else 1
    items: List[str] = []
    while i < len(lines):
        m = ITEM.match(lines[i])
        if not m or len(m.group(1)) != base or m.group(2)[0].isdigit() != ordered:
            break
        content = len(lines[i]) - len(m.group(3))  # (where the item's text starts)
        own, i, text = [m.group(3)], i + 1, True  # (text: the last line was a paragraph's)
        while i < len(lines):
            line = lines[i]
            if not line.strip():
                nxt = next((j for j in range(i + 1, len(lines)) if lines[j].strip()), None)
                if nxt is None:
                    break
                sub = ITEM.match(lines[nxt])
                if _indent(lines[nxt]) < content and not (sub and len(sub.group(1)) > base):
                    break
                own.append("")
                i, text = i + 1, False
                continue
            indent = _indent(line)
            sub = ITEM.match(line)
            if indent >= content or (sub and indent > base):
                own.append(line[min(indent, content):])
                text = not (FENCE.match(line) or sub)
                i += 1
                continue
            if sub or not text or _interrupts(lines, i):
                break
            own.append(line.strip())  # (a lazy line: the paragraph goes on)
            i += 1
        while own and not own[-1].strip():
            own.pop()
        parts = _blocks(own, link)
        if "" not in own:  # (one paragraph, and any list under it: no <p>)
            parts = [p[3:-4] if p.startswith("<p>") and p.endswith("</p>") else p for p in parts]
        items.append("<li>" + "".join(parts) + "</li>")
        nxt = next((j for j in range(i, len(lines)) if lines[j].strip()), None)
        if nxt is not None and nxt > i:  # (a blank line between items)
            m2 = ITEM.match(lines[nxt])
            if m2 and len(m2.group(1)) == base and m2.group(2)[0].isdigit() == ordered:
                i = nxt
    tag = "ol" if ordered else "ul"
    opening = f'<ol start="{start}">' if ordered and start != 1 else f"<{tag}>"
    return opening + "".join(items) + f"</{tag}>", i


def _blocks(lines: List[str], link: Optional[Callable[[str], str]] = None) -> List[str]:
    """Lines of Markdown with no headings of their own (a section's text, a list item's, a quote's)
    as HTML blocks."""
    out: List[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        fence = FENCE.match(line)
        if fence:
            indent, code = _indent(line), []
            i += 1
            while i < len(lines) and not (FENCE.match(lines[i]) and lines[i].strip().startswith(fence.group(1))):
                code.append(lines[i][indent:] if not lines[i][:indent].strip() else lines[i].lstrip())
                i += 1
            i += 1
            out.append("<pre><code>" + html.escape("\n".join(code), quote=False) + "</code></pre>")
            continue
        if _table_at(lines, i):
            rows = []
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                rows.append(lines[i])
                i += 1
            out.append(table(rows, link))
            continue
        if line.lstrip().startswith(">"):
            quoted = []
            while i < len(lines) and lines[i].lstrip().startswith(">"):
                quoted.append(re.sub(r"^ *> ?", "", lines[i]))
                i += 1
            out.append("<blockquote>" + "".join(_blocks(quoted, link)) + "</blockquote>")
            continue
        if ITEM.match(line):
            listed, i = _list(lines, i, link)
            out.append(listed)
            continue
        heading = HEADING.match(line)
        if heading:  # (one inside a list or a quote: a paragraph in bold)
            out.append(f"<p><strong>{inline(heading.group(2), link)}</strong></p>")
            i += 1
            continue
        para = [line.strip()]
        i += 1
        while i < len(lines) and lines[i].strip() and not _interrupts(lines, i):
            para.append(lines[i].strip())
            i += 1
        out.append(f"<p>{inline(' '.join(para), link)}</p>")
    return out


class Page:
    """A Markdown page taken apart: its title, its opening (the blocks before its first section), its
    body, and its sections with their subsections [(anchor, title, [(anchor, title)])] for the index."""

    def __init__(self, markdown: str, link: Optional[Callable[[str], str]] = None):
        self.title, self.opening, self.sections = "", "", []
        seen: Dict[str, int] = collections.Counter()
        out: List[str] = []
        chunk: List[str] = []
        skipping, in_section, fence = False, False, None

        def flush():
            if chunk and not skipping:
                blocks = "\n".join(_blocks(chunk, link))
                if not in_section and not out:
                    self.opening += blocks
                else:
                    out.append(blocks)
            chunk.clear()

        for line in markdown.splitlines():
            if fence is None:
                f = FENCE.match(line)
                if f:
                    fence = f.group(1)
            elif line.strip().startswith(fence):
                fence = None
                chunk.append(line)
                continue
            heading = HEADING.match(line) if fence is None and not _indent(line) else None
            if not heading:
                chunk.append(line)
                continue
            flush()
            level, text = len(heading.group(1)), heading.group(2).strip()
            anchor = slug(text)
            if seen[anchor]:  # (GitHub's: a heading's anchor taken before gets -1, -2, ...)
                anchor, seen[anchor] = f"{anchor}-{seen[anchor]}", seen[anchor] + 1
            else:
                seen[anchor] += 1
            if level == 1:
                self.title = self.title or text
                continue
            if level == 2:
                skipping = text == "Contents"  # (the page's index takes its place)
                if skipping:
                    continue
                if in_section:
                    out.append("</section>")
                in_section = True
                self.sections.append((anchor, text, []))
                out.append(f'<section>\n<h2 id="{anchor}">{inline(text, link)}</h2>')
                continue
            if skipping:
                continue
            if level == 3 and self.sections:
                self.sections[-1][2].append((anchor, text))
            out.append(f'<h{level} id="{anchor}">{inline(text, link)}</h{level}>')
        flush()
        if in_section:
            out.append("</section>")
        self.body = "\n".join(out)


def style() -> str:
    """The manual's style: the fonts, the patch notes' style (pagestyle.css), and what the manual adds."""
    with open(STYLE, encoding="utf-8") as f:
        return pagefonts.faces() + f.read() + EXTRA_STYLE


def _bar(current: str) -> str:
    links = []
    for page, _, name, spoilers in PAGES:
        mark = ' aria-current="page"' if page == current else ""
        note = f' <span class="spoil">({spoilers})</span>' if spoilers else ""
        links.append(f'<li><a href="{page}"{mark}>{html.escape(name)}</a>{note}</li>')
    return ('<nav class="manual" aria-label="The manual\'s pages">\n'
            '  <a class="home" href="index.html">Obsidian Edition manual</a>\n'
            f'  <ol>{"".join(links)}</ol>\n</nav>')


def _index(sections, link) -> str:
    return "".join(f'<li><a href="#{a}">{inline(t, link)}</a>'
                   + ("<ol>" + "".join(f'<li><a href="#{sa}">{inline(st, link)}</a></li>' for sa, st in sub) + "</ol>"
                      if sub else "") + "</li>"
                   for a, t, sub in sections)


def _page(current: str, source: str, title: str, opening: str, index: str, content: str, label: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(html.unescape(re.sub(r"<[^>]+>", " ", title)))} · Obsidian Edition manual</title>
<!-- Made from {source} by obsidian-edition/dsloader/manual.py: edit the Markdown, then run python -m dsloader.manual -->
<link rel="stylesheet" href="{CSS}">
</head>
<body>
{_bar(current)}
<header class="banner">
  <div class="eyebrow">Dark Sun: Shattered Lands · Obsidian Edition</div>
  <h1>{title}</h1>
  <div class="intro">{opening}</div>
</header>
<div class="wrap">
  <nav class="index" id="contents" aria-label="Contents">
    <p>{label}</p>
    <ol>{index}</ol>
  </nav>
  <main>
{content}
  </main>
</div>
<footer>
  <p>Made from <code>{os.path.basename(source)}</code>, which reads the same on <a href="{BLOB}{source}">GitHub</a>. Obsidian Edition runs on Windows with the GOG release of Dark Sun: Shattered Lands, in DOSBox. <a href="index.html">The manual's start page</a> · <a href="{REPO}/releases/latest">The latest release</a> · <a href="{REPO}">The project on GitHub</a></p>
</footer>
</body>
</html>
"""


def _heading(title: str) -> str:
    """The page's title for its banner: the Markdown's own, without "Obsidian Edition: " before it."""
    name = re.sub(r"^Obsidian Edition: ", "", title)
    return inline(name[:1].upper() + name[1:])


def _changes(source: str) -> str:
    """The patch notes in the manual (patchnotes.py's reading of them, tags and all)."""
    from . import patchnotes
    link = linker(source)
    with open(os.path.join(ROOT, source), encoding="utf-8") as f:
        content, sections, head = patchnotes.body(f.read(), link)
    opening = "".join([f'<p class="meta">{html.escape(head["subtitle"])}</p>']
                      + [f'<p class="meta">{s}</p>' for s in head["status"]] + [f'<p>{head["lede"]}</p>'])
    return _page("changes.html", source, _heading(head["title"]), opening,
                 _index([(a, t, []) for a, t in sections], link), content, "In these notes")


def build(page: str) -> str:
    """The manual's page PAGE (index.html, kits.html, ...) as HTML."""
    source = next(s for p, s, _, _ in PAGES if p == page)
    if source == "PATCH-NOTES.md":
        return _changes(source)
    link = linker(source)
    with open(os.path.join(ROOT, source), encoding="utf-8") as f:
        parsed = Page(f.read(), link)
    return _page(page, source, _heading(parsed.title), parsed.opening, _index(parsed.sections, link),
                 parsed.body, "On this page")


def outputs() -> Dict[str, str]:
    """Every file of the manual (each page, and the shared style), by its path, with its text."""
    out = {os.path.join(MANUAL, page): build(page) for page, _, _, _ in PAGES}
    out[os.path.join(MANUAL, CSS)] = ("/* Made by obsidian-edition/dsloader/manual.py from pagestyle.css and the fonts "
                                      "(pagefonts.py): run python -m dsloader.manual */\n" + style())
    return out


def write() -> None:
    os.makedirs(MANUAL, exist_ok=True)
    for path, text in outputs().items():
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)


def main() -> None:
    write()
    for page, _, _, _ in PAGES:
        print(os.path.join(MANUAL, page))


if __name__ == "__main__":
    main()
