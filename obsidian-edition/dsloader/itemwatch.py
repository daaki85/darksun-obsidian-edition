"""Items that go missing (itemwatch.py): the party's items watched, and a report written when
one is gone from the whole party, like the crash reports, so a disappearance can be looked
into afterwards (an Inix Hide armour once vanished with nothing to show why).

The watch takes a snapshot of every party member's items each second (GameData.party_items:
the item's number in the game's item table, who has it and where). An item whose number is
in no member's list for GONE_WAIT seconds is gone from the party. The report says what the
Loader can tell about where it went: the item's record now (the same item outside the party,
as when it was dropped, sold, given or stolen; or a record freed or reused, as when it was
destroyed, used up or discarded by the game), the owner's items before and after, the whole
party's, the game's time, region and fight state, the switches, and the dice log's and the
dialogue's last lines. It is saved as crash-logs/item-YYYY-MM-DD-HHMMSS.txt and the dice log
says so. An item that comes back within GONE_WAIT (moved between screens) is not news; nor is
one that turns up with another member (handed over), under its own number or, as the game may
move it, under another (the same item, a new number, within the wait: ARRIVED).

Only a loss with nothing ordinary to show for it is written as a report; the rest pass in
silence (each was a dice log line, which a shop or a hand-over made a stream of): an item that
still exists outside the party (dropped, put in a chest, given, sold or stolen), one that is used
up or taken by a script (fruit and quest items, arrows, scrolls), one a spell made (Shillelagh,
the spell's Flame Blade, Spiritual Hammer), one sold (the party's money went up), and a weapon
that broke (a Broken Weapon came in its place). A game loaded (the game's clock gone back)
starts the watch afresh.
"""

import collections
import struct
import time
from typing import Deque, Dict, List, Optional, Tuple

from . import game as game_mod
from .game import ItemSeen

CHECK_INTERVAL = 1.0   # seconds between snapshots
GONE_WAIT = 2.0        # seconds an item must be missing before it counts as gone
# A game loaded with the same party, from later on: the clock moved on past what play does in a
# second (game seconds; a rest jumps hours, but takes no items), or most of the items gone at once
CLOCK_JUMP = 600
ARRIVED_KEEP = 10.0    # seconds an item new to the party is kept in mind, to match a hand-over (the
                       # Loader busy, the vanish may be confirmed well after the item reappeared)
MOST_GONE = 3          # (at least this many, and over half the party's items)
DICE_LINES, TALK_LINES = 300, 80   # context kept for the report, as the crash report keeps it
# item types whose going is ordinary: fruit and quest items (60), arrows (62), scrolls (96),
# psionic scrolls (99) and grain (110), used up or taken by scripts; and the items spells make,
# Shillelagh (28), Flame Blade (29) and Spiritual Hammer (30), gone when the spell ends
USED_UP = frozenset((60, 62, 96, 99, 110))
SPELL_MADE = frozenset((28, 29, 30))
BROKEN = frozenset((93, 107))  # (a Broken Weapon: the game's, in place of one that broke)


class ItemWatch:
    def __init__(self, folder: Optional[str] = None):
        self.folder = folder              # where reports go (None: the crash-logs folder)
        self._seen: Dict[int, ItemSeen] = {}
        self._missing: Dict[int, Tuple[ItemSeen, float]] = {}
        self._next = 0.0
        self._clock: Optional[int] = None  # (the game's clock at the last look)
        self._money: Optional[int] = None  # (the party's money at the last look)
        self._gains: List[Tuple[float, int]] = []  # (each rise in the party's money: when, by how much)
        self._broke_at: Dict[int, float] = {}  # (member: when a Broken Weapon last came to them)
        self._arrived: Dict[Tuple[int, ...], float] = {}  # (an item new to the party: when)
        self.dice: Deque[str] = collections.deque(maxlen=DICE_LINES)
        self.talk: Deque[str] = collections.deque(maxlen=TALK_LINES)
        self.reports: List[str] = []      # the paths written (tests read them)

    def reset(self) -> None:
        """Forget everything (a game was loaded: the party's items are a new set)."""
        self._seen.clear()
        self._missing.clear()
        self._clock = self._money = None
        self._gains.clear()
        self._broke_at.clear()
        self._arrived.clear()

    def remember(self, lines: List[str]) -> None:
        self.dice.extend(lines)

    def remember_talk(self, entries) -> None:
        for e in entries:
            for line in (e.text, *e.replies, e.chosen and "You chose: " + e.chosen):
                if line:
                    self.talk.append(line)

    def check(self, data, now: float, settings: Optional[dict] = None) -> List[str]:
        """Look at the party's items; lines for the dice log when one is gone."""
        if now < self._next:
            return []
        self._next = now + CHECK_INTERVAL
        try:
            items = data.party_items()
        except Exception:                 # (a half-loaded game: try again next time)
            return []
        current = {i.index: i for i in items}
        clock, money = _read(data.game_time), _read(getattr(data, "money", None))
        if clock is not None and self._clock is not None and not 0 <= clock - self._clock <= CLOCK_JUMP:
            self.reset()                  # (the clock gone back, or on further than play takes it: a game loaded)
        gone = [index for index in self._seen if index not in current]
        if len(gone) >= MOST_GONE and 2 * len(gone) > len(self._seen):
            self.reset()                  # (most of the items gone at once: a game loaded)
        if money is not None and self._money is not None and money > self._money:
            self._gains.append((now, money - self._money))
        self._clock, self._money = clock, money
        if not self._seen:                # the first look, or after a reset
            self._seen = current
            return []
        for i in current.values():
            if i.index not in self._seen:
                self._arrived[_same(i.record)] = now
                if i.type in BROKEN:
                    self._broke_at[i.member] = now
        # (what happened as an item went: within the wait it took to count as gone)
        recent = lambda at: at is not None and now - at <= GONE_WAIT + CHECK_INTERVAL
        self._gains = [(at, gain) for at, gain in self._gains if recent(at)]
        gains = {gain for _, gain in self._gains}
        broke = {m for m, at in self._broke_at.items() if recent(at)}
        self._arrived = {k: at for k, at in self._arrived.items() if now - at <= ARRIVED_KEEP}
        out: List[str] = []
        for index, was in list(self._seen.items()):
            if index in current:
                self._missing.pop(index, None)
                continue
            since = self._missing.setdefault(index, (was, now))[1]
            if now - since < GONE_WAIT:
                continue
            del self._missing[index]
            if _same(was.record) in self._arrived:
                continue              # (handed over: the same item with another member, a new number)
            out += self._gone(data, was, current, now, settings, bool(gains & sale_prices(was.record)), was.member in broke)
        # what is there now is what the next look compares with (the gone ones are reported,
        # the ones still inside GONE_WAIT stay remembered through _missing)
        kept = {i: was for i, (was, _) in self._missing.items()}
        self._seen = {**kept, **current}
        return out

    def _gone(self, data, was: ItemSeen, current: Dict[int, ItemSeen], now: float,
              settings: Optional[dict], sold: bool = False, broke: bool = False) -> List[str]:
        try:
            record = data.item_record(was.index)
        except Exception:
            record = b""
        fate = describe_fate(was, record)
        where = f"{was.owner}'s {was.slot}" if was.slot else f"{was.owner}'s pack"
        if ordinary_loss(was, record, sold, broke):
            return []
        text = item_report(was, record, fate, current, data, now, settings, list(self.dice), list(self.talk))
        try:
            from . import launch
            path = launch.write_crash_report(text, time.time(), self.folder or launch.CRASH_DIR, "item")
        except OSError as e:
            path = f"(could not be saved: {e})"
        self.reports.append(path)
        return [f"{was.label} is gone from {where}: {fate}. An item report is saved in {path}."]


ITEM_VALUE = 0x06  # an item's price, in its record (npcitems.ITEM_VALUE)


def sale_prices(record: bytes) -> set:
    """What the party's money goes up by when a shop buys the item: its price (the game's), or
    60% of it (the CHA rule's: prices.sell_price)."""
    from . import prices
    if len(record) < ITEM_VALUE + 2:
        return set()
    value = struct.unpack_from("<H", record, ITEM_VALUE)[0]
    return {value, prices.sell_price(value)} - {0}


def _same(record: bytes) -> Tuple[int, ...]:
    """What tells an item from another whatever its number, owner and place: its picture, type,
    name and plus (the rest of its record the game may change as the item moves)."""
    if len(record) < game_mod.ITEM_SIZE:
        return ()
    return (struct.unpack_from("<H", record, 0)[0], struct.unpack_from("<H", record, game_mod.ITEM_TYPE)[0],
            struct.unpack_from("<H", record, game_mod.ITEM_NAME)[0], record[game_mod.ITEM_PLUS])


def _read(get) -> Optional[int]:
    try:
        return get() if get is not None else None
    except Exception:
        return None


def ordinary_loss(was: ItemSeen, record: bytes, sold: bool, broke: bool) -> Optional[str]:
    """Why the item's going is nothing to report, or None (a report is written)."""
    if len(record) >= game_mod.ITEM_SIZE:
        typ, name = struct.unpack_from("<HH", record, game_mod.ITEM_TYPE)[0], \
            struct.unpack_from("<H", record, game_mod.ITEM_NAME)[0]
        if record == was.record or (typ == was.type and name == struct.unpack_from("<H", was.record, game_mod.ITEM_NAME)[0]):
            return "it is outside the party (dropped, put away, given or stolen)"
    if was.type in USED_UP:
        return "used up, or taken for a quest"
    if was.type in SPELL_MADE:
        return "a spell made it, and the spell is over"
    if broke:
        return "it broke (a Broken Weapon in its place)"
    if sold:
        return "sold (the party's money went up)"
    return None


def describe_fate(was: ItemSeen, record: bytes) -> str:
    """What the item's record says now, in a few words."""
    if len(record) < game_mod.ITEM_SIZE:
        return "its record could not be read"
    if record == was.record:
        return "the item still exists outside the party, as it was (dropped, sold, given or stolen)"
    typ, = struct.unpack_from("<H", record, game_mod.ITEM_TYPE)
    name, = struct.unpack_from("<H", record, game_mod.ITEM_NAME)
    was_name, = struct.unpack_from("<H", was.record, game_mod.ITEM_NAME)
    if typ == was.type and name == was_name:
        return "the item still exists outside the party, its record changed (see the bytes below)"
    if not any(record):
        return "its record is empty: the game freed it (destroyed, used up or discarded)"
    return "its record now holds another item: the game freed it and reused the number"


def item_report(was: ItemSeen, record: bytes, fate: str, current: Dict[int, ItemSeen], data,
                now: float, settings: Optional[dict], dice: List[str], talk: List[str]) -> str:
    stamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    where = f"{was.owner}'s {was.slot} slot" if was.slot else f"{was.owner}'s pack (not worn)"
    lines = [f"Obsidian Edition item report, {stamp}", "",
             f"{was.label} (item {was.index}, type {was.type}) is gone from {where}.",
             f"What its record says now: {fate}.", ""]
    lines += _state_lines(data)
    lines += ["", "The item's record when last seen:", "  " + was.record.hex(" "),
              "The record at that number now:    ", "  " + (record.hex(" ") if record else "(unreadable)"),
              "Its type's record:", "  " + was.kind.hex(" ")]
    mine = [i for i in current.values() if i.member == was.member]
    lines += ["", f"{was.owner}'s items now:"] + (_item_lines(mine) or ["  (none)"])
    lines += ["", "The party's items now:"] + (_item_lines(list(current.values())) or ["  (none)"])
    if settings is not None:
        try:
            from . import launch
            lines += ["", "Switches (as set on the Options tab, else the default):"]
            lines += [f"  {key}: {value!r}" for key, value in sorted(launch.effective_switches(settings).items())]
        except Exception:
            pass
    lines += ["", "The dice log's last lines:", "\n".join(dice) or "(empty)",
              "", "The dialogue's last lines:", "\n".join(talk) or "(empty)", ""]
    return "\n".join(lines)


def _state_lines(data) -> List[str]:
    out = []
    for label, get in (("Game time", lambda: game_mod.game_time(data.game_time()) if data.game_time() is not None else None),
                       ("Region", lambda: f"{data.region()} (RGN{data.region():02X}.GFF)"),
                       ("In a fight", lambda: "yes" if data.in_combat() else "no"),
                       ("Whose turn", lambda: data.combatant_name(data.whose_turn()) if data.in_combat() and data.whose_turn() is not None else None)):
        try:
            value = get()
        except Exception:
            value = None
        if value is not None:
            out.append(f"{label}: {value}")
    return out


def _item_lines(items: List[ItemSeen]) -> List[str]:
    return [f"  {i.owner}: {i.label} (item {i.index}, {i.slot if i.slot else 'carried'})"
            for i in sorted(items, key=lambda i: (i.member, i.slot is None, i.index))]
