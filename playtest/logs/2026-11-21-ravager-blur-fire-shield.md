# Test log: Blur's and Fire Shield's saves, Wake of the Ravager (2026-11-21)

Under test: DSCLOG2's BLUR_SAVE and FSHIELD_SAVE (SL's blur_save and fire_shield_save, of "spells and
psionics as the manual describes them"): Blur +1 on saves against magic, Fire Shield +2 against fire
and cold. The sequel's manual says both, as SL's does (its spell texts are SL's).

## Found first

- **The sequel's save modifiers** (83606h, SL's 79D46h) are rewritten: DI the modifier, [BP+0Ah] the
  target's effects' bits (far; bit n effect n, the sequel's numbering: 6 Barkskin, 9 Blessed, 13 Blurry,
  38 Fire Shielded, 73/77/78 Protected vs Cold/Fire/Lightning), [BP-4] the spell's flags (+1Ah). It has
  Barkskin's +1 (8373Ah) and Blessed's +1 but nothing for Blurry or Fire Shielded. Protection from Fire
  and Lightning are +4 here (SL's +3), Cold +3.
- **The effects' bits** (608h:25h, 7FE93h) are made from the effects table's run of records of one
  owner (d8h:0Dh finds the first): the table is kept in owner order, so a record put in for a test goes
  in its owner's place (scratch `eff.py`: owner, caster, spell words, the effect byte, three zero bytes).

## In the game (ravhold.sh, RAV_LOADER=1, about 16:10 UTC)

The dice log attached (the rules on). Draxan 21 given Blurry (13, spell Blur) and Fire Shielded (38,
spell Fire Shield) in the effects table (test edits; DOSBox stopped after, nothing saved). Ar'anda's
Fireball on Draxans 21, 26, 27.

- The helper's count of Blur's and Fire Shield's modifiers: 2 (one each, the Fire Shielded Draxan's
  save alone); the two others' saves added nothing.
- The log: "Draxan's saving throw vs Fireball from Ar'Anda (spell): d20 total 6, needs 11 -> failed"
  (its model takes both in), the others "d20 total 19, needs 13" and "total 9, needs 13".
- The shielded Draxan took 24 of the 24 rolled (60 to 36): the log said "(halved: Fire Shielded)", so
  either the sequel doesn't halve fire on a Fire Shielded creature (SL's 7B565h does) or it had lost HP
  before. To check.

## Still to do

- The game's own save total (not the log's) for a Blurry target, to see the +1 there.
- Fire Shield's halving in the sequel (above).

Water: none new (the same street).
