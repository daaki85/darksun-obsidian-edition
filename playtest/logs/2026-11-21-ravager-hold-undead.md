# Test log: Hold Undead's level, Wake of the Ravager (2026-11-21)

Under test: DSCLOG2's SITE 14, HOLD_HD (SL's hold_undead_level): Hold Undead (31) leaves an undead of
more levels (hit dice) than the cast's level immune, as the manual has it.

## Found first

- The sequel's spells' immunity routine is its own (8451Ah: DI the target combatant, SI the spell,
  [BP+14h] the cast's level; AX 1 immune via 84562h, 0 not at 84AAFh). Undead are the sheet's race
  (+12h) 9 (the Giant Skeletons: race 9, no class, 4 HD in the level byte +1Eh).
- The game's own Hold Undead holds only the undead: on a living Draxan it gave no save and no effect
  (SL's hold_undead bug, a hold on anything, isn't in the sequel).
- A first site at the routine's last test (84AA5h) never ran: only spell 120h gets there; every other
  spell leaves by 84A71h's "jmp 84AAFh". The site is now 84A65h ("mov ax,si / cmp ax,0FCh", where all
  spells not yet immune pass); immune is 84A62h's "jmp 84562h".

## In the game (ravhold.sh, RAV_LOADER=1, the dice log on, about 21:00-21:40 UTC)

Ar'anda taught Hold Undead (scratch hsetup.py), the party's HP 250, the Draxans' sheets made undead
(race 9: sheet 16, 8 levels; sheet 14, 10), Ar'anda's preserver level set to 7, then 10 (test edits;
DOSBox stopped after each run, nothing saved).

- **At level 7 on an 8-level undead Draxan**: the time line ("lasts 8 rounds (caster level 7 ...)"),
  then nothing: no saving throw, no effect entry; the helper's count 1 (HOLD_HD found it immune).
- **At level 10, the same kind**: "Draxan's saving throw vs Hold Undead from Ar'Anda (spell): d20 total
  13, needs 13 -> saved"; the count still 1. An earlier run with the first site (at level 10): saved
  failed, Paralyzed (69) put on.
- Aiming: the target shows red under the spell's pointer only on a foe's figure; a party member
  (yellow) can't be taken by a hold, and a figure behind another can't be picked.

## Still to do

- The dice log has no line for the immunity (SL's log says "too many hit dice"): it shows the time and
  then nothing.

Water: none new (the same street).
