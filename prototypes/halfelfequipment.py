"""Export the fitted half-elf Fighter and Preserver layers from the approved studies.

python prototypes/halfelfequipment.py GAME_DIR OUTPUT_ZIP
"""
import argparse
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

import halfelfstudy as he
from dsloader import classoutfits as co, figures, sprites
from outfitdetail import RAMPS, HALFTONES


PLUM = set(RAMPS["plum"]) | set(HALFTONES["plum"].values()) | {233, 238}
ARMOR = co.CHEST | co.ARMS | co.LEGS
LIMBS = co.LEFT_FOOT | co.RIGHT_FOOT | co.FOREARM


def layers(study, obj, pose, role):
    key = he.FIGURES[0 if obj == 307 else 1]
    fig = study.game.fig(key)
    combat, frame = divmod(pose, 15)
    stock = fig.rows(combat, frame)
    body, pad = study.rows(key, pose, "Body base")
    outfit, _ = study.rows(key, pose, role)
    parent = {"Fighter": "Warrior", "Preserver": "Mage"}[role] if obj == 307 else role
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
    output = {name: [[None]*w for _ in range(h)] for name in ("image", "regions", "head", "cloak")}
    waist = fig.parts(combat, frame).waist
    for v, row in enumerate(outfit):
        for u, c in enumerate(row):
            x, y = u-pad, v-pad
            source = he.at(stock, x, y)
            if c != source:
                output["image"][v][u] = 255 if c is None else c
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
                    upper = y <= waist if waist is not None else y >= len(stock)//2
                    armor = co.CHEST if upper else co.LEGS
            else:
                armor = 0
            bits = bow | armor | (bits & LIMBS if skin and not head and not bow else 0)
            if bits:
                output["regions"][v][u] = bits
    return output


def export(game_dir, path):
    study = he.Study(game_dir)
    with ZipFile(path, "w") as archive:
        for obj in co.HALF_ELF_SOURCES:
            for role in co.HALF_ELF_ROLES.values():
                for start, stop, tag in ((0, 15, "walk"), (15, 29, "combat")):
                    frames = [layers(study, obj, pose, role) for pose in range(start, stop)]
                    for name in frames[0]:
                        suffix = "" if name == "image" else "-"+name
                        entry = ZipInfo(f"{obj}/{role}/{tag}{suffix}")
                        data = sprites.encode_frames([f[name] for f in frames])
                        archive.writestr(entry, data, compress_type=ZIP_DEFLATED)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("game_dir", type=Path)
    parser.add_argument("archive", type=Path)
    args = parser.parse_args()
    export(args.game_dir, args.archive)
