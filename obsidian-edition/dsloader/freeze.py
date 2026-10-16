"""The freeze report: what the Loader can see of a game that has stopped while DOSBox runs on.

DSCLOG notes where the game was as its timer struck (PROBE_TICK: TICKS, the header's +356, a
record of TICK_SIZE bytes for every 16 strikes, counted at +358). The report gives those places,
newest first, with what is at each now (the game's code, or DSCLOG's own), whether the timer and
the map's main loop still run, DSCLOG's header, the switches and the dice log's and dialogue's
last lines; and keeps all of the emulated PC's memory below 1 MB + 64 KB beside it, to read the
game's state from afterwards. Everything goes in one zip in crash-logs/.
"""

import os
import struct
import time
import zipfile
from collections import Counter
from typing import Callable, Dict, List, NamedTuple, Optional

from . import game

TSR_HDR_OFF = 20  # DSCLOG's header: where it is in DSCLOG's segment
TSR_MAIN_TICKS = 260  # the map's main loop run (counted)
TSR_TICK_OFF, TSR_TICK_SEQ = 356, 358  # TICKS's offset; records taken (counted)
TICK_SLOTS, TICK_SIZE = 32, 16
HEADER_BYTES = 362  # DSCLOG's header, as it was, in the report (to KIT_POISONED and its spare byte)
EXE_HEADER = 0x5400  # DSUN.EXE's header: a load-segment address + this is its place in the file
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
    base = hdr - struct.unpack("<H", read(hdr + TSR_HDR_OFF, 2))[0]
    off, seq = struct.unpack("<HH", read(hdr + TSR_TICK_OFF, 4))
    raw = read(base + off, TICK_SLOTS * TICK_SIZE)
    taken = min(seq, TICK_SLOTS)
    return [Tick(*struct.unpack_from("<8H", raw, ((seq - taken + k) % TICK_SLOTS) * TICK_SIZE))
            for k in range(taken)]


def place(cs: int, ip: int, tsr_seg: Optional[int], load_seg: Optional[int]) -> str:
    """Whose code CS:IP is: DSCLOG's, the BIOS's, or the game's (its place in DSUN.EXE, which an
    overlay's code doesn't have)."""
    if tsr_seg is not None and cs == tsr_seg:
        return f"DSCLOG +{ip:04X}"
    if cs >= BIOS_SEG:
        return "the BIOS"
    if load_seg is not None and cs >= load_seg:
        return f"game {cs - load_seg:04X}:{ip:04X} (DSUN.EXE {(cs - load_seg) * 16 + ip + EXE_HEADER:X}h, unless an overlay)"
    return "below the game (DOS or a driver)"


def summary(found: List[Tick], tsr_seg: Optional[int], load_seg: Optional[int]) -> List[str]:
    """A line or two on where the game spent its last strikes."""
    if not found:
        return ["DSCLOG has noted nothing yet (the game's timer hasn't struck since it started)."]
    last = found[-8:]
    where = Counter((t.cs, t.ip) for t in last)
    (cs, ip), n = where.most_common(1)[0]
    segs = Counter(t.cs for t in last)
    lines = []
    if n == len(last) and len(last) > 1:
        lines.append(f"The last {n} notes are all at {cs:04X}:{ip:04X}: {place(cs, ip, tsr_seg, load_seg)}.")
    elif len(segs) == 1:
        span = (min(t.ip for t in last), max(t.ip for t in last))
        lines.append(f"The last {len(last)} notes are all in segment {cs:04X}, {span[0]:04X} to {span[1]:04X}: "
                     f"{place(cs, span[0], tsr_seg, load_seg)}.")
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
    load_seg = ds - game.DGROUP if ds is not None else None
    if hdr is None:
        lines.append("DSCLOG wasn't found in memory, so where the game was isn't known.")
    else:
        tsr_seg = (hdr - struct.unpack("<H", read(hdr + TSR_HDR_OFF, 2))[0]) // 16
        lines.append(f"DSCLOG's segment {tsr_seg:04X}; the game's load segment "
                     + (f"{load_seg:04X}, DS {ds:04X}" if ds is not None else "not found"))
        if moved is not None:
            lines.append(f"In {WATCH_SECONDS:g} s the timer was noted {moved['tick']} times "
                         f"(0: the game's timer isn't striking) and the map's main loop ran {moved['main']} times.")
        found = ticks(read, hdr)
        lines += [""] + summary(found, tsr_seg, load_seg)
        lines += ["", "Where the game was as its timer struck, newest first (every 16th strike):",
                  "  CS:IP      flags SS:SP      BP   DS   ES    whose"]
        for t in reversed(found):
            lines.append(f"  {t.cs:04X}:{t.ip:04X}  {t.flags:04X}  {t.ss:04X}:{t.sp:04X}  {t.bp:04X} {t.ds:04X} "
                         f"{t.es:04X}  {place(t.cs, t.ip, tsr_seg, load_seg)}")
        lines += ["", "The code at each place now:"]
        for cs, ip in dict.fromkeys((t.cs, t.ip) for t in reversed(found)):
            lines.append(f"  {cs:04X}:{ip:04X}  {read(cs * 16 + ip, CODE_BYTES).hex(' ')}")
        if found:
            t = found[-1]
            lines += ["", f"The newest stack (SS:SP {t.ss:04X}:{t.sp:04X}), 64 words:"]
            words = struct.unpack("<64H", read(t.ss * 16 + t.sp, 128))
            for k in range(0, 64, 16):
                lines.append("  " + " ".join(f"{w:04X}" for w in words[k:k + 16]))
        lines += ["", f"DSCLOG's header ({HEADER_BYTES} bytes):"]
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


def write_report(folder: str, now: float, text: str, memory: bytes) -> str:
    """Save the report and the memory as crash-logs/freeze-YYYY-MM-DD-HHMMSS.zip (a number after
    it if there is one already); returns its path."""
    os.makedirs(folder, exist_ok=True)
    stem = os.path.join(folder, time.strftime("freeze-%Y-%m-%d-%H%M%S", time.localtime(now)))
    path, n = stem + ".zip", 1
    while os.path.exists(path):
        n += 1
        path = f"{stem}-{n}.zip"
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("freeze-report.txt", text)
        z.writestr("memory.bin", memory)
    return path


def freeze_report(read: Callable[[int, int], bytes], hdr: Optional[int], ds: Optional[int], version: str,
                  switches: Dict[str, object], dice: str, dialogue: str, folder: str) -> str:
    """Watch the counters a moment, write the report and the memory; returns the zip's path."""
    now = time.time()
    moved = _watch(read, hdr, WATCH_SECONDS) if hdr is not None else None
    text = report_text(read, hdr, ds, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(now)), version,
                       switches, dice, dialogue, moved)
    return write_report(folder, now, text, read(0, game.CONVENTIONAL_AND_UPPER))
