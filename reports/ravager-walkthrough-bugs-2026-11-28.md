# Wake of the Ravager: the bugs players report, checked (2026-11-28)

The owner's private walkthrough of the sequel lists 49 things players have hit that look like bugs. Each
was checked against the sequel's scripts (GPLDATA.GFF of the GOG release 1.1, read with `dsloader/gpl.py`),
its program (DSUN.EXE) and what the mod already changes. Nothing of the walkthrough is quoted here: each
bug is described in our own words. The script sweep before this one is
[ravager-script-bugs-2026-11-28.md](ravager-script-bugs-2026-11-28.md).

Branch `claude/ravager-walkthrough-bugs`. Fixes to the program are `Patch` entries in `dsloader/ravager.py`'s
`PATCHES`; fixes to scripts are `SCRIPT_FIXES` (same length) and `SCRIPT_DETOURS` (longer, run from after the
script's end); the new potion is made in `ravager.free_action_potion`. Seen in play:
`playtest/logs/2026-11-28-ravager-walkthrough-bugs.md`.

## Fixed now

| Bug | What was wrong | The fix |
|---|---|---|
| **Resist Fire, Resist Cold, Protection from Fire and from Lightning, Fire Shield** never lessened a fire or cold spell | The damage routine halves a spell's damage when the target is guarded from every kind of damage the spell does. Its test was the wrong way round (a `jz` where Shattered Lands' same routine has `jnz`), so a spell of fire alone (Fireball) or cold alone (Cone of Cold) was never halved, while a spell of fire and something else was. | The test as Shattered Lands' (`protection_halves`). In play: a Fireball's 22, saved to 11, now does 5 to a member under Protection from Fire; without the fix the same set-up took the full 9 of a saved 19. |
| **Detonate** never offered when a psionicist gains a power | The level-up list finds a power's discipline through a routine whose test skipped power 0, Detonate, so it was never listed (the program's other copy of the routine has it right). | The test as the other copy's (`detonate_listed`). In play: a Kinetics level-up lists 6 powers with LEARN DETONATE (5 before). |
| The **ranger's warning** of the Draxans' ambush in the forest never comes | The tracking roll stores its result in one flag (70); the two scripts that should warn the party (GPL 234 and 187) read another (424) that no script sets. | Both read flag 70 (`ambush_warning_*`). |
| **Xarax's potions** (the alchemist): the potion of Free Action was paid for and never given, and orders went astray | Three slips: the potion he hands over for Free Action is an object no file has; the "an order is waiting" flag (506) was never cleared, so a later order was mixed up with the first; and his brewing clock was a global number (113) the earth temple's script also counts down and resets. | A potion of Free Action made from the potion beside it in the objects file (`free_action_potion`); the flag cleared as each order is priced (`potion_batch`); his clock on a number no script uses (160, `potion_clock_*`). |
| The **psionic powerstone, Ioun stones** and other items with an effect of their own (a mod bug) | With the mod's six new wizard spells on, an item whose effect number fell in the new spells' numbers (the powerstone, two Ioun stones, a staff and some others) was taken for a scroll of a new spell: its box showed the new spell's picture, and taking it off ended the new spell's effects instead of the item's own. | Only a wizard's scroll or spellbook is taken for a new spell (DSCLOG2's `NS_BOOK`). In play: an Ioun stone's box shows its own picture again (a new spell's face before). |

## Already fixed by the mod

- A worn item's spell stayed on after the item was taken off (`worn_spell_off`, 2026-11-23).
- The gladiator's AC bonus without armour (the mod's gladiator rules).
- The druid's XP table the cleric's (the AD&D tables rule).
- Psionic Blast taking real hit points (the mod's Psionic Blast, as Shattered Lands').
- The sleeping giant's key could be taken again and again (the script sweep, #310).
- Items and bags lost or changed in the transfer from Shattered Lands (the Loader's own party transfer
  brings every item across and bags keep what is in them).

## Not a bug in the scripts

- **Fayina's debt and Acar**: the knock that opens the way is set once Fayina is gone whichever way the
  debt was settled, the key is given, and the knock is also written in a book; no soft lock was found.
- **Abelard's fruit**: the fruit offered is looked for on the member talking and taken from the same
  member; nothing in the script loses it. Not reproduced.
- **The Bloodletter coffer's golems**: the script makes all six and sets them all hunting; two not
  joining is their walk, not the script.

## Found and left as the game has them

- **Magnolia thanks the party for saving her twice** one stage early: the line is behind "stage above 4",
  where the second rescue is stage 6; there is no other line for stage 5, so moving it would leave a gap.
- **Donno's flask stays full**: the flask's charges and the script's own count are two counters; it
  favours the player and nothing breaks.

## Rules and design, not mended

Water of Life acting as Heal, Tenser's Transformation, Produce Fire's damage, Magma Blade breaking,
Quench Fire against magical fire, Energy Containment blocking healing too, Flesh Armor's strength, the
intellect devourers' damage, weapons whose spell charges run out, the difficulty setting only at a
creature's making, the air clerics' missing 6th-level spells, the Steadfast Ring and Ring of Insight on a
level up, and casting a multi-shot spell again before its last shot: these are the sequel's rules as
written. Changing them is a rules change for the owner to choose, not a bug fix.

## Not fixable by the Loader (paths, maps, pictures, the program's drawing)

Bohumir's walk, a member stuck before the Veiled Alliance's meeting, Snappersaw's place, a cave exit
that leads back, NO PATH FROM HERE after the elevator, the mines' cart switch picture, a sound glitch in
the mind flayers' laboratory, Magnolia's figure in the jann camp, a cabinet in the maze letting the party
out of bounds, the volcano's Draxans, the Jumah crypt's walls going black, the mines' item counts on the
maps, key mashing on a black screen, and merging the two yellow keys (a crash not reproduced). These are
the maps', the pictures' or the walking code's; a few may be looked at in the recompiled program later.

## Still to look at

The Sultan's "access to the treasure" line before the guards allow it, the option to free Magnolia
going away, the Helm +3 missing from a body, the lemon showing as Unknown, and the Crystal Rod's
picture: not yet read in the scripts and objects.

## Shattered Lands (both games' parity)

None of the fixed slips is in Shattered Lands: its halving test is the right way round, it has no
second copy of the power list routine, the ambush and the alchemist are the sequel's own scenes, and
its items' own effects (spell bytes F9h on) are past its new spells' numbers (196 to 201).
