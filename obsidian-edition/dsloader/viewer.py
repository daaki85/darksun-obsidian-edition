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
from tkinter import filedialog, messagebox, simpledialog, ttk
from typing import Callable, Dict, List, Optional, Set, Tuple

from . import __version__, art, combatlog, dicelog, game, kits, launch, namedsaves, partyview, rings, spellbook, theme, values
from .dicelog import DiceLog, DiceLogError
from .guestmem import GuestMemory
from .layout import Layout
from .process import ProcessError

REFRESH_MS = 500
SAVES_EVERY = 3.0  # seconds between looks at the game's saves (namedsaves.py)
DICE_MS = 50
RETRY_SECONDS = 2.0
MAX_LOG_LINES = 3000
HIGHLIGHT_SECONDS = 3.0
HEX_PREFIX = 17  # width of "+0040  0012a3f0  "
MAX_HITS = 500


def _printable(data: bytes) -> str:
    return "".join(chr(b) if 32 <= b < 127 else "." for b in data)


def _query_bytes(text: str) -> bytes:
    """Search text as bytes: plain text, or "hex:" followed by hex byte values."""
    if text.lower().startswith("hex:"):
        return bytes.fromhex(text[4:])
    return text.encode("cp437", errors="replace")


# the game window's sizes (DOSBox scales the game's 320x200, with the aspect corrected)
WINDOW_CHOICES = {"Double (640x480)": 2, "Triple (960x720)": 3, "Quadruple (1280x960)": 4, "Full screen": None}

class Viewer:
    def __init__(self, root: tk.Tk, layout: Layout, connect: Callable[[], GuestMemory]):
        self.root = root
        self.layout = layout
        self.connect = connect
        self.guest: Optional[GuestMemory] = None
        self.hits: List[int] = []
        self.hex_start = 0  # guest address of the first byte in the hex view
        self.hex_data = b""
        self.prev_hex: Dict[int, int] = {}  # guest address -> last byte value
        self.changed_at: Dict[int, float] = {}  # guest address -> time it last changed
        self.ds: Optional[int] = None  # the game's data segment, once found
        self.dice: Optional[DiceLog] = None
        self.next_try = 0.0  # when to retry connecting / attaching
        self.dosbox = None  # the game, when started from here (Start the game)
        self._game_dir, self._started, self._refused = None, 0.0, []  # (for a crash report)
        # the game's portraits and font, from the player's own install (if it can be found)
        self.art = art.GameArt(launch.find_game_dir())
        self._images: List[tk.PhotoImage] = []  # Tk shows an image only while it's referenced

        root.title(f"{theme.NAME} {__version__} - {layout.game or 'party viewer'}")
        root.geometry("1320x780")
        theme.apply(root)
        root.protocol("WM_DELETE_WINDOW", self.close)
        self._build()
        self.reconnect()
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
        ttk.Button(top, text="Reconnect", command=self.reconnect).pack(side="right")
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

        tabs = ttk.Notebook(panes)
        panes.add(tabs, weight=1)
        tabs.enable_traversal()  # Ctrl+Tab between tabs, Alt + the underlined letter

        dice = ttk.Frame(tabs, padding=6)
        tabs.add(dice, text="Dice log", underline=5)
        row = ttk.Frame(dice)
        row.pack(fill="x")
        ttk.Button(row, text="Clear", command=lambda: self.dice_text.delete("1.0", "end")).pack(side="right")
        ttk.Button(row, text="Save...", command=lambda: self.save_text(self.dice_text, "dice log")).pack(
            side="right", padx=4)
        self.dice_status = tk.StringVar(value="Waiting for the game...")
        ttk.Label(row, textvariable=self.dice_status).pack(side="left", fill="x")
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
        self.dice_text.tag_configure("monster", foreground=theme.MONSTER_COLOUR, font="LedgerFixedBold")
        self._monster_names: Set[str] = set()  # every monster seen in a fight this session

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

        tools = ttk.Frame(tabs, padding=6)
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
        self.hex = tk.Text(hexframe, font="TkFixedFont", height=20, wrap="none")
        theme.style_text(self.hex)
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
        settings = launch.load_settings()
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

        note = ttk.Label(options, text="Everything here applies in games started from the Loader. A switch that "
                         "says \"from the next start\" waits until the game is started again.", wraplength=460)
        note.pack(anchor="w", pady=(0, 8))
        options.bind("<Configure>", lambda e: note.configure(wraplength=max(200, e.width - 60)), add="+")
        in_game = section("in_game", "In the game")
        # long lines wrap to the window (as with larger text) instead of running out of it
        options.bind("<Configure>", lambda e: [ttk.Style().configure(
            kind, wraplength=max(200, e.width - 60)) for kind in ("TCheckbutton", "TRadiobutton")], add="+")
        # the combat log's panel over the map in a fight (combatlog.py), at a level of its own
        self.combat_log = tk.BooleanVar(value=bool(settings.get("combat_log", True)))
        ttk.Checkbutton(in_game, text="Show a combat log in the game, bottom right, in a fight",
                        variable=self.combat_log, command=self._options_changed).pack(anchor="w")
        self.combat_log_level = tk.StringVar(value=dicelog.combat_log_level(settings))
        for value, text in ((combatlog.MINIMAL, "... at the least: what came of each attack and spell"),
                            (combatlog.SHORT, "... in short: each roll, what it needed and the damage"),
                            (combatlog.DETAIL, "... in detail, as in the log")):
            ttk.Radiobutton(in_game, text=text, value=value, variable=self.combat_log_level,
                            command=self._options_changed).pack(anchor="w", padx=(20, 0))
        # ... or in a strip below the map, the game's screen 22 rows taller (gamepatch.STRIP)
        self.combat_log_strip = tk.BooleanVar(value=settings.get("combat_log_strip", False) is True)
        ttk.Checkbutton(in_game, text="... below the map instead of over it: the round and the newest line, the game's "
                        "screen 22 rows taller (from the next start)",
                        variable=self.combat_log_strip, command=self._options_changed).pack(anchor="w", padx=(20, 0))
        # the game's Look box, on a monster in a fight: what hurts it, then all of it in a window
        self.monster_info = tk.BooleanVar(value=bool(settings.get("monster_info", True)))
        ttk.Checkbutton(in_game, text="Describe monsters when you Look at them in a fight (defences, then a window)",
                        variable=self.monster_info, command=self._options_changed).pack(anchor="w", pady=(4, 0))
        rules = section("rules", "Rule changes")
        custom = section("custom", "More character customization")
        features = section("features", "Expanded features")
        # the thief's rules and picking pockets together, as the guide's Thieves section has them
        thieves = ttk.Frame(features)
        ttk.Label(thieves, text="Improved thieving", style="Status.TLabel").pack(anchor="w")
        # the Loader's own content: people, a quest and items in the game, and the new spells. Some
        # are written into the game's files when it is started; what a save already has stays
        new = section("new_content", "New content")
        ttk.Label(new, text="People, a quest and items: from the next start, in places "
                  "not yet visited. What a saved game already has (people met, items given) stays in it. "
                  "The new spells: at once.",
                  wraplength=460).pack(anchor="w")
        options.bind("<Configure>", lambda e, label=new.winfo_children()[-1]: label.configure(
            wraplength=max(200, e.width - 60)), add="+")
        where = {"weapon_specialization": custom, "kits": custom, "level_10": custom, "cha_prices": features, "buyback": features,
                 "thief_table": thieves, "stealth": thieves, "new_spells": new}
        # one switch for each of game.RULE_SETTINGS
        self.rule_vars: Dict[str, tk.BooleanVar] = {}
        self.stealth_gear = tk.BooleanVar(value=settings.get("stealth_gear", True) is not False)
        # (in the order the README has them)
        for key, text in (
                ("class_restrictions", "Class restrictions on armour, shields and weapons, the strictest class "
                                       "winning (psionicists, multiclass thieves, preservers, druids, clerics' "
                                       "spheres); a multiclass preserver casts no spells in armour"),
                ("multiclass_hp", "Multiclass hit points as in AD&D: CON's bonus on every die (a warrior's if "
                                  "a class is a warrior), the total shared between the classes"),
                ("best_hit_die", "Hit dice rolled twice, the better kept, at creation and at every level "
                                 "(every character)"),
                ("rolled_scores", "Character creation keeps what the die rolls: a score may be raised only "
                                  "while the six add up to no more than the die gave (lower one to raise "
                                  "another; the total is shown under CHR), and the hit points can't be "
                                  "clicked; a change of CON adds or takes off its bonus"),
                ("ranger_casting_level", "Rangers' spells last and do damage as cast at the ranger level less 7, "
                                         "as the spell levels they may cast count it (the game takes the whole "
                                         "level)"),
                ("int_learning", "Preservers' INT: a chance to learn a spell from a scroll (35% at INT 9 "
                                 "to 100% at 24; a failed try uses the scroll up) and the most spells of "
                                 "each spell level they may know (6 at INT 9, all from 19)"),
                ("adnd_tables", "AD&D's class tables: the XP each class needs (a gladiator's its own, not the "
                                "fighter's), priests' THAC0 (2 better every 3 levels), and clerics', druids' and "
                                "preservers' spell slots by level (WIS's bonus slots stay the game's)"),
                ("spell_save", "Spells are saved against with the spell save (the game uses "
                               "petrification/polymorph)"),
                ("no_doubled_save", "Saves against fire, cold and electricity: DEX defensive adjustment "
                                    "instead of a doubled d20"),
                ("two_weapons", "Two weapons: -2 main hand, -4 off hand, DEX reaction adjustment added "
                                "(no better than 0; rangers and Twin-blades none in light armour); the off hand attacks once a round"),
                ("item_saves", "Items save against acid as in AD&D, by material, a plus helping, where that's "
                               "better than the game's (which destroys armour without a magical power outright)"),
                ("protection_rules", "Rings and cloaks of protection as in AD&D: only the better of two rings "
                                     "counts, a ring gives no AC with magical armour, and a cloak does nothing "
                                     "with magical or metal armour or a shield"),
                ("half_giant_hands", "Half-giants wield two-handed weapons in one hand (a shield or a light "
                                     "weapon in the other; two heavy weapons still can't be held)"),
                ("helm_ac", "Helms give AC 1 (the game's helms give none)"),
                ("weapon_specialization", "Weapon specialization: fighters and gladiators specialize (+1 to hit, +2 "
                                          "damage), fighters on to mastery at 5th level and grand mastery at 9th; "
                                          "rangers have expertise, every ranger with the bow; specialists and "
                                          "rangers shoot missiles faster; other weapons at a warrior's plain rate "
                                          "(chosen on the creation panel's WEAPON SPEC pages)"),
                ("kits", "Kits: a character of one class may take one of its class's three kits, each "
                         "giving something and costing something (chosen on the creation panel's KIT "
                         "page)"),
                ("level_10", "Class levels go up to 10 (the game stops at 9; no spells past 5th level are needed)"),
                ("cha_prices", "The leader's CHA lowers what shops ask: 5% off at CHA 18 and 5% more for each "
                               "point after, to 40% at 25; shops pay 60% of an item's price"),
                ("buyback", "Merchants keep the magical items the party sells them, to buy back at their price "
                            "(the game destroys whatever is sold; other items still are)"),
                ("thief_table", "Thief skills from AD&D's table by level, with Dark Sun's race and DEX adjustments "
                                "(the game adds 4 a level to a base of its own, and DEX by a formula)"),
                ("stealth", "Thieves hide in shadows and move silently to backstab, rangers to attack from behind "
                            "(no enemy beside them; thieves half the chance in daylight, rangers indoors)"),
                ("new_spells", "New wizard spells: Cat's Grace (2nd level: DEX + 1d6), and at 1st level Erdlu Claw "
                               "(unarmed 1d6+1), Fogbolt (-3 to hit, AC 2 worse), Reflected Image, Spook and Friends")):
            self.rule_vars[key] = tk.BooleanVar(
                value=bool(settings.get(key, settings.get(game.OLD_SETTING_NAMES.get(key, key), True))))
            parent = where.get(key, rules)
            ttk.Checkbutton(parent, text=text, variable=self.rule_vars[key],
                            command=self._options_changed).pack(anchor="w", pady=(4 if parent.winfo_children()[:-1] else 0, 0))
            if key == "stealth":  # (under it: what worn gear adds)
                ttk.Checkbutton(thieves, text="... a worn cloak adds 10 to hiding, worn boots 10 to moving silently; "
                                            "a worn belt adds 5 to picking pockets and opening locks (hiding or not)",
                                variable=self.stealth_gear, command=self._options_changed).pack(anchor="w", padx=(20, 0))

        self.roll_store = tk.BooleanVar(value=settings.get("roll_store", True) is not False)
        ttk.Checkbutton(custom, text="STORE and RECALL on the creation screen: keep a roll, try the die again, "
                        "and bring the kept roll back (from the next start)", variable=self.roll_store,
                        command=self._options_changed).pack(anchor="w", pady=(4, 0))
        self.starting_gear = tk.BooleanVar(value=bool(settings.get("starting_gear", True)))
        ttk.Checkbutton(custom, text="Fuller starting gear: new characters (and the game's own party) also get a weapon in hand they can use, "
                        "a sling, leather armour where they may wear it, a belt, boots and a dagger (rangers "
                        "and Stalkers a cloak); a multiclass preserver's armour goes in the backpack",
                        variable=self.starting_gear, command=self._options_changed).pack(anchor="w", pady=(4, 0))

        self.content_vars: Dict[str, tk.BooleanVar] = {}
        for key, text in (
                ("kalzith", "Kalzith, a defiler slave in the slave pens who sells arcane scrolls (new games)"),
                ("semyon", "Semyon in the slave pens after he leaves the arena, and breaking out with Scar"),
                ("vulture", "The cooked vulture: Dinos cooks it for the party (XP and a full rest)"),
                ("defiler_scrolls", "Defilers' scrolls: a defiler in a fight carries a scroll of a random "
                                    "preserver spell one time in 20, dropped where it dies"),
                (launch.NEW_ITEMS, "New items, magical and mundane: weapons, armour and other gear the game "
                                   "lacks or never placed, on its people, in its shops and chests (the guide's "
                                   "New items lists them)")):
            self.content_vars[key] = tk.BooleanVar(value=settings.get(key, True) is not False)
            ttk.Checkbutton(new, text=text, variable=self.content_vars[key],
                            command=self._options_changed).pack(anchor="w", pady=(4, 0))
        self.pickpockets = tk.BooleanVar(value=bool(settings.get("pickpockets", True)))
        ttk.Checkbutton(thieves, text="Picking pockets: a thief uses Thieves' Tools on someone in sight (each "
                        "thief gets a set), until caught", variable=self.pickpockets,
                        command=self._options_changed).pack(anchor="w", pady=(4, 0))
        thieves.pack(anchor="w", fill="x", pady=(8, 0))

        # how the game looks
        looks = section("on_screen", "Graphics")
        self.elf_looks = tk.BooleanVar(value=settings.get("elf_looks", True) is not False)
        ttk.Checkbutton(looks, text="Elves have pointed ears, and half-elves figures of their own instead of the "
                        "humans' (from the next start)",
                        variable=self.elf_looks, command=self._options_changed).pack(anchor="w")
        self.cilla_elf = tk.BooleanVar(value=settings.get("cilla_elf", True) is not False)
        ttk.Checkbutton(looks, text="Cilla, an elf in the game's own party, drawn as an elf (the game gives her "
                        "the half-elf woman's figure; from the next start)", variable=self.cilla_elf,
                        command=self._options_changed).pack(anchor="w", pady=(4, 0))
        self.show_gear = tk.BooleanVar(value=bool(settings.get("show_gear", True)))
        ttk.Checkbutton(looks, text="Show what the party wears on their figures (weapons, armour, helms, "
                        "cloaks, boots, belts)", variable=self.show_gear,
                        command=self._options_changed).pack(anchor="w", pady=(4, 0))
        self.show_shadows = tk.BooleanVar(value=bool(settings.get("shadows", True)))
        ttk.Checkbutton(looks, text="Shadows under the figures (see-through, on the floor)",
                        variable=self.show_shadows, command=self._options_changed).pack(anchor="w", pady=(4, 0))
        self.show_dust = tk.BooleanVar(value=bool(settings.get("dust", True)))
        ttk.Checkbutton(looks, text="Dust raised behind the feet of anyone walking on sand or dirt",
                        variable=self.show_dust, command=self._options_changed).pack(anchor="w", pady=(4, 0))

        # the mouse and keys in the game
        controls = section("controls", "Controls")
        self.use_targeting = tk.BooleanVar(value=bool(settings.get("targeting", True)))
        ttk.Checkbutton(controls, text="In a fight, Tab (Shift+Tab back) chooses an enemy, its ring brighter, and "
                        "Enter attacks it, even behind someone", variable=self.use_targeting,
                        command=self._options_changed).pack(anchor="w")
        self.ring_mode = tk.StringVar(value=rings.mode(settings))
        ttk.Label(controls, text="Red rings on the ground in a fight:").pack(anchor="w", pady=(4, 0))
        for value, text in ((rings.OFF, "... none"),
                            (rings.ONLY_CHOSEN, "... under the enemy chosen with Tab"),
                            (rings.ALL, "... under all the enemies (the chosen one's redder)")):
            ttk.Radiobutton(controls, text=text, value=value, variable=self.ring_mode,
                            command=self._options_changed).pack(anchor="w", padx=(20, 0))
        self.scroll_map = tk.BooleanVar(value=bool(settings.get("scroll_map", True)))
        ttk.Checkbutton(controls, text="Scroll the map by pressing the mouse wheel and moving", variable=self.scroll_map,
                        command=self._options_changed).pack(anchor="w", pady=(4, 0))
        self.scroll_right = tk.BooleanVar(value=bool(settings.get("scroll_right", False)))
        ttk.Checkbutton(controls, text="... or by holding the right mouse button and moving (a right "
                        "click still changes the pointer)", variable=self.scroll_right,
                        command=self._options_changed).pack(anchor="w", padx=(20, 0))
        self.effects_kept = tk.BooleanVar(value=settings.get("effects_kept", True) is not False)
        ttk.Checkbutton(controls, text="A click on a spell's icon on the Effects screen leaves it on (the game "
                        "ends it; psionic powers can still be stopped); from the next start",
                        variable=self.effects_kept, command=self._options_changed).pack(anchor="w", pady=(4, 0))

        # the game's speed (DOSBox's CPU)
        pace = section("speed", "Game speed (from the next start)")
        speed = settings.get("cycles", launch.DEFAULT_SPEED)
        speed = launch.SPEEDS[-1] if speed == launch.FASTEST_BEFORE else speed
        self.game_speed = tk.StringVar(value=str(speed if speed in launch.SPEEDS or speed == launch.GOG_SPEED
                                                 else launch.DEFAULT_SPEED))
        for value, text in ((launch.GOG_SPEED, "GOG's own (walking can be choppy with shadows and dust)"),
                            ("20000", "Faster: smooth walking with shadows and dust (the default)"),
                            ("35000", "Fastest: the whole party in view walks as fast as the leader alone "
                                      "(needs a faster PC)")):
            ttk.Radiobutton(pace, text=text, value=value, variable=self.game_speed,
                            command=self._speed_chosen).pack(anchor="w")
        # the saves, a second time under their names in the game (namedsaves.py)
        kept = section("saves", "Saves")
        about = ttk.Label(kept, text="Every save is copied, as the game writes it, into the Loader's \"Named "
                          "saves\" folder under the name it has in the game (\"Page 2 slot 05 - Before Scar's "
                          "battle.SAV\").", style="Status.TLabel", wraplength=460, justify="left")
        about.pack(anchor="w")
        kept.bind("<Configure>", lambda e: about.configure(wraplength=max(200, e.width - 20)), add="+")
        buttons = ttk.Frame(kept)
        buttons.pack(anchor="w", pady=(4, 0))
        ttk.Button(buttons, text="Open the folder", command=self.open_named_saves).pack(side="left")
        ttk.Button(buttons, text="Put a save in a slot...", command=self.restore_save).pack(side="left", padx=(8, 0))
        ttk.Button(options, text="Restore defaults", command=self.restore_defaults).pack(anchor="w", pady=(12, 0))

    def _saves_game_dir(self) -> Optional[str]:
        game_dir = self._game_dir or launch.find_game_dir()
        if game_dir is None:
            messagebox.showinfo("Saves", "The Loader hasn't found the game yet: start it once from the Loader.",
                                parent=self.root)
        return game_dir

    def open_named_saves(self) -> None:
        game_dir = self._saves_game_dir()
        if game_dir is None:
            return
        namedsaves.sync(game_dir)
        os.makedirs(namedsaves.NAMED, exist_ok=True)
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
        os.makedirs(namedsaves.NAMED, exist_ok=True)
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
                "(Its named copy stays in the folder.)", parent=self.root):
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
        for var in (self.monster_info, self.stealth_gear, self.pickpockets, self.roll_store, self.elf_looks, self.cilla_elf,
                    self.starting_gear, self.show_gear, self.show_shadows, self.show_dust, self.use_targeting,
                    self.scroll_map, self.effects_kept):
            var.set(True)
        for var in (self.scroll_right, self.combat_log):
            var.set(False)
        self.combat_log_level.set(dicelog.combat_log_level({}))
        self.combat_log_strip.set(False)
        self.ring_mode.set(rings.mode({}))
        self.game_speed.set(str(launch.DEFAULT_SPEED))
        self._options_changed()
        self._speed_chosen()
        self.status.set("Options set back to their defaults (those that wait for the next start, from then).")

    def _sections_changed(self) -> None:
        """Remember which of the Options tab's sections are open."""
        settings = launch.load_settings()
        settings["options_open"] = [key for key, part in self.sections.items() if part.is_open]
        launch.save_settings(settings)

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

    def _fit_party(self) -> None:
        """Columns wide enough for the text size, and the divider moved to fit them."""
        field, slot = round(150 * theme.scale()), round(118 * theme.scale())
        self.table.column("field", width=field, minwidth=field, stretch=False)
        for i in range(self.layout.count):
            self.table.column(f"slot{i}", width=slot, minwidth=slot)
        # at large text sizes the table scrolls sideways rather than squeezing the logs
        wanted = field + slot * self.layout.count + 24
        width = self.panes.winfo_width()
        if width < 200:  # not laid out yet (a slow start): placing the divider now would hide the party
            self.root.after(200, self._fit_party)
            return
        place = min(wanted, int(width * 0.55))
        if self.panes.sashpos(0, place) < place // 2:  # the panes weren't ready after all: again soon
            self.root.after(200, self._fit_party)

    def save_text(self, widget: tk.Text, what: str) -> None:
        """Save a log as a text file (to read with other tools, such as a screen reader)."""
        path = filedialog.asksaveasfilename(title=f"Save the {what}", defaultextension=".txt",
                                            initialfile=f"{what.replace(' ', '-')}.txt",
                                            filetypes=[("Text", "*.txt"), ("All files", "*.*")])
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(widget.get("1.0", "end-1c"))

    def _drop_dice(self) -> None:
        if self.dice is not None:
            self.dice.close()
        self.dice = None

    def reconnect(self, quiet: bool = False) -> None:
        self.ds = None
        self._drop_dice()
        try:
            self.guest = self.connect()
        except Exception as e:  # shown to the user, who can fix it and retry
            self.guest = None
            if not quiet or not self.status.get().startswith("Not connected"):
                self.status.set(f"Not connected: {e}")
            self.next_try = time.monotonic() + RETRY_SECONDS
            return
        self.status.set(f"Connected to DOSBox pid {self.guest.proc.pid}, "
                        f"guest RAM {self.guest.size // (1024 * 1024)} MB at host {self.guest.base:#x}")

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
                messagebox.showerror("Start the game", f"{game_dir} has no DSUN.EXE and DOSBOX folder; "
                                     "pick the GOG install folder of Shattered Lands.")
                return
            launch.save_settings(dict(launch.load_settings(), game_dir=game_dir))
            self.art = art.GameArt(game_dir)
        try:
            self._game_dir, self._started = game_dir, time.time()
            self.dosbox, problem = launch.launch(game_dir)
        except (launch.LaunchError, OSError) as e:
            messagebox.showerror("Start the game", str(e))
            return
        if problem:
            self.status.set(f"Starting the game without the dice log: it can't run with this copy ({problem}).")
        else:
            self.status.set(f"Starting Shattered Lands from {game_dir}...")
        self.next_try = time.monotonic() + RETRY_SECONDS
        self._start_state()

    def _dosbox_closed(self) -> None:
        """DOSBox started from here has closed: say how, in the log (an exit code a crash of
        DOSBox's own gives, such as C0000005h on Windows, is told apart from the game ending)."""
        if self.dosbox is None or self.dosbox.poll() is None:
            return
        code, self.dosbox = self.dosbox.returncode, None
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
        text = launch.crash_report(code, note, launch.load_settings(), self.dice_text.get("1.0", "end"),
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
            messagebox.showerror("Layout", f"Could not load {self.layout.path}:\n{e}")
            return
        self._apply_layout()

    def save_layout(self) -> None:
        self.layout.save()
        messagebox.showinfo("Layout", f"Saved slots to {self.layout.path}")

    def search_name(self) -> None:
        text = self.search_text.get().strip()
        if not text or not self.guest:
            return
        try:
            pattern = _query_bytes(text)
        except ValueError:
            messagebox.showerror("Search", "After hex: give byte values like 14 16 12")
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
        if not sel or sel[0] >= len(self.hits):
            messagebox.showinfo("Assign", "Select a search hit first.")
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
            messagebox.showerror("Stride", f"Not a number: {text}")
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
        self.guest = None
        self._drop_dice()
        self.ds = None
        self.status.set(f"Disconnected ({err}). Waiting for DOSBox...")
        self.dice_status.set("Waiting for the game...")
        self.next_try = time.monotonic() + RETRY_SECONDS

    def close(self) -> None:
        """Put the game's rand() back before closing, so the game keeps working."""
        try:
            if self.dice:
                self.dice.detach()
                self.dice.close()
        except Exception:
            pass
        self.root.destroy()

    def _tick(self) -> None:
        if not self.guest and time.monotonic() >= self.next_try:
            self.reconnect(quiet=True)
        self._start_state()
        if self.guest:
            try:
                self._auto_locate()
                self._refresh_table()
                self._refresh_hex()
            except ProcessError as e:
                self._disconnected(e)
        self._sync_saves()
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
                self.status.set("Save copied: " + ", ".join(made))

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
        self._dosbox_closed()
        try:
            self._dice_step()
        except ProcessError as e:
            self._disconnected(e)
        self.root.after(DICE_MS, self._dice_tick)

    def _dice_step(self) -> None:
        if not self.guest:
            return
        now = time.monotonic()
        if self.dice is None or not self.dice.attached:
            if now < self.next_try:
                return
            self.next_try = now + RETRY_SECONDS
            if self.dice is None:
                self.dice = DiceLog(self.guest)
                self.dice.speaker_names = launch.speaker_names()
                self.dice.learned_speakers = launch.learned_speakers()
                self.dice.monster_info = self.monster_info.get()
                self.dice.arena_ring = self.content_vars[launch.NEW_ITEMS].get()
                self.dice.pickpockets = self.pickpockets.get()
                self.dice.show_gear = self.show_gear.get()
                self.dice.starting_gear = self.starting_gear.get()
                self.dice.show_shadows = self.show_shadows.get()
                self.dice.combat_log = self.combat_log.get()
                self.dice.combat_log_level = self.combat_log_level.get()
                self.dice.game_dir = launch.find_game_dir()
                self.dice.show_dust = self.show_dust.get()
                self.dice.elf_looks = self.elf_looks.get()
                self.dice.cilla_elf = self.cilla_elf.get()
                self.dice.ring_mode = self.ring_mode.get()
                self.dice.use_targeting = self.use_targeting.get()
                self.dice.scroll_map = self.scroll_map.get()
                self.dice.scroll_right = self.scroll_right.get()
                self.dice.vulture_on = self.content_vars["vulture"].get()
                self.dice.defiler_scrolls = self.content_vars["defiler_scrolls"].get()
                self.dice.stealth_gear = self.stealth_gear.get()
                self.dice.load_picked(launch.pickpocketed())
                self.dice.tools_given = launch.tools_given()
                self.dice.set_rules(self._rules())
            try:
                self.dice_status.set(self.dice.attach())
            except DiceLogError as e:
                self.dice_status.set(str(e))
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
        picked = self.dice.take_picked()
        if picked is not None:
            launch.set_pickpocketed(picked)
        given = self.dice.take_tools_given()
        if given:
            launch.add_tools_given(given)
        learned = self.dice.take_speakers()
        if learned:  # names worked out from conversations: keep them, and show them on earlier lines
            launch.add_learned_speakers(learned)
            for portrait in learned:
                self._rename_portrait(portrait)
        talk = self.dice.take_dialogue()
        if talk:
            self._append_dialogue(talk)

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
        settings = launch.load_settings()
        if scale is None:
            settings["fullscreen"] = True
        else:
            settings["fullscreen"] = False
            settings["window_scale"] = scale
        launch.save_settings(settings)
        self.status.set(f"Game window: {self.window_choice.get()}, from the next time you start the game "
                        "(Alt+Enter switches full screen while playing).")

    def _speed_chosen(self) -> None:
        """Remember the game's speed; it applies the next time the game is started."""
        value = self.game_speed.get()
        settings = launch.load_settings()
        settings["cycles"] = value if value == launch.GOG_SPEED else int(value)
        launch.save_settings(settings)
        self.status.set("Game speed: from the next time you start the game.")

    def _options_changed(self) -> None:
        """A switch on the Options tab changed: all of them saved, and the log told."""
        settings = launch.load_settings()
        for old in ("turn_popups", "turn_popups_level", "turn_popups_detail"):  # (the turn pop-up, gone)
            settings.pop(old, None)
        settings["monster_info"] = self.monster_info.get()
        settings["combat_log"] = self.combat_log.get()
        settings["combat_log_level"] = self.combat_log_level.get()
        settings["combat_log_strip"] = self.combat_log_strip.get()
        settings["pickpockets"] = self.pickpockets.get()
        settings["show_gear"] = self.show_gear.get()
        settings["starting_gear"] = self.starting_gear.get()
        settings["shadows"] = self.show_shadows.get()
        settings["dust"] = self.show_dust.get()
        settings["elf_looks"] = self.elf_looks.get()
        settings["cilla_elf"] = self.cilla_elf.get()
        settings["rings"] = self.ring_mode.get()
        settings["targeting"] = self.use_targeting.get()
        settings["scroll_map"] = self.scroll_map.get()
        settings["scroll_right"] = self.scroll_right.get()
        for key, var in self.content_vars.items():
            settings[key] = var.get()
        settings["effects_kept"] = self.effects_kept.get()
        settings["stealth_gear"] = self.stealth_gear.get()
        settings["roll_store"] = self.roll_store.get()
        for key, var in self.rule_vars.items():
            settings[key] = var.get()
        launch.save_settings(settings)
        if self.dice is not None:
            self.dice.set_monster_info(self.monster_info.get())
            self.dice.arena_ring = self.content_vars[launch.NEW_ITEMS].get()
            self.dice.set_pickpockets(self.pickpockets.get())
            self.dice.show_gear = self.show_gear.get()
            self.dice.starting_gear = self.starting_gear.get()
            self.dice.show_shadows = self.show_shadows.get()
            self.dice.show_dust = self.show_dust.get()
            self.dice.combat_log = self.combat_log.get()
            self.dice.combat_log_level = self.combat_log_level.get()
            self.dice.ring_mode = self.ring_mode.get()
            self.dice.use_targeting = self.use_targeting.get()
            self.dice.scroll_map = self.scroll_map.get()
            self.dice.scroll_right = self.scroll_right.get()
            self.dice.vulture_on = self.content_vars["vulture"].get()
            self.dice.defiler_scrolls = self.content_vars["defiler_scrolls"].get()
            self.dice.stealth_gear = self.stealth_gear.get()
            self.dice.cilla_elf = self.cilla_elf.get()
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
        launch.set_speaker_name(portrait, name)
        if name:
            self.dice.speaker_names[portrait] = name
        else:
            self.dice.speaker_names.pop(portrait, None)
        self._rename_portrait(portrait)

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
                image = art.photo(self.root, face, max(2, round(2 * theme.scale())), background=theme.DEEP)
                self._images.append(image)
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
        if self._following.get(self.talk_text, True):
            self.talk_text.see("end")

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

    def _append_dice(self, lines: List[str]) -> None:
        names = self._log_names() if lines else []
        for line in lines:
            tag = combatlog.line_kind(line)
            self.dice_text.insert("end", line + "\n", tag)
            self._colour_names(line, names)
        excess = int(self.dice_text.index("end-1c").split(".")[0]) - MAX_LOG_LINES
        if excess > 0:
            self.dice_text.delete("1.0", f"{excess + 1}.0")
        if self._following.get(self.dice_text, True):
            self.dice_text.see("end")

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
                hits.append(", ".join(f"{h.thac0} {h.name}" for h in gd.weapon_hits(index)) if known else "")
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
                items = gd.equipment((addr - table) // game.CREATURE_SIZE) if addr is not None else []
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
            if known and not thief and self.rule_vars["stealth"].get():  # a ranger's, for the stealth rule
                thief, label = gd.ranger_skills_now(index), "Ranger skills now"
            equipment = gd.equipment(index) if known else []
            try:
                hits = gd.weapon_hits(index) if known and index < game.PARTY_SIZE else []
                saves = gd.saves_now(index) if known and index < game.PARTY_SIZE else []
            except (struct.error, IndexError, ValueError):
                hits, saves = [], []
            try:
                weapons = gd.specializations(index) if known and index < game.PARTY_SIZE else []
                no_spells = bool(known and index < game.PARTY_SIZE and gd.no_spells(index))
                kit = gd.kit(index) if known and index < game.PARTY_SIZE else None
                kit_move = sum(kits.move(k) for k in gd.kit_ids(index)) if kit else 0
            except (struct.error, IndexError, ValueError):
                weapons, no_spells, kit, kit_move = [], False, None, 0
            card.show(name, dict(fields), status, ac, self.art, member_slots, thief, equipment, hits, saves,
                      skills_label=label, weapons=weapons, no_spells=no_spells, kit=kit, kit_move=kit_move)

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


def run(layout: Layout, connect: Callable[[], GuestMemory], dosbox=None, game_dir: Optional[str] = None) -> None:
    """The Loader's window; DOSBOX, if given, is the game started for it (from GAME_DIR), whose
    closing is told in the log as if started from the window."""
    root = tk.Tk()
    viewer = Viewer(root, layout, connect)
    if dosbox is not None:
        viewer.dosbox, viewer._game_dir, viewer._started = dosbox, game_dir, time.time()
        viewer._start_state()
    root.mainloop()
