"""Build the elf body and first three outfit studies from a Shattered Lands installation.

python prototypes/elfoutfits.py GAME_DIR OUTPUT_DIR
"""

import argparse
from pathlib import Path
from statistics import median

from PIL import Image, ImageDraw

import dwarfoutfits as dwarf
import outfits
from dsloader import classoutfits, figures

MODELS = ((figures.ELF_WOMAN, "Female"), (figures.ELF_MAN, "Male"))
STUDIES = ("Original", "Body base", "Gladiator", "Fighter", "Cleric")
FLESH = (129, 134, 132, 130, 145, 147)
GOLD = {44, 45, 64, 65, 179, 180, 181, 182, 183, 200, 201}
SHIRTS = {
    figures.ELF_MAN: {24, 29, 38, 39, 48, 49, 50, 158, 159, 160, 161, 162},
    figures.ELF_WOMAN: {36, 37, 58, 59, 60, 174, 175, 176, 177, 178},
}
# Native x bounds of the skirt near the knees, from side idle through side steps 1–4.
SIDE_HEMS = {
    figures.ELF_WOMAN: {2: (0, 8), 11: (1, 8), 12: (4, 13), 13: (0, 7), 14: (2, 11)},
    figures.ELF_MAN: {2: (-1, 7), 11: (-1, 6), 12: (1, 10), 13: (0, 7), 14: (2, 11)},
}
PAD = 4


def render(game, model, pose, role):
    combat, frame = divmod(pose, 15)
    fig = game.fig(model)
    source = fig.rows(combat, frame)
    height, width = len(source), len(source[0])
    if role == "Original":
        return [row[:] for row in source]
    fallen = pose == 28
    rows = source[::-1] if fallen else source
    parts = fig.parts(combat, frame)

    def point_up(point):
        x, y = point
        return (x, height - 1 - y if fallen else y)

    hair = {point_up(p) for p in parts.hair}
    bow = game.bow(fig, source, parts) if pose in (24, 25, 26) else set()
    bow = {point_up(p) for p in bow}
    protected = hair | bow
    head = parts.head
    if head:
        face_x = (head.left + head.right) / 2
        brow = head.brow
    else:
        # The fallen sprites are drawn head-down; find the crown in the
        # upright copy. Gold hair and the bow use common palette entries.
        crown = [(x, y) for y, row in enumerate(rows[:8]) for x, c in enumerate(row) if c in GOLD]
        face_x = median(x for x, y in crown)
        brow = min(y for x, y in crown) + 3

    if fallen:
        # Each death frame is a separate drawing. Read the torso feet-down.
        shoulder, waist = (8, 13) if model == figures.ELF_WOMAN else (7, 14)
    else:
        shoulder, waist = parts.shoulders[0], parts.waist
    shirt = SHIRTS[model]

    def axis(y):
        points = [x for r in rows[max(0, y - 1) : y + 2] for x, c in enumerate(r) if c in shirt]
        return median(points) if points else (width - 1) / 2

    upper = axis(shoulder)
    hip = axis(waist - 2)
    profile = pose in (2, 11, 12, 13, 14, 21, 22, 23, 24, 25)
    rear = pose in (1, 7, 8, 9, 10, 18, 19, 20, 25)
    lit = [sum(v * w for v, w in zip(rgb, (0.299, 0.587, 0.114))) for rgb in game.palette]
    out = [[None] * (width + 2 * PAD) for _ in range(height + 2 * PAD)]
    body = {(x, y) for y, row in enumerate(rows) for x, c in enumerate(row) if c is not None}
    for y, row in enumerate(rows):
        t = max(0, min(1, (y - shoulder) / max(1, waist - shoulder)))
        center = upper + (hip - upper) * t
        radius = (2.8 if profile else 4.3) - 0.7 * t
        depth = y - waist
        for x in range(-PAD, width + PAD):
            c = row[x] if 0 <= x < width else None
            dx = x - center
            u = dx / radius
            paint = c
            # The original chin and hair fall in front of the costume. The stock
            # cuffs are removed, but the hand crossing the chest stays in front.
            face = abs(x - face_x) <= 2.5 and brow - 1 <= y <= brow + 3
            # The two green (woman) or blue (man) eye pixels in front view
            # share colors with the stock costume. Preserve them inside the face.
            native_face = c in outfits.SKINC or c in (77, 158, 159, 188, 254)
            foreground = c is not None and (
                (x, y) in protected or c in GOLD or (face and native_face)
            )
            arm = c is not None and (
                c in (249, 250)
                or (
                    c in outfits.SKINC
                    and shoulder - 1 <= y <= waist + 2
                    and (
                        abs(u) > 0.8
                        or y < waist
                        and any(abs(x - hx) + abs(y - hy) <= 4 for hx, hy in parts.hands.values())
                    )
                )
            )
            if c is not None and not foreground:
                if y >= waist + 1:
                    # Shade the two limbs independently at their actual locations.
                    start = x
                    while (start - 1, y) in body:
                        start -= 1
                    end = x
                    while (end + 1, y) in body:
                        end += 1
                    pos = (x - start + 0.5) / (end - start + 1)
                    tone = 1 if pos > 0.72 else 4 if 0.18 < pos < 0.54 else 2
                    if (x, y + 1) not in body:
                        tone = max(0, tone - 1)
                else:
                    tone = 1 if u > 0.65 else 4 if -0.8 < u < -0.18 else 2
                    # Short light across the ribs, a recessed waist and a
                    # rounded hip; the arm swing retains the original lighting.
                    if 0.17 < t < 0.42 and -0.8 < u < 0.62:
                        tone = 3 if abs(u) < 0.18 else 5
                    elif 0.42 <= t < 0.58 and abs(u) < 0.76:
                        tone = 1 if u > 0.10 else 2
                    elif 0.75 < t < 0.99 and -0.66 < u < 0.18:
                        tone = 3
                if c not in outfits.SKINC or (not arm and y >= shoulder - 1):
                    paint = FLESH[tone]
            if role != "Body base" and not foreground and not arm:
                torso = c is not None and shoulder - 2 <= y <= waist and abs(dx) <= radius + 1
                rank = 0 if u > 0.85 else 1 if u > 0.25 else 3 if -0.9 < u < -0.22 else 2
                if c is not None and lit[c] > 125 and rank == 3:
                    rank = 4
                if role == "Gladiator":
                    if torso and abs(dx - (1.8 - 3.8 * t)) < 1.12:
                        paint = dwarf.LEATHER[0 if depth == -1 else rank]
                    if c is not None and 0 <= depth <= 3 and abs(dx) <= radius + 1:
                        paint = dwarf.LEATHER[rank]
                elif role == "Fighter":
                    if torso or (c is not None and 0 <= depth <= 3 and abs(dx) <= radius + 1):
                        paint = dwarf.LEATHER[rank]
                        if torso and abs(dx - (1.9 - 4 * t)) < 0.8:
                            paint = dwarf.HIDE[2]
                elif role == "Cleric" and shoulder - 1 <= y <= waist + 6:
                    fall = max(0, depth) / 6
                    hem_center = center - (1.7 * fall if profile else 0.5 * fall)
                    breadth = radius + 1.65 * fall
                    if depth > 0 and pose in SIDE_HEMS[model]:
                        left, right = SIDE_HEMS[model][pose]
                        hem_center = center * (1 - fall) + (left + right) / 2 * fall
                        breadth = radius * (1 - fall) + (right - left + 1) / 2 * fall
                    # Fill the narrow wedge behind her crossing wrist at the
                    # top of the skirt in the last profile step.
                    if model == figures.ELF_WOMAN and pose == 14 and depth == 1:
                        breadth += 0.5
                    fold = (x - hem_center) / breadth
                    if (
                        abs(fold) <= 1
                        and (y > shoulder or c is not None)
                        and depth <= 6 - int(fold > 0.25)
                    ):
                        crease = 0.22 - 0.55 * fall + 0.12 * (1 - t)
                        shade = (
                            0
                            if fold > 0.87
                            else 1 if abs(fold - crease) < 0.16 or fold > 0.58 else 2
                        )
                        if -0.76 + 0.17 * fall < fold < -0.44 + 0.13 * fall:
                            shade = 4 if y > shoulder + 1 else 3
                        if 0.39 < fold < 0.60 and depth >= 2:
                            shade = 3
                        if depth == 6 or (depth == 5 and fold > 0.35):
                            shade = max(1, shade - 1)
                        paint = dwarf.CREAM[shade]
                if depth == 0 and abs(dx) <= radius and paint is not None:
                    paint = 169 if abs(dx) < 0.55 else 205
                # Follow the actual sleeve pixels on the upper arm; the far
                # shoulder can disappear behind the braid or raised forearm.
                outside = (1 if rear else -1) * dx
                if (
                    role in ("Gladiator", "Fighter")
                    and c in shirt
                    and shoulder - 2 <= y <= shoulder + 1
                    and abs(u) > 0.55
                    and (role == "Fighter" or outside > 0)
                ):
                    ramp = dwarf.BONE if role == "Fighter" else dwarf.BRONZE
                    paint = ramp[3 if y == shoulder - 1 else 0 if y == shoulder + 1 else 2]
            if paint is not None:
                out[y + PAD][x + PAD] = paint
    if fallen:
        out.reverse()
    # Use the same foreground ear pass as the live elf renderer.
    return figures.ears_over(out, source, model, frame, bool(combat), PAD)


def tile(game, model, pose, role, terrain, scale):
    rows = render(game, model, pose, role)
    extra = 0 if role == "Original" else PAD
    return placed_tile(game, rows, terrain, scale, extra, extra, extra)


def placed_tile(game, rows, terrain, scale, left, top, bottom):
    h = len(rows) - top - bottom
    w = len(rows[0]) - 2 * left
    canvas = terrain.copy()
    ox = (canvas.width - w) // 2 - left
    oy = canvas.height - 2 - h - top
    for y, row in enumerate(rows):
        for x, c in enumerate(row):
            if c is not None:
                assert 0 <= x + ox < canvas.width and 0 <= y + oy < canvas.height
                canvas.putpixel((x + ox, y + oy), game.palette[c])
    return canvas.resize((canvas.width * scale, canvas.height * scale), Image.Resampling.NEAREST)


def reference_sheet(game, terrain):
    im = Image.new("RGB", (781, 467), dwarf.PAPER)
    pen = ImageDraw.Draw(im)
    pen.text((12, 8), "Elf and human outfits", font=dwarf.board_font(20), fill=dwarf.INK)
    columns = (
        "Original elf",
        "Elf Cleric",
        "Human Cleric",
        "Elf Fighter",
        "Human Fighter",
        "Elf Gladiator",
        "Human Gladiator",
    )
    for i, caption in enumerate(columns):
        pen.text(
            (113 + 101 * i, 46), caption, font=dwarf.board_font(12), fill=dwarf.INK, anchor="ma"
        )
    for j, (model, sex) in enumerate(MODELS):
        human = 2099 if model == figures.ELF_WOMAN else 2095
        for i, pose in enumerate((0, 13)):
            y = 68 + (2 * j + i) * 98
            pen.text((5, y + 18), sex, font=dwarf.board_font(12), fill=dwarf.INK)
            pen.text(
                (5, y + 38),
                "Front" if pose == 0 else "Side 3/4",
                font=dwarf.board_font(11),
                fill=dwarf.INK,
            )
            samples = [tile(game, model, pose, "Original", terrain, 2)]
            for role, alias in (
                ("Cleric", "Priest"),
                ("Fighter", "Warrior"),
                ("Gladiator", "Gladiator"),
            ):
                samples.append(tile(game, model, pose, role, terrain, 2))
                rows = classoutfits.frames(alias, False, human)[pose].canvas(
                    game.fr(human, pose), 10
                )
                samples.append(placed_tile(game, rows, terrain, 2, 10, 10, 0))
            for n, sample in enumerate(samples):
                im.paste(sample, (69 + 101 * n, y))
    return im


def gallery(game, output):
    terrain = (
        Image.open(
            Path(__file__).resolve().parents[1] / "playtest/logs/img/2026-11-18-alt-arena.png"
        )
        .convert("RGB")
        .crop((51, 154, 95, 194))
    )
    frames = []
    for k, name in enumerate(dwarf.NAMES):
        im = Image.new("RGB", (777, 438), dwarf.PAPER)
        pen = ImageDraw.Draw(im)
        pen.text((12, 10), "Elf outfit study", font=dwarf.board_font(21), fill=dwarf.INK)
        pen.text((765, 14), name, font=dwarf.board_font(15), fill=dwarf.INK, anchor="ra")
        for col, role in enumerate(STUDIES):
            cx = 136 + col * 143
            pen.text((cx, 48), role, font=dwarf.board_font(15), fill=dwarf.INK, anchor="ma")
        for j, (_, sex) in enumerate(MODELS):
            pen.text((8, 124 + j * 181), sex, font=dwarf.board_font(14), fill=dwarf.INK)
        im = im.quantize(32).convert("RGB")
        for j, (model, _) in enumerate(MODELS):
            for col, role in enumerate(STUDIES):
                cx = 136 + col * 143
                for scale, offset in ((3, 73), (1, 196)):
                    t = tile(game, model, k, role, terrain, scale)
                    im.paste(t, (cx - t.width // 2, offset + j * 181))
        q = im.quantize(256, dither=Image.Dither.NONE)
        assert q.convert("RGB").tobytes() == im.tobytes()
        frames.append(q)
    output.mkdir(exist_ok=True, parents=True)
    frames[0].save(output / "elf-first-pass.png")
    reference_sheet(game, terrain).save(output / "elf-human-reference.png")
    for row, (_, sex) in enumerate(MODELS):
        # Fixed-size tiles for stepping through the individual source poses.
        sheet = Image.new("RGB", (3 * 465, 10 * 118), dwarf.PAPER)
        for k, frame in enumerate(frames):
            x, y = (k % 3) * 465, (k // 3) * 118
            pen = ImageDraw.Draw(sheet)
            pen.text((x + 4, y), dwarf.NAMES[k], font=dwarf.board_font(12), fill=dwarf.INK)
            for i in range(len(STUDIES)):
                cx = 136 + 143 * i
                top = 196 + 181 * row
                t = frame.crop((cx - 22, top, cx + 22, top + 40)).resize(
                    (88, 80), Image.Resampling.NEAREST
                )
                sheet.paste(t, (x + 3 + 92 * i, y + 18))
                pen.text(
                    (x + 3 + 92 * i, y + 99), STUDIES[i], font=dwarf.board_font(10), fill=dwarf.INK
                )
        sheet.save(output / f"elf-{sex.lower()}-poses.png")
    keys = [0, 3, 4, 5, 6, 0, 1, 7, 8, 9, 10, 1, 2, 11, 12, 13, 14, 2, *range(15, 29)]
    frames[0].save(
        output / "elf-first-pass.gif",
        save_all=True,
        append_images=[frames[k] for k in keys[1:]],
        duration=[1000 if k < 3 or k >= 24 else 300 for k in keys],
        loop=0,
        disposal=1,
        optimize=False,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("game_dir")
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()
    gallery(outfits.Game(args.game_dir), args.output_dir)
