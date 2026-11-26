"""Encode the fitted race study poses and their native equipment surfaces."""
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

from wornreview import sprites


def make_layers(source, outfit, left, top, regions, cloak, head, belt, cape=None):
    """Convert native coordinates into matching study canvases, preserving clear edits."""
    height, width = len(outfit), len(outfit[0])
    if height != len(source) + top or width != len(source[0]) + 2 * left:
        raise ValueError("Outfit and source registration disagree")
    layers = {name: [[None]*width for _ in range(height)]
              for name in ("image", "regions", "cloak", "head", "belt")}
    for y, row in enumerate(outfit):
        for x, color in enumerate(row):
            sx, sy = x-left, y-top
            raw = source[sy][sx] if 0 <= sy < len(source) and 0 <= sx < len(source[0]) else None
            if raw != color:
                layers["image"][y][x] = 255 if color is None else color
    for bit, points in regions.items():
        for x, y in points:
            u, v = x+left, y+top
            assert 0 <= u < width and 0 <= v < height and outfit[v][u] is not None, (x, y, bit)
            layers["regions"][v][u] = bit | (layers["regions"][v][u] or 0)
    for x, y in head:
        assert 0 <= x+left < width and 0 <= y+top < height
        layers["head"][y+top][x+left] = 1
    for x, y in belt:
        assert 0 <= x+left < width and 0 <= y+top < height and outfit[y+top][x+left] is not None
        layers["belt"][y+top][x+left] = 1
    for (x, y), rank in cloak.items():
        assert 0 <= x+left < width and 0 <= y+top < height and 0 <= rank <= 5
        layers["cloak"][y+top][x+left] = rank+1
    if cape is not None:
        layers["cape"] = [[None]*width for _ in range(height)]
        for (x, y), colour in cape.items():
            assert 0 <= x+left < width and 0 <= y+top < height and colour not in (None, 255)
            layers["cape"][y+top][x+left] = colour
    return layers


def write_archive(path, models, pose_layers):
    """Write one deterministic archive of pose chunks from the study figures."""
    path = Path(path)
    with TemporaryDirectory(dir=path.parent) as staging:
        temporary = Path(staging)/path.name
        with ZipFile(temporary, "w") as archive:
            for model in models:
                for start, stop, tag in ((0, 15, "walk"), (15, 29, "combat")):
                    poses = [pose_layers(model, pose) for pose in range(start, stop)]
                    for role in sorted(poses[0]):
                        for name in poses[0][role]:
                            chunks = [pose[role][name] for pose in poses]
                            suffix = "" if name == "image" else "-" + name
                            entry = ZipInfo(f"{model}/{role}/{tag}{suffix}")
                            archive.writestr(entry, sprites.encode_frames(chunks), compress_type=ZIP_DEFLATED)
        temporary.replace(path)
