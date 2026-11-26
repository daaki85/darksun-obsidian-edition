# Test log: fire, cold and electricity, Wake of the Ravager (2026-11-21)

Under test: DEX instead of a doubled d20 (SL's RULE_NO_DOUBLE, always on), ported: the Loader's patch
"no_double" (the saving throw's `shl al,1` at 66E63h made two NOPs: the stock game doubles the d20
when the spell's flags word, +1Ah, has 86h) and the spell fix "dodge" in the Loader's RESOURCE.GFF
copy (bit 40h of the category word, +11h, on the 32 records so flagged).

## Found first

- The sequel's modifiers routine (628h:A7h, 83606h) reads the spell's record (B8h:3) and has SL's
  tests as they were: +11h bit 40h subtracts the target's DEX AC adjustment (98h:2F2h), 1Eh adds WIS
  (98h:324h). No spell has the bit in the stock game.
- The spell save: the sequel's save routine takes the spell's kind (+1Fh bits 5-7) as the sheet's save
  index directly, so kind 5 is already the spell save. Nothing to port.
- Finger of Death and Prismatic Sphere carry the fire flag (0202h, FFFFh) and so get the DEX too, as
  their doubling was.

## In the game (ravhold.sh, RAV_LOADER=1, about 15:00 UTC)

The Draxans' ambush in Tyr, the party given 250 HP (a test edit; DOSBox stopped after, nothing
saved), the dice log with 0xE0008205. The Loader's copies checked first: DSUNLOG2.EXE has `90 90` at
66E63h, Fireball's record +11h is 40h.

Ar'anda's Fireball (LEVEL 3 on USE, the first icon) on the Draxans, catching two party members:

| Who | DEX | d20 | Total | DEX adjustment |
|---|---|---|---|---|
| Terrannus | 17 | 13 | 16 | +3 |
| Draxan | 20 | 12 | 16 | +4 |
| Draxan | 20 | 10 | 14 | +4 |
| Thy'rokh | 21 | 11 | 18 | +7 (his AC line's DEX -5, and +2 the log doesn't name) |

None doubled (the stock game's would be 26, 24, 20, 22 before the modifiers): every total is the d20
and the DEX defence. Each saved for half damage.

## Still to do

- The dice log's save line in the sequel says "d20 total N" without the parts (the natural roll isn't
  recorded there), so the DEX isn't named; Thy'rokh's other +2 not identified (a thri-kreen's?).
- Cold and electricity not cast here (the same flag test).

Water: none new (the same street).
