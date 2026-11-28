# Pavis’s writing basin and the hinged chests

## El’s Temple

Loaded a private copy of the Roost save in DOSBox and used Reyhan’s travel fixture to reach RGN037, square (109, 45). After dismissing Jestris’s greeting, used the sword on Pavis. His encounter took him out of the writing basin. GPL 246 advances object 465 at (1724, 698) and brings the standing yuan-ti into the room. The party can obscure the bottom of the desk during combat. The two captures of the unattended desk are aligned on the room because the camera followed the fight. The paper stays on the rim, and the lowest pixel of the desk stays on world row 697 in all three stored poses.

Repeated with stock figures and the integrated redraw from `8728123d`. The occupied drawing went from 61 visible rows to 50 and the vacated one from 36 to 24. Keep the earlier redraw. [Matched DOSBox views](../../reports/ravager-furniture/pavis-basin-live.png)

## Mines 3

Object 3143 at (577, 744) in RGN03A uses picture 1112. The only other byte-identical copy of its two stock frames is picture 3250, on object 9731 at (1833, 323) in the Pyramid. The package already lowered the Pyramid copy. The new package lowers the Mines copy once from the original. The visible heights go from 41 to 27 pixels closed and 60 to 40 pixels open. Both remain 50 pixels wide. Each region keeps its original animation script. The Mines x offset is 24 in both states, the Pyramid’s is 23, and the y offsets are 40 and 59 in both regions.

Entering Mines 3 for the first time triggers a collapse and moves the party away from the chamber. For the interaction check, used a private revisit fixture that set the visited flag (276), selected sector 11, applied its camera bounds, and placed the party at (35, 47). The first revisit left the party and dialogue panels washed out. Running the region display calls 36 (0, 0) and 37 (0, 1) after the bounds and sector selection restored the dark blue floor, orange party figure and readable interface for the matched captures. The chest’s own Use script was active in both builds. Used Look on the chest, then the hand on its item card. The game listed a rod, a set of bracers, a key and 5,000, and the lid stood open after dismissing the message. A second use returned “The chest has already been cleaned out.” No game was saved. [Matched Mines 3 captures](../../reports/ravager-furniture/mines-chest-live.png)

[Whole maps with the chest rooms marked](../../reports/ravager-furniture/mine-chest-maps.png) · [Both poses with a Shattered Lands upper castle chest for scale](../../reports/ravager-furniture/mine-chest-poses.png)

## Pyramid

The chest sits just behind the southern wall of the eastern room. A direct jump from the Roost keeps the arrival room’s camera bounds. The test used the eastern bounds from GPL 313 and square (112, 18) to bring this chest into view. Its lower edge sits behind the wall. No interaction for object 9731 was found in the region’s registered triggers. In a private Loader copy, selected the raised animation step as the initial step, including its own drawing offsets. On a second room entry the game drew the raised lid over the same floor tile. The wall obscured the feet in both captures, with the dark inside panel clearly visible above it. The shipping Pyramid script and art retain their original behavior. [Pyramid captures and Mines loot messages](../../reports/ravager-furniture/chests-live.png)

No water source was identified at the scribe’s desk or in the Mines chest chamber.
