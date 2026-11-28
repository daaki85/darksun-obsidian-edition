# The Mines prisoner, two weapon tables and four polearm stands

Started each room visit from a private copy of the Roost save with autosave and quick save disabled. A staged Reyhan jump loaded the region, its original objects, and its native interaction scripts. The control used stock Ravager pictures through the Loader’s figures switch. The revised build used the packaged Obsidian Edition pictures. The foreground party member can obscure the feet when standing against a fixture. For the comparison of the prisoner, the party stands a few squares to the west.

## Mines 3 prisoner

Revisit RGN03A in sector 4 at (120, 14), with the camera bounds from GPL 96. Look at the occupied rack and choose the green hand on the item card labelled “Rack.” Answer Yes when the prisoner asks for help. The first message names the rescuer, the second awards that party member 1,000 experience. The standing miner thanks the party. Choose “Good luck. I have to go.” and dismiss the message about the miner disappearing into the corridor.

In both builds the room script called GPL 86 at 4020. At 4275 it changed object 5064 to the empty rack picture supplied by Limbo object 5065. A longer capture from (116, 14) shows both idle head positions with the party clear of the restraints. Its drawing origin stayed at world (1936, 177) through the change. In the matched rescue visits, all opaque pixels of each empty rack matched its packaged drawing at screen (208, 49) within VGA colour conversion tolerance. The loose restraints are visible after the miner departs. This was a staged visit past the laboratory guards. [Stock and redrawn racks through release](../../reports/ravager-furniture/captive-rack-live.png)

## Weapon tables and Yuan-ti vessels

Mines 3 sector 6 at (51, 46) shows the first table. The Yuan-ti tunnels at (19, 66) show the second. In both art sets the weapons cross the join between pictures 2794 and 2795. The figures switch exposes the difference in table height. In DOSBox, both halves matched their individual bitmaps across all opaque pixels at both placements. The upright weapons nearby belong to a separate floor stand.

In the Yuan-ti tunnels, (84, 23) brings the jar and both bowls into one view. The current 82% height retains the rim of the grey jar and the light edges around the turquoise and blue contents of the bowls. Their use as drinking water was untested. No rest-water source was identified in the Mines rack rooms or at the Volcano 2 stand. [Matched table and vessel captures](../../reports/ravager-furniture/weapon-tables-live.png)

## Upright polearms

Picture 2796 is shared by four separate objects. A uniform reduction made the broad upper axe heads look flat. The selected version keeps the top 16 rows intact and shortens the lower 43 rows at the Tyr scale. The visible drawing is 58 × 45 game pixels, down from 58 × 59. The picture keeps its original canvas and anchor. The freestanding rack beneath Teaquetzl in Shattered Lands (Subterranean Temple, region 2D, object 2252, picture 2010) is 29 × 37 game pixels. It carries lighter weapons and is shown at the same enlargement.

| Area | Stand object | World position | Party square for the capture |
|---|---:|---:|---:|
| Mines 3, beside the weapon table | 10346 | (755, 727) | (51, 46), sector 6 |
| Mines 3, southern room | 10356 | (710, 917) | (47, 59), sector 9 |
| Yuan-ti tunnels | 9880 | (405, 1016) | (23, 64) |
| Volcano 2 | 10629 | (223, 411) | (16, 27), northern part of the map |

A plain jump to Volcano 2 loaded the southern camera bounds. For the northern room, set story flag 442 in the private jump before travelling to (16, 27). GPL 210 then selected sector 0 and the northern bounds. In all four revised captures, all opaque pixels of the stand matched picture 2796 at its original drawing position within VGA colour conversion tolerance.

The screen control in the upper left overlaps a few pixels of the original southern Mines stand. The lowered stand clears it. [Four placements and the Shattered Lands reference](../../reports/ravager-furniture/polearm-stands-live.png) · [Whole maps](../../reports/ravager-furniture/rack-whole-maps.png)
