# Obsidian Edition: the player's guide

How **Dark Sun: Shattered Lands** plays with the Obsidian Edition mod: making
a party, the classes and kits, fighting, magic, psionics, equipment and
levels, with the tables you need.

It is **spoiler-free**: no places, people or quests past the opening arena but
those the Loader's Options tab names (the slave pens, Kalzith, Semyon, Dinos's
cooked vulture, Scar and the champions' bout, in the labels [at the end](#the-options-tab-at-a-glance)),
and no word of where any item is found (the mod's new items are listed by what
they are).

Everything here is the mod with its **default options**, which is how the
Loader starts. Most of the rule changes are always on; a few, and the new content, have a switch on
the Loader's **Options** tab: [the Options tab at a glance](#the-options-tab-at-a-glance), at the
end, gives each switch's default and when it takes effect, and lists the changes that are always on.
Where it helps to know what the mod changes, a **Without the mod** note says what the game does
without it.
The [features page](FEATURES.md) has every rule in full detail, and the
[Kits](KITS.md) page each kit's numbers, and the [Weapon specs](WEAPON-SPECS.md) page
weapon specialization's: the guide links to their tables.

## Contents

- [Getting started](#getting-started)
- [Playing](#playing)
- [Making a party](#making-a-party)
  - [Ability scores](#ability-scores)
  - [Races](#races)
  - [Ages](#ages)
  - [More than one class](#more-than-one-class)
- [The classes](#the-classes)
  - [What each class may use](#what-each-class-may-use)
  - [Fighter](#fighter), [Gladiator](#gladiator), [Ranger](#ranger),
    [Thief](#thief), [Preserver](#preserver), [Cleric](#cleric),
    [Druid](#druid), [Psionicist](#psionicist)
- [Kits](#kits)
  - [Multiclass kits](#multiclass-kits)
- [Weapon specialization and attacks](#weapon-specialization-and-attacks)
- [Experience and levels](#experience-and-levels)
  - [Hit points](#hit-points)
  - [THAC0 by level](#thac0-by-level)
- [Fighting](#fighting)
  - [Initiative](#initiative)
  - [Moving in a fight](#moving-in-a-fight)
  - [Hitting](#hitting)
  - [Two weapons](#two-weapons)
  - [From behind, and backstabs](#from-behind-and-backstabs)
  - [The chance shown before the swing](#the-chance-shown-before-the-swing)
  - [Hiding in shadows](#hiding-in-shadows)
  - [Saving throws](#saving-throws)
  - [Monsters](#monsters)
- [Thieves' skills and picking pockets](#thieves-skills-and-picking-pockets)
- [Magic](#magic)
  - [Spell slots](#spell-slots)
  - [Learning preserver spells](#learning-preserver-spells)
  - [How spells work](#how-spells-work)
  - [Spell lists](#spell-lists)
  - [Status effects](#status-effects)
  - [Resting](#resting)
- [Psionics](#psionics)
- [Equipment](#equipment)
  - [Size](#size), [Cahulaks](#cahulaks), [Stinkpots](#stinkpots), [Polearm reach](#polearm-reach)
  - [Magic weapons by class](#magic-weapons-by-class)
  - [Armour](#armour), [Protection](#protection), [Acid](#acid)
  - [New items](#new-items)
- [Quality of life](#quality-of-life)
- [Worth knowing](#worth-knowing)
- [Glossary](#glossary)
- [The Options tab at a glance](#the-options-tab-at-a-glance)
  - [Elsewhere in the Loader](#elsewhere-in-the-loader)

## Getting started

Installing and starting the game, and carrying on a saved game, are in the
[README](README.md#running-it-windows); before the first fight, skim [Worth knowing](#worth-knowing).

## Playing

The pointer has three modes, changed with a right-click: **Walk**, **Attack**
and **Look**; a left-click acts. Look at someone to **Talk**, at a thing to
**Use** or **Pick Up** it, and at a monster in a fight to see its hit points,
AC and defences. Resting at a fire ring fills PSP and spell slots; with the
mod's [Resting as in AD&D](#resting) the party's priests and psionicists first cure the party with the
spells and powers they have left, and each member heals 3 hit points plus CON's bonus a
night, not all of them.
What the mod adds to the game's screens and controls is under [Quality of
life](#quality-of-life).

## Making a party

On the main menu choose **CREATE CHARACTERS**, right-click an empty slot and
choose **NEW**, then set race, classes, sphere and alignment, roll, and press
**DONE**. [Choosing a kit](KITS.md#choosing-a-kit) walks through the panel,
the mod's **KIT** page among it (the **KITS** button). After DONE a warrior (and a Swashbuckler, Battle Mage, Crusader or Mind Warrior) picks its weapon specs
([weapon specialization](#weapon-specialization-and-attacks)), as a preserver
picks its spells, and every character then picks its psionic powers
([features](FEATURES.md#psionic-powers-at-creation)). A party has one to four characters, all good or neutral.

### Ability scores

Each click of the die rolls a whole character:

- Each score is rolled **four times as 4d4 + 4** and the best kept (8 to 20),
  then the race's adjustment is added.
- A score below what the classes need is raised to it: each class's least is
  the manual's (the table below), and a character of several classes takes
  the highest of each score.
- **What the die gives is what you get.** A score can be lowered with a right
  click, and the points freed raise others with a left click, but the six
  never add up to more than the die gave. Under CHR, `SUM:99/101` is what
  they add up to now and the most they may: 2 points to spare. A new class
  that raises a score to its minimum raises the most with it. *Without the
  mod:* a click raises any score to its most.
- **STORE and RECALL**, under the hit points, keep a roll and bring it back
  (scores, hit points and PSP), as in Baldur's Gate: store a good roll, try
  the die again, and recall it if nothing better comes. Changing the race,
  sex, classes or kit forgets the stored roll.

| Class | Prime requisites | Least at creation |
|---|---|---|
| Fighter | STR | STR 9 |
| Gladiator | STR | STR 13, DEX 12, CON 15 |
| Ranger | STR, DEX, WIS | STR 13, DEX 13, CON 14, WIS 14 |
| Thief | DEX | DEX 9 |
| Preserver | INT | INT 9 |
| Cleric | WIS | WIS 9 |
| Druid | WIS, CHA | WIS 12, CHA 15 |
| Psionicist | CON, WIS | CON 11, INT 12, WIS 15 |

*Without the mod:* the die raised the prime requisite to 17, and every other
score to 9 to 14.

What the scores do:

- **STR:** to-hit and damage in melee, and how much is carried.
- **DEX:** AC (−1 at 15, down to −6 at 24), to-hit with missiles,
  [initiative](#initiative), thief skills, the
  [two-weapon penalty](#two-weapons), and dodging fire, cold and electricity
  ([saving throws](#saving-throws)).
- **CON:** hit points, saves against paralysis, poison and death; at 20 or
  more, a hit point comes back now and then.
- **INT:** for preservers, the chance to learn a spell from a scroll and how
  many spells of each level they can know
  ([learning spells](#learning-preserver-spells)).
- **WIS:** priests' bonus spell slots, and saves against mind-affecting magic.
- **CHA:** how some people take to the party, and the **party leader's** CHA
  lowers what shops ask:

  | Leader's CHA | 17 or less | 18 | 19 | 20 | 21 | 22 | 23 | 24 | 25 |
  |---|---|---|---|---|---|---|---|---|---|
  | Shops ask | full price | 5% less | 10% less | 15% less | 20% less | 25% less | 30% less | 35% less | 40% less |

  Shops pay 60% of an item's price when you sell. A magical item you sell stays
  in the merchant's stock, to buy back; anything else sold is gone. *Without
  the mod:* CHA makes no difference to prices, shops pay the full price, and
  everything sold is gone.

### Races

| Race | STR | DEX | CON | INT | WIS | CHA | Notes |
|---|---|---|---|---|---|---|---|
| Human | | | | | | | one class at a time, but can change class |
| Dwarf | +1 | −1 | +2 | | | −2 | better CON saves |
| Elf | | +2 | −2 | +1 | −1 | | |
| Half-elf | | +1 | −1 | | | | |
| Half-giant | +4 | −5 | +2 | −5 | −3 | −3 | double hit dice; holds a two-handed weapon in one hand; large: weapons roll their larger dice against it, Hold and Charm Person fail on it, cahulaks can't tangle it ([size](#size)) |
| Halfling | −2 | +2 | −1 | | +2 | −1 | better CON saves |
| Mul | +2 | | +1 | −1 | | −2 | |
| Thri-kreen | | +2 | | −1 | +1 | −2 | base AC 5, moves 15 (others 12); four claws (1d4) and a bite (1d4+1) a round, that cut (edged, not crushing); with weapons in hand, the weapons in the claws' place, and the bite still; throws a chatkcha once more a round; no armour, cloaks, belts, boots or rings |

With each score rolled 8 to 20 before the adjustment, a race's scores run from
8 to 20 plus its adjustment: a half-giant's STR 12 to 24, its DEX and INT 3 to
15, its WIS and CHA 5 to 17. (The Dark Sun book caps a half-giant's DEX and
INT at 15 and its WIS and CHA at 17, with smaller adjustments; the game gets
the same caps from these larger ones.)

**Classes by race** (the creation screen greys the rest):

| Race | Cleric | Druid | Fighter | Gladiator | Preserver | Psionicist | Ranger | Thief |
|---|---|---|---|---|---|---|---|---|
| Human | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Dwarf | ✓ | | ✓ | ✓ | | ✓ | | ✓ |
| Elf | ✓ | | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Half-elf | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Half-giant | ✓ | | ✓ | ✓ | | ✓ | ✓ | |
| Halfling | ✓ | ✓ | ✓ | ✓ | | ✓ | ✓ | ✓ |
| Mul | ✓ | ✓ | ✓ | ✓ | | ✓ | | ✓ |
| Thri-kreen | ✓ | ✓ | ✓ | ✓ | | ✓ | ✓ | |

**Alignment:** a druid must be true neutral, a ranger good (lawful, neutral
or chaotic good). The others may be any good or neutral alignment.

### Ages

With [Ages and magical aging](FEATURES.md#ages-and-magical-aging)
on, each character has an age from the Dark Sun rules (on the inventory
panel, under the saves). Middle, old and venerable age change the scores, and
a character dies at the most its race lives. Each 365 days of game time adds
a year, and their hair greys on the map as they age (with what the party wears
on); the creation screen shows the age a new character starts at. Magic ages
them faster: **Haste**
costs a year, after a system shock roll by CON that a character can fail and
die (85% to survive at CON 13, 99% from 18); **Restore Youth** gives magical
years back. *Without the mod:* no ages, and Haste costs nothing.

| Race | Starting age | Middle age | Old age | Venerable | Most it lives |
|---|---|---|---|---|---|
| Human | 15 + 1d8 | 40 | 53 | 80 | 80 + 2d20 |
| Dwarf | 25 + 4d6 | 100 | 133 | 200 | 200 + 3d20 |
| Elf | 15 + 3d4 | 50 | 67 | 100 | 100 + 2d20 |
| Half-elf | 15 + 2d4 | 45 | 60 | 90 | 90 + 2d20 |
| Half-giant | 20 + 5d4 | 60 | 80 | 120 | 120 + 1d100 |
| Halfling | 25 + 3d6 | 45 | 60 | 90 | 90 + 4d12 |
| Mul | 15 + 1d6 | 40 | 53 | 80 | 80 + 1d10 |
| Thri-kreen | 6 | – | – | 25 | 25 + 1d10 |

- **The scores change** on reaching each age, once and for good, adding up:
  middle age −1 STR and CON, +1 INT and WIS; old age −2 STR and DEX, −1 CON,
  +1 WIS; venerable −1 STR, DEX and CON, +1 INT and WIS. A thri-kreen has only
  a venerable age, and loses 1 STR and 1 DEX there. At the most its race lives
  (its own roll, kept secret) a character dies of old age.
- **The starting age** is rolled on the creation screen with each roll of the
  die and each choice of race, sex or class, and kept at DONE; the game's own
  party, or a character made before ages, gets its roll the first time the
  Loader sees it (the dice log says so: `Cermak is 22 (a human: 15 + 1d8 = [7]);
  middle-aged at 40.`).
- **A year passes each 365 days** of the game's own clock, from the start of
  the game (`A year has passed: Cermak is 23.`): a party that rests 5000 times
  is only 5 to 9 years older. The years counted are kept in the save, so a
  loaded game shows the ages as they were, and none is counted twice or missed
  (one that passes in the arena counts as the party leaves it).
- **Haste** makes each creature it hastes roll **system shock** (85% at CON 13,
  88% at 14, 90% at 15, 95% at 16, 97% at 17, 99% at 18 to 24, 100% at 25) or
  die; a party member who survives is a year older. Monsters have no ages: for
  them it is the roll alone. A thri-kreen, venerable at 25, feels it most.
- **Grey hair:** iron grey streaks when middle-aged, grey when old, white when
  venerable, on the map with what the party wears on (a helm or cloak over the
  hair is left as it is; dwarves, muls and thri-kreen have no hair to grey).
- The age shows on the creation screen, the inventory panel (`AGE: 23`) and
  the Loader's Characters tab, with the category and the next age to come
  (`Age: 45, middle-aged; old at 53`).

### More than one class

**Multiclass (any race but human).** A character takes two or three classes at
once. Experience is split evenly between them, so each rises more slowly; hit
points are shared out ([hit points](#hit-points)); and the strictest class
decides what may be worn and wielded
([what each class may use](#what-each-class-may-use)). **Gladiators never
multiclass.** The combinations, by race:

| Race | Two classes | Three classes |
|---|---|---|
| Dwarf | cleric/fighter, cleric/psionicist, fighter/psionicist, fighter/thief, psionicist/thief | cleric/fighter/psionicist, fighter/psionicist/thief |
| Elf | any two of cleric, fighter, preserver, psionicist, ranger and thief but fighter/ranger | any three of them without both fighter and ranger |
| Half-elf | as the elf, and a druid with fighter, preserver, psionicist or thief | as the elf, and a druid with any two of fighter, preserver, psionicist and thief |
| Half-giant | cleric/fighter, cleric/psionicist, cleric/ranger, fighter/psionicist, psionicist/ranger | none |
| Halfling | cleric or druid with fighter, psionicist or thief (and cleric/ranger); fighter/psionicist, fighter/thief, psionicist/ranger, psionicist/thief, ranger/thief | fighter/psionicist/thief, psionicist/ranger/thief |
| Mul | cleric or druid with fighter, psionicist or thief; fighter/psionicist, fighter/thief, psionicist/thief | cleric/fighter/thief, druid/fighter/thief, fighter/psionicist/thief |
| Thri-kreen | cleric or druid with fighter or psionicist; cleric/ranger, fighter/psionicist, psionicist/ranger | cleric/fighter/psionicist, cleric/psionicist/ranger, druid/fighter/psionicist |

No character is both cleric and druid, druid and ranger (a druid is true
neutral, a ranger good), or fighter and ranger.

**Dual class (humans only).** A human has one class, and can change to another
with **DUAL** on a portrait's right-click menu when:

- it is **3rd level or more** (as the manual says; 2nd with the rule change
  [dual-classing as the manual has it](FEATURES.md#dual-classing-as-the-manual-has-it) off) and has
  changed class at most once before;
- **every prime requisite of its current class is 15 or more**, and **every
  one of the new class's 17 or more** (the table below: a ranger's STR, DEX
  and WIS, a druid's WIS and CHA, a psionicist's CON and WIS); with the rule
  off, the game's one score a class (STR for fighters and gladiators, WIS for
  clerics, druids, psionicists and rangers, INT for preservers, DEX for
  thieves);
- the new class is of **another group** than every class it has had: priests
  (cleric, druid), warriors (fighter, gladiator, ranger), preserver,
  psionicist, thief;
- its alignment suits the new class (a druid true neutral, a ranger good).

The new class starts at 1st level. The old class stops rising, and what it
gives (its hit points, THAC0, saves, weapon specs and kit) **sleeps until the
new class's level passes the old one's**; then both count. A human keeps its kit and takes no
other; one with none may take one for the new class, and some kits rule out
classes ([kits](#kits)).

The change starts the new class at 0 XP, and any XP past the old level's need
is lost: change as soon as the level you want comes. How far the new class can
then rise: [XP left over at the top](#xp-left-over-at-the-top).

## The classes

| Class | Hit die | Prime requisites | Races | Armour | Weapons | Kits |
|---|---|---|---|---|---|---|
| [Fighter](#fighter) | d10 | STR | all | any | any | Myrmidon, Sentinel, Ravager |
| [Gladiator](#gladiator) | d10 | STR | all | any | any | Arena Champion, Twin-blade, Brute |
| [Ranger](#ranger) | d10 | STR, DEX, WIS | not dwarf, mul | any (two weapons without penalty in light only) | any | Stalker, Justifier, Seeker |
| [Thief](#thief) | d6 | DEX | not half-giant, thri-kreen | light (with another class: heavier, without thief skills) | any | Swashbuckler, Assassin, Shinobi |
| [Preserver](#preserver) | d4 | INT | elf, half-elf, human | none | daggers, quarterstaffs, slings and staff slings | Scholar, Battle Mage, Arcanist |
| [Cleric](#cleric) | d8 | WIS | all | any | its sphere's | Elementalist, Healer, Crusader |
| [Druid](#druid) | d8 | WIS, CHA | half-elf, halfling, human, mul, thri-kreen | none | any but great axes | Grove Warden, Lifebinder, Wanderer |
| [Psionicist](#psionicist) | d6 | CON, WIS | all | light | small weapons | Mind Bender, Mind Warrior, Kineticist |

The [THAC0](#thac0-by-level) and [experience](#experience-and-levels) tables
cover every class; [new items](#new-items) lists what the mod adds to find, and
[magic weapons by class](#magic-weapons-by-class) which of them each class can wield.

**More than one class.** Each class's section gives its dual-class rule. The
multiclass combinations and their races are in [More than one
class](#more-than-one-class) (a gladiator never multiclasses), and some kits rule
out a change of class ([which](KITS.md#kits-that-rule-out-classes-and-each-other)).

**Starting gear.** Each class's section names what a new character starts
with. A character of several classes gets one class's gear (the first of
fighter or ranger, cleric, thief, psionicist, preserver and druid), less what
its classes can't use. The mod then adds plain gear, as each section says: a
weapon in hand it can use (a thief/psionicist, which can't use the long sword,
gets a bone short sword), a sling if it has no bow or sling, leather armour
where it may wear it, and a cloak for a Stalker, an Assassin or a Shinobi
(kits' own weapons: [Starting gear](KITS.md#starting-gear)). A thri-kreen gets
nothing more than the game's own starting gear: its claws serve it better than
another weapon, and it wears none of the rest; its weapon spec is the chatkcha
if none is picked. A multiclass preserver starts with no armour, so it can
cast. Nothing is given that the character can't use or already has. The
game's own party gets the same. *Without the mod:* the class's gear only,
armour it can't use in the backpack.

### What each class may use

The game's own lists still need only one of a character's classes; on top of
them, the mod's limits below apply to every class, the strictest winning:

| Class | Armour and helms | Shields | Weapons |
|---|---|---|---|
| Psionicist, whatever its other classes | light only (leather, hide, silk) | none alone; leather with a fighter, gladiator, ranger or cleric class | daggers, bone and obsidian short swords, clubs, chatkchas, bows; with another class, also the maces, metal short sword and slings its lists allow |
| Thief | light only; with a warrior or cleric class, as that class allows, but no thief skills in heavier armour | leather ones only; with another class, only if that class is fighter, gladiator, ranger or cleric | as its classes allow |
| Preserver, one class | none | none | as the game's lists allow: a preserver's |
| Druid | none | none | as the game's lists allow: any but great axes |
| Cleric | any | any | air: missile and thrown weapons, daggers, cahulaks; earth: stone, obsidian, metal, wood; fire: obsidian; water: bone, wood |

- A preserver with another class may wear what that class allows, but casts
  no spells while wearing armour (a helm counts, a shield doesn't). Bracers
  of defense aren't armour.
- A thief with another class (a fighter/thief, a cleric/thief) may wear what
  that class allows, but in armour heavier than leather, hide or silk it has
  no thief skills (all 0) and no backstab.
- A human who was a fighter, gladiator or ranger and is now a thief or a
  preserver (or the other way round) is treated the same way: it may wear the
  warrior's armour, losing its thief skills, or its spells, while it does. So
  is a human cleric who became a thief: the cleric's armour, without thief
  skills.
- A ranger may always use a bow (a Seeker only where its sphere allows one).
- A human who changed class is held by its new class (but for the warrior's
  or cleric's armour above), and may use the weapon specs it specialized in
  once its old class wakes.
- A thief of any kind holds only leather shields, with the rule or without:
  the game's own lists leave thieves out of the wooden shield, and the mod's
  metal one.
- A new character starts without the weapons, armour and shields its classes
  can't use: the Loader leaves them behind and says so in the dice log
  (`Yilballa's Chest Armor is left behind: their classes can't use it`), and
  one left without a weapon gets one with fuller starting gear.

*Without the mod:* an item was allowed if **any** of the character's classes
allowed it, and a preserver with another class cast in armour.

Which magic weapons that leaves each class: [magic weapons by class](#magic-weapons-by-class).

**Weaker materials.** Athas is short of metal, and the game makes a plain
weapon of anything else worse: wood −3 to hit and −2 damage, bone −1 and −1,
stone and obsidian −2 and −1. A weapon with a plus has no penalty, nor do clubs
and staves, which are meant to be wooden. The inventory, View Character and the
dice log all count it, and the weapon's item box (right-click it) shows the
to-hit under its damage: "Hit -1" for bone, the damage line already less the
material's.

### Fighter

*d10 · STR · any race · XP for 2nd level 2,000, for 10th 500,000*

**How it plays.** The steadiest front-liner: any armour, any shield, any
weapon, the best THAC0, and it masters one weapon spec. Choose it with care:
it is the fighter's weapon for the whole game.

**What the mod changes.**

- [Weapon specialization](#weapon-specialization-and-attacks): one weapon
  type, +1 to hit and +2 damage with 3/2 attacks a round; **mastery** at 5th
  level (+3 and +3), **grand mastery** at 9th (the damage die the next size
  up, against large targets too: a long sword 1d10, 1d20 against a large one;
  and one more attack). Other weapons attack once a round until 7th level.
  *Without the mod:* 3/2 attacks with any weapon, no other bonus.
- Hit dice rolled twice; levels up to the [XP cap](#experience-and-levels).
- [Two weapons](#two-weapons) cost to-hit, and the off hand attacks once a
  round.

**Weapons and armour.** Everything. A fighter with other classes is held to
theirs ([what each class may use](#what-each-class-may-use)).

**Kits.**

*Myrmidon.* Drilled in a sorcerer-king's legions, where a soldier who falls out
of step is left for the kanks. They master the polearm of the battle line as well
as a weapon of their own choosing,
but years of obeying orders leave their minds open to anyone who barks them,
and they wait for the order to strike.

*Sentinel.* Caravan guards and city-gate wardens who live behind their shields
and are lost without one, last to give ground. They trust bone and
obsidian over sorcery, and spells bite them harder for it.

*Ravager.* Raiders of the wastes who fight half-naked under the crimson sun,
scarred hide hardening with every season. They charge in close and stay there:
bows, slings and shields are for those who mean to live long.

Each kit's gains, costs and starting gear:
[Fighter kits](KITS.md#fighter-kits) on the Kits page.

**Starting gear.** A plain weapon of its weapon spec (in a material its
classes allow), a shield, leather chest, arm and leg armour; with fuller
starting gear, also a sling.

**Dual class.** With STR 15, a human fighter can become a cleric, druid, preserver, psionicist or
thief, never a gladiator or ranger. Its weapon specs sleep with the class; once awake, its
specialized weapon specs stay usable whatever the new class allows.

### Gladiator

*d10 · STR · any race · XP for 2nd level 2,250, for 10th 600,000*

**How it plays.** The arena's finest: trained in many weapons rather than one,
better AC as it rises, and the most varied kits. A gladiator is **always a
single class** (a human may still change class).

**What the mod changes.**

- [Weapon specialization](#weapon-specialization-and-attacks) in **two** weapon
  types at 1st level, a third at 6th and a fourth at 9th: +1 to hit, +2 damage
  and 3/2 attacks with each. *Without the mod:* 3/2 attacks with any weapon.
- AC 2 better at 10th level, with the [XP cap](#experience-and-levels) letting it get there (the game's own AC 1 better from 5th), in armour only. *Without the mod:* with or without armour.
- AD&D's experience table. *Without the mod:* the fighter's.
- Hit dice rolled twice; levels up to the [XP cap](#experience-and-levels).

**Weapons and armour.** Everything.

**Kits.**

*Arena Champion.* Crowd favourites of the fighting pits, schooled to turn every
blow with a shield and answer it before the cheering dies. Without one they
feel naked on the sand, and fight like it.

*Twin-blade.* Showfighters who carry a weapon in each hand and make the crowd
count the blows. They have no use for a shield, nor for a weapon so heavy it
needs both hands.

*Brute.* Pit fighters bought for size and fed for strength, swinging great axes
and mauls that end a bout in one blow. Anything smaller looks like a toy in
their hands, and they treat it like one.

Each kit's gains, costs and starting gear:
[Gladiator kits](KITS.md#gladiator-kits) on the Kits page.

**Starting gear.** A plain weapon of its first weapon spec, a club in the off
hand, leather arm armour; with fuller starting gear, also leather chest and
leg armour and a sling.

**Dual class.** With STR 15, a human gladiator can become a cleric, druid, preserver, psionicist or
thief.

### Ranger

*d10 · STR, DEX, WIS · elf, half-elf, half-giant, halfling, human, thri-kreen · good
alignment · XP for 2nd level 2,250, for 10th 600,000*

**How it plays.** A warrior of the wastes: the bow and one more weapon spec,
two weapons at no penalty in light armour, hiding and moving silently under
the open sky to strike from behind, and a little priest magic late on.

**What the mod changes.**

- [Expertise](#weapon-specialization-and-attacks) with the bow and one more
  weapon spec: a specialist's attacks a round. *Without the mod:* 3/2 in melee
  with any weapon.
- [Hiding in shadows](#hiding-in-shadows) in a fight with a thief's numbers for
  its level, halved indoors; a successful hide and move silently makes its next
  attack from behind.
- Priest spells of its sphere from 8th level, cast as a priest of its level
  less 7 for damage and duration too (1 slot at 8th, 2 at 9th, 2 and 1 at
  10th). *Without the mod:* cast at its full level.
- AD&D's experience table (2,250 for 2nd level; *without the mod:* 2,200).
- Hit dice rolled twice; levels up to the [XP cap](#experience-and-levels).

**Weapons and armour.** Everything; any multiclass ranger keeps the bow
whatever its other classes allow (a Seeker: its sphere's weapons).

**Kits.**

*Stalker.* Hunters of the scrub and the city's shadowed alleys alike, moving
where no one is watching and striking before anyone knows they are there. Heavy
armour would only slow them down and give them away.

*Seeker.* Wanderers on a lifelong pilgrimage through the wastes, looking for
the spirit that still lives in Athas's broken land. As they come to understand
it, the elements begin to answer them, though only through the arms a priest
would carry.

*Justifier.* Hunters hired to deal with whatever is too dangerous for anyone
else: a tribe's chieftain, a defiler's lair, a beast that has emptied a
village. They train their weapons to a killer's edge and leave prayer to
others.

Each kit's gains, costs and starting gear:
[Ranger kits](KITS.md#ranger-kits) on the Kits page.

**Starting gear.** A plain weapon of its weapon spec, bow and arrows, leather
chest and arm armour; with fuller starting gear, also leather leg armour (a
Stalker a cloak too).

**Dual class.** With STR, DEX and WIS 15, a human ranger can become a cleric, preserver, psionicist
or thief (a druid must be neutral, a ranger good). A human of another class with STR, DEX and WIS 17
and a good alignment can become a ranger.

### Thief

*d6 · DEX · not half-giant or thri-kreen · XP for 2nd level 1,250, for 10th
160,000*

**How it plays.** Locks, traps and pockets out of a fight; in one, it waits
for a clear turn, slips into the shadows and backstabs. Light on hit points,
so keep it off the front line.

**What the mod changes.**

- [Thief skills](#thieves-skills-and-picking-pockets) from AD&D's table with
  Dark Sun's race and DEX adjustments, none above 95. *Without the mod:* the game's own,
  much higher, with penalties for what is held.
- [Hiding in shadows](#hiding-in-shadows) in a fight to backstab, halved in
  daylight. *Without the mod:* backstabs only when the target faces someone
  else. A backstab multiplies the weapon's dice more as the thief rises
  ([backstabs](#from-behind-and-backstabs)).
- **Picking pockets** with a thief's Pick Pockets button, from anyone in sight.
- A worn cloak, boots and belt help hiding, moving silently, picking pockets
  and opening locks.
- AD&D's experience table (1,250 for 2nd level; *without the mod:* 1,200).
- A d6 at 10th too; hit dice rolled twice; levels up to the
  [XP cap](#experience-and-levels).

**Weapons and armour.** Any weapon, but only one no heavier than a long sword
backstabs (see [Equipment](#equipment)); light armour only (leather, hide,
silk), and of shields only leather ones (the game's own rule), with another
class only if that class allows shields. A thief with a warrior or cleric
class, or a human once a warrior, may wear heavier armour that class allows,
but has no thief skills and no backstab while it does; an Assassin or Shinobi
may not while its kit is awake (the limit sleeps with the kit after a change of
class).

**Kits.**

*Assassin.* Knives for hire in the templars' cities, where a noble house pays
well to see a rival fall. They learn to vanish in the full glare of the sun,
strike from behind deadlier than any other thief, and leave locks and purses
to lesser thieves.

*Swashbuckler.* Swaggering rogues of the merchant houses and the elven markets,
as handy with a blade as any soldier. Their luck is another matter: a lock
that opens for them one day sticks the next, and every try at a thief's craft
may go a little or a lot worse (0 to 25 off, rolled each time).

*Shinobi.* Spies trained in secret by the Veiled Alliance, who carry a few
spells beside their knives. Their masters teach them only what they need, so
a scroll is theirs only if they can make out its script, and they travel light.
The Effects screen (Current Spell Effects) shows a Shinobi's chance to read a
scroll under its kit ([the Effects screen's kit line](KITS.md#the-kits-in-play)).

Each kit's gains, costs and starting gear: [Thief kits](KITS.md#thief-kits),
and the Shinobi's slots by level in
[Kits' spell slots](KITS.md#kits-spell-slots), on the Kits page.

**Starting gear.** Bone long sword, sling, leather chest armour; with fuller
starting gear, also leather arm and leg armour (an Assassin or Shinobi a cloak
too).

**Dual class.** With DEX 15, a human thief can become a cleric, druid, fighter, gladiator,
preserver, psionicist or ranger.

### Preserver

*d4 · INT · elf, half-elf, human · XP for 2nd level 2,500, for 10th 250,000*

**How it plays.** The strongest magic and the weakest body: no armour, few
weapons, a d4 hit die. Keep it back, act before the enemy reaches it (a
character hit in a round [can't cast](#initiative)), and choose its spells well.

**What the mod changes.**

- **INT limits learning:** a chance to learn each scroll's spell, and a limit on
  the spells it knows of each level ([learning
  spells](#learning-preserver-spells)). *Without the mod:* every scroll learnt,
  no limit.
- It **chooses** its starting spells and one at each level up. EXIT while
  choosing its starting spells gives it the game's usual ones for the rest.
- AD&D's wizard [spell slots](#spell-slots) (4 2 1 at 5th level; *without the
  mod:* 3 2 1).
- Six **new spells**: Cat's Grace, Erdlu Claw, Fogbolt, Reflected Image,
  Spook and Friends.
- With another class it may wear that class's armour but **can't cast in
  it**. **Bracers of Defense** and the mod's two **robes** give AC without
  being armour.
- Hit dice rolled twice; levels up to the [XP cap](#experience-and-levels).

**Weapons and armour.** No armour or shield as a single class. Daggers,
quarterstaffs, slings and staff slings (and the odd magic weapon the game
allows them).

**Kits.**

*Arcanist.* Scholars of the Veiled Alliance who live for the Art, hoarding
spells while their bodies wither from years of study in hiding. Their spells
strike and last as a preserver's a level beyond them.

*Scholar.* Keepers of forbidden lore who have spent more time over hidden
libraries than learning to hold a weapon. A Scholar learns two spells at
each level where another preserver learns one, and so has the right one to
hand more often; its touch spells miss a little more often for it.

*Battle Mage.* Preservers who learned in the arena or the legions that a spell
is no use if you are dead before you finish it. They fight in leather with a
chosen weapon and keep casting while others bleed, at the cost of a little of
their magic.

Each kit's gains, costs and starting gear:
[Preserver kits](KITS.md#preserver-kits) on the Kits page.

**Starting gear.** Quarterstaff, sling; two 1st-level spells of its choice.

**Dual class.** With INT 15, a human preserver can become a cleric, druid, fighter, gladiator,
psionicist, ranger or thief. A human who becomes a preserver chooses its first two spells.

### Cleric

*d8 · WIS · any race · XP for 2nd level 1,500, for 10th 450,000*

**How it plays.** A priest of one element (air, earth, fire or water) in any
armour, knowing every spell of its spheres from the start, with bonus slots
for WIS. Its element decides its weapons, so choose with them in mind: earth
has the most, air and fire the fewest.

**What the mod changes.**

- AD&D's priest [spell slots](#spell-slots) (3 3 1 at 5th level; *without the
  mod:* 3 2 1) and THAC0 (20 to 3rd level, 18 at 4th; *without the mod:* 19 at
  3rd).
- With another class, its sphere still limits weapons. *Without the mod:* the
  other class's list was enough.
- Hit dice rolled twice; levels up to the [XP cap](#experience-and-levels).

**Weapons and armour.** Any armour and shield. Weapons by sphere:

| Sphere | May wield | Plain weapons |
|---|---|---|
| Air | missile and thrown weapons, daggers, cahulaks | daggers (any material), cahulaks, chatkcha, bow, sling, staff sling |
| Earth | stone, obsidian, metal, wood | obsidian and metal long swords, daggers and short swords; metal and obsidian maces, axes and great axes; club; stone and metal picks; quarterstaff; metal polearm; metal and obsidian cahulaks; chatkcha; bow |
| Fire | obsidian | obsidian long sword, dagger, short sword, mace, axe, great axe and cahulaks; chatkcha |
| Water | bone, wood | bone long sword, dagger, short sword, mace, axe, great axe and polearm; club; quarterstaff; gythka; cahulaks; bow |

**Kits.**

*Healer.* Water priests who answer to the needs of the dying more than to the
temples. They pray to the cosmos as well as to water, so they have the cures
and other spells only druids are given, Cure Serious and Critical Wounds and
Raise Dead among them (never the harming ones), but no other element answers them, not even if they
take up another calling: a Healer who becomes a ranger serves water.
They keep a free hand for the work and won't fill it with a weapon.

*Crusader.* Warrior priests who carry their element's anger into battle, as
deadly with a weapon as any soldier. Their prayers are fewer for it.

*Elementalist.* Priests who have bargained with two of the elemental lords at
once and wield both powers. Divided worship comes slowly, and their spells lag
a level behind.

Each kit's gains, costs and starting gear:
[Cleric kits](KITS.md#cleric-kits) on the Kits page.

**Starting gear.** Shield, leather chest and arm armour, a club in the
backpack; with fuller starting gear, also a weapon of its sphere in hand (the
club; an air cleric an obsidian dagger, a fire cleric an obsidian mace),
leather leg armour and a missile weapon its sphere allows (air a sling, earth
and fire a chatkcha; water none).

**Dual class.** With WIS 15, a human cleric can become a fighter, gladiator, preserver, psionicist,
ranger (if good) or thief; never a druid.

### Druid

*d8 · WIS, CHA · half-elf, halfling, human, mul, thri-kreen · true neutral · XP
for 2nd level 2,000, for 10th 125,000*

**How it plays.** A priest of the land and its element: no armour, but any
weapon, the cheapest levels in the game, and the only priest with the common
4th and 5th-level spells (the great cures among them), but for a Healer
cleric. +2 on saves against fire and electricity.

**What the mod changes.**

- AD&D's priest [spell slots](#spell-slots) and THAC0, as the cleric's.
- Hit dice rolled twice; levels up to the [XP cap](#experience-and-levels).

**Weapons and armour.** No armour or shield, but the mod's two robes. Every
weapon but the great axes (the game's lists).

**Kits.**

*Grove Warden.* Guardians of an oasis or a hidden grove, whose skin toughens
like bark the longer they keep watch. They take up only the weapons their
element allows, as a cleric of it does.

*Wanderer.* Druids with no grove of their own, crossing salt flats and stony
barrens under the sun and the freezing night. Heat and cold barely touch them,
but they rarely stop long enough to armour themselves properly.

*Lifebinder.* Druids devoted to the life in what defilers have left behind,
mending wounds as they would mend a dying field. They fight only with blunt
weapons, which wound without spilling blood, and never learn the spells that
harm.

Each kit's gains, costs and starting gear:
[Druid kits](KITS.md#druid-kits) on the Kits page.

**Starting gear.** Club, sling.

**Dual class.** With WIS and CHA 15, a human druid can become a fighter, gladiator, preserver,
psionicist or thief; never a cleric, nor a ranger (who must be good). A human of another class
becomes a druid only if true neutral.

### Psionicist

*d6 · CON, WIS · any race · XP for 2nd level 2,200, for 10th 400,000*

**How it plays.** The master of the mind's three disciplines, with a new power
at each level (two at odd levels and at 4th) paid for in PSP. Light armour and
small weapons; +2 on saves against mind-affecting spells and charms. Every
other character has one discipline and uses it as a 1st-level psionicist.
Every new character picks its powers when it is made: four of its discipline,
or a psionicist as many as its level gives, from all three; all know Mind
Blank ([features](FEATURES.md#psionic-powers-at-creation)).

**What the mod changes.**

- Its limits on armour and weapons hold whatever its other classes. *Without
  the mod:* another class's lists were enough.
- Hit dice rolled twice; levels up to the [XP cap](#experience-and-levels).

**Weapons and armour.** Light armour, a leather shield, or one of the mod's
robes. Daggers, bone and obsidian short swords, clubs, chatkchas and bows (the
game's lists leave out its maces, slings and the metal short sword). With
another class, also the maces, metal short sword and slings that class's lists
allow. No shield alone; a leather one with a fighter, gladiator, ranger or
cleric class.

**Kits.**

*Mind Warrior.* Students of the Way who turned their discipline to the body,
fighting like trained soldiers with minds as sharp as their blades. Their
training leaves a little less room for the powers of the mind.

*Mind Bender.* Masters of other minds, at ease reaching into thoughts and
bending wills. Moving the world with thought alone comes harder to them.

*Kineticist.* Psionicists who move the world with their minds, throwing stone
and flame with a thought. Reaching into another mind costs them more.

Each kit's gains, costs and starting gear: [Psionicist
kits](KITS.md#psionicist-kits) on the Kits page. The powers and their costs are
in [Psionics](#psionics).

**Starting gear.** Club, bow and arrows, leather chest armour; with fuller
starting gear, also leather arm and leg armour.

**Dual class.** With CON and WIS 15, a human psionicist can become a cleric, druid, fighter,
gladiator, preserver, ranger or thief.

## Kits

A character takes a kit, or none, when it is made, on the creation panel's
**KIT** page. [The Kits page](KITS.md) has who may take which, and each kit's
numbers and starting gear; the class sections above, and the multiclass kits
below, say who takes each kit on Athas.

- After DONE, on the weapon window, the **Myrmidon** picks its first weapon spec as any fighter
  does and is given the polearm as its second; the **Battle Mage**, **Crusader** and **Mind
  Warrior** pick their one (a melee weapon; a thri-kreen Mind Warrior may take the chatkcha), and
  the **Swashbuckler** its weapon of choice (long sword, dagger or short sword)
  ([who picks what](WEAPON-SPECS.md#who-picks-what)). The **Elementalist** picks its second sphere on the CLERICAL SPHERE list.
- A kit belongs to its class: a human who changes class keeps it, asleep until
  the new class's level passes the old. **One kit a character:** a human with a
  kit takes no other when it changes class; one with none may take one for
  the new class.
- Some kits rule out classes a human could change to; the DUAL window and the
  kit menu leave them out
  ([which, and why](KITS.md#kits-that-rule-out-classes-and-each-other)).
- The dice log names each change a kit makes to a new character's gear.
- Which kits change spell slots, and by how much at each level: [Kits' spell
  slots](KITS.md#kits-spell-slots) on the Kits page.

### Multiclass kits

Only the race named may take these, with all its classes taken at once. "Under the
open sky" is an outdoor map, or open ground outside a city's buildings.

*Battle Dancer* (elf cleric/fighter). Elven warrior-priests whose battle is a
dance, sword and bow moving to a rhythm only they hear. A good start lifts the
whole fight; a stumble costs them dearly.

*Shadowblade* and *Military Scout* (half-elf fighter/thief). Shadowblades are
half-elves who learnt that no one notices someone who belongs nowhere. Scouts
range ahead of armies and caravans: in the open they are at home, under a roof
less so.

*Wilderness Avenger* (half-elf druid/fighter). Sworn to the land's living
things, they hunt whatever profanes it and move through the wild as quietly as
any ranger. They have given up mending for harming: no healing spells, but their
wounding spells cut deeper.

*Rescuer* (half-elf cleric/ranger). They bring the lost back from the wastes
alive: their healing runs strong, and they cover ground quickly in a fight,
with no shield to slow them.

*Ghetto Fighter* and *Wayfinder* (dwarf fighter/thief). Ghetto Fighters grew
up in the cities' poorest quarters, where a dagger in each hand settles most
arguments. Wayfinders are dwarves whose focus is the hidden road: they slip
past unseen, but have little use for other people's purses, and a party they
guide acts that little bit quicker, the guide quickest of all.

*Spellarcher* (half-elf fighter/preserver). Half-elf freedom fighters who
weave a little magic into every arrow. The technique is a secret, and the bow
is all they train with, and they wear no armour. A Spellarcher starts with a
Fine Bow (+1 to hit, not magic) and 24 arrows of each touch spell it picked (24 plain arrows if
neither). Outside a fight,
it can spend a spell slot to weave one of its touch spells (Chill Touch,
Shocking Grasp, Vampiric Touch) into an arrow that casts the spell on what it
hits; the arrows last until shot, a stack of each spell of up to 24, and what one hits saves only
as the spell allows (against Chill Touch, not the others) ([how](KITS.md#spellarcher)).

*Titan Mind* (half-giant fighter/psionicist). Half-giants who turned the Way
inward, to their own great bodies; other minds remain a puzzle to them.

*Poisoner* (halfling fighter/thief). Halfling hunters whose blades
carry the jungle's venoms: each blade's first wound in a fight is poisoned. They
train with the dagger and the short sword alone, and travel light.

*Spirit Caller* (halfling cleric/psionicist). Shamans of the halfling tribes,
who speak to the spirits of sky and land. Under the open sky the spirits answer
loudly; behind walls, hardly at all.

*Wasteland Seer* (thri-kreen druid/fighter/psionicist). Thri-kreen who read the wastes as
others read books. The open land lends their spells and their minds its strength; walls
dull both.

*Wild Fury* (mul druid/fighter). Muls who broke out of the fighting pits for
the wastes, and found the land's own fury waiting there. When the blood starts
to flow they call on it: some days it answers; some days it only makes them
reckless.

Each kit's gains, costs and starting gear:
[Multiclass kits](KITS.md#multiclass-kits) on the Kits page.

**The game's own party** (START GAME with no party made), with kits on: Cermak
is an Arcanist, and the other three are given a feature of their own, not a
kit's. Gerakis fights wild, as a Wild Fury does; K'ratchek's spells and psionics
are stronger under the open sky, as a Wasteland Seer's are;
Cilla's hiding is never halved in daylight, as an Assassin's isn't (the dice
log calls her an Elven Shadow-walker). What each is given, and her chatkcha's
throws: [the game's own party](FEATURES.md#the-games-own-party).

## Weapon specialization and attacks

Warriors train in **weapon specs**: kinds of weapon, whatever their material
(a bone, obsidian or metal long sword is the long sword spec alike). Pick
them in a window of weapon pictures that comes up after **DONE** on the
creation screen, and again at a level up that brings another (point at one for
its name; those you can't pick are greyed); EXIT leaves the rest to the mod.
A fighter specializes in one (+1 to hit, +2 damage), on to mastery at 5th level
and grand mastery at 9th; a gladiator in two, a third at 6th level and a fourth
at 9th; a ranger has expertise with the bow and one more. With a chosen weapon
spec a warrior keeps 3/2 attacks a round in melee (2 from 7th level) and shoots
faster; with any other weapon it attacks once a round until 7th level. The
Battle Mage, Crusader, Mind Warrior and Swashbuckler pick one too.

Who picks what, the sixteen weapon specs, the attacks a round with every kind of
weapon, grand mastery's dice and the starting weapons: [Weapon
specs](WEAPON-SPECS.md).

*Without the mod:* every warrior has 3/2 attacks a round in melee (2 from 7th
level) with any weapon, and no other bonus; missile weapons shoot at the
weapon's own rate for everyone.

## Experience and levels

Experience comes from kills (an equal share for each character, split again
between a character's classes) and from deeds along the way. A level up comes
by itself, with hit points, a better THAC0 and saves, spell slots, a new
preserver spell or psionic power, and any weapon spec due.

A class whose **prime requisites are all 16 or more** ([the
table](#ability-scores)) gains **10% more XP** from everything, as the manual
has it: a fighter with STR 16, a ranger with STR, DEX and WIS 16. The
character's own scores count, not what an item or a spell gives. A character
of several classes has one XP for them all, so each class with the bonus adds
10% divided by the classes: a fighter/thief with both 10%, with one 5%. A
human counts the class it follows now. The Loader adds the bonus as each
award comes (the dice log shows it: `+12 for Fighter, STR 17`), so it needs the
Loader following the game; a level that the bonus alone reaches comes with the
next award. *Without the mod:* no bonus.

Levels stop at a cap of **749,999 XP**, shared out: a character of one class
goes up while its next level needs no more; two classes share it evenly
(374,999 each), three too (249,999); and a human who changed class has the
cap less what its old classes' levels needed (the game starts the new class
at 0 XP). XP keeps counting past the cap. The highest levels:

| Class | One class | Two classes | Three classes |
|---|---|---|---|
| Fighter | 10 | 9 | 8 |
| Gladiator | 10 | – | – |
| Ranger | 10 | 9 | 8 |
| Thief | 13 | 11 | 11 |
| Preserver | 11 | 10 | 9 |
| Cleric | 11 | 9 | 9 |
| Druid | 12 | 12 | 11 |
| Psionicist | 11 | 9 | 9 |

*Without the mod:* every class stops at 9th.

Past 9th everything is the game's own, which it had all along: its XP tables
go on to 20th (with AD&D's off, druids by a table of their own), and THAC0,
saves, spell slots and thief skills are worked out from the level ([hit
points](#hit-points), [THAC0](#thac0-by-level), [spell slots](#spell-slots)). A
gladiator's armour optimizing goes on (AC 2 better at 10th). A preserver still
picks a spell on CHOOSE A SPELL at each level, offered from spell level (class
level + 1) / 2 down but no higher than 5th; a psionicist picks a power (two at
odd levels and 4th). Spell damage that grows with the caster's level stops at level
10. The level up is the game's usual one, and View Character stops showing the
next level's XP at the cap.

AD&D's tables:

| To reach level | Fighter | Gladiator, ranger | Thief | Preserver | Cleric | Druid | Psionicist |
|---|---|---|---|---|---|---|---|
| 2 | 2,000 | 2,250 | 1,250 | 2,500 | 1,500 | 2,000 | 2,200 |
| 3 | 4,000 | 4,500 | 2,500 | 5,000 | 3,000 | 4,000 | 4,400 |
| 4 | 8,000 | 9,000 | 5,000 | 10,000 | 6,000 | 7,500 | 8,800 |
| 5 | 16,000 | 18,000 | 10,000 | 20,000 | 13,000 | 12,500 | 16,500 |
| 6 | 32,000 | 36,000 | 20,000 | 40,000 | 27,500 | 20,000 | 30,000 |
| 7 | 64,000 | 75,000 | 40,000 | 60,000 | 55,000 | 35,000 | 55,000 |
| 8 | 125,000 | 150,000 | 70,000 | 90,000 | 110,000 | 60,000 | 100,000 |
| 9 | 250,000 | 300,000 | 110,000 | 135,000 | 225,000 | 90,000 | 200,000 |
| 10 | 500,000 | 600,000 | 160,000 | 250,000 | 450,000 | 125,000 | 400,000 |
| 11 | 750,000 | 900,000 | 220,000 | 375,000 | 675,000 | 200,000 | 600,000 |
| 12 | 1,000,000 | 1,200,000 | 440,000 | 750,000 | 900,000 | 300,000 | 800,000 |
| 13 | 1,250,000 | 1,500,000 | 660,000 | 1,125,000 | 1,125,000 | 750,000 | 1,000,000 |

*Without the mod:* a gladiator needs what a fighter does, a ranger 2,200 for
2nd level and a thief 1,200.

### XP left over at the top

The cap stops levels, not XP: past a class's highest level the XP keeps
counting (to the game's own limit, 2,000,000,000), but no level comes of it.
What is left over is the cap less the XP the highest level needed. For a human
it is also the room a new class has: dual-classing starts the new class at 0
XP, and the new class may rise only as far as the cap less the old class's
level's XP allows.

One class, with AD&D's tables:

| Class | Highest level | XP it needs | Next level needs | Left over |
|---|---|---|---|---|
| Fighter | 10 | 500,000 | 750,000 | 249,999 |
| Gladiator | 10 | 600,000 | 900,000 | 149,999 |
| Ranger | 10 | 600,000 | 900,000 | 149,999 |
| Thief | 13 | 660,000 | 880,000 | 89,999 |
| Preserver | 11 | 375,000 | 750,000 | 374,999 |
| Cleric | 11 | 675,000 | 900,000 | 74,999 |
| Druid | 12 | 300,000 | 750,000 | 449,999 |
| Psionicist | 11 | 600,000 | 800,000 | 149,999 |

A human can change class before the top. The room left for the new class, by
the level the old class had when it changed:

| Old class's level | Fighter | Gladiator, ranger | Thief | Preserver | Cleric | Druid | Psionicist |
|---|---|---|---|---|---|---|---|
| 3 | 745,999 | 745,499 | 747,499 | 744,999 | 746,999 | 745,999 | 745,599 |
| 4 | 741,999 | 740,999 | 744,999 | 739,999 | 743,999 | 742,499 | 741,199 |
| 5 | 733,999 | 731,999 | 739,999 | 729,999 | 736,999 | 737,499 | 733,499 |
| 6 | 717,999 | 713,999 | 729,999 | 709,999 | 722,499 | 729,999 | 719,999 |
| 7 | 685,999 | 674,999 | 709,999 | 689,999 | 694,999 | 714,999 | 694,999 |
| 8 | 624,999 | 599,999 | 679,999 | 659,999 | 639,999 | 689,999 | 649,999 |
| 9 | 499,999 | 449,999 | 639,999 | 614,999 | 524,999 | 659,999 | 549,999 |
| 10 | 249,999 | 149,999 | 589,999 | 499,999 | 299,999 | 624,999 | 349,999 |
| 11 | – | – | 529,999 | 374,999 | 74,999 | 549,999 | 149,999 |
| 12 | – | – | 309,999 | – | – | 449,999 | – |
| 13 | – | – | 89,999 | – | – | – | – |

Look the room up in the XP table above: a fighter who changes at 9th has
499,999, enough for a 10th-level cleric (450,000); one who changes at 10th has
249,999, enough for a 9th. A human who changes class twice has the cap less
both old levels' XP.

Two or three classes share the cap (374,999 or 249,999 each):

| Class | Two classes: highest level | Left over | Three classes: highest level | Left over |
|---|---|---|---|---|
| Fighter | 9 | 124,999 | 8 | 124,999 |
| Ranger | 9 | 74,999 | 8 | 99,999 |
| Thief | 11 | 154,999 | 11 | 29,999 |
| Preserver | 10 | 124,999 | 9 | 114,999 |
| Cleric | 9 | 149,999 | 9 | 24,999 |
| Druid | 12 | 74,999 | 11 | 49,999 |
| Psionicist | 9 | 174,999 | 9 | 49,999 |

With the game's own XP tables (AD&D's off), a gladiator has the fighter's
numbers (249,999 left over), and a druid needs 675,000 for 11th and 900,000
for 12th, so stops at 11th with 74,999 left over (10th with two or three
classes: 249,999 or 124,999). *Without the mod:* every class stops at 9th, all
XP past 9th's need is left over, and a human who changes class loses it.

### Hit points

| Class | Hit die | At 10th level | Past 10th |
|---|---|---|---|
| Fighter, gladiator, ranger | d10 | +3 | +3 |
| Cleric, druid | d8 | +2 | +2 |
| Psionicist | d6 | +2 | +2 |
| Thief | d6 | d6 | +2 |
| Preserver | d4 | d4 | +1 |

- **Every hit die is rolled twice and the better kept,** at creation (one die
  for every starting level) and at every level up. *Without the mod:* one roll.
- **The hit points are as rolled:** clicking them on the creation screen does
  nothing. Changing CON there adds or takes off its bonus for every level.
  *Without the mod:* a click sets them anywhere the dice could have, and a
  higher CON adds nothing unless they are below the new least.
- Half-giants roll double. A roll counts at least 2 with CON 20, 3 with CON
  21-22 and 4 with CON 23 or more.
- CON 20 or more gives a party member hit points back by themselves, one an
  hour at CON 20, 50 minutes at 21, 40 at 22, 30 at 23, 20 at 24 and 10 at
  25 ([CON as in AD&D](FEATURES.md#con-as-in-add)); minutes short of the next
  one count towards it later (`Gerakis regenerates 1 HP (CON 22), now 12/54
  HP`). *Without the mod:* one every 5 minutes at any of them.
- Two [kits](#kits) change the die: a **Battle Mage** rolls a d6, an **Arcanist** a d3.
- **CON's bonus** comes with every level: for a fighter, gladiator or ranger
  +1 at CON 15, +2 at 16, +3 at 17, +4 at 18, +5 at 19-20, +6 at 21-23 and +7 at
  24-25 (−1 at 4-6); for anyone else at most +2.
- **A character of several classes** adds CON's bonus to every die (the
  fighter's bonus on every die if one of its classes is a warrior), and the
  total is divided by the number of classes. *Without the mod:* the dice are
  added and the total divided, and CON's bonus counts once a level of the
  highest class.
- At 0 hit points a character is Out Cold; at −10, dead.

### THAC0 by level

AD&D's tables; a character of several classes uses its best. The creation
screen shows it with STR and DEX counted, right of the hit points
(`THAC0: M18 R19`: melee with STR's to-hit adjustment, ranged with DEX's
missile adjustment), so a click on either shows what it does; the inventory
screen's THAC0 counts the weapon in hand too.

| Level | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Fighter, gladiator, ranger | 20 | 19 | 18 | 17 | 16 | 15 | 14 | 13 | 12 | 11 | 10 | 9 | 8 |
| Cleric, druid | 20 | 20 | 20 | 18 | 18 | 18 | 16 | 16 | 16 | 14 | 14 | 14 | 12 |
| Thief | 20 | 20 | 19 | 19 | 18 | 18 | 17 | 17 | 16 | 16 | 15 | 15 | 14 |
| Psionicist | 20 | 20 | 19 | 19 | 18 | 18 | 17 | 17 | 16 | 16 | 15 | 15 | 14 |
| Preserver | 20 | 20 | 20 | 19 | 19 | 19 | 18 | 18 | 18 | 17 | 17 | 17 | 16 |

*Without the mod:* clerics and druids improve by about 2/3 a level (19 at
3rd, 17 at 6th, 15 at 9th); the rest are as above.

## Fighting

### Initiative

At the start of each round everyone's initiative is **20 + a 0-9 roll + DEX's
adjustment**, +2 Hasted, −2 Slowed, −2 Blind; highest acts first. The weapon
makes no difference. **Wait** drops a character to act later.

| DEX | 1 | 2 | 3 | 4 | 5 | 6-15 | 16 | 17-18 | 19-20 | 21-23 | 24-25 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Adjustment | −6 | −4 | −3 | −2 | −1 | 0 | +1 | +2 | +3 | +4 | +5 |

A character hit in a round can't cast a spell until the next round: the game
won't let it choose a spell, and drops one chosen before the hit. The Battle
Mage isn't stopped.

### Moving in a fight

Each round a character has **ten movement points for each point of Move** (the
name box shows what is left, in Move); Hasted doubles them, Slowed halves
them. A step costs **10 straight, 14 diagonally**. With fewer than 10 left the
walk is over.

- **The squares still in reach are marked** with small crosses on the
  floor ([squares in reach](FEATURES.md#squares-in-reach)): a marked square is
  one click away (behind a wall the farthest may take two: click a nearer one
  first).
- Nobody walks through anybody, allies included; corners can be cut.
- Walking past an enemy costs nothing and brings no free blow.
- **F10 takes a move back** (the game's own key): the character stands where
  its turn began, with its movement. Use it before the last step: once the
  movement is all spent F10 puts the character back but it can't walk again
  that turn.

The detail: [how the game works](HOW-THE-GAME-WORKS.md#moving-in-a-fight).

### Hitting

An attack hits on **d20 ≥ THAC0 − the target's AC**. A 20 always hits and a 1
always misses, but **there are no critical hits**: a 20 does ordinary damage.
To-hit changes with:

- STR in melee, DEX with missiles;
- the weapon's plus, or a plain weapon's material
  ([weaker materials](#what-each-class-may-use));
- weapon specialization;
- Bless and Prayer +1, Curse −1, Slow −4;
- attacking from behind +2, a backstab +2 more;
- two weapons ([below](#two-weapons)).

Damage is the weapon's dice, its plus, specialization's bonus and, in melee,
STR's bonus; at least 1.

A **held** (Paralyzed) or **Out Cold** target is hit automatically, a 1 too,
for normal damage, as in AD&D; a held party member too. *Without the mod:* the
d20 was rolled as ever, and a hit did double damage.

### Two weapons

With a melee weapon in each hand:

- **−2 to hit with the main (right) hand and −4 with the off (left) hand,** and
  the DEX adjustment from [initiative](#initiative) added, which can lessen the
  penalty to 0 but never make it a bonus: DEX 17 is 0 and −2, DEX 21 is 0 and 0,
  DEX 3 is −5 and −7.
- **Rangers, Twin-blades and Battle Dancers** have no penalty while all their
  armour is light (leather, or none), a Twin-blade with cahulaks too; a Justifier has none in any armour, and a
  Ghetto Fighter's is 0 and −2.
- **The off hand attacks once a round.** Extra attacks are the main hand's: a
  warrior at 3/2 attacks 3/2 + 1 (one round 1 + 1, the next 2 + 1).

A weapon and a shield, or a weapon and a bow or sling, aren't two weapons.
[Cahulaks](#cahulaks), a head in each hand, fight under the same penalties.

*Without the mod:* no penalty (a small bonus at DEX 5 or less), and each hand
attacks at the character's full rate.

### From behind, and backstabs

- Each round a creature turns to face the first one to attack it, and keeps
  facing that way. An attacker in the square directly behind it attacks
  **from behind**: +2 to hit, and the target loses its DEX bonus and its
  shield.
- A **backstab** is a thief's attack from behind, in melee, with a weapon no
  heavier than a long sword (see [Equipment](#equipment)): +4 to hit in all,
  and the thief's first attack of the round multiplies the **weapon's dice**
  **×2** at levels 1-4, **×3** at 5-8, **×4** at 9-12 and **×5** at 13 (an
  Assassin's one step more); STR's bonus and the weapon's plus are added once
  after. *Without the mod:* the whole damage, STR included, is multiplied, on
  the round's first two attacks.

### The chance shown before the swing

With an enemy chosen with **Tab** ([the chance to hit before the
swing](FEATURES.md#the-chance-to-hit-before-the-swing)), the dice log's line and the combat log's
header say what the member whose turn it is must roll, and the chance: `needs 14+ (35%)`. A 20
always hits and a 1 always misses, so the chance is never above 95% or below 5%.

- **Which weapon.** Next to the enemy it is the weapon in hand (each of two, named, when their
  numbers differ). Farther off, Enter walks the member up to fight hand to hand, and the attack
  pointer shoots: both are given, `Bone Long Sword needs 14+ (35%); Short Bow needs 12+ (45%)`.
  They are listed in the order the game swings them (often the left hand's first), and the header
  gives the first.
- **From behind.** Next to the enemy the Loader knows whether the attack is [from
  behind](#from-behind-and-backstabs) and says so: `needs 10+ (55%) from behind`, `a backstab` for a
  thief's. Farther off it depends on where the walk ends, so both numbers are given: `needs 14+
  (35%), from behind 10+ (55%)` (in the header `14+ 35%, behind 10+`). An enemy nobody has attacked
  yet this round turns to face its first attacker, so only the first number is given; and a shot is
  never from behind, except a hidden archer's (`unseen`).
- **A hidden thief** ([hiding in shadows](#hiding-in-shadows)) attacks from behind wherever it
  stands, and the number is the backstab's.
- **A held enemy** (Paralyzed or Out Cold): `hits whatever the roll (Paralyzed)`.

What it can't know: the number is for things as they stand when Tab is pressed (the header's
follows them while the enemy stays chosen); a spell cast or an effect ending before the swing
changes it. An enemy's AC is counted from the game's own rules and its rings of protection; what
else the mod's rules add to it (a kit's AC, a cloak of protection, the Boots of Speed) is known from
the first attack on that enemy in the fight on, so before it the number can be off by that much
for an enemy that has one of them. The swing's own line in the dice log is always the game's.

### Hiding in shadows

A thief or ranger whose turn comes in a fight **with no enemy in the eight
squares around** first tries to **hide in shadows**, then to **move
silently**. With both, their next attack that turn is from behind: a thief's is
a backstab with a light enough weapon (not a Military Scout's). Attacking, or
ending the turn, gives them away. A soft breath sounds as one hides. An enemy beside them when the turn comes
means no hiding: get clear first (a Shadowblade tries anyway).

- Thieves' hiding is **halved in daylight** (under the open sky; not an
  Assassin's, a Military Scout's or Cilla's); rangers' is halved indoors
  instead. Open desert and rock, the villages' open ground and the arena are
  under the open sky; the slave pens, the sewers, the lava caverns and other
  underground or roofed places aren't. Where buildings stand on open ground,
  it goes by the floor under the hider: in a building it is out of the sun, in
  a roofless ruin it isn't.
- A worn cloak adds 10 to hiding in shadows and worn boots 10 to moving
  silently, up to 95. A worn belt adds 5 to a thief's picking pockets and
  opening locks. The inventory screen's thief skills count them.
- The **Cloak of Elvenkind** makes its wearer all but invisible: it hides at
  95 under the open sky and 90 under a roof, never halved by the light (or
  with its own chance, if that is better). The **Boots of Elvenkind** make it
  silent: it moves silently at 95 at least. Thieves and rangers only.

*Without the mod:* thieves backstab only a target that has turned to face
someone else, and no one hides in a fight.

### Saving throws

A save succeeds when **d20 + its modifiers reaches the save's number**; a 1
always fails and a 20 always saves. Everyone has five: paralysis, poison and
death (`PPD`), rod, staff and wand (`RSW`), petrification and polymorph
(`PP`), breath weapon (`BW`) and spell (`SP`). Each character's five numbers,
by class and level, are on the inventory screen's panel and on View Character.

- **Spells are saved against with the spell save**, except poisons, death
  spells and psionic attacks (paralysis, poison and death).
- **Against fire, cold and electricity spells, DEX helps you dodge:**

  | DEX | 1-2 | 3 | 4 | 5 | 6 | 7-14 | 15 | 16 | 17 | 18-20 | 21-23 | 24-25 |
  |---|---|---|---|---|---|---|---|---|---|---|---|---|
  | Modifier | −5 | −4 | −3 | −2 | −1 | 0 | +1 | +2 | +3 | +4 | +5 | +6 |

*Without the mod:* almost every spell is saved against with petrification and
polymorph, and against fire, cold and electricity the d20 counts double, so
most saves against a Fireball succeed.

Other modifiers:

| Modifier | On |
|---|---|
| WIS: −6 at 1, −4 at 2, −3 at 3, −2 at 4, −1 at 5-7, +1 at 15, +2 at 16, +3 at 17, +4 at 18 or more | mind-affecting spells, charms, holds, fear and illusions |
| CON: −2 at 1, −1 at 2, +1 at 19-20, +2 at 21-22, +3 at 23-24, +4 at 25; dwarves and halflings +1 more for every 3.5 points of CON (against poison, with [CON as in AD&D](FEATURES.md#con-as-in-add), in place of CON's own) | paralysis, poison and death |
| Druids +2 | fire and electricity |
| Psionicists +2 | mind-affecting spells and charms |
| Bless +1, Barkskin +1, Spirit Armor +3 (not PPD), Prayer ±1, a ring or cloak of protection +1 | every save |
| Protection from Evil +2; from Fire, from Cold +3; from Lightning +4 | against the matching caster or spell |
| +4 | against a spell at you alone, when its caster can't see you |

Creatures of 6th level or less can't save against Cloudkill; only warriors
save against Chaos; against Scare, 6th level and up always save, an elf or
half-elf priest below that saves as usual, and others can't. *Without the
mod:* no one below 6th level could save against Scare.

### Monsters

Monsters have defences of their own: some need magic weapons, some are hurt
only by edged weapons or immune to crushing ones, some shrug off fire, cold,
poison or the powers of the mind, some can't be charmed or held. **Look** at
one in a fight: the box shows its hit points, AC, THAC0, alignment, magic
resistance and chief defence (`NEEDS +1 WEAPON`, `IMM FIRE COLD`, `NO CRUSH`,
`HALF FROM WPNS`, `UNDEAD`), and closing it tells the rest. Undead take
nothing from poison or draining, and mind-affecting spells don't work on them.

## Thieves' skills and picking pockets

A thief's skills come from the table by thief level, plus the race's and
DEX's adjustments. A thief who isn't Okay, or is Blind, Afraid, Confused,
Berserk or Paralyzed, can't use them. Worn gear doesn't lower the skills.
The one exception: a thief with another class, in armour heavier than leather,
hide or silk, has all skills at 0. No skill goes above 95, whatever the table
says (its 99s are 95 in play).

| Thief level | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Pick pockets | 30 | 35 | 40 | 45 | 50 | 55 | 60 | 65 | 70 | 80 | 90 | 95 | 99 |
| Open locks | 25 | 29 | 33 | 37 | 42 | 47 | 52 | 57 | 62 | 67 | 72 | 77 | 82 |
| Find/remove traps | 20 | 25 | 30 | 35 | 40 | 45 | 50 | 55 | 60 | 65 | 70 | 75 | 80 |
| Move silently | 15 | 21 | 27 | 33 | 40 | 47 | 55 | 62 | 70 | 78 | 86 | 94 | 99 |
| Hide in shadows | 10 | 15 | 20 | 25 | 31 | 37 | 43 | 49 | 56 | 63 | 70 | 77 | 85 |
| Hear noise | 10 | 10 | 15 | 15 | 20 | 20 | 25 | 25 | 30 | 30 | 35 | 35 | 40 |
| Climb walls | 85 | 86 | 87 | 88 | 90 | 92 | 94 | 96 | 98 | 99 | 99 | 99 | 99 |
| Read languages | 0 | 0 | 0 | 20 | 25 | 30 | 35 | 40 | 45 | 50 | 55 | 60 | 65 |

| Race | Pick pockets | Open locks | Find/remove traps | Move silently | Hide in shadows | Hear noise | Climb walls | Read languages |
|---|---|---|---|---|---|---|---|---|
| Dwarf | 0 | +10 | +15 | 0 | 0 | 0 | −10 | −5 |
| Elf | +5 | −5 | 0 | +5 | +10 | +5 | 0 | 0 |
| Half-elf | +10 | 0 | 0 | 0 | +5 | 0 | 0 | 0 |
| Halfling | +5 | +5 | +5 | +10 | +15 | +5 | −15 | −5 |
| Mul | 0 | −5 | 0 | +5 | 0 | 0 | +5 | −5 |

(Humans, half-giants and thri-kreen have none.)

| DEX | Pick pockets | Open locks | Find/remove traps | Move silently | Hide in shadows |
|---|---|---|---|---|---|
| 9 | −15 | −10 | −10 | −20 | −10 |
| 10 | −10 | −5 | −10 | −15 | −5 |
| 11 | −5 | 0 | −5 | −10 | 0 |
| 12 | 0 | 0 | 0 | −5 | 0 |
| 13-15 | 0 | 0 | 0 | 0 | 0 |
| 16 | 0 | +5 | 0 | 0 | 0 |
| 17 | +5 | +10 | 0 | +5 | +5 |
| 18 | +10 | +15 | +5 | +10 | +10 |
| 19 | +15 | +20 | +10 | +15 | +15 |
| 20 | +20 | +25 | +12 | +20 | +17 |
| 21 | +25 | +27 | +15 | +25 | +20 |
| 22 | +27 | +30 | +17 | +30 | +22 |

Rangers hide and move silently with the thief's numbers for their ranger level
and the same race and DEX adjustments.

**When the skills are rolled:**

- **Open locks, find/remove traps, climb walls, hear noise** and the one
  pocket the game has to pick: when the game asks, at certain locks, traps
  and walls. A locked and trapped chest the mod adds asks a thief to check
  it for traps first, then to pick the lock (again and again; with **Thieves as in AD&D**, a thief
  who fails must gain a thief level before trying that lock again, though
  another thief may try); anyone
  else may try to bash it open, which sets off a trap still in it. A trap
  that goes off may still be avoided by the party's best at find/remove
  traps.
- **Hide in shadows and move silently:** at the start of a thief's or ranger's
  turn in a fight ([hiding in shadows](#hiding-in-shadows)).
- **Picking pockets** (the mod's): on the **USE** screen, press the thief's
  **Pick Pockets** button (a purse, where a priest's Turn Undead is), then
  click someone in sight with the talking pointer (not in a fight). Any thief
  can, party leader or not, so long as their backpack has room. The thief
  rolls **pick pockets**:
  - **success:** one small thing from them goes into the thief's backpack
    (with a purse's jingle): something light that isn't worn on the body;
  - **failure:** the thief rolls **move silently** to slip away. Made, they can
    try again at once; missed, they are caught, and that person keeps a hand on
    their pockets from then on (with Thieves as in AD&D, until that thief has
    gained a level; another thief may try at once).

  When nothing worth taking is left, the thief takes 2 to 5 ceramic pieces
  from the purse for each thief level (a 4th-level thief 8 to 20), and that is
  the last try on them. A cleric/thief has both buttons outside fights, the
  purse beside Turn Undead; in a fight, Turn Undead alone.

  In more detail:
  - **What can be lifted:** something weighing 10 or less (a bag or arrows are
    10, a helm 15, a long sword 30) that isn't worn on the body (armour, a belt,
    boots, a helm, a cloak), wherever its owner keeps it: a dagger, a ring, an
    amulet, a gem, food. Keys stay, as scripts may look for them. Three weapons
    some of the game's people carry can be lifted whatever their weight
    ([Items](ITEMS.md#every-magic-item) says which, with spoilers): each is
    worth 200 XP to the thief once a game, given as a quest's is, with its
    sound (split among a multiclass thief's classes; sold and lifted back, it
    is worth nothing more). Anything else lifted, or the coins, comes with a
    purse's jingle.
  - **When there is no try:** a thief whose backpack is full can't try
    ("Daaki's backpack is full."): nothing is rolled, and it doesn't count. A
    right click on the map that changes the pointer puts the try away. The
    Trustee is left to his own conversation, where the game's one pocket is.
  - **Who remembers:** the Loader keeps who has caught a thief, or been
    emptied of coins, for this party, by the time on the game's clock: load a
    game saved before the try and the clock goes back past it, so the try is
    forgotten and that person can be tried again. A caught thief's dice log
    line says why it can't try yet (the person "remembers Daaki, and keeps a
    close hand on their purse").
  - The game's message window and the dice log say what happened:
    `Daaki picks Kurzak's pocket: d100 = 71, needs 63 or less -> failed`, then
    `Daaki moves silently to get away: d100 = 12, needs 55 or less -> success`.
- **Read languages** is rolled only when a Shinobi reads a scroll.

*Without the mod:* the game's own chances, which run much higher (a base of its
own plus 4 a level), and a penalty when a thief holds anything in either hand,
or has anything in the quiver or on the legs.

## Magic

### Spell slots

Casting uses a slot of the spell's level; resting fills them.

AD&D's tables (the slots at 1st, 2nd, 3rd... spell level), to the highest
level each class reaches under the XP cap (a druid's 12th, a cleric's and a
preserver's 11th):

| Level | Cleric, druid | Preserver |
|---|---|---|
| 1 | 1 | 1 |
| 2 | 2 | 2 |
| 3 | 2 1 | 2 1 |
| 4 | 3 2 | 3 2 |
| 5 | 3 3 1 | 4 2 1 |
| 6 | 3 3 2 | 4 2 2 |
| 7 | 3 3 2 1 | 4 3 2 1 |
| 8 | 3 3 3 2 | 4 3 3 2 |
| 9 | 4 4 3 2 1 | 4 3 3 2 1 |
| 10 | 4 4 3 3 2 | 4 4 3 2 2 |
| 11 | 5 4 4 3 2 1 | 4 4 4 3 3 |
| 12 (druid) | 6 5 5 3 2 2 | – |

The 6th-level slots are for the mod's 6th-level priest spells. Preservers have
no 6th-level spells.

*Without the mod:* one table for all three: 1; 2; 2 1; 2 2; 3 2 1; 3 2 2;
4 3 2 1; 4 3 2 2; 5 4 3 2 1; 5 4 3 2 2.

**Rangers** have one 1st-level slot at 8th level, two at 9th, and a 2nd-level
slot at 10th, as in AD&D.

**Clerics and druids** have more for WIS, the game's own rule (the bonus
slots at 1st, 2nd, 3rd... spell level). They count only at spell levels the
class level reaches, the 6th-level ones too (AD&D's class tables bring the
6th-level slots):

| WIS | 1st | 2nd | 3rd | 4th | 5th | 6th |
|---|---|---|---|---|---|---|
| 13 | 1 | | | | | |
| 14 | 2 | | | | | |
| 15 | 2 | 1 | | | | |
| 16 | 2 | 2 | | | | |
| 17 | 3 | 2 | 1 | | | |
| 18 | 3 | 2 | 2 | | | |
| 19 | 3 | 3 | 2 | 1 | | |
| 20 | 3 | 3 | 2 | 2 | | |
| 21 | 3 | 3 | 3 | 2 | 1 | |
| 22 | 3 | 3 | 3 | 2 | 2 | |
| 23 | 3 | 3 | 3 | 3 | 2 | 1 |
| 24 | 3 | 3 | 3 | 3 | 2 | 2 |
| 25 | 3 | 3 | 3 | 3 | 3 | 2 |

These are more than AD&D's own table gives (WIS 18: 2 2 1 1 there). The game's
rule also gives WIS 25 a 7th-level slot, of no use: there are no 7th-level
spells.

A character's classes add up their slots. Several [kits](#kits) have more or
fewer. The game's USE screen shows what is left of each level.

### Learning preserver spells

A preserver chooses a spell at each level up, and can learn more from scrolls
(right-click the scroll in the inventory, then click its icon; the result
shows on the line under the paper doll), of a level it can cast. INT sets two
limits:

| INT | Chance to learn from a scroll | Most spells of each level |
|---|---|---|
| 9 | 35% | 6 |
| 10 | 40% | 7 |
| 11 | 45% | 7 |
| 12 | 50% | 7 |
| 13 | 55% | 9 |
| 14 | 60% | 9 |
| 15 | 65% | 11 |
| 16 | 70% | 11 |
| 17 | 75% | 14 |
| 18 | 85% | 18 |
| 19 | 95% | all |
| 20-23 | 96-99% | all |
| 24-25 | 100% | all |

- **A failed roll uses the scroll up.**
- **A full spell level** learns no more: the scroll is kept.
- The level-up choice leaves out levels already full.
- **A Shinobi** learns only its own spells from scrolls, and first has to read
  the scroll: a roll against its read languages, then INT's chance.
- **Defilers sometimes carry scrolls:** each defiler in a fight has a 1 in 20
  chance of carrying a scroll of a random preserver spell, found on its body
  when it dies.

*Without the mod:* every scroll is learnt, and there is no limit.

### How spells work

- **Damage** grows with the caster's level up to **10th**: Fireball and
  Lightning Bolt do at most 10d6. Someone Out Cold gets no save and takes the
  most the dice can do.
- **Duration** is so much a caster level plus dice; a round is a minute of game
  time.
- **Caster level** is the caster's best level in a class whose sphere has the
  spell. A ranger casts at its level less 7, for what it may cast and for
  damage and duration alike. An elemental spell works only for a priest of
  that element.
- **Area spells catch the caster** and the party.
- **Hold Person, Charm Person and Charm Person or Mammal** don't work on a
  large target (a half-giant, a large monster, anyone Enlarged), with no save;
  Charm Person or Mammal still charms a large beast ([size](#size)).
  *Without the mod:* the game keeps no sizes.
- **Spells roll to hit** (a rule change, on by default). The missile spells,
  Acid Arrow, Turn Pebble to Boulder, Magical Stone, Condense and each of Minute
  Meteors' five globes (at +2), roll a d20 against the target's AC as a weapon
  would (Acid Arrow with a fighter's THAC0 of the caster's level, the rest with
  the caster's own, and DEX's missile adjustment), and so does a touch spell
  cast at an enemy (Chill Touch, Shocking Grasp, Vampiric Touch, the Cause
  Wounds spells, Cause Disease, Poison), with STR's. A 20 always hits, a 1
  always misses, and a miss does nothing (no damage, no Acid burning on, no
  effect; the dice log shows the damage roll that was lost): "Miss" floats
  over the target. The roll is the game's own for an attack: the target's AC
  as the game works it out for a blow (armour, DEX, Shield, Blur), with Bless,
  Prayer, Curse and the rest, and for a monster the game's difficulty setting.
  A touch spell on one's own side lands as before, and a spell from a weapon's
  hit (a spell arrow, a magical weapon) doesn't roll again. Monsters' spines
  roll too. Magic Missile, Flame Arrow (neither the manual nor AD&D gives its
  bolts an attack roll), areas, cones and psionic powers are left as they
  are. *Without the mod:* they always landed.
- **Spells and psionics as the manual describes them** (a rule change, on by
  default): twenty-four spells and two psionic powers, and seven monsters, as the manual
  has them (Solid Fog for a few rounds, not the whole fight; Hold Undead only
  on undead of the caster's level or lower; Strength by class; shadows that
  drain STR; the list is in [How the game
  works](HOW-THE-GAME-WORKS.md#the-spells-and-powers-it-changes)).
- **Turn Undead**, the cleric's button on the USE screen, follows AD&D's
  turning table (with the manual's spells): it tries each undead in its area,
  one at a time; by the undead's hit dice and the cleric's level, a d20 turns it
  (it flees for 3d4 rounds), or it is turned or destroyed with no roll, or
  can't be turned at all. A cleric who fails against an undead can't try it
  again that fight. *Without the mod:* each success destroyed, and a failure
  could be tried again and again.
- **Resting** heals by the priests' spells left and a night's rest, not to
  full: [Resting](#resting).
- **Mirror Image**'s images take each hit, and each foe's spell aimed at one
  creature, three times in four (Reflected Image's half the time), the image
  vanishing and the blow or spell lost; your own side's spells always get
  through. *Without the mod:* the images stopped no weapon blow, and took the
  caster's own Armor.
- **Armor** uses a charge for each damaging hit. *Without the mod:* two for
  each hit, and one for any spell landing on its wearer, a friend's Bless too.
- **Share Strength** ends on its receiver when the power ends. *Without the
  mod:* the receiver kept the strength.
- **Dispel Magic** only dispels. *Without the mod:* the preserver's also stopped
  everyone it caught casting spells, your own party too.
- **Negative Plane Protection** gives a save against an undead's draining
  touch; saved, the touch is stopped and the undead takes 2d6. *Without the
  mod:* it never stopped anything.
- **Cloak of Bravery** gives +4 on saves against fear spells. *Without the
  mod:* the bonus never applied.
- **Absorb Disease** takes the disease only. *Without the mod:* it gave the
  psionicist STR too.
- **Cause Serious and Critical Wounds** do 2d8+1 and 3d8+3, as the Cure spells
  heal (Light: 1d8 both ways). *Without the mod:* 2d9 and 3d9.
- **Enlarge** adds 10% a caster level to the weapon's dice only, rounded up;
  STR and magic are added after. *Without the mod:* to the whole melee damage,
  STR included.
- Shillelagh, Flame Blade and Spiritual Hammer need an empty hand. With weapon
  specialization on, a spec counts with them as with a club, a long sword and a
  mace.
- Six **new wizard spells**, learnt like any other:
  - **Cat's Grace** (2nd level, on a party member): DEX up by a die that
    depends on the class (a rogue 1d8; a wizard, warrior or psionicist 1d6; a
    priest 1d4; a multiclass character's best; at most 24) for an hour of game
    time a caster level, which betters AC, initiative, thief skills and
    dodging. *Without the manual's spells:* DEX + 1d6 for anyone.
  - **Erdlu Claw** (1st level, on a party member): talons for 5 rounds a
    caster level. Unarmed attacks, a thri-kreen's claws but not its bite, do
    1d6+1 where that's better, are +1 to hit and count as a +1 magical edged
    weapon (a thri-kreen's claws and bite cut even without it). With Body Weaponry or
    Animal Affinity, their dice are +1 (2d4+1, 1d10+1); those powers, as the
    game has them, change only the first of a creature's natural attacks.
  - **Fogbolt** (1st level): a dark grey bolt of clinging fog at one creature
    in a clear line, for 2d4 rounds unless it saves: −3 to its attacks, +2 to
    attacks on it.
  - **Reflected Image** (1st level, on the caster): one image, which a hit or a
    foe's spell strikes half the time instead of the caster, and which then
    vanishes (Mirror Image's images are struck three times in four). It and
    Mirror Image replace each other; Dispel Magic ends it.
  - **Spook** (1st level): one creature flees in fear for 3 rounds unless it
    saves, at −1 for every 2 caster levels (at most −6). Undead aren't
    affected; magic resistance applies, and Cloak of Bravery gives +4 against
    it.
  - **Friends** (1st level, on the caster): CHA + 2d4 (at most 25) for 1d4
    rounds and 1 a caster level, for better prices when the party leader casts
    it. Casting it again replaces it; a CHA of 25 already is left as it is.

### Spell lists

**Preservers' spells** (with the mod's six new ones):

| Level | Spells |
|---|---|
| 1 | Armor, Burning Hands, Charm Person, Chill Touch, Color Spray, Enlarge, Erdlu Claw, Fogbolt, Friends, Gaze Reflection, Grease, Magic Missile, Reflected Image, Shield, Shocking Grasp, Spook, Wall of Fog |
| 2 | Acid Arrow, Blur, Cat's Grace, Detect Invisibility, Flaming Sphere, Fog Cloud, Glitterdust, Invisibility, Mirror Image, Protection from Paralysis, Scare, Stinking Cloud, Strength, Web |
| 3 | Blink, Dispel Magic, Fireball, Flame Arrow, Haste, Hold Person, Hold Undead, Lightning Bolt, Minor Malison, Minute Meteors, Monster Summoning I, Protection from Normal Missiles, Slow, Spirit Armor, Vampiric Touch |
| 4 | Black Tentacles, Charm Monster, Confusion, Fear, Fire Shield, Ice Storm, Improved Invisibility, Minor Globe of Invulnerability, Minor Spell Turning, Monster Summoning II, Rainbow Pattern, Solid Fog, Stoneskin, Turn Pebble to Boulder, Wall of Fire, Wall of Ice |
| 5 | Chaos, Cloudkill, Cone of Cold, Conjure Elemental, Dismissal, Domination, Feeblemind, Hold Monster, Lower Resistance to Magic, Monster Summoning III, Summon Shadow, Wall of Force, Wall of Stone |

**Priests' spells.** Every cleric, druid and ranger has the common ones of the
levels it can cast; druids alone (and a cleric with the Healer kit) have the
common 4th and 5th-level ones; and each has its own element's. A Healer or
Lifebinder never knows the harming ones: the Cause spells, Cause Disease,
Poison, Slay Living and Harm.

| Level | Every priest | Druids only |
|---|---|---|
| 1 | Bless, Cause Fear, Cause Light Wounds, Cure Light Wounds, Curse, Entangle, Invisibility to Undead, Protection from Evil, Remove Fear, Shillelagh | |
| 2 | Aid, Barkskin, Charm Person or Mammal, Find Traps, Hold Person, Spiritual Hammer | |
| 3 | Bestow Curse, Cause Blindness or Deafness, Cause Disease, Cure Blindness or Deafness, Cure Disease, Dispel Magic, Magical Vestments, Negative Plane Protection, Prayer, Remove Curse, Remove Paralysis | |
| 4 | | Abjure, Cause Serious Wounds, Cloak of Bravery, Cloak of Fear, Cure Serious Wounds, Free Action, Neutralize Poison, Poison, Protection from Evil 10' Radius |
| 5 | | Cause Critical Wounds, Cure Critical Wounds, Dispel Evil, Raise Dead, Slay Living |
| 6 | | Harm, Heal, Restore Youth |

| Level | Air | Earth | Fire | Water |
|---|---|---|---|---|
| 1 | | Magical Stone | | |
| 2 | Dust Devil | Dust Devil | Flame Blade, Resist Cold, Resist Fire | |
| 3 | Conjure Lesser Air Elemental, Summon Insects | Conjure Lesser Earth Elemental | Conjure Lesser Fire Elemental, Protection from Fire | Conjure Lesser Water Elemental |
| 4 | Dust Cloud, Protection from Lightning | Condense, Dust Cloud | Focus Heat, Produce Fire | Blood Flow, Dehydrate |
| 5 | Conjure Air Elemental, Deflection, Insect Plague | Conjure Earth Elemental, Ironskin, Quicksand | Conjure Fire Elemental, Flame Strike, Wall of Fire | Conjure Water Elemental, Quicksand |
| 6 | Blade Barrier, Whirlwind | Heartseeker, Wall of Thorns | Fire Seeds, Sunstroke | Heartseeker, Water of Life |

An Elementalist has its second sphere's column too.

**The 6th-level spells** are the mod's, for priests of 11th level and up (with
AD&D's class tables and the **New spells** switch on):

- **Heal** (touch): every wound healed, disease and blindness cured (and,
  with the manual's spells, Feeblemind).
- **Harm** (touch): the creature is left 1d4 hit points, a helpless one too;
  no save. It also leaves the creature Diseased, as in AD&D, which here only
  keeps a STR lowered by something else from coming back.
- **Restore Youth** (touch; the mod's, the reverse of AD&D's Age Creature):
  takes back a year of magical aging (from Haste) a caster level, never below
  the creature's true age (its starting age and the game's years). It must
  survive a system shock first; one with no magical years rolls nothing. It
  needs the **Ages and magical aging** rule, and does nothing to a monster.
- **Blade Barrier** and **Wall of Thorns**: a wall that does 8d8 (blades,
  edged, a save for none) or 8 plus the creature's AC (thorns, no save: the
  less armour, the worse; a party member's AC as the game last worked it out
  when something attacked them, anyone else's from armour, shield, DEX and a
  gladiator's levels, not spells) to each creature in it or passing through:
  circling blades or a tangle of thorns. Any number can stand at once. Mind
  where you put it: it hurts your party too.
- **Sunstroke**: one creature collapses, helpless as Hold Person holds, for 2
  rounds a level unless it saves, and the heat burns it for 1d4 fire at the
  start of each round (a fire resistance counts), until the paralysis ends or
  is cured.
- **Fire Seeds**: four seeds of 2d8 burst together where you aim, one burst of
  8d8 rather than one by one, a save for half.
- **Heartseeker**: a spell of death, not an arrow: one creature saves against
  death or dies; if it saves, it takes half of 4d8, as from Slay Living.
- **Water of Life** (touch): the creature's wounds pass to the caster, who
  keeps at least 5 hit points.
- **Whirlwind**: a turning funnel of dust that stays where it is cast a round
  a caster level. At the start of each round, before anyone acts, and as it is
  cast, it does 2d8 crushing to each creature in it, a save for half; one that
  fails is swept off its feet and loses its turn (that round's if it hasn't
  acted yet, else the next), without being helpless. Walking into it does
  nothing until the next round starts. Nothing can be shot or cast through it.
  Keep your own people out of it: it strikes them too, and anyone knocked out
  in it.

### Status effects

| Effect | Does |
|---|---|
| Blessed / Cursed | +1 / −1 to hit (Bless also +1 on saves); they cancel each other |
| Hasted / Slowed | Hasted: double movement and attacks, +2 initiative; with ages on, a system shock roll and a year older. Slowed: half, loses every other turn, −4 to hit, AC 4 worse, −2 initiative |
| Paralyzed | no turns; fails every save; every blow hits it |
| Stuck (Grease, Web, Entangle and the like) | can't move; Free Action stops it |
| Tangled ([cahulaks](#cahulaks)) | loses its next turn: no movement, no attack |
| Nauseated ([a stinkpot](#stinkpots)) | −2 to hit |
| Afraid | runs; can't attack or cast |
| Charmed | fights for the caster |
| Confused | each turn: runs off, does nothing, fights for a side picked at random, or acts normally |
| Berserk | fights for a side picked at random; can't cast |
| Can't attack | can't attack or cast harmful spells |
| Blind | AC 4 worse, −2 initiative; can't cast spells that need sight |
| Acid | 2d4 a round |
| Poisoned | fatal if time passes out of a fight (resting, for one) before it wears off or is cured |
| Stoneskin, Mirror Image | each blow stopped, or image struck, uses a charge (an image takes a hit, or a foe's spell for one creature, three times in four) |
| Invisible | ends with an attack or a harmful spell (Improved Invisibility doesn't) |

### Resting

Use a **fire ring** (the Look pointer on it, out of a fight) to rest 8 hours.
The game then fills every member's spell slots and PSP, brings STR back (but
a diseased member's), and a cleric or druid of 5th level or more among those
Okay casts Cure Disease, Remove Curse and Remove Paralysis on everyone, a
druid of 7th or more Neutralize Poison too. Anyone still **Poisoned** when the
rest ends dies.

With **Resting as in AD&D** (a rule change, on by default), the rest heals as
AD&D's does:

1. **The priests' spells first.** Before the slots fill again, each priest who
   can cast spends the priest spells it has left on the party: Neutralize
   Poison on the Poisoned, Cure Blindness on the Blind, Cure Disease on the
   Diseased (when no cleric or druid of 5th level would cure it free), then
   Cure Light, Serious and Critical Wounds and Heal on the most wounded, the
   cure that fits what the night won't heal (Cure Light for a wound of 4 or
   more, Serious 10, Critical 16, Heal 30, else the smallest left). A priest
   casts only if it can (Okay, not feebleminded, paralysed, charmed or barred
   from spells). So a 4th-level slot kept back
   keeps a poisoned friend alive.
2. **Then psionicists' Cell Adjustment** (5 PSP each: 1d4 HP and a disease
   cured), on the Diseased, then the wounded, while their PSP last.
3. **A night's natural healing:** each member heals **3 hit points plus CON's
   hit point bonus** (its bonus a level, [hit points](#hit-points): a warrior's
   in full, +1 at CON 15 up to +7, anyone else's at most +2), up to its most. CON 20 or more also regenerates through the
   8 hours.

Slots and PSP still fill to the most, STR still comes back, the 8 hours pass,
and a script's full rest is as the game has it.

So rest more than once to heal a badly hurt party with no priest, or keep cure
spells back for the night. The dice log shows each: `At rest: Seneca casts Cure
Light Wounds on Gerakis (1st-level slots: 1 left)` and `Gerakis rests 8 hours:
+3, +2 (CON 16) = +5, now 35/40 HP`.

## Psionics

A power costs PSP to use, and one kept up costs more at the start of each
round; when the PSP run short, it drops. Against a psionic attack, a character
raises the best defence mode it knows and can pay for, by itself.

| Power | Discipline | PSP to use | Each round kept up |
|---|---|---|---|
| Detonate | psychokinesis | 18 | |
| Disintegrate | psychokinesis | 40 | |
| Project Force | psychokinesis | 10 | |
| Ballistic Attack | psychokinesis | 5 | |
| Control Body | psychokinesis | 8 | |
| Inertial Barrier | psychokinesis | 7 | 5 |
| Animal Affinity | psychometabolism | 15 | 4 |
| Energy Containment | psychometabolism | 10 | |
| Life Draining | psychometabolism | 11 | |
| Absorb Disease | psychometabolism | 12 | |
| Adrenalin Control | psychometabolism | 8 | 4 |
| Biofeedback | psychometabolism | 6 | 3 |
| Body Weaponry | psychometabolism | 9 | 4 |
| Cell Adjustment | psychometabolism | 5 | |
| Displacement | psychometabolism | 6 | 3 |
| Enhanced Strength | psychometabolism | (24 − STR) × 2 | 8 |
| Flesh Armor | psychometabolism | 8 | 4 |
| Graft Weapon | psychometabolism | 10 | 1 |
| Lend Health | psychometabolism | 4 | |
| Share Strength | psychometabolism | 6 | 2 |
| Domination | telepathy | 3, 8, 13 or 18 by the target's level | |
| Mass Domination | telepathy | 3, 8, 13 or 18 by the target's level | |
| Psychic Crush (attack) | telepathy | 7 | |
| Superior Invisibility | telepathy | 5 | 5 |
| Tower of Iron Will (defence) | telepathy | 6 | |
| Ego Whip (attack) | telepathy | 4 | |
| Id Insinuation (attack) | telepathy | 5 | |
| Intellect Fortress (defence) | telepathy | 4 | |
| Mental Barrier (defence) | telepathy | 3 | |
| Mind Bar | telepathy | 6 | 4 |
| Mind Blank (defence) | telepathy | 0 | |
| Psionic Blast (attack) | telepathy | 10 | |
| Synaptic Static | telepathy | 15 | 10 |
| Thought Shield (defence) | telepathy | 1 | |

Psionic Blast leaves a victim that fails its save at a fifth of its hit
points; the wounds are imagined, so a party member gets them back as the fight
ends, and until then a blow that would kill it only knocks it out (it wakes
with them). Mind Bar gives 75% magic resistance to mind-affecting spells. Body Weaponry
makes unarmed blows 2d4, and Animal Affinity at least 1d10: a thri-kreen's
claws, not its bite. The Mind Bender, Kineticist and Titan Mind
[kits](#kits) change some costs.

## Equipment

**Weapons.** Most are wood, bone, stone or obsidian; plain ones of those hit
worse than metal ([hitting](#hitting)), and can break (1 chance in 160 after a
hit; not clubs or quarterstaffs). Weapons of every type come in several
materials, the short sword among them.

| Weapon | Damage | Against a large foe | Can backstab |
|---|---|---|---|
| Dagger | 1d4 | 1d3 | yes |
| Short sword | 1d6 | 1d8 | yes |
| Long sword | 1d8 | 1d12 | yes |
| Club | 1d6 | 1d3 | yes |
| Quarterstaff (two-handed) | 1d6 | 1d6 | yes |
| Axe | 1d8 | 1d10 | bone and obsidian ones (not metal) |
| Pick | 1d6+1 | 2d4 | yes |
| Great axe (two-handed) | 1d10 | 2d8 | no |
| Mace | 1d6+1 | 1d6 | no |
| Cahulaks (both hands) | 1d6 | 1d6 | no |
| Gythka (two-handed) | 2d4 | 1d10 | no |
| Polearm (two-handed) | 1d10 | 2d6 | no |
| Chatkcha | 1d6+2 | 1d4+2 | no: missiles never backstab |
| Bow (two-handed) | 1d8: the bow's own dice, whatever the arrows | the same | no |
| Sling | 1d4: the sling's own | the same | no |
| Staff sling (two-handed) | 1d3: a stinkpot | the same | no |

A half-giant holds a two-handed weapon in one hand, with a shield or a light
weapon in the other.

### Size

Against a **large** target (a half-giant, a large monster such as the
Mountain Stalker, anyone Enlarged) a weapon rolls AD&D's dice for large
targets, the table's third column; its plus, STR and specialization are added
as before. Shillelagh does 1d6+1 against smaller foes and 2d4 against large
ones, Spiritual Hammer 1d4+1 and 1d4. A weapon's item box shows both
(`1D8-1/1D12-1`); the inventory and View Character show the first. Hold Person
and Charm Person don't work on a large target ([how spells
work](#how-spells-work)). [The creatures' table](CREATURES.md) (spoilers) gives
every creature's size. *Without the mod:* the game keeps no sizes.

### Cahulaks

Cahulaks are two bladed heads on a rope, one in each hand. Their wielder
attacks one more time a round, with the off head, at the [two-weapon](#two-weapons)
penalties: −2 for the main head and −4 for the off, DEX's adjustment added but
never making it a bonus (a ranger in light armour has none, a Justifier in any, a Ghetto Fighter 0
and −2). A hit that does damage **tangles** a man-sized or smaller foe unless
it saves against petrification: it loses its next turn. Half-giants, large monsters,
anyone Enlarged, the bodiless (elementals, slimes, swarms, shadows) and a few
other beasts can't be tangled ([the creatures' table](CREATURES.md) (spoilers)
marks each). Twin-blades fight with them as with any two weapons, with no
penalty in light armour; Battle Dancers and Brutes can't use them.
*Without the mod:* a plain two-handed 1d6 weapon.

### Stinkpots

The staff sling throws clay pots of burning sulphur: 1d3 damage
against any size, and a target hit saves against poison or is **nauseated**
for 1d3+1 rounds, −2 on its attack rolls. Undead, and anything immune to
poison, shrug it off. *Without the mod:* the staff sling shot for 1d4, nothing
more.

### Polearm reach

A polearm held with no other weapon in the hands (a shield,
which only a half-giant can hold beside it, is fine; a bow in the missile slot
too) strikes a foe two squares away as well as an adjacent one: two squares
straight, or two across and one along, not two diagonally. The attack pointer
shows the sword over such a foe; it reaches over a creature in between, not
through a wall. Foes with polearms have the reach too. With a bow in the
missile slot, a click on a foe two squares away swings the polearm; from three
on, the bow shoots. *Without the mod:* a polearm strikes only an adjacent foe.

### Magic weapons by class

The magic weapons each class can wield, by the rules in [what each class may
use](#what-each-class-may-use). A character of several classes may wield those
any of its classes may, less what any class's limits forbid (a cleric's sphere,
a psionicist's weapons). Those the mod adds or changes are marked \* ([new
items](#new-items) says what they are).

**Every magic weapon,** by weapon spec: long swords Dragonsbane +4, Swiftbite +2, El's Drinker +2,
Dark Flame +2, Draketooth +1, Hornblade +1, Bloodwrath +1; short swords
Greenbright\* +2, Searing Blade\* +2, Shadowseeker\* +1, Mindshard\* +1, Stillwater\* +1; daggers Dag's Dagger +3,
Terror Blade +2, Galefang\* +2, Nightsliver\* +2, Hayneedle\* +1; axes Glasshewer\* +2, Drakejaw\*
+1, Soulcrusher +1, Axe +1; great axes Great Axe +3, Headsman\* +2; gythkas Gythka +3, Gythka +2\*,
Kreenfang\* +1; polearms Linebreaker\* +2, Polearm +1, Thornwall\* +1; maces Mace +2, Blackmace +1;
quarterstaffs Quarterstaff +2, Balk's Staff +1, Parting Staff +1; club Gutterknot\* +1; pick
Deepbiter\* +1; cahulaks Ironwhirl\* +2, Cahulaks +2\*, Emberlash\* +1, Cahulaks +1\*; bows Bow +2,
Phrain's Bow +1, Dunesong\* +1; slings Sling +2, Sling +1; staff sling Windlash\* +1; chatkchas
Skycutter\* +2, Chatkcha +1.

| Class | Magic weapons | Its kits |
|---|---|---|
| Fighter | every one | **Ravager:** none of the bows, slings, Windlash\*, chatkchas or Dag's Dagger (thrown) |
| Gladiator | every one | **Twin-blade:** none of the two-handed ones (great axes, gythkas, polearms, quarterstaffs, bows, staff sling), but the cahulaks, a blade in each hand. **Brute:** in melee only Great Axe +3, Headsman\*, the gythkas, the polearms and the quarterstaffs (not the cahulaks); any missile weapon |
| Ranger | every one | **Seeker:** only its sphere's, bows too: air, the daggers, the cahulaks, bows, slings, Windlash\*, the chatkchas; earth, the metal, obsidian, stone and wooden ones (wooden bows; no bone, no slings); fire, the obsidian ones alone (no bow); water, the bone and wooden ones. It has no ranger's expertise with the bow either, unless the bow is its weapon spec |
| Thief | every one | **Shinobi:** only Greenbright\*, Searing Blade\*, Shadowseeker\*, Mindshard\*, Stillwater\*, Dag's Dagger, Terror Blade, Galefang\*, Nightsliver\*, Hayneedle\*, the quarterstaffs, bows, slings, Windlash\* and the chatkchas |
| Preserver | Hornblade +1 (a bone long sword the game lets preservers use), Dag's Dagger +3, Terror Blade +2, Galefang\* +2, Nightsliver\* +2, Hayneedle\* +1, Quarterstaff +2, Balk's Staff +1, Parting Staff +1, Sling +2, Sling +1, Windlash\* +1 | **Battle Mage:** also those of its chosen weapon spec |
| Cleric of air | every dagger (Dag's Dagger +3, Terror Blade +2, Galefang\* +2, Nightsliver\* +2, Hayneedle\* +1), Bow +2, Phrain's Bow +1, Dunesong\* +1, Sling +2, Sling +1, Windlash\* +1, Skycutter\* +2, Chatkcha +1, Ironwhirl\* +2, Cahulaks +2\*, Emberlash\* +1, Cahulaks +1\* | **Elementalist:** its second sphere's too |
| Cleric of earth | Dragonsbane +4, El's Drinker +2, Dark Flame +2, Bloodwrath +1, Greenbright\* +2, Searing Blade\* +2, Shadowseeker\* +1, Mindshard\* +1, Dag's Dagger +3, Terror Blade +2, Galefang\* +2, Nightsliver\* +2, Glasshewer\* +2, Soulcrusher +1, Axe +1, Great Axe +3, Headsman\* +2, Linebreaker\* +2, Blackmace +1, the three quarterstaffs, Gutterknot\* +1, Deepbiter\* +1, Ironwhirl\* +2, Emberlash\* +1, Bow +2, Phrain's Bow +1, Dunesong\* +1, Skycutter\* +2, Chatkcha +1 | **Elementalist:** its second sphere's too |
| Cleric of fire | Dark Flame +2, Bloodwrath +1, Searing Blade\* +2, Mindshard\* +1, Nightsliver\* +2, Glasshewer\* +2, Blackmace +1, Emberlash\* +1, Skycutter\* +2, Chatkcha +1 (not the obsidian Terror Blade: the game's own lists keep it from fire clerics) | **Elementalist:** its second sphere's too |
| Cleric of water | Stillwater\* +1, Hayneedle\* +1, Drakejaw\* +1, Gythka +3, Gythka +2\*, Kreenfang\* +1, Polearm +1, Thornwall\* +1, Mace +2, the three quarterstaffs, Gutterknot\* +1, Cahulaks +2\*, Cahulaks +1\*, Bow +2, Phrain's Bow +1, Dunesong\* +1 (not the bone Swiftbite, Draketooth or Hornblade: the game's own lists keep them from water clerics) | **Elementalist:** its second sphere's too |
| Druid | every one but Great Axe +3 and Headsman\* | **Grove Warden:** only those its sphere allows, as a cleric of that sphere. **Lifebinder:** only Mace +2, Blackmace +1, the three quarterstaffs, Gutterknot\* +1, the slings and Windlash\* |
| Psionicist | Searing Blade\* +2, Mindshard\* +1, Stillwater\* +1, Dag's Dagger +3, Terror Blade +2, Galefang\* +2, Nightsliver\* +2, Hayneedle\* +1, Gutterknot\* +1, Bow +2, Phrain's Bow +1, Dunesong\* +1, Skycutter\* +2, Chatkcha +1; with a fighter, gladiator, ranger or thief class, also Greenbright\* +2, Shadowseeker\* +1, Mace +2, Blackmace +1, Sling +2 and Sling +1, its other class's lists allowing them; with a cleric class, only those its sphere allows too (the Searing Blade and Mindshard with fire or earth, Stillwater with water) | — |
| Cleric with a fighter class | its sphere's, as a cleric of that sphere, and those the game's lists keep from that sphere's clerics alone (the Terror Blade with fire; Swiftbite, Draketooth and Hornblade with water) | **Battle Dancer** (an elf cleric/fighter): only the long swords and bows, whatever its sphere: Dragonsbane +4, Swiftbite +2, El's Drinker +2, Dark Flame +2, Draketooth +1, Hornblade +1, Bloodwrath +1, Bow +2, Phrain's Bow +1, Dunesong\* +1 |

### Armour

Armour is worn in pieces (chest, arms, legs, a helm), each lowering AC by
its own amount, and a shield and DEX lower it more (but not against an attack
[from behind](#from-behind-and-backstabs)). **Helms give AC 1**. *Without
the mod:* helms give no AC. The inventory screen's AC line counts them all; the
Loader's Characters tab shows the AC of the last attack and what made it.

### Protection

Rings and cloaks of protection give +1 AC and +1 on every
save, by AD&D's rules: two rings don't add up (the better counts, the left
hand's if they're equal); a ring gives no AC with magical armour (its saves
still count); a cloak does nothing with magical or metal armour or a shield
(leather, bone and plain helms are fine), and still adds to a ring. A cloak isn't armour: any class may wear one, druids too.
**Bracers of Defense** give their AC (6, 5, 4 or 2), and the mod's two
**robes** their plus, only with no armour worn, and a preserver casts in
either. These are rare finds.

### Acid

Some monsters' acid or corroding touch can destroy worn armour or a
held weapon. Each item gets a saving throw by its material: wood 8, bone 11,
stone and obsidian 5, metal 13, leather 10, cloth 12, less its plus and 1
more for a magical power (any item uses the game's own number where that's
easier). At most one piece of armour is lost to a hit. *Without the mod:* plain
armour is destroyed outright.

### New items

The mod adds items the game never had, or never placed: here is what each
is, not where it is ([Items](ITEMS.md) lists that, with spoilers, for those
who want it). The magic weapons the mod adds or changes are marked \* in [magic weapons by
class](#magic-weapons-by-class).

**Mundane:**

| Item | What it is |
|---|---|
| Bone, obsidian and metal short swords | 1d6; the game has no short sword |
| Bone and obsidian axes | 1d8 |
| Bone, obsidian and metal great axes | 1d10, two-handed |
| Bone and metal daggers | 1d4; the bone one is the only dagger a water cleric can use |
| Obsidian and metal maces | 1d6+1 |
| Metal pick, metal polearm, metal cahulaks | the game's, in metal |
| Obsidian cahulaks | the game's cahulaks, in obsidian: earth, fire and air clerics may use them |
| Bone Scale Arm Armor, Leg Armor and Bone Helm | the rest of the bone scale set whose chest piece the game has |
| Helm | a leather helm |

New characters with weapon specialization start with a plain weapon of their
chosen type, often one of these.

**Magic weapons** (each class's list in [The classes](#the-classes) says who can wield them):

| Item | What it is |
|---|---|
| Greenbright | metal short sword +2 |
| Searing Blade | obsidian short sword +2 whose blade burns what it hits: 2d6 fire damage, a save for half |
| Shadowseeker | metal short sword +1: its wielder sees the invisible |
| Mindshard | obsidian short sword +1 |
| Stillwater | bone short sword +1 |
| Galefang | metal dagger +2 |
| Nightsliver | obsidian dagger +2 |
| Hayneedle | bone dagger +1 |
| Glasshewer | obsidian axe +2 |
| Drakejaw | bone axe +1 |
| Headsman | metal great axe +2 |
| Kreenfang | bone gythka +1, two-handed |
| Linebreaker | metal polearm +2 |
| Thornwall | bone polearm +1 |
| Gutterknot | club +1 (the game has no magic club) |
| Deepbiter | stone pick +1 |
| Cahulaks +1 | bone cahulaks +1 |
| Emberlash | obsidian cahulaks +1 |
| Ironwhirl | metal cahulaks +2 |
| Windlash | staff sling +1 |
| Dunesong | bow +1 |
| Skycutter | chatkcha +2 |

The game's own Gythka +1 and Cahulaks +1 are a Gythka +2 and a Cahulaks +2
with the mod (the cahulaks still cast Cause Light Wounds on a hit). The game's
own Polearm +1, which it never placed, can be found now.

**Other magic items:**

| Item | What it does |
|---|---|
| Ring of Protection +1 (two), Cloak of Protection +1 | +1 AC and +1 on every save ([protection](#protection)) |
| Bracers of Defense (four pairs: AC 6, 5, 4 and 2) | their AC with no armour worn; a preserver casts in them |
| Ashen Robe | worn on the chest by preservers, psionicists and druids, not armour: AC 1 better with no armour, +1 on saves against spells |
| Veiled Robe, a robe of the Veiled Alliance | the same, AC 2 better, +1 on every save, and a wizard spell slot more at spell levels 1, 2 and 3 |
| Inixhide | leather chest armour +1 |
| Gutterward | a wooden shield +1: AC 2 better in a hand |
| Ironbulwark | a metal shield +3, the game's only metal shield: AC 4 better in a hand |
| Warden's Chest, Arms, Legs and Helm | plate armour +1 in four pieces: the chest 4 points of AC better, the arms and legs 3 each, the helm 2 (a helm's AC 1, +1): 12 better as a set, so AC 10 becomes −2 before DEX; the chest gives Resist Fire, the helm Cloak of Bravery, while worn |
| Arrowbane | a circlet: Protection from Normal Missiles while worn; not armour |
| Girdle of Back Defense | a belt: no enemy gets the bonuses for attacking its wearer from behind, and no backstab |
| Golden Girdle of Urnst | a belt: AC 3 better against long and short swords |
| Amulet of Magic Resistance | 15% magic resistance, added to any the wearer has |
| Sunking Crown | a crown: Protection from Evil while worn; not armour |
| Cloak of Elvenkind, Boots of Elvenkind | help a thief or ranger [hide and move silently](#hiding-in-shadows); thieves and rangers only |
| Boots of Speed | in a fight, double movement and AC 2 better while the wearer can move (not Stuck, Paralyzed or Slowed); anyone may wear them |
| Tome of Understanding | read from the inventory as a scroll: +1 WIS for good (at most 25) |
| Kalzith's six scrolls | Shield, Burning Hands, Blur, Cat's Grace (with the new spells on), Lightning Bolt and Haste, sold by Kalzith: spells the game has no scroll of |
| Defilers' scrolls | a scroll of any preserver spell (the game's 69, and the new ones with the new spells on), carried by a defiler 1 time in 20 and found on its body; the arena's defiler in the champions' bout always has one, of Fogbolt, Spook or Reflected Image (of the game's own spells with the new spells off) |
| Chill, Shocking and Vampiric Arrows | made only by a [Spellarcher](#multiclass-kits) from its own spells, one a slot; they last until shot, and only a Spellarcher carries them (their item box's INFO lists the SPELLARCHERS:) |
| Fine Bow | a Spellarcher's own bow from the start: +1 to hit, not magic |

The game's own Grey's Scale arm and leg armour is AC 3 each with the mod (2
without).

## Quality of life

**On the game's screens** the mod shows what the game kept hidden: every roll in the combat log
(**L** on the map), names over figures (a spell cast, "Miss", "Armor: 7 left", the arrows left),
THAC0, all five saves and thief skills on the inventory and View Character screens, spell slots on
the USE screen, a monster's hit points and defences in the Look box, charges and to-hit in item
boxes, and the kit, weapon specs and spells' uses left on the Effects screen. Each is in [the
features page](FEATURES.md#always-on).

**Keys** (always on):

| Key | What it does |
|---|---|
| **S** (selling) | On a shop's screen, **S** sells the plain gear (weapons, armour, shields, clothing: no plus, no magic) in the backpack of the member on show, at the shop's prices; worn and held things, ammunition, metal, magic, keys, scrolls, food and gems stay. *Without the mod:* one thing at a time. |
| **T** (looting) | With a body's (or a chest's) window open, **T** puts everything in it into the party's backpacks, and **Shift+T** everything but plain weapons; what doesn't fit stays. *Without the mod:* a click to take each thing and another to put it down. |
| **M**, **U** and **I** | **M** on the map opens the overhead map (the game's **O**), and **M** again closes it. **U** and **I** close the USE and inventory screens when pressed again (and still switch from one to the other). *Without the mod:* only **O** opens the map, and **U** and **I** only switch. |

The mod's other controls are always on too: Tab and Enter to choose and attack an enemy (the red
ring under it, and the chance to hit it shown before the swing, are on the Options tab), the squares in reach marked on a party member's turn and **Alt** held to ring and name
everything in view that can be used (switches in the tab's **In the game** section), scrolling with the mouse wheel, the whole party in
view, the view in fights, the pointer, and spells on the Effects screen ([controls](FEATURES.md#controls)). Quick save and
quick load with **F5** and **F9**, and autosave, have switches under **Saves** on the Options tab.

**Saves and characters:** 40 saves, four pages of ten (**PAGE 1** to **PAGE 4**, or **PgUp** and
**PgDn**), a fifth page, **QUICK**, for the quick saves (**F5**; **F9** loads) and the autosaves
the game makes on coming into another area and after a fight, the last five of each kept ([quick
save, quick load and autosave](FEATURES.md#quick-save-quick-load-and-autosave)), and 29 characters
in the roster ([more saves and characters](FEATURES.md#saves)).

**Graphics** (figures in what they wear, shadows, dust, see-through hiders) are in
[Features: graphics](FEATURES.md#graphics), and **steady pace** in [Features: game
speed](FEATURES.md#game-speed); scanlines or hard-edged pixels for the game window, and another
MIDI device for the music, in [Features: picture and music](FEATURES.md#picture-and-music).
**Running the game** (the game window's size, crash and freeze
reports) and **the Loader's window** (the dice log, the characters' sheets, the dialogue, the
[journal](README.md#the-journal-tab) that keeps what was said and every reward, follows your
saves and lists your quests, open and finished, without naming one you haven't been given, every
spell's dice) are in the README: [running it](README.md#running-it-windows), [the Loader's
window](README.md#the-loaders-window) and [reports](README.md#crash-freeze-and-item-reports); [the
dice log, line by line](DICE-LOG.md) says what each of its lines means.

## Worth knowing

- **Cure poison before resting.** A character still Poisoned when time passes
  out of a fight dies (with Resting as in AD&D, a priest's Neutralize Poison left
  unspent is cast at the rest: [resting](#resting)).
- **Area spells catch the caster and the party.** Aim fireballs and clouds
  away from your own.
- **Act before you are hit if you mean to cast** ([why](#initiative)).
- **Watch the quiver.** After a party archer's shot the arrows left float over it ("Arrows: 17
  left", "Out of arrows"); one that runs dry in the middle of its shots keeps its turn, to walk,
  fight hand to hand or end it ([names over figures](FEATURES.md#names-over-figures)).
- **Someone Out Cold takes the most a spell's dice can do,** with no save.
- **Two weapons cost to-hit** unless your DEX is high or you are a ranger,
  Twin-blade or Battle Dancer in light armour, and the off hand attacks only
  once a round.
- **A held or Out Cold foe is hit by every blow,** for normal damage.
- **A warrior's weapon specs matter:** outside them it attacks once a round
  until 7th level.
- **Multiclass preservers take off their armour to cast** (a helm counts),
  and multiclass thieves to use their thief skills (light armour is fine).
- **Thieves hide with no enemy beside them** when their turn comes; step away
  first. Daylight halves their chance, and rangers' indoors.
- **Plain wood, bone, stone and obsidian weapons can break** (clubs and
  quarterstaffs can't); magic ones never do.
- **Spell damage stops growing at caster level 10.**
- **Wait** puts a character later in the round.
- **Ready a missile weapon and a melee weapon:** the game uses whichever fits
  the target's distance.
- **The look pointer pauses the game.** While it is up, no time passes: no one
  moves, and no one comes calling. Switch back to the walk arrow to let time run.
- **The people you fight wear their armour from the start.** Without the mod
  they put it on only when they first acted in a fight, so an opening blow or
  a backstab before then met AC 10; now it meets their armour.

## Glossary

| Term | Meaning |
|---|---|
| **d20, 2d4, 1d6+1** | Dice: 2d4 is two four-sided dice added up; 1d6+1 a six-sided die plus 1. |
| **AC** | Armour class: how hard a character is to hit. Lower is better (10 is no armour; it can go below 0). |
| **THAC0** | "To hit AC 0": the d20 a character needs to hit AC 0. The roll needed against a target is THAC0 less its AC (THAC0 15 against AC 3 needs 12). Lower is better. |
| **HP** | Hit points. At 0 a character is Out Cold, at −10 dead. |
| **PSP** | Psionic strength points, spent on psionic powers. |
| **XP** | Experience points, which bring new levels. |
| **Saving throw** (save) | A d20 to escape or lessen a spell or attack, needing the number of one of five kinds: **PPD** paralysis, poison and death; **RSW** rod, staff and wand; **PP** petrification and polymorph; **BW** breath weapon; **SP** spell. |
| **MR** | Magic resistance: a monster's percentage chance to shrug off a spell outright. |
| **REAC**, **DEF** | DEX's reaction adjustment (initiative, two weapons) and defensive adjustment (AC, dodging fire, cold and electricity). |
| **Prime requisite** | The score a class depends on (a fighter's STR; a ranger has three). At creation a score is raised to the class's minimum if the die gave less. |
| **Multiclass, dual class** | Two or three classes at once (any race but human); a human's change from one class to another. |
| **Kit** | A class's speciality, chosen at creation: something gained, something given up ([Kits](#kits)). |
| **Weapon spec** | A kind of weapon a warrior trains in, whatever its material: **specialized**, **mastery** and **grand mastery** for fighters, **expertise** for rangers ([weapon specialization](#weapon-specialization-and-attacks)). |
| **Backstab**, **from behind** | A thief's attack on an unaware target, damage multiplied; an attack from behind is +2 to hit, the target's DEX and shield not counting ([from behind](#from-behind-and-backstabs)). |
| **Caster level** | The level a spell is cast at, which sets its damage and duration. |
| **Spell slot** | One spell of a level that can be cast before resting. |
| **Sphere**, **discipline** | A cleric's element (air, earth, fire, water), which sets its spells and weapons; a psionicist's field of powers. |
| **Preserver**, **defiler** | Wizards who draw magic from the land: preservers without harming it (the class you play), defilers by killing it. |
| **Under the open sky** | An outdoor map, or open ground outside a city's buildings. |
| **Ceramic pieces** | Athas's money. |
| **The Loader** | The window that starts the game with the mod and shows the dice log and the party. |

## The Options tab at a glance

Every switch on the Loader's **Options** tab, in the tab's order and under its
sections, with the words the Loader gives it. They count in games started from
the Loader or its `.bat` files. **Restore defaults**, at the bottom of the tab,
sets every switch back to the default below; it leaves the Wake of the Ravager folder and the
settings [elsewhere in the Loader](#elsewhere-in-the-loader) as they are. Where a row lists
choices (separated by /), one of them is picked.

**Takes effect** says when a change counts:

- **at once**: in the game running, as soon as the box is ticked or unticked;
- **next start**: the next time the game is started (the Loader writes it into
  the game's copy as it starts it; the label says "from the next start");
- **new characters**: characters made from then on, while those already made
  keep what they have;
- **first visit**: from the next start, in an area the party hasn't visited
  yet. A saved game keeps what it already has (people met, items given); a new
  game has it all.

Most of the mod has no switch and is always on:

- **The rule changes** but three (hit dice, half-giants' two-handed weapons and helms' AC, which keep
  their switches): [class restrictions](FEATURES.md#class-restrictions), [multiclass hit
  points](FEATURES.md#multiclass-hit-points), [scores and hit points as
  rolled](FEATURES.md#scores-and-hit-points-as-rolled), [AD&D's class
  tables](FEATURES.md#adds-class-tables), [CON as in AD&D](FEATURES.md#con-as-in-add), [ages and
  magical aging](FEATURES.md#ages-and-magical-aging), [dual-classing as the manual has
  it](FEATURES.md#dual-classing-as-the-manual-has-it), [the level cap by XP](FEATURES.md#level-cap-by-xp),
  AD&D's [two-weapon](#two-weapons) penalties, [weapon traits](FEATURES.md#weapon-traits),
  [creature size](FEATURES.md#creature-size) (the footman's pick's 1d6+1 among it), [held
  targets](FEATURES.md#held-targets), [rings and cloaks of
  protection](FEATURES.md#rings-and-cloaks-of-protection), [items saving against
  acid](FEATURES.md#items-saving-against-acid), and all of the magic ones: [rangers' casting
  level](FEATURES.md#rangers-casting-level), [preservers' INT](FEATURES.md#preservers-int), [saving
  throws against spells](FEATURES.md#spells-saved-against-with-the-spell-save),
  [Enlarge](FEATURES.md#enlarge-multiplies-the-weapons-dice-only), [spells and psionics as the manual
  describes them](FEATURES.md#spells-and-psionics-as-the-manual-describes-them), [spells rolling to
  hit](FEATURES.md#spells-roll-to-hit) and [resting as in AD&D](FEATURES.md#resting-as-in-add).
- [Weapon specialization](FEATURES.md#weapon-specialization) and [STORE and
  RECALL](FEATURES.md#store-and-recall-on-the-creation-screen).
- [The combat log in the game](FEATURES.md#the-combat-log-in-the-game) (its level is a choice:
  below).
- [Shops as in AD&D](FEATURES.md#the-leaders-cha-at-shops), and all of [improved
  thieving](FEATURES.md#improved-thieving): thief skills from AD&D's table, hiding in shadows to
  backstab (and what a cloak, boots and belt add), picking pockets.
- [The graphics](FEATURES.md#graphics): elves' ears and half-elves' figures, Cilla as an elf, what
  the party wears, shadows, dust, see-through figures.
- [The controls](FEATURES.md#controls): choosing an enemy with Tab and Enter, scrolling the map, the
  view in fights, the pointer in scenes and where it starts, the whole party in view, spells on the
  Effects screen; and the keys **T** and **Shift+T** (looting), **S** (selling), **M**, **U** and **I**.
- What the game's own screens show ([always on](FEATURES.md#always-on)), the fixes to [the game's
  own bugs](GAME-BUGS.md), the [magic items' icons](FEATURES.md#magic-items-icons) and [spells on the
  ground](FEATURES.md#spells-on-the-ground), [40 saves and 29 characters](FEATURES.md#saves), and the
  picks at **DONE**: [preservers' first spells](FEATURES.md#preservers-first-spells) and [psionic
  powers](FEATURES.md#psionic-powers-at-creation).

A settings file from an older Loader with one of these unticked has it on all the same.
[Features](FEATURES.md) has them all.

**In the game**

| Loader label | Default | Takes effect | Details |
|---|---|---|---|
| The combat log in the game (L on the map shows and hides it): ... at the least: what came of each attack and spell / ... in short: each roll, what it needed and the damage / ... in detail, as in the log | in short | at once | [The combat log in the game](FEATURES.md#the-combat-log-in-the-game) |
| What hurts a monster (the Look box): Look at one in a fight for its hit points, AC, THAC0 and defences; closing the box shows the rest in a window | on | at once | [What hurts a monster](FEATURES.md#what-hurts-a-monster-the-look-box) |
| Names over figures: a spell's name over its caster, "Miss" over whoever an attack missed, a used charge ("Armor: 7 left") over its owner, and the arrows left over a party archer after each shot | on | at once | [Names over figures](FEATURES.md#names-over-figures) |
| A red ring on the ground in a fight: ... none / ... under the enemy chosen with Tab | under the enemy | at once | [Choosing an enemy](FEATURES.md#choosing-an-enemy-tab-enter-and-the-rings) |
| The chance to hit: with an enemy chosen with Tab, what the d20 must show to hit it and the chance, in the dice log and the combat log's header | on | at once | [The chance to hit before the swing](FEATURES.md#the-chance-to-hit-before-the-swing) |
| Squares in reach: in a fight, a small cross on each square the party member whose turn it is can still walk to | on | at once | [Squares in reach](FEATURES.md#squares-in-reach) |
| Showing what can be used: hold Alt on the map, out of a fight | on | at once | [Showing what can be used](FEATURES.md#showing-what-can-be-used-alt) |

**Rule changes**

| Loader label | Default | Takes effect | Details |
|---|---|---|---|
| Hit dice: the better of two, each die rolled twice at creation and at every level (every character) | on | at once | [Hit dice](FEATURES.md#hit-dice-the-better-of-two) |
| Half-giants' two-handed weapons: a half-giant wields one in one hand, a shield or a light weapon in the other | on | at once | [Half-giants' two-handed weapons](FEATURES.md#half-giants-two-handed-weapons) |
| Helms give AC 1 (the game's helms give none) | on | at once | [Helms give AC 1](FEATURES.md#helms-give-ac-1) |

**More character customization**

| Loader label | Default | Takes effect | Details |
|---|---|---|---|
| Kits: three for each class and some for multiclass characters, one a character, each giving something and costing something (chosen on the creation panel's KIT page, or after DUAL by a human with none) | on | new characters, and a human's DUAL | [Kits](FEATURES.md#kits); [every kit](KITS.md) |
| Fuller starting gear: new characters (and the game's own party) also get a weapon they can use, a sling, and leather armour where they may wear it | on | new characters (the game's own party: in a new game) | [Fuller starting gear](FEATURES.md#fuller-starting-gear) |

**New content** (the tab's note: "People, a quest, an arena bout and items:
from the next start, in places not yet visited. What a saved game already has
(people met, items given) stays in it. The new spells and defilers' scrolls: at
once.")

| Loader label | Default | Takes effect | Details |
|---|---|---|---|
| New spells: six for wizards (Cat's Grace, Erdlu Claw, Fogbolt, Reflected Image, Spook and Friends) and ten 6th-level priest spells (Heal, Harm, Blade Barrier...) | on | at once | [New wizard spells](FEATURES.md#new-wizard-spells); [6th-level priest spells](FEATURES.md#6th-level-priest-spells) |
| Kalzith, a defiler slave in the slave pens who sells arcane scrolls | on | first visit (the slave pens) | [Kalzith](FEATURES.md#kalzith) (spoilers) |
| Semyon in the slave pens after he leaves the arena, and breaking out with Scar | on | first visit (the slave pens) | [Semyon](FEATURES.md#semyon) (spoilers) |
| The cooked vulture: Dinos cooks it for the party (XP and a full rest) | on | next start | [The cooked vulture](FEATURES.md#the-cooked-vulture) (spoilers) |
| Defilers' scrolls: a defiler in a fight carries a scroll of a random preserver spell one time in 20, dropped where it dies | on | at once | [Defilers' scrolls](FEATURES.md#defilers-scrolls) (spoilers) |
| New items, magical and mundane: weapons, armour and other gear on the game's people, in its shops and chests, and the champions' arena bout after Scar's death | on | first visit (each item's area) | [New items](FEATURES.md#new-items) (spoilers); this guide's [New items](#new-items) |

**Game speed (from the next start)**

| Loader label | Default | Takes effect | Details |
|---|---|---|---|
| GOG's own (walking can be choppy with shadows and dust) / Faster: for an older PC (fewer pictures a second with the whole party in view) / Fastest: the whole party walks at full speed, nearly every picture shown (the default) | Fastest | next start | [Game speed](FEATURES.md#game-speed) |
| Steady pace: walking at full speed on the map whatever is drawn (a picture skipped rather than the party slowed) | on | next start | [Game speed](FEATURES.md#game-speed) |

**Picture and music (from the next start)**

| Loader label | Default | Takes effect | Details |
|---|---|---|---|
| Plain: every pixel of the game as a block (the default) / Scanlines: a black line under each row of the picture, as on an old monitor / TV: a dimmed line under each row of the picture, softer than scanlines / Sharp: hard-edged pixels at any size, the stretching left unsmoothed (DOSBox's OpenGL) | Plain | next start | [Picture and music](FEATURES.md#picture-and-music) |
| Music device | Windows' default | next start | a MIDI device of Windows' to play the game's music, by name: [Picture and music](FEATURES.md#picture-and-music) |

**Wake of the Ravager (optional)** and **Saves**

| Loader label | Default | Takes effect | Details |
|---|---|---|---|
| Choose its folder... | found by itself where it can be | next start | where Wake of the Ravager is installed, for the new priest spells' icons and pictures: [Requirements](README.md#requirements) |
| Quick save and quick load: on the map, F5 saves at once on the QUICK page of the save window, and F9 opens the load window there | on | at once | [Quick save, quick load and autosave](FEATURES.md#quick-save-quick-load-and-autosave) |
| Autosave: on coming into another area and after a fight, on the QUICK page of the save window | on | at once | [Quick save, quick load and autosave](FEATURES.md#quick-save-quick-load-and-autosave) |
| Open the folder | (a button) | | opens the Named saves folder: [Saves under their names](FEATURES.md#saves-under-their-names) |
| Put a save in a slot... | (a button) | | puts a named save back in one of the game's slots: [Saves under their names](FEATURES.md#saves-under-their-names) |

### Elsewhere in the Loader

The Loader's other settings are outside the Options tab, and **Restore defaults** leaves them be.

| Setting | Where | Default | Kept |
|---|---|---|---|
| **Game window**: Single (320x240), Double (640x480), Triple (960x720), Quadruple (1280x960) or Full screen | the top of the window | Triple (960x720) | remembered (`settings.json`); counts from the next start |
| **Text size**: **A+** and **A-** (or Ctrl +, Ctrl - and Ctrl 0), up to 2.5 times | the top of the window | normal | for this session: the Loader opens at the normal size |
| **Readable layout** | above the dice log | on | remembered (`settings.json`) |
| **Show details (the sums behind each roll)** | above the dice log | on | for this session |
| **Show unlabelled rolls** | above the dice log | off | for this session |
| **The game folder** | asked for at the first **Start the game** when it isn't in GOG's usual folders, or `--game-dir` ([troubleshooting](README.md#troubleshooting)) | found in GOG's usual folders | remembered (`settings.json`) |
| **Dark Sun Recompiled or DOSBox** | found in or beside this folder, or `--recompiled` and `--dosbox` ([Dark Sun Recompiled](README.md#dark-sun-recompiled)) | DOSBox, unless Recompiled is found | looked for at each start; a choice made with `--recompiled` or `--dosbox` remembered (`settings.json`) |
| **Speakers' names** | the Dialogue tab (**Name speaker...**, or a right-click on a name) | learned from the talk | remembered (`settings.json`) |
| **Which Options sections are open** | the Options tab (a section's header) | all closed | remembered (`settings.json`) |
| **Show** and **Only spells the party has a caster level for** | the Spells tab | all, off | for this session |
| **Keep a journal** | the Journal tab | on | remembered (`settings.json`) |

What each does: [the Loader's window](README.md#the-loaders-window) and [the dice
log](README.md#the-dice-log).
