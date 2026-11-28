# Mines 3 worktables, the floor safe and the forge throne in play

Compared the previous furniture package (7345dc35) with the revised one in DOSBox through the Loader. Each trip used a private copy of the Roost save and Reyhan’s travel fixture with the specified region sector and its camera bounds. Figure redraws were enabled in both builds. The eight affected pictures still matched the original game before this change. The worktable comparisons and quest screenshots are native game views. The whole maps and the Shattered Lands reference are renders of the placed scenery.

## Five worktables

| Object and location | Pictures | World position of first piece | Party square | Sector |
|---|---|---|---|---:|
| Long table running front to back | 3766, 3767 | (1407, 994) | (91, 63) | 4 |
| Crystal table to its east | 3770, 3771 | (1503, 996) | (91, 63) | 4 |
| Vials and tubing behind the front wall | 3772, 3773 | (1727, 837) | (108, 48) | 4 |
| Second vials and tubing table | 3772, 3773 | (1936, 1014) | (121, 63) | 4 |
| Empty southern table | 3774, 3775 | (1508, 1444) | (93, 91) | 2 |

The four horizontal tables share a 48-row drawing height. Their visible height now measures 43 pixels. The long table uses 48 rows from the rear piece and 38 from the front. Resampling the lower 16 rows of the combined 86-row surface gives 81 visible rows. Its bottle crosses the original boundary. Independently lowering both drawings would separate the bottle. All five tabletops moved five rows toward their feet. The vessels painted onto the tables retained their original pixels. Each piece matched its expected origin in both builds, including the pair at the front wall. All eight pictures keep their original canvases, drawing order and map positions.

[Five placements before and after](../../reports/ravager-furniture/mine-five-worktables-live.png) · [Gedron at the same magnification](../../reports/ravager-furniture/mine-lab-worktable-comparison.png) · [Whole mine maps and the reference area](../../reports/ravager-furniture/mine-worktable-whole-maps.png)

## The Inquisitor’s safe

Object 5104 uses picture 1138 at (1610, 828). From sector 4 square (102, 50), inspect the safe. The test trip supplied the real Inquisitor’s key, object 3138, through the game’s inventory command. Choose “Use the Inquisitor’s key.” The lock turns, the party finds an unusual triangular key and a vial of greenish gas, and the game awards 5,000 experience. Using the opened safe again says that nothing is left.

Captured the whole unlock and matched all three frames above the foreground wall against the installed art. The second frame extends the four clamps. In the third, the lid lies in front of the opening. Its bottom extends 12 pixels below the safe’s floor anchor and the wall hides part of its lower edge. A trial that compressed the base thinned the keyhole on the detached lid. The original art preserves both the keyhole and the mechanism’s changing footprint. [Closed, unclamped and open in DOSBox](../../reports/ravager-furniture/mine-inquisitor-safe-live.png)

## Promere’s Hammer

The seated skeleton and the forge throne use objects 5156 and 5157, pictures 2962 and 2963, at (474, 59) and (474, 94). Their two drawings meet at the hammer. The figure catalogue lists both as screened originals. From sector 12 square (29, 7), Look at the skeleton and select the green hand on the Throne card. During a fresh encounter its fingers locked around the hammer and the game announced that the statues began to move.

A separate visit supplied the release encounter’s story flags 257 and 259 before arrival. The fingers released the hammer, the game confirmed its recovery, and the party received the 100,000 experience message. The level-up screens then covered the lower part of the throne. To compare the final pose at the original camera position, a second private replay returned immediately before the experience distribution, after the native hammer handoff. GPL 93 advanced both pictures through their own scripts. The hands are empty in both halves of the final pose. The guardian combat itself was outside this staged check.

## The kettle and four winged statues

The kitchen soup kettle at (1296, 1438) is picture 3343, object 5098. Revisit sector 2 at (82, 90). The red contents, ladle and glowing burner stand apart. Look offered “Try the soup?” Chose No. The pot and gas vial yielded no drinking water in these visits.

The two northern statues use picture 3740 at (736, 87) and (880, 88), visible from (50, 7) in sector 3. The two on round plinths use 3739 at (1057, 591), seen from (67, 38) in sector 7, and (400, 1469), seen from (26, 93) in sector 10. All four matched their installed drawings at every opaque pixel. Their tall silhouettes and plinths distinguish them from seats. [Forge throne before and after release, kitchen kettle and all four statues](../../reports/ravager-furniture/mine-forge-and-statuary-live.png)
