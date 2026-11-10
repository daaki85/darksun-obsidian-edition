# Obsidian Edition: Patch Notes

*A Dark Sun: Shattered Lands mod · Current version 2.15.0 · Every change from the original game*

Obsidian Edition is a free mod for the GOG release of Dark Sun: Shattered Lands. It shows the rolls the game keeps hidden, brings its rules closer to AD&D 2nd Edition, adds kits, weapons, magic items and people to Athas, dresses the party in what they wear, and fixes bugs left over since 1993. You start the game with the Loader, which loads the mod with your options and logs every roll as it happens. Nearly everything is switchable, the game's own files are never touched, and your saves stay where they are.

**Download:** https://github.com/daaki85/darksun-obsidian-edition/releases/latest

*These notes are also a web page, [`patch-notes.html`](patch-notes.html), with a button that copies them as Markdown for forums. They follow the repository, so a change made since the current version is here before its release; the [changelog](CHANGELOG.md) says which pull request brought it.*

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

- **[New]** A combat log in the game: **L** on the map shows every roll, in small 7-pixel lettering (8 lines at a time) and the Loader's colours, at one of three levels of detail, and **L** again hides it. It works in a fight or after one (a thief's roll, a new level's hit points). It is a panel over the map's lower right that scrolls back (its scrollbar, or the mouse wheel on Windows), shrinks to one line or opens up with filters (All, Party, Damage, Saves).
- **[New]** Names over figures: a spell's name floats over its caster as it is cast, "Miss" over anyone an attack misses, and "Armor: 7 left" when a spell that lasts a number of uses (Armor, Mirror Image, Reflected Image...) loses one, in the game's lettering (an Options switch, on).
- **[New]** Out of a fight, the combat log panel's top line shows how long the game has run, `Day 47, 14:20`; in the arena, once the game has shown the count, how many arena fights the party has had instead (the game's own count, one a trip into the arena).
- **[New]** The inventory screen shows THAC0, all five saving throws, the THAC0 with each weapon, DEX's reaction and defence adjustments, a thief's skills and, with ages on, the character's age, in the game's own lettering.
- **[New]** The creation screen shows the THAC0, right of the hit points: `THAC0: M18 R19`, melee (with STR's to-hit) and ranged (with DEX's missile adjustment), the kit counted, changing as you click STR and DEX or choose a kit.
- **[New]** With ages on, the creation screen shows the age a new character will start at, above RECALL: Table 7's dice, rolled again with each roll of the die (STORE and RECALL keep it with the roll).
- **[New]** View Character shows THAC0 and saves, and for a character of several classes, which class levels up next.
- **[New]** The USE screen shows the spell slots left at the spell level and list on show (wizard slots on the MAGE list, priest slots on the CLERIC list), and the most you get after resting.
- **[New]** In a fight, the Look box shows a monster's hit points, AC, THAC0, alignment, magic resistance and chief defence (NEEDS +1 WEAPON, IMM FIRE COLD...). Close it to read the rest.
- **[New]** Item boxes show a wand's charges left, the bonus a cloak, boots or belt gives to thief skills, and a plain wooden, bone, stone or obsidian weapon's to-hit penalty (`Hit -1` for bone, `Hit -2` for obsidian).
- **[New]** The Effects screen lists your kits and weapon specializations, and a Shinobi's chance to read languages; with the pointer on the icon of a spell that lasts a number of uses (Armor, Mirror Image, Reflected Image...), it says how many charges are left, for Enlarge how much more it gives (ENLARGED (+90% DICE), or DAMAGE with its rule off), and for Barkskin, Flesh Armor and Magical Vestments the armour AC they give (BARKSKIN (AC 3)).
- **[New]** Reading a scroll on the inventory screen tells you what happened (YOU LEARN THE SPELL, YOU CAN NOT READ THE SCROLL, THAT IS NOT A SHINOBI SPELL...) on the line under the paper doll. The game showed nothing there.

## Combat

**Weapon specialization**

- **[New]** Fighters specialize in one weapon spec, a kind of weapon such as the long sword (+1 to hit, +2 damage, 3/2 attacks a round), with **mastery** at 5th level (+3, +3) and **grand mastery** at 9th (the next greater damage die against every target, a long sword's 1d12 against a large one 1d20 as Player's Option: Combat & Tactics has it, and one more attack).
- **[New]** Gladiators specialize in two weapon specs, a third at 6th level and a fourth at 9th. Rangers gain expertise with the bow and one other weapon spec. The Battle Mage, Crusader and Mind Warrior kits gain expertise with one melee weapon spec of their choice (3/2 attacks a round, 2 from 7th level).
- **[Fixed]** Warriors attack at AD&D's plain rate with weapons outside their specializations *(was 3/2 with any weapon)*. Specialists shoot missiles faster.
- **[Changed]** Every thri-kreen, foes too, throws a chatkcha once more a round, AD&D's 2/1 for its own weapon *(was at the weapon's rate, like anyone)*; a thri-kreen Mind Warrior may take the chatkcha as its weapon spec.
- **[New]** The weapons spells make count for specialization: the Flame Blade as a long sword, Shillelagh as a club, Spiritual Hammer as a mace.

**Saving throws**

- **[Fixed]** Spells are saved against with the spell save *(was petrification/polymorph for almost every spell)*.
- **[Fixed]** Against fire, cold and electricity, DEX helps you dodge, from −5 to +6 *(was a doubled d20)*. Needing 14 at DEX 12, the chance to save against a Fireball is 35% *(was 70%)*.

> *Developers' Notes: The doubled d20 isn't in the manual or in AD&D. It made most enemies shrug off a Fireball. Nimble targets still dodge; slow ones now burn.*

**Two weapons**

- **[Fixed]** Two weapons cost −2 to hit with the main hand and −4 with the off hand, less with high DEX; rangers, Twin-blades and Battle Dancers fight with two at no penalty in light armour, a Justifier in any, and a Ghetto Fighter at 0 and −2 *(was a small bonus at DEX 5 or less, otherwise nothing)*.
- **[Fixed]** The off hand attacks once a round, and extra attacks belong to the main hand *(was the full rate in each hand)*.

**Held targets**

- **[Fixed]** A blow on a held (Paralyzed) or Out Cold creature hits automatically and does normal damage, as in AD&D *(was a roll to hit as ever, and double damage)*. It cuts both ways: a held party member is hit every time too.

**Armour and protection**

- **[Changed]** Helms give AC 1 *(was 0)*.
- **[Changed]** Rings and cloaks of protection follow AD&D: two rings don't stack, a ring gives no AC with magical armour, and a cloak does nothing with magical or metal armour or a shield.
- **[Fixed]** Acid and corroding touches let each item save by its material, as in AD&D *(was any non-magical armour destroyed outright)*.

**Races**

- **[Changed]** Half-giants can hold a two-handed weapon in one hand.

**Size and weapons**

- **[New]** **Creature size**: a large target (a half-giant, a large monster, anyone Enlarged) takes AD&D's damage for large targets from a weapon (a long sword 1d12, a great axe 2d8, a gythka 1d10; a dagger 1d3, a chatkcha 1d4+2), and Hold Person and Charm Person don't work on it at all. A weapon's item box shows both damages (`1D8-1/1D12-1`), and Shillelagh's damage reads 1D6+1 (2D4 against a large foe). *(the game keeps no sizes)*
- **[Changed]** The **pick** is AD&D's footman's pick, 1d6+1 (2d4 against a large foe), and the **axe** the battle axe, 1d10 against a large foe, as *Player's Option: Skills & Powers* has them *(the pick was the horseman's 1d4+1 (1d4); the axe 1d8 against any size)*. Deepbiter and the Metal Pick hit as the footman's pick too.
- **[New]** **Cahulaks** fight as Dark Sun's rules describe them: a bladed head in each hand, so one more attack a round (at −2 and −4, as with two weapons, DEX helping), and a hit can tangle a man-sized or smaller foe, which then loses its next turn unless it saves against petrification. Half-giants, large monsters, anyone Enlarged, the bodiless (elementals, slimes, swarms, shadows) and a few other beasts can't be tangled ([the creatures' table](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/CREATURES.md) (spoilers) marks each). Twin-blades and Battle Dancers can't use cahulaks.
- **[New]** **Staff sling stinkpots** (AD&D's *Arms and Equipment Guide*; with the cahulaks' traits, one switch: **Weapon traits**): the staff sling throws clay pots of burning sulphur, 1d3 damage against any size, and a target hit saves against poison or is nauseated for 1d3+1 rounds, −2 on its attack rolls (NAUSEATED on the Effects screen). Undead, and anything immune to poison, are unaffected. *(was a plain 1d4 shot)*
- **[New]** **Polearm reach** (with **Weapon traits**): a polearm held with no other weapon in the hands (a shield, or a bow in the missile slot, is fine) strikes a foe two squares away as well as an adjacent one, for the party and its foes alike. Two squares diagonally don't count. *(a polearm struck only an adjacent foe)*

## Classes and Kits

**All classes**

- **[Changed]** Levels stop at a cap of **749,999 XP** instead of 9th level, shared out: one class goes as far as its next level needs no more (cleric 11th, druid 12th, fighter, gladiator and ranger 10th, preserver and psionicist 11th, thief 13th); two or three classes share it evenly (374,999 or 249,999 each); a human who changed class has what its old classes' levels didn't use *(was 9th level for every class)*.
- **[Changed]** Character creation keeps what the die rolls: lower a score to raise another, but the six never add up to more than the die gave (shown under CHR as `SUM:99/101`), and the hit points stay as rolled, moving only with CON's bonus *(was any score clicked up to its most, and the hit points set by a click)*.
- **[New]** **STORE** and **RECALL** on the character creation screen, as in Baldur's Gate: keep a roll, try the die again, and bring the kept roll back.
- **[Fixed]** An air cleric can use daggers, as its sphere allows *(was none: no dagger in the game listed the air cleric)*.
- **[Changed]** An air cleric may also use cahulaks (Dark Sun's cahulaks are thrown weapons, as AD&D's daggers are) *(was not: the class restrictions took them away)*.
- **[New]** New characters start with fuller gear: a weapon in hand they can use, a sling, leather armour where they may wear it, a Stalker, Assassin or Shinobi a cloak, and some kits weapons of their own (a Battle Dancer two long swords, a Poisoner two of its weapon spec, daggers or short swords). A multiclass preserver starts with no armour, so it can cast.
- **[Fixed]** Class restrictions hold: a character may use an item only if every one of its classes allows it, and a multiclass preserver can't cast in armour *(was any one class allowing it)*. Thieves wear light armour only; a multiclass thief (or a human once a warrior or cleric) may wear heavier, losing its thief skills and backstab in it.
- **[Fixed]** Multiclass characters gain hit points as in AD&D: CON's bonus on every hit die (a warrior's if one class is a warrior), the total divided between the classes.
- **[Changed]** Every character's hit dice are rolled twice and the better kept, at character creation and at every level (a rule change, on unless unticked).
- **[Fixed]** Experience, priests' THAC0 and spell slots follow AD&D's tables: a gladiator needs 2,250 XP for 2nd level *(was 2,000)*, a preserver has 4 2 1 slots at 5th *(was 3 2 1)*, a cleric 3 3 1 *(was 3 2 1)*.
- **[Fixed]** A ranger's spells last and deal damage at its level minus 7, as AD&D has it *(was its full level)*.
- **[New]** **Ages** (a rule change, on unless unticked): each character has an age from the Dark Sun rules' tables, shown on the inventory screen and the Loader's Characters tab. Middle, old and venerable age change the scores, and a character dies at the most its race lives; everyone is a year older each 365 days of game time (the dice log says so), and magic ages them faster. **Haste** now asks each creature it speeds for a system shock roll by CON, as in AD&D: one that fails dies, and a party member who survives is a year older. **Restore Youth** (a 6th-level priest spell: Magic and Psionics) takes magical years back.
- **[Fixed]** **CON 20 and up** gives a hit point back at AD&D's rate, one an hour at CON 20 to one every 10 minutes at 25 *(was one every 5 minutes at any of them)*; and a dwarf's or halfling's poison save gets only its racial bonus, as in AD&D *(was CON's adjustment as well)* (a rule change, CON as in AD&D, on unless unticked).
- **[Fixed]** **Dual-classing** as the manual has it: from 3rd level, with every prime requisite of the old class at 15 or more and every one of the new class at 17 or more (a rule change, on by default) *(was 2nd level, and one score a class checked: a ranger, druid or psionicist on WIS alone)*.
- **[Fixed]** Preservers' INT sets their chance to learn a spell from a scroll (35% at INT 9 to 100% at 24) and the most spells of each level they can know. New preservers choose their starting spells.

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

- **[New]** Thirteen kits for two (or, for one, three) classes taken at once, each for one race only:

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
| Thri-kreen druid/fighter/psionicist | Wasteland Seer |
| Mul druid/fighter | Wild Fury |

A few of them:

- **Arcanist:** two preserver spells per turn in a fight, for a d3 hit die.
- **Scholar:** one more spell slot at each spell level, and one more spell learnt at each level, for 1 worse to hit.
- **Healer:** a water cleric only, given the sphere of the cosmos: the spells only druids had, Cure Serious and Critical Wounds, Raise Dead and Neutralize Poison among them, each cure healing 1 more a die.
- **Assassin:** a backstab one step deadlier (×3 at 1st level up to ×6 from 13th), for −15 to picking pockets and locks.
- **Wilderness Avenger:** +1 to hit and damage against anything, and Cause Wounds spells doing 1 more a die, for no healing spells at all.
- **Rescuer:** cures heal 1 more a die and +2 movement in a fight, for no shield and only +1 from behind.
- **Poisoner:** every melee hit poisons (a save or 10 damage), for a dagger or short sword spec only.
- **Battle Mage:** a warrior's THAC0, leather armour it can cast in, expertise with one weapon, and spells that still go off after being hit.
- **Shinobi:** a thief trained by the Veiled Alliance who casts preserver spells from 6th level (4th-level ones, Improved Invisibility, Solid Fog and Confusion, at 13th), and learns its own from a scroll only if it can read it (its read languages).
- **Ravager:** fights without a shield or missile weapons, with a natural AC that hardens from 7 to 3 as it levels.
- **Battle Dancer:** dances as each fight starts, a roll against DEX at −4: +1 to hit, damage and AC for a few rounds, or −1 if it stumbles. Long swords and bows only, and no shield.
- **Military Scout:** better at stealth, traps and climbing under the open sky, with +2 initiative and +1 to hit with bows and slings there, and its hiding isn't halved by the sun; worse under a roof, and it never backstabs.
- **Spellarcher:** shoots every arrow as a magic one (1 better, at least +1), and weaves the touch spells it knows into arrows: a button on the USE screen for each, a spell slot for 5 arrows a preserver level in its empty quiver (or added to the same spell's arrows there), each casting its spell on what it hits at the archer's preserver level. They stay in the quiver until shot, as a Flame Blade stays in the hand. Making them plays the spell's own cast sound.
- **Wild Fury:** Wild Fighting as each fight starts, a roll against CON at −4: one more attack a round in melee and +3 damage, or −3 to hit and AC 3 worse if it fails.
- **[New]** The game's own party has features of its own: Gerakis fights wild (as a Wild Fury does), K'ratchek casts and uses psionics as a Wasteland Seer does, Cilla hides as well in the sun as out of it (her feature, the Elven Shadow-walker), and Cermak is an Arcanist.

> *Developers' Notes: Each kit is built into the game's own code, so it works everywhere the game checks: THAC0, spell slots, hit dice, PSP costs, attacks a round and what you may hold. The player's guide has all 37, with a short description of who takes each one on Athas.*

## Magic and Psionics

- **[Fixed]** **Spells and psionics as the manual describes them** (a rule change, on by default, from the next start): saves against Bestow Curse and Blood Flow; Flaming Sphere negated by a save; no save against Quicksand; Solid Fog (1d3 rounds + 1 a level), Cause Fear (1d4 rounds), Minor Spell Turning (3 rounds a level) and Stinking Cloud (1d4+1 rounds) for the manual's time; Turn Pebble to Boulder 11-26; Minute Meteors five globes of 1d4; Flame Arrow a 5d6 bolt for every 5 caster levels; Ironskin a blow stopped a caster level; Chaos saved against by creatures of very high or very low INT; Color Spray saved against only by creatures of more levels than the caster, and Hold Undead only on undead of the caster's level or lower; Free Action frees creatures held by Web, Solid Fog, Quicksand, Entangle or Grease; Fire Shield +2 and Blur +1 on saves; Chill Touch weakens for an hour and sends undead fleeing; Cloudkill kills weak creatures; Feeblemind stops psionics too, and Heal cures it; Lower Resistance takes 30% plus 1% a level; Strength and Cat's Grace roll by class; Rainbow Pattern holds a round a level and breaks when its victim is hurt; Cell Adjustment heals 1d4; Biofeedback always leaves a blow at least 1. **Turn Undead** follows AD&D's table: turned undead flee for 3d4 rounds, the strongest results destroy, and a priest who fails can't try the same undead again that fight *(was destroyed or nothing, as often as the priest liked)*. Monsters' hit dice count as their level for saving throws *(was level 0 for a monster with no class)*.
- **[Fixed]** **Monsters as the manual describes them** (with the same rule change): Shadows and Greater Shadows drain Strength and shrug off cold, the Babau and Blue Slaad carry deadly poison, the Styr breathes fire (and only +1 weapons hurt it), the Djinn turns invisible and makes mirror images, and the Tari's bite can carry disease *(was cold damage and paralysis, a corroding touch, disease, and nothing of the rest)*.
- **[Fixed]** **Spells roll to hit** (a rule change, on by default, from the next start): the missile spells (Acid Arrow, Turn Pebble to Boulder, Magical Stone, Condense, and each of Minute Meteors' globes, at +2) and the Strine's spines roll against the target's AC, as do the touch spells cast at an enemy (Chill Touch, Shocking Grasp, Vampiric Touch, the Cause Wounds spells, Cause Disease, Poison); a miss does nothing *(was every one landing)*.
- **[Changed]** **Resting** heals by the priests' remaining spells (and psionicists' Cell Adjustment) and a night's natural healing (3 HP and CON's bonus, plus CON 20+ regeneration) (a rule change, on by default) *(was every member healed to full)*.
- **[Fixed]** **Enlarge** makes only the weapon's dice bigger, 10% a caster level, rounded up, with STR and magic added after, as in AD&D (a rule change, on unless unticked) *(was the whole melee damage made bigger, STR included)*.
- **[New]** Six new wizard spells, each with its own icon and description:

| Spell | Level | What it does |
|---|---|---|
| **Erdlu Claw** | 1st | unarmed attacks (a thri-kreen's claws, not its bite) become talons: +1 to hit, 1d6+1, as a +1 magical edged weapon (Body Weaponry's and Animal Affinity's dice gain +1) |
| **Fogbolt** | 1st | a dark grey bolt: the creature has −3 to its attacks and is hit at +2, for 2d4 rounds |
| **Reflected Image** | 1st | one image of the caster, struck instead of it half the time |
| **Spook** | 1st | a creature flees for 3 rounds unless it saves |
| **Friends** | 1st | CHA +2d4 for a short while, for better prices |
| **Cat's Grace** | 2nd | DEX +1d8 for a rogue, 1d6 for a wizard, warrior or psionicist, 1d4 for a priest (1d6 for anyone with the manual's spells off), for an hour of game time a caster level |

- **[New]** Ten 6th-level priest spells for clerics and druids of 11th level and up, with a 6th-level slot at 11th and two at 12th:

| Spell | Who | What it does |
|---|---|---|
| **Heal** | druids, Healer clerics | every wound healed, disease and blindness cured |
| **Harm** | druids, Healer clerics | leaves a creature 1d4 hit points, no save |
| **Restore Youth** | druids, Healer clerics | takes back a year of magical aging (Haste's) a caster level, after a system shock roll |
| **Blade Barrier** | air | a wall: 8d8 to each creature in it, a save for none |
| **Wall of Thorns** | earth | a wall: 8 plus the creature's AC to each creature in it |
| **Sunstroke** | fire | one creature that fails its save collapses, helpless, and burns for 1d4 fire each round |
| **Fire Seeds** | fire | four seeds of 2d8 burst together in an area, a save for half |
| **Heartseeker** | earth, water | save against death or die; 2–16 on a save |
| **Water of Life** | water | heals a creature by taking its wounds onto the caster |
| **Whirlwind** | air | a whirlwind that stays a round a caster level: 2d8 each round to each creature in it, a save for half; one that fails loses its next turn; nothing can be shot or cast through it |

## Improved Thieving

- **[New]** A soft breath as a thief or ranger hides in a fight, and a purse's jingle for a picked pocket (lifting one of the three named weapons plays the game's quest sound).
- **[Fixed]** Thief skills follow AD&D's table by level, with Dark Sun's race and DEX adjustments, and none goes above 95 *(was a 3rd-level elf with move silently 66 and hide in shadows 61)*.
- **[New]** Thieves **hide in shadows and move silently** in a fight to backstab, halved in daylight. Rangers do it to attack from behind, at full strength under the open sky *(was a backstab only on a target turned to face someone else)*.
- **[Fixed]** A **backstab** multiplies only the weapon's dice; STR and magic bonuses are added once after, as in AD&D, and only the round's first attack is a backstab *(was the whole damage multiplied, STR included, so a strong thief could hit for over 100, on the first two attacks of the round)*.
- **[New]** **Picking pockets** with a thief's **Pick Pockets** button on the USE screen (where a priest's Turn Undead is), then a click on anyone in sight: any thief can try, leader or not, and what's lifted goes in that thief's backpack. A cleric/thief has both buttons, the purse beside Turn Undead. Fail and you roll move silently to get away. A purse holds 2 to 5 ceramic pieces for each of the thief's levels, and a few named weapons can be lifted for 200 XP (once a game each).
- **[New]** A worn cloak adds 10 to hiding, boots 10 to moving silently, and a belt 5 to picking pockets and opening locks, for thieves and rangers alike; the inventory screen's thief skills count them.

## Items

**Magic weapons**

- **[New]** Twenty-two new magic weapons, each with its own icon, and all but the Cahulaks +1 with a story from the game's own item sage:

| Weapon | What it is |
|---|---|
| **Flame Blade** | an obsidian long sword +1, an item (not the blade the spell makes), whose blade burns what it hits (2d6 fire damage, a save for half); a fire or earth cleric can wield it |
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
| **Cahulaks +1** | bone cahulaks +1, their blades glowing in fire colours: Legcrusher fights with them (no more clubs) |
| **Emberlash** | obsidian cahulaks +1 an earth, fire or air cleric can wield |
| **Ironwhirl** | metal cahulaks +2 an earth or air cleric can wield |
| **Dunesong** | a bow +1, which the Bowyer's archery target counts as it does the game's own bows |
| **Windlash** | a staff sling +1, the game's first magic staff sling |
| **Skycutter** | a chatkcha +2 |

Where each is found is in [ITEMS](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/ITEMS.md#every-magic-item).

- **[Changed]** The Elven Leader's gift is a **Gythka +2** *(was +1)*.
- **[Changed]** The elven caravan's buried cahulaks are a **Cahulaks +2**, still casting Cause Light Wounds on a hit, their blades glowing blue *(was the game's Cahulaks +1)*.
- **[New]** The game's own **Polearm +1**, which it defines but never placed, is in the world now.

**Magic armour and worn items**

- **[New]** **Bracers of Defense**: AC 6 to 2 for those who wear no armour, four pairs across Athas. A preserver casts in them.
- **[New]** **Ashen Robe** (+1): AC 1 better and +1 on saves against spells, for preservers, psionicists and druids. A preserver casts in it.
- **[New]** **Veiled Robe** (+2), a robe of the Veiled Alliance: AC 2 better, +1 on every save, and a wizard spell slot more at spell levels 1 to 3, for preservers, psionicists and druids.
- **[New]** **The Warden's Plate**: plate armour +1 in four pieces, 12 points of AC as a set. The helm gives Cloak of Bravery and the chest Resist Fire while worn.
- **[New]** **Inixhide**: leather chest armour +1.
- **[New]** **Rings of Protection +1** (two) and a **Cloak of Protection +1** (in Pehtucl's locked chest: see World): +1 AC and +1 on every saving throw.
- **[New]** **Cloak of Elvenkind**: all but invisible when hiding in shadows. Thieves and rangers only.
- **[New]** **Boots of Elvenkind**: silent when moving. Thieves and rangers only.
- **[New]** **Boots of Speed**: in a fight, double movement and AC 2 better while the wearer can move. Anyone can wear them.
- **[New]** **Arrowbane**: a silver circlet whose wearer can't be hurt by normal arrows, sling stones or chatkchas. Not armour: a preserver casts in it, and bracers and rings and cloaks of protection still work with it.
- **[New]** **Sunking Crown**: a gold crown that protects its wearer from evil. Not armour, as Arrowbane isn't.
- **[New]** **Girdle of Back Defense**: no enemy gets the bonus for attacking its wearer from behind, nor a backstab.
- **[New]** **Golden Girdle of Urnst**: AC 3 better against long and short swords.
- **[New]** **Amulet of Magic Resistance**: 15% magic resistance. Unlike AD&D's, it never shatters.
- **[New]** **Gutterward**, a wooden shield +1, and **Ironbulwark**, a metal shield +3: the game had no metal shield.

**Other magic items**

- **[New]** **Tome of Understanding**: read it for +1 WIS for good.
- **[New]** **Kalzith's six scrolls**: Shield, Burning Hands, Blur, Cat's Grace (with the new spells on), Lightning Bolt and Haste, spells the game has no scroll of.
- **[New]** **Defilers' scrolls**: a defiler in a fight may carry a scroll of a preserver spell, one time in 20, found on its body.
- **[New]** **Burning, Chill, Shocking and Vampiric Arrows**: a Spellarcher's own, woven from its touch spells; each casts its spell on what it hits, and they fade at the next rest.

**Mundane items**

The plain weapons the game never had, sold by merchants and carried across Athas, and more.

- **[New]** **Short swords** (1d6) in bone, obsidian and metal: the game had none.
- **[New]** **Axes** (1d8) in bone and obsidian.
- **[New]** **Great axes** (1d10, two-handed) in bone, obsidian and metal.
- **[New]** **Daggers** in metal, and in bone: the only dagger a water cleric can use.
- **[New]** **Maces** in obsidian and metal.
- **[New]** A **metal pick** and a **metal polearm**.
- **[New]** **Metal cahulaks**: the champions' mul wields them, and the Weapon Merchant sells them. The arena's dead body by the stone arch holds plain bone cahulaks.
- **[New]** **Obsidian cahulaks**, which earth, fire and air clerics may use: Jark sells them, and an earth or fire cleric-warrior who picks the cahulaks starts with them.
- **[Changed]** The game's **bone scale armour** set is complete, with its arm and leg pieces and helm.
- **[New]** The game's plain **leather helm**, which it never placed: Kurzak wears one in the slave pens, and Scar in the arena.

## World

- **[New]** **Kalzith**, a defiler slave who scribes spell scrolls by night and sells them to anyone who treats him with respect, with a face of his own, painted in the game's portrait style.
- **[New]** More of **Semyon**'s story, for players who help him in the arena. Once he has told of it (ask him "Seen anything useful?"), **Thornwall** comes onto the slave pens' weapon rack.
- **[New]** **Pehtucl's chest**, locked and trapped with a poisoned needle: a thief disarms it and picks the lock, anyone else can try to bash it open and set the needle off. The Cloak of Protection +1 is inside.
- **[New]** A last arena bout: once Scar dies in the arena, six champions from a distant arena come to test the new king, led by a Tohr-kreen carrying **Kreenfang** ([the champions' bout](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/FEATURES.md#the-champions-bout)).
- **[New]** A use for the cooked vulture: share it with the pens' cook for a full rest and 100 XP each.
- **[New]** Merchants give your party leader a discount for high Charisma, from 5% at CHA 18 to 40% at 25.
- **[Changed]** Merchants pay 60% of an item's price *(was all of it)*.
- **[New]** Merchants keep the magical items you sell them, to buy back *(was destroyed when sold)*.
- **[New]** Scar fights with a pair of obsidian cahulaks and wears a full leather suit with a helm; his henchmen swing bone great axes, which they drop when they fall, and wear leather chest and arm armour (in a new game: the arena's fighters are made on its first visit).
- **[New]** People the party fights who had nothing in hand and struck with their fists carry weapons and armour that suit them.

## Graphics

- **[New]** The party's figures show the weapons, shields, armour, helms and cloaks they wear, in each material's colours, walking and fighting.
- **[New]** Magic gear glows on the party's figures: a weapon's bright edge, a shield's boss and rim, and sparks on armour, bracers, cloaks, helms, boots and belts shimmer in the animated colour nearest the item's icon: fire, green, violet or blue. The weapons spells make glow whole, the Flame Blade and Shillelagh in fire and Spiritual Hammer in blue, as do Kreenfang's blades. Boots of Elvenkind now show on the feet, in soft green. The mod's magic gear with no plus (the Boots of Speed, the Elvenkind cloak and boots, the girdles) glows too.
- **[New]** Nineteen of the game's magic items that sat still in their icons now shimmer, as its other magic items do: the Parting Staff, the Chameleon Gloves, the Hornblade, Cahulaks +1 (Legcrusher's now, in fire colours; the caravan's, made +2, has a blue glow of its own), Dag's Dagger, the Terror Blade, Blackmace, the Shimmer, Drake and Silk Armor, Tanelyv's and Grey's arm and leg pieces, the Living Cloak, the Golden Torque, Light of Dawn, El's Ring and the Orb of Knowledge. A plain item sharing an icon with one of them (plain cahulaks, a plain ring) keeps the still one.
- **[New]** Elves have pointed ears.
- **[New]** With ages on, a party member's hair greys on the map as they age: streaks when middle-aged, grey when old, white when venerable (with what the party wears shown).
- **[New]** Half-elves no longer look like humans: a half-elf man is built like the elf, a little broader, with short fair hair, a leather jerkin, green trousers and pointed ears; a half-elf woman is a little slimmer than the human woman, with golden hair in a bun, pointed ears, a purple cloak and red boots.
- **[New]** Every figure casts a soft shadow, and walkers kick up dust on sand and dirt.
- **[New]** A thief or ranger hidden in shadows in a fight, and anyone invisible, is drawn half see-through.
- **[New]** The 6th-level priest spells that stay on the map have pictures of their own: Blade Barrier's circling blades, Wall of Thorns' tangle of thorns, Fire Seeds' fireball and Whirlwind's tall, turning funnel of dust. The blades and thorns are Wake of the Ravager's, read from your copy (GOG sells it with Shattered Lands); without it they are the fire wall, recoloured.

## Quality of Life

- **[New]** **Tab** chooses the nearest enemy and **Enter** attacks it, with no aiming of the mouse. A red ring marks the enemy chosen.
- **[New]** Press the mouse wheel and drag to scroll the map.
- **[New]** **M** opens the overhead map, and **M** again closes it. **U** and **I** close the USE and inventory screens when pressed again.
- **[Changed]** A game starts and loads with the whole party on the map, and it stays in view after a fight, as **5** does (an Options switch, on); **6** still gathers it into the leader *(was the leader alone, often, until 5)*.
- **[New]** The game's pointer in the intro, its logos and its other scenes, and a click skips a scene as a key does *(was no pointer, and only a key)*.
- **[Changed]** The pointer starts in the middle of the screen, stays where you leave it as screens change (the intro, menus, loading), moves as far up and down as across, and in a window as fast as your desktop's pointer *(was at the screen's right edge, half as far up and down, and in a window three times as fast, so placing items in the inventory was fiddly)*.
- **[Changed]** The pointer stands still for less time after you pick up or put down an item in the inventory, so it jumps less far when it moves again *(was up to a tenth of a second)*.
- **[Changed]** In a fight the view stays put while a figure walks, moving only to bring back one that walks off the screen *(was following each one near the edge)*.
- **[Changed]** 40 save slots on four pages *(was 10)*, each also kept under its name in a folder of the Loader's, and 29 stored characters *(was 19)*.
- **[Changed]** The default game speed is Fastest (35,000 cycles): the whole party walks at full speed with nearly every picture shown. Faster stays for older computers.
- **[Changed]** The mod's shadows, dust and see-through figures cost about a third less to draw: walking shows about 50% more pictures a second at the Faster speed (15.5, was 10.2) and walks faster at Fastest. Dust is lighter, as it was meant to be (a walker raised a puff almost every moment).
- **[Changed]** The game runs faster than with GOG's settings: DOSBox is given more of the computer's time, and a **Game speed** setting chooses how much (GOG's own, faster or fastest). On the map the whole party keeps its walking pace with shadows and dust on: when drawing a picture costs the walkers more steps than the original game's pictures do, the next picture is skipped rather than everyone slowing down, and a quick computer sees every picture *(was slower with the whole party in view)*. Steady pace is an Options switch under Game speed, on.
- **[New]** Crash reports: if the game stops with an error, the message stays on screen and a report is written, with the game's own error message and how much memory it had left; if it freezes, a freeze report saves what it was doing; if DOSBox closes while the game still runs, a report says so.
- **[New]** A warning when memory runs low: the dice log tells you to save and restart before the game runs out (a fresh start has all of it back).
- **[New]** Item reports: if an item vanishes from the party with nothing ordinary to explain it (not dropped, given, sold, used up or broken), or the game destroys one (acid, Detonate's blast), the Loader saves a report in `crash-logs`, as it does for a crash, and says so in the dice log.
- **[New]** The game's window at its own size, double, triple or quadruple, or full screen, chosen in the Loader.
- **[Changed]** No more copy protection: the dragon asking for a word from the manual never comes.

## The Loader

- **[New]** A **fight's summary** in the dice log as it ends: `Fight over: 3 rounds, 4 kills; the party dealt 61 damage and took 19`, then each member's attacks that hit, damage dealt, kills and damage taken.
- **[New]** The dice log reads at a glance: each event on one line, what came of it first (`● Seneca hits Arena Guard for 11 — backstab`), the HP left and the roll in columns at the right, the sums under it dimmed, coloured by whether it went well or badly for the party. **Readable layout** above the log switches back to the lines as written.
- **[New]** The Loader: it starts the game with the mod and your options, and stays open while you play, laid out in the game's own colours.
- **[New]** **The dice log:** every attack, damage roll, saving throw, thief skill, initiative score and character creation roll as it happens, with the number it needed, the chance of success, and where every bonus came from.
- **[New]** **Characters:** each party member's sheet as View Character lays it out, plus THAC0 with each weapon, saves as the d20 needed right now, attacks a round, current AC and what it's made of, spell slots and thief skills.
- **[New]** **Spells:** every wizard spell, priest spell and psionic power's damage dice, saving throw, effect and duration, read from the running game.
- **[New]** **Dialogue:** everything said, with the speaker's portrait and name, and the reply you chose.
- **[New]** **Find** in the dice log and the dialogue (Ctrl+F): every match highlighted, Enter for the next.
- **[New]** More of a fight in the dice log: the **psionic defence** against Ego Whip, Id Insinuation, Psychic Crush and Psionic Blast; the **protection that halved** a spell's damage (Resist Fire, Fire Shield...); what a monster's **special attack** does (`Paralysing attack: lasts 7 rounds unless saved against`); **Detonate**'s blast on an item: which one, the d20, and whether it's gone (it picks the worn item that breaks most easily, a bone helm before bone armour); and whether a thri-kreen strikes with a **claw or its bite**.
- **[New]** More of the game's own choices in the dice log: why it **refused a spell** you clicked (no line of sight, too far...); what a **script** asked for (a rest, random monsters, an arena bout); the **ability checks scripts make** with a roll of their own (a CHA to talk someone round, STR to break chains); and a party member's **ability score** changing.
- **[New]** Each shot at the **Bowyer's archery target** in the dice log: the roll, what it needed, how far the archer is from the target and the Bowyer, and whether a centre shot earns his arrows.
- **[New]** **How the game works** compares every cleric spell and psionic power with the manual: what the manual says, what the game's code does, and what the log shows.
- **[New]** The Loader can run the game as **Dark Sun Recompiled**, the game translated into a program of its own, instead of in DOSBox, where it is installed.
- **[New]** **Options:** nearly every rule change and addition in these notes has its own switch (not the keys and the game's fixed bugs), all on by default (the red ring's, the game speed's and the combat log's level aside), and **Restore defaults** sets them all back.
- **[New]** **Accessibility:** text that can be enlarged up to 2.5 times (**A+**, **A-**, **Ctrl +** and **Ctrl -**), every control reachable from the keyboard, colours with at least 4.5:1 contrast, and the logs saved as text for screen readers.

> *Developers' Notes: Shattered Lands rolls dice for everything and shows you almost none of it. Fireball victims kept saving and nobody knew why (the game doubles the d20 against fire). The Loader started as a way to see those numbers. Once we could see them, we started fixing them.*

## Bug Fixes

The main fixes are below; every bug of the original game the mod mends, with what the game did, is in [the game's bugs, fixed](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/GAME-BUGS.md).

- **[Fixed]** The **Quicksilver Glove** fought as if it were wooden (−3 to hit, −2 damage): it had no material, which the game read as wood. It is leather now, as the Chameleon Gloves are.
- **[Fixed]** **Alagorn** told two items wrong: the Quicksilver Glove as "Quicksilver Gauntlets" that graft a weapon to the hand (it casts Detonate on every hit), and the Helm of Contemplation as a shield against psionic attacks (it is Gaze Reflection). His menus now name the glove as the game does, and his two stories say what the items do.
- **[Fixed]** **Alagorn**, asked about clothes when the party carried none, said "no magic clothes", then "Ah, magic clothes", and showed an empty menu. Now he says one thing and the menu matches.
- **[Fixed]** The **Effects screen** showed "(15 CHARGES)" on a magic item's power (Shadowseeker's Detect Invisibility), from a stray byte. Charges now show only for a spell that lasts a number of uses or a timed effect.
- **[Fixed]** A party member cured of poison at a rest (a druid's free Neutralize Poison) still died of the poison: the rest checked for poison before its cures. The cures now come first.
- **[Fixed]** In a busy area, things could stop being drawn (an item dropped, a body, a figure, a doorway), as SSI's own note for Wake of the Ravager describes: the game has 300 picture slots and gave none back until the next area. Once all are taken, a slot nothing uses any more is now reused, so new pictures always show.
- **[Fixed]** After many changes of gear in one area, the figures on the map could vanish (the party's and the monsters'), coming back for a moment when the inventory was opened: the Loader's dressing of the figures filled the game's store of pictures. The Loader now reuses the store's room for the new outfits, so they always show.
- **[Fixed]** The game's **people put on their weapons and armour only at their first action in a fight**: until then they were AC 10, their armour unworn, so an opening blow, a backstab or a first-round hit met none, and their Look box showed no weapon. Now they wear and wield their gear from the moment they're on the map, as the game puts it on. They also wear the cloaks, belts, boots, amulets and up to two rings they carry, which the game never put on: each counts by the same rules as the party's.
- **[Fixed]** **Mirror Image** stopped no weapon blow, and swallowed the caster's own spells (Armor cast on oneself was lost three times in four, an image with it). Now each hit, and each foe's spell aimed at one creature, has a 75% chance to strike an image instead (50% for Reflected Image); spells from your own side always get through.
- **[Fixed]** **Armor** used up two charges for each hit, and one for any spell cast on its wearer, even a friend's Bless. Now one charge for each damaging hit, a weapon's or a spell's.
- **[Fixed]** **Share Strength** left its strength on the one who got it after the power ended. Now it ends on them too.
- **[Fixed]** The preserver's **Dispel Magic** also stopped everyone it caught from casting spells, your own party included. Now it only dispels.
- **[Fixed]** **Cause Serious and Critical Wounds** did 2d9 and 3d9 damage. Now 2d8+1 and 3d8+3, as AD&D has them and as the Cure spells heal.
- **[Fixed]** **Absorb Disease** gave the psionicist 1d6 STR as well (and the STR alone with no disease to take). Now it only takes the disease.
- **[Fixed]** **Bless** and **Aid** left out the wrong allies: the check for an enemy beside each one measured from the wrong place.
- **[Fixed]** **Negative Plane Protection** never stopped anything: it saved as against Vampiric Touch, which allows no save. Now a save against death magic stops an undead's draining touch, and the undead takes 2d6.
- **[Fixed]** **Acid Arrow**'s acid never burned after the hit. Now it does 2d4 at the start of each round it lasts (four rounds for an 11th-level caster).
- **[Fixed]** **Cloak of Bravery**'s +4 on saves against fear never applied. Now it does against Scare, Fear, Cause Fear and Insect Plague, and the new Spook.
- **[Fixed]** A click on a spell's icon on the Effects screen no longer ends the spell by mistake. A psionic power's icon still ends it, as that's how you stop a power.
- **[Fixed]** A **berserk** or **confused** party member could be left fighting for the monsters when it wore off. Now they're back on your side.
- **[Fixed]** A **thri-kreen**'s claws and bite did crushing damage, as the game makes every unarmed attack, so creatures that crushing weapons can't hurt were safe from it. Now they cut.
- **[Fixed]** The **fire elementals**' resistances were the wrong way round. Now the fire elemental needs +2 weapons and the lesser one +1, and neither is hurt by fire.
- **[Fixed]** Monsters' **walls** (Wall of Fire, Ice, Force and the rest) came out a single point. Now they run across the line of fire, four cells long.
- **[Fixed]** Items that raise or lower an **ability score** worked from the backpack as well as worn. Now only while worn. (Found by OpenDS and yuan-ti.)
- **[Fixed]** The **gladiator**'s better AC (1 for every 5 levels) came with no armour on. Now only in armour, as Dark Sun has it. (Found by OpenDS and yuan-ti.)
- **[Fixed]** **Pehtucl's ambush** at the slave pens' fountain sent every Arena Guard and Guard in the pens after the party, from across the map, and a fight in the passage before the fountain could set off the alarm. Now only Pehtucl and the five guards he calls hunt the party, and the fountain masks a guard's yell in that passage too.
- **[Fixed]** An **arrow or sling stone** counted as from behind (+2, the target's DEX and shield lost) by the target's facing, from any distance. Now only melee does; a missile is from behind only as a hidden archer's shot, shown as **unseen**.
- **[Fixed]** **Scare** allowed no saving throw at all, so even a 7th-level fighter was Scared. Now 6th level and up always save, as the game's own code means; below 6th, creatures can't save, but an elf or half-elf priest saves as usual (its rule asked for both races at once: found by yuan-ti).
- **[Fixed]** Creatures that **can't save** (against Chaos, Cloudkill, Scare below 6th level, Color Spray with the manual's spells) saved anyway: the game's comparison read the −100 as a big number. Now they fail, even on a natural 20; any other save still succeeds on a natural 20.
- **[Fixed]** **Psionic Blast**'s wounds are imagined (its victim believes it has lost most of its hit points), but the game took them for good. Now a party member gets them back as the fight ends, and until then a blow that would kill them only knocks them out; they wake with the hit points back.
- **[Fixed]** Thief skills no longer drop for holding a weapon. The game's equipment penalty looked at the hands, quiver and legs, and never at the armour worn.
- **[Fixed]** **DELETE** in the character roster deleted the wrong character when the list was scrolled.
- **[Fixed]** A character not yet played showed 0 in every thief skill.
- **[Fixed]** Once the party has killed **Legcrusher**, **Kurzak** no longer calls for him when they're late for a fight, nor greets them as if he'd brought them, nor speaks of him as still about when asked (Dinos neither): he wonders where his monster trainer has got to.
- **[Fixed]** The **Trustee** in the slave pens could stop on his rounds and stay busy for good, never talking again. Now he walks on, even in a save where he's already stuck, once talked to; and a save made while he was walking no longer leaves him standing still when it's loaded (the same for anyone else who walks rounds of their own).
- **[Fixed]** In a long session the game could stop with **"Out of memory in OEOpenGraph"**: each time the map comes back (after the USE screen, a talk, a menu) it needs a large block of free memory, and little was left over. Part of the game's code and its music now live in upper memory, which leaves about 97 KB to spare with the map up (the original game: 57 KB).
- **[Fixed]** When the game rolls a thief skill for the **whole party** (a trap going off, listening in by a wagon), the first party member always rolled, however poor at it. Now the member with the best chance does.
- **[Fixed]** **Random monsters** came in numbers worked out from the wrong monster, and in some areas could crash the game ("Divide error"). Now the count fits the monster that comes, and the crash can't happen.
- **[Fixed]** Magic items didn't shine in a **shop** (Kalzith's, for one): their glow stood still. Now it moves as it does everywhere else.
- **[Fixed]** The game's Sling +1 had no icon.
- **[Fixed]** The game's **Great Axe +3** had no material at all. It is metal now, as its icon shows: "Metal Great Axe +3".
- **[Fixed]** On the **creation screen** the die raised the class's prime requisite to 17 and every other score to 9 or more, where the manual asks less (a fighter needs only STR 9) and, for some classes, more of other scores (a druid CHA 15, a ranger STR and DEX 13). Each class's least is now the manual's, and a multiclass character's the highest of their classes'.
- **[Fixed]** A class whose **prime requisites are all 16 or more** gets the **10% more XP** the manual promises, which the game never gave: a fighter with STR 16, a ranger with STR, DEX and WIS 16. A character of several classes gets 10% for each such class, divided by the classes. The Loader adds it as each award comes.
- **[Fixed]** A character's **most PSP** took the WIS bonus from whatever the creation screen last held (in play, a stray byte), and its bonus tables ran out at 22: INT 22 gave nothing, INT 23 and up 20 too many, WIS 23 and up none. Now each comes from the character's own score, on to 25. (Found by yuan-ti.)
- **[Fixed]** A fight's **music** took its level from the wrong creature for every one but the region's first. (Found by yuan-ti.)
- **[Fixed]** **View Character** showed one or two more damage than a non-magical wooden, bone, stone or obsidian weapon does: it left out the weaker material (2 for wood, 1 for the others). It now matches the inventory and the fight.
- **[Fixed]** A **hasted** or **slowed** character's damage lines (the inventory, View Character) showed their attacks a round as if they were neither. Now Haste doubles them and Slow halves them there (`0.5x1D8`), as in the fight itself.
- **[Fixed]** An archer's pointer showed "can't shoot" after a shot that killed, with shots left (a click still shot). Now it shows "can't" only once every shot of the round is made.
- **[Fixed]** **Slay Living**'s description said a creature that saves takes 3 to 17; the game does 2 to 16 (half of 4d8). It says so now.
- **[Fixed]** Three of the game's script bugs: in **Darkhold** the portcullis guard stopped fighting back when attacked and three creatures lost their look text; the **Lava Rifts** ranger's trigger ran the hermit's talk (endless, with a second Iron Necklace); and **Linara** in Gedron, after the extract, ended her talk with no menu, so Jasmine's spellbook never came up.
- **[Fixed]** A ranger could never read the tracks around the **Wagon Train's bodies**: the check found no ranger, tested the wrong thing for its level, and rolled the wrong way round. Now a ranger reads them on a d20 under its WIS (more at higher levels), for XP. (Found by yuan-ti.)
- **[Fixed]** The slave pens' **sewer grate** never offered "hack the lock off", and a hack that worked left it shut. Now a member with a weapon in hand can hack it open, half the time (always with Bloodwrath). A failed hack said the weapon broke but kept it: now a weapon that can break in a fight (plain wood, bone, stone or obsidian) is lost, and a metal or magic one rings off the grate unharmed. An attack on the grate always broke its lock: now it takes a Strength roll, as ripping it open does. (Found by yuan-ti.)
- **[Fixed]** The **Rebel Mindhome** in Undermountain gave its 5000 XP for the spiders again at every talk once they were dead. Now once. (Found by yuan-ti.)
- **[Fixed]** The **messenger in region 9**, who comes with men bursting from the sand once the elves have left, came only if the party left the region and came back. Now he comes. (Found by OpenDS and yuan-ti.)
- **[Fixed]** The **Draj serf**, left far behind on the way to region 10, stayed without his orders and gave a second obelisk gem when talked to again. Now he comes along. (Found by OpenDS and yuan-ti.)
- **[Fixed]** Lines that depend on the active member's **race or sex** always took them for a man of no race: a halfling is now greeted as a fellow halfling, a woman told "only a mad woman would think of fighting Draj", a thri-kreen hears the bell the mastyrial hears near Demothi's camp. (The halfling's found by yuan-ti.)
- **[Fixed]** A preserver or psionicist with another class couldn't claim to have scried the **haystack** or read the man's thoughts, and the cave guide told even a dwarf or halfling to "go bother someone your own size". **Dagolar's slime book** counted a fighter's or an air cleric's training as magical but not an earth, fire or water cleric's or a druid's: now any cleric, druid, preserver or psionicist can read it.
- **[Fixed]** Cilla, an elf in the ready-made party, was drawn with the half-elf woman's figure; she looks like an elf now (a switch keeps the game's figure).

**Rules the game got wrong** are fixed too. Each is tagged **[Fixed]** under its own heading above and has a switch, on by default, for anyone who wants the game's own rule: the saving throws against spells and the doubled d20 against fire, cold and electricity, two weapons, warriors' attacks, acid on armour and held targets (Combat); class restrictions, multiclass hit points, the class tables, rangers' spells, dual-classing, preservers' learning from scrolls, CON's regeneration and poison saves (Classes and Kits); spells, psionics and monsters as the manual describes them (Turn Undead by AD&D's table with them), spells rolling to hit and Enlarge's dice (Magic and Psionics); and thief skills and backstabs (Improved Thieving). The other rule changes are the mod's own choices, not corrections, and stay **[Changed]** or **[New]**: helms' AC, resting, the XP level cap, hit dice rolled twice, creation scores as rolled, half-giants' two-handed weapons, creature size, cahulaks, a thri-kreen's extra chatkcha throw, and ages.

## Your Saved Games

**You don't need to start a new game for these fixes.** They're in the patched game and the Loader, not in your saves, so they work from the moment you load. The fixes stop the old bugs from happening, but don't undo what they already did to a save.

**A save isn't for an older version** where a release changed what a save holds: 2.13.0, 2.13.2 and 2.14.0 did, so a save made with one of them or later doesn't load in the versions before it. Older saves load in newer versions as they are.

**A new game is still the way to see all of the mod.** Kits, STORE and RECALL and fuller starting gear come with characters made with the mod, and much of the new content (Kalzith, Semyon, the vulture, the new items in the slave pens) is in the game's first areas. The new and changed gear the game's people carry and its chests hold comes only in areas the save hasn't been to: where the party has been, they keep what they had. A save made with the original game loads and plays with every fix and rule change, but its characters have no kits, and what it has already been through stays as it was. What else an older save keeps is in the README's [saved games](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/README.md#updating-backups-saved-games-and-the-loaders-files).
