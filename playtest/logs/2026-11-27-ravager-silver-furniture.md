# Silver furniture and side-facing shop counters

Compared all 31 placements in the stock region tables with before and after captures from the Loader in DOSBox. Both builds used the mod’s figures. The earlier package had no picture or animation override for any of these five furnishings. Four additional visits with stock figures supplied camera-matched controls for 13 placements. The before and after close-ups are native captures. The whole maps and the Shattered Lands examples are map renders at a common scale.

| Picture | Visible height before → after | Volcano 1 | Volcano 2 | Alliance |
|---|---:|---:|---:|---:|
| 2621, silver table | 44 → 29 | 2 | 3 | 0 |
| 2622, silver stool | 30 → 20 | 10 | 2 | 0 |
| 2623, rear silver seat | 25 → 17 | 1 | 1 | 0 |
| 3485, stacked goods on a side-facing counter | 61 → 55 | 2 | 2 | 2 |
| 3486, jug on a side-facing counter | 61 → 55 | 1 | 3 | 2 |

## Keeping the silver pieces together

In Volcano 1 the table is at (1702, 1102). Its rear piece, object 10796, stood at (1703, 1059). The stock rear feet met the top row of the table. Lowering the pictures separately moved the tabletop 15 pixels away from the rear feet. Moving just the rear piece to y = 1074 restores contact. In Volcano 2 the table is at (830, 133), and the seat, object 10594, had a 33-pixel offset from it. Moving the seat from y = 100 to 111 preserves the partial overlap. The front table hides part of the seat’s feet in both builds. All three silver designs keep their original widths. The other tables and all twelve stools keep their map positions.

## Side-facing counters

The upper 43 rows of each 17-by-61 counter move six pixels down together. This keeps the full outline of the jug and the length of the piled goods along the wall. The lower 18 rows compress to 12 and retain the original floor row. The four mirrored placements are Volcano 1 (1465, 998) and Volcano 2 (326, 889), (1625, 911) and (1766, 915). Their ETAB flag includes 80h. Comparing unmirrored pictures to the screen gives a poor match even when the counter is fully visible. The game draws all four reflected horizontally at the original origin.

[Room close-ups and Shattered Lands comparisons](../../reports/ravager-furniture/silver-furniture-live.png) · [Whole map comparison](../../reports/ravager-furniture/silver-furniture-whole-maps.png)

[All 11 rooms, before and after](../../reports/ravager-furniture/silver-furniture-all-rooms.png)

## Reproducing the rooms

Use a private Roost save and Reyhan’s travel fixture. Set Volcano 1 flag 478 for the eastern rooms. In Volcano 2 set flag 442 for the northern rooms and clear it for the south. In the Alliance use the intact layout for the western room and bit 2000h of story variable 87h:55h for the ruined east. Autosave and quick save were disabled. Compare opaque pixels at each placed item against its installed drawing and region palette. Walls, the party and the map interface can hide part of a furnishing. The grey jugs are painted into the counters. This pass checked their appearance, without testing a drinking-water action.

| Region | Party square | Pictures and floor points before the change |
|---|---|---|
| Volcano 1 | (90, 29) | 2622 (1335, 452), 2622 (1383, 452), 2622 (1336, 500), 2622 (1383, 500), 2622 (1432, 501), 2622 (1336, 548), 2622 (1383, 548) |
| Volcano 1 | (99, 64) | 3485 (1465, 998), 3485 (1721, 1023), 2623 (1703, 1074), 3486 (1461, 1078), 2622 (1655, 1093), 2621 (1702, 1102) |
| Volcano 1 | (91, 45) | 2622 (1576, 727), 2622 (1575, 788), 2621 (1526, 795) |
| Volcano 2 | (108, 54) | 3485 (1625, 911), 3486 (1766, 915), 3486 (1827, 939) |
| Volcano 2 | (117, 91) | 2622 (1928, 1545), 2622 (1993, 1548), 2621 (1967, 1556) |
| Volcano 2 | (45, 3) | 2623 (832, 111), 2621 (830, 133) |
| Volcano 2 | (70, 18) | 2621 (1198, 358) |
| Volcano 2 | (13, 54) | 3486 (326, 889) |
| Volcano 2 | (35, 79) | 3485 (697, 1345) |
| Alliance | (36, 53) | 3486 (486, 891), 3485 (680, 918) |
| Alliance | (100, 54) | 3486 (1510, 891), 3485 (1704, 918) |
