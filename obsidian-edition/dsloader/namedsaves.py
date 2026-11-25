"""The game's saves kept a second time under the names they have in the game.

The game keeps its saves as SAVE01.SAV to SAVE10.SAV, and with the Loader's four pages
(savepages.py) SAVB, SAVC and SAVD01.SAV to 10.SAV too, in its folder or, with GOG's, in
cloud_saves (the fifth page, QUICK, SAVQ: quicksave.py's quick saves and autosaves, is left out:
its slots are written over in turn, so their copies would only come and go). Only the game's own list says which is which: the name typed for each is inside
the file (its STXT chunk). The Loader copies each into its own folder NAMED, as "Page 2 slot 05 -
Before Scar's battle.SAV", whenever the game writes one, one copy for each slot: a slot saved over
has its copy replaced. A copy can be put back in a slot (to be loaded from the game's list) with
`restore`.

Wake of the Ravager's saves (`wotr=True`) the same way, into a folder of their own, NAMED_WOTR: its one
page of ten (SAVE01.SAV to SAVE10.SAV; its quick saves' page, SAVQ, left out as Shattered Lands'), a save
told by its sheet table (SAVE 6: 17 sheets of 42h bytes, or the Loader's 48h, ravager.SHEET_SIZE). A copy
put back in a slot is made the Loader's 48h sheets first (ravager.resized_chunks), as the Loader makes
every save of the sequel's folder as it starts the game (ravager.widen_files).
"""

import os
import re
import shutil
from typing import Dict, List, Optional, Tuple

from .gff import GffError, read_gff, write_atomic
from .savefile import party_chunks

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAMED = os.path.join(HERE, "Named saves")
NAMED_WOTR = os.path.join(HERE, "Named saves (Wake of the Ravager)")
WOTR_PAGES = 1  # (the sequel's save window: one page of ten)
PAGES = ("SAVE", "SAVB", "SAVC", "SAVD")  # page 1 (the game's own) to 4 (not the QUICK page, SAVQ)
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


def _wotr_save(chunks) -> None:
    """ValueError unless CHUNKS are a Wake of the Ravager save's (its sheet table, 17 sheets)."""
    from . import ravager
    if len(chunks.get(ravager.SHEETS_CHUNK, b"")) not in {ravager.SHEETS_COUNT * size for size in ravager.BACKUP}:
        raise ValueError("not a Wake of the Ravager save")


def save_name(data: bytes, wotr: bool = False) -> Optional[str]:
    """The name typed for a save in the game (WOTR: Wake of the Ravager), or None if DATA isn't one."""
    try:
        chunks = read_gff(data)
        if wotr:
            _wotr_save(chunks)
        else:
            party_chunks(chunks)
        text = chunks.get(NAME_CHUNK)
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


def _same_bytes(copy: str, data: bytes) -> bool:
    try:
        with open(copy, "rb") as f:
            return f.read() == data
    except OSError:
        return False


def sync(game_dir: str, folder: str = NAMED, wotr: bool = False) -> List[str]:
    """Each of the game's saves copied into FOLDER under its name, where its copy is missing or not
    the same save (even if its timestamp and size match); a slot's copy under another name (the
    slot saved over) is replaced. The copies made. WOTR: Wake of the Ravager's (one page)."""
    copies = _copies(folder)
    made = []
    for page in range(1, (WOTR_PAGES if wotr else len(PAGES)) + 1):
        for slot in range(1, SLOTS + 1):
            path = slot_path(game_dir, page, slot)
            if path is None:
                continue
            existing = copies.get((page, slot), [])
            try:
                with open(path, "rb") as f:
                    stamp = os.fstat(f.fileno()).st_mtime
                    data = f.read()
            except OSError:
                continue
            if len(existing) == 1 and _same_bytes(os.path.join(folder, existing[0]), data):
                continue
            name = save_name(data, wotr)
            if name is None:
                continue  # (being written, or not a save)
            target = copy_name(page, slot, name)
            try:
                os.makedirs(folder, exist_ok=True)
                target_path = os.path.join(folder, target)
                write_atomic(target_path, data)
                try:
                    os.utime(target_path, (stamp, stamp))
                except OSError:
                    pass
                for old in existing:
                    if os.path.normcase(old) != os.path.normcase(target):
                        os.remove(os.path.join(folder, old))
            except OSError:
                continue
            made.append(target)
    return made


def slot_name(game_dir: str, page: int, slot: int, wotr: bool = False) -> Optional[str]:
    """The name of the save in a slot now, or None for an empty one."""
    path = slot_path(game_dir, page, slot)
    try:
        with open(path, "rb") as f:
            return save_name(f.read(), wotr) or ""
    except (OSError, TypeError):
        return None


def replaced_name(page: int, slot: int, name: str) -> str:
    """The file the save a restore replaces is kept as: "Replaced - Page 1 slot 05 - NAME.SAV" (not
    a slot's copy, so sync never replaces it)."""
    return "Replaced - " + copy_name(page, slot, name)


def is_wotr_save(path: str) -> bool:
    """PATH is a Wake of the Ravager save (a named copy of one, or the game's own)."""
    try:
        with open(path, "rb") as f:
            return save_name(f.read(), True) is not None
    except OSError:
        return False


def restore(copy: str, game_dir: str, page: int, slot: int, folder: str = NAMED, wotr: bool = False) -> str:
    """A named copy (or any save file) put in the game's PAGE and SLOT, to be loaded from its list.
    The slot's save, if any, is kept first in FOLDER (replaced_name; "(2)" and on if that is taken):
    the slot's own named copy is replaced at the next sync, as for any slot saved over. Written
    through a temporary file, so a failure leaves the slot as it was and no temporary file. Its
    name in the game. ValueError if it isn't a save."""
    with open(copy, "rb") as f:
        data = f.read()
    name = save_name(data, wotr)
    if name is None:
        raise ValueError(f"{os.path.basename(copy)} isn't a {'Wake of the Ravager' if wotr else 'Shattered Lands'} save")
    if not (1 <= page <= (WOTR_PAGES if wotr else len(PAGES)) and 1 <= slot <= SLOTS):
        raise ValueError("no such page or slot")
    if wotr:  # (the Loader's sheets, as every save of the sequel's folder: ravager.widen_files)
        from . import icons, ravager
        wide = ravager.resized_chunks(read_gff(data), ravager.SHEET_SIZE)
        if wide:
            data = icons.with_chunks(data, wide)
    old = slot_path(game_dir, page, slot)
    if old is not None:
        with open(old, "rb") as f:
            before = f.read()
        if before != data:
            os.makedirs(folder, exist_ok=True)
            kept = replaced_name(page, slot, save_name(before, wotr) or "no name")
            base, n = kept[:-len(".SAV")], 2
            while os.path.exists(os.path.join(folder, kept)):
                kept, n = f"{base} ({n}).SAV", n + 1
            shutil.copy2(old, os.path.join(folder, kept))
    path = os.path.join(saves_dir(game_dir), slot_file(page, slot))
    write_atomic(path, data)
    return name
