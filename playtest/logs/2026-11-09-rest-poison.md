# Rest and poison (2026-11-09): a 7th-level druid's free Neutralize Poison saved no one

Under test: the game's rest (DSUN.EXE 8066Dh, overlay 5E8h; see 2026-11-09-group-4-research.md §3).
Its pass 2 takes each member's effects as a bitset (76944h, at 8075Dh) *before* the free cures
(807E7h: Neutralize Poison when the best Okay druid is 7th level or more), then kills the Poisoned
(1000 damage, 80963h) from that copy. The proposed fix (cures first, a reorder of 80765h-807ECh and
the loop's jump at 80984h) is in the session's scratchpad, rest-poison.md; not in the mod yet.

## Setup

`loadsave.sh pens-fire-count4` (party in the fire room, 1896,872, camera 1728,768; the ring at
1931,856, screen 203,88). In memory (never saved): `spellsetup.py 1=7` (K'ratchek, a fire druid,
class 7, to level 7), `addeffect.py 0 35 119` (Gerakis Poisoned, an untimed record of the spell
Poison). `pointer.py look`, a slow press on the ring. HP and status (creature +0, +1Ch) read after.

## Results

| Run | Code | Druid | Dice log | Gerakis after |
|---|---|---|---|---|
| A | game's | 7th | THE PARTY RESTS / Poisoned ends on Gerakis / Gerakis now 0/54 HP (-21) | **status 5 (dead)**, effect gone |
| C | fixed (in memory) | 7th | THE PARTY RESTS / Poisoned ends on Gerakis | **status 1, 54/54 HP** |
| D | fixed (in memory) | 2nd | THE PARTY RESTS / Gerakis now 12/54 HP (-42) | status 5 (dead), **Poisoned still on him** |

(The later "+12" in A is CON 22 regeneration of the 8 hours, on a dead creature; D's -42 is the same
death seen after it.) D shows death doesn't take the effect off, so A's "Poisoned ends" was the
druid's cast, made before the kill read its stale bit: the cure is cast and the member dies anyway.
In C the reordered pass reads the effects after the cure and the member lives.

Static: spell 118's record has effect byte DDh (-35, Poisoned removed), Poison (119) 23h (+35), Cure
Disease F3h (-13).

## Tools and notes

- `addeffect.py OWNER EFFECT [SPELL] [CHARGES]` (new): an effect record put into the game's table in
  owner order (the game finds an owner's records by a binary search, 76A99h); `del OWNER EFFECT`.
- `restfixmem.py [check|fix|undo]` (new): finds the rest's pass 2 in the overlay buffer and swaps
  the game's bytes for the fix's. Rest once first so the overlay is loaded; it was at DDD95h, then
  moved to DD655h by the overlay manager with the fix's bytes kept.
- Resting three times in pens-fire-count4 brought no call from Kurzak within the run.
- No watchdog was run (short, scripted steps, each with a timeout); the DOSBox lock was held
  throughout.
