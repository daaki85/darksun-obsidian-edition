"""Class trim and exposed skin underneath the human outfits' armor regions."""

from functools import lru_cache
from pathlib import Path
from zipfile import ZipFile

from . import art

# Colors actually used for these accents in the finished human art.
BONE = {61, 62, 63, 155, 194, 199, 206}
TEAL = {17, 40, 69, 70, 71, 72, 73}
LEAF = {53, 54, 55, 56, 57, 69, 188, 189, 225, 226, 227}


@lru_cache(maxsize=4)
def _bodies(model, combat):
    female = model == 2099
    archive = "woman_outfit_layers.zip" if female else "human_outfit_layers.zip"
    tag = "combat" if combat else "walk"
    key = f"Base/{tag}" if female else f"Study/{tag}-body"
    with ZipFile(Path(__file__).with_name(archive)) as layers:
        chunk = layers.read(key)
    return tuple(art.decode_frame(chunk, f)[2] for f in range(14 if combat else 15))


def _trim(cells, depth, *, axis):
    """Follow the painted hem (or the leading edge of a stole) as it swings."""
    sections = {}
    for x, y in cells:
        if axis == "left":
            along, across = y, x
        else:
            along, across = x, y if axis == "top" else -y
        sections.setdefault(along, []).append((across, (x, y)))
    trim = set()
    for section in sections.values():
        limit = min(across for across, _ in section) + depth
        trim.update(point for across, point in section if across < limit)
    return trim


def protected(frame, role, pose, model, head_landmark=None):
    """Native coordinates kept in their original colors beneath armor and robe dyes."""
    combat, f = divmod(pose, 15)
    body = _bodies(model, bool(combat))[f]
    left = 8 if model == 2095 and pose == 13 else 6
    body_left = left + (len(body[0]) - len(frame.image[0])) // 2
    chest, arms, legs = (set(frame.regions[b]) for b in (1, 2, 4))
    cells = chest | arms | legs
    colors = {(x, y): frame.image[y + 6][x + left] for x, y in cells}

    # Old region masks sometimes extend beyond the garment. Compare the two
    # registered edits, including transparency which inherits the retail pixel.
    # The woman's kilt intentionally shares red swatches with skin.
    keep = {(x, y) for (x, y), color in colors.items()
            if color is None or (0 <= x + body_left < len(body[0])
                                 and color == body[y + 6][x + body_left])}
    keep.update(cells.intersection(frame.head))
    if head_landmark:
        # The male archive predates head masks. His Ranger's ochre feather
        # and the Psionicist's head wrap cross the legacy chest-slot boundary.
        crown, left, right, brow, shoulder = head_landmark[:5]
        keep.update((x, y) for x, y in cells if left - 1 <= x <= right + 1
                    and crown <= y < min(brow + 2, shoulder - 1))

    if role == "Warrior":
        bone = {p for p, color in colors.items() if color in BONE}
        keep.update(bone)
        if not bone:
            # The back arm hides both bone caps during the woman's rear bow.
            keep.update(_trim(chest - keep, 1, axis="bottom"))
    elif role == "Gladiator":
        # Keep the incised leather contact edge and the two faces of the
        # steel buckle. The oiled ridge beside the seam takes the armor dye.
        keep.update(p for p in chest if colors[p] == 208)
        keep.update(p for p, color in colors.items() if color in (210, 214))
    elif role == "Priest":
        # A narrow strip of the original linen stays on the moving skirt,
        # with the same cream lights and brown shadows it has when unequipped.
        keep.update(_trim(legs - keep, 2, axis="left"))
        keep.update(_trim((chest | arms) - keep, 2, axis="top"))
    elif role == "Psionicist":
        wrap = {p for p in chest if colors[p] in TEAL}
        keep.update(_trim(wrap, 2, axis="bottom"))
    elif model == 2099 and role == "Druid":
        # The fitted bodice and the short mantle share the leaf ramp. The
        # chest mask follows the bodice beneath the mantle. Keep its green
        # neckline and bound side seam while allowing the body fabric to dye.
        bodice = chest - keep
        keep.update(_trim(bodice, 1, axis="top"))
        keep.update(_trim(bodice, 1, axis="left"))
        keep.update((x, y) for x, y, _ in frame.cloak)
    elif role in ("Druid", "Ranger"):
        # The green mantle and ochre kilt are separate materials. The shoulder
        # can fall within the chest slot on front views of the woman.
        keep.update(p for p in chest if colors[p] in LEAF)
    return frozenset(keep)
