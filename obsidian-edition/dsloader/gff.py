"""Reader for SSI's GFF container format (Dark Sun resource and save files).

Layout, as seen in Shattered Lands saves:
  header:  "GFFI", version, data offset, TOC offset, TOC length, flags, ...  (u32 each)
  TOC:     u32 x2 (offsets), u16 type count, then per type:
             4-char type, u32 chunk count, then per chunk: u32 id, u32 offset, u32 length
           or, when the count has its top bit set (the game's resource files), the ids as
           ranges: u32 total, u32 id of the GFFI chunk that holds the chunks' offsets,
           u32 range count, then per range: u32 first id, u32 count. That GFFI chunk is
           u32 count, then per chunk: u32 offset, u32 length.
"""

import os
import struct
from typing import Dict, List, Tuple

Chunks = Dict[Tuple[str, int], bytes]


class GffError(Exception):
    pass


def read_gff(data: bytes) -> Chunks:
    """{(type, id): chunk bytes} for every chunk in a GFF file."""
    if data[:4] != b"GFFI":
        raise GffError("Not a GFF file (missing GFFI signature)")
    try:
        toc_offset, = struct.unpack_from("<I", data, 12)
        pos = toc_offset + 8
        type_count, = struct.unpack_from("<H", data, pos)
        pos += 2
        places = {}
        ranged = []
        for _ in range(type_count):
            ctype, count = struct.unpack_from("<4sI", data, pos)
            ctype = ctype.decode("latin1")
            pos += 8
            if count & 0x80000000:
                _, index, runs = struct.unpack_from("<III", data, pos)
                pos += 12
                ids = []
                for _ in range(runs):
                    first, n = struct.unpack_from("<II", data, pos)
                    pos += 8
                    if len(ids) + n > len(data) // 8:  # (each id's place takes 8 bytes of the file: a
                        raise GffError(f"A run of {n} {ctype!r} ids is longer than the file can index")  # corrupt count)
                    ids += range(first, first + n)
                ranged.append((ctype, index, ids))
                continue
            for _ in range(count):
                cid, offset, length = struct.unpack_from("<III", data, pos)
                pos += 12
                places[(ctype, cid)] = (offset, length)
        for ctype, index, ids in ranged:
            if ("GFFI", index) not in places:
                raise GffError(f"No index chunk for {ctype!r}")
            at = places[("GFFI", index)][0] + 4
            for i, cid in enumerate(ids):
                places[(ctype, cid)] = struct.unpack_from("<II", data, at + 8 * i)
        chunks = {}
        for (ctype, cid), (offset, length) in places.items():
            if offset + length > len(data):
                raise GffError(f"Chunk {ctype!r} {cid} runs past the end of the file")
            chunks[(ctype, cid)] = data[offset:offset + length]
    except struct.error as e:
        raise GffError(f"Truncated GFF table of contents: {e}") from e
    return chunks


def index_places(data: bytes, ctype: str) -> Dict[int, Tuple[int, int, int]]:
    """{id: (where its offset and length are in DATA, offset, length)} for the chunks of CTYPE:
    where the file's index says each one is, and where that is said (to change a chunk's length
    in place: the game reads it there each time it loads the chunk)."""
    try:
        toc_offset, = struct.unpack_from("<I", data, 12)
        pos = toc_offset + 8
        type_count, = struct.unpack_from("<H", data, pos)
        pos += 2
        listed: Dict[Tuple[str, int], int] = {}
        wanted = None
        for _ in range(type_count):
            kind, count = struct.unpack_from("<4sI", data, pos)
            kind = kind.decode("latin1")
            pos += 8
            if count & 0x80000000:
                _, index, runs = struct.unpack_from("<III", data, pos)
                pos += 12
                ids: List[int] = []
                for _ in range(runs):
                    first, n = struct.unpack_from("<II", data, pos)
                    pos += 8
                    if len(ids) + n > len(data) // 8:  # (each id's place takes 8 bytes of the file: a
                        raise GffError(f"A run of {n} {kind!r} ids is longer than the file can index")  # corrupt count)
                    ids += range(first, first + n)
                if kind == ctype:
                    wanted = (index, ids)
                continue
            for _ in range(count):
                cid, = struct.unpack_from("<I", data, pos)
                listed[(kind, cid)] = pos + 4
                pos += 12
        out: Dict[int, Tuple[int, int, int]] = {}
        if wanted is None:
            for (kind, cid), at in listed.items():
                if kind == ctype:
                    out[cid] = (at,) + struct.unpack_from("<II", data, at)
            return out
        index, ids = wanted
        if ("GFFI", index) not in listed:
            raise GffError(f"No index chunk for {ctype!r}")
        base = struct.unpack_from("<I", data, listed[("GFFI", index)])[0] + 4
        for i, cid in enumerate(ids):
            at = base + 8 * i
            out[cid] = (at,) + struct.unpack_from("<II", data, at)
        return out
    except struct.error as e:
        raise GffError(f"Truncated GFF table of contents: {e}") from e


def rooms(data: bytes, ctype: str) -> Dict[int, int]:
    """{id: the bytes from where each chunk of CTYPE starts to where the next chunk of any type
    (or the table of contents, or the file's end) does}: how much may be written there in place."""
    try:
        toc_offset, = struct.unpack_from("<I", data, 12)
        type_count, = struct.unpack_from("<H", data, toc_offset + 8)
    except struct.error as e:
        raise GffError(f"Truncated GFF table of contents: {e}") from e
    kinds, pos = [], toc_offset + 10
    for _ in range(type_count):
        try:
            kind, count = struct.unpack_from("<4sI", data, pos)
        except struct.error as e:
            raise GffError(f"Truncated GFF table of contents: {e}") from e
        kinds.append(kind.decode("latin1"))
        try:
            pos += 8 + (12 + 8 * struct.unpack_from("<I", data, pos + 16)[0] if count & 0x80000000 else 12 * count)
        except struct.error as e:  # (a ranged type's run count cut short too)
            raise GffError(f"Truncated GFF table of contents: {e}") from e
    starts = sorted({off for kind in kinds for _, off, _ in index_places(data, kind).values()}
                    | {toc_offset, len(data)})
    out: Dict[int, int] = {}
    for cid, (_, off, _) in index_places(data, ctype).items():
        after = next((s for s in starts if s > off), len(data))
        out[cid] = after - off
    return out


def write_atomic(dest: str, data: bytes) -> None:
    """DATA written to DEST whole or not at all: into DEST.tmp, then put in its place. A write
    that fails (a full disk; on Windows DEST held open by the game or an antivirus) leaves no
    .tmp behind (a copy's is megabytes) and DEST as it was."""
    tmp = dest + ".tmp"
    try:
        with open(tmp, "wb") as f:
            f.write(data)
        os.replace(tmp, dest)
    finally:
        if os.path.exists(tmp):
            try:
                os.remove(tmp)
            except OSError:
                pass
