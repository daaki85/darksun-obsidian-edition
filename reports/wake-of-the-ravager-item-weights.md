# Wake of the Ravager's items with weights: the plan

Daaki (2026-11-26): "I think we can give weight to Ravager items." A study and a plan, nothing built
yet. Measured on the GOG releases of both games (Shattered Lands, SL; Wake of the Ravager, WotR) in
`$PLAYTEST_WORK/inst` and `$PLAYTEST_WORK/rav`, read only. The code was read in each `DSUN.EXE`
(capstone, 16-bit) and in each program's start-up image with every overlay loaded (Dark Sun
Recompiled's `tools/build_image.py`, its `layout.json` to follow far calls through the overlay
stubs). Addresses are `DSUN.EXE` file offsets, as the docs give them.

## In short

- **The sequel still has all of SL's code that reads weight; only its data is missing.** Its item
  types keep SL's weight field (one byte at +2 where SL has a word at +4), but 71 of its 102 types
  hold 0 there. SSI filled in the other 31, some oddly (a two-handed sword weighs 20, a crystal sword 10).
- **What weight does in both games** (the same routines, at other addresses in each):
  1. **"Too heavy a load to carry"**: the check is there (an item put on a member against the STR
     table's *maximum press*, AD&D's table in tenths of a pound), but **it never refuses, in either
     game**: the total it adds up is not the items' weight and comes to 0 (played, section 8).
  2. **"Cannot use two heavy weapons"**: two weapons over 30 (3 lb) can't be held together.
  3. **Backstab**: only with a weapon of 40 or less.
  4. **"HEAVY"** in the item box, for a one-handed weapon over 30.
  5. **Equipping a monster or NPC**: the routine that hands a creature its gear avoids two heavy
     weapons.
  6. The Loader: **picking pockets** (10 or less) and the dice log's **backstab chance** (40 or less).
- **Nothing slows a loaded character down, in either game.** SL has the routine for it (Move cut in
  proportion between the STR table's two columns), but nothing calls it. The sequel dropped it.
  Weights change no movement, and "encumbered and slowed in combat" in both manuals never happened.
- **Data only, no rule port**: the weights go into the Loader's copy of `OBJEX.GFF` (`OBJEX2.GFF`,
  `ravager.objects_fixed`), as the mod's 33 types already do. No DSCLOG2 site is needed.
- **Saves need nothing.** The type table is read from `OBJEX.GFF` as a game starts or loads.
  Neither `CHARSAVE.GFF` nor `SAVEnn` holds it, and an item records only its type's number.
- **Pick pockets** then goes by real weights. `rav_pocket_sized` keeps its kind test only for the
  types still at 0 (furniture, doors, monsters' weapons).
- **Size: small.** About a day: a weight table and one more step in the existing OBJEX copy, tests,
  a short in-game probe and play check, and the docs.
- **Daaki's choices** (below): fill the zeros only, or also correct SSI's odd light weights (B,
  recommended); no slowing (recommended), or a new slowing rule for both games. SL's leather chest
  armour weighs 75 lb, but SL's armour weights don't follow the PHB closely enough to call it a slip,
  so it is left alone (section 1).
- **Built** (2026-11-26) with B, no slowing, always on (`RAV_SKIP=weights` for a control run):
  section 8. One new choice came from the play: a real carry limit (choice 5).

## 1. Where each game keeps an item type's weight

| | Shattered Lands | Wake of the Ravager |
|---|---|---|
| File, chunk | `GPLDATA.GFF` `IT1R` 1: 115 types of 20 bytes (the Loader's copy adds its own after them: `itemtables.py`) | `OBJEX.GFF` `ALL ` 4: 102 types of 15 bytes (the Loader's `OBJEX2.GFF` adds the mod's 33 as 102-134: `ravager.mod_types_table`) |
| The weight | **word at +04h**, tenths of a pound (`pickpocket.TYPE_WEIGHT`) | **byte at +02h**, the same units (`ravlog.TYPE_FIELDS` maps SL's +4 to it), so **255 at most** (25.5 lb) |
| In memory | far pointer DS:1669h, 14h a type | far pointer DS:19CDh, 0Fh a type |
| Other copies | none | each object's `RDFF` record holds its type's 15 bytes too (level 3, kind 4): all 1,216 equal `ALL 4` today. The weight checks read the table, so these only need to stay in step |

The sequel's one-byte field fits every weight below. SL's 750 for its leather chest armour would
not fit (the end of section 1).

The mod's own types in the sequel (102-145, SL's 115-158, `npcitems.TYPES` through
`ravager.wotr_type`; 2026-11-27: 102-134 before, the metal, obsidian and bone Ravager weapons going
across as the sequel's own kinds) and SL's bone long sword after them (146, `ravager.SL_EXTRA_TYPES`)
already carry SL's weights: the bone great sword 110 in both games (the user's, 2026-11-27). So do the transfer's added items
(`ravitems.make` copies the type record). The heavy-weapon check already runs for those.

### The weight table

Each sequel type: what it is, its weight now, the SL type that `ITEMS.BIN` (the transfer's pairs)
most gives in its place and that type's weight, and the two proposals:

- **A** fills the zeros only and keeps SSI's own weights.
- **B** also brings SSI's oddly light ones into line with SL and with the Loader's backported
  sequel weapons (`npcitems.TYPES` 148-153).

For a type with no SL match, the weight comes from the nearest SL item, or from the AD&D PHB
weight. Types nobody carries (furniture, doors, bodies, monsters' and spells' missiles) are
left as they are. "Material" is the type's +4 low nibble (0 wood, 1 bone, 2 stone, 3 obsidian,
4 metal, 5 leather). The item names are the sequel's objects' in `OBJEX.GFF` and its regions.

| Type | The sequel's items of it | Kind, slot, material, damage | Now | SL by ITEMS.BIN (weight) | A | B | Basis |
|---:|---|---|---:|---|---:|---:|---|
| 0 | (none) | missile, waist, wood, 1d6+1 | 0 | - | 0 | 0 | left: no item; a monster's or a spell's missile |
| 1 | Brigandine Armor | thing, arms, bone | 0 | 13 (86) | 86 | 86 | SL 13 brigandine arm |
| 2 | Chain Armor, Promere's Armor, Scale Armor | thing, arms, metal | 0 | 58 (50); 26 (100); 54 (50) | 50 | 50 | SL 58 chain arm |
| 3 | Armor | thing, arms, leather | 0 | 7 (36) | 36 | 36 | SL 7 leather arm |
| 4 | Ring Armor | thing, arms, bone | 0 | 10 (74) | 74 | 74 | SL 10 ring arm |
| 5 | Scale Armor | thing, arms, bone | 0 | 55 (50) | 50 | 50 | SL 55 scale arm |
| 6 | Arrow, Heartseeker | missile, ammo, wood, 1d6 | 0 | 62 (10) | 10 | 10 | SL 62 arrows |
| 7 | Arrow of harm, Arrow of binding | missile, ammo, wood, 1d6 | 0 | - | 10 | 10 | SL 62 arrows |
| 8 | Axe | melee, hand, metal, 1d8 | 0 | 22 (70) | 70 | 70 | SL 22 metal axe |
| 9 | Coins, Key, Fruit, Orb | thing, - | 10 | 60 (1) | 10 | 10 | the sequel's own, kept |
| 10 | Bag | thing, - | 0 | 66 (10) | 10 | 10 | SL 66 bag |
| 11 | (none) | melee, hand, metal, 1d8 | 0 | - | 0 | 0 | left: no item of it |
| 12 | Pants, Belt | thing, waist | 0 | 42 (1) | 1 | 1 | SL 42 belt |
| 13 | Bloodletter | melee, hand, metal, 1d8 | 0 | - | 40 | 40 | metal long sword (SL 63) |
| 14 | Gem, Bracelet, Berries, Voucher | thing, - | 1 | 60 (1); 87 (1) | 1 | 1 | the sequel's own, kept |
| 15 | Belt | thing, waist | 1 | - | 1 | 1 | the sequel's own, kept |
| 16 | Longsword | melee, hand, wood, 1d8+1 | 40 | 41 (40) | 40 | 40 | the sequel's own, kept |
| 17 | (none) | thing, feet | 0 | - | 1 | 1 | SL 68 boots |
| 18 | Bow, Bow/Accuracy | bow, missile, wood, 1d8, 2-handed | 0 | 1 (30); 69 (30) | 30 | 30 | SL 1 bow |
| 19 | Chest | thing, - | 0 | 49 (300); 14 (86); 108 (2000) | 0 | 0 | left: chest: furniture, not carried |
| 20 | Bracer | thing, arms, leather | 1 | - | 1 | 1 | the sequel's own, kept |
| 21 | Broken Weapon | melee, hand, wood, 1d1 | 0 | - | 5 | 5 | SL 107 broken weapon |
| 22 | (none) | melee, hand, wood, 2d6-2, 2-handed | 0 | - | 0 | 0 | left: no item; a monster's (2d6-2) |
| 23 | (none) | missile, missile, wood, 2d10 | 0 | - | 0 | 0 | left: no item; a spell's or monster's missile |
| 24 | Cahulaks | melee, hand, bone, 1d6, 2-handed | 0 | 21 (120) | 120 | 120 | SL 21 cahulaks |
| 25 | Chatchka | missile, missile, obsidian, 1d6+2 | 0 | 48 (5); 70 (1) | 5 | 5 | SL 48 chatkcha |
| 26 | Robes, Vest, Shirt | thing, chest, wood | 1 | 65 (10) | 1 | 1 | the sequel's own, kept |
| 27 | (none) | melee, hand, wood, 1d2 | 1 | - | 1 | 1 | left: no item; a fist or claw (1d2) |
| 28 | Cloak, StalkerCloak | thing, cloak | 0 | 65 (10); 38 (10) | 10 | 10 | SL 65 cloak |
| 29 | Club, Beast club | melee, hand, wood, 1d6 | 0 | 18 (30) | 30 | 30 | SL 18 club |
| 30 | Brigandine Armor | thing, chest, bone | 0 | 12 (175); 90 (50); 89 (50) | 175 | 175 | SL 12 brigandine chest |
| 31 | Chain Armor, Promere's Armor, Scale Armor | thing, chest, metal | 75 | 57 (200); 88 (200) | 75 | 200 | the sequel's own, kept; B: SL 57 chain chest |
| 32 | Armor | thing, chest, leather | 0 | 4 (50); 6 (750); 35 (1) | 96 | 96 | SL 6's 750 doesn't fit the byte: 96, so that with the arm and leg pieces (36, 18) the suit weighs the PHB's 15 lb |
| 33 | Ring Armor | thing, chest, bone | 0 | 9 (150) | 150 | 150 | SL 9 ring chest |
| 34 | Scale Armor | thing, chest, bone | 0 | 15 (200) | 200 | 200 | SL 15 scale chest |
| 35 | Crystal sword | melee, hand, wood, 1d10, 2-handed | 10 | - | 10 | 150 | the sequel's own, kept; B: a two-handed sword, as 101 |
| 36 | (none) | missile, missile, wood, 1d6 | 0 | - | 0 | 0 | left: no item; a missile |
| 37 | Dagger | melee, hand, stone, 1d4 | 10 | 94 (10); 84 (10) | 10 | 10 | the sequel's own, kept |
| 38 | Darts | thrown, missile, wood, 1d2 | 0 | - | 5 | 5 | PHB dart 1/2 lb; the Loader's darts (SL 153) 5 |
| 39 | Double Spear | melee, hand, wood, 1d6, 2-handed | 50 | 19 (150) | 50 | 60 | the sequel's own, kept; B: the Loader's double spear (SL 150) 60 |
| 40 | (none) | melee, hand, stone, 1d4 | 10 | - | 10 | 10 | the sequel's own, kept |
| 41 | Door | thing, - | 0 | - | 0 | 0 | left: door |
| 42 | Gloves | melee, hand, wood, 1d6+3 | 0 | - | 1 | 1 | SL 37 gloves |
| 43 | Darts | thrown, missile, stone, 1d4 | 0 | - | 5 | 5 | as 38 |
| 44 | Boots, Sandals | thing, feet | 0 | 68 (1) | 1 | 1 | SL 68 boots |
| 45 | Ring | thing, finger | 1 | 102 (1); 75 (1); 52 (1) | 1 | 1 | the sequel's own, kept |
| 46 | Fire ruby, Amulet | thing, neck | 0 | - | 1 | 1 | SL 36 necklace |
| 47 | Flameblade | melee, hand, metal, 1d4+4 | 0 | - | 40 | 40 | SL's Flame Blade 40 |
| 48 | Axe | melee, arms, obsidian, 1d6 | 10 | - | 10 | 30 | the sequel's own, kept; B: SL 50 obsidian axe 30 |
| 49 | Boots, Barrel, Bust, Bookcase | thing, - | 10 | - | 10 | 10 | the sequel's own, kept |
| 50 | Rock, Platform, Plant, Switch | thing, - | 4 | - | 4 | 4 | the sequel's own, kept |
| 51 | Great Axe | melee, hand, obsidian, 1d10, 2-handed | 0 | 2 (70) | 70 | 70 | SL 2 great axe |
| 52 | Gythka | melee, hand, bone, 2d4, 2-handed | 0 | 44 (120) | 120 | 120 | SL 44 gythka |
| 53 | Gloves, Cosmic scepter, Gem | thing, hand | 1 | 37 (1) | 1 | 1 | the sequel's own, kept |
| 54 | Hat, Ioun stone, Circlet of clarity | thing, head | 1 | - | 1 | 1 | the sequel's own, kept |
| 55 | Helm, Hat | thing, head | 0 | 5 (15); 109 (50) | 15 | 15 | SL 5 helm |
| 56 | Helm of domination, Helm | thing, head | 0 | - | 15 | 15 | SL 5 helm |
| 57 | (none) | melee, hand, bone, 1d8 | 0 | - | 20 | 20 | bone long sword (SL 81) |
| 58 | Body, Bones, Chest, Snake | thing, - | 0 | - | 0 | 0 | left: bodies, chests, furniture |
| 59 | Javelin, Javelin lightning | missile, missile, obsidian, 1d4 | 0 | - | 20 | 20 | PHB javelin 2 lb; the Loader's javelin (SL 152) 20 |
| 60 | (none) | thing, legs, wood | 1 | - | 1 | 1 | the sequel's own, kept |
| 61 | Lotulis | melee, hand, stone, 2d4, 2-handed | 20 | - | 20 | 100 | the sequel's own, kept; B: the Loader's lotulis (SL 149) 100 |
| 62 | Brigandine Armor | thing, legs, bone | 0 | - | 86 | 86 | SL 14 brigandine legs |
| 63 | Chain Armor, Scale Armor | thing, legs, metal | 0 | 59 (50); 25 (100); 24 (50) | 50 | 50 | SL 59 chain legs |
| 64 | Armor | thing, legs, leather | 0 | 8 (18) | 18 | 18 | SL 8 leather legs |
| 65 | Ring Armor | thing, legs, bone | 0 | 11 (74) | 74 | 74 | SL 11 ring legs |
| 66 | Ring Armor | thing, legs, bone | 0 | 56 (50) | 74 | 74 | SL 11 ring legs (ITEMS.BIN pairs it with SL 56, 50) |
| 67 | Mace | melee, hand, bone, 1d6+1 | 0 | 20 (100) | 100 | 100 | SL 20 mace |
| 68 | Jasmine | melee, hand, metal, 1d6+1 | 0 | - | 100 | 100 | SL 20 mace |
| 69 | Magma blade | melee, hand, metal, 1d8 | 0 | - | 40 | 40 | metal long sword (SL 63) |
| 70 | Necklace | thing, neck | 0 | 101 (1); 36 (1); 87 (1) | 1 | 1 | SL 36/101 necklace |
| 71 | Net | thrown, missile, wood, 0d0 | 10 | - | 10 | 10 | the sequel's own, kept |
| 72 | Dagger | melee, hand, obsidian, 1d4 | 0 | 17 (10); 33 (10) | 10 | 10 | SL 17 dagger |
| 73 | Longsword, Dragonsbane | melee, hand, obsidian, 1d8 | 0 | 81 (20); 45 (30); 47 (40) | 30 | 30 | SL 45 obsidian long sword |
| 74 | Mace | melee, hand, obsidian, 1d6+1 | 100 | 46 (100) | 100 | 100 | the sequel's own, kept |
| 75 | (none) | thing, - | 0 | - | 0 | 0 | left: no item |
| 76 | Shutters, Campfire | thing, - | 0 | - | 0 | 0 | left: shutters, campfire |
| 77 | One-use Scroll, Spellbook, Rod, Deck of illusions | thing, - | 0 | 96 (1); 74 (1) | 1 | 1 | SL 96 scroll |
| 78 | Bracelet, Psionic powerstone | thing, - | 0 | 99 (1) | 1 | 1 | SL 99 psionic item |
| 79 | Pick | melee, hand, stone, 1d4+1, 2-handed | 40 | 112 (40); 60 (1) | 40 | 40 | the sequel's own, kept |
| 80 | Polearm | melee, hand, bone, 1d10, 2-handed | 0 | 19 (150) | 150 | 150 | SL 19 polearm |
| 81 | Promere hammer | melee, hand, wood, 1d10, 2-handed | 0 | - | 100 | 100 | PHB war hammer/maul; SL's mace 100 |
| 82 | (none) | thing, arms, metal | 10 | - | 10 | 10 | the sequel's own, kept |
| 83 | (none) | thing, chest, metal | 10 | - | 10 | 10 | the sequel's own, kept |
| 84 | (none) | thing, legs, metal | 10 | - | 10 | 10 | the sequel's own, kept |
| 85 | Quarterstaff, Staff paralysis | melee, hand, wood, 1d6, 2-handed | 0 | 3 (40); 80 (40) | 40 | 40 | SL 3 quarterstaff |
| 86 | Gloves | melee, hand, wood, 1d6+2 | 1 | 113 (1) | 1 | 1 | the sequel's own, kept |
| 87 | Rainbow | missile, missile, wood, 1d8, 2-handed | 0 | - | 30 | 30 | SL 1 bow (the spell's) |
| 88 | (none) | thing, finger | 0 | - | 1 | 1 | SL 102 ring |
| 89 | Toothed Club | melee, hand, wood, 1d8+2 | 10 | - | 10 | 30 | the sequel's own, kept; B: SL 18 club 30 |
| 90 | Shillelagh | melee, hand, wood, 2d4 | 0 | - | 10 | 10 | SL's Shillelagh 10 |
| 91 | Shield, El's Shield | shield, hand, leather | 0 | 83 (50) | 50 | 50 | SL 4 shield |
| 92 | Shield | shield, hand, wood | 0 | 16 (50) | 50 | 50 | SL 16 shield |
| 93 | Sling | missile, missile, wood, 1d4 | 0 | 64 (5) | 5 | 5 | SL 64 sling |
| 94 | Rock | melee, hand, stone, 1d4 | 10 | - | 10 | 10 | the sequel's own, kept |
| 95 | Spirit hammer | missile, hand, wood, 1d4+1 | 0 | - | 40 | 40 | SL's Spiritual Hammer 40 |
| 96 | (none) | thing, - | 0 | - | 1 | 1 | small thing |
| 97 | Longsword, El's Drinker, Life Stealer, Magic Weapon | melee, hand, metal, 1d8 | 0 | 63 (40); 98 (30); 85 (40) | 40 | 40 | SL 63 metal long sword |
| 98 | Staff Sling | missile, missile, leather, 1d4, 2-handed | 0 | 0 (20) | 20 | 20 | SL 0 staff sling |
| 99 | Dagger | thrown, missile, metal, 1d4 | 1 | - | 1 | 10 | the sequel's own, kept; B: SL 17 dagger 10 |
| 100 | Trikal | melee, hand, wood, 1d10 | 0 | - | 80 | 80 | the Loader's trikal (SL 151) 80 |
| 101 | Twohand Sword | melee, hand, obsidian, 1d10, 2-handed | 20 | - | 20 | 150 | the sequel's own, kept; B: the Loader's two-handed sword (SL 148) 150; PHB 15 lb |

What A and B change at the rule thresholds (one-handed over 30 is HEAVY and can't be paired with
another heavy weapon; over 40 can't backstab; over 10 can't be pickpocketed):

- **Both**: the metal long swords (13, 69, 97), Flameblade (47) and Spirit hammer (95) at 40 are
  HEAVY but can still backstab. The metal axe (8, 70), the maces (67, 68, 74, 100), the trikal (80)
  and the two-handers (great axe 70, gythka 120, polearm 150, Promere hammer 100, quarterstaff 40)
  can't backstab. The obsidian long sword (73) at 30 and the clubs, daggers and bone weapons stay
  light.
- **B only**: the Twohand Sword (101) and the Crystal sword (35) at 150 and the Lotulis (61) at 100
  can't backstab. Under A, at 20 and 10, they can, and the Crystal sword can even be lifted from a
  pocket: that is so today already, since it is one of SSI's non-zero weights. The thrown
  Dagger (99) goes from 1 to 10 (still pocket-sized). The rest of B changes no check (the load check never refuses: section 2).

**SL's leather chest armour** (type 6) weighs 750 (75 lb), against 36 and 18 for the leather arm and
leg pieces. Before calling it a slip, here are SL's armour weights (GPLDATA's IT1R, the Loader's copy
as the game's) set beside the AD&D PHB's. SL splits a suit into chest, arm and leg pieces. In
tenths of a pound, the unit fits every whole suit:

| Armour | SL's types | Chest + arms + legs | Suit | PHB | Fits? |
|---|---|---|---:|---:|---|
| Leather | 6, 7, 8 | 750 + 36 + 18 | 80.4 lb | 15 lb | no: five times over |
| Ring mail | 9, 10, 11 | 150 + 74 + 74 | 29.8 lb | 30 lb | yes |
| Brigandine | 12, 13, 14 | 175 + 86 + 86 | 34.7 lb | 35 lb | yes |
| Scale mail | 15, 55, 56 | 200 + 50 + 50 | 30 lb | 40 lb | no: 10 lb light |
| Chain mail | 57, 58, 59 | 200 + 50 + 50 | 30 lb | 40 lb | no: 10 lb light |
| Studded leather, banded, plate | none in SL | | | 25, 35, 50 lb | (the Loader's plate, npcitems 131-133: 250 + 75 + 75, 40 lb) |
| Shield | 4, 16 | 50 | 5 lb | 5 lb small, 10 medium | the small shield |
| Drake Shield | 34 | 100 | 10 lb | | |
| Helm | 5 | 15 | 1.5 lb | 5 lb (basinet) to 10 (great helm) | no: light |
| Drake Armor, Shimmer Armor | 79, 82 | 75 (a chest piece alone) | 7.5 lb | | |

Two suits match the PHB in that unit, but scale and chain are 10 lb light and the helm is light
too: SSI didn't follow the PHB throughout. So leather is **left as it is in SL** (no fix, no
GAME-BUGS row), and noted here only. In the sequel the byte can't hold 750, so its leather chest
(32) gets 96: with the arm and leg pieces the suit comes to the PHB's 15 lb.

## 2. What reads weight, in each program

| What | Shattered Lands | Wake of the Ravager | The sequel's data now |
|---|---|---|---|
| **Load check**, putting an item on a member (the inventory's routine, SL 6EF52h / WotR 7761Bh): the carried total vs the STR table's maximum press; refused with "Too heavy a load to carry" | 6F248h: the total of GPL field 6 over the member and what it holds (resident D9A4h), less sheet +0Eh, vs CAE7Fh(member, 1); the message DS:19B0h | 77893h: the total of field 59h (resident FF21h), with nothing taken off, vs 20186h(member, 1); the message DS:1BF3h at 778DBh | runs, but sums a field items don't have: never refuses (section 2) |
| **The STR table**: weight allowance and maximum press, tenths of a pound, by STR 0-25 (AD&D's, 18 taken as 185/330) | DS:0740h, read by CAE7Fh (overlay 10, file 5E9BFh) | DS:07B0h, the same values, read by 20186h (file 1D286h) | the same |
| **Slowed by the load**: Move x (press − excess) / (press − allowance) | 5E8FBh (overlay 10): **never called** (no far call, stub call or near call to it) | **gone** | (none) |
| **A round's movement** | 5754Ah: creature +1Bh x 10, no load in it | the same | (none) |
| **Two heavy weapons** in the hands: both over 30, "Cannot use two heavy weapons" | 6F38Fh / 6F3A1h (DS:19FBh) | 779CEh / 779E0h (DS:1C3Eh) | 0 passes: two metal long swords or maces go together today |
| **Backstab**: weapon 40 or less | 5832Eh | 5C978h | 0 passes: a polearm or great axe backstabs today |
| **"HEAVY"** in the item box: a one-handed weapon over 30 | 8C0B8h (DS:3481h) | 9A410h (DS:2F2Ch) | never shown for 0 |
| **A weapon's weight** (0 if not a melee weapon), used by the routine that equips a creature: no two heavy weapons | 5EAFEh, called at 5AC61h / 5AD92h | 1D3C9h, called at 5F937h / 5FA63h | the same |
| **Too big to carry** | type +08h bits 10h/20h, not weight | type +04h | unchanged |
| **The Loader**: pick pockets (`pickpocket.pocket_sized`, 10 or less), the dice log's backstab chance (`hitchance.STAB_WEIGHT` 40) | the type's +4 | the same, through `ravlog.ReadOnlyGuest`'s SL view of the table, and `ravlog.rav_pocket_sized` while weights are 0 | kind test for 0 |

No screen shows a weight or a total in either game (no such string in either program). Shops
don't read weight. **The sequel's code is all there, fed zeros.** What wasn't kept is the slowing
routine, and SL never called its copy.

**The probe settled the load check: it never refuses, in either game.** The sequel's total sums
GPL field 59h, and field 59h's table (built at run time) has an entry only for the item-type class
(class 4, offset 2: the type's own weight byte). An item is class 1, whose offset for field 59h is
-1, so each item adds 0 and the total is 0 whatever the types weigh. SL's version sums field 6 and
also came to nothing. Both were played with a STR 1 member (a test edit, never saved): Cilla took
Gerakis's long sword in SL, and in the sequel a STR 1 member took 45 lb with the weights in. So
"Too heavy a load to carry" is never seen, and the weights don't change carrying.

## 3. What weights would change in play

- **Carrying**: nothing changes. The load check never refuses (section 2), in SL or the sequel, so
  no member is refused an item for its weight. A real carry limit would be a new rule for both
  games (choice 5).
- **No slowing** in fights or on the map: neither game has it.
- **Two weapons**: a member can no longer put two heavy weapons (over 30) in the hands, as in SL.
  Weapons already in the hands stay, and the refusal comes when one is taken out and put back.
  Gerakis's Dragonsbane +4 (73, 30) and Longsword +1 (97, 40) still go together. Any other
  two-weapon member of the pregenerated party should be looked at in the play check (Ar'anda's
  pair).
- **Backstab** loses the heavy weapons (above), as in SL. DSCLOG2's ported hiding-to-backstab
  goes by the game's own conditions, so it follows.
- **Rule port or data?** **Data only**, in the Loader's copied file. The sequel's routines are
  SL's and already read the field. A slowing rule (choice 2) would be a new rule port: a DSCLOG2
  site at the sequel's round movement, the counterpart of SL's 5754Ah, and a DSCLOG one for SL.

## 4. Saves

The weights are read from the type table at run time. The sequel reads `OBJEX.GFF`'s `ALL 4` (the
Loader's `OBJEX2.GFF`) into memory as it starts and loads a game. A save made with SSI's table
loaded with the mod's 135 types (`logs/2026-11-22-ravager-item-types.md`). An item record (17h
bytes) names its type by number. `CHARSAVE.GFF` and `SAVEnn.SAV` hold no type table (their chunks:
CHAR, CACT, GREQ, PREF, PSIN, PSST, SPST; SAVE, STXT, ETME). **No save conversion.** A game saved
with the weights and loaded without the Loader goes back to SSI's zeros.

The transfer's added objects (`RAVITEMS.GFF` in the mod's dos folder, built up by each transfer)
carry a copy of their type. The new step rewrites the type copies of every object in the Loader's
copy, those included, so old transfers need nothing either.

## 5. Picking pockets

`ravlog.rav_pocket_sized` (the fallback by kind while the sequel's types weigh 0) stays, but only
types left at 0 still reach it. Everything carried then goes by weight, as in SL
(`pickpocket.MAX_WEIGHT` 10): rings, gems, scrolls, daggers, darts, slings, arrows, a cloak, a
bag. Long swords, helms (15) and armour can't be lifted. Its comment and DEVELOPMENT-RULES'
paragraph get rewritten, and `test_ravpickpocket` gets a case for each path.

## 6. The build

1. **Probe first** (in the game, test edits only, never saved, `ravload.sh ravager-after-ambush`):
   a member's STR set low and an item moved onto them, to see "TOO HEAVY A LOAD TO CARRY" at the
   maximum press; then two type-97 long swords: "CANNOT USE TWO HEAVY WEAPONS". (Done: the first
   never refuses, the second does; section 8.)
2. **The data**: `ravager.RAV_WEIGHTS` (type: weight, the table's A or B column) written by
   `objects_fixed` into `ALL 4`'s first 102 types at +2, and into each object's `RDFF` type copy
   (level 3, kind 4) of those types. Each original byte is checked against SSI's first (as the
   patches check theirs), and `RAV_SKIP=weights` leaves the step out for a control run.
3. **Pick pockets**: `rav_pocket_sized`'s comment, and the test cases.
4. **Tests**: the table applied, SSI's bytes guarded, the copies in step, every weight 255 or less,
   `test_ravpickpocket`.
5. **Play check**: a heavy load refused at a weak member's limit and taken by a strong one (moot:
   the check never refuses); two
   metal long swords refused; a thief's backstab with a polearm refused and with a dagger made; a
   long sword not lifted from a pocket and a ring lifted; the pregenerated party's own hands
   checked. Test log, and RESEARCH.md's Wake of the Ravager section updated.
6. **Docs**: FEATURES (the Wake of the Ravager part), DEVELOPMENT-RULES (weights in the sequel),
   HOW-THE-GAME-WORKS (the load check and the STR table, true of SL too and not written down
   yet), the CHANGELOG, and a row in the port plan.

**Size**: about 60 lines of code and data, 80 of tests, the docs; a day's work with the probe
and the play check. No DSCLOG2 code, no saves touched.

## 7. Daaki's choices

1. **A or B**: fill only SSI's zeros (A), or also correct its oddly light weights (B: the
   two-handed sword, crystal sword and lotulis can't backstab or be pickpocketed, as in SL and as
   the Loader's own copies of those weapons in SL weigh). **Recommended: B**, so a weapon weighs
   the same in both games.
2. **Slowing a loaded character**: neither game ever did it, whatever the manuals say. **Recommended:
   no** (weights only, as SL plays). Slowing would be a new rule for both games, for later and
   with an Options switch.
3. **SL's 75 lb leather chest armour**: left as it is (the comparison in section 1: SL's armour
   weights aren't the PHB's throughout, so this one isn't plainly a slip).
4. **Always on, or a switch**: **recommended: always on**, a data fix that makes the sequel's
   checks work as SL's do (with `RAV_SKIP=weights` for testing). Built so.
5. **A real carry limit** (new, from the play): neither game ever refused a load, as the check
   sums a field items don't have. Making it work would be a rule port for both games (a DSCLOG
   site in SL's 6F248h and a DSCLOG2 one in the sequel's 77893h, summing the items' type weights
   against the maximum press), with an Options switch. **Recommended: not now**: both games were
   played and balanced without it, and the weights already do their other jobs.

## 8. Built (2026-11-26)

Option B, no slowing rule, always on, `RAV_SKIP=weights` for a control run. Code:
`ravager.RAV_WEIGHTS`, `weighted`, `weighted_table`, `weighted_objects` (the 102 types of `ALL 4`
at +2 and every object's `RDFF` type copy, each byte checked against SSI's first), called from
`objects_fixed`; `ravlog.rav_pocket_sized`'s comment; tests in `test_ravager`, `test_ravitems`,
`test_ravpickpocket`; `playtest/ravweights.py` reads the weights and a party's loads from the
running game. The play (a throwaway copy, `ravager-after-ambush`, test edits never saved; the
test log `playtest/logs/2026-11-26-ravager-item-weights.md`):

| Check | Seen |
|---|---|
| The weights in memory | `ravweights.py --types`: all 102 as `RAV_WEIGHTS` |
| Two heavy weapons | a second long sword (97, 40) into Ar'Anda's left hand: "CANNOT USE TWO HEAVY WEAPONS"; with `RAV_SKIP=weights`, "CANNOT USE THIS ITEM" (a later check, as the swords weigh 0 then) |
| The party's own pairs | Gerakis's Dragonsbane (30) and Longsword (40), and Ar'Anda's dagger and long sword, went back into their hands |
| "HEAVY" in the item box | shown for the long sword |
| Pick pockets | with `RAV_PICK_ROLL=1` on the Caravan Master: 20 coins lifted, not his Obsidian Longsword (30) |
| Heavy load | never refused, in either game (section 2), so nothing to see |
| Backstab with a heavy weapon | **not played**: the Tyr thieves fight with Ar'Anda's weapon set to a polearm (type 8, 70) in memory went badly and she couldn't hide. Verified from the program instead: 5C978h reads the type's byte at +2, which holds 70 in memory |

SL's leather chest armour is left as it is (section 1), so there is no SL change and no GAME-BUGS
entry.
