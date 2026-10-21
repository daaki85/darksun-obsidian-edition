"""The game's memory as the crash report tells it: its far heap and the DOS memory after it.

"Out of memory in OEOpenGraph." (DSUN 23413h) is the game stopping when the map's view can't be
opened again: each time it opens (back from the USE screen, a talk, a menu) it takes a block of
60,000 bytes in one piece from the heap (farmalloc, 1DF3:00E3h's EA60h), two smaller ones, and
three pages of video memory; another screen gives them back. The heap is Borland's: its first,
last and rover segments at the runtime's 0FE7h, 0FE9h and 0FEBh (the load segment's), a free
block's size in paragraphs at +0 and the next free one at +6 (a ring); it grows into the DOS
memory after the game's block. Measured on the map with the user's save: no free block in the
heap, 53 KB of DOS memory after it (the unmodded game: 57 KB). Making characters over and over
doesn't change that (35 made, the heap and video memory the same each time), so what used it up
in a long game is unknown: the crash report gives the last sample and the session's lowest."""

import struct
from typing import NamedTuple, Optional

HEAP_VARS = 0x0FE7  # first, last, rover (words, in the load segment)
MAP_BLOCK = 60000  # (what OEOpenGraph asks for in one piece)
PSP_PARAS = 0x10  # (the game's PSP is the 256 bytes before its load segment; its MCB the paragraph before)


class Memory(NamedTuple):
    heap: int  # bytes from the heap's first block to its last
    free: int  # bytes in the heap's free blocks
    largest: int  # the largest of them
    pieces: int
    dos_free: int  # DOS memory free after the game's block (bytes)
    dos_largest: int


def sample(read, load_seg: int) -> Optional[Memory]:
    """The heap and DOS memory now (READ(address, size) -> bytes), or None if they don't read as
    a heap and an MCB chain (the game not running yet, or gone)."""
    try:
        first, last, rover = struct.unpack("<HHH", read(load_seg * 16 + HEAP_VARS, 6))
        if not first or not last or last < first:
            return None
        sizes = []
        block = rover
        while block and len(sizes) < 2000:
            size, = struct.unpack("<H", read(block * 16, 2))
            nxt, = struct.unpack("<H", read(block * 16 + 6, 2))
            sizes.append(size * 16)
            block = nxt
            if block == rover:
                break
        else:
            if block:
                return None  # (no ring: not a heap)
        dos = []
        mcb = load_seg - PSP_PARAS - 1
        for _ in range(64):
            sig, owner, size = struct.unpack("<BHH", read(mcb * 16, 5))
            if sig not in (0x4D, 0x5A):
                return None
            if owner == 0 and mcb > load_seg:
                dos.append(size * 16)
            if sig == 0x5A:
                break
            mcb += size + 1
        return Memory((last - first) * 16, sum(sizes), max(sizes, default=0), len(sizes),
                      sum(dos), max(dos, default=0))
    except (OSError, struct.error, ValueError):
        return None


def describe(m: Memory) -> str:
    return (f"heap {m.heap // 1024} KB with {m.free // 1024} KB free in it ({m.pieces} piece{'' if m.pieces == 1 else 's'}, the largest "
            f"{m.largest} bytes); DOS memory free after the game {m.dos_free // 1024} KB (the largest piece "
            f"{m.dos_largest} bytes)")


class Watch:
    """The last sample and the session's lowest (by DOS memory free), for the crash report."""

    def __init__(self):
        self.last: Optional[Memory] = None
        self.lowest: Optional[Memory] = None

    def take(self, read, load_seg: int) -> None:
        m = sample(read, load_seg)
        if m is None:
            return
        self.last = m
        if self.lowest is None or m.dos_free + m.free < self.lowest.dos_free + self.lowest.free:
            self.lowest = m

    def lines(self) -> list:
        if self.last is None:
            return []
        return ["The game's memory (the map's view needs a block of 60,000 bytes each time it opens):",
                "  last read: " + describe(self.last), "  lowest this session: " + describe(self.lowest)]


WATCH = Watch()  # (one game at a time: the dice log fills it, the crash report reads it)
