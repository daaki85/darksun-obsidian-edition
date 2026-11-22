# The party transfer to Wake of the Ravager: every item across, every effect working

*Design, 2026-11-22. Branch `claude/ravager-party-transfer`. The first part is done:
`dsloader/ravtransfer.py` is SSI's CHARTRAN in Python. It writes the same bytes as CHARTRAN on all 15
Shattered Lands saves in `playtest/saves` and 20 made-up ones (logs/2026-11-22-ravager-transfer-format.md).
This page plans what the mod adds on top.*

Daaki's asks (2026-11-22):

- every item the party carries comes across;
- the mod's own effects work in the sequel too, not just the item;
- the party ages by a random gap of 3-12 months, rolled once. Each member ages a year with a chance
  of months/12, and the age rule's usual effects apply.

## What CHARTRAN loses today

Every item without an ITEMS.BIN pair becomes a money bag, object 900. On the kit's saves that is
about one item in five:

| save | items | money bags |
|---|---|---|
| trap-user | 50 | 8 |
| selling-junk-user | 44 | 10 |
| rest-no-call-user | 26 | 8 |

Across all 15 saves, the items that turn into money bags are of three kinds:

- **The mod's items.** These are its 33 item types (SL type 115 on) and the objects it adds (2419-2678,
  65 named in `icons.ICONS`). Examples: Short Sword, Shadowseeker, Inixhide, the Rings and Cloak of
  Protection, Ashen Robe, Hayneedle, Bone Helm, Shocking Arrows.
- **SL's own quest and story items** (type 60): Slavepen key, Pot of Water, Empty Water Pot, Guava,
  the Vulture, plus SL's two Bags, 1571 and 1572. ITEMS.BIN pairs those two bags with sequel objects
  that are only a picture.
- **SL's scrolls** (object 1440).

## How the items come across

1. **The mod's item types go into the sequel's type table. Done** (2026-11-22,
   playtest/logs/2026-11-22-ravager-item-types.md). The table turned out to be data: OBJEX.GFF's chunk
   ALL 4, 102 types, read into memory at the chunk's own length. The Loader's copy (D:\OBJEX2.GFF,
   opened by DSCLOG2 in place of OBJEX.GFF) has the mod's 33 types after them as 102-134, converted to
   15 bytes (`ravager.objects_fixed`). Seen in the game: an item given type 107 shows as an obsidian
   1d6 blade, and the control as the metal 1d8 longsword it was.
2. **Each mod item gets a sequel object.** It goes in the Loader's copy of OBJEX.GFF, in the free ids
   14000-29999:
   - its RDFF item record is built from SL's, with the type, plus, power and name;
   - its name is one of DSCLOG2's names past the game's 256 (done 2026-11-22: the game's list is full
     and can't grow, so the helper answers the game's 7 reads of it for numbers 256-415);
   - its icon is copied from the player's own SL files at the Loader's run, as the mod's icons are now.
     Nothing from the games is committed.

   The transfer then maps each such SL object to its new object instead of the money bag. If a mod item
   is a sequel weapon with a plus (a gythka, cahulaks, chatkcha, club, pick, polearm, bow or staff sling),
   it takes the sequel's own type, with the mod's name and plus.
3. **SL's quest items become keepsakes.** They are carried and sellable, and they do nothing in the
   sequel's story. They take the sequel's plain item type 9 (bag, amulet, barrel...) with SL's picture
   and name. SL's two Bags take the sequel's own bag object, and they keep what they hold.
4. **Scrolls** keep their spell where the sequel has it (the spell map is `ravtransfer.spell_place`). A
   scroll of a dropped spell becomes a keepsake. **Done** (2026-11-22, `ravtransfer.Sequel.scrolls`):
   Kalzith's Shield scroll comes across as the sequel's One-use Scroll of Shield. Learning from a
   transferred scroll is not seen yet (playtest/logs/2026-11-22-ravager-transfer-items.md).
5. **Spell-made weapons** (Shillelagh, Flame Blade, Spiritual Hammer) are left behind. Their spell is
   over. **Done** (2026-11-22, `ravtransfer.SPELL_MADE`: the list closes over them, the report names
   them; tests only, as no kit save carries one).
6. **Roster slots:** CHARTRAN overwrites slots 32-35 without asking. The Loader keeps a backup of the
   player's CHARSAVE.GFF (CHARSAVE.GFF.BAK, done). **Done** (2026-11-22, `ravtransfer.places`): the
   roster is CHAR 32-39, a place listed while its CACT isn't 0 (seen in the game, and the game's DELETE
   sets it to 0). A member takes its earlier copy's place, else the lowest free one; with too few free,
   the transfer stops and asks the player to delete characters in the sequel.
7. **Aging:** the months are rolled once per transfer. Each member gains a year with a chance of
   months/12, through the Loader's age pass (RavDiceLog._aging_pass, age at sheet +41h). **Done**
   (2026-11-22, `ravtransfer.roll_gap`, `gap_years`, `aged`): SL's age (sheet +17h) comes across to
   +41h, which CHARTRAN left 0 (the Loader then gave a new random age); a year added changes the scores
   at the categories reached; a year that would reach the race's most isn't added. Seen in the game:
   Cenna 39 to 40, Cromwell 23 to 24.

## The mod's effects, item by item

Each effect is ported to DSCLOG2 in the same way as the rules (a SITE byte each, played in the sequel,
logged). The groups are listed in the order of the build.

| group | items | what makes it work in the sequel |
|---|---|---|
| A. Stats only (type, material, dice, plus) | Short Sword; the bone, obsidian and metal short swords, axes, daggers, maces, great axes, picks, polearms and cahulaks; Hayneedle, Stillwater, Drakejaw, Thornwall, Gythka +2, Kreenfang, Cahulaks +1, Galefang, Greenbright, Headsman, Linebreaker, Ironwhirl, Nightsliver, Mindshard, Glasshewer, Emberlash, Deepbiter, Gutterknot, Windlash, Skycutter, Dunesong, Sling +1; Inixhide, Warden's Arms and Legs, Bone Helm, Gutterward, Ironbulwark | steps 1-2 alone. The sequel's own rules already port polearm reach, stinkpots and helms (they read the type) |
| B. Who may wield it | the cleric-element and psionicist weapons (Hayneedle, Stillwater, Drakejaw, Galefang, Nightsliver, Mindshard, Glasshewer, Emberlash; the bone and obsidian types) | the mod's wield tables added to DSCLOG2's class-restriction sites (19-21) |
| C. On a hit | Searing Blade (Focus Heat, 2d6), Cahulaks +2 (Cause Light Wounds), Chill, Shocking, Vampiric and Burning Arrows | an item power the sequel casts on a hit, where it has the spell; else a DSCLOG2 site at the hit |
| D. While worn | Shadowseeker (sees the invisible), Warden's Chest (Resist Fire), Warden's Helm (Cloak of Bravery), Arrowbane (Protection from Normal Missiles), Sunking Crown (Protection from Evil) | the effect put on the wearer when the item is worn and taken off when it is removed (SL's worn-effect feature, ported) |
| E. AC and saves | Rings of Protection +1 (two), Cloak of Protection +1, Ashen Robe, Veiled Robe (with its extra wizard slots), Bracers of Defense, Golden Girdle of Urnst, Boots of Speed (with their Move) | DSCLOG2's PROBE_AC (done for helms) and the save site (done for Blur and Fire Shield), each with the mod's rule |
| F. Other rules | Girdle of Back Defense (no rear bonus, no backstab), Boots and Cloak of Elvenkind (silent, hidden), Amulet of Magic Resistance (+15%) | the rear attack, the thief-skill site (done for class restrictions) and the magic resistance check |
| G. Used up | Tome of Understanding (+1 WIS), Kalzith's six scrolls | the sequel's scroll use, with the mod's two cases |

The display features (charges, material in the item box) are already ported. They show on all these
items once they have types.

## The build, in order

1. The type table: done (above). Still to see: a transferred Short Sword in a fight, with its dice
   in the dice log.
2. The objects, names and icons in the Loader's OBJEX and RESOURCE copies. The transfer maps to them.
   **Done for the mod's items and the keepsakes** (2026-11-22, playtest/logs/2026-11-22-ravager-transfer-items.md:
   Shocking Arrows, Ring of Protection +1, Bone Short Sword and Pot of Water in a transferred fighter's
   inventory, money bags in the control). Scrolls keep their spell; spell-made weapons are left behind.
3. Roster slots, aging, the Loader's button ("Take the party to Wake of the Ravager": pick an SL save,
   then a report of every item and what it became).
4. Groups B to G, one feature at a time, each played in the sequel with a control run (the rules' way:
   PLAYTESTING.md, ravhold.sh).
5. A play from an SL save to the sequel's party screen with the transferred party, and the docs and
   the PR.

Each step goes in the port plan's table (reports/wake-of-the-ravager-port-plan.md) as it lands.
