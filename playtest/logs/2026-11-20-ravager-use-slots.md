# Test log: spell slots on the USE screen, Wake of the Ravager (2026-11-20)

Under test: DSCLOG2's PROBE_USE / PROBE_WIN (patches `use` 79543h, `window` 303BEh) drawing the
Loader's spell slot lines (RavDiceLog._write_slots into SLOTS_TEXT) on the sequel's USE screen.

## 1. ravager-after-ambush (23:05 UTC)

- Loaded with `ravload.sh` (the Loader's copy, the new DSCLOG2), `ravdice.py` attached.
- USE (the top-left icon) for Ar'anda: the panel reads SPELLS LEFT / WIZ 1/3 under the spells. LEVEL
  2: WIZ 2/2; LEVEL 3: WIZ 2/2 (each redrawn as the level changes: PROBE_USE).
- Terrannus made leader, then his portrait clicked: the screen turns to him, CLERIC, LEVEL 1: SPELLS
  LEFT / PRI 7/7 (redrawn by PROBE_WIN as the character changes).
- The helper's lines for all four: Ar'anda WIZ 1/3 2/2 2/2; Terrannus PRI 7/7 6/6 4/4 2/2; Thy'rokh
  PRI 6/7 4/6 3/4 1/2; the gladiator none. The game's counts left match its own memory.
- Found on the way: the sequel's slot routine (626B7h) is SL's but for its test switch (a byte at
  DS:13F8h, SL's word at 1164h, which in the sequel holds 4748h) and which classes cast (asked of a
  routine at 62B45h: wizard 11 and 18, priest 1-8, 13-16 and 19). The Loader's numbers now use both.

## 2. ravager-roost, a rest at the inn (23:15 UTC)

- The new Loader code (the sequel's slot routine's switch and classes) with `ravdice.py`.
- Before: Ar'anda WIZ 0/3 1/2 0/2; Terrannus PRI 7/7 6/6 4/4 2/2; Thy'rokh PRI 6/7 4/6 3/4 1/2.
- The inn's route (RESEARCH.md): Reyhan, 1 3 4, Space, Left 4, Down 9, Right 14; the second doorway's
  steps were at game (253, 90) this time (the guide says 270, 104: the view differs a little), Up 6,
  the look pointer on the ring at game (268, 126). The party rested.
- After: every count left equals the Loader's most: Ar'anda WIZ 3/3 2/2 2/2, Terrannus and Thy'rokh
  PRI 7/7 6/6 4/4 2/2 (the game's own memory: no slot at any level the lines don't show). So the
  most, worked out from the sequel's tables, is what its own rest gives.
- USE: Ar'anda MAGE LEVEL 1, SPELLS LEFT / WIZ 3/3; PSIONIC, nothing drawn (as SL's).
- Armor cast from USE on Ar'anda (the icon dragged to her portrait): the panel at once WIZ 2/3.
- Nothing saved; DOSBox and the dice log stopped by pid.

Result: spell slots on USE work in the sequel as in Shattered Lands.
