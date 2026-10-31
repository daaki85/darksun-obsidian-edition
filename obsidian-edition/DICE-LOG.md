# The dice log, line by line

*Part of Obsidian Edition's documentation, from the [README](README.md#the-dice-log): every kind
of line the Loader's dice log writes, and what it means. How to read and search the log is in the
README.*

## Contents

- [Fights](#fights)
- [Spells, saves and effects](#spells-saves-and-effects)
- [Checks, thief skills and searches](#checks-thief-skills-and-searches)
- [Hit points, kills and levels](#hit-points-kills-and-levels)
- [Character creation](#character-creation)
- [Everything else](#everything-else)

## Fights

| Line | Meaning |
|---|---|
| `Round 2: K'ratchek 32, Cermak 31, Cilla 30, Gerakis 26, Slig 26` | A new round of a fight, numbered from the fight's start, and the order everyone acts in (highest first). The order also stays in view above the log for the whole round, however far the log has scrolled: `Round 2. Now: Cilla (30). Still to act: Gerakis 26, Slig 26. Done: K'ratchek 32, Cermak 31. Down: ...`, and the [combat log in the game](README.md#the-combat-log-in-the-game) begins with who acts and who is next. The lines under it (shown with **Show details**) give each score's make-up: `    Gerakis 26 = 20 + 6 (0-9 roll), tie broken by 38 (0-199 roll)` (see [Initiative](HOW-THE-GAME-WORKS.md#initiative)). If the log was started in the middle of a round, the list has only the rolls it saw. |
| `Gerakis's turn` | Whose turn it is now, each time the turn passes in a fight. |
| `X attacks Y with Long Sword +1 (1d8+1): d20 = 14, needs 12+ (45%), hits AC 1, target AC 3 -> HIT` | An attack roll, the weapon and its damage dice: the d20, the roll this attacker needed against this target (THAC0 − target AC) and the chance of it, the lowest AC the roll hits, and the target's AC as the game used it. More below the table. |
| `    THAC0 16, +1 Blessed, +6 STR, +1 weapon = 8` | Where the attacker's THAC0 for this attack comes from: STR (melee) or DEX (missiles), spells (Bless, Prayer, Slow, Graft Weapon, the target's Blur), attacking from behind, the weapon's plus, the penalty for non-metal weapons (wooden −3, bone −1, stone and obsidian −2), the two-weapon adjustment (see [Two weapons](FEATURES.md#two-weapons)), and the difficulty setting for monsters. |
| `  X hits Y for 14: 1d8 = [6] +8 STR 20` | The damage of that hit: the dice, the weapon's bonus, and the STR bonus the game adds for melee. Damage is at least 1. |
| `  X hits Y for 27: 1d8 = [5] +12 STR 24 +10 backstab (the dice 5 x3 = 15)` / `  X hits Y for 51: (1d8 = [5] +12 STR 24) x3 backstab` | A backstab (see [backstabs](HOW-THE-GAME-WORKS.md#attacks-from-behind-and-backstabs)) multiplies the weapon's dice, the rest added once; with that option off, the whole damage, STR bonus included. |
| `Mistra dances: d20 = 3, needs 18 or less (DEX 22 -4) -> +1 to hit, damage and AC for 15 rounds` / `Halton fights wild: d20 = 9, needs 11 or less (CON 15 -4) -> 1 more attack a round and +3 damage for the fight` | A Battle Dancer's dance or a Wild Fury's Wild Fighting as a fight starts (see [Multiclass kits](KITS.md#multiclass-kits)). |
| `Chosen with Tab: Guard (50 HP) - Enter attacks it` | An enemy chosen with Tab in a fight (see [Choosing an enemy](FEATURES.md#choosing-an-enemy-tab-enter-and-the-rings)). |

**Attack rolls, in more detail.** `hits on anything but a 1` or `only a 20 hits`
replace `needs 12+` when the roll is out of the ordinary range. `X attacks Y
from behind ...` and `X attacks Y BACKSTAB ...` mark attacks from behind and
backstabs (see [Attacks from behind and
backstabs](HOW-THE-GAME-WORKS.md#attacks-from-behind-and-backstabs)). The
target's AC includes armour, DEX and spells. A natural 20 always hits and a
natural 1 always misses, but a 20 does no extra damage: the game has no critical
hits (see [No critical hits](HOW-THE-GAME-WORKS.md#no-critical-hits)).

## Spells, saves and effects

| Line | Meaning |
|---|---|
| `Shocking Grasp damage: 1d8 = [5] +10 = 15 (1d8 + 1 for each caster level: 10 at caster level 20, which counts as 10)` | A spell's damage roll, rolled for each target before its saving throw, with the spell's formula from the game's data. Damage stops growing at caster level 10 (Fireball does at most 10d6). Magic Missile, Flame Arrow and Minute Meteors are rolled elsewhere in the game, without the caster's level, so their line says how many steps the dice stand for. |
| `  Slig takes 15 from Shocking Grasp, now 3/18 HP` / `  Cilla takes 9 from Fireball (halved: Prot Fire)` | What the spell really did to each creature, after its save, resistances and protections (or the healing it gave). A protection that halved it is named: Resist Fire or Cold, Protection from Fire or Lightning, Fire Shield, a Wanderer's own. A creature that is Out Cold gets no save and takes the most the dice can do (the game's damage code does that), marked `(Out Cold: the most the dice can do)`. |
| `    Blur lasts 23 rounds (caster level 20: 1 for each caster level = 20 + 3 from the dice; dice 3d1)` | How long a spell's effect lasts, and how the game worked it out. A round is 60 game seconds. The game often "rolls" dice with one side, which are fixed numbers. |
| `    Stoneskin has 23 charges (caster level 20: 1 for each caster level = 20 + 3 from the dice; dice 1d4 = [3])` | Effects that last a number of uses rather than a time (Stoneskin's blows, Mirror Image's images, Invisibility's one attack, Poison's rounds): the game stores them as charges, worked out like a duration. |
| `    Acid on Slig: 2d4 = [3 + 1] = 4 acid damage` / `    Sunstroke's heat on Scar: 1d4 = 3 fire damage` / `    Improved AC on Slig: one charge used, 7 left` | Acid Arrow's damage each round while the acid lasts; Sunstroke's heat each round while it holds; and an effect with charges using one up, with how many are left (Armor or Ironskin taking a hit, Mirror Image losing an image...). |
| `Harm: all the target's hit points but 1d4 (...)` / `  Wall of Thorns' wall instead: 8 + AC 3 = 11` / `    Slig is swept off its feet: loses its next turn` | The [6th-level priest spells](FEATURES.md#6th-level-priest-spells)' own lines: Harm leaving 1d4 hit points (the dice the game rolls go unused), Wall of Thorns' damage by the creature's AC in place of the dice rolled, and a creature that fails its save against Whirlwind losing its next turn. |
| `Strength: 1d6 = 5 -> Cilla's STR +5 while it lasts (at most 24)` | The amount Strength (or Adrenalin Control) adds. |
| `Y magic resistance 30% vs Fireball: d100 = 71 -> not resisted` | The magic resistance roll (only shown for targets that have some), counting Mind Bar and Lower Resistance. |
| `    Dispel Magic on Slig's Blessed: d100 = 60, needs 85 or less (50 + 5 x 7 - 5 x 0 (its caster's level)) -> dispelled` | Dispel Magic tries each effect on its target separately: 50 + 5 for each of the dispeller's levels, less 5 for each of the level the effect was cast at. It can't touch some (Biofeedback, Diseased, Feeblemind, Poisoned, Graft Weapon, No spell use, Stuck, Mind Bar and a few more). |
| `Cilla can't cast Fireball there: no line of sight` | A spell you clicked to cast that the game refused, and why: no creature there, not a creature that spell takes, a wall too long, no line of sight, or too far away. The game itself only crosses out the pointer. |
| `Script: random monsters come (request 8: 32766, 1, 0)` | Something a script asked the game to do: the party resting, random monsters, an arena bout, a cinematic, game over. The numbers are the request's own values. The everyday ones (doors, blocked cells, music, creatures changing sides) only show with "Show unlabelled rolls". |
| `Cilla's STR 12 -> 16` | A party member's ability score changed, once the change holds: a spell's or effect's (Strength, Remove Curse giving back a lowered STR, Raise Dead's point of CON), and the game's own. |
| `    Abjure on Y: d20 = 14, needs 12 or more (11 - caster level 5 + its level 6) -> sent away` | Abjure sends a summoned creature away (1000 damage) on a d20 at or over 11 - the caster's level + the creature's. |
| `    Summoning: 1d3 = 2 picks which of its 3 creatures comes` | Which creature a summoning spell brings. |
| `Paralysing attack: lasts 7 rounds unless saved against (2d4 = [4 + 3] = 7)` | A monster's power the game has no name for (its records 172-195), named by what its record does: the effect it puts on (Paralysing, Disease, Entangling, Poison attack), else its damage's kind (`Fire attack (6d6 fire)`), else its number (`special attack 190`). Dice rolled just before the save are how long the effect would last. |
| `Y's saving throw vs Fireball from X (petrification/polymorph): d20 = 6, doubled against fire = 12 +1 Blessed = 13, needs 11 (80% to save) -> saved: half damage, 19 of 38` | A saving throw: which of the target's five saves it uses, the d20, each of the game's modifiers by name (anything the log can't account for shows as `other`), the number it had to reach and the chance of that; for a damaging spell, what the save left of that target's damage roll. More below the table. |
| `X gives Blessed to Y, Z: +1 to hit, +1 on saves` / `Blessed ends on Y` | A spell or psionic effect starting or ending, with what it does in the game's code where that is known: to-hit, AC and saving throws, movement and attacks, whether the creature can attack or cast, who controls it (see [Spells and effects](HOW-THE-GAME-WORKS.md#spells-and-effects)). `Stuck on Y` (no "gives") is an effect a creature has from a spell on the ground or cast on itself. |

**Saving throws, in more detail.** The modifiers are those of [the game's saving
throws](HOW-THE-GAME-WORKS.md#the-games-saving-throws). With the [rule
changes](FEATURES.md#rule-changes) off, the game uses petrification/polymorph
for almost every spell and doubles the d20 against fire, cold and electricity
spells, as in the example above, so Fireball's victims usually save; with them
on (the default), the line names the spell save and DEX's adjustment instead
(`+5 DEX 21 dodging`). A natural 1 always fails and a natural 20 always saves.
For a damaging spell the result says what the save left: `saved: half damage, 19
of 38`, `failed: full damage, 38`, or `saved: no damage` for spells such as
Chill Touch; the HP line after it shows what the creature really lost, once
resistances and protections have had their say. A failed save also lets the
spell's effect take hold. Spells left on the ground (Grease, clouds) make
creatures save again as they stay in them; those lines have no "from".

## Checks, thief skills and searches

| Line | Meaning |
|---|---|
| `X DEX check: d20 = 9, needs 16 or less (DEX 16) -> success` | An ability check. A natural 20 always fails. |
| `Daaki CHA check: 0-19 = 15, needs 16 or less (CHA 20 - 4) -> success` / `Cilla INT check: d20 = 3, needs 4 or less (INT 14 - 10) -> success` | An ability check a script makes with a roll of its own rather than the game's check, against the character acting (the leader outside a fight): talking Chahl round, breaking chains, spotting a secret door. The roll is shown as the script makes it (0 to 19, say), with what it needed. |
| `Daaki shoots at the archery target (15 squares from the target, 8 from the Bowyer): 0-20 = 2, needs under 14 (DEX 21 - 15 / 2), the centre 4 or less -> the centre: the Bowyer's reward, 6 Arrows +2` | A shot at the Bowyer's archery target in Teaquetzl: the roll, what it needed, how far the archer is from the target and from the Bowyer, and why a centre shot did or didn't earn his arrows (more than 13 squares from the target, the Bowyer within 25, once a game). |
| `Cilla tries to open locks: d100 = 35, needs 40 or less -> success` / `    open locks 40 = 18 + 16 thief level 4 + 10 elf...` | A thief skill roll (see [How the game works out thief skills](HOW-THE-GAME-WORKS.md#how-the-game-works-out-thief-skills)), and what its chance is made of. |
| `Zulak uses Graft Weapon: power check d20 = 14, needs 11 or less -> it fails` / `    power score 11 = 16 CON - 5 Graft Weapon` | A psionic power's check (see [Psionics](HOW-THE-GAME-WORKS.md#psionics)): a d20 at or under the power's score, the ability it uses plus the power's adjustment. A failure is the game's `psionic power check fails`, and costs half the PSP. A line `... within X's Synaptic Static: ...` comes first when someone else keeps Synaptic Static up. |
| `Gerakis's psionic defence: d6 = 5 and 6, both need over 4 (the attacker's power check d20) -> resisted` | A psionic attack mode (Ego Whip, Id Insinuation, Psychic Crush, Psionic Blast) resisted or not: its target rolls 1 to its defence twice, each needing more than the attacker's power check (see [Psionics](HOW-THE-GAME-WORKS.md#psionics)). |
| `Tezral hides in shadows: d100 = 21, needs 27 or less (54, halved in daylight) -> hidden` / `  Tezral moves silently: ...` | A thief's or ranger's hiding and moving silently at the start of their turn (with [hiding to backstab](FEATURES.md#hiding-in-shadows-to-backstab) on). |
| `    X's special effect on Y: d10 = 1, works on a 1 -> it works` | The 1-in-10 extra effect some creatures' hits have (the thri-kreen bite, for one). |
| `    X's Bone Long Sword nearly broke: 0 on 0-7, then 12 on 0-19 (needed 0)` / `... BREAKS` | The weapon check the game makes after an attack sequence whose last attack hit. Only non-magical wood, bone, stone and obsidian weapons can break (and not every kind: clubs and quarterstaffs can't): they break when a 0-7 roll and then a 0-19 roll both come up 0, 1 chance in 160. The line only appears when the first roll comes up 0. |
| `  Rampager's acid on Gerakis's Leather Chest Armor: d20 = 12, needs 10 (AD&D's, 10 for leather; the game's: destroyed without a roll) -> safe` | An item the Rampager's acid or the Babau's corroding touch could destroy: the d20, the number it needed and whose number that was (see [Items saving against acid](FEATURES.md#items-saving-against-acid)). |
| `Detonate's blast on Cilla's Bone Helm: d20 = 7, breaks it under 15 (15) -> DESTROYED` | Detonate (a daggoran's too) trying to destroy its target's worn item: the one that breaks most easily, a bone helm before bone armour, on a d20 under 15 less its plus. |
| `Haystack searched: 0-10 = 7, an old, soiled loincloth (the party's 2nd find of 6 in hay)` / `  The rat's bite: 0-4 = 3 damage` | Searching a junk pile, a haystack or a wardrobe: the game's roll, what it found, and how far its count has got (see [Searching junk, hay and wardrobes](HOW-THE-GAME-WORKS.md#searching-junk-hay-and-wardrobes)); a rat's bite or a falling pot rolls its damage the same way. |

## Hit points, kills and levels

| Line | Meaning |
|---|---|
| `  Slig now 8/18 HP (-10)` / `  Gerakis now 51/54 HP (+1)` | Any combatant's hit points going down or up, with what's left out of their most. The game never shows a monster's HP; this does. The line comes just after the damage that caused it (sometimes after the next roll, when the game is quick). |
| `  Gerrard regenerates 1 HP (CON 22), now 16/35 HP` | A hit point back by itself, to a party member with CON 20 or more: every 5 minutes of game time in the game, or at AD&D's rate by CON with [CON as in AD&D](FEATURES.md#con-as-in-add) (an hour at 20 to 10 minutes at 25). |
| `  Rampager now 69/72 HP (-3: 3 of the 7 rolled, non-magical weapons do half)` / `  Mastyrial takes none of the 6 damage: crushing weapons can't hurt it` | A weapon hit that took less than its roll, or none at all (no HP lost three seconds on, or by the next round), with the reason when the monster's own defences give one (what weapons hurt it); otherwise "a protection or resistance took it" (Stoneskin, say). |
| `Slig is killed` | A creature dying. What it's worth comes on the XP line below, only if the party gains it (the opening fight in the arena gives none, whoever dies). |
| `XP: Gerakis +67, K'ratchek +22, ... (for Slig 270)` | Experience the party got, and for which kills, with each one's XP from its character sheet. The game gives it right after the kill: an equal share to each character, split again between a multiclass character's classes (the sheet counts XP per class, so a three-class thri-kreen shows a third of the share). |
| `Cilla is now a 3rd level Ranger` / `    max HP 15 -> 21 (+6)` | A level gained, and the new maximum HP. |
| `    max HP unchanged: the game divides the hit point total by the classes, ...` | A multiclass character gained a level and its most hit points stayed the same: every class level rolls its die, but the game divides the whole total by the number of classes, so a small roll can add only a fraction (it counts at a later level). A human who changed class gets none in the new class until its level passes the old class's. |
| `Cilla's 3rd Ranger level: hit points d10 = 2, raised to 3 for CON 21` | The hit point roll for a new level: the class's die (d8 clerics and druids, d10 fighters, gladiators and rangers, d4 preservers, d6 psionicists and thieves; the Battle Mage and Arcanist [kits](FEATURES.md#kits) have their own), never less than 2, 3 or 4 with CON 20, 21-22 or 23+, and doubled for half-giants. After level 9 or 10 there's no roll, just a fixed gain (thieves roll at 10th too with [Level cap by XP](FEATURES.md#level-cap-by-xp)). With [the better of two](FEATURES.md#hit-dice-the-better-of-two) both rolls show (`d10 = 2 and 7, the better 7`), and with [multiclass hit points](FEATURES.md#multiclass-hit-points) CON's bonus on the die (`, +4 CON 18, into the total shared by 3 classes`). |

## Character creation

| Line | Meaning |
|---|---|
| `Character creation, STR 17: best of four 4d4 (7, 11, 9, 10) = 11, +4, +1 dwarf = 16, raised to 17 (the Fighter's prime requisite)` | An ability score rolled on the character creation screen (see [Character creation](HOW-THE-GAME-WORKS.md#character-creation)). The die rolls a whole character several times while it tumbles, faster than the log can read every roll, so the helper keeps each ability's last four 4d4 itself; the log gives only the character the die stops on, once it stops, each ability checked against the one the screen shows. A hit point roll that came too fast to record leaves a note: `some of its rolls came too fast to record`. |
| `Character creation: the six scores add up to 101` | After the scores, what they add up to: the most they may add up to with [Scores and hit points as rolled](FEATURES.md#scores-and-hit-points-as-rolled). |
| `Character creation, hit points 15: Fighter d10 per level: 7 + 9; Thief d6 per level: 5 + 1 = 22, / 2 classes = 11, +4 CON 16 = 15` | The new character's hit points: a die for every level of every class, divided by the number of classes, plus CON's bonus (see [Character creation](HOW-THE-GAME-WORKS.md#character-creation)). With [the better of two](FEATURES.md#hit-dice-the-better-of-two) each die shows both rolls (`10 (the better of 2 and 10)`); with [multiclass hit points](FEATURES.md#multiclass-hit-points) CON's bonus goes on each die before the total is shared (`+2 CON 16 on each of 4 dice = 30, / 2 classes = 15`). |
| `Character creation: a name picked at random, 1d33 = 6` | The game picks a new name from its lists when the sex or race changes. |

## Everything else

| Line | Meaning |
|---|---|
| `Message: Long Sword is broken !` | The game's own message boxes: broken or corroded weapons and armour, level-ups, "NO PATH FROM HERE" and so on. |
| `Dinos cooks the vulture and the party eats with him: ... restored as after a full rest (HP, PSP and spell slots); the game gives each 100 XP` | Dinos asked about the cooked vulture (see [The cooked vulture](FEATURES.md#the-cooked-vulture)); the XP itself is on the `XP:` line after it. |
| `Dreamwalker reads the scroll of Magic Missile: d100 = 37, needs 60 or less (INT 14) -> learnt` / `Xan reads the scroll of Shield: read languages d100 = 70, needs 35 or less -> can't read it (the scroll is used up)` / `Xan can't learn Armor from the scroll: not one of a Shinobi's spells (the scroll is kept)` | A try at a scroll's spell (see [Preservers' INT](FEATURES.md#preservers-int)): a preserver's d100 against INT's chance; a Shinobi's d100 against its read languages first, then INT's. A spell already known gives no line. |
| `Daaki makes 20 burning arrows (5 a preserver level, 4): a 1st-level slot used; ...` | A Spellarcher's arrow button (see [Multiclass kits](KITS.md#multiclass-kits)): the arrows go in its empty quiver, and stay there; with the same spell's arrows there, the line ends its first part with how many it holds now (`, 27 in the quiver now`). |
| `Dice: 1d8 = [3] = 3` | Dice the log couldn't tie to anything (for example a spell with no saving throw). |
| `(The Loader stopped one of its own writes over the game's memory: ...)` | A safety net: the Loader never writes over the start of memory (the interrupt vectors, the BIOS's and DOS's data) or the first bytes of the game's data, which its C runtime checks ("Null pointer assignment"). Such a write could only come from a pointer the game has left empty for a moment; the line says where in the Loader it came from. Please report it. |
