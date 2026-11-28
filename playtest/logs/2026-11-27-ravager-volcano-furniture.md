# Volcano furniture and the torn red blanket

Played Wake of the Ravager through the Loader in DOSBox. Each visit started with a private Roost save, using Reyhan’s travel fixture to load the native region and its objects. The controls used stock figures, the mod at 06613fc3, and the revised package. The furniture close-ups are native captures. The whole maps and the Shattered Lands references are renders from the installed game files.

## Volcano 1 and Volcano 2

Volcano 1 flag 478 selects the eastern rooms. In Volcano 2 set flag 442 for the northern half and clear it for the southern half. In particular, (10, 42) and (94, 42) belong to the northern half. Entering them with the southern bounds shows the wrong rooms. Compared stock and mod captures using the actual drawn background to locate the camera, then matched each visible picture against its installed palette and floor point. Party members, foreground walls, the interface and the map boundary can obscure part of a drawing.

| Region | In-game coverage | Findings |
|---|---|---|
| Volcano 1 | 25 previously listed placements, four additional set tables, both torn-bed pieces and one turquoise bed | Six shelves, both stocked counters, the dining sets and bedroom. The stock turquoise bed is clipped at the top of the room capture. Its entire lowered drawing is visible. |
| Volcano 2 | All 46 previously listed placements | Fifteen shelves, both counter designs, the loaded dining table, barrel stack, storage piles, polearm stand, and loose furnishings. The top of the northernmost shelf meets the map boundary. |

The round dining tables use two identical stocked pictures, 1321 and 2624, and the empty table 2625. Comparing each stock meal with the bare wood isolates the place settings. They move with their points of contact on the lowered tabletop. The front cup overlaps the central platter. The two share one mask to retain that edge. The cloth and jug on counters 1342 and 2630 stay intact while the lowest 9 and 22 rows respectively take the reduction. The Volcano 1 shop counter at (1554, 1022) stands beside shelf 2631.

In the Volcano 2 southern storeroom the rear barrel, object 10650, moves from (1200, 1392) to (1200, 1400). The open barrel at (1204, 1414) remains the support. The same object stays at (80, 660) in the northern storeroom, where it stands beside the other barrel. The Loader’s region copy changes only the one placement record.

The four stocked shelf drawings 2979–2982 originally lost rows from their contents. The new shelves omit 9, 12, 15 and 12 rows respectively, selected from bare wood or empty space. Their books, flasks, stones, vials and remaining shelf boards retain every original pixel row. The northern glass shelves are visible from (10, 6), the book display from (53, 6), and the colorful small bottles from (52, 15).

[Whole maps and Shattered Lands reference](../../reports/ravager-furniture/volcano-furniture-whole-maps.png) · [Stock, previous and revised close-ups with Shattered Lands](../../reports/ravager-furniture/volcano-furniture-live.png) · [All 21 shelf placements in DOSBox](../../reports/ravager-furniture/volcano-shelves-live.png)

## Shared pictures in the Alliance headquarters

The same designs appear at 14 placements across the two Alliance layouts: five shelves using 2979, four using 2980, two using 2982, two dining tables using 2624 and one stocked counter using 2630. Checked all 14 with stock and revised figures in DOSBox. The northeast book shelf at (1527, 76) is in sector 3. For that visit, set bits 2000h and 0020h of story variable 87h:55h before travelling to (95, 5) or (96, 6). With only 2000h set the camera stops at map row 256 and shows the glass shelf farther south.

## Two-piece bed from the earlier figure redraw

| Room | Head and foot objects | World floor points | Party square |
|---|---|---|---|
| Volcano 1 bedroom | 10788 and 10790 | (793, 959) and (793, 981) | (50, 59) |
| Tyr bedroom | 9435 and 9437 | (1942, 1377) and (1942, 1399) | (121, 86) |

The head is picture 530 and the foot is 531. Before repair both were separately lowered by the figure redraw. Floor showed across the blanket in both rooms. The foot begins 41 rows below the head, so five rows overlap in the stock 68-row bed. Lowering the assembled bed once preserves that overlap, the original floor row and the torn edge. Both revised pieces matched their expected drawings at every opaque pixel in Volcano 1. A party member partly obscured the foot of the Tyr bed. Both blankets meet above the feet. The neighboring turquoise bed, 547, is a single image. [Both bedrooms in DOSBox](../../reports/ravager-furniture/volcano-tyr-torn-bed-live.png)

## Room visits

The squares below reproduce the views. A room can require more than one view, and some pictured objects sit across the camera boundary. These counts describe visual checks of the placed furniture. Scripted use and treasure outcomes were outside these visits.

| Volcano 1 party squares | Volcano 2 north party squares | Volcano 2 south party squares |
|---|---|---|
| (106, 80) | (10, 42) | (75, 88) |
| (98, 60) | (28, 6) | (108, 89) |
| (96, 23) | (119, 36) | (19, 55) |
| (103, 91) | (94, 42) | (42, 75) |
| (53, 75) | (52, 15) | (118, 55) |
| (95, 44) | (10, 6) | (17, 82) |
| (50, 59) | (97, 22) | (119, 72) |
|  | (36, 14) | (83, 91) |
|  | (13, 13) |  |
|  | (16, 25) |  |
|  | (118, 18) |  |
|  | (53, 6) |  |

The additional silver furnishings (2621–2623) and narrow, side-facing shelves (3485–3486) are visible in the two Volcano levels. Their depth and their use against walls still need a separate review. The jugs on the stocked counters are part of the drawing. No drinking-water action was tested.
