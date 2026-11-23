"""Finish the cloth in registered outfit archives, using the player's game palette.

python prototypes/outfitdetail.py GAME_DIR SOURCE_ARCHIVE OUTPUT_ARCHIVE

Each archive keeps its pre-detail paint so a second export starts from the same
pixels. Equipment masks, body edits, registration and retail art are independent.
"""
import argparse
from collections import Counter
from functools import lru_cache
import os
from pathlib import Path
from tempfile import NamedTemporaryFile
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

import outfits
from dsloader import art, classoutfits as co, sprites

# Material ramps include intermediate warm/cool shades between the main fold
# tones. All entries are fixed VGA colors, outside the game's cycling ranges.
RAMPS = {
    "linen": (208, 204, 207, 205, 194, 206, 120, 121, 61, 123, 199, 125, 62, 155, 63),
    "slate": (208, 17, 18, 19, 20, 21, 22, 49, 23, 24, 25, 50, 26, 27, 28, 29),
    "plum": (208, 17, 174, 112, 175, 113, 58, 74, 115, 59, 117, 118, 239, 119, 232),
    "teal": (208, 17, 69, 188, 53, 70, 225, 71, 40, 72, 73),
    "leaf": (208, 17, 69, 188, 53, 189, 225, 54, 226, 55, 227, 56, 57),
    "hide": (208, 88, 204, 89, 90, 207, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100),
    "ochre": (207, 204, 205, 94, 95, 97, 99, 168, 169, 170, 171),
}
# Colored half-tones used where the weave turns across the light. Keep the
# ground hue dominant, especially on the very small teal panels.
HALFTONES = {
    "teal": {208: 209, 17: 18, 69: 48, 188: 210, 53: 49, 70: 211,
             225: 160, 71: 212, 40: 226, 72: 213, 73: 215},
    "linen": {205: 92, 194: 95, 206: 97, 120: 118, 121: 119, 61: 122,
              123: 124, 199: 214, 125: 215, 155: 126},
    "plum": {17: 18, 112: 19, 113: 114, 58: 116, 115: 22, 117: 23,
             119: 120, 232: 238},
}
MATERIAL = {
    **dict.fromkeys((61, 62, 63, 115, 155, 194, 199, 206), "linen"),
    **dict.fromkeys(range(18, 32), "slate"),
    **dict.fromkeys((58, 59, 60, 118, 119, 122, 174, 175), "plum"),
    **dict.fromkeys((70, 71, 72, 73), "teal"),
    **dict.fromkeys((*range(53, 58), *range(188, 192)), "leaf"),
    **dict.fromkeys((*range(88, 105), 203, 204), "hide"),
    **dict.fromkeys(range(168, 173), "ochre"),
}
DEFAULT = {"Cleric": "linen", "Priest": "linen", "Thief": "slate", "Ranger": "leaf",
           "Druid": "leaf", "Psionicist": "teal", "Mage": "plum", "Preserver": "plum"}
CROSS = ((-1, 0), (1, 0), (0, -1), (0, 1))
BLOCKED = co.FOREARM | co.BOW | co.LEFT_FOOT | co.RIGHT_FOOT
SHELL = co.CHEST | co.LEGS


@lru_cache(None)
def tones(palette, family):
    ramp = RAMPS[family]
    def light(c):
        r, g, b = palette[c]
        return 0.299 * r + 0.587 * g + 0.114 * b
    return {c: ramp.index(c) if c in ramp else min(range(len(ramp)), key=lambda i: abs(light(c) - light(ramp[i])))
            for c in range(256)}


def reference_folds(game):
    """Signed relief from eight-row swatches on the backs of the retail garments."""
    swatches = {}
    for label, npc, left, top in (("linen", 1563, 8, 8), ("slate", 630, 7, 9),
                                  ("plum", 724, 8, 9)):
        rows = game.fr(npc, 1)
        relief = []
        for row in rows[top:top + 8]:
            lights = [sum(a * b for a, b in zip(game.palette[c], (0.299, 0.587, 0.114)))
                      for c in row[left:left + 8]]
            middle = sum(lights) / 8
            relief.append([max(-3, min(3, round((v - middle) / 14))) for v in lights])
        swatches[label] = relief
    return swatches


def shade_frame(rows, paint, regions, folds, heads, base, model, role, waist, palette, swatches, pose):
    """Shade opaque, authored garment texels. Image and masks share the archive canvas."""
    fallen = pose == 28
    h, w = len(paint), len(paint[0])
    top, left = h - len(rows), (w - len(rows[0])) // 2
    occupied, cloth = set(), {}
    hooded = "Thief" in role.split("/")
    main = DEFAULT.get(role.split("/")[0], "hide")
    for y in range(h):
        for x in range(w):
            c = paint[y][x]
            sy, sx = y - top, x - left
            native = rows[sy][sx] if 0 <= sy < len(rows) and 0 <= sx < len(rows[0]) else None
            under = base[y][x] if base is not None else None
            visible = c if c is not None else under if under is not None else native
            if visible in (None, 255):
                continue
            p = (x, y)
            occupied.add(p)
            bits = regions[y][x] or 0
            hood = hooded and heads is not None and heads[y][x] is not None and c is not None and c != native
            if bits & BLOCKED or (heads is not None and heads[y][x] is not None and not hood):
                continue
            if c is None or not (bits & SHELL or folds[y][x] or hood):
                continue
            # A cap, buckle or accent sewn to another garment keeps its artist's highlights.
            if bits & co.ARMS or c in (168, 169, 170, 171) and role != "Druid":
                continue
            if c in (155, 199) and main != "linen":
                continue
            if "/" in role and "Psionicist" in role and main != "teal" and c in (70, 71, 72, 73):
                continue
            # The dwarf front fold emerges between the ribs and the crossing wrist.
            if model in co.DWARVES and pose == 11 and main == "linen" and (sx, sy) == (6, 7):
                continue
            if c in MATERIAL or c in (17, 69, 205, 207, 208):
                cloth[p] = c

    family_at = {}
    for (x, y), c in cloth.items():
        family = MATERIAL.get(c)
        if family is None:
            nearby = Counter(MATERIAL.get(cloth.get((x + dx, y + dy))) for dx, dy in CROSS)
            nearby.pop(None, None)
            family = nearby.most_common(1)[0][0] if nearby else main
        family_at[x, y] = family

    # Measure the fold across the torso, so a moving sprite never passes
    # through a screen-fixed pattern. Use the retail waist for vertical phase.
    if not cloth:
        return
    axis_y = waist + top
    band = [x for x, y in occupied if abs(y - axis_y) <= 1]
    axis_x = (min(band) + max(band)) // 2 if band else w // 2
    hood_points = [(x, y) for x, y in cloth if hooded and heads and heads[y][x]]
    brow = (max if fallen else min)((y for x, y in hood_points), default=0)
    for (x, y), c in cloth.items():
        family = family_at[x, y]
        ramp = RAMPS[family]
        dy = (y - axis_y) * (-1 if fallen else 1)
        u = x - axis_x
        # The small checker uses adjacent tones. Offset successive groups
        # of rows to avoid a rigid screen or full-height vertical stripes.
        phase = (u + dy + dy // 4) & 1
        tone = tones(palette, family)[c]
        rich = model != 2099 and family in ("linen", "slate", "teal", "leaf", "plum")
        texture = swatches.get(family, swatches["slate"])
        relief = texture[dy % 8][(u + dy // 5) % 8]
        if rich:
            tone += relief + (1 if phase else -1)
        elif phase or relief < 0:
            tone += 1 if relief > 0 else -1
        if hooded and heads and heads[y][x]:
            # Let the crown catch light, then turn the cloth into the darker cowl.
            drop = abs(y - brow)
            if drop <= 1 and phase:
                tone += 1
            elif drop >= 4 and relief < 0:
                tone -= 1
        right = (x + 1, y) not in occupied
        hem = (x, y + (-1 if fallen else 1)) not in occupied
        if right or hem:
            if rich or (u + dy) % 3:
                tone = min(tone, 1 + phase if family == "linen" else 2 + phase)
        elif (x - 1, y) not in occupied and dy % 4 == 0:
            tone = min(tone, 3 + phase)
        elif model == 2099 and (u + 2 * dy) % 3:
            continue
        elif family == "teal" and abs(relief) <= 1 and not phase:
            continue
        shade = ramp[max(0, min(len(ramp) - 1, tone))]
        if rich and not (right or hem) and (u - dy) % 3 == 1:
            shade = HALFTONES.get(family, {}).get(shade, shade)
        # Keep the idle dwarf's overlapping leather belt ends warm at the right hip.
        if model in co.DWARVES and pose == 0 and family == "hide" and shade == 208:
            if 11 <= x - left <= 15 and 12 <= y - top <= 15:
                shade = 88
        paint[y][x] = shade
        if folds[y][x] and shade != c:
            # Translate the new fold relief into the six steps used by an equipped cloak.
            delta = sum((v - u) * weight for u, v, weight in
                        zip(palette[c], palette[shade], (0.299, 0.587, 0.114)))
            folds[y][x] = max(1, min(6, folds[y][x] + round(delta / 22)))


def finish_archive(game, source, output):
    """Rebuild only the outfit paint. Retain the original paint for repeatable exports."""
    output = Path(output)
    palette = tuple(map(tuple, game.palette))
    swatches = reference_folds(game)
    with NamedTemporaryFile(dir=output.parent, delete=False) as tmp:
        temp_path = Path(tmp.name)
    try:
        with ZipFile(source) as src, ZipFile(temp_path, "w") as dst:
            entries = set(src.namelist())
            female = "Base/walk" in entries
            for name in src.namelist():
                if name.endswith(("-underpaint", "-dye")):
                    continue
                data = src.read(name)
                prefix, tag = name.rsplit("/", 1)
                if prefix != "Base" and tag in ("walk", "combat"):
                    original = name + "-underpaint"
                    raw = src.read(original) if original in entries else data
                    parts = prefix.split("/")
                    model = int(parts.pop(0)) if parts[0].isdigit() else 2099 if female else 2095
                    role = "/".join(parts)
                    cb = tag == "combat"
                    def stream(key):
                        return src.read(key) if key in entries else None
                    aux = [stream(name + "-regions"), stream(name + "-cloak"),
                           stream(("Base/" + tag if female else name) + "-head"),
                           stream("Base/" + tag) if female else None]
                    frames, dyes = [], []
                    for f in range(14 if cb else 15):
                        rows = game.fr(model + cb, f)
                        paint = art.decode_frame(raw, f)[2]
                        masks = [art.decode_frame(b, f)[2] if b else None for b in aux]
                        waist = game.fig(model).parts(cb, f).waist
                        shade_frame(rows, paint, *masks, model, role, waist if waist is not None else len(rows) // 2,
                                    palette, swatches, f + 15 * cb)
                        frames.append(paint)
                        dyes.append(masks[1])
                    data = sprites.encode_frames(frames)
                    dst.writestr(ZipInfo(name + "-dye"), sprites.encode_frames(dyes), ZIP_DEFLATED)
                    dst.writestr(ZipInfo(original), raw, ZIP_DEFLATED)
                dst.writestr(ZipInfo(name), data, ZIP_DEFLATED)
        os.replace(temp_path, output)
    finally:
        temp_path.unlink(missing_ok=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for arg in ("game_dir", "source", "output"):
        parser.add_argument(arg, type=Path)
    args = parser.parse_args()
    finish_archive(outfits.Game(args.game_dir), args.source, args.output)
