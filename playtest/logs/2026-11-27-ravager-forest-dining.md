# The eight Forest dining tables

The Forest inventory contains 60 placements. The northern dining groups account for 38 of them, including eight main tables, seven little tables with a cup or jug, one bare little table and 22 seats or benches. We compared all 38 placements in DOSBox. The remaining 22 were also located on screen, including picture 649, Cleave in the redrawn sickbed. His occupied pose was present. The healing quest and the foot chest's opening were outside these room checks.

[Whole Forest and Gedron maps](../../reports/ravager-furniture/forest-dining-whole-maps.png) · [Original furniture, previous squash, revision and Shattered Lands](../../reports/ravager-furniture/forest-dining-live.png) · [All eight tables in DOSBox](../../reports/ravager-furniture/forest-dining-all-eight.png)

## What changed

The first pass reduced the wood and everything painted on it to two-thirds of its height. The Forest’s broad red pitcher, shallow dishes and small jugs lost their silhouettes. The revised package keeps all 15 dining drawings on their previous canvases. It changes only the four loaded table designs (567–570) and the two loaded side tables (572–573). The bare table and side table supply the wood behind each setting. On the two broad tables the benches are part of the same drawing as the wood, and their lowered pixels remain the same. Touching dishes on the crowded table move together. Seven main tables and seven side tables show the change.

Full-size vessels hide more of the chair backs if all seats stay at the previous placements. We tried that version in play, then checked the following three changes with a second native visit. The other eleven seat adjustments from the first pass still apply.

| Chair floor x | Original y | Previous squash y | Revised y | Table floor point |
|---:|---:|---:|---:|---|
| 1166 | 133 | 143 | 138 | (1166, 161) |
| 1234 | 177 | 189 | 183 | (1241, 212) |
| 1897 | 121 | 131 | 127 | (1898, 150) |

The eastern rear chair has about 73% of its opaque pixels visible in the original room, 45% in the first full-size-vessel trial, and 72% after repositioning. At (1383, 184) two scenery pieces overlap the horizontal bench. All 108 exposed bench pixels in the original furniture and all 72 exposed pixels in the revision match their drawings. The hidden middle is also hidden in the stock layout.

## Reproducing the views

Use a private Roost save, the Loader and the Reyhan travel fixture for Forest region 01h. Disable autosave and quick save. A plain jump can show trees even when the destination is a room. In the throwaway script copy, have the arrival entry in GPL 48 set the viewing rectangle with the Forest's native call 33 and center the view using its call 38. For an origin (col, row), use col × 1000 + row and 20013 for the bounds. A matching background confirms that the correct room was loaded. The table lists the actual camera origins recovered from the captured scenery.

| Party square | Camera in pixels | What to look for |
|---|---|---|
| (35, 13) | (416, 40) | Green-rug pair, tiny jug to the northwest, grey bed |
| (59, 12) | (800, 40) | Small side tables and the edge of Cleave’s room |
| (74, 12) | (1040, 40) | Three set tables, including the crowded pitcher table |
| (88, 12) | (1264, 40) | Table at (1495, 151) and the bench behind hanging cloth |
| (104, 12) | (1520, 40) | Table at (1706, 162), rear bench and side chair |
| (117, 12) | (1728, 40) | Eastern table with the two jugs and rear chair |
| (9, 10) | (0, 8) | Three barrels in the northwest |
| (9, 38), (19, 38) | (0, 456), (160, 456) | Western storage, bed, foot chest and narrow gem table |
| (9, 50), (19, 50) | (0, 648), (160, 648) | Two furnished western rooms, the cup table, the broad gem table and the other beds |
| (54, 13) | (720, 56) | Cleave’s occupied bed in full view |

All three dining builds kept the figure redraw enabled. The original-furniture control restored only Forest pictures 567–581 and the 14 corresponding seat placements. We checked the previous squash separately. The package comparison against the previous mod found six changed bitmap chunks and three changed destination coordinates. Every other catalogue chunk, animation, object assignment and region placement matched. [Other Forest room captures](../../reports/ravager-furniture/forest-room-survey.png) show the occupied bed, the cloth over the bench and the two gem tables. The six additional room visits used the previous mod. All 22 furnishings outside the dining set have identical art and positions in the final package.

The close-ups and the eight pairs are native game captures. The whole maps and Shattered Lands references are renders. The southern checks turned up two gem tables (629 and 630) and a separate cup table (628) worth comparing before the Forest is closed. The cup table also appears twice in the Alliance headquarters. Jugs were visible on the dining furniture. No drinking or refill action was established.
