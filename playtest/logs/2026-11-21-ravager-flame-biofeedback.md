# Test log: Flaming Arrow's bolts and Biofeedback's least, Wake of the Ravager (2026-11-21)

Under test: DSCLOG2's SITE numbers 6 and 7: FLAME_COUNT (SL's flame_arrow_count, at the cast's tail
7E8E0h, SL's 7567Fh: "mov dl,[es:bx]", the spell record's count) gives Flaming Arrow (28) one bolt for
every five of the caster's levels, at least one; BIO_LEAST (SL's biofeedback_least, 8348Bh, SL's 79C83h:
"sub si,2") leaves at least 1 of a blow of 2 or less on a creature under Biofeedback (the sequel's
effect 8), as the manual says.

## In the game (ravhold.sh, RAV_LOADER=1, the dice log on, about 18:00 UTC)

Ar'anda taught Flaming Arrow and made a 10th-level preserver with casts left (scratch fsetup.py, test
edits); later the party's STR 8 (creature +19h, sheet +15h) and Biofeedback (8) put on the four Draxans
in the effects table. DOSBox stopped after, nothing saved.

- **Flaming Arrow**: the USE screen, LEVEL to level 3, the spell, a Draxan (the aim must be on a
  combatant: a click on the street does nothing). The first bolt: "Flaming Arrow damage: 5d6 = [1 + 1 +
  4 + 2 + 5] = 13 / Draxan takes 13 ... now 57/70 HP"; then the game put the spell's icon up again as the
  pointer for the second bolt (two at 10th level): "5d6 ... = 16 / Draxan takes 16 ... now 41/70 HP".
  The helper's count 1 (the site runs once per cast).
- **Biofeedback**: under Computer Control, every hit on a Draxan logged its "-2 Biofeedback", and the
  blows of 2: "Thy'rokh hits Draxan for 1: 1d4 = [1] +1 claw -1 Biofeedback", the game's HP "-1" (the
  game's own, not the log's), and the same for Terrannus's "1d8 = [1] +1 weapon -1 Biofeedback"; the
  helper's count up 4 (four such blows). Without the rule these blows do 0.
- The party's STR: creature +19h (STR DEX CON INT WIS CHA from there), sheet +15h; recorded in
  RESEARCH.md's memory edits for the sequel.

## Still to do

- A control cast of Flaming Arrow (no dice log) to see the sequel's own count (one bolt by its record, as
  SL's).

Water: none new (the same street).
