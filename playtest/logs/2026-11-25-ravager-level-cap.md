# Test log: the level cap by XP in Wake of the Ravager (2026-11-25), paused before the play

Under test: DSCLOG2's LEVEL CAP BY XP (sites 110-117, RULE_LEVEL_10 now in ravager.RULES_PORTED) with the owner's
cap of 5,625,000 XP shared between a character's classes; XP_HOLD (XP held at the share); a thief's d6 to 10th
(the psionicist's stays 9th); the Player's Handbook's saves (SAVE_BASE, RULE_HI_TABLES); THIEF_TABLE to 17th; a
druid's slots flat from 15th and a ranger's the Handbook's (ADND_SLOTS); a ranger's casting level at most 9; the
party transfer's XP held at Shattered Lands' share. The owner's tables (thief skills 1-17, ranger 1-20, druid
slots, the hit dice) came through the coordinator: rows 1-13 of the thief table match THIEF_TABLE and DSCLOG's.

## Done (no play yet)

- Static research: RESEARCH.md's "The level up, the XP table and the saves in the sequel".
- Tests: tests/test_ravlevelcap.py runs every new site in an emulated CPU (LV_UP against ravager.level_room for
  1-3 classes at levels 1-20, the owner's highest levels, a human dual-class, View Character, the clamp and
  XP_NEED's "most", XP_HOLD, RAV_XP_AT against tables.RAV_XP, the thief's and psionicist's hit dice, the saves
  against tables.rav_saves at levels 1-24, XP_SUFFIX's " F)"); test_tables.py the slot, saves and thief tables in
  DSCLOG2 and DSCLOG; test_ravtransfer.py the transfer's XP hold. All suites pass (pytest with DSUN_WOTR: 2685
  passed; unittest discover OK).
- DSCLOG2: 47072 bytes (45168 before). Upper memory free: not measured (no play); the last measure was about
  113,000 bytes free after a 42,000-byte DSCLOG2, so about 111,000 should be left.

## Not played (the usage limit; the DOSBox lock came only as the session paused)

The plan, with `files/2026-11-25-ravager-level-cap-start.sh`'s steps (RAV_LOADER=1 ravstart.sh on a copy `/tmp/playtest/ravLC`,
ravdice.py attached, the opening talk to the Draxans' ambush), then `ravlevel.py set` before the fight's XP:
- member 3 a fighter 17 at 3,000,000 XP: expect 20th, saves 3/5/4/4/6, no next XP on View Character;
- member 0 a fighter/cleric/thief 14/15/17 at 4,000,000: expect 15/16/18 and the XP held at 1,875,000;
- member 1 a human fighter 17 who was a cleric 20, at 3,100,000: expect 19th (share 2,925,000), XP held there;
- member 2 a thief 9 at 155,000 (+ the award): expect 10th with a d6 in the dice log;
- a control with RAV_SKIP=level_cap_up,level_cap_view,level_clamp,xp_suffix,thief_hd_roll,thief_hd_con,
  thief_hd_clamp,save_table.
The watchdog (guard_start.sh) wasn't to be started: its pid file is shared, and starting it kills another
agent's.

## Gaps

- An XP award from a script that doesn't run the level up (95820h) isn't held until the next level up: not
  checked which awards run it (the fight's does).
- The game's dwarf/halfling CON bonus to saves tests the group (CX) for 1 or 4, so it goes to the warrior
  group's saves only: kept as the game's (SL's the same).
- SL has the same saves bug (87844h): for later.
- The druid's XP: the owner's High Level Campaigns table (2,000,000 at 20th) differs from RAV_XP's (5,500,000);
  RAV_XP kept, the owner asked.
