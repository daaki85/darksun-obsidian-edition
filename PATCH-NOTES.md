# Obsidian Edition: Patch Notes

*A Dark Sun: Shattered Lands mod · Current version 2.5.0 · Every change from the original game*

Obsidian Edition is a free mod for the GOG release of Dark Sun: Shattered Lands. It shows the rolls the game keeps hidden, brings its rules closer to AD&D 2nd Edition, adds kits, weapons, magic items and people to Athas, dresses the party in what they wear, and fixes bugs left over since 1993. You start the game with the Loader, which loads the mod with your options and logs every roll as it happens. Everything is switchable, the game's own files are never touched, and your saves stay where they are.

**Download:** https://github.com/daaki85/darksun-obsidian-edition/releases/latest

*These notes are also a web page, [`patch-notes.html`](patch-notes.html), with a button that copies them as Markdown for forums.*

## Contents

- [In the Game's Screens](#in-the-games-screens)
- [Combat](#combat)
- [Classes and Kits](#classes-and-kits)
- [Magic and Psionics](#magic-and-psionics)
- [Improved Thieving](#improved-thieving)
- [Items](#items)
- [World](#world)
- [Graphics](#graphics)
- [Quality of Life](#quality-of-life)
- [The Loader](#the-loader)
- [Bug Fixes](#bug-fixes)
- [Your Saved Games](#your-saved-games)

## In the Game's Screens

- **[New]** A combat log in the game: **L** on the map shows every roll, in the game's own lettering and the Loader's colours, at one of three levels of detail, and **L** again hides it. It works in a fight or after one (a thief's roll, a new level's hit points).
- **[New]** The combat log is a panel over the map's lower right that scrolls back (its scrollbar, or the mouse wheel on Windows), shrinks to one line or opens up with filters (All, Party, Damage, Saves); or, as an option, a strip always shown below the map (the game's screen 22 rows taller).
- **[New]** The combat log panel's **A** button shows how many arena fights the party has had (the game's own count, one a trip into the arena), and a click again hides it.
- **[New]** The inventory screen shows THAC0, all five saving throws, the THAC0 with each weapon, DEX's reaction and defence adjustments, and a thief's skills, in the game's own lettering.
- **[New]** View Character shows THAC0 and saves, and for a character of several classes, which class levels up next.
- **[New]** The USE screen shows the spell slots left at each spell level, and the most you get after resting.
- **[New]** In a fight, the Look box shows a monster's hit points, AC, THAC0, alignment, magic resistance and chief defence (NEEDS +1 WEAPON, IMM FIRE COLD...). Close it to read the rest.
- **[New]** Item boxes show a wand's charges left, and the bonus a cloak, boots or belt gives to thief skills.
- **[New]** The Effects screen lists your kits and weapon specializations.

## Combat

**Weapon specialization**

- **[New]** Fighters specialize in one weapon spec, a kind of weapon such as the long sword (+1 to hit, +2 damage, 3/2 attacks a round), with **mastery** at 5th level (+3, +3) and **grand mastery** at 9th (a larger damage die and one more attack).
- **[New]** Gladiators specialize in two weapon specs, a third at 6th level and a fourth at 9th. Rangers gain expertise with the bow and one other weapon spec.
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
- **[Changed]** A thri-kreen in the party fights with edged claws, so creatures that crushing weapons can't hurt are no longer safe from it *(was crushing, as every unarmed attack)*.

## Classes and Kits

**All classes**

- **[Changed]** Every class can reach **10th level** *(was 9th)*.
- **[Changed]** Character creation keeps what the die rolls: lower a score to raise another, but the six never add up to more than the die gave (shown under CHR as `SUM:99/101`), and the hit points stay as rolled, moving only with CON's bonus *(was any score clicked up to its most, and the hit points set by a click)*.
- **[New]** **STORE** and **RECALL** on the character creation screen, as in Baldur's Gate: keep a roll, try the die again, and bring the kept roll back.
- **[Changed]** An air cleric can use daggers, as its sphere allows *(was none: no dagger in the game listed the air cleric)*.
- **[New]** New characters start with fuller gear: a weapon in hand they can use, a sling, leather armour where they may wear it, a Stalker, Assassin or Shinobi a cloak, and some kits weapons of their own (a Battle Dancer two long swords, a Poisoner two daggers). A multiclass preserver starts with no armour, so it can cast.
- **[Changed]** Class restrictions hold: a character may use an item only if every one of its classes allows it, and a multiclass preserver can't cast in armour *(was any one class allowing it)*. Thieves wear light armour only; a multiclass thief (or a human once a warrior or cleric) may wear heavier, losing its thief skills and backstab in it.
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

- **[New]** Thirteen kits for two classes taken at once, each for one race only:

| Race and classes | Kits |
|---|---|
| Elf cleric/fighter | Battle Dancer |
| Half-elf fighter/thief | Shadowblade, Military Scout |
| Half-elf druid/fighter | Wilderness Avenger |
| Half-elf cleric/ranger | Rescuer |
| Dwarf fighter/thief | Ghetto Fighter, Wayfinder |
| Half-elf fighter/preserver | Spellarcher |
| Half-giant fighter/psionicist | Titan Mind |
| Halfling fighter/thief | Poisoner |
| Halfling cleric/psionicist | Spirit Caller |
| Thri-kreen druid/fighter | Wasteland Seer |
| Mul druid/fighter | Wild Fury |

A few of them:

- **Arcanist:** one more spell slot at each level, and two preserver spells per turn in a fight, for a d3 hit die.
- **Healer:** a water cleric only, given the sphere of the cosmos: the spells only druids had, Cure Serious and Critical Wounds, Raise Dead and Neutralize Poison among them, each cure healing 1 more a die.
- **Battle Mage:** a warrior's THAC0, leather armour it can cast in, expertise with one weapon, and spells that still go off after being hit.
- **Shinobi:** a thief trained by the Veiled Alliance who casts preserver spells from 6th level, and learns its own from a scroll only if it can read it (its read languages).
- **Ravager:** fights without a shield or missile weapons, with a natural AC that hardens from 7 to 3 as it levels.
- **Battle Dancer:** dances as each fight starts, a roll against DEX at −4: +1 to hit, damage and AC for a few rounds, or −1 if it stumbles. Long swords and bows only.
- **Military Scout:** better at stealth, traps and climbing under the open sky, with +2 initiative and +1 to hit with bows and slings there, and its hiding isn't halved by the sun; worse under a roof, and it never backstabs.
- **Wild Fury:** Wild Fighting as each fight starts, a roll against CON at −4: one more attack a round in melee and +3 damage, or −3 to hit and AC 3 worse if it fails.
- **[New]** The game's own party has features no one else can have: Gerakis fights wild, K'ratchek casts as a Wasteland Seer and throws her chatkcha twice a round, Cilla, an Elven Wanderer, hides as well in the sun as out of it, and Cermak is an Arcanist.

> *Developers' Notes: Each kit is built into the game's own code, so it works everywhere the game checks: THAC0, spell slots, hit dice, PSP costs, attacks a round and what you may hold. The player's guide has all 37, with a short description of who takes each one on Athas.*

## Magic and Psionics

- **[New]** Six new wizard spells, each with its own icon and description:

| Spell | Level | What it does |
|---|---|---|
| **Cat's Grace** | 2nd | DEX +1d6, for an hour of game time a caster level |
| **Erdlu Claw** | 1st | unarmed attacks become talons: +1 to hit, 1d6+1, as a +1 magical edged weapon (Body Weaponry's and Animal Affinity's dice gain +1) |
| **Fogbolt** | 1st | a dark grey bolt: the creature has −3 to its attacks and is hit at +2, for 2d4 rounds |
| **Reflected Image** | 1st | one image of the caster, struck instead of it half the time |
| **Spook** | 1st | a creature flees for 3 rounds unless it saves |
| **Friends** | 1st | CHA +2d4 for a short while, for better prices |

## Improved Thieving

- **[Changed]** Thief skills follow AD&D's table by level, with Dark Sun's race and DEX adjustments *(was a 3rd-level elf with move silently 66 and hide in shadows 61)*.
- **[New]** Thieves **hide in shadows and move silently** in a fight to backstab, halved in daylight. Rangers do it to attack from behind, at full strength under the open sky *(was a backstab only on a target turned to face someone else)*.
- **[New]** **Picking pockets** with a thief's **Pick Pockets** button on the USE screen (where a priest's Turn Undead is), then a click on anyone in sight: any thief can try, leader or not, and what's lifted goes in that thief's backpack. A cleric/thief has both buttons, the purse beside Turn Undead. Fail and you roll move silently to get away. A purse holds 2 to 5 ceramic pieces for each of the thief's levels, and a few named weapons can be lifted for 200 XP.
- **[New]** A worn cloak adds 10 to hiding, boots 10 to moving silently, and a belt 5 to picking pockets and opening locks, for thieves and rangers alike; the inventory screen's thief skills count them.

## Items

**Magic weapons**

- **[New]** Nineteen new magic weapons, each with its own icon and a story from the game's own item sage:

| Weapon | What it is |
|---|---|
| **Flame Blade** | an obsidian long sword +1 whose blade burns what it hits (2d6 fire damage, a save for half); a fire or earth cleric can wield it |
| **Greenbright** | a metal short sword +2 |
| **Shadowseeker** | a short sword +1 whose wielder sees the invisible |
| **Mindshard** | an obsidian short sword +1 a psionicist can wield |
| **Stillwater** | a bone short sword +1 a psionicist can wield |
| **Galefang** | a metal dagger +2 an air cleric can wield |
| **Nightsliver** | an obsidian dagger +2 a fire or earth cleric can wield |
| **Hayneedle** | a bone dagger +1 a water cleric can wield |
| **Glasshewer** | an obsidian axe +2 a fire or earth cleric can wield |
| **Drakejaw** | a bone axe +1 a water cleric can wield |
| **Headsman** | a metal great axe +2 |
| **Kreenfang** | a bone gythka +1 |
| **Linebreaker** | a metal polearm +2 |
| **Thornwall** | a bone polearm +1 |
| **Gutterknot** | a club +1, the game's first magic club |
| **Deepbiter** | a stone pick +1, the game's first magic pick |
| **Dunesong** | a bow +1, sold in a shop |
| **Windlash** | a staff sling +1, the game's first magic staff sling, sold in a shop |
| **Skycutter** | a chatkcha +2 |

- **[Changed]** The Elven Leader's gift is a **Gythka +2** *(was +1)*.

**Magic armour and worn items**

- **[New]** **Bracers of Defense**: AC 6 to 2 for those who wear no armour, four pairs across Athas. A preserver casts in them.
- **[New]** **Ashen Robe** (+1): AC 1 better and +1 on saves against spells, for preservers, psionicists and druids. A preserver casts in it.
- **[New]** **Veiled Robe** (+2), a robe of the Veiled Alliance: AC 2 better, +1 on every save, and a wizard spell slot more at spell levels 1 to 3, for preservers, psionicists and druids.
- **[New]** **The Warden's Plate**: plate armour +1 in four pieces, 12 points of AC as a set. The helm gives Cloak of Bravery and the chest Resist Fire while worn.
- **[New]** **Inixhide**: leather chest armour +1.
- **[New]** **Rings of Protection +1** (two) and a **Cloak of Protection +1**: +1 AC and +1 on every saving throw.
- **[New]** **Cloak of Elvenkind**: all but invisible when hiding in shadows. Thieves and rangers only.
- **[New]** **Boots of Elvenkind**: silent when moving. Thieves and rangers only.
- **[New]** **Arrowbane**: a silver circlet whose wearer can't be hurt by normal arrows, sling stones or chatkchas. Not armour: a preserver casts in it, and bracers and rings and cloaks of protection still work with it.
- **[New]** **Sunking Crown**: a gold crown that protects its wearer from evil. Not armour, as Arrowbane isn't.
- **[New]** **Gutterward**, a wooden shield +1, and **Ironbulwark**, a metal shield +3: the game had no metal shield.

**Other magic items**

- **[New]** **Tome of Understanding**: read it for +1 WIS for good.
- **[New]** **Kalzith's six scrolls**: Shield, Burning Hands, Blur, Cat's Grace, Lightning Bolt and Haste, spells the game has no scroll of.
- **[New]** **Defilers' scrolls**: a defiler in a fight may carry a scroll of a preserver spell, one time in 20, found on its body.

**Mundane items**

The plain weapons the game never had, sold by merchants and carried across Athas, and more.

- **[New]** **Short swords** (1d6) in bone, obsidian and metal: the game had none.
- **[New]** **Axes** (1d8) in bone and obsidian.
- **[New]** **Great axes** (1d10, two-handed) in bone, obsidian and metal.
- **[New]** **Daggers** in metal, and in bone: the only dagger a water cleric can use.
- **[New]** **Maces** in obsidian and metal.
- **[New]** A **metal pick** and a **metal polearm**.
- **[Changed]** The game's **bone scale armour** set is complete, with its arm and leg pieces and helm.

## World

- **[New]** **Kalzith**, a defiler slave who scribes spell scrolls by night (six spells the game has no scroll of) and sells them to anyone who treats him with respect.
- **[New]** More of **Semyon**'s story, for players who help him in the arena.
- **[New]** A use for the cooked vulture: share it with the pens' cook for a full rest and 100 XP each.
- **[New]** Merchants give your party leader a discount for high Charisma, from 5% at CHA 18 to 40% at 25, and pay 60% of an item's price *(was all of it)*.
- **[New]** Merchants keep the magical items you sell them, to buy back *(was destroyed when sold)*.

## Graphics

- **[New]** The party's figures show the weapons, shields, armour, helms and cloaks they wear, in each material's colours, walking and fighting.
- **[New]** Elves have pointed ears.
- **[New]** Half-elves no longer look like humans: a half-elf man is built like the elf, a little broader, with short fair hair, a leather jerkin, green trousers and pointed ears; a half-elf woman is a little slimmer than the human woman, with golden hair in a bun, pointed ears, a purple cloak and red boots.
- **[New]** Every figure casts a soft shadow, and walkers kick up dust on sand and dirt.
- **[New]** A red ring can mark the enemy you've chosen, or all of them.

## Quality of Life

- **[New]** **Tab** chooses the nearest enemy and **Enter** attacks it, with no aiming of the mouse.
- **[New]** Press the mouse wheel and drag to scroll the map (or, as an option, hold the right button).
- **[Changed]** In a fight the view stays put while a figure walks, moving only to bring back one that walks off the screen *(was: it followed each one near the edge)*.
- **[Changed]** 40 save slots on four pages *(was 10)*, each also kept under its name in a folder of the Loader's, and 29 stored characters *(was 19)*.
- **[New]** A game speed setting, so the whole party walks as smoothly as one.
- **[New]** Crash reports: if the game stops with an error, the message stays on screen and a report is written, with the game's own error message in it; if it freezes, a freeze report saves what it was doing; if DOSBox closes while the game still runs, a report says so.
- **[New]** Item reports: if an item vanishes from the party with nothing ordinary to explain it (not dropped, given, sold, used up or broken), the Loader saves a report in `crash-logs`, as it does for a crash, and says so in the dice log.
- **[New]** The game's window at double, triple or quadruple size, or full screen, chosen in the Loader.
- **[Changed]** No more copy protection: the dragon asking for a word from the manual never comes.

## The Loader

- **[New]** The Loader: it starts the game with the mod and your options, and stays open while you play, laid out in the game's own colours.
- **[New]** **The dice log:** every attack, damage roll, saving throw, thief skill, initiative score and character creation roll as it happens, with the number it needed, the chance of success, and where every bonus came from.
- **[New]** **Characters:** each party member's sheet as View Character lays it out, plus THAC0 with each weapon, saves as the d20 needed right now, attacks a round, current AC and what it's made of, spell slots and thief skills.
- **[New]** **Spells:** every wizard spell, priest spell and psionic power's damage dice, saving throw, effect and duration, read from the running game.
- **[New]** **Dialogue:** everything said, with the speaker's portrait and name, and the reply you chose.
- **[New]** **Options:** every rule change and addition in these notes has its own switch, nearly all on by default, and **Restore defaults** sets them all back.
- **[New]** **Accessibility:** text that can be enlarged up to 2.5 times (**A+**, **A-**, **Ctrl +** and **Ctrl -**), every control reachable from the keyboard, colours with at least 4.5:1 contrast, and the logs saved as text for screen readers.

> *Developers' Notes: Shattered Lands rolls dice for everything and shows you almost none of it. Fireball victims kept saving and nobody knew why (the game doubles the d20 against fire). The Loader started as a way to see those numbers. Once we could see them, we started fixing them.*

## Bug Fixes

- **[Fixed]** **DELETE** in the character roster deleted the wrong character when the list was scrolled.
- **[Fixed]** A character not yet played showed 0 in every thief skill.
- **[Fixed]** The game's Sling +1 had no icon.
- **[Fixed]** **Mirror Image** stopped no weapon blow, and swallowed the caster's own spells (Armor cast on oneself was lost three times in four, an image with it). Now each hit, and each foe's spell aimed at one creature, has a 75% chance to strike an image instead (50% for Reflected Image); spells from your own side always get through.
- **[Fixed]** **Armor** used up two charges for each hit, and one for any spell cast on its wearer, even a friend's Bless. Now one charge for each damaging hit.
- **[Fixed]** **Share Strength** left its strength on the one who got it after the power ended. Now it ends on them too.
- **[Fixed]** The preserver's **Dispel Magic** also stopped everyone it caught from casting spells, your own party included. Now it only dispels.
- **[Fixed]** **Hold Undead** held living creatures too. Now only the undead.
- **[Fixed]** **Cause Serious and Critical Wounds** did 2d9 and 3d9 damage. Now 2d8+1 and 3d8+3, as AD&D has them and as the Cure spells heal.
- **[Fixed]** Thief skills no longer drop for holding a weapon. The game's armour penalty looked at the hands, quiver and legs, and never at the armour worn.
- **[Fixed]** A click on a spell's icon on the Effects screen no longer ends the spell by mistake. A psionic power's icon still ends it, as that's how you stop a power.
- **[Fixed]** The **Trustee** in the slave pens could stop on his rounds and stay busy for good, never talking again. Now he walks on, even in a save where he's already stuck, once talked to.
- **[Fixed]** Cilla, an elf in the ready-made party, was drawn with the half-elf woman's figure; she looks like an elf now (a switch keeps the game's figure).

Rules the game got wrong are put right too, each under its own heading above with a switch, on by default: the saving throws against spells and the doubled d20 against fire, cold and electricity, two weapons, warriors' attacks and acid on armour (Combat); class restrictions, multiclass hit points, the class tables and rangers' spells (Classes and Kits); and thief skills (Improved Thieving).

## Your Saved Games

**You don't need to start a new game for these fixes.** They're in the patched game and the Loader, not in your saves, so they work from the moment you load: images, Armor's charges, Share Strength, Dispel Magic and Hold Undead follow the new rules from the next spell cast, even on effects already running. The fixes stop the old bugs from happening, but don't undo what they already did to a save:

- A character who kept the strength from Share Strength after the power ended still has it (it shows on their Effects screen). Load a save from before the power was used to be rid of it.
- A character silenced by the preserver's Dispel Magic ("No spell use" on their Effects screen) casts again once it wears off.
- A new game whose arena fight never began (no announcer, and walking said NO PATH FROM HERE: a 2.4.0 bug) can't be mended: start a new one.
- Thieves' Tools from an earlier version of the mod (Mirlon's or Kel's) do nothing now: a thief picks pockets with the Pick Pockets button.

**A new game is still the way to see all of the mod.** Kits, STORE and RECALL and fuller starting gear come with characters made with the mod, and much of the new content (Kalzith, Semyon, the vulture, the new items in the slave pens) is in the game's first areas. A save made with the original game loads and plays with every fix and rule change, but its characters have no kits, and what it has already been through stays as it was.
