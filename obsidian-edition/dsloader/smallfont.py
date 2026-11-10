"""The combat log panel's small font: 8 pixels a line, its shadow in it.

The glyphs are the X11 misc-fixed 5x7 font's ("Public domain font. Share and enjoy."), ASCII and a
few more: each 7 rows of two hex digits (their bits the 5 columns, 10h the leftmost), set in a cell
5 wide and 8 high with the shadow a pixel down and right, as the game's own font has it (none past
the cell's right edge). It reads as art.Font does (height, glyph), so the panel draws it as it drew
the game's. (Until 2.15.0 it was the 4x6 font, a pixel smaller each way.)"""

from typing import Dict, Tuple

FONT_INK, FONT_SHADOW = 254, 20  # (art.FONT_INK, FONT_SHADOW)
WIDTH, HEIGHT = 5, 8
ROWS = HEIGHT - 1  # (the glyph's rows; the cell's last is the shadow's)

GLYPHS: Dict[str, str] = {
    ' ': "00000000000000", '!': "04040404000400", '"': "0a0a0a00000000", '#': "000a1f0a1f0a00",
    '$': "000e140e050e00", '%': "10120408120200", '&': "00081408140a00", "'": "04040400000000",
    '(': "04080808080400", ')': "08040404040800", '*': "000a040e040a00", '+': "0004041f040400",
    ',': "00000000060408", '-': "0000001e000000", '.': "000000000c0c00", '/': "00020408100000",
    '0': "040a0a0a0a0400", '1': "040c0404040e00", '2': "0c120204081e00", '3': "1e020c02120c00",
    '4': "040c141e040400", '5': "1e101c02120c00", '6': "0c101c12120c00", '7': "1e020404080800",
    '8': "0c120c12120c00", '9': "0c12120e020c00", ':': "000c0c000c0c00", ';': "000c0c000c0810",
    '<': "00020408040200", '=': "00001e001e0000", '>': "00080402040800", '?': "040a0204000400",
    '@': "0c121616100c00", 'A': "0c12121e121200", 'B': "1c121c12121c00", 'C': "0c121010120c00",
    'D': "1c121212121c00", 'E': "1e101c10101e00", 'F': "1e101c10101000", 'G': "0c121016120e00",
    'H': "12121e12121200", 'I': "0e040404040e00", 'J': "02020202120c00", 'K': "12141818141200",
    'L': "10101010101e00", 'M': "121e1e12121200", 'N': "121a1a16161200", 'O': "0c121212120c00",
    'P': "1c12121c101000", 'Q': "0c1212121a0c02", 'R': "1c12121c141200", 'S': "0c120804120c00",
    'T': "0e040404040400", 'U': "12121212120c00", 'V': "121212120c0c00", 'W': "1212121e1e1200",
    'X': "12120c0c121200", 'Y': "0a0a0a04040400", 'Z': "1e020408101e00", '[': "0e080808080e00",
    '\\': "00100804020000", ']': "0e020202020e00", '^': "040a0000000000", '_': "00000000001e00",
    '`': "08040000000000", 'a': "00000e12160a00", 'b': "10101c12121c00", 'c': "00000c10100c00",
    'd': "02020e12120e00", 'e': "00000c16180c00", 'f': "040a081c080800", 'g': "00000e120c100e",
    'h': "10101c12121200", 'i': "04000c04040e00", 'j': "02000202020a04", 'k': "10101418141200",
    'l': "0c040404040e00", 'm': "0000141e121200", 'n': "00001c12121200", 'o': "00000c12120c00",
    'p': "00001c12121c10", 'q': "00000e12120e02", 'r': "00001c12101000", 's': "00000e18061c00",
    't': "08081c08080600", 'u': "00001212120e00", 'v': "00000a0a0a0400", 'w': "000012121e1e00",
    'x': "0000120c0c1200", 'y': "000012120a0408", 'z': "00001e04081e00", '{': "02040c04040200",
    '|': "04040404040400", '}': "08040604040800", '~': "0a140000000000", '·': "00000c0c000000",
    '×': "0000120c0c1200", '÷': "000c001e000c00", '°': "040a0400000000", '±': "04041f04041f00",
}
# (what the log writes that the glyphs lack, as the nearest they have)
TYPOGRAPHY = {"\u2212": "-", "\u2013": "-", "\u2014": "-", "\u2192": ">", "\u2190": "<",
              "\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"', "\u2022": "\u00b7"}


def _cell(rows: str) -> bytes:
    ink = [[bool(int(rows[2 * y:2 * y + 2], 16) & (0x10 >> x)) for x in range(WIDTH)] for y in range(ROWS)]
    ink.append([False] * WIDTH)
    cell = bytearray(WIDTH * HEIGHT)
    for y in range(HEIGHT):
        for x in range(WIDTH):
            if ink[y][x]:
                cell[y * WIDTH + x] = FONT_INK
            elif x and y and ink[y - 1][x - 1]:
                cell[y * WIDTH + x] = FONT_SHADOW
    return bytes(cell)


class SmallFont:
    """The 5x7 glyphs as art.Font gives the game's: height, and glyph(ch): (width, the pixels)."""

    def __init__(self):
        self.height = HEIGHT
        self._cells = {ch: _cell(rows) for ch, rows in GLYPHS.items()}

    def glyph(self, ch: str) -> Tuple[int, bytes]:
        return WIDTH, self._cells.get(TYPOGRAPHY.get(ch, ch)) or self._cells["?"]
