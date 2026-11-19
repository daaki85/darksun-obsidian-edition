"""Writes the Loader may never make: over low memory, or the start of the game's data segment."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import game
from dsloader.guestmem import GuestMemory, LOW_MEMORY, WriteRefused


class FakeProcess:
    def __init__(self, size):
        self.mem = bytearray(size)

    def read(self, addr, n):
        return bytes(self.mem[addr:addr + n])

    def write(self, addr, data):
        self.mem[addr:addr + len(data)] = data


class GuardTests(unittest.TestCase):
    def test_refused_and_noted(self):
        """A write from a pointer read while the game had it empty (0:offset) goes nowhere, says
        where it came from, and raises (WriteRefused); others are made."""
        proc = FakeProcess(0x100000)
        guest = GuestMemory(proc, 0, 0x100000)
        game.GameData(guest, 0x4000)
        for at, data in ((0x10, b"\xff\xff"), (0x4000 * 16 + 2, b"\xff"), (LOW_MEMORY - 1, b"\xff\xff")):
            with self.assertRaises(WriteRefused):  # (raised: a change of several writes not half made)
                guest.write(at, data)
        self.assertEqual(proc.mem[0x10], 0)
        self.assertEqual(proc.mem[0x40002], 0)
        self.assertEqual(proc.mem[LOW_MEMORY], 0)
        self.assertEqual(len(guest.refused), 3)
        self.assertIn("low memory", guest.refused[0])
        self.assertIn("data segment", guest.refused[1])
        self.assertIn("test_guestmem.py", guest.refused[0])
        guest.write(0x4000 * 16 + game.NULL_AREA, b"\x07")
        guest.write(LOW_MEMORY, b"\x07")
        self.assertEqual((proc.mem[0x4000 * 16 + game.NULL_AREA], proc.mem[LOW_MEMORY]), (7, 7))
        self.assertEqual(len(guest.refused), 3)


class NullTableTests(unittest.TestCase):
    def test_no_write_through_a_null_table(self):
        """A table's pointer read null (an area loading): no address made from it to write through
        (game.TableGone), where a sheet index far enough in would pass the low-memory guard; the
        dice log's step drops it quietly, for a later pass."""
        from dsloader import aging, dicelog
        proc = FakeProcess(0x100000)
        guest = GuestMemory(proc, 0, 0x100000)
        gd = game.GameData(guest, 0x4000)
        with self.assertRaises(game.TableGone):
            aging.sheet_address(gd, 30)
        proc.mem[0x4000 * 16 + game.SHEETS_PTR:0x4000 * 16 + game.SHEETS_PTR + 4] = b"\x00\x00\x00\x50"
        self.assertEqual(aging.sheet_address(gd, 1), 0x50000)  # (its creature, zeros: sheet 0)
        log = dicelog.DiceLog(guest)
        self.assertEqual(log._step(lambda: aging.sheet_address(game.GameData(GuestMemory(FakeProcess(0x100000), 0, 0x100000), 0x4000), 30)), [])


if __name__ == "__main__":
    unittest.main()


class LocateTests(unittest.TestCase):
    def test_recompiled_mark_across_two_chunks(self):
        """Dark Sun Recompiled's mark (F000:FFC0, 18 bytes) found where it starts in one 4 MB chunk
        of the search and ends in the next (the chunks overlap by the longest mark, not the BIOS
        date's 8 bytes)."""
        from dsloader import guestmem
        from dsloader.process import Region
        base = guestmem._CHUNK - guestmem.RECOMPILED_ADDR - 5  # (the mark's first 5 bytes in the first chunk)
        proc = FakeProcess(base + 0x110000)
        proc.regions = lambda: [Region(0, len(proc.mem))]
        for i in range(32):  # (an IVT: the BIOS's handlers at F000:xxxx)
            proc.mem[base + i * 4 + 2:base + i * 4 + 4] = (0xF000).to_bytes(2, "little")
        at = base + guestmem.RECOMPILED_ADDR
        proc.mem[at:at + len(guestmem.RECOMPILED_MARK)] = guestmem.RECOMPILED_MARK
        self.assertEqual(guestmem.locate(proc).base, base)
