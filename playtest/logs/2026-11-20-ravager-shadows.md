# Test log: Shattered Lands-style wall shadows in Wake of the Ravager, drawn at run time (2026-11-20)

Under test: DSCLOG2's WALL SHADOWS (dos/dsclog2.asm) and two patches (dsloader/ravager.py:
floor_all 2B81Ch, floor_rect 2B97Fh, INT C4h/C5h). The sequel's own art and ground, the Loader's
way (`RAV_LOADER=1 sh ravstart.sh $WORK/ravsh`, a copy of the plain install).

## Steps
1. Read DSCLOG's SHADOWS (dsclog.asm): INT at the starts of SL's two floor routines (2700Eh, 27162h),
   their way back made FLOOR_POST, which darkens into the mode-X page through DARK (each colour's
   nearest at 3/4 strength), a plane at a time (DARKEN, SPANS_FLUSH). DSCLOG2 had rand, save, AC and
   the picture cache's four probes; no drawing.
2. The sequel's twins, found by their code: the floor of the view at 2B81Ch ("push bp / mov bp,sp /
   sub sp,1Ch", arguments page, camera x, y) and of a rectangle at 2B97Fh ("... sub sp,1Eh", page,
   x0, y0, x1 + 1, y1, camera x, y), as SL's; FLOOR_ON is the byte DS:29EAh (SL's 2F44h); the page
   routines at 0BF3:42B9h... read SL's page table layout (+4 segment, +404h x0, +604h y0, +804h x1,
   +A04h y1, +C04h flags) in segment load + 0BF3h (SL's 0980h); DGROUP 47E0h.
3. Built: WALL SHADOWS in dsclog2.asm (INT C4h/C5h, FLOOR_POST, WALL_PASS, IS_WALL on GMAP's C0h
   bits through DS:0538h, WS_RECT, WS_DARKEN, WS_FLUSH, DARK from the DAC: DARK_CHECK, WS_BUILD;
   the far block grown for spans, the palette and DARK) and the patches floor_all, floor_rect in
   ravager.py. `nasm -f bin -o dos/DSCLOG2.EXE dos/dsclog2.asm`: 5,232 bytes.
4. `RAV_LOADER=1 sh ravstart.sh $WORK/ravsh` (a copy of the plain install, its run files from
   __support/save): the game starts with the helper loaded high; Tyr's opening talk already shows
   darker bands right of the street's walls (shadows-tyr-after.png against base-tyr.png).
5. Into the ambush (3, Return twice): the helper's header (found by its signature in guest memory,
   C91B0h this run): wall_shadows 1, 61 floor passes shadowed, DARK made 3 times (the fade-in).
   Shadows right of each wall cell's run: the street's left wall, the right room's west wall
   (shadows-fight-after.png; shadows-before-after.png beside the plain game's grab).
6. Ar'Anda walked along the street wall (Move 12 to 5) with the camera scrolling: the shadows held
   through the rectangle redraws, nothing left behind (burst shwalk).
7. DOSBox stopped by pid, the lock released.

## Results

Run-time wall shadows work, SL's way (drawn into the floor before walls and figures, see-through,
any shape, no tile limit). Left: the shadow's shape is per cell (12 right, 8 down: longer casts need
cells two away); the strength (3/4) and length to tune by eye; other regions and their palettes
(DARK is made per palette); a switch for the Loader's Options tab (the header's +148).

## Retune to SL's shadows (the coordinator, from the owner: "don't look as good as SL's")

SL's pens (RGN29 from RMAP, GMAP C0h outlined): full one-cell bands right of and below wall cells with
45-degree ends; tone floor 28 to shadowed 26. Now: each wall square swept from (0, 0) to (16, 16): in an
open cell NW's covers all of it, W's x <= y, N's x > y (one span a row); DARK's target SL's
transform (Lab L x 0.73, a + 11, b x 0.82) fitted in 6-bit RGB (R x 0.730 + 5.4, G x 0.705 - 1.8,
B x 0.735 - 0.3; mean error 2 in 63), the nearest of 24-239. DSCLOG2.EXE 5,280 bytes.


### The retune tested (2026-11-20)

- Geometry right: full one-cell bands with 45-degree ends (diff masks of off/on grabs).
- The sequel's walk map pads every wall a cell into the room (the street's west wall: C0h in columns
  68-69, its art in 69 alone; the right room's: 80-81, art in 80), drawn as floor. Skipping wall cells
  left an unshadowed cell between a wall and its shadow; shadowing all of them put triangles inside
  the padding. Now a wall-marked cell is shadowed only when wholly in shadow (NW wall, or W and N).
- DARK: the cycled colours 16-23 map to themselves (a torch's flame went brighter, made from one
  frame of the cycle) and the DAC checksum leaves them out: DARK made 3 times in the fade-in, then
  steady (was 23 times a minute). Leaving 240-255 unmapped too was wrong: the street's greys are
  there (no shadow on the street at all).
- Tone: SL's transform on WR's grey cobbles gives a warm red-grey (grey 69 to 73,48,44; the exact Lab
  transform 67,45,52), on the brown room floors a maroon. Faithful to SL; to judge by eye.
- Redraw for a same-view toggle: set the header's +148, press C (USE, the left half) then Escape: the
  left half redrawn. (Escape then C on the EXIT GAME? box redraws only the box. ravclick.py could not
  move the pointer this run: it stayed at 158,99.)
- Grabs: shadows-retune-off.png / shadows-retune-on.png (same view, the ambush's first turn, camera
  as the run gave it); shadows-before-after-sl.png the pair; shadows-vs-sl.png SL's pens (the
  coordinator's render, 3x) beside the retuned shadows at 3x. The first prototype for comparison:
  shadows-fight-after.png.
- DSCLOG2.EXE 5,328 bytes. DOSBox stopped by pid, the lock released.
