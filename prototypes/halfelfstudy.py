"""Draw the half-elf single-class outfit study on the Loader's actual figure geometry.

python prototypes/halfelfstudy.py GAME_DIR OUTPUT_DIR
"""
import argparse
from functools import lru_cache
from pathlib import Path
from zipfile import ZipFile

from PIL import Image

import elfoutfits as elf
import halfelfpairs as pairs
import outfits
from outfitdetail import RAMPS
from thiefhood import FRONT, OLD_SLATE, SLATE
from dsloader import art, classoutfits as co, figures
from elfreview import TERRAIN, dwarf, label, loop

ROLES = ("Original", "Body base", "Gladiator", "Fighter", "Cleric")
NEW_SINGLES = ("Druid", "Preserver", "Psionicist", "Ranger", "Thief")
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

# Crest of the trailing fold, from shoulder towards hem in each profile pose.
# The gap above the woman's third step is where her raised arm crosses the cloth.
MANTLE_CREST = {
    outfits.HALF_ELF_WOMAN: {
        2: (8, (3, 3, 2, 2, 1, 1, 0, 0, -1, -1)),
        11: (8, (2, 2, 2, 1, 1, 1, 0, 0, -1)),
        12: (8, (4, 4, 3, 3, 2, 2, 1, 1, 0, -1)),
        13: (9, (7, 7, 6, 6, 5, 5, 4, 3, 2)),
        14: (8, (6, 5, 5, 4, 4, 3, 2, 2, 1, 0, 1)),
    },
    outfits.HALF_ELF_MAN: {
        2: (9, (2, 1, 1, 1, 0, 0, -1, 0, -1, -1)),
        11: (8, (-1, -1, -2, -2, -3, -3, -4, -4, -3, -3, -4)),
        12: (7, (3, 2, 1, 0, -1, -2, -2, -3, -3, -4, -5)),
        13: (7, (2, 1, 1, 0, -1, -1, -2, -2, -2, -3, -4, -5)),
        14: (9, (1, 1, 1, 0, 0, -1, -1, -2, -2, -2, -3)),
    },
}

# Left edge of the overlapping reeds on the near hip, one x per front pose.
REED_PLEAT = {0: 7, 3: 6, 4: 8, 5: 8, 6: 5, 15: 6, 16: 10, 17: 13, 24: 9}


class Study:
    def __init__(self, game_dir):
        self.game = outfits.Game(game_dir)
        self.floor = Image.open(TERRAIN).convert("RGB").crop((50, 150, 102, 194))
        with ZipFile(Path(co.__file__).with_name("woman_outfit_layers.zip")) as archive:
            self.body = [art.decode_frame(archive.read("Base/" + tag), f)[2]
                         for tag, count in (("walk", 15), ("combat", 14)) for f in range(count)]

    @lru_cache(None)
    def rows(self, key, pose, role):
        if role in pairs.ROSTER:
            return pairs.draw_pair(self, key, pose, role)
        cb, f = divmod(pose, 15)
        fig = self.game.fig(key)
        stock = fig.rows(cb, f)
        if role == "Original":
            return stock, 0
        model = fig.model
        src = self.game.fr(model + cb, f)
        female = key == outfits.HALF_ELF_WOMAN
        if role == "Druid" and not female:
            return self.druid(key, pose, fig), MARGIN
        parent = {"Fighter": "Warrior", "Cleric": "Priest", "Preserver": "Mage"}.get(role, role) if female else role
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
        folds = {(x, y) for x, y, _ in fields.cloak}
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
                hood = role == "Thief" and (sx, y) in folds and color in OLD_SLATE
                if (sx, y) in bow:
                    color = native
                elif not hood and ((sx, y) in scalp or (head_row and own != native and
                        (own in figures.GOLDEN_HAIR or own in outfits.SKINC or own is None))):
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
        elif female and role == "Ranger" and pose in (2, 11, 13):
            # A tip of the human quiver shows through the shortened hair.
            x, y = {2: (0, 4), 11: (4, 4), 13: (9, 5)}[pose]
            out[y + MARGIN][x + MARGIN] = None
        elif female and role == "Druid":
            out = self.druid(key, pose, fig, out)
        elif role == "Preserver" and pose in MANTLE_CREST[key]:
            start, crest = MANTLE_CREST[key][pose]
            for step, x in enumerate(crest):
                row = out[start + step + MARGIN]
                # Ease the highlight into the shoulder and back into the hem.
                dist = min(step, len(crest) - 1 - step)
                light = (59, 118, 239)[min(dist, 2)]
                for dx, tone in ((0, light), (1, 175)):
                    px = x + dx + MARGIN
                    if row[px] in RAMPS["plum"] or row[px] in (18, 19, 233, 238):
                        row[px] = tone
        elif role == "Psionicist" and female:
            # Fit the wrap to the narrow torso. The human cape underpaint
            # also has cloth trailing behind her shoulder and striking wrist.
            body, pad = self.rows(key, pose, "Body base")
            forearm = set(fields.regions[co.FOREARM])
            for py, row in enumerate(out):
                for px in range(len(row)):
                    x, y = px - pad, py - pad
                    if body[py][px] is None or (back(x, y), y) in forearm:
                        row[px] = body[py][px]
        elif role == "Thief":
            self.finish_hood(out, key, pose, fields, back)
        # Pinholes inside the rim beside her cheek on the side strike and bow.
        if female and role == "Thief":
            for x, y in {21: ((17, 9), (17, 10)), 26: ((11, 6),)}.get(pose, ()):
                out[y + MARGIN][x + MARGIN] = SLATE[0]
        return out, MARGIN

    def finish_hood(self, out, key, pose, fields, back):
        # These are the half-elf's actual bun and jaw positions. The human
        # woman's flying hair had lifted the crown far above her raised arm.
        panels = {
            16: (6, 2, FRONT),
            21: (9, 5, FRONT),
            27: (1, -1, ("...2332...", "..344321..", ".24323221.",
                          ".23221..21", "2321....11", "231......1",
                          "231.......", ".21.......")),
        }
        if key == FIGURES[0] and pose in panels:
            body, pad = self.rows(key, pose, "Body base")
            ox, oy, panel = panels[pose]
            bottom = oy + len(panel)
            # Preserve the hanging cloak below the end of the hood. At the
            # struck shoulder the hand stays in front of the near cheek.
            for y in range(-pad, bottom):
                for x in range(-pad, len(out[0])-pad):
                    point = back(x, y), y
                    if point in fields.regions[co.FOREARM] or point in fields.regions[co.BOW]:
                        continue
                    old = out[y+pad][x+pad]
                    if old in OLD_SLATE:
                        out[y+pad][x+pad] = body[y+pad][x+pad]
                    cx, cy = x-ox, y-oy
                    if 0 <= cy < len(panel) and 0 <= cx < len(panel[cy]):
                        stitch = panel[cy][cx]
                        if stitch != ".":
                            out[y+pad][x+pad] = SLATE[int(stitch)]
        if key == FIGURES[0]:
            # Cover the back of the bun where it extends past the parent rim.
            # The fallen figure's crown points toward the bottom of the frame.
            crown = {
                2: ((1, 0, "2"),), 11: ((5, 0, "2"),), 12: ((7, 0, "23"),),
                13: ((10, 0, "2"),), 14: ((5, 0, "23"), (5, 1, "2"), (5, 2, "1")),
                22: ((12, 0, "23"), (12, 1, "2")), 23: ((12, 0, "23"),),
                28: ((3, 13, "2"), (3, 14, "2"), (3, 15, "2"),
                     (3, 16, "2343221"), (3, 17, "2344321"), (4, 18, "232")),
            }
            for left, y, strip in crown.get(pose, ()):
                for x, rank in enumerate(strip, left):
                    if out[y+MARGIN][x+MARGIN] in figures.GOLDEN_HAIR:
                        out[y+MARGIN][x+MARGIN] = SLATE[int(rank)]
        # Close the single-pixel gap where the shortened nape meets the rim.
        nape = ({4: (13, 3), 5: (12, 3)} if key == FIGURES[0]
                else {11: (3, 5), 13: (5, 5)})
        if pose in nape:
            x, y = nape[pose]
            out[y+MARGIN][x+MARGIN] = SLATE[1]

    def druid(self, key, pose, fig, source=None):
        """Shape the leaf cape and reed wrap at the registered hip in each pose."""
        cb, f = divmod(pose, 15)
        body, pad = self.rows(key, pose, "Body base")
        linen, _ = self.rows(key, pose, "Cleric")
        female = key == FIGURES[0]
        source_role = "Druid" if female else "Ranger"
        if source is None:
            source, _ = self.rows(key, pose, source_role)
        frame = co.frames(source_role, cb, fig.model)[f]
        folds = {(x, y) for x, y, _ in frame.cloak}
        robe = co.frames("Priest" if female else "Cleric", cb, fig.model)[f]
        legs = set(robe.regions[co.LEGS])
        crossed = set(frame.regions[co.BOW] + frame.regions[co.FOREARM])
        back = figures.mover_back(fig.maker.cuts[bool(cb), f])
        parts = fig.parts(cb, f)
        if pose == 28:
            waist, center = (12, 9) if female else (14, 10)
        else:
            waist = parts.waist
            _, left, right = parts.shoulders
            center = (left + right) // 2
        height = len(body) - pad
        cape = dict(zip(RAMPS["leaf"], (208, 17, 69, 188, 53, 53, 54, 54, 55, 55, 56, 56, 57)))
        reed = (204, 205, 94, 95, 97, 168, 169, 170, 171)
        out = [row[:] for row in body]
        for py, row in enumerate(out):
            y = py - pad
            upright = height - 1 - y if pose == 28 else y
            for px, skin in enumerate(row):
                x = px - pad
                point = back(x, y), y
                hem = waist + 1 - min(4, abs(x - center + 2) // 2)
                if female and (upright <= hem or point in crossed):
                    row[px] = source[py][px]
                    continue
                if point in crossed:
                    continue
                # The wrapped skirt sits higher on the far hip. Use the
                # registered robe folds down to the upper thigh only.
                depth = upright - waist
                hem_depth = 4 - int(x > center + 1) - int(x < center - 4)
                if -1 <= depth <= hem_depth and point in legs:
                    cloth = linen[py][px]
                    if cloth is not None:
                        r, g, b = self.game.palette[cloth]
                        rank = min(8, (2*r + 3*g + b) // 150)
                        row[px] = reed[rank] if depth < hem_depth else reed[max(0, rank-2)]
                        if not female and pose in REED_PLEAT and depth >= 1:
                            # Warm the broad lit panel, then turn one lip into shadow.
                            lip = REED_PLEAT[pose] - int(depth >= 3)
                            if row[px] == 171:
                                row[px] = 169
                            if x == lip:
                                row[px] = 168 if depth == hem_depth else 170
                            elif x == lip + 1:
                                row[px] = 95 if depth == hem_depth else 94
                # The folded corner is longest toward the trailing shoulder.
                cloth = source[py][px]
                if upright <= hem and point in folds and cloth in cape and cloth != skin:
                    row[px] = cape[cloth]
                    if upright == hem and (x - center) % 3:
                        row[px] = 188 if cloth in (54, 55, 56, 57) else 69
        # These Ranger fold tips belong to the part of the long cape that
        # swings clear of the shorter Druid cape.
        tips = {} if female else {13: ((10, 9),), 17: ((22, 8), (23, 8), (22, 9))}
        for x, y in tips.get(pose, ()):
            out[y+pad][x+pad] = body[y+pad][x+pad]
        # His spread-leg strikes expose terrain between the tied reeds and
        # the torso. Turn the top lip of the kilt upward into that space.
        if not female:
            seams = {
                16: ((11, 12, 205), (10, 13, 97), (11, 13, 94),
                     (12, 13, 168), (13, 13, 95)),
                21: ((18, 22, 95),),
                22: ((7, 16, 95),),
                # The short leaf panel shows behind the bent arm on the bow.
                26: ((11, 12, 69), (11, 14, 188), (12, 15, 69)),
            }
            for x, y, color in seams.get(pose, ()):
                out[y + pad][x + pad] = color
        return out

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

    def cloak_reference(self, out):
        samples = ("Druid", "Ranger", "Preserver", 724, "Thief", 630)
        page = Image.new("RGB", (806, 604), dwarf.PAPER)
        label(page, (10, 8), "Cloaks on the arena floor", 20)
        for col, caption in enumerate(("Druid", "Ranger", "Preserver", "Retail mage", "Thief", "Retail thief")):
            label(page, (143 + 120 * col, 40), caption, 13, "ma")
        for i, (key, pose) in enumerate((key, p) for key in FIGURES for p in (1, 12)):
            y = 61 + i * 135
            label(page, (6, y + 32), "Female" if key == FIGURES[0] else "Male")
            label(page, (6, y + 52), dwarf.NAMES[pose], 11)
            for col, sample in enumerate(samples):
                if isinstance(sample, str):
                    tile = self.tile(key, pose, sample, 1)
                else:
                    rows = self.game.fr(sample, pose)
                    tile = elf.placed_tile(self.game, rows, self.floor, 1, 0, 0, 0)
                x = 90 + col * 120
                page.paste(tile.resize((104, 88), Image.Resampling.NEAREST), (x, y))
                page.paste(tile, (x + 26, y + 88))
        page.save(out / "half-elf-cloak-references.png")

    def hooded_cape_walk(self, out):
        cycle = (1, 7, 8, 9, 10, 1, 2, 11, 12, 13, 14, 2, 0, 3, 4, 5, 6, 0)
        frames = []
        for pose in cycle:
            page = Image.new("RGB", (684, 213), dwarf.PAPER)
            label(page, (10, 7), "Half-elf capes in motion", 19)
            label(page, (page.width - 10, 9), dwarf.NAMES[pose], 14, "ra")
            for col, (caption, role) in enumerate((
                    ("Half-elf woman", "Druid/Thief"), ("Half-elf woman", "Ranger/Thief"),
                    ("Half-elf man", "Druid/Thief"), ("Half-elf man", "Ranger/Thief"),
                    ("Shattered Lands", 630), ("Shattered Lands", 724))):
                x = 5 + col * 113
                if isinstance(role, str):
                    tile = self.tile(FIGURES[col // 2], pose, role, 1)
                    name = role
                else:
                    tile = elf.placed_tile(self.game, self.game.fr(role, pose), self.floor, 1, 0, 0, 0)
                    name = "Thief" if role == 630 else "Mage"
                label(page, (x + 54, 40), caption, 11, "ma")
                label(page, (x + 54, 57), name, 14, "ma")
                page.paste(tile.resize((104, 88), Image.Resampling.NEAREST), (x, 77))
                page.paste(tile, (x + 26, 167))
            frames.append(page.quantize(256, dither=Image.Dither.NONE))
        frames[0].save(out / "half-elf-hooded-cape-walk.gif", save_all=True,
                       append_images=frames[1:], loop=0, disposal=1,
                       duration=[780 if pose < 3 else 230 for pose in cycle])

    def gallery(self, out):
        out.mkdir(parents=True, exist_ok=True)
        self.references(out)
        self.cloak_reference(out)
        self.hooded_cape_walk(out)
        self.pose_gallery(out, ROLES, "study", "Half-elf outfit study")
        self.pose_gallery(out, ROLES[2:] + NEW_SINGLES, "singles", "Half-elf single classes")

        for group, bases in pairs.GROUPS:
            roles = [role for role in pairs.ROSTER if pairs.base_class(role) in bases]
            self.pose_gallery(out, roles, "pairs-" + group, "Half-elf two-class outfits")

    def pose_gallery(self, out, roles, stem, title):
        frames = []
        width = 684 + (len(roles) - 5) * 124
        sheets = [Image.new("RGB", (104 + len(roles) * 120, 45 + 29 * 80), dwarf.PAPER) for key in FIGURES]
        for sheet, key in zip(sheets, FIGURES):
            label(sheet, (8, 5), key.capitalize() + " · all poses", 15)
            for j, role in enumerate(roles):
                label(sheet, (157 + j * 120, 26), role, 10 if "/" in role else 12, "ma")
        for pose, name in enumerate(dwarf.NAMES):
            page = Image.new("RGB", (width, 339), dwarf.PAPER)
            label(page, (12, 8), title, 20)
            label(page, (width - 12, 10), name, 15, "ra")
            for i, key in enumerate(FIGURES):
                y = 65 + i * 135
                label(page, (9, y + 40), ("Female", "Male")[i], 14)
                label(sheets[i], (6, 67 + pose * 80), f"{pose:02d}  {name}", 11)
                for j, role in enumerate(roles):
                    x = 66 + j * 124
                    if i == 0:
                        label(page, (x + 57, 39), role, 11 if "/" in role else 14, "ma")
                    tile = self.tile(key, pose, role, 1)
                    page.paste(tile.resize((104, 88), Image.Resampling.NEAREST), (x+5, y))
                    page.paste(tile, (x+31, y+89))
                    sheets[i].paste(tile.crop((2, 4, 50, 44)).resize((96, 80), Image.Resampling.NEAREST),
                                    (109 + j*120, 45 + pose*80))
            frames.append(page)
        loop(frames, out / f"half-elf-{stem}.gif")
        frames[0].save(out / f"half-elf-{stem}.png")
        for sheet, sex in zip(sheets, ("female", "male")):
            prefix = "" if stem == "study" else stem + "-"
            sheet.save(out / f"half-elf-{prefix}{sex}-poses.png")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("game_dir", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    Study(args.game_dir).gallery(args.output)
