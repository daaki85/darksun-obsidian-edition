"""DOSBox-X as the engine (dosboxx.py, and launch.py's branch on it): the engine setting, the
version check, the memory file's name, the whole configuration written for each of the Options
tab's settings, and the start itself with a stand-in for the program."""

import os
import stat
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import dosboxx, launch  # noqa: E402

AUTOEXEC = (launch.UMB_PLUS_COM, launch.PATCHED_EXE, launch.GAME_END_COM)


def lines(settings=None, **more):
    settings = dict(settings or {})
    look = more.pop("look", launch.picture(settings))
    return dosboxx.conf_lines("/game", "/mod/dos", "/dev/shm/x.mem", settings, look=look, autoexec=AUTOEXEC, **more)


def section(conf, name):
    """The lines of one section of a configuration."""
    at = conf.index(f"[{name}]") + 1
    end = next((i for i in range(at, len(conf)) if conf[i].startswith("[")), len(conf))
    return [line for line in conf[at:end] if line]


def no_bundled(test):
    """dosboxx.BUNDLED_DIR an empty folder of the test's own for the test (the Loader's real one
    may hold the DOSBox-X a release brought); returns that folder."""
    d = tempfile.mkdtemp()
    saved = dosboxx.BUNDLED_DIR
    test.addCleanup(lambda: (setattr(dosboxx, "BUNDLED_DIR", saved), dosboxx._USABLE.clear(),
                             __import__("shutil").rmtree(d, ignore_errors=True)))
    dosboxx.BUNDLED_DIR = d
    dosboxx._USABLE.clear()
    return d


def fake_program(folder, version="2026.10.01", name=None):
    """A file that reads as DOSBox-X VERSION (its own file names its configuration file), and on
    Linux and macOS answers -version as the real one does."""
    path = os.path.join(folder, name or dosboxx.BUNDLED_NAMES[0])
    with open(path, "w") as f:
        f.write(f"#!/bin/sh\n# dosbox-x-{version}.conf\necho 'DOSBox-X version {version} SDL2'\n")
    os.chmod(path, os.stat(path).st_mode | stat.S_IXUSR)
    return path


class EngineSettingTests(unittest.TestCase):
    def setUp(self):
        self.bundled = no_bundled(self)

    def test_gogs_with_no_dosbox_x_and_for_anything_unknown(self):
        for settings in ({}, {"engine": "gog"}, {"engine": None}, {"engine": 3}, {"engine": "dosbox"},
                         {"engine": True}, {"engine": ["dosbox-x"]}):
            self.assertEqual(dosboxx.engine(settings), dosboxx.GOG, settings)

    def test_dosbox_x_however_it_is_typed(self):
        for value in ("dosbox-x", "DOSBox-X", " dosbox-x "):
            self.assertEqual(dosboxx.engine({"engine": value}), dosboxx.DOSBOX_X)
            self.assertEqual(dosboxx.chosen({"engine": value}), dosboxx.DOSBOX_X)
        self.assertEqual(dosboxx.chosen({"engine": " GOG"}), dosboxx.GOG)
        for value in (None, "dosbox", 3):
            self.assertIsNone(dosboxx.chosen({"engine": value}))

    def test_dosbox_x_is_the_default_when_the_mod_brings_one(self):
        path = fake_program(self.bundled)
        self.assertEqual(dosboxx.bundled(), path)
        self.assertEqual(dosboxx.program({}), path)
        for settings in ({}, {"engine": None}, {"engine": "nonsense"}, {"dosbox_x_path": "/gone/dosbox-x"}):
            self.assertEqual(dosboxx.engine(settings), dosboxx.DOSBOX_X, settings)
        self.assertEqual(dosboxx.engine({"engine": "gog"}), dosboxx.GOG)  # (chosen on the Options tab)
        self.assertIsNone(dosboxx.problem({}))
        self.assertIsNone(dosboxx.problem({"engine": "dosbox-x"}))

    def test_or_when_the_player_named_one(self):
        d = tempfile.mkdtemp()
        self.addCleanup(lambda: __import__("shutil").rmtree(d, ignore_errors=True))
        mine = fake_program(d, name="dosbox-x")
        bundled = fake_program(self.bundled)
        self.assertEqual(dosboxx.program({"dosbox_x_path": mine}), mine)  # (the player's before the mod's)
        self.assertEqual(dosboxx.engine({"dosbox_x_path": mine}), dosboxx.DOSBOX_X)
        os.remove(bundled)
        self.assertEqual(dosboxx.engine({"dosbox_x_path": mine}), dosboxx.DOSBOX_X)

    def test_one_too_old_is_no_default(self):
        fake_program(self.bundled, "2024.03.01")
        self.assertEqual(dosboxx.engine({}), dosboxx.GOG)
        self.assertEqual(dosboxx.engine({"engine": "dosbox-x"}), dosboxx.DOSBOX_X)  # (chosen: the start says why not)
        self.assertIn("too old", dosboxx.problem({"engine": "dosbox-x"}))

    def test_an_os_free_build_is_no_default_and_is_named(self):
        """DOSBox-X's OS-free builds have no DOS to run the game in (the owner's Windows test, 2026-11-26):
        never the default, and the start and the Options tab say what it is and what to get."""
        path = fake_program(self.bundled)
        with open(path, "a") as f:
            f.write("# LOG: DOSBox-X OS-Free build -- %s\n" % dosboxx.OS_FREE_MARK.decode())
        self.assertTrue(dosboxx.os_free(path))
        self.assertEqual(dosboxx.engine({}), dosboxx.GOG)
        for said in (dosboxx.problem({"engine": "dosbox-x"}), dosboxx.found_line(path)):
            self.assertIn("OS-free", said)
            self.assertIn("vsbuild-win64-VERSION-portable.zip", said)
        self.assertFalse(dosboxx.os_free(fake_program(tempfile.mkdtemp())))  # (the usual build)
        self.assertFalse(dosboxx.os_free("/no/such/dosbox-x"))

    def test_it_is_one_of_the_switches_and_restores_to_none_chosen(self):
        self.assertIsNone(launch.SWITCH_DEFAULTS["engine"])
        self.assertEqual(launch.effective_switches({})["engine"], "gog")
        self.assertEqual(launch.effective_switches({"engine": "dosbox-x"})["engine"], "dosbox-x")
        self.assertEqual(launch.effective_switches({"engine": "nonsense"})["engine"], "gog")
        fake_program(self.bundled)
        self.assertEqual(launch.effective_switches({})["engine"], "dosbox-x")
        self.assertEqual(launch.effective_switches({"engine": "gog"})["engine"], "gog")


class VersionTests(unittest.TestCase):
    def test_what_the_program_prints(self):
        text = b"\nDOSBox-X version 2026.10.01 SDL2, copyright 2011-2026 The DOSBox-X Team.\n"
        self.assertEqual(dosboxx.parse_version(text), (2026, 10, 1))
        self.assertIsNone(dosboxx.parse_version(b"DOSBox version 0.74-3"))
        self.assertIsNone(dosboxx.parse_version(b""))

    def test_new_enough_from_the_first_with_a_memory_file(self):
        self.assertTrue(dosboxx.new_enough((2025, 1, 1)))
        self.assertTrue(dosboxx.new_enough((2026, 10, 1)))
        self.assertFalse(dosboxx.new_enough((2024, 12, 4)))
        self.assertFalse(dosboxx.new_enough((2024, 3, 1)))  # (Ubuntu 24.04's package)
        self.assertFalse(dosboxx.new_enough(None))

    def test_read_from_the_programs_file_without_running_it(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "dosbox-x.exe")
            with open(path, "wb") as f:
                f.write(b"MZ" + b"\0" * 5000 + b"\0dosbox-x-2025.02.01.conf\0" + b"\0" * 100)
            self.assertEqual(dosboxx.version_in_file(path), (2025, 2, 1))
            with open(path, "wb") as f:
                f.write(b"MZ" + b"\0" * 5000)
            self.assertIsNone(dosboxx.version_in_file(path))
            self.assertIsNone(dosboxx.version_in_file(os.path.join(d, "none")))

    def test_a_version_across_two_chunks_is_found(self):
        saved = dosboxx._SCAN_CHUNK
        self.addCleanup(lambda: setattr(dosboxx, "_SCAN_CHUNK", saved))
        dosboxx._SCAN_CHUNK = 64
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "dosbox-x")
            with open(path, "wb") as f:
                f.write(b"\0" * 50 + b"dosbox-x-2026.10.01.conf" + b"\0" * 200)
            self.assertEqual(dosboxx.version_in_file(path), (2026, 10, 1))

    @unittest.skipIf(os.name == "nt", "a shell script stands in for the program")
    def test_asked_of_the_program(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "dosbox-x")
            with open(path, "w") as f:
                f.write("#!/bin/sh\necho 'DOSBox-X version 2024.03.01 SDL2, copyright' >&2\n")
            os.chmod(path, os.stat(path).st_mode | stat.S_IXUSR)
            self.assertEqual(dosboxx.version(path), (2024, 3, 1))

    def test_what_the_options_tab_says(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "dosbox-x")
            open(path, "wb").close()
            self.assertIn("No DOSBox-X chosen", dosboxx.found_line(""))
            self.assertIn("isn't there", dosboxx.found_line(os.path.join(d, "gone")))
            self.assertIn("new enough", dosboxx.found_line(path, (2026, 10, 1), asked=True))
            old = dosboxx.found_line(path, (2024, 3, 1), asked=True)
            self.assertIn("too old", old)
            self.assertIn("2025.01.01", old)
            self.assertIn("can't be read", dosboxx.found_line(path, None, asked=True))

    def test_why_the_game_cant_start(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertIn("no DOSBox-X program", dosboxx.problem({}))
            self.assertIn("isn't there", dosboxx.problem({"dosbox_x_path": os.path.join(d, "gone")}))
            path = os.path.join(d, "dosbox-x")
            with open(path, "wb") as f:
                f.write(b"dosbox-x-2024.03.01.conf")
            old = dosboxx.problem({"dosbox_x_path": path})
            self.assertIn("too old", old)
            with open(path, "wb") as f:
                f.write(b"dosbox-x-2025.01.01.conf")
            self.assertIsNone(dosboxx.problem({"dosbox_x_path": path}))
            with open(path, "wb") as f:  # (a version that can't be read isn't refused: it may be fine)
                f.write(b"nothing")
            self.assertIsNone(dosboxx.problem({"dosbox_x_path": path}))


class MemoryFileTests(unittest.TestCase):
    def test_one_name_for_each_loader_folder(self):
        a, b = dosboxx.memory_path("/mods/one"), dosboxx.memory_path("/mods/two")
        self.assertNotEqual(a, b)
        self.assertEqual(a, dosboxx.memory_path("/mods/one"))
        self.assertTrue(os.path.basename(a).startswith("obsidian-edition-"))
        self.assertTrue(a.endswith(".mem"))

    def test_in_memory_on_linux_else_the_temp_folder(self):
        folder = dosboxx.memory_dir()
        if sys.platform.startswith("linux") and os.access("/dev/shm", os.W_OK):
            self.assertEqual(folder, "/dev/shm")
        else:
            self.assertEqual(folder, tempfile.gettempdir())

    def test_the_settings_can_name_another_folder(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(dosboxx.memory_dir({"dosbox_x_memory_dir": d}), d)
            self.assertEqual(os.path.dirname(dosboxx.memory_path("/mods/one", {"dosbox_x_memory_dir": d})), d)
            gone = os.path.join(d, "gone")
            self.assertEqual(dosboxx.memory_dir({"dosbox_x_memory_dir": gone}), dosboxx.memory_dir())

    def test_removed_and_gone_already_are_both_gone(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "x.mem")
            open(path, "wb").close()
            self.assertTrue(dosboxx.remove_memory_file(path))
            self.assertFalse(os.path.exists(path))
            self.assertTrue(dosboxx.remove_memory_file(path))
            self.assertTrue(dosboxx.remove_memory_file(""))
            self.assertFalse(dosboxx.remove_memory_file(d))  # (a folder: not taken away, and said)

    def test_read_from_a_configuration(self):
        with tempfile.TemporaryDirectory() as d:
            conf = os.path.join(d, "x.conf")
            with open(conf, "w", newline="") as f:
                f.write("[dosbox]\r\nmemsize=32\r\nmemory file=/dev/shm/a b.mem\r\n[cpu]\r\n")
            self.assertEqual(dosboxx.conf_memory_file(conf), "/dev/shm/a b.mem")
            with open(conf, "w") as f:
                f.write("[dosbox]\nmemsize=32\n")
            self.assertIsNone(dosboxx.conf_memory_file(conf))
            self.assertIsNone(dosboxx.conf_memory_file(os.path.join(d, "none.conf")))

    @unittest.skipUnless(os.path.isdir("/proc/self"), "needs /proc")
    def test_read_from_a_running_programs_command_line(self):
        import subprocess
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "x.conf"), "w") as f:
                f.write("[dosbox]\nmemory file=/dev/shm/mine.mem\n")
            child = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)", "-conf", "x.conf",
                                      "-nomenu"], cwd=d)
            try:
                import time
                for _ in range(200):  # (until the child is the program started, not still this one)
                    if dosboxx.process_memory_file(child.pid):
                        break
                    time.sleep(0.01)
                self.assertEqual(dosboxx.process_memory_file(child.pid), "/dev/shm/mine.mem")
            finally:
                child.kill()
                child.wait()
            self.assertIsNone(dosboxx.process_memory_file(child.pid))


class ConfTests(unittest.TestCase):
    def test_the_settings_the_mod_relies_on_are_all_said(self):
        conf = lines()
        self.assertEqual(section(conf, "dosbox")[:3], ["machine=svga_s3", "memsize=32", "memory file=/dev/shm/x.mem"])
        for line in ("ems=false", "xms=true", "umb=true", "minimum mcb free=100", "kernel allocation in umb=true",
                     "umb end=FBFF"):
            self.assertIn(line, section(conf, "dos"))
        # (the BIOS in 16 KB, so upper memory can run to FBFFh: `umb end` alone would turn it off)
        for line in ("rom bios allocation max=16", "rom bios minimum size=16"):
            self.assertIn(line, section(conf, "dosbox"))
        self.assertEqual(section(conf, "config"), ["dos=umb"])
        self.assertEqual(section(conf, "sblaster"), ["sbtype=sb16", "sbbase=220", "irq=5", "dma=1", "hdma=5"])
        for line in ("showmenu=false", "autolock=true", "middle_unlock=none", "clip_mouse_button=none"):
            self.assertIn(line, section(conf, "sdl"))
        for line in ("aspect=true", "doublescan=false"):
            self.assertIn(line, section(conf, "render"))

    def test_the_autoexec_runs_the_helper_and_the_patched_game(self):
        auto = section(lines(), "autoexec")
        self.assertEqual(auto, ["@echo off", 'mount c "/game"', 'mount d "/mod/dos"', "c:", r"d:\umbplus.com",
                                r"lh d:\dsclog.exe", r"d:\dsunlog.exe", r"d:\gameend.com", "exit"])

    def test_without_the_dice_log_it_just_runs_the_game(self):
        auto = section(lines(dice_log=False), "autoexec")
        self.assertNotIn(r"lh d:\dsclog.exe", auto)
        self.assertEqual(auto[-3:], ["darksun", r"d:\gameend.com", "exit"])

    def test_gogs_cloud_saves_are_overlaid(self):
        with tempfile.TemporaryDirectory() as d:
            os.mkdir(os.path.join(d, "cloud_saves"))
            auto = section(dosboxx.conf_lines(d, "/mod/dos", "/x.mem", {}, autoexec=AUTOEXEC), "autoexec")
            self.assertIn(f'mount c "{os.path.join(d, "cloud_saves")}" -t overlay', auto)

    def test_the_game_speed_has_its_own_numbers(self):
        for chosen, core, cycles in ((None, "dynamic", dosboxx.SPEEDS[35000][1]),
                                     (35000, "dynamic", dosboxx.SPEEDS[35000][1]),
                                     (30000, "dynamic", dosboxx.SPEEDS[35000][1]),  # (the fastest of before)
                                     (20000, "dynamic", dosboxx.SPEEDS[20000][1]),
                                     ("gog", "normal", dosboxx.SPEEDS["gog"][1]),
                                     (12345, "dynamic", dosboxx.SPEEDS[35000][1]),
                                     ("fast", "dynamic", dosboxx.SPEEDS[35000][1]),
                                     (True, "dynamic", dosboxx.SPEEDS[35000][1])):
            cpu = section(lines({} if chosen is None else {"cycles": chosen}), "cpu")
            self.assertEqual(cpu, [f"core={core}", "cputype=auto", f"cycles=fixed {cycles}"], chosen)

    def test_every_speed_the_options_tab_offers_has_one(self):
        self.assertEqual(set(dosboxx.SPEEDS), {launch.GOG_SPEED, *launch.SPEEDS})
        self.assertEqual(dosboxx.DEFAULT_SPEED, launch.DEFAULT_SPEED)
        self.assertEqual(dosboxx.FASTEST_BEFORE, launch.FASTEST_BEFORE)
        cycles = [dosboxx.SPEEDS[key][1] for key in (launch.GOG_SPEED, *launch.SPEEDS)]
        self.assertEqual(cycles, sorted(cycles))  # (GOG's own, Faster, Fastest: each faster)

    def window(self, scale, picture="plain"):
        settings = {"window_scale": scale, "picture": picture}
        conf = lines(settings)
        return section(conf, "sdl"), section(conf, "render")

    def test_the_single_window_is_always_plain(self):
        for picture in launch.PICTURES:
            sdl, render = self.window(1, picture)
            self.assertIn("output=surface", sdl)
            self.assertIn("windowresolution=original", sdl)
            self.assertIn("scaler=none", render)
            self.assertIn("sensitivity=100,100", sdl)

    def test_plain_windows(self):
        sdl, render = self.window(2)
        self.assertIn("output=surface", sdl)
        self.assertIn("scaler=normal2x", render)
        for scale in (3, 4):  # (through OpenGL: on the surface output these drew an empty window)
            sdl, render = self.window(scale)
            self.assertIn("output=openglnb", sdl)
            self.assertIn(f"windowresolution={320 * scale}x{240 * scale}", sdl)
            self.assertIn(f"scaler=normal{scale}x", render)

    def test_scanlines_and_tv_windows(self):
        for picture, scaler in (("scanlines", "scan"), ("tv", "tv")):
            for scale in (2, 3):
                sdl, render = self.window(scale, picture)
                self.assertIn("output=surface", sdl)
                self.assertIn(f"scaler={scaler}{scale}x", render)
            sdl, render = self.window(4, picture)  # (no 4x of either: 2x, doubled unsmoothed)
            self.assertIn("output=openglnb", sdl)
            self.assertIn("windowresolution=1280x960", sdl)
            self.assertIn(f"scaler={scaler}2x", render)

    def test_sharp_windows(self):
        for scale in (2, 3, 4):
            sdl, render = self.window(scale, "sharp")
            self.assertIn("output=openglnb", sdl)
            self.assertIn(f"windowresolution={320 * scale}x{240 * scale}", sdl)
            self.assertIn("scaler=none", render)

    def test_the_pointer_moves_as_the_desktops_across_and_down(self):
        for scale, speed in ((1, 100), (2, 50), (3, 33), (4, 25)):
            sdl, _ = self.window(scale)
            self.assertIn(f"sensitivity={speed},{speed}", sdl)
            self.assertIn("fullscreen=false", sdl)

    def test_a_window_size_the_loader_doesnt_know_is_the_default(self):
        for scale in (0, 7, "3", None, True):
            sdl, render = self.window(scale)
            self.assertIn("windowresolution=960x720", sdl, scale)

    def test_full_screen(self):
        for picture, output, scaler in (("plain", "opengl", "normal3x"), ("scanlines", "opengl", "scan3x"),
                                        ("tv", "opengl", "tv3x"), ("sharp", "openglnb", "none")):
            conf = lines({"fullscreen": True, "picture": picture, "window_scale": 1})
            sdl, render = section(conf, "sdl"), section(conf, "render")
            self.assertIn("fullscreen=true", sdl)
            self.assertIn("fullresolution=desktop", sdl)
            self.assertIn(f"output={output}", sdl)
            self.assertIn(f"scaler={scaler}", render)
            self.assertIn("sensitivity=100,100", sdl)
            self.assertIn("aspect=true", render)

    def test_a_picture_the_loader_doesnt_know_is_plain(self):
        sdl, render = self.window(3, "crt")
        self.assertIn("scaler=normal3x", render)

    def test_the_music_device(self):
        self.assertEqual(section(lines(), "midi"), ["mpu401=intelligent", "mididevice=default"])
        self.assertEqual(section(lines({"midi_device": 2}), "midi"),
                         ["mpu401=intelligent", "mididevice=win32", "midiconfig=2"])
        self.assertEqual(section(lines({"midi_device": "128:0"}), "midi"),
                         ["mpu401=intelligent", "mididevice=alsa", "midiconfig=128:0"])
        self.assertEqual(section(lines({"midi_device": "nonsense"}), "midi"),
                         ["mpu401=intelligent", "mididevice=default"])

    def test_the_soundfont_file(self):
        with tempfile.TemporaryDirectory() as d:
            font = os.path.join(d, "gm.sf2")
            open(font, "wb").close()
            self.assertEqual(section(lines({"soundfont": font}), "midi"),
                             ["mpu401=intelligent", "mididevice=synth", f"midiconfig={font}"])
            # (a device chosen goes before it; a file that isn't there is no soundfont)
            self.assertEqual(section(lines({"soundfont": font, "midi_device": 1}), "midi"),
                             ["mpu401=intelligent", "mididevice=win32", "midiconfig=1"])
            self.assertEqual(section(lines({"soundfont": os.path.join(d, "gone.sf2")}), "midi"),
                             ["mpu401=intelligent", "mididevice=default"])
            self.assertEqual(section(lines({"soundfont": 5}), "midi"), ["mpu401=intelligent", "mididevice=default"])
            self.assertIn("gm.sf2", dosboxx.music_line({"soundfont": font}))
            self.assertIn("isn't there", dosboxx.music_line({"soundfont": os.path.join(d, "gone.sf2")}))
            self.assertIn("No soundfont", dosboxx.music_line({}))
            self.assertIn("device 3", dosboxx.music_line({"soundfont": font, "midi_device": 3}))

    def test_mt32_is_never_written(self):
        for settings in ({}, {"midi_device": "mt32"}, {"midi_device": 0}):
            self.assertNotIn("mididevice=mt32", lines(settings))

    def test_a_tests_own_options(self):
        conf = lines(options={"core": "normal", "cycles": 12345, "capture": "/cap",
                              "extra": ["midi|fluid.driver=file"]})
        self.assertEqual(section(conf, "cpu"), ["core=normal", "cputype=auto", "cycles=fixed 12345"])
        self.assertEqual(conf[conf.index("[midi]") + 1], "fluid.driver=file")
        self.assertIn("captures=/cap", section(conf, "dosbox"))
        self.assertIn(r"dx-capture /a d:\dsunlog.exe", section(conf, "autoexec"))

    def test_the_arguments(self):
        self.assertEqual(dosboxx.arguments("/x/obsidian.conf"),
                         ["-conf", "/x/obsidian.conf", "-nopromptfolder", "-nomenu", "-fastlaunch"])


class LaunchTests(unittest.TestCase):
    """launch.py's branch: write_conf, is_game_dir, the lock file's memory line, the start."""

    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)
        d = self.dir.name
        names = ("SETTINGS", "HERE", "DBX_DIR", "DBX_CONF", "DBX_LOG", "GAME_LOCK", "CONF", "prepare_patched_game",
                 "STARTED", "STARTED_ENGINE", "STARTED_DOSBOX_X", "MEMORY_FILE", "LAST_SETTINGS", "recompiled_program", "recompiled_command",
                 "process_name")
        saved = {name: getattr(launch, name) for name in names}
        self.addCleanup(lambda: [setattr(launch, name, value) for name, value in saved.items()])
        self.addCleanup(launch.release_game)
        launch.HERE = d
        launch.SETTINGS = os.path.join(d, "settings.json")
        launch.DBX_DIR = os.path.join(d, "dosbox-x")
        launch.DBX_CONF = os.path.join(launch.DBX_DIR, "obsidian.conf")
        launch.DBX_LOG = os.path.join(launch.DBX_DIR, "dosbox-x.log")
        launch.GAME_LOCK = os.path.join(d, "game.lock")
        launch.CONF = os.path.join(d, "dosbox_dicelog.conf")
        launch.prepare_patched_game = lambda game_dir, settings=None: None
        launch.recompiled_program = lambda settings=None: None
        launch.process_name = lambda pid: "dosbox-x"  # (the stand-in is a shell script: the system names its shell)
        self.bundled = no_bundled(self)
        self.game = os.path.join(d, "game")
        os.mkdir(self.game)
        open(os.path.join(self.game, "DSUN.EXE"), "wb").close()
        self.memory = os.path.join(d, "mem")
        os.mkdir(self.memory)

    def program(self, version="2026.10.01", seconds=30):
        """A stand-in for DOSBox-X: a script that answers -version and otherwise sleeps."""
        os.makedirs(os.path.join(self.dir.name, "bin"), exist_ok=True)
        path = os.path.join(self.dir.name, "bin", "dosbox-x")
        with open(path, "w") as f:
            f.write(f"#!/bin/sh\n# dosbox-x-{version}.conf\n"
                    f"if [ \"$1\" = -version ]; then echo 'DOSBox-X version {version} SDL2'; exit 0; fi\n"
                    f"echo started \"$@\"\nexec sleep {seconds}\n")
        os.chmod(path, os.stat(path).st_mode | stat.S_IXUSR)
        return path

    def settings(self, **more):
        s = {"engine": "dosbox-x", "dosbox_x_memory_dir": self.memory}
        s.update(more)
        launch.save_settings(dict(s))
        return s

    def test_a_folder_with_only_the_game_is_a_game_folder_for_dosbox_x(self):
        launch.save_settings({})
        self.assertFalse(launch.is_game_dir(self.game))  # (GOG's engine wants GOG's DOSBOX folder)
        self.assertIn("DOSBOX folder", launch.game_dir_wanted())
        self.settings()
        self.assertTrue(launch.is_game_dir(self.game))
        self.assertIn("isn't needed", launch.game_dir_wanted())
        self.assertFalse(launch.is_game_dir(self.dir.name))  # (no DSUN.EXE)

    def test_write_conf_writes_dosbox_xs_whole_configuration(self):
        settings = self.settings(window_scale=2, picture="tv", cycles=20000)
        path = launch.write_conf(self.game, settings=settings)
        self.assertEqual(path, launch.DBX_CONF)
        with open(path, encoding="utf-8") as f:
            conf = f.read().splitlines()
        memory = dosboxx.memory_path(launch.HERE, settings)
        self.assertEqual(os.path.dirname(memory), self.memory)
        self.assertIn(f"memory file={memory}", conf)
        self.assertIn("scaler=tv2x", conf)
        self.assertIn(f"cycles=fixed {dosboxx.SPEEDS[20000][1]}", conf)
        self.assertIn(f'mount c "{self.game}"', conf)
        self.assertIn(f'mount d "{launch.DOS_DIR}"', conf)
        self.assertNotIn('mount c ".."', conf)  # (nothing of GOG's configuration)
        self.assertEqual(dosboxx.conf_memory_file(path), memory)

    def test_gogs_engine_writes_gogs_as_before(self):
        path = launch.write_conf(self.game, settings={"window_scale": 2})
        self.assertEqual(path, launch.CONF)
        with open(path, encoding="utf-8") as f:
            conf = f.read().splitlines()
        self.assertIn('mount c ".."', conf)
        self.assertFalse(any(line.startswith("memory file") for line in conf))
        self.assertFalse(os.path.exists(launch.DBX_DIR))

    def test_the_start_is_refused_with_no_program_or_an_old_one(self):
        self.settings()
        with self.assertRaises(launch.LaunchError) as raised:
            launch.launch(self.game)
        self.assertIn("no DOSBox-X program", str(raised.exception))
        self.settings(dosbox_x_path=self.program("2024.03.01"))
        with self.assertRaises(launch.LaunchError) as raised:
            launch.launch(self.game)
        self.assertIn("too old", str(raised.exception))
        self.assertFalse(launch.holds_game())

    @unittest.skipIf(os.name == "nt", "a shell script stands in for the program")
    def test_with_none_chosen_the_mods_dosbox_x_starts_unless_the_recompiled_program_is_there(self):
        program = self.program()
        os.replace(program, os.path.join(self.bundled, "dosbox-x"))
        program = os.path.join(self.bundled, "dosbox-x")
        launch.save_settings({"dosbox_x_memory_dir": self.memory})
        self.assertTrue(launch.is_game_dir(self.game))  # (no DOSBOX folder needed)
        proc, problem = launch.launch(self.game, "a test")
        try:
            self.assertEqual(proc.args[0], program)
            self.assertEqual(launch.STARTED_ENGINE, dosboxx.DOSBOX_X)
        finally:
            proc.kill()
            proc.wait()
            launch.release_game()
        # the recompiled program, found beside the mod, comes before DOSBox-X none chosen...
        started = []

        class Started:
            pid = os.getpid()
            args = ["recompiled"]

        popen = launch.subprocess.Popen
        self.addCleanup(lambda: setattr(launch.subprocess, "Popen", popen))
        launch.recompiled_program = lambda settings=None: os.path.join(self.dir.name, "dsun-recompiled")
        launch.recompiled_command = lambda program, game_dir: [program]
        launch.subprocess.Popen = lambda args, **k: started.append(args) or Started()
        launch._launch(self.game, launch.load_settings())
        self.assertEqual(started, [[os.path.join(self.dir.name, "dsun-recompiled")]])
        self.assertEqual(launch.STARTED_ENGINE, dosboxx.GOG)
        # ... but not before DOSBox-X chosen on the Options tab
        launch.subprocess.Popen = popen
        launch.save_settings({"dosbox_x_memory_dir": self.memory, "engine": "dosbox-x"})
        proc, problem = launch._launch(self.game, launch.load_settings())
        try:
            self.assertEqual(proc.args[0], program)
        finally:
            proc.kill()
            proc.wait()

    @unittest.skipIf(os.name == "nt", "a shell script stands in for the program")
    def test_the_start_the_lock_files_memory_line_and_the_end(self):
        program = self.program()
        settings = self.settings(dosbox_x_path=program)
        memory = dosboxx.memory_path(launch.HERE, settings)
        with open(memory, "wb") as f:  # (an earlier game's, left behind: taken away before the start)
            f.write(b"old")
        proc, problem = launch.launch(self.game, "a test")
        try:
            self.assertIsNone(problem)
            self.assertFalse(os.path.exists(memory))
            self.assertEqual(proc.args, [program, "-conf", launch.DBX_CONF, "-nopromptfolder", "-nomenu",
                                         "-fastlaunch"])
            self.assertEqual((launch.STARTED, launch.STARTED_ENGINE, launch.MEMORY_FILE),
                             (None, dosboxx.DOSBOX_X, memory))
            self.assertEqual(launch.engine_name(), "DOSBox-X")
            self.assertIn("in DOSBox-X", launch.started_line(self.game))
            self.assertEqual(launch.lock_game(), (proc.pid, "dosbox-x"))
            self.assertEqual(launch.lock_memory(), memory)
            self.assertEqual(launch.memory_game(), (proc.pid, memory))
            self.assertEqual(launch.game_memory_file(proc.pid), memory)
            self.assertEqual(launch.game_memory_file(os.getpid()), "")
            with open(memory, "wb") as f:  # (DOSBox-X makes it)
                f.write(b"ram")
            # the Loader closed while the game runs on: the lock's lines and the file stay
            launch.release_game()
            self.assertTrue(os.path.exists(memory))
            self.assertEqual(launch.memory_game(), (proc.pid, memory))
            launch.hold_game("another Loader")
            self.assertEqual(launch.game_memory_file(proc.pid), memory)
            with self.assertRaises(launch.GameBusy):
                launch.launch(self.game, "another Loader")
            import time
            for _ in range(300):  # (until the stand-in has printed its line)
                if os.path.getsize(launch.DBX_LOG):
                    break
                time.sleep(0.01)
        finally:
            proc.kill()
            proc.wait()
        self.assertEqual(launch.closed_line(0), "DOSBox-X closed.")
        self.assertIn("signal 9", launch.closed_line(proc.returncode))
        self.assertIn("DOSBox-X closed", launch.closed_line(proc.returncode))
        self.assertEqual(launch.game_end_note(), launch.CUT_OFF)  # (killed mid-game: it didn't end on its own)
        output = launch.dosbox_output(self.game, 0)
        self.assertIn("started -conf", output["output (dosbox-x.log)"])
        launch.release_game()  # (the game ended: its memory file goes)
        self.assertFalse(os.path.exists(memory))
        self.assertEqual(launch.memory_game(), (0, ""))

    @unittest.skipIf(os.name == "nt", "a shell script stands in for the program")
    def test_a_memory_file_left_by_a_game_no_loader_saw_end_is_taken_away(self):
        program = self.program(seconds=0)
        settings = self.settings(dosbox_x_path=program)
        memory = dosboxx.memory_path(launch.HERE, settings)
        proc, _ = launch.launch(self.game, "a test")
        with open(memory, "wb") as f:
            f.write(b"ram")
        _HELD = dict(launch._HELD)
        # (as if this Loader had closed while the game ran: the file and the lock's lines left)
        os.close(launch._HELD.pop("fd"))
        launch._HELD.clear()
        proc.wait()
        self.assertTrue(os.path.exists(memory))
        self.assertTrue(_HELD)
        launch.hold_game("the next Loader")
        self.assertFalse(os.path.exists(memory))
        self.assertEqual(launch.lock_memory(), "")

    def test_gogs_closed_lines_are_as_before(self):
        launch.STARTED, launch.STARTED_ENGINE = None, dosboxx.GOG
        self.assertEqual(launch.closed_line(0), "DOSBox closed.")
        self.assertIn("an access violation", launch.closed_line(0xC0000005 - (1 << 32)))
        self.assertIn("an access violation", launch.closed_line(0xC0000005))
        self.assertEqual(launch.closed_line(3), "DOSBox closed with exit code 3.")


class AppTests(unittest.TestCase):
    def test_a_macos_app_is_the_program_inside_it(self):
        with tempfile.TemporaryDirectory() as d:
            app = os.path.join(d, "dosbox-x.app")
            inside = os.path.join(app, "Contents", "MacOS")
            os.makedirs(inside)
            self.assertEqual(dosboxx.app_program(app), app)  # (no program in it yet: as given)
            exe = os.path.join(inside, "dosbox-x")
            open(exe, "wb").close()
            self.assertEqual(dosboxx.app_program(app), exe)
            self.assertEqual(dosboxx.app_program(app + "/"), exe)
            self.assertEqual(dosboxx.program({dosboxx.PATH_SETTING: app}), exe)
            self.assertEqual(dosboxx.app_program(exe), exe)  # (a program is itself)
            self.assertIsNone(dosboxx.app_program(None))


if __name__ == "__main__":
    unittest.main()
