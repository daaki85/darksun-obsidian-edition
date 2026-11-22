# Test log: resting as in AD&D, natural healing, Wake of the Ravager (2026-11-22)

Under test: DSCLOG2's SITE 17, REST_HP (SL's rest_hp, "Resting as in AD&D", RULE_REST): a night's rest
heals 3 hit points plus CON's bonus (a warrior's in full, others at most +2), not the game's full heal.

## Found first

- The sequel's rest is 8CA7Ah (mode [BP+6], hours [BP+8]; SL's 8066Dh), called from the fire ring's
  look (6951Ch). Its pass 2 sets an Okay member's HP to the sheet's most (+8) with `mov [es:bx],ax` at
  8CF79h (SL's 808AFh), the same code with the sequel's records; PSP at 8CFBDh.
- The level hit point table is at load + 45BEh (selector 4D0h): the same bytes as SL's 40B1h table
  (groups at +10h + class, CON's hit points at +52h + CON), the sequel's classes 18 and 19 in groups 2
  and 0. A creature's CON is its +1Bh.

## In the game (ravload.sh ravager-roost, the Loader, the dice log on, about 18:10-18:25 UTC)

The Roost's route (RESEARCH.md): Reyhan, rent one night (keys 1, 3, 4, then Space to close the talk,
and one right-click to get the walk arrow back), the corridor, the room's steps, Up 6, the look
pointer on the fire ring. Before the look, every member's HP set to 10 (test edit; DOSBox stopped
after, nothing saved). Terrannus was dead in this save (status 7) and stays so: the rest heals only
the Okay.

- "Ar'Anda rests 8 hours: +3, +2 (CON 17) = +5, now 15/48 HP" (a preserver: CON 17's +3 kept to +2)
- "Thy'rokh rests 8 hours: +3, +5 (CON 19) = +8, now 18/75 HP" (a fighter: the warrior's +5)
- "Gerakis rests 8 hours: +3, +6 (CON 22) = +9, now 19/165 HP", then "Gerakis now 115/165 HP (+96)":
  CON 20 and more regenerates as the clock jumps the 8 hours (the game's own, kept as in SL).
- The game read the same afterwards (15, 18, 115); the helper's count 3.

## Still to do

- REST_PRE: the party's priests spending their spells left on the party before the night.

Water: a jug on a stand in the room beside the rented one (seen, not looked at); nothing new.
