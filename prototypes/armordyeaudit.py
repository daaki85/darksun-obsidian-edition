"""Compare armor with the same pose's original class outfit in encoded Loader pictures.

Run: python prototypes/armordyeaudit.py GAME_DIR OUTPUT_DIR [FIGURE ...]
frames.csv measures the visible garment, spill, palette detail, and original
class colors. parents.csv checks whether multiclass artwork that differed from
its parent can still be distinguished after putting the same armor on both.
"""
import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

from studygeartest import roles_for, array
from wornreview import Atlas, art, sg, sprites
from dsloader import classoutfits as co

# Narrow, diagnostic sets of native swatches. Measure only authored clothing
# surfaces, so surrounding unaltered skin and hair cannot pass the color check.
PIGMENTS = {
    "Cleric": (61, 62, 63, 121, 123, 125, 126, 155, 199),
    "Druid": (53, 54, 55, 56, 57, 188, 189, 190, 191, 225, 226, 227),
    "Fighter": (*range(88, 105), 61, 62, 63, 155, 168, 169, 194, 199, 204, 205, 206, 207),
    "Gladiator": (*range(88, 105), 64, 65, 66, 168, 169, 204, 205, 207),
    "Preserver": (58, 59, 60, 74, 112, 113, 115, 117, 118, 174, 175, 176, 239, 232),
    "Psionicist": (40, 69, 70, 71, 72, 73),
    "Ranger": (53, 54, 55, 56, 57, 188, 189, 190, 191, 225, 226, 227),
    "Thief": (*range(17, 32), 48, 49, 50),
}
PIGMENTS.update(Priest=PIGMENTS["Cleric"], Warrior=PIGMENTS["Fighter"], Mage=PIGMENTS["Preserver"])
FRAMES = ("obj", "role", "pose", "equipment", "changed", "garment", "outside", "silhouette", "bow",
          "glints", "glints_outside", "regional_dye", "edges", "edges_kept", "strong_folds", "strong_folds_kept",
          "native_color", "native_color_kept")
PARENTS = ("obj", "role", "parent", "pose", "equipment", "native_differences",
           "equipped_differences", "original_pixels_still_distinct")


def edge_counts(base, worn, surface, rgb, light):
    """Check neighboring unlike RGB colors, and folds with >=16/255 original luma contrast."""
    edges = kept = folds = ordered = 0
    for first, second in (((slice(None), slice(1, None)), (slice(None), slice(None, -1))),
                          ((slice(1, None), slice(None)), (slice(None, -1), slice(None)))):
        a, b = base[first], base[second]
        c, d = worn[first], worn[second]
        on_cloth = surface[first] & surface[second]
        pair = on_cloth & (rgb[a] != rgb[b])
        edges += np.count_nonzero(pair)
        kept += np.count_nonzero(pair & (rgb[c] != rgb[d]))
        step = light[a] - light[b]
        dyed_step = light[c] - light[d]
        strong = on_cloth & (abs(step) >= 16)
        folds += np.count_nonzero(strong)
        ordered += np.count_nonzero(strong & (np.sign(step) * dyed_step >= 4))
    return edges, kept, folds, ordered


def mask(shape, points, pad):
    result = np.zeros(shape, bool)
    sx, sy = pad
    for x, y in points:
        result[y + sy, x + sx] = True
    return result


def audit(atlas, obj, frame_rows, parent_rows):
    # Use packed RGB for comparisons; a few game palette indices look identical.
    rgb = np.array([r << 16 | g << 8 | b for r, g, b in atlas.game.palette])
    rgb[255] = -1  # A transparent pixel has no visible palette color.
    light = np.array([.30*r + .59*g + .11*b for r, g, b in atlas.game.palette])
    cases = {"Leather": (6, 7, 8), "Plate": (88, 25, 26), "Magic chest": (88 | sg.MAGIC_ARMOUR,),
             "Ashen robe": atlas.gear["Ashen Robe"][1], "Veiled robe": atlas.gear["Veiled Robe"][1]}
    model = obj if obj in co.HALF_ELF_SOURCES else atlas.pictures.model(obj)
    for combat in (False, True):
        pad = sprites.room(combat)

        def render(role, armor):
            chunk = atlas.pictures.build(obj, combat, {}, armor, role=role)
            return [array(art.decode_frame(chunk, f)[2]) for f in range(14 if combat else 15)]

        art_by_role = {}
        for role in filter(None, roles_for(obj)):
            frame = co.frames(role, combat, model)
            base = render(role, ())
            art_by_role[role] = {"Empty": base}
            pigments = tuple({p for name in role.split("/") for p in PIGMENTS[name]})
            for name, kit in cases.items():
                worn = render(role, kit)
                art_by_role[role][name] = worn
                for f, (original, result, field) in enumerate(zip(base, worn, frame)):
                    points = field.regions
                    upper = set(points[co.CHEST])
                    lower = set(points[co.LEGS])
                    body = upper | lower | set(points[co.ARMS])
                    cloak = {(x, y) for x, y, _ in field.cloak}
                    # The two robes own upper cloth plus exposed skirt; solver may protect
                    # more pixels inside these bounds. Measure full sets on all body slots.
                    allowed = upper if name == "Magic chest" else upper | lower if name.endswith("robe") else body
                    owned = mask(original.shape, allowed, pad)
                    surface = mask(original.shape, body | cloak, pad) & (original != 255)
                    diff = original != result
                    glints = diff & np.isin(result, tuple(c for group in sg.GLOWS for c in group))
                    regional = diff & ~glints & ~(((result >= 16) & (result <= 79)) |
                                                    ((result >= 128) & (result <= 222)) | (result == 254))
                    on_color = surface & np.isin(original, pigments)
                    texture = owned & (original != 255)
                    frame_rows.writerow((obj, role, f + 15*combat, name, diff.sum(), texture.sum(),
                                         (diff & ~owned).sum(), ((original == 255) != (result == 255)).sum(),
                                         (diff & mask(original.shape, points[co.BOW], pad)).sum(),
                                         glints.sum(), (glints & ~owned).sum(), regional.sum(),
                                         *edge_counts(original, result, texture, rgb, light),
                                         on_color.sum(), (on_color & (rgb[original] == rgb[result])).sum()))
        for role, pictures in art_by_role.items():
            parts = role.split("/")
            if len(parts) < 2:
                continue
            for i in range(len(parts)):
                parent = "/".join(parts[:i] + parts[i+1:])
                if parent not in art_by_role:
                    continue
                other = art_by_role[parent]
                for name in cases:
                    for f, (base, dressed, parent_base, parent_dressed) in enumerate(
                            zip(pictures["Empty"], pictures[name], other["Empty"], other[name])):
                        cue = (base != 255) & (rgb[base] != rgb[parent_base])
                        still_visible = cue & (rgb[dressed] != rgb[parent_dressed])
                        parent_rows.writerow((obj, role, parent, f + 15*combat, name, cue.sum(),
                                              still_visible.sum(), (still_visible & (base == dressed)).sum()))


def summarize(output):
    summary = defaultdict(Counter)
    with (output / "frames.csv").open() as stream:
        for row in csv.DictReader(stream):
            total = summary[row["equipment"]]
            total["poses"] += 1
            total["lost_color"] += int(row["native_color"]) > 0 and int(row["native_color_kept"]) == 0
            for key in ("edges", "edges_kept", "strong_folds", "strong_folds_kept",
                        "outside", "silhouette", "bow", "glints_outside", "regional_dye"):
                total[key] += int(row[key])
    with (output / "parents.csv").open() as stream:
        for row in csv.DictReader(stream):
            if int(row["native_differences"]):
                total = summary[row["equipment"]]
                total["lost_parent"] += int(row["equipped_differences"]) == 0
                total["parent_recolored"] += int(row["original_pixels_still_distinct"]) == 0
    for name, total in summary.items():
        edges = total["edges_kept"] / max(1, total["edges"])
        folds = total["strong_folds_kept"] / max(1, total["strong_folds"])
        print(f"{name}  {total['poses']} poses, {edges:.1%} adjacent colors distinct, "
              f"{folds:.1%} strong folds keep direction, {total['lost_color']} poses lose sampled class colors, "
              f"{total['lost_parent']} parent cues lost, {total['parent_recolored']} parent cues entirely recolored, "
              f"{total['outside']} outside, {total['silhouette']} silhouette, {total['bow']} bow, "
              f"{total['glints_outside']} misplaced glints, {total['regional_dye']} regional dye pixels")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("game_dir", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("figures", type=int, nargs="*", default=range(300, 308))
    args = parser.parse_args()
    args.output.mkdir(exist_ok=True, parents=True)
    atlas = Atlas(args.game_dir)
    with (args.output / "frames.csv").open("w", newline="") as file, \
            (args.output / "parents.csv").open("w", newline="") as parents:
        frames, pairs = csv.writer(file), csv.writer(parents)
        frames.writerow(FRAMES)
        pairs.writerow(PARENTS)
        for obj in args.figures:
            audit(atlas, obj, frames, pairs)
            print("Checked", obj, flush=True)
    summarize(args.output)
