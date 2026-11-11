# 2026-11-10: can a polearm reach two squares? (the range byte)

Memory edits only, from `fountain-user`, with every foe held. Not saved.

Setup:
- Ester's right-hand item (35) was made the game's polearm, type 19 (`setitem.py 35 19`).
- Type 19's range byte (+0Ah, 1 for every melee weapon) was set to 2 in the type table (far pointer DS:1669h).
- On her turn she walked to (936,1512), two squares west of the held Templar (968,1512).
- Her turn's movement was set to 0: the word at segment DS - (4356h - 37BDh), +22Bh + 2 x creature.

Results:
- **With her bow still in the missile slot**, the attack pointer's click on the Templar shot the bow. A target out of melee reach takes the missile weapon.
- **With the bow and her second sword taken out** (`ring.unlink` on items 10 and 31, the polearm alone in her hands), the click on the Templar's figure did nothing. No swing, and her turn passed, as for a melee target out of reach.

So the game's melee doesn't use the item type's range byte, which the missile code does use. A polearm's reach would need the game's own adjacency test for melee found and patched. The user chose reach over the hook (2026-11-10). Whether to go on with that is the user's call.

## With the reach rule built (commit 7ae3e7f)
`buildcheck.py` OK. The polearm type's range stays 1. The rest is as above:
- Ester's right hand made the polearm (type 19);
- her left-hand sword taken out (`ring.unlink` item 31);
- her bow left in the missile slot;
- every foe held;
- she walked to (936,1512), two squares from the Templar at (968,1512);
- her Move was set to 0;
- `pointer.py attack` and a click on the Templar.
```
Ester attacks Templar with Bone Polearm (1d10): d20 = 9, needs 14+ (35%), hits AC 9, target AC 4 -> HIT
    THAC0 19, +3 STR, -1 bone, -1 Battle Dancer = 18
    Paralyzed: hit automatically, for normal damage (AD&D's held target)
  Ester hits Templar for 16: 1d10 = [10] -1 bone -1 Battle Dancer +8 STR 20
```
A melee swing from two squares, with the polearm and not the bow. The cases without reach are tested in emulation (`test_reach`): another weapon in the other hand, two polearms, a wall on the line, the rule off, and other callers. In the game I didn't see the computer's foes use it, nor walk-to-attack stop at two squares.
