"""The Options tab's switches (viewer.Viewer._options_changed, restore_defaults) on a real Loader
window: every switch the Loader reads (launch.CONTENT, game.RULE_SETTINGS, launch.SWITCH_DEFAULTS)
saved when one changes, and set back by Restore defaults; the picture and the music device; and the Help button, which opens the
player's guide; and Play Wake of the Ravager, beside Play Shattered Lands. Needs tkinter and a display (else skipped:
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
        # (the music devices as where they can't be read, a field to type in, whatever this
        # computer has: on Windows the real list has "Microsoft GS Wavetable Synth")
        devices = viewer.midiout.devices
        self.addCleanup(lambda: setattr(viewer.midiout, "devices", devices))
        viewer.midiout.devices = lambda: None

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
        v.picture.set("tv")
        v.engine.set("dosbox-x")
        v._show_midi(2)
        v._options_changed()
        settings = self.saved()
        self.assertEqual(settings["engine"], "dosbox-x")
        # (every switch off; the game changes with no switch, game.ALWAYS_ON, none of theirs written)
        self.assertEqual(launch.content(settings), {key: False for key in launch.CONTENT})
        self.assertFalse(set(settings) & game.ALWAYS_ON)
        for key, _ in game.RULE_SETTINGS:
            self.assertIs(settings.get(key), False, key)
        for key, default in launch.SWITCH_DEFAULTS.items():
            if key == "cycles":  # (the game's speed: saved by its own box, _speed_chosen)
                continue
            self.assertIn(key, settings, key)
            if default is True:
                self.assertIs(settings[key], False, key)
        self.assertEqual((settings["combat_log_level"], settings["rings"]), ("detail", "off"))
        self.assertEqual((settings["picture"], settings["midi_device"]), ("tv", 2))
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

    def test_engine(self):
        """The engine (Engine, from the next start): GOG's DOSBox unless DOSBox-X is chosen; the
        DOSBox-X program asked for, its version said, one too old for the memory file refused and
        not kept; the soundfont file; Restore defaults back to GOG's with the program remembered."""
        v = self.viewer
        dosboxx = viewer.dosboxx
        self.assertEqual(v.engine.get(), "gog")
        self.assertIn("engine", v.sections)
        d = os.path.dirname(launch.SETTINGS)
        old, new = os.path.join(d, "old-dosbox-x"), os.path.join(d, "dosbox-x")
        with open(old, "wb") as f:
            f.write(b"dosbox-x-2024.03.01.conf")
        with open(new, "wb") as f:
            f.write(b"dosbox-x-2026.10.01.conf")
        saved = viewer.filedialog.askopenfilename, viewer.messagebox.showerror, viewer.messagebox.askyesno
        self.addCleanup(lambda: (setattr(viewer.filedialog, "askopenfilename", saved[0]),
                                 setattr(viewer.messagebox, "showerror", saved[1]),
                                 setattr(viewer.messagebox, "askyesno", saved[2])))
        errors = []
        viewer.messagebox.showerror = lambda title, text, **k: errors.append(text)
        # DOSBox-X chosen with no program yet: remembered, and the status says it can't start
        v.engine.set("dosbox-x")
        v._engine_chosen()
        self.assertEqual(self.saved()["engine"], "dosbox-x")
        self.assertIn("can't start yet", v.status.get())
        self.assertIsNotNone(dosboxx.problem(self.saved()))
        # one too old: said, and not kept
        viewer.filedialog.askopenfilename = lambda **k: old
        v.choose_dosbox_x()
        self.assertEqual(len(errors), 1)
        self.assertIn("too old", errors[0])
        self.assertNotIn("dosbox_x_path", self.saved())
        # a new one: kept, its version shown
        viewer.filedialog.askopenfilename = lambda **k: new
        v.choose_dosbox_x()
        self.assertEqual(self.saved()["dosbox_x_path"], new)
        self.assertIn("2026.10.01", v.dosbox_x_status.get())
        self.assertIn("new enough", v.dosbox_x_status.get())
        self.assertIsNone(dosboxx.problem(self.saved()))
        self.assertEqual(launch.effective_switches(self.saved())["engine"], "dosbox-x")
        # nothing chosen in the dialog: nothing changed
        viewer.filedialog.askopenfilename = lambda **k: ""
        v.choose_dosbox_x()
        self.assertEqual(self.saved()["dosbox_x_path"], new)
        # the full screen keys named for the engine
        v.window_choice.set("Double (640x480)")
        v._window_chosen()
        self.assertIn("F12 and F", v.status.get())
        # the soundfont file
        font = os.path.join(d, "gm.sf2")
        open(font, "wb").close()
        viewer.filedialog.askopenfilename = lambda **k: font
        v.choose_soundfont()
        self.assertEqual(self.saved()["soundfont"], font)
        self.assertIn("gm.sf2", v.soundfont_status.get())
        self.assertIn(f"midiconfig={font}", dosboxx.midi_lines(self.saved()))
        v.no_soundfont()
        self.assertEqual(self.saved()["soundfont"], "")
        self.assertIn("mididevice=default", dosboxx.midi_lines(self.saved()))
        # back to GOG's
        v.engine.set("gog")
        v._engine_chosen()
        self.assertEqual(self.saved()["engine"], "gog")
        self.assertIn("GOG's DOSBox", v.status.get())
        v._window_chosen()
        self.assertIn("Alt+Enter", v.status.get())
        v.engine.set("dosbox-x")
        v._engine_chosen()
        viewer.messagebox.askyesno = lambda *a, **k: True
        v.restore_defaults()
        self.assertEqual((v.engine.get(), self.saved()["engine"]), ("gog", "gog"))
        self.assertEqual(self.saved()["dosbox_x_path"], new)  # (the program stays remembered)

    def test_a_stored_engine_the_loader_doesnt_know_is_gogs(self):
        with open(launch.SETTINGS, "w") as f:
            json.dump({"engine": "dosbox-y", "dosbox_x_path": 7, "soundfont": ["x"]}, f)
        v = viewer.Viewer(self.root, Layout.load(LAYOUT), lambda: (_ for _ in ()).throw(OSError("no game")))
        self.assertEqual(v.engine.get(), "gog")
        self.assertEqual((v.dosbox_x_path, v.soundfont), ("", ""))

    def test_picture_and_music_device(self):
        """The picture and the music device (Picture and music): each saved as it is chosen, in
        settings.json as launch.display_lines and midiout.conf_lines read them; a music device
        typed that is none is not kept; and stored values the Loader doesn't know are shown, and
        used, as the defaults."""
        v = self.viewer
        self.assertEqual((v.picture.get(), v._midi_value()), ("plain", "default"))
        self.assertIsNone(v.midi_names)  # (not read here, setUp: a field to type in)
        v.picture.set("scanlines")
        v._picture_chosen()
        self.assertEqual(self.saved()["picture"], "scanlines")
        self.assertIn("scaler=scan3x", launch.display_lines(self.saved()))
        self.assertIn("next start", v.status.get())
        v.window_choice.set("Single (320x240)")
        v._window_chosen()
        self.assertIn("plain in a Single window", v.status.get())
        self.assertEqual(self.saved()["picture"], "scanlines")  # (kept for a larger window)
        self.assertIn("scaler=none", launch.display_lines(self.saved()))
        v.picture.set("sharp")
        v._picture_chosen()
        self.assertIn("always plain", v.status.get())
        v.window_choice.set("Full screen")
        v._window_chosen()
        self.assertEqual(launch.display_lines(self.saved()), ["[sdl]", "output=openglnb", ""])
        for typed, stored in (("3", 3), ("128:0", "128:0"), ("", "default"), (" 1 ", 1)):
            v.midi_device.set(typed)
            v._midi_chosen()
            self.assertEqual(self.saved()["midi_device"], stored, typed)
            self.assertEqual(launch.midiout.setting(self.saved()), stored)
        v.midi_device.set("the loud one")
        v._midi_chosen()
        self.assertEqual(self.saved()["midi_device"], 1)
        self.assertEqual(v.midi_device.get(), "1")  # (back to the one remembered)
        self.assertIn("a number", v.status.get())
        v.midi_device.set("nonsense")  # (still in the field as another switch is changed: not saved)
        v.monster_info.set(False)
        v._options_changed()
        self.assertEqual(self.saved()["midi_device"], 1)

    def test_picture_and_music_device_as_stored(self):
        """A window opened on stored choices shows them; on ones it doesn't know, the defaults,
        and leaves the file as it is until something is chosen. With Windows' device names read,
        the music device is a list of them."""
        def window(settings, names=None):
            with open(launch.SETTINGS, "w") as f:
                json.dump(settings, f)
            real = viewer.midiout.devices
            viewer.midiout.devices = lambda: names
            try:
                root = tk.Toplevel(self.root)
                self.addCleanup(root.destroy)
                return viewer.Viewer(root, Layout.load(LAYOUT), lambda: (_ for _ in ()).throw(OSError("no game")))
            finally:
                viewer.midiout.devices = real
        v = window({"picture": "tv", "midi_device": "128:0"})
        self.assertEqual((v.picture.get(), v.midi_device.get(), v._midi_value()), ("tv", "128:0", "128:0"))
        v = window({"picture": "hologram", "midi_device": "the loud one"})
        self.assertEqual((v.picture.get(), v.midi_device.get(), v._midi_value()), ("plain", "", "default"))
        v.monster_info.set(False)
        v._options_changed()
        self.assertEqual((self.saved()["picture"], self.saved()["midi_device"]), ("hologram", "the loud one"))
        self.assertEqual(launch.effective_switches(self.saved())["picture"], "plain")
        names = ["Microsoft GS Wavetable Synth", "A soundfont synth"]
        v = window({"midi_device": 1}, names)
        self.assertEqual(v.midi_device.get(), "1: A soundfont synth")
        self.assertEqual(list(v.midi_box.cget("values")), ["Windows' default", "0: Microsoft GS Wavetable Synth",
                                                           "1: A soundfont synth"])
        v.midi_device.set("0: Microsoft GS Wavetable Synth")
        v._midi_chosen()
        self.assertEqual(self.saved()["midi_device"], 0)
        v = window({"midi_device": 4}, names)  # (a device that isn't there now)
        self.assertEqual(v.midi_device.get(), "4: (no such device now: no music)")
        self.assertEqual(v._midi_value(), 4)
        asked = viewer.messagebox.askyesno
        viewer.messagebox.askyesno = lambda *a, **k: True
        try:
            v.restore_defaults()
        finally:
            viewer.messagebox.askyesno = asked
        self.assertEqual((v.midi_device.get(), self.saved()["midi_device"], self.saved()["picture"]),
                         ("Windows' default", "default", "plain"))

    def test_help_opens_the_manual(self):
        """Help, at the top of the window, opens the manual's start page (manual/index.html, beside
        the Loader) in the browser as a file URL; where no browser opens it, the status line says
        where it is."""
        def buttons(widget):
            for child in widget.winfo_children():
                if isinstance(child, viewer.ttk.Button):
                    yield child
                yield from buttons(child)
        help_ = [b for b in buttons(self.root) if b.cget("text") == "Help"]
        self.assertEqual(len(help_), 1)
        self.assertTrue(os.path.isfile(viewer.HELP_PAGE), viewer.HELP_PAGE)
        opened = []
        real = viewer.webbrowser.open
        self.addCleanup(lambda: setattr(viewer.webbrowser, "open", real))
        viewer.webbrowser.open = lambda url: opened.append(url) or True
        help_[0].invoke()
        self.assertEqual(len(opened), 1)
        self.assertTrue(opened[0].startswith("file:") and opened[0].endswith("/manual/index.html"), opened)
        self.assertIn("index.html", self.viewer.status.get())  # (said even when it opened)
        viewer.webbrowser.open = lambda url: False
        self.viewer.open_guide()
        self.assertIn(os.path.join("manual", "index.html"), self.viewer.status.get())

    def _ravager_button(self, found):
        """Play Wake of the Ravager pressed with ravager.find_dir answering FOUND: what launch.launch
        was given and the message boxes shown."""
        from dsloader import ravager
        started, shown = [], []

        class Running:
            args, pid, returncode = ["DOSBox.exe"], 1, None

            def poll(self):
                return None
        for module, name, stand_in in (
                (ravager, "find_dir", lambda sl_dir=None, given=None: found),
                (launch, "launch", lambda game_dir, what="": started.append(game_dir) or (Running(), None)),
                (viewer.messagebox, "showinfo", lambda *a, **k: shown.append(a)),
                (viewer.messagebox, "showerror", lambda *a, **k: shown.append(a))):
            real = getattr(module, name)
            self.addCleanup(setattr, module, name, real)
            setattr(module, name, stand_in)
        def every(widget):
            for child in widget.winfo_children():
                yield child
                yield from every(child)
        buttons = [b for b in every(self.root)
                   if isinstance(b, viewer.ttk.Button) and b.cget("text") == "Play Wake of the Ravager"]
        self.assertEqual(len(buttons), 1)
        self.assertFalse(buttons[0].instate(["disabled"]))
        buttons[0].invoke()
        return started, shown, buttons[0]

    def test_top_row_wraps_when_narrow(self):
        """The right-hand group of the top row (Game window, Text size, Freeze report...) goes under
        the start buttons, whole, exactly when the row is too narrow for both groups, and is beside
        them otherwise. (Measured, not by fixed widths: the fonts, and the widest window the
        screen allows, differ from one computer to another.)"""
        row, starts, top = self.viewer.top_row
        self.root.deiconify()
        need = None
        for width in (1080, 2400):
            self.root.geometry(f"{width}x700")
            self.root.update()
            self.viewer._wrap_top()
            self.root.update()
            need = starts.winfo_reqwidth() + top.winfo_reqwidth()
            wrapped = need > row.winfo_width() - 12
            self.assertEqual(int(top.grid_info()["row"]), 1 if wrapped else 0, (width, row.winfo_width(), need))
            self.assertLessEqual(top.winfo_reqwidth(), row.winfo_width(), width)
        # (so narrow that it must wrap, wherever it runs: below the Loader's least width)
        self.root.minsize(1, 1)
        self.root.geometry(f"{need // 2}x700")
        self.root.update()
        self.viewer._wrap_top()
        self.assertEqual(int(top.grid_info()["row"]), 1)

    def test_ravager_button_not_found(self):
        """Without the sequel found, the button starts nothing and points to Options' Choose its folder..."""
        started, shown, _ = self._ravager_button(None)
        self.assertEqual(started, [])
        self.assertEqual(len(shown), 1)
        self.assertIn("Choose its folder...", shown[0][1])
        self.assertIsNone(self.viewer.dosbox)

    def test_ravager_button_starts_the_sequel(self):
        """Found, the button starts the game in the sequel's folder (launch._launch runs it as Wake of
        the Ravager), says what isn't ported yet, and both start buttons wait for the game to close."""
        folder = os.path.join(os.sep, "games", "Dark Sun 2")
        started, shown, button = self._ravager_button(folder)
        self.assertEqual((started, shown), ([folder], []))
        self.assertEqual(self.viewer._game_dir, folder)
        self.assertIn(launch.RAVAGER_NO_LOG[1:], self.viewer.dice_text.get("1.0", "end"))
        self.assertTrue(button.instate(["disabled"]))
        self.assertTrue(self.viewer.start_button.instate(["disabled"]))


    def test_take_the_party_across(self):
        """Take the party to Wake of the Ravager (Options, Wake of the Ravager): the save picked, asked,
        ravtransfer.transfer run with the folders, its report shown in a window of its own; nothing run
        without the sequel's folder or when the player says no."""
        from dsloader import ravager, ravtransfer, wotrart
        mod = viewer
        real = (launch.find_game_dir, wotrart.find_resources, ravager.is_wotr_dir, mod.filedialog.askopenfilename,
                mod.messagebox.askyesno, mod.messagebox.showinfo, ravtransfer.transfer)

        def put_back():
            (launch.find_game_dir, wotrart.find_resources, ravager.is_wotr_dir, mod.filedialog.askopenfilename,
             mod.messagebox.askyesno, mod.messagebox.showinfo, ravtransfer.transfer) = real
        self.addCleanup(put_back)
        calls, told = [], []
        launch.find_game_dir = lambda: "/sl"
        wotrart.find_resources = lambda sl, given=None: "/wotr/RESOURCE.GFF"
        ravager.is_wotr_dir = lambda folder: folder == "/wotr"
        mod.filedialog.askopenfilename = lambda **kw: "/sl/SAVE03.SAV"
        mod.messagebox.showinfo = lambda *a, **kw: told.append(a)
        mod.messagebox.askyesno = lambda *a, **kw: False
        ravtransfer.transfer = lambda *a: calls.append(a) or "Lex: place 4 of the roster\n"
        self.viewer.take_party_to_wotr()
        self.assertEqual(calls, [])  # (said no)
        mod.messagebox.askyesno = lambda *a, **kw: True
        self.viewer.take_party_to_wotr()
        self.assertEqual(calls, [("/sl/SAVE03.SAV", "/wotr", "/sl", launch.DOS_DIR)])
        texts = [w for w in self.root.winfo_children() if isinstance(w, tk.Toplevel)]
        self.assertTrue(any("Lex: place 4" in c.get("1.0", "end") for t in texts for c in t.winfo_children()
                            if isinstance(c, tk.Text)))
        ravager.is_wotr_dir = lambda folder: False
        self.viewer.take_party_to_wotr()
        self.assertEqual(len(calls), 1)
        self.assertIn("hasn't found Wake of the Ravager", told[-1][1])


if __name__ == "__main__":
    unittest.main()
