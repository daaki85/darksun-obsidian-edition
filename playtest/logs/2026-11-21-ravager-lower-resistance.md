# Test log: Lower Resistance as the manual has it, Wake of the Ravager (2026-11-21)

Under test: DSCLOG2's SITE 8 and 9 and ACID_ROUNDS: CAST_START keeps a cast's level (the cast's tail,
7E32Ch, at "mov di,[bp+0Ah]", 7E338h); ACID_ROUNDS puts it into Low Magic Res.'s (61) amount, the
entry's +9, as Lower Resistance (64) puts the effect on; LOWRES_SITE (84B2Eh-84B4Eh, 33 bytes, the
magic resistance routine 84AB5h, SL's 7A4A8h) takes 30% + 1% a level of the caster off, the effect's
level or the cast's own, the bigger, where the game halved the resistance for the effect and took 30 +
the level off for the cast itself (SL's lower_resistance_manual).

## Found first

- The sequel's routine is SL's: [BP+6] the combatant, SI the spell, [BP+0Ah] the cast's level, [BP-2]
  the resistance (the sheet's +23h), Mind Barred (64) +75 ([BP-0Ah] 1), Low Magic Res. (61) halving
  ([BP-0Bh] 20h), Lower Resistance's own 30 + level, then at least 0. The only reader of the sheet's +23h.
- The effect adder (7FA40h on) writes its argument [BP+12h] into the entry's +9 just before
  ACID_ROUNDS' compare (7FAA6h), ES:BX the entry less 24Dh: the place to put the level.
- The dice log read Mind Bar and Low Resistance by SL's numbers (32, 31): now game.MIND_BAR_EFFECT and
  LOW_RESISTANCE_EFFECT, which the sequel's layout makes 64 and 61 (test_ravlog's
  test_magic_resistance_reads_the_sequels_effects).

## In the game (ravhold.sh, RAV_LOADER=1, the dice log on, about 18:30-19:00 UTC)

Ar'anda taught Flaming Arrow and Lower Resistance and made a 10th-level preserver with casts left; the
Draxans' sheets' magic resistance 50; the party's HP 250 (scratch lsetup.py; test edits). The others
under Computer Control, Ar'anda by hand. DOSBox stopped after, nothing saved. (A first run without the
HP edit and with `ravfight.py until 0`, which ends the others' turns, lost the fight: the cast was seen
before it.)

- **Lower Resistance's own check**: "Draxan magic resistance 10% (-40 this Lower Resistance, level 10)
  vs Lower Resistance to Magic: d100 = 29 -> not resisted" (twice, in both runs); the effect's entry
  after: `1a 00 00 00 40 00 3d 00 00 0a`, Draxan 26, spell 64, effect 61, **+9 10** (the level kept;
  the game's 0). The helper's CAST_LEVEL 10.
- **A later spell on it**: Flaming Arrow at the same Draxan, the helper's count up 1 for the
  resistance (the game's routine took the 40 off: the count moves only when it takes something), and
  with the fixed dice log: "Draxan magic resistance 10% (-40 Lower Resistance on it, level 10) vs
  Flaming Arrow: d100 = 87 -> not resisted" (the game's own would have been 25%, halved). Before the
  fix the log said 50%.
- Ar'anda's second Flaming Arrow bolt waits as the pointer until aimed, even across `ravfight.py wait`
  (it reports turn 0 while the bolt is pending).

## Still to do

- A control run (no dice log) to see the game's halving.
- A creature with Mind Bar against a mind-affecting spell (the log's +75 by the sequel's 64).

Water: none new (the same street).
