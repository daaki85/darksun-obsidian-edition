# The combat log's doc pictures retaken (2026-11-09)

For the audit's docs: `docs/combat-log.png`, `combat-log-expanded.png` and `combat-log-live.gif`
showing the panel's 7-pixel font (8 lines docked, 14 expanded) and the new Short wording, taken with
the final build of the audit's code batch (`buildcheck.py`: OK). DOSBox held under
`/tmp/playtest/dosbox.lock` (a background `flock` waiting on a HELDFILE) for the whole run.

- `loadsave.sh fountain-user`, `dismiss.sh`: Pehtucl's ambush started (fight_on 1).
- Party turns with Tab + Return (state.py's `turn` 0-3 before each); `healparty.py` twice in memory
  (Jenna fell to 4 HP; its "+N" HP lines show in the expanded shot). Never saved.
- The view: `scroll.py -60 -80` in the fight moved the camera to (1048, 1368) and brought the party
  to the left of the panel (screen x 40-90, y 120-190). The pointer parked with
  `click.py 20 150 none` (the arrow, on floor west of the party).
- Panel buttons (320x200): docked, **+** at (311,129) expands it; expanded, **-** is at (296,74)
  (a box at x 292-299, y 70-77: a click at 311,75 did nothing).
- Pictures: `shot.sh`'s 320x200 scaled 200% (640x400), as the old ones.
- The GIF: `import -window` in a loop for 14-16 s (about 32 grabs a second, 320x240), started just
  before Tab + Return; frames picked 40 ms apart by their timestamps, two recordings joined (Lex's
  hit and Seneca's hide; then her backstab, the poison and the kill), `convert -delay 4 ... -scale
  200% -layers Optimize`: 337 frames, 640x480, 323 KB.
- DOSBox killed by pid afterwards; the lock released.
