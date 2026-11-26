# Test log: scores and hit points as rolled, Wake of the Ravager (2026-11-22)

Under test: SL's scores and hit points as rolled (game.RULE_ROLLED, rules_hi 32; DSCLOG's RL_*) in
DSCLOG2: RL_SCORE, RL_HP, RL_ROLL, RL_CON and RL_SUM (sites 27-31). RULE_ROLLED added to
ravager.RULES_PORTED.

## Found first

- The sequel's creation screen is SL's code moved 7D89h on, its data 6C0h back: the score click
  writes `mov al,[bp-2] / mov es:[bx+19h],al` at 6D1DDh (the creature being made DS:142Dh, its
  scores from +19h, SL's +22h); the least and most score are DS:42D4h and 42D2h, the most hit points
  DS:42D6h (the least 42D8h), the race's adjustment + 4 DS:42DAh. The hit point click's `add
  ax,[bp-2]` is at 6B7D2h, CON's case `les bx,[1429h]` at 6B6CFh, the die's three loops' writes at
  6D55Ah, 6D593h, 6D5CCh (their roll flag the byte `[BP+6]`, SL's DI), the scores' redraw 6CD7Bh
  (its `add sp,4` after the put-back at 6CD98h; the saved background selector 368h, SL's 340h).
- A score click: left +1, right -1; past the most it goes round to the least and back (a right click
  on STR 17 gave 20 with the rule off: 17 is that score's least here). The hit point click answers on
  the line below its numbers (game y 175-178, x 84-120), not on them.

## In the game (ravcreation.sh 3, the Loader's game, a new fighter; about 20:35-20:55 UTC)

Rules written with `ravcreation.py` (RULES_PORTED), then rules_hi f226h (on) or f206h (off) for the
control by hand. After three rolls: Kornec, human fighter 7, scores 17 17 16 18 14 17, total 99.

- **SUM**: "SUM:99/99" under CHR (screenshot), redrawn with every score click.
- **A raise with nothing to spare**: STR 17 left click: kept at 17 (the counter of raises cut 1);
  INT 18 left click: kept.
- **Lowering frees points**: WIS 14 right click: 13 (SUM 98/99); INT left click: 19 (SUM 99/99); INT
  again: kept at 19.
- **The hit points as rolled**: two left clicks and a right click on them: 55 stays 55.
- **CON**: 16 lowered to 15: the most hit points 84 to 77 and the hit points 58 to 51 with them.
- **Control, the rule off**: INT 19 to 20 (a total of 100 over the die's 99); the hit points 51 up to
  55 with clicks, then 54; CON 15 raised to 16: the most back to 84, the hit points left at 51 (the
  game's); no SUM drawn ("SUM:" stays only where the rule had drawn it before it was turned off).
- Water: none (the creation screen).
