"""The class outfits on Wake of the Ravager's party (the owner's choice, 2026-11-27: the sequel's party drawn as
Shattered Lands' figures, dressed as there).

The party is objects 300-313 in both games (300 + the figure picked at creation; the sequel's creature keeps it
at +10h, SL's +18h). Each sequel party object names a picture (OJFF +0Ch, after ravfigures' moves): its walking
frames BMP n, its fighting frames CBMP n, its animation SCMD n. The shipped figures (ravfigures) already make
them Shattered Lands' own frames; here (`copy_chunks`, into the Loader's OBJEX2.GFF) each is the Loader's own
Shattered Lands picture of the object instead (sprites.Pictures: room round the frames for an outfit, the
elves' pointed ears, the half-elves' own figures), each colour the nearest of the sequel's that no region
changes (ravitems.stable_colours: the map is drawn in the region's palette), its script Shattered Lands' in the
sequel's form (darksun-recompiled's `tools/sl_figures.py build`: empty slots FFFFh, the flag 40h on every step
when the sequel's own script has it on all of them), with room kept after each picture for a dressed one.

In the running game (`RavDresser`) the Loader writes each party figure's two pictures in the class outfit of
the first member who has that figure (classoutfits.for_sheet, on the sequel's sheet) over the old in the copy,
their new lengths in the file's index, and has the game load them anew as Shattered Lands' Dresser does: the
picture cache's slots holding that number made STALE (FFFEh: the sequel's cache, load + 42A2h:0CA8h, 300 slots of
16 bytes, SL's layout; DS:265Dh of them) and each map thing drawn with it (DS:67BBh + 25h n, its picture's number
at +19h, its cache slot at +10h) given no slot (FFFFh), which the game fills by loading the picture again
(28BFEh: a thing with no slot is given one, 2A388h). Worn gear, a second member of the same figure, the
creation screen's figure and the small figures are not drawn yet (RAVAGER.md's list)."""

import os
import struct
from typing import Dict, List, Optional, Sequence, Tuple

from . import art, classoutfits, gff

SKIP = "class_outfits"
PARTY = range(300, 314)
PICTURE = 0x0C  # OJFF: the walking picture's number (both games)
SL_SCRIPT = 0x0E  # OJFF: Shattered Lands' SCMD number (the sequel's script is SCMD <picture>)
SLOTS, STEP = 36, 8  # SCMD: 36 words (the step each animation starts at), then 8-byte steps
WR_PARTY_FLAG = 0x40
WR_NONE = 0xFFFF
ROOM = 1.25  # (room after a picture: the largest outfit's size, as sprites' capacity, and the colours' runs)

CREATURE_FIGURE = 0x10  # (the sequel's creature: 300 + this is its object; SL's +18h)
CACHE_SEG, CACHE_OFF, CACHE_COUNT, CACHE_MOST, CACHE_ENTRY = 0x42A2, 0x0CA8, 0x265D, 300, 16
STALE = 0xFFFE
THINGS, THING_SIZE, THING_SLOT, THING_PICTURE = 0x67BB, 0x25, 0x10, 0x19
PARTY_SIZE = 4

RGB = Tuple[int, int, int]


def wr_script(script: bytes, wr_like: bytes) -> bytes:
    """Shattered Lands' SCMD SCRIPT in the sequel's form: its empty slots FFFFh (slot 0's own 0 kept), and
    the flag 40h on every step when the sequel's own script for the figure (WR_LIKE) has it on all of its."""
    slots = list(struct.unpack_from(f"<{SLOTS}H", script, 0))
    slots = [s if (k == 0 or s) else WR_NONE for k, s in enumerate(slots)]
    out = bytearray(struct.pack(f"<{SLOTS}H", *slots))
    theirs = [wr_like[SLOTS * 2 + STEP * k:SLOTS * 2 + STEP * (k + 1)] for k in range((len(wr_like) - SLOTS * 2) // STEP)]
    flag = WR_PARTY_FLAG if theirs and all(s[2] & WR_PARTY_FLAG for s in theirs) else 0
    for k in range((len(script) - SLOTS * 2) // STEP):
        step = bytearray(script[SLOTS * 2 + STEP * k:SLOTS * 2 + STEP * (k + 1)])
        step[2] |= flag
        out += step
    return bytes(out)


def _lab(rgb: RGB) -> Tuple[float, float, float]:
    """RGB (0-255) in CIE Lab (D65): distances there are as the eye sees them."""
    def lin(c):
        c /= 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (lin(v) for v in rgb)
    x = (0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.9505
    y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    z = (0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.089

    def f(t):
        return t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116
    return 116 * f(y) - 16, 500 * (f(x) - f(y)), 200 * (f(y) - f(z))


class Colours:
    """Shattered Lands' palette numbers to the nearest of the sequel's STABLE ones ((number, RGB)) in Lab, 0
    kept (nearer than weighted RGB: 10-20% less colour error over the outfits, hair and skin closer to SL's,
    2026-11-27's comparison in project files class-figures/outfit-colour-comparison/)."""

    def __init__(self, sl_palette: Sequence[RGB], stable: Sequence[Tuple[int, RGB]]):
        self.sl, self.stable = sl_palette, stable
        self._labs = [(n, _lab(c)) for n, c in stable]
        self.cache: Dict[int, int] = {}

    def __call__(self, p):
        if not p:
            return p
        if p not in self.cache:
            want = _lab(self.sl[p])
            self.cache[p] = min(self._labs, key=lambda e: sum((a - b) ** 2 for a, b in zip(e[1], want)))[0]
        return self.cache[p]


def recoloured(picture: bytes, colours: Colours) -> bytes:
    """PICTURE (every frame) with each pixel through COLOURS, in Shattered Lands' run-length frames."""
    from .sprites import encode_frames
    n, = struct.unpack_from("<H", picture, 4)
    frames = [art.decode_frame(picture, f)[2] for f in range(n)]
    return encode_frames([[[colours(p) for p in row] for row in rows] for rows in frames])


def party_pictures(objects: gff.Chunks) -> Dict[int, int]:
    """{party object: its picture in the sequel's OBJECTS (the copy's, after ravfigures' moves)}."""
    out = {}
    for obj in PARTY:
        rec = objects.get(("OJFF", obj))
        if rec and len(rec) >= PICTURE + 2:
            out[obj] = struct.unpack_from("<H", rec, PICTURE)[0]
    return out


class Sources:
    """What the sequel's party pictures are made from: Shattered Lands' objects (its SEGOBJEX: sprites.Pictures)
    and palette, and the sequel's steady colours."""

    def __init__(self, sl_objects: gff.Chunks, sl_palette: Sequence[RGB], stable: Sequence[Tuple[int, RGB]]):
        from . import spritegear, sprites
        spritegear.set_palette(list(sl_palette))  # (the half-elves' own figures and the outfits' colours read it)
        self.sl = sl_objects
        self.pics = sprites.Pictures(sl_objects)
        self.colours = Colours(sl_palette, stable)

    @classmethod
    def from_files(cls, sl_dir: Optional[str], sequel_dir: Optional[str]) -> Optional["Sources"]:
        """From Shattered Lands' folder SL_DIR and the sequel's SEQUEL_DIR (its RESOURCE.GFF and region palettes);
        None without either, or with a file it can't read."""
        from . import icons, ravager, ravitems
        if not sl_dir or not sequel_dir:
            return None

        def read(folder, name):
            path = art._find(folder, name)
            if not path:
                raise OSError(name)
            with open(path, "rb") as f:
                return gff.read_gff(f.read())
        try:
            sl_objects = read(sl_dir, icons.OBJECTS_FILE)
            palette = art.palette_colours(read(sl_dir, "GPLDATA.GFF")[("PAL ", art.PORTRAIT_PALETTE)])
            stable = ravitems.stable_colours(read(sequel_dir, ravager.RESOURCE_FILE), ravitems.region_palettes(sequel_dir))
            return cls(sl_objects, palette, stable) if stable else None
        except (OSError, KeyError, ValueError, IndexError, struct.error, gff.GffError):
            return None

    def model(self, obj: int) -> Optional[int]:
        return self.pics.model(obj)

    def role(self, obj: int, sheet: bytes) -> Optional[str]:
        """The class outfit of a character of the sequel's SHEET drawn as OBJ (classoutfits' roles)."""
        model = self.model(obj)
        if model is None or not self.pics.supports_outfits(obj, model):
            return None
        return classoutfits.for_sheet(sheet, obj if obj in classoutfits.HALF_ELF_SOURCES else model)

    def pictures(self, obj: int, role: Optional[str] = None) -> Tuple[bytes, bytes]:
        """OBJ's walking and fighting pictures in ROLE's outfit (None: plain), in the sequel's colours."""
        model = self.model(obj)
        return tuple(recoloured(self.pics.build(obj, combat, {}, (), model, obj, 0, role), self.colours)
                     for combat in (False, True))

    def room(self, obj: int, combat: bool) -> int:
        return int(self.pics.room(obj, combat) * ROOM)


def copy_chunks(objects: gff.Chunks, sources: Sources) -> Tuple[gff.Chunks, Dict[Tuple[str, int], int]]:
    """For the Loader's OBJEX2.GFF: each party picture of OBJECTS (BMP, CBMP, SCMD) made from Shattered Lands'
    object, plain, and the room to keep after each (the bytes free for a dressed one)."""
    out: gff.Chunks = {}
    room: Dict[Tuple[str, int], int] = {}
    for obj, picture in party_pictures(objects).items():
        theirs = sources.sl.get(("OJFF", obj))
        if not theirs or sources.model(obj) is None or ("BMP ", picture) in out:
            continue
        script = sources.sl.get(("SCMD", theirs[SL_SCRIPT]))
        if not script:
            continue
        walk, fight = sources.pictures(obj)
        out[("BMP ", picture)], out[("CBMP", picture)] = walk, fight
        out[("SCMD", picture)] = wr_script(script, objects.get(("SCMD", picture), b""))
        room[("BMP ", picture)] = max(0, sources.room(obj, False) - len(walk))
        room[("CBMP", picture)] = max(0, sources.room(obj, True) - len(fight))
    return out, room


class RavDresser:
    """Keeps the sequel's party figures in their class outfits in the running game: their pictures written into
    the Loader's OBJEX2.GFF (COPY_FILE), and the game made to load them from there."""

    def __init__(self, gd, sources: Sources, copy_file: str):
        self.gd, self.sources, self.copy_file = gd, sources, copy_file
        self.places: Dict[Tuple[str, int], Tuple[int, int, int]] = {}
        self.rooms: Dict[Tuple[str, int], int] = {}
        self.objects: Dict[int, int] = {}  # party object: its picture
        self._stamp: Optional[Tuple[int, int]] = None
        self.shown: Dict[int, Optional[str]] = {}  # object: the role its pictures in the copy show
        self._built: Dict[Tuple[int, Optional[str]], Tuple[bytes, bytes]] = {}

    def _check_copy(self) -> bool:
        from .gff import GffError, index_places, rooms
        try:
            st = os.stat(self.copy_file)
        except OSError:
            return False
        stamp = (st.st_mtime_ns, st.st_size)
        if stamp != self._stamp:
            try:
                with open(self.copy_file, "rb") as f:
                    data = f.read()
                self.places, self.rooms = {}, {}
                for kind in ("BMP ", "CBMP"):
                    self.places.update({(kind, n): p for n, p in index_places(data, kind).items()})
                    self.rooms.update({(kind, n): r for n, r in rooms(data, kind).items()})
                self.objects = party_pictures(gff.read_gff(data))
            except (OSError, GffError, struct.error):
                return False
            self._stamp = stamp
            self.shown = {}
        return True

    def wanted(self) -> Dict[int, Optional[str]]:
        """{party object: the class outfit it is drawn in}: the first member with each figure's."""
        out: Dict[int, Optional[str]] = {}
        for member in range(PARTY_SIZE):
            rec = self.gd.creature(member)
            if len(rec) <= CREATURE_FIGURE + 1 or not any(rec):
                continue
            obj = PARTY[0] + struct.unpack_from("<H", rec, CREATURE_FIGURE)[0]
            if obj not in PARTY or obj in out or obj not in self.objects:
                continue
            out[obj] = self.sources.role(obj, self.gd.sheet(member))
        return out

    def _write(self, chunks: Dict[Tuple[str, int], bytes]) -> bool:
        for key, chunk in chunks.items():
            if key not in self.places or len(chunk) > self.rooms.get(key, 0):
                return False
        try:
            with open(self.copy_file, "r+b") as f:
                for key, chunk in chunks.items():
                    entry, offset, _ = self.places[key]
                    f.seek(offset)
                    f.write(chunk)
                    f.seek(entry + 4)
                    f.write(struct.pack("<I", len(chunk)))
                    self.places[key] = (entry, offset, len(chunk))
            st = os.stat(self.copy_file)
            self._stamp = (st.st_mtime_ns, st.st_size)
        except OSError:
            return False
        return True

    def _reload(self, picture: int) -> None:
        """PICTURE taken out of the game's cache and every map thing drawn with it given no slot: the game
        loads it anew from the copy and draws it."""
        g, gd = self.gd.guest, self.gd
        count, = struct.unpack("<H", g.read(gd.ds * 16 + CACHE_COUNT, 2))
        base = (gd.load_seg + CACHE_SEG) * 16 + CACHE_OFF
        for k in range(min(count, CACHE_MOST)):
            number, = struct.unpack("<H", g.read(base + k * CACHE_ENTRY, 2))
            if number == picture:
                g.write(base + k * CACHE_ENTRY, struct.pack("<H", STALE))
        for n in range(PARTY_SIZE):
            at = gd.ds * 16 + THINGS + n * THING_SIZE
            if struct.unpack("<H", g.read(at + THING_PICTURE, 2))[0] == picture:
                g.write(at + THING_SLOT, struct.pack("<H", 0xFFFF))

    def writable(self) -> List[Tuple[int, int]]:
        """What update writes in the game's memory (ravlog's _writable)."""
        gd = self.gd
        return [((gd.load_seg + CACHE_SEG) * 16 + CACHE_OFF, CACHE_MOST * CACHE_ENTRY),
                (gd.ds * 16 + THINGS, PARTY_SIZE * THING_SIZE)]

    def update(self) -> List[int]:
        """Each party figure in its outfit, where it has changed. The objects written."""
        if not self._check_copy():
            return []
        changed = []
        for obj, role in self.wanted().items():
            if obj in self.shown and self.shown[obj] == role:
                continue
            picture = self.objects[obj]
            built = self._built.get((obj, role))
            if built is None:
                built = self._built[(obj, role)] = self.sources.pictures(obj, role)
            chunks = {("BMP ", picture): built[0], ("CBMP", picture): built[1]}
            if not self._write(chunks):
                continue
            self.shown[obj] = role
            self._reload(picture)
            changed.append(obj)
        return changed
