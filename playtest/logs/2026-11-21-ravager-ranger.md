# Test log: rangers' casting level, Wake of the Ravager (2026-11-21)

Under test: DSCLOG2's RANGER_LEVEL (SL's PROBE_RANGER_LEVEL, RULE_HI_RANGER): the level a ranger's spell
takes for its duration and damage is the ranger's level less 7, as the level it casts at already is.

## Found first

- The sequel's caster level routine has SL's "sub dx,7" for a ranger (97E00h, SL's 81B6Ah: classes 13
  to 16, in SI there).
- The duration and damage level routine: 628AFh (SL's 5E25Ch), the best level of the caster's classes
  that cast the spell, a ranger's whole. Its read of a class's level is "mov al,es:[bx+1Eh] / mov ah,0"
  at 629F0h (SL's "mov al,es:[bx+24h] / cbw"): INT EAh there.

## In the game (ravhold.sh, RAV_LOADER=1, about 15:30 UTC)

The Draxans' ambush; Thy'rokh (fighter/druid 6/6) made a fighter/ranger (fire), the ranger 12th level,
the four given 250 HP (test edits; DOSBox stopped after, nothing saved). The dice log with
0xE0028205 (RULE_HI_RANGER on). Thy'rokh's turn (ravfight.py until 2), USE, LEVEL 1, Shillelagh:

- "Shillelagh lasts 9 rounds (caster level 5: 1 for each caster level = 5 + 4 from the dice; dice 4d1)".
  The level is the game's own argument to the duration roll (the dice log reads it from the call), so
  the game took 12 less 7; the stock game passes 12 (16 rounds).

## Still to do

- A ranger's damage spell not cast (the same routine gives both).

Water: none new (the same street).
