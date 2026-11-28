# Jann camp baskets and the tapestry cart

Compared all 54 inventoried placements in Jann with stock and installed Obsidian Edition art. The additional survey found four filled baskets, two seated figures and eight pieces of serving ware beyond the earlier 40 placements.

[Whole maps and cushion rooms](../../reports/ravager-furniture/jann-camp-whole-maps.png) · [Basket comparison](../../reports/ravager-furniture/jann-filled-baskets.png) · [Wagon and figure captures](../../reports/ravager-furniture/jann-wagon-and-figures.png) · [54 placements](../../reports/ravager-furniture/jann-placements.csv)

## Baskets in three parts of the camp

The earlier pass lowered the two empty baskets beside Utella. A filled basket there uses the same woven sides and handles. Three produce baskets use a similar weave. The full and empty containers had visibly different depths. Pictures 2763 and 2767 now shorten the bottom 14 rows to nine. The six upper rows of produce and eight upper rows of weaving supplies move down intact. The width, anchor and bottom row stay fixed. The produce basket is now 15 opaque rows high, the supply basket 17. The larger empty basket is 14. The green and purple strands still hang over the rim.

Checked both baskets at the loom, a produce basket at (581, 1340) and another at (35, 1430). The before panel in the basket comparison uses the previous mod, so Utella’s approved figure and the two empty baskets are the same on both sides. Rebuilding the pack changed just the two filled basket bitmaps.

## Cushions, figures and serving ware

Checked 13 thick cushions and 21 thin pillows in their tent arrangements. Shortening just the lower edges of the five thick designs preserves the overlaps around the Sultan. The occupied cushion is part of the Sultan’s figure. The resting pose, a staged head turn and a staged empty seat all kept the same contact with the pile. An additional view used the camp script’s guard-departure calls to see the pillows behind the front rank.

At Utella’s actual loom, the stored weaving poses both played with her hands at the textile. Heroga sits on her own smaller ochre cushion at (441, 607). Zorani sits on the ground by the coals at (1481, 1204). To inspect all five of Heroga’s gestures and both of Zorani’s poses, additional captures held the less frequently seen poses in private copies of their animation scripts. Heroga’s wide gestures use a horizontal anchor five pixels farther from the left edge. The comparison uses the same animation step for each stock and redrawn figure. Keep the food tray, its two gold jugs and five stemmed goblets at their current sizes. The tray lies on the floor and its handles are clear. No drinking-water use was verified for the jugs.

## The wagon in play

At the southeast camp the wagon body (3227) and shafts (3228) start in their one-pixel states. To reproduce the late-camp setup from the Roost save, jump to region 3Bh, square (100, 91). In a private copy of the region initialization, run the four original instructions from GPL 74 offsets 3938 through 3973. These show both pieces and register the regular callback at 2644. The setup stages the quest condition. The following steps use the game’s normal controls.

1. Look at the dark wagon cover to open the **Cart** card. Choose the green Use hand.
2. The open body and shafts appear at the same anchors. The two new drawings are pictures 2729 and 2730. Their opaque pixels matched both native captures in full. The loose tapestry appears on the sand.
3. Look at the loose object. The card identifies it as **Tapestry**. Choose the pickup hand. In stock and Obsidian Edition the game reported that the party member found a tapestry.

## Verification

Private DOSBox runs used the Loader and the Roost save with quick save and autosave disabled. The placement census pinned the camera and suppressed unrelated encounters. Stock used the shipped figures and placements. The revised census reused captures from the previous mod for drawings outside the two changed bitmaps only after verifying the pack difference. The CSV gives one camera, frame and pixel count per placement for each build. For each of the 54 placements, at least one capture matched all visible reference pixels to DOS palette precision on each build. The maps and Shattered Lands reference are renders. Ravager room panels are DOSBox captures.

The full suite with both games installed passed 3,565 tests and 876,169 subtests, with 33 tests skipped.
