# Wake of the Ravager: defilers' scrolls, 2026-11-27

**Under test**: Shattered Lands' defilers' scrolls (`defilerscrolls.py`) in the sequel's dice log (its
`item_watches` step, `RavDiceLog._item_watches_pass`) on the sequel's names (`ravlog.rav_items`: its defiler
objects, its wizard spells, the scroll a Spellbook, `ravlog.rav_book`). Branch `claude/sequel-defiler-scrolls`.

**Set-up**: Xvfb `:55`, the DOSBox lock held by this session. `RAV_DEFILER_CHANCE=100` (a new `ravdice.py`
switch: every defiler gets a scroll) so one roll is enough. Memory edits were test edits: nothing was saved.

**Finding the defilers**: the sequel's objects whose OBJEX.GFF record has class 18 on its sheet (+1Bh): the Lord
Warrior (3), El (6), Fermin (160), the Defiler (369), the Yuan-ti (434), Solurnis (436), Raenika (496). Their
placements (the regions' ETAB, 8-byte entries x, y, height, flags, object as a positive word): Raenika and five
Defilers in the Pyramid (RGN034), the Yuan-ti in RGN036 and RGN037, the Lord Warrior in RGN044, the rest in Limbo.

**Steps and what was seen**

1. **A jump to the Pyramid** (`ravjump.py 0x22 45 32`): DOSBox closed at once, twice, as the talk ran. Looked into
   (steps 5 to 7): my mistake, not the mod's. `ravjump.py`'s REGION is the region file's hex number, and the
   Pyramid is RGN034, so 0x34; 0x22 asks for RGN022.GFF, which the game hasn't, and it quits to DOS printing that
   name. The stock game does the same.
2. **A defiler made by a test edit**: Tyr's ambush (`logs/files/2026-11-26-ravager-new-spells-run.sh def2 0 0`,
   with `RAV_DEFILER_CHANCE=100`), then one of the fight's Draxans (creature 25) given the Defiler's object
   ([files/2026-11-27-ravager-defiler-crobj.py](files/2026-11-27-ravager-defiler-crobj.py) `25 369`), and the
   dice log started again (the first had already seen him as no defiler: the answer is kept for the fight).
   Within the pass his backpack list held a new item 208: `entity -31002, type 77, power 26, price 9000, slot 14,
   name 4` (a Spellbook of spell 25, a 3rd-level one). No dice log line, as in Shattered Lands. (A first try
   edited creature 5, a Draxan of the street who was not in the fight: nothing, as it should be.)
3. **Dropped where he died**: Computer Control on all four won the fight. His record emptied (status 3, his lists
   9999) and the book was in his body's container, thing 445, cell 3, with his other six things
   ([files/2026-11-27-ravager-defiler-finditem.py](files/2026-11-27-ravager-defiler-finditem.py) `208`).
4. **Read**: the body wasn't found on the screen among the others (the eye opened containers 218 and 211), so
   the book was moved into Ar'Anda's backpack by a test edit (out of 445's chain, first in her pack list 518, cell
   14). Inventory, a right-click: "Spellbook, 9000", its spell icon (game 286,17): `Ar'Anda reads the scroll of
   Blink: d100 = 76, needs 85 or less (INT 18) -> learnt`, `Message: YOU LEARN THE SPELL`, and the book gone. No
   item report for it (a book used up is ordinary).

## The Pyramid's real Defilers (a second run, the same day)

5. **Stock**: a stock copy of the sequel (no Loader) with its Reyhan talk edited the same way: `0x22` quits to DOS
   with "RGN022.GFF" on the screen; `0x34 45 32` arrives in the Pyramid among the Defilers. Their creature
   records carry object -363 (placed as 369 in RGN034's ETAB), in stock and in the mod alike.
6. **The mod, `ravjump.py 0x34 45 32`** with `RAV_DEFILER_CHANCE=100`: the five Defilers (creatures 15, 17, 21,
   22, 23) are not defilers to the dice log until 363 is in `RAV_DEFILER_OBJECTS` (the fix: 363 added, its test
   line too). With it, each got a new backpack list (500, 504, 502, 501, 494) holding a Spellbook (item 57: power
   55, price 12000; item 58: power 69, 18000).
7. **Dropped**: Computer Control. The first Defiler killed stayed at status 7 with its list 500 while the
   Pyramid's script talk ("That slow-witted fool deserved to die...") waited for a click; clicked, his record
   emptied (lists 9999) and the book was in thing 496 (slot FFh) with his body's things. The second likewise.

**Seen, not changed**: the fight's phantom `Preserver is killed` line at its start (seen before, 2026-11-27).

**Not seen in play**: the body's container opened by a click.

**Result**: a defiler in a sequel fight is given a Spellbook (the Pyramid's five too, once 363 was known), it drops
with the body's things, and it teaches. The Pyramid "crash" was the jump's wrong region number, not the mod. The
DOSBox and the dice logs of this test were closed by pid.

## Water

The Pyramid (RGN034) reached by a jump, in a fight: no water, jugs or waterskins seen on the screens looked at.
