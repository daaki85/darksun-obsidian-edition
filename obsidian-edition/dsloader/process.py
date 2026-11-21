"""Access to another process's memory.

Windows is the main target (ReadProcessMemory). Linux (/proc/<pid>/mem) is
supported too, mostly so the tool can be developed and tested there.

FileMemory, at the end, is the other way to the game's memory: DOSBox-X's memory
file (dosboxx.py), read and written as a file, with no access to the process at all.
"""

import os
import signal
import sys
import time
from typing import Iterator, List, NamedTuple, Optional, Tuple


STOP_TRIES, STOP_STEP = 50, 0.001  # (Linux: how long a stop is waited for, in steps of seconds)


class ProcessError(Exception):
    pass


class Region(NamedTuple):
    start: int
    size: int

    @property
    def end(self) -> int:
        return self.start + self.size


def find_dosbox_processes() -> List[Tuple[int, str]]:
    """(pid, executable name) for every running process that looks like DOSBox (DOSBox-X among
    them: is_dosbox_x tells which)."""
    return [(pid, name) for pid, name in list_processes()
            if "dosbox" in name.lower() or name.lower().startswith("dsun")]  # (dsun: Dark Sun Recompiled)


def is_dosbox_x(name: str) -> bool:
    """Whether a process's NAME is DOSBox-X's ("dosbox-x", "dosbox-x.exe", "DOSBox-X"), not
    DOSBox 0.74's ("dosbox", "DOSBox.exe")."""
    return name.lower().startswith("dosbox-x")


if sys.platform == "win32":
    import ctypes
    from ctypes import wintypes

    _k32 = ctypes.WinDLL("kernel32", use_last_error=True)

    _PROCESS_QUERY_INFORMATION = 0x0400
    _PROCESS_VM_READ = 0x0010
    _PROCESS_VM_WRITE = 0x0020
    _PROCESS_VM_OPERATION = 0x0008
    _PROCESS_SUSPEND_RESUME = 0x0800
    _MEM_COMMIT = 0x1000
    _PAGE_GUARD = 0x100
    _WRITABLE = 0x04 | 0x08 | 0x40 | 0x80  # READWRITE, WRITECOPY, EXECUTE_READWRITE, EXECUTE_WRITECOPY
    _TH32CS_SNAPPROCESS = 0x2
    _INVALID_HANDLE = ctypes.c_void_p(-1).value

    class _MemoryBasicInformation(ctypes.Structure):
        # ctypes alignment reproduces the padding of the 64-bit layout.
        _fields_ = [
            ("BaseAddress", ctypes.c_void_p),
            ("AllocationBase", ctypes.c_void_p),
            ("AllocationProtect", wintypes.DWORD),
            ("RegionSize", ctypes.c_size_t),
            ("State", wintypes.DWORD),
            ("Protect", wintypes.DWORD),
            ("Type", wintypes.DWORD),
        ]

    class _ProcessEntry32(ctypes.Structure):
        _fields_ = [
            ("dwSize", wintypes.DWORD),
            ("cntUsage", wintypes.DWORD),
            ("th32ProcessID", wintypes.DWORD),
            ("th32DefaultHeapID", ctypes.c_size_t),
            ("th32ModuleID", wintypes.DWORD),
            ("cntThreads", wintypes.DWORD),
            ("th32ParentProcessID", wintypes.DWORD),
            ("pcPriClassBase", ctypes.c_long),
            ("dwFlags", wintypes.DWORD),
            ("szExeFile", ctypes.c_wchar * 260),
        ]

    _k32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    _k32.OpenProcess.restype = wintypes.HANDLE
    _k32.CloseHandle.argtypes = [wintypes.HANDLE]
    _k32.VirtualQueryEx.argtypes = [
        wintypes.HANDLE, wintypes.LPCVOID, ctypes.POINTER(_MemoryBasicInformation), ctypes.c_size_t]
    _k32.VirtualQueryEx.restype = ctypes.c_size_t
    _k32.ReadProcessMemory.argtypes = [
        wintypes.HANDLE, wintypes.LPCVOID, wintypes.LPVOID, ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_size_t)]
    _k32.ReadProcessMemory.restype = wintypes.BOOL
    _k32.WriteProcessMemory.argtypes = [
        wintypes.HANDLE, wintypes.LPVOID, wintypes.LPCVOID, ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_size_t)]
    _k32.WriteProcessMemory.restype = wintypes.BOOL
    _k32.CreateToolhelp32Snapshot.argtypes = [wintypes.DWORD, wintypes.DWORD]
    _k32.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
    _k32.Process32FirstW.argtypes = [wintypes.HANDLE, ctypes.POINTER(_ProcessEntry32)]
    _k32.Process32NextW.argtypes = [wintypes.HANDLE, ctypes.POINTER(_ProcessEntry32)]
    _k32.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]

    def list_processes() -> List[Tuple[int, str]]:
        snap = _k32.CreateToolhelp32Snapshot(_TH32CS_SNAPPROCESS, 0)
        if snap in (None, _INVALID_HANDLE):
            raise ProcessError(f"CreateToolhelp32Snapshot failed ({ctypes.get_last_error()})")
        result = []
        entry = _ProcessEntry32()
        entry.dwSize = ctypes.sizeof(entry)
        try:
            ok = _k32.Process32FirstW(snap, ctypes.byref(entry))
            while ok:
                result.append((entry.th32ProcessID, entry.szExeFile))
                ok = _k32.Process32NextW(snap, ctypes.byref(entry))
        finally:
            _k32.CloseHandle(snap)
        return result

    class ProcessMemory:
        def __init__(self, pid: int):
            self.pid = pid
            self._handle = _k32.OpenProcess(
                _PROCESS_QUERY_INFORMATION | _PROCESS_VM_READ | _PROCESS_VM_WRITE | _PROCESS_VM_OPERATION
                | _PROCESS_SUSPEND_RESUME, False, pid)
            if not self._handle:
                raise ProcessError(
                    f"Cannot open process {pid} (error {ctypes.get_last_error()}). "
                    "Use 64-bit Python for 64-bit DOSBox, and run as the same user.")

        def regions(self) -> Iterator[Region]:
            """Committed, writable, readable regions (where DOSBox keeps guest RAM)."""
            mbi = _MemoryBasicInformation()
            addr = 0
            while _k32.VirtualQueryEx(self._handle, addr, ctypes.byref(mbi), ctypes.sizeof(mbi)):
                base = mbi.BaseAddress or 0
                if (mbi.State == _MEM_COMMIT and mbi.Protect & _WRITABLE
                        and not mbi.Protect & _PAGE_GUARD):
                    yield Region(base, mbi.RegionSize)
                addr = base + mbi.RegionSize
                if addr >= sys.maxsize * 2:
                    break

        def read(self, addr: int, size: int) -> bytes:
            buf = ctypes.create_string_buffer(size)
            done = ctypes.c_size_t(0)
            if not _k32.ReadProcessMemory(self._handle, addr, buf, size, ctypes.byref(done)):
                raise ProcessError(
                    f"ReadProcessMemory at {addr:#x} failed ({ctypes.get_last_error()})")
            return buf.raw[:done.value]

        def write(self, addr: int, data: bytes) -> None:
            done = ctypes.c_size_t(0)
            if not _k32.WriteProcessMemory(self._handle, addr, data, len(data), ctypes.byref(done)) \
                    or done.value != len(data):
                raise ProcessError(
                    f"WriteProcessMemory at {addr:#x} failed ({ctypes.get_last_error()})")

        def suspend(self) -> bool:
            """The process held still (itemgate.py), True if it is."""
            try:
                return ctypes.WinDLL("ntdll").NtSuspendProcess(self._handle) == 0
            except (OSError, AttributeError):
                return False

        def resume(self) -> None:
            try:
                ctypes.WinDLL("ntdll").NtResumeProcess(self._handle)
            except (OSError, AttributeError):
                pass

        def is_alive(self) -> bool:
            code = wintypes.DWORD()
            _k32.GetExitCodeProcess(self._handle, ctypes.byref(code))
            return code.value == 259  # STILL_ACTIVE

        def close(self) -> None:
            if self._handle:
                _k32.CloseHandle(self._handle)
                self._handle = None

else:

    def list_processes() -> List[Tuple[int, str]]:
        result = []
        try:
            entries = os.listdir("/proc")
        except OSError:  # (no /proc, as on macOS: UNTESTED there)
            return _ps_processes()
        for entry in entries:
            if entry.isdigit():
                try:
                    with open(f"/proc/{entry}/comm") as f:
                        result.append((int(entry), f.read().strip()))
                except OSError:
                    pass
        return result or _ps_processes()

    def _ps_processes() -> List[Tuple[int, str]]:
        """The processes as `ps` lists them (a system without /proc: macOS). UNTESTED on macOS."""
        import subprocess
        try:
            out = subprocess.run(["ps", "-axo", "pid=,comm="], capture_output=True, text=True, timeout=10).stdout
        except (OSError, subprocess.SubprocessError):
            return []
        result = []
        for line in out.splitlines():
            pid, _, name = line.strip().partition(" ")
            if pid.isdigit() and name.strip():
                result.append((int(pid), os.path.basename(name.strip())))
        return result

    class ProcessMemory:
        def __init__(self, pid: int):
            self.pid = pid
            try:
                self._mem = open(f"/proc/{pid}/mem", "r+b", buffering=0)
            except OSError as e:
                raise ProcessError(
                    f"Cannot open memory of process {pid}: {e}. "
                    "You may need root, or kernel.yama.ptrace_scope=0.") from e

        def regions(self) -> Iterator[Region]:
            with open(f"/proc/{self.pid}/maps") as f:
                for line in f:
                    addrs, perms = line.split()[:2]
                    if perms.startswith("rw"):
                        start, end = (int(x, 16) for x in addrs.split("-"))
                        yield Region(start, end - start)

        def read(self, addr: int, size: int) -> bytes:
            try:  # (at a position of its own: the dice log's stats thread reads too)
                data = os.pread(self._mem.fileno(), size, addr)
            except (OSError, ValueError, OverflowError) as e:
                raise ProcessError(f"Read at {addr:#x} failed: {e}") from e
            if len(data) < size and not self.is_alive():
                raise ProcessError(f"process {self.pid} has ended")
            return data

        def write(self, addr: int, data: bytes) -> None:
            try:
                done = os.pwrite(self._mem.fileno(), data, addr)
            except (OSError, ValueError, OverflowError) as e:
                raise ProcessError(f"Write at {addr:#x} failed: {e}") from e
            if done < len(data) and not self.is_alive():
                raise ProcessError(f"process {self.pid} has ended")

        def suspend(self) -> bool:
            """The process held still (itemgate.py), True once all its threads have stopped."""
            return stop_process(self.pid)

        def resume(self) -> None:
            os.kill(self.pid, signal.SIGCONT)

        def _stopped(self) -> bool:
            return process_stopped(self.pid)

        def is_alive(self) -> bool:
            """Running still: not gone, and not a zombie (ended, not yet reaped by its parent)."""
            try:
                with open(f"/proc/{self.pid}/stat") as f:
                    return f.read().rsplit(")", 1)[1].split()[0] not in ("Z", "X")
            except (OSError, IndexError):
                return False

        def close(self) -> None:
            self._mem.close()


def stop_process(pid: int) -> bool:
    """Process PID held still with a signal (no access to its memory needed): True once all its
    threads have stopped; if they haven't in time, it is let go again and False. Not Windows."""
    try:
        os.kill(pid, signal.SIGSTOP)
    except OSError:
        return False
    for _ in range(STOP_TRIES):
        if process_stopped(pid):
            return True
        time.sleep(STOP_STEP)
    try:
        os.kill(pid, signal.SIGCONT)
    except OSError:
        pass
    return False


def process_stopped(pid: int) -> bool:
    """Whether every thread of PID has stopped (Linux's /proc; where there is none, as on macOS,
    the stop signal sent is taken as done: UNTESTED there)."""
    if not os.path.isdir("/proc/self"):
        return True
    try:
        for task in os.listdir(f"/proc/{pid}/task"):
            with open(f"/proc/{pid}/task/{task}/stat") as f:
                if f.read().rsplit(")", 1)[1].split()[0] not in ("T", "t"):
                    return False
        return True
    except OSError:
        return False


def process_running(pid: int) -> bool:
    """Whether process PID still runs (one that has ended but not been collected by its parent, a
    zombie, does not)."""
    if pid <= 0:
        return False
    if sys.platform == "win32":
        handle = _k32.OpenProcess(0x1000, False, pid)  # (PROCESS_QUERY_LIMITED_INFORMATION)
        if not handle:
            return ctypes.get_last_error() == 5  # (access denied: there, someone else's)
        try:
            code = wintypes.DWORD()
            return bool(_k32.GetExitCodeProcess(handle, ctypes.byref(code))) and code.value == 259
        finally:
            _k32.CloseHandle(handle)
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except OSError:
        return True  # (someone else's: there)
    try:
        with open(f"/proc/{pid}/stat") as f:
            return f.read().rsplit(")", 1)[1].split()[0] != "Z"
    except (OSError, IndexError):
        return True  # (no /proc: the signal's answer stands)


# DOSBox-X's memory file. DOSBox-X (2025.01.01 and later) can keep the emulated PC's RAM in a file
# ("[dosbox] memory file=PATH", written by dosboxx.py), which it maps shared: what another program
# reads from and writes to the file is the guest's memory, with no access to DOSBox-X's process at
# all (no ptrace right, no root, no task port on macOS, no /proc in a sandbox). FileMemory is that
# file behind ProcessMemory's interface: guest address 0 is the file's offset 0, so
# guestmem.locate() finds it as it finds any region (base 0).
#
# Linux, macOS: the file is read and written with pread and pwrite, not through a mapping of our
# own. DOSBox-X cuts the file to nothing and makes it again each time it starts (ftruncate), and a
# mapping read at that moment would kill the Loader (SIGBUS); a pread then just comes back short.
# The kernel keeps one copy of a file's pages for a mapping and for read/write, so both see the
# same bytes at once (played on Linux; macOS's unified buffer cache does the same: UNTESTED).
#
# Windows (UNTESTED): DOSBox-X opens the file with CreateFile (sharing read and write, not
# delete), sets its size and maps it with CreateFileMapping (no name: the mapping can't be opened
# by name, only the file). Python has no pread there, and Windows doesn't promise that ReadFile and
# WriteFile on a file agree with a mapped view of it; it does promise that views of the same local
# file agree with each other, whichever mapping object they come from. So the Loader maps the file
# too (mmap). While that mapping is held the file can't be cut (SetEndOfFile fails with
# ERROR_USER_MAPPED_FILE), so a DOSBox-X started again would get no memory file: the Loader lets
# the mapping go when the game ends (close), and removes the file before each start.
MEMORY_FILE_ENV = "DSLOADER_MEMORY_FILE"  # the file's path: the Loader then uses it, not a process (the playtest kit's)
MEMORY_PID_ENV = "DSLOADER_MEMORY_PID"    # DOSBox-X's pid, if known: to hold it still (itemgate.py) and see it close
ALIVE_EVERY = 0.1  # seconds between the fuller looks at whether DOSBox-X still runs (a file reads on after it has gone)


def memory_file() -> str:
    """The memory file the Loader is told to use by its environment, or ""."""
    return os.environ.get(MEMORY_FILE_ENV, "")


def _pread(fd: int, size: int, addr: int) -> bytes:
    """os.pread where there is one; else (Windows, which maps the file instead) a seek and a read."""
    if hasattr(os, "pread"):
        return os.pread(fd, size, addr)
    os.lseek(fd, addr, os.SEEK_SET)
    return os.read(fd, size)


def _pwrite(fd: int, data: bytes, addr: int) -> None:
    """os.pwrite where there is one; else a seek and a write."""
    if hasattr(os, "pwrite"):
        os.pwrite(fd, data, addr)
        return
    os.lseek(fd, addr, os.SEEK_SET)
    os.write(fd, data)


class FileMemory:
    """DOSBox-X's memory file PATH as the game's memory; PID is DOSBox-X's process, if known (0:
    not known), used only to hold the game still for the item gate and to tell when it has closed.
    MAPPED: through a mapping of the file (Windows' way) rather than pread and pwrite."""

    by_file = True  # (not another process's memory: the Loader's status line says which)

    def __init__(self, path: str, pid: int = 0, mapped: Optional[bool] = None):
        self.path = path
        self.pid = pid or int(os.environ.get(MEMORY_PID_ENV, "0") or 0)
        self._map = None
        self._handle = None  # (Windows: the process, for suspend)
        self._checked = 0.0
        self._fd: Optional[int] = None
        try:
            self._fd = os.open(path, os.O_RDWR | getattr(os, "O_BINARY", 0))
        except OSError as e:
            raise ProcessError(
                f"DOSBox-X's memory file isn't there ({path}: {e.strerror or e}). DOSBox-X makes it as it "
                "starts; one older than 2025.01.01 never does.") from e
        if (sys.platform == "win32") if mapped is None else mapped:
            import mmap
            try:
                self._map = mmap.mmap(self._fd, 0)
            except (OSError, ValueError) as e:  # (an empty file: DOSBox-X hasn't sized it yet)
                self.close()
                raise ProcessError(f"DOSBox-X's memory file can't be mapped yet ({path}: {e})") from e

    def _size(self) -> int:
        if self._map is not None:
            return len(self._map)
        return os.fstat(self._fd).st_size

    def regions(self) -> Iterator[Region]:
        size = self._size()
        if size:
            yield Region(0, size)

    def _check_alive(self) -> None:
        """DOSBox-X gone (the file would read on, unchanged, for ever): a ProcessError, as a read of
        a closed process's memory is."""
        if not self.pid:
            return
        if sys.platform != "win32":  # (asked at every read: a signal that sends nothing, a microsecond)
            try:
                os.kill(self.pid, 0)
            except ProcessLookupError:
                raise ProcessError(f"DOSBox-X (process {self.pid}) has closed") from None
            except OSError:
                pass  # (someone else's: there)
        now = time.monotonic()
        if now - self._checked < ALIVE_EVERY:
            return
        self._checked = now
        if not process_running(self.pid):  # (ended and not yet collected by its parent, too; Windows' whole check)
            raise ProcessError(f"DOSBox-X (process {self.pid}) has closed")

    def read(self, addr: int, size: int) -> bytes:
        self._check_alive()
        try:
            if self._map is not None:
                data = self._map[addr:addr + size]
            else:
                data = _pread(self._fd, size, addr)
        except (OSError, ValueError, OverflowError, TypeError) as e:
            raise ProcessError(f"Read at {addr:#x} failed: {e}") from e
        if len(data) != size:  # (the file cut: DOSBox-X starting again)
            raise ProcessError(f"Read at {addr:#x} came back short: the memory file is being made again")
        return data

    def write(self, addr: int, data: bytes) -> None:
        self._check_alive()
        try:
            if addr < 0 or addr + len(data) > self._size():  # (never make the file longer)
                raise ProcessError(f"Write at {addr:#x} is past the memory file's end")
            if self._map is not None:
                self._map[addr:addr + len(data)] = data
            else:
                _pwrite(self._fd, data, addr)
        except (OSError, ValueError, OverflowError, TypeError) as e:
            raise ProcessError(f"Write at {addr:#x} failed: {e}") from e

    def suspend(self) -> bool:
        """DOSBox-X held still (itemgate.py), if its pid is known: by a signal, or on Windows
        NtSuspendProcess; neither needs its memory. The file takes writes all the same."""
        if not self.pid:
            return False
        if sys.platform == "win32":
            try:
                if not self._handle:
                    self._handle = _k32.OpenProcess(_PROCESS_SUSPEND_RESUME, False, self.pid)
                return bool(self._handle) and ctypes.WinDLL("ntdll").NtSuspendProcess(self._handle) == 0
            except (OSError, AttributeError):
                return False
        return stop_process(self.pid)

    def resume(self) -> None:
        if not self.pid:
            return
        if sys.platform == "win32":
            try:
                if self._handle:
                    ctypes.WinDLL("ntdll").NtResumeProcess(self._handle)
            except (OSError, AttributeError):
                pass
            return
        try:
            os.kill(self.pid, signal.SIGCONT)
        except OSError:
            pass

    def is_alive(self) -> bool:
        return process_running(self.pid) if self.pid else os.path.exists(self.path)

    def close(self) -> None:
        if self._map is not None:
            try:
                self._map.close()
            except (OSError, ValueError):
                pass
            self._map = None
        if self._fd is not None:
            try:
                os.close(self._fd)
            except OSError:
                pass
            self._fd = None
        if self._handle and sys.platform == "win32":
            _k32.CloseHandle(self._handle)
            self._handle = None
