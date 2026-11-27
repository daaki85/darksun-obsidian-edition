# The figures' shadows under their feet in Wake of the Ravager (2026-11-27)

**Under test**: the owner's report that in the sequel the shadows sit away from the figures, so they
look as if they float when walking (a screenshot of the red-haired woman, Ar'Anda). Branch
`claude/ravager-shadow-anchor`.

1. `ravload.sh ravager-after-ambush` (the plain DOSBox, the Loader's copies), key 1 (Ar'Anda the
   leader), `ravgo.py x 1100` and grabs while she walked: her shadow began about 14 game rows below
   her feet and a little left of them, a streak on the cobbles under nothing (img/
   2026-11-27-shadow-feet-before-after.png, left). Thy'rokh (2) and the half-giant (4) were drawn
   with their shadows at the feet.
2. **Why**: [the probe](files/2026-11-27-ravager-shadow-feet-probe.py) gave Ar'Anda's picture as 599,
   one of Codex's redraws (ravfigures.py's data), frame 2 34 x 45. The redraw's frames have clear
   margins all round (10 rows under the feet for 599 and 3961, 12 for 2472, up to 22 for 2554 and
   2556, 5 for 2536; the stock frames none), and DSCLOG2's FIG_OF and FIG_RECORD took the frame's
   bottom edge for the feet. The figure is drawn from its top left (the draw list's place less the
   map thing's +7, +8), so the figure was right and only the shadow fell the margin too low.
3. **The fix**: FEET_ROW (dos/shared_routines.inc, both helpers): the feet are the frame's last
   listed row (the run frames list rows top down, clear ones left out). DSCLOG (Shattered Lands)
   runs it from the tail (FEET_FAR, TAIL_CALL: 6 bytes of the segment, which had 276 free).
4. Again, the fixed build (FEET_ROW's bytes found in the running helper): Ar'Anda's shadow starts at
   her feet as she walks (the image, right); the others as before. `ravfig.py`: 472 shadows cast in
   399 passes, 131 from kept frames, none missed.

The start-up tests on both games' files passed; the full unit suite passed.
