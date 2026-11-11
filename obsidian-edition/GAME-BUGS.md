# The game's bugs, fixed

*Part of Obsidian Edition's documentation, from [Features and rules](FEATURES.md#the-games-bugs-fixed).
**Spoilers:** some of these name places and people from later in the game, most of them under
[People and quests](#people-and-quests).*

The patched game mends these whatever the Options tab says. The rules the game got wrong, each with
a switch, are [further down](#rules-it-got-wrong-with-a-switch). The script bugs are mended in the
Loader's copy of the game's scripts; many were found by yuan-ti and the OpenDS project
([credits](https://github.com/daaki85/darksun-obsidian-edition#credits)). How the fixes work:
[DEVELOPMENT-CONTENT.md](DEVELOPMENT-CONTENT.md) (the script bugs, the spells, worn items), the
memory fixes in [DEVELOPMENT.md](DEVELOPMENT.md#room-in-the-helper), and the rows' own links.

## Contents

- [Spells and psionics](#spells-and-psionics)
  - [Wrong numbers](#wrong-numbers)
  - [Saving throws](#saving-throws)
  - [Effects that did the wrong thing](#effects-that-did-the-wrong-thing)
- [Fights](#fights)
  - [Sides and blows](#sides-and-blows)
  - [Who turns up, and how](#who-turns-up-and-how)
  - [Resting](#resting)
- [Characters and items](#characters-and-items)
  - [Making and keeping characters](#making-and-keeping-characters)
  - [Thief skills](#thief-skills)
  - [Items](#items)
- [Screens and memory](#screens-and-memory)
  - [Numbers and pointers on screen](#numbers-and-pointers-on-screen)
  - [Pictures and memory](#pictures-and-memory)
- [People and quests](#people-and-quests)
  - [Scripts that stuck, or ran twice](#scripts-that-stuck-or-ran-twice)
  - [Who is talking: class, race and sex](#who-is-talking-class-race-and-sex)
- [Rules it got wrong, with a switch](#rules-it-got-wrong-with-a-switch)
- [Two more, with a switch](#two-more-with-a-switch)
- [Saved games](#saved-games)

## Spells and psionics

### Wrong numbers

| | The game | With the Loader |
|---|---|---|
| **Cause Serious and Critical Wounds** | 2d9 and 3d9 (the Cure spells heal AD&D's 2d8+1 and 3d8+3) | 2d8+1 and 3d8+3 |
| **Slay Living**'s description | Said a creature that saves takes 3 to 17 | Says 2 to 16 (half of 4d8), what the game does |
| A character's **most PSP** (worked out at each level-up check, for every party member) | The WIS bonus read from the creation screen's record, not the character's (in play, any number at all), and the bonus tables too short, so INT 22 gave nothing, INT 23 to 25 20 to 24 too many, WIS 23 to 25 none at all, CON 23 to 25 0 to 2 | Each from the character's own score: CON and INT the score less 15, WIS twice it less 10, on to 25 (found by yuan-ti). The most only ever rises, so a character's may go up once, the next time it's worked out |

### Saving throws

| | The game | With the Loader |
|---|---|---|
| **Negative Plane Protection** | Saved as against Vampiric Touch, which allows no save, so it never stopped anything | A save against paralysis, poison and death, as AD&D's against death magic: saved, the undead's touch is stopped and it takes 2d6 |
| **Scare**'s save | No one saved, of any level (a 7th-level fighter was Scared): its record allowed no save, so the save code's rules for it never ran; and those asked for an elf or half-elf priest as one creature of both races | 6th level and up always save, as the game's code means; below 6th level creatures can't save (whatever the Options: the fix below makes "can't save" fail), but an elf or half-elf priest saves as usual |
| **"Can't save"** (Chaos for all but warriors, Cloudkill on the weak, Scare below 6th level, Color Spray with the manual's spells) | The saving throw compared its total with the number needed unsigned, so the −100 for "can't save" made a total such as −85, read as 171: the creature always saved | "Can't save" fails, even on a natural 20 (the game took a natural 20 as a save before adding anything; the patched game adds the modifiers first: [the game's saving throws](HOW-THE-GAME-WORKS.md#the-games-saving-throws)) |
| **Cloak of Bravery** | Its +4 on saves against fear asked for a mark no spell had, so it never applied | +4 against Scare, Fear, Cause Fear and Insect Plague (and a Cloak of Fear's), and the new [Spook](FEATURES.md#new-wizard-spells) |

### Effects that did the wrong thing

| | The game | With the Loader |
|---|---|---|
| **Mirror Image** (and Reflected Image) | The images stopped no weapon blow, and took a spell for one creature three times in four whoever cast it: Armor cast on oneself was lost, an image with it | Each hit, and each foe's spell for one creature, strikes an image three times in four (Reflected Image's half the time); your own side's spells always get through ([how long it lasts](HOW-THE-GAME-WORKS.md#spells-and-effects)) |
| **Armor** | A charge used each time any spell or blow landed on the wearer, as well as for the damage: two for each hit, and one for a friend's Bless | One charge for each damaging hit |
| **Share Strength** (any maintained power on someone else) | Ended, it stayed on the one who got it, and could end another of the psionicist's own effects instead | It ends on everyone it was on |
| **Dispel Magic** (the preserver's) | Also laid "No spell use" on everyone it caught, your own party too, which Dispel Magic can't remove | Only dispels, as the cleric's always did |
| **Absorb Disease** (the psionic power) | Also gave the psionicist 1d6 STR, as Strength does, and the STR alone when there was no disease to take | Takes the disease only |
| **Bless** and **Aid** | Left out those of the caster's side with an enemy beside them, but measured it from the wrong place, so the wrong ones were left out | Measured from where each stands |
| **Acid Arrow** | After the hit its acid never burned again: its time was a timer that only ended it, and nothing spent it a round at a time | 2d4 acid at the start of each round it lasts (a round for each started minute of its time: four for an 11th-level caster) |
| **Psionic Blast** on a party member | Its imagined wounds (down to a fifth of its hit points) were real and stayed | Given back as the fight ends; until then a blow that would kill it knocks it out instead, and one knocked out wakes with them (the dice log says so; [how](DEVELOPMENT-CONTENT.md#worn-items-the-gladiators-armour-and-psionic-blast)) |
| **Walls** cast by monsters | The computer aimed both ends of a wall at the same spot, so its walls were a single point | Across the line of fire, four cells long |

## Fights

### Sides and blows

| | The game | With the Loader |
|---|---|---|
| A **berserk** or **confused** party member | Could end it fighting for the monsters' side: their side is rolled each turn, and only a charm's end put it back | Back on their own side when it ends |
| **Missiles from behind** | An arrow or a sling stone counted as from behind by the target's facing, at any distance: +2 to hit, and the target's DEX and shield lost, for a whole room's width (a ranger's three arrows each) | Only melee is from behind by the target's facing; a missile counts so only as a hidden archer's shot, "unseen" ([hiding in shadows](FEATURES.md#hiding-in-shadows-to-backstab)) |
| A **thri-kreen's claws and bite** | Crushing, as the game makes every unarmed attack, so a creature crushing weapons can't hurt (a mastyrial) was safe from them | Edged: they cut, for a thri-kreen in the party ([Erdlu Claw](FEATURES.md#new-wizard-spells)'s talons too) |
| The **fire elementals** | The resistances the wrong way round: the fire elemental hurt by +1 weapons, the lesser one only by +2 and by fire | The fire elemental needs +2 weapons and the lesser one +1, as the clue book has them, and neither takes anything from fire |

### Who turns up, and how

| | The game | With the Loader |
|---|---|---|
| The game's **people's weapons and armour** | Carried in their packs until each one's first action in a fight: until then AC 10, armour unworn, no weapon in the Look box; anyone hit before acting (an opening blow, a backstab, the first round) met no armour | Worn and in hand as they come on the map, as the game puts them on: the best weapon in the main hand, a shield or a second weapon in the other, a bow and its arrows, armour and a helm. The mod also puts on a cloak, a belt, boots, an amulet and up to two rings, which the game never did. Each counts by the same rules as the party's |
| **Random monsters** (a vanishing body, a survivor's warning) | How many came was worked out from the wrong monster's strength, and in seven regions the last monster on the list divided by 0, which ended the game ("Divide error") | Worked out from the monster that comes: 1 to 6, fewer of the strong ones |
| A fight's **music** | An attack that starts a fight asks for the music level the region gives its creature, but read it with the wrong step, so every creature but the region's first got another's level | The creature's own level (found by yuan-ti) |

### Resting

| | The game | With the Loader |
|---|---|---|
| **Resting while poisoned** with a druid of 7th level or more | The druid's free Neutralize Poison at the rest was cast after the rest had already looked at who was poisoned, so the poisoned member died anyway (and a disease cured at a rest gave STR back only at the next) | The free cures come first: a 7th-level druid's cure saves the poisoned member, and STR comes back the rest a disease is cured ([resting](HOW-THE-GAME-WORKS.md#resting)) |

## Characters and items

### Making and keeping characters

| | The game | With the Loader |
|---|---|---|
| **DELETE** in the roster | Deleted the character in the row clicked counting from the top of the list, not from the top of what was shown, so with the list scrolled down another character was deleted | Deletes the one chosen ([how](DEVELOPMENT-SCREENS.md#more-characters)) |
| The **creation screen's least scores** | The class's prime requisite raised to 17 and every other score to 9 to 14, against the manual: a fighter's STR never below 17, a thief's CHA never below 9, while a druid's CHA, a ranger's STR and DEX and a psionicist's CON had no minimum of their own | The manual's: cleric WIS 9; druid WIS 12, CHA 15; fighter STR 9; gladiator STR 13, DEX 12, CON 15; preserver INT 9; psionicist CON 11, INT 12, WIS 15; ranger STR 13, DEX 13, CON 14, WIS 14; thief DEX 9; a multiclass character the highest of their classes' ([character creation](HOW-THE-GAME-WORKS.md#character-creation)) |
| **XP for high prime requisites** | None, though the manual promises 10% more XP to a class whose prime requisites are all 16 or more | 10% more of every award for each such class, divided by a multiclass character's classes (one XP for them all); a human's class followed now. The Loader adds it as each award comes, so it needs the Loader following the game ([Experience and levels](PLAYER-GUIDE.md#experience-and-levels)) |

### Thief skills

| | The game | With the Loader |
|---|---|---|
| A **New** character's thief skills | A character made with CREATE CHARACTERS is New until the game starts, when the game makes it Okay; the game's tests for Okay left New out, so a New thief's skills all showed 0 on the inventory screen | The patched game and the Loader count New as Okay wherever they test for Okay; the status under the portrait still reads New, and the game still makes New characters Okay when it starts |
| **Thief skills**' equipment penalty | Taken for anything in the hands, quiver or leg slot (a weapon held cost 5 to 10 points), never for the armour worn | None ([how the game works out thief skills](HOW-THE-GAME-WORKS.md#how-the-game-works-out-thief-skills)) |
| A thief skill rolled **for the whole party** (a trap going off, hearing the men by the wagon) | Meant for the member with the best chance, but the pick compared the wrong way round, so the first party member always rolled | The member with the best chance rolls ([where the game rolls them](HOW-THE-GAME-WORKS.md#where-the-game-rolls-thief-skills)) |

### Items

| | The game | With the Loader |
|---|---|---|
| Items that raise or lower an **ability score** | Changed the score wherever they were, the backpack too, so one carried did as much as one worn | Only while worn ([how](DEVELOPMENT-CONTENT.md#worn-items-the-gladiators-armour-and-psionic-blast)) |
| The **gladiator's armour optimisation** (AC 1 better a 5 gladiator levels) | Given with no armour on, where Dark Sun gives it to armour worn | Only with armour on (arms, legs, head or chest; not a shield, bracers or a robe) |
| **Alagorn's stories** of the Quicksilver Glove and the Helm of Contemplation | Told of what neither does: gauntlets that graft a weapon to the hand, and a shield of thought against all psionic attacks | The glove's name as the game has it and what it does (Detonate on every hit); the helm as Gaze Reflection ([Alagorn's stories](ITEMS.md#alagorns-stories)) |
| The game's **Sling +1** | A blank icon (its picture is missing from the game's data) | The Sling's, with a glow |
| The game's **Great Axe +3** (the Army Commander's) | Its type had no material, as a ring's: its name showed none, and no sphere's cleric could wield it | Metal, as its icon's grey and teal head and its weight have it: "Metal Great Axe +3" |
| The game's **Quicksilver Glove** | Its type had no material, which the game read as wood: it fought at -3 to hit and -2 damage | Leather, as the Chameleon Gloves are: "Leather Quicksilver Glove", 1D6+2 |
| The **air cleric's daggers** | None: no dagger in the game listed the air cleric among those who may use it, though its sphere allows daggers | Every dagger lists it ([how](DEVELOPMENT-CONTENT.md#new-items)) |

## Screens and memory

### Numbers and pointers on screen

| | The game | With the Loader |
|---|---|---|
| **View Character's DAM line** with a wooden, bone, stone or obsidian weapon | One or two more than the attack does: it left out the weaker material's damage (2 for wood, 1 for the others, on a weapon with no plus), which the inventory's line and the attack take off | The same as the inventory's and the attack's |
| The **DAM lines** of a **hasted** or **slowed** character (the inventory screen, View Character) | The attacks a round as if neither: a fight's attack doubles them for Haste and halves them for Slow, but the lines never did, and the inventory's showed half an attack a round (Slow's) as one | Twice, or half, as the attack has them (`3x1D8+13` hasted, `0.5x1D8+6` slowed), as on the Loader's Characters tab |
| **What a scroll says** on the inventory screen | YOU LEARN THE SPELL, YOU CAN NOT READ THE SCROLL and the rest were written to the line under the paper doll but never reached the screen | Shown there, until the pointer is on something else ([what a scroll says](FEATURES.md#what-a-scroll-says)) |
| An archer's **pointer** after a shot | Showed "can't shoot" once any shot of the round was made (one that killed its target, say), though the click still shot the shots left | Shows "can't" only once every shot of the round is made |
| A magic item's power on the **Effects screen** (Shadowseeker's Detect Invisibility) | Said "(15 CHARGES)": the game adds an item's power as it does a permanent effect, leaving a stray value in the charges byte, and showed charges unless the spell's own time was permanent | Charges show only for a spell that lasts a number of uses or a timed effect, as Armor's |

### Pictures and memory

| | The game | With the Loader |
|---|---|---|
| **Graphics disappearing in a busy area** (SSI's note 2712 for Wake of the Ravager, the same engine) | The game keeps 300 picture slots for walls, doors, figures and items lying about, and gives none back until the next area: once a visit had used 300 (items of many kinds dropped, bodies, spells, new monsters), a new picture got no slot and wasn't drawn: an item on the ground, a body, a figure, a doorway | Once all 300 are taken, a slot holding a picture nothing uses now (out of memory, named by no wall or thing on the map) is reused, its picture put where it fits in the store (a different limit from the picture store [the party's outfits](FEATURES.md#what-the-party-wears) fill) ([how](DEVELOPMENT-CONTENT.md#graphics-disappearing-in-a-busy-area)) |
| A magic item's **glow in a shop** | Stood still: a shop runs its own loop, which never turned the colours that make it shine | Shines, as on the map and in the inventory |
| **"Out of memory in OEOpenGraph"** in a long session | The map needs a large block of memory each time it comes back (after the USE screen, a talk, a menu), and with the map up the game had little more than that to spare, so it could stop | Part of the game's code and its music buffer kept in upper memory, so there is much more to spare, and a warning in the dice log if it runs low (`Memory is running low: ...`) ([crash, freeze and item reports](README.md#crash-freeze-and-item-reports)) |

## People and quests

### Scripts that stuck, or ran twice

| | The game | With the Loader |
|---|---|---|
| **The Trustee** in the slave pens | His rounds' two pauses took their corner from numbers other scripts in the pens change, so he could set off for a spot that doesn't exist and stay busy ("I'd love to talk more...") for good. And his key, picked in his talk by a thief with no room for it, fell at his feet: after each step of his rounds he went back for it ("There it is!") without picking it up, and stalled the same way | The pauses keep a corner of their own, and his busy line starts his rounds again, so one already stuck walks on once talked to; the key stays where it lies, for the party to pick up, and he says the busy line once and walks on; and a save made while he (or anyone on rounds of their own) walked no longer leaves him standing when loaded |
| **Kurzak's door** in the slave pens (the entryway to his stop) | It could stand open, both its leaves drawn open, while the map the walkers use still had its doorway shut: the party couldn't step in, and Legcrusher, sent to fetch them, stood still for good (a user's save) | Once its leaves have stood open over a shut doorway for 10 seconds of game time, out of a fight, the doorway opens on that map too; in that save Legcrusher walked through at once |
| **Alagorn's** clothes when the party carries none | He said "no magic clothes", then "Ah, magic clothes", and showed an empty menu: the script's two nested tests for clothes disagreed | The two tests are kept: he says one thing, and the menu matches |
| **Kurzak** calling for **Legcrusher** once the party has killed him (he sends him when they're slow to come to a fight) | Kurzak went on calling for him, greeting the party as if he'd brought them, and speaking of him as still about (Dinos too) | He notices: "Legcrusher? Where has that lump got to? Gladiators! Get up here yourselves!", "I sent Legcrusher after you, and he never came back. You wouldn't know anything about that, would you?", "That was Legcrusher, the monster trainer. He's gone missing."; Dinos says Kurzak will come down himself |
| **Darkhold**'s scripts | Story events left some creatures' triggers pointing at an empty script: the wyvern scene's creature and two in the queen's chamber lost their look text, and the portcullis guard no longer fought back when attacked | Each keeps its own |
| The **Lava Rifts** ranger | His sight trigger, set again, pointed at the hermit's script: endless hermit talk, and a second Iron Necklace | He keeps his own |
| **Linara** in Gedron | Once the extract was delivered, her talk ended with no menu, so Jasmine's spellbook could never come up | Her talk goes on to her menu |
| The slave pens' **sewer grate** | The search for a weapon in hand stopped at once, so "hack the lock off" was never offered; and a hack that worked left the grate shut; one that failed said the weapon broke, and kept it; an attack on the grate always broke its lock | Offered to a member with a melee weapon in either hand (not a bow, sling, chatkcha or shield), and the weapon named is the one used (the game named the next item carried). A hack works half the time, always with Bloodwrath, and opens the grate, saying "his" or "her" as picking the lock does (one that fails breaks a weapon that can break in a fight, a plain wooden, bone, stone or obsidian one, which is lost; a metal or magic one "rings off the grate, unharmed"). An attack breaks the lock on a Strength roll, as ripping the grate open does, or "fails to damage the lock" |
| **Pehtucl's ambush** at the slave pens' fountain | Besides the five guards he calls, every other Arena Guard and Guard in the pens (up to ten) was sent after the party from wherever it stood, and a guard attacked in the passage before the fountain, where the party stands as he turns on them, raised the alarm (every guard in the pens hunting), though the fight was meant to be fought there unheard ("the roar of the fountain masks his voice") | Only Pehtucl and the five guards he calls hunt the party; the fountain masks a yell in that passage too, as in the fountain's room |
| The **Rebel Mindhome** in Undermountain | Once the party had killed the four spiders, every talk to the Mindhome's leader gave the thanks and its 5000 XP again | The 5000 XP comes once |
| The **messenger in region 9** (the men who burst from the sand, after the elves leave) | Came only if the party left the region and came back after the elves had gone, so a party that stayed never met him | He comes once the elves have left |
| The **Draj serf** led to region 10 | One left more than 14 squares behind stayed in region 38 without his orders, and talking to him again ran the whole deal and gave a second obelisk gem | He comes along however far behind |

### Who is talking: class, race and sex

| | The game | With the Loader |
|---|---|---|
| A **ranger tracking** at the Wagon Train's bodies | The check looked for the ranger's flag where the character's record isn't, so found no ranger; it tested a ranger's level as a bit of its class; and the d20 had to beat the score, not come under it: "You cannot interpret the tracks surrounding the body" | A ranger reads the tracks on a d20 under its score (WIS, more at higher ranger levels), for XP |
| A **multi-class preserver or psionicist** talking about the haystack | The talk tested the class as the whole class word, so only a single-class one could answer "Being a powerful magician, I scried it" or "I can read your very thoughts" | Any preserver or psionicist |
| **Dagolar's slime book**, in his laboratory | "Magical training" to read it took a psionicist, a preserver, a fighter or an air cleric, not an earth, fire or water cleric or a druid | A cleric, druid, preserver or psionicist (any one of the character's classes); a fighter has no magical training |
| The cave guide's "Why don't you go bother someone **your own size**" | Asked "not a dwarf, or not a halfling?", true of everyone, so a dwarf or halfling heard it too | A dwarf or halfling is told to bother "someone else" |
| Lines that depend on the **race or sex** of the one talking to someone | Read from the wrong record, so they always took the party's active member for a man of no race: a halfling was never greeted as a fellow halfling ("Oh, it is a relief to see a fellow halfling") nor named by race in the insult that follows, a woman was told "only a mad man would think of fighting Draj" and of "his purse", a thri-kreen never heard the bell the mastyrial hears near Demothi's camp, nor was told "your help" rather than "the help of any humanoid" | Each reads the active member's own race or sex |

## Rules it got wrong, with a switch

Most of the [rule changes](FEATURES.md#rule-changes) put right a rule the game gets wrong: it
departs from its own manual, from itself, or from the Player's Handbook it follows. Each has a
switch on the Options tab, on by default, so the game's own rule is still there to go back to. (The
rule changes that are the mod's own choices, not corrections, are left out: helms' AC, resting, the
XP level cap, hit dice, creation scores, half-giants' weapons, creature size, weapon traits (cahulaks, stinkpots, polearm reach) and ages.)

| Rule | The game | The rulebook | Switch |
|---|---|---|---|
| Saves against spells | Petrification or polymorph for almost every spell | The save against spells | [Saving throws against spells](FEATURES.md#spells-saved-against-with-the-spell-save) |
| Fire, cold and electricity | The save's d20 doubled (70% to save a Fireball where 35% is due), which the manual and AD&D don't have | DEX's adjustment | [Saving throws against spells](FEATURES.md#fire-cold-and-electricity-dex-instead-of-a-doubled-d20) |
| Spells, psionics and monsters | Saves, times, damage and effects that part from its own manual (pp. 29-44) | As the manual has them | [As the manual describes them](FEATURES.md#spells-and-psionics-as-the-manual-describes-them) |
| Turn Undead | A d20 against a number of its own, a row too easy for 2- and 3-HD undead and a row too hard for 5 HD; a success destroys, there is no fleeing, and a priest may try the same undead as often as they like | AD&D's turning table: undead turned flee for 3d4 rounds, D destroys, D* destroys more of the kind, "---" no chance; a priest who fails can't try that undead again that fight ([the table](HOW-THE-GAME-WORKS.md#adds-turning-table)) | [As the manual describes them](FEATURES.md#spells-and-psionics-as-the-manual-describes-them) (it goes with the spells' switch) |
| Missile and touch spells | Every one lands, every time | They roll to hit ("as if fired by a fighter") | [Spells roll to hit](FEATURES.md#spells-roll-to-hit) |
| Enlarge | Grows the whole hit, STR's bonus and magic's too, rounded down | The weapon's dice grow, rounded up; STR, class and magic aren't altered (Player's Handbook p. 173) | [Enlarge](FEATURES.md#enlarge-multiplies-the-weapons-dice-only) |
| A ranger's spells | Spell levels by its level less 7, but duration and damage by its whole level | Level less 7 for all | [Rangers' casting level](FEATURES.md#rangers-casting-level) |
| Preservers' spells | Any spell learnt from any scroll, every spell known | INT's chance to learn, and its most spells of each level | [Preservers' INT](FEATURES.md#preservers-int) |
| Dual-classing | From 2nd level, one prime requisite a class | From 3rd level, every prime requisite (the game's manual, pp. 12 and 22-26) | [Dual-classing](FEATURES.md#dual-classing-as-the-manual-has-it) |
| Class restrictions | Any one class allowing an item is enough | The strictest class wins | [Class restrictions](FEATURES.md#class-restrictions) |
| Multiclass hit points | CON's bonus once a level | CON's bonus on every hit die, the total shared | [Multiclass hit points](FEATURES.md#multiclass-hit-points) |
| Class tables | Priests' THAC0 a level early, short spell slots, a little too little XP for 2nd level | AD&D's tables | [AD&D's class tables](FEATURES.md#adds-class-tables) |
| CON 20 and up | A hit point back every 5 minutes at any CON; CON's adjustment on a dwarf's or halfling's poison save | AD&D's rate (one an hour at CON 20, one every 10 minutes at 25); the racial bonus only | [CON as in AD&D](FEATURES.md#con-as-in-add) |
| Two weapons | No penalty (a small bonus at DEX 5 or less), the full rate in each hand | -2 and -4, DEX's adjustment, one attack with the off hand | [Two weapons](FEATURES.md#two-weapons) |
| Warriors' attacks | 3/2 with any weapon | The plain rate outside a specialization | [Weapon specialization](FEATURES.md#weapon-specialization) |
| Held and Out Cold targets | A roll to hit as ever, and double damage | A hit automatically, for normal damage | [Held targets](FEATURES.md#held-targets) |
| Acid on armour | The item destroyed outright | Each item saves by its material | [Items saving against acid](FEATURES.md#items-saving-against-acid) |
| Thief skills and backstabs | Skills too high (a 3rd-level elf with move silently 66); a backstab multiplied STR's bonus too | The Player's Handbook's table; a backstab multiplies the weapon's dice only | [Thieves as in AD&D](FEATURES.md#thief-skills-from-adds-table) |

## Two more, with a switch

Two of the game's bugs are mended by a switch of their own: Cilla's figure (the game gives the elf
the half-elf woman's; see [Elves and half-elves](FEATURES.md#elves-and-half-elves)), and a click on a
spell's icon on the Effects screen ending it ([Spells on the Effects
screen](FEATURES.md#spells-on-the-effects-screen)).

## Saved games

There's no need to start a new game for these: they're in
the patched game, not in a save, so they work from the moment a game is
loaded. What a bug already did stays in the save: [your saved
games](README.md#updating-backups-saved-games-and-the-loaders-files) says what.
