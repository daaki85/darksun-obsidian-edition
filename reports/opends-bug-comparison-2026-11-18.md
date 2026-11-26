# Our fixed-bug list against OpenDS's catalogue (2026-11-18)

*Status: done, research; nothing sent to OpenDS. Its corrections are acted on in the Edition's pages: the random monsters' divide by zero and "Out of memory in OEOpenGraph" are no longer called the game's bugs.*

Every row of `obsidian-edition/GAME-BUGS.md` (66 rows, the games' own bugs the Edition fixes),
set against OpenDS at `fe35c52` (`docs/known-bugs.md`, `docs/ds1-sweep-triage-2026-10-07.md`,
`docs/community-crossread-2026-11-13.md`, `ds1-patch/`, `CREDITS.md`). The match is by my reading of
their docs, not a mechanical diff, and a row marked absent means I found no description of that bug there.

**Counts:** 11 rows OpenDS already has from us (relayed through yuan-ti, recorded there as
unverified); 11 are script repairs that are OpenDS's, yuan-ti's or both (or, for the Legcrusher and elven-leader rows,
ours where they have the row but no fix); 5 are the same bug as an open row of theirs, where we have a mechanism and
a fix they lack; **39 are absent from their catalogue**. The catalogue is theirs to keep, so
this is a list of what they might want, not a claim they are missing it.

## The five that answer an open row of theirs (the most useful to send)

**Correction (2026-11-18):** an earlier version listed seven. The seventh, row 47 ("Out of memory in OEOpenGraph"), is not a bug of the original game: release-notes/v2.6.0.md says that with the mod only about 53 KB were left for the 60,000-byte block, against 57 KB in the original game. It is the mod's own memory use, so it is not offered to OpenDS (and it does not answer their random-crashes row).

Addresses are from our DEVELOPMENT docs (file offsets in GOG 1.10's DSUN.EXE where marked "file"; the
others are segment:offset or overlay offsets as those docs write them). Re-check an address against the
image before sending it; I did not today.

- **Row 23, random monsters** (their 3.3(5) "random crashes"). **Corrected 2026-11-18:** REQUEST 8 at 80BE4h reads
  `MONR` 1 of `RESOURCE.GFF` (42-byte records, {region, 10 x {OJFF, strength}}); the slot search leaves SI one
  past the match, so `idiv word es:[bx+4]` at 80CD8h divides by the *next* slot's strength (verified in the stock
  bytes today). The Edition's notes add that this divides by zero in regions 6, 13, 14, 27, 39, 40, 44 and 255
  ("Divide error"). **The shipped data does not show that**: every strength in `MONR` 1 is at least 1 and the empty
  slots are (0, 1), so the divisor there is 1. Only the wrong-monster count is supported; do not offer the crash
  as an anchor for their random-crashes row until it is shown. **This is "not shown", not "not real".** I ran the
  routine's divisor logic over the shipped data (every real slot of the 29 records as the match, 270 cases): no zero
  and no read past the end of the chunk. The claim entered the Edition on 2026-10-23 (commit 5d68715, a code-reading
  change with no play log; the crash is not in `playtest/logs/`). It could still be real if the chunk in memory
  differs from the file, if another path reaches the divide, or if my reading of the slot layout is off (I did
  disassemble the loop: `bx = record + 4 x SI`, SI one past the match). What would settle it: read the loaded
  `MONR` chunk in DOSBox (the playtest memory tools) and, better, force a random-monster request in region 6. (The Edition's public notes, GAME-BUGS.md among
  them, carry the divide-by-zero claim; that is the user's to decide.)
- **Row 45, graphics disappearing** (their 2.2 "doorway / item graphics disappearance", deferred, and 3.3(1) the
  Gem Fields item ceiling): the game keeps every picture it loads in a table of **300 slots** and a store of a
  fixed **741,376 bytes**, appends a slot for each picture number it hasn't got and gives neither back until an
  area loads; past 300, new pictures go missing. SSI's note 2712 for Wake of the Ravager is the same engine.
  Their Gem Fields "3 gems" may be the same cause; we haven't tested that.
- **Row 32, stat-boost gear** (their 3.3(4), "grant keyed to possession, strip keyed to slot removal"): the
  mechanism is that the ability routine counts every listed item's score wherever it is carried: `mov
  al,es:[bx+0Fh]` at 7B8ABh. We make it count only an item in a worn slot. **Seen in play** (2026-11-01, dice log:
  DEX 15 -> 17 on putting a sling with +2 DEX in the worn missile slot, back to 15 in the backpack): one of those
  with a play log (the gladiator's and the picture slots' have one too).
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
| 23 | Random monsters (a vanishing body, a survivor's warning) | absent (wrong-slot count; the divide-by-zero is unsupported, see below) |
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
| 47 | "Out of memory in OEOpenGraph" in a long session | absent (and mod-induced, see the correction above) |
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
asks for an issue before a PR. The five above are one issue each (plus the random-monster count, as a smaller one), or a single PR adding a section to their
known-bugs for "found and fixed by the Obsidian Edition". The other 39 would be one table. Two
cautions: this repository's documents are GPL-3.0 and theirs are MIT, so what goes out is facts in new words,
not our text, unless the owner says otherwise; and nothing from the private installation-files repository
(game data, the walkthrough) goes with it.

## Verification status (added 2026-11-18, after the thief-row mistake)

Checked today against the stock DS1 `DSUN.EXE` (611,408 bytes) and `RESOURCE.GFF`, looking also for a Loader patch
at each site: the bytes at 7B758 (function start), 7B8AB (`mov al,es:[bx+0Fh]`), 58DD3 (start), 58F86 (`test
word es:[bx+12h],40h`), 80BE4 (start), 80CD8 (`idiv word es:[bx+4]`), 43918 (`0e 0d`), 26009 (`cmp word
[1F84h],300; jae`), 6A692 (`push dword 10000`), the 741,376-byte constant (0xB5000 at 60D9D), 78BA0 (a frame that
returns 1), 79A71, 79A89 (`and ax,1` on the byte at +4Fh), 79BBA (`cmp al,[bp-1]; jae`), 87666, 876AB, 872DE,
87779, 87BE6, 8066D, and `MONR` 1 (29 records). The Loader patches 7B8AB, 58F86, 80CD8, 43918, 26009, 872DE,
87779, 87BE6, 876AB and others: everything above is the *stock* bytes, which is what the issue texts describe.
**Not checked** (taken from the Edition's own notes): Psionic Blast's case 169 and its kill/knock-out thresholds,
the Scare/Protection-from-Normal-Missiles semantics, the resting-while-poisoned sequence, the PSP table claims,
what each fire-elemental class number means. One claim failed the check: the random-monster divide by zero (row 23).
