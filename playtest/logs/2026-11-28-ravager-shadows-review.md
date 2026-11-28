# Wake of the Ravager's shadows reviewed: figures and scenery (2026-11-28)

**Under test**: the owner's ask to look at the sequel's shadows for the characters and the environment,
against Shattered Lands'. Branch `claude/ravager-shadows-review`, after #293 (the feet).

## Where

1. **Tyr** (`ravload.sh ravager-after-ambush`): the street, `ravgo.py y 1224 x 560 y 1130 x 420 y 1000 x 300 y
   900` to Shadow Square's stalls, grabs at each leg; the house east of the start (shelves, jars, sacks,
   tables), the build and a control (`RAV_SKIP=figures`, the game's own furniture).
2. **The Harbinger's Roost** (`ravload.sh ravager-roost`): the hall, the bedroom; [the on/off
   grabs](files/2026-11-28-ravager-shadows-onoff.sh) and their difference show what the Loader adds.
3. **The air drakes' fight on the Cloud** (`ravjump.py 0x42 85 15` from the Roost, Reyhan's talk, Space
   twice, a click on the region's picture): four drakes and the party.
4. **Shattered Lands** (`loadsave.sh trap-user`, Pehtucl's room; `fountain-user`) for comparison.
   Water: none seen in these places.

## What was seen

5. **Scenery**: Shattered Lands' walls have their shadows drawn into the floor tiles (lower right of each
   wall); its furniture (bed, screens, chairs, the table) casts none. In the sequel the Loader's wall shadows
   fall the same way, under every wall and through doorways and windows onto the floor beyond; its
   furniture, stalls, crates and barrels cast none, in the game's own art and in Codex's lowered furniture
   alike. As Shattered Lands: nothing to change, nothing for Codex.
6. **Figures**: the party and the people cast theirs from the feet (#293). On the dark floors (Tyr's grey
   cobbles, the Roost's patterned tiles, the houses' brown) a shadow is faint, as Shattered Lands' on dark
   ground.
7. **The drakes cast none.** `ravfig.py` on the Cloud: "none for want of one 189". The probe
   (logs/files/2026-11-27-ravager-shadow-feet-probe.py, things below 40) gave them RESOURCE's picture
   11005, in memory, frame 67 x 58: a planar picture (FFh "PLNR"), as are the other drakes (11006, 11007)
   and the Tarrasque (11001, 11002), and DSCLOG2 cast none from a planar frame.
8. **A big figure's kept shadow lost its foot.** A kept frame held the first 48 runs from the top (64 in
   Shattered Lands): 14 of the sequel's pictures (and 6 of Codex's) and over 20 of Shattered Lands' have
   frames with more in the rows that cast, so with the picture out of memory such a figure cast only the
   top of its shadow, away from its feet.
9. **The Tarrasque's widest frames cast none**: wider than 128 (134 to 153), which FIG_OF refused.

## The fixes

10. Kept runs go round again past SC_RUNS, the runs nearest the feet kept (both helpers). The sequel's
    frames up to 255 wide cast a shadow. Its planar frames are unpacked as the game draws them
    (PLANAR FIGURES, in DSCLOG2's tail through PL_CALL: the segment had 1,760 bytes left, under the 2,048
    margin), their feet found, their runs kept; the floor pass casts from the kept runs.
11. **Again on the Cloud**: each drake has its shadow from its feet, laid toward the lower right on the clay
    (img/2026-11-28-drake-shadows-before-after.png); `ravfig.py`: 377 cast in 76 passes, 339 from kept
    frames, none missed. Shattered Lands' `fountain-user`: Pehtucl's and the party's shadows and the dust
    as before.

The unit suite and both games' start-up tests passed.

## The Tarrasque, played again

12. `ravload.sh ravager-roost`, `ravjump.py 0x44 33 43`, Reyhan's talk, Down x7, the cinematic, then the camera on
    the beast (`cam.py 1256 380`, a redraw). Its shadow fell under its own body and its front claws cast none:
    **the Tarrasque is two map things**, the back half (thing 41, picture 11001) and the front half with the
    claws (thing 252, picture 11002). Only thing 41 is a creature in the things table; 252 is kind 0, so
    `FIG_ALIVE` said "not a creature" and nothing of it was kept or cast. A map thing's +21h names its part
    and **+23h the thing it is part of** (FFFFh none): 41 has +21h = 252, 252 has +23h = 41.
13. **The fix**: `FIG_ALIVE` follows +23h to the whole and asks after that one (dying, dead or gone cast
    none, as before). Played again: picture 11002's frame 7 kept (115 wide, 48 runs, the runs nearest the
    feet), and with the figures' shadows off and on (`onoff.sh`) the claws cast theirs onto the tiles to the
    lower right (img/2026-11-28-tarrasque-shadow-marked.png, the difference in red). On the Roost's dark
    tiles a shadow is faint, as everywhere on dark ground.
14. **Shattered Lands' big figures**: `legcrusher-fountain-user`, the fight with Legcrusher (picture 1781,
    frames to 70 runs) and two of the party (75 and 76 runs), all past the old 64: with `shadowsw.py` off and
    on (the camera fixed with `camera.py` and a scroll to redraw) each casts from its feet to the lower right
    as before (img/2026-11-28-sl-legcrusher-shadows-off-on.png). A faint shadow also shows on the brick wall
    at the view's foot, from someone beyond it; not looked into.

