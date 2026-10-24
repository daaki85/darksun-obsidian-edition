import struct
import unittest

from dsloader import scenepointer


def picture(rows):
    """A one-frame picture chunk as the game packs one (each pixel literal, a row's span ending
    with 80h)."""
    width, height = max(len(r) for r in rows), len(rows)
    body = bytearray()
    for y, row in enumerate(rows):
        x = 0
        while x < len(row) and row[x] is None:
            x += 1
        pixels = [p if p is not None else 0 for p in row[x:]]
        data = bytes((2 * (len(pixels) - 1),)) + bytes(pixels)
        body += bytes((y, x, 0x80, 0, len(data))) + data
    body += b"\xff"
    head = struct.pack("<IHI", 0, 1, 10)
    return head + struct.pack("<HH", width, height) + bytes(body)


class PointerDataTests(unittest.TestCase):
    """POINTER.BIN: rows, colours, their parts (6 bits), each row's pixels as colour numbers."""

    def test_layout(self):
        palette = bytearray(768)
        palette[5 * 3:5 * 3 + 3] = bytes((63, 62, 61))
        palette[9 * 3:9 * 3 + 3] = bytes((1, 2, 3))
        data = scenepointer.pointer_data(picture([[9, 5], [9, 5, 9]]), bytes(palette))
        self.assertEqual(len(data), 2 + scenepointer.COLOURS * 3 + scenepointer.SHAPE)
        self.assertEqual(data[:2], bytes((2, 2)))
        self.assertEqual(data[2:8], bytes((63, 62, 61, 1, 2, 3)))  # (colour 5 first, then 9)
        shape = data[2 + scenepointer.COLOURS * 3:]
        self.assertEqual(shape[:7], bytes((2, 1, 0, 2, 1, 2, 0)))

    def test_too_big(self):
        with self.assertRaises(ValueError):
            scenepointer.pointer_data(picture([[1] * 20] * 20), bytes(768))

    def test_no_game_files(self):
        import os, tempfile
        dest = os.path.join(tempfile.mkdtemp(), scenepointer.POINTER_FILE)
        open(dest, "wb").close()
        self.assertFalse(scenepointer.write_pointer(None, None, dest))
        self.assertFalse(os.path.exists(dest))


if __name__ == "__main__":
    unittest.main()
