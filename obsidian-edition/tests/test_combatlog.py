import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import combatlog as c

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

    def test_rolls_only(self):
        """Out of a fight (the strip's), only lines with a roll, and those under them."""
        log = c.Log()
        log.add(["Cilla starts with more gear: Belt, Boots", "Cilla hides in shadows: d100 = 81, needs 25 or "
                 "less -> seen", "  (her cloak's +10)", "Character creation: STR 3d6 = 12", "Gerakis HP: 1d12 = 7"],
                rolls_only=True)
        self.assertEqual([line for _, line in log.lines], [
            "Cilla hides in shadows: d100 = 81, needs 25 or less -> seen", "  (her cloak's +10)",
            "Gerakis HP: 1d12 = 7"])

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
        self.assertEqual(len(lines), len(FIGHT))  # (all but the unlabelled die, the round's order a line of its own)
        self.assertEqual(lines[0], c.Line("round", None, "ROUND 1", 0))  # (the order after the rule)
        self.assertEqual(lines[1], c.Line("detail", None, "Defiler 29, Rampager 29, Slig 27", 1))
        self.assertEqual(lines[2].text, "Defiler 29 = 20 + 4 (0-9 roll) +5 DEX, tie broken by 103 (0-199 roll)")
        self.assertEqual(lines[2].depth, 2)

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


class PlanarTests(unittest.TestCase):
    def test_planar(self):
        """Each row its four planes' bytes in turn (DSCLOG's PANEL_BLIT copies a plane's run whole)."""
        picture = bytes(range(16))  # two rows of 8
        self.assertEqual(c.planar(picture, 8), bytes((0, 4, 1, 5, 2, 6, 3, 7, 8, 12, 9, 13, 10, 14, 11, 15)))


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


    def test_strip_scrolled_back(self):
        """The strip's one row: scrolled back it still shows a line (the "Latest" chip in its
        header instead), the handle within its bar, the wheel a line a notch."""
        dac = bytes(range(256)) * 3
        ink = c.inks(dac)
        g = c.STRIP
        log = c.Log()
        log.add(FIGHT)
        lines = log.at(c.DETAIL, NAMES)
        rows = c.rows_of(FakeFont(), lines, NAMES, g)
        self.assertEqual(c.visible(0, g), 1)
        self.assertEqual(c.scroll_to(0, len(rows), g), 0)
        top, height = c.handle(0, len(rows), g)
        self.assertGreaterEqual(top, g.track[1] + 1)
        self.assertLessEqual(top + height, g.track[1] + 1 + g.track_h)
        background = c.render(dac, ink, g)
        picture = c.draw(background, FakeFont(), ink, "Round 1", lines, NAMES, 0, 3, g)
        row = picture[g.text_y * g.width:(g.text_y + c.LINE_H) * g.width]
        self.assertNotEqual(row, background[g.text_y * g.width:(g.text_y + c.LINE_H) * g.width])
        self.assertIn(ink["outline"], picture[1 * g.width + 200:1 * g.width + g.track[0] - 1])  # (the chip)
        panel = c.Panel()
        panel.strip, panel._rows = True, len(rows)
        panel.wheel(1)
        self.assertEqual(panel.first, len(rows) - 2)
        panel.wheel(-1)
        self.assertIsNone(panel.first)  # (back at the newest: following again)


class StatesTests(unittest.TestCase):
    def setUp(self):
        self.panel, self.game = c.Panel(), FakeGame()
        self.panel.mouse(self.game, HDR)

    def press(self, px, py):
        """A press at PX, PY in the panel as it is now."""
        hits = c.struct.unpack_from("<H", self.game.guest.mem, HDR + c.TSR_MOUSE + 6)[0] + 1
        x, y = c.PANEL_X0 + px, self.panel.g.top + py
        self.game.guest.mem[HDR + c.TSR_MOUSE:HDR + c.TSR_MOUSE + 12] = c.struct.pack("<hhHHhh", x, y, 0, hits, x, y)
        self.panel.mouse(self.game, HDR)

    def test_sizes(self):
        for g in c.SIZES.values():
            self.assertEqual(g.top + g.height, c.PANEL_Y0 + c.PANEL_H)  # (the foot stays)
            self.assertLessEqual(g.height, 130)  # (DSCLOG's PANEL_H_MOST)
            if g.rows:
                self.assertLessEqual(g.text_y + g.rows * c.LINE_H, g.well[3] + 1)
        self.assertEqual(c.SIZES[c.DOCKED].well, c.WELL)

    def test_buttons(self):
        plus, minus = c.PLUS_X0 + 3, c.MINUS_X0 + 3
        self.press(plus, 5)
        self.assertEqual(self.panel.size, c.EXPANDED)
        self.press(plus, 5)  # (as big as it gets)
        self.assertEqual(self.panel.size, c.EXPANDED)
        self.press(minus, 5)
        self.press(minus, 5)
        self.assertEqual(self.panel.size, c.COLLAPSED)
        self.press(minus, 5)
        self.assertEqual(self.panel.size, c.COLLAPSED)

    def test_level_chip(self):
        x0, y0, x1, y1 = c.level_rect(None)
        self.assertEqual(self.panel.level, c.SHORT)
        self.press(x0 + 2, y0 + 2)
        self.assertEqual(self.panel.level, c.DETAIL)
        self.press(x0 + 2, y0 + 2)
        self.assertEqual(self.panel.level, c.MINIMAL)

    def test_filters(self):
        self.panel.font = FakeFont()
        self.panel.resize(c.EXPANDED)
        rects = dict(c.filter_rects(FakeFont(), self.panel.g))
        x0, y0, x1, y1 = rects["saves"]
        self.press(x0 + 2, y0 + 2)
        self.assertEqual(self.panel.filter, "saves")
        self.panel.resize(c.DOCKED)  # (no filters' row: all of it again)
        self.assertEqual(self.panel.filter, "all")
        log = c.Log()
        log.add(FIGHT)
        lines = log.at(c.SHORT, NAMES)
        self.assertTrue(all(ln.kind in ("save", "round") for ln in c.filtered(lines, "saves")))
        self.assertIn("Slig is killed", [ln.text for ln in c.filtered(lines, "damage")])
        self.assertEqual(c.filtered(lines, "party"), [ln for ln in lines if ln.kind == "round"])

    def test_l_key(self):
        """L with the panel shown hides it (the Loader shows it again on the next L)."""
        self.panel.resize(c.EXPANDED)
        self.panel.open = True
        keys = HDR + c.TSR_KEYS
        self.panel.mouse(self.game, HDR)
        count = c.struct.unpack_from("<H", self.game.guest.mem, keys)[0]
        self.game.guest.mem[keys:keys + 2] = c.struct.pack("<H", count + 1)
        self.panel.mouse(self.game, HDR)
        self.assertFalse(self.panel.open)
        self.assertEqual(self.panel.size, c.EXPANDED)  # (its size kept for next time)
        self.assertEqual(self.panel.keys(self.game, HDR), 0)  # (counted once)

    def test_l_label(self):
        """The header's L, left of the level chip: a click on it hides the panel, as L does."""
        self.panel.mouse(self.game, HDR)
        x0, y0, x1, y1 = c.key_rect(self.panel.font, self.panel.g)
        self.assertLess(x1, c.level_rect(self.panel.font, self.panel.g)[0])
        self.panel.open = True
        self.press((x0 + x1) // 2, (y0 + y1) // 2)
        self.assertFalse(self.panel.open)

    def test_no_a_button(self):
        """The header has no A any more (the game's A key turns animations on and off, so a button
        A read as a key it isn't): left of the L is header text."""
        self.assertFalse(hasattr(c, "arena_rect"))
        self.assertFalse(hasattr(self.panel, "arena"))

    def test_arena_count_in_the_header(self):
        """Given a count (between fights in the slave pens and the arena), the header says it, docked
        or expanded; collapsed keeps the newest line, and without a count the header is the round."""
        g = self.game.guest
        g.mem[HDR + c.TSR_PANEL_SEG:HDR + c.TSR_PANEL_SEG + 2] = c.struct.pack("<H", 0x800)
        g.mem[HDR + c.TSR_HDR_OFF:HDR + c.TSR_HDR_OFF + 2] = c.struct.pack("<H", 0)
        g.mem[HDR + c.TSR_DAC:HDR + c.TSR_DAC + 2] = c.struct.pack("<H", 0x2000)
        self.panel.log.add(FIGHT)
        for size in (c.DOCKED, c.EXPANDED):
            self.panel.resize(size)
            self.panel.update(self.game, HDR, True, 1, "", NAMES, 2)
            self.assertEqual(self.panel._shown[1], "Arena fights: 2")
        self.panel.resize(c.COLLAPSED)
        self.panel.update(self.game, HDR, True, 1, "", NAMES, 2)
        self.assertNotEqual(self.panel._shown[1], "Arena fights: 2")
        self.panel.resize(c.DOCKED)
        self.panel.update(self.game, HDR, True, 1, "Round 1", NAMES)
        self.assertEqual(self.panel._shown[1], "Round 1")
        self.assertEqual(c.arena_line(None), "Arena fights: ?")
        self.assertEqual(c.ARENA_REGIONS, (0x29, 0x2A))

    def test_update_writes_the_size(self):
        g = self.game.guest
        g.mem[HDR + c.TSR_PANEL_SEG:HDR + c.TSR_PANEL_SEG + 2] = c.struct.pack("<H", 0x800)
        g.mem[HDR + c.TSR_HDR_OFF:HDR + c.TSR_HDR_OFF + 2] = c.struct.pack("<H", 0)
        g.mem[HDR + c.TSR_DAC:HDR + c.TSR_DAC + 2] = c.struct.pack("<H", 0x2000)
        self.panel.resize(c.COLLAPSED)
        self.panel.log.add(FIGHT)
        self.panel.update(self.game, HDR, True, 1, "Round 1", NAMES)
        self.assertEqual(c.struct.unpack_from("<HH", g.mem, HDR + c.TSR_PANEL_TOP),
                         (c.SIZES[c.COLLAPSED].top, c.SIZES[c.COLLAPSED].height))
        self.assertEqual(c.struct.unpack_from("<H", g.mem, HDR + c.TSR_PANEL_NEW)[0], 1)


    def test_the_strip(self):
        """With the strip's patch in the game's code: the strip, 320 x 22 at row 200, one row."""
        g = self.game.guest
        g.mem[HDR + c.TSR_PANEL_SEG:HDR + c.TSR_PANEL_SEG + 2] = c.struct.pack("<H", 0x800)
        g.mem[HDR + c.TSR_HDR_OFF:HDR + c.TSR_HDR_OFF + 2] = c.struct.pack("<H", 0)
        g.mem[HDR + c.TSR_DAC:HDR + c.TSR_DAC + 2] = c.struct.pack("<H", 0x2000)
        self.game.ds = c.DGROUP_SEG + 0x10
        at = 0x100 + c.STRIP_AT
        g.mem[at:at + 2] = c.STRIP_INT
        self.panel.log.add(FIGHT)
        self.panel.update(self.game, HDR, True, 1, "Round 1", NAMES)
        self.assertTrue(self.panel.strip)
        self.assertTrue(self.panel.over())  # (the wheel scrolls it wherever the pointer is)
        self.assertEqual(c.struct.unpack_from("<HH", g.mem, HDR + c.TSR_PANEL_TOP), (200, 22))
        g0 = c.STRIP
        self.assertEqual(len(c.render(bytes(768), None, g0)), 320 * 22)
        self.assertLessEqual(g0.text_y + g0.rows * c.LINE_H, g0.well[3] + 1)  # (the rows within the well)

    def test_strip_between_fights(self):
        """The strip with no header (between fights): the row before the newest in its top line."""
        dac = bytes(range(256)) * 3
        ink = c.inks(dac)
        g = c.STRIP
        background = c.render(dac, ink, g)
        log = c.Log()
        log.add(FIGHT)
        lines = log.at(c.SHORT, NAMES)
        rows = c.rows_of(FakeFont(), lines, NAMES, g)
        empty = c.draw(background, FakeFont(), ink, "", lines[:0], NAMES, None, 0, g)
        with_top = c.draw(background, FakeFont(), ink, "", lines, NAMES, None, 0, g)
        header = slice(g.header_y * g.width, (g.header_y + 1) * g.width)
        self.assertEqual(empty[header], background[header])
        self.assertNotEqual(with_top[header], background[header])  # (the row before: its letters)
        self.assertGreater(len(rows), 1)


if __name__ == "__main__":
    unittest.main()
