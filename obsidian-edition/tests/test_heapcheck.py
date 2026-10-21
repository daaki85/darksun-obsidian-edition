import struct
import unittest

from dsloader import heapcheck

LOAD = 0x0200


def memory():
    """A game at LOAD (MCB at LOAD-11h) of 3000h paragraphs, a free block and the last one after
    it; its heap 2000h-3000h with two free blocks in a ring."""
    m = bytearray(0x40000)
    mcb = LOAD - 0x11
    struct.pack_into("<BHH", m, mcb * 16, 0x4D, LOAD - 0x10, 0x3010)
    nxt = mcb + 0x3010 + 1
    struct.pack_into("<BHH", m, nxt * 16, 0x4D, 0, 0x100)  # 4 KB free
    nxt += 0x101
    struct.pack_into("<BHH", m, nxt * 16, 0x5A, 0, 0x200)  # 8 KB free
    struct.pack_into("<HHH", m, LOAD * 16 + heapcheck.HEAP_VARS, 0x2000, 0x3000, 0x2400)
    struct.pack_into("<HHHH", m, 0x2400 * 16, 0x40, 0, 0x2800, 0x2800)  # (size, prev real, prev free, next free)
    struct.pack_into("<HHHH", m, 0x2800 * 16, 0x10, 0, 0x2400, 0x2400)
    return m


def reader(m):
    return lambda at, size: bytes(m[at:at + size])


class SampleTests(unittest.TestCase):
    def test_heap_and_dos(self):
        s = heapcheck.sample(reader(memory()), LOAD)
        self.assertEqual(s, heapcheck.Memory(0x1000 * 16, 0x50 * 16, 0x40 * 16, 2, 0x300 * 16, 0x200 * 16))

    def test_no_game(self):
        self.assertIsNone(heapcheck.sample(reader(bytearray(0x40000)), LOAD))

    def test_watch_keeps_the_lowest(self):
        w = heapcheck.Watch()
        self.assertEqual(w.lines(), [])
        m = memory()
        w.take(reader(m), LOAD)
        struct.pack_into("<H", m, 0x2400 * 16, 0x08)  # less free
        w.take(reader(m), LOAD)
        struct.pack_into("<H", m, 0x2400 * 16, 0x80)  # more again
        w.take(reader(m), LOAD)
        self.assertEqual(w.last.largest, 0x80 * 16)
        self.assertEqual(w.lowest.largest, 0x10 * 16)
        lines = w.lines()
        self.assertIn("60,000 bytes", lines[0])
        self.assertIn("2 pieces", lines[1])


class NoteTests(unittest.TestCase):
    """The dice log's lines: the overlay buffer not in upper memory (once), and memory low with the
    map open (once, again only after it has recovered)."""
    DS, HDR = 0x3800, 0x3A000

    def setUp(self):
        self.m = memory()
        self.read = reader(self.m)
        self.map_open(True)

    def map_open(self, on):
        struct.pack_into("<H", self.m, self.DS * 16 + heapcheck.MAP_OPEN, 1 if on else 0)

    def spare(self, kb):  # (DOS's free blocks after the game, 4 and 8 KB, cut to fit; the heap's 1.25 KB)
        struct.pack_into("<H", self.m, 0x2400 * 16, 0x10)
        struct.pack_into("<H", self.m, 0x2800 * 16, 0x10)
        last = LOAD - 0x11 + 0x3010 + 1 + 0x101
        struct.pack_into("<H", self.m, last * 16 + 3, max(kb * 64 - 0x100 - 0x20, 0))

    def test_overlay_in_upper_memory(self):
        struct.pack_into("<H", self.m, self.HDR + heapcheck.TSR_OVR_GIVEN, 0xDE1F)
        w = heapcheck.Watch()
        self.spare(80)
        self.assertEqual(w.take(self.read, LOAD, self.DS, self.HDR), [])
        self.assertIn("in upper memory (DE1Fh)", w.lines()[3])

    def test_overlay_not_there(self):
        w = heapcheck.Watch()
        self.spare(80)
        self.assertEqual(w.take(self.read, LOAD, self.DS, self.HDR), [heapcheck.OVERLAY_LOW_LINE])
        self.assertEqual(w.take(self.read, LOAD, self.DS, self.HDR), [])  # (once)
        self.assertIn("in the 640 KB", w.lines()[3])

    def test_low_once_then_again_after_recovering(self):
        struct.pack_into("<H", self.m, self.HDR + heapcheck.TSR_OVR_GIVEN, 0xDE1F)
        w = heapcheck.Watch()
        self.spare(20)
        lines = w.take(self.read, LOAD, self.DS, self.HDR)
        self.assertEqual(len(lines), 1)
        self.assertTrue(lines[0].startswith("Memory is running low: 20 KB spare with the map open."))
        self.assertEqual(w.take(self.read, LOAD, self.DS, self.HDR), [])  # (said once)
        self.spare(28)  # (not yet recovered)
        w.take(self.read, LOAD, self.DS, self.HDR)
        self.spare(20)
        self.assertEqual(w.take(self.read, LOAD, self.DS, self.HDR), [])
        self.spare(40)
        w.take(self.read, LOAD, self.DS, self.HDR)
        self.spare(20)
        self.assertEqual(len(w.take(self.read, LOAD, self.DS, self.HDR)), 1)  # (said again)

    def test_not_while_the_map_is_closed(self):
        struct.pack_into("<H", self.m, self.HDR + heapcheck.TSR_OVR_GIVEN, 0xDE1F)
        self.map_open(False)
        self.spare(10)
        self.assertEqual(heapcheck.Watch().take(self.read, LOAD, self.DS, self.HDR), [])

if __name__ == "__main__":
    unittest.main()
