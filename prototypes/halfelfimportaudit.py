"""Check the imported half-elf outfits against the approved study and the previous Loader.

python prototypes/halfelfimportaudit.py GAME_DIR OUTPUT_DIR --previous-checkout CHECKOUT
For the compatibility comparison, use the pre-import checkout at 17bbc0bc.
The --bounds option also checks every weapon against an oversized canvas.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys

import numpy as np
from scipy.ndimage import label

from studygeartest import ADJACENT, Atlas, array, art, co, he, sg, sprites
from studygeartest import starting_canvas, visible_cuffs, visible_greaves, weapon_bounds
from dsloader import game, kitpages
from equipmentfitreview import slot_loadouts
from magicgearitems import loadouts

FIGURES = {306: he.FIGURES[1], 307: he.FIGURES[0]}
ROLES = (*he.ROLES[2:], *he.NEW_SINGLES, *he.pairs.ROSTER, *he.pairs.TRIPLES)
GROUPS = ("Cleric", "Druid", "Fighter", "Gladiator", "Preserver", "Psionicist", "Ranger", "Thief")


def equipment(atlas):
    kits = {name: atlas.gear[name] for name in (
        "Class colors", "Chest plate", "Full plate", "Ashen Robe", "Veiled Robe",
        "Cloak", "Sword and shield", "Shield", "Polearm", "Bow", "Bow and quiver")}
    kits.update({name: value for name, value in slot_loadouts(atlas).items() if name != "Empty"})
    kits.update({name: value for name, value in loadouts(atlas).items() if name != "Empty"})
    return kits


def fingerprint(data):
    return hashlib.sha256(data).hexdigest()


def legacy(game_dir):
    atlas = Atlas(game_dir)
    return {f"{obj}/{role}/{combat}/{name}": fingerprint(atlas.pictures.build(obj, combat, gear, armor, role=role))
            for obj in FIGURES for role in ("Fighter", "Preserver", None) for combat in (0, 1)
            for name, (gear, armor) in equipment(atlas).items()}


def historical(game_dir, checkout):
    script = Path(__file__).resolve()
    command = ("import json,runpy,sys; r=runpy.run_path(sys.argv[1]); "
               "json.dump(r['legacy'](sys.argv[2]),sys.stdout)")
    return json.loads(subprocess.check_output([sys.executable, "-c", command, str(script), str(game_dir.resolve())],
                                              cwd=checkout/"prototypes"))


def route(obj, role):
    sheet = bytearray(game.SHEET_SIZE)
    sheet[game.SHEET_RACE] = kitpages.HALF_ELF
    for i, name in enumerate(role.split("/")):
        group = GROUPS.index(name) + 1
        sheet[game.SHEET_CLASSES+i] = next(key for key, value in kitpages.CREATION_CLASS.items() if value == group)
    return co.for_sheet(sheet, obj)


def owned(frame, item, cuffs, greaves):
    region = frame.regions
    if item in ("Ashen Robe", "Veiled Robe"):
        return set(region[co.CHEST]) | set(region[co.LEGS])
    if item in ("Magic leather", "Magic bone"):
        return set(region[co.CHEST])
    if item == "Magic bracers":
        return set(cuffs)
    if item == "Magic boots":
        return set(region[co.LEFT_FOOT]) | set(region[co.RIGHT_FOOT])
    plate = frame.plate_regions or region
    if item in ("Chest plate", "Chest only"):
        return set(plate[co.CHEST])
    if item == "Arms only":
        return set(plate[co.ARMS]) | set(cuffs)
    if item == "Legs only":
        return set(plate[co.LEGS]) | set(greaves)
    if item in ("Full plate", "All three"):
        return set().union(*(plate[k] for k in (co.CHEST, co.ARMS, co.LEGS)), cuffs, greaves)
    return None


def frame_digests(picture):
    count, = struct.unpack_from("<H", picture, 4)
    ends = (*struct.unpack_from(f"<{count}I", picture, 6), len(picture))
    return [fingerprint(picture[a:b]) for a, b in zip(ends, ends[1:])]


def parent_checks(digests):
    checked = 0
    lost = {}
    for (role, item), frames in digests.items():
        for index, _ in enumerate(role.split("/")):
            members = role.split("/")
            parent = "/".join(members[:index]+members[index+1:])
            if (parent, item) not in digests or item == "Class colors":
                continue
            base = digests[role, "Class colors"]
            parent_base = digests[parent, "Class colors"]
            for original, former, equipped, other in zip(base, parent_base, frames, digests[parent, item]):
                if original != former:
                    checked += 1
                    if equipped == other:
                        lost[item] = lost.get(item, 0) + 1
    return checked, lost


def audit(game_dir, output, checkout, bounds):
    atlas = Atlas(game_dir)
    study = he.Study(game_dir)
    kits = equipment(atlas)
    results = {"outfits": 0, "art_poses": 0, "art_differences": 0, "routing_errors": 0,
               "regression_pictures": 0, "regression_errors": 0, "removal_errors": 0,
               "clipped_study_pixels": 0, "clipped_cape_cells": 0, "multiclass_comparisons": 0,
               "fully_occluded_by_item": {}, "lost_multiclass_cues": 0, "loaded_quiver_distinct": 0, "quiver_poses": 0}
    if checkout:
        previous = historical(game_dir, checkout)
        current = legacy(game_dir)
        changes = [key for key, digest in previous.items() if current.get(key) != digest]
        (output/"legacy-differences.json").write_text(json.dumps(changes, indent=2) + "\n")
        results.update(regression_pictures=len(previous), regression_errors=len(changes))
    assert len(set(ROLES)) == len(ROLES) == 48
    assert set(co.HALF_ELF_ROLES.values()) == set(ROLES), "Incomplete Loader roster"
    colors = {v for group in sg.GLOWS for v in group}
    with (output/"equipment.csv").open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(("figure", "role", "pose", "item", "changed", "glints", "outside_slot",
                         "changed_bow", "changed_head", "silhouette", "detached", "isolated", "study_difference"))
        for obj, key in FIGURES.items():
            family = [{}, {}]
            for role in ROLES:
                results["outfits"] += 1
                results["routing_errors"] += route(obj, role) != role
                for combat in (0, 1):
                    model, native, owners = atlas.pictures.base(atlas.pictures.model(obj), obj, combat)
                    fields = co.frames(role, combat, obj)
                    render = {name: atlas.pictures.build(obj, combat, gear, armor, role=role)
                              for name, (gear, armor) in kits.items()}
                    for name, picture in render.items():
                        family[combat][role, name] = frame_digests(picture)
                    empty = render["Class colors"]
                    results["removal_errors"] += empty != atlas.pictures.build(obj, combat, {}, (), role=role)
                    side, top = sprites.room(combat)
                    for frame, (rows, field) in enumerate(zip(native, fields)):
                        pose = 15*combat+frame
                        reference, _ = study.rows(key, pose, role)
                        canvas = starting_canvas(reference, rows, sprites.PAD)
                        expected = array(sprites.trimmed(canvas, combat))
                        results["clipped_study_pixels"] += int(np.sum(array(canvas) != 255)-np.sum(expected != 255))
                        results["clipped_cape_cells"] += sum(not (-side <= x < len(rows[0])+side and -top <= y < len(rows))
                            for x, y, _ in (field.equipped_cape or field.cloak))
                        results["loaded_quiver_distinct"] += (family[combat][role, "Bow"][frame] !=
                                                             family[combat][role, "Bow and quiver"][frame])
                        results["quiver_poses"] += 1
                        original = array(art.decode_frame(empty, frame)[2])
                        art_error = np.count_nonzero(original != expected)
                        results["art_differences"] += int(art_error)
                        results["art_poses"] += 1
                        cuffs = visible_cuffs(atlas.pictures, obj, combat, frame, field)
                        greaves = visible_greaves(atlas.pictures, obj, combat, frame, field)
                        for name, chunk in render.items():
                            image = array(art.decode_frame(chunk, frame)[2])
                            changed = image != original
                            solid = image != 255
                            labels, count = label(solid, ADJACENT)
                            sizes = np.bincount(labels.ravel(), minlength=count+1)
                            touched = set(labels[original != 255]) | {0}
                            detached = sum(sizes[k] for k in range(1, count+1) if k not in touched)
                            allowed = owned(field, name, cuffs, greaves)
                            cy, cx = np.nonzero(changed)
                            region = set(zip(cx-side, cy-top))
                            glints = sum(image[y,x] in colors for y,x in zip(cy,cx))
                            writer.writerow((obj, role, pose, name, len(region), glints,
                                             len(region-allowed) if allowed is not None else "",
                                             len(region & set(field.regions[co.BOW])),
                                             len(region & set(field.head)), np.count_nonzero(solid!=(original!=255)),
                                             detached, np.count_nonzero(sizes[1:]==1), art_error if name=="Class colors" else ""))
            for digests in family:
                checked, lost = parent_checks(digests)
                results["multiclass_comparisons"] += checked
                results["lost_multiclass_cues"] += sum(lost.values())
                occluded = results["fully_occluded_by_item"]
                for item, count in lost.items():
                    occluded[item] = occluded.get(item, 0) + count
            if bounds:
                weapon_bounds(atlas, obj, output)
    with (output/"equipment.csv").open(newline="") as stream:
        cases = {}
        for entry in csv.DictReader(stream):
            name = entry["item"]
            case = cases.setdefault(name, dict.fromkeys(("poses", "visible", "sparkling", "outside_slot",
                                                        "changed_bow", "detached", "isolated"), 0))
            case["poses"] += 1
            case["visible"] += int(entry["changed"]) > 0
            case["sparkling"] += int(entry["glints"]) > 0
            for key in ("outside_slot", "changed_bow", "detached", "isolated"):
                case[key] += int(entry[key] or 0)
    results["equipment"] = cases
    (output/"summary.json").write_text(json.dumps(results, indent=2) + "\n")
    print(json.dumps(results, indent=2))
    failures = sum(results[key] for key in ("art_differences", "routing_errors", "regression_errors",
                                            "removal_errors", "clipped_study_pixels", "clipped_cape_cells"))
    failures += sum(case[key] for case in cases.values()
                    for key in ("outside_slot", "changed_bow", "detached", "isolated"))
    if bounds:
        for obj in FIGURES:
            with (output/f"bounds-{obj}.csv").open(newline="") as stream:
                failures += sum(int(row[key]) for row in csv.DictReader(stream)
                                for key in ("outside_pixels", "inside_difference", "detached_pixels",
                                            "bow_pixels_changed"))
    if failures:
        raise SystemExit("Equipment or artwork differences failed the audit; see the output files.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("game_dir", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--previous-checkout", type=Path)
    parser.add_argument("--bounds", action="store_true")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    audit(args.game_dir, args.output, args.previous_checkout, args.bounds)
