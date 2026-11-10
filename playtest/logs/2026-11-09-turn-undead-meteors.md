# Play test: Turn Undead by AD&D's table, Minute Meteors' five globes, Flame Arrow's bolts (2026-11-09)

Under test, all with "Spells as the manual describes them" and "Spells roll to hit" on (the
defaults):

- `turn_undead_manual` (7AE01h, DSCLOG's `TURN_SITE`, `tu_site`): AD&D's turning table, turned
  undead Afraid for 3d4 rounds (added through 598:3Eh), D, D\*, and no second try by a priest who
  failed on that undead this fight; the dice log's `KIND_TURN` line (`_turn_manual`).
- `meteors_count`, `meteors_damage`: Minute Meteors five globes of 1d4; `TH_METEORS`: each rolls to
  hit with +2.
- `flame_arrow_damage`, `flame_arrow_count` (7567Fh, `FLAME_SITE`): a 5d6 bolt for every five
  caster levels.

DOSBox, the Loader's patched game, the dice log `$PLAYTEST_WORK/dice.txt`, all under
`/tmp/playtest/dosbox.lock` (waited for another agent's hold from 00:34 to 01:12, then held by a
background `flock` until the end; this session's DOSBox, dice log and watchdog stopped at the end).

## Build check

- `dos/DSUNLOG.EXE` (the Loader's patched copy): 7AE01h `cd 98 7f 90`, 7567Fh `cd 98 80`, 42390h
  `16`, 423ACh `00 09 04`, 4230Ch `00 29 06`, 7A15Ah `cd 98 7d`.
- DSCLOG in memory at C91B0h: the first 40 bytes of `tu_site` (image 8694h), `flame_site` (8898h)
  and `th_hit` (8421h) found there; INT 98h's vector C91B:4A15.

## Results

| Case | Seen (dice log) | Verdict |
|---|---|---|
| Fail (Seneca cleric 1 vs the Templar made undead, 5 HD: 20 needed) | `Seneca turns Templar: d20 = 8, needs 20+ (priest level 1 vs 5 HD, AD&D's table) -> not turned: can't try again on it this fight` | OK |
| The same priest again, next round | `Seneca can't turn Templar again: failed against it this fight` (no d20 rolled, the turn spent) | OK |
| T (Seneca 4 vs a Guard made 1 HD) | `Seneca turns Guard: turned: flees 3d4 = 10 rounds (Afraid), automatically (T) (priest level 4 vs 1 HD, AD&D's table)`; `Seneca gives Afraid to Guard`; effects.py `Afraid (10 rounds)`, 600 s. On its next turn the Guard didn't attack and ran north, from screen (192,144) to (288,0) and later off it (map 1080,1240) | OK: the undead flees |
| The same turning's area caught the Templar beside it | `Seneca can't turn Templar again: failed against it this fight` | OK (the game tries every undead the box reaches) |
| D\* (Seneca 8 vs four Arena Guards made 1 HD, one sheet, in one box) | `Seneca turns Arena Guard: destroyed automatically (D*), and up to 2d4 = 5 more of its kind this turning`, then `destroyed, one of the D*'s more of its kind (4 left)`, `(3 left)`, `(2 left)`; all four killed, 480 XP | OK |
| Another priest on a creature Seneca failed against (Jenna, a human ranger with a cleric class in memory: priest level 0 by the game) | `Jenna turns Templar: d20 = 3, needs 13+ (priest level 0 vs 1 HD, AD&D's table) -> not turned` | OK: allowed (per priest); level 0 one column before level 1 |
| D (Lex, cleric 6 as a third class in memory, vs the Templar 1 HD) | `Lex turns Templar: destroyed automatically (D) (priest level 6 vs 1 HD, AD&D's table)` / `  Templar is destroyed by Turn Undead`, XP | OK |
| A number made (second load: Seneca 3 vs the Templar 1 HD: 4 needed) | `Seneca turns Templar: d20 = 19, needs 4+ (priest level 3 vs 1 HD, AD&D's table) -> turned: flees 3d4 = 9 rounds (Afraid)`; effects.py `Afraid (9 rounds)` | OK |
| Minute Meteors (Lex, preserver 10) at the Templar | five casts, each `Minute Meteors damage: 1d4 = [...]` and `Lex's Minute Meteors at Templar: attack d20 = N, needs 8+ (65%) (THAC0 18, +4 DEX, +2 Minute Meteors; target AC 4)`: HIT 4, MISS (2 lost), MISS (1 lost), HIT 2, HIT 1 (natural 20) | OK: 18 - 4 - 2 - 4 = 8 |
| Flame Arrow, Lex preserver 10 | two casts, `Flame Arrow damage: 5d6 = [6 + 6 + 5 + 6 + 2] = 25`, then 11; no attack line | OK |
| Flame Arrow, preserver 15 | three bolts, 24, 18, 18 | OK |
| Flame Arrow, preserver 9 | one bolt, 15 | OK |

Afraid on an undead first read "(undead are immune; Bravery stops it)", the effect's usual words:
the dice log now says `turned, it flees (...)` for Afraid on an undead (tested in
test_dicelog's `test_turned_undead_flee`, not seen in DOSBox).

One D\* HP line came in between: `Arena Guard now 0/150 HP (-150)` before its "is destroyed by Turn
Undead" (the HP poll read that creature's fall before its turning's entry): the order of two
lines, nothing wrong in the game.

## Not done

- A turning out of a fight (it clears the failures, then starts the fight): only in the Unicorn test.
- Flame Arrow at preserver 4: a 4th-level preserver can't cast 3rd-level spells (the LEVEL button
  stays on 1); the least is 5, one bolt.
- A monster casting Minute Meteors or Flame Arrow: none of these foes has them. By the code
  (5A3BAh, 5AA39h ignore the cast's answer) a monster's cast lands once.

## Steps

- `loadsave.sh fountain-user`, `dismiss.sh`: Pehtucl's ambush, Lex's turn. `spellsetup.py 0=10 2=9
  hp=200 33 28`, `hp.py 150`, `turnsetup.py 3 1 25=5` (new tool: Seneca a fire cleric of that
  level, the Templar's sheet undead of 5 HD), then per case `turnsetup.py 3 4 42=1`, `3 8 24=1`,
  `1 6 25=1`; Lex's third class made cleric 6 by hand. The second run (`loadsave.sh fountain-user`
  again) `spellsetup.py 0=15 33 28`, `turnsetup.py 3 3 25=1`, later `spellsetup.py 0=9`.
- Turning: U, TURN UNDEAD (156,146, a slow press), a click on the figure (its feet's y less 12; the
  foes' places from DS:669Dh + 32n, the Templar and the Guards right this time). The Arena Guards
  stood at x 384-400 off the screen's right: `scroll.py -150 0` brought them on (in a fight; the
  aim showed a ring of beads, the range, and a click inside it at the group took four).
- Lex's first Minute Meteors try did nothing: "YOU WERE HIT" (an arrow before his turn), icons not
  crossed but no cast; the next round's worked.
- Nothing saved; the memory edits died with DOSBox.
