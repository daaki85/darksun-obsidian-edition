# tools_index.py: writes TOOLS.md, the index of the playtest tools, from the first sentence of each
# tool's own header comment or docstring (its usage, "name ARGS: what it does", split into two
# columns). Run it after adding or changing a tool.
import ast
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))


def header(path: str) -> str:
    """The tool's header: its leading # comment lines, or a Python module's docstring."""
    text = open(path, errors="replace").read()
    if path.endswith(".py"):
        try:
            doc = ast.get_docstring(ast.parse(text))
        except SyntaxError:
            doc = None
        if doc:
            return " ".join(doc.split())
    lines = []
    for line in text.split("\n")[:15]:
        if line.startswith("#!"):
            continue
        if line.startswith("#"):
            lines.append(line.lstrip("#").strip())
        elif lines or line.strip():
            break
    return " ".join(lines)


def split_usage(name: str, text: str):
    """(usage, what) when TEXT opens with the tool's name and its arguments before ': '."""
    stem = name.rsplit(".", 1)[0]
    head, sep, rest = text.partition(": ")
    first = head.split(" ", 1)[0] if head else ""
    if sep and first in (name, stem) and len(head) < 90:
        return head, rest
    return name, text


def first_sentence(text: str) -> str:
    """Up to the first full stop or semicolon past 40 characters, at most 220 characters."""
    m = re.search(r"(?<=.{40})[.;](\s|$)", text)
    text = text[:m.start() + 1] if m else text
    return text if len(text) <= 220 else text[:217].rsplit(" ", 1)[0] + "..."


def main() -> None:
    rows = []
    for name in sorted(os.listdir(HERE)):
        if not name.endswith((".py", ".sh")) or name in ("tools_index.py", "env.sh", "live.py"):
            continue
        usage, what = split_usage(name, header(os.path.join(HERE, name)))
        what = first_sentence(what) or "(no description in the file)"
        cell = lambda s: s.replace("|", "\\|")
        rows.append(f"| `{cell(usage)}` | {cell(what)} |")
    page = ("# The playtest tools\n\n"
            "Every tool in `playtest/`, with the first sentence of its own header comment "
            "(`python3 tools_index.py` writes this page again from the files: run it after adding "
            "or changing a tool). `env.sh` and `live.py` are the others' shared set-up. How to use "
            "them is in [PLAYTESTING.md](PLAYTESTING.md).\n\n"
            "| Tool | What it does |\n|---|---|\n" + "\n".join(rows) + "\n")
    with open(os.path.join(HERE, "TOOLS.md"), "w") as f:
        f.write(page)
    print(len(rows), "tools")


if __name__ == "__main__":
    main()
