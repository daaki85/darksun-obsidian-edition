# Test log: the better of two hit dice, Wake of the Ravager (2026-11-21)

Under test: the first of the rules on the sequel. SL's "hp_best" (DSCLOG's PROBE_HP_BEST) as
DSCLOG2's, at the sequel's roll of a level's hit die (95025h, "mov cx,ax"; the roll starts at
9500Ah, SL's 872FDh), and the rules' plumbing: DSCLOG2's header now has RULES (+170) and RULES_HI
(+270), and the Loader writes only the rules ported to the sequel (ravager.RULES_PORTED; RavDiceLog's
set_rules, RavGameData.rules).

## Found first

- The sequel has two hit-die rolls in its level routines: 9501Dh (SL's, used by the creation screen's
  die) and 95CCEh (a level-up from XP, rolling up to three classes in a loop). Only the first is
  SL's patch; the second is the sequel's own and isn't hooked yet.
- The roll goes into the sheet's +0Ah (the rolled hit points before CON), capped by a class
  table's byte (+38h). The creation screen's hit points line reads the creature's +0 over the sheet's
  +8, and showed 7/7 for a 7th-level fighter in every roll (rule on or off): what the sequel does
  with +0Ah afterwards is still to be read.
- The helper writes nothing for a dice log started without settings (`ravdice.py`): its rules are 0
  until the Loader's settings set them.

## In the game (creation screen, about 03:45 UTC)

- A script attached RavDiceLog and set the rules (all on: masked to 8000h in DSCLOG2's header), then
  clicked the die 15 times with the rule off and 15 with it on, reading the sheet's +0Ah each time
  (a 7th-level fighter, d10 a level):
  - off: 46 37 33 45 30 26 45 40 38 39 59 43 39 44 33, mean 39.8 (7 x 5.5 = 38.5 expected)
  - on: 46 54 53 61 53 55 46 52 44 61 54 55 52 48 50, mean 52.3 (7 x 7.15 = 50 expected for the
    better of two d10s)
- Nothing else changed on the screen; the THAC0 line still drawn.
- No water: the creation screen only.
