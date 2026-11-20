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

## Phase 2: Tyr regraded (2026-11-20)

`sl_figures.py regrade ... RGN032 1.0`: Tyr's palette entries 16-95 (its ground and objects) moved to SL's ground colours (Lab mean and spread, all SL regions in their own palettes); the cobbles' 32 shared colours clustered into the 10 entries Tyr's tiles and objects leave free (21, 23, 67-69, 71, 91-94). In the same copy as phases 0 and 1.

1. **First run (strength 1.0):** the cobbles turned a warm stone, but the floors indoors and
   the sandstone round them came out a harsh yellow. Pixels sampled from the grab matched palette
   entries 16 and 19 at the game's own values, not the file's: **WR cycles entries 16-23 at run
   time** (torch and fire glow), and the ground had been put in two of them (21, 23), which
   looked free in the files. Fixed: the free entries come from 32-95 only (8 left in Tyr: 67-69,
   71, 91-94).
2. **Second run:** floors a warm tan, the street a warm stone; the light sandstone walls blown out
   to near white: a straight lightness shift (+22 L) pushes light colours past white. Fixed:
   lightness by a power curve (WR's mean to SL's, white kept white); a and b by mean and spread.
3. **Third run:** warm orange sandstone, tan floors, warm pale cobbles; the interface and the
   figures unchanged (their colours aren't touched). Compared with SL's slave pens (a screenshot
   from the docs): SL's ground is lighter and more muted (beige-green floors, red brick); Tyr's
   sandstone now reads more saturated orange than SL's. Strength and the spread's cap are the
   knobs to tune it.
4. DOSBox stopped by pid, the lock released.

**Water:** none seen in Tyr's opening street (the same view as before).

**Results (phase 2):** a region can be regraded as a data patch without touching the interface
or figures: its own palette entries 16-95 (ground and scenery together) graded, the ground's
pixels in shared colours moved into the region's spare entries. One region done (Tyr, RGN032);
for the owner to judge.

## Phase 4 pilot: walls and furniture at SL's angle (2026-11-20)

The owner: the ground can stay regraded, the walls and other objects need repainting; use art from all of SL, and mind the angles. SL looks down at buildings far more steeply (a square inset 21x19, about 65 degrees; WR's barrel rims 14x11, about 50), with short wall faces, big tops and cast shadows. Prototype in OBJEX.GFF, from the pens' tiles (PAL 41) in Tyr's regraded colours, each picture's size kept (its top left clear, so its base stays): the sandstone wall block 330 as an SL rubble block half as tall, the thin pillars 350 and 353 as brick columns half as tall, the table 516 as SL's bench 170.

1. `sh ravstart.sh $WORK/ravsl` into the ambush. The game draws the new run-length pictures. The
   thin pillar at the room's right edge is now a short brick stub; the bench stands where the table
   was at the top left. But the scene breaks: WR's walls are several overlapping pictures that
   assume its angle, and shortening one (the block 330) opened a hole where sacks behind the wall
   show through, its rubble hidden by the pictures in front.
2. DOSBox stopped by pid, the lock released.

**Results (pilot):** SL's angle can't be brought in piece by piece: a region's structure pictures
work together (tall faces hiding what's behind), so the angle has to change for all of a region's
structures at once. Options for the owner: keep WR's angle and refill surfaces with SL materials
(consistent, cheap, half the look); or change every structure in a region together (all faces
shortened, SL tops added, shadows), which is re-authoring the region's architecture.

## Whole-region squash of Tyr (2026-11-20)

Every structure and furniture picture placed in Tyr (197; not the 42 animated ones, people, doors and curtains, nor the rugs 534-537, 2385, 2386, 2896) squashed to 0.66 of its height (cos 65 / cos 50), bottom-anchored, canvas kept; entities placed at a height (10, 30, 64) lowered by the same factor in the ETAB. On the party-figures OBJEX.GFF (the pilot's pieces taken out), with the regraded ground and SL's interface. No SL tops or shadows yet.

1. **Every picture squashed to 0.66:** the scene held together (the table lower, the walls lower,
   nothing behind showing through) except the walls running north-south, which broke into
   pieces with gaps: they are stacks of thin pictures whose height is mostly the wall's top
   receding, not height.
2. **Only the bottom 48 rows (the face) squashed, the rest moved down:** fewer gaps, still about
   10 pixels at some joints.
3. **Structures (24 wide or less, or 56 tall or more) moved down 16 rows and cut by 16 at the
   bottom; furniture squashed:** the north-south walls joined, except where pieces stacked on top
   of walls (entity height 64: pictures 2815, 342) came down twice, by the lowered height and the
   picture's shift. Objects on screen found from the camera (DS:1408h) and the ETAB: **ETAB x is
   in the camera's units** (not halved).
4. **Pieces only ever placed on top of something keep their picture and come down by 16 through
   their height:** the walls continuous (two small notches on the far right); the table flatter,
   the bottom wall's top lower and its face shorter; the room reads as seen from higher up.
   Nothing broken.
5. DOSBox stopped by pid, the lock released.

**Results (squash):** a whole region can be shown from SL's steeper angle as a data patch
(`sl_figures.py squash WR_DIR RGN032 0.66 OUT_DIR`): structures' tops come down 16 rows, furniture
squashed, stacked pieces lowered through their heights. The change is moderate at this factor.
Not done yet: SL's wall tops (brick or rubble) and cast shadows, which carry much of SL's look.
