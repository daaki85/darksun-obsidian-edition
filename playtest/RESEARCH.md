# Research recipes: the game's sounds, pictures, timing, scripts and other targets

Part of the playtest guide ([PLAYTESTING.md](PLAYTESTING.md): read its startup procedure before any
in-game test). These recipes are for finding out how the game works rather than for checking a
change: its sounds, the see-through figures, the picture store, frame rate and cycles, its scripts,
the unchanged game, the recompiled program and Wake of the Ravager. Tools: [TOOLS.md](TOOLS.md).

## Sounds

- **Hearing the game**: start.sh sends DOSBox's sound to a file when `PT_AUDIO` names one (`export
  PT_AUDIO=$WORK/audio.raw` before start.sh or loadsave.sh; else /dev/null): raw 16-bit stereo at
  44100 Hz, about 176 KB a second, real time. Note the file's size before and after an action, then
  `python3.13 soundmatch.py $PT_AUDIO A B clip.wav...` gives the loudest sample and how well each
  clip matches (r about 1.0 for the one played; 0.04 for another). `playsound.py N` has DSCLOG play
  sound N (its SOUND_REQ). The game plays nothing much on its own while the party stands about: a
  recording of minutes was silence but for a second at the start. The game's own 53 and 96 recorded
  at peaks near 2,800.
- **Comparing loudness** (logs/2026-11-09-sounds-louder.md): `playsound.py N` for each sound with 3 s
  between, the raw file's size noted round each, then the peak and the loudest 400 ms RMS of each
  stretch (numpy over the memmap): the game's fight sounds peak about 2,960, RMS -27 to -31 dBFS. A
  sound's descriptor +6 is its priority: the game skips one lower than the sound playing. **The
  descriptor's +0Ah (6Eh) is not a volume** (logs/2026-11-10-sounds-denser.md): set from 20 to 127
  the output peaked at 2,957 each time. DOSBox plays every clip at the same peak, so a quiet clip can
  only be made denser (make.py's soft-limiter drive): hide now -27.5, pick -30.5 dBFS.
- **The game's table of sounds**: at load segment + 3A98h, offset 08A2h, 6 bytes each: +1 the kind
  (5 a digital clip), +2 a far pointer to a 12-byte descriptor (+7 its BVOC). 0-130 are digital,
  131-180 another kind (4), past 180 other data: a BVOC numbered past 130 isn't played by its number
  (the mod's 140 and 141 were silent until DSCLOG lent itself entries 131 and 132 for the call), and
  the game keeps the last clip loaded under a number (one lent entry for both sounds played the
  first again).

## See-through figures

- **`ghostchk.py`** shows DSCLOG's block (GHOST_SEG), GHOST_ON and the tables; `ghostchk.py 0` marks
  thing 0 (the leader) see-through and has the view drawn again, for a look without a fight or a
  spell; `ghostchk.py 0 1` marks things 0 and 1 (each call replaces the marks). Outside a fight the
  party is one figure, the leader's; walking, it spreads into four. The live table of vectors
  (segment 0, 4 bytes each) shows which handler has each; **the install's bytes turning up twice in
  the image means two probes on one vector**, not chance ([target AC
  255](HISTORY.md#two-probes-on-one-vector-target-ac-255)).
- **A big frame see-through** (logs/2026-11-06-see-through-after-fix.md): `bigthings.py` lists the
  map's things with their pictures' most runs (near the pens' gate none past 164); `setpic.py THING
  PICTURE` draws a thing with another picture in memory (picture 459, a tuft of grass of 563 runs;
  put the old number back after), and `pastblock.py save|cmp FILE` keeps and compares the 4 KB past
  GHOST's block. Past 192 runs only the frame's top is drawn see-through, by design.
- **In a fight** (logs/2026-11-05-fight-test.md): seen from a real hide and a real Invisibility. The
  pale bits behind a walking figure are the mod's dust (dust.py), not a smear: solid figures leave
  them too, and a full redraw clears them; an END menu left up keeps them on screen.
- **A hidden walk to Move 0, and the turn's end** (logs/2026-11-06-solid-frames-turn-end.md):
  `walkprobe.py N X Y DIR [SECS]` clicks, then keeps a window grab with N's position, whose turn and
  DSCLOG's STEALTH word (header +204) as often as it can (about 50 a second). **Since GHOST_UNION**
  (logs/2026-11-06-solid-at-turn-end.md) the figure is solid about 0.1 s after the hiding ends, in
  the next enemy's turn, if that enemy steps or swings; one that does nothing redraws nothing, and
  the old wait applies: the figure keeps its see-through picture through the enemies' turns and is
  drawn solid when a party member's turn begins ([the old wait](HISTORY.md#see-through-figures-at-a-turns-end)).
- **`ghostclear.py [TRIALS]`**: at each enemy turn's start, Cermak marked see-through with
  GH_CHANGED set, the byte and the turn read every 20 ms: whether GHOST_UNION cleared it within that
  turn. `markmember.py THING|none CHANGED` writes GHOST_TAB and its changed byte (GH_CHANGED) by
  hand.
- **Pointer trails**: sweeping the pointer with `xdotool mousemove_relative` (DOSBox takes only
  relative moves) while asking for view redraws (DSCLOG header +242 = 1, 30 a second) showed no
  trails, before or after the fix (interrupts off again while DSCLOG draws: DRAW_MASKED).

## Pictures, the picture store and memory

- **Memory**: `memaudit.py` lists every DOS block (the game's, DSCLOG's, the overlay buffer, the
  see-through tables, the music buffer, free) and the heap; `memsample.py LABEL` gives one line (free
  DOS memory after the game, more while the inventory or USE screen is open); `dacwatch.py SECONDS`
  shows DSCLOG's palette copy changing (every 30 s where the game cycles colours); `ghostwatch.py
  SECONDS` counts samples with GHOST_ON 0. The current figures are in [where DOSBox's memory
  is](../obsidian-edition/DEVELOPMENT.md#where-dosboxs-memory-is); the history is in
  logs/2026-11-08-memory-pass.md and logs/2026-11-09-memory-pass-2.md. Comparing builds: [builds,
  the Loader and the tests](PLAYTESTING.md#builds-the-loader-and-the-tests).
- **The picture store** (logs/2026-11-09-missing-figures.md): the game's store (741,376 bytes,
  fixed, DSUN.EXE 60D9Bh) and its table of 300 picture slots (load segment + 3E60h; DS:1F84h the
  slots taken) are given back only at an area load. The pens load 203 of the 300 slots on arrival
  and walking about adds none (`slotcount.py` at each stop; logs/2026-11-09-picture-slots-explore.md);
  fights add a few (bodies, dropped items, spells). Wake of the Ravager's "graphics disappear" note
  is this same limit; leaving the region clears it. The Loader leaves a figure undressed when the
  store has no room (`_room_for`), and puts a re-dressed picture into a slot the game already has
  (`sprites.Dresser._in_store`, logs/2026-11-09-picture-store-fix.md), so `cachelist.py`'s slot count
  no longer climbs one a gear change: a toggle reuses the slot holding that outfit, the inventory
  open writes each picture's own slot, other outfits take a free STALE slot; a new slot only when
  the outfit is bigger than any free one (a few in the first dozens of changes, then none). DSCLOG's
  PIC_REUSE reuses free slots past 300. **Figures gone from the map** (the party, at times the foes,
  not drawn though their places are right; clicks on them miss) mean the store ran out: check
  `cachelist.py` (slots taken) and `cachelist.py all` (the last slot's place + length against
  741,376), and reload the save or change area to start afresh; I then Escape draws them again for a
  while. How it was found and what it did before the fix: [the picture
  store](HISTORY.md#figures-gone-from-the-map-the-picture-store).
- **Watching figures and pictures**: `figwatch.py SECONDS [EVERY] [TAG]` (passive, no writes: each
  member's screen place, its map record's +0 (80h: not drawn), its picture slot (+0Fh) with that
  slot's number and flags (2: in memory), the draw list's order and the member's place in it, and a
  strip of grabs round each figure); `drawlist.py [all]` (the draw list at DS:6690h, kept in rising
  y: the drawing finds its window DS:57CAh-57C8h by a scan that stops at the first y past the view,
  so an entry out of order would hide all after it; never seen out of order); `cachelist.py [all]`;
  `poolfree.py [SECONDS]` (the picture memory's free bytes, DS:8E94h); `figcheck.py LABEL` (a grab
  before and after DSCLOG's VIEW_REDRAW, header +242, and the pixels changed round each member: a
  figure missing then drawn shows hundreds). An inventory move in a test: `click.py` the item, then
  the place.
- **The store itself** (logs/2026-11-09-picture-store.md): an XMS block behind the game's paged
  memory manager (handle DS:4C33h, pages through the directory at DS:42D2h); in DOSBox it was guest
  RAM at 110000h, XMS pages 2-2Fh in one run. `picstore.py` finds it and checks every in-memory
  picture against its store bytes (`check`; all should match), lists the STALE cells (`stale`) or
  dumps a slot. The picture pool is 60,000 bytes; opening the inventory (I) puts every picture out
  of memory (`cachelist.py`: 0 in memory).
- **Changing outfits for a test**: `outfitcycle.py MEMBER SLOT N` changes an outfit N times
  (waiting for the Loader's copy to be written, not for the slots to grow) and prints slots, STALE,
  the store's end and whether the figure is drawn each time; `randout.py N [SEED]` puts random items
  of member 0 on and off. `fillcache.py MEMBER SLOT UNTIL` fills the slots fast by toggling a worn
  item's slot byte, the Loader dressing each time (memory edit, never save), but it waits for the
  count to grow, which the store's reuse stopped: it stalls (4 s a change) and is of no use now. A
  test that needs the store full needs a picture loaded anew some other way.
- **Lots of items on the ground** (logs/2026-11-09-picture-slot-reuse.md): `giveitems.py MEMBER N
  [FIRST]` gives items of different objects (each its own picture) into free backpack cells in
  memory (12 cells: then "no room"); `groundfill.sh CYCLES [FIRST]` gives Gerakis 12 and DROPs each
  (I, his portrait 20,20, a cell then DROP at 213,134; cells x 195/213, y 26-116), cycle after
  cycle, printing `slotcount.py` (slots, store end, in memory, STALE, and PIC_REUSE's reuse count
  `pf_count`, read through a symbol map). Dropped items pile on the party's square: walk off to see
  them. `slotcheck.py`: every map thing with a slot finds its own picture there, every wall's slot
  taken; six entries of the thing table naming slot 0 with nonsense pictures are the table's unused
  ones (the same on a fresh load). From `pens-thornwall-rack` 145 items took the table from 203 to
  300 in nine dozen (about 40 s a dozen).
- **The inventory and the picture cache**: opening it puts every picture out of memory, and its
  icons are loaded through the same cache and let go once drawn, so at 300 slots they are free for
  reuse. PIC_REUSE searches round from after the last slot it reused ([why](HISTORY.md#slot-reuse-and-the-inventorys-icons)).

## Frame rate and cycles (framerate.py)

`python3 framerate.py 20` walks the party back and forth (screen 40,104 to 280,104, a click every
3 s) for 20 s, out of a fight, and prints: the frames shown a second (DSCLOG's flip_count); those
steady pace left undrawn (pace_skipped); the steps run and lost (pace_ran, pace_lost: steady pace on
only); these found from a symbol map of the helper as built; the main loop's passes; the BIOS
clock and the game's clock (96 a second) against real time; the leader's map units a second
**while walking** (the waits at a target left out); and DOSBox's CPU. `PT_CYCLES=N sh start.sh` (or
before loadsave.sh) sets DOSBox's cycles; settings are changed with `launch.save_settings` before
loading (the log of 2026-11-08).
Its walk clicks are at y 104: from `fountain-user` after its fight they land in the fountain and
nobody walks (0 map units/s), so measure from another save.

How the game paces walking: its timer (DSUN.EXE seg 1DF3:29E8h) sets DS:1F7Eh at each tick of
the game's clock (DS:11D6h, 96 a second); the step (1DF3:26DCh) runs only with it set and clears
it. A tick passed while a frame draws is a step lost.

How to compare two builds fairly: run them **alternately in the same session** (before, after,
before, after) rather than against an older table: runs of one build agreed within 0.3 frames a
second, so a difference of 1 is real. A loaded game's first framerate.py run is as good as later
ones. `framerate.py` takes the symbols from `obsidian-edition/dos/dsclog.asm`; for another build's
EXE in `dos/`, set `DSCLOG_ASM` to that build's source, or it reads the wrong counters. The script
is logs/2026-11-08-drawing-savings-runs.sh (results in logs/2026-11-08-drawing-savings.md); put the
EXE back and `cmp` it afterwards.

The measurements (pens-after-arena, the whole party walking, 2026-11-08), the old steady pace's
and the faster drawing's: [HISTORY.md](HISTORY.md#frame-rate-measurements).

## Scripts and the game's code

- **The docs' code addresses (5883Ah and the like) are DSUN.EXE file offsets**, the patches'
  (`gamepatch.Patch`'s offset), not linear addresses in memory: most of the fight code is an
  overlay, so memory there reads zeros or other code. Disassemble the file (capstone, 16-bit, the
  offset as the address: near jumps and calls come out right within a routine); a near call's
  target is offset + 3 + rel16. Far calls in it carry relocations: leave their bytes where they are
  in a patch. A new hook needs no vector of its own: a site (`gamepatch._site`, DSCLOG's `site`
  table, in order) on VEC_CR_SPELLS; a site replacing a compare puts its flags into the INT's frame
  (`ammo_turn`). (logs/2026-11-14-quiver-turn.md)

- **The arena's flags and numbers can't be set from outside**: the pointers at DS:1352h and 1356h
  stay null in the arena even while a script waits on a message, so a poller never finds them. To
  test a script's branch there, build a copy of the scripts with the test forced (edit the module,
  run `start.sh`, which writes `dos/GPLDATA.GFF`, then put the module back) and say so in the log.
- **Setting the arena's visit count**: in the pens the game's numbers have a place in memory;
  number 12 is the count (4: the next trip is Scar's; 5 and up the everyday speech, or the
  champions' after Scar's death in the arena). Write it at the far pointer DS:1356h + 2 x 12:
  **`setcount.py [N]`** reads it and, with N, writes it.
- **Reading a value inside a script**: a test build whose repair PRINTs (4Fh, 98) a field prints
  nothing for a number; print a marker string under an IF per guess instead (TEST field == N, IF,
  PRINT " aN", ENDIF; the IF's address in `relocate`). Keep such a probe small: one of about 200
  tests (some 5 KB of detour) ran nothing at all, nor did 100 reading fields 72,n. Item fields seen:
  72 = the item's +00h (its kind, minus its object), 85 = its slot (+11h); no field 0-99, nor
  72,0-99, gave its type.
- **The game's command table** is words at DS:00C0h + 2 x command, the handlers in segment 5DFh
  (the dispatcher at linear 5FE9h, `call [bx+0C0h]`): dump memory with live.py (`gd.guest.read(0,
  0xA0000)`) and `ndisasm -b16 -o OFF`. 41h (5DF:1895h) stores its value, an object's number (or a
  kind, looked up), in 3923:361h (object 2Ch); 49h (5DF:140Ah), the item loop, copies each item into
  one scratch object (2Bh, 3923:35Fh).
- **The pens' master script and named routines**: `KIND='MAS ' dec.py 29 0 140` decodes the pens'
  master script; GPLI 1 is the index of named routines (id, offset, script: 2-byte words).
- **The inventory's input** (for anyone trying a click there by hand): the game takes clicks from
  its queue of events, never INT 33h's position; what was tried is in [HISTORY.md](HISTORY.md#the-inventorys-input).

## The unchanged game

For a comparison with the game as it shipped (no DSCLOG, no Loader, no dice log;
logs/2026-11-16-spell-grid.md):

- **Starting it**: a DOSBox config of the Loader's settings with its own autoexec: `sed
  '/^\[autoexec\]/,$d' ../obsidian-edition/dosbox_dicelog.conf > $WORK/plain.conf`, then append
  `[autoexec]`, `mount c ".."`, `c:`, `DSUN.EXE`, `exit`. Kill any DOSBox (by pid), then from
  `$DS_GAME/DOSBOX`: `setsid dosbox -conf ../__support/app/dosbox_darksun.conf -conf $WORK/plain.conf
  &`. The game folder's files are the originals (the Loader writes its copies to
  `obsidian-edition/dos/`). **Not `start.sh` or `loadsave.sh`**: they start the Loader's game.
- **Its intro plays**: two title clicks, then Escape a few times, then the main menu.
- **A save**: copy `saves/NAME/*` into the game folder, then LOAD SAVED GAME (170,109), the slot
  (100,46), LOAD (253,46). A save made with the mod loads.
- **What works**: `click.py`, `creationscores.py`, `sheetinfo.py`, `shotinfo.py`, `hp.py` and the
  memory tools. Not: `buildcheck.py`, the dice log and its readers, and Tab's target (`fightout.sh`,
  `toturn.sh`): attack with `pointer.py attack` and a click on the foe.
- **It differs at creation**: a new preserver gets no CHOOSE A SPELL (the mod's); the window shows
  at a level-up.
- **A screen's layout**: read its WIND chunk in the game's RESOURCE.GFF against the Loader's copy
  in `obsidian-edition/dos/` (`dsloader.gff.read_gff`; a window's places are 30-byte items from
  +105h: the tag at +4, the id at +8, x and y at +0Ch).

## The recompiled program as the target

The kit drives the recompiled program (Dark Sun Recompiled) too (`PT_TARGET=recomp`, exported for
every tool; `DSUN` names the program, default `/home/user/darksun-recompiled/build/cmake/dsun`):

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
  or before a save is loaded, it prints nothing afterwards; `loadsave.sh` restarts it after the
  load, and after any restart of the program check that an action shows in `$WORK/dice.txt` before
  trusting its silence.
- **Saves cross over both ways**: a save made in DOSBox loads on the program (pens-kurzak-door),
  and one made on the program loads in DOSBox (pens-kurzak-door-recomp). The program's save
  leaves DARKSAVE.GFF as it was, as DOSBox's did.
- Controls behave as in DOSBox: click.py's relative moves converge on the pointer, walkto walks,
  right-click cycles arrow, red sword, red look, arrow; the arrow over a person shows the portrait
  pointer and a click opens the mod's Look box (Talk is its first button, 216,99).
- **The view does not scroll by itself** here either; the middle-button drag works (the program's
  runtime passes the middle button through). **The drag scrolls only with the Loader attached**
  (the dice log counts: it switches the helper's `scroll_on` on at attach); a program started with
  no Loader, as its own headless tests run, keeps the view still. **A kit tool that stalls on the
  program and not in DOSBox is a program fault to report**, not a tool to work around.
- **Doors at Kurzak's stop**: the look pointer on the doorway's drawing (square 95,27, above the
  door square) opens the mod's Look box "Door" (INFO only); the arrow, the look click and the sword
  on the door square do nothing and log nothing; the sword on Kurzak (object 29, then at square
  99,31) does nothing either: no fight starts from a click on a friendly figure.

## Wake of the Ravager

Set up with `setup_ravager.sh` ([setting up](PLAYTESTING.md#2-setting-up)). Its DSUN.EXE is laid out otherwise:
the creature/sheet records 42h bytes at the far pointer DS:19C5h, a class's level at +1Eh, its class
at +1Bh; the XP table is RESOURCE.GFF's DATA 1000 (8 rows of 20 words, in hundreds, looked up by
`lcall 5C8:20` with 3E8h); much of the code is in overlays, so a far call's segment isn't a place in
the file. Its level-up (95860h on) caps XP at the table's entry 3 levels past each class's own, then
raises a class under 15 (2026-11-08: no race limits, whatever its README says).

**Playing it in DOSBox** (2026-11-19, logs/2026-11-19-ravager-memory.md): GOG's settings are in
`__support/app/dosbox_darksun2.conf` (memsize 16, cycles fixed 15000, XMS, EMS and upper memory
on); it runs as `DSUN -W0 -L` (RAVAGER.BAT) from its folder as C:, with `CHARSAVE.GFF` and
`DARKSAVE.GFF` copied in from `__support/save` as SL's are. The CD is D:: Linux's DOSBox 0.74 can't
take GOG's `game.ins` (its music tracks are .ogg files), so mount a cue of the data track alone
(`FILE "game.gog" BINARY` / `TRACK 01 MODE2/2352` / `INDEX 01 00:00:00`) with `imgmount d data.cue
-t iso`; the music is then silent, nothing else missing. Shift held a second skips the intro (the
menu at 6 s). Its window is 640x480 (SVGA). **The first click only captures the mouse**: click once
anywhere harmless, then `xdotool mousemove_relative`, checking with a grab (START GAME at window
310,170). START GAME, the narrated cinematic (about 60 s, no skip), then Tyr: "Hurry! You must
come with me to the Veiled Alliance!" over the map. It runs with `ems=false` and `UMBPLUS.COM` too.
**`dosmem.py [PID]`** reads the memory of any DOSBox (no helper needed): both MCB chains, the
program's far heap (load + 0FE7h in SL, **+ 135Bh** in WotR) and DOS memory after it.

**The Loader's way** (the port, `dsloader/ravager.py`): `RAV_LOADER=1 sh ravstart.sh FOLDER` makes the
Loader's copies (DSUNLOG2.EXE, RESOURC2.GFF in the mod's dos folder) and starts DSUNLOG2.EXE from D:
(the mod's folder) with the game as C: and the CD as **F:**: the game finds its CD through MSCDEX
whatever its letter (2026-11-19: to Tyr with the CD on F:, as on D:). The copy reads its data from the
current folder (C:) by its "path" patch (DS:44F2h, SL's 4B81h).

**Driving it** (2026-11-19, logs/2026-11-19-ravager-fixes-2.md): `sh ravstart.sh [FOLDER]` starts
it to Tyr with no mouse (Shift twice, **S** on the menu is START GAME, 80 s). The game is 320x200
shown at 640x480: **game y = window y / 2.4**. Its pointer is DS:A109h (x) and A10Bh (y) (SL's
A133h); `python3 ravclick.py X Y [left|right|none]` moves there and presses slowly (0.3 s). The USE
screen (the top-left icon, 22,17) acts for the leader out of a fight (a portrait click doesn't
change who); the small top button left of a portrait is MAKE <NAME> LEADER (47,43 the first);
hovering names a button in the bar below; VIEW CHARACTER 47,171, VIEW INVENTORY 74,171, LEVEL
197,171. The opening party: Ar'anda (elf preserver/psionicist/thief 6/6/7), an earth cleric 7,
Thy'rokh (thri-kreen fighter/druid, the leader), a half-giant gladiator 7; its sheets at the far
pointer DS:19C5h. **Running one of its routines on the live game** (`ravthief.py`, the thief
skills): most of its code is in overlays swapped out to XMS, so lay every overlay above A0000h from
Dark Sun Recompiled's `build_image.py` (its PSP set to the live one) with that image's stubs, the
live memory below; and give the emulator SS = DS (Borland reads stack buffers through DS).

**Its fights in the Loader's dice log** (logs/2026-11-20-ravager-dicelog.md): `python3 ravdice.py SECONDS
[OUT]` runs dsloader.ravlog.RavDiceLog (SL's dice log on the sequel's layout, its memory read only) on the
running sequel. Addresses found for it: the combatants selector 388h at C33h (load + 3F49h), the
initiative selector 308h at DCh (load + 3C4Fh), the attack's target DS:4206h, the item types 15 bytes
(DS:19CDh), the item names RESOURCE.GFF's TEXT 1000 (a line a name, from 1), the rules' small tables SL's
+70h. A selector's segment: the segment table at load + 45E8h, + the selector. `ravds.py --fuzzy HEX`
maps an SL data address by the code round its uses.
The AC function is the sequel's own (5D520h; its end 5D6E6h, PROBE_AC). `ravdice.py --all` shows every
roll and each AC worked out. **To find an unnamed roll's code**: catch its entry (its frame's first words
are the return address, then the arguments: the dice routine's count and sides) and read the code at
that address at once, before the overlay moves, then find those bytes in DSUN.EXE.
**Its picture cache** (2026-11-20): the loader at 2A568h (SL's 25FA6h) keeps SL's 300 slots, 16 bytes each
(number, length, store place, memory, flags), the count at DS:265Dh, the table at load + 42A2h:0CA8h;
253 taken at the start of Tyr (`cache.py`-style dump: the count, then each slot). Its one caller is the
map things' routine (2A388h: DS:67BBh, 25h bytes a thing, up to 141h, the slot at +10h); the walls don't
come through it. `ravsites.py [NAME...]` finds SL's patch sites in the sequel by likeness (about 8 minutes
for all 454; its finds are leads to read by hand).

**Shattered Lands' figures in the sequel** (2026-11-20, logs/2026-11-20-ravager-sl-figures.md):
`darksun-recompiled/tools/sl_figures.py build SL_DIR WR_DIR OUT.GFF` writes the sequel's `OBJEX.GFF`
with the party's 14 figures taken from SL (the walking `BMP n`, the combat `CBMP n`, the script `SCMD
n`; the study is that repository's `docs/FIGURES.md`). To play it, **copy the install for real**
(`cp -a $WORK/rav $WORK/ravsl`, 287 MB): with hard links the game's writes (DARKRUN.GFF, saves)
would change the original too. Put the built file in the copy and `sh ravstart.sh $WORK/ravsl`.
Seen working: standing, walking, the swing, hits and deaths, the anchors right. **`sh ravburst.sh
NAME SECONDS X Y W H`** grabs the window as fast as `import` goes (about 15 a second) while an action
plays, and makes a sheet of 24 of them cropped to X Y W H (window pixels); look at single grabs
(`$WORK/burst/NAME-NNN.png`) round a moment at full rate. For a death on cue, set members' HP to 1
(the creature records at DS:19C9h, +0; `ravcreatures.py` lists them): a test edit, never saved.
SL's standing side frame has the legs apart: it isn't a walk frame left on screen.
`sl_figures.py build-ui` does the same for the interface (`RESOURCE.GFF`: pictures and icons; put it
in the copy beside the patched OBJEX.GFF). Its screens in a fight: **Q** the END menu (Escape closes
it); a click on the status box (window 560,50) captures the mouse harmlessly; USE at game 22,17;
VIEW INVENTORY 74,171 on USE (47,171 opened the inventory too, not the character sheet); Escape in
the inventory closes it and USE together. The game writes its run files (DARKRUN.GFF and the like)
into the folder it runs from, so copy `__support/save`'s three files back into the copy between
runs for the same start.
`sl_figures.py regrade SL_DIR WR_DIR RGN032 STRENGTH OUT.GFF` regrades a region (Tyr is RGN032,
the opening street); put it in the copy as `RGN032.GFF`. **The sequel cycles palette entries 16-23 at
run time** (torches, fire): a colour put there shows in the game's glow colours, not the file's.
To check a colour on screen, sample the grab's pixels and match them to the region's PAL (in its
`RGNxxx.GFF`). Shattered Lands draws region N in `GPLDATA.GFF`'s PAL N (the pens, RGN29, in PAL 41).
**What's on screen where:** the camera is DS:1408h (x, y), in map pixels; the screen shows map
pixels minus the camera. The ground: **`MAP ` (or `RMAP`) is 98 rows of 128 tile numbers** (not 112 x
112), tile (c, r) at map pixel (16c, 16r); `GMAP`, the same shape, holds per-cell flags. A region's
entities (its `ETAB`, 8 bytes each: x, y, height, flags, the object negated) stand at map pixel (x, y). An object's record (`OJFF`) anchors its picture by +2 (x) and +4 (y):
the bottom centre. `sl_figures.py squash` lowers a region's structures for SL's angle.
**An exact frame from a grab:** the sequel's 320x200 frame shows in DOSBox's 640x480 window with every
pixel doubled across and rows repeated 2 or 3 times (2, 2, 3, 2, 3...), no blending: the first row of
each repeat, every other pixel, is the frame exactly, and each pixel matches a palette colour shown as
v x 4 + v / 16 (`darksun-recompiled/tools/proto/frame.py`). Sampling rows at (r + 0.5) x 2.4 instead
picks the wrong row now and then, enough to spoil tile matching. The frame isn't in guest memory as a
320x200 buffer.

**The Loader's window on the sequel**: `apt-get install -y python3-tk`, Xvfb `:56` 1440x900 (`:55` is
smaller than the window), `python3.12 -m dsloader view --pid $(cat $WORK/rav.pid)` from `obsidian-edition/`;
stop `ravdice.py` first and the window (by pid) before running it again (the game's lock). Its party tabs
use the sequel's layout made from SL's. No moment out of a fight at the start: the opening talk ends in
the ambush, so the inventory screen (to check the gear's slot names) waits for a later save.

**Its first fight** (logs/2026-11-19-ravager-fight.md): the opening talk (3, Return) ends in the
Draxans' ambush, a fight at once; in a fight USE opens for the one whose turn it is (DS:426Dh, SL's
4979h). Right clicks on bare floor cycle the pointer: arrow, sword, look; a figure under it turns
red; a look opens a box (name, level, weapons) that a click on it closes. Creature records: 31h
bytes at the far pointer DS:19C9h, +0 HP, the region's people all listed (`ravcreatures.py`).
`ravds.py HEX` finds the WotR address of an SL data-segment offset by the code before its uses.
Of the opening party's spells only Chill Touch is a fixed one (Ar'anda's); its aimed click wasn't
taken on a Draxan 1.5 squares off (a touch spell: too far, likely).

**Fights and spells, for a test** (logs/2026-11-19-ravager-scare.md): the manual's hot keys: **Q**
brings the END menu (**E** in it is END TURN), C the cast screen, G guard, W wait, N/P the next or
previous foe, 1-4 the leader; Esc with nothing up quits. `ravfight.py until N` ends the others' turns
until member N's (the order varies run to run). A caster hit this round has every icon crossed out.
**Spells known**: a 15-byte bitset a member (bit n, spell n; wizard spells only), the roster's `SPST`
chunk; Ar'anda's at 3F3DCh after START GAME (a set bit is offered on USE at once: a test edit, never
saved). An area spell's reach shows as a ring of dots round the aim (on bare floor or a foe, not on a
party figure). A creature record's +18h is 60h while Afraid. **Spell slots**: DS:446Ah + 22h a
member, wizard casts left by level, the priest's 0Bh on: a cast went off if its level's count
dropped (logs/2026-11-19-ravager-cant-save.md). **A creature's level** for the saves (1987:154 in
build_image's image): a human's first level (sheet +1Eh), else the best of its class levels. In the
file, an overlay's far call names an overlay-manager selector (98h), not a segment: follow it in
the image.

**Its spells, and the fixes carried over** (2026-11-19, logs/2026-11-19-ravager-fixes.md): no
spell table in its program; each spell is `RESOURCE.GFF`'s `DATA` 0-319, 73 bytes (SL's 32-byte
record, then the name and an 8-letter short name), read one at a time as the spell is used
(choosing Bless on USE loaded `DATA` 115 whole; nothing else held). In Tyr: Return pages a talk,
the number keys pick a reply, the top-left icon opens USE, a right click cancels a spell's aim.
**`ravfixes.py [OUT]`** makes a copy of the sequel (`$WORK/ravfix`) with the mod's fixes that
carry over unchanged: five of the program's at their twins' offsets, the spell records' by name.

**Its transfer program, CHARTRAN.EXE** (2026-11-19; the study in
[reports/wake-of-the-ravager.md](../reports/wake-of-the-ravager.md)): `sh chartran.sh SAVE.SAV OUTDIR
DEBUG` runs it in a headless DOSBox of its own (its own config: `C:\DSUN` holds the save as
SAVE01.SAV, `C:\RAVAGER` CHARTRAN, `ITEMS.BIN`, `OBJEX.GFF` and the install's roster from
`__support/save`), types Enter (the paths screen) and A (the one save), and leaves the roster it
wrote in `OUTDIR/C/RAVAGER/CHARSAVE.GFF`; 15 seconds, no Loader, no lock. Its screen goes to
`OUT.TXT` (the command line redirects it). `DEBUG` on its command line writes `DEBUG.DAT`: each item
`OLD: -<SL object>, NEW: <WotR object>` (900: a money bag, for anything not in `ITEMS.BIN`'s 234
pairs of words, so every mod item) and each spell or psionic aptitude it couldn't carry.
The party goes into free `CHAR` slots (32-35 of the install's roster, their `CACT` set from 0 to
the entity's number). A `CHAR` record: the creature record at `+0Ah` (name `+2Bh`), the sheet at
`+45h`, SL's sheet less `+0Eh`-`+0Fh`, `+14h`-`+17h` (the mod's weapon specs: lost) and `+3Ch`; SL's
`+43h` (the mod's kit byte) lands at `+3Dh` and `+45h` (second sphere) at `+3Fh`, which no
`es:[...]` access in WotR's code reads. Tried on the user's saves `selling-junk-user`, `trap-user`
and `rest-no-call-user`: all transferred, the kits kept.
