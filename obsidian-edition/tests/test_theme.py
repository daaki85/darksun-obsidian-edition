"""Accessibility checks on the window's colours (AODA: WCAG 2.0 level AA)."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import palette

try:
    import tkinter as tk
    from dsloader import theme
except ImportError:  # (a Python without tkinter)
    tk = None


def _root():
    """A hidden window, or None without tkinter or a display."""
    if tk is None:
        return None
    try:
        root = tk.Tk()
    except tk.TclError:
        return None
    root.withdraw()
    return root


class ContrastTests(unittest.TestCase):
    def test_contrast_formula(self):
        self.assertAlmostEqual(palette.contrast("#000000", "#FFFFFF"), 21.0, places=3)
        self.assertAlmostEqual(palette.contrast("#777777", "#FFFFFF"), 4.48, places=2)

    def test_every_text_colour_meets_aa(self):
        for use, (text, background) in palette.TEXT_PAIRS.items():
            with self.subTest(use):
                self.assertGreaterEqual(palette.contrast(text, background), 4.5,
                                        f"{use}: {text} on {background}")

    def test_the_rock_behind_the_title_is_dark_enough_everywhere(self):
        for rock in palette.ROCK:
            self.assertGreaterEqual(palette.contrast(palette.AMBER, rock), 4.5, rock)
            self.assertGreaterEqual(palette.contrast(palette.SAND, rock), 4.5, rock)


class SectionTests(unittest.TestCase):
    """The Options tab's sections that open and close."""

    def setUp(self):
        self.root = _root()
        if self.root is None:
            self.skipTest("no tkinter or no display")
        theme.apply(self.root)
        self.addCleanup(self.root.destroy)

    def test_opens_and_closes(self):
        seen = []
        part = theme.Section(self.root, "Rule changes", on_toggle=seen.append)
        part.pack()
        self.assertFalse(part.is_open)
        self.assertEqual(part.header.cget("text"), "\u25b8  Rule changes")
        self.assertFalse(part.body.winfo_manager())
        part.header.invoke()
        self.assertTrue(part.is_open)
        self.assertEqual(part.header.cget("text"), "\u25be  Rule changes")
        self.assertEqual(part.body.winfo_manager(), "pack")
        self.root.deiconify()  # (keys go to a shown window's focus)
        part.header.focus_force()
        self.root.update()
        part.header.event_generate("<Return>")
        self.assertFalse(part.is_open)
        self.assertEqual(seen, [True, False])

    def test_starts_open(self):
        part = theme.Section(self.root, "Dice log", open_=True)
        self.assertTrue(part.is_open)
        self.assertEqual(part.body.winfo_manager(), "pack")


if __name__ == "__main__":
    unittest.main()
