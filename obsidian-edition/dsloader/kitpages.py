"""Kits: the creation panel's KIT page (DSCLOG's KIT_* routines) and the kits' names.

A character of one class may take one of its class's three kits, or none (the class as it is).
The kit is the sheet's byte KIT_BYTE: 0 none, 1 to 3 the class's kits in KITS's order. A
character of two classes at once (not a human) may take a kit of its race and pair of classes, if
they have any (MULTI: a group numbered on from the classes, 9-19, its kits in KITS as a class's),
in KIT_BYTE the same way. It is
chosen on the creation panel, on a page of its own (a window for each class, its rows the
NO KIT and the class's kits, its button VIEW PSIONICS back to the disciplines), which KITS opens:
the button of the disciplines' window for a class with no sphere, of the spheres' for a
cleric, druid or ranger, of the last weapon page for a warrior choosing weapons. The rows'
pictures are carved as the weapon pages' are (weaponpages.py), names too long for the panel
shortened as the game shortens its own (P-KINESIS).
"""

from typing import Dict, List, Optional, Sequence, Tuple

from . import gff, specialize
from . import weaponpages as wp

KIT_BYTE = 0x43
# By class as the creation screen numbers them (game.CREATION_CLASS_NAMES): the kits' names
KITS = {1: ("Elementalist", "Healer", "Crusader"),
        2: ("Grove Warden", "Lifebinder", "Wanderer"),
        3: ("Myrmidon", "Sentinel", "Ravager"),
        4: ("Arena Champion", "Twin-blade", "Brute"),
        5: ("Scholar", "Battle Mage", "Arcanist"),
        6: ("Mind Bender", "Mind Warrior", "Kineticist"),
        7: ("Stalker", "Justifier", "Seeker"),
        8: ("Swashbuckler", "Assassin", "Shinobi"),
        9: ("Battle Dancer",), 10: ("Shadowblade", "Military Scout"), 11: ("Wilderness Avenger",),
        12: ("Rescuer",), 13: ("Ghetto Fighter", "Wayfinder"), 14: ("Spellarcher",), 15: ("Titan Mind",),
        16: ("Poisoner",), 17: ("Spirit Caller",), 18: ("Wasteland Seer",), 19: ("Wild Fury",)}
# the multiclass kits' groups: (race, the pair of classes as the creation screen numbers them)
ELF, HALF_ELF, DWARF, HALF_GIANT, HALFLING, MUL, THRI_KREEN = 3, 4, 2, 5, 6, 7, 8
MULTI = {9: (ELF, frozenset((1, 3))),  # elf cleric/fighter
         10: (HALF_ELF, frozenset((3, 8))),  # half-elf fighter/thief
         11: (HALF_ELF, frozenset((2, 3))),  # half-elf druid/fighter
         12: (HALF_ELF, frozenset((1, 7))),  # half-elf cleric/ranger
         13: (DWARF, frozenset((3, 8))),  # dwarf fighter/thief
         14: (HALF_ELF, frozenset((3, 5))),  # half-elf fighter/preserver
         15: (HALF_GIANT, frozenset((3, 6))),  # half-giant fighter/psionicist
         16: (HALFLING, frozenset((3, 8))),  # halfling fighter/thief
         17: (HALFLING, frozenset((1, 6))),  # halfling cleric/psionicist
         18: (THRI_KREEN, frozenset((2, 3))),  # thri-kreen druid/fighter
         19: (MUL, frozenset((2, 3)))}  # mul druid/fighter
# the rows' text where the name is too long for the panel
SHORT = {"Arena Champion": "CHAMPION", "Swashbuckler": "SWASHBUCK", "Elementalist": "ELEMENTAL",
         "Grove Warden": "WARDEN", "Battle Mage": "BATTLMAGE", "Mind Bender": "M-BENDER", "Mind Warrior": "M-WARRIOR",
         "Battle Dancer": "B-DANCER", "Shadowblade": "SHADOWBLD", "Military Scout": "M-SCOUT",
         "Wilderness Avenger": "W-AVENGER", "Ghetto Fighter": "G-FIGHTER",
         "Spellarcher": "SPELLARCH", "Spirit Caller": "S-CALLER", "Wasteland Seer": "WASTE SEER"}
# the widest a row's picture may be, its mark's room in: the panel's frame comes in to about 95
# pixels past the rows' left at the second kit's row, and a few more are kept clear of it
ROW_WIDTH = 88
# a sheet's class (game.CLASS_NAMES, 1-17) as the creation screen numbers them
CREATION_CLASS = {**{c: 1 for c in range(1, 5)}, **{c: 2 for c in range(5, 9)}, 9: 3, 10: 4, 11: 5, 12: 6,
                  **{c: 7 for c in range(13, 17)}, 17: 8}

KIT_DISCIPLINES, KIT_SPHERES, KIT_LAST_PAGE = 3022, 3023, 3025  # (3020 and 3024 are the game's)
KIT_WINDOW = 3026  # + creation class (or multiclass group) - 1
KIT_ROW, KIT_NONE, KIT_VIEW = 0x870, 0x888, 0x889  # rows: KIT_ROW + 3 * (class - 1) + kit - 1
MULTI_ROW = 0x88A  # a multiclass group's rows: MULTI_ROW + 3 * (group - 9) + kit - 1
DRAWN = {
    "J": ("..####",
          "...##.",
          "...##.",
          "...##.",
          "...##.",
          "##.##.",
          ".###.."),
    "-": ("...",
          "...",
          "...",
          "...",
          "###",
          "...",
          "..."),
}

# the rules' bit (game.RULE_KITS), here to keep this module standalone
KITS_ON = 65536
SPHERES = {1, 2, 7}  # (creation classes: cleric, druid, ranger)


def row_text(name: str) -> str:
    return SHORT.get(name, name.upper())


def row_id(group: int, kit: int) -> int:
    """The kit page's row for kit KIT (1-3) of a class or multiclass group."""
    if group >= min(MULTI):
        return MULTI_ROW + 3 * (group - min(MULTI)) + kit - 1
    return KIT_ROW + 3 * (group - 1) + kit - 1


def multi_group(race: int, classes: Sequence[int]) -> int:
    """The multiclass group (9-13) of a character of RACE and two CLASSES at once, as the creation
    screen numbers them (0 for none), or 0: none of that race and pair (DSCLOG's MULTI_GROUP)."""
    pair = frozenset(c for c in classes if c)
    if len(pair) != 2 or len([c for c in classes if c]) != 2:
        return 0
    return next((g for g, (r, cs) in MULTI.items() if r == race and cs == pair), 0)


def sheet_group(sheet: bytes) -> int:
    """The multiclass group of a sheet (its classes 1-17), or 0: one class, a human, or none."""
    if len(sheet) <= KIT_BYTE or sheet[0x18] == 1 or not sheet[0x22]:
        return 0
    return multi_group(sheet[0x18], [CREATION_CLASS.get(c, 0) for c in sheet[0x21:0x24]])


def kit_place(sheet: bytes) -> Optional[int]:
    """The place (0-2) among the sheet's classes of its oldest class, as DSCLOG's KIT_PLACE: 0 for
    one class, or for two classes at once with a multiclass group (sheet_group); for a human who
    has changed class (the classes move down, the new one first) its first class, the last of its
    classes; None for more than one class otherwise (no kits)."""
    if len(sheet) <= KIT_BYTE:
        return None
    if not sheet[0x22] and not sheet[0x23]:
        return 0
    if sheet[0x18] != 1:  # (a human's: game.HUMAN)
        return 0 if sheet_group(sheet) else None
    return 2 if sheet[0x23] else 1


def kit_at(sheet: bytes, place: int) -> int:
    """The kit (the creation class x 4 + the kit: RAVAGER 15) of the class at PLACE, asleep or not,
    or 0, as DSCLOG's KIT_AT: KIT_BYTE has two bits for each class (0 none, 1-3), the first class's
    lowest, each class taken after (DUAL) the next two. (The rule is the caller's to weigh.)"""
    oldest = kit_place(sheet)
    if oldest is None or not 0 <= place <= oldest or sheet[KIT_BYTE] == 0xFF:  # (0xFF: KIT_OPEN)
        return 0
    kit, cls = sheet[KIT_BYTE] >> 2 * (oldest - place) & 3, sheet_group(sheet) or CREATION_CLASS.get(sheet[0x21 + place])
    if cls in KITS and kit > len(KITS[cls]):
        return 0  # (a group's kit it hasn't)
    return cls * 4 + kit if cls is not None and kit else 0


def kit_awake(sheet: bytes, place: int) -> bool:
    """Whether the kit of the class at PLACE counts, as DSCLOG's KIT_AWAKE: the class a human has
    now always; a class it had before once the class it has now is of a higher level (as the game
    counts its earlier classes). Asleep till then."""
    return place == 0 or sheet[0x24] > sheet[0x24 + place]


def kits_of(sheet: bytes) -> List[Tuple[int, int, bool]]:
    """[(kit, place, awake), ...]: the sheet's kits, the oldest class's first."""
    oldest = kit_place(sheet)
    if oldest is None:
        return []
    return [(kit_at(sheet, p), p, kit_awake(sheet, p)) for p in range(oldest, -1, -1) if kit_at(sheet, p)]


def kit_ids(sheet: bytes) -> List[int]:
    """The sheet's kits that count (awake), the oldest class's first: DSCLOG's KIT_IS finds these."""
    return [kid for kid, _, awake in kits_of(sheet) if awake]


def kit_place_of(sheet: bytes, kid: int) -> Optional[int]:
    """The place of the class the sheet has kit KID for, asleep or not, or None."""
    return next((p for k, p, _ in kits_of(sheet) if k == kid), None)


def kit_level(sheet: bytes, kid: int) -> int:
    """The level of the class the sheet has kit KID for, 0 for none: DSCLOG's KIT_LEVEL (a Ravager's
    AC, a Seeker's slots, a Shinobi's casting go by it)."""
    place = kit_place_of(sheet, kid)
    return 0 if place is None else sheet[0x24 + place]


def kit_class_of(sheet: bytes, kid: int) -> int:
    """The class (1-17) the sheet has kit KID for, 0 for none: DSCLOG's KIT_CLASS_OF_SHEET."""
    place = kit_place_of(sheet, kid)
    return 0 if place is None else sheet[0x21 + place]


# KIT_IS's numbers, by name
KIT_IDS = {name: cls * 4 + k + 1 for cls, names in KITS.items() for k, name in enumerate(names)}


def name_of(kid: int) -> str:
    return KITS[kid // 4][kid % 4 - 1]


def kit_names(sheet: bytes) -> List[str]:
    """The sheet's kits (the game's classes, 1-17), asleep or not, the oldest class's first."""
    return [name_of(kid) for kid, _, _ in kits_of(sheet)]


def kit_byte(sheet: bytes, place: int, kit: int) -> int:
    """KIT_BYTE with the kit (0-3, of its class's three) of the class at PLACE set to KIT."""
    oldest = kit_place(sheet)
    byte = 0 if sheet[KIT_BYTE] == 0xFF else sheet[KIT_BYTE]
    shift = 2 * (oldest - place)
    return byte & ~(3 << shift) & 0xFF | kit << shift


def kit_class(classes: Sequence[int], rules: int, race: int = 0) -> int:
    """The creation class with kits to choose (CLASSES as the creation sheet has them, 0 for
    none), or for two classes the multiclass group of RACE and them (multi_group), or 0: the rule
    off, or more than one class without a group."""
    if not rules & KITS_ON:
        return 0
    if any(classes[1:3]):
        return multi_group(race, classes)
    return classes[0] if 1 <= classes[0] <= 8 else 0


def panel_windows(classes: Sequence[int], rules: int, race: int = 0) -> Tuple[int, int]:
    """The windows the panel shows for the sheet being made: the disciplines' and the spheres'
    (DSCLOG's WP_IDS), with KITS for their button where there are kits to choose. (A warrior's
    weapon specs are picked after DONE, on the weapon window: DSCLOG's CR_WEAPONS.)"""
    sphere = any(c in SPHERES for c in classes)
    if kit_class(classes, rules, race):
        return (wp.DISCIPLINES if sphere else KIT_DISCIPLINES), KIT_SPHERES
    return wp.DISCIPLINES, wp.SPHERES


def chunks(resource: gff.Chunks) -> Dict[Tuple[str, int], bytes]:
    """For the Loader's copy of RESOURCE.GFF: the kit pages, the windows with KITS for their
    button, and their rows' and buttons' pictures and buttons."""
    font = wp.glyphs(resource)
    for ch, art in DRAWN.items():
        font[ch] = [[c == "#" for c in line] for line in art]
    row_colours = wp._colours(resource[("ICON", wp.ROW_TEMPLATE)])
    toggle_colours = wp._colours(resource[("ICON", wp.TOGGLE_TEMPLATE)])
    row_button, toggle_button = resource[("BUTN", wp.ROW_TEMPLATE)], resource[("BUTN", wp.TOGGLE_TEMPLATE)]
    added: Dict[Tuple[str, int], bytes] = {}
    rows: List[Tuple[int, str]] = [(row_id(cls, k + 1), row_text(name))
                                   for cls, names in KITS.items() for k, name in enumerate(names)]
    for cid, text in rows + [(KIT_NONE, "NO KIT")]:
        added[("ICON", cid)] = wp.picture(font, text, wp.ROW_PAD, row_colours)
        added[("BUTN", cid)] = wp.row_button(row_button, cid, font, text)
    added[("ICON", KIT_VIEW)] = wp.picture(font, "KITS", 0, toggle_colours)
    added[("BUTN", KIT_VIEW)] = wp._button(toggle_button, wp.TOGGLE_TEMPLATE, KIT_VIEW)
    spheres = resource[("WIND", wp.SPHERES)]
    sphere_items = wp._items(spheres)  # (four rows, then the button)
    rows_at = [(x, y) for _, x, y in sphere_items[:4]]
    toggle_at = sphere_items[4][1:]
    for cls in KITS:
        ids = [KIT_NONE] + [row_id(cls, k + 1) for k in range(len(KITS[cls]))]
        items = [(cid, x, y) for cid, (x, y) in zip(ids, rows_at)] + [(wp.BACK, *toggle_at)]
        added[("WIND", KIT_WINDOW + cls - 1)] = wp._window(spheres, KIT_WINDOW + cls - 1, items)
    added[("WIND", KIT_SPHERES)] = wp._window(
        spheres, KIT_SPHERES, [(KIT_VIEW if c == wp.SPHERE_TOGGLE else c, x, y) for c, x, y in sphere_items])
    disciplines = resource[("WIND", wp.DISCIPLINES)]
    added[("WIND", KIT_DISCIPLINES)] = wp._window(
        disciplines, KIT_DISCIPLINES,
        [(KIT_VIEW if c == wp.DISCIPLINE_TOGGLE else c, x, y) for c, x, y in wp._items(disciplines)])
    last = len(wp.PAGES) - 1
    page_rows = [(wp.ROW_FIRST + last * specialize.PAGE_SIZE + r, x, y) for r, (x, y) in enumerate(rows_at)]
    added[("WIND", KIT_LAST_PAGE)] = wp._window(spheres, KIT_LAST_PAGE, page_rows + [(KIT_VIEW, *toggle_at)])
    return added


def row_widths(resource: gff.Chunks) -> Dict[str, int]:
    """Each row's picture's width (to hold them to ROW_WIDTH)."""
    font = wp.glyphs(resource)
    for ch, art in DRAWN.items():
        font[ch] = [[c == "#" for c in line] for line in art]
    out = {}
    for names in KITS.values():
        for name in names:
            out[name] = len(wp.label(font, row_text(name), wp.ROW_PAD, 1)[0])
    out["NO KIT"] = len(wp.label(font, "NO KIT", wp.ROW_PAD, 1)[0])
    return out
