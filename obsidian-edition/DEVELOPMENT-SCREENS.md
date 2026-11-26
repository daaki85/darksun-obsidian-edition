# Development: screens, controls and saves

*Part of the [development notes](DEVELOPMENT.md). How the game's own screens show more (the combat log, names over figures, THAC0 and saves, the Look box, charges), what the Loader's tabs read, and the controls, saves and game speed: where the patched game calls DSCLOG, and what the Loader reads and writes. How the dice log labels the rolls outside fights (searches, the Bowyer's target, the scripts' ability checks) is in [the internals](DEVELOPMENT-INTERNALS.md#labelling-rolls). Most headings name the section of a player's page they explain (the [features page](FEATURES.md), the [README](README.md), [items](ITEMS.md), [kits](KITS.md), [bugs fixed](GAME-BUGS.md), [how the game works](HOW-THE-GAME-WORKS.md), [the dice log](DICE-LOG.md)); the rest, a part of one or a note of their own, say which at their start.*

## Contents

- [The Dialogue tab](#the-dialogue-tab)
- [The Journal tab](#the-journal-tab)
  - [The quests](#the-quests)
- [The combat log in the game](#the-combat-log-in-the-game)
  - [What the game allows](#what-the-game-allows)
  - [The panel](#the-panel)
- [Names over figures](#names-over-figures)
- [THAC0, saves and thief skills](#thac0-saves-and-thief-skills)
- [The creation screen](#the-creation-screen)
- [Spell slots on the USE screen](#spell-slots-on-the-use-screen)
- [Detonate's blast on an item](#detonates-blast-on-an-item)
- [The psionic power check](#the-psionic-power-check)
- [What hurts a monster (the Look box)](#what-hurts-a-monster-the-look-box)
- [Charges in item boxes](#charges-in-item-boxes)
- [No manual check](#no-manual-check)
- [Scripts' requests and refused casts in the dice log](#scripts-requests-and-refused-casts-in-the-dice-log)
- [Looting a body: T and Shift+T](#looting-a-body-t-and-shiftt)
- [Selling plain gear: S](#selling-plain-gear-s)
- [Choosing an enemy: Tab, Enter and the rings](#choosing-an-enemy-tab-enter-and-the-rings)
- [The chance to hit before the swing](#the-chance-to-hit-before-the-swing)
  - [Under the pointer](#under-the-pointer)
- [Squares in reach](#squares-in-reach)
- [F10 takes a whole move back](#f10-takes-a-whole-move-back)
- [Showing what can be used: Alt](#showing-what-can-be-used-alt)
- [Scrolling the map](#scrolling-the-map)
- [M, U and I: open a screen, close it again](#m-u-and-i-open-a-screen-close-it-again)
- [The whole party in view](#the-whole-party-in-view)
- [The view in fights](#the-view-in-fights)
- [The pointer in scenes, and where it starts](#the-pointer-in-scenes-and-where-it-starts)
- [Spells on the Effects screen](#spells-on-the-effects-screen)
- [CHOOSE A SPELL's grid](#choose-a-spells-grid)
- [More saves](#more-saves)
  - [Quick save, quick load and autosave](#quick-save-quick-load-and-autosave)
- [More characters](#more-characters)
- [Game speed](#game-speed)
- [Picture and music](#picture-and-music)
- [The engine: GOG's DOSBox or DOSBox-X](#the-engine-gogs-dosbox-or-dosbox-x)

## The Dialogue tab

([In the README](README.md#the-dialogue-tab).)

The game keeps the clicked reply's row at DS:1F0A while it flashes it; the log
reads the reply's text from the game's own list.

**Learned speakers' names.** The dialogue window gets only a portrait number.
When the game runs a script on someone (clicked, or coming up to the party) it
notes who; the log reads that as a conversation opens. A conversation showing
one face, started on a named creature outside the party, is that creature
talking, and the portrait takes its name (`settings.json`'s
`speakers_learned`): portrait 5 became `Kurzak` ("Legcrusher! Get
gladiators!"), portrait 100 `Legcrusher`. A speech with no replies teaches a
name only when its speaker stands within 4 squares of the party
(`GameData.talk_target_distance`: Kurzak's call to the arena is started on no
one, and once taught "Trustee"). Several faces taking turns teach nothing.
Portrait 119's `The Announcer` isn't replaced by a learned name (he calls out
mid-fight, when the game's last script ran on a fighter).

## The Journal tab

([In the README](README.md#the-journal-tab).)

`dsloader/journal.py`. The dice log hands the journal each dialogue entry as it
is made (after `_not_ours`, so not the log's own turn summaries), the reply
chosen, and each message box (`DiceLog._journal_note`), with the game's clock
and region read then. A message box is a reward if it says "receives N
experience points", and left out if it is one of the game's notices (SAVING
GAME, GAME SAVED, CAN'T SAVE DURING COMBAT). Within one pass the talk goes
before the message boxes; the order between them isn't kept.

**The file.** `Journal/journal.jsonl`, a line of JSON for each entry, only ever
added to: `id`, `parent` (the entry before it in that game; 0 for a game's
first), `kind` (`talk`, `chosen`, `message`, `reward`), `clock` (game seconds),
`region`, `portrait`, `speaker` (the name as known when it was said; the tab
shows the name as known now), `text`, `replies`, `title`. A game's journal is
the chain from its newest entry back through the parents, so one file holds
every game and every branch. A line that isn't an entry is passed over; a file
that can't be written keeps its entries in memory for the next try.

**Following the saves.** The newest entry's id is kept in the game's global
numbers 198 and 199 (low word, high word: `journal.NUMBERS`; [the game's
numbers](DEVELOPMENT-INTERNALS.md#the-loaders-game-flags)), at the far
pointer DS:1356h, which the game saves whole (`SAVE` chunk 30, 400 bytes, 200
words) and loads back. The game's scripts read and set numbers 0-136 only
(`ScriptNumbersTests`, with `DSUN_GPLDATA`), and 137-199 are zero in every
save in `playtest/saves`. Every quarter second, not while a game is loading
(`_journal_sync`, with the party's watches), `Journal.sync` reads the id:

- the one last written: the chain's new entries are flushed to disk before their
  head is written into the game's numbers. A refused write leaves the last head
  in memory and is retried;
- another, read twice running (`STEADY`: a game being loaded may show one for
  a moment): a game was loaded or begun, and its chain is shown (`_follow`,
  `changed` counted so the tab draws it again). An id no entry has (the file
  lost) gives an empty journal whose new ids start past it, so an id a save
  holds is never given to another entry;
- none (the pointer null, as in the arena outside a script's run): nothing,
  and entries added meanwhile have ids the game doesn't hold yet. A save made
  then holds the older id; when it is loaded, and that id is on the chain shown
  till then, entries after it can be recovered if their clock is strictly
  earlier than the loaded game's. An entry from the same game second can
  belong to play after the save was made.

Before the first id is read (the Loader just started), entries wait (up to
500) and join the game's chain when it is known; until then the tab shows the
chain last added to. On the first stable read after attachment, the journal
reads from disk again before assigning IDs, under the game's lock. This
accounts for entries another Loader wrote while the window was waiting.
`DiceLog.detach` flushes pending entries and resets that first read.
At the title the numbers read zero, an
empty journal; the game's own comes back when its save is loaded, and nothing
is written to the file until something is said.

**The tab** (`Viewer._build_journal`, `_journal_tick` after each dice pass):
new entries are added at the end (`journal.rows`: a heading where the day or
the region changes, then the speaker, the text, the replies, the answer under
them); the whole is drawn again when the chain became another or the Show box
or the words wanted changed. With either set, each new entry draws the whole
again (`journal.chosen` keeps an answer with its talk). The switch is `journal`
in `settings.json` (**Keep a journal**, on the tab); the windowless starts keep
the journal too.

Region names: `journal.REGIONS` has the slave pens and the arena; the others
are to be added as play reaches them.

A message box is a reward (`journal.kind_of_message`) when it says someone
receives, gains or earns a number of experience (or "exp"): the game's routine
says "... receives N experience points!", and the 34 awards the scripts give
themselves are worded each their own way ("The party gains 4,000 exp!").

Tests: `tests/test_journal.py` (entries kept and read again, a save loaded showing its own chain,
a branch played from it, entries from while the numbers were away, a lost file, the tab on a real
window, and with `DSUN_GPLDATA` no script using the journal's numbers). Verified: [log](https://github.com/daaki85/darksun-obsidian-edition/blob/main/playtest/logs/2026-11-16-journal.md)
(Kurzak's speeches recorded; a save holding an older id loaded, its id read back from the game,
and the talk after it filed as a branch).

### The quests

`dsloader/quests.py` (the table, and what is open or finished) and
`dsloader/questdraft.py` (the tool that drafts it). The Show box's last
choice, **Quests**, draws the list in the journal's own text
(`Viewer._journal_tick`, `quests.rows`), the count beside it saying how many
are open and finished.

**What the game keeps.** No quest log: its scripts keep the story in 808
global flags (a bit each at the far pointer DS:1352h, `SAVE` chunk 29: read
in a script with variable 8Dh, set with destination 13) and 200 global numbers
(DS:1356h, `SAVE` chunk 30). A deed is rewarded in one of two ways:

- script 74's routines, at 135 for each party member and at 171 for one
  person, the amount put in number 16 first: 57 calls in 40 scripts, 78,510 XP
  counting the amount set last before each (three calls choose between two
  amounts, one gives what the party gave), saying "... receives N experience
  points!";
- the script itself (command 21h: who, how many), with words of its own: 34
  places.

**The table.** `QUESTS`, each a `Quest`: a name, the area or person it
belongs to, `told` (shown while it is open: only what the party was told
when it was given), `ended` (shown once finished), its `given` and `done`
conditions (`F(n)`: flag n set; `N(n, v)`: number n at v or more), `steps`
(an open quest's progress, "2 of 3"), a `reward` (the regions, the amount,
each party member or one) for a quest finished when the journal holds that
message, the rewards it was read from (`sites`: script and offset), and how
sure it is:

- `HIGH`: the done flag (or number) is set within 12 commands
  (`questdraft.NEAR`) of a reward in the script named, and no script clears
  it;
- `MEDIUM`: the done condition was read by hand to lie on the reward's way
  but further off (a comment says where), or the quest is finished by its
  reward's message alone.

`quests.status`: finished when any `done` holds or the reward is among the
journal's reward entries of the chain shown (so it goes back with a load, as
the chain does); open when not finished and any `given` holds; else not known
and not listed. A quest with no `given` shows only once finished. 45 quests:
39 from the rewards of the game's routine (49 of the 57 calls), 2 from
scripts' own awards (two more such awards end quests of the 39: the chief's
daughter and the alliance), 4 of the mod's own (Semyon's shipment, the
champions' bout, the cooked vulture, the arena's ring: the modules' own
flags). `LEFT_OUT` lists the other 8 calls with the reason for each. The
words are the project's own: with the game's scripts at hand,
`NoGameTextTests` checks no line of the table holds a line of theirs.

**Telling a reward by its message.** Ten quests have a `reward`: eight keep
no flag at all, the temple's is far from its reward, and Kalinin's is cleared
by the last battle. The journal's reward entry gives the region, the amount
and whether it was each party member's or one person's; `SCRIPT_REGIONS`
says which regions' master scripts start each script with a reward (`MAS n`
is region n's; directly or through one other script), and the test holds
each such quest to a message no other reward of the routine could give in
its regions. A reward given while the journal was off, or its file lost,
isn't seen: the quest is then not listed.

**Flags the table must not use.** Script 74 at 251 clears flags 5, 8, 9, 11,
13, 70 and 316-320, and is run as a region is entered: each region uses them
for its own passing state (317 and 318 are set beside two rewards). Flags
65, 267 and 268 (an ally's word given) are cleared by the last battle's
script 62.

**Reading the game.** With the journal's look, every quarter second and not
while a game is loading, `DiceLog._quest_look` reads the 101 bytes of flags
and the 400 of numbers (`quests.read_state`) and keeps the reading
(`quest_state`); while the flags' pointer is null (the arena outside a
script's run) the last one stays, until the game is gone or started again
(`DiceLog.detach` forgets it: the next game's is read afresh). The tab asks
for it at each pass.

**Without the game.** The viewer writes the reading to `Journal/quests.json`
with the journal's head at that moment, when it changed, every five seconds
at most, and at closing (`_quests_keep`). With no game attached (or none read
yet) the tab shows that reading under a line saying so, if its head is an
entry of the chain shown (or both are empty: a new game); otherwise the
reading is some other game's, and the tab shows only what the journal's own
rewards tell, under a line saying that. The reading is not kept per save: one
file, the last game read.

**Adding a quest.**

1. `python -m dsloader.questdraft GPLDATA.GFF -o /somewhere/outside/draft.txt`
   (never into the repository: the draft holds the game's text). For each
   reward it gives the script and offset, the amount, whose it is, the flags
   and numbers set within 12 commands, the flags the script sets and tests
   before it with the other scripts that use them, and the text around it.
   `--flag N` lists every place a flag is set or tested with the text there;
   `--script N` one script's rewards. `playtest/dec.py` shows the commands.
2. Read the script around the reward: which flag is set on every way to it
   and nowhere else (done), which is set when the task is given (given: often
   in another script, found with `--flag` on the flags the reward's script
   tests), and that neither is a scratch flag or cleared later.
3. Write the entry in your own words, `told` with nothing the party hasn't
   heard by then, and take the call out of `LEFT_OUT` if it was there.
4. `tests/test_quests.py` with `DSUN_GPLDATA` says whether the flags are
   where the entry claims; a reward told by its message needs its script in
   `SCRIPT_REGIONS`.

Tests: `tests/test_quests.py` (the table's shape; open and finished from flags, numbers, steps
and the journal's rewards; nothing shown of a quest not given; the reading from memory and from
every save in `playtest/saves`; the last reading kept on disk; the tab on a real window; and with
`DSUN_GPLDATA` the table held to the scripts: each done flag set beside a reward in its script,
each given flag set by the game, none a region's scratch flag, all 57 rewards of the game's
routine in a quest or in the list left out, a reward told by its message alone unlike any other
in its region, the draft tool's output, and no line of the table one of the game's).

Not done yet: the other 29 of the scripts' own awards (allies joining, the
strongholds' ends), and "given" flags for most quests (of the game's, only
Gilal, the chief's daughter, the temple, Notaku's three errands and the
alliance have one): the rest show under Finished only.

## The combat log in the game

([In the features page](FEATURES.md#the-combat-log-in-the-game).)

### What the game allows

What was measured before the panel was built (Stage 0 of
[the design brief](https://github.com/daaki85/darksun-obsidian-edition/blob/main/reports/archive/combat-log-design-handoff.md)), with the patched game and the
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
- **Memory.** With GOG's settings (`ems=true`) EMS's page frame leaves DSCLOG too little upper memory, so the Loader turns EMS off: [EMS
  off](DEVELOPMENT-INTERNALS.md#ems-off) (the game's memory layer then uses XMS; without
  EMS it loaded a save, walked the pens, opened a conversation and a shop, and
  played the arena's opening fight to the end without a fault: a check, not a
  whole game).

### The panel

- **Only while the map is the screen.** `DiceLog._update_panel` asks for the panel
  (`TSR_PANEL_ON`) only with the game's `DS:0BC9h` at 1 (`_map_up`): with a window, a screen, a
  menu or a talk up (2) it is taken off, and put back when the map is the screen again;
  `combat_log_open` is untouched, so L's choice stays. Before, DSCLOG drew it on top of whatever
  was up: over the save and load windows' QUICK button and list (the owner's report), and where
  a member's END menu opens.
- **Where it lives.** The Loader draws the panel's picture (`combatlog.py`:
  180 × 78 palette indices in the area's own colours, matched to the palette
  DSCLOG last read) into DSCLOG's far block, beside the dice log's ring
  (`FAR_PANEL`; its segment `panel_seg`, header `+328`: [the far
  block](DEVELOPMENT-INTERNALS.md#the-far-block)).
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
- **On and off.** The Loader sets `panel_on` (`+326`) while the panel is to be
  shown (in and out of fights: `combatlog.py`); cleared, or the Loader silent for 5 seconds (`stats_stamp`, which it
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
  78 (7 lines), expanded 130 (12 lines and the filters' row). The lines are in a font of
  the Loader's (`smallfont.py`: the X11 misc-fixed 5x7 glyphs, public domain,
  with the game's shadow, 8 pixels a line); the header, the buttons and the
  filters stay in the game's. The header's level chip
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

([In the features page](FEATURES.md#names-over-figures).)

- **The quiver's count.** After each party shot the dice log floats "Arrows: N left" (the quiver's
  count) or "Out of arrows" over the archer (`quiver.py` through `labels.py`, in the charges' blue
  and priority; none with names over figures off). The turn kept when the quiver runs dry: [An
  archer's last arrow](DEVELOPMENT-CONTENT.md#an-archers-last-arrow-and-a-dry-quiver).
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
  then cut) and 11 rows. They go into one of four slots in DSCLOG's tail
  (the header's `+1834` its segment, `+1838` their offset; `LBL_SIZE` 360
  bytes each: the label's number, width, height, how far above
  the feet, the two colours, the map thing, the masks), the number written
  0 first and last of all, so DSCLOG never takes a half-written one. A label
  stays 1.5 seconds, a charge used 3 (`CHARGE_FOR`); a new one takes the slot
  of one over the same figure, else a free one, else the oldest, but a "Miss"
  or spell's name never takes a charge's (its priority). Below them all are the
  standing labels, which take free slots only: the names of what can be used
  ([Alt](#showing-what-can-be-used-alt)) and the chance to hit [under the
  pointer](#under-the-pointer). When a label is taken off, moved or reworded
  the dice log has the view drawn again (`Labels.took_off`: what DSCLOG draws
  over the old place didn't stay in a still scene), and a new Loader empties
  the slots an earlier one left filled.
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
  boxes at the top, row 40, and kept on the screen; a figure whose feet are
  above the page's top, the view dragged away, gets none), as the main loop doesn't
  run while the game shows an attack or a spell.
- **The main loop** (`LABEL_TICK`, after `PANEL_TICK` in `PROBE_SCROLL`, which
  runs its pass with interrupts on when the game had them on, off only round
  the pointer's read with the drag's state and `TARGET_CLICK`'s calls to the
  game's mouse handler, so the game's clock loses no ticks to the redraws and
  the retrace wait)
  places labels too, and has where one was drawn again when it goes, moves or
  changes (`LABEL_ERASE`: the game's routine for a rectangle of the view,
  `1DF3:142Fh`, with page 1 and a flip, as its own call at 28185h; page 0
  without one drew to the screen not shown and left the label). When the view
  has scrolled, the game's scrolling has copied any label with it, so all are
  taken off and the view drawn again whole (`VIEW_AGAIN`); the timer doesn't
  put labels while the view isn't where the main loop last saw it.
- **Memory.** The first two slots and the code cost about 1.5 KB of DSCLOG's
  upper memory; the other two,
  720 bytes, fit in the room left.
- **Measured** in DOSBox, a fight in the slave pens with every attack made to
  miss, a slot watcher grabbing the screen as each label came: "Miss" was in
  every one of nine grabs half a second in, through swings and damage
  bursts; a cast from the USE screen showed its name once the map was back.

## THAC0, saves and thief skills

([In the features page](FEATURES.md#thac0-saves-and-thief-skills).)

How: the patched game calls DSCLOG (`INT 65h`) just after the panel's
weapon lines; DSCLOG prints the lines with the game's own text routine,
whose address, like the selected character, it reads from the game's code
around the patch (overlays move, so nothing is fixed in advance). The View
Character screen does the same through `INT F3h`, called once it has drawn the
character's two panels (the saves under the item icons; MOVE, the creature
record's +1Bh, and THAC0 at x D8h on HP's and PSI's lines, 7Fh and 86h, clear
of HP's value at its longest), and the routine that lists the weapons through
`INT FAh` after each one. The Loader keeps the numbers in DSCLOG's memory,
with the time it last did: older than 5 seconds, DSCLOG shows the sheet's
numbers instead. Before a screen is drawn, DSCLOG asks the Loader to
update them and waits for its answer, half a second at most (`STATS_SYNC`:
`stats_req`, `stats_reply`). The game stands still while it waits, its
pointer too, so the Loader answers from a thread of its own
(`DiceLog.answer_stats_in_background`, a look each millisecond, about 4 ms to
work the numbers out), not from its main loop's next pass: that took 26-79 ms
with the Loader's window open, on top of the game's own pause after an item is
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
closing bracket, DSCLOG (`INT D2h`) finds which classes that number
belongs to and adds their letters first.

## The creation screen

([In the features page](FEATURES.md#the-creation-screen).)

What the creation screen gains is drawn by DSCLOG with the game's own text
routine, each where the game draws nothing of its own: the AGE ([The age on
the creation screen](DEVELOPMENT-RULES.md#the-age-on-the-creation-screen)),
SUM ([Scores and hit points as
rolled](DEVELOPMENT-RULES.md#scores-and-hit-points-as-rolled)), STORE and
RECALL ([STORE and
RECALL](DEVELOPMENT-RULES.md#store-and-recall-on-the-creation-screen)), KITS
([Choosing one](DEVELOPMENT-KITS.md#choosing-one)), and the THAC0, below. The THAC0 shares the
age's sites (`CR_AGE`, `CR_AGE_CON`, `CR_NAME`, `CR_OPEN`), named in the age's
section.

**THAC0** (`CR_THAC0_DRAW`, always, whatever the rules): `THAC0: M18 R19` at `CR_AGE_X`
on the hit points' line, the THAC0 (`CR_THAC0_BASE`) less the game's STR
to-hit table's entry (DS:7C2h + STR) for M and its DEX missile table's
(`DEX_REACTION`'s, + DEX) for R, no less than 0. The game works the THAC0 out
again as the classes change, but `PROBE_THAC0` reads the kit from the party's
sheets, not the one being made, so the creature's `+1Fh` lacks a kit chosen on
the panel: `PROBE_THAC0` keeps the game's own, kit-less (`THAC0_GAME`,
`THAC0_SEEN` from `CR_OPEN` on), and `CR_THAC0_BASE` applies the sheet being
made's kit to it (`kits.thac0`: a Scholar 1 worse; a warrior THAC0 kit's is its
chosen weapon's alone, on the attack: `WAR_HIT`); with none worked out on
the screen (an EDIT), the creature's `+1Fh`, its kit in it. A kit chosen or
taken back (`KIT_SHOWN_DUE`, from `KIT_ROW`) draws the hit points and the
THAC0 again at the click's end (`KIT_REDRAW`), after a Battle Mage's, Mind
Warrior's or Arcanist's hit points are rolled again (`KIT_REROLL`) the age too,
whose PSP box that puts back. The hit points' box (the 7th, `CR_HP_BOX`) is widened to x 243
(`cr_thac0_box`; DONE's left is 244), so the game's putting it back clears the
line. It is drawn after each redraw of the hit points: the panel's, at
`CR_AGE` (65A89h, PSP after them), a click on CON (`CR_AGE_CON`), and `CR_HP`
(a site at 63AC3h, a click on the hit points, and 63EDAh); a click on STR or
DEX redraws neither, so `RL_SUM` (the scores' redraw) puts the hit points' box
back itself (`CR_BOX_PUT`, the far call's operand and the saved backgrounds'
segment read from the overlay's code beside its site, as `CR_NAME` does for
PSP's), draws the hit points again (`CR_PAIR_DRAW`, shared with PSP's) and the
THAC0. Verified in play (no log kept). Tests: `test_thac0_line`.

## Spell slots on the USE screen

([In the features page](FEATURES.md#spell-slots-on-the-use-screen).)

Always on, while the Loader (or its command-line dice log) runs. Two patches:
`use` (DSUN.EXE 70FBBh, "add sp,0Ch" in the USE screen's routine that labels
its LEVEL button, which runs whenever the screen is drawn or the level changes:
`INT F2h`, `PROBE_USE`) and `window` (2BBA9h, "xor ax,ax / pop si" at the end
of the game's routine that brings a window to the front and redraws it, which
repaints the screen's panels after a character or a level is picked: `INT F4h`,
`PROBE_WIN`, which draws only on the USE screen's window once `PROBE_USE` has
drawn on it, `USE_WIN`). Both call `USE_DRAW`: for the selected character
(the segment 3931h:25Bh) it finds, in `SLOTS_TEXT` (the header's +148: four
of `SLOTS_SIZE`, 128 bytes, one a member), the heading and the line keyed by
the list on show (DS:4AE8h, a byte a member: 1 MAGE, 2 CLERIC, 3 PSIONIC) and
the level (DS:4AECh, the LEVEL button's), and prints them in the empty panel
under the spells with the game's text routine (2B7Ah:16Dh). The PSIONIC list
has no lines, so it shows none.

The Loader writes the lines (`DiceLog.slots_lines`, `_write_slots`, only when
they change): for each kind of magic the member casts, a heading (`SPELLS
LEFT`, or `NO SPELLS IN ARMOUR` for a multiclass preserver's wizard spells
when the class restrictions bar them, `game.no_spells`) and a line a spell
level (`PRI 3/5`), each keyed by its first byte (`SLOT_KEY` 80h, the list
shifted 4, the level; 0 the heading), "|" between them. The numbers are
`game.spell_slots`: the slots left from the game's own counts, and the most
with WIS's bonus (`max_spell_slots`), at the levels the class levels reach
without WIS (the game gives WIS's bonus slots at levels the class can't cast
yet too). They are the Characters tab's.

## Detonate's blast on an item

([In How the game works](HOW-THE-GAME-WORKS.md#psionics); its line: [the dice log's page](DICE-LOG.md#checks-thief-skills-and-searches).)

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

([In the features page](FEATURES.md#what-hurts-a-monster-the-look-box).)

How: the patched game calls DSCLOG (`INT F5h`; INT 66h-6Fh can't be used:
the game calls those itself, looking for sound drivers) where the box has
drawn its first status rows; DSCLOG asks the Loader and waits a moment for
its answer, and prints the lines with the game's text routine. `INT F6h`, at
the end of the routine that closes the box, shows the whole description.

The AC is the one `PROBE_AC` last recorded for the creature
(`DiceLog.monster_ac`: the game works an AC out only for an attack, and keeps
none). Before any attack on it, `GameData.counted_ac` counts it as the game's
AC routine (58DD3h) does, as `THORNS_AC` does in DSCLOG: the sheet's base
(+27h, 10 for an armed man), less each worn item's plus and its type's AC
(types with +0Fh 80h, in the worn item list, +8), a fifth of a
gladiator's level and the DEX adjustment; the effects' part (Armor,
Barkskin...) is left out.

## Charges in item boxes

([In the features page](FEATURES.md#charges-in-item-boxes).)

An item that casts a spell has the spell + 1 in its `+0Fh` and its charges
left in `+0Eh` (the routine finishing an item's use takes one off, 721E4h,
unless its type's `+0Fh` has 2). `PROBE_ITEM_BOX` (`INT DAh`, at the end of
the routine filling an item's box, 8C1A1h, the item `[BP+6]`) draws
`Charges: n` in the row after the box's own lines (`IB_CHARGES`) when the
spell byte is below F9h (from there the game's own effects: a belt's STR, a
ring's AC...) and the charges aren't 0, but not for fruit (type 60, eaten
whole) nor scenery (a type whose `+08h` has both 20h and 40h: a door, a
mirror, a crank), where those bytes hold something else (`TYPE_SCENERY`).
With no charges to show, `IB_MATERIAL` (always on) draws `Hit -N` there for a
weapon (its type's dice count, `+0Dh`, not 0) with no plus (the item's `+14h`)
whose type's `+08h` has neither 80h (the game's own exemption: clubs, staves,
the chatkcha) nor 40h (no material), of wood (`-3`), bone (`-1`), stone or
obsidian (`-2`): `game.MATERIAL_TO_HIT`, the attack's own (the box's damage line
already has the material's damage off).

## No manual check

([In the features page](FEATURES.md#no-manual-check).)

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

([In the dice log's page](DICE-LOG.md#spells-saves-and-effects).)

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

## Looting a body: T and Shift+T

([In the features page](FEATURES.md#looting-a-body-t-and-shiftt).)

How: DSCLOG's `INT 16h` hook (`OUR_KEY`) hands each key to `LOOT_KEY` first. T
(1474h) or Shift+T (1454h) while the game's DS:05E6h names a container (a map
thing whose window is open; 9999 none) is made Escape, which shuts the window.
When the game reads the key (not a peek: `MK_READ`), DSCLOG counts it in
`loot_seq` (header +1846) with the container (`loot_thing`, +1848) and the mode
(`loot_mode`, +1850: 0 T, everything; 1 Shift+T, all but plain weapons). The
dice log's `_loot_pass` sees the count change and, once the window is shut,
`dsloader/loot.py` moves each item into the backpack of the first member up and
about with room, keeps what doesn't fit in the container, and writes a line of what
each took. The Loader pauses the game and prepares the destination backpacks before
relinking the container. If a write fails, it restores the saved bytes in reverse
order before the game resumes. Other keys, and T with no window open, pass as they were.

## Selling plain gear: S

([In the features page](FEATURES.md#selling-plain-gear-s).)

How: `SELL_KEY`, next in `OUR_KEY`, takes S (1F73h) or Shift+S (1F53h) only on a
shop's screen: `SHOP_LOOP` (the shop's loop, [beside its
shine](DEVELOPMENT-CONTENT.md)) stamps the BIOS tick in `shop_at` (+1858) on
each pass, and S counts only within `SHOP_FRESH` (2) ticks of it. The key is
made Escape, which shuts the shop, and when read it is counted in `sell_seq`
(+1852) with the member on show (the game's 3931h:25Bh, `sell_member` +1854)
and the merchant (DS:179Ch, `sell_merchant` +1856). The dice log's `_sell_pass`
then has `dsloader/sell.py` sell that member's plain gear (`plain_gear`: no plus
or power, not worn or held, not ammunition, metal, keys, nor what the shop won't
buy) at the game's price (SELL_PRICE's 60% with **Shops as in AD&D**), keeping
the magic for buyback, adding the money (MONEY_SEG 3781h:357h) and writing the
sale's line.

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

## The chance to hit before the swing

([In the features page](FEATURES.md#the-chance-to-hit-before-the-swing).)

`dsloader/hitchance.py`, all in the Loader: nothing is asked of DSCLOG and nothing is written to
the game. `predict(gd, attacker, target, rules, hidden, ac_gap)` reads what the game's attack set
(`DSUN.EXE` 58019h) reads and gives a `Swing` for each weapon that would swing; `line` words them
for the dice log's `Chosen with Tab` line (`targeting.update`'s `chance`), `brief` for the panel's
header (`combatlog.header`'s `chance`, the whole header while an enemy is chosen: its room is 103
pixels of the game's font, which `Round 2: Gerakis` nearly fills; `DiceLog._chance_brief` works it
out afresh every half second). The setting is `hit_chance` (`DiceLog.hit_chance`).

What the game's code does, and the Loader after it:

- **THAC0** before the target counts: `GameData.weapon_hits` (with `unarmed=True` a member with only
  a bow gets its fists for melee). The target's part, from 5B8:EDh (7C3E9h) and DSCLOG's
  `PROBE_STEALTH`: its Blur 2 worse, its Fogbolt 2 better, the Golden Girdle of Urnst 3 worse for a
  sword in melee.
- **AC**: `GameData.attack_ac(target, attacker, rear)`, the game's routine (58DD3h) and its effects'
  part (5B8:F2h, 7C557h) read from the code. The sheet's base (+27h) and the worn pieces whose type
  counts (+0Fh 80h): those on the arms, legs and chest (the item's +11h 0, 6, 9) are the armour the
  spells stand in for, the rest is added after; a shield (the type's word +0, bit 4) isn't counted
  from behind; a fifth of a gladiator's level in armour. Then the effects, on the target unless
  said: Spirit Armor (56) armour 4 at worst, else Improved AC (2) 6; Barkskin (57) 6 less a quarter
  of its level; Shielded (46) 4, not from behind; Magical Vestments (60) 5, 1 better each 3 levels
  above 5; Flesh Armor (59) 10 less its level; the DEX adjustment (508:6Bh), not from behind;
  Displacement (58) 2 better; Dispelling evil (52) 7 better against an attacker of race 14 (7AF65h);
  Blind (8) and Slowed (47) 4 worse each; Prot Evil (38) 2 better against an evil attacker (the
  sheet's +1Ah 3, 6 or 9); 4 better when the attacker can't see it (7BD4Bh: the attacker Blind, or
  the target Invisible, 23, or Invisible to Undead, 24, against the undead, unless the attacker has
  Detect Invis, 15); Biofeedback (4) 1 better. Not read: 7BD4Bh's first test of the target (5C0:20h
  with 1Bh), which makes it seen.
- **What DSCLOG adds to the AC**: a ring of protection's plus is counted (`PROBE_RING_AC`: every
  ring's, or with AD&D's protection rule the better one's and none over magical armour; the
  Templar's ring at the fountain was the first prediction's 1 off). The rest (`KIT_AC`,
  `PROBE_RING_AC`'s cloak, bracers and robe, `BOOTS_AC`) isn't worked out again in the Loader: at each AC the game works out (`DiceLog._ac`, DSCLOG's `PROBE_AC`
  record) the dice log keeps the game's figure less `attack_ac`'s for the same attacker and side
  (`DiceLog.ac_gap`, forgotten with the fight as `last_ac` is), and `predict` adds it. So an enemy
  with one of those is counted right from the first attack on it.
- **Which weapon**: the picker (5900Ah: [BP+6] the last weapon taken, -2 at first, [BP+8] the
  creature's item list, [BP+0Ch] the distance, [BP+0Eh] the count it returns) takes the items in
  hand (their record's +2 1, and 58FBFh answering 4Eh) whose type's range (+0Ah) is 1 when the
  distance is 1 or less, and above 1 when it is more; with none, the attack set swings the natural
  attacks (58127h). The distance is the caller's: a click on a foe attacks at once at 1 or less and
  walks up otherwise (1B123h), the attack pointer shoots (1B730h). So next to the target the melee
  weapons are given, farther off those and the missile weapon if its range reaches
  (`hitchance.squares`, the game's distance between footprints).
- **The facing** is a byte a creature at +5Bh of the round's segment (the one with the initiative
  scores, `game.INITIATIVE_SEG`; `game.FACING_OFF`, `GameData.facing`), below 0 while it faces
  nowhere. The attack set (5826Fh on) asks 96C:009Bh (0EB5Bh; "30:9Bh" in the overlay's code on
  disk, see below) for the direction from the target's square to the attacker's (the feet,
  `DS:669Dh` + 32 x thing, over 16): with `DS:01F8h` 1 (as the game starts) one of eight, by the
  signs of the two differences alone through the table at 3779:0000h (0 north, 1 north-east, and
  on clockwise to 7 north-west; straight north, east, south or west only when the other difference
  is 0), else one of four (0, 2, 4, 6: the nearer). With no facing yet it stores that
  direction (5834Eh: the target turns to its attacker) and the attack is from the front; otherwise
  the attack is from behind when the facing is that direction + 4 (5881Eh, modulo 8): the attacker
  stands opposite where the target faces. Not for an object (its thing's kind 1). From behind:
  [BP-1Ah] set, THAC0 2 less; a backstab ([BP-24h], 2 more) for a thief (the sheet's +12h, 400h)
  in melee with a weapon whose type weighs 40 or less (+4). `predict` gives the answer next to the
  target (`hitchance.way`, `WAYS`), both numbers farther off, and never from behind for a missile
  (DSCLOG's `MISSILE_REAR`) or a target facing nowhere. DSCLOG's changes after the game's are
  followed: a hidden one's attack from behind (`STEALTH`, read from the header at
  `stealth.TSR_STEALTH`), the Girdle of Back Defense (`ITEM_REAR`), a thief in heavy armour
  (`THIEF_REAR`), a Military Scout's and a Rescuer's (`KIT_REAR`), and only the round's first
  attack a backstab with Thieves as in AD&D (`STAB_FIRST`).
- **The order of the swings** is the creature's items' own (the picker walks the list): the left
  hand's weapon often first (Seneca's Hayneedle before her Shadowseeker, Jenna's obsidian sword
  before her bone one: `WeaponHit.order`), and that one is the backstab.
- **A hidden one's second weapon**: the attack set's flags [BP-1Ah] and [BP-24h] are cleared
  once, at its start (58036h), and DSCLOG's `STEALTH` bit is used up by the first weapon, so for
  the second the game lowers nothing (by the facing it is in front). Until #116 the flags stayed
  up: the AC from behind, the log's "from behind", and `STAB_FIRST` adding back a 2 never taken
  off (Seneca's Shadowseeker at the fountain, 2026-11-17, needed 12 where a plain swing needed 10).
  DSCLOG's `REAR_FRESH` now clears a flag the swing didn't pay for, so the second swing is a plain
  one, or from behind (no backstab) by the target's facing; `predict` gives that.
- **Segments in an overlay's code on disk** aren't the program's: the far calls and `mov ax,
  seg` of the overlay code in DSUN.EXE hold a segment's place in the table at file 46770h (8 bytes
  a segment, the first word its segment from the program's start), so `30h` is 096Ch, `0A0h`
  1A0Ah, `2E0h` 37BDh (the round's segment), `360h` 3972h (the things), `390h` 3BF6h (the
  effects), and `4E0h`, `508h`, `5B8h` the overlays' stub segments 41BEh, 41F1h, 42ABh.
- **The d20**: a 20 hits and a 1 misses whatever is needed (589E9h), so `chance` is 5 to 95; with
  the held-target rule a Paralyzed or Out Cold target is hit on any roll (`HELD_HIT`).

Tests: `tests/test_hitchance.py`. Verified: [log](https://github.com/daaki85/darksun-obsidian-edition/blob/main/playtest/logs/2026-11-17-hit-chance.md).

### Under the pointer

`dsloader/hover.py`, the Loader's alone again: a label's slot is all it writes. Setting `hit_hover`
(`DiceLog.hit_hover`), its own: it works with `hit_chance` and "Names over figures" off.

- **Which enemy: the game's own answer.** Every pass of the map's loop the game lights up the
  thing under the pointer (`DSUN.EXE` 1E126h, called with 270Fh for "the pointer's": it colours a
  creature by its side, +1Dh, and of the items only a body, object 1101, and blinks it, the thing
  lit in `DS:0BD1h`, the state in `DS:0BCDh`). It keeps the thing in **`DS:0BCBh`** (FFFFh: none),
  from the finder a click uses too (25B52h, DSCLOG's `PROBE_HIT`: camera x, y, pointer x, y; the
  draw list from its last entry, the front, down to the first in the view; a thing drawn, map
  record +0 bit 10h, with a picture, +0Fh not FFFFh, whose box holds the pointer, left +3 less the
  camera, top +5 less the camera less the signed byte +0Dh, width +12h, height +13h; then, on the
  map, the first whose picture has a pixel there, 147D:0166h, mirrored for a draw-list entry's +5
  bit 80h). So the label goes over what a click would act on: the figure in front where two
  overlap, nothing between a big figure's legs, nothing where an ally stands in front. Seen in
  every pointer mode. After the pointer has moved on, the word is the thing lit before for a pass
  (1E2C2h puts it back to take the light off), so `hover.target` believes it only with the
  pointer inside that thing's box (`hover.inside`, the finder's own test), among `rings.enemies`
  (as `_drawn` last found them), and `Hover.update` only when two looks running agree or the
  enemy is the one already labelled; a label up outlasts its enemy's last look by `LINGER` (0.2 s).
- **When.** A fight on, a party member's turn (`whose_turn` under 4), the map up (`DS:0BC9h` 1: 2
  with a window, a menu, the END menu, a talk), the pointer's mode (`DS:11B8h`) 1 walk or 4
  attack (not 2, the eye: a click there only looks, so there is nothing to foretell), and the pointer not on the combat log's panel (the header's `TSR_PANEL_ON` and
  `TSR_PANEL_TOP`: the finder knows nothing of the panel and answers with the enemy behind it).
  The turn passing takes the label off in the same pass.
- **One number** (`hover.swing`, from `predict`'s swings in the game's order; a label is 128
  pixels): next to the enemy the first melee weapon. Farther off the click decides. The walk
  arrow's (1B0E9h: at a distance above 1 the member walks up) is the first melee weapon's, and the
  eye shows that too. The attack pointer's (1B67Bh on: with a line of sight, 898:00A4h, the attack
  at the distance between them, so the picker takes the missile weapon) is the shot's when
  `predict` has one (its range reaches) and the quiver holds something (`quiver.quiver`; with
  none the game walks the member up), else the melee number. Not read: the line of sight (a
  blocked shot's click does nothing, the label still shows), and which weapons have already swung
  this turn (after a kill that keeps the turn, Seneca's label was her Hayneedle's 12+ and the
  swing left her Shadowseeker's 11+).
- **The words** (`hitchance.over`): `12+ (45%)`; next to the enemy `Behind 10+ (55%)`, `Backstab 8+
  (65%)`, `Unseen 10+ (55%)`; where the walk decides `14+ (35%), behind 10+` (`, backstab 8+`: 125
  pixels at its widest in the game's font); a held target with the rule `Hits`.
- **The label** (`Labels.hover`): one standing label of the lowest priority (`HOVER`, below the
  usable names' `NAME`), kept up `HOVER_FOR` past its last asking. It takes a free slot only and
  waits while another label is over its figure; `Labels.show` gives its slot to a "Miss", a
  spell's name or a charge over that figure, or to any of them when no slot is free. Asked for
  again with the same text it writes nothing.
- **The pass** (`DiceLog._hover_pass`, every pass beside `_usable_key`): with the pointer off every
  enemy, four small reads (9 microseconds measured); resting on one, 16; the prediction is made
  again only when the attacker, the enemy, the pointer's mode or either one's feet changed, or
  `AGAIN` (0.5 s) has passed (755 microseconds).
- **A label taken off was left on the screen** (found here, with "Miss" as with this label): in a
  still scene DSCLOG's `LABEL_ERASE` showed for one frame and the label was back until something
  else drew the view. `Labels.took_off` now tells the dice log when a label has been taken off,
  moved or reworded, and it has the view drawn again (`shadows.redraw`, `DiceLog._labels_gone`):
  the label is gone 0.2 s after the pointer leaves and stays gone. And a Loader stopped with a
  label up left its slot filled for good: `Labels.tick` empties the slots that aren't its own
  once, at its first look (`Labels.attached` for a game newly attached).
- **Measured** (the fountain's fight, a still scene, 10 s each): the pointer on a guard with the
  label, 23.9 frames shown a second and 933 passes of the map's loop; the same with the switch
  off (the game's own blinking of the figure), 24.1 and 23.9 frames, 2,018 and 2,054 passes; the
  pointer away, no frames (nothing drawn) and 3,168 passes either way. So the frames are the
  same, and the passes a label costs are DSCLOG's upkeep of any label.

Tests: `tests/test_hover.py` (the box and the game's word believed inside it; the swing by the
pointer's mode; every text within a label's width in the game's font; "Miss" and charges before
it, no write for the same text; two looks, the linger, the turn, the map, the panel; the switch
with the other two off; the view asked for again). Verified: [log](https://github.com/daaki85/darksun-obsidian-edition/blob/main/playtest/logs/2026-11-18-hit-chance-hover.md).

## Squares in reach

([In the features page](FEATURES.md#squares-in-reach).)

How: the Loader works out where the party member whose turn it is can still walk
(`dsloader/squares.py`, from `DiceLog._drawn`, four times a second) and DSCLOG marks those
squares in the floor pass.

- **The Loader's side.** `mover`: in a fight, the party member whose turn it is (`whose_turn` under
  4), its square (its thing's place / 16), its movement points (a word a creature at 37BD:022Bh)
  and bit 0 of its turn's flags (37BD:01D5h, "can still walk": without it the points count as 0).
  `reach` on the game's live walk map (the far pointer DS:0556h, 128 x 98 bytes): the squares whose
  shortest way (`costs`: Dijkstra, 10 a straight step and 14 a diagonal one, a square with bit 40h
  barred, corners cut) costs no more than the points, and the squares of a clear diagonal run whose
  last step is begun with 10 or more. `bitmap` makes DSCLOG's `SQ_MAP` of them, 32 x 32 squares
  with the member in the middle (kept on the map at its edges): a Move of 15 fits; the far squares
  of a hasted walker's reach are left unmarked. `Squares.update` writes it (with `SQUARES_ON` 0
  around the write) and asks for the view to be drawn again (`shadows.redraw`) when it changes;
  while the member walks the marks are left as they were until two looks running find it on the
  same square with the same points, as each change has the whole view drawn again. LIGHT is made
  as the dust makes it (`dust.light_table`) when the palette is read again, and the shadows'
  upkeep is asked for with the switch on (`needed`). Out of a party member's turn `SQUARES_ON` is
  0; a DSCLOG met with it left on by another Loader is told so.
- **DSCLOG's side** (`TINT_PASS`, called before `RING_PASS` in `SHADOW_PASS`, so the Tab ring is
  drawn over the marks and both under the figures): for each set bit of `SQ_MAP` (with the
  header's `SQUARES_ON`, +1890, set) the square's middle on the screen (square
  x 16 + 8 less the camera) goes to `RING_POINTS` with `SQ_DOTS`, a quarter of a cross five pixels
  each way, mirrored as the rings' quarters are, and `RING_PX` lightens each pixel four times
  (`R_KIND` 3) through LIGHT: `RING_PX` takes its table from the word `R_TAB`, `FAR_RED` but for
  this pass. LIGHT has a lighter colour only for what the dust takes for ground (sand, dirt, the
  pens' paving); a pixel of any other colour is darkened four times through DARK, the shadows'
  table, instead (`RING_PX`'s `.none`, at a pixel's first look only), so a floor the dust has no
  colours for still shows its crosses, dark ones (seen in the game only with LIGHT emptied in
  memory: the pens' and the arena's floors are all ground to the dust). Things drawn over the
  floor (a rug, the arena's stone platform) are drawn after the pass and cover the crosses under
  them. A row or a square whose cross is all outside what is
  being drawn (a walker's rectangle) is passed over before `RING_DOT` tests its pixels.
- **Where it is kept.** DSCLOG's segment and upper memory had no room left for the pass and its
  map ([the limits](DEVELOPMENT-INTERNALS.md#the-limits)). `TINT_PASS` in the segment is a test of
  `SQUARES_ON` and a call; the loop is `TINT_FAR`, code in DSCLOG's tail run through `TAIL_CALL`
  ([DSCLOG's segment](DEVELOPMENT-INTERNALS.md#dsclogs-segment)), which reaches the segment's
  variables through GS and `RING_POINTS` through a far entry (`RING_POINTS_FAR`). `SQ_MAP` (130
  bytes) is in DSCLOG's own PSP, the 100h bytes before its header, at 5Ch (`squares.SQ_MAP_PSP`):
  the room DOS keeps for a program's FCBs and command line, which nothing reads once DSCLOG has
  stayed resident, so the map costs no upper memory. The Loader writes it at the header's address
  less 100h plus 5Ch.
  `FLOOR_ENTER` takes `SQUARES_ON` beside the shadows', the dust's and the rings' switches.
- **Why one click's reach and not the bare rule.** By the game's rule ([moving in a
  fight](HOW-THE-GAME-WORKS.md#moving-in-a-fight)) a square is in reach when a square beside it
  is reached with 10 points to spare, but the game's own route takes its diagonal steps first, so
  only an all-diagonal way ends on a step begun with 10 to 13: marked by the bare rule, a rim of
  squares would each be a step out of a click's reach, and that click spends the whole Move.
  What is left: the game's route round a wall can cost more than the shortest way (8 points
  more seen, through a doorway off the straight line), so the last cross or two behind a wall can
  take two clicks. The game's route finder (segment 8BBh, 0DFB0h-0EAC1h: a straight run, the
  barred stretches walked round along their edges, then straightened) is not played out.
- **What the game has** (file offsets): the round's start gives each combatant its points
  (57566h, Move x 10, then doubled or halved); the walker's step (1BFB6h) asks the flags
  (41BE:008Eh, 590B2h) and then takes the step's cost from the table at DS:055Ch (59106h: under
  10 left, the points zeroed and bit 0 cleared); a square is barred by bit 40h of its byte
  (142F:00DCh, 197CCh), over a wide figure's whole footprint (2067Bh); the path finder tests only
  the square stepped into (0E711h); F10 in a fight (the key table at 1BC5Bh, 4400h to 1B83Ah)
  puts the member back where its turn began (DS:4966h, 4968h) with its points (DS:4964h), but not
  its flags' bit 0.
- **The cost** (measured in Pehtucl's ambush, a member walked back and forth along a row,
  `playtest/squarecost.py`, on and off in turn): 154 map units a second with the marks against
  157 without with 250 points in memory (the whole bitmap marked), 157 against 160 with a real
  120; a frame a second. Before the pass passed over what is outside the clip, and with the marks
  made again at every step, the same walk was 131 against 156.

- **R shows and hides them** (`DiceLog._squares_key`, every pass): with the switch on (`squares`),
  the map up (`DS:0BC9h` 1) and a fight on, R or Shift+R flips `squares_shown` (settings.json,
  on by default), DSCLOG's marks are written at once, a line goes to the dice log and a word
  floats over the member whose turn it is (`_float`: with "Names over figures" on). The marks are
  drawn while both `squares` and `squares_shown` are on. **The key costs DSCLOG nothing**
  (`dsloader/keywatch.py`): DOSBox's keyboard handler puts every key into the BIOS keyboard
  buffer in the game's memory (sixteen words from 0040:001Eh, the tail at 0040:001Ch), and the
  game reads its keys through INT 16h, which leaves the words where they were; the keys pressed
  since the last look are the words between the tail then and the tail now. The Loader only
  looks, so the key reaches the game as well: R is in none of the game's key tables ([the game's
  keys](HOW-THE-GAME-WORKS.md#the-games-keys): the map's and the fight's at DSUN.EXE 1BC5Bh, 26
  keys; the map's second at 71C1Bh, overlay 4272h, 33 keys; and its letters' jump table at
  71BE3h, c to v), and pressed in the game it did nothing to see. A key the game does use is
  counted by DSCLOG instead and taken from the game (L, T, S, F5, F9). Two presses between two
  looks leave things as they were.

Tests: `tests/test_squares.py` (the rules on a made-up walk map, the bitmap, the upkeep),
`tests/test_squares_drawing.py` (`TINT_PASS` in the emulator: the crosses, the clip, the rings'
red kept), `tests/test_keywatch.py` (the buffer's keys, and R). Verified:
[log](https://github.com/daaki85/darksun-obsidian-edition/blob/main/playtest/logs/2026-11-18-squares-in-reach.md),
R and the PSP's map: [log](https://github.com/daaki85/darksun-obsidian-edition/blob/main/playtest/logs/2026-11-18-modernisation-features.md).

## F10 takes a whole move back

([In the features page](FEATURES.md#f10-takes-a-whole-move-back).)

`dsloader/moveback.py`, the Loader's (`DiceLog._move_back_pass`, every pass; setting
`move_back`), and DSCLOG's `F10_PIN` (always on), which leaves a pinned member where it is. The game's F10 (DSUN.EXE 1B83Ah, key 4400h of the table at 1BC5Bh) acts with a
fight on (the word at 377Eh:0019h neither 0 nor 1), a party member's turn (`DS:4979h` under 4) and
the member standing still (1BF9Dh: bit 20h of its map record's first byte, `DS:6694h` + member x
20h): it places the member on the turn's first square (`DS:4968h` x, `DS:4966h` y) and writes the
turn's points (`DS:4964h`) into the creature's movement word (37BDh:022Bh). The three words are
kept by 1E4D6h as a member's turn comes up. It restores nothing else: not the attacks made, and
not bit 0 of the turn's flags (37BDh:01D5h, "can walk"), which the step that leaves under 10
points clears with the points (591BCh).

Everything in DSUN.EXE that takes the bit away, found by its instructions' bytes: 591BCh (the
last step: the points zeroed too); 786CBh (an effect, numbers 22h and 33h, on a party member:
the points untouched); and the whole word zeroed at 1C090h and 78637h (the turn over or lost),
or set to 2 at 58093h. So the Loader sets the bit again only after it has seen, in one turn of one
party member and in this order: the flags with the bit; then the same flags without it and the
points 0; then, the flags still those, the points equal to `DS:4964h` (10 or more), the member on
the turn's first square and standing still. It also forgets the walk the points ran out on (FFh at
3972h:0377h + thing x 1Ch, 0 at 3972h:08AAh + thing x 13h), which the game would otherwise go on
with from the square F10 put the member on.

**Never for a member pinned at F10**: the pin (786A9h-786CBh, in the routine that gives an effect)
clears bit 0 when effect 22h or 33h lands (34 Paralyzed, 51 Stuck; nothing else there touches bit
0, and 591BCh and 786CBh are the only `and word [bx+1D5h], 0FFFEh` in DSUN.EXE) and leaves the rest
of the flags and the points alone. One landing after the last step therefore leaves the flags as
the step did, and the order alone took it for the last step: the first version gave such a member
its walk (seen in the game: Seneca, Paralyzed after her last step, walked a step on F10 before the
game ended her turn). So at F10 the member's effects are read (`GameData.effects()`, owner its
combatant): with 34 or 51 among them nothing is written, no line is said, and the turn's sequence is
forgotten. Since DSCLOG's `F10_PIN` (below) the game's F10 no longer moves such a member, so the
mend never sees the points come back for it; the check stays as a second guard.

**A pinned member isn't moved (DSCLOG's `F10_PIN`).** The game's F10 doesn't look at effects: a
member Paralyzed or Stuck, after its last step or with movement left, was put back on the turn's
first square with the turn's points (seen in the game: Lex, Paralyzed by a memory edit after his
last step, back on his first square with 120 points). The site `F10_PIN` (`NS_IMAGE + 122`,
gamepatch `f10_pin`) replaces F10's "or ax,ax / jz 1B872h" at 1B86Bh, the test of 1BF9Dh's answer
(0: standing still) and the jump to the move, with INT 98h, the site's number and a NOP; the "jmp
1BC55h" after it, the key's end, is the game's. DSCLOG returns past that JMP, to 1B872h (the IRET's
IP 4 on: `F10_TO_MOVE`), only for AX 0 and the member on its turn (`WHOSE_TURN`, DS:4979h, its own
combatant number) holding neither effect 34 nor 51 in the game's table (`ns_has`, as `held_hit`
reads Paralyzed); else it returns to the JMP and F10 does nothing. AX and every other register are
kept; nothing after either way reads the flags (the IRET's own come back). 32 bytes of the segment.
Nothing else about F10 changes: a member standing still and not pinned is moved as the game does,
and a pin on anyone else counts for nothing.

**Never after an attack**: either of two bytes of the creature's ends it for the turn, the swings
made (37BDh:0181h) or the attack commands given (37BDh:01ABh). The first alone is not enough: an
attack ends the member's turn (the flags zeroed), but one that kills leaves the turn, with the
swings' count back at 0 and the commands' at 1, and F10 then still puts the member back with its
points. The first version of the mend read only the swings' count and gave the walk there (seen
in the game, and mended before anything was committed as finished).

Tests: `tests/test_moveback.py`; `tests/test_f10pin.py` runs `F10_PIN` in Unicorn (Paralyzed or Stuck on
the member: no move; neither, or a pin on another combatant: the game's). Verified:
[log](https://github.com/daaki85/darksun-obsidian-edition/blob/main/playtest/logs/2026-11-18-modernisation-features.md)
(F10 with movement left: the game's, nothing written; after the last step: walks again; after a
kill made on the last step's square: put back by the game, no walk);
[log](https://github.com/daaki85/darksun-obsidian-edition/blob/main/playtest/logs/2026-11-20-f10-after-spell.md)
(after a spell: a cast zeroes the flags, nothing written, Curse, Reflected Image and Magical Stone,
after the last step and with movement left; Paralyzed by a memory edit after the last step: the
first version gave the walk, the mended one none, and a plain last step still walks again);
[log](https://github.com/daaki85/darksun-obsidian-edition/blob/main/playtest/logs/2026-11-20-f10-held-stays.md)
(`F10_PIN`: Paralyzed after the last step, Stuck after the last step and Paralyzed with movement
left, every foe Paralyzed too: F10 left the member on its square with its points, no Loader line;
the pin taken off, F10 the game's again, after the last step with the walk given back);
[log](https://github.com/daaki85/darksun-obsidian-edition/blob/main/playtest/logs/2026-11-20-f10-real-pin.md)
(a real pin, no memory edit to it: Stuck by the game's Web on the member's own walk, with movement
left and after the last step, and at a Stuck turn's start; Paralyzed by the member's own Hold
Person turned back by Spell Turning, before and after a walk: F10 left the member on its square
with its points every time, no Loader line; the pin taken off, F10 the game's again).

## Showing what can be used: Alt

([In the features page](FEATURES.md#showing-what-can-be-used-alt).)

The Loader's alone (`dsloader/usable.py`); DSCLOG has nothing new. It reuses two
things the helper already draws for whatever the Loader names: the rings
(`RING_PASS` rings every thing of the game's draw list whose byte in `RING_TAB`
isn't 0, whatever the thing is and however many) and the four floating labels
(placed over any thing in the draw list).

- **The key.** The BIOS's shift flags, `0:0417h`, bit 3 (either Alt), read from
  the game's memory every pass of the dice log (`DiceLog._usable_key`: 50 ms
  apart in the window, less in the windowless logs), so the marks go up and
  down within a pass of the key, not at the next of the quarter-second looks
  that keep them up (`_drawn`, `_marks`). Alt alone sends the game no key.
  DOSBox lets go of every key when its window loses the focus, so Alt+Tab
  leaves no flag set (tried: the flag cleared as the focus went); as a backstop
  Alt read as held for `STUCK_AFTER` (30 s) takes the marks down until it reads
  clear again. Ctrl wasn't chosen: Ctrl with the function keys is DOSBox's
  (Ctrl+F9 ends it).
- **What is marked** (`usable.marks`), among the draw list's entries (far
  pointer `DS:6690h`, count `DS:1F72h`: the whole region's) that are creatures
  or items in the things table (`3972:0C36h`; the region's own scenery has
  numbers past 519, and drawn things of kind 0, banners, have no record):
  - a creature outside the party, alive: a person if a talk trigger names it,
    else a foe if its side (`+1Dh`) is neither the party's nor 4 (neutral), else
    nothing (in the pens Legcrusher and the Arena Guards are on side 2 and have
    talk triggers, so the side alone doesn't tell);
  - an item: a body (objects 1101 and 2666); a door (item types 17h and 72h,
    the only two the game's objects use for doors, unless named a wall: the two
    "Brick Wall" doors are secret); a container (its `+8` a list); anything a
    use, look or use-with trigger names; anything that can be picked up (its
    type's `+08h` without 20h: 60h is scenery).
- **The triggers** are read where the game keeps them, not from the region's
  MAS script, so those a script adds or clears as the story goes count too. One
  table, 13 bytes a trigger, at the far pointer `DS:42CCh`: `+0` the place in
  the script, `+2` the script, `+4` the object's id (the object number negated,
  as the scripts write it), `+6` a use-with trigger's other id, `+0Bh` the
  next one's index (FFFFh the last). The lists' heads are words in segment
  `377Eh`: `+0Fh` talk, `+11h` attack, `+13h` look, `+15h` use, `+17h` use with.
  `DSUN.EXE` 967Ah is the game's own "what can be done with this thing" (it
  takes the thing's id, field 48h through `1A0A:0651h`, walks each list at
  9720h and returns a bit for each that names it: 4 talk, 2 attack, 8 look, 10h
  use, 20h use with); `usable.triggers` walks them the same way. A thing's id
  is an item record's first word and a creature record's `+6`.
- **The rings** (`rings.Rings.update`, which owns `RING_TAB` and its colour
  table, `RED`): handed the marks' table, out of a fight it writes that (ring
  kind 1) and a gold table (`rings.gold_table`: each colour's one clearly nearer
  gold among the palette's, as the red one is made); with none, or in a fight
  whatever is handed in, the Tab ring's table and the red one. The table and
  colours first, `RINGS_ON` last, and the view drawn again. Only things in the
  view or within 16 pixels of it are marked, and the marks are made again as
  soon as the view has moved (`Usable.changed`): `RING_PASS` goes round every
  marked thing's ring at each floor pass, on the screen or not.
- **The names** (`labels.Labels.names`): the four named marks nearest the
  pointer (`DS:A133h`), as standing labels of the lowest priority (`NAME`): they
  take free slots only, give theirs up to a "Miss", a spell's name or a charge,
  and stay while asked for whether or not the floating names are switched on. A
  name's bottom row is 3 rows over the thing's picture (the map record's `+8`),
  at most a man's 34.
- **Measured** in DOSBox (the slave pens' hall, the party walking, 20 s runs
  alternated): nothing marked 19.5 frames a second and 155 map units a second
  walked; 3 marked and 2 names 18.0 and 131; Alt held with the switch off as
  nothing marked. A first build that marked all 87 usable things of the region
  cost as much with one ring on screen (16.5 and 120), which is why only the
  view's are marked. A bounds test in `RING_PASS` before its points would take
  most of the rings' share.
- Switch: `show_usable` (on).

Tests: `tests/test_usable.py` (what is marked on a made-up map: people, foes, doors, containers,
bodies, items, things with a trigger; not the party, the dead, secret doors or scenery; the
trigger lists walked; Alt's flag and a stuck one; the rings' table and colours shared with the
Tab ring, gold out of a fight and red in one; the names' slots).

Verified: [log](https://github.com/daaki85/darksun-obsidian-edition/blob/main/playtest/logs/2026-11-17-show-usable.md) (the marks in the pens and at the
fountain, a fight beginning with Alt held, bodies after it, Alt+Tab and Alt+Enter leaving nothing
stuck). Not seen: a door opened or a talk begun with Alt held, any region but the pens, GOG's
DOSBox on Windows.

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

## M, U and I: open a screen, close it again

([In the features page](FEATURES.md#m-u-and-i-open-a-screen-close-it-again).)

`MAP_KEY`, in DSCLOG's `INT 16h` handler for both reads and
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

## The whole party in view

([In the features page](FEATURES.md#the-whole-party-in-view).)

The map's party is one figure while `DS:1168h`
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
(`party_spread`, always on: [the switches always on](DEVELOPMENT-RULES.md#the-switches-always-on)).

## The view in fights

([In the features page](FEATURES.md#the-view-in-fights).)

The game writes the view's place (`DS:1178h`,
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
party members walking as well as monsters. The patch (`camera_still`, once a
switch, always applied now, `CAMERA`) rewrites that call's 54 bytes of set-up: while `IN_COMBAT`
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

With DOSBox's `autolock`, as GOG's setup has it, the first click in the window only takes the
mouse; the next one skips the scene.

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

## Spells on the Effects screen

([In the features page](FEATURES.md#spells-on-the-effects-screen).)

A click on an effect's icon on the Effects screen ends it in the game; with the
mod (`gamepatch.EFFECTS_KEPT`, always in the game's copy), a spell's effect
is left on: two jumps in the screen's click handler (DSUN.EXE 7F226h and
7F236h, the patches `effects_click_low` and `effects_click_high`) go to its way
out instead of to the routine ending an effect. A psionic power's (spells 8Ah-ABh) still ends, as stopping it there is
how a power is dropped.

## CHOOSE A SPELL's grid

([In the bugs fixed](GAME-BUGS.md#numbers-and-pointers-on-screen); `spellgrid.py`.) The window (WIND 17500 in RESOURCE.GFF) has 21
places for the spells on offer, APFM 2BCDh-2BE1h, which the routine (85560h) fills in that order:
the first 15 are the middle five of seven columns, row by row (x 47 to 123, y 24, 44, 64), the next
three the right-hand column (142), the last three the left-hand one (28). Past 15 spells the grid
sat right of centre: the game's 4th level has 16 wizard spells, and with the new spells the 1st has
18 (seen 2026-11-16, compared with the window in the unchanged game's RESOURCE.GFF, the same). The
Loader's copy of RESOURCE.GFF (`icons.py`'s chunks) has the first 18 places six to a row, 19 apart,
filled row by row and centred where the seven columns were (x 38 to 133); no level offers more, and
the last three stay as they are. The routine and its clicks are the game's: only the places move.

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

The other pages are `SAVB`, `SAVC`, `SAVD` and `SAVQ` (the QUICK page, DSCLOG's fifth letter:
`PAGES`, `sp_letters`), not `SAVE11` on, so the game's own
window never sees them: it puts each save it finds in the row its number names,
with room for ten, and a `SAVE11.SAV` would be written past the end.

Saves under their names (`dsloader/namedsaves.py`): every few seconds the
Loader looks at the 40 slots' files of pages 1 to 4 (not the QUICK page's: its slots are written
over in turn, each with the day and time in its name, so a copy of each would only come and go;
`cloud_saves` before the game folder, as
GOG's DOSBox mounts it over the folder), and copies a save whose bytes differ to
`Named saves/` as `Page P slot NN - NAME.SAV`, the name from the save's
`STXT 1` (up to its first NUL; characters Windows won't take become `_`). A
slot's copy under another name is removed. **Put a save in a slot...** copies
a file with valid party tables back as `SAVE`/`SAVB`/`SAVC`/`SAVD` + the slot, through a temporary file,
the slot's save first kept as `Replaced - Page P slot NN - NAME.SAV` (which
`sync` doesn't match, so never removes).

### Quick save, quick load and autosave

([In the features page](FEATURES.md#quick-save-quick-load-and-autosave).) `dsloader/quicksave.py`
holds the policy; DSCLOG has two small parts, `QS_KEY` and `SAVE_TICK`.

**The game's own keys.** On the map the game reads F1 (the SAVE window, the game going on
after), F2 (the LOAD window), F3 (quit), F4 (music on and off) and, from its key table at
DSUN.EXE 1BC5Bh, F5, F6, F9 and F10. F5 (1B811h) draws the view again and nothing else; F9 (an
overlay's entry, 810DCh) breaks the camp the game's rest routine at 80Fxxh makes (the party's
creature records' +1Dh 4, a fire and bedrolls put on the map), and does nothing otherwise. Neither
showed anything on the map in the pens. So F5 and F9 are the two keys, and while the party camps
(+1Dh 4) the Loader gives both back to the game.

**The keys.** The Loader writes the two keys into DSCLOG's header (`QS_KEYS`, +1878; FFFFh with
the switch off, so they stay the game's). `QS_KEY` (from `OUR_KEY`, the INT 16h hook) takes one
and counts it (`QS_SEQ`, +1882, a word each) only if the map's main loop ran within the last two
BIOS ticks. That loop (`main()`'s, the one caller of the routine `PROBE_SCROLL` is in) doesn't
run while a window, a talk, a screen or a menu is up (the game's DS:0BC9h is 2 then), nor on an
enemy's turn.

**A save.** The Loader writes the file (the game's save path, DS:4B81h, `.\` as the Loader starts
it, then `SAVQnn.SAV`) and the name into `SAVE_TEXT` (112 bytes in the tail, its offset at +1888)
and sets `SAVE_REQ` (+1886) to 1. `SAVE_TICK`, called from `PROBE_SCROLL` (its work is `SAVE_FAR`'s,
code in the tail run through `TAIL_CALL`: [DSCLOG's segment](DEVELOPMENT-INTERNALS.md#dsclogs-segment)), sets it to 0, and
unless a fight is on (the word at 377Eh:0019h, which the game's own menu tests: "CAN'T SAVE
DURING COMBAT") calls the routine the SAVE window's wrapper calls, the overlay entry 4242h:0089h
(DSUN.EXE 6912Dh, `save(far file, far name)`), through its stub as `GIVE_XP` calls its overlay;
then leaves 3 (saved), 4 (the routine returned 0) or 5 (a fight). The routine writes the SAVE
chunks and `STXT 1` into `DARKRUN.GFF` and copies it to the file; it shows nothing. The Loader
gives up a request not taken within 6 seconds.

What the window does besides, and why the direct call needs none of it (Verified:
[log](https://github.com/daaki85/darksun-obsidian-edition/blob/main/playtest/logs/2026-11-17-quick-save.md)):

- opening the window (overlay 428Ah, 7452Dh) closes the item boxes (1587h:22BAh), stops the
  map's drawing while the window is made (1587h:2CCBh, undone by 2C8Dh at the end) and sets the
  pointer's shape (191Fh:0B36h, 4): all for the window;
- the wrapper (7468Bh) shows SAVING GAME and GAME SAVED and, after the save, writes the 11-byte
  `PREF` 100 chunk (music, sound and such) into **`CHARSAVE.GFF`**, not into the save; a load
  reads it from there if it is there. `DARKSAVE.GFF` is written by neither.

A save by the direct call and one by the window at the same game second (the look pointer up,
which stops the clock) differ in the name and in six words of `SAVE 1` (the map objects' records,
32 bytes each: the word at +15h of the four party members' and two more), which hold a picture's
slot number while the map is open and the picture's own number (negative) while a window has it
closed. Loading either gives the same game (the same places, clock and numbers, in the same
session and from a fresh start), so a load makes those words again.

**Safe moments.** `PROBE_SCROLL` is called only from the top of `main()`'s loop (1A947h), the same
loop whose event dispatch reaches the game's own SAVE window: a save from there is made at a
moment the player could have pressed F1. It is never inside a talk or a message box (their loops
are nested and don't come back to it), and scripts that wait across passes of the loop (Kurzak's
call, the escort to the fountain) are saved by the game's own save in the same state. Tried: a
quick save with Kurzak's call pending, and autosaves after the fountain's ambush, on coming into
the arena and after Scar's bout there (the arena's patience running), each loaded from a fresh
start and played on: the call still stood, the Announcer and the bout began, the arena's next
bout came.

**Quick load.** The Loader pokes Q into the two file names (as DSCLOG's page buttons do), sets
the window's chosen row (3BA7h:04E4h) to the newest save of the page, and sets `SAVE_REQ` to 2:
`SAVE_TICK` calls the overlay entry that opens the LOAD window (428Ah:0020h, what F2 and the
menus call). The load itself is the window's (Enter or LOAD). The window never opens on
the QUICK page by itself: whenever it is shut (the map's loop running, DS:0BC9h 1) and the page's
letter is Q, the Loader writes back the letter of pages 1 to 4 it saw last (`_page_back`), so a
save made by hand doesn't land in a slot that is written over in turn. Seen in the game: an F1
save after an F9 window had gone to `SAVQ01.SAV` before this.

**Autosave.** The Loader asks for one when the region (DS:117Ch) has changed, or a fight has
ended, and for 4 seconds since the map's loop has run with the game on the map (DS:0BC9h 1) and
no fight; not while a game is loading (the dice log's `_party_check`: the party changed or the
clock went back) and, after a fight, not within a minute of the last autosave. The Loader keeps
observing the area and fight while a keypress or an in-progress request has priority. A due
autosave waits for a free request slot and the usual map conditions. The dice log's load signal
resets the area and fight timers. Slots 1-5 hold quick saves and slots 6-10 hold autosaves. Each
kind takes its first empty slot, then its oldest file.

**The disk.** The game's save shows "Disk Space Low !!!" in a box that waits for a click when
DOS reports under about 2.7 MB free. DOSBox always reports 262 MB for a mounted folder
(`localDrive::AllocationInfo`), so the box can't come up there; the real danger is the real
disk, and the Loader asks for no save with under 4 MB free in the saves' folder, saying so.

**Time and memory.** A save took 0.34 s from the request to the answer (five measured, 20,000
cycles), the game standing still for it; the game's memory read the same before and after
(95 KB of DOS memory free, `heapcheck`). What the two routines and their text cost DSCLOG:
[the limits](DEVELOPMENT-INTERNALS.md#the-limits).

Tests: `tests/test_quicksave.py` (the slots' rotation with the two kinds kept apart, the names,
when an autosave is due: a new area, a fight over; not while a game loads, a window is up or the
disk is nearly full; what is asked of DSCLOG and said; and DSCLOG's `QS_KEY` and `SAVE_TICK` in the
emulator).

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

Measured in the slave pens with the whole party walking and everything on
(`playtest/framerate.py`, which counts DSCLOG's page flips, the steps run and
lost, and the leader's map units while walking), with the cheaper drawing of
2026-11-08 below (playtest/logs/2026-11-08-drawing-savings.md; the features
page's [steady pace GIF](FEATURES.md#game-speed) is from the same save):

| Slave pens, whole party walking, everything on | Pictures a second | Steps lost a second (of 96) | Walking, map units a second |
|---|---|---|---|
| 20,000 cycles, steady pace off | 18.9 | | 103 |
| 20,000 cycles, steady pace on | 15.5 | 25 | 112 |
| 35,000 cycles, steady pace on | 18.9 | 14 | 141 |

Before that drawing was made cheaper (the first measurements of steady pace):

| | Pictures a second | Steps lost a second (of 96) | Walking, map units a second |
|---|---|---|---|
| 20,000 cycles, steady pace off | 16.6 | | 80 |
| 20,000 cycles, steady pace on | 10.5 | 26 | 114 |
| 35,000 cycles, steady pace on | 15.7 | 24 | 112 |
| 20,000 cycles, the mod's drawing off, steady pace on | 16.4 | 22 | 121 |

A fixed schedule of 70 frames a second on the clock (a tick 70 units, a frame
96) doesn't suit the game: the map draws only when something moved, about 17
times a second, so every frame looks late, and at 20,000 cycles it showed 6
pictures a second and left out 17. The Loader's two speeds run DOSBox's dynamic core (GOG's settings run
this game on the slower normal core): the same cycles do more, at about a third
less of the computer's time.

**Steady pace** (`gamepatch.STEADY_PACE`, DSCLOG's STEADY PACE): the map's
frame (DSUN.EXE 1E8E4h) calls the step for everything (`call far 1DF3:26DC`,
which also builds the list of what moved at DS:57D0h, 10 bytes each: where
the thing was drawn, its size, the thing) and then the drawing of that list
with the page flip (`call far 1DF3:15EA`), the flip waiting for the vertical
retrace; the frame is drawn only when something moved. The step runs only when
DS:1F7Eh is set, which the game's timer (1DF3:29E8h, with the game's clock
DS:11D6h, 96 ticks a second) does at each tick, and clears it: a step a tick
at most, and a tick passed while drawing is a step lost. The "think" that
starts a figure on its next square runs once a step, for one creature at a
time, so catching up a figure's animation steps alone (tried before) only made
it wait at the end of its square. PROBE_PACE_PASS counts the steps run (the
flag set as the step is called); PROBE_PACE_DRAW, at each frame, adds the
steps lost since the last (the clock's ticks less the steps run) to a debt in
quarter ticks and takes off an allowance (`PACE_ALLOW`, 1.5 ticks: about what
the unmodded game's own frames lose, 22 steps a second at 16.4 frames). While
the debt is above 0, on the map (a
fight, the fight state's +19h, draws every frame), the drawing and its flip are
left out and the list is kept in the far block (FAR_PACE, 64 entries); the
next frame drawn has it added after its own, so the old places of what moved
in the skipped frame are drawn over too. PROBE_PACE_PASS sets "something
moved" after the step when a kept list has waited 2 ticks, so a frame is drawn
for it though nothing has moved since. A pause of 24 ticks (a load, a talk)
starts the schedule afresh; the debt is held between -1.5 and 16 ticks.

To count the pictures the game shows, read DSCLOG's `flip_count` (header
+1832, counted at each flip); `pace_ran`, `pace_lost` and `pace_skipped` count
the steps run, the steps lost and the frames left undrawn (`playtest/framerate.py`
finds them by a symbol map of DSCLOG as built).

The Loader's drawing is as cheap as it can be without looking any different:
a shadow is darkened a plane of the video memory at a time (the graphics
card's registers set four times for a figure, not four times for each of its
rows), and a dust puff's pixels are worked out a row at a time, only within
its outline and the part of the view being drawn again. The pictures the
Loader draws the party's gear on are each exactly as long as their outfit,
with only the room gear needs round the figure while walking (6 pixels at the
sides, 2 above; 10 in a fight), since the game draws a walking figure's whole
picture at every step.

The drawing's savings, with the same picture
(`tests/test_dsclog_drawing.py` runs it over a scene of figures against an
emulated VGA, checks every screen against the one drawn before the change, and
counts the instructions; DOSBox charges about a cycle each). A figure's shadow
is tested against the part of the view being drawn again using its frame's
real width and height, so a figure whose shadow can't reach that part costs
nothing (the strip right of the combat log's panel and the rows under it are
drawn as parts of their own). A frame row outside that part is passed over
before any of its runs is worked out. Each thing remembers which slot of the
shadows' cache holds its frame, so the 80 slots are searched only for a frame
not seen before. The spans are darkened through `XLAT`, and the slant of a
run comes from a table in place of a division. A dust puff's thickness by age,
row and column is worked out once (DUST_BUILD, in the far block) in place of
for every row of every puff, every pass. A see-through figure's pixels go
through `XLAT` in place of a call. The four floor calls of a frame drawn round
the panel now take 32% fewer instructions with everything on, 39% fewer with
shadows alone, and 28% fewer with dust alone. A see-through figure takes 12% fewer.
Some other passes are skipped. The panel is put again only when the floor drawn
reaches it: the game draws the figures of a rectangle on a page of the
rectangle's own, so the rectangles REDRAW_PARTS draws round the panel can't
cover it. The view is drawn whole at most once in a pass of the main loop
(the panel and the labels each asked for it after a scroll). When no slot
holds a label, LABEL_STAMP returns at once. After walking stops, the dust's
leftovers are cleared with a rectangle round them, not the whole view. A
palette too dark for DARK (a fade, or a dark area) is tried again twice a
second, not in every floor pass. Rings alone widen the rectangles by 16 and 8
pixels, not by a shadow's 72 and 44.
A walker now raises a puff every 6 pixels, as meant. Before, the clock's tick
was added in place of the distance, so it raised one nearly every pass. A
walker off the view raises none.

## Picture and music

([In the features page](FEATURES.md#picture-and-music).)

Both are lines in the configuration the Loader writes over GOG's
(`launch.write_conf`: `dosbox_dicelog.conf`, read after GOG's
`dosbox_darksun.conf`), from `picture` and `midi_device` in `settings.json`.
What follows is DOSBox 0.74's source (GOG ships it beside its DOSBox:
`src/gui/render.cpp`, `sdlmain.cpp`, `midi.cpp`, `midi_win32.h`).

**The picture** (`launch.display_lines`, `launch.picture`). The game's mode
13h is 320x200 with both sides doubled by the VGA, so DOSBox applies the
`scaler` without "forced". GOG's settings are `output=ddraw`, `aspect=true`,
`fullresolution=desktop`: a scaler makes the picture 2 or 3 times 320x200 and
the output stretches it to 4:3 (and in full screen to the desktop).

| Game window | Plain | Scanlines, TV | Sharp |
|---|---|---|---|
| Single | `scaler=none` | plain | plain |
| Double, Triple | `scaler=normal2x`, `normal3x` | `scaler=scan2x`, `scan3x`; `tv2x`, `tv3x` | `output=openglnb`, `windowresolution=640x480` or `960x720`, the plain scaler |
| Quadruple | `output=opengl`, `windowresolution=1280x960`, `scaler=normal2x` | the same with `scan2x` or `tv2x` | the same with `output=openglnb` |
| Full screen | nothing (GOG's own) | `scaler=scan3x`, `tv3x` | `output=openglnb` |

- 0.74 has scan and tv scalers at 2x and 3x only (`render.cpp`: any other size
  falls to the normal one), so Quadruple doubles the 2x one in OpenGL.
- The scan and tv scalers have no 8-bit output (`GFX_RGBONLY`); DirectDraw,
  OpenGL and a plain surface all take them at the desktop's depth.
- `openglnb` is `opengl` with the texture's filter `GL_NEAREST`
  (`sdl.opengl.bilinear` false). With a `windowresolution` DOSBox opens the
  window at that size (`GFX_SetupSurfaceScaled`), and OpenGL does the aspect
  correction that a plain surface gets from the scaler's line table. The
  plain scaler is kept so that where OpenGL fails (`goto dosurface`) the
  window still opens at its size, with the plain picture.
- A stored `picture` the window hasn't (any at Single) or that isn't one of
  the four is the plain one: the playtest kit's 320x240 window stays `scaler=none` whatever is stored.
- The window's size is the same for every picture, so the mouse's
  `sensitivity` (100 over the scale: [the pointer in scenes, and where it
  starts](#the-pointer-in-scenes-and-where-it-starts)) is too.

Seen on Linux's DOSBox 0.74-3, which has no DirectDraw and takes its plain
surface for GOG's `output=ddraw` (Verified: [log](https://github.com/daaki85/darksun-obsidian-edition/blob/main/playtest/logs/2026-11-17-picture-music.md)):

- Every window opens at its size with every picture (640x480, 960x720,
  1280x960; 320x240 at Single whatever is asked), and OpenGL takes both
  outputs.
- Scanlines at Triple: each game row is two lit lines and a black one, and
  the aspect correction repeats the black line under three rows in five
  (rows of 3 or 4 screen lines). At Double a lit line and one or two black.
- TV at Triple: each row's lines at full, about five eighths and about a
  third of the brightness, the last repeated where the row is 4 lines.
- Sharp at Triple is the same picture as Plain there (the surface's own line
  table is unsmoothed too); at Quadruple the rows are 4 or 5 lines of one
  colour where Plain blends them; in full screen it fills the screen's
  height at 4:3 with rows of 5 or 6 lines (1080 high).
- Scanlines at Quadruple: OpenGL smooths the doubled picture, the dark lines
  4.8 screen lines apart, some a full black line and some two half-dark ones.
- Full screen with the plain surface isn't stretched at all on Linux (the
  picture sits unscaled on a black screen: only the OpenGL outputs scale
  there), so Scanlines and TV in full screen, which keep GOG's DirectDraw
  output, are for Windows to show. The same goes for how DirectDraw smooths
  its stretch in a window.
- In the game at Triple (the slave pens, `playtest/picstart.sh`) the window
  was 960x720 with each of the four pictures and the pointer moved the same
  with each: 28 game pixels across for 90 of the hand's, 23 down for 90.

**The music device** (`midiout.py`). GOG's `[midi]` section is
`mpu401=intelligent`, `mididevice=default`, `midiconfig=` empty. On Windows
0.74's only MIDI handler is `win32`: with `midiconfig` empty it opens the MIDI
Mapper (`midiOutOpen(MIDI_MAPPER)`); with a number in it, that device
(`midiOutOpen(number)`), counted as `midiOutGetDevCaps` counts them. A number
with no device is not an error to it: nothing is opened, the handler reports
success, and the game has no music. So the Loader writes `[midi]`,
`midiconfig=N` for a device chosen and nothing for the default, and reads the
devices' names itself to show them: `midiout.devices` calls winmm's
`midiOutGetNumDevs` and `midiOutGetDevCapsW` through ctypes (no package
needed; `MIDIOUTCAPSW` is 84 bytes, the name 32 UTF-16 units). Where there is
no winmm the window has a field in place of the list. A Linux DOSBox reads
`midiconfig` as an ALSA sequencer port ("client:port", `midi_alsa.h`), so the
field takes that too; anything else stored (`midiout.parse`) is the default.
The game's choice of score (General MIDI, MT-32 or the PC speaker, in its
`SOUND.CFG`) is not touched.

Tests: `tests/test_launch.py` (the picture's lines for every window), `tests/test_midiout.py` (the
stored choice read, anything unknown the default; DOSBox's `[midi]` lines; Windows' device names
read through a stand-in for winmm; the Loader's list) and `tests/test_viewer_options.py` (the
window's two choices).

## The engine: GOG's DOSBox or DOSBox-X

([In the features page](FEATURES.md#the-engine-gogs-dosbox-or-dosbox-x).)

`engine` in `settings.json` is "dosbox-x" or "gog" when the player chose one (`dosboxx.chosen`).
With neither (the default, and anything else stored) `dosboxx.engine` gives DOSBox-X when one is
found that isn't too old (`dosboxx.usable`, its version asked once a program and file time), else
GOG's. The program (`dosboxx.program`) is `dosbox_x_path`, the player's, if that file is there,
else the one in the Loader's `dosbox-x` folder (`dosboxx.bundled`: `dosbox-x.exe` on Windows,
`dosbox-x` or `dosbox-x.app` elsewhere), which the release puts there for Windows (below).
`soundfont` is a `.sf2` file. The order at a start (`launch._launch`): DOSBox-X chosen; the
[recompiled program](README.md#dark-sun-recompiled) when it is found; DOSBox-X by default; GOG's
DOSBox. Restore defaults removes `engine` (`SWITCH_DEFAULTS` has `None` for it). Wake of the
Ravager follows the same engine (`launch._launch_wotr`): with DOSBox-X, `_launch_wotr_dosbox_x`
makes its copies as for GOG's DOSBox and writes DOSBox-X's whole configuration with the sequel's
autoexec (`dosboxx.conf_lines(sequel=...)`, from `ravager.conf_lines`), the CD as F: from
`dosbox-x/ravager-cd.cue` (`ravager.cd_sheet`: GOG's `game.ins` with each file's full path as the
folder has it; GOG names `music\Track02.ogg` where the folder is `MUSIC`, which DOSBox-X couldn't
open on Linux, so the CD wasn't mounted and the game quit); both games start through
`launch._start_dosbox_x`. With GOG's
nothing below runs: `launch._launch`, `write_conf` and `is_game_dir` take their old path. With
DOSBox-X (`launch._launch_dosbox_x`):

1. `dosboxx.problem` refuses the start with no program, one that is gone, or one older than
   2025.01.01 (`dosboxx.version`: `dosbox-x -version` asked of the program; on Windows, where
   that opens a console and waits for a key, and where the program gives no answer, the version
   is read from the program's own file, which holds the name of its configuration file,
   `dosbox-x-2026.10.01.conf`). A version that can't be read at all is let through: the memory
   file then says (below).
2. The patched game and the copies are made as ever (`prepare_patched_game`).
3. The memory file's name is `dosboxx.memory_path`: `obsidian-edition-<ten hex digits of the
   Loader folder's path>.mem`, in `/dev/shm` on Linux (memory, not a disk), else the temp folder
   (`dosbox_x_memory_dir` in `settings.json` names another folder; hand-edited). One name for
   each Loader folder, since only one game runs from a folder at a time ([the game's
   lock](DEVELOPMENT-INTERNALS.md#reading-and-writing-memory)). A file left by an earlier game is
   removed before the start.
4. `launch.write_conf` writes DOSBox-X's **whole** configuration to `dosbox-x/obsidian.conf` in
   the Loader's folder (`dosboxx.conf_lines`; nothing of GOG's `dosbox_darksun.conf` is read,
   because DOSBox-X's defaults differ from 0.74's), and DOSBox-X is started in that folder as
   `dosbox-x -conf obsidian.conf -nopromptfolder -nomenu -fastlaunch`, what it prints kept in
   `dosbox-x/dosbox-x.log` for the crash report. The game's folder is mounted by its full path
   and never written to.
5. `launch.note_game` writes the game's pid, program and memory file in `game.lock` (a third
   line, `memory PATH`), so a Loader opened later finds the game and its file again
   (`launch.memory_game`).

**Following the game.** `__main__.connect` reads a game in DOSBox-X through
`process.FileMemory` (the file) and anything else through `process.ProcessMemory` (the
process): [reading and writing memory](DEVELOPMENT-INTERNALS.md#reading-and-writing-memory)
has how, and the memory's layout under each engine. Which file a process has is
`launch.game_memory_file(pid)`: the Loader's own record, the lock file's, or, for a DOSBox-X
started outside the Loader (the playtest kit's `start_dosboxx.sh`), the `memory file=` line of
the configuration its command line names (`dosboxx.process_memory_file`, Linux's `/proc`).
With no pid given and several DOSBoxes running, the only one of the chosen engine's kind is
taken (`process.is_dosbox_x`: a `dosbox-x` beside a `dosbox` is never taken for it, nor the
other way), and two of a kind are listed for `--pid` as before. The window's status line says
"Connected to the game (DOSBox-X, process N, through its memory file PATH)".

**The end.** `launch.closed_line` names what closed ("DOSBox-X closed."; ended by a signal on
Linux, "it was ended by signal 9 (killed)"), `GAMEEND.COM` and `GAMEOK.TXT` work as on 0.74 (a
DOSBox-X closed mid-game is a [crash report](DEVELOPMENT-INTERNALS.md#the-crash-report) with
"The game didn't end on its own"), and `launch.release_game` removes the memory file once the
game has ended (DOSBox-X leaves it). The window lets go of the file the moment its DOSBox-X
closes (`_dosbox_closed`), so file and lock are gone a tenth of a second after the process (a
kill: 2.5 seconds, the crash report written first). If the Loader closes first the file stays, with the lock
file's lines, for the next Loader to attach by; if the game then ends unseen, the next
`hold_game` or start removes the file.

**The configuration**, line by line (`dosboxx.conf_lines`; each was needed, found in
[the experiment](https://github.com/daaki85/darksun-obsidian-edition/blob/main/playtest/logs/2026-11-18-dosbox-x.md)
and [the engine's own log](https://github.com/daaki85/darksun-obsidian-edition/blob/main/playtest/logs/2026-11-19-dosbox-x-engine.md)):

| Setting | Without it |
|---|---|
| `[dosbox] memory file=PATH`, `memsize=32`, `machine=svga_s3` | (the point; GOG's machine and memory) the file is 32 MB, sparse, mode 0600, made as DOSBox-X starts |
| `[sblaster] irq=5` (`sb16`, 220h, DMA 1, high DMA 5) | DOSBox-X's default is IRQ 7: the game stops, "Mel Fatal Error ... DSP Detect Fail" |
| `[config] dos=umb` (not DOSBox-X's `high, umb`) | DOS takes the HMA; DSCLOG's far block goes into upper memory and leaves no room there for the game's overlay buffer |
| `[dos] minimum mcb free=100`, `kernel allocation in umb=true` | the game loads at 0824h, not 0224h: 26.7 KB less conventional memory than on 0.74 |
| `[dos] ems=false`, `xms=true`, `umb=true` | as on 0.74 ([EMS off](DEVELOPMENT-INTERNALS.md#ems-off)) |
| `[dos] umb end=FBFF`, with `[dosbox] rom bios allocation max=16` and `rom bios minimum size=16` | upper memory ends at EFFFh (the BIOS takes F000h up): 48 KB less for DSCLOG (free upper memory 16,368 bytes in place of 65,520 in `fountain-user`). `umb end` past EFFFh without the two BIOS lines turns upper memory off ([the log](https://github.com/daaki85/darksun-obsidian-edition/blob/main/playtest/logs/2026-11-25-dosbox-x-upper-memory.md)) |
| `[sdl] autolock=true`, `middle_unlock=none`, `clip_mouse_button=none`, `autolock_feedback=none` | the middle button unlocks the mouse and the right one is DOSBox-X's clipboard: no map drag |
| `[sdl] sensitivity=N,N` (100 over the window's scale, across and down) | one number alone is across only: in a Triple window the pointer went three times too fast down the screen (60 of the hand's pixels moved it 48 game pixels; 16 on 0.74 and with both) |
| `[render] doublescan=false`, `aspect=true` | the 320x200 mode handed on as 640x400: a window twice the size asked for |
| `[sdl] showmenu=false`, and `-nomenu` | DOSBox-X's menu bar makes the window taller than the picture |
| `[dosbox] quit warning=false`, `fastbioslogo=true`, `startbanner=false`; `-fastlaunch`, `-nopromptfolder` | a question at closing, a logo and a banner at the start, a question about the working folder |
| `[dos] log console=true` | (kept for the crash report: DOS's own text, "DSCLOG loaded.", goes to `dosbox-x.log`) |

`UMBPLUS.COM` runs in the autoexec as on 0.74 and changes nothing (the upper memory chain isn't
0.74's; DOSBox-X's block already starts lower, at CC00h, after the VGA BIOS, C000h-C3FFh, and
DOS's own tables, C400h-CBFFh, and ends at FBFFh: 192 KB, where 0.74's D000h-EFFFh is 128 KB).
Moving DOS's tables out of upper memory (`kernel allocation in umb=false`, `private area in
umb=false`) would add 32 KB there but take 32 KB of conventional memory; `umb start` can't go
below them.

**DOSBox-X in the release.** `.github/workflows/release.yml` downloads DOSBox-X's own 64-bit
Windows build of `DOSBOX_X_VERSION` (`dosbox-x-vsbuild-win64-VERSION-portable.zip` from its GitHub
release; `DOSBOX_X_SHA256`, when set, is checked: it holds that zip's) and adds `dosbox-x.exe`, `COPYING.txt` (GPL 2),
its `README.txt` and a `SOURCE.txt` of its own to the zip's `dosbox-x` folder. DOSBox-X's source
archive of the same tag goes beside the zip as an asset of the release, so the source is offered
from the same place as the program (GPL 2, section 3). Nothing of DOSBox-X is in this repository
(`dosbox-x/` is in `.gitignore`: the Loader's work folder). Linux has no DOSBox-X build of its
own (its project ships a Flatpak) and macOS's is unsigned, so neither comes with the mod.
The step is `.github/scripts/add_dosbox_x.py`. The **Test package** workflow
(`.github/workflows/test-package.yml`) runs it too, on every pull request and by hand on any branch, so a
tester downloads what a release would give: the run's artifact `Obsidian-Edition-test-BRANCH-COMMIT` (the
PR's Checks tab, Test package, Summary, Artifacts) is the unpacked zip with DOSBox-X in its `dosbox-x`
folder, and `dosbox-x-source-VERSION` is the run's other artifact.

**The Options tab's other settings on this engine.**

*Game speed* (`dosboxx.SPEEDS`; the `cycles` setting's three values name the choice, not
DOSBox-X's cycles). DOSBox-X does less with the same cycles than 0.74, and each core needs its
own number. Measured with `playtest/framerate.py 20` in the slave pens (`pens-after-arena`), the
whole party walking, everything on, a fresh start for each run, both engines in one session
(2026-11-19; 0.74 is Ubuntu's 0.74-3 with the Loader's configuration):

| Engine, core, cycles | Pictures a second | Steps run / lost a second | Walking, map units a second | Host CPU |
|---|---|---|---|---|
| 0.74, GOG's own (normal core, 7,000; two runs) | 6.4, 6.0 | 44 / 35, 46 / 33 | 97, 102 | 14%, 13% |
| **DOSBox-X normal 8,000** (through the Loader's start; two runs) | 6.5, 6.8 | 50 / 33, 49 / 34 | 99, 97 | 14% |
| DOSBox-X normal 7,000; 8,500; 10,000 | 6.1; 7.1; 7.7 | 42 / 38; 49 / 33; 58 / 31 | 91; 99; 106 | 15%; 15%; 16% |
| 0.74 dynamic 20,000 | 15.4 | 68 / 26 | 113 | 20% |
| **DOSBox-X dynamic 22,000** | 15.2 | 67 / 26 | 114 | 16% |
| DOSBox-X dynamic 20,000; 24,000 | 14.2; 15.9 | 67 / 26; 68 / 26 | 114; 113 | 15%; 17% |
| 0.74 dynamic 35,000 (two runs) | 18.8, 18.9 | 81 / 13, 81 / 14 | 139, 142 | 28%, 26% |
| **DOSBox-X dynamic 42,000** | 18.8 | 81 / 14 | 141 | 23% |
| DOSBox-X dynamic 40,000; 44,000 | 18.4; 18.9 | 78 / 17; 83 / 12 | 133; 141 | 22%; 22% |

So: **GOG's own** is `core=normal`, `cycles=fixed 8000` (0.74's `core=auto` runs this game on its
normal core at GOG's 7,000); **Faster** `core=dynamic`, 22,000; **Fastest** `core=dynamic`,
42,000. `dynamic` is DOSBox-X's dynamic core for the computer it runs on: `dynamic_x86` here; on
an ARM computer (an Apple Silicon Mac) it is `dynamic_rec`, which did more per cycle in the
experiment (165 map units a second at 45,000 against 151), so the numbers would want measuring
there. The BIOS clock and the game's clock kept real time in every run.

*The game window and the picture* (`dosboxx.display`; `launch.picture` decides which picture the
window has, as for 0.74):

| Game window | Plain | Scanlines, TV | Sharp |
|---|---|---|---|
| Single | `output=surface`, `scaler=none` | plain | plain |
| Double | `output=surface`, `scaler=normal2x` | `output=surface`, `scaler=scan2x`, `tv2x` | `output=openglnb`, `windowresolution=640x480`, `scaler=none` |
| Triple | `output=openglnb`, `windowresolution=960x720`, `scaler=normal3x` | `output=surface`, `scaler=scan3x`, `tv3x` | `output=openglnb`, `windowresolution=960x720`, `scaler=none` |
| Quadruple | `output=openglnb`, `windowresolution=1280x960`, `scaler=normal4x` | `output=openglnb`, `windowresolution=1280x960`, `scaler=scan2x`, `tv2x` | `output=openglnb`, `windowresolution=1280x960`, `scaler=none` |
| Full screen | `fullscreen=true`, `fullresolution=desktop`, `output=opengl`, `scaler=normal3x` | the same with `scan3x`, `tv3x` | the same with `output=openglnb`, `scaler=none` |

- Seen (Xvfb, Mesa's software OpenGL 4.5): every window opens at its size with every picture;
  Scanlines and TV draw as on 0.74; Sharp is hard-edged.
- **`normal3x` and `normal4x` on the surface output drew an empty grey window** with this game
  (`normal2x`, `scan3x` and `tv3x` draw there), so Plain at Triple and Quadruple goes through
  `openglnb`, which stretches the scaler's picture to 4:3 unsmoothed, as 0.74's surface does
  with its line table. Where OpenGL fails DOSBox-X falls back to the surface by itself.
- Quadruple Scanlines and TV are the 2x scaler doubled by `openglnb` (0.74: by `opengl`,
  smoothed), so the dark lines stay whole lines.
- Full screen was seen under a window manager (openbox on Xvfb, a 1280x720 screen): the window
  takes the screen and the picture is 942 pixels wide, as in the 960x720 window: 4:3, black at
  the sides. Without a window manager (bare Xvfb) SDL2 switches to full screen in name only.
  Plain is smoothed there (`opengl`), as GOG's own full screen is.
- Not offered yet: `output=openglpp` (pixel-perfect: whole multiples only, so 4:3 just at
  1600x1200, 5x6; at 960x720 it draws 960x600), which fits none of the four windows, and
  `glshader=` (CRT shaders: files that come with DOSBox-X's packages, not with every build). Both
  want a setting of their own.
- Full screen is switched while playing with DOSBox-X's host key and F (F12, on Windows F11);
  the window's status line says so.

*The music device* (`dosboxx.midi_lines`, from `midi_device` and `soundfont`):

| Chosen | Written |
|---|---|
| a device number (Windows' MIDI outputs, as `midiout.devices` lists them) | `mididevice=win32`, `midiconfig=N` |
| an ALSA port (`128:0`) | `mididevice=alsa`, `midiconfig=128:0` |
| the default, and a soundfont file that is there | `mididevice=synth`, `midiconfig=FILE` |
| the default, no soundfont | `mididevice=default` |

DOSBox-X has FluidSynth twice. `mididevice=synth` plays into DOSBox-X's own mixer beside the
Sound Blaster, so the music needs nothing outside DOSBox-X and is in DOSBox-X's own recordings;
`mididevice=fluidsynth` (with `fluid.soundfont`) plays through FluidSynth's own sound driver
instead, which found no PulseAudio here and left the game silent (the experiment;
playtest/logs/2026-11-21-dosbox-x-unchecked.md). The Loader writes `synth`. MT-32 (`mididevice=mt32`, which needs the Roland ROMs) is not
written for any setting.

**Windows and macOS: written, not run.** What the code does there, from DOSBox-X's source
(`src/hardware/memory.cpp`, 2026.10.01):

- *Windows.* DOSBox-X opens the memory file with `CreateFile` (read and write, sharing
  `FILE_SHARE_READ | FILE_SHARE_WRITE`, not delete), cuts it to nothing, sets its size, marks it
  sparse, and maps it with `CreateFileMapping` **with no name**: another program can't open the
  mapping, only the file. Python's `os.open` shares read and write, so the open succeeds. There
  is no `pread` on Windows, and Windows doesn't promise that `ReadFile`/`WriteFile` agree with a
  mapped view; it does promise that views of one local file agree, whichever mapping object they
  come from. So `FileMemory` maps the file itself there (`mmap`). While the Loader holds its
  mapping the file can't be cut (`ERROR_USER_MAPPED_FILE`): a DOSBox-X started again would get
  no memory file, so the Loader drops the mapping when the game ends and removes the file before
  each start (a start is refused, with the reason, if it can't). The game is held still for the
  item gate with `NtSuspendProcess` on a handle opened by pid. `-version` isn't run there. The
  configuration is written in the ANSI code page, as for 0.74 (`conf_encoding`): untried.
- *macOS.* The same code as Linux (`mmap` of the file, `MAP_SHARED`; the Loader reads with
  `pread`). No `/dev/shm`: the file goes in the temp folder, on disk, where the system writes
  changed pages back now and then. The process list comes from `ps` (no `/proc`), and a stop
  signal is taken as done. The Loader has never run on macOS with either engine.
- `playtest/dosboxx_memtest.py` checks the file's half of this on any system without the game
  ([the kit's tools](https://github.com/daaki85/darksun-obsidian-edition/blob/main/playtest/TOOLS.md)).

Tests: `tests/test_dosboxx.py` (the engine setting, the version read three ways and refused when
old, the memory file's name and folder, every line of the configuration for each window, picture,
speed, music device and soundfont, the start with a stand-in program: the lock file's memory
line, the file removed at the end, a killed DOSBox-X's lines), `tests/test_filememory.py` (the
file as guest memory both ways, `pread` and mapped; a cut file and a closed DOSBox-X as
`ProcessError`; holding the process still by pid; `connect`'s choice among a DOSBox, a DOSBox-X
and the Loader's own game), `tests/test_viewer_options.py` (the Engine section: chosen, saved,
an old program refused, the soundfont, Restore defaults).
