# 2026-11-25: Tab in the sequel, the two things left open: the view to an enemy off the screen, the walk-up one off

**Under test:** branch `claude/ravager-tab-followups` (on `claude/ravager-shops-tab`): DSCLOG2's PAN (DSCLOG's
PAN_X and PAN_Y at its header's +230/+232, PAN_TICK from PROBE_SCROLL: the view moved by what the Loader adds,
through the game's own centring routine 1C5F:01F3), the Loader's targeting.py writing them (RavDiceLog's
`_target_ranges` makes them writable); `game.armour_ready` (a monster's armour counted before its gear is
placed, for a gladiator's AC); `ravdice.py`'s `RAV_PREDICT` (a Tab line's chance taken apart) and `RAV_NO_PAN`
(the control), `ravtab.py`'s PAN words. DSCLOG2.EXE **41680 bytes** (the join's 41536 and PAN_TICK).

The runs ([files/2026-11-25-ravager-tab-followups-run.sh](files/2026-11-25-ravager-tab-followups-run.sh), the
Tab log's run script with this worktree and a copy `ravTF`): a fresh copy of `ravK` each time, the transferred
party, a new game, HP 250 for the four (a test edit, never saved; the copy thrown away), `ravdice.py
--numbers` with `RAV_PREDICT=1`, the Draxans' ambush in Tyr played with `xdotool key` (Tab, shift+Tab, Return)
and `ravclick.py`. Run a with the PAN build and the Loader before the AC fix (the measurement, the PAN play and
its control); run c with both.

## What was seen

- **The view to the chosen enemy (run a).** Lex's turn first. Tab: Draxan#26 in the west doorway (screen
  80,48: inside the view, but within the top's margin) -> the view from 1032,1368 to 952,1312 (`pan_moves=1`).
  Tab on to the Caravan Master (#20, off the right edge, screen 336,128): the view to 1208,1368, the ring under
  him ([picture](img/2026-11-25-ravager-tab-pan.png) is the way back: Shift+Tab x4 to #26, view 888,1296,
  `pan_moves=3`, the ring in the doorway). Enter: Lex walked up and attacked #26 (`attack_clicks=1`).
- **Control** (Jenna's turn, the dice log started again with `RAV_NO_PAN=1`: the Loader as before PAN). The
  view edge-scrolled right to 1504,1304, the Draxans 400 pixels off the left edge; Tab to #26: the view stayed
  ([picture](img/2026-11-25-ravager-tab-pan-control.png)), Enter counted (`attack_seq` 2 -> 3) but no click
  (`attack_clicks` 2). The dice log without it: Tab -> the view 952,1312 (`pan_moves=4`), the Draxans on
  screen.
- **The walk-up one off, measured (run a).** Lex's line for #26: `needs 14+ (35%)`; `RAV_PREDICT`: THAC0 16, AC
  2 front (6 behind), no gap, no effects. Enter, the walk: `Lex attacks Draxan#26 ... needs 15+ (30%), target AC
  1`. Seneca (the dice log restarted with `--all`, the gap forgotten): `Bone item 291 +1 needs 14+; Metal item
  261 +1 needs 13+; Sling needs 16+` (the Tab log's numbers); the game: `AC of Draxan#26 against Seneca#1: 1
  (base 10, armour -4, DEX -4, other -1)`, needs 15+ and 14+ (x2).
- **Found:** the Draxans are **gladiators of level 8** (sheet flags 40h, class 10), a fifth of the level (1)
  better in armour, which the Loader counts only with armour worn by the slot bytes. A Draxan that hasn't
  fought has its items' slots **14-19** (the brigandine's chest, arm and leg pieces 14-16, the weapons after);
  after the first swing at #26 they were 9, 6 and 0 (chest, legs, arm), 3, 2, 1. So nothing to do with the
  walk or the start position: the first attack on a monster that hadn't fought yet (the other sets matched
  because their Draxans had attacked first, or the dice log had seen their AC). `game.armour_ready` counts
  the armour of a monster none of whose items is placed; the unplaced #27 and #23: AC front 1 (was 2), #21 (no
  gladiator) 7 either way.
- **The fix played (run c, everything unplaced at the first turn).** Jenna's turn first: Tab (the view moved
  once) to #26, unplaced: `Obsidian Longsword needs 16+ (25%); Bow needs 17+ (20%)` (AC 1); Enter, the walk-up:
  `Jenna attacks Draxan#26 with Obsidian Longsword (1d8): d20 = 14 / 10 / 12, needs 16+ (25%)`: **matches**.
  Seneca's walk-up to the same Draxan: the line `Bone item 291 +1 needs 15+ (30%) ...; Metal item 261 +1 needs
  14+ (35%)`, the dice log `needs 15+` and `needs 14+`: **matches** (the case the Tab log left open, 14+/13+
  said there).
- Seen too: the Tab list in the sequel holds the street's other people (Caravan Master, Dhukkar, Arslan,
  Templar, Boric, pedestrians), over 20 after Jenna had walked; Enter on one out of reach (#27 in the room
  behind the doorway, a pedestrian) gives the click and the game does nothing; a shot with the attack pointer at
  #27 in the room did nothing either.
- No Illegal Op (`STDOUT.TXT` empty), the watchdog quiet. Not measured: the upper memory after DSCLOG2 (144
  bytes more than the join's, which left 114448 free).

No new area (Tyr's ambush street only).

Pictures for the docs: `/mnt/project-files/ravager/2026-11-25-ravager-tab-pan.png`, `-tab-pan-far.png`,
`-tab-pan-control.png`.
