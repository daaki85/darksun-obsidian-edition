# 2026-11-19: the final audit's fixes in the game (claude/final-audit-fixes)

Under test: the Loader's rules starting at the always-on ones and its off-branches removed (the
reference models now always the rule's), write_atomic's own temporary names, launch.CONTENT
without the always-on keys, and DSCLOG without wp_redraw (6 bytes, the room unchanged).

## Set-up

- Lock taken (`flock /tmp/playtest/dosbox.lock`, a background holder).
- `loadsave.sh fountain-user`: window 320x240, `buildcheck.py` OK (the routines, 129 vectors at
  their handlers, the tail the same as the EXE), watchdog on (`guard_start.sh` and a Monitor).

## 1. The ambush's fight (`fountain-user`; foes held with `foeset.py C eff=34` but the Templar, 25)

- Weapon specialization and STR: `THAC0 19, +2 STR, +1 weapon, +1 specialized = 15`, damage
  `1d6 = [3] +1 weapon +2 specialized +4 STR 18`; three swings a round (3/2 + two weapons).
- A ring on a save: `Templar's saving throw vs Poison (10 damage) from Seneca (paralysis/poison/death): d20 = 5 +1 Ring of Protection = 6, needs 7 (75% to save) -> failed`.
- Hiding and the backstab, with the later swings (load 1 of the loop): `Seneca hides in shadows: d100 = 63, needs 67 or less (57 +10 cloak = 67, out of the sun) -> hidden`,
  `moves silently: d100 = 24, needs 77 (67 +10 boots) or less -> unheard`, then
  `Seneca attacks Templar BACKSTAB with Bone Hayneedle +1 ...: THAC0 19, +2 from behind, +2 backstab, +2 STR, +1 weapon = 12` (a miss),
  and both Shadowseeker swings `Seneca attacks Templar with Shadowseeker +1 ...: THAC0 19, +2 STR, +1 weapon, +1 specialized = 15`:
  not from behind, the +2 STR right (the #116 fix, with this branch's Loader).
- Spells rolling to hit (`spellsetup.py 2=9`, a memory edit, not saved): Ester's Magical Stone
  (USE, the level-1 priest page's second row, second icon) three throws, e.g.
  `Ester's Magical Stone at Templar: attack d20 = 4, needs 11+ (50%) (THAC0 19, +4 DEX; target AC 4) -> MISS: the spell does nothing, the 2 damage rolled lost`.
- A spell save with the spell save: Hold Person (level 2, first icon of the second row):
  `Templar's saving throw vs Hold Person from Ester (spell): d20 = 1 (natural 1) -> failed`.
- The Effects screen (E): Ester `KIT: B-DANCER / SPECIALIZED IN LONG SWORD`.
- Aiming a spell: the click goes 6 pixels above `foepos.py`'s point (y 128 for 134); 10 above
  missed twice ("no creature there").

## 2. A barred item (`pens-after-arena`)

Gerakis's chest armour (173,70) picked up, Cilla's portrait (22,160), her chest place:
`CANNOT USE THIS ITEM` on the bar (restrict.usable, now unconditional in the Loader). Not saved.

## 3. Kalzith's shop (`selling-junk-user`, `openshop.sh`)

The shop up, Gerakis (CHA 14) leading: 1$, 9000$, 6000$, 24$, 9000$, 6000$ (the game's prices, as
on 2026-11-19 before). A Bone Dagger from the backpack (195,62) and SELL (272,64): `I'll give you
1$` (60%, never below 1); LEAVE IT (145,104).

## 4. Resting (`pens-fire-count4`, `ringrest.sh`)

The priests' cures first (`At rest: K'ratchek casts Cure Serious Wounds on Gerakis (4th-level slots: 0 left)`, five
Cure Light Wounds, Cilla's), `Message: THE PARTY RESTS`, then AD&D's healing:
`Gerakis rests 8 hours: +3, +6 (CON 22) = +9 (+6: no more than the most), now 54/54 HP`,
`Cilla rests 8 hours: +3, +2 (CON 17) = +5 (+0: no more than the most), now 15/15 HP`.

## 5. The creation screen (start.sh, the title clicks, 30 s, CREATE CHARACTERS 165,92, a right-click on 64,52, NEW 110,57)

- Scores as rolled (`SUM: 99/99`), STORE and RECALL, `AGE`, `THAC0: M17 R16`, the hit dice the
  better of two (`8 (the better of 7 and 8) + 9 (the better of 9 and 4) + ...`), the KITS page
  (NO KIT, MYRMIDON, SENTINEL, RAVAGER, VIEW PSIONICS). EXIT.
- **Found, not this branch's**: the screen's AGE and the dice log's age line disagree after a new
  roll (the die, 155,97): AGE 19, 21, 22 against the log's 23, 23, 20 with this branch's Loader,
  and AGE 22, 16 against 23, 18 with origin/obsidian-edition's Loader (its dicelog run from a
  `git archive` copy against the same game): the same both ways. The log's line is
  `aging.give_ages` on the sheet being made, DSCLOG's AGE its own roll (`cr_age_draw`); left for a
  look of its own.

## 6. The Loader's window (`python3.12`, apt's tkinter), and `docs/dicelog-readable.png`

- Xvfb `:55` restarted at 1700x900 (DOSBox at 0,0, the window moved to 340,0: no overlap, so the
  kit's clicks still reach the game), `loadsave.sh fountain-user`, start.sh's text dice log killed
  by pid, the window started from a scratch wrapper that also appends the dice log's raw lines to
  `$WORK/dice.txt` (so the kit's loops can read them), and attached with **Reconnect**.
- Each reload: `loadsave.sh`, the text log killed, Ctrl+F10 to DOSBox (it lets the mouse go),
  Reconnect (1462,70), then `xdotool windowfocus` DOSBox and a click in it (it takes the mouse
  again). The second load: hidden and unheard, and the backstab hit:
  `Seneca hits Templar for 7: 1d4 = [1] +1 weapon +4 STR 18 +1 backstab (the dice 1 x2 = 2)`, then
  `Seneca attacks Templar with Shadowseeker +1 ...: THAC0 19, +2 STR, +1 weapon, +1 specialized = 15`
  twice (hits for 12 and 11): no from behind, the +2 STR right.
- The picture: the window 1320x880, the pane's sash dragged left (from x 951 to 420), the round
  cropped with **Show details** ticked and again unticked (1196x724, the two crops one above the
  other). The README's caption says what it shows now.
- **The party view**: the Characters cards. Seneca (thief 3 / fighter 2) has `Thief skills now:
  pick pockets 72%, open locks 68%, find/remove traps 52%, move silently 77%, hide in shadows 67%,
  hear noise 20%, climb walls 72%` (her 67 and 77 the dice log's `57 +10 cloak = 67` and
  `67 +10 boots`); Lex (fighter/preserver) and Ester (fighter/cleric) none.
- **Starting the game from the window, twice**: DOSBox killed by pid, Reconnect (the status
  "Not connected"), **Start the game** twice. Each time `prepare_patched_game` wrote the copies
  (GPLDATA, RESOURCE, SEGOBJEX and the regions at 18:27:16, then 18:28:16) and no `.tmp` was left in
  `dos/`; then the launch stopped at GOG's `DOSBox.exe`, a Windows program here ("[Errno 13]
  Permission denied"), the container's limit, not the mod's. The kit's start.sh, which calls the
  same `prepare_patched_game`, ran nine times over the play with the same result.
- **Found and fixed**: the copies came out mode 0600 (mkstemp's), where open() had made them 0644;
  `write_atomic` now sets 0644 before putting the file in place (a test).
- **Found, not this branch's**: the window attached by Reconnect to a DOSBox it didn't start kept
  saying "Connected to the game" after that DOSBox was killed, until Reconnect; and a reload under
  it logged once `Loader error in the party table: error: unpack requires a buffer of 4 bytes
  (game.py:798); it carries on`.

## Results

Every rule tried read as the rules have it, the backstab's later swings right, with the Loader's
rules now starting at the always-on ones and its off-branches gone. Nothing saved (the memory edits:
foes held, Ester's spells and levels, the party healed, all in `fountain-user`, never saved).
DOSBox, Xvfb, the dice logs, the window and the watchdog stopped by pid; the lock let go.
