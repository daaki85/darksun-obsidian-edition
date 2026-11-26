# Test log: multiclass hit points, Wake of the Ravager (2026-11-22)

Under test: SL's multiclass hit points (game.RULE_MULTI_HP, always on in SL; DSCLOG's CON_SHARE at
PROBE_MC_CON and PROBE_MC_UNCON) in DSCLOG2: MC_CON (site 25) and MC_UNCON (site 26) with CON_SHARE on
the sequel's layout. RULE_MULTI_HP added to ravager.RULES_PORTED.

## Found first

- The sequel's most hit points is SL's routine at 95193h (SL's 874B0h): the sheet's total (+0Ah) times
  the levels (+1Eh..) over the levels before any were lost (+39h..), divided (unsigned, where SL's is
  signed) by the classes (9521Ah: 1 for a human, race +12h 1, else the classes set), plus CON's part
  (95261h); `add di,ax / mov ax,di` at 95208h. The reverse (954A5h, SL's 877BEh): `mov dx,[es:bx+8] /
  sub dx,ax` at 954BDh (SL's patch site, `sub dx,ax`, is only 2 bytes: too short for a SITE).
- CON is the creature's +1Bh; the hit point table (dice and last level by group, the class's group at
  +10h, a warrior's CON bonus at +52h) is SL's, byte for byte, at the load + 45BEh (4D0h in the code).
- Its callers: the level up (957E2h) and a sheet made from a script (6E8CEh, the reverse). Nothing else
  works the most out again, so a level up is the way to see it.

## In the game (ravhold.sh, the Draxans' ambush; the Loader, the dice log on; about 20:00-20:20 UTC)

Test edits (DOSBox stopped after, nothing saved): Ar'anda's thief level and best 7 made 6, Thy'rokh's
druid level and best 6 made 5 (the fight's 10,000 XP brings them back), the party's HP 250 and base
AC -10, the four Draxans near at 1 HP, Computer Control for all four.

- **The rule on** (DSCLOG2's rules 6804h): Ar'anda's 7th thief level, d6 = 4: total 102 to 106, most
  hit points **48** = (106 + 2 x 19 dice) / 3 (CON 17's +3, at most +2 for a class that isn't a
  warrior's; her levels 6 + 6 + 7). The game's own would be 106 / 3 + 2 x 7 (its highest class's
  levels) = 49. Thy'rokh's 6th and 7th druid levels (8, 2): total 94, most **79** = (94 + 5 x 13) / 2.
  MC_CON counted 6 calls.
- **Control, the rule off** (2804h): Ar'anda's d6 = 5, total 107, most **49** = 107 / 3 + 14, the
  game's; with the rule it would be 48. Thy'rokh total 96, most 80: both ways the same for a warrior
  (the full bonus on every die). MC_CON counted nothing.
- The dice log's level-up line says "into the total shared by 3 classes" in the control too: it
  describes the rule (SL's, always on).
- Water: nothing new (the ambush's street).
