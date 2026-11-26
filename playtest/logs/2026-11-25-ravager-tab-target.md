# 2026-11-25: choosing an enemy with Tab in Wake of the Ravager

**Under test:** branch `claude/ravager-tab-target` (on `claude/ravager-port-all`): DSCLOG2's TARGETING (Tab,
Shift+Tab and Enter taken from INT 16h on a party member's turn), PROBE_HIT (site 77, at the sequel's finder of
what is under the pointer, file 29DBDh), RINGS (the red ring drawn into the floor after the walls' shadows, RED
made by the Loader from the palette) and the Loader's side in RavDiceLog (targeting.py, rings.py, hover.py,
hitchance.py on the sequel's layout). DSCLOG2.EXE 40880 bytes.

The runs ([files/2026-11-25-ravager-tab-target-run.sh](files/2026-11-25-ravager-tab-target-run.sh)): a fresh copy
`ravTT` of `ravK` (the `fountain-user` party transferred) each time, the Loader's start, the four ADDed, a new
game, HP 250 for the four (a test edit, never saved; the copy thrown away), `ravdice.py --numbers`, the Draxans'
ambush in Tyr played by hand with `xdotool key` (Tab, shift+Tab, Return) and `ravclick.py X Y none` for the
pointer; `ravtab.py` (new) for DSCLOG2's words. Four starts (a-d), each fixing what the one before showed.

## What was seen

- **Run a, the control with the ring and chances off** (`RAV_TAB_OFF=1`): Tab chose: `Chosen with Tab: Draxan
  (140 HP) - Enter attacks it`, no "needs", no ring (`rings_on=0 ring_draws=0`). Enter gave nothing: the first
  build's click (the button bit of the main loop's pointer call, 20230h) isn't how the sequel reads clicks.
  **Found:** the main loop's 35B9:0034 is INT 33h 3 for the pointer's place only (edge scrolling); clicks come
  through the handler the game sets with INT 33h 0Ch. DSCLOG2 now finds that handler by INT 33h 14h (swapped
  for a RETF and given back at once) and calls it with a press and a letting go, as SL's DSCLOG does.
- **Run b, on:** Tab chose the nearest (`hit_target=0x1b`, 16 map units from Ester), Tab again the next ones,
  Shift+Tab back. The red ring under the chosen Draxan. Enter: `Ester attacks Draxan#27 with Obsidian Longsword
  (1d8): d20 = 14, needs 15+ (30%)` three times; the Tab line had said `needs 15+ (30%)`. On Seneca's turn the
  pointer over a Draxan in the doorway showed `14+ (35%)` over it; Tab to it, Enter: she **walked up and
  attacked** (`Seneca attacks Draxan#26 ... needs 15+`, `... item 261 +1 ... needs 14+`): **one off** from
  that line's `14+`/`13+` (before the walk; after it the Loader's prediction for the same pair was 15/14, and
  the effects on the board were none of the Draxan's). Open: why the walk-up prediction from the doorway was
  one easier.
- **Run c**: `dosmem.py` found the upper memory chain **broken right after DSCLOG2's block**: the new code had
  gone in after RESIDENT_END (freed when the helper went resident, the next MCB written over). Moved into the
  resident part.
- **Run d, the build under test** (every point again): DSCLOG2 **40352 bytes** in upper memory, **115104 free**
  after it in one piece (the chain whole). Jenna's turn: Tab `hit_target=0x17` (the nearest, 22 units), Tab
  `0x1a`, Shift+Tab `0x17`; the ring ([picture](img/2026-11-25-ravager-tab-ring.png)); Enter: `Jenna attacks
  Draxan#23 with Obsidian Longsword (1d8): d20 = 10, needs 16+ (25%)` (x3), the line `needs 16+ (25%)`. Lex's
  turn: the pointer on the Draxan standing behind the first: `15+ (30%)` over it
  ([picture](img/2026-11-25-ravager-hover-chance.png)); Tab twice to it, the ring under it behind the front
  one; Enter: `Lex attacks Draxan#26 with Bone item 258 (1d6): d20 = 6, needs 15+ (30%)`: the one behind,
  the line `needs 15+ (30%)`. DSCLOG2's counts: `attack_clicks=2 hit_answers=23 ring_draws=39`.
- **Control, the Loader stopped** (the dice log killed, DSCLOG2 left with `target_on=1`): Tab is the game's
  again: it opens the game's own menu (the Tab menu), `tab_seq` unchanged. (With the Loader there, Tab on a
  party member's turn in a fight is the Loader's, as in Shattered Lands.)
- Not done: the view scrolling to a chosen enemy off the screen (SL's PAN: no such words in DSCLOG2; Enter
  does nothing then). Weapons named `item 258`, `Bone item 291 +1` in the Tab line as in the dice log's own
  attack lines (the transferred items' names past the list RavGameData reads: not this branch's).
- No water in this run (Tyr's ambush street only).

Pictures for the docs: `/mnt/project-files/ravager/2026-11-25-ravager-tab-ring.png`, `-tab-ring-behind.png`,
`-hover-chance.png`, `-tab-no-loader.png`.
