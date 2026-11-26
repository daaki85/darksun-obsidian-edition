# Test log: items saving against acid, Wake of the Ravager (2026-11-22)

Under test: SL's items saving against acid (game.RULE_ITEM_SAVES, always on in SL; DSCLOG's
PROBE_ITEM_WEAPON, PROBE_ITEM_SKIP, PROBE_ITEM_ARMOUR) in DSCLOG2: ITEM_WEAPON, ITEM_SKIP and
ITEM_ARMOUR (sites 22, 23, 24) and ADND_NEEDED with the sequel's item and type offsets.
RULE_ITEM_SAVES added to ravager.RULES_PORTED.

## Found first

- The sequel's two checks are SL's code: the first melee weapon held (7CEC0h; `mov dx,8 / sub
  dx,[bp-2]` at 7CF22h, the plus from item +16h) and the worn arm, leg and chest pieces (7D02Ah; the
  power the word at item +10h, `cmp word [bp-2],0` at 7D0AAh before the jump to "destroyed", `mov
  dx,0Ah / sub dx,[bp-2]` at 7D0BEh). Detonate's item check is the next routine (7CF50h), as in SL.
- Both are entries of overlay stub 472Fh (selector 5F8h: 4Dh the weapon, 61h the armour, 52h
  Detonate's). Their only callers are cases of the power handler's switch (656ECh, on the power
  number at [BP+0Eh], its table at CS:28C1h, 81 powers): **103 Crystal Brittle** (the weapon, then the
  armour if the weapon came through), 275 and 283 (the armour), 284 (the weapon), 235 Detonate. 275,
  283 and 284 are named MONS275... in RESOURCE.GFF: no monster with them was met.
- So Crystal Brittle is the sequel's way into the acid check; with the rule its items get the acid
  save for their material too (SL's table: obsidian 5, leather 10).

## In the game (ravload.sh ravager-after-ambush, the Loader, the dice log on, about 19:00-19:40 UTC)

Test edits (DOSBox stopped after, nothing saved): Ar'anda knows Crystal Brittle (`ravknow.py 103
18`: her preserver level 18, so the USE screen offers level 9), the party's HP 250 and base AC -10,
DSCLOG2's rules word 0804h (two weapons, item saves; class restrictions off, so Ar'anda casts in her
leather armour) and 0004h for the control, and the thieves' armour slots moved (`ravitems.py
--worn`: at the fight's start their armour read slots 14-16, which the armour loop skips). The fight:
Tyr's two thieves and two thugs in the alley north of the Roost ("Run along now, pip").

- **A weapon, the rule on**: Crystal Brittle on a thief: "Ar'Anda's acid on Thief's Obsidian
  Longsword: d20 = 18, needs 5 (AD&D's, 5 for obsidian; the game's: 8) -> safe". (The dice log called
  it acid: it now names the sequel's powers, ravlog's ITEM_ATTACKS.)
- **Weapon and armour, the rule on**: on a thief with his armour in the worn slots: his Obsidian
  Dagger safe on 11 (needs 5), his chest Leather Armor **safe on 13** (needs AD&D's 10; the game
  destroys armour with no power without a roll), then his leg piece corroded on 2: gone from his
  items. DSCLOG2's count of checks: 4.
- **Control, the rule off**: Crystal Brittle on a thug: his Obsidian Dagger destroyed on a d20 of 6
  (the game's 8; AD&D's 5 would have kept it). Again on the other thief-armoured thug: his chest
  Leather Armor destroyed at once (no armour roll; the weapon came through). No check of DSCLOG2's
  counted (still 4).
- Water: none seen in the alley (Tyr's water as noted before).

Not seen: the monsters' touches 275, 283, 284 (no such monster met). Shattered Lands' check of the
same code is unchanged.
