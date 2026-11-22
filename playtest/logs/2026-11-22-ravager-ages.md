# Test log: ages and magical aging, Wake of the Ravager (2026-11-22)

Under test: SL's ages (game.RULE_AGING, aging.py) in the sequel: RavDiceLog's aging pass (give_ages,
natural_tick for the years the clock passes, hasted for each new Hasted effect, 42), the age at the
sheet's +41h (AGE_PLAIN), and DSCLOG2's AGE line in PROBE_CHAR (RULE_HI_AGING, 256). RULE_AGING added
to ravager.RULES_PORTED.

## Found first

- The sheet's +3Dh, +3Fh and +41h are the only bytes no instruction of the sequel's reads or writes
  (ndisasm of DSUN.EXE, every `[es:..+NNh]`); +3Dh and +3Fh hold CHARTRAN's kit and second sphere, so
  the age goes in +41h, alone. No byte is left for a count of the years, and the sequel's flags have
  none spare: the years are counted as the clock passes them while the Loader watches.
- Ar'anda knows Haste (LEVEL 3 on USE, the middle icon at game 196, 60); it aims on the map (an area).
  Her class restriction stops it ("YOU CANNOT CAST SPELLS"): rules 4804h as a test edit.

## In the game (ravhold.sh's ambush, the Loader, the dice log on; about 20:10-20:35 UTC)

Test edits, DOSBox stopped after, nothing saved: rules 4804h; the party's HP 250 and AC -10 (tough.py);
the clock put at 365 days less 5 minutes (DS:9C0Ch's far pointer).

- **The rule on** (rules_hi FF2Eh): at the dice log's first look "Ar'Anda is 21 (an elf: 15 + 3d4 =
  [4 + 1 + 1]); middle-aged at 50", Terrannus 16, Thy'rokh 6, Gerakis 30 (sheet +41h 7, 2, 1, 11).
  Haste aimed at the party: all four Hasted, each "system shock (Haste's aging): d100 = 74, needs 99 or
  less (CON 18) -> survives" and "ages 1 year (Haste)". The fight run on past the year: "A year has
  passed: Ar'Anda is 23." and the other three. The inventory (I): **AGE: 32** between SP and STR on
  Gerakis's panel.
- **Control** (RAV_RULES_OFF=0x1000000: rules_hi FE2Eh): no ages given (+41h stays 0), Haste on the
  party with no shock and no year, the clock past a year with nothing, and no AGE line on the panel.
- Water: nothing new (Tyr's street).

Result: ages and magical aging work in the sequel. Not played: a failed system shock (death), a
category's score changes, death of old age (the same aging.py code as SL's, its tests).
