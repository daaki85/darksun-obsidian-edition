"""Prototype, not part of the Ledger: each outfit's pictures beside the game's own, and an audit
of what changed, part by part (outfitparts.py's reading of the figure's own picture).

    python3 prototypes/outfitcompare.py GAME_DIR OUT_DIR

writes OUT_DIR/compare_<outfit>.png (each figure's twelve sample frames in pairs: the game's own
picture, then the outfit's) and OUT_DIR/compare.txt, and prints the audit's table. For each
outfit and figure, over its 28 standing, walking and fighting frames (not the dead one):

  changed   the share of the figure's own pixels that are another colour
  added     pixels drawn where the figure's own picture has none (a cloak), as a share of it
  face      pixels of the face in another colour: none should be (under a hood worn up, the
            crown and the hair's line are the hood's, so only the face below the brow counts, and
            not from behind)
  hair      pixels of the hair in another colour: none should be, but under a hood worn up
  hands     pixels of the hands in another colour: none should be, but where a cloak seen from
            behind lies over them (so the back frames are left out)
  bare      where the clothes cover the skin: skin left as it was on the chest and legs, as a
            share of the skin there (the warrior's legs below the kilt are meant bare)

compare.txt lists every frame with a face, hair or hand pixel changed, the worst first.
"""

import collections
import os
import sys
from typing import List

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import outfitfixes as F  # noqa: E402
import outfitparts as P  # noqa: E402
import outfits as O  # noqa: E402


def audit(game: O.Game):
    table, frames = {}, []
    for npc, o in O.OUTFITS.items():
        for key, name in O.FIGURES:
            walk, fight = game.full(key, npc)
            t = collections.Counter()
            for cb, group in ((0, walk), (1, fight[:13])):
                for f, (rows, ox, oy, own) in enumerate(group):
                    _, p, parts = P.reading(game, key, cb, f)
                    bands = game.fig(key).bands(cb, f)  # (wristbands are made steel on purpose)
                    ears = key in O.figures.ELVES  # (and the elves' ears are drawn beside the head)
                    c = collections.Counter()
                    for y, r in enumerate(own):
                        for x, was in enumerate(r):
                            if was is None:
                                continue
                            now = rows[y - oy][x - ox]
                            k = parts.get((x, y))
                            t["own"] += 1
                            t["changed"] += now != was
                            if ears and now in (O.figures.LIT, O.figures.RIM):
                                continue
                            if k == "face" and now != was and not (o.hood and p.head and (
                                    y <= p.head.brow + 1 or p.facing == O.sp.BACK)):
                                c["face"] += 1
                            if k == "hair" and now != was and not o.hood:
                                c["hair"] += 1
                            if k == "hand" and now != was and p.facing != O.sp.BACK and (x, y) not in bands:
                                c["hands"] += 1
                            if o.cover and k in ("torso", "leg") and was in O.SKINC:
                                t["skin"] += 1
                                t["bare"] += now == was
                    t["added"] += sum(1 for y, r in enumerate(rows) for x, now in enumerate(r) if now is not None and not (
                        0 <= y + oy < len(own) and 0 <= x + ox < len(own[0]) and own[y + oy][x + ox] is not None))
                    t.update(c)
                    if c:
                        frames.append((sum(c.values()), o.name, name, cb, f, dict(c)))
            table[(o.name, name)] = t
    frames.sort(key=lambda r: -r[0])
    return table, frames


def sheet(game: O.Game, npc: int, path: str) -> None:
    from PIL import Image, ImageDraw, ImageFont
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
    except OSError:
        font = ImageFont.load_default()
    CW, CH, BASE, Z, LW, TOP = 40, 58, 52, 2, 150, 44
    ink, ground, pale = (40, 24, 12), (196, 150, 104), (206, 164, 122)
    cols = O.COLUMNS
    img = Image.new("RGB", (LW + len(cols) * 2 * CW * Z, TOP + len(O.FIGURES) * CH * Z), ground)
    d = ImageDraw.Draw(img)
    o = O.OUTFITS[npc]
    d.text((8, 6), f"{o.name}: each frame as the game draws the figure (left, on the paler ground), and in the outfit (right)", fill=ink, font=font)
    for ci, (name, _, _) in enumerate(cols):
        d.text((LW + ci * 2 * CW * Z + CW * Z - 18, 26), name, fill=ink, font=font)
    for mi, (key, label) in enumerate(O.FIGURES):
        walk, fight = game.full(key, npc)
        tile = Image.new("RGB", (len(cols) * 2 * CW, CH), ground)
        for ci, (_, cb, f) in enumerate(cols):
            rows, ox, oy, own = (walk, fight)[cb][f]
            for k, (pic, dx, dy) in enumerate(((own, 0, 0), (rows, ox, oy))):
                x0 = (ci * 2 + k) * CW
                if k == 0:
                    for yy in range(CH):
                        for xx in range(CW):
                            tile.putpixel((x0 + xx, yy), pale)
                bx, by = x0 + CW // 2 - len(own[0]) // 2 + dx, BASE - len(own) + dy
                for y, r in enumerate(pic):
                    for x, c in enumerate(r):
                        if c is not None and x0 <= bx + x < x0 + CW and 0 <= by + y < CH:
                            tile.putpixel((bx + x, by + y), game.palette[c])
        img.paste(tile.resize((tile.width * Z, CH * Z), Image.NEAREST), (LW, TOP + mi * CH * Z))
        d.text((8, TOP + mi * CH * Z + CH * Z // 2 - 8), label, fill=ink, font=font)
    img.save(path, optimize=True)


def main(argv: List[str]) -> None:
    if len(argv) < 2:
        raise SystemExit(__doc__)
    game = O.Game(argv[0])
    os.makedirs(argv[1], exist_ok=True)
    table, frames = audit(game)
    lines = []
    for o in O.OUTFITS.values():
        lines.append(f"\n{o.name:17} changed  added   face  hair  hands   bare")
        for _, name in O.FIGURES:
            t = table[(o.name, name)]
            own = max(1, t["own"])
            bare = f"{100 * t['bare'] / t['skin']:5.0f}%" if t["skin"] else "     -"
            lines.append(f"  {name:15} {100 * t['changed'] / own:6.0f}% {100 * t['added'] / own:5.0f}% {t['face']:6} {t['hair']:5} {t['hands']:6} {bare}")
    text = "\n".join(lines)
    print(text)
    with open(os.path.join(argv[1], "compare.txt"), "w") as out:
        out.write(text + "\n\nFrames with a face, hair or hand pixel changed, the worst first:\n")
        for n, outfit, name, cb, f, c in frames:
            out.write(f"  {outfit:8} {name:17} {F.frame_name(cb, f):9} " + ", ".join(f"{k} {v}" for k, v in c.items()) + "\n")
    for npc, o in O.OUTFITS.items():
        sheet(game, npc, os.path.join(argv[1], f"compare_{o.name.lower()}.png"))
    print(f"\n{len(frames)} frames with a face, hair or hand pixel changed; the pictures and the list are in {argv[1]}")


if __name__ == "__main__":
    main(sys.argv[1:])
