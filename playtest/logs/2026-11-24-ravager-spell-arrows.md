# 2026-11-24: the spell arrows at the archer's level in Wake of the Ravager

*Branch `claude/ravager-party-transfer`. reports/wake-of-the-ravager-party-transfer.md, group C.*

The user's choice (2026-11-23), for the spell arrows that cast for anyone at level 6: "the caster's spell
level". Read as Shattered Lands has it (ARCHER_LEVEL): an arrow's spell casts at the archer's preserver
level; a party member with no preserver class shoots them as plain arrows; anyone else at its highest
level. A weapon's own spell keeps level 6 (the Searing Blade's 2d6+6, the user's earlier choice).

## The build

- **WEAPON_CAST** (site 46, 5D2C2h) pushes the archer's level for the cast when the hit's spell is one of
  the arrows' (Chill Touch 3, Shocking Grasp 10, Vampiric Touch 38, the sequel's numbers) and not the
  weapon's own (item SI's +10h less 1). The attacker is combatant DI (the cast's caster); `[4206h]` is
  the target (an early build read that, and gave the target's level).
- **PLAIN_ARROW** (site 49, 5D248h, "mov [bp-18h],ax / dec word [bp-18h]") makes the game's own move,
  then for a party archer with no preserver class puts the spell past the game's (148h): the game's
  own test at 5D24Eh then skips the whole cast, as for an item with no spell.
- Unit tests: `test_ravprotect.ProtectionTests.test_spell_arrows` (both sites, every case).

## In the game (a copy of `$WORK/rav` with the transferred `fountain-user` party, the Draxans' fight in Tyr; Computer Control for all four)

Test edits in memory, never saved (scratch `arrows.py`): Ester's and Jenna's plain arrows given Chill
Touch (power 4), every bow and arrow +15 so they hit. Lex's arrows are her own, transferred: Shocking
Arrows (the Loader's object 22618, power 11).

- **Found on the way**: in the sequel's items, arrows are type 6 in slot 1 and the bow type 18 in slot
  2; the attack's item SI is the bow, and `308h:[7]` the arrows' power, which comes first.
- **A first build skipped the cast** at WEAPON_CAST (the call jumped over, the pushed words dropped).
  The game crashed twice a round later (HP and AC read as garbage, then DOSBox gone); a control with the
  committed helper and the same edits ran clean. The attack calls 5F0h:D4h for the cast before the
  site, and skipping only the cast left that half done. PLAIN_ARROW skips the cast the game's own way.
- **The build kept** (four rounds, no crash):
  ```
  Lex attacks Draxan#21 with Wooden Bow +15 (1d8+15): d20 = 4, hits on anything but a 1 (95%), hits AC -5, target AC 7 -> HIT
  Shocking Grasp damage: 1d8 = [2] +2 = 4 (1d8 + 1 for each caster level: 2 at caster level 2)
  Ester attacks Draxan#27 with Wooden Bow +15 (1d8+15): d20 = 9, hits on anything but a 1 (95%), hits AC -9, target AC 1 -> HIT
  Jenna attacks Draxan#21 with Wooden Bow +15 (1d8+15): d20 = 20 (natural 20), hits on anything but a 1 (95%), hits AC -20, target AC 7 -> HIT
  ```
  Lex (fighter 3, preserver 2): every Shocking Grasp at caster level 2 (it was 1d8+6, level 6, before).
  Ester (fighter/druid) and Jenna (ranger): no Chill Touch after any hit, DSCLOG2's `arrows_plain` 3.

## Also played: the spellbook and the tome's message (2026-11-23, logs/2026-11-23-ravager-tome-scrolls.md)

No new area, no water noted.
