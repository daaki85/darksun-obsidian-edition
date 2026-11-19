"""DOSBox-X's memory file behind the Loader's memory access (process.FileMemory): found as guest
memory from its start, read and written in place, never made longer, a cut file and a closed
DOSBox-X told as a ProcessError; the mapped way (Windows') the same; and connect's choice of it."""

import argparse
import os
import subprocess
import sys
import tempfile
import time
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import __main__ as cli  # noqa: E402
from dsloader import launch, process  # noqa: E402
from dsloader.guestmem import BIOS_DATE, BIOS_DATE_ADDR, GuestMemoryError, locate  # noqa: E402
from dsloader.process import FileMemory, ProcessError  # noqa: E402

SIZE = 2 * 1024 * 1024


def guest_ram() -> bytearray:
    ram = bytearray(SIZE)
    ram[BIOS_DATE_ADDR:BIOS_DATE_ADDR + len(BIOS_DATE)] = BIOS_DATE
    for vector in range(32):  # (the interrupt table: most vectors in the BIOS's segment)
        ram[vector * 4 + 2:vector * 4 + 4] = (0xF000).to_bytes(2, "little")
    return ram


class FileMemoryTests(unittest.TestCase):
    mapped = False

    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)
        self.path = os.path.join(self.dir.name, "guest.mem")
        with open(self.path, "wb") as f:
            f.write(guest_ram())

    def memory(self, pid: int = 0) -> FileMemory:
        proc = FileMemory(self.path, pid, mapped=self.mapped)
        self.addCleanup(proc.close)
        return proc

    def test_locate_finds_the_file_as_guest_memory_from_its_start(self):
        guest = locate(self.memory())
        self.assertEqual((guest.base, guest.size), (0, SIZE))
        self.assertEqual(guest.read(BIOS_DATE_ADDR, 8), BIOS_DATE)

    def test_a_write_is_in_the_file_for_another_reader(self):
        guest = locate(self.memory())
        guest.write(0x12345, b"\x90\x90")
        other = FileMemory(self.path)  # (another open of it, as DOSBox-X's mapping is)
        self.addCleanup(other.close)
        self.assertEqual(other.read(0x12345, 2), b"\x90\x90")

    def test_another_writers_change_is_read(self):
        proc = self.memory()
        self.assertEqual(proc.read(0x2000, 4), b"\0\0\0\0")
        with open(self.path, "r+b") as f:
            f.seek(0x2000)
            f.write(b"DSUN")
        self.assertEqual(proc.read(0x2000, 4), b"DSUN")

    def test_a_write_never_makes_the_file_longer(self):
        proc = self.memory()
        with self.assertRaises(ProcessError):
            proc.write(SIZE - 1, b"\x00\x00")
        with self.assertRaises(ProcessError):
            proc.write(-1, b"\x00")
        self.assertEqual(os.path.getsize(self.path), SIZE)

    def test_a_read_past_the_end_is_a_process_error(self):
        with self.assertRaises(ProcessError):
            self.memory().read(SIZE - 2, 8)

    def test_no_file_is_a_process_error_that_says_why(self):
        with self.assertRaises(ProcessError) as raised:
            FileMemory(os.path.join(self.dir.name, "none.mem"), mapped=self.mapped)
        self.assertIn("2025.01.01", str(raised.exception))

    def test_a_closed_dosbox_x_is_a_process_error_though_the_file_reads_on(self):
        """The file stays readable for ever: a read says DOSBox-X has gone once its process has."""
        child = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"])
        self.addCleanup(child.wait)
        self.addCleanup(child.kill)
        proc = self.memory(child.pid)
        self.assertEqual(proc.read(BIOS_DATE_ADDR, 8), BIOS_DATE)
        self.assertTrue(proc.is_alive())
        child.kill()
        child.wait()
        proc._checked = 0.0  # (looked at every ALIVE_EVERY seconds: now)
        with self.assertRaises(ProcessError) as raised:
            proc.read(BIOS_DATE_ADDR, 8)
        self.assertIn("has closed", str(raised.exception))
        self.assertFalse(proc.is_alive())

    def test_the_process_is_asked_about_only_now_and_then(self):
        asked = []
        saved = process.process_running
        self.addCleanup(lambda: setattr(process, "process_running", saved))
        process.process_running = lambda pid: asked.append(pid) or True
        proc = self.memory(4242)
        for _ in range(50):
            proc.read(0, 4)
        self.assertEqual(asked, [4242])

    @unittest.skipIf(sys.platform == "win32", "a signal: not Windows")
    def test_suspend_and_resume_are_the_process_by_its_pid(self):
        child = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"])
        self.addCleanup(child.wait)
        self.addCleanup(child.kill)
        proc = self.memory(child.pid)
        self.assertTrue(proc.suspend())
        if os.path.isdir("/proc/self"):
            with open(f"/proc/{child.pid}/stat") as f:
                self.assertIn(f.read().rsplit(")", 1)[1].split()[0], ("T", "t"))
        proc.write(0x3000, b"held")  # (the file takes the write with the game held still)
        self.assertEqual(proc.read(0x3000, 4), b"held")
        proc.resume()
        if os.path.isdir("/proc/self"):
            for _ in range(100):
                with open(f"/proc/{child.pid}/stat") as f:
                    if f.read().rsplit(")", 1)[1].split()[0] not in ("T", "t"):
                        break
                time.sleep(0.01)
            else:
                self.fail("not resumed")

    def test_without_a_pid_nothing_is_held_still(self):
        proc = self.memory()
        self.assertFalse(proc.suspend())
        proc.resume()
        self.assertTrue(proc.is_alive())


class PreadTests(FileMemoryTests):
    def test_a_file_cut_to_nothing_is_a_process_error_and_no_guest_memory(self):
        """DOSBox-X cuts the file to nothing and makes it again as it starts: read then, it is a
        ProcessError (the Loader waits and tries again), never a crash."""
        proc = self.memory()
        os.truncate(self.path, 0)
        with self.assertRaises(ProcessError):
            proc.read(BIOS_DATE_ADDR, 8)
        self.assertEqual(list(proc.regions()), [])
        with self.assertRaises(GuestMemoryError):
            locate(proc)


class MappedTests(FileMemoryTests):
    """Windows' way (a mapping of the file), run wherever the tests run."""
    mapped = True

    def test_an_empty_file_cant_be_mapped_yet(self):
        empty = os.path.join(self.dir.name, "empty.mem")
        open(empty, "wb").close()
        with self.assertRaises(ProcessError):
            FileMemory(empty, mapped=True)


del FileMemoryTests  # (the two ways run it; not by itself)


class ProcessHelperTests(unittest.TestCase):
    def test_dosbox_x_is_told_from_dosbox(self):
        for name in ("dosbox-x", "DOSBox-X.exe", "dosbox-x.exe", "dosbox-x-sdl1"):
            self.assertTrue(process.is_dosbox_x(name), name)
        for name in ("dosbox", "DOSBox.exe", "dsun", "dosbox_x_helper", "db74"):
            self.assertFalse(process.is_dosbox_x(name), name)

    def test_both_are_found_as_dosbox_processes(self):
        saved = process.list_processes
        self.addCleanup(lambda: setattr(process, "list_processes", saved))
        process.list_processes = lambda: [(1, "init"), (10, "dosbox"), (11, "dosbox-x"), (12, "dsun"), (13, "python3")]
        self.assertEqual(process.find_dosbox_processes(), [(10, "dosbox"), (11, "dosbox-x"), (12, "dsun")])

    def test_process_running(self):
        self.assertTrue(process.process_running(os.getpid()))
        self.assertFalse(process.process_running(0))
        child = subprocess.Popen([sys.executable, "-c", "pass"])
        child.wait()
        self.assertFalse(process.process_running(child.pid))

    @unittest.skipUnless(os.path.isdir("/proc/self"), "needs /proc")
    def test_an_ended_process_not_yet_collected_does_not_run(self):
        child = subprocess.Popen([sys.executable, "-c", "pass"])
        for _ in range(200):  # (ended, and still there: a zombie until wait())
            with open(f"/proc/{child.pid}/stat") as f:
                if f.read().rsplit(")", 1)[1].split()[0] == "Z":
                    break
            time.sleep(0.01)
        self.assertFalse(process.process_running(child.pid))
        child.wait()


class ConnectTests(unittest.TestCase):
    """dsloader's connect: which DOSBox, and through its process or its memory file."""

    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)
        self.path = os.path.join(self.dir.name, "guest.mem")
        with open(self.path, "wb") as f:
            f.write(guest_ram())
        saved = {(mod, name): getattr(mod, name) for mod, name in (
            (cli, "find_dosbox_processes"), (cli, "_located"), (launch, "memory_game"),
            (launch, "game_memory_file"), (launch, "load_settings"))}
        self.addCleanup(lambda: [setattr(mod, name, value) for (mod, name), value in saved.items()])
        env = os.environ.pop(process.MEMORY_FILE_ENV, None)
        self.addCleanup(lambda: env is not None and os.environ.__setitem__(process.MEMORY_FILE_ENV, env))
        self.addCleanup(lambda: os.environ.pop(process.MEMORY_FILE_ENV, None))
        self.settings = {}
        launch.load_settings = lambda *a, **k: dict(self.settings)
        launch.memory_game = lambda *a: (0, "")
        launch.game_memory_file = lambda pid: ""
        cli._located = lambda pid, host_base=None: ("process", pid)
        self.found = []
        cli.find_dosbox_processes = lambda: list(self.found)

    def connect(self, pid=None, started=None):
        guest = cli.connect(argparse.Namespace(pid=pid, host_base=None), started)
        if not isinstance(guest, tuple):
            self.addCleanup(guest.proc.close)
        return guest

    def test_the_only_dosbox_is_read_from_its_process(self):
        self.found = [(10, "dosbox")]
        self.assertEqual(self.connect(), ("process", 10))

    def test_no_dosbox_is_said(self):
        with self.assertRaises(cli.CliError):
            self.connect()

    def test_a_dosbox_x_beside_a_dosbox_is_not_taken_for_it(self):
        self.found = [(10, "dosbox"), (11, "dosbox-x")]
        self.assertEqual(self.connect(), ("process", 10))  # (GOG's engine: the 0.74)
        self.settings = {"engine": "dosbox-x"}
        launch.game_memory_file = lambda pid: self.path if pid == 11 else ""
        guest = self.connect()
        self.assertIsInstance(guest.proc, FileMemory)
        self.assertEqual((guest.proc.pid, guest.proc.path), (11, self.path))

    def test_two_of_a_kind_are_said_not_guessed(self):
        self.found = [(10, "dosbox"), (12, "dosbox")]
        with self.assertRaises(cli.CliError) as raised:
            self.connect()
        self.assertIn("--pid", str(raised.exception))
        self.settings = {"engine": "dosbox-x"}  # (no DOSBox-X among them: no telling either)
        with self.assertRaises(cli.CliError):
            self.connect()

    def test_the_game_this_loader_started_is_read_through_its_memory_file(self):
        self.found = [(10, "dosbox"), (11, "dosbox-x"), (14, "dosbox-x")]
        launch.game_memory_file = lambda pid: self.path if pid == 14 else ""
        guest = self.connect(started=14)
        self.assertEqual((type(guest.proc), guest.proc.pid), (FileMemory, 14))
        self.assertEqual(self.connect(started=10), ("process", 10))
        self.assertEqual(self.connect(pid=10, started=14), ("process", 10))  # (--pid first)

    def test_a_dosbox_x_game_started_from_this_folder_earlier_is_found_again(self):
        """The Loader closed and opened again while the game ran on: no pid given, the lock
        file's game and its memory file are the game (launch.memory_game)."""
        self.found = [(10, "dosbox"), (11, "dosbox-x")]
        launch.memory_game = lambda *a: (11, self.path)
        guest = self.connect()
        self.assertEqual((type(guest.proc), guest.proc.pid), (FileMemory, 11))

    def test_the_environments_memory_file_is_used_outright(self):
        os.environ[process.MEMORY_FILE_ENV] = self.path
        guest = self.connect(pid=77)
        self.assertEqual((type(guest.proc), guest.proc.pid, guest.proc.path), (FileMemory, 77, self.path))

    def test_a_memory_file_not_there_yet_is_a_process_error(self):
        launch.game_memory_file = lambda pid: os.path.join(self.dir.name, "later.mem")
        with self.assertRaises(ProcessError):
            self.connect(started=14)


if __name__ == "__main__":
    unittest.main()
