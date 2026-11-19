"""DOSBox-X as the game's engine: its configuration, its memory file, its version.

An option (the Options tab's Engine; `engine` in settings.json), new and played on Linux only so
far; GOG's DOSBox 0.74 stays the default and nothing of its start is changed. With it chosen the
Loader starts the player's own DOSBox-X (`dosbox_x_path`: nothing is bundled or downloaded) with a
configuration written whole here (nothing of GOG's dosbox_darksun.conf is used: DOSBox-X's
defaults differ from 0.74's, so every setting the mod relies on is said), and follows the game
through DOSBox-X's memory file: `[dosbox] memory file=PATH` (DOSBox-X 2025.01.01 and later) keeps
the emulated PC's RAM in a file, mapped shared, which the Loader reads and writes
(process.FileMemory) in place of another process's memory. So on Linux this engine needs no root
and no ptrace setting.

What each line of the configuration is for is said where it is written (conf_lines); how it was
found is in reports/modernisation-research-and-plan.md ("DOSBox-X: what was found") and
playtest/logs/2026-11-18-dosbox-x.md, 2026-11-19-dosbox-x-engine.md.

    python -m dsloader.dosboxx GAME_DIR CONF MEMORY_FILE [name=value ...]

writes CONF from the saved settings with the name=value pairs over them (`cycles=42000`,
`core=normal`, `extra=section|name=value`: the playtest kit's start_dosboxx.sh) and prints the
command's arguments after the program's name.
"""

import hashlib
import os
import re
import subprocess
import sys
import tempfile
from typing import Dict, List, Optional, Tuple

from . import midiout

GOG, DOSBOX_X = "gog", "dosbox-x"
ENGINES = (GOG, DOSBOX_X)
SETTING, PATH_SETTING = "engine", "dosbox_x_path"
SOUNDFONT_SETTING = "soundfont"          # a .sf2 file for DOSBox-X's built-in FluidSynth
MEMORY_DIR_SETTING = "dosbox_x_memory_dir"  # (hand-edited: another folder for the memory file)
MIN_VERSION = (2025, 1, 1)               # the first DOSBox-X with "memory file"
NAME = "DOSBox-X"


def engine(settings: dict) -> str:
    """The engine the settings ask for: "dosbox-x", else GOG's (also for anything unknown)."""
    chosen = settings.get(SETTING, GOG)
    return DOSBOX_X if isinstance(chosen, str) and chosen.strip().lower() == DOSBOX_X else GOG


def program(settings: dict) -> Optional[str]:
    """The DOSBox-X program the settings name, if it is a file; None otherwise."""
    path = settings.get(PATH_SETTING)
    return path if isinstance(path, str) and path and os.path.isfile(path) else None


# ---- the version ---------------------------------------------------------------------------

_VERSION = re.compile(rb"DOSBox-X version (\d{4})\.(\d{2})\.(\d{2})")
_IN_FILE = (re.compile(rb"dosbox-x-(\d{4})\.(\d{2})\.(\d{2})\.conf"),  # (the name of its own configuration file)
            re.compile(rb"DOSBox-X (\d{4})\.(\d{2})\.(\d{2})"))
VERSION_WAIT = 15  # seconds `dosbox-x -version` is given
_SCAN_CHUNK = 8 * 1024 * 1024

Version = Tuple[int, int, int]


def parse_version(text: bytes) -> Optional[Version]:
    """The version in what `dosbox-x -version` prints ("DOSBox-X version 2026.10.01 SDL2, ...")."""
    m = _VERSION.search(text)
    return (int(m.group(1)), int(m.group(2)), int(m.group(3))) if m else None


def version_in_file(path: str) -> Optional[Version]:
    """The version read from the program's own file (the name of its configuration file,
    "dosbox-x-2026.10.01.conf", is in it), without running it."""
    try:
        with open(path, "rb") as f:
            tail = b""
            while True:
                chunk = f.read(_SCAN_CHUNK)
                if not chunk:
                    return None
                data = tail + chunk
                for pattern in _IN_FILE:
                    m = pattern.search(data)
                    if m:
                        return int(m.group(1)), int(m.group(2)), int(m.group(3))
                tail = data[-64:]
    except OSError:
        return None


def version(path: str) -> Optional[Version]:
    """DOSBox-X's version at PATH, or None if it can't be told. Asked of the program
    (`-version`) except on Windows, where that opens a console and waits for a key: there, and
    where the program gives no answer, it is read from the program's file."""
    found = None
    if os.name != "nt":
        try:
            out = subprocess.run([path, "-version"], capture_output=True, timeout=VERSION_WAIT,
                                 stdin=subprocess.DEVNULL)
            found = parse_version(out.stdout + out.stderr)
        except (OSError, subprocess.SubprocessError):
            found = None
    return found or version_in_file(path)


def new_enough(found: Optional[Version]) -> bool:
    return found is not None and found >= MIN_VERSION


def version_text(found: Version) -> str:
    return "%04d.%02d.%02d" % found


def found_line(path: Optional[str], found: Optional[Version] = None, asked: bool = False) -> str:
    """What the Options tab says of the DOSBox-X at PATH (its version looked up unless ASKED
    says FOUND is the answer already)."""
    if not path:
        return "No DOSBox-X chosen yet: choose its program (dosbox-x, or dosbox-x.exe)."
    if not os.path.isfile(path):
        return f"Not found: {path} isn't there any more. Choose the program again."
    if not asked:
        found = version(path)
    if found is None:
        return (f"{path}: its version can't be read. It needs 2025.01.01 or later (the first with a memory "
                "file); if the Loader never connects to the game, this one is older.")
    if not new_enough(found):
        return (f"{path} is DOSBox-X {version_text(found)}: too old. The Loader follows the game through "
                "DOSBox-X's memory file, which came with 2025.01.01. Get a newer DOSBox-X.")
    return f"Found DOSBox-X {version_text(found)} ({path}): new enough for the memory file."


def problem(settings: dict) -> Optional[str]:
    """Why the game can't be started in DOSBox-X with these settings, or None."""
    path = settings.get(PATH_SETTING)
    if not isinstance(path, str) or not path:
        return ("DOSBox-X is chosen as the engine, but no DOSBox-X program is: choose it on the Options tab "
                "(Engine), or go back to GOG's DOSBox there.")
    if not os.path.isfile(path):
        return (f"DOSBox-X is chosen as the engine, but its program isn't there any more ({path}): choose it "
                "again on the Options tab (Engine), or go back to GOG's DOSBox there.")
    found = version(path)
    if found is not None and not new_enough(found):
        return (f"{path} is DOSBox-X {version_text(found)}, too old for the Loader: it follows the game "
                "through DOSBox-X's memory file, which came with 2025.01.01. Get a newer DOSBox-X, or go back "
                "to GOG's DOSBox on the Options tab (Engine).")
    return None


# ---- the memory file -----------------------------------------------------------------------

def memory_dir(settings: Optional[dict] = None) -> str:
    """The folder the memory file goes in: the settings' own if they name one that is there; else
    Linux's /dev/shm (memory, not a disk: the system then never writes the game's changing memory
    out); else the temp folder."""
    named = (settings or {}).get(MEMORY_DIR_SETTING)
    if isinstance(named, str) and named and os.path.isdir(named):
        return named
    if sys.platform.startswith("linux") and os.path.isdir("/dev/shm") and os.access("/dev/shm", os.W_OK):
        return "/dev/shm"
    return tempfile.gettempdir()


def memory_path(here: str, settings: Optional[dict] = None) -> str:
    """The memory file for the Loader in folder HERE: one name for each Obsidian Edition folder
    (only one game runs from a folder at a time: launch.GAME_LOCK), so the Loader finds its
    game's file again, and a file left behind is the next start's to take away."""
    mark = hashlib.sha1(os.path.abspath(here).encode("utf-8", "replace")).hexdigest()[:10]
    return os.path.join(memory_dir(settings), f"obsidian-edition-{mark}.mem")


def remove_memory_file(path: Optional[str]) -> bool:
    """The memory file taken away (the game has ended); True if it is gone."""
    if not path:
        return True
    try:
        os.remove(path)
    except FileNotFoundError:
        return True
    except OSError:
        return False
    return True


_MEMORY_LINE = re.compile(r"^\s*memory file\s*=\s*(.+?)\s*$", re.IGNORECASE | re.MULTILINE)


def conf_memory_file(conf: str) -> Optional[str]:
    """The memory file a DOSBox-X configuration file names, or None."""
    try:
        with open(conf, encoding="utf-8", errors="replace") as f:
            m = _MEMORY_LINE.search(f.read())
    except OSError:
        return None
    return m.group(1) if m else None


def process_memory_file(pid: int) -> Optional[str]:
    """The memory file of the DOSBox-X running as process PID, read from the configuration its
    command line names (`-conf FILE`); None if it has none or it can't be read (only Linux's
    /proc tells another process's command line here)."""
    try:
        with open(f"/proc/{pid}/cmdline", "rb") as f:
            args = [a.decode("utf-8", "replace") for a in f.read().split(b"\0")]
        cwd = os.readlink(f"/proc/{pid}/cwd")
    except OSError:
        return None
    for at, arg in enumerate(args[:-1]):
        if arg.lower() in ("-conf", "--conf"):
            found = conf_memory_file(os.path.join(cwd, args[at + 1]))
            if found:
                return os.path.join(cwd, found)
    return None


# ---- the configuration ---------------------------------------------------------------------

# The game's speed. DOSBox-X does less with the same cycles than 0.74, and each of its cores
# needs its own number: these walk as 0.74 does at the Loader's three speeds (launch.cpu_lines),
# measured with playtest/framerate.py (the slave pens, the whole party walking, everything on):
# playtest/logs/2026-11-19-dosbox-x-engine.md has the table. The keys are the `cycles` setting's
# values, which name the choice on the Options tab (GOG's own, Faster, Fastest), not DOSBox-X's
# cycles. "dynamic" is DOSBox-X's dynamic core for the computer it runs on (dynamic_x86 on an x86
# one; on an ARM one, an Apple Silicon Mac say, dynamic_rec, which does more per cycle: UNTESTED).
SPEEDS: Dict[object, Tuple[str, int]] = {
    "gog": ("normal", 8000),      # GOG's own: as 0.74's normal core at 7000
    20000: ("dynamic", 22000),    # Faster
    35000: ("dynamic", 42000),    # Fastest (the default)
}
DEFAULT_SPEED = 35000
FASTEST_BEFORE = 30000  # (launch.FASTEST_BEFORE: an older setting, taken as the fastest)


def speed(settings: dict) -> Tuple[str, int]:
    """(core, cycles) for the settings' game speed."""
    chosen = settings.get("cycles", DEFAULT_SPEED)
    chosen = DEFAULT_SPEED if chosen == FASTEST_BEFORE else chosen
    if isinstance(chosen, bool) or chosen not in SPEEDS:
        chosen = DEFAULT_SPEED
    return SPEEDS[chosen]


WINDOW_SCALES, DEFAULT_SCALE = (1, 2, 3, 4), 3
PLAIN, SCANLINES, TV, SHARP = "plain", "scanlines", "tv", "sharp"
LINE_SCALERS = {SCANLINES: "scan", TV: "tv"}  # (scan2x, scan3x; tv2x, tv3x: no 4x of either, as on 0.74)
FULL_SCREEN_LINES = 3


def display(settings: dict, look: str) -> Tuple[List[str], List[str]]:
    """The [sdl] and [render] lines for the settings' window and the picture LOOK (launch.picture:
    plain where the window has no other). The same four sizes and four pictures as on 0.74:

    - a window: 320x240 times `window_scale`. Plain is DOSBox-X's normal2x, normal3x or normal4x
      scaler (it has a 4x, which 0.74 lacks): twice on its plain surface output, three and four
      times through its unfiltered OpenGL output (`openglnb`), because on the surface output
      normal3x and normal4x drew this game as an empty grey window (DOSBox-X 2026.10.01, SDL2,
      Linux; scan3x and tv3x draw there). Scanlines and TV are its scan and tv scalers, 2x or 3x
      as the window's on the surface output, and in the four-times window 2x doubled by
      `openglnb`. Sharp is `openglnb` stretching the game's own 320x200 to the window, nothing
      smoothed; with every pixel a block either way, it differs from Plain only in which rows
      the 200 lines are made 240 by.
    - full screen at the desktop's size, through OpenGL (the surface output doesn't stretch),
      the picture kept 4:3 with black at the sides of a wider screen: Plain `opengl` (smoothed,
      as GOG's own full screen is) over normal3x, Scanlines and TV the 3x scaler under it, Sharp
      `openglnb`.

    Not offered yet: DOSBox-X's pixel-perfect output (`openglpp`: whole multiples only, so 4:3
    just at 1600x1200, 5x6, which none of the four windows is) and its CRT shaders (`glshader`:
    files that come with DOSBox-X's packages, not with every build).

    `aspect=true` keeps the picture 4:3 as on 0.74, and `doublescan=false` keeps the 320x200 mode
    from being handed on as 640x400 (the window would be twice the size asked for). The mouse is
    captured on a click and moves the game's pointer as the desktop's moves (`sensitivity` 100
    over the scale: launch.display_lines), and the middle and right buttons are the game's:
    DOSBox-X's defaults give the middle one to unlocking the mouse (the mod's map drag then does
    nothing) and the right one to its clipboard."""
    sdl = ["showmenu=false", "autolock=true", "autolock_feedback=none", "middle_unlock=none",
           "clip_mouse_button=none"]
    render = ["aspect=true", "doublescan=false"]
    if settings.get("fullscreen"):
        sdl += ["fullscreen=true", "fullresolution=desktop", "sensitivity=100,100",
                "output=" + ("openglnb" if look == SHARP else "opengl")]
        if look == SHARP:
            render.append("scaler=none")
        else:
            render.append(f"scaler={LINE_SCALERS.get(look, 'normal')}{FULL_SCREEN_LINES}x")
        return sdl, render
    scale = settings.get("window_scale", DEFAULT_SCALE)
    scale = scale if scale in WINDOW_SCALES and not isinstance(scale, bool) else DEFAULT_SCALE
    speed_ = round(100 / scale)
    sdl += ["fullscreen=false", f"sensitivity={speed_},{speed_}"]  # (across, down: one number alone is across only)
    size = f"windowresolution={320 * scale}x{240 * scale}"
    if scale == 1:
        sdl += ["output=surface", "windowresolution=original"]
        render.append("scaler=none")
    elif look == SHARP:
        sdl += ["output=openglnb", size]
        render.append("scaler=none")
    elif look in LINE_SCALERS:
        by = 2 if scale == 4 else scale
        sdl += ["output=openglnb", size] if scale == 4 else ["output=surface", "windowresolution=original"]
        render.append(f"scaler={LINE_SCALERS[look]}{by}x")
    else:
        sdl += ["output=surface", "windowresolution=original"] if scale == 2 else ["output=openglnb", size]
        render.append(f"scaler=normal{scale}x")
    return sdl, render


def soundfont(settings: dict) -> Optional[str]:
    """The soundfont file the settings name, if it is there; None otherwise."""
    path = settings.get(SOUNDFONT_SETTING)
    return path if isinstance(path, str) and path and os.path.isfile(path) else None


def midi_lines(settings: dict) -> List[str]:
    """DOSBox-X's [midi] lines for the settings' music device (midiout.setting) and soundfont:

    - a device chosen (a number as Windows counts its MIDI outputs, or an ALSA port "128:0"):
      that device, `mididevice=win32` or `alsa` with `midiconfig` naming it;
    - else, with a soundfont file named: DOSBox-X's built-in FluidSynth playing through it
      (`mididevice=fluidsynth`, `fluid.soundfont`). On Linux this is how the music is heard
      without a synthesizer set up outside DOSBox-X;
    - else DOSBox-X's own default (`mididevice=default`: Windows' MIDI Mapper there; on Linux,
      where FluidSynth has no soundfont to play, usually no music).

    MT-32 (`mididevice=mt32`, which needs the Roland ROMs) isn't offered."""
    lines = ["mpu401=intelligent"]
    device = midiout.setting(settings)
    font = soundfont(settings)
    if device != midiout.DEFAULT:
        lines += ["mididevice=" + ("alsa" if isinstance(device, str) else "win32"), f"midiconfig={device}"]
    elif font:
        lines += ["mididevice=fluidsynth", f"fluid.soundfont={font}"]
    else:
        lines += ["mididevice=default"]
    return lines


def music_line(settings: dict) -> str:
    """What the music plays through on DOSBox-X with these settings, for the Options tab."""
    device = midiout.setting(settings)
    if device != midiout.DEFAULT:
        return f"On DOSBox-X the music goes to device {device}."
    font = soundfont(settings)
    if font:
        return f"On DOSBox-X the music plays through its own synthesizer with {os.path.basename(font)}."
    named = settings.get(SOUNDFONT_SETTING)
    if isinstance(named, str) and named:
        return f"The soundfont file isn't there any more ({named})."
    return ("No soundfont file chosen. On Linux DOSBox-X needs one (a .sf2 file) for its own synthesizer to "
            "play the music; without it there is usually none.")


def conf_lines(game_dir: str, dos_dir: str, memory_file: str, settings: Optional[dict] = None,
               dice_log: bool = True, look: str = PLAIN, autoexec: Tuple[str, str, str] = ("", "", ""),
               options: Optional[dict] = None) -> List[str]:
    """The whole configuration. GAME_DIR is mounted as C:, DOS_DIR (the Loader's dos folder) as
    D:; AUTOEXEC names the three programs run from D: (launch's UMBPLUS.COM, DSUNLOG.EXE,
    GAMEEND.COM). OPTIONS, for tests of the engine itself: `core`, `cycles`, `capture` (a folder:
    the game run under DOSBox-X's own `dx-capture /a`, its sound written there), `extra` (more
    lines, each "section|name=value")."""
    s = settings or {}
    o = dict(options or {})
    core, cycles = speed(s)
    core, cycles = o.get("core", core), o.get("cycles", cycles)
    sdl, render = display(s, look)
    umbplus, patched, game_end = autoexec
    lines = ["[sdl]"] + sdl + [""]
    lines += [
        # GOG's machine and memory; the file that is the emulated PC's RAM (process.FileMemory)
        "[dosbox]", "machine=svga_s3", "memsize=32", f"memory file={memory_file}",
        "quit warning=false", "fastbioslogo=true", "startbanner=false",
        *([f"captures={o['capture']}"] if o.get("capture") else []), "",
        "[render]"] + render + [
        "",
        "[cpu]", f"core={core}", "cputype=auto", f"cycles=fixed {cycles}", "",
        # GOG's card: the game's sound driver is set up for it (DOSBox-X's own default is IRQ 7:
        # "Mel Fatal Error ... DSP Detect Fail")
        "[sblaster]", "sbtype=sb16", "sbbase=220", "irq=5", "dma=1", "hdma=5", "",
        "[midi]"] + midi_lines(s) + [
        "",
        # EMS off as on 0.74 (launch.DOS_LINES: its page frame takes the upper memory DSCLOG loads
        # into; the game takes XMS without it). Conventional memory as 0.74's: by default DOSBox-X
        # keeps DOS's own structures in the 640 KB and pads them up to segment 0700h, and the game
        # then loads at 0824h, 26.7 KB higher than on 0.74 (01A2h). With the last two lines it
        # loads at 0224h (2 KB higher); the structures go in DOSBox-X's private area
        # (C800h-CBFFh), which takes nothing from the upper memory DSCLOG loads into (CC00h-EFFFh)
        "[dos]", "xms=true", "ems=false", "umb=true", "log console=true",
        "minimum mcb free=100", "kernel allocation in umb=true", "",
        # DOS itself not in the HMA (DOSBox-X's default is "dos=high, umb"): DSCLOG's far block
        # takes the HMA, as on 0.74; refused it, its far block would go into upper memory and
        # leave no room there for the game's overlay buffer
        "[config]", "dos=umb", "",
    ]
    for extra in o.get("extra", ()):
        section, line = extra.split("|", 1)
        lines.insert(lines.index(f"[{section}]") + 1, line)
    lines += ["[autoexec]", "@echo off", f'mount c "{game_dir}"']
    if os.path.isdir(os.path.join(game_dir, "cloud_saves")):  # where GOG keeps the saves
        lines.append(f'mount c "{os.path.join(game_dir, "cloud_saves")}" -t overlay')
    lines += [f'mount d "{dos_dir}"', "c:"]
    run = "dx-capture /a " if o.get("capture") else ""
    if dice_log:
        # (UMBPLUS.COM changes nothing under DOSBox-X: its chain isn't 0.74's, and its upper
        # memory already starts lower, at CC00h; run all the same, so one autoexec serves both)
        lines += ["d:\\" + umbplus.lower(), r"lh d:\dsclog.exe", run + "d:\\" + patched.lower()]
    else:
        lines += [run + "dsun.exe" if run else "darksun"]
    lines += ["d:\\" + game_end.lower(), "exit", ""]
    return lines


def arguments(conf: str) -> List[str]:
    """DOSBox-X's arguments: this configuration alone, no menu bar (it would make the window
    taller than the game's picture), no question about the working folder, no logo."""
    return ["-conf", conf, "-nopromptfolder", "-nomenu", "-fastlaunch"]


def _value(text: str):
    if text.lower() in ("true", "false"):
        return text.lower() == "true"
    return int(text) if text.isdigit() else text


def main(argv: List[str]) -> int:
    from . import launch
    game_dir, conf, memory_file = argv[:3]
    settings = launch.load_settings()
    options: dict = {"extra": []}
    dice_log = True
    for item in argv[3:]:
        name, value = item.split("=", 1)
        if name == "extra":
            options["extra"].append(value)
        elif name == "dice_log":
            dice_log = bool(_value(value))
        elif name in ("core", "cycles", "capture"):
            options[name] = _value(value)
        else:
            settings[name] = _value(value)
    settings[SETTING] = DOSBOX_X
    if dice_log:
        problem_ = launch.prepare_patched_game(game_dir, settings)
        if problem_:
            print("problem:", problem_, file=sys.stderr)
            return 1
    launch.write_conf(game_dir, conf, dice_log, settings, memory_file=memory_file, options=options)
    print(" ".join(arguments(conf)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
