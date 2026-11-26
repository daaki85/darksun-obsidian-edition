"""Elf roster, equipment, and face review boards from the registered loader pictures.

python prototypes/elfreview.py GAME_DIR OUTPUT_DIR
"""

import argparse
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw

import elfoutfits as elf
from dsloader import art, classoutfits as co, game as rules, spritegear as sg, sprites

dwarf = elf.dwarf
OBJECTS = {2059: 305, 2061: 304}
TERRAIN = Path(__file__).resolve().parents[1] / "playtest/logs/img/2026-11-18-alt-arena.png"
GEAR = {
    "Empty": ({}, ()),
    "Boots": ({"boots": (rules.SPEED_BOOTS_TYPE, 5)}, ()),
    "Cloak": ({"cloak": (65, 5)}, ()),
    "Shield": ({"left": (4, 0)}, ()),
    "Steel plate": ({}, (88,)),
    "Magic plate": ({}, (88 | sg.MAGIC_ARMOUR,)),
}
CYCLE = [0, 3, 4, 5, 6, 0, 1, 7, 8, 9, 10, 1, 2, 11, 12, 13, 14, 2, *range(15, 29)]


def label(im, xy, text, size=13, anchor="la"):
    ImageDraw.Draw(im).text(xy, text, font=dwarf.board_font(size), fill=dwarf.INK, anchor=anchor)


def loop(frames, path):
    frames = [im.quantize(256, dither=Image.Dither.NONE) for im in frames]
    frames[0].save(
        path,
        save_all=True,
        append_images=[frames[k] for k in CYCLE[1:]],
        loop=0,
        duration=[940 if k < 3 or k >= 24 else 290 for k in CYCLE],
        disposal=1,
    )


class Review:
    def __init__(self, game, output):
        self.game, self.output = game, output
        self.pics = sprites.Pictures(game.chunks)
        self.sand = Image.open(TERRAIN).convert("RGB").crop((51, 154, 95, 194))

    @lru_cache(maxsize=250)
    def sequence(self, model, combat, role, gear):
        data = self.pics.build(OBJECTS[model], combat, *GEAR[gear], role=role)
        return [art.decode_frame(data, f)[2] for f in range(14 if combat else 15)]

    def rows(self, model, pose, role, gear="Empty"):
        cb, f = divmod(pose, 15)
        if role in ("Original", "Body base"):
            pad = 0 if role == "Original" else elf.PAD
            return elf.render(self.game, model, pose, role), pad, pad, pad
        side, top = sprites.room(cb)
        return self.sequence(model, cb, role, gear)[f], side, top, 0

    def tile(self, model, pose, role, scale, gear="Empty"):
        rows, left, top, bottom = self.rows(model, pose, role, gear)
        return elf.placed_tile(self.game, rows, self.sand, scale, left, top, bottom)

    def roster(self, roles, stem, title, equipment=False):
        cols = 3 if len(roles) > 4 else 2
        frames = []
        for k, name in enumerate(dwarf.NAMES):
            im = Image.new(
                "RGB", (cols * 208 + 12, 51 + 135 * ((len(roles) + cols - 1) // cols)), dwarf.PAPER
            )
            label(im, (10, 7), title, 18)
            label(im, (im.width - 10, 11), name, 14, "ra")
            label(im, (10, 32), "Female elf at left   ·   Male elf at right", 12)
            for i, caption in enumerate(roles):
                x, y = 6 + 208 * (i % cols), 51 + 135 * (i // cols)
                label(im, (x + 104, y), caption, 13, "ma")
                for j, (m, _) in enumerate(elf.MODELS):
                    role, gear = ("Preserver", caption) if equipment else (caption, "Empty")
                    for scale, off in ((2, 17), (1, 94)):
                        t = self.tile(m, k, role, scale, gear)
                        im.paste(t, (x + 53 + 102 * j - t.width // 2, y + off))
            frames.append(im)
        loop(frames, self.output / f"elf-{stem}.gif")
        # Full native frames, labeled independently of GIF timing.
        sheet = Image.new("RGB", (140 + len(roles) * 90, 48 + 29 * 47), dwarf.PAPER)
        label(sheet, (6, 4), title, 15)
        for i, role in enumerate(roles):
            if "/" not in role:
                label(sheet, (184 + 90 * i, 22), role, 9, "ma")
            if "/" in role:
                for j, part in enumerate(role.split("/")):
                    label(sheet, (184 + 90 * i, 17 + j * 10), part, 9, "ma")
        for k, name in enumerate(dwarf.NAMES):
            y = 48 + 47 * k
            label(sheet, (5, y + 12), name, 12)
            for i, cap in enumerate(roles):
                for j, (m, _) in enumerate(elf.MODELS):
                    role, gear = ("Preserver", cap) if equipment else (cap, "Empty")
                    sheet.paste(self.tile(m, k, role, 1, gear), (140 + i * 90 + j * 44, y))
        sheet.save(self.output / f"elf-{stem}-frames.png")

    def comparison(self):
        roles = ("Cleric", "Fighter", "Gladiator", "Preserver", "Psionicist", "Ranger", "Thief")
        human = ("Priest", "Warrior", "Gladiator", "Mage", "Psionicist", "Ranger", "Thief")
        references = (
            (1563, "Cleric"),
            (1252, "Fighter"),
            (2055, "Dwarf"),
            (724, "Mage"),
            (2061, "Male elf"),
            (2059, "Female elf"),
            (630, "Thief"),
        )
        im = Image.new("RGB", (700, 69 + len(roles) * 85), dwarf.PAPER)
        label(im, (10, 7), "Outfit contrast at map size", 19)
        for i, caption in enumerate(
            ("Elf pair", "Human pair", "Elf pair", "Human pair", "Original game")
        ):
            label(im, (160 + 116 * i, 35), caption, 13, "ma")
            label(
                im,
                (160 + 116 * i, 51),
                "Sand" if i < 2 or i == 4 else "Sand in low light",
                10,
                "ma",
            )
        dark = self.sand.point(lambda v: round(v * 0.48))
        for i, (role, alias, (npc, name)) in enumerate(zip(roles, human, references)):
            y = 68 + i * 85
            label(im, (8, y + 23), role, 14)
            for k, off in ((0, 0), (13, 41)):
                for j, bg in enumerate((self.sand, self.sand, dark, dark)):
                    for sex, (m, _) in enumerate(elf.MODELS):
                        if j % 2 == 0:
                            rows, l, t, b = self.rows(m, k, role)
                        else:
                            obj = (301, 300)[sex]
                            data = self.pics.build(obj, False, {}, (), role=alias)
                            rows = art.decode_frame(data, k)[2]
                            l, t = sprites.room(False)
                            b = 0
                        tile = elf.placed_tile(self.game, rows, bg, 1, l, t, b)
                        im.paste(tile, (116 + j * 116 + sex * 44, y + off))
                ref = self.game.fr(npc, k)
                im.paste(elf.placed_tile(self.game, ref, self.sand, 1, 0, 0, 0), (608, y + off))
            label(im, (655, y + 35), name, 10)
        im.save(self.output / "elf-contrast.png")

    def faces(self):
        roles = ("Original", "Body base", "Cleric", "Thief", "Psionicist")
        frames = []
        for k, name in enumerate(dwarf.NAMES):
            im = Image.new("RGB", (685, 359), dwarf.PAPER)
            label(im, (12, 8), "Elf faces", 20)
            label(im, (670, 12), name, 15, "ra")
            for i, role in enumerate(roles):
                x = 72 + i * 122
                label(im, (x + 58, 43), role, 14, "ma")
                for j, (m, sex) in enumerate(elf.MODELS):
                    y = 65 + j * 142
                    if i == 0:
                        label(im, (6, y + 50), sex, 13)
                    rows, left, top, bottom = self.rows(m, k, role)
                    t = self.tile(m, k, role, 1)
                    cx, cy = elf.JAWS[m][k]
                    h = len(rows) - top - bottom
                    if k == 28:
                        cy = h - 1 - cy
                    cx += (t.width - (len(rows[0]) - 2 * left)) // 2
                    cy += t.height - 2 - h
                    crop = t.crop((cx - 9, cy - 10, cx + 10, cy + 5))
                    im.paste(crop.resize((114, 90), Image.Resampling.NEAREST), (x, y))
                    im.paste(t, (x + 35, y + 94))
            frames.append(im)
        loop(frames, self.output / "elf-faces.gif")
        frames[0].save(self.output / "elf-faces.png")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("game_dir")
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    review = Review(elf.outfits.Game(args.game_dir), args.output_dir)
    review.faces()
    review.comparison()
    for size in (1, 2, 3):
        roles = [role for combo, role in co.ELF_ROLES.items() if len(combo) == size]
        if size == 1:
            review.roster(["Original", "Body base", *roles], "singles", "Elf single classes")
        else:
            mid = len(roles) // 2
            for suffix, group in (("a", roles[:mid]), ("b", roles[mid:])):
                review.roster(
                    group, f"{size}-{suffix}", f"Elf {'two' if size==2 else 'three'}-class outfits"
                )
    review.roster(list(GEAR), "equipment", "Preserver equipment", True)


if __name__ == "__main__":
    main()
