# 2026-11-27: the Loader pictures retaken with the new bar

Under test: nothing changed in the code; the docs' pictures of the Loader window (`dicelog.png`,
`dialogue.png`, `viewer.png`) still showed the old button bar (Start the game, no Journal tab).
Build: `origin/obsidian-edition` at 497966e (after #257), branch `claude/docs-pictures-retake`.

Steps and what was seen:

- Xvfb `:55` at 2100x900 started by hand, `sh start.sh` (DOSBox at 0,0, 320x240), its text dice log
  killed by pid, `dice.txt` emptied, the window started from the wrapper `/tmp/playtest/winwrap.py`
  (`python3.12`, runs `dsloader view` with `Viewer._append_dice` also writing to `dice.txt`), moved to
  340,0: "Connected to the game (process 330)", the new bar, Readable layout and Show details ticked.
- A new game: the title clicked twice, `s`, then `boxclick.sh` through the opening show. The
  Loader-written `dice.txt` never has "Step forward" (the Announcer's lines go to the Dialogue tab, not
  the dice log), so a loop waiting for it, as `topartyfight.sh` does with the text dice log, never stops:
  wait for "Fight over" instead. The show: 3 rounds, the Rampager killed the Defiler with 2d6 and Acid.
- `dicelog.png`: the window cropped from the root (1320x780 at 340,0), Characters with Gerakis and
  K'ratchek, the Dice log at the round's end. `dialogue.png`: the Dialogue tab, the Announcer twice.
- `viewer.png` (earlier, on `:56`, the practice program FAKEPTY.COM and `window_scale` 3): Memory tools,
  "sadira" searched and assigned to slot 1, All fields.
- `dicelog-readable.png` not retaken: it is a crop of the log alone, no bar. `fogbolt.png` not retaken.
- PNG8 (`convert -colors 256`): 88 KB and 65 KB.
