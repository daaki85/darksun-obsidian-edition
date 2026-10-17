"""The player's guide as a web page: PLAYER-GUIDE.md made player-guide.html, in the patch notes'
look (its style read from ../patch-notes.html), with the guide's sections as the index.

`python -m dsloader.guidepage` writes it; tests/test_guidepage.py checks it is up to date. Only
the Markdown the guide uses: headings, paragraphs, lists (nested, numbered, with images and
paragraphs inside), tables, images, links, code, bold and italic, and backslash escapes."""

import html
import os
import re
from typing import List, Tuple

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GUIDE = os.path.join(HERE, "PLAYER-GUIDE.md")
PAGE = os.path.join(HERE, "player-guide.html")
PATCH_NOTES = os.path.join(os.path.dirname(HERE), "patch-notes.html")

EXTRA_STYLE = """
main { max-width: 80ch; }
ol { padding-left: 24px; margin: 6px 0; }
li > p { margin: 6px 0; }
main img { max-width: 100%; height: auto; image-rendering: pixelated; vertical-align: middle; }
main p > img, main li > img { display: block; margin: 12px 0; border: 1px solid var(--line); }
td img { image-rendering: pixelated; }
h5 { font: 700 15px var(--font-body); margin: 14px 0 4px; }
.lede em { color: var(--muted); }
"""


def slug(text: str) -> str:
    """GitHub's anchor for a heading: lower case, punctuation but hyphens gone, spaces hyphens."""
    text = re.sub(r"[`*_\[\]()]", "", text).lower()
    return re.sub(r"[^\w\- ]", "", text).replace(" ", "-")


def inline(text: str) -> str:
    """One line or paragraph of Markdown as HTML."""
    out, codes = text, []

    def keep(m):
        codes.append("<code>" + html.escape(m.group(1), quote=False) + "</code>")
        return f"\x00{len(codes) - 1}\x00"
    out = re.sub(r"`([^`]+)`", keep, out)
    escapes = []

    def escaped(m):
        escapes.append(html.escape(m.group(1), quote=False))
        return f"\x01{len(escapes) - 1}\x01"
    out = re.sub(r"\\([\\`*_\[\]()#|!.-])", escaped, out)
    out = html.escape(out, quote=False)
    out = re.sub(r"!\[([^\]]*)\]\(([^)\s]+)\)",
                 lambda m: f'<img src="{html.escape(m.group(2))}" alt="{html.escape(m.group(1))}">', out)
    out = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", lambda m: f'<a href="{html.escape(m.group(2))}">{m.group(1)}</a>', out)
    out = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", out)
    out = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", out)
    out = re.sub(r"\x01(\d+)\x01", lambda m: escapes[int(m.group(1))], out)
    return re.sub(r"\x00(\d+)\x00", lambda m: codes[int(m.group(1))], out)


ITEM = re.compile(r"^( *)([-*]|\d+\.) (.*)$")


def _indent(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def _list(lines: List[str], i: int) -> Tuple[str, int]:
    """The list starting at line I (and any nested in it): its HTML, and the line after it."""
    first = ITEM.match(lines[i])
    base = len(first.group(1))
    tag = "ol" if first.group(2)[0].isdigit() else "ul"
    items: List[str] = []
    while i < len(lines):
        m = ITEM.match(lines[i])
        if not m or len(m.group(1)) != base:
            break
        content = base + len(m.group(2)) + 1  # (where the item's text starts)
        body, para, i = [], [m.group(3)], i + 1
        while i < len(lines):
            line = lines[i]
            if not line.strip():
                nxt = next((j for j in range(i + 1, len(lines)) if lines[j].strip()), None)
                if nxt is None or _indent(lines[nxt]) < content:
                    break
                body.append(("p", " ".join(para)))
                para, i = [], nxt
                continue
            sub = ITEM.match(line)
            if sub and len(sub.group(1)) > base:
                if para:
                    body.append(("p", " ".join(para)))
                    para = []
                nested, i = _list(lines, i)
                body.append(("html", nested))
                continue
            if _indent(line) <= base and (ITEM.match(line) or not para):
                break
            para.append(line.strip())
            i += 1
        if para:
            body.append(("p", " ".join(para)))
        paras = [b for b in body if b[0] == "p"]
        parts = []
        for kind, text in body:
            if kind == "html":
                parts.append(text)
            elif len(paras) > 1:
                parts.append(f"<p>{inline(text)}</p>")
            else:
                parts.append(inline(text))
        items.append("<li>" + "".join(parts) + "</li>")
        while i < len(lines) and not lines[i].strip():  # (a blank line between items)
            nxt = next((j for j in range(i, len(lines)) if lines[j].strip()), None)
            m2 = ITEM.match(lines[nxt]) if nxt is not None else None
            if m2 and len(m2.group(1)) == base:
                i = nxt
            break
    return f"<{tag}>" + "".join(items) + f"</{tag}>", i


def _cells(line: str) -> List[str]:
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|") and not line.endswith("\\|"):
        line = line[:-1]
    return [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", line)]


def body(markdown: str) -> Tuple[str, List[Tuple[str, str]], str, str]:
    """The guide's HTML body, its sections [(anchor, title)], its title and its opening
    (the paragraphs before the first section)."""
    lines = markdown.splitlines()
    out: List[str] = []
    sections: List[Tuple[str, str]] = []
    title, lede, skipping = "", [], False
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        heading = re.match(r"^(#{1,6}) (.*)$", line)
        if heading:
            level, text = len(heading.group(1)), heading.group(2).strip()
            i += 1
            if level == 1:
                title = text
                continue
            skipping = level == 2 and text == "Contents"  # (the page's index takes its place)
            if skipping:
                continue
            if level == 2:
                if sections:
                    out.append("</section>")
                sections.append((slug(text), text))
                out.append(f'<section id="{slug(text)}">')
                out.append(f"<h2>{inline(text)}</h2>")
            else:
                out.append(f'<h{level} id="{slug(text)}">{inline(text)}</h{level}>')
            continue
        if skipping:
            i += 1
            continue
        if line.lstrip().startswith("|"):
            rows = []
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                rows.append(lines[i])
                i += 1
            head, rest = _cells(rows[0]), [r for r in rows[2:]]
            table = ["<div class=\"tablewrap\"><table><thead><tr>"
                     + "".join(f"<th>{inline(c)}</th>" for c in head) + "</tr></thead><tbody>"]
            for r in rest:
                table.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in _cells(r)) + "</tr>")
            out.append("".join(table) + "</tbody></table></div>")
            continue
        if ITEM.match(line):
            listed, i = _list(lines, i)
            out.append(listed)
            continue
        para = []
        while i < len(lines) and lines[i].strip() and not re.match(r"^#{1,6} ", lines[i]) \
                and not lines[i].lstrip().startswith("|") and not (para and ITEM.match(lines[i])):
            para.append(lines[i].strip())
            i += 1
        text = inline(" ".join(para))
        if not sections:
            lede.append(text)
        else:
            out.append(f"<p>{text}</p>")
    if sections:
        out.append("</section>")
    return "\n".join(out), sections, title, "".join(f'<p class="lede">{p}</p>' for p in lede)


def style() -> str:
    """The patch notes' style, and what the guide adds."""
    with open(PATCH_NOTES, encoding="utf-8") as f:
        page = f.read()
    m = re.search(r"<style>(.*?)</style>", page, re.S)
    return (m.group(1) if m else "") + EXTRA_STYLE


def build() -> str:
    with open(GUIDE, encoding="utf-8") as f:
        content, sections, _, lede = body(f.read())
    index = "".join(f'<li><a href="#{a}">{inline(t)}</a></li>' for a, t in sections)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Obsidian Edition Player's Guide</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Marcellus+SC&family=Alegreya+Sans:ital,wght@0,400;0,500;0,700;1,400&family=IBM+Plex+Mono:wght@400;500&display=swap">
<!-- Made from PLAYER-GUIDE.md by dsloader/guidepage.py: edit the guide, then run python -m dsloader.guidepage -->
<style>{style()}</style>
</head>
<body>
<header class="banner">
  <div class="eyebrow">Dark Sun: Shattered Lands · Mod</div>
  <h1>Obsidian Edition<br>Player's Guide</h1>
  {lede}
</header>
<div class="wrap">
  <nav class="index" aria-label="Sections">
    <p>In this guide</p>
    <ol>{index}</ol>
  </nav>
  <main id="guide">
{content}
  </main>
</div>
<footer>
  <p>Obsidian Edition runs on Windows with the GOG release of Dark Sun: Shattered Lands, in DOSBox. The <a href="README.md">README</a> has every rule in full detail, and the <a href="../patch-notes.html">patch notes</a> every change from the original game.</p>
</footer>
</body>
</html>
"""


def write() -> None:
    with open(PAGE, "w", encoding="utf-8", newline="\n") as f:
        f.write(build())


if __name__ == "__main__":
    write()
    print(PAGE)
