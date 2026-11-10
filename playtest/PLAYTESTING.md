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
In this guide `$WORK` is that work folder: `env.sh` sets `WORK` from `PLAYTEST_WORK` for the
tools, but a shell you type in doesn't have it, so type `$PLAYTEST_WORK` there.

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
   `playtest/saves/`; [its README](saves/README.md) lists them all (`pens-after-arena`, the slave
   pens just after the arena, is the usual start). None came with the game and none were on the
   Drive (2026-11-01). **Save at every milestone** (below) and add the save to `playtest/saves/`
   with a line in its README, then commit: replaying the arena took most of a day.

## 1. Setting up

1. Packages: `dosbox Xvfb xdotool imagemagick innoextract poppler-utils nasm python3-tk`, and
   `pip install capstone unicorn` (check with `command -v`; the environment's setup script
   installs most of them, below).
2. The game: `sh setup_game.sh` (the GOG installer from the user's Google Drive, file id in the
   script, extracted with innoextract into `$DS_GAME`).
   **A walkthrough** (2026-11-09, the user's): `sh setup_guide.sh` fetches kibbitz's GameFAQs guide
   from the same Drive folder into `$WORK/guide/kibbitz.html` and its text, `kibbitz.txt`, to
   search (`grep -n -i caravan`): where things are, who sells what, quest steps and talk choices
   ("2-4-2"), region by region. Someone else's work: never commit it (the repository is public).
   Weigh it with the game's data: it is one player's account.
   Wake of the Ravager, the sequel, for comparing (its code, data and README; nothing in the kit
   plays it): `sh setup_ravager.sh`, the GOG installer from the same Drive folder, into
   `$WORK/rav`. Its DSUN.EXE is laid out otherwise: the creature/sheet records 42h bytes at the far
   pointer DS:19C5h, a class's level at +1Eh, its class at +1Bh; the XP table is RESOURCE.GFF's
   DATA 1000 (8 rows of 20 words, in hundreds, looked up by `lcall 5C8:20` with 3E8h); much of the
   code is in overlays, so a far call's segment isn't a place in the file. Its level-up (95860h on)
   caps XP at the table's entry 3 levels past each class's own, then raises a class under 15
   (2026-11-08: no race limits, whatever its README says).
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
   Compare code, not the whole image: the variables in it differ once the game runs (1,235 bytes
   did, 2026-11-08); take a routine's offset from a symbol map (`[map all FILE]` in a scratch copy
   of the source, as framerate.py's `symbols()`) and compare 40 bytes there. Since 2026-11-08 the
   vectors are set from a table in the install code (`all_vectors`: the vector byte, then its
   handler's offset): read it from the EXE and check each vector in segment 0 against it. **The
   far block** (`far_seg`, the header's +142: FFFFh, the HMA, so linear FFFF0h + offset) now holds
   DAC (+238's offset), RING_TAB (+246), RED (+248), LIGHT (+236), the dust's walked counts, its
   puffs and DARK: a tool reading those at the helper's segment reads stale bytes (`dacwatch.py`
   and `ghostwatch.py` were changed for it). **The tail** (2026-11-09: `tail_seg`, the header's
   +1834, the paragraph after the image, +1836 paragraphs on from the helper's segment) holds the
   labels' slots (+1838's offset), TICKS (+356's), the item types and the companion's names; the
   header's +144 is now where ALL_VECTORS is in the image. **`buildcheck.py`** does the whole
   check (routines' bytes against the EXE, every vector at its handler, the tail's segment and
   its data) in one go; it takes routine names to compare others.
   **Comparing two builds' memory**: put the old `DSCLOG.EXE` in `obsidian-edition/dos/` for one
   `loadsave.sh`, run `memaudit.py`, then put the new one back and `cmp` it with a fresh build;
   don't do it while the unit tests run (they read `dos/DSCLOG.EXE`). A failing
   tests/test_dsclog.py is slow (each failing emulation runs to its count): 323 tests took 7 s
   passing and over 20 minutes failing (2026-11-08), so a test run that drags means failures, not
   a slow machine.
   `dec.py` stops with "unknown term" when LO falls inside a command: start it at a command
   (or decode the whole script with `dsloader.gpl.load_scripts` and `decode`). Every script in
   the built copy should decode (2026-11-05: eleven didn't, and a later change gave up on one).
5. **The watchdog**: `sh guard_start.sh`, then a Monitor on `$WORK/guard.log` (grep
   `STUCK|GONE`, with `tail -n0 -F` so old lines don't fire) for the whole test. Stop it (`kill
   $(cat $WORK/guard.pid)`) before going idle. The log keeps earlier runs' lines (2026-11-07: GONE
   lines from a watchdog started without a display, two hours before): read the times before
   believing one.
6. **DOSBox dies when the session sits idle** (the container's processes are reclaimed). After
   any pause (waiting on the user), check `pgrep -x dosbox` before the next step; if it's gone,
   start again from `start.sh`. Don't leave a test half-done across a pause expecting it to be
   there.
7. **After a worker restart Xvfb is gone too**, and start.sh in the background didn't restart it
   (every xdotool call: "Can't open display"). `pgrep -a Xvfb`; else `setsid nohup Xvfb :55 -screen
   0 1024x768x24 &` by hand.

**The environment's setup script (2026-11-06):** the user's "Google Drive" cloud environment now
installs `innoextract nasm dosbox xdotool`, `pip install capstone unicorn`, and runs
`setup_game.sh` into `/tmp/playtest/inst` (and, from 2026-11-08, `setup_ravager.sh` into
`/tmp/playtest/rav`, about 12 s) when the container is built fresh, with
`drive.usercontent.google.com` and `drive.google.com` already allowed. So a new session should
only need `export PLAYTEST_WORK=/tmp/playtest`, then `loadsave.sh` (check `command -v dosbox` and
`$PLAYTEST_WORK/inst/DSUN.EXE` first; if missing, do it by hand, as below). Checked by hand
that day: the download went through with no environment change, `loadsave.sh pens-after-scar`
loaded (region 29h, leader 1816,440, window 320x240, dice log attached). A worker restart of
the session killed DOSBox as an idle pause does. With the game's files the unit tests run
more: `DSUN_GPLDATA=$G/GPLDATA.GFF DSUN_OBJECTS=$G/SEGOBJEX.GFF DSUN_RESOURCE=$G/RESOURCE.GFF`
(`G=$PLAYTEST_WORK/inst`). With them set, `python3` skips 9, all for want of tkinter; without
them, 24 (2026-11-07). `/usr/bin/python3.12` has tkinter.

**A fresh container by hand (2026-11-06)**, if the setup script didn't run: `apt-get update`, then
install `dosbox xdotool innoextract nasm` (`Xvfb`, ImageMagick, poppler were there). The Drive
installer download is blocked by the default network policy (403 on `drive.usercontent.google.com`):
allow that host with update_environment, wait ~20 s, then `setup_game.sh` works (22 MB). `start.sh`
shows the window at 640x400 until a save is loaded; after `loadsave.sh` it is 320x240.

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
- **Doors at Kurzak's stop** (2026-11-01): the look pointer on the doorway's drawing (square
  95,27, above the door square) opens the mod's Look box "Door" (INFO only); the arrow, the look
  click and the sword on the door square do nothing and log nothing; the sword on Kurzak (object
  29, then at square 99,31) does nothing either: no fight starts from a click on a friendly
  figure.

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
- **People's gear** (logs/2026-11-06-npcs-equip.md): the game makes a person's items in its
  backpack list (+0Ch) and puts them on itself at that person's first action in a fight (weapons
  held, armour worn: Legcrusher's Leather Inixhide +1 and both clubs, an Arena Guard's leather,
  arrows, long sword and bow, and his AC from behind 8, not 10). Before that, out of a fight or
  killed first (Kurzak by a backstab: target AC 10), all of it was in the pack, and the game's
  Look box, which lists held weapons, showed none. **Since 2026-11-06 `people.py` puts it on as
  each person comes on the map**: `npcgear.py` lists every creature on the map with its worn, held
  and backpack items. Moved into the held list (`pickpocket.place(gd, creature, item, 3)`) a weapon
  is fought with by anyone (a Tohr-kreen with Headsman: "attacks Cermak with Headsman +2
  (1d10+2)"); armour in the worn list counts for anyone's AC. A creature that dies carrying
  something leaves a Dead Body (object 1101) with its things.
- **Setting the arena's visit count**: in the pens the game's numbers have a place in memory;
  number 12 is the count (4: the next trip is Scar's; 5 and up the everyday speech, or the
  champions' after Scar's death in the arena). Write it at the far pointer DS:1356h + 2 x 12.
- **The arena's flags and numbers can't be set from outside** (2026-11-05): the pointers at
  DS:1352h and 1356h stay null in the arena even while a script waits on a message, so a poller
  never found them. To test a script's branch there, build a copy of the scripts with the test
  forced (edit the module, run `start.sh`, which writes `dos/GPLDATA.GFF`, then put the module
  back) and say so in the log.
- **Moving the party in memory** (2026-11-04, for a check where the way is shut): `teleport.py X Y
  CX CY` writes each of map objects 0-3's x, y words at DS:669Dh + 32n (map units) and the camera at
  DS:1178h; then walk one step with `walkto.py`: the game redraws and makes the objects near the new
  place. Only for checks; the scripts see none of it.
- **AC in the inventory** (2026-11-02): the AC line is the game's own, worked out afresh from what
  is worn, but drawn one change behind: switch to another member's portrait and back (20,62 then
  20,20) before reading it. It follows a gladiator level raised in memory (`sheetedit.py`); the
  THAC0 line doesn't. Gerakis's armour: chest (173,70), arm (66,70), legs (173,128); the
  backpack's cells: section 3's inventory places.
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
  **Comparing loudness** (2026-11-09, logs/2026-11-09-sounds-louder.md): `playsound.py N` for each sound
  with 3 s between, the raw file's size noted round each, then the peak and the loudest 400 ms RMS of
  each stretch (numpy over the memmap): the game's fight sounds peak about 2,960, RMS -27 to -31 dBFS.
  A sound's descriptor +6 is its priority: the game skips one lower than the sound playing.
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
- **`ghostclear.py [TRIALS]`** (2026-11-07): at each enemy turn's start, Cermak marked see-through with
  GH_CHANGED set, the byte and the turn read every 20 ms: whether GHOST_UNION cleared it within that
  turn. **`rec.py [FIRST LAST]`**: creatures' combat records in hex, to find a field.
- **The game's free things** (2026-11-07): `thingsfree.py LABEL` gives one line: the free list's
  length (of the 200, things 320-519), the count out (DS:4C48h), and the item lists the people on
  the map hold. The pens: 143 free after loading, 131 in the alarm fight; the arena on arrival 191
  (the pens' all freed). `arenatrip.sh` loads `pens-after-scar` (through `toalarm.sh`), rests in the
  fire room till Kurzak calls, and takes the party to the arena, counting the things on the way.
- **A creature's level / hit dice** (2026-11-08, logs/2026-11-08-touch-level-and-hd.md): every
  creature has a 47h-byte sheet (`gd.sheet(creature)`; race +18h, classes +21h, levels +24h). The game's
  level of a combatant (508h:2Ah, 5E85Fh) is +24h for a human, else the best level of a class that is
  set, so a monster with no class (elementals, slaads, Sand Howler, Rampager...) counts as 0 though its
  hit dice are at +24h. The game's own monster sheets are the RDFF chunks of SEGOBJEX.GFF (record type 4,
  `dataitems.records`). The undead (race 9) all have a class. With "Spells and psionics as the manual describes them" a classless
  creature's saves count its hit dice as its level (DSCLOG's HD_SAVE_SITE in the save modifiers only;
  checked 2026-11-08, logs/2026-11-08-hd-spells.md).
- **Memory after the 2026-11-08 memory pass** (logs/2026-11-08-memory-pass.md): `memaudit.py` on
  the map in the pens: the helper's block 62,208 bytes with its PSP, the overlay buffer 32,992,
  the see-through tables 14,160, the music buffer 12,016, 37,392 free in one piece. **View
  Character** (I, then the inventory's bottom icons; the Effects screen is the one at 243,187, View
  Character at 52,171; the portraits there at 65/112, 55/110) shows each member's EXP and the next
  level's need with its class letter ("EXP:4487 (5000 Pr)"): a quick check of the XP tables
  (AD&D's when the header's rules_hi, +270, has bit 8). `framerate.py`'s walk clicks at y 104: from
  `fountain-user` after its fight they land in the fountain and nobody walks (0 map units/s).
- **Memory after the second memory pass** (2026-11-09, logs/2026-11-09-memory-pass-2.md): the
  helper's block 62,640 bytes with its PSP and tail (the build before: 63,760), 288 bytes free
  between it and the overlay buffer (704), 37,392 free in one piece (35,856); DOS memory free after
  the game 97 KB, as before. The old build for a comparison: `git show HEAD:obsidian-edition/dos/
  DSCLOG.EXE` into a scratch file, copied into `dos/` for one `loadsave.sh`, then the new one put
  back (`cmp` it with a fresh build). A quick look at the far block and the tail in a running game:
  LIGHT at the header's +236 (an offset in the far block), the puffs 256 after it and DARK 288 after
  those; TICKS at `tail_seg` x 16 + the +356 offset, the labels' slots at +1838's.
- **Memory** (2026-11-06, logs/2026-11-06-memory-audit.md): `memaudit.py` lists every DOS block (the
  game's, DSCLOG's, the overlay buffer, the see-through tables, the music buffer, free) and the
  heap; `memsample.py LABEL` gives one line (free DOS memory after the game: 100,016 bytes on the
  map in the pens, 131-138 KB while the inventory or USE screen is open); `dacwatch.py SECONDS`
  shows DSCLOG's palette copy changing (every 30 s where the game cycles colours). `ghostwatch.py
  SECONDS` counts samples with GHOST_ON 0.

### Frame rate and cycles (framerate.py)

`python3 framerate.py 20` walks the party back and forth (screen 40,104 to 280,104, a click every
3 s) for 20 s, out of a fight, and prints: the frames shown a second (DSCLOG's flip_count); those
steady pace left undrawn (pace_skipped); the steps run and lost (pace_ran, pace_lost: steady pace on
only); these found from a symbol map of the helper as built; the main loop's passes; the BIOS
clock and the game's clock (96 a second) against real time; the leader's map units a second
**while walking** (the waits at a target left out: before 2026-11-08 the tool averaged over the
whole run, so every setting read 64 to 66); and DOSBox's CPU. `PT_CYCLES=N sh start.sh` (or before
loadsave.sh) sets DOSBox's cycles; settings are changed with `launch.save_settings` before loading
(the scripts were /tmp/playtest/matrix*.sh: see the log of 2026-11-08).

How the game paces walking: its timer (DSUN.EXE seg 1DF3:29E8h) sets DS:1F7Eh at each tick of
the game's clock (DS:11D6h, 96 a second); the step (1DF3:26DCh) runs only with it set and clears
it. A tick passed while a frame draws is a step lost.

Results, pens-after-arena, the whole party walking, 2026-11-08. The old steady pace (schedule of
70 frames a second), walking speed not measured right:

| Cycles, settings | Shown/s | Undrawn/s | DOSBox CPU |
|---|---|---|---|
| 20000, all on | 6.1 | 16.9 | 21% |
| 35000, all on | 8.3 | 11.9 | 30% |
| 50000, all on | 10.6 | 8.0 | 45% |
| 65000, all on | 16.6 | 1.3 | 48% |
| 80000, all on | 17.4 | 0.3 | 57% |
| 100000, all on | 17.7 | 0 | 69% |
| 20000, steady pace off, the rest on | 17.0 | 0 | 21% |

The new steady pace (steps lost against an allowance of 1.5 ticks a frame):

| Cycles, settings | Shown/s | Undrawn/s | Steps run / lost a second | Walking, map units/s |
|---|---|---|---|---|
| 20000, all on | 10.5 | 7.3 | 69 / 26 | 114 |
| 20000, all on, steady pace off | 16.6 | 0 | (not counted) | 80 |
| 35000, all on | 15.7 | 1.9 | 72 / 24 | 112 |
| 20000, the mod's drawing off | 16.4 | 1.2 | 74 / 22 | 121 |

The faster drawing (2026-11-08, DSCLOG's shadows, dust and see-through figures redone with the same
picture; `obsidian-edition/tests/test_dsclog_drawing.py` counts their instructions). Each line is
two runs, before and after in turn in one session, the old build being `DSCLOG.EXE` and source kept
aside (`DSCLOG_ASM=` that source for framerate.py's symbols):

| Cycles, settings | Shown/s before → after | Undrawn/s | Steps lost/s | Walking, map units/s |
|---|---|---|---|---|
| 20000, all on | 10.2 → 15.5 | 7.5 → 3.5 | 26 → 25 | 113 → 112 |
| 20000, all on, steady pace off | 16.8 → 18.9 | 0 → 0 | (not counted) | 80 → 103 |
| 35000, all on | 16.0 → 18.9 | 1.6 → 0.2 | 25 → 14 | 113 → 141 |

How to compare two builds fairly: run them **alternately in the same session** (before, after,
before, after) rather than against an older table: runs of one build agreed within 0.3 frames a
second, so a difference of 1 is real. A loaded game's first framerate.py run is as good as later
ones. `framerate.py` takes the symbols from `obsidian-edition/dos/dsclog.asm`; for another build's
EXE in `dos/`, set `DSCLOG_ASM` to that build's source, or it reads the wrong counters. The script
is logs/2026-11-08-drawing-savings-runs.sh (results in logs/2026-11-08-drawing-savings.md); put the EXE back and `cmp` it afterwards. Out of a fight the combat log
panel shows only after `L` (panel.sh reads "hidden" for the expanded panel: look at a shot).

## 3. Controls that work

- **Clicks**: `python3 click.py X Y [left|right|none]` in game pixels (320x200). DOSBox captures
  the mouse, so the tool moves it relatively until the game's own pointer reads X,Y. Plain
  `xdotool mousedown/up` clicks where the pointer already is (fine for dismissing a message).
- **The look pointer pauses the game** (the user, 2026-11-07): while the eye is the pointer, the
  game's time doesn't run (no Kurzak's call, no alarm, nobody moving). Put the walk arrow back
  (`pointer.py walk`) as soon as a look or a rest is done; a wait with the eye up waits for nothing.
- **The pointer**: a right-click on the map cycles it: the plain arrow (Walk, and use/talk on a
  thing), the sword (attack), the **eye (look: opens doors)**, back to the arrow (checked
  2026-11-01). **`pointer.py walk|look|attack`** reads the mode from memory (DS:11B8h: 1 the arrow,
  4 the sword, 2 the eye) and right-clicks on bare floor until it is the one wanted (2026-11-07:
  right-clicks guessed from shots left the sword up). **Right-click only on empty floor**: on a
  party member it opens the USE screen (Escape closes it). Over bare floor the sword and the eye
  show red with a bar (nothing to act on), over a wall a red "no" sign; over a door the eye is
  plain. Only walkable ground takes a walking click (the user, 2026-11-01): a click on a wall does
  nothing, and a walk tool clicking in eye mode looks at the floor and nothing moves.
- **Walking**: `python3 walkto.py X Y` (map units). Screen = map - camera, 1 unit a pixel; the
  camera scrolls in steps and does NOT keep the leader centred, so work from the camera, never the
  screen centre. **The view can stop scrolling**: in the arena (2026-11-01) it stayed put with the
  leader at the top edge (screen y 24, under the top bar), so nothing north of it could be clicked;
  resting the pointer on the edge didn't scroll it, and writing DS:1178h (`camera.py X Y`) changed
  the number but not the picture (it's a copy, not what's drawn).
- **Scrolling the view: drag with the middle mouse button** (`python3 scroll.py DX DY`; the user's
  advice, 2026-11-01). It moves the map like grabbing it: dragging down shows more of the north (60
  pixels moved the camera 48 map units, in steps of 16). **Keep the pointer off the screen's edges
  while dragging**: at an edge the view scrolls by itself the other way, so a long drag from the
  centre ran the pointer off the bottom and sent the view south, and a loop that sized each drag
  from the last ran it off to (0, 1368) (2026-11-01). scroll.py starts each drag on the side it
  moves away from and caps it (270 x 150 pixels). Then click the spot and the party walks there,
  finding its own way round walls. **After a drag, release every button** (scroll.py does): the game
  took no clicks at all until they were. **A message box blocks drags too**: drags made under one
  did nothing, and the view later jumped. Clear boxes first. A click on a wall or off the walkable
  area does nothing but log "NO PATH FROM HERE"; walkto stops after two clicks that don't move the
  leader.
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
  and the view snaps back to the party. Plan hops on a map picture (`mapshot.py`, next) and
  use `viewto.py X Y` to bring each hop's spot on screen before clicking it; clicks on walls or
  on the edge of the screen (often a wall) do nothing. walkto.py drags the view back to the
  leader when it falls behind.
- **Map pictures**: `python3 mapshot.py OUT.png [W H]` steps the view across the region and
  pastes the captures at their cameras: one map unit a pixel, so a point's pixel is its map
  position. Keep a region picture worth having in `playtest/maps/` (none is there yet).
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
  screen or menu that is open, and **opens EXIT: SAVE GAME? when nothing is**: a click after that
  can quit to DOS. Press Escape only with a menu or screen showing.
- **Ending a turn by hand**: section 4 rule 11 (a click ON the figure opens its END menu, E there
  is END TURN; E with no menu up opens the Effects screen).
- **Loose `xdotool` commands need `DISPLAY=:55`** (`export DISPLAY=:55` first): the kit's tools
  set it, a command typed on its own doesn't ("Can't open display").
- **In the enemies' turns the view follows the one acting** (2026-11-07, `ghostturn.py`): a test that
  needs a still view through an enemy turn (a figure redrawn or not) can't rely on it; the move
  redraws the whole view by itself. `markmember.py THING|none CHANGED` writes GHOST_TAB and its
  changed byte (GH_CHANGED) by hand.
- **In a fight the view barely drags**: two drags of 150 moved the camera from (1728, 768) to
  (1712, 832); the party's figures stayed on the screen (2026-11-07). Drag out of a fight to put a
  figure off the view.
- **The combat log panel covers the bottom right** (x 135+, y 120+): a click there lands on the
  panel, not the map, and a party member's figure under it can't be clicked (its END menu). Hide it
  before walking near it (the party's first step into the arena, for one, is right above it) with
  `sh panel.sh hide|show`, which checks the panel's pixel before pressing L (L alone toggles, and
  can leave it the wrong way round). `panel.sh` reads "hidden" when the panel is expanded (its check
  is for the small panel, 2026-11-06): look at a shot, and press L yourself. The expanded panel's
  filter chips are at y 87 (All 148, Party about 175); a filter chosen stays (Party leaves out the
  foes' attacks).

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
  from beside the pens' gold post at (1528, 456) (whatever part of it was clicked, 2026-11-01).
- **Opening a door (the user, 2026-11-01): the look pointer.** Cycle the pointer with right-clicks
  to the look cursor and click the door; then, with the walk arrow, click on the far side of the
  open door to move past it. The walk arrow on a door, or on the floor beyond a closed one, does
  nothing (that was the stall at Kurzak's last stop, 95,28). `python3 doors.py` lists the closed
  doors and gates on the edge of the area the party can reach (live grid 192+ where the file's
  grid has a doorway), with their map positions.
- **`doorpath.py TC TR`**: the shortest way to a square through closed doors too, listing the doors
  it crosses and its turns; `BLOCK="C,R C,R"` rules out squares (a locked door). **route.py** skips
  squares a figure stands on (96: a party member there takes the click and nobody walks), drops a
  square whose click moved nobody, and brings the view to the way ahead when nothing nearer the
  goal is on screen (the view on the leader can hide the way, as the hall south of Kurzak's stop).
- **The creation screen** (2026-11-08, logs/2026-11-08-creation-least.md): the main menu's CREATE
  CHARACTERS (165,92) opens VIEW CHARACTER (its bottom icons: view character, inventory, cast,
  effects at x 52, 76, 100, 122, y 171; RETURN TO GAME 266,172 goes back to the menu); right-click
  an empty slot (64,52) for NEW / ADD / CANCEL, and NEW (110,57) opens the creation screen with a
  human fighter. A score's **small square** (x 6; STR y 140, DEX 146, CON 154, INT 161, WIS 167,
  CHA 174) takes the clicks, not the number: right-click lowers by 1, left-click raises, kept
  between the least (DS:4994h, just worked out for that score by 67399h) and the most (DS:4992h),
  going round past either (with the as-rolled rule a round trip upward is cut to what's spare).
  A class: click its name (x 250; cleric 13, druid 21, fighter 29, gladiator 37, preserver 45,
  psionicist 53, ranger 61, thief 69); a human's class must be clicked off before another is
  chosen (a click on a second class does nothing). The race text and the small figure at the top
  don't change the race (the figure rolled a new character); a race and classes can be set in
  memory for a check (the creation sheet at the far pointer DS:119Ch: race +18h, classes +21h,
  1-8 as the list). EXIT (278,160) leaves without keeping the character. **The pointers stay
  set afterwards**: DS:119Ch then points at the party's first sheet and DS:11A0h at the creature
  table, in play too (null only in a game loaded first); on the screen the record is straight after
  the sheet (`gd.creating()`). While the screen is up the party's first slot carries the
  character's name on a stand-in sheet (XP 4,000, scores 10) whose XP moves with the class.
- **Loading**: the title (two clicks), then the main menu: START GAME, CREATE CHARACTERS, LOAD
  SAVED GAME (170, 109), EXIT TO DOS; the LOAD screen lists the slots (click one at 100, 46), then
  LOAD (253, 46). `loadsave.sh` does it.
- **Talk menus** (WHAT DO YOU SAY?): click the line, or press a number key: 1-5 choose the line at
  once, as the manual says (2026-11-08: `xdotool key --window $W 2` chose Kurzak's second line, 5 his
  Goodbye; the game's talk key table, DSUN.EXE 7DDB0h: 1-5, Y, N, Up, PgUp, Down, PgDn; the Loader takes
  none of them. An earlier note said they did nothing: the key had gone to another window). The list scrolls:
  its down arrow is at (311, 187), and the last visible line is about y 189. The dice log lists
  every choice with a number, which helps find the one wanted.
- **The inventory screen's places** (2026-11-02, from hovering: the name shows in the bar at the
  bottom; the ones used): ammo (66,26), missile (66,48), arm (66,70), right hand (66,92); chest
  (173,70), left hand (173,92), legs (173,128); the backpack fills down its first column first:
  (195,26), (195,44), (195,62), (195,80)... (rows 18 apart; 48 and 70 are between cells), then
  (213,26)... Click an item to pick it up, click a place to put it; armour can't be put on in a
  fight ("CANNOT USE THIS ITEM"); a wrong place says "ILLEGAL PLACEMENT" and keeps it on the
  pointer. **The feet** are at (174,147) (2026-11-09, logs/2026-11-09-silent-labels.md); a
  right-click there opens the boots' box. **To give an item to another member**: click it, click
  the other's portrait (22,160 for the fourth), click the place. An item turned into another in
  memory (a whole record but its link +4, flags +10h and slot +11h, so the price comes with it)
  shows in its box once the portrait is switched away and back.
- **Checking a figure's glow** (2026-11-09): `sprites.worn(gd, MEMBER)` (through live.py) gives what
  the Loader dresses it in, `'magic'` on a magic piece; then eight `import -window` grabs 0.2 s apart,
  cropped round the piece and montaged: a glint is a few pixels changing between grabs (the pointer's
  animation changes pixels too: move it off with `click.py 280 180 none` first: a red patch at
  Gerakis's feet was taken for the pointer and his boots for missing). **An outfit changed in memory
  on the map shows only once the game draws the figure again**: the Loader writes the store in place
  when the slot's picture isn't in memory (flags 1: stored; 3: stored and in memory), and the game
  reads it back at its next draw (a walk). Compare the slot's memory (its far pointer) with the
  Loader's copy (`dos/SEGOBJEX.GFF`) before calling a figure undressed. `memberpos.py N` out of a fight gave the leader's
  place for every member: find the figure on a shot.
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
- **The Loader's own window for a screenshot** (2026-11-07, `docs/dicelog.png`): the container's
  Python has no tkinter; `apt-get install -y python3-tk` gives it to `/usr/bin/python3.12`, which
  runs `python3.12 -m dsloader view` from `obsidian-edition/`. Stop start.sh's text dice log first
  (by pid: two Loaders would both write to the game), and start Xvfb big enough (`-screen 0
  1440x900x24`: the window is 1320x780; topartyfight.sh's checks need the text log, so play the
  opening by hand: S at the menu, the proclamation's seal at 262,165, then boxclick.sh). The two
  windows overlap there: `xdotool windowraise` the one to click. DOSBox keeps the mouse once it has
  it: Ctrl+F10 (`xdotool key --window DOSBOX ctrl+F10`) lets it go, then `xdotool windowfocus` the
  Loader before typing (keys typed with DOSBox focused reach the game: the letters toggled its
  animations). `import -window` grabs the window at its size. The opening show was over within
  about 15 s of the seal (2026-11-07): attach the window before START GAME to have the default
  party's opening lines and the show's rounds in its log. For a picture of the default **Game
  window** box (Triple), pick it in the box (the list opens below it; Triple is the third line):
  that writes `window_scale` 3 to settings.json, so set it back to 1 afterwards (`launch.save_settings`)
  or the next start.sh run's checks fail. The status line then says "from the next time you start
  the game" in place of "Connected to DOSBox".
- **The practice program** (`tests/make_fake_party.py`, for `docs/viewer.png`): run `dosbox
  FAKEPTY.COM` in a scratch folder, then the window; Sadira loses 1 HP a second and her byte wraps
  past 0 (133/30 two minutes in), so search `sadira`, pick the hit and Assign within about 15 s of
  starting it. Reconnect picks up a restarted DOSBox.
- **The leader**: the inventory screen's small face button left of each portrait (the first of the
  two; the lit one is the leader's): Cilla's at (7, 152), the others' 44 higher each (2026-11-08,
  from the manual's "Leader" button).
- **Talking to someone who walks** (the Trustee, 2026-11-08): wait where his rounds pass
  (`$WORK`-free scripts: his thing from `gd.combatants()`, his place at DS:669Dh + 32n), and when he
  is on screen and near, `pointer.py look`: the eye pauses the game, so he stops. A slow press on his
  figure (about 12 pixels above his feet; a red eye means bare floor) opens the Look box; its first
  button (left, about 188,158 when the box is low) talks. A YES/NO question first: Y or N.
- **The Trustee's pocket** (his talk's "(PICK THE TRUSTEE'S POCKETS)"): offered only if the one
  talking is a thief, within 4 squares of him as the talk opens, and the key isn't stolen (flag 55;
  script 146 at 884h-8ABh): a talk opened from the Look box across a room has no such line. "You
  find a key!", then Goodbye hands it over (GIVE at 0ABh, to the one talking; at his feet if that
  fails) with 250 XP. The key's icon (picture 2161, 12 x 5) is a faint grey key on the grey cell,
  near invisible at the game's size: hover the cell for "SLAVEPEN KEY" (logs/2026-11-08-trustee-key.md).
- **An XP award by hand** (2026-11-08): the dice log's tracker sees an award only as each sheet's
  XP going up, so `award.py N` (each member's sheet XP += N / its classes, a human's N;
  the sheet from `aging.sheet_address`) stand in for a kill's to check what follows an award (the
  prime requisite bonus); on the creation screen `leasts.sh` reads each score's least (`creationscores.py`). Restart the dice log (kill its pid; `python3 -u -m dsloader dicelog >>
  $PLAYTEST_WORK/dice.txt` from obsidian-edition, setsid nohup) to run changed Loader code. QUIT on
  the EXIT menu ends DOSBox.
- **Picking a pocket:** U, the thief's portrait (Cilla 108,108), the purse under the spell counts
  (157,145, a slow press: the USE screen closes), then the talk pointer on the person. The result
  is a narration box with a Continue line (click it, 30,157). From `pens-after-scar` (2026-11-07,
  logs/2026-11-07-release-check.md): walkto (1816,408), (1704,408), (1592,440), `viewto.py 1592
  470`, and Kurzak stands just south of the party (thing 47 at 1592,504; his figure at 190,118).
  A failure the thief slips away from can be tried again at once.

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
   **Where the turn's movement is** (2026-11-09, logs/2026-11-09-boots-of-speed.md): a word a creature
   at segment DS - (4356h - 37BDh), +22Bh + creature x 2 (Move x 10, set as its turn starts: 57566h,
   DSCLOG's PROBE_MOVE); the END menu shows what is left ("Move : 12"). **boxclick.sh once a fight is
   on clicks the map**: on a member's turn its clicks at 160,20 walk it (one walked Seneca 100).
   A DSCLOG routine can be tried on the live state: snapshot `g.read(0, 0x110000)` into Unicorn, CS the
   helper's segment (the header DSCLOGva less its offset in the image), DS the game's, a HLT for the
   return.
6. **Spells** (more below, "Casting spells for a test"): open the USE button (24,17), page to the spell (LEVEL at 196,171), click its icon, then the target
   (2026-11-08: a plain click on the icon closes the screen and gives an aiming pointer with the
   spell's range drawn as a ring of beads; a click on a figure inside casts. The icons drawn
   **crossed out** can't be cast then: clicks on them do nothing, and RETURN TO GAME then a map
   click walks the caster instead. They were crossed at a turn's start and plain the next round;
   why is open. A spell taught in memory (the known byte at segment DS-B56h, 168h + member x 8Ah
   + spell) shows and casts as any other. `passto.sh N` passes the party's turns to member N's,
   opening each END menu by a click above the figure, checked by the screen changing, before E);
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
8. **Never `pkill -f` or `pgrep -f | kill` a pattern your own command line contains**: it kills the
   shell running it (exit 144, twice on 2026-11-01, the second time with this rule already written:
   run the kill as its own command, by pid, and nothing else in it). Kill by pid, found by a pattern
   your command line can't match (`pgrep -f "sh [l]eavearena.sh"`), then `kill PID` in a command of
   its own. And stopping a background task can leave its children running: check with pgrep
   afterwards.
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

- **A blow from outside a fight is struck before the fight begins** (2026-11-06, `orderwatch.py`:
  fight_on and the dice log every 10 ms).
- **Seeing foes attack, without killing them** (2026-11-05, logs/2026-11-05-champions.md): not
  `fightout.sh` (it puts every foe at 1 HP); pass the party's turns instead (rule 11), stopping
  once the dice log has N more "attacks NAME" lines (`passmiss.sh` does it for a miss, then drags
  the view and takes a shot). Between
  waves click the messages and walk about in the arena (staying brings more fights). It can lose
  the whole party ("YOUR PARTY HAS BEEN DEFEATED"; a level-1 party loses to the champions): have
  a save to go back to.
- **Testing Psionic Blast without a blaster** (2026-11-04): find DSCLOG's header in memory
  (`b'DSCLOGva'`, 16-aligned; 0xC91B0 in that run), write a member's kept hit points at +1814
  (a word per combatant 0-3) and the member's HP (creature record +0) to -9, so any blow would
  kill by the game's rule (damage at HP + 10); pass turns until it's hit: it goes to 0 HP, not
  dead, and the fight's end gives the hit points back ("shakes off Psionic Blast's imagined
  wounds"). CON 20+ regeneration can wake it first (Gerakis did).
- **Level-ups in fights**: PICK A PSIONIC POWER (a psionicist's level) isn't levelup.sh's: click a
  red power's icon (about 158, 62), then FINISHED (112, 139).
- **The see-through figures in a fight** (2026-11-05/06, logs/2026-11-05-fight-test.md): seen from a
  real hide (Cilla, thief level raised to 12 in memory: hides at 95) and a real Invisibility. The
  pale bits behind a walking figure are the mod's dust (dust.py), not a smear: solid figures leave
  them too, and a full redraw clears them; an END menu left up keeps them on screen. Pace:
  `walktime.py N X Y [DIR]` (about 0.07 s a step, see-through or not; for frames, crops of
  `import` grabs, 120,50 70x70, tiled with montage). Cilla's hide, with her thief level raised,
  lands often at 95 (a d100 of 94 hid her; 2026-11-06). Hidden, Tab + Return walks the thief up
  and backstabs; it is drawn solid from the blow on.
- **A hidden walk to Move 0, and the turn's end** (2026-11-06,
  logs/2026-11-06-solid-frames-turn-end.md): `walkprobe.py N X Y DIR [SECS]` clicks, then keeps a
  window grab with N's position, whose turn and DSCLOG's STEALTH word (header +204) as often as it
  can (about 50 a second). **Move running out doesn't pass the turn**: the walk stops and END
  <NAME>'S MOVE opens and waits. After E, STEALTH went to 0 within one Loader pass, but the figure
  kept its see-through picture through the enemies' turns (about 1.4 s) and was drawn solid when a
  party member's turn began: the view is drawn again from the map's main loop, which doesn't run in
  the enemies' turns. The 2026-11-05 "two solid frames" weren't seen in 38 more hidden steps (beside
  Gerakis and K'ratchek too): closed as not reproducible after the vector fix. **Since GHOST_UNION**
  (logs/2026-11-06-solid-at-turn-end.md) the figure is solid about 0.1 s after the hiding ends, in
  the next enemy's turn, if that enemy steps or swings; one that does nothing redraws nothing, and
  the old wait applies. A turn passed can come straight back (her END TURN was the round's last but
  one; round 2 opened with her and a new hide roll): check the round order in the dice log.
- **The combat log panel and the turn tools** (2026-11-08, logs/2026-11-08-panel-fight.md):
  expanded, the panel covers the screen's right half from y 68 (docked from y 120), and a figure
  under it can't be clicked: drag the view (`scroll.py -96 0`) first. `panel.sh` reads a docked
  panel's frame pixel (140,150): for an expanded one it says "hidden" while it's up; check with a
  shot. passto.sh's "END menu opened" test counts changed pixels, and the panel's new lines can
  pass it: with the panel up it pressed E with no menu and opened the Effects screen. Hide the
  panel for passto.sh, or use fightout.sh.
- **memberpos.py can miss** a figure in a crowd: about 12 pixels higher
  opened the END menu; check a shot first.
- **Casting spells for a test** (2026-11-08, logs/2026-11-08-manual-spells.md, from `fountain-user`
  clicked into Pehtucl's ambush): `spellsetup.py 0=9 2=9 hp=200` teaches the spells, fills every
  slot and sets each of the member's casting classes (any place) to level 9 (Lex, #0, is the preserver there, Ester, #2,
  the priest), and prints the pages the LEVEL button will offer (`0 Wizard: LEVEL pages [1, 3]`);
  `hp.py 150` keeps the foes up. Then:
  - **The USE screen remembers the spell level page** each caster was last on: the LEVEL button is
    at **(196,171)** (not y 187) and steps 1, 2, ... 5, 1; shoot the page before clicking an icon.
    The arc at (266,171) is RETURN TO GAME. Icons are about 18 apart, five a row: x 176, 194, 212,
    230, 248; y 59, 77, 97; in spell-number order of the spells known at that level (`gd.spell_level`).
  - **Aimed spells** close the screen and give the aiming pointer (a ring of beads, or a box for an
    area); a click on a foe's figure casts. Harmful aimed spells are refused on the party ("can't
    cast X there: not a creature that spell can be cast on"), and "no creature there" means the
    click missed the figure: click lower, on the body (zoom a shot). **Touch spells** (record
    +0Ch 3 or 5: Free Action, Ironskin, Blood Flow, Cure Light Wounds, Remove Paralysis...) keep
    the screen up and wait for a **portrait** (66,62 / 112,62 / 66,108 / 112,108): their icon
    "does nothing" until one is clicked, and through a portrait even Blood Flow lands on the party.
    Self spells (Minor Spell Turning) cast at the icon's click.
  - **Crossed-out icons**: a caster hit just before its turn ("YOU WERE HIT" in the bar) has every
    icon crossed for that turn; plain again the next round.
  - **A right-click while aiming cancels, and passed the turn twice**; Escape on the USE screen is
    safer. A Stuck or Paralyzed member's turn opens with its END menu up: E ends it, Escape closes it
    to act (USE then opens). **`passuntil.sh N`** passes turns until member N's by the END menu
    (checked by its pixels, never E blind: E for a member with no menu, Jenna with Free Action, opened
    the Effects screen; its icon at 100,171 goes back to USE). passto.sh's clicks above a figure
    walked Lex off alone once.
  - **A spell outside the caster's spheres is cast at level 0** (2026-11-08,
    logs/2026-11-08-touch-level-and-hd.md): spellsetup.py teaches any spell, and the USE screen lets
    it be cast, but the level its time and damage take (5E25Ch) counts only classes sharing a sphere
    with it, so a fire cleric's Blood Flow or Ironskin got "caster level 0" (taken as 1). Touch or
    aimed makes no difference (Free Action on a portrait: 600 s at druid 1, 5400 s at druid 9).
    spellsetup.py now names such spells ("cast at level 0"): set a class of that sphere in memory.
    In `pens-after-arena` Cilla is an earth druid (Ironskin, Free Action, Quicksand) and K'ratchek a
    fire druid (his priest levels move with the sky: K'ratchek counts as a Wasteland Seer). Out of a
    fight, U then Cilla (108,108), the CLERIC/MAGE button (150,171) switches the spell kind; an aimed
    summon there did nothing (red no-sign). In a fight a summon keeps no effect timer (effects.py
    shows none) and no "lasts" line.
  - **Giving an effect in memory** (2026-11-09, logs/2026-11-09-rest-poison.md): `addeffect.py OWNER
    EFFECT [SPELL]` inserts a record in the effect table in owner order (35 Poisoned, 13 Diseased);
    `addeffect.py del OWNER EFFECT` takes it out. A rest at the fire ring then shows what the rest does
    with it (a Poisoned member dies: status 5, creature +1Ch). `restfixmem.py check|fix|undo` swaps the
    rest's pass 2 in the overlay buffer for the proposed "cures first" order (rest once first, so the
    overlay is loaded). Death does not take effects off a member.
  - **`effects.py`** lists the effects with time left (Stuck (11 rounds), Ironskin (6 charges));
    `effects.py OWNER 51 34 86` rewrites a Stuck into Paralyzed (47 Slowed) to test a cure.
  - The fight's Templar was creature 30 (the dice log's saves showed its WIS 17), not 11: check
    which creature a combatant is before writing its scores.
  - **Level and class tests on a foe** (2026-11-08, logs/2026-11-08-hd-spells.md): write the
    target's sheet in memory (race +18h, classes +21h..23h, levels +24h..26h; race 9 makes it
    undead for Hold Undead). Creatures of one kind share a sheet (the ambush's three Guards, 8, 9
    and 31, all sheet 15). The ambush's foes read map position -1,-1 at DS:669Dh + 32 x thing:
    find them on a shot, not from that table. Archers hitting the caster before its turn cross out
    its icons turn after turn: kill them in memory by name (`aging.kill`) when the story doesn't
    matter (never save). A "cannot save" in the dice log is the save's -100 (a natural 20 is shown
    first and saves); a natural 1 is shown before it too.
  - **Color Spray** (preserver 1, its icon first on Lex's page in `fountain-user`) can catch a
    member beside the figure clicked. **Hold Undead** (preserver 3) aims with the spell's icon as
    the pointer, takes a second click for another target, and logs "lasts N rounds" for each
    landing even on an immune target (then nothing more: no save, no effect).
  - A cast that logs nothing but takes a slot was a click beside the figure: aim from a zoomed shot.
  - Magical Stone gives three throws a casting (the stone pointer comes back; the turn ends after
    the third). The count is the spell record's byte +0, bits 2-7 (Magical Stone 3, Hold Person 4,
    Hold Undead 2, the rest 1), counted at DS:942Ch by the cast's end (DSUN 7566Eh).
  - **Spells rolling to hit** (2026-11-08, logs/2026-11-08-spell-to-hit.md): with `spell_to_hit` on
    each missile or hostile touch spell has a line `X's SPELL at Y: [touch ]attack d20 = ...` after
    its damage roll; each of Magical Stone's three throws rolls. **Touch spells need the caster
    beside the target** ("too far away" from two squares): walk it up on its turn first, cast the
    next. Moving a combatant in memory (DS:669Dh + 32n) moves neither its figure nor what a click
    finds. **Escape while aiming** cancels the aim but opens EXIT GAME? (CANCEL 125,116). For hits
    on demand, raise the target's sheet base AC (+27h) in memory; a weapon's spell on a hit can be
    tried by writing a held weapon's item +0Fh (the spell + 1). Put both back, never save.
  - **Turn Undead** (2026-11-08, logs/2026-11-08-turn-undead.md): U (in a fight it opens the USE
    screen for the one whose turn it is; the click at 24,17 opened the inventory), the TURN UNDEAD
    button at (158,146) with a slow press (out of a fight the thief's purse is beside it, at 176), then
    the aiming box: a click on the undead's figure. The button shows for any sheet with a cleric
    element in +12h bits 0-3 (1/2/4/8): to make a member a cleric in memory, set a class byte (+21h..)
    to 1-4, its level (+24h..), and OR +12h with the element (a druid, 5-8, has 0 there: no button).
    A target is undead by the sheet's race (+18h = 9), its HD the sheet's +24h; creatures of a kind
    share a sheet. Each use ends the turn; out of a fight it starts one. The ambush's foes' places
    did read right this time (`DS:669Dh + 32 x combatant`, map units): screen = map - camera.
  - **Turn Undead the AD&D way** (2026-11-09, logs/2026-11-09-turn-undead-meteors.md; "Spells as the
    manual describes them"): `turnsetup.py MEMBER LEVEL [COMBATANT=HD ...]` makes a member a fire
    cleric of LEVEL in its **second** class place (+22h; a preserver whose class is there, Lex in
    `fountain-user`, loses it: give him a cleric third class by hand, +23h 3, +26h the level) and each
    combatant's sheet undead of HD hit dice (every creature of that sheet), and lists the combatants
    with sheet, race, HD and HP. Each outcome by the table: level 4 vs 1 HD is T, 6 D, 8 D\*, 3 a 4
    needed, 1 vs 5 HD a 20. The turning's box takes every undead it reaches (the Templar beside a
    Guard was tried too); four Arena Guards stood together off the right edge of `fountain-user`'s
    view: `scroll.py -150 0` in the fight brought them on, the aim then showed a ring of beads (the
    range), and a click inside it took all four. A turned undead walks off and doesn't attack (the
    Guard ran north off the screen). A human with a cleric class added in memory is priest level 0
    to the game (Jenna). The party's places (DS:669Dh + 32n) were right; most Arena Guards read far
    off the map.
  - **The LEVEL button didn't move from LEVEL 1** once (2026-11-09, `fountain-user`, Lex after
    `spellsetup.py 0=10 33 28`, clicks at 186-205,171). It **did not come back** in a later check
    (logs/2026-11-09-level-button.md: three loads with the same arguments, in and out of the fight,
    the rules off too: 1, 3, 1, 3 each time). No fault in the game or the mod. The game's rule (88A94h ->
    81664h): a level is offered when a spell of it is known, the classes give a slot there on
    resting (not slots left: a 0/1 page is offered) and it is at most (caster level + 1) / 2 (81B16h
    for spell 0 or 69); a **human's casting class in place 2 or 3 counts 0 unless below the first
    class's level** (5E7CFh, and no slots, 5E130h: the MAGE page went away entirely). spellsetup.py
    prints the pages and warns of that. A stuck button means a caster level of 0 or 1: check what
    else was written to the sheet. For a level-1 test spell: Ester's Magical Stone, `spellsetup.py
    2=9`, the priest page's second row, second icon (hover an icon for its name in the bar at the
    bottom, y 182-194). An Arena Guard off the right edge was in reach.
  - **The USE screen's LEVEL button skips levels with nothing known** (or no class slot, or past
    the caster level's cap); the USE screen opens on the kind with slots (PSIONIC when a member has no
    wizard or priest slots), the kind button at 150,171: Lex at preserver 10 with
    only 3rd-level spells known went 1 to 3; at preserver 4 it stayed on 1 (no 3rd-level spells at
    that level: the least for Flame Arrow is 5). **The first click after U opens the screen was lost
    twice**: shoot the page after each LEVEL click. A caster shot ("YOU WERE HIT" in the bar) before
    his turn couldn't cast though his icons weren't crossed: the next round's cast worked.
  - **Combatants past 64** (2026-11-09, logs/2026-11-09-audit-fixes.md): out of a fight the map's
    things keep their numbers (`pens-after-scar`: Kalzith 220, guards 256-290, Mirlon 317; every
    combatant of `fountain-user` is under 64), but **a fight renumbers them**: at its Round 1 the things
    past the party moved to 21-47 (Kalzith 42). So a combatant past 64 in a fight is rare; the unit
    tests cover them. A Turn Undead out of a fight starts one, and its line named the target "?"
    (the number had changed by the time the dice log read it); since 2026-11-09 the record carries
    the creatures and the line names them (logs/2026-11-09-turn-undead-name.md: Cermak on Kalzith).
    **party.py's classes don't tell a human**: a human who dual-classed lists two; read the race
    (sheet +18h, 1 human) before making a priest with turnsetup.py (a human's added class is level 0). DSCLOG's per-fight tables are in the
    far block since then: TU_FAILED at FFFF0h + FD10h (a byte a combatant, bit N priest N), SWEPT
    (FF18h) and DJ_DONE (FF59h), a bit a combatant. Kalzith's pen (`route.py 1592 584`, then
    `route.py 1560 860`) puts the party beside him for a turning, and the aiming box reaches him there
    (the guards west of Kurzak's stop are behind a wall: "no line of sight").
  - **The panel's level chip** (2026-11-09): a click on the expanded panel's chip (292,74) docks the
    panel instead; the docked panel's chip (268,129) cycles Detail -> Least -> Short. The mouse wheel
    doesn't reach it under DOSBox; a click on the scrollbar's track above the handle (309,140) pages up.
    The cycle was used to see the spell to-hit lines at Short.
  - **Minute Meteors and Flame Arrow** (same log): with the manual's spells, Minute Meteors gives five
    casts a slot (the pointer comes back after each, as Magical Stone's), each with its attack line
    (`+2 Minute Meteors`), and Flame Arrow one cast for every five levels (2 at preserver 10, 3 at 15,
    1 at 9), each 5d6 with no attack roll. Click the target once per cast, 4 s apart.
  - **Group 3 of the manual's spells** (2026-11-09, logs/2026-11-09-group-3.md, `fountain-user`):
    - **`foeset.py`** lists every combatant (creature, HP, sheet, race, classes, levels, magic
      resistance, the creature record's six scores) and the table of active effects (owner, caster,
      spell, effect, handle, charges, amount); `foeset.py C race= cls=a,b,c lv=a,b,c mr= hp= int=
      eff=ID[:SPELL[:AMOUNT]]` writes them (the sheet is shared by a kind; effects go in owner order,
      handles from 200, no timer). Used for Fire Shield (20), Blur (55), Biofeedback (4), Feeblemind
      (19), Diseased (13) and Paralyzed (34) on a creature. (`addeffect.py`, another session's, adds
      effects too.)
    - **A creature's scores (+22h) are worked out only when something asks** (a spell's handler that
      changes them, an effect's end): an effect put on in memory shows in them after the next
      Strength cast on that creature, for one.
    - **"cannot save" used to mean a save**: the game's save compare is unsigned (79BBAh), so every
      −100 saved. Since `save_signed` it fails (with the manual's spells only at first; always applied,
      in no switch, from 2026-11-09).
      Look at the effect or the HP, not only the save line.
    - **Archers crossing out the caster's icons every turn** (hit before its turn): `foeset.py C
      eff=34` (Paralyzed) on each foe that shoots; then the turns come clean. Paralyzed foes also
      fail every save (handy for a failed save on demand).
    - **Touch spells: adjacent only** ("too far away" at two squares diagonally): click a floor square
      beside the target with the walk arrow, then cast in the same turn (it worked with Move left).
      A miss with icons already up: `foeset`-free trick, the sheet's base AC (+27h) 30. **Escape while
      aiming** opens EXIT GAME?; its CANCEL leaves the aim up (the next map click casts at it); a
      right-click cancels and passes the turn.
    - **Range**: Cloudkill at about 230 map units said "too far away"; at 80 it cast. Rainbow Pattern
      and Cloudkill are areas that stay: Rainbow Pattern (2d3 rounds) made Lex, Jenna and Seneca save
      each turn and paralysed some, so aim them away from the party; Cloudkill near the party: raise
      the party's levels in memory first (6 and up only take damage).
    - **Psionic powers in memory**: a member knows power P (0-33, numbered from 138) when its byte at
      the segment of selector 2F0h (`game.SEGMENT_TABLE` + `POWER_OWN_SELECTOR`), +77h + member x 22h
      + P, has bits 3-7 set (write 8). The four members of `fountain-user` already know Life
      Draining, Biofeedback, Flesh Armor, Graft Weapon and Mind Blank. U on the member's turn opens the
      PSIONIC page; icons in power order; Adrenalin Control and Cell Adjustment then take a portrait.
    - **A spell's description in a fight**: on the USE screen a right-click on its icon opens the box
      (Fire Shield's and Cat's Grace's, logs/img/2026-11-09-group-3-*.png); a known bit or
      `spellsetup.py 0=10 44` first.
    - **A hang** (fixed): a kill made by DSCLOG's own far call of 4E0:61h inside a lasting cloud's
      round left the screen still and the pointer stuck at DS:A133h while the game's clock (DS:11D6h)
      ran on: `compare -metric AE` of two shots 5 s apart gave 0, and clicks did nothing. Restart.
    - Two natural 20s in a row came up on one Guard's saves; nothing wrong found.
  - **Group 4: the manual's monsters, dual-classing, resting** (2026-11-09, logs/2026-11-09-group-4.md):
    - **Monster powers on demand**: `kinds.py CREATURE=KIND` writes a creature record's kind (+16h);
      a kind's properties and resistance class then apply to it (15/13 the shadows' STR drain, 3 the
      babau's deadly poison, 38 the Styr's breath, 39 the Djinn's first-turn invisibility and images,
      40 the Tari's disease). **The hit powers come with melee hits only** (7A6BAh): the ambush's Arena
      Guards (bows) never brought one; the Guards (two clubs) did, and only from the first attack set
      (the off hand's hits brought none). A kind set on a creature not in the fight does nothing: set
      every guard of the kind. **The priests' Poison a hit casts (bit 15) kills at once on a failed save**,
      in a fight too ("Jenna takes 263 from Poison, now 0/300 HP", status 5): put the member back in
      memory (`addeffect.py del N 35`, `setmem.py status=N:1 hp=N:300`).
    - **`passn.sh N`** passes N party turns as passuntil.sh does, dragging the view to each member
      first (the ambush's party stood 200 map units apart; passuntil.sh stopped "off screen").
    - **A Weakened's amount is added to STR** (the ability routine, 7B80Eh): -1 takes a point off, 1 adds
      one (a first drain raised STR, seen); Chill Touch's is -1 (79855h). Each Weakened is its own entry.
    - **The DUAL window** (dual-classing): the inventory screen (I), a right-click on a portrait (Cermak
      20,104 in pens-fire-count4) opens EDIT NAME / DROP / DUAL (CANCEL in DUAL's place when it isn't
      offered); DUAL at 90,145; the classes greyed or white (zoom a shot: `convert -crop 120x110+150+30
      -scale 300%`); EXIT 213,145. `sheetscore.py M lv=N con=N ...` sets the first level and the creature's
      scores (what the window reads). `setmem.py ruleshi=-2048` turns the rule off in DSCLOG's header
      for a comparison (the Loader writes the rules only when they change).
    - **Rests for a test**: `pens-fire-count4`, `ringrest.sh`; each rest test from a fresh load (two rests
      bring Kurzak's call, and his patience runs out). `setmem.py` sets HP (negative too, with status 3
      for Out Cold), PSP, a power known (`power=1:13`, K'ratchek's Cell Adjustment) and DSCLOG's rules;
      K'ratchek (a druid there) knows Neutralize Poison and has a 4th-level slot. The rest's dice-log
      lines: `At rest: ... casts ...`, `X rests 8 hours: +3, +6 (CON 22) = +9, now 19/54 HP`; CON 20+
      regeneration's +12 for the 8 hours then follows as an HP line.
- **A read-only dice log** (`rolog.py`, 2026-11-08): to try changed dice-log code on a DOSBox whose
  Loader isn't this session's (stopping another's Loader was refused), run `rolog.py` into a file of
  your own: describe() and hp_changes() from this checkout, no writes to the game. Its pending rolls
  ("Dice: ...") and the Loader's come seconds after the lines around them: read the order with care.
  `--d20` shows each 1d20's caller code and frame (an overlay's INT 3Fh stub, `cd3f...`, in place of
  the code after the call is common in the spells' overlay).
- **The shared DOSBox lock** (2026-11-08): with another agent on the same DOSBox, every play step
  ran under `flock /tmp/playtest/dosbox.lock`, held for the whole session by a background
  `flock ... -c 'while [ -e HELDFILE ]; do sleep 2; done'` (each Bash call is a new shell, so `exec
  9>` doesn't last); removing HELDFILE releases it. A DOSBox found running that this session didn't
  start isn't restarted: play in it (`loadsave.sh` would kill it).
- **Figures gone from the map** (2026-11-08, the ambush after a long run of clicks): the party, and at
  times the foes, weren't drawn though their places were right; I then Escape (the inventory opened
  and shut) drew them again, for a while. Clicks on a figure not drawn missed (passuntil.sh gave up).
  **Found 2026-11-09** (logs/2026-11-09-missing-figures.md): the game's **picture store** (741,376
  bytes, fixed, DSUN.EXE 60D9Bh) and its table of 300 picture slots (load segment + 3E60h; DS:1F84h
  the slots taken) are given back only at an area load. Each time the Loader dresses a member anew
  (any change to what its figure wears: inventory moves, a weapon's +0Fh written in memory) it marks
  the old pictures FFFEh and the game takes a new slot and about 7 KB of store for each. The pens
  take 200 slots and 275 KB on arrival, so after some 30-60 gear changes there a picture lies past
  the store's end: drawn while in memory, never read back once let go, and every failed read keeps
  the memory it took, until no figure can be loaded (all gone; I then Escape frees that memory, so
  they come back for a while). **A long test in one area with many gear changes runs into it**:
  check `cachelist.py` (slots taken) and `cachelist.py all` (the last slot's place + length against
  741,376), and reload the save or change area to start afresh. Fixed: the Loader leaves a figure
  undressed when the store has no room (`_room_for`), and reuses the game's slots (the picture-store
  fix, below), so the store hardly grows. Flaming Sphere cast at a foe two squares off struck the
  caster (twice); farther off it took a slot and logged nothing.
- **Watching figures and pictures** (2026-11-09): `figwatch.py SECONDS [EVERY] [TAG]` (passive, no
  writes: each member's screen place, its map record's +0 (80h: not drawn), its picture slot (+0Fh)
  with that slot's number and flags (2: in memory), the draw list's order and the member's place in
  it, and a strip of grabs round each figure); `drawlist.py [all]` (the draw list at DS:6690h, kept
  in rising y: the drawing finds its window DS:57CAh-57C8h by a scan that stops at the first y past
  the view, so an entry out of order would hide all after it; never seen out of order);
  `cachelist.py [all]`; `poolfree.py [SECONDS]` (the picture memory's free bytes, DS:8E94h);
  `fillcache.py MEMBER SLOT UNTIL` (fills the slots fast by toggling a worn item's slot byte, the
  Loader dressing each time; memory edit, never save); `figcheck.py LABEL` (a grab before and after
  DSCLOG's VIEW_REDRAW, header +242, and the pixels changed round each member: a figure missing then
  drawn shows hundreds). An inventory move in a test: `click.py` the item, then the place; an item
  left on the pointer isn't in a shot (it was dropped by the next click on DROP, 213,134).
- **The picture store itself** (2026-11-09, logs/2026-11-09-picture-store.md): an XMS block behind
  the game's paged memory manager (handle DS:4C33h, pages through the directory at DS:42D2h); in
  DOSBox it was guest RAM at 110000h, XMS pages 2-2Fh in one run. `picstore.py` finds it and checks
  every in-memory picture against its store bytes (`check`; all should match), lists the STALE cells
  (`stale`) or dumps a slot. The picture pool is 60,000 bytes; opening the inventory (I) puts every
  picture out of memory (`cachelist.py`: 0 in memory). `outfitcycle.py MEMBER SLOT N` changes an
  outfit N times (as fillcache.py, but waiting for the Loader's copy to be written, not for the
  slots to grow) and prints slots, STALE, the store's end and whether the figure is drawn each time.
  A scratch copy of the mod for a Loader change: `git archive HEAD | tar -x -C DIR`, the game copied
  to its own `PLAYTEST_WORK`, and the tools run from `DIR/playtest` (start.sh takes the Loader from
  the kit's parent folder); restart only the dice log (`python3 -u -m dsloader dicelog` from
  `DIR/obsidian-edition`) to run changed Loader code in a running game.
- **The combat log's doc pictures** (2026-11-09, logs/2026-11-09-combat-log-shots.md): from
  `fountain-user`'s ambush, `scroll.py -60 -80` in the fight brings the party left of the panel; the
  docked panel's **+** is at (311,129), the expanded one's **-** at (296,74) (not 311). Pictures are
  `shot.sh`'s scaled 200%; a GIF is `import -window` grabs in a loop (about 32 a second), picked 40
  ms apart and `convert -delay 4 -scale 200% -layers Optimize`.
- **Picture slots while exploring** (2026-11-09, logs/2026-11-09-picture-slots-explore.md): the
  pens load 203 of the 300 slots on arrival and walking about adds none (`slotcount.py` at each
  stop); fights add a few (bodies, dropped items, spells). Wake of the Ravager's "graphics disappear"
  note is this same limit; leaving the region clears it.
- **A person's new gear and old saves** (2026-11-09): the Loader's changes to a person's items (its
  object's record in SEGOBJEX, as worldgear's) reach only creatures the game makes after them: in
  `fountain-user` Legcrusher still held his two Wooden Clubs (`npcgear.py`), not the Cahulaks +1, since
  the save holds him as he was made. Test such a change in a new game, or an area not yet visited.
  Type 146 (the metal cahulaks) read from the game's type table as built (`gd.item_type_record`).
- **A weapon's rule in a fight** (2026-11-09, logs/2026-11-09-cahulaks.md): from `fountain-user`, a
  weapon put on a member in memory (a whole record from SEGOBJEX: `champions.game_item(chunks, TYPE)`,
  its link +4, flags and slot kept, +08h 270Fh) before the speech box is clicked; Tab + Return on the
  member's turn (`passuntil.sh N`). **The ambush defeats the party when turns are only passed** (twice:
  a Templar's Hold Person, the archers): paralyze every foe first (`foeset.py C eff=34` on each, 17 to 47
  there, more coming as the guards are sent), free one with `addeffect.py del C 34` to watch its turns.
  A foe's save numbers are its sheet's +37h-+3Bh (PPD, RSW, PP, BW, SP), shared by its kind. The dice log
  can be restarted on a running game to try changed Loader code (kill its pid, `python3 -u -m dsloader
  dicelog --pid ... >> $PLAYTEST_WORK/dice.txt` from obsidian-edition).
- **A rule by size in a fight** (2026-11-10, logs/2026-11-10-creature-size.md): from `fountain-user`,
  every foe Paralyzed (`foeset.py C eff=34`) and its sheet made a half-giant (`foeset.py C race=5`:
  large by race; the Guards there, Legcrusher's kind, are half-giants already), then Tab + Return on
  party turns: the dice log's damage line says "(1d12 for 1d8: a large target)". **A Paralyzed
  target gets no save line from Hold Person** (it fails every save; the game logs only "gives
  Paralyzed"): free it first (`addeffect.py del C 34`). Hold Person's pointer stays up for its next
  target after a cast. `setmem.py ruleshi=-16384` / `=16384` turns the size rule off and on.
  **Held foes lose more HP than the log shows** (an open finding, not the size rule: a hit for 8 took
  16 and a miss after it 10, read from memory): don't check damage numbers on Paralyzed foes.
  `passuntil.sh` stops with "member N off screen"; `passn.sh N` drags the view first.
  **The large dice in the item box** (same day): I on the fight's first turn opens the member whose
  turn it is; a portrait (20,104 the third) shows another; a right-click on the right hand (66,92)
  opens its item box (crop `-crop 110x80+70+60`, scaled 200%). The inventory's weapon block (Ester's
  bow and two long swords, its worst case) ends at y 162 and the panel's stone at about 176: no room
  for more lines. **No weapon name is wider than "+1 Shadowseeker"** (82 pixels, the panel's whole
  82; "+3 Dag's Dagger" the same; measured in the game's font, `art.GameArt(GAME).font`).
  **The inventory's input** (for anyone trying a click there again): the stats panel is no cell;
  the game takes clicks from its queue of events (the mouse handler at GAME_HANDLER posts (2, 0Eh,
  0, x, y, -, events) through 3164:023Ah; its keyboard reader, 31C48h, posts (1, 0Ah, 0, key,
  shift) from the BIOS buffer through the same call), and never polled INT 33h's functions 3, 5 or 6
  there. Clicks with x and y changed to a portrait didn't reach the portrait's handler (70352h);
  **Space** (3920h) in the inventory gives the shown member's portrait event 8: drawn again, and its
  EDIT NAME menu opened (it then blocks every click; Escape posted after it didn't close it in step);
  **1-4** (the table at 6FDD0h + 1E3Bh) give event 7, which doesn't draw the shown member again.
  `symread.py NAME...` reads DSCLOG's variables in the running game by name.
  **An item's icon in the game** (same day): write a held item's +0 (minus the object: -2672 the
  Cahulaks +2's) and +0Ah (its type) through live.py (the items at the far pointer DS:165Dh, 15h
  bytes each; Lex's 43 the right hand, 36 the missile slot in `fountain-user`), then I and the
  member's portrait: the slot draws the object's icon (the box's text stays the old item's).
- **Lots of items on the ground** (2026-11-09, logs/2026-11-09-picture-slot-reuse.md): `giveitems.py
  MEMBER N [FIRST]` gives items of different objects (each its own picture) into free backpack cells
  in memory (12 cells: then "no room"); `groundfill.sh CYCLES [FIRST]` gives Gerakis 12 and DROPs
  each (I, his portrait 20,20, a cell then DROP at 213,134; cells x 195/213, y 26-116), cycle after
  cycle, printing `slotcount.py` (slots, store end, in memory, STALE, and PIC_REUSE's reuse count
  `pf_count`, read through a symbol map). Dropped items pile on the party's square: walk off to see
  them. **An item record copied from the objects file needs +08h set to 270Fh** (no contents; the
  file has 0, which in memory names item 0, and then the inventory drew no icons at all, whatever
  the build). `slotcheck.py`: every map thing with a slot finds its own picture there, every wall's
  slot taken; six entries of the thing table naming slot 0 with nonsense pictures are the table's
  unused ones (the same on a fresh load). From `pens-thornwall-rack` 145 items took the table from
  203 to 300 in nine dozen (about 40 s a dozen).
- **The inventory and the picture cache**: opening it puts every picture out of memory, and its
  icons are loaded through the same cache and let go once drawn, so at 300 slots they are free for
  reuse: a search that always began at slot 0 had the icons take one slot in turn (3,590 reuses in
  a cycle). PIC_REUSE now searches round from after the last slot it reused.
- **Outfits and the store since the fix** (2026-11-09, logs/2026-11-09-picture-store-fix.md): the
  Loader puts a re-dressed picture into a slot the game already has (`sprites.Dresser._in_store`), so
  `cachelist.py`'s slot count no longer climbs one a gear change: a toggle reuses the slot holding
  that outfit, the inventory open writes each picture's own slot, other outfits take a free STALE
  slot; a new slot only when the outfit is bigger than any free one (a few in the first dozens of
  changes, then none). `fillcache.py` waits for the count to grow, so it now stalls (4 s a change):
  use `outfitcycle.py` or `randout.py N [SEED]` (random items of member 0 on and off). A test that
  needs the store full (the old vanishing figures) now needs a picture loaded anew some other way.
  Before a DOSBox run with the repository's Loader while another session edits the helper, assemble
  `dos/dsclog.asm` to a scratch file and `cmp` it with `dos/DSCLOG.EXE`: the same, and the tree's
  build is fine to run.

## 5. The story so far: what's known of the route

**A new game** (`start.sh`, then `topartyfight.sh`: START GAME, the ready-made party, the opening,
the step forward) ends in the arena's first fight (region 2Ah), party at about (488, 424).
- The opening's show fight (a Rampager kills a Defiler) isn't the party's: leave it be.
- The party then waits at the gate (488, 168-184): "Gladiators: Step forward, into the arena!".
  One step south takes it to (488, 232), between the gate and the bone wall; the game brings it
  into the arena (488, 424) and starts the fight on its own once some game time has passed:
  keep clicking south (each click passes time) until `fight_on 1`, about 8 clicks.
- Then `sh arenawaves.sh`: every wave fought with fightout.sh, the messages between, and the
  YES/NO question answered N; and at once `sh leavearena.sh` (out of the arena: below). Run them
  together: `(sh arenawaves.sh && sh leavearena.sh)`, in the background, followed with a Monitor.
- **The first bout can fail to start**, now and then (2026-11-02: topartyfight.sh ended "NO
  FIGHT" at (488, 232), and 60-odd more clicks south and walks between (488, 232) and (488, 264)
  (the bone wall stops the party at 264) over several game minutes didn't start it; two later
  fresh games that day started at once). The bout is GPL 2's entry at 1 (case gnum 3 = 1, "Step
  forward" sets it), run by MAS 42's code-111 trigger on object 2059 at (498, 341), beyond the
  bone wall, and it waits on flag 5 (MAS 42 sets it on loading); the flags can't be read in the
  arena. Why it sometimes doesn't is open. **When it doesn't start, restart (`start.sh`) and try
  again before digging.**
- **Resting** (the user, 2026-11-05): the fire room off the east passage, its door at square (115,
  53), map (1848, 856), opened with the look pointer; in it a small fire ring among haystacks (map
  about 1931, 856): the **look pointer on the ring** rests ("THE PARTY RESTS", hit points full; the
  game's rest, 8066Dh; the east hall's object 2264 at 1908, 675 is a haystack, 137:F5h, not the
  ring). After two or three rests and a step, Kurzak calls ("Gerakis! Get up here! It's your turn in
  the arena!"). **Answer the call quickly**: twice the party walked to Kurzak's stop and on toward
  the gate (1816, 408) and he ran out of patience ("That's it! Time's run out!"), then the alarm and
  a fight with every guard. **The alarm fight on purpose**: `toalarm.sh` (loads `pens-after-scar`,
  records the sound, raises Cilla's thief level in memory, walks to the fire room), then
  `restalarm.sh` (rests, then waits Kurzak out); the alarm then sends wave after wave, with
  `fight_on` 0 only a moment between them (fightout.sh stops "DONE" there: run it again); about 15 minutes in all, in the background with a
  Monitor. **toalarm.sh can stop short at (1832, 856)**, outside the fire room (2026-11-06: its last
  walkto said NO PATH FROM HERE with the door open). **A look click on an open door closes it** (the
  closed door is the gold pole; the user caught a close taken for an open): check a shot before
  clicking a door. With the door open, the walk arrow on the room's floor (screen 240,160, camera
  1656,720) took the party in. **The pointer must be the eye before restalarm.sh**: on 2026-11-06 it
  was the sword, no rest came ("rests: 0") and the click on the ring fell on Cilla (Gerakis attacked
  her out of a fight). In a fresh container (2026-11-06) `toalarm.sh` then `restalarm.sh` worked
first time, with the eye set by two right-clicks on bare floor (a red eye with a bar over floor
is the eye). `toarena.sh` answers the call instead (up to the arena).
- **Into the arena from the pens** (the user, 2026-11-05): after the call, Kurzak's entryway
  (`route.py 1592 584`), his stop (1592, 520), north to (1592, 440), east along the corridor at
  y 408 (walkto in two steps: further north, y 376, counts as escaping and sets off the alarm)
  to (1816, 408), then a click into the gap in the brick wall just south of it (1816, 440):
  "Enter the arena?" **Y** (before Kurzak's call the gap asks nothing). In the arena: south from
  the gate (488, 200) with clicks (each passes time), through the bone wall's gap (504, 360), and
  on south onto the stone platform until the bone gate closes behind the party (488, 408-424):
  then the Announcer and the bout.
- **The pens' main door** (objects 2145-2146 at 1571-1611, 559: the entryway Kurzak opens) has
  the "Take me to the Arena! I want a fight!" menu (137:14CEh), but open it answers nothing to
  the look pointer.
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
  "Attention gladiators: Go back to the pens to heal your wounds." After a repeat fight it may
  say only that, with no YES/NO question (arenawaves.sh stops at either).
- **Staying sends another fight, every time**: the clock after "Go back to the pens" is short (a
  few walking clicks; it barely moves while the party stands), then "Since you will not leave, you
  must fight!", "If you don't want to return to the pens, then you must want another fight!" or
  "Excellent! These gladiators wish to fight again!" and a wave (Silt Runners, a Screamer
  Beetle...), each able to bring a level-up screen, and "Go back to the pens" again, until the
  party leaves. Leave at once, and don't walk south or east first (the 2026-11-01 run lost its
  time getting the view to the wall).
- **Out of the arena** (done 2026-11-01, the fourth run; `leavearena.sh` does all of it): after the
  last fight, drag the view north (scroll.py) until the ground inside the wall (488, 232) shows,
  click it, and the party walks round into it by itself (the user's advice, 2026-11-01: if the
  party stops at the stone wall, click inside the wall's boundary; don't stay outside the walls,
  as more monsters are sent); then click the gate strip (488, 184): "This corridor leads down to
  the slavepens. Do you wish to continue? (Answer Yes or No)": **Y** (N, as for the Announcer,
  turns it down, and the question comes back only on stepping off the strip and on again). The
  party comes out in the pens (region 29h) at (1816, 440). In the scripts (MAS 42's move
  triggers): the gate strip, squares 28-32 at row 11 (map x 448-527, y 176-191), runs script 3 at
  73Eh, which (with flag 11 set, by script 2 at BB8h, and local 32 at 0) takes the party to the
  pens (region 29h, 113, 27); squares 5-7 at rows 30-32 run script 3 at 6B4h ("Gladiators
  escaping! Guards! Sound the alarms!": avoid them).
- The cluebook (#13): "Follow Kurzak to and from the pens when fighting in the Arena."

**The slave pens (region 29h)**: through the gate the party comes out at (1816, 440) and Kurzak
meets it ("These are the slavepens. I'm Kurzak, leader of the guards. Follow me. I'm here to lead
you to your cell."; his menu: help me escape or I'll kill you, about yourself, the half-giant,
escaped slaves, the exits, Goodbye: "Get moving! I gotta get back to work."). `pens-after-arena`
was saved a little further on, in the corridor at (1672, 344) with Kurzak beside the party
(checked by loading it, 2026-11-07). The way to the grate, from the scripts and the region file (2026-11-01):
- The stalker pen nearest the north: its door, objects 2163/2164 at (256, 864-896), is barred.
  Using it says "The door is locked. It appears quite sturdy."; attacking it (138:121h) rolls
  RAND(30) against the attacker's STR to bash it open, and the Mountain Stalker (151, at 187,856)
  then hunts the party. A second stalker pen is further south (door 2157/2158 at 255,1087-1119).
- **From the save, follow Kurzak**: the party starts in the corridor at (1672, 344), shut in on the
  west (the corridor runs on to 1352-1400, 344): a gate at squares (81, 20-21), map (1304, 320-351), the gold post west of it,
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
  door at (113, 90) (map 1816, 1448; `route.py 1816 1400` stands beside it; locked on 2026-11-04,
  with the party straight from the arena and Kurzak followed: check its look box), west along the bottom
  corridor (rows 91-95) through the door at (93, 94), north up columns 34-35 to the south hall
  (rows 66-70), and north at columns 17-20 to the stalker pen's anteroom (its door 16, 54-56).
  On the way, two slaves whisper "Is it time to break out yet?" / "Shh, not yet!".
- **Opening the stalker pen's door sets off the alarm** (the user, 2026-11-01): plan for it (the
  guards come) or find another way to the button.
- Button 1281 at (139, 748), the pen's north wall: used from within 4 squares (137:1AE8h, else
  "is too far away to press the button") it sets flag 518 and "hears a click as the secret door to
  the west opens". (Button 1280 at 1335,798 opens another door, 81-82,53-54, only once the monster
  266 at 1264,848 is gone or flag 317 is set; otherwise "presses the button, but nothing happens".)
- The grate, object 1234 at (46, 86), the far northwest; walking onto squares 3-4, 5-6 (map
  48-79, 80-111) runs its menu (137:29Bh): Pick the lock / Rip it open / Hack the lock off.
- **The weapon rack** (Thornwall's, object 2599) is at square (48, 34), map (779, 550), in the room
  west of the door at (65, 38-39); from (52, 36) beside it the game has made it. Its contents (map
  object 478 on 2026-11-04): Polearm, Quarterstaff, Polearm, Axe, with Thornwall first once
  Semyon has told of the shipment (flags 756, then 757).
- The pens' cell doors (2141-2164) have USE (script 138) and ATTACK handlers ("This door is too
  strong to bash open" for the cells').

- **Pehtucl's chest** (2026-11-07, logs/2026-11-07-pehtucls-chest.md,
  logs/2026-11-07-review-fixes.md): `saves/pens-new-chest` is a new game with the chest's USE
  command (older saves lack it), but its chest was made before the shut type: run `shut.py` after
  loading, or the game opens it whatever the script says. To reach it: `teleport.py 200 1432 40
  1322`, walkto (216, 1440), then (184, 1400), a square west of it (from (120, 1464) the script says
  "You must be next to the chest"; standing on it, a figure takes the click); `pointer.py look`, a
  slow press on it (163, 70), the look box's third button (236, 101) (`chestuse.sh`). `thief.py N
  LEVEL` / `thief.py N off` makes a thief in memory. The chest's look box: first button closes,
  second **moves the chest**, third uses it. The game's trap objects: +0Fh is the trap's descriptor
  (d6, reach, damage kind), DSUN.EXE 80A11h. A new game to the pens in the background: `start.sh`,
  `topartyfight.sh`, `arenawaves.sh`, `leavearena.sh` (about 30 minutes).
  **In a game from before 2.14.0** (`saves/trap-user`, 2026-11-08) the chest was the game's plain
  one and opened after any use; the Loader shuts it now (`pehtuclchest.watch`, a few seconds after
  loading). There, from beside it (walkto 184,1400; the eye on it at 204,90, the look box's third
  button 141,125), a non-thief gets "Bash it open?" (Y); `bashloop.sh N` repeats the use and Y until
  "breaking it open" (Lex's 15% came in a few tries), clicking messages only while `msgbox.sh` sees
  one (a click on the map walks the party off) and cancelling an EXIT menu an Escape brings up.

From the cluebook's map: #11 the stalker pen (break the door,
kill the mountain stalker, push the button on the north wall: a secret door to the northwest
corner), #12 the sewer grate (square 46, 86; "use" it or walk over it: rip, hack or pick; a failed
try can be tried again), #15 the campfire (rest; two rests bring the next arena fight; keeping
Kurzak waiting sets off the alarm), #10 Pehtucl's ambush (Bloodwrath on his body).

**Water for resting (an idea for later, the user's, 2026-11-10):** resting might one day cost water,
which would need water and jugs on sale or to find in every part of the game. Whenever a play
reaches a new area, note in the test log and here where water, jugs or waterskins are (a shop,
a well, a body, a chest), with the region and map position. Nothing is built for it yet.

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
