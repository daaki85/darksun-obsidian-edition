# The dice log, line by line

*Part of Obsidian Edition's documentation, from the [README](README.md#the-dice-log): how to read
the Loader's dice log, and every kind of line it writes, with what it means. Finding a line and the
log's boxes are in the README.*

**The readable layout** (**Readable layout**, above the log, ticked: the default) puts each event on
a line of its own with what came of it first, `● Seneca hits Arena Guard for 11 — backstab, Bone
Hayneedle +1`, then in columns at the right the HP it left (`19/30 (−11)`, marked `!` and coral when
a party member is down to a third) and the roll (`d20 15 vs 4+ (85%) · AC 8`). Under it, smaller
and dim, the working: the to-hit sum against the target's AC with the lowest AC the roll would have
hit, the damage dice, a save's line in full, each initiative score. A party member's line has a
filled pip, a monster's a hollow one; a round starts with a rule and its order, a turn with `▸` and
the name. The outcome's colour is the party's view of it: sky blue for good (the party hits, a
monster fails its save), coral for bad (a monster hits, a party member fails), dim for a miss or a
monster's save, gold for a kill. **Show details** hides the working. A fight's summary is shown as
the fight's close, every member's line shown.

**Reading the lines as written.** The lines below are the log as it is written: what **Save...**
writes, what the crash and freeze reports hold, and what the window shows with **Readable layout**
unticked. Lines at the left edge are the events: a round starting, whose turn it is, attack rolls,
saves, spells, kills. Lines indented two spaces are their results (damage, HP left); lines indented
four spaces are the details: the sums behind a THAC0, a save's modifiers, the initiative scores.
Untick **Show details**, above the log, to hide the details and keep the rest; they come back when
it's ticked again. In the window, each kind has its colour (hits green, misses grey, damage amber,
saves blue, turns sand, rounds underlined with a gap above), and the words say the same thing
([accessibility](README.md#accessibility)). Names stand out in bold: each party member in a colour
of their own (cyan, magenta, peach and white, by place in the party) and every monster and other
creature in red, so who acts and who is hit can be followed down the log.

## Contents

- [Fights](#fights)
- [Spells, saves and effects](#spells-saves-and-effects)
- [Checks, thief skills and searches](#checks-thief-skills-and-searches)
- [Inventory and shops](#inventory-and-shops)
- [Hit points, kills and levels](#hit-points-kills-and-levels)
- [Character creation](#character-creation)
- [Ages](#ages)
- [Everything else](#everything-else)

## Fights

| Line | Meaning |
|---|---|
| `Round 2: K'ratchek 32, Cermak 31, Cilla 30, Gerakis 26, Slig 26` | A new round: its number, and the order everyone acts in, highest first. |
| `Initiative: K'ratchek 32, Cermak 31, ...` | The same order when the log doesn't know the round's number. |
| `Rounds 4-5 go by at once: no one in the fight can act` | When everyone is unable to act, the game can play several rounds between polls. The log counts the rounds and lists the last round's order (`Round 6: ...`). The in-game panel shows `ROUNDS 4-5 SKIPPED` at every detail level. |
| `Gerakis's turn` | Whose turn it is now, each time the turn passes in a fight. |
| `X attacks Y with Long Sword +1 (1d8+1): d20 = 14, needs 12+ (45%), hits AC 1, target AC 3 -> HIT` | An attack roll, the weapon and its damage dice: the d20, the roll this attacker needed against this target (THAC0 − target AC) and the chance of it, the lowest AC the roll hits, and the target's AC as the game used it. More below the table. |
| `    THAC0 16, +1 Blessed, +6 STR, +1 weapon = 8` | Where the attacker's THAC0 for this attack comes from, part by part. |
| `  X hits Y for 14: 1d8 = [6] +8 STR 20` | The damage of that hit, part by part; at least 1. |
| `  X hits Y for 27: 1d8 = [5] +12 STR 24 +10 backstab (the dice 5 x3 = 15)` | A backstab: the weapon's dice multiplied. |
| `  X hits Bulette for 10: 1d12 = [11] -1 bone (1d12 for 1d8: a large target)` | A weapon's dice for the target's size, with [Creature size as in AD&D](FEATURES.md#creature-size). |
| `  X hits Y for 17: 1d8 = [4] +12 STR 24 +1 Enlarge (the dice 4 x110% = 5, level 1)` | A blow by an Enlarged attacker. |
| `    X's cahulaks tangle Y? Save against petrification: d20 = 2, needs 19+ -> tangled: loses its next turn` | A cahulaks hit's tangle: the target's save against petrification. |
| `    X's trikal trips Y? Save against paralysis: d20 = 12, needs 13+ -> tripped: loses its next turn` | A trikal specialist's hit's trip: the target's save against paralysis ([the trikal](FEATURES.md#trikal)). |
| `    X turns the double spear's last swing from Y to Z, beside it (a specialist's second foe, 1 less damage)` | A lotulis or double spear specialist's last swing of the round, on a second foe ([two-headed weapons](FEATURES.md#lotulis-and-double-spear)); the attack line after it is that swing. |
| `Y's saving throw vs a stinkpot from X (paralysis/poison/death): d20 = 7, needs 14 (40% to save) -> failed: nauseated` | A staff sling's stinkpot: the target's save against poison. |
| `    Paralyzed: hit automatically, for normal damage (AD&D's held target)` | A held or Out Cold target hit whatever the d20, with [Held targets as in AD&D](FEATURES.md#held-targets). |
| `Mistra dances: d20 = 3, needs 18 or less (DEX 22 -4) -> +1 to hit, damage and AC for 15 rounds` | A Battle Dancer's dance as a fight starts. |
| `Mistra dances: d20 = 20, needs 18 or less (DEX 22 -4) -> stumbles: -1 to hit, damage and AC for 3 rounds (d8 = 3)` | A dance that failed, and its rounds (a d8). |
| `Chosen with Tab: Guard (50 HP), needs 14+ (35%) - Enter attacks it` | An enemy chosen with Tab in a fight (see [Choosing an enemy](FEATURES.md#choosing-an-enemy-tab-enter-and-the-rings)), and what the member whose turn it is must roll to hit it ([the chance shown before the swing](PLAYER-GUIDE.md#the-chance-shown-before-the-swing)): `from behind 10+ (55%)` after it where that depends on where the member walks to, each weapon named when they differ, `hits whatever the roll (Paralyzed)` for a held enemy. |
| `Look: Mountain Stalker: HP 38/60, AC 4, THAC0 11, chaotic evil.` | A monster looked at in a fight: what the [Look box](FEATURES.md#what-hurts-a-monster-the-look-box) shows of it, and on the lines below its defences and what its hits do, as the game's window shows them on closing the box. |

**The lines above, in more detail.**

- A new round of a fight, numbered from the fight's start, and the order everyone acts in (highest first). The order also stays in view above the log for the whole round, however far the log has scrolled: `Round 2. Now: Cilla (30). Still to act: Gerakis 26, Slig 26. Done: K'ratchek 32, Cermak 31. Down: ...`, and the [combat log in the game](FEATURES.md#the-combat-log-in-the-game) begins with who acts and who is next. The lines under it (shown with **Show details**) give each score's make-up: `    Gerakis 26 = 20 + 6 (0-9 roll), tie broken by 38 (0-199 roll)` (see [Initiative](HOW-THE-GAME-WORKS.md#initiative)). If the log was started in the middle of a round, the list has only the rolls it saw.
- Where the attacker's THAC0 for this attack comes from: STR (melee) or DEX (missiles), spells (Bless, Prayer, Slow, Graft Weapon, the target's Blur), attacking from behind, the weapon's plus, the penalty for plain non-metal weapons (wooden −3, bone −1, stone and obsidian −2), the two-weapon adjustment (see [Two weapons](FEATURES.md#two-weapons)) or a cahulaks head's (`-4 cahulaks, off head at DEX 10`, the main head's −2: [Cahulaks](FEATURES.md#cahulaks)), a weapon spec's (`+1 specialized`, `+3 grand mastery`: [Weapon specialization](WEAPON-SPECS.md)), a kit's by name, the new spells' (`+1 Erdlu Claw`, `-3 Fogbolt`, `+2 target's Fogbolt`: [New wizard spells](FEATURES.md#new-wizard-spells)), a stinkpot's `-2 Nauseated` ([Staff sling stinkpots](FEATURES.md#staff-sling-stinkpots)), and the difficulty setting for monsters.
- The damage of that hit: the dice, the weapon's bonus, a weapon spec's (`+2 specialized`; a grand master's bigger die, `(d10 for d8: grand mastery)`, against a large target `(1d20 for 1d8: a large target, grand mastery)`), a kit's or Wild Fighting's (`+3 Wild Fighting`), and the STR bonus the game adds for melee. Damage is at least 1. On a creature with Biofeedback, `-2 Biofeedback`: 2 off, at least 1 left (the game's own left none of a blow of 2 or less).
- A backstab (see [backstabs](HOW-THE-GAME-WORKS.md#attacks-from-behind-and-backstabs)) multiplies the weapon's dice, the rest added once ([Thieves as in AD&D](FEATURES.md#thief-skills-from-adds-table), always on; the game multiplied the whole damage, STR bonus included). Other lines of the kind: `  X hits Y for 27: 1d8 = [5] +12 STR 24 +10 backstab (the dice 5 x3 = 15)`.
- With [Creature size as in AD&D](FEATURES.md#creature-size), a weapon rolling other dice for the target's size: AD&D's against a large target (a half-giant, a large monster, anyone Enlarged), or a Shillelagh's 1d6+1 against a smaller one. Other lines of the kind: `(... for 2d4: a target smaller than large)`.
- A blow by an Enlarged attacker: with [Enlarge multiplies the weapon's dice only](FEATURES.md#enlarge-multiplies-the-weapons-dice-only), the dice grown by 10% a caster level, rounded up, the rest added after. Other lines of the kind: `  X hits Y for 22: (1d8 = [4] +4 weapon +12 STR 24) x110% Enlarge (level 1)`.
- Under a cahulaks hit that did damage, with [Weapon traits](FEATURES.md#cahulaks): the target's save against being tangled, its own number against petrification (a 20 always saves); `-> saved`, or tangled, losing its next turn. A target too big for it, or with nothing to tangle, has no line ([the creatures' table](CREATURES.md)).
- After a staff sling's hit that did damage, with [Weapon traits](FEATURES.md#staff-sling-stinkpots): the target's save against poison (the game's own, as against a monster's poisoned hit, with its bonuses), then the rounds it is nauseated (−2 to hit) on a failure; `-> saved` and nothing more on a success. A held or sleeping target fails with no roll (`nauseated, no saving throw (helpless)`). An undead or a creature immune to poison: `    X's stinkpot bursts on Y: undead, unaffected` (or `immune to poison`). Other lines of the kind: `    X's stinkpot: Y is nauseated, -2 to hit for 1d3+1 = 2 + 1 = 3 rounds`.
- Under an attack on a held (Paralyzed) or Out Cold target, with [Held targets as in AD&D](FEATURES.md#held-targets): the attack hits whatever the d20 (the line above it still shows the roll and what it needed), and the damage line after it is the damage as rolled.
- A helpless target makes no saving throw, so a Poisoner's poison on it has no save line: the log names it with the hit, and its 10 (`  Y takes 10 from Poison (10 damage)`) when it lands, which can be after the round's next swing. Other lines of the kind: `  Y is poisoned by the hit: Poison (10 damage), no saving throw (Paralyzed)` (a Poisoner's: each weapon's first hit in a fight).
- A Battle Dancer's dance or a Wild Fury's Wild Fighting as a fight starts (see [Multiclass kits](KITS.md#multiclass-kits)). Other lines of the kind: `Halton fights wild: d20 = 9, needs 11 or less (CON 15 -4) -> 1 more attack a round and +3 damage, -3 to hit and AC 3 worse for the fight`.
- A dance that failed, and its rounds (a d8); a dance's end, good or bad, when its rounds run out; and Wild Fighting that failed (its penalties without its gains). Other lines of the kind: `Mistra's dance is over`; `Halton fights wild: d20 = 14, needs 11 or less (CON 15 -4) -> fails: -3 to hit and AC 3 worse for the fight`.

**Attack rolls, in more detail.** `hits on anything but a 1` or `only a 20 hits`
replace `needs 12+` when the roll is out of the ordinary range. `X attacks Y
from behind ...` and `X attacks Y BACKSTAB ...` mark attacks from behind and
backstabs, and `X attacks Y unseen ...` a hidden archer's shot (see [Attacks from behind and
backstabs](HOW-THE-GAME-WORKS.md#attacks-from-behind-and-backstabs)). A
thri-kreen of the party with nothing in hand attacks `with a claw (1d4)`, four
times a round, then `with its bite (1d4+1)`, whose damage line shows its
`+1 bite`; with weapons in hand, it attacks with them and then still bites.
The claw's dice are the ones it has now (Erdlu Claw's `1d6+1`, Animal
Affinity's `1d10`, Body Weaponry's `2d4`). Anyone else unarmed, and a
monster's own attacks, have no `with`. The
target's AC includes armour, DEX and spells. A natural 20 always hits and a
natural 1 always misses, but a 20 does no extra damage: the game has no critical
hits (see [No critical hits](HOW-THE-GAME-WORKS.md#no-critical-hits)).

**Kits in the lines.** A kit shows where it changes a number, by name: an attack's THAC0 line has
`from behind (Rescuer)` for the Rescuer's +1, the initiative's parts `Wayfinder's Path-finder`
(and the Wayfinder's own `+2 Wayfinder`), a healing spell's `+1 Healer` (or `+1 Rescuer`) or a Lifebinder's `+ 1d8 Lifebinder (the kit's
die)`, Cell Adjustment's `1d4 = 3, +1d4 = 2 (Lifebinder)` or `1d4 = 3, +1 (Healer)`, a
Wilderness Avenger's `+1 Wilderness Avenger` on a Cause spell's damage, the warrior's THAC0 of a
Swashbuckler, Battle Mage, Crusader or Mind Warrior with its chosen weapon (`+4 Crusader (a
warrior's THAC0)`), the Spellarcher's Fine Bow (`+1 fine`), and a Swashbuckler's bad luck on each thief skill roll (`-7 Swashbuckler's bad
luck`, 0 to 25, rolled each time) ([Kits](KITS.md)). An Arcanist's spells show the level it casts
at, one more than its preserver level, in their `caster level` and damage parts, without naming the
kit.

## Spells, saves and effects

| Line | Meaning |
|---|---|
| `Shocking Grasp damage: 1d8 = [5] +10 = 15 (1d8 + 1 for each caster level: 10 at caster level 20, which counts as 10)` | A spell's damage roll, before the target's save. |
| `Lex's Magical Stone at Zombie: attack d20 = 9, needs 12+ (45%) (THAC0 16, +1 DEX; target AC 3) -> MISS: the spell does nothing, the 7 damage rolled lost` | A missile or touch spell's attack roll, with [Spells roll to hit](FEATURES.md#spells-roll-to-hit). |
| `  Slig takes 15 from Shocking Grasp, now 3/18 HP` | What a spell really did to a creature, after its save and protections. |
| `    Blur lasts 23 rounds (caster level 20: 1 for each caster level = 20 + 3 from the dice; dice 3d1)` | How long a spell's effect lasts, and how the game worked it out. A round is 60 game seconds. The game often "rolls" dice with one side, which are fixed numbers. |
| `    Stoneskin has 23 charges (caster level 20: 1 for each caster level = 20 + 3 from the dice; dice 1d4 = [3])` | Effects that last a number of uses rather than a time (Stoneskin's blows, Mirror Image's images, Invisibility's one attack, Poison's rounds): the game stores them as charges, worked out like a duration. |
| `    Acid Arrow burns 3 rounds more, 2d4 at the start of each (...)` | How many more rounds Acid Arrow's acid burns, worked out from the caster level as a duration is. |
| `    Acid on Slig: 2d4 = [3 + 1] = 4 acid damage` | Acid Arrow's acid burning, a round at a time. |
| `Harm: all the target's hit points but 1d4 (...)` | Harm leaving 1d4 hit points, a [6th-level priest spell](FEATURES.md#6th-level-priest-spells)'s own line. |
| `Strength: 1d6 = 5 -> Cilla's STR +5 while it lasts (at most 24)` | What Strength adds to STR. |
| `Y magic resistance 30% vs Fireball: d100 = 71 -> not resisted` | A magic resistance roll (only for a target that has some). |
| `Chill Touch on Zombie, undead: no damage, no STR lost; Afraid 1d4 = 3 rounds instead` | Chill Touch on an undead, as the manual describes the spell. |
| `Shadow drains 1 STR from Gerakis: Weakened for 2d4 = 5 turns (no save)` | A shadow's hit draining STR, as the manual describes the monster. |
| `At rest: Seneca casts Cure Serious Wounds on Gerakis (4th-level slots: 1 left)` | A priest's cast before a rest, with [Resting as in AD&D](FEATURES.md#resting-as-in-add). |
| `    Dispel Magic on Slig's Blessed: d100 = 60, needs 85 or less (50 + 5 x 7 - 5 x 0 (its caster's level)) -> dispelled` | Dispel Magic trying one effect on its target. |
| `Cilla can't cast Fireball there: no line of sight` | A spell you clicked to cast that the game refused, and why: no creature there, not a creature that spell takes, a wall too long, no line of sight, or too far away. The game itself only crosses out the pointer. |
| `Script: random monsters come (request 8: 32766, 1, 0)` | Something a script asked the game to do: the party resting, random monsters, an arena bout, a cinematic, game over. The numbers are the request's own values. The everyday ones (doors, blocked cells, music, creatures changing sides) only show with "Show unlabelled rolls". |
| `Cilla's STR 12 -> 16` | A party member's ability score changed, once the change holds: a spell's or effect's (Strength, Remove Curse giving back a lowered STR, Raise Dead's point of CON), and the game's own. |
| `    Abjure on Y: d20 = 14, needs 12 or more (11 - caster level 5 + its level 6) -> sent away` | Abjure sends a summoned creature away (1000 damage) on a d20 at or over 11 - the caster's level + the creature's. |
| `Seneca turns Zombie: d20 = 14, needs 10+ (priest level 3 vs 2 HD, AD&D's table) -> turned: flees 3d4 = 7 rounds (Afraid)` | Turn Undead with AD&D's table, with [Spells and psionics as the manual describes them](FEATURES.md#spells-and-psionics-as-the-manual-describes-them): turned undead flee ([AD&D's turning table](HOW-THE-GAME-WORKS.md#adds-turning-table)). |
| `    Summoning: 1d3 = 2 picks which of its 3 creatures comes` | Which creature a summoning spell brings. |
| `    Mirror Image on X: d100 = 41, 75 or less strikes an image -> an image is struck instead, the blow lost` | A blow on someone with Mirror Image or Reflected Image up. |
| `X is confused: d10 = 4 -> does nothing` | A confused creature's turn: the d10 picks what it does. |
| `Paralysing attack: lasts 7 rounds unless saved against (2d4 = [4 + 3] = 7)` | A monster's power the game has no name for, named by what it does. |
| `Y's saving throw vs Fireball from X (spell): d20 = 12 +1 Blessed = 13, needs 11 (55% to save) -> saved: half damage, 19 of 38` | A saving throw, each modifier by name. More below the table. |
| `Y's saving throw vs Spook from X (...): d20 = 9 -1 Spook, the caster's levels = 8, needs 16 (...) -> failed` | A save against [Spook](FEATURES.md#new-wizard-spells), one of the new spells: 1 worse for every 2 levels its caster casts it at (at most −6). |
| `Guard's saving throw vs Hold Person from Seneca (...): Guard is too big for Hold Person -> unaffected` | With [Creature size as in AD&D](FEATURES.md#creature-size): Hold Person, Charm Person, or Charm Person or Mammal on a large person, which they don't take on: no roll, and no effect. |
| `X gives Blessed to Y, Z: +1 to hit, +1 on saves` | A spell or psionic effect starting, with what it does. |

**The lines above, in more detail.**

- A spell's damage roll, rolled for each target before its saving throw, with the spell's formula from the game's data. Damage stops growing at caster level 10 (Fireball does at most 10d6). Magic Missile, Flame Arrow and Minute Meteors are rolled elsewhere in the game, without the caster's level, so their line says how many steps the dice stand for.
- With [Spells roll to hit](FEATURES.md#spells-roll-to-hit): a missile spell's or a touch spell's attack roll, after its damage roll (the game rolls the dice first). THAC0 (Acid Arrow's a fighter's of the caster's level (a Scholar's 1 worse)), the DEX (missile) or STR (touch) adjustment, the rest of the game's to-hit adjustments (`spells`: Bless, Prayer, the target's Blur...) and a monster's `difficulty`, against the target's AC. A miss does nothing: the damage line before it is lost, and "Miss" floats over the target. Other lines of the kind: `Ester's Cause Light Wounds at Slig: touch attack d20 = 15, needs 10+ (55%) (THAC0 18, +1 STR, +1 spells; target AC 6) -> HIT`.
- What the spell really did to each creature, after its save, resistances and protections (or the healing it gave). A protection that halved it is named: Resist Fire or Cold, Protection from Fire or Lightning, Fire Shield, a Wanderer's own. A helpless creature, Out Cold or Paralyzed (held), gets no save and takes the most the dice can do (the game's damage code does that), marked `(Out Cold: the most the dice can do)` or `(Paralyzed: the most the dice can do)`: the damage line above it shows the roll, which it doesn't take. Other lines of the kind: `  Cilla takes 9 from Fireball (halved: Prot Fire)`.
- A weapon's or a spell arrow's spell on a hit (the Searing Blade's Focus Heat, a Chill Arrow's Chill Touch): its damage, duration and saving throw lines come straight after the hit, with no attack roll of their own, cast by the wielder or the archer (the save names it: `Cermak's saving throw vs Chill Touch from Elf (spell)`), a weapon's at level 6, a spell arrow's at the archer's level ([Spellarcher](KITS.md#spellarcher)).
- Acid Arrow's damage each round while the acid lasts; Sunstroke's heat each round while it holds; and an effect with charges using one up, with how many are left (Armor or Ironskin taking a hit, Mirror Image losing an image...). Other lines of the kind: `    Sunstroke's heat on Scar: 1d4 = 3 fire damage`; `    Improved AC on Slig: one charge used, 7 left`.
- The [6th-level priest spells](FEATURES.md#6th-level-priest-spells)' own lines: Harm leaving 1d4 hit points (the dice the game rolls go unused), Wall of Thorns' damage by the creature's AC in place of the dice rolled, and a creature that fails its save against Whirlwind losing its next turn. Other lines of the kind: `  Wall of Thorns' wall instead: 8 + AC 3 = 11`; `    Slig is swept off its feet: loses its next turn`.
- The amount Strength (or Adrenalin Control) adds to STR, and the [new spells](FEATURES.md#new-wizard-spells) Cat's Grace to DEX and Friends to CHA. With [Spells and psionics as the manual describes them](FEATURES.md#spells-and-psionics-as-the-manual-describes-them) Strength's and Cat's Grace's die is by class, the class named: `Strength: 1d8 = 6 (fighter) -> Ester's STR +6`, `Cat's Grace: 1d8 = 3 (thief) -> Seneca's DEX +3`. Other lines of the kind: `Cat's Grace: 1d6 = 4 -> Gerakis's DEX +4 while it lasts (at most 24)`; `Friends: 2d4 = [4 + 3] = 7 -> Xan's CHA +7 while it lasts (at most 25)`.
- The magic resistance roll (only shown for targets that have some), counting Mind Bar, Lower Resistance and the Amulet of Magic Resistance (`+15 Amulet of Magic Resistance`): 30% + 1% its caster's level off for a Lower Resistance on the creature (the manual's; the game's halved it). A Lower Resistance being cast takes the bigger of the two off its own roll, its own 30 + level or the one on the creature. Other lines of the kind: `Guard magic resistance 20% (-40 Lower Resistance on it, level 10) vs Scare: ...`; `Templar magic resistance 20% (-40 this Lower Resistance, level 10) vs Lower Resistance to Magic: ...`
- What [Spells and psionics as the manual describes them](FEATURES.md#spells-and-psionics-as-the-manual-describes-them) (each spell: [in more detail](HOW-THE-GAME-WORKS.md#each-spell-in-more-detail)) does beyond the game: Chill Touch on an undead, Cloudkill's kill by hit dice (`4 to 5 HD: the save failed` for the middle band; the death then said as `  Guard is slain by Cloudkill`), damage freeing a creature Rainbow Pattern holds, Cell Adjustment's 1d4 and its cure, Heal curing Feeblemind, and a feebleminded creature's psionic power failing its check. Other lines of the kind: `Cloudkill: Guard dies (under 4 HD: no save; its level for saves 3)`; `    Jenna takes 14 damage: Rainbow Pattern's hold on it ends`; `Cell Adjustment: 1d4 = 3 -> Seneca healed 3 HP, and Seneca is cured of disease`; `Heal cures Seneca's Feeblemind: INT and WIS as they were`; `Seneca is feebleminded: Biofeedback can't be used (no psionics)`.
- The monsters as the manual describes them (the same box): a shadow's or greater shadow's hit draining STR in place of its cold or paralysis (the STR change follows as the game works it out), a Tari's bite that rolled the game's 1 in 10 for disease and then the d2 that makes it the manual's 1 in 20 (on a 1 the disease's own save comes next), a djinn's first turn of a fight. Other lines of the kind: `Tari's bite on Seneca: 1 in 10, and a d2 for the manual's 1 in 20: 2 -> no disease`; `Djinn turns invisible (14 rounds) and makes 6 mirror images of itself`.
- [Resting as in AD&D](FEATURES.md#resting-as-in-add): a priest's or psionicist's cast before the rest, with the slots of that level (or PSP) it has left after it (the healing then follows as the game's own lines), and each member's natural healing: 3, CON's part, the total, and the hit points after (`(+2: no more than the most)` when the most stopped it). Other lines of the kind: `At rest: K'ratchek casts Cell Adjustment on Cilla (17 PSP left)`; `Gerakis rests 8 hours: +3, +2 (CON 16) = +5, now 35/40 HP`.
- Dispel Magic tries each effect on its target separately: 50 + 5 for each of the dispeller's levels, less 5 for each level the effect was cast at (of every effect of that kind on it: usually one). It can't touch some (Biofeedback, Diseased, Feeblemind, Poisoned, Graft Weapon, No spell use, Stuck, Mind Bar and a few more).
- Turn Undead, by AD&D's table: a number is the d20 needed to turn the undead, which are Afraid and flee for the rounds shown; T, D and D\* are the table's turned, destroyed and destroyed with more of its kind, all with no roll, and "no chance" its ---. A priest who fails can't try that undead again in the fight. Other lines of the kind: `Seneca turns Zombie: d20 = 5, needs 10+ (...) -> not turned: can't try again on it this fight`; `Seneca can't turn Zombie again: failed against it this fight`; `Lex turns Zombie: destroyed automatically (D) (...)`; `Lex turns Zombie: destroyed automatically (D*), and up to 2d4 = 5 more of its kind this turning (...)`; `Lex turns Zombie: destroyed, one of the D*'s more of its kind (4 left)`; `Seneca turns Shadow King: no chance (...)`. In full, with the game's own rule beside it: [Turn Undead](HOW-THE-GAME-WORKS.md#turn-undead).
- A blow or spell on someone with Mirror Image or Reflected Image up: the d100 against the chance an image takes it (Reflected Image's 50%). A spell from the target's own side never strikes an image. Other lines of the kind: `... -> the blow gets through`; `..., a spell from its own side -> no image takes it`.
- A confused creature's turn: the d10 picks whether it runs off, does nothing, fights for a side picked at random (the d2 under it) or acts normally. Other lines of the kind: `    X fights on the monsters' side this turn (d2 = 2)`.
- A monster's power the game has no name for (its records 172-195), named by what its record does: the effect it puts on (Paralysing, Disease, Entangling, Poison attack), else its damage's kind (`Fire attack (6d6 fire)`), else its number (`special attack 190`). Dice rolled just before the save are how long the effect would last.
- A saving throw: which of the target's five saves it uses, the d20, each of the game's modifiers by name (anything the log can't account for shows as `other`), the number it had to reach and the chance of that; for a damaging spell, what the save left of that target's damage roll. More below the table.
- A spell or psionic effect starting or ending, with what it does in the game's code where that is known: to-hit, AC and saving throws, movement and attacks, whether the creature can attack or cast, who controls it (see [Spells and effects](HOW-THE-GAME-WORKS.md#spells-and-effects)). `Stuck on Y` (no "gives") is an effect a creature has from a spell on the ground or cast on itself. Other lines of the kind: `Blessed ends on Y`; `X gives Paralyzed to Y, in place of the one it had: ...`, an effect put on someone who has it already: the game takes the old one off and puts the new one on with its own time, which can be shorter (Rainbow Pattern's hold over a longer Hold Person ends sooner), so the effect lasts on and its end comes at the new one's time. A recast that reuses the same effect record is reported when it changes the scheduled expiration.

**Saving throws, in more detail.** The modifiers are those of [the game's saving
throws](HOW-THE-GAME-WORKS.md#the-games-saving-throws). The line names the
spell save and, against fire, cold and electricity, DEX's adjustment (`+5 DEX
21 dodging`): the game's own petrification/polymorph and doubled d20 are gone
([Saving throws against spells](FEATURES.md#spells-saved-against-with-the-spell-save)). A natural 1 always fails and a natural 20 saves, unless no save is allowed:
`none allowed (cannot save) -> failed` (`cannot save, even on a natural 20` when the d20 was a 20) is a save the game gives −100 (Chaos for
all but warriors, Cloudkill, Scare below 6th level, Color Spray with the manual's
spells): it fails (the game's own compare read the total as a big number and
the creature saved; the patched game's compare is signed, [a bug
fixed](GAME-BUGS.md#spells-and-psionics) whatever the Options). With [Spells and
psionics as the manual describes
them](FEATURES.md#spells-and-psionics-as-the-manual-describes-them) the line also
counts `+2 Fire Shield` against fire and cold and `+1 Blur`.
For a damaging spell the result says what the save left: `saved: half damage, 19
of 38`, `failed: full damage, 38`, or `saved: no damage` for spells such as
Chill Touch (`saved: no damage (not 14)` with the damage rolled); a creature that
saves without a roll has `not needed (saves automatically) -> saved`; the HP line after it shows what the creature really lost, once
resistances and protections have had their say. A failed save also lets the
spell's effect take hold. Spells left on the ground (Grease, clouds) make
creatures save again as they stay in them; those lines have no "from".

## Checks, thief skills and searches

| Line | Meaning |
|---|---|
| `X DEX check: d20 = 9, needs 16 or less (DEX 16) -> success` | An ability check. A natural 20 always fails. |
| `Daaki CHA check: 0-19 = 15, needs 16 or less (CHA 20 - 4) -> success` | An ability check a script makes with a roll of its own. |
| `Daaki shoots at the archery target (15 squares from the target, 8 from the Bowyer): 0-20 = 2, needs under 14 (DEX 21 - 15 / 2), the centre 4 or less -> the centre: the Bowyer's reward, 6 Arrows +2` | A shot at the Bowyer's archery target in Teaquetzl: the roll, what it needed, how far the archer is from the target and from the Bowyer, and why a centre shot did or didn't earn his arrows (more than 13 squares from the target, the Bowyer within 25, once a game). |
| `Cilla tries to open locks: d100 = 35, needs 40 or less -> success` | A thief skill roll. |
| `Cilla tries to climb walls: d100 = 40 -> failure (an effect stops it)` | A thief skill an effect rules out, with no chance shown. |
| `Zulak uses Graft Weapon: power check d20 = 14, needs 11 or less -> it fails` | A psionic power's check: a d20 at or under the power's score. |
| `    K'ratchek spends 16 PSP (52 -> 36)` | PSP used for a power, or to keep one up. |
| `Gerakis's psionic defence: d6 = 5 and 6, both need over 4 (the attacker's power check d20) -> resisted` | A psionic attack mode (Ego Whip, Id Insinuation, Psychic Crush, Psionic Blast) resisted or not: its target rolls 1 to its defence twice, each needing more than the attacker's power check (see [Psionics](HOW-THE-GAME-WORKS.md#psionics)). |
| `Cilla picks Tobrian's pocket: d100 = 23, needs 45 or less -> success` | A thief's Pick Pockets button on the USE screen. |
| `  Daaki moves silently to get away: d100 = 12, needs 55 or less -> success` | A failed pick: a move silently roll to get away. |
| `Cilla tries to open locks: d100 = 40 -> failure (Cilla failed this lock at this thief level: another try once a level is gained)` | With **Thieves as in AD&D**, a lock this thief has failed, tried again before a level is gained (see [Thief skills from AD&D's table](FEATURES.md#thief-skills-from-adds-table)): no chance, whatever the roll. Another thief may still try. |
| `Tezral hides in shadows: d100 = 21, needs 27 or less (54, halved in daylight) -> hidden` | A thief's or ranger's hiding at the start of its turn. |
| `    X's special effect on Y: d10 = 1, works on a 1 -> it works` | The 1-in-10 extra effect some creatures' hits have. |
| `    X's Bone Long Sword nearly broke: 0 on 0-7, then 12 on 0-19 (needed 0)` | A plain weapon that nearly broke. |
| `  Rampager's acid on Gerakis's Leather Chest Armor: d20 = 12, needs 10 (AD&D's, 10 for leather; the game's: destroyed without a roll) -> safe` | An item the Rampager's acid or the Babau's corroding touch could destroy: the d20, the number it needed and whose number that was (see [Items saving against acid](FEATURES.md#items-saving-against-acid)). |
| `  Detonate's blast on Cilla's Bone Helm: d20 = 7, breaks it under 15 (15) -> DESTROYED` | Detonate (a daggoran's too) trying to destroy its target's worn item that breaks most easily, on a d20 under 15 less its plus (see [Psionics](HOW-THE-GAME-WORKS.md#psionics)). |
| `Haystack searched: 0-10 = 7, an old, soiled loincloth (the party's 2nd find of 6 in hay)` | Searching a junk pile, a haystack or a wardrobe. |

**The lines above, in more detail.**

- An ability check a script makes with a roll of its own rather than the game's check, against the character acting (the leader outside a fight): talking Chahl round, breaking chains, spotting a secret door. The roll is shown as the script makes it (0 to 19, say), with what it needed. Other lines of the kind: `Cilla INT check: d20 = 3, needs 4 or less (INT 14 - 10) -> success`.
- A thief skill roll (see [How the game works out thief skills](HOW-THE-GAME-WORKS.md#how-the-game-works-out-thief-skills)), and what its chance is made of. Other lines of the kind: `    open locks 40 = 18 + 16 thief level 4 + 10 elf...`
- A thief skill an effect rules out, with no chance shown; and the last parts of a chance: the situation's bonus for this attempt, and a Swashbuckler's bad luck (`-7 Swashbuckler's bad luck`; on a pocket `(45 - 7, a Swashbuckler's bad luck)`, hiding and moving silently `; - 7, a Swashbuckler's bad luck`). Other lines of the kind: `    open locks 52 = ... +10 this attempt`.
- A psionic power's check (see [Psionics](HOW-THE-GAME-WORKS.md#psionics)): a d20 at or under the power's score, the ability it uses plus the power's adjustment. A failure is the game's `psionic power check fails`, and costs half the PSP. A line `... within X's Synaptic Static: ...` comes first when someone else keeps Synaptic Static up. Other lines of the kind: `    power score 11 = 16 CON - 5 Graft Weapon`.
- PSP used for a power (or to keep one up), and PSP coming back. Other lines of the kind: `    Cyrus regains 8 PSP (20 -> 28)`.
- A thief's Pick Pockets button on the USE screen (see [Picking pockets](FEATURES.md#picking-pockets)): the d100 against the thief's pick pockets, then what came of it on the line below. For one of the three weapons worth XP, `  Cilla receives 200 experience points!` follows. With nothing small left on the person, the thief takes their coins instead, the last try on them: `  coins: 3d4+3 (2 to 5 for each of 3 thief levels) = 11` and `  Cilla lifts 11 ceramic pieces from Tobrian's purse, all there was to take.` Other lines of the kind: `  Cilla lifts Stone Dagger from Tobrian unnoticed.`
- A failed try: a move silently roll to get away. Made, the thief slips away and may try the same person again; missed, they're caught. A thief may go on trying until caught or until they take the coins. Caught (**Thieves as in AD&D**) means `  Tobrian catches Daaki's hand!` and `  (Daaki may try Tobrian again once a thief level is gained)`; a try before then is `Tobrian remembers Daaki, and keeps a close hand on their purse. (Daaki was caught at this thief level: ...)` with no roll. Another line of the kind: `  Daaki fumbles Tobrian's pockets, but slips away unnoticed.`
- A thief's or ranger's hiding and moving silently at the start of their turn ([hiding to backstab](FEATURES.md#hiding-in-shadows-to-backstab)), or why they can't: an enemy in one of the eight squares around them. Other lines of the kind: `  Tezral moves silently: ...`; `Tezral can't hide in shadows: Slig is right beside them`.
- The 1-in-10 extra effect some creatures' hits have: the disease of the game's Blue Slaad. With [the manual's monsters](FEATURES.md#spells-and-psionics-as-the-manual-describes-them) (the default; [which](HOW-THE-GAME-WORKS.md#the-monsters-as-the-manual-describes-them)) the Blue Slaad has deadly poison instead, with no d10, and the roll is a Tari's bite's, made 1 in 20 by a d2 more. A thri-kreen's paralysing bite, from 5th level, rolls no d10: its hit queues the paralysis, and the target's save is the roll.
- The weapon check the game makes after an attack sequence whose last attack hit. Only non-magical wood, bone, stone and obsidian weapons can break (and not every kind: clubs and quarterstaffs can't): they break when a 0-7 roll and then a 0-19 roll both come up 0, 1 chance in 160. The line only appears when the first roll comes up 0. Other lines of the kind: `... BREAKS`.
- Searching a junk pile, a haystack or a wardrobe: the game's roll, what it found, and how far its count has got (see [Searching junk, hay and wardrobes](HOW-THE-GAME-WORKS.md#searching-junk-hay-and-wardrobes)); a rat's bite or a falling pot rolls its damage the same way. Other lines of the kind: `  The rat's bite: 0-4 = 3 damage`.

## Inventory and shops

| Line | Meaning |
|---|---|
| `Ester takes Bone Axe, Guava (4)` | **T** or **Shift+T** with a body's or chest's window open: what each member took. |
| `Gerakis sells 9 things for 95 ceramic pieces: Wooden Club 1, Bone Axe 4, ...` | **S** on a shop's screen: what the member on show sold. |

**The lines above, in more detail.**

- **T** or **Shift+T** with a body's or chest's window open ([Looting a body](FEATURES.md#looting-a-body-t-and-shiftt)): what each member took, what didn't fit, and with Shift+T the plain weapons left behind. Other lines of the kind: `No room in the backpacks for: Leather Chest Armour`; `Plain weapons left: Wooden Club`.
- **S** on a shop's screen ([Selling plain gear](FEATURES.md#selling-plain-gear-s)): what the member on show sold, each with its price. Other lines of the kind: `Gerakis has no plain gear in the backpack to sell.`

## Hit points, kills and levels

| Line | Meaning |
|---|---|
| `  Slig now 8/18 HP (-10)` | A combatant's hit points going down or up. |
| `  Gerrard regenerates 1 HP (CON 22), now 16/35 HP` | A hit point back by itself, to a party member with CON 20 or more, at AD&D's rate by CON ([CON as in AD&D](FEATURES.md#con-as-in-add): an hour at 20 to 10 minutes at 25; the game's every 5 minutes of game time). |
| `  Rampager now 69/72 HP (-3: 3 of the 7 rolled, non-magical weapons do half)` | A weapon hit that took less than its roll, or none. |
| `Cilla shakes off Psionic Blast's imagined wounds as the fight ends: +23 HP, now 30/38` | Psionic Blast's imagined wounds given back as a fight ends. |
| `Slig is killed` | A creature dying. What it's worth comes on the XP line below, only if the party gains it (the opening fight in the arena gives none, whoever dies). |
| `Fight over: 3 rounds, 4 kills; the party dealt 61 damage and took 19` | A fight's summary as it ends. |
| `XP: Gerakis +67, K'ratchek +22, ... (for Slig 270)` | Experience the party got, and for which kills. |
| `XP: Dag +137 (+12 for Fighter, STR 17) (for Mountain Stalker 500)` | Experience with the bonus for high prime requisites. |
| `Cilla is now a 3rd level Ranger` | A level gained. |
| `    max HP unchanged: the game divides the hit point total by the classes, ...` | A multiclass level that added no hit points. |
| `Cilla's 3rd Ranger level: hit points d10 = 2, raised to 3 for CON 21` | The hit point roll for a new level. |

**The lines above, in more detail.**

- Any combatant's hit points going down or up, with what's left out of their most. The game never shows a monster's HP; this does. The line comes just after the damage that caused it (sometimes after the next roll, when the game is quick). Other lines of the kind: `  Gerakis now 51/54 HP (+1)`.
- A weapon hit that took less than its roll, or none at all (no HP lost three seconds on, or by the next round), with the reason when the monster's own defences give one (what weapons hurt it); otherwise "a protection or resistance took it" (Stoneskin, say). Other lines of the kind: `  Mastyrial takes none of the 6 damage: crushing weapons can't hurt it`.
- A party member's hit points taken by Psionic Blast given back once the fight is over (its wounds are imagined: see [the game's bugs, fixed](GAME-BUGS.md#spells-and-psionics)); one knocked out wakes with them (until the fight's end a blow that would kill such a member knocks it out), one Dying or dead gets none back. Other lines of the kind: `Gerakis wakes and shakes off ...`
- A fight's summary as it ends (the game's fight flag down for 2 seconds; each arena wave its own): its rounds, the party's kills, the damage the party dealt (spells too) and took, then a line for each member who attacked, dealt or took damage or killed: weapon attacks that hit out of those made, damage dealt, kills, damage taken. A kill goes to whoever hurt the creature last; a spell's damage to its caster (the cast's record names it, so Magic Missile's too), and only a party member's spells count for the party (a monster's don't). The readable layout shows it as the fight's close, every member's line shown. Other lines of the kind: `    Seneca: 2 of 2 attacks hit, 30 dealt, 1 kill`; `    Jenna: 3 of 3 attacks hit, 22 dealt, took 6`.
- Experience the party got, and for which kills, with each one's XP from its character sheet. The game gives it right after the kill: an equal share to each character, split again between a multiclass character's classes (the sheet counts XP per class, so a three-class thri-kreen shows a third of the share).
- The same with the bonus for high prime requisites, which the Loader adds to the game's award: 10% for each class whose prime requisites are all 16 or more, divided by the character's classes ([Experience and levels](PLAYER-GUIDE.md#experience-and-levels)). The figure after the name includes it.
- A level gained, and the new maximum HP. Other lines of the kind: `    max HP 15 -> 21 (+6)`.
- A multiclass character gained a level and its most hit points stayed the same: every class level rolls its die, but the game divides the whole total by the number of classes, so a small roll can add only a fraction (it counts at a later level). A human who changed class gets none in the new class until its level passes the old class's.
- The hit point roll for a new level: the class's die (d8 clerics and druids, d10 fighters, gladiators and rangers, d4 preservers, d6 psionicists and thieves; the Battle Mage and Arcanist [kits](KITS.md#preserver-kits) have their own), never less than 2, 3 or 4 with CON 20, 21-22 or 23+, and doubled for half-giants. After level 9 or 10 there's no roll, just a fixed gain (thieves roll at 10th too with [Level cap by XP](FEATURES.md#level-cap-by-xp)). With [the better of two](FEATURES.md#hit-dice-the-better-of-two) both rolls show (`d10 = 2 and 7, the better 7`), and with [multiclass hit points](FEATURES.md#multiclass-hit-points) CON's bonus on the die (`, +4 CON 18, into the total shared by 3 classes`).

## Character creation

| Line | Meaning |
|---|---|
| `Character creation, DEX 9: best of four 4d4 (4, 4, 4, 4) = 4, +4, -1 dwarf = 7, raised to 9 (the Thief's minimum)` | An ability score rolled on the character creation screen. |
| `Character creation: the six scores add up to 101` | After the scores, what they add up to: the most they may add up to with [Scores and hit points as rolled](FEATURES.md#scores-and-hit-points-as-rolled). |
| `Character creation, hit points 15: Fighter d10 per level: 7 + 9; Thief d6 per level: 5 + 1 = 22, / 2 classes = 11, +4 CON 16 = 15` | A new character's hit points. |
| `Character creation: a name picked at random, 1d33 = 6` | The game picks a new name from its lists when the sex or race changes. |
| `Grog starts with a plain obsidian long sword for the weapon specialization chosen, in place of the bone long sword` | A new character's starting weapon: a plain one of its [weapon spec](WEAPON-SPECS.md#starting-weapons). |
| `Swat starts with more gear: Short Sword (in hand), Arm Armor, Leg Armor` | What [Fuller starting gear](FEATURES.md#fuller-starting-gear) gave a new character. |
| `Halton starts with a Fine Bow (+1 to hit): a Spellarcher's` | A new Spellarcher's Fine Bow ([its kit](KITS.md#spellarcher)). |
| `Yilballa's Chest Armor is left behind: their classes can't use it` | Starting gear its classes can't use, left behind. |

**The lines above, in more detail.**

- An ability score rolled on the character creation screen (see [Character creation](HOW-THE-GAME-WORKS.md#character-creation)). The die rolls a whole character several times while it tumbles; the log gives only the character the die stops on, once it stops. A hit point roll that came too fast to record leaves a note: `some of its rolls came too fast to record`.
- The new character's hit points: a die for every level of every class, divided by the number of classes, plus CON's bonus (see [Character creation](HOW-THE-GAME-WORKS.md#character-creation)). With [the better of two](FEATURES.md#hit-dice-the-better-of-two) each die shows both rolls (`10 (the better of 2 and 10)`); with [multiclass hit points](FEATURES.md#multiclass-hit-points) CON's bonus goes on each die before the total is shared (`+2 CON 16 on each of 4 dice = 30, / 2 classes = 15`).
- A new character's starting weapon swapped for a plain one of its [weapon spec](WEAPON-SPECS.md#starting-weapons), or fitted to its [kit](KITS.md#starting-gear), with a reason when the spec's own weapon can't be used. Other lines of the kind: `T'Jun starts with a plain bone axe for the Battle Mage's weapon spec, in place of the Quarterstaff`; `Rok starts with a second bone long sword in the left hand: a Ravager fights without a shield`.
- What [Fuller starting gear](FEATURES.md#fuller-starting-gear) gave a new character. Other lines of the kind: `Swat takes the Club from the backpack in hand`.
- A new Spellarcher's Fine Bow and its arrows, by the touch spells it picked ([its kit](KITS.md#spellarcher)). Other lines of the kind: `Halton starts with 24 chill arrows in the quiver: Chill Touch picked`; `Garn starts with 24 arrows: no touch spell picked`.
- Starting gear taken away: what its classes ([class restrictions](FEATURES.md#class-restrictions)) or its [kit](KITS.md#starting-gear) forbid. Other lines of the kind: `Xan's Chest Armor is left behind: a multiclass preserver can't cast in armour`; `Rok's Shield is left behind: a Shadowblade fights without a shield`; `Aticus's Long Sword goes into the backpack: a Seeker can't use it`.

## Ages

With [ages](FEATURES.md#ages-and-magical-aging) on:

| Line | Meaning |
|---|---|
| `Cyrus the Great is 21 (a human: 15 + 1d8 = [6]); middle-aged at 40.` | A character's starting age: the race's base and dice (Table 7), the first time the Loader sees a character with none (the game's own party, an older save). |
| `Cyrus the Great is 21 (a human: 15 + 1d8 = 6, as the creation screen rolled); middle-aged at 40.` | A character just made: the age the creation screen showed as AGE, given at DONE. |
| `A year has passed: Gerakis is 60, middle-aged: STR -1, CON -1, INT +1, WIS +1.` | Each 365 days of game time, every party member a year older, with the score changes of an age category reached. At the most the race lives, the line ends `; that is the most a human lives: Gerakis dies of old age.` |
| `K'ratchek's system shock (Haste's aging): d100 = 89, needs 99 or less (CON 19) -> survives` | Haste's system shock roll, and the year it ages a survivor. |
| `Gerakis's system shock (Restore Youth): d100 = 40, needs 99 or less (CON 22) -> survives` | Restore Youth's system shock roll. |

**The lines above, in more detail.**

- Haste's system shock roll by CON for each creature it speeds, and a party member who survives a year older. A failed roll kills: `-> fails: K'ratchek dies`. Other lines of the kind: `  K'ratchek ages 1 year (Haste): now 7.`
- Restore Youth's system shock roll, then the magical years it takes back; with none to take back, no roll. Other lines of the kind: `  Gerakis grows younger 10 years (Restore Youth): now 27.`; `Restore Youth: Gerakis has no magical years to take back (27, Gerakis's true age).`

## Everything else

| Line | Meaning |
|---|---|
| `Message: Long Sword is broken !` | The game's own message boxes: broken or corroded weapons and armour, level-ups, "NO PATH FROM HERE" and so on. |
| `Dinos cooks the vulture and the party eats with him: ... restored as after a full rest (HP, PSP and spell slots); the game gives each 100 XP` | Dinos asked about the cooked vulture (see [The cooked vulture](FEATURES.md#the-cooked-vulture)); the XP itself is on the `XP:` line after it. |
| `Dreamwalker reads the scroll of Magic Missile: d100 = 37, needs 60 or less (INT 14) -> learnt` | A preserver's try at a scroll's spell ([Preservers' INT](FEATURES.md#preservers-int)). |
| `The shocking arrows go back to Lex from Jenna: only a Spellarcher carries them (7)` (how many) | Spell arrows another party member was given, back with the party's Spellarcher (out of a fight, the inventory shut): onto its stack of that spell, or into its pack. |
| `Gerakis's chill arrows are put away in the backpack: only a Spellarcher readies them (24)` (how many) | Spell arrows found readied by someone who isn't a Spellarcher, with none in the party (from an older save, say), moved to a free cell of that member's backpack (out of a fight, the inventory shut). |
| `Daaki makes one of the chill arrows in the quiver (1 of 24 now): a 1st-level slot used; ...` | A Spellarcher's arrow button (see [Spellarcher](KITS.md#spellarcher)): the arrow joins that spell's stack wherever it is; a new stack goes in the quiver if it is empty (`in the quiver`), else in the pack (`in the pack`). |
| `Gerakis specializes in the long sword and the gythka.` | The game's own party made ready for the rule changes that are on. |
| `Gerakis's Leg Armor is now counted as worn (it had been counted as held, and gave no AC)` | Once, as a save is loaded: armour (or a cloak) an earlier version of the Loader gave to a character's held items, where the game counted it for no AC, moved to what the character wears. |
| `Cilla's Thieves' Tools is put away in the backpack (it had been counted as held)`; `Lex's Bow is now held, ready to use (it had been counted as worn)` | The same, once as a save is loaded, for other items an earlier version left in the wrong list: a backpack item counted as held (a dagger, Thieves' Tools), or a weapon counted as worn (a bow, which the game didn't shoot with); `... is now counted as worn (it had been counted as held)` for another worn thing (arrows, a ring). |
| `Tamar, a Healer, knows the sphere of the cosmos's spells: Abjure, Cloak of Bravery, ...` | A Healer made by an earlier version given its cosmos spells, once, as a save is loaded. |
| `Memory is running low: 23 KB spare with the map open. The game stops with "Out of memory" when it runs out: save and restart the game soon (a new start has it all back).` | The game's memory running low in a long session, said once until it recovers (see ["Out of memory"](GAME-BUGS.md#screens-and-memory)). `Memory: upper memory had no room for the game's overlay buffer ...` says DOSBox's settings left it less room from the start. |
| `AC of Gerakis against Wild Mul: 8 (base 10, armour -1, DEX -1, other +0)` | Only with "Show unlabelled rolls": each AC the game works out for an attack, and what it is made of (the sheet's base, the armour and shield worn, DEX, and spells, rings and the rest). |
| `Dice: 1d8 = [3] = 3` | Dice the log couldn't tie to anything (for example a spell with no saving throw). |
| `Script roll: 0-9 = 4 (script position 1234)` | Only with "Show unlabelled rolls": a script's random number that is no search or check the log knows. |
| `    X's Bone Club can't break` | Only with "Show unlabelled rolls": a weapon that can't break. |
| `(The Loader stopped one of its own writes over the game's memory: ...)` | A safety net: the Loader refused one of its own writes to memory it must never touch. The line says where in the Loader it came from. Please report it. |
| `Loader error in the dice log: ...; it carries on` | The Loader failed to read an entry: please report it if it repeats. |

**The lines above, in more detail.**

- A try at a scroll's spell (see [Preservers' INT](FEATURES.md#preservers-int)): a preserver's d100 against INT's chance; a Shinobi's d100 against its read languages first, then INT's. A spell already known gives no line. Other lines of the kind: `Xan reads the scroll of Shield: read languages d100 = 70, needs 35 or less -> can't read it (the scroll is used up)`; `Xan can't learn Armor from the scroll: not one of a Shinobi's spells (the scroll is kept)`.
- The game's own party (START GAME with no party made) made ready for the rule changes that are on, once, in the game's first hour (see [The game's own party](FEATURES.md#the-games-own-party)). Other lines of the kind: `Gerakis carries a bone gythka in place of the club.`; `Cilla has no armour: a druid wears none.`; `Cilla knows Armor.`; `Cermak is an Arcanist.`; `Gerakis fights wild: Wild Fighting, as a fight starts.`
- Once, as a save is loaded: a [Healer](KITS.md#cleric-kits) made by an earlier version given its cosmos spells, a [Wilderness Avenger](KITS.md#multiclass-kits) its healing spells taken away, a Healer or Lifebinder its harming ones. Other lines of the kind: `Halton, a Wilderness Avenger, knows no healing spells: Cure Light Wounds, Blood Flow taken away`; `Tamar, a Healer, knows no harming spells: Cause Serious Wounds, Poison taken away`.
- Only with "Show unlabelled rolls": a weapon that can't break (a club or quarterstaff), a check the log couldn't name, and the game's raw random numbers with where they were asked for. Other lines of the kind: `Check: d20 = 7`; `rand() = 12345  (at 1234:5678)`.
- The Loader failed to read an entry, or the game rolled faster than the Loader could read: the log has a gap there. Please report the first if it repeats. Other lines of the kind: `(12 rolls came too fast to record)`.
