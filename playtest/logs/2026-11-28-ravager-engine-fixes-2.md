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
- Hasted and Slowed: unit tests only (test_ravengine: SPEED_HALVES against the speed routine's order). The
  inventory couldn't be opened: the window grab stayed the loaded picture and no click or key reached the game
  after the memory edit (game time went on). Not yet seen in play.
