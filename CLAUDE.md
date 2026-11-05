# Notes for Claude

- **Before any in-game test** (anything run in DOSBox: seeing a fix work, a screenshot, a play
  check), read `playtest/PLAYTESTING.md` in full and follow it. Its tools are in `playtest/`.
  After every play, add everything learned to it (controls, screens, routes, timings, script
  details, tool changes, stalls) and commit and push, so it isn't lost with the container (an
  earlier version of the guide was). Keep the summary below in step with it.
- `playtest/` is outside `obsidian-edition/`, so it never ships in a release zip (the zip is that
  folder alone). Keep it that way.

## Playing the game for a test: the essentials

This summary is here so it survives a compacted chat; `playtest/PLAYTESTING.md` has the detail and
wins where they differ.

**Setup.** Tools are in `playtest/` (run from there, `export DISPLAY=:55`, and set
`PLAYTEST_WORK` to a scratch folder; the game is `$PLAYTEST_WORK/inst`, from `setup_game.sh`).
`start.sh` starts Xvfb, the Loader's patched game in DOSBox and the dice log
(`$PLAYTEST_WORK/dice.txt`). Check the build under test is in place before trusting anything
(`GPLDATA=../obsidian-edition/dos/GPLDATA.GFF python3 dec.py SCRIPT LO HI`). Start the watchdog
(`guard_start.sh`, a Monitor on `guard.log` for STUCK/GONE). Keep a test log the user can read and
send it at each milestone; copy it to `playtest/logs/` and commit.

**The recompiled program** (Dark Sun Recompiled) as the target: `export PT_TARGET=recomp`, then
`start_recomp.sh` / `loadsave.sh` as usual (its window is made 320x240; its pid is in
`$WORK/dsun.pid`; pixel checks are tolerant through `pixmatch.py`). Its `build/ds1o` must be lifted
from this branch's helper (`tools/build_mod.sh` there) or `$WORK/dsun.log` shows `no function at`.
What stalls on it and not in DOSBox is a program fault to report.

**Start from a save.** `sh loadsave.sh pens-after-arena` loads the slave pens after the arena
(region 29h). Save at every milestone (Escape, S, click a slot at 120,46, type a name, SAVE at
253,46: the game then quits) and add it to `playtest/saves/` with a README line.

**The window must be 320x240** (`xdotool getwindowgeometry`): start.sh sets the Loader's
`window_scale` 1; at 960x720 every pixel check (message boxes, CHOOSE A SPELL) fails.

**DOSBox dies when the session sits idle**: after any pause, check `pgrep -x dosbox` and reload.

**Reading the game.** `state.py [FLAGS]` (fight, whose turn, region, leader, camera; a flag reads
0 whenever the flags have no place in memory, as in the arena). The dice log's tail after every
action (dialogue, narration, menus, "NO PATH FROM HERE"). `itemlists.py` (each member's worn +08h, held +0Ah and backpack +0Ch lists: the game's AC
counts +08h only). The dice log with `--all` gives each AC's parts. `shot.sh OUT.png` is the 320x200
capture; window grabs (`import -window`) are 320x240, so y x 1.2.

**Controls.**
- Clicks: `click.py X Y [left|right|none]` (game pixels). Right-click cycles the pointer: the
  plain arrow walks.
- Walking: `walkto.py X Y` (map units; screen = map - camera at DS:1178h). The view doesn't
  follow the leader: drag it with the middle button, `scroll.py DX DY` (dragging down shows the
  north). The tool keeps the pointer off the screen's edges, since an edge scrolls the view the
  other way, and releases every button afterwards. Click past a wall and the party finds its own
  way round.
- Doors open with the **look** pointer (right-click to cycle to it, then click the door); then
  click on the far side of the open door with the walk arrow to go through.
- Message boxes block clicks, keys and drags: click ON the box (`boxclick.sh`, 160,20).
- A YES/NO question needs the N or Y key, and only while the dice log's last line is `    2. No`.
  The arena gate's "Do you wish to continue?" is **Y**; the Announcer's question is N.
- Talk menus: click the line (the list scrolls, down arrow at 311,187); number keys don't work.
- The combat log panel covers the bottom right: `panel.sh hide`.
- E opens the Effects screen. In an END <NAME>'S MOVE menu, E is END TURN, and clicks there
  don't register.
- Escape with nothing open brings EXIT: SAVE GAME?; press Escape only with a screen or menu up.
- The arena's flags and numbers have no place in memory to set from outside (even mid-script):
  to test a branch there, force it in a test build of the scripts, then put the module back.

**Fights.** `fightout.sh` does a story fight the game's way: foes to 1 HP (not prisoners), Tab +
Return on party turns, E for a member out of movement, and messages and level-ups (CHOOSE A SPELL,
`levelup.sh`) cleared. Never `killfoes.py` in a fight a script waits on: the scripts miss the
kills.

**Git.** Other sessions push to `obsidian-edition` too: fetch and rebase onto
`origin/obsidian-edition` before every push. GitHub deletes the branch when its pull request
merges: then make it again from `origin/main` and put any unmerged commits on top.

**Shell.** Never `pkill -f` or `pgrep -f | kill` a pattern your own command line contains: it
kills your shell. Kill by pid, in a command of its own. Long runs go in the background with a
Monitor, and every step gets a `timeout`.

**The route so far.**
1. New game: `start.sh`, `topartyfight.sh` (the opening, then clicks south from the gate until
   the game brings the party into the arena). On 2026-11-02 the first bout never started from
   there (the bone wall stops the party at 488,264): restart and try again before digging.
2. The arena: `(sh arenawaves.sh && sh leavearena.sh)` fights the waves, answers N, drags the view
   north, clicks inside the wall (488,232), then the gate strip (488,184), and answers Y.
   Staying sends more fights.
3. The pens: the party arrives at (1816,440) and Kurzak greets it (choose Goodbye). The cluebook
   (`Cluebook.PDF`, `pdftotext -layout`) gives the rest. Kurzak's door is the entryway south of
   his stop (99,33-34) into the hall; the corridor gate (81,20-21) is locked, so the way west is
   the door at (113,90), the bottom corridor and its door (93,94) (`doorpath.py`). Then: #11, break into the stalker pen, kill
   the mountain stalker, push the button on the north wall; #12 is the sewer grate (46,86).
