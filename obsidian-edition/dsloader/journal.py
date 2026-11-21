"""The journal: what was said and done in a game, kept on disk and following the game's saves.

The dice log hands it every dialogue (who spoke, what, the replies and the one chosen) and every
message box, each with the game's clock and region as it came (DiceLog._journal_note). Each is an
entry in JOURNAL (a line of JSON each, only ever added to): its id, its PARENT (the entry before it
in that game) and what it holds. A game's journal is the chain from its newest entry (the HEAD)
back through the parents, so the file holds every game played and every branch of each (a save
loaded and played on another way) without one's lines showing in another's.

Which chain is the game's own, the game's saves say: the head's id is kept in two of the game's
global numbers (NUMBERS: words 198 and 199 of the 200 a save keeps, SAVE chunk 30; the game's
scripts use 0-136, tests/test_journal.py), written whenever an entry is added. A save made then
holds it; when the id in memory is not the one last written, a game was loaded (or begun: 0), and
the journal shows that id's chain (sync). The numbers have no place in memory at times (their
pointer is null: game.number), so an entry can be added before its id is written: when a load is
seen and the loaded id is an entry of the chain shown till then, entries after it with a strictly
earlier clock can be kept. A save and a later entry can have the same game second.
"""

import json
import os
import re
import struct
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Tuple

from . import game

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FOLDER = os.path.join(HERE, "Journal")
JOURNAL = os.path.join(FOLDER, "journal.jsonl")
NUMBERS = (198, 199)  # the game's global numbers the head's id is kept in (low word, high word)
NUMBER_COUNT = 200  # the numbers a save keeps (SAVE chunk 30, 400 bytes)
TALK, CHOSEN, MESSAGE, REWARD = "talk", "chosen", "message", "reward"
KINDS = (TALK, CHOSEN, MESSAGE, REWARD)
# a reward's message: the game's routine's ("... receives 200 experience points!") and the ones
# some scripts word themselves ("The party gains 4,000 exp!", "you earn 6,000 EXP!")
_REWARD = re.compile(r"\b(receives?|gains?|earns?)\b[^.!?]*?\b\d[\d,]*\s*(experience|exp)\b", re.I)
# message boxes that say nothing of the story (the game's own notices)
_NOTICES = re.compile(r"^(saving game|game saved|loading game|can't save during combat|disk space low)", re.I)
# the regions with a name (the rest: "Area 1Fh"); playtest/PLAYTESTING.md's route
REGIONS = {0x29: "The slave pens", 0x2A: "The arena"}
STEADY = 2  # looks in a row that must read the same id before it is believed (a game being loaded)
UNSYNCED_MOST = 500  # entries kept in memory while the game's numbers can't be read


def region_name(region: Optional[int]) -> str:
    if region is None:
        return ""
    return REGIONS.get(region) or f"Area {region:02X}h"


def day_of(clock: Optional[int]) -> Optional[int]:
    return None if clock is None else max(0, clock) // 86400 + 1


def time_of(clock: Optional[int]) -> str:
    """ "Day 3, 14:20" (as the combat log's header, combatlog.clock_line), or "" with no clock."""
    if clock is None:
        return ""
    rest = max(0, clock) % 86400
    return f"Day {day_of(clock)}, {rest // 3600:02d}:{rest % 3600 // 60:02d}"


def kind_of_message(text: str) -> Optional[str]:
    """A message box's kind: a reward, a message, or None for the game's own notices."""
    said = " ".join(text.split())
    if not said or _NOTICES.match(said):
        return None
    return REWARD if _REWARD.search(said) else MESSAGE


class Entry:
    """One thing said or done. Its fields are the JSON line's."""

    __slots__ = ("id", "parent", "kind", "clock", "region", "portrait", "speaker", "text", "replies", "title")

    def __init__(self, id: int = 0, parent: int = 0, kind: str = TALK, clock: Optional[int] = None,
                 region: Optional[int] = None, portrait: Optional[int] = None, speaker: str = "",
                 text: str = "", replies: Sequence[str] = (), title: str = ""):
        self.id, self.parent, self.kind, self.clock, self.region = id, parent, kind, clock, region
        self.portrait, self.speaker, self.text, self.replies, self.title = portrait, speaker, text, list(replies), title

    def line(self) -> str:
        out = {"id": self.id, "parent": self.parent, "kind": self.kind}
        for name in ("clock", "region", "portrait"):
            if getattr(self, name) is not None:
                out[name] = getattr(self, name)
        for name in ("speaker", "text", "replies", "title"):
            if getattr(self, name):
                out[name] = getattr(self, name)
        return json.dumps(out, ensure_ascii=False, separators=(",", ":"))

    @classmethod
    def parse(cls, line: str) -> Optional["Entry"]:
        """The entry a line holds, or None for one that isn't an entry (cut short, or not ours)."""
        try:
            d = json.loads(line)
            if not isinstance(d, dict) or d.get("kind") not in KINDS:
                return None
            ident, parent = d["id"], d.get("parent", 0)
            if not (isinstance(ident, int) and isinstance(parent, int) and 0 < ident <= 0xFFFFFFFF and 0 <= parent < ident):
                return None
            whole = lambda v: v if isinstance(v, int) and not isinstance(v, bool) else None
            return cls(ident, parent, d["kind"], whole(d.get("clock")), whole(d.get("region")),
                       whole(d.get("portrait")), str(d.get("speaker", "")), str(d.get("text", "")),
                       [str(r) for r in d.get("replies", []) if isinstance(r, str)], str(d.get("title", "")))
        except (ValueError, KeyError, TypeError):
            return None

    def matches(self, wanted: str) -> bool:
        """WANTED (any case) is in what the entry says or who says it."""
        wanted = wanted.casefold()
        return any(wanted in part.casefold() for part in (self.speaker, self.text, self.title, *self.replies))


def read_head(gd) -> Optional[int]:
    """The id in the game's numbers now, or None while they have no place in memory."""
    numbers = game.far_pointer(gd.guest, gd.ds, game.NUMBERS_PTR)
    if not numbers:
        return None
    return struct.unpack("<I", gd.guest.read(numbers + NUMBERS[0] * 2, 4))[0]


def write_head(gd, head: int) -> bool:
    """HEAD put in the game's numbers; False while they have no place in memory."""
    numbers = game.far_pointer(gd.guest, gd.ds, game.NUMBERS_PTR)
    if not numbers:
        return False
    gd.guest.write(numbers + NUMBERS[0] * 2, struct.pack("<I", head))
    return True


class Journal:
    """The journal's file and the chain shown. `changed` counts the times the chain shown became
    another (a game loaded): whoever shows it draws it again then; `added` are the entries added to
    the chain since take_added."""

    def __init__(self, path: Optional[str] = None):
        self.path = JOURNAL if path is None else path
        self.entries: Dict[int, Entry] = {}
        self.head: Optional[int] = None  # the chain shown: its newest entry's id (0: none yet); None: not known yet
        self.written: Optional[int] = None  # the id last seen or put in the game's numbers
        self.changed = 0
        self.failed = False  # the file couldn't be written the last time it was tried
        self._added: List[Entry] = []
        self._unsynced: List[Entry] = []  # entries from before the head was known (ids and parents not given yet)
        self._unwritten: List[Entry] = []  # entries the file refused, for the next try
        self._seen: Tuple[Optional[int], int] = (None, 0)  # the id read last, and the looks in a row it was read
        self._next = 1
        self._refresh_needed = True
        self._refresh()  # for display before attaching; refresh again under the game lock
        self._refresh_needed = True

    # ---- the file ---------------------------------------------------------------

    def _refresh(self) -> bool:
        """Refresh the ID allocation before the session writes, even for a window opened earlier."""
        entries = {}
        try:
            with open(self.path, encoding="utf-8", errors="replace") as f:
                for line in f:
                    entry = Entry.parse(line)
                    if entry is not None:
                        entries[entry.id] = entry
        except FileNotFoundError:
            pass
        except OSError:
            self.failed = True
            return False
        for pending in self._unwritten:
            existing = entries.get(pending.id)
            if existing is not None and existing.line() != pending.line():
                self.failed = True
                return False  # keep the pending entries without overwriting another game's IDs
        self.entries.update(entries)
        self._next = max(self._next, max(self.entries, default=0) + 1)
        self._refresh_needed, self.failed = False, False
        return True

    def flush(self) -> None:
        """What the file doesn't hold yet, written now."""
        self._write()

    def _write(self) -> bool:
        """The entries not yet in the file, added to it; kept for the next try if it can't be."""
        if not self._unwritten:
            return True
        if self._refresh_needed and not self._refresh():
            return False
        try:
            os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
            with open(self.path, "a+b") as f:
                if f.tell():
                    f.seek(-1, os.SEEK_END)
                    if f.read(1) != b"\n":
                        f.write(b"\n")  # separate a partial previous record from the retry
                f.write("".join(entry.line() + "\n" for entry in self._unwritten).encode("utf-8"))
                f.flush()
                os.fsync(f.fileno())
            self._unwritten, self.failed = [], False
            return True
        except OSError:
            self.failed = True
            return False

    # ---- entries ----------------------------------------------------------------

    def add(self, kind: str, text: str = "", clock: Optional[int] = None, region: Optional[int] = None,
            portrait: Optional[int] = None, speaker: str = "", replies: Sequence[str] = (), title: str = "") -> Entry:
        """An entry added after the chain's newest. Before the game's id is known (sync) it waits,
        and joins the chain then."""
        entry = Entry(0, 0, kind, clock, region, portrait, speaker, text, replies, title)
        if self.written is None or self.head is None:
            self._unsynced.append(entry)
            del self._unsynced[:-UNSYNCED_MOST]
        else:
            self._append(entry)
        return entry

    def _append(self, entry: Entry) -> None:
        entry.id, entry.parent = self._next, self.head or 0
        self._next += 1
        self.entries[entry.id] = entry
        self.head = entry.id
        self._added.append(entry)
        self._unwritten.append(entry)

    def chain(self, head: Optional[int] = None) -> List[Entry]:
        """The entries of the chain ending at HEAD (by default the one shown), oldest first."""
        out, at = [], self.head if head is None else head
        while at and at in self.entries:
            out.append(self.entries[at])
            at = self.entries[at].parent
        out.reverse()
        return out

    def shown(self) -> List[Entry]:
        """The chain to show: the game's, or until it is known the one last added to."""
        return self.chain(max(self.entries, default=0) if self.head is None else self.head)

    def take_added(self) -> List[Entry]:
        out, self._added = self._added, []
        return out

    # ---- following the game's saves ---------------------------------------------

    def reset(self) -> None:
        """The game was started again (or the Loader attached anew): the id in its numbers is
        looked at afresh, and isn't a load."""
        self.written, self._seen = None, (None, 0)
        self._refresh_needed = True

    def sync(self, read: Callable[[], Optional[int]], write: Callable[[int], bool], clock: Optional[int]) -> None:
        """One look at the game's numbers (READ: the id there, None while they can't be read; WRITE
        puts one there). An id other than the one last written, read STEADY times running, is a
        game loaded or begun: its chain is shown from then. Then the chain's head is written, if
        it isn't there."""
        seen = read()
        if seen is None:
            self._seen = (None, 0)
            if self.head is not None:
                self._write()
            return
        self._seen = (seen, self._seen[1] + 1 if self._seen[0] == seen else 1)
        if seen != self.written or self.head is None:
            if self._seen[1] < STEADY:
                return
            if self._refresh_needed and not self._refresh():
                return
            self._follow(seen, clock)
            self.written = seen
        if self._write() and self.head != seen and write(self.head):
            self.written, self._seen = self.head, (self.head, STEADY)

    def _follow(self, seen: int, clock: Optional[int]) -> None:
        """The chain shown becomes SEEN's (see the module's words for the entries kept past it)."""
        before = self.head
        head = seen
        if seen and before and seen != before and clock is not None:
            later = self.chain(before)
            ids = [entry.id for entry in later]
            if seen in ids:  # (the save is of the game played till now)
                for entry in later[ids.index(seen) + 1:]:
                    if entry.clock is None or entry.clock >= clock:
                        break
                    head = entry.id
        self._next = max(self._next, seen + 1)  # (an id a save holds is never given to another entry)
        if head != before:
            if before is not None:
                self.changed += 1
                self._added = []
            self.head = head
        waiting, self._unsynced = self._unsynced, []
        for entry in waiting:  # (said before the game's id was known: this game's)
            self._append(entry)

    def close(self) -> None:
        """The Loader is done: what waits is written (entries whose game was never known as their
        own chain, so they are not lost)."""
        if self._unsynced:
            if self._refresh_needed and not self._refresh():
                return
            if self.written is None or self.head is None:
                self.head = 0
            waiting, self._unsynced = self._unsynced, []
            for entry in waiting:
                self._append(entry)
        self._write()


def text_of(entries: Iterable[Entry], speaker: Callable[[Entry], str] = lambda e: e.speaker) -> str:
    """The entries as plain text (the Journal tab's Save, and the tests)."""
    out: List[str] = []
    for kind, text in rows(entries, speaker):
        out.append(text if kind != "gap" else "")
    return "\n".join(out).strip() + "\n"


def place(entry: Entry) -> Tuple[Optional[int], Optional[int]]:
    """An entry's day and region: a heading is shown where they change."""
    return day_of(entry.clock), entry.region


def rows(entries: Iterable[Entry], speaker: Callable[[Entry], str] = lambda e: e.speaker,
         where: Tuple[Optional[int], Optional[int]] = (None, None)) -> List[Tuple[str, str]]:
    """The entries as rows to show, each (what it is, its text): "day" a new day or area's heading
    (WHERE: the place of the entry shown before these), "speaker", "text", "reply" (a reply
    offered), "chosen", "reward", "message" and "gap" (a blank line)."""
    out: List[Tuple[str, str]] = []
    for entry in entries:
        here = place(entry)
        if here != where and here != (None, None):
            where = here
            parts = [f"Day {here[0]}" if here[0] is not None else "", region_name(here[1])]
            out.append(("day", " - ".join(p for p in parts if p)))
            out.append(("gap", ""))
        if entry.kind == CHOSEN:
            if out and out[-1][0] == "gap":
                out.pop()  # (under the replies it answers)
            out.append(("chosen", f"  You chose: {entry.text}"))
        elif entry.kind in (MESSAGE, REWARD):
            out.append((entry.kind, entry.text))
        else:
            out.append(("speaker", speaker(entry) or "Narration"))
            if entry.text:
                out.append(("text", entry.text))
            if entry.title:
                out.append(("reply", f"  ({entry.title})"))
            out += [("reply", f"  {n}. {reply}") for n, reply in enumerate(entry.replies, 1)]
        out.append(("gap", ""))
    return out


def chosen(entries: Sequence[Entry], kinds: Optional[Sequence[str]] = None, wanted: str = "") -> List[Entry]:
    """The entries of KINDS (None: all) that hold WANTED. A reply chosen goes with the talk it
    answers: shown when that talk is, and a talk is shown when its answer holds WANTED too."""
    out: List[Entry] = []
    for i, entry in enumerate(entries):
        if entry.kind == CHOSEN:
            if out and i and out[-1] is entries[i - 1]:
                out.append(entry)
            continue
        if kinds is not None and entry.kind not in kinds:
            continue
        answer = entries[i + 1] if i + 1 < len(entries) and entries[i + 1].kind == CHOSEN else None
        if not wanted or entry.matches(wanted) or (answer is not None and answer.matches(wanted)):
            out.append(entry)
    return out
