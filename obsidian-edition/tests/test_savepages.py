"""Tests for savepages.py: the save/load window's PAGE 1 and PAGE 2 buttons."""

import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import art, savepages


def fake_window(items=14):
    """A window chunk as the game's: 'WIND', its length, its id, ..., its item count at 243, its
    items (30 bytes each) from 261, each its type 4 bytes in."""
    head = bytearray(261)
    head[0:4] = b"WIND"
    struct.pack_into("<I", head, 8, savepages.WINDOW)
    struct.pack_into("<H", head, savepages.WIND_COUNT, items)
    body = b"".join(bytes(4) + b"BUTN" + struct.pack("<IHH", 0x700 + i, 10, 10 * i) + bytes(14)
                    for i in range(items))
    out = bytearray(head + body)
    struct.pack_into("<I", out, 4, len(out))
    return bytes(out)


def fake_font():
    """A font chunk: height 9, every glyph 6 wide, all ink (254) on its third row."""
    height, width = 9, 6
    glyph = bytes([width, 0]) + bytes(width * 2) + bytes([art.FONT_INK] * width) + bytes(width * (height - 3))
    chunk = bytearray(0x308)
    chunk[2] = height
    for code in range(256):
        struct.pack_into("<H", chunk, 0x108 + 2 * code, len(chunk))
    return bytes(chunk + glyph)


def fake_exit_icon():
    """EXIT's four 44x15 pictures, each its stone colour all over (as LOOKS has them)."""
    return savepages.encode_frames([[[look[0]] * 44 for _ in range(15)] for look in savepages.LOOKS])


class WindowTests(unittest.TestCase):
    def test_buttons_put_in(self):
        window = savepages.window_with_buttons(fake_window())
        self.assertEqual(struct.unpack_from("<I", window, 4)[0], len(window))
        self.assertEqual(struct.unpack_from("<H", window, savepages.WIND_COUNT)[0], 14 + len(savepages.PAGES))
        for i, (cid, _, y) in enumerate(savepages.PAGES):
            item = window[261 + 30 * (14 + i):261 + 30 * (15 + i)]
            self.assertEqual(item[:4], bytes(4))  # (the game's: the chunk's address)
            self.assertEqual(item[4:16], b"BUTN" + struct.pack("<IHH", cid, savepages.BUTTON_X, y))
        self.assertEqual(savepages.window_with_buttons(window), window)  # (once)

    def test_button_chunk(self):
        exit_button = b"BUTN" + struct.pack("<I", 110) + struct.pack("<I", savepages.EXIT) + bytes(78) \
            + struct.pack("<H", savepages.EXIT) + bytes(8) + struct.pack("<I", savepages.EXIT) + bytes(6)
        mine = savepages._button(exit_button, 0x815)
        self.assertNotIn(struct.pack("<I", savepages.EXIT), mine)
        self.assertEqual(mine.count(struct.pack("<H", 0x815)), 3)


class PictureTests(unittest.TestCase):
    def test_four_pictures_with_the_text(self):
        font = art.Font(fake_font())
        chunk = savepages.encode_frames(savepages.button_pictures(fake_exit_icon(), font, "PAGE 1"))
        self.assertEqual(struct.unpack_from("<IH", chunk, 0), (len(chunk), 4))
        for f, (stone, ink, _, (top, _), (left, right), push) in enumerate(savepages.LOOKS):
            width, height, rows = art.decode_frame(chunk, f)
            self.assertEqual((width, height), (44, 15))
            row = rows[savepages.TEXT_TOP + push + 2]
            inked = [x for x in range(width) if row[x] == ink]
            self.assertEqual(len(inked), 36)  # (6 letters, 6 wide each)
            self.assertEqual(inked[0], left + (right - left + 1 - 36) // 2)  # (centred)
            self.assertEqual(rows[0][0], stone)


if __name__ == "__main__":
    unittest.main()
