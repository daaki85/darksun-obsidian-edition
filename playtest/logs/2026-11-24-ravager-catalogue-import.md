# 2026-11-24: the approved Ravager figure redraws in the game

**Under test:** the catalogue's approved redraws (Codex's art, reviewed by Daaki) as built by
`darksun-recompiled/tools/proto/import_catalogue.py` (PR daaki85/darksun-recompiled#8): 87 pictures
from 39 packages, the greater elementals on their own figures (objects 428 and 429 to 3954 and 3955),
the Mines3 dining-room placements. Base: the dressed people (`people_dress.py`) on the shipped
OBJEX, with the shipped game's scripts for the still figures.

**Offline checks:** every frame decodes; every script step's frame exists (2,400 steps). The first
build had 428 bad steps: the dressing gives some still pictures (714, 715, 720-722, 2778, 3613...) a
walking script, and a package with only pictures kept it. Fixed: a package's missing script or combat
pictures come from the shipped game. No approved figure uses a colour its own regions leave undefined
(63,0,63); the magenta seen when all are drawn in Tyr's palette is only that.

**In the game** (Wake of the Ravager in DOSBox, ravsl copy, the opening ambush: answer 3; each fighter's
chunks written over the Draxans' picture 2428, `ravburst.sh` grabs):

| Fighter | Seen |
| --- | --- |
| 914 Ptar, 2471 Helmine, 2405 Greater Air, 2470, 1753, 1754, 1755, 1756, 1758, 1759 | walked up and fought, first run |
| 779, 780 (half-elves), 915 Water, 1881 Earth, 2557 Greater Fire, 3954 Greater Earth, 3955 Greater Water, 2469, 1412, 1757, 2843-2849, 2895 yuan-ti, 2022 Melody, 2394 obsidian golem, 2408 | walked up and fought on the rerun without still figures in the room |
| 2345 Sundew, 2403 Snappersaw | stay rooted (they have no walk), drawn right |

All drew on their feet at the anchors, in their colours, through walk, swing and hits.

**Still figures** were put in the rug room's people (2427, 2420) two at a time beside each fighter:
they draw there (the Sultan's cushions, Asquire, Snaggle's bed, Ikibod's counter were seen), but a
still figure in those walking people's slots stalls the ambush (the fight never starts), so their own
places (Tyr's shops, the Jann camp, the mines, Humbleton) remain the real check.

**Not imported:** Tarrasque 269 and Magma Golem 693, approved as loose PNG frames only.
