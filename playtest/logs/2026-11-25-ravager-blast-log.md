# Test log 2026-11-25: Psionic Blast's wounds, the save's d20, RL_TRY, the combat log's drag (Wake of the Ravager)

Build: branch claude/ravager-blast-log (worktree /home/claude/wt-blast): DSCLOG2 sites 79 BLAST_LOSS (6662Dh),
80 BLAST_KO (5CC51h), 81 RL_TRY (6C585h); header +280/+282 RL_SEQ/RL_TRIES, +1814 BLAST_HP. DSCLOG2.EXE 41856 bytes.
Loader: RavDiceLog._blast_pass, _creation_pass, _is_save_roll (the sequel's [BP-0Ah] frame).
Game copy: ravBL (fresh copy of ravK each run), run script logs/files/2026-11-25-ravager-blast-log-run.sh.

## Run B (rules on), the Draxans' ambush
- Psionic Blast on an ally: the game refuses a party member as the target (the pointer lights the figure yellow, no
  cast). Test edits (never saved): the target's side (+15h) 7 (the Draxans'), its sheet's five saves (+30h) 30, the
  caster's own byte for power 31 at selector 370h (load + 3E71h):9CDh + member x 22h (`ravkits.py power`).
- A blast costs 10 PSP on a passed power check, 5 on a failed one (three failed, no line: the power check isn't in the
  sequel's dice log).
- Ester's blast on Seneca (saves as they were): "Seneca#1's saving throw vs Psionic Blast from Ester#2
  (paralysis/poison/death): d20 = 9 +9 other = 18, needs 9 (95% to save) -> saved" (the natural d20 now shown).
- Jenna's blast on Seneca (saves 30): "d20 = 13 +9 other = 22, needs 30 (5% to save) -> failed", "Seneca takes 152
  from Psionic Blast, now 50/250 HP": BLAST_HP (0, 152, 0, 0), blast_seen 1.
- Then Seneca's HP 1 (test edit): a Draxan's blow of 11 or more would kill.
- Draxans' HP made 15 (test edit) to reach the fight's end; the party fights by Tab and Enter (/tmp/claude-0/tabfight.sh; ravfight.py fight never reached the Draxans in the building).
- Run B ended in YOUR PARTY HAS BEEN DEFEATED (the Draxans' HP edit came late; ravfight.py fight never reached
  them in the building): no fight's end. The knock-out was seen before that: Seneca at 1 HP (test edit) with 152 owed,
  a Draxan's 13: "Seneca now 0/250 HP (-1)", status 3 (Out Cold), blast_kos 1. (Ester, owed nothing, later died: status 7.)

## Run B2 (rules on)
- Seneca's blast on Ester (Ester's and Jenna's side 7, saves 30; the target spot of members 2 and 3): "Ester#2's
  saving throw vs Psionic Blast from Seneca#1 (paralysis/poison/death): d20 = 18 +4 other = 22, needs 30 (5% to
  save) -> failed", "Ester takes 200 from Psionic Blast, now 50/250 HP": BLAST_HP (0, 0, 200, 0).
- Edits restored; Ester HP 1, the Draxans 20 HP (test edits). Tab and Enter each party turn (the loop needs Q then
  E to end a turn: Q alone leaves the END MOVE menu up). Ester wasn't hit before the end.
- The fight's end: level-ups (CHOOSE A SPELL for Lex; with the HP 250 edit each level-up made HP negative, e.g.
  "Ester now -219/30 HP": the sequel's level-up takes the most's change off the hit points, a test-edit artefact),
  then "Ester shakes off Psionic Blast's imagined wounds as the fight ends: +39 HP, now 39/39" (her most after the
  level-ups), BLAST_HP back to (0, 0, 0, 0).
- **The combat log panel never showed** (L counted by DSCLOG2, PANEL_KEYS 1 then 2, PANEL_ON stayed 0): DiceLog._map_up
  reads SL's DS:0BC9h (the map up), which in the sequel holds 0A2Eh; the sequel's is DS:0DABh (1 on the map; hover's
  ON_MAP already mapped). Mapped in RAV_TARGETING (quicksave.SCREEN_IS); a new dice log on the same game: L shows the
  panel ("Day 1, 00:15", L, Short, - +).

## The creation screen's tries (RL_TRY, row 26), logs/files/2026-11-25-ravager-blast-log-creation.sh
- R (ravBLC, a copy of rav; CREATE CHARACTERS, NEW, ravcreation.py 8 rolls): RL_SEQ 1176 after 8 rolls (147 4d4 a
  roll as the die tumbles). Every roll gave its six lines, e.g. "Character creation, DEX 16: best of four 4d4 (8, 12,
  9, 10) = 12, +4 = 16" and "the six scores add up to 102". A 7th-level fighter's STR came out "STR 17 (its rolls came
  too fast to record)" 6 times in 8: the sequel keeps the game's own least (a class's prime requisite 17), not SL's
  least_scores table; RavDiceLog now says "raised to 17 (the classes' least)".
- R2 (the raise line): "Character creation, STR 17: best of four 4d4 (11, 12, 12, 8) = 12, +4 = 16, raised to 17 (the
  classes' least)" (3 rolls seen, the other lines as in R). Picture: 2026-11-25-ravager-creation-tries.png.
- Control C (RAV_SKIP=rl_try): RL_SEQ 0, RL_TRIES all 0, no "Character creation" line in 8 rolls. ravcreation.py's
  hit point checks: 0 wrong in each run.

## Run C (control: RAV_SKIP=psionic_blast,blast_knockout; the copy's bytes at 6662Dh and 5CC51h the game's)
- Ester's blast on Lex (sides 7, saves 30): "Lex#0's saving throw vs Psionic Blast from Ester#2 (paralysis/poison/
  death): d20 = 3 +1 other = 4, needs 30 (5% to save) -> failed", "Lex takes 200 from Psionic Blast, now 50/250 HP";
  BLAST_HP stayed (0, 0, 0, 0), blast_seen 0.
- Lex at 1 HP (test edit), a Draxan's 12: "Lex now 0/250 HP (-1)", status 7 (dead), where B's Seneca was knocked out.
- "Fight over: 14 rounds" and no "shakes off" line.
- **The combat log panel's scrollbar drag** (this run, the panel shown with L in the fight): the pointer on the handle
  at game (308,186), the button held (xdotool mousedown), moved up 72 pixels in 12 steps, released: DSCLOG2's words
  PANEL_HELD 1, PANEL_HITS 1, the press at (308,185), the pointer at (308,149) while held; the log went back to
  ROUND 1's first lines with the "Latest" chip under it, and stayed there after the release. Picture:
  2026-11-25-ravager-panel-drag.png (before, held, after). The mouse wheel can't be played here: DOSBox 0.74 never
  passes it on and wheel.py's hook is Windows' alone; RavDiceLog runs SL's _panel_input, which takes it there.

No Illegal Op (STDOUT.TXT empty), DOSBox up to the end of each run. Window the sequel's 640x480 (as every
Ravager run). Not run: the watchdog (the fights watched turn by turn). No new area (Tyr's ambush street and the
creation screen): no water.
