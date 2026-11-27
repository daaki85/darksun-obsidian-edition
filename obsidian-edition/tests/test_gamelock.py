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
import threading
import unittest
from unittest import mock

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)

from dsloader import launch  # noqa: E402
from dsloader import __main__ as cli  # noqa: E402
from dsloader import ravlog  # noqa: E402,F401  (imported before a test mocks DiceLog: ravlog.PASS reads DiceLog.PASS at import)

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

    def game(self) -> subprocess.Popen:
        """A process standing in for the game a Loader started (DOSBox)."""
        proc = subprocess.Popen([sys.executable, "-c", "import sys; sys.stdin.read()"], stdin=subprocess.PIPE)

        def end():
            if proc.poll() is None:
                proc.kill()
            proc.wait()
            proc.stdin.close()
        self.addCleanup(end)
        return proc

    def test_the_game_outlives_the_loader_that_started_it(self):
        """The window closed with its game still running: the lock goes, but the game's line stays
        in the file, so a second start is refused (the copies not rebuilt under the running game)
        while a Loader following that game may still take the lock; once the game has closed, a
        start goes ahead."""
        game = self.game()
        launch.hold_game("the Loader's window", self.lock)
        launch.note_game(game.pid, sys.executable)
        self.assertEqual(launch.lock_game(self.lock), (game.pid, os.path.basename(os.path.realpath(sys.executable)).lower()))
        launch.release_game()
        self.assertTrue(os.path.exists(self.lock))  # (kept: the game runs on)
        self.assertEqual(launch.running_game(self.lock), game.pid)
        launch.hold_game("the dicelog command", self.lock)  # (following it: allowed, its line kept)
        self.assertEqual(launch.lock_game(self.lock)[0], game.pid)
        launch.release_game()
        with tempfile.TemporaryDirectory() as d, \
                mock.patch.object(launch, "GAME_LOCK", self.lock), \
                mock.patch.object(launch, "SETTINGS", os.path.join(d, "settings.json")), \
                mock.patch.object(launch, "_launch") as started:
            with self.assertRaises(launch.GameBusy) as caught:
                launch.launch(d)
            self.assertIn(f"still running (process {game.pid})", str(caught.exception))
            started.assert_not_called()
            self.assertFalse(launch.holds_game())
            game.kill()
            game.wait()
            self.assertEqual(launch.running_game(self.lock), 0)
            started.return_value = (mock.Mock(pid=4321, args=["DOSBox.exe", "-conf"]), None)
            launch.launch(d)
            started.assert_called_once()
            self.assertEqual(launch.lock_game(self.lock)[0], 4321)
            self.assertEqual(launch.LAST_SETTINGS, {})

    def test_a_pid_reused_by_another_program_is_not_the_game(self):
        with mock.patch.object(launch, "pid_alive", lambda pid: True):
            with mock.patch.object(launch, "process_name", lambda pid: "notepad.exe"):
                self.assertFalse(launch.game_alive(1234, "dosbox.exe"))
            with mock.patch.object(launch, "process_name", lambda pid: "DOSBox.exe".lower()):
                self.assertTrue(launch.game_alive(1234, "DOSBox.exe"))
            with mock.patch.object(launch, "process_name", lambda pid: None):  # (can't tell: alive is enough)
                self.assertTrue(launch.game_alive(1234, "dosbox.exe"))
        self.assertFalse(launch.game_alive(0, "dosbox.exe"))

    def test_a_dead_games_lock_file_is_taken_away(self):
        game = self.game()
        launch.hold_game("the Loader's window", self.lock)
        launch.note_game(game.pid, "python")
        game.kill()
        game.wait()
        launch.release_game()
        self.assertFalse(os.path.exists(self.lock))

    @unittest.skipUnless(sys.platform.startswith("linux") or os.name == "nt", "no way to ask a process's program")
    def test_process_name(self):
        self.assertEqual(launch.process_name(os.getpid()), os.path.basename(os.path.realpath(sys.executable)).lower())
        self.assertIsNone(launch.process_name(0))

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
            launch.save_settings({"steady_pace": False})
            launch.save_settings({"steady_pace": True})
        self.assertEqual(len(set(used)), 2)
        self.assertNotIn("settings.json.tmp", used)
        self.assertTrue(all(name.startswith("settings.json.") and name.endswith(".tmp") for name in used))
        self.assertEqual(os.listdir(self.dir), ["settings.json"])  # (none left behind)

    def test_a_failed_write_leaves_no_temporary_file(self):
        with mock.patch("os.replace", side_effect=PermissionError(13, "in use")), mock.patch("time.sleep"):
            with self.assertRaises(PermissionError):
                launch.save_settings({"steady_pace": False})
        self.assertEqual(os.listdir(self.dir), [])

    def test_unreadable_is_not_missing(self):
        """Missing: no settings, strictly or not. There but held elsewhere: tried again, then a
        plain read gives none and a strict one raises SettingsUnreadable (an OSError)."""
        self.assertEqual(launch.load_settings(strict=True), {})
        self.write({"steady_pace": False})
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
        self.assertIs(launch.load_settings()["steady_pace"], False)

    def held(self):
        """settings.json held elsewhere (an antivirus, a backup) while the block runs."""
        import builtins
        real_open = builtins.open

        def locked(path, *args, **kwargs):
            if path == launch.SETTINGS:
                raise PermissionError(13, "in use", path)
            return real_open(path, *args, **kwargs)
        import contextlib
        stack = contextlib.ExitStack()
        stack.enter_context(mock.patch("builtins.open", locked))
        stack.enter_context(mock.patch("time.sleep"))
        return stack

    def test_pickpocketed_read_strictly(self):
        """The pockets tried, held elsewhere: SettingsUnreadable, never [] (which the next pick
        would save over every earlier try)."""
        self.write({"pickpocketed": ["Dag|41|7|Trader@500"]})
        with self.held():
            with self.assertRaises(launch.SettingsUnreadable):
                launch.pickpocketed()
        self.assertEqual(launch.pickpocketed(), ["Dag|41|7|Trader@500"])

    def test_prepare_reads_the_switches_strictly(self):
        """prepare_patched_game with no settings given never builds the copies from the defaults."""
        self.write({"kalzith": False})
        with self.held(), mock.patch.object(launch.gamepatch, "write_patched") as patched:
            with self.assertRaises(launch.SettingsUnreadable):
                launch.prepare_patched_game(self.dir)
            patched.assert_not_called()

    def test_dicelog_command_waits_for_the_settings(self):
        """The dicelog command's switches and rules read strictly: a file held at the start is
        waited for, not taken for every rule on."""
        self.write({"pickpocketed": ["Dag|41|7|Trader@500"], "helms": False})
        tries = []
        real = launch.load_settings

        def load(strict=False, tries_=None, **kwargs):
            if strict and not tries:
                tries.append(1)
                raise launch.SettingsUnreadable(13, "settings.json can't be read just now (in use)")
            return real(strict=strict, **kwargs)

        class Stop(Exception):
            pass
        log, guest = mock.Mock(), mock.Mock()
        log.use_settings.side_effect = Stop
        with mock.patch.object(launch, "load_settings", load), mock.patch.object(cli, "connect", return_value=guest), \
                mock.patch("dsloader.dicelog.DiceLog", return_value=log), mock.patch("time.sleep"), \
                mock.patch("builtins.print"):
            with self.assertRaises(Stop):
                cli._follow(argparse.Namespace(pid=None, host_base=None, raw=False, all=False))
        self.assertEqual(tries, [1])
        settings, = log.use_settings.call_args.args
        self.assertEqual(settings["pickpocketed"], ["Dag|41|7|Trader@500"])
        self.assertIs(settings["helms"], False)
        log.use_settings.assert_called_once_with(settings)
        log.close.assert_called_once()
        guest.proc.close.assert_called_once()

    def test_dicelog_waits_for_dosbox_again(self):
        """When DOSBox exits, close the old log and handle before connecting again."""
        from dsloader.dicelog import DiceLog
        from dsloader.process import ProcessError
        first_guest, next_guest = mock.Mock(), mock.Mock()
        first_log, next_log = DiceLog(first_guest), DiceLog(next_guest)
        for log in (first_log, next_log):
            self.addCleanup(log.close)
            log.guest.proc.close.side_effect = lambda log=log: self.assertFalse(log._stats_thread.is_alive())
        worker_started = threading.Event()

        def answer_stats():
            worker_started.set()
            first_log._stats_stop.wait(5)
            return False

        def disconnect():
            self.assertTrue(worker_started.wait(5))
            raise ProcessError("DOSBox closed")

        first_log._answer_stats = answer_stats
        first_log.attach = mock.Mock(return_value="Dice log attached.")
        first_log.still_patched = disconnect
        next_log.attach = mock.Mock(side_effect=KeyboardInterrupt)

        def connect(args):
            if not first_log.attach.called:
                return first_guest
            first_guest.proc.close.assert_called_once()
            self.assertFalse(first_log._stats_thread.is_alive())
            return next_guest

        with mock.patch.object(cli, "connect", side_effect=connect) as opened, \
                mock.patch("dsloader.dicelog.DiceLog", side_effect=[first_log, next_log]), mock.patch("time.sleep"), \
                mock.patch("builtins.print") as said:
            cli._follow(argparse.Namespace(pid=None, host_base=None, raw=False, all=False))
        self.assertEqual(opened.call_count, 2)
        said.assert_any_call("DOSBox can't be read any more (DOSBox closed). Waiting for it...", flush=True)
        next_guest.proc.close.assert_called_once()
        self.assertFalse(next_log._stats_thread.is_alive())

    def test_play_says_settings_unreadable(self):
        """Play Dark Sun (in-game rolls) with settings.json held elsewhere: said as the window says
        it, not "Something went wrong"."""
        import tempfile
        from unittest import mock
        said = []

        def unreadable(args):
            raise launch.SettingsUnreadable(13, "settings.json can't be read just now (in use)")
        with tempfile.TemporaryDirectory() as d, mock.patch.object(launch, "HERE", d), \
                mock.patch.object(cli, "_game_dir", unreadable), \
                mock.patch.dict(sys.modules, {"tkinter": None}), \
                mock.patch("builtins.print", lambda *a, **k: said.append(" ".join(map(str, a)))):
            cli.cmd_play(argparse.Namespace())
        self.assertEqual(len(said), 1)
        self.assertIn("settings.json can't be read just now (in use): it may be held by a backup", said[0])

    def test_play_starts_the_sequel(self):
        """`play --ravager` (Play Wake of the Ravager (in-game rolls).bat): the sequel's folder started, not
        Shattered Lands', and its dice log made by the helper the game loaded (ravlog.make) once it is there."""
        import tempfile
        dosbox = mock.Mock(pid=7, returncode=0)
        dosbox.poll.side_effect = [None, None, None, 0, 0]
        made = mock.Mock()
        made.lines.return_value = []
        made.take_dialogue.return_value = []
        with tempfile.TemporaryDirectory() as d, mock.patch.object(launch, "HERE", d), \
                mock.patch.object(cli, "_ravager_dir", return_value="/wotr"), \
                mock.patch.object(cli, "_game_dir", side_effect=AssertionError("Shattered Lands' folder asked")), \
                mock.patch.object(launch, "launch", return_value=(dosbox, None)) as started, \
                mock.patch.object(launch, "LAST_SETTINGS", {}), mock.patch.object(launch, "left_out_line", return_value=None), \
                mock.patch.object(launch, "game_end_note", return_value=None), mock.patch.object(launch, "release_game"), \
                mock.patch.object(cli, "connect", return_value=mock.Mock()), \
                mock.patch.object(ravlog, "running", side_effect=[None, True]), \
                mock.patch.object(ravlog, "make", return_value=made) as make, mock.patch("time.sleep"):
            cli.cmd_play(argparse.Namespace(ravager=True))
            with open(os.path.join(d, "play.log")) as f:
                said = f.read()
        self.assertEqual(started.call_args[0], ("/wotr", "Play Wake of the Ravager (in-game rolls)"))
        make.assert_called_once()
        made.attach.assert_called_once()
        self.assertIn("The dice log follows Wake of the Ravager.", said)

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
                    "pickpocketed": 5, "steady_pace": False})
        settings = launch.load_settings()
        self.assertEqual(settings["steady_pace"], False)
        self.assertNotIn("speakers", settings)
        self.assertEqual(launch.speaker_names(), {})
        self.assertEqual(launch.learned_speakers(), {})
        self.assertEqual(launch.pickpocketed(), [])
        launch.set_speaker_name(5, "Tarkon")
        launch.add_learned_speakers({6: "Dinos"})
        self.assertEqual(launch.speaker_names(), {5: "Tarkon"})
        self.assertEqual(launch.learned_speakers(), {6: "Dinos"})
        self.write({"settings_version": "two", "combat_log": False})
        self.assertEqual(launch.load_settings()["settings_version"], launch.SETTINGS_VERSION)  # (version 1: upgraded)
        self.write({"settings_version": 2, "pickpocketed": ["a@1", 7]})
        self.assertEqual(launch.pickpocketed(), ["a@1"])


class ConnectTests(unittest.TestCase):
    def test_dicelog_closes_the_process_when_log_construction_fails(self):
        guest = mock.Mock()
        with mock.patch.object(cli, "connect", return_value=guest), \
                mock.patch("dsloader.dicelog.DiceLog", side_effect=RuntimeError("setup failed")):
            with self.assertRaisesRegex(RuntimeError, "setup failed"):
                cli._follow_once(argparse.Namespace(raw=False, all=False))
        guest.proc.close.assert_called_once()

    def test_dicelog_closes_the_process_when_the_worker_cannot_start(self):
        guest = mock.Mock()
        with mock.patch.object(cli, "connect", return_value=guest), \
                mock.patch("threading.Thread.start", side_effect=RuntimeError("cannot start worker")):
            with self.assertRaisesRegex(RuntimeError, "cannot start worker"):
                cli._follow_once(argparse.Namespace(raw=False, all=False))
        guest.proc.close.assert_called_once()

    def test_dicelog_reattaches_inside_the_same_dosbox(self):
        guest, log = mock.Mock(), mock.Mock()

        def attach():
            if log.attach.call_count == 1:
                return "Dice log attached."
            log.detach.assert_called_once()
            log.close.assert_not_called()
            guest.proc.close.assert_not_called()
            raise KeyboardInterrupt

        log.attach.side_effect = attach
        log.still_patched.return_value = False
        with mock.patch.object(cli, "connect", return_value=guest) as opened, \
                mock.patch.object(launch, "load_settings", return_value={}), \
                mock.patch("dsloader.dicelog.DiceLog", return_value=log), mock.patch("builtins.print"):
            cli._follow_once(argparse.Namespace(raw=False, all=False))
        opened.assert_called_once()
        log.answer_stats_in_background.assert_called_once()
        self.assertEqual(log.attach.call_count, 2)
        log.close.assert_called_once_with(stats_timeout=None)
        guest.proc.close.assert_called_once()

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
