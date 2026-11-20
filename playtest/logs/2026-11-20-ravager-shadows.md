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
