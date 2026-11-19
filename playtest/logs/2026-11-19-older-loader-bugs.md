# 2026-11-19: three older Loader bugs in the game (claude/older-loader-bugs)

Under test: the dice log's age line on the creation screen (`aging.give_ages` skipped while the
screen is up, `aging.made_age` at DONE), and a DOSBox that ends under a Loader window attached to it
by Reconnect (`process.ProcessMemory`'s Linux reads and writes raise once the process has ended),
with the party table's `unpack requires a buffer of 4 bytes (game.py:798)` on a reload. Each was
seen with origin/obsidian-edition's Loader first (a `git archive` copy run against the same game),
then with the branch's.

## Set-up

- Lock taken (`flock /tmp/playtest/dosbox.lock`, a background holder), `start.sh`, `buildcheck.py`
  OK, the watchdog on (`guard_start.sh` and a Monitor; its GONE lines were the restarts below).

## 1. The creation screen's AGE and the dice log (start.sh, the title, CREATE CHARACTERS, NEW)

- **origin's Loader** (its dice log alone, the branch's killed by pid), a fresh game's first
  character: the screen's AGE 19, 23, 16, 19 over four rolls of the die (155,97), the log's
  `Ulf is 23 (a human: 15 + 1d8 = [8])`, then 18, 22, 23, 18: one line each roll, none agreeing
  (`img/2026-11-19-age-origin.png`). Memory meanwhile: `gd.creating()` True, the creation sheet
  with no age, **party member 0 "Ulf", the screen's stand-in, aged 18, roll 2**: the age the Loader
  had written into the stand-in's sheet.
- **The cause**: `aging.give_ages` (a starting age for each member without one) ran on the stand-in
  in the party's first slot; DSCLOG's AGE is its own roll (`CR_AGE`), the one `AGE_PUT` writes into
  the new member's sheet at DONE. So the screen is right and the log wrong.
- **The branch's Loader**: a first character, AGE 23 after rolls of 16, 22, 21, 23, no age line;
  DONE (278,182), the weapon window's long sword (72,46), four psionic picks (123,62): the sheet
  `age 23 roll 7`, as the screen showed. A second (slot 2, 120,52 right, NEW 165,57), with the dice
  log restarted on the new `made_age`: AGE 18, 21, 18, 16 (`img/2026-11-19-age-fixed.png`), no line
  while rolling, then at DONE `Morbad th'Worst is 16 (a human: 15 + 1d8 = 1, as the creation screen
  rolled); middle-aged at 40.` and the sheet `age 16 roll 0`.
- Seen too: the stand-in isn't always the first slot (the second character's was member 1), and it
  starts with the creation sheet's last age bytes (23, roll 7 from the first character) until DONE
  writes its own.

## 2. "Connected" after DOSBox ends, and the party table's error (`fountain-user`)

Xvfb `:55` restarted at 1700x900, the window (`python3.12 -m dsloader view`) moved to 340,0, start.sh's
text dice log killed by pid (two Loaders would both follow the game).

- **origin's window**, attached by Reconnect (Ctrl+F10 to DOSBox first, Reconnect at 1462,70):
  `kill -9` of DOSBox (as start.sh kills it) left the status `Connected to the game (process 2838)`
  for 12 s and more (`img/2026-11-19-reconnect-origin-status.png`), and the dice log said once
  `Loader error in the party table: error: unpack requires a buffer of 4 bytes (game.py:798); it
  carries on` (`img/2026-11-19-reconnect-origin-error.png`): both bugs at once. A plain `kill`
  (SIGTERM) the time before was noticed ("Not connected"): DOSBox's own exit, slower, gave a read
  error on the way.
- **The cause**: on Linux a read of `/proc/PID/mem` for a process that has ended (a zombie or
  reaped) comes back empty and a write writes nothing, without an error (tried on `sleep`), so no
  `ProcessError` reached the window; `game.far_pointer` unpacked the 0 bytes. A reload in the kit
  is a new DOSBox (loadsave.sh runs start.sh), so the error came "during a reload". The game has
  no load without a restart here (its EXIT menu's SAVE quits).
- **The branch's window**: the same `kill -9`, and within 4 s `Not connected: No DOSBox process
  found`, no error in the dice log. With the status kept on quiet retries, a reload by
  `loadsave.sh fountain-user` under the window read `Disconnected (process 3444 has ended).
  Waiting for the game...` three times 1.5 s apart, then `Connected to the game (process 3630)`
  (`img/2026-11-19-reconnect-fixed-status.png`), attached through the title and the load with no
  error; the party cards Lex's and Jenna's as before.

## Results

The screen's AGE is the age kept; the dice log now says it once at DONE and gives no age of its own
on the screen. The window sees a DOSBox it didn't start end, and a reload no longer logs the party
table's error. Nothing saved, no memory edit. DOSBox, Xvfb, the windows, the dice logs and the
watchdog stopped by pid; the lock let go.
