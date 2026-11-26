# 2026-11-25: Psionic Blast's wounds and the quick saves joined in one build of the sequel's helper

**Under test:** branch `claude/ravager-join-blast-saves` (PR #174), the join of [Psionic Blast's wounds and
the combat log's L](2026-11-25-ravager-blast-log.md) and [the quick saves](2026-11-25-ravager-quick-saves.md),
each played alone before. DSCLOG2.EXE rebuilt from the joined source: **42512 bytes**. A smoke play: nothing new
built. Play 14:07-14:20 UTC, two throwaway copies, both deleted after; no save kept.

The build in place: DSCLOG2's segment in memory (CA1Bh, the INT F5h vector's, header `DSCLOGR1`) compared with
the load images over its first 24 KB: the joined file **23819** bytes alike (23842 in copy B, after the fight),
the quick-saves branch's (42400 bytes) 23808, the blast branch's (41856) 5987. The window the sequel's 640x480
(as every Ravager run).

## Copy A: quick save and quick load (no edits)

[The quick saves' start script](files/2026-11-25-ravager-quick-saves-start.sh) from this worktree: `ravQS`, a
fresh copy of `rav`, ravager-after-ambush through the Loader's start, the dice log.

- **Memory** (`dosmem.py`): DSCLOG2 **41984 bytes** in upper memory (MCB CA0Ah), **113472 free** after it in one
  piece (MCB D44Bh, the chain's Z: whole). The Tab/small-ports join had 41216 and 114240 (768 more now). DOS
  memory free after the game 73 KB (74432 bytes).
- After the load: keys 3F00 4300, counts 0, letters E E.
- **F5**: "Quick save" over the leader ([picture](img/2026-11-25-ravager-blastsaves-f5.png)), the dice log
  `Quick save: "Quick - Day 1, 00:04" (the QUICK page, slot 1)`, SAVQ01.SAV 51771 bytes, SAVE 6 **1224 bytes = 17
  x 48h**, GREQ 101 written.
- **F9**: the LOAD window on "Quick - Day 1, 00:04", letters Q Q
  ([picture](img/2026-11-25-ravager-blastsaves-f9.png)); **Return** loaded it: GREQ read 1, letters back E E.
- **L**: the combat log panel on the map ("Day 1, 00:05", L, Short, - +: [picture](img/2026-11-25-ravager-blastsaves-panel.png)).

## Copy B: Psionic Blast's wounds (test edits, no saving)

[The blast log's run script](files/2026-11-25-ravager-blast-log-run.sh) (tag J): `ravBL`, a fresh copy of
`ravK`, the transferred four, a new game to the Draxans' ambush, HP 250 for the four. **Quick saves and
autosave off** for the dice log (`QuickSave.keys` and `.auto` held False by a `sitecustomize.py` on PYTHONPATH:
`ravdice.py` doesn't read settings.json for them); seen: keys **FFFF FFFF**, and no SAVQ file in the copy at
any time.

- Test edits: Psionic Blast (power 31) given to Jenna (`ravkits.py power 3 31`); members 0-2 side 7 and their
  saves 30 (the blast log's `-side.py`, `-saves.py`; restored right after the cast). Jenna's turn: C, Telepath,
  the second icon, a click on Lex: `Lex#0's saving throw vs Psionic Blast from Jenna#3 (paralysis/poison/death):
  d20 = 18 +1 other = 19, needs 30 (5% to save) -> failed`, `Lex takes 200 from Psionic Blast, now 50/250 HP`;
  **BLAST_HP (200, 0, 0, 0)**.
- The Draxans' HP 3 (a test edit: the creature records whose +15h is 7, at creature indices 25, 26, 29 and 31,
  not the combatant numbers #21-27; `ravkits.py hp N` on the combatant numbers wrote other creatures and the
  Draxans' shared sheet's +8, the most, not their HP). The fight by [Tab and Enter](files/2026-11-25-ravager-blast-log-tabfight.sh).
- The fight's end: the level-ups (CHOOSE A SPELL for Lex, the first icon; with the HP 250 edit HP went negative,
  as in the blast log), the level messages clicked through, then **"Lex shakes off Psionic Blast's imagined
  wounds as the fight ends: +44 HP, now 44/44"** and "Fight over: 4 rounds"; BLAST_HP back to **(0, 0, 0, 0)**.
  L on the map showed both lines in the panel ([picture](img/2026-11-25-ravager-blastsaves-shake.png)). No
  autosave after the fight (the switch off).

## No Illegal Op, no quit

`STDOUT.TXT` empty in both copies, DOSBox up to the end of each, stopped by pid. The watchdog not run (both
copies watched step by step). No new area (Tyr's ambush street): no water.

Pictures for the docs: `/mnt/project-files/ravager/2026-11-25-ravager-blastsaves-f5.png`, `-f9.png`,
`-panel.png`, `-shake.png`.
