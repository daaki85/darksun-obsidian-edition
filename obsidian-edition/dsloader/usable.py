"""Showing what can be used: while Alt is held on the map, out of a fight, a ring under every door,
container, body, item on the ground and person in view, and the names of those nearest the pointer.

All the Loader's: DSCLOG rings whatever its RING_TAB marks (rings.py, which owns the table and its
colours: a gold tint for these, the red one back for a fight's Tab ring) and floats a name over any
thing in the game's draw list (labels.py's slots, the lowest priority there). The key is the BIOS's
shift flags (0:0417h, bit 3: either Alt), read every pass.

What is marked, among the things in the game's draw list (DS:6690h; the things table 3972:0C36h
gives each one's kind and record):

- a creature outside the party, alive: a person, if a talk trigger names it; else a foe, if it
  stands on another side than the party's (not a neutral one's); else nothing;
- an item: a body (objects 1101 and 2666); a door (the two door types, unless named a wall: a
  secret door stays secret); a container (its contents a list of the game's); anything a use, look
  or use-with trigger names (a haystack, a button, the fountain); and anything that can be picked
  up (its type not scenery). Plain scenery gets nothing.

The triggers are the game's own table, as its scripts register them (the region's MAS script at
area load, others as the story goes): 13 bytes each at the far pointer DS:42CCh (the script's
place and number, the object's id at +4, a use-with's other id at +6, the next one's index at
+0Bh), in lists whose heads are words in segment 377Eh (talk 0Fh, attack 11h, look 13h, use 15h,
use with 17h), walked as the game's own routine does (DSUN.EXE 967Ah: "what can be done with this
thing", a thing's id being its record's: an item's first word, a creature's +6).
"""

import math
import struct
from typing import Dict, List, NamedTuple, Optional, Set, Tuple

from . import game, labels, targeting

KEY_FLAGS, ALT = 0x417, 0x08  # the BIOS's shift flags (0:0417h), and either Alt held
STUCK_AFTER = 30.0  # seconds Alt may read as held before it is taken for stuck (Alt+Tab away)
DRAW_LIST, DRAW_COUNT, DRAW_SIZE, DRAW_MOST = 0x6690, 0x1F72, 8, 600  # DS: the game's draw list
POINTER = 0xA133  # DS: the game's pointer, x and y on the screen
MAP_HEIGHT = 8  # a map thing's record: how far its picture reaches above its feet
MAP_OBJECT = 0x1A  # ... and its object's number
TRIGGERS_PTR, TRIGGER_SIZE, TRIGGERS_MOST = 0x42CC, 13, 512  # DS: far pointer to the triggers
TRIGGER_ID, TRIGGER_OTHER, TRIGGER_NEXT = 4, 6, 11
HEADS_SEG = 0x377E  # (less the load segment) the lists' heads
TALK, LOOK, USE, USE_WITH = 0x0F, 0x13, 0x15, 0x17
NO_TRIGGER = 0xFFFF
CREATURE_ID = 6  # a creature record's id (an item's is its first word)
ITEM_CONTENTS = 8
SCENERY = 0x20  # an item type's +08h: not to be picked up (a door, a haystack, a wall)
TYPE_FLAGS = 8
DOOR_TYPES = (0x17, 0x72)
BODIES = (1101, 2666)  # the Dead Body's objects (a thri-kreen's the second)
STATUS_DYING, STATUS_DEAD = 4, 5
SIDE_NEUTRAL = 4
# Wake of the Ravager's foes: those whose side's bit (1 << side) is in this mask (rings.HOSTILE_SIDES's, the game's
# own 0F80h); None: Shattered Lands' rule (another side than the leader's, not the neutral one). ravlog sets it.
HOSTILE_SIDES: Optional[int] = None
PERSON, FOE, DOOR, CONTAINER, BODY, ITEM, USED = "person", "foe", "door", "container", "body", "item", "use"
RING = 1  # (DSCLOG's ring kind: two pixels thick, tinted twice)
NAMED = labels.SLOTS
NAME_INK = (255, 236, 170)
FOE_INK = (255, 120, 100)
VIEW_W, VIEW_H = 320, 200
NEAR = 16  # rings go under what is in the view or this near it (a ring reaches 14 pixels from the
# feet): DSCLOG goes round every marked thing's ring at each of the game's floor passes, on the
# screen or not (10 marked cost a walking party 13% of its pace, measured), so none are marked
# that can't show; the view moved is seen at the next pass (Usable.changed)
UP_LEAST, UP_MOST, UP_OVER = 12, labels.UP, 3  # a name's bottom row above the thing's feet


class Mark(NamedTuple):
    thing: int
    kind: str
    name: str  # ("" for a thing the game has no name for)
    x: int     # its feet on the map
    y: int
    up: int    # how far above them its name goes


def alt_held(guest) -> bool:
    return bool(guest.read(KEY_FLAGS, 1)[0] & ALT)


def triggers(gd) -> Dict[int, Set[int]]:
    """{list's head offset: the ids its triggers name} for the talk, look, use and use-with lists."""
    guest = gd.guest
    table = guest.read(game.far_pointer(guest, gd.ds, TRIGGERS_PTR), TRIGGER_SIZE * TRIGGERS_MOST)
    heads = guest.read((gd.load_seg + HEADS_SEG) * 16, USE_WITH + 2)
    out = {}
    for head in (TALK, LOOK, USE, USE_WITH):
        ids, at, seen = set(), struct.unpack_from("<H", heads, head)[0], 0
        while at != NO_TRIGGER and at < TRIGGERS_MOST and seen < TRIGGERS_MOST:
            ids.add(struct.unpack_from("<h", table, at * TRIGGER_SIZE + TRIGGER_ID)[0])
            if head == USE_WITH:
                ids.add(struct.unpack_from("<h", table, at * TRIGGER_SIZE + TRIGGER_OTHER)[0])
            at, seen = struct.unpack_from("<H", table, at * TRIGGER_SIZE + TRIGGER_NEXT)[0], seen + 1
        out[head] = ids
    return out


def draw_list(gd) -> List[Tuple[int, int, int]]:
    """(thing, x, y) for each entry of the game's draw list that is one of its things."""
    guest, ds = gd.guest, gd.ds * 16
    count = min(struct.unpack("<H", guest.read(ds + DRAW_COUNT, 2))[0], DRAW_MOST)
    if not count:
        return []
    raw = guest.read(game.far_pointer(guest, gd.ds, DRAW_LIST), count * DRAW_SIZE)
    out = []
    for i in range(len(raw) // DRAW_SIZE):
        x, y, _, _, thing = struct.unpack_from("<hhBBH", raw, i * DRAW_SIZE)
        if thing < game.THINGS:
            out.append((thing, x, y))
    return out


def creature_kind(rec: bytes, index: int, leader: bytes, talk: Set[int]) -> Optional[str]:
    """PERSON, FOE or None for creature INDEX's record."""
    if index < game.PARTY_SIZE or len(rec) < game.CREATURE_SIZE or not rec[game.CREATURE_NAME]:
        return None
    if struct.unpack_from("<h", rec, 0)[0] <= 0 or rec[game.CREATURE_STATUS] in (STATUS_DYING, STATUS_DEAD):
        return None
    if struct.unpack_from("<h", rec, CREATURE_ID)[0] in talk:
        return PERSON
    side = rec[game.CREATURE_SIDE]
    if HOSTILE_SIDES is not None:
        return FOE if side < 16 and HOSTILE_SIDES >> side & 1 else None
    if len(leader) >= game.CREATURE_SIZE and side not in (leader[game.CREATURE_SIDE], SIDE_NEUTRAL):
        return FOE
    return None


def item_kind(item: bytes, typ: bytes, obj: int, name: str, found: Dict[int, Set[int]]) -> Optional[str]:
    """What an item on the map is to a click (BODY, DOOR, CONTAINER, USED, ITEM), or None: scenery."""
    if len(item) < game.ITEM_SIZE or len(typ) < game.ITEM_TYPE_SIZE:
        return None
    ident, = struct.unpack_from("<h", item, 0)
    if abs(obj) in BODIES:
        return BODY
    if struct.unpack_from("<H", item, game.ITEM_TYPE)[0] in DOOR_TYPES:
        return None if "wall" in name.lower() else DOOR
    if struct.unpack_from("<H", item, ITEM_CONTENTS)[0] < game.THINGS:
        return CONTAINER
    if any(ident in found.get(head, ()) for head in (USE, LOOK, USE_WITH)):
        return USED
    if not typ[TYPE_FLAGS] & SCENERY:
        return ITEM
    return None


def marks(gd) -> List[Mark]:
    """Everything on the map a click does something with, wherever the view is."""
    guest, ds = gd.guest, gd.ds * 16
    listed = draw_list(gd)
    if not listed:
        return []
    things = guest.read((gd.load_seg + game.COMBATANTS_SEG) * 16 + game.COMBATANTS_OFF, game.THINGS * 3)
    items = game.far_pointer(guest, gd.ds, game.ITEMS_PTR)
    found = triggers(gd)
    leader = gd.creature(0)
    out, seen = [], set()
    for thing, x, y in listed:
        if thing in seen:
            continue
        seen.add(thing)
        kind, index = struct.unpack_from("<Bh", things, thing * 3)
        record = guest.read(ds + targeting.MAP_THINGS + thing * targeting.MAP_THING_SIZE, targeting.MAP_THING_SIZE)
        up = max(UP_LEAST, min(UP_MOST, record[MAP_HEIGHT] + UP_OVER))
        if kind == 2 and 0 <= index < 512:
            rec = gd.creature(index)
            what = creature_kind(rec, index, leader, found[TALK])
            if what:
                out.append(Mark(thing, what, gd.creature_name(index).strip(), x, y, labels.UP))
        elif kind == game.THING_ITEM and 0 <= index < game.NO_ITEM:
            item = guest.read(items + index * game.ITEM_SIZE, game.ITEM_SIZE)
            typ = gd.item_type_record(item)
            name = gd.item_name(struct.unpack_from("<H", item, game.ITEM_NAME)[0]).strip()
            if name.startswith("item "):  # (game.item_name's word for no name)
                name = ""
            what = item_kind(item, typ, struct.unpack_from("<h", record, MAP_OBJECT)[0], name, found)
            if what:
                out.append(Mark(thing, what, name[:1].upper() + name[1:], x, y, up))
    return out


def ring_table(found: List[Mark], camera: Tuple[int, int]) -> bytes:
    """DSCLOG's table of rings: one under each mark in the view or NEAR it."""
    out = bytearray(game.THINGS)
    for m in found:
        if -NEAR <= m.x - camera[0] < VIEW_W + NEAR and -NEAR <= m.y - camera[1] < VIEW_H + NEAR:
            out[m.thing] = RING
    return bytes(out)


def nearest(found: List[Mark], camera: Tuple[int, int], pointer: Tuple[int, int], most: int = NAMED) -> List[Mark]:
    """The named marks in the view, the nearest to the pointer first, MOST of them."""
    def on_screen(m: Mark) -> Tuple[int, int]:
        return m.x - camera[0], m.y - camera[1]
    seen = [m for m in found if m.name and 0 <= on_screen(m)[0] < VIEW_W and 0 <= on_screen(m)[1] < VIEW_H]
    # (a thing's middle, not its feet: the pointer rests on the thing)
    return sorted(seen, key=lambda m: (math.hypot(on_screen(m)[0] - pointer[0],
                                                  on_screen(m)[1] - m.up // 2 - pointer[1]), m.thing))[:most]


def _camera(gd) -> Tuple[int, int]:
    return struct.unpack("<hh", gd.guest.read(gd.ds * 16 + targeting.CAMERA, 4))


class Usable:
    def __init__(self):
        self.active = False
        self._held_since: Optional[float] = None
        self._stuck = False
        self._table: Optional[bytes] = None
        self._camera: Optional[Tuple[int, int]] = None

    def held(self, guest, now: float) -> bool:
        """Alt is held, and not for so long that it must be a flag left set (Alt+Tab away from
        DOSBox: then nothing until it reads clear again)."""
        if not alt_held(guest):
            self._held_since, self._stuck = None, False
            return False
        if self._held_since is None:
            self._held_since = now
        if now - self._held_since >= STUCK_AFTER:
            self._stuck = True
        return not self._stuck

    def changed(self, gd, on: bool, now: float) -> bool:
        """Whether the marks are due to go up, come down (the key just pressed or let go, a fight
        begun) or move (the view scrolled): asked every pass, so they don't wait for the next look."""
        if (on and self.held(gd.guest, now) and not gd.in_combat()) != self.active:
            return True
        return self.active and self._camera != _camera(gd)

    def update(self, gd, tsr_hdr: Optional[int], on: bool, now: float, names: Optional[labels.Labels] = None) -> Optional[bytes]:
        """The table of rings for rings.py while the marks are up (else None), the names put in
        NAMES's slots or taken out."""
        self.active = bool(on and tsr_hdr is not None and self.held(gd.guest, now) and not gd.in_combat())
        if not self.active:
            if names is not None:
                names.names(gd.guest, tsr_hdr, [], now)
            self._table = self._camera = None
            return None
        found = marks(gd)
        camera = self._camera = _camera(gd)
        if names is not None:
            pointer = struct.unpack("<hh", gd.guest.read(gd.ds * 16 + POINTER, 4))
            names.names(gd.guest, tsr_hdr, [(m.thing, m.name, FOE_INK if m.kind == FOE else NAME_INK, m.up)
                                            for m in nearest(found, camera, pointer)], now)
        self._table = ring_table(found, camera)
        return self._table
