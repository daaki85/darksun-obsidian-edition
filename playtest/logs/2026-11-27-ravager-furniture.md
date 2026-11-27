# Ravager furniture in Tyr

Used the Loader from the all-area furniture branch and the after-ambush save on a private copy of the game. The displayed DOSBox surface was 640 × 480. The original game view is 320 × 200. Compared the output with the branch’s built OBJEX2.GFF and registered the camera against the Tyr map using street edges and room details.

1. Loaded the save and saw the freestanding shelf through the east wall of the starting street. The memory-assisted load clicks were unavailable in this environment. Pressing L on the title screen and Return on the slot screen loaded the highlighted after-ambush save.
2. Walked south of Shadow Square, then north to Notaku. From the customer’s side, both curved halves meet at the same floor line. The teal area behind the display is the floor of the stall. The merchant stands visibly behind it and the merchandise is visible across the front. This check covered the assembled stall at rest.
3. Walked north through Tyr to the red-carpeted room on the east side of the street. Its purple chair 2590 at (1341, 238) renders at the new height. At the 419 pixels where the original and new room renders differ around the chair, mean absolute RGB error against the game was 3.9 with the new picture and 55.7 with the old one (0–255 channel values).
4. Read the built OBJEX2.GFF, decoded all 64 frames of the 61 new picture resources, and compared every row with the bottom-anchored 0.66 sample from the stock files. All 217 placements produced a change in their map renders. The other regions and the openable fixtures were checked offline.

[In-game images](../../reports/ravager-furniture/tyr-live.png) · [Room and whole-map comparisons](../../reports/ravager-furniture/README.md)
