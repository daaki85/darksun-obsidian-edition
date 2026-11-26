# Test log: Turn Undead AD&D's way, Wake of the Ravager (2026-11-21)

Under test: DSCLOG2's SITE 15, TU_SITE (SL's turn_undead_manual, of "spells and psionics as the manual
describes them"): AD&D's turning table (20 19 16 13 10 7 4 T T D D, then D\*), a d20 against the cell,
turned undead Afraid for 3d4 rounds, a failed priest unable to try that undead again this fight.

## Found first

- **The sequel's turning of one undead** is at 97C50h (SL's 7ADB7h, the same frame: [BP+6] the target,
  [BP+8] the priest, [BP+0Ah] a flags pointer, [BP+0Ch] the priest level, [BP-4] the undead's sheet).
  Its own number is SL's (10 + 3 x (the row less the column), 22 made 20), read from the sheet's +1Eh
  (SL's +24h) at 97C9Ch, the site; the d20 at 97CE9h, the destroy (1000 damage, 598:7Fh) at 97CFCh, the
  failure call at 97D12h, the end at 97D1Bh.
- It is reached through the stub 47C1h:48h from one call, 66184h: the case of **spell 310** (136h) in
  the handler for spells with rules of their own, so the sequel's Turn Undead is spell 310 (SL's 190).
- The undead's Afraid is the sequel's effect 35; the adder is 608h:3Eh (7F9E6h).

## In the game (ravhold.sh, RAV_LOADER=1, the dice log on, about 17:15-17:45 UTC)

Terrannus is the opening party's earth cleric (member 1, class 2, level 7): his USE screen has a TURN
UNDEAD icon under SPELLS LEFT (`ravclick.py 157 145`), which closes USE and puts up a circle on the map
around the pointer; a click turns every undead foe in it. Out of reach (about 100 game pixels) or
behind a wall the pointer is a barred sign and a click does nothing. Test edits (DOSBox stopped after,
nothing saved): the party's HP 250; the Draxans' sheets made undead (race 9): sheet 16 with its own 8
levels, sheet 14 with 2, sheet 13 with 1; later Terrannus's level 9 (scratch tsetup.py, tund.py).

- **First turning, four Draxans in the circle** (the helper's count 4):
  - "Terrannus turns Draxan: d20 = 7, needs 16+ (priest level 7 vs 8 HD, AD&D's table) -> not turned:
    can't try again on it this fight"
  - "Terrannus turns Draxan: turned: flees 3d4 = 6 rounds (Afraid), automatically (T) (priest level 7
    vs 2 HD)"
  - "d20 = 17, needs 16+ ... -> turned: flees 3d4 = 11 rounds (Afraid)"
  - "d20 = 15, needs 16+ ... -> not turned"
  - The effects table after: Afraid (35) for spell 310 from Terrannus on combatants 21 and 27, the two
    turned, and on no other. The 2-HD Draxan walked off into the room to the left on its turn.
- **Second turning, next round** (count 6): a new 8-HD Draxan "d20 = 12, needs 16+ -> not turned", and
  the one that failed before: "Terrannus can't turn Draxan again: failed against it this fight" (no roll).
- **The destroy (D, D\*) not played**: the only undead left in reach were behind walls. Its way on
  (97CFCh, the game's own push of 1000 damage) is read from the code; the failure's and the end's ways,
  worked out the same way, ran.
- No hang, no stray turn: the fight went on as before after each turning.

## Still to do

- A D or D\* in play (an undead of 1 hit die in the open, Terrannus level 7 or 9).
- The dice log names no "gives Afraid" line for the turned (it does in SL); the effect is in the table.

Water: none new (the same street).
