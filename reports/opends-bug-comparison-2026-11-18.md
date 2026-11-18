# Our fixed-bug list against OpenDS's catalogue (2026-11-18)

Every row of `obsidian-edition/GAME-BUGS.md` (66 rows, the games' own bugs the Edition fixes),
set against OpenDS at `fe35c52` (`docs/known-bugs.md`, `docs/ds1-sweep-triage-2026-10-07.md`,
`docs/community-crossread-2026-11-13.md`, `ds1-patch/`, `CREDITS.md`). The match is by my reading of
their docs, not a mechanical diff, and a row marked absent means I found no description of that bug there.

**Counts:** 11 rows OpenDS already has from us (relayed through yuan-ti, recorded there as
unverified); 11 are script repairs that are OpenDS's, yuan-ti's or both (or, for the Legcrusher and elven-leader rows,
ours where they have the row but no fix); 7 are the same bug as an open row of theirs, where we have a mechanism and
a fix they lack; **37 are absent from their catalogue**. The catalogue is theirs to keep, so
this is a list of what they might want, not a claim they are missing it.

## The seven that answer an open row of theirs (the most useful to send)

Addresses are from our DEVELOPMENT docs (file offsets in GOG 1.10's DSUN.EXE where marked "file"; the
others are segment:offset or overlay offsets as those docs write them). Re-check an address against the
image before sending it; I did not today.

- **Row 23, random monsters** (their 3.3(5) "random crashes: no static anchor"). REQUEST 8 at 80BE4h reads
  `MONR` 1 of `RESOURCE.GFF` (42-byte records, {region, 10 x {OJFF, strength}}); the slot search leaves SI one
  past the match, so `idiv word es:[bx+4]` at 80CD8h divides by the *next* slot's strength: 0 after the last
  slot of the records with nine or seven, in regions 6, 13, 14, 27, 39, 40, 44 and 255: "Divide error", the game
  ends. Our fix reads `[bx+0]`. (DEVELOPMENT-CONTENT, "Random monsters".) A real crash with an anchor.
- **Row 47, "Out of memory in OEOpenGraph"** (same row): the map needs a large block each time it comes back
  (after the USE screen, a talk, a menu) and has little more than that to spare in a long session. Another
  crash with an anchor (DEVELOPMENT-INTERNALS, "Room and memory").
- **Row 45, graphics disappearing** (their 2.2 "doorway / item graphics disappearance", deferred, and 3.3(1) the
  Gem Fields item ceiling): the game keeps every picture it loads in a table of **300 slots** and a store of a
  fixed **741,376 bytes**, appends a slot for each picture number it hasn't got and gives neither back until an
  area loads; past 300, new pictures go missing. SSI's note 2712 for Wake of the Ravager is the same engine.
  Their Gem Fields "3 gems" may be the same cause; we haven't tested that.
- **Row 32, stat-boost gear** (their 3.3(4), "grant keyed to possession, strip keyed to slot removal"): the
  mechanism is that the ability routine counts every listed item's score wherever it is carried: `mov
  al,es:[bx+0Fh]` at 7B8ABh. We make it count only an item in a worn slot. **Seen in play** (2026-11-01, dice log:
  DEX 15 -> 17 on putting a sling with +2 DEX in the worn missile slot, back to 15 in the backpack): the one
  fix of the seven with a play log.
- **Row 33, the gladiator's AC** (their 3.4 "engine recompute 0x4E0:0x7F / ovr46 family"): the optimisation
  at file 58F86h (`or es:[bx+12h],40h`) is given with no armour on; we make it count only with armour (arms,
  legs, head or chest). Seen in play 2026-11-01 (Cermak, no armour, AC 6, not 4).
- **Row 21, the fire elementals** (their 3.4, "resistance rows in the EXE-side enum record, data key not clean"):
  the monster kinds' table (3E45h:00A8h + the kind, file 43918h) holds resistance classes 14 (+1 weapons,
  nothing from fire) and 13 (+2 weapons, fire hurting) for kinds 32 and 33, the wrong way round against the clue
  book (lesser +1, the others +2). Ours sets them to 15 and 14 (class 15: +2, nothing from fire).
- **Row 15, Psionic Blast on a party member** (their 3.4, "real HP, power table at file 41F70h"): its imagined
  wounds were real; the Loader gives them back as the fight ends and knocks out, not kills, in the meantime.
  (A hook in our helper, so not an in-place patch.)

## Also worth a line each, with no open row of theirs

- **Row 25, resting while poisoned** (a 7th-level druid): the rest (8066Dh, overlay 5E8h; its one caller 62C2Ch)
  looks at who is poisoned (bitset 598:25h, 8075Dh) before the free cures at 809A2h run, so the poisoned die
  anyway. Order, not data.
- **Row 3, most PSP**: read from the creation screen's record rather than the character's, and tables too short
  (INT 22 gave nothing, INT 23 to 25 gave 20 to 24 too many, WIS 23 to 25 none).
- **Row 6, "can't save"**: the save compares its total with the number needed unsigned, so -100 ("can't save")
  read as large: the creature always saved (Chaos, Cloudkill on the weak, Scare below 6th level).
- Rows 8 to 14 and 16 to 19 (spell and fight rules) and 22 (the people's gear carried in their packs until their
  first action: AC 10 until then).

## The whole list

| # | Our row | In OpenDS |
|---:|---|---|
| 1 | Cause Serious and Critical Wounds | relayed |
| 2 | Slay Living's description | absent |
| 3 | A character's most PSP (worked out at each level-up check, for every party membe | absent |
| 4 | Negative Plane Protection | absent |
| 5 | Scare's save | relayed |
| 6 | "Can't save" (Chaos for all but warriors, Cloudkill on the weak, Scare below 6th | absent |
| 7 | Cloak of Bravery | absent |
| 8 | Mirror Image (and Reflected Image) | relayed |
| 9 | Armor | relayed |
| 10 | Share Strength (any maintained power on someone else) | relayed |
| 11 | Dispel Magic (the preserver's) | relayed |
| 12 | Absorb Disease (the psionic power) | absent |
| 13 | Bless and Aid | absent |
| 14 | Acid Arrow | absent |
| 15 | Psionic Blast on a party member | same bug, open there |
| 16 | Walls cast by monsters | absent |
| 17 | A berserk or confused party member | absent |
| 18 | Missiles from behind | absent |
| 19 | An archer whose quiver runs dry | absent |
| 20 | A thri-kreen's claws and bite | relayed |
| 21 | The fire elementals | same bug, open there |
| 22 | The game's people's weapons and armour | absent |
| 23 | Random monsters (a vanishing body, a survivor's warning) | same bug, open there |
| 24 | A fight's music | absent |
| 25 | Resting while poisoned with a druid of 7th level or more | absent |
| 26 | DELETE in the roster | relayed |
| 27 | The creation screen's least scores | absent |
| 28 | XP for high prime requisites | absent |
| 29 | A New character's thief skills | relayed |
| 30 | Thief skills' equipment penalty | absent |
| 31 | A thief skill rolled for the whole party (a trap going off, hearing the men by t | absent |
| 32 | Items that raise or lower an ability score | same bug, open there |
| 33 | The gladiator's armour optimisation (AC 1 better a 5 gladiator levels) | same bug, open there |
| 34 | Alagorn's stories of the Quicksilver Glove and the Helm of Contemplation | absent |
| 35 | The game's Sling +1 | relayed |
| 36 | The game's Great Axe +3 (the Army Commander's) | absent |
| 37 | The game's Quicksilver Glove | absent |
| 38 | The air cleric's daggers | absent |
| 39 | View Character's DAM line with a wooden, bone, stone or obsidian weapon | absent |
| 40 | The DAM lines of a hasted or slowed character (the inventory screen, View Charac | absent |
| 41 | What a scroll says on the inventory screen | absent |
| 42 | An archer's pointer after a shot | absent |
| 43 | A magic item's power on the Effects screen (Shadowseeker's Detect Invisibility) | absent |
| 44 | CHOOSE A SPELL's icons with more than 15 spells on offer (the game's own 4th lev | absent |
| 45 | Graphics disappearing in a busy area (SSI's note 2712 for Wake of the Ravager, t | same bug, open there |
| 46 | A magic item's glow in a shop | absent |
| 47 | "Out of memory in OEOpenGraph" in a long session | same bug, open there |
| 48 | The Trustee in the slave pens | relayed |
| 49 | Kurzak's door in the slave pens (the entryway to his stop) | absent |
| 50 | Alagorn's clothes when the party carries none | absent |
| 51 | Kurzak calling for Legcrusher once the party has killed him (he sends him when t | theirs |
| 52 | Legcrusher sent for a party that is at the fountain (its room, or the passage be | absent |
| 53 | Darkhold's scripts | theirs |
| 54 | The Lava Rifts ranger | theirs |
| 55 | Linara in Gedron | theirs |
| 56 | The slave pens' sewer grate | theirs |
| 57 | Pehtucl's ambush at the slave pens' fountain | absent |
| 58 | The Rebel Mindhome in Undermountain | theirs |
| 59 | The messenger in region 9 (the men who burst from the sand, after the elves leav | theirs |
| 60 | The Draj serf led to region 10 | theirs |
| 61 | The elven slavers' leader, asked "Who are you?" | theirs |
| 62 | A ranger tracking at the Wagon Train's bodies | theirs |
| 63 | A multi-class preserver or psionicist talking about the haystack | absent |
| 64 | Dagolar's slime book, in his laboratory | absent |
| 65 | The cave guide's "Why don't you go bother someone your own size" | absent |
| 66 | Lines that depend on the race or sex of the one talking to someone | theirs |

## How to send it

OpenDS's CONTRIBUTING says new bugs are recorded in `docs/known-bugs.md` before (or instead of) fixing, and
asks for an issue before a PR. The seven above are one issue each, or a single PR adding a section to their
known-bugs for "found and fixed by the Obsidian Edition". The other 37 would be one table. Two
cautions: this repository's documents are GPL-3.0 and theirs are MIT, so what goes out is facts in new words,
not our text, unless the owner says otherwise; and nothing from the private installation-files repository
(game data, the walkthrough) goes with it.
