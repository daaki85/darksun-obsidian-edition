"""The party as the game's own View Character screen shows it: a card for each character.

Each card has the character's figure (the creation screen's picture for their
race and sex, from the installed game), name, HP and PSP as "54/54" (PSP in
blue, as in the game), their condition, and then the character sheet: scores,
race, sex and alignment, classes and levels, experience, AC, THAC0, movement
and attacks. All of it is ordinary text in the window's fonts, so it grows with
the text size.
"""

import re
import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Optional, Tuple

from . import art, game, theme

SCORES = ("STR", "DEX", "CON", "INT", "WIS", "CHA")
_NUMBER = re.compile(r"\s*\((-?\d+)\)$")


def plain(display: str) -> str:
    """ "Half-giant (5)" -> "Half-giant"."""
    return _NUMBER.sub("", display)


def number(display: str) -> Optional[int]:
    """ "Half-giant (5)" -> 5; "12" -> 12."""
    m = _NUMBER.search(display)
    if m:
        return int(m.group(1))
    try:
        return int(display)
    except ValueError:
        return None


def classes_text(fields: Dict[str, str]) -> str:
    """ "Fighter 2 / Druid 2 / Psionicist 2", from the Class and Level fields."""
    parts = []
    for i in (1, 2, 3):
        cls, level = fields.get(f"Class {i}", ""), fields.get(f"Level {i}", "")
        if cls and number(cls) not in (None, 0):
            parts.append(f"{plain(cls)} {level}".strip())
    return " / ".join(parts)


class Card(ttk.Frame):
    """One character, laid out like the game's View Character screen."""

    def __init__(self, parent, index: int):
        super().__init__(parent, style="Card.TFrame", padding=8)
        self.index = index
        self.figure_key: Optional[Tuple[int, int]] = None
        self.image: Optional[tk.PhotoImage] = None
        self.vars: Dict[str, tk.StringVar] = {}

        self.figure = ttk.Label(self, style="Card.TLabel", anchor="n")
        self.figure.grid(row=0, column=0, rowspan=4, sticky="n", padx=(0, 10))
        self._label("name", 0, 1, "CardName.TLabel")
        self._label("hp", 1, 1, "CardStat.TLabel")
        self._label("psp", 2, 1, "CardPsp.TLabel")
        self._label("status", 3, 1, "CardStatus.TLabel", wrap=True)

        sheet = ttk.Frame(self, style="CardBody.TFrame")
        sheet.grid(row=4, column=0, columnspan=2, sticky="we", pady=(8, 0))
        for i, score in enumerate(SCORES):
            ttk.Label(sheet, text=f"{score}:", style="Card.TLabel").grid(row=i, column=0, sticky="w")
            var = self.vars[score] = tk.StringVar()
            ttk.Label(sheet, textvariable=var, style="CardStat.TLabel").grid(row=i, column=1, sticky="w",
                                                                           padx=(4, 16))
        right = ("who", "alignment", "age", "classes", "kit", "xp", "ac", "thac0", "saves", "move", "attacks", "weapons",
                 "equipment", "slots", "thief")
        labels = []
        self.rows: Dict[str, ttk.Label] = {}  # (an empty one is hidden, leaving no blank line)
        for row, key in enumerate(right):
            var = self.vars[key] = tk.StringVar()
            label = ttk.Label(sheet, textvariable=var, style="Card.TLabel")
            label.grid(row=row, column=2, sticky="nw")
            labels.append(label)
            self.rows[key] = label
        # long lines (three classes) wrap at the card's edge rather than being cut off
        sheet.bind("<Configure>", lambda e: [l.configure(wraplength=max(e.width - l.winfo_x() - 6, 80))
                                             for l in labels])
        sheet.columnconfigure(2, weight=1)
        self.columnconfigure(1, weight=1)

    def _label(self, key: str, row: int, column: int, style: str, wrap: bool = False) -> None:
        var = self.vars[key] = tk.StringVar()
        label = ttk.Label(self, textvariable=var, style=style)
        label.grid(row=row, column=column, sticky="nw")
        if wrap:
            label.bind("<Configure>", lambda e: label.configure(wraplength=max(e.width, 120)))

    def show(self, name: str, fields: Dict[str, str], status: str, current_ac: Optional[int],
             game_art: Optional["art.GameArt"], slots=(), thief=(), equipment=(), hits=(), saves=(), skills_label: str = "Thief skills now",
             weapons=(), no_spells: bool = False, kit: Optional[str] = None, kit_move: int = 0,
             move_why: str = "", age: Optional[str] = None) -> None:
        """`slots`: [(kind, [(spell level, left, most), ...]), ...], as GameData.spell_slots gives;
        `thief`: [(skill, percent), ...], as GameData.thief_skills gives; `hits` and `saves`,
        THAC0 with each weapon and the saves as they stand now (GameData.weapon_hits, saves_now);
        `weapons`, the kinds chosen with weapon specialization (GameData.specializations);
        `no_spells`, a multiclass preserver in armour (GameData.no_spells); `kit`, the kit taken
        (GameData.kit), and what it adds to Move in a fight (kits.move); `age`, aging.describe's."""
        get = fields.get
        self.vars["name"].set(name.upper() if name else f"SLOT {self.index + 1}")
        pair = lambda cur, top: f"{get(cur, '')}/{get(top, '')}" if get(cur) else ""
        self.vars["hp"].set(f"HP: {pair('HP', 'Max HP')}")
        self.vars["psp"].set(f"PSP: {pair('PSP', 'Max PSP')}")
        self.vars["status"].set(status)
        for score in SCORES:
            self.vars[score].set(get(score, ""))
        sex, race = plain(get("Gender", "")), plain(get("Race", ""))
        self.vars["who"].set(f"{sex} {race}".strip())
        self.vars["alignment"].set(plain(get("Alignment", "")))
        self.vars["age"].set(f"Age: {age}" if age else "")
        self.vars["classes"].set(classes_text(fields))
        self.vars["kit"].set(f"Kit: {kit}" if kit else "")
        self.vars["xp"].set(f"EXP: {get('XP', '')}")
        base = get("Base AC", "")
        self.vars["ac"].set(f"AC: {current_ac}" + (f" (base {base})" if base else "")
                            if current_ac is not None else f"AC: {base} (base; no fight yet)")
        base = get("THAC0", "")
        if hits:
            each = ", ".join(f"{h.thac0} with {h.name}" for h in hits)
            self.vars["thac0"].set(f"THAC0: {each}" + (f" (base {base})" if base else ""))
        else:
            self.vars["thac0"].set(f"THAC0: {base}")
        self.vars["saves"].set(("Saves (d20 needed now): " + ", ".join(
            f"{short} {s.needs}" for short, s in zip(game.SAVE_SHORT, saves))) if len(saves) == 5 else "")
        move = get("Move", "")
        why = move_why or kit
        fight = number(move) + kit_move if kit_move and why and number(move) is not None else None
        self.vars["move"].set(f"Move: {move}" + (f" ({fight} in a fight: {why})" if fight else ""))
        self.vars["attacks"].set(attacks_text(get("Attacks/round", ""), hits))
        self.vars["weapons"].set(("Weapons: " + ", ".join(f"{kind} ({skill})" for kind, skill in weapons))
                                 if weapons else "")
        self.vars["equipment"].set("\n".join(f"{slot.capitalize() if slot else 'Carried'}: {item}"
                                              for slot, item in equipment))
        self.vars["thief"].set((f"{skills_label}: " + ", ".join(f"{name} {n}%" for name, n in thief))
                               if thief else "")
        self.vars["slots"].set("\n".join(f"{kind} spells left: {game.slots_text(levels)}"
                                         + (" (no spells in armour)" if no_spells else "") for kind, levels in slots))
        for row, label in self.rows.items():
            label.grid() if self.vars[row].get() else label.grid_remove()
        key = (number(get("Race", "")) or 0, number(get("Gender", "")) or 0)
        zoom = 2 if theme.scale() >= 1.6 else 1
        if game_art and (key, zoom) != self.figure_key:
            self.figure_key = (key, zoom)
            pixels = game_art.figure(*key)
            self.image = art.photo(self, pixels, zoom, background=theme.DEEP) if pixels else None
            self.figure.configure(image=self.image or "")


def halves_text(halves: int) -> str:
    return str(halves // 2) if halves % 2 == 0 else f"{halves}/2"


def attacks_text(shown: str, hits) -> str:
    """The attacks line: the game's attacks a round, or, with weapon specialization, each ready
    weapon's where they differ (specialize.attacks)."""
    from . import specialize
    whole, _, half = shown.partition("/")
    try:
        halves = int(whole) if half else int(whole) * 2
    except ValueError:
        return f"Attacks: {shown} a round"
    each = [(h.name, h.halves if h.halves is not None else specialize.attacks(halves, h.skill)) for h in hits
            if (h.skill or h.halves is not None) and h.item >= 0]
    if not each or all(n == halves for _, n in each):
        return f"Attacks: {shown} a round"
    return "Attacks: " + ", ".join(f"{halves_text(n)} a round with {name}" if i == 0 else f"{halves_text(n)} with {name}"
                                   for i, (name, n) in enumerate(each))


class PartyCards(theme.ScrollArea):
    """Four cards, two by two like the game's party screen, scrolling when the text is large."""

    def __init__(self, parent, count: int):
        super().__init__(parent)
        self.cards: List[Card] = []
        for i in range(count):
            card = Card(self.inner, i)
            card.grid(row=i // 2, column=i % 2, sticky="nsew", padx=4, pady=4)
            self.cards.append(card)
        for c in (0, 1):
            self.inner.columnconfigure(c, weight=1, uniform="card")
