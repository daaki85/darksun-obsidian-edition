# Test log: class restrictions, Wake of the Ravager (2026-11-22)

Under test: SL's class restrictions (game.RULE_RESTRICT, always on in SL; dsloader/restrict.py) in
DSCLOG2: CU_SITE (site 19, the end of the sequel's "may this character equip it"), BELT_SITE (site
20, the end of the thief skill routine) and THIEF_REAR (called from MISSILE_REAR at the attack's
set-up). RULE_RESTRICT added to ravager.RULES_PORTED.

## Found first

- The sequel's equip test (its end 7761Ah; SL's 6EF51h) has the same tests, but its answer is a byte,
  `mov [bp-1],al` at 775FDh after `test [es:bx+0Ch],ax` (the type's classes against the sheet's +10h),
  then "CANNOT USE THIS ITEM" (DS:1B3Ch) when it is 0. DX the type, [BP+0Ah] the sheet.
- The sequel's item types (15 bytes): flags +0 (4 a shield), material +4, the type's slot +5, armour
  +0Bh 80h, classes +0Ch, AC +0Eh. The armour types: 1-5 arms (slot 3), 30-34 chest (1), 62-66 legs
  (10), 56 the helm (6), 91 the one shield; materials as SL's (1 bone: brigandine, ring, scale; 4 metal:
  chain; 5 leather: "Armor"). No bracers, robe or cloak type counts as armour, so SL's exceptions for
  them have nothing to do here. Worn slots (an item's +13h) as SL's: arms 0, legs 6, head 7, chest 9.
- A sheet: class bits +10h (thief 400h), race +12h (human 1), classes +1Bh, levels +1Eh: SL's less 6.
- The thief skill routine is 8C647h (combatant [BP+6], skill [BP+8]); it ends `mov ax,si / pop di`
  at 8C7C5h. Its callers: the party's best thief for a skill (8C5C0h on) and 7366Fh, the scripts'
  skill check. The inventory's PICK, LOCK... numbers come from elsewhere: they don't change.
- The backstab is set at 5C94Ah-5C987h (from behind the byte [BP-19h], a backstab the byte [BP-21h],
  THAC0 [BP-1Eh]), and MISSILE_REAR's INT already sits on the next `mov al,[bp-19h]` (5C99Fh): the
  check went there rather than in a site of its own (a second patch there failed the Loader's check of
  the original bytes).
- The sequel's "can't cast" test (SL's 89B4Dh) is a case of a larger routine, 84E94h ("can this creature
  do it": [BP+6] the kind, DI the creature, SI a second argument; its jump table at CS:1C44h): it reads
  the creature's effect bits through 608h:25h into [BP-10h] and its casting case (84EE7h) wants a sheet,
  Okay, not hit this round (308h:[DI+B2h]), none of Can't Cast (68: `test byte [bp-8],10h`), effect 4,
  Afraid 35, Feebleminded 37, effect 7, and a roll for effect 62; its "yes" is `mov ax,1` at 84F6Eh. A
  first search missed it: the sequel never asks the effect test (608h:20h) for 68 by number; reading
  the bitset's callers (608h:25h) for a test of byte +8, bit 10h found it.

## In the game (ravload.sh ravager-after-ambush, the Loader, the dice log on, about 17:45-18:10 UTC)

Test edits (DOSBox stopped after, nothing saved): DSCLOG2's rules word written for the controls
(0004h without, 2004h with the rule), item types changed in memory.

- **A psionicist's weapon**: Ar'anda (preserver/psionicist/thief, an elf) took her long sword (metal,
  type 97: not a psionicist's kind) from her hand to the backpack and back: "CANNOT USE THIS ITEM",
  the sword left on the pointer. Control, the rule off: the same move put "+1 Longsword 1D8+5" in her
  right hand.
- **An earth cleric's weapon**: Terrannus (cleric of earth, human) and Thy'rokh's gythka (bone) made a
  mace (type 67, bone, one-handed: the gythka itself is two-handed, "NEED TWO FREE HANDS" first):
  "CANNOT USE THIS ITEM" for his free left hand. Control, the rule off: "+1 Gythka 1D6+9" in the hand.
- A thri-kreen druid and leg armour: the game's own "THRIKREEN CAN'T USE" came first; no non-kreen
  druid in the party to try the druid's bare rule.
- **A thief's skills in heavy armour**: Ar'anda's leather Armor (type 32) made Brigandine (type 30,
  bone; her AC went from 4 to 3 on the screen). The thief skill routine run in an emulator on the live
  memory, through the patched site and DSCLOG2's own INT F5h (playtest/RESEARCH.md, "Running one of
  its routines... through the helper"): every skill 0 (INT F5h seen). Control, the rule off: pick
  pockets 81, open locks 68, traps 61, move silently 70, hide 70, hear 56, climb 96, read 24; with the
  rule on and the leather back, the same numbers.
- **A multiclass preserver in armour** (a second run, about 18:10 UTC): Ar'anda in her leather Armor,
  the USE screen: every spell crossed out, her status Okay, the dice log's "NO SPELLS IN ARMOUR"; a click
  on a spell, "YOU CANNOT CAST SPELLS". Control, the rule off (LEVEL pressed to redraw): the level 2
  spells plain, one cast (WIZ 2/2 to 1/2). In the thieves' fight below, her spells crossed out too.
- **The backstab in a fight** (two thieves and two thugs in the alley north of the Roost, provoked with
  "Run along now, pip"; ravager-after-ambush, the arrow keys Up 8 and Right 40 from the save; Computer
  Control for all four; test edits: Ar'anda in brigandine, everyone's HP 250). No attack of hers came
  from behind by itself in two fights, and a live edit of the overlay's facing test didn't hold (the
  overlay is reloaded several times a round, at other addresses: playtest/RESEARCH.md); so DSCLOG2's
  MISSILE_REAR start was changed in memory to make the first member's every attack from behind and a
  backstab (the game's own [BP-19h], [BP-21h] and THAC0 2 + 2), THIEF_REAR left as it is. Control, the
  rule off: "Ar'Anda attacks Thug BACKSTAB with Obsidian Dagger (1d4)... THAC0 17 base, +4 in bonuses",
  "+4 backstab (the dice 2 x3 = 6)"; "...BACKSTAB with Longsword +1... +7 in bonuses". The rule on, the
  same fight: "Ar'Anda attacks Thief from behind with Obsidian Dagger (1d4)... +2 in bonuses", "...from
  behind with Longsword +1 (1d8+1)... +5 in bonuses", "Ar'Anda hits Thief for 8: 1d8 = [3] +1 weapon
  +4 STR 18": from behind kept, the backstab's +2 and its multiplied dice gone.
- The helper's count rose by 2 for every refused try: the screen asks once to light the slots it can
  take and once on the click.

## A druid and the human dual-class cases (ravload.sh ravager-after-ambush, the Loader, the dice log on, about 21:45-22:05 UTC)

Test edits, DOSBox stopped after, nothing saved: Terrannus's (member 1, a human cleric of 7th level)
classes (sheet +1Bh) and race (+12h) written for each case, his class bits (+10h, cleric) left so the
game's own test lets him wear it all; for the thief's cases his leather Armor (item 7) made Brigandine
(type 32 to 30, bone). Each case: the inventory on him, his chest armour (game 173, 80) to the backpack
(195, 35) and back; the item's worn slot (+13h) read after, 9 worn, 255 still on the pointer. Controls
with the rules word 4804h (RULE_RESTRICT off). (The inventory's slots in game coordinates: the screen's
x / 2, y / 2.4; the shield at 65, 90.)

| Case | Classes, race | The rule on | Control, the rule off |
|---|---|---|---|
| A human druid, leather Armor | 6, human | **CANNOT USE THIS ITEM** | worn |
| A human druid, his (leather) shield | 6, human | **CANNOT USE THIS ITEM** | worn |
| A half-elf druid/fighter (multiclass) | 6 9, half-elf | **refused** | |
| A human fighter, once a druid | 9 6, human | worn | |
| A human preserver, leather Armor | 11, human | **refused** | worn |
| A human preserver, once a fighter | 11 9, human | worn | |
| A human thief, Brigandine | 17, human | **CANNOT USE THIS ITEM** | worn |
| A human thief, once a fighter | 17 9, human | worn | |
| A human thief, once a cleric | 17 2, human | worn | |
| An elf thief/fighter (multiclass) | 17 9, elf | worn (as the fighter allows) | |

- The armour he already wore stayed on through every edit: the rule refuses a new equip only.
- **The order of a human's classes, in the game's own DUAL**: Terrannus (dualset.py's scores) in the
  DUAL window (the rule on) took FIGHTER: his classes became 9, 2 (the new class first), levels 1, 7,
  class bits 0020h (the fighter's alone), THAC0 20. So the cases above, the new class first, are how
  the sequel keeps a dual-classed human, as DSCLOG2's CLASS_FORBIDS and DUAL_WARRIOR read it.
- The helper's count rose 2 to 7 for a refused try (the screen asks for each slot it lights).

## Not played

- A new character's starting gear (SL's weaponchoice.class_gear: the Loader's creation side isn't on the
  sequel's creation screen yet), a ranger's bow, a human thief once a warrior keeping his skills at 0
  in heavy armour (THIEF_HEAVY: the skills seen at 0 for a multiclass thief above), a human preserver
  once a warrior casting in armour.

## Water

None new: the Tyr street outside the save's place, as before (both sessions).
