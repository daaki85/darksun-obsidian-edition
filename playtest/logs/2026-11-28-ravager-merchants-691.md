# Tyr's shopkeepers (picture 691, #313) in the game

Build: obsidian-edition after #313. Save: ravager-after-ambush, walked to Shadow Square (`ravgo.py y 1224 x 560`).

1. The ten shopkeepers who use picture 691 (objects 152-155, 320-325) live in Limbo (RGN0FF's ETAB);
   none is on Tyr's map on a walk. Tyr's stall sellers are other objects (the pottery seller is object 159,
   picture 720) and the stalls' map records at (260-311, 1472-1488) are pictures 312 and 323-327.
2. Staged for a look: object 159's picture (OJFF +12) set to 691 in the Loader's `dos/OBJEX2.GFF`
   after `ravstart.sh` wrote it and before the save was loaded (test-only, the copy is rewritten on every
   start). The pottery seller then stands at his stall in the new drawing: Shattered Lands' human size,
   pale wrap, red sash, dark hair, standing on the stall's floor line. The same staging with
   `RAV_SKIP=figures` is the control. [Close-up, stock left, new right](img/2026-11-28-ravager-merchant-691.png)
3. The object's own colour change applies to whatever picture it shows (the stock 691 under object 159
   came out blonde in purple), so each shop record can tint 691 its own way; Codex's sheet stages all ten.

Shattered Lands has no picture 691 shopkeeper: this change is the sequel's only.
Water: none seen at the Shadow Square stalls.
