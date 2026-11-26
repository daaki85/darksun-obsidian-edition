# 2026-11-23: weapons and arrows that cast on a hit in Wake of the Ravager (effects group C)

*Branch `claude/ravager-party-transfer`. reports/wake-of-the-ravager-party-transfer.md, group C.*

## What was found

- **The sequel already casts a weapon's spell on a hit**, as Shattered Lands does. Its attack (DSUN
  5D20Dh, SL's 58B63h) reads the item's power (+10h, the spell + 1, a word; SL keeps it at +0Fh, a
  byte) and casts it on the one hit at level 6 (5D2CCh). Its own objects use it: a longsword with
  Burning Hands, one with Vampiric Touch, a Focus Heat missile weapon (OBJEX.GFF). For a shot, a word at
  308h:[7] comes first: the **ammunition's** power, so an arrow with a power casts it too.
- **The transfer gave the mod's items no power.** The Loader's own objects (the mod's items) were
  made with power 0, and the two games number spells differently (Focus Heat is SL's 116 and the
  sequel's 174). Now `ravtransfer.spell_map` matches the spells by name (SL's RESOURCE.GFF SPIN
  chunks with the sequel's spell records, and a short list of spelling differences such as "Detect
  Invisibility" and "Detect Invisible"). Each of the Loader's own objects takes its SL item's spell:
  - the Searing Blade gets Focus Heat (174);
  - the Spellarcher's arrows get their touch spell, found by the arrows' name.

  The Cahulaks +2 are not one of the Loader's objects: they are SL's own Cahulaks +1 (object 30003)
  made +2, and ITEMS.BIN (SSI's own pairs) sends that object to the sequel's cahulaks, object 686.
  So they arrive +2 (the plus is carried) with the sequel's spell on that object, Poison, not
  Shattered Lands' Cause Light Wounds. That is SSI's own choice and it is kept.

  The sequel's own objects keep theirs, and keepsake scrolls get none. Tests: `ItemSpellTests` in
  tests/test_ravtransfer.py, one of them on both games' real files (DSUN_WOTR and DSUN_SL).
- **A weapon's touch spell rolled to hit a second time.** DSCLOG2's spell-to-hit rule
  (TH_CAST) tells a weapon's cast by the bytes at the cast's way back. In play that test failed,
  probably because the overlay manager's return need not be the attack's code. So a hit's Cause
  Light Wounds or an arrow's Chill Touch rolled a touch attack, and a natural 1 lost it:

  ```
  Ar'Anda#0's Cause Light Wounds at Draxan#21: touch attack d20 = 8, needs 8+ (65%) ... -> HIT
  Draxan#27's Chill Touch at Gerakis#3: touch attack d20 = 1 (natural 1) ... -> MISS: the spell does nothing
  ```

  The fix is DSCLOG2's WEAPON_CAST (site 46, `weapon_cast` at 5D2C2h, SL's ARROW_LEVEL). It makes the
  cast's own pushes (level 6, the spell) and marks the cast a weapon's, so no roll follows. Tested in
  an emulated CPU (`test_weapon_cast`).

## In the game (about 04:20-04:50 UTC; `RAV_LOADER=1 sh ravhold.sh`, Computer Control, `ravdice.py --all --numbers`)

Test edits in memory, never saved (a scratch `powerset.py`: an item's +10h and +2 set to the
spell + 1, as the transfer writes them). DOSBox and the dice log were stopped by pid each time.

1. **Focus Heat on Gerakis's Dragonsbane, Cause Light Wounds on Ar'anda's longsword** (the build
   before WEAPON_CAST):
   ```
   Gerakis attacks Draxan#27 with Obsidian Dragonsbane +4 (1d8+4): d20 = 14 ... -> HIT
   Focus Heat damage: 2d6 = [5 + 2] +6 = 13 (2d6 + 1 for each caster level: 6 at caster level 6)
   Draxan#27's saving throw vs Focus Heat from Gerakis#3 (spell): d20 total 6, needs 13 -> failed: full damage, 13
   ```
   There were four Focus Heats (saves for half), and Ar'anda's longsword cast Cause Light Wounds
   (1d8), but it rolled the touch attack above.
2. **Chill Touch on the Draxans' arrows** (their type-18 ammunition, power 4): each bow hit cast
   Chill Touch on the one hit ("Chill Touch damage: 1d4 ... lasts 60 rounds (caster level 6)"),
   with its save. It also rolled the touch attack, and one natural 1 lost it.
3. **The new build** (WEAPON_CAST), with Cause Light Wounds on three party weapons and Chill Touch
   on the Draxans' arrows: 11 weapon casts (DSCLOG2's `weapon_casts`) and **no touch attack line**.
   Each spell landed straight after its hit ("Draxan takes 6 from Cause Light Wounds"; "Thy'rokh
   takes 2 from Chill Touch" after a failed save).

## Differences from Shattered Lands, for the user

- **Focus Heat is stronger.** The sequel's Focus Heat adds the caster's level, and a weapon casts
  at 6, so the Searing Blade burns for 2d6+6. In Shattered Lands it does 2d6. Asked in the thread.
- **The spell arrows cast for anyone.** The sequel has no kits, so whoever shoots them casts their
  spell, at level 6 (SL: a Spellarcher only, at its preserver level).

Water: none new (the same street).
