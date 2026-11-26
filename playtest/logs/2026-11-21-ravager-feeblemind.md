# Test log: no psionics while feebleminded, Wake of the Ravager (2026-11-21)

Under test: DSCLOG2's SITE 12, PSI_FEEBLE (SL's feeblemind_psionics): the psionic power check
(61D2Eh, SL's 5D59Dh: SI the user, DI the power, numbered from 0), after its test that the user has the
power ("or ax,ax / jnz 61D50h / mov al,0", 61D47h): a feebleminded user (the sequel's effect 37) can use
no power, as the manual has it (the game's Feeblemind stopped spells only).

## In the game (ravhold.sh, RAV_LOADER=1, the dice log on, about 20:00 UTC)

The party's HP 250 (scratch csetup.py) and Feebleminded (37, spell 62) put on Ar'anda in the effects
table (`eff.py 0 37 62`; the USE screen showed her "Feebleminded"); test edits, DOSBox stopped after,
nothing saved.

- Ar'anda's Cellular Adjustment (PSIONIC, Metabolic, x 232) on Gerakis's box: nothing healed, the
  helper's count 1, the log "Ar'Anda is feebleminded: Heat Exhaustion can't be used (no psionics)":
  the right refusal with SL's name for power 13 (SL's powers start at 138, the sequel's at 0EBh).
  Fixed: GameData.psionic_first, RavGameData's 0EBh (test_ravlog's
  test_psionic_powers_by_the_sequels_numbers); on her next turn, the dice log restarted: "Ar'Anda is
  feebleminded: Cellular Adjustment can't be used (no psionics)", Gerakis's HP unchanged.
- Her PSPs went 96 to 84 over the two tries: a refused power still costs its points here (the game's
  own way after a failed check; SL's the same code).

## Still to do

- Heal curing Feeblemind (SL's PROBE_CURE) isn't ported.

Water: none new (the same street).
