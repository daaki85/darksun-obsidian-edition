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

    def test_the_tabs_names_show_whole(self):
        """Six tabs, each with its Alt letter, and the divider placed so the right-hand pane is at
        least as wide as their names need (a narrower notebook cuts every name short: "Dice lo",
        "Journa"), at the window's default size and at its smallest."""
        from tkinter import font as tkfont
        v = self.window()
        names = [v.tabs.tab(t, "text") for t in v.tabs.tabs()]
        self.assertEqual(names, ["Dice log", "Dialogue", "Journal", "Spells", "Memory tools", "Options"])
        letters = [name[int(v.tabs.tab(t, "underline"))].lower() for name, t in zip(names, v.tabs.tabs())]
        self.assertEqual(letters, ["l", "i", "j", "s", "m", "o"])  # (Alt+L, Alt+I, Alt+J, Alt+S, Alt+M, Alt+O)
        need = viewer.tabs_width(v.tabs)
        font = tkfont.Font(root=self.root, font=viewer.ttk.Style(self.root).lookup("TNotebook.Tab", "font"))
        self.assertGreaterEqual(need, sum(font.measure(n) + 2 * viewer.theme.TAB_PADDING[0] for n in names))
        for width in (1320, 1080):
            placed = []
            with mock.patch.object(v.panes, "winfo_width", lambda: width), \
                    mock.patch.object(v.panes, "sashpos", lambda i, at: placed.append(at) or at):
                v._fit_party()
            self.assertEqual(len(placed), 1)
            self.assertGreaterEqual(width - placed[0], need, width)
            self.assertGreaterEqual(width - placed[0], v.tools_tab.winfo_reqwidth(), width)

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
        launch.save_settings({"steady_pace": False, "monster_info": False, "helm_ac": False, "game_dir": "C:\\GOG"})
        real_open = builtins.open

        def locked(path, *args, **kwargs):
            if path == launch.SETTINGS:
                raise PermissionError(13, "in use", path)
            return real_open(path, *args, **kwargs)
        with mock.patch("builtins.open", locked), mock.patch("time.sleep"):
            v = self.window()
        self.assertTrue(v._options_unread)
        self.assertTrue(v.steady_pace.get())  # (the defaults shown...)
        self.assertIn("shows the defaults", v.status.get())
        v.rule_vars["best_hit_die"].set(False)  # (...and one switch changed once the file can be read)
        v._options_changed()
        settings = self.saved()
        self.assertIs(settings["best_hit_die"], False)
        self.assertEqual((settings["steady_pace"], settings["monster_info"], settings["helm_ac"], settings["game_dir"]),
                         (False, False, False, "C:\\GOG"))  # (the player's other choices kept)

    def test_only_the_switch_changed_is_saved(self):
        """Another writer's change to another switch since the tab was read stays."""
        v = self.window()
        launch.update_settings({"steady_pace": False})
        v.monster_info.set(False)
        v._options_changed()
        settings = self.saved()
        self.assertEqual((settings["steady_pace"], settings["monster_info"]), (False, False))

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

    def attach_once(self, v, held=False):
        """One try at following the game, with a stand-in dice log whose attach fails (a plain
        game); settings.json HELD elsewhere as it is read. The stand-in."""
        made = []

        def Log(guest):
            log = mock.MagicMock()
            log.attached = False
            log.attach.side_effect = viewer.DiceLogError("not the patched game")
            made.append(log)
            return log
        real_open = builtins.open

        def locked(path, *args, **kwargs):
            if held and path == launch.SETTINGS:
                raise PermissionError(13, "in use", path)
            return real_open(path, *args, **kwargs)
        v.guest, v.next_try = object(), 0.0
        with mock.patch.object(viewer, "DiceLog", Log), mock.patch("builtins.open", locked), mock.patch("time.sleep"):
            v._dice_step()
        return made[0]

    def test_attach_reads_the_pockets_strictly_and_lets_the_lock_go(self):
        """settings.json held as the window first follows the game: the dice log is told its list
        of pockets isn't the saved one (nothing saved over it); an attach that fails lets the
        game's lock go (`play` not refused meanwhile), taken again at the next try."""
        launch.save_settings({"pickpocketed": ["Dag|41|7|Trader@500"]})
        v = self.window()
        log = self.attach_once(v, held=True)
        args, kwargs = log.use_settings.call_args
        self.assertEqual((args[0], kwargs.get("picked_known")), ({}, False))
        log.attach.assert_called_once()
        self.assertFalse(launch.holds_game())
        self.assertIn("not the patched game", v.dice_status.get())

    def test_attach_with_the_settings_read(self):
        launch.save_settings({"pickpocketed": ["Dag|41|7|Trader@500"]})
        v = self.window()
        log = self.attach_once(v)
        args, kwargs = log.use_settings.call_args
        self.assertEqual(args[0]["pickpocketed"], ["Dag|41|7|Trader@500"])
        self.assertIs(kwargs.get("picked_known"), True)
        log.load_picked.assert_not_called()  # (not read a second time, non-strictly)


if __name__ == "__main__":
    unittest.main()
