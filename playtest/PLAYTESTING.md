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
3. **Start from a saved game past the parts you don't need**: `sh loadsave.sh NAME` loads one of
   `playtest/saves/` (see its README: `pens-after-arena`, the slave pens after the arena). None
   came with the game and none were on the Drive (2026-11-01). **Save at every milestone** (below)
   and add the save to `playtest/saves/` with a line in its README, then commit: replaying the
   arena took most of a day.

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

## 1b. The recompiled program as the target (Dark Sun Recompiled)

The kit drives the recompiled program too (`PT_TARGET=recomp`, exported for every tool; `DSUN`
names the program, default `/home/user/darksun-recompiled/build/cmake/dsun`), 2026-11-01:

- `start_recomp.sh` (and `loadsave.sh` under that target) starts it with the Loader's patched
  game (`prepare_patched_game`, as start.sh) and the mod's `dos` folder, makes its window 320x240
  at 0,0 (so the window grabs and their pixel positions are DOSBox's), records its pid in
  `$WORK/dsun.pid` (the dice log and `live.py` use that pid: other dsun processes may be headless
  runs of the program's own tests, and `dsloader dicelog` refuses to guess among several) and
  attaches the dice log. **Its build must match the mod's helper**: the program lifts
  `dos/DSCLOG.EXE` into its `build/ds1o`; a branch with a newer helper needs
  `tools/build_mod.sh <this repo>/obsidian-edition` in the program's repository and its
  convergence runs first (a wrong helper shows as `no function at B....` in `$WORK/dsun.log`).
- `shot.sh` grabs its window and scales it to 320x200 (there is no Ctrl+F5 capture). Its colours
  differ from DOSBox's by one (38 of 63 is 153, DOSBox says 154) and its picture is stretched to
  240 rows a row apart, so pixel checks go through `pixmatch.py` (within 3 a channel, a row up or
  down): msgbox.sh, panel.sh and levelup.sh use it.
- Controls behave as in DOSBox: click.py's relative moves converge on the pointer, walkto walks,
  right-click cycles arrow, red sword, red look, arrow; the arrow over a person shows the portrait
  pointer and a click opens the mod's Look box (Talk is its first button, 216,99).
- **The view does not scroll by itself** here either; the middle-button drag did nothing on the
  program until its runtime passed the middle button through (fixed 2026-11-01: every button but
  the left had been the right one). A kit tool that stalls on the program and not in DOSBox is a
  program fault to report, not a tool to work around.

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
- **Pixel checks** go through `pixmatch.py` (colours within 3, a row either way, for the
  recompiled program); it uses PIL, or ImageMagick where PIL is broken (2026-11-01: "cannot import
  name '_imaging'" made every msgbox.sh call fail).
- **Two picture sizes**: `shot.sh` saves the game's own capture, 320x200; a window grab
  (`import -window`, which msgbox.sh, panel.sh and levelup.sh use for speed) is 320x**240**, the
  height stretched: a pixel at y in a capture is at y x 1.2 in a grab. Take a pixel's coordinates
  from the same kind of picture the check uses (panel.sh read the wrong row this way for a day).
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
  screen centre. **The view can stop scrolling**: in the arena (2026-11-01) it stayed put with the
  leader at the top edge (screen y 24, under the top bar), so nothing north of it could be clicked;
  resting the pointer on the edge didn't scroll it, and writing DS:1178h (`camera.py X Y`) changed
  the number but not the picture (it's a copy, not what's drawn).
- **Scrolling the view: drag with the middle mouse button** (`python3 scroll.py DX DY`; the
  user's advice, 2026-11-01). It moves the map like grabbing it: dragging down shows more of the
  north (60 pixels moved the camera 48 map units, in steps of 16). **Keep the pointer off the
  screen's edges while dragging**: at an edge the view scrolls by itself the other way, so a long
  drag from the centre ran the pointer off the bottom and sent the view south, and a loop that
  sized each drag from the last ran it off to (0, 1368) (2026-11-01). scroll.py starts each drag
  on the side it moves away from and caps it (270 x 150 pixels). Then click the spot and the
  party walks there, finding its own way round walls. **After a drag, release every button**
  (scroll.py does): the game took no clicks at all until they were. **A message box blocks drags
  too**: drags made under one did nothing, and the view later jumped. Clear boxes first. A click on a wall or off the walkable area does nothing but log "NO PATH FROM
  HERE"; walkto stops after two clicks that don't move the leader.
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
- **Long walks: hop.** A click a few hundred map units away walks the party there, round walls
  (1672,344 to 1400,344 in the pens), but a click across a whole region says NO PATH FROM HERE,
  and the view snaps back to the party. Plan hops on a map picture (`mapshot.py`, below) and
  use `viewto.py X Y` to bring each hop's spot on screen before clicking it; clicks on walls or
  on the edge of the screen (often a wall) do nothing. walkto.py drags the view back to the
  leader when it falls behind.
- **Message boxes** (a speech box with a portrait at the top, or the grey message window) take a
  click to go away, and while one is up Tab, Return, map clicks and drags do nothing. `msgbox.sh`
  tells whether one is up; **click ON the box** (`boxclick.sh`: 160, 20): a click wherever the
  pointer was (low on the map, after a drag) left "Excellent! These gladiators wish to fight
  again!" up through a whole loop of clicks (2026-11-01). `dismiss.sh` does this for several.
- **YES/NO questions** ("Yell something back at the Announcer? (Answer Yes or No)") look like a
  message box, but a click doesn't answer them: press **N** (or Y). One is waiting only while the
  dice log's last line is `    2. No` (answered, `    > No` follows): a check for "2. No" in the
  last few lines took an old, answered one for a new one (2026-11-01). `dismiss.sh` stops at one.
- **Keys**: Tab picks the nearest enemy and Return attacks it (the mod's keys, in a fight); L shows
  or hides the combat log panel; **E opens the Effects screen** (not "end turn"); Escape closes a
  screen or menu that is open, and **opens EXIT GAME? when nothing is**: a click after that can quit
  to DOS. Press Escape only with a menu or screen showing.
- **Ending a turn by hand**: a click exactly ON the active member's figure opens END <NAME>'S
  MOVE (GUARD / WAIT / END TURN); a click beside it walks it a step instead. In that menu press
  **E** for END TURN: when Return opened it (no Move left), clicks on its rows didn't register
  (2026-11-01). E with no menu up opens the Effects screen instead (Escape closes that).
- **Loose `xdotool` commands need `DISPLAY=:55`** (`export DISPLAY=:55` first): the kit's tools
  set it, a command typed on its own doesn't ("Can't open display").
- **The combat log panel covers the bottom right** (x 135+, y 120+): a click there lands on the
  panel, not the map. Press L to hide it before walking near it (the party's first step into the
  arena, for one, is right above it).

- **Level-up screens block everything**: CHOOSE A SPELL (a preserver's new level, mid-fight)
  waits for a spell's icon to be clicked; the watchdog reports it as STUCK. `levelup.sh` finds it
  (its scroll's rollers) and clicks the first spell (125, 90); fightout.sh runs it each turn.

- **Saving**: Escape (nothing else open) brings EXIT: SAVE GAME? (SAVE / QUIT / CANCEL); **S**
  opens the SAVE screen: click a slot (the first at 120, 46), type a name (`xdotool type`), click
  SAVE (253, 46). "GAME SAVED", and then **the game quits to DOS** (it's the exit menu): restart
  with loadsave.sh. The slot is `SAVE01.SAV` in the game folder (85,680 bytes), with
  `CHARSAVE.GFF` and `DARKRUN.GFF` written at the same time; keep all three.
- **Loading**: the title (two clicks), then the main menu: START GAME, CREATE CHARACTERS, LOAD
  SAVED GAME (170, 109), EXIT TO DOS; the LOAD screen lists the slots (click one at 100, 46), then
  LOAD (253, 46). `loadsave.sh` does it.
- **Talk menus** (WHAT DO YOU SAY?): number keys don't choose; click the line. The list scrolls:
  its down arrow is at (311, 187), and the last visible line is about y 189. The dice log lists
  every choice with a number, which helps find the one wanted.

## 4. Fights

1. **Story fights: `sh fightout.sh`.** It sets every foe to 1 HP (not the arena's prisoners) and
   finishes the fight with Tab + Return on each party turn, clicking messages away and pressing E
   (END TURN) for a member with no Move left, so the game's scripts see every kill. It refuses to
   run with no fight on: run outside one, hp.py and its keys did harm (a prisoner at 1 HP, the
   party stuck in place).
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
8. **Never `pkill -f` or `pgrep -f | kill` a pattern your own command line contains**: it kills
   the shell running it (exit 144, twice on 2026-11-01, the second time with this rule already
   written: run the kill as its own command, by pid, and nothing else in it). Kill by pid (`pgrep -f "sh leavearena.sh"`, then `kill PID`). And
   stopping a background task can leave its children running: check with pgrep afterwards.
9. **Never cut steps out of a bigger script with sed**: its header may restart the whole game.
   Use the small tools.
10. **Every step gets its own `timeout`**; long runs go in the background and are followed through
   the watchdog's Monitor, not by sleeping.

## 5. The story so far: what's known of the route

**A new game** (`start.sh`, then `topartyfight.sh`: START GAME, the ready-made party, the opening,
the step forward) ends in the arena's first fight (region 2Ah), party at about (488, 424).
- The opening's show fight (a Rampager kills a Defiler) isn't the party's: leave it be.
- The party then waits at the gate (488, 168-184): "Gladiators: Step forward, into the arena!".
  One step south takes it to (488, 232), between the gate and the bone wall; the game brings it
  into the arena (488, 424) and starts the fight on its own once some game time has passed:
  keep clicking south (each click passes time) until `fight_on 1`, about 8 clicks.
- Then `sh arenawaves.sh`: every wave fought with fightout.sh, the messages between, and the
  YES/NO question answered N; and at once `sh leavearena.sh`: the view dragged north until the
  ground inside the wall (488, 232) shows, a click there (the party finds its own way in), then
  the gate strip, until the region is the pens (29h). Run them together:
  `(sh arenawaves.sh && sh leavearena.sh)`, in the background, followed with a Monitor.
- **The combat log panel**: `sh panel.sh hide|show` checks the panel's pixel before pressing L
  (L alone toggles, and can leave it the wrong way round).

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
- **After a repeat fight the arena may only say "Go back to the pens"**, with no YES/NO question:
  arenawaves.sh stops at either.
- **Staying sends another fight** each time: "Excellent! These gladiators wish to fight again! We
  shall see how they fare!" (Silt Runners, a Screamer Beetle...), then "Go back to the pens" again:
  the arena repeats until the party leaves. Each fight can bring a level-up screen.
- **The clock after "Go back to the pens" is short**: a few walking clicks, then "Since you will
  not leave, you must fight!" and another fight (Silt Runners...). Leave at once, and don't walk
  south or east first: the 2026-11-01 run lost its time getting the view to the wall.
- **Out of the arena (done 2026-11-01, the fourth run):** after the last fight, drag the view
  north (scroll.py) until the ground inside the wall (488, 232) shows, click it, and the party
  walks round into it by itself; then click the gate strip (488, 184): "This corridor leads down
  to the slavepens. Do you wish to continue? (Answer Yes or No)": **Y** (N, as for the Announcer,
  turns it down, and the question comes back only on stepping off the strip and on again). The
  party comes out in the pens (region 29h) at (1816, 440). `leavearena.sh` does all of it.
- **Leaving the arena (the user's advice, 2026-11-01):** if the party stops at the stone wall,
  click inside the wall's boundary: the party finds its own way in, and that safely takes it back
  into the pens. Don't stay outside the walls in the arena: more monsters are sent.

**Map pictures**: `python3 mapshot.py OUT.png [W H]` steps the view across the region and pastes
the captures at their cameras: one map unit a pixel, so a point's pixel is its map position.
Region pictures made so far are in `playtest/maps/`.

**The slave pens (region 29h)**: through the gate the party comes out at (1816, 440) and Kurzak
meets it ("These are the slavepens. I'm Kurzak, leader of the guards. Follow me. I'm here to lead
you to your cell."; his menu: help me escape or I'll kill you, about yourself, the half-giant,
escaped slaves, the exits, Goodbye: "Get moving! I gotta get back to work."). Saved there:
`pens-after-arena`. The way to the grate, from the scripts and the region file (2026-11-01):
- The stalker pen nearest the north: its door, objects 2163/2164 at (256, 864-896), is barred.
  Using it says "The door is locked. It appears quite sturdy."; attacking it (138:121h) rolls
  RAND(30) against the attacker's STR to bash it open, and the Mountain Stalker (151, at 187,856)
  then hunts the party. A second stalker pen is further south (door 2157/2158 at 255,1087-1119).
- **From the save, follow Kurzak**: the party starts shut in the corridor where Kurzak met it
  (1352-1400, 344): a gate at squares (81, 20-21), map (1304, 320-351), the gold post west of it,
  is closed (live grid 192/193), clicking it does nothing, and no script opens those squares.
  Kurzak (object 29) walks his route a waypoint at a time (141 at 0h: squares 99,25 then 99,31...),
  each waiting for the party within 4 squares: `python3 follow.py 29` keeps walking the party
  beside him. At (99, 32): "All right, go through the door. There's a place to rest down the east
  hall. I'll come get you when it's time for your next fight. If you want to fight before that,
  knock on the door." 
- **Opening that door sets off the alarm** (the user, 2026-11-01): plan for it (the guards come)
  or find another way to the button.
- Button 1281 at (139, 748), the pen's north wall: used from within 4 squares (137:1AE8h, else
  "is too far away to press the button") it sets flag 518 and "hears a click as the secret door to
  the west opens". (Button 1280 at 1335,798 opens another door, 81-82,53-54, only once the monster
  266 at 1264,848 is gone or flag 317 is set; otherwise "presses the button, but nothing happens".)
- The grate, object 1234 at (46, 86), the far northwest; walking onto squares 3-4, 5-6 (map
  48-79, 80-111) runs its menu (137:29Bh): Pick the lock / Rip it open / Hack the lock off.
- The pens' cell doors (2141-2164) have USE (script 138) and ATTACK handlers ("This door is too
  strong to bash open" for the cells').

From the cluebook's map: #11 the stalker pen (break the door,
kill the mountain stalker, push the button on the north wall: a secret door to the northwest
corner), #12 the sewer grate (square 46, 86; "use" it or walk over it: rip, hack or pick; a failed
try can be tried again), #15 the campfire (rest; two rests bring the next arena fight; keeping
Kurzak waiting sets off the alarm), #10 Pehtucl's ambush (Bloodwrath on his body).

## 6. After

**Other sessions push to this branch too** (2026-11-01: a Dark Sun Recompiled session changed the
kit while this one played): `git fetch origin obsidian-edition` and `git rebase
origin/obsidian-edition` before every push, read what changed in `playtest/`, and keep both
sessions' lessons. The kit drives the recompiled program as well (`PT_TARGET=recomp`,
`start_recomp.sh`).


**After every play, add everything learned to this guide** (the user's standing instruction,
2026-11-01): not only stalls, but every control, screen, message, map position, route step,
timing, script detail and tool change found while playing, each where it belongs above, then
commit and push. Do it at each stop, not only at the end: a pause can lose the container.


1. Stop the watchdog; restore anything raised in memory.
2. Send the test log; copy it to `playtest/logs/` and commit.
3. Add any new kind of stall to this guide (a numbered rule, the date and the test), and any new
   tool to this folder, then commit and push both.
