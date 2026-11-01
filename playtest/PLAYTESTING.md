# Playing the game for a test: read this before every in-game test

This is Claude's own guide to driving Dark Sun: Shattered Lands in a headless DOSBox, so that an
in-game test (a fix seen working, a screenshot for the docs) doesn't stall. Every rule here comes
from a test that got stuck. **Read it all before starting, follow it in order, and add to it
(then commit and push) whenever a new kind of stall turns up.** It lives in the repository, at the
root and outside `obsidian-edition/` (so it never ships in a release zip), because the scratch
folder and everything in it is lost when the container is reclaimed: an earlier version of this
guide and its tools were lost that way.

The tools are in this folder. Each finds its own paths (`env.sh`, `paths.py`): the repository,
a work folder for screenshots and logs (`PLAYTEST_WORK`, default `/tmp/playtest`) and the
extracted game (`DS_GAME`, default `$PLAYTEST_WORK/inst`). Nothing in the work folder is kept.

## 0. Before anything

1. **Keep a test log the user can read, and send it as it fills.** Write it in the work folder as
   you go (what's under test, each step, what was seen), and send it with SendUserFile at each
   milestone and when stopping. At the end copy it to `playtest/logs/DATE-what.md` and commit it.
2. **Plan the route first.** Know where the thing under test is and how the party gets there:
   the cluebook (`Cluebook.PDF` in the game folder: `pdftotext -layout`), the scripts (`dec.py`,
   the triggers in the region's MAS script), the region's entities (ETAB in `RGNxx.GFF`). Don't
   assume a place is reachable from a new game: check what the story requires (the slave pens'
   sewer grate, for one, is behind the stalker pen's secret door).
3. **Look for a saved game past the parts you don't need.** There are none in the extracted game.
   Ask the user, or look on their Google Drive (the Drive connector) for save files, before
   playing a long way in.

## 1. Setting up

1. Packages: `dosbox Xvfb xdotool imagemagick innoextract poppler-utils` (check with
   `command -v`; they were installed in the 2026-11 container).
2. The game: `sh setup_game.sh` (the GOG installer from the user's Google Drive, file id in the
   script, extracted with innoextract into `$DS_GAME`).
3. `sh start.sh`: Xvfb `:55`, the Loader's patched game (`prepare_patched_game`, so a rebuild is a
   restart), DOSBox, and the Loader's dice log (`$WORK/dice.txt`). Kills any old ones.
4. **Check the build under test is in place** (every restart): the game runs
   `obsidian-edition/dos/` (GPLDATA.GFF, DSUN.EXE's patched copy...). For a script change, decode
   the built copy (`GPLDATA=../obsidian-edition/dos/GPLDATA.GFF python3 dec.py SCRIPT LO HI`) and
   check the change is there before trusting anything seen in play. Memory edits are lost on any
   restart.
5. **The watchdog**: `sh guard_start.sh`, then a Monitor on `$WORK/guard.log` (grep
   `STUCK|GONE`) for the whole test. Stop it (`kill $(cat $WORK/guard.pid)`) before going idle.
6. **DOSBox dies when the session sits idle** (the container's processes are reclaimed). After
   any pause (waiting on the user), check `pgrep -x dosbox` before the next step; if it's gone,
   start again from `start.sh`. Don't leave a test half-done across a pause expecting it to be
   there.

## 2. Reading the game

- `python3 state.py [FLAG...]`: fight on, whose turn (0-3 the party), region, the leader's map
  position, the camera, and any game flags (`state.py 11 505`).
- **A game flag reads as 0 whenever the flags have no place in memory** (`gd.flag`: their pointer,
  DS:1352h, is null at times, such as in the arena outside a script's run). Check `gd.flags_ready()`
  before believing a 0; `state.py` prints `flags ?` when they can't be read (2026-11-01: an arena
  "flag 11 never set" was only this).
- `$WORK/dice.txt`: the dice log: every roll, every line of dialogue and narration
  (`[Narration] ...`, `[The Announcer] ...`), menus with their choices, and "Message: NO PATH FROM
  HERE". Read its tail after each action; it is the most reliable record of what happened.
- `sh shot.sh OUT.png`, then Read the picture: the game's own 320x200 capture. Look at the screen
  before any key that could do harm (Escape) and whenever a step didn't do what it should.
- `live.py` (exec'd by the Python tools) gives `g` (memory), `ds`, `gd` (dsloader's GameData);
  `CAMERA` (DS:1178h) and `POINTER` (DS:A133h).

## 3. Controls that work

- **Clicks**: `python3 click.py X Y [left|right|none]` in game pixels (320x200). DOSBox captures
  the mouse, so the tool moves it relatively until the game's own pointer reads X,Y. Plain
  `xdotool mousedown/up` clicks where the pointer already is (fine for dismissing a message).
- **Pointer mode**: a right-click on the map cycles it: the plain arrow (Walk, and use/talk on a
  thing), a red sword (attack), another red one, back to the arrow. Check the pointer in a
  screenshot before walking.
- **Walking**: `python3 walkto.py X Y` (map units). Screen = map - camera, 1 unit a pixel; the
  camera scrolls in steps and does NOT keep the leader centred, so work from the camera, never the
  screen centre. A click on a wall or off the walkable area does nothing but log "NO PATH FROM
  HERE"; walkto stops after two clicks that don't move the leader.
- **Message boxes** (a speech box with a portrait at the top, or the grey message window) take a
  click to go away, and while one is up Tab, Return and map clicks do nothing. `msgbox.sh` tells
  whether one is up; `dismiss.sh` clicks them away.
- **YES/NO questions** ("Yell something back at the Announcer? (Answer Yes or No)") look like a
  message box, but a click doesn't answer them: press **N** (or Y). `dismiss.sh` stops at one and
  says so.
- **Keys**: Tab picks the nearest enemy and Return attacks it (the mod's keys, in a fight); L shows
  or hides the combat log panel; **E opens the Effects screen** (not "end turn"); Escape closes a
  screen or menu that is open, and **opens EXIT GAME? when nothing is**: a click after that can quit
  to DOS. Press Escape only with a menu or screen showing.
- **Ending a turn by hand**: a click exactly ON the active member's figure opens END <NAME>'S
  MOVE (GUARD / WAIT / END TURN); a click beside it walks it a step instead. The menu's position
  varies: read its rows off a screenshot before clicking END TURN.

## 4. Fights

1. **Story fights: `sh fightout.sh`.** It sets every foe to 1 HP and finishes the fight with Tab
   + Return on each party turn, clicking messages away, so the game's scripts see every kill.
2. **Never `killfoes.py` in a fight a script waits on.** Kills made in memory bypass the scripts'
   reactions to them (in the arena, none of the Announcer's lines about the kills). It is only for
   fights no story depends on, and the fight still needs its turn ended.
3. **The arena sends waves.** After one fight ends, messages, then another fight: run
   `fightout.sh` again until the wave messages stop (a YES/NO question ends them).
4. **Whose turn**: `state.py`'s `turn` (0-3 the party); never guess from sleeps. Act only on party
   turns; enemies act alone.
5. **Movement**: a member with no Move left can't reach anyone; a click then opens its END menu or
   does nothing ("Move : 0"). For a test that needs reach, raise its Move in memory first (the
   old movekeeper.py did; rebuild it when needed: the combat record's movement, see
   dsloader/game.py), and restore it after; never save the game while it's raised.
6. **Spells**: open the USE button (24,17), page to the spell, click its icon, then the target;
   check the dice log for the spell's line before going on. If none appears, look at the screen:
   usually a menu left open, the wrong spell page, or no Move or slots left. Try Tab + Return at
   the targeting step before clicking a figure.
7. **Shots**: unreliable. Enter is a left click on the enemy: with Move left the member walks up
   and fights hand to hand; with Move 0 the END menu opens; in Attack mode a far target showed the
   red "can't" pointer and the turn passed. A shot test needs a clear line, a target in range, and
   a readied missile weapon with ammunition in the missile slot.
8. **Never cut steps out of a bigger script with sed**: its header may restart the whole game.
   Use the small tools.
9. **Every step gets its own `timeout`**; long runs go in the background and are followed through
   the watchdog's Monitor, not by sleeping.

## 5. The story so far: what's known of the route

**A new game** (`start.sh`, then `topartyfight.sh`: START GAME, the ready-made party, the opening,
the step forward) ends in the arena's first fight (region 2Ah), party at about (488, 424).

**The arena (region 2Ah)**, as of 2026-11-01:
- Several waves (Sligs and a Screamer Beetle; Sand Howlers and a Tohr-kreen; ...), then "The
  crowd is awed...", the Announcer, and "Yell something back at the Announcer?" (N), then
  "Attention gladiators: Go back to the pens to heal your wounds." The game clock barely moves
  while the party stands; if it doesn't leave in time: "The patience of the citizens of Draj is
  not infinite. Since you will not leave, you must fight!"
- **Open problem: the way out.** MAS 42's move triggers: squares 5-7 at rows 30-32 run script 3
  at 6B4h ("Gladiators escaping! Guards! Sound the alarms!": avoid); a strip at squares 28-32,
  row 11 runs script 3 at 73Eh, which (with flag 11 set and local 32 at 0) teleports the party to
  the pens (region 29h, 113, 27). Flag 11 is set by script 2 at BB8h (its handler at B61h is
  called from script 4 at B23h). In the 2026-11-01 run the party walked straight north from
  (488, 424) and stopped at the bone wall (488, 328: NO PATH FROM HERE), and the arena ran out of
  patience before the way out was found. Next time, before the fight: note where the party
  stands when the arena loads (it comes in by the gate, and the opening's "step forward" walks it
  south from there), and find that strip on screen (squares are 16 map units: x 448-527,
  y 176-191) before the "Go back to the pens" line starts the clock.
- The cluebook (#13): "Follow Kurzak to and from the pens when fighting in the Arena."

**The slave pens (region 29h)**, from the cluebook's map: #11 the stalker pen (break the door,
kill the mountain stalker, push the button on the north wall: a secret door to the northwest
corner), #12 the sewer grate (square 46, 86; "use" it or walk over it: rip, hack or pick; a failed
try can be tried again), #15 the campfire (rest; two rests bring the next arena fight; keeping
Kurzak waiting sets off the alarm), #10 Pehtucl's ambush (Bloodwrath on his body).

## 6. After

1. Stop the watchdog; restore anything raised in memory.
2. Send the test log; copy it to `playtest/logs/` and commit.
3. Add any new kind of stall to this guide (a numbered rule, the date and the test), and any new
   tool to this folder, then commit and push both.
