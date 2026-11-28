# Silt Sea Giants furniture and standing figures

Starting from the Roost save in the Loader’s DOSBox build at b82b5db2, the travel fixture put the party into region 41h with its normal region script and objects. Separate game copies used the distributed figure pack and the original figure and placement chunks. Autosave and quick save were off. No fixture was saved.

[Whole islands beside Gedron](../../reports/ravager-furniture/giants-furniture-whole-map.png) · [Room comparisons beside Shattered Lands](../../reports/ravager-furniture/giants-furniture-live.png) · [Other furniture placements](../../reports/ravager-furniture/giants-other-rooms.png) · [Velden and Generoe](../../reports/ravager-furniture/giants-figures-live.png)

## All twelve placements

Coordinates below are the object’s world-pixel anchor. Heights count visible rows in the original and installed drawings. The listed jump squares give a clear view of the objects in both builds.

| Furnishing | Picture | World positions | Original → mod height | Jump square |
|---|---:|---|---:|---|
| Plank table | 3698 | (456, 636), (281, 1246), (1879, 184) | 57 → 38 | (36, 36), (23, 76), (118, 13) |
| Stump stool | 3699 | (497, 633), (335, 1225) | 27 → 18 | (36, 36), (23, 76) |
| Red chair | 3870 | (482, 529), (639, 649) | 49 → 33 | (36, 36) |
| Footstool | 3871 | (483, 552) | 22 → 15 | (36, 36) |
| Green and purple cloth furnishings | 3442, 3443 | (797, 566), (453, 1259) | 58 → 38, 54 → 36 | (48, 37), (23, 76) |
| Wall-side table | 3695 | (337, 1180) | 34 → 23 | (21, 73) |
| Generoe and his rocker | 3866 | (210, 86) | Settled, 42 → 35 | (15, 7) |

The cameras were (424, 480) for the northwestern village furniture, (616, 496) for the green cloth, (216, 1120) for the southern room, (184, 1072) for its wall table and (1728, 112) for the eastern hut. We aligned the terrain first, then checked the visible pieces at their installed drawing offsets. Nine pieces matched throughout their opaque area to within DOS palette rounding in both builds. The green-cloth piece matched to 99.9%. The eastern table matched across 97% of the original and 95% of the modded drawing. Its position and floor contact were visible. The western table and its stump are separate objects with their own feet.

## The giant in the earlier preview

The static gallery originally drew frame 0 of picture 2469 over the table beside Gilad’s recorded position (500, 602). That frame survives in the redrawn picture bank. The catalogue’s standing slot for the facing shown selects frame 12. Gilad was absent from the table on these Roost visits. His routine in GPL 118 also refers to the farm and the exit at squares (101, 51) and (77, 58).

To check which figure the game actually displays, visit Velden the smith at (22, 57) and Davin the hunter at (91, 32). They share the same standing picture as Gilad. Stock Ravager drew frame 0 and Obsidian Edition drew frame 12 at both native placements. Every opaque pixel of each frame matched the capture. Velden was at camera (200, 816), Davin at (1296, 416). Kiril at (50, 40) showed the corresponding redrawn frame 12 of picture 2470.

A private diagnostic gave Generoe picture 2469. His seated object displayed the retained frame 1 in both builds. A substitute actor can initialize a different pose. The figure comparison uses Velden in his own workshop.

## The rocking chair

At square (15, 7), camera (88, 16), Generoe initially calls out for Drisha. Dismiss his greeting to see him rock at home. The game displayed each of the three occupied frames and their original drawing offsets in both builds. The lowest painted pixel rises three rows in the middle pose in both versions, then returns to the settled position. His green chair, red seat and body move together.

The fourth drawing contains the empty rocker. We checked it at Generoe’s own placement by selecting animation step 8 at startup in a private copy. Its red seat and runners match the settled occupied frame where visible. This checks the stored pose. The story outcome that sends Generoe to Limbo was outside this visit.

Velden’s workshop has blue troughs near him and the anvil. We did not test drinking or filling a container there.

The figure-pack and real-game startup tests passed with both games installed (29 tests and 30 subtests).
