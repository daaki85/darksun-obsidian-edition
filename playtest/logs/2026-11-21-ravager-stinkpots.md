# Test log: the staff sling's stinkpots, Wake of the Ravager (2026-11-21)

Under test: DSCLOG2's STINKPOTS (Weapon traits, RULE_HI_CAHULAKS): the Staff Sling's (type 98) shot is a
stinkpot, 1d3 (STINK_SWING sets the call's sides on its first swing), and a hit on a living target not
immune to poison makes it save, or be Nauseated (-2 to hit) for 1d3+1 rounds (STINK_HIT, from CAH_HIT's
missile way).

## Found first

- **The sequel's far calls go through selectors**: a word table at file 4B080h, 8 bytes a selector
  (selector / 8 the row; its first word the segment, the load's + it). 388h is the load + 3F49h, 608h
  + 473Bh, 598h + 46A7h, 628h + 475Ah. A stub segment (paragraph aligned in the root, `CD 3F 00 00`,
  then the overlay's place from 57580h as a dword and its size, then 5 bytes an entry from +20h: `CD
  3F`, the routine's offset) names each overlay routine; so 608h:3Eh is the load + 473Bh, entry 3Eh.
  (The guide's "0806:0020" for "has effect" is the bytes `08 06`: selector 608h.)
- **The game routines STINK_HIT calls**:
  - the saving throw, 66D26h (598h:75h): (target, thrower, power, level), AL 0 failed; SL's 79A71h.
  - the damage resistance, 85052h (628h:25h, its only caller near, 84689h): (target, a far pointer, the
    kind's bits), AX the share taken, 0 immune; SL's 7B492h.
  - the effect adder, 7F9E6h (608h:3Eh): (target, thrower, spell, effect, time as a dword: seconds, a
    timer; negative: charges, the record's +8; a last byte, +9). SL's 76442h, the same prologue.
  - no undead routine: the sequel tests a sheet's race (+12h) against 9 in place, ten times.
- **Empty effects**: the sequel's 113 effect records (31 bytes, the name and an icon word, ICON 21000 +
  the spell: Poisoned's 52BBh is Poison's, 179) have two empty ones, 12 and 88. Nauseated takes 12
  (the Loader's patch "nauseated_name": the name and Stinking Cloud's icon, 21022).
- **No monster poison power** as SL's 176: the save is against Stinking Cloud (22), which the dice log
  shows as "(paralysis/poison/death)", the right save.

## In the game (ravhold.sh, RAV_LOADER=1, about 12:30 UTC)

The Draxans' ambush; Thy'rokh's Chatchka (item 10) and Ar'anda's Sling (item 3) made Staff Slings
(type 98), the four given 250 HP; in the last run the Draxans' saves made 20 (test edits; DOSBox
stopped after each, nothing saved). The dice log with 0xE0008205.

- Under Computer Control Thy'rokh threw it once (run 1): "Thy'rokh hits Draxan for 4: 1d3 = [3] +1
  weapon", then "Draxan's saving throw vs a stinkpot from Thy'rokh (paralysis/poison/death): d20 total
  12, needs 10 -> saved". The AI mostly closes to melee; Web from a Draxan holds the party (an END menu
  for the webbed one, and its Computer Control turned off).
- By hand (run 3): Thy'rokh walked two squares back, the sword pointer (one right-click) on a Draxan
  until red showed, a click: a throw. The second throw: "d20 total 3, needs 20 -> failed: nauseated",
  "Thy'rokh's stinkpot: Draxan is nauseated, -2 to hit for 1d3+1 = 2 + 1 = 3 rounds". The effects
  table then had `17 00 02 00 16 00 0c 00 00 00` (Draxan 23, Thy'rokh, Stinking Cloud, effect 12, a
  timer). That Draxan's two swings: "THAC0 13 base, -1 in bonuses = 14", the other Draxan's "+1 in
  bonuses = 12": the 2 off. The helper's counters: 2 stinkpot saves, 1 Nauseated, 2 nauseated swings.
  By round 4 the effect was gone (3 rounds, 180 seconds).

## Fixed after

- The damage line said "(1d3 for 1d4: a large target)": DSCLOG2 sets the stinkpot's dice in the frame
  (SL's changes the type table, so its line has no note). Now "(1d3 for 1d4: a stinkpot)".

## Still to do

- The attack line doesn't name Nauseated in its bonuses (the total is right).
- The Effects screen's "Nauseated" not seen (the Draxan had it, not a party member).
- Poison immunity (the kind's bit 1, SL's) not seen: no poison-immune foe in this fight.

Water: none new (the same street).
