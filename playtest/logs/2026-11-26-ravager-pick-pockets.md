# 2026-11-26: picking pockets in Wake of the Ravager

**Under test:** branch `claude/ravager-pick-pockets`: DSCLOG2's PICK POCKETS (sites 180-186, header +2000 to +2018),
the Loader's `RavDiceLog._answer_pick` (SL's `pickpocket.attempt` on the sequel's memory), the purse icon (ICON
3048 in the Loader's RESOURCE copy, drawn from the sequel's earth Turn Undead icon 3045). DSCLOG2.EXE 52,256 bytes.

**Set-up:** a throwaway copy `ravPP` of `$WORK/rav`; `sh ravload.sh ravager-after-ambush /tmp/playtest/ravPP` (the
Tyr ambush won, the party in the street); the dice log `RAV_NO_SAVES=1 ravdice.py 6900` (quick saves and autosaves
off: nothing was saved); the DOSBox lock held throughout. Ar'Anda (slot 0) is the party's thief, 7th level, pick
pockets 90%, move silently 85%. The person tried is the Caravan Master (thing 20, creature 32), at the game's 289,191
on the save's first screen. The steps: [the try script](files/2026-11-26-ravager-pick-pockets-try.sh) (USE, the
purse, a click on the person, a grab, the dice log's tail, Continue) and [the header reader](files/2026-11-26-ravager-pick-pockets-hdr.py).

## Steps

**1. The button.** USE (22,17) with Ar'Anda: a purse where a cleric has Turn Undead (156,144 at the game's size;
[the screen](img/2026-11-26-rav-pick-use.png)), "PICK POCKETS" in the bar under the screen with the pointer on it.
A click arms it (pp_armed 1) and closes USE; the pointer is the sequel's look pointer (mode 2).

**2. The first tries (before a fix).** On the Caravan Master:

```
Ar'Anda picks Caravan Master's pocket: d100 = 94, needs 90 or less -> failed
  Ar'Anda moves silently to get away: d100 = 34, needs 85 or less -> success
  Ar'Anda fumbles Caravan Master's pockets, but slips away unnoticed.
Ar'Anda picks Caravan Master's pocket: d100 = 36, needs 90 or less -> success
  Ar'Anda lifts Obsidian Longsword from Caravan Master unnoticed.
```

**A bug:** a long sword from a pocket. The sequel's item types carry no weight (the byte SL's MAX_WEIGHT reads is 0
for its dagger, long sword, shield and armour), so everything passed. Fixed: `pickpocket.pocket_sized`, a hook the
sequel's layout binds to `ravlog.rav_pocket_sized` (a weight if the type has one, else no armour or shield, a weapon
of at most 4 damage, anything else). Ar'Anda's own liftable things after it: her dagger and sling, not her sword.

**3. Success (after the fix, reloaded).**

```
Ar'Anda picks Caravan Master's pocket: d100 = 16, needs 90 or less -> success
  coins: 7d4+7 (2 to 5 for each of 7 thief levels) = 28
  Ar'Anda lifts 28 ceramic pieces from Caravan Master's purse, all there was to take.
Caravan Master keeps a close hand on their purse now: Ar'Anda won't get another chance.
```

The text in the game's own message window ([the picture](img/2026-11-26-rav-pick-coins.png)); the party's money
5000 to 5028. A second try: the "close hand" line, no roll. A dead body of the ambush (95,133): "There are no
pockets to pick there." With `RAV_PICK_ROLL=1`: success, 25 coins (5025), the long sword not lifted.

**4. Caught (`RAV_PICK_ROLL=100`, reloaded).**

```
Ar'Anda picks Caravan Master's pocket: d100 = 100, needs 90 or less -> failed
  Ar'Anda moves silently to get away: d100 = 100, needs 85 or less -> failed
  Caravan Master catches Ar'Anda's hand!
  (Ar'Anda may try Caravan Master again once a thief level is gained)
Caravan Master remembers Ar'Anda, and keeps a close hand on their purse. (Ar'Anda was caught at this thief level: another try once a level is gained, with Thieves as in AD&D)
```

[The window](img/2026-11-26-rav-pick-caught.png). As in Shattered Lands, being caught is a message and a person
closed to that thief until a level is gained: nobody turns on the party.

**5. The rest.** A right click while armed: the pointer back to the walk arrow (mode 1), pp_armed 0. A plain look
after a pick: the game's Look box (the Caravan Master LEVEL 3). Terrannus (cleric) after Ar'Anda: Turn Undead's icon
and name as before (the button's cache let go). The pointer on the purse with a right click: its name, no box. The
header's late count stayed 0, seq and reply matched each time.

**6. The control: `RAV_SKIP` of the eight patches** (pp_show, pp_click, pp_lit, pp_arm, pp_text_hover,
pp_text_info, pp_info, pp_hand). Ar'Anda's USE screen has no button there ([the screen](img/2026-11-26-rav-pick-control.png)),
a click on the place does nothing, the element word 0, the header's counters 0, no dice log line.

## Water

No new area: the play stayed on the save's first screen (the jugs there, Uhubito's caravan office, are in ROUTE.md
since 2026-11-25).

## Open

- A cleric/thief: Turn Undead keeps the place (SL's PP_EXTRAS beside it not ported).
- The purse's description on a right click, its sound.
- XP for lifted weapons (SL's LIFTABLE_NAMES list is SL's; empty for the sequel).
- No item lift seen after the fix (only coins); the weight rule by kind is a guess at what fits a pocket.
