"""Preview armor dyes on unregistered class art, before fitting the actual item slots.

python prototypes/studyarmordetail.py GAME_DIR OUTPUT_DIR

The study figures provide the original garment, body, pose and multiclass artwork.
The Loader provides the material dyes. The comparison is for a complete suit;
it does not claim chest/arm/leg ownership or simulate equipment for these studies.
"""
import argparse
import csv
from functools import lru_cache
from pathlib import Path

from PIL import Image

from elfreview import dwarf, elf, label
from outfitdetail import DEFAULT, HALFTONES, RAMPS
from studygeartest import Atlas, NAMES, co, he, hg, hl, mul, sg, study_rows
from dsloader import figures

MATERIALS = {"Leather": sg.LEATHER_SHADES, "Mail": sg.CHAIN_SHADES, "Scale": sg.BONE_SHADES,
             "Plate": sg.METAL_SHADES, "Plain ash cloth": sg.CHAIN_SHADES, "Plain veiled cloth": sg.VEILED_CLOTH}
SAMPLES = {306: ("Druid", 12), 307: ("Cleric/Preserver", 3), 308: ("Cleric/Fighter", 0),
           309: ("Ranger", 8), 310: ("Thief", 3), 311: ("Psionicist/Ranger", 7), 312: ("Druid/Fighter", 0)}


def landmarks(obj, pose, game):
    """Use the same moving garment cuts and canvas margins as the artwork."""
    if obj in (306, 307):
        key = he.FIGURES[1 if obj == 306 else 0]
        fig = game.fig(key)
        parts = fig.parts(*divmod(pose, 15))
        if parts.waist is None:
            # The two prone half-elf garments use the donor's feet-down fitting.
            shoulder, waist = 7, (12 if obj == 307 else 14)
        else:
            shoulder, waist = parts.shoulders[0], parts.waist
        return shoulder, waist, None, he.MARGIN, he.MARGIN
    if obj in (308, 309):
        dy = hg.FEMALE_OFFSETS[pose][1] if obj == 309 else 0
        shoulder, waist, knee = hg.CUTS[pose]
        return (*(dy + (cut[1]+cut[3])/2 for cut in (shoulder, waist, knee)), 5, 0)
    if obj in (310, 311):
        shoulder, waist, left, right, offset = hl.fit.CUT[pose]
        dy = offset[1] if obj == 311 else 0
        return shoulder[1]+dy, waist[1]+dy, None, 4, 0
    shoulder, _, waist, _, _ = mul.fit.ROBE_CUTS[pose]
    return shoulder[0], waist[0], None, mul.fit.PAD, 0


def garment(outfit, body):
    return {(x, y) for y, row in enumerate(outfit) for x, color in enumerate(row)
            if color is not None and color != body[y][x]}


OUTER_FABRIC = {"Ranger": set(RAMPS["leaf"]), "Druid": set(RAMPS["leaf"]),
                "Preserver": set(RAMPS["plum"]) | set(HALFTONES["plum"].values()),
                "Thief": set(RAMPS["slate"])}


def base_garment(obj, role):
    """Follow the study's layering order, consistently through every stride."""
    names = role.split("/")
    if len(names) == 1 or 308 <= obj <= 309:
        return names[0]
    if obj < 308:
        if "Thief" in names and ("Druid" in names or len(names) == 3 and role != "Fighter/Psionicist/Thief"):
            names.remove("Thief")
        return he.pairs.base_class("/".join(names))
    if names[0] in ("Cleric", "Druid"):
        return names[0]
    if "Ranger" in names:
        return "Ranger"
    return "Thief" if "Thief" in names else names[0]


@lru_cache(maxsize=256)
def halfelf_exposed_garment(game, obj, role, pose):
    """Locate cloth beneath a cloak of the same color on the fitted donor."""
    combat, frame = divmod(pose, 15)
    key = he.FIGURES[1 if obj == 306 else 0]
    figure = game.fig(key)
    if role == "Preserver":
        # This single has its own fitted masks on the half-elf models.
        data = co.frames(role, combat, obj)[frame]
        raw = None
    else:
        donor = "Ranger" if role == "Druid" and obj == 306 else role
        data = co.frames(donor, combat, figure.model)[frame]
        raw = figures.mover_back(figure.maker.cuts[bool(combat), frame])
    armor = set().union(*(data.regions[bit] for bit in (co.CHEST, co.ARMS, co.LEGS)))
    armor.difference_update((x, y) for x, y, _ in data.cloak)
    armor.difference_update(data.head, data.regions[co.BOW], data.regions[co.FOREARM])
    native = figure.rows(combat, frame)
    return {(x+he.MARGIN, y+he.MARGIN) for y, row in enumerate(native)
            for x in range(len(row)) if (raw(x, y) if raw else x, y) in armor}


def suit_surface(outfit, body, cloth, additions, pose, cuts):
    shoulder, waist, knee, _, top = cuts
    surface = set()
    for x, y in cloth - additions:
        level = len(outfit)-1-y if pose == 28 else y-top
        # Exclude collars, hoods, the waist binding, sandals and hanging cloak
        # corners. Keep the closing pixel of each hem on a bent or lifted leg.
        if (level <= shoulder+1 or abs(level-waist) < 1 or knee is not None and level >= knee
                or body[y][x] is None or outfit[y][x] in range(128, 155)):
            continue
        below = (x, y-1 if pose == 28 else y+1)
        if level > waist and below not in cloth:
            continue
        surface.add((x, y))
    return surface


def keep_binding(surface, signature, pose, cuts, height):
    """Retain the colored edge where a hood dye or sash occupies almost all of it."""
    if signature and len(signature - surface) < min(3, len(signature)):
        waist_row = height-1-cuts[1] if pose == 28 else cuts[4]+cuts[1]
        rows = sorted({y for _, y in signature}, key=lambda y: (abs(y-waist_row), y))[:2]
        surface.difference_update((x, y) for x, y in signature if y in rows)


def study_surface(game, obj, pose, rows, role, cuts):
    """Visible garment, suit dye area, and protected accents on one approved pose."""
    outfit, body = rows[role], rows["Body base"]
    # Keep the distinctive secondary layers, including a retinted
    # hood or scale. Leave the outer fabric of the base class over
    # the armor wherever it still shows in its original pigment.
    base = base_garment(obj, role)
    parent = rows[base]
    cloth = garment(outfit, body)
    additions = {(x, y) for x, y in cloth if outfit[y][x] != parent[y][x]}
    outer = OUTER_FABRIC.get(base, ())
    covered = {(x, y) for x, y in cloth if parent[y][x] in outer}
    if obj in co.HALF_ELF_SOURCES and outer:
        covered -= halfelf_exposed_garment(game, obj, base, pose)
    surface = suit_surface(outfit, body, cloth, additions | covered, pose, cuts)
    pigment = set(RAMPS[DEFAULT.get(base, "hide")]) - {208, 17, 207, 204}
    signature = {(x, y) for x, y in cloth if outfit[y][x] in pigment}
    keep_binding(surface, signature, pose, cuts, len(outfit))
    return cloth, surface, additions, covered, signature


def contrasts(source, dyed, cells, palette):
    total = distinct = 0
    for x, y in cells:
        for xx, yy in ((x+1, y), (x, y+1)):
            if (xx, yy) in cells and palette[source[y][x]] != palette[source[yy][xx]]:
                total += 1
                distinct += palette[dyed[y][x]] != palette[dyed[yy][xx]]
    return distinct, total


REVIEW_COLUMNS = ("Class colors", "Leather", "Scale", "Plate", "Plain veiled cloth", "Retail reference")
RETAIL = {306: (1252, "Warrior"), 307: (724, "Mage"), 308: (1563, "Priest"), 309: (630, "Thief"),
          310: (630, "Thief"), 311: (630, "Thief"), 312: (1252, "Warrior")}


def place_sample(board, tile, column, row):
    x, y = 146 + 159*column, 70 + 181*row
    board.paste(tile.resize((156, 132), Image.Resampling.NEAREST), (x, y))
    board.paste(tile, (x+104, y+133))


def compare(game_dir, output, objects):
    output.mkdir(parents=True, exist_ok=True)
    atlas = Atlas(game_dir)
    study = he.Study(game_dir)
    swatches = hg.reference_folds(atlas.game)
    board = Image.new("RGB", (1103, 76+len(objects)*181), dwarf.PAPER)
    label(board, (12, 10), "Full-suit material study", 20)
    for col, text in enumerate(REVIEW_COLUMNS):
        label(board, (225+col*159, 48), text, 12, "ma")
    with (output/"study-armor-detail.csv").open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(("figure", "role", "pose", "material", "garment", "surface", "changed",
                         "original_garment_pixels", "intact_edges", "source_edges", "parent_cue_pixels",
                         "class_pigment", "original_class_pigment"))
        for i, obj in enumerate(objects):
            for pose in range(29):
                rows = study_rows(obj, pose, atlas.game, study, swatches)
                cuts = landmarks(obj, pose, atlas.game)
                for role, outfit in rows.items():
                    if role in ("Original", "Body base") or (obj < 308 and role in ("Fighter", "Preserver")):
                        continue
                    cloth, surface, additions, covered, signature = study_surface(
                        atlas.game, obj, pose, rows, role, cuts)
                    sample = SAMPLES[obj] == (role, pose)
                    if sample:
                        label(board, (12, 84+i*181), NAMES[obj], 13)
                        label(board, (12, 105+i*181), role, 11)
                        label(board, (12, 126+i*181), dwarf.NAMES[pose], 11)
                        npc, name = RETAIL[obj]
                        place_sample(board, atlas.tile(npc, pose, "", "", 1), len(REVIEW_COLUMNS)-1, i)
                        label(board, (146+159*(len(REVIEW_COLUMNS)-1), 211+i*181), name, 12)
                    for material, shades in (("Class colors", None), *MATERIALS.items()):
                        if shades is None and not sample:
                            continue
                        dyed = [row[:] for row in outfit]
                        if shades is not None:
                            sg.dye_garment(dyed, surface, shades, 0, outfit)
                            sg.retain_cloth_shadows(dyed, surface, 0, outfit)
                            changed = {(x, y) for y, row in enumerate(dyed) for x, color in enumerate(row)
                                       if color != outfit[y][x]}
                            assert changed <= surface and not changed & (additions | covered)
                            assert not signature or signature - changed
                            kept, total = contrasts(outfit, dyed, surface, atlas.game.palette)
                            writer.writerow((NAMES[obj], role, pose, material, len(cloth), len(surface),
                                             len(changed), len(cloth)-len(changed), kept, total, len(additions),
                                             len(signature), len(signature - changed)))
                        if sample and material in REVIEW_COLUMNS:
                            tile = elf.placed_tile(atlas.game, dyed, atlas.floor, 1, cuts[3], cuts[4], 0)
                            place_sample(board, tile, REVIEW_COLUMNS.index(material), i)
    board.save(output/"study-armor-detail.png")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("game_dir", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("figures", nargs="*", type=int, default=list(SAMPLES))
    args = parser.parse_args()
    compare(args.game_dir, args.output, args.figures)
