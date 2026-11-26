# Test log: Cellular Adjustment's 1d4, Wake of the Ravager (2026-11-21)

Under test: DSCLOG2's SITE 11, CELL_HEAL (SL's cell_adjustment_heal): Cellular Adjustment's (power 248)
2 HP made 1d4, as the manual has it.

## Found first

- The sequel's handler for spells with rules of their own has Cellular Adjustment's case at 664C5h,
  "push 2 / jmp 65811h" (5 bytes; SL's 795A2h, "push 2 / jmp short"); Neutralize Poison's case ends
  "push ax / jmp 65811h" at 66545h, so CELL_HEAL rolls 1d4 into AX and returns there. [BP+8] the user
  (9999 for none), DI the target. Its record's cure of disease is the game's own; the record line
  (MN_CELL) leaves the kit's more 0 (the sequel has no kits).
- Psionic powers on the USE screen: the class button (`ravclick.py 150 171`, MAGE / PSIONIC), then the
  discipline button (197 171: Kinetics, Metabolic, ...); Ar'anda's Metabolic page has Energy Control,
  Life Drain, Biofeedback, Cellular Adjustment (x 232), and one more below.

## In the game (ravhold.sh, RAV_LOADER=1, the dice log on, about 19:40 UTC)

The party's HP 250, then Gerakis's 100 of 165 (scratch csetup.py; test edits). DOSBox stopped after,
nothing saved.

- Ar'anda's Cellular Adjustment on Gerakis's box: "Cell Adjustment: 1d4 = 1 -> Gerakis healed 1 HP",
  Gerakis 100 to 101 (the game's own HP). The helper's count 1.
- The dice log also put the HP change down as "Gerakis regenerates 1 HP (CON 22), now 101/165 HP": its
  HP watcher takes any rise it can't place for regeneration. To fix in the log.

## Still to do

- A roll above 2 seen; the log's regeneration line.

Water: none new (the same street).
