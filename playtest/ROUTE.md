# The route through the story

Part of the playtest guide ([PLAYTESTING.md](PLAYTESTING.md): read its startup procedure before any
in-game test). How to get the party somewhere: a new game, the arena, the slave pens, Kurzak's call
and back to the arena. Tools: [TOOLS.md](TOOLS.md).

## A new game

A new game (`start.sh`, then `topartyfight.sh`: START GAME, the ready-made party, the opening,
the step forward) ends in the arena's first fight (region 2Ah), party at about (488, 424).
- The opening's show fight (a Rampager kills a Defiler) isn't the party's: leave it be.
- The party then waits at the gate (488, 168-184): "Gladiators: Step forward, into the arena!".
  One step south takes it to (488, 232), between the gate and the bone wall; the game brings it
  into the arena (488, 424) and starts the fight on its own once some game time has passed:
  keep clicking south (each click passes time) until `fight_on 1`, about 8 clicks.
- Then `sh arenawaves.sh`: every wave fought with fightout.sh, the messages between, and the
  YES/NO question answered N; and at once `sh leavearena.sh` (out of the arena: below). Run them
  together: `(sh arenawaves.sh && sh leavearena.sh)`, in the background, followed with a Monitor.
  A new game to the pens in the background: `start.sh`, `topartyfight.sh`, `arenawaves.sh`,
  `leavearena.sh` (about 30 minutes; about 25 minutes through the arena).
- **The first bout can fail to start**, now and then: topartyfight.sh ends "NO FIGHT" at (488,
  232), and more clicks south don't start it (the bone wall stops the party at 264). **When it
  doesn't start, restart (`start.sh`) and try again before digging.** What's known of the
  bout's script, and the run where it failed: [HISTORY.md](HISTORY.md#the-arenas-first-bout-that-didnt-start).

## The arena (region 2Ah)

- Several waves (Sligs and a Screamer Beetle; Sand Howlers and a Tohr-kreen; ...), then "The
  crowd is awed...", the Announcer, and "Yell something back at the Announcer?" (N), then
  "Attention gladiators: Go back to the pens to heal your wounds." After a repeat fight it may
  say only that, with no YES/NO question (arenawaves.sh stops at either).
- **Staying sends another fight, every time**: the clock after "Go back to the pens" is short (a
  few walking clicks; it barely moves while the party stands), then "Since you will not leave, you
  must fight!", "If you don't want to return to the pens, then you must want another fight!" or
  "Excellent! These gladiators wish to fight again!" and a wave (Silt Runners, a Screamer
  Beetle...), each able to bring a level-up screen, and "Go back to the pens" again, until the
  party leaves. Leave at once, and don't walk south or east first.
- **Out of the arena** (`leavearena.sh` does all of it): after the last fight, drag the view north
  (scroll.py) until the ground inside the wall (488, 232) shows, click it, and the party walks round
  into it by itself (the user's advice: if the party stops at the stone wall, click inside the
  wall's boundary; don't stay outside the walls, as more monsters are sent); then click the gate
  strip (488, 184): "This corridor leads down to the slavepens. Do you wish to continue? (Answer Yes
  or No)": **Y** (N, as for the Announcer, turns it down, and the question comes back only on
  stepping off the strip and on again). The party comes out in the pens (region 29h) at (1816,
  440). In the scripts (MAS 42's move triggers): the gate strip, squares 28-32 at row 11 (map x
  448-527, y 176-191), runs script 3 at 73Eh, which (with flag 11 set, by script 2 at BB8h, and
  local 32 at 0) takes the party to the pens (region 29h, 113, 27); squares 5-7 at rows 30-32 run
  script 3 at 6B4h ("Gladiators escaping! Guards! Sound the alarms!": avoid them).
- **The arena's people are made at its first visit** (logs/2026-11-10-scar-bout-gear.md): a save
  made past the first bout (every kept save but `pens-new-chest`) holds Scar and his henchmen as
  they were made then, so a change to their gear (worldgear's gifts for objects 87 and 229) shows
  only in a new game: `pens-fire-count4`'s Scar still swung his old long sword. The route for it: a
  new game through the arena (about 25 minutes, above), Goodbye to Kurzak, `follow.py 29`,
  `setcount.py 4`, the fire room and its rests, `toarena.sh`.
- The cluebook (#13): "Follow Kurzak to and from the pens when fighting in the Arena."
- After Scar's death in the arena the next visit is the champions' bout. Scar's bout opens with his
  talk: 5 ("No more talk. I'm committed.") fights.

## The slave pens (region 29h)

### Arriving and following Kurzak

- Through the gate the party comes out at (1816, 440) and Kurzak meets it ("These are the
  slavepens. I'm Kurzak, leader of the guards. Follow me. I'm here to lead you to your cell."; his
  menu: help me escape or I'll kill you, about yourself, the half-giant, escaped slaves, the exits,
  Goodbye: "Get moving! I gotta get back to work."). `pens-after-arena` was saved a little further
  on, in the corridor at (1672, 344) with Kurzak beside the party.
- **From the save, follow Kurzak**: the party starts in the corridor at (1672, 344), shut in on the
  west (the corridor runs on to 1352-1400, 344): a gate at squares (81, 20-21), map (1304,
  320-351), the gold post west of it, is closed (live grid 192/193), clicking it does nothing, and
  no script opens those squares. Kurzak (object 29) walks his route a waypoint at a time (141 at
  0h: squares 99,25 then 99,31...), each waiting for the party within 4 squares: `python3 follow.py
  29` keeps walking the party beside him. At (99, 32): "All right, go through the door. There's a
  place to rest down the east hall. I'll come get you when it's time for your next fight. If you
  want to fight before that, knock on the door."
- **Into the pens (the user)**: Kurzak's "door" is the entryway south of where he stops, squares
  (99, 33-34), map (1592, 536-551), open once he has led the party there; through it is the
  east-west hall (rows 35-37, columns 90-115), the cells south of it, and "the east hall" (the
  campfire) down the passage at columns 112-114. `route.py 1592 584` walks through.
- **The pens' main door** (objects 2145-2146 at 1571-1611, 559: the entryway Kurzak opens) has
  the "Take me to the Arena! I want a fight!" menu (137:14CEh), but open it answers nothing to
  the look pointer.
- The pens' cell doors (2141-2164) have USE (script 138) and ATTACK handlers ("This door is too
  strong to bash open" for the cells').
- **Kurzak's door** (logs/2026-11-11-doorway-blocked.md): the entryway, squares 99,33-34 (99,34 is
  the one that shuts); its leaves objects 2145 and 2146: map record +12h bit 08h open (20h or 10h
  shut), +17h the frame (07h the spiked gate, 04h open). It is the only way between Kurzak's stop
  and the pens' south passages. The game's call opens it; `doorwatch.py SECONDS` (background) prints
  the square, Kurzak and Legcrusher at each change. If the leaves are open and the square shut, the
  Loader's `kurzakdoor.py` opens the square after 10 game seconds ("Kurzak's door: open, but its
  doorway was barred on the map; opened"). **A door action (22h, 2) is no way to open a door from
  a script line**: put before Kurzak's line it shut the open door.

### The way west, the stalker pen and the grate

The way to the grate, from the scripts and the region file, and the cluebook:
- **The corridor gate (81, 20-21) is locked**: the look pointer on the gold post opens a look box
  titled "Door" whose only live button is the third (USE, 116,137): "The door is locked. It
  appears quite sturdy." The box message then has to be clicked away (boxclick.sh), and the
  pointer is left on the eye: right-click on to the arrow before walking.
- **The other way west** (`doorpath.py`, with BLOCK="81,20 81,21"): down the east passage to the
  door at (113, 90) (map 1816, 1448; `route.py 1816 1400` stands beside it; it was locked once,
  2026-11-04, with the party straight from the arena and Kurzak followed: check its look box), west
  along the bottom corridor (rows 91-95) through the door at (93, 94), north up columns 34-35 to the
  south hall (rows 66-70), and north at columns 17-20 to the stalker pen's anteroom (its door 16,
  54-56). On the way, two slaves whisper "Is it time to break out yet?" / "Shh, not yet!".
- The stalker pen nearest the north: its door, objects 2163/2164 at (256, 864-896), is barred.
  Using it says "The door is locked. It appears quite sturdy."; attacking it (138:121h) rolls
  RAND(30) against the attacker's STR to bash it open, and the Mountain Stalker (151, at 187,856)
  then hunts the party. A second stalker pen is further south (door 2157/2158 at 255,1087-1119).
- **Opening the stalker pen's door sets off the alarm** (the user): plan for it (the guards come)
  or find another way to the button.
- Button 1281 at (139, 748), the pen's north wall: used from within 4 squares (137:1AE8h, else
  "is too far away to press the button") it sets flag 518 and "hears a click as the secret door to
  the west opens". (Button 1280 at 1335,798 opens another door, 81-82,53-54, only once the monster
  266 at 1264,848 is gone or flag 317 is set; otherwise "presses the button, but nothing happens".)
- The grate, object 1234 at map (46, 86) (square 2, 5), the far northwest; walking onto squares
  3-4, 5-6 (map 48-79, 80-111) runs its menu (137:29Bh): Pick the lock / Rip it open / Hack the
  lock off (Pick the lock only with a thief in the party: without one the keys shift, 1 rip, 2 hack,
  as saves/README.md has it). From `saves/grate-user` (Cromwell leading, beside it): `walkto.py 60 100`, then the Y
  key, then the reply's number key (`xdotool key --window <DOSBox's window> 2`). The weapon search
  runs as the menu is made, before the question. Hack is offered for the first melee weapon in
  either hand; `itemedit.py 0 2 slot=3` then `itemedit.py 0 3 slot=2` (just after loading) puts
  Cromwell's Bow in the weapon hand and the Axe out: then only Rip it open / Leave.
- **The weapon rack** (Thornwall's, object 2599) is at square (48, 34), map (779, 550), in the room
  west of the door at (65, 38-39); from (52, 36) beside it the game has made it. Its contents (map
  object 478 on 2026-11-04): Polearm, Quarterstaff, Polearm, Axe, with Thornwall first once
  Semyon has told of the shipment (flags 756, then 757). `rackcheck.py` reads it.
- From the cluebook's map: #11 the stalker pen (break the door, kill the mountain stalker, push the
  button on the north wall: a secret door to the northwest corner), #12 the sewer grate (map 46,
  86; "use" it or walk over it: rip, hack or pick; a failed try can be tried again), #15 the
  campfire (rest; two rests bring the next arena fight; keeping Kurzak waiting sets off the alarm),
  #10 Pehtucl's ambush (Bloodwrath on his body).

### Resting and Kurzak's call

- **Resting** (the user): the fire room off the east passage, its door at square (115, 53), map
  (1848, 856), opened with the look pointer; in it a small fire ring among haystacks (map about
  1931, 856): the **look pointer on the ring** rests ("THE PARTY RESTS", hit points full; the
  game's rest, 8066Dh; the east hall's object 2264 at 1908, 675 is a haystack, 137:F5h, not the
  ring). `ringrest.sh` rests there. After two or three rests and a step, Kurzak calls ("Gerakis!
  Get up here! It's your turn in the arena!"). **Answer the call quickly**: if the party dawdles
  (walking to Kurzak's stop and on toward the gate, 1816, 408) he runs out of patience ("That's it!
  Time's run out!"), then the alarm and a fight with every guard ([as it went
  twice](HISTORY.md#the-pens-kurzaks-patience-and-the-alarm-fight)). `toarena.sh` answers the call
  (up to the arena).
- **The fire room's door**: with the door open, the walk arrow on the room's floor (screen 240,160,
  camera 1656,720) takes the party in. The closed door is the gold pole; **a look click on an open
  door closes it**: check a shot before clicking a door. **In a new game** its door is shut: from
  `route.py 1832 856` (camera 1656, 720) the eye on the gold pole at screen (198, 112) opens it, the
  walk arrow at (240, 160) goes in, and the ring is at screen (276, 134) (ringrest.sh's 203, 88 is
  for camera 1728, 768).
- **The alarm fight on purpose**: `toalarm.sh` (loads `pens-after-scar`, records the sound, raises
  Cilla's thief level in memory, walks to the fire room), then `restalarm.sh` (rests, then waits
  Kurzak out); the alarm then sends wave after wave, with `fight_on` 0 only a moment between them
  (fightout.sh stops "DONE" there: run it again); about 15 minutes in all, in the background with a
  Monitor. **toalarm.sh can stop short at (1832, 856)**, outside the fire room (its last walkto said
  NO PATH FROM HERE with the door open). **The pointer must be the eye before restalarm.sh** (else no
  rest comes, "rests: 0", and the click on the ring can fall on a member); set it with two
  right-clicks on bare floor (a red eye with a bar over floor is the eye) or `pointer.py look`.
- **No call from Kurzak after a rest** (logs/2026-11-11-arrows-sound-and-no-call.md): check flag 497
  (`state.py 497`). The Trustee's key used on a door sets it (GPLI routine 752, script 137 at 1h)
  and the call script then never calls, until the party talks to a guard carrying routine 753
  (objects 55, 260, 261; MAS 29 makes them).


### Into the arena from the pens

- (the user) After the call, Kurzak's entryway (`route.py 1592 584`), his stop (1592, 520), north
  to (1592, 440), east along the corridor at y 408 (walkto in two steps: further north, y 376,
  counts as escaping and sets off the alarm) to (1816, 408), then a click into the gap in the brick
  wall just south of it (1816, 440): "Enter the arena?" **Y** (before Kurzak's call the gap asks
  nothing). In the arena: south from the gate (488, 200) with clicks (each passes time), through
  the bone wall's gap (504, 360), and on south onto the stone platform until the bone gate closes
  behind the party (488, 408-424): then the Announcer and the bout. **walkto.py can't take the
  gap** (it stops at (488, 216-264), NO PATH, and its view snaps back): `scroll.py 0 -100` twice
  (camera about 328, 232-256), a click on the gap's floor (screen 176-180, 106-130), then clicks at
  map (488, 420) until `fight_on 1` (two). With the camera at y 256 map y 420 is off the view
  (screen y 164 is fine, y 260 is not): after the gap's click, `viewto.py 504 360` (camera about
  344, 280) and clicks at screen (144, 145). A click below the view (screen y 200 and more)
  opens EXIT: SAVE GAME? over an empty red view (camera 344, 1360): CANCEL, then viewto.py. `setcount.py 4` makes the next trip Scar's.

### Kalzith

- **Kalzith**: from `pens-after-scar`, walkto (1816,408), (1704,408), (1592,440), then clicks at
  screen (200,178) (camera 1392,384) take the party through Kurzak's entryway past him (route.py
  wouldn't: he stands in front of it); then `route.py 1560 880` reaches Kalzith's pen (him at
  1576,888, thing 220). The arrow's click on him does nothing (the party stands on him): the look
  pointer (two right-clicks on bare floor) on him opens the Look box (KALZITH, LEVEL 5), and its
  first button (163,150) talks. Replies are lines from y 162, 8 apart; "We mean no harm", then click
  the box twice, then "Show us what you have" opens his shop. `openshop.sh` does it from
  `selling-junk-user` ([selling](PLAYTESTING.md#inventory-looting-selling-and-shops)).
- **Someone else's talk through Kalzith** (logs/2026-11-10-outstanding-checks.md), for a talk whose
  speaker isn't in the pens (Alagorn's): a test build with Kalzith's entry (1139) pointed at the
  other talk's script and place (Alagorn's 211 at 1h) in `kalzith.script_chunks`, `loadsave.sh`
  (which writes `dos/GPLDATA.GFF`), then `git checkout dsloader/kalzith.py`. From `pens-after-scar`:
  walkto (1816,408), (1704,408), (1592,440), a click at screen (152,165) (camera 1440,416) past the
  guard in the entryway, `route.py 1560 880`, the eye and a slow press on Kalzith (the old man in
  green, about 257,120), Talk (163,150). Alagorn's way to his stories: 1, 1, Y, 1 (Weapons or
  Armor), then the kind (2 Magic melee weapons); he lists only items the party holds. The next
  `start.sh` or `loadsave.sh` writes the scripts afresh.

### Pehtucl's chest

- (logs/2026-11-07-pehtucls-chest.md, logs/2026-11-07-review-fixes.md) `saves/pens-new-chest` is a
  new game with the chest's USE command (older saves lack it), but its chest was made before the
  shut type: run `shut.py` after loading, or the game opens it whatever the script says. To reach
  it: `teleport.py 200 1432 40 1322`, walkto (216, 1440), then (184, 1400), a square west of it
  (from (120, 1464) the script says "You must be next to the chest"; standing on it, a figure takes
  the click); `pointer.py look`, a slow press on it (163, 70), the look box's third button (236, 101)
  (`chestuse.sh [y|n]`: the answer to a non-thief's "Bash it open?"; checked 2026-11-17). `thief.py N LEVEL` / `thief.py N off` makes a thief in memory. The chest's look
  box: first button closes, second **moves the chest**, third uses it. The game's trap objects:
  +0Fh is the trap's descriptor (d6, reach, damage kind), DSUN.EXE 80A11h. Retrying a lock:
  [a lock barred until a level](PLAYTESTING.md#inventory-looting-selling-and-shops).
- **In a game from before 2.14.0** (`saves/trap-user`) the chest was the game's plain one and
  opened after any use; the Loader shuts it now (`pehtuclchest.watch`, a few seconds after
  loading). There, from beside it (walkto 184,1400; the eye on it at 204,90, the look box's third
  button 141,125), a non-thief gets "Bash it open?" (Y); `bashloop.sh N` repeats the use and Y until
  "breaking it open" (Lex's 15% came in a few tries), clicking messages only while `msgbox.sh` sees
  one (a click on the map walks the party off) and cancelling an EXIT menu an Escape brings up.

## Water for resting (an idea for later)

The user's idea (2026-11-10): resting might one day cost water, which would need water and jugs on
sale or to find in every part of the game. Whenever a play reaches a new area, note in the test log
and here where water, jugs or waterskins are (a shop, a well, a body, a chest), with the region and
map position. Nothing is built for it yet.

- The slave pens (29h): a fountain at about square (68,94), where Pehtucl's ambush and Legcrusher's
  fetching take place (`fountain-user`, `legcrusher-fountain-user`); whether it gives water is
  unchecked. In `fountain-user` Lex carries a **Pot of Water** (item 104, type 60, value 1), so the
  game has such an item (2026-11-18).
- The arena (2Ah): no water, jug or waterskin seen on the platform or on the champions' bodies
  (2026-11-18).
- Wake of the Ravager, Forest (01h): the Roost test jump and overhead-map check did not establish a water source (2026-11-27).
- Wake of the Ravager, Veiled Alliance HQ (33h), Forest dining room and Mines 3 throne room: no water seen in the rooms looked at (2026-11-27, logs/2026-11-27-ravager-furniture-review.md).
- Wake of the Ravager, the first scene in Tyr (the street at the start): a red pot and a jug on the
  table of the room to the west; not looked at (2026-11-22, logs/2026-11-22-ravager-transfer-items.md).
- Wake of the Ravager, Tyr (2026-11-25, logs/2026-11-25-ravager-shops-scrolls.md): **Uhubito's caravan
  office** (the street's east side, world y ~1340-1420) has clay jugs by its counter and on the shelves at
  the back; **Shadow Square** (the city's west) has barrels, jars and sacks at the stalls south-west of
  Notaku's (world ~150-250, 1000-1100). None looked at; Notaku sells no water.
- Wake of the Ravager, the Draxans' ambush street in Tyr (2026-11-25, logs/2026-11-25-ravager-fight-keys.md):
  no water, jug or waterskin among Alt's marks there (a scroll, sandals, the bodies).
