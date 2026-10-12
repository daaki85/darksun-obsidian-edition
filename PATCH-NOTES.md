# Obsidian Edition: Patch Notes

*A Dark Sun: Shattered Lands mod · Current version 2.1.1 · Every change from the original game*

Obsidian Edition is a free mod for the GOG release of Dark Sun: Shattered Lands. It shows the rolls the game keeps hidden, brings its rules closer to AD&D 2nd Edition, adds kits, weapons, magic items and people to Athas, dresses the party in what they wear, and fixes bugs left over since 1993. Its companion window, Templar's Ledger, runs beside the game and logs every roll as it happens. Everything is switchable, the game's own files are never touched, and your saves stay where they are.

**Download:** https://github.com/daaki85/darksun-obsidian-edition/releases/latest

*These notes are also a web page, [`patch-notes.html`](patch-notes.html), with a button that copies them as Markdown for forums.*

## Templar's Ledger

- **[New]** A companion window that starts the game and runs beside it, laid out in the game's own colours.
- **[New]** **The dice log:** every attack, damage roll, saving throw, thief skill, initiative score and character creation roll as it happens, with the number it needed, the chance of success, and where every bonus came from.
- **[New]** **Characters:** each party member's sheet as View Character lays it out, plus THAC0 with each weapon, saves as the d20 needed right now, attacks a round, current AC and what it's made of, spell slots and thief skills.
- **[New]** **Spells:** every wizard spell, priest spell and psionic power's damage dice, saving throw, effect and duration, read from the running game.
- **[New]** **Dialogue:** everything said, with the speaker's portrait and name, and the reply you chose.
- **[New]** **Options:** every rule change and addition below has its own switch. All are on by default.

> *Developers' Notes: Shattered Lands rolls dice for everything and shows you almost none of it. Fireball victims kept saving and nobody knew why (the game doubles the d20 against fire). The Ledger started as a way to see those numbers. Once we could see them, we started fixing them.*

## In the Game's Screens

- **[New]** The inventory screen shows THAC0, all five saving throws, the THAC0 with each weapon, DEX's reaction and defence adjustments, and a thief's skills, in the game's own lettering.
- **[New]** View Character shows THAC0 and saves, and for a character of several classes, which class levels up next.
- **[New]** The USE screen shows the spell slots left at each spell level, and the most you get after resting.
- **[New]** In a fight, the Look box shows a monster's hit points, AC, THAC0, alignment, magic resistance and chief defence (NEEDS +1 WEAPON, IMM FIRE COLD...). Close it to read the rest.
- **[New]** Optionally, the game pauses after each turn in a fight to show that turn's rolls in its own dialogue window.
- **[New]** Item boxes show a wand's charges left, and the bonus a cloak, boots or belt gives to thief skills.
- **[New]** The Effects screen lists your kits and weapon specializations.

## Combat

**Weapon specialization**

- **[New]** Fighters specialize in one kind of weapon (+1 to hit, +2 damage, 3/2 attacks a round), with **mastery** at 5th level (+3, +3) and **grand mastery** at 9th (a larger damage die and one more attack).
- **[New]** Gladiators specialize in two kinds, a third at 6th level and a fourth at 9th. Rangers gain expertise with the bow and one other kind.
- **[Changed]** Warriors attack at AD&D's plain rate with weapons outside their specializations *(was 3/2 with any weapon)*. Specialists shoot missiles faster.

**Saving throws**

- **[Changed]** Spells are saved against with the spell save *(was petrification/polymorph for almost every spell)*.
- **[Changed]** Against fire, cold and electricity, DEX helps you dodge, from −5 to +6 *(was a doubled d20)*. Needing 14 at DEX 12, the chance to save against a Fireball is 35% *(was 70%)*.

> *Developers' Notes: The doubled d20 isn't in the manual or in AD&D. It made most enemies shrug off a Fireball. Nimble targets still dodge; slow ones now burn.*

**Two weapons**

- **[Changed]** Two weapons cost −2 to hit with the main hand and −4 with the off hand, less with high DEX; rangers and Twin-blades fight with two at no penalty in light armour *(was a small bonus at DEX 5 or less, otherwise nothing)*.
- **[Changed]** The off hand attacks once a round, and extra attacks belong to the main hand *(was the full rate in each hand)*.

**Armour and protection**

- **[Changed]** Helms give AC 1 *(was 0)*.
- **[Changed]** Rings and cloaks of protection follow AD&D: two rings don't stack, a ring gives no AC with magical armour, and a cloak does nothing with magical or metal armour or a shield.
- **[Changed]** Acid and corroding touches let each item save by its material, as in AD&D *(was any non-magical armour destroyed outright)*.
- **[Changed]** Half-giants can hold a two-handed weapon in one hand.

## Classes and Kits

**All classes**

- **[Changed]** Every class can reach **10th level** *(was 9th)*.
- **[Changed]** Character creation keeps what the die rolls: lower a score to raise another, but the six never add up to more than the die gave (shown under CHR as `SUM:99/101`), and the hit points stay as rolled, moving only with CON's bonus *(was any score clicked up to its most, and the hit points set by a click)*.
- **[Changed]** Class restrictions hold: a character may use an item only if every one of its classes allows it, and a multiclass preserver can't cast in armour *(was any one class allowing it)*.
- **[Changed]** Multiclass characters gain hit points as in AD&D: CON's bonus on every hit die (a warrior's if one class is a warrior), the total divided between the classes. Every hit die is rolled twice and the better kept.
- **[Changed]** Experience, priests' THAC0 and spell slots follow AD&D's tables: a gladiator needs 2,250 XP for 2nd level *(was 2,000)*, a preserver has 4 2 1 slots at 5th *(was 3 2 1)*, a cleric 3 3 1 *(was 3 2 1)*.
- **[Changed]** A ranger's spells last and deal damage at its level minus 7, as AD&D has it *(was its full level)*.
- **[Changed]** Preservers' INT sets their chance to learn a spell from a scroll (35% at INT 9 to 100% at 24) and the most spells of each level they can know. New preservers choose their starting spells.

**Kits**

- **[New]** Each class has three kits, chosen at character creation. Each gives something and costs something. A human who changes class can take one for each class, up to three.

| Class | Kits |
|---|---|
| Fighter | Myrmidon, Sentinel, Ravager |
| Gladiator | Arena Champion, Twin-blade, Brute |
| Ranger | Stalker, Seeker, Justifier |
| Thief | Assassin, Swashbuckler, Shinobi |
| Preserver | Arcanist, Scholar, Battle Mage |
| Cleric | Healer, Crusader, Elementalist |
| Druid | Grove Warden, Wanderer, Lifebinder |
| Psionicist | Mind Warrior, Mind Bender, Kineticist |

- **Arcanist:** one more spell slot at each level, and two preserver spells per turn in a fight, for a d3 hit die.
- **Battle Mage:** a warrior's THAC0, leather armour it can cast in, expertise with one weapon, and spells that still go off after being hit.
- **Shinobi:** a thief trained by the Veiled Alliance who casts preserver spells from 6th level, but is unable to read magical script.
- **Ravager:** fights without a shield or missile weapons, with a natural AC that hardens from 7 to 3 as it levels.

> *Developers' Notes: Each kit is built into the game's own code, so it works everywhere the game checks: THAC0, spell slots, hit dice, PSP costs, attacks a round and what you may hold. The player's guide has all 24, with a short description of who takes each one on Athas.*

## Magic and Psionics

- **[New]** Three new wizard spells, each with its own icon and description: **Cat's Grace** (2nd level: DEX +1d6 for an hour of game time a caster level), **Erdlu Claw** (1st level: unarmed attacks become talons, 1d6+1 (or Body Weaponry's and Animal Affinity's dice +1), +1 to hit and as a +1 magical weapon) and **Fogbolt** (1st level: a dark grey bolt that gives a creature -3 to its attacks and +2 to attacks on it, for 2d4 rounds).
- **[Changed]** A click on a spell's icon on the Effects screen no longer ends the spell by mistake. A psionic power's icon still ends it, as that's how you stop a power.

## Thieves

- **[Changed]** Thief skills follow AD&D's table by level, with Dark Sun's race and DEX adjustments *(was a 3rd-level elf with move silently 66 and hide in shadows 61)*.
- **[New]** Thieves **hide in shadows and move silently** in a fight to backstab, halved in daylight. Rangers do it to attack from behind, at full strength under the open sky. *(was a backstab only on a target turned to face someone else)*
- **[New]** **Picking pockets**: use Thieves' Tools on anyone in sight. Fail and you roll move silently to get away. A few named weapons can be lifted for 200 XP.
- **[New]** A worn cloak adds 10 to hiding, boots 10 to moving silently, and a belt 5 to picking pockets and opening locks.
- **[Fixed]** Thief skills no longer drop for holding a weapon. The game's armour penalty looked at the hands, quiver and legs, and never at the armour worn.

## Items

**Weapons**

- **[New]** Short swords, bone and obsidian axes, great axes, daggers, maces, and metal picks and polearms, the plain weapons the game never had, sold by merchants and carried across Athas.
- **[New]** Sixteen new magic weapons, each with its own icon and a story from the game's own item sage. Among them: Flame Blade, an obsidian long sword whose edge burns; Galefang, a dagger an air cleric can wield; Mindshard and Stillwater, short swords for psionicists; and the first magic club, pick and staff sling in the game.

**Armour and worn items**

- **[New]** **Bracers of Defense** (AC 6 to 2) and two robes, the **Ashen Robe** and the **Veiled Robe**, for those who wear no armour. A preserver casts in them.
- **[New]** **The Warden's Plate**: plate armour +1 in four pieces, 12 points of AC as a set.
- **[New]** Rings and a cloak of protection, the Cloak and Boots of Elvenkind, Arrowbane, the Sunking Crown, and the Tome of Understanding (+1 WIS for good).
- **[Changed]** The game's bone scale armour set is complete, with its arm and leg pieces and helm.

## World

- **[New]** **Kalzith**, a defiler slave who scribes spell scrolls by night and sells them to anyone who treats him with respect.
- **[New]** More of **Semyon**'s story, for players who help him in the arena.
- **[New]** A use for the cooked vulture: share it with the pens' cook for a full rest and 100 XP each.
- **[New]** Merchants give your party leader a discount for high Charisma, from 5% at CHA 16 to 25% at 20, as in Baldur's Gate.

## Graphics

- **[New]** The party's figures show the weapons, shields, armour, helms and cloaks they wear, in each material's colours, walking and fighting.
- **[New]** Every figure casts a soft shadow, and walkers kick up dust on sand and dirt.
- **[New]** A red ring can mark the enemy you've chosen, or all of them.

## Quality of Life

- **[New]** **Tab** chooses the nearest enemy and **Enter** attacks it, with no aiming of the mouse.
- **[New]** Press the mouse wheel and drag to scroll the map.
- **[Changed]** 40 save slots on four pages *(was 10)*, and 29 stored characters *(was 19)*.
- **[New]** A game speed setting, so the whole party walks as smoothly as one.
- **[New]** Crash reports: if the game stops with an error, the message stays on screen and a report is written.
- **[New]** The game's window at double, triple or quadruple size, or full screen, chosen in the Ledger.
- **[Changed]** No more copy protection: the dragon asking for a word from the manual never comes.

## Bug Fixes

- **[Fixed]** **DELETE** in the character roster deleted the wrong character when the list was scrolled.
- **[Fixed]** A character not yet played showed 0 in every thief skill.
- **[Fixed]** The game's Sling +1 had no icon.
