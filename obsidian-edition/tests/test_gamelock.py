"""One Loader at a time on the game (launch.hold_game), settings.json read and written safely with
several Loaders about (a temporary file of each write's own; an unreadable file never saved over or
taken for the defaults; a hand-edited file's odd shapes read, not raised), and the Loader attaching
to the DOSBox it started by its pid."""

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)

from dsloader import launch  # noqa: E402
from dsloader import __main__ as cli  # noqa: E402

# a second process taking the lock and keeping it until its stdin closes
HOLDER = """
import sys
sys.path.insert(0, sys.argv[1])
from dsloader import launch
launch.hold_game("Play Dark Sun (in-game rolls)", sys.argv[2])
print("held", flush=True)
sys.stdin.read()
"""


class GameLockTests(unittest.TestCase):
    def setUp(self):
        d = tempfile.mkdtemp()
        self.addCleanup(lambda: __import__("shutil").rmtree(d, ignore_errors=True))
        self.lock = os.path.join(d, "game.lock")
        self.addCleanup(launch.release_game)

    def holder(self) -> subprocess.Popen:
        proc = subprocess.Popen([sys.executable, "-c", HOLDER, HERE, self.lock], stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE, text=True)
        def end():
            if proc.poll() is None:
                proc.kill()
            proc.wait()
            proc.stdin.close()
            proc.stdout.close()
        self.addCleanup(end)
        self.assertEqual(proc.stdout.readline().strip(), "held")
        return proc

    def test_a_second_process_is_refused_naming_the_first(self):
        proc = self.holder()
        with self.assertRaises(launch.GameBusy) as caught:
            launch.hold_game("the Loader's window", self.lock)
        self.assertIn(f"Play Dark Sun (in-game rolls) (process {proc.pid})", str(caught.exception))
        self.assertFalse(launch.holds_game())

    def test_a_dead_holders_lock_is_no_lock(self):
        """The holder killed (no release): its lock went with it, and its file is taken over."""
        proc = self.holder()
        proc.kill()
        proc.wait()
        self.assertTrue(os.path.exists(self.lock))
        launch.hold_game("the Loader's window", self.lock)
        self.assertEqual(launch.lock_holder(self.lock), (os.getpid(), "the Loader's window"))

    def test_held_again_by_the_same_process_and_released(self):
        launch.hold_game("the Loader's window", self.lock)
        launch.hold_game("the Loader's window", self.lock)  # (a second start from the same window)
        self.assertTrue(launch.holds_game())
        launch.release_game()
        self.assertFalse(launch.holds_game())
        self.assertFalse(os.path.exists(self.lock))
        launch.release_game()  # (nothing held: nothing done)

    def test_without_a_system_lock_the_pid_decides(self):
        """Where the file can't be locked (a network drive), a live pid in it refuses and a dead
        one's file is taken over."""
        with open(self.lock, "w") as f:
            f.write("4000000 the dicelog command\n")
        with mock.patch.object(launch, "_lock_file", lambda fd: None):
            with mock.patch.object(launch, "pid_alive", lambda pid: True):
                with self.assertRaises(launch.GameBusy) as caught:
                    launch.hold_game("the Loader's window", self.lock)
                self.assertIn("the dicelog command (process 4000000)", str(caught.exception))
            with mock.patch.object(launch, "pid_alive", lambda pid: False):
                launch.hold_game("the Loader's window", self.lock)
        self.assertEqual(launch.lock_holder(self.lock)[0], os.getpid())

    def test_pid_alive(self):
        self.assertTrue(launch.pid_alive(os.getpid()))
        self.assertFalse(launch.pid_alive(0))

    def test_launch_refused_before_anything_is_written(self):
        """A second launch while another holds the game: GameBusy, and the dos folder's copies
        (prepare_patched_game) not touched."""
        self.holder()
        with tempfile.TemporaryDirectory() as d, \
                mock.patch.object(launch, "GAME_LOCK", self.lock), \
                mock.patch.object(launch, "SETTINGS", os.path.join(d, "settings.json")), \
                mock.patch.object(launch, "prepare_patched_game") as prepare:
            with self.assertRaises(launch.GameBusy):
                launch.launch(d)
            prepare.assert_not_called()

    def test_dicelog_command_refused(self):
        self.holder()
        with mock.patch.object(launch, "GAME_LOCK", self.lock):
            with self.assertRaises(cli.CliError) as caught:
                cli.cmd_dicelog(argparse.Namespace(pid=None, host_base=None, raw=False, all=False))
        self.assertIn("already started or followed by", str(caught.exception))


class SettingsTests(unittest.TestCase):
    def setUp(self):
        d = tempfile.mkdtemp()
        self.addCleanup(lambda: __import__("shutil").rmtree(d, ignore_errors=True))
        self.dir = d
        patcher = mock.patch.object(launch, "SETTINGS", os.path.join(d, "settings.json"))
        patcher.start()
        self.addCleanup(patcher.stop)

    def write(self, data) -> None:
        with open(launch.SETTINGS, "w") as f:
            json.dump(data, f)

    def test_each_write_has_a_temporary_file_of_its_own(self):
        used = []
        real = os.replace

        def replace(src, dst):
            used.append(os.path.basename(src))
            return real(src, dst)
        with mock.patch("os.replace", replace):
            launch.save_settings({"dust": False})
            launch.save_settings({"dust": True})
        self.assertEqual(len(set(used)), 2)
        self.assertNotIn("settings.json.tmp", used)
        self.assertTrue(all(name.startswith("settings.json.") and name.endswith(".tmp") for name in used))
        self.assertEqual(os.listdir(self.dir), ["settings.json"])  # (none left behind)

    def test_a_failed_write_leaves_no_temporary_file(self):
        with mock.patch("os.replace", side_effect=PermissionError(13, "in use")), mock.patch("time.sleep"):
            with self.assertRaises(PermissionError):
                launch.save_settings({"dust": False})
        self.assertEqual(os.listdir(self.dir), [])

    def test_unreadable_is_not_missing(self):
        """Missing: no settings, strictly or not. There but held elsewhere: tried again, then a
        plain read gives none and a strict one raises SettingsUnreadable (an OSError)."""
        self.assertEqual(launch.load_settings(strict=True), {})
        self.write({"dust": False})
        import builtins
        real_open = builtins.open
        tries = []

        def locked(path, *args, **kwargs):
            if path == launch.SETTINGS:
                tries.append(1)
                raise PermissionError(13, "in use", path)
            return real_open(path, *args, **kwargs)
        with mock.patch("builtins.open", locked), mock.patch("time.sleep"):
            self.assertEqual(launch.load_settings(), {})
            self.assertEqual(len(tries), launch.SETTINGS_TRIES)
            with self.assertRaises(launch.SettingsUnreadable) as caught:
                launch.load_settings(strict=True, tries=3)
            self.assertIn("can't be read just now", caught.exception.strerror)
            with self.assertRaises(launch.LaunchError):  # (a launch never builds the copies from defaults)
                launch.launch(self.dir)
        self.assertIs(launch.load_settings()["dust"], False)

    def test_a_second_unreadable_file_keeps_the_first(self):
        for text in ("{cut", "{also cut"):
            with open(launch.SETTINGS, "w") as f:
                f.write(text)
            self.assertEqual(launch.load_settings(), {})
        with open(launch.SETTINGS + ".bad") as f:
            self.assertEqual(f.read(), "{cut")
        with open(launch.SETTINGS + ".bad-2") as f:
            self.assertEqual(f.read(), "{also cut")

    def test_hand_edited_shapes_are_read(self):
        """A string settings_version, speakers that aren't a dict, pickpocketed that isn't a list:
        read (the odd ones dropped), never raised at every start."""
        self.write({"settings_version": "2", "speakers": "Tarkon", "speakers_learned": [1, 2],
                    "pickpocketed": 5, "dust": False})
        settings = launch.load_settings()
        self.assertEqual(settings["dust"], False)
        self.assertNotIn("speakers", settings)
        self.assertEqual(launch.speaker_names(), {})
        self.assertEqual(launch.learned_speakers(), {})
        self.assertEqual(launch.pickpocketed(), [])
        launch.set_speaker_name(5, "Tarkon")
        launch.add_learned_speakers({6: "Dinos"})
        self.assertEqual(launch.speaker_names(), {5: "Tarkon"})
        self.assertEqual(launch.learned_speakers(), {6: "Dinos"})
        self.write({"settings_version": "two", "combat_log": False})
        self.assertEqual(launch.load_settings()["combat_log"], True)  # (version 1: upgraded)
        self.write({"settings_version": 2, "pickpocketed": ["a@1", 7]})
        self.assertEqual(launch.pickpocketed(), ["a@1"])


class ConnectTests(unittest.TestCase):
    def test_the_started_dosbox_by_its_pid(self):
        """With another DOSBox running too, the one the Loader started is attached by its pid; an
        explicit --pid still wins; with neither, two DOSBoxes ask for --pid."""
        found = [(10, "DOSBox.exe"), (20, "DOSBox.exe")]
        with mock.patch.object(cli, "find_dosbox_processes", lambda: found), \
                mock.patch.object(cli, "_located", lambda pid, host_base=None: pid):
            self.assertEqual(cli.connect(argparse.Namespace(pid=None, host_base=None), 20), 20)
            self.assertEqual(cli.connect(argparse.Namespace(pid=10, host_base=None), 20), 10)
            with self.assertRaises(cli.CliError):
                cli.connect(argparse.Namespace(pid=None, host_base=None))


if __name__ == "__main__":
    unittest.main()
