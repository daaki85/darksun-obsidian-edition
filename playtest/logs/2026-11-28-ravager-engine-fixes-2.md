# Test log: Shattered Lands' engine fixes in Wake of the Ravager, part 2 (2026-11-28)

Branch claude/ravager-engine-fixes-2. Under test: the creation screen's least scores (least_scores at 6F12Dh),
Hasted and Slowed in the DAM lines (DSCLOG2's SPEED_HALVES; ravlog's SPEED_EFFECTS), a scripted walk a save
left standing (stuckwalk on the sequel's table, 3F49:08A7h).

- Least scores (ravcreation.sh 2: CREATE CHARACTERS, NEW): the overlay's code in memory is the patch's (its
  first 30 bytes found, the game's not). A 7th-level human fighter: a right click on STR took it 18, 17, 16,
  15 and DS:42D4h (the least worked out) read 9 (the game's rule held a fighter's STR at 17); on DEX and CON 3
  (no requirement: the game's were 9 to 14). Screenshot: STR 15 on the screen.
- Stuck walkers (ravload.sh ravager-after-ambush): the table read with objects 15 and 16 walking (order 15,
  script file 147, their places changing). Object 17 (a creature standing at 1880,1176, no script) given
  object 15's entry in memory (order 15, file 147): with ravdice.py (RAV_NO_SAVES=1) running 75 s, the log said
  "Pedestrian walks on (a walk saved halfway had left them standing)" twice and object 17's order was 0 (the
  other a real pedestrian at a stop: its order taken back, its script sending it on, as SL's). No save made.
- Hasted and Slowed (fresh load of ravager-after-ambush, no other edit): Thy'rokh's inventory read "+1 Chatchka
  1D6+3" and "+1 Gythka 1.5x2D4+8". An effect record added in memory (owner 2, Hasted 42): "2x1D6+3" and
  "3x2D4+8". Made Slowed (91): "Slowed" under her portrait, AC 0 to 4, "0.5x1D6+3" and "0.5x2D4+8" (3 halves
  halved, rounded down: 1). The game took input throughout. No save made.
- The input freeze seen in the first try: the stuck-walker test's own memory edit. Object 17 given object 15's
  walk entry froze input within 75 s with no dice log running, the same on the code before PR #315 (530fa354).
  The dice log alone for 75 s on a fresh load: no reset, input fine. A quick save made while the pedestrians
  walked (F5), loaded: they walk on, the dice log 75 s reset no one, and the inventory opened after.
