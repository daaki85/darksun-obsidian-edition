"""Author the human body planes on the registered skin paint preceding this pass.

python prototypes/humanbody.py GAME_DIR PREVIOUS_HUMAN_OR_WOMAN_ZIP OUTPUT_ZIP

Supply the paint from 17aaacef to reproduce this revision. The output carries
the finished body and exposed-skin underpaint. For subsequent garment exports,
use outfitdetail.py with --keep-cloak-dyes on that archive.
"""
import argparse
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

import numpy as np

import outfits
from outfitdetail import finish_archive
from dsloader import art, classoutfits as co, sprites

SKIN = (129, 134, 133, 132, 131, 130, 144, 145, 146, 147, 148, 149, 151)

# Socket centre, shoulder radius, then belt centre, in crown-up pose coordinates.
SOCKETS = {
    2095: (
        (9.5, 6, 6.5, 9, 14), (10.5, 7, 4.5, 11, 14), (4, 8.5, 2.35, 4, 15),
        (9, 6, 6, 8, 13), (9.5, 6, 5.5, 9, 13), (8.5, 6, 5.5, 9, 13), (9.5, 6, 5.5, 9, 13),
        (6.5, 7, 4.5, 6, 14), (7.5, 7, 4.5, 7, 15), (7.5, 7, 4.5, 8, 14), (8, 7, 5, 8, 15),
        (6, 8.5, 2.35, 5, 15), (9, 8.5, 2.35, 7, 15), (6, 7.5, 2.35, 5, 14), (8, 8.5, 2.35, 7, 15),
        (7.5, 15.5, 2.5, 7, 23), (12, 7.5, 4, 12, 12), (16.5, 7.5, 2.5, 18, 12),
        (6.5, 11, 3.5, 6, 18), (7, 14, 3, 7, 21), (14.5, 7, 3.5, 18, 14),
        (13.5, 13.5, 4.5, 15, 21), (10.5, 8, 3.5, 8, 15), (10.5, 6, 3.5, 7, 12),
        (7.5, 7, 2.5, 7, 15), (8.5, 10, 2.5, 9, 18), (8, 9, 4, 9, 17), (6.5, 7, 3.5, 9, 12),
        (8, 7, 4, 8, 13),
    ),
    2099: (
        (8, 7, 4.8, 8, 14), (10, 8, 4.8, 10, 14), (5, 7, 3.05, 5, 14),
        (8, 7, 4.8, 7, 14), (10, 7, 4.8, 9, 13), (9, 7, 4.8, 9, 13), (8, 7, 4.8, 8, 13),
        (9, 7, 4.8, 9, 14), (10, 7, 4.8, 10, 14), (11, 7, 4.8, 11, 14), (10, 7, 4.8, 10, 14),
        (9, 7, 3.05, 8, 13), (11, 8, 3.05, 11, 14), (14, 8, 3.05, 13, 15), (10, 7, 3.05, 9, 14),
        (10, 16, 4.35, 9, 23), (12, 9, 4.8, 11, 14), (16, 8, 4.8, 17, 12),
        (6, 12, 4.35, 6, 17), (8, 16, 4.35, 9, 22), (16, 8, 4.8, 17, 13),
        (15, 14, 3.05, 15, 21), (15, 9, 3.05, 13, 15), (15, 8, 3.05, 13, 13),
        (9, 8, 4.35, 7, 14), (6, 10, 4.8, 7, 16), (9, 10, 4.8, 9, 16), (7, 10, 4.8, 9, 15),
        (10, 8, 4.8, 11, 12),
    ),
}

# The man has no head mask. These lower head scanlines overlap his shoulders.
JAW = {
    0: ((6, 8, 12),), 3: ((6, 7, 11),), 4: ((6, 7, 11),), 5: ((6, 7, 11),), 6: ((6, 8, 12),),
    13: ((7, 5, 7),), 15: ((15, 6, 9),), 16: ((7, 9, 14),),
    17: ((7, 11, 18), (8, 11, 17), (9, 12, 16), (10, 12, 15)), 21: ((13, 11, 14),),
    22: ((8, 10, 12),), 23: ((6, 10, 14),), 27: ((7, 2, 8), (8, 3, 7), (9, 4, 7)),
}

# Painted relief from socket to belt. Hex digits are positions in the skin
# ramp. The front rib shelf, tapering shoulder blades and profile ribcage
# each have their own direction. Leave retail variation inside the planes.
PLANES = {
    "front": ("23589876567832", "36ABAA899AA753", "3689AAA9778863", "24678888456742", "13445665554421",
              "24567776555542", "35689987567653", "24578876556542", "13456654334421", "23456654334532"),
    "back": ("45688866578743", "579AAA98689953", "689AAA98689963", "47889998568953", "35678875357852",
             "24567764345542", "23567754344532", "13456654334421", "24568876545532", "34567765445532"),
    "side": ("3568887543", "679AAA9864", "589A998653", "3678887542", "2345554321",
             "3467765421", "3578876532", "2456665432", "1345554321", "2345665432"),
}


def thigh_tone(row, x, y, belt_x, depth, torso_height, protected):
    left = right = x
    while left > 0 and row[left - 1] in SKIN and (left - 1, y) not in protected:
        left -= 1
    while right + 1 < len(row) and row[right + 1] in SKIN and (right + 1, y) not in protected:
        right += 1
    if right - left > 5 and left < belt_x < right:
        if x < belt_x:
            right = int(belt_x) - 1
        else:
            left = int(belt_x)
    if right <= left:
        return SKIN.index(row[x])
    across = (x - left + .28) / (right - left + 1)
    target = np.interp(across, (0, .25, .48, .74, 1), (4.6, 8.8, 7.9, 4.5, 1.4))
    if (right + left) / 2 >= belt_x + .8:
        target -= 1.4
    if depth > torso_height * .66:
        target -= .4
    return round(.64 * target + .36 * SKIN.index(row[x]))


def body_edits(body, model, pose, facing, protected):
    shoulder_x, shoulder_y, radius, belt_x, belt_y = SOCKETS[model][pose]
    height = max(3, belt_y - shoulder_y)
    if pose in (15, 24):
        facing = "side"
    if pose == 28 or (pose == 27 and model == 2095):
        facing = "back"
    panel = PLANES[facing]
    edits = {}
    for y, row in enumerate(body):
        upright = len(body) - 1 - y if pose == 28 else y
        v = (upright - shoulder_y) / height
        if not -.12 <= v <= 1.85:
            continue
        t = min(1, max(0, v))
        centre = shoulder_x + (belt_x - shoulder_x) * t
        width = max(2, radius * np.interp(t, (0, .27, .66, 1), (1, 1, .79, .65)))
        for x, old in enumerate(row):
            if old not in SKIN[1:] or (x, y) in protected:
                continue
            u = (x - centre) / width
            if abs(u) <= 1.03 and v <= 1.03:
                line = panel[round(t * (len(panel) - 1))]
                col = min(len(line) - 1, max(0, round((len(line) - 1) * (u + 1) / 2)))
                target = round(int(line[col], 16) * .74 + SKIN.index(old) * .26)
            elif .5 < upright - belt_y <= max(3, height * .94) and abs(x - belt_x) <= radius * .85 + (upright - belt_y) * .9:
                target = thigh_tone(row, x, y, belt_x, upright - belt_y, height, protected)
            else:
                continue
            if SKIN[target] != old:
                edits[x, y] = old, SKIN[target]
    return edits


def compose(native, layer):
    top = len(layer) - len(native)
    left = (len(layer[0]) - len(native[0])) // 2
    return [[under if over is None else None if over == 255 else over
             for under, over in zip(row, layer[y + top][left:])]
            for y, row in enumerate(native)]


def foreground(masks, heads, model, pose):
    left = 8 if model == 2095 and pose == 13 else 6
    keep = {(x - left, y - 6) for y, row in enumerate(masks) for x, bits in enumerate(row)
            if bits and bits & (co.BOW | co.FOREARM)}
    if heads:
        keep.update((x - left, y - 6) for y, row in enumerate(heads) for x, ink in enumerate(row) if ink is not None)
    else:
        keep.update((x, y) for y, start, end in JAW.get(pose, ()) for x in range(start, end + 1))
    return keep


def apply(layer, native, edits, visible=None, keep=(), inherit=False):
    top = len(layer) - len(native)
    left = (len(layer[0]) - len(native[0])) // 2
    for (x, y), (old, new) in edits.items():
        ink = layer[y + top][x + left]
        if visible is not None and ((x, y) in keep or visible[y][x] != old):
            continue
        if ink == old or (ink is None and not inherit):
            layer[y + top][x + left] = new


def author(game, source, output):
    with ZipFile(source) as archive:
        entries = {n: archive.read(n) for n in archive.namelist()}
    woman = "Base/walk" in entries
    model = 2099 if woman else 2095
    for combat, tag in enumerate(("walk", "combat")):
        base_name = f"Base/{tag}" if woman else f"Study/{tag}-body"
        layers = {name: [] for name in entries if name.endswith(f"/{tag}-underpaint") or name == base_name}
        for f in range(14 if combat else 15):
            def read(name):
                return art.decode_frame(entries[name], f)[2]

            pose = f + 15 * combat
            native = game.fr(model + combat, f)
            body_layer = read(base_name)
            body = compose(native, body_layer)
            heads = read(f"Base/{tag}-head") if woman else ()
            protected = foreground(read(f"Gladiator/{tag}-regions"), heads, model, pose)
            facing = game.fig(model).parts(combat, f).facing
            edits = body_edits(body, model, pose, facing, protected)
            apply(body_layer, native, edits)
            layers[base_name].append(body_layer)
            for name, frames in layers.items():
                if name == base_name:
                    continue
                dressed_name = name.removesuffix("-underpaint")
                visible = compose(body if woman else native, read(dressed_name))
                keep = foreground(read(dressed_name + "-regions"), heads, model, pose)
                layer = read(name)
                apply(layer, native, edits, visible, keep, inherit=woman)
                frames.append(layer)
        entries.update((name, sprites.encode_frames(frames)) for name, frames in layers.items())
    with TemporaryDirectory() as folder:
        intermediate = Path(folder) / "underpaint.zip"
        with ZipFile(intermediate, "w") as archive:
            for name, data in entries.items():
                archive.writestr(name, data)
        finish_archive(game, intermediate, output, keep_cloak_dyes=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for arg in ("game_dir", "source", "output"):
        parser.add_argument(arg, type=Path)
    args = parser.parse_args()
    author(outfits.Game(args.game_dir), args.source, args.output)
