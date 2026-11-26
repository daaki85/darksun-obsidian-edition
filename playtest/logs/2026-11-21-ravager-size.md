# Test log: creature size, Wake of the Ravager (2026-11-21)

Under test: DSCLOG2's SIZE (Weapons and armour, RULE_HI_SIZE 4000h): a weapon's AD&D large dice on a
large target (SIZE_DICE, from CAH_SWING at 5D052h, on the call's first swing), Shillelagh's 1d6+1 on a
smaller one, Hold Person (30, 136) and Charm Person (2) leaving a large target alone (SIZE_SPARED, in
PROBE_SAVE), and the cahulaks' tangle sparing a large target (IS_LARGE in CAH_HIT). Who is large: the
helper's LARGE_BITS (66 bytes, header +1842 in the segment at +1834), written by the dice log from
sizes.py's table (sizes.Large, in RavDiceLog's pass after the rolls), the sequel's monsters in
sizes.RAV_NAMES, a people's size its race's (half-giants large).

## In the game (ravhold.sh, RAV_LOADER=1, about 11:00 UTC)

The Draxans' ambush in Tyr, Ar'anda taught Hold Person (ravhold.sh's test edit), the dice log with
0xE0008205. The Draxans are people (a race 1 to 8), so medium by the rule: for the test the dice log's
`sizes.large_by_table` was made to answer yes for "Draxan" (a test edit in the dice log's process, not
the game's). The four given 250 HP (test edits; DOSBox stopped after, nothing saved).

- **LARGE_BITS** read back from the helper, before the test's change: `08 00 00 32`, combatants 3
  (Gerakis, a half-giant) and 25, 28, 29 (the three Giant Skeletons further up the street). After it:
  `08 00 a0 3e`, the Draxans 21, 23, 26, 27 too. So the combatant numbers are the game's table at
  (load+3F49h):0C33h, the one DSCLOG2 reads.
- **Hold Person** before the change (a Draxan medium): "saving throw vs Hold Person ... d20 total 17,
  needs 13 -> saved", the game's own. After it: **"Draxan is too big for Hold Person -> unaffected"**.
- **Large dice** with Computer Control for all four: 15 hits on a Draxan in about two minutes, every
  weapon hit with the rule's dice and the log saying so:
  - "Terrannus hits Draxan for 18: 1d12 = [10] +1 weapon (1d12 for 1d8: a large target) +7 STR 19"
  - "Gerakis hits Draxan for 23: 1d12 = [7] +4 weapon (1d12 for 1d8: a large target) +12 STR 24"
  - "Thy'rokh hits Draxan for 9: 1d10 = [1] +1 weapon (1d10 for 2d4: a large target) +7 STR 19" (the
    Gythka's AD&D large die)
  - Thy'rokh's claws (no item) kept the game's 1d4, as they should.
- **On Gerakis** (large by race): a Draxan's Bone Mace (1d6+1) hit "1d6 = [3] -1 bone": the mace's large
  1d6 with the +1 gone (AD&D's footman's mace), right; but the log line has no "(... a large target)"
  note, since the note looks at the dice alone (dicelog.py, SL's too). A Stone Lotulis kept its 2d4: the
  Lotulis has no weapon kind (below).
- No tangle line: nobody had cahulaks in this fight (the tangle shares IS_LARGE, so it isn't a separate
  path).

## Fixed after

- The dice log's note named Shillelagh and the Hammer by SL's item types (28, 30): in the sequel these are
  90 and 95 (DSCLOG2's). apply_layout now rebinds sizes.SHILLELAGH_TYPE and HAMMER_TYPE
  (test_ravlog's test_size_rule_takes_the_sequels_tables).

## The sequel's own weapons (later the same day, about 12:30 UTC)

The game's dice for every weapon type, read from its item types in play, showed SL's kinds wrong for
five of them as well as the twelve with none: the Toothed Club (1d8+2, the club's 1d3 would have made
it 1d3+2), the Flameblade (the spell's 1d4+4, made 1d12+4 as a long sword), the Crystal sword (1d10
two-handed), the 1d6 Axe (48, a hand axe) and the Pick (1d4+1). DSCLOG2's RAV_LARGE now gives them
their AD&D dice (DEVELOPMENT-RULES.md, Creature size, has the table and why). A run with the Draxans
taken for large (the dice log's test patch): "Terrannus hits Draxan for 17: 3d6 = [2 + 6 + 1] +1 weapon
(3d6 for 1d10: a large target)" with a Twohand Sword (his Longsword made type 101 in memory), and
Gerakis's Polearm "2d6 = [5 + 5] +4 weapon (2d6 for 1d10: a large target)". DOSBox stopped after.

## Still to do

- A bonus-only change (the mace's) could say so in the log line.
- Charm Person and Enlarge (an Enlarged target counts as large) not seen here.

Water: none new (the same street as the held-target log).
