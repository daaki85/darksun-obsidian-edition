# The combat log's panel copied as the view moves; autosave without a restart (2026-11-27)

Under test: branch `claude/panel-scroll-autosave` (from `obsidian-edition` after #252): DSCLOG's
`PANEL_FOLLOW`, `CENTRE_THING`, `CENTRE_XY` (sites 125-127) and `VIEW_MOVED`; `COPIES` moved to the
tail; `DiceLog.follow_switches`.

## The panel's copies
Seen in the screenshot retake (logs/2026-11-27-outfit-screenshots.md): while the game moved the view
to a guard, the docked panel's header was drawn several times along its row ("Needs Needs Needs").
The game's drawing of a moved view scrolls the screen, panel and all, and draws only what came in;
`PANEL_TICK` drew the view again only at the main loop's next pass.

- Setup each run: `loadsave.sh fountain-user`, `buildcheck.py` OK, `dismiss.sh`, `panel.sh show`,
  `scroll.py -60 -80`; `framegrab.sh DIR 90` (or 150) in the background while `untilturn.sh`
  played Lex, Jenna, Ester and Seneca (`PARTY=...`); `panelcopies.py DIR` counted.
- **Control** (only `PANEL_FOLLOW`, a full `VIEW_AGAIN`): 3,254 frames, copies in runs of up to 8
  frames (a whole panel shifted 30 pixels left at the guard's turn).
- **Both moves caught, `VIEW_AGAIN` whole** (two rounds, 12 monster turns): 5,338 frames, runs of
  up to 49 frames. Counters in a scratch build (DSCLOG's segment from the INT 60h vector): follow 8,
  centre 25, moved 8: the sites ran, but redrawing the whole view (above the panel first) left the
  copy up as long as before. Frames around one: the map half drawn, then the copy, then the guards.
- **Only the copy's place drawn again** (`VIEW_MOVED` with AL 1: the panel's rectangle moved by the
  old view less the new, `REDRAW_CLIPPED`), two rounds, 7 monster turns: 5,595 frames, copies in 2
  runs of 1 and 2 frames (while the game itself is still drawing), the rest "Miss" labels. Counters:
  follow 12, centre 53, moved 26. No patch of map left wrong, the panel always in place.
- Room: 64 bytes over the segment's margin; the files-with-copies table (`COPIES`, 256 bytes) moved to
  the tail, read through ES. `kept_end` 65,200 as before, upper memory 70 paragraphs free (86 before).
  Opening the copies (SEGOBJEX, RESOURCE, GPLDATA, the regions) worked through every load of the play.

## Autosave in settings.json
With the dice log running (start.sh's, no Loader window), `autosave` set true in settings.json: the
dice log printed `(settings.json changed: quick save keys off, autosave on)` within a second; set
false again: `... autosave off`. Unit test: `test_the_quick_save_switches_follow_the_settings_file`.

## Checks
- `test_start_files.py` with both games (DSUN_SL, DSUN_WOTR): 3 passed. The full suite: 3,191 passed.
- Water: no new area.
