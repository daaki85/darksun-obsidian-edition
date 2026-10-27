"""The Loader's changes to the game's item lists made only while the game leaves them be.

The game rebuilds its item lists as an area loads (and at START GAME): it writes the area it
leaves out, reads the next in, and hands the party's items new records (every item a new number).
A change of the Loader's made across that, from numbers read before it, lands on records that
are no longer what they were: a record taken from the free list that the game hands out too, or a
list linked through an item that is now another's. An item cut out of its list so is simply gone.

So every write of the Loader's to the item lists (the item table, the things table and its free
lists, a creature's list heads) goes through this gate (GuestMemory.write: ItemGate.covers). The
first in a pass (dicelog's poll: begin, end) waits until WAIT has passed since the pass began
reading, pauses DOSBox, and looks again at the game's free lists, its area and its item table's
place: all as at the start, and the writes go ahead with the game held still until the pass ends;
anything changed, and none of the pass's item writes are made (ItemsBusy), to be tried again in the
next. A write outside a pass (a tool's) has the lists looked at over the wait first, not held.
"""

import atexit
import time
from typing import Callable, Optional

from . import game

WAIT = 0.06  # seconds the game's lists must stay the same before the Loader changes them
ITEM_RECORDS = 400  # the game's item table: records 0-399
THING_COUNT = 0x208  # (ring.THING_COUNT: objects 0-519, 3 bytes each)
FREE_THINGS, THINGS_USED, FREE_ITEMS = 0x4D72, 0x4C48, 0x4D76  # (ring.py's)
REGION = 0x117C  # (ring.REGION)
MAX_CREATURES = 512  # (buyback.MAX_CREATURES)


class ItemsBusy(ValueError):
    """The game was changing its item lists: the Loader's change waits for the next pass. (A
    ValueError, so the passes' own guards against a game read mid-change catch it too.)"""


class ItemGate:
    def __init__(self, gd, wait: float = WAIT, clock: Callable[[], float] = time.monotonic,
                 sleep: Callable[[float], None] = time.sleep):
        self.gd = gd
        self.wait, self.clock, self.sleep = wait, clock, sleep
        self._heads: Optional[bytes] = None  # (the lists as the pass began)
        self._since = 0.0
        self._state = "idle"  # idle, watching (a pass begun), held (writes go ahead), refused
        self._paused = False  # (DOSBox paused while held)
        self.refusals = 0  # (passes whose item writes waited: for tests and the freeze report)

    def _read_heads(self) -> bytes:
        guest, ds = self.gd.guest, self.gd.ds * 16
        return b"".join(guest.read(ds + at, size) for at, size in
                        ((FREE_ITEMS, 2), (FREE_THINGS, 2), (THINGS_USED, 2), (REGION, 2),
                         (game.ITEMS_PTR, 4), (game.CREATURES_PTR, 4)))

    def covers(self, addr: int, size: int) -> bool:
        """Whether a write there changes the game's item lists."""
        guest, ds = self.gd.guest, self.gd.ds
        end = addr + size
        heads = ds * 16
        if any(addr < heads + at + 2 and end > heads + at for at in (FREE_ITEMS, FREE_THINGS, THINGS_USED)):
            return True
        things = (self.gd.load_seg + game.COMBATANTS_SEG) * 16 + game.COMBATANTS_OFF
        if addr < things + THING_COUNT * 3 and end > things:
            return True
        items = game.far_pointer(guest, ds, game.ITEMS_PTR)
        if items and addr < items + ITEM_RECORDS * game.ITEM_SIZE and end > items:
            return True
        creatures = game.far_pointer(guest, ds, game.CREATURES_PTR)
        if creatures and creatures <= addr < creatures + MAX_CREATURES * game.CREATURE_SIZE:
            first = (addr - creatures) // game.CREATURE_SIZE
            for index in range(first, (end - 1 - creatures) // game.CREATURE_SIZE + 1):
                at = creatures + index * game.CREATURE_SIZE
                if any(addr < at + o + 2 and end > at + o for o in game.CREATURE_ITEM_LISTS):
                    return True
        return False

    def begin(self) -> None:
        """A pass begins: the lists as they are now, before it reads anything of them."""
        self.end()
        self._heads, self._since, self._state = self._read_heads(), self.clock(), "watching"

    def open(self) -> None:
        """Before a write to the item lists: once per pass, the wait, DOSBox paused and the lists
        looked at again. Raises ItemsBusy if they changed (and for the rest of the pass)."""
        if self._state == "held":
            return
        if self._state == "refused":
            raise ItemsBusy("the game's item lists changed")
        if self._state == "idle":  # (a write outside a pass: looked at over the wait, not held)
            heads = self._read_heads()
            self.sleep(self.wait)
            if self._read_heads() != heads:
                self.refusals += 1
                raise ItemsBusy("the game's item lists changed")
            return
        left = self.wait - (self.clock() - self._since)
        if left > 0:
            self.sleep(left)
        proc = getattr(self.gd.guest, "proc", None)
        paused = _pause(proc)
        try:
            heads = self._read_heads()
        except BaseException:  # (DOSBox never left paused behind a failed look)
            if paused:
                _resume(proc)
            raise
        if heads != self._heads:
            if paused:
                _resume(proc)
            self._state = "refused"
            self.refusals += 1
            raise ItemsBusy("the game's item lists changed")
        # (with no pausing to be had, the writes follow the look as closely as they can)
        self._state, self._paused = "held", paused
        if paused:
            _HELD.add(proc)

    def release(self) -> None:
        """A block of writes made: DOSBox runs on, the pass goes on (a later write looks again,
        against the lists as the pass began)."""
        if self._state == "held":
            if self._paused:
                _resume(getattr(self.gd.guest, "proc", None))
            self._state, self._paused = "watching", False

    def end(self) -> None:
        """The pass is over: DOSBox runs on."""
        if self._state == "held" and self._paused:
            _resume(getattr(self.gd.guest, "proc", None))
        self._state, self._heads, self._paused = "idle", None, False


def hold(gd) -> None:
    """Before a change to the game's item lists that can't be made twice (a roll, a counter
    moved on): the gate opened for this pass now, so that if the game is changing them (ItemsBusy)
    nothing has been done yet and it is tried again in a later pass."""
    gate = getattr(getattr(gd, "guest", None), "item_gate", None)
    if gate is not None:
        gate.open()


def release(gd) -> None:
    """A block of changes to the item lists made: the game runs on (ItemGate.release)."""
    gate = getattr(getattr(gd, "guest", None), "item_gate", None)
    if gate is not None:
        gate.release()


def _pause(proc) -> bool:
    try:
        return bool(proc is not None and proc.suspend())
    except (OSError, AttributeError):
        return False


def _resume(proc) -> None:
    _HELD.discard(proc)
    try:
        proc.resume()
    except (OSError, AttributeError):
        pass


_HELD: set = set()  # (processes paused now: let go if the Loader exits mid-pass)


@atexit.register
def _let_go() -> None:
    for proc in list(_HELD):
        _resume(proc)
