import struct
import unittest

from dsloader import scrolling

HDR = 0x9000


class Guest:
    def __init__(self):
        self.mem = bytearray(0x10000)

    def read(self, at, n):
        return bytes(self.mem[at:at + n])

    def write(self, at, data):
        self.mem[at:at + len(data)] = data


class Game:
    def __init__(self):
        self.guest = Guest()

    def words(self, at, n):
        return struct.unpack(f"<{n}H", self.guest.read(HDR + at, 2 * n))


class ScrollingTests(unittest.TestCase):
    def test_update(self):
        """The switch written when it changes (and again for a new DSCLOG)."""
        gd, s = Game(), scrolling.Scrolling()
        s.update(gd, HDR, True)
        self.assertEqual(gd.words(scrolling.TSR_SCROLL_ON, 1), (1,))
        gd.guest.write(HDR + scrolling.TSR_SCROLL_ON, b"\0\0")  # (the game started again)
        s.update(gd, HDR, True)
        self.assertEqual(gd.words(scrolling.TSR_SCROLL_ON, 1), (0,))  # (not written: unchanged)
        s.forget()
        s.update(gd, HDR, True)
        self.assertEqual(gd.words(scrolling.TSR_SCROLL_ON, 1), (1,))
        s.update(gd, HDR, False)
        self.assertEqual(gd.words(scrolling.TSR_SCROLL_ON, 1), (0,))
        s.update(gd, HDR, True, right=True)  # (the right button too)
        self.assertEqual(gd.words(scrolling.TSR_SCROLL_ON, 1), (scrolling.DRAG_MIDDLE | scrolling.DRAG_RIGHT,))


if __name__ == "__main__":
    unittest.main()
