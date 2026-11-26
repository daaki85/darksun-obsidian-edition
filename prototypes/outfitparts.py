"""Prototype, not part of the Ledger: what outfits.py takes each pixel of a figure for. Most
faults in the pictures it makes are a part misread (a chin taken for a collar, a thigh for an
arm), so this draws the reading itself, to be looked at and put right at its source.

    python3 prototypes/outfitparts.py GAME_DIR OUT.png "FIGURE" [FRAMES] [--zoom N] [--own]
    python3 prototypes/outfitparts.py GAME_DIR count

Each frame of the figure with every pixel in its part's colour:

    face    yellow     hair   magenta    other head  white (eyes, a collar in the head's box)
    hand    red        forearm orange    upper arm   blue  (the arm from the hand up: to a third
    torso   green      leg    cyan       boot        grey   of the way the forearm, then the arm)
    cloak   purple (a cloak of the figure's own)           black: outline and shadow, as drawn

and, as lines: the head's box (white), the brow (yellow), the shoulders' row (red, from its left
end to its right), the waist (green), each foot (grey). --own draws the figure's own picture
before each. FRAMES as outfitbench.py's ("w0-14,f0-13"; default all). count: for every figure,
how many pixels of each part its 29 frames have, to compare figures and find a frame with none.
"""

import collections
import os
import sys
from typing import List

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import outfitbench as B  # noqa: E402
import outfitfixes as F  # noqa: E402
import outfits as O  # noqa: E402

COLOUR = {"face": (250, 220, 60), "hair": (220, 60, 200), "head": (245, 245, 245), "hand": (230, 40, 40),
          "forearm": (255, 150, 30), "arm": (60, 90, 230), "torso": (50, 170, 70), "leg": (60, 200, 210),
          "boot": (130, 130, 130), "cloak": (150, 70, 200)}
PROBE = O.OUTFITS[724]  # (the mage's: sleeves and clothes that cover, so every part is told apart)


def reading(game: O.Game, key, cb: int, f: int):
    """A frame's pixels by part, and its parts (spriteparts', as outfits.py mends them)."""
    fig = game.fig(key)
    own, p = fig.rows(cb, f), fig.parts(cb, f)
    out = {}
    if not (p.head and p.shoulders and p.waist is not None):
        return own, p, out
    bow = game.bow(fig, own, p) if cb and f in O.sp.BOW_FRAMES else frozenset()
    _, what = game.clothe(own, fig, p, PROBE, fig.bands(cb, f), bow)
    arm = game.arms(own, p, O.keep_out(own, p, fig.hair), fig.bands(cb, f), fig.sure_bands)
    reach = max(4, p.waist - p.shoulders[0])
    hairc = fig.hair - O.SKINC
    for (x, y), k in what.items():
        c = own[y][x]
        if c == 254:
            continue
        if k == "head":
            k = "hair" if (x, y) in p.hair or c in hairc else "face" if c in O.SKINC else "head"
        elif k == "arm" and arm.get((x, y), 99) < reach / 3:
            k = "forearm"
        out[(x, y)] = k
    return own, p, out


def view(game: O.Game, path: str, figure: str, frames, zoom: int, with_own: bool) -> None:
    from PIL import Image, ImageDraw
    key = next(k for k, name in O.FIGURES if name == figure)
    got = [(cb, f, *reading(game, key, cb, f)) for cb, f in frames]
    W = max(len(own[0]) for _, _, own, _, _ in got) + 4
    H = max(len(own) for _, _, own, _, _ in got) + 4
    kinds = 2 if with_own else 1
    per = max(1, min(len(got), 2000 // (W * zoom * kinds)))
    lines = (len(got) + per - 1) // per
    TOP = 12
    img = Image.new("RGB", (per * kinds * W * zoom, lines * (H * zoom + TOP)), (196, 150, 104))
    d = ImageDraw.Draw(img)
    for i, (cb, f, own, p, parts) in enumerate(got):
        for k in range(kinds):
            X0, Y0 = ((i % per) * kinds + k) * W * zoom, (i // per) * (H * zoom + TOP) + TOP
            bx, by = X0 + ((W - len(own[0])) // 2) * zoom, Y0 + (H - len(own) - 2) * zoom
            for y, r in enumerate(own):
                for x, c in enumerate(r):
                    if c is None:
                        continue
                    rgb = game.palette[c] if (with_own and k == 0) else COLOUR.get(parts.get((x, y)), (0, 0, 0))
                    d.rectangle((bx + x * zoom, by + y * zoom, bx + (x + 1) * zoom - 1, by + (y + 1) * zoom - 1), fill=rgb)
            if not (with_own and k == 0) and p.head and p.shoulders and p.waist is not None:
                h, (sy, sa, sb) = p.head, p.shoulders

                def line(x0, y0, x1, y1, col):
                    d.line((bx + x0 * zoom, by + y0 * zoom, bx + x1 * zoom, by + y1 * zoom), fill=col)
                d.rectangle((bx + h.left * zoom, by + h.top * zoom, bx + (h.right + 1) * zoom, by + sy * zoom), outline=(255, 255, 255))
                line(h.left, h.brow + 1, h.right + 1, h.brow + 1, (250, 220, 60))
                line(sa, sy, sb + 1, sy, (230, 40, 40))
                line(sa, p.waist + 1, sb + 1, p.waist + 1, (20, 120, 40))
                for fy, fa, fb in p.feet:
                    line(fa, fy + 1, fb + 1, fy + 1, (90, 90, 90))
                for hx, hy in p.hands.values():
                    d.ellipse((bx + hx * zoom - 1, by + hy * zoom - 1, bx + (hx + 1) * zoom, by + (hy + 1) * zoom), outline=(255, 255, 255))
            d.text((X0 + 2, Y0 - TOP), F.frame_name(cb, f), fill=(40, 24, 12))
    img.save(path)
    print(path, img.size)


def count(game: O.Game) -> None:
    kinds = list(COLOUR)
    print(f"{'':17}" + "".join(f"{k:>8}" for k in kinds) + "   frames with no hand / no face / unread")
    for key, name in O.FIGURES:
        total = collections.Counter()
        none = collections.Counter()
        for cb, n in ((0, 15), (1, 13)):
            for f in range(n):
                _, p, parts = reading(game, key, cb, f)
                c = collections.Counter(parts.values())
                total.update(c)
                if not parts:
                    none["unread"] += 1
                else:
                    none["hand"] += not c["hand"]
                    none["face"] += not c["face"]
        print(f"{name:17}" + "".join(f"{total[k]:8}" for k in kinds) + f"   {none['hand']} / {none['face']} / {none['unread']}")


def main(argv: List[str]) -> None:
    opts, args = {}, []
    it = iter(argv)
    for a in it:
        if a == "--zoom":
            opts[a] = next(it)
        elif a == "--own":
            opts[a] = True
        else:
            args.append(a)
    if len(args) < 2:
        raise SystemExit(__doc__)
    game = O.Game(args[0], {})
    if args[1] == "count":
        count(game)
    else:
        view(game, args[1], args[2], B.frames_of(args[3] if len(args) > 3 else "w0-14,f0-12"),
             int(opts.get("--zoom", 5)), bool(opts.get("--own")))


if __name__ == "__main__":
    main(sys.argv[1:])
