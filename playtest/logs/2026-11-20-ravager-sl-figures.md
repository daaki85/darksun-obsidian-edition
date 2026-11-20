# Test log: Shattered Lands' party figures in Wake of the Ravager (phase 0)

2026-11-20. Branch `claude/ravager-sl-figures` (from `claude/ravager-port`).

**Under test:** Ravager's `OBJEX.GFF` with the party's 14 figures (objects 300-313) replaced by
Shattered Lands' (`darksun-recompiled/tools/sl_figures.py build`): each figure's walking picture
(`BMP n`), combat picture (`CBMP n`) and animation script (`SCMD n`), colours remapped, the
script's empty slots FFFFh and flag 40h set as Ravager sets it. Copy in `/tmp/playtest/ravsl`;
the unpatched game in `/tmp/playtest/rav` for comparison.

**To see:** the opening party (Ar'anda the elf, the cleric, Thy'rokh the thri-kreen, the
half-giant) drawn as SL's figures in Tyr; standing, walking, facing each way; in the Draxans'
ambush: attacking, being hit, dying. And whether flag 40h, the step's second byte, the anchors
and shadows behave.

## Steps
- 14:42 memory edit for the death test (never saved): HP of Terrannus, Thy'rokh, Gerakis set to 1

(Times are from one run of about 25 minutes; grabs in `$WORK/burst/`, not kept.)

1. **Baseline.** `sh ravstart.sh $WORK/rav` (the unpatched game) to Tyr; the talk answered with 3,
   then Return twice: the Draxans' ambush starts, Thy'rokh's turn. Grabs `base-*.png`.
2. **Patched.** `sh ravstart.sh $WORK/ravsl` (a real copy of the install, not hard links: the
   game writes its run and save files into its folder). Same steps. The game loads the patched
   `OBJEX.GFF` without complaint. The party is drawn as Shattered Lands' figures: Ar'Anda as SL's
   elf woman, Terrannus as the human man, Thy'rokh as the thri-kreen, Gerakis as the half-giant;
   colours right, no stray pixels, nothing cut. They stand a fifth to a third shorter than the
   sequel's Draxans beside them, as expected.
3. **Walking.** Ar'Anda's turn: the first click only captured the mouse (as the notes say), then
   `ravclick.py 185 125`: she walked right two squares on SL's side-walk frames (stride, facing the
   way she goes), feet on the ground, and stopped on SL's standing side frame (whose legs are
   apart too: at first it looked like a walk frame left on screen).
4. **Being hit.** Turn ended (`ravfight.py end`): a Draxan hit the party for 11, then for 10;
   the damage markers sit on the swapped figures.
5. **Attacking.** Terrannus's turn: a click on the Draxan above the party (it turned red, aimed),
   he stepped up and swung: SL's side attack (a crouched wind-up, a lunge with the arm out, back to
   standing), his feet on one line throughout, so the anchors in SL's script place SL's frames
   right. Damage dealt as usual.
6. **Dying.** Memory edit for the test only (never saved; the copy is thrown away): Terrannus,
   Thy'rokh and Gerakis set to 1 HP (creature records at DS:19C9h, +0). Two rounds of ended turns:
   the Draxans hit (13, 11, 3, 14); the fallen are drawn as SL's dead figures on the floor;
   Ar'Anda fell last (her hit at grab 362, her body down from 366) and the game ended with "YOUR
   PARTY HAS..." (Gerakis left at 1 HP counted as down: the game ends a fight when no one can act).
   **Pressing `ravfight.py end` while an enemy's turn is up** (turn 23) did nothing harmful.
7. Both DOSBoxes stopped by pid, the lock released.

## Results

- **It works.** Ravager draws, walks, swings, takes hits and kills Shattered Lands' party
  figures from the three swapped chunks, with no change to its program.
- **Flag 40h**, set on every step as the sequel sets it: nothing wrong seen with it. Whether it
  is needed was not tested (a build without it is the next check, if it matters).
- **The step's second byte** (SL's values kept): the swing's timing looked like the sequel's
  own; no sound was heard (DOSBox ran with sound off), so whether it plays a sound is still open.
- **Anchors:** right. Walking, standing, swinging and falling all sit on the same ground line.
- **Shadows:** neither game's figures showed one here; nothing to carry.
- **Size:** as found from the data: SL's figures are shorter beside the sequel's.

## Water

Tyr's opening street (the Draxans' ambush): no water, jugs or waterskins seen.

## Phase 1: the interface (2026-11-20)

`sl_figures.py build-ui`: RESOURCE.GFF with 45 interface pictures and 224 icons from SL (132 matched by look from another number), recoloured into the 92 colours WR keeps steady. In the same copy as the party figures. The run files reset from `__support/save`.

1. `sh ravstart.sh $WORK/ravsl` to Tyr: the game loads the patched RESOURCE.GFF. The talk boxes
   (WR's own, 20029 left out) showed a lavender ghost of a button at the top box's right edge:
   the dimmed MORE button (ICON 12100, frames 2-3). WR draws its dimmed frame in its stone greys,
   so it vanishes into WR's box; SL's, from SL's bluer stone, stays visible even remapped. Fixed
   by keeping WR's MORE and scroll icons (12100-12102, `ICON_KEEP`); rebuilt (221 icons) and
   seen gone in a second run.
2. Into the ambush (3, Return twice): the status box and the top-left icon draw right.
   **Q** (the END menu) opens and Escape closes it. A click on the status box (560,50 in the
   window) captures the mouse harmlessly in a fight.
3. **USE** (22,17): SL's frame (bluer, smoother stone), the fire border and the spell icons, all
   in place; the spell icons matched by look show the same symbols as the unpatched game's.
4. **VIEW INVENTORY** (74,171 on USE): SL's stone, slot icons, the carved side panel, DROP and
   SPLIT, all in place; WR's large creation figure stays (20000-20013 left out). The party's
   small figures down the left are SL's (the patched OBJEX). Escape there closes the inventory
   and USE together. 47,171 opened the inventory as well, not the character sheet: the
   character sheet wasn't reached.
5. The unpatched game to the same screens (`$WORK/rav`) for comparison: the change is subtle
   but consistent: WR's interface is SL's art re-encoded in fewer colours, so SL's is smoother
   and a little bluer; nothing misplaced.
6. DOSBoxes stopped by pid, the lock released.

**Results (phase 1, the interface):** works as a data patch. Ravager draws SL's interface
pictures and icons (rle frames among its own PLNR and PLAN ones) with no program change. Left
for later: WR's own talk boxes (20029 and the like, laid out otherwise), the character sheet
(not reached), and the mix of SL's bluer stone with WR's neutral grey where both show.
