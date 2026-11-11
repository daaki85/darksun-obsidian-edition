# The playtesting kit's history

How the rules and recipes in [PLAYTESTING.md](PLAYTESTING.md) were found: the incidents behind
them, the approaches given up, the measurements made, and when each thing was learned. The guide
states current practice; this file keeps the story, by topic and with dates, so nothing learned is
lost. The test logs themselves are in [logs/](logs/). Add to it when a play's incident or a
superseded approach would clutter a recipe.

## The guide and the kit

- The first version of the guide and its tools lived in the scratch folder and were lost when the
  container was reclaimed; the guide was written again into the repository on 2026-11-01
  (logs/2026-11-01-sewer-grate.md: "Stopped here to write the playing guide"), with the tools, at
  the root and outside `obsidian-edition/`.
- None of the saves came with the game (2026-11-01): every one in `playtest/saves/` was made in a
  play. Replaying the arena took most of a day, hence the rule to save at every milestone.
- The user's standing instruction to add everything learned to the guide after every play dates
  from 2026-11-01.
- **Other sessions push to this branch too** (2026-11-01: a Dark Sun Recompiled session changed the
  kit while this one played), hence the fetch and rebase before every push.
- The shared DOSBox lock (`flock /tmp/playtest/dosbox.lock`) dates from 2026-11-08, with another
  agent on the same DOSBox.
- 2026-11-11: the guide was reorganised into a short startup procedure, task recipes and the route,
  with the incidents and dates moved here.

## The shell

`pkill -f` with a pattern the command line itself contains killed the shell running it (exit 144),
twice on 2026-11-01, the second time with the rule already written: run the kill as its own
command, by pid, and nothing else in it.

## The game's installer

On 2026-11-11 the user's Drive copies of the GOG installers had been shared by link, and those links
were in this public repository; that is piracy, so their downloads are now restricted and the links
are gone from the scripts. Since then `setup_game.sh` and `setup_ravager.sh` (and the environment's
setup script that runs them) find no installer unless one was put in place, and stop with a message.

The environment's setup script dates from 2026-11-06; it was checked that day, with the old
download: `loadsave.sh pens-after-scar` loaded (region 29h, leader 1816,440, window 320x240, dice
log attached). A worker restart of the session killed DOSBox as an idle pause does. The fresh
container by hand was worked out the same day.

The missing `DARKSAVE.GFF` of a bare `innoextract` was found on 2026-11-10, checking a clean install
and the release zip (logs/2026-11-10-pre-merge-checks.md); `setup_game.sh` has copied
`__support/save/*` into the game folder since.

## The window size and pixel checks

- 2026-11-02: with no `obsidian-edition/settings.json` the Loader's default window was 960x720
  (window_scale 3), every pixel check (msgbox.sh, levelup.sh, panel.sh) failed, message boxes and
  CHOOSE A SPELL went unseen and the loops stalled. start.sh has set `window_scale` 1 since, and
  pixmatch.py samples a bigger grab down to 320x240.
- 2026-11-01: "cannot import name '_imaging'" (a broken PIL) made every msgbox.sh call fail;
  pixmatch.py falls back on ImageMagick since.
- panel.sh read the wrong row for a day: the pixel was taken from a 320x200 capture while the check
  uses a 320x240 window grab.
- 2026-11-06: `panel.sh` was found to read "hidden" for the expanded panel (its check is for the
  small panel); 2026-11-08 (logs/2026-11-08-panel-fight.md): passto.sh's "END menu opened" test was
  passed by the panel's new lines, and it pressed E with no menu and opened the Effects screen.

## Flags that read 0

2026-11-01: an arena "flag 11 never set" was only the flags having no place in memory (their
pointer, DS:1352h, null outside a script's run). 2026-11-05: the pointers at DS:1352h and 1356h were
found to stay null in the arena even while a script waits on a message, so a poller never found
them; hence the test builds with a branch forced.

## The watchdog

2026-11-07: GONE lines in `guard.log` from a watchdog started without a display, two hours before,
were taken for a new run's: the log keeps earlier runs' lines.

## Scripts that didn't decode

2026-11-05: eleven scripts in the built copy didn't decode, and a later change gave up on one;
every script in the built copy should decode.

## The pointer

- The cycle (arrow, sword, eye, arrow) was checked on 2026-11-01; that only walkable ground takes a
  walking click is the user's (2026-11-01).
- 2026-11-07: right-clicks guessed from shots left the sword up, hence `pointer.py`, which reads the
  mode from memory. The same day the user pointed out that the look pointer pauses the game.
- 2026-11-06 (`restalarm.sh`): the pointer was the sword, no rest came ("rests: 0") and the click on
  the ring fell on Cilla (Gerakis attacked her out of a fight).

## The view and scrolling

- 2026-11-01, in the arena: the view stayed put with the leader at the top edge (screen y 24, under
  the top bar), so nothing north of it could be clicked; resting the pointer on the edge didn't
  scroll it, and writing DS:1178h (`camera.py X Y`) changed the number but not the picture.
- The middle-button drag is the user's advice (2026-11-01). Runaway drags the same day: a long drag
  from the centre ran the pointer off the bottom and sent the view south, and a loop that sized each
  drag from the last ran it off to (0, 1368). scroll.py starts each drag on the side it moves away
  from and caps it since.
- 2026-11-07 (`ghostturn.py`): in the enemies' turns the view follows the one acting; in a fight the
  view barely drags.

## Message boxes and YES/NO questions

- 2026-11-01: a click wherever the pointer was (low on the map, after a drag) left "Excellent!
  These gladiators wish to fight again!" up through a whole loop of clicks; hence `boxclick.sh`, a
  click ON the box.
- 2026-11-01: a check for "2. No" in the last few lines of the dice log took an old, answered
  question for a new one; hence the check of the last line only.
- Talk keys: an earlier note said the number keys did nothing in a talk menu: the key had gone to
  another window. 2026-11-08: `xdotool key --window $W 2` chose Kurzak's second line, 5 his Goodbye.
  2026-11-10: 6 does nothing (his Goodbye, sixth line, takes the down arrow).
- View Character: a 2026-11-08 note put it among the inventory's bottom icons at 52,171; on
  2026-11-10 it was found to be the inventory's first bottom icon (168,187), not 52,171 (52,171 is
  on the creation screen's VIEW CHARACTER).

## The recompiled program

The kit has driven Dark Sun Recompiled since 2026-11-01.
- The dice log attached at the program's start, or before a save was loaded, printed nothing
  afterwards (2026-11-01, twice); `loadsave.sh` restarts it after the load since.
- The middle-button drag did nothing on the program until its runtime passed the middle button
  through (fixed 2026-11-01: every button but the left had been the right one).
- 2026-11-06: the drag was found to scroll only with the Loader attached (it switches the helper's
  `scroll_on` on at attach).
- The doors at Kurzak's stop were tried on the program on 2026-11-01.

## Two probes on one vector: target AC 255

2026-11-05: VEC_GHOST was given 62h, VEC_AC's, and every attack's AC went to the see-through probe:
the dice log's "target AC 255" on every attack on the party. The install's bytes turned up twice in
the image: two probes on one vector, not chance. VEC_GHOST is 80h now, test_gamepatch checks the
vectors are distinct, and `buildcheck.py` checks every hooked vector points at its handler.

## See-through figures at a turn's end

- 2026-11-05/06 (logs/2026-11-05-fight-test.md): the see-through figures seen from a real hide
  (Cilla, thief level raised to 12 in memory: hides at 95; on 2026-11-06 a d100 of 94 hid her) and
  a real Invisibility.
- 2026-11-06 (logs/2026-11-06-solid-frames-turn-end.md, `walkprobe.py`): Move running out doesn't
  pass the turn. After E, STEALTH went to 0 within one Loader pass, but the figure kept its
  see-through picture through the enemies' turns (about 1.4 s) and was drawn solid when a party
  member's turn began: the view is drawn again from the map's main loop, which doesn't run in the
  enemies' turns. The 2026-11-05 "two solid frames" weren't seen in 38 more hidden steps (beside
  Gerakis and K'ratchek too): closed as not reproducible after the vector fix.
- Then GHOST_UNION (logs/2026-11-06-solid-at-turn-end.md): the figure solid about 0.1 s after the
  hiding ends, if the next enemy steps or swings. `ghostclear.py` dates from 2026-11-07.

## Figures gone from the map: the picture store

- 2026-11-08, the ambush after a long run of clicks: the party, and at times the foes, weren't drawn
  though their places were right; I then Escape (the inventory opened and shut) drew them again,
  for a while. Clicks on a figure not drawn missed (passuntil.sh gave up).
- **Found 2026-11-09** (logs/2026-11-09-missing-figures.md): the game's picture store and its 300
  slots are given back only at an area load. Each time the Loader dressed a member anew (any change
  to what its figure wears: inventory moves, a weapon's +0Fh written in memory) it marked the old
  pictures FFFEh and the game took a new slot and about 7 KB of store for each. The pens take 200
  slots and 275 KB on arrival, so after some 30-60 gear changes there a picture lay past the
  store's end: drawn while in memory, never read back once let go, and every failed read kept the
  memory it took, until no figure could be loaded (all gone; I then Escape frees that memory, so
  they came back for a while). A long test in one area with many gear changes ran into it.
- Fixed: the Loader leaves a figure undressed when the store has no room (`_room_for`), and reuses
  the game's slots (logs/2026-11-09-picture-store-fix.md), so the store hardly grows. `fillcache.py`,
  which waits for the slot count to grow, has stalled since (4 s a change).

## Slot reuse and the inventory's icons

Opening the inventory puts every picture out of memory, and its icons are loaded through the same
cache and let go once drawn, so at 300 slots they are free for reuse: a search that always began at
slot 0 had the icons take one slot in turn (3,590 reuses in a cycle). PIC_REUSE now searches round
from after the last slot it reused (2026-11-09, logs/2026-11-09-picture-slot-reuse.md).

## Frame rate measurements

Before 2026-11-08 `framerate.py` averaged the walking speed over the whole run (the waits at a
target included), so every setting read 64 to 66 map units a second; it counts only while walking
since.

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

## The arena's first bout that didn't start

2026-11-02: topartyfight.sh ended "NO FIGHT" at (488, 232), and 60-odd more clicks south and walks
between (488, 232) and (488, 264) (the bone wall stops the party at 264) over several game minutes
didn't start it; two later fresh games that day started at once. The bout is GPL 2's entry at 1
(case gnum 3 = 1, "Step forward" sets it), run by MAS 42's code-111 trigger on object 2059 at (498,
341), beyond the bone wall, and it waits on flag 5 (MAS 42 sets it on loading); the flags can't be
read in the arena. Why it sometimes doesn't is open.

## The arena: waves and leaving

- The arena's waves and messages as of 2026-11-01.
- Out of the arena: done on 2026-11-01, the fourth run (`leavearena.sh` does it since); clicking
  inside the wall's boundary is the user's advice that day. The 2026-11-01 run lost its time
  getting the view to the wall: hence "don't walk south or east first".
- 2026-11-10, twice: walkto.py couldn't take the bone wall's gap on the way to a bout (it stopped
  at (488, 216-264), NO PATH, and its view snapped back); hence the drag and the click on the gap.

## The pens: Kurzak's patience and the alarm fight

- The way to the grate was worked out from the scripts and the region file on 2026-11-01; the
  entryway into the pens and the alarm at the stalker pen's door are the user's (2026-11-01).
  `pens-after-arena`'s place was checked by loading it on 2026-11-07. The door at (113, 90) was
  locked on 2026-11-04, with the party straight from the arena and Kurzak followed.
- Resting at the fire ring is the user's (2026-11-05), as is the way into the arena from the pens.
- Twice the party walked to Kurzak's stop and on toward the gate (1816, 408) after his call, and he
  ran out of patience ("That's it! Time's run out!"), then the alarm and a fight with every guard.
- 2026-11-06: `toalarm.sh` stopped short at (1832, 856), outside the fire room (its last walkto said
  NO PATH FROM HERE with the door open). The user caught a look click on an open door (the gold
  pole) taken for an open: it had closed it. The pointer was the sword before `restalarm.sh` (see
  [the pointer](#the-pointer)). In a fresh container the same day `toalarm.sh` then `restalarm.sh`
  worked first time, with the eye set by two right-clicks on bare floor.
- 2026-11-10: the fire room's door shut in a new game; Alagorn's talk tried through Kalzith.

## The LEVEL button that stuck

2026-11-09, `fountain-user`, Lex after `spellsetup.py 0=10 33 28`, clicks at 186-205,171: the LEVEL
button didn't move from LEVEL 1. It **did not come back** in a later check
(logs/2026-11-09-level-button.md: three loads with the same arguments, in and out of the fight, the
rules off too: 1, 3, 1, 3 each time). No fault in the game or the mod; the game's rule for the pages
offered is in the guide.

## "cannot save" used to save

The game's save compare is unsigned (79BBAh), so every −100 ("cannot save") saved. Since
`save_signed` it fails (with the manual's spells only at first; always applied, in no switch, from
2026-11-09).

## Turn Undead's unnamed target

A Turn Undead out of a fight starts one, and its line named the target "?" (the number had changed
by the time the dice log read it, the fight having renumbered the combatants); since 2026-11-09 the
record carries the creatures and the line names them (logs/2026-11-09-turn-undead-name.md: Cermak
on Kalzith). DSCLOG's per-fight tables moved to the far block then.

## The inventory's input

(2026-11-09.) For anyone trying a click there again: the stats panel is no cell; the game takes
clicks from its queue of events (the mouse handler at GAME_HANDLER posts (2, 0Eh, 0, x, y, -,
events) through 3164:023Ah; its keyboard reader, 31C48h, posts (1, 0Ah, 0, key, shift) from the
BIOS buffer through the same call), and never polled INT 33h's functions 3, 5 or 6 there. Clicks
with x and y changed to a portrait didn't reach the portrait's handler (70352h); **Space** (3920h)
in the inventory gives the shown member's portrait event 8: drawn again, and its EDIT NAME menu
opened (it then blocks every click; Escape posted after it didn't close it in step); **1-4** (the
table at 6FDD0h + 1E3Bh) give event 7, which doesn't draw the shown member again.

## Pehtucl's chest

2026-11-07 (logs/2026-11-07-pehtucls-chest.md, logs/2026-11-07-review-fixes.md): the chest's USE
command and the shut type; `pens-new-chest` was saved then. 2026-11-08: `saves/trap-user`, a game
from before 2.14.0, where the chest was the game's plain one.

## When things were learned

The recipes in the guide mostly carry no date; a recipe with a log names its date in the log's
file name. The others, by the day they were found:

- **2026-11-01**: the pointer's cycle; walkable ground only (the user); the middle-button drag (the
  user); clicking ON a message box; the YES/NO check; doors with the look pointer (the user); "NO
  LINE OF SIGHT" at the pens' gold post; the recompiled program as the target; the pens' route from
  the scripts; the arena's waves and the way out.
- **2026-11-02**: the window size; AC in the inventory; the party's item lists; the parts of an AC;
  ability items and memory edits; the inventory screen's places; a spell's description box; the
  first bout that didn't start.
- **2026-11-04**: the game making a region's map objects near the party; `teleport.py`; Psionic
  Blast without a blaster; the weapon rack's contents.
- **2026-11-05**: a Shinobi for a test; hearing the game and the game's table of sounds; the
  see-through figures and `ghostchk.py`; the arena's flags can't be set from outside; route.py
  won't walk through a figure; looting a body (the user); reading a scroll; the inventory panel's
  picture for the docs; passing one member's turn; seeing foes attack; Kalzith.
- **2026-11-06**: people's gear (`people.py` since); a big frame see-through; a hidden walk to Move
  0; a blow from outside a fight; the environment's setup script; a fresh container by hand.
- **2026-11-07**: the look pointer pauses the game (the user); `pointer.py`; `ghostclear.py`,
  `rec.py`; the game's free things and `arenatrip.sh`; the view in the enemies' turns and in a
  fight; the Loader's own window for a screenshot (the opening show over within about 15 s of the
  seal); picking a pocket.
- **2026-11-08**: a creature's level / hit dice; `rolog.py`; frame rate and cycles; the creation
  screen; the talk keys; View Character (from the inventory); the leader button; talking to someone
  who walks; the Trustee's pocket; an XP award by hand; the panel and the turn tools; casting spells
  for a test (the basics from 2026-11-07); a spell outside the caster's spheres; level and class
  tests on a foe; spells rolling to hit; Turn Undead; test_dsclog's slow failures; Wake of the
  Ravager's level-up.
- **2026-11-09**: a person's new gear and old saves; checking a figure's glow; the feet's place;
  the walkthrough; comparing loudness; where the turn's movement is; a weapon's rule in a fight;
  the combat log's doc pictures; giving an effect in memory; Turn Undead the AD&D way; combatants
  past 64; the panel's level chip; Minute Meteors and Flame Arrow; `foeset.py` and its group;
  monster powers, dual-classing and resting; the picture store and slots; lots of items on the
  ground; the large dice in the item box; an item's icon in the game.
- **2026-11-10**: `setcount.py`; the arena's people made at its first visit; a multiclass
  character; a held item changed in memory; an item type's record; a class in memory; the Loader
  window's Help; a spell box's text; View Character as the first bottom icon; the window Loader's
  `game.lock`; the load window for the docs; a rule by size; `held_hit`; a shot with a weapon put
  in memory; melee reach; a grand master; every HP change with its time; the sound descriptor's
  +0Ah; a clean install and the release zip; the fire room in a new game; someone else's talk
  through Kalzith; water for resting (the user's idea).
- **2026-11-11**: reading a value inside a script; no call from Kurzak after a rest; a Spellarcher;
  a lock barred until a level; pointer trails; the weapon rack's tool; looting with T; selling with
  S; the shop and pocket tools; `docs/viewer.png` retaken; the combat log panel's level button and
  its GIF; bodies under the party's figures and Caps Lock; the grate's Hack for the first melee
  weapon in either hand; the installers' public links removed.
