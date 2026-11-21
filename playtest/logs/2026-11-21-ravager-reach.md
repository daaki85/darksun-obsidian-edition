# Test log: the polearm's reach, Wake of the Ravager (2026-11-21)

Under test: DSCLOG2's REACH (Weapon traits, RULE_HI_CAHULAKS): a polearm held alone reaches two squares.
INT E9h replaces "mov ax,[bp-1Ch]" at the end of the combatant distance routine (25CDDh); a distance of
2 becomes 1 when a melee test asked (by its way back), the attacker holds a polearm and no other weapon,
and no wall is between.

## Found first

- **The distance routine**: 1D40:35EFh (file 25BEFh; SL's 1A0A:2BA5h, 22045h): [BP+6] the attacker,
  [BP+8] the target, the result in [BP-1Ch] (SL's [BP-16h]). The UI's callers use the real segment
  (`9A EF 35 40 1D`), the overlays' the selector C8h, which the overlay loader rewrites in memory.
- **Its melee callers** (each compares with 1), by the way back as a file offset: the pointer's sword
  20617h, the attack pointer's click 1EADCh, the walk arrow's click on a foe 1E2AAh, the walk to attack
  arriving 1FF39h and 260CBh, the step switch's case 2420Ah; the computer's, in the combat overlay
  (5A920h): the target's distance against the weapon's range (IP 14A2h, 5BDC2h) and the target found
  in range (IP 1A72h, 5C392h). SL's code around each matched byte for byte but for the segments.
- **The line test**: 0B0Bh:00A4h (10354h, SL's 898:00A4h), the same arguments; the map things' feet at
  DS:67C5h/67C7h, 25h bytes a thing (SL's 669Dh, 20h).
- A creature's item lists are things 201h and on in the combatants' table, so the hands' scan must go
  past 400 (the first try stopped there and found no polearm).

## In the game (ravhold.sh, RAV_LOADER=1, about 14:00 UTC)

Gerakis's right-hand weapon (item 13) made a Polearm (type 80, 1d10, two-handed: a half-giant may) and
his left-hand Longsword (item 14) a shield type (91), the four given 250 HP (test edits; DOSBox stopped
after, nothing saved). The dice log with 0xE0008205. A debugging build recorded each distance-2 call's
way back.

- On Gerakis's turn he walked two squares off the Draxans (the walk arrow), then the sword pointer on a
  Draxan two squares away: before the hands' fix "no", after it the sword. A click: "Gerakis attacks
  Draxan with Bone Dragonsbane +4 (1d10+4): ... HIT ... hits Draxan for 25", twice, and he didn't move.
  The pointer's test came back from 18C9:2787h (file 20617h), as found.
- Under Computer Control the computer's range test (IP 14A2h, the overlay loaded at 57E2h and 5AA0h
  above the load) came with distances of 2 for everyone; the helper's count of reaches rose by one
  more. Other distance-2 callers (IP 024Fh, 1976h: the computer's moves, a spell) kept 2.
- The build without the debugging (the one committed), once more under Computer Control from the
  fight's start: the helper's reaches 1, 2, 3 in the first 45 seconds, Gerakis's five swings with the
  polearm in the log, no hang; DOSBox stopped after.

## Still to do

- A wall between (REACH_LINE's "no") not tried; nor the walk arrow's click on a foe two away.

Water: none new (the same street).
