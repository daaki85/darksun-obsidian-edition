"""Compare the human Warrior's profile carry and cloak to a specific earlier Loader.

python prototypes/hipprofilereview.py GAME_DIR OUTPUT_DIR --previous-checkout CHECKOUT
Use a checkout of 1d82ed6 for the published comparison.
"""
import argparse
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw

from hipwalkreview import Atlas, GalleryPalette, TERRAIN, captures, previous_captures, tiles, dwarf


PROFILE = (2, 11, 12, 13, 14)
CASES = tuple((cloaked, item) for cloaked in (False, True) for item in ("empty", "sword", "pair"))
HEADINGS = ("No weapon", "Right sword", "Sword + dagger") * 2 + ("Original woman",)


def profile_tiles(source, pose):
    return [source[300, "Warrior", cloak, item][pose] for cloak, item in CASES]


def profile_view(floor, images):
    # Keep all poses and both revisions at the same game registration. Leave room
    # behind the helmet and outside the cloak where an extended fold can appear.
    left, top, right, bottom = 13, 26, 38, 54
    ground = floor.convert("RGB")
    for image in images:
        a, b, c, d = ImageChops.difference(image.convert("RGB"), ground).getbbox()
        left, top, right, bottom = min(left, a), min(top, b), max(right, c), max(bottom, d)
    return left-2, top-2, right+2, min(floor.height, bottom+2)


def board(palette, pose, before, after, original, crop):
    heads = 85
    width, height = crop[2]-crop[0], crop[3]-crop[1]
    col = max(width*4+6, 128)
    row = 37+height*4+60+5
    frame = palette.board((14+7*col, heads+2*row+4))
    drawing = ImageDraw.Draw(frame)
    palette.text(frame, (8, 6), "Human Warrior  /  Profile cloak and weapons", 18)
    palette.text(frame, (frame.width-8, 8), f"{pose:02}   {dwarf.NAMES[pose]}", 15, "ra")
    for start, n, description in ((0, 3, "Cloak slot empty"), (3, 3, "Wearing a cloak"), (6, 1, "Retail reference")):
        x = 7+start*col
        palette.text(frame, (x+n*col//2, 35), description, 14, "ma")
        drawing.line((x+3, 57, x+n*col-3, 57), fill=palette.text_ramp[2])
    for i, heading in enumerate(HEADINGS):
        palette.text(frame, (7+i*col+col//2, 63), heading, 13, "ma")
    for i, (source, label) in enumerate(((before, "Earlier fit  ·  1d82ed6"), (after, "Revised fit"))):
        y = heads+i*row
        drawing.line((8, y, frame.width-8, y), fill=palette.text_ramp[1])
        palette.text(frame, (8, y+5), label, 15)
        palette.text(frame, (frame.width-8, y+6), "4× above  ·  Game size and 6× waist detail below", 12, "ra", muted=True)
        for j, whole in enumerate((*profile_tiles(source, pose), original)):
            x = 7+j*col+col//2
            tile = whole.crop(crop)
            frame.paste(tile.resize((width*4, height*4), Image.Resampling.NEAREST), (x-width*2, y+31))
            low = y+34+height*4
            # Same waist/upper-leg window on the six loadouts and retail reference.
            detail = whole.crop((17, 39, 32, 49)).resize((90, 60), Image.Resampling.NEAREST)
            start = x-(width+4+detail.width)//2
            frame.paste(tile, (start, low+60-height))
            frame.paste(detail, (start+width+4, low))
    return frame


def pictures(game_dir, checkout):
    atlas = Atlas(game_dir)
    with Image.open(TERRAIN) as source:
        floor = source.convert("RGB").crop((47, 138, 103, 194))
    palette = GalleryPalette(atlas, floor)
    before = tiles(palette, previous_captures(game_dir, checkout, ["human"]))
    after = tiles(palette, captures(game_dir, ["human"]))
    native = {p:palette.tile(atlas.game.fr(2099, p), 0) for p in PROFILE}
    images = [im for src in (before, after) for p in PROFILE for im in profile_tiles(src, p)]
    crop = profile_view(floor, [*images, *native.values()])
    return {p:board(palette, p, before, after, native[p], crop) for p in PROFILE}


def render(game_dir, output, checkout):
    result = pictures(game_dir, checkout)
    output.mkdir(parents=True, exist_ok=True)
    result[12].convert("RGB").save(output/"hip-profile-human.png", optimize=True)
    # The second, slower walk gives each overlap time to read.
    walk = (*PROFILE, *PROFILE)
    delays = [780, 220, 220, 220, 220, 780, 520, 520, 520, 520]
    result[walk[0]].save(output/"hip-profile-human.gif", save_all=True, append_images=[result[p] for p in walk[1:]],
                         loop=0, disposal=1, duration=delays)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("game_dir", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--previous-checkout", type=Path, required=True)
    args = parser.parse_args()
    render(args.game_dir, args.output, args.previous_checkout)
