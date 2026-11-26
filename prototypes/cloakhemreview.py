"""Check cloak dye against the registered cloth and render the profile examples.

python prototypes/cloakhemreview.py GAME_DIR OUTPUT_DIR
"""
import argparse
from pathlib import Path

from PIL import Image

from wornreview import Atlas, FIGURES, dwarf, elf, game, label, sprites
from dsloader import classoutfits as co


def outfits(obj):
    if obj < 302:
        return co.CLASSES[1:]
    return (co.DWARF_ROLES if obj < 304 else co.ELF_ROLES).values()


def audit(atlas):
    side, top = sprites.room(False)
    for obj, model in co.MODELS.items():
        count = 0
        for role in outfits(obj):
            brown = atlas.sequence(obj, False, role, "Cloak")
            green = atlas.sequence(obj, False, role, "Green cloak")
            for pose, frame in enumerate(co.frames(role, False, model)):
                observed = {(x - side, y - top) for y, row in enumerate(green[pose])
                            for x, color in enumerate(row) if color != brown[pose][y][x]}
                expected = {(x, y) for x, y, _ in frame.cloak}
                if observed != expected:
                    raise ValueError(f"Dye differs from cloth mask on {model} {role}, pose {pose}")
                count += 1
        print(f"{FIGURES[obj - 300]}: {count} idle and walk poses")


def tile(atlas, obj, role, pose, item, scale, marks=()):
    side, top = sprites.room(False)
    source = atlas.sequence(obj, False, role, item)[pose]
    image = elf.placed_tile(atlas.game, source, atlas.floor, 1, side, top, 0)
    ox = (image.width - len(source[0]) + 2 * side) // 2
    oy = image.height - 2 - len(source) + top
    for x, y in marks:
        image.putpixel((x + ox, y + oy), (255, 224, 50))
    return image.resize((image.width * scale, image.height * scale), Image.Resampling.NEAREST)


def gallery(atlas, output):
    cases = (
        (300, "Mage", 12, "Between legs"), (301, "Mage", 13, "Thigh detail"),
        (301, "Warrior", 2, "Boot overlap"), (302, "Fighter", 12, "Boot overlap"),
        (303, "Fighter", 12, "Boot overlap"), (304, "Ranger", 12, "Old lower hem"),
        (305, "Preserver", 12, "Elbow and hem"), (305, "Ranger", 14, "Single fleck"),
    )
    columns = ("Class colors", "Green cloak", "Boots", "Boots + cloak", "Inspected pixels")
    sheet = Image.new("RGB", (191 + len(columns) * 124, 34 + 110 * len(cases)), dwarf.PAPER)
    for j, title in enumerate(columns):
        label(sheet, (253 + j * 124, 7), title, 13, "ma")
    for i, (obj, role, pose, detail) in enumerate(cases):
        model = co.MODELS[obj]
        frame = co.frames(role, False, model)[pose]
        cloth = {(x, y) for x, y, _ in frame.cloak}
        if detail == "Boot overlap":
            marks = cloth.intersection(frame.regions[co.LEFT_FOOT] + frame.regions[co.RIGHT_FOOT])
        elif detail == "Between legs":
            marks = {(x, y) for x, y in cloth if (18 <= y <= 21 and 3 <= x <= 7)}
        elif detail == "Single fleck":
            marks = {(7, 16)}
        elif detail == "Thigh detail":
            # Show the non-cloak foreground garment beside the green panel.
            marks = set(frame.regions[co.LEGS]).difference(cloth)
        else:
            waist = atlas.game.fig(model).parts(False, pose).waist
            body = atlas.game.fr(model, pose)
            under = elf.render(atlas.game, model, pose, role, show_cape=False)
            base = atlas.sequence(obj, False, role, "Class colors")[pose]
            side, top = sprites.room(False)
            marks = {(x, y) for x, y in cloth if y > waist
                     and x >= next(i for i, c in enumerate(body[y]) if c is not None)
                     and base[y + top][x + side] != under[y + elf.PAD][x + elf.PAD]}
        y = 34 + i * 110
        label(sheet, (8, y + 10), FIGURES[obj - 300] + " · " + role, 13)
        label(sheet, (8, y + 32), "Side idle" if pose == 2 else f"Side step {pose - 10}", 13)
        label(sheet, (8, y + 54), detail, 12)
        for j, item in enumerate(columns):
            image = tile(atlas, obj, role, pose, "Boots + cloak" if j == 4 else item,
                         1, marks if j == 4 else ())
            image = image.crop((6, 8, 46, 44)).resize((120, 108), Image.Resampling.NEAREST)
            sheet.paste(image, (193 + 124 * j, y))
    sheet.save(output / "cloak-hem-audit.png")

    frames = []
    for pose in (11, 12, 13, 14):
        image = Image.new("RGB", (3 * 210, 2 * 158 + 32), dwarf.PAPER)
        label(image, (8, 5), f"Profile step {pose - 10}/4 · class colors and green cloak", 16)
        for i, (obj, model) in enumerate(co.MODELS.items()):
            role = "Mage" if obj < 302 else "Fighter" if obj < 304 else "Ranger"
            x, y = i % 3 * 210, i // 3 * 158 + 32
            label(image, (x + 6, y + 1), FIGURES[i] + " · " + role, 13)
            for j, item in enumerate(("Class colors", "Green cloak")):
                image.paste(tile(atlas, obj, role, pose, item, 2), (x + j * 104, y + 20))
                image.paste(tile(atlas, obj, role, pose, item, 1), (x + j * 104 + 28, y + 111))
        frames.append(image)
    frames[0].save(output / "cloak-hem-audit.gif", save_all=True, append_images=frames[1:],
                   loop=0, duration=240)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("game_dir", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    atlas = Atlas(args.game_dir)
    green = (game.ELVEN_CLOAK_TYPE, 5)
    atlas.gear.update({"Green cloak": ({"cloak": green}, ()), "Boots": ({"boots": (68, 5)}, ()),
                       "Boots + cloak": ({"boots": (68, 5), "cloak": green}, ())})
    audit(atlas)
    gallery(atlas, args.output)
