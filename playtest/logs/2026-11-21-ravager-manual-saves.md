# Test log: Stinking Cloud, Color Spray, Chaos, Cloudkill and classless levels, Wake of the Ravager (2026-11-21)

Under test: DSCLOG2's SITE (INT F5h and a byte, one vector for many sites, as DSCLOG's) with
STINK_ROUND, HD_SAVE, CHAOS_SAVE, SPRAY_SAVE, CLOUD_SAVE and CLOUD_KILL: SL's stinking_cloud_round,
classless_save_level, chaos_int, color_spray_level, cloudkill_save and cloudkill_kills (the manual's
spells).

## Found first

- **Spell time** (80171h, SL's 76CB3h): the same routine, "les bx,[bp-4]" at 80249h before the unit.
- **The save modifiers' tail** (83E83h on) is SL's 79F80h on with DI for SI: Chaos's -100 for a creature
  with no warrior levels (the sequel's own test, the best of classes 13-16 and 9-10 by 580h:61h), then
  Dismissal's level difference, Cloudkill's -100 for 6 levels or fewer, Scare's 6 or more. The target's
  level (83656h) from 98h:154h; the sheet [BP-0Eh] (classes +1Bh..+1Dh, levels +1Eh), the creature
  [BP-0Ah] (INT +1Ch).
- **The damage on one creature** keeps the save's answer at 651C5h ("mov [bp-1],al", SL's 78DB6h), the
  same frame (DI the combatant, SI the spell, [BP-6] the percent, a dword).
- **The sequel's Cloudkill allows no save** (its record's +1Fh 3Ch; SL's 3Dh; its manual: "SAVING THROW:
  None"). Left so: every creature of 5 levels or fewer it catches dies.
- The Draxans' kinds: sheet 14 (60 HP, class 13 level 10) and 16 (70 HP, class 19 level 10, which
  Chaos takes for a warrior). Casting: USE remembers its page; LEVEL goes round the levels with spells
  known; a caster hit this round has every icon crossed out.

## In the game (ravhold.sh, RAV_LOADER=1, the dice log on, about 16:40-17:20 UTC)

Ar'anda taught Color Spray, Stinking Cloud, Chaos and Cloudkill, made a 10th-level preserver with
casts left; Draxan kinds made classless (sheet classes 0, the first level byte the hit dice), one
Draxan's INT 21; the party's HP 250 in one run (all test edits; DOSBox stopped after each, nothing
saved).

- **Cloudkill's kill**: a classless Draxan of 3 HD took "60 from Cloud Kill, now 0/60" on a 1d10 of 3;
  the 10th-level Draxans took their 1d10 (8, 9, 10). The helper's count 1.
- **Color Spray**: on a classless Draxan of 10 HD (the caster 10th): "none allowed (cannot save) ->
  failed", Paralyzed (69) put on it; the count 2 (its level from the hit dice, and Color Spray's -100).
- **Stinking Cloud**: "lasts 5 rounds (... 4 from the dice + 1 more; dice 1d4 = [4])" and "4 rounds (3 +
  1)", No Attacks (65) on the Draxan; the count up 2.
- **Chaos** on the classless Draxans (no warrior levels now): those of INT 14-15 "cannot save" and
  Confused; the one of INT 21 rolled under its number anyway (every Draxan's d20 was 9 or less), so
  its save wasn't seen; the count went up by 7 (the levels and the INT 21 exemption).

## Still to do

- Chaos against an INT 21 (or 4) creature with a good roll.
- Cloudkill against 4 or 5 HD (dies, no save, as above) and 6 and more (damage).

Water: none new (the same street).
