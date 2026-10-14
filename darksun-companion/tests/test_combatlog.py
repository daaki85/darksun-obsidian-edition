import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dscompanion import combatlog as c

# the arena's opening show, as the dice log wrote it
FIGHT = """Round 1: Defiler 29, Rampager 29, Slig 27
    Defiler 29 = 20 + 4 (0-9 roll) +5 DEX, tie broken by 103 (0-199 roll)
Defiler's turn
Fireball damage: 9d6 = [4 + 6 + 1 + 6 + 1 + 4 + 5 + 4 + 1] = 32 (1d6 for each caster level: 9 at caster level 9)
Slig's saving throw vs Fireball from Defiler (spell): d20 = 11, needs 16 (25% to save) -> failed: full damage, 32
Rampager magic resistance 25% vs Fireball: d100 = 28 -> not resisted
Rampager's saving throw vs Fireball from Defiler (spell): d20 = 14, needs 8 (65% to save) -> saved: half damage, 13 of 27
  Slig takes 18 from Fireball, now 0/18 HP
Slig is killed
Dice: 1d6 = 3
Rampager's turn
Rampager attacks Defiler: d20 = 20 (natural 20), needs 16+ (25%), hits AC -13, target AC -9 -> HIT
    THAC0 7 = 7
  Rampager hits Defiler for 4: 2d6 = [1 + 3]
  Defiler now 14/18 HP (-4)
Defiler attacks Rampager with Bone Dagger (1d4): d20 = 11, only a 20 hits (5%), hits AC 8, target AC -4 -> miss
Defiler's saving throw vs Fear from Rampager (spell): d20 = 20 (natural 20) -> saved""".splitlines()
NAMES = {"Defiler": "monster", "Rampager": "monster", "Slig": "monster", "Gerakis": "member0"}


class FakeFont:
    """Every character 5 pixels wide, 9 high: ink on the top row, shadow on the second."""
    height = 9

    def glyph(self, ch):
        return 5, bytes([c.FONT_INK] * 5 + [c.FONT_SHADOW] * 5 + [0] * 35)


class LinesTests(unittest.TestCase):
    def setUp(self):
        self.log = c.Log()
        self.log.add(FIGHT)

    def test_kinds(self):
        self.assertEqual(c.line_kind("Round 2: Defiler 34"), "round")
        self.assertEqual(c.line_kind("Rampager's turn"), "turn")
        self.assertEqual(c.line_kind(FIGHT[4]), "save")
        self.assertEqual(c.line_kind(FIGHT[5]), "save")
        self.assertEqual(c.line_kind(FIGHT[11]), "hit")
        self.assertEqual(c.line_kind(FIGHT[15]), "miss")
        self.assertEqual(c.line_kind(FIGHT[12]), "detail")
        self.assertEqual(c.line_kind(FIGHT[13]), "damage")
        self.assertEqual(c.line_kind(FIGHT[3]), "damage")
        self.assertEqual(c.line_kind("Slig is killed"), "other")

    def test_not_the_fight(self):
        self.assertFalse(any(line.startswith("Dice:") for _, line in self.log.lines))

    def test_short(self):
        texts = [line.text for line in self.log.at(c.SHORT, NAMES)]
        self.assertEqual(texts, [
            "ROUND 1",
            "Defiler's turn",
            "Fireball damage: 9d6 = 32",
            "Slig's save vs Fireball: 11 vs 16, failed",
            "Rampager MR 25% vs Fireball: 28, not resisted",
            "Rampager's save vs Fireball: 14 vs 8, saved",
            "Slig takes 18 from Fireball, now 0/18 HP",
            "Slig is killed",
            "Rampager's turn",
            "Rampager attacks Defiler: 20 vs 16+ HIT, 4 damage (2d6)",  # the damage on the attack's line
            "Defiler now 14/18 HP (-4)",
            "Defiler attacks Rampager: 11 vs 20+ miss",
            "Defiler's save vs Fear: 20, saved",
        ])

    def test_least(self):
        texts = [line.text for line in self.log.at(c.MINIMAL, NAMES)]
        self.assertEqual(texts, [
            "ROUND 1",
            "Slig fails to save vs Fireball",
            "Rampager saves vs Fireball",
            "Slig takes 18 from Fireball, now 0/18 HP",
            "Slig is killed",
            "Rampager hits Defiler for 4",
            "Defiler misses Rampager",
            "Defiler saves vs Fear",
        ])

    def test_detail(self):
        lines = self.log.at(c.DETAIL, NAMES)
        self.assertEqual(len(lines), len(FIGHT) - 1)  # (all but the unlabelled die)
        self.assertEqual(lines[1].text, "Defiler 29 = 20 + 4 (0-9 roll) +5 DEX, tie broken by 103 (0-199 roll)")
        self.assertEqual(lines[1].depth, 2)
        self.assertEqual(lines[0].depth, 0)

    def test_sides(self):
        lines = {line.text: line.side for line in self.log.at(c.SHORT, NAMES)}
        self.assertEqual(lines["Rampager's turn"], "monster")
        self.assertIsNone(lines["ROUND 1"])
        self.assertIsNone(lines["Fireball damage: 9d6 = 32"])
        log = c.Log()
        log.add(["Gerakis attacks Slig: d20 = 5, needs 11+ (50%), hits AC 5, target AC 6 -> miss"])
        self.assertEqual(log.at(c.SHORT, NAMES)[0].side, "party")

    def test_percent_rolls(self):
        line = "Cilla hides in shadows: d100 = 85, needs 25 or less (50, halved in daylight) -> seen"
        self.assertEqual(c.shorten(line, c.SHORT), "Cilla hides in shadows: 85 vs 25 or less, seen")
        self.assertEqual(c.shorten(line, c.MINIMAL), "Cilla hides in shadows: seen")
        line = ("Cilla moves silently: d100 = 1, needs 57 or less -> unheard: their next attack this turn is "
                "from behind (a backstab with a weapon that can)")
        self.assertEqual(c.shorten(line, c.SHORT), "Cilla moves silently: 1 vs 57 or less, unheard")

    def test_damage_without_its_attack_keeps_its_own_line(self):
        log = c.Log()
        log.add(["  Rampager hits Defiler for 4: 2d6 = [1 + 3]"])
        self.assertEqual(log.at(c.SHORT, NAMES)[0].text, "Rampager hits Defiler for 4 damage (2d6)")
        self.assertEqual(log.at(c.MINIMAL, NAMES)[0].text, "Rampager hits Defiler for 4")

    def test_history_is_kept_to_its_length(self):
        log = c.Log()
        log.add([f"Slig is killed {n}" for n in range(c.HISTORY + 10)])
        self.assertEqual(len(log.lines), c.HISTORY)
        self.assertEqual(log.lines[0][1], "Slig is killed 10")


class HeaderTests(unittest.TestCase):
    def test_header(self):
        status = {"round": 2, "now": ("Gerakis", 30), "next": [("Cermak", 25), ("Cilla", 20)]}
        self.assertEqual(c.header(status), "Round 2: Gerakis, then Cermak, Cilla")
        self.assertEqual(c.header({"round": 3, "now": ("Slig", 1), "next": []}), "Round 3: Slig")
        self.assertEqual(c.header({"round": 3, "now": None, "next": [("Slig", 1)]}), "Round 3: then Slig")
        self.assertEqual(c.header(None), "")

    def test_fit(self):
        font = FakeFont()
        self.assertEqual(c.fit(font, "Round 2: Gerakis", 200), "Round 2: Gerakis")
        # (5 pixels a character: 32 in 160, the "..." in them)
        self.assertEqual(c.fit(font, "Round 2: Gerakis, then Cermak, Cilla", 160), "Round 2: Gerakis, then Cermak...")
        self.assertEqual(c.fit(font, "Round 2: Gerakis, then Cermak, Cilla", 155), "Round 2: Gerakis...")


class DrawingTests(unittest.TestCase):
    def test_coloured(self):
        self.assertEqual(c.coloured("Rampager attacks Defiler: 3 vs 16+ miss", "log miss", NAMES),
                         [("Rampager", "monster"), (" attacks ", "log miss"), ("Defiler", "monster"),
                          (": 3 vs 16+ miss", "log miss")])
        # a longer name first, a name only as a whole word
        self.assertEqual(c.coloured("Slig Leader hits Sligs", "log hit", {"Slig": "monster", "Slig Leader": "member1"}),
                         [("Slig Leader", "member1"), (" hits Sligs", "log hit")])

    def test_wrap(self):
        font = FakeFont()
        rows = c.wrap(font, [("aaaa bbbb cccc", "x")], 50, 30)
        self.assertEqual(["".join(t for t, _ in row) for row in rows], ["aaaa bbbb", "cccc"])
        rows = c.wrap(font, [("aaaaaaaaaaaa", "x")], 25, 25)  # a word too long for a row: cut
        self.assertEqual(["".join(t for t, _ in row) for row in rows], ["aaaaa", "aaaaa", "aa"])

    def test_draw(self):
        dac = bytes(range(256)) * 3
        ink = c.inks(dac)
        background = c.render(dac, ink)
        self.assertEqual(len(background), c.PANEL_W * c.PANEL_H)
        log = c.Log()
        log.add(FIGHT)
        lines = log.at(c.SHORT, NAMES)
        picture = c.draw(background, FakeFont(), ink, "Round 1: Defiler", lines, NAMES)
        self.assertEqual(len(picture), len(background))
        self.assertNotEqual(picture, background)
        # the last rows of the log at the well's foot: its last line's first letter at TEXT_X, in
        # the monster's colour, its pip before it
        rows = c.rows_of(FakeFont(), lines, NAMES)
        last = max(n for n, row in enumerate(rows) if row[0] is not None)
        self.assertEqual(rows[last][2][0], ("Defiler", "monster"))  # ("Defiler's save vs Fear: 20, saved")
        y = c.WELL[1] + 2 + (c.ROWS - (len(rows) - last)) * c.LINE_H
        self.assertEqual(picture[y * c.PANEL_W + c.TEXT_X], ink["monster"])
        self.assertEqual(picture[(y + 3) * c.PANEL_W + c.WELL[0] + 2], ink["monster"])
        # no font: the frame alone, the handle the whole bar
        self.assertEqual(c.draw(background, None, ink, "Round 1", lines, NAMES),
                         c.draw(background, None, ink, "", [], {}))


class FakeGuest:
    def __init__(self):
        self.mem = bytearray(0x10000)

    def read(self, addr, size):
        return bytes(self.mem[addr:addr + size])

    def write(self, addr, data):
        self.mem[addr:addr + len(data)] = data


class FakeGame:
    def __init__(self):
        self.guest = FakeGuest()


HDR = 0x1000


class ScrollingTests(unittest.TestCase):
    def test_scroll_to(self):
        self.assertIsNone(c.scroll_to(None, 50))
        self.assertEqual(c.scroll_to(10, 50), 10)
        self.assertEqual(c.scroll_to(-4, 50), 0)
        self.assertIsNone(c.scroll_to(50 - (c.ROWS - 1), 50))  # the last rows: following again
        self.assertIsNone(c.scroll_to(0, 3))  # (all of it in view)

    def test_handle(self):
        top, height = c.handle(None, 4)
        self.assertEqual((top, height), (c.TRACK[1] + 1, c.TRACK_H))  # all in view: the whole bar
        top, height = c.handle(None, 60)  # following: at the foot
        self.assertEqual(top + height, c.TRACK[1] + 1 + c.TRACK_H)
        self.assertEqual(c.handle(0, 60)[0], c.TRACK[1] + 1)  # the oldest: at the top
        self.assertGreaterEqual(c.handle(0, 1000)[1], c.HANDLE_MIN)

    def press(self, panel, game, x, y, held=1, at=None):
        hits = c.struct.unpack_from("<H", game.guest.mem, HDR + c.TSR_MOUSE + 6)[0] + 1
        mx, my = at or (x, y)
        game.guest.mem[HDR + c.TSR_MOUSE:HDR + c.TSR_MOUSE + 12] = c.struct.pack(
            "<hhHHhh", mx, my, held, hits, x, y)
        panel.mouse(game, HDR)

    def test_mouse(self):
        panel, game = c.Panel(), FakeGame()
        panel._rows = 60
        panel.mouse(game, HDR)  # (the count as it stands: no press)
        bar_x = c.PANEL_X0 + (c.TRACK[0] + c.TRACK[2]) // 2
        top, height = c.handle(None, 60)
        self.press(panel, game, bar_x, c.PANEL_Y0 + top - 3)  # above the handle: a page back
        self.assertEqual(panel.first, 60 - c.ROWS - (c.ROWS - 1))
        self.assertEqual(panel._back_rows, 60)
        # the handle dragged to the top: the oldest rows
        top, height = c.handle(panel.first, 60)
        self.press(panel, game, bar_x, c.PANEL_Y0 + top + 1)
        self.press(panel, game, bar_x, c.PANEL_Y0 + top + 1, at=(bar_x, c.PANEL_Y0))
        self.assertEqual(panel.first, 0)
        # ... and to the foot: following again
        game.guest.mem[HDR + c.TSR_MOUSE + 2:HDR + c.TSR_MOUSE + 4] = c.struct.pack("<h", c.PANEL_Y0 + c.PANEL_H)
        panel.mouse(game, HDR)
        self.assertIsNone(panel.first)
        # let go: moving no longer drags
        self.press(panel, game, bar_x, c.PANEL_Y0 + c.TRACK[1] + 2)  # (a page back, the handle at the foot)
        first = panel.first
        game.guest.mem[HDR + c.TSR_MOUSE + 4:HDR + c.TSR_MOUSE + 6] = bytes(2)
        panel.mouse(game, HDR)
        game.guest.mem[HDR + c.TSR_MOUSE + 2:HDR + c.TSR_MOUSE + 4] = c.struct.pack("<h", c.PANEL_Y0)
        panel.mouse(game, HDR)
        self.assertEqual(panel.first, first)
        # the chip: the newest
        x0, y0, x1, y1 = c.chip_rect()
        self.press(panel, game, c.PANEL_X0 + x0 + 5, c.PANEL_Y0 + y0 + 3, held=0)
        self.assertIsNone(panel.first)

    def test_wheel(self):
        panel = c.Panel()
        panel._rows = 40
        panel.wheel(1)
        self.assertEqual(panel.first, 40 - c.ROWS - c.WHEEL_ROWS)
        panel.wheel(-5)
        self.assertIsNone(panel.first)
        panel.pointer = (c.PANEL_X0 + 5, c.PANEL_Y0 + 5)
        self.assertTrue(panel.over())
        panel.pointer = (c.PANEL_X0 - 1, c.PANEL_Y0 + 5)
        self.assertFalse(panel.over())

    def test_chip(self):
        dac = bytes(range(256)) * 3
        ink = c.inks(dac)
        log = c.Log()
        log.add(FIGHT)
        lines = log.at(c.DETAIL, NAMES)
        picture = c.draw(c.render(dac, ink), FakeFont(), ink, "", lines, NAMES, 0, 3)
        x0, y0, x1, y1 = c.chip_rect()
        self.assertEqual(picture[y0 * c.PANEL_W + x0], ink["outline"])
        self.assertEqual(picture[(y0 + 1) * c.PANEL_W + x0 + 1], ink["stone"])


if __name__ == "__main__":
    unittest.main()
