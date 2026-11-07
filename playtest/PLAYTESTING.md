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
   `playtest/saves/` (see its README: `pens-after-arena`, the slave pens after the arena;
   `pens-thornwall-rack`, the party by the weapon rack with Thornwall on it). None
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
   For a DSCLOG change, find a few of the new code's bytes in memory where they are in
   `dos/DSCLOG.EXE` (less its 20h header, from DSCLOG's segment: C91B0h in the 2026-11 runs), and
   read the vectors it hooks in the table at segment 0 (each its own handler: two probes on one
   vector once made every attack's AC 255). `ghostchk.py` shows the see-through block is there.
   `dec.py` stops with "unknown term" when LO falls inside a command: start it at a command
   (or decode the whole script with `dsloader.gpl.load_scripts` and `decode`). Every script in
   the built copy should decode (2026-11-05: eleven didn't, and a later change gave up on one).
5. **The watchdog**: `sh guard_start.sh`, then a Monitor on `$WORK/guard.log` (grep
   `STUCK|GONE`) for the whole test. Stop it (`kill $(cat $WORK/guard.pid)`) before going idle.
6. **DOSBox dies when the session sits idle** (the container's processes are reclaimed). After
   any pause (waiting on the user), check `pgrep -x dosbox` before the next step; if it's gone,
   start again from `start.sh`. Don't leave a test half-done across a pause expecting it to be
   there.

7. **After a worker restart Xvfb is gone too**, and start.sh in the background didn't restart it
  (every xdotool call: "Can't open display"). `pgrep -a Xvfb`; else `setsid nohup Xvfb :55 -screen
  0 1024x768x24 &` by hand.

**Fresh container (2026-11-06):** `apt-get update` then install `dosbox xdotool innoextract nasm`
(`Xvfb`, ImageMagick, poppler were there). The Drive installer download is blocked by the default
network policy (403 on `drive.usercontent.google.com`): allow that host with update_environment, wait
~20 s, then `setup_game.sh` works (22 MB). `start.sh` shows the window at 640x400 until a save is
loaded; after `loadsave.sh` it is 320x240. `toalarm.sh` then `restalarm.sh` worked first time (the
pointer: two right-clicks on bare floor; a red eye with a bar over floor is the eye). Cilla's
hide lands often at 95 (d100 94 ok); her walk frames: `walktime.py 3 X Y DIR`, crops of
`import` grabs (120,50 70x70) tiled with montage.

**The environment's setup script (2026-11-06):** the user's "Google Drive" cloud environment now
installs `innoextract nasm dosbox xdotool`, `pip install capstone unicorn`, and runs
`setup_game.sh` into `/tmp/playtest/inst` when the container is built fresh, with
`drive.usercontent.google.com` and `drive.google.com` already allowed. So a new session should
only need `export PLAYTEST_WORK=/tmp/playtest`, then `loadsave.sh` (check `command -v dosbox` and
`$PLAYTEST_WORK/inst/DSUN.EXE` first; if missing, run the steps above by hand). Checked by hand
that day: the download went through with no environment change, `loadsave.sh pens-after-scar`
loaded (region 29h, leader 1816,440, window 320x240, dice log attached). A worker restart of
the session killed DOSBox as an idle pause does. With the game's files the unit tests run
more: `DSUN_GPLDATA=$G/GPLDATA.GFF DSUN_OBJECTS=$G/SEGOBJEX.GFF DSUN_RESOURCE=$G/RESOURCE.GFF`
(`G=$PLAYTEST_WORK/inst`) left 8 skipped (tkinter's), not 15.

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
- **The dice log must be attached after the game is loaded**: attached at the program's start,
  or before a save is loaded, it printed nothing afterwards (2026-11-01, twice); `loadsave.sh`
  restarts it after the load, and after any restart of the program check that an action shows in
  `$WORK/dice.txt` before trusting its silence.
- **Saves cross over both ways**: a save made in DOSBox loads on the program (pens-kurzak-door),
  and one made on the program loads in DOSBox (pens-kurzak-door-recomp). The program's save
  leaves DARKSAVE.GFF as it was, as DOSBox's did.
- Controls behave as in DOSBox: click.py's relative moves converge on the pointer, walkto walks,
  right-click cycles arrow, red sword, red look, arrow; the arrow over a person shows the portrait
  pointer and a click opens the mod's Look box (Talk is its first button, 216,99).
- **The view does not scroll by itself** here either; the middle-button drag did nothing on the
  program until its runtime passed the middle button through (fixed 2026-11-01: every button but
  the left had been the right one). A kit tool that stalls on the program and not in DOSBox is a
  program fault to report, not a tool to work around. **The drag scrolls only with the Loader
  attached** (the dice log counts: it switches the helper's `scroll_on` on at attach); a program
  started with no Loader, as its own headless tests run, keeps the view still (2026-11-06).

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
- **The window must be 320x240** (2026-11-02): with no `obsidian-edition/settings.json` the
  Loader's default window is 960x720 (window_scale 3), and every pixel check (msgbox.sh,
  levelup.sh, panel.sh) then failed, so message boxes and CHOOSE A SPELL went unseen and the
  loops stalled. start.sh now sets `window_scale` 1, and pixmatch.py samples a bigger grab down
  to 320x240 first. Check with `xdotool getwindowgeometry`.
- **Two picture sizes**: `shot.sh` saves the game's own capture, 320x200; a window grab
  (`import -window`, which msgbox.sh, panel.sh and levelup.sh use for speed) is 320x**240**, the
  height stretched: a pixel at y in a capture is at y x 1.2 in a grab. Take a pixel's coordinates
  from the same kind of picture the check uses (panel.sh read the wrong row this way for a day).
- `sh shot.sh OUT.png`, then Read the picture: the game's own 320x200 capture. Look at the screen
  before any key that could do harm (Escape) and whenever a step didn't do what it should.
- `live.py` (exec'd by the Python tools) gives `g` (memory), `ds`, `gd` (dsloader's GameData);
  `CAMERA` (DS:1178h) and `POINTER` (DS:A133h). A script outside `playtest/` that execs it needs
  `sys.path.insert(0, PLAYTEST)` and `__file__` set to live.py's path first.
- **The game makes a region's map objects near the party** (2026-11-04): on arriving in the pens
  the weapon rack (object 2599, square 48,34) and many others were not among the map objects
  (`gd.things_of(obj)`, DS:66AEh), and so their items were not in memory either; walking south made
  more (1221, 1224, 1230...). Once made they stayed after the party walked off. To find an
  object's items, look it up by its object number when it is made, not by item type: type 6Ch is
  the weapon rack's and a coffin's (1574, at 75,43, holding a gem).
- **People's gear** (2026-11-05; **since 2026-11-06 `people.py` puts it on** as each person comes
  on the map, so `npcgear.py` shows it worn and held, as the game would after a first action): the
  game makes a person's items in its backpack list (+0Ch): Kurzak's, the Arena Guards', Scar's
  were all there, none worn or held, so none counted for AC or was fought with. Moved into the held list (`pickpocket.place(gd, creature, item, 3)`) a weapon is
  fought with by anyone (a Tohr-kreen with Headsman: "attacks Cermak with Headsman +2 (1d10+2)");
  armour in the worn list counts for anyone's AC. A creature that dies carrying something leaves
  a Dead Body (object 1101) with its things. **Correction (2026-11-06, logs/2026-11-06-npcs-equip.md):
  the game equips a person itself, on its first action in a fight**: Legcrusher then wore his
  Leather Inixhide +1 and held both clubs, an Arena Guard wore his leather and arrows and held his
  long sword and bow, and they attacked with them; Legcrusher's AC from behind was then 8, not 10.
  Before its first action (out of a fight, or killed first, as Kurzak by a backstab: target AC 10)
  everything is in the backpack list.
- **The arena's flags and numbers can't be set from outside** (2026-11-05): the pointers at
  DS:1352h and 1356h stay null in the arena even while a script waits on a message, so a poller
  never found them. To test a script's branch there, build a copy of the scripts with the test
  forced (edit the module, run `start.sh`, which writes `dos/GPLDATA.GFF`, then put the module
  back) and say so in the log.
- **Fighting a wave without killing it** (2026-11-05): `fightout.sh` puts every foe at 1 HP first;
  to see foes attack, pass the party's turns instead (Tab, Return, and the END menu for a member
  out of movement: section 4 rule 11), as in
  `logs/2026-11-05-champions.md`. A
  level-1 party loses to the champions.
- **Moving the party in memory** (2026-11-04, for a check where the way is shut): write each of map
  objects 0-3's x, y words at DS:669Dh + 32n (map units) and the camera at DS:1178h, then walk one
  step with `walkto.py`: the game redraws and makes the objects near the new place. Only for
  checks; the scripts see none of it.
- **AC in the inventory** (2026-11-02): the AC line is the game's own, worked out afresh from what
  is worn, but drawn one change behind: switch to another member's portrait and back (20,62 then
  20,20) before reading it. It follows a gladiator level raised in memory (`sheetedit.py`); the
  THAC0 line doesn't. Gerakis's armour: chest (173,70), arm (66,70), legs (173,128); the
  backpack's cells start at (195,26), (213,26), then down 18 a row.
- **The party's item lists** (2026-11-02): worn things (armour, a shield, rings, a cloak,
  ammunition) at the creature record's +08h, held weapons at +0Ah, the backpack at +0Ch; the
  inventory screen files by the type's kind, and the game's AC counts +08h only. `itemlists.py`
  shows where things are; swapping two list words
  in memory (the record's +08h/+0Ah/+0Ch) is a quick, undoable test of what a list does.
- **The parts of an AC** (2026-11-02): run the dice log with `--all` (kill its process by pid,
  then `python3 -u -m dsloader dicelog --all >> $WORK/dice.txt` from obsidian-edition): each AC the
  game works out gets a line "AC of X against Y: 8 (base 10, armour -1, DEX -1, other +0)".
- **Ability items and memory edits** (2026-11-02): an item's +0Fh is also the spell the game casts
  on the wearer as it is put on (FAh-FFh: STR to CHA, +0Eh the amount), kept as an effect (the
  item's byte 2 links it, for taking it off). Picking an item up or putting it down recounts the
  scores (opening the inventory doesn't); clearing the bytes of a worn item leaves its effect
  behind: reload. `itemedit.py MEMBER SLOT [slot= e= f=]`, `sheetedit.py MEMBER [levelN= flags|=]`
  and `party.py` (classes, flags, scores, items) are the tools.
- **A Shinobi for a test** (2026-11-05): `scrolltest.py shinobi` makes member 0 an 8th-level thief
  with the Shinobi kit in memory (class 17 at sheet +21h, level +24h, kit byte +43h = 3, flags 0400h).
  `give` adds the defilers' scrolls (`defilerscrolls.scroll`). Never save after. live.py's `gd` has
  no rules set, so `gd.kit_ids` reads []: use `kitpages.kits_of(gd.sheet(m))`.
- **Hearing the game** (2026-11-05): start.sh sends DOSBox's sound to a file when `PT_AUDIO` names
  one (`export PT_AUDIO=$WORK/audio.raw` before start.sh or loadsave.sh; else /dev/null): raw
  16-bit stereo at 44100 Hz, about 176 KB a second, real time. Note the file's size before and
  after an action, then `python3.13 soundmatch.py $PT_AUDIO A B clip.wav...` gives the loudest
  sample and how well each clip matches (r about 1.0 for the one played; 0.04 for another).
  `playsound.py N` has DSCLOG play sound N (its SOUND_REQ). The game plays nothing much on its
  own while the party stands about: a recording of minutes was silence but for a second at the
  start. The game's own 53 and 96 recorded at peaks near 2,800.
- **The game's table of sounds** (2026-11-05): at load segment + 3A98h, offset 08A2h, 6 bytes each:
  +1 the kind (5 a digital clip), +2 a far pointer to a 12-byte descriptor (+7 its BVOC). 0-130
  are digital, 131-180 another kind (4), past 180 other data: a BVOC numbered past 130 isn't
  played by its number (the mod's 140 and 141 were silent until DSCLOG lent itself entries 131 and
  132 for the call), and the game keeps the last clip loaded under a number (one lent entry for
  both sounds played the first again).
- **See-through figures** (2026-11-05): `ghostchk.py` shows DSCLOG's block (GHOST_SEG), GHOST_ON and
  the tables; `ghostchk.py 0` marks thing 0 (the leader) see-through and has the view drawn again,
  for a look without a fight or a spell. Outside a fight the party is one figure, the leader's;
  walking, it spreads into four. **The install's bytes turning up twice in the image meant two
  probes on one vector**, not chance: VEC_GHOST was given 62h, VEC_AC's, and every attack's AC went
  to the see-through probe (the dice log's "target AC 255" on every attack on the party, 2026-11-05;
  now 80h, and test_gamepatch checks the vectors are distinct). The live table of vectors
  (segment 0, 4 bytes each) shows which handler has each.
- **A big frame see-through** (2026-11-06, logs/2026-11-06-see-through-after-fix.md): `bigthings.py`
  lists the map's things with their pictures' most runs (near the pens' gate none past 164);
  `setpic.py THING PICTURE` draws a thing with another picture in memory (picture 459, a tuft of
  grass of 563 runs; put the old number back after), `ghostchk.py 0 1` marks things 0 and 1 (each
  call replaces the marks), and `pastblock.py save|cmp FILE` keeps and compares the 4 KB past
  GHOST's block. Past 192 runs only the frame's top is drawn see-through, by design.
- **Memory** (2026-11-06, logs/2026-11-06-memory-audit.md): `memaudit.py` lists every DOS block (the
game's, DSCLOG's, the overlay buffer, the see-through tables, the music buffer, free) and the heap;
`memsample.py LABEL` gives one line (free DOS memory after the game: 100,016 bytes on the map in the
pens, 131-138 KB while the inventory or USE screen is open); `dacwatch.py SECONDS` shows DSCLOG's
palette copy changing (every 30 s where the game cycles colours). The arena gate (the gap at
1816,440) asks nothing before Kurzak's call. `ghostwatch.py SECONDS` counts samples with GHOST_ON 0.
- **Who holds weapons** (2026-11-06, before `people.py`; with it, everyone's gear is on as they come
  on the map): `npcgear.py` lists every creature on the map with its worn, held
  and backpack items. In the pens (`pens-after-scar`) all 25 creatures besides the party carried
  everything in the backpack list, nothing worn or held: Kurzak (Shadowseeker, a long sword, his
  armour), the guards, the templars, Merzol, Kalzith. So the game's Look box, which lists held
  weapons, shows none for them; the champions (`champions.py` moves their gear to hand and body)
  are the only people whose weapons it lists before they have acted (see the correction above:
  the game equips everyone else on their first action in a fight).

## 3. Controls that work

- **Clicks**: `python3 click.py X Y [left|right|none]` in game pixels (320x200). DOSBox captures
  the mouse, so the tool moves it relatively until the game's own pointer reads X,Y. Plain
  `xdotool mousedown/up` clicks where the pointer already is (fine for dismissing a message).
- **Pointer cycle, as checked 2026-11-01**: arrow, sword, eye, arrow. **`pointer.py walk|look|attack`**
  reads the mode from memory (DS:11B8h: 1 the arrow, 4 the sword, 2 the eye) and right-clicks on bare
  floor until it is the one wanted (2026-11-07: right-clicks guessed from shots left the sword up,
  and one opened the USE screen on a party member). Over bare floor the sword and
  the eye show red with a bar (nothing to act on); over a door the eye is plain. Check the mode on a
  shot before walking (a walk tool clicking in eye mode looks at the floor and nothing moves).
- **Pointer mode**: a right-click on the map cycles it: the plain arrow (Walk, and use/talk on a
  thing), the sword (attack), the **eye (look: opens doors)**, back to the arrow. Over a wall a red
  "no" sign is drawn on top. **Right-click only on empty floor**: on a party member it opens the
  USE screen (Escape closes it). Only walkable ground takes a walking click (the user,
  2026-11-01): a click on a wall does nothing. Check the pointer in a
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
  screen or menu that is open, and **opens EXIT: SAVE GAME? when nothing is**: a click after that can quit
  to DOS. Press Escape only with a menu or screen showing.
- **Ending a turn by hand**: a click exactly ON the active member's figure opens END <NAME>'S
  MOVE (GUARD / WAIT / END TURN); a click beside it walks it a step instead. In that menu press
  **E** for END TURN: when Return opened it (no Move left), clicks on its rows didn't register
  (2026-11-01). E with no menu up opens the Effects screen (section 4 rule 11).
- **Loose `xdotool` commands need `DISPLAY=:55`** (`export DISPLAY=:55` first): the kit's tools
  set it, a command typed on its own doesn't ("Can't open display").
- **In a fight the view barely drags**: two drags of 150 moved the camera from (1728, 768) to
  (1712, 832); the party's figures stayed on the screen (2026-11-07). Drag out of a fight to put a
  figure off the view.
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
  `CHARSAVE.GFF` and `DARKSAVE.GFF` written at the same time; keep all three (`saves/README.md`).
- **The save name field keeps the slot's old name**: typing goes in front of it (KURZAK DOORPENS),
  and Backspace from the start does nothing: press End, then Backspace enough times, then type.
- **Look needs line of sight**: "NO LINE OF SIGHT" from a party round a wall corner, and still
  from beside the pens' gold post at (1528, 456) (whatever part of it was clicked, 2026-11-01): that
  post may not be a door at all.
- **Opening a door (the user, 2026-11-01): the look pointer.** Cycle the pointer with right-clicks
  to the look cursor and click the door; then, with the walk arrow, click on the far side of the
  open door to move past it. The walk arrow on a door, or on the floor beyond a closed one, does
  nothing (that was the stall at Kurzak's last stop).
- **`doorpath.py TC TR`**: the shortest way to a square through closed doors too, listing the doors
  it crosses and its turns; `BLOCK="C,R C,R"` rules out squares (a locked door). **route.py** skips
  squares a figure stands on (96: a party member there takes the click and nobody walks), drops a
  square whose click moved nobody, and brings the view to the way ahead when nothing nearer the
  goal is on screen (the view on the leader can hide the way, as the hall south of Kurzak's stop).
- **Doors**: `python3 doors.py` lists the closed doors and gates on the edge of the area the party
  can reach (live grid 192+ where the file's grid has a doorway), with their map positions.
  Clicking a door square, or the floor beyond it, did nothing for the pens' doors near Kurzak's
  last stop (95,28; 2026-11-01).
- **Loading**: the title (two clicks), then the main menu: START GAME, CREATE CHARACTERS, LOAD
  SAVED GAME (170, 109), EXIT TO DOS; the LOAD screen lists the slots (click one at 100, 46), then
  LOAD (253, 46). `loadsave.sh` does it.
- **Talk menus** (WHAT DO YOU SAY?): number keys don't choose; click the line. The list scrolls:
  its down arrow is at (311, 187), and the last visible line is about y 189. The dice log lists
  every choice with a number, which helps find the one wanted.
- **The inventory screen's places** (2026-11-02, from hovering: the name shows in the bar at the
  bottom; the ones used): ammo (66,26), missile (66,48), arm (66,70), right hand (66,92); chest
  (173,70), left hand (173,92), legs (173,128); the backpack fills down its first column first: (195,26),
  (195,44), (195,62), (195,80)... (rows 18 apart; 48 and 70 are between cells), then (213,26)... Click an item to pick it up, click a place to put it;
  armour can't be put on in a fight ("CANNOT USE THIS ITEM"); a wrong place says "ILLEGAL
  PLACEMENT" and keeps it on the pointer.
- **A spell's description box** (2026-11-02): U, a member's portrait (Cermak 66,108), then
  right-click a spell's icon (from 177,59, about 14 apart). Seven lines fill the box: an eighth
  spills over its edge, so check a lengthened text in the game. A new wizard spell is known by a
  bit of the sheet's +45h (`game.NEW_KNOWN`: Erdlu Claw 20h), which a scratch write can set for a
  shot (the sheet from SHEETS_PTR and the creature's +4 index). Doc panels like
  `new-spells.png` are crops of `shot.sh`'s 320x200 picture scaled 2.09 (304x188 each).
- **Looting a body** (the user, 2026-11-05): the **look pointer** on the body's picture; the plain
  eye (not the red one) shows when it is over it. A body's map position isn't where its picture
  is drawn when others lie on it: move the pointer over the picture, beside the party (a body far
  off opened nothing). A window of cells opens: a click on an item puts it on the pointer (the
  cells light yellow), a click on a party member's figure gives it to that member. A party
  member standing on the heap takes the click instead (the Effects screen opened): walk off first.
- **Reading a scroll** (2026-11-05): right-click it in the backpack to open its item box, which shows
  the price, "Scroll" and the spell's icon. The box opens beside the item's row (row 26: icon at
  288,20; row 44: 289,33; rows 62 and 70: 289,47; row 80: 290,65), so take a shot and read where the
  icon is. Then point at the icon (`click.py X Y none`), wait, and press slowly (`xdotool mousedown 1`,
  0.15 s, `mouseup 1`): click.py's quick click there was lost about half the time. The result is on
  the line under the paper doll and in the dice log ("X reads the scroll of Y: ..."). The dice log
  doesn't repeat a `Message:` line the same as the last one, so look for the "reads the scroll" line.
  The screen can draw the backpack one change behind: close the inventory and open it again (Escape, I)
  before believing a cell is empty.
- **route.py won't walk through a figure** (2026-11-05): with someone standing at (99, 31), in
  front of Kurzak's entryway (99, 33-34, open), it found no way south from his stop and gave up;
  the live grid showed the doorway clear. Walk round with clicks, or wait for him to move.
- **The inventory panel's picture for the docs** (2026-11-05): I opens the inventory; the panel is
  `shot.sh`'s x 230-319, y 0-199, scaled 2x (`convert -crop 90x200+230+0 +repage -scale 200%`).
  A class can be tried in memory: the sheet's class byte (`SHEET_CLASSES`, 13 a ranger) and its
  flags (0200h a ranger, 0040h a gladiator); never save after.
- **The combat log panel**: `sh panel.sh hide|show` checks the panel's pixel before pressing L
  (L alone toggles, and can leave it the wrong way round).
- **The combat log panel in tests** (2026-11-06): `panel.sh` reads "hidden" when the panel is
  expanded (its pixel check is for the small panel): look at a shot, and press L yourself. The
  expanded panel's filter chips are at y 87 (All 148, Party about 175); a filter chosen stays
  (Party leaves out the foes' attacks). A party member's figure under the panel can't be clicked
  (its END menu): hide the panel first. **Picking a pocket:** U, the thief's portrait (Cilla
  108,108), the purse under the spell counts (157,145, a slow press), then the talk pointer on the
  person. `orderwatch.py`-style logging (fight_on and the dice log every 10 ms) showed a blow from
  outside a fight is struck before the fight begins.

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
   out of a fight (U, the caster's portrait, e.g. Cermak 66,108) the target is a portrait on the
   same screen: the icon (177,59 the first), then the target's portrait (Gerakis 66,62), and the
   dice log says it ("Cermak gives Enlarged to Gerakis"); no name floats, the screen covers the
   map (2026-11-07);
   check the dice log for the spell's line before going on. If none appears, look at the screen:
   usually a menu left open, the wrong spell page, or no Move or slots left. Try Tab + Return at
   the targeting step before clicking a figure.
7. **Shots**: unreliable. Enter is a left click on the enemy: with Move left the member walks up
   and fights hand to hand; with Move 0 the END menu opens; in Attack mode a far target showed the
   red "can't" pointer and the turn passed. A shot test needs a clear line, a target in range, and
   a readied missile weapon with ammunition in the missile slot.
8. **Never `pkill -f` or `pgrep -f | kill` a pattern your own command line contains**: it kills
   the shell running it (exit 144, twice on 2026-11-01, the second time with this rule already
   written: run the kill as its own command, by pid, and nothing else in it). Kill by pid, found by a pattern your command line can't match (`pgrep -f "sh [l]eavearena.sh"`), then `kill PID` in a command of its own. And
   stopping a background task can leave its children running: check with pgrep afterwards.
9. **Never cut steps out of a bigger script with sed**: its header may restart the whole game.
   Use the small tools.
10. **Every step gets its own `timeout`**; long runs go in the background and are followed through
   the watchdog's Monitor, not by sleeping.
11. **Passing one member's turn** (2026-11-05): `memberpos.py N` gives its figure on the screen;
   a click there opens its END menu, and E in that menu ends the turn. E with no menu up opens
   the Effects screen, and closing that (Escape) left the view at the map's corner (camera 0,0):
   drag it back with `scroll.py` (about 216 x 72 map units for each -216 -96 drag). A member off
   the screen (memberpos gives y below 0) can't be clicked: drag the view first. Tab + Return
   didn't end Gerakis's turn (his weapons' reach); the END menu does.
12. **"target AC" in the dice log** is the AC the game uses for an attack: check it against
   `gd.counted_ac` (`acs.py`) whenever the foes seem to hit too often. A test fight that
   goes badly: `healparty.py` puts the party's hit points back in memory (never save after).

**More on fights:**

- **Testing Psionic Blast without a blaster** (2026-11-04): find DSCLOG's header in memory
  (`b'DSCLOGva'`, 16-aligned; 0xC91B0 in that run), write a member's kept hit points at +1814
  (a word per combatant 0-3) and the member's HP (creature record +0) to -9, so any blow would
  kill by the game's rule (damage at HP + 10); pass turns until it's hit: it goes to 0 HP, not
  dead, and the fight's end gives the hit points back ("shakes off Psionic Blast's imagined
  wounds"). CON 20+ regeneration can wake it first (Gerakis did).
- **Getting a party member attacked**: a scratch loop that passes the party's turns (Tab +
  Return, then the END menu if the turn stays: section 4 rule 11) and stops once the dice log has N more "attacks NAME"
  lines; between waves click the messages and walk about in the arena (staying brings more
  fights). It can lose the whole party ("YOUR PARTY HAS BEEN DEFEATED"): have a save to go back to.
- **Level-ups in fights**: PICK A PSIONIC POWER (a psionicist's level) isn't levelup.sh's: click a
  red power's icon (about 158, 62), then FINISHED (112, 139).
- **The see-through figures in a fight** (2026-11-05/06, logs/2026-11-05-fight-test.md): seen from a
  real hide (Cilla, thief level raised to 12 in memory: hides at 95) and a real Invisibility. The
  pale bits behind a walking figure are the mod's dust (dust.py), not a smear: solid figures leave
  them too, and a full redraw clears them; an END menu left up keeps them on screen. Pace:
  `walktime.py N X Y [DIR]` (about 0.07 s a step, see-through or not). Hidden, Tab + Return walks
  the thief up and backstabs; it is drawn solid from the blow on.
- **A hidden walk to Move 0, and the turn's end** (2026-11-06, logs/2026-11-06-solid-frames-turn-end.md):
  `walkprobe.py N X Y DIR [SECS]` clicks, then keeps a window grab with N's position, whose turn and
  DSCLOG's STEALTH word (header +204) as often as it can (about 50 a second). **Move running out
  doesn't pass the turn**: the walk stops and END <NAME>'S MOVE opens and waits. After E, STEALTH
  went to 0 within one Loader pass, but the figure kept its see-through picture through the
  enemies' turns (about 1.4 s) and was drawn solid when a party member's turn began: the view is
  drawn again from the map's main loop, which doesn't run in the enemies' turns. The 2026-11-05
  "two solid frames" weren't seen in 38 more hidden steps (beside Gerakis and K'ratchek too):
  closed as not reproducible after the vector fix. **Since GHOST_UNION** (logs/2026-11-06-solid-at-turn-end.md)
  the figure is solid about 0.1 s after the hiding ends, in the next enemy's turn, if that enemy
  steps or swings; one that does nothing redraws nothing, and the old wait applies. A turn passed
  can come straight back (her END TURN was the round's last but one; round 2 opened with her and
  a new hide roll): check the round order in the dice log.
- **memberpos.py can miss** a figure in a crowd: about 12 pixels higher
  opened the END menu; check a shot first.

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
- **The first bout can fail to start** (2026-11-02): topartyfight.sh ended "NO FIGHT" at
  (488, 232), and 60-odd more clicks south and walks between (488, 232) and (488, 264) (the bone
  wall stops the party at 264) over several game minutes didn't start it. The bout is GPL 2's
  entry at 1 (case gnum 3 = 1, "Step forward" sets it), run by MAS 42's code-111 trigger on
  object 2059 at (498, 341), beyond the bone wall, and it waits on flag 5 (MAS 42 sets it on
  loading); the flags can't be read in the arena. Earlier runs got in from the same place; why
  not this one is open. Next time: restart (`start.sh`) and try again before digging.
- **The first bout started at once** in two later fresh games on 2026-11-02 (topartyfight.sh
  "FIGHT"), so the failure below is intermittent.
- **Resting** (the user, 2026-11-05): the fire room off the east passage, its door at square
  (115, 53), map (1848, 856), opened with the look pointer; in it a small fire ring among
  haystacks (map about 1931, 856): the **look pointer on the ring** rests ("THE PARTY RESTS",
  hit points full). After two or three rests and a step, Kurzak calls ("Gerakis! Get up here!
  It's your turn in the arena!"). **Answer the call quickly**: twice the party walked to Kurzak's
  stop and on toward the gate (1816, 408) and he ran out of patience ("That's it! Time's run
  out!"), then the alarm and a fight with every guard. **The alarm fight on purpose**:
  `toalarm.sh` (loads `pens-after-scar`, records the sound, raises Cilla's thief level in memory,
  walks to the fire room), then `restalarm.sh` (rests, then waits Kurzak out); about 15 minutes in
  all, in the background with a Monitor. **toalarm.sh can stop short at (1832, 856)**, outside the
fire room (2026-11-06: its last walkto said NO PATH FROM HERE with the door open). **A look click on
an open door closes it** (the closed door is the gold pole; the user caught a close taken for an
open): check a shot before clicking a door. With the door open, the walk arrow on the room's floor
(screen 240,160, camera 1656,720) took the party in. **The pointer must be the eye before restalarm.sh**: on
  2026-11-06 it was the sword, no rest came ("rests: 0") and the click on the ring fell on Cilla
  (Gerakis attacked her out of a fight). `toarena.sh` answers the call instead (up to the arena).
- **Into the arena from the pens** (the user, 2026-11-05): after the call, Kurzak's entryway
  (`route.py 1592 584`), his stop (1592, 520), north to (1592, 440), east along the corridor at
  y 408 (walkto in two steps: further north, y 376, counts as escaping and sets off the alarm)
  to (1816, 408), then a click into the gap in the brick wall just south of it (1816, 440):
  "Enter the arena?" **Y**. In the arena: south from the gate (488, 200) with clicks (each passes
  time), through the bone wall's gap (504, 360), and on south onto the stone platform until the
  bone gate closes behind the party (488, 408-424): then the Announcer and the bout.
- **Staying in the arena after "Go back to the pens"** for a few minutes brings "If you don't want
  to return to the pens, then you must want another fight!" and a wave.
- **Setting the arena's visit count**: in the pens the game's numbers have a place in memory;
  number 12 is the count (4: the next trip is Scar's; 5 and up the everyday speech, or the
  champions' after Scar's death in the arena). Write it at the far pointer DS:1356h + 2 x 12.
- **The pens' main door** (objects 2145-2146 at 1571-1611, 559: the entryway Kurzak opens) has
  the "Take me to the Arena! I want a fight!" menu (137:14CEh), but open it answers nothing to
  the look pointer. **Resting** is at a fire ring (the game's rest, 8066Dh); the east hall's
  object 2264 (1908, 675) is a haystack (137:F5h), not the fire ring.
- **Kalzith** (2026-11-05): from `pens-after-scar`, walkto (1816,408), (1704,408), (1592,440), then
  clicks at screen (200,178) (camera 1392,384) take the party through Kurzak's entryway past him
  (route.py wouldn't: he stands in front of it); then `route.py 1560 880` reaches Kalzith's pen
  (him at 1576,888, thing 220). The arrow's click on him does nothing (the party stands on him):
  the look pointer (two right-clicks on bare floor) on him opens the Look box (KALZITH, LEVEL 5),
  and its first button (163,150) talks. Replies are lines from y 162, 8 apart; "We mean no harm",
  then click the box twice, then "Show us what you have" opens his shop.

**The arena (region 2Ah)**, as of 2026-11-01:
- Several waves (Sligs and a Screamer Beetle; Sand Howlers and a Tohr-kreen; ...), then "The
  crowd is awed...", the Announcer, and "Yell something back at the Announcer?" (N), then
  "Attention gladiators: Go back to the pens to heal your wounds." The game clock barely moves
  while the party stands; if it doesn't leave in time: "The patience of the citizens of Draj is
  not infinite. Since you will not leave, you must fight!"
- **The way out** (an open problem until the fourth run, below: `leavearena.sh`). MAS 42's move triggers: squares 5-7 at rows 30-32 run script 3
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
  (The user's advice, 2026-11-01: if the party stops at the stone wall, click inside the wall's
  boundary; don't stay outside the walls, as more monsters are sent.)

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
- **Into the pens (2026-11-01, the user)**: Kurzak's "door" is the entryway south of where he
  stops, squares (99, 33-34), map (1592, 536-551), open once he has led the party there; through it
  is the east-west hall (rows 35-37, columns 90-115), the cells south of it, and "the east hall"
  (the campfire) down the passage at columns 112-114. `route.py 1592 584` walks through.
- **The corridor gate (81, 20-21) is locked**: the look pointer on the gold post opens a look box
  titled "Door" whose only live button is the third (USE, 116,137): "The door is locked. It
  appears quite sturdy." The box message then has to be clicked away (boxclick.sh), and the
  pointer is left on the eye: right-click on to the arrow before walking.
- **The other way west** (`doorpath.py`, with BLOCK="81,20 81,21"): down the east passage to the
  door at (113, 90) (map 1816, 1448; `route.py 1816 1400` stands beside it), west along the bottom
  corridor (rows 91-95) through the door at (93, 94), north up columns 34-35 to the south hall
  (rows 66-70), and north at columns 17-20 to the stalker pen's anteroom (its door 16, 54-56).
  On the way, two slaves whisper "Is it time to break out yet?" / "Shh, not yet!".
- **Opening the stalker pen's door sets off the alarm** (the user, 2026-11-01): plan for it (the guards come)
  or find another way to the button.
- On the recompiled program (2026-11-01) the same: the look pointer on the doorway's drawing
  (square 95,27, above the door square) opens the mod's Look box "Door" (INFO only); the arrow,
  the look click and the sword on the door square do nothing and log nothing; the sword on
  Kurzak (object 29, then at square 99,31) does nothing either: no fight starts from a click on a
  friendly figure.
- Button 1281 at (139, 748), the pen's north wall: used from within 4 squares (137:1AE8h, else
  "is too far away to press the button") it sets flag 518 and "hears a click as the secret door to
  the west opens". (Button 1280 at 1335,798 opens another door, 81-82,53-54, only once the monster
  266 at 1264,848 is gone or flag 317 is set; otherwise "presses the button, but nothing happens".)
- The grate, object 1234 at (46, 86), the far northwest; walking onto squares 3-4, 5-6 (map
  48-79, 80-111) runs its menu (137:29Bh): Pick the lock / Rip it open / Hack the lock off.
- **The door at (113, 90) was locked** on 2026-11-04 (look box "Door", its third button: "The door
  is locked. It appears quite sturdy."), with the party straight from the arena and Kurzak
  followed to his stop: the way west by the bottom corridor isn't always open.
- **The weapon rack** (Thornwall's, object 2599) is at square (48, 34), map (779, 550), in the room
  west of the door at (65, 38-39); from (52, 36) beside it the game has made it. Its contents (map
  object 478 on 2026-11-04): Polearm, Quarterstaff, Polearm, Axe, with Thornwall first once
  Semyon has told of the shipment (flags 756, then 757).
- The pens' cell doors (2141-2164) have USE (script 138) and ATTACK handlers ("This door is too
  strong to bash open" for the cells').

- **Pehtucl's chest** (2026-11-07, logs/2026-11-07-pehtucls-chest.md, logs/2026-11-07-review-fixes.md):
  `saves/pens-new-chest` is a new game with the chest's USE command (older saves lack it), but its
  chest was made before the shut type: run `shut.py` after loading, or the game opens it whatever
  the script says. To reach it: `teleport.py 200 1432 40 1322`, walkto (216, 1440), then (184, 1400),
  a square west of it (from (120, 1464) the script says "You must be next to the chest"; standing on
  it, a figure takes the click); `pointer.py look`, a slow press on it (163, 70), the look box's third
  button (236, 101) (`chestuse.sh`). `thief.py N LEVEL` / `thief.py N off` makes a thief in memory. The chest's look box: first button closes,
  second **moves the chest**, third uses it. A thief in memory needs the class byte and level and the
  sheet's flags 400h (`sheetedit.py N flags|=0x400`). The game's trap objects: +0Fh is the trap's
  descriptor (d6, reach, damage kind), DSUN.EXE 80A11h. A new game to the pens in the background:
  `start.sh`, `topartyfight.sh`, `arenawaves.sh`, `leavearena.sh` (about 30 minutes).

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
