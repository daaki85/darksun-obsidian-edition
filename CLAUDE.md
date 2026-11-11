# Notes for Claude

- **Before any in-game test** (anything run in DOSBox: seeing a fix work, a screenshot, a play
  check), read the [startup procedure](playtest/PLAYTESTING.md#startup-procedure) of
  `playtest/PLAYTESTING.md` in full and follow it, then the guide's recipes for the job in hand.
  Its tools are in `playtest/`. After every play, add everything learned to it (controls, screens,
  routes, timings, script details, tool changes, stalls: recipes as current practice, the incidents
  and dates in `playtest/HISTORY.md`) and commit and push, so it isn't lost with the container (an
  earlier version of the guide was). Keep the summary below in step with it.
- `playtest/` is outside `obsidian-edition/`, so it never ships in a release zip (the zip is that
  folder alone). Keep it that way.

## Playing the game for a test: the essentials

This is what must survive a compacted chat; `playtest/PLAYTESTING.md` has the rest and wins where
they differ.

- **Set-up**: run the tools from `playtest/`, `export DISPLAY=:55`, and set `PLAYTEST_WORK` to a
  scratch folder (the guide's `$WORK`; type `$PLAYTEST_WORK` in a shell). The game is
  `$PLAYTEST_WORK/inst`, from `setup_game.sh`; `start.sh` starts Xvfb, DOSBox with the Loader's
  patched game and the dice log (`$PLAYTEST_WORK/dice.txt`); `sh loadsave.sh NAME` loads a save
  from `playtest/saves/` (`pens-after-arena` the usual start, `fountain-user` for a fight, spell or
  rule test; `saves/README.md` lists them). Check the build under test is in place
  (`buildcheck.py`, `dec.py`), start the watchdog (`guard_start.sh` and a Monitor on `guard.log`),
  and keep a test log the user can read: the guide's [startup
  procedure](playtest/PLAYTESTING.md#startup-procedure).
- **Never fetch the game, Wake of the Ravager or the walkthrough from a public link, and never put a
  link to them in this public repository** (that is piracy, the user's word, 2026-11-11): the
  installers go at `$PLAYTEST_WORK/dl/sl.exe` and `rav.exe` from a copy the user provides privately;
  the walkthrough (`setup_guide.sh`) is never committed.
- **The window must be 320x240** (`xdotool getwindowgeometry`): at 960x720 every pixel check
  (message boxes, CHOOSE A SPELL) fails and the loops stall.
- **DOSBox dies when the session sits idle**: after any pause, check `pgrep -x dosbox` and reload.
- **Press Escape only with a screen or menu up** (with nothing open it brings EXIT: SAVE GAME?), and
  **never save after a memory edit** made for a test.
- **Story fights go through `fightout.sh`**; never `killfoes.py` in a fight a script waits on (the
  scripts miss the kills).
- Everything else (reading the game, controls, walking and doors, talk, fights, spells, inventory
  and shops, pictures for the docs, the recompiled program as the target) is in the guide's
  [recipes](playtest/PLAYTESTING.md#recipes); the route through the story (new game, arena, slave
  pens, Kurzak's call, back to the arena) is its [route](playtest/PLAYTESTING.md#the-route-through-the-story).

**Git.** The repository is `daaki85/darksun-obsidian-edition` (was `milenkovicdarko`: if `git remote -v`
still shows that, `git remote set-url origin https://github.com/daaki85/darksun-obsidian-edition.git`).
Other sessions push to `obsidian-edition` too: fetch and rebase onto
`origin/obsidian-edition` before every push. GitHub deletes the branch when its pull request
merges: then make it again from `origin/main` and put any unmerged commits on top.

**Shell.** Never `pkill -f` or `pgrep -f | kill` a pattern your own command line contains: it
kills your shell. Kill by pid, in a command of its own. Long runs go in the background with a
Monitor, and every step gets a `timeout`. Share DOSBox between agents with
`flock /tmp/playtest/dosbox.lock`.

**Water.** Whenever a play reaches a new area, note in the test log and in PLAYTESTING.md where
water, jugs or waterskins are (the user's idea of resting costing water one day).
