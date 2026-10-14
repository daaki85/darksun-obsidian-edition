# Handoff: a scrolling combat log inside the game (Obsidian Edition)

*From Claude Design, kept as received (design only). The three mock-up images it names
(`1-in-game-concept.png`, `2-panel-states.png`, `3-line-types-and-behaviour.png`) were shared
as screenshots in the conversation and are not in this folder yet.*

**Status (built):** Stages 0 to 5 are in (the panel, its lines, scrolling, the sizes, level chip, filters and L); see DEVELOPMENT.md, "The in-game combat log", for what was built and how it differs (the header reads "Round 2: Gerakis, then Cermak", the panel is 78 rows docked, and End, PgUp and PgDn stay the game's). Not built: keeping the panel up under game windows, and clicking a name to centre the view.

**Status when written:** design only. Nothing in this brief was built then, and nothing here has been run against the game. The repo was read at HEAD `9a78f62` without `DSUN.EXE`, DOSBox or a way to play, so every claim about the game's internals below is either quoted from `DEVELOPMENT.md` / `dsclog.asm` or marked **unverified**.

**The ask:** put the Ledger's dice log on screen in the game itself, as a docked panel that scrolls, like the combat log in Baldur's Gate: Enhanced Edition. Today the log lives only in the Templar's Ledger window, and the in-game option ("Show each turn's rolls in the game") is a blocking dialogue box at the end of each turn.

## 1. The design

| File | What it shows |
|---|---|
| `1-in-game-concept.png` | The panel docked bottom right on a real game screenshot (1200 × 750 = the 320 × 200 game screen at 3.75×). |
| `2-panel-states.png` | A collapsed · B docked, in short (default) · C scrolled back with filters and a "Jump to latest" chip · D expanded, in detail. |
| `3-line-types-and-behaviour.png` | Every line type with its colour, the controls, size and placement, and the three detail levels. |

The log lines in the mock-ups are copied from the Ledger's own output (the arena's opening show: Defiler, Slig, Rampager, Gerakis). The numbers in the "Attack, miss", "Power points" and header rows (`5 vs 11+`, `NEXT Cermak, Cilla`) are illustrative; the final strings are whatever `turn_summary` / the log produce.

### Layout
- **Docked bottom right**, about **180 × 67 px on the 320 × 200 screen**, clear of the status box (top right) and of the fight (middle).
- Frame in the game's own stone: `#71718A` with `#A6A6BE` / `#595971` bevel, `#202038` outline, rounded corners. Dark well `#30304D` (`palette.DEEP`). All from `dscompanion/palette.py`.
- **Pinned header**: `ROUND 2   NOW Gerakis   NEXT Cermak, Cilla` (the Ledger already keeps this status line: `status["round"]`, `still_to_act` in `dicelog.py`).
- **Seven lines visible** docked. Top line fades (a dithered edge, like the dust puffs; no alpha in mode X).
- Header buttons: an `L` key hint, a detail-level chip (`Short` / `Detail` / `Least`), a collapse arrow. Scrollbar on the right.

### States
- **A. Collapsed:** one line, the newest event; `L` or the arrow expands.
- **B. Docked (default):** short form, follows the action.
- **C. Scrolled back:** scrolling stops auto-follow. A chip `Jump to latest · N new` counts what has happened since; a click on it, or `End`, goes back. Filter chips (`All · Party · Damage · Saves`) narrow the view without losing history. **Optional; build last.**
- **D. Expanded, in detail:** the Ledger's own detail lines, wrapped with a hanging indent, sub-lines indented. About 106 px tall: for reading, not for leaving open.

### Line colours
By line kind, as in the Ledger (`palette.LOG_COLOURS`), with names in the Ledger's name colours.

| Kind | Colour | Example (short level) |
|---|---|---|
| hit | `#8FD16A` | `Rampager attacks Defiler: 20 vs 16+ HIT, 2 damage` |
| miss | `#B4B4C8` | `Gerakis attacks Slig: 5 vs 11+ miss` |
| damage / HP | `#FFA600` | `Defiler takes 16 from Acid, now 0/18 HP` · `Cone of Cold damage: 9d6 = 30` |
| save / magic resistance | `#86ABFF` | `Slig saves vs Cone of Cold: d20 = 9, needs 16 -> failed` |
| turn | `#D3A28A` | `Rampager's turn` |
| kill / other | `#E7EB18` | `Slig is killed` |
| detail | `#C8C8D8` | `THAC0 7 = 7` · `Gerakis regains 18 PSP (27 -> 45)` |
| round rule | `#D7D7E3`, underlined | `ROUND 2` between two rules |
| party names | `#6FD8E8` `#F48CF4` `#FFB86B` `#FFFFFF` | by place in the party (`palette.PARTY_COLOURS`) |
| monster names | `#FF7070` bold | `palette.MONSTER_COLOUR` |

Colour is never the only cue: a **filled pip** marks a party member's line, a **hollow pip** a monster's, and the words (`HIT`, `miss`, `failed`, `is killed`) carry the meaning. Each colour is matched to the nearest index of the current area's palette (as `shadows.py` / `dust.py` already do).

### Detail levels
Reuse `POPUP_MINIMAL`, `POPUP_SHORT` (panel default), `POPUP_DETAIL`. Strings from `DiceLog.turn_summary` / `_for_game` (`%` -> `" pct"`). **The panel needs a per-line version, with each line's kind and whose line it is**, which `turn_summary` doesn't give today.

### Controls
| Input | Action |
|---|---|
| click scrollbar arrows / drag thumb | scroll |
| `PgUp` / `PgDn` | page |
| `End` | jump to latest |
| `L` | expand / collapse (**unverified that the game doesn't use L**) |
| click a name | centre the view on that creature (stretch goal) |

No mouse wheel: GOG's DOSBox 0.74 never passes it to the game (`DEVELOPMENT.md`, "Scrolling the map").

## 2. What already exists
- Text into the game: `INT F1h` (`probe_turn`), `DiceLog._answer_turn`, `TSR_*` header fields, `HDR_SIG`.
- Drawing: the game's text routine (`INT 65h`, `F3h`, `F5h` `LOOK_DRAW`, `EF_PUT`); pixels into the mode X page in the floor pass (`PROBE_FLOOR`, `FLOOR_POST`, `vga_save` / `vga_restore`, `SHADOW_PASS`, `DUST_PASS`).
- Input: `int33` (mouse), `int16` (Tab / Shift+Tab / Enter).
- Game windows made from resources (window 3021, the psionicists' picker).
- Ledger side: `dicelog.py` (`lines()`, `turn_summary`, `still_to_act`, `popup_level`), `textlog.py`, the Options tab in `viewer.py`, `launch.py` `SWITCH_DEFAULTS`, `__main__.py` popup flags; Ledger-less `play`.
- Tests: `tests/test_dsclog.py` (unicorn), `python -m unittest discover -s tests`.

## 3. Constraints
1. **Memory**: DSCLOG is one 64 KB segment in a 63 KB UMB, a few KB left. Don't keep the history in DOS memory; check `mem` each stage.
2. **Every INT vector is taken**: share one with a site number (not 66h-6Fh).
3. **Only the GOG `DSUN.EXE` (611,408 bytes)**.
4. The turn popup blocks; the panel doesn't. Independent switches suggested.
5. The helper must never wait on a missing Ledger.
6. 256 colours, mode X, no alpha; dim through the shadow code's darker-colour tables.
7. Long lines: short form docked, detail only in state D.

## 4. Proposed architecture
- **The Ledger holds the history** (about 200 lines with kind, side, party slot) and formats, wraps, filters and slices.
- **DSCLOG holds only the visible slice** (about 1 KB) plus scroll position, state and follow flags.
- Ledger -> helper: slice + sequence number (as `_answer_turn`). Helper -> Ledger: scroll requests as counter + argument. Extra lines above/below the slice if latency hurts.
- Draw when the slice changes and whenever the game redraws the area under the panel.
- Settings: a switch beside "Show each turn's rolls in the game" (default off), level radio shared.

## 5. Staged plan (check in after each stage)
- **Stage 0, recon:** how the status box is drawn and kept on top; a final point in the frame (page flip) to draw last; the game's text routine and font metrics; free keys (`L`, `End`, `PgUp`, `PgDn`); UMB headroom. Write the answers into `DEVELOPMENT.md`.
- **Stage 1, static frame** in combat, surviving scrolling, figures, spells, inventory/View Character, dialogues, area changes, save/load, window sizes.
- **Stage 2, text:** per-line records, header, pips, colours, hanging indent; Options switch and level radio.
- **Stage 3, scrolling:** scrollbar (`int33`), `PgUp`/`PgDn`/`End` (`int16`), follow mode, the "Jump to latest" chip.
- **Stage 4, states:** collapse, expand, level chip, state D; filters and click-a-name if memory allows.
- **Stage 5, finish:** README, DEVELOPMENT, CHANGELOG, PATCH-NOTES, screenshot, release note; bump `HDR_SIG`.

## 6. Tests
Ledger side: per-line kind/side tagging for every line type, wrapping and slicing, follow/scroll arithmetic, filters, `%` handling, header layout. Helper side: unicorn tests for new handlers. Colours in `palette.TEXT_PAIRS`. Playtest: the arena's opening show, a normal and a long fight, scrolling back, save/load, area change, inventory during a fight, end of fight, DOSBox window sizes, `play` with no Ledger window, the Ledger closed mid-game, `mem` unchanged.

## 7. Decisions (suggested defaults)
1. On in fights when the switch is ticked; `L` collapses it.
2. Panel and turn popups on independent switches.
3. Filters only in Stage 4, dropped if memory is short.
4. Fixed bottom-right position first.
5. Click-a-name to centre: stretch goal.

## 8. Risks
No final-frame hook (fallbacks: a persistent game window; a modal log window on a key; the Ledger window as today); memory; flicker; scroll latency; the unverified game internals above.
