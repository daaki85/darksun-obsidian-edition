# 2026-11-16: the kit rebalance's code audit, fixed

A read-only audit of the branch's DSCLOG and Loader changes found seven issues (the CHANGELOG's
"A code audit of the branch" lists them and their fixes). In the game (`fountain-user`, the new
build, `buildcheck.py` OK):

- **POISON_USED cleared by DSCLOG at a fight's start** (no longer by the dice log, a pass late):
  the header's +1860 written FFh in memory before the ambush (as a fight before would leave it), the
  ambush clicked into: at the first turn (Round 1 in the dice log) it read 00h. **PASS.**

The rest are covered by the emulator and Loader tests (`test_poisoner_on_a_helpless_target`,
`test_war_hit`, `test_myrmidon_polearm`, `test_gear_hold`). No game was saved.
