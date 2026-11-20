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

## SL wall tops and shadows in Tyr (2026-11-20)

1. **Tops, first try (a band above each face):** ashlar (the arena district's tiles 5 and 43:
   pink-cream blocks with white joints; 54 and 55 have floor at their edges) chosen over the
   pens' brick and rubble by eye. In the game the bottom wall got its top, but the walls running
   north-south showed only scattered blocks: they are pieces of 46, 64 and 32 rows at uneven
   spacing, and a thin piece's whole picture is the wall's top seen from above.
2. **Tops, second try (thin pieces all top):** continuous ashlar walls; roofed walls left alone.
3. **Shadows as ground tiles:** written into `GMAP`, which turned out to be per-cell flags (0, 64,
   192 in this area), not the drawn tile map: my pattern search had lined up by chance (floor blocks
   match several tiles, among them 0 and 64). Reverted at once (the region file back to the squash's
   output). `MAP` doesn't match the screen at any grid offset either: how WR draws its ground is not
   known yet. DOSBox shows a 6-bit palette value v as v*4+v/16 (134 where v*255/63 gives 133).
4. **Shadows baked into the wall pictures:** each structure's outline offset 10 right and 6 down,
   every other pixel near-black (palette 231), the wall drawn over it; the canvas grows right and
   down, so the anchor (from the top-left) holds. In the game: a dark band right of each ashlar
   wall across the street and floors, as SL's light from the upper left. Flaw: where two pictures'
   checkerboards overlap out of step (below the bottom wall) the shadow is solid black.
5. DOSBox stopped by pid, the lock released.

## The solid shadow overlaps fixed (2026-11-20)

Each picture's checkerboard had its own phase, so where two shadows overlapped out of step they
filled in solid. Now one global phase: a shadow pixel only where its screen x + y is even. 71 of the
137 shadowed pictures are placed at both parities: each gets an odd-phase copy (BMP 5001 on) and
its odd placements a copy of their object pointing at it (81 objects, OJFF 32100 on, in the ETAB),
written with a ranged-index GFF writer (`tools/proto/gffr.py`). Offline over all of Tyr, solid 2x2
patches of the shadow colour: 5,546 before, 484 after, 446 with no shadows at all (the walls' own
dark details). In the game (one run, the opening ambush): clean checkerboards, no solid patches on
screen. DOSBox stopped by pid, the lock released.

## How Ravager draws its ground (2026-11-20)

The unpatched game (`$WORK/rav`) to the opening ambush; grabs and the camera read. The grab is the
320x200 frame doubled across and rows repeated 2 or 3 times (200 distinct rows): the exact frame,
every pixel a palette colour. Tyr's tiles matched 101-103 blocks exactly at grid offset (0, 8), but
neither `MAP ` nor `GMAP` read as 112 x 112 fitted. The region loader (DSUN.EXE 2B5xxh) settled it:
`RMAP`/`MAP ` (tile numbers) and `GMAP` (flags) are **98 rows of 128**; `MAP ` read that way matched
103 of 103 blocks, the screen's top-left at map pixel = camera (1008, 1368). Tyr drawn offline from
these rules matches the game's frame; SL's slave pens drawn the same way come out as their maze. The
frame isn't in guest memory (no 32-byte run of it found). DOSBox stopped by pid, the lock released.

## Shadows drawn into Tyr's ground (2026-11-20)

`groundshadow.py` (darksun-recompiled `tools/proto/`): each structure's outline cast 12 right and 8
down into the ground map as darkened copies of its tiles (SL's shadowed floor), 162 new tiles (the
255 limit), 1,642 of 1,710 cells exact. Only the ground drawing reads the map's tile numbers (DSUN.EXE
2B8A4h, 2BA19h). In the game (`$WORK/ravsl`, the opening ambush): solid warm dark bands right of the
walls on the street and in the rooms. Ar'Anda walked into a wall's shadow (Move 12 to 5, the camera
scrolling 40 left, the shadows moving with the ground). DOSBox stopped by pid, the lock released.

**Water:** none seen in this part of Tyr.

## Heights restored, thick walls (2026-11-20)

After the second comparison (the angle not established): the squash undone; WR's own wall
pictures with ashlar tops at full height (`build_tops.py nosquash`). `GMAP` overlaid on the opening
street: 192 marks wall cells (two cells wide where WR draws 18-pixel strips), 64 cells next to walls
and furniture. Every wall cell given an SL ashlar top tile with an edge line (`thickwalls.py`, 31 new
tiles). In the game: wide ashlar walls along the street, the sandstone faces at full height; the
fight went on normally (it was the Draxans' turn, so no walk this time). DOSBox stopped by pid, the
lock released.

## Shadows along the wall cells; WR's own wall art (2026-11-20)

`cellshadow.py`: each wall cell's square (GMAP 192) cast 12 right and 8 down onto open cells, 1,540
cells in 131 tiles (12 without). Variant A (WR's wall pictures, thick tops from WR's own sandstone,
square of piece 343) in the game: thick sandstone walls, straight shadow bands along their right and
lower sides. Gerakis's walk to a cell beside the street wall was refused ("can't go" pointer): that
cell is GMAP 64, unchanged from the shipped file, so 64 is the game's own no-walk margin beside walls
and furniture. DOSBox stopped by pid, the lock released.

## After the owner's review: party from the mod, furniture squash, creatures (2026-11-20)

The ground back to Ravager's own. Party built from the Obsidian Edition's SEGOBJEX copy: in the game
(a test copy with Terrannus and Ar'Anda as the half-elves) the mod's half-elves drawn right. Furniture
squash (60 pictures) in the game: tables lower, walls as shipped. Creature swap, first batch: in the
opening ambush picture 2427 (templar) turned the blonde woman who opens the game into an SL templar,
who walked and fought on SL's frames: the swap works, but 2427 is shared with her, so it was taken out.
DOSBox stopped by pid, the lock released.
