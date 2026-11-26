"""Prototype, not part of the Ledger: corrections by hand to the pictures outfits.py makes, kept
as text so they outlive the rules that make the pictures.

A rule that is right for most frames leaves the odd pixel wrong in one. Such a pixel is put
right by hand, and the correction kept in prototypes/outfit_fixes.txt, one frame to a block:

    Mage / half-elf man / walk 12
      14,9: 38 > 160
      15,9: . > 159
      3,20: 71 > .

Each line is a pixel of the figure's own frame (x across, y down, from its top left corner; a
cloak can lie outside it, so they may be below 0 or past its edge), the palette colour the rules
drew there when the correction was made, and the colour it should be ("." is no pixel).

Every time the pictures are made, each correction is laid on its frame where the rules still
draw the colour it was made over (or already draw what it asks for). Where they now draw
something else, the rules have changed under it: it is left off and reported as stale, to be
looked at again (kept as it is, redone or dropped), never laid blindly on a picture it wasn't
made for. Colours are compared as the screen shows them (the palette has the same colour under
more than one number).

The order of work: a fault seen in many frames or figures is a fault of the rules, mended in
outfits.py; only what is left, one frame's own, is corrected here. outfitcheck.py counts the
corrections by outfit and figure: many on one figure point at a rule to mend instead.

Corrections are made on outfitreview.py's page (pick a frame, paint, copy the text out) or
written here by hand; `python3 prototypes/outfitfixes.py GAME_DIR OUTFIT FIGURE FRAME` (as
"Mage" "half-elf man" "walk 12") prints a frame's colour numbers to write them from.
"""

import os
import sys
from typing import Dict, List, Optional, Tuple

FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outfit_fixes.txt")
Key = Tuple[str, str, int, int]  # (outfit, figure, fighting, frame)
Fix = Dict[Tuple[int, int], Tuple[Optional[int], Optional[int]]]  # pixel: (before, after)
HEAD = """# Corrections by hand to the pictures prototypes/outfits.py makes (outfitfixes.py):
# OUTFIT / FIGURE / walk or fight N, then its pixels as "x,y: before > after" in the figure's own
# frame, palette colours ("." no pixel). Laid on only where the rules still draw "before".
"""


def frame_name(cb: int, f: int) -> str:
    return f"{'fight' if cb else 'walk'} {f}"


def _colour(text: str) -> Optional[int]:
    return None if text.strip() == "." else int(text)


def parse(text: str) -> Dict[Key, Fix]:
    out: Dict[Key, Fix] = {}
    cur: Optional[Fix] = None
    for n, line in enumerate(text.splitlines(), 1):
        line = line.split("#")[0].rstrip()
        if not line.strip():
            continue
        try:
            if not line[0].isspace():
                outfit, figure, frame = (p.strip() for p in line.split("/"))
                kind, f = frame.split()
                cur = out.setdefault((outfit, figure, int(kind == "fight"), int(f)), {})
            else:
                at, change = line.split(":")
                x, y = (int(v) for v in at.split(","))
                before, after = change.split(">")
                cur[(x, y)] = (_colour(before), _colour(after))
        except (ValueError, TypeError) as e:
            raise SystemExit(f"outfit_fixes.txt line {n}: {line.strip()!r} ({e})")
    return out


def read(path: str = FILE) -> Dict[Key, Fix]:
    if not os.path.exists(path):
        return {}
    with open(path) as f:
        return parse(f.read())


def text(fixes: Dict[Key, Fix]) -> str:
    def show(c):
        return "." if c is None else str(c)
    out = [HEAD]
    for (outfit, figure, cb, f), fix in sorted(fixes.items()):
        if fix:
            out.append(f"{outfit} / {figure} / {frame_name(cb, f)}")
            out += [f"  {x},{y}: {show(a)} > {show(b)}" for (x, y), (a, b) in sorted(fix.items(), key=lambda t: (t[0][1], t[0][0]))]
            out.append("")
    return "\n".join(out)


def apply(rows: List[List[Optional[int]]], pad: int, fix: Fix, palette) -> List[Tuple[int, int]]:
    """FIX laid on a frame (ROWS, with PAD round the figure's own): each pixel where the rules
    drew its "before" (or its "after" already). The pixels left off, stale, are returned."""
    def same(a, b):
        return a == b or (a is not None and b is not None and palette[a] == palette[b])
    stale = []
    for (x, y), (before, after) in fix.items():
        X, Y = x + pad, y + pad
        if not (0 <= Y < len(rows) and 0 <= X < len(rows[0])):
            stale.append((x, y))
        elif same(rows[Y][X], before):
            rows[Y][X] = after
        elif not same(rows[Y][X], after):
            stale.append((x, y))
    return stale


def main(argv: List[str]) -> None:
    if len(argv) < 4:
        raise SystemExit(__doc__)
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import outfits as O
    game = O.Game(argv[0])
    npc = next(n for n, o in O.OUTFITS.items() if o.name.lower() == argv[1].lower())
    key = next(k for k, name in O.FIGURES if name == argv[2])
    kind, f = argv[3].split()
    rows, ox, oy, own = game.full(key, npc)[int(kind == "fight")][int(f)]
    print(f"{O.OUTFITS[npc].name} / {argv[2]} / {argv[3]}: the figure's own frame is {len(own[0])} by {len(own)}; x across, y down")
    print("   y\\x " + " ".join(f"{x + ox:3}" for x in range(len(rows[0]))))
    for y, r in enumerate(rows):
        if any(c is not None for c in r):
            print(f"{y + oy:6} " + " ".join("  ." if c is None else f"{c:3}" for c in r))


if __name__ == "__main__":
    main(sys.argv[1:])
