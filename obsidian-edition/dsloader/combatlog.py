"""The combat log's panel in the game (DSCLOG's PANEL), drawn and kept up by the Loader.

The Loader draws the panel, a picture of PANEL_W x PANEL_H palette indices (render), and puts it
in the memory block DSCLOG keeps for it (TSR_PANEL_SEG); DSCLOG puts the picture over the map,
bottom right, from the game's main loop and after each rectangle of the view the game draws again
(the map is drawn straight into the screen on show, a rectangle at a time). The Loader turns it on
in a fight (TSR_PANEL_ON) and off after, when DSCLOG has the view drawn again without it.

The picture is in the area's own colours: the game's stone (palette.py) matched to the nearest of
the palette DSCLOG last read (for the shadows: shadows.Shadows.palettes), among the colours the
game doesn't animate, and drawn again when that palette changes or the log has new lines. The
frame is the stone of the game's status box, speckled; the well, where the log's lines go,
mottled like the game's dialogue window, in darker shades.

The lines are the dice log's own (DiceLog.lines), from the fight (Log): in detail all of them, in
short a line for each attack, saving throw and spell's damage with its dice, at the least what came
of them. They are in the game's font (art.Font), in the Loader's colours for their kind
(palette.LOG_COLOURS) with the names in the party's and the monsters' colours, a filled pip before
a party member's line and a hollow one before a monster's, long lines wrapped with a hanging
indent. Above them the round, who is acting and who is next. See docs/combat-log/HANDOFF.md.
"""

import re
import struct
from collections import deque
from typing import Deque, Dict, List, NamedTuple, Optional, Sequence, Tuple

from . import palette

TSR_HDR_OFF = 20  # DSCLOG's header: where it is in DSCLOG's segment
TSR_DAC = 238  # ... the offset of DAC, the palette as DSCLOG last read it (768 values, 0-63)
TSR_PANEL_ON, TSR_PANEL_SEG, TSR_PANEL_NEW = 326, 328, 330  # ... the panel shown; its picture; a new one
PANEL_W, PANEL_H = 180, 78  # (DSCLOG's PANEL_W, PANEL_H)
PANEL_X0, PANEL_Y0 = 136, 120  # (DSCLOG's: where on the screen)
FIRST, LAST = 16, 223  # the palette's colours the game doesn't animate (DSCLOG's DARK_FIRST, DARK_LAST)
FONT_INK, FONT_SHADOW = 254, 20  # (art.FONT_INK, FONT_SHADOW: the font's pixels)

# the detail levels (the Options tab's combat_log_level)
MINIMAL, SHORT, DETAIL = "minimal", "short", "detail"
HISTORY = 200  # lines kept

RGB = Tuple[int, int, int]
# the picture's colours
COLOURS = {
    "outline": palette.SHADOW, "light": palette.EDGE_LIT, "stone": palette.BUTTON, "dark": palette.STONE,
    "grain_hi": "#8A8AA2", "grain_lo": "#5F5F78",  # the stone's speckles, as the status box's
    "handle": palette.EDGE_LIT,
    # the well: four shades of the deep blue-grey, mottled (palette.DEEP the most of it)
    "well0": "#262640", "well1": "#2C2C48", "well2": palette.DEEP, "well3": "#3A3A5A",
    "shadow": "#101018",  # the letters' shadow
    "text": palette.PALE, "monster": palette.MONSTER_COLOUR,
    **{f"log {k}": v for k, v in palette.LOG_COLOURS.items()},
    **{f"member{n}": c for n, c in enumerate(palette.PARTY_COLOURS)},
}
WELL = (4, 15, PANEL_W - 5, PANEL_H - 5)  # x0, y0, x1, y1 (inclusive), in the picture
GRAIN_HI_N, GRAIN_LO_N = 32, 32  # (of 256: the stone's pixels speckled lighter, darker)
LINE_H = 9  # the font's height, its shadow in it
ROWS = 6  # lines in the well
TEXT_X = WELL[0] + 7  # where the lines start (after the pip) ...
TEXT_RIGHT = WELL[2] - 9  # ... and end (before the scrollbar)
INDENT = 8  # a wrapped line's rows after its first, and each level of a detail line
HEADER_X, HEADER_Y = 4, 2
TSR_MOUSE = 332  # DSCLOG's header: the pointer (x, y), the left button held after a press on the
#   panel, the presses on it counted and where the last was (x, y): six words, game pixels
TRACK = (WELL[2] - 6, WELL[1] + 1, WELL[2] - 1, WELL[3] - 1)  # the scrollbar: x0, y0, x1, y1
HANDLE_X0, HANDLE_X1 = TRACK[0] + 1, TRACK[2] - 1
TRACK_H = TRACK[3] - TRACK[1] - 1  # (the handle's room, a pixel in from each end)
HANDLE_MIN = 8
WHEEL_ROWS = 3  # rows a notch of the mouse wheel scrolls
TSR_PANEL_TOP = 344  # DSCLOG's header: the panel's top on the screen and its height (two words)
TSR_KEYS = 348  # ... L pressed on the map with the panel shown, counted


class Line(NamedTuple):
    kind: str  # palette.LOG_COLOURS's
    side: Optional[str]  # "party", "monster": whose line (its pip), or None
    text: str
    depth: int = 0  # a detail line's indent (the log's leading spaces, in twos)


def line_kind(line: str) -> str:
    """A dice log line's kind, for its colour (as the Loader's log shows it)."""
    return ("round" if line.startswith(("Round ", "Initiative: ")) else
            "turn" if line.endswith("'s turn") else
            "save" if "'s saving throw vs " in line or " magic resistance " in line else
            "hit" if "-> HIT" in line else
            "miss" if "-> miss" in line else
            "detail" if line.startswith("    ") else
            "damage" if line.startswith("  ") or " damage: " in line else "other")


# The dice log's lines, as they are
ATTACK = re.compile(r"(?P<who>.+?) attacks (?P<target>.+?)(?: with .+?)?: d20 = (?P<d20>\d+)(?: \(natural \d+\))?, "
                    r"(?:needs (?P<need>-?\d+)\+|only a 20 hits)(?: \([^)]*\))?.*-> (?P<result>HIT|miss)$")
HIT_FOR = re.compile(r"(?P<who>.+?) hits (?P<target>.+?) for (?P<n>\d+): (?P<dice>[0-9d+\-]+)")
SAVE = re.compile(r"(?P<who>.+?)'s saving throw vs (?P<what>.+?)(?: from .+?)?: d20 = (?P<d20>\d+)"
                  r"(?: \(natural \d+\))?(?:, needs (?P<need>-?\d+))?(?: \([^)]*\))? -> (?P<result>\w+)")
RESIST = re.compile(r"(?P<who>.+?) magic resistance (?P<pct>\d+)% vs (?P<what>.+?): d100 = (?P<roll>\d+) -> "
                    r"(?P<result>.+)")
DAMAGE_ROLL = re.compile(r"(?P<what>.+?) damage: (?P<dice>\S+) = (?:\[[^\]]*\](?: [+-]\s?\d+)? = )?(?P<total>\d+)")
PERCENT = re.compile(r"(?P<what>.+?): d100 = (?P<roll>\d+), needs (?P<need>-?\d+) or less.*-> (?P<result>.+)")
ROUND = re.compile(r"Round (?P<n>\d+)")
NOT_THE_FIGHT = ("Message: ", "Dice: ", "Look: ", "Chosen with Tab", "(")


def shorten(line: str, level: str) -> Optional[str]:
    """A dice log line as the panel shows it at a level (None: not at that level). In detail,
    the line itself; in short, the dice and what came of them ("Rampager attacks Defiler: 20 vs
    16+ HIT"), no working; at the least, only what came of them ("Rampager hits Defiler")."""
    text = line.strip()
    if level == DETAIL:
        return text
    if line.startswith("    ") or text.startswith("Initiative"):
        return None
    m = ROUND.match(text)
    if m:
        return f"ROUND {m.group('n')}"
    m = ATTACK.match(text)
    if m:
        need = m.group("need") or "20"
        if level == MINIMAL:
            return f"{m.group('who')} {'hits' if m.group('result') == 'HIT' else 'misses'} {m.group('target')}"
        return f"{m.group('who')} attacks {m.group('target')}: {m.group('d20')} vs {need}+ {m.group('result')}"
    m = HIT_FOR.match(text)
    if m:
        return f"for {m.group('n')}" if level == MINIMAL else f"{m.group('n')} damage ({m.group('dice')})"
    m = SAVE.match(text)
    if m:
        saved = m.group("result") == "saved"
        if level == MINIMAL:
            return f"{m.group('who')} {'saves' if saved else 'fails to save'} vs {m.group('what')}"
        need = f" vs {m.group('need')}" if m.group("need") else ""
        return f"{m.group('who')}'s save vs {m.group('what')}: {m.group('d20')}{need}, {m.group('result')}"
    m = RESIST.match(text)
    if m:
        resisted = m.group("result").startswith("resisted")
        if level == MINIMAL:
            return f"{m.group('who')} resists {m.group('what')}" if resisted else None
        return f"{m.group('who')} MR {m.group('pct')}% vs {m.group('what')}: {m.group('roll')}, " \
               f"{'resisted' if resisted else 'not resisted'}"
    m = PERCENT.match(text)  # (a thief's skills, a scroll learnt)
    if m:
        result = m.group("result").split(":")[0]  # (what it means: the log has it)
        if level == MINIMAL:
            return f"{m.group('what')}: {result}"
        return f"{m.group('what')}: {m.group('roll')} vs {m.group('need')} or less, {result}"
    m = DAMAGE_ROLL.match(text)
    if m:
        return None if level == MINIMAL else f"{m.group('what')} damage: {m.group('dice')} = {m.group('total')}"
    if level == MINIMAL and (text.endswith("'s turn") or " now " in text and text.endswith(")")):
        return None  # (who acts: the header says; HP left: the "takes" lines say)
    return text


class Log:
    """The fight's lines, kept for the panel at all three levels (so a change of level shows the
    fight so far)."""

    def __init__(self):
        self.lines: Deque[Tuple[str, str]] = deque(maxlen=HISTORY)  # (kind, the log's line)
        self.version = 0  # counts changes

    def add(self, lines: Sequence[str]) -> None:
        for line in lines:
            if not line.strip() or line.startswith(NOT_THE_FIGHT):
                continue
            self.lines.append((line_kind(line), line))
            self.version += 1

    def at(self, level: str, names: Dict[str, str]) -> List[Line]:
        """The lines at a level, `names` the colours' keys of the names to know (whose line it is)."""
        out: List[Line] = []
        for kind, line in self.lines:
            text = shorten(line, level)
            if text is None:
                continue
            depth = (len(line) - len(line.lstrip(" "))) // 2 if level == DETAIL else 0
            hit = HIT_FOR.match(line.strip()) if level != DETAIL else None
            if hit and out and out[-1].kind == "hit" and out[-1].text.startswith(hit.group("who")):
                join = " " if level == MINIMAL else ", "
                out[-1] = out[-1]._replace(text=out[-1].text + join + text)  # an attack's damage on its line
                continue
            if hit:
                text = f"{hit.group('who')} hits {hit.group('target')} " + (text if level == MINIMAL else f"for {text}")
            if kind == "round":  # a rule, "ROUND 3", and in detail the order after it
                m = ROUND.match(text)
                if m is None:
                    kind = "detail"
                else:
                    out.append(Line("round", None, f"ROUND {m.group('n')}", 0))
                    rest = text[m.end():].lstrip(": ")
                    if rest:
                        out.append(Line("detail", None, rest, 1))
                    continue
            out.append(Line(kind, _side(text, names) if kind not in ("round", "detail") else None, text, depth))
        return out


def _side(text: str, names: Dict[str, str]) -> Optional[str]:
    """Whose line: the name it starts with."""
    for name in sorted(names, key=len, reverse=True):
        if text.startswith(name) and text[len(name):len(name) + 1] in ("", " ", "'"):
            return "monster" if names[name] == "monster" else "party"
    return None


# the strip's top line between fights (it keeps the last one's lines)
BETWEEN_FIGHTS, NO_FIGHT = "The last fight", "No fight yet"


def header(status: Optional[dict]) -> str:
    """The panel's top line from DiceLog.round_status: "Round 2: Gerakis, then Cermak, Cilla" (who
    is acting, then who is still to)."""
    if not status:
        return ""
    now = status["now"][0] if status.get("now") else ""
    nxt = ", ".join(name for name, _ in status.get("next", []))
    who = f"{now}, then {nxt}" if now and nxt else now or (f"then {nxt}" if nxt else "")
    top = f"Round {status['round']}" if status.get("round") else ""
    return f"{top}: {who}" if top and who else top or who


def rgb(colour: str) -> RGB:
    return tuple(int(colour[i:i + 2], 16) for i in (1, 3, 5))


def nearest(dac: bytes, colour: RGB) -> int:
    """The palette index (FIRST to LAST) nearest to COLOUR (0-255 a channel) in DAC (0-63 a
    channel, as the VGA's)."""
    def distance(index: int) -> int:
        return sum((dac[index * 3 + c] * 4 + dac[index * 3 + c] // 16 - colour[c]) ** 2 for c in range(3))
    return min(range(FIRST, LAST + 1), key=distance)


def _speckle(x: int, y: int) -> int:
    """A pattern fixed by x and y, 0-255 (the stone's grain, the well's dither)."""
    v = (x * 29 + y * 71) & 0xFFFF
    v ^= v >> 4
    return (v * 0x6D) & 0xFF


def _lattice(i: int, j: int) -> int:
    v = (i * 113 + j * 197 + 0x55) & 0xFFFF
    v ^= v >> 5
    return ((v * 0x9D) & 0xFFFF) >> 3 & 0xFF


def _smooth(x: int, y: int, shift: int) -> int:
    """Value noise, cells of 1 << SHIFT pixels: 0-255."""
    size = 1 << shift
    i, j, fx, fy = x >> shift, y >> shift, x & (size - 1), y & (size - 1)
    top = _lattice(i, j) * (size - fx) + _lattice(i + 1, j) * fx
    bottom = _lattice(i, j + 1) * (size - fx) + _lattice(i + 1, j + 1) * fx
    return (top * (size - fy) + bottom * fy) >> (2 * shift)


def mottle(x: int, y: int) -> int:
    """The well's shade at x, y (0 darkest to 3): blotches of 4 and 8 pixels, their edges
    dithered, as the game's dialogue window's stone."""
    v = (_smooth(x, y, 3) * 2 + _smooth(x + 37, y + 11, 2)) // 3 + (_speckle(x, y) & 31) - 16
    return 0 if v < 92 else 1 if v < 118 else 2 if v < 160 else 3


def inks(dac: bytes) -> Dict[str, int]:
    """Each of COLOURS as its nearest index in DAC."""
    return {name: nearest(dac, rgb(c)) for name, c in COLOURS.items()}


class Geometry(NamedTuple):
    """A size of the panel: its height (its foot stays at PANEL_Y0 + PANEL_H), the rows of lines
    in its well (none: collapsed, the newest line in its header), and the filters' row. The strip
    below the map (STRIP) is wider, at the screen's left, its header and well closer together."""
    height: int
    rows: int
    filters: bool = False
    width: int = PANEL_W
    x0: int = PANEL_X0
    foot: int = PANEL_Y0 + PANEL_H
    strip: bool = False

    @property
    def top(self) -> int:
        return self.foot - self.height

    @property
    def well(self) -> Tuple[int, int, int, int]:
        return (4, 11, self.width - 5, self.height - 2) if self.strip else (4, 15, self.width - 5, self.height - 5)

    @property
    def header_y(self) -> int:
        return 1 if self.strip else HEADER_Y

    @property
    def plus_x0(self) -> int:
        return self.width - 5 - BUTTON_W

    @property
    def minus_x0(self) -> int:
        return self.plus_x0 - 1 - BUTTON_W

    @property
    def text_right(self) -> int:
        return self.well[2] - 9

    @property
    def track(self) -> Tuple[int, int, int, int]:
        x0, y0, x1, y1 = self.well
        return x1 - 6, y0 + 1, x1 - 1, y1 - 1

    @property
    def track_h(self) -> int:
        _, y0, _, y1 = self.track
        return y1 - y0 - 1

    @property
    def text_y(self) -> int:
        return self.well[1] + (1 if self.strip else 2) + (LINE_H if self.filters else 0)


COLLAPSED, DOCKED, EXPANDED = "collapsed", "docked", "expanded"
SIZES = {COLLAPSED: Geometry(15, 0), DOCKED: Geometry(PANEL_H, ROWS), EXPANDED: Geometry(130, 11, True)}
STRIP_W, STRIP_H, STRIP_Y0 = 320, 22, 200  # the strip below the map (the 320 x 222 screen: DSCLOG's STRIP)
STRIP = Geometry(STRIP_H, 1, False, STRIP_W, 0, STRIP_Y0 + STRIP_H, True)
DGROUP_SEG = 0x4356  # (the game's data segment, less its load segment: DSCLOG's DGROUP_SEG)
STRIP_AT, STRIP_INT = 0x11640 - 0x5400, bytes((0xCD, 0xF7))  # the game's code there with the
#   strip's patch (gamepatch's strip_lines: INT VEC_STRIP), from its load segment


def strip_patched(gd) -> bool:
    """The game was started with the combat log below the map (its screen 320 x 222)."""
    ds = getattr(gd, "ds", None)
    return ds is not None and gd.guest.read((ds - DGROUP_SEG) * 16 + STRIP_AT, 2) == STRIP_INT
SIZE_ORDER = (COLLAPSED, DOCKED, EXPANDED)
LEVEL_ORDER = (MINIMAL, SHORT, DETAIL)
LEVEL_NAMES = {MINIMAL: "Least", SHORT: "Short", DETAIL: "Detail"}
FILTERS = (("all", "All"), ("party", "Party"), ("damage", "Damage"), ("saves", "Saves"))
BUTTON_W = 9  # the header's + and - buttons, at its right; the level chip before them
PLUS_X0 = PANEL_W - 5 - BUTTON_W
MINUS_X0 = PLUS_X0 - 1 - BUTTON_W
HEADER_Y0, HEADER_Y1 = 2, 11  # (the buttons' rows)


def render(dac: bytes, ink: Optional[Dict[str, int]] = None, g: Geometry = SIZES[DOCKED]) -> bytes:
    """The panel's frame and well, PANEL_W x G.height palette indices row by row, in the colours
    of DAC (no lines)."""
    ink = ink or inks(dac)
    w, h = g.width, g.height
    rows: List[bytearray] = [bytearray(w) for _ in range(h)]

    def fill(x0: int, y0: int, x1: int, y1: int, colour: int) -> None:
        for y in range(y0, y1 + 1):
            rows[y][x0:x1 + 1] = bytes((colour,)) * (x1 - x0 + 1)

    shades = [ink["well0"], ink["well1"], ink["well2"], ink["well3"]]
    if g.strip:  # the strip: all of it the well's darker shade, the top line too
        for y in range(h):
            for x in range(w):
                rows[y][x] = shades[mottle(x, y)]
        fill(0, 0, w - 1, 0, ink["outline"])  # (its edge against the map)
        fill(3, 10, w - 4, 10, ink["well0"])  # (the top line's rule, faint)
        t = g.track
        fill(t[0], t[1], t[2], t[3], ink["dark"])
        return b"".join(bytes(r) for r in rows)

    fill(0, 0, w - 1, h - 1, ink["outline"])
    for y in range(1, h - 1):  # the stone, speckled (as the screen's, wherever it is)
        for x in range(1, w - 1):
            n = _speckle(x + g.x0, y + g.top)
            rows[y][x] = ink["grain_hi"] if n < GRAIN_HI_N else ink["grain_lo"] if n < GRAIN_HI_N + GRAIN_LO_N \
                else ink["stone"]
    fill(1, 1, w - 2, 1, ink["light"])  # the bevel, lit from the upper left
    fill(1, 1, 1, h - 2, ink["light"])
    fill(2, h - 2, w - 2, h - 2, ink["dark"])
    fill(w - 2, 2, w - 2, h - 2, ink["dark"])
    if g.rows:
        fill(3, 12, w - 4, 12, ink["dark"])  # the header's groove
        fill(3, 13, w - 4, 13, ink["light"])
        x0, y0, x1, y1 = g.well
        for y in range(y0, y1 + 1):  # the well, mottled
            for x in range(x0, x1 + 1):
                rows[y][x] = shades[mottle(x, y)]
        t = g.track
        fill(t[0], t[1], t[2], t[3], ink["dark"])  # the scrollbar (its handle: draw)
    return b"".join(bytes(r) for r in rows)


Run = Tuple[str, str]  # (text, the colour's key)


def coloured(text: str, colour: str, names: Dict[str, str]) -> List[Run]:
    """TEXT in runs of colour: the names (longest first) in theirs, the rest in COLOUR."""
    keys = [colour] * len(text)
    taken = [False] * len(text)
    for name in sorted(names, key=len, reverse=True):
        for found in re.finditer(r"(?<!\w)" + re.escape(name) + r"(?!\w)", text):
            start, end = found.span()
            if any(taken[start:end]):
                continue
            for i in range(start, end):
                keys[i], taken[i] = names[name], True
    runs: List[Run] = []
    for ch, key in zip(text, keys):
        if runs and runs[-1][1] == key:
            runs[-1] = (runs[-1][0] + ch, key)
        else:
            runs.append((ch, key))
    return runs


def _width(font, text: str) -> int:
    return sum(font.glyph(ch)[0] for ch in text)


def fit(font, text: str, room: int) -> str:
    """TEXT, or as much of it as fits in ROOM pixels with "..." after, cut after a name."""
    if _width(font, text) <= room:
        return text
    while text and _width(font, text + "...") > room:
        cut = text.rfind(", ")
        text = text[:cut] if cut > 0 else text[:-1]
    return text + "..."


def wrap(font, runs: List[Run], first: int, rest: int) -> List[List[Run]]:
    """RUNS in rows of at most FIRST pixels, then REST, broken at spaces (a word wider than a
    row, where it must)."""
    chars = [(ch, key) for text, key in runs for ch in text]
    rows: List[List[Tuple[str, str]]] = []
    while chars:
        room = first if not rows else rest
        width, cut, space = 0, len(chars), None
        for i, (ch, _) in enumerate(chars):
            width += font.glyph(ch)[0]
            if width > room:
                cut = i
                break
            if ch == " ":
                space = i
        if cut < len(chars) and space is not None:
            cut = space + 1
        cut = max(cut, 1)
        rows.append(chars[:cut])
        chars = chars[cut:]
        while chars and chars[0][0] == " ":
            chars = chars[1:]
    out = []
    for row in rows:
        while row and row[-1][0] == " ":
            row = row[:-1]
        merged: List[Run] = []
        for ch, key in row:
            if merged and merged[-1][1] == key:
                merged[-1] = (merged[-1][0] + ch, key)
            else:
                merged.append((ch, key))
        out.append(merged)
    return out


_picture_w = PANEL_W  # the width of the picture being drawn (draw: its geometry's)


def _text(picture: bytearray, font, x: int, y: int, runs: List[Run], ink: Dict[str, int], right: int,
          shadow_key: str = "shadow") -> None:
    """RUNS into PICTURE (_PICTURE_W wide) at x, y, cut at x RIGHT, the letters' shadow in
    SHADOW_KEY's colour."""
    shadow = ink[shadow_key]
    for text, key in runs:
        colour = ink.get(key, ink["text"])
        for ch in text:
            width, data = font.glyph(ch)
            for gy in range(font.height):
                row = (y + gy) * _picture_w
                for gx in range(width):
                    if x + gx > right:
                        break
                    b = data[gy * width + gx]
                    if b == FONT_INK:
                        picture[row + x + gx] = colour
                    elif b == FONT_SHADOW:
                        picture[row + x + gx] = shadow
            x += width
            if x > right:
                return


def _pip(picture: bytearray, x: int, y: int, filled: bool, colour: int) -> None:
    """A 3 x 3 pip, hollow for a monster's line."""
    for dy in range(3):
        for dx in range(3):
            if filled or dx != 1 or dy != 1:
                picture[(y + dy) * _picture_w + x + dx] = colour


def rows_of(font, lines: List[Line], names: Dict[str, str],
            g: Geometry = SIZES[DOCKED]) -> List[Tuple[Optional[Line], int, List[Run]]]:
    """Every line's rows as the well (of G's width) shows them: (the line, on its first row, else
    None; the row's x; its runs)."""
    out: List[Tuple[Optional[Line], int, List[Run]]] = []
    width = g.text_right - TEXT_X
    for line in lines:
        indent = INDENT * line.depth
        if line.kind == "round":  # a rule across, the round in the middle
            out.append((line, TEXT_X, [(line.text, "log round")]))
            continue
        rows = wrap(font, coloured(line.text, f"log {line.kind}", names), width - indent, width - indent - INDENT)
        for n, row in enumerate(rows):
            out.append((line if n == 0 else None, TEXT_X + indent + (INDENT if n else 0), row))
    return out


def visible(first: Optional[int], g: Geometry = SIZES[DOCKED]) -> int:
    """Rows of lines the well shows: one fewer when scrolled back, for the "Latest" chip (the
    strip's chip is in its header)."""
    return g.rows if first is None or g.strip else g.rows - 1


def scroll_to(first: Optional[int], total: int, g: Geometry = SIZES[DOCKED]) -> Optional[int]:
    """FIRST (the top row shown, None following the newest) kept within TOTAL rows: None once it
    shows the last of them."""
    if first is None:
        return None
    first = max(0, first)
    return None if first >= total - visible(first, g) else first


def top_row(first: Optional[int], total: int, g: Geometry = SIZES[DOCKED]) -> int:
    """The top row shown."""
    return max(0, total - g.rows) if first is None else first


def handle(first: Optional[int], total: int, g: Geometry = SIZES[DOCKED]) -> Tuple[int, int]:
    """The scrollbar's handle: its top (in the panel) and height."""
    if total <= g.rows:
        return g.track[1] + 1, g.track_h
    height = min(g.track_h, max(HANDLE_MIN, g.track_h * visible(first, g) // total))
    room = total - visible(first, g)
    return g.track[1] + 1 + (g.track_h - height) * min(top_row(first, total, g), room) // room, height


def chip_rect(g: Geometry = SIZES[DOCKED]) -> Tuple[int, int, int, int]:
    """The "Latest" chip, at the well's foot when scrolled back: x0, y0, x1, y1 in the panel."""
    y = g.text_y + (g.rows - 1) * LINE_H
    return g.well[0] + 1, y - 1, g.track[0] - 2, y + LINE_H - 1


def level_rect(font, g: Geometry = SIZES[DOCKED]) -> Tuple[int, int, int, int]:
    """The header's level chip, before the - and + buttons."""
    width = max(_width(font, name) for name in LEVEL_NAMES.values()) + 6 if font is not None else 34
    return g.minus_x0 - 2 - width, HEADER_Y0, g.minus_x0 - 2, HEADER_Y1


def filter_rects(font, g: Geometry) -> List[Tuple[str, Tuple[int, int, int, int]]]:
    """The filters' chips along the top of the well (expanded): (the filter, its x0, y0, x1, y1)."""
    if not g.filters or font is None:
        return []
    out, x = [], g.well[0] + 2
    y = g.well[1] + 1
    for key, label in FILTERS:
        x1 = x + _width(font, label) + 5
        out.append((key, (x, y, x1, y + LINE_H - 1)))
        x = x1 + 3
    return out


def filtered(lines: List[Line], filt: str) -> List[Line]:
    """The lines a filter keeps: a party member's, the hits and damage (and deaths), the saving
    throws and magic resistance; the rounds' rules with them."""
    if filt == "party":
        return [ln for ln in lines if ln.side == "party" or ln.kind == "round"]
    if filt == "damage":
        return [ln for ln in lines if ln.kind in ("hit", "damage", "round") or " is killed" in ln.text]
    if filt == "saves":
        return [ln for ln in lines if ln.kind in ("save", "round")]
    return lines


def _box(picture: bytearray, rect: Tuple[int, int, int, int], ink: Dict[str, int], fill: str) -> None:
    x0, y0, x1, y1 = rect
    for cy in range(y0, y1 + 1):
        for cx in range(x0, x1 + 1):
            edge = cy in (y0, y1) or cx in (x0, x1)
            picture[cy * _picture_w + cx] = ink["outline"] if edge else ink[fill]


def _button(picture: bytearray, font, rect, label: str, ink: Dict[str, int], on: bool = False) -> None:
    """A chip or button: stone (light when ON), its label in the middle."""
    _box(picture, rect, ink, "light" if on else "stone")
    x0, y0, x1, _ = rect
    _text(picture, font, (x0 + x1 + 1 - _width(font, label)) // 2, y0 + 1,
          [(label, "outline" if on else "text")], ink, x1 - 1, "light" if on else "shadow")


def draw(background: bytes, font, ink: Dict[str, int], top: str, lines: List[Line], names: Dict[str, str],
         first_row: Optional[int] = None, new: int = 0, g: Geometry = SIZES[DOCKED], level: Optional[str] = None,
         filt: str = "all") -> bytes:
    """The panel with its lines: the header TOP, and the well's rows from FIRST_ROW (None: the
    last ones; else with a chip to go back to them, saying how many rows came since, NEW). With
    LEVEL, the header's level chip and size buttons; G its size (collapsed: TOP is the newest
    line); FILT the filter chosen, when it has the filters' row."""
    global _picture_w
    _picture_w = w = g.width
    picture = bytearray(background)
    rows = rows_of(font, lines, names, g) if font is not None and g.rows else []
    if g.rows:
        hy, hh = handle(first_row, len(rows), g)
        x0, x1 = g.track[0] + 1, g.track[2] - 1
        for y in range(hy, hy + hh):
            picture[y * w + x0:y * w + x1 + 1] = bytes((ink["handle"],)) * (x1 - x0 + 1)
    if font is None:
        return bytes(picture)
    level = None if g.strip else level  # (the strip: no buttons, out of the pointer's reach)
    room = (level_rect(font, g)[0] if level else w - 4) - 2
    chip = f"Latest: {new} new" if new else "Latest"
    if g.strip and first_row is not None:  # (the strip's chip: in its header, at the right)
        chip_w = _width(font, chip) + 6
        strip_chip = (g.track[0] - 2 - chip_w, 1, g.track[0] - 2, 10)
        room = strip_chip[0] - 2
    _text(picture, font, HEADER_X, g.header_y, coloured(fit(font, top, room - HEADER_X), "log round", names), ink,
          room)
    if level:
        _button(picture, font, level_rect(font, g), LEVEL_NAMES.get(level, level), ink)
        if g != SIZES[COLLAPSED]:
            _button(picture, font, (g.minus_x0, HEADER_Y0, g.minus_x0 + BUTTON_W - 1, HEADER_Y1), "-", ink)
        if g != SIZES[EXPANDED]:
            _button(picture, font, (g.plus_x0, HEADER_Y0, g.plus_x0 + BUTTON_W - 1, HEADER_Y1), "+", ink)
    for key, rect in filter_rects(font, g):
        _button(picture, font, rect, dict(FILTERS)[key], ink, on=key == filt)
    start = top_row(first_row, len(rows), g)
    y = g.text_y
    right = g.track[0] - 3
    for line, x, runs in rows[start:start + visible(first_row, g)]:
        if line is not None and line.kind == "round":
            label = _width(font, line.text)
            mid = (TEXT_X + right) // 2
            for rx in list(range(TEXT_X, mid - label // 2 - 3)) + list(range(mid + label // 2 + 3, right)):
                picture[(y + 4) * w + rx] = ink["log round"]
            _text(picture, font, mid - label // 2, y, runs, ink, right)
        else:
            if line is not None and line.side is not None:
                _pip(picture, g.well[0] + 2, y + 3, line.side == "party",
                     ink["member0"] if line.side == "party" else ink["monster"])
            _text(picture, font, x, y, runs, ink, right)
        y += LINE_H
    if first_row is not None and g.rows:  # the chip: "Latest" and the rows since
        _button(picture, font, strip_chip if g.strip else chip_rect(g), chip, ink)
    return bytes(picture)


class Panel:
    def __init__(self):
        self._on: Optional[bool] = None
        self._palettes = 0
        self._ink: Optional[Dict[str, int]] = None
        self._backgrounds: Dict[str, bytes] = {}  # each size's frame, in the palette last read
        self._shown: Optional[tuple] = None  # what's in the picture now
        self.log = Log()
        self.font = None  # art.Font: no font, no lines
        self.level = SHORT
        self.size = DOCKED
        self._open_size = DOCKED  # the size L opens a collapsed panel to
        self.filter = "all"
        self.first: Optional[int] = None  # the top row shown when scrolled back (None: the newest)
        self._back_rows = 0  # ... the rows there were then (the chip's "new")
        self._rows = 0  # the rows at the last drawing
        self._hits: Optional[int] = None  # DSCLOG's count of presses on the panel, as last seen
        self._keys: Optional[int] = None  # ... and of L
        self._grab: Optional[int] = None  # dragging the handle: the press's distance below its top
        self.pointer = (-1, -1)  # where the game's pointer is (DSCLOG's), on the screen
        self.strip = False  # in the strip below the map (the Options tab's combat_log_strip)

    @property
    def g(self) -> Geometry:
        return STRIP if self.strip else SIZES[self.size]

    @property
    def shown(self) -> bool:
        return bool(self._on)

    def over(self) -> bool:
        """The game's pointer is over the panel (the strip: anywhere, as it can't reach it)."""
        if self.strip:
            return True
        x, y = self.pointer
        return 0 <= x - PANEL_X0 < PANEL_W and 0 <= y - self.g.top < self.g.height

    def _scroll(self, first: Optional[int]) -> None:
        if first is not None and self.first is None:
            self._back_rows = self._rows
        self.first = scroll_to(first, self._rows, self.g)

    def resize(self, size: str) -> None:
        if size != self.size:
            self.size = size
            if size != COLLAPSED:
                self._open_size = size
            if size != EXPANDED:
                self.filter = "all"
            self.first, self._grab = None, None

    def wheel(self, notches: int) -> None:
        """The mouse wheel turned over the panel: NOTCHES up (back) or, below 0, down."""
        if notches and self.g.rows:
            step = 1 if self.strip else WHEEL_ROWS  # (the strip's one row: a line a notch)
            self._scroll(top_row(self.first, self._rows, self.g) - notches * step)

    def mouse(self, gd, tsr_hdr: int) -> None:
        """The left button on the panel (DSCLOG's TSR_MOUSE): on the scrollbar's handle, dragging
        it; on the bar above or below it, a page back or on; on the "Latest" chip, the newest; on
        the header's level chip, the next level; on + or -, a size bigger or smaller; on a filter,
        that filter. L (TSR_KEYS) collapses the panel or opens it again."""
        mx, my, held, hits, hx, hy = struct.unpack("<hhHHhh", gd.guest.read(tsr_hdr + TSR_MOUSE, 12))
        keys, = struct.unpack("<H", gd.guest.read(tsr_hdr + TSR_KEYS, 2))
        self.pointer = (mx, my)
        if self._keys is None:
            self._keys = keys
        if keys != self._keys:
            self._keys = keys
            self.resize(self._open_size if self.size == COLLAPSED else COLLAPSED)
        if self._hits is None:
            self._hits = hits
        g = self.g
        if hits != self._hits:  # a press
            self._hits = hits
            self._grab = None
            px, py = hx - g.x0, hy - g.top
            filters = filter_rects(self.font, g)
            if HEADER_Y0 <= py <= HEADER_Y1 and px >= g.minus_x0:  # - and +
                order = SIZE_ORDER.index(self.size)
                self.resize(SIZE_ORDER[max(0, order - 1)] if px < g.plus_x0 else SIZE_ORDER[min(2, order + 1)])
                return
            lx0, ly0, lx1, ly1 = level_rect(self.font, g)
            if ly0 <= py <= ly1 and lx0 <= px <= lx1:
                self.level = LEVEL_ORDER[(LEVEL_ORDER.index(self.level) + 1) % len(LEVEL_ORDER)] \
                    if self.level in LEVEL_ORDER else SHORT
                self.first = None
                return
            for key, (fx0, fy0, fx1, fy1) in filters:
                if fx0 <= px <= fx1 and fy0 <= py <= fy1:
                    self.filter, self.first = key, None
                    return
            if not g.rows:
                return
            top, height = handle(self.first, self._rows, g)
            x0, y0, x1, y1 = chip_rect(g)
            t = g.track
            if self.first is not None and x0 <= px <= x1 and y0 <= py <= y1:
                self.first = None
            elif t[0] - 1 <= px <= t[2] + 1 and t[1] <= py <= t[3]:
                shown = top_row(self.first, self._rows, g)
                if top <= py < top + height:
                    self._grab = py - top
                elif py < top:
                    self._scroll(shown - (g.rows - 1))
                else:
                    self._scroll(shown + g.rows - 1)
        if not held:
            self._grab = None
        elif self._grab is not None and self._rows > g.rows:
            _, height = handle(0, self._rows, g)  # (the height while scrolled back)
            room = g.track_h - height
            if room > 0:
                pos = my - g.top - self._grab - (g.track[1] + 1)
                self._scroll(round(max(0, min(room, pos)) * (self._rows - visible(0, g)) / room))

    def update(self, gd, tsr_hdr: int, on: bool, palettes: int, top: str = "",
               names: Optional[Dict[str, str]] = None) -> None:
        """ON: the panel shown (once it is drawn in a palette DSCLOG has read: PALETTES counts the
        reads), with the header TOP and the log's lines, NAMES their colours' keys."""
        guest = gd.guest
        self.strip = strip_patched(gd)
        seg, = struct.unpack("<H", guest.read(tsr_hdr + TSR_PANEL_SEG, 2))
        if not seg:  # (no memory for it: no panel)
            on = False
        names = names or {}
        if on and palettes and palettes != self._palettes:
            base = tsr_hdr - struct.unpack("<H", guest.read(tsr_hdr + TSR_HDR_OFF, 2))[0]
            dac_off, = struct.unpack("<H", guest.read(tsr_hdr + TSR_DAC, 2))
            self._dac = guest.read(base + dac_off, 768)
            self._ink = inks(self._dac)
            self._backgrounds = {}
            self._palettes = palettes
            self._shown = None
        if not on:
            self.first, self._grab = None, None  # (the next fight: its newest lines)
        if on and self._ink is not None:
            now = (self._palettes, top, self.log.version, self.level, tuple(sorted(names.items())), self.first,
                   "strip" if self.strip else self.size, self.filter)
            if now != self._shown:
                g, size = self.g, now[6]
                if size not in self._backgrounds:
                    self._backgrounds[size] = render(self._dac, self._ink, g)
                lines = filtered(self.log.at(self.level, names), self.filter)
                if g.rows:
                    self._rows = len(rows_of(self.font, lines, names, g)) if self.font is not None else 0
                    self.first = scroll_to(self.first, self._rows, g)
                else:  # collapsed: the newest line in the header
                    top = lines[-1].text if lines else top
                picture = draw(self._backgrounds[size], self.font, self._ink, top, lines, names, self.first,
                               max(0, self._rows - self._back_rows), g, self.level, self.filter)
                guest.write(seg * 16, picture)
                guest.write(tsr_hdr + TSR_PANEL_TOP, struct.pack("<HH", g.top, g.height))
                guest.write(tsr_hdr + TSR_PANEL_NEW, struct.pack("<H", 1))
                self._shown = now[:5] + (self.first,) + now[6:]
        want = on and self._palettes > 0
        if want != self._on:
            guest.write(tsr_hdr + TSR_PANEL_ON, struct.pack("<H", int(want)))
            self._on = want
