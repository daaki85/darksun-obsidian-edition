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

## Not done

- Learning them in the sequel: the level-up CHOOSE A SPELL screen and scrolls (the item powers past 320 are
  taken as no spell: 77CF9h, 9A7D4h, 9A9C5h compare with 140h), so they come only with a transferred
  character (or a test edit); creation's first spells neither.
- Erdlu Claw's 1d6+1 not seen in play; its +1 to hit is on any unarmed attack (SL's on the first set only),
  and its "+1 magical weapon" (SL's NS_FIST) isn't ported.
- The dice log's to-hit line doesn't name Fogbolt ("in bonuses").
