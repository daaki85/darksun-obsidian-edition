# The combat log's doc pictures retaken for the new font (2026-11-11)

After 2.16.0 the panel's font is a pixel bigger (8 pixels a line: 7 lines docked, 12 expanded), so
the four pictures were retaken from `saves/fountain-user` (Pehtucl's ambush; never saved after).

- `start.sh`, `buildcheck.py` (OK), `loadsave.sh fountain-user`, `dismiss.sh`, L for the panel,
  `scroll.py -60 -80`, the pointer parked with `click.py 20 150 none`.
- Party turns with Tab + Return; a member out of movement gets END <NAME>'S MOVE (E ends it); E
  with no menu opened the Effects screen once (Escape closed it). `healparty.py` once (its "+N"
  lines were pushed out of view before the shots).
- `combat-log.png`: docked, Short (the level button at 262,129: Detail, Least, Short), round 4,
  Jenna's turn. `combat-log-expanded.png`: **+** at (311,129). `combat-log-detail.png`: the level
  button at (262,74) once (Detail), a miss with its THAC0's parts and Jenna's hide roll. All
  `shot.sh` 320x200 scaled 200%.
- `combat-log-live.gif`: a fresh load, then DOSBox's Ctrl+F5 screenshots in a loop for 24 s (314
  frames, about 13 a second) while Jenna, Lex, Seneca and Ester took their turns: Seneca's poison
  and Ester's kill of the Templar. `convert -delay 8 ... -scale 200% -layers Optimize`: 457 KB.
  Window grabs (`import -window`, 320x240) made a 1 MB GIF; Ctrl+Alt+F5 (video) wrote nothing.
