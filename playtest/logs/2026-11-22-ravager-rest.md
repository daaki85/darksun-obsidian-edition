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

## The priests' spells first (SITE 18, REST_PRE; about 18:40 UTC)

Ported after the run above: the rest's first move (8CA82h) runs SL's pass with the sequel's numbers,
casting through the rest's own free-cure cast (4787h:25h, 8D074h). The same route, then (test edits)
Terrannus alive (status 1), every member's HP 10, Terrannus's priest slots 3 for levels 1-4, and
Gerakis Poisoned (an effects entry: 71, spell 179).

- "At rest: Terrannus casts Neutralize Poison on Gerakis (4th-level slots: 2 left)"; the effects table
  empty after, Gerakis alive (the rest's poison kill had nothing to kill).
- Then the cures on the most wounded (Gerakis, 146 missing after the night): Cure Serious Wounds three
  times (Terrannus twice, Thy'rokh the druid once), then Cure Light Wounds until both priests' 1st-level
  slots were gone; 2d8 and 1d8 each, the game's own spells. Their 2nd- and 3rd-level slots (no cures)
  kept.
- Then the night: "+3, +2 (CON 17)" and the rest as before; Gerakis 90/165, then 165 by his CON 22
  regeneration. The helper's count 17 (14 casts and 3 nights' healing).

## Still to do

- The psionicists' Cell Adjustment at rest (SL's RP_PSI_CAST): the sequel's power bytes not found yet.
- Cure Blindness and Cure Disease at rest (the same path as Neutralize Poison's, not seen).

Water: a jug on a stand in the room beside the rented one (seen, not looked at); nothing new.
