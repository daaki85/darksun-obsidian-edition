# Test log: Strength's dice by class, Wake of the Ravager (2026-11-21)

Under test: DSCLOG2's SITE 10, STRENGTH_DICE (SL's strength_dice): Strength's (23) handler's "push
dword 60001h" (1d6; 6624Eh, SL's 79483h) made the target's classes' AD&D die (warriors 1d8, priests,
rogues and psionicists 1d6, wizards 1d4; a multiclass character's best); Adrenalin Control (245, the
same code) and a creature with no class keep 1d6.

## Found first

- The sequel's handler is SL's: DI the target combatant, [BP+0Eh] the spell (0F5h Adrenalin Control
  gives effect 2, the rest effect 62h, Strength); Strength is spell 23 as in SL, and the sequel has no
  Cat's Grace (the mod's own in SL). The sheet's classes at +1Bh: SL's 1-17, then 18 (a wizard's) and
  19 (a priest's) (ravlog's WIZARD_CLASSES and PRIEST_CLASSES).

## In the game (ravhold.sh, RAV_LOADER=1, the dice log on, about 19:20 UTC)

Ar'anda taught Strength, a 10th-level preserver with casts left; the party's HP 250 (scratch
ssetup.py; test edits). DOSBox stopped after, nothing saved.

- USE, LEVEL to 2, Strength (x 213), then Gerakis's box on the USE screen (a touch spell takes a
  character's box as its target).
- "Strength: 1d8 = 3 (gladiator) -> Gerakis's STR +3 while it lasts (at most 24)": the game rolled 1d8
  (its own 1d6 before), and the effect's entry `03 00 00 00 17 00 62 00 00 03` (Gerakis, spell 23,
  Strength 62h, its amount +9 the roll 3). The helper's count 1.

## Still to do

- A wizard target (1d4) and Adrenalin Control (1d6) seen.

Water: none new (the same street).
