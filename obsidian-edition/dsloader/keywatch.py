"""The keys pressed in the game, read from the BIOS keyboard buffer: a key of the Loader's own that
costs DSCLOG nothing (R, which shows and hides the squares in reach: squares.py).

DOSBox's keyboard handler puts every key into the BIOS buffer in the game's memory, as a PC's BIOS
does: sixteen words from 0040:001Eh, the next free one at 0040:001Ch (the tail), the next to read
at 0040:001Ah (the head), both offsets from segment 40h that go round from 3Eh to 1Eh. The game
reads its keys through INT 16h, which takes them from the head; the bytes stay where they were
written. So the keys pressed since the last look are the words between the tail as it was then
and the tail now, whether the game has read them yet or not.

The Loader only looks: the key still reaches the game. That suits a key the game has no use for on
the map (R is not among the keys of its table at DSUN.EXE 1BC5Bh, nor a hot key of its manual's),
and it is why a key the game does use is counted by DSCLOG instead (L, T, S, F5 and F9: taken from
the game there). More than fifteen keys between two looks (20 to 50 ms apart) would be missed;
nobody types that fast.
"""

import struct
from typing import List, Optional

BIOS = 0x400  # the BIOS data area (segment 40h)
HEAD, TAIL = 0x1A, 0x1C  # words: the buffer's next key to read, and its next free place
FIRST, END = 0x1E, 0x3E  # the buffer: sixteen words, the offsets going round
KEY_R, KEY_SHIFT_R = 0x1372, 0x1352  # as INT 16h gives them: the scan code, then the letter


class KeyWatch:
    def __init__(self):
        self._tail: Optional[int] = None  # the tail at the last look

    def forget(self) -> None:
        """Another game, or a game started again: nothing known of its buffer."""
        self._tail = None

    def take(self, guest) -> List[int]:
        """The keys pressed since the last look, oldest first (none at the first look, or when the
        buffer's words read as no buffer)."""
        tail, = struct.unpack("<H", guest.read(BIOS + TAIL, 2))
        if not FIRST <= tail < END or tail & 1:
            self._tail = None
            return []
        before, self._tail = self._tail, tail
        if before is None or before == tail:
            return []
        out = []
        at = before
        while at != tail and len(out) < (END - FIRST) // 2:
            out.append(struct.unpack("<H", guest.read(BIOS + at, 2))[0])
            at = at + 2 if at + 2 < END else FIRST
        return out
