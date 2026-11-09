# Audit fixes: DOSBox checks (2026-11-09)

Under test: `dos/DSCLOG.EXE` rebuilt from the audit's fixes (the per-fight tables SWEPT, TU_FAILED and
DJ_DONE over every combatant up to MAP_COUNT, 520, in the far block: FAR_TU at FD10h, FAR_SWEPT at
FF18h, FAR_DJ at FF59h, linear FFFF0h + offset in the HMA) and the Loader's panel reading the spell
to-hit line (combatlog.py). Memory edits only; nothing saved; DOSBox killed afterwards.

## Build in place

`loadsave.sh fountain-user`, then `buildcheck.py` (OK: 134 vectors at their handlers, the tail as the
EXE) and `buildcheck.py tu_site tu_bit swept_mark map_bit probe_move djinn_turn acid_round th_hit`:
all eight routines the same as the EXE.

## Fix 1: Turn Undead's failure remembered in the far block, the retry refused

- `fountain-user`'s combatants are all under 64 (0-3, 17-47). `pens-after-scar` has many past 64 out
  of a fight (Kalzith 220, guards 256-290, Mirlon 317): `/tmp/playtest/combpos.py` (thing, creature,
  name, map place).
- From `pens-after-scar`: walkto (1816,408), (1704,408), (1592,440); the guards west of Kurzak's stop
  (256, 260, 287, 289, 290) are behind a wall: Turn Undead at them said "no line of sight".
  `route.py 1592 584`, `route.py 1560 860` into Kalzith's pen (he at 1576,888).
- `turnsetup.py 1 1 220=5`: K'ratchek a level-1 cleric (second class), Kalzith's sheet (12, shared
  with Dinos, Gilal, Mirlon) undead of 5 HD: 20 needed.
- Out of a fight: U, K'ratchek's portrait (112,62), TURN UNDEAD (158,146, slow press), the aiming box,
  a click at (196,146): `K'ratchek turns ?: d20 = 10, needs 20+ ... -> not turned` and the fight
  began. **The fight renumbered the combatants**: at Round 1 the map's things past the party moved to
  21-47 (Kalzith 42, Mirlon 21, the guards 26-40), so no combatant past 64 was left in the fight. The
  out-of-fight line's "?" is that: the dice log named combatant 220 after it had become another
  number. (Round 1 clears TU_FAILED anyway, as before: a turning that starts a fight starts afresh.)
- In the fight, K'ratchek's turn: `K'ratchek turns Kalzith: d20 = 17, needs 20+ ... -> not turned:
  can't try again on it this fight`. The far block then read TU_FAILED byte 42 = 2 (priest 1's bit),
  nothing else set (`/tmp/playtest/fartu.py`: SWEPT and DJ_DONE all 0).
- Rounds 2 and 3, the same: `K'ratchek can't turn Kalzith again: failed against it this fight` (no
  roll; the turn ended).
- A combatant past 64 in a fight wasn't found: the unit tests cover 64, 300, 519 and 520 (Turn
  Undead, Whirlwind's SWEPT through ACID_ONCE and PROBE_MOVE, the Djinn's first turn).

## Fix 2: the spell to-hit line in the panel's Short level

- Cermak (member 2) taught Minute Meteors at preserver 10 (`spellsetup.py 2=10 33`); Kalzith's sheet
  base AC (+27h) -3 for a miss, then 10.
- The panel (L) came up expanded at Detail (settings.json's `combat_log_level`); a click on the
  expanded panel's chip (292,74) docked it; the docked chip (268,129) cycles Detail -> Least -> Short.
- Five casts (U, LEVEL 196,171 twice to page 3, the icon 176,59, Kalzith at 194,142, then four more
  clicks 4 s apart): three MISS (18 vs 20+, 4 vs 7+, natural 1), two HIT, each "Kalzith takes N from
  Minute Meteors, now X/16 HP".
- At Short (img/2026-11-09-audit-short-spell-misses.png, -hits.png): `Cermak's Minute Meteors misses
  Kalzith (4 vs 7+)` in the miss colour (grey), `Cermak's Minute Meteors hits Kalzith for 2 (8 vs 7+)`
  in the hit colour (#A2A27D, the nearest the pens' palette has to the hit green), its damage joined,
  then `Kalzith now 11/16 HP`. At Least (img/2026-11-09-audit-turn-refused-least.png) the Turn Undead
  refusal in the miss colour.
