# Test log: the level cap by XP in Wake of the Ravager (2026-11-25)

Under test: DSCLOG2's LEVEL CAP BY XP (sites 110-117, RULE_LEVEL_10 now in ravager.RULES_PORTED) with the owner's
cap of 5,625,000 XP shared between a character's classes; XP_HOLD (XP held at the share); a thief's d6 to 10th
(the psionicist's stays 9th); the Player's Handbook's saves (SAVE_BASE, RULE_HI_TABLES); THIEF_TABLE to 17th; a
druid's slots flat from 15th and a ranger's the Handbook's (ADND_SLOTS); a ranger's casting level at most 9; the
party transfer's XP held at Shattered Lands' share. The owner's tables (thief skills 1-17, ranger 1-20, druid
slots, the hit dice) came through the coordinator: rows 1-13 of the thief table match THIEF_TABLE and DSCLOG's.
The druid's XP is settled: the owner's tables confirm the Handbook's 5,500,000 at 20th (RAV_XP's).

## Before the play

- Static research: RESEARCH.md's "The level up, the XP table and the saves in the sequel".
- Tests: tests/test_ravlevelcap.py runs every new site in an emulated CPU (LV_UP against ravager.level_room for
  1-3 classes at levels 1-20, the owner's highest levels, a human dual-class, View Character, the clamp and
  XP_NEED's "most", XP_HOLD, RAV_XP_AT against tables.RAV_XP, the thief's and psionicist's hit dice, the saves
  against tables.rav_saves at levels 1-24, XP_SUFFIX's " F)"); test_tables.py the slot, saves and thief tables in
  DSCLOG2 and DSCLOG; test_ravtransfer.py the transfer's XP hold.
- DSCLOG2: 47072 bytes (45168 before).

## The play

A second game beside the shared one (another agent held the lock with its own sequel game): the kit copied to
`/tmp/playtest/lckit` with `obsidian-edition` linked, display `:58`, DOSBox copied as `dbLC`
(`SDL_VIDEO_X11_WMCLASS=dosbox`), `PLAYTEST_WORK=/tmp/playtest/lcw`, the game a throwaway copy
`/tmp/playtest/ravLC`. `files/2026-11-25-ravager-level-cap-start.sh`'s steps (its paths changed for the copy):
RAV_LOADER=1 ravstart.sh, ravdice.py attached, the opening talk to the Draxans' ambush. Then, all test edits
(never saved; both DOSBoxes stopped unsaved): `ravlevel.py set` on the four, the Draxans' HP 1
(`ravlevel.py foes 1`), Computer Control for all four (C, then the USE screen's lower small icons), the XP
boxes clicked through. The fight gives 4,000 XP a member (a third each to a triple class), then the box's
10,000.

| member | set | the rule on | the control (RAV_SKIP, the eight patches) |
|---|---|---|---|
| Gerakis, half-giant fighter | 17th, 3,000,000 | 18th, 19th, 20th ("Gerakis is 20th level Fighter"); XP 3,014,000 kept; THAC0 1; saves 3/5/4/4/6; View Character "EXP:3014000" with no next XP | stays 17th, **XP 0** |
| Ar'Anda, elf fighter/cleric/thief | 14/15/17, 4,000,000 | 15/16/18 (three messages); XP held at the share, 1,875,000; THAC0 6; saves 4/6/5/4/7; View Character no next XP | 15/15/17, **XP 0**, saves 8/8/8/10/9 (the game's formula) |
| Terrannus, human fighter (a cleric 20 before) | 17/20, 3,100,000 | fighter 19th ("gains a level" twice); XP held at 2,925,000; THAC0 2; saves 2/5/4/4/6; View Character "19/20", no next XP | stays 17th, **XP 0** |
| Thy'rokh, thri-kreen thief | 9th, 155,000 | 10th: "Thy'rokh's 10th Thief level: hit points d6 = 3 and 6, the better 6" (base HP 84 to 90); saves 11/10/10/14/11; View Character "EXP:169000 (220000)" | 10th with a d4 (base HP 84 to 86) |

- **The saves** are the least of each group's (the game's own loop, 954D2h): Ar'Anda's warrior 15th
  (4/6/5/4/7) is under her priest 16th (4/8/7/10/9) and rogue 18th (9/6/8/12/7) in all five; Terrannus's
  2/5/4/4/6 is his priest 20th's 2 and warrior 19th's other four. All the Handbook's Table 60. Helper counts:
  lv_rooms 9, lv_tops 1, hd_tens 2, save_count 85.
- **The control** shows the original's bug the clamp fixes: past the table's end the game's XP clamp reads a 0,
  and a character at 17th or more loses all the XP. The level cap held everyone else at 15th.
- **Upper memory** (`dosmem.py`, the Loader's start): DSCLOG2's block 46,544 bytes; 109,056 bytes free in two
  pieces, the largest 108,912. Conventional: 111,296 bytes after the game.
- Screenshots (to the project's `ravager/` folder): `level-cap-view-gerakis-20th.png` (View Character at 20th,
  the saves), `level-cap-triple-held-at-share.png` (Ar'Anda at 15/16/18 held), `level-cap-thief-10-and-human-held.png`.

**What a play needs to know** (to PLAYTESTING.md and RESEARCH.md): on View Character a click on a portrait at
the Effects screen's spots, (70,56) (117,56) (70,127) (117,127), shows that member (the top-left icon's
screen keeps the leader's otherwise). Level-up messages come one a click of the box (160,100); the dice log's
"Message:" lines list them all, the screen grabs may miss one. A triple class gets a third of a fight's XP.

The watchdog (guard_start.sh) wasn't started: its pid file is shared, and starting it kills another agent's.

## Gaps

- An XP award from a script that doesn't run the level up (95820h) isn't held until the next level up: not
  checked which awards run it (the fight's does).
- The game's dwarf/halfling CON bonus to saves tests the group (CX) for 1 or 4, so it goes to the warrior
  group's saves only: kept as the game's (SL's the same).
- SL has the same saves bug (87844h): for later.
- Not played: a druid or ranger past 15th (the slots and the casting level), the transfer's XP hold (both
  covered by the tests).
