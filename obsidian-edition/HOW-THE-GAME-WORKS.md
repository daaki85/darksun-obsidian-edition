# How the game works

*Part of Obsidian Edition's documentation: the original game's own rules, for
the curious. [The README](README.md) is about the mod.*

What the game does that its manual doesn't say, from its code and checked in
play. The dice log shows each as it happens, and the
[rule changes](FEATURES.md#rule-changes) change some of it.

## Initiative

From the game's code: at the start of every round each combatant's initiative
is 20 + a roll of 0-9 + a DEX adjustment + Hasted +2, Slowed −2 and Blind −2.
The DEX adjustment has its own table: −6 at DEX 1, −4 at 2, −3 at 3, −2 at 4,
−1 at 5, none for 6-15, +1 at 16, +2 at 17-18, +3 at 19-20, +4 at 21-23 and
+5 at 24-25. The weapon makes no difference (there are no weapon speeds). The
highest score acts first; a second roll, 0-199, decides between equal scores
(the log shows it only for those). Choosing Wait lowers the character's score
to 10 (or by one, if it's 10 or less already) so they act later in the round.

## Spells and effects

What the log says about spells comes from the game's own spell records and
code, checked by casting each spell in a fight. Where the game differs from the
AD&D rules, the log follows the game.

**Damage.** Each spell's record gives its dice: base dice plus dice (and a flat
bonus) for each step of caster level, counted up to level 10. So Fireball and
Lightning Bolt do at most 10d6, and Burning Hands 1d3 + 2 a level. A save halves
the damage, or stops it all for spells such as Chill Touch. A creature that is
Out Cold gets no save and takes the most the dice can do.

**Saves.** Almost every spell is saved against with petrification/polymorph,
and against fire, cold and electricity the save's d20 counts double: see
[The game's saving throws](#the-games-saving-throws).

**How long.** A duration is (caster level × so much + dice) × a unit of time.
A round is 60 game seconds. Some effects last a number of uses instead
(charges):
- Stoneskin: 1 a level + 1d4. Any damage uses a charge, even fire that gets
  through, but only blows are stopped.
- Ironskin: 1d6 blows stopped.
- Mirror Image: 1 a level + 1d4 images. With the Loader each hit, and each
  foe's spell for one creature (not an area's, a cone's or a wall's), has a 75%
  chance to strike an image instead, the image vanishing and the blow or spell
  lost; the dice log shows each d100 (the game's own images worked otherwise:
  see [The game's bugs, fixed](FEATURES.md#the-games-bugs-fixed)).
- Invisibility: one attack or hostile spell ends it. Improved Invisibility is
  timed instead, so attacking doesn't end it.
- Minor Spell Turning: one spell turned back.
- Armor: a number of damaging hits, one charge each (with the Loader: see
  [The game's bugs, fixed](FEATURES.md#the-games-bugs-fixed)).

Charm, Feeblemind, Web and a few others last until removed.

**What effects do**, from the game's code:

| Effect | In the game |
|---|---|
| Blessed / Cursed | +1 / −1 to hit (Bless also +1 on saves); each one cancels the other instead of being added |
| Hasted / Slowed | Hasted: double movement and attacks, +2 initiative. Slowed: half movement and attacks, loses every other turn, −4 to hit, AC 4 worse, −2 initiative. Each cancels the other; Free Action and Protection from Paralysis stop Slow |
| Paralyzed | Loses its turns, can't move, fails every saving throw. Free Action and Protection from Paralysis stop it |
| Stuck (Grease, Web, Entangle, Solid Fog, Quicksand) | Can't move; Free Action stops it; some creatures are immune |
| Afraid | The computer runs it; it can't attack or cast. Undead are immune, and Cloak of Bravery stops the next fear (and ends) |
| Charmed | Joins the caster's side, run by the computer |
| Confused | Each turn a d10: 1 runs off, 2–6 does nothing, 7–9 fights for a side picked with a d2, 10 acts normally (the log shows the rolls) |
| Berserk | Fights for a side picked at random each turn; can't cast. In the game a party member could be left on the monsters' side when this or Confused ended; the patched game puts it back ([bugs fixed](FEATURES.md#the-games-bugs-fixed)) |
| Can't Attack (Stinking Cloud) | Can't attack or cast harmful spells |
| No spell use, Feeblemind | Can't cast spells |
| Blind | AC 4 worse, −2 initiative, can't cast spells that need sight |
| Acid (Acid Arrow) | 2d4 acid damage each round |
| Poisoned | Fatal (1000 damage) if time passes out of combat, for instance resting, before it wears off or is cured |
| Cloak of Fear | Whoever hits the wearer has Cause Fear cast on them, once |

Other things the game does its own way:
- Strength adds 1d6 to STR while it lasts, up to 24. The same goes for the
  psionic Adrenalin Control, and Weakened or lending strength takes it away
  (never below 3).
- Shillelagh, Flame Blade and Spiritual Hammer need an empty hand: with a
  weapon ready the game says "Failed, weapon in hand" and nothing happens.
- Death spells (Slay Living, Dismissal) do the target's HP + 10 on a failed save.
- In the arena, summonings fail ("Your summoning goes unanswered").
- A spell's caster level is the caster's highest level in a class that shares
  a sphere with the spell. Priests have one element each (cleric, druid and
  ranger classes come in air, earth, fire and water): Flame Blade, Focus Heat
  and Flame Strike are fire spells, Blood Flow and Dehydrate water, Deflection
  air, while spells such as Bless, Barkskin or Spiritual Hammer belong to
  every sphere. Cast by a priest of another element, an elemental spell counts
  caster level 0. The game shows each priest only their element's spells, so
  this only happens if a character somehow has the others.
- Clerics never have the common 4th and 5th-level priest spells: Cure Serious
  and Critical Wounds, Raise Dead, Neutralize Poison, Free Action and the rest
  are marked for druids alone (a cleric's 4th and 5th levels are its element's
  spells only). The mod's Healer kit gives them to a water cleric.

The spell's area catches its caster too. Cilla's Scare made her Afraid, and her
Fireball, cast at a Slig next to her, killed her.

## Psionics

Psionic powers are numbered after the spells (Detonate 138 to Thought Shield
171) and go through the same code: the same records for damage, saves and
effects, so the log treats them like spells and names them. Some things are
their own:

- **Level.** A power works at the character's psionicist level; anyone else
  with psionic powers counts as level 1.
- **PSP.** A power costs its PSP to use. Kept-up powers (Inertial Barrier,
  Biofeedback, Graft Weapon...) cost more PSP at the start of each round, and
  the game puts them on again for another round; when the PSP runs short, the
  power drops. The log shows every change in a party member's PSP
  (` K'ratchek spends 18 PSP (52 -> 34)`).
- **The power check.** Each use rolls a d20 that must come up at or under the
  power's score: the ability the power uses (CON for most psychometabolism and
  psychokinesis, WIS for telepathy and Disintegrate, INT for Superior
  Invisibility, Mind Bar and Synaptic Static) plus the power's adjustment, from
  −1 (Lend Health) to −7 (Mind Blank). A 1 always works and a 20 always fails;
  a failure says "psionic power check fails" and costs half the PSP. The game
  also keeps a number for each power a character knows, and adds anything
  above 1 to the score, but no code was found that raises it. Near someone
  else's **Synaptic Static**, the user first rolls a d20 against that number
  (the game reads the ability for it and drops it, so it's 1 for most
  characters): over it, "psionics disrupted by static". Otherwise the Static's
  keeper rolls a d20 at or under their own Synaptic Static score, and no lower
  than the user's, to disrupt it. The log shows each of these rolls.
- **Detonate** (the daggorans use it too): besides 1d10 from the blast, it
  picks the worn item that breaks most easily, the one with the lowest
  fragility number (under 6: a cloak 3, a bone helm or leather chest armour 4,
  bone scale arm and leg armour 5; a short sword's 6 is never picked; on a tie,
  the first), and destroys it outright on a d20 under 15 less its plus (70% for
  a plain item; one of a stack). The log shows the check.
- **Psionic defence.** Attacked by a psionic attack mode (Psychic Crush, Ego
  Whip, Id Insinuation, Psionic Blast), a character defends with WIS − 7, or
  with a defence mode already raised (used beforehand, it stays up at no cost
  each round) if that does better: the mode's rank plus half its cost, which
  the character pays again, if they can. A monster defends with its level where
  that's better. Two rolls of 1 to that number, both over the attacker's own
  roll for the power, resist it.
- **Mind Bar** adds 75% magic resistance against mind-affecting spells:
  charms, holds, Scare, Confusion, Chaos, Feeblemind, Minor Malison. The log's
  magic resistance line counts it, and Lower Resistance halving the result.
- **Body Weaponry** makes unarmed attacks 2d4; **Animal Affinity** at least 1d10.
- Monsters use them too: the Screamer Beetle's special attack is Psychic
  Crush (1d8, save vs paralysis/poison/death for half).

### Each power against the manual

What the game's code does with each power, next to the manual's text. Every use
also logs the power check and the PSP spent; a power with a save logs the save.

| Power | The manual | The game | The log |
|---|---|---|---|
| Detonate | 1d10 to everyone within 10'; may turn an item to ash | 1d10 to the target only, no save; then destroys its worn item that breaks most easily on a d20 under 15 less its plus (above) | the blast's damage and the item check |
| Disintegrate | save vs death or turned to ash | save vs paralysis/poison/death (the same save) or 10,000 damage | the save and the damage |
| Project Force | 1d6 plus the target's AC | 1d6 plus the target's AC (less against a good AC), no save | the 1d6 and the HP lost (with the AC in it) |
| Ballistic Attack | 1d6 on a successful hit | 1d6, no attack roll, no save | the damage |
| Control Body | the target fights for you at −6 to hit | Charmed for 5 rounds on a failed save vs paralysis/poison/death: it joins your side under the computer's control, with no −6 | the save and the charm |
| Inertial Barrier | halves damage from breath, missiles, gas, acid, ice storms | missile attacks miss its user outright; nothing else | "missile attacks miss it" |
| Animal Affinity | claws, 1d10 | unarmed attacks at least 1d10 | the effect |
| Energy Containment | no damage from electricity, cold, fire, heat, sound | no damage that is only fire, cold, electricity or magic | the effect |
| Life Draining | drains up to 6 HP as extra HP for an hour | 1d6 damage, the same as extra HP for the user | the drain roll and the HP |
| Absorb Disease | takes the target's disease to cure it | takes the disease (the mod's fix: the game also gave 1d6 STR) | the effect |
| Adrenalin Control | STR + 1 to 6 | STR + 1d6, at most 24 | the 1d6 and the STR |
| Biofeedback | damage −2 and AC −1 | AC −1 only; no damage is taken off | "AC −1" |
| Body Weaponry | the arm as a wood or steel weapon | unarmed attacks 2d4 | the effect |
| Cell Adjustment | heals wounds, cures diseases | heals 2 HP; cures nothing | the HP regained |
| Displacement | attacks miss the image; AC −2 | AC −2 | the effect |
| Enhanced Strength | STR up to 24, cost twice the points | STR 24 (a higher one kept), cost (24 − STR) × 2 | the effect and the PSP |
| Flesh Armor | armour by level, no penalties | AC 10 − level at best | the effect |
| Graft Weapon | +1 to hit, can't switch weapons | +1 to hit; stops picking pockets, locks and climbing | the effect |
| Lend Health | gives HP, within both maximums | gives the target's missing HP, keeping the user at 5 or more | the HP both ways |
| Share Strength | gives STR at 2 for 1 | target + a, user − 2a (a up to 24 − its STR and (the user's STR − 3) / 2) | the effects (not the amount) |
| Domination | controls the target; combat only | Charmed for 5 rounds on a failed spell save; combat only | the save and the charm |
| Mass Domination | up to 5 creatures | its record targets one creature, as Domination, for 10 rounds | the save and the charm |
| Psychic Crush | up to 6 damage | 1d8, half on a save vs paralysis/poison/death; psionic defence first | the defence, save and damage |
| Superior Invisibility | unseen; ends if it attacks | Invisible; attacking or casting at an enemy ends it | the effect |
| Ego Whip | stunned 1d4 rounds | can't attack or cast harmful spells for 1d4 rounds; psionic defence, no save | the defence and the effect |
| Id Insinuation | paralyzed 1d4 rounds; combat only | Paralyzed 1d4 rounds; psionic defence, no save; combat only | the defence and the effect |
| Psionic Blast | believes it has lost 80% of its HP | loses real HP down to a fifth of its maximum on a failed save vs paralysis/poison/death; psionic defence first | the defence, save and HP lost |
| Mind Bar | 75% resistance to mind spells | the same | the resistance roll |
| Synaptic Static | no one nearby can use psionics | its keeper can't; anyone else must beat the static (above) | the contest |
| Tower of Iron Will, Intellect Fortress, Mental Barrier, Mind Blank, Thought Shield | defences against psionic attacks | defence modes (above) | the defence rolls |

What each costs, from the game's own table, and for three of them worked out as
they're used: Enhanced Strength (24 less the target's STR) × 2, and Domination and
Mass Domination 3, 8, 13 or 18 by the target's level (below 6, below 11, below
16, and up):

| Power | Discipline | PSP to use | PSP each round kept up |
|---|---|---|---|
| Detonate | psychokinesis | 18 | — |
| Disintegrate | psychokinesis | 40 | — |
| Project Force | psychokinesis | 10 | — |
| Ballistic Attack | psychokinesis | 5 | — |
| Control Body | psychokinesis | 8 | — |
| Inertial Barrier | psychokinesis | 7 | 5 |
| Animal Affinity | psychometabolism | 15 | 4 |
| Energy Containment | psychometabolism | 10 | — |
| Life Draining | psychometabolism | 11 | — |
| Absorb Disease | psychometabolism | 12 | — |
| Adrenalin Control | psychometabolism | 8 | 4 |
| Biofeedback | psychometabolism | 6 | 3 |
| Body Weaponry | psychometabolism | 9 | 4 |
| Cell Adjustment | psychometabolism | 5 | — |
| Displacement | psychometabolism | 6 | 3 |
| Enhanced Strength | psychometabolism | (24 − STR) × 2 | 8 |
| Flesh Armor | psychometabolism | 8 | 4 |
| Graft Weapon | psychometabolism | 10 | 1 |
| Lend Health | psychometabolism | 4 | — |
| Share Strength | psychometabolism | 6 | 2 |
| Domination | telepathy | 3-18 by level | — |
| Mass Domination | telepathy | 3-18 by level | — |
| Psychic Crush (attack mode) | telepathy | 7 | — |
| Superior Invisibility | telepathy | 5 | 5 |
| Tower of Iron Will (defence mode) | telepathy | 6 | 0 |
| Ego Whip (attack mode) | telepathy | 4 | — |
| Id Insinuation (attack mode) | telepathy | 5 | — |
| Intellect Fortress (defence mode) | telepathy | 4 | 0 |
| Mental Barrier (defence mode) | telepathy | 3 | 0 |
| Mind Bar | telepathy | 6 | 4 |
| Mind Blank (defence mode) | telepathy | 0 | 0 |
| Psionic Blast (attack mode) | telepathy | 10 | — |
| Synaptic Static | telepathy | 15 | 10 |
| Thought Shield (defence mode) | telepathy | 1 | 0 |

## Character creation

Every click of the die on the creation screen (and every change of race or sex)
rolls a new character. From the game's code, and checked against the screen:

* **Abilities.** Each score is rolled four times as 4d4 + 4 + the race's
  adjustment, and the best of the four counts. That's 8 to 20 before the race's
  adjustment. The score is then raised, if need be, to the least that the
  classes allow: 17 in the class's prime requisite (STR for fighters and
  gladiators, WIS for clerics, druids, psionicists and rangers, INT for
  preservers, DEX for thieves), and otherwise 9 (clerics, fighters, preservers,
  thieves), 12 (druids, psionicists), 13 (gladiators) or 14 (rangers). A
  multiclass character takes the highest of their classes' minimums.
* **Race adjustments** (STR, DEX, CON, INT, WIS, CHA): dwarf +1 −1 +2 0 0 −2;
  elf 0 +2 −2 +1 −1 0; half-elf 0 +1 −1 0 0 0; half-giant +4 −5 +2 −5 −3 −3;
  halfling −2 +2 −1 0 +2 −1; mul +2 0 +1 −1 0 −2; thri-kreen 0 +2 0 −1 +1 −2.
  Humans have none.
* **Hit points.** One die for every level of every class (d8 clerics and
  druids, d10 fighters, gladiators and rangers, d4 preservers, d6 psionicists
  and thieves), doubled for half-giants. The total is divided by the number of
  classes (rounded down), and then CON's bonus is added for every level: a
  warrior's full bonus (+1 at CON 15, +2 at 16, +3 at 17, +4 at 18, +5 at
  19-20, +6 at 21-23, +7 at 24-25; −1 at 4-6, −2 at 2-3, −3 at 0-1), and at
  most +2 for levels in the other classes. There is no automatic maximum at
  first level: the first level rolls like the rest.
* **Choices without dice.** Raising a score to a new class's minimum (adding
  Thief raises DEX to 17) and PSP aren't rolled, so they don't appear in the
  log. The creation screen's other random numbers only choose pictures.
* **The total.** After the six scores comes what they add up to, the most they
  may add up to with
  [Scores and hit points as rolled](FEATURES.md#scores-and-hit-points-as-rolled).

Changing sex or race can make the game roll hit points twice, once with the
old scores and once with the new: the last hit point line is the one that
counts.

## Monsters' defences

From the game's damage code (DSUN.EXE); none of this is in the manual:

- Every creature has a monster kind, and each kind a resistance class and a
  set of properties, in a table the game fills when it starts.
- Every hit has damage kinds: fire, cold, electricity, acid, poison, draining,
  psionic, death, and for weapons crushing, edged or pointed, from the item's
  type; a natural (unarmed) attack's is crushing, fists and monsters' claws
  alike (with Obsidian Edition, a thri-kreen of the party's claws and Erdlu
  Claw's talons are edged: see [Erdlu Claw](FEATURES.md#new-wizard-spells)). A weapon's hit also carries its magic: one bit for +1 or better, one
  for +2 or better and one for +3 or better (the weapon's plus, or its
  ammunition's if that's higher). A monster's own attacks count as magical by
  its level: (level - 2) / 2, so a 6th-level monster hits like a +2 weapon.
- A resistance class is up to four rules: "these kinds of damage: this
  percent of it". The largest percent that applies counts. So "crushing, edged
  and pointed: 0%; +1 or better: 100%" is a monster only magical weapons hurt.
  The game's 14 classes come to: only +1 (or +2) weapons hurt it, sometimes
  with immunity to poison and draining, or to fire; half damage from
  non-magical weapons and psionic attacks (the Rampager); immune to crushing
  weapons (the mastyrials); immune to crushing and pointed weapons, fire and
  acid, so that only edged weapons hurt it (the slimes); immune to fire and
  cold (and half from electricity); half from fire; immune to poison; immune
  to psionic attacks.
- Properties: can't be charmed or held; unaffected by spells left on the
  ground (fogs, clouds, walls, Web, Grease); not held by Grease, Web,
  Entangle, Solid Fog or Quicksand; and hits that also cast one of the
  monsters' powers on the target: 2d6 cold, 2d6 or 20 acid, paralysis,
  poison of 10 or 30 damage, a deadly Poison, disease on 1 hit in 10. The 20
  acid (the Rampager's) and a corroding touch (the Babau's) can also destroy a
  worn item (see [Items saving against acid](FEATURES.md#items-saving-against-acid)).
- Undead (race 9 on the character sheet) take nothing from poison and
  draining, and mind-affecting spells, charms and holds don't work on them.

The dice log notes a weapon hit that takes less than its roll, or nothing at
all, with what the monster's defences say about it
(`Mastyrial takes none of the 6 damage: crushing weapons can't hurt it`: the
game's mastyrials take nothing from clubs and maces, only from edged and
pointed weapons).

## Searching junk, hay and wardrobes

Junk piles, haystacks and wardrobes are searched by one of the game's scripts,
each with a roll of its own: 0 to N, each number as likely. A low roll finds
nothing, and junk and hay stop giving anything once the party has found 6
things in them (each kind counts its own finds); wardrobes count every search,
and after 6 every wardrobe is empty.

| Search | Roll | Finds nothing on | What the rolls find |
|---|---|---|---|
| Junk pile | 0-14 | 0-1, or after 6 finds in junk | 2 a scorpion bite, dodged; 3 a scrap of paper ("Watch out for the..."); 4 a dead rat; 5 stale bread; 6 a piece of a grainpot; 7 a rat's bite (0-4 damage); 8 magic fruit; 9 wood for a club; 10 a drawing of a four-armed statue; 11 trinkets with a gem; 12 dung; 13 arrows; 14 magic fruit |
| Haystack | 0-10 | 0-2, or after 6 finds in hay | 3 a bone needle; 4 a piece of a pot; 5 a rat's bite (0-4 damage); 6 a table leg for a club; 7 a soiled loincloth; 8 15 ceramic coins; 9 a bug; 10 a small gem |
| Wardrobe | 0-10 | 0-2 (after 6 searches, empty) | 3 a rat's bite (0-4 damage); 4 a piece of a pot; 5 "Gareth the scribe was here."; 6 magic fruit; 7 a falling pot (0-5 damage); 8 a small gem; 9 a falling pot that misses; 10 "Don't trust Pehtucl." |

The script also has outcomes for the rolls that find nothing (a scorpion's bite
in junk, a skull in hay, coins in a wardrobe...), but its "nothing" check comes
first, so they never happen.

How it works: [DEVELOPMENT.md](DEVELOPMENT.md#searching-junk-hay-and-wardrobes).

## No critical hits

A natural 20 on an attack always hits, and a natural 1 always misses, but
that is all the d20 does: the game has no critical hits or fumbles. Its attack
routine uses the d20 only for those two checks and the comparison with THAC0,
and never passes it to the damage routine, so a hit on a 20 rolls the same
damage as any other. A backstab is the only thing that multiplies damage.

## The game's two weapons

The manual says a character with two weapons ready uses the second "at a
disadvantage", unless a ranger or dextrous. The game's code does something
else: with two weapons ready (in melee), every attack, first hand and second
alike, is adjusted by the DEX table used for initiative with its sign flipped
and never below 0, and rangers are left out. That comes to a **bonus** of +6 at
DEX 1, +4 at 2, +3 at 3, +2 at 4 and +1 at 5, and nothing at DEX 6 and up, so
in practice there is no off-hand penalty at all: both weapons hit as well as a
single one would. The log names it, e.g. `+2 two weapons at DEX 4`. It looks
like a sign slip: AD&D uses the same DEX adjustment to make two-weapon
fighting *harder* at low DEX.

## How the game works out thief skills

The game never shows thief skills, but it rolls them: for traps, and for the
locks, walls and so on its scripts ask for (see
[Where the game rolls thief skills](#where-the-game-rolls-thief-skills)). The
game gives the skills no names; its eight are AD&D's in AD&D's order (pick
pockets, open locks, find/remove traps, move silently, hide in shadows, hear
noise, climb walls, read languages), which the checks below fit. The roll is a
d100 that must come in under the skill's chance. The game's code works the
chance out as:
- a base for each skill, in that order (28, 18, 13, 28, 18, 23, 78, −4),
- plus 4 for each thief level,
- plus a racial adjustment. These are AD&D's, for example a dwarf gets +10 to
  open locks, +15 to find traps, −10 to climb walls and −5 to read languages.
- plus DEX: −5 for each point below 12, 11, 12, 13 or 11 (the first five skills);
  +5 for each point above 16, 15, 17, 16 or 16; and −3 for each point above
  21, 20, 21, 19 or 19, so very high DEX gains less,
- minus an equipment penalty (5, 0, 0, 10, 5, 0, 10, 0) when the thief has
  anything at all in the leg armour slot, the quiver or either hand. That is
  the game's own check: it doesn't look at what the item is (leather or metal)
  and ignores chest and arm armour and helmets, so a thief holding any weapon
  pays it. (The manual's "anything other than leather-type armor" is AD&D's
  rule, not what the code does.) In games started with the dice log there is
  no equipment penalty at all: the slots are a list in the game's data (legs,
  quiver, left hand, right hand), and the dice log's copy of the game empties
  it. The Loader reads the list from the running game, so its numbers match
  whichever game it is.
- plus the situation's bonus or penalty (a hard lock, say).

With **Thief skills from AD&D's table** ticked (see
[Thief skills from AD&D's table](FEATURES.md#thief-skills-from-adds-table)), the first
two and the DEX part are AD&D's instead.

Only characters with thief levels have the skills; everyone else's chance is
0. The character's condition must be Okay (the status the character screen
shows under HP): a thief who is Stunned, Out Cold, Dying and so on can't use
the skills. A character not yet played (New, before the game starts) counts as
Okay with the mod, so a party's thief skills show while it is made (see
[More characters](FEATURES.md#more-characters)).

Some effects rule out a skill:
- Blind, Afraid, Confused, Berserk and Paralyzed stop them all, except that a
  blind thief can still hear noise.
- Slowed stops all but picking pockets.
- Fire Shield stops picking pockets and hiding; Mirror Image stops hiding.
- Graft Weapon stops picking pockets, opening locks and climbing.
- Feeblemind stops reading languages.
- Enlarge scales the situation's bonus or penalty, not the skill: for hiding it's
  divided by (100 + 10 × Enlarge's level)%, for climbing multiplied by it. With
  no bonus or penalty it changes nothing; with a penalty, climbing gets harder.

Two effects make a skill certain instead: Detect Traps (anyone, thief or not,
finds traps) and Invisible (hiding in shadows).

These effects work on the situation's bonus: ruling a skill out takes 1000 off
it, so the roll can't succeed, and making it certain adds 1000. (One more rule
in the code would make move silently certain, and hearing noise impossible, for
someone wearing one particular item on their legs, but the game passes that
check its two lists the wrong way round, so it never applies.)

## Where the game rolls thief skills

There is no hide or sneak command, and nothing in the game's code rolls a thief
skill on its own: every roll comes from the game's scripts (conversations,
doors, walls...), which ask in two ways. Every script in GPLDATA.GFF decodes
(see `dsloader/gpl.py`), so these are all of them:
- **13 skill checks**: find/remove traps 4 times (a hidden passage, a secret
  door, a loose rug, a cord on a lava-dome egg; bonuses −10 to +3), open locks
  4 times (a safe, a grate and cell doors; −4 to +8), climb walls 3 times, and
  pick pockets and hear noise once each (a key in a trustee's pocket; two men
  arguing by a wagon, a check for the whole party). Most are made by the
  character who acted.
- **50 trap triggers, in 16 scripts.** A script sets off an object at a spot on
  the map (a trap, or a blast: the bound prisoners in the arena, a Drajian
  messenger's thrown sphere, a summoning circle, a breaking mirror...). First
  the party's best at find/remove traps rolls, with no bonus; success, or
  Detect Traps on the character who set it off, avoids it. This is the roll the
  arena prisoner makes.

A party check goes to the member with the best chance. *Without the mod* it
always went to the first party member: the game's pick meant to find the best
but compared the wrong way round. (The game also has a script command that lets
each member try in turn, but no script uses it.)

**The game never rolls move silently, hide in shadows or read languages**, so
on their own they make no difference, nor does the equipment penalty on them.
The Loader rolls them: move silently when a pocket isn't picked
([Picking pockets](FEATURES.md#picking-pockets)), hide in shadows and move silently in
fights ([backstabs](FEATURES.md#hiding-in-shadows-to-backstab)), and read languages when
a [Shinobi](KITS.md#thief-kits) reads a scroll. The scripts also make
3 ability checks (a d20 under the ability): CHA twice and STR once.

`python -m dsloader checks` lists them all with the script's text around
each (spoilers).

The **Characters** tab shows each thief's chances as they stand, with the
equipment penalty (none in games started with the dice log) and effects (but
not the situation's bonus or penalty), for the five skills the game rolls
(pick pockets, open locks, find/remove traps, hear noise, climb walls) and
the two the Loader rolls: move silently (when a pocket isn't picked, see
[Picking pockets](FEATURES.md#picking-pockets)) and hide in shadows (to
[backstab](FEATURES.md#hiding-in-shadows-to-backstab)).
**All fields** has them in a row (`PP/OL/FT/MS/HS/HN/CW`).

## Attacks from behind and backstabs

From the game's code:

- An attack is **from behind** when the attacker stands in the square directly
  behind the way the target is facing. A creature faces nowhere in particular
  at the start of each round; the first attack on it in the round turns it
  to face that attacker (one of eight directions), and it keeps facing that
  way for the rest of the round. So a second attacker on the far side, later
  in the same round, attacks from behind. (Its own attacks don't turn it.)
  It gets +2 to hit, and the target loses its DEX bonus and its shield.
- A **backstab** is an attack from behind by a thief, in melee, with a weapon
  that isn't too heavy (the game's weight value at most 40, a metal long
  sword's). It gets another +2 to hit (+4 in all), and on the thief's first
  attack of the round the damage, STR bonus included, is multiplied: x2 at
  thief levels 1-4, x3 at 5-8 and x4 at 9 and 10.

Which weapons can backstab, the game's and the [Loader's](FEATURES.md#new-items) (magic
ones included). Weight belongs to the weapon's type and material, in the
game's units, which look like tenths of a pound (a dagger is 10, a club 30, a
mace 100, as AD&D's 1, 3 and 10 lb), so the limit is 4 lb. Missile weapons
(slings, bows, a thrown chatkcha) never backstab: it has to be melee.

| Weapon | Material (weight) | Damage | Backstab |
|---|---|---|---|
| Dagger | bone, stone, obsidian, metal (10) | 1d4 | yes |
| Short sword | bone (15); obsidian, metal (30) | 1d6 | yes |
| Long sword | bone, obsidian, metal (10 to 40, metal at the limit) | 1d8 | yes |
| Club | wood (30) | 1d6 | yes |
| Quarterstaff | wood (40) | 1d6 | yes |
| Axe | bone, obsidian (30) | 1d8 | yes |
| Pick | stone, metal (40) | 1d4+1 | yes |
| Shillelagh, Flame Blade, Spiritual Hammer (spells) | (10, 40, 40) | 2d4, 1d4+4, 1d4+1 | yes |
| Axe | metal (70) | 1d8 | no |
| Great axe | bone (50); obsidian, metal (70) | 1d10 | no |
| Mace | bone, obsidian, metal (100) | 1d6+1 | no |
| Cahulaks, gythka | bone (120) | 1d6, 2d4 | no |
| Polearm | bone, metal (150) | 1d10 | no |

About a dozen more weapon types are in the game's tables with no item of
theirs in its data (monsters' own, made by scripts, or unused).

## The game's saving throws

From the game's saving throw routine. The spell names which of the character
sheet's five saves to use; a natural 1 always fails and a natural 20 always
saves; otherwise the d20 and the modifiers below must reach the save's number.

**Petrification/polymorph for almost every spell.** The game's code maps the
spell's save kind 5 to the sheet's third save; kind 1 is
paralysis/poison/death, used by the clouds, Poison, Slay Living and the
psionic attacks. The spell save, the one AD&D uses for spells, is never used:
a 3rd-level warrior needs 13 against Psychic Crush (paralysis) and 14 against
Fireball (petrification), where the spell save would be 16.

**Fire, cold and electricity: the d20 counts double.** Each spell's record has
a word of flags saying what kind of damage it does, and the saving throw code
doubles the d20 whenever the kind is fire, cold or electricity. Nothing else
is doubled: not acid (Acid Arrow), crushing (Ice Storm, Magical Stone), poison
(Cloudkill), draining (Vampiric Touch, the Cause Wounds spells) or the psionic
attacks. The doubled spells are:
- fire: Burning Hands, Flaming Sphere, Fireball, Flame Arrow, Minute Meteors,
  Fire Shield, Wall of Fire (both), Focus Heat, Produce Fire, Flame Strike;
- cold: Chill Touch, Cone of Cold;
- electricity: Shocking Grasp, Lightning Bolt.

In between a 1 and a 20 the doubled roll makes saving far easier: needing 14,
a normal d20 saves 35% of the time and a doubled one 70%, which is why
Fireball's victims usually get away with half damage. It isn't AD&D, and the
game never explains it; it may have been meant as a dodge. The log says it on
each save: `d20 = 7, doubled against fire = 14`. Two of the
mod's [rule changes](FEATURES.md#spells-saved-against-with-the-spell-save) put the
spell save back and take the doubled d20 away.

The target's spells and effects:
- Blessed +1, Barkskin +1, Spirit Armor +3 (but not on
  paralysis/poison/death saves), and the Save penalty effect −1.
- Prayer: +1 if its caster is on your side, −1 if not.
- Protection from Evil +2 against an evil caster (lawful, neutral or chaotic
  evil); Protection from Fire and from Cold +3 against fire and cold spells;
  Protection from Lightning +4 against electricity.
- +4 against a spell aimed at one target (not an area) when the caster can't
  see you: the caster is Blind, or you're Invisible (or Invisible to Undead,
  against an undead caster) and the caster can't detect invisibility.

Class, race and abilities:
- WIS, against mind-affecting spells, charms and holds, fear and illusions: −6
  at WIS 1, −4 at 2, −3 at 3, −2 at 4, −1 at 5-7, +1 at 15, +2 at 16, +3 at 17
  and +4 at 18 and up.
- CON, on paralysis/poison/death saves: −2 at CON 1, −1 at 2, +1 at 19-20, +2
  at 21-22, +3 at 23-24 and +4 at 25. Dwarves and halflings also add CON x 2 /
  7 (+1 for every 3.5 points).
- Druids +2 against fire and electricity; psionicists +2 against
  mind-affecting spells and charms.
- Some spells carry a modifier of their own (a monster's poison at −4).

Spells with rules of their own: creatures of 6th level or lower can't save
against Cloudkill; against Chaos only warriors (fighters, gladiators and
rangers) can; against Dismissal the target adds its level and takes away the
caster's; and against Scare, 6th level and up always save and everyone below
can't. The Scare code looks meant to let some elf or half-elf priests save
(AD&D gives elves, half-elves and priests a bonus), but it asks for a
creature that is both an elf and a half-elf, so no one qualifies.

Rules in the code that never come into play: Cloak of Bravery's +4 against
fear applies only to a kind of spell that no spell in the game is marked as
(the patched game marks the fear spells: see
[The game's bugs, fixed](FEATURES.md#the-games-bugs-fixed)), and so does AD&D's DEX defensive adjustment for attacks that can be dodged (+5
at DEX 1 to −6 at DEX 25 on AC, so −5 to +6 on the save), unless the
[rule change](FEATURES.md#rule-changes) puts it on the fire, cold and electricity spells.
And nothing in the game gives saves from items: there are no rings or cloaks
of protection, which is why the mod adds [two rings and a cloak](FEATURES.md#new-items). Their +1 is in the log's saving throws as
`+1 Ring of Protection` and `+1 Cloak of Protection` (with
[AD&D's rules for them](FEATURES.md#rings-and-cloaks-of-protection) off, all of it as
`Ring of Protection`).

## The arena's count of fights

The game counts the party's trips into Draj's arena (its global number 12; the
combat log panel's top line shows it between fights in the slave pens and the
arena). It goes up by one each time the
party walks out of the arena's gate after being called, however many waves
came that day; extra waves don't count. Being called needs the game's clock to
run: Kurzak's call comes once a little over 8 hours of game time (8 h 05 min)
have passed since the last trip, and the clock stands still while the Look
pointer is chosen, so a party resting by the fire with it chosen is never
called.

The announcer greets each trip by the count:

| Count | What happens |
|---|---|
| 0-3 | A speech of its own for each of the first four trips ("Before you is a handful of gladiators...", "Behold these gladiators as they fight in melee...", "These slaves have proven their worth...", "...Let the games begin!"), then the fight. |
| 4 | Scar's challenge: "The 'King of the Pens', Scar, has become so disgusted with the survival of these scum that he has offered to kill them himself", when a check the script makes on Scar passes; otherwise the everyday speech. |
| 1000 | "This day is very special. Let's have a round of applause for the one thousandth fight of our gladiators. King Tectuktitlay himself has sent gifts for these brave souls." Two weapons appear at the party's feet, with a sound: **El's Drinker +2** (a metal sword that carries a spell) and a **Bone Gythka +3**, each worth 65,000. The script then goes on as on any other day. |
| 5000 | "You win! Through fighting in the arena, you have completely depopulated Athas of all monsters." No monsters come: the announcer sends the party back to the pens to heal, the crowd throws money, and the script marks the war against Draj won (flag 10, and the final battle's state, global number 49, set to 3). Reaching the final battlefield afterwards plays the game's victory: 20,000 XP, the allies' farewells, Dragonsbane, the genie's prophecy, and "Congratulations! You have defeated the Drajian army and completed Shattered Lands. Feel free to continue playing the game." |
| Any other | "Once again, expectant spectators, you see trained warriors pitted against the hordes of creatures which dwell beyond our walls." |

Checked in play: the count going up once a trip, Scar's challenge on the fifth,
and, with the count set to 5000, the 5000th trip's speech, the party sent back
with no fight, and the final battle marked won. The 1000th trip is as its
script reads; it wasn't played.
