# Test log: Enlarge, Wake of the Ravager (2026-11-21)

Under test: Enlarge multiplies the weapon's dice only (SL's RULE_ENLARGE, always on), ported: DSCLOG2's
ENL_ROLL (INT EBh at 5D0C8h, after the attack's damage roll: the dice's sum kept for a melee hit) and
ENL_SITE (INT ECh at 863E7h, Enlarge's multiplying in 863B2h: the dice x(100 + 10 a level)%, rounded
up, the rest added once).

## Found first

- The sequel's Enlarge routine is SL's (863B2h, 628h:57h, called by the attack at 5D0D2h): STR's bonus,
  then with effect 32 (bit 0 of the effects bitset's fifth byte) the whole damage x(100 + 10 x the
  levels of the Enlarges on the attacker)% (608h:52h: each Enlarge's caster level, 698h:34h).
- The caster level routine (698h:34h, 97DC5h): below 0EBh the best level of the classes that cast the
  spell (588h:20h), a ranger's 7 less; 0EBh-10Ch the psionicist's level; 132h the best cleric level;
  else the creature's best. The sequel's spells: wizard 0-114, priest 115-234, psionic 235-268.
- The attack's frame is SL's but for its locals: the dice's bonus is [BP-14h] (SL's [BP-12h]).

## In the game (ravhold.sh, RAV_LOADER=1, about 16:00-16:45 UTC)

The Draxans' ambush; Ar'anda taught Enlarge (bit 5 of her known-spells bitset at 3F3DCh), the four
given 250 HP (test edits; DOSBox stopped after each run, nothing saved). The dice log with
0xE2028205. USE, LEVEL 1, Enlarge, dropped on Gerakis's portrait (her slots 3/4 to 2/4); the effects
table then held `03 00 00 00 05 00 20 ...` (Gerakis, Ar'anda, spell 5, effect 32). Then Computer
Control for all four.

- **Control** (RAV_SKIP=enlarge_roll,enlarge_dice: the stock game): Gerakis's hits the dice log put at
  24, 17, 19, 18 took 38, 27, 30, 28 off: the whole x160%, rounded down (Ar'anda's 6th level).
- **Patched, first run**: hits of 21, 23 took 24, 28: the dice 5 and 7 made 8 and 12 (x160%, rounded
  up), the rest once. The dice log's line didn't show Enlarge: its caster level for the effect read
  SL's sphere tables, which the sequel hasn't (now RavGameData.effect_caster_level, the sequel's
  routine).
- **Patched, after the fix**: "Gerakis hits Draxan for 24: 1d8 = [5] +4 weapon +12 STR 24 +3 Enlarge
  (the dice 5 x160% = 8, level 6)", and the Draxan "-24"; likewise 26/-26, 25/-25, 15/-15 (a 1 made 2).

## Fixed after

- The USE screen said "NO SPELLS IN ARMOUR" for Ar'anda (a multiclass preserver in armour: SL's class
  restrictions), which the sequel doesn't have: she cast Enlarge. RavGameData's no_spells and
  thief_heavy now follow RULE_RESTRICT, not ported.

## Still to do

- An Enlarged target counting as large (sizes) not seen.
- The Effects screen's DICE line (SL's ef_enlarge_dice) not ported.

Water: none new (the same street).
