# 2026-11-10: grand mastery's die against a large target

The build under test is commit bfb355f: DSCLOG's NEXT_DIE, with grand mastery stepping the large dice too. `buildcheck.py` OK. Memory edits only; no game was saved.

From `fountain-user`:
- Ester (member 2) was made a 9th-level fighter of the long sword in memory: sheet classes (9,0,0), levels (9,0,0), specs +14h = 1, unpacked. `specialize.skill` with her Bone Long Sword (type 81) gave 5, GRAND.
- Every foe was made a half-giant (`foeset.py C race=5` on one combatant of each sheet) and held (`foeset.py C eff=34`, 24 of them).
- The speech box was clicked away, then `passuntil.sh 2` and Tab + Return.

Ester against the Templar (a half-giant for the test):
```
Ester attacks Templar with Bone Long Sword (1d8): d20 = 16, needs 10+ (55%), hits AC -2, target AC 4 -> HIT
    THAC0 19, +3 STR, -1 bone, +3 grand mastery = 14
    Paralyzed: hit automatically, for normal damage (AD&D's held target)
  Ester hits Templar for 25: 1d20 = [15] -1 bone +3 grand mastery (1d20 for 1d8: a large target, grand mastery) +8 STR 20
```
Her second attack was also 1d20 (an 8, for 18). Before the fix it would have been the size rule's 1d12.

Not seen in the game: a man-sized target. The Templars and Arena Guards were turned back to race 1, but Ester had no Move left to reach one, and the next round's Tab chose an Arena Guard out of reach. That case (1d8 to 1d10) is the old behaviour, and `test_grand_mastery` covers it in emulation, through the game's attack routine and the probe.
