"""Fit the legal Mul multiclasses to the approved single-class study."""
import argparse
from pathlib import Path

from PIL import Image

import mulfront
import mulsingles as singles
import mulstudy as fit
from elfreview import TERRAIN, dwarf, elf, label, loop
from halflingmultis import caption, parents
from outfitdetail import reference_folds
from wornreview import Atlas


GROUPS = {
    "cleric": ("Cleric/Fighter", "Cleric/Psionicist", "Cleric/Thief"),
    "druid": ("Druid/Fighter", "Druid/Psionicist", "Druid/Thief"),
    "leather": ("Fighter/Psionicist", "Fighter/Thief", "Psionicist/Thief"),
    "triples": ("Cleric/Fighter/Thief", "Druid/Fighter/Thief", "Fighter/Psionicist/Thief"),
}
BELT = (88, 89, 91, 92, 94, 96, 98)
# Centres of the hip still visible beyond the passing forearm.
HIP_OFFSET = {2: (-1, 1), 11: (-1, 2), 12: (1, 1), 13: (0, 1), 15: (1, 1), 17: (0, 1),
              22: (-1, 0), 23: (-1, 0), 24: (-1, 1), 26: (-1, 1), 27: (1, 0)}


def hood_pixels(pose):
    if pose not in mulfront.FRONT:
        return singles.thief_hood(pose)
    hx, hy, spans = fit.HEADS[pose]
    crown = {(hx+x, hy+y) for y, (lo, hi) in enumerate(spans[:3])
             for x in range(lo, hi+1)}
    return crown | {(hx+x-2, hy+y) for y, row in enumerate(mulfront.COWL)
                    for x, ink in enumerate(row) if ink != " "}


def draw(game, pose, swatches):
    rows = singles.draw(game, pose, swatches)
    body = rows["Body base"]
    h, w = len(body), len(body[0])-2*fit.PAD
    hood = hood_pixels(pose)
    gx, gy, _, _ = fit.HIDE_POINTS[pose]
    _, shoulder_left, shoulder_right = fit.ROBE_CUTS[pose][0]
    inward = 1 if gx < (shoulder_left+shoulder_right)/2 else -1
    profile_guard = pose in fit.PROFILE_HIDE
    wy, left, right = fit.ROBE_CUTS[pose][2]
    dx, dy = HIP_OFFSET.get(pose, (0, 0))
    hip = (left+right)/2+dx

    # Sample the native figure in drawing coordinates. The fallen cel is
    # rotated; its knots and guard must turn with it.
    def pixel(x, y):
        if pose == 28:
            x, y = w-1-x, h-1-y
        return x+fit.PAD, y

    def with_hood(base):
        out = [row[:] for row in rows[base]]
        for x, y in hood:
            u, v = pixel(x, y)
            if 0 <= v < h and 0 <= u < len(out[v]) and rows["Thief"][v][u] in singles.SLATE:
                out[v][u] = rows["Thief"][v][u]
        return out

    def with_waist(base, accent, above_belt=False):
        out = [row[:] for row in rows[base]]
        wrap = accent == "Psionicist"
        ramp = singles.TEAL if wrap else BELT
        if not wrap:
            for y in range(gy-2, gy+4):
                for x in range(gx-3, gx+5):
                    u, v = pixel(x, y)
                    if not (0 <= v < h and 0 <= u < len(out[v])):
                        continue
                    bone = rows["Fighter"][v][u]
                    # Hide and bone share shadow colours. Transfer those
                    # shadows only within the actual shoulder scale.
                    if bone in fit.JERKIN and not fit.bone_surface(x, y, gx, gy, inward, profile_guard):
                        continue
                    if (bone in fit.BONE and bone != body[v][u] and body[v][u] is not None
                            and not ("Thief" in base and (x, y) in hood)):
                        out[v][u] = bone
        # The band lies on visible garment pixels over the pelvis. Let the
        # parent's armhole, passing hand and free cloak corner occlude it.
        for y in range(wy-5, wy+6):
            for x in range(left-1+dx, right+2+dx):
                u, v = pixel(x, y)
                if not (0 <= v < h and 0 <= u < len(out[v])):
                    continue
                cloth = rows[base][v][u]
                if cloth is None or cloth == body[v][u] or ("Thief" in base and (x, y) in hood):
                    continue
                across = x-hip
                depth = y-wy-dy+int(above_belt)*2+round(across*(.32 if wrap else .17))
                knot = -across if pose in singles.REAR else across
                # On the three-class fitting the teal end hangs opposite
                # the leather sword tab. The twisting follow-through exposes
                # the returning edge on the near side of the hip.
                end = -knot if above_belt and pose != 17 else knot
                tail = 1 <= end <= 3 and depth in (1, 2)
                if depth not in (-1, 0) and not tail:
                    continue
                red, green, blue = game.palette[cloth]
                light = (.3*red+.55*green+.15*blue)/110
                grain = swatches["slate"][(y-wy)%8][(x-left)%8]
                level = 2.6+light+.65*grain+1.1*(depth == -1)-.7*tail-.15*across
                # A bound edge on the teal wrap and two leather keepers
                # follow the same sloping belt through the turn. Break their
                # highlights where the parent cloth folds into shadow.
                if wrap:
                    level += .8*(depth == -1 and grain >= 0) - 1.15*(depth == 0)
                    if tail and round(end) == 2:
                        level += 1.4
                else:
                    keeper = round(knot) in (-3, 2) and depth in (-1, 0)
                    level += 1.7*keeper - 1.3*(depth == 0 and not keeper)
                out[v][u] = singles.shade(ramp, level)
                if not wrap and round(knot) == 1 and depth == 0:
                    out[v][u] = 199
        return out

    for base in ("Cleric", "Druid"):
        rows[base+"/Thief"] = with_hood(base)
        for accent in ("Fighter", "Psionicist"):
            rows[base+"/"+accent] = with_waist(base, accent)
    rows["Fighter/Psionicist"] = with_waist("Fighter", "Psionicist")
    for accent in ("Fighter", "Psionicist"):
        rows[accent+"/Thief"] = with_waist("Thief", accent)
    for base in ("Cleric", "Druid"):
        rows[base+"/Fighter/Thief"] = with_waist(base+"/Thief", "Fighter")
    rows["Fighter/Psionicist/Thief"] = with_waist("Fighter/Thief", "Psionicist", above_belt=True)
    return rows


def render(game_dir, output):
    atlas = Atlas(game_dir)
    game = atlas.game
    swatches = reference_folds(game)
    sand = Image.open(TERRAIN).convert("RGB").crop((39, 130, 93, 181))
    paving = Image.open(TERRAIN.with_name("2026-11-09-figures-all-gone.png")).convert("RGB").crop((158, 21, 212, 72))
    builds = [name for group in GROUPS.values() for name in group]
    sheet = Image.new("RGB", (134+88*len(builds), 88+29*80), dwarf.PAPER)
    label(sheet, (10, 7), "Mul multiclass outfits", 20)
    overview = Image.new("RGB", (626, 508), dwarf.PAPER)
    label(overview, (10, 7), "Mul multiclass outfits", 20)
    label(overview, (10, 35), "Front idle and rear walk step two", 13)
    for j, build in enumerate(builds):
        caption(sheet, 176+88*j, 34, build, 12)
        label(overview, (104+208*(j%3), 63+110*(j//3)), build, 14, "ma")
    frames = {group: [] for group in GROUPS}
    for pose, title in enumerate(dwarf.NAMES):
        rows = draw(game, pose, swatches)
        tiles = {key: [elf.placed_tile(game, rows[key], ground, 1, 0, 0, 0).crop((5, 7, 49, 51))
                       for ground in (sand, paving)] for key in rows}
        label(sheet, (6, 102+80*pose), f"{pose:02} {title}", 13)
        for j, name in enumerate(builds):
            for member in parents(name):
                if member != name and rows[member] == rows[name]:
                    raise ValueError(f"{name} loses its distinction from {member} in pose {pose}")
            tile = tiles[name][0].crop((0, 5, 44, 44))
            if pose in (0, 8):
                ox = 16+208*(j%3)+(88 if pose == 8 else 0)
                overview.paste(tile.resize((88, 78), Image.Resampling.NEAREST), (ox, 85+110*(j//3)))
            sheet.paste(tile.resize((88, 78), Image.Resampling.NEAREST), (134+88*j, 88+80*pose))
        for group, names in GROUPS.items():
            page = Image.new("RGB", (750, 405), dwarf.PAPER)
            label(page, (10, 8), "Mul multiclass outfits", 19)
            label(page, (740, 9), f"{pose:02}  {title}", 16, "ra")
            for j, name in enumerate(names):
                cx = 125+250*j
                label(page, (cx, 44), name, 15, "ma")
                page.paste(tiles[name][0].resize((132, 132), Image.Resampling.NEAREST), (cx-66, 68))
                family = parents(name)
                for n, member in enumerate(family):
                    x = cx+int((n-(len(family)-1)/2)*60)
                    page.paste(tiles[member][1], (x-22, 203))
                    caption(page, x, 250, "Pair" if member == name and len(family)==3 else
                            "Triple" if member == name else member, 11)
            for j, (npc, name) in enumerate(((1563, "SL Priest"), (630, "SL Thief"), (1252, "SL Warrior"))):
                ref = pose if pose%15 < game.count(npc+pose//15) else 0
                atlas.floor = sand
                tile = atlas.tile(npc, ref, "", "", 1)
                cx = 125+250*j
                page.paste(tile.resize((108, 102), Image.Resampling.NEAREST), (cx-54, 281))
                label(page, (cx, 384), name+(" (idle)" if ref!=pose else ""), 12, "ma")
            frames[group].append(page)
    output.mkdir(exist_ok=True, parents=True)
    overview.save(output/"mul-multiclass.png")
    sheet.save(output/"mul-multiclass-poses.png")
    for group, pages in frames.items():
        loop(pages, output/f"mul-multiclass-{group}.gif")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("game_dir", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    render(args.game_dir, args.output)
