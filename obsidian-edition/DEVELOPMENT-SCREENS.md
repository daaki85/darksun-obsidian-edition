# Development: what the game and the Loader show

*Part of the [development notes](DEVELOPMENT.md). How the game's own screens show more (the combat log, names over figures, THAC0 and saves, the Look box, charges), what the Loader's tabs read, and the controls, saves and game speed: where the patched game calls the helper (DSCLOG), and what the Loader reads and writes. Each heading names the section of the [features page](FEATURES.md) or the [README](README.md) it explains.*

## Contents

- [The Dialogue tab](#the-dialogue-tab)
- [Searching junk, hay and wardrobes](#searching-junk-hay-and-wardrobes)
- [The Bowyer's archery target](#the-bowyers-archery-target)
- [Ability checks in the scripts' conditions](#ability-checks-in-the-scripts-conditions)
- [The combat log in the game](#the-combat-log-in-the-game)
  - [What the game allows](#what-the-game-allows)
  - [The panel](#the-panel)
- [Names over figures](#names-over-figures)
- [THAC0, saves and thief skills](#thac0-saves-and-thief-skills)
- [Detonate's blast on an item](#detonates-blast-on-an-item)
- [The psionic power check](#the-psionic-power-check)
- [What hurts a monster (the Look box)](#what-hurts-a-monster-the-look-box)
- [Charges in item boxes](#charges-in-item-boxes)
- [No manual check](#no-manual-check)
- [Scripts' requests and refused casts in the dice log](#scripts-requests-and-refused-casts-in-the-dice-log)
- [Choosing an enemy: Tab, Enter and the rings](#choosing-an-enemy-tab-enter-and-the-rings)
- [Scrolling the map](#scrolling-the-map)
- [The pointer in scenes, and where it starts](#the-pointer-in-scenes-and-where-it-starts)
- [More saves](#more-saves)
- [More characters](#more-characters)
- [Game speed](#game-speed)

## The Dialogue tab

([In the README](README.md#the-dialogue-tab).)

The game keeps the clicked reply's row at DS:1F0A while it flashes it; the log
reads the reply's text from the game's own list.

## Searching junk, hay and wardrobes

([In How the game
works](HOW-THE-GAME-WORKS.md#searching-junk-hay-and-wardrobes).)

How: the scripts' random command has a routine of its own in the game; the
patched game has DSCLOG look in there (`INT D3h`), which records the roll, its
range, where the running script is (which tells the three searches and their
damage rolls apart) and the three counts (`dsloader/searches.py`). Tested in
play: a haystack search in the slave pens logged
`0-10 = 7, an old, soiled loincloth (the party's 2nd find of 6 in hay)`, as
the game's own message said.

## The Bowyer's archery target

Shooting at the target in Teaquetzl runs script 178 (with a bow in hand: the
script counts objects 1017, 1039 and 30007, the bow, the Bow +2 and Phrain's
Bow, into variables 1 to 3, added up at 40Dh; the Loader's copy jumps from
there to code added at the script's end, which counts Dunesong, 2594, into
variable 5, adds the four and jumps back to 41Ah, so nothing in the script
moves: `bowyer.with_dunesong`): its distance command (80h)
gives the archer's distance from the target (object 1314) in squares, as the
game's distance routine (DSUN.EXE DD8Ch) counts them: the least n, from its
estimate, with n * n + n at least dx * dx + dy * dy (map squares, the map
things' 16ths of a square at DS:669Dh shifted by 4). Under 5 is a bull's eye
with no roll; otherwise a random 0-20 under DEX - distance / 2 (2 if DEX is under
the distance) hits, under by 10 or more is the centre, which from more than 13
squares with the Bowyer (object 283) within 25 gives 6 Arrows +2, once (flag
642). `dsloader/bowyer.py` writes the shot's line from the random command
PROBE_SCRIPT_RAND records (position 57Fh, script 178's alone), the archer the one
whose turn it is, the distances worked out the same way from where they stand.

## Ability checks in the scripts' conditions

Some scripts test an ability without the ability check command: a condition
compares the random command with a field of the character acting (fields 23 to
28, STR to CHA), as Chahl's `random(19) <= CHA` when asked about his scars
(script 181), the chains a strong character breaks (76) or a secret door an
intelligent one spots (69, `INT - 10`). `dsloader/scriptchecks.py` finds every
such condition in the Loader's copy of GPLDATA.GFF (15 of them; 14 in the game's own) by the position
DSCLOG records past its random command (as the searches are told apart; a
position two scripts share is left out), and the dice log evaluates the
condition with the roll and the score of whoever's turn it is (outside a fight
the leader, the character acting): `Daaki CHA check: 0-19 = 15, always made
(CHA 20) -> success`. Which way the condition goes is the one the ability
favours (the score 25 with the lowest roll). Tested in play with Chahl.

## The combat log in the game

([In FEATURES](FEATURES.md#the-combat-log-in-the-game).)

### What the game allows

What was measured before the panel was built (Stage 0 of
[the design brief](docs/combat-log/HANDOFF.md)), with the patched game and the
dice log running:

- **Pages.** The game keeps a table of pages at `0980:0004` (DSUN.EXE
  segments, less the load segment; the shadows read it): each page's memory
  segment (`+4`; a child page, flag `40h` at `+C04h`, names its parent there),
  its bounds (`+404h` x0, `+604h` y0, `+804h` x1, `+A04h` y1). Pages 0 and 1
  are the two screens (`A400h` and `A000h`, 320 x 200 in mode X); the others
  are windows over them and buffers in the rest of video memory (`A7E8h`, a
  third 320 x 200; smaller ones to `AE55h`).
- **The flip.** The routine at `0980:5814` (DSUN.EXE 14414h) shows one screen
  or the other (the CRTC start address; `0980:118E` says which, 1 for `A400h`)
  and swaps them for −1. It is called from 45 places, all in overlays, for
  screens and windows: in five seconds of walking on the map the page shown
  changed three times, on opening and closing windows.
- **The map draws into the screen shown.** The view's floor, walls and
  figures go straight into `A400h`, the screen on show (the shadows' `v_seg`
  read live), a rectangle at a time as things move (`PROBE_REDRAW` 2475Fh,
  `PROBE_REDRAW_ALL` 24B18h, the floor routines 2700Eh and 27162h). So there is
  no last moment of a frame on the map: a panel over the view has to be drawn
  again after each of those redraws that overlaps it (their way back, as
  `FLOOR_POST` does for the floor), or the figures walking under it would
  wipe it (the panel is: see below).
- **Keys.** On the map End and PgUp scroll the view (16 pixels down-left and
  up-right: the numeric keypad's diagonals; PgDn and Home likely too, at the
  map's edge here), so they stay the game's; L did nothing on the map, and is
  the panel's.
- **Font.** The game's text font is RESOURCE.GFF's FONT 100, 9 pixels high
  with its shadow (`art.py`): a panel 67 pixels high holds a header and 6
  lines.
- **Memory.** With GOG's settings (`ems=true`) DOSBox keeps EMS's 64 KB page
  frame where upper memory would be, and with the helper loaded `mem` shows 1
  KB of upper memory free. With `ems=false` (the launcher's own config, after
  GOG's) it shows 65 KB (largest block 64 KB), conventional memory unchanged
  at 632 KB ([Room in the helper](DEVELOPMENT.md#room-in-the-helper)). The game's memory layer (VMEM)
  takes EMS, XMS or extended memory, whichever there is: without EMS it loaded
  a save, walked the pens, opened a conversation and a shop, and played the
  arena's opening fight to the end without a fault (a check, not a whole
  game).

### The panel

- **Where it lives.** The Loader draws the panel's picture (`combatlog.py`:
  180 × 78 palette indices in the area's own colours, matched to the palette
  DSCLOG last read) into the helper's far block, beside the dice log's ring
  (`FAR_PANEL`; its segment `panel_seg`, header `+328`: [Room in the
  helper](DEVELOPMENT.md#room-in-the-helper)).
- **Putting it on screen.** DSCLOG copies the picture into the screen on show,
  a plane at a time (`PANEL_BLIT`, its height kept on the screen; the Loader
  stores each row as its four planes' bytes in turn, `combatlog.planar`, so a
  plane's part of a row is copied whole with `REP MOVSW`), from the main loop
  (`PANEL_TICK`, in `PROBE_SCROLL`) when the floor has been drawn since or the
  Loader has a new picture (`panel_new`, `+330`).
- **Kept whole.** The game draws what moves a rectangle at a time, through one
  routine (2475Fh, 1DF3:142F: a window page the rectangle's size, the floor,
  walls and figures drawn into it) or the same steps inline in the routine
  drawing again all that moved (from 24B18h). A rectangle over the panel,
  while it is on screen, is drawn as its parts round it instead (`CLIP_CHECK`,
  `REDRAW_PARTS`: above, below, left and right, through 2475Fh, `RP_BUSY`
  letting them by), so nothing the game draws there covers it: the routine
  itself is left out (its caller's way back kept in a frame of its own shape,
  for the overlay manager), and the inline one goes on at its end (24C65h).
  With the routine's last argument the screens are flipped and the rectangle
  copied to the other, so the panel is put on the screen not shown first
  (`PANEL_DRAW_OTHER`). Measured in the arena's fight, playing turns: before,
  the map showed through the panel in every frame grabbed (300), up to 7,000
  of its pixels; after, in none. What still reaches it is the view drawn whole
  (a scroll, centring on whose turn it is), put back on the next pass of the
  main loop. The game's own scrolling (at the screen's edge, following who
  walks) copies the screen as it is, the panel too, and draws only what comes
  into view, which left copies of the panel on the map; so when `PANEL_TICK`
  finds the view moved since its last pass (`CAM_X`, `CAM_Y` against
  `panel_cx`, `panel_cy`), it has the view drawn again whole (`VIEW_AGAIN`),
  round the panel, and then puts the panel. The inline routine's way back
  (`RESUME`, which the floor's and the rectangle routine's probes also use,
  and which the parts come through) is kept on the stack while the parts are
  drawn: overwritten, the game went on from the wrong place and wrote over its
  own memory until it quit.
- **Flips.** Much of what the game draws in a fight (a step of an attack, a spell's effect, the
  view drawn whole) goes into the screen not on show, and then the screens are flipped
  (0980:5814, DSUN.EXE 14414h). The panel is drawn into the screen on show, so each such flip
  showed the map without it until `PANEL_TICK`'s next pass: a frame or two, longer in a monster's
  turn (the main loop doesn't run while the game shows an attack or a spell). Measured in the
  arena's fight, frames grabbed at about 43 a second for 40 seconds, the frames with no game
  window up but no panel either: 19 runs before (up to half a second); with `FLIP_PANEL` in the
  rectangle routines' probes (a rectangle away from the panel, with the flag to flip: the panel
  put on the other screen first, as `REDRAW_PARTS` does for one over it) 10; with `FLIP_SITE` as
  well (`INT 98h` and its site number over "mov ax,0A000h / cmp word [118Eh],0" in the flip,
  14444h, where the screen to show is set and the VGA not yet told: the panel put on it if it is
  on the screen shown now, and that counted as its page) none but the frame or two after a
  message closes (the view drawn again without the panel; back at the next pass). A game window
  is never drawn over: on the map with one up (a message, a figure's menu, EXIT GAME, the game
  menu) `SCREEN_IS` is 2, and the panel waits, as before, until it closes.
  With `FLIP_SITE`, a rectangle over the panel that is to be flipped to (the flag, into page 1,
  the screen not on show) is drawn whole, not in parts: the panel is put on that screen at the
  flip, before it shows, and the routine's copy to the other screen takes it along. In parts each
  part was drawn with the flag, so each was a flip of its own (the pointer taken off and put back,
  and a wait for the monitor's refresh, `PROBE_FLIP`): a monster's turn with the panel up flipped
  about 25 times instead of 15 and took 1.03 seconds on average against 0.89 without it. Drawing
  the parts but the last without the flag, and then again into the other screen, flipped once but
  drew the map and figures twice, and was slower still (1.29 seconds). Drawn whole, measured the
  same way (playing the arena fight for three minutes, the panel shown and hidden by turns of a
  minute): 0.95 seconds against 0.83 (turns vary by a third of a second either way: no difference
  to be told), the screens flipped as often either way, and the animation's flips 38 ms apart
  against 36 (the panel put at each). With K'ratchek's Whirlwind turning (by turns of 20
  seconds): 42 ms against 41, a monster's turn 1.01 seconds against 1.00.
- **The pointer.** The game draws its pointer into the screen on show itself:
  28D1:093D keeps what is under it (from page `[A05Dh]`, the map without the
  panel) and draws it; 28D1:0B7F puts what it kept back, so taking the pointer
  off over the panel leaves a patch of map. `PROBE_POINTER` (the stack check
  at the start of 093D, 2EA55h) puts the panel first when the pointer is to be
  drawn over it, or was last drawn over it (`[A137h]`, `[A13Fh]`;
  `POINTER_MOST`, 32, the box). `PANEL_DRAW_POINTER` puts the panel and then
  calls 093D, without taking the pointer off. `PANEL_TICK`'s refresh with the
  panel unchanged (at most once a BIOS tick), is `PANEL_DRAW_AROUND`: the
  panel without the pointer's box (`PB_SKIP` in `PANEL_BLIT`), so the pointer
  stays on screen.
- **On and off.** The Loader sets `panel_on` (`+326`) in a fight with the
  switch on; off, or the Loader silent for 5 seconds (`stats_stamp`, which it
  writes about once a second), DSCLOG has the view drawn again without it.
- **The game's windows.** A figure's menu, a question or EXIT GAME are shown
  on the other screen, the view drawn there again first: the panel is not on
  it, and is back when the window closes. Full screens (USE, View Character)
  stop the main loop, and `PANEL_LIVE` counts the panel as on screen only on
  the map (`ON_MAP`: the game's `DS:0BC9h`, `SCREEN_IS`, is 1 on the map, 2
  with a character's screen or a talk over it, 0 on the title, the menus and in
  character creation; the game's DS is learnt in `PROBE_POINTER`): else the hooks that draw the view round the panel
  and keep its clicks from the game drew a full screen round it too, the panel
  left over it and the clicks there lost. (Drawing it into both
  screens doesn't work: the game keeps other pictures in the one not shown.)
- **The lines (Stage 2).** The Loader keeps the fight's dice log lines
  (`combatlog.Log`, the last 200, from the moment it sees a fight to 5 seconds
  after) and draws them into the picture: a header line (`round_status`: the
  round, who is acting, who is next), then the last 6 rows of the well. Each
  line's level (`shorten`) is worked out from the log's own wording (the
  attack, save, magic resistance, damage and d100 patterns), an attack's
  damage put on its line; its kind (`line_kind`, the Loader's colours) from
  the full line; whose line from the name it starts with (a filled pip for
  the party, hollow for a monster). The game's font comes from RESOURCE.GFF
  (`art.Font`); without it the panel has no lines. A new picture is written
  only when something in it changes.
- **Scrolling (Stage 3).** DSCLOG's mouse handler (`PANEL_MOUSE`, in
  `MOUSE_EVENT`) notes where the pointer is (header `+332`, game pixels, as
  the driver gives them), and a left press on the panel, while the page on
  show is the one the panel was last drawn into (not under a game window), is
  counted with where it was (`+338` on) and kept from the game with its
  release, `+336` set while it is held. The Loader (`Panel.mouse`, each pass
  of the log) makes it a drag of the handle, a page, or a click on the
  **Latest** chip; the mouse wheel comes from a Windows low-level mouse hook
  (`wheel.py`, its own thread), counted only with DOSBox's window in front
  and the pointer over the panel. Scrolled back, the top row stays put
  (`Panel.first`; `None` follows the newest).
- **Drawn again.** Besides the floor and the redrawn rectangles, the game
  draws parts of the view in a fight as the pointer moves over it (what it is
  over), through routines not hooked: `PANEL_TICK` puts the panel again when
  the pointer has moved, and anyway (round the pointer: see **The
  pointer**), at most once a BIOS tick (`PANEL_TICKS`; counted in passes of
  the main loop, it was most of what the game's CPU did with the pointer
  moving).
- **Sizes (Stage 4).** The Loader sets the panel's top and height (`+344`,
  `+346`, before `PANEL_NEW`; the picture's block is PANEL_W x 130, the most);
  its foot stays at row 198. Smaller than it was, DSCLOG draws the view again
  under it first. Collapsed is 15 rows (the newest line in the header), docked
  78, expanded 130 (11 lines and the filters' row). The header's level chip
  and - / + buttons, and the filters, are pressed through `PANEL_MOUSE` as the
  scrollbar is. **L** (`INT 16h`, `our_key`, while the panel is on screen:
  `PANEL_LIVE`) is counted at `+348` and kept from the game; the keyboard hook
  is on while the panel is shown, not only with Tab targeting. With the panel
  hidden, L is counted too (`L_ON_MAP`) while the map's main loop has run in
  the last BIOS tick or two (`MAP_TICK`: no game window, menu or save name
  waiting on keys, where L is the game's) and the Loader is there. The Loader
  shows the panel while `Panel.open` (saved as `combat_log_open`, off at
  first): L with it hidden shows it, L or the header's **L** button
  (`combatlog.key_rect`) with it shown hides it, in a fight or out of one. Out
  of fights the log takes the lines with a roll in them
  (`Log.add(rolls_only=True)`). The level and size are saved in the settings
  (`combat_log_level`, `combat_log_size`). Out of a fight the header says the
  game's time (`clock_line`: `Day 47, 14:20` from `GameData.game_time`, day 1 at
  00:00), but in the arena (region 2Ah, `combatlog.ARENA_REGION`), once it has
  been read, the arena's count of fights, read there and in the slave pens (29h, `ARENA_REGIONS`) (`arena_line`, docked or expanded; it once had a
  button, A, dropped as the game's A key turns animations on and off):
  the game's global number 12 (`GameData.number(ARENA_FIGHTS)`, a word at the
  far pointer `NUMBERS_PTR`, DS:1356h; scripts' 07h/87h variables), which
  script 3 adds one to when the party walks out of the arena after a call.
- **Not checked mid-fight:** saving and loading, and area changes, as the game
  allows neither in a fight. DOSBox's window size doesn't matter (it is drawn
  into the game's screen).

## Names over figures

([In FEATURES](FEATURES.md#names-over-figures).)

- **What starts one.** A spell's cast: `CAST_SITE` (INT 98h and its site
  number over `mov cx,[bp+6]` at 772AAh, the start of the routine at 772A5h
  that casts a spell or a power, the game's `598:89h`: `[BP+6]` the caster's
  combatant, `[BP+8]` the target's, `[BP+0Ah]` the spell) records an entry of
  kind 8, `KIND_CAST`, with the spell as its value. Every cast goes through it:
  the party's from the USE screen or a click, the monsters', a weapon's or a
  spell arrow's on a hit. The dice log floats the spell's name over the caster
  (`dicelog._float`), and "Miss" over the target of an attack whose roll
  missed. A combatant's number is its map thing's (the game's table of
  combatants, `3972:0C36h`, has one entry a thing).
- **The Loader's side** (`labels.py`). Each label is drawn in the game's font,
  its ink with a dark edge a pixel round it (the colours nearest gold or
  light grey and near black in the palette DSCLOG last read), as two one-bit
  masks of 16 bytes a row (128 pixels; longer names shortened word by word,
  then cut) and 11 rows. They go into one of four slots in the header (`+374`,
  `LBL_SIZE` 360 bytes each: the label's number, width, height, how far above
  the feet, the two colours, the map thing, the masks), the number written
  0 first and last of all, so DSCLOG never takes a half-written one. A label
  stays 1.5 seconds, a charge used 3 (`CHARGE_FOR`); a new one takes the slot
  of one over the same figure, else a free one, else the oldest, but a "Miss"
  or spell's name never takes a charge's (its priority).
- **DSCLOG's side** (`LABEL_*`). The map is drawn straight into the screen on
  show, and figures are drawn again as they move, swing and take damage, by
  routines that weren't all hooked in the first trial (a label over melee was
  whole in only a third of the frames). So the labels are put again from the
  game's timer: `PROBE_TICK` (about 120 strikes a second) calls `LABEL_STAMP`
  every other strike. It writes only (no reads of video memory, so the VGA's
  latches are left alone), keeps the VGA's registers as the shadows do
  (`VGA_SAVE`; it waits for its next strike while another pass has them kept,
  `VGA_BUSY`, as the slots are shared), finds the screen on show from where the VGA starts it (CRTC
  0Ch, the high byte the game's page flip sets: A000h or A400h), stays off the combat log's panel, and
  does nothing while the game's busy flag for it is up or off the map. It
  also places a new label (`LABEL_WHERE`: centred over the thing's feet, its
  bottom `UP` rows above them, under the feet if it would reach the game's
  boxes at the top, row 40, and kept on the screen), as the main loop doesn't
  run while the game shows an attack or a spell.
- **The main loop** (`LABEL_TICK`, after `PANEL_TICK` in `PROBE_SCROLL`)
  places labels too, and has where one was drawn again when it goes, moves or
  changes (`LABEL_ERASE`: the game's routine for a rectangle of the view,
  `1DF3:142Fh`, with page 1 and a flip, as its own call at 28185h; page 0
  without one drew to the screen not shown and left the label). When the view
  has scrolled, the game's scrolling has copied any label with it, so all are
  taken off and the view drawn again whole (`VIEW_AGAIN`); the timer doesn't
  put labels while the view isn't where the main loop last saw it.
- **Memory.** The first two slots and the code cost about 1.5 KB of the helper's
  upper memory (the ring went from 74 entries to 66 for it); the other two,
  720 bytes, fit in the room left.
- **Measured** in DOSBox, a fight in the slave pens with every attack made to
  miss, a slot watcher grabbing the screen as each label came: "Miss" was in
  every one of nine grabs half a second in, through swings and damage
  bursts; a cast from the USE screen showed its name once the map was back.

## THAC0, saves and thief skills

([In FEATURES](FEATURES.md#thac0-saves-and-thief-skills).)

How: the patched game calls the helper (`INT 65h`) just after the panel's
weapon lines; the helper prints the lines with the game's own text routine,
whose address, like the selected character, it reads from the game's code
around the patch (overlays move, so nothing is fixed in advance). The View
Character screen does the same through `INT F3h`, called once it has drawn the
character's two panels (the saves under the item icons; MOVE, the creature
record's +1Bh, and THAC0 at x D8h on HP's and PSI's lines, 7Fh and 86h, clear
of HP's value at its longest), and the routine that lists the weapons through
`INT FAh` after each one. The Loader keeps the numbers in the helper's memory,
with the time it last did: older than 5 seconds, the helper shows the sheet's
numbers instead. Before a screen is drawn, the helper asks the Loader to
update them and waits for its answer, half a second at most (`STATS_SYNC`:
`stats_req`, `stats_reply`). The game stands still while it waits, its
pointer too, so the Loader answers from a thread of its own
(`DiceLog.answer_stats_in_background`, a look each millisecond, about 4 ms to
work the numbers out), not from its main loop's next pass: that took 26-79 ms
with the Ledger's window open, on top of the game's own pause after an item is
picked up or put down (50-90 ms at 20,000 cycles: its mouse handler, DSUN.EXE
3573Dh, only queues the moves, and the pointer is drawn again once the game
has done with the item). That pause is shorter too: the game flips its two
screen pages as it redraws, and its flip (14414h) waits for the next vertical
retrace each time; `PROBE_FLIP` (INT 8Bh in place of the flip's call to the
wait, 1445Fh) skips the wait while a full screen is up (`SCREEN_IS` 2: the
inventory, View Character, USE, a talk) and waits as the game does on the map,
whose pace may hang on it. Measured with a save (Zulak's inventory,
20,000 cycles, where the game last drew the pointer, `DS:A137h`): 56-103 ms
(85 on average) before, 42-45 putting an item down and 63-67 picking one up
after; skipping every retrace wait saves no more, and the rest is the game's
own drawing (a faster game speed shortens it). Nothing else in the game changes.

Which class levels up next, on View Character: the game looks up the XP for
each class's next level in its tables and shows the lowest. Where it adds the
closing bracket, the helper (`INT D2h`) finds which classes that number
belongs to and adds their letters first.

## Detonate's blast on an item

The effect switch (its values at CS:0D96h of the segment at file 78BA0h, case
138 at 797F6h) queues effect 195 (the blast, 1d10) on the target, then calls
7AAEBh: of the target's items listed by A0:1A2Dh, those worn (+2 = 1), the one
whose item +10h is lowest and under 6 (the first on a tie); a 1d20 (the dice
routine, 0538:0089h through the overlay stub) under 15 less its item +14h
(the plus) has 4E0:7Ah take it away (one off a stack whose type's +0Fh has
bit 2, else the whole item; nothing left in its place). The item templates'
+10h: cloak 3, bone helm and leather chest 4, bone scale arm and leg 5, short
sword 6. `DET_ITEM` replaces its "mov dx,0Fh / sub dx,ax" (7AB95h) to record
the check (KIND_ITEM, extra the item | 4000h); the d20's own dice entry (its
caller's code `DETONATE_ROLL_RETURN`) is left out for it.

## The psionic power check

([In How the game works](HOW-THE-GAME-WORKS.md#psionics).)

The check is 5D59Dh (combatant, power 0-33, bonus), from the routine using a
power (5CC2Dh): its return is the d20 when the power works, 0 when it fails
("psionic power check fails", half the PSP), FFh when static disrupts it. Its
d20s come from random(low, high) (`1A0A:2FA9h`, selector A0h), whose code after
`rand()` no filter matched until `RANGE_SITE`; the dice log tells the three
calls apart by the code after each (`POWER_CHECK_RETURN`, `STATIC_FIRST_RETURN`,
`STATIC_SECOND_RETURN`), the psionic defence's two rolls (5D718h, the target and
the attack's elements 400h; random(1, its defence) with the attacker's kept d20
pushed after the arguments, so the call's `[BP+0Ah]`: `DEFENCE_FIRST_RETURN`,
`DEFENCE_SECOND_RETURN`), and skips its other callers (points for some spells'
pictures, 60041h). The score, the byte at `[BP-2]`, is the ability `+0` bits 0-2
of the power's 8 bytes name (`3FB9h:0000h`, `game.POWERS_SEG`; through 508:57h,
the ability as it is now), plus `+0` bits 3-7 (signed), plus the bonus, plus the
user's own number for the power, less 1: for a party member bits 3-7 of the byte
at selector 2F0h, `+77h + member * 22h + power` (0 not known; 1 known, all a new
character has), for anyone else 1 (5C9E7h). The game has routines to raise and
lower that number (5CF35h, 5CFA9h, 1 to 30) that nothing found calls. With a
Synaptic Static (effect 1Eh) kept up by someone else, the user's d20 over
`[BP-8]` disrupts the power; that was to be the power's score, but the ability
read for it is dropped and only the user's own number kept. Else the keeper's
d20 at or under its own Static score (`[BP-6]`), and no lower than the user's,
does.

## What hurts a monster (the Look box)

([In FEATURES](FEATURES.md#what-hurts-a-monster-the-look-box).)

How: the patched game calls the helper (`INT F5h`; INT 66h-6Fh can't be used:
the game calls those itself, looking for sound drivers) where the box has
drawn its first status rows; the helper asks the Loader and waits a moment for
its answer, and prints the lines with the game's text routine. `INT F6h`, at
the end of the routine that closes the box, shows the whole description.

The AC is the one `PROBE_AC` last recorded for the creature
(`DiceLog.monster_ac`: the game works an AC out only for an attack, and keeps
none). Before any attack on it, `GameData.counted_ac` counts it as the game's
AC routine (58DD3h) does, as `THORNS_AC` does in the helper: the sheet's base
(+27h, 10 for an armed man), less each worn item's plus and its type's AC
(types with +0Fh 80h, in the worn item list, +8), a fifth of a
gladiator's level and the DEX adjustment; the effects' part (Armor,
Barkskin...) is left out.

## Charges in item boxes

([In FEATURES](FEATURES.md#charges-in-item-boxes).)

An item that casts a spell has the spell + 1 in its `+0Fh` and its charges
left in `+0Eh` (the routine finishing an item's use takes one off, 721E4h,
unless its type's `+0Fh` has 2). `PROBE_ITEM_BOX` (`INT DAh`, at the end of
the routine filling an item's box, 8C1A1h, the item `[BP+6]`) draws
`Charges: n` in the row after the box's own lines (`IB_CHARGES`) when the
spell byte is below F9h (from there the game's own effects: a belt's STR, a
ring's AC...) and the charges aren't 0, but not for fruit (type 60, eaten
whole) nor scenery (a type whose `+08h` has both 20h and 40h: a door, a
mirror, a crank), where those bytes hold something else (`TYPE_SCENERY`).

## No manual check

([In FEATURES](FEATURES.md#no-manual-check).)

How: the dragon's question is the game's script 20, which script 120 runs (a
call into another script, command 14h) when the party leaves the warrens
(region 28h) until bit 12 of the game's variable (135, 73) is set. The right
answer goes on to script 86 at 1087, which sets 255 in the variable (7, 4)
and, in region 28h, that bit. In the Loader's copy of the scripts
(`dsloader/manualcheck.py`), script 20 does just that and ends: the same start
(offset 1, its one entry in the game's table of entry points), no words and no
question. It is replaced only if it is the dragon's (its `" word on page "`
line).

## Scripts' requests and refused casts in the dice log

Two `NS_IMAGE` sites record what the game does without a roll:

- `REQ_SITE` (DSUN.EXE 7FF42h, "mov bx,[bp+6] / dec bx") in the routine running
  a script's REQUEST (command 22h, 7FF30h; a jump table of 20 at its CS:177h):
  kind 6 (`KIND_REQUEST`), the request as the entry's value, the frame for who
  and the two values. `REQUEST_NAMES` names all 20 (from the yuan-ti project's
  notes on the game: rest, door, skill check, rest, an object's state,
  cinematic, trap, random monsters, transform, block and unblock a cell and its
  sight, arena bout, the pointer to walk, music, place an object, change sides,
  game over, count creatures).
- `AIM_SITE` (8455Bh, "cmp dx,-1") where a click on the map takes the readied
  spell's target (84538h; the cast follows) after the aim check (84C54h; its
  other caller, 8404Bh, picks the pointer's form on every pass of the main loop,
  about 2,000 times a second, and is left alone): -1 no creature there, -2 not
  one the spell takes, -3 a wall too long, -4 out of sight (its line-of-sight
  call, 0020:00A4 in the overlay's terms), -5 too far. A refusal is kind 7
  (`KIND_AIM`): the answer and the spell (DS:9428h) in the value, the caster
  (DS:9426h) in EXTRA.

## Choosing an enemy: Tab, Enter and the rings

([In the features page](FEATURES.md#choosing-an-enemy-tab-enter-and-the-rings).)

How: DSCLOG hooks the keyboard (`INT 16h`) and takes Tab, Shift+Tab and, with an
enemy chosen, Enter from what the game reads, counting them for the Loader
(`dsloader/targeting.py`), which marks the chosen one in DSCLOG's
`RING_TAB` (`dsloader/rings.py`). The ring is drawn in the floor pass, after the
shadows, through a table of each colour's redder one made from the palette. For
Enter, DSCLOG puts the pointer at the enemy's feet and gives the game a left
click there, from the main loop, while the routine that finds what is under the
pointer (`DSUN.EXE` 25B52h, `INT DBh`) answers with the chosen enemy for half a
second, whatever stands in front of it.

## Scrolling the map

([In the features page](FEATURES.md#scrolling-the-map).)

How: the game hears of the mouse's buttons from the mouse driver, through a
handler it gives it (`INT 33h`, function 0Ch). DSCLOG hooks `INT 33h` and puts
its own handler in between, which keeps the middle button (the wheel pressed)
from the game (the right button is left to it). The game's main loop
asks where the pointer is (to scroll at the screen's edge); there DSCLOG has
the game centre its view where the drag puts it, with the game's own routine
(the one clicking on the overview map uses, which draws the view again), and
keeps the pointer it reports off the edges meanwhile. The Loader only switches
it (`dsloader/scrolling.py`). (Turning the wheel isn't used: DOSBox 0.74,
GOG's, never passes it on to the game.)

**M, U and I.** `MAP_KEY`, in DSCLOG's `INT 16h` handler for both reads and
peeks, turns M into O (the game's key for its overhead map) while the map's
main loop has run within the last tick or two (`MAP_TICK`, set in
`PANEL_TICK`), and lets U and I (USE, inventory) through; `OVERHEAD` then holds
the key's letter. The same key again, the loop not run since (the screen pauses
it), turns into Escape, which closes the screen. U on the inventory or I on USE
goes through (the game switches screens) and moves `OVERHEAD` to it; any other
key there clears it. The game reads a key in its keyboard interrupt (35600h:
a peek, `AH=1`, then the read, `AH=0`), so `OVERHEAD` changes only on the read
(`MK_READ`), and both give the same key. `PANEL_TICK` clears `OVERHEAD` when the
map runs again.

**The whole party in view.** The map's party is one figure while `DS:1168h`
(`game.IN_COMBAT`: not 0 in a fight and while the party is spread out, so the
Loader's `in_combat` also asks the fight state's +19h) is 0
(each member's map record, `DS:6694h` + 32 a member, has 80h when inside the
leader's figure). The game's key table on the map (1587h:0FEBh, its handlers 34h
on) has 5 call 1587h:3109h (argument 1: the view drawn again), which spreads the
members round the leader and sets it, and 6 call 1587h:32E2h, which gathers
them; a fight's end calls that too (from 1D51h and 3490h, unless `DS:496Ah`).
Loading a game (69218h, reading `DARKRUN.GFF`) sets it from the members' 80h.
`SPREAD_LOAD` (site `NS_IMAGE+48`, over the load's `mov word [1168h],0`, 692CEh)
and `SPREAD_GATHER` (`NS_IMAGE+55`, over the gathering's, 1DFE8h, only when its
way back is a fight's end, not 6's 0CE2h) set `SPREAD_DUE`; `SPREAD_TICK`, in
`PANEL_TICK`, then calls 3109h itself on the map out of a fight, if the party is
still one figure. (A 5 put in the BIOS's buffer waits there: the game reads
keys only in its keyboard interrupt.) Switch: `gamepatch.PARTY_SPREAD`
(`party_spread`, on).

**The view in a fight.** The game writes the view's place (`DS:1178h`,
`117Ah`) in two routines that centre it (on a figure, `191F:01FFh`, and on a
spot, `191F:0281h`; their callers test first whether the figure is off the
screen, `0AC0:AC7Ah`) and in one that steps it toward a spot (`2191:0BE3h`,
with `27845h` deciding: the spot off the screen, or within the margins at
`DS:2F6Fh` to `2F75h` of an edge it is heading for). The drift in a fight is
the last, called from the routine that moves a fight's figure a step
(`0AC0:C7B3h`, at `C9F2h`) on every step (a monster's only while the game
shows monsters' moves, `ES:19h` of segment `377Eh`). Found with `INT 3` put
over the first byte of each routine in a test build of DSCLOG, which kept its
callers' return addresses: in a fight the centring routine was never called,
and every move of the view came from that call (returning to `1CA37h`), for
party members walking as well as monsters. The patch (`camera_still`, a
switch, `CAMERA`) rewrites that call's 54 bytes of set-up: while `IN_COMBAT`
(`DS:1168h`) is set (a fight, or the party spread out), the game's own on-screen test first, skipping the
step while the figure is on the screen; the figure's spot pushed straight from
its record (one `push dword`). The game's `mov ax,377Eh` stays at `CA15h`: DOS
adds the load segment to that word as the game loads (the EXE's relocation
table), and a first version, which put other code there, ran garbled.
`gamepatch.patched` now refuses any patch that changes a word DOS relocates
(`gamepatch.relocated`). Out of a fight the same routine runs too (the arena's
opening, the party walking out through the gate: held still, the party never
left the view and the scene never went on), so there it is as the game has it,
as is the map's own walking.

## The pointer in scenes, and where it starts

([In the features page](FEATURES.md#the-pointer-in-scenes-and-where-it-starts).)

How: the scenes (the intro, its logos, the decree and the rest) are played by
one routine (`DSUN.EXE` 568BEh, each piece through `660:20`), whose player
asks the game's event queue between a piece's steps (`929F5h`); a key, DX 1,
ends the scene (`92A28h`). The game's own mouse handler isn't installed yet in
the intro, and the mouse driver's pointer can't be drawn there: the scenes'
VGA mode is unchained (mode X, 4 planes, page flipping), which DOSBox's driver
draws as garbage. So DSCLOG draws the game's own arrow (its pointer on the
menus, `RESOURCE.GFF`'s ICON 6001, 10 by 13 in 11 colours of `GPLDATA.GFF`'s
palette). The Loader reads it from the player's game at each start
(`scenepointer.py`) into `dos\POINTER.BIN`, which DSCLOG reads over its
`CP_DATA` as it loads: the rows, the colours (6 bits a part), then each row's
pixels as colour numbers, ending with 0. Without the file DSCLOG keeps a plain
black and white arrow of its own, so nothing of the game's is in the mod.

- **At each step** (`CINE_STEP`, the step's `or dx,dx / jz`): a button pressed
  since the last step (`INT 33h` function 5, both buttons) makes DX 1, as a key
  does. At most 30 times a second the arrow is wiped and drawn again where the
  driver has the pointer (function 3), each of its colours as the scene's
  palette's nearest (read from the DAC, the three parts' differences summed; of
  equals the last, as a picture seldom uses them), in the page shown (the CRTC's
  start address), each pixel's plane selected with the sequencer's map mask and
  the graphics controller's read map (both saved and put back, with the
  controller's mode, bit mask, set/reset and rotate). What was under it is kept,
  and put back only where the arrow still is: a frame drawn over it since stays
  as it is.
- **From the game's timer** (`PROBE_TICK`, while a scene plays): 30 times a
  second the arrow follows the pointer, and about 7 times it is drawn afresh,
  palette and all, so a still picture fading in shows it. The game writes its
  palette with interrupts off, so the timer never reads the DAC halfway
  through its writing.
- **At the scene's start** the driver's ranges are made the screen's (0 to 319,
  0 to 199; its own are 640 across) and the pointer put where it was last
  seen (`MP_X`, `MP_Y`: the arrow's place in a scene, the game's mouse events'
  out of one; the middle at first); a video mode set puts them back, which the
  next step sees (an x past 319) and sets again.
- **At the end** (`CINE_END`, the scenes' routine's `or si,si / jz`, where
  every scene comes, played or skipped) the arrow is wiped.

**Where the pointer starts.** After a video mode set the driver puts its
pointer in the middle of its 640 across; the game then gives it the ranges 0
to 319 (`2A8F2h`), which leave it at the right edge (318, 100). Just after
that (`MOUSE_SET`, its `mov word [0A12Dh],0`) DSCLOG moves it back to where
it was last seen when it is there (function 4; `MP_X`, `MP_Y`, kept by the
scenes' arrow and by every mouse event the game is sent: the middle before
the first), so a pointer moved in the intro or on a menu stays put through the
next screen's video mode set. The driver's own speed is 8 mickeys a pixel
across and 16 up and down; as the game resets the driver at its start
(`MOUSE_INIT`, `356F5h`, after function 0) and again with the ranges, DSCLOG
makes them 8 and 10 (function 0Fh): the window's aspect correction makes a
pixel 1.2 times as tall as it is wide, so 10 moves the pointer as far on the
screen up and down as across.

**Its speed in a window.** With the mouse captured, DOSBox 0.74 moves the
driver's pointer by the desktop mouse's motion times 8 over the mickeys a
pixel (`Mouse_CursorMoved`: one game pixel for each desktop pixel at 8), so in
the usual window, three times the game, the pointer moved three screen pixels
for each one the desktop pointer would: fast, and in steps of three, which
made placing items fiddly. The Loader's DOSBox settings set the mouse's
`sensitivity` (which scales that motion) to 100 over the window's scale, 33 in
the usual window (`launch.display_lines`, with `MOUSE_START`), and
`autolock=true`, as GOG has it: uncaptured, DOSBox reads the desktop pointer's
place in the window instead, which the sensitivity would scale too. In full
screen the scale depends on the monitor, and DOSBox's own is kept.

The two are switches (`SCENE_POINTER`: `cine_step`, `cine_end`; `MOUSE_START`:
`mouse_set`, `mouse_init`). The room in upper memory came from the freeze
report's records (32 to 16, taken half as often).

## More saves

([In the features page](FEATURES.md#more-saves).)

How: the save names the game searches the folder for and writes a save to
(`SAVE??.SAV`, `SAVE%.2d.SAV`) are two strings in its memory; DSCLOG changes
their fourth letter for the page. The window's event routine leaves keys and
buttons it has no use for to a jump to its end; the patched game has DSCLOG
take them there (`INT D8h`, `INT D7h`), and for a new page run the window's
own routines that search the folder, draw the rows and draw the window. Enter
is taken out of the window's key table, so it comes to DSCLOG too, which goes
on to LOAD (or SAVE) as the table did, but not on a row with no save. The
buttons are the game's kind, in the Loader's copy of `RESOURCE.GFF`: placed
in the window under EXIT, with pictures made from EXIT's, its letters taken
away and the page's put in with the game's text font
(`dsloader/savepages.py`; the buttons' own carved letters have no P, G or
digits).

Saves under their names (`dsloader/namedsaves.py`): every few seconds the
Loader looks at the 40 slots' files (`cloud_saves` before the game folder, as
GOG's DOSBox mounts it over the folder), and copies one newer than its copy to
`Named saves/` as `Page P slot NN - NAME.SAV`, the name from the save's
`STXT 1` (up to its first NUL; characters Windows won't take become `_`). A
slot's copy under another name is removed. **Put a save in a slot...** copies
a file back as `SAVE`/`SAVB`/`SAVC`/`SAVD` + the slot.

## More characters

([In the features page](FEATURES.md#more-characters).)

How: the game's file routines take any number; only its loops over the
characters stop at 20, its roster list has room for 20 and its "Maximum
characters" check counts to 19. The patched game has 30 and 29 there
(`dsloader/gamepatch.py`, a byte each).

A New character counts as Okay wherever the game tests for Okay: a jump each
(`NEW_AS_OKAY` in `dsloader/gamepatch.py`), and `game.py` does the same.

## Game speed

([In the features page](FEATURES.md#game-speed).)

**Steady pace** (`gamepatch.STEADY_PACE`, DSCLOG's STEADY PACE): the map's
frame (DSUN.EXE 1E8E4h) calls the step for everything (`call far 1DF3:26DC`,
which also builds the list of what moved at DS:57D0h, 10 bytes each: where
the thing was drawn, its size, the thing) and then the drawing of that list
with the page flip (`call far 1DF3:15EA`), the flip waiting for the vertical
retrace. The game has no other clock for walking: a step is a frame, and the
"think" that starts a figure on its next square runs once a frame, for one
creature at a time, so catching up a figure's animation steps alone (tried
before) only made it wait at the end of its square. PROBE_PACE_DRAW keeps a
schedule of 70 frames a second on the game's clock (DS:11D6h, 96 ticks a
second: a tick 70 units, a frame 96): at a frame or more behind, on the map (a
fight, the fight state's +19h, draws every frame), the drawing and its flip are
left out and the list is kept in the far block (FAR_PACE, 64 entries); the
next frame drawn has it added after its own, so the old places of what moved
in the skipped frame are drawn over too. PROBE_PACE_PASS sets "something
moved" after the step when a kept list has waited 2 ticks, so a frame is drawn
for it though nothing has moved since. A pause of 8 ticks (a load, a talk)
starts the schedule afresh; at most 4 frames are owed.

To count the pictures the game shows, watch the word at offset 118Eh of the
flip routine's own code segment (the routine at DSUN.EXE 14414h toggles it at
each flip): with the whole party walking in the slave pens it changed about 37
times a second without steady pace and 27 with it, the step a picture going
from one to two or three.

The Loader's drawing is as cheap as it can be without looking any different:
a shadow is darkened a plane of the video memory at a time (the graphics
card's registers set four times for a figure, not four times for each of its
rows), and a dust puff's pixels are worked out a row at a time, only within
its outline and the part of the view being drawn again. The pictures the
Loader draws the party's gear on are each exactly as long as their outfit,
with only the room gear needs round the figure while walking (6 pixels at the
sides, 2 above; 10 in a fight), since the game draws a walking figure's whole
picture at every step.
