import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import launch


def make_game(root: str, cloud_saves: bool) -> str:
    game = os.path.join(root, "Dark Sun Shattered Lands")
    os.makedirs(os.path.join(game, "DOSBOX"))
    for path in ("DSUN.EXE", os.path.join("DOSBOX", "DOSBox.exe"), "dosbox_darksun.conf"):
        open(os.path.join(game, path), "w").close()
    if cloud_saves:
        os.mkdir(os.path.join(game, "cloud_saves"))
    return game


def native(path: str) -> None:
    """A stand-in for a Windows program: an MZ header pointing at a PE signature."""
    head = bytearray(0x48)
    head[:2], head[0x3C:0x40], head[0x40:0x44] = b"MZ", (0x40).to_bytes(4, "little"), b"PE\0\0"
    with open(path, "wb") as f:
        f.write(head)


class LaunchTests(unittest.TestCase):
    def test_the_games_dos_program_is_not_it(self):
        """The game's own DSUN.EXE (DOS: an MZ header, no PE) beside the mod's folder, as when the
        mod is unzipped in the game's folder (Windows finds it as dsun.exe), is not the recompiled
        program; a Windows program of that name is; and a named path that is no program is passed
        over."""
        with tempfile.TemporaryDirectory() as d:
            mod = os.path.join(d, "mod")
            os.mkdir(mod)
            beside = os.path.join(d, launch.RECOMPILED_EXE)
            with open(beside, "wb") as f:
                f.write(b"MZ" + bytes(0x3A) + (0x40).to_bytes(4, "little") + b"\x0e\x1f\xba\x0e")
            self.assertFalse(launch.native_program(beside))
            self.assertIsNone(launch.found_recompiled_program(mod))
            native(beside)
            self.assertTrue(launch.native_program(beside))
            self.assertEqual(launch.found_recompiled_program(mod), beside)
            dos = os.path.join(d, "DSUN.EXE")
            with open(dos, "wb") as f:
                f.write(b"MZ" + bytes(0x60))
            self.assertNotEqual(launch.recompiled_program({"recompiled": dos}), dos)

    def test_started_and_closed_lines(self):
        """The log says which runs, and names it when it closes, by what was started."""
        saved = launch.STARTED
        try:
            launch.STARTED = None
            self.assertIn("in DOSBox", launch.started_line("G"))
            self.assertEqual(launch.closed_line(0), "DOSBox closed.")
            launch.STARTED = "C:/dsr/dsun.exe"
            self.assertIn("as Dark Sun Recompiled (C:/dsr/dsun.exe)", launch.started_line("G"))
            self.assertEqual(launch.closed_line(0), "Dark Sun Recompiled closed.")
            self.assertEqual(launch.closed_line(3), "Dark Sun Recompiled closed with exit code 3.")
            self.assertIn("Dark Sun Recompiled closed: it crashed (an access violation", launch.closed_line(0xC0000005))
        finally:
            launch.STARTED = saved

    def test_the_recompiled_program_instead_of_dosbox(self):
        with tempfile.TemporaryDirectory() as d:
            os.mkdir(os.path.join(d, "recompiled"))
            program = os.path.join(d, "recompiled", "dsun.exe")   # (not DSUN.EXE: the game's own)
            native(program)
            game = os.path.join(d, "game")
            os.mkdir(game)
            open(os.path.join(game, "DSUN.EXE"), "w").close()      # the data files, no DOSBox
            settings = {"recompiled": program}
            self.assertEqual(launch.recompiled_program(settings), program)
            self.assertIsNone(launch.recompiled_program({"recompiled": False}))     # --dosbox
            self.assertEqual(launch.recompiled_program({"recompiled": os.path.join(d, "gone.exe")}),
                             launch.found_recompiled_program())                       # a bad path: whatever is beside the mod
            # the program found where a player would unzip it: in the mod's folder (recompiled\),
            # or beside the mod's folder
            mod = os.path.join(d, "mod")
            os.makedirs(os.path.join(mod, "recompiled"))
            self.assertIsNone(launch.found_recompiled_program(mod))
            native(os.path.join(mod, "recompiled", launch.RECOMPILED_EXE))
            self.assertEqual(launch.found_recompiled_program(mod), os.path.join(mod, "recompiled", launch.RECOMPILED_EXE))
            os.remove(os.path.join(mod, "recompiled", launch.RECOMPILED_EXE))
            os.makedirs(os.path.join(d, "darksun-recompiled-windows-x64", "windows"))
            beside = os.path.join(d, "darksun-recompiled-windows-x64", "windows", launch.RECOMPILED_EXE)
            native(beside)
            self.assertEqual(launch.found_recompiled_program(mod), beside)
            self.assertEqual(launch.recompiled_command(program, game),
                             [program, "--game", game, "--cd", launch.DOS_DIR])
            saved = launch.SETTINGS
            try:
                launch.SETTINGS = os.path.join(d, "settings.json")
                launch.save_settings(dict(settings))
                self.assertTrue(launch.is_game_dir(game))       # DSUN.EXE is enough with the program
                self.assertFalse(launch.is_game_dir(d))
            finally:
                launch.SETTINGS = saved

    def test_recognises_the_game_folder(self):
        with tempfile.TemporaryDirectory() as d:
            game = make_game(d, cloud_saves=False)
            self.assertTrue(launch.is_game_dir(game))
            self.assertFalse(launch.is_game_dir(d))
            self.assertEqual(launch.find_game_dir(game), game)

    def test_settings_not_the_loaders_kept_aside(self):
        """A settings.json that is JSON but not an object (a list, a number) is read as none and
        kept aside as settings.json.bad, as an unreadable one is, so the next save loses nothing."""
        saved = launch.SETTINGS
        with tempfile.TemporaryDirectory() as d:
            try:
                launch.SETTINGS = os.path.join(d, "settings.json")
                with open(launch.SETTINGS, "w") as f:
                    f.write("[1, 2]")
                self.assertEqual(launch.load_settings(), {})
                self.assertTrue(os.path.exists(launch.SETTINGS + ".bad"))
                self.assertFalse(os.path.exists(launch.SETTINGS))
            finally:
                launch.SETTINGS = saved

    def test_drives_searched_once_and_only_when_needed(self):
        """The saved folder is tried before any drive; the drives' search (each drive only as far
        as needed: candidate_dirs is a generator) is made once a run, its answer kept."""
        searched = []
        def candidates():
            searched.append(1)
            yield from ()
        saved = launch.SETTINGS, launch.candidate_dirs
        launch._SEARCHED.clear()
        with tempfile.TemporaryDirectory() as d:
            try:
                launch.SETTINGS, launch.candidate_dirs = os.path.join(d, "settings.json"), candidates
                game = make_game(d, cloud_saves=False)
                launch.save_settings({"game_dir": game})
                self.assertEqual(launch.find_game_dir(), game)
                self.assertEqual(searched, [])
                launch.save_settings({})
                self.assertIsNone(launch.find_game_dir())
                self.assertIsNone(launch.find_game_dir())
                self.assertEqual(searched, [1])
            finally:
                launch.SETTINGS, launch.candidate_dirs = saved
                launch._SEARCHED.clear()

    def test_conf_loads_the_helper_before_the_game(self):
        with tempfile.TemporaryDirectory() as d:
            game = make_game(d, cloud_saves=True)
            conf = launch.write_conf(game, os.path.join(d, "test.conf"))
            with open(conf, newline="") as f:
                text = f.read()
        lines = text.split("\r\n")
        self.assertIn("[autoexec]", lines)
        self.assertIn(r'mount C "..\cloud_saves" -t overlay', lines)
        self.assertIn(f'mount d "{launch.DOS_DIR}"', lines)
        self.assertLess(lines.index(r"lh d:\dsclog.exe"), lines.index(r"d:\dsunlog.exe"))
        # upper memory moved down to C900h just before the helper loads into it
        self.assertEqual(lines.index(r"d:\umbplus.com"), lines.index(r"lh d:\dsclog.exe") - 1)
        self.assertTrue(os.path.isfile(os.path.join(launch.DOS_DIR, launch.UMB_PLUS_COM)))
        self.assertLess(lines.index("c:"), lines.index(r"d:\dsunlog.exe"))  # run from the game folder
        self.assertEqual(lines[-2:], ["exit", ""])
        # a game stopping with an error leaves its message up, saved for the crash report
        self.assertEqual(lines.index(r"d:\gameend.com"), lines.index(r"d:\dsunlog.exe") + 1)
        self.assertTrue(os.path.isfile(os.path.join(launch.DOS_DIR, launch.GAME_END_COM)))
        # EMS off, so the helper has the upper memory block EMS's page frame would take
        self.assertLess(lines.index("ems=false"), lines.index("[autoexec]"))
        self.assertEqual(lines[lines.index("ems=false") - 1], "[dos]")

    def test_conf_without_the_helper_leaves_ems_alone(self):
        with tempfile.TemporaryDirectory() as d:
            game = make_game(d, cloud_saves=False)
            conf = launch.write_conf(game, os.path.join(d, "test.conf"), dice_log=False)
            with open(conf, newline="") as f:
                self.assertNotIn("ems=", f.read())

    def test_dosbox_closing_said_in_the_log(self):
        self.assertEqual(launch.closed_line(0), "DOSBox closed.")
        self.assertIn("crashed (an access violation, code C0000005h)", launch.closed_line(3221225477))
        self.assertIn("C0000005h", launch.closed_line(-1073741819))  # (the same, as a signed int)
        self.assertEqual(launch.closed_line(3), "DOSBox closed with exit code 3.")

    def test_content_switches(self):
        """Each piece of new content is on unless the settings switch it off."""
        on = launch.content({})
        self.assertEqual(set(on), set(launch.CONTENT))
        self.assertTrue(all(on.values()))
        off = launch.content({"vulture": False, "kalzith": False, "semyon": None})
        self.assertFalse(off["vulture"])
        self.assertFalse(off["kalzith"])
        self.assertTrue(off["semyon"])  # (only False switches off)
        # (the new items: one box for all their parts, the parts' own old settings not read)
        items = launch.content({"new_items": False, "world_gear": True})
        self.assertFalse(any(items[k] for k in launch.ITEM_PARTS))
        self.assertTrue(items["vulture"])
        self.assertTrue(all(launch.content({"world_magic": False, "pens_gear": False})[k] for k in launch.ITEM_PARTS))

    def test_combat_log_on_unless_switched_off(self):
        """The combat log in the game is on by default, in the switches and in the dice log."""
        self.assertIs(launch.SWITCH_DEFAULTS["combat_log"], True)
        self.assertTrue(launch.effective_switches({})["combat_log"])
        self.assertFalse(launch.effective_switches({"combat_log": False})["combat_log"])

    def test_older_settings_get_the_combat_log_once(self):
        """Settings saved before version 2 have the combat log turned on, once; then it is the player's."""
        old = {"combat_log": False, "dust": False}
        self.assertTrue(launch.upgrade_settings(old))
        self.assertEqual(old, {"combat_log": True, "dust": False, "settings_version": launch.SETTINGS_VERSION})
        old["combat_log"] = False  # (switched off again, and saved as version 2)
        self.assertFalse(launch.upgrade_settings(old))
        self.assertFalse(old["combat_log"])
        self.assertFalse(launch.upgrade_settings({}))  # (no settings yet: the defaults)
        import json
        with tempfile.TemporaryDirectory() as d:
            saved_path = launch.SETTINGS
            launch.SETTINGS = os.path.join(d, "settings.json")
            try:
                with open(launch.SETTINGS, "w") as f:
                    json.dump({"combat_log": False}, f)
                self.assertTrue(launch.load_settings()["combat_log"])
                launch.save_settings(dict(launch.load_settings(), combat_log=False))
                self.assertFalse(launch.load_settings()["combat_log"])
            finally:
                launch.SETTINGS = saved_path

    def test_settings_saved_whole_and_never_over_an_unreadable_file(self):
        """A save goes through settings.json.tmp, so no half-written file is left; an unreadable
        settings.json is kept aside as settings.json.bad, so a save after it can't lose what it
        held; update_settings changes only what it's given."""
        import json
        with tempfile.TemporaryDirectory() as d:
            saved_path = launch.SETTINGS
            launch.SETTINGS = os.path.join(d, "settings.json")
            try:
                launch.save_settings({"game_dir": "C:\\GOG", "dust": False})
                self.assertFalse(os.path.exists(launch.SETTINGS + ".tmp"))
                launch.update_settings({"combat_log_level": "short"})
                self.assertEqual(launch.load_settings()["game_dir"], "C:\\GOG")
                self.assertEqual(launch.load_settings()["combat_log_level"], "short")
                with open(launch.SETTINGS, "w") as f:
                    f.write('{"game_dir": "C:\\\\GOG", "du')  # (cut off)
                self.assertEqual(launch.load_settings(), {})
                with open(launch.SETTINGS + ".bad") as f:
                    self.assertIn("game_dir", f.read())
                launch.update_settings({"dust": True})
                with open(launch.SETTINGS) as f:
                    self.assertEqual(json.load(f)["dust"], True)
            finally:
                launch.SETTINGS = saved_path

    def test_settings_with_a_bom(self):
        """A settings.json saved by Notepad with a byte-order mark is read, not put aside as bad."""
        with tempfile.TemporaryDirectory() as d:
            saved_path = launch.SETTINGS
            launch.SETTINGS = os.path.join(d, "settings.json")
            try:
                with open(launch.SETTINGS, "w", encoding="utf-8-sig") as f:
                    f.write('{"game_dir": "C:\\\\GOG"}')
                self.assertEqual(launch.load_settings()["game_dir"], "C:\\GOG")
                self.assertFalse(os.path.exists(launch.SETTINGS + ".bad"))
            finally:
                launch.SETTINGS = saved_path

    def test_recompiled_exit_is_not_cut_off(self):
        """No marker files: under DOSBox the game was cut off (GAMEEND.COM writes GAMEOK.TXT as it
        ends), under the recompiled program, which has no GAMEEND.COM, it ended as usual."""
        with tempfile.TemporaryDirectory() as d:
            saved = launch.GAME_END, launch.GAME_MESSAGE, launch.GAME_OK, launch.STARTED
            launch.GAME_END, launch.GAME_MESSAGE, launch.GAME_OK = (os.path.join(d, n) for n in ("E", "M", "OK"))
            try:
                launch.STARTED = None
                self.assertEqual(launch.game_end_note(), launch.CUT_OFF)
                launch.STARTED = "game.exe"
                self.assertIsNone(launch.game_end_note())
            finally:
                launch.GAME_END, launch.GAME_MESSAGE, launch.GAME_OK, launch.STARTED = saved

    def test_a_locked_settings_file_is_never_saved_over(self):
        """settings.json there but not readable for now (Windows: held by an antivirus or a
        backup): a plain read gives no settings, but a read to change and save raises after a few
        tries, so the file is never replaced by the change alone; a missing file is no settings."""
        import builtins
        import json
        from unittest import mock
        with tempfile.TemporaryDirectory() as d:
            saved_path = launch.SETTINGS
            launch.SETTINGS = os.path.join(d, "settings.json")
            try:
                launch.update_settings({"combat_log_level": "short"})  # (no file yet: made)
                launch.save_settings({"game_dir": "C:\\GOG", "dust": False})
                real_open = builtins.open

                def locked(path, *args, **kwargs):
                    if path == launch.SETTINGS and (not args or "r" in args[0]):
                        raise PermissionError(13, "in use", path)
                    return real_open(path, *args, **kwargs)
                with mock.patch("builtins.open", locked), mock.patch("time.sleep"):
                    self.assertEqual(launch.load_settings(), {})
                    with self.assertRaises(OSError):
                        launch.update_settings({"pickpocketed": ["x@1"]})
                    with self.assertRaises(OSError):
                        launch.add_learned_speakers({5: "Tarkon"})
                with open(launch.SETTINGS) as f:
                    self.assertEqual(json.load(f)["game_dir"], "C:\\GOG")
            finally:
                launch.SETTINGS = saved_path

    def test_game_message(self):
        """DSCLOG's GAMEMSG.BIN: the text the game wrote as it quit, and far returns on its stack
        as places in DSUN.EXE."""
        import struct
        load = 0x1000
        stack = bytearray(launch.MSG_STACK)
        struct.pack_into("<HH", stack, 4, 0x01A9, load + 0x2FA6)  # (a way back into the game)
        text = b"\r\nABEND: VMDelHeap() returned error 3\r\n"
        data = b"GMSG" + struct.pack("<BHHH", 1, load, 0x5000, 0xFF00) + bytes(stack) \
            + struct.pack("<H", len(text)) + text
        out = launch.game_message(data)
        self.assertIn("quit with code 1", out)
        self.assertIn("ABEND: VMDelHeap() returned error 3", out)
        self.assertIn(f"DSUN {0x2FA60 + 0x1A9 + 0x5400:X}h (+04: 2FA6:01A9)", out)
        self.assertIsNone(launch.game_message(b"nope"))

    def test_crash_report(self):
        """What DOSBox and the game left, the switches, and the end of the logs, in a file of its
        own in crash-logs."""
        dice = "\n".join(f"line {n}" for n in range(500))
        text = launch.crash_report(0, "Return code 00h, video mode 03h\nNull pointer assignment",
                                   {"vulture": False, "cycles": 20000, "game_dir": "C:\\Games", "tools_given": ["Xan|Xan"]}, dice,
                                   "Dinos\nA vulture! Give it here.", ["2 bytes at 0x10 (low memory), from x"],
                                   {"stdout.txt": "DOSBox version 0.74-3"}, 1000.0, 1000.0 + 600)
        self.assertIn("DOSBox closed.", text)
        self.assertIn("The game ran for 10 minutes.", text)
        self.assertIn("The game stopped with an error. On the screen:\nReturn code 00h, video mode 03h\n"
                      "Null pointer assignment", text)
        self.assertIn("  vulture: False", text)
        self.assertIn("  cycles: 20000", text)
        self.assertIn("  shadows: True", text)  # (not in the settings: its default)
        self.assertIn("  stealth: True", text)
        self.assertNotIn("Games", text)  # (where the game is installed is left out)
        self.assertNotIn("Xan", text)  # (and the lists kept for the game, not switches)
        self.assertIn("2 bytes at 0x10 (low memory)", text)
        self.assertIn("DOSBox's stdout.txt:\nDOSBox version 0.74-3", text)
        self.assertIn("line 499", text)
        self.assertNotIn("line 199\n", text)  # (the last 300)
        self.assertNotIn("The game's memory", text)  # (no sample taken)
        self.assertIn("A vulture! Give it here.", text)
        with tempfile.TemporaryDirectory() as d:
            path = launch.write_crash_report(text, 1000.0, os.path.join(d, "crash-logs"))
            self.assertTrue(os.path.basename(path).startswith("crash-") and path.endswith(".txt"))
            with open(path, encoding="utf-8") as f:
                self.assertEqual(f.read(), text)
            again = launch.write_crash_report(text, 1000.0, os.path.join(d, "crash-logs"))
            self.assertNotEqual(again, path)
            self.assertTrue(again.endswith("-2.txt"))

    def test_crash_report_memory(self):
        from dsloader import heapcheck
        saved = heapcheck.WATCH
        try:
            heapcheck.WATCH = heapcheck.Watch()
            heapcheck.WATCH.last = heapcheck.WATCH.lowest = heapcheck.Memory(250000, 0, 0, 0, 54000, 53000)
            text = launch.crash_report(1, None, {}, "", "", [], {}, 0, 1000.0)
            self.assertIn("The game's memory (the map's view needs a block of 60,000 bytes each time it opens):\n"
                          "  last read: heap 244 KB with 0 KB free in it (0 pieces, the largest 0 bytes); DOS memory "
                          "free after the game 52 KB (the largest piece 53000 bytes)", text)
        finally:
            heapcheck.WATCH = saved

    def test_game_cut_off(self):
        """GAMEEND.COM notes the game ending as usual in GAMEOK.TXT: without it, and with no error
        noted, DOSBox closed while the game ran, and that is the note (a crash report is saved)."""
        from unittest import mock
        with tempfile.TemporaryDirectory() as d:
            paths = {name: os.path.join(d, name) for name in ("GAMEEND.TXT", "GAMEMSG.BIN", "GAMEOK.TXT")}
            with mock.patch.object(launch, "GAME_END", paths["GAMEEND.TXT"]), \
                    mock.patch.object(launch, "GAME_MESSAGE", paths["GAMEMSG.BIN"]), \
                    mock.patch.object(launch, "GAME_OK", paths["GAMEOK.TXT"]):
                self.assertEqual(launch.game_end_note(), launch.CUT_OFF)
                open(paths["GAMEOK.TXT"], "w").close()
                self.assertIsNone(launch.game_end_note())
        text = launch.crash_report(0, launch.CUT_OFF, {}, "", "", [], {}, 0, 0)
        self.assertIn(launch.CUT_OFF, text)
        self.assertNotIn("On the screen", text)

    def test_dosbox_output(self):
        """DOSBox's stdout.txt and stderr.txt from this run only."""
        with tempfile.TemporaryDirectory() as d:
            game = make_game(d, cloud_saves=False)
            with open(os.path.join(game, "DOSBOX", "stdout.txt"), "w") as f:
                f.write("Exit to error: CPU:GRP5:Illegal Call 7\n")
            self.assertEqual(launch.dosbox_output(game, 0), {"stdout.txt": "Exit to error: CPU:GRP5:Illegal Call 7"})
            self.assertEqual(launch.dosbox_output(game, os.path.getmtime(os.path.join(game, "DOSBOX", "stdout.txt")) + 1), {})

    def test_game_speed(self):
        """20000 cycles on the dynamic core unless asked otherwise (smooth walking with the party in
        view, shadows and dust); 35000 the fastest (30000, the fastest of before, taken as it); GOG's
        own when asked; nothing else taken."""
        self.assertEqual(launch.cpu_lines({}), ["[cpu]", "core=dynamic", "cycles=fixed 20000", ""])
        self.assertEqual(launch.cpu_lines({"cycles": 35000}), ["[cpu]", "core=dynamic", "cycles=fixed 35000", ""])
        self.assertEqual(launch.cpu_lines({"cycles": 30000}), ["[cpu]", "core=dynamic", "cycles=fixed 35000", ""])
        self.assertEqual(launch.cpu_lines({"cycles": "gog"}), [])
        self.assertEqual(launch.cpu_lines({"cycles": 99999}), ["[cpu]", "core=dynamic", "cycles=fixed 20000", ""])

    def test_a_window_three_times_the_game_unless_asked_otherwise(self):
        self.assertEqual(launch.display_lines({}),
                         ["[sdl]", "fullscreen=false", "autolock=true", "sensitivity=33", "[render]", "aspect=true", "scaler=normal3x", ""])
        self.assertIn("scaler=normal3x", launch.display_lines({"window_scale": 3}))
        self.assertIn("scaler=none", launch.display_lines({"window_scale": 1}))
        self.assertIn("scaler=normal3x", launch.display_lines({"window_scale": 7}))
        self.assertIn("scaler=normal2x", launch.display_lines({"window_scale": 2}))
        four = launch.display_lines({"window_scale": 4})
        self.assertIn("windowresolution=1280x960", four)
        self.assertIn("output=opengl", four)
        self.assertEqual(launch.display_lines({"fullscreen": True}), [])  # GOG's own full screen
        # the pointer at the desktop's speed: the mouse's sensitivity 100 over the scale
        self.assertIn("sensitivity=50", launch.display_lines({"window_scale": 2}))
        self.assertIn("sensitivity=25", four)
        self.assertIn("sensitivity=100", launch.display_lines({"window_scale": 1}))
        self.assertNotIn("sensitivity=33", launch.display_lines({"mouse_start": False}))
        saved = launch.load_settings
        launch.load_settings = lambda: {}
        try:
            with tempfile.TemporaryDirectory() as d:
                game = make_game(d, cloud_saves=False)
                with open(launch.write_conf(game, os.path.join(d, "test.conf")), newline="") as f:
                    lines = f.read().split("\r\n")
        finally:
            launch.load_settings = saved
        self.assertLess(lines.index("fullscreen=false"), lines.index("[autoexec]"))

    def test_without_the_dice_log_it_runs_the_game_as_usual(self):
        with tempfile.TemporaryDirectory() as d:
            game = make_game(d, cloud_saves=False)
            with open(launch.write_conf(game, os.path.join(d, "test.conf"), dice_log=False)) as f:
                text = f.read()
        self.assertIn("darksun\n", text)
        self.assertNotIn("dsclog", text)

    def test_unknown_game_version_is_reported(self):
        with tempfile.TemporaryDirectory() as d:
            game = make_game(d, cloud_saves=False)
            self.assertIn("GOG release", launch.prepare_patched_game(game))

    def test_no_overlay_mount_without_cloud_saves(self):
        with tempfile.TemporaryDirectory() as d:
            game = make_game(d, cloud_saves=False)
            with open(launch.write_conf(game, os.path.join(d, "test.conf"))) as f:
                self.assertNotIn("cloud_saves", f.read())


if __name__ == "__main__":
    unittest.main()
