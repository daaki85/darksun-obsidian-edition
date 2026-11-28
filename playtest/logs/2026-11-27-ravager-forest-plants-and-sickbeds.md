# Forest plants, cup tables and sickbeds

Used the Loader and DOSBox with the figure catalogue enabled in every run. The Roost travel fixture supplied room access. Two objects previously labelled gem tables in the furniture survey have the in-game name “Plant.” The broad plant offers acorns and the narrow one offers grapes. Cleave’s healing scene also revealed a discontinuity between the redrawn occupied bed and the original empty frame.

[Whole Forest and Alliance maps beside Shattered Lands](../../reports/ravager-furniture/forest-plants-whole-maps.png) · [Plants and cup tables at room scale](../../reports/ravager-furniture/forest-plants-and-cups.png) · [Cleave, Snaggle, both chest poses and the harvest prompts](../../reports/ravager-furniture/forest-beds-and-harvest.png)

## Cup table and fruit plants

| Picture | Original visible height | Previous mod | Revised | Placements |
|---|---:|---:|---:|---|
| 628, red cup and grey dishes | 38 | 25 | 33 | Forest (67, 831), Alliance (458, 494) and (1482, 494) |
| 629, acorn plant | 35 | 23 | 31 | Forest (107, 742) |
| 630, grape plant | 33 | 22 | 29 | Forest (307, 538) |

Only the bottom 14 rows of the cup table and the bottom 11 rows of each plant stand take the furniture scale. The front feet stay at the same coordinates, and the fruit, vessels and highlights retain all their source rows. All five visits showed the installed pictures at their intended floor points.

From Forest square (7, 47) or (19, 35), Look at a plant and use the green hand on its item card. The test fixture gave each bush two fruit using game call 49, field 7. Both offered “Pick some?” and named their fruit. Accepting the acorn in this Roost story state produced “The fruit shrivels the moment you touch it.” MAS 1 registers both objects with GPL 38 at offset 3431. Dariya’s harvesting lesson was outside the test.

For the Forest cup table, square (5, 52) puts the camera at (0, 648). Alliance square (26, 32) shows the intact table at camera (264, 416). For the ruined room, set bit 2000h of variable 87h:55h in the travel fixture and jump to (90, 32). If the table falls below the frame, use the private MAS 51 camera call at offset 42 with upper-left square (82, 25) and extent 20 by 13. The matched camera origin was (1312, 400).

## Reviving Cleave

In the previous mod, picture 649 had a 24-row bed frame. When Cleave got up, his bed grew 12 pixels towards the wall. The cure uses the picture of object 1013, the empty bed, at the original anchor. Picture 2574 now uses the same floor row and side rails as the occupied catalogue pose. The correction leaves Cleave’s figure and his dialogue and reward scripts intact.

Use the Forest room fixture with square (52, 10) and camera (720, 56). Put the Hero Flask, object 3212, on clear floor at (54, 9) with game command 37 and give it one dose with call 49, field 7. A flask placed beneath the tent can be obscured by the party. Look at the flask, pick it up with the middle icon and click Cleave in bed. We played through this sequence in both builds. The game displayed “You revive Cleave!” and awarded each party member 5,000 experience points. The revised bed kept its size when Cleave left it. The pool trip and filling the flask were staged.

## Snaggle and the foot chest

Forest object 1013 at (438, 95) also uses the empty bed. During the wounded-Snaggle sequence GPL 48 takes the picture of object 262, picture 2573, from Limbo. Its catalogue artist had redrawn Snaggle and his blanket on the full-height bed. The builder separates the figure from the original bedding, moves it six pixels down intact and puts it on the shorter frame. This treatment is specific to the reviewed catalogue drawing. We staged the original picture-selection call at the Forest placement and compared the empty and occupied states at camera (320, 16). Both have the same frame. The Forest story route leading to Snaggle’s injury was outside this replay.

At Forest (265, 573), object 9130 draws the two-state foot chest below the bed. Looking at the lid from square (17, 36) gave no item card. The Forest scripts contain no registered Use action for the chest. In a private object-file copy we selected the second stored drawing step at startup. The closed lid matched the shipping picture at screen (91, 94), and the raised lid matched at (91, 93) using the step’s own one-pixel offset. The feet meet the same floor line. This was a staged pose check. No chest-opening action or loot was observed.

Autosave and quick save were disabled. No fixture was saved. Neither plant offered drinking water. The Hero Flask can carry water from the Pool of Heroism according to the cluebook. The cure confirms its use on Cleave.
