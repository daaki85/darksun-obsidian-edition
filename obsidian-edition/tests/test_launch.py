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


class LaunchTests(unittest.TestCase):
    def test_recognises_the_game_folder(self):
        with tempfile.TemporaryDirectory() as d:
            game = make_game(d, cloud_saves=False)
            self.assertTrue(launch.is_game_dir(game))
            self.assertFalse(launch.is_game_dir(d))
            self.assertEqual(launch.find_game_dir(game), game)

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
        self.assertIn("A vulture! Give it here.", text)
        with tempfile.TemporaryDirectory() as d:
            path = launch.write_crash_report(text, 1000.0, os.path.join(d, "crash-logs"))
            self.assertTrue(os.path.basename(path).startswith("crash-") and path.endswith(".txt"))
            with open(path, encoding="utf-8") as f:
                self.assertEqual(f.read(), text)
            again = launch.write_crash_report(text, 1000.0, os.path.join(d, "crash-logs"))
            self.assertNotEqual(again, path)
            self.assertTrue(again.endswith("-2.txt"))

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
                         ["[sdl]", "fullscreen=false", "[render]", "aspect=true", "scaler=normal3x", ""])
        self.assertIn("scaler=normal3x", launch.display_lines({"window_scale": 3}))
        self.assertIn("scaler=none", launch.display_lines({"window_scale": 1}))
        self.assertIn("scaler=normal3x", launch.display_lines({"window_scale": 7}))
        self.assertIn("scaler=normal2x", launch.display_lines({"window_scale": 2}))
        four = launch.display_lines({"window_scale": 4})
        self.assertIn("windowresolution=1280x960", four)
        self.assertIn("output=opengl", four)
        self.assertEqual(launch.display_lines({"fullscreen": True}), [])  # GOG's own full screen
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
