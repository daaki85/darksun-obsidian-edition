"""The party's map sprites with what each character wears (spritegear.py), in the running game.

The party are objects 300-313 (SEGOBJEX's OJFF chunks): object 300 + the figure picked at character
creation (the creature's +18h). An object's word +0Ch names its walking picture (a BMP chunk), its
combat picture the next chunk. In the Loader's copy of SEGOBJEX (icons.write_objects) each of the
14 objects gets a pair of its own, SPRITE_BASE on: the game's own pictures with room round them
(gear sticks out), each with room kept free after it in the file (not in its length).

The game loads a picture from the file when it first needs it (DSUN.EXE 25FA6h), keeping it in a
table of the pictures it has (PICTURE_TABLE: 16 bytes each, +0 the picture's number, +2 its
length), and draws a figure's whole picture each time: so a picture's length is what drawing it
costs, and the Loader's are exactly as long as they need be. When a party member's worn items
change, the Loader writes their object's two pictures, dressed, over the old in its copy of the
file, with their new lengths in the file's index (where the game reads them each time it loads
one), takes the old ones out of the game's table (their number changed to STALE: the game frees
them itself, as any it no longer draws), and empties the member's slots on the map, so the game
loads the new ones and draws them at once (in a few milliseconds, as fast as writing them into
its memory).

Two party members of the same race and sex share an object, and the game loads a picture once and
draws everyone with it. So the copy also has a spare pair for each party place (SPARES, after the
14), each with room for any model: a member whose figure an earlier member already has is drawn in
the spare pair of their place. Each thing on the map (the table at MAP_ENTRIES, one entry per
combatant) names the picture it is drawn with (+18h, the walking one; its combat one is the next)
and the slot in the game's table it is drawn from (+0Fh). The Loader names the member's spare
picture there and empties the slot, and the game loads the picture itself and draws them with it
at once. The same puts right a save from before the copy, whose party still names the game's own
pictures.
"""

import struct
from typing import Callable, Dict, List, Optional, Tuple

from . import art, figures, game, halfelf, spritegear as sg, spriteparts as sp
from .game import GameData

SPRITE_BASE = 2450  # (pairs: object 300's walking picture 2450, its combat one 2451, ...)
PARTY_OBJECTS = range(300, 314)
SPARES = range(314, 314 + game.PARTY_SIZE)  # (each party place's spare pair: 314 + the member)
# Things on the map: 32 bytes each, by combatant; +0Fh the picture-cache slot it is drawn from,
# +18h its walking picture's number
MAP_ENTRIES, MAP_ENTRY_SIZE, MAP_SLOT, MAP_PICTURE = 0x6694, 32, 0x0F, 0x18
# ... and, for the party, where on its picture it stands (+7h half the width, +8h the height, of the
# picture it was made with): ours have more room left, right and above than the game's own (room)
MAP_ANCHOR = 0x07
MAP_FLAGS, MAP_CHANGED = 0x00, 0x01  # (+0: bit 0 marks it changed, for the game to draw again)
# A thing whose slot is NO_SLOT the game gives one as it goes through them (DSUN.EXE 23232h): its
# picture loaded into the cache (the walking one, or the combat one in a fight pose), and drawn
NO_SLOT = 0xFFFF
OJFF_PICTURE = 0x0C
CREATURE_FIGURE = 0x18
PAD = 10  # (room round the game's own picture that gear is drawn in)
# ... of which a walking picture keeps WALK_SIDE on each side and WALK_TOP above: as much as
# anything worn reaches out walking (gear in a fight reaches further: a fight picture keeps it
# all). The game draws a walking figure's whole picture again at each step, so room it doesn't
# need slows walking (four figures with ten all round: a third slower)
WALK_SIDE, WALK_TOP = 6, 2
ROOM = 2  # the room in the file for a picture, of its plain size (the bulkiest outfit: 1.38)
# The game's table of the pictures it has loaded (DSUN.EXE: segment 3E60h of its image), how many
# it has (DS:1F84h, at most 300), and the number a picture is given to take it out of the table
PICTURE_TABLE_SEG, PICTURE_COUNT, PICTURE_ENTRY, PICTURES_MOST = 0x3E60, 0x1F84, 16, 300
STALE = 0xFFFE
# Seconds after a picture is loaded anew to have the view drawn again: the shadows are drawn on the
# floor before the figures, and while the game loads the new picture its figure casts none
REDRAW_AFTER = 0.3

# The slots (game.EQUIP_SLOTS) and what spritegear makes of them
HANDS = {"right hand": "right", "left hand": "left", "missile": "missile", "ammo": "ammo",
         "head": "helm", "cloak": "cloak", "foot": "boots", "waist": "belt"}
ARMOUR_SLOTS = ("chest", "arm", "legs")


def picture_ids(obj: int) -> Tuple[int, int]:
    walk = SPRITE_BASE + 2 * (obj - PARTY_OBJECTS[0])
    return walk, walk + 1


def encode_frames(frames: List[sg.Rows]) -> bytes:
    """A picture chunk of FRAMES (the game's format: art.decode_frame reads it back)."""
    from .icons import encode
    bodies = [encode(f)[10:] for f in frames]
    head = 4 + 2 + 4 * len(bodies)
    offsets, pos = [], head
    for b in bodies:
        offsets.append(pos)
        pos += len(b)
    return struct.pack("<IH", pos, len(bodies)) + b"".join(struct.pack("<I", o) for o in offsets) + b"".join(bodies)


def room(combat: bool) -> Tuple[int, int]:
    """The room a walking (or COMBAT) picture keeps round the game's own: (each side, above)."""
    return (PAD, PAD) if combat else (WALK_SIDE, WALK_TOP)


def trimmed(rows: sg.Rows, combat: bool) -> sg.Rows:
    """ROWS drawn with PAD all round, cut down to the room the picture keeps (room)."""
    side, top = room(combat)
    cut = PAD - side
    return [r[cut:len(r) - cut] for r in rows[PAD - top:]]


def capacity(frames: List[sg.Rows], combat: bool = False) -> int:
    """The room for any outfit on these frames: ROOM times the plain picture's size."""
    return int(len(encode_frames([trimmed(sg.padded(f, PAD), combat) for f in frames])) * ROOM)


class Pictures:
    """The game's own pictures each party object's are made from, and the template cloak. With
    LOOKS, elves have pointed ears and half-elves their own figures (figures.py); without, as the
    game draws them (half-elves in their own colours, halfelf.py)."""

    def __init__(self, chunks, looks: bool = True):
        self.chunks = chunks
        self.looks = looks
        self.frames: Dict[int, List[sg.Rows]] = {}
        self.made: Dict[Tuple[int, bool], Optional[Tuple[int, List[sg.Rows], List[Optional[sg.Own]]]]] = {}

    def model(self, obj: int) -> Optional[int]:
        rec = self.chunks.get(("OJFF", obj))
        return struct.unpack_from("<H", rec, OJFF_PICTURE)[0] if rec else None

    def own(self, picture: int) -> List[sg.Rows]:
        if picture not in self.frames:
            d = self.chunks[("BMP ", picture)]
            n, = struct.unpack_from("<H", d, 4)
            self.frames[picture] = [[list(r) for r in art.decode_frame(d, f)[2]] for f in range(n)]
        return self.frames[picture]

    def spare_capacity(self, combat: bool) -> int:
        """A spare picture's size: room for any model's."""
        frames = [self.own(m + combat) for m in sp.MODELS if ("BMP ", m + combat) in self.chunks]
        for figure in (halfelf.MAN, halfelf.WOMAN):  # (their own figures)
            model = self.model(figure)
            if model is not None and ("BMP ", model + combat) in self.chunks:
                frames.append(self.base(model, figure, combat)[1])
        return max(capacity(f, combat) for f in frames)

    def base(self, model: int, figure: int, combat: bool) -> Tuple[int, List[sg.Rows], List[Optional[sg.Own]]]:
        """What FIGURE's walking (or COMBAT) pictures are made from: (the model, its frames, and
        for each what the gear can't read from it, sg.Own): the game's own (MODEL's), or a
        half-elf's own figure (figures.py), where the file has the pictures it is made from."""
        key = (figure, combat)
        if key not in self.made:
            self.made[key] = None
            made = figures.HalfElfMan if figure == halfelf.MAN else figures.HalfElfWoman if figure == halfelf.WOMAN else None
            source = figures.ELF_MAN if figure == halfelf.MAN else figures.HUMAN_WOMAN
            if self.looks and made is not None and all(("BMP ", source + c) in self.chunks for c in (0, 1)) and sg._LIGHT:
                try:
                    maker = made(self.own(source), self.own(source + 1))
                    frames = maker.frames(combat)
                    owns = [figures.own(maker, f, combat, rows, source) for f, rows in enumerate(frames)]
                    self.made[key] = (source, frames, owns)
                except (ValueError, IndexError, KeyError, TypeError, ZeroDivisionError, struct.error):
                    self.made[key] = None  # (the game's own, in the half-elf's colours: halfelf.py)
        if self.made[key] is not None:
            return self.made[key]
        frames = self.own(model + combat)
        return model, frames, [None] * len(frames)

    def build(self, obj: int, combat: bool, gear: Dict[str, Tuple[int, ...]], armour: Tuple[int, ...],
              model: Optional[int] = None, figure: Optional[int] = None) -> bytes:
        """The object's walking (or COMBAT) picture in this outfit (a spare (SPARES): MODEL's, in
        FIGURE's looks: a half-elf's are their own, figures.py and halfelf.py; an elf has pointed
        ears)."""
        model = self.model(obj) if model is None else model
        figure = obj if figure is None else figure
        model, frames, owns = self.base(model, figure, combat)
        own = self.made.get((figure, combat)) is not None  # (a half-elf's own figure)
        cloaks = self.own(sg.CLOAK_MODEL + combat)
        out = []
        for f, rows in enumerate(frames):
            template = sg.cloak_template(cloaks[f], sg.CLOAK_MODEL, f, combat) if f < len(cloaks) else None
            dressed = sg.armed(rows, model, f, combat, gear, PAD, armour, template, owns[f])
            if not own:
                dressed = halfelf.over(dressed, rows, figure, PAD)
            if self.looks and model in figures.ELVES and figure not in (halfelf.MAN, halfelf.WOMAN):
                dressed = figures.ears_over(dressed, rows, model, f, combat, PAD)
            out.append(trimmed(dressed, combat))
        return encode_frames(out)

    def room(self, obj: int, combat: bool) -> int:
        """The room for the object's walking (or COMBAT) picture in the file (a spare's: any model's)."""
        if obj in SPARES:
            return self.spare_capacity(combat)
        model = self.model(obj)
        if model is None:
            return 0
        own = capacity(self.own(model + combat), combat)
        if obj in (halfelf.MAN, halfelf.WOMAN):  # (made from another's, maybe bigger)
            own = max(own, capacity(self.base(model, obj, combat)[1], combat))
        return own


def _spare_model(chunks) -> Optional[int]:
    return next((m for m in sorted(sp.MODELS) if ("BMP ", m) in chunks and ("BMP ", m + 1) in chunks), None)


def new_chunks(chunks, looks: bool = True) -> Dict[Tuple[str, int], bytes]:
    """For the Loader's copy of SEGOBJEX: each party object's own pair of pictures (as the game's,
    with room for gear), the object pointing at them; LOOKS as Pictures has it."""
    pics = Pictures(chunks, looks)
    out = {}
    for obj in PARTY_OBJECTS:
        if pics.model(obj) is None or pics.model(obj) not in sp.MODELS:
            continue
        walk, fight = picture_ids(obj)
        out[("BMP ", walk)] = pics.build(obj, False, {}, ())
        out[("BMP ", fight)] = pics.build(obj, True, {}, ())
        rec = bytearray(chunks[("OJFF", obj)])
        struct.pack_into("<H", rec, OJFF_PICTURE, walk)
        out[("OJFF", obj)] = bytes(rec)
    spare_model = _spare_model(chunks)
    if spare_model is not None:  # (no object of their own: the Loader names them on the map)
        for obj in SPARES:
            walk, fight = picture_ids(obj)
            out[("BMP ", walk)] = pics.build(obj, False, {}, (), spare_model)
            out[("BMP ", fight)] = pics.build(obj, True, {}, (), spare_model)
    return out


def new_room(chunks, new: Dict[Tuple[str, int], bytes], looks: bool = True) -> Dict[Tuple[str, int], int]:
    """The room to keep free in the file after each of the party's pictures in NEW (new_chunks):
    up to Pictures.room in all."""
    pics = Pictures(chunks, looks)
    out = {}
    for obj in tuple(PARTY_OBJECTS) + tuple(SPARES):
        for combat, picture in zip((False, True), picture_ids(obj)):
            chunk = new.get(("BMP ", picture))
            if chunk is not None:
                out[("BMP ", picture)] = max(0, pics.room(obj, combat) - len(chunk))
    return out


def _magic(item) -> bool:
    """A plus or a power."""
    return struct.unpack("b", item[game.ITEM_PLUS:game.ITEM_PLUS + 1])[0] > 0 or bool(item[game.ITEM_POWER])


def item_glow(chunks, item) -> int:
    """Which of spritegear.GLOWS a magic ITEM glows in: the one nearest its icon's colour (the
    item's picture word, negated, its object; the object's icon), else the blue."""
    from . import icons
    obj = -struct.unpack_from("<h", item, 0)[0]
    record = chunks.get(("OJFF", obj)) if chunks else None
    if not record or len(record) < icons.OJFF_ICON + 2:
        return sg.BLUE_GLOW
    picture = chunks.get(("BMP ", struct.unpack_from("<H", record, icons.OJFF_ICON)[0]))
    if not picture:
        return sg.BLUE_GLOW
    try:
        return sg.glow_for(icons.decode(picture))
    except (ValueError, IndexError, struct.error):
        return sg.BLUE_GLOW


def worn(gd: GameData, member: int, chunks=None) -> Tuple[Dict[str, Tuple[int, ...]], Tuple[int, ...]]:
    """What a party member wears, as spritegear takes it: ({place: (item type, material[, name])},
    armour), the name for one of the Loader's weapons spritegear colours as its icon, else MAGIC for
    any other with a plus or a power (its edge glints); a magic piece of armour's type with
    MAGIC_ARMOUR added (it glints too). With the objects file's CHUNKS, each glows in the colours
    nearest its icon's (item_glow: a 4th element, or GLOW_SHIFT's bits); without, the fire's."""
    from .icons import which
    gear: Dict[str, Tuple[int, ...]] = {}
    armour: List[int] = []
    for _, item, typ in gd._worn(member):
        slot = item[game.ITEM_SLOT]
        if slot >= len(game.EQUIP_SLOTS):
            continue
        name = game.EQUIP_SLOTS[slot]
        kind = struct.unpack_from("<H", item, game.ITEM_TYPE)[0]
        material = typ[0x08] & 0x0F if len(typ) == game.ITEM_TYPE_SIZE else 4
        magic = _magic(item)
        glow = item_glow(chunks, item) if magic and chunks is not None else sg.FIRE_GLOW
        if name in ARMOUR_SLOTS:
            armour.append(kind | (sg.MAGIC_ARMOUR | glow << sg.GLOW_SHIFT if magic else 0))
        elif name in HANDS:
            special = which(bytes(item))
            if special in sg.BLADE_COLOURS:
                gear[HANDS[name]] = (kind, material, special, glow)
            elif magic:
                gear[HANDS[name]] = (kind, material, sg.MAGIC, glow)  # (its edge glints: spritegear.GLOWS)
            else:
                gear[HANDS[name]] = (kind, material)
    return gear, tuple(sorted(armour))


class Dresser:
    """Keeps the party's sprites in the running game dressed in what they wear: each outfit
    written into the Loader's copy of SEGOBJEX (COPY_FILE) at its own length, and the game made to
    load it from there."""

    def __init__(self, gd: GameData, objects_file: str, palette: List[Tuple[int, int, int]],
                 copy_file: Optional[str] = None, looks: bool = True):
        from .gff import read_gff
        with open(objects_file, "rb") as f:
            self.pics = Pictures(read_gff(f.read()), looks)
        sg.set_palette(palette)
        self.gd = gd
        self.copy_file = copy_file
        self.places: Dict[int, Tuple[int, int, int]] = {}  # picture: (index entry, offset, length)
        self._stamp: Optional[Tuple[int, int]] = None  # the copy as the Loader last saw it
        self.shown: Dict[int, tuple] = {}  # object: the outfit its pictures in the copy show
        self.request_redraw: Optional[Callable[[], None]] = None  # has the view drawn again (DSCLOG)
        self._redraw_at: Optional[float] = None  # (once pictures loaded anew are in)

    @classmethod
    def for_game(cls, gd: GameData, game_dir: Optional[str], copy_file: Optional[str] = None,
                 looks: bool = True) -> Optional["Dresser"]:
        """A Dresser from the game's own files (the objects and the palette), or None; LOOKS as
        the copy was written with (Pictures)."""
        from .gff import GffError, read_gff
        objects = art._find(game_dir, "SEGOBJEX.GFF") if game_dir else None
        gpl = art._find(game_dir, "GPLDATA.GFF") if game_dir else None
        if not objects or not gpl:
            return None
        try:
            with open(gpl, "rb") as f:
                palette = art.palette_colours(read_gff(f.read())[("PAL ", art.PORTRAIT_PALETTE)])
            return cls(gd, objects, palette, copy_file, looks)
        except (OSError, GffError, KeyError, struct.error, ValueError):
            return None

    def _check_copy(self) -> bool:
        """The copy's index read (again, if the launcher has written it anew since: then what it
        shows is plain). Whether there is a copy to dress."""
        import os
        from .gff import GffError, index_places
        if not self.copy_file:
            return False
        try:
            st = os.stat(self.copy_file)
        except OSError:
            return False
        stamp = (st.st_mtime_ns, st.st_size)
        if stamp != self._stamp:
            try:
                with open(self.copy_file, "rb") as f:
                    self.places = index_places(f.read(), "BMP ")
            except (OSError, GffError):
                return False
            self._stamp = stamp
            self.shown = {}
        return True

    def _write(self, pictures: Dict[int, bytes]) -> bool:
        """PICTURES ({number: chunk}) into the copy, each where its plain one is, its length in the
        file's index. False (nothing written) if one has no place or no room there."""
        import os
        for picture, chunk in pictures.items():
            place = self.places.get(picture)
            if place is None:
                return False
        try:
            with open(self.copy_file, "r+b") as f:
                for picture, chunk in pictures.items():
                    entry, offset, length = self.places[picture]
                    f.seek(offset)
                    f.write(chunk)
                    f.seek(entry + 4)
                    f.write(struct.pack("<I", len(chunk)))
                    self.places[picture] = (entry, offset, len(chunk))
            st = os.stat(self.copy_file)
            self._stamp = (st.st_mtime_ns, st.st_size)
        except OSError:
            return False  # (tried again at the next update)
        return True

    def _unload(self, pictures) -> None:
        """PICTURES taken out of the game's table of those it has loaded: it loads them anew."""
        count, = struct.unpack("<H", self.gd.guest.read(self.gd.ds * 16 + PICTURE_COUNT, 2))
        if count > PICTURES_MOST:
            return
        base = (self.gd.load_seg + PICTURE_TABLE_SEG) * 16
        table = self.gd.guest.read(base, count * PICTURE_ENTRY)
        for k in range(count):
            number, = struct.unpack_from("<H", table, k * PICTURE_ENTRY)
            if number in pictures:
                self.gd.guest.write(base + k * PICTURE_ENTRY, struct.pack("<H", STALE))

    def objects(self) -> Dict[int, Tuple[int, int]]:
        """{object: (party member, their figure's object)}: the first member with a figure has its
        object, any other with the same figure the spare of their place."""
        out: Dict[int, Tuple[int, int]] = {}
        for member in range(game.PARTY_SIZE):
            rec = self.gd.creature(member)
            if len(rec) < game.CREATURE_SIZE or not rec[game.CREATURE_NAME]:
                continue
            obj = PARTY_OBJECTS[0] + struct.unpack_from("<H", rec, CREATURE_FIGURE)[0]
            if obj not in PARTY_OBJECTS or self.pics.model(obj) is None:
                continue
            if obj in out and SPARES[0] + member in SPARES:
                out[SPARES[0] + member] = (member, obj)
            else:
                out.setdefault(obj, (member, obj))
        return out

    def _point(self, member: int, figure: int, target: int, reload: bool = False) -> bool:
        """MEMBER's things on the map drawn with TARGET's pictures (their FIGURE's object's, or
        their place's spare) where they name another of the party's, or the game's own picture of
        the figure (a save from before the copy): the picture named, and the slot emptied, so that
        the game loads it and draws from it at once. With RELOAD, those drawn with TARGET's too
        (their pictures written anew). Whether any was."""
        wanted = picture_ids(target)
        model = self.pics.model(figure)
        others = {picture_ids(o)[0] for o in (figure,) + tuple(SPARES) if o != target}
        if model is not None:
            others.add(model)
        moved = False
        for combatant, creature in self.gd.combatants().items():
            if creature != member:
                continue
            at = self.gd.ds * 16 + MAP_ENTRIES + combatant * MAP_ENTRY_SIZE
            picture, = struct.unpack("<H", self.gd.guest.read(at + MAP_PICTURE, 2))
            if reload and picture == wanted[0]:  # (written anew: loaded again, and drawn)
                self.gd.guest.write(at + MAP_SLOT, struct.pack("<H", NO_SLOT))
                request = getattr(self, "request_redraw", None)
                if request is not None:
                    request()  # (the view drawn again: not marked, as in a fight that
                else:                      #   can set it walking again)
                    self._changed(at)
                moved = True
            elif picture in others:
                self.gd.guest.write(at + MAP_PICTURE, struct.pack("<H", wanted[0]))
                self.gd.guest.write(at + MAP_SLOT, struct.pack("<H", NO_SLOT))
                if picture == model:  # (the game's own, smaller: drawn from where ours has room)
                    x, y = struct.unpack("<bb", self.gd.guest.read(at + MAP_ANCHOR, 2))
                    side, top = room(False)
                    self.gd.guest.write(at + MAP_ANCHOR, struct.pack("<bb", min(127, x + side), min(127, y + top)))
                self._changed(at)
                moved = True
        return moved

    def _changed(self, at: int) -> None:
        """The thing on the map at AT marked changed: the game gives it its picture (where its slot
        is empty) and draws it again, then clears the mark."""
        flags = self.gd.guest.read(at + MAP_FLAGS, 1)[0]
        self.gd.guest.write(at + MAP_FLAGS, bytes([flags | MAP_CHANGED]))

    def update(self, on: bool = True, now: float = 0.0) -> List[int]:
        """Each party member's sprites in what they wear (ON; else as the game's own), where it
        has changed. The objects written."""
        redraw_at = getattr(self, "_redraw_at", None)
        if redraw_at is not None and now >= redraw_at:
            self._redraw_at = None
            if self.request_redraw is not None:
                self.request_redraw()  # (their shadows too, now their pictures are in)
        if not self._check_copy():
            return []
        changed = []
        for obj, (member, figure) in self.objects().items():
            outfit = worn(self.gd, member, self.pics.chunks) if on else ({}, ())
            model = self.pics.model(figure)
            key = (model, figure, repr(sorted(outfit[0].items())), outfit[1])
            fresh = self.shown.get(obj) != key
            if fresh:
                pictures = {}
                for combat, picture in zip((False, True), picture_ids(obj)):
                    chunk = self.pics.build(obj, combat, outfit[0], outfit[1], model, figure)
                    if len(chunk) > self.pics.room(obj, combat):  # (more than there is room for: plain)
                        chunk = self.pics.build(obj, combat, {}, (), model, figure)
                    pictures[picture] = chunk
                if not self._write(pictures):
                    continue
                self._unload(pictures)
                self.shown[obj] = key
                self._redraw_at = now + REDRAW_AFTER
            if self._point(member, figure, obj, reload=fresh) or fresh:
                changed.append(obj)
        return changed
