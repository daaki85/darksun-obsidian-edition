# Mines 3 dining room and Elderbrain

Ran Wake of the Ravager in DOSBox with the Obsidian Edition Loader and private copies of the Roost save. Used the same revisit and sector lighting as the [chest playtest](2026-11-27-ravager-basin-and-chests.md). The maps mark both rooms and the dining table in Gedron used as a Shattered Lands scale reference. [Whole maps](../../reports/ravager-furniture/mine-encounter-maps.png)

## Five soup bowls

Use Reyhan’s jump to RGN03A, square (84, 73), with the region visited and sector 2 active. A normal close approach can alarm the diners and start combat. For these comparisons, disabled the proximity alarm at GPL 89 offset 5928 in the private copy. For the slump, set the serving count (7, 69) to four, the first diner index (7, 68) to zero and scheduled the game’s final-serving callback 4433 on region clock object 5075. Dismiss each diner’s message. This exercises the eating, slump and reward handlers, starting after the poison has been served.

Stock Ravager shows five red bowls during the meal. In the previous mod the smaller tabletop and the five redrawn diners were visible, but all five bowls disappeared behind their hands. Moved objects 10379–10383 eight game pixels forward, from y 1236/1237 to y 1244/1245, with their x coordinates and elevation 16 retained. In a fresh run with the revised placement table, all five bowls appeared during the meal. The diners fell forward in succession, partly covering the bowls, and the scripted message awarded 15,000 experience to each party member. The quiet idle capture has the final-serving timer disabled so the five places can be seen together. [Eating and slumped, with stock and Gedron controls](../../reports/ravager-furniture/mine-dining-live.png)

## Elderbrain

Jump to RGN03A, square (14, 45), in sector 11, with the visited flag 276 and lowered-barrier flag 254 set. Use the sword pointer on the brain in the glass tank. The game recenters the camera, breaks the glass, throws the brain, flashes the screen, clears the platform and awards the party 100,000 experience. This stages the barrier opening and exercises the game’s attack and destruction sequence.

The stock and previous mod both showed bright cyan fluid in the intact tank. The previous mod already carried the approved four-piece redraw in OBJEX pictures 1032–1035 and the still 3511. The running encounter reads two other pictures from RESOURCE.GFF. BMP 11008 contains the complete intact tank. BMP 11016 contains 29 frames, including glass and flying debris beyond the four scenery pieces. Transferred the approved drawing where the originals coincide and used matching local source colours for the remaining fragments. Decoded all 30 frames and compared dimensions and transparency against stock. Played the attack with the revised Loader resources. The darker fluid and modelled brain appear in both the idle tank and the break, and the reward follows after the room clears. [Matched DOSBox frames](../../reports/ravager-furniture/mine-elderbrain-live.png)

No rest-water source was identified in either room.
