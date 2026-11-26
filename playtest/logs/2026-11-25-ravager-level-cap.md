# Test log: the level cap by XP in Wake of the Ravager (2026-11-25, levels 21-30 2026-11-26)

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

## Levels 21-30 (2026-11-26)

The owner's decision: past 20th for anyone, as far as the 5,625,000 cap allows, by their AD&D tables (XP,
slots; the rest the game's formulas). DSCLOG2: RAV_XP to 30 levels (dwords: the druid's 10,500,000 at 30th
won't go in a word of hundreds), XP_NEED answering RAV_XP's past the game's 20 entries (`xp_pasts`), LV_CLAMP to
index 29, RAV_SLOTS 30 rows a table, and LV_ORDINAL (site 118, "level_ordinal": "21st" for the game's "21th").
DSCLOG2 48,064 bytes; upper memory: its block 47,536, 108,064 bytes free (the largest 107,920). The highest
levels (ravager.level_most, as the coordinator's but the druid): one class: cleric, fighter, thief 30,
psionicist 27, ranger and gladiator 26, preserver 25, druid 20 (21st needs 6,000,000); two: thief 22, the
rest as before; three: as before. (The thief's 30th is 4,400,000: 2,420,000 + 9 x 220,000.)

Played in the same second game (`:58`, `dbLC`, ravLC), test edits never saved:

| Run | Set | Seen |
|---|---|---|
| 1 | Gerakis fighter 20, Ar'Anda preserver 20 at 5,625,000, Thy'rokh psionicist 20 at 5,600,000 | each **four levels** from the one award: the game's hold (XP to 3 levels on) cut the XP to 24th's (fighter 4,000,000, preserver 5,250,000, psionicist 4,400,000); fighter 24th THAC0 -3; "Gerakis is 21th level Fighter" (the build before LV_ORDINAL) |
| 2 | Gerakis fighter 26 at 5,600,000, Ar'Anda preserver 21 at 5,625,000, Thy'rokh psionicist 23 at 5,600,000, her 34 powers all marked known | **fighter 30th** ("Gerakis is 27th ... 30th level Fighter"), XP 5,500,000, THAC0 -9 (View Character "THAC0: -9"), saves 3/5/4/4/6, base HP +3 a level (123 to 135); **preserver 25th**, XP 5,625,000, THAC0 12, saves 8/3/5/7/4, HP +1 a level; **psionicist 27th**, XP 5,600,000, THAC0 7, saves 8/4/7/11/5, HP +2 a level; View Character no next XP for all three |
| rest | `ravager-roost`, Ar'Anda preserver 25, Thy'rokh druid 25, Terrannus cleric 30 (dead in the save), a night at the Roost | casts left: the preserver's **5 5 5 5 5 5 5 5 5** (10th 0), the druid's 9 9 8 7 4 2 1 (6 6 6 6 4 2 1 and WIS 19's); `slot_count` 18 |
| control | run 2's edits, RAV_SKIP the level cap's nine patches | no level up (the game's 15th); XP held by XP_NEED's past-20 answers still (fighter 5,500,000) |

- **CHOOSE A SPELL from 20th opens on LEVEL 10**: the sequel has four 10th-level wizard spells (Dome of
  Invulnerability, Magical Plague, Rift, Wall of Ash; DS:0656h's starts 111-114) and the window opens on level / 2.
  The owner's slots leave the 10th column out, so a pick there has no slot: an open question for the owner.
- **The psionicists' pop-up** with every power known lists them still: each pick raised power 1's number (its
  byte 2 to 14: six picks over four levels). Nothing breaks.
- **Messages**: a preserver's and psionicist's "gains a level" (the long message over 29 characters).
- Screenshots: `level-30-view-gerakis.png`, `level-27-psionicist-25-preserver.png` (the project's `ravager/`).

## Gaps

- An XP award from a script that doesn't run the level up (95820h) isn't held until the next level up: not
  checked which awards run it (the fight's does).
- The game's dwarf/halfling CON bonus to saves tests the group (CX) for 1 or 4, so it goes to the warrior
  group's saves only: kept as the game's (SL's the same).
- SL has the same saves bug (87844h): for later.
- Not played: a ranger past 15th (the slots and the casting level), the transfer's XP hold, "21st" in a
  message (all covered by the tests); a cleric's slots past 20th after a rest (Terrannus was dead in the save).
