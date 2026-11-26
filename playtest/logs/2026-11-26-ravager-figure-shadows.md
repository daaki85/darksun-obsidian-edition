# Test log: the figures' shadows in Wake of the Ravager (2026-11-26)

Under test: DSCLOG2's FIGURE SHADOWS (`dos/dsclog2.asm`: FIG_PASS in the floor pass, FIG_WIDE_ALL and
FIG_WIDE widening the redraws, FIG_KEEP keeping each frame's shadow as the game draws it) and three patches
(`dsloader/ravager.py`: `fig_wide_all` 2868Ch site 160, `fig_wide` 2828Ch site 161, `fig_keep` 2A347h site
162). The Loader's way (`RAV_LOADER=1` through `ravload.sh`), a throwaway copy of the sequel
(`/tmp/playtest/ravGX`, its `game.gog` a link to the plain install's), the save `ravager-after-ambush`
(Tyr's street after the ambush: Thy'rokh the thri-kreen leading, the only party member on the map out of a
fight, a templar and a man walking the street).

## Steps

1. Waited for the shared DOSBox lock (another agent's `sb.held`, about 25 minutes), then held it with a
   background `flock` of my own (`gx.held`).
2. First build (sites 160-161 only: the shadow traced from the picture in the game's cache, as SL's first
   SHADOWS): loaded; `ravfig.py` said 180 floor passes with 65 shadows cast, but none showed under the
   kreen. Its map thing (thing 2, creature 2, status 1, slot 236, frame 2, the 50 x 32 frame placed at the
   map thing's +3, +5: the draw list's flag 20h clear) was right, its picture's cache slot flags 01h: **out of
   memory** (+0Eh bit 2 clear). The sequel frees pictures whenever it wants room (2AB90h on: each slot with
   bit 2 given back through 2AD2Ah until enough is free; the drawer, 2A28Fh, loads its picture again through
   2A1F7h when it draws it). Only the templar's picture, walking, was in memory at some floor drawings (a
   shadow seen under him once).
3. So SL's shadow cache, filled at the one place the picture is sure to be in memory: the thing drawer's call
   of the picture routine (`call far 1D40:3BEC`, 2A347h; site 162 on its first three bytes, the relocated
   segment word kept; FIG_KEEP makes the call itself and comes back past it). 64 slots of 152 bytes in the
   far block (9,728 bytes; the far block is in the HMA here). Rebuilt: DSCLOG2.EXE 52,784 bytes.
4. Loaded again: 106 passes, 127 shadows cast, **15 frames kept, 74 cast from kept shadows** at once; after a
   while 18 frames kept (the kreen's frame 2, 50 wide, 28 runs; the walkers' frames 0-11), 231 from kept.
5. Thy'rokh walked left (`ravgo.py x 1180`, the arrow keys, to world 1183, 1353): a soft dark shadow laid
   below and right of the kreen on the grey cobbles (`img/2026-11-26-ravager-figure-shadows-street.png`).
6. A same-view toggle (`ravfig.py 0` / `1` and DSCLOG2's VIEW_REDRAW) didn't make a clean pair: the redraw
   lands a frame or more late and the street's walkers move between, so the grabs were of the other state.
   The control is the separate run below.
7. **Control**: `RAV_SKIP=fig_wide_all,fig_wide,fig_keep` (the copy without the three sites), the same save,
   the same walk: `ravfig.py` 0 passes, 0 cast (the walls' passes 230 as ever), no shadow under the kreen.
   Side by side (control left, the port right): `img/2026-11-26-ravager-figure-shadows.png`.
8. Memory (`dosmem.py`, the port's run): DSCLOG2 52,256 bytes in upper memory (3,266 paragraphs), **103,200
   bytes of upper memory free** in one piece, 74,432 bytes free in the 640 KB after the game; the far block
   in the HMA.
9. DOSBox stopped by pid, the lock released.

## Results

The figures cast shadows in the sequel, from kept frames when their pictures are out of memory (most
drawings); none in the control. Left: a fight with the whole party (out of a fight the sequel draws only the
leader), the shadows in a big fight (64 kept frames: enough?), and the tone on the darker floors (the walls'
DARK, x 0.73, reads faint on the street's dark cobbles).
