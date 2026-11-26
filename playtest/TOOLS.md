# The playtest tools

Every tool in `playtest/`, with the first sentence of its own header comment (`python3 tools_index.py` writes this page again from the files: run it after adding or changing a tool). `env.sh` and `live.py` are the others' shared set-up. How to use them is in [PLAYTESTING.md](PLAYTESTING.md).

| Tool | What it does |
|---|---|
| `acs.py` | each combatant's AC as the game counts it (gd.counted_ac), to hold against the dice log's "target AC" |
| `addeffect.py OWNER EFFECT [SPELL] [CHARGES]` | give combatant OWNER (0-3 the party) the effect EFFECT (35 Poisoned, 13 Diseased, 34 Paralyzed...) in memory, untimed. |
| `altflag.py [latency N \| watch SECONDS]` | the BIOS's shift flags (0:0417h; Alt is bit 3, Ctrl bit 2, the Shifts bits 0 and 1), which the Loader reads for "show what can be used" (dsloader/usable.py). |
| `ammodump.py` | Jenna's and Ester's quiver, bow and backpack item records (item number, list, address, the record in hex: count +2, link +4, type +0Ah, name +12h, plus +14h, slot +11h). |
| `arenatrip.sh` | from pens-after-scar, rest in the fire room till Kurzak calls, answer at once, and count the game's free things (thingsfree.py) there and on arriving in the arena. |
| `arenawaves.sh` | with the arena's first fight on, fight every wave (fightout.sh) and click away the messages between them, until the YES/NO question ("Yell something back at the Announcer?"), which it answers N. |
| `award.py N` | N XP as the game's award gives it: each member's sheet XP += N / its classes (a human: N) |
| `bashloop.sh N` | use Pehtucl's chest from beside it and answer Y to "Bash it open?" until the lock breaks (N tries) |
| `bigthings.py` | the map's things with their walking picture (+18h), its frames' most runs (from the Loader's SEGOBJEX.GFF) and where they stand, the most runs first: for a test of drawing a big frame |
| `bodyitems.py` | each Dead Body on the map (object 1101 or the thri-kreen's 2666), its things: item, name, type, plus, power, value, name number and +02h, and the type's worn place, weight and flags. |
| `boxclick.sh` | click a waiting message away by clicking ON it (160, 20, the speech box at the top): a click wherever the pointer happens to be (after a drag, say) didn't always count (2026-11-01) |
| `buildcheck.py [NAME...]` | checks the DSCLOG running in DOSBox is the build in obsidian-edition/dos. |
| `cachelist.py [all]` | the game's picture cache: the slots taken, the STALE ones, and with "all" every slot. |
| `camera.py [X Y]` | read the camera (the view's top-left, DS:1178h), or set it to X, Y (map units) to look somewhere the view won't scroll to by itself (it does not follow the leader everywhere) |
| `canuse.py MEMBER TYPE...` | whether the kit rules (restrict.kit_forbids) let party member MEMBER use each item type, and pick it as a weapon spec |
| `carried.py NAME` | what the creature named NAME carries, list by list: item, name as the game shows it, type, slot, value, plus, name entry and the +02h word (2026-11-11: guavas named "Brgnd.Chst Armor"). |
| `chartran.sh SAVE.SAV OUTDIR [DEBUG]` | runs Wake of the Ravager's own transfer utility (CHARTRAN.EXE, from $RAV, setup_ravager.sh) on one Shattered Lands save in a headless DOSBox of its own (not the game's: no Loader, no lock needed), and leaves in... |
| `chestuse.sh [y\|n]` | uses Pehtucl's chest from a square beside it (ROUTE.md, Pehtucl's chest): the eye set with pointer.py look, a slow press on the chest (163,70), its look box's third button (236,101), then the walk arrow back. |
| `click.py X Y [left\|right\|none]` | move the game's pointer to game pixel X,Y (320x200) and click. |
| `codepatch.py [SECONDS] [game]` | does a write to CODE in the game's memory take effect at once? (The DOSBox-X experiment, 2026-11-18: the Loader patches code while the game runs, and a write that doesn't go through DOSBox's own page handlers, as one... |
| `creationscores.py` | the creation screen's scores, classes and race, and the least and most the game last worked out |
| `dacwatch.py SECONDS` | DSCLOG's copy of the palette (TSR_DAC) watched: each change, hashed whole and for colours 16-223 only. |
| `dbxadopt.sh` | makes the kit's tools follow the game the Loader itself started (its window's Start the game, `launch` or `play`) rather than one of the kit's start scripts: it writes that game's pid, read from the Loader's lock... |
| `darkfix_apply.py GPLDATA_IN GPLDATA_OUT FIXES_DIR` | put OpenDS darkfix-ds1 GPL repairs (every fix .py in FIXES_DIR, a checkout of their ds1-patch/fixes) into a copy of GPLDATA.GFF, with our own code: each fix's REPAIRS list is read by AST, never imported or run, and... |
| `dec.py SCRIPT LO HI` | decode GPL script SCRIPT (the game's own GPLDATA.GFF, $DS_GAME) from offset LO to HI (hex): each command's offset, number and arguments. |
| `dismiss.sh [N]` | click away up to N (default 6) waiting messages (msgbox.sh), then print the dice log's last lines. |
| `doorpath.py TC TR` | the shortest way from the leader to square (TC, TR) on the live grid, through closed doors too (live 192+ where the region file has a doorway); |
| `doors.py` | the closed doors and gates on the edge of the area the party can reach now: squares the live grid blocks (192 and up) where the region file's grid has a doorway (below 192). |
| `doorwatch.py SECONDS` | Kurzak's door and the two who use it, printed at each change (every half second). |
| `dosmem.py [PID]` | DOS memory in any running DOSBox, no helper needed (so either game, modded or not, or Wake of the Ravager): every block of the conventional chain and the upper memory chain (owner's name, size), the largest free... |
| `dosboxx_memtest.py DOSBOX-X [normal]` | says whether a second program can read and write DOSBox-X's memory file while DOSBox-X runs, without the game: the check to run on Windows and on macOS, where the mod's DOSBox-X engine is untested. |
| `drawlist.py [all]` | the game's draw list (far pointer DS:6690h, count DS:1F72h; |
| `dsword.py ADDR [VALUE]` | the game's DS word at ADDR (hex), or set it (memory only). |
| `effects.py` | every active effect (owner, caster, effect id), its charges and game seconds left (60 a round), as the Loader reads them. |
| `f10watch.py MEMBER SECONDS` | follows a party member's turn for F10 tests, printing each change with its time: whose turn (DS:4979h), the member's turn flags (37BD:01D5h, bit 0 "can walk"), movement points (+22Bh), swings (+181h) and attack... |
| `figcheck.py [LABEL]` | whether the party's figures are drawn on the map. |
| `fightout.sh [MAX]` | finish a fight the game's own way, so its scripts see each kill: every foe to 1 HP (hp.py 1), then on each party turn Tab (the mod picks the nearest enemy) + Return (attacks). |
| `figwatch.py SECONDS [EVERY] [TAG]` | passive watch for the party's figures (no writes). |
| `fillcache.py MEMBER SLOT UNTIL` | fills the game's picture slots (cachelist.py) the way a change of gear does, fast. |
| `foepos.py` | each combatant past the party: its name, HP and figure on screen (feet x, y - 10) |
| `foeset.py` | foeset.py [COMBATANT [race=R] [cls=A,B,C] [lv=A,B,C] [mr=N] [hp=N] [int=N] [name=S] [eff=ID[:SPELL[:AMOUNT]]] ...]: memory only, never save after (2026-11-09, logs/2026-11-09-group-3.md). |
| `follow.py OBJECT [ROUNDS]` | keep the party within a few squares of a map object that walks (an escort). |
| `framerate.py SECONDS [X1 X2 Y]` | walks the party back and forth between screen points (X1,Y) and (X2,Y) for SECONDS and reports the frame rate, a second at a time and in all. |
| `gamekeys.py [dis START [LEN]]` | the keys the game itself acts on with the map up, read from DSUN.EXE ($DS_GAME): the root's table at 1BC5Bh (26 keys, then their handlers), the map overlay's at 71C1Bh (overlay 4272h: 33 keys) and that overlay's jump... |
| `gearpoll.py` | watches the Loader's creation gear reach the roster, for 110 s. |
| `ghostchk.py [THING...]` | DSCLOG's see-through figures: its block (GHOST_SEG), GHOST_ON, the first REP and BLEND bytes and GHOST_TAB; |
| `ghostclear.py [TRIALS]` | whether GHOST_UNION clears a see-through mark within an enemy turn. |
| `ghostturn.py` | in a fight, GHOST_UNION's whole view on a GHOST_TAB change (GH_CHANGED) in the enemies' turns. |
| `ghostwatch.py SECONDS` | DSCLOG's GHOST_ON and its palette copy watched every 20 ms: each change of GHOST_ON, and how many samples had it 0. |
| `giveitems.py MEMBER N [FIRST]` | gives party member MEMBER up to N items of different objects in memory (never save after). |
| `groundfill.sh CYCLES [FIRST_TYPE]` | fill the ground with items (2026-11-09, the picture-cache test). |
| `guard_start.sh` | the watchdog. Every 20 s: GONE if DOSBox has quit; |
| `healparty.py` | each party member's hit points to their sheet's most (memory only: never save after) |
| `hitcheck.py [ATTACKER]` | the chance to hit before the swing (dsloader/hitchance.py), read-only: for whoever's turn it is (or combatant ATTACKER) against every enemy, what the Loader would say on the "Chosen with Tab" line (without the dice... |
| `hovercost.py SECONDS \| loader` | what the chance to hit under the pointer (dsloader/hover.py) costs. |
| `hoverhit.sh C [attack]` | the chance to hit under the pointer against the swing itself. |
| `hoverlabel.py [X Y \| foe C] [watch SECONDS]` | the chance to hit under the pointer (dsloader/hover.py) as the game has it: moves the pointer (no click) to game pixel X, Y, or onto enemy combatant C's figure (10 pixels above its feet), then prints the pointer, its... |
| `hp.py HP` | every combatant past the party (index 4 and up) to HP hit points, its sheet's most too. |
| `itemedit.py MEMBER SLOT [slot=N] [e=N] [f=N]` | show (and change) the item party member MEMBER has in slot SLOT: its slot byte (+11h), +0Eh (an ability item's amount) and +0Fh (its ability byte, FAh-FFh STR-CHA, or a spell). |
| `itemlists.py` | each party member's three item lists (+08h worn, +0Ah held weapons, +0Ch the backpack) as (item, slot byte, type). |
| `killfoes.py` | kill every foe in memory (aging.kill), not the arena's prisoners. |
| `kinds.py [CREATURE=KIND ...]` | a creature record's monster kind (+16h: 0 people; |
| `kitset.py MEMBER CLASS LEVEL KITBYTE` | the member made a single-class character of CLASS (the sheet's class number) at LEVEL with kit KITBYTE (0 none, 1-3 the class's kits in kitpages.KITS order). |
| `known.py MEMBER` | the spells party member MEMBER knows (the known table, low four bits), by number and name |
| `leasts.sh (on the creation screen; ROWS="y ..." to pick rows)` | for each score's square, a right click (lower) then the least the game worked out, then a left click back |
| `leavearena.sh` | takes the party from the arena to the pens, right after "Go back to the pens" (arenawaves.sh), before the arena's patience runs out (a few actions). |
| `levelup.sh` | if CHOOSE A SPELL is up (a preserver's level-up, mid-fight; |
| `loadquick.sh [ROW]` | start the game (start.sh) and load a save of the QUICK page (SAVQnn.SAV, the quick saves and autosaves: dsloader/quicksave.py) that is in the game folder already, from the main menu: LOAD SAVED GAME (170, 109), the... |
| `loadsave.sh NAME` | start the game (start.sh, or start_recomp.sh with PT_TARGET=recomp) with the save in saves/NAME copied into the game folder (as slot 1), and load it. |
| `mapshot.py OUT.png [W H]` | a picture of the whole region the party is in, W x H map units (default 1920 x 1536). |
| `markmember.py THING\|none CHANGED` | GHOST_TAB with only THING marked see-through (or none), and GH_CHANGED set to CHANGED (1: DSCLOG's GHOST_UNION draws the whole view at the next step). |
| `memaudit.py` | DOS memory now: every block, its owner and size, and DSCLOG's header figures. |
| `memberpos.py N` | party member N's figure on screen, to click (its feet x, and y - 12), from its map position and the camera; |
| `memsample.py [LABEL]` | one line of the game's memory: the map's flag, the heap, its free blocks, DOS memory free after the game. |
| `movestate.py [R]` | in a fight, whose turn it is, its square, the movement points it has left (37BD:022Bh + creature x 2) and its turn's flags (37BD:01D5h; |
| `msgbox.sh` | exit 0 if a message waits for a click: the speech box with a portrait at the top (its frame's pixel at 60,3 is 154,154,178) or the grey message window (113,113,138 at 200,50). |
| `npcgear.py` | every creature on the map now (the game's things that are creatures), with the items in its three lists: +08h worn, +0Ah held (what the Look box lists and the game fights with), +0Ch backpack. |
| `openshop.sh` | from the "selling junk" save (saves/selling-junk-user), Kalzith's shop: the eye on him (his figure's square found from memory: his feet less 16), Talk, 1, the box clicked through, 1, the box. |
| `orderwatch.py SECONDS` | fight_on and whose turn, with each new dice-log line, timed every 10 ms (which came first: a blow or the fight's start). |
| `outfitcycle.py MEMBER SLOT N [SECONDS]` | changes MEMBER's outfit N times and prints the picture store after each. |
| `pacerec.sh on\|off OUT.mkv` | a recording for docs/steady-pace.gif: pens-after-arena, steady pace on or off, the party walked east and back, recorded at 70 frames a second from the X display (the DOSBox window at 0,0, 320x240) |
| `panel.sh hide\|show` | the combat log panel (bottom right) hidden or shown, by its frame's pixel at 140,150 in the 320x240 window grab (140,125 in the 320x200 capture; |
| `party.py` | each party member's classes and levels, the gladiator flag, the scores the game uses now (the creature record's), and every item with its slot, +0Eh and +0Fh (ability bytes) |
| `passmiss.sh` | in a fight, the party's turns passed through each member's END menu (memberpos.py, E) until a foe misses (the dice log's "-> miss"), then the view dragged and shots taken (missdrag.png, missafter.png). |
| `passn.sh N` | pass N party turns, passuntil.sh's way (a click on the member's figure, the END menu checked by its grey pixels, E). |
| `passto.sh N (PASS_LIMIT tries, default 60)` | pass party turns until member N's: a click above the member's figure opens its END menu (the screen's top-left block changes), then E (END TURN); |
| `passuntil.sh N [MAX]` | pass party turns until member N's: a click ON the figure (memberpos.py), the END menu checked by its grey pixels in a shot (over 1300; |
| `pastblock.py save\|cmp FILE` | the 4 KB past GHOST's block (GHOST_SEG + 885 paragraphs), kept or compared |
| `paths.py` | the same paths as env.sh, for the Python tools |
| `picmove.py DX DY` | move the hand DX, DY screen pixels (xdotool, relative: DOSBox has the mouse) and print how far the game's pointer (DS:A133, game pixels) went. |
| `picpattern.sh WHERE:SCALE:PICTURE ...` | the Loader's display settings (launch.display_lines) tried in a DOSBox of its own, without the game and without the DOSBox lock: a 33-byte program puts a pattern on the game's screen mode (13h, 320x200) and waits. |
| `picstart.sh PICTURE [SCALE] [OUT_DIR]` | the game started with one of the Loader's pictures (plain, scanlines, tv, sharp) in a window SCALE times the game's (default 3), NOT the kit's 320x240 start: pens-after-arena loaded by the pointer (click.py), then... |
| `picstore.py [check\|dump SLOT\|stale]` | the game's picture store (the 741,376 bytes behind memory handle DS:4C33h) as the Loader can reach it (2026-11-09, logs/2026-11-09-picture-store.md). |
| `pixmatch.py X Y R G B [X Y R G B ...]` | exit 0 if every named pixel of a fresh 320x240 window grab is that colour, within 3 a channel and one row up or down. |
| `placefoe.py THING DX DY [MEMBER]` | map thing THING (a foe's combatant number) put DX, DY squares from party member MEMBER (default 1) in memory (DS:669Dh + 20h a thing, in sixteenths): a foe beside a member for a melee test, or two squares off for a... |
| `playsound.py N` | have DSCLOG play sound N from the map's main loop (its header's SOUND_REQ, +1822): a game sound (0-130) or one of the mod's (140, 141). |
| `pocket.sh MEMBER_X MEMBER_Y NAME [PURSE_X]` | one pocket try: U, the thief's portrait on the USE screen (its position), the purse (157,145, a slow press; |
| `pointer.py [walk\|look\|attack [X Y]]` | the map pointer's mode (DS:11B8h: 1 walk, 2 look (the eye: also talk, use), 4 attack; |
| `poolfree.py [SECONDS]` | the game's picture memory (the blocks at DS:8E94h, 8 bytes each: +0 the bytes free in it (dword), +4 its far pointer; |
| `powers.py` | each party member's known psionic powers (selector 2F0h's segment, +77h + member x 22h + power, bits 3-7: known), by name. |
| `qsave.py SLOT [NAME] \| load \| state` | ask DSCLOG for a save by the game's own routine (SAVE_REQ, the header's +1886: dsloader/quicksave.py), as the Loader's quick save does, and say what came of it and how long it took (seconds of this machine's clock,... |
| `rackcheck.py` | the slave pens' weapon rack (object 2599; |
| `randout.py N [SEED]` | N random outfit changes for member 0: each time one of its worn items (slot under 12) taken off (slot byte +11h set to 50) or put back, waiting for the Loader's copy of SEGOBJEX.GFF to be written; |
| `ravburst.sh NAME SECONDS [X Y W H]` | a burst of window grabs of the running Wake of the Ravager ($WORK/rav.pid's DOSBox), as fast as `import` goes (about 15 a second), into $WORK/burst/NAME-NNN.png, then a sheet of up to 24 of them, evenly spaced,... |
| `ravclick.py X Y [left\|right\|none] [PID]` | Wake of the Ravager's click.py: moves the pointer to game pixel X,Y (320x200) by relative moves until the game's own pointer (DS:A109h x, A10Bh y; |
| `ravcreation.py [ROLLS] [RULES] [PID]` | Wake of the Ravager's creation screen checked, the die pressed ROLLS times (default 20; |
| `ravcreation.sh [ROLLS]` | Wake of the Ravager started as the Loader starts it (ravstart.sh, RAV_LOADER=1, to the title menu), CREATE CHARACTERS (160,92), a right-click on the roster's first slot (70,56), NEW (110,57), then ravcreation.py... |
| `ravcreatures.py [OUT] [PID]` | Wake of the Ravager's creature records (31h bytes each, at the far pointer DS:19C9h; |
| `ravdice.py [--all] SECONDS [OUT]` | the Loader's dice log for Wake of the Ravager (dsloader.ravlog.RavDiceLog: the sequel's layout, its memory read only) attached to the running sequel ($WORK/rav.pid), its lines printed (and appended to OUT) as they... |
| `ravds.py [--fuzzy] HEX...` | Shattered Lands data-segment offsets to Wake of the Ravager's: for each SL instruction using the offset (mov/cmp/les/lea... |
| `ravfight.py [state\|end\|wait N\|until N\|cast X Y LEVELS\|attack\|fight [S]\|tabfight [S]]` | Wake of the Ravager's fight by its memory. `tabfight`: Tab (the nearest enemy) and Return (attack) on every party turn, which reaches foes indoors where `fight` stops at "no foe on screen". |
| `ravgo.py [x\|y TARGET]... [PID]` | Wake of the Ravager's leader walked with the arrow keys to each world x or y in turn (stops a leg at a wall); prints where it ends. |
| `ravfirst.py` | a sequel party member's wizard spells and psionic powers as the game holds them, and DSCLOG2's first spells' and powers' counts (the running sequel, $WORK/rav.pid; |
| `ravfixes.py [OUT] [--skip=NAME,...]` | a copy of Wake of the Ravager ($RAV, default $WORK/rav) in OUT (default $WORK/ravfix, hard links but for the two files changed and those the game writes) with the mod's bug fixes that carry over unchanged: five of... |
| `ravhold.sh [FOLDER]` | a real Hold Person in Wake of the Ravager's first fight (the Draxans' ambush in Tyr), for the held-target rule (DSCLOG2's HELD_HIT, HELD_DAMAGE): ravstart.sh FOLDER (default $WORK/rav; |
| `ravitems.py N... [--worn]` | Wake of the Ravager's combatant N's items, as its helper reads them: the item number, type, worn slot (+13h), plus (+16h), power (the word at +10h) and the type's material (+4), flags (+0) and armour byte (+0Bh). |
| `ravkeys.py` | R, F10 and Alt in the running sequel ($WORK/rav.pid): DSCLOG2's words for them and the game's. |
| `ravkits.py` | the kits in the running sequel ($WORK/rav.pid; |
| `ravknow.py SPELL [LEVEL]` | a test edit (never saved): Wake of the Ravager's first party member (Ar'anda in the opening party; |
| `ravlevel.py` | the level cap by XP in the running sequel ($WORK/rav.pid; |
| `ravload.sh NAME [FOLDER]` | Wake of the Ravager from the save in saves/NAME (SAVE01.SAV, CHARSAVE.GFF, DARKSAVE.GFF copied into FOLDER, default $WORK/rav, as slot 1), started as the Loader starts it (RAV_LOADER=1; |
| `ravloot.py` | looting with T, selling with S and M/U/I in the running sequel ($WORK/rav.pid): DSCLOG2's LOOT_KEY and SELL_KEY fields (its header's +1846 to +1859, DSCLOG's), the shop loop's passes and OVERHEAD (from `nasm -l`'s... |
| `ravquick.py` | the quick saves in the running sequel ($WORK/rav.pid): DSCLOG2's QUICK SAVES (its header's +1904 on, MAIN_TICKS at +260) and the game's words the Loader writes for them. |
| `ravring.py OUT SECONDS [PID]` | follows Wake of the Ravager's helper (DSCLOG2, header "DSCLOGR1") and appends every new ring entry (192 bytes, DSCLOG's ENTRY LAYOUT) to OUT as a hex line, polling 5 times a second, for SECONDS. |
| `ravscare.sh [FOLDER]` | Scare in Wake of the Ravager's first fight (the Draxans' ambush in Tyr), for the saving throw's fixes: ravstart.sh FOLDER (default $WORK/rav; |
| `ravshop.py CMD ...` | Wake of the Ravager's shops and scrolls for a test (run from playtest/; |
| `ravsites.py [NAME...]` | where Shattered Lands' patch sites (dsloader.gamepatch.PATCHES) are in Wake of the Ravager's DSUN.EXE, by likeness: SL's 64 bytes round each site (the patch's own bytes left out) scored against every place in WotR's... |
| `ravspecs.py [MEMBER...\|check]` | the weapon specs of the running sequel's party and DSCLOG2's WEAPON PICKS' counts, read only. |
| `ravstart.sh [FOLDER]` | Wake of the Ravager in DOSBox (GOG's settings, sound off), from FOLDER (default $WORK/rav; |
| `ravstore.py [roll\|gear]` | STORE and RECALL and the fuller starting gear in the running sequel ($WORK/rav.pid). |
| `ravtab.py` | the state of choosing an enemy with Tab in the running sequel ($WORK/rav.pid; |
| `ravtext.py [N]` | Wake of the Ravager's text buffer (DSCLOG2's TEXT, sites 93 and 94): the last N records (default 40) the dialogue window's input and the message box left in it (kind 0 a reply, 1 a portrait and its number, 2 text, 3... |
| `ravthief.py [MEMBER] [PID]` | Wake of the Ravager's own thief-skill routine (its DSUN.EXE 8C647h, SL's 80240h) run in an emulator (unicorn) on the running game's memory, for party member MEMBER (default 0), once with the game's list of slots that... |
| `ravtone.py [warm\|neutral\|show] [FLAG]` | Wake of the Ravager wall shadows' tone (DSCLOG2's WS_GAIN, header + 5F8Bh) swapped in guest memory, DARK made again; |
| `ravxfer_check.py SAVE.SAV [SAVE.SAV...]` | the Loader's party transfer (dsloader/ravtransfer.py) set against SSI's own (CHARTRAN.EXE, through chartran.sh) on each Shattered Lands save: every roster chunk the two write (CHAR, CACT, SPST, PSST, PSIN) compared,... |
| `rec.py [FIRST LAST]` | the combat records (58 bytes) of creatures FIRST to LAST (default the party, 0-3), hex from +10h, to find a field by comparing what the screen shows |
| `restalarm.sh` | in the fire room (toalarm.sh), rest at the ring (map 1931, 856) with the look pointer until Kurzak calls, then wait there till his patience runs out: the alarm, and a fight with the guards. |
| `restfixmem.py [check\|fix\|undo]` | the rest routine's pass 2 (DSUN.EXE 8066Dh, overlay 5E8h) in the overlay buffer, if loaded: `check` says which version is there (the game's: the effects read before the free cures; |
| `ringall.py [N \| all \| still \| clear] [KIND]` | for measuring the rings' cost (framerate.py): a ring (DSCLOG's RING_TAB, kind 1) under every one of the game's things on the screen now, whatever it is (N: under the N nearest the screen's middle; |
| `ringrest.sh` | rest at the fire room's ring in pens-fire-count4 (camera 1728,768: the ring at screen 203,88): the eye, a slow press on the ring, the walk arrow back (2026-11-09). |
| `rolog.py [--d20]` | a read-only dice log beside the session's own Loader (2026-11-08). |
| `route.py TX TY` | walk the party's leader to map position TX, TY over any distance: a path found on the region's walkability grid as the game has it now (live.py's live_map, DS:0556h; |
| `savediff.py A.SAV B.SAV [-v]` | two saves (or any two GFF files) compared chunk by chunk (dsloader/gff.py's read_gff): the chunks only one has, and for each chunk both have that differs, its size in each and how many bytes differ (with -v, the... |
| `scroll.py DX DY` | drag the map view with the middle mouse button by DX, DY game pixels (the user's advice, 2026-11-01): the way to see past walls, where the view won't scroll by itself. |
| `scrolltest.py [shinobi] [give]` | member 0 made an 8th-level Shinobi (memory only: never save after) and the defilers' scrolls (defilerscrolls.scroll) given to members 0 and 2. |
| `setarrows.py MEMBER N` | the member's quiver stack's count made N, in memory (never save after; |
| `setcount.py [N]` | read (and with N, write) the arena's visit count, the game's number 12 (4: the next trip is Scar's). |
| `setitem.py ITEM TYPE\|obj=N\|rec=HEX` | makes item ITEM (its number in the item table) a plain item of type TYPE in memory. |
| `setmem.py [hp=M:V psp=M:V status=M:V ruleshi=+N\|-N power=M:P slots=M:L:N]` | the party's HP, PSP and status (creature +0, +2, +1Ch), DSCLOG's rules_hi (the header's +270: +N sets bits, -N clears them; |
| `setpic.py THING PICTURE` | a map thing drawn with another walking picture (memory only, never save) |
| `setup_game.sh` | the game for testing, in $GAME: the GOG installer extracted with innoextract. |
| `setup_guide.sh` | the owner's walkthroughs made searchable. |
| `setup_ravager.sh` | Wake of the Ravager, the sequel, for comparing with Shattered Lands (its code, data and README), in $RAV (default $WORK/rav): the owner's GOG installer, extracted with innoextract. |
| `sheetedit.py MEMBER [levelN=V] [flags\|=V] [flags=V]` | show (and change) party member MEMBER's character sheet: its three classes and levels and its class flags word (+12h; |
| `sheetinfo.py` | each party member's name, classes, levels, race, kits and weapon specs (by name), status (0 New) |
| `sheetscore.py MEMBER [lv=N] [str= dex= con= int= wis= cha=]` | the sheet's first level (+24h) and the creature record's scores (+22h on: what the game's DUAL window reads), then race, classes, levels, alignment and scores. |
| `shot.sh OUT.png` | a screenshot of the game (DOSBox's own capture, Ctrl+F5: the 320x200 picture) |
| `shotinfo.py` | the camera, member 2's map and screen place, whose turn it is, and each foe on the screen with its place and distance (for a shot: click about 10 pixels above the foe's feet). |
| `shut.py` | Pehtucl's chest (object 1568) given the shut type (pehtuclchest.SHUT_TYPE, 67h) in memory, as a new game makes it: the pens-new-chest save's chest was made before the shut type. |
| `slotcheck.py [LABEL]` | every map thing with a picture slot (+0Fh) finds its own picture's number in that slot (+18h, the walking picture, or +18h + 1 for its fighting one), and every wall's slot is taken. |
| `slotcount.py [LABEL]` | one line: the leader's place, the game's picture slots taken (of 300), the store's end (of 741,376), how many are in memory and STALE, and with DSCLOG's PIC_REUSE how many slots it has reused. |
| `soundmatch.py RAW START END WAV...` | in DOSBox's recorded output (RAW: 16-bit stereo at 44100 Hz, from start.sh with PT_AUDIO set; |
| `specset.py MEMBER KIND...` | party member MEMBER's weapon specs made KIND... |
| `spellsetup.py [MEMBER=LEVEL ...] [hp=N] [SPELL ...]` | teaches each MEMBER the spells, fills its slots and sets its casting classes to LEVEL, in memory (never save after). |
| `squarecost.py LEGS COL1 ROW COL2 [POINTS]` | what a walk costs in a fight, for the squares in reach: on a party member's turn it walks the member along row ROW between columns COL1 and COL2, LEGS times, its points set to POINTS (250) before each leg (a test's... |
| `squaresweep.py POINTS [all\|edge\|out][here] [MAX]` | the Loader's squares in reach (dsloader/squares.py) against the game, on a party member's turn in a fight, from where its turn began. |
| `squarewalk.py COL ROW [POINTS]` | on a party member's turn in a fight, click the middle of walk-map square COL,ROW with whatever pointer is up (pointer.py walk first) and say where the member stopped and what movement it has left. |
| `start.sh` | Xvfb :55, the Loader's patched game in DOSBox as the Loader starts it (the repository's current code: rebuild = restart), and the Loader's dice log ($WORK/dice.txt). |
| `start_dosboxx.sh DOSBOX-X [name=value ...]` | the mod in DOSBox-X (the Options tab's other engine: dsloader/dosboxx.py), a game of its own beside the shared one, for the kit's tools. |
| `start_recomp.sh` | the game on Dark Sun Recompiled ($DSUN, its build of the mod) instead of DOSBox, with the Loader's patched game prepared as start.sh does and the dice log attached. |
| `start_stock.sh [GAMEDIR]` | the stock game (no Loader, no dice log) in plain DOSBox on :55, from GAMEDIR (default $WORK/darkfix-inst: a copy of inst with OpenDS's darkfix applied by darkfix_apply.py). |
| `state.py` | one line of the game's state: fight (fight_on, whose turn), region, the leader's map position, the camera, and the flags named on the command line (state.py 11 505) |
| `stepfight.sh` | from the arena gate, clicks south until the fight is on (topartyfight.sh's last loop) |
| `symread.py` | Read DSCLOG variables by name in the running game: `python3 symread.py NAME [NAME...]` (each's first 4 bytes, hex), from a symbol map of obsidian-edition/dos/dsclog.asm as built (the tree's DSCLOG.EXE). |
| `tabhit.sh [TABS [nohit]]` | the chance to hit before the swing against the swing itself. |
| `teleport.py X Y CX CY` | the party (map objects 0-3) put at map X, Y and the camera at CX, CY, in memory (DS:669Dh + 32n, DS:1178h); |
| `thief.py MEMBER LEVEL \| MEMBER off` | a party member made a thief of LEVEL in memory (class 17 in a free class place of the sheet, its level, the thief flag 400h), or no thief (off). |
| `thingsfree.py [LABEL]` | the game's dynamic things (objects 320-519, handed out from a free list). |
| `toalarm.sh` | from pens-after-scar to the fire room (1896, 856), through Kurzak's entryway and the east passage. |
| `toarena.sh` | after Kurzak's call, from the fire room: up to the arena (route.py through his entryway, his stop, the corridor at y 408), then a click into the gap south of (1816, 408): "Enter the arena?" (answer Y yourself) |
| `tofight.sh N` | fountain-user loaded, Ester's arrows made N, the ambush started, every foe Paralyzed, and on to Ester's turn (logs/2026-11-14-quiver-turn.md). |
| `topartyfight.sh` | a fresh DOSBox at its title: START GAME, through the opening show fight, the party gathered (6), the panel hidden (L), stepped forward until the arena fight is on; |
| `toturn.sh N` | the party's turns played until member N's (state.py's turn): Tab + Return for each member, and E when the same member's turn is still up after that (no Move left: its END menu, wherever the game puts it, waits; |
| `turnsetup.py MEMBER LEVEL [COMBATANT=HD ...]` | memory only, never save after (2026-11-09). |
| `turnwatch.py MEMBER SECONDS` | polls whose turn it is and the member's turn bytes every 5 ms, printing each change with its time. |
| `untilturn.sh NAME` | play party turns (Tab + Return) until NAME's turn comes, messages clicked away. |
| `usable.py [all]` | what the Loader would mark as usable while Alt is held (dsloader/usable.py): each thing's number, kind, name, map place and screen place, those in the view only unless "all"; |
| `viewto.py X Y` | drag the view (scroll.py, the middle button) until map point X, Y is near the screen's centre, so a far spot can be clicked. |
| `walkprobe.py N X Y DIR [SECS]` | a click at screen X, Y (game pixels), then for SECS seconds (default 6) as often as it can, a sample of the walk. |
| `walktime.py N X Y [DIR]` | a click at screen X, Y (game pixels), then party member N's map position every 50 ms until it has stood still for 1.5 s: each step's time (the walking pace), and with DIR a window grab at each step (DIR/wNN.png) |
| `walkto.py TX TY [TRIES]` | walk the party's leader to map position TX, TY (16ths of a square, as party_position) with left clicks on the map in Walk mode (the plain arrow pointer; |
