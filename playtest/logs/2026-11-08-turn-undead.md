# Play test: Turn Undead, the game's rules and the dice log's new line (2026-11-08)

Under test: what the game's Turn Undead (spell 190, the cleric's USE-screen button) does, against
the code read in DSUN.EXE (7ADB7h), and the Loader's new dice-log line for it
(`dsloader/dicelog.py`: `TURN_ROLL_RETURN`, `_overlay_turn`, `_turn_undead`, `turn_needed`; the
1000 damage said as "is destroyed by Turn Undead"). Nothing in the game was changed.

## Setting

- DOSBox was already running `fountain-user` in Pehtucl's ambush, left by the session before
  (started 23:03, idle since 23:16, with that test's memory edits: the Guards' sheet made undead,
  `hp.py 150`, `spellsetup.py`). DOSBox is shared with another agent: every step below was under
  `flock /tmp/playtest/dosbox.lock` (a background holder, released at 23:50), and that DOSBox was
  not restarted (not started by this session). Its own Loader (`dsloader dicelog`, writing
  `dice.txt`) couldn't be stopped either (refused: not this session's process), so the new code ran
  beside it as a **read-only dice log**, `playtest/rolog.py` (new: describe() and hp_changes()
  only, no attach writes), into `$PLAYTEST_WORK/tu-rolog.txt`. `dice.txt` thus shows what the
  Loader printed before this change, `tu-rolog.txt` what it prints now.
- Ester (#2, fighter/fire cleric 3) was Paralyzed and Afraid, so her turns were skipped: Seneca
  (#3, thief/fighter) was made a fire cleric in memory (class +22h 3, level +25h, sheet +12h low
  nibble 4), later Lex (#0) too. Targets: the ambush's Guards (sheet 15, already race 9), a Templar
  made undead (sheet 10: race 9, HD at +24h), and the pens' real Zombie (creature 21, 2 HD).
  Everything was put back in memory afterwards; nothing saved.

## Results

| Case | Expected (code) | Seen | Verdict |
|---|---|---|---|
| Button for a cleric | shows when sheet +12h bits 0-3 (the cleric element) are set | Seneca with +12h 0424h: TURN UNDEAD (158,146) on the USE screen; in a fight alone, out of one beside the thief's purse | OK |
| Button for a druid | none: druids have 0 there | Seneca as a druid (class 6, +12h 0420h): only the purse | OK |
| Druid with the nibble set | the class isn't looked at | class 6 with +12h 0424h: the button back | the test is the element bits only |
| Cleric 3 vs 2 HD (Guard) | 10 + 3 x (2 - 3) = 7 | `Seneca turns Guard: d20 = 11, needs 7+ (priest level 3 vs 2 HD) -> destroyed`; old log: `Guard is killed`, the XP, then `Dice: 1d20 = [11] = 11` | OK, destroyed |
| Cleric 1 vs 4 HD (Templar) | 19 | `Seneca turns Templar: d20 = 2, needs 19+ (priest level 1 vs 4 HD) -> not turned`: HP 150 unchanged, no effect on it, Seneca's turn over | OK, failure does nothing |
| The same again, next round | (nothing kept) | round 14: `d20 = 14, needs 19+ ... -> not turned` | can be retried, same creature |
| "Level 0" (Lex, a non-cleric with the element bit) vs 4 HD | 10 + 12 = 22, made 20 | `Lex turns Templar: d20 = 3, needs 20+ (priest level 0 vs 4 HD) -> not turned` | the 22 -> 20 rule seen |
| Cleric 13 vs 8 HD (Lex) | column 9, row 12: 1, any roll | `Lex turns Templar: d20 = 5, needs 1+, any roll (priest level 13 vs 8 HD) -> destroyed`, and the fight was over (the last foe) | OK; level 13 counts as 14+ |
| A later fight, a real undead: Seneca (cleric 3) on the pens' Zombie, out of a fight | 7 | `Seneca turns Zombie: d20 = 20, needs 7+ (priest level 3 vs 2 HD) -> destroyed` / `  Zombie is destroyed by Turn Undead`; old log: `Zombie now 0/150 HP (-150)`, `Zombie is killed`, a Round 1 initiative, `Dice: 1d20 = [20] = 20` | OK: works out of a fight (starting one) and in a later one |

Uses: Seneca turned in rounds 12, 13, 14 of the ambush and again after it; nothing stopped him. The
button's description (RESOURCE.GFF SPIN 1000: "May be used once per creature") isn't kept to by
the game: no per-creature, per-fight or per-day mark, no slot (580:CFh readies it with the slot kind
FFh). Each use ends the turn.

The floating name over the caster read **"special attack 190"** (game.spell_name has no name for
190): the dice log's float now says "Turn Undead".

**What the Loader printed before**: only `Dice: 1d20 = [N] = N` (a pending roll flushed seconds
later, after the kill's lines), and the destruction as `Zombie now 0/150 HP (-150)` (or nothing but
`Guard is killed`).

## The overlay stub

Every Turn Undead roll seen came back through the overlay manager's INT 3Fh stub: the caller's code
read `cd3fb822a08b0700...`, not the `83c4043b46fa7c15...` after the d20 call (the dice routine's
overlay, 63240h on, loaded over the spells' one, 78BA0h). The frame was still the routine's:
`args [25, 3, -975, 1] [BP-6] 19 last cast (3, 190)`: target, caster, &flags, level, and the number
needed. `_overlay_turn` knows it by the last cast (190, from DSCLOG's CAST_SITE, which does see the
button's cast), the target undead and [BP-6] equal to the game's number for its HD and the level.
The first version took levels 1-40 only, and missed Lex's level-0 roll; now 0-40.

## Not done

- The figures of the party kept vanishing from the map (drawn again by I then Escape); clicks on
  them then missed, so `passuntil.sh` gave up and Lex walked a step. Not looked into (the DOSBox had
  been through another session's tests).
