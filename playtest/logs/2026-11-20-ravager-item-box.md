# Test log: charges in item boxes, Wake of the Ravager (2026-11-20)

Under test: DSCLOG2's PROBE_ITEM_BOX (patch `item_box`, 9A4FEh: INT D0h in the item box routine's
"push 0") drawing "Charges: n" for an item that casts a spell, else "Hit -N" for a plain weapon of a
weaker material.

## Found first

- The sequel's item box routine ends at 9A4FEh (SL's 8C1A1h), the same code with the sequel's records;
  its colours C200B5h (SL's 960081h); a box has an INFO button at the right of its last row.
- **The sequel's item record keeps the power (spell + 1) as a word at +10h**, not SL's byte at +0Fh: the
  program's uses of each item field counted alike (SL's +0Fh 37 uses, the sequel's +10h 35, nearly all
  word reads; +0Fh none), the charges at +0Eh (the use routine at 7A942h decrements the byte, then tests
  the word), and items in Tyr: a One-use Scroll charges 1 spell + 1 9, a Spellbook spell + 1 54.
  `ravager.item_field` mapped SL's +0Fh and +10h to the same offsets: fixed (+0Fh -> +10h, +10h -> +12h).
- The material to-hit routine is SL's (1D401h, SL's 5EB31h): wood -3, bone -1, stone and obsidian -2.

## In the game (ravager-roost, 23:35 UTC)

- Inventory (I), Ar'anda, a right click on her Obsidian Dagger: the box reads "Hit -2" under the damage.
- Test edits (never saved): the dagger's charges 12, spell + 1 9: "Charges: 12" (and the game's own spell
  icon in the box). 250: "Charges: 250" ran into the INFO button by a letter; the space after the colon
  is now left out from 100 up ("Charges:250", clear of INFO); 7: "Charges: 7".
- Leather Armor: the box as the game's (AC BONUS:1), nothing added; with a test edit of 3 charges,
  "Charges: 3" in the row after AC BONUS.
- DOSBox stopped by pid, nothing saved.

Not seen: a real charged item counting down as it is used (no save has one; the countdown is the game's).
