# The party's way into Wake of the Ravager: SSI's CHARTRAN read and redone in Python (2026-11-22)

Branch `claude/ravager-party-transfer` (built on `claude/ravager-port`). No game was played for this
step: SSI's own transfer utility (CHARTRAN.EXE) was run headless on Shattered Lands saves
(`chartran.sh SAVE OUT DEBUG`), its roster (Wake of the Ravager's CHARSAVE.GFF) read chunk by chunk,
and `dsloader/ravtransfer.py` written to make the same chunks. `ravxfer_check.py` sets the two side by side.

## What CHARTRAN writes

Member M of the SL party goes to roster slot 35-M (CHARTRAN overwrites slots 32-35 every time).
Per member it writes five chunks:

| chunk | holds |
|---|---|
| CHAR | the member's records: creature, sheet, three item lists with their items and any bag's contents, end |
| CACT | the SL creature's word +6 |
| SPST | 9 bytes, one bit per wizard spell the sequel knows (SL's 0-68 mapped; 34, 42, 49, 64 dropped) |
| PSST | 34 bytes, one per psionic power: (SL byte & F8h) >> 2 |
| PSIN | the disciplines: 1 for powers 0-5, 2 for 6-19, 4 for 20-33 |

A CHAR record has an RDFF's 10-byte header (level, of, kind, number, flags, length). The item lists
(SL creature +8, +0Ah, +0Ch) are flagged 16, 17 and 4; a list's first item is level 2, the next ones
level 4 pointing at the record before; a bag's contents follow its list, their first item "of" the bag.
An item takes the sequel object that ITEMS.BIN pairs with its SL object (first pair wins), and with no
pair the money bag (object 900). The money bag also covers a pair whose sequel object is only a
picture with no record (ITEMS.BIN pairs SL's bags 1572 and 1571 with 2228 and 2227, which have no record).
The creature's six scores come from the sheet (+1Bh-+20h), not the creature's own +22h (grate-user's
Cromwell: 25 on the creature, 20 on the sheet, and CHARTRAN writes 20). A list's bags are walked after
the list ends, the last bag first, and a bag inside a bag right after the bag that holds it. The item record is the sequel object's own, with the SL item's
quantity, charges, slot and plus written over it. The full field maps are in the memory note and in
`ravtransfer.py`.

## Result

| save | members | chunks | Python vs CHARTRAN |
|---|---|---|---|
| saves/trap-user | 4 | 20 | the same |
| saves/selling-junk-user | 4 | 20 | the same |
| saves/rest-no-call-user | 4 | 20 | the same |
| the other 12 SL saves in playtest/saves | 4 | 20 | the same (after the three rules above, found on doorway-blocked-user, grate-user and semyon-rack-user) |
| 20 made-up saves (spells, powers, bags in each list, nested bags, scores) | 4 | 20 | the same |

The only difference is a stray bit for spell 71 that CHARTRAN sets now and then, which matches no spell
the member knows. ravtransfer.py does not set it.

## What CHARTRAN loses (the Loader's job next)

- Every SL item without an ITEMS.BIN pair turns into a money bag. In the three kit saves that is
  8 of 50 items (trap-user), 10 of 44 (selling-junk-user) and 8 of 26 (rest-no-call-user).
- Priest spells aren't written (in the sequel, priests pray for theirs), and the 4 dropped wizard spells are lost.
- The mod's own items (its item types 115-147, Shadowseeker, Inixhide, the Rings and Cloak of
  Protection, the robes, the bone and metal weapons) all become money bags. Daaki's ask
  (2026-11-22): they come across, and their effects must work in the sequel.
- The player's roster slots 32-35 are overwritten without asking.

Water: no area was entered.
