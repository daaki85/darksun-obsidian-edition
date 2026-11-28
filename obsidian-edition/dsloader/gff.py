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
import tempfile
import time
from typing import Dict, List, Optional, Tuple

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


class CopyIndex:
    """A copy of a game file the Loader writes chunks into in place while the game runs (the class outfits'
    pictures: sprites.Dresser in SEGOBJEX's copy, ravdress.RavDresser in OBJEX2.GFF): for each chunk of KINDS,
    keyed (kind, id), its place (index_places: where its length is said, offset, length) and its room (rooms),
    read again whenever the file has changed since it was last read or written here."""

    def __init__(self, path: str, kinds=("BMP ",)):
        self.path, self.kinds = path, tuple(kinds)
        self.places: Dict[Tuple[str, int], Tuple[int, int, int]] = {}
        self.rooms: Dict[Tuple[str, int], int] = {}
        self._stamp: Optional[Tuple[int, int]] = None  # (the file as last read or written here)

    def _now(self) -> Tuple[int, int]:
        st = os.stat(self.path)
        return st.st_mtime_ns, st.st_size

    def refresh(self) -> Tuple[bool, Optional[bytes]]:
        """(whether there is a copy to write in, the file's bytes if it was read again: then what any chunk
        in it shows is what the Loader wrote it as, not what was written here)."""
        try:
            stamp = self._now()
        except OSError:
            return False, None
        if stamp == self._stamp:
            return True, None
        try:
            with open(self.path, "rb") as f:
                data = f.read()
            places, rooms_ = {}, {}
            for kind in self.kinds:
                places.update({(kind, n): p for n, p in index_places(data, kind).items()})
                rooms_.update({(kind, n): r for n, r in rooms(data, kind).items()})
        except (OSError, GffError, struct.error):
            return False, None
        self.places, self.rooms, self._stamp = places, rooms_, stamp
        return True, data

    def forget(self) -> None:
        """The file read again at the next refresh (what was read of it made no sense to the caller)."""
        self._stamp = None

    def write(self, chunks: Dict[Tuple[str, int], bytes]) -> bool:
        """CHUNKS ({(kind, id): bytes}) each where its old one is, its length in the file's index; False
        (nothing written) if one has no place, or no room there (ROOMS: the room the copy itself has, whatever
        the caller reckons)."""
        if any(key not in self.places or len(chunk) > self.rooms.get(key, 0) for key, chunk in chunks.items()):
            return False
        try:
            with open(self.path, "r+b") as f:
                for key, chunk in chunks.items():
                    entry, offset, _ = self.places[key]
                    f.seek(offset)
                    f.write(chunk)
                    f.seek(entry + 4)
                    f.write(struct.pack("<I", len(chunk)))
                    self.places[key] = (entry, offset, len(chunk))
            self._stamp = self._now()
        except OSError:
            return False  # (tried again at the next update)
        return True

    def holds(self, chunks: Dict[Tuple[str, int], bytes]) -> bool:
        """Whether the copy already holds each of CHUNKS as it is (and there are some)."""
        try:
            with open(self.path, "rb") as f:
                for key, chunk in chunks.items():
                    place = self.places.get(key)
                    if place is None or place[2] != len(chunk):
                        return False
                    f.seek(place[1])
                    if f.read(len(chunk)) != chunk:
                        return False
        except OSError:
            return False
        return bool(chunks)


REPLACE_TRIES, REPLACE_WAIT = 5, 0.05
COPY_MODE = 0o644  # (a copy of the game's files: as open() makes one with the usual umask)


def replace_retried(tmp: str, dest: str) -> None:
    """TMP put in DEST's place, again after a moment (5 tries, 50 ms apart, as
    launch.save_settings) when Windows refuses it: a virus scan holding the last DSUNLOG.EXE for a
    moment had the game start without the dice log."""
    for attempt in range(REPLACE_TRIES):
        try:
            os.replace(tmp, dest)
            return
        except PermissionError:
            if attempt == REPLACE_TRIES - 1:
                raise
            time.sleep(REPLACE_WAIT)


def write_atomic(dest: str, data: bytes) -> None:
    """DATA written to DEST whole or not at all: into a temporary file of this write's own beside
    it (two writers of one copy, the window and `play`, never share one), then put in its place
    (replace_retried). A write that fails (a full disk; on Windows DEST held open by the game or an
    antivirus) leaves no temporary file behind (a copy's is megabytes) and DEST as it was. Flushed
    to the disk before it is put in place, readable by all as an ordinary file is (mkstemp's own
    file is the owner's alone)."""
    fd, tmp = tempfile.mkstemp(prefix=os.path.basename(dest) + ".", suffix=".tmp",
                               dir=os.path.dirname(dest) or ".")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.chmod(tmp, COPY_MODE)
        replace_retried(tmp, dest)
    finally:
        if os.path.exists(tmp):
            try:
                os.remove(tmp)
            except OSError:
                pass
