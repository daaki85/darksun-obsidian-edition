# Notes for Claude

- **Before any in-game test** (anything run in DOSBox: seeing a fix work, a screenshot, a play
  check), read the [startup procedure](playtest/PLAYTESTING.md#startup-procedure) of
  `playtest/PLAYTESTING.md` in full and follow it, then the guide's recipes for the job in hand.
  Its tools are in `playtest/`. **After every play**, add everything learned to the guide and commit
  and push: [after a play](playtest/PLAYTESTING.md#3-after-a-play). Keep the summary below in step
  with the guide.
- **Code audits**: when the user asks for a code audit / code quality review, use the project skill
  `/thermo-nuclear-code-quality-review` (`.claude/skills/thermo-nuclear-code-quality-review/SKILL.md`)
  and follow it in full.
- `playtest/` is outside `obsidian-edition/`, so it never ships in a release zip (the zip is that
  folder alone). Keep it that way.

## Playing the game for a test: the essentials

This is what must survive a compacted chat; `playtest/PLAYTESTING.md` has the rest and wins where
they differ. In the order of [the guide's checklist](playtest/PLAYTESTING.md#2-the-checklist):

1. **The environment**: run the tools from `playtest/`, `export DISPLAY=:55` and `export
   PLAYTEST_WORK=/tmp/playtest` (the guide's `$WORK`; the default, which the shared DOSBox lock
   assumes). The game is `$PLAYTEST_WORK/inst`, from `setup_game.sh`. **DOSBox dies when the
   session sits idle**, and a worker restart takes Xvfb too: after any pause, check `pgrep -x
   dosbox` and `pgrep -x Xvfb`, restart what is gone (a lost Xvfb by hand: `setsid nohup Xvfb :55
   -screen 0 1024x768x24 &`) and reload.
2. **`sh start.sh`** starts Xvfb, DOSBox with the Loader's patched game and the dice log
   (`$PLAYTEST_WORK/dice.txt`).
3. **`sh loadsave.sh NAME`** (it runs start.sh itself) loads a save from `playtest/saves/`
   (`pens-after-arena` the usual start, `fountain-user` for a fight, spell or rule test;
   `saves/README.md` lists them).
4. **The window must be 320x240** (`xdotool getwindowgeometry`): the tools that read a raw grab at
   the game's coordinates (figcheck.py, walkprobe.py and the like) read the wrong pixels at 960x720
   (pixmatch.py's checks sample down, so they would pass).
5. **Check the build under test is in place** (`buildcheck.py`, `dec.py`).
6. **Start the watchdog** (`guard_start.sh` and a Monitor on `guard.log`).
7. **Keep a test log the user can read**, and send it as it fills.

And always:

- **Never fetch the game, Wake of the Ravager or the walkthrough from a public link, and never put a
  link to them in this public repository** (that is piracy, the user's word): they come from the
  user's **private** repository `daaki85/darksun-installation-files`, checked out beside this one
  (attach it with `add_repo` if a session lacks it), and nothing from it is committed here (the
  guide's rule 10).
- **Never cut steps out of a bigger script with sed** (its header may restart the game): use the
  small tools.
- **A second DOSBox must run under another name** (a copy of the program, as `picpattern.sh`'s
  `dbpat`): the tools attach to the newest process named dosbox and `start.sh` kills them all.
- **Press Escape only with a screen or menu up** (with nothing open it brings EXIT: SAVE GAME?), and
  **never save after a memory edit** made for a test: the game autosaves after a fight and an area
  change, so set `"autosave": false` and `"quick_save": false` first, or fight with `PT_NO_EDIT=1`.
- **The look pointer pauses the game**: while the eye is up nothing happens (no call, no alarm,
  nobody moving), so a wait with it up waits for nothing. Put the walk arrow back (`pointer.py
  walk`) as soon as a look is done.
- **Story fights go through `fightout.sh`**; never `killfoes.py` in a fight a script waits on (the
  scripts miss the kills).
- Everything else (reading the game, controls, walking and doors, talk, fights, spells, inventory
  and shops, pictures for the docs) is in the guide's [recipes](playtest/PLAYTESTING.md#recipes);
  the route through the story (new game, arena, slave pens, Kurzak's call, back to the arena) is in
  [ROUTE.md](playtest/ROUTE.md), the research recipes (memory edits for a test, sounds, the picture
  store, frame rate, the picture and the music device, the game's scripts, the recompiled program as the target, Wake of the Ravager)
  in [RESEARCH.md](playtest/RESEARCH.md), and every tool in [TOOLS.md](playtest/TOOLS.md).

**Git.** The repository is `daaki85/darksun-obsidian-edition`. Work on a `claude/<task>` branch
(Branch names, below) made from `origin/obsidian-edition`; other sessions push to
`obsidian-edition` too, so fetch and rebase onto `origin/obsidian-edition` before every push. The
work goes in by a pull request into `obsidian-edition`, which goes to `main` at a release. GitHub
deletes `obsidian-edition` when its pull request into `main` merges: then make it again from
`origin/main` and put any unmerged commits on top.

**Branch names.** A cloud session is handed a random branch name (`claude/eloquent-bohr-g8rr37`,
`ccr-7f9f358f-nn0os3`). Don't use it: this rule is the user's standing permission to push to a
branch named after the task instead. Before the first commit or push, make `claude/<task>` (never
push the random name: a session can make branches but not delete them, so it would be left behind
for the user to delete by hand), where `<task>` is two to five lowercase words joined by hyphens
saying what the work is (`claude/class-outfits`, `claude/opends-report`, `claude/gear-mark-roster`);
check `git ls-remote origin` that it is free, else add `-2`. Commit and push there, and say the name in the first reply. If the user names a
branch, or the work continues an existing branch, use that one.

**Shell.** Never `pkill -f` or `pgrep -f | kill` a pattern your own command line contains: it
kills your shell. Kill by pid, in a command of its own. Long runs go in the background with a
Monitor, and every step gets a `timeout`. Share DOSBox between agents with
`flock /tmp/playtest/dosbox.lock`; start Xvfb before taking the lock (what `start.sh` starts inside it
keeps it), and end a session by killing its DOSBox and dice log by pid. Stop only what you
started: never kill a process you can't prove is yours (an agent once killed the shared display
to free the lock, 2026-11-17); if something else holds the lock, say so and wait. A session's own
`flock` waits on its own background lock holder: with the holder running, don't take the lock again
in a step.

**Water.** Whenever a play reaches a new area, note in the test log and in [ROUTE.md's water
section](playtest/ROUTE.md#water-for-resting-an-idea-for-later) where water, jugs or waterskins
are (the user's idea of resting costing water one day).
