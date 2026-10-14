"""Tests for rollstore.py: STORE and RECALL on the creation screen (their pictures, buttons and the
creation window), and their patch and probe."""

import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import gamepatch, rollstore as rs
from dsloader.art import decode_frame
from dsloader.weaponpages import BUTN_SIZE, ITEM_AT, ITEM_SIZE, WIND_COUNT, _encode, _items

BEVEL, FACE, HIGH, MID, SHADE = 21, 24, 31, 27, 20
LETTER_W = 7


def button(word: str, width: int, touching: bool = False):
    """A carved button's three frames: a bevel, the face, and WORD's letters as blocks in the
    three tones, a column of face between them (or, TOUCHING, one of shadow joining them)."""
    def frame():
        rows = [[BEVEL if x < 2 or x >= width - 2 or y < 2 or y >= 13 else FACE for x in range(width)]
                for y in range(15)]
        x = 4
        for _ in word:
            for y in range(3, 11):
                for dx in range(LETTER_W):
                    rows[y][x + dx] = (HIGH, MID, SHADE)[dx % 3]
            if touching:
                rows[6][x + LETTER_W] = SHADE
            x += LETTER_W + 1
        return rows
    return _encode([frame() for _ in range(3)])


def fake_resource():
    window = bytearray(ITEM_AT)
    window[0:4] = b"WIND"
    items = [(0x7D0, 243, 174, b"BUTN"), (0xFA3, 40, 125, b"EBOX")]
    struct.pack_into("<H", window, WIND_COUNT, len(items))
    window += b"".join(bytes(4) + kind + struct.pack("<IHH", cid, x, y) + bytes(ITEM_SIZE - 16)
                       for cid, x, y, kind in items)
    struct.pack_into("<I", window, 4, len(window))
    butn = bytearray(BUTN_SIZE + 4)
    struct.pack_into("<I", butn, 8, rs.SAVE)
    return {("WIND", rs.CREATION): bytes(window), ("BUTN", rs.SAVE): bytes(butn),
            ("ICON", rs.SAVE): button("SAVE", 44, touching=True), ("ICON", rs.LOAD): button("LOAD", 44, touching=True),
            ("ICON", rs.DROP): button("DROP", 44), ("ICON", rs.DELETE): button("DELETE", 62),
            ("ICON", rs.EXIT): button("EXIT", 44)}


class RollStoreTests(unittest.TestCase):
    def setUp(self):
        self.resource = fake_resource()
        self.out = rs.chunks(self.resource)

    def test_buttons(self):
        """Each its own id, as wide as its picture, 15 high; three pictures each."""
        for cid, width in ((rs.STORE, rs.STORE_WIDTH), (rs.RECALL, rs.RECALL_WIDTH)):
            butn = self.out[("BUTN", cid)]
            self.assertEqual(struct.unpack_from("<I", butn, 8)[0], cid)
            self.assertEqual(struct.unpack_from("<HH", butn, BUTN_SIZE), (width, 15))
            icon = self.out[("ICON", cid)]
            self.assertEqual(struct.unpack_from("<H", icon, 4)[0], len(rs.FRAMES))
            w, h, rows = decode_frame(icon, 0)
            self.assertEqual((w, h), (width, 15))
            self.assertEqual(decode_frame(icon, 2)[2], rows)  # (the third as the first)

    def test_letters_cut(self):
        """Touching letters are cut into as many as the word has."""
        _, _, rows = decode_frame(self.resource[("ICON", rs.SAVE)], 0)
        self.assertEqual(len(rs._letters(rows, 4)), 4)

    def test_c_in_o_tones(self):
        c, _ = rs._glyph(self.resource, "C", 0)
        o, _ = rs._glyph(self.resource, "O", 0)
        tones = {p for r in c[rs.C_TOP:rs.C_TOP + len(rs.C_SHAPE)] for p in r if p is not None}
        self.assertEqual(tones, {o[3][2], o[4][2], o[3][5]})

    def test_window(self):
        """The window's own items kept as they are (its name box too), the two buttons after
        them, under the hit points and PSP; and only once."""
        window = self.out[("WIND", rs.CREATION)]
        original = self.resource[("WIND", rs.CREATION)]
        self.assertEqual(window[ITEM_AT:ITEM_AT + 2 * ITEM_SIZE], original[ITEM_AT:])
        self.assertEqual(_items(window)[-2:], [(rs.STORE, *rs.STORE_AT), (rs.RECALL, *rs.RECALL_AT)])
        self.assertEqual(struct.unpack_from("<I", window, 4)[0], len(window))
        self.assertEqual(rs.with_buttons(window), window)
        self.assertLessEqual(rs.STORE_AT[0] + rs.STORE_WIDTH, rs.RECALL_AT[0])
        self.assertLessEqual(rs.RECALL_AT[0] + rs.RECALL_WIDTH, 243)  # (clear of DONE)

    def test_missing(self):
        self.assertEqual(rs.chunks({}), {})

    def test_patch(self):
        """The click routine's lookup of its buttons goes to DSCLOG's PROBE_RS_CLICK."""
        patch = next(p for p in gamepatch.PATCHES if p.name == "roll_store")
        self.assertEqual(patch.replacement[:2], bytes((0xCD, gamepatch.VEC_RS_CLICK)))
        here = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(here, "..", "dos", "dsclog.asm")) as f:
            asm = f.read()
        self.assertIn(f"VEC_RS_CLICK equ 0x{gamepatch.VEC_RS_CLICK:X}", asm)
        self.assertIn(f"RS_STORE  equ 0x{rs.STORE:X}", asm)
        self.assertIn(f"RS_RECALL equ 0x{rs.RECALL:X}", asm)


if __name__ == "__main__":
    unittest.main()
