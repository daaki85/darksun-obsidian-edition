# Wake of the Ravager: spellbooks of the new wizard spells in a fresh game (2026-11-26)

Branch `claude/ravager-spell-books` (on part 3's `claude/ravager-new-spells-learn`, PR #201, which already holds
`obsidian-edition` with #191's `ravgear.py` and #193's `shopstock.py`). Under test: `ravgear.BOOKS`, spellbooks of
the six new wizard spells (320-325) put into OBJEX2.GFF's copy by ravgear's own mechanism.

## How Shattered Lands has them

- **Kalzith** (the slave pens) sells a scroll of **Cat's Grace** at 6000 among his six (`kalzith.SCROLLS`; 3000 a
  level, the game's price for its scrolls).
- **Loot**: a defiler's body may hold a scroll of any preserver spell, the six among them with their switch
  (`defilerscrolls.spells`, 5 in 100), and the arena's defiler champion one of **Fogbolt, Spook or Reflected
  Image** (`champions.SCROLL_SPELLS`).
- Nowhere else: Erdlu Claw and Friends are only in those random rolls.

## What the sequel gets

The sequel's one seller of spellbooks is **Notaku** (Tyr's Shadow Square, object 58: his own a 3rd-level
spellbook at 9000, a psionic book and a one-use Shield scroll). Its shops (scripts calling GPL op 24h, the shop:
43, 53, 54, 143, 144, 148, 153, 155, 157, 158, 221) are otherwise the Weaponer's, Armorers', Salespersons',
the mines' Receptionist's and Sureshot's, with weapons, armour and goods. So:

| Book | Object | Price | Where |
|---|---|---|---|
| Cat's Grace (2nd) | 31190 | 6000 | Notaku |
| Erdlu Claw | 31191 | 3000 | Notaku |
| Fogbolt | 31192 | 3000 | Notaku; carried by Raenika (496) |
| Reflected Image | 31193 | 3000 | Notaku; carried by Fermin (160) |
| Spook | 31194 | 3000 | Notaku; carried by Kalaobuta (290) |
| Friends | 31195 | 3000 | Notaku |

Fermin, Kalaobuta and Raenika are three of the sequel's people who already carry a wizard's spellbook (OBJEX.GFF):
the loot, as SL's defilers' scrolls. Where they are met was not looked up, nor played.

Each book is an object of its own (a shop shows items of one object as one), free in the sequel and in the
numbers the game teaches from (31000-31199; a 313xx object is a one-use scroll, cast), its OJFF and RDFF copies
of the sequel's own 1st- or 2nd-level spellbook (31002, 31010): its picture the sequel's book (BMP 1969, the
OJFF's icon), its name "Spellbook", its +2 and +10h the spell + 1 (321-326). With the new spells' switch only
(`ravager.write_objects`: `ravspells.SKIP`). `shopstock` tops up a saved game's Notaku too (by object), as far as
his 12 pack cells go: 4 of the 6 after his own 7 and the Short Sword +1 (not played).

## Played

Throwaway copy `/tmp/playtest/ravSB` (a fresh `cp -a` of `rav`), `RAV_LOADER=1 sh ravstart.sh` (a new game, the
build's OBJEX2.GFF with RDFF/OJFF 31190-31195), the dice log attached (`ravdice.py --numbers`, RAV_NO_SAVES=1:
autosaves off). Nothing was saved.

- **The opening**: the talk (3, Return x4), then the ambush: C opens the USE screen; the first click there only
  took the mouse (`ravclick.py` read the pointer at (158,99)); after a click on the window the four lower small
  icons (47,53 / 98,53 / 47,112 / 98,113) lit and "COMPUTER CONTROL IS ON"; Escape; won ("Each party member
  receives 10000 experience points!"), Return x6.
- `ravgo.py y 1224 x 560 y 1130 x 420 y 1000 x 300 y 900`: at (308, 903), below Notaku's stall.
- **Notaku's list in memory** (`ravshop.py thing 33`) before the talk: his 7, the Short Sword +1, then **31190-31195**,
  prices 6000 and 3000 x5, power 321-326, type 77, name 4; the first 12 in backpack cells 14-25, the last two (Spook,
  Friends) cell 255: the game gave them none, and the shop listed them all the same.
- The talk: two right-clicks for the look pointer, a click on him (game 138,16), the Look box's first button
  (157,66), then 3, 1, 3, **2 "Show me your goods."**. Money 5000 -> 50,000 by a test edit
  (`files/2026-11-26-ravager-spell-books-money.py`, never saved).
- **The shop**: page 1 the sequel's six; MORE, page 2: potion 5000, Short Sword +1 20800, then the **books at 6000,
  3000, 3000, 3000** with the book's picture; the pointer over one: **"SPELLBOOK"**
  ([picture](img/2026-11-26-ravager-spell-books-shop.png)); MORE, page 3: **two more at 3000**
  ([picture](img/2026-11-26-ravager-spell-books-shop-3.png)). 14 items in all. No CHA discount at the leader's CHA.
- **Bought** Friends (page 3's second) with Ar'anda chosen (her portrait, game 27,25): **"SOLD!", 50,000 -> 47,000**;
  put in her pack (195,28): item 132, entity -31195, power 326, slot 14. Right-clicked: the box "Spellbook, 3000"
  with **Friends' heart icon** ([picture](img/2026-11-26-ravager-spell-books-box.png)); the icon right-clicked:
  "FRIENDS: The caster's charisma rises by 2d4...".
- **In the shop** a left click on the box's icon closed the box and taught nothing. Out of it (Escape: "Thank you,
  your business is appreciated."; 4 Goodbye; Return), the inventory (top-left icon, game 22,17), the book
  right-clicked, its icon clicked: **"YOU LEARN THE SPELL"**, the book gone
  ([picture](img/2026-11-26-ravager-spell-books-learn.png)); her sheet +3Dh **80h** (Friends),
  DSCLOG2's `ns_taught` 1, `ns_scrolls_n` 1 (`files/2026-11-26-ravager-new-spells-mem.py`).
- **Control** (`RAV_LOADER=1 RAV_SKIP=new_spells`, a new fresh copy; `ravstart.sh` now takes `new_spells` for
  OBJEX2.GFF: the books left out, the spells kept): the copy has no 31190-31195 (the Short Sword +1's 19900 still
  there), and Notaku's list at the start of the game ends with the Short Sword +1 (8 items, no books).

Not played: Cat's Grace's 2nd-level book bought and read, the three carriers, a saved game's top-up.

## Water

No new area: Tyr's streets and Shadow Square (as logs/2026-11-25-ravager-weapon-gaps.md).
