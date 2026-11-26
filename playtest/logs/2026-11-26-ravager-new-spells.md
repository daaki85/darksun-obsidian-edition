# Wake of the Ravager: the new wizard spells (2026-11-26)

Branch `claude/ravager-new-spells`. The six new wizard spells (Cat's Grace, Erdlu Claw, Fogbolt, Reflected
Image, Spook, Friends) in the sequel: part 1 their numbers, records, icons and texts; part 2 their casting
(DSCLOG2's sites 140-147).

## Their numbers

- The sequel's RESOURCE.GFF has DATA 0-319, all in use: wizard 0-114 (Armor to Wall of Ash), priest
  115-234, psionic 235-268, monsters' powers 269-319 (MONS269...). No six free wizard numbers below 120:
  115-119 are Bless, Curse, Cure Light Wounds, Cause Light Wounds and Entangle; only their five known bits
  are unused.
- So the six are **320-325** (past the table, as SL's 196-201 past its 196): DATA 320-325, ICON 21320-21325,
  SPIN 321-326. The game holds ICON 21000-21268 and SPIN 1-269, so none of those numbers is taken.
- Who knows them: the sheet's bits SL already keeps (+3Fh 08h-80h, +3Dh 80h), which the party transfer
  carries. Nothing new is needed on the sheet, and +45h-47h are not used.

## The copy

- `dsloader/ravspells.py` builds the records from the sequel's own Strength (23), Enlarge (5), Charm Person (2)
  and Mirror Image (19) records with DSCLOG's NS_PATCHES. The landing sounds come from Haste's, Shocking
  Grasp's and Fog Cloud's, Fogbolt's cast sound from Fog Cloud's and its flight from Magic Missile's. Spook's
  effect is the sequel's Afraid (35).
- Icons: SL's drawn ones (icons.py), each colour the nearest of those the sequel's own spell icons use, in the
  PLNR form. Without SL, the template's own icon.
- With `"new_spells": false` they are left out.

## Played

- `RAV_LOADER=1 sh ravstart.sh /tmp/playtest/ravSP` (a throwaway copy): the copy with DATA 320-325 starts
  through the Loader to Tyr ("Hurry! You must come with me to the Veiled Alliance!"), the same as before.
  RESOURC2.GFF holds the six records, icons and texts.
- Not played: learning and casting. The game never asks for a spell past 319 until DSCLOG2 answers for these.

## Part 2: casting them (DSCLOG2, sites 140-147)

What the helper does (`dos/dsclog2.asm`, NEW SPELLS; the patches `ravspells.program_patches()`):

| Site | Where | What |
|---|---|---|
| 140 NS_CMP | 60 compares of a spell with 73h, EBh, 10Dh | a new spell compared as wizard spell 72h (`dos/ns_cmp_table.inc`, from `ravspells.cmp_table_asm`) |
| 141 NS_KNOW | 62625h, "does member know spell" | the sheet's bit |
| 142 NS_LEVEL | 62AD0h, a spell's level | Cat's Grace 2, the others 1 |
| 143 NS_LIST | 6254Fh, the USE screen's list | the known ones of that level first |
| 144 NS_CAST | 656D0h, the spell handler's switch | Cat's Grace and Friends to Strength's case |
| 145 NS_EFFECT | 6623Bh, Strength's case | effect 113 (Cat's Grace) or 116 (Friends, its own 2d4) |
| 146 NS_ABILITY | 85351h, the abilities' effects | 113 DEX +amount (3-24), 116 CHA +amount (to 25) |
| 147 NS_CLAW | 86A45h, a natural attack's dice | the first 1d6+1 with Erdlu Claw (114) where better |

Through existing hooks: STINK_SWING calls NS_SWING (Fogbolt 115: the fogged attacker 3 worse, attacks on it
2 better; Erdlu Claw: an unarmed attack 1 better), IMAGE_SPELL and IMAGE_BLOW take 50 for Reflected Image
(NS_IMAGE_CHANCE: the Mirror Images effect's spell 323), PROT_SAVE calls NS_SPOOK_SAVE (1 worse a 2 levels
of the caster's preserver or wizard class, at most 6), and STRENGTH_DICE rolls Cat's Grace by class
(GRACE_SIDES: rogues 1d8, priests 1d4, the rest 1d6). "ns_effects" names the empty effect records 113-116
(Cat's Grace, Erdlu Claw, Fogbolt, Friends) with their spells' icons; Erdlu Claw's and Fogbolt's records
take 114 and 115. The dice log (ravlog) has the spells as 320-325 and the effects as 113-116.

DSCLOG2.EXE 51024 -> 52752 bytes. It loads high: its UMB block 52224 bytes (from about 51150), UMB free
103232 after it; conventional memory free 80576 in the largest piece with the game running (a5), as before
(the helper isn't there).

## Played (part 2)

Runs `logs/files/2026-11-26-ravager-new-spells-run.sh TAG` (ravSP, a throwaway copy; Ar'anda taught the six
in her sheet's bits and the party at 250 HP, test edits never saved; the class restrictions off in the
dice log's rules so a preserver in armour casts). In the Draxans' fight, from Ar'anda's USE screen: a spell
dropped on a portrait casts on that member (`logs/files/2026-11-26-ravager-new-spells-mem.py` prints DSCLOG2's
counters, `...-fx.py` the active effects); a drop on the list's panel brings the aim pointer up ("NO
TARGET"), then a click on the figure. `ravfight.py cast X Y LEVELS OBJECT` (new: OBJECT) aims at one object.

- **The USE list** (level 1): Erdlu Claw, Fogbolt, Reflected Image, Spook, Friends first, then her own;
  level 2: Cat's Grace first. ns_cmps counts every compare made a wizard's; ns_lost stayed 0.
- **Erdlu Claw** on Thy'rokh (a2, a3): the effect 114 "Erdlu Claw" on him (spell 321). His bite then
  "THAC0 15 base, +5 in bonuses = 10" (ns_swings 1: Claw's +1 on an unarmed attack). Not seen: the claws'
  1d6+1 (ns_claws 0): he fights with his gythka (a move of it out of his hand in memory wasn't enough).
- **Fogbolt** on Draxan#23 (a2): "Fogbolt: 2d4 = [3 + 1] = 4", "Draxan#23's saving throw vs Fogbolt from
  Ar'Anda#0 (spell): d20 = 10, needs 13 (40% to save) -> failed"; effect 115. His attacks on Ar'anda then
  needed 11+ where they needed 8+ ("THAC0 13 base, -2 in bonuses = 15": 3 worse; the log doesn't name it).
- **Reflected Image** on herself (a2, a5): Mirror Images (46) with spell 323 and one image; a Draxan's
  attack: "Mirror Images on Ar'Anda#0: an image vanishes, none left: it ends", ns_reflects 1 (the 50).
- **Spook** (a5) on Draxan#23: "Draxan#23's saving throw vs Spook from Ar'Anda#0 (spell): d20 = 3 -3 other =
  0, needs 13 (25% to save) -> failed", Afraid (35) on him; ns_spooks 1 (her preserver level 6: -3). The
  log named it "other" (its spell record read stopped at 320: fixed after, `ravlog.SPELLS_END`). In a3 a
  paralysed Draxan took it without a save (the game's helpless rule).
- **Friends** on herself (a3): "Friends: 2d4 = [2 + 4] = 6 -> Ar'Anda#0's CHA +6 while it lasts (at most
  25)"; her CHA 18 -> 24 (the creature's +1Eh), "Friends" under her name on the map.
- **Cat's Grace** (a3, a4): on Terrannus "Cat's Grace: 1d6 = 4 -> Terrannus#1's DEX +4"; after Grace by
  class (a4) on Thy'rokh, a fighter/druid: "Cat's Grace: 1d6 = 6 (fighter) -> Thy'rokh#2's DEX +6 while it
  lasts (at most 24)"; effect 113 "Cat's Grace".
- **Control** (c1, `RAV_SKIP` all 68 of `ravspells.program_patches()`, the same sheet bits): the copy's
  program holds the game's bytes at every one; her USE screen at level 1 shows only her own four spells
  (no new ones), and DSCLOG2's counters stay 0 (ns_cmps, ns_listed, ns_casts).

Lessons: the USE screen keeps its LEVEL between openings (a LEVEL press for Cat's Grace left the next open
at level 2: a Fireball and a Web went out by mistake); look at it before a click. The slots-for-all byte
(DS:13F8h, 1) shows every wizard spell crossed out: no use for a test. After a cast the list shows crossed
out until the next turn. A Web between caster and target gives "NO LINE OF SIGHT".

## Part 3: learning them (DSCLOG2, sites 148-149)

Branch `claude/ravager-new-spells-learn` (on part 2's `claude/ravager-new-spells`).

| Where | What | DSCLOG2 |
|---|---|---|
| PICK_LIST (93246h, VEC_PICK_LIST) | CHOOSE A SPELL's page (the level up's and creation's): the new spells of the page's level the reader doesn't know added after the game's, at most 20 words at 370h:7 | `ns_page_add` |
| PICK_ROOM, PICK_FULL | the INT rules count them: a level has room while one is unknown; a known one counts towards the INT's most (PICK_ANY, PICK_PAGE and PICK_MOST through these) | `ns_level_new` |
| CR_PICKS' count (`wiz_count`) | a pick of one at creation counts as a pick (CR_DUE by level) | |
| 148 NS_SCROLL | 999FBh, a spellbook read ("mov es,ax / mov bx,es:[0B44h]", after NS_CMP at 999EEh): a new spell known, on to YOU ALREADY KNOW THIS SPELL; else its sheet bit set and on to the book used up and YOU LEARN THE SPELL | `ns_scroll`, `ns_teach` |
| 149 NS_LEARN | 936B4h, CHOOSE A SPELL's pick ("mov es,ax / or es:[bx+39Ch],dl"): a new spell's sheet bit instead of the bitset's | `ns_learn` |
| NS_CMP, 3 more | 77CF9h, 9A7D4h, 9A9C5h ("cmp ax,140h" with AX an item's power, the spell + 1): NS_PLUS1 (80h) in the table's form | `ns_cmp` |
| NS_SWING | Erdlu Claw's +1 only for the set-up's first set of natural attacks ([BP-20h] in the **set-up's** frame, the hit routine's caller: `[bp]`) | `ns_swing` |

The dice log: Fogbolt named in the to-hit line ("-3 Fogbolt", "+2 target's Fogbolt"), Erdlu Claw's +1 ("+1
Erdlu Claw") for an unarmed first-set attack (ravlog's `_after_setup`). DSCLOG2.EXE 52752 -> 53168 bytes.

## Played (part 3)

All in throwaway copies of `rav` (`/tmp/playtest/ravSP`), all test edits never saved, the dice log attached
(`logs/files/2026-11-26-ravager-new-spells-run.sh TAG BITS KIT`: BITS 0 and KIT 0 for nothing known).
`...-mem.py` now prints `ns_paged`, `ns_taught`, `ns_scrolls_n` and the four sheets' +3Dh/+3Fh; `...-known.py`
a member's bitset by level.

- **Level up** (l2, l3; `...-levelup.sh`: Ar'anda made a 5th-level preserver with `ravlevel.py set 0 40000 3
  11,12,17 5,6,7`, the Draxans' HP 1, Computer Control, the XP boxes): "Ar'Anda gains a level", CHOOSE A SPELL
  opened on LEVEL 3 (12 of the game's); LEVEL to 1: **13, the 8 unknown of the game's then Erdlu Claw,
  Fogbolt, Reflected Image, Spook, Friends**; LEVEL 2: 11, **Cat's Grace last** (`ns_paged` 6). Cat's Grace
  clicked: the window shut, +3Fh 10h (`ns_taught` 1). In l1 a blind click on the XP box at (160,100) had
  picked a 3rd-level spell on the window (it was up under the box's place): grab before a click.
- **Spellbooks** (l3, out of the fight on the inventory screen; `...-scroll.py ITEM POWER 60` copies the
  spellbook item 60's entity, type and name over Ar'anda's carried items 1-3 and writes the power, the spell +
  1): Friends (326): "YOU LEARN THE SPELL", the book gone, +3Dh 00h -> 80h; Erdlu Claw (322): +3Fh 30h;
  Cat's Grace (321, known): "YOU ALREADY KNOW THIS SPELL", the book kept; Fogbolt (323): +3Fh 70h
  (`ns_scrolls_n` 3). Her armour (item 0) made a book of Burning Hands (power 2), the game's path: "Ar'Anda
  reads the scroll of Burning Hands: d100 = 83, needs 85 or less (INT 18) -> learnt", bit 1 set. Only the
  spellbooks (objects 31000-31199, 31400-31499: 999D0h) teach; a one-use scroll (313xx) is cast (9B7Dh). A
  non-preserver's book (Terrannus) did nothing on the click.
- **The first build's scroll site broke the game**: at 999F8h, "mov ax,370h / mov es,ax", the INT's number
  sat on the word the overlay manager fixes up as it loads the code, so the code ran another INT: the read
  did nothing, and DS:4 and DS:4Ch were written (the Borland signature "Corland", the Loader's
  `find_data_segment` failing after). Moved to 999FBh (`mov es,ax / mov bx,es:[0B44h]`).
- **Creation** (c1, `...-create.sh`: CREATE CHARACTERS, a new human preserver, DONE): CHOOSE A SPELL at LEVEL
  1 with **17**: the 12 of 1st level and the five (the list 0-11, 321-325); one clicked (Fogbolt, +3Fh 40h),
  three of the game's; the next window LEVEL 2 with 13 + **Cat's Grace** (320); Grace clicked (+3Fh 50h,
  `cr_due` [0, 2, 2, 1]); EXIT, "YOU HAVEN'T CHOSEN", EXIT: CR_FILL gave the rest (3 + Fogbolt of 1st, 2 +
  Grace of 2nd, 2 of 3rd, 1 of 4th: 10 as the game gives); the powers' pop-up EXITed; View Character, +3Fh
  50h kept.
- **Erdlu Claw's 1d6+1** (l5, `...-claw.sh`): Claw dropped on Thy'rokh's portrait (effect 114); his chatkcha
  and gythka moved to his pack **in the inventory screen** (a slot edit in memory alone, `...-scroll.py slot`,
  left a member with nothing in hand unable to attack at all: a barred sword over a foe, for Ar'anda and him
  both; through the game's own move the foe turned red). His inventory DAM: "<4x1D6+8>" and "<1D4+8>". Then:
  "Thy'rokh attacks Draxan#23 with a claw (1d6+1) ... THAC0 15, +3 STR, +1 Erdlu Claw = 11", "hits Draxan#23
  for 9: 1d6 = [1] +1 claw +7 STR 19" (14 for a 6); four claws so, then "with its bite (1d4+1): ... THAC0 15,
  +3 STR = 12": **the bite has no +1** (`ns_claws` 5, `ns_swings` 2). In l4, before the frame fix, the claws
  had no +1 (`ns_swings` 0): NS_SWING read [BP-20h] in the hit routine's frame, not the set-up's (part 2's
  "+1 on the bite" was that).
- **Fogbolt** (l5) on Draxan#23 (failed save; a first cast on #21 was saved, no effect): "Draxan attacks
  Thy'rokh#2 with Stone Lotulis (2d4): ... needs 15+ ... THAC0 13, +3 STR, -2 stone, -3 Fogbolt = 15".
- **Spook** (l5, the SPELLS_END fix): "Draxan#21's saving throw vs Spook from Ar'Anda#0 (spell): d20 = 6 -3
  Spook, the caster's levels +2 WIS 16 = 5, needs 11 (45% to save) -> failed" (`ns_spooks` 1). Her level-1
  slots for it given back in memory (DS:446Ah, a test edit).
- **Control** (static: `ravager.write_patched` with `skip` the five new patches, ns_cmp_77cf9, ns_cmp_9a7d4,
  ns_cmp_9a9c5, ns_scroll, ns_learn): the program holds the game's bytes at each; with them, `cd f5 8c` and
  `cd f5 94/95` + NOPs.
- **Memory** (`dosmem.py`, in the fight): DSCLOG2's upper block 52640 bytes, 102816 free after it; the
  conventional largest piece 79552.

Lessons: the screen is 640x480 here (the run's window): a grab's game y is the pixel's / 2.4, x / 2. Count a
CHOOSE A SPELL icon from the screen, not the list: creation's six-a-row page isn't in list order. The aim
pointer's place is ravclick's; hover with `none` and look for the red before pressing. `ravfight.py cast`
didn't aim from the USE screen (the panel's drop at (230,110), then a hovered figure, did). C opens USE on the
member's turn; (22,17) opened the inventory there. No water seen (Tyr's ambush street).

## Not done

- No INT roll for a new spell's spellbook (SCROLL_LEARN's is the bitset's), and no dice-log line for it.
- Erdlu Claw's "+1 magical weapon" (SL's NS_FIST) isn't ported.
- The sequel's shops and loot have no scrolls of the new spells.
