# Kalak’s Pyramid furniture in DOSBox

## What to keep

Retain the lowered shelves, tables, chairs, chest, barrels and sandstone furnishings. Keep the two teleportation cabinets at their stock scale. Their closed drawing is 59 pixels tall beside the revised 42-pixel shelves. With the doors open there is room to read the entrance behind them. The same distinction is visible beside the doorway, bench and chair in the Shattered Lands Upper Castle.

[Whole maps](../../reports/ravager-furniture/pyramid-furniture-whole-maps.png) · [Matched eastern room, chairs and cabinet passage](../../reports/ravager-furniture/pyramid-furniture-live.png) · [All placements](../../reports/ravager-furniture/pyramid-placements.csv)

## Placement check

Compared the original Ravager figures with the current Obsidian Edition figure pack from the Roost save in separate Loader installations. Autosave and quick save were off. For the survey we pinned the Pyramid camera in temporary copies of the region script and suppressed the remaining entry triggers. All furniture stayed at the installed coordinates. Both builds kept the current gameplay patches. Character artwork therefore differs between the two figure settings. The whole maps and the Shattered Lands room are renders. The Ravager room comparisons are DOSBox captures.

The 23 previously listed placements comprise six narrow chairs, two high shelves, three dark tables, one chest, one wooden table, one pair of barrels drawn together, and nine sandstone furnishings. For each placement we compared the pixels in its drawing that remain visible after accounting for foreground scenery. The ledger gives the matched pixel count and camera origin for each build. Party members, moving room occupants and the pointer can cover part of the reference artwork. Both stored chest poses were already checked in a [separate playtest](2026-11-27-ravager-basin-and-chests.md).

## Cabinet passage

Object 5872 occurs twice, at (1888, 131) and (799, 239), using picture 2546 at both ends. The two stored frames are 64 × 59 and 64 × 64 pixels. Both closed placements matched the stock drawing in full at the recorded cameras. MAS 52 registers the cabinet handler in GPL 313 at offset 2543.

For the interaction, started afresh from the Roost and travelled to (118, 9). Used the eastern camera bounds from GPL 313 and left the region triggers active. Look named the object “Cabinet.” Choosing the green hand opened the doors. Looking again and using the hand a second time near the opening brought up “There is barely room in the cabinet for all of you. Get in the cabinet?” Choosing Yes transported the party to the Garden, where a Defiler took a combat turn. This run covers the journey from the eastern room. The opposite cabinet was inspected in place.

No drinking-water source was identified among the surveyed furnishings. The figure-pack and two-game startup checks passed (29 tests and 30 subtests).
