# 2026-11-25: Wake of the Ravager in DOSBox-X (branch claude/ravager-dosbox-x)

**Under test:** the sequel started by the Loader itself (`launch.launch(FOLDER)`, `engine` dosbox-x),
DOSBox-X 2026.10.01 built here, Linux, window single. `$WORK/ravX`: a fresh copy of the install with
`fountain-user`'s party transferred (`python -m dsloader.ravtransfer saves/fountain-user/SAVE01.SAV ravX
SL_FOLDER ./dos`). Run script: the steps of logs/files/2026-11-25-ravager-small-ports-run.sh with the
Loader's start in place of ravstart.sh; `rav.pid` the DOSBox-X's pid (ravclick.py and ravfight.py then
read its memory file through the lock file).

## What was seen

- **First start: the game quit at once.** DOSBox-X's log: "Could not load image file: .../game.ins",
  "MSCDEX: Failure". GOG's sheet names `music\Track02.ogg`, the folder is `MUSIC`: DOSBox-X reads
  the sheet itself and on Linux finds no such file. Fixed: `ravager.cd_sheet` writes
  `dosbox-x/ravager-cd.cue` with each file's full path as the folder has it. Second start: "CDROM:
  Loaded Track02.ogg [44100 Hz 2-channel length 1.9 min.]" and the rest; DSCLOG2 loaded.
- Title menu, CREATE CHARACTERS, the four transferred members ADDed (View Character: Jenna, Ranger,
  STR 20), Escape, S: the cinematic, the opening talk in Tyr.
- HP 250 for the four (a test edit, never saved; autosave off; the copy thrown away), `ravdice.py
  --numbers` attached through the memory file: initiative lines, the Draxans' bow and lotulis attacks
  with THAC0 and damage lines, Seneca's hide in shadows roll. 118 turns logged.
- `ravfight.py fight 600`: the party's attacks often stopped at "no foe on screen" (Draxans inside
  the building, its known limit), so the fight was not finished (4 foes standing, the party up)
  when the session stopped for the owner's usage limit. DOSBox-X never quit.

## Still to do

- Finish the Draxans' fight (Tab + Return on each party turn, the sequel's Tab), and a save and load.
- The music heard: the CD's tracks are loaded; nobody has listened.
- Pre-existing, not this branch: `test_ravitems.GameTests` (with DSUN_WOTR) expects no `wide_sheets`
  from `objects_fixed`; it fails on the base branch too.
