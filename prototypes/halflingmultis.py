"""Render the twelve halfling pairs and two triples from the approved single outfits."""
import argparse
from pathlib import Path

from PIL import Image

import halflingsingles as singles
import halflingstudy as fit
from elfreview import TERRAIN, dwarf, elf, label, loop
from outfitdetail import RAMPS, reference_folds
from wornreview import Atlas
from multiclasscolor import TEAL_SCALE, dye_fitted_hoods

GROUPS = {
    "cleric": ("Cleric/Fighter", "Cleric/Psionicist", "Cleric/Ranger", "Cleric/Thief"),
    "druid": ("Druid/Fighter", "Druid/Psionicist", "Druid/Thief"),
    "leather": ("Fighter/Psionicist", "Fighter/Thief", "Psionicist/Ranger",
                "Psionicist/Thief", "Ranger/Thief"),
    "triples": ("Fighter/Psionicist/Thief", "Psionicist/Ranger/Thief"),
}
DRUID_GUARD = dict(zip(fit.BONE, (207, 188, 53, 55, 199, 62), strict=True))
LEAF = set(RAMPS["leaf"])
SLATE = set(RAMPS["slate"])
CLOTH = set().union(*RAMPS.values(), fit.BONE, singles.TEAL)
# Hip-relative sewing line. On the downward front strike and recoil the
# near arm crosses the belt and the usable hip lies on the far side.
WAIST_SHIFT = {12: (1, 2), 13: (-1, 1), 15: (2, 1), 16: (1, 0), 17: (1, 0), 22: (-1, 0),
               23: (1, 0), 24: (0, 1), 26: (0, 1), 27: (1, 1)}


def hooded(parent, rows, pose, dx, dy, twin):
    out = [row[:] for row in rows[parent]]
    shell, opening, _ = singles.hood(pose)
    for x, y in shell:
        u, v = 4+dx+x, dy+y
        if 0 <= v < len(out) and 0 <= u < len(out[v]) and rows["Thief"][v][u] in SLATE:
            out[v][u] = rows["Thief"][v][u]
    if twin:
        bow = {(x, y) for y, lo, hi in fit.BOW_ARCS.get(pose, ()) for x in range(lo, hi+1)}
        if pose == 24:
            bow.add((6-dx, 16-dy))
        singles.tuck_hair(pose, out, rows["Original"], dx, dy, bow, shell, opening,
                          twin[parent+"/Thief"], twin["Original"])
    return out


def waist_detail(game, pose, rows, base, accent, dx, dy, grain, above_belt=False):
    out = [row[:] for row in rows[base]]
    (hx, hy) = fit.CUT[pose][1]
    shift, drop = WAIST_SHIFT.get(pose, (0, 0))
    hx, hy = hx+shift, hy+drop
    wrap = accent == "Psionicist"
    if above_belt:
        hy -= 2
    head = fit.head_pixels(pose)
    protected = singles.hood(pose)[0] | head
    gx, gy = fit.SHOULDER[pose]
    for v, row in enumerate(out):
        for u, c in enumerate(row):
            x, y = u-4-dx, v-dy
            if (not wrap and (x, y) not in protected and 0 <= y-gy <= 2 and abs(x-gx) <= 2
                    and c is not None and c != rows["Body base"][v][u]
                    and rows["Fighter"][v][u] in fit.BONE):
                # Use the Fighter's own guard where the arm emerges from the
                # outer garment. Let hair and the near edge of a cloak overlap.
                hidden = (base == "Druid" and c in singles.MOSS or base == "Thief" and c in SLATE)
                if not hidden:
                    bone = rows["Fighter"][v][u]
                    out[v][u] = DRUID_GUARD[bone] if base == "Druid" else bone
            if (wrap and base in ("Fighter", "Fighter/Thief") and c in fit.BONE
                    and c == rows["Fighter"][v][u] and c != rows["Body base"][v][u]
                    and (x, y) not in head
                    and 0 <= y-gy <= 2 and abs(x-gx) <= (2 if y-gy == 1 else 1)):
                out[v][u] = TEAL_SCALE[c]
            # Clip the fitting to visible cloth over the pelvis. The trailing
            # end of the profile cloak passes behind the hip and carries no belt.
            if (c not in CLOTH or c == rows["Body base"][v][u] or (x, y) in protected
                    or abs(x-hx) > (4 if pose in fit.PROFILE else 5)):
                continue
            across = x-hx
            slope = max(-2, min(2, round(across*(.38 if wrap else .17))))
            depth = y-hy+slope
            side = -1 if pose in fit.REAR else 1
            knot = across*side
            if wrap:
                visible = depth in (-1, 0) or (0 <= knot <= 1 and depth == 1 and not above_belt)
                if above_belt:
                    # The knot turns down opposite the sword tab. Where the
                    # arm crosses the ribs, this end still shows at the hip.
                    visible |= -3 <= knot <= -1 and depth in (1, 2, 3)
                    if c != rows["Thief"][v][u]:
                        visible = False
                if pose == 13:
                    # As the forearm swings across the chest the tucked end
                    # remains visible along the outside edge of the near hip.
                    visible |= (x in (1, 2) and y in (11, 12) or x == 1 and y in (13, 14))
                if pose == 15 and above_belt:
                    visible |= (x in (8, 9) and y == 14 or x == 9 and y in (15, 16))
            else:
                visible = depth in (0, 1) or (1 <= knot <= 2 and depth in (2, 3))
            if not visible:
                continue
            red, green, blue = game.palette[c]
            relief = (.30*red+.59*green+.11*blue)/125
            weave = grain[(y-hy)%8][(x-hx)%8]
            if wrap:
                light = 2.8+1.65*relief+.45*weave+1.2*(depth < 0)-.23*abs(across)
                out[v][u] = fit.dye(singles.TEAL, light)
            elif knot == 1 and depth == 0:
                out[v][u] = 199
            else:
                out[v][u] = fit.dye(RAMPS["hide"], 3.8+1.2*relief+.45*weave-1.4*(depth > 0))
    return out


def ranger_robe(rows, pose, dx, dy):
    # Use the Ranger's own swinging hem. Leave a turned strip of linen
    # beside the green and keep the full Cleric skirt beneath the cloak.
    out = [r[:] for r in rows["Cleric"]]
    hx, hy = fit.CUT[pose][1]
    for v, row in enumerate(rows["Ranger"]):
        for u, c in enumerate(row):
            if c not in LEAF or c == rows["Body base"][v][u]:
                continue
            x, y = u-4-dx, v-dy
            inner = out[v][u] in RAMPS["linen"]
            if inner and ((x > hx and pose in fit.REAR) or
                          (abs(x-hx) <= 1 and pose not in fit.REAR) or y > hy+3):
                continue
            out[v][u] = c
    return out


def draw(game, pose, swatches):
    by_model = {}
    twin = None
    for model in fit.MODELS:
        rows = singles.draw(game, model, pose, swatches)
        if pose == 28:
            rows = {k: fit.flip(v) for k, v in rows.items()}
        dx, dy = fit.CUT[pose][-1] if twin else (0, 0)
        for base in ("Cleric", "Druid", "Ranger"):
            rows[base+"/Thief"] = hooded(base, rows, pose, dx, dy, twin)
        rows["Cleric/Ranger"] = ranger_robe(rows, pose, dx, dy)
        for name, base, accent in (
            ("Cleric/Fighter", "Cleric", "Fighter"), ("Cleric/Psionicist", "Cleric", "Psionicist"),
            ("Druid/Fighter", "Druid", "Fighter"), ("Druid/Psionicist", "Druid", "Psionicist"),
            ("Fighter/Psionicist", "Fighter", "Psionicist"), ("Fighter/Thief", "Thief", "Fighter"),
            ("Psionicist/Ranger", "Ranger", "Psionicist"), ("Psionicist/Thief", "Thief", "Psionicist"),
            ("Fighter/Psionicist/Thief", "Fighter/Thief", "Psionicist"),
            ("Psionicist/Ranger/Thief", "Ranger/Thief", "Psionicist"),
        ):
            rows[name] = waist_detail(game, pose, rows, base, accent, dx, dy,
                                      swatches["slate"], above_belt=(name == "Fighter/Psionicist/Thief"))
        # Finish each hood after the near arm, hair and both waist layers.
        # Keep the donor for the woman's tucked hair in its original palette.
        twin = rows
        shell, _, _ = singles.hood(pose)
        rows = dye_fitted_hoods(rows, ((4+dx+x, dy+y) for x, y in shell))
        by_model[model] = {k: fit.flip(v) for k, v in rows.items()} if pose == 28 else rows
    return by_model


def parents(name):
    parts = name.split("/")
    if len(parts) == 2:
        return parts[0], name, parts[1]
    a, b, c = parts
    return a+"/"+b, a+"/"+c, name, b+"/"+c


def caption(im, x, y, name, size):
    for line, part in enumerate(name.split("/")):
        label(im, (x, y+line*(size+1)), part, size, "ma")


def render(game_dir, output):
    atlas = Atlas(game_dir)
    game = atlas.game
    swatches = reference_folds(game)
    sand = Image.open(TERRAIN).convert("RGB").crop((39, 130, 93, 181))
    paving = Image.open(TERRAIN.with_name("2026-11-09-figures-all-gone.png")).convert("RGB").crop(
        (164, 21, 218, 72))
    frames = {group: [] for group in GROUPS}
    names = [name for roles in GROUPS.values() for name in roles]
    sheets = {m: Image.new("RGB", (150+82*len(names), 87+29*64), dwarf.PAPER) for m in fit.MODELS}
    for m, sheet in sheets.items():
        label(sheet, (10, 8), "Halfling "+("man" if m == 2068 else "woman")+" · twelve pairs and two triples", 17)
        for j, name in enumerate(names):
            caption(sheet, 191+j*82, 36, name, 12)
    for pose, pose_name in enumerate(dwarf.NAMES):
        builds = draw(game, pose, swatches)
        tiles = {}
        for model, rows in builds.items():
            singles.verify_face(rows, model, pose, names)
            for name in names:
                for parent in parents(name):
                    if parent != name and rows[name] == rows[parent]:
                        raise ValueError(f"{model}, pose {pose}: {name} matches {parent}")
            for k in names + list(fit.ROLES[2:]) + list(singles.SINGLES):
                tiles[model, k] = [
                    elf.placed_tile(game, rows[k], floor, 1, 0, 0, 0).crop((7, 18, 47, 50))
                    for floor in (sand, paving)]
            sheet = sheets[model]
            label(sheet, (8, 105+64*pose), f"{pose:02}  {pose_name}", 14)
            for j, name in enumerate(names):
                sheet.paste(tiles[model, name][0].resize((80, 64), Image.Resampling.NEAREST),
                            (150+82*j, 87+64*pose))
        for group, roles in GROUPS.items():
            triple = group == "triples"
            width = max(740, 80+len(roles)*148)
            panel = (width-70)//len(roles)
            page = Image.new("RGB", (width, 510), dwarf.PAPER)
            label(page, (12, 7), "Halfling "+("three-class" if triple else "two-class")+" outfits", 19)
            label(page, (width-12, 10), f"{pose:02}  {pose_name}", 15, "ra")
            for j, name in enumerate(roles):
                cx = 65+panel*j+panel//2
                label(page, (cx, 40), name, 14, "ma")
                comparison = parents(name)
                stride = 68 if triple else 42
                for i, model in enumerate(fit.MODELS):
                    y = 65+i*169
                    if j == 0:
                        label(page, (9, y+42), ("Man", "Woman")[i], 14)
                    tile = tiles[model, name][0]
                    page.paste(tile.resize((120, 96), Image.Resampling.NEAREST), (cx-60, y))
                    for n, parent in enumerate(comparison):
                        x = cx+int((n-(len(comparison)-1)/2)*stride)
                        for floor in (0, 1):
                            page.paste(tiles[model, parent][floor], (x-20, y+99+floor*32))
            if triple:
                for j, name in enumerate(roles):
                    cx = 65+panel*j+panel//2
                    for n, parent in enumerate(parents(name)):
                        caption(page, cx+int((n-1.5)*68), 401, "Triple" if parent == name else parent, 11)
            else:
                label(page, (width//2, 400), "At game size, read left to right for the first class, the pair and the second class.",
                      13, "ma")
            for j, (npc, title) in enumerate(((1563, "Retail Priest"), (630, "Retail Thief"),
                                               (1252, "Retail Warrior"), (300, "Human Psionicist"))):
                frame = pose
                if npc != 300 and pose%15 >= game.count(npc+pose//15):
                    frame, title = 0, title+" (idle)"
                x = width*(2*j+1)//8
                label(page, (x, 432), title, 13, "ma")
                for n, floor in enumerate((sand, paving)):
                    atlas.floor = floor
                    page.paste(atlas.tile(npc, frame, "Psionicist", "Class colors", 1),
                               (x-54+n*54, 451))
            frames[group].append(page)
    output.mkdir(parents=True, exist_ok=True)
    for group, pages in frames.items():
        loop(pages, output/f"halfling-multiclass-{group}.gif")
    for model, sheet in sheets.items():
        sex = "man" if model == 2068 else "woman"
        sheet.save(output/f"halfling-{sex}-multiclass.png")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("game_dir", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    render(args.game_dir, args.output)
