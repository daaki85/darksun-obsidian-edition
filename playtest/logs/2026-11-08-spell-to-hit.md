# Play test: spells roll to hit (2026-11-08)

Under test: the Options tab's new rule "Spells roll to hit" (settings key `spell_to_hit`, on by
default; `gamepatch.SPELL_TO_HIT`: `spell_hit` at 7A15Ah and `spell_hit_stub` at 78BA3h, DSCLOG's
SPELL_HIT and SPELL_STUB, site numbers NS_IMAGE + 74 and + 75). DOSBox, the Loader's patched game,
dice log `$PLAYTEST_WORK/dice.txt`. The DOSBox lock (`/tmp/playtest/dosbox.lock`) held throughout;
the DOSBox left from an earlier run (lock free) was replaced by `loadsave.sh`.

## Summary

| Case | Seen (dice log) | Verdict |
|---|---|---|
| Acid Arrow (Lex, preserver 9) | `Lex's Acid Arrow at Templar: attack d20 = 12, needs 4+ (85%) (THAC0 12 (a fighter's of the caster's level), +4 DEX; target AC 4) -> HIT`, then `Templar takes 3 from Acid Arrow` | OK: 21 - 9 = 12 |
| Magical Stone (Ester), three throws | each throw its own roll: HIT, HIT, then `attack d20 = 10, needs 11+ (50%) (THAC0 19, +4 DEX; target AC 4) -> MISS: the spell does nothing, the 2 damage rolled lost`, no HP lost | OK |
| Condense (Ester) | `attack d20 = 9, needs 14+ (35%) (THAC0 19, +4 DEX; target AC 1) -> MISS: ..., the 4 damage rolled lost` | OK |
| Turn Pebble to Boulder (Lex) | `3d6 = [5 + 2 + 3] +8 = 18`, `attack d20 = 12, needs 4+ (85%) (THAC0 18, +4 DEX; target AC 10) -> HIT`, `Templar takes 18` | OK |
| Chill Touch (Lex, beside the Templar) | `touch attack d20 = 8, needs 14+ (35%) (THAC0 18, +3 STR; target AC 1) -> MISS: the spell does nothing, the 4 damage rolled lost`, no HP lost | OK |
| Shocking Grasp | `touch attack d20 = 1 (natural 1), needs 14+ ... -> MISS: ..., the 15 damage rolled lost` | OK |
| Vampiric Touch (Templar's base AC raised in memory to give a hit) | `touch attack d20 = 15, needs 5+ (80%) (THAC0 18, +3 STR; target AC 10) -> HIT`, `Lex now 185/200 HP (+14)`, `Templar now 93/150 HP (-14)` | OK: the drain after the hit |
| Cause Light Wounds (Ester) | `1d8 = [3]`, `touch attack d20 = 16, needs 6+ (75%) (THAC0 19, +3 STR; target AC 10) -> HIT`, `Templar takes 3` | OK |
| Magic Missile (Lex) | `5d4 ... = 16`, `Templar takes 16`: no attack line | OK: unchanged |
| A weapon's spell on a hit (Jenna's swords given Chill Touch, item +0Fh = 4, in memory) | `Jenna attacks Guard ... -> HIT`, `Chill Touch damage: 1d4`, the save, `Guard takes ... from Chill Touch`: no attack line for the spell | OK: no second roll |
| Acid's burn each round (spell 18 through the same routine) | `Templar now 139/150 HP (-5)` at the round's start, no attack line | OK |
| The switch off | `launch.content({'spell_to_hit': False})`'s copy: 78BA0h `558becb801005dcb`, 7A15Ah `8976fa`, DSUN.EXE's; on: `558beccd987e5dcb`, `cd987d` (the only 6 bytes that differ) | OK |

Not done: a monster casting one of these (none of the ambush's foes did; the monster path,
caster combatant 4+ with the difficulty, is in the Unicorn test); a Spellarcher's spell arrows (the
same path as the sword's spell on a hit above: ARROW_LEVEL then CAST_SITE, checked); Acid Arrow
missing (its burn not put on: by the code, 78D42h skips the effect).

## Steps

- Build check: `dos/DSUNLOG.EXE` 7A15Ah `cd 98 7d`, 78BA0h `55 8b ec cd 98 7e 5d cb`; DSCLOG in
  memory at C91B0h, SPELL_HIT's first 40 bytes (image offset 83E1h) found at D1591h; INT 98h's
  vector C91B:4A15.
- `loadsave.sh fountain-user`, the speech clicked away: Pehtucl's ambush. `spellsetup.py 0=9 2=9
  hp=200 18 3 10 39 8 53 9 75 72 113 111 97 119 128` (Lex preserver 9, Ester priest 9; Ester's
  Magical Stone, Condense and Cause Serious "cast at level 0": not her spheres), `hp.py 150`.
- The Templar (combatant 25, creature 30) came up to the party; touch spells need the caster beside
  the target: "can't cast Chill Touch there: too far away" from two squares. Moving a combatant in
  memory (DS:669Dh + 32n) didn't move its figure or what a click finds ("no creature there"): walk
  the caster up with the arrow on its own turn first (a member hit before its turn has its icons
  crossed out: cast the next round).
- Escape while aiming cancels the aim and opens EXIT GAME? (CANCEL at 125,116); the aiming pointer
  stays on the screen after it. A right-click to set the walk pointer then ended Lex's turn.
- The USE button (24,17) opened the Effects screen once (the screen last used): its icon at
  100,171 goes to USE.
- Seneca hides far north each round (888,1384): `passuntil.sh` stops "off screen"; a drag
  (`scroll.py 0 60`) puts her on screen for her END menu. The kit's
  `/tmp/playtest/tolex.sh` did the passing with that drag (not kept).
- Lex's level pages cycle 1-4 (his known spells' levels): LEVEL clicks wrap at 4, not 5.
- Afterwards: the items' +0Fh and the Templar's base AC put back; nothing saved; DOSBox, the dice
  log and the watchdog stopped; the lock released.
