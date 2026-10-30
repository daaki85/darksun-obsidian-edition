"""Starting the GOG release of Shattered Lands with the dice log.

GOG runs DOSBox with two config files: dosbox_darksun.conf (settings) and
dosbox_darksun_single.conf (the [autoexec] that mounts the game and shows a
small menu). We keep the first and replace the second with our own
[autoexec], which also mounts the Loader's dos folder as D:, loads
DSCLOG.EXE into upper memory, and runs DSUNLOG.EXE: a patched copy of the
game (see gamepatch.py) that the launcher keeps in the dos folder. Nothing in
the game folder is changed.
"""

import json
import os
import string
import struct
import subprocess
import threading
import time
from typing import Dict, Iterator, List, Optional, Tuple

from . import gamepatch, gff, gpl, icons, kalzith, scenepointer, tome, worldgear

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOS_DIR = os.path.join(HERE, "dos")
HELPER = "DSCLOG.EXE"
SETTINGS = os.path.join(HERE, "settings.json")
CONF = os.path.join(HERE, "dosbox_dicelog.conf")
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
    is to run as Dark Sun Recompiled instead of in DOSBox)."""
    dosbox = _find_file(folder, "DOSBOX")
    if not _find_file(folder, "DSUN.EXE"):
        return False
    return bool(dosbox and _find_file(dosbox, "DOSBox.exe")) or recompiled_program() is not None


# Dark Sun Recompiled (github.com/daaki85/darksun-recompiled): the game translated into a program
# of its own, with the mod's patched game and its helper built in. The Loader starts that program
# instead of DOSBox when it finds it: unzipped into this folder (a "recompiled" subfolder, or its
# files here), or beside this folder ("darksun-recompiled..." next to it), or named in SETTINGS
# ("recompiled"; `dsloader launch --recompiled <path>` remembers a path, `--dosbox` turns the
# program off until `--recompiled` again). It is started with the game's folder (its data files;
# the game is recognised by its DSUN.EXE) and the mod's dos folder as drive D (DSUNLOG.EXE and
# the data files the helper replaces); it keeps its memory images (build/ds1o) beside itself.
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
    """Dark Sun Recompiled's program where a player would put it: in this folder, in a folder
    named after it, or beside this folder; None when there is none (a file of its name that is no
    program of the computer's own, the game's DOS DSUN.EXE above all, isn't it: native_program)."""
    import glob as _glob
    parent = os.path.dirname(here)
    candidates = [os.path.join(here, "recompiled", RECOMPILED_EXE), os.path.join(here, RECOMPILED_EXE),
                  os.path.join(parent, RECOMPILED_EXE)]
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


def upgrade_settings(settings: dict) -> bool:
    """Bring settings saved by an older Loader up to SETTINGS_VERSION; True if anything changed."""
    if not settings or settings.get("settings_version", 1) >= SETTINGS_VERSION:
        return False
    settings["combat_log"] = True
    settings["settings_version"] = SETTINGS_VERSION
    return True


# One read-modify-write of settings.json at a time (the window, and the thread reading the game,
# both change it: update_settings)
SETTINGS_LOCK = threading.RLock()


def load_settings(strict: bool = False) -> dict:
    """settings.json as a dict ({} if there is none). STRICT, for a read that is changed and saved
    again: a file that is there but can't be read now (Windows: open elsewhere for a moment, an
    antivirus or a backup) is tried again, and then raises OSError rather than read as empty, so
    the save after it can't put just the change in place of everything."""
    with SETTINGS_LOCK:
        for attempt in range(5):
            try:
                with open(SETTINGS, encoding="utf-8-sig") as f:  # (a BOM from Notepad too)
                    settings = json.load(f)
                break
            except FileNotFoundError:
                return {}
            except OSError:
                if not strict:
                    return {}
                if attempt == 4:
                    raise
                time.sleep(0.05)
            except ValueError:
                # (unreadable: kept aside as settings.json.bad, so the next save can't lose what it held)
                try:
                    os.replace(SETTINGS, SETTINGS + ".bad")
                except OSError:
                    pass
                return {}
        if not isinstance(settings, dict):
            return {}
        if upgrade_settings(settings):
            try:
                save_settings(settings)
            except OSError:
                pass  # (upgraded again next time)
        return settings


def save_settings(settings: dict) -> None:
    """Written whole or not at all: into settings.json.tmp, then put in settings.json's place."""
    settings["settings_version"] = SETTINGS_VERSION
    with SETTINGS_LOCK:
        tmp = SETTINGS + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
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


def update_settings(changes: dict) -> dict:
    """settings.json with CHANGES made, read and written as one step; the settings as saved."""
    with SETTINGS_LOCK:
        settings = load_settings(strict=True)
        settings.update(changes)
        save_settings(settings)
        return settings


def speaker_names() -> Dict[int, str]:
    """The names the player has given dialogue portraits: {portrait: name}."""
    names = load_settings().get("speakers", {})
    return {int(k): v for k, v in names.items() if str(k).isdigit() and isinstance(v, str) and v}


def set_speaker_name(portrait: int, name: str) -> None:
    """Remember a name for a portrait (an empty name forgets it)."""
    with SETTINGS_LOCK:
        _set_speaker_name(portrait, name)


def _set_speaker_name(portrait: int, name: str) -> None:
    settings = load_settings(strict=True)
    names = settings.setdefault("speakers", {})
    if name:
        names[str(portrait)] = name
    else:
        names.pop(str(portrait), None)
    save_settings(settings)


def learned_speakers() -> Dict[int, str]:
    """Portrait names the Loader worked out from conversations: {portrait: name}."""
    names = load_settings().get("speakers_learned", {})
    return {int(k): v for k, v in names.items() if str(k).isdigit() and isinstance(v, str) and v}


def pickpocketed() -> List[str]:
    """The pockets tried already (pickpocket.py), "key@game time" each: each person gets one try."""
    return list(load_settings().get("pickpocketed", []))


def set_pickpocketed(entries: List[str]) -> None:
    update_settings({"pickpocketed": list(entries)})



def add_learned_speakers(learned: Dict[int, str]) -> None:
    with SETTINGS_LOCK:
        settings = load_settings(strict=True)
        settings.setdefault("speakers_learned", {}).update({str(k): v for k, v in learned.items()})
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


def display_lines(settings: dict) -> List[str]:
    """DOSBox's display, over GOG's settings (full screen): a window, by default three times the
    game's 320x200 (960x720 with the aspect correction GOG turns on); `window_scale` 2 makes it
    twice, 4 four times, 1 leaves it at 320x240; `fullscreen` true keeps GOG's full screen.
    Alt+Enter switches either way in DOSBox. DOSBox 0.74 has no 4x scaler, so four times is
    DOSBox scaling the window itself, which needs its OpenGL output.
    With the pointer's start and speed (`mouse_start`, on unless switched off) the mouse's
    `sensitivity` is 100 over the scale: DOSBox moves the captured game's pointer a game pixel for
    each pixel the hand moves on the desktop, SCALE screen pixels in the window, so this makes it
    move as the desktop's pointer does (DSCLOG's MOUSE_RATIO allows for the taller pixels); the
    mouse is captured on a click (`autolock`, as GOG has it)."""
    if settings.get("fullscreen"):
        return []
    scale = settings.get("window_scale", DEFAULT_SCALE)
    scale = scale if scale in WINDOW_SCALES else DEFAULT_SCALE
    sdl = ["[sdl]", "fullscreen=false"]
    if settings.get("mouse_start", True) is not False:
        sdl += ["autolock=true", f"sensitivity={round(100 / scale)}"]  # (captured: uncaptured,
        # DOSBox reads the desktop pointer's place in the window, which the sensitivity would scale)
    if scale == 4:
        return sdl + ["output=opengl", "windowresolution=1280x960", "[render]",
                      "aspect=true", "scaler=normal2x", ""]
    return sdl + ["[render]", "aspect=true",
                  "scaler=" + ("none" if scale == 1 else SCALERS[scale]), ""]


# The game's speed: DOSBox's emulated CPU (fixed cycles: instructions a millisecond). The game
# draws a frame, shows it at the screen's next refresh (70 a second), and a walking figure takes a
# step a frame (a walk of one square: four frames): a frame that takes a moment longer than a
# refresh waits for the next, and the party walks at half speed. With the whole party in view and
# the Loader's shadows and dust a frame needs about 35000 to fit: there the four walk as fast as the
# leader alone; at 20000 about half as fast, at GOG's 7000 slower still. Both with the dynamic core
# (GOG's "auto" runs this game, a real-mode one, on the normal core): the same cycles do more and
# cost the computer about a third less. (30000, the fastest of before, is taken as the fastest now.)
GOG_SPEED, SPEEDS, DEFAULT_SPEED = "gog", (20000, 35000), 20000
FASTEST_BEFORE = 30000
CORE = "dynamic"


def cpu_lines(settings: dict) -> List[str]:
    """DOSBox's CPU speed, over GOG's settings: `cycles` 20000 (the default) or 35000, on the
    dynamic core; "gog" keeps GOG's own."""
    speed = settings.get("cycles", DEFAULT_SPEED)
    if speed == GOG_SPEED:
        return []
    speed = SPEEDS[-1] if speed == FASTEST_BEFORE else speed
    speed = speed if speed in SPEEDS else DEFAULT_SPEED
    return ["[cpu]", f"core={CORE}", f"cycles=fixed {speed}", ""]


# GOG's dosbox_darksun.conf has EMS on, and DOSBox 0.74 then keeps EMS's 64 KB page frame in the
# upper memory the helper loads into, leaving it 1 KB to spare; with EMS off the block is the
# helper's (65 KB free). The game's memory layer takes XMS when there is no EMS.
DOS_LINES = ["[dos]", "ems=false", ""]


def write_conf(game_dir: str, path: str = CONF, dice_log: bool = True) -> str:
    """Our replacement for dosbox_darksun_single.conf. Without the dice log it just runs the game."""
    settings = load_settings()
    lines = display_lines(settings) + cpu_lines(settings)
    if dice_log:  # (EMS's 64 KB page frame sits where the helper loads; the game takes XMS without it)
        lines += DOS_LINES
    lines += ["[autoexec]", "@echo off", "cls", 'mount c ".."']
    if os.path.isdir(os.path.join(game_dir, "cloud_saves")):
        lines.append(r'mount C "..\cloud_saves" -t overlay')  # where GOG keeps the saves
    lines += [f'mount d "{DOS_DIR}"', "c:"]
    # the game runs from C: (the game folder), where the patched copy looks for its files
    # (UMBPLUS.COM first: DOSBox 0.74's upper memory from C900h, not D000h, 28 KB more for the helper)
    lines += ["d:\\" + UMB_PLUS_COM.lower(), r"lh d:\dsclog.exe", "cls",
              "d:\\" + PATCHED_EXE.lower()] if dice_log else ["darksun"]
    # a game that stops with an error ("Null pointer assignment", "Stack overflow!") leaves its
    # message on screen until a key is pressed, rather than DOSBox closing over it, and saved for
    # the crash report (GAMEEND.COM: the screen's text, or a return code other than 0)
    lines += ["d:\\" + GAME_END_COM.lower(), "exit", ""]
    with open(path, "w", newline="\r\n") as f:
        f.write("\n".join(lines))
    return path


# The Options tab's new content and game changes (settings keys), each on unless switched off;
# the game's copies are written with them as they stand when it is started
CONTENT = ("kalzith", "semyon", "vulture", "pens_gear", "magic_arms", "world_gear", "world_magic", "effects_kept", "stealth_gear", "arena_ring",
           "elf_looks", "roll_store", "cilla_elf", "camera_still", "scene_pointer", "mouse_start",
           "steady_pace", "party_spread")
# the new items' parts (worldgear.data_chunks', and the arena's ring, ring.py), all switched by
# one box: NEW_ITEMS
ITEM_PARTS, NEW_ITEMS = ("pens_gear", "magic_arms", "world_gear", "world_magic", "arena_ring"), "new_items"


def content(settings: dict) -> dict:
    """{key: on} for each of CONTENT (on unless the settings say False; the new items' parts as
    NEW_ITEMS is)."""
    items = settings.get(NEW_ITEMS, True) is not False
    return {key: items if key in ITEM_PARTS else settings.get(key, True) is not False for key in CONTENT}


def prepare_patched_game(game_dir: str, settings: Optional[dict] = None) -> Optional[str]:
    """Write DSUNLOG.EXE next to DSCLOG.EXE, and the copies of the game's files with the
    companion's additions: SEGOBJEX.GFF with its item icons (icons.py; without it the items keep
    the plain icons) and Kalzith's object, RESOURCE.GFF with Cat's Grace's icon, GPLDATA.GFF and
    RGN29.GFF with Kalzith (kalzith.py), each addition only if switched on in SETTINGS (CONTENT;
    the saved settings if none given). Returns why the game can't be patched, or None."""
    on = content(load_settings() if settings is None else settings)
    skip = (frozenset() if on["effects_kept"] else frozenset(gamepatch.EFFECTS_KEPT)) \
        | (frozenset() if on["roll_store"] else frozenset(gamepatch.ROLL_STORE)) \
        | (frozenset() if on["camera_still"] else frozenset(gamepatch.CAMERA)) \
        | (frozenset() if on["scene_pointer"] else frozenset(gamepatch.SCENE_POINTER)) \
        | (frozenset() if on["mouse_start"] else frozenset(gamepatch.MOUSE_START)) \
        | (frozenset() if on["steady_pace"] else frozenset(gamepatch.STEADY_PACE))\
        | (frozenset() if on["party_spread"] else frozenset(gamepatch.PARTY_SPREAD))
    try:
        gamepatch.write_patched(_find_file(game_dir, "DSUN.EXE"), os.path.join(DOS_DIR, PATCHED_EXE), skip)
    except (gamepatch.PatchError, OSError) as e:
        return str(e)
    objects_ok, new_objects = False, ()
    try:
        objects = _find_file(game_dir, icons.OBJECTS_FILE)
        if objects:
            objects_ok, new_objects = icons.write_objects(objects, os.path.join(DOS_DIR, icons.OBJECTS_FILE), on)
    except (gff.GffError, OSError, KeyError, struct.error, ValueError, IndexError):
        pass  # no icons of our own: the game's plain ones
    # the regions with a person given an object of their own for a new item (worldgear.py): only
    # with that object in the objects copy (a region naming an object that isn't there would stop
    # the game)
    # (the slave pens' clones go into Kalzith's copy of the pens, when he's in it: one copy)
    with_kalzith = on["kalzith"] and objects_ok
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
        except (gff.GffError, OSError, KeyError, struct.error, ValueError, IndexError, gpl.ScriptError):
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
        on["pens_gear"] and objects_ok, worldgear.HAYNEEDLE_OBJECT in new_objects))]  # (Alagorn knows
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
        if not with_kalzith and not pens_clones:
            try:
                os.remove(os.path.join(DOS_DIR, kalzith.REGION_FILE))
            except FileNotFoundError:
                pass  # (no region copy to take away)
    except (gff.GffError, OSError, KeyError, struct.error, ValueError, IndexError, gpl.ScriptError):
        for name in (kalzith.SCRIPTS_FILE, kalzith.REGION_FILE):  # (all or nothing: the game's own)
            try:
                os.remove(os.path.join(DOS_DIR, name))
            except OSError:
                pass
    # the game's own arrow for the scenes' pointer (DSCLOG's, without it)
    scenepointer.write_pointer(_find_file(game_dir, icons.RESOURCE_FILE), _find_file(game_dir, "GPLDATA.GFF"),
                               os.path.join(DOS_DIR, scenepointer.POINTER_FILE))
    try:
        resources = _find_file(game_dir, icons.RESOURCE_FILE)
        if resources:
            icons.write_resources(resources, os.path.join(DOS_DIR, icons.RESOURCE_FILE), on["roll_store"])
    except (gff.GffError, OSError, KeyError, struct.error, ValueError, IndexError):
        pass  # no Cat's Grace icon: Flaming Sphere's
    return None


# Windows' codes for a program that crashes (DOSBox itself, not the game in it)
CRASH_CODES = {0xC0000005: "an access violation", 0xC00000FD: "a stack overflow", 0xC0000409: "a stack buffer overrun"}


# what launch() last started: the recompiled program's path, or None for DOSBox (closed_line,
# started_line: by what was started, not by what the settings say now)
STARTED: Optional[str] = None


def started_line(game_dir: str) -> str:
    """The log's line for the game started from GAME_DIR: in DOSBox, or as Dark Sun Recompiled
    (which program), so a player sees which one runs."""
    if STARTED:
        return f"Starting Shattered Lands from {game_dir} as Dark Sun Recompiled ({STARTED})."
    return f"Starting Shattered Lands from {game_dir} in DOSBox."


def closed_line(code: int) -> str:
    """The log's line for DOSBox (or the recompiled program, if that was started) closing with exit
    code CODE."""
    name = "Dark Sun Recompiled" if STARTED else "DOSBox"
    if code == 0:
        return f"{name} closed."
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
    """DOSBox's stdout.txt and stderr.txt (in its folder; only read) written since SINCE."""
    out: Dict[str, str] = {}
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
SWITCH_DEFAULTS = {"monster_info": True, "floating_names": True, "pickpockets": True,
                   "show_gear": True, "starting_gear": True, "shadows": True, "dust": True, "rings": "chosen", "combat_log": True,
                   "targeting": True, "scroll_map": True, "cycles": DEFAULT_SPEED,
                   "combat_log_level": "short", "defiler_scrolls": True, NEW_ITEMS: True}  # (combatlog.SHORT, the panel's level unless chosen)


def effective_switches(settings: dict) -> Dict[str, object]:
    """Every switch as the Loader uses it: as set, else its default (rule changes and content: on)."""
    from . import game
    out: Dict[str, object] = {key: settings.get(key, default) for key, default in SWITCH_DEFAULTS.items()}
    out.update(content(settings))
    out.update({key: bool(settings.get(key, True)) for key, _ in game.RULE_SETTINGS})
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


def launch(game_dir: str) -> Tuple[subprocess.Popen, Optional[str]]:
    """Start the game. Returns DOSBox's process (or the recompiled program's) and, if the dice log
    can't run, why."""
    global STARTED
    game_dir = os.path.abspath(game_dir)  # (DOSBox runs in its own folder: a relative path would miss)
    program = recompiled_program()
    if program is not None:
        if not _find_file(game_dir, "DSUN.EXE"):
            raise LaunchError(f"{game_dir} has no DSUN.EXE; pick the GOG install folder")
        problem = prepare_patched_game(game_dir)
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
    problem = prepare_patched_game(game_dir)
    for old in (GAME_END, GAME_MESSAGE, GAME_OK):  # (the last game's)
        try:
            os.remove(old)
        except OSError:
            pass
    exe = _find_file(dosbox_dir, "DOSBox.exe")
    if exe is None:
        raise LaunchError(f"No DOSBox.exe in {dosbox_dir}")
    conf = write_conf(game_dir, dice_log=problem is None)
    return subprocess.Popen(
        [exe, "-conf", settings_conf, "-conf", conf, "-noconsole"],
        cwd=dosbox_dir), problem
