# Test log: preservers' INT and scrolls, Wake of the Ravager (2026-11-21)

Under test: DSCLOG2's SCROLL_LEARN, LEARN_SAID and LEARN_REFUSED (SL's INT_LEARN, RULE_HI_INT): a wizard
learning a spell from a scroll has INT's chance (AD&D's table) and can know only so many of a level.

## Found first

- The sequel's scroll: an item whose entity (+0, negated) is 7918h-79DFh (a wizard scroll; 7AA8h-7B0Bh
  the others), its spell the power (+10h) less 1, item type 77 (78 a priest scroll). Clicking the spell's
  icon in the item's box (right-click the item on the inventory screen) runs 999EEh-99A8Ah: the bit of the
  reader's known spells (selector 320h:39Ch + 15 a member) tested, set, the scroll used up (5F8h:43h).
- The spells' levels: a table at DS:0656h, each level's first spell, 11 bytes for wizard spells (0, 12,
  25, 39, 56, 68, 81, 92, 102, 111, then 115 the end) and 11 for priest (115, 127 ... 233, 235). The
  sequel has ten levels.

## In the game (ravload.sh ravager-after-ambush, RAV_LOADER=1, about 14:40 UTC)

Ar'anda's items made scrolls of Shield and Grease by copying a real scroll's record (item 58) into her
Dagger, Longsword and Sling (entity, type, name; the power set), her INT and known spells written (all
test edits; DOSBox stopped after, nothing saved). The dice log with 0xE2068205.

- **A failed try** (INT 9, chance 35%): the Dagger's scroll of Shield went, the spell not learnt; the
  helper's +272 read `01 00 | 00 09 09 23 2a 01` (Ar'anda, Shield, INT 9, 35, d100 42, failed). The dice
  log then didn't read +272 (fixed: RavDiceLog now does); again with Grease: "Ar'Anda reads the scroll of
  Grease: d100 = 61, needs 35 or less (INT 9) -> not learnt (the scroll is used up)", the bit still clear.
- **A full level** (INT 9, the most 6; eight 1st-level spells known): "Ar'Anda can't learn Shield from
  the scroll: knows 8 1st-level spells, the most for INT 9 (the scroll is kept)", and it was (three
  clicks, three lines).
- **Learnt** (INT 18, 85%): "Ar'Anda reads the scroll of Shield: d100 = 68, needs 85 or less (INT 18) ->
  learnt", her bitset's second byte 29h to 2Bh (spell 9).

## Still to do

- No message on screen for any outcome: the game's message routine (560h:2Ah) showed nothing on the
  inventory screen or the map after, its own "already know" included. To look into.
- The level-up's spell list (SL's PROBE_PICK_LIST, PICK_ANY): not ported.

Water: none new (Tyr's street after the ambush).
