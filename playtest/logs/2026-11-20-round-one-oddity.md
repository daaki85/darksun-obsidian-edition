# 2026-11-20: the "Round 1" heading at the whole party's clock jump

Build: claude/round-one-oddity = origin/obsidian-edition 346e72e (2.19.2 + #131). DOSBox 0.74-3,
320x240, buildcheck.py OK. settings.json autosave false, quick_save false before loadsave.sh.
Save fountain-user, `dismiss.sh` into Pehtucl's ambush. **The oddity** ([the last
play](2026-11-20-paralyzed-ends-oddity.md), run B): with the whole party Paralyzed (Rainbow
Pattern) the clock seemed to jump from 3326 to 3806, and the dice log printed a `Round 1` heading
listing about 50 combatants, most of them `?`.

## The answer

**The game plays the rounds; the log merged them.** With no one in the fight able to act, the
game runs round after round in a blink (60 s on the clock and every combatant's initiative rolled
each round, every turn skipped), so no jump and nothing reset or half-written. The dice log shows
a round's order 0.3 s after its last initiative roll, or at the next other roll: here no other roll
came for six rounds, so it put 60 pairs (10 combatants x 6 rounds) under one heading. It names
each roll by its tie-break in the game's table, which holds only the last round's: the rest were
`?`. And it numbered the heading by the clock, 420 s since the last heading, past its 120 s
fight gap: a new fight's `Round 1` (a dance rolled again, the foes' ACs forgotten), and the
next rounds counted 2, 3... instead of 9, 10.

**Fixed in the dice log** (`initiative_lines`, `_rounds_passed`, `_round_number`): the last
round is the run of rolls at the end whose tie-breaks are those of combatants in rising order
(the game rolls in that order); when the rolls are whole rounds of that many and the clock has
moved a round for each, the earlier ones are counted, not listed: `Rounds 4-5 go by at once: no one
in the fight can act`, then `Round 6: ...` with the last round's ten names. The round count goes
on through them (no new fight), and a dance's rounds run out in them too. Two tests; the suite
with `-W error` 2,194 tests, OK both ways (57 skipped plain, none with the game's files).
Watched in game (run 3 below).

## Run 1: reproduced (2.19.2 + #131's dice log)

dismiss.sh into Pehtucl's ambush; foeset.py C eff=34 on 17-47 (not 41, 44: 29 held);
spellsetup.py 0=9 2=9 50. The dice log run through a scratch wrapper (tracewrap.py) writing every
initiative roll and, at each heading, the pairs, the clock and the initiative table; a watcher
(r1watch.py) on the clock, whose turn, the party's effects, the kind-7 events and the table, every
20 ms.

- Lex, round 1: Rainbow Pattern at the floor among the party (158,148): `2d3 = 5`; Lex failed,
  Templar replaced in place; Ester failed at her turn's start; Jenna failed; round 2 Seneca failed.
- The whole party Paralyzed, the foes held. The watcher: the clock 3324 -> 3384 -> 3444 ... -> 3744
  **in 60-second steps, all within 0.1 s** (796.81-796.91); the effects due at 3744 then ended.
  Not one jump: the game played rounds 3-8 one by one, each skipping every turn.
- The trace: 60 initiative pairs in a row (seq 93-212), 10 a round (the 10 in the fight), nothing
  else rolled between them, under the 0.3 s the log waits. One heading:
  `Round 1: Seneca 33, Lex 33, ? 29, ? 29, ... ? 20` (60 names, 50 of them `?`). The table at that
  moment held only the last round's tie-breaks (and every score -1: the turns passed). Then
  `Round 2`, `Round 3`... for the game's rounds 9, 10, 11; and Ester's dance rolled again (the log
  took it for a new fight: 3744 - 3324 = 420 s > FIGHT_GAP 120).

## The cause, in the game's code

DSUN.EXE 57414h is a round's start: `add dword [es:35Bh],3Ch` (60 seconds on the clock), the
events due (call D0:348h), then for every combatant DI = 0, 1, 2 ... (57447h-5764Dh) in the fight
(kind 2, creature +1Ch 1, +1Dh & 3, a member also by 6CC0h) the 0-9 roll (574DEh) and the 0-199
roll (57520h), the score and the tie-break stored at once (5751Bh, 57545h: 37BD:00D9h + creature x
4); the others get score -1. Nothing reset or rebuilt: with no one able to act every turn is
skipped and the next round starts at once. The dice log groups the initiative rolls until 0.3 s
pass or another roll comes; here no other roll came, so several rounds' pairs became one heading,
matched against a table holding only the last round's tie-breaks (the "?"), and the clock's 420 s
since the last heading read as a new fight (FIGHT_GAP 120): "Round 1", Ester's dance rolled again,
the foes' ACs and the Poisoner's doses forgotten.

## Run 2: the fix's first version (2.19.2 + the split, the clock check (passed + 1) x 60)

loadsave.sh again, the same setup; Ester's turn first, passuntil.sh 0; Lex's Rainbow Pattern at
(158,148), `2d3 = 4`: Ester failed. Passes: Seneca failed (round 4), then:

```
Rounds 5-7 go by at once: no one in the fight can act
Round 8: Lex 33, Jenna 30, Templar 28, ...            (10 names, none "?")
Paralyzed ends on Ester, Templar
Round 9: Lex 31, Jenna 31, ..., ? 28, ? 28, ...       (20 names: not split)
```

The second batch held rounds 9 and 10 (3684, 3744), but the last heading's clock was already 3684
(read once round 9's 60 s were on, before its rolls), so the check wanted 120 s and saw 60. Fixed:
the clock must be on at least a round for each round passed (`passed x 60`). Replayed on the
three batches seen (the traces' pairs and tables): 60 pairs -> 5 rounds passed, 40 -> 3, 20 -> 1.

## Run 3: the fix as committed (the Loader's own dice log, no wrapper)

`loadsave.sh fountain-user`, the foes held, `spellsetup.py 0=9 2=9 50`, the watcher. Lex's Rainbow
Pattern at (158,148) in round 1 (Ester failed), a second at (150,152) in round 2; Seneca, Jenna and
Lex failed at their turns' starts (round 3, clock 3324). The dice log as written:

```
Round 3: Arena Guard 31, Lex 31, Arena Guard 31, Arena Guard 30, Guard 29, Seneca 29, ...
Lex's saving throw vs Rainbow Pattern (spell): d20 = 9 +1 Ring of Protection -1 WIS 6 = 9, needs 12 (45% to save) -> failed
Paralyzed on Lex: loses its turns, can't move, fails every saving throw
Lex's turn
Rounds 4-5 go by at once: no one in the fight can act
Round 6: Seneca 33, Lex 33, Ester 31, Templar 31, Guard 29, Arena Guard 28, ...   (10 names)
Round 7: Lex 33, Jenna 30, Arena Guard 30, Arena Guard 29, Seneca 27, ...           (10 names)
Lex's turn
Paralyzed ends on Ester, Templar
Rounds 8-9 go by at once: no one in the fight can act
Round 10: Ester 33, Seneca 33, Arena Guard 30, Arena Guard 30, Lex 30, ...
Ester's turn
Templar's turn
Templar attacks Jenna with Obsidian Bloodwrath +1 (1d8+1): d20 = 2, needs 14+ (35%), hits AC 15, target AC 3 -> HIT
```

The watcher's clock: 3324 (round 3), 3444, 3504, 3564 within 0.04 s, a pause of 1.2 s, 3624,
then 3744 (round 10) with Ester's and the Templar's holds ended: round N = 3204 + 60 (N - 1)
throughout, so the numbers are the game's. No `?`, no `Round 1`, Ester's dance not rolled again.
(Round 7 came alone, after the 1.2 s pause, as an ordinary heading.)

**The panel**: `panel.sh show` after the fight went on: header `Round 11: Ester...`, `ROUND 11`
in the well. It shows the same lines: in 2.19.2 it had `ROUND 1`, in detail the 60 names, and the
header's "then ?, ?, ..." (round_status lists every row of the order, the `?` ones never acting).
Now a `Rounds 4-5 go by ...` line in the well (a `Round 6 goes by ...` line is drawn as the
`ROUND 6` rule with the rest under it).

## Real play

The batch needs several rounds in a row with **no roll at all but initiative** (any other roll
ends the wait and the heading comes out round by round), within 0.3 s each: everyone in the fight
unable to act. The whole party held is not enough: a free foe's attack rolls dice. So real play
needs the party and every foe held, asleep or out of the fight at once: Rainbow Pattern's area
over everybody, or the party held while the foes are held by the party's own Hold Person or Rainbow
Pattern. Uncommon, but no memory edit is needed: the rounds pass the same way.

## Stopped

DOSBox, the dice log, the watcher and the watchdog stopped by pid, the lock released. Nothing
saved: the `SAVQ*` files are 2026-11-19's; `SAVE01.SAV`, `CHARSAVE.GFF`, `DARKSAVE.GFF` 17:24 are
loadsave.sh's copies. Water: none new (`fountain-user`).
