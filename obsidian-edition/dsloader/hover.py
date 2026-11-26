"""The chance to hit over the enemy under the pointer: in a fight, on a party member's turn, while
the game's pointer rests on an enemy, what the d20 must show and the chance float over it as "Miss"
does ("12+ (45%)"), and go when the pointer leaves or the turn passes.

All the Loader's: nothing is asked of DSCLOG and nothing but a label's slot is written (labels.py:
Labels.hover, a standing label below every other, so a "Miss", a spell's name or a charge over the
same figure takes its place and it never takes theirs).

- Which enemy: the game's own answer. Every pass of the map's loop the game finds the thing under
  the pointer to light it up (DSUN.EXE 1E126h, which keeps it in DS:0BCBh, FFFFh for none; its
  finder, 25B52h, goes through the draw list from the front and takes the first figure whose
  picture has a pixel under the pointer), and a click acts on that same thing. So a figure standing
  in front of an enemy hides it from the pointer here as it does from a click. That word is the
  thing lit last for a pass after the pointer has moved on, so it is believed only when the
  pointer is inside the thing's picture on the screen (inside: the finder's own box test, from the
  map record's left, top, width and height) and when two looks running agree (Hover.update).
- Which number, one (a label is 128 pixels): the weapon a click would swing first, as
  hitchance.predict orders them. Next to the enemy the first melee weapon. Farther off the pointer
  decides, as it does for the click: the walk arrow gives the walk-up melee number, the attack
  pointer (the sword) the shot when the missile weapon reaches and its quiver isn't empty, else
  the melee number too. With the eye up nothing shows: a click there only looks.
- When: a fight on, a party member's turn, the map up with no window, menu or talk over it
  (DS:0BC9h 1), the pointer the walk arrow or the sword (DS:11B8h) and not on the combat log's
  panel (the game's finder knows nothing of the panel: it answers with the enemy behind it, and
  a click there is the panel's).
- The cost: a pass with the pointer off every enemy reads four small pieces of the game's memory;
  the prediction is worked out again only when the attacker, the enemy, the pointer's mode or
  either one's place has changed, or AGAIN seconds have passed (an effect may have come or gone).
"""

import struct
from typing import Callable, List, NamedTuple, Optional, Sequence, Tuple

from . import combatlog, game, hitchance, labels, quiver, targeting, usable

UNDER = 0xBCB  # DS: the thing the game last found under the pointer (FFFFh: none)
ON_MAP = 0xBC9  # DS: 1 with the map up and nothing over it (2: a window, a menu, a talk, a screen)
MODE = 0x11B8  # DS: the pointer's mode
WALK, LOOK, ATTACK = 1, 2, 4
NONE = 0xFFFF
# a map thing's record (DS:6694h, 32 bytes each), as the game's finder reads it (25BC7h-25C3Ah)
MAP_FLAGS, MAP_SHOWN = 0, 0x10  # its flags: 10h, drawn
MAP_LEFT, MAP_TOP = 3, 5  # its picture's left and top on the map (words)
MAP_RISE = 0x0D  # ... how far it is drawn above that (a signed byte)
MAP_PICTURE = 0x0F  # its picture's slot (FFFFh: none loaded)
MAP_WIDTH, MAP_HEIGHT = 0x12, 0x13  # its picture's size (signed bytes)
MAP_SIZES = "<bb"  # (how its finder reads them: the sequel's reads bytes unsigned, ravlog's layout)
INK = (255, 236, 170)
AGAIN = 0.5  # seconds a prediction is kept while nothing it was made from has moved
LINGER = 0.2  # seconds the label outlasts the last look that found its enemy under the pointer


class Look(NamedTuple):
    on_map: bool
    under: int  # the thing the game has under the pointer (NONE: nothing)
    mode: int
    pointer: Tuple[int, int]
    camera: Tuple[int, int]


def look(gd) -> Look:
    """What the game says of its pointer just now."""
    guest, ds = gd.guest, gd.ds * 16
    on_map, under = struct.unpack("<HH", guest.read(ds + ON_MAP, 4))
    mode, = struct.unpack("<H", guest.read(ds + MODE, 2))
    return Look(on_map == 1, under, mode, struct.unpack("<hh", guest.read(ds + usable.POINTER, 4)),
                struct.unpack("<hh", guest.read(ds + targeting.CAMERA, 4)))


def box(record: bytes, camera: Tuple[int, int]) -> Optional[Tuple[int, int, int, int]]:
    """A map thing's picture on the screen: left, top, right, bottom (inclusive), as the game's
    finder has it; None for a thing that isn't drawn."""
    if len(record) < targeting.MAP_THING_SIZE or not record[MAP_FLAGS] & MAP_SHOWN \
            or struct.unpack_from("<H", record, MAP_PICTURE)[0] == NONE:
        return None
    left, top = struct.unpack_from("<hh", record, MAP_LEFT)
    rise, = struct.unpack_from("<b", record, MAP_RISE)
    wide, = struct.unpack_from(MAP_SIZES[:2], record, MAP_WIDTH)
    high, = struct.unpack_from(MAP_SIZES[:1] + MAP_SIZES[2:], record, MAP_HEIGHT)
    left, top = left - camera[0], top - camera[1] - rise
    return left, top, left + wide, top + high


def inside(record: bytes, camera: Tuple[int, int], pointer: Tuple[int, int]) -> bool:
    """The pointer is within the thing's picture (its box: which pixels are the figure's is the
    game's to say)."""
    b = box(record, camera)
    return b is not None and b[0] <= pointer[0] <= b[2] and b[1] <= pointer[1] <= b[3]


def target(gd, seen: Look, enemies: Sequence[int]) -> Optional[int]:
    """The enemy under the pointer: the thing the game found there, if it is one of ENEMIES and the
    pointer is inside its picture (so not the one lit before the pointer moved away)."""
    if not seen.on_map or seen.mode not in (WALK, ATTACK) or seen.under not in enemies:
        return None
    record = gd.guest.read(gd.ds * 16 + targeting.MAP_THINGS + seen.under * targeting.MAP_THING_SIZE,
                           targeting.MAP_THING_SIZE)
    return seen.under if inside(record, seen.camera, seen.pointer) else None


def on_panel(guest, tsr_hdr: int, pointer: Tuple[int, int]) -> bool:
    """The pointer is on the combat log's panel (DSCLOG's, bottom right while it is shown)."""
    if not struct.unpack("<H", guest.read(tsr_hdr + combatlog.TSR_PANEL_ON, 2))[0]:
        return False
    top, high = struct.unpack("<HH", guest.read(tsr_hdr + combatlog.TSR_PANEL_TOP, 4))
    return combatlog.PANEL_X0 <= pointer[0] < combatlog.PANEL_X0 + combatlog.PANEL_W and top <= pointer[1] < top + high


def swing(swings: List["hitchance.Swing"], mode: int, loaded: bool) -> Optional["hitchance.Swing"]:
    """The one of SWINGS (hitchance.predict's, in the game's order) a click would make first with
    the pointer in MODE: the shot with the attack pointer when there is one (the enemy out of
    melee reach, the missile weapon reaching it) and LOADED (ammunition in the quiver), else the
    first melee weapon's."""
    if mode == ATTACK and loaded:
        shot = next((s for s in swings if s.missile), None)
        if shot is not None:
            return shot
    return next((s for s in swings if not s.missile), None)


class Hover:
    def __init__(self):
        self.thing: Optional[int] = None  # the enemy the label is over
        self._last: Optional[int] = None  # the last look's enemy (two looks running must agree)
        self._seen_at = 0.0
        self._key: Optional[tuple] = None
        self._made_at = 0.0
        self._text = ""
        self.made = 0  # predictions worked out (for the tests and the cost's measure)

    def _drop(self, names: "labels.Labels", guest, tsr_hdr: Optional[int], now: float) -> None:
        if self.thing is not None:
            names.hover(guest, tsr_hdr, None, "", INK, now)
        self.thing = self._key = None

    def update(self, gd, tsr_hdr: Optional[int], on: bool, now: float, names: "labels.Labels",
               enemies: Callable[[], Sequence[int]],
               predict: Callable[[int, int], List["hitchance.Swing"]]) -> Optional[int]:
        """One pass's look: the label put over the enemy under the pointer, kept, or taken off.
        ENEMIES() the fight's enemies (rings.enemies), PREDICT(attacker, target) the swings
        (hitchance.predict with the dice log's part). Returns the enemy the label is over."""
        guest = gd.guest
        turn = gd.whose_turn() if on and tsr_hdr is not None and gd.in_combat() else None
        if turn is None or turn >= game.PARTY_SIZE:
            self._drop(names, guest, tsr_hdr, now)
            self._last = None
            return None
        seen = look(gd)
        found = target(gd, seen, enemies()) if seen.under != NONE else None
        if found is not None and on_panel(guest, tsr_hdr, seen.pointer):
            found = None
        before, self._last = self._last, found
        if found is None or found not in (before, self.thing):
            # (nothing there, or an enemy at its first look: the label that is up stays LINGER
            # seconds past its own enemy's last look, so one stale look doesn't blink it)
            if self.thing is not None and (not seen.on_map or now - self._seen_at >= LINGER):
                self._drop(names, guest, tsr_hdr, now)
            return self.thing
        key = (turn, found, seen.mode, targeting.feet(gd, turn), targeting.feet(gd, found))
        if key != self._key or not 0 <= now - self._made_at < AGAIN:
            chosen = swing(predict(turn, found), seen.mode, quiver.quiver(gd, turn) is not None)
            self._text = hitchance.over(chosen) if chosen is not None else ""
            self._key, self._made_at = key, now
            self.made += 1
        if not self._text:
            self._drop(names, guest, tsr_hdr, now)
            return None
        names.hover(guest, tsr_hdr, found, self._text, INK, now)
        self.thing, self._seen_at = found, now
        return found
