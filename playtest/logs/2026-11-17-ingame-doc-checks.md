# 2026-11-17: in-game doc checks (look box picture, combat log level button, chestuse.sh, setitem.py)

Under test: the build of `obsidian-edition` at origin/obsidian-edition (branch
`claude/ingame-doc-checks`). The game set up with `setup_game.sh` from the private installers'
checkout (`PT_INSTALL_FILES` pointed at it: this worktree isn't beside it). The DOSBox lock held for
the session.

## Steps

- `loadsave.sh fountain-user`: window 320x240, `buildcheck.py` OK, watchdog started.

### The look box picture

- No creature with magic resistance in reach: a scan of every creature in the pens with
  `monsters.monster_lines` (fountain-user, pens-kurzak-door) found none with MR; the only one with
  a defence line is the pens' **Zombie** (creature 21, LEVEL 2, HP 10/10 AC 8, THAC0 19 AL TN,
  IMM POISON), in a room west of Kurzak's (square 79,53, map 1272,856). The two Mountain Stalkers
  (creatures 34-35, map 184,856 and 184,1064) show only HP/AC and THAC0/AL (NE).
- From `pens-kurzak-door`: `teleport.py 1200 864 1112 756` (a memory edit: nothing saved after),
  `pointer.py look`, a slow press on the Zombie at (160,88): the box at screen x 171-263, y
  49-124. Cropped 98x82+168+46 and scaled 200% (196x164, the old picture's size): the new
  `docs/look-box.png` shows Zombie, LEVEL: 2, HP 10/10 AC 8, THAC0 19 AL TN, IMM POISON.
- Escape does nothing with the look box up. Its fourth button (the plain rectangle, about 245,115)
  closes it, and the whole description comes in the dialogue window (Continue at 24,157).

### The combat log's buttons

- L, then slow presses (crops of 190x30 at 400%): the docked chip at (273,127) went Short ->
  Detail -> Least -> Short; + (306,127) expanded the panel; the expanded chip at (273,74) and at
  (262,74) went Short -> Detail -> Least -> Short; - (296,74) docked it; a press at (292,74)
  docked it too (the -'s left edge: the old note's "chip at 292,74 docks the panel"); the header's
  L (250,127) hid the panel. The rectangles match `combatlog.level_rect` / `key_rect` plus the
  panel's place (136, 120 docked / 68 expanded): L 245-254, chip 256-290, - 292-300, + 302-310,
  rows 122-131 / 70-79.

### chestuse.sh (Pehtucl's chest)

- `loadsave.sh pens-new-chest`, `shut.py` (chest type 67h, not disarmed, locked), `teleport.py 200
  1432 40 1322`, `walkto.py 216 1440` (STOPPED at 200,1432), `walkto.py 184 1400` (ARRIVED).
- `chestuse.sh` as it was: the look box "Chest" came up (cu1) and its third button gave "The chest
  is locked. Gerakis doesn't know how to pick the lock. Bash it open?" (cu2): the USE screen as
  meant. But the pointer was still the eye afterwards (`pointer.py` said mode 2 once N was
  pressed): the question took the right-clicks of the script's last `pointer.py walk`.
- Fixed: `chestuse.sh [y|n]` answers the question when given, clicks any message after it away
  (`msgbox.sh`, `boxclick.sh`), then puts the walk arrow back; without an answer it leaves the
  question up and says so. Runs: no answer (the message, exit 0), `n` (pointer mode 1), `y`
  ("Gerakis smashes at the lock, making a lot of noise but little else.", pointer mode 1).

### setitem.py

- `loadsave.sh fountain-user`, before the ambush's speech was clicked: `itemlists.py` showed Lex's
  held `(36, 2, 1)` (the bow, slot 2). `setitem.py 36 0`: type 1 -> 0; the record kept its link
  (+4, 270Fh), flags and slot (+10h 04, +11h 02), +08h 270Fh, +0Ch 0; +0 object and +12h name
  from the sling's record. After: `(36, 2, 0)`.
- The speech clicked away, `passuntil.sh 0` to Lex's turn, I: the weapon block "Staff Sling 1D3",
  and a right-click on the missile slot (64,49): "2 handed Leather Staff Sling 1D3". Escape closed
  the box and the inventory together.
- `pointer.py attack`, a press on the Templar (256,134): "Lex attacks Templar with Leather Staff
  Sling (1d3): d20 = 15, needs 10+ (55%) -> HIT", "Lex hits Templar for 3: 1d3 = [3]", then the
  stinkpot's save. `setitem.py` does what the recipe says; nothing changed. Not saved (memory
  edits).

## Water

No new area: the pens only (Pehtucl's room, the Zombie's room west of Kurzak's: no water, jug or
waterskin seen in either).

## Results

1. `docs/look-box.png` retaken on the pens' Zombie (no creature with MR in reach); the alt text's
   line in FEATURES.md changed to match.
2. The combat log's buttons measured and confirmed; the guide's bullet has one set.
3. `chestuse.sh` opened the USE question but left the eye up; fixed and run three ways.
4. `setitem.py` worked first time: memory, the item box and a shot all agree.
