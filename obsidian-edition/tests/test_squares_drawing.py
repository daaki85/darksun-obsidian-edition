"""DSCLOG's marks on the squares in reach (TINT_PASS, in the floor pass) run in a CPU emulator
(needs unicorn and nasm), over test_dsclog_drawing's scene and VGA: each marked square's cross,
lightened through LIGHT, clipped to what is being drawn, and the rings' red left as it was."""
import shutil
import struct
import unittest

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from test_dsclog_drawing import CALLER, CAM, SS, TSR, Figures, Uc, floor  # noqa: E402

from dsloader import squares  # noqa: E402

HDR_SQUARES_ON = squares.TSR_SQUARES_ON
ORIGIN = (CAM[0] // 16 - 3, CAM[1] // 16 - 2)  # (the bitmap's first square: left of and above the view)
CROSS = [(0, 0)] + [(d * s, 0) for d in (1, 2) for s in (1, -1)] + [(0, d * s) for d in (1, 2) for s in (1, -1)]
PASSES = 4


def light(c):
    return 0 if c % 13 == 0 else (c + 2) & 0xFF  # (the scene's LIGHT)


def dark(c):
    return (c * 3 + 5) & 0xFF  # (the scene's DARK)


class Marks(Figures):
    """The scene with nothing else drawn (no shadows, dust or rings) and SQ_MAP marking SQUARES."""

    def __init__(self, marked, on=(0, 0, 0), squares_on=1):
        super().__init__(on=on)
        hdr = self.sym["hdr"]
        self.mu.mem_write(TSR * 16 + hdr + HDR_SQUARES_ON, struct.pack("<H", squares_on))
        bits = bytearray(squares.MAP_BYTES)
        bits[0], bits[1] = ORIGIN
        for col, row in marked:
            bit = (row - ORIGIN[1]) * squares.SIDE + col - ORIGIN[0]
            bits[2 + bit // 8] |= 1 << bit % 8
        self.mu.mem_write(TSR * 16 + hdr - squares.PSP_BYTES + squares.SQ_MAP_PSP, bytes(bits))  # (DSCLOG's PSP)


def expected(marked, clip=(0, 0, 319, 199)):
    """The floor with each marked square's cross lightened PASSES times (as far as LIGHT goes)."""
    x0, y0, x1, y1 = clip
    out = bytearray(floor(x, y) for y in range(200) for x in range(320))
    for col, row in marked:
        for dx, dy in CROSS:
            x, y = col * 16 + 8 - CAM[0] + dx, row * 16 + 8 - CAM[1] + dy
            if x0 <= x <= x1 and y0 <= y <= y1:
                c = out[y * 320 + x]
                table = light if light(c) else dark  # (no lighter colour at the first look: darkened)
                for _ in range(PASSES):
                    if not table(c):
                        break
                    c = table(c)
                out[y * 320 + x] = c
    return bytes(out)


# squares on the view, at its edges (a cross cut by them), off it, and the bitmap's corners
C0, R0 = CAM[0] // 16, CAM[1] // 16  # (the square the view's top left is in: 62, 31)
MARKED = [(C0 + 5, R0 + 4), (C0 + 6, R0 + 4), (C0 + 6, R0 + 5), (C0 + 12, R0 + 9), (C0, R0), (C0 + 20, R0 + 12),
          (C0 + 19, R0 + 3), (C0 - 3, R0 - 2), (C0 + 28, R0 + 29), (C0 + 10, R0 + 20), (C0 - 1, R0 + 6), (C0 + 13, R0 + 3)]


@unittest.skipIf(Uc is None or not shutil.which("nasm"), "needs unicorn and nasm")
class SquaresDrawingTests(unittest.TestCase):
    def test_built_with_the_loaders_numbers(self):
        """The header's fields and the bitmap's size are the Loader's (squares.py)."""
        scene = Marks([])
        sym = scene.sym
        self.assertEqual(sym["squares_on"] - sym["hdr"], squares.TSR_SQUARES_ON)
        self.assertEqual(sym["hdr"], 0)  # (the PSP is the 100h bytes before the header)
        import test_header_offsets
        equ = test_header_offsets.symbols()  # (with the EQUs)
        self.assertEqual(equ["SQ_MAP"], squares.SQ_MAP_PSP)
        self.assertEqual(equ["SQ_MAP_BYTES"], squares.MAP_BYTES)
        self.assertLessEqual(squares.SQ_MAP_PSP + squares.MAP_BYTES, squares.PSP_BYTES)
        self.assertGreaterEqual(squares.SQ_MAP_PSP, 0x5C)  # (from the FCBs on: nothing of DOS's to keep)
        self.assertEqual(equ["SQ_SIDE"], squares.SIDE)

    def test_crosses_on_the_view(self):
        """A cross of nine pixels in the middle of each marked square, lightened four times
        through LIGHT (fewer where it runs out of lighter colours), or, where LIGHT has no colour
        for the floor's (not the dust's ground), darkened four times through DARK; those off the
        view left out and those at its edge cut."""
        scene = Marks(MARKED)
        scene.floor(3, *CAM)
        self.assertEqual(scene.screen(), expected(MARKED))
        self.assertNotEqual(scene.screen(), expected([]))
        floor_ = expected([])
        changed = [(a, b) for a, b in zip(floor_, scene.screen()) if a != b]
        self.assertTrue(any(light(a) for a, _ in changed))  # (both kinds are in the scene's floor)
        self.assertTrue(any(not light(a) and b == dark(dark(dark(dark(a)))) for a, b in changed))

    def test_clipped_to_the_rectangle_drawn(self):
        """A rectangle's floor drawn again (a walker's): only the crosses' pixels inside it."""
        scene = Marks(MARKED)
        rect = (C0 * 16 + 5 * 16 + 7 - CAM[0], 40, C0 * 16 + 6 * 16 + 9 - CAM[0], 90)  # (through two crosses)
        scene.floor(3, rect[0], rect[1], rect[2] + 1, rect[3], *CAM)
        want = expected(MARKED, rect)
        self.assertEqual(scene.screen(), want)
        self.assertNotEqual(want, expected([]))
        self.assertNotEqual(want, expected(MARKED))

    def test_passes_over_what_is_outside(self):
        """Rows and squares outside what is drawn cost a few instructions each, not a cross's."""
        scene = Marks(MARKED)
        whole = scene.floor(3, *CAM)
        small = scene.floor(3, 300, 190, 320, 199, *CAM)  # (a corner with no cross in it)
        empty = Marks([]).floor(3, 300, 190, 320, 199, *CAM)
        self.assertLess(small - empty, 45 * len(MARKED))  # (the rows' tests and a square's: no cross's pixels)
        self.assertGreater(whole - small, 3000)

    def test_off(self):
        """SQUARES_ON 0: nothing drawn, whatever the bitmap holds."""
        scene = Marks(MARKED, squares_on=0)
        scene.floor(3, *CAM)
        self.assertEqual(scene.screen(), expected([]))

    def test_rings_keep_their_red(self):
        """The rings after the marks are drawn through RED as ever (RING_PX's table put back)."""
        with_marks, without = Marks([(C0 + 27, R0 + 28)], on=(0, 0, 1)), Marks([], on=(0, 0, 1), squares_on=0)
        with_marks.floor(3, *CAM)
        without.floor(3, *CAM)
        self.assertEqual(with_marks.screen(), without.screen())  # (that square is off the view)
        self.assertNotEqual(without.screen(), expected([]))  # (rings were drawn)
        self.assertEqual(struct.unpack("<H", with_marks.get("r_tab", 2))[0], with_marks.sym["FAR_RED"])

    def test_floor_pass_asked_for_the_marks_alone(self):
        """With shadows, dust and rings off, the marks alone have the floor routine's way back
        pointed at FLOOR_POST."""
        for on, busy in ((1, 1), (0, 0)):
            scene = Marks([], squares_on=on)
            scene.ds(0x2F44, struct.pack("<H", 1))  # (FLOOR_ON: the routine draws)
            args = (3,) + CAM
            sp = 0x800 - 2 * len(args) - 4 - 6
            scene.mu.mem_write(SS * 16 + sp, struct.pack("<3H", 0x602, CALLER, 0x0202) + struct.pack("<2H", 0x700, CALLER)
                               + struct.pack(f"<{len(args)}h", *args))
            scene.run(scene.sym["probe_floor_all"], 0x602, sp)
            self.assertEqual(scene.get("floor_busy", 1)[0], busy)


if __name__ == "__main__":
    unittest.main()
