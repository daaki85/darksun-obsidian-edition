"""Wake of the Ravager's figures redrawn in Shattered Lands' style (Codex's approved catalogue, the owner's
choice to ship it, 2026-11-27): the people, the party's figures, the creatures, the still figures in the
scenes, the Tarrasque and the three drakes, put into the Loader's copies of the sequel's files.

DATA (ravager-figures.zip, beside this module) holds every chunk the catalogue's import changes, by file:
OBJEX.GFF's pictures (BMP), combat pictures (CBMP) and scripts (SCMD); RESOURCE.GFF's Tarrasque, its
cinematic, the drakes and the Elderbrain tank; RGN03A.GFF's dining-room table (ETAB 58: the Mines3 dining room's furniture,
placed again for its smaller pictures). manifest.json names them, and the 32 objects (OJFF) moved to another
picture (the greater elementals' own, and the people given a figure of their own) as "object, the game's
picture, the new one". The empty temple throne takes the drawing offset for its lowered bowl.
The rest of each file is the player's own, as the game ships it.

  * object_chunks(CHUNKS): the chunks for the Loader's OBJEX2.GFF (ravager.objects_fixed, unless SKIP is
    in its SKIP), an object moved only from the picture the game gives it;
  * resource_chunks(CHUNKS): RESOURC2.GFF's (ravager.resources_fixed);
  * region_chunks(NAME, CHUNKS): a region file's (REGIONS: ravager.write_regions writes their copies, which
    DSCLOG2 opens in their place: RGN03A.GFF is D:\\RGN03A2.GFF).

`python -m dsloader.ravfigures pack IMPORTED STOCK [SOURCE]` makes DATA from the catalogue's import
(darksun-recompiled's tools/proto/import_catalogue.py, run on the stock files: IMPORTED its OUT_DIR, STOCK
the game's folder). It also lowers reviewed furnishings from the stock file.
One correction to the catalogue's chunks: Notaku's combat drawings (CBMP 2409, Shattered
Lands' picture 385, whose background is colour 0 there) have their background, the colour round each drawing's
edge, made clear (CLEAR_EDGE): in the sequel it was drawn, a box round him as he fought."""
import collections
import io
import json
import os
import struct
import zipfile
from typing import Dict, List, Optional, Tuple

from . import gff

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ravager-figures.zip")
SKIP = "figures"  # (ravager's SKIP name: the copies without them, RAV_SKIP's control)
MANIFEST = "manifest.json"
FILES = ("OBJEX.GFF", "RESOURCE.GFF", "RGN03A.GFF")  # Files with imported catalogue chunks.
REGIONS = {"RGN001.GFF": "RGN0012.GFF", "RGN033.GFF": "RGN0332.GFF", "RGN03A.GFF": "RGN03A2.GFF"}
PICTURE = 12  # (OJFF: the object's picture's number, a word)
KINDS = ("BMP ", "CBMP", "SCMD", "ETAB")  # (the chunks DATA may hold)
CLEAR_EDGE = (("CBMP", 2409),)  # (pack: a drawing's background made clear, see above)

# Stock shelves reviewed at every placement (reports/ravager-furniture/README.md).
SHELVES = (1137, 1140, 1170, 1171, 1172, 1334, 2628, 2629, 2631, 2674,
           2675, 2676, 2979, 2980, 2981, 2982, 3356, 3414, 3416)

# Keep the rims on the tiny bowls and jar, and both barrel lids above the Tyr wall.
SHALLOW_STORAGE = (3172, 3173, 3174, 3558)
DAMAGED_CRATES = (3795, 3796, 3797, 3798)
# The foreground wall also hides the front row of broken crates at full Tyr scale.
FURNITURE_SCALES = dict.fromkeys(SHALLOW_STORAGE + DAMAGED_CRATES, 0.82)
STORAGE = (532, 533, 1014, 1015, 1016, 2220, 2221, 2222, 2223, 2225, 2354, 2356,
           2769, 2770, 3364) + SHALLOW_STORAGE
TABLES = (515, 517, 628, 629, 630, 1342, 2050, 2585, 2589, 2624, 2625, 2626, 2627,
          2630, 2703, 2793, 3247, 3248, 3249, 3503, 3504, 3505, 3525, 3695, 3698, 3824, 3825, 3828, 3830, 3871)
SEATING_AND_BEDS = (522, 523, 541, 543, 544, 545, 546, 626, 627, 632, 633, 634, 635, 789, 2218,
                    2590, 2591, 2704, 2789, 2790, 2824, 2840, 3078, 3246, 3276, 3442, 3443, 3627, 3628,
                    3629, 3699, 3793, 3826, 3829, 3835, 3836, 3870)
OPENABLE = (631, 1112, 2825, 3250)  # Two stored states, each with its original SCMD.
FURNITURE = SHELVES + STORAGE + TABLES + SEATING_AND_BEDS + OPENABLE

# Only these bottom rows take the Tyr scale. Keep cushion faces, brazier smoke and the tips of the polearms intact.
BASE_ROWS = {2166: 16, 2167: 16, 2697: 9, 2698: 9, 2699: 9, 2732: 22, 2733: 22, 2796: 43}

# Each assembly uses the same floor line for the pictures and their attached pieces.
# The four placement fields are stock object, x, y and the new y. Other placements
# of the same object (especially vase 9606) keep their own coordinates.
ASSEMBLIES = (
    ("RGN001.GFF", tuple(range(567, 582)), (
        (9026, 1897, 121, 131), (9022, 1234, 177, 189), (9026, 1166, 133, 143),
        (9046, 1706, 132, 142), (9027, 1723, 148, 153), (9026, 1245, 90, 100),
        (9038, 1225, 118, 119), (9038, 1265, 118, 119), (9044, 537, 180, 187),
        (9044, 536, 195, 197), (9038, 587, 196, 197), (9026, 646, 168, 179),
        (9038, 623, 194, 196), (9038, 674, 195, 196),
    )),
    ("RGN033.GFF", (532, 533, 455), (
        (9508, 677, 1269, 1276), (9646, 566, 1289, 1296),
        (9646, 551, 1303, 1305), (9642, 552, 1278, 1289),
    )),
    ("RGN033.GFF", (2224, 2226), (
        (9645, 606, 1281, 1291), (9606, 599, 1261, 1278),
    )),
    ("RGN033.GFF", (3072,), ((9586, 1761, 1124, 1135),)),
    ("RGN033.GFF", (3792,), ((9586, 1727, 783, 794),)),
    ("RGN033.GFF", DAMAGED_CRATES, (
        (9491, 1683, 244, 248), (9494, 1686, 261, 263),
        (9495, 1629, 1284, 1294), (9491, 1639, 1313, 1317), (9637, 1625, 1254, 1269),
    )),
    ("RGN03A.GFF", (2785, 2786), ((10347, 223, 737, 747),)),
    (None, (2794, 2795), ()),  # Weapons cross the join in both the Yuan-ti tunnels and Mines 3.
)


class FigureError(Exception):
    pass


def _name(kind: str, number: int) -> str:
    return f"{kind.replace(' ', '_')}-{number}"


def _key(name: str) -> Tuple[str, int]:
    kind, number = name.rsplit("-", 1)
    return kind.replace("_", " ").ljust(4), int(number)


_loaded: Optional[dict] = None


def load(path: str = DATA) -> dict:
    """{"files": {FILE: {key: chunk}}, "added": {FILE: keys the game's file lacks}, "objects": [(object, old
    picture, new picture)], "source": str, "placements": {region: [[object, x, y, new_y], ...]}}."""
    global _loaded
    if _loaded is not None and path == DATA:
        return _loaded
    try:
        with zipfile.ZipFile(path) as z:
            man = json.loads(z.read(MANIFEST))
            files = {f: {_key(n): z.read(f"{f}/{n}") for n in names} for f, names in man["files"].items()}
    except (OSError, KeyError, ValueError, zipfile.BadZipFile) as e:
        raise FigureError(f"{os.path.basename(path)}: {e}")
    added = {f: {_key(n) for n in names} for f, names in man.get("added", {}).items()}
    out = {"files": files, "added": added, "objects": [tuple(o) for o in man["objects"]], "source": man.get("source", ""),
           "placements": man.get("placements", {})}
    if path == DATA:
        _loaded = out
    return out


def _for(name: str, chunks: gff.Chunks, data: dict) -> gff.Chunks:
    """DATA's chunks for the file NAME, none unless CHUNKS (the game's file) has every one DATA replaces:
    another release's, or a file not the game's, is left as it is."""
    got = data["files"].get(name, {})
    added = data["added"].get(name, set())
    if any(k not in chunks for k in got if k not in added):
        return {}
    return dict(got)


def object_chunks(chunks: gff.Chunks, data: Optional[dict] = None) -> gff.Chunks:
    """The chunks DATA gives OBJEX.GFF's copy: its pictures, and each moved object's record (from CHUNKS,
    the copy's so far) pointing at its new picture, if the game gives it the old one (else left); none
    for a file without the pictures DATA replaces (_for)."""
    data = data or load()
    out = _for("OBJEX.GFF", chunks, data)
    if not out:
        return {}
    for obj, old, new in data["objects"]:
        rec = chunks.get(("OJFF", obj))
        if rec is None or len(rec) < PICTURE + 2:
            continue
        cur, = struct.unpack_from("<H", rec, PICTURE)
        if cur == old:
            rec = bytearray(rec)
            struct.pack_into("<H", rec, PICTURE, new)
            out[("OJFF", obj)] = bytes(rec)
    # GPL 256 replaces seated Tantris with the empty throne from Limbo at the tile centre.
    # His floor point is eight pixels northwest of that centre. His frame anchor is (29, 50).
    throne = ("OJFF", 3530)
    record = chunks.get(throne, b"")
    picture = ("BMP ", 789)
    if (len(record) >= PICTURE + 2 and struct.unpack_from("<H", record, PICTURE)[0] == 789
            and struct.unpack_from("<hh", record, 2) == (0, 0)
            and picture in chunks and picture in out
            and ("SCMD", 789) not in chunks and ("SCMD", 789) not in out
            and out[picture] == lowered_furniture(chunks[picture])):
        rec = bytearray(record)
        struct.pack_into("<hh", rec, 2, 37, 58)
        out[throne] = bytes(rec)
    return out


def resource_chunks(chunks: gff.Chunks, data: Optional[dict] = None) -> gff.Chunks:
    """The chunks DATA gives RESOURCE.GFF's copy (the Tarrasque, its cinematic, the drakes and the Elderbrain encounter): _for's."""
    return _for("RESOURCE.GFF", chunks, data or load())


def region_chunks(name: str, chunks: gff.Chunks, data: Optional[dict] = None) -> gff.Chunks:
    """Merge placement edits with the catalogue scene, or the player's ETAB where it supplies none."""
    name = name.upper()
    data = data or load()
    out = _for(name, chunks, data)
    moves = data.get("placements", {}).get(name)
    if not moves:
        return out
    key = ("ETAB", int(name[3:6], 16))
    original = out.get(key, chunks.get(key))
    if original is None or len(original) % 8:
        return out
    targets = {(obj, x, y): new_y for obj, x, y, new_y in moves}
    table = bytearray(original)
    for index, (x, y, height, flags, obj) in enumerate(struct.iter_unpack("<HHBBh", original)):
        new_y = targets.get((obj, x, y))
        if new_y is not None and height == 0:
            struct.pack_into("<H", table, index * 8 + 2, new_y)
    if table != original:
        out[key] = bytes(table)
    return out


# --- making DATA (not at play: from the catalogue's import) ---

def _frames(chunk: bytes) -> List[bytes]:
    n, = struct.unpack_from("<H", chunk, 4)
    offs = list(struct.unpack_from(f"<{n}I", chunk, 6)) + [len(chunk)]
    return [chunk[offs[i]:offs[i + 1]] for i in range(n)]


def cleared_edges(chunk: bytes) -> bytes:
    """CHUNK (a picture, run-length frames) with each frame's background clear: the colour of most of its
    edge's pixels, wherever it reaches from the edge."""
    from . import art, sprites
    frames = []
    for i in range(struct.unpack_from("<H", chunk, 4)[0]):
        w, h, rows = art.decode_frame(chunk, i)
        edge = [rows[y][x] for x in range(w) for y in (0, h - 1)] + [rows[y][x] for y in range(h) for x in (0, w - 1)]
        bg, n = collections.Counter(edge).most_common(1)[0]
        if bg is not None and n * 2 > len(edge):
            todo = [(x, y) for x in range(w) for y in (0, h - 1)] + [(x, y) for y in range(h) for x in (0, w - 1)]
            while todo:
                x, y = todo.pop()
                if 0 <= x < w and 0 <= y < h and rows[y][x] == bg:
                    rows[y][x] = None
                    todo += [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
        frames.append(rows)
    return sprites.encode_frames(frames)


def lowered_furniture(chunk: bytes, base_rows: Optional[int] = None, scale: float = 0.66) -> bytes:
    """Scale the base toward its floor line. Any artwork above BASE_ROWS moves down intact."""
    from . import sequelicons, sprites
    frames = []
    for index in range(struct.unpack_from("<H", chunk, 4)[0]):
        rows = sequelicons.decode(chunk, index)
        height = len(rows)
        clear = [None] * len(rows[0])
        depth = height if base_rows is None else min(base_rows, height)
        base = []
        for distance in range(depth):
            offset = int(distance / scale + 0.5)
            if offset >= depth:
                break
            base.append(rows[height - 1 - offset])
        frames.append([clear] * (depth - len(base)) + rows[:height - depth] + base[::-1])
    return sprites.encode_frames(frames)


def _lower_split_bed(old: gff.Chunks, new: gff.Chunks) -> None:
    """Resample the assembled bed, then split it back across the two stock drawing areas."""
    from . import sequelicons, sprites
    head, foot = ("BMP ", 524), ("BMP ", 525)
    for key in (head, foot):
        if key not in old or key not in new or ("SCMD", key[1]) in new:
            return
        if struct.unpack_from("<H", old[key], 4)[0] != 1:
            return
        if new[key] not in (old[key], lowered_furniture(old[key])):
            return  # Preserve a different catalogue redraw.
    top = sequelicons.decode(old[head])
    bottom = sequelicons.decode(old[foot])
    # At all four placements the foot starts 39 rows below the head, overlapping seven rows.
    if (len(top), len(bottom), len(top[0]), len(bottom[0])) != (46, 29, 40, 40):
        return
    overlap = 7
    shared = [[front if front is not None else back for back, front in zip(upper, lower)]
              for upper, lower in zip(top[-overlap:], bottom[:overlap])]
    joined = top[:-overlap] + shared + bottom[overlap:]
    scaled = sequelicons.decode(lowered_furniture(sprites.encode_frames([joined])))
    new[head] = sprites.encode_frames([scaled[:len(top)]])
    clear = [None] * len(bottom[0])
    new[foot] = sprites.encode_frames([[clear] * overlap + scaled[len(top):]])


def pack(imported: str, stock: str, dest: str = DATA, source: str = "") -> dict:
    """DATA from the catalogue's import (IMPORTED: its OUT_DIR) against the game's own files (STOCK): every
    chunk of KINDS that differs, and the objects moved. Returns the counts."""
    files: Dict[str, Dict[str, bytes]] = {}
    added: Dict[str, List[str]] = {}
    objects = []
    placements = {}
    for f in FILES:
        try:
            with open(os.path.join(imported, f), "rb") as h:
                new = gff.read_gff(h.read())
        except OSError:
            continue
        with open(os.path.join(stock, f), "rb") as h:
            old = gff.read_gff(h.read())
        gone = [k for k in old if k not in new and k[0] in KINDS]
        if gone:
            raise FigureError(f"{f}: the import took out {gone[:5]}")
        if f == "OBJEX.GFF":
            _lower_split_bed(old, new)
            for number in (*FURNITURE, *BASE_ROWS):
                key = ("BMP ", number)
                # A later catalogue replacement owns its art and all its poses.
                script = ("SCMD", number)
                if key not in old or new.get(key) != old[key] or new.get(script) != old.get(script):
                    continue
                if script not in old or number in OPENABLE:
                    scale = FURNITURE_SCALES.get(number, 0.66)
                    new[key] = lowered_furniture(old[key], BASE_ROWS.get(number), scale)
            # Package positions only when every piece still uses this group's artwork.
            for region, pictures, moves in ASSEMBLIES:
                keys = [("BMP ", pic) for pic in pictures]
                if any(k not in old or k not in new or ("SCMD", k[1]) in new for k in keys):
                    continue
                lowered = {k: lowered_furniture(old[k], scale=FURNITURE_SCALES.get(k[1], 0.66)) for k in keys}
                if all(new[k] in (old[k], lowered[k]) for k in keys):
                    new.update(lowered)
                    if moves:
                        placements.setdefault(region, []).extend(moves)
        for k, v in sorted(new.items()):
            if old.get(k) == v:
                continue
            if k[0] == "OJFF":
                was = old.get(k)
                if was is None or was[:PICTURE] + was[PICTURE + 2:] != v[:PICTURE] + v[PICTURE + 2:]:
                    raise FigureError(f"{f}: object {k[1]} changed past its picture")
                objects.append((k[1], struct.unpack_from("<H", was, PICTURE)[0], struct.unpack_from("<H", v, PICTURE)[0]))
            elif k[0] in KINDS:
                files.setdefault(f, {})[_name(*k)] = cleared_edges(v) if k in CLEAR_EDGE else v
                if k not in old:
                    added.setdefault(f, []).append(_name(*k))
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        man = {"source": source, "files": {f: sorted(c) for f, c in files.items()}, "added": added, "objects": objects,
               "placements": placements}
        z.writestr(MANIFEST, json.dumps(man, indent=1))
        for f, c in files.items():
            for n in sorted(c):
                z.writestr(f"{f}/{n}", c[n])
    with open(dest, "wb") as h:
        h.write(buf.getvalue())
    return {f: len(c) for f, c in files.items()} | {"objects": len(objects)}


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 4 or sys.argv[1] != "pack":
        sys.exit("usage: python -m dsloader.ravfigures pack IMPORTED_DIR STOCK_DIR [SOURCE]")
    print(pack(sys.argv[2], sys.argv[3], DATA, sys.argv[4] if len(sys.argv) > 4 else ""))
