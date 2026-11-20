# The playtest tools

Every tool in `playtest/`, with the first sentence of its own header comment (`python3 tools_index.py` writes this page again from the files: run it after adding or changing a tool). `env.sh` and `live.py` are the others' shared set-up. How to use them is in [PLAYTESTING.md](PLAYTESTING.md).

| Tool | What it does |
|---|---|
| `acs.py` | each combatant's AC as the game counts it (gd.counted_ac), to hold against the dice log's "target AC" |
| `addeffect.py OWNER EFFECT [SPELL] [CHARGES]` | give combatant OWNER (0-3 the party) the effect EFFECT (35 Poisoned, 13 Diseased, 34 Paralyzed...) in memory, untimed: a 10-byte record put into the game's effect table (load segment + 3BF6h:0106h, DS:1E24h the... |
| `ammodump.py` | Jenna's and Ester's quiver, bow and backpack item records (item number, list, address, the record in hex: count +2, link +4, type +0Ah, name +12h, plus +14h, slot +11h). |
| `arenatrip.sh` | from pens-after-scar (toalarm.sh: loaded, Cilla a thief in memory, to the fire room), rest till Kurzak calls, answer at once (toarena.sh, Y at "Enter the arena?"), and count the game's free things (thingsfree.py) in... |
| `arenawaves.sh` | with the arena's first fight on, fight every wave (fightout.sh) and click away the messages between them, until the YES/NO question ("Yell something back at the Announcer?"), which it answers N. |
| `award.py N` | N XP as the game's award gives it: each member's sheet XP += N / its classes (a human: N) |
| `bashloop.sh N` | use Pehtucl's chest from beside it and answer Y to "Bash it open?" until the lock breaks (N tries) |
| `bigthings.py` | the map's things with their walking picture (+18h), its frames' most runs (from the Loader's SEGOBJEX.GFF) and where they stand, the most runs first: for a test of drawing a big frame |
| `bodyitems.py` | each Dead Body on the map (object 1101 or the thri-kreen's 2666), its things: item, name, type, plus, power, value, name number and +02h, and the type's worn place, weight and flags. |
| `boxclick.sh` | click a waiting message away by clicking ON it (160, 20, the speech box at the top): a click wherever the pointer happens to be (after a drag, say) didn't always count (2026-11-01) |
| `buildcheck.py [NAME...]` | is the DSCLOG running in DOSBox the build in obsidian-edition/dos? Compares 40 bytes of each routine named (default: a set touched by the 2026-11-09 memory pass) in memory with dos/DSCLOG.EXE, checks every vector of... |
| `cachelist.py [all]` | the game's picture cache (the table at load segment + 3E60h, 16 bytes a slot: +0 the picture's number, FFFEh one the Loader took out (sprites.STALE), +2 its length, +6 its place (negative: none), +0Ah its far... |
| `camera.py [X Y]` | read the camera (the view's top-left, DS:1178h), or set it to X, Y (map units) to look somewhere the view won't scroll to by itself (it does not follow the leader everywhere) |
| `canuse.py MEMBER TYPE...` | whether the kit rules (restrict.kit_forbids) let party member MEMBER use each item type, and pick it as a weapon spec |
| `carried.py NAME` | what the creature named NAME carries, list by list: item, name as the game shows it, type, slot, value, plus, name entry and the +02h word (2026-11-11: guavas named "Brgnd.Chst Armor"). |
| `chartran.sh SAVE.SAV OUTDIR [DEBUG]` | runs Wake of the Ravager's own transfer utility (CHARTRAN.EXE, from $RAV, setup_ravager.sh) on one Shattered Lands save in a headless DOSBox of its own (not the game's: no Loader, no lock needed), and leaves in... |
| `chestuse.sh` | uses Pehtucl's chest from where the party stands (see PLAYTESTING, Pehtucl's chest): the eye (two right-clicks on bare floor at 200,175), a slow press on the chest (161,72), its look box's third button (236,101). |
| `click.py X Y [left\|right\|none]` | move the game's pointer to game pixel X,Y (320x200) and click. |
| `creationscores.py` | the creation screen's scores, classes and race, and the least and most the game last worked out |
| `dacwatch.py SECONDS` | DSCLOG's copy of the palette (TSR_DAC) watched: each change, hashed whole and for colours 16-223 only. |
| `dec.py SCRIPT LO HI` | decode GPL script SCRIPT (the game's own GPLDATA.GFF, $DS_GAME) from offset LO to HI (hex): each command's offset, number and arguments. |
| `dismiss.sh [N]` | click away up to N (default 6) waiting messages (msgbox.sh), then print the dice log's last lines. |
| `doorpath.py TC TR` | the shortest way from the leader to square (TC, TR) on the live grid, through closed doors too (live 192+ where the region file has a doorway); |
| `doors.py` | the closed doors and gates on the edge of the area the party can reach now: squares the live grid blocks (192 and up) where the region file's grid has a doorway (below 192). |
| `doorwatch.py SECONDS` | Kurzak's door and the two who use it, printed at each change (every half second): the live walk map's square 99,34 (0 open, 192 shut, 96 someone in it), and Kurzak's and Legcrusher's map places with their orders... |
| `dosmem.py [PID]` | DOS memory in any running DOSBox, no helper needed (so either game, modded or not, or Wake of the Ravager): every block of the conventional chain and the upper memory chain (owner's name, size), the largest free... |
| `drawlist.py [all]` | the game's draw list (far pointer DS:6690h, count DS:1F72h; |
| `dsword.py ADDR [VALUE]` | the game's DS word at ADDR (hex), or set it (memory only). |
| `effects.py` | every active effect (owner, caster, effect id), its charges and game seconds left (60 a round), as the Loader reads them. |
| `figcheck.py [LABEL]` | are the party's figures drawn? A window grab, then DSCLOG's VIEW_REDRAW (header +242: the whole view drawn again, as the game does), a second grab, and for each member the pixels changed in a box round its figure... |
| `fightout.sh [MAX]` | finish a fight the game's own way, so its scripts see each kill: every foe to 1 HP (hp.py 1), then on each party turn Tab (the mod picks the nearest enemy) + Return (attacks). |
| `figwatch.py SECONDS [EVERY] [TAG]` | passive watch for the party's figures (no writes): every EVERY seconds a window grab, the camera, each member's screen place and whether its thing is in the draw list (its index, and OUTWIN when outside the last... |
| `fillcache.py MEMBER SLOT UNTIL` | fills the game's picture slots (cachelist.py) the way a change of gear does, fast: the slot byte (+11h) of the item MEMBER has in SLOT (itemedit.py's) set to 50 (no place: not drawn on the figure) and back, so what... |
| `foepos.py` | each combatant past the party: its name, HP and figure on screen (feet x, y - 10) |
| `foeset.py` | foeset.py [COMBATANT [race=R] [cls=A,B,C] [lv=A,B,C] [mr=N] [hp=N] [int=N] [eff=ID[:SPELL[:AMOUNT]]] ...]: memory only, never save after (2026-11-09, logs/2026-11-09-group-3.md). |
| `follow.py OBJECT [ROUNDS]` | keep the party within a few squares of a map object that walks (an escort: Kurzak, object 29, leads a new party from the arena's gate to its cell, a waypoint at a time, each waiting until the party is within 4... |
| `framerate.py SECONDS [X1 X2 Y]` | walks the party back and forth between screen points (X1,Y) and (X2,Y) for SECONDS and reports, a second at a time and in all: the map's main loop passes (DSCLOG's main_ticks, header +260), the frames shown... |
| `gearpoll.py` | from DONE on the creation screen, each change of DSCLOG's GEAR_DUE (+1830) and lv_creating (+361, the weapon window up), the dice log's new lines, CHARSAVE.GFF written (the roster's copy) and the Loader's heartbeat... |
| `ghostchk.py [THING...]` | DSCLOG's see-through figures: its block (GHOST_SEG), GHOST_ON, the first REP and BLEND bytes and GHOST_TAB; |
| `ghostclear.py [TRIALS]` | in a fight, at the start of each enemy turn, Cermak marked see-through with GH_CHANGED set, then the byte and the turn read every 20 ms: whether DSCLOG's GHOST_UNION cleared it (the whole view drawn) while that... |
| `ghostturn.py` | in a fight, GHOST_UNION's whole view on a GHOST_TAB change (GH_CHANGED) in the enemies' turns: at the start of one enemy turn Cermak (thing 2) is marked see-through without the changed byte (the control), at the next... |
| `ghostwatch.py SECONDS` | DSCLOG's GHOST_ON and its palette copy watched every 20 ms: each change of GHOST_ON, and how many samples had it 0. |
| `giveitems.py MEMBER N [FIRST]` | memory only, never save after. Gives party member MEMBER up to N items of different objects (SEGOBJEX.GFF's item records, each object once, from the FIRSTth on: each its own picture on the ground), into free backpack... |
| `groundfill.sh CYCLES [FIRST_TYPE]` | fill the ground with items (2026-11-09, the picture-cache test): each cycle gives Gerakis (member 0) 12 plain items of new types in memory (giveitems.py), opens the inventory and DROPs each, closes it, waits for the... |
| `guard_start.sh` | the watchdog. Every 20 s: GONE if DOSBox has quit; |
| `healparty.py` | each party member's hit points to their sheet's most (memory only: never save after) |
| `hp.py HP` | every combatant past the party (index 4 and up) to HP hit points, its sheet's most too. |
| `itemedit.py MEMBER SLOT [slot=N] [e=N] [f=N]` | show (and change) the item party member MEMBER has in slot SLOT: its slot byte (+11h), +0Eh (an ability item's amount) and +0Fh (its ability byte, FAh-FFh STR-CHA, or a spell). |
| `itemlists.py` | each party member's three item lists (+08h worn, +0Ah held weapons, +0Ch the backpack) as (item, slot byte, type). |
| `killfoes.py` | kill every foe in memory (aging.kill), not the arena's prisoners. |
| `kinds.py [CREATURE=KIND ...]` | a creature record's monster kind (+16h: 0 people; |
| `kitset.py MEMBER CLASS LEVEL KITBYTE` | the member made a single-class character of CLASS (the sheet's class number) at LEVEL with kit KITBYTE (0 none, 1-3 the class's kits in kitpages.KITS order), and a non-warrior's attack rate (+2Ah 2: the game reads... |
| `known.py MEMBER` | the spells party member MEMBER knows (the known table, low four bits), by number and name |
| `leasts.sh (on the creation screen; ROWS="y ..." to pick rows)` | for each score's square, a right click (lower) then the least the game worked out, then a left click back |
| `leavearena.sh` | right after "Go back to the pens" (arenawaves.sh), before the arena's patience runs out (a few actions): each step first clicks away any message (a box blocks drags as well as clicks), then drags the view (scroll.py,... |
| `levelup.sh` | if CHOOSE A SPELL is up (a preserver's level-up, mid-fight; |
| `loadsave.sh NAME` | start the game (start.sh, or start_recomp.sh with PT_TARGET=recomp) with the save in saves/NAME copied into the game folder (as slot 1), and load it: the title screens clicked past, LOAD SAVED GAME (170, 109), the... |
| `mapshot.py OUT.png [W H]` | a picture of the whole region the party is in, W x H map units (default 1920 x 1536), made by dragging the view across it (scroll.py) and pasting each 320x200 capture (shot.sh) at its camera, the top bar and anything... |
| `markmember.py THING\|none CHANGED` | GHOST_TAB with only THING marked see-through (or none), and GH_CHANGED set to CHANGED (1: DSCLOG's GHOST_UNION draws the whole view at the next step). |
| `memaudit.py` | DOS memory now: the chain from the game's block (each block, owner, size), the upper memory chain from 9FFFh (DSCLOG, the overlay buffer, the see-through tables, the music buffer, free), the game's heap and DSCLOG's... |
| `memberpos.py N` | party member N's figure on screen, to click (its feet x, and y - 12), from its map position and the camera; |
| `memsample.py [LABEL]` | one line of the game's memory: the map's flag, the heap, its free blocks, DOS memory free after the game. |
| `msgbox.sh` | exit 0 if a message waits for a click: the speech box with a portrait at the top (its frame's pixel at 60,3 is 154,154,178) or the grey message window (113,113,138 at 200,50). |
| `npcgear.py` | every creature on the map now (the game's things that are creatures), with the items in its three lists: +08h worn, +0Ah held (what the Look box lists and the game fights with), +0Ch backpack. |
| `openshop.sh` | from the "selling junk" save (saves/selling-junk-user), Kalzith's shop: the eye on him (his figure's square found from memory: his feet less 16), Talk, 1, the box clicked through, 1, the box. |
| `orderwatch.py SECONDS` | fight_on and whose turn, with each new dice-log line, timed every 10 ms (which came first: a blow or the fight's start). |
| `outfitcycle.py MEMBER SLOT N [SECONDS]` | changes MEMBER's outfit N times, as fillcache.py does (the slot byte, +11h, of the item it has in SLOT set to 50, no place, and back), waiting each time for the Loader to dress the figure (its copy of SEGOBJEX.GFF... |
| `pacerec.sh on\|off OUT.mkv` | a recording for docs/steady-pace.gif: pens-after-arena, steady pace on or off, the party walked east and back, recorded at 70 frames a second from the X display (the DOSBox window at 0,0, 320x240) |
| `panel.sh hide\|show` | the combat log panel (bottom right) hidden or shown, by its frame's pixel at 140,150 in the 320x240 window grab (140,125 in the 320x200 capture; |
| `party.py` | each party member's classes and levels, the gladiator flag, the scores the game uses now (the creature record's), and every item with its slot, +0Eh and +0Fh (ability bytes) |
| `passmiss.sh` | in a fight, the party's turns passed through each member's END menu (memberpos.py, E) until a foe misses (the dice log's "-> miss"), then the view dragged and shots taken (missdrag.png, missafter.png). |
| `passn.sh N` | pass N party turns (passuntil.sh's way: a click on the member's figure, the END menu checked by its grey pixels, E), the member's figure brought on screen with scroll.py first when the party stands spread out... |
| `passto.sh N (PASS_LIMIT tries, default 60)` | pass party turns until member N's: a click above the member's figure opens its END menu (the screen's top-left block changes), then E (END TURN); |
| `passuntil.sh N [MAX]` | pass party turns until member N's: a click ON the figure (memberpos.py), the END menu checked by its grey pixels in a shot (over 1300; |
| `pastblock.py save\|cmp FILE` | the 4 KB past GHOST's block (GHOST_SEG + 885 paragraphs), kept or compared |
| `paths.py` | the same paths as env.sh, for the Python tools |
| `picstore.py [check\|dump SLOT\|stale]` | the game's picture store (the 741,376 bytes behind memory handle DS:4C33h) as the Loader can reach it (2026-11-09, logs/2026-11-09-picture-store.md). |
| `pixmatch.py X Y R G B [X Y R G B ...]` | exit 0 if every named pixel of a fresh 320x240 window grab is that colour, within 3 a channel and one row up or down. |
| `playsound.py N` | have DSCLOG play sound N from the map's main loop (its header's SOUND_REQ, +1822): a game sound (0-130) or one of the mod's (140, 141). |
| `pocket.sh MEMBER_X MEMBER_Y NAME [PURSE_X]` | one pocket try: U, the thief's portrait on the USE screen (its position), the purse (157,145, a slow press; |
| `pointer.py [walk\|look\|attack [X Y]]` | the map pointer's mode (DS:11B8h: 1 walk, 2 look (the eye: also talk, use), 4 attack; |
| `poolfree.py [SECONDS]` | the game's picture memory (the blocks at DS:8E94h, 8 bytes each: +0 the bytes free in it (dword), +4 its far pointer; |
| `powers.py` | each party member's known psionic powers (selector 2F0h's segment, +77h + member x 22h + power, bits 3-7: known), by name. |
| `rackcheck.py` | the slave pens' weapon rack (object 2599; |
| `randout.py N [SEED]` | N random outfit changes for member 0: each time one of its worn items (slot under 12) taken off (slot byte +11h set to 50) or put back, waiting for the Loader's copy of SEGOBJEX.GFF to be written; |
| `ravburst.sh NAME SECONDS [X Y W H]` | a burst of window grabs of the running Wake of the Ravager ($WORK/rav.pid's DOSBox), as fast as `import` goes (about 15 a second), into $WORK/burst/NAME-NNN.png, then a sheet of up to 24 of them, evenly spaced,... |
| `ravclick.py X Y [left\|right\|none] [PID]` | Wake of the Ravager's click.py: moves the pointer to game pixel X,Y (320x200) by relative moves until the game's own pointer (DS:A109h x, A10Bh y; |
| `ravcreatures.py [OUT] [PID]` | Wake of the Ravager's creature records (31h bytes each, at the far pointer DS:19C9h; |
| `ravdice.py [--all] SECONDS [OUT]` | the Loader's dice log for Wake of the Ravager (dsloader.ravlog.RavDiceLog: the sequel's layout, its memory read only) attached to the running sequel ($WORK/rav.pid), its lines printed (and appended to OUT) as they... |
| `ravds.py [--fuzzy] HEX...` | Shattered Lands data-segment offsets to Wake of the Ravager's: for each SL instruction using the offset (mov/cmp/les/lea... |
| `ravfight.py [state\|end\|wait N\|cast SPELL_ICON_X SPELL_ICON_Y LEVELS] [PID]` | Wake of the Ravager's fight by its memory. |
| `ravfixes.py [OUT] [--skip=NAME,...]` | a copy of Wake of the Ravager ($RAV, default $WORK/rav) in OUT (default $WORK/ravfix, hard links but for the two files changed and those the game writes) with the mod's bug fixes that carry over unchanged: five of... |
| `ravring.py OUT SECONDS [PID]` | follows Wake of the Ravager's helper (DSCLOG2, header "DSCLOGR1") and appends every new ring entry (192 bytes, DSCLOG's ENTRY LAYOUT) to OUT as a hex line, polling 5 times a second, for SECONDS. |
| `ravscare.sh [FOLDER]` | Scare in Wake of the Ravager's first fight (the Draxans' ambush in Tyr), for the saving throw's fixes: ravstart.sh FOLDER (default $WORK/rav; |
| `ravsites.py [NAME...]` | where Shattered Lands' patch sites (dsloader.gamepatch.PATCHES) are in Wake of the Ravager's DSUN.EXE, by likeness: SL's 64 bytes round each site (the patch's own bytes left out) scored against every place in WotR's... |
| `ravstart.sh [FOLDER]` | Wake of the Ravager in DOSBox (GOG's settings, sound off), from FOLDER (default $WORK/rav; |
| `ravthief.py [MEMBER] [PID]` | Wake of the Ravager's own thief-skill routine (its DSUN.EXE 8C647h, SL's 80240h) run in an emulator (unicorn) on the running game's memory, for party member MEMBER (default 0), once with the game's list of slots that... |
| `rec.py [FIRST LAST]` | the combat records (58 bytes) of creatures FIRST to LAST (default the party, 0-3), hex from +10h, to find a field by comparing what the screen shows |
| `restalarm.sh` | in the fire room (toalarm.sh), rest at the ring (map 1931, 856) with the look pointer until Kurzak calls, then wait there till his patience runs out: the alarm, and a fight with the guards. |
| `restfixmem.py [check\|fix\|undo]` | the rest routine's pass 2 (DSUN.EXE 8066Dh, overlay 5E8h) in the overlay buffer, if loaded: `check` says which version is there (the game's: the effects read before the free cures; |
| `ringrest.sh` | rest at the fire room's ring in pens-fire-count4 (camera 1728,768: the ring at screen 203,88): the eye, a slow press on the ring, the walk arrow back (2026-11-09). |
| `rolog.py [--d20]` | a read-only dice log beside the session's own Loader (2026-11-08): the Loader's describe() and hp_changes() on DSCLOG's entries, from this checkout's dsloader, writing nothing to the game (no attach(): it writes... |
| `route.py TX TY` | walk the party's leader to map position TX, TY over any distance: a path found on the region's walkability grid as the game has it now (live.py's live_map, DS:0556h; |
| `scroll.py DX DY` | drag the map view with the middle mouse button by DX, DY game pixels (the user's advice, 2026-11-01): the way to see past walls, where the view won't scroll by itself. |
| `scrolltest.py [shinobi] [give]` | member 0 made an 8th-level Shinobi (memory only: never save after) and the defilers' scrolls (defilerscrolls.scroll) given to members 0 and 2. |
| `setarrows.py MEMBER N` | the member's quiver stack's count made N, in memory (never save after; |
| `setcount.py [N]` | read (and with N, write) the arena's visit count, the game's number 12 (4: the next trip is Scar's). |
| `setmem.py [hp=M:V psp=M:V status=M:V ruleshi=+N\|-N power=M:P slots=M:L:N]` | the party's HP, PSP and status (creature +0, +2, +1Ch), DSCLOG's rules_hi (the header's +270: +N sets bits, -N clears them; |
| `setpic.py THING PICTURE` | a map thing drawn with another walking picture (memory only, never save) |
| `setup_game.sh` | the game for testing, in $GAME: the GOG installer extracted with innoextract. |
| `setup_guide.sh` | the owner's walkthrough of Shattered Lands, made searchable: from $WORK/guide/kibbitz.html (the owner's saved copy of the page, from the private repository of installation files, $INSTALL, or put there by hand) to... |
| `setup_ravager.sh` | Wake of the Ravager, the sequel, for comparing with Shattered Lands (its code, data and README), in $RAV (default $WORK/rav): the owner's GOG installer, extracted with innoextract. |
| `sheetedit.py MEMBER [levelN=V] [flags\|=V] [flags=V]` | show (and change) party member MEMBER's character sheet: its three classes and levels and its class flags word (+12h; |
| `sheetinfo.py` | each party member's name, classes, levels, race, kits and weapon specs (by name), status (0 New) |
| `sheetscore.py MEMBER [lv=N] [str= dex= con= int= wis= cha=]` | the sheet's first level (+24h) and the creature record's scores (+22h on: what the game's DUAL window reads), then race, classes, levels, alignment and scores. |
| `shot.sh OUT.png` | a screenshot of the game (DOSBox's own capture, Ctrl+F5: the 320x200 picture) |
| `shotinfo.py` | the camera, member 2's map and screen place, whose turn it is, and each foe on the screen with its place and distance (for a shot: click about 10 pixels above the foe's feet). |
| `shut.py` | Pehtucl's chest (object 1568) given the shut type (pehtuclchest.SHUT_TYPE, 67h) in memory, as a new game makes it: the pens-new-chest save's chest was made before the shut type. |
| `slotcheck.py [LABEL]` | every map thing with a picture slot (+0Fh) finds its own picture's number in that slot (+18h, the walking picture, or +18h + 1 for its fighting one), and every wall's slot is taken: the check that reusing slots... |
| `slotcount.py [LABEL]` | one line: the leader's place, the game's picture slots taken (of 300), the store's end (of 741,376), how many are in memory and STALE, and with DSCLOG's PIC_REUSE how many slots it has reused (pf_count, from a symbol... |
| `soundmatch.py RAW START END WAV...` | in DOSBox's recorded output (RAW: 16-bit stereo at 44100 Hz, from start.sh with PT_AUDIO set; |
| `spellsetup.py [MEMBER=LEVEL ...] [hp=N] [SPELL ...]` | memory only, never save after. Teaches each MEMBER the spells (the known byte at segment DS-B56h, 168h + member x 8Ah + spell), fills its wizard and priest slots (9 at every level, DS:4B08h / 4B11h + 1Eh x member),... |
| `start.sh` | Xvfb :55, the Loader's patched game in DOSBox as the Loader starts it (the repository's current code: rebuild = restart), and the Loader's dice log ($WORK/dice.txt). |
| `start_recomp.sh` | the game on Dark Sun Recompiled ($DSUN, its build of the mod) instead of DOSBox, with the Loader's patched game prepared as start.sh does and the dice log attached. |
| `state.py` | one line of the game's state: fight (fight_on, whose turn), region, the leader's map position, the camera, and the flags named on the command line (state.py 11 505) |
| `stepfight.sh` | from the arena gate, clicks south until the fight is on (topartyfight.sh's last loop) |
| `symread.py` | Read DSCLOG variables by name in the running game: `python3 symread.py NAME [NAME...]` (each's first 4 bytes, hex), from a symbol map of obsidian-edition/dos/dsclog.asm as built (the tree's DSCLOG.EXE). |
| `teleport.py X Y CX CY` | the party (map objects 0-3) put at map X, Y and the camera at CX, CY, in memory (DS:669Dh + 32n, DS:1178h); |
| `thief.py MEMBER LEVEL \| MEMBER off` | a party member made a thief of LEVEL in memory (class 17 in a free class place of the sheet, its level, the thief flag 400h), or no thief (off). |
| `thingsfree.py [LABEL]` | the game's dynamic things (objects 320-519, handed out from a free list): how many are free (the free list walked), the game's count out (DS:4C48h), and how many item lists the people on the map hold (worn, held,... |
| `toalarm.sh` | from pens-after-scar (loaded here, DOSBox's sound recorded to $WORK/audio.raw), Cilla's thief level raised to 12 in memory (she hides at 95: never save after), then through Kurzak's entryway and the east passage to... |
| `toarena.sh` | after Kurzak's call, from the fire room: up to the arena (route.py through his entryway, his stop, the corridor at y 408), then a click into the gap south of (1816, 408): "Enter the arena?" (answer Y yourself) |
| `tofight.sh N` | fountain-user loaded, Ester's arrows made N, the ambush started, every foe Paralyzed, and on to Ester's turn (logs/2026-11-14-quiver-turn.md). |
| `topartyfight.sh` | a fresh DOSBox at its title: START GAME, through the opening show fight, the party gathered (6), the panel hidden (L), stepped forward until the arena fight is on; |
| `toturn.sh N` | the party's turns played until member N's (state.py's turn): Tab + Return for each member, and E when the same member's turn is still up after that (no Move left: its END menu, wherever the game puts it, waits; |
| `turnsetup.py MEMBER LEVEL [COMBATANT=HD ...]` | memory only, never save after (2026-11-09). |
| `turnwatch.py MEMBER SECONDS` | polls whose turn it is and the member's turn bytes every 5 ms, printing each change with its time: +181h attacks made this round (63h = spent, the turn ends), +1ABh attack commands, +1D5h, +5Bh (the segment DS -... |
| `untilturn.sh NAME` | play party turns (Tab + Return) until NAME's turn comes, messages clicked away. |
| `viewto.py X Y` | drag the view (scroll.py, the middle button) until map point X, Y is near the screen's centre, so a far spot can be clicked: the party then walks there by itself, finding its own way (it does over a whole region, if... |
| `walkprobe.py N X Y DIR [SECS]` | a click at screen X, Y (game pixels), then for SECS seconds (default 6) as often as it can: party member N's map position, whose turn it is (the game's word), DSCLOG's STEALTH word (header +204: bit N set while N is... |
| `walktime.py N X Y [DIR]` | a click at screen X, Y (game pixels), then party member N's map position every 50 ms until it has stood still for 1.5 s: each step's time (the walking pace), and with DIR a window grab at each step (DIR/wNN.png) |
| `walkto.py TX TY [TRIES]` | walk the party's leader to map position TX, TY (16ths of a square, as party_position) with left clicks on the map in Walk mode (the plain arrow pointer; |
