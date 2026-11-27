"""Wake of the Ravager's figures redrawn in Shattered Lands' style (Codex's approved catalogue, the owner's
choice to ship it, 2026-11-27): the people, the party's figures, the creatures, the still figures in the
scenes, the Tarrasque and the three drakes, put into the Loader's copies of the sequel's files.

DATA (ravager-figures.zip, beside this module) holds every chunk the catalogue's import changes, by file:
OBJEX.GFF's pictures (BMP), combat pictures (CBMP) and scripts (SCMD); RESOURCE.GFF's Tarrasque, its
cinematic and the drakes; RGN03A.GFF's dining-room table (ETAB 58: the Mines3 dining room's furniture,
placed again for its smaller pictures). manifest.json names them, and the 32 objects (OJFF) moved to another
picture (the greater elementals' own, and the people given a figure of their own) as "object, the game's
picture, the new one". The rest of each file is the player's own, as the game ships it.

  * object_chunks(CHUNKS): the chunks for the Loader's OBJEX2.GFF (ravager.objects_fixed, unless SKIP is
    in its SKIP), an object moved only from the picture the game gives it;
  * resource_chunks(CHUNKS): RESOURC2.GFF's (ravager.resources_fixed);
  * region_chunks(NAME, CHUNKS): a region file's (REGIONS: ravager.write_regions writes their copies, which
    DSCLOG2 opens in their place: RGN03A.GFF is D:\\RGN03A2.GFF).

`python -m dsloader.ravfigures pack IMPORTED STOCK [SOURCE]` makes DATA from the catalogue's import
(darksun-recompiled's tools/proto/import_catalogue.py, run on the stock files: IMPORTED its OUT_DIR, STOCK
the game's folder). The one change from the catalogue's chunks: Notaku's combat drawings (CBMP 2409, Shattered
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
FILES = ("OBJEX.GFF", "RESOURCE.GFF", "RGN03A.GFF")
REGIONS = {"RGN03A.GFF": "RGN03A2.GFF"}  # (a region file the figures change: its copy's name in the dos folder)
PICTURE = 12  # (OJFF: the object's picture's number, a word)
KINDS = ("BMP ", "CBMP", "SCMD", "ETAB")  # (the chunks DATA may hold)
CLEAR_EDGE = (("CBMP", 2409),)  # (pack: a drawing's background made clear, see above)


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
    picture, new picture)], "source": str}."""
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
    out = {"files": files, "added": added, "objects": [tuple(o) for o in man["objects"]], "source": man.get("source", "")}
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
    return out


def resource_chunks(chunks: gff.Chunks, data: Optional[dict] = None) -> gff.Chunks:
    """The chunks DATA gives RESOURCE.GFF's copy (the Tarrasque, its cinematic, the drakes): _for's."""
    return _for("RESOURCE.GFF", chunks, data or load())


def region_chunks(name: str, chunks: gff.Chunks, data: Optional[dict] = None) -> gff.Chunks:
    """The chunks DATA gives the region file NAME's copy: _for's."""
    return _for(name.upper(), chunks, data or load())


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


def pack(imported: str, stock: str, dest: str = DATA, source: str = "") -> dict:
    """DATA from the catalogue's import (IMPORTED: its OUT_DIR) against the game's own files (STOCK): every
    chunk of KINDS that differs, and the objects moved. Returns the counts."""
    files: Dict[str, Dict[str, bytes]] = {}
    added: Dict[str, List[str]] = {}
    objects = []
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
        man = {"source": source, "files": {f: sorted(c) for f, c in files.items()}, "added": added, "objects": objects}
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
