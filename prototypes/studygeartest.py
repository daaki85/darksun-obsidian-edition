"""Exercise equipment on all party figures and on the seven outfit studies before import.

Run: python prototypes/studygeartest.py GAME_DIR OUTPUT_DIR
Results are per figure, outfit, item and pose. The study probe replaces only
the starting pixel canvas. Landmarks, item records and gear drawing come from
the unmodified Loader. No future costume ownership masks are assumed.
"""
import argparse
import csv
from pathlib import Path
from unittest.mock import patch

import numpy as np
from PIL import Image
from scipy.ndimage import label

import halfelfstudy as he
import halfgiantstudy as hg
import halflingmultis as hl
import mulmultis as mul
from dsloader import classoutfits as co
from wornreview import Atlas, CASES, WEAPONS, art, elf, sg, sprites

NAMES = {300: "Human man", 301: "Human woman", 302: "Dwarf man", 303: "Dwarf woman",
         304: "Elf man", 305: "Elf woman", 306: "Half-elf man", 307: "Half-elf woman", 308: "Half-giant man",
         309: "Half-giant woman", 310: "Halfling man", 311: "Halfling woman",
         312: "Mul", 313: "Thri-kreen"}
EMPTY = "Class colors"
EXTRA = {
    "Leather set": ({}, (6, 7, 8)), "Mail set": ({}, (57, 58, 59)),
    "Scale set": ({}, (15, 55, 56)), "Arm plate": ({}, (25,)), "Leg plate": ({}, (26,)),
    "Magical chest plate": ({}, (88 | sg.MAGIC_ARMOUR,)),
}
KIT = tuple(dict.fromkeys((*CASES, *WEAPONS, *EXTRA)))
CHECKS = ("changed", "separate", "clipped", "bow", "bare_skin")
ADJACENT = np.ones((3, 3), dtype=bool)


def array(rows):
    # Palette index 255 is the transparency key in these figures.
    return np.nan_to_num(np.array(rows, dtype=float), nan=255).astype(np.uint8)


def starting_canvas(rows, native, pad, below=0):
    width, height = len(native[0]), len(native)
    left = pad - (len(rows[0])-width)//2
    top = pad - (len(rows)-height)
    assert left >= 0 and top >= 0 and left + len(rows[0]) <= width + 2 * pad
    result = [[None]*(width+2*pad) for _ in range(height+pad+below)]
    for y, row in enumerate(rows, top):
        result[y][left:left+len(row)] = row
    return result


def study_rows(obj, pose, game, study, swatches):
    if obj in (306, 307):
        key = he.FIGURES[1 if obj == 306 else 0]
        roles = (*he.ROLES[1:], *he.NEW_SINGLES, *he.pairs.ROSTER, *he.pairs.TRIPLES)
        return {role: study.rows(key, pose, role)[0] for role in roles}
    if obj in (308, 309):
        return hg.study_rows(game, hg.MODELS[obj-308], pose, swatches["linen"], pairs=True)
    if obj in (310, 311):
        return hl.draw(game, pose, swatches)[hl.fit.MODELS[obj-310]]
    return mul.draw(game, pose, swatches)


def roles_for(obj):
    if obj < 302:
        return co.CLASSES[1:]
    if obj < 304:
        return co.DWARF_ROLES.values()
    if obj < 306:
        return co.ELF_ROLES.values()
    return (None,)


def weapon_bounds(atlas, obj, output):
    """Repeat the regular builder with extra room, including below the floor line."""
    pad = 32
    below = 16
    plain_pad = sg.padded
    class_canvas = co.Frame.canvas
    normal_pad = sprites.PAD

    def extend(rows):
        return rows + [[None] * len(rows[0]) for _ in range(below)]

    def wider(role, combat, gear):
        kept = []

        def capture(rows, fighting):
            kept.append(array(rows))
            side, top = (normal_pad, normal_pad) if fighting else sprites.room(False)
            dx = pad - side
            return [r[dx:len(r)-dx] for r in rows[pad-top:-below]]

        with patch.object(sprites, "PAD", pad), patch.object(sprites, "trimmed", capture), \
                patch.object(sg, "padded", lambda rows, n: extend(plain_pad(rows, n))), \
                patch.object(co.Frame, "canvas", lambda self, rows, n: extend(class_canvas(self, rows, n))):
            chunk = atlas.pictures.build(obj, combat, gear, (), role=role)
        return kept, chunk

    with (output/f"bounds-{obj}.csv").open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(("outfit", "pose", "item", "outside_pixels", "inside_difference"))
        for role in roles_for(obj):
            for combat in (False, True):
                base, _ = wider(role, combat, {})
                side, top = sprites.room(combat)
                dx, dy = pad-side, pad-top
                for name in (*WEAPONS, "Bow and quiver", "Sword and shield"):
                    gear, _ = atlas.gear[name]
                    rendered, cropped = wider(role, combat, gear)
                    original = atlas.pictures.build(obj, combat, gear, (), role=role)
                    for f, (frame, naked) in enumerate(zip(rendered, base)):
                        diff = frame != naked
                        diff[dy:-below, dx:-dx] = False
                        inside = 0
                        if original != cropped:
                            normal = array(art.decode_frame(original, f)[2])
                            actual = array(art.decode_frame(cropped, f)[2])
                            inside = np.count_nonzero(normal != actual)
                        writer.writerow((role or "Retail", f+15*combat, name,
                                         np.count_nonzero(diff), inside))


def stock_test(atlas, obj, output):
    pics = atlas.pictures
    # The actual empty/equipped/removed picture builder, including compression,
    # figure selection and half-elf registration. Kreen armour is a negative control.
    with (output/f"loader-{obj}.csv").open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(("outfit", "item", "pose", "changed_pixels", "bow", "separate", "armour_spill"))
        for role in roles_for(obj):
            for combat in (False, True):
                count = 14 if combat else 15
                model = pics.model(obj)
                side, above = sprites.room(combat)
                empty = pics.build(obj, combat, {}, (), role=role)
                bases = [array(art.decode_frame(empty, f)[2]) for f in range(count)]
                fields = co.frames(role, combat, model) if role else None
                for name in KIT[1:]:
                    gear, armour = atlas.gear[name]
                    dressed = pics.build(obj, combat, gear, armour, role=role)
                    assert pics.build(obj, combat, {}, (), role=role) == empty, (obj, role, name, "removal")
                    for f, base in enumerate(bases):
                        worn = array(art.decode_frame(dressed, f)[2])
                        assert base.shape == worn.shape
                        mask = worn != base
                        changed = np.count_nonzero(mask)
                        if obj == 313 and (name in EXTRA or name in ("Full plate", "Chest plate",
                                "Warden's Plate", "Ashen Robe", "Veiled Robe", "Boots of Speed", "Bracers")):
                            assert not changed, (name, f)
                        bow_hits = spill = ""
                        if fields:
                            reg = fields[f].regions
                            bow_hits = sum(mask[y+above, x+side] for x, y in reg[co.BOW])
                            if armour and not gear:
                                allowed = set()
                                for item in armour:
                                    kind = item & (sg.MAGIC_ARMOUR-1)
                                    piece = sg.ARMOUR[kind][0]
                                    allowed.update(reg[{sg.ARMOUR_CHEST: co.CHEST, sg.ARMOUR_ARMS: co.ARMS,
                                                        sg.ARMOUR_LEGS: co.LEGS}[piece]])
                                    if kind == sg.game.ROBE_TYPE:
                                        allowed.update(reg[co.LEGS])
                                ys, xs = np.nonzero(mask)
                                spill = sum((x-side, y-above) not in allowed for x, y in zip(xs, ys))
                        labels, components = label(worn != 255, ADJACENT)
                        touching = set(labels[base != 255])
                        separate = any(k not in touching for k in range(1, components+1))
                        writer.writerow((role or "Retail", name, f+15*combat, changed, bow_hits,
                                         int(separate), spill))


def inspect_pose(atlas, obj, pose, rows, output, writer):
    pics = atlas.pictures
    cb, f = divmod(pose, 15)
    model, frames, owners = pics.base(pics.model(obj), obj, bool(cb))
    native = frames[f]
    fig = atlas.game.fig(he.FIGURES[1 if obj == 306 else 0] if obj < 308 else model)
    template = sg.cloak_template(pics.own(sg.CLOAK_MODEL+cb)[f], sg.CLOAK_MODEL, f, bool(cb))
    bow = atlas.game.bow(fig, native, fig.parts(cb, f)) if 24 <= pose <= 26 else set()
    if obj in (310, 311) and 24 <= pose <= 26:
        dx, dy = hl.fit.CUT[pose][-1] if obj == 311 else (0, 0)
        bow = {(x+dx,y+dy) for y,l,r in hl.fit.BOW_ARCS[pose] for x in range(l,r+1)}
        if obj == 311 and pose == 24:
            bow.add((6, 16))
    pad = sprites.PAD
    side, above = sprites.room(cb)
    y0, x0 = pad-above, pad-side
    w, h = len(native[0])+2*side, len(native)+above
    seeds = {}
    plain_pad = sg.padded

    def initial(source, margin):
        if source is native:
            return [row[:] for row in seeds[margin]]
        return plain_pad(source, margin)

    def render(name, margin):
        gear, armour = atlas.gear[name]
        return sg.armed(native, model, f, bool(cb), gear, margin, armour, template, owners[f])

    body = array(starting_canvas(rows["Body base"], native, pad))[y0:, x0:x0+w]
    with patch.object(sg, "padded", initial):
        for role, image in rows.items():
            if role in ("Body base", "Original"):
                continue
            seeds[pad] = starting_canvas(image, native, pad)
            seeds[32] = starting_canvas(image, native, 32, 16)
            base = array(render(EMPTY, pad))[y0:, x0:x0+w]
            assert np.array_equal(base, array(seeds[pad])[y0:, x0:x0+w])
            if role == "Fighter" and pose in {p for p, _ in SAMPLES}:
                tile = elf.placed_tile(atlas.game, sprites.trimmed(seeds[pad], cb), atlas.floor,
                                       1, side, above, 0)
                tile.save(output/f"sample-{obj}-{pose}-Empty.png")
            occupied = base != 255
            skin = (base == body) & (base >= 130) & (base <= 153)
            for name in KIT[1:]:
                equipped = render(name, pad)
                worn = array(equipped)[y0:, x0:x0+w]
                different = worn != base
                clipped = False
                separate = False
                if name in WEAPONS or name in ("Bow and quiver", "Sword and shield"):
                    extended = array(render(name, 32))
                    extended_base = array(seeds[32])
                    outside = extended != extended_base
                    outside[32-above:32-above+h, 32-side:32-side+w] = False
                    clipped = bool(outside.any())
                    components, count = label(worn != 255, ADJACENT)
                    if count > 1:
                        touched = set(components[occupied]) | {0}
                        separate = any(i not in touched for i in range(1, count+1))
                bow_diff = sum(different[y+above, x+side] for x,y in bow)
                bare = (np.count_nonzero(different & skin) if name in
                        ("Full plate", "Chest plate", "Ashen Robe", "Veiled Robe") else 0)
                writer.writerow((role, pose, name, np.count_nonzero(different), int(separate),
                                 int(clipped), bow_diff, bare))
                if role == "Fighter" and (pose, name) in SAMPLES:
                    tile = elf.placed_tile(atlas.game, sprites.trimmed(equipped, cb), atlas.floor,
                                           1, side, above, 0)
                    tile.save(output/f"sample-{obj}-{pose}-{name}.png")
            assert render(EMPTY, pad) == seeds[pad], (obj, role, pose, "removal")


SAMPLES = ((0, "Chest plate"), (0, "Full plate"), (12, "Warden's Plate"),
           (3, "Ashen Robe"), (3, "Veiled Robe"), (16, "Sword and shield"),
           (23, "Polearm"), (26, "Bow and quiver"))


def run(game_dir, output, objects, loader_only=False, bounds_only=False):
    output.mkdir(parents=True, exist_ok=True)
    atlas = Atlas(game_dir)
    atlas.gear.update(EXTRA)
    atlas.floor = Image.open(hg.TERRAIN).convert("RGB").crop((30, 125, 110, 195))
    study = he.Study(game_dir)
    swatches = hg.reference_folds(atlas.game)
    for obj in objects:
        weapon_bounds(atlas, obj, output)
        if bounds_only:
            continue
        stock_test(atlas, obj, output)
        if loader_only or obj not in range(306, 313):
            continue
        with (output/f"study-{obj}.csv").open("w", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(("outfit", "pose", "item", *CHECKS))
            for pose in range(29):
                rows = study_rows(obj, pose, atlas.game, study, swatches)
                inspect_pose(atlas, obj, pose, rows, output, writer)
        print("Completed", NAMES[obj], flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("game_dir", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("objects", type=int, nargs="*", default=list(NAMES))
    parser.add_argument("--loader-only", action="store_true")
    parser.add_argument("--bounds-only", action="store_true")
    args = parser.parse_args()
    run(args.game_dir, args.output, args.objects, args.loader_only, args.bounds_only)
