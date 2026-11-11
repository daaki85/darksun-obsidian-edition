# The sewer grate's hack wants a melee weapon (2026-11-11)

The user's ask: "Make the grate want a melee weapon." Save `saves/grate-user` (Cromwell leading:
Wooden Shield worn in slot 10, Metal Axe in the weapon hand, slot 3, Wooden Bow in slot 2).

## Finding how to test "melee" in a script

- A first try tested the item's field 4,0 (as the type's flags): no item matched, so no hack.
- Probe builds (marker prints per guess) showed: field 85 is the slot (+11h: the axe 3, the bow
  2); field 72 is the item's +00h, minus its object (the axe -1183); no field 0-99 nor 72,0-99
  holds the type (22 for the axe). A number printed with 4Fh shows nothing; large probes (about 200
  tests) ran nothing at all.
- So the test leaves out, by kind, the 17 items held in a hand that aren't melee weapons (bows,
  slings, chatkchas, shields, the Storm Ring), from the Loader's SEGOBJEX and the game's IT1R.

## The wrong weapon named

- With the axe found the game said "Cromwell's Bow rings off the grate" (and on 2026-11-01
  "hacks the lock off with his Bow"). Read from memory: command 49h copies each item into one
  scratch object (2Bh); on a find the game names it (41h, into 2Ch) and goes round once more, and
  that step copies the next item (the Bow) over it. Setting the naming value by hand did nothing.
- The repair now leaves the loop on the find (jump to its RETURN, A96h).

## In play

- Axe in hand: "1. Rip it open. 2. Hack the lock off. 3. Leave the grate."; Hack:
  "Cromwell's Axe rings off the grate, unharmed." (a failed hack; metal rings off).
- Bow in the weapon hand, the axe moved out (`itemedit.py`, memory only): "1. Rip it open.
  2. Leave the grate." No hack.

Tests: `test_grate_hack_wants_a_melee_weapon`, `test_not_melee_kinds` (with DSUN_GPLDATA and
DSUN_OBJECTS); the whole suite passes (1869, 20 skipped).
