# Test log 2026-11-25: the save modifiers and the THAC0 line in the sequel's dice log, the cahulaks' heads (Wake of the Ravager)

Build: branch claude/ravager-save-mods (worktree /home/claude/wt-ravager-save-mods), commit c97e091: RavGameData.save_modifiers
(the sequel's 628h:A7h, 83606h, with DSCLOG2's PROT_SAVE, KIT_SAVE, BLUR_SAVE, FSHIELD_SAVE and CON_SAVE in it), the THAC0
line from the sequel's set-up locals (5C5E1h: [BP-1Eh], [BP-8], bytes [BP-19h] and [BP-21h]) and its to-hit routine (628h:66h,
8599Eh), a nauseated attacker's -2 after the set-up, the difficulty at DS:143Ah. No DSCLOG2 change (no sites, no header
fields): DSCLOG2.EXE as on the branch.
Control: the commit before (64f5862) checked out at /tmp/claude-0/sm/base, its ravdice.py attached to the same game: the same
rolls with the old lines.
Game copy: ravSV (fresh copy of ravK each run), run script logs/files/2026-11-25-ravager-save-mods-run.sh.
Then (commit 23adce2 and after): the sequel's spell records read past SL's 255 (Psionic Blast is 266), and DSCLOG2's
PROBE_TWO taking `kit_two` for the cahulaks too (DSCLOG2.EXE 45168 -> 45184 bytes); `ravdice.py RAV_FRAMES=1`.
Area: Tyr's street, the Draxans' ambush only (no new area, no water seen).

## Run A: the new dice log and the old one on the same game

`sh logs/files/2026-11-25-ravager-save-mods-run.sh A /tmp/claude-0/sm/base`, then
`TAG=A sh logs/files/2026-11-25-ravager-save-mods-tabfight.sh 900` to the fight's end.

- Attack lines: the new log broke 247 of 250 attack lines down by name, the old one none ("THAC0 N base, +M in bonuses").
  The same swings, side by side:
  - old `THAC0 14 base, +4 in bonuses = 10`; new `THAC0 13, +3 STR, -2 stone, +2 difficulty = 10` (a Draxan's Stone Lotulis);
  - old `... in bonuses, +1 specialized = 15`; new `THAC0 19, +2 STR, +1 weapon, +1 specialized = 15` (Seneca's +1 weapon).
- The three left were Ester's swings in round 1 (see run C).
- Save: `Draxan#21's saving throw vs Psionic Blast from Jenna#3 (paralysis/poison/death): d20 = 8 +2 other = 10` in
  both logs. The new log was still "other" because `spell_record` returned nothing for spells numbered 256 or more
  (SL's table ends at 255; Psionic Blast is 266). Fixed (`RavGameData.spell_record`, `spell_rules`), dice log restarted
  ("--- restarted ---" in the log). The fight ended in level-ups.

## Run B: the set-up's locals (`RAV_FRAMES=1`), the old DSCLOG2 (the control for run C)

Test edits (never saved): Ester's item 32 made type 24 (Cahulaks) with `...-type.py 32 24`, her DEX 22 -> 12
(`...-ability.py 2 1 12`), Psionic Blast given to Jenna (`ravkits.py power 3 31`).

- Each THAC0 line followed by `[set-up: THAC0, bonus, rear, backstab, ready; type, mode, skill, after]`.
- Ester, a Battle Dancer in light armour, round 1 with the cahulaks: bonus -3 (bone -1, head -2). The dice log follows SL
  (no two-weapon penalty for a Battle Dancer in light armour), so the line fell back to "in bonuses". DSCLOG2's PROBE_TWO
  went to `cah_adjust` for the cahulaks without asking `kit_two`, unlike SL's DSCLOG. Fixed: the cahulaks' branch now
  takes `two_base` -2 and `kit_two` first (a Ghetto Fighter 2 better, a Twin-blade or Battle Dancer in light armour none);
  `cah_adjust` uses `two_base` and `two_base - 2`.
- Jenna's psionics showed every icon crossed and said CAN'T START THAT PSIONIC while a Draxan stood beside her ("Jenna
  can't hide in shadows: Draxan is right beside them"); with no foe beside her (run C) the icons were whole and the blast
  went off. The PSP shown on the USE panel is read when it opens (close it and open it again after `ravkits.py power`).

## Run C: the new DSCLOG2, a party member's save, the cahulaks' heads

`RAV_FRAMES=1 sh logs/files/2026-11-25-ravager-save-mods-run.sh C` (DSCLOG2.EXE 45184 bytes).

- `dosmem.py`: DSCLOG2 44656 bytes in upper memory, 110944 free after it (the largest 110800).
- Ester with cahulaks (type 24, DEX 22, Battle Dancer): `THAC0 19, +3 STR, -1 bone, +1 Battle Dancer = 16  [set-up: ...
  bonus -1 ...]`: no head penalty, the line broken down. The control (run B's old build): -3.
- Jenna's Psionic Blast at Lex (his side made 7 for the cast with `logs/files/2026-11-25-ravager-blast-log-side.py 0 7`,
  0 again after): `Lex#0's saving throw vs Psionic Blast from Jenna#3 (paralysis/poison/death): d20 = 13 +1 Ring of
  Protection -1 WIS 6 +1 CON 19 = 14, needs 13 (45% to save) -> saved`. In the old log this was "+1 other".
- Cahulaks for Seneca (item 17, `...-type.py 17 24`, DEX 12) and Lex (item 8, DEX 12):
  - `THAC0 19, +2 STR, +1 weapon, -2 cahulaks, main head at DEX 12 = 18`, `... -4 cahulaks, off head at DEX 12 = 20` (Seneca);
  - `THAC0 18, +3 STR, -1 bone, -2 cahulaks, main head at DEX 12 = 18`, `... -4 cahulaks, off head at DEX 12 = 20` (Lex);
  - Seneca's other hand: `-4 two weapons, off hand at DEX 12`.
- From round 2 the heads cost nothing: the DEX edits had gone back to the sheet's (21, 22) at the round's turn, and the
  lines agree (`THAC0 18, +3 STR, -1 bone = 16`). An ability edit on the creature lasts a round; edit the sheet for longer.
- One line still falls back: a Battle Dancer's first swing in the round she starts to dance (`THAC0 19 base, +1 in
  bonuses, +1 specialized = 17`, `after [('Battle Dancer', 1)]`). The game's THAC0 lacks the dance's +1, which the log
  already counts. This is the dance's timing (the Python side starts the dance), not the save or head lines: left as it is.
- 16 rounds, no Illegal Op. Picture: `img/2026-11-25-ravager-save-mods-cahulaks.png` (the end), and
  `img/2026-11-25-ravager-save-mods-blast.png` (Jenna aiming the blast).

## Not seen in play

- A foe's Psionic Blast save with the fix (run A's was before it): the WIS part comes from the same code as Lex's.
- Chaos, Cloudkill, Dismissal and Scare: left to the save line's existing handling.
- Cahulak users in the sequel's data are all in later areas (OBJEX 153 Weaponer, 203 a Draxan, 320 Salesperson,
  438 Tantris, 514 and 516 Gladiators: in Limbo, RGN0FF, and Gladiator2 in the Pyramid, RGN034), so the heads were
  played by a test edit.

Tests: `pytest -q` 2681 passed, 89 skipped; `unittest discover -s tests` 2503 OK (skipped 120).
