# Test log: preservers' INT at a level up, Wake of the Ravager (2026-11-21)

Under test: DSCLOG2's PICK_ANY, PICK_LIST and PICK_PAGE (SL's pick_any and pick_list, RULE_HI_INT): at a
level up a preserver chooses a spell only from levels its INT has room in (AD&D's most a level: INT 9,
six).

## Found first

- **The level up**: 957ABh calls 688h:66h (93160h) for class 11 alone, and only when the class's level
  passes the best it has reached (the sheet's +39h + the class's place; a level regained gives nothing).
  93160h takes the class level (98h:C1h) into [BP-2] (9317Fh: "mov [bp-2],ax / or ax,ax", SL's 85580h)
  and asks the list routine at each level from it down; a spell found, CHOOSE A SPELL (93378h).
- **The list routine** 94C7Ch (member, a far list, level): the unknown spells of that one level (the
  table at DS:0656h), at most 19, put at 370h:7. Called from 93160h and from CHOOSE A SPELL's page
  (93222h: the level DS:43ECh, the reader 370h:0B44h; "mov di,ax" after it at 93246h, SL's 8563Fh).
- **CHOOSE A SPELL** shows one spell level a page (LEVEL pages 1 to the highest, then round), opening on
  the highest it casts (698h:39h: (level + 1) / 2 below 10th, level / 2 from it; "mov [43ECh],al" at
  93487h). A row with no spell can't be clicked.
- The game's own count from the class level, not the spell level: past 10 it reads the priest rows
  (a 12th-level preserver's "level 12" is priest spells 115-126).

## In the game (ravhold.sh, RAV_LOADER=1, about 15:00-15:50 UTC)

The Draxans' ambush; Ar'anda (preserver 6, 40,000 XP) made 5th with best 5, INT 9 (creature +1Ch and
sheet +18h), her known spells written, the Draxans' HP 5 (all test edits; DOSBox stopped after each run,
nothing saved). Computer Control for all four; the XP box clicked.

- **Control** (no dice log, so the helper's rules 0): levels 1-3 six known each, the game's window on
  LEVEL 3 with eight spells.
- **PICK_LIST** (the dice log attached with that window up): LEVEL to 1: an empty page (the counter
  pick_cut 1); a click where the first spell would be learnt nothing; level 2 made three known: its page
  ten spells; level 3 empty again; a spell clicked on level 2: spell 15 learnt, the window shut.
- **PICK_ANY, all full** (levels 1-3 six each, the dice log from the start): level 6 reached, pick_asks
  1, no window.
- **Room at level 2** (1 and 3 full): the window opened on LEVEL 3, empty (before PICK_PAGE); paging to
  2 showed the spells, one learnt (16). With PICK_PAGE: it opened on **LEVEL 2** with its ten spells;
  the first clicked, spell 15 learnt.

## Still to do

- The dice log has no line for it (SL's hasn't either).
- The game's scroll messages (560h:2Ah) still show nothing.

Water: none new (the same street).
