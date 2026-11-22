"""Render a dwarf outfit study from the player's own Shattered Lands figures.

    python3 prototypes/dwarfoutfits.py GAME_DIR OUTPUT_DIR

Write a labeled animation for each dwarf figure. Coordinates below are in its
native frame. The fallen pose is drawn feet-down, then turned back for display.
"""

import argparse
from pathlib import Path
from typing import NamedTuple

from PIL import Image, ImageDraw, ImageFont

import outfits


class Pose(NamedTuple):
    crown_x: int
    crown_y: int
    shoulder_x: int
    shoulder_y: int
    hip_x: int
    hip_y: int


# The collar travels with the rib cage. In profile the head leads the hip.
POSES = [
    (10, 0, 10, 5, 10, 12),
    (10, 0, 10, 5, 9, 12),
    (8, 0, 5, 6, 4, 12),
    (9, 0, 9, 5, 9, 12),
    (9, 0, 9, 5, 9, 11),
    (9, 0, 9, 5, 9, 11),
    (10, 0, 10, 5, 10, 11),
    (7, 0, 7, 5, 7, 12),
    (6, 0, 6, 5, 6, 12),
    (7, 0, 7, 5, 7, 12),
    (7, 0, 7, 5, 7, 12),
    (7, 0, 4, 6, 3, 11),
    (12, 0, 9, 5, 7, 12),
    (8, 0, 5, 6, 4, 12),
    (11, 0, 8, 5, 7, 12),
    (7, 2, 7, 7, 5, 14),
    (11, 0, 11, 5, 10, 10),
    (8, 4, 10, 9, 10, 12),
    (6, 0, 6, 5, 6, 12),
    (5, 0, 7, 5, 7, 11),
    (6, 0, 8, 5, 9, 11),
    (8, 0, 8, 5, 9, 11),
    (14, 0, 11, 5, 8, 11),
    (13, 0, 10, 5, 7, 10),
    (8, 0, 7, 5, 6, 12),
    (5, 3, 6, 8, 6, 14),
    (7, 3, 8, 8, 9, 14),
    (7, 3, 6, 7, 8, 11),
    (6, 1, 6, 5, 7, 11),
]
ROLES = ("Warrior", "Thief", "Priest", "Mage", "Druid", "Ranger", "Gladiator", "Psionicist")
LEATHER = (208, 88, 207, 92, 96)
BONE = (207, 194, 61, 199, 63)
HOOD = (208, 17, 20, 24, 28)
CREAM = (207, 194, 61, 199, 155)
PLUM = (17, 174, 175, 58, 119)
LEAF = (207, 188, 54, 55, 56)
OCHRE = (204, 95, 168, 169, 170)
FOREST = (17, 69, 53, 54, 56)
BRONZE = (88, 203, 94, 168, 185)
TEAL = (17, 69, 70, 71, 73)
FLESH = (134, 132, 130, 145, 147)
CLOAK_LENGTHS = {"Thief": 4, "Mage": 3, "Druid": 3, "Ranger": 4, "Priest": 5}
RAMPS = (LEATHER, HOOD, CREAM, PLUM, LEAF, FOREST, LEATHER, TEAL)
NAMES = (
    ["Front idle", "Rear idle", "Side idle"]
    + [f"{side} walk {i}/4" for side in ("Front", "Rear", "Side") for i in range(1, 5)]
    + [f"{side} strike {i}/3" for side in ("Front", "Rear", "Side") for i in range(1, 4)]
    + ["Front bow", "Rear bow", "Side bow", "Hit", "Fallen"]
)


def draw(game, model, k, role):
    combat, f = divmod(k, 15)
    figure = game.fig(model)
    rows = figure.rows(combat, f)
    dead = k == 28
    if dead:
        rows = rows[::-1]
    height, width = len(rows), len(rows[0])
    pose = Pose(*POSES[k])
    if model == 2053 and k == 15:
        pose = Pose(*POSES[0])  # her first strike uses a standing wind-up
    cx, cy, sx, sy, hx, hy = pose
    profile = k in (2, 11, 12, 13, 14, 21, 22, 23, 24, 25)
    rear = k in (1, 7, 8, 9, 10, 18, 19, 20, 25)
    bow = game.bow(figure, rows, figure.parts(combat, f)) if k in (24, 25, 26) else set()
    palette = RAMPS[ROLES.index(role)]
    lower = OCHRE if role == "Druid" else LEATHER if role == "Ranger" else palette
    band = {249: 168, 250: 205}
    hue = [sum(c * v for c, v in zip(rgb, (0.30, 0.59, 0.11))) for rgb in game.palette]
    pad = 4
    pixels = Image.new("P", (width + 2 * pad, height + 2 * pad), 255)
    pixels.putpalette([c for rgb in game.palette for c in rgb])
    hands = set(bow)
    if dead:
        wrists = [(x, y) for y, row in enumerate(rows) for x, c in enumerate(row) if c in band]
    else:
        wrists = figure.bands(combat, f)
    for x, y in wrists:
        for yy in range(max(0, y - 2), min(height, y + 3)):
            for xx in range(max(0, x - 2), min(width, x + 3)):
                if (x - xx) ** 2 + (y - yy) ** 2 <= 5:
                    hands.add((xx, yy))
    for y in range(height):
        t = min(1, max(0, (y - sy) / max(1, hy - sy)))
        mid = sx * (1 - t) + hx * t
        radius = (3 if profile else 4.3) - 0.55 * t
        for x in range(-pad, width + pad):
            c = rows[y][x] if 0 <= x < width else None
            dx = x - mid
            d = y - hy
            depth = y - sy
            head = c is not None and cy <= y < sy and abs(x - cx) <= min(3, 1.5 + (y - cy))
            hand = c is not None and (x, y) in hands
            body = c is not None and not (head or hand)
            paint = c
            # A broad light plane on the near shoulder and a narrow shadow
            # under it read at the dwarves' native height of about 20 pixels.
            shade = 0 if dx > radius - 0.6 else 1 if dx > 1 else 3 if dx > -2.8 else 2
            if c is not None and hue[c] > 145 and dx < 1:
                shade = min(4, shade + 1)
            if c is not None and c not in outfits.SKINC and not (head or hand):
                paint = FLESH[shade if abs(dx) < radius else 1 + int(hue[c] > 65)]
            if body and y >= height - 3 and d > 1:
                paint = LEATHER[1 + int(hue[c] > 65)]
            torso = body and 0 <= depth and d <= 1 and abs(dx) <= radius + 0.5
            if torso:
                paint = palette[shade]
                if role == "Gladiator" and abs(dx - (2 - 4 * t)) > 1.1:
                    paint = c if c in outfits.SKINC else FLESH[shade]
                if role == "Warrior" and abs(dx - (2.5 - 5 * t)) < 1:
                    paint = LEATHER[4 if dx < 2.5 - 5 * t else 1]
                if role == "Priest" and -0.7 < dx + 1.6 - 0.4 * t < 0.7:
                    paint = CREAM[4 if depth % 4 else 1]
                if role == "Mage" and not rear and depth in (2, 3) and abs(dx + 1.1) < 1:
                    paint = PLUM[4 if depth == 2 else 1]
            # Outer cloth rests on the shoulders. Its trailing side swings
            # with the weight transfer and clears the forearm in front views.
            if role in CLOAK_LENGTHS and depth >= 0 and d <= CLOAK_LENGTHS[role]:
                progress = depth / (hy - sy + CLOAK_LENGTHS[role] + 1)
                sway = (-1, 0, 1, 0)[f % 4] if k not in (0, 1, 2, 28) else 0
                center = mid - (2.6 if profile else 0.4) * progress + sway * progress
                breadth = (3.7 if profile else 4.4) + 1.3 * progress
                u = (x - center) / breadth
                if abs(u) < 1 and d <= CLOAK_LENGTHS[role] - max(0, round((u + 0.2) * 1.6)):
                    face = rear or (profile and u < -0.28) or c is None or depth <= 2 and torso
                    if face:
                        crease = u + 0.22 * progress
                        fold = (
                            0
                            if u > 0.85
                            else (
                                1
                                if -0.15 < crease < 0.17 or u > 0.64
                                else 3 if -0.76 < crease < -0.35 else 2
                            )
                        )
                        if -0.63 < crease < -0.48 and depth >= 2:
                            fold = 4
                        paint = palette[fold]
                        if role == "Druid" and d == CLOAK_LENGTHS[role] - max(
                            0, round((u + 0.2) * 1.6)
                        ):
                            paint = OCHRE[min(3, fold)]
            if role == "Priest" and 0 <= d <= min(height - 3 - hy, 6):
                u = dx / (radius + 0.45 * d)
                if abs(u) <= 1 and (d < 6 or abs(u) < 0.8):
                    paint = CREAM[
                        1 if u > 0.55 else 4 if -0.55 < u < -0.25 else 0 if 0.05 < u < 0.26 else 2
                    ]
            if role != "Priest" and 0 <= d <= (4 if role in ("Thief", "Druid") else 3):
                if abs(dx) <= radius + 0.22 * d and (body or role != "Thief" and d <= 2):
                    if (
                        not rear
                        or role not in CLOAK_LENGTHS
                        or role == "Druid"
                        and dx > 1.8
                        or d > CLOAK_LENGTHS[role]
                    ):
                        rank = (
                            0
                            if dx > 2.4
                            else 3 if -2.9 < dx < -0.6 else 1 if abs(dx - 0.7) < 1 else 2
                        )
                        paint = lower[rank]
            if d == 0 and abs(dx) <= radius and not (rear and role in CLOAK_LENGTHS):
                paint = 169 if abs(dx) < 0.5 else 205
            if (
                body
                and 0 <= depth <= 2
                and (
                    role == "Warrior"
                    and abs(abs(dx) - 3.3) < 1.6
                    or role == "Gladiator"
                    and abs(dx - 3) < 1.6
                )
            ):
                paint = (BONE if role == "Warrior" else BRONZE)[
                    4 if depth == 0 else 3 if depth == 1 and dx < 4 else 1
                ]
            if (
                role == "Ranger"
                and -1 <= depth < hy - sy
                and abs(dx - (-3.6 + 0.32 * depth)) < 1.25
                and paint is not None
            ):
                paint = 155 if depth == -1 else 168 if depth == 1 else 205 if dx < -1.8 else 207
            if role == "Psionicist" and torso and abs(dx - (2.5 - 5 * t)) < 0.8:
                paint = 72 if depth > 1 else 169
            if head:
                paint = c
                if role == "Thief" and (rear or y <= cy + 1 or dx < -1.3 or dx > 2.2):
                    paint = HOOD[min(4, int(hue[c] // 42))]
                elif role == "Psionicist" and y == cy + 1:
                    paint = 169 if x == cx else 71
            if hand:
                paint = band.get(c, c) if (x, y) not in bow else c
            if paint is not None:
                pixels.putpixel((x + pad, y + pad), paint)
    if dead:
        pixels = pixels.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
    pixels.info["transparency"] = 255
    return pixels.convert("RGBA")


def gallery(game, model, name):
    # Keep all cells at the same integer scale and on the native foot anchor.
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 14)
    except OSError:
        font = ImageFont.load_default()
    frames = []
    for k, label in enumerate(NAMES):
        gallery = Image.new("RGB", (476, 280), "#322e2b")
        pen = ImageDraw.Draw(gallery)
        pen.text((8, 5), name, fill="#f1e6d4", font=font)
        pen.text((468, 5), label, fill="#f1e6d4", font=font, anchor="ra")
        for i, role in enumerate(ROLES):
            actor = draw(game, model, k, role)
            panel = Image.new("RGB", (38, 32), "#b4a694")
            panel.paste(actor, ((38 - actor.width) // 2, 32 - actor.height + 2), actor)
            x = 4 + (i % 4) * 118
            y = 23 + (i // 4) * 127
            gallery.paste(panel.resize((114, 96), Image.Resampling.NEAREST), (x, y))
            pen.text((x + 57, y + 99), role, anchor="ma", fill="#f1e6d4", font=font)
        frames.append(gallery)
    return frames


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("game_dir")
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    game = outfits.Game(args.game_dir)
    for model, gender in ((2053, "female"), (2055, "male")):
        frames = gallery(game, model, "Dwarf " + gender)
        frames[0].save(
            args.output_dir / f"dwarf-{gender}.gif",
            save_all=True,
            append_images=frames[1:],
            duration=[
                950 if k in (0, 1, 2, 24, 25, 26, 27, 28) else 300 for k in range(len(NAMES))
            ],
            loop=0,
            disposal=1,
        )


if __name__ == "__main__":
    main()
