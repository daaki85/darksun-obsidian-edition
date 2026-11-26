"""Export every half-elf single, pair and triple from its approved study drawing.

python prototypes/halfelfequipment.py GAME_DIR OUTPUT_ZIP
"""
import argparse
from pathlib import Path

import halfelfequipmasks
import halfelfstudy as he
from dsloader import classoutfits as co, figures
from fittedraceequipment import write_archive
from outfitdetail import RAMPS, HALFTONES


PLUM = set(RAMPS["plum"]) | set(HALFTONES["plum"].values()) | {233, 238}
ARMOR = co.CHEST | co.ARMS | co.LEGS
LIMBS = co.LEFT_FOOT | co.RIGHT_FOOT | co.FOREARM


def approved_masks(study, key, pose, role, outfit, pad):
    """Keep the original Fighter and Preserver equipment registration."""
    combat, frame = divmod(pose, 15)
    fig = study.game.fig(key)
    body, _ = study.rows(key, pose, "Body base")
    parent = {"Fighter": "Warrior", "Preserver": "Mage"}[role] if key == he.FIGURES[0] else role
    donor = co.frames(parent, combat, fig.model)[frame]
    back = figures.mover_back(fig.maker.cuts[bool(combat), frame])
    source_outfit = donor.canvas(study.game.fr(fig.model + combat, frame), pad)
    ownership = {}
    for bit, cells in donor.regions.items():
        for point in cells:
            ownership[point] = ownership.get(point, 0) | bit
    folds = {(x, y): shade for x, y, shade in donor.cloak}
    scalp = set(donor.head)
    hair = fig.parts(combat, frame).hair
    h = len(outfit)
    w = len(outfit[0])
    output = {name: [[None]*w for _ in range(h)] for name in ("regions", "head", "cloak")}
    waist = fig.parts(combat, frame).waist
    for v, row in enumerate(outfit):
        for u, c in enumerate(row):
            x, y = u-pad, v-pad
            if c is None:
                continue
            point = back(x, y), y
            bits = ownership.get(point, 0)
            skin = c == body[v][u] or c in he.outfits.SKINC
            head = (x, y) in hair or (point in scalp and skin)
            bow = bits & co.BOW
            if head:
                output["head"][v][u] = 1
            # The old long hair hid part of the half-elf's garment. Continue
            # the jerkin in that opening. Its former hair cannot own armor.
            cloth = not skin and not bow and not head
            fold = folds.get(point)
            # The woman's tunic and mantle share their plum ramp. Keep the
            # parent ownership unless a refitted plum fold moved across it.
            extra_fold = c in PLUM and (not bits & ARMOR or
                         c != he.at(source_outfit, point[0]+pad, point[1]+pad))
            mantle = role == "Preserver" and cloth and (fold is not None or extra_fold)
            if fold is not None and not head and not bow and not bits & co.FOREARM:
                output["cloak"][v][u] = fold+1
            if mantle and fold is None:
                rgb = study.game.palette[c]
                light = (.30*rgb[0]+.59*rgb[1]+.11*rgb[2])/255
                output["cloak"][v][u] = 1+min(5, round(light*8))
            if cloth and not mantle:
                armor = bits & ARMOR
                if not armor and role == "Fighter" and not bits & LIMBS:
                    upper = y <= waist if waist is not None else y >= (h-pad)//2
                    armor = co.CHEST if upper else co.LEGS
            else:
                armor = 0
            bits = bow | armor | (bits & LIMBS if skin and not head and not bow else 0)
            if bits:
                output["regions"][v][u] = bits
    return output


def layers(study, obj, pose, role):
    key = he.FIGURES[0 if obj == 307 else 1]
    fig = study.game.fig(key)
    stock = fig.rows(*divmod(pose, 15))
    outfit, pad = study.rows(key, pose, role)
    if role in ("Fighter", "Preserver"):
        masks = approved_masks(study, key, pose, role, outfit, pad)
        if obj == 307 and role == "Fighter":
            # Her older mantle also left windows between the moving folds.
            # Other angles retain the original Preserver drape.
            masks["cape"] = (halfelfequipmasks.layers(study, obj, pose, role)["cape"]
                             if pose in halfelfequipmasks.REAR_CAPE else [[None]*len(row) for row in outfit])
    else:
        masks = halfelfequipmasks.layers(study, obj, pose, role)
    # Erase the generated half-elf's old clothes wherever the approved
    # drawing leaves a transparent pixel.
    image = []
    for y, row in enumerate(outfit):
        paint = []
        for x, color in enumerate(row):
            source = he.at(stock, x - pad, y - pad)
            edit = 255 if color is None else color
            paint.append(None if color == source else edit)
        image.append(paint)
    return {"image": image, **masks}


def export(game_dir, path):
    study = he.Study(game_dir)

    def pose_layers(obj, pose):
        return {role: layers(study, obj, pose, role) for role in co.HALF_ELF_ROLES.values()}

    write_archive(path, co.HALF_ELF_SOURCES, pose_layers)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("game_dir", type=Path)
    parser.add_argument("archive", type=Path)
    args = parser.parse_args()
    export(args.game_dir, args.archive)
