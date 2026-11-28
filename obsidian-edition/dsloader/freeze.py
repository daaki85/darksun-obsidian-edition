"""The freeze report: what the Loader can see of a game that has stopped while DOSBox runs on.

DSCLOG notes where the game was as its timer struck (PROBE_TICK: TICKS, in its tail at the header's
+356, a record of TICK_SIZE bytes for every 32 strikes, counted at +358). The report gives those places,
newest first, with what is at each now (the game's code, or DSCLOG's own), whether the timer and
the map's main loop still run, DSCLOG's header, the switches and the dice log's and dialogue's
last lines; and keeps all of the emulated PC's memory below 1 MB + 64 KB beside it, to read the
game's state from afterwards. Everything goes in one zip in crash-logs/.

Wake of the Ravager's helper, DSCLOG2, keeps TICKS the same way at the same header fields; its header's
signature (SEQUEL_SIG) tells the report the sequel's DS (ravager.DGROUP) and its program's header
(SEQUEL_EXE_HEADER), and its memory block is DSUNLOG2.
"""

import os
import re
import struct
import time
import zipfile
from collections import Counter
from typing import Callable, Dict, List, NamedTuple, Optional

from . import game
from .dicelog import HDR_SIG

TSR_HDR_OFF = 20  # DSCLOG's header: where it is in DSCLOG's segment
TSR_MAIN_TICKS = 260  # the map's main loop run (counted)
TSR_TICK_OFF, TSR_TICK_SEQ = 356, 358  # TICKS's offset (in the tail); records taken (counted)
TSR_TAIL_SEG = 1834  # the tail's segment (TAIL_SEG: TICKS's)
TICK_SLOTS, TICK_SIZE = 16, 16
HEADER_BYTES = 374  # DSCLOG's header, as it was, in the report (to UMB_NEED, +372: the overlay buffer's place at +368)
EXE_HEADER = 0x5400  # DSUN.EXE's header: a load-segment address + this is its place in the file
SEQUEL_SIG = b"DSCLOGR1"  # DSCLOG2's header (Wake of the Ravager)
SEQUEL_EXE_HEADER = 0x5200  # the sequel's DSUN.EXE's header
SEQUEL_DGROUP = 0x47E0  # the sequel's DS less its load segment (ravager.DGROUP)
CODE_BYTES = 24  # what is at each place now
WATCH_SECONDS = 1.0  # how long the report watches the counters for moving
BIOS_SEG = 0xF000


class Tick(NamedTuple):
    ip: int
    cs: int
    flags: int
    ss: int
    sp: int
    bp: int
    ds: int
    es: int


def ticks(read: Callable[[int, int], bytes], hdr: int) -> List[Tick]:
    """DSCLOG's records of where the game was, oldest first (at most TICK_SLOTS)."""
    base = struct.unpack("<H", read(hdr + TSR_TAIL_SEG, 2))[0] * 16
    off, seq = struct.unpack("<HH", read(hdr + TSR_TICK_OFF, 4))
    raw = read(base + off, TICK_SLOTS * TICK_SIZE)
    taken = min(seq, TICK_SLOTS)
    if taken < TICK_SLOTS and any(raw[taken * TICK_SIZE:]):  # (the count wrapped past 65535: every slot's
        taken = TICK_SLOTS                                    #   been written, the newest at seq - 1)
    return [Tick(*struct.unpack_from("<8H", raw, ((seq - taken + k) % TICK_SLOTS) * TICK_SIZE))
            for k in range(taken)]


def place(cs: int, ip: int, tsr_seg: Optional[int], load_seg: Optional[int], sequel: bool = False) -> str:
    """Whose code CS:IP is: DSCLOG's (DSCLOG2's in the SEQUEL), the BIOS's, or the game's (its place in
    DSUN.EXE, which an overlay's code doesn't have)."""
    if tsr_seg is not None and cs == tsr_seg:
        return f"{helper_name(sequel)} +{ip:04X}"
    if cs >= BIOS_SEG:
        return "the BIOS"
    if load_seg is not None and cs >= load_seg:
        header = SEQUEL_EXE_HEADER if sequel else EXE_HEADER
        return f"game {cs - load_seg:04X}:{ip:04X} (DSUN.EXE {(cs - load_seg) * 16 + ip + header:X}h, unless an overlay)"
    return "below the game (DOS or a driver)"


def helper_name(sequel: bool) -> str:
    return "DSCLOG2" if sequel else "DSCLOG"


def is_sequel(read: Callable[[int, int], bytes], hdr: int) -> bool:
    """HDR is DSCLOG2's header (Wake of the Ravager's helper)."""
    return read(hdr, len(SEQUEL_SIG)) == SEQUEL_SIG


def summary(found: List[Tick], tsr_seg: Optional[int], load_seg: Optional[int], sequel: bool = False) -> List[str]:
    """A line or two on where the game spent its last strikes."""
    if not found:
        return [f"{helper_name(sequel)} has noted nothing yet (the game's timer hasn't struck since it started)."]
    last = found[-8:]
    where = Counter((t.cs, t.ip) for t in last)
    (cs, ip), n = where.most_common(1)[0]
    segs = Counter(t.cs for t in last)
    lines = []
    if n == len(last) and len(last) > 1:
        lines.append(f"The last {n} notes are all at {cs:04X}:{ip:04X}: {place(cs, ip, tsr_seg, load_seg, sequel)}.")
    elif len(segs) == 1:
        span = (min(t.ip for t in last), max(t.ip for t in last))
        lines.append(f"The last {len(last)} notes are all in segment {cs:04X}, {span[0]:04X} to {span[1]:04X}: "
                     f"{place(cs, span[0], tsr_seg, load_seg, sequel)}.")
    else:
        lines.append("The last notes are spread over " + ", ".join(f"{s:04X}" for s in segs) + ".")
    return lines


def _watch(read: Callable[[int, int], bytes], hdr: int, seconds: float) -> Dict[str, int]:
    """How much the timer's strikes noted and the map's main loop moved in SECONDS."""
    def now():
        seq, = struct.unpack("<H", read(hdr + TSR_TICK_SEQ, 2))
        main, = struct.unpack("<H", read(hdr + TSR_MAIN_TICKS, 2))
        return seq, main
    first = now()
    time.sleep(seconds)
    second = now()
    return {"tick": (second[0] - first[0]) & 0xFFFF, "main": (second[1] - first[1]) & 0xFFFF}


def report_text(read: Callable[[int, int], bytes], hdr: Optional[int], ds: Optional[int], stamp: str,
                version: str, switches: Dict[str, object], dice: str, dialogue: str,
                moved: Optional[Dict[str, int]]) -> str:
    """The report's text (READ the guest's memory; HDR DSCLOG's header's address, DS the game's
    data segment, either None when not found)."""
    lines = [f"Obsidian Edition freeze report, {stamp}", f"Loader {version}", ""]
    sequel = hdr is not None and is_sequel(read, hdr)
    if sequel:
        lines[-1:] = ["Wake of the Ravager", ""]
    load_seg = (ds - (SEQUEL_DGROUP if sequel else game.DGROUP) if ds is not None
                else load_from_block(read(0, 0xA0000)))
    if hdr is None:
        lines.append("DSCLOG wasn't found in memory, so where the game was isn't known.")
    else:
        name = helper_name(sequel)
        tsr_seg = (hdr - struct.unpack("<H", read(hdr + TSR_HDR_OFF, 2))[0]) // 16
        lines.append(f"{name}'s segment {tsr_seg:04X}; the game's load segment "
                     + (f"{load_seg:04X}, DS {ds:04X}" if ds is not None else
                        f"{load_seg:04X} (from its memory block: its DS not found)" if load_seg is not None else "not found"))
        if moved is not None:
            lines.append(f"In {WATCH_SECONDS:g} s the timer was noted {moved['tick']} times "
                         f"(0: the game's timer isn't striking) and the map's main loop ran {moved['main']} times.")
        found = ticks(read, hdr)
        lines += [""] + summary(found, tsr_seg, load_seg, sequel)
        lines += ["", "Where the game was as its timer struck, newest first (every 32nd strike):",
                  "  CS:IP      flags SS:SP      BP   DS   ES    whose"]
        for t in reversed(found):
            lines.append(f"  {t.cs:04X}:{t.ip:04X}  {t.flags:04X}  {t.ss:04X}:{t.sp:04X}  {t.bp:04X} {t.ds:04X} "
                         f"{t.es:04X}  {place(t.cs, t.ip, tsr_seg, load_seg, sequel)}")
        lines += ["", "The code at each place now:"]
        for cs, ip in dict.fromkeys((t.cs, t.ip) for t in reversed(found)):
            lines.append(f"  {cs:04X}:{ip:04X}  {read(cs * 16 + ip, CODE_BYTES).hex(' ')}")
        if found:
            t = found[-1]
            lines += ["", f"The newest stack (SS:SP {t.ss:04X}:{t.sp:04X}), 64 words:"]
            words = struct.unpack("<64H", read(t.ss * 16 + t.sp, 128))
            for k in range(0, 64, 16):
                lines.append("  " + " ".join(f"{w:04X}" for w in words[k:k + 16]))
        lines += ["", f"{name}'s header ({HEADER_BYTES} bytes):"]
        head = read(hdr, HEADER_BYTES)
        for k in range(0, HEADER_BYTES, 24):
            lines.append(f"  +{k:<3d} {head[k:k + 24].hex(' ')}")
    lines += ["", "Switches (as set on the Options tab, else the default):"]
    lines += [f"  {key}: {value!r}" for key, value in sorted(switches.items())]
    lines += ["", "The dice log's last lines:", _last_lines(dice, 300),
              "", "The dialogue's last lines:", _last_lines(dialogue, 80), ""]
    return "\n".join(lines)


def _last_lines(text: str, count: int) -> str:
    return "\n".join(text.rstrip().splitlines()[-count:]) or "(empty)"


KEEP_REPORTS = 20  # the freeze reports kept in crash-logs (about 1 MB each): the newest, the rest removed


def write_report(folder: str, now: float, text: str, memory: bytes) -> str:
    """Save the report and the memory as crash-logs/freeze-YYYY-MM-DD-HHMMSS.zip (a number after
    it if there is one already), the older ones past KEEP_REPORTS removed (prune); returns its path."""
    os.makedirs(folder, exist_ok=True)
    stem = os.path.join(folder, time.strftime("freeze-%Y-%m-%d-%H%M%S", time.localtime(now)))
    path, n = stem + ".zip", 1
    while os.path.exists(path):
        n += 1
        path = f"{stem}-{n}.zip"
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("freeze-report.txt", text)
        z.writestr("memory.bin", memory)
    prune(folder, path)
    return path


def prune(folder: str, kept: str, keep: int = KEEP_REPORTS) -> None:
    """The freeze reports in FOLDER past the newest KEEP removed (by time written, then name; KEPT,
    the one just written, never). Only the Loader's own freeze-*.zip: the crash reports' text, a
    few KB each, and anything else there left alone. One that can't be removed (held open): left."""
    def when(name: str):
        try:
            return os.path.getmtime(os.path.join(folder, name)), name
        except OSError:
            return 0.0, name
    names = [n for n in os.listdir(folder) if n.startswith("freeze-") and n.endswith(".zip")
             and os.path.join(folder, n) != kept]
    for name in sorted(names, key=when, reverse=True)[max(0, keep - 1):]:
        try:
            os.remove(os.path.join(folder, name))
        except OSError:
            pass


def freeze_report(read: Callable[[int, int], bytes], hdr: Optional[int], ds: Optional[int], version: str,
                  switches: Dict[str, object], dice: str, dialogue: str, folder: str) -> str:
    """Watch the counters a moment, write the report and the memory; returns the zip's path."""
    now = time.time()
    memory = read(0, game.CONVENTIONAL_AND_UPPER)
    if hdr is None:  # (the dice log no longer attached: the game's memory overwritten, say, its DS lost)
        hdr = find_header(memory)
    moved = _watch(read, hdr, WATCH_SECONDS) if hdr is not None else None
    text = report_text(read, hdr, ds, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(now)), version,
                       switches, dice, dialogue, moved)
    return write_report(folder, now, text, memory)


def load_from_block(memory: bytes) -> Optional[int]:
    """The game's load segment from its DOS memory block (named DSUNLOG, the sequel's DSUNLOG2: the PSP's
    256 bytes, then the program), for when its DS can't be found (overwritten)."""
    found = next((m.start() for m in re.finditer(rb"DSUNLOG(\0|2)", memory) if m.start() % 16 == 8), None)
    return None if found is None else (found - 8) // 16 + 1 + 0x10


def find_header(memory: bytes) -> Optional[int]:
    """DSCLOG's header in MEMORY (conventional and upper), by its signature on a paragraph (DSCLOG2's,
    SEQUEL_SIG, for the sequel)."""
    sigs = re.escape(HDR_SIG) + b"|" + re.escape(SEQUEL_SIG)
    return next((m.start() for m in re.finditer(sigs, memory) if m.start() % 16 == 0), None)
