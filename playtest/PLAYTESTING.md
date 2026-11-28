# Playing the game for a test: read this before every in-game test

This is Claude's own guide to driving Dark Sun: Shattered Lands in a headless DOSBox, so that an
in-game test (a fix seen working, a screenshot for the docs) doesn't stall. Every rule here comes
from a test that got stuck. It lives in the repository, in `playtest/`, outside `obsidian-edition/`
(so it never ships in a release zip), because the scratch folder and everything in it is lost when
the container is reclaimed: an earlier version of this guide and its tools were lost that way.

**How to use it.** Read [the startup procedure](#startup-procedure) in full before every in-game
test and follow it in order. Then read the [recipes](#recipes) for the job in hand, [the
route](ROUTE.md) (its own page) when the party has to get somewhere, and [the research
recipes](RESEARCH.md), split by subject (memory edits for a test, sounds, the picture store, frame rate, the picture and the music device, the game's
scripts, the recompiled program, Wake of the Ravager) when a test needs memory written or the game
looked into. **Add to it after every play** ([after a play](#3-after-a-play)). How things were
found, the incidents behind the rules and the approaches given up are in [HISTORY.md](HISTORY.md),
by topic and with dates; a recipe links to its part where the story helps.

The tools are in this folder, each listed with what it does in [TOOLS.md](TOOLS.md) (made from
their own headers by `tools_index.py`). Each finds its own paths (`env.sh`, `paths.py`): the
repository, a work folder for screenshots and logs (`PLAYTEST_WORK`, default `/tmp/playtest`) and
the extracted game (`DS_GAME`, default `$PLAYTEST_WORK/inst`). Nothing in the work folder is kept.
In this guide `$WORK` is that work folder: `env.sh` sets `WORK` from `PLAYTEST_WORK` for the
tools, but a shell you type in doesn't have it, so type `$PLAYTEST_WORK` there.

# Startup procedure

## 1. The rules

1. **Keep a test log the user can read, and send it as it fills.** Write it in the work folder as
   you go (what's under test, each step, what was seen), and send it at each milestone and when
   stopping (with SendUserFile, where the session has it). At the end copy it to
   `playtest/logs/DATE-what.md` and commit it ([the logs' index](logs/README.md)).
2. **Plan the route first.** Know where the thing under test is and how the party gets there:
   the cluebook (`Cluebook.PDF` in the game folder: `pdftotext -layout`), the walkthrough ([a
   walkthrough](#the-walkthrough)), the scripts (`dec.py`, the triggers in the region's MAS
   script), the region's entities (ETAB in `RGNxx.GFF`), and [the
   route](ROUTE.md#the-route-through-the-story). Don't assume a place is reachable from a new game:
   check what the story requires (the slave pens' sewer grate, for one, is behind the stalker pen's
   secret door).
3. **Start from a saved game past the parts you don't need**: `sh loadsave.sh NAME` loads one of
   `playtest/saves/`; [its README](saves/README.md) lists them all (`pens-after-arena`, the slave
   pens just after the arena, is the usual start). None came with the game. **Save at every
   milestone** ([saving](#loading-and-saving)) and add the save to `playtest/saves/` with a line
   in its README, then commit: replaying the arena took most of a day.
4. **Never `pkill -f` or `pgrep -f | kill` a pattern your own command line contains**: it kills the
   shell running it (exit 144; [it happened twice](HISTORY.md#the-shell)). Kill by pid, found by a
   pattern your command line can't match (`pgrep -f "sh [l]eavearena.sh"`), then `kill PID` in a
   command of its own, with nothing else in it. And stopping a background task can leave its
   children running: check with pgrep afterwards.
5. **Never cut steps out of a bigger script with sed**: its header may restart the whole game.
   Use the small tools.
6. **Every step gets its own `timeout`**; long runs go in the background and are followed through
   the watchdog's Monitor, not by sleeping.
7. **Press Escape only with a menu or screen showing**: with nothing open it brings EXIT: SAVE
   GAME?, and a click after that can quit to DOS ([keys](#controls)).
8. **Never save after a memory edit made for a test** (levels, HP, Move, spells taught, items or
   classes written): restore anything raised in memory before saving or stopping. **The game now
   saves by itself** (an autosave 4 seconds after an area change or a fight's end, F5 a quick
   save): before a test that edits memory switch both off, or fight with `PT_NO_EDIT=1` ([quick
   saves and autosaves](#loading-and-saving)).
9. **The look pointer pauses the game** (the user's): while the eye is the pointer, the game's time
   doesn't run (no Kurzak's call, no alarm, nobody moving). Put the walk arrow back (`pointer.py
   walk`) as soon as a look or a rest is done; a wait with the eye up waits for nothing.
10. **The game's and Wake of the Ravager's installers and the walkthrough are the user's own
    copies**: never fetched from a public link, never linked from or committed to this repository
    (it is public; a public link to them is piracy, the user's word, 2026-11-11). They come from
    the user's **private** repository `daaki85/darksun-installation-files`, checked out beside this
    one (`$INSTALL` in env.sh, default `../darksun-installation-files`; `PT_INSTALL_FILES` to name
    another; attach it with `add_repo` if the session lacks it); nothing from it is committed here
    ([why the links are gone](HISTORY.md#the-games-installer)).
11. **A DOSBox shared with another agent**: run every play step under `flock
    /tmp/playtest/dosbox.lock`, held for the whole session by a background `flock ... -c 'while [ -e
    HELDFILE ]; do sleep 2; done'` (each Bash call is a new shell, so `exec 9>` doesn't last);
    removing HELDFILE releases it. **Everything `start.sh` (or `ravstart.sh`) starts inside the lock inherits it** (Xvfb,
    DOSBox, the dice log: [an Xvfb left from a finished session held it for an
    hour](HISTORY.md#the-shell); `lslocks` and `ls -l /proc/PID/fd` show who): start Xvfb before
    taking the lock, and end a session by killing its DOSBox and dice log by pid. Stop only what
    you started: never kill a process you can't prove is yours. With another agent's game running,
    `PT_KEEP_OTHERS=1` keeps `start.sh` from killing every dice log and DOSBox (its own first line
    does), and a game of your own beside it is [a second game](#loading-and-saving). A DOSBox found
    running that this session didn't start isn't
    restarted: play in it (`loadsave.sh` would kill it). **After a pause every flock holder is gone
    with DOSBox**, and their marker files stay (`*.held`, `*.locked` in the work folder): check
    `pgrep -a flock`, not the files. Wait for a busy lock with one `flock -w 1500`, never a polling
    loop. **With that holder running, don't take the lock again in a step** (`flock
    /tmp/playtest/dosbox.lock -c ...`): it is another open of the file, so it waits for the holder,
    this session's own, until its `timeout` (200 s lost, 2026-11-19); the holder already keeps other
    agents out, so the steps run without it. **A dice log is not under the lock**: another agent's Loader
    test once attached its dice log to a DOSBox it didn't start (2026-11-24) and wrote its own rules
    into the sequel's helper, voiding that run: check the helper's rules word (header +170) is the one
    your run set before trusting a rule's run ([the sequel's
    specialization](RESEARCH-RAVAGER.md#wake-of-the-ravager)).

## 2. The checklist

Run these in order, from `playtest/`, at the start of every test and again after any pause.

1. **The environment.** `export PLAYTEST_WORK=/tmp/playtest DISPLAY=:55` (the kit's tools set
   `DISPLAY` themselves; a loose `xdotool` command without it says "Can't open display"). Check
   `command -v dosbox` and `$PLAYTEST_WORK/inst/DSUN.EXE`; if either is missing, set the container
   up first ([setting up a container](#setting-up-a-container)). **DOSBox dies when the session
   sits idle**, and a worker restart of the session takes Xvfb with it: after any pause (waiting on
   the user), `pgrep -x dosbox` and `pgrep -x Xvfb` before the next step. A Xvfb gone isn't
   restarted by start.sh run in the background (every xdotool call: "Can't open display"): `setsid
   nohup Xvfb :55 -screen 0 1024x768x24 &` by hand. Don't leave a test half-done across a pause
   expecting it to be there.
2. **Start the game: `sh start.sh`.** Xvfb `:55`, the Loader's patched game
   (`prepare_patched_game`, so a rebuild is a restart), DOSBox, and the Loader's dice log
   (`$WORK/dice.txt`). It kills any old ones. `loadsave.sh` (next) runs it itself, so start.sh on
   its own is for a new game (`topartyfight.sh`) or the creation screen.
3. **Load a save: `sh loadsave.sh NAME`** ([loading and saving](#loading-and-saving); the saves:
   [saves/README.md](saves/README.md)). It clicks past the title, loads the save as slot 1 and
   prints `state.py` once loaded.
4. **Check the window is 320x240** (`xdotool getwindowgeometry`). The window is 640x400 until a
   save is loaded; with no `obsidian-edition/settings.json` the Loader's default is 960x720
   (window_scale 3). start.sh sets `window_scale` 1. The pixel checks (msgbox.sh, levelup.sh,
   panel.sh) go through pixmatch.py, which samples a bigger grab down to 320x240 first; what needs
   320x240 is the tools that read a raw grab at the game's coordinates (figcheck.py, walkprobe.py,
   figwatch.py, ghostturn.py), which at 960x720 read the wrong pixels (before pixmatch.py sampled down,
   message boxes and CHOOSE A SPELL went unseen that way and the loops stalled: [the
   story](HISTORY.md#the-window-size-and-pixel-checks)).
   In a detached DOSBox run, confirm the visible pointer is over LOAD SAVED GAME before clicking. The 320 × 240 window stretches the vertical coordinates of the 320 × 200 game. For the PENS save, wait until the slot list has appeared and then check the pointer over the first slot and LOAD. [Staged elf outfit test](logs/2026-11-22-elf-outfits.md)
5. **Check the build under test is in place** (after every restart: memory edits are lost on any
   restart). The game runs `obsidian-edition/dos/` (GPLDATA.GFF, DSUN.EXE's patched copy...).
   - For a DSCLOG change, **`python3 buildcheck.py`**: it compares 40 bytes of a set of routines in
     memory with `dos/DSCLOG.EXE` (name others to compare them), checks every hooked vector in
     segment 0 points at its handler (two probes on one vector once made every attack's AC 255:
     [the story](HISTORY.md#two-probes-on-one-vector-target-ac-255)), checks the tail's segment
     and data, and checks the game's item types and names in memory are the chunks of the Loader's copy
     of GPLDATA (`itemtables.py`, memory pass 7) with DSCLOG's notes of them (`types_first` 115). Compare code, not the whole image: the variables in it differ once the game runs.
     To do it by hand, take the offsets from [the helper's
     segment](../obsidian-edition/DEVELOPMENT-INTERNALS.md#dsclogs-segment) and [the far
     block](../obsidian-edition/DEVELOPMENT-INTERNALS.md#the-far-block): a tool reading the far block's data
     at the helper's segment reads stale bytes. `ghostchk.py` shows the see-through block is there.
   - For a DSCLOG2 change (Wake of the Ravager), **`python3 ravtail.py`** with the sequel running: the
     helper's tail where its header says (+1834 the segment + TAIL_PARAS), its tables as built, and what
     the Loader has written in its buffers (the USE screen's lines, the item names, the labels)
     ([DSCLOG2's segment, tail and install](../obsidian-edition/DEVELOPMENT-INTERNALS.md#dsclog2s-segment-tail-and-install)).
   - For a script change, decode the built copy (`GPLDATA=../obsidian-edition/dos/GPLDATA.GFF
     python3 dec.py SCRIPT LO HI`) and check the change is there before trusting anything seen in
     play. `dec.py` stops with "unknown term" when LO falls inside a command: start it at a command
     (or decode the whole script with `dsloader.gpl.load_scripts` and `decode`). Every script in
     the built copy should decode ([not always so](HISTORY.md#scripts-that-didnt-decode)).
   - Comparing two builds, the slow failing tests and running changed Loader code: [builds, the
     Loader and the tests](#builds-the-loader-and-the-tests).
6. **Start the watchdog: `sh guard_start.sh`**, then a Monitor on `$WORK/guard.log` (grep
   `STUCK|GONE`, with `tail -n0 -F` so old lines don't fire) for the whole test. Stop it (`kill
   $(cat $WORK/guard.pid)`) before going idle. The log keeps earlier runs' lines: read the times
   before believing one. A level-up screen shows as STUCK ([level-ups](#controls)).
7. **Start the test log** in the work folder ([rule 1](#1-the-rules)): what is under test, the
   build, the save, and from here each step and what was seen.

## 3. After a play

**After every play, add everything learned to this guide** (the user's standing instruction):
not only stalls, but every control, screen, message, map position, route step, timing, script
detail and tool change found while playing, each where it belongs (a recipe stated as current
practice; the incident behind it, with its date, in [HISTORY.md](HISTORY.md)), then commit and
push. Do it at each stop, not only at the end: a pause can lose the container.

1. Stop the watchdog; restore anything raised in memory.
2. Send the test log; copy it to `playtest/logs/`, add its line to [logs/README.md](logs/README.md),
   and commit.
3. **Water**: whenever a play reaches a new area, note in the test log and in [ROUTE.md's water
   section](ROUTE.md#water-for-resting-an-idea-for-later) where water, jugs or waterskins are.
4. Add any new kind of stall to this guide (where it belongs, or a numbered rule in
   [Fights](#fights) for a fight stall, with the test), and any new tool to this folder (a header
   comment whose first sentence says what it does, then `python3 tools_index.py`), then commit and
   push both. Edit these files at a unique anchor (assert one match, or cut at the last one): a cut
   at the first of two like lines [once lost a test log's last
   parts](HISTORY.md#the-guide-and-the-kit).
5. **Other sessions push to `obsidian-edition` too**: `git fetch origin obsidian-edition` and `git
   rebase origin/obsidian-edition` before every push, read what changed in `playtest/`, and keep both
   sessions' lessons.

# Recipes

## Setting up a container

1. Packages: `dosbox Xvfb xdotool imagemagick innoextract poppler-utils nasm python3-tk`, and
   `pip install capstone unicorn` (check with `command -v`; the environment's setup script installs
   most of them, below).
2. The game: `sh setup_game.sh` extracts the GOG installer with innoextract into `$DS_GAME`, from
   the private repository's checkout ([rule 10](#1-the-rules)): the scripts run its `join.sh`,
   which puts both installers in `$WORK/dl` (the Ravager's in three parts there, GitHub taking files
   up to 100 MB) and checks them against its SHA256SUMS. Without the checkout, put the installer at
   `$WORK/dl/sl.exe` (or name it in `PT_SL_INSTALLER`); the script stops and says so when it has
   neither. **A bare `innoextract` has no `DARKSAVE.GFF` in the game folder** (GOG's install puts
   `__support/save` in `cloud_saves`, which its DOSBox overlays on C:; Linux's DOSBox 0.74-3 has no
   overlay mount), and the game quits at START GAME with "DARKSAVE.GFF to DARKRUN.GFF failed" in
   `dos/GAMEEND.TXT` (and leaves DARKRUN.GFF empty): `setup_game.sh` copies `__support/save/*` into
   the game folder. Don't make a `cloud_saves` folder here: the Loader then writes the overlay
   mount, which this DOSBox refuses.
3. **The environment's setup script:** the user's cloud environment for this repository installs
   `innoextract nasm dosbox xdotool`, `pip install capstone unicorn`, and runs `setup_game.sh` and
   `setup_ravager.sh` when the container is built fresh; they find the installers in the private
   repository's checkout when the session has it (the environment's Repositories list must include
   it: a setup script can't fetch a private repository itself), and otherwise stop with a message.
   If the game is missing in a new session, attach that repository (`add_repo`), clone it beside
   this one and run `setup_game.sh`.
4. **A fresh container by hand**, if the setup script didn't run: `apt-get update`, then install
   `dosbox xdotool innoextract nasm` (`Xvfb`, ImageMagick, poppler were there). Then the private
   repository's checkout beside this one (or the installer at `$WORK/dl/sl.exe`, 22 MB) and
   `setup_game.sh`.

## The walkthrough

`sh setup_guide.sh` makes the user's copy of the walkthrough (from the private repository's
`guide/`, or put at `$WORK/guide/kibbitz.html` by hand) into text, `kibbitz.txt`, to search (`grep
-n -i caravan`): where things are, who sells what, quest steps and talk choices ("2-4-2"), region
by region. Someone else's work: never commit it ([rule 10](#1-the-rules)). Weigh it with the
game's data: it is one player's account.

Wake of the Ravager's walkthrough (the user's copy, already text) comes the same way, from the
private repository's `guide/wake-of-the-ravager-walkthrough.txt` to `$WORK/guide/ravager.txt`. The
sequel itself: `sh setup_ravager.sh`, the user's GOG installer (from the private repository, or put at
`$WORK/dl/rav.exe`), into `$WORK/rav`; it plays in DOSBox by [its recipe](RESEARCH-RAVAGER.md#wake-of-the-ravager).

## Loading and saving

- **Loading**: the title (two clicks), then the main menu: START GAME, CREATE CHARACTERS, LOAD
  SAVED GAME (170, 109), EXIT TO DOS; the LOAD screen lists the slots (click one at 100, 46), then
  LOAD (253, 46). `loadsave.sh` does it.
- **Saving**: Escape (nothing else open) brings EXIT: SAVE GAME? (SAVE / QUIT / CANCEL); **S**
  opens the SAVE screen: click a slot (the first at 120, 46), type a name (`xdotool type`), click
  SAVE (253, 46). "GAME SAVED", and then **the game quits to DOS** (it's the exit menu): restart
  with loadsave.sh. The slot is `SAVE01.SAV` in the game folder (85,680 bytes), with
  `CHARSAVE.GFF` and `DARKSAVE.GFF` written at the same time; keep all three (`saves/README.md`).
  QUIT on the EXIT menu ends DOSBox.
- **F1 opens the SAVE window and the game goes on after it** (F2 the LOAD window, F3 quits, F4
  music on and off: the game's own keys, on the map with nothing else up, not while a message box
  is). No quit to DOS, so it is the way to save in the middle of a test: F1, a row (the first at
  120, 46), the name, SAVE (253, 46), then a click for GAME SAVED. A key pressed with a message box
  up is lost: `dismiss.sh` first, and look at a shot before clicking in the window (a click with
  no window up walks the party).
- **The window's page buttons** are at x 253: PAGE 1 at y 76-87, QUICK at 165 (drawn 18 under
  their y in `savepages.PAGES`); rows are 11 apart from y 46 (row 5 at 90, row 7 at 112). The window opens on the
  page last shown.
- **Quick saves and autosaves** (`dsloader/quicksave.py`; the dice log does them, so `start.sh`'s
  game has them): F5 on the map saves to `SAVQ01-05.SAV`, F9 opens the LOAD window on the QUICK
  page (Return loads the newest), and an autosave goes to `SAVQ06-10.SAV` 4 seconds after an area
  change or a fight's end. **They are saves of the game as it stands: none after a memory edit**
  (rule 8), so before a test that edits memory switch them off (`"quick_save": false, "autosave":
  false` in `obsidian-edition/settings.json` after `start.sh` has written it, then restart the dice
  log), and fight with `PT_NO_EDIT=1 sh fightout.sh` (no foe's HP changed) when the autosave after
  the fight is what is under test. `loadsave.sh` copies only `SAVE01.SAV`: the folder's `SAVQ*`
  files stay from the last play (delete them for a test that counts them).
  - `qsave.py SLOT [NAME]` asks DSCLOG for a save as the Loader does and times it; `qsave.py load`
    opens the LOAD window; `qsave.py state` prints the keys, the counts, `SAVE_REQ`, the main
    loop's count, DS:0BC9h (1 on the map, 2 with a window, a talk or a screen up) and the game's
    memory; `qsave.py keys FFFF FFFF` gives the two keys back to the game (`3F00 4300` to DSCLOG).
  - `loadquick.sh [ROW]` starts the game and loads a row of the QUICK page from the main menu,
    with the folder's `CHARSAVE.GFF` and `DARKSAVE.GFF` as they are.
  - `savediff.py A.SAV B.SAV [-v]` compares two saves chunk by chunk and prints each one's name
    and journal id (`SAVE` 30, words 198-199).
  - **Two saves of the same moment**: the look pointer up (`pointer.py look`: the clock stands
    still), `qsave.py 1 NAME`, then F1 and a window save: they differ in `STXT 1` and six words of
    `SAVE 1` only (the map objects' picture slots, which a window's opening lets go of).
  - **A second game's kit made again after every change** (logs/2026-11-18-squares-in-reach.md):
    a small script that copies the tree's `playtest/` afresh, changes the display in `env.sh` and
    `paths.py`, puts the copy's own `start.sh` back and links `obsidian-edition`; and one that
    starts only its dice log again with a setting changed (by its pid file), to compare a switch
    on and off in one game.
  - **A second game beside the shared one** (when the shared DOSBox is busy): a copy of the kit
    and of `inst` in a scratch folder with the tree's `obsidian-edition` linked beside it, `env.sh`
    and `paths.py` on display `:56`, and a `start.sh` that starts its own Xvfb, DOSBox copied
    under another name (`dbq`, with `SDL_VIDEO_X11_WMCLASS=dosbox` so xdotool finds its window),
    writes its pid to `$WORK/dsun.pid` (live.py reads it) and starts the dice log as `python3 -um
    dsloader dicelog --pid PID` (not the command line the shared `start.sh` kills), stopping only
    its own by their pid files. Run a tool there through a wrapper that sets `PLAYTEST_WORK` and
    `DISPLAY` and changes to the copy's `playtest/` (logs/2026-11-18-integration.md: `:60`,
    `dbint`). `pgrep -a dosbox` also lists another agent's `dosbox-x`; `pgrep -x` tells them apart. For the sequel (logs/2026-11-25-ravager-level-cap.md): the copied
    kit's `ravstart.sh` with `dosbox` changed to the renamed copy and its Xvfb line off, `env.sh` and
    `paths.py` on the copy's display; ravstart's tools read `$WORK/rav.pid`, so a `PLAYTEST_WORK` of its
    own keeps them on the copy's game.
    `framerate.py` and the tools that look for a window of class `dosbox` on `:55` are the shared
    game's: in a copy, change the display in `env.sh` and `paths.py` only. **The copy's `inst` goes
    in its own work folder** (`$PLAYTEST_WORK/inst`, or set `DS_GAME`): `loadsave.sh` copies the
    save there and the copy's `start.sh` starts DOSBox from it. **A control run with the old
    Loader**: the kit's `obsidian-edition` a link to a detached `git worktree` of
    `origin/obsidian-edition` (its own patched files and `settings.json`), then the same steps;
    remove the worktree after (logs/2026-11-25-xp-held-at-cap.md: `:56`, `dbxp`).
  - **The arena with no memory edit** (for the autosave on an area change): `PT_NO_EDIT=1 sh
    arenatrip.sh` from `pens-after-scar` (toalarm.sh then leaves Cilla's thief level alone; the
    rests, the call and the walk went the same, 2026-11-18): "Autosave: "Auto - Day 2, 17:01 - The
    arena" (the QUICK page, slot 6)" 4 s after arriving; `loadquick.sh 6` loads it from a fresh
    start, and the walk onto the platform starts the champions' bout.
  - **Scar's trip from a save**: the arena's gate (488, 200); `viewto.py 500 380`, then clicks at
    screen (144, 140) (the gap, to 488, 424) and (150, 185) (the platform, 488, 472) with the walk
    arrow: the Announcer, then `fight_on 1`. After the bout: the "Go back to the pens" box, the
    yes/no question (N), then the autosave; dawdling brings "These gladiators wish to fight
    again!" and another bout.
  - A save takes 0.34 s (the game stands still); a fight's save is refused (`qsave.py`: "refused: a
    fight"), and with a talk or a window up the request waits (the map's loop doesn't run).
- **The save name field keeps the slot's old name**: typing goes in front of it (KURZAK DOORPENS),
  and Backspace from the start does nothing: press End, then Backspace enough times, then type.
- **The SAVE screen's EXIT** is at (253, 66): it closes the screen without saving and the game
  goes on (no quit to DOS).
- **A save with other values in it, without saving after a memory edit**: change a copy of a
  save's file in the work folder and load that (never a file in `saves/`). The journal's test
  put an id in global numbers 198-199 that way: find `SAVE` chunk 30's 400 bytes in the file
  (`read_gff`, then `bytes.find`), `struct.pack_into` at word 198, copy it with the set's
  `CHARSAVE.GFF` and `DARKSAVE.GFF` into the game folder, then the steps of `loadsave.sh` from
  `start.sh` on. The load puts the file's numbers in memory (read back with
  `dsloader.journal.read_head(gd)`).
- **The game's global numbers** (far pointer DS:1356h) were in memory in 20 reads of 20 in the
  pens, out of a fight.
- **The journal** writes `obsidian-edition/Journal/journal.jsonl` while the dice log runs
  (`start.sh`'s too): delete it before a test that counts its entries. `follow.py 29` from
  `pens-after-arena` makes Kurzak's two speeches at his stop, two entries.
- A save made in DOSBox loads on the recompiled program and the other way round ([the recompiled
  program](RESEARCH-CODE.md#the-recompiled-program-as-the-target)).

- **The stock game** (no Loader, no dice log: OpenDS's darkfix betas, or the original's behaviour):
  `darkfix_apply.py inst/GPLDATA.GFF darkfix-inst/GPLDATA.GFF FIXES` into a copy of `inst` in the work
  folder (it reads their fix files, never runs them), then `start_stock.sh` (GOG's
  `dosbox_darksun.conf` first: with our conf alone DSUN.EXE went straight back to DOS). The intro
  plays (Escape), then the main menu and loadsave.sh's clicks; the Loader's saves load in it, and
  `click.py`, `walkto.py`, `pointer.py`, `state.py` work (they read memory). No dice log: read the
  screen. **A reload replays the same rolls** (a load doesn't reseed): wait a different time before a
  roll to see the other outcome ([the grate's QA](logs/2026-11-24-darkfix-beta-qa.md)).

## Reading the game

- `python3 state.py [FLAG...]`: fight on, whose turn (0-3 the party), region, the leader's map
  position, the camera, and any game flags (`state.py 11 505`).
- **A game flag reads as 0 whenever the flags have no place in memory** (`gd.flag`: their pointer,
  DS:1352h, is null at times, such as in the arena outside a script's run). Check `gd.flags_ready()`
  before believing a 0; `state.py` prints `flags ?` when they can't be read ([an arena "flag 11
  never set" was only this](HISTORY.md#flags-that-read-0)).
- `$WORK/dice.txt`: the dice log: every roll, every line of dialogue and narration
  (`[Narration] ...`, `[The Announcer] ...`), menus with their choices, and "Message: NO PATH FROM
  HERE". Read its tail after each action; it is the most reliable record of what happened. It
  doesn't repeat a `Message:` line the same as the last one.
- `sh shot.sh OUT.png`, then Read the picture: the game's own 320x200 capture. Look at the screen
  before any key that could do harm (Escape) and whenever a step didn't do what it should.
- **Two picture sizes**: `shot.sh` saves the game's own capture, 320x200; a window grab
  (`import -window`, which msgbox.sh, panel.sh and levelup.sh use for speed) is 320x**240**, the
  height stretched: a pixel at y in a capture is at y x 1.2 in a grab. Take a pixel's coordinates
  from the same kind of picture the check uses ([panel.sh read the wrong row this
  way](HISTORY.md#the-window-size-and-pixel-checks)).
- **Pixel checks** go through `pixmatch.py` (colours within 3, a row either way, for the
  recompiled program); it uses PIL, or ImageMagick where PIL is broken ("cannot import name
  '_imaging'").
- `live.py` (exec'd by the Python tools) gives `g` (memory), `ds`, `gd` (dsloader's GameData);
  `CAMERA` (DS:1178h) and `POINTER` (DS:A133h). A script outside `playtest/` that execs it needs
  `sys.path.insert(0, PLAYTEST)` and `__file__` set to live.py's path first. `symread.py NAME...`
  reads DSCLOG's variables in the running game by name; it prints each as its first four bytes in
  memory order, not a number (`game_mask 7f008102` is the word 007Fh, `a20_lost 000083c4` is 0). **`rec.py [FIRST LAST]`**: creatures'
  combat records in hex, to find a field. More of the game's memory: [memory edits for a
  test](#memory-edits-for-a-test).
- **The parts of an AC**: run the dice log with `--all` (kill its process by pid, then `python3 -u
  -m dsloader dicelog --all >> $WORK/dice.txt` from obsidian-edition): each AC the game works out
  gets a line "AC of X against Y: 8 (base 10, armour -1, DEX -1, other +0)".
- **A read-only dice log** (`rolog.py`): to try changed dice-log code on a DOSBox whose Loader isn't
  this session's (stopping another's Loader was refused), run `rolog.py` into a file of your own:
  describe() and hp_changes() from this checkout, no writes to the game. Its pending rolls ("Dice:
  ...") and the Loader's come seconds after the lines around them: read the order with care.
  `--d20` shows each 1d20's caller code and frame (an overlay's INT 3Fh stub, `cd3f...`, in place
  of the code after the call is common in the spells' overlay).
- **Every HP change with its time** (logs/2026-11-10-held-damage.md): a poller of each combatant's
  HP (creature +0) every 10 ms, printing each change with the seconds since its start, run in the
  background just before Tab + Return, shows falls the dice log's lines merge or order differently
  (a poison landing after the next swing's line). The script is in that log; `live.py`'s
  `gd.combatant_creature`, `gd.creature`, `gd.creature_name`.
- **A blow from outside a fight is struck before the fight begins** (`orderwatch.py`: fight_on and
  the dice log every 10 ms).

## Builds, the Loader and the tests

- **Running changed Loader code in a running game: restart only the dice log.** Kill its pid; then
  `python3 -u -m dsloader dicelog >> $PLAYTEST_WORK/dice.txt` from obsidian-edition, setsid nohup
  (or `python3 -u -m dsloader dicelog --pid ... >> $PLAYTEST_WORK/dice.txt`, naming the game's
  process).
- **Check a dice log is really gone with `pgrep`** (logs/2026-11-25-ravager-blast-log.md): one
  started by `setsid nohup` inside a backgrounded bash keeps running after the job shows Done, and
  a second one then writes into the same file (every line twice, and both write the game's memory).
  Before starting one, `pgrep -af "dsloader dicelog"` and kill the old pid.
- **The old dice log beside the new one, a control on the same game** (logs/2026-11-25-ravager-save-mods.md):
  `git worktree add --detach BASE HEAD~1`, the Loader's `dos/` copies put in BASE's (`cp -n`), and BASE's
  `ravdice.py` attached with BASE's Loader on PYTHONPATH: the same rolls in both logs, the lines old and new. Both
  make the Python side's own rolls (hiding), so those differ. Why an attack line didn't break down:
  `RAV_FRAMES=1` prints the attack set-up's locals after it.
- **A queued series of runs** (logs/2026-11-25-ravager-kits.md): never edit a shell script while it
  runs (`sh` reads it as it goes, and an edit breaks the run in progress): write a new file. In a run
  script, keep the arguments in variables before any `set --` in a loop, which replaces them. A run on
  a merged build can use a second worktree (`git worktree add DIR HEAD --detach`): the tools use the
  Loader beside them (`env.sh`'s REPO).
- **A scratch copy of the mod for a Loader change**: `git archive HEAD | tar -x -C DIR`, the game
  copied to its own `PLAYTEST_WORK`, and the tools run from `DIR/playtest` (start.sh takes the
  Loader from the kit's parent folder); restart the dice log as above, from `DIR/obsidian-edition`.
- **Comparing two builds in play** (logs/2026-11-19-free-dsclog-room.md): the game's dice differ
  from run to run even from the same save (`fountain-user`'s ambush went differently each load), so
  compare the dice log's lines by their form (the THAC0 and damage parts), not roll by roll; or
  emulate both builds with the unit tests (the session's harness ran the new tests on the old
  `DSCLOG.EXE` with every always-on bit forced set).
- **Comparing two builds' memory**: `git show HEAD:obsidian-edition/dos/DSCLOG.EXE > SCRATCH` (the
  old build), copy it into `obsidian-edition/dos/` for one `loadsave.sh`, run `memaudit.py`, then
  put the new one back and `cmp` it with a fresh build; not while the unit tests run (they read
  `dos/DSCLOG.EXE`).
- **Memory at the hungry moments** (logs/2026-11-19-final-audit-memory.md): `memaudit.py` run with
  the map open, in `fountain-user`'s ambush (ten combatants), with a USE screen up, 0.4 s into a
  spell's picture (Ester's Curse, below), with Kalzith's shop up (`openshop.sh`) and after it:
  upper memory never moved (its free piece 26,256 bytes at E330h with this build, 144 bytes at
  CA00h; with 2.19.0's quick save and squares merged in, 25,712 bytes at E352h), and the conventional memory's free piece was 99,008 bytes with the map open, 134,848 with
  the USE screen, 124,608 with the shop, 100,032 with the map open again after it. Read the free
  piece, not the heap's own free (the game's heap reads 0 KB free with the map open: the map has it).
- **Another session editing the helper**: before a DOSBox run with the repository's Loader,
  assemble `dos/dsclog.asm` to a scratch file and `cmp` it with `dos/DSCLOG.EXE`: the same, and the
  tree's build is fine to run.
- **The whole suite with nothing skipped** (2026-11-19, logs/2026-11-19-merge-2.19-update.md):
  `/usr/local/bin/python3` has unicorn and capstone but no tkinter, `/usr/bin/python3.12` tkinter
  but not them: `python3.12 -m pip install --break-system-packages unicorn capstone` once, then
  `DISPLAY=:55 python3.12 -W error -m unittest discover -s tests` with the game's files below runs
  all of it (2,185 tests, 0 skipped, at the 2.19.0 merge).
- **The unit tests with the game's files** run more: `DSUN_GPLDATA=$G/GPLDATA.GFF
  DSUN_OBJECTS=$G/SEGOBJEX.GFF DSUN_RESOURCE=$G/RESOURCE.GFF` (`G=$PLAYTEST_WORK/inst`). With them
  set, only the tests that need tkinter (or a display) are skipped ([the
  list](../obsidian-edition/DEVELOPMENT.md#tests)). `/usr/bin/python3.12` has tkinter.
- **A failing tests/test_dsclog.py is slow** (each failing emulation runs to its count): 323 tests
  took 7 s passing and over 20 minutes failing, so a test run that drags means failures, not a
  slow machine.
- **A clean install and the release zip** (logs/2026-11-10-pre-merge-checks.md): the zip as the
  Release workflow makes it (`git archive --format=zip ... HEAD:obsidian-edition`), unpacked as
  `obsidian-edition/` beside a copy of the kit (`git archive HEAD playtest | tar -x`), with a game
  of its own (`innoextract` into its `PLAYTEST_WORK/inst`): `start.sh` and `topartyfight.sh` from
  that kit run the zip's Loader.
- **A DSCLOG routine tried on the live state**: snapshot `g.read(0, 0x110000)` into Unicorn, CS the
  helper's segment (the header, found by its signature `dicelog.HDR_SIG`, less its offset in the
  image), DS the game's, a HLT for the return.
- **The Loader's own window with the game** (logs/2026-11-18-modernisation-features.md): stop the
  dice log (one Loader follows a game), then `DISPLAY=:77 /usr/bin/python3.12 -m dsloader view`
  from obsidian-edition on **a second Xvfb** (`Xvfb :77 -screen 0 1280x1024x24`): the Loader reads
  the game through DOSBox's process, so its window needs neither DOSBox's display nor its mouse
  (no Ctrl+F10), and it connects by itself ("Connected to the game (process N)"). `import -window
  root` on that display for a picture; `xdotool mousemove X Y click 1` for its tabs (Journal at
  828,132; the Show box at 775,200, its Quests row 99 below). The window tests' display can be
  the same one. A DOSBox killed under a window that attached by itself shows
  "Disconnected (Read at ... failed: [Errno 5] Input/output error). Waiting for the game..." (the
  Reconnect path says "process N has ended"); either way no party table error. **`start.sh` starts no Xvfb when any Xvfb is running** (`pgrep -x Xvfb`): with
  `:77` up, start `:55` by hand first. Look at the Characters tab once: an error there shows as
  a line in the dice log's pane ("Loader error in the party table") and only with a game attached.
- **The Loader's own start of Wake of the Ravager with GOG's DOSBox** (`play --ravager`, `launch --ravager`
  with the GOG engine): it runs the sequel folder's `DOSBOX/DOSBox.exe`, a Windows program. On a **copy** of
  `$WORK/rav`, replace it with a bash shim that drops `-noconsole` and execs `/usr/bin/dosbox "$@"`, and copy
  `__support/save/*` into the folder first (as `ravstart.sh` does; without them the game stops at once with
  `DARKSAVE.GFF to DARKRUN.GFF failed`). `play.log` in `obsidian-edition/` says when the dice log
  attaches ([the run](logs/2026-11-27-ravager-ingame-rolls.md)).
- **The Loader window's Help**: in this container `gio` takes the URL and finds no browser, so
  nothing opens; the status line names the guide either way.
- The kit drives the recompiled program as well (`PT_TARGET=recomp`, `start_recomp.sh`): [the
  recompiled program](RESEARCH-CODE.md#the-recompiled-program-as-the-target).

## A game in DOSBox-X

The Options tab's DOSBox-X engine, the default (`dsloader/dosboxx.py`; logs/2026-11-18-dosbox-x.md, the
experiment, and logs/2026-11-19-dosbox-x-engine.md, the engine as built). It is always **a game
of its own beside the shared one**: its own display and work folder, never `:55` or
`/tmp/playtest`. `PT_DISPLAY` names the display for every tool (`env.sh`, `paths.py`; default
`:55`), `PLAYTEST_WORK` the work folder, whose `inst` is a copy of the shared game folder (36 MB).

- **DOSBox-X itself**: 2025.01.01 or later (Ubuntu 24.04's package is 2024.03.01: too old).
  Built here from the project's GitHub source in 6 minutes (`apt-get install libsdl2-dev
  libfluidsynth-dev libgl-dev libxkbfile-dev libxrandr-dev libasound2-dev libsdl2-net-dev`, then
  `./autogen.sh && ./configure --enable-sdl2 && make -j4`; the program is `src/dosbox-x`). It is
  lost with the container: build it again.
- **`PT_DISPLAY=:59 PLAYTEST_WORK=DIR sh start_dosboxx.sh /path/to/dosbox-x [name=value ...]`**
  starts the mod in DOSBox-X with the Loader's own configuration for it (window single, no quick
  saves or autosaves), an Xvfb on that display if there is none (1600x1000), and the dice log
  (`$WORK/dice.txt`). `PT_SAVE=NAME` loads a save as `loadsave.sh` does. `cycles=N`,
  `core=normal`, `window_scale=3`, `picture=tv`, `fullscreen=true`, `soundfont=FILE` after the
  program change the configuration. It stops only the DOSBox-X and dice log it started before
  (pid files in the work folder).
- **How the tools find a DOSBox-X game**: by its pid in `$PLAYTEST_WORK/dsun.pid` (`live.py`
  reads it before looking for the newest process named dosbox; the start script writes it). The
  Loader's `connect` then reads that DOSBox-X's memory file, named in the configuration its
  command line gives (`dosboxx.process_memory_file`), or in the Loader's `game.lock` for a game
  the Loader started. So each shell needs only `PT_DISPLAY` and `PLAYTEST_WORK`; state, click,
  walkto, route, follow, scroll, memaudit, buildcheck, qsave, framerate, altflag, tabhit,
  hoverlabel, squarewalk, movestate, foepos, panel, dismiss, fightout and toarena all ran
  unchanged. `DSLOADER_MEMORY_FILE` (and `DSLOADER_MEMORY_PID`) in the environment name a file
  outright.
- **A game the Loader itself started** (its window's Start the game, `launch`, `play`, or
  `launch.launch()` from a script): `sh dbxadopt.sh` writes its pid from `obsidian-edition/game.lock`
  into `dsun.pid` and moves the window to 0,0. With `play` or the window there is no
  `$WORK/dice.txt` (the dice log is inside the Loader), and the tools that read it (dismiss.sh's
  question check, toarena.sh, fightout.sh's waits) want one: start the game with a few lines of
  Python that call `launch.launch(game_dir, "a test")` and then `launch.release_game()` (the game
  runs on and `game.lock` keeps its pid and memory file), and then `python3 -u -m dsloader dicelog
  > $WORK/dice.txt` with no `--pid` (it finds the game by the lock file's memory line).
- **The Loader refuses a start while the last game still runs** ("The game started from this
  Obsidian Edition folder earlier is still running"): DOSBox-X takes a second or two to close
  after `kill`, so wait four seconds, or for the pid to go, before the next start (a start one
  second after the kill failed twice, 2026-11-19).
- **The menu's clicks want the title past**: two clicks, then 15 seconds, before LOAD SAVED GAME
  (12 was too short once, and the clicks landed on the menu as it came up).
- **`shot.sh` doesn't work** (it presses 0.74's Ctrl+F5 and looks in GOG's capture folder): `import
  -window root -crop 320x240+0+0 +repage OUT.png` on the game's display, the window at 0,0.
  A grab taken as the pointer moves can show its arrow twice.
- **`start.sh`, `loadsave.sh` and everything that calls them (toalarm.sh, arenatrip.sh,
  loadquick.sh, picstart.sh) are the shared game's**: they kill every process named dosbox. For a
  trip, load the save yourself and run the steps after the loadsave line.
- **DOSBox 0.74 beside it, for a comparison**: a copy of `/usr/bin/dosbox` under another name
  (`db74`), started with GOG's configuration and the Loader's (`launch.write_conf` with `engine`
  "gog"), `SDL_VIDEO_X11_WMCLASS=dosbox`, its pid in `dsun.pid`, the dice log with `--pid`. One
  game at a time in one work folder: both engines share `obsidian-edition/dos`.
- **Full screen needs a window manager**: on a bare Xvfb SDL2 says "switched to full screen
  mode" and the window stays 640x400. `apt-get install openbox`, `DISPLAY=:58 openbox &` on an
  Xvfb of the size wanted (1280x720 shows the black bars of a wide screen).
- **The pointer's speed in a larger window**: with the mouse captured, `xdotool
  mousemove_relative 60 60` and the game's pointer (DS:A133h) before and after: 20 across and 16
  down in a Triple window on both engines.
- **`dosboxx_memtest.py /path/to/dosbox-x`** needs no game: it starts DOSBox-X with a memory
  file and a 26-byte DOS program and says whether a second program reads and writes the file (by
  file reads and by a mapping), whether DOSBox-X can be held still, and whether a write to code
  is acted on. It is the check for Windows and macOS (its header has the owner's instructions);
  on Linux it passes.
- **Ending it**: the game's own QUIT (Escape with nothing up, then QUIT at 130, 104) closes
  DOSBox-X about 4 seconds later, with `dos/GAMEOK.TXT` written; the Loader then removes the
  memory file and its `game.lock`. To watch an end, poll the process (`/proc/PID/stat`), `ls
  /dev/shm`, the lock file and `obsidian-edition/Journal/quests.json` every tenth of a second
  from before the click (the first such watch showed the Loader reading on for 16 s after
  DOSBox-X had gone). The mouse is let go with Ctrl+F10 (`xdotool key --window $W ctrl+F10`)
  before clicking in the Loader's window on the same display, and taken again by a click in the
  game's.
- **An autosave or a quick save in a DOSBox-X game**: `start_dosboxx.sh` writes `autosave` and
  `quick_save` false; set them true in `obsidian-edition/settings.json` after it and restart the
  dice log alone (kill `dice.pid`'s pid, then `python3 -u -m dsloader dicelog --pid $(cat
  $WORK/dbx.pid) >> $WORK/dice.txt` from `obsidian-edition/`): it reads the settings once, at its
  start. A fight won with no edit then autosaves (logs/2026-11-21-dosbox-x-unchecked.md:
  `fountain-user` won by Tab + Return and `PT_NO_EDIT=1 fightout.sh`, 5 rounds).
- **The sound of a DOSBox-X game, into a file**: `PT_SDL_AUDIO=disk PT_AUDIO=$WORK/audio.raw` and
  `soundfont=/usr/share/sounds/sf2/TimGM6mb.sf2` after the program (`apt-get install
  fluid-soundfont-gm`): DOSBox-X's own mix, 48 kHz stereo 16-bit, the Sound Blaster's effects and
  the music (the Loader's `mididevice=synth` plays into that mix; DOSBox-X's log says "Opened
  device:synth"). `sox -t raw -r 48000 -e signed -b 16 -c 2 audio.raw out.ogg trim 70 40` makes a
  clip. Its other FluidSynth, `mididevice=fluidsynth`, needs a sound server (no music here:
  logs/2026-11-21-dosbox-x-unchecked.md part 3).
- **More upper memory in DOSBox-X** (logs/2026-11-25-dosbox-x-upper-memory.md): `extra=dos|umb
  end=FBFF extra=dosbox|rom bios allocation max=16 extra=dosbox|rom bios minimum size=16` gives
  48 KB more (CC00-FBFF; `memaudit.py` free upper 16,368 to 65,520 bytes), the game played a
  fight with it. `umb end` past EFFF without the two BIOS lines turns upper memory off.
- **A killed DOSBox-X leaves its memory file** in /dev/shm (32 MB): the next `start_dosboxx.sh`
  removes it, the last one's by hand (`$WORK/memfile.path` names it).
- **`codepatch.py [SECONDS] [game]`**: is a write to code acted on at once (the helper's own
  counter, or the game's main loop).

## Controls

- **Clicks**: `python3 click.py X Y [left|right|none]` in game pixels (320x200). DOSBox captures
  the mouse, so the tool moves it relatively until the game's own pointer reads X,Y. Plain
  `xdotool mousedown/up` clicks where the pointer already is (fine for dismissing a message).
  **A slow press** (point with `click.py X Y none`, wait, `xdotool mousedown 1`, 0.15 s, `mouseup
  1`) where a quick click gets lost (a scroll's spell icon, a body, the USE screen's buttons).
- **The pointer**: a right-click on the map cycles it: the plain arrow (Walk, and use/talk on a
  thing), the sword (attack), the **eye (look: opens doors)**, back to the arrow.
  **`pointer.py walk|look|attack`** reads the mode from memory (DS:11B8h: 1 the arrow, 4 the sword,
  2 the eye) and right-clicks on bare floor until it is the one wanted (right-clicks guessed from
  shots [left the sword up](HISTORY.md#the-pointer)). **Right-click only on empty floor**: on a
  party member it opens the USE screen (Escape closes it). Over bare floor the sword and the eye
  show red with a bar (nothing to act on), over a wall a red "no" sign; over a door the eye is
  plain. Only walkable ground takes a walking click (the user): a click on a wall does nothing, and
  a walk tool clicking in eye mode looks at the floor and nothing moves. The look pointer pauses
  the game ([rule 9](#1-the-rules)).
- **Alt, for "show what can be used"** (dsloader/usable.py): `xdotool keydown --window $W Alt_L`
  holds it (the BIOS flag 0:0417h reads 08h at once) and `keyup` lets go; `altflag.py` prints the
  flag and whether the marks are up, `altflag.py latency N` times them, `altflag.py watch SECONDS`
  follows the flag, fight_on, the rings' table and colours and the label slots. **`shot.sh` takes
  no picture while Alt is held** (Ctrl+F5 becomes Ctrl+Alt+F5, DOSBox's video capture, which
  writes nothing), and the flag written in memory doesn't hold (DOSBox's BIOS cleared it within
  half a second): hold the key and grab the window (`import -window`, scaled 200% for a doc picture: 640x480, the
  window's shape; `-sample '320x200!'` drops rows through the names' letters). **With
  Alt down, Tab and Return are Alt+Tab and Alt+Enter to the game** (and Alt+Enter is DOSBox's full
  screen): no fight tool works with the key or the flag left down, so let go before `fightout.sh`.
  DOSBox lets go of every key when its window loses the focus (`xdotool windowfocus` of another
  window cleared the flag at once).
- **Message boxes** (a speech box with a portrait at the top, or the grey message window) take a
  click to go away, and while one is up Tab, Return, map clicks and drags do nothing. `msgbox.sh`
  tells whether one is up; **click ON the box** (`boxclick.sh`: 160, 20): a click wherever the
  pointer was [leaves the box up](HISTORY.md#message-boxes-and-yesno-questions). `dismiss.sh`
  does this for several. **Once a fight is on, boxclick.sh clicks the map**: on a member's turn its
  clicks at 160,20 walk it.
  **In Wake of the Ravager** the grey box waits the options' message time, and a click anywhere or a
  key closes it at once and is used up by it (2026-11-27, [the sequel's scenes, pointer and message
  box](RESEARCH-RAVAGER.md)); its films and narrated opening show the arrow and skip on a click.
- **YES/NO questions** ("Yell something back at the Announcer? (Answer Yes or No)") look like a
  message box, but a click doesn't answer them: press **N** (or Y). One is waiting only while the
  dice log's last line is `    2. No` (answered, `    > No` follows): a check for "2. No" in the
  last few lines takes an old, answered one for a new one. `dismiss.sh` stops at one.
- **The function keys on the map**: F1 the SAVE window, F2 LOAD, F3 quits (never press it), F4
  music ("MUSIC OFF" / "MUSIC ON" messages), F5 the mod's quick save and F9 its quick load (the
  game's own: F5 draws the view again, F9 breaks a camp; neither shows anything in the pens), F6,
  F7, F8, F10, F11 and F12 nothing seen. DOSBox's own are Ctrl+F-keys.
- **The game's own keys on the map** (read from its three key tables, logs/2026-11-18-modernisation-features.md;
  the table with what each does is HOW-THE-GAME-WORKS.md's "The game's keys"): the root's table at
  DSUN.EXE 1BC5Bh (26 keys: 1-6, P, N, Space, F5, F6, F9, F10, Home, End, the arrows, PgUp, PgDn,
  Alt+F1, Alt+F2, Alt+F4); the map overlay's (4272h, file 71C1Bh, 33 keys: Esc, 1-4, =, Tab, Q, W,
  T, A, S, G, H, Alt+X, Ctrl+C, M, ?, Space, F1-F6), where **A and F6 switch animations on and
  off** and S, T, M and ? do something only with DS:11B0h non-zero (never in play); and its
  letters' jump table (71BE3h, c to v: C, E, I, U, V the screens, O and P one routine). **Free
  letters: B, D, F, J, K, L, R, X, Z** (the mod has L and R). `gamekeys.py` prints the tables
  (and `gamekeys.py dis START` disassembles a handler); an overlay's routine is found from its
  stub (the stub segment's dword at +4, plus 52EB0h, plus the entry's offset).
- **R in a fight hides and shows the squares in reach** (the Loader reads it from the BIOS keyboard
  buffer, 0040:001Ah-003Dh: `xdotool key r` works; the game does nothing with it): the dice log's
  line "Squares in reach: hidden (R shows them)", "Squares hidden" over the member, and
  `squares_shown` in settings.json, which **stays as the last test left it**: check it before a
  test that looks for the crosses.
- **Keys**: Tab picks the nearest enemy and Return attacks it (the mod's keys, in a
  fight); L shows or hides the combat log panel; **E opens the Effects screen** (not "end turn");
  Escape closes a screen or menu that is open, and **opens EXIT: SAVE GAME? when nothing is**: a
  click after that can quit to DOS. Press Escape only with a menu or screen showing. I opens the
  inventory, U the USE screen.
- **The pointer in a scene** (logs/2026-11-18-audit-fixes-2.md): START GAME's first scene, the
  king's decree, shows DSCLOG's arrow; `xdotool mousemove_relative -- 25 8` moves it (click.py
  reads the game's pointer, which a scene doesn't move), shots 0.7 s apart show it following. The
  decree is a still picture and plays to its end whatever is clicked; the arena's speech after it
  takes a click.
- **Ending a turn by hand**: [Fights rule 8](#fights) (a click ON the figure opens its END menu, E
  there is END TURN; E with no menu up opens the Effects screen).
- **Level-up screens block everything**: CHOOSE A SPELL (a preserver's new level, mid-fight) waits
  for a spell's icon to be clicked; the watchdog reports it as STUCK. `levelup.sh` finds it (its
  scroll's rollers) and clicks the first spell (113, 71: the grid of [CHOOSE A SPELL at
  creation](#the-creation-screen)); fightout.sh runs it each turn. PICK A PSIONIC POWER (a
  psionicist's level) isn't levelup.sh's: click a red power's icon (about 158, 62), then FINISHED
  (112, 139).
- **A turn with nothing in reach stalls `toturn.sh`** (logs/2026-11-26-sl-saves-scout.md): its E for a
  turn that stays up opened Ester's Effects screen in the slave pens' ambush and the turns stopped there;
  close the screen (Escape, a screen being up) and end the turn by hand.
- **The combat log panel covers the bottom right** (x 135+, y 120+): a click there lands on the
  panel, not the map, and a party member's figure under it can't be clicked (its END menu). Hide it
  before walking near it (the party's first step into the arena, for one, is right above it) with
  `sh panel.sh hide|show` (on the map only: with a window, a screen or a member's END menu up the
  Loader puts the panel away, and it reads "hidden" though L's choice is "shown"), which checks the panel's pixel before pressing L (L alone toggles, and
  can leave it the wrong way round). `panel.sh` reads a docked panel's frame pixel (140,150), so
  it reads "hidden" when the panel is expanded (its check is for the small panel): look at a shot,
  and press L yourself. Expanded, the panel covers the screen's right half from y 68 (docked from y
  120), and a figure under it can't be clicked: drag the view (`scroll.py -96 0`) first. Out of a
  fight the panel shows only after `L`. More on the panel's buttons: [the combat log's doc
  pictures](#pictures-for-the-docs).
- **The panel's buttons** (measured 2026-11-17, logs/2026-11-17-ingame-doc-checks.md): the
  header's buttons are on the same x docked and expanded, at y 122-131 docked (centre 127) and
  70-79 expanded (centre 74): **L** 245-254 (hides the panel, as the key does), the level chip
  256-290 (centre 273: a click goes Least -> Short -> Detail -> Least), **-** 292-300 (296) and
  **+** 302-310 (306; the expanded panel has none). A press anywhere right of 292 in the header
  row resizes: left of 302 smaller, else bigger. The expanded panel's filter chips are at y 84-92
  (All 142-157, Party 160-193, Damage 196-237, Saves 240-274); a filter chosen stays (Party leaves
  out the foes' attacks). The panel remembers its size and level across loads (the settings'
  `combat_log_level`, `combat_log_size`; `combatlog.level_rect`, `key_rect`, `filter_rects` give
  the rectangles, x + 136 and y + the panel's top). The mouse wheel doesn't reach it under DOSBox;
  a click on the scrollbar's track above the handle (309,140) pages up.

## Walking, the view and doors

- **Walking**: `python3 walkto.py X Y` (map units). Screen = map - camera, 1 unit a pixel; the
  camera scrolls in steps and does NOT keep the leader centred, so work from the camera, never the
  screen centre. **The view can stop scrolling** with the leader at an edge, so nothing beyond it
  can be clicked; resting the pointer on the edge doesn't scroll it, and writing DS:1178h
  (`camera.py X Y`) changes the number but not the picture (it's a copy, not what's drawn): drag
  it ([in the arena](HISTORY.md#the-view-and-scrolling)). A click on a wall or off the walkable
  area does nothing but log "NO PATH FROM HERE"; walkto stops after two clicks that don't move the
  leader. walkto.py drags the view back to the leader when it falls behind.
- **Scrolling the view: drag with the middle mouse button** (`python3 scroll.py DX DY`; the user's
  advice). It moves the map like grabbing it: dragging down shows more of the north (60 pixels
  moved the camera 48 map units, in steps of 16). **Keep the pointer off the screen's edges while
  dragging**: at an edge the view scrolls by itself the other way ([runaway
  drags](HISTORY.md#the-view-and-scrolling)). scroll.py starts each drag on the side it moves away
  from and caps it (270 x 150 pixels). Then click the spot and the party walks there, finding its
  own way round walls. **After a drag, release every button** (scroll.py does): the game took no
  clicks at all until they were. **A message box blocks drags too**: drags made under one did
  nothing, and the view later jumped. Clear boxes first.
- **In the enemies' turns the view follows the one acting** (`ghostturn.py`): a test that needs a
  still view through an enemy turn (a figure redrawn or not) can't rely on it; the move redraws the
  whole view by itself. **In a fight the view barely drags** in one place: two drags of 150 moved
  the camera from (1728, 768) to (1712, 832); the party's figures stayed on the screen. Drag out
  of a fight to put a figure off the view. On a party member's turn at the fountain and in the
  arena `viewto.py` did drag it, 100 to 200 map units, and the view moved by itself when a member
  walked out of it (logs/2026-11-18-squares-in-reach.md).
- **The walkability grid**: each region has one, 128 x 98 squares of 16 map units (GMAP in
  RGNxx.GFF): 0 floor, 192 walls, 64 things (furniture, a button on a wall), 1-31 and 64-95 wall
  edges and doorways. The game's live copy (far pointer at **DS:0556h**, `live_map()` in live.py)
  also has closed doors and gates (192, 193, 204, 205) and figures (96). `route.py TX TY` finds a
  path on the live grid and walks it in clicks near the leader, preferring squares with floor all
  round and two squares deep to the south: **walls are drawn with height, so a wall's face covers
  the floor squares north of it, and a click there is a click on the wall** (NO PATH FROM HERE).
  The camera at DS:1178h is the real view (screen = map - camera; checked by drawing the grid's
  walls over a screenshot); the view stays put while the party walks, so bring it back
  (`viewto.py`) when the party nears an edge. `route.py` says NO ROUTE when a closed door cuts the
  way: the region file's grid didn't show that.
- **route.py** skips squares a figure stands on (96: a party member there takes the click and
  nobody walks), drops a square whose click moved nobody, and brings the view to the way ahead
  when nothing nearer the goal is on screen (the view on the leader can hide the way, as the hall
  south of Kurzak's stop). **It won't walk through a figure**: with someone standing in front of
  Kurzak's entryway it found no way south from his stop and gave up, though the live grid showed
  the doorway clear. Walk round with clicks, or wait for the figure to move.
- **Long walks: hop.** A click a few hundred map units away walks the party there, round walls
  (1672,344 to 1400,344 in the pens), but a click across a whole region says NO PATH FROM HERE,
  and the view snaps back to the party. Plan hops on a map picture (`mapshot.py`, next) and
  use `viewto.py X Y` to bring each hop's spot on screen before clicking it; clicks on walls or
  on the edge of the screen (often a wall) do nothing.
- **Map pictures**: `python3 mapshot.py OUT.png [W H]` steps the view across the region and
  pastes the captures at their cameras: one map unit a pixel, so a point's pixel is its map
  position. Keep a region picture worth having in `playtest/maps/` (none is there yet).
- **Opening a door (the user): the look pointer.** Cycle the pointer with right-clicks to the look
  cursor and click the door; then, with the walk arrow, click on the far side of the open door to
  move past it. The walk arrow on a door, or on the floor beyond a closed one, does nothing.
  **A look click on an open door closes it**: check a shot before clicking a door. `python3
  doors.py` lists the closed doors and gates on the edge of the area the party can reach (live
  grid 192+ where the file's grid has a doorway), with their map positions.
- **`doorpath.py TC TR`**: the shortest way to a square through closed doors too, listing the doors
  it crosses and its turns; `BLOCK="C,R C,R"` rules out squares (a locked door).
- **Look needs line of sight**: "NO LINE OF SIGHT" from a party round a wall corner, and still
  from beside the pens' gold post at (1528, 456) (whatever part of it was clicked).
- **Moving the party in memory** (for a check where the way is shut): `teleport.py X Y CX CY`
  writes each of map objects 0-3's x, y words at DS:669Dh + 32n (map units) and the camera at
  DS:1178h; then walk one step with `walkto.py`: the game redraws and makes the objects near the new
  place. Only for checks; the scripts see none of it.
- **Where the party's figures are**: `memberpos.py N` out of a fight gave the leader's place for
  every member: find the figure on a shot. In a fight it gives member N's figure on the screen, and
  can miss a figure in a crowd (about 12 pixels higher opened the END menu): check a shot first.
- **Timing a walk**: `walktime.py N X Y [DIR]` (about 0.07 s a step, see-through or not; for frames,
  crops of `import` grabs, 120,50 70x70, tiled with montage).

## Talking

- **Talk menus** (WHAT DO YOU SAY?): click the line, or press a number key: 1-5 choose the line at
  once, as the manual says (`xdotool key --window $W 2` chose Kurzak's second line, 5 his Goodbye).
  **6 does nothing**: Kurzak's Goodbye, his sixth line, takes the down arrow at 311,187 and then a
  click on it at 30,189. The game's talk key table, DSUN.EXE 7DDB0h: 1-5, Y, N, Up, PgUp, Down,
  PgDn; the Loader takes none of them ([an earlier note said they did
  nothing](HISTORY.md#message-boxes-and-yesno-questions)). The list scrolls: its down arrow is at
  (311, 187), and the last visible line is about y 189. The dice log lists every choice with a
  number, which helps find the one wanted.
- **Talking to someone who walks** (the Trustee): wait where his rounds pass (his thing from
  `gd.combatants()`, his place at DS:669Dh + 32n), and when he is on screen and near, `pointer.py
  look`: the eye pauses the game, so he stops. A slow press on his figure (about 12 pixels above
  his feet; a red eye means bare floor) opens the Look box; its first button (left, about 188,158
  when the box is low) talks. Escape doesn't close a creature's Look box: its fourth button (the
  plain rectangle at its bottom right, about 245,115 for a box at 171-263, 49-124) does, and the
  mod's whole description of a monster then comes in the dialogue window (Continue, 24,157). A YES/NO question first: Y or N.
- **The Trustee's pocket** (his talk's "(PICK THE TRUSTEE'S POCKETS)"): offered only if the one
  talking is a thief, within 4 squares of him as the talk opens, and the key isn't stolen (flag 55;
  script 146 at 884h-8ABh): a talk opened from the Look box across a room has no such line. "You
  find a key!", then Goodbye hands it over (GIVE at 0ABh, to the one talking; at his feet if that
  fails) with 250 XP. The key's icon (picture 2161, 12 x 5) is a faint grey key on the grey cell,
  near invisible at the game's size: hover the cell for "SLAVEPEN KEY" (logs/2026-11-08-trustee-key.md).
- **Picking a pocket:** U, the thief's portrait (Cilla 108,108), the purse under the spell counts
  (157,145, a slow press: the USE screen closes), then the talk pointer on the person. The result
  is a narration box with a Continue line (click it, 30,157). From `pens-after-scar`
  (logs/2026-11-07-release-check.md): walkto (1816,408), (1704,408), (1592,440), `viewto.py 1592
  470`, and Kurzak stands just south of the party (thing 47 at 1592,504; his figure at 190,118).
  A failure the thief slips away from can be tried again at once. `pocket.sh X Y NAME`: one pocket
  try by the thief at USE-screen portrait X,Y on NAME; its result window wants the key 1.
- Kalzith's talk and shop, and another speaker's talk put on him for a test: [Kalzith](ROUTE.md#kalzith).

## The creation screen

- **The main menu**: it comes about 30 s after the two title clicks (a CREATE CHARACTERS click
  before it does nothing: shoot, then click). If `click.py` reads the pointer stuck at (160,100) and
  clicks do nothing, the mouse isn't captured yet: `xdotool windowfocus W`, then `xdotool mousemove
  --window W 160 30 click 1`, and it follows.
- **The creation screen** (logs/2026-11-08-creation-least.md): the main menu's CREATE CHARACTERS
  (165,92) opens VIEW CHARACTER (its bottom icons: view character, inventory, cast, effects at x 52,
  76, 100, 122, y 171; RETURN TO GAME 266,172 goes back to the menu); right-click an empty slot
  (64,52) for NEW / ADD / CANCEL, and NEW (110,57) opens the creation screen with a human fighter.
  A score's **small square** (x 6; STR y 140, DEX 146, CON 154, INT 161, WIS 167, CHA 174) takes
  the clicks, not the number: right-click lowers by 1, left-click raises, kept between the least
  and the most, going round past either (with the as-rolled rule a round trip upward is cut to
  what's spare). `leasts.sh` reads each score's least (`creationscores.py`). EXIT (278,160) leaves
  without keeping the character. The screen's memory (its sheet, the least and most, the stand-in
  sheet): [the creation screen in memory](RESEARCH-MEMORY.md#creation-and-levels).
- **AGE and the dice log** (logs/2026-11-19-older-loader-bugs.md): the screen's AGE (155,97 rolls
  the die, AGE under THAC0: crop a shot at `80x10+150+176` and scale it 300% to read it) is the age
  the character keeps (DSCLOG's roll, put in its sheet at DONE). The dice log gives no age while the
  screen is up, and at DONE `NAME is N (a human: 15 + 1d8 = k, as the creation screen rolled)`.
  Before the fix (origin up to 2026-11-19) it gave the screen's stand-in an age of its own each roll
  (`NAME is N (... = [k])`), which disagreed. The stand-in is a party slot (`gd.creating()` True;
  the first character's in member 0, the second's in member 1) that starts with the creation
  sheet's last age bytes. `sheetinfo.py`, or `aging.age_of(gd.sheet(M))` through live.py, reads
  the age kept.
- **The race**: the big portrait (40,60) steps through the portraits, and with them the race and
  sex: read the sheet's +18h after each click (two clicks a race: 1 human, 2 dwarf, 3 elf, 4
  half-elf ... 7 mul). The race text and the small figure at the top don't change it (the figure
  rolls a new character).
- **The full-length picture** (top left) is the inventory's painting for the classes picked
  (logs/2026-11-27-creation-inventory-pictures.md): DSCLOG's CREATION_PORTRAIT gives the game the
  inventory's key when it draws it (a race or portrait click, the screen opening), and FIG_DRAWS draws it
  again after a class click; with no class picked it is the game's own. The sequel's the same (DSCLOG2's
  CR_FIGURE, CR_DRAW from KP_CLASS and CR_HP). Crop a shot at `110x120+0+0`.
- **The figure at the top** wears the class's outfit (logs/2026-11-27-creation-figure-outfits.md):
  crop a shot at `60x45+130+12` and scale it 400% to see it; it changes at each class, race or
  portrait click. Read the game's blob of the screen's figures with `creationfigure.Figures(gd)`
  ([RESEARCH-MEMORY.md](RESEARCH-MEMORY.md#creation-and-levels)).
- **The classes**: click a name (x 250; cleric 13, druid 21, fighter 29, gladiator 37, preserver
  45, psionicist 53, ranger 61, thief 69); a human's class must be clicked off before another is
  chosen.
- **A priest's sphere and a psionic discipline**: the **CLERICAL SPHERE** list is in the lower
  window (AIR 240,105, EARTH 113, FIRE 121, WATER 129; AIR is marked first); **VIEW PSIONICS**
  (240,138, in the KITS button's place on the kit page) shows the disciplines (P-KINESIS 250,106,
  P-METAB 114, TELEPATHY 122), VIEW SPHERES back. In both, while one is marked the others are greyed
  and take no click: click the marked one off first.
- **A kit** (logs/2026-11-15-kit-rebalance-checks.md): KITS (232,138) opens the kit page, where NO
  KIT (240,106) is marked and must be clicked off before a kit takes a click; the class's three kits
  are at y 114, 122, 130 (fighter: Myrmidon, Sentinel, Ravager; gladiator: Champion, Twin-blade,
  Brute; ranger: Stalker, Justifier, Seeker; thief: Swashbuckler, Assassin, Shinobi; preserver:
  Scholar, Battle Mage, Arcanist; cleric: Elementalist, Healer, Crusader, the Healer offered with
  WATER marked; druid: Warden, Lifebinder, Wanderer); a multiclass race's own kit is the only row (a
  mul druid/fighter: WILD FURY; a dwarf fighter/thief: G-FIGHTER, WAYFINDER). `sheetinfo.py` lists
  each member's classes, kits and weapon specs by name; `known.py M` its spells; `canuse.py M
  TYPE...` the kit rules for item types; `carried.py NAME` what it holds.
- **A kit in Wake of the Ravager** (logs/2026-11-25-ravager-kit-choice.md; `ravclick.py`, its
  coordinates the same 320x200 game pixels): from the main menu CREATE CHARACTERS (160,92); the
  roster's slots are 2 by 2 (portraits at 70,56, 120,56, 70,112): a right click on an empty one
  brings NEW / ADD / CANCEL, NEW just under the click (slot 1 110,57, slot 2 160,57, slot 3
  140,117). The class list is at x 255 from fighter's y 29 (the same order and spacing as SL's), a
  class clicked off before another is taken; KITS (234,138), NO KIT 106 and the kit rows 114, 122,
  130 at x 250, VIEW PSIONICS (260,138) back, DONE (271,182). `ravkits.py page` reads the sheet
  being made (race, classes, kit byte) and which window is up (3022/3023/3026+ the KIT PAGE's,
  19504/19505 the game's own: no KITS button), and its hit points with their least and most and its PSP
  (a Battle Mage's, Arcanist's or Mind Warrior's rolled again as the kit is chosen:
  logs/2026-11-26-ravager-kit-psp-hd.md, step 3). A new character there is 7th level (a preserver with
  CON 18: 21 to 42 hit points). A member's menu (a right click on its roster portrait) has EDIT at
  (110,57) for slot 1 and DROP 10 below: a click a little low drops it (CANCEL at 110,82). **STORE and RECALL** in the sequel (2026-11-25,
  logs/2026-11-25-ravager-store-gear.md) at (114,192) and (175,192), under the hit points and PSP; the die
  (145,92); `ravstore.py roll` prints the roll on screen and DSCLOG2's counts, `ravstore.py gear` the
  starting gear's flags (GEAR_DONE holds DONE for the Loader: the dice log must run). The sphere list's
  AIR (240,106), FIRE (240,122). The roster's slot 4 NEW at (162,117). **DUAL**: the roster's inventory (75,171), a right
  click on the member's portrait (30,69 / 30,114 / ...) gives EDIT / DROP / DUAL, DUAL just under
  (the menu's third row: 70,98 for the top member, 100,147 for the third); in the DUAL window the
  classes are at x 181-200 from y 105 (preserver 105, thief 132 ...), and a human's kit menu then
  comes up (its first row 145,104). The Effects button is (121,171) in View Character, (242,185) on
  the inventory bar. Escape on Effects goes all the way back to the main menu.
- **A kit's THAC0 in Wake of the Ravager** (logs/2026-11-27-ravager-scholar.md): the sequel writes a
  member's THAC0 (+16h of its creature) only when the character is made and at a level up, never on
  equip, so a THAC0 change is seen by making a new member or by levelling one in a fight (set it one XP
  short with `ravlevel.py set`, then the fight route with Computer Control). `ravkits.py show` lists
  DSCLOG2's counters (`scholar_thac0s` among them). A kit's extra spell window counts when it closes, not
  while it is up. The creation screen's THAC0 line is drawn again at a roll (the die, 145,92) and at a
  click at (40,162), the second without the game working the THAC0 out again
  (logs/2026-11-27-ravager-dam-lines.md). **A kit or rule test in the sequel needs the dice log running**
  (`ravdice.py`): `ravload.sh` alone leaves DSCLOG2's rules words 0 (`ravkits.py count`'s first line).
  **The sequel's dice log writes only where a feature names the bytes** (`guest.writable`, `_writable`):
  a write anywhere else is dropped without a word, so a ported feature that writes memory (the tracker's
  XP bonus: logs/2026-11-27-ravager-xp-lines.md) must name its ranges. An XP edit by hand counts as an
  award (and gets the bonus): make it before the dice log attaches.
  **To see the sequel's item report**, free a party item's record with a test edit (its +0 word 0:
  logs/files/2026-11-27-ravager-item-watch-edit.py): two seconds on the dice log names the report in
  `obsidian-edition/crash-logs/` (git ignores it); an item of an ordinary type (an arrow, 6) freed says nothing.
  **The sequel's inventory and shop by clicks** (logs/2026-11-27-ravager-item-watch.md): its window is
  640x480, so a game y is the window's / 2.4 (not / 2): Ar'Anda's left hand 173,90, missile 65,50, right
  hand 65,91, portraits 30,21 / 30,71, backpack 196,27 / 45 / 63 / 81, DROP 206,135. In Notaku's shop SELL is
  292,164 (an item on the pointer first), TAKE IT 145,92, the list's first place 253,88, MORE 255,164; the
  list is drawn one change behind, so read `ravshop.py shop` before buying. A one-use scroll's spell icon
  out of a fight gives a casting pointer that found no valid target; a right-click ends it.
  **A defiler for a test** (logs/2026-11-27-ravager-defiler-scrolls.md): `ravjump.py 0x34 45 32` (the Pyramid,
  RGN034, among its five Defilers, creatures 15, 17, 21, 22 and 23, object 363 in the running game) with
  `RAV_DEFILER_CHANCE=100`. `ravjump.py`'s REGION is the region file's hex number: 0x22 (34 decimal) asks for
  RGN022.GFF, which the game hasn't, and it quits to DOS printing the name (DOSBox closes; stock does the same).
  For a defiler in a smaller fight, give one of Tyr's ambush's Draxans (creatures 25, 26, 29, 31 in the fight; 5,
  7, 8 are the street's, not in it) the Defiler's object (logs/files/...-defiler-crobj.py `25 369`) and start the
  dice log again (a running log keeps its answer for the fight). The pointer's mode (DS:1440h: 1 walk, 4, 2 the
  eye; 0 while a container is open, DS:05D6h its thing) tells which a right-click gave.
  The USE screen opens from the top-left icon (22,17); there the inventory is (75,171), View Character
  (170,188), the portraits (30,23 / 30,71 / 30,121 / 30,167) on the inventory screen.
- **DONE for a new fighter** (logs/2026-11-23-memory-pass-6.md): PICK A WEAPON SPECIALTY comes up
  over the screen (four rows of six icons, the Ravager kinds among them); a click on an icon (the
  gythka at 210,66) takes it ("SPECIALIZE IN GYTHKA" below, the dice log's gear lines), then PICK
  A PSIONIC POWER: its icons in a row at y 62 from x 124, the row closing up after each pick, so
  click 124,62 again for each of the picks; after the last, VIEW CHARACTER with the new member.
- **First spells and powers in Wake of the Ravager** (logs/2026-11-25-ravager-first-spells.md): DONE opens
  CHOOSE A SPELL for a new preserver once a spell (icons five a row from 124,74, 19 by 17 apart; LEVEL
  107,147; EXIT 205,147, then EXIT 112,92), then PICK A PSIONIC POWER (icons from 121,62, 19 apart; the
  discipline button 115,140; EXIT 202,140, then EXIT 112,92). `ravfirst.py M` reads what came of it.
- **Weapon specs at creation in Wake of the Ravager** (logs/2026-11-26-ravager-spec-pick.md): after the
  powers, a fighter, gladiator or ranger gets the weapon window (four rows of six, slots 34 apart: the
  long sword 75,32, club 109,32, the two-handed sword 211,100, lotulis 245,100, double spear 75,134;
  EXIT 228,176, then EXIT 112,92 for the defaults). The pointer on a slot names it under them. It needs
  the Loader or the dice log attached (DSCLOG2's rules word 0 before: no window). `ravspecs.py` reads the
  specs and the pick's counters; EDIT (right click on a "New" member's portrait, 170,117) asks only for
  picks still due. In CREATE CHARACTERS after a restart the party is empty: right click, ADD (the
  menu's second line), the roster's rows from 100,45, 11 apart, ADD 253,46.
- **A name**: click the name (40,128), press **Delete** 16 times (BackSpace does nothing; typing
  goes in front of the old name), type it, Return.
- **CHOOSE A SPELL at creation** (a preserver, after DONE): the icons are 6 a row, filled row by row
  (the Loader's `dsloader/spellgrid.py`), 19 apart from (113,71), rows 20 apart: the Nth spell from 0
  at x 113 + 19 x (N mod 6), y 71 + 20 x (N div 6). They are in spell-number order (Armor, Burning
  Hands, Charm Person, Chill Touch, Color Spray...; Shield and Shocking Grasp the 10th and 11th:
  Shocking Grasp alone first at (189,91)), and the list closes up after each pick. Pick one at a
  time and read `known.py M` after each: the number of picks goes by INT (a half-elf
  fighter/preserver 2/2: four at INT 16-17, two at INT 15), and a click past the last pick lands in
  the weapon window. LEVEL 1 turns LEVEL 2 for a 3rd-level preserver's 2nd-level picks.
- **The weapon window** (after CHOOSE A SPELL, at DONE; PICK A WEAPON SPECIALTY, or OF EXPERTISE for
  a ranger, Battle Mage, Crusader or Mind Warrior; at a level up too): icons 33 apart, **four rows
  of six since Wake of the Ravager's kinds** (logs/2026-11-23-ravager-weapons.md), the window taller
  and the rows higher: row four is y 134 (the double spear 75,134, the trikal 109,134), so row one
  about 35 (the long sword about 72,35). The title is under row four. Before 2026-11-23: three rows
  from (72,46), the cahulaks (245,78), the bow (105,112). A click closes it and the dice log gives the start weapon ("starts with a plain
  obsidian cahulaks ... in place of the bone long sword"). A Battle Dancer's has only the long
  sword (72,46) and the bow in use, a Spellarcher's the bow alone.
- **Psionic powers at creation** (logs/2026-11-11-psionic-picks.md): after the weapon window PICK A
  PSIONIC POWER opens: icons from (123,62), 17 apart, five to a row (the list closes up after each
  pick: clicking (123,62) again takes the next); the discipline button (117,140); the count beside
  it; EXIT (202,140), then EXIT at YOU HAVE MORE (140,91). The last pick closes it. Each member's
  known powers: `python3 powers.py`. **P-METAB's 14 powers** are powers 6-19 in order (Animal
  Affinity first): Cell Adjustment the 8th, second row third (157,79).
- **DROP, ADD and the roster**: on VIEW CHARACTER a right-click on a slot opens its menu just right
  of it, at the slot + (46,5) and + (46,14) (the second slot's, 120,52: NEW/EDIT 165,57, ADD/DROP
  165,66; the fourth's, 120,110: 166,117 and 166,125); DROP asks YES (the first row); the last
  member can't be dropped ("LAST ONE: CAN'T DROP", OKAY). ADD (112,66 from the first slot) lists
  the roster (rows y 45 + 11n, scroll with the arrow at 219,146; the game's five first, Garn,
  Aticus, Seneca, Deestan, Shandra, then the made ones, not always newest last: read the shot), a
  name, then ADD (252,46); EXIT (252,66). A dropped character's record stays in memory
  (`sheetinfo.py` still lists it).
- **The Loader's gear and the roster** (logs/2026-11-15-kit-rebalance-checks.md part 7,
  logs/2026-11-16-roster-gear.md): the roster keeps the character as the game wrote it at DONE, and
  DSCLOG holds that write (GEAR_HOLD) for the Loader's creation gear, so a character ADDed in a later
  session has it. To check: start `timeout 115 python3
  gearpoll.py > $WORK/gearpoll.log &` just before DONE; the dice log's "starts with ..." lines must
  come before `charsave_written=True` (the roster write, after the psionic powers). To see the
  roster's copy: restart (start.sh, title, CREATE CHARACTERS), ADD it, then list its items with
  `gd.party_items()` (live.py). A check with a rule off: only the switches the Options tab keeps
  (`game.RULE_SETTINGS`: `helm_ac`, `best_hit_die`, `half_giant_hands`, `kits`, `new_spells`) can be
  set off in `obsidian-edition/settings.json` before `start.sh`, which keeps the other keys; take
  it out again after. **The rest are always on since 2026-11-18** (`game.ALWAYS_ON`: weapon
  specialization, `held_hit`, `spell_to_hit`, shadows ...): the Loader drops their keys as it reads
  the file (logs/2026-11-18-fewer-switches.md), and since 2026-11-19 DSCLOG no longer reads their
  bits (logs/2026-11-19-free-dsclog-room.md): clearing one in `rules`/`rules_hi` (`setmem.py
  ruleshi=-N`) changes nothing. To see the game's own way, run origin's build from before
  2026-11-19 ([comparing two builds](#builds-the-loader-and-the-tests)).
- **The DUAL window** (dual-classing, logs/2026-11-09-group-4.md): the inventory screen (I), a
  right-click on a portrait (Cermak 20,104 in pens-fire-count4) opens EDIT NAME / DROP / DUAL
  (CANCEL in DUAL's place when it isn't offered; the menu opens at different heights: shoot it
  first, DUAL at 90,145 or 90,97); the classes greyed or white (zoom a shot: `convert -crop
  120x110+150+30 -scale 300%`); EXIT 213,145. Its scores, a kit's menu and the rule switched off in
  memory: [DUAL in memory](RESEARCH-MEMORY.md#creation-and-levels).
- **The DUAL sphere menu** (logs/2026-11-15-kit-rebalance-checks.md part 9): after CLERIC, DRUID or
  RANGER on the DUAL window, a menu whose title row is "SPHERE: AIR" (no click there), EARTH
  (140,92), FIRE (140,104), WATER (140,116), and a close button (210,116). **The game makes the
  close the air class and changes the member** (a real change: only on a test save or in memory);
  for a class the member's kit bars (a Brute's air cleric) DSCLOG makes it no change.
- **A party made on the creation screen into a fight**: Escape on VIEW CHARACTER goes back to the
  main menu (the made characters stay), and **S** there is START GAME; then topartyfight.sh's steps
  from the message boxes on (typed, not cut from it: its first clicks are for the title, and
  (160,120) on the main menu is near EXIT TO DOS). Four fresh 2nd-level characters lose the arena's
  first wave to Tab + Return: check a USE screen at the gate, and take a shot from `tofight.sh`
  instead (logs/2026-11-16-spellarcher-fine-bow.md).

## Inventory, looting, selling and shops

- **The sequel's class outfits** (logs/2026-11-27-ravager-class-outfits.md): `ravdress` dresses only with the dice log attached (`ravdice.py`; its `dress` pass), the copy's pictures plain until then. Only the leader is drawn outside a fight: keys 1-4 make each member the leader, to see each outfit. Thy'rokh (the thri-kreen) has none. `RAV_SKIP=class_outfits` is the control. The inventory's party column and the creation screen's small figure (DSCLOG2's SMALL_FIG) need no dice log: their pictures are keyed by figure and classes, made at the copy. On the creation screen it follows every class, race and portrait click; with no class it is the stock figure (a class-less key quit the game with "Math Err").
- **The party column's small figures** (logs/2026-11-27-small-party-figures.md): each is frame 0 of the member's walking picture in the Loader's SEGOBJEX (DSCLOG's `SMALL_FIGURE`; the member's picture in the header's `SMALL_PICS`, +1893), so with the Loader attached it is their map figure, outfit and gear; with it detached (0 there) the game's stock figure from start-up. To see a class change, close the inventory and open it again (Escape, I) after the Loader's pass (about 2 s).
- **Class portraits.** From the PENS save, press I and select each party face. Cermak wears his active Preserver outfit. Compare Gerakis, K’ratchek and Cilla with their retail half-giant, thri-kreen and elf inventory pictures. The DOS helper reads the portrait from the prepared RESOURCE.GFF, so this check also works with the host dice log detached. To compare human fittings, capture the central parchment after each party selection and again after returning to the first member. In a 320 × 240 DOSBox window, horizontal pixels are native and the 200 game rows stretch to 240. Use that vertical scale when aligning a capture with the Loader’s decoded picture.

- **An item's box on the inventory screen**: a right-click on the item opens it (lower for a lower
  backpack cell), a left-click on the box closes it. Escape closes the whole inventory, and
  right-clicks after that cycle the map's pointer (`pointer.py walk` puts the arrow back). Click
  with `click.py X Y right` at game pixels (the backpack's first column x 195, y 27, 45, 63, 81
  opened the four boxes; 250,33 closes one): an `xdotool click --window` never reaches the game,
  whose pointer DOSBox holds (logs/2026-11-25-obsidian-lotulis-bone-great-sword.md).
- **The inventory screen's places** (from hovering: the name shows in the bar at the bottom; the
  ones used): ammo (66,26), missile (66,48), arm (66,70), right hand (66,92); chest (173,70), left
  hand (173,92), legs (173,128); **the feet** (174,147) (logs/2026-11-09-silent-labels.md; a
  right-click there opens the boots' box); the backpack fills down its first column first:
  (195,26), (195,44), (195,62), (195,80)... (rows 18 apart; 48 and 70 are between cells), then
  (213,26)... Click an item to pick it up, click a place to put it; armour can't be put on in a
  fight ("CANNOT USE THIS ITEM"); a wrong place says "ILLEGAL PLACEMENT" and keeps it on the
  pointer. An item left on the pointer isn't in a shot (it was dropped by the next click on DROP,
  213,134). **To give an item to another member**: click it, click the other's portrait (22,160 for
  the fourth), click the place. The screen can draw the backpack one change behind: close the
  inventory and open it again (Escape, I) before believing a cell is empty.
- **Wake of the Ravager's weapon icons** (`sequelicons.py`) are put in the Loader's copy only when
  it finds the sequel (`$WORK/rav`, from `setup_ravager.sh`); without it the game shows the
  Loader's own drawings. Check which a play has before judging an icon
  (logs/2026-11-25-sequel-weapon-icons.md).
- **AC in the inventory**: the AC line is the game's own, worked out afresh from what is worn, but
  drawn one change behind: switch to another member's portrait and back (20,62 then 20,20) before
  reading it. It follows a gladiator level raised in memory (`sheetedit.py`); the THAC0 line
  doesn't. Gerakis's armour: chest (173,70), arm (66,70), legs (173,128).
- **View Character**: the inventory's first bottom icon (168,187); on it the icons are at y 171
  (view, inventory, cast, effects at x 52, 76, 100, 122), in play as on the creation screen, and
  the Effects page's MORE: CLICK HERE is a click on the panel (220,135) (the inventory's own Effects
  icon is 243,187; the portraits there at 65/112, 55/110). It shows each member's EXP and the
  next level's need with its class letter ("EXP:4487 (5000 Pr)"): a quick check of the XP tables
  (AD&D's, always). For inventory or DUAL pictures
  use `pens-after-arena`: in `fountain-user` the ambush starts on loading.
- **The leader**: the inventory screen's small face button left of each portrait (the first of the
  two; the lit one is the leader's): Cilla's at (7, 152), the others' 44 higher each (from the
  manual's "Leader" button).
- **Reading a scroll**: right-click it in the backpack to open its item box, which shows the price,
  "Scroll" and the spell's icon. The box opens beside the item's row (row 26: icon at 288,20; row
  44: 289,33; rows 62 and 70: 289,47; row 80: 290,65), so take a shot and read where the icon is.
  Then point at the icon (`click.py X Y none`), wait, and press slowly (`xdotool mousedown 1`, 0.15
  s, `mouseup 1`): click.py's quick click there was lost about half the time. The result is on the
  line under the paper doll and in the dice log ("X reads the scroll of Y: ..."). The dice log
  doesn't repeat a `Message:` line the same as the last one, so look for the "reads the scroll"
  line.
- **The item box's INFO** (logs/2026-11-18-spell-arrows-info.md): its one button, at the box's
  bottom right (a pack's first cell: about 291,57, or 289,54 for a box with a price line; the right
  hand's: 160,115; zoom the box to find it), toggles the box to the game's "USEABLE BY:" list (the
  party members the can-use routine, DSCLOG's `PROBE_CAN_USE` with it, allows; else NO ONE); a
  second click, or one outside the button, shuts the box. A click just after the box opens can be
  lost: point (`click.py X Y none`), wait a second, then click. **A Spellarcher for a test in
  memory**: the sheet's race half-elf (+18h 4), classes fighter and preserver (+21h 9, 11), the kit
  byte 1, **and the class mask (+12h) with the fighter's bit (20h)**: the game tests that mask
  before DSCLOG's kit checks, and a preserver's alone (80h) bars arrows. A spell arrows' stack put in
  a non-Spellarcher's pack goes to the Spellarcher as the inventory shuts (`return_strays`); with
  no Spellarcher, or no room in its pack, ones it has readied go back in its own pack. **SPLIT** (205,147): press it with
  nothing on the pointer, then click a stack: a stack comes onto the pointer
  (logs/2026-11-18-spell-arrows-info.md).
- **Items changed in memory** (an item turned into another, a held item rewritten, an item's icon,
  a figure's glow and outfit): `itemedit.py`, `setitem.py`, `sprites.worn` and the item records'
  fields, in [items in memory](RESEARCH-MEMORY.md#items-in-memory).
- **Looting a body** (the user): the **look pointer** on the body's picture; the plain eye (not the
  red one) shows when it is over it. A body's map position isn't where its picture is drawn when
  others lie on it: move the pointer over the picture, beside the party (a body far off opened
  nothing). A slow press opens its window (logs/2026-11-11-looting.md); `dsword.py 5E6` reads its
  map thing (9999 shut). A window of cells opens: a click on an item puts it on the pointer (the
  cells light yellow), a click on a party member's figure gives it to that member. **T** /
  **Shift+T** (`xdotool key shift+t`) with it open take everything / all but plain weapons; Escape
  shuts it. **Bodies under the party's figures can't be clicked** (a look click there opens the
  member's Effects screen): walk the party aside first. `bodyitems.py` lists what each dead body
  on the map holds (name, type, plus, power, value). `xdotool key --window W Caps_Lock` sets the
  BIOS's Caps Lock flag (0:0417h 40h) for a test (logs/2026-11-11-caps-lock-loot.md). **T shuts the
  window itself**: no Escape after it (with nothing open that brings EXIT: SAVE GAME?; CANCEL
  140,115) (logs/2026-11-18-audit-fixes-1.md).
- **Bulk loot to full packs** (logs/2026-11-20-open-prs-checks.md): from `fountain-user` after
  `fightout.sh`, the five guard bodies by the fountain (`bodyitems.py`'s screen places, a slow press
  with the eye at the place +2 in y) fill all four packs (12 cells each, `pickpocket.BACKPACK`):
  the third body ends with `No room in the backpacks for: ...`, the rest `The party's backpacks are
  full: nothing taken.` `carried.py NAME` shows each pack. A guard's purse-like thing (type 60,
  name number 9999) is named `item 9999` in the loot lines.
- **Selling with S** (logs/2026-11-11-selling.md): Kalzith's shop (his look box's first button Talk
  at 163,86; 1, then 1 "Show us what you have"); S on the shop sells the plain gear of the member on
  show (the game's 3931h:25Bh; a portrait click changes it). Kalzith moves: zoom a shot to find him.
  The game's SELL: an item on the pointer, SELL 265,63, TAKE IT 140,91. Backpack cells on the shop
  screen run down two columns (193,26 and 211,26, 18 apart).
- **The buyback with and without the Loader** (logs/2026-11-18-audit-fixes-1.md): an item on the
  pointer is DS:179Eh's thing 523 (`ring.Items(gd).things + 523 * 3`); a magic item sold with the
  Loader goes to Kalzith's pack (DSCLOG's queue at the header's +308/+310, its items at +1868,
  0FFFFh once the Loader has seen to it), bought back it comes onto the pointer (click a cell to put
  it down). **No Loader for a test**: kill the dice log's pid (`pgrep -f '^python3 -u -m
  dsloade[r] dicelog'`), wait over 5 s (DSCLOG's LOADER_FRESH), sell; start it again as start.sh
  does (`setsid nohup python3 -u -m dsloader dicelog >> $WORK/dice.txt` from `obsidian-edition/`).
  Money for a test: `gd.add_money(N)` through live.py (never saved).
- **The leader's CHA in a shop** (logs/2026-11-19-free-dsclog-room.md): the prices are drawn as
  the shop opens, so a leader changed on the shop screen (its face buttons, as the inventory's)
  doesn't change them: make the leader on the inventory screen (I, the face button, Escape) before
  `openshop.sh`. In `selling-junk-user` Gerakis (CHA 14) leads, prices as the game's; Cermak (CHA
  18, 7,108) 5% off. **Escape on Kalzith's shop goes back into his talk and says Farewell**; his
  talk after that differs and `openshop.sh` then fails (the eye left up): load the save again.
- **Shop and pocket tools**: `openshop.sh` (Kalzith's shop from `selling-junk-user`, finding him
  from memory), `pocket.sh X Y NAME` ([picking a pocket](#talking)), `carried.py NAME` (what someone
  carries, with name numbers).
- **A lock barred until a level** (logs/2026-11-11-lock-retry.md): Pehtucl's chest with a
  1st-level thief (`thief.py 0 1`) fails easily; a second use reads "failed this lock at this thief
  level", and `thief.py 0 2` lets it roll again. `chestuse.sh [y|n]` sets the eye with `pointer.py look`
  and presses the chest at (163,70), then its look box's USE; a non-thief's "Bash it open?" takes
  the right-clicks that put the walk arrow back, so give the answer (y or n): the script presses
  it, clicks the messages after it away and puts the arrow back (without one it leaves the
  question and the eye up, and says so). If the eye shows red over the
  chest, `pointer.py walk` then `look` again. The chest itself: [Pehtucl's
  chest](ROUTE.md#pehtucls-chest).
- **The pens' weapon rack** (logs/2026-11-11-semyon-rack.md): `rackcheck.py` shows it (object
  2599), what's in it and where any Thornwall is. In a new game answer Kurzak's greeting first: until then
  it finds no thing of the rack (logs/2026-11-25-ravager-magic-metal.md). A rack the party emptied has contents 9999 (no
  list). Where it is: [the slave pens](ROUTE.md#the-way-west-the-stalker-pen-and-the-grate).

## Fights

1. **Story fights: `sh fightout.sh`.** It sets every foe to 1 HP (not the arena's prisoners) and
   finishes the fight with Tab + Return on each party turn, clicking messages away and pressing E
   (END TURN) for a member with no Move left, so the game's scripts see every kill. It refuses to
   run with no fight on: run outside one, hp.py and its keys did harm (a prisoner at 1 HP, the
   party stuck in place). **A Tab + Return loop of your own stalls on a member with no Move left**
   (Tab keeps choosing, nothing attacks): use fightout.sh, which presses E for it. When the alarm
   sends waves, `fight_on` is 0 only a moment between them and fightout.sh stops "DONE" there: run
   it again. **In Wake of the Ravager** (logs/2026-11-25-ravager-blast-log.md) a Tab + Return
   loop must press Q and then E to end a member's turn (Q alone leaves END MOVE up), and
   `ravfight.py fight` doesn't reach foes inside a building (the walk to them stops at the door): `ravfight.py tabfight` is that loop and does.
   **`fountain-user`'s ambush needs Pehtucl's speech clicked away first** (2026-11-26): loaded, the
   speech box is up with `fight_on` 0 and fightout.sh says NO FIGHT ON; `msgbox.sh` only reports the
   box. Five clicks on it (`click.py 160 30 left`, 3 s apart) start the fight (`fight_on 1`).
   **The sequel's ravclick.py coordinates in the 640x480 window** (2026-11-27): the game's x is the screen's / 2,
   its y the screen's / 2.4 (USE's spell icons at y 58, the portraits at 47/98, 53/112). A killed creature
   leaves the combatants' table at once: a watcher of that table misses its last hit points.
2. **Never `killfoes.py` in a fight a script waits on.** Kills made in memory bypass the scripts'
   reactions to them (in the arena, none of the Announcer's lines about the kills). It is only for
   fights no story depends on, and the fight still needs its turn ended. To kill one foe in memory
   by name where the story doesn't matter: `aging.kill` (never save).
3. **The arena sends waves.** After one fight ends, messages, then another fight: run
   `fightout.sh` again until the wave messages stop (a YES/NO question ends them).
4. **Whose turn**: `state.py`'s `turn` (0-3 the party); never guess from sleeps. Act only on party
   turns; enemies act alone.
5. **Movement**: a member with no Move left can't reach anyone; a click then opens its END menu or
   does nothing ("Move : 0"). **Move running out doesn't pass the turn**: the walk stops and END
   <NAME>'S MOVE opens and waits. For a test that needs reach, raise its Move in memory first ([the
   turn's movement word](RESEARCH-MEMORY.md#fights-and-foes-in-memory)), and restore it after; never save
   the game while it's raised. The END menu shows what is left ("Move : 12").
   **Walking a member square by square** (logs/2026-11-18-squares-in-reach.md): `movestate.py`
   prints whose turn it is, its square, points and flags and the walk map round it with the
   Loader's marks; `squarewalk.py COL ROW [POINTS]` clicks a square's middle and says where the
   member stopped; `squaresweep.py POINTS [edge|out|all][here]` tries the marks' rim (or the free
   squares just outside, or all) a walk each; `squarecost.py` times a walk for the marks' cost.
   - **F10 takes the move back** (the game's own key, with no menu up: Escape closes the END
     menu first): the member stands where its turn began with its points. After the last step
     the game gives the points back but not the walk (bit 0 of the turn's flags stays off); the
     Loader's mend (`move_back`, dsloader/moveback.py) sets the bit within a pass or two when its
     dice log saw the last step (its line "F10: NAME's move taken back (can walk again)"), so a
     dice log restarted in the middle of a turn mends nothing that turn. `squarewalk.py` with
     POINTS puts the bit back itself.
   - **F10 after a spell** (logs/2026-11-20-f10-after-spell.md): a cast zeroes the whole flags
     word (37BD:01D5h), so the mend stays out. Most casts end the turn (F10 is then the next
     member's); Magical Stone keeps it till the third throw, and F10 then puts the caster back with
     its points and the flags still 0 (no walk, no Loader line). **A pin put on after the last step**
     (`addeffect.py N 34` there, then F10) got the walk back from 2.19.0's mend, one step before the
     game ended the turn (the game's own pin, 786CBh, only clears bit 0, already clear); since the
     fix the mend reads the member's effects at F10 and gives nothing with 34 or 51 (Stuck) on it:
     no line, flags as the last step left them. **Since DSCLOG's `F10_PIN`
     (logs/2026-11-20-f10-held-stays.md) the game's F10 doesn't move a member with 34 or 51 on it
     at all**: it stays on its square with its points (0 after the last step), f10watch shows no
     change; take the pin off (`addeffect.py del N 34`) and F10 is the game's again (and the mend
     gives the walk, its sequence kept through the pin). An `addeffect.py` pin with movement left
     leaves bit 0 set (the game's own pin would clear it); the site reads the effect table. Follow a
     turn with `f10watch.py MEMBER SECONDS` in the background: each change of the flags, points,
     square and the turn's start words, with its time.
   - **A real pin for an F10 test** (logs/2026-11-20-f10-real-pin.md; no memory edit to the pin):
     from `fountain-user` with the foes held and `spellsetup.py 0=9 2=9`, Lex's Web (wizard level 2,
     fourth icon 230,59) at the Templar (240,124) leaves a web east of the party; a member walked into
     it saves on the step into a web square (`saving throw vs Web (spell)`), and a failure stops the
     walk there, Stuck, the END menu up, the turn its own (with movement left, or with 0 after a last
     step into it: aim the walk to spend its points on that step, and try it: the path cost more than
     worked out). F10 then does nothing. A Stuck member's later turns open with the END menu, 0
     points and the turn's start words 0 and its own square. **Paralyzed with the turn kept**: Spell
     Turning on the target foe (`foeset.py 25 eff=44:48`, the Templar; held foes turn too), then the
     member's own Hold Person at it (Ester, priest level 2, 176,79): `Templar gives Paralyzed to
     Ester`, the Hold Person pointer stays up and the turn with it (flags 0); walk first for a case
     the game's own F10 would have moved. A Paralyzed member's turn otherwise never comes (Hold
     Person, and Rainbow Pattern's save at each turn's start: "X's turn" logged, gone in 150 ms).
   - **An attack ends the member's turn, unless it kills** (turnwatch.py: +181h back at 0, +1ABh
     1, the flags as they were, the turn still its own; a second swing of the same command can
     end it all the same: Jenna's did, Ester's didn't). For "walked out, killed, F10": a foe on
     the last step's next square at 1 HP (`foeset.py C hp=1`, autosave off), Tab + Return, F10.
   - **A walk the Move ran out on stays the member's**, and with the bit put back in memory the
     game goes on with it from wherever F10 put the member, so the next click's walk is mixed with
     it: forget it with the edit (FFh at 3972:0377h + thing x 1Ch, 0 at 3972:08AAh + thing x
     13h; the two tools do). In play the bit never comes back in a turn.
   - **A click on the square behind a figure is a click on the figure** (its END menu, or an
     attack on a foe that ends the turn): a walk test leaves out the two squares north of anyone.
   - **A walk can begin a second or two after the click**: wait for the member's place to change
     before waiting for it to stand still.
   - **The view** follows a member that walks out of it ([dragging it in a
     fight](#walking-the-view-and-doors)); the party's squares on the walk map are
     DS:0546h (x, y a member; 129, 99 for one with none, as the leader at the ambush's start,
     whose square others can then walk onto).
   - From `fountain-user`: a two-square doorway at squares (53-54, 78) and a one-square one at
     (45, 82-83), north-west of the fountain's corridor; nobody stands near them.
6. **Spells**: USE (24,17), the level page (LEVEL at 196,171), the icon, then the target; check
   the dice log for the spell's line before going on. The detail: [Casting spells for a
   test](#casting-spells-for-a-test).
7. **Shots**: a bow is used only against a foe not beside the archer: Tab + Return walks it up and
   strikes (with its melee weapon, or bare-handed with none), even from afar. To shoot: on its
   turn `pointer.py attack`, then a click on the foe's figure 10 pixels above its feet (`foepos.py`
   lists each living foe's place on the screen), the archer not next to that foe (one beside a foe
   [shot another two squares off](HISTORY.md#an-archers-turn-and-the-quiver)). Enter is a left
   click on the enemy (with Move left the member walks up and fights hand to hand). A shot test
   needs a clear line, a target in range, and a readied missile weapon with ammunition in the
   missile slot. [An archer's shots and its turn](#an-archers-shots).
8. **Playing the party's turns to a member's.** Which tool:

   | Tool | Does | Use it for | Watch out |
   |---|---|---|---|
   | `passuntil.sh N` | passes turns to member N's through each END menu (a click on the figure, the menu checked by its pixels, then E) | the safe default when the party should only wait | stops "member N off screen": drag the view first (`scroll.py`) |
   | `toturn.sh N` | Tab + Return for each member's turn, E when a turn stays up (no Move) | getting to N with the party fighting | E with no END menu opens the Effects screen (closing it leaves the view at the map's corner) |
   | `PARTY="A\|B\|C\|D" sh untilturn.sh NAME` | Tab + Return for the named members, messages clicked, foes waited out | the same, by name | keeps pressing Tab on a member with no Move left |
   | `passn.sh N` | passes N party turns by the END menu, dragging the view to each member | a party spread out | as passuntil.sh |
   | `fightout.sh` | finishes a story fight (foes at 1 HP, E for a member with no Move) | ending a fight the scripts watch | not for a fight whose foes must live (but `KEEP_HP=1`: their HP kept; `HEAL=1` heals the party each pass) |

   **A member held by a foe's Hold Person has no turn at all** (Lex in `fountain-user`, 2026-11-20:
   no "Lex's turn" for two rounds; not the END menu below): `passuntil.sh N` for that member passes
   turns until the party is defeated; check `effects.py` for 34 on it first, and paralyze the foes
   before passing turns. Rainbow Pattern (it can be aimed at bare floor) does the same: each
   creature in it saves at its turn's start, and a failure skips that turn at once (no save while
   walking in it).
   **The combat log panel covers the party's figures** when they stand low on the view: a click
   at `memberpos.py`'s place then lands on the panel and `passn.sh` presses E with no END menu (the
   Effects screen comes up; Escape closes it). `panel.sh hide` first (2026-11-20).
   By hand: `memberpos.py N` gives a member's figure on the screen; a click there opens its END
   menu, and E in that menu ends the turn (E with no menu opens the Effects screen). A Stuck or
   Paralyzed member's turn opens with its END menu up: E ends it, Escape closes it to act. So does
   a member with no Move left at its turn's start (seen after memory edits that moved foes):
   `untilturn.sh` then presses Tab for ever; click the figure and E, or use `passuntil.sh`
   (logs/2026-11-23-ravager-weapons.md). A turn
   passed can come straight back (the round's last but one, then first in the next): check the round
   order in the dice log. `stepfight.sh` from the arena gate clicks south until the fight is on. The
   incidents behind these notes are in [HISTORY.md](HISTORY.md).
9. **"target AC" in the dice log** is the AC the game uses for an attack: check it against
   `gd.counted_ac` (`acs.py`) whenever the foes seem to hit too often. A test fight that
   goes badly: `healparty.py` puts the party's hit points back in memory (never save after).
10. **R, F10 and Alt in Wake of the Ravager** (logs/2026-11-25-ravager-fight-keys.md): after a
   member's last step the sequel opens its own **END <name>'s MOVE** menu (GUARD, WAIT, END TURN)
   and F10 does nothing while it is up: press Escape first (the menu is a screen up, so it's safe),
   then F10. `ravkeys.py` shows the squares, F10's counts (moves taken back, refused), the points,
   the flags (bit 0 clear: no walk) and the turn's start; `ravkeys.py effect OWNER 66` (Cannot
   Move) or `69` (Paralyzed) holds a member for the pin's test and `del` takes it off (never save
   after). The crosses on Tyr's grey street are dark (no light for stone). Alt's rings come only out
   of a fight; in one RING_TAB stays empty. Put the four on Computer Control (the small icons beside
   USE) to end the ambush quickly: they win it in a few minutes with HP 250.

### Foes in a test fight

- **One foe's AC or attacks out of several** (logs/2026-11-18-champions-gear.md): name the foes
  apart in memory (the creature record's name, `game.CREATURE_NAME`, 16 bytes: the champions are
  all "Champion"; `foeset.py C name=S` writes it, logs/2026-11-23-ravager-weapons.md: a tripped
  foe's lost turn seen that way), put the others at 1 HP and the one wanted at 200 (`foeset.py C hp=N`, by the
  combatant number `foeset.py` lists), then `KEEP_HP=1 HEAL=1 sh fightout.sh` (the foes' HP kept,
  the party healed each pass): the party's Tab + Return kill the rest and then strike the one, each
  line its "target AC". Never save after.
- **One foe's attacks on the party** (logs/2026-11-18-champion-chill-arrows.md): name the foes apart
  as above (a loop over creatures 6-11 writing `game.CREATURE_NAME` through `live.py`'s `g.write`),
  Paralyze every other foe (`foeset.py C eff=34`), the one wanted at 200 HP, then `passn.sh 1` and
  `healparty.py` a pass at a time until the dice log has its "NAME attacks" lines: the elf champion
  shot at Cermak on the third pass, 2 shots. In the champions' bout the elf is combatant 45
  (creature 10, a level 7 fighter). **The dice log's HP lines can lag a hit** when two hits land
  close together (a weapon's spell's damage put on the next arrow's line): add up the "hits for"
  and spell damage lines, not the "now N/M HP" ones.
- **Seeing foes attack, without killing them** (logs/2026-11-05-champions.md): not `fightout.sh` (it
  puts every foe at 1 HP); pass the party's turns instead (rule 8), stopping once the dice log has N
  more "attacks NAME" lines (`passmiss.sh` does it for a miss, then drags the view and takes a
  shot). Between waves click the messages and walk about in the arena (staying brings more fights).
  It can lose the whole party ("YOUR PARTY HAS BEEN DEFEATED"; a level-1 party loses to the
  champions): have a save to go back to.
- **The ambush defeats the party when turns are only passed** (from `fountain-user`: a Templar's
  Hold Person, the archers): paralyze every foe first (`foeset.py C eff=34` on each, 17 to 47
  there, more coming as the guards are sent), free one with `addeffect.py del C 34` to watch its
  turns. **Archers crossing out the caster's icons every turn** (hit before its turn): the same,
  Paralyzed on each foe that shoots; then the turns come clean. Paralyzed foes also fail every save
  (handy for a failed save on demand). From `fountain-user` with every foe held, `passuntil.sh 3`
  gives Seneca's turn, and Tab + Return backstabs the Templar (41 HP) about half the time.
- **A memory-edit hold lasts only until a real one reaches the foe** (logs/2026-11-20-paralyzed-ends-oddity.md): an effect put on a creature that has it already takes the
  old record's place, with the new spell's time. Rainbow Pattern's area (no save line: a held foe fails
  without a roll) or a Hold Person on a `foeset.py`-held foe gives it a timer, and it acts again when
  that runs out (the dice log: `..., in place of the one it had`, later `Paralyzed ends on`). Keep holds
  and areas off foes that must stay held, or run `foeset.py C eff=34` again after. **With the whole
  party Paralyzed and the foes held, the game plays the rounds through in a blink**
  (logs/2026-11-20-round-one-oddity.md): no jump, but one round after another, 60 s each on the
  clock, every turn skipped, a tenth of a second for six rounds, until a hold ends; the dice log
  says `Rounds 4-5 go by at once: no one in the fight can act`. A watcher sampling every 50 ms
  sees only the clock leap. **Getting the whole party held for real**: Lex's Rainbow Pattern
  (`spellsetup.py 0=9 2=9 50`, wizard level 4, the only icon 176,59) at the floor among the party
  (158,148), a second one the next round if he is still free, then `passn.sh 1` a pass at a time
  while a count of the party's 34 records (a few lines over `live.py`) is under 4: each member saves
  at its turn's start; each of three loads had all four held within four rounds (the pattern lasts
  2d3 rounds: once it is gone, load again).
  **Untimed holds on both sides (`addeffect.py N 34` on the party, `foeset.py C eff=34` on the
  foes) never end by themselves**: the blink then runs at about 190 rounds a second until a hold is
  taken off by hand, the dice log's ring overruns ("N rolls came too fast to record"), and the
  game's turn (`state.py`'s `turn`, `gd.whose_turn`) stays the same through it, so nothing waiting
  for the turn to change fires (logs/2026-11-20-open-prs-checks.md). For a short burst take one
  member's hold off within a second of passing the last free turn. Since #140 the helper keeps the
  fight and round it is in: `symread.py initiative_fight initiative_round` (the first word of each).
- **Held foes are hit automatically, for normal damage** (the rule `held_hit`,
  logs/2026-11-10-held-damage.md: the dice log's `Paralyzed: hit automatically` under the attack).
  So a to-hit test needs a free target (the rule is always on since 2026-11-18, and DSCLOG has had
  no off path for it since 2026-11-19: no memory edit turns it off). **A Paralyzed target gets no save line from Hold Person** (it fails every
  save; the game logs only "gives Paralyzed"): free it first (`addeffect.py del C 34`).
- Seneca is a **Poisoner**: each of her weapons' first melee hit in a fight also poisons (10, no save
  for a held target: the log's `is poisoned by the hit` line), landing about 0.5 s later, after her
  next swing's line; a weapon's later hits that fight don't. Her Hayneedle is in the left hand,
  Shadowseeker in the right (logs/2026-11-14-quiver-turn.md part 6). To check a weapon's own
  damage, free the target (`addeffect.py del C 34`) or use a member who isn't a Poisoner, and read
  the "hits X for N" line.
- **Seneca's backstab round on demand** (logs/2026-11-19-backstab-str-line.md): from
  `fountain-user` with every foe held, `passuntil.sh 3`, the Templar freed (`addeffect.py del 25 34`),
  Tab + Return: she backstabs only when the dice log has both `hides in shadows ... -> hidden` and
  `moves silently ... -> unheard` (about half the loads; `heard` or `seen` gives plain attacks), so
  loop the load until the dice log has `BACKSTAB`. Her round is the Hayneedle (left hand) first,
  then one or two Shadowseeker swings, **all in one call of the attack routine**: a later swing's
  frame shows what the first left behind.
- **An attack's frame** (the same log): a copy of `rolog.py` (in the scratch folder) printing
  `e.parent_local(-N)` under each dice-log line with ` attacks ` in it gives the attack routine's
  locals at the roll: [BP-20h] the THAC0 before [BP-8] (the weapon's and specialization's), [BP-1Ah]
  from behind, [BP-24h] the backstab, [BP-22h] the attack's number in the round. The way to tell a
  wrong THAC0 from a log that only names a part wrong.
- **An ordinary attack from behind on demand** (the same log; a memory edit, never save): the
  game's from behind is the target's facing byte (segment DS - 4356h + 37BDh, **+5Bh + creature**,
  the creature's number, not the combatant's; 255 none yet, set by the first attack on it) equal to
  the attacker's direction to it (DS:494Ch after the attack, also the attacker's creature +38h).
  Let the member attack the target once, read DS:494Ch, write that into the target's facing byte
  before the member's next turn (standing where it was), and its next round is from behind.
- **Hidden members** (logs/2026-11-05-fight-test.md): Cilla, thief level raised to 12 in memory,
  hides at 95. Hidden, Tab + Return walks the thief up and backstabs; it is drawn solid from the
  blow on. The see-through drawing: [see-through figures](RESEARCH-PICTURES.md#see-through-figures).
- Foes and effects written in memory (`foeset.py`, `addeffect.py`, `effects.py`, `kinds.py`, a
  foe's saves, level and class, Psionic Blast without a blaster, held targets on any roll):
  [fights and foes in memory](RESEARCH-MEMORY.md#fights-and-foes-in-memory).

### An archer's shots

- **A Computer Control archer in Wake of the Ravager shoots only when the bow outclasses its melee**
  (logs/2026-11-26-ravager-poison-arrows.md): with a short sword in hand, or with it put in the pack in
  memory (its readied list is the fight's start's), it closes in and strikes; with its bow +15 (`ravitems.py N
  --bow15`, a test edit, never saved) it shoots every turn. `--fine` names its bows the Fine Bow.
- **An archer's shots and its turn** (logs/2026-11-14-quiver-turn.md): `shotinfo.py [MEMBER]` lists
  the foes on the screen with their places (click about 10 pixels above the feet in attack mode);
  `turnwatch.py MEMBER SECONDS`, started in the background just before the click, prints each
  change of whose turn it is and the member's turn bytes. **An attack command spends the turn
  unless it kills its target**: against one still standing the turn passes after the shots
  whatever is left; a kill with attacks left keeps it (walk, ready, strike again). For a kill on
  demand, `foeset.py C hp=1`. **Arrows set in memory must be set before the fight starts**
  ([arrows in memory](RESEARCH-MEMORY.md#items-in-memory)). With no arrows at all, a click on a far foe
  walks the member up and strikes with its melee weapon instead of shooting.
- **Readying arrows in a fight** (logs/2026-11-14-quiver-turn.md): on the member's turn, I, then
  the quiver (66,26) and a backpack cell (195,26) by clicks; another member's arrows: its portrait
  (20,63 the second), its quiver, the archer's portrait (20,104 the third), the archer's quiver
  (a same-kind stack merges). Escape, then `pointer.py attack` again: **closing the inventory leaves
  the pointer in walk mode** (DS:11B8h 1), and a click then walks. **A stack made in memory
  (`npcitems.add_to`) never shoots**: test readying with the game's own items. After a volley at a
  target still standing, a second shot at it that turn does nothing even with arrows readied (not
  yet understood).
- **An archer's test fight in one step**: `sh tofight.sh N` loads `fountain-user`, gives Ester N
  arrows (`setarrows.py MEMBER N`, before the ambush starts), starts the fight, holds every foe and
  passes to Ester's turn; the Templar is at screen (240,144). `ammodump.py` prints the archers' item
  records. **The floating arrow count** (the quiver's) shows for about a second in `shot.sh` grabs
  half a second apart (crop round the figure and montage them).
- **The large dice in the item box**: I on the fight's first turn opens the member whose turn it
  is; a portrait (20,104 the third) shows another; a right-click on the right hand (66,92) opens its
  item box (crop `-crop 110x80+70+60`, scaled 200%). The inventory's weapon block (Ester's bow and
  two long swords, its worst case) ends at y 162 and the panel's stone at about 176: no room for
  more lines. **No weapon name is wider than "+1 Shadowseeker"** (82 pixels, the panel's whole 82;
  "+3 Dag's Dagger" the same; measured in the game's font, `art.GameArt(GAME).font`).
- A weapon or a rule tried in a fight by a memory edit (a weapon put on a member, a named weapon, a
  shot with a weapon put in memory with `setitem.py`, melee reach, grand mastery, a rule by size):
  [items in memory](RESEARCH-MEMORY.md#items-in-memory) and [fights and foes in
  memory](RESEARCH-MEMORY.md#fights-and-foes-in-memory).

### The chance to hit against the swing

- **The chance to hit against the swing** (logs/2026-11-17-hit-chance.md): from `fountain-user`
  (nobody held, so the d20 counts), on a party turn `sh tabhit.sh` presses Tab, prints the dice
  log's `Chosen with Tab` line (the Loader's prediction), presses Return and prints the attack's
  lines (`needs N+`, THAC0 and the target's AC); `tabhit.sh 1 nohit` only chooses. `python3
  hitcheck.py [ATTACKER]` prints what a number is made of for every enemy (the squares between,
  the target's facing, the AC from the front and from behind, THAC0 by weapon); it is not the
  session's Loader, so it has no dance, Wild Fighting or AC gap (Ester read 1 off there while the
  Loader agreed with the game). The fountain's party: Lex 0 (short sword, bow), Jenna 1 (two long
  swords, bow; hides as a Stalker), Ester 2 (two bone long swords, bow; a Battle Dancer), Seneca 3
  (Shadowseeker +1, Hayneedle +1, sling; hides). The Templar there wears a Ring of Protection +1
  (AC 4, 5 from behind) and bone brigandine; the Guards are AC 10.
- **What the fountain's fight showed of the game's attack**: the weapons swing in the order of the
  creature's item list (the left hand's often first: Seneca's Hayneedle, Jenna's obsidian sword),
  and that first one is the backstab; a hidden thief's second weapon was "from behind" by the
  first's flags only (the AC from behind, THAC0 2 worse than a plain swing) until #116's
  `REAR_FRESH`, which judges each swing on its own; a target's facing (a byte a creature at +5Bh of the round's segment, FFh for none) is the
  way to its round's first attacker, 0 north and on clockwise.
- **A shot on a turn where Tab was pressed**: Tab scrolls the view to the chosen enemy by DSCLOG's
  pan, which `state.py`'s camera doesn't show, so a click worked out from the camera misses. Take
  a grab (`shot.sh`, the panel hidden with `panel.sh hide`: it covers the bottom right) and click
  the figure about 8 pixels above its ring, with `pointer.py attack X Y` first (X, Y bare floor).
  **Move the pointer with `xdotool mousemove`, never with a click on the floor**: with the walk
  arrow a click walks the member and spends its Move.

### The chance to hit under the pointer

- **The label against the swing** (logs/2026-11-18-hit-chance-hover.md): from `fountain-user` on a
  party turn, `sh hoverhit.sh C [attack]` puts the pointer on enemy combatant C's figure (the walk
  arrow, or the attack pointer), prints the label the Loader floats over it (`hoverlabel.py`,
  which reads the text back from DSCLOG's slot by its ink mask), clicks and prints the attack's
  lines. `hoverlabel.py X Y` or `foe C` only moves the pointer and reads; `watch SECONDS` prints
  the slots whenever they change (a label going, "Miss" taking its place, flicker), started in the
  background just before a click. `hovercost.py SECONDS` counts the map's loop passes and the
  frames shown, `hovercost.py loader` times the Loader's look.
- **Where to point**: `foepos.py`'s place (10 pixels above the feet) is the front figure's where
  two overlap (the game's finder takes the first picture with a pixel there, from the front): a
  back one's head is 22 to 25 pixels above its feet. Between a half-giant's legs there is nothing.
  The thing the game has under the pointer is DS:0BCBh (`hoverlabel.py` prints it).
- **Never bring the pointer to the screen's edge** (x 318 scrolled the view 480 units in one
  probe, and every place worked out from the camera was then wrong): drag the view back with
  `scroll.py`, the pointer in the middle first.
- **After restarting the dice log in a fight** its Loader has not seen the round's dance, Wild
  Fighting or the AC gaps: a Battle Dancer's number is 1 off until her next dance. Compare on
  another member, or wait a round.
- **A click that walks a member out of Move** opens END <NAME>'S MOVE (no label then: a menu is
  up); Escape closes it and a click on a foe next to the member still attacks.
- `panel.sh hide` can print "panel hidden" with the panel up and empty: look at a shot, and press L
  by hand (`xdotool key --window W l`).

## Casting spells for a test

**A spell's picture in one minute** (logs/2026-11-19-final-audit-memory.md): `fountain-user`,
`dismiss.sh` (the ambush starts, Lex's turn), then on Ester's turn U, her priest icon at (194,59)
(Curse: the aiming ring comes up) and a click on the Templar standing on the view's right
(`foepos.py`: screen 224-240,134; click 6 pixels above: 10 above said "no creature there" for
Magical Stone and Hold Person, 2026-11-19, while 6 above hit). Lex's first wizard icon (176,59) is
Shocking Grasp, a touch spell: "too far away" from there.

From `fountain-user` clicked into Pehtucl's ambush (logs/2026-11-08-manual-spells.md):
`spellsetup.py 0=9 2=9 hp=200` teaches the spells, fills every slot and sets each of the member's
casting classes (any place) to level 9 (Lex, #0, is the preserver there, Ester, #2, the priest), and
prints the pages the LEVEL button will offer (`0 Wizard: LEVEL pages [1, 3]`); `hp.py 150` keeps the
foes up. Teach `spellsetup.py` the spell number, not the SPIN chunk (the spell + 1); spells it
teaches outside the caster's spheres it names ("cast at level 0"). Then:

- **The basics**: open the USE button (24,17), page to the spell (LEVEL at 196,171), click its icon,
  then the target. A plain click on the icon closes the screen and gives an aiming pointer with the
  spell's range drawn as a ring of beads; a click on a figure inside casts. Out of a fight (U, the
  caster's portrait, e.g. Cermak 66,108) the target is a portrait on the same screen: the icon
  (177,59 the first), then the target's portrait (Gerakis 66,62), and the dice log says it ("Cermak
  gives Enlarged to Gerakis"); no name floats, the screen covers the map. Check the dice log for
  the spell's line before going on. If none appears, look at the screen: usually a menu left open,
  the wrong spell page, or no Move or slots left. Try Tab + Return at the targeting step before
  clicking a figure. In a fight U opens the USE screen for the one whose turn it is.
- **The USE screen remembers the spell level page** each caster was last on: the LEVEL button is
  at **(196,171)** (not y 187) and steps 1, 2, ... 5, 1; shoot the page before clicking an icon.
  The arc at (266,171) is RETURN TO GAME. Icons are about 18 apart, five a row: x 176, 194, 212,
  230, 248; y 59, 77, 97; in spell-number order of the spells known at that level (`gd.spell_level`).
  Hover an icon for its name in the bar at the bottom (y 182-194).
  In Wake of the Ravager (logs/2026-11-26-ravager-kit-casting.md) the same five a row at x 175, 197, 220,
  242, 262 and y 60, 79, 98 (game pixels); a quick hover sweep names only the first three of a row (the
  rest show "N LEVEL N SPELLS TO CAST"): a right-click on an icon shows its description with the name, a
  left-click closes it. A spell for a party member is picked up and dropped on the member's **portrait** in
  the USE screen (`ravfight.py cast ... OBJECT` with a member leaves it on the pointer). To reach a member's
  next turn in the Tyr ambush let the others attack (`ravfight.py attack`): ending every turn with Q lost it.
- **The LEVEL button skips levels with nothing known** (or no class slot, or past the caster level's
  cap); the USE screen opens on the kind with slots (PSIONIC when a member has no wizard or priest
  slots), the kind button (CLERIC/MAGE) at 150,171: Lex at preserver 10 with only 3rd-level spells
  known went 1 to 3; at preserver 4 it stayed on 1 (no 3rd-level spells at that level: the least for
  Flame Arrow is 5). spellsetup.py prints the pages and warns when a human's second class counts 0
  ([the game's rule for the pages](RESEARCH-MEMORY.md#spells-and-powers-in-memory)). A stuck button means
  a caster level of 0 or 1: check what else was written to the sheet ([the one time it
  stuck](HISTORY.md#the-level-button-that-stuck)). **The first click after U opens the screen was
  lost twice**: shoot the page after each LEVEL click.
- **Aimed spells** close the screen and give the aiming pointer (a ring of beads, or a box for an
  area); a click on a foe's figure casts. Harmful aimed spells are refused on the party ("can't
  cast X there: not a creature that spell can be cast on"), and "no creature there" means the
  click missed the figure: click lower, on the body (zoom a shot). A cast that logs nothing but
  takes a slot was a click beside the figure: aim from a zoomed shot. **Touch spells** (record
  +0Ch 3 or 5: Free Action, Ironskin, Blood Flow, Cure Light Wounds, Remove Paralysis...) keep
  the screen up and wait for a **portrait** (66,62 / 112,62 / 66,108 / 112,108): their icon
  "does nothing" until one is clicked, and through a portrait even Blood Flow lands on the party.
  Self spells (Minor Spell Turning) cast at the icon's click.
- **Touch spells: adjacent only** ("too far away" from two squares, diagonally too): click a floor
  square beside the target with the walk arrow on the caster's turn, then cast in the same turn (it
  worked with Move left) or the next. Moving a combatant in memory (DS:669Dh + 32n) moves neither
  its figure nor what a click finds.
- **Crossed-out icons**: a caster hit just before its turn ("YOU WERE HIT" in the bar) has every
  icon crossed for that turn; plain again the next round. Clicks on them do nothing, and RETURN TO
  GAME then a map click walks the caster instead. A caster hit before its turn can also fail to
  cast with its icons plain: try again the next round. Archers doing it turn after turn:
  [paralyze them](#foes-in-a-test-fight).
- **Cancelling an aim**: a right-click while aiming cancels, and passes the turn. **Escape
  while aiming** cancels the aim but opens EXIT GAME? (CANCEL 125,116), and that CANCEL leaves the
  aim up (the next map click casts at it). Escape on the USE screen is safer. Hold Person's pointer
  stays up for its next target after a cast.
- **A spell outside the caster's spheres is cast at level 0** (logs/2026-11-08-touch-level-and-hd.md):
  the USE screen lets it be cast, but its time and damage count only classes sharing a sphere with
  it ("caster level 0", taken as 1): set a class of that sphere in memory. In `pens-after-arena`
  Cilla is an earth druid (Ironskin, Free Action, Quicksand) and K'ratchek a fire druid (his priest
  levels move with the sky: K'ratchek counts as a Wasteland Seer). Out of a fight, U then Cilla
  (108,108), the CLERIC/MAGE button (150,171) switches the spell kind; an aimed summon there did
  nothing (red no-sign). In a fight a summon keeps no effect timer (effects.py shows none) and no
  "lasts" line. The detail: [spells and powers in memory](RESEARCH-MEMORY.md#spells-and-powers-in-memory).
- **Range**: Cloudkill at about 230 map units said "too far away"; at 80 it cast. Rainbow Pattern
  and Cloudkill are areas that stay: Rainbow Pattern (2d3 rounds) made Lex, Jenna and Seneca save
  each turn and paralysed some, so aim them away from the party; Cloudkill near the party: raise
  the party's levels in memory first (6 and up only take damage). Flaming Sphere cast at a foe two
  squares off struck the caster; farther off it took a slot and logged nothing.
- **Without `spellsetup.py`** (logs/2026-11-20-f10-after-spell.md): Ester's level-1 page is Bless
  (176,59), Curse (194), Cure Light Wounds (212), Cause Light Wounds (230), Entangle (248);
  Invisibility to Undead (176,79), Protection from Evil (194), Remove Fear (212), Cause Fear (230).
  **Entangle's aiming box is as wide as half the view** at the ambush's start and took the party in
  wherever it was put (2026-11-21): cancel with a right-click (the turn stays the caster's). Bless
  aimed at a member (Jenna, 170,140) blesses those near ("Ester gives Blessed to Jenna, Ester").
  Lex's: Shocking Grasp (176,59), Erdlu Claw (194), Reflected Image (212, a self spell: cast at the
  icon's click), Friends (230). Hover an icon and shoot to read its name; the first hover after U
  can show nothing.
- **Ester's pages in `fountain-user`** (after `spellsetup.py 2=9`; logs/2026-11-19-final-audit-fixes.md):
  level 1's second row, second icon (194,79) is Magical Stone; LEVEL (196,171) to level 2, whose
  second row's first icon (176,79) is Hold Person (a spell save on a free target).
- **Haste on the whole party** (logs/2026-11-20-open-prs-checks.md): `spellsetup.py 0=9 29`, on
  Lex's turn U, LEVEL to page 3, the icon (176,59), a click on a member: one cast hastes all four,
  each with the Loader's system shock roll and a year. Cast again the next turn, the dice log (since
  #141) says `Lex gives Hasted to ..., in place of the ones they had`, with no ageing.
- **Several casts a slot**: Magical Stone gives three throws a casting (the stone pointer comes
  back; the turn ends after the third). With the manual's spells
  (logs/2026-11-09-turn-undead-meteors.md), Minute Meteors gives five casts a slot (the pointer
  comes back after each, as Magical Stone's), each with its attack line (`+2 Minute Meteors`), and
  Flame Arrow one cast for every five levels (2 at preserver 10, 3 at 15, 1 at 9), each 5d6 with no
  attack roll. Click the target once per cast, 4 s apart.
- **Color Spray** (preserver 1, its icon first on Lex's page in `fountain-user`) can catch a
  member beside the figure clicked. **Hold Undead** (preserver 3) aims with the spell's icon as
  the pointer, takes a second click for another target, and logs "lasts N rounds" for each
  landing even on an immune target (then nothing more: no save, no effect). For a level-1 test
  spell: Ester's Magical Stone, `spellsetup.py 2=9`, the priest page's second row, second icon. An
  Arena Guard off the right edge was in reach.
- **Saves in the dice log**: a "cannot save" is the save's -100 (a natural 20 is shown first and
  saves); a natural 1 is shown before it too. Since `save_signed` (always applied, in no switch) a
  "cannot save" fails ([it used to save](HISTORY.md#cannot-save-used-to-save)). Look at the effect
  or the HP, not only the save line.
- **Spells rolling to hit** (logs/2026-11-08-spell-to-hit.md): each missile
  or hostile touch spell has a line `X's SPELL at Y: [touch ]attack d20 = ...` after its damage
  roll; each of Magical Stone's three throws rolls. Hits on demand and a weapon's spell on a hit:
  [spells and powers in memory](RESEARCH-MEMORY.md#spells-and-powers-in-memory).
- **Turn Undead** (logs/2026-11-08-turn-undead.md): U (in a fight it opens the USE screen for the
  one whose turn it is; the click at 24,17 opened the inventory), the TURN UNDEAD button at
  (158,146) with a slow press (out of a fight the thief's purse is beside it, at 176), then the
  aiming box: a click on the undead's figure. Each use ends the turn; out of a fight it starts one.
  The turning's box takes every undead it reaches: four Arena Guards stood together off the right
  edge of `fountain-user`'s view; `scroll.py -150 0` in the fight brought them on, the aim then
  showed a ring of beads (the range), and a click inside it took all four. A turned undead walks
  off and doesn't attack. Kalzith's pen (`route.py 1592 584`, then `route.py 1560 880`) puts the
  party beside him for a turning, and the aiming box reaches him there (the guards west of
  Kurzak's stop are behind a wall: "no line of sight"). A cleric and undead made in memory
  (`turnsetup.py`): [Turn Undead in memory](RESEARCH-MEMORY.md#spells-and-powers-in-memory).
- **A power out of a fight** (logs/2026-11-15-kit-rebalance-checks.md): U, the user's portrait,
  the kind button (150,171) CLERIC/MAGE -> PSIONIC (the P-METAB powers then: Animal Affinity 176,59,
  Energy Containment 194, Life Draining 212, Cell Adjustment 230), the icon, the target's portrait.
  A failed power check costs 2 PSP and logs "psionic power check fails"; try again. In a fight U on
  the member's turn opens the PSIONIC page; icons in power order; Adrenalin Control and Cell
  Adjustment then take a portrait.
- **Spell arrows** (a Spellarcher): the USE screen on it shows, under its spells, a button for each
  touch spell it knows (Chill light blue, Shocking blue: 157,147 and 176,147 with those two; no
  Burning Hands button); a slow press makes one arrow ("makes one of the shocking arrows in the
  pack (1 of 24 now)") and **closes the screen** (an Escape after it opens EXIT: SAVE GAME?). With
  wooden arrows in the quiver the new stack goes to the pack: swap them in the inventory (quiver
  66,26, a backpack cell). **In the sequel** the same buttons and places ([spell arrows made in
  the sequel](RESEARCH-RAVAGER-RECORDS.md): the party to ADD again at every start, the way out to a fight, the quiver).
- **A spell's description box**: U, a member's portrait (Cermak 66,108), then right-click a spell's
  icon (from 177,59, about 14 apart); in a fight the same on the USE screen (Fire Shield's and Cat's
  Grace's, logs/img/2026-11-09-group-3-*.png); a known bit or `spellsetup.py 0=10 44` first. Seven
  lines fill the box: an eighth spills over its edge, so check a lengthened text in the game (the
  box's limits are in [new
  spells](../obsidian-edition/DEVELOPMENT-CONTENT.md#new-spells-wizard-and-6th-level-priest)). Doc
  panels like `new-spells.png` are crops of `shot.sh`'s 320x200 picture scaled 2.09 (304x188 each).

### Rests for a test

- `pens-fire-count4`, `ringrest.sh`; each rest test from a fresh load (two rests bring Kurzak's
  call, and his patience runs out). `setmem.py` sets HP (negative too, with status 3 for Out Cold),
  PSP, a power known (`power=1:13`, K'ratchek's Cell Adjustment) and DSCLOG's rules; K'ratchek (a
  druid there) knows Neutralize Poison and has a 4th-level slot. The rest's dice-log lines: `At
  rest: ... casts ...`, `X rests 8 hours: +3, +6 (CON 22) = +9, now 19/54 HP`; CON 20+
  regeneration's +12 for the 8 hours then follows as an HP line. Where the ring is and how the call
  comes: [resting in the pens](ROUTE.md#resting-and-kurzaks-call). An effect given in memory before
  a rest (`addeffect.py`, `restfixmem.py`): [fights and foes in
  memory](RESEARCH-MEMORY.md#fights-and-foes-in-memory).

**A power aimed at a party member, in Wake of the Ravager** (logs/2026-11-25-ravager-blast-log.md):
the game refuses a member as a power's target; make the target's side byte (creature +15h) 7, a
Draxan's, for the click, and both members' if two stand on the spot; put it back after. A failed
power check costs 5 PSP and leaves no dice log line. `ravkits.py power MEMBER POWER` gives a member
a power for a test (PSP 200), `ravkits.py blast` reads the blast's counters.

**Aiming a spell in Wake of the Ravager's fight** (logs/2026-11-27-ravager-shinobi-spells.md): with the
spell pointer up, a party member under it turns yellow, and a click there says INVALID TARGET. A foe shows
a red edge and the pointer becomes the spell's own icon: press then. `ravfight.py state` gives the places
(a figure's body about 12 right and 18 down of its object), but in ravhold.sh's bunched party the Draxans
stand behind the members (one at game 164,86 there). After the cast the pointer stays up on the
caster's turn: a right-click on bare floor drops it. In a fight USE serves only the member whose turn
it is: another's portrait says ONLY ACTIVE CHAR CAN CAST. So close USE with **one** Escape and wait
for that member's turn. A second Escape, with nothing open, brought EXIT, and the next keys
(ravfight.py's Q and E) quit the game.

**Hit points raised for a test, then a level-up** (same log): the level's hit points are worked
from the edited ones and can come out negative. Raise them after a level-up, not before.

## Memory edits for a test

The game's records and how to write them for a test are in [the research recipes' memory
edits](RESEARCH-MEMORY.md#memory-edits-for-a-test), by subject. Never save after any of them (rule 8). The
tools, and where each is described:

| Subject | Tools |
|---|---|
| [The party and the map's people](RESEARCH-MEMORY.md#the-party-and-the-maps-people) | `itemlists.py`, `party.py`, `sheetedit.py`, `thief.py`, `award.py`, `kitset.py`, `scrolltest.py`, `npcgear.py`, `thingsfree.py`, `arenatrip.sh` |
| [Items](RESEARCH-MEMORY.md#items-in-memory) | `itemedit.py`, `setitem.py`, `specset.py`, `setarrows.py`, `ammodump.py`, `sprites.worn`, `ring.unlink` |
| [Fights and foes](RESEARCH-MEMORY.md#fights-and-foes-in-memory) | `foeset.py`, `addeffect.py`, `effects.py`, `kinds.py`, `restfixmem.py`, `setmem.py`, `turnwatch.py` |
| [Spells and powers](RESEARCH-MEMORY.md#spells-and-powers-in-memory) | `spellsetup.py`, `turnsetup.py`, `powers.py`, `setmem.py power=` |
| [Creation and levels](RESEARCH-MEMORY.md#creation-and-levels) | `creationscores.py`, `sheetscore.py`, `sheetinfo.py`, `gearpoll.py`, `foeset.py C int=` |

## Pictures for the docs

For an outfit review with the loader detached, stage the walking and fighting chunks in the disposable pictures file before DOSBox starts. Record the object, figure, class combination, and worn items for each party member. A fixed-state capture can verify how the sprite and its palette cycle look in the map view. Exercise inventory changes separately with the loader attached. [Dwarf and human play log](logs/2026-11-23-dwarf-human-outfits.md)

- **Which pictures the class outfits change** (logs/2026-11-27-docs-pictures-retake.md): the map
  figures and the creation screen's figure only. The inventory, Effects and USE screens' portraits are
  the game's own whatever the outfit, so a picture of those screens never needs a retake for outfits;
  check a map picture's figures are the party (the Trustee, Dinos, Scar's gladiators are the game's).
- **Kalzith's shop and body** (`docs/kalzith.png`, `kalzith-body.png`): `openshop.sh` from
  `selling-junk-user` for the talk (that save's shop has the party's sold junk in it, so keep an
  older shop half). The body: from `pens-after-scar` by [ROUTE.md's Kalzith](ROUTE.md#kalzith) to
  `route.py 1560 880`, then `pointer.py attack 120 185` and a click on him at (262,126) from beside
  him (from (1496,840) the click says NO PATH FROM HERE); then `walkto.py 1544 856`, `pointer.py look
  120 185` and a slow press at (262,129) opens the body (a scroll, the Quarterstaff, the Cloak, the
  Ashen Robe); `shot.sh`, 200%. In `selling-junk-user` the attack pointer finds no Kalzith to hit.
- **Wake of the Ravager's screen in its own pixels and colours** (logs/2026-11-28-outfits-vs-stock.md):
  `shot.sh` is Shattered Lands' capture only. The sequel's grab (`ravload.sh`'s `$WORK/rav-loaded.png`, or
  `import -window`) is 640x480, each game pixel twice across and 2.4 times down, in ImageMagick's own palette: take
  every second column and row `int((y+0.5)*2.4)` for the 320x200 picture, and the region palette
  (`ravitems.region_palettes`, each 6-bit value as `v*4+v//16`) for the game's colours (region 1 is Tyr's).
- **Outfits beside the stock people on a real floor**: cut a clean floor patch from a `shot.sh` capture (its
  palette is the game's), tile it, and paint the built pictures (`sprites.Pictures.build`) and the stock ones
  (SEGOBJEX `BMP` frames 0 front, 1 back, 2 side) on it, feet on one line: the scripts are in project files
  `class-figures/stock-comparison/tools/`.
- **A magic item for a look at its box**: [items in memory](RESEARCH-MEMORY.md#items-in-memory).
- **An icon's shimmer** (logs/2026-11-18-item-glows.md): the game cycles four runs of the palette
  in the inventory too (1-5 green, 6-10 violet, 11-15 the water's, 240-248 fire). Move the pointer
  off (`click.py 280 190 none`), take four `shot.sh` captures 0.4 s apart, crop the cell
  (`convert -crop 22x22+X+Y +repage -scale 800%`) and `+append` them; count the pixels of the
  glow's hue that change. In `fountain-user`, items written with `setitem.py` before the ambush's
  speech is clicked are in hand for the fight: Jenna (member 1; her slot-10 weapon at the
  inventory's 173,92, her chest at 173,70), Seneca (member 3: the 4th portrait, 22,160).
- **`docs/look-box.png`** (logs/2026-11-17-ingame-doc-checks.md): the pens' Zombie (creature 21,
  map 1272,856, a room west of Kurzak's), the one creature in the saves' pens with a defence line
  (IMM POISON); none there has magic resistance (`monsters.monster_lines` for each creature shows
  what its box will say). From `pens-kurzak-door`, `teleport.py 1200 864 1112 756` (memory: never
  save after), `pointer.py look`, a slow press on it (160,88); the box is x 171-263, y 49-124:
  `convert -crop 98x82+168+46 +repage -scale 200%` (196x164).
- **`docs/elvenkind.png`** (logs/2026-11-18-docs-review-2.md): from `pens-after-arena`,
  Gerakis's Arm Armor (item 25) made the boots (`setitem.py 25 rec=` with
  `worldgear.ELVEN_BOOTS.hex()`, its slot byte +11h set to 13) or the cloak (`ELVEN_CLOAK`, slot
  12), the inventory open, a right-click on the feet place (174,147) or the cloak place (174,48),
  the pointer off and a `shot.sh` at once: **an item box closes on its own about a second after
  the pointer leaves it**, so only the first capture has it. Crops: the cloak's box 93x66 at
  +184+18, the boots' 112x66 at +173+95, each 200%, side by side, a black row under (410x133).
- **The inventory panel's picture**: I opens the inventory; the panel is `shot.sh`'s x 230-319, y
  0-199, scaled 2x (`convert -crop 90x200+230+0 +repage -scale 200%`). A class can be tried in
  memory ([a class in memory](RESEARCH-MEMORY.md#the-party-and-the-maps-people)); never save after.
- **The Loader's own window for a screenshot** (`docs/dicelog.png`): the container's Python has no
  tkinter; `apt-get install -y python3-tk` gives it to `/usr/bin/python3.12`, which runs
  `python3.12 -m dsloader view` from `obsidian-edition/`. Stop start.sh's text dice log first (by
  pid: two Loaders would both write to the game), and start Xvfb big enough (`-screen 0
  1440x900x24`: the window is 1320x780; topartyfight.sh's checks need the text log, so play the
  opening by hand: S at the menu, the proclamation's seal at 262,165, then boxclick.sh). The two
  windows overlap there: `xdotool windowraise` the one to click. DOSBox keeps the mouse once it has
  it: Ctrl+F10 (`xdotool key --window DOSBOX ctrl+F10`) lets it go, then `xdotool windowfocus` the
  Loader before typing (keys typed with DOSBox focused reach the game). `import -window` grabs the
  window at its size. The opening show is over within about 15 s of the seal: attach the window
  before START GAME to have the default party's opening lines and the show's rounds in its log.
  For a picture of the default **Game window** box (Triple), pick it in the box (the list opens
  below it; Triple is the third line): that writes `window_scale` 3 to settings.json, so set it
  back to 1 afterwards (`launch.save_settings`) or the next start.sh run's checks fail. The status
  line then says "from the next time you start the game" in place of "Connected to the game".
  **The window Loader holds `game.lock`** (logs/2026-11-10-loader-shots-and-chatkcha-line.md):
  - start.sh's text dice log, started beside the window, exits at once. `dice.txt` stays empty, and
    nothing sets the new game's own features (no WILD FIGHTING on the Effects screen).
  - To fix it: kill the window by pid first.
  - A tall picture of the Options tab needs a screen taller than the window: Xvfb `-screen 0
    1400x3400x24`, then `xdotool windowsize W 1320 3300` (`xdotool search --onlyvisible --name .`
    finds the window: its title, "Dark Sun Obsidian Edition Loader ..."). The Options tab at
    (1061,132); a section's header toggles it (Rule changes at 720,260 with all closed), or
    settings.json's `options_open` (a list of the sections' keys: `in_game`, `rules`, `custom`,
    `new_content`, `engine`, `speed`, `picture`, `ravager`, `saves`) opens them as the window starts; the picture is x
    608-1314 from y 116 to under Restore defaults (706x1964 on 2026-11-16; with every section open
    and the fewer switches, 706x1536 on a 1400x2400 screen, 2026-11-18), saved as a 256-colour PNG.
  - Retaken 2026-11-27 (the docs audit), no game needed: the Loader alone, `python3.12 -m dsloader
    view` (the container's python3 has no tkinter) from an export of the folder at a neutral path
    (`git archive HEAD:obsidian-edition | tar -x -C /opt/obsidian-edition`: the Engine section prints
    the program's path), with a stub `dosbox-x/dosbox-x` there that answers `-version` with
    `DOSBox-X version 2025.12.01`, so the Engine section shows the default as a player has it, and
    `options_open` with `engine` and `picture` too (nine sections). The Options tab was at
    (1116,132) by then (the Journal tab came before it); the picture 706x2619, y 116 to 2735.
- **The Loader window under Xvfb** (logs/2026-11-27-loader-pictures.md): a click on a tab or button
  reaches Tk only after `xdotool windowfocus --sync $W`, and `xdotool type --window` types nothing
  (focus, then a plain `type`); a Tk message box grabs black with `import -window`, so crop from
  `import -window root`. A tab click leaves a focus ring on the pane's last button (the Dialogue tab's
  Clear): click in the text before the grab. With the window at 0,0 the tabs are at y 132 (Memory
  tools x 1017, All fields 157, Dialogue 744). The window's dice lines never hold "Step forward" (the
  Dialogue tab has it): wait for "Fight over" when the window, not the text dice log, writes
  `dice.txt`. A script that sources `env.sh` from outside `playtest/` sets `PT` first.
- **`docs/dicelog-readable.png`** (logs/2026-11-19-final-audit-fixes.md): the Loader's window
  attached to a game the kit started, so the kit's loops still run. Xvfb `:55` at 1700x900 (start it
  by hand before `loadsave.sh`: start.sh only starts one when none runs), DOSBox at 0,0 and the
  window moved to 340,0 (`xdotool windowmove`; no overlap, so `click.py` still reaches the game).
  After `loadsave.sh`, kill start.sh's text dice log by pid and start the window from a scratch
  wrapper of `python3.12 -m dsloader view` that also appends `Viewer._append_dice`'s lines to
  `$WORK/dice.txt` (start.sh truncates that file at each start; the wrapper's appends carry on).
  Attach with **Reconnect** (1462,70 on the screen): first Ctrl+F10 to DOSBox (it lets the mouse
  go), after it `xdotool windowfocus` DOSBox and a click in it (it takes the mouse back). Then
  Seneca's backstab round as in [foes in a test fight](#foes-in-a-test-fight) (twice the loads, a
  hit on the second). For the picture: `xdotool windowsize` 1320x880, the panes' sash dragged from
  x 951 to 420 (mousedown, two moves, mouseup), the round cropped from the root window with **Show
  details** ticked, and again unticked (its box at 438,240), one crop above the other.
- **The window's Play Shattered Lands (once Start the game) in the container** (the same log): it runs `prepare_patched_game`
  (the copies rewritten, a check of `write_atomic`), then stops at GOG's `DOSBox.exe`, a Windows
  program ("[Errno 13] Permission denied", a message box: OK at 1000,470). A game it was attached
  to that is killed is seen within a few seconds since 2026-11-19 (`Disconnected (process N has
  ended). Waiting for the game...`); before, attached by Reconnect, it said "Connected to the game"
  on and Start did nothing (logs/2026-11-19-older-loader-bugs.md).
- **The window across a kit reload** (the same log): `loadsave.sh` is a new DOSBox (start.sh's
  `pkill -9 -x dosbox`; the game has no load without a restart here), so the window shows
  `Disconnected (process N has ended)` for a few seconds, then attaches to the new one by itself,
  through the title and the load: no Reconnect needed (still kill start.sh's text dice log by pid,
  or two Loaders follow the game when the window's folder isn't the kit's). An old Loader's window
  (origin before 2026-11-19) needs `kill -9` to show its stale "Connected" and the party table's
  `unpack requires a buffer of 4 bytes (game.py:798)`; a plain `kill` let DOSBox's own exit give a
  read error, which it did notice.
- **The party view's thief skills**: the Characters tab, the mouse wheel over the cards (25 clicks
  of button 5) to reach the fourth; a thief's card ends `Thief skills now: pick pockets 72%, ...`.
- **The load window** (`docs/save-pages.png`): a save's name is its STXT chunk
  (`namedsaves.NAME_CHUNK`), a fixed field padded with zeros, so ten saves with plain names are the
  kept saves copied to `$PLAYTEST_WORK/inst/SAVE01-10.SAV` with that field rewritten in place
  (`gff.read_gff` for the old bytes, then `find` and overwrite). Title, LOAD SAVED GAME (170,109),
  the pointer moved off the list, a shot; PAGE 2 (252,106), a shot; both side by side at 200%.
- **`docs/viewer.png`**: Xvfb `:56` 1440x900, `dosbox FAKEPTY.COM -exit` in a scratch folder,
  `python3.12 -m dsloader view` (apt's `python3-tk`). Clicks by window position (`xdotool mousemove
  --window W X Y click 1`): Memory tools (950,132), name box (735,199), Search (913,199), the hit
  (700,268), Assign (956,235), All fields (161,132), a byte (995,499). The Game window list is a
  separate window (`import -window` shows it black): Triple is its third line (600,132 on the
  screen); it writes `window_scale` 3, so copy settings.json back afterwards. Picking it there can
  leave a black patch and a window that takes no more clicks: then kill both by pid, start
  `FAKEPTY.COM` first and the window after it (it reads Triple from settings.json and connects at
  once), and do the clicks within ~10 s. From the program's start to the shot in about 9 s: Sadira
  21/30.
- **The practice program** (`tests/make_fake_party.py`, for `docs/viewer.png`): run `dosbox
  FAKEPTY.COM` in a scratch folder, then the window; Sadira loses 1 HP a second and her byte wraps
  past 0 (133/30 two minutes in), so search `sadira`, pick the hit and Assign within about 15 s of
  starting it. Reconnect picks up a restarted DOSBox.
- **The combat log's doc pictures** (logs/2026-11-09-combat-log-shots.md): from `fountain-user`'s
  ambush, `scroll.py -60 -80` in the fight brings the party left of the panel (the panel's buttons:
  [controls](#controls)). Pictures are `shot.sh`'s scaled 200%; a GIF is `import -window` grabs in a
  loop (about 32 a second), picked 40 ms apart and `convert -delay 4 -scale 200% -layers Optimize`.
  For a GIF at the docs' 640x400, take DOSBox's own screenshots in a loop (`xdotool key --window W
  ctrl+F5; sleep 0.04`: about 14 a second, all kept, in `inst/__support/app/capture/`), then `convert
  -delay 8 dsunlog_*.png -scale 200% -layers Optimize` (314 frames, 457 KB). Window grabs are
  320x240 (4:3) and gave 1 MB; Ctrl+Alt+F5, DOSBox's video capture, wrote no file. From a fresh
  load of `fountain-user` the first turns stay near the camera after `scroll.py -60 -80`; later a
  member out of movement gets the END menu over the panel (E ends the turn).
- **`docs/steady-pace.gif`** (logs/2026-11-16-doc-pictures.md): `PT_CYCLES=20000 sh pacerec.sh off
  $WORK/off.mkv`, then `... on $WORK/on.mkv` (each: the setting written, start.sh, pens-after-arena,
  the panel hidden, ffmpeg's x11grab at 70 frames a second for 13 s, clicks east and back; it stops
  itself with `-t`: a `timeout` kill leaves the file unreadable). Then both side by side at half
  speed: `ffmpeg -ss 0.8 -t 10 -i off.mkv -ss 0.8 -t 10 -i on.mkv -filter_complex
  "[0:v]pad=324:240:0:0[a];[a][1:v]hstack,setpts=2*PTS,split[s0][s1];[s0]palettegen=max_colors=128:stats_mode=diff[p];[s1][p]paletteuse=dither=none:diff_mode=rectangle"
  -r 35 out.gif` (about 500 KB). Take `steady_pace` out of settings.json after. At 35,000 cycles
  the two sides look alike: record at 20,000.
- A spell's description box and the doc panels of spells: [casting
  spells](#casting-spells-for-a-test).
- **The party wears its class outfits only with the dice log attached** (2026-11-27,
  logs/2026-11-27-outfit-screenshots.md): the Loader dresses the figures live, so a game started
  without it (picstart.sh before that day) shows the copy's older looks. Every picture of the party
  comes from a game the kit started (start.sh, loadsave.sh, picstart.sh) or the window attached.
- **The pictures retaken for the outfits** (the same log): the combat log's four and
  `hit-chance-hover.png`, `squares-in-reach.png`, `floating-names.png` from `fountain-user` (the
  camera put left of the panel with `camera.py`, `untilturn.sh` with Ctrl+F5 in a loop for the
  GIF); `shadows.png` (`shadowsw.py 0`, the view scrolled a pixel and back), `rings.png`,
  `default-party-armor.png`, `floating-charges.png` (Armor dropped on Gerakis's portrait: Cilla
  hides and isn't struck), `whirlwind.gif` (Cilla made an air druid with `sheetbyte.py 3 0x22 5`
  and `spellsetup.py 3=12`, LEVEL to 6), `dust.png`, `magic-glint.gif` (`itemplus.py`) from the
  arena's waves after `topartyfight.sh`; `see-through.png`, `picture-modes.png`, `steady-pace.gif`,
  `gear.png` from `pens-after-arena`; `creation-store-recall.png` from a new character. To catch a
  label or a spell's bolt, start a grab loop before the click. A Ctrl+F5 loop was too slow for
  Fogbolt's bolt (gone by the first capture); a loop of `import -window $W` grabs (60, `sleep 0.03`
  between, about 0.1 s apart) caught it in flight (logs/2026-11-27-docs-review-pictures.md: Lex, made to
  know Fogbolt, on his turn in `fountain-user`'s ambush, at the Templar; the 25th grab). `spellsetup.py` can't teach the mod's new spells (196 and up): a new
  wizard spell is a bit in the sheet (`sheetbyte.py M 0x45 or0x40`, Fogbolt), a new 6th-level
  priest spell comes with the caster's sphere.
