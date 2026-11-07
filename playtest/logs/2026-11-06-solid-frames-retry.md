# 2026-11-06: trying to reproduce Cilla's two solid frames (open item)

**Under test:** the unexplained case from 2026-11-05: in one hidden walk ending beside K'ratchek and
Gerakis, the last 2 of 15 frames drew Cilla solid.

**Setup:** fresh container (dosbox, xdotool, innoextract installed with apt; the game installer needed
`drive.usercontent.google.com` allowed in the environment's network). `start.sh`, then `toalarm.sh`
(pens-after-scar, Cilla's thief level 12 in memory, to the fire room) and `restalarm.sh` (pointer
the eye first: right-click twice on bare floor): FIGHT-ON, turn 3, 5 rests, 1 call. Window 320x240.
(`ghostchk.py 0` was run once before the load, marking Gerakis in memory: lost on the load.)

**Seen:** Cilla's first turn: "hides in shadows: d100 = 94, needs 95 ... hidden; moves silently:
d100 = 64 ... unheard". Walks with `walktime.py 3 X Y DIR` (frames kept), all with her hidden:
- to a spot a step west of Gerakis: 7 steps (0.45 s), 7 frames;
- back south toward K'ratchek: 4 frames; north again: 2; south again: 2.
All 15 frames cropped and tiled: **Cilla see-through in every one**, including the last steps
beside Gerakis. **Not reproduced.** (Her Move ran out after these, so no longer walk.)
She was never walked into the exact square between K'ratchek and Gerakis: that is still the
closest untried case.

**Nit (read, not changed): PLAY_SOUND's lent entry.** The table entry is 6 bytes (+1 kind, +2..+5 the
far pointer; +0 is never written). PLAY_SOUND saves +1..+6 (`push word [es:bx+1]`, `push dword
[es:bx+3]`) and restores the same, so byte +0 is never touched; the one stray byte is +6, the NEXT
entry's byte 0, read and written back unchanged. Harmless unless the game changes that byte during
the sound call. No change made; a DOSBox sound test would be needed to be sure.
