"""The Loader's window (tkinter), in the colours of the game's own screens.

Left: the party, a card for each character (partyview.py) and every field the
layout maps in a table. For Shattered Lands the party is found automatically;
other layouts locate a character by name (linked records such as the character
sheet are then found automatically).
Right: the dice log (when the game was started with DSCLOG), the dialogue, the
spells, the memory tools (name search, the layout's buttons, and a live hex
view of a record that highlights bytes as they change; click a byte to see it
decoded as each value type) and the Options tab.
"""

import os
import re
import struct
import subprocess
import sys
import time
import tkinter as tk
import webbrowser
from collections import deque
from pathlib import Path
from tkinter import filedialog, messagebox, simpledialog, ttk
from tkinter import font as tkfont
from typing import Callable, Dict, List, Optional, Set, Tuple

from . import __version__, art, combatlog, dicelog, dosboxx, journal, ledger, freeze, game, kits, launch, manual, midiout, namedsaves, partyview, quests, rings, spellbook, theme, values
from .dicelog import DiceLog, DiceLogError
from .guestmem import GuestMemory
from .layout import Layout
from .process import ProcessError

REFRESH_MS = 500
SAVES_EVERY = 3.0  # seconds between looks at the game's saves (namedsaves.py)
DICE_MS = 50
RETRY_SECONDS = 2.0
MAX_LOG_LINES = 3000
# the Journal tab's Show box: its choices and the kinds of entry each shows (None: all)
JOURNAL_SHOWS = (("Everything", None), ("Talk", (journal.TALK,)),
                 ("Rewards", (journal.REWARD,)), ("Rewards and messages", (journal.REWARD, journal.MESSAGE)))
JOURNAL_QUESTS = "Quests"  # the Show box's last choice: the game's quests in place of the entries (quests.py)
QUESTS_KEPT_EVERY = 5.0  # seconds between writings of the quests' last reading (quests.save_snapshot)
QUESTS_AS_READ = "The game can't be read just now: these are the quests as the Loader last read them from it."
QUESTS_UNREAD = ("The game's flags have not been read for this journal: only the quests whose rewards "
                 "the journal holds are shown.")
HIGHLIGHT_SECONDS = 3.0
HEX_PREFIX = 17  # width of "+0040  0012a3f0  "
MAX_HITS = 500
# what Help opens: the manual's start page, manual/index.html beside the Loader (dsloader.manual)
HELP_PAGE = manual.START


def _printable(data: bytes) -> str:
    return "".join(chr(b) if 32 <= b < 127 else "." for b in data)


def _query_bytes(text: str) -> bytes:
    """Search text as bytes: plain text, or "hex:" followed by hex byte values."""
    if text.lower().startswith("hex:"):
        return bytes.fromhex(text[4:])
    return text.encode("cp437", errors="replace")


# the game window's sizes (DOSBox scales the game's 320x200, with the aspect corrected)
WINDOW_CHOICES = {"Single (320x240)": 1, "Double (640x480)": 2, "Triple (960x720)": 3, "Quadruple (1280x960)": 4, "Full screen": None}

def tabs_width(tabs: "ttk.Notebook") -> int:
    """The width TABS needs to show every tab's name whole, in the tabs' own font: each name with
    its padding and border (theme.TAB_PADDING, TAB_EDGES), and the row's margins."""
    style = ttk.Style(tabs)
    font = tkfont.Font(root=tabs, font=style.lookup("TNotebook.Tab", "font") or "TkDefaultFont")
    each = 2 * theme.TAB_PADDING[0] + theme.TAB_EDGES
    return sum(font.measure(tabs.tab(tab, "text")) + each for tab in tabs.tabs()) + 24


class Viewer:
    def __init__(self, root: tk.Tk, layout: Layout, connect: Callable[[], GuestMemory],
                 connect_pid: Optional[Callable[[int], GuestMemory]] = None, dosbox=None):
        self.root = root
        self.layout = layout
        self.connect = connect
        # (the DOSBox this window, or the launch before it, started: found by its pid, so that another
        # DOSBox running beside it doesn't stop the attach)
        self.connect_pid = connect_pid
        self.guest: Optional[GuestMemory] = None
        self.hits: List[int] = []
        self.hex_start = 0  # guest address of the first byte in the hex view
        self.hex_data = b""
        self.prev_hex: Dict[int, int] = {}  # guest address -> last byte value
        self.changed_at: Dict[int, float] = {}  # guest address -> time it last changed
        self.ds: Optional[int] = None  # the game's data segment, once found
        self.dice: Optional[DiceLog] = None
        self.next_try = 0.0  # when to retry connecting / attaching
        self.dosbox = dosbox  # the game, when started from here (Start the game, or `launch`)
        self._game_dir, self._started, self._refused = None, 0.0, []  # (for a crash report)
        self._learned_unsaved = False  # (names or pockets the settings file refused, last pass)
        # the game's portraits and font, from the player's own install (if it can be found)
        self.art = art.GameArt.of(launch.find_game_dir())
        # (Tk shows an image only while it's referenced: one for each portrait at each size, shared
        # by every line it is shown on)
        self._images: Dict[Tuple[int, int], tk.PhotoImage] = {}
        self._widest: Tuple[str, str] = ("", "")  # the All fields table's longest label and value

        root.title(f"{theme.NAME} {__version__} - {layout.game or 'party viewer'}")
        root.geometry("1320x780")
        root.minsize(1080, 640)  # (smaller, the right-hand tabs and rows of buttons lose their ends)
        theme.apply(root)
        root.protocol("WM_DELETE_WINDOW", self.close)
        self._build()
        self.reconnect()
        if self._options_unread:
            self.status.set(f"The Options tab shows the defaults: {self._options_unread}. A switch you change is "
                            "saved alone, the rest of your settings kept; open the Loader again to see them.")
        self._tick()
        self._dice_tick()

    # ---- layout of the window -------------------------------------------------

    def _build(self) -> None:
        self.banner = theme.Banner(self.root)
        self.banner.pack(fill="x")
        if self.art.font:
            self.banner.use_game_font(self.art.font)
        top = ttk.Frame(self.root, padding=(6, 6, 6, 0))
        top.pack(fill="x")
        self.status = tk.StringVar(value="Not connected")
        # on a line of its own, below the buttons, so it never pushes them off at larger text sizes
        ttk.Label(self.root, textvariable=self.status, style="Status.TLabel", padding=(8, 2)).pack(fill="x")
        # the manual (manual/index.html, beside the Loader) in the browser
        ttk.Button(top, text="Help", command=self.open_guide).pack(side="right", padx=(4, 0))
        ttk.Button(top, text="Reconnect", command=self.reconnect).pack(side="right")
        # the game stopped but DOSBox runs on: where it was, its memory and the logs, in a zip
        ttk.Button(top, text="Freeze report", command=self.freeze_report).pack(side="right", padx=(0, 4))
        # for when the Loader was opened on its own: start the game (with the dice log) from here
        self.start_button = ttk.Button(top, text="Start the game", command=self.start_game)
        self.start_button.pack(side="left")
        # text size, also Ctrl + / Ctrl - / Ctrl 0
        ttk.Button(top, text="A+", width=3, command=lambda: self.zoom(1.15)).pack(side="right", padx=(4, 12))
        ttk.Button(top, text="A-", width=3, command=lambda: self.zoom(1 / 1.15)).pack(side="right")
        ttk.Label(top, text="Text size").pack(side="right", padx=4)
        # the size of DOSBox's window, for the next time the game is started from here
        self.window_choice = tk.StringVar(value=self._window_label(launch.load_settings()))
        box = ttk.Combobox(top, textvariable=self.window_choice, values=list(WINDOW_CHOICES), state="readonly",
                           width=24)
        box.pack(side="right", padx=(4, 12))
        box.bind("<<ComboboxSelected>>", self._window_chosen)
        ttk.Label(top, text="Game window").pack(side="right", padx=4)
        for key, factor in (("<Control-plus>", 1.15), ("<Control-equal>", 1.15), ("<Control-KP_Add>", 1.15),
                            ("<Control-minus>", 1 / 1.15), ("<Control-KP_Subtract>", 1 / 1.15),
                            ("<Control-0>", None)):
            self.root.bind_all(key, lambda _e, f=factor: self.zoom(f))

        self.panes = panes = ttk.PanedWindow(self.root, orient="horizontal")
        panes.pack(fill="both", expand=True, padx=6, pady=(0, 6))
        # room for all four characters' columns before the logs take the rest
        self.root.after(200, self._fit_party)

        party_tabs = ttk.Notebook(panes)
        party_tabs.enable_traversal()
        panes.add(party_tabs, weight=1)
        # the party as the game's View Character screen shows it
        self.cards = partyview.PartyCards(party_tabs, self.layout.count)
        party_tabs.add(self.cards, text="Characters", underline=0)
        # every field the layout maps, in a table
        party = ttk.Frame(party_tabs)
        party_tabs.add(party, text="All fields", underline=0)
        self.table = ttk.Treeview(party, show="headings")
        across = ttk.Scrollbar(party, orient="horizontal", command=self.table.xview)
        self.table.configure(xscrollcommand=across.set)
        across.pack(side="bottom", fill="x")
        self.table.pack(fill="both", expand=True)

        self.tabs = tabs = ttk.Notebook(panes)
        panes.add(tabs, weight=1)
        tabs.enable_traversal()  # Ctrl+Tab between tabs, Alt + the underlined letter

        dice = ttk.Frame(tabs, padding=6)
        tabs.add(dice, text="Dice log", underline=5)
        row = ttk.Frame(dice)
        row.pack(fill="x")
        ttk.Button(row, text="Clear", command=self.clear_dice).pack(side="right")
        ttk.Button(row, text="Save...", command=self.save_dice).pack(side="right", padx=4)
        self.dice_status = tk.StringVar(value="Waiting for the game...")
        ttk.Label(row, textvariable=self.dice_status).pack(side="left", fill="x")
        dice_find = ttk.Frame(dice)
        dice_find.pack(fill="x", pady=(4, 0))
        # what the log shows (the game's switches are on the Options tab)
        row = ttk.Frame(dice)
        row.pack(fill="x", pady=(4, 0))
        # the indented lines under a roll (what a THAC0 or save was made of); hiding them leaves
        # the rolls, results, turns and HP
        self.show_details = tk.BooleanVar(value=True)
        ttk.Checkbutton(row, text="Show details (the sums behind each roll)", variable=self.show_details,
                        command=lambda: self.dice_text.tag_configure("detail", elide=not self.show_details.get())
                        ).pack(side="left")
        self.show_all = tk.BooleanVar(value=False)
        ttk.Checkbutton(row, text="Show unlabelled rolls", variable=self.show_all).pack(side="left", padx=(12, 0))
        # the readable layout (ledger.py): the outcome first, the roll and HP in columns, the working
        # under it; off, the log's own lines as they are written
        self.readable = tk.BooleanVar(value=launch.load_settings().get("dice_layout", "readable") == "readable")
        ttk.Checkbutton(row, text="Readable layout", variable=self.readable, command=self._layout_changed
                        ).pack(side="left", padx=(12, 0))
        # the round's order stays here while the log scrolls on: who acts now, who is still to come
        self.round_line = tk.StringVar(value="")
        self.round_label = ttk.Label(dice, textvariable=self.round_line, style="Status.TLabel", wraplength=900,
                                     justify="left")
        self.round_label.pack(fill="x", pady=(4, 0))
        self.round_label.bind("<Configure>", lambda e: self.round_label.configure(wraplength=max(200, e.width - 8)))
        box = ttk.Frame(dice)
        box.pack(fill="both", expand=True, pady=(6, 0))
        self.dice_text = tk.Text(box, font="TkFixedFont", wrap="word", height=20)
        theme.style_text(self.dice_text)
        scroll = ttk.Scrollbar(box, command=self.dice_text.yview)
        self.dice_text.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.dice_text.pack(side="left", fill="both", expand=True)
        self._following: Dict[tk.Text, bool] = {}
        self._follow_end(self.dice_text, scroll)
        for tag, colour in theme.LOG_COLOURS.items():
            self.dice_text.tag_configure(tag, foreground=colour)
        self.dice_text.tag_configure("round", underline=True, spacing1=8)  # a gap before each round
        # names: each party member's in a colour of their own, monsters' in one (configured last,
        # so they show over the line's own colour)
        for n, colour in enumerate(theme.PARTY_COLOURS):
            self.dice_text.tag_configure(f"member{n}", foreground=colour, font="LedgerFixedBold")
        # the readable layout's: its roles' colours, the working smaller, the turn's marker, the
        # event rows' columns (tabs set to the widget's width: _set_columns)
        for role, colour in theme.LEDGER_COLOURS.items():
            self.dice_text.tag_configure(f"lg_{role}", foreground=colour)
        self.dice_text.tag_configure("lg_detail", font="LedgerFixedSmall", lmargin1=0, lmargin2=0)
        self.dice_text.tag_configure("lg_turn", font="LedgerFixedSmall", spacing1=4)
        self.dice_text.tag_configure("lg_round", spacing1=8, spacing3=2)
        self.dice_text.tag_configure("lg_event", spacing1=2)
        self.dice_text.tag_configure("lg_summary", spacing1=2, spacing3=6)
        self.dice_text.bind("<Configure>", lambda e: self._set_columns(e.width), add="+")
        self.dice_text.tag_configure("monster", foreground=theme.MONSTER_COLOUR, font="LedgerFixedBold")
        self._raw_dice: "deque[str]" = deque(maxlen=MAX_LOG_LINES)  # (the log's own lines, as written)
        self._ledger = ledger.Ledger(lambda name: False)
        self._slots: Set[str] = set()  # (the readable layout's slots waiting for their fills)
        self._monster_names: Set[str] = set()  # every monster seen in a fight this session
        self._finds: Dict[ttk.Frame, ttk.Entry] = {}  # each tab's find box, for Ctrl+F
        self._find_bar(dice_find, self.dice_text, dice)

        talk = ttk.Frame(tabs, padding=6)
        tabs.add(talk, text="Dialogue", underline=1)
        row = ttk.Frame(talk)
        row.pack(fill="x")
        ttk.Button(row, text="Clear", command=self.clear_dialogue).pack(side="right")
        ttk.Button(row, text="Save...", command=lambda: self.save_text(self.talk_text, "dialogue")).pack(
            side="right", padx=4)
        # the game shows only a face; the player can name it (right-click a name, or this button
        # for the latest speaker), and the name sticks for every line from that portrait
        ttk.Button(row, text="Name speaker...", command=lambda: self.name_speaker(self._last_portrait)).pack(
            side="right")
        talk_find = ttk.Frame(talk)
        talk_find.pack(fill="x", pady=(4, 0))
        box = ttk.Frame(talk)
        box.pack(fill="both", expand=True, pady=(6, 0))
        self.talk_text = tk.Text(box, wrap="word", height=20, font="TkTextFont")
        theme.style_text(self.talk_text)
        self.talk_text.configure(foreground=theme.AMBER)  # the game's dialogue text
        scroll = ttk.Scrollbar(box, command=self.talk_text.yview)
        self.talk_text.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.talk_text.pack(side="left", fill="both", expand=True)
        self._follow_end(self.talk_text, scroll)
        self.talk_text.tag_configure("speaker", font=theme.fonts()[1], foreground=theme.YELLOW)
        self.talk_text.tag_configure("reply", foreground=theme.PALE)
        self.talk_text.tag_configure("chosen", foreground=theme.GREEN)
        self._last_portrait: Optional[int] = None
        self.talk_text.tag_bind("speaker", "<Button-3>", self._speaker_clicked)
        self._find_bar(talk_find, self.talk_text, talk)
        self._build_journal(tabs, launch.load_settings())
        # Ctrl+F: the find box of the log tab shown
        self.root.bind_all("<Control-f>", lambda _e: self._focus_find(tabs))
        self.root.bind_all("<Control-F>", lambda _e: self._focus_find(tabs))

        # what each spell and psionic power really does, from the game's records
        spells = ttk.Frame(tabs, padding=6)
        tabs.add(spells, text="Spells", underline=0)
        row = ttk.Frame(spells)
        row.pack(fill="x")
        ttk.Label(row, text="Show").pack(side="left")
        self.spell_kind = tk.StringVar(value="All")
        kind = ttk.Combobox(row, textvariable=self.spell_kind, state="readonly", width=10,
                            values=("All", "Wizard", "Priest", "Psionic"))
        kind.pack(side="left", padx=4)
        kind.bind("<<ComboboxSelected>>", lambda _e: self.show_spells())
        ttk.Button(row, text="Save...", command=lambda: self.save_text(self.spell_text, "spells")).pack(side="right")
        ttk.Button(row, text="Refresh", command=self.show_spells).pack(side="right", padx=4)
        self.spells_party = tk.BooleanVar(value=False)
        ttk.Checkbutton(spells, text="Only spells the party has a caster level for", variable=self.spells_party,
                        command=self.show_spells).pack(anchor="w", pady=(4, 0))
        box = ttk.Frame(spells)
        box.pack(fill="both", expand=True, pady=(6, 0))
        self.spell_text = tk.Text(box, wrap="word", height=20, font="TkTextFont")
        theme.style_text(self.spell_text)
        scroll = ttk.Scrollbar(box, command=self.spell_text.yview)
        self.spell_text.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.spell_text.pack(side="left", fill="both", expand=True)
        self.spell_text.tag_configure("name", font=theme.fonts()[1], foreground=theme.YELLOW)
        self.spell_text.insert("end", "Connect to the game to read its spells.")
        tabs.bind("<<NotebookTabChanged>>", lambda _e: self.show_spells()
                  if tabs.select() == str(spells) and not self._spells_shown else None)
        self._spells_shown = False

        self.tools_tab = tools = ttk.Frame(tabs, padding=6)
        tabs.add(tools, text="Memory tools", underline=0)

        locate = ttk.LabelFrame(tools, text="Locate by name (or hex:14 16 12 for bytes)", padding=6)
        locate.pack(fill="x")
        row = ttk.Frame(locate)
        row.pack(fill="x")
        self.search_text = tk.StringVar()
        entry = ttk.Entry(row, textvariable=self.search_text, width=24)
        entry.pack(side="left")
        entry.bind("<Return>", lambda _e: self.search_name())
        ttk.Button(row, text="Search", command=self.search_name).pack(side="left", padx=4)
        # the field addresses found (layouts/), for mapping fields or other layouts
        ttk.Button(row, text="Save layout", command=self.save_layout).pack(side="right")
        ttk.Button(row, text="Reload layout", command=self.reload_layout).pack(side="right", padx=4)
        row = ttk.Frame(locate)
        row.pack(fill="x", pady=(6, 0))
        ttk.Label(row, text="Assign selected name hit to slot").pack(side="left", padx=(0, 2))
        self.assign_slot = self._slot_box(row)
        ttk.Button(row, text="Assign", command=self.assign_hit).pack(side="left", padx=4)
        ttk.Label(row, text="Stride").pack(side="left", padx=(12, 2))
        self.stride_text = tk.StringVar()
        ttk.Entry(row, textvariable=self.stride_text, width=8).pack(side="left")
        ttk.Button(row, text="Apply", command=self.apply_stride).pack(side="left", padx=4)
        self.hit_list = tk.Listbox(locate, height=6, font="TkFixedFont", foreground=theme.YELLOW)
        theme.style_text(self.hit_list)
        self.hit_list.configure(foreground=theme.YELLOW)
        self.hit_list.pack(fill="x", pady=(6, 0))

        hexframe = ttk.LabelFrame(tools, text="Record bytes (changed bytes light up)", padding=6)
        hexframe.pack(fill="both", expand=True, pady=(6, 0))
        row = ttk.Frame(hexframe)
        row.pack(fill="x")
        self.hex_record = ttk.Combobox(row, width=10, state="readonly")
        self.hex_record.pack(side="left")
        ttk.Label(row, text="slot").pack(side="left", padx=(6, 2))
        self.hex_slot = self._slot_box(row)
        self.show_addresses = tk.BooleanVar(value=False)
        ttk.Checkbutton(row, text="Record addresses in the party table",
                        variable=self.show_addresses).pack(side="right")
        # (a line of its own: the decoded values are long)
        self.inspect = tk.StringVar(value="Click a byte to decode it.")
        ttk.Label(hexframe, textvariable=self.inspect, font="TkFixedFont").pack(anchor="w", pady=(4, 0))
        self.hex = tk.Text(hexframe, font="TkFixedFont", height=20, width=60, wrap="none")
        theme.style_text(self.hex)
        # (a line is 76 characters: in a narrow pane it scrolls sideways rather than losing its end; its
        # width asked for is less, so the divider is placed by the rows of buttons above)
        across = ttk.Scrollbar(hexframe, orient="horizontal", command=self.hex.xview)
        self.hex.configure(xscrollcommand=across.set)
        across.pack(side="bottom", fill="x")
        self.hex.pack(fill="both", expand=True, pady=(6, 0))
        # underlined as well as coloured, so a change doesn't depend on seeing the colour
        self.hex.tag_configure("changed", background=theme.AMBER, foreground=theme.SHADOW, underline=True)
        self.hex.tag_configure("selected", background=theme.PSI_BLUE, foreground=theme.SHADOW)
        self.hex.bind("<Button-1>", self.on_hex_click)

        self._build_options(tabs)
        self._apply_layout()

    def _build_options(self, tabs: ttk.Notebook) -> None:
        """The Options tab: what the Loader shows, changes and adds in the game."""
        # it scrolls, for a window too small (or text too large) to show it all
        area = theme.ScrollArea(tabs, padding=6)
        tabs.add(area, text="Options", underline=0)
        options = area.inner
        # the player's settings, read strictly: one held a moment by an antivirus or a backup is tried
        # again for a second, and if it still can't be read the tab shows the defaults and says so
        # (_options_unread); only a switch then changed is saved, never the defaults over the file
        try:
            settings = launch.load_settings(strict=True, tries=20)
            self._options_unread: Optional[str] = None
        except launch.SettingsUnreadable as e:
            settings, self._options_unread = {}, e.strerror
        self.sections: Dict[str, theme.Section] = {}
        opened = settings.get("options_open", [])
        opened = opened if isinstance(opened, list) else []

        def section(key: str, title: str) -> ttk.Frame:
            """A section that opens and closes (closed until opened; remembered)."""
            part = theme.Section(options, title, open_=key in opened,
                                 on_toggle=lambda _open: self._sections_changed())
            part.pack(fill="x", pady=(8 if self.sections else 0, 0))
            self.sections[key] = part
            return part.body

        note = ttk.Label(options, text="Everything here applies in games started from the Loader or its .bat files. A switch that "
                         "says \"from the next start\" waits until the game is started again.", wraplength=460)
        note.pack(anchor="w", pady=(0, 8))
        options.bind("<Configure>", lambda e: note.configure(wraplength=max(200, e.width - 60)), add="+")
        in_game = section("in_game", "In the game")
        # long lines wrap to the window (as with larger text) instead of running out of it
        options.bind("<Configure>", lambda e: [ttk.Style().configure(
            kind, wraplength=max(200, e.width - 60)) for kind in ("TCheckbutton", "TRadiobutton")], add="+")
        # the combat log's panel over the map, shown and hidden with L (combatlog.py), at a level of its own
        # (always there: its switch gone, game.ALWAYS_ON)
        ttk.Label(in_game, text="The combat log in the game (L on the map shows and hides it):").pack(anchor="w")
        self.combat_log_level = tk.StringVar(value=dicelog.combat_log_level(settings))
        for value, text in ((combatlog.MINIMAL, "... at the least: what came of each attack and spell"),
                            (combatlog.SHORT, "... in short: each roll, what it needed and the damage"),
                            (combatlog.DETAIL, "... in detail, as in the log")):
            ttk.Radiobutton(in_game, text=text, value=value, variable=self.combat_log_level,
                            command=self._options_changed).pack(anchor="w", padx=(20, 0))
        # the game's Look box, on a monster in a fight: what hurts it, then all of it in a window
        self.monster_info = tk.BooleanVar(value=bool(settings.get("monster_info", True)))
        ttk.Checkbutton(in_game, text="What hurts a monster (the Look box): Look at one in a fight for its hit points, AC, "
                        "THAC0 and defences; closing the box shows the rest in a window",
                        variable=self.monster_info, command=self._options_changed).pack(anchor="w", pady=(4, 0))
        # names floating over figures on the map for a moment (labels.py)
        self.floating_names = tk.BooleanVar(value=bool(settings.get("floating_names", True)))
        ttk.Checkbutton(in_game, text="Names over figures: a spell's name over its caster, \"Miss\" over whoever an "
                        "attack missed, a used charge (\"Armor: 7 left\") over its owner, and the arrows left over a party "
                        "archer after each shot",
                        variable=self.floating_names, command=self._options_changed).pack(anchor="w")
        # the red ring under the enemy chosen with Tab (rings.py; choosing one is always on: targeting.py)
        self.ring_mode = tk.StringVar(value=rings.mode(settings))
        ttk.Label(in_game, text="A red ring on the ground in a fight:").pack(anchor="w", pady=(4, 0))
        for value, text in ((rings.OFF, "... none"),
                            (rings.ONLY_CHOSEN, "... under the enemy chosen with Tab")):
            ttk.Radiobutton(in_game, text=text, value=value, variable=self.ring_mode,
                            command=self._options_changed).pack(anchor="w", padx=(20, 0))
        # what the d20 must show to hit the chosen enemy (hitchance.py)
        self.hit_chance = tk.BooleanVar(value=settings.get("hit_chance", True) is not False)
        ttk.Checkbutton(in_game, text="The chance to hit: with an enemy chosen with Tab, what the d20 must show to hit "
                        "it and the chance, in the dice log and the combat log's header",
                        variable=self.hit_chance, command=self._options_changed).pack(anchor="w", pady=(4, 0))
        # ... and over the enemy the game's pointer is on (hover.py)
        self.hit_hover = tk.BooleanVar(value=settings.get("hit_hover", True) is not False)
        ttk.Checkbutton(in_game, text="The chance to hit under the pointer: in a fight, with the pointer over an enemy, "
                        "what the d20 must show and the chance float over it",
                        variable=self.hit_hover, command=self._options_changed).pack(anchor="w", pady=(4, 0))
        # the squares the party member whose turn it is can still walk to (squares.py)
        self.show_squares = tk.BooleanVar(value=settings.get("squares", True) is not False)
        ttk.Checkbutton(in_game, text="Squares in reach: in a fight, a small cross on each square the party member "
                        "whose turn it is can still walk to (R in a fight hides and shows them)",
                        variable=self.show_squares, command=self._options_changed).pack(anchor="w", pady=(4, 0))
        # F10 after the last step: the move taken back can be walked again (moveback.py)
        self.move_back = tk.BooleanVar(value=settings.get("move_back", True) is not False)
        ttk.Checkbutton(in_game, text="F10 takes a whole move back: after the last step too, the party member can "
                        "walk again (the game's F10 puts it back but lets it walk no more)",
                        variable=self.move_back, command=self._options_changed).pack(anchor="w", pady=(4, 0))
        # gold rings and names for what a click does something with, while Alt is held (usable.py)
        self.show_usable = tk.BooleanVar(value=settings.get("show_usable", True) is not False)
        ttk.Checkbutton(in_game, text="Showing what can be used: hold Alt on the map, out of a fight",
                        variable=self.show_usable, command=self._options_changed).pack(anchor="w", pady=(4, 0))
        # the rule changes that keep a switch (game.RULE_SETTINGS; the rest are always on: game.ALWAYS_ON)
        rules = section("rules", "Rule changes")
        custom = section("custom", "More character customization")
        # the Loader's own content: people, a quest and items in the game, and the new spells. Some
        # are written into the game's files when it is started; what a save already has stays
        new = section("new_content", "New content")
        ttk.Label(new, text="People, a quest, an arena bout and items: from the next start, in places "
                  "not yet visited. What a saved game already has (people met, items given) stays in it. "
                  "The new spells and defilers' scrolls: at once.",
                  wraplength=460).pack(anchor="w")
        options.bind("<Configure>", lambda e, label=new.winfo_children()[-1]: label.configure(
            wraplength=max(200, e.width - 60)), add="+")
        where = {"kits": custom, "new_spells": new}
        # one switch for each of game.RULE_SETTINGS
        self.rule_vars: Dict[str, tk.BooleanVar] = {}
        # (in the order FEATURES.md has them, each opening with its name there; "New spells" stands for
        # two headings, New wizard spells and 6th-level priest spells)
        for key, text in (
                ("best_hit_die", "Hit dice: the better of two, each die rolled twice at creation and at every level "
                                 "(every character)"),
                ("half_giant_hands", "Half-giants' two-handed weapons: a half-giant wields one in one hand, a shield "
                                     "or a light weapon in the other"),
                ("helm_ac", "Helms give AC 1 (the game's helms give none)"),
                ("kits", "Kits: three for each class and some for multiclass characters, one a character, each "
                         "giving something and costing something (chosen on the creation panel's KIT "
                         "page, or after DUAL by a human with none)"),
                ("new_spells", "New spells: six for wizards (Cat's Grace, Erdlu Claw, Fogbolt, Reflected Image, "
                               "Spook and Friends) and ten 6th-level priest spells (Heal, Harm, Blade Barrier...)")):
            var = self.rule_vars[key] = tk.BooleanVar(value=game.setting_on(settings, key))
            parent = where.get(key, rules)
            ttk.Checkbutton(parent, text=text, variable=var,
                            command=self._options_changed).pack(anchor="w", pady=(4 if parent.winfo_children()[:-1] else 0, 0))

        self.starting_gear = tk.BooleanVar(value=bool(settings.get("starting_gear", True)))
        ttk.Checkbutton(custom, text="Fuller starting gear: new characters (and the game's own party) also get a weapon "
                        "they can use, a sling, and leather armour where they may wear it",
                        variable=self.starting_gear, command=self._options_changed).pack(anchor="w", pady=(4, 0))

        self.content_vars: Dict[str, tk.BooleanVar] = {}
        for key, text in (
                ("kalzith", "Kalzith, a defiler slave in the slave pens who sells arcane scrolls"),
                ("semyon", "Semyon in the slave pens after he leaves the arena, and breaking out with Scar"),
                ("vulture", "The cooked vulture: Dinos cooks it for the party (XP and a full rest)"),
                ("defiler_scrolls", "Defilers' scrolls: a defiler in a fight carries a scroll of a random "
                                    "preserver spell one time in 20, dropped where it dies"),
                (launch.NEW_ITEMS, "New items, magical and mundane: weapons, armour and other gear on the game's "
                                   "people, in its shops and chests, and the champions' arena bout after Scar's death")):
            self.content_vars[key] = tk.BooleanVar(value=settings.get(key, True) is not False)
            ttk.Checkbutton(new, text=text, variable=self.content_vars[key],
                            command=self._options_changed).pack(anchor="w", pady=(4, 0))

        # what runs the game: GOG's DOSBox 0.74, or the player's own DOSBox-X (dosboxx.py)
        motor = section("engine", "Engine (from the next start)")
        self.engine = tk.StringVar(value=dosboxx.engine(settings))
        for value, text in ((dosboxx.GOG, "GOG's DOSBox 0.74, which comes with the game (the default)"),
                            (dosboxx.DOSBOX_X, "DOSBox-X, your own copy of it: new, and tested on Linux only "
                                               "so far")):
            ttk.Radiobutton(motor, text=text, value=value, variable=self.engine,
                            command=self._engine_chosen).pack(anchor="w")
        self.dosbox_x_path = settings.get(dosboxx.PATH_SETTING) if isinstance(
            settings.get(dosboxx.PATH_SETTING), str) else ""
        self.dosbox_x_status = tk.StringVar(value=dosboxx.found_line(self.dosbox_x_path)
                                            if self.dosbox_x_path or self.engine.get() == dosboxx.DOSBOX_X
                                            else "No DOSBox-X chosen.")
        found_x = ttk.Label(motor, textvariable=self.dosbox_x_status, style="Status.TLabel", wraplength=460,
                            justify="left")
        found_x.pack(anchor="w", pady=(4, 0))
        ttk.Button(motor, text="Choose the DOSBox-X program...", command=self.choose_dosbox_x).pack(
            anchor="w", pady=(4, 0))
        about_x = ttk.Label(motor, text="DOSBox-X is not part of the mod and is not downloaded: install it "
                            "yourself (2025.01.01 or later) and choose its program here. The Loader starts it with "
                            "a configuration of its own and follows the game through DOSBox-X's memory file, so on "
                            "Linux it needs neither root nor a ptrace setting. This engine is new: it has been "
                            "played on Linux only, and is untested on Windows and macOS. The game's saves are the "
                            "same on both engines.", style="Status.TLabel", wraplength=460, justify="left")
        about_x.pack(anchor="w", pady=(4, 0))
        motor.bind("<Configure>", lambda e: [label.configure(wraplength=max(200, e.width - 20))
                                             for label in (found_x, about_x)], add="+")
        # the game's speed (DOSBox's CPU)
        pace = section("speed", "Game speed (from the next start)")
        speed = settings.get("cycles", launch.DEFAULT_SPEED)
        speed = launch.SPEEDS[-1] if speed == launch.FASTEST_BEFORE else speed
        self.game_speed = tk.StringVar(value=str(speed if speed in launch.SPEEDS or speed == launch.GOG_SPEED
                                                 else launch.DEFAULT_SPEED))
        for value, text in ((launch.GOG_SPEED, "GOG's own (walking can be choppy with shadows and dust)"),
                            ("20000", "Faster: for an older PC (fewer pictures a second with the whole party in view)"),
                            ("35000", "Fastest: the whole party walks at full speed, nearly every picture "
                                      "shown (the default)")):
            ttk.Radiobutton(pace, text=text, value=value, variable=self.game_speed,
                            command=self._speed_chosen).pack(anchor="w")
        self.steady_pace = tk.BooleanVar(value=settings.get("steady_pace", True) is not False)
        ttk.Checkbutton(pace, text="Steady pace: walking at full speed on the map whatever is drawn (a picture skipped "
                        "rather than the party slowed)", variable=self.steady_pace,
                        command=self._options_changed).pack(anchor="w", pady=(4, 0))
        # how DOSBox draws the game larger, and where it sends the music (launch.display_lines, midiout.py)
        look = section("picture", "Picture and music (from the next start)")
        chosen = settings.get("picture", launch.DEFAULT_PICTURE)
        self.picture = tk.StringVar(value=chosen if chosen in launch.PICTURES else launch.DEFAULT_PICTURE)
        for value, text in ((launch.PLAIN, "Plain: every pixel of the game as a block (the default)"),
                            (launch.SCANLINES, "Scanlines: a black line under each row of the picture, as on an "
                                               "old monitor"),
                            (launch.TV, "TV: a dimmed line under each row of the picture, softer than scanlines"),
                            (launch.SHARP, "Sharp: hard-edged pixels at any size, the stretching left unsmoothed "
                                           "(DOSBox's OpenGL)")):
            ttk.Radiobutton(look, text=text, value=value, variable=self.picture,
                            command=self._picture_chosen).pack(anchor="w")
        ttk.Label(look, text="A Single game window is always plain: there is nothing to draw larger.",
                  style="Status.TLabel").pack(anchor="w", pady=(2, 0))
        music = ttk.Frame(look)
        music.pack(anchor="w", fill="x", pady=(8, 0))
        ttk.Label(music, text="Music device").pack(side="left")
        device = midiout.setting(settings)
        self.midi_names = midiout.devices()  # (Windows' MIDI outputs by name; None where they can't be read)
        if self.midi_names is None:
            self.midi_device = tk.StringVar(value="" if device == midiout.DEFAULT else str(device))
            self.midi_box: tk.Widget = ttk.Entry(music, textvariable=self.midi_device, width=8)
            hint = ("Empty for the default. Else a device's number as Windows counts them, from 0 (their names "
                    "can't be read here), or for a Linux DOSBox an ALSA port such as 128:0.")
        else:
            self.midi_device = tk.StringVar(value=midiout.label(device, self.midi_names))
            self.midi_box = ttk.Combobox(music, textvariable=self.midi_device, state="readonly", width=44,
                                         values=midiout.labels(self.midi_names, device))
            self.midi_box.bind("<<ComboboxSelected>>", lambda _e: self._midi_chosen())
            hint = ("Windows' default, or one of its MIDI devices: a software synthesizer with a soundfont, or an "
                    "MT-32 driver, that you have installed.")
        self.midi_box.pack(side="left", padx=(6, 0))
        self.midi_box.bind("<Return>", lambda _e: self._midi_chosen())
        self.midi_box.bind("<FocusOut>", lambda _e: self._midi_chosen())
        about_midi = ttk.Label(look, text=hint, style="Status.TLabel", wraplength=460, justify="left")
        about_midi.pack(anchor="w", pady=(2, 0))
        # DOSBox-X's own synthesizer plays through a soundfont the player names (dosboxx.midi_lines)
        self.soundfont = settings.get(dosboxx.SOUNDFONT_SETTING) if isinstance(
            settings.get(dosboxx.SOUNDFONT_SETTING), str) else ""
        font = ttk.Frame(look)
        font.pack(anchor="w", fill="x", pady=(8, 0))
        ttk.Label(font, text="Soundfont file (DOSBox-X only)").pack(side="left")
        ttk.Button(font, text="Choose a soundfont file...", command=self.choose_soundfont).pack(side="left", padx=(6, 0))
        ttk.Button(font, text="No soundfont", command=self.no_soundfont).pack(side="left", padx=(6, 0))
        self.soundfont_status = tk.StringVar(value=self._soundfont_line())
        about_font = ttk.Label(look, textvariable=self.soundfont_status, style="Status.TLabel", wraplength=460,
                               justify="left")
        about_font.pack(anchor="w", pady=(2, 0))
        look.bind("<Configure>", lambda e: [label.configure(wraplength=max(200, e.width - 20))
                                            for label in (about_midi, about_font)], add="+")
        # Wake of the Ravager, for the 6th-level priest spells' icons and pictures (wotrart.py)
        ravager = section("ravager", "Wake of the Ravager (optional)")
        self.wotr_status = tk.StringVar(value=self._wotr_status())
        found = ttk.Label(ravager, textvariable=self.wotr_status, style="Status.TLabel", wraplength=460,
                          justify="left")
        found.pack(anchor="w")
        ravager.bind("<Configure>", lambda e: found.configure(wraplength=max(200, e.width - 20)), add="+")
        ttk.Button(ravager, text="Choose its folder...", command=self.choose_wotr).pack(anchor="w", pady=(4, 0))
        # the saves, a second time under their names in the game (namedsaves.py)
        kept = section("saves", "Saves")
        # F5, F9 and the saves the game makes by itself, on the save window's QUICK page (quicksave.py)
        self.quick_save = tk.BooleanVar(value=settings.get("quick_save", True) is not False)
        ttk.Checkbutton(kept, text="Quick save and quick load: on the map, F5 saves at once on the QUICK page of the "
                        "save window, and F9 opens the load window there", variable=self.quick_save,
                        command=self._options_changed).pack(anchor="w")
        self.autosave = tk.BooleanVar(value=settings.get("autosave", True) is not False)
        ttk.Checkbutton(kept, text="Autosave: on coming into another area and after a fight, on the QUICK page of "
                        "the save window", variable=self.autosave,
                        command=self._options_changed).pack(anchor="w", pady=(4, 8))
        about = ttk.Label(kept, text="While this window is open, every save is copied, as the game writes it, into the Loader's \"Named "
                          "saves\" folder under the name it has in the game (\"Page 2 slot 05 - Before Scar's "
                          "battle.SAV\").", style="Status.TLabel", wraplength=460, justify="left")
        about.pack(anchor="w")
        kept.bind("<Configure>", lambda e: about.configure(wraplength=max(200, e.width - 20)), add="+")
        buttons = ttk.Frame(kept)
        buttons.pack(anchor="w", pady=(4, 0))
        ttk.Button(buttons, text="Open the folder", command=self.open_named_saves).pack(side="left")
        ttk.Button(buttons, text="Put a save in a slot...", command=self.restore_save).pack(side="left", padx=(8, 0))
        ttk.Button(options, text="Restore defaults", command=self.restore_defaults).pack(anchor="w", pady=(12, 0))
        self._options_shown = self._option_values()  # (as read: only what changes from it is saved)

    def _wotr_status(self) -> str:
        """Where the Loader finds Wake of the Ravager, for the 6th-level priest spells' art."""
        from . import wotrart
        found = wotrart.find_resources(launch.find_game_dir())
        if found:
            return (f"Found in {os.path.dirname(found)}: the 6th-level priest spells use its icons and "
                    "pictures.")
        return ("Not found (looked beside the game's folder and in GOG's usual folders): the 6th-level "
                "priest spells use the Loader's own icons. If it is installed, choose its folder.")

    def _engine_chosen(self) -> None:
        """Remember the engine; it applies the next time the game is started. DOSBox-X chosen with
        no program named, or one too old: said, and the choice kept (the start says it again)."""
        self._options_changed()
        if self._options_shown.get(dosboxx.SETTING) != self.engine.get():
            return  # (not saved: the status line says why)
        if self.engine.get() == dosboxx.DOSBOX_X:
            line = dosboxx.found_line(self.dosbox_x_path)
            self.dosbox_x_status.set(line)
            wrong = dosboxx.problem({dosboxx.PATH_SETTING: self.dosbox_x_path})
            self.status.set("Engine: DOSBox-X, from the next start." if wrong is None else
                            "Engine: DOSBox-X, but it can't start yet: " + line)
        else:
            self.status.set("Engine: GOG's DOSBox, from the next start.")

    def choose_dosbox_x(self) -> None:
        """The player's DOSBox-X program: asked for, its version read, and remembered unless it
        is too old for the memory file (then said, and not kept)."""
        path = filedialog.askopenfilename(parent=self.root, title="Where is the DOSBox-X program (dosbox-x)?")
        if not path:
            return
        found = dosboxx.version(path)
        line = dosboxx.found_line(path, found, asked=True)
        if found is not None and not dosboxx.new_enough(found):
            messagebox.showerror("DOSBox-X", line, parent=self.root)
            return
        if self._save_settings({dosboxx.PATH_SETTING: path}):
            self.dosbox_x_path = path
            self.dosbox_x_status.set(line)
            self.status.set("DOSBox-X: remembered. Choose it as the engine above to play in it, from the "
                            "next start." if self.engine.get() != dosboxx.DOSBOX_X else
                            "DOSBox-X: remembered, from the next start.")

    def _soundfont_line(self) -> str:
        return dosboxx.music_line({dosboxx.SOUNDFONT_SETTING: self.soundfont,
                                   midiout.SETTING: getattr(self, "_options_shown", {}).get(midiout.SETTING)})

    def choose_soundfont(self) -> None:
        path = filedialog.askopenfilename(parent=self.root, title="Which soundfont file?",
                                          filetypes=[("Soundfonts", "*.sf2 *.SF2 *.sf3 *.SF3"), ("All files", "*")])
        if path and self._save_settings({dosboxx.SOUNDFONT_SETTING: path}):
            self.soundfont = path
            self.soundfont_status.set(self._soundfont_line())
            self.status.set("Soundfont file: from the next start, in DOSBox-X.")

    def no_soundfont(self) -> None:
        if self._save_settings({dosboxx.SOUNDFONT_SETTING: ""}):
            self.soundfont = ""
            self.soundfont_status.set(self._soundfont_line())
            self.status.set("Soundfont file: none, from the next start.")

    def choose_wotr(self) -> None:
        from . import wotrart
        folder = filedialog.askdirectory(parent=self.root, title="Where is Dark Sun: Wake of the Ravager installed?")
        if not folder:
            return
        if not wotrart.find_resources(None, folder):
            messagebox.showerror("Wake of the Ravager", f"{folder} has no Wake of the Ravager RESOURCE.GFF.",
                                 parent=self.root)
            return
        self._save_settings({wotrart.SETTING: folder})
        self.wotr_status.set(self._wotr_status() + " From the next start.")

    def _saves_game_dir(self) -> Optional[str]:
        game_dir = self._game_dir or launch.find_game_dir()
        if game_dir is None:
            messagebox.showinfo("Saves", "The Loader hasn't found the game yet: start it once from the Loader.",
                                parent=self.root)
        return game_dir

    def open_guide(self) -> None:
        """The manual, made from the player's pages (README.md, PLAYER-GUIDE.md, ...) and shipped beside
        the Loader in manual/, at its start page, in the browser."""
        if not os.path.exists(HELP_PAGE):
            self.status.set(f"The manual isn't there: {HELP_PAGE}")
            return
        try:
            opened = webbrowser.open(Path(HELP_PAGE).as_uri())
        except webbrowser.Error:
            opened = False
        # (said either way: an opener can report success and still find no browser, as gio did)
        self.status.set(f"The manual, opening in your browser: {HELP_PAGE}" if opened
                        else f"The manual is {HELP_PAGE}")

    def open_named_saves(self) -> None:
        game_dir = self._saves_game_dir()
        if game_dir is None:
            return
        try:
            namedsaves.sync(game_dir)
            os.makedirs(namedsaves.NAMED, exist_ok=True)
        except OSError as err:
            self.status.set(f"Couldn't open the named saves: {err}")
            return
        try:
            if sys.platform == "win32":
                os.startfile(namedsaves.NAMED)  # type: ignore[attr-defined]
            else:
                subprocess.Popen(["xdg-open", namedsaves.NAMED])
        except OSError:
            self.status.set(f"The named saves are in {namedsaves.NAMED}")

    def restore_save(self) -> None:
        """A save file (a named copy) put in a slot of the game's list, to be loaded from there."""
        game_dir = self._saves_game_dir()
        if game_dir is None:
            return
        try:
            os.makedirs(namedsaves.NAMED, exist_ok=True)
        except OSError:
            pass  # (no Named saves folder: the dialog starts elsewhere)
        copy = filedialog.askopenfilename(parent=self.root, title="Which save?", initialdir=namedsaves.NAMED,
                                          filetypes=[("Saves", "*.SAV *.sav"), ("All files", "*")])
        if not copy:
            return
        m = namedsaves.COPY.match(os.path.basename(copy))
        where = simpledialog.askstring("Put a save in a slot", "Which page and slot of the game's list? "
                                       "(page 1 to 4, slot 1 to 10, as 2-5)", parent=self.root,
                                       initialvalue=f"{m.group(1)}-{int(m.group(2))}" if m else "1-1")
        if not where:
            return
        try:
            page, slot = (int(n) for n in where.replace(" ", "").split("-"))
            if not (1 <= page <= 4 and 1 <= slot <= 10):
                raise ValueError
        except ValueError:
            messagebox.showerror("Put a save in a slot", "That isn't a page and slot (such as 2-5).", parent=self.root)
            return
        there = namedsaves.slot_name(game_dir, page, slot)
        if there is not None and not messagebox.askyesno(
                "Put a save in a slot", f"Page {page} slot {slot} has \"{there}\". Put this save there instead? "
                "(It is kept in the Named saves folder as \"Replaced - ...\".)", parent=self.root):
            return
        try:
            name = namedsaves.restore(copy, game_dir, page, slot)
        except (OSError, ValueError) as e:
            messagebox.showerror("Put a save in a slot", str(e), parent=self.root)
            return
        self.status.set(f"\"{name}\" is in page {page} slot {slot}: load it from the game's list.")

    def restore_defaults(self) -> None:
        """Every switch on the Options tab back as it comes (after asking)."""
        if not messagebox.askyesno("Restore defaults", "Set every option on the Options tab back to its default?",
                                   parent=self.root):
            return
        for var in list(self.rule_vars.values()) + list(self.content_vars.values()):
            var.set(True)
        for var in (self.monster_info, self.floating_names, self.starting_gear, self.steady_pace,
                    self.hit_chance, self.hit_hover, self.show_squares, self.move_back, self.show_usable, self.quick_save, self.autosave):
            var.set(True)
        self.combat_log_level.set(dicelog.combat_log_level({}))
        self.ring_mode.set(rings.mode({}))
        self.game_speed.set(str(launch.DEFAULT_SPEED))
        self.picture.set(launch.DEFAULT_PICTURE)
        self.engine.set(dosboxx.GOG)  # (the DOSBox-X program and the soundfont file stay remembered)
        self._show_midi(midiout.DEFAULT)
        self._options_changed(every=True)
        self._speed_chosen()
        self.status.set("Options set back to their defaults (a switch marked \"from the next start\" applies from the next start).")

    def _sections_changed(self) -> None:
        """Remember which of the Options tab's sections are open."""
        self._save_settings({"options_open": [key for key, part in self.sections.items() if part.is_open]})

    def _slot_box(self, parent) -> ttk.Combobox:
        box = ttk.Combobox(parent, width=3, state="readonly")
        box.pack(side="left")
        return box

    def _apply_layout(self) -> None:
        """Refresh everything that depends on the layout (after loading or reloading it)."""
        slots = [str(i + 1) for i in range(self.layout.count)]
        for box in (self.assign_slot, self.hex_slot):
            box.configure(values=slots)
            box.current(0)
        self.hex_record.configure(values=list(self.layout.records))
        self.hex_record.set(self.layout.name.record)
        stride = self.layout.name_record.stride
        self.stride_text.set("" if stride is None else f"{stride:#x}")

        cols = ["field"] + [f"slot{i}" for i in range(self.layout.count)]
        self.table.delete(*self.table.get_children())
        self.table.configure(columns=cols)
        self.table.heading("field", text="")
        self.table.column("field", width=150, anchor="w", stretch=False)
        for i in range(self.layout.count):
            self.table.heading(f"slot{i}", text=f"Slot {i + 1}")
            self.table.column(f"slot{i}", width=118, anchor="center")

    # ---- actions ----------------------------------------------------------------

    def zoom(self, factor: Optional[float]) -> None:
        """Enlarge or shrink all text (None: back to the usual size)."""
        theme.set_scale(self.root, 1.0 if factor is None else theme.scale() * factor)
        self.banner.redraw()
        self._fit_party()

    def _fit_party(self, divider: bool = True) -> None:
        """Columns wide enough for the text size and the longest label and value, and (DIVIDER)
        the divider moved to fit them, short of squeezing the right-hand tabs' buttons."""
        font = tkfont.nametofont("TkDefaultFont")
        field = max(round(150 * theme.scale()), font.measure(self._widest[0]) + 16)
        slot = max(round(110 * theme.scale()), font.measure(self._widest[1]) + 16)
        self.table.column("field", width=field, minwidth=field, stretch=False)
        for i in range(self.layout.count):
            self.table.column(f"slot{i}", width=slot, minwidth=slot)
        if not divider:  # (the columns widened as the table fills: the divider left where it is)
            return
        # at large text sizes the table scrolls sideways rather than squeezing the logs
        wanted = field + slot * self.layout.count + 24
        width = self.panes.winfo_width()
        if width < 200:  # not laid out yet (a slow start): placing the divider now would hide the party
            self.root.after(200, self._fit_party)
            return
        # (the widest rows of buttons, the memory tools', and every tab's name whole: a notebook
        # narrower than its tabs cuts each name short, "Dice lo", "Journa")
        right = max(self.tools_tab.winfo_reqwidth() + 16, tabs_width(self.tabs))
        place = min(wanted, int(width * 0.55), max(width - right, width // 3))
        if self.panes.sashpos(0, place) < place // 2:  # the panes weren't ready after all: again soon
            self.root.after(200, self._fit_party)

    def save_text(self, widget: tk.Text, what: str) -> None:
        """Save a log as a text file (to read with other tools, such as a screen reader)."""
        path = filedialog.asksaveasfilename(title=f"Save the {what}", defaultextension=".txt",
                                            initialfile=f"{what.replace(' ', '-')}.txt",
                                            filetypes=[("Text", "*.txt"), ("All files", "*.*")], parent=self.root)
        if path:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(widget.get("1.0", "end-1c"))
            except OSError as e:
                messagebox.showerror(f"Save the {what}", f"It could not be saved there:\n{e}", parent=self.root)

    def freeze_report(self) -> None:
        """Save a freeze report (freeze.py) in crash-logs/ and say where; for when the game has
        stopped but DOSBox hasn't."""
        if not self.guest:
            messagebox.showinfo("Freeze report", "The Loader isn't connected to DOSBox, so there is nothing "
                                "to report. Start the game from the Loader, or press Reconnect.", parent=self.root)
            return
        attached = self.dice is not None and self.dice.attached
        hdr = self.dice.tsr_hdr if attached else None
        ds = self.dice.game.ds if attached and self.dice.game is not None else None
        self.status.set("Writing a freeze report...")
        self.root.update_idletasks()
        try:
            path = freeze.freeze_report(self.guest.read, hdr, ds, __version__,
                                        launch.effective_switches(launch.load_settings()),
                                        "\n".join(self._raw_dice), self.talk_text.get("1.0", "end-1c"),
                                        launch.CRASH_DIR)
        except Exception as e:  # (DOSBox gone, say): said, not raised
            self.status.set(f"No freeze report: {e}")
            return
        self.status.set(f"Freeze report saved: {path}")
        messagebox.showinfo("Freeze report", f"Saved in\n{path}\n\nSend it along with what you were doing "
                            "when the game stopped.", parent=self.root)

    def _drop_dice(self) -> None:
        if self.dice is not None:
            self.dice.close()
        self.dice = None

    def _drop_guest(self) -> None:
        """Let go of DOSBox's memory: its process handle closed."""
        if self.guest is not None:
            try:
                self.guest.proc.close()
            except Exception:
                pass
        self.guest = None

    def reconnect(self, quiet: bool = False) -> None:
        self.ds = None
        self._drop_dice()
        self._drop_guest()
        try:
            started = self.dosbox if self.dosbox is not None and self.dosbox.poll() is None else None
            if started is not None and self.connect_pid is not None:
                self.guest = self.connect_pid(started.pid)
            else:
                self.guest = self.connect()
        except Exception as e:  # shown to the user, who can fix it and retry
            self.guest = None
            if not quiet or not self.status.get().startswith(("Not connected", "Disconnected")):
                # (a quiet try after the game was lost: "Disconnected (why)" stays up)
                self.status.set(f"Not connected: {e}")
            self.next_try = time.monotonic() + RETRY_SECONDS
            return
        self.status.set(f"Connected to the game (DOSBox-X, process {self.guest.proc.pid}, through its memory "
                        f"file {self.guest.proc.path})" if getattr(self.guest.proc, "by_file", False)
                        else f"Connected to the game (process {self.guest.proc.pid})")

    def start_game(self) -> None:
        """Start Shattered Lands with the dice log, as "Start Game with Dice Log.bat" does; the
        Loader attaches to it once DOSBox is up. The game folder is the remembered one, or asked
        for (and then remembered)."""
        if self.guest or (self.dosbox and self.dosbox.poll() is None):
            return
        game_dir = launch.find_game_dir()
        if game_dir is None:
            game_dir = filedialog.askdirectory(parent=self.root, title="Where is Dark Sun: Shattered Lands installed?")
            if not game_dir:
                return
            if not launch.is_game_dir(game_dir):
                messagebox.showerror("Start the game", f"{game_dir} has no {launch.game_dir_wanted()}.",
                                     parent=self.root)
                return
            self._save_settings({"game_dir": game_dir})
            self.art = art.GameArt.of(game_dir)
        try:
            self._game_dir, self._started = game_dir, time.time()
            self.dosbox, problem = launch.launch(game_dir, "the Loader's window")
        except (launch.LaunchError, OSError) as e:  # (GameBusy among them: another Loader has the game)
            messagebox.showerror("Start the game", str(e), parent=self.root)
            return
        if problem:
            self.status.set(f"Starting the game without the dice log: it can't run with this copy ({problem}).")
        else:
            self.status.set(launch.started_line(game_dir))
        self._append_dice([launch.started_line(game_dir)])
        left_out = launch.left_out_line()
        if left_out:  # (a copy that couldn't be made: told, not silent)
            self._append_dice([left_out])
            messagebox.showwarning("Start the game", left_out, parent=self.root)  # (DOSBox or Dark Sun Recompiled: which runs)
        self.next_try = time.monotonic() + RETRY_SECONDS
        self._start_state()

    def _dosbox_closed(self) -> None:
        """DOSBox started from here has closed: say how, in the log (an exit code a crash of
        DOSBox's own gives, such as C0000005h on Windows, is told apart from the game ending)."""
        if self.dosbox is None or self.dosbox.poll() is None:
            return
        code, self.dosbox = self.dosbox.returncode, None
        self._release_game()
        self._append_dice([launch.closed_line(code)])
        note = launch.game_end_note()
        if code != 0 or note:
            self._crash_report(code, note)
        self._start_state()

    def _crash_report(self, code: int, note) -> None:
        """DOSBox crashed, or the game stopped with an error: save what is known of it in
        crash-logs (launch.crash_report), and say where in the log."""
        now = time.time()
        refused = list(self.guest.refused) if self.guest is not None else self._refused
        text = launch.crash_report(code, note, launch.load_settings(), "\n".join(self._raw_dice) + "\n",
                                   self.talk_text.get("1.0", "end"), refused,
                                   launch.dosbox_output(self._game_dir, self._started), self._started, now)
        try:
            path = launch.write_crash_report(text, now)
        except OSError as e:
            self._append_dice([f"Couldn't save a crash report: {e}"])
            return
        lines = ["The game stopped with an error: " + note.splitlines()[-1]] if note and "\n" in note else []
        self._append_dice(lines + [f"A crash report is saved in {path}. Please send it with a description "
                                   "of what happened just before."])

    def _start_state(self) -> None:
        """"Start the game" only while there's no game to attach to."""
        running = self.guest is not None or (self.dosbox is not None and self.dosbox.poll() is None)
        self.start_button.state(["disabled"] if running else ["!disabled"])

    def reload_layout(self) -> None:
        try:
            self.layout = Layout.load(self.layout.path)
        except (OSError, ValueError, KeyError) as e:
            messagebox.showerror("Layout", f"Could not load {self.layout.path}:\n{e}", parent=self.root)
            return
        self._apply_layout()

    def save_layout(self) -> None:
        try:
            self.layout.save()
        except OSError as e:  # (a folder that can't be written, or the file held elsewhere: said)
            messagebox.showerror("Layout", f"Could not save {self.layout.path}:\n{e}", parent=self.root)
            return
        messagebox.showinfo("Layout", f"Saved slots to {self.layout.path}", parent=self.root)

    def search_name(self) -> None:
        text = self.search_text.get().strip()
        if not text or not self.guest:
            return
        try:
            pattern = _query_bytes(text)
        except ValueError:
            messagebox.showerror("Search", "After hex: give byte values like 14 16 12", parent=self.root)
            return
        try:
            data = self.guest.snapshot()
        except ProcessError as e:
            self._disconnected(e)
            return
        self.hits = self.guest.find(pattern, ignore_case=True, data=data)
        self.hit_list.delete(0, "end")
        for addr in self.hits[:MAX_HITS]:
            self.hit_list.insert("end", f"{addr:#010x}  {_printable(data[addr:addr + 40])}")
        if not self.hits:
            self.hit_list.insert("end", "No matches.")
        elif len(self.hits) > MAX_HITS:
            self.hit_list.insert("end", f"... {len(self.hits) - MAX_HITS} more")

    def assign_hit(self) -> None:
        sel = self.hit_list.curselection()
        if not sel or sel[0] >= min(len(self.hits), MAX_HITS):  # (past the list: its "... more" line)
            messagebox.showinfo("Assign", "Select a search hit first.", parent=self.root)
            return
        slot = int(self.assign_slot.get()) - 1
        self.layout.clear_slot(slot)
        self.layout.name_record.slots[slot] = self.hits[sel[0]] - (self.layout.name.offset or 0)
        self.link_records()
        self.hex_slot.current(slot)
        self.prev_hex.clear()
        self.changed_at.clear()

    def link_records(self) -> None:
        """Find linked records (e.g. character sheets) for every located slot."""
        if not self.guest:
            return
        try:
            data = self.guest.snapshot()
        except ProcessError as e:
            self._disconnected(e)
            return
        name = self.layout.name
        for slot, addr in enumerate(self.layout.name_record.addresses()):
            if addr is not None and name.display(data[addr:addr + (name.offset or 0) + name.length], 0):
                self.layout.link_slot(slot, data)

    def apply_stride(self) -> None:
        text = self.stride_text.get().strip()
        try:
            self.layout.name_record.stride = values.parse_int(text) if text else None
        except ValueError:
            messagebox.showerror("Stride", f"Not a number: {text}", parent=self.root)
            return
        self.link_records()

    def on_hex_click(self, event) -> str:
        line, col = (int(x) for x in self.hex.index(f"@{event.x},{event.y}").split("."))
        column = (col - HEX_PREFIX) // 3
        i = (line - 1) * 16 + column
        if col < HEX_PREFIX or column >= 16 or i >= len(self.hex_data):
            return "break"
        base = self._hex_base() or 0
        offset = self.hex_start + i - base
        parts = [f"{t}={v}" for t in ("u8", "s8", "u16", "s16", "u32")
                 if (v := values.decode(self.hex_data, i, t)) is not None]
        self.inspect.set(f"offset {'-' if offset < 0 else '+'}{abs(offset):#x}: " + "  ".join(parts))
        self.hex.tag_remove("selected", "1.0", "end")
        self.hex.tag_add("selected", f"{line}.{HEX_PREFIX + column * 3}",
                         f"{line}.{HEX_PREFIX + column * 3 + 2}")
        return "break"

    # ---- refresh loop --------------------------------------------------------------

    def _disconnected(self, err: Exception) -> None:
        if self.guest is not None:
            self._refused = list(self.guest.refused)  # (for a crash report)
        self._drop_dice()
        self._drop_guest()
        self.ds = None
        self._release_game()
        self.status.set(f"Disconnected ({err}). Waiting for the game...")
        self.dice_status.set("Waiting for the game...")
        self.next_try = time.monotonic() + RETRY_SECONDS

    def _release_game(self) -> None:
        """The game's lock let go (launch.release_game) once this window neither runs a game nor
        follows one, so another Loader, or `play`, may have it."""
        running = self.dosbox is not None and self.dosbox.poll() is None
        if not running and not (self.dice is not None and self.dice.attached):
            launch.release_game()

    def _save_settings(self, changes: dict) -> bool:
        """CHANGES saved in settings.json; when it is held elsewhere (an antivirus, a backup), the
        status line says so rather than the choice being lost unseen. True if saved."""
        try:
            launch.update_settings(changes)
            return True
        except OSError as e:
            self.status.set(f"The Loader's settings could not be saved just now ({e}); choose again to retry.")
            return False

    def close(self) -> None:
        """Done with the dice log before closing: it lets go of the game (detach) and stops its thread,
        and the game's lock goes."""
        try:
            if self.dice:
                self.dice.detach()
                self.dice.close()
        except Exception:
            pass
        try:
            self._quests_keep(now=True)
            self.journal.close()
        except Exception:
            pass
        launch.release_game()
        self.root.destroy()

    def _tick(self) -> None:
        if not self.guest and time.monotonic() >= self.next_try:
            self.reconnect(quiet=True)
        self._start_state()
        try:
            if self.guest:
                try:
                    self._auto_locate()
                    self._refresh_table()
                    self._refresh_hex()
                except ProcessError as e:
                    self._disconnected(e)
            self._sync_saves()
        except Exception as e:  # (anything else: said once, and the loop goes on)
            self._loop_error("the party table", e)
        finally:
            self.root.after(REFRESH_MS, self._tick)

    def _sync_saves(self) -> None:
        """Every few seconds, the game's saves copied under their names (namedsaves.py)."""
        now = time.monotonic()
        if now < getattr(self, "_saves_due", 0.0):
            return
        self._saves_due = now + SAVES_EVERY
        game_dir = self._game_dir or launch.load_settings().get("game_dir")
        if game_dir and os.path.isdir(game_dir):
            try:
                made = namedsaves.sync(game_dir)
            except OSError:
                made = []
            if made:
                self.status.set("Save copied to Named saves: " + ", ".join(made))

    def _auto_locate(self) -> None:
        """For Shattered Lands, point the party slots at the game's own tables."""
        if not self.layout.raw.get("auto_locate"):
            return
        if self.ds is None:
            self.ds = game.find_data_segment(self.guest)
            if self.ds is None:
                return
        creature, sheet = self.layout.records.get("creature"), self.layout.records.get("sheet")
        records = game.party_records(self.guest, self.ds)
        if not any(c for c, _ in records):  # the game restarted or quit: find DS again
            self.ds = None
            return
        for slot, (c, s) in enumerate(records[:self.layout.count]):
            if creature:
                creature.slots[slot] = c
            if sheet:
                sheet.slots[slot] = s

    # ---- dice log ---------------------------------------------------------------

    def _dice_tick(self) -> None:
        try:
            self._dosbox_closed()
            try:
                self._dice_step()
            except ProcessError as e:
                self._disconnected(e)
        except Exception as e:  # (anything else: said once, and the loop goes on)
            self._loop_error("the dice log", e)
        finally:
            self.root.after(DICE_MS, self._dice_tick)

    def _loop_error(self, what: str, err: Exception) -> None:
        """An error a refresh loop didn't expect: written to the dice log once for each kind (with
        where it came from, for a report), and the loop goes on."""
        import traceback
        from .dicelog import error_key
        key = (what,) + error_key(err)  # (by where, not its text: dicelog.error_key)
        seen = self.__dict__.setdefault("_loop_errors", set())
        if key in seen:
            return
        seen.add(key)
        where = traceback.extract_tb(err.__traceback__)[-1]
        try:
            self._append_dice([f"Loader error in {what}: {type(err).__name__}: {err} "
                               f"({os.path.basename(where.filename)}:{where.lineno}); it carries on"])
        except Exception:
            pass

    def _dice_step(self) -> None:
        if not self.guest:
            return
        now = time.monotonic()
        if self.dice is None or not self.dice.attached:
            if now < self.next_try:
                return
            self.next_try = now + RETRY_SECONDS
            if self.dice is None:
                try:  # (strictly: the pockets tried, as saved; one held elsewhere read again later)
                    saved, known = launch.load_settings(strict=True), True
                except launch.SettingsUnreadable:
                    saved, known = {}, False
                self.dice = DiceLog(self.guest)
                self.dice.use_settings(saved, picked_known=known)  # (the panel's size and state as saved; then the tab's own)
                self.dice.answer_stats_in_background()
                self.dice.speaker_names = launch.speaker_names()
                self.dice.learned_speakers = launch.learned_speakers()
                self.dice.monster_info = self.monster_info.get()
                self.dice.arena_ring = self.content_vars[launch.NEW_ITEMS].get()
                self.dice.starting_gear = self.starting_gear.get()
                self.dice.combat_log_level = self.combat_log_level.get()
                self.dice.floating_names = self.floating_names.get()
                self.dice.journal = self.journal if self.keep_journal.get() else None
                self.dice.game_dir = launch.find_game_dir()
                self.dice.ring_mode = self.ring_mode.get()
                self.dice.hit_chance = self.hit_chance.get()
                self.dice.hit_hover = self.hit_hover.get()
                self.dice.show_squares = self.show_squares.get()
                self.dice.move_back = self.move_back.get()
                self.dice.show_usable = self.show_usable.get()
                self.dice.quicksave.keys = self.quick_save.get()
                self.dice.quicksave.auto = self.autosave.get()
                self.dice.vulture_on = self.content_vars["vulture"].get()
                self.dice.defiler_scrolls = self.content_vars["defiler_scrolls"].get()
                self.dice.set_rules(self._rules())
            try:  # (one Loader at a time follows the game: two would both make its changes)
                launch.hold_game("the Loader's window")
            except launch.GameBusy as e:
                self.dice_status.set(str(e))
                return
            try:
                self.dice_status.set(self.dice.attach())
            except DiceLogError as e:
                self.dice_status.set(str(e))
                self._release_game()  # (nothing followed: the lock not kept from `play` meanwhile; taken again next try)
            return
        if now >= self.next_try:  # every couple of seconds: has the game restarted?
            self.next_try = now + RETRY_SECONDS
            if not self.dice.still_patched():
                self.dice.detach()
                self.dice_status.set("The game restarted; attaching again...")
                return
        lines = self.dice.lines(self.show_all.get())
        if lines:
            self._append_dice(lines)
        if self.dice.combat_log_level != self.combat_log_level.get():  # (the panel's level chip)
            self.combat_log_level.set(self.dice.combat_log_level)
        self.round_line.set(self._round_text())
        # (names worked out from conversations kept, and shown on earlier lines; the pockets tried
        # kept; a save the file refused tried again next pass)
        learned, failed = self.dice.save_learned(launch.add_learned_speakers, launch.set_pickpocketed,
                                                 lambda: launch.pickpocketed(tries=1))
        for portrait in learned:
            self._rename_portrait(portrait)
        if failed and not self._learned_unsaved:
            self.status.set("The Loader's settings could not be saved just now; it will try again.")
        self._learned_unsaved = failed
        talk = self.dice.take_dialogue()
        if talk:
            self._append_dialogue(talk)
        self._journal_tick()

    def _round_text(self) -> str:
        """The round in progress, in initiative order: who acts now, who is still to come."""
        try:
            status = self.dice.round_status()
        except (struct.error, IndexError, ValueError, OSError):
            return ""
        if not status:
            return ""
        def names(rows):
            return ", ".join(f"{name} {score}" for name, score in rows)
        parts = [f"Round {status['round']}." if status["round"] else "This round."]
        if status["now"]:
            parts.append(f"Now: {status['now'][0]} ({status['now'][1]}).")
        parts.append(f"Still to act: {names(status['next'])}." if status["next"] else "No one else to act.")
        if status["done"]:
            parts.append(f"Done: {names(status['done'])}.")
        if status["down"]:
            parts.append(f"Down: {names(status['down'])}.")
        return " ".join(parts)

    @staticmethod
    def _window_label(settings: dict) -> str:
        if settings.get("fullscreen"):
            return "Full screen"
        scale = settings.get("window_scale", launch.DEFAULT_SCALE)
        return next((label for label, v in WINDOW_CHOICES.items() if v == scale), "Triple (960x720)")

    def _window_chosen(self, _event=None) -> None:
        """Remember the game window's size; it applies the next time the game is started."""
        scale = WINDOW_CHOICES[self.window_choice.get()]
        if self._save_settings({"fullscreen": True} if scale is None else
                               {"fullscreen": False, "window_scale": scale}):
            plain = (" The picture is plain in a Single window."
                     if scale == 1 and self.picture.get() != launch.PLAIN else "")
            keys = ("in DOSBox-X, F12 and F together, F11 and F on Windows, switch"
                    if self.engine.get() == dosboxx.DOSBOX_X else "Alt+Enter switches")
            self.status.set(f"Game window: {self.window_choice.get()}, from the next start "
                            f"({keys} full screen while playing).{plain}")

    def _speed_chosen(self) -> None:
        """Remember the game's speed; it applies the next time the game is started."""
        value = self.game_speed.get()
        if self._save_settings({"cycles": value if value == launch.GOG_SPEED else int(value)}):
            self.status.set("Game speed: from the next start.")

    def _picture_chosen(self) -> None:
        """Remember the picture; it applies the next time the game is started. In a Single window
        there is only the plain one, and the status line says so."""
        self._options_changed()
        if self._options_shown.get("picture") != self.picture.get():
            return  # (not saved: the status line says why)
        if self.picture.get() != launch.PLAIN and WINDOW_CHOICES[self.window_choice.get()] == 1:
            self.status.set("Picture: remembered, but a Single game window is always plain; pick a larger "
                            "Game window (or Full screen) to see it.")
        else:
            self.status.set("Picture: from the next start.")

    def _midi_value(self) -> Optional[midiout.Device]:
        """The music device the box shows; None when what was typed is no device."""
        return midiout.from_label(self.midi_device.get())

    def _show_midi(self, device: midiout.Device) -> None:
        """DEVICE in the music device's box (a list of names on Windows, a field elsewhere)."""
        if self.midi_names is None:
            self.midi_device.set("" if device == midiout.DEFAULT else str(device))
        else:
            self.midi_box.configure(values=midiout.labels(self.midi_names, device))
            self.midi_device.set(midiout.label(device, self.midi_names))

    def _midi_chosen(self) -> None:
        """Remember the music device; it applies the next time the game is started. Something
        typed that is no device is not kept: the box goes back to the one remembered."""
        device = self._midi_value()
        if device is None:
            self._show_midi(self._options_shown.get(midiout.SETTING, midiout.DEFAULT))
            self.status.set("Music device: a number (0 is Windows' first device), an ALSA port such as 128:0, "
                            "or empty for the default.")
            return
        if device != self._options_shown.get(midiout.SETTING):
            self._options_changed()
            self.soundfont_status.set(self._soundfont_line())
            self.status.set("Music device: from the next start.")

    def _option_values(self) -> dict:
        """Every switch of the Options tab as the tab shows it: {settings key: value}."""
        values = {"monster_info": self.monster_info.get(), "floating_names": self.floating_names.get(),
                  "combat_log_level": self.combat_log_level.get(), "starting_gear": self.starting_gear.get(),
                  "rings": self.ring_mode.get(), "steady_pace": self.steady_pace.get(),
                  "hit_chance": self.hit_chance.get(), "hit_hover": self.hit_hover.get(), "squares": self.show_squares.get(), "move_back": self.move_back.get(), "show_usable": self.show_usable.get(), "quick_save": self.quick_save.get(),
                  "autosave": self.autosave.get(), "picture": self.picture.get(),
                  dosboxx.SETTING: self.engine.get()}
        device = self._midi_value()  # (something typed that is no device: the one remembered stays)
        values[midiout.SETTING] = getattr(self, "_options_shown", {}).get(
            midiout.SETTING, midiout.DEFAULT) if device is None else device
        values.update({key: var.get() for key, var in self.content_vars.items()})
        values.update({key: var.get() for key, var in self.rule_vars.items()})
        return values

    def _options_changed(self, every: bool = False) -> None:
        """A switch on the Options tab changed: saved, and the log told. Only the switches changed
        since the tab was read or last saved are written (EVERY: all of them, for Restore defaults),
        so a tab that had to show the defaults (settings.json held elsewhere as it opened) never
        puts them over the player's other choices."""
        values = self._option_values()
        shown = getattr(self, "_options_shown", {})
        changes = values if every else {key: value for key, value in values.items()
                                        if key not in shown or shown[key] != value}
        try:
            with launch.SETTINGS_LOCK:  # (read and written as one step)
                settings = launch.load_settings(strict=True)
                for old in ("turn_popups", "turn_popups_level", "turn_popups_detail"):  # (the turn pop-up, gone)
                    settings.pop(old, None)
                settings.update(changes)
                launch.save_settings(settings)
        except OSError as e:  # (settings.json held elsewhere: kept as it was, not saved over)
            self.status.set(f"The options could not be saved just now ({e}); change one again to retry.")
            return
        self._options_shown = values
        if self.dice is not None:
            self.dice._settings = settings  # (the item reports' switches, as now)
            self.dice.set_monster_info(self.monster_info.get())
            self.dice.arena_ring = self.content_vars[launch.NEW_ITEMS].get()
            self.dice.starting_gear = self.starting_gear.get()
            self.dice.combat_log_level = self.combat_log_level.get()
            self.dice.floating_names = self.floating_names.get()
            self.dice.ring_mode = self.ring_mode.get()
            self.dice.hit_chance = self.hit_chance.get()
            self.dice.hit_hover = self.hit_hover.get()
            self.dice.show_squares = self.show_squares.get()
            self.dice.move_back = self.move_back.get()
            self.dice.show_usable = self.show_usable.get()
            self.dice.quicksave.keys = self.quick_save.get()
            self.dice.quicksave.auto = self.autosave.get()
            self.dice.vulture_on = self.content_vars["vulture"].get()
            self.dice.defiler_scrolls = self.content_vars["defiler_scrolls"].get()
            self.dice.set_rules(self._rules())

    def _rules(self) -> int:
        return game.rules_from_settings({key: var.get() for key, var in self.rule_vars.items()})

    def show_spells(self) -> None:
        """Fill the Spells tab from the running game's records."""
        self.spell_text.delete("1.0", "end")
        if not self.guest or self.ds is None:
            self.spell_text.insert("end", "Connect to the game to read its spells.")
            return
        try:
            spells = spellbook.all_spells(game.GameData(self.guest, self.ds, self._rules()))
        except (struct.error, IndexError, ValueError, OSError) as e:
            self.spell_text.insert("end", f"Couldn't read the spells: {e}")
            return
        kind = self.spell_kind.get()
        shown = [s for s in spells if (kind == "All" or s.magic == kind)
                 and (not self.spells_party.get() or s.casters)]
        for info in shown:
            first, *rest = info.lines()
            self.spell_text.insert("end", first + "\n", "name")
            self.spell_text.insert("end", "".join(line + "\n" for line in rest) + "\n")
        if not shown:
            self.spell_text.insert("end", "No spells to show.")
        self._spells_shown = True

    def _speaker_clicked(self, event) -> None:
        tags = self.talk_text.tag_names(f"@{event.x},{event.y}")
        portrait = next((int(t.split()[1]) for t in tags if t.startswith("portrait ")), None)
        self.name_speaker(portrait)

    def name_speaker(self, portrait: Optional[int]) -> None:
        """Ask for a name for a dialogue portrait, remember it, and show it on every line from it."""
        from tkinter import simpledialog
        if portrait is None or self.dice is None:
            messagebox.showinfo("Name speaker", "No one with a portrait has spoken yet.", parent=self.root)
            return
        shown = self.dice.speaker(portrait)
        name = simpledialog.askstring(
            "Name speaker", f"Name for the speaker shown as \"{shown}\" (portrait {portrait}).\n"
            "Leave it empty to go back to the default.", initialvalue=self.dice.speaker_names.get(portrait, ""),
            parent=self.root)
        if name is None:
            return
        name = " ".join(name.split())
        try:
            launch.set_speaker_name(portrait, name)
        except OSError as e:  # (settings.json held a moment: an antivirus, a backup)
            self.status.set(f"The name could not be saved just now ({e}); name the speaker again to retry.")
            return
        if name:
            self.dice.speaker_names[portrait] = name
        else:
            self.dice.speaker_names.pop(portrait, None)
        self._rename_portrait(portrait)

    # ---- the journal (journal.py) ------------------------------------------------

    def _build_journal(self, tabs: ttk.Notebook, settings: dict) -> None:
        """The Journal tab: the game's journal (what was said, the replies chosen, rewards and
        messages, under each day and area), kept on disk and following the game's saves."""
        self.journal = journal.Journal()
        self._journal_drawn = (-1, None, None)  # (journal.changed, the kinds shown, the words wanted) as drawn
        self._journal_place = (None, None)  # the day and region of the last entry drawn
        self._quests_kept = (None, None, 0.0)  # the quests' reading last written: (the head, the reading, when)
        page = ttk.Frame(tabs, padding=6)
        tabs.add(page, text="Journal", underline=0)
        row = ttk.Frame(page)
        row.pack(fill="x")
        self.keep_journal = tk.BooleanVar(value=settings.get("journal", True) is not False)
        ttk.Checkbutton(row, text="Keep a journal", variable=self.keep_journal,
                        command=self._journal_switched).pack(side="left")
        ttk.Button(row, text="Save...", command=lambda: self.save_text(self.journal_text, "journal")).pack(side="right")
        ttk.Button(row, text="Open the folder", command=self._open_journal_folder).pack(side="right", padx=4)
        pick = ttk.Frame(page)
        pick.pack(fill="x", pady=(4, 0))
        ttk.Label(pick, text="Show:").pack(side="left")
        self.journal_kind = tk.StringVar(value=JOURNAL_SHOWS[0][0])
        kinds = ttk.Combobox(pick, textvariable=self.journal_kind, state="readonly", width=22,
                             values=[label for label, _ in JOURNAL_SHOWS] + [JOURNAL_QUESTS])
        kinds.pack(side="left", padx=(4, 12))
        kinds.bind("<<ComboboxSelected>>", lambda _e: self._journal_tick())
        ttk.Label(pick, text="Only entries with:").pack(side="left")
        self.journal_wanted = tk.StringVar()
        ttk.Entry(pick, textvariable=self.journal_wanted, width=18).pack(side="left", padx=(4, 0))
        self.journal_wanted.trace_add("write", lambda *_a: self._journal_tick())
        self.journal_count = tk.StringVar()
        ttk.Label(pick, textvariable=self.journal_count).pack(side="left", padx=(8, 0))
        find = ttk.Frame(page)
        find.pack(fill="x", pady=(4, 0))
        box = ttk.Frame(page)
        box.pack(fill="both", expand=True, pady=(6, 0))
        self.journal_text = tk.Text(box, wrap="word", height=20, font="TkTextFont")
        theme.style_text(self.journal_text)
        self.journal_text.configure(foreground=theme.AMBER)
        scroll = ttk.Scrollbar(box, command=self.journal_text.yview)
        self.journal_text.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.journal_text.pack(side="left", fill="both", expand=True)
        self._follow_end(self.journal_text, scroll)
        self.journal_text.tag_configure("day", font=theme.fonts()[1], foreground=theme.SAND)
        self.journal_text.tag_configure("speaker", font=theme.fonts()[1], foreground=theme.YELLOW)
        self.journal_text.tag_configure("reply", foreground=theme.PALE)
        self.journal_text.tag_configure("chosen", foreground=theme.GREEN)
        self.journal_text.tag_configure("reward", foreground=theme.GREEN)
        self.journal_text.tag_configure("message", foreground=theme.PALE)
        self.journal_text.tag_configure("note", foreground=theme.PALE)
        self._find_bar(find, self.journal_text, page)
        self._journal_tick()

    def _journal_switched(self) -> None:
        on = self.keep_journal.get()
        if self._save_settings({"journal": on}):
            self.status.set("The journal is kept from now on." if on else
                            "The journal is no longer kept; what it holds stays.")
        if self.dice is not None:
            self.dice.journal = self.journal if on else None
            if on:
                self.journal.reset()

    def _open_journal_folder(self) -> None:
        try:
            os.makedirs(journal.FOLDER, exist_ok=True)
            if sys.platform == "win32":
                os.startfile(journal.FOLDER)  # type: ignore[attr-defined]
            else:
                subprocess.Popen(["xdg-open", journal.FOLDER])
        except OSError as e:
            messagebox.showerror("The journal", f"Its folder could not be opened:\n{e}", parent=self.root)

    def _journal_speaker(self, entry) -> str:
        """Who said an entry: the portrait's name as known now, else as it was when said."""
        if entry.portrait and self.dice is not None:
            name = self.dice.speaker(entry.portrait)
            if not name.startswith("Portrait "):
                return name
        return entry.speaker

    def _journal_tick(self) -> None:
        """The Journal tab kept up: new entries added at its end; drawn again when the game's
        journal became another (a save loaded) or what to show was changed."""
        kinds = dict(JOURNAL_SHOWS).get(self.journal_kind.get())
        wanted = self.journal_wanted.get().strip()
        text = self.journal_text
        self._quests_keep()
        if self.journal_kind.get() == JOURNAL_QUESTS:
            self.journal.take_added()
            reading, note = self._quests_reading()
            made, open_, finished = quests.rows(reading, quests.rewards_of(self.journal.shown()), wanted, note)
            state = ("quests", made)
            if state != self._journal_drawn:
                self._journal_drawn = state
                text.delete("1.0", "end")
                for kind, line in made:
                    text.insert("end", line + "\n", () if kind in ("gap", "text") else (kind,))
                self.journal_count.set(quests.count_text(open_, finished))
                text.see("1.0")
            return
        state = (self.journal.changed, self.journal_kind.get(), wanted)
        if state != self._journal_drawn:
            self._journal_drawn = state
            self.journal.take_added()
            entries = self.journal.shown()
            shown = journal.chosen(entries, kinds, wanted)
            text.delete("1.0", "end")
            self._journal_place = (None, None)
            self._journal_insert(shown)
            total = sum(1 for e in entries if e.kind != journal.CHOSEN)
            some = sum(1 for e in shown if e.kind != journal.CHOSEN)
            self.journal_count.set(f"{some} of {total}" if (kinds is not None or wanted) else
                                   (f"{total} entr{'y' if total == 1 else 'ies'}" if total else "Nothing yet"))
            text.see("end")
            return
        added = self.journal.take_added()
        if not added:
            return
        if kinds is not None or wanted:  # (a choice of entries: looked at whole, a reply with its talk)
            self._journal_drawn = (-1, None, None)
            self._journal_tick()
            return
        self._journal_insert(added)
        total = sum(1 for e in self.journal.shown() if e.kind != journal.CHOSEN)
        self.journal_count.set(f"{total} entr{'y' if total == 1 else 'ies'}")
        if self._following.get(text, True):
            text.see("end")

    def _quests_live(self):
        """The game's flags and numbers as the dice log last read them (quests.State), or None
        with no game attached or before its first reading."""
        dice = self.dice
        return dice.quest_state if dice is not None and dice.attached else None

    def _quests_reading(self):
        """(the reading the quests are shown from, a note for the top of the list): the game's
        own while it runs; without it the last one written (quests.save_snapshot), if the
        journal shown is the one it was made in (its head is an entry of the chain shown, or
        both are empty); else none, and only the journal's own rewards tell of quests."""
        live = self._quests_live()
        if live is not None:
            return live, ""
        kept = quests.load_snapshot(quests.snapshot_path(self.journal.path))
        if kept is not None:
            shown = self.journal.shown()
            if kept[0] in {entry.id for entry in shown} or (kept[0] == 0 and not shown):
                return kept[1], QUESTS_AS_READ
        return None, QUESTS_UNREAD

    def _quests_keep(self, now: bool = False) -> None:
        """The game's reading written for the next time the Loader runs without the game (with
        the journal's head it was made at), when it changed, every few seconds at most."""
        live, head = self._quests_live(), self.journal.head
        if live is None or head is None:
            return
        kept_head, kept, at = self._quests_kept
        clock = time.monotonic()
        if (head, live) == (kept_head, kept) or (not now and kept is not None and clock - at < QUESTS_KEPT_EVERY):
            return
        if quests.save_snapshot(quests.snapshot_path(self.journal.path), head, live):
            self._quests_kept = (head, live, clock)

    def _journal_insert(self, entries) -> None:
        text = self.journal_text
        made = journal.rows(entries, self._journal_speaker, self._journal_place)
        if made and made[0][0] == "chosen" and text.get("end-2c", "end-1c") == "\n" and text.index("end-1c") != "1.0":
            text.delete("end-2c")  # (an answer to the replies above: into the gap under them)
        for kind, line in made:
            text.insert("end", line + "\n", () if kind in ("gap", "text") else (kind,))
        for entry in entries:
            if journal.place(entry) != (None, None):
                self._journal_place = journal.place(entry)

    def _rename_portrait(self, portrait: int) -> None:
        """Show a portrait's current name on every line already shown from it."""
        tag = f"portrait {portrait}"
        ranges = self.talk_text.tag_ranges(tag)
        for start, end in reversed(list(zip(ranges[0::2], ranges[1::2]))):
            self.talk_text.delete(start, end)
            self.talk_text.insert(start, self.dice.speaker(portrait), ("speaker", tag))

    def clear_dialogue(self) -> None:
        self.talk_text.delete("1.0", "end")
        self._images.clear()

    def _append_dialogue(self, entries) -> None:
        for entry in entries:
            if entry.chosen:  # the player's answer to the replies above
                self.talk_text.delete("end-2c")  # into the gap under the replies
                self.talk_text.insert("end", f"  You chose: {entry.chosen}\n\n", "chosen")
                continue
            face = self.art.portrait(entry.portrait) if entry.portrait else None
            if face:  # the game's portrait, twice its size (more at larger text sizes)
                size = max(2, round(2 * theme.scale()))
                image = self._images.get((entry.portrait, size))
                if image is None:
                    image = self._images[(entry.portrait, size)] = art.photo(self.root, face, size, background=theme.DEEP)
                self.talk_text.image_create("end", image=image, padx=2, pady=4, align="center")
                self.talk_text.insert("end", " ")
            tags = ("speaker", f"portrait {entry.portrait}") if entry.portrait else ("speaker",)
            self.talk_text.insert("end", self.dice.speaker(entry.portrait), tags)
            self.talk_text.insert("end", "\n")
            if entry.portrait:
                self._last_portrait = entry.portrait
            if entry.text:
                self.talk_text.insert("end", entry.text + "\n")
            if entry.title:
                self.talk_text.insert("end", f"  ({entry.title})\n", "reply")
            for n, reply in enumerate(entry.replies, 1):
                self.talk_text.insert("end", f"  {n}. {reply}\n", "reply")
            self.talk_text.insert("end", "\n")
        excess = int(self.talk_text.index("end-1c").split(".")[0]) - MAX_LOG_LINES
        if excess > 0:  # (kept to the last MAX_LOG_LINES lines, as the dice log)
            self.talk_text.delete("1.0", f"{excess + 1}.0")
        if self._following.get(self.talk_text, True):
            self.talk_text.see("end")

    def _find_bar(self, row: ttk.Frame, text: tk.Text, tab: ttk.Frame) -> None:
        """A find box over a log: every match (any case) marked, Enter or Next to the next one,
        Shift+Enter or Previous back (round the end), Escape to clear; the log stops following
        its newest line while a match is shown, so new lines don't take it away. Hidden lines
        (details turned off) aren't searched."""
        wanted = tk.StringVar()
        where = tk.StringVar()
        ttk.Label(row, text="Find (Ctrl+F):").pack(side="left")
        entry = ttk.Entry(row, textvariable=wanted, width=16)
        entry.pack(side="left", padx=(4, 0))
        self._finds[tab] = entry
        text.tag_configure("found", background=theme.SAND, foreground=theme.SHADOW)
        text.tag_configure("found_now", background=theme.AMBER, foreground=theme.SHADOW)
        shown = {"at": None}

        def matches() -> List[Tuple[str, str]]:
            text.tag_remove("found", "1.0", "end")
            text.tag_remove("found_now", "1.0", "end")
            pattern = wanted.get()
            if not pattern:
                return []
            out, start, length = [], "1.0", tk.IntVar()
            while True:
                at = text.search(pattern, start, stopindex="end", nocase=True, count=length)
                if not at or length.get() == 0:
                    return out
                end = f"{at}+{length.get()}c"
                out.append((at, end))
                text.tag_add("found", at, end)
                start = end

        def go(step: int) -> None:
            found = matches()
            if not found:
                shown["at"] = None
                where.set("no match" if wanted.get() else "")
                return
            starts = [text.index(a) for a, _ in found]
            last = shown["at"]
            if last is None:  # (a new search: Next from the top, Previous from the bottom)
                k = 0 if step > 0 else len(found) - 1
            else:
                after = [i for i, a in enumerate(starts) if text.compare(a, ">" if step > 0 else "<", last)]
                k = (after[0] if step > 0 else after[-1]) if after else (0 if step > 0 else len(found) - 1)
            at, end = found[k]
            shown["at"] = starts[k]
            text.tag_add("found_now", at, end)
            text.tag_raise("found")
            text.tag_raise("found_now")
            self._following[text] = False
            text.see(at)
            where.set(f"{k + 1} of {len(found)}")

        def clear(_event=None) -> str:
            wanted.set("")
            shown["at"] = None
            matches()
            where.set("")
            return "break"

        entry.bind("<Return>", lambda _e: go(1))
        entry.bind("<KP_Enter>", lambda _e: go(1))
        entry.bind("<Shift-Return>", lambda _e: go(-1))
        entry.bind("<Escape>", clear)
        wanted.trace_add("write", lambda *_a: shown.update(at=None))
        ttk.Button(row, text="Previous", command=lambda: go(-1)).pack(side="left", padx=(4, 0))
        ttk.Button(row, text="Next", command=lambda: go(1)).pack(side="left", padx=(4, 0))
        ttk.Label(row, textvariable=where).pack(side="left", padx=(8, 0))

    def _focus_find(self, tabs: ttk.Notebook) -> str:
        """Ctrl+F: the find box of the log tab shown (none on the others)."""
        entry = self._finds.get(self.root.nametowidget(tabs.select())) if tabs.select() else None
        if entry is not None:
            entry.focus_set()
            entry.select_range(0, "end")
        return "break"

    def _follow_end(self, text: tk.Text, scroll: ttk.Scrollbar) -> None:
        """A log keeps its newest line in view unless the reader has scrolled up to read back:
        following stops when they scroll up and starts again when they scroll to the bottom (by
        the wheel, the scrollbar or the keys). New lines that came while its tab was hidden are
        in view when it's shown."""
        self._following[text] = True

        def check(_event=None) -> None:
            first, last = text.yview()
            self._following[text] = last >= 0.999 or text.dlineinfo("end-1c") is not None

        def later(_event=None) -> None:
            text.after_idle(check)

        def scrolled(*args) -> None:
            text.yview(*args)
            later()

        scroll.configure(command=scrolled)
        for event in ("<MouseWheel>", "<Button-4>", "<Button-5>", "<KeyRelease>", "<ButtonRelease-1>"):
            text.bind(event, later, add="+")
        text.bind("<Map>", lambda _e: self._following.get(text, True) and text.after_idle(lambda: text.see("end")),
                  add="+")

    def _log_names(self) -> List[Tuple[str, str]]:
        """(name, tag) for the dice log's names: the party's by place, then the monsters met in
        fights (longest first, so "Mountain Stalker" wins over a "Stalker" inside it)."""
        party: Dict[str, str] = {}
        try:
            g = self.dice.game if self.dice is not None and self.dice.attached else None
            if g is not None:
                for n in range(game.PARTY_SIZE):
                    name = g.creature_name(n)
                    if name and not name.startswith("creature "):  # (an empty place in the party)
                        party.setdefault(name, f"member{n}")
                for index in set(g.combatants().values()):
                    name = g.creature_name(index)
                    if index >= game.PARTY_SIZE and name and name not in party:
                        self._monster_names.add(name)
        except (struct.error, IndexError, ValueError, AttributeError):
            pass
        names = list(party.items()) + [(m, "monster") for m in self._monster_names if m not in party]
        return sorted(names, key=lambda pair: -len(pair[0]))

    def _colour_names(self, line: str, names: List[Tuple[str, str]]) -> None:
        """Tag each name in the line just added (the last line of the log)."""
        row = int(self.dice_text.index("end-1c").split(".")[0]) - 1
        taken: List[Tuple[int, int]] = []
        for name, tag in names:
            for found in re.finditer(r"(?<!\w)" + re.escape(name) + r"(?!\w)", line):
                start, end = found.span()
                if any(start < b and a < end for a, b in taken):
                    continue
                taken.append((start, end))
                self.dice_text.tag_add(tag, f"{row}.{start}", f"{row}.{end}")

    def _append_dice(self, lines: List[str], keep: bool = True) -> None:
        names = self._log_names() if lines else []
        if keep:
            self._raw_dice.extend(lines)
        readable = self.readable.get()
        if readable:
            party = {name for name, tag in names if tag.startswith("member")}
            self._ledger.is_party = party.__contains__
        for line in lines:
            if not readable:
                tag = combatlog.line_kind(line)
                self.dice_text.insert("end", line + "\n", tag)
                self._colour_names(line, names)
                continue
            for op in self._ledger.feed(line):
                if isinstance(op, ledger.Fill):
                    self._fill(op, names)
                else:
                    self._row(op, line, names)
        excess = int(self.dice_text.index("end-1c").split(".")[0]) - MAX_LOG_LINES
        if excess > 0:
            self.dice_text.delete("1.0", f"{excess + 1}.0")
            for sid in [sid for sid in self._slots if self.dice_text.index(sid) == "1.0"]:
                self.dice_text.mark_unset(sid)  # (its row gone: never filled)
                self._slots.discard(sid)
        if self._following.get(self.dice_text, True):
            self.dice_text.see("end")

    _KIND_TAGS = {ledger.EVENT: ("lg_event",), ledger.DETAIL: ("detail", "lg_detail"), ledger.TURN: ("lg_turn",),
                  ledger.ROUND: ("lg_round",), ledger.SUMMARY: ("lg_summary",)}

    def _row(self, row: "ledger.Row", line: str, names: List[Tuple[str, str]]) -> None:
        """A row of the readable layout at the log's end, its slots marked for their fills."""
        start = self.dice_text.index("end-1c")
        kind_tags = self._KIND_TAGS.get(row.kind) or (row.plain_kind or combatlog.line_kind(line),)
        for piece in row.pieces:
            if piece.slot:
                self.dice_text.mark_set(piece.slot, "end-1c")
                self.dice_text.mark_gravity(piece.slot, "left")  # (the rows after it come after it)
                self._slots.add(piece.slot)
                continue
            tags = kind_tags if row.kind == ledger.PLAIN else kind_tags + (f"lg_{piece.role}",)
            self.dice_text.insert("end", piece.text, tags)
        self.dice_text.insert("end", "\n", kind_tags)
        if row.kind != ledger.DETAIL:  # (the working stays dim: the names stand out above it)
            self._colour_range(start, self.dice_text.index("end-1c"), names)

    def _fill(self, fill: "ledger.Fill", names: List[Tuple[str, str]]) -> None:
        """A slot an earlier row left, filled (a hit's damage, the HP left)."""
        if fill.slot not in self._slots:
            return
        self._slots.discard(fill.slot)
        at = self.dice_text.index(fill.slot)
        line_tags = tuple(t for t in self.dice_text.tag_names(f"{at} linestart") if t.startswith("lg_event"))
        for piece in reversed(fill.pieces):
            self.dice_text.insert(fill.slot, piece.text, line_tags + (f"lg_{piece.role}",))
        end = self.dice_text.index(f"{at}+{sum(len(p.text) for p in fill.pieces)}c")
        self.dice_text.mark_unset(fill.slot)
        self._colour_range(at, end, names)

    def _colour_range(self, start: str, end: str, names: List[Tuple[str, str]]) -> None:
        """Tag each name between START and END (a row or a fill just added)."""
        text = self.dice_text.get(start, end)
        taken: List[Tuple[int, int]] = []
        for name, tag in names:
            for found in re.finditer(r"(?<!\w)" + re.escape(name) + r"(?!\w)", text):
                a, b = found.span()
                if any(a < y and x < b for x, y in taken):
                    continue
                taken.append((a, b))
                self.dice_text.tag_add(tag, f"{start}+{a}c", f"{start}+{b}c")

    def _set_columns(self, width: int) -> None:
        """The event rows' columns: the HP right-aligned, then the roll, both at the window's right."""
        char = tkfont.nametofont("TkFixedFont").measure("0")
        roll_at = max(char * 40, width - 16 - char * 30)
        self.dice_text.tag_configure("lg_event", tabs=(roll_at - char * 2, "right", roll_at, "left"),
                                     lmargin2=char * 4)
        small = tkfont.nametofont("LedgerFixedSmall").measure("0")
        self.dice_text.tag_configure("lg_detail", lmargin2=small * 8)  # (a long working's next lines, under it)

    def _layout_changed(self) -> None:
        """The readable layout on or off: the log shown again from its own lines."""
        self._save_settings({"dice_layout": "readable" if self.readable.get() else "classic"})
        self.dice_text.delete("1.0", "end")
        for sid in self._slots:
            self.dice_text.mark_unset(sid)
        self._slots.clear()
        self._ledger = ledger.Ledger(lambda name: False)
        self._append_dice(list(self._raw_dice), keep=False)

    def clear_dice(self) -> None:
        self.dice_text.delete("1.0", "end")
        self._raw_dice.clear()
        self._slots.clear()
        self._ledger = ledger.Ledger(lambda name: False)

    def save_dice(self) -> None:
        """Save the log's own lines (as written, whichever layout shows them)."""
        path = filedialog.asksaveasfilename(title="Save the dice log", defaultextension=".txt",
                                            filetypes=[("Text", "*.txt"), ("All files", "*.*")], parent=self.root)
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write("\n".join(self._raw_dice) + "\n")
        except OSError as e:
            messagebox.showerror("Save", f"Couldn't save the dice log: {e}", parent=self.root)

    def _ac_rows(self, slots) -> List[Tuple[str, List[str]]]:
        """The AC the game last worked out for each character in a fight, and what it was made
        of, as the dice log sees them; "-" until then."""
        labels = ("Current AC", "  AC: armour, shield", "  AC: DEX", "  AC: spells, rings, other")
        if not (self.dice and self.dice.attached and self.ds is not None and "creature" in self.layout.records):
            return [(label, ["-"] * len(slots)) for label in labels]
        table = game.far_pointer(self.guest, self.ds, game.CREATURES_PTR)
        columns = []
        for s in slots:
            addr = s[1].get("creature")
            index = (addr - table) // game.CREATURE_SIZE if addr is not None else None
            ac, detail = self.dice.last_ac.get(index), self.dice.ac_detail.get(index)
            if detail is None or detail.total != ac:
                columns.append(["-" if ac is None else str(ac), "-", "-", "-"])
            else:
                columns.append([str(ac)] + [f"{v:+d}" for v in (detail.armour, detail.dex, detail.other)])
        return [(label, [c[i] for c in columns]) for i, label in enumerate(labels)]

    def _now_rows(self, slots) -> List[Tuple[str, List[str]]]:
        """THAC0 with each weapon ready, and the d20 each save needs, as they stand now."""
        labels = ("  THAC0 now, each weapon", "  Saves now " + "/".join(game.SAVE_SHORT))
        if self.ds is None:
            return [(label, [""] * len(slots)) for label in labels]
        gd = game.GameData(self.guest, self.ds, self._rules())
        table = game.far_pointer(self.guest, self.ds, game.CREATURES_PTR)
        hits, saves = [], []
        for s in slots:
            addr = s[1].get("creature")
            index = (addr - table) // game.CREATURE_SIZE if addr is not None else None
            try:
                known = index is not None and 0 <= index < game.PARTY_SIZE
                hits.append(", ".join(f"{h.thac0} {h.name}" for h in gd.weapon_hits(index)) if known and gd.items_readable(index) else "")
                saves.append(" ".join(str(x.needs) for x in gd.saves_now(index)) if known else "")
            except (struct.error, IndexError, ValueError):
                hits.append("")
                saves.append("")
        return [(labels[0], hits), (labels[1], saves)]

    def _member_slots(self, slots) -> List[list]:
        """Each slot's spell slots (GameData.spell_slots), or [] when the game isn't running."""
        if self.ds is None:
            return [[] for _ in slots]
        gd = game.GameData(self.guest, self.ds, self._rules())
        table = game.far_pointer(self.guest, self.ds, game.CREATURES_PTR)
        out = []
        for s in slots:
            addr = s[1].get("creature")
            index = (addr - table) // game.CREATURE_SIZE if addr is not None else None
            try:
                out.append(gd.spell_slots(index) if index is not None and 0 <= index < 4 else [])
            except (struct.error, IndexError):
                out.append([])
        return out

    def _slot_rows(self, slots) -> List[Tuple[str, List[str]]]:
        """'Wizard spells left' / 'Priest spells left': '1st 3/5, 2nd 2/3', left of the most."""
        per_member = [dict(m) for m in self._member_slots(slots)]
        rows = [(f"{kind} spells left", [game.slots_text(m.get(kind, [])) for m in per_member])
                for kind, _ in game.MAGIC_KINDS]
        if self.ds is not None:  # each thief's skills as they stand (equipment and effects)
            gd = game.GameData(self.guest, self.ds, self._rules())
            table = game.far_pointer(self.guest, self.ds, game.CREATURES_PTR)
            cells = []
            for s in slots:
                addr = s[1].get("creature")
                skills = gd.thief_skills_now((addr - table) // game.CREATURE_SIZE, game.LEDGER_SKILLS) \
                    if addr is not None else []
                cells.append(" ".join(f"{n}" for _, n in skills))
            rows.append(("Thief skills PP/OL/FT/MS/HS/HN/CW", cells))
            worn = []
            for s in slots:
                addr = s[1].get("creature")
                who = (addr - table) // game.CREATURE_SIZE if addr is not None else None
                items = gd.equipment(who) if who is not None and gd.items_readable(who) else []
                worn.append(", ".join(f"{slot}: {item}" if slot else item for slot, item in items))
            rows.append(("Equipment", worn))
        return rows

    def _refresh_table(self) -> None:
        slots = [self.layout.decode_slot(i, self.guest.read) for i in range(self.layout.count)]
        rows = [(f"{r} @", [f"{s[1][r]:#x}" if s[1][r] is not None else "" for s in slots])
                for r in self.layout.records] if self.show_addresses.get() else []
        for i, s in enumerate(slots):  # the game shows names in capitals
            self.table.heading(f"slot{i}", text=s[0].upper() if s[0] else f"Slot {i + 1}")
        labels = [f.label for f in self.layout.fields]
        for i, f in enumerate(self.layout.fields):
            cells = [s[2][i][1] for s in slots]
            if f"Max {f.label}" in labels:  # "54/54", as the game shows HP and PSP
                top = labels.index(f"Max {f.label}")
                cells = [f"{c}/{s[2][top][1]}" if c != "" else "" for c, s in zip(cells, slots)]
            elif f.label.startswith("Max ") and f.label[4:] in labels:
                continue
            rows.append((f.label, cells))
            if f.label == "Base AC":
                rows += self._ac_rows(slots)
            elif f.label == "THAC0":
                rows += self._now_rows(slots)[:1]
            elif f.label == "Save: Spell":
                rows += self._now_rows(slots)[1:]
        rows += self._slot_rows(slots)

        self._refresh_cards(slots)
        existing = self.table.get_children()
        if len(existing) != len(rows):
            self.table.delete(*existing)
            existing = [self.table.insert("", "end") for _ in rows]
        for item, (label, cells) in zip(existing, rows):
            self.table.item(item, values=[label] + cells)
        # the columns widened to the longest label and value shown (never narrowed while it runs)
        widest = (max([label for label, _ in rows] + [self._widest[0]], key=len),
                  max([c for _, cells in rows for c in cells] + [self._widest[1]], key=len))
        if widest != self._widest:
            self._widest = widest
            self._fit_party(divider=False)

    def _refresh_cards(self, slots) -> None:
        """The Characters tab: each slot's card, with its condition and current AC."""
        gd = game.GameData(self.guest, self.ds, self._rules()) if self.ds is not None else None
        effects = gd.effects_left() if gd else []
        combatants = gd.combatants() if gd else {}
        table = game.far_pointer(self.guest, self.ds, game.CREATURES_PTR) if gd else None
        spell_slots = self._member_slots(slots)
        for card, (name, bases, fields), member_slots in zip(self.cards.cards, slots, spell_slots):
            status, ac = "", None
            addr = bases.get("creature")
            if gd and addr is not None and table is not None:
                index = (addr - table) // game.CREATURE_SIZE
                code = self.guest.read(addr + game.CREATURE_STATUS, 1)[0]
                status = game.STATUS_NAMES.get(code, "")
                mine = [c for c, i in combatants.items() if i == index]
                names = sorted({game.effect_text(e, charges, seconds) for e, charges, seconds in effects
                                if e.owner in mine})
                if names:
                    status += (", " if status else "") + ", ".join(names)
                ac = self.dice.last_ac.get(index) if self.dice and self.dice.attached else None
            known = gd and addr is not None and table is not None
            thief = gd.thief_skills_now(index, game.LEDGER_SKILLS) if known else []
            label = "Thief skills now"
            if known and thief and index < game.PARTY_SIZE and gd.thief_heavy(index):
                label = "Thief skills now (none in armour that isn't light)"
            if known and not thief:  # a ranger's, for the stealth rule (always on)
                thief, label = gd.ranger_skills_now(index), "Ranger skills now"
            # (before the game loads its item tables, at the menu or creating characters, items read
            # as noise: no equipment then, and attacks from the sheet alone)
            items_ok = bool(known and gd.items_readable(index))
            equipment = gd.equipment(index) if items_ok else []
            try:
                hits = gd.weapon_hits(index) if items_ok and index < game.PARTY_SIZE else []
                saves = gd.saves_now(index) if known and index < game.PARTY_SIZE else []
            except (struct.error, IndexError, ValueError):
                hits, saves = [], []
            try:
                weapons = gd.specializations(index) if known and index < game.PARTY_SIZE else []
                no_spells = bool(known and index < game.PARTY_SIZE and gd.no_spells(index))
                kit = gd.kit(index) if known and index < game.PARTY_SIZE else None
                kit_move = sum(kits.move(k) for k in gd.kit_ids(index)) if kit else 0
                move_why = [kit] if kit_move else []
            except (struct.error, IndexError, ValueError):
                weapons, no_spells, kit, kit_move, move_why = [], False, None, 0, []
            age = None
            if known and index < game.PARTY_SIZE:  # (ages: always on)
                from . import aging
                try:
                    age = aging.describe(gd.sheet(index))
                except (struct.error, IndexError, ValueError):
                    age = None
            card.show(name, dict(fields), status, ac, self.art, member_slots, thief, equipment, hits, saves,
                      skills_label=label, weapons=weapons, no_spells=no_spells, kit=kit, kit_move=kit_move,
                      move_why=", ".join(move_why), age=age)

    def _hex_base(self) -> Optional[int]:
        record = self.layout.records.get(self.hex_record.get())
        return record.addresses()[int(self.hex_slot.get()) - 1] if record else None

    def _refresh_hex(self) -> None:
        base = self._hex_base()
        if base is None:
            self.hex_data = b""
            self._set_hex_text(f"The {self.hex_record.get()} record of slot {self.hex_slot.get()} "
                               "is not located yet.\n\n"
                               "Search for the character's name above, pick the hit\n"
                               "that looks like their record, and press Assign.", [])
            return
        self.hex_start = base - self.layout.hex_before
        self.hex_data = self.guest.read(self.hex_start, self.layout.hex_before + self.layout.hex_after)
        now = time.monotonic()
        for i, b in enumerate(self.hex_data):
            addr = self.hex_start + i
            if addr in self.prev_hex and self.prev_hex[addr] != b:
                self.changed_at[addr] = now
            self.prev_hex[addr] = b

        lines, marks = [], []
        for row in range(0, len(self.hex_data), 16):
            chunk = self.hex_data[row:row + 16]
            rel = self.hex_start + row - base
            lines.append(f"{'-' if rel < 0 else '+'}{abs(rel):04x}  {self.hex_start + row:08x}  "
                         + " ".join(f"{b:02x}" for b in chunk).ljust(48) + " " + _printable(chunk))
            for i in range(len(chunk)):
                if now - self.changed_at.get(self.hex_start + row + i, -1e9) < HIGHLIGHT_SECONDS:
                    marks.append((row // 16 + 1, HEX_PREFIX + i * 3))
        self._set_hex_text("\n".join(lines), marks)

    def _set_hex_text(self, text: str, marks) -> None:
        selected = self.hex.tag_ranges("selected")
        self.hex.delete("1.0", "end")
        self.hex.insert("1.0", text)
        for line, col in marks:
            self.hex.tag_add("changed", f"{line}.{col}", f"{line}.{col + 2}")
        if selected:
            self.hex.tag_add("selected", *selected)


def run(layout: Layout, connect: Callable[[], GuestMemory], dosbox=None, game_dir: Optional[str] = None,
        connect_pid: Optional[Callable[[int], GuestMemory]] = None) -> None:
    """The Loader's window; DOSBOX, if given, is the game started for it (from GAME_DIR), whose
    closing is told in the log as if started from the window; CONNECT_PID attaches to a DOSBox by
    its pid (the one started), CONNECT to whichever runs."""
    root = tk.Tk()
    viewer = Viewer(root, layout, connect, connect_pid, dosbox)  # (its DOSBox known before it first connects)
    if dosbox is not None:
        viewer._game_dir, viewer._started = game_dir, time.time()
        viewer._start_state()
    root.mainloop()
