# dosboxx_memtest.py DOSBOX-X [normal]: can a second program read and write DOSBox-X's memory file while DOSBox-X runs?
#
# WHAT IT IS FOR. Obsidian Edition can run the game in DOSBox-X (the Loader's Options tab, Engine).
# The Loader then follows the game through DOSBox-X's "memory file": a file that IS the emulated
# PC's memory. That was played on Linux only. This script checks the same thing on Windows and on
# macOS, without the game and without the mod: it needs only Python 3.8 or later and DOSBox-X
# 2025.01.01 or later. It changes nothing on the computer but a temporary folder of its own,
# which it removes at the end.
#
# HOW TO RUN IT.
#   Windows:  open a Command Prompt in this script's folder and type
#               py dosboxx_memtest.py "C:\path\to\dosbox-x.exe"
#             (DOSBox-X's portable zip unpacks to a folder holding dosbox-x.exe; an installed one
#             is usually C:\DOSBox-X\dosbox-x.exe)
#   macOS:    open Terminal and type
#               python3 dosboxx_memtest.py /Applications/dosbox-x.app
#             (the app itself, or the program inside it, dosbox-x.app/Contents/MacOS/dosbox-x)
#   Linux:    python3 dosboxx_memtest.py /path/to/dosbox-x
# A DOSBox-X window opens for about half a minute, showing nothing much, and closes by itself:
# leave it alone. Add the word  normal  after the path to run DOSBox-X's normal core instead of
# its dynamic one (the last test, "code", is expected to differ between them).
#
# WHAT TO SEND BACK. Everything it prints, which it also saves as dosboxx_memtest-report.txt in
# the folder you ran it from. The line that matters most is the last, "RESULT:".
#
# WHAT IT DOES. It starts DOSBox-X with a configuration of its own ("memory file=..." in a
# temporary folder) and a 26-byte DOS program that counts for ever and copies one byte ("inbox")
# to another ("outbox"). Then, from outside, through the file:
#   1 found      the file is made, has the size of the PC's memory, and the program is in it
#   2 read       the count is seen going up (the game's memory is read as it changes)
#   3 write      a byte written to "inbox" comes back in "outbox" (the game sees what is written)
#   4 hold       DOSBox-X held still (as the Loader holds the game for a moment to change its
#                item lists), the count stands; let go, it runs again
#   5 code       the counting instruction made "do nothing" and put back: does the count stop?
#                (on a dynamic core old code can run on: known, and the same in DOSBox 0.74)
#   6 the file   whether it can be removed while DOSBox-X runs, and after it has closed
# Each of 2 and 3 is done two ways: reading and writing the file (what the Loader does on Linux
# and macOS), and through a mapping of the file (what it does on Windows, where the first way is
# not promised to agree with DOSBox-X's own mapping). The report says which ways work here.
import mmap, os, re, shutil, signal, struct, subprocess, sys, tempfile, time

PROGRAM = bytes.fromhex("eb0c4f4253494449414e00000000ff060a01a00c01a20d01ebf4")  # (memloop: see WHAT IT DOES)
SIG = b"OBSIDIAN"
COUNT, INBOX, OUTBOX, CODE = 8, 10, 11, 12   # from the signature
INC = bytes.fromhex("ff060a01")              # inc word [count]
MIN_VERSION = (2025, 1, 1)
lines = []


def say(text=""):
    print(text, flush=True)
    lines.append(text)


def version_of(path):
    """DOSBox-X's version: asked of the program (not on Windows, where that waits for a key),
    else read from the program's file."""
    found = None
    if os.name != "nt":
        try:
            out = subprocess.run([path, "-version"], capture_output=True, timeout=20, stdin=subprocess.DEVNULL)
            found = re.search(rb"DOSBox-X version (\d{4})\.(\d\d)\.(\d\d)", out.stdout + out.stderr)
        except (OSError, subprocess.SubprocessError):
            pass
    if not found:
        try:
            with open(path, "rb") as f:
                data = f.read()
            found = (re.search(rb"dosbox-x-(\d{4})\.(\d\d)\.(\d\d)\.conf", data)
                     or re.search(rb"DOSBox-X (\d{4})\.(\d\d)\.(\d\d)", data))
        except OSError:
            pass
    return tuple(int(n) for n in found.groups()) if found else None


class ByFile:
    """Reading and writing the file itself."""
    name = "file read/write"

    def __init__(self, path):
        self.fd = os.open(path, os.O_RDWR | getattr(os, "O_BINARY", 0))

    def read(self, at, size):
        if hasattr(os, "pread"):
            return os.pread(self.fd, size, at)
        os.lseek(self.fd, at, os.SEEK_SET)
        return os.read(self.fd, size)

    def write(self, at, data):
        if hasattr(os, "pwrite"):
            os.pwrite(self.fd, data, at)
        else:
            os.lseek(self.fd, at, os.SEEK_SET)
            os.write(self.fd, data)

    def close(self):
        os.close(self.fd)


class ByMap:
    """Through a mapping of the file."""
    name = "mapping"

    def __init__(self, path):
        self.fd = os.open(path, os.O_RDWR | getattr(os, "O_BINARY", 0))
        self.map = mmap.mmap(self.fd, 0)

    def read(self, at, size):
        return self.map[at:at + size]

    def write(self, at, data):
        self.map[at:at + len(data)] = data

    def close(self):
        self.map.close()
        os.close(self.fd)


def hold(pid):
    """DOSBox-X held still; returns the function that lets it go, or None if it can't be held."""
    if os.name == "nt":
        import ctypes
        from ctypes import wintypes
        k32 = ctypes.WinDLL("kernel32", use_last_error=True)
        k32.OpenProcess.restype = wintypes.HANDLE
        k32.OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
        k32.CloseHandle.argtypes = (wintypes.HANDLE,)
        ntdll = ctypes.WinDLL("ntdll")
        ntdll.NtSuspendProcess.argtypes = (wintypes.HANDLE,)
        ntdll.NtResumeProcess.argtypes = (wintypes.HANDLE,)
        handle = k32.OpenProcess(0x0800, False, pid)  # PROCESS_SUSPEND_RESUME
        if not handle or ntdll.NtSuspendProcess(handle) != 0:
            return None

        def let_go():
            ntdll.NtResumeProcess(handle)
            k32.CloseHandle(handle)
        return let_go
    try:
        os.kill(pid, signal.SIGSTOP)
    except OSError:
        return None
    return lambda: os.kill(pid, signal.SIGCONT)


def main(argv):
    if len(argv) < 2:
        print(__doc__ or "usage: python dosboxx_memtest.py PATH-TO-DOSBOX-X [normal]")
        print("usage: python dosboxx_memtest.py PATH-TO-DOSBOX-X [normal]   (the instructions are at the top of this file)")
        return 2
    program = argv[1]
    if program.rstrip("/").endswith(".app"):  # (macOS: the app; the program is inside it)
        inner = os.path.join(program, "Contents", "MacOS")
        names = [n for n in (os.listdir(inner) if os.path.isdir(inner) else []) if n.lower().startswith("dosbox-x")]
        program = os.path.join(inner, names[0]) if names else program
    core = "normal" if "normal" in argv[2:] else "dynamic"
    say(f"dosboxx_memtest: {sys.platform}, Python {sys.version.split()[0]} ({struct.calcsize('P') * 8}-bit), "
        f"{time.strftime('%Y-%m-%d %H:%M')}")
    say(f"DOSBox-X: {program}")
    if not os.path.isfile(program):
        say("RESULT: no such file. Give the path of the DOSBox-X program.")
        return 2
    found = version_of(program)
    say("its version: " + ("%04d.%02d.%02d" % found if found else "could not be read"))
    if found and found < MIN_VERSION:
        say("RESULT: this DOSBox-X is older than 2025.01.01 and has no memory file. Get a newer one.")
        return 2
    tmp = tempfile.mkdtemp(prefix="dbxmem")
    shm = "/dev/shm" if sys.platform.startswith("linux") and os.access("/dev/shm", os.W_OK) else tmp
    mem = os.path.join(shm, f"dosboxx-memtest-{os.getpid()}.mem")
    say(f"the memory file: {mem}")
    with open(os.path.join(tmp, "MEMLOOP.COM"), "wb") as f:
        f.write(PROGRAM)
    conf = os.path.join(tmp, "memtest.conf")
    with open(conf, "w", newline="\r\n" if os.name == "nt" else "\n") as f:
        f.write(f"""[sdl]
output=surface
showmenu=false
[dosbox]
memsize=16
memory file={mem}
quit warning=false
fastbioslogo=true
startbanner=false
[cpu]
core={core}
cycles=fixed 20000
[dos]
ems=false
umb=true
[config]
dos=umb
[autoexec]
mount c "{tmp}"
c:
memloop.com
""")
    ok = {}
    proc = None
    ways = []
    try:
        log = open(os.path.join(tmp, "dosbox-x.log"), "wb")
        proc = subprocess.Popen([program, "-conf", conf, "-nopromptfolder", "-nomenu", "-fastlaunch"], cwd=tmp,
                                stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT)
        log.close()
        say(f"DOSBox-X started (process {proc.pid}), core={core}")
        # 1 found
        at = -1
        size = 0
        for _ in range(80):
            time.sleep(0.5)
            if proc.poll() is not None:
                break
            try:
                size = os.path.getsize(mem)
                with open(mem, "rb") as f:
                    at = f.read(0x100000).find(SIG)
            except OSError:
                continue
            if at >= 0:
                break
        if at < 0:
            say(f"1 found: NO. The file {'is there, %d bytes' % size if size else 'was not made'}"
                + ("; DOSBox-X closed with code %s" % proc.returncode if proc.poll() is not None else "")
                + ". (An older DOSBox-X ignores \"memory file\".)")
            try:
                with open(os.path.join(tmp, "dosbox-x.log"), "rb") as f:
                    say("DOSBox-X's last lines:\n" + f.read()[-1500:].decode("utf-8", "replace"))
            except OSError:
                pass
            say("RESULT: FAILED at the first step: no memory file with the test program in it.")
            return 1
        say(f"1 found: yes. The file is {size} bytes ({size // (1024 * 1024)} MB), the program at {at:#x}.")
        ok["found"] = size == 16 * 1024 * 1024
        for kind in (ByFile, ByMap):
            try:
                ways.append(kind(mem))
            except (OSError, ValueError) as e:
                say(f"  ({kind.name}: could not be opened: {e})")

        def count(way):
            return struct.unpack("<H", way.read(at + COUNT, 2))[0]

        def runs(way, secs=0.5):
            a = count(way)
            time.sleep(secs)
            return count(way) != a

        # 2 read
        for way in ways:
            ok[f"read by {way.name}"] = runs(way)
            say(f"2 read by {way.name}: " + ("yes, the count is seen going up" if ok[f"read by {way.name}"]
                                             else "NO, the count read does not change"))
        # 3 write
        for n, way in enumerate(ways):
            for m, reader in enumerate(ways):
                value = bytes([0x41 + n * 4 + m])
                way.write(at + INBOX, value)
                time.sleep(0.3)
                got = reader.read(at + OUTBOX, 1)
                key = f"write by {way.name}, read back by {reader.name}"
                ok[key] = got == value
                say(f"3 {key}: " + ("yes" if got == value else f"NO (wrote {value!r}, outbox is {got!r})"))
        way = next((w for w in ways if ok.get(f"read by {w.name}")), None)
        if way is None:
            say("RESULT: FAILED: the memory file is there, but what is read from it does not change.")
            return 1
        # 4 hold
        let_go = hold(proc.pid)
        if let_go is None:
            ok["hold"] = False
            say("4 hold: NO, DOSBox-X could not be held still")
        else:
            time.sleep(0.3)
            stood = not runs(way)
            way.write(at + INBOX, b"H")  # (a write made while it is held is there when it runs again)
            let_go()
            time.sleep(0.3)
            again, landed = runs(way), way.read(at + OUTBOX, 1) == b"H"
            ok["hold"] = stood and again and landed
            say(f"4 hold: held still, the count {'stands' if stood else 'RUNS ON'}; let go, it "
                f"{'runs again' if again else 'DOES NOT RUN'}; a write made meanwhile "
                f"{'is there' if landed else 'IS NOT THERE'}")
        # 5 code
        was = way.read(at + CODE, 4)
        if was != INC:
            say(f"5 code: skipped (the instruction read is {was.hex()}, not {INC.hex()})")
        else:
            way.write(at + CODE, b"\x90" * 4)
            stale = runs(way, 1.0)
            way.write(at + CODE, was)
            back = runs(way, 1.0)
            ok["code (information only)"] = True
            say("5 code: the instruction made \"do nothing\": the count "
                + ("RUNS ON (stale code: expected on a dynamic core, and the same in DOSBox 0.74)" if stale
                   else "stops (the change is acted on at once)")
                + f"; put back, it {'runs' if back else 'does not run'}")
        # 6 the file
        try:
            os.remove(mem)
            removed = True
        except OSError as e:
            removed = False
            why = e
        say("6 the file, while DOSBox-X runs and this script has it open: "
            + ("it could be removed (its name is gone; DOSBox-X keeps its memory)" if removed
               else f"it can't be removed ({why}): expected on Windows"))
    finally:
        for way in ways:
            try:
                way.close()
            except (OSError, ValueError):
                pass
        if proc is not None and proc.poll() is None:
            proc.kill()
        if proc is not None:
            proc.wait()
        left = os.path.exists(mem)
        try:
            if left:
                os.remove(mem)
            say("6 the file, after DOSBox-X closed: " + ("removed" if left else "already gone"))
        except OSError as e:
            say(f"6 the file, after DOSBox-X closed: IT CAN'T BE REMOVED ({e})")
            ok["removed after"] = False
        shutil.rmtree(tmp, ignore_errors=True)
    failed = [key for key, good in ok.items() if not good]
    file_way = all(ok.get(k) for k in ok if "file read/write" in k and "mapping" not in k)
    map_way = all(ok.get(k) for k in ok if "mapping" in k and "file read/write" not in k)
    say()
    say(f"the file read/write way works: {'yes' if file_way else 'NO'}; the mapping way works: {'yes' if map_way else 'NO'}; "
        f"holding DOSBox-X still works: {'yes' if ok.get('hold') else 'NO'}")
    wanted = map_way if os.name == "nt" else file_way  # (the way the Loader uses on this system)
    if wanted and ok.get("hold") and ok.get("found") and "removed after" not in failed:
        say("RESULT: PASSED. A second program reads and writes DOSBox-X's memory through the file here, "
            "the way the Loader does on this system." + (" (Not everything passed: " + "; ".join(failed) + ".)"
                                                         if failed else ""))
        return 0
    say("RESULT: FAILED: " + "; ".join(failed or ["the way the Loader uses on this system"]) + ".")
    return 1


if __name__ == "__main__":
    code = 2
    try:
        code = main(sys.argv)
    except Exception as e:  # (said in the report, not lost in a closing window)
        import traceback
        say("RESULT: the script itself failed: " + repr(e))
        say(traceback.format_exc())
    try:
        with open("dosboxx_memtest-report.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        print("(saved as dosboxx_memtest-report.txt)")
    except OSError:
        pass
    sys.exit(code)
