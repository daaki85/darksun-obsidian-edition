"""The squares a party member can still walk to this turn (dsloader/squares.py): the game's rules
of movement in a fight, the bitmap DSCLOG is given, and its upkeep."""
import struct
import unittest

from dsloader import dust, game, shadows, squares

HDR = 0x9000
DS = 0x5000
LOAD = DS - game.DGROUP
MAP_AT = 0x60000
FAR_SEG = 0x8000
SQ_AT, LIGHT_OFF, DAC_OFF = HDR - squares.PSP_BYTES + squares.SQ_MAP_PSP, 0x300, 0x500  # (SQ_MAP: DSCLOG's PSP)
W = squares.MAP_W


def grid(barred=(), value=0xC0):
    out = bytearray(W * squares.MAP_H)
    for col, row in barred:
        out[row * W + col] = value
    return out


class ReachTests(unittest.TestCase):
    def test_open_floor(self):
        """10 a straight step, 14 a diagonal one, the shortest way within the points."""
        r = squares.reach(grid(), 50, 50, 60)
        self.assertIn((56, 50), r)  # (six straight: 60)
        self.assertNotIn((57, 50), r)
        self.assertIn((55, 51), r)  # (a diagonal and four straight: 54)
        self.assertNotIn((56, 51), r)  # (64)
        self.assertIn((53, 53), r)  # (three diagonal: 42)
        self.assertIn((54, 53), r)  # (52)
        self.assertNotIn((55, 53), r)  # (62)
        self.assertNotIn((50, 50), r)  # (its own square)

    def test_last_step_begun_with_ten(self):
        """A step is taken with 10 points or more left, whatever it costs: a run of diagonal steps
        alone ends on one begun with 10 to 13 (the game's route takes its diagonal steps first, so
        no other way's last step is diagonal)."""
        r = squares.reach(grid(), 50, 50, 24)
        self.assertIn((52, 52), r)  # (28 for 24 points: the second step begun with 10)
        self.assertIn((48, 48), r)
        self.assertIn((52, 51), r)  # (a diagonal and a straight step: 24)
        r = squares.reach(grid(), 50, 50, 23)
        self.assertNotIn((52, 52), r)  # (the second step would begin with 9)
        self.assertNotIn((52, 51), r)
        self.assertEqual(squares.reach(grid(), 50, 50, 10) - {(49, 49), (51, 49), (49, 51), (51, 51)},
                         {(50, 49), (51, 50), (50, 51), (49, 50)})  # (10: every square beside it)
        self.assertEqual(len(squares.reach(grid(), 50, 50, 10)), 8)

    def test_diagonal_run_stops_at_what_bars_it(self):
        r = squares.reach(grid([(52, 52)]), 50, 50, 24)
        self.assertEqual(r & {(52, 52), (53, 53)}, set())
        self.assertIn((51, 51), r)

    def test_no_points_no_squares(self):
        self.assertEqual(squares.reach(grid(), 50, 50, 9), set())
        self.assertEqual(squares.reach(grid(), 50, 50, 0), set())

    def test_what_bars_a_square(self):
        """Bit 40h bars (walls and shut doors 192 and up, things 64, figures 96); edges without
        it (1-31) and the line test's bit 80h alone don't."""
        for value, barred in ((0xC0, True), (0x40, True), (0x60, True), (0x45, True), (0xCD, True),
                              (0x01, False), (0x1F, False), (0x80, False), (0x20, False)):
            r = squares.reach(grid([(51, 50)], value), 50, 50, 10)
            self.assertEqual((51, 50) not in r, barred, hex(value))

    def test_round_a_wall(self):
        """A wall across the way: round its end, and the squares behind cost what that costs."""
        wall = [(52, row) for row in range(45, 53)]  # (its south end at row 52)
        r = squares.reach(grid(wall), 50, 50, 60)
        self.assertNotIn((52, 50), r)
        self.assertIn((53, 53), r)  # (51,51 51,52 52,53 53,53: 14 + 10 + 14 + 10 = 48)
        self.assertIn((53, 52), r)  # (... 52,53 and a diagonal step back north: 52)
        self.assertNotIn((53, 51), r)  # (62)
        self.assertNotIn((53, 50), r)
        open_floor = squares.reach(grid(), 50, 50, 60)
        self.assertIn((53, 50), open_floor)

    def test_corner_cut(self):
        """A diagonal step needs only the square stepped into free (the game tests no other)."""
        r = squares.reach(grid([(51, 50), (50, 51)]), 50, 50, 20)
        self.assertIn((51, 51), r)

    def test_map_edge(self):
        r = squares.reach(grid(), 0, 0, 20)
        self.assertEqual(r, {(1, 0), (2, 0), (0, 1), (0, 2), (1, 1)})
        r = squares.reach(grid(), 127, 97, 10)
        self.assertEqual(r, {(126, 97), (127, 96), (126, 96)})

    def test_bitmap(self):
        """The origin (the square 16 left of and above the member's, kept on the map), then a bit a
        square, a row's leftmost its bit 0."""
        bits = squares.bitmap({(50, 50), (51, 50), (34, 34), (65, 65), (66, 50), (33, 50)}, 50, 50)
        self.assertEqual(len(bits), squares.MAP_BYTES)
        self.assertEqual(bits[:2], bytes([34, 34]))
        rows = struct.unpack("<32I", bits[2:])
        self.assertEqual(rows[16], 1 << 16 | 1 << 17)
        self.assertEqual(rows[0], 1)
        self.assertEqual(rows[31], 1 << 31)
        self.assertEqual(sum(bin(r).count("1") for r in rows), 4)  # (the two outside it left out)
        self.assertEqual(squares.bitmap(set(), 3, 2)[:2], bytes([0, 0]))
        self.assertEqual(squares.bitmap(set(), 126, 96)[:2], bytes([128 - 32, 98 - 32]))


class Guest:
    def __init__(self):
        self.mem = bytearray(0x110000)
        self.writes = []

    def read(self, at, n):
        return bytes(self.mem[at:at + n])

    def write(self, at, data):
        self.mem[at:at + len(data)] = data
        self.writes.append(at)


class Game:
    """A fight: party member TURN on square (50, 50) with POINTS, creature record TURN."""

    def __init__(self, points=60, flags=0x3FF, turn=1):
        self.guest, self.ds, self.load_seg = Guest(), DS, LOAD
        self.turn, self.fight = turn, True
        mem = self.guest.mem
        struct.pack_into("<HH", mem, DS * 16 + squares.WALK_MAP, MAP_AT & 15, MAP_AT >> 4)
        self.place(turn, 50, 50)
        self.points(points, flags)
        struct.pack_into("<H", mem, HDR + squares.TSR_FAR_SEG, FAR_SEG)
        struct.pack_into("<HH", mem, HDR + squares.TSR_LIGHT, LIGHT_OFF, DAC_OFF)
        for i in range(256):  # a palette of greys and browns
            mem[FAR_SEG * 16 + DAC_OFF + i * 3:FAR_SEG * 16 + DAC_OFF + i * 3 + 3] = bytes(
                [i % 64, (i * 3 // 4) % 64, (i // 2) % 64])

    def place(self, thing, col, row):
        struct.pack_into("<HH", self.guest.mem, DS * 16 + game.POSITIONS + thing * 32, col * 16 + 8, row * 16 + 8)

    def points(self, points, flags=0x3FF):
        at = (LOAD + squares.POINTS_SEG) * 16 + self.turn * 2
        struct.pack_into("<h", self.guest.mem, at + squares.POINTS_OFF, points)
        struct.pack_into("<H", self.guest.mem, at + squares.FLAGS_OFF, flags)

    def bar(self, col, row, value=0x60):
        self.guest.mem[MAP_AT + row * W + col] = value

    def in_combat(self):
        return self.fight

    def whose_turn(self):
        return self.turn

    def combatant_creature(self, thing):
        return thing

    def on(self):
        return struct.unpack("<H", self.guest.read(HDR + squares.TSR_SQUARES_ON, 2))[0]

    def marked(self):
        data = self.guest.read(SQ_AT, squares.MAP_BYTES)
        out = set()
        for bit in range(squares.SIDE * squares.SIDE):
            if data[2 + bit // 8] >> bit % 8 & 1:
                out.add((data[0] + bit % squares.SIDE, data[1] + bit // squares.SIDE))
        return out

    def redraw_asked(self):
        asked = struct.unpack("<H", self.guest.read(HDR + shadows.TSR_VIEW_REDRAW, 2))[0]
        self.guest.write(HDR + shadows.TSR_VIEW_REDRAW, b"\0\0")
        return bool(asked)


class MoverTests(unittest.TestCase):
    def test_mover(self):
        gd = Game(points=70)
        self.assertEqual(squares.mover(gd), (50, 50, 70))
        gd.points(70, 0x3FE)  # (the "can walk" bit off: Move run out, or held)
        self.assertEqual(squares.mover(gd), (50, 50, 0))
        gd.turn = 17  # (an enemy's turn)
        self.assertIsNone(squares.mover(gd))
        gd.turn, gd.fight = 1, False
        self.assertIsNone(squares.mover(gd))


class UpkeepTests(unittest.TestCase):
    def test_marks_follow_the_member(self):
        gd, s = Game(points=20), squares.Squares()
        gd.bar(51, 50)  # (an ally beside it)
        s.update(gd, HDR, True, 1)
        self.assertEqual(gd.on(), 1)
        self.assertEqual(gd.marked(), squares.reach(squares.walk_map(gd), 50, 50, 20))
        self.assertNotIn((51, 50), gd.marked())
        self.assertIn((48, 50), gd.marked())
        self.assertTrue(gd.redraw_asked())
        s.update(gd, HDR, True, 1)  # (nothing changed: nothing written, no redraw)
        self.assertFalse(gd.redraw_asked())
        before = gd.marked()
        gd.place(1, 49, 50)  # (a step west: 10 left)
        gd.points(10)
        s.update(gd, HDR, True, 1)  # (walking: the marks left alone, the view not drawn again)
        self.assertEqual(gd.marked(), before)
        self.assertFalse(gd.redraw_asked())
        s.update(gd, HDR, True, 1)  # (standing: the marks from where it stands)
        self.assertEqual(gd.marked(), squares.reach(squares.walk_map(gd), 49, 50, 10))
        self.assertTrue(gd.redraw_asked())
        gd.points(0, 0x3FE)  # (Move run out: the map empty, still on until the turn passes)
        s.update(gd, HDR, True, 1)
        s.update(gd, HDR, True, 1)
        self.assertEqual(gd.marked(), set())
        self.assertTrue(gd.redraw_asked())

    def test_off_out_of_the_members_turn(self):
        gd, s = Game(), squares.Squares()
        s.update(gd, HDR, True, 1)
        self.assertEqual(gd.on(), 1)
        gd.redraw_asked()
        gd.turn = 20
        s.update(gd, HDR, True, 1)
        self.assertEqual(gd.on(), 0)
        self.assertTrue(gd.redraw_asked())
        s.update(gd, HDR, True, 1)
        self.assertFalse(gd.redraw_asked())
        gd.turn = 2
        gd.place(2, 60, 60)
        gd.points(30)
        s.update(gd, HDR, True, 1)
        self.assertEqual(gd.on(), 1)
        self.assertIn((63, 60), gd.marked())

    def test_switched_off(self):
        gd, s = Game(), squares.Squares()
        gd.guest.write(HDR + squares.TSR_SQUARES_ON, b"\x01\x00")  # (left on by another Loader)
        s.update(gd, HDR, False, 1)
        self.assertEqual(gd.on(), 0)
        self.assertTrue(gd.redraw_asked())
        gd.guest.writes.clear()
        s.update(gd, HDR, False, 1)
        self.assertEqual(gd.guest.writes, [])  # (off: nothing more touched)
        s.update(gd, HDR, True, 1)
        s.update(gd, HDR, False, 1)
        self.assertEqual(gd.on(), 0)

    def test_light_table(self):
        """LIGHT (the dust's table) made from DSCLOG's palette when the palette is read again."""
        gd, s = Game(), squares.Squares()
        s.update(gd, HDR, True, 0)  # (no palette read yet: no table)
        far = FAR_SEG * 16
        self.assertEqual(gd.guest.read(far + LIGHT_OFF, 256), bytes(256))
        s.update(gd, HDR, True, 1)
        want = dust.light_table(gd.guest.read(far + DAC_OFF, 768))
        self.assertEqual(gd.guest.read(far + LIGHT_OFF, 256), want)
        gd.guest.mem[far + DAC_OFF + 300] ^= 0x15
        s.update(gd, HDR, True, 1)  # (the same count: not made again)
        self.assertEqual(gd.guest.read(far + LIGHT_OFF, 256), want)
        s.update(gd, HDR, True, 2)
        self.assertEqual(gd.guest.read(far + LIGHT_OFF, 256), dust.light_table(gd.guest.read(far + DAC_OFF, 768)))

    def test_no_walk_map(self):
        gd, s = Game(), squares.Squares()
        struct.pack_into("<HH", gd.guest.mem, DS * 16 + squares.WALK_MAP, 0, 0)
        s.update(gd, HDR, True, 1)
        self.assertEqual(gd.on(), 0)


if __name__ == "__main__":
    unittest.main()
