"""The Loader's window with settings.json held elsewhere as it opens (the Options tab shows the
defaults and says so, and a switch then changed is saved alone, never the defaults over the
player's other choices), and attaching to the DOSBox it started by that one's pid. Needs tkinter
and a display (else skipped: run under xvfb-run for it)."""

import builtins
import json
import os
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import launch  # noqa: E402

try:
    import tkinter as tk
    from dsloader import viewer
    from dsloader.layout import Layout
except ImportError:  # no tkinter in this Python
    viewer = None

LAYOUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "layouts", "shattered_lands.json")


class Running:
    """A stand-in for the DOSBox process the window started."""
    pid = 4242

    def poll(self):
        return None


@unittest.skipIf(viewer is None, "needs tkinter")
class ViewerSettingsTests(unittest.TestCase):
    def setUp(self):
        try:
            self.root = tk.Tk()
        except tk.TclError:
            self.skipTest("needs a display")
        self.root.withdraw()
        self.addCleanup(self.root.destroy)
        d = tempfile.mkdtemp()
        self.addCleanup(lambda: __import__("shutil").rmtree(d, ignore_errors=True))
        for name, value in (("SETTINGS", os.path.join(d, "settings.json")), ("GAME_LOCK", os.path.join(d, "game.lock")),
                            ("find_game_dir", lambda *a: None)):
            patcher = mock.patch.object(launch, name, value)
            patcher.start()
            self.addCleanup(patcher.stop)
        self.addCleanup(launch.release_game)

    def window(self, **kwargs):
        def no_game():
            raise OSError("no game in a test")
        v = viewer.Viewer(self.root, Layout.load(LAYOUT), kwargs.pop("connect", no_game), **kwargs)
        self.root.update_idletasks()
        return v

    def saved(self):
        with open(launch.SETTINGS) as f:
            return json.load(f)

    def test_an_unreadable_file_is_never_saved_over_with_the_defaults(self):
        launch.save_settings({"dust": False, "shadows": False, "helm_ac": False, "game_dir": "C:\\GOG"})
        real_open = builtins.open

        def locked(path, *args, **kwargs):
            if path == launch.SETTINGS:
                raise PermissionError(13, "in use", path)
            return real_open(path, *args, **kwargs)
        with mock.patch("builtins.open", locked), mock.patch("time.sleep"):
            v = self.window()
        self.assertTrue(v._options_unread)
        self.assertTrue(v.show_dust.get())  # (the defaults shown...)
        self.assertIn("shows the defaults", v.status.get())
        v.rule_vars["two_weapons"].set(False)  # (...and one switch changed once the file can be read)
        v._options_changed()
        settings = self.saved()
        self.assertIs(settings["two_weapons"], False)
        self.assertEqual((settings["dust"], settings["shadows"], settings["helm_ac"], settings["game_dir"]),
                         (False, False, False, "C:\\GOG"))  # (the player's other choices kept)

    def test_only_the_switch_changed_is_saved(self):
        """Another writer's change to another switch since the tab was read stays."""
        v = self.window()
        launch.update_settings({"dust": False})
        v.show_shadows.set(False)
        v._options_changed()
        settings = self.saved()
        self.assertEqual((settings["dust"], settings["shadows"]), (False, False))

    def test_the_started_dosbox_attached_by_its_pid(self):
        asked = []

        def by_pid(pid):
            asked.append(pid)
            raise OSError("not yet")

        def by_name():
            asked.append("by name")
            raise OSError("several DOSBox processes")
        v = self.window(connect=by_name, connect_pid=by_pid, dosbox=Running())
        self.assertEqual(asked, [4242])
        v.dosbox = None
        v.reconnect()
        self.assertEqual(asked, [4242, "by name"])

    def test_the_lock_let_go_when_the_game_closes(self):
        v = self.window()
        launch.hold_game("the Loader's window")
        v.dosbox = Running()
        v._release_game()  # (still running: kept)
        self.assertTrue(launch.holds_game())
        v.dosbox = None
        v._release_game()
        self.assertFalse(launch.holds_game())


if __name__ == "__main__":
    unittest.main()
