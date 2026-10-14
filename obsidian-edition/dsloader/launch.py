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
import time
from typing import Dict, List, Optional, Tuple

from . import gamepatch, gff, gpl, icons, kalzith, tome, worldgear

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
    dosbox = _find_file(folder, "DOSBOX")
    return bool(_find_file(folder, "DSUN.EXE") and dosbox and _find_file(dosbox, "DOSBox.exe"))


def candidate_dirs() -> List[str]:
    drives = [f"{d}:\\" for d in string.ascii_uppercase if os.path.exists(f"{d}:\\")] if os.name == "nt" else []
    return [os.path.join(drive, sub) for drive in drives for sub in GOG_SUBDIRS]


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


def load_settings() -> dict:
    try:
        with open(SETTINGS, encoding="utf-8") as f:
            settings = json.load(f)
    except (OSError, ValueError):
        return {}
    if upgrade_settings(settings):
        try:
            save_settings(settings)
        except OSError:
            pass  # (upgraded again next time)
    return settings


def save_settings(settings: dict) -> None:
    settings["settings_version"] = SETTINGS_VERSION
    with open(SETTINGS, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)


def speaker_names() -> Dict[int, str]:
    """The names the player has given dialogue portraits: {portrait: name}."""
    names = load_settings().get("speakers", {})
    return {int(k): v for k, v in names.items() if str(k).isdigit() and isinstance(v, str) and v}


def set_speaker_name(portrait: int, name: str) -> None:
    """Remember a name for a portrait (an empty name forgets it)."""
    settings = load_settings()
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
    settings = load_settings()
    settings["pickpocketed"] = list(entries)
    save_settings(settings)


def tools_given() -> set:
    """The thieves given thieving tools already (tools.py)."""
    return set(load_settings().get("tools_given", []))


def add_tools_given(keys: List[str]) -> None:
    settings = load_settings()
    settings["tools_given"] = sorted(set(settings.get("tools_given", [])) | set(keys))
    save_settings(settings)


def add_learned_speakers(learned: Dict[int, str]) -> None:
    settings = load_settings()
    settings.setdefault("speakers_learned", {}).update({str(k): v for k, v in learned.items()})
    save_settings(settings)


def find_game_dir(given: Optional[str] = None) -> Optional[str]:
    """The game folder: `given`, the one remembered from last time, or a usual GOG location."""
    for folder in [given, load_settings().get("game_dir")] + candidate_dirs():
        if folder and is_game_dir(folder):
            return folder
    return None


SCALERS = {2: "normal2x", 3: "normal3x"}
DEFAULT_SCALE = 3
WINDOW_SCALES = (1, 2, 3, 4)


def display_lines(settings: dict) -> List[str]:
    """DOSBox's display, over GOG's settings (full screen): a window, by default three times the
    game's 320x200 (960x720 with the aspect correction GOG turns on); `window_scale` 2 makes it
    twice, 4 four times, 1 leaves it at 320x240; `fullscreen` true keeps GOG's full screen.
    Alt+Enter switches either way in DOSBox. DOSBox 0.74 has no 4x scaler, so four times is
    DOSBox scaling the window itself, which needs its OpenGL output."""
    if settings.get("fullscreen"):
        return []
    scale = settings.get("window_scale", DEFAULT_SCALE)
    scale = scale if scale in WINDOW_SCALES else DEFAULT_SCALE
    if scale == 4:
        return ["[sdl]", "fullscreen=false", "output=opengl", "windowresolution=1280x960", "[render]",
                "aspect=true", "scaler=normal2x", ""]
    return ["[sdl]", "fullscreen=false", "[render]", "aspect=true",
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
    lines += [r"lh d:\dsclog.exe", "cls", "d:\\" + PATCHED_EXE.lower()] if dice_log else ["darksun"]
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
           "elf_looks", "roll_store", "cilla_elf")
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
        | (frozenset() if on["roll_store"] else frozenset(gamepatch.ROLL_STORE))
    try:
        gamepatch.write_patched(_find_file(game_dir, "DSUN.EXE"), os.path.join(DOS_DIR, PATCHED_EXE), skip)
    except (gamepatch.PatchError, OSError) as e:
        return str(e)
    objects_ok, new_objects = False, ()
    try:
        objects = _find_file(game_dir, icons.OBJECTS_FILE)
        if objects:
            objects_ok, new_objects = icons.write_objects(objects, os.path.join(DOS_DIR, icons.OBJECTS_FILE), on)
    except (gff.GffError, OSError, KeyError, struct.error, ValueError):
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
        except (gff.GffError, OSError, KeyError, struct.error, ValueError):
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
        on["pens_gear"] and objects_ok))]  # (Alagorn knows the weapons by their own
    # pictures; the Elven Leader gives the cloak, and Father Garyn the tome, of its own object)
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
    try:
        resources = _find_file(game_dir, icons.RESOURCE_FILE)
        if resources:
            icons.write_resources(resources, os.path.join(DOS_DIR, icons.RESOURCE_FILE), on["roll_store"])
    except (gff.GffError, OSError, KeyError, struct.error, ValueError, IndexError):
        pass  # no Cat's Grace icon: Flaming Sphere's
    return None


# Windows' codes for a program that crashes (DOSBox itself, not the game in it)
CRASH_CODES = {0xC0000005: "an access violation", 0xC00000FD: "a stack overflow", 0xC0000409: "a stack buffer overrun"}


def closed_line(code: int) -> str:
    """The log's line for DOSBox closing with exit code CODE."""
    if code == 0:
        return "DOSBox closed."
    known = CRASH_CODES.get(code & 0xFFFFFFFF)
    if known:
        return (f"DOSBox closed: it crashed ({known}, code {code & 0xFFFFFFFF:08X}h). That is DOSBox "
                "itself failing, not the game stopping with an error.")
    return f"DOSBox closed with exit code {code}."


# GAMEEND.COM, run after the game, notes in GAMEEND.TXT (in DOS_DIR) how the game stopped with an
# error; the Loader's crash reports go in CRASH_DIR
GAME_END_COM = "GAMEEND.COM"
GAME_END = os.path.join(DOS_DIR, "GAMEEND.TXT")
CRASH_DIR = os.path.join(HERE, "crash-logs")
DOSBOX_OUTPUT = ("stdout.txt", "stderr.txt")  # DOSBox's own messages with -noconsole (its folder)


def game_end_note() -> Optional[str]:
    """What GAMEEND.COM saved of the game stopping with an error (its return code, video mode,
    and the screen's text), or None if it ended as usual."""
    try:
        with open(GAME_END, encoding="cp437", errors="replace") as f:
            return f.read().rstrip()
    except OSError:
        return None


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
SWITCH_DEFAULTS = {"monster_info": True, "pickpockets": True,
                   "show_gear": True, "shadows": True, "dust": True, "rings": "chosen", "combat_log": True,
                   "targeting": True, "scroll_map": True, "scroll_right": False, "cycles": DEFAULT_SPEED}


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
    if note:
        lines += ["", "The game stopped with an error. On the screen:", note]
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


def write_crash_report(text: str, now: float, folder: str = CRASH_DIR) -> str:
    """Save a crash report as crash-logs/crash-YYYY-MM-DD-HHMMSS.txt (a number after it if there
    is one already); returns its path."""
    os.makedirs(folder, exist_ok=True)
    stem = os.path.join(folder, time.strftime("crash-%Y-%m-%d-%H%M%S", time.localtime(now)))
    path, n = stem + ".txt", 1
    while os.path.exists(path):  # (two in the same second)
        n += 1
        path = f"{stem}-{n}.txt"
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return path


def launch(game_dir: str) -> Tuple[subprocess.Popen, Optional[str]]:
    """Start the game. Returns DOSBox's process and, if the dice log can't run, why."""
    dosbox_dir = _find_file(game_dir, "DOSBOX")
    settings_conf = _find_file(game_dir, "dosbox_darksun.conf") or _find_file(
        os.path.join(game_dir, "__support", "app"), "dosbox_darksun.conf")
    if not dosbox_dir or not settings_conf:
        raise LaunchError(f"{game_dir} does not look like the GOG install of Shattered Lands")
    problem = prepare_patched_game(game_dir)
    try:
        os.remove(GAME_END)  # (the last game's)
    except OSError:
        pass
    conf = write_conf(game_dir, dice_log=problem is None)
    return subprocess.Popen(
        [_find_file(dosbox_dir, "DOSBox.exe"), "-conf", settings_conf, "-conf", conf, "-noconsole"],
        cwd=dosbox_dir), problem
