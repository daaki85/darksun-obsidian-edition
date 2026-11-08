# Spells against the manual

What *Dark Sun: Shattered Lands* does with each spell and power, set against its manual
(`Manual.pdf`, page numbers are the PDF's), where the two part ways, with a suggested resolution
for each. Spells that match, or that the mod has already put right, are listed at the end.

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
| **Scare: no one ever saves** | Its record's save byte is A0h: bit 0, "a save allowed", is clear (Charm Person's and Hold Person's are A1h). The saving-throw routine (79A71h) tests that bit first (79A89h) and goes straight to "not saved" without it. So every creature but the undead is Scared, 6th level and up included. The level rule and the elf/half-elf priest rule live in the save modifiers (79FA4h-7A01Dh), behind that test, so they never run: **2.14.0's `scare_elves` fix has no effect**, and HOW-THE-GAME-WORKS and FEATURES describe Scare wrongly. (Checked in the code; to be seen in play.) |
| **Missile spells never miss** | Acid Arrow, Turn Pebble to Boulder, Magical Stone and Condense are sent to a to-hit check (78BA0h) that is `mov ax,1 / retf`: always a hit. |
| **Protection from Normal Missiles stops breath weapons** | Any spell or power whose save kind is breath (the Fire Eel's, the Red Slaad's, the Animated Statue's) misses a target with effect 28 entirely (7A142h). Inertial Barrier and Deflection use the same effect. |

## Preserver spells (manual pp. 29-34)

### Scare (2nd): no save for anyone (seen in DOSBox 2026-11-08; the save bit set since: `scare_save`)
- **Manual (p. 31):** creatures below six HD or levels tremble; "Saving throw: Neg."
- **Game:** no save at all (above); Afraid 1d4 + 1 round a level, undead immune.
- **Impact:** far stronger than the manual: it works on 6th-level foes and the arena's champions.
- **Resolution (small):** set the record's save bit (4222Fh A0h → A1h), which brings the
  game's own rules into play (6th level and up always save; the elf/half-elf fix works). To match
  "Neg." for everyone below 6th, also let them save normally (79FBEh's `jle` to the −100 made a
  jump past it). Correct HOW-THE-GAME-WORKS and FEATURES.

### Turn Pebble to Boulder (4th): 6d6, never misses
- **Manual (p. 33):** 11-26 damage "if it strikes the target".
- **Game:** 6d6 crushing (6-36, average 21 against 18.5), no save, always hits.
- **Resolution (small):** 3d6+8 in the record (+1Ch..+1Eh `08 1F 06`); the to-hit as below.

### Missile spells always hit (Acid Arrow, Turn Pebble to Boulder; priests' Magical Stone, Condense)
- **Manual:** Acid Arrow "as if fired from the bow of a fighter the same level" (p. 31); Turn
  Pebble "if it strikes"; Condense "if it hits" (p. 38).
- **Resolution (medium):** a DSCLOG attack roll in place of 78BA0h's stub (the caster's THAC0,
  a fighter's for Acid Arrow, against the target's AC, through the to-hit routine at 7C3E9h). Or
  leave it as the designers' simplification and say so in HOW-THE-GAME-WORKS.

### Minute Meteors (3rd): 1d4 a level, no to-hit
- **Manual (p. 32):** five globes of 1d4, +2 to hit.
- **Game:** 1d4 for each caster level (to 10), fire, no save, no attack roll (unverified).
- **Impact:** the manual's 5d4 at 5th level; 3d4 at 3rd, 9d4 at 9th.
- **Resolution (small, then check):** a flat 5d4 in the record (`00 2F 04`), checked in DOSBox.

### Lower Resistance (5th): halves magic resistance
- **Manual (p. 34):** resistance drops by 30% + 1% a caster level.
- **Game:** while it lasts, resistance is halved (7A507h); the manual's 30 + level counts only for
  the cast's own resistance check (7A518h), which the dice log leaves out.
- **Impact:** weaker against low resistance (30% → 15%, the manual's 0%), a little stronger
  against very high.
- **Resolution (medium):** DSCLOG: subtract 30 + the effect's caster level instead of halving;
  the dice log's line for the cast (small).

### Flaming Sphere (2nd): a save halves it
- **Manual (p. 30):** 2-8 damage, "Saving throw: Neg.", 1 round.
- **Game:** 2d4 fire, a save halves it, instant.
- **Resolution (small):** a save negates: 42142h 40h → C0h.

### Strength (2nd): 1d6 for every class
- **Manual (p. 31):** +1 to 8 by the target's class (AD&D: warriors 1d8, priests and rogues 1d6,
  wizards 1d4), at most 24.
- **Game:** a flat 1d6 (79483h).
- **Resolution (small to medium):** a DSCLOG site on the dice at 79483h choosing the sides by the
  target's classes. (Adrenalin Control shares the code: leave it at 1d6.)

### Solid Fog (4th) and Web (2nd): held until removed
- **Manual:** Solid Fog slows to a tenth for 2-4 rounds + 1 a level, fire dispels it (p. 33);
  Web holds for 2 turns a level, removed only by fire (p. 31).
- **Game:** Stuck (no movement at all) until removed; Dispel Magic can't remove it, and Free
  Action frees no one already Stuck (79406h). Web allows a save at −2, Solid Fog none.
- **Impact:** Solid Fog much stronger (stuck for the fight); Web about the same.
- **Resolution (small):** give Solid Fog the manual's time (1d3 + 1 round a level: +4 31h, +5 1,
  +7 60); Web 2 turns a level if wanted. "Slowed to a tenth" isn't something the game's movement
  can do: leave. Let Free Action end Stuck too (small, DSCLOG).

### Rainbow Pattern (4th): 1d3 rounds, attacks don't break it
- **Manual (p. 33):** holds until the creatures are attacked.
- **Game:** Paralyzed for 1d3 rounds; a hit doesn't end it, and Paralyzed fails every save.
- **Resolution (medium):** DSCLOG: a creature it holds that takes damage is freed; a longer time
  (1 round a level) for "special".

### Minor Spell Turning (4th): one spell, not 3 rounds a level
- **Manual (p. 33):** turns 1st- to 3rd-level spells for 3 rounds a level.
- **Game:** one charge, used by the first spell turned; it never times out (so it can be cast long
  before a fight). The level and single-target limits are right (7BD9Ch, 7A634h).
- **Resolution (small):** timed in the record (+4 10h, +5 3, +7 60). That turns every such spell
  for its time; AD&D caps it at 1d4+6 spell levels, which would need a DSCLOG counter (medium).

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
  (79E03h); the Loader's description of the effect to mention the returned damage.

### Blur (2nd) and Shield (1st): no save bonuses
- **Manual:** Blur +1 on saves against magic (p. 30); Shield better saves against missiles (p. 30).
- **Game:** Blur −2 to attackers only; Shield AC 4 except from behind, and it stops Magic Missile
  under a condition not traced (7A181h). The game has no saves against missiles.
- **Resolution:** Blur's +1, small (DSCLOG, as Barkskin's at 79DC3h). Shield: leave.

### Chill Touch (1st): no STR loss, no fear
- **Manual (p. 29):** 1d4 and −1 STR a hit; undead may flee.
- **Game:** 1d4 cold, a save stops it; no STR loss, no fear, one touch.
- **Resolution (medium):** DSCLOG: Weakened 1 STR on a failed save; undead Afraid 1d4 rounds.
  Repeated touches: leave.

### Feeblemind (5th): no INT or WIS loss, and nothing cures it
- **Manual (p. 34):** INT and WIS drop, no spells or psionics; Heal cures it.
- **Game:** "can't cast spells" until removed; Dispel can't touch it, and no spell removes it
  (unverified: whether it stops psionics).
- **Resolution:** the mod's Heal to remove it (small, DSCLOG); psionics, check then small;
  INT and WIS, medium to large.

### Cloudkill (5th): never kills
- **Manual (p. 34):** kills weak monsters; stronger ones take damage.
- **Game:** 1d10 poison, a save at −2 halves it; creatures of 6th level or lower can't save. No
  death.
- **Resolution (medium):** DSCLOG: a failed save by a creature of 4th level or lower (AD&D's 4+1
  HD) kills, as Slay Living does.

### Confusion (4th) and Chaos (5th): one save, at the cast
- **Manual (pp. 32, 34):** a save each round; Chaos lets only fighters, and creatures of INT 21+
  or 4−, save.
- **Game:** one save at the cast, then confused for the whole time; Chaos lets warriors save, with
  no INT exception (medium confidence).
- **Resolution:** per-round saves, medium to large: leave and say so. Chaos's INT exception, small.

### Smaller (leave; say so in the docs)
- **Stinking Cloud (2nd):** 1d6 rounds, not 2-5 (same average).
- **Color Spray (1st):** everyone saves, not only higher levels.
- **Invisibility (2nd):** ends only on an attack or a spell at an enemy (a buff on a friend keeps it).
- **Hold Undead (3rd):** the manual's "HD no more than the caster's" isn't in the target test (unverified elsewhere).
- **Protection from Normal Missiles (3rd):** stops breath weapons too (above), maybe magical missiles (unverified).

## Cleric spells (manual pp. 35-40)

| Spell | Manual | Game | Resolution (size) |
|---|---|---|---|
| Bestow Curse (3rd) | −4 to attacks and saves; save Neg.; removed by Remove Curse or Dispel | Cursed: −1 to hit only; **no save** (A0h); Remove Curse doesn't end it | save bit A0h → A1h (small); −4 to hit and saves (medium); Remove Curse to end it (small) |
| Blood Flow (4th) | stuns up to 4 rounds, save Neg. | Paralyzed 1d4 rounds, **no save** (A0h) | save bit A0h → A1h (small) |
| Quicksand (5th) | held 1 turn + 1 round a level, no save | Stuck 1 round, a save allowed | 1 round a level, no save, in the record (small) |
| Free Action (4th) | breaks slow, hold and web | ends Paralyzed and Slowed only, not Stuck | DSCLOG: also end Stuck (small) |
| Magical Stone (1st) | three stones, 1d4 each, 2d8 against undead | one 1d4, never misses | 3d4 in the record (small); the undead part after checking its 1000h damage bit (medium) |
| Cause Fear (1st) | 1d4 rounds | 1 round a level | 1d4 rounds in the record (small) |
| Entangle (1st) | moves very slowly, 1 turn a level, save halves | Stuck 1 round, a save negates | leave, or 1 round a level (small) |
| Cause Disease (3rd) | saps STR and HP | Diseased: lowers nothing by itself | DSCLOG: Weakened 1d4 on a failed save (medium) |
| Remove Curse (4th) | ends Bestow Curse | puts a lowered STR back, ends no curse | with Bestow Curse (small) |
| Ironskin (5th) | immune to weapons, "special" | 1d6 blows stopped | more charges, 1 a level (small) |
| Dispel Evil (5th) | AC −7 against summoned evil; it saves or is dispelled | AC −7 only | leave, or DSCLOG (medium) |
| Insect Plague (5th) | blocks vision and spells, 1 HP a round | Afraid 2 rounds a level and no spells a round; its record has 1d1 damage (unverified in play; the docs say none) | leave; check the 1 HP and correct the docs (small) |
| Summon Insects (4th) | a cloud: AC +2, −2 to hit | summons a creature | leave |
| Dust Cloud (4th) | blocks sight and missiles | a ground cloud, no effect in the record | check in play whether it blocks sight |
| Raise Dead (5th) | a chance by CON and time dead | always works (not elves) | leave, or a survival roll (medium) |
| Bless (1st) | +1 to hit | +1 to hit and +1 on saves | leave (better) |

## Psionic powers (manual pp. 41-44)

| Power | Manual | Game | Resolution (size) |
|---|---|---|---|
| Cell Adjustment | heals wounds, cures disease | heals exactly 2 HP (795A2h), cures nothing | 1d6 a level or so, and remove Diseased (small to medium) |
| Biofeedback | damage −2 and AC −1 | AC −1 only | DSCLOG −2 a blow (small to medium) |
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
−4: 7BD4Bh, 7C6C2h), Protection from Paralysis, Blink (7A112h), Fireball, Flame Arrow, Hold Person,
Hold Undead, Lightning Bolt, Minor Malison, Monster Summoning I-III, Slow, Spirit Armor, Vampiric
Touch (its cap never reached), Charm Monster, Black Tentacles, Fear, Ice Storm, Improved
Invisibility, Minor Globe, Stoneskin, Wall of Fire, Wall of Ice, Cone of Cold, Conjure Elemental,
Dismissal, Domination, Hold Monster, Summon Shadow, Wall of Force, Wall of Stone, **Glitterdust**
(its handler, 79433h, removes Invisible), and the cleric spells HOW-THE-GAME-WORKS lists as matching.

**Already fixed by the mod:** Mirror Image's images, Armor's charges, the preserver's Dispel
Magic, Acid Arrow's burning, Cause Serious and Critical Wounds' dice, Negative Plane Protection,
the Cloak of Bravery, Absorb Disease, Share Strength, Bless and Aid's targets, Hold Undead's guard,
Psionic Blast, Slay Living's description; as rules, Enlarge's dice and the saves (the spell save,
DEX for the doubled d20). **Not fixed after all:** Scare (above).

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
| Shadow, Greater Shadow | strength drain | **Absent:** Greater Shadows' hits paralyse 2d6 rounds; the level-3 Shadows' do 2d6 cold |
| Babau | poison | **Absent:** a corroding touch instead |
| Blue Slaad | deadly poison | **Absent:** disease on 1 hit in 10 |
| Tari | disease | **Absent:** a 2nd-level human fighter |
| Djinn | invisibility, illusions, magic resistance | **Absent:** none, MR 0 |
| Styr | fire breath | **Absent** |

The dice log's note on its "special effect: d10, works on a 1" line calls that the thri-kreen
bite; it is the disease roll (kind bit 25). Its stat differences from the manual (lower hit dice
for several monsters, other attacks) look like the designers' balance and are left as they are.
