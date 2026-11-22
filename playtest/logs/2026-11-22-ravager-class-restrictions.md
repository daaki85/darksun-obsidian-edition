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
- Not found: the sequel's "can't cast" test (SL's 89B4Dh, which DSCLOG's PROBE_NO_CAST hooks). The
  sequel never calls its effect test (608h:20h) with Can't Cast (68) as SL does with its 50, yet its
  USE screen crosses a Can't Cast character's spells out (seen: Ar'anda with effect 68 added). So a
  multiclass preserver in armour still casts, and the dice log's "NO SPELLS IN ARMOUR" stays off.

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
- The helper's count rose by 2 for every refused try: the screen asks once to light the slots it can
  take and once on the click.

## Not played

- A backstab taken back in armour (THIEF_REAR): no fight with a thief behind a foe set up.
- A new character's starting gear (SL's weaponchoice.class_gear: the Loader's creation side isn't on
  the sequel's creation screen yet), the human dual-class cases, a ranger's bow, a druid's bare rule.
- The multiclass preserver's casting in armour (above: the sequel's cast test not found).

## Water

None new: the Tyr street outside the save's place, as before.
