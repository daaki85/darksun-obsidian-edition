# Mines 2 storage, miners and rail equipment

All 25 listed placements in region 039h were compared in stock and Obsidian Edition. Keep the current heights. At map scale the walkways, tracks and rock openings have the same outline. The clearest change is in the western storeroom, where the sacks and both barrel lids remain distinct in the shortened pile beside the crate. Gedron in Shattered Lands gives a comparison for the proportions of grouped containers.

[Whole maps](../../reports/ravager-furniture/mines2-whole-maps.png) · [Storage and miners](../../reports/ravager-furniture/mines2-storage-and-miners.png) · [Rail and elevator controls](../../reports/ravager-furniture/mines2-rail-and-elevator.png) · [All 25 placements](../../reports/ravager-furniture/mines2-placements.csv)

## The seven storage placements and three miners

Four crates, two storage piles from the figure redraw and one barrel-and-sack pile account for the seven storage placements. The latter already uses 82% of its original height. For an unobstructed view of it, place the party southeast of the pile at square (11, 20). The nearby redrawn pile is a separate picture.

The two tunnel openings use picture 2479 at (431, 1073) and (374, 1116). The redraw changes the miner inside each opening and preserves the surrounding rock. Picture 3613 at (535, 1138) includes the miner and his pick. Recorded consecutive native frames and compared the two stored poses using their individual script anchors. The stock and mod screenshots on each side of a figure comparison show the same pose. Compare the helmet and shoulders in the tunnel mouth, and the pick and body silhouette on the open floor.

## Thirteen whistles and two winches

Pictures 2510 through 2521 are ore-car whistles. Picture 2510 occurs twice. All twelve object IDs, 5815 through 5826, use the same call in GPL 287. The operator’s dialogue in GPL 295 explains that he sends a car when he hears a whistle. At square (23, 9), the game identified the fixture as “Whistle” and accepted Use. The capture verifies its resting pose. The two other stored whistle frames and arrival of an ore car were not confirmed in play.

The western and eastern winches share object 5802 and picture 3733. From square (8, 12) the western Use attempt reported that the party was too far away. From square (121, 9) at the eastern winch, Look identified the cable wound around the drum. Use brought the elevator platform into the shaft. Look then described the cable as played out. Using the winch again removed the platform and restored the wound-cable description. GPL 268 updates the winch and elevator parts 5835 and 5836 together.

## How the comparisons were made

Private DOSBox runs started from the Roost save through the Loader with autosave and quick save disabled. The stock control used the shipped figures and region placements. The mod used the current branch art. The placement census used fixed cameras and suppressed unrelated regional events. The winch check kept the native winch callbacks, and the whistle was also checked with the regular region script. The whole maps and Gedron views are renders. The Ravager close-ups and control panels are game captures.

For each side, the CSV records an aligned camera, the displayed frame and the count of matched visible reference pixels. Foreground scenery is excluded. Each of the 25 placements had a capture with all its visible reference pixels matching the installed picture to DOS palette precision. No usable drinking-water source was identified in these rooms. The figure-pack and startup tests with both games installed passed 29 tests and 30 subtests.
