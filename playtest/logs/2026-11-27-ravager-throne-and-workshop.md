# Tantris’s vacated throne and Ikibod’s workbench

Used the Loader through DOSBox with a private copy of the Roost save and the Reyhan travel fixture. Ran the stock pictures control with `RAV_SKIP=figures`, the figure package from `6fb9ef77`, and the repaired package. The two rooms were reached directly. No save was made after a jump.

## El’s Temple

Square (64, 13) puts the party between the six braziers with Tantris seated at the head of the aisle. In the stock and furniture captures the opening camera origin was (872, 112). Both rows of three bowls line up with the same floor tiles. The lowered pictures match all six placements in the game. The exposed smoke retains its original height. [Temple maps and Shattered Lands brazier hall](../../reports/ravager-furniture/el-temple-maps.png)

Used Look on Tantris at screen (154, 29). His warning opened the dialogue view. Advancing it replaced the seated figure with the empty throne and brought his standing figure into the aisle. The game then reported that the halfling prisoners escaped. The playtest ends at that transition.

| Build | Occupied picture origin in dialogue | Empty picture origin in the same view | Visible empty seat height |
|---|---|---|---|
| Stock Ravager | (131, 54) | (168, 112) | 51 pixels |
| Previous PR | (131, 54) | (168, 112) | 51 pixels |
| Repaired package | (131, 54) | (131, 54) | 34 pixels |

The occupied picture is 788 on object 562. GPL 256 swaps in object 3530 from Limbo, which uses picture 789. The stock empty object has zero drawing offset. The replacement lands at the tile centre, eight pixels southeast of the seated figure’s placement on each axis. Taking the seated pose’s drawing offset (29, 50) and adding those eight pixels gives (37, 58). Trying just (29, 50) in DOSBox left the empty seat eight pixels southeast. The final offset aligns the drawing and the lower rim. Only the empty drawing and its object offset changed. The party and Tantris’s standing figure can obscure parts of the lower rim. The comparison shows them as captured. [Seated and vacated throne in all three builds](../../reports/ravager-furniture/el-temple-throne-transition.png)

## Mosaic

Square (18, 37) triggers Ikibod’s greeting beside the workbench. Asking about the tapestry and choosing to look around returns the view to the workshop. Matched the room landmarks, the table feet and its bottles between the two Loader runs. Object 227 stands at (294, 567). Picture 1479 supplies the wizard, tabletop, bottles and legs together. The three occupied frames match the idle and raised-vial poses seen in game. Each has 17 clear rows above the redrawn figure, and the feet stay on the original line. The fourth, unattended frame was checked in the built object file. The formula puzzle and tapestry exit were outside this visit. [Whole Mosaic map, Shattered Lands worktable and workshop captures](../../reports/ravager-furniture/ikibod-workshop.png)

No water source was identified in either room during these visits.
