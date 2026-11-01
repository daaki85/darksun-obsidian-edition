"""The web pages' fonts, inside the pages themselves: Marcellus SC, Alegreya Sans and IBM Plex Mono
(their Latin sets as Google Fonts serves them, in fonts/, with their SIL Open Font Licences), so a
page needs nothing from the internet and looks the same saved or passed on."""

import base64
import os

FONTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")

# (family, style, weight, file)
FACES = (("Marcellus SC", "normal", 400, "MarcellusSC-400.woff2"),
         ("Alegreya Sans", "normal", 400, "AlegreyaSans-400.woff2"),
         ("Alegreya Sans", "italic", 400, "AlegreyaSans-400i.woff2"),
         ("Alegreya Sans", "normal", 500, "AlegreyaSans-500.woff2"),
         ("Alegreya Sans", "normal", 700, "AlegreyaSans-700.woff2"),
         ("IBM Plex Mono", "normal", 400, "IBMPlexMono-400.woff2"),
         ("IBM Plex Mono", "normal", 500, "IBMPlexMono-500.woff2"))

# Google's Latin set: what falls outside it comes from the next font in the family's list
LATIN = ("U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, "
         "U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD")


def faces() -> str:
    """The @font-face rules, each font as a data: URL."""
    out = ["/* Marcellus SC, Alegreya Sans and IBM Plex Mono: SIL Open Font License 1.1 "
           "(obsidian-edition/dsloader/fonts) */"]
    for family, style, weight, name in FACES:
        with open(os.path.join(FONTS, name), "rb") as f:
            data = base64.b64encode(f.read()).decode("ascii")
        out.append(f'@font-face {{ font-family: "{family}"; font-style: {style}; font-weight: {weight}; '
                   f'font-display: swap; src: url(data:font/woff2;base64,{data}) format("woff2"); '
                   f'unicode-range: {LATIN}; }}')
    return "\n".join(out) + "\n"
