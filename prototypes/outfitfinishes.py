"""Apply the final pose-painted edits after fitting the garment and its equipment."""

from functools import lru_cache
from pathlib import Path
from zipfile import ZipFile

from dsloader import art, sprites


@lru_cache(maxsize=None)
def _chunk(entry):
    with ZipFile(Path(__file__).with_name("outfit_finishes.zip")) as archive:
        return archive.read(entry)


def apply(rows, model, role, pose, suffix=""):
    combat, frame = divmod(pose, 15)
    tag = "combat" if combat else "walk"
    edits = art.decode_frame(_chunk(f"{model}/{role}/{tag}{suffix}"), frame)[2]
    if len(edits) != len(rows) or len(edits[0]) != len(rows[0]):
        raise ValueError(f"Finish and garment registration differ for {model} {role} {pose}")
    for y, row in enumerate(edits):
        for x, color in enumerate(row):
            if color is not None:
                # Paint encodes an explicit cutout as 255. In an equipment
                # mask the same edit removes the cell from the surface.
                rows[y][x] = None if suffix and color == 255 else color


def mask_chunk(chunk, model, role, combat, suffix):
    frames = []
    for f in range(14 if combat else 15):
        rows = art.decode_frame(chunk, f)[2]
        apply(rows, model, role, f + 15 * combat, suffix)
        frames.append(rows)
    return sprites.encode_frames(frames)
