"""Fit and review the six single-class Mul studies on retail terrain."""
import argparse
from math import cos
from pathlib import Path

from PIL import Image, ImageDraw

import mulstudy as fit
from elfreview import TERRAIN, dwarf, elf, label, loop
from outfitdetail import RAMPS, reference_folds
from wornreview import Atlas


NEW = ("Druid", "Psionicist", "Thief")
REAR = {1, 7, 8, 9, 10, 18, 19, 20, 25}
PROFILE = {2, 11, 12, 13, 14, 15, 22, 23, 26}
TEAL = (17, 69, 70, 71, 40, 72, 73)
MOSS = (208, 69, 188, 53, 189, 54, 226, 55, 227)
# Back corner of the long cloak in each profile and deep lean. The second
# step lifts the corner behind the hip. The fourth drops it toward the heel.
TRAIL = {2: (-2, 21), 11: (-2, 20), 12: (-3, 18), 13: (-4, 19), 14: (-1, 21),
         15: (-3, 21), 17: (19, 15), 21: (2, 19), 22: (-3, 18), 23: (-3, 16),
         24: (1, 21), 26: (0, 23), 27: (19, 11)}

SHORT_TRAIL = {2: (0, 17), 11: (0, 17), 12: (-2, 16), 13: (-2, 17), 14: (1, 18),
               15: (-1, 18), 17: (17, 13), 21: (4, 16), 22: (0, 16), 23: (0, 14),
               24: (1, 18), 26: (2, 19), 27: (16, 10)}


def shade(ramp, light):
    return ramp[max(0, min(len(ramp)-1, round(light)))]


def cape(pose, short):
    shoulder, ribs, waist, hem, lift = fit.ROBE_CUTS[pose]
    sy, sl, sr = shoulder
    wy, wl, wr = waist
    hip = (wl+wr)//2
    if pose == 27:
        # Recoil sends the cloth into the space under the raised arm.
        # The bent thigh stays visible below the fold.
        points = (((9, 6), (12, 6), (16, 8), (15, 10), (12, 10), (8, 9)) if short else
                  ((9, 6), (12, 6), (15, 7), (19, 7), (18, 10), (16, 12), (10, 12), (8, 10)))
    elif pose in TRAIL:
        tx, ty = SHORT_TRAIL[pose] if short else TRAIL[pose]
        right = tx > hip
        near = wr if right else wl
        shoulder_x = sr if right else sl
        edge = 1 if right else -1
        points = ((shoulder_x, sy), (shoulder_x+edge, sy+3), (tx, ty-1),
                  (tx-edge, ty), (near, ty-1), (hip, wy+1), (hip, ribs[0]))
    else:
        ey = wy+2 if short else hem[0]
        if pose == 28:
            ey -= 1
        left, right = (wl-2, wr+1) if short else (hem[1]-1, hem[2]+1)
        points = ((sl, sy), (sr, sy), (sr, ribs[0]), (right, ey-max(0, lift)),
                  (right-2, ey-max(0, lift)+1), (hip+1, ey-1),
                  (hip-2, ey+1), (left, ey-max(0, -lift)), (sl, ribs[0]))
    # Rasterize in native coordinates, allowing the flying corner outside
    # the original bounding box as in the retail cloaks.
    mask = Image.new("1", (64, 54))
    ImageDraw.Draw(mask).polygon([(x+fit.PAD, y) for x, y in points], fill=1)
    return {(x-fit.PAD, y) for y in range(mask.height) for x in range(mask.width) if mask.getpixel((x, y))}


def thief_hood(pose):
    """Round crown, open cheeks, and a trailing nape around the Mul's own head."""
    left, top, spans = fit.HEADS[pose]
    shell = set()
    for y, (a, b) in enumerate(spans):
        # Extend the crown outline by a pixel at the turn; its lower edge
        # leaves the brow and cheek as native skin in front and in profile.
        lo = left+a-(1 if y < 5 else 0)
        hi = left+b+(1 if y < 3 or pose in REAR else 0)
        for x in range(lo, hi+1):
            crown = y < 2
            if pose in REAR:
                crown = True
            elif pose in PROFILE:
                crown |= x < left+a or (y == 2 and x < left+a+2)
            else:
                crown |= x < left+a or x > left+b
            if crown:
                shell.add((x, top+y))
    # Drape the temple panels over the shoulders. On the backswing the
    # left arm is raised behind the head, so the far panel disappears.
    sy, sl, sr = fit.ROBE_CUTS[pose][0]
    if pose in REAR:
        shell.update((left+x, top+y) for y in range(len(spans)-1, len(spans)+3)
                     for x in range(1, 5))
    else:
        bends = [(left-1, sl)]
        if pose in (17, 27):
            bends = []
        if pose not in PROFILE:
            bends.append((left+max(b for _, b in spans)+1, sr))
        for temple, shoulder in bends:
            last = max(top+6, sy+3)
            for y in range(top+2, last+1):
                t = (y-top-2)/(last-top-2)
                x = round(temple*(1-t) + shoulder*t)
                outer = -1 if temple < left else 1
                shell.update(((x, y), (x+outer, y)))
        # Blend the crown into the rims on either side of the open brow.
        a, b = spans[2]
        shell.add((left+a, top+2))
        if pose not in PROFILE:
            shell.add((left+b, top+2))
    # Return the inner lip of the flared temple to the cheek contour.
    # These cells are floor on the bare head, visible between brim and rim.
    returned = {0: ((15, 3), (15, 4)), 3: ((14, 4),), 4: ((13, 3), (13, 4), (5, 5)),
                6: ((14, 4), (14, 5)), 10: ((4, 5),), 21: ((12, 4),),
                24: ((11, 7),), 28: ((15, 3),)}
    shell.update(returned.get(pose, ()))
    if pose == 17:
        shell.difference_update(((3, 6), (2, 8)))
    return shell


def draw(game, pose, swatches):
    rows = fit.fitted_rows(game, pose)
    body = rows["Body base"]
    h, w = len(body), len(body[0])-2*fit.PAD
    cb, f = divmod(pose, 15)
    figure = game.fig(fit.MODEL)
    parts = figure.parts(cb, f)
    raw = game.fr(fit.MODEL+cb, f)
    bow = game.bow(figure, raw, parts) if pose in (24, 25, 26) else set()
    limbs = {(hx+dx, hy+dy) for hx, hy in parts.hands.values()
             for dx, dy in ((0, 0), (-1, 0), (1, 0), (0, -1), (0, 1))}
    if pose in fit.CROSSING_ARMS:
        elbow, bend, wrist, thickness = fit.CROSSING_ARMS[pose]
        arm = Image.new("1", (w, h))
        ImageDraw.Draw(arm).line((elbow, bend, wrist), fill=1, width=thickness)
        limbs.update((x, y) for y in range(h) for x in range(w) if arm.getpixel((x, y)))
    protected = fit.head_pixels(pose, w, h) | fit.neckline_pixels(pose, w, h)
    cuts = fit.ROBE_CUTS[pose]
    sy, sl, sr = cuts[0]
    wy, wl, wr = cuts[2]
    hip = (wl+wr)/2
    panels = {"Druid": cape(pose, True), "Thief": cape(pose, False)}
    # At a swinging elbow open the cape back out to the floor, or continue
    # its lining behind the wrist when that side of the cape is on top.
    for role, panel in panels.items():
        if pose == 10:
            panel.add((2, 13))
        if role == "Druid":
            for pt in {0: ((4, 13),), 6: ((16, 12), (15, 13), (15, 14)),
                       12: ((3, 16),), 13: ((0, 17), (1, 17)), 14: ((3, 18),), 17: ((15, 13),)}.get(pose, ()):
                panel.add(pt)
    hood = thief_hood(pose)
    face = fit.head_pixels(pose, w, h)
    hx, hy, spans = fit.HEADS[pose]
    out = {name: [row[:] for row in body] for name in NEW}
    for py in range(h):
        for px in range(-fit.PAD, w+fit.PAD):
            x, y = (w-1-px, h-1-py) if pose == 28 else (px, py)
            point = px, py
            i = px+fit.PAD
            skin = body[py][i]
            if point in bow or (skin is not None and point in limbs):
                continue
            grain = swatches["slate"][(y-wy) % 8][(x-wl) % 8]
            depth = (y-sy)/(wy-sy)
            axis = (sl+sr)/2 + (hip-(sl+sr)/2)*min(max(depth, 0), 1)
            if point not in protected:
                # Use the proven armhole and neckline of the Mul tunic,
                # then fit the shorts to each leg inside its native silhouette.
                tailored = skin is not None and rows["Cleric"][py][i] != skin
                if tailored and y <= wy+4:
                    u = (x-axis)/max(2, (wr-wl)*.58)
                    grain_light = .70*grain - 1.4*abs(u+.23)
                    for role, ramp in (("Druid", RAMPS["ochre"]), ("Thief", RAMPS["hide"]), ("Psionicist", TEAL)):
                        light = .62*(len(ramp)-1) + grain_light
                        if role == "Psionicist":
                            # Narrow diagonal folds curve across the rib cage.
                            light = 3.65 + .35*grain - .8*abs(u+.2) + 1.05*cos((y-sy)*.8 + (x-axis)*.51)
                        else:
                            light += 1.7*cos(x-axis+.32*(y-wy))
                        if y == wy or (y == wy+1 and u < -.55):
                            color = 94 if u < 0 else 89
                        else:
                            color = shade(ramp, light - (1.2 if y > wy else 0))
                        out[role][py][i] = color
                for role, panel in panels.items():
                    if (x, y) not in panel:
                        continue
                    # Keep arms and the front opening on top. In profile
                    # only the trailing side crosses the visible tunic.
                    if skin is not None:
                        if not tailored and (pose not in REAR or y <= wy):
                            continue
                        if pose in TRAIL:
                            direction = 1 if TRAIL[pose][0] > hip else -1
                            if (x-axis)*direction < .6:
                                continue
                        elif pose not in REAR and abs(x-axis) < (.7+2*min(1, max(0, depth))):
                            continue
                    ramp = MOSS if role == "Druid" else RAMPS["slate"]
                    swing = (TRAIL[pose][0]-hip)*.52 if pose in TRAIL else cuts[3][1]-wl
                    fold = x-axis - swing*min(depth, 1.7)
                    light = .57 + .14*cos(.94*fold+.65*depth) + .045*grain
                    if (x+1, y) not in panel or (x, y+1) not in panel:
                        light -= .21
                    out[role][py][i] = shade(ramp, light*(len(ramp)-1))
            if (x, y) in hood:
                # Leave the eye, ear, cheek and jaw exactly as drawn on the
                # clean head, including the low face on the second strike.
                if pose not in REAR and y-hy >= 3 and skin is not None and point in face:
                    continue
                k = min(len(spans)-1, max(0, y-hy))
                a, b = spans[k]
                across = (x-hx-a)/max(1, b-a)
                light = 10.6 - 6*abs(across-.28) - .67*k + .50*grain
                if (x, y+1) not in hood or (x+1, y) not in hood:
                    light -= 2
                out["Thief"][py][i] = shade(RAMPS["slate"], light)
    return rows | out


def render(game_dir, output):
    atlas = Atlas(game_dir)
    game = atlas.game
    swatches = reference_folds(game)
    sand = Image.open(TERRAIN).convert("RGB").crop((39, 130, 93, 181))
    paving = Image.open(TERRAIN.with_name("2026-11-09-figures-all-gone.png")
                        ).convert("RGB").crop((158, 21, 212, 72))
    roles = fit.ROLES + NEW
    sheet = Image.new("RGB", (126+110*len(roles), 48+105*29), dwarf.PAPER)
    label(sheet, (12, 9), "Mul poses", 18)
    for j, role in enumerate(roles):
        label(sheet, (177+j*110, 12), role, 15, "ma")
    frames = []
    for pose, name in enumerate(dwarf.NAMES):
        rows = draw(game, pose, swatches)
        y = 44+105*pose
        label(sheet, (10, y+27), f"{pose:02}", 14)
        label(sheet, (10, y+49), name, 13)
        for j, role in enumerate(roles):
            tile = elf.placed_tile(game, rows[role], sand, 2, 0, 0, 0)
            sheet.paste(tile, (123+j*110, y))
        page = Image.new("RGB", (820, 463), dwarf.PAPER)
        label(page, (12, 8), "Mul single classes", 20)
        label(page, (807, 8), f"{pose:02}   {name}", 16, "ra")
        for j, role in enumerate(("Original",)+NEW):
            x = 22+203*j
            label(page, (x+81, 41), "Retail Mul" if j == 0 else role, 16, "ma")
            page.paste(elf.placed_tile(game, rows[role], sand, 3, 0, 0, 0), (x, 65))
            for k, floor in enumerate((sand, paving)):
                page.paste(elf.placed_tile(game, rows[role], floor, 1, 0, 0, 0), (x+25+58*k, 225))
        label(page, (12, 286), "Retail figures and approved human outfits", 16)
        for j, (ref, caption) in enumerate(((1252, "Retail Warrior"), ("Druid", "Human Druid"),
                                            ("Psionicist", "Human Psionicist"), (724, "Retail Mage"),
                                            (630, "Retail Thief"))):
            x = 8+j*163
            if isinstance(ref, int):
                cb, f = divmod(pose, 15)
                pic = ref+cb
                if f >= game.count(pic):
                    pic, f = ref, 0
                    caption += " (idle)"
                sample = game.fr(pic, f)
                large = elf.placed_tile(game, sample, sand, 2, 0, 0, 0)
                small = elf.placed_tile(game, sample, paving, 1, 0, 0, 0)
            else:
                atlas.floor = sand
                large = atlas.tile(300, pose, ref, "Class colors", 2)
                atlas.floor = paving
                small = atlas.tile(300, pose, ref, "Class colors", 1)
            label(page, (x+80, 316), caption, 14, "ma")
            page.paste(large, (x, 344))
            page.paste(small, (x+108, 395))
        frames.append(page)
    output.mkdir(parents=True, exist_ok=True)
    sheet.save(output/"mul-singles-poses.png")
    loop(frames, output/"mul-singles.gif")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("game_dir", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    render(args.game_dir, args.output)
