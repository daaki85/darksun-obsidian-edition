# Test log: an archer's turn ending when the quiver runs dry (2026-11-14)

**Under test:** the user's report that a character's turn ends as soon as its quiver runs out of
arrows mid-turn, when it should still be able to move or ready more arrows.

**Plan:** find where the game ends the turn after a shot with no ammunition left (DSUN.EXE's weapon
attack routine 5883Ah and its ammunition routine 58C8Fh, from DEVELOPMENT-RULES.md), see the
behaviour in a fight (save `fountain-user`, an archer with one arrow and 2 shots a round), fix it in
DSCLOG, and test again.

## Steps
1. Game set up from the user's installer; `fountain-user` loaded; buildcheck OK. Fight started.
2. Found the cause in DSUN.EXE: the weapon attack routine (5883Ah) cuts a shot's attacks to the
   arrows left (5899Ah, "Out of ammo" with none) and, once that cut-down count is made, writes 63h
   (99) to the attacker's +181h (58C45h), which ends the turn (5844Eh). So the turn ends with shots
   still due, and a shot tried with an empty quiver ends the turn with nothing done.
3. Fix: DSCLOG sites AMMO_CAP (5899Ah, keeps the round's attacks before the cut) and AMMO_TURN
   (58C38h, compares a party member's attacks made with the uncut count). Built (70,208 bytes);
   unit tests OK.
4. First play with the fix (fountain-user, every foe Paralyzed, Ester's quiver set to 1 arrow in
   memory before the ambush speech was clicked): she shot the Templar (34/41 left), "Out of ammo",
   and the turn passed. Watched with `turnwatch.py`: +181h went to 1 (not 99: the fix held), but the
   caller (58456h) ends an attack command when its **target is still standing** (creature +1Ch
   Okay), whatever attacks are left: the game's own rule (an attack spends the turn unless it
   kills), not the arrows'.
5. So the arrows' bug is the **kill** case. Templar set to 1 HP (`foeset.py 25 hp=1`), Ester with 1
   arrow and 2 shots: the arrow killed him, +181h stayed 1, **the turn stayed Ester's**, and a walk
   click moved her (872,1528 to 904,1512) on the same turn.
6. Baseline, the two patches left out of a scratch build: the same kill passed the turn to Jenna at
   once (+181h straight to 99, then 0). The fix is what keeps the turn.
7. An empty quiver at the click: the game didn't try the bow at all; Ester walked up and struck with
   her long sword (turn over after the melee, as normal).
8. Unit tests 1905 OK. No save made (memory edits throughout).

## Result
Fixed and checked: an archer (a party member) that kills its target with its last arrow keeps its
turn, as after any kill, to walk, ready more arrows or strike again. Against a target still standing
the turn ends after the shots, with arrows or without: that is the game's rule for every attack.
