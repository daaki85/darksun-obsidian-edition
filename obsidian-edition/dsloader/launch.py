"""Starting the GOG release of Shattered Lands with the dice log.

GOG runs DOSBox with two config files: dosbox_darksun.conf (settings) and
dosbox_darksun_single.conf (the [autoexec] that mounts the game and shows a
small menu). We keep the first and replace the second with our own
[autoexec], which also mounts the Loader's dos folder as D:, loads
DSCLOG.EXE into upper memory, and runs DSUNLOG.EXE: a patched copy of the
game (see gamepatch.py) that the Loader keeps in the dos folder. Nothing in
the game folder is changed.

With DOSBox-X chosen as the engine (the Options tab; dosboxx.py) the Loader starts the player's
own DOSBox-X instead, with a configuration of its own written whole (nothing of GOG's is read),
and follows the game through DOSBox-X's memory file.
"""

import json
import os
import string
import struct
import subprocess
import tempfile
import threading
import time
from typing import Dict, Iterator, List, Optional, Tuple

from . import champions, dosboxx, gamepatch, gff, gpl, icons, kalzith, midiout, scenepointer, tome, worldgear

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOS_DIR = os.path.join(HERE, "dos")
SETTINGS = os.path.join(HERE, "settings.json")
CONF = os.path.join(HERE, "dosbox_dicelog.conf")
# DOSBox-X's own folder in the Loader's: its configuration, what it prints (DBX_LOG, for the crash
# report), and whatever it writes beside itself (it runs here, never in the game's folder)
DBX_DIR = os.path.join(HERE, "dosbox-x")
DBX_CONF = os.path.join(DBX_DIR, "obsidian.conf")
DBX_LOG = os.path.join(DBX_DIR, "dosbox-x.log")
PATCHED_EXE = "DSUNLOG.EXE"

GOG_SUBDIRS = (
    r"GOG Games\Dark Sun Shattered Lands",
    r"Program Files (x86)\GOG Galaxy\Games\Dark Sun Shattered Lands",
    r"Program Files\GOG Galaxy\Games\Dark Sun Shattered Lands",
    r"GOG Galaxy\Games\Dark Sun Shattered Lands",
    r"Games\Dark Sun Shattered Lands",
    r"Program Files (x86)\GOG Galaxy\Games\Dark Sun",  # (GOG Galaxy's own name for it)
    r"Program Files\GOG Galaxy\Games\Dark Sun",
    r"GOG Galaxy\Games\Dark Sun",
)


class LaunchError(Exception):
    pass


def _find_file(folder: str, name: str) -> Optional[str]:
    """`name` inside `folder`, ignoring case (for Linux, and odd installs)."""
    try:
        for entry in os.listdir(folder):
            if entry.lower() == name.lower():
                return os.path.join(folder, entry)
    except OSError:
        pass
    return None


def is_game_dir(folder: str) -> bool:
    """The GOG install: DSUN.EXE and its DOSBox (just DSUN.EXE and the data files, when the game
    is to run as Dark Sun Recompiled instead of in DOSBox, or in the player's own DOSBox-X: the
    Options tab's engine)."""
    dosbox = _find_file(folder, "DOSBOX")
    if not _find_file(folder, "DSUN.EXE"):
        return False
    if dosbox and _find_file(dosbox, "DOSBox.exe"):
        return True
    settings = load_settings()
    return recompiled_program(settings) is not None or dosboxx.engine(settings) == dosboxx.DOSBOX_X


def game_dir_wanted() -> str:
    """What a folder must hold to be the game's, for the message when it doesn't."""
    if dosboxx.engine(load_settings()) == dosboxx.DOSBOX_X:
        return "DSUN.EXE: pick the game's folder (with DOSBox-X as the engine, GOG's DOSBOX folder isn't needed)"
    return "DSUN.EXE and DOSBOX folder; pick the GOG install folder of Shattered Lands"


# Dark Sun Recompiled (github.com/daaki85/darksun-recompiled): the game translated into a program
# of its own, with the mod's patched game and DSCLOG built in. The Loader starts that program
# instead of DOSBox when it finds it: unzipped into this folder (a "recompiled" subfolder, or its
# files here), or in its own "darksun-recompiled..." folder beside this one (a bare dsun.exe beside
# this folder, in Downloads say, is never taken: it could be anything), or named in SETTINGS
# ("recompiled"; `dsloader launch --recompiled <path>` remembers a path, `--dosbox` turns the
# program off until `--recompiled` again). It is started with the game's folder (its data files;
# the game is recognised by its DSUN.EXE) and the mod's dos folder as drive D (DSUNLOG.EXE and
# the data files DSCLOG replaces); it keeps its memory images (build/ds1o) beside itself.
RECOMPILED_EXE = "dsun.exe" if os.name == "nt" else "dsun"


def native_program(path: str) -> bool:
    """Whether PATH is a program of the computer's own (a Windows PE, or an ELF): not the game's DOS
    DSUN.EXE, which Windows, with no case in its file names, also finds as dsun.exe (a mod unzipped
    in the game's folder has it beside it)."""
    try:
        with open(path, "rb") as f:
            head = f.read(64)
            if head[:4] == b"\x7fELF":
                return True
            if head[:2] != b"MZ" or len(head) < 64:
                return False
            f.seek(int.from_bytes(head[0x3C:0x40], "little"))
            return f.read(4) == b"PE\0\0"
    except (OSError, ValueError):
        return False


def found_recompiled_program(here: str = HERE) -> Optional[str]:
    """Dark Sun Recompiled's program where a player would put it: in this folder (or its
    "recompiled" subfolder), or in a folder named after it ("darksun-recompiled...") in this folder
    or beside it; None when there is none. Only those: a program merely named dsun.exe in the
    folder that holds this one (Downloads, say) isn't taken, and a file of its name that is no
    program of the computer's own, the game's DOS DSUN.EXE above all, isn't it either
    (native_program)."""
    import glob as _glob
    parent = os.path.dirname(here)
    candidates = [os.path.join(here, "recompiled", RECOMPILED_EXE), os.path.join(here, RECOMPILED_EXE)]
    candidates += sorted(_glob.glob(os.path.join(here, "darksun-recompiled*", RECOMPILED_EXE)))
    candidates += sorted(_glob.glob(os.path.join(parent, "darksun-recompiled*", RECOMPILED_EXE)))
    candidates += sorted(_glob.glob(os.path.join(parent, "darksun-recompiled*", "windows", RECOMPILED_EXE)))
    for c in candidates:
        if os.path.isfile(c) and native_program(c):
            return c
    return None


def recompiled_program(settings: Optional[dict] = None) -> Optional[str]:
    """The path of the recompiled program to start instead of DOSBox: the one named in the
    settings when it is there, else the one found beside the mod; None when the settings say
    DOSBox (--dosbox) or there is none."""
    path = (load_settings() if settings is None else settings).get("recompiled")
    if path is False:
        return None
    if isinstance(path, str) and path and os.path.isfile(path) and native_program(path):
        return path
    return found_recompiled_program()


def recompiled_command(program: str, game_dir: str) -> List[str]:
    """The command line that starts the recompiled program with the mod."""
    return [program, "--game", game_dir, "--cd", DOS_DIR]


def drives() -> Iterator[str]:
    """Windows' drives from C: on, each looked at only when the one before has been searched: an
    empty floppy drive or a sleeping network drive can take seconds to answer (A: and B:, the
    floppies, never)."""
    if os.name != "nt":
        return
    for letter in string.ascii_uppercase[2:]:
        root = f"{letter}:\\"
        if os.path.exists(root):
            yield root


def candidate_dirs() -> Iterator[str]:
    for drive in drives():
        for sub in GOG_SUBDIRS:
            yield os.path.join(drive, sub)


# Settings saved before version 2 had the combat log off by default (and saved it so): version 2
# turns it on once, after which the player's own choice stands.
SETTINGS_VERSION = 2


def settings_version(settings: dict) -> int:
    """The settings' version (1 if none, or not a number: a hand-edited file's "2" is 2)."""
    version = settings.get("settings_version", 1)
    if isinstance(version, bool):
        return 1
    try:
        return int(version)
    except (TypeError, ValueError):
        return 1


def upgrade_settings(settings: dict) -> bool:
    """Bring settings saved by an older Loader up to SETTINGS_VERSION; True if anything changed."""
    if not settings or settings_version(settings) >= SETTINGS_VERSION:
        return False
    settings["settings_version"] = SETTINGS_VERSION  # (version 1's combat log turned on: always on now)
    return True


# One read-modify-write of settings.json at a time (the window, and the thread reading the game,
# both change it: update_settings)
SETTINGS_LOCK = threading.RLock()


class SettingsUnreadable(OSError):
    """settings.json is there but couldn't be read (held by an antivirus or a backup for a moment):
    not the same as no settings, so nothing may be saved over it."""


# how long a read of settings.json held elsewhere is tried for (tries, each SETTINGS_WAIT apart)
SETTINGS_TRIES, SETTINGS_WAIT = 10, 0.05


def load_settings(strict: bool = False, tries: int = SETTINGS_TRIES) -> dict:
    """settings.json as a dict ({} if there is none). A file that is there but can't be read now
    (Windows: open elsewhere for a moment, an antivirus or a backup) is tried again for a while;
    then a plain read gives {}, and a STRICT one (for a read that is changed and saved again, or
    whose answer must be the player's settings) raises SettingsUnreadable rather than read as
    empty, so the save after it can't put just the change, or the defaults, in place of
    everything. A missing file is {} either way."""
    with SETTINGS_LOCK:
        for attempt in range(max(1, tries)):
            try:
                with open(SETTINGS, encoding="utf-8-sig") as f:  # (a BOM from Notepad too)
                    settings = json.load(f)
                break
            except FileNotFoundError:
                return {}
            except OSError as e:
                if attempt == max(1, tries) - 1:  # (tried again first either way: one held a moment
                    if not strict:                # read as empty lost the picked pockets once the next pick saved)
                        return {}
                    raise SettingsUnreadable(e.errno, f"settings.json can't be read just now ({e.strerror or e})",
                                             SETTINGS) from e
                time.sleep(SETTINGS_WAIT)
            except ValueError:
                # (unreadable: kept aside as settings.json.bad, so the next save can't lose what it held)
                _keep_aside()
                return {}
        if not isinstance(settings, dict):  # (JSON, but not the Loader's: kept aside too)
            _keep_aside()
            return {}
        _drop_misshapen(settings)
        from . import game
        game.drop_always_on(settings)  # (a switch now always on: an older file's False passed over)
        if upgrade_settings(settings):
            try:
                save_settings(settings)
            except OSError:
                pass  # (upgraded again next time)
        return settings


# the settings kept as lists and dicts (and what each holds), which every reader takes as such: a
# hand-edited file's other shape (a string, a number) is dropped as read, not raised at every start
SHAPES = {"speakers": dict, "speakers_learned": dict, "pickpocketed": list}


def _drop_misshapen(settings: dict) -> None:
    for key, kind in SHAPES.items():
        if key in settings and not isinstance(settings[key], kind):
            del settings[key]
    if "pickpocketed" in settings:
        settings["pickpocketed"] = [e for e in settings["pickpocketed"] if isinstance(e, str)]


def _keep_aside() -> None:
    """settings.json, unreadable, renamed settings.json.bad (an earlier .bad kept as .bad-2...)."""
    bad, n = SETTINGS + ".bad", 1
    while os.path.exists(bad) and n < 100:
        n += 1
        bad = f"{SETTINGS}.bad-{n}"
    try:
        os.replace(SETTINGS, bad)
    except OSError:
        pass


def save_settings(settings: dict) -> None:
    """Written whole or not at all: into a temporary file of this write's own (two Loaders, or the
    window and `play`, never share one), then put in settings.json's place."""
    from . import game
    game.drop_always_on(settings)  # (a switch now always on isn't kept: game.ALWAYS_ON)
    settings["settings_version"] = SETTINGS_VERSION
    with SETTINGS_LOCK:
        fd, tmp = tempfile.mkstemp(prefix=os.path.basename(SETTINGS) + ".", suffix=".tmp",
                                   dir=os.path.dirname(SETTINGS) or ".")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=2)
                f.flush()
                os.fsync(f.fileno())
            for attempt in range(5):
                try:
                    os.replace(tmp, SETTINGS)
                    return
                except PermissionError:  # (Windows: the file open elsewhere for a moment)
                    if attempt == 4:
                        raise
                    time.sleep(0.05)
        finally:
            if os.path.exists(tmp):  # (not put in place: not left behind)
                try:
                    os.remove(tmp)
                except OSError:
                    pass


SETTINGS_FILE_WAIT = 2.0  # seconds update_settings waits for another process's settings lock, at most
_settings_file_held = threading.local()


def _settings_file_lock():
    """A lock on settings.lock beside settings.json, across processes (the window and `play` both
    rewrite settings.json: a read and write of one, between the other's, lost the other's change).
    Waited for up to SETTINGS_FILE_WAIT, then gone on without (as before); none where the folder
    can't be written or the system can't lock. A context manager; again within it, nothing."""
    import contextlib

    @contextlib.contextmanager
    def held():
        if getattr(_settings_file_held, "depth", 0):
            _settings_file_held.depth += 1
            try:
                yield
            finally:
                _settings_file_held.depth -= 1
            return
        try:
            fd: Optional[int] = os.open(os.path.splitext(SETTINGS)[0] + ".lock", os.O_RDWR | os.O_CREAT, 0o644)
        except OSError:
            fd = None
        taken = False
        if fd is not None:
            end = time.monotonic() + SETTINGS_FILE_WAIT
            while True:
                got = _lock_file(fd)
                if got is not False or time.monotonic() >= end:
                    taken = bool(got)
                    break
                time.sleep(0.02)
        _settings_file_held.depth = 1
        try:
            yield
        finally:
            _settings_file_held.depth = 0
            if fd is not None:
                if taken:
                    _unlock_file(fd)
                os.close(fd)
    return held()


def _unlock_file(fd: int) -> None:
    try:
        if os.name == "nt":
            import msvcrt
            os.lseek(fd, _LOCK_AT, os.SEEK_SET)
            msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
        else:
            import fcntl
            fcntl.flock(fd, fcntl.LOCK_UN)
    except OSError:
        pass


def update_settings(changes: dict) -> dict:
    """settings.json with CHANGES made, read and written as one step (in this process, and against
    another's: _settings_file_lock); the settings as saved."""
    with SETTINGS_LOCK, _settings_file_lock():
        settings = load_settings(strict=True)
        settings.update(changes)
        save_settings(settings)
        return settings


def _names(settings: dict, key: str) -> Dict[int, str]:
    """{portrait: name} from the settings' KEY (nothing if a hand-edited file has no dict there)."""
    names = settings.get(key, {})
    if not isinstance(names, dict):
        return {}
    return {int(k): v for k, v in names.items() if str(k).isdecimal() and isinstance(v, str) and v}


def _dict_in(settings: dict, key: str) -> dict:
    """settings[KEY], made a dict if it is missing or not one (a hand-edited file)."""
    if not isinstance(settings.get(key), dict):
        settings[key] = {}
    return settings[key]


def speaker_names() -> Dict[int, str]:
    """The names the player has given dialogue portraits: {portrait: name}."""
    return _names(load_settings(), "speakers")


def set_speaker_name(portrait: int, name: str) -> None:
    """Remember a name for a portrait (an empty name forgets it)."""
    with SETTINGS_LOCK:
        _set_speaker_name(portrait, name)


def _set_speaker_name(portrait: int, name: str) -> None:
    settings = load_settings(strict=True)
    names = _dict_in(settings, "speakers")
    if name:
        names[str(portrait)] = name
    else:
        names.pop(str(portrait), None)
    save_settings(settings)


def learned_speakers() -> Dict[int, str]:
    """Portrait names the Loader worked out from conversations: {portrait: name}."""
    return _names(load_settings(), "speakers_learned")


def pickpocketed(tries: int = SETTINGS_TRIES) -> List[str]:
    """The pockets tried already (pickpocket.py), "key@game time" each: each person gets one try.
    Read strictly: SettingsUnreadable if settings.json is held elsewhere, never [] in place of the
    list (which the next pick would then save over it)."""
    entries = load_settings(strict=True, tries=tries).get("pickpocketed", [])
    return [e for e in entries if isinstance(e, str)] if isinstance(entries, list) else []


def set_pickpocketed(entries: List[str]) -> None:
    update_settings({"pickpocketed": list(entries)})


def add_learned_speakers(learned: Dict[int, str]) -> None:
    with SETTINGS_LOCK:
        settings = load_settings(strict=True)
        _dict_in(settings, "speakers_learned").update({str(k): v for k, v in learned.items()})
        save_settings(settings)


def find_game_dir(given: Optional[str] = None) -> Optional[str]:
    """The game folder, as a full path (DOSBox runs in its DOSBOX folder, so a relative one would
    point elsewhere): `given`, the one remembered from last time, or a usual GOG location (the
    drives searched once a run: _SEARCHED)."""
    for folder in (given, load_settings().get("game_dir")):
        if folder and is_game_dir(folder):
            return os.path.abspath(folder)
    if "found" not in _SEARCHED:
        _SEARCHED["found"] = next((os.path.abspath(f) for f in candidate_dirs() if is_game_dir(f)), None)
    return _SEARCHED["found"]


_SEARCHED: Dict[str, Optional[str]] = {}  # (find_game_dir's search of the drives, kept for the run)


SCALERS = {2: "normal2x", 3: "normal3x"}
DEFAULT_SCALE = 3
WINDOW_SCALES = (1, 2, 3, 4)

# The picture: how DOSBox 0.74 draws the game's 320x200 larger (its render.cpp and sdlmain.cpp).
# PLAIN is each pixel as a block (`normal2x`, `normal3x`). SCANLINES and TV are 0.74's `scan` and
# `tv` scalers, which leave the last line of each game row black (scan) or dimmed (tv); they come
# at 2x and 3x only. SHARP is 0.74's unfiltered OpenGL output (`openglnb`): whatever stretching is
# left to DOSBox's output (the aspect correction, the four-times window, full screen up to the
# desktop's size) is done without the smoothing GOG's DirectDraw output or `opengl` give it.
PLAIN, SCANLINES, TV, SHARP = "plain", "scanlines", "tv", "sharp"
PICTURES = (PLAIN, SCANLINES, TV, SHARP)
DEFAULT_PICTURE = PLAIN
LINE_SCALERS = {SCANLINES: "scan", TV: "tv"}  # (scan2x, scan3x; tv2x, tv3x: 0.74 has no 4x of any)
FULL_SCREEN_LINES = 3  # (full screen: the 3x one, its dark line a third of a row, not half)


def pictures(settings: dict) -> Tuple[str, ...]:
    """The pictures there are for the settings' window: every one in full screen and in a window
    of twice the game's size or more; in the single-size window (320x240, nothing scaled) only the
    plain one."""
    if settings.get("fullscreen"):
        return PICTURES
    return (PLAIN,) if settings.get("window_scale", DEFAULT_SCALE) == 1 else PICTURES


def picture(settings: dict) -> str:
    """The picture DOSBox is asked for: the settings' `picture` if the window has it, else the
    plain one (also for a `picture` the Loader doesn't know)."""
    chosen = settings.get("picture", DEFAULT_PICTURE)
    return chosen if isinstance(chosen, str) and chosen in pictures(settings) else DEFAULT_PICTURE


def display_lines(settings: dict) -> List[str]:
    """DOSBox's display, over GOG's settings (full screen): a window, by default three times the
    game's 320x200 (960x720 with the aspect correction GOG turns on); `window_scale` 2 makes it
    twice, 4 four times, 1 leaves it at 320x240; `fullscreen` true keeps GOG's full screen.
    Alt+Enter switches either way in DOSBox. DOSBox 0.74 has no 4x scaler, so four times is
    DOSBox scaling the window itself, which needs its OpenGL output.
    `picture` (picture()) changes how it is drawn larger. Scanlines and TV put 0.74's scan or tv
    scaler in the plain one's place: 2x or 3x as the window's, 2x in the four-times window (which
    OpenGL then doubles), 3x in full screen (GOG's output stretching it to the desktop). Sharp
    makes the output `openglnb`, with the window's size given so that OpenGL does the aspect
    correction (the plain scaler stays, so a driver without OpenGL, where DOSBox falls back to its
    plain surface, still opens the window at its size).
    With the pointer's start and speed (`mouse_start`, on unless switched off) the mouse's
    `sensitivity` is 100 over the scale: DOSBox moves the captured game's pointer a game pixel for
    each pixel the hand moves on the desktop, SCALE screen pixels in the window, so this makes it
    move as the desktop's pointer does (DSCLOG's MOUSE_RATIO allows for the taller pixels); the
    mouse is captured on a click (`autolock`, as GOG has it). The picture changes none of that:
    the window's size is the same for each."""
    look = picture(settings)
    if settings.get("fullscreen"):
        if look == SHARP:
            return ["[sdl]", "output=openglnb", ""]
        if look in LINE_SCALERS:
            return ["[render]", f"scaler={LINE_SCALERS[look]}{FULL_SCREEN_LINES}x", ""]
        return []
    scale = settings.get("window_scale", DEFAULT_SCALE)
    scale = scale if scale in WINDOW_SCALES else DEFAULT_SCALE
    sdl = ["[sdl]", "fullscreen=false"]
    sdl += ["autolock=true", f"sensitivity={round(100 / scale)}"]  # (the pointer where it starts, mouse_start:
    # captured, as uncaptured DOSBox reads the desktop pointer's place in the window, which the sensitivity would scale)
    if scale == 1:
        return sdl + ["[render]", "aspect=true", "scaler=none", ""]
    by = 2 if scale == 4 else scale  # (the scaler's share of it)
    scaler = f"{LINE_SCALERS[look]}{by}x" if look in LINE_SCALERS else SCALERS[by]
    if scale == 4 or look == SHARP:
        sdl += ["output=" + ("openglnb" if look == SHARP else "opengl"),
                f"windowresolution={320 * scale}x{240 * scale}"]
    return sdl + ["[render]", "aspect=true", "scaler=" + scaler, ""]


# The game's speed: DOSBox's emulated CPU (fixed cycles: instructions a millisecond). The game
# moves everything a step at each tick of its clock (96 a second), and a tick passed while a frame
# is drawn is a step lost. Measured in the slave pens, the whole party walking, everything on and
# steady pace on: at 35000, 18.9 frames a second (about all the game draws) and 141 map units a
# second walking; at 20000, 15.5 and 112; GOG's 7000 slower still. 35000 is the default. Both with the dynamic core
# (GOG's "auto" runs this game, a real-mode one, on the normal core): the same cycles do more and
# cost the computer about a third less. (30000, the fastest of before, is taken as the fastest now.)
GOG_SPEED, SPEEDS, DEFAULT_SPEED = "gog", (20000, 35000), 35000
FASTEST_BEFORE = 30000
CORE = "dynamic"


def cpu_lines(settings: dict) -> List[str]:
    """DOSBox's CPU speed, over GOG's settings: `cycles` 20000 or 35000 (the default), on the
    dynamic core; "gog" keeps GOG's own."""
    speed = settings.get("cycles", DEFAULT_SPEED)
    if speed == GOG_SPEED:
        return []
    speed = SPEEDS[-1] if speed == FASTEST_BEFORE else speed
    speed = speed if speed in SPEEDS else DEFAULT_SPEED
    return ["[cpu]", f"core={CORE}", f"cycles=fixed {speed}", ""]


# GOG's dosbox_darksun.conf has EMS on, and DOSBox 0.74 then keeps EMS's 64 KB page frame in the
# upper memory DSCLOG loads into, leaving it 1 KB to spare; with EMS off the block is the
# DSCLOG's (65 KB free). The game's memory layer takes XMS when there is no EMS.
DOS_LINES = ["[dos]", "ems=false", ""]


def write_conf(game_dir: str, path: Optional[str] = None, dice_log: bool = True, settings: Optional[dict] = None,
               memory_file: Optional[str] = None, options: Optional[dict] = None) -> str:
    """Our replacement for dosbox_darksun_single.conf (at CONF unless PATH says where). Without the
    dice log it just runs the game. SETTINGS: the saved ones if not given.
    With DOSBox-X as the settings' engine it is DOSBox-X's whole configuration instead (at
    DBX_CONF; dosboxx.conf_lines, with MEMORY_FILE the memory file: the Loader's own for this
    folder if not given; OPTIONS are dosboxx.conf_lines')."""
    settings = load_settings() if settings is None else settings
    if dosboxx.engine(settings) == dosboxx.DOSBOX_X:
        path = path or DBX_CONF
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        lines = dosboxx.conf_lines(
            game_dir, DOS_DIR, memory_file or dosboxx.memory_path(HERE, settings), settings, dice_log,
            picture(settings), (UMB_PLUS_COM, PATCHED_EXE, GAME_END_COM), options)
        return _write_conf_file(path, lines, "DOSBox-X")
    path = path or CONF
    lines = display_lines(settings) + cpu_lines(settings) + midiout.conf_lines(settings)
    if dice_log:  # (EMS's 64 KB page frame sits where DSCLOG loads; the game takes XMS without it)
        lines += DOS_LINES
    lines += ["[autoexec]", "@echo off", "cls", 'mount c ".."']
    if os.path.isdir(os.path.join(game_dir, "cloud_saves")):
        lines.append(r'mount C "..\cloud_saves" -t overlay')  # where GOG keeps the saves
    lines += [f'mount d "{DOS_DIR}"', "c:"]
    # the game runs from C: (the game folder), where the patched copy looks for its files
    # (UMBPLUS.COM first: DOSBox 0.74's upper memory from CA00h, not D000h, 24 KB more for DSCLOG)
    lines += ["d:\\" + UMB_PLUS_COM.lower(), r"lh d:\dsclog.exe", "cls",
              "d:\\" + PATCHED_EXE.lower()] if dice_log else ["darksun"]
    # a game that stops with an error ("Null pointer assignment", "Stack overflow!") leaves its
    # message on screen until a key is pressed, rather than DOSBox closing over it, and saved for
    # the crash report (GAMEEND.COM: the screen's text, or a return code other than 0)
    lines += ["d:\\" + GAME_END_COM.lower(), "exit", ""]
    return _write_conf_file(path, lines, "DOSBox")


def _write_conf_file(path: str, lines: List[str], name: str) -> str:
    """LINES written as the configuration file PATH, in the encoding NAME (DOSBox, DOSBox-X) reads."""
    encoding = conf_encoding()
    try:
        data = "\n".join(lines).replace("\n", "\r\n").encode(encoding)
    except UnicodeEncodeError as e:
        line = e.object[e.object.rfind("\n", 0, e.start) + 1:].split("\r", 1)[0]  # (the mount naming it)
        raise LaunchError(f"{name} can't be given a folder whose path has {e.object[e.start:e.end]!r} in it "
                          f"({line}): its configuration is read in Windows' code page ({encoding}), which "
                          "hasn't those letters. Move the game, or the Obsidian Edition folder, to a folder "
                          "whose path has only letters of that code page.") from None
    with open(path, "wb") as f:
        f.write(data)
    return path


def conf_encoding() -> str:
    """The encoding DOSBox reads its configuration in: Windows' ANSI code page there ("mbcs"), else
    UTF-8."""
    return "mbcs" if os.name == "nt" else "utf-8"


# The Options tab's new content and game changes (settings keys), each on unless switched off;
# the game's copies are written with them as they stand when it is started (the game changes with
# no switch, game.ALWAYS_ON, are always in: none of them here)
CONTENT = ("kalzith", "semyon", "vulture", "pens_gear", "magic_arms", "world_gear", "world_magic", "arena_ring",
           "steady_pace")
# the new items' parts (worldgear.data_chunks', and the arena's ring, ring.py), all switched by
# one box: NEW_ITEMS
ITEM_PARTS, NEW_ITEMS = ("pens_gear", "magic_arms", "world_gear", "world_magic", "arena_ring"), "new_items"


def content(settings: dict) -> dict:
    """{key: on} for each of CONTENT (on unless the settings say False; the new items' parts as
    NEW_ITEMS is)."""
    items = settings.get(NEW_ITEMS, True) is not False
    return {key: items if key in ITEM_PARTS else settings.get(key, True) is not False for key in CONTENT}


# what the last prepare_patched_game couldn't make, each "PART (FILE: why)": the game then runs with the
# game's own file there, and a save that has the mod's objects or scripts in it may not load
LEFT_OUT: List[str] = []


def left_out_line() -> Optional[str]:
    """A line for the player on what LEFT_OUT holds, or None if nothing was left out."""
    if not LEFT_OUT:
        return None
    return ("Started without " + "; ".join(LEFT_OUT) + ". The game runs on its own files there, and a save "
            "made with them may not load: start the game again once the cause is put right.")


def prepare_patched_game(game_dir: str, settings: Optional[dict] = None) -> Optional[str]:
    """Write DSUNLOG.EXE next to DSCLOG.EXE, and the copies of the game's files with the
    companion's additions: SEGOBJEX.GFF with its item icons (icons.py; without it the items keep
    the plain icons) and Kalzith's object, RESOURCE.GFF with Cat's Grace's icon, GPLDATA.GFF and
    RGN29.GFF with Kalzith (kalzith.py), each addition only if switched on in SETTINGS (CONTENT;
    the saved settings if none given). Returns why the game can't be patched, or None; what of the
    copies couldn't be made is in LEFT_OUT (left_out_line), for the player to be told."""
    del LEFT_OUT[:]
    from . import alagorn
    del alagorn.LEFT_OUT[:]  # (an earlier start's: its scripts written only with some switches on)
    chosen = load_settings(strict=True) if settings is None else settings
    on = content(chosen)
    # (every patch group in, but Steady pace's when it is unticked: the others' switches went after
    # 2.18, game.ALWAYS_ON)
    skip = frozenset() if on["steady_pace"] else frozenset(gamepatch.STEADY_PACE)
    source = _find_file(game_dir, "DSUN.EXE")
    if source is None:  # (gone since the folder was picked: said, not a TypeError)
        return f"{game_dir} has no DSUN.EXE"
    try:
        gamepatch.write_patched(source, os.path.join(DOS_DIR, PATCHED_EXE), skip)
    except (gamepatch.PatchError, OSError) as e:
        return str(e)
    objects_ok, new_objects, kalzith_object = False, (), False
    try:
        objects = _find_file(game_dir, icons.OBJECTS_FILE)
        if objects:
            objects_ok, new_objects, kalzith_object = icons.write_objects(
                objects, os.path.join(DOS_DIR, icons.OBJECTS_FILE), on)
            if not objects_ok:  # (not written, though nothing raised: said, not dropped unseen)
                LEFT_OUT.append(f"the new items, people and icons ({icons.OBJECTS_FILE}: not written)")
        else:
            LEFT_OUT.append(f"the new items, people and icons ({icons.OBJECTS_FILE}: not in the game's folder)")
    except (gff.GffError, OSError, KeyError, struct.error, ValueError, IndexError) as e:
        LEFT_OUT.append(f"the new items, people and icons ({icons.OBJECTS_FILE}: {e})")
    if not objects_ok:  # (an earlier start's copy taken away: DSCLOG would open it in place of the
        _drop(os.path.join(DOS_DIR, icons.OBJECTS_FILE))  # game's, made with other switches)
    # the regions with a person given an object of their own for a new item (worldgear.py): only
    # with that object in the objects copy (a region naming an object that isn't there would stop
    # the game)
    # (the slave pens' clones go into Kalzith's copy of the pens, when he's in it: one copy)
    with_kalzith = on["kalzith"] and objects_ok and kalzith_object
    if on["kalzith"] and objects_ok and not kalzith_object:  # (the rest of the copy kept)
        LEFT_OUT.append(f"Kalzith, the slave pens' defiler ({icons.OBJECTS_FILE}: his object couldn't be "
                        "made in this copy of the game)")
    gifts = (worldgear.GIFTS if on["world_gear"] else ()) + (worldgear.MAGIC if on["world_magic"] else ())
    pens_clones = [g for g in gifts if g.region == kalzith.REGION and g.clone and g.clone[1] in new_objects]
    for region in worldgear.regions(worldgear.GIFTS + worldgear.MAGIC):
        if region == kalzith.REGION and with_kalzith:
            continue
        name, dest = worldgear.region_file(region), os.path.join(DOS_DIR, worldgear.region_file(region))
        mine = [g for g in gifts if g.region == region and g.clone and g.clone[1] in new_objects]
        try:
            source = _find_file(game_dir, name)
            if mine and source:
                worldgear.write_region(source, dest, region, mine)
            elif os.path.exists(dest):
                os.remove(dest)
        except (gff.GffError, OSError, KeyError, struct.error, ValueError, IndexError, gpl.ScriptError) as e:
            LEFT_OUT.append(f"the gifts placed in {name} ({e})")
            try:
                os.remove(dest)
            except OSError:
                pass
    # Kalzith, the slave pens' defiler: in his pen and with his conversation only if the objects
    # copy has him too (the pens naming an object that isn't there would stop the game)
    # (Semyon, the vulture and the pens' questions are in the scripts' copy too: with Kalzith off,
    # or no objects copy with him, it is written without him, and the pens' region is the game's)
    files = [(kalzith.SCRIPTS_FILE, lambda source, dest: kalzith.write_scripts(
        source, dest, with_kalzith, on["semyon"], on["vulture"], on["arena_ring"],
        on["magic_arms"] and objects_ok, on["world_magic"] and objects_ok,
        worldgear.ELVEN_CLOAK_OBJECT in new_objects, tome.TOME_OBJECT in new_objects,
        on["pens_gear"] and objects_ok, worldgear.HAYNEEDLE_OBJECT in new_objects,
        champions.TOHR_KREEN in new_objects))]  # (Alagorn knows
    # the weapons by their own pictures; the Elven Leader gives the cloak, Father Garyn the tome and
    # Merzol's hay stash Hayneedle, of its own object)
    if with_kalzith:
        files.append((kalzith.REGION_FILE, lambda source, dest: kalzith.write_region(source, dest, pens_clones)))
    try:
        for name, write in files:
            source = _find_file(game_dir, name)
            if not source:
                raise OSError(f"no {name}")
            write(source, os.path.join(DOS_DIR, name))
        LEFT_OUT.extend(alagorn.LEFT_OUT)  # (a story menu of Alagorn's too long for the game's scripts: told)
        if not with_kalzith and not pens_clones:
            try:
                os.remove(os.path.join(DOS_DIR, kalzith.REGION_FILE))
            except FileNotFoundError:
                pass  # (no region copy to take away)
    except (gff.GffError, OSError, KeyError, struct.error, ValueError, IndexError, gpl.ScriptError) as e:
        # (RGN29's copy goes with them, and with it the pens' gifts it held, Kalzith's copy or, with
        # him off, the region's own: said too, not dropped unseen)
        gifts_too = f"; with it the gifts placed in {kalzith.REGION_FILE}" if pens_clones else ""
        LEFT_OUT.append(f"the new scripts: Kalzith, Semyon, the new people's talk ({kalzith.SCRIPTS_FILE}: {e})"
                        + gifts_too)
        for name in (kalzith.SCRIPTS_FILE, kalzith.REGION_FILE):  # (all or nothing: the game's own)
            try:
                os.remove(os.path.join(DOS_DIR, name))
            except OSError:
                pass
    # the game's own arrow for the scenes' pointer (DSCLOG's, without it)
    scenepointer.write_pointer(_find_file(game_dir, icons.RESOURCE_FILE), _find_file(game_dir, "GPLDATA.GFF"),
                               os.path.join(DOS_DIR, scenepointer.POINTER_FILE))
    resources_ok = False
    try:
        resources = _find_file(game_dir, icons.RESOURCE_FILE)
        if resources:
            icons.write_resources(resources, os.path.join(DOS_DIR, icons.RESOURCE_FILE))
            resources_ok = True
    except (gff.GffError, OSError, KeyError, struct.error, ValueError, IndexError) as e:
        LEFT_OUT.append(f"the new spells' icons and texts ({icons.RESOURCE_FILE}: {e})")
    if not resources_ok:  # (as the objects' copy: no earlier start's in its place)
        _drop(os.path.join(DOS_DIR, icons.RESOURCE_FILE))
    return None


def _drop(path: str) -> None:
    """PATH taken away if it is there (a copy the game must not open)."""
    try:
        os.remove(path)
    except OSError:
        pass


# One Loader at a time for this mod's game: the window, `play` and `dicelog` each take GAME_LOCK
# before starting the game or attaching to it, and keep it while the game runs or they follow it.
# Two at once would both make the game's changes (pickpockets, Kalzith's loot, gifts: twice) and one
# would rewrite the dos folder's copies under the other's running game. The lock is the operating
# system's on the file (Windows: msvcrt.locking; elsewhere fcntl.flock), so it goes with the process
# that held it, however that ended: a lock file left by a crash is no lock. The file holds the
# holder's pid and what it is, for the message; where the system can't lock the file (some network
# drives), that pid is checked instead, and a dead one's file taken over.
GAME_LOCK = os.path.join(HERE, "game.lock")
_LOCK_AT = 1 << 20  # (Windows locks bytes: one far past the pid's line, so the line can still be read)


class GameBusy(LaunchError):
    """Another Loader (or `play`, or `dicelog`) has the game."""


_HELD: Dict[str, object] = {}  # {"fd": the lock file's descriptor, "path": it, "what": the holder}


def _kernel32():
    """kernel32 with the process calls' types set (a HANDLE is pointer-sized: not cut to a C int)."""
    import ctypes
    from ctypes import wintypes
    k32 = ctypes.WinDLL("kernel32", use_last_error=True)
    k32.OpenProcess.restype = wintypes.HANDLE
    k32.OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
    k32.GetExitCodeProcess.restype = wintypes.BOOL
    k32.GetExitCodeProcess.argtypes = (wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD))
    k32.CloseHandle.restype = wintypes.BOOL
    k32.CloseHandle.argtypes = (wintypes.HANDLE,)
    k32.QueryFullProcessImageNameW.restype = wintypes.BOOL
    k32.QueryFullProcessImageNameW.argtypes = (wintypes.HANDLE, wintypes.DWORD, wintypes.LPWSTR,
                                               ctypes.POINTER(wintypes.DWORD))
    return k32


def pid_alive(pid: int) -> bool:
    """Whether a process PID runs (for a lock file the system couldn't lock)."""
    if pid <= 0:
        return False
    if os.name == "nt":
        import ctypes
        from ctypes import wintypes
        k32 = _kernel32()
        handle = k32.OpenProcess(0x1000, False, pid)  # (PROCESS_QUERY_LIMITED_INFORMATION)
        if not handle:
            return ctypes.get_last_error() == 5  # (access denied: there, someone else's)
        try:
            code = wintypes.DWORD()
            return bool(k32.GetExitCodeProcess(handle, ctypes.byref(code))) and code.value == 259  # STILL_ACTIVE
        finally:
            k32.CloseHandle(handle)
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return False
    return True


def process_name(pid: int) -> Optional[str]:
    """The file name of the program process PID runs (lower case, "dosbox.exe"), or None if it
    can't be told (gone, someone else's, or no way to ask on this system)."""
    if pid <= 0:
        return None
    if os.name == "nt":
        import ctypes
        from ctypes import wintypes
        k32 = _kernel32()
        handle = k32.OpenProcess(0x1000, False, pid)
        if not handle:
            return None
        try:
            size = wintypes.DWORD(1024)
            buf = ctypes.create_unicode_buffer(size.value)
            if not k32.QueryFullProcessImageNameW(handle, 0, buf, ctypes.byref(size)):
                return None
            return os.path.basename(buf.value).lower() or None
        finally:
            k32.CloseHandle(handle)
    try:
        return os.path.basename(os.readlink(f"/proc/{pid}/exe")).lower() or None
    except OSError:
        return None


def game_alive(pid: int, name: str) -> bool:
    """Whether the game a Loader started (GAME_LOCK's game line: its PID and program's NAME) still
    runs: the pid alive, and running that program where the system says which (a pid reused by
    another program since is not the game)."""
    if not pid_alive(pid):
        return False
    now = process_name(pid)
    return now is None or not name or now == name.lower()


def _lock_file(fd: int) -> Optional[bool]:
    """The system's lock on FD: True taken, False held by another process, None if the system
    can't lock it."""
    import errno
    try:
        if os.name == "nt":
            import msvcrt
            os.lseek(fd, _LOCK_AT, os.SEEK_SET)
            msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return True
    except OSError as e:
        if e.errno in (errno.EACCES, errno.EAGAIN, errno.EWOULDBLOCK, getattr(errno, "EDEADLOCK", errno.EDEADLK)):
            return False
        return None


def lock_holder(path: Optional[str] = None) -> Tuple[int, str]:
    """(pid, what) the lock file names (0, "" if none)."""
    try:
        with open(path or GAME_LOCK, encoding="utf-8", errors="replace") as f:
            pid, _, what = f.readline().strip().partition(" ")
        return int(pid), what
    except (OSError, ValueError):
        return 0, ""


GAME_LINE = "game"  # (the lock file's second line: "game PID PROGRAM", the game the holder started)
MEMORY_LINE = "memory"  # (its third, for a game in DOSBox-X: "memory PATH", that game's memory file)


def lock_memory(path: Optional[str] = None) -> str:
    """The memory file the lock file says its game has (DOSBox-X's: dosboxx.py), or ""."""
    try:
        with open(path or GAME_LOCK, encoding="utf-8", errors="replace") as f:
            for line in f.read().splitlines()[1:]:
                word, _, rest = line.strip().partition(" ")
                if word == MEMORY_LINE and rest:
                    return rest
    except OSError:
        pass
    return ""


def memory_game(path: Optional[str] = None) -> Tuple[int, str]:
    """(pid, memory file) of the DOSBox-X game started from this folder if it still runs and has a
    memory file; (0, "") otherwise."""
    pid = running_game(path)
    memory = lock_memory(path) if pid else ""
    return (pid, memory) if pid and memory else (0, "")


def game_memory_file(pid: int) -> str:
    """The memory file of the game running as process PID, if it is a DOSBox-X this Loader (or one
    before it, from this folder) started with one, or one whose own configuration names one
    (dosboxx.process_memory_file: a DOSBox-X started by the playtest kit); "" for a DOSBox 0.74
    or anything else, whose memory is read from its process."""
    if isinstance(_HELD.get("game"), tuple) and _HELD["game"][0] == pid and _HELD.get("memory"):
        return str(_HELD["memory"])
    known, memory = memory_game()
    if known == pid and memory:
        return memory
    from .process import is_dosbox_x
    if is_dosbox_x(process_name(pid) or ""):
        return dosboxx.process_memory_file(pid) or ""
    return ""


def lock_game(path: Optional[str] = None) -> Tuple[int, str]:
    """(pid, program) of the game the lock file says was started (0, "" if none)."""
    try:
        with open(path or GAME_LOCK, encoding="utf-8", errors="replace") as f:
            f.readline()
            word, _, rest = f.readline().strip().partition(" ")
        if word != GAME_LINE:
            return 0, ""
        pid, _, name = rest.partition(" ")
        return int(pid), name
    except (OSError, ValueError):
        return 0, ""


def running_game(path: Optional[str] = None) -> int:
    """The pid of the game a Loader started from this folder if it still runs (the Loader that
    started it closed since, or this one), else 0."""
    pid, name = lock_game(path)
    return pid if pid and game_alive(pid, name) else 0


def game_running_line(pid: int) -> str:
    return (f"The game started from this Obsidian Edition folder earlier is still running (process {pid}), "
            "though the Loader that started it has closed. Close that game first: starting it again now "
            "would write the mod's files under it.")


def busy_line(pid: int, what: str) -> str:
    """Why the game can't be started or followed here: another holds it."""
    who = f"{what} (process {pid})" if what and pid else (f"process {pid}" if pid else "another Loader")
    return (f"The game is already started or followed by {who}, from this Obsidian Edition folder. Only one may "
            "start it or follow it at a time: close that one (or the game it started) first.")


def hold_game(what: str, path: Optional[str] = None) -> None:
    """Take the game's lock for this process (WHAT: who holds it, for another's message); nothing if
    this process holds it already. Raises GameBusy, naming the holder, if another process does."""
    path = path or GAME_LOCK
    if _HELD.get("path") == path:
        return
    while True:
        try:
            fd = os.open(path, os.O_RDWR | os.O_CREAT, 0o644)
        except OSError:  # (a folder that can't be written: no lock to be had, and none kept from the player)
            return
        taken = _lock_file(fd)
        if taken is False:
            os.close(fd)
            raise GameBusy(busy_line(*lock_holder(path)))
        if taken is None:  # (no system lock here: the pid in the file says)
            pid, holder = lock_holder(path)
            if pid and pid != os.getpid() and pid_alive(pid):
                os.close(fd)
                raise GameBusy(busy_line(pid, holder))
        if os.name != "nt":  # (taken from a file another took away and made anew since: try again)
            try:
                if os.stat(path).st_ino != os.fstat(fd).st_ino:
                    os.close(fd)
                    continue
            except FileNotFoundError:
                os.close(fd)
                continue
        break
    game = lock_game(path)  # (a game a closed Loader started, still running: its line kept)
    alive = bool(game[0]) and game_alive(*game)
    memory = lock_memory(path)
    if memory and not alive:  # (a DOSBox-X game that ended with no Loader watching: its file left behind)
        dosboxx.remove_memory_file(memory)
    _HELD.update(fd=fd, path=path, what=what, game=game if alive else (0, ""), memory=memory if alive else "")
    _write_lock()


def _write_lock() -> None:
    """The held lock file's lines: this process and what it is; the game it (or a Loader before
    it) started, if any."""
    fd = _HELD["fd"]
    pid, name = _HELD.get("game", (0, ""))
    text = f"{os.getpid()} {_HELD['what']}\n" + (f"{GAME_LINE} {pid} {name}\n" if pid else "")
    if pid and _HELD.get("memory"):
        text += f"{MEMORY_LINE} {_HELD['memory']}\n"
    try:
        os.lseek(fd, 0, os.SEEK_SET)
        os.ftruncate(fd, 0)
        os.write(fd, text.encode("utf-8"))
    except OSError:
        pass


def note_game(pid: int, program: str, memory: str = "") -> None:
    """The game this process started (its pid and program; MEMORY its memory file, for one in
    DOSBox-X) written in the held lock file: while it runs, no Loader starts the game again from
    this folder (running_game), even once this one has let the lock go (the window closed with the
    game still running), and a Loader opened later finds its memory (memory_game)."""
    if "fd" in _HELD:
        _HELD["game"] = (pid, os.path.basename(os.path.realpath(program)).lower() if program else "")
        _HELD["memory"] = memory
        _write_lock()


def release_game() -> None:
    """Let the game's lock go (nothing if this process doesn't hold it); its file taken away."""
    fd, path = _HELD.pop("fd", None), _HELD.pop("path", None)
    _HELD.pop("what", None)
    game = _HELD.pop("game", (0, ""))
    memory = _HELD.pop("memory", "")
    if fd is None:
        return
    keep = bool(game[0]) and game_alive(*game)  # (the game still runs: its line stays for the next Loader)
    if memory and not keep:  # (the game in DOSBox-X has ended: its memory file goes)
        dosboxx.remove_memory_file(str(memory))
    try:
        if os.name != "nt" and not keep:
            os.remove(path)  # (while still locked: no one takes the file being removed)
    except OSError:
        pass
    try:
        if os.name == "nt":
            import msvcrt
            try:
                os.lseek(fd, _LOCK_AT, os.SEEK_SET)
                msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
            except OSError:
                pass
        os.close(fd)
    except OSError:
        pass
    if os.name == "nt" and not keep:
        try:
            os.remove(path)  # (fails while another has it open: it is theirs then)
        except OSError:
            pass


def holds_game() -> bool:
    """Whether this process holds the game's lock."""
    return "fd" in _HELD


# Windows' codes for a program that crashes (DOSBox itself, not the game in it)
CRASH_CODES = {0xC0000005: "an access violation", 0xC00000FD: "a stack overflow", 0xC0000409: "a stack buffer overrun"}


# what launch() last started: the recompiled program's path, or None for DOSBox (closed_line,
# started_line: by what was started, not by what the settings say now)
STARTED: Optional[str] = None
# ... and, when it was DOSBox, which: GOG's 0.74 (dosboxx.GOG) or the player's DOSBox-X, and that
# one's program
STARTED_ENGINE: str = dosboxx.GOG
STARTED_DOSBOX_X: Optional[str] = None


def engine_name() -> str:
    """What launch() last started, as the log names it."""
    if STARTED:
        return "Dark Sun Recompiled"
    return dosboxx.NAME if STARTED_ENGINE == dosboxx.DOSBOX_X else "DOSBox"


def started_line(game_dir: str) -> str:
    """The log's line for the game started from GAME_DIR: in DOSBox, in DOSBox-X (which program),
    or as Dark Sun Recompiled (which program), so a player sees which one runs."""
    if STARTED:
        return f"Starting Shattered Lands from {game_dir} as Dark Sun Recompiled ({STARTED})."
    if STARTED_ENGINE == dosboxx.DOSBOX_X:
        return f"Starting Shattered Lands from {game_dir} in DOSBox-X ({STARTED_DOSBOX_X})."
    return f"Starting Shattered Lands from {game_dir} in DOSBox."


def closed_line(code: int) -> str:
    """The log's line for DOSBox (or DOSBox-X, or the recompiled program, if that was started)
    closing with exit code CODE."""
    name = engine_name()
    if code == 0:
        return f"{name} closed."
    if code < 0 and code & 0xFFFFFFFF not in CRASH_CODES:  # (not Windows: ended by a signal)
        return f"{name} closed: it was ended by signal {-code}" + (
            " (killed)." if code in (-9, -15) else f". That is {name} itself failing, not the game stopping "
            "with an error.")
    known = CRASH_CODES.get(code & 0xFFFFFFFF)
    if known:
        return (f"{name} closed: it crashed ({known}, code {code & 0xFFFFFFFF:08X}h). That is {name} "
                "itself failing, not the game stopping with an error.")
    return f"{name} closed with exit code {code}."


# GAMEEND.COM, run after the game, notes in GAMEEND.TXT (in DOS_DIR) how the game stopped with an
# error; the Loader's crash reports go in CRASH_DIR
GAME_END_COM = "GAMEEND.COM"
UMB_PLUS_COM = "UMBPLUS.COM"  # (dos/umbplus.asm)
GAME_END = os.path.join(DOS_DIR, "GAMEEND.TXT")
# and in GAMEOK.TXT that it ended as usual: without either, DOSBox closed while the game still ran
GAME_OK = os.path.join(DOS_DIR, "GAMEOK.TXT")
CUT_OFF = ("The game didn't end on its own: DOSBox closed while it was still running (closed with its "
           "window's button, or after the game froze, or DOSBox stopped with an error of its own).")
CRASH_DIR = os.path.join(HERE, "crash-logs")
DOSBOX_OUTPUT = ("stdout.txt", "stderr.txt")  # DOSBox's own messages with -noconsole (its folder)


# DSCLOG's GAMEMSG.BIN (DOS_QUIT): the game's last text to the screen and its stack as it quit
# with an error code ("GMSG", the code, the load segment, SS, SP, MSG_STACK bytes, the text's
# length, the text)
GAME_MESSAGE = os.path.join(DOS_DIR, "GAMEMSG.BIN")
MSG_STACK = 256
DGROUP_SEG = 0x4356  # (the game's code segments lie below its data, from its load segment)
EXE_HEADER = 0x5400


def game_message(data: bytes) -> Optional[str]:
    """GAMEMSG.BIN as lines for the crash report: what the game printed (its fatal error's text,
    which the game clears from the screen as it quits), and the far calls' ways back on its stack
    as places in DSUN.EXE (each a guess: any word pair that looks like one), or None."""
    head = 4 + 1 + 2 + 2 + 2
    if len(data) < head + MSG_STACK + 2 or data[:4] != b"GMSG":
        return None
    code, load, ss, sp = struct.unpack_from("<BHHH", data, 4)
    stack = data[head:head + MSG_STACK]
    size, = struct.unpack_from("<H", data, head + MSG_STACK)
    text = data[head + MSG_STACK + 2:head + MSG_STACK + 2 + size].decode("cp437", "replace")
    text = "\n".join(line.rstrip() for line in text.replace("\r", "").splitlines()).strip()
    lines = [f"The game quit with code {code}. What it last wrote to the screen:",
             text or "(nothing)"]
    places = []
    for at in range(0, MSG_STACK - 3, 2):
        ip, cs = struct.unpack_from("<HH", stack, at)
        if load <= cs < load + DGROUP_SEG and ip >= 5 and not any(f"{cs - load:04X}:{ip:04X})" in p for p in places):
            places.append(f"DSUN {(cs - load) * 16 + ip + EXE_HEADER:X}h (+{at:02X}: {cs - load:04X}:{ip:04X})")
    lines += ["", f"Its stack (SS:SP {ss:04X}:{sp:04X}, load segment {load:04X}), the ways back it seems to hold:"]
    lines += ["  " + p for p in places] or ["  (none)"]
    lines += ["  " + stack[i:i + 32].hex(" ") for i in range(0, MSG_STACK, 32)]
    return "\n".join(lines)


def game_end_note() -> Optional[str]:
    """What GAMEEND.COM saved of the game stopping with an error (its return code, video mode,
    and the screen's text), and DSCLOG's GAMEMSG.BIN (game_message); CUT_OFF if neither and
    GAMEEND.COM didn't note it ending as usual either (GAME_OK); None if it ended as usual."""
    notes = []
    try:
        with open(GAME_END, encoding="cp437", errors="replace") as f:
            notes.append(f.read().rstrip())
    except OSError:
        pass
    try:
        with open(GAME_MESSAGE, "rb") as f:
            message = game_message(f.read())
        if message:
            notes.append(message)
    except OSError:
        pass
    if not notes and STARTED is None and not os.path.exists(GAME_OK):  # (DOSBox's GAMEEND.COM writes it;
        notes.append(CUT_OFF)                                           #   the recompiled program has none)
    return "\n\n".join(notes) or None


def dosbox_output(game_dir: str, since: float) -> Dict[str, str]:
    """DOSBox's stdout.txt and stderr.txt (in its folder; only read) written since SINCE; for a
    game in DOSBox-X, what it printed (DBX_LOG, which the Loader keeps)."""
    out: Dict[str, str] = {}
    if STARTED_ENGINE == dosboxx.DOSBOX_X and not STARTED:
        try:
            if os.path.getmtime(DBX_LOG) >= since - 1:
                with open(DBX_LOG, encoding="utf-8", errors="replace") as f:
                    out["output (dosbox-x.log)"] = f.read()[-20000:].rstrip()
        except OSError:
            pass
        return out
    folder = _find_file(game_dir, "DOSBOX") if game_dir else None
    for name in DOSBOX_OUTPUT if folder else ():
        path = _find_file(folder, name)
        try:
            if path and os.path.getmtime(path) >= since:
                with open(path, encoding="utf-8", errors="replace") as f:
                    out[name] = f.read()[-20000:].rstrip()
        except OSError:
            pass
    return out


# The Options tab's switches and their defaults (what a key missing from settings.json means)
SWITCH_DEFAULTS = {"monster_info": True, "floating_names": True, "starting_gear": True, "rings": "chosen",
                   "hit_chance": True, "hit_hover": True, "squares": True, "move_back": True, "show_usable": True, "quick_save": True, "autosave": True,
                   "cycles": DEFAULT_SPEED, "picture": DEFAULT_PICTURE, midiout.SETTING: midiout.DEFAULT,
                   dosboxx.SETTING: dosboxx.GOG,
                   "combat_log_level": "short", "defiler_scrolls": True, NEW_ITEMS: True}  # (combatlog.SHORT, the panel's level unless chosen)


def effective_switches(settings: dict) -> Dict[str, object]:
    """Every switch as the Loader uses it: as set, else its default (rule changes and content: on)."""
    from . import game
    out: Dict[str, object] = {key: settings.get(key, default) for key, default in SWITCH_DEFAULTS.items()}
    out.update({key: on for key, on in content(settings).items() if key not in game.ALWAYS_ON})
    out.update({key: game.setting_on(settings, key)
                for key, _ in game.RULE_SETTINGS})  # (as game.rules_from_settings reads them)
    from . import dicelog, rings
    out["rings"] = rings.mode(settings)  # (an older "all" is the chosen enemy's now)
    out["combat_log_level"] = dicelog.combat_log_level(settings)
    out["picture"] = picture(settings)  # (as DOSBox is asked for it: plain where the window has no other)
    out[midiout.SETTING] = midiout.setting(settings)
    out[dosboxx.SETTING] = dosboxx.engine(settings)
    return out


def crash_report(code: int, note: Optional[str], settings: dict, dice: str, dialogue: str,
                 refused: List[str], output: Dict[str, str], started: float, now: float) -> str:
    """The text of a crash report: how DOSBox closed, what the game left on screen, the switches,
    and the end of the dice log and the dialogue."""
    stamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(now))
    lines = [f"Obsidian Edition crash report, {stamp}", "", closed_line(code)]
    if started:
        lines.append(f"The game ran for {round((now - started) / 60)} minutes.")
    if note == CUT_OFF:
        lines += ["", note]
    elif note:
        lines += ["", "The game stopped with an error. On the screen:", note]
    from . import heapcheck
    memory = heapcheck.WATCH.lines()
    if memory:
        lines += [""] + memory
    lines += ["", "Switches (as set on the Options tab, else the default):"]
    lines += [f"  {key}: {value!r}" for key, value in sorted(effective_switches(settings).items())]
    if refused:
        lines += ["", "Writes the Loader refused (a pointer read while the game had it empty):"]
        lines += ["  " + r for r in refused[-50:]]
    for name, text in output.items():
        lines += ["", f"DOSBox's {name}:", text]
    lines += ["", "The dice log's last lines:", _last_lines(dice, 300),
              "", "The dialogue's last lines:", _last_lines(dialogue, 80), ""]
    return "\n".join(lines)


def _last_lines(text: str, count: int) -> str:
    return "\n".join(text.rstrip().splitlines()[-count:]) or "(empty)"


def write_crash_report(text: str, now: float, folder: str = CRASH_DIR, kind: str = "crash") -> str:
    """Save a report as crash-logs/crash-YYYY-MM-DD-HHMMSS.txt (a number after it if there is one
    already; KIND names it: "item" for a lost item's, itemwatch.py); returns its path."""
    os.makedirs(folder, exist_ok=True)
    stem = os.path.join(folder, time.strftime(f"{kind}-%Y-%m-%d-%H%M%S", time.localtime(now)))
    path, n = stem + ".txt", 1
    while os.path.exists(path):  # (two in the same second)
        n += 1
        path = f"{stem}-{n}.txt"
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return path


def launch(game_dir: str, what: str = "the Loader") -> Tuple[subprocess.Popen, Optional[str]]:
    """Start the game. Returns DOSBox's process (or the recompiled program's) and, if the dice log
    can't run, why. Takes the game's lock first (hold_game, WHAT naming this Loader): GameBusy if
    another has the game; the caller lets it go (release_game) once the game has closed. Raises
    LaunchError, too, when settings.json is there but can't be read: the copies are built by the
    player's switches, never by the defaults in their place."""
    game_dir = os.path.abspath(game_dir)  # (DOSBox runs in its own folder: a relative path would miss)
    try:
        settings = load_settings(strict=True, tries=40)  # (two seconds: held a moment, then read)
    except SettingsUnreadable as e:
        raise LaunchError(f"{e.strerror}, so the game isn't started with the wrong options: start it "
                          "again in a moment.") from None
    global LAST_SETTINGS
    held = holds_game()
    hold_game(what)
    try:
        running = running_game(_HELD.get("path"))  # (one a closed Loader started: its files in use)
        if running:
            raise GameBusy(game_running_line(running))
        proc, problem = _launch(game_dir, settings)
    except BaseException:
        if not held:
            release_game()  # (nothing started: nothing held)
        raise
    args = proc.args if isinstance(proc.args, (list, tuple)) else [proc.args]
    note_game(proc.pid, str(args[0]) if args else "", MEMORY_FILE or "")
    LAST_SETTINGS = settings
    return proc, problem


# the settings launch() last started the game with, read strictly (the dice log's switches and rules
# for `play`, as the copies were built: never a second read that could find the file held)
LAST_SETTINGS: Optional[dict] = None


# the memory file of the DOSBox-X game launch() last started (None: not DOSBox-X)
MEMORY_FILE: Optional[str] = None


def _launch_dosbox_x(game_dir: str, settings: dict) -> Tuple[subprocess.Popen, Optional[str]]:
    """The game started in the player's DOSBox-X (dosboxx.py): its configuration written whole,
    its memory file named (an earlier game's taken away first), what it prints kept in DBX_LOG."""
    global STARTED, STARTED_ENGINE, STARTED_DOSBOX_X, MEMORY_FILE
    wrong = dosboxx.problem(settings)
    if wrong:
        raise LaunchError(wrong)
    if not _find_file(game_dir, "DSUN.EXE"):
        raise LaunchError(f"{game_dir} has no DSUN.EXE; pick the game's folder")
    program = os.path.abspath(settings[dosboxx.PATH_SETTING])
    problem = prepare_patched_game(game_dir, settings)
    for old in (GAME_END, GAME_MESSAGE, GAME_OK):  # (the last game's)
        _drop(old)
    memory = dosboxx.memory_path(HERE, settings)
    if not dosboxx.remove_memory_file(memory):  # (Windows: still open somewhere; DOSBox-X couldn't cut it)
        raise LaunchError(f"The memory file of an earlier game is still in use ({memory}): close the "
                          "DOSBox-X or the Loader that holds it, then start the game again.")
    conf = write_conf(game_dir, dice_log=problem is None, settings=settings, memory_file=memory)
    try:
        log = open(DBX_LOG, "wb")
    except OSError:
        log = None
    try:
        proc = subprocess.Popen([program] + dosboxx.arguments(conf), cwd=DBX_DIR, stdin=subprocess.DEVNULL,
                                stdout=log or subprocess.DEVNULL, stderr=subprocess.STDOUT)
    except OSError as e:
        raise LaunchError(f"DOSBox-X couldn't be started ({program}: {e.strerror or e}).") from None
    finally:
        if log is not None:
            log.close()  # (DOSBox-X has its own handle on it)
    STARTED, STARTED_ENGINE, STARTED_DOSBOX_X, MEMORY_FILE = None, dosboxx.DOSBOX_X, program, memory
    return proc, problem


def _launch(game_dir: str, settings: dict) -> Tuple[subprocess.Popen, Optional[str]]:
    global STARTED, STARTED_ENGINE, STARTED_DOSBOX_X, MEMORY_FILE
    STARTED_ENGINE, STARTED_DOSBOX_X, MEMORY_FILE = dosboxx.GOG, None, None
    if dosboxx.engine(settings) == dosboxx.DOSBOX_X:  # (the Options tab's engine: before the recompiled
        return _launch_dosbox_x(game_dir, settings)    #   program found beside the mod, a choice made there)
    program = recompiled_program(settings)
    if program is not None:
        if not _find_file(game_dir, "DSUN.EXE"):
            raise LaunchError(f"{game_dir} has no DSUN.EXE; pick the GOG install folder")
        problem = prepare_patched_game(game_dir, settings)
        if problem:
            raise LaunchError(f"The recompiled program runs the game with the helper, which needs the patched game ({problem}).")
        for old in (GAME_END, GAME_MESSAGE, GAME_OK):  # (the last game's)
            try:
                os.remove(old)
            except OSError:
                pass
        proc = subprocess.Popen(recompiled_command(program, game_dir), cwd=os.path.dirname(os.path.abspath(program)))
        STARTED = program
        return proc, None
    STARTED = None
    dosbox_dir = _find_file(game_dir, "DOSBOX")
    settings_conf = _find_file(game_dir, "dosbox_darksun.conf") or _find_file(
        os.path.join(game_dir, "__support", "app"), "dosbox_darksun.conf")
    if not dosbox_dir or not settings_conf:
        raise LaunchError(f"{game_dir} does not look like the GOG install of Shattered Lands")
    if not _find_file(game_dir, "DSUN.EXE"):
        raise LaunchError(f"{game_dir} has no DSUN.EXE; pick the GOG install folder")
    problem = prepare_patched_game(game_dir, settings)
    for old in (GAME_END, GAME_MESSAGE, GAME_OK):  # (the last game's)
        try:
            os.remove(old)
        except OSError:
            pass
    exe = _find_file(dosbox_dir, "DOSBox.exe")
    if exe is None:
        raise LaunchError(f"No DOSBox.exe in {dosbox_dir}")
    conf = write_conf(game_dir, dice_log=problem is None, settings=settings)
    return subprocess.Popen(
        [exe, "-conf", settings_conf, "-conf", conf, "-noconsole"],
        cwd=dosbox_dir), problem
