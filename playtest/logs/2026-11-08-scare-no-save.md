# 2026-11-08: Scare's saving throw, in DOSBox

Under test: whether a creature targeted by Scare (spell 21) ever rolls a saving throw. The code
says its record's save byte is A0h (no save allowed), so the save routine (79A71h) answers
"not saved" at once and nothing rolls.

## Steps
1. `toalarm.sh`: pens-after-scar loaded, Cilla's thief level raised in memory, the party at the fire room (1832,856).
2. Cermak (preserver) taught Scare in memory (the known-spells byte for spell 21; never saved).
3. `restalarm.sh`: rests until Kurzak calls, then waits him out: the alarm fight (every guard in the
   region a combatant, templars across the map too).
4. Turns passed (a click above the member's figure for its END menu, checked by the screen
   changing, then E: /tmp/playtest/passto.sh) to Cermak's.
5. Cermak's first try: the USE screen (24,17) showed the level-2 icons crossed out and clicks on
   them did nothing; RETURN TO GAME then a click on the map walked him (Move 0). Next round the
   icons were plain: a click on Scare closed the screen and gave an aiming pointer with the range
   drawn as a ring; a click on an Arena Guard cast it.
6. Result: `Cermak gives Afraid to Merzol` (a 7th-level fighter), `... to Gladiator` (3rd), and
   `Afraid on Cermak` (the caster, inside the area): **no saving throw rolled for anyone**. The
   game's own rule (6th level and up always save) never ran: confirmed.
