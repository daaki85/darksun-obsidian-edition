"""The freeze report (dsloader/freeze.py), from a made-up memory."""

import os
import struct
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dsloader import freeze, game  # noqa: E402

TSR_SEG, HDR_AT, TICKS_AT = 0xC000, 0x40, 0x900  # DSCLOG's segment, its header's and TICKS's offsets
DS = 0x4356 + 0x1A2


def memory(notes, seq=None):
    """1 MB + 64 KB with DSCLOG's header at C000:0040 and NOTES (CS, IP pairs) in TICKS, the last
    the newest, SEQ taken in all."""
    mem = bytearray(game.CONVENTIONAL_AND_UPPER)
    hdr = TSR_SEG * 16 + HDR_AT
    struct.pack_into("<H", mem, hdr + freeze.TSR_HDR_OFF, HDR_AT)
    seq = len(notes) if seq is None else seq
    struct.pack_into("<HH", mem, hdr + freeze.TSR_TICK_OFF, TICKS_AT, seq)
    for k, (cs, ip) in enumerate(notes):
        slot = (seq - len(notes) + k) % freeze.TICK_SLOTS
        struct.pack_into("<8H", mem, TSR_SEG * 16 + TICKS_AT + slot * freeze.TICK_SIZE,
                         ip, cs, 0x0246, 0x4000, 0x0F00 + k, 0x0F10, DS, 0xA000)
    return mem, hdr


class FreezeTests(unittest.TestCase):
    def test_ticks_oldest_first(self):
        notes = [(0x2000, 0x100 + k) for k in range(40)]  # more than the slots: the last 32 kept
        mem, hdr = memory(notes[-freeze.TICK_SLOTS:], seq=40)
        found = freeze.ticks(lambda a, n: bytes(mem[a:a + n]), hdr)
        self.assertEqual([(t.cs, t.ip) for t in found], notes[-freeze.TICK_SLOTS:])
        self.assertEqual(found[-1].sp, 0x0F00 + freeze.TICK_SLOTS - 1)

    def test_places(self):
        load = DS - game.DGROUP
        self.assertEqual(freeze.place(TSR_SEG, 0x1234, TSR_SEG, load), "DSCLOG +1234")
        self.assertEqual(freeze.place(0xF000, 0x10, TSR_SEG, load), "the BIOS")
        self.assertEqual(freeze.place(load + 0x33A5, 0x4D9, TSR_SEG, load),
                         "game 33A5:04D9 (DSUN.EXE 39329h, unless an overlay)")

    def test_stuck_in_one_place(self):
        load = DS - game.DGROUP
        mem, hdr = memory([(load + 0x33A5, 0x4D9)] * 10)
        read = lambda a, n: bytes(mem[a:a + n])
        text = freeze.report_text(read, hdr, DS, "now", "9.9", {"kits": True}, "a\nb", "", {"tick": 0, "main": 0})
        self.assertIn("The last 8 notes are all at 3547:04D9: game 33A5:04D9 (DSUN.EXE 39329h", text)
        self.assertIn("the timer was noted 0 times", text)
        self.assertIn("  kits: True", text)
        self.assertIn("The dice log's last lines:\na\nb", text)
        self.assertIn("The dialogue's last lines:\n(empty)", text)

    def test_spread(self):
        mem, hdr = memory([(0x2000 + k % 3, 0x10) for k in range(9)])
        text = freeze.report_text(lambda a, n: bytes(mem[a:a + n]), hdr, DS, "now", "9.9", {}, "", "", None)
        self.assertIn("The last notes are spread over", text)

    def test_no_helper(self):
        text = freeze.report_text(lambda a, n: bytes(n), None, None, "now", "9.9", {}, "", "", None)
        self.assertIn("DSCLOG wasn't found in memory", text)

    def test_zip(self):
        mem, hdr = memory([(0x2000, 0x10)])
        with tempfile.TemporaryDirectory() as folder:
            first = freeze.write_report(folder, 0, "report", bytes(mem))
            second = freeze.write_report(folder, 0, "again", b"")
            self.assertTrue(first.endswith(".zip") and second.endswith("-2.zip"))
            with zipfile.ZipFile(first) as z:
                self.assertEqual(z.read("freeze-report.txt"), b"report")
                self.assertEqual(len(z.read("memory.bin")), game.CONVENTIONAL_AND_UPPER)


if __name__ == "__main__":
    unittest.main()
