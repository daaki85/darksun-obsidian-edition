"""The Options tab's switches (viewer.Viewer._options_changed, restore_defaults) on a real Loader
window: every switch the Loader reads (launch.CONTENT, game.RULE_SETTINGS, launch.SWITCH_DEFAULTS)
saved when one changes, and set back by Restore defaults. Needs tkinter and a display (else skipped:
run under xvfb-run for it)."""

import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import game, launch  # noqa: E402

try:
    import tkinter as tk
    from dsloader import viewer
    from dsloader.layout import Layout
except ImportError:  # no tkinter in this Python
    viewer = None

LAYOUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "layouts", "shattered_lands.json")


@unittest.skipIf(viewer is None, "needs tkinter")
class OptionsTests(unittest.TestCase):
    def setUp(self):
        try:
            self.root = tk.Tk()
        except tk.TclError:
            self.skipTest("needs a display")
        self.root.withdraw()
        self.addCleanup(self.root.destroy)
        d = tempfile.mkdtemp()
        self.addCleanup(lambda: __import__("shutil").rmtree(d, ignore_errors=True))
        saved = launch.SETTINGS, launch.find_game_dir
        self.addCleanup(lambda: (setattr(launch, "SETTINGS", saved[0]), setattr(launch, "find_game_dir", saved[1])))
        launch.SETTINGS = os.path.join(d, "settings.json")
        launch.find_game_dir = lambda: None

        def no_game():
            raise OSError("no game in a test")
        self.viewer = viewer.Viewer(self.root, Layout.load(LAYOUT), no_game)
        self.root.update_idletasks()

    def saved(self):
        with open(launch.SETTINGS) as f:
            return json.load(f)

    def booleans(self):
        """Every switch box of the window (its BooleanVars), the content's and the rules' among them."""
        v = self.viewer
        out = [var for var in vars(v).values() if isinstance(var, tk.BooleanVar)]
        return out + list(v.content_vars.values()) + list(v.rule_vars.values())

    def test_every_switch_saved_and_restored(self):
        v = self.viewer
        for var in self.booleans():
            var.set(False)
        v.combat_log_level.set("detail")
        v.ring_mode.set("off")
        v._options_changed()
        settings = self.saved()
        self.assertEqual(launch.content(settings), {key: False for key in launch.CONTENT})
        for key, _ in game.RULE_SETTINGS:
            self.assertIs(settings.get(key), False, key)
        for key, default in launch.SWITCH_DEFAULTS.items():
            if key == "cycles":  # (the game's speed: saved by its own box, _speed_chosen)
                continue
            self.assertIn(key, settings, key)
            if default is True:
                self.assertIs(settings[key], False, key)
        self.assertEqual((settings["combat_log_level"], settings["rings"]), ("detail", "off"))
        asked = viewer.messagebox.askyesno
        viewer.messagebox.askyesno = lambda *a, **k: True
        try:
            v.game_speed.set("20000")
            v.restore_defaults()
        finally:
            viewer.messagebox.askyesno = asked
        settings = self.saved()
        self.assertEqual(launch.content(settings), {key: True for key in launch.CONTENT})
        for key, _ in game.RULE_SETTINGS:
            self.assertIs(settings.get(key), True, key)
        for key, default in launch.SWITCH_DEFAULTS.items():
            self.assertEqual(settings.get(key), default, key)
        self.assertEqual(launch.effective_switches(settings), launch.effective_switches({}))


if __name__ == "__main__":
    unittest.main()
