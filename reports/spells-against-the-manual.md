# Spells against the manual

What *Dark Sun: Shattered Lands* does with each spell and power, set against its manual
(`Manual.pdf`, page numbers are the PDF's), where the two part ways, with a suggested resolution
for each. Spells that match, or that the mod has already put right, are listed at the end.

**Where it stands.** The mod has since acted on the report in three groups, each checked in
DOSBox (playtest/logs/2026-11-08-manual-spells.md, 2026-11-08-hd-spells.md,
2026-11-08-spell-to-hit.md, 2026-11-09-turn-undead-meteors.md, 2026-11-09-group-3.md,
2026-11-09-group-4.md): the record changes and small fixes (group 2), the DSCLOG handlers (group 3)
and the monsters (group 4), under the Options tab's "Spells and psionics as the manual describes
them", with the missile and touch spells' attack rolls under "Spells roll to hit". Each entry
below says what was done, in italics; where the done thing differs from the suggested
resolution, the entry says why. The Scare and "can't save" fixes are bug fixes, always on.

**How this was found (2026-11-08).** The 32-byte spell records were read from the unpatched
`DSUN.EXE` (spell *s* at file offset `41F70h + 20h × s`) and decoded with the Loader's own
`spellbook.spell_info`; the code was disassembled from the file. Addresses are `DSUN.EXE` file
offsets, as the repository's docs and `gamepatch.py` use. Nothing here was cast in DOSBox for the
report: **"unverified"** marks a point the code didn't settle, and each fix would be checked in
the game before it ships.

Record fields used below: +4 duration dice (count low nibble, sides high), +5 duration a level,
+7 the unit (60 a round; negative: that many charges; −9999 until removed), +11h category word
(8000h: a save negates the damage), +17h the ground picture, +19h the effect, +1Ah damage kinds,
+1Ch to +1Eh damage dice, +1Fh the save (bit 0 a save allowed, bits 1-4 its modifier, 5-7 its kind).

Sizes: **small** a record change in `gamepatch.py` or a few lines of the Loader; **medium** a
DSCLOG handler; **large** new game mechanics.

## Read first

| | What the code shows |
|---|---|
| **Scare: no one ever saves** | Its record's save byte is A0h: bit 0, "a save allowed", is clear (Charm Person's and Hold Person's are A1h). The saving-throw routine (79A71h) tests that bit first (79A89h) and goes straight to "not saved" without it. So every creature but the undead is Scared, 6th level and up included. The level rule and the elf/half-elf priest rule live in the save modifiers (79FA4h-7A01Dh), behind that test, so they never run: **2.14.0's `scare_elves` fix has no effect**, and HOW-THE-GAME-WORKS and FEATURES describe Scare wrongly. (Checked in the code; to be seen in play.) *Fixed (always on): `scare_save` sets the bit; with `save_signed` (below) 6th level and up always save, those below can't, but an elf or half-elf priest saves as usual.* |
| **Missile spells never miss** | Acid Arrow, Turn Pebble to Boulder, Magical Stone and Condense are sent to a to-hit check (78BA0h) that is `mov ax,1 / retf`: always a hit. *Done: "Spells roll to hit" (below).* |
| **"Can't save" saves** (found 2026-11-09) | The saving throw compares its byte total with the number needed unsigned (79BBAh, `jae`), so the −100 the save modifiers give for "can't save" (Chaos, Cloudkill, Scare below 6th level, the mod's Color Spray) makes a total read as 156 and up: the creature always saves. Seen in DOSBox (Arena Guards "unable to save" took half Cloudkill's damage; a Guard "unable to save" against Scare was never Afraid). *Fixed: `save_signed` (jge), a bug fix, always on.* |
| **Protection from Normal Missiles stops breath weapons** | Any spell or power whose save kind is breath (the Fire Eel's, the Red Slaad's, the Animated Statue's) misses a target with effect 28 entirely (7A142h). Inertial Barrier and Deflection use the same effect. |

## Preserver spells (manual pp. 29-34)

### Scare (2nd): no save for anyone (seen in DOSBox 2026-11-08; fixed: `scare_save`)
- **Manual (p. 31):** creatures below six HD or levels tremble; "Saving throw: Neg."
- **Game:** no save at all (above); Afraid 1d4 + 1 round a level, undead immune.
- **Impact:** far stronger than the manual: it works on 6th-level foes and the arena's champions.
- **Resolution (small):** set the record's save bit (4222Fh A0h → A1h), which brings the
  game's own rules into play (6th level and up always save; the elf/half-elf fix works). To match
  "Neg." for everyone below 6th, also let them save normally (79FBEh's `jle` to the −100 made a
  jump past it). Correct HOW-THE-GAME-WORKS and FEATURES. *Done: the bit set (always on), with the
  game's own rules: 6th level and up always save; below 6th no save (the −100 failing since
  `save_signed`), but an elf or half-elf priest saves as usual. The manual's "Neg." below 6th is
  left: the game's rule is kept. The docs corrected.*

### Turn Pebble to Boulder (4th): 6d6, never misses
- **Manual (p. 33):** 11-26 damage "if it strikes the target".
- **Game:** 6d6 crushing (6-36, average 21 against 18.5), no save, always hits.
- **Resolution (small):** 3d6+8 in the record (+1Ch..+1Eh `08 1F 06`); the to-hit as below.
  *Done: `pebble_damage`, 3d6+8; it rolls to hit with "Spells roll to hit".*

### Missile spells always hit (Acid Arrow, Turn Pebble to Boulder; priests' Magical Stone, Condense)
- **Manual:** Acid Arrow "as if fired from the bow of a fighter the same level" (p. 31); Turn
  Pebble "if it strikes"; Condense "if it hits" (p. 38).
- **Resolution (medium):** a DSCLOG attack roll in place of 78BA0h's stub (the caster's THAC0,
  a fighter's for Acid Arrow, against the target's AC, through the to-hit routine at 7C3E9h). Or
  leave it as the designers' simplification and say so in HOW-THE-GAME-WORKS. *Done, as its own
  Options switch, "Spells roll to hit" (`spell_hit` at 7A15Ah, `spell_hit_stub` at 78BA3h): the
  four, each of Minute Meteors' globes (at +2) and the Strine's spines roll with the caster's THAC0
  (Acid Arrow a fighter's of the caster's level) and DEX, and the hostile touch spells (Chill
  Touch, Shocking Grasp, Vampiric Touch, the Cause Wounds spells, Cause Disease, Poison) with STR,
  at a creature of another side; a miss does nothing.*

### Minute Meteors (3rd): 1d4 a level, no to-hit
- **Manual (p. 32):** five globes of 1d4, +2 to hit.
- **Game:** 1d4 for each caster level (to 10), fire, no save, no attack roll (unverified).
- **Impact:** the manual's 5d4 at 5th level; 3d4 at 3rd, 9d4 at 9th.
- **Resolution (small, then check):** a flat 5d4 in the record (`00 2F 04`), checked in DOSBox.
  *Done otherwise: five globes of 1d4, the record's repeat count made 5 (Magical Stone's is 3),
  each landing on its own and, with "Spells roll to hit", rolling at +2 (`meteors_count`,
  `meteors_damage`). A flat 5d4 would have been one blast, not the manual's five globes.*

### Lower Resistance (5th): halves magic resistance
- **Manual (p. 34):** resistance drops by 30% + 1% a caster level.
- **Game:** while it lasts, resistance is halved (7A507h); the manual's 30 + level counts only for
  the cast's own resistance check (7A518h), which the dice log leaves out.
- **Impact:** weaker against low resistance (30% → 15%, the manual's 0%), a little stronger
  against very high.
- **Resolution (medium):** DSCLOG: subtract 30 + the effect's caster level instead of halving;
  the dice log's line for the cast (small). *(Done 2026-11-09: `lower_resistance_manual`, the
  cast's level kept in the effect's amount; seen in DOSBox.)*

### Flaming Sphere (2nd): a save halves it
- **Manual (p. 30):** 2-8 damage, "Saving throw: Neg.", 1 round.
- **Game:** 2d4 fire, a save halves it, instant.
- **Resolution (small):** a save negates: 42142h 40h → C0h. *Done: `flaming_sphere_negates`.*

### Strength (2nd): 1d6 for every class
- **Manual (p. 31):** +1 to 8 by the target's class (AD&D: warriors 1d8, priests and rogues 1d6,
  wizards 1d4), at most 24.
- **Game:** a flat 1d6 (79483h).
- **Resolution (small to medium):** a DSCLOG site on the dice at 79483h choosing the sides by the
  target's classes. (Adrenalin Control shares the code: leave it at 1d6.) *(Done 2026-11-09:
  `strength_dice`, Cat's Grace by the Tome of Magic's too; Strength and Adrenalin Control no
  longer add up. A second Strength already replaced the first.)*

### Solid Fog (4th) and Web (2nd): held until removed
- **Manual:** Solid Fog slows to a tenth for 2-4 rounds + 1 a level, fire dispels it (p. 33);
  Web holds for 2 turns a level, removed only by fire (p. 31).
- **Game:** Stuck (no movement at all) until removed; Dispel Magic can't remove it, and Free
  Action frees no one already Stuck (79406h). Web allows a save at −2, Solid Fog none.
- **Impact:** Solid Fog much stronger (stuck for the fight); Web about the same.
- **Resolution (small):** give Solid Fog the manual's time (1d3 + 1 round a level: +4 31h, +5 1,
  +7 60); Web 2 turns a level if wanted. "Slowed to a tenth" isn't something the game's movement
  can do: leave. Let Free Action end Stuck too (small, DSCLOG). *Done: Solid Fog 1d3 rounds + 1 a
  level (`solid_fog_time`); Free Action frees the Stuck (Web, Solid Fog, Quicksand, Entangle,
  Grease: `free_action_stuck`, its handler made a loop). Web left as it was.*

### Rainbow Pattern (4th): 1d3 rounds, attacks don't break it
- **Manual (p. 33):** holds until the creatures are attacked.
- **Game:** Paralyzed for 1d3 rounds; a hit doesn't end it, and Paralyzed fails every save.
- **Resolution (medium):** DSCLOG: a creature it holds that takes damage is freed; a longer time
  (1 round a level) for "special". *(Done 2026-11-09. Seen: the pattern is an area of its own
  (2d3 rounds) where everyone, the caster too, saves again each turn.)*

### Minor Spell Turning (4th): one spell, not 3 rounds a level
- **Manual (p. 33):** turns 1st- to 3rd-level spells for 3 rounds a level.
- **Game:** one charge, used by the first spell turned; it never times out (so it can be cast long
  before a fight). The level and single-target limits are right (7BD9Ch, 7A634h).
- **Resolution (small):** timed in the record (+4 10h, +5 3, +7 60). That turns every such spell
  for its time; AD&D caps it at 1d4+6 spell levels, which would need a DSCLOG counter (medium).
  *Done: 3 rounds a level (`spell_turning_time`), turning every 1st- to 3rd-level spell for its
  whole time (seen in DOSBox); no cap.*

### Mirror Image (2nd): images last until struck
- **Manual (p. 31):** 3 rounds a level.
- **Game:** 1d4 + 1 a 3 levels images, as charges that never expire. (The mod has already fixed
  what they stop.)
- **Resolution:** leave (an effect lasts either charges or time); a DSCLOG timer would be medium.

### Fire Shield (4th): no +2 on saves
- **Manual (p. 32):** attackers in melee take the damage back; the caster takes half and saves at +2.
- **Game:** the damage does go back to a melee attacker as fire (58B32h-58B4Ah), and the caster
  takes half from spells all of fire or cold (7B565h), but there is no +2.
- **Resolution (small):** a DSCLOG +2 against fire and cold beside Protection from Fire's
  (79E03h); the Loader's description of the effect to mention the returned damage. *(Done
  2026-11-09: `fire_shield_save` at Protection from Cold's test; its description says so.)*

### Blur (2nd) and Shield (1st): no save bonuses
- **Manual:** Blur +1 on saves against magic (p. 30); Shield better saves against missiles (p. 30).
- **Game:** Blur −2 to attackers only; Shield AC 4 except from behind, and it stops Magic Missile
  under a condition not traced (7A181h). The game has no saves against missiles.
- **Resolution:** Blur's +1, small (DSCLOG, as Barkskin's at 79DC3h). Shield: leave. *(Blur's
  +1 done 2026-11-09: `blur_save`.)*

### Chill Touch (1st): no STR loss, no fear
- **Manual (p. 29):** 1d4 and −1 STR a hit; undead may flee.
- **Game:** 1d4 cold, a save stops it; no fear, one touch. *Corrected 2026-11-09:* the handler's
  tail (79855h) does put Weakened 1 on a creature that fails its save, but with the record's time,
  0 rounds, so it ends at once (seen in DOSBox).
- **Resolution (medium):** DSCLOG: Weakened 1 STR on a failed save; undead Afraid 1d4 rounds.
  Repeated touches: leave. *(Done 2026-11-09: `chill_touch_time`, an hour; `CHILL_UNDEAD`.)*

### Feeblemind (5th): no INT or WIS loss, and nothing cures it
- **Manual (p. 34):** INT and WIS drop, no spells or psionics; Heal cures it.
- **Game:** "can't cast spells" until removed; Dispel can't touch it, and no spell removes it;
  psionics work. *Corrected 2026-11-09:* INT and WIS are 3 while it lasts (7B848h; seen in DOSBox).
- **Resolution:** the mod's Heal to remove it (small, DSCLOG); psionics, check then small;
  INT and WIS, medium to large. *(Done 2026-11-09: Heal cures it, `feeblemind_psionics`.)*

### Cloudkill (5th): never kills
- **Manual (p. 34):** kills weak monsters; stronger ones take damage.
- **Game:** 1d10 poison, a save at −2 halves it; creatures of 6th level or lower can't save. No
  death.
- **Resolution (medium):** DSCLOG: a failed save by a creature of 4th level or lower (AD&D's 4+1
  HD) kills, as Slay Living does. *(Done 2026-11-09: under 4 no save, 4-5 a failed save kills,
  6+ the damage. The game's "6 or less can't save" in fact always saved: the unsigned compare
  above.)*

### Confusion (4th) and Chaos (5th): one save, at the cast
- **Manual (pp. 32, 34):** a save each round; Chaos lets only fighters, and creatures of INT 21+
  or 4−, save.
- **Game:** one save at the cast, then confused for the whole time; Chaos lets warriors save, with
  no INT exception (medium confidence).
- **Resolution:** per-round saves, medium to large: leave and say so. Chaos's INT exception, small.
  *Done: Chaos's INT exception (`chaos_int`); the one save left, and said so in FEATURES.*

### Smaller (leave; say so in the docs)
- **Stinking Cloud (2nd):** 1d6 rounds, not 2-5 (same average). *Done: 1d4+1 (the record's
  1d4, DSCLOG's STINK_SITE adding the round).*
- **Color Spray (1st):** everyone saves, not only higher levels. *Done: creatures of the caster's
  level or lower can't save (`color_spray_level`), and a monster with no class counts its hit dice
  as its level for saves (`classless_save_level`).*
- **Invisibility (2nd):** ends only on an attack or a spell at an enemy (a buff on a friend keeps it).
- **Hold Undead (3rd):** the manual's "HD no more than the caster's" isn't in the game at all.
  *Done: undead of more levels (hit dice) than the caster's level are immune (`hold_undead_level`).*
- **Protection from Normal Missiles (3rd):** stops breath weapons too (above), maybe magical missiles (unverified).

## Cleric spells (manual pp. 35-40)

| Spell | Manual | Game | Resolution (size) |
|---|---|---|---|
| Bestow Curse (3rd) | −4 to attacks and saves; save Neg.; removed by Remove Curse or Dispel | Cursed: −1 to hit only; **no save** (A0h); Remove Curse doesn't end it | save bit A0h → A1h (small); −4 to hit and saves (medium); Remove Curse to end it (small). *Done: the save (`bestow_curse_save`); the −4 and Remove Curse left* |
| Blood Flow (4th) | stuns up to 4 rounds, save Neg. | Paralyzed 1d4 rounds, **no save** (A0h) | save bit A0h → A1h (small). *Done: `blood_flow_save`* |
| Quicksand (5th) | held 1 turn + 1 round a level, no save | Stuck 1 round, a save allowed | 1 round a level, no save, in the record (small). *Done: no save only (`quicksand_no_save`). Its time is left: its Stuck lasts a round and is put on again each round while the quicksand's own 5d3 rounds last, so the record's time changes nothing (seen in DOSBox)* |
| Free Action (4th) | breaks slow, hold and web | ends Paralyzed and Slowed only, not Stuck | DSCLOG: also end Stuck (small). *Done: `free_action_stuck` (a Poisoned creature stays Paralyzed, as the game has it)* |
| Magical Stone (1st) | three stones, 1d4 each, 2d8 against undead | three stones of 1d4 (seen in DOSBox 2026-11-08; "one" here was wrong), never misses | the undead part after checking its 1000h damage bit (medium). *Left as it is: the game already throws three stones of 1d4 (a record of 3d4 made each stone 3d4); each stone rolls to hit with "Spells roll to hit"* |
| Cause Fear (1st) | 1d4 rounds | 1 round a level | 1d4 rounds in the record (small). *Done: `cause_fear_time`* |
| Entangle (1st) | moves very slowly, 1 turn a level, save halves | Stuck 1 round, a save negates | leave, or 1 round a level (small) |
| Cause Disease (3rd) | saps STR and HP | Diseased: lowers nothing by itself | DSCLOG: Weakened 1d4 on a failed save (medium) |
| Remove Curse (4th) | ends Bestow Curse | puts a lowered STR back, ends no curse | with Bestow Curse (small) |
| Ironskin (5th) | immune to weapons, "special" | 1d6 blows stopped | more charges, 1 a level (small). *Done: a blow stopped a caster level (`ironskin_charges`, its level divisor 1)* |
| Dispel Evil (5th) | AC −7 against summoned evil; it saves or is dispelled | AC −7 only | leave, or DSCLOG (medium) |
| Insect Plague (5th) | blocks vision and spells, 1 HP a round | Afraid 2 rounds a level and no spells a round; its record has 1d1 damage (unverified in play; the docs say none) | leave; check the 1 HP and correct the docs (small) |
| Summon Insects (4th) | a cloud: AC +2, −2 to hit | summons a creature | leave |
| Dust Cloud (4th) | blocks sight and missiles | a ground cloud, no effect in the record | check in play whether it blocks sight |
| Raise Dead (5th) | a chance by CON and time dead | always works (not elves) | leave, or a survival roll (medium) |
| Bless (1st) | +1 to hit | +1 to hit and +1 on saves | leave (better) |

## Psionic powers (manual pp. 41-44)

| Power | Manual | Game | Resolution (size) |
|---|---|---|---|
| Cell Adjustment | heals wounds, cures disease | heals exactly 2 HP (795A2h); *its record does cure disease* (effect −13; corrected 2026-11-09) | *done 2026-11-09: 1d4* |
| Biofeedback | damage −2 and AC −1 | AC −1, *and 2 off blows and crushing, edged or pointed damage (79BF9h), to 0* (corrected 2026-11-09) | *done 2026-11-09: at least 1 left* |
| Control Body | fights for you at −6 to hit | Charmed 5 rounds, no −6 | DSCLOG (medium) |
| Mass Domination | up to five creatures | one | an area in the record (medium, check) |
| Detonate | 1d10 to everyone within 10' | the target only | leave, or an area (medium) |
| Inertial Barrier | halves breath, missiles, gas, acid, ice | missiles and breath miss outright; nothing else | leave, or half damage (medium) |
| Synaptic Static | no one can use psionics | only its keeper can't; others contest it | leave |
| Domination | while maintained | 5 rounds | leave |
| Psychic Crush | up to 6 | 1d8, half on a save | leave |

## Match, or already fixed by the mod

**Match:** Burning Hands, Charm Person (persons only, races 1-7: 7AFE7h), Gaze Reflection, Grease,
Magic Missile, Shocking Grasp, Wall of Fog, Detect Invisibility, Fog Cloud, Invisibility (attackers
−4: 7BD4Bh, 7C6C2h), Protection from Paralysis, Blink (7A112h), Fireball, Hold Person, Lightning Bolt, Minor Malison, Monster Summoning I-III, Slow, Spirit Armor, Vampiric
Touch (its cap never reached), Charm Monster, Black Tentacles, Fear, Ice Storm, Improved
Invisibility, Minor Globe, Stoneskin, Wall of Fire, Wall of Ice, Cone of Cold, Conjure Elemental,
Dismissal, Domination, Hold Monster, Summon Shadow, Wall of Force, Wall of Stone, **Glitterdust**
(its handler, 79433h, removes Invisible), and the cleric spells HOW-THE-GAME-WORKS lists as matching.

**Already fixed by the mod:** Mirror Image's images, Armor's charges, the preserver's Dispel
Magic, Acid Arrow's burning, Cause Serious and Critical Wounds' dice, Negative Plane Protection,
the Cloak of Bravery, Absorb Disease, Share Strength, Bless and Aid's targets, Hold Undead's guard,
Psionic Blast, Slay Living's description; as rules, Enlarge's dice and the saves (the spell save,
DEX for the doubled d20). Since the report: Scare's save and "can't save" (bug fixes); with "Spells
and psionics as the manual describes them" every *Done* above, and **Flame Arrow** (taken out of
"Match": the game made one blast of 5d6 for every five levels, 10d6 at 10th; now a bolt of 5d6 for
every five levels, each landing on its own, as AD&D's), **Hold Undead** (taken out of "Match": its
hit dice limit, above), **Turn Undead** by AD&D's turning table (turned undead flee 3d4 rounds; a
priest who fails can't try that undead again that fight), and a classless monster's hit dice as
its level for saves; with "Spells roll to hit" the missile and touch spells.

## Monsters: powers the manual promises

Checked in the game's code and data. Monsters get powers three ways: on a hit (by their kind),
by a special action one turn in four (routine 5A90Fh, by kind bit), and by regeneration (kind
bit 17: 3 HP a turn).

| Monster | The manual's power | In the game |
|---|---|---|
| Thri-kreen | paralysing bite | **Present** from 5th level: the bite (the last natural attack) of a kind-0 thri-kreen, party or monster, queues power 189: Paralyzed 2d8 rounds, save vs paralysis/poison/death (7A7A5h). The arena's Tohr-kreen (7th) has it; the 2nd-level Thrikreen don't. |
| Fire Eel | fire breath | **Present:** 6d6 fire, an area, a save halves it (power 181) |
| Strine | spines | **Present:** 1d6 piercing (power 180) |
| Sand Howler | paralysing gaze | **Present**, as a power: Paralyzed 2d6 rounds, save vs paralysis (179) |
| Tyrian and Dagolar slimes | webs | **Present:** Entangled, at an area (175); their hits also 2d6 acid |
| Red Slaad | healing | **Present:** 3 HP a turn; also paralyses 2d4 rounds (182) |
| Mastyrial | regeneration, poison sting | **Present:** 3 HP a turn; the sting 30 poison |
| Dark Spider | type F poison | 10 poison on the bite, a save stops it (one record, 54, has none but regenerates) |
| Shadow, Greater Shadow | strength drain | **Absent:** Greater Shadows' hits paralyse 2d6 rounds; the level-3 Shadows' do 2d6 cold. *Done as the manual describes them: 1 STR drained a hit (no save, Weakened 2d4 turns, adding up) in place of the cold and the paralysis; both unaffected by cold (`shadow_drain`, `shadow_cold`)* |
| Babau | poison | **Absent:** a corroding touch instead. *Done: deadly poison in place of the corroding touch (`babau_poison`)* |
| Blue Slaad | deadly poison | **Absent:** disease on 1 hit in 10. *Done: deadly poison in place of the disease (`blue_slaad_poison`)* |
| Tari | disease | **Absent:** a 2nd-level human fighter. *Done: a 3-HD bite of 1d3, disease 1 in 20 (`tari_kind`, `tari_bite`)* |
| Djinn | invisibility, illusions (the manual promises no magic resistance: the earlier "magic resistance" here was wrong) | **Absent:** none (MR 0, as the manual and AD&D). *Done: invisible (Improved Invisibility) with mirror images at its first turn of a fight (`djinn_kind`, DSCLOG's DJINN_TURN)* |
| Styr | fire breath | **Absent**. *Done: 3d6 fire breath one turn in four, +1 weapons to hurt it, HD 14, THAC0 7 (`styr_kind`)* |

The dice log's note on its "special effect: d10, works on a 1" line called that the thri-kreen
bite; it is the disease roll (kind bit 25): the game's Blue Slaad's, and with the manual's monsters
(the Blue Slaad's disease taken off) the Tari's, made 1 in 20 by a d2 more. A thri-kreen's bite
rolls no d10. *Corrected in DICE-LOG.md.* Its stat differences from the manual (lower hit dice
for several monsters, other attacks) look like the designers' balance and are left as they are.
