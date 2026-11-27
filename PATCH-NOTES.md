# Obsidian Edition: Changes from the Original Game

*A Dark Sun: Shattered Lands mod · Current version 2.19.2 · What the mod adds and changes, and its main bug fixes*

Obsidian Edition is a free mod for the GOG release of Dark Sun: Shattered Lands. It shows the rolls the game keeps hidden, brings its rules closer to AD&D 2nd Edition, adds kits, weapons, magic items and people to Athas, dresses the party in what they wear, and fixes bugs left over since 1993. You start the game with the Loader, which loads the mod with your options and logs every roll as it happens. The new content and a few rules are switchable, the game's own files are never touched, and your saves stay where they are.

**Download:** https://github.com/daaki85/darksun-obsidian-edition/releases/latest

*These notes describe version 2.19.2, and on GitHub any later change not yet in a release; the [changelog](https://github.com/daaki85/darksun-obsidian-edition/blob/main/CHANGELOG.md) says which pull request brought each one, and each version's [release notes](https://github.com/daaki85/darksun-obsidian-edition/tree/main/release-notes) what it changed from the one before.*

Each release also has these notes as a web page, [`patch-notes.html`](https://github.com/daaki85/darksun-obsidian-edition/releases/latest/download/patch-notes.html), with a button that copies them as Markdown for forums.

## At a Glance

- **Every hidden roll shown.** The Loader's dice log writes each attack, saving throw, check and creation roll as it happens, with the number it needed and where each bonus came from. A combat log in the game (**L**) shows the rolls on the map.
- **Rules closer to AD&D 2nd Edition.** Saving throws, weapon specialization, two weapons, thief skills, class restrictions and the class tables as the books have them; spells, psionics and monsters as the manual describes them.
- **More to choose and find.** Three kits for each class ([every kit](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/KITS.md)), twenty-two new magic weapons and more new magic and plain items ([every item, and where it is](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/ITEMS.md)), and new people and an arena bout in the game's first areas.
- **The party as it is dressed.** The figures show the gear they wear, magic gear glows on them, and elves have pointed ears.
- **Quicker play.** Keys to choose a target, loot a body and sell plain gear, quick saves and autosaves, 40 save slots, a faster default speed, and no copy protection.
- **Bugs fixed.** The main fixes are under [Bug Fixes](#bug-fixes); every one, with what the game did, is in [the game's bugs, fixed](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/GAME-BUGS.md).
- **Wake of the Ravager too.** The sequel starts from the Loader with most of the mod, and your party can go on into it ([Wake of the Ravager](#wake-of-the-ravager)).
- **Your choice.** The new content, and a few rules, have a switch in the Loader's Options; the rest is always on. Shattered Lands' own files are never touched, and saves made with the original game load; Wake of the Ravager's saves are converted for the mod, a copy of each kept (see [Your Saved Games](#your-saved-games)).

Each change is tagged. **[Fixed]** is a bug of the game, or a rule it got wrong against its own manual or AD&D: these are always on, with no switch. **[Changed]** and **[New]** are the mod's own choices. Every change is told in full in [Features and rules](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/FEATURES.md), which the links below go to.

## In the Game's Screens

- **[New]** A combat log in the game: **L** on the map shows every roll in the Loader's colours, at one of three levels of detail, in a panel that scrolls back, shrinks to a line or filters ([the combat log](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/FEATURES.md#the-combat-log-in-the-game)).
- **[New]** Out of a fight, the panel's top line shows the game's time, `Day 47, 14:20`, or in the arena how many arena fights the party has had.
- **[New]** Names over figures: a spell's name over its caster, "Miss" over anyone missed, "Armor: 7 left" as a spell's charge is used, "Arrows: 17 left" over an archer ([names over figures](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/FEATURES.md#names-over-figures)).
- **[New]** **The chance to hit, before the swing**: with an enemy chosen with Tab, the dice log and the combat log's header say what the d20 must show and the chance (`needs 14+ (35%)`); rest the pointer on an enemy and the number floats over it ([the chance to hit](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/FEATURES.md#the-chance-to-hit-before-the-swing)).
- **[New]** **Squares in reach**: on a party member's turn a small cross marks every square one click can still walk to, counted by the game's own rules; **R** hides and shows them ([squares in reach](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/FEATURES.md#squares-in-reach)).
- **[New]** **Hold Alt** on the map, out of a fight: a gold ring under every door, chest, body, item and person in view that a click does something with, and the names of those nearest the pointer ([showing what can be used](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/FEATURES.md#showing-what-can-be-used-alt)).
- **[New]** The inventory screen and View Character show THAC0, all five saves, the THAC0 with each weapon, DEX's adjustments, a thief's skills and the age ([THAC0, saves and thief skills](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/FEATURES.md#thac0-saves-and-thief-skills)).
- **[New]** The creation screen shows the THAC0 (`THAC0: M18 R19`), changing with STR, DEX and the kit, and the starting age ([the creation screen](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/FEATURES.md#the-creation-screen)).
- **[New]** The USE screen shows the spell slots left at the level on show, and the most you get after resting ([spell slots](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/FEATURES.md#spell-slots-on-the-use-screen)).
- **[New]** In a fight, the Look box shows a monster's hit points, AC, THAC0, alignment, magic resistance and chief defence ([the Look box](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/FEATURES.md#what-hurts-a-monster-the-look-box)).
- **[New]** Item boxes show a wand's charges, a cloak's, boots' or belt's bonus to thief skills, and a plain weapon's material penalty (`Hit -2` for obsidian) ([charges in item boxes](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/FEATURES.md#charges-in-item-boxes)).
- **[New]** The Effects screen lists kits and weapon specs, a spell's charges left, and what Enlarge, Barkskin and the like give ([the Effects screen](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/FEATURES.md#the-effects-screen)).
- **[New]** Reading a scroll tells you what happened (YOU LEARN THE SPELL, YOU CAN NOT READ THE SCROLL...) where the game showed nothing ([what a scroll says](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/FEATURES.md#what-a-scroll-says)).

## Combat

- **[New]** **Weapon specialization**: a fighter specializes in one weapon spec (+1 to hit, +2 damage, 3/2 attacks), with mastery at 5th level and grand mastery at 9th; gladiators take two, then more; rangers and three kits gain expertise ([weapon specialization](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/FEATURES.md#weapon-specialization)).
- **[New]** **Twenty-two weapon specs**: six more for the weapons taken from Wake of the Ravager (two-handed sword, lotulis, double spear, trikal, javelin, darts), on a weapon window of four rows; a specialist throws the javelin and darts faster ([the twenty-two weapon specs](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/WEAPON-SPECS.md#the-twenty-two-weapon-specs)).
- **[Fixed]** Warriors attack at AD&D's plain rate outside their specializations *(was 3/2 with any weapon)*; specialists shoot missiles faster; the weapons spells make count as their weapon.
- **[Changed]** Every thri-kreen throws a chatkcha once more a round, AD&D's 2/1 for its own weapon *(was at the weapon's rate)*.
- **[Fixed]** Spells are saved against with the spell save *(was petrification/polymorph for almost every spell)* ([spell saves](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/FEATURES.md#spells-saved-against-with-the-spell-save)).
- **[Fixed]** Against fire, cold and electricity, DEX helps you dodge, −5 to +6 *(was a doubled d20)*: at DEX 12, a 35% chance to save against a Fireball *(was 70%)* ([DEX, not a doubled d20](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/FEATURES.md#fire-cold-and-electricity-dex-instead-of-a-doubled-d20)).

> *Developers' Notes: The doubled d20 isn't in the manual or in AD&D. It made most enemies shrug off a Fireball. Nimble targets still dodge; slow ones now burn.*

- **[Fixed]** Two weapons cost −2 and −4 to hit, less with high DEX, and the off hand attacks once a round *(was no penalty, and the full rate in each hand)*; rangers and some kits are exempt ([two weapons](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/FEATURES.md#two-weapons)).
- **[Fixed]** A blow on a held or Out Cold creature hits automatically, for normal damage *(was a roll to hit, and double damage)* ([held targets](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/FEATURES.md#held-targets)).
- **[Changed]** Helms give AC 1 *(was 0)* ([helms](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/FEATURES.md#helms-give-ac-1)).
- **[Changed]** Rings and cloaks of protection follow AD&D: two rings don't stack, and neither works with magical armour (a cloak nor with metal armour or a shield) ([rings and cloaks](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/FEATURES.md#rings-and-cloaks-of-protection)).
- **[Fixed]** Acid lets each item save by its material *(was any non-magical armour destroyed)* ([acid](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/FEATURES.md#items-saving-against-acid)).
- **[Changed]** Half-giants can hold a two-handed weapon in one hand ([half-giants](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/FEATURES.md#half-giants-two-handed-weapons)).
- **[New]** **Creature size**: a large target takes AD&D's damage for large targets (a long sword 1d12), and Hold and Charm Person don't work on it *(the game keeps no sizes)* ([creature size](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/FEATURES.md#creature-size)).
- **[Changed]** The pick is the footman's pick, 1d6+1 (2d4 large), and the axe the battle axe, 1d10 large *(was the horseman's pick, and an axe 1d8 against any size)*.
- **[New]** **Weapon traits**: cahulaks strike once more a round and can tangle a foe ([cahulaks](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/FEATURES.md#cahulaks)); the staff sling throws stinkpots that nauseate ([stinkpots](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/FEATURES.md#staff-sling-stinkpots)) *(was a plain 1d4 shot)*.
- **[New]** **Polearm reach** (with Weapon traits): a polearm held alone strikes a foe two squares away, for the party and its foes alike ([polearm reach](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/FEATURES.md#polearm-reach)).
- **[New]** **The sequel's weapon traits** (with Weapon traits): the lotulis' and double spear's last swing of a round strikes a second foe beside the wielder, and a trikal hit can trip a man-sized foe, which loses its next turn; the trikal reaches two squares as a polearm does ([lotulis and double spear](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/FEATURES.md#lotulis-and-double-spear), [trikal](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/FEATURES.md#trikal)).

## Classes and Kits

- **[Changed]** Levels stop at **749,999 XP**, shared out between a character's classes, instead of 9th level, and XP stops there too *(was 9th level for every class, and XP counting on to 2,000,000,000)* ([level cap](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/FEATURES.md#level-cap-by-xp)).
- **[Changed]** Creation keeps what the die rolls: the six scores never add up to more than it gave, and hit points stay as rolled *(was any score clicked up to its most)* ([as rolled](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/FEATURES.md#scores-and-hit-points-as-rolled)).
- **[New]** **STORE** and **RECALL** on the creation screen, as in Baldur's Gate ([STORE and RECALL](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/FEATURES.md#store-and-recall-on-the-creation-screen)).
- **[Fixed]** Class restrictions hold: the game's own item lists still need only one of a character's classes, and AD&D's limits on armour, shields and weapons hold for every class, the strictest winning *(was the game's lists alone)*; thieves wear light armour, a multiclass preserver can't cast in armour; an air cleric uses daggers and cahulaks ([class restrictions](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/FEATURES.md#class-restrictions)).
- **[New]** New characters start with fuller gear: a weapon they can use, a sling, leather armour where allowed, and their kit's own weapons ([fuller starting gear](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/FEATURES.md#fuller-starting-gear)).
- **[Fixed]** Multiclass characters gain hit points as in AD&D, CON's bonus on every hit die ([multiclass hit points](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/FEATURES.md#multiclass-hit-points)).
- **[Changed]** Hit dice are rolled twice and the better kept, at creation and every level ([hit dice](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/FEATURES.md#hit-dice-the-better-of-two)).
- **[Fixed]** Experience, priests' THAC0, saving throws and spell slots follow AD&D's tables: a gladiator needs 2,250 XP for 2nd level *(was 2,000)*, a 12th-level fighter saves at 7/9/8/8/10 *(was 11/11/11/13/11 from 10th level on)*, a psionicist by Dark Sun's own table *(was a thief's)* ([class tables](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/FEATURES.md#adds-class-tables)).
- **[Fixed]** A ranger's spells last and hurt by its level minus 7 *(was its full level)* ([rangers' casting level](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/FEATURES.md#rangers-casting-level)).
- **[New]** **Ages** from the Dark Sun rules' tables: age changes the scores, a character can die of old age, and magic (Haste) ages them ([ages](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/FEATURES.md#ages-and-magical-aging)).
- **[Fixed]** CON 20 and up regenerates at AD&D's rate *(was every 5 minutes)*, and a dwarf's or halfling's poison save gets its racial bonus only ([CON](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/FEATURES.md#con-as-in-add)).
- **[Fixed]** Dual-classing from 3rd level, with every prime requisite at 15 and 17 *(was 2nd level and one score)* ([dual-classing](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/FEATURES.md#dual-classing-as-the-manual-has-it)).
- **[Fixed]** Preservers' INT sets their chance to learn a spell from a scroll and the most they know ([preservers' INT](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/FEATURES.md#preservers-int)); new preservers choose their first spells.
- **[New]** **Psionic powers picked at creation** on the game's own window *(was the same powers for every character of a discipline)* ([psionic powers](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/FEATURES.md#psionic-powers-at-creation)).

**Kits**

- **[New]** Three kits for each class and thirteen for two or three classes taken at once, 37 in all, each giving something and costing something; one kit a character ([kits](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/FEATURES.md#kits)). [The Kits page](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/KITS.md) has each one's gains and costs:
- **Warriors**: the fighter's Myrmidon, Sentinel and Ravager; the gladiator's Arena Champion, Twin-blade and Brute; the ranger's Stalker, Justifier and Seeker ([fighter](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/KITS.md#fighter-kits), [gladiator](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/KITS.md#gladiator-kits), [ranger](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/KITS.md#ranger-kits)).
- **Priests**: the cleric's Elementalist, Healer and Crusader; the druid's Grove Warden, Lifebinder and Wanderer ([cleric](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/KITS.md#cleric-kits), [druid](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/KITS.md#druid-kits)).
- **Preservers**: the Scholar, Battle Mage and Arcanist ([preserver](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/KITS.md#preserver-kits)).
- **Psionicists**: the Mind Bender, Mind Warrior and Kineticist ([psionicist](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/KITS.md#psionicist-kits)).
- **Thieves**: the Swashbuckler, Assassin and Shinobi, a Veiled Alliance thief who casts preserver spells of its own ([thief](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/KITS.md#thief-kits)).
- **More than one class**, each for one race: Battle Dancer, Shadowblade, Military Scout, Wilderness Avenger, Rescuer, Ghetto Fighter, Wayfinder, Spellarcher, Titan Mind, Poisoner, Spirit Caller, Wasteland Seer and Wild Fury ([multiclass](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/KITS.md#multiclass-kits)).
- **[New]** The game's own party has features of its own: Gerakis fights wild, K'ratchek casts as a Wasteland Seer, Cilla hides as well in the sun, and Cermak is an Arcanist ([the game's own party](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/FEATURES.md#the-games-own-party)).

> *Developers' Notes: Each kit is built into the game's own code, so it works everywhere the game checks: THAC0, spell slots, hit dice, PSP costs, attacks a round and what you may hold. The Kits page has all 37, with a short description of who takes each one on Athas.*

## Magic and Psionics

- **[Fixed]** **Spells, psionics and monsters as the manual describes them**: their saves, durations, damage and effects, from Bestow Curse to Biofeedback, and monsters' poisons and drains ([as the manual describes them](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/FEATURES.md#spells-and-psionics-as-the-manual-describes-them)).
- **[Fixed]** **Turn Undead** follows AD&D's table: turned undead flee, the strongest results destroy, and a failure can't be retried that fight *(was destroyed or nothing, as often as the priest liked)*.
- **[Fixed]** Monsters' hit dice count as their level for saving throws *(was level 0 for a monster with no class)*.
- **[Fixed]** **Spells roll to hit**: the missile spells and the touch spells cast at an enemy roll against AC, and a miss does nothing *(was every one landing)* ([spells roll to hit](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/FEATURES.md#spells-roll-to-hit)).
- **[Changed]** **Resting** heals by the priests' spells left and a night's natural healing *(was every member healed to full)* ([resting](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/FEATURES.md#resting-as-in-add)).
- **[Fixed]** **Enlarge** makes only the weapon's dice bigger, STR and magic added after *(was the whole damage, STR included)* ([Enlarge](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/FEATURES.md#enlarge-multiplies-the-weapons-dice-only)).
- **[New]** Six new wizard spells, each with its icon and description: Erdlu Claw, Fogbolt, Reflected Image, Spook, Friends and Cat's Grace ([new wizard spells](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/FEATURES.md#new-wizard-spells)).
- **[New]** Ten 6th-level priest spells for clerics and druids from 11th level: Heal, Harm, Restore Youth, Blade Barrier, Wall of Thorns, Sunstroke, Fire Seeds, Heartseeker, Water of Life and Whirlwind ([6th-level priest spells](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/FEATURES.md#6th-level-priest-spells)).

## Improved Thieving

- **[Fixed]** Thief skills follow AD&D's table by level, with Dark Sun's race and DEX adjustments, none above 95 *(was a 3rd-level elf with move silently 66)* ([thief skills](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/FEATURES.md#thief-skills-from-adds-table)).
- **[New]** Thieves **hide in shadows and move silently** in a fight to backstab, halved in daylight; rangers to attack from behind *(was a backstab only on a target facing away)* ([hiding](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/FEATURES.md#hiding-in-shadows-to-backstab)).
- **[Fixed]** A **backstab** multiplies only the weapon's dice, on the round's first attack only *(was the whole damage, STR included, on two attacks)*.
- **[Fixed]** A thief's **later attacks in a round after a backstab** from hiding count as from behind only when the thief is behind the target *(was the first attack's from behind kept for the round: the game's attack routine never clears it)*.
- **[New]** **Picking pockets** with a button on the USE screen: any thief can try, and a purse holds ceramic pieces by the thief's level ([picking pockets](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/FEATURES.md#picking-pockets)).
- **[Changed]** A thief who fails a lock, or is caught at a pocket, tries that one again only after a level *(was again and again; caught, never)*.
- **[Changed]** A thief beside any square of a big creature can't hide there *(was its one square only)*.
- **[New]** A worn cloak adds 10 to hiding, boots 10 to moving silently and a belt 5 to picking pockets and locks; a soft breath sounds as a thief hides, a purse's jingle at a picked pocket.

## Items

- **[New]** Twenty-two new magic weapons, each with its own icon and most with a story from the game's item sage, from Greenbright to Skycutter ([where each is](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/ITEMS.md#every-magic-item)).
- **[Changed]** The Elven Leader's gift is a **Gythka +2** *(was +1)*; the elven caravan's buried cahulaks are **Cahulaks +2** *(was +1)*; the game's unplaced **Polearm +1** is in the world.
- **[New]** Magic armour and worn items: Bracers of Defense, the Ashen and Veiled Robes, the Warden's Plate, Inixhide, rings and a cloak of protection, Elvenkind cloak and boots, Boots of Speed, Arrowbane, the Sunking Crown, two girdles, an Amulet of Magic Resistance and two shields.
- **[New]** Other magic: a Tome of Understanding, Kalzith's six scrolls, defilers' scrolls and a Spellarcher's spell arrows ([new items](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/FEATURES.md#new-items)).
- **[New]** The plain weapons the game never had, sold by merchants: short swords, axes, great axes, daggers, maces, a metal pick and polearm, metal and obsidian cahulaks; and a Spellarcher's Fine Bow, +1 to hit but not magic.
- **[New]** **Six of Wake of the Ravager's weapons** the game has none of: a two-handed sword, the lotulis, the double spear and trikal (gladiators only), the javelin and darts, sold in Teaquetzl and Kel's caravan and carried by people of the like; metal and obsidian ones, a bone great sword, and magic ones along the way, from the Double Spear +1 to the Great Sword +3 ([weapons](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/ITEMS.md#weapons)). The sequel's net is left out.
- **[Changed]** The game's bone scale armour set is complete, and its unplaced leather helm is worn by Kurzak and Scar.

## World

- **[New]** **Kalzith**, a defiler slave who scribes spell scrolls by night, with a face of his own ([Kalzith](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/FEATURES.md#kalzith)).
- **[New]** More of **Semyon**'s story, and Thornwall on the slave pens' weapon rack once he has told it ([Semyon](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/FEATURES.md#semyon)).
- **[New]** **Pehtucl's chest**, locked and trapped, holds a Cloak of Protection +1.
- **[New]** A last arena bout: once Scar dies, six champions from a distant arena come to test the new king ([the champions' bout](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/FEATURES.md#the-champions-bout)).
- **[New]** Legcrusher, sent for a party out by the fountain, finds the cells empty and attacks alone *(was his warning, as if they were in the cells)* ([Legcrusher](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/PEOPLE.md#legcrusher-at-the-fountain)).
- **[New]** A use for the cooked vulture: share it with the pens' cook for a full rest and 100 XP each ([the vulture](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/FEATURES.md#the-cooked-vulture)).
- **[Fixed]** Every thri-kreen leaves a thri-kreen's body *(was a human's Dead Body)*.
- **[New]** Merchants give the leader a discount for high CHA, 5% at 18 to 40% at 25 ([CHA at shops](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/FEATURES.md#the-leaders-cha-at-shops)).
- **[Changed]** Merchants pay 60% of an item's price *(was all of it)*, and keep the magical items you sell, to buy back *(was destroyed)* ([buying back](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/FEATURES.md#buying-back-magical-items)).
- **[New]** Scar and his henchmen fight with cahulaks and great axes, and people who struck with their fists carry weapons and armour that suit them.

## Graphics

- **[New]** The party's figures show the weapons, shields, armour, helms and cloaks they wear, walking and fighting ([what the party wears](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/FEATURES.md#what-the-party-wears)).
- **[New]** **Class outfits**: each party member is dressed for their class before any gear goes on, the mage in a plum mantle, the thief hooded, the psionicist in teal, and every other race in an outfit for its whole class combination (thri-kreen keep the game's figure) ([class outfits](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/FEATURES.md#what-the-party-wears)).
- **[New]** Magic gear glows on the figures, in the colour nearest the item's icon, and twenty of the game's still magic icons shimmer ([icons](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/FEATURES.md#magic-items-icons)).
- **[New]** Elves have pointed ears, half-elves no longer look like humans, and hair greys with age ([elves and half-elves](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/FEATURES.md#elves-and-half-elves)).
- **[New]** Every figure casts a soft shadow, walkers kick up dust, and the hidden and invisible are drawn half see-through ([shadows](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/FEATURES.md#shadows)).
- **[New]** The 6th-level priest spells that stay on the map have pictures of their own, some from Wake of the Ravager when installed ([spells on the ground](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/FEATURES.md#spells-on-the-ground)).

## Quality of Life

- **[New]** **Tab** chooses the nearest enemy and **Enter** attacks it ([Tab and Enter](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/FEATURES.md#choosing-an-enemy-tab-enter-and-the-rings)); the mouse wheel pressed and dragged scrolls the map.
- **[New]** **T** takes everything from a body or chest, **Shift+T** all but plain weapons *(was a click and a drop each)* ([looting](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/FEATURES.md#looting-a-body-t-and-shiftt)).
- **[New]** **S** in a shop sells the plain gear in the backpack on show *(was a click each)* ([selling](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/FEATURES.md#selling-plain-gear-s)).
- **[New]** **M** opens and closes the overhead map; **U** and **I** close the USE and inventory screens.
- **[New]** **F5** saves at once, with no window, and **F9** opens the load window on those saves; the game also **saves by itself** on coming into another area and after a fight. All on a fifth page of the save window, **QUICK**, which keeps the last five of each ([quick save and autosave](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/FEATURES.md#quick-save-quick-load-and-autosave)).
- **[Changed]** **F10**, the game's key that takes a move back in a fight, gives the walk back after the last step too, and leaves a held or stuck character where it is *(was the character put back, unable to walk, a held or stuck one too)* ([F10](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/FEATURES.md#f10-takes-a-whole-move-back)).
- **[Changed]** A game starts and loads with the whole party on the map, and stays so after a fight *(was the leader alone)* ([the whole party](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/FEATURES.md#the-whole-party-in-view)).
- **[Changed]** In a fight the view stays put while a figure walks *(was following each one near the edge)*.
- **[Changed]** The pointer shows in the intro and scenes, starts in the middle, keeps its place and moves at the desktop's speed ([the pointer](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/FEATURES.md#the-pointer-in-scenes-and-where-it-starts)).
- **[Changed]** 40 save slots on four pages *(was 10)*, each kept under its name too, and 29 stored characters *(was 19)* ([more saves](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/FEATURES.md#more-saves)).
- **[Changed]** The game runs faster than with GOG's settings, Fastest by default, and the party keeps its walking pace with the shadows and dust drawn ([game speed](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/FEATURES.md#game-speed)).
- **[Changed]** More memory to spare with the map up, for the mod's own needs: about 97 KB *(the original game: 57 KB)*, with part of the game's code and its music buffer in upper memory, so a long session is less likely to stop with "Out of memory in OEOpenGraph".
- **[New]** Crash, freeze and item reports, and a warning in the dice log before memory runs out ([reports](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/README.md#crash-freeze-and-item-reports)).
- **[New]** The game's window at its own size, double, triple or quadruple, or full screen.
- **[New]** **The picture**: plain, scanlines, TV or hard-edged pixels at any size; and **the music** sent to any MIDI device of Windows' (a soundfont synthesizer, an MT-32 driver) ([picture and music](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/FEATURES.md#picture-and-music)).
- **[New]** **DOSBox-X as the engine**: the game in DOSBox-X in place of GOG's DOSBox 0.74 whenever there is one (it comes with the mod on Windows; on Linux and macOS choose your own on the Options tab). It gives the mod 64 KB more upper memory to work with; on Linux the whole mod runs without root, and the music can play through a soundfont file of yours. GOG's DOSBox can still be chosen ([the engine](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/FEATURES.md#the-engine-gogs-dosbox-or-dosbox-x)).
- **[Changed]** No more copy protection: the dragon asking for a word from the manual never comes ([no manual check](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/FEATURES.md#no-manual-check)).

## The Loader

- **[New]** The Loader starts the game with the mod and your options, and stays open while you play ([the Loader's window](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/README.md#the-loaders-window)).
- **[New]** **The dice log**: every roll as it happens, with what it needed, its chance and every bonus, a fight's summary at its end, and the game's own choices ([the dice log](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/DICE-LOG.md)).
- **[New]** **Characters**, **Spells** and **Dialogue** tabs: each member's sheet with more than the game shows, every spell's numbers, and everything said ([Characters](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/README.md#the-characters-tab)).
- **[New]** **The Journal tab**: everything said and every reward, by day and area, kept on disk and following the save you load; and **Quests**, open and finished, read from the game's own flags ([the Journal tab](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/README.md#the-journal-tab)).
- **[New]** **Find** in the dice log and the dialogue (Ctrl+F).
- **[New]** The Loader can run the game as **Dark Sun Recompiled**, where it is installed ([other ways to start](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/README.md#dark-sun-recompiled)).
- **[New]** **Play Shattered Lands** and **Play Wake of the Ravager** at the top of the window start either game with the mod, and **Take the party to Wake of the Ravager...** carries a save's party across ([Wake of the Ravager](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/FEATURES.md#wake-of-the-ravager)).
- **[New]** **Options**: switches for the new content and a few rules (hit dice, half-giants' weapons, helms, kits, starting gear), the combat log's level and the red ring, all on by default, and **Restore defaults** sets them back; the rest of the mod is always on.
- **[New]** **Accessibility**: text up to 2.5 times bigger, every control from the keyboard, 4.5:1 contrast, logs as text ([accessibility](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/README.md#accessibility)).
- **[New]** **The manual in the download**, as web pages that link to each other; the Loader's **Help** button opens it.
- **[Fixed]** The dice log's age for a character being made could differ from the creation screen's **AGE**: it now gives the screen's age, once you press DONE.
- **[Fixed]** On Linux, the Loader's window kept saying "Connected to the game" after a game it hadn't started was closed, with an error in the party table: it now says the game has ended.

> *Developers' Notes: Shattered Lands rolls dice for everything and shows you almost none of it. Fireball victims kept saving and nobody knew why (the game doubles the d20 against fire). The Loader started as a way to see those numbers. Once we could see them, we started fixing them.*

## Wake of the Ravager

The sequel, started from the Loader when it is installed (GOG sells it with Shattered Lands), has most of the mod too ([everything ported](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/FEATURES.md#wake-of-the-ravager)); what it lacks is on [the kits page](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/KITS.md) and [the game's bugs](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/GAME-BUGS.md#in-wake-of-the-ravager).

- **[New]** **Your party goes on**: a Shattered Lands save's party comes across with every item and its effects, kits, weapon specs, spells and ages, after 3 to 12 months between the games ([taking the party](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/FEATURES.md#taking-the-party-to-wake-of-the-ravager)).
- **[New]** The mod's rules, screens and keys in the sequel: the dice log and combat log, weapon specialization in all twenty-two specs, the kits, AD&D's thieves, stealth and picking pockets, two weapons, Tab and Enter, quick saves and autosaves, looting and selling keys, STORE and RECALL, and the Loader's Dialogue and Journal tabs.
- **[Changed]** **Levels to 30th**: a level cap of **5,625,000 XP** shared between a character's classes *(was a stop at 15th)*, with AD&D's tables past the sequel's 20th; most characters of three classes reach 15th, a fighter alone 30th ([the levels](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/PLAYER-GUIDE.md#in-wake-of-the-ravager)).
- **[New]** **Kits and weapon specs past 13th level**: a gladiator picks a weapon spec more every 4 levels past 9th, a fighter a second at 13th that goes on to grand mastery, and the kits' tables go on ([past 13th level](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/WEAPON-SPECS.md#past-13th-level)).
- **[New]** The six new wizard spells, learnt and cast as in Shattered Lands, their spellbooks sold by Notaku in Tyr.
- **[New]** Starting gear fitted to each class and kit, a warrior's weapon a +1 of its first weapon spec, and the sequel's own party fitted to the rules.
- **[New]** Shadows, dust, see-through figures and shining magic items, as in Shattered Lands.
- **[New]** **The kits, nearly all whole**: their spells and powers too (casting levels, cures, the spells each knows, PSP costs, hit dice), the Shinobi's own wizard spells, the Poisoner's poison on each hand's first hit, and the Spellarcher's spell arrows made on the USE screen (with Shattered Lands installed too, for their pictures); the Scholar's extra spells still to come ([which kits work there](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/KITS.md#in-wake-of-the-ravager)).
- **[New]** **Weapon traits** there too: the lotulis's and double spear's second foe, the trikal's trip and its reach of two squares; the dice log says when an effect starts and ends, PSP spent and regained, and an ability score changing; a lock a thief failed stays shut to it until it gains a level.
- **[Changed]** **The sequel's roster and saves are converted** for the mod at each start from the Loader, each file kept first as `NAME.42H`; converted, they load only from the Loader until turned back ([how](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/FEATURES.md#wake-of-the-ravager)).
- **[Fixed]** The sequel's items weigh what they do in Shattered Lands *(71 of its 102 kinds weighed nothing)*, so two heavy weapons can't be held together and pockets go by weight.

## Bug Fixes

The main fixes; every bug of the original game the mod mends, with what the game did, is in [the game's bugs, fixed](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/GAME-BUGS.md). Many were found by yuan-ti and the OpenDS project.

**Spells and psionics**

- **[Fixed]** **Mirror Image** stopped no blow and swallowed the caster's own spells; **Armor** spent two charges a hit, and one for a friend's Bless.
- **[Fixed]** **Share Strength** stayed after the power ended; the preserver's **Dispel Magic** stopped everyone casting, your party too.
- **[Fixed]** **Cause Serious and Critical Wounds** did 2d9 and 3d9, not AD&D's 2d8+1 and 3d8+3; **Absorb Disease** gave STR as well.
- **[Fixed]** **Bless** and **Aid** left out the wrong allies; **Negative Plane Protection** and **Cloak of Bravery** never worked; **Acid Arrow** never burned on.
- **[Fixed]** Creatures that **can't save** saved anyway; **Scare** allowed no save at all; **Psionic Blast**'s imagined wounds were taken for good.
- **[Fixed]** A click on a spell's icon on the Effects screen ended it by mistake.

**Fights**

- **[Fixed]** An archer that killed with its **last arrow** lost the rest of its turn, though a shot was still due.
- **[Fixed]** The game's people put on their **weapons and armour only at their first action**: until then they were AC 10. Now from the start, and their worn items count.
- **[Fixed]** A **berserk** or **confused** party member could be left fighting for the monsters.
- **[Fixed]** A **thri-kreen**'s claws and bite crushed, so some creatures were safe from it; the **fire elementals**' resistances were the wrong way round.
- **[Fixed]** Monsters' **walls** came out a single point; an **arrow** counted as from behind by the target's facing, at any distance.
- **[Fixed]** **Random monsters** came in numbers from the wrong monster; a fight's **music** took the wrong level.

**Characters and items**

- **[Fixed]** Items that change an **ability score** worked from the backpack; the **gladiator**'s better AC came with no armour on.
- **[Fixed]** Thief skills dropped for holding a weapon; a party roll of a thief skill always fell to the first member, not the best.
- **[Fixed]** The creation screen's **least scores** were the game's, not the manual's; the **10% more XP** for high prime requisites was never given.
- **[Fixed]** A character's **most PSP** took the wrong WIS bonus, and its tables stopped at 22.
- **[Fixed]** **DELETE** in the roster deleted the wrong character when the list was scrolled; a new character showed 0 in every thief skill.
- **[Fixed]** The **Quicksilver Glove** fought as wood, the **Great Axe +3** had no material, and the Sling +1 no icon.
- **[Fixed]** View Character's damage and a hasted or slowed character's attacks, and an archer's "can't shoot" pointer, were wrong.

**Screens and memory**

- **[Fixed]** In a busy area things stopped being drawn: the game's 300 picture slots are now reused.
- **[Fixed]** **CHOOSE A SPELL** set its icons off-centre above 15 spells; the Effects screen showed stray charges; magic items stood still in a **shop**.

**People and quests**

- **[Fixed]** **Pehtucl's ambush** sent every guard in the pens; **Kurzak's door** could stand open and bar the way; Kurzak still called for a dead **Legcrusher**.
- **[Fixed]** The **Trustee** could stop on his rounds for good; walkers in a save stood still once it was loaded.
- **[Fixed]** **Alagorn** told two items wrong, and showed an empty clothes menu.
- **[Fixed]** The **sewer grate**'s hack, a ranger's **tracking** at the Wagon Train, the **Rebel Mindhome**'s repeated award, the **messenger** and the **Draj serf** (found by yuan-ti and OpenDS).
- **[Fixed]** Lines that depend on the speaker's **race, sex or class** read the wrong record; script bugs in **Darkhold**, the **Lava Rifts** and **Linara**'s talk.
- **[Fixed]** Cilla, an elf, was drawn with the half-elf woman's figure.

**Wake of the Ravager** (started from the Loader)

- **[Fixed]** Most of the fixes above that touch the engine, from Mirror Image and Armor to the picture slots and resting while poisoned; the page of [the game's bugs](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/GAME-BUGS.md#in-wake-of-the-ravager) says which, and which are still to come.
- **[Fixed]** The sequel's own: a new character's **hit points** stayed one a level, its **weapon** started in the off hand, the **message box** never stayed on screen, a **worn item's spell** never ended when it came off, **saving throws** stopped at the table's last row, and the Tyr inn's room never rested.

## Your Saved Games

**You don't need to start a new game for these fixes.** They're in the patched game and the Loader, not in your saves, so they work from the moment you load. The fixes stop the old bugs from happening, but don't undo what they already did to a save.

**A save isn't for an older version** where a release changed what a save holds: 2.13.0, 2.13.2, 2.14.0, 2.15.0 and 2.18.0 did, so a save made with one of them or later doesn't load in the versions before it. Older saves load in newer versions as they are.

**Wake of the Ravager's saves are converted.** Each start of the sequel from the Loader makes its roster and saves hold the Loader's longer character sheet, in the sequel's folder, keeping each file first as `NAME.42H` (a later conversion of the same file replaces that copy). The sequel started by itself can't read them; to play it without the Loader, or before uninstalling, turn them back with the Loader ([how](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/FEATURES.md#wake-of-the-ravager)).

**A new game is still the way to see all of the mod.** Kits, STORE and RECALL and fuller starting gear come with characters made with the mod, and much of the new content (Kalzith, Semyon, the vulture, the new items in the slave pens) is in the game's first areas. The game's people and chests have the new gear only in areas the save hasn't been to. A save made with the original game loads and plays with every fix and rule change, but its characters have no kits. More in the README's [saved games](https://github.com/daaki85/darksun-obsidian-edition/blob/main/obsidian-edition/README.md#compatibility-with-older-saves).
