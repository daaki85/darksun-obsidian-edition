# 2026-11-10: damage on held (Paralyzed) foes

Under test: why held foes lose more HP than the dice log shows (the open finding of
logs/2026-11-10-creature-size.md).

## What the code says (before playing)
- The attack routine (5883Ah) calls the game's damage call (5B8:20h, 78BA8h) with the damage
  rolled and, at 58B0Dh, the damage x 2 ("shl ax,1") as "what a helpless target takes".
- 78E44h hands both to 79BF9h, which takes the second when the target's status bits have 4
  (held) or its creature +1Ch is 3 (out cold). So a weapon hit on a held foe does double damage:
  the game's own rule, the same mechanism as the spells' "the most its dice can do".

## Steps
Build: `buildcheck.py` OK (routines as the EXE, 134 vectors at their handlers, the tail as built).
Save `fountain-user`, the speech box clicked, every foe Paralyzed in memory (`foeset.py C eff=34`
on 17, 19-28, 30, 32, 34, 39, 40, 42, 45, 46), `passuntil.sh 3` (Seneca's turn), then an HP poller
(below) in the background and Tab + Return. Memory edits only; nothing saved.

1. **The finding again, the old log** (Seneca: Bone Hayneedle +1 and Shadowseeker +1): a BACKSTAB
   hit "for 13" took 26 (41 -> 15 at 2.91 s), then 10 more with no line (-> 5 at 3.35 s), then the
   off hand's hit "for 12" took the last 5 (3.86 s). The 26 is the game's x2; the 10 is not the
   off hand's: Seneca's kit is **Poisoner** (65), whose every melee hit queues the monsters'
   poison (DSCLOG's PROBE_POISON: power 176, 10 damage, save negates), and a held creature
   makes no save (79B0Ch: `test [bp-0Ch],4` / creature +1Ch 3 -> failed, no roll), so there was
   no save line to name it. The finding's "a miss took 10" was this poison, landing ~0.5 s after
   the hit before it.
2. **The dice log changed, first try** (the poison put down through the spell window): the
   doubling matched (`for 18: (1d4 = [4] +1 weapon +4 STR 18) x2 Paralyzed`, -18), but the first
   hit's poison landed after the second hit's line, so the log took the -10 as "10 of the 22
   rolled" and the kill's -13 as "13 from Poison". Changed to a poison due on the target for 3 s,
   taking a fall of exactly 10 (or 10 and the first waiting hits).
3. **The dice log changed, second try**:
   ```
   Seneca attacks Templar BACKSTAB with Bone Hayneedle +1 (1d4+1): d20 = 18, needs 7+ (70%), hits AC -6, target AC 5 -> HIT
     Seneca hits Templar for 26: (1d4 = [4] +1 weapon +4 STR 18 +4 backstab (the dice 4 x2 = 8)) x2 Paralyzed: a helpless target takes double
     Templar is poisoned by the hit: Poison (10 damage), no saving throw (Paralyzed)
     Templar now 15/41 HP (-26)
   Seneca attacks Templar from behind with Shadowseeker +1 (1d6+1): d20 = 16, needs 12+ (45%), hits AC 1, target AC 5 -> HIT
     Seneca hits Templar for 18: (1d6 = [2] +1 weapon +2 specialized +4 STR 18) x2 Paralyzed: a helpless target takes double
     Templar is poisoned by the hit: Poison (10 damage), no saving throw (Paralyzed)
     Templar takes 10 from Poison (10 damage), now 5/41 HP
     Templar now 0/41 HP (-5)
   Templar is killed
   ```
   The poller: 41 -> 15 (2.91 s), 15 -> 5 (3.34 s), 5 -> 0 (3.87 s). Every fall has its line.

## Not changed
The game's rule itself (double damage, no save for a helpless target). AD&D's treatment of held
creatures differs (the user to decide whether to follow it); the manual says nothing.

## The HP poller (hpwatch.py, run from anywhere)
```python
import os, sys, time, struct
PLAYTEST = '/home/user/darksun-obsidian-edition/playtest'
sys.path.insert(0, PLAYTEST)
__file__ = os.path.join(PLAYTEST, 'live.py')
exec(open(__file__).read())
secs = float(sys.argv[1])
def hps():
    out = {}
    for c in range(48):
        cr = gd.combatant_creature(c)
        if cr is None: continue
        out[c] = (gd.creature_name(cr), struct.unpack_from('<h', gd.creature(cr), 0)[0])
    return out
last = hps(); t0 = time.time()
while time.time() - t0 < secs:
    now = hps()
    for c, v in now.items():
        if c in last and last[c][1] != v[1]:
            print('%.2f %s (%d) %d -> %d' % (time.time() - t0, v[0], c, last[c][1], v[1]), flush=True)
    last = now
    time.sleep(0.01)
```

## The rule: held targets as in AD&D (the user's choice, option 1)
The user asked for AD&D 2nd edition's held target as a rule, on by default: hit automatically,
normal damage (PHB Table 51). DSCLOG's HELD (sites 589E9h and 58B0Dh), the Loader's `held_hit`.
Build 67,744 bytes (before the rebase onto the size rule's SIZE_PRE: 67,776 after, the sites 108 and 109), `buildcheck.py` OK; both sites seen patched in the running game's code
(`cd 98 9e 90 74 11` at the d20's test, `cd 98 9f 90 90` at the damage).

4. **Rule on** (`rules_hi` FFFFh): `fountain-user`, every foe held, the Templar's sheet base AC
   (+27h) written -10 (its AC -16: only a 20 hits), Seneca's turn, Tab + Return:
   ```
   Seneca attacks Templar with Bone Hayneedle +1 (1d4+1): d20 = 8, only a 20 hits (5%), hits AC 8, target AC -16 -> HIT
       Paralyzed: hit automatically, for normal damage (AD&D's held target)
     Seneca hits Templar for 6: 1d4 = [1] +1 weapon +4 STR 18
     Templar now 35/41 HP (-6)
     Templar takes 10 from Poison (10 damage), now 25/41 HP
   Seneca attacks Templar with Shadowseeker +1 (1d6+1): d20 = 5, ... -> HIT    (for 9: -9, then the poison's 10)
   Seneca attacks Templar with Shadowseeker +1 (1d6+1): d20 = 9, ... -> HIT    (for 13: the last 6)
   ```
   The poller: 41 -> 35 -> 25 -> 16 -> 6 -> 0. Every swing hit, each for its damage, not doubled.
5. **Rule off** (`"held_hit": false` in settings.json, reloaded: `rules_hi` 7FFFh), the same setup:
   a natural 20 backstab for 26 (`x2 Paralyzed`), then two Shadowseeker swings on 12: misses. The
   game's way. settings.json put back.

Not tried in the game: a monster's blow on a held party member (the same routine and sites; the
unit tests run them with any target).
