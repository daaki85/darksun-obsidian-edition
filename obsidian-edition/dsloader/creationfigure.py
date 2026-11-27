"""The creation screen's figure in the outfit of the class chosen (classoutfits.py).

At start-up the game reads one picture for each figure picked at creation, frame 0 of the walking
picture of party object 300 + the figure (in the Loader's copy of SEGOBJEX: sprites.SPRITE_BASE
on), and keeps them together in a handle of its paged memory (DS:FIGURES_HANDLE, of FIGURES_SIZE),
with the offsets of its entries in a table of dwords (DS:FIGURES_TABLE): entry n is from table[n]
to table[n + 1], the figures' entries FIRST + the figure, table[END] the last one's end. Each entry
is a picture chunk of one frame (its length, 1, the frame's offset 10). The routine that draws the
screen's figure (overlay stub 4239h:2Ah, at x 91h, y 16h) reads the figure's entry each time
(4414h:9Dh, 73034h in DSUN.EXE), so a picture written there is what it draws next.

The game draws the figure when the screen opens and after a click on a race or a portrait, not
after a click on a class. So DSCLOG (PROBE_WP_CLASS, after every click on the screen) sets FIG_DUE
when the classes or the figure have changed, waits for the Loader to clear it (FIG_HOLD, at most a
second), and draws the figure again.

Here the Loader writes the figure's entry in the class's outfit (or plain, for a class with none)
over the old one, moving the entries after it to keep them one after another (the handle has room
after the last: about 51 KB), and their offsets with them, with DOSBox held still. The figures'
entries for the others are left as they are (any written before: drawn each time the figure is
written again, so never shown out of date). The entries before the figures' (the screen's other
pictures) aren't touched.
"""

import struct
from typing import Dict, List, Optional, Tuple

from . import classoutfits, game, kitpages, sprites
from .game import GameData

FIGURES_HANDLE, FIGURES_SIZE = 0x4C2F, 0x4B000
FIGURES_TABLE, FIRST, END = 0x543D, 0x20, 0x2E
TSR_FIG_DUE = 1892  # DSCLOG's header: a figure to draw again (PROBE_WP_CLASS), cleared by the Loader
FRAME_HEAD = struct.Struct("<IHI")  # (an entry's head: its length, 1 frame, the frame at offset 10)
# a class as the creation screen numbers it (game.CREATION_CLASS_NAMES) to one of the sheet's that
# kitpages.CREATION_CLASS gives it from (classoutfits.for_sheet reads a party member's sheet)
GAME_CLASS = {creation: min(c for c, k in kitpages.CREATION_CLASS.items() if k == creation)
              for creation in set(kitpages.CREATION_CLASS.values())}


def creation_role(sheet: bytes, layers: Optional[int]) -> Optional[str]:
    """The class outfit (classoutfits' role) of the character on the creation screen, its SHEET's
    classes numbered as the screen numbers them."""
    if len(sheet) < game.SHEET_CLASSES + 3:
        return None
    own = bytearray(sheet)
    for i in range(3):
        c = own[game.SHEET_CLASSES + i]
        own[game.SHEET_CLASSES + i] = GAME_CLASS.get(c, 0) if c else 0
    return classoutfits.for_sheet(bytes(own), layers)


class Figures(sprites.Store):
    """The game's handle of the creation screen's figures, read and written where it is (DOSBox's
    XMS block, as sprites.Store): found by the head of the first figure's entry, and taken for it
    only if every figure's entry has its head there."""

    def _pages(self) -> Optional[List[int]]:
        return sprites.handle_pages(self.gd, FIGURES_HANDLE, FIGURES_SIZE)

    def table(self) -> Optional[List[int]]:
        """The entries' offsets, or None if they aren't in order inside the handle."""
        raw = self.gd.guest.read(self.gd.ds * 16 + FIGURES_TABLE, 4 * (END + 1))
        tab = list(struct.unpack("<%dI" % (END + 1), raw))
        if any(b <= a for a, b in zip(tab[FIRST:END], tab[FIRST + 1:END + 1])) or tab[END] > FIGURES_SIZE:
            return None
        return tab

    def _heads(self, tab: List[int]) -> bool:
        return all(self.read(tab[n], FRAME_HEAD.size) == FRAME_HEAD.pack(tab[n + 1] - tab[n], 1, FRAME_HEAD.size)
                   for n in range(FIRST, END))

    def locate(self, slots=()) -> bool:
        pages = self._pages()
        tab = self.table() if pages is not None else None
        if tab is None:
            self.base = None
            return False
        key = (self.gd.guest.read(self.gd.ds * 16 + FIGURES_HANDLE, 4), tuple(pages))
        self.pages = pages
        if key == self._key and self.base is not None and self._heads(tab):
            return True
        self.base, self._key = None, key
        g = self.gd.guest
        mem = g.read(sprites.HIGH_MEMORY, g.size - sprites.HIGH_MEMORY)
        head = FRAME_HEAD.pack(tab[FIRST + 1] - tab[FIRST], 1, FRAME_HEAD.size)
        at = self._offset(tab[FIRST])
        i = mem.find(head)
        while i >= 0:
            self.base = sprites.HIGH_MEMORY + i - at
            if self._heads(tab):
                return True
            i = mem.find(head, i + 1)
        self.base = None
        return False

    def put(self, figure: int, chunk: bytes) -> bool:
        """FIGURE's entry made CHUNK (a one-frame picture), the entries after it moved along. Whether
        it is there."""
        if not 0 <= figure < END - FIRST or not self.locate():
            return False
        tab = self.table()
        if tab is None:
            return False
        n = FIRST + figure
        if self.read(tab[n], tab[n + 1] - tab[n]) == chunk:
            return True
        after = [self.read(tab[k], tab[k + 1] - tab[k]) for k in range(n + 1, END)]
        data = chunk + b"".join(after)
        if tab[n] + len(data) > FIGURES_SIZE:
            return False
        new, pos = [], tab[n]
        for piece in [chunk] + after:
            pos += len(piece)
            new.append(pos)
        proc = getattr(self.gd.guest, "proc", None)
        held = _hold(proc)  # (the game drawing it while half written: never)
        try:
            self.write(tab[n], data)
            self.gd.guest.write(self.gd.ds * 16 + FIGURES_TABLE + 4 * (n + 1), struct.pack("<%dI" % len(new), *new))
        finally:
            if held:
                proc.resume()
        return True


def _hold(proc) -> bool:
    try:
        return bool(proc is not None and proc.suspend())
    except (OSError, AttributeError):
        return False


class CreationFigure:
    """Keeps the creation screen's figure in the class's outfit."""

    def __init__(self, gd: GameData):
        self.gd = gd
        self.figures = Figures(gd)
        self.shown: Optional[Tuple[int, Optional[str]]] = None  # (the figure, its role) last written
        self._built: Dict[Tuple[int, Optional[str]], bytes] = {}

    def wanted(self, pics: "sprites.Pictures") -> Optional[Tuple[int, Optional[str]]]:
        """(the figure, its class outfit) of the character being made, or None."""
        creature = game.far_pointer(self.gd.guest, self.gd.ds, game.CREATION_CREATURE_PTR)
        figure, = struct.unpack("<H", self.gd.guest.read(creature + sprites.CREATURE_FIGURE, 2))
        obj = sprites.PARTY_OBJECTS[0] + figure
        if obj not in sprites.PARTY_OBJECTS:
            return None
        model = pics.model(obj)
        if model is None:
            return None
        role = None
        if pics.supports_outfits(obj, model):
            layers = obj if obj in classoutfits.HALF_ELF_SOURCES else model
            role = creation_role(self.gd.creation_sheet(), layers)
        return figure, role

    def update(self, pics: Optional["sprites.Pictures"], tsr_hdr: Optional[int]) -> bool:
        """The figure written if the character's figure or class changed (on the creation screen,
        with PICS, the Dresser's), and DSCLOG's FIG_DUE cleared. Whether one was written."""
        written = False
        if self.gd.creating() and pics is not None:
            want = self.wanted(pics)
            if want is not None and want != self.shown:
                chunk = self._built.get(want)
                if chunk is None:
                    figure, role = want
                    obj = sprites.PARTY_OBJECTS[0] + figure
                    chunk = pics.build(obj, False, {}, (), pics.model(obj), obj, 0, role, only=0)
                    self._built[want] = chunk
                if self.figures.put(want[0], chunk):
                    self.shown = want
                    written = True
        elif not self.gd.creating():
            self.shown = None  # (written again when the screen next opens: the game may have read anew)
        if tsr_hdr is not None and self.gd.guest.read(tsr_hdr + TSR_FIG_DUE, 1) != b"\0":
            self.gd.guest.write(tsr_hdr + TSR_FIG_DUE, b"\0")
        return written
