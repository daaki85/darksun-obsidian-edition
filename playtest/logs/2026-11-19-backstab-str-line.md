# 2026-11-19: Seneca's later attacks after a backstab (the "-2 STR" line)

Branch `claude/backstab-str-line`. Under test: the odd line of
[2026-11-19-free-dsclog-room.md](2026-11-19-free-dsclog-room.md) part 1, a later attack in the same
round as Seneca's backstab reading `THAC0 19, +2 from behind, -2 STR, +1 weapon, +1 specialized = 17`
(her STR 18 gives +2: the game's STR table at DS:7C2h reads 1, 2, 3 for 17, 18, 19). First
origin/obsidian-edition's DSCLOG, then the fix (`REAR_FRESH`).

## Set-up

- Lock taken (`flock /tmp/playtest/dosbox.lock`, held by a background loop), `loadsave.sh
  fountain-user`: window 320x240, `buildcheck.py` OK, watchdog on (`guard_start.sh`).
- Each try: `dismiss.sh`, every foe Paralyzed (`foeset.py C eff=34`), `panel.sh hide`,
  `passuntil.sh 3` (Seneca's turn), the Templar (combatant 25) freed (`addeffect.py del 25 34`),
  Tab + Return. Seneca has the Bone Hayneedle +1 in the left hand and Shadowseeker +1 in the right;
  her round is the Hayneedle's swing first, then one or two Shadowseeker swings (3/2 + two weapons).
- A frame log beside the Loader's: `rolog.py` copied to the scratch folder, printing for each
  attack line the attack routine's locals (`e.parent_local`: [BP-8], [BP-16h], [BP-18h], [BP-1Ah]
  from behind, [BP-1Ch], [BP-20h] the THAC0 before [BP-8], [BP-22h] the attack's number in the call,
  [BP-24h] the backstab).

## 1. The bug, reproduced (the old build)

Seneca hidden and unheard (`their next attack this turn is from behind`), the round's three swings
at the Templar:

```
Seneca attacks Templar BACKSTAB with Bone Hayneedle +1 (1d4+1): d20 = 19, needs 7+ (70%), hits AC -7, target AC 5 -> HIT
    THAC0 19, +2 from behind, +2 backstab, +2 STR, +1 weapon = 12
  [attack] frame {'-8h': 1, '-16h': 2, '-18h': 7, '-1Ah': 1, '-1Ch': 0, '-20h': 13, '-22h': 0, '-24h': 1}
Seneca attacks Templar from behind with Shadowseeker +1 (1d6+1): d20 = 12, needs 12+ (45%), hits AC 5, target AC 5 -> HIT
    THAC0 19, +2 from behind, -2 STR, +1 weapon, +1 specialized = 17
  [attack] frame {'-8h': 1, '-16h': 2, '-18h': 8, '-1Ah': 1, '-1Ch': 0, '-20h': 19, '-22h': 1, '-24h': 0}
Seneca attacks Templar from behind with Shadowseeker +1 (1d6+1): d20 = 1 (natural 1), needs 12+ (45%), hits AC 16, target AC 5 -> miss
    THAC0 19, +2 from behind, -2 STR, +1 weapon, +1 specialized = 17
  [attack] frame {... '-1Ah': 1, '-20h': 19, '-22h': 1, '-24h': 0}
```

The second and third swings' [BP-20h] is 19, her base: from behind set, but nothing taken off.

## 2. The cause (DSUN.EXE, read with capstone)

The melee attack routine (58019h) clears [BP-1Ah] and [BP-24h] once, at its start (58036h,
58040h), then runs all of the round's attacks in one loop (from 58113h, back there from 584CAh,
[BP-22h] counting them). Each pass loads [BP-20h] with the creature's THAC0 again (58124h) and
takes 2 off for from behind (582FFh) and 2 more for a backstab (58335h) only when this attack is
from behind (the target's facing at segment DS - 4356h + 37BDh, +5Bh a byte a creature, against the
attacker's direction to it: 582D0h). Nothing clears the flags between passes. So the Hayneedle's
backstab (from hiding: DSCLOG's stealth path) left [BP-1Ah] = 1 and [BP-24h] = 1 for the
Shadowseeker swings, which were not from behind and got no 2s; DSCLOG's STAB_FIRST (a later attack
in the round: no backstab) cleared [BP-24h] and added 2 back: 19 + 2 - 2 (STR) = 19, less [BP-8]'s
+1 weapon and +1 specialized: 17. The real THAC0 should have been 15, and as the flag said "from
behind" the target's DEX and shield didn't count either. The dice log's breakdown was right about
its numbers: it names the remainder STR, and the remainder was STR's +2 less the 2 given back and
the 2 from behind never taken.

## 3. The fix (REAR_FRESH, first in PROBE_STEALTH)

The creature's THAC0 (+1Fh) less [BP-20h] is what the game's code took off this attack: under 2,
[BP-1Ah] cleared; under 4, [BP-24h] cleared. 48 bytes. With it, the same round (try 6 of the
loads: the hiding and moving silently must both pass, about half the time):

```
Seneca attacks Templar BACKSTAB with Bone Hayneedle +1 (1d4+1): d20 = 18, needs 7+ (70%), hits AC -6, target AC 5 -> HIT
    THAC0 19, +2 from behind, +2 backstab, +2 STR, +1 weapon = 12
  Seneca hits Templar for 13: 1d4 = [4] +1 weapon +4 STR 18 +4 backstab (the dice 4 x2 = 8)
Seneca attacks Templar with Shadowseeker +1 (1d6+1): d20 = 15, needs 11+ (50%), hits AC 0, target AC 4 -> HIT
    THAC0 19, +2 STR, +1 weapon, +1 specialized = 15
  [attack] frame {... '-1Ah': 0, '-20h': 17, '-22h': 1, '-24h': 0}
Seneca attacks Templar with Shadowseeker +1 (1d6+1): d20 = 4, needs 11+ (50%), hits AC 11, target AC 4 -> miss
    THAC0 19, +2 STR, +1 weapon, +1 specialized = 15
```

The later swings are plain attacks now: THAC0 15, the Templar's shield counted (target AC 4, not 5).

- **A first-attack backstab** reads as before: three more in the next rounds (`THAC0 19, +2 from
  behind, +2 backstab, +2 STR, +1 weapon = 12`, on Arena Guards too).
- **Ordinary attacks**: `THAC0 19, +2 STR, +1 weapon = 16` (Hayneedle), `... +1 specialized = 15`.
- **An ordinary from behind by the target's facing** (a memory edit, not saved): a first round on
  a Guard (creature 31) left DS:494Ch (the attacker's direction) 1 and the Guard's facing byte 5;
  the facing byte set to 1 before Seneca's next turn made her round from behind by the game's own
  check: `Seneca attacks Guard BACKSTAB with Bone Hayneedle +1 ... THAC0 19, +2 from behind, +2
  backstab, +2 STR, +1 weapon = 12`, then `Seneca attacks Guard from behind with Shadowseeker +1
  (1d6+1): d20 = 3, needs 3+ (90%), hits AC 10, target AC 10 -> HIT` / `THAC0 19, +2 from behind,
  +2 STR, +1 weapon, +1 specialized = 13`: from behind kept, its backstab taken back (STAB_FIRST).

## Clean-up

No save made (memory edits: foes held, HP raised, a facing byte). DOSBox, Xvfb, the Loader's dice
log, the frame log and the watchdog stopped by pid; the lock released.
