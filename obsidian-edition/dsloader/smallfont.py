"""The combat log panel's small font: 7 pixels a line, its shadow in it.

The glyphs are the X11 misc-fixed 4x6 font's ("Public domain font. Share and enjoy."), ASCII and a
few more: each 6 rows of a hex digit (its bits the 4 columns, 8 the leftmost), set in a cell 4 wide
and 7 high with the shadow a pixel down and right, as the game's own font has it (none past the
cell's right edge). It reads as art.Font does (height, glyph), so the panel draws it as it drew the
game's."""

from typing import Dict, Tuple

FONT_INK, FONT_SHADOW = 254, 20  # (art.FONT_INK, FONT_SHADOW)
WIDTH, HEIGHT = 4, 7

GLYPHS: Dict[str, str] = {
    ' ': "000000", '!': "444040", '"': "aa0000", '#': "afafa0", '$': "4ec2e4", '%': "824820", '&': "4a4a50",
    "'": "440000", '(': "244442", ')': "844448", '*': "a4e4a0", '+': "44e440", ',': "000048", '-': "00e000",
    '.': "000040", '/': "224880", '0': "4aea40", '1': "4c44e0", '2': "4a24e0", '3': "e242c0", '4': "aae220",
    '5': "e8c2c0", '6': "68ca40", '7': "e24880", '8': "6a4ac0", '9': "4a62c0", ':': "040040", ';': "040048",
    '<': "248420", '=': "0e0e00", '>': "842480", '?': "c24040", '@': "6aa860", 'A': "4aeaa0", 'B': "cacac0",
    'C': "4a8a40", 'D': "caaac0", 'E': "e8c8e0", 'F': "e8c880", 'G': "68aa60", 'H': "aaeaa0", 'I': "e444e0",
    'J': "222a40", 'K': "aacaa0", 'L': "8888e0", 'M': "aeeaa0", 'N': "2aea80", 'O': "4aaa40", 'P': "cac880",
    'Q': "4aaa42", 'R': "cacaa0", 'S': "6842c0", 'T': "e44440", 'U': "aaaae0", 'V': "aaae40", 'W': "aaeea0",
    'X': "aa4aa0", 'Y': "aa4440", 'Z': "e248e0", '[': "644460", '\\': "884220", ']': "c444c0", '^': "4a0000",
    '_': "00000e", '`': "420000", 'a': "06aa60", 'b': "8caac0", 'c': "068860", 'd': "26aa60", 'e': "04ac60",
    'f': "24e440", 'g': "06a62c", 'h': "8caaa0", 'i': "40c4e0", 'j': "20222c", 'k': "8acaa0", 'l': "c444e0",
    'm': "0aeaa0", 'n': "0caaa0", 'o': "04aa40", 'p': "0cac88", 'q': "06aa62", 'r': "0ac880", 's': "06c2c0",
    't': "4e4420", 'u': "0aaa60", 'v': "0aaa40", 'w': "0aaea0", 'x': "0a44a0", 'y': "0aa62c", 'z': "0e24e0",
    '{': "24c442", '|': "444440", '}': "846448", '~': "5a0000", '·': "004000", '×': "0a4a00", '÷': "40e040",
    '°': "4a4000", '±': "4e40e0",
}
# (what the log writes that the glyphs lack, as the nearest they have)
TYPOGRAPHY = {"\u2212": "-", "\u2013": "-", "\u2014": "-", "\u2192": ">", "\u2190": "<",
              "\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"', "\u2022": "\u00b7"}


def _cell(rows: str) -> bytes:
    ink = [[bool(int(r, 16) & (8 >> x)) for x in range(WIDTH)] for r in rows] + [[False] * WIDTH]
    cell = bytearray(WIDTH * HEIGHT)
    for y in range(HEIGHT):
        for x in range(WIDTH):
            if ink[y][x]:
                cell[y * WIDTH + x] = FONT_INK
            elif x and y and ink[y - 1][x - 1]:
                cell[y * WIDTH + x] = FONT_SHADOW
    return bytes(cell)


class SmallFont:
    """The 4x6 glyphs as art.Font gives the game's: height, and glyph(ch): (width, the pixels)."""

    def __init__(self):
        self.height = HEIGHT
        self._cells = {ch: _cell(rows) for ch, rows in GLYPHS.items()}

    def glyph(self, ch: str) -> Tuple[int, bytes]:
        return WIDTH, self._cells.get(TYPOGRAPHY.get(ch, ch)) or self._cells["?"]
