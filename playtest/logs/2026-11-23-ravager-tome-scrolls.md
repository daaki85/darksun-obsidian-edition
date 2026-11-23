# 2026-11-23: the Tome of Understanding and Kalzith's scrolls in Wake of the Ravager (effects group G)

*Branch `claude/ravager-party-transfer`. reports/wake-of-the-ravager-party-transfer.md, group G.*

The mod's two used-up items are the Tome of Understanding (+1 WIS, SL object 1446) and Kalzith's six
scrolls (SL objects from 1440). The sequel has no tome; its scrolls are learned or cast from the item
box's icon (opener 99260h, handler 995AFh, the use at 999CDh: `[bp-4]` holds the spell, power - 1).

## The build

- **The transfer carries the Loader's own SL objects.** `ravtransfer.with_added` read SL's objects
  from the player's SEGOBJEX only, so the mod's new ones (the tome, the scrolls, every object the
  Loader adds) arrived as money bags. It now reads the Loader's copy (`dos/SEGOBJEX.GFF`) as well. A
  transfer of `fountain-user` printed `1446 -> 21446 (the Loader's)`, `1442 -> 31010` (Kalzith's Blur
  as the sequel's own Spellbook of Blur) and `1443 -> 21443` (a keepsake).
- **The tome** is the Loader's object 21446, made like the sequel's wizard scroll (its picture from
  object 31300), with the power 318 (spell 317, past every spell the sequel has). DSCLOG2's
  TOME_READ (site 48, the Loader's patch `tome` at 999CDh, where the routine does `dec [bp-4]`)
  takes that object: +1 WIS on the sheet (+19h) and the creature (+1Dh), at most 25, the message
  "NAME reads the tome: WIS N." (or "NAME can grow no wiser.") into the routine's message buffer, and
  the routine's own end: the item used up (99B44h), or kept when the reader is at 25 (99B67h). Any
  other item goes on as before. Unit tests: `test_ravprotect.ProtectionTests.test_tome_read`, `test_ravtransfer.ItemSpellTests.test_tome`.

## In the game (a copy of `$WORK/rav` with the transferred `fountain-user` party, the Draxans' fight in Tyr)

Test edits in memory, never saved (scratch `mktome.py` turns a keepsake into a tome).

- **Items work only in a fight, on the member's turn.** Outside a fight the box's icon does nothing:
  the opener sets `[9D8Ch]` from its caller's flag, 1 only in a fight. That holds for the sequel's
  own Spellbook of Blur too. (Earlier, learning from a transferred scroll "did nothing" for this
  reason.)
- **The tome, Lex's turn**: the box ("Scroll", 5000), its icon clicked: the tome gone from the pack,
  Lex's WIS 6 to 7 (sheet and creature, DSCLOG2's `tomes_read` 1). A second tome (a keepsake made one
  in memory): WIS 7 to 8 on the inventory screen, `tomes_read` 2.
  ![](img/2026-11-23-ravager-tome-read.png)
- **The message was not seen**: no text in the inventory's bar nor on the map after the box closed
  (a 20-a-second burst). The sequel's own Spellbook of Blur, clicked the same way, shows nothing
  either and stays in the pack: whether Lex learned Blur is **not yet checked** (her spell list, or a
  wizard who can).
- **Not played**: the WIS 25 case (unit test only).

## Open

- Where the routine's message shows (if it does in a fight's inventory), and a Kalzith scroll learned
  by a wizard (the sequel's own spellbook object, so the sequel's rule).

No new area, no water noted.
