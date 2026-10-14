"""The combat log's panel in the game (DSCLOG's PANEL), drawn and kept up by the Ledger.

The Ledger draws the panel, a picture of PANEL_W x PANEL_H palette indices (render), and puts it
in the memory block DSCLOG keeps for it (TSR_PANEL_SEG); DSCLOG puts the picture over the map,
bottom right, from the game's main loop and after each rectangle of the view the game draws again
(the map is drawn straight into the screen on show, a rectangle at a time). The Ledger turns it on
in a fight (TSR_PANEL_ON) and off after, when DSCLOG has the view drawn again without it.

The picture is in the area's own colours: the game's stone (palette.py) matched to the nearest of
the palette DSCLOG last read (for the shadows: shadows.Shadows.palettes), among the colours the
game doesn't animate, and drawn again when that palette changes or the log has new lines. The
frame is the stone of the game's status box, speckled; the well, where the log's lines go,
mottled like the game's dialogue window, in darker shades.

The lines are the dice log's own (DiceLog.lines), from the fight (Log): in detail all of them, in
short a line for each attack, saving throw and spell's damage with its dice, at the least what came
of them. They are in the game's font (art.Font), in the Ledger's colours for their kind
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

# the detail levels (dicelog's POPUP_MINIMAL, POPUP_SHORT, POPUP_DETAIL)
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


class Line(NamedTuple):
    kind: str  # palette.LOG_COLOURS's
    side: Optional[str]  # "party", "monster": whose line (its pip), or None
    text: str
    depth: int = 0  # a detail line's indent (the log's leading spaces, in twos)


def line_kind(line: str) -> str:
    """A dice log line's kind, for its colour (as the Ledger's log shows it)."""
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
            out.append(Line(kind, _side(text, names) if kind not in ("round", "detail") else None, text, depth))
        return out


def _side(text: str, names: Dict[str, str]) -> Optional[str]:
    """Whose line: the name it starts with."""
    for name in sorted(names, key=len, reverse=True):
        if text.startswith(name) and text[len(name):len(name) + 1] in ("", " ", "'"):
            return "monster" if names[name] == "monster" else "party"
    return None


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


def render(dac: bytes, ink: Optional[Dict[str, int]] = None) -> bytes:
    """The panel's frame and well, PANEL_W x PANEL_H palette indices row by row, in the colours
    of DAC (no lines)."""
    ink = ink or inks(dac)
    w, h = PANEL_W, PANEL_H
    rows: List[bytearray] = [bytearray(w) for _ in range(h)]

    def fill(x0: int, y0: int, x1: int, y1: int, colour: int) -> None:
        for y in range(y0, y1 + 1):
            rows[y][x0:x1 + 1] = bytes((colour,)) * (x1 - x0 + 1)

    fill(0, 0, w - 1, h - 1, ink["outline"])
    for y in range(1, h - 1):  # the stone, speckled
        for x in range(1, w - 1):
            n = _speckle(x + PANEL_X0, y + PANEL_Y0)
            rows[y][x] = ink["grain_hi"] if n < GRAIN_HI_N else ink["grain_lo"] if n < GRAIN_HI_N + GRAIN_LO_N \
                else ink["stone"]
    fill(1, 1, w - 2, 1, ink["light"])  # the bevel, lit from the upper left
    fill(1, 1, 1, h - 2, ink["light"])
    fill(2, h - 2, w - 2, h - 2, ink["dark"])
    fill(w - 2, 2, w - 2, h - 2, ink["dark"])
    fill(3, 12, w - 4, 12, ink["dark"])  # the header's groove
    fill(3, 13, w - 4, 13, ink["light"])
    x0, y0, x1, y1 = WELL
    shades = [ink["well0"], ink["well1"], ink["well2"], ink["well3"]]
    for y in range(y0, y1 + 1):  # the well, mottled
        for x in range(x0, x1 + 1):
            rows[y][x] = shades[mottle(x, y)]
    fill(x1 - 6, y0 + 1, x1 - 1, y1 - 1, ink["dark"])  # the scrollbar ...
    fill(x1 - 5, y1 - 17, x1 - 2, y1 - 2, ink["handle"])  # ... and its handle
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


def _text(picture: bytearray, font, x: int, y: int, runs: List[Run], ink: Dict[str, int], right: int) -> None:
    """RUNS into PICTURE (PANEL_W wide) at x, y, cut at x RIGHT."""
    shadow = ink["shadow"]
    for text, key in runs:
        colour = ink.get(key, ink["text"])
        for ch in text:
            width, data = font.glyph(ch)
            for gy in range(font.height):
                row = (y + gy) * PANEL_W
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
                picture[(y + dy) * PANEL_W + x + dx] = colour


def rows_of(font, lines: List[Line], names: Dict[str, str]) -> List[Tuple[Optional[Line], int, List[Run]]]:
    """Every line's rows as the well shows them: (the line, on its first row, else None; the
    row's x; its runs)."""
    out: List[Tuple[Optional[Line], int, List[Run]]] = []
    width = TEXT_RIGHT - TEXT_X
    for line in lines:
        indent = INDENT * line.depth
        if line.kind == "round":  # a rule across, the round in the middle
            out.append((line, TEXT_X, [(line.text, "log round")]))
            continue
        rows = wrap(font, coloured(line.text, f"log {line.kind}", names), width - indent, width - indent - INDENT)
        for n, row in enumerate(rows):
            out.append((line if n == 0 else None, TEXT_X + indent + (INDENT if n else 0), row))
    return out


def draw(background: bytes, font, ink: Dict[str, int], top: str, lines: List[Line], names: Dict[str, str],
         first_row: Optional[int] = None) -> bytes:
    """The panel with its lines: the header TOP, and the well's ROWS rows from FIRST_ROW (None:
    the last ones)."""
    picture = bytearray(background)
    if font is None:
        return bytes(picture)
    _text(picture, font, HEADER_X, HEADER_Y, coloured(fit(font, top, PANEL_W - 4 - HEADER_X), "log round", names),
          ink, PANEL_W - 4)
    rows = rows_of(font, lines, names)
    start = max(0, len(rows) - ROWS) if first_row is None else max(0, min(first_row, len(rows) - ROWS))
    y = WELL[1] + 2
    for line, x, runs in rows[start:start + ROWS]:
        if line is not None and line.kind == "round":
            label = _width(font, line.text)
            mid = (TEXT_X + TEXT_RIGHT) // 2
            for rx in list(range(TEXT_X, mid - label // 2 - 3)) + list(range(mid + label // 2 + 3, TEXT_RIGHT)):
                picture[(y + 4) * PANEL_W + rx] = ink["log round"]
            _text(picture, font, mid - label // 2, y, runs, ink, TEXT_RIGHT)
        else:
            if line is not None and line.side is not None:
                _pip(picture, WELL[0] + 2, y + 3, line.side == "party",
                     ink["member0"] if line.side == "party" else ink["monster"])
            _text(picture, font, x, y, runs, ink, TEXT_RIGHT)
        y += LINE_H
    return bytes(picture)


class Panel:
    def __init__(self):
        self._on: Optional[bool] = None
        self._palettes = 0
        self._ink: Optional[Dict[str, int]] = None
        self._background = b""
        self._shown: Optional[tuple] = None  # what's in the picture now
        self.log = Log()
        self.font = None  # art.Font: no font, no lines
        self.level = SHORT

    def update(self, gd, tsr_hdr: int, on: bool, palettes: int, top: str = "",
               names: Optional[Dict[str, str]] = None) -> None:
        """ON: the panel shown (once it is drawn in a palette DSCLOG has read: PALETTES counts the
        reads), with the header TOP and the log's lines, NAMES their colours' keys."""
        guest = gd.guest
        seg, = struct.unpack("<H", guest.read(tsr_hdr + TSR_PANEL_SEG, 2))
        if not seg:  # (no memory for it: no panel)
            on = False
        names = names or {}
        if on and palettes and palettes != self._palettes:
            base = tsr_hdr - struct.unpack("<H", guest.read(tsr_hdr + TSR_HDR_OFF, 2))[0]
            dac_off, = struct.unpack("<H", guest.read(tsr_hdr + TSR_DAC, 2))
            dac = guest.read(base + dac_off, 768)
            self._ink = inks(dac)
            self._background = render(dac, self._ink)
            self._palettes = palettes
            self._shown = None
        if on and self._ink is not None:
            now = (self._palettes, top, self.log.version, self.level, tuple(sorted(names.items())))
            if now != self._shown:
                picture = draw(self._background, self.font, self._ink, top, self.log.at(self.level, names), names)
                guest.write(seg * 16, picture)
                guest.write(tsr_hdr + TSR_PANEL_NEW, struct.pack("<H", 1))
                self._shown = now
        want = on and self._palettes > 0
        if want != self._on:
            guest.write(tsr_hdr + TSR_PANEL_ON, struct.pack("<H", int(want)))
            self._on = want
