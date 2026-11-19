"""Quick save, quick load and autosave: a fifth page of the save window, QUICK, that fills itself.

The page is SAVQ01.SAV to SAVQ10.SAV (savepages.py's QUICK button; DSCLOG's fifth letter). Slots
1 to 5 are the quick saves, 6 to 10 the autosaves: each kind writes to its first empty slot, then
over its oldest save, so five of each are kept and neither pushes the other out.

- **The quick save key** (F5) on the map saves at once, with no window: "Quick - Day 47, 14:20".
- **The quick load key** (F9) opens the game's own LOAD window on the QUICK page with the newest
  save there chosen: Enter loads it, Escape or EXIT goes back to the game.
- **Autosave**: a few seconds after the party comes into another area ("Auto - Day 47, 14:20 -
  The slave pens"), and after a fight ends ("Auto - Day 47, 14:20 - after a fight").

How: DSCLOG counts the two keys (QS_SEQ, header +1882; its keys are the Loader's to set, QS_KEYS
+1878, FFFFh for none: the switch off leaves them the game's) when the map's main loop is running,
which it does only with no window, talk, screen or menu up. For a save the Loader writes the file
(the game's save path, DS:4B81h, then SAVQnn.SAV) and the name into SAVE_TEXT (the tail's, +1888)
and sets SAVE_REQ (+1886) to 1; DSCLOG, from the top of the game's main loop (PROBE_SCROLL: the
one place the game's own save can be reached from too), calls the routine the SAVE window calls
(an overlay's entry, 4242h:0089h) unless a fight is on, and leaves 3 (saved), 4 (the game's save
failed) or 5 (a fight). For a load the Loader makes Q the page (the letter in the game's two file
names, as DSCLOG's page buttons do), chooses the row, and sets 2: DSCLOG opens the LOAD window
(428Ah:0020h).

The save window never opens on the QUICK page by itself (_page_back): its slots are written over
in turn, so a save made by hand belongs on pages 1 to 4.

An autosave is asked for only out of a fight, on the map, with the main loop seen running, not
while a game is loading and not within AUTO_GAP of the last; and none of the three with the disk
nearly full (the game's "Disk Space Low !!!" box would stop the game for a click: DOSBox tells the
game a made-up free space, so the Loader looks at the real folder).
"""

import os
import shutil
import struct
from typing import List, Optional, Tuple

from . import journal, namedsaves

TSR_QS_KEYS, TSR_QS_SEQ, TSR_SAVE_REQ, TSR_SAVE_OFF = 1878, 1882, 1886, 1888  # DSCLOG's header
TSR_TAIL_SEG, TSR_MAIN_TICKS = 1834, 260
SAVE_FILE, SAVE_NAME = 64, 48  # SAVE_TEXT: the file's bytes, then the name's (each with its NUL)
NAME_MOST = 42  # the save window keeps 43 bytes of a name
REQ_SAVE, REQ_LOAD, DONE, FAILED, IN_FIGHT = 1, 2, 3, 4, 5
KEY_SAVE, KEY_LOAD, NO_KEY = 0x3F00, 0x4300, 0xFFFF  # F5 and F9, as INT 16h gives them
KEY_NAMES = ("F5", "F9")
PREFIX, LETTER, PAGE = "SAVQ", "Q", 5
QUICK_SLOTS, AUTO_SLOTS = (1, 2, 3, 4, 5), (6, 7, 8, 9, 10)
SAVE_PATH = 0x4B81  # DS: the folder the game writes saves to, as it puts it before a file's name
NAME_FIND, NAME_SAVE = 0x1DCF + 3, 0x1DDA + 3  # DS: the page's letter in "SAVE??.SAV" and "SAVE%.2d.SAV"
WINDOW_FROM_DS, CHOSEN = 0x4356 - 0x3BA7, 0x4E4  # the save window's data: the row chosen
SCREEN_IS, ON_MAP = 0x0BC9, 1  # DS word: 1 on the map
CAMP_BYTE, CAMPING = 0x1D, 4  # a creature's record: 4 while the party is in the camp the game's rest
                              # routine at DSUN.EXE 80Fxxh makes (F9 is the game's key that breaks it)
AREA_WAIT = 4.0  # seconds in a new area, the main loop running, before its autosave
FIGHT_WAIT = 4.0  # ... and out of a fight (the arena's waves follow each other sooner)
AUTO_GAP = 60.0  # seconds between two autosaves
ANSWER_WAIT = 6.0  # seconds DSCLOG has to take a request (a window opened meanwhile: given up)
DISK_LEAST = 4 * 1024 * 1024  # bytes free in the saves' folder, or nothing is saved
QUICK, AUTO = "Quick", "Auto"
KEPT_PAGES = (b"E", b"B", b"C", b"D")  # the letters of pages 1 to 4 (DSCLOG's sp_letters)


def slot_file(slot: int) -> str:
    return f"{PREFIX}{slot:02d}.SAV"


def slot_path(game_dir: str, slot: int) -> Optional[str]:
    """The save the game sees in a slot of the page (cloud_saves' over the game folder's), or None."""
    for folder in dict.fromkeys((namedsaves.saves_dir(game_dir), game_dir)):
        path = os.path.join(folder, slot_file(slot))
        if os.path.isfile(path):
            return path
    return None


def _time(path: Optional[str]) -> Optional[float]:
    try:
        return os.path.getmtime(path) if path else None
    except OSError:
        return None


def next_slot(game_dir: str, slots: Tuple[int, ...]) -> int:
    """The slot of SLOTS to write: the first with no save, else the one saved longest ago."""
    times = [(slot, _time(slot_path(game_dir, slot))) for slot in slots]
    empty = [slot for slot, t in times if t is None]
    if empty:
        return empty[0]
    return min(times, key=lambda st: st[1])[0]


def newest_slot(game_dir: str) -> Optional[int]:
    """The slot of the page saved last (quick or auto), or None with none."""
    times = [(t, slot) for slot in QUICK_SLOTS + AUTO_SLOTS
             for t in (_time(slot_path(game_dir, slot)),) if t is not None]
    return max(times)[1] if times else None


def quick_name(clock: Optional[int]) -> str:
    """ "Quick - Day 47, 14:20" """
    return " - ".join(part for part in (QUICK, journal.time_of(clock)) if part)[:NAME_MOST]


def auto_name(what: str, clock: Optional[int]) -> str:
    """ "Auto - Day 47, 14:20 - The slave pens": the time first (a row of the window shows about 32
    letters, so it is the place that is cut off there), WHAT cut short if the name would be too
    long for the game."""
    when = journal.time_of(clock)
    room = NAME_MOST - len(AUTO) - 3 - (len(when) + 3 if when else 0)
    return " - ".join(part for part in (AUTO, when, what[:max(0, room)].rstrip()) if part)


def disk_free(game_dir: str) -> Optional[int]:
    """Bytes free where the game writes its saves (None: unknown)."""
    try:
        return shutil.disk_usage(namedsaves.saves_dir(game_dir)).free
    except OSError:
        return None


class QuickSave:
    """The dice log's part: tick() each pass gives its lines. `keys` and `auto` are the switches."""

    def __init__(self):
        self.keys = True
        self.auto = True
        self.label: Optional[str] = None  # a word to float over the leader (taken by the dice log)
        self._hdr: Optional[int] = None  # (the DSCLOG the rest is about)
        self._seq: Optional[Tuple[int, int]] = None  # QS_SEQ as last acted on
        self._keys_set: Optional[Tuple[int, int]] = None
        self._ticks: Optional[int] = None
        self._running = False  # the map's main loop ran between the last two passes
        self._asked: Optional[Tuple[int, float, str, int, str]] = None  # (request, when, kind, slot, name)
        self._region: Optional[int] = None  # the area the last autosave (or the first look) was in
        self._region_at: Optional[float] = None  # when the party was first seen in another
        self._fought = False
        self._fight_over_at: Optional[float] = None
        self._auto_at: Optional[float] = None
        self._said_disk = False
        self._page_was = KEPT_PAGES[0]  # the save window's page of 1 to 4 as last seen with the window shut

    # ---- DSCLOG's side -----------------------------------------------------------------------

    def _word(self, gd, field: int) -> int:
        return struct.unpack("<H", gd.guest.read(self._hdr + field, 2))[0]

    def _camping(self, gd) -> bool:
        try:
            return any(gd.creature(n)[CAMP_BYTE] == CAMPING for n in range(4))
        except IndexError:
            return False

    def _set_keys(self, gd) -> None:
        """The two keys DSCLOG's with the switch on, but the game's while the party camps (its F9
        breaks the camp, 810DCh)."""
        keys = (KEY_SAVE, KEY_LOAD) if self.keys and not self._camping(gd) else (NO_KEY, NO_KEY)
        if keys != self._keys_set:
            gd.guest.write(self._hdr + TSR_QS_KEYS, struct.pack("<HH", *keys))
            self._keys_set = keys

    def _ask_save(self, gd, kind: str, slot: int, name: str, now: float) -> Optional[str]:
        """The request for a save written; a line if it can't be asked."""
        path = gd.guest.read(gd.ds * 16 + SAVE_PATH, SAVE_FILE).split(b"\0", 1)[0]
        file = path + slot_file(slot).encode("ascii")
        if len(file) >= SAVE_FILE:
            return f"{kind} save: not made, the game's save folder has too long a name ({len(path)} letters)"
        text = file.ljust(SAVE_FILE, b"\0") + name.encode("cp437", "replace")[:NAME_MOST].ljust(SAVE_NAME, b"\0")
        tail = self._word(gd, TSR_TAIL_SEG) * 16 + self._word(gd, TSR_SAVE_OFF)
        gd.guest.write(tail, text)
        gd.guest.write(self._hdr + TSR_SAVE_REQ, struct.pack("<H", REQ_SAVE))
        self._asked = (REQ_SAVE, now, kind, slot, name)
        return None

    def _ask_load(self, gd, game_dir: str, now: float) -> Optional[str]:
        slot = newest_slot(game_dir)
        if slot is None:
            return "Quick load: no quick save or autosave yet"
        for at in (NAME_FIND, NAME_SAVE):
            gd.guest.write(gd.ds * 16 + at, LETTER.encode("ascii"))
        gd.guest.write((gd.ds - WINDOW_FROM_DS) * 16 + CHOSEN, struct.pack("<H", slot - 1))
        gd.guest.write(self._hdr + TSR_SAVE_REQ, struct.pack("<H", REQ_LOAD))
        self._asked = (REQ_LOAD, now, "", slot, "")
        return None

    def _answer(self, gd, now: float) -> List[str]:
        """What came of the request, once DSCLOG says (or the wait is up)."""
        request, when, kind, slot, name = self._asked
        got = self._word(gd, TSR_SAVE_REQ)
        if got in (0, request):
            if now - when < ANSWER_WAIT:
                return []
            if got == request:  # (never taken: a window, a screen or an enemy's turn in the way)
                gd.guest.write(self._hdr + TSR_SAVE_REQ, struct.pack("<H", 0))
            self._asked = None
            return [f"{kind} save: not made, the game was busy"] if request == REQ_SAVE and kind == QUICK else []
        gd.guest.write(self._hdr + TSR_SAVE_REQ, struct.pack("<H", 0))
        self._asked = None
        if request == REQ_LOAD:
            return []
        if got == DONE:
            if kind == AUTO:
                self._auto_at = now
            self.label = "Quick save" if kind == QUICK else "Autosave"
            return [f"{self.label}: \"{name}\" (the QUICK page, slot {slot})"]
        if got == IN_FIGHT:
            return ["Quick save: not in a fight (the game saves none there)"] if kind == QUICK else []
        return [f"{kind} save: the game could not write {slot_file(slot)}"]

    def _page_back(self, gd) -> None:
        """The save window never opens on the QUICK page by itself: with the window shut (the map's
        loop running, the game on the map) a page left on QUICK (after a quick load, or a look at
        the page) is made the page of 1 to 4 shown last, so a save made by hand in the window
        doesn't land in a slot that is written over in turn. (F9 makes the page QUICK as it opens
        the window; the QUICK button and PgDn still show it.)"""
        if self._asked is not None or not self._running or gd._word(SCREEN_IS) != ON_MAP:
            return
        now = gd.guest.read(gd.ds * 16 + NAME_FIND, 1)
        if now in KEPT_PAGES:
            self._page_was = now
        elif now == LETTER.encode("ascii"):
            for at in (NAME_FIND, NAME_SAVE):
                gd.guest.write(gd.ds * 16 + at, self._page_was)

    # ---- the policy --------------------------------------------------------------------------

    def _disk_ok(self, game_dir: str, out: List[str], say: bool) -> bool:
        free = disk_free(game_dir)
        if free is None or free >= DISK_LEAST:
            self._said_disk = False
            return True
        if say or not self._said_disk:
            out.append(f"No quick save or autosave: the disk is nearly full ({free // 1024} KB free)")
        self._said_disk = True
        return False

    def _auto_due(self, gd, loading: bool, now: float) -> Optional[str]:
        """What an autosave due now is for (its name's middle), or None."""
        region = gd.region()
        fighting = gd.fight_on()
        if loading or self._region is None:  # (a game loaded, or the first look: where it is, no save)
            self._region, self._region_at = region, None
            self._fought, self._fight_over_at = fighting, None
            return None
        if fighting:
            self._fought, self._fight_over_at = True, None
            self._region_at = None if region == self._region else self._region_at
            return None
        ready = self._running and gd._word(SCREEN_IS) == ON_MAP and not self._camping(gd)
        spaced = self._auto_at is None or now - self._auto_at >= AUTO_GAP
        if region != self._region:
            if not ready:
                self._region_at = None  # (counted again from when the map is back)
                return None
            if self._region_at is None:
                self._region_at = now
            if now - self._region_at >= AREA_WAIT:
                self._region, self._region_at = region, None
                self._fought, self._fight_over_at = False, None
                return journal.region_name(region)  # (always: coming in is worth its save)
            return None
        if self._fought:
            if not ready:
                self._fight_over_at = None
                return None
            if self._fight_over_at is None:
                self._fight_over_at = now
            if now - self._fight_over_at >= FIGHT_WAIT:
                self._fought, self._fight_over_at = False, None
                return "after a fight" if spaced else None
        return None

    def tick(self, gd, tsr_hdr: Optional[int], game_dir: Optional[str], loading: bool, now: float) -> List[str]:
        """One pass: the keys counted since the last, an autosave due, a request's answer."""
        if tsr_hdr is None or gd is None or not game_dir:
            return []
        out: List[str] = []
        if tsr_hdr != self._hdr:  # (a new DSCLOG: nothing asked, nothing pressed yet)
            self._hdr, self._seq, self._keys_set, self._ticks, self._asked = tsr_hdr, None, None, None, None
        self._set_keys(gd)
        ticks = self._word(gd, TSR_MAIN_TICKS)
        self._running, self._ticks = self._ticks is not None and ticks != self._ticks, ticks
        seq = struct.unpack("<HH", gd.guest.read(self._hdr + TSR_QS_SEQ, 4))
        pressed = (False, False) if self._seq is None else (seq[0] != self._seq[0], seq[1] != self._seq[1])
        self._seq = seq
        if self._asked is not None:
            out += self._answer(gd, now)
        self._page_back(gd)
        due = self._auto_due(gd, loading, now) if self.auto else None
        if not self.auto:
            self._region = None  # (switched on later: from where the party is then)
        if self._asked is not None or loading:
            return out  # (one at a time; a key pressed meanwhile is dropped)
        line = None
        if self.keys and pressed[0]:
            if gd.fight_on():
                line = "Quick save: not in a fight (the game saves none there)"
            elif self._disk_ok(game_dir, out, True):
                line = self._ask_save(gd, QUICK, next_slot(game_dir, QUICK_SLOTS), quick_name(gd.game_time()), now)
        elif self.keys and pressed[1]:
            line = self._ask_load(gd, game_dir, now)
        elif due is not None and self._disk_ok(game_dir, out, False):
            line = self._ask_save(gd, AUTO, next_slot(game_dir, AUTO_SLOTS), auto_name(due, gd.game_time()), now)
        if line:
            out.append(line)
        return out
