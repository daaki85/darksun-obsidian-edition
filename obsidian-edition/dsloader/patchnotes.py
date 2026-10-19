"""The patch notes as a web page: ../PATCH-NOTES.md made ../patch-notes.html, in the look the
player's guide shares (pagestyle.css), with the notes' sections as the index and a button that
copies the Markdown itself for forums.

`python -m dsloader.patchnotes` writes it; tests/test_patchnotes.py checks it is up to date. Only
the Markdown the notes use: the title, the italic line under it, paragraphs, bold lines as
sub-headings, lists whose items open with a tag (**[New]**, **[Changed]**, **[Fixed]**), tables,
and "> *Developers' Notes: ...*" quotes; *(was ...)* comes out as the old value."""

import html
import os
import re
from typing import List, Tuple

from .guidepage import _cells, inline, slug

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(HERE)
NOTES = os.path.join(ROOT, "PATCH-NOTES.md")
PAGE = os.path.join(ROOT, "patch-notes.html")
STYLE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pagestyle.css")
REPO = "https://github.com/daaki85/darksun-obsidian-edition"
TAGS = {"New": "new", "Changed": "chg", "Fixed": "fix"}
DEV = re.compile(r"^> \*([^:*]+): (.*)\*$")


def style() -> str:
    with open(STYLE, encoding="utf-8") as f:
        return f.read()


def item(text: str) -> str:
    """A list item: its tag as a label, its *(was ...)* as the old value."""
    tag = re.match(r"\*\*\[(\w+)\]\*\* (.*)$", text)
    label = ""
    if tag and tag.group(1) in TAGS:
        label = f'<span class="tag {TAGS[tag.group(1)]}">{tag.group(1)}</span>'
        text = tag.group(2)
    out = inline(text)
    out = re.sub(r"<em>(\(was .+?\))</em>", r'<span class="was">\1</span>', out)
    return f"<li>{label}{out}</li>"


def body(markdown: str) -> Tuple[str, List[Tuple[str, str]], dict]:
    """The notes' HTML body, their sections [(anchor, title)], and the opening's parts (title,
    subtitle, lede, download)."""
    lines = markdown.splitlines()
    out: List[str] = []
    sections: List[Tuple[str, str]] = []
    head = {"title": "", "subtitle": "", "lede": "", "download": f"{REPO}/releases/latest"}
    skipping = False
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
                head["title"] = text
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
                out.append(f'<h{level + 1} id="{slug(text)}">{inline(text)}</h{level + 1}>')
            continue
        if skipping:
            i += 1
            continue
        if line.lstrip().startswith("|"):
            rows = []
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                rows.append(lines[i])
                i += 1
            table = ['<div class="tablewrap"><table><thead><tr>'
                     + "".join(f"<th>{inline(c)}</th>" for c in _cells(rows[0])) + "</tr></thead><tbody>"]
            for r in rows[2:]:
                table.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in _cells(r)) + "</tr>")
            out.append("".join(table) + "</tbody></table></div>")
            continue
        if line.startswith("- "):
            items = []
            while i < len(lines) and lines[i].startswith("- "):
                items.append(item(lines[i][2:].strip()))
                i += 1
            out.append("<ul>" + "".join(items) + "</ul>")
            continue
        dev = DEV.match(line)
        if dev:
            out.append(f'<div class="dev"><b>{html.escape(dev.group(1), quote=False)}</b>{inline(dev.group(2))}</div>')
            i += 1
            continue
        bold = re.match(r"^\*\*([^*]+)\*\*$", line)
        if bold:
            out.append(f"<h4>{inline(bold.group(1))}</h4>")
            i += 1
            continue
        para = []
        while i < len(lines) and lines[i].strip() and not re.match(r"^(#{1,6} |- |\||> )", lines[i]):
            para.append(lines[i].strip())
            i += 1
        text = " ".join(para)
        if not sections:  # (the opening: the italic line, the lede, the download, the page's own note)
            download = re.match(r"^\*\*Download:\*\* (\S+)$", text)
            if download:
                head["download"] = download.group(1)
            elif re.match(r"^\*[^*].*\*$", text):
                if not head["subtitle"]:
                    head["subtitle"] = text[1:-1]
            elif not head["lede"]:
                head["lede"] = inline(text)
            continue
        out.append(f"<p>{inline(text)}</p>")
    if sections:
        out.append("</section>")
    return "\n".join(out), sections, head


def build() -> str:
    with open(NOTES, encoding="utf-8") as f:
        markdown = f.read()
    content, sections, head = body(markdown)
    index = "".join(f'<li><a href="#{a}">{inline(t)}</a></li>' for a, t in sections)
    name, _, kind = head["title"].partition(": ")
    source = markdown.replace("</", "<\\/")  # (inside a script)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(name)} {html.escape(kind)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Marcellus+SC&family=Alegreya+Sans:ital,wght@0,400;0,500;0,700;1,400&family=IBM+Plex+Mono:wght@400;500&display=swap">
<!-- Made from PATCH-NOTES.md by obsidian-edition/dsloader/patchnotes.py: edit the notes, then run python -m dsloader.patchnotes -->
<style>
{style()}</style>
</head>
<body>
<header class="banner">
  <div class="eyebrow">Dark Sun: Shattered Lands · Mod</div>
  <h1>{html.escape(name)}<br>{html.escape(kind)}</h1>
  <div class="meta">{html.escape(head["subtitle"])}</div>
  <p class="lede">{head["lede"]}</p>
  <div class="actions">
    <a class="btn" href="{html.escape(head["download"])}">Download</a>
    <a class="btn ghost" href="{REPO}/blob/main/obsidian-edition/PLAYER-GUIDE.md">Player's guide</a>
    <button class="btn ghost" id="copy" type="button">Copy as Markdown</button>
    <span class="copied" id="copied" hidden>Copied</span>
  </div>
</header>
<div class="wrap">
  <nav class="index" aria-label="Sections">
    <p>In these notes</p>
    <ol>{index}</ol>
  </nav>
  <main id="notes">
{content}
  </main>
</div>
<footer>
  <p>Obsidian Edition runs on Windows with the GOG release of Dark Sun: Shattered Lands, in DOSBox, and needs 64-bit Python 3.8 or later (its .bat files offer to install it). It never changes the game's own files. <a href="{REPO}/releases/latest">Download the latest release</a> · <a href="{REPO}/blob/main/obsidian-edition/README.md">Full documentation</a> · <a href="{REPO}/blob/main/CHANGELOG.md">Changelog</a></p>
</footer>
<textarea id="md" aria-hidden="true" tabindex="-1"></textarea>
<script type="text/markdown" id="source">{source}</script>
<script>
(function () {{
  const text = document.getElementById('source').textContent.replace(/<\\\\\\//g, '</');
  const btn = document.getElementById('copy'), ok = document.getElementById('copied'), ta = document.getElementById('md');
  btn.addEventListener('click', () => {{
    const done = () => {{ ok.hidden = false; setTimeout(() => {{ ok.hidden = true; }}, 2500); }};
    const fallback = () => {{ ta.value = text; ta.select(); try {{ document.execCommand('copy'); }} catch (e) {{}} done(); }};
    try {{ navigator.clipboard.writeText(text).then(done, fallback); }} catch (e) {{ fallback(); }}
  }});
}})();
</script>
</body>
</html>
"""


def write() -> None:
    with open(PAGE, "w", encoding="utf-8", newline="\n") as f:
        f.write(build())


if __name__ == "__main__":
    write()
    print(PAGE)
