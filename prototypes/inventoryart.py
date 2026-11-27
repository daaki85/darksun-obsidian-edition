"""Fit the inventory garments to the 14 full-length poses from a Shattered Lands install.
Run with the game directory as the sole argument. Requires Pillow and NumPy at art-build time.
Only the transparent garment layers are exported to the Loader.
"""

from pathlib import Path
import sys
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "obsidian-edition"))
from dsloader import art, icons, inventoryart

# (centre, row, width) at the shoulders, belt and long hem, followed by the
# head's centre, crown and width. The two half-giants kneel and lean sideways.
FIT = (
    ((24, 16, 29), (24, 42, 20), (23, 79, 39), (25, 0, 14)),
    ((22, 18, 23), (22, 38, 16), (21, 74, 28), (22, 0, 13)),
    ((29, 16, 40), (28, 33, 28), (27, 59, 47), (28, 0, 18)),
    ((22, 17, 21), (22, 33, 17), (27, 58, 30), (22, 0, 13)),
    ((35, 17, 27), (37, 38, 22), (37, 79, 39), (34, 0, 15)),
    ((29, 17, 23), (28, 38, 17), (29, 77, 41), (30, 0, 14)),
    ((23, 16, 26), (23, 41, 20), (22, 79, 32), (23, 0, 15)),
    ((25, 17, 26), (25, 39, 20), (25, 79, 32), (25, 0, 14)),
    ((45, 22, 40), (37, 51, 28), (37, 79, 52), (47, 0, 20)),
    ((33, 22, 29), (34, 50, 23), (39, 79, 45), (34, 0, 17)),
    ((17, 14, 22), (17, 30, 16), (18, 57, 25), (17, 0, 13)),
    ((15, 13, 17), (14, 29, 14), (15, 51, 23), (14, 0, 12)),
    ((32, 18, 35), (31, 48, 23), (31, 90, 37), (32, 0, 16)),
)
# Foreground limbs and props, traced separately for poses where they cross cloth.
FRONT = {
    1: [
        [(1, 26), (4, 24), (12, 31), (17, 32), (17, 36), (12, 36), (1, 31)],
        [(40, 25), (43, 28), (34, 35), (28, 37), (27, 32), (32, 31)],
    ],
    3: [[(12, 38), (17, 33), (24, 34), (24, 39), (17, 44), (12, 45)]],
    4: [[(1, 38), (17, 41), (25, 46), (21, 46), (0, 41)]],
    5: [
        [(4, 28), (9, 30), (16, 34), (19, 32), (21, 34), (18, 39), (12, 37), (4, 32)],
        [(47, 0), (50, 0), (69, 88), (67, 88)],
    ],
    8: [[(1, 31), (6, 29), (15, 36), (24, 42), (31, 44), (33, 49), (27, 53), (20, 49), (8, 44), (1, 38)]],
    9: [[(6, 33), (10, 32), (18, 43), (24, 46), (25, 51), (20, 55), (15, 51), (7, 43)]],
    11: [[(1, 20), (4, 20), (9, 23), (18, 23), (20, 21), (23, 22), (19, 28), (8, 27), (2, 25)]],
}
# Source coordinates use a 96 x 140 cell for each front-facing garment. The
# points follow its shoulder line and belt so the pictured buckle lands at the waist.
SHOULDER = (0, 8, 7, 3, 4, 3, 4, 35)
BELT = (59, 66, 71, 75, 56, 65, 74, 81)
HEM = (0.98, 0.64, 0.44, 0.42, 0.94, 0.60, 0.78, 0.63)
WIDTH = (1.35, 1.03, 1.12, 1.08, 1.15, 0.90, 1.15, 1.12)
SAFE = [i for i in (*range(16, 80), *range(128, 218)) if i not in (19, 21, 29)]
# Warm/plum or teal cloth, with bone trim and leather fittings left in their own hues.
TEAL = [69, 70, 71, 72, 73]
PLUM = [17, 174, 58, 75, 59, 197, 198]


def fitted(figure, cls, size, atlas, accent=None):
    shoulder, waist, hem, head = FIT[figure]
    cx, top, sw = shoulder
    wx, belt, ww = waist
    hx, bottom, hw = hem
    head_x, crown, head_w = head
    i = cls - 1
    end = belt + (bottom - belt) * (0.78 if (figure, cls) == (8, 4) else HEM[i])
    # Use the same projection for attachments and for their parent outfit.
    source = np.asarray(atlas.crop((i % 4 * 96, i // 4 * 140, i % 4 * 96 + 96, i // 4 * 140 + 140)))
    yy, xx = np.indices(source.shape[:2])
    keep = np.ones(yy.shape, bool)
    if accent == "bone":
        keep = (yy < 36) & ((xx < 29) | (xx > 66))
    elif accent == "mantle":
        keep = (yy < 38) & ((xx < 36) | (xx > 57))
    elif accent == "green":
        keep = (xx < 24) | ((yy < 33) & (xx > 65))
    elif accent == "sash":
        keep = (yy > 21) & (yy < 74) & (xx < 75 - (yy - 21) * 0.62)
    elif accent == "hood":
        keep = yy < 46
    # Open the Thief's hood for the wearer's own face.
    if cls == 8:
        keep &= ~(((xx - 49) / 17) ** 2 + ((yy - 22) / 13) ** 2 < 1)
    # Remove the darkness inside the empty standing collar on the other garments.
    if cls != 8:
        keep &= ~((yy < 10) & (np.abs(xx - 48) < (11 - yy)))
    rgba = source.copy()
    if cls in (2, 7):
        red, green, blue = source[:, :, :3].astype(float).transpose(2, 0, 1)
        leaves = (green > red * 0.82) & (green > blue * 1.12)
        if cls == 2:
            leaves &= yy < 36
        # The game's neutral palette has no olive ramp. Bring the leaf edges
        # toward the same muted sage and bottle greens as the map cloaks.
        rgba[:, :, 0][leaves] = (red[leaves] * 0.67).astype("uint8")
        rgba[:, :, 1][leaves] = np.minimum(255, green[leaves] * 1.13)
        rgba[:, :, 2][leaves] = np.minimum(255, blue[leaves] * 1.32 + 9)

    rgba[~keep, 3] = 0
    # A four-times working canvas antialiases the costume before VGA quantization.
    garment = Image.fromarray(rgba)
    w, h = size
    canvas = Image.new("RGBA", (4 * w, 4 * h))
    knots_y = [top, belt, end]
    knots_src = [SHOULDER[i], BELT[i], 139]
    centres = [cx, wx, hx]
    spans = [sw * WIDTH[i], ww * (1.48 if cls != 4 else 1.36), hw]
    if cls == 4:
        spans[-1] = ww * 1.50
    if cls == 8:
        knots_y.insert(0, crown - 1)
        knots_src.insert(0, 0)
        centres.insert(0, head_x)
        spans.insert(0, head_w * 2.8)
    else:
        knots_y[0] -= 1
        knots_src[0] = 0
    for y in range(max(0, int(knots_y[0] * 4)), min(h * 4, round(end * 4) + 1)):
        level = y / 4
        sy = round(np.interp(level, knots_y, knots_src))
        span = max(1, round(4 * np.interp(level, knots_y, spans)))
        centre = np.interp(level, knots_y, centres)
        strip = garment.crop((0, sy, 96, sy + 1)).resize((span, 1), Image.Resampling.BILINEAR)
        canvas.paste(strip, (round(centre * 4 - span / 2), y))
    layer = canvas.resize(size, Image.Resampling.LANCZOS)
    draw = ImageDraw.Draw(layer)
    for polygon in FRONT.get(figure, ()):
        draw.polygon(polygon, fill=(0, 0, 0, 0))
    return layer


def indexed(layer, palette, cls, accent):
    pixels = np.asarray(layer)
    colours = pixels[:, :, :3].astype(float)
    indices = np.array(SAFE)[((colours[:, :, None, :] - palette[SAFE]) ** 2).sum(3).argmin(2)]
    r, g, b = colours.transpose(2, 0, 1)
    value = colours.mean(2)
    if cls == 6 or accent == "sash":
        cloth = (g >= r - 9) & (g >= b - 7) if cls == 6 else np.ones(r.shape, bool)
        ramp = np.array(TEAL)[np.digitize(value, [45, 85, 125, 176])]
        indices[cloth] = ramp[cloth]
    if cls == 5:
        cloth = (r > b * 0.98) & (b > g * 1.06)
        ramp = np.array(PLUM)[np.digitize(value, [28, 44, 61, 81, 107, 149])]
        indices[cloth] = ramp[cloth]
    return [
        [int(c) if a >= 124 else None for c, a in zip(row, alpha)]
        for row, alpha in zip(indices, pixels[:, :, 3])
    ]


# Marks follow the separate plates of the thorax and forelimbs. Each combination
# can carry all its markings while preserving the shell, joints, eyes and mandibles.
SHELL = {
    1: ([(20, 25), (24, 24), (28, 26), (26, 27), (24, 26), (21, 27)], (62, 63)),
    2: ([(24, 37), (26, 40), (29, 41), (28, 43), (25, 42), (22, 39)], (188, 56)),
    3: ([(37, 28), (42, 24), (47, 23), (45, 26), (42, 26), (39, 30)], (205, 62)),
    4: ([(10, 34), (14, 29), (17, 28), (16, 31), (13, 32), (11, 36)], (195, 168)),
    6: ([(23, 28), (27, 30), (30, 28), (29, 31), (27, 33), (24, 31)], (70, 72)),
    7: ([(37, 41), (42, 38), (49, 38), (47, 40), (43, 40), (40, 43)], (53, 56)),
}


def main(game_dir):
    figures = art.GameArt(game_dir)
    palette = np.asarray(figures.colours)
    atlas = Image.open(HERE / "inventory-garments.png")
    # The human plates are painted at the native scale of each inventory pose.
    # Columns follow the class IDs. Index zero leaves the retail figure visible.
    humans = Image.open(HERE / "inventory-human.png")
    dest = HERE.parent / "obsidian-edition/dsloader/inventory-garments.zip"
    with ZipFile(dest, "w") as z:
        for figure, builds in enumerate(inventoryart.BUILDS):
            w, h, src = art.decode_frame(figures.figures[art.FIGURE_FIRST + figure])
            names = sorted({p for combo in builds for p in inventoryart.pieces(figure, combo)})
            for name in names:
                if figure < 2:
                    left = (int(name[4:]) - 1) * 48
                    top = figure * 95
                    plate = humans.crop((left, top, left + w, top + h))
                    rows = [[pixel or None for pixel in row] for row in np.asarray(plate).tolist()]
                elif name.startswith("mark"):
                    pts, inks = SHELL[int(name[4:])]
                    mask = Image.new("L", (w, h))
                    draw = ImageDraw.Draw(mask)
                    draw.polygon(pts, fill=inks[0])
                    draw.line(pts[:3], fill=inks[1])
                    rows = [
                        [mask.getpixel((x, y)) or None if c is not None else None for x, c in enumerate(row)]
                        for y, row in enumerate(src)
                    ]
                else:
                    cls = (
                        int(name[4:])
                        if name.startswith("body")
                        else {"bone": 3, "mantle": 5, "green": 7, "sash": 4, "hood": 8}[name]
                    )
                    rows = indexed(fitted(figure, cls, (w, h), atlas, name), palette, cls, name)
                info = ZipInfo(f"{figure}/{name}")
                z.writestr(info, icons.encode(rows), compress_type=ZIP_DEFLATED, compresslevel=9)


if __name__ == "__main__":
    main(sys.argv[1])
