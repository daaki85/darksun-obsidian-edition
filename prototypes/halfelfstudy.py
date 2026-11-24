"""Draw the initial half-elf outfit study on the Loader's actual figure geometry.

python prototypes/halfelfstudy.py GAME_DIR OUTPUT_DIR
"""
import argparse
from functools import lru_cache
from pathlib import Path
from zipfile import ZipFile

from PIL import Image

import elfoutfits as elf
import outfits
from dsloader import art, classoutfits as co, figures
from elfreview import TERRAIN, dwarf, label, loop

ROLES = ("Original", "Body base", "Gladiator", "Fighter", "Cleric")
FIGURES = (outfits.HALF_ELF_WOMAN, outfits.HALF_ELF_MAN)
MARGIN = 10


def at(rows, x, y):
    return rows[y][x] if 0 <= y < len(rows) and 0 <= x < len(rows[y]) else None


# Near edge of the narrow strap, traced from shoulder to belt on the rear poses.
# A missing point skips the near arm as it passes in front during the swing.
BACK_STRAP = {
    1: (6, (13, 12, 12, 11, 10, 10, 9, 8)),
    7: (6, (12, 12, 11, 11, 10, 9, 8, 7)),
    8: (6, (13, 12, 12, 11, 11, 10, 9, 8)),
    9: (6, (14, 13, 12, 12, 11, 11, 10, 9)),
    10: (6, (13, 12, 12, 11, 10, 9, 9, 8)),
    18: (9, (7, 7, None, None, None, 7, 6, 5)),
    19: (15, (10, 10, 10, 9, 9, 8, 7)),
}
# Brown creases across the foreshortened leather. Keep the dark outer edge.
JERKIN_FOLDS = {
    0: ((9, 10, 91), (9, 11, 89), (10, 13, 89)),
    1: ((11, 10, 91), (11, 11, 90), (10, 12, 89), (10, 13, 90)),
    18: ((7, 15, 89), (7, 16, 90)),
    19: ((11, 18, 89), (11, 19, 90), (10, 20, 89), (10, 21, 91),
         (10, 22, 89), (12, 25, 89)),
    21: ((18, 18, 89), (18, 19, 90), (18, 20, 89)),
    27: ((9, 7, 89), (9, 8, 91), (10, 8, 90), (9, 9, 89),
         (8, 10, 90), (11, 9, 89), (11, 10, 90)),
}


class Study:
    def __init__(self, game_dir):
        self.game = outfits.Game(game_dir)
        self.floor = Image.open(TERRAIN).convert("RGB").crop((50, 150, 102, 194))
        with ZipFile(Path(co.__file__).with_name("woman_outfit_layers.zip")) as archive:
            self.body = [art.decode_frame(archive.read("Base/" + tag), f)[2]
                         for tag, count in (("walk", 15), ("combat", 14)) for f in range(count)]

    @lru_cache(None)
    def rows(self, key, pose, role):
        cb, f = divmod(pose, 15)
        fig = self.game.fig(key)
        stock = fig.rows(cb, f)
        if role == "Original":
            return stock, 0
        model = fig.model
        src = self.game.fr(model + cb, f)
        female = key == outfits.HALF_ELF_WOMAN
        parent = {"Fighter": "Warrior", "Cleric": "Priest"}.get(role, role) if female else role
        fields = co.frames("Gladiator" if role == "Body base" else parent, cb, model)[f]
        if role != "Body base":
            dressed = fields.canvas(src, MARGIN)
        elif female:
            dressed = co.Frame(self.body[pose], {}).canvas(src, MARGIN)
        else:
            base = elf.render(self.game, model, pose, role, {k: {} for k in ("regions", "head", "cloak")})
            dressed = co.Frame(base[:-elf.PAD], {}).canvas(src, MARGIN)

        back = figures.mover_back(fig.maker.cuts[bool(cb), f])
        scalp = set(fields.head)
        bow = set(fields.regions[co.BOW])
        parts = fig.parts(cb, f)
        if female and cb and f in figures.WOMAN_FIGHTS:
            _, (_, _, _, jaw), _, _ = figures.WOMAN_FIGHTS[f]
        elif pose != 28:
            jaw = parts.shoulders[0] - 1 if female else elf.JAWS[model][pose][1]
        else:
            jaw = 12
        # Register the approved parent garment to the real widened/slimmed body.
        # The half-elf maker supplies the bun, clipped nape, ears and expression.
        # Where the parent's long locks hid a shoulder, continue that material.
        out = []
        for y in range(-MARGIN, len(stock)):
            line = []
            for x in range(-MARGIN, len(stock[0]) + MARGIN):
                sx = back(x, y)
                color = at(dressed, sx + MARGIN, y + MARGIN)
                own = at(stock, x, y)
                native = at(src, sx, y)
                head_row = y <= jaw if pose != 28 else y >= jaw
                if (sx, y) in bow:
                    color = native
                elif (sx, y) in scalp or (head_row and own != native and
                        (own in figures.GOLDEN_HAIR or own in outfits.SKINC or own is None)):
                    if female and pose == 16 and (x, y) == (5, 2):
                        color = None  # Tip of the tossed stock cape above her striking wrist.
                    elif female and own in figures.CLOAK:
                        # Her original purple collar sits beside the jaw, within
                        # the human's long hair mask in several front poses.
                        color = self.behind_locks(dressed, scalp, bow, sx, y, role)
                    elif not female and own in (168, 169, 171, 207):
                        # The maker put linen and leather in the former hair shadow.
                        color = {168: 134, 169: 132, 171: 145, 207: 129}[own]
                    elif female and own == 76 and (pose, x, y) in ((0, 7, 6), (17, 14, 8)):
                        color = 132  # Default neck jewel immediately below the chin.
                    elif own in figures.GOLDEN_HAIR or own in outfits.SKINC or head_row:
                        color = own
                    elif own is None:
                        color = None
                    else:
                        color = self.behind_locks(dressed, scalp, bow, sx, y, role)
                line.append(color)
            out.append(line)
        if female and role == "Gladiator" and pose in BACK_STRAP:
            body, pad = self.rows(key, pose, "Body base")
            start, edge = BACK_STRAP[pose]
            for y, right in enumerate(edge, start):
                if right is None:
                    continue
                for x in range(right - 4, right + 4):
                    px, py = x + pad, y + pad
                    skin = body[py][px]
                    if skin not in outfits.SKINC or (back(x, y), y) in fields.regions[co.FOREARM]:
                        continue
                    if x == right:
                        out[py][px] = 168 if y in (start, start + 4) else 95
                    elif x == right - 1:
                        out[py][px] = 205 if y % 3 else 94
                    elif out[py][px] in (88, 94, 95, 168, 185, 203, 205):
                        out[py][px] = skin
        elif not female and role == "Fighter":
            for x, y, brown in JERKIN_FOLDS.get(pose, ()):
                if out[y + MARGIN][x + MARGIN] in (88, 204, 208):
                    out[y + MARGIN][x + MARGIN] = brown
        elif female and role == "Cleric" and pose == 0:
            # Lit lip of the left fold and the turned-under right shoulder.
            for x, y, shade in ((4, 5, 199), (2, 6, 206), (3, 6, 123), (5, 6, 194),
                                (11, 5, 199), (11, 6, 206), (12, 6, 123), (13, 6, 194)):
                out[y + MARGIN][x + MARGIN] = shade
        return out, MARGIN

    @staticmethod
    def behind_locks(dressed, scalp, bow, x, y, role):
        for dx, dy in ((-1, 0), (1, 0), (0, 1), (-2, 0), (2, 0), (0, 2), (0, 3), (0, 4)):
            sx, sy = x + dx, y + dy
            color = at(dressed, sx + MARGIN, sy + MARGIN)
            if (sx, sy) not in scalp and (sx, sy) not in bow and color is not None:
                if role != "Body base" or color in outfits.SKINC:
                    return color
        return {"Cleric": 206, "Fighter": 136}.get(role, 132)

    def tile(self, key, pose, role, scale):
        rows, pad = self.rows(key, pose, role)
        return elf.placed_tile(self.game, rows, self.floor, scale, pad, pad, 0)

    def references(self, out):
        page = Image.new("RGB", (782, 488), dwarf.PAPER)
        label(page, (10, 7), "Half-elf outfits beside the human and retail figures", 18)
        for col, title in enumerate(("View", "Retail Warrior", "Gladiator", "Human Fighter", "Fighter", "Retail Cleric", "Cleric")):
            label(page, (60 + col * 110, 40), title, 12, "ma")
        for row, (key, pose) in enumerate((key, p) for key in FIGURES for p in (0, 13)):
            y = 64 + row * 100
            human = 2099 if key == FIGURES[0] else 2095
            fighter = co.frames("Warrior", False, human)[pose].canvas(self.game.fr(human, pose), MARGIN)
            samples = (self.game.fr(1252, pose), "Gladiator", fighter, "Fighter",
                       self.game.fr(1563, pose), "Cleric")
            label(page, (8, y + 24), "Woman" if key == FIGURES[0] else "Man", 14)
            label(page, (8, y + 47), dwarf.NAMES[pose], 12)
            for col, sample in enumerate(samples, 1):
                if isinstance(sample, str):
                    tile = self.tile(key, pose, sample, 2)
                else:
                    pad = MARGIN if col == 3 else 0
                    tile = elf.placed_tile(self.game, sample, self.floor, 2, pad, pad, 0)
                page.paste(tile, (col * 110 + 7, y))
        label(page, (10, 465), "Retail warrior 1252 and priest 1563 are shown in their own map colors.", 12)
        page.save(out / "half-elf-references.png")

    def gallery(self, out):
        out.mkdir(parents=True, exist_ok=True)
        self.references(out)
        frames = []
        sheets = [Image.new("RGB", (704, 45 + 29 * 80), dwarf.PAPER) for key in FIGURES]
        for sheet, key in zip(sheets, FIGURES):
            label(sheet, (8, 5), key.capitalize() + " · all poses", 15)
            for j, role in enumerate(ROLES):
                label(sheet, (157 + j * 120, 26), role, 12, "ma")
        for pose, name in enumerate(dwarf.NAMES):
            page = Image.new("RGB", (684, 339), dwarf.PAPER)
            label(page, (12, 8), "Half-elf outfit study", 20)
            label(page, (672, 10), name, 15, "ra")
            for i, key in enumerate(FIGURES):
                y = 65 + i * 135
                label(page, (9, y + 40), ("Female", "Male")[i], 14)
                label(sheets[i], (6, 67 + pose * 80), f"{pose:02d}  {name}", 11)
                for j, role in enumerate(ROLES):
                    x = 66 + j * 124
                    if i == 0:
                        label(page, (x + 57, 39), role, 14, "ma")
                    tile = self.tile(key, pose, role, 1)
                    page.paste(tile.resize((104, 88), Image.Resampling.NEAREST), (x+5, y))
                    page.paste(tile, (x+31, y+89))
                    sheets[i].paste(tile.crop((2, 4, 50, 44)).resize((96, 80), Image.Resampling.NEAREST),
                                    (109 + j*120, 45 + pose*80))
            frames.append(page)
        loop(frames, out / "half-elf-study.gif")
        frames[0].save(out / "half-elf-study.png")
        for sheet, sex in zip(sheets, ("female", "male")):
            sheet.save(out / f"half-elf-{sex}-poses.png")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("game_dir", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    Study(args.game_dir).gallery(args.output)
