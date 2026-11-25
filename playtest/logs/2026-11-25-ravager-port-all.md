# 2026-11-25: the Ravager port's branches together, a smoke run

**Under test:** branch `claude/ravager-port-all`: `claude/ravager-kit-choice` (on `claude/ravager-kits`) with
`claude/ravager-thieves` and `claude/ravager-sphere` merged, DSCLOG2.EXE rebuilt from the merged source (39776
bytes). DSCLOG2's site table: 52 THIEF_SKILL, 53 STAB_TIMES, 60-61 the kits', 62-69 the KIT pages, 70-75 the
screens', 76 DUAL_KIT, 90-92 EL_SPHERE; 54-59 and 77-89 `site_none`. Every ported rule on (no settings.json:
the Loader's defaults; DSCLOG2's header rules 0xFB45, rules_hi 0xFF2F).

The run ([files/2026-11-25-ravager-port-all-run.sh](files/2026-11-25-ravager-port-all-run.sh)): a fresh
copy `ravPA` of `ravK` (the `fountain-user` party transferred), ravstart with the Loader (`RAV_LOADER=1`,
`RAV_STDOUT=1`), the four ADDed, a new game, HP 250 for the four (a test edit, never saved; the copy thrown
away after), the dice log (`ravdice.py --numbers`), Computer Control for all four in the Draxans' ambush.
No kit edits: Ester's Battle Dancer is the transfer's own.

## What was seen

- **The fight won** in about three minutes: "Each party member receives 10000 experience points!"
  ([picture](img/2026-11-25-ravager-port-all-won.png)). **STDOUT.TXT empty**: no "Illegal Op".
- **Specialization**: `THAC0 18 base, +1 in bonuses, +1 specialized = 16`, `Lex hits Draxan#23 for 8: 1d8
  = [8] -2 wooden +2 specialized` (16 "specialized" lines in 580).
- **A kit**: `Ester hits Draxan#23 for 4: 1d8 = [5] -2 wooden +1 Battle Dancer`.
- **The thief table**: `Seneca hides in shadows: d100 = 42, needs 33 or less (57 +10 cloak = 67, halved in
  daylight) -> seen` (57: AD&D's average for her level with the halfling row, as in the thieves' log).
- DSCLOG2's counters at the end: kit_hits 6, kit_damages 6, kit_moves 10, kit_twos 2, spec_hits 10,
  spec_damages 10, spec_rates 18; the rest 0 (no backstab, no Elementalist in this party).
- **Memory** (`dosmem.py`): DSCLOG2 39248 bytes in upper memory (the kits' build 36192), 116208 bytes of
  it free after in one piece; DOS memory free after the game 80 KB.
- The sequel's window was 640x480 (the clicks through `ravclick.py`, as in the kits' runs).
- No water in this run (Tyr's ambush street only).
