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
            # (a program merely named dsun.exe in the folder holding the mod's, Downloads say, is
            # never started: only one in the mod's folder or a darksun-recompiled folder)
            self.assertIsNone(launch.found_recompiled_program(mod))
            os.makedirs(os.path.join(d, "darksun-recompiled"))
            named = os.path.join(d, "darksun-recompiled", launch.RECOMPILED_EXE)
            native(named)
            self.assertEqual(launch.found_recompiled_program(mod), named)
            dos = os.path.join(d, "DSUN.EXE")
            with open(dos, "wb") as f:
                f.write(b"MZ" + bytes(0x60))
            self.assertNotEqual(launch.recompiled_program({"recompiled": dos}), dos)

    def test_started_and_closed_lines(self):
        """The log says which runs, and names it when it closes, by what was started."""
        saved = launch.STARTED
        try:
            launch.STARTED = None
            self.assertEqual(launch.started_line("G"), "Starting Shattered Lands from G in DOSBox.")
            with tempfile.TemporaryDirectory() as d:  # (the sequel's folder: its DSUN.EXE's size)
                from dsloader import ravager
                with open(os.path.join(d, "DSUN.EXE"), "wb") as f:
                    f.truncate(ravager.WOTR_SIZE)
                self.assertEqual(launch.started_line(d), f"Starting Wake of the Ravager from {d} in DOSBox.")
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

    def test_names_hand_edited_keys(self):
        """A hand-edited portrait key that is a digit to str.isdigit but no number to int ("²") is
        passed over, not a ValueError that broke every name look-up."""
        self.assertEqual(launch._names({"k": {"5": "Tarkon", "\u00b2": "x", "a": "y", "7": ""}}, "k"), {5: "Tarkon"})

    def dsun_only(self) -> str:
        """A folder with an empty DSUN.EXE alone (gamepatch.write_patched mocked: no more needed)."""
        d = tempfile.mkdtemp()
        self.addCleanup(lambda: __import__("shutil").rmtree(d, ignore_errors=True))
        open(os.path.join(d, "DSUN.EXE"), "w").close()
        return d

    def test_dsun_exe_gone(self):
        """DSUN.EXE gone from the folder since it was picked: a clear refusal in DOSBox's way and
        the recompiled program's, and prepare_patched_game says why (it gave a TypeError)."""
        with tempfile.TemporaryDirectory() as d:
            game = make_game(d, cloud_saves=False)
            os.remove(launch._find_file(game, "DSUN.EXE"))
            with self.assertRaises(launch.LaunchError) as raised:
                launch._launch(game, {"recompiled": False})
            self.assertIn("has no DSUN.EXE", str(raised.exception))
            self.assertIn("has no DSUN.EXE", launch.prepare_patched_game(game, {}))

    def test_shattered_lands_layout_back_before_its_copies(self):
        """A sequel's game played from this Loader leaves the sequel's layout on (ravlog.apply_layout)
        until a dice log is made for Shattered Lands, after its copies: prepare_patched_game puts
        Shattered Lands' back first (2026-11-27's code audit: the copies made with the sequel's item
        offsets left out the new items, people and icons)."""
        from dsloader import game, ravlog
        sl = game.ITEM_PLUS, game.SHEET_SIZE
        ravlog.apply_layout()
        self.addCleanup(ravlog.restore_layout)
        self.assertNotEqual((game.ITEM_PLUS, game.SHEET_SIZE), sl)
        with tempfile.TemporaryDirectory() as d:
            launch.prepare_patched_game(d, {})
        self.assertEqual((game.ITEM_PLUS, game.SHEET_SIZE), sl)

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
            conf = launch.write_conf(game, os.path.join(d, "test.conf"), settings={})  # (not this folder's own settings: its engine)
            with open(conf, newline="") as f:
                text = f.read()
        lines = text.split("\r\n")
        self.assertIn("[autoexec]", lines)
        self.assertIn(r'mount C "..\cloud_saves" -t overlay', lines)
        self.assertIn(f'mount d "{launch.DOS_DIR}"', lines)
        self.assertLess(lines.index(r"lh d:\dsclog.exe"), lines.index(r"d:\dsunlog.exe"))
        # upper memory moved down to CA00h just before DSCLOG loads into it
        self.assertEqual(lines.index(r"d:\umbplus.com"), lines.index(r"lh d:\dsclog.exe") - 1)
        self.assertTrue(os.path.isfile(os.path.join(launch.DOS_DIR, launch.UMB_PLUS_COM)))
        self.assertLess(lines.index("c:"), lines.index(r"d:\dsunlog.exe"))  # run from the game folder
        self.assertEqual(lines[-2:], ["exit", ""])
        # a game stopping with an error leaves its message up, saved for the crash report
        self.assertEqual(lines.index(r"d:\gameend.com"), lines.index(r"d:\dsunlog.exe") + 1)
        self.assertTrue(os.path.isfile(os.path.join(launch.DOS_DIR, launch.GAME_END_COM)))
        # EMS off, so DSCLOG has the upper memory block EMS's page frame would take
        self.assertLess(lines.index("ems=false"), lines.index("[autoexec]"))
        self.assertEqual(lines[lines.index("ems=false") - 1], "[dos]")

    def test_every_patch_switch_skipped_when_off(self):
        """Each of gamepatch's switches (a tuple of patch names) is left out of the patched game when
        its Options key is off (prepare_patched_game's skip), and none is with every key on."""
        from dsloader import gamepatch
        names = {p.name for p in gamepatch.PATCHES}
        switches = {key: value for key, value in vars(gamepatch).items()
                    if key.isupper() and isinstance(value, tuple) and value and set(value) <= names}
        self.assertIn("SPELLS_MANUAL", switches)
        skips = []
        saved = gamepatch.write_patched

        def write_patched(source, target, skip=frozenset()):
            skips.append(frozenset(skip))
            raise gamepatch.PatchError("not in a test")
        gamepatch.write_patched = write_patched
        try:
            def skip(settings):
                self.assertEqual(launch.prepare_patched_game(self.dsun_only(), settings), "not in a test")
                return skips[-1]
            self.assertEqual(skip({}), frozenset())
            off = {key: skip({key: False}) for key in launch.CONTENT}
        finally:
            gamepatch.write_patched = saved
        # (the switches gone from the tab, game.ALWAYS_ON: their patches always in, whatever is saved)
        always = {"EFFECTS_KEPT", "ROLL_STORE", "CAMERA", "SCENE_POINTER", "MOUSE_START", "PARTY_SPREAD",
                  "SPELLS_MANUAL", "SPELL_TO_HIT"}
        for name, patches in switches.items():
            keys = [key for key, skipped in off.items() if set(patches) <= skipped]
            if name in always:
                self.assertEqual(keys, [], f"gamepatch.{name}: always on now")
                continue
            self.assertTrue(keys, f"gamepatch.{name}: no Options key leaves it out")
        for key, skipped in off.items():  # (nothing else left out: only whole switches)
            self.assertTrue(all(set(patches) <= skipped or not set(patches) & skipped
                                for patches in switches.values()), key)
            self.assertEqual(skipped, frozenset().union(*(p for p in switches.values() if set(p) <= skipped)), key)
        self.assertNotIn("save_signed", frozenset().union(*off.values()))  # (always applied)

    def test_conf_in_the_code_page(self):
        """The conf in the encoding DOSBox reads it in (Windows' ANSI code page there, else UTF-8); a
        folder whose name the code page can't hold is a LaunchError that says so."""
        self.assertEqual(launch.conf_encoding(), "mbcs" if os.name == "nt" else "utf-8")
        saved = launch.conf_encoding, launch.DOS_DIR
        try:
            with tempfile.TemporaryDirectory() as d:
                game = make_game(d, cloud_saves=False)
                launch.conf_encoding = lambda: "cp1252"
                launch.DOS_DIR = os.path.join(d, "Café", "dos")
                with open(launch.write_conf(game, os.path.join(d, "test.conf")), "rb") as f:
                    self.assertIn(b'mount d "' + launch.DOS_DIR.encode("cp1252") + b'"\r\n', f.read())
                launch.DOS_DIR = os.path.join(d, "ゲーム", "dos")
                with self.assertRaises(launch.LaunchError) as raised:
                    launch.write_conf(game, os.path.join(d, "test2.conf"))
                self.assertIn("'ゲーム'", str(raised.exception))
                self.assertIn('(mount d "', str(raised.exception))
                self.assertIn("cp1252", str(raised.exception))
                self.assertFalse(os.path.exists(os.path.join(d, "test2.conf")))
                launch.conf_encoding = saved[0]
                if os.name != "nt":
                    with open(launch.write_conf(game, os.path.join(d, "test3.conf")), "rb") as f:
                        self.assertIn(launch.DOS_DIR.encode("utf-8"), f.read())
        finally:
            launch.conf_encoding, launch.DOS_DIR = saved

    def test_conf_without_the_helper_leaves_ems_alone(self):
        with tempfile.TemporaryDirectory() as d:
            game = make_game(d, cloud_saves=False)
            conf = launch.write_conf(game, os.path.join(d, "test.conf"), dice_log=False, settings={})
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

    def test_combat_log_always_on(self):
        """The combat log in the game has no switch now (game.ALWAYS_ON): an older settings file's
        False is dropped as it is read, and the dice log has it on whatever the settings say."""
        self.assertNotIn("combat_log", launch.SWITCH_DEFAULTS)
        self.assertNotIn("combat_log", launch.effective_switches({"combat_log": False}))
        self.assertIn("combat_log_level", launch.SWITCH_DEFAULTS)  # (its level kept)

    def test_older_settings_upgraded_once(self):
        """Settings saved before version 2 are brought up to it once (the combat log then turned on:
        it has no switch now, and the key is dropped as the file is read)."""
        old = {"combat_log": False, "steady_pace": False}
        self.assertTrue(launch.upgrade_settings(old))
        self.assertEqual(old["settings_version"], launch.SETTINGS_VERSION)
        self.assertFalse(launch.upgrade_settings(old))
        self.assertFalse(launch.upgrade_settings({}))  # (no settings yet: the defaults)
        import json
        with tempfile.TemporaryDirectory() as d:
            saved_path = launch.SETTINGS
            launch.SETTINGS = os.path.join(d, "settings.json")
            try:
                with open(launch.SETTINGS, "w") as f:
                    json.dump({"combat_log": False, "steady_pace": False}, f)
                self.assertEqual(launch.load_settings()["steady_pace"], False)
                self.assertNotIn("combat_log", launch.load_settings())
            finally:
                launch.SETTINGS = saved_path

    def test_old_false_for_an_always_on_switch_is_passed_over(self):
        """A settings.json from before the switches went, with some of them unticked (shadows, dust,
        weapon specialization, thieves as in AD&D, spells rolling to hit, the merged-away halves),
        still has every rule on: the keys are dropped as it is read, the dice log's switches are on,
        the patched game leaves nothing of theirs out, and DSCLOG's rule bits (RULES, RULES_HI) all
        set; a switch the tab keeps is still the player's."""
        import json
        from dsloader import dicelog, game, gamepatch
        old = {key: False for key in game.ALWAYS_ON | frozenset(game.ALWAYS_ON_OLD_NAMES)}
        old.update({"helm_ac": False, "steady_pace": False})
        with tempfile.TemporaryDirectory() as d:
            saved_path = launch.SETTINGS
            launch.SETTINGS = os.path.join(d, "settings.json")
            try:
                with open(launch.SETTINGS, "w") as f:
                    json.dump(old, f)
                settings = launch.load_settings(strict=True)
                launch.save_settings(settings)
                with open(launch.SETTINGS) as f:
                    written = json.load(f)
            finally:
                launch.SETTINGS = saved_path
        for key in game.ALWAYS_ON:
            self.assertNotIn(key, settings, key)
            self.assertNotIn(key, written, key)
            self.assertTrue(game.setting_on(old, key), key)  # (even unread: the raw file's False)
        self.assertIs(settings["helm_ac"], False)
        rules = game.rules_from_settings(old)
        for key, bit in game.RULE_SETTINGS_GONE:
            self.assertTrue(rules & bit, key)
        self.assertTrue(rules & game.RULE_TWO_WEAPONS)
        self.assertFalse(rules & game.RULE_HELMS)  # (its switch kept, unticked)
        self.assertEqual(rules, game.rules_from_settings(settings))
        self.assertEqual(game.rules_from_settings(old) | game.RULE_HELMS,
                         game.rules_from_settings({}))
        on = launch.content(old)
        self.assertFalse(set(launch.CONTENT) & game.ALWAYS_ON)  # (no always-on key read)
        self.assertFalse(on["steady_pace"])
        log = dicelog.DiceLog(None)
        log.use_settings(old)
        for name in ("pickpockets", "show_gear", "show_shadows", "combat_log", "scroll_map", "show_dust",
                     "see_through", "elf_looks", "cilla_elf", "stealth_gear", "use_targeting"):
            self.assertFalse(hasattr(log, name), name)  # (no switch of the dice log's left for them)
        self.assertEqual(log.rules, rules)
        # (DSCLOG's two words, as set_rules writes them: every gone switch's bit in one or the other)
        low, high = rules & 0xFFFF, rules >> 16 & 0xFFFF
        self.assertEqual(low | high << 16, rules)
        self.assertEqual(game.RULES_ALWAYS & ~(low | high << 16), 0)
        skips = []
        saved = gamepatch.write_patched

        def write_patched(source, target, skip=frozenset()):
            skips.append(frozenset(skip))
            raise gamepatch.PatchError("not in a test")
        gamepatch.write_patched = write_patched
        try:
            self.assertEqual(launch.prepare_patched_game(self.dsun_only(), old), "not in a test")
        finally:
            gamepatch.write_patched = saved
        self.assertEqual(skips[-1], frozenset(gamepatch.STEADY_PACE))  # (only the kept switch's)
        self.assertIn("sensitivity=33", launch.display_lines(old))  # (the pointer's speed: mouse_start)

    def test_settings_saved_whole_and_never_over_an_unreadable_file(self):
        """A save goes through settings.json.tmp, so no half-written file is left; an unreadable
        settings.json is kept aside as settings.json.bad, so a save after it can't lose what it
        held; update_settings changes only what it's given."""
        import json
        with tempfile.TemporaryDirectory() as d:
            saved_path = launch.SETTINGS
            launch.SETTINGS = os.path.join(d, "settings.json")
            try:
                launch.save_settings({"game_dir": "C:\\GOG", "steady_pace": False})
                self.assertFalse(os.path.exists(launch.SETTINGS + ".tmp"))
                launch.update_settings({"combat_log_level": "short"})
                self.assertEqual(launch.load_settings()["game_dir"], "C:\\GOG")
                self.assertEqual(launch.load_settings()["combat_log_level"], "short")
                with open(launch.SETTINGS, "w") as f:
                    f.write('{"game_dir": "C:\\\\GOG", "du')  # (cut off)
                self.assertEqual(launch.load_settings(), {})
                with open(launch.SETTINGS + ".bad") as f:
                    self.assertIn("game_dir", f.read())
                launch.update_settings({"steady_pace": True})
                with open(launch.SETTINGS) as f:
                    self.assertEqual(json.load(f)["steady_pace"], True)
            finally:
                launch.SETTINGS = saved_path

    @unittest.skipIf(os.name == "nt", "the other process's lock taken with fcntl")
    def test_settings_changed_by_another_process_kept(self):
        """Another process (the window, `play`) changing settings.json under its lock as this one
        updates it: this one waits for the lock, so both changes are kept (each read and wrote the
        whole file: the later one's lost the other's)."""
        import json
        import subprocess
        import sys
        import time as _time
        with tempfile.TemporaryDirectory() as d:
            saved_path = launch.SETTINGS
            launch.SETTINGS = os.path.join(d, "settings.json")
            try:
                launch.save_settings({"game_dir": "C:\\GOG"})
                lock, ready = os.path.join(d, "settings.lock"), os.path.join(d, "ready")
                other = subprocess.Popen([sys.executable, "-c", (
                    "import fcntl, json, os, sys, time\n"
                    "fd = os.open(sys.argv[1], os.O_RDWR | os.O_CREAT)\n"
                    "fcntl.flock(fd, fcntl.LOCK_EX)\n"
                    "s = json.load(open(sys.argv[2]))\n"
                    "open(sys.argv[3], 'w').close()\n"
                    "time.sleep(0.4)\n"
                    "s['pickpocketed'] = ['x@1']\n"
                    "json.dump(s, open(sys.argv[2], 'w'))\n"), lock, launch.SETTINGS, ready])
                try:
                    end = _time.monotonic() + 10
                    while not os.path.exists(ready) and _time.monotonic() < end:
                        _time.sleep(0.01)
                    launch.update_settings({"combat_log_level": "short"})
                finally:
                    other.wait(10)
                with open(launch.SETTINGS) as f:
                    got = json.load(f)
                self.assertEqual((got.get("pickpocketed"), got.get("combat_log_level")), (["x@1"], "short"))
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
        self.assertIn("  monster_info: True", text)  # (not in the settings: its default)
        self.assertIn("  helm_ac: True", text)
        self.assertNotIn("  shadows:", text)  # (always on now: no switch to report)
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
        """35000 cycles on the dynamic core unless asked otherwise (the whole party walking at full
        speed, nearly every picture drawn); 20000 when asked (30000, the fastest of before, taken as
        35000); GOG's own when asked; nothing else taken."""
        self.assertEqual(launch.cpu_lines({}), ["[cpu]", "core=dynamic", "cycles=fixed 35000", ""])
        self.assertEqual(launch.cpu_lines({"cycles": 20000}), ["[cpu]", "core=dynamic", "cycles=fixed 20000", ""])
        self.assertEqual(launch.cpu_lines({"cycles": 35000}), ["[cpu]", "core=dynamic", "cycles=fixed 35000", ""])
        self.assertEqual(launch.cpu_lines({"cycles": 30000}), ["[cpu]", "core=dynamic", "cycles=fixed 35000", ""])
        self.assertEqual(launch.cpu_lines({"cycles": "gog"}), [])
        self.assertEqual(launch.cpu_lines({"cycles": 99999}), ["[cpu]", "core=dynamic", "cycles=fixed 35000", ""])

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
        self.assertIn("sensitivity=33", launch.display_lines({"mouse_start": False}))  # (always on now)
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

    def test_the_picture(self):
        """Scanlines and TV are DOSBox 0.74's scan and tv scalers in the plain one's place (2x, 3x;
        2x in the four-times window, 3x in full screen); Sharp its unfiltered OpenGL output with
        the window's size given. The window's size and the mouse's sensitivity are the plain
        picture's at every size; the single-size window (the playtest kit's) is always plain, and
        so is a picture the Loader doesn't know."""
        def lines(scale, picture, **more):
            return launch.display_lines({"window_scale": scale, "picture": picture, **more})
        plain = {scale: lines(scale, "plain") for scale in launch.WINDOW_SCALES}
        for scale in launch.WINDOW_SCALES:  # (no picture named: the plain one, as before there was a choice)
            self.assertEqual(launch.display_lines({"window_scale": scale}), plain[scale])
        self.assertEqual(plain[1], ["[sdl]", "fullscreen=false", "autolock=true", "sensitivity=100",
                                    "[render]", "aspect=true", "scaler=none", ""])
        self.assertEqual(plain[4], ["[sdl]", "fullscreen=false", "autolock=true", "sensitivity=25", "output=opengl",
                                    "windowresolution=1280x960", "[render]", "aspect=true", "scaler=normal2x", ""])
        for picture in launch.PICTURES + ("crt", "", None, 3, ["tv"]):
            self.assertEqual(lines(1, picture), plain[1], picture)
        for picture in ("crt", "", None, 3, ["tv"], "SCANLINES"):
            for scale in (2, 3, 4):
                self.assertEqual(lines(scale, picture), plain[scale], picture)
            self.assertEqual(lines(3, picture, fullscreen=True), [], picture)
        # scanlines and tv: the scaler alone changes
        for picture, scaler in (("scanlines", "scan"), ("tv", "tv")):
            for scale, by in ((2, 2), (3, 3), (4, 2)):
                self.assertEqual(lines(scale, picture),
                                 [f"scaler={scaler}{by}x" if line.startswith("scaler=") else line
                                  for line in plain[scale]], (picture, scale))
            self.assertEqual(lines(3, picture, fullscreen=True), ["[render]", f"scaler={scaler}3x", ""])
        # sharp: openglnb, the window's size given, the plain scaler kept
        self.assertEqual(lines(2, "sharp"), ["[sdl]", "fullscreen=false", "autolock=true", "sensitivity=50",
                                             "output=openglnb", "windowresolution=640x480",
                                             "[render]", "aspect=true", "scaler=normal2x", ""])
        self.assertEqual(lines(3, "sharp"), ["[sdl]", "fullscreen=false", "autolock=true", "sensitivity=33",
                                             "output=openglnb", "windowresolution=960x720",
                                             "[render]", "aspect=true", "scaler=normal3x", ""])
        self.assertEqual(lines(4, "sharp"), [line.replace("output=opengl", "output=openglnb") for line in plain[4]])
        self.assertEqual(lines(3, "sharp", fullscreen=True), ["[sdl]", "output=openglnb", ""])
        self.assertEqual(lines(3, "sharp", mouse_start=False), lines(3, "sharp"))  # (the mouse: always on now)
        # every scaler and output named is one DOSBox 0.74 has (render.cpp, sdlmain.cpp)
        for scale in launch.WINDOW_SCALES:
            for picture in launch.PICTURES:
                for full in (False, True):
                    for line in lines(scale, picture, fullscreen=full):
                        if line.startswith("scaler="):
                            self.assertIn(line[7:], ("none", "normal2x", "normal3x", "scan2x", "scan3x", "tv2x", "tv3x"))
                        if line.startswith("output="):
                            self.assertIn(line[7:], ("opengl", "openglnb"))
        # which pictures a window has, and the one used
        self.assertEqual(launch.pictures({"window_scale": 1}), ("plain",))
        self.assertEqual(launch.pictures({"window_scale": 1, "fullscreen": True}), launch.PICTURES)
        self.assertEqual(launch.pictures({}), launch.PICTURES)
        self.assertEqual(launch.picture({"picture": "tv"}), "tv")
        self.assertEqual(launch.picture({"picture": "tv", "window_scale": 1}), "plain")
        self.assertEqual(launch.picture({}), "plain")
        self.assertEqual(launch.effective_switches({"picture": "tv", "window_scale": 1})["picture"], "plain")
        self.assertEqual(launch.effective_switches({"picture": "sharp"})["picture"], "sharp")

    def test_the_configuration_written_for_the_picture_and_the_music_device(self):
        """write_conf: the picture's lines and the music device's `[midi]` section ahead of the
        autoexec; neither for the defaults."""
        def conf(settings):
            with tempfile.TemporaryDirectory() as d:
                game = make_game(d, cloud_saves=False)
                with open(launch.write_conf(game, os.path.join(d, "test.conf"), settings=settings), newline="") as f:
                    return f.read().split("\r\n")
        usual = conf({})
        self.assertNotIn("[midi]", usual)
        self.assertEqual(conf({"picture": "plain", "midi_device": "default"}), usual)
        self.assertEqual(conf({"picture": "holo", "midi_device": "the loud one"}), usual)
        lines = conf({"picture": "scanlines", "midi_device": 2})
        self.assertIn("scaler=scan3x", lines)
        at = lines.index("[midi]")
        self.assertEqual(lines[at:at + 3], ["[midi]", "midiconfig=2", ""])
        self.assertLess(at, lines.index("[autoexec]"))
        self.assertLess(lines.index("[cpu]"), at)
        self.assertEqual([line for line in lines if line not in usual],
                         ["scaler=scan3x", "[midi]", "midiconfig=2"])
        lines = conf({"fullscreen": True, "picture": "sharp", "midi_device": "128:0"})
        self.assertEqual(lines[:3], ["[sdl]", "output=openglnb", ""])
        self.assertIn("midiconfig=128:0", lines)
        self.assertEqual(launch.effective_switches({"midi_device": 3})["midi_device"], 3)
        self.assertEqual(launch.effective_switches({"midi_device": -1})["midi_device"], "default")

    def test_the_sequels_configuration_has_the_picture_and_speed_but_no_music_device(self):
        """write_conf_wotr: the Options tab's picture and speed reach Wake of the Ravager, the music
        device doesn't (its music is the CD's audio tracks, not MIDI: write_conf_wotr)."""
        def conf(settings):
            with tempfile.TemporaryDirectory() as d:
                game = os.path.join(d, "Ravager")
                os.mkdir(game)
                open(os.path.join(game, "game.ins"), "w").close()
                path = launch.write_conf_wotr(game, os.path.join(d, "test.conf"), settings=settings)
                with open(path, newline="") as f:
                    text = f.read().replace(d, "GAMES")  # (each call's own folder)
                return text.split("\r\n")
        usual = conf({})
        self.assertIn(f"cycles=fixed {launch.DEFAULT_SPEED}", usual)
        lines = conf({"picture": "scanlines", "cycles": 20000, "midi_device": 2})
        self.assertIn("scaler=scan3x", lines)
        self.assertIn("cycles=fixed 20000", lines)
        self.assertNotIn("[midi]", lines)
        self.assertFalse([line for line in lines if line.startswith("midiconfig")])
        self.assertEqual(conf({"midi_device": "128:0"}), usual)

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

    def test_a_copy_left_out_is_told(self):
        """A copy that can't be made (here a broken objects file and no scripts file) is in LEFT_OUT
        and left_out_line, for the player (the audit of 2026-11-10: it was silent); a clean start
        clears them."""
        from unittest import mock
        from dsloader import gamepatch, icons
        with tempfile.TemporaryDirectory() as d:
            game, dos = make_game(d, cloud_saves=False), os.path.join(d, "dos")
            os.makedirs(dos)
            with open(os.path.join(game, icons.OBJECTS_FILE), "wb") as f:
                f.write(b"not a GFF file")
            with mock.patch.object(gamepatch, "write_patched", lambda *a, **k: None), \
                    mock.patch.object(launch, "DOS_DIR", dos):
                self.assertIsNone(launch.prepare_patched_game(game, {}))
                left = " ".join(launch.LEFT_OUT)
                self.assertIn(icons.OBJECTS_FILE, left)
                self.assertIn("GPLDATA.GFF", left)
                self.assertIn("may not load", launch.left_out_line())
                launch.LEFT_OUT[:] = []
                self.assertIsNone(launch.left_out_line())

    def test_no_overlay_mount_without_cloud_saves(self):
        with tempfile.TemporaryDirectory() as d:
            game = make_game(d, cloud_saves=False)
            with open(launch.write_conf(game, os.path.join(d, "test.conf"))) as f:
                self.assertNotIn("cloud_saves", f.read())


if __name__ == "__main__":
    unittest.main()
