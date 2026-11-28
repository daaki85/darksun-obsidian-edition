# Four split beds and the Veiled Alliance storeroom

Claude’s DOSBox review of PR #265 caught floor tiles showing through the middle of a red blanket. I reproduced the split in the west bedroom. I compared three Loader runs from the same camera position using the stock figures control, the previous PR package and the repaired package. The floor runs all the way across the blanket only in the previous PR. [Three-way DOSBox comparison](../../reports/ravager-furniture/split-bed-and-stacks.png)

## Finding the two pictures

The bed uses pictures 524 and 525 from the existing figure redraw. On the map the foot draws 39 pixels below the head, overlapping the last seven rows. Lowering each towards its own floor left three completely empty rows between them. The repair lowers the joined 68-row drawing once to 45 rows, then splits it across the two original pictures. The feet stay on the original floor line.

I scanned the placement tables in all 20 region files and loaded each of the four beds in DOSBox. Coordinates below are the placement of the head. The foot is directly south by 22 map pixels. In each capture, every opaque pixel of the joined drawing matched the game screen within the 6-bit VGA palette conversion tolerance. The old and stock western beds each matched their own reference at the same screen position. [All four live captures](../../reports/ravager-furniture/split-bed-four-rooms.png)

| Region | Head position | What was visible |
|---|---|---|
| Veiled Alliance HQ, intact west | 55, 423 | Red blanket continuous from the pillow to the foot beside the hide rug |
| Veiled Alliance HQ, ruined east | 1079, 423 | Same join in the eastern bedroom |
| Tyr | 407, 95 | Bed against the wall on the dark tiled floor |
| Mines 1 | 1996, 1340 | Continuous blanket beside the worktable on the cave floor |

The two objects in the original report were neighboring furniture. Object 9536 uses picture 2591, the side-facing red chair. Object 9537 uses picture 2704, the pale table. I reviewed paired stock and branch map renders at all thirteen chair placements (nine in Tyr, four in headquarters) and all six table placements (all in headquarters). The chairs and tables stand on the floor and are independent of the bed. [Nineteen placement comparisons](../../reports/ravager-furniture/alliance-bed-id-review.png)

## Storeroom supports

The western, intact storeroom has the touching barrel stack, the barrels under the sacks and the intact vase on a crate. I captured all three builds at camera origin (472, 1168). With the corrected placements the upper barrels touch their supports, the sacks rest on the barrels and the vase stays seated on the crate as the crate meets the boxes below. The eastern coordinates in the review fall in the ruined layout, which has a separate set of broken crates and pots. [Both layouts on the whole map, alongside the Shattered Lands upper castle](../../reports/ravager-furniture/split-bed-map.png)

## Repeating the check

Started from the private Roost save through the Loader in DOSBox. Used the test travel script to jump from Reyhan to each room and centered the view on arrival. For the eastern Alliance bedroom the travel fixture also selected the headquarters' ruined story state before entry. Reopened the game for the other story state and region checks. The stock control used the same object, resource and region writers as `RAV_SKIP=figures`. The comparisons show native gameplay capture except for the explicitly labeled map renders. No save was made from the travel fixture. No water source was identified in these rooms.
