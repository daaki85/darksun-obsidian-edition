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
