"""ProcessMemory on Linux (/proc/<pid>/mem) once its process has ended: a read or a write no longer
comes back empty without a word (the kernel's answer for a process whose memory is gone), but
raises ProcessError, so the window and the dice log see the game gone (a window attached by
Reconnect said "Connected to the game" on, and its party table failed on the empty reads)."""

import os
import subprocess
import sys
import time
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader.process import ProcessError, ProcessMemory  # noqa: E402


def child_memory(test):
    """A child process (sleep), its ProcessMemory and an address of its own to read."""
    child = subprocess.Popen(["sleep", "60"])
    test.addCleanup(child.wait)
    test.addCleanup(child.kill)
    for _ in range(200):  # (exec'd: its memory sleep's, not a copy of this Python's)
        try:
            if os.path.basename(os.readlink(f"/proc/{child.pid}/exe")).startswith("sleep"):
                break
        except OSError:
            pass
        time.sleep(0.01)
    try:
        proc = ProcessMemory(child.pid)
    except ProcessError as e:
        test.skipTest(f"can't open another process's memory here: {e}")
    test.addCleanup(proc.close)
    return child, proc, next(proc.regions()).start


def ended(proc) -> bool:
    for _ in range(200):
        if not proc.is_alive():
            return True
        time.sleep(0.01)
    return False


@unittest.skipUnless(sys.platform.startswith("linux"), "Linux's /proc/<pid>/mem")
class EndedProcessTests(unittest.TestCase):
    def test_read_and_write_after_the_end_raise(self):
        child, proc, at = child_memory(self)
        data = proc.read(at, 16)
        self.assertEqual(len(data), 16)
        proc.write(at, data)
        self.assertTrue(proc.is_alive())
        child.kill()
        self.assertTrue(ended(proc))  # (ended, not yet reaped: a zombie, its memory gone)
        with self.assertRaisesRegex(ProcessError, "has ended"):
            proc.read(at, 16)
        with self.assertRaisesRegex(ProcessError, "has ended"):
            proc.write(at, data)
        child.wait()  # (reaped: gone from /proc)
        self.assertFalse(proc.is_alive())
        with self.assertRaisesRegex(ProcessError, "has ended"):
            proc.read(at, 4)

    def test_nothing_asked_nothing_raised(self):
        child, proc, at = child_memory(self)
        child.kill()
        child.wait()
        self.assertEqual(proc.read(at, 0), b"")


if __name__ == "__main__":
    unittest.main()
