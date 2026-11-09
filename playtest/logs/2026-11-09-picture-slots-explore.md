# Does Shattered Lands lose graphics as Wake of the Ravager does? (2026-11-09)

The user found SSI's technical note 2712 for Wake of the Ravager: too many items in a region (on
characters, in chests, on bodies) make doorways, niches or items vanish; leaving the region and
coming back clears it. Shattered Lands runs the same engine, and the limit is the one found on
2026-11-09 (logs/2026-11-09-missing-figures.md, logs/2026-11-09-picture-store.md): the game's
table of 300 picture slots and its 741,376-byte picture store, shared by walls (doorways,
niches) and every figure and item picture, never given back until a region loads. At 300 the
game gives a new picture no slot and doesn't draw it.

Measured with `slotcount.py` (new):

- `pens-after-arena` on load: 203 slots, store end 305,305 (41%). Walking the corridor: 203.
- `pens-thornwall-rack` on load: 203. Walked (route.py) to (1816,1000), (1848,700), (1608,600)
  and Kalzith's pen (1560,856), the far stops refused (NO ROUTE): **203 throughout**. The region's
  pictures are all loaded on arrival; walking about adds none.
- Earlier runs: a whole fight (the ambush, fightout.sh) added 6 (bodies, the game's own new
  pictures); the Loader's outfit changes add none since the picture-store fix.

So in the pens about 97 slots are spare after arrival, and only new pictures in that one visit
(bodies, dropped items of new kinds, spells, monsters sent in) take them. The pens' alarm, wave
after wave, is the heaviest case seen and hasn't been counted yet. Leaving the region frees all.
