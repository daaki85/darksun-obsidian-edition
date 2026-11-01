# Sewer grate test: notes

Live notes, written as the test goes. Newest at the bottom.

## What's under test

The four grate repairs in `scriptfixes.py` (script 137), as the Loader builds them (commit 1740690+):

- A65h: "Hack the lock off." offered to a member with a weapon in the right hand
- 9E0h: the success line says his or her (detour, with relocated IF/ELSE addresses)
- A14h: a hack that works opens the grate (flag 505, "The grate opens.")
- A31h: a failed hack breaks a weapon that can break (TAKE), and a metal or magic one "rings off the grate, unharmed" (detour, reads the material through the item's type)

## Setup

- Headless DOSBox (Xvfb :55), the Loader's patched game and rebuilt scripts (`start.sh`), the dice log attached for memory reads and writes.
- No saved games in the test folder: a new game with the ready-made party.
- Plan: through the opening arena fight to the slave pens; then move the party next to the grate (region 29h, square 46,86) by writing positions in memory; if that misbehaves, the cluebook route (#11: the stalker pen, the button on the north wall).
- The hack's roll (RAND(3) < 2) forced in the test copy's GPLDATA only, to get success and failure on demand.

## Log

### 13:05 Rules reviewed first

- Read the testing rules (`combat-testing.md`). It had been lost with the container; rebuilt from
  the session log (rules 1-14). Several tools it names are gone too (the watchdog, movekeeper,
  walkto, mouse, waitfor). Rebuilt the watchdog (`guard_start.sh`) and started it; Monitor on
  guard.log for STUCK/GONE.
- Rule 4 (the build in place): the game runs `obsidian-edition/dos/GPLDATA.GFF`, built 12:57 today.
  Checked script by script: every repair is in place (31, 42, 44, 56, 80, 137, 142, 203, 210).
  Script 137 is 8575 bytes (8238 in the game's), the grate detours at its end.

### 13:06 New game

- `start.sh`, then `topartyfight.sh`: new game, ready-made party, through the opening to the
  arena's first fight. Reached: `FIGHT: in_combat 1, turn 1, region 0x2a` (the arena).
- Next: end the fight with `killfoes.py` (rule 3's purpose: a fight that isn't under test, ended
  quickly), then follow the game back to the pens (region 29h).

### 13:10 The opening fight ended

- `killfoes.py`: 3 Sligs and the Screamer Beetle killed. The fight stayed on until K'ratchek's turn
  ended: a click on her figure opened END K'RATCHEK'S MOVE (GUARD / WAIT / END TURN); END TURN, and
  `fc.py` read `fight_on 0`. (A first click beside her walked her a step instead: Move 15 to 14.)
- Region still 2Ah (the arena), party at (488, 424). The game clock barely moves with the party
  standing (00:03 to 00:08); no message came in over a minute, so nothing will happen on its own.

### 13:14 Stopped: can't walk the party

- The arena's way back to the pens: the scripts say "Attention gladiators: Go back to the pens to
  heal your wounds" (script 2) and Kurzak "So! You survived this time. Follow me." (script 141), so
  the party has to walk out by the gate. A click at the gate (160, 40) didn't move it.
- My old setup put the pointer in Walk mode first (`ptrmode.py`) and walked with `walkto.py`; both
  are among the lost tools. Rebuilding them is the next step.
- Watchdog stopped while I report (no STUCK lines from it during the test).

### Still ahead (the cluebook's route, pens map)

1. Back to the pens (follow Kurzak out of the arena).
2. #11: break down the mountain stalker pen's door, kill the stalker, push the button on the north
   wall: the secret door to the pens' northwest corner.
3. #12: the grate. Each weapon case there (wood, metal, magic, Bloodwrath), the roll forced in the
   test copy, a save before each case. The cluebook says a failed attempt can be tried again.

### 14:00 Second run: learning the controls again (the old tools were lost)

- DOSBox had died while the session sat idle: restarted (start.sh, topartyfight.sh).
- E opens the Effects screen (Escape closes it). A click ON the active figure opens its END menu;
  END TURN's row moves with the menu (read it off a screenshot).
- Right-click cycles the pointer: arrow (Walk), red sword (attack), another red, arrow.
- The camera is DS:1178h: screen = map - camera, 1 unit a pixel; it scrolls in steps, not centred.
  Wrote walkto.py on that: walking works ((488,424) to (552,376), then to a 40-unit step).
- killfoes.py had bypassed the arena's scripts: no Announcer, flag 11 never set. Restarted again
  and finished the fights with fightout.sh (foes to 1 HP, Tab + Return). A message box blocks
  Tab/Return: msgbox.sh detects it, and fightout clicks it away first.
- The arena sent waves (Sand Howlers, a Tohr-kreen...), then "Yell something back at the
  Announcer? (Answer Yes or No)": a click doesn't answer it, the N key does. Then "Attention
  gladiators: Go back to the pens to heal your wounds."
- Flag 11 still 0. Walking north stopped at the bone wall (488, 328: NO PATH FROM HERE). Later:
  "The patience of the citizens of Draj is not infinite. Since you will not leave, you must fight!"
- Stopped here to write the playing guide (playtest/PLAYTESTING.md) and its tools, committed to
  the repository. The way out of the arena is its open problem.
