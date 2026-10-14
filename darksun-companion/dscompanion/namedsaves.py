"""The game's saves kept a second time under the names they have in the game.

The game keeps its saves as SAVE01.SAV to SAVE10.SAV, and with the Ledger's four pages
(savepages.py) SAVB, SAVC and SAVD01.SAV to 10.SAV too, in its folder or, with GOG's, in
cloud_saves. Only the game's own list says which is which: the name typed for each is inside
the file (its STXT chunk). The Ledger copies each into its own folder NAMED, as "Page 2 slot 05 -
Before Scar's battle.SAV", whenever the game writes one, one copy for each slot: a slot saved over
has its copy replaced. A copy can be put back in a slot (to be loaded from the game's list) with
`restore`.
"""

import os
import re
import shutil
from typing import Dict, List, Optional, Tuple

from .gff import GffError, read_gff

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAMED = os.path.join(HERE, "Named saves")
PAGES = ("SAVE", "SAVB", "SAVC", "SAVD")  # page 1 (the game's own) to 4
SLOTS = 10
NAME_CHUNK = ("STXT", 1)
UNSAFE = re.compile(r'[<>:"/\\|?*\x00-\x1f]')  # (not in a Windows file name)
COPY = re.compile(r"^Page ([1-4]) slot (\d\d) - .*\.SAV$", re.IGNORECASE)


def slot_file(page: int, slot: int) -> str:
    """The game's file for PAGE (1-4) and SLOT (1-10)."""
    return f"{PAGES[page - 1]}{slot:02d}.SAV"


def saves_dir(game_dir: str) -> str:
    """Where the game writes its saves: GOG's cloud_saves if the game has one (mounted over its
    folder), else its folder."""
    cloud = os.path.join(game_dir, "cloud_saves")
    return cloud if os.path.isdir(cloud) else game_dir


def slot_path(game_dir: str, page: int, slot: int) -> Optional[str]:
    """The save the game sees in a slot: cloud_saves' over the game folder's. None if empty."""
    for folder in dict.fromkeys((saves_dir(game_dir), game_dir)):
        path = os.path.join(folder, slot_file(page, slot))
        if os.path.isfile(path):
            return path
    return None


def save_name(data: bytes) -> Optional[str]:
    """The name typed for a save in the game, or None if DATA isn't one."""
    try:
        text = read_gff(data).get(NAME_CHUNK)
    except (GffError, ValueError, IndexError, KeyError):
        return None
    if text is None:
        return None
    return text.split(b"\0", 1)[0].decode("cp437", "replace").strip()


def copy_name(page: int, slot: int, name: str) -> str:
    """The copy's file name: "Page 2 slot 05 - NAME.SAV" (characters Windows won't take as _)."""
    name = UNSAFE.sub("_", name).rstrip(". ") or "no name"
    return f"Page {page} slot {slot:02d} - {name}.SAV"


def _copies(folder: str) -> Dict[Tuple[int, int], List[str]]:
    out: Dict[Tuple[int, int], List[str]] = {}
    if os.path.isdir(folder):
        for entry in os.listdir(folder):
            m = COPY.match(entry)
            if m:
                out.setdefault((int(m.group(1)), int(m.group(2))), []).append(entry)
    return out


def sync(game_dir: str, folder: str = NAMED) -> List[str]:
    """Each of the game's saves copied into FOLDER under its name, where its copy is missing or
    older; a slot's copy under another name (the slot saved over) is replaced. The copies made."""
    copies = _copies(folder)
    made = []
    for page in range(1, len(PAGES) + 1):
        for slot in range(1, SLOTS + 1):
            path = slot_path(game_dir, page, slot)
            if path is None:
                continue
            try:
                stamp = os.path.getmtime(path)
            except OSError:
                continue
            existing = copies.get((page, slot), [])
            if existing and all(os.path.getmtime(os.path.join(folder, e)) >= stamp for e in existing):
                continue
            try:
                with open(path, "rb") as f:
                    data = f.read()
            except OSError:
                continue
            name = save_name(data)
            if name is None:
                continue  # (being written, or not a save)
            target = copy_name(page, slot, name)
            try:
                os.makedirs(folder, exist_ok=True)
                tmp = os.path.join(folder, target + ".tmp")
                with open(tmp, "wb") as f:
                    f.write(data)
                os.utime(tmp, (stamp, stamp))
                os.replace(tmp, os.path.join(folder, target))
                for old in existing:
                    if old != target:
                        os.remove(os.path.join(folder, old))
            except OSError:
                continue
            made.append(target)
    return made


def slot_name(game_dir: str, page: int, slot: int) -> Optional[str]:
    """The name of the save in a slot now, or None for an empty one."""
    path = slot_path(game_dir, page, slot)
    try:
        with open(path, "rb") as f:
            return save_name(f.read()) or ""
    except (OSError, TypeError):
        return None


def restore(copy: str, game_dir: str, page: int, slot: int) -> str:
    """A named copy (or any save file) put in the game's PAGE and SLOT, to be loaded from its list
    (the slot's save, if any, replaced). Its name in the game. ValueError if it isn't a save."""
    with open(copy, "rb") as f:
        data = f.read()
    name = save_name(data)
    if name is None:
        raise ValueError(f"{os.path.basename(copy)} isn't a Shattered Lands save")
    if not (1 <= page <= len(PAGES) and 1 <= slot <= SLOTS):
        raise ValueError("no such page or slot")
    path = os.path.join(saves_dir(game_dir), slot_file(page, slot))
    shutil.copyfile(copy, path)
    return name
