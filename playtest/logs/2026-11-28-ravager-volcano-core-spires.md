# Volcano Core spires in DOSBox

The Loader used the current Obsidian Edition figure pack with the game files installed. Testing started from the Roost save. The travel fixture took the party to Volcano Core (3Fh). Autosave and quick save were off. We used separate private installations for the distributed art, the original picture control and the shorter trial.

[Whole maps](../../reports/ravager-furniture/volcano-core-spires-whole-maps.png) · [Matched DOSBox views beside the Shattered Lands Lava Rift](../../reports/ravager-furniture/volcano-core-spires-live.png) · [Per-placement measurements](../../reports/ravager-furniture/volcano-core-placement-check.csv)

## Which height works here?

| Picture | Placements | Shipped height | Trial height |
|---|---:|---:|---:|
| 1376 | 36 | 60 px | 40 px |
| 1377 | 45 | 63 px | 42 px |
| 1378 | 47 | 54 px | 36 px |

All three shipped pictures match stock, have one frame and have no animation script. The trial ran the existing furniture scaling function at 0.66 on just these pictures. Their feet kept the original coordinates. The shorter rocks expose more of the lava and more of a party member behind them. At the eastern crossing and central ridge, this also breaks up the high outline that identifies the bank. Keep all three at terrain height. In Shattered Lands region 1Bh, the 56- and 58-pixel rock arches stand above the lower outcrops along the Lava Rift.

## Placement checks

We visited the eastern crossing at square (88, 24) with the regular region script. For the full census, private camera fixtures held the view in place and suppressed the eruption and encounters during the captures. Each object remained at its shipped position. The checks use the camera visible in each capture, which can differ by eight pixels from the requested origin. The moving lava is a poor camera reference. Align the terrain first, then compare the spire silhouettes at nearby eight-pixel offsets.

For each object we compared its visible opaque pixels, accounting for mirroring and foreground overlap. We revisited the two spires near the screen edges from different angles. Across the captures, every visible pixel of each of the 128 placements matched the installed drawing to DOS palette precision. The CSV gives a verified camera for each placement. The current and trial close-ups use the same camera positions. The whole maps and Shattered Lands references are renders.

## Seven collapsible rocks

The 128 recurring spires use separate object records from seven visually similar rocks in the ambush area. MAS 63 registers the attack handler in GPL 188 at offset 1209 for objects 5035 through 5041, pictures 1383 through 1389. The shorter trial leaves all seven pictures and their scripts intact. In a separate private check we dispatched the existing handler on object 5035 and saw the debris-hit message. That invocation alone did not demonstrate the rock disappearing after a player attack.

No drinking-water source was identified along the channels. The figure-pack and real-game startup tests passed with both games installed (29 tests and 30 subtests).
