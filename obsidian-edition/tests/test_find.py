"""The logs' find box (viewer.Viewer._find_bar), on a real Tk text widget."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import tkinter as tk
    from tkinter import ttk
    from dsloader import viewer
except ImportError:  # no tkinter in this Python
    viewer = None


def make_root():
    try:
        return tk.Tk()
    except tk.TclError:  # (no display)
        return None


@unittest.skipIf(viewer is None, "needs tkinter")
class FindTests(unittest.TestCase):
    def setUp(self):
        self.root = make_root()
        if self.root is None:
            self.skipTest("needs a display")
        self.text = tk.Text(self.root)
        self.text.insert("end", "Gerakis attacks Slig\nCilla tries to find/remove traps\nSlig is killed\n")
        self.text.insert("end", "    THAC0 17 = 17\n", "detail")
        row = ttk.Frame(self.root)
        tab = ttk.Frame(self.root)
        host = type("Host", (), {})()
        host._following, host._finds, host.root = {self.text: True}, {}, self.root
        viewer.Viewer._find_bar(host, row, self.text, tab)
        self.host, self.entry = host, host._finds[tab]
        self.where = row.winfo_children()[-1]
        row.pack()
        self.text.pack()
        self.root.update()

    def tearDown(self):
        if self.root is not None:
            self.root.destroy()

    def find(self, word, key="<Return>", times=1):
        self.entry.delete(0, "end")
        self.entry.insert(0, word)
        self.entry.focus_force()
        self.root.update()
        for _ in range(times):
            self.entry.event_generate(key)

    def shown(self):
        return self.text.get(*self.text.tag_ranges("found_now")) if self.text.tag_ranges("found_now") else None

    def test_next_and_count(self):
        """Every match marked, the current one too, with which of how many; any case."""
        self.find("slig")
        self.assertEqual(len(self.text.tag_ranges("found")), 4)  # (two matches: start and end each)
        self.assertEqual(self.text.index(self.text.tag_ranges("found_now")[0]), "1.16")
        self.assertEqual(self.root.getvar(self.where.cget("textvariable")), "1 of 2")
        self.entry.event_generate("<Return>")
        self.assertEqual(self.text.index(self.text.tag_ranges("found_now")[0]), "3.0")
        self.assertEqual(self.root.getvar(self.where.cget("textvariable")), "2 of 2")
        self.entry.event_generate("<Return>")  # (round to the first again)
        self.assertEqual(self.text.index(self.text.tag_ranges("found_now")[0]), "1.16")
        self.assertFalse(self.host._following[self.text])  # (new lines don't take the match away)

    def test_previous_and_clear(self):
        self.find("slig", "<Shift-Return>")
        self.assertEqual(self.text.index(self.text.tag_ranges("found_now")[0]), "3.0")
        self.entry.event_generate("<Escape>")
        self.assertEqual(self.entry.get(), "")
        self.assertEqual(self.text.tag_ranges("found"), ())

    def test_hidden_details_left_out(self):
        self.text.tag_configure("detail", elide=True)
        self.find("THAC0")
        self.assertEqual(self.root.getvar(self.where.cget("textvariable")), "no match")
        self.text.tag_configure("detail", elide=False)
        self.find("THAC0")
        self.assertEqual(self.shown(), "THAC0")


if __name__ == "__main__":
    unittest.main()
