# Obsidian Edition

Obsidian Edition is a mod for **Dark Sun: Shattered Lands** (the GOG release)
in DOSBox, with its own companion window, **Templar's Ledger**, beside the
game.

## Contents

- [What it does](#what-it-does)
- [Requirements](#requirements)
  - [Suggested system requirements](#suggested-system-requirements)
- [Running it (Windows)](#running-it-windows)
  - [One-time setup](#one-time-setup)
  - [Every time you play](#every-time-you-play)
  - [Other ways to start](#other-ways-to-start)
  - [If the game or DOSBox crashes](#if-the-game-or-dosbox-crashes)
- [The Ledger's window](#the-ledgers-window)
  - [The Characters tab](#the-characters-tab)
  - [The Spells tab](#the-spells-tab)
  - [The Dialogue tab](#the-dialogue-tab)
- [The dice log](#the-dice-log)
- [How the game works](#how-the-game-works)
  - [Initiative](#initiative)
  - [Spells and effects](#spells-and-effects)
  - [Psionics](#psionics)
  - [Character creation](#character-creation)
  - [Monsters' defences](#monsters-defences)
  - [Searching junk, hay and wardrobes](#searching-junk-hay-and-wardrobes)
  - [No critical hits](#no-critical-hits)
  - [The game's two weapons](#the-games-two-weapons)
  - [How the game works out thief skills](#how-the-game-works-out-thief-skills)
  - [Where the game rolls thief skills](#where-the-game-rolls-thief-skills)
  - [Attacks from behind and backstabs](#attacks-from-behind-and-backstabs)
  - [The game's saving throws](#the-games-saving-throws)
- [In the game](#in-the-game)
  - [THAC0, saves and thief skills](#thac0-saves-and-thief-skills)
  - [Spell slots on the USE screen](#spell-slots-on-the-use-screen)
  - [Each turn's rolls](#each-turns-rolls)
  - [What hurts a monster (the Look box)](#what-hurts-a-monster-the-look-box)
  - [Charges in item boxes](#charges-in-item-boxes)
  - [No manual check](#no-manual-check)
- [Rule changes](#rule-changes)
  - [Class restrictions](#class-restrictions)
  - [Multiclass hit points](#multiclass-hit-points)
  - [Hit dice: the better of two](#hit-dice-the-better-of-two)
  - [Scores and hit points as rolled](#scores-and-hit-points-as-rolled)
  - [Rangers' casting level](#rangers-casting-level)
  - [Preservers' INT](#preservers-int)
  - [AD&D's class tables](#adds-class-tables)
  - [Spells saved against with the spell save](#spells-saved-against-with-the-spell-save)
  - [Fire, cold and electricity: DEX instead of a doubled d20](#fire-cold-and-electricity-dex-instead-of-a-doubled-d20)
  - [Two weapons](#two-weapons)
  - [Items saving against acid](#items-saving-against-acid)
  - [Rings and cloaks of protection](#rings-and-cloaks-of-protection)
  - [Half-giants' two-handed weapons](#half-giants-two-handed-weapons)
  - [Helms](#helms)
- [More character customization](#more-character-customization)
  - [Weapon specialization](#weapon-specialization)
  - [Kits](#kits)
  - [Levels up to 10](#levels-up-to-10)
  - [STORE and RECALL on the creation screen](#store-and-recall-on-the-creation-screen)
  - [The game's own party](#the-games-own-party)
- [Expanded features](#expanded-features)
  - [The leader's CHA at shops](#the-leaders-cha-at-shops)
  - [Improved thieving](#improved-thieving)
    - [Thief skills from AD&D's table](#thief-skills-from-adds-table)
    - [Hiding in shadows to backstab](#hiding-in-shadows-to-backstab)
    - [Picking pockets](#picking-pockets)
- [New content](#new-content)
  - [New wizard spells](#new-wizard-spells)
  - [New items](#new-items)
    - [Bracers of defense](#bracers-of-defense)
    - [Robes](#robes)
  - [New people](#new-people)
    - [Kalzith](#kalzith)
    - [Semyon](#semyon)
    - [What Dinos and the Trustee say about them](#what-dinos-and-the-trustee-say-about-them)
  - [The cooked vulture](#the-cooked-vulture)
- [Item tables](#item-tables)
  - [Every magic item](#every-magic-item)
  - [Every mundane weapon](#every-mundane-weapon)
- [Graphics](#graphics)
  - [Elves and half-elves](#elves-and-half-elves)
  - [What the party wears](#what-the-party-wears)
  - [Shadows](#shadows)
  - [Dust](#dust)
- [Controls](#controls)
  - [Choosing an enemy: Tab, Enter and the rings](#choosing-an-enemy-tab-enter-and-the-rings)
  - [Scrolling the map](#scrolling-the-map)
  - [Spells on the Effects screen](#spells-on-the-effects-screen)
- [More saves and characters](#more-saves-and-characters)
  - [More saves](#more-saves)
    - [Saves under their names](#saves-under-their-names)
  - [More characters](#more-characters)
- [Game speed](#game-speed)
- [Accessibility](#accessibility)
- [Without the game](#without-the-game)
- [The player's guide](GUIDE.md)
- [Development](DEVELOPMENT.md)

## What it does

New to the game, or to the mod? [The player's guide](GUIDE.md) has its rules
and tables in one place, without spoilers, with a section for each class.

It shows what the game keeps hidden. Every roll is logged as it happens:
attacks, damage, saving throws, thief skills, initiative, even the dice at
character creation. Each comes with what it needed and where every bonus came
from ([the dice log](#the-dice-log)). The game's own screens gain THAC0, saves,
thief skills and spell slots, and the Look box tells you what can hurt a
monster ([In the game](#in-the-game)).

It brings the rules closer to AD&D: class restrictions, AD&D's class tables
(experience, priests' THAC0, spell slots), INT's limits on learning spells,
saving throws as the books have them, scores and hit points kept as rolled,
and multiclass hit points as the books have them ([Rule
changes](#rule-changes)). It gives more ways to build a character: weapon
specialization and mastery, kits (three for each class), levels up to 10,
and STORE and RECALL for a creation roll ([More character
customization](#more-character-customization)). And it expands play:
thieves with AD&D's skills hide in shadows to backstab and pick pockets, and
the party leader's CHA lowers shop prices ([Expanded
features](#expanded-features)).

It adds to Athas: new weapons in every material, magic items with stories of
their own (robes and bracers among them, for those who wear no armour), three wizard
spells ([Cat's Grace, Erdlu Claw and Fogbolt](#new-wizard-spells)), Kalzith
(a defiler who sells scrolls), more of Semyon's story, and a use for the cooked
vulture ([New content](#new-content)). On the map, the party
wears its weapons and armour, figures cast shadows and kick up dust, and elves
and half-elves have a look of their own ([Graphics](#graphics)).

Quality of life changes: choosing an enemy with Tab and attacking it with
Enter, scrolling the map by dragging with the mouse wheel
([Controls](#controls)), 40 saves, each also kept under its name, and 29 saved
characters ([More saves and characters](#more-saves-and-characters)), a game speed setting ([Game
speed](#game-speed)), crash reports, and no dragon asking for a word from the
manual, the game's copy protection ([No manual check](#no-manual-check)).

**What it changes on your computer.** The game's own files are never
modified: the Ledger runs a patched copy of the game, with copies of its data
files, from its own folder (see
[DEVELOPMENT.md](DEVELOPMENT.md#how-the-dice-log-works)). Play writes to the
game folder only what you'd expect:

- your saves: page 1 as always, pages 2 to 4 as files of their own beside
  them ([more saves](#more-saves));
- your characters, 20 to 29 among the game's own in `CHARSAVE.GFF`
  ([more characters](#more-characters));
- in a saved game, the new items, if **New items** is ticked. Some are item
  types the original game doesn't have (the Short Sword, the Cloak of
  Protection, the bracers, the robes, plate mail, the Cloak and Boots of
  Elvenkind, a metal shield), so load such a save with the Ledger.

The window is dressed in the game's own colours, sampled from it; no game
artwork is copied.

## Requirements

- **Windows** with DOSBox (plain DOSBox 0.74, DOSBox Staging, or the DOSBox
  bundled with the GOG/Steam release).
- **64-bit Python 3.8+** from python.org. If it isn't installed, the `.bat`
  files offer to install it for you (see below). Python includes tkinter and
  needs no extra packages. It has to be 64-bit because 64-bit DOSBox can't be
  read from 32-bit Python.
- Linux works too if you can read other processes' memory (root, or
  `kernel.yama.ptrace_scope=0`).

### Suggested system requirements

DOSBox runs the whole game on one processor core, so what counts is the speed
of a single core, not how many there are. By [game speed](#game-speed)
setting (suggestions, not tested limits):

| Game speed | Processor (one core's speed) | Memory |
|---|---|---|
| GOG's own | anything that runs GOG's release | 2 GB |
| Faster (20,000 cycles, the default) | a dual-core from about 2010 on, 2 GHz or more (Intel Core i3 or AMD Phenom II) | 4 GB |
| Fastest (35,000 cycles) | a processor from about 2015 on, 3 GHz or more (Intel Core i5 or AMD Ryzen) | 4 GB |

The Ledger itself (Python and its window) needs about 100 MB of memory and
little processor time. A screen of 1920×1080 or more shows the game's window
at **Triple** size beside the Ledger's; on a smaller one choose **Double**.
If the computer can't keep up, the sound crackles or stutters and the game
slows instead of speeding up: choose the next setting down.

## Running it (Windows)

Templar's Ledger, the mod's companion window, is a separate program that runs
next to the game. You don't install anything into the game folder.

### One-time setup

1. Download the latest release, `Dark-Sun-Shattered-Lands-Obsidian-Edition-<version>.zip`,
   from the [Releases page](https://github.com/daaki85/darksun-obsidian-edition/releases),
   and unzip it anywhere: the files you need are in its
   `Dark-Sun-Shattered-Lands-Obsidian-Edition-<version>` folder. (Or the project as it stands: on its
   GitHub page click **Code → Download ZIP**; the files are then in its
   `darksun-companion` folder.)
2. Python: the first time you double-click one of the `.bat` files, it
   checks for a 64-bit Python 3.8 or later. If there is none, it asks
   whether to install it with Windows' own package manager (winget): that
   downloads the official, signed installer from python.org, for your user
   only, with no administrator rights. Answer **Y**, and when it's done, start
   the `.bat` file again. (If you'd rather do it yourself, or winget isn't
   there, install the 64-bit Python from <https://www.python.org/downloads/>
   and tick **"Add python.exe to PATH"** on the installer's first screen.)

**"Open File - Security Warning"** ("The publisher could not be verified"): Windows
asks this for any `.bat` file unzipped from a download, since a `.bat` file can't
be signed. To skip it altogether, before unzipping right-click the zip, choose
**Properties**, tick **Unblock** and press **OK**. Otherwise press **Run** the
first time: the Ledger then takes the download mark off the files in its own
folder (what that Unblock box does, and nothing outside the folder), so the other
`.bat` files start without asking.

Everything else is plain text you can read: the `.bat` files, the Python
code in `dscompanion`, and the dice log helper's source (`dos\dsclog.asm`,
which builds `dos\DSCLOG.EXE`, the small DOS program DOSBox loads). There is
no packaged program to trust.

### Every time you play

1. Double-click **`Start Obsidian Edition.bat`** in that
   folder. The Ledger opens on its own.
2. On its **Options** tab, pick what you want: the rule changes, the new
   content, picking pockets, each turn's rolls in the game and so on (see
   [The Ledger's window](#the-ledgers-window) and [Rule changes](#rule-changes)).
   They're remembered for next time.
3. Pick the **Game window** size at the top if you like, then press **Start
   the game** (top left).

That starts Shattered Lands (through GOG's own DOSBox) with the dice log helper
loaded and your options in force, and the Ledger picks it up once DOSBox is up.
Your saves are the same ones the game normally uses. The first time, it looks
for the game in the usual GOG folders; if it can't find it, it asks you where
the game is installed and remembers the answer.

DOSBox opens in a window three times the game's size (960x720), not full
screen. To change that, pick **Game window** at the top of the Ledger:
**Double (640x480)**, **Triple (960x720)**, **Quadruple (1280x960)** or **Full
screen**. It's remembered, and used from the next time you start the game.
Alt+Enter switches between window and full screen while playing. (From a
command prompt: `--window-scale 2` to `4`, `--fullscreen` or `--windowed` after
`launch` or `play` do the same.) GOG's DOSBox has no four-times scaler, so
Quadruple has DOSBox stretch its window with OpenGL (`output=opengl`,
`windowresolution=1280x960`); if your graphics driver doesn't take to that,
pick Triple.

Load your game. The party's stats fill in by themselves, and rolls appear in
the **Dice log** tab as they happen.

### Other ways to start

**Game and Ledger in one double-click:** **`Start Game with Dice Log.bat`**
starts the game with the dice log and opens the Ledger next to it, with the
options as you last set them on the Options tab. With the game started the
normal way instead (GOG's own shortcut), the Ledger still shows the party, but
the dice log will say the game was started without it.

**Just the game, with the in-game additions, no Ledger window:** double-click
**`Play Dark Sun (in-game rolls).bat`**. The dice log runs unseen and stops
when you close DOSBox. It uses the switches on the Ledger's Options tab as you
last set them (each turn's rolls, monster descriptions, picking pockets, the
rule changes); the new items, the new people and the cooked
vulture are there too. If anything goes wrong it says so in a message box and
writes the details to `play.log`.

### If the game or DOSBox crashes

When the game stops with an error (such as
"Null pointer assignment"), DOSBox waits with the game's message on screen
("The game stopped with an error", then press a key) rather than closing over
it. With the game started from the Ledger (or either `.bat` file), the dice log
also says how DOSBox closed: `DOSBox closed: it crashed (an access violation,
code C0000005h)` means DOSBox itself failed, not the game.

Either way, the Ledger saves a crash report in the
`crash-logs` folder (beside `Start Obsidian Edition.bat`), named for the time,
such as `crash-logs\crash-2026-10-04-213012.txt`, and says so in the dice log
(or, with `Play Dark Sun (in-game rolls).bat`, in a message box). It holds:
- how DOSBox closed (its exit code), and what the game left on the screen;
- how long the game ran, and the Ledger's switches and game speed (not where the
  game is installed, nor the party's names);
- DOSBox's own `stdout.txt` and `stderr.txt` from that run, if it wrote them;
- any writes into the game the Ledger refused as unsafe;
- the last 300 lines of the dice log and the last 80 of the dialogue.

Send the file along with what you were doing just before. A game closed the
usual way (Exit to DOS, or closing DOSBox's window) writes no report. With the
game started from GOG's own shortcut, the Ledger can't see how it closed, so
there is no report.

## The Ledger's window

The window has the party on one side and the logs and tools on the other, with
**Start the game**, the game window's size, the text size and **Reconnect** (to
find the game again) along the top. The
party pane has two tabs:

- **Characters** (Alt+C): a card for each character, laid out like the game's
  View Character screen (scroll with the mouse wheel, or Tab to the cards and
  use the arrow and Page keys):
  - the figure for their race and sex (as on the character creation screen,
    read from your install), their name, and HP and PSP (PSP in blue);
  - their condition (New, for a character not yet played, Okay, Stunned, Out
    Cold, Dying, Dead, Animated, Petrified or Gone), then the spells and
    effects on them with the rounds or charges left: `Blur (22 rounds)`,
    `Stoneskin (5 charges)`;
  - the character sheet: scores, sex, race and alignment, classes and levels,
    experience, AC (the one the game last used in a fight, with the base AC
    beside it), THAC0 with each weapon ready (`THAC0: 15 with Wooden Club, 14
    with Wooden Bow (base 19)`), the saves as the d20 needed now (see
    [In the game](#thac0-saves-and-thief-skills)), movement (`Move: 12 (14 in
    a fight: Stalker)`) and attacks;
  - what they wear and hold, by the game's own slot names ("Right hand: Bone
    Long Sword"; "Carried" for the backpack), with each item's material and
    plus;
  - last, spell slots for spellcasters (see below), thief skills for thieves,
    and for rangers, with hiding to backstab on, their chances to hide and move
    silently (`Ranger skills now`).
- **All fields** (Alt+A): every field the layout maps, in a table, with rows
  of its own for the AC in a fight and what it's made of, THAC0 with each
  weapon and the saves now, and at the end the spell slots, thief skills and
  equipment.

The other side has the **Dice log**, **Dialogue** and **Spells** tabs (below),
**Memory tools** (for mapping the game's memory, with **Save layout** and
**Reload layout**: see [DEVELOPMENT.md](DEVELOPMENT.md#mapping-memory)), and
**Options** (Alt+O) with the Ledger's switches, in sections that open and
close: click a section's heading (or Tab to it and press Space or Enter) to
open it, ▸ when closed and ▾ when open. Which sections are open is remembered.
Everything there applies in games started from the Ledger; a switch that says
"from the next start" waits until the game is started again. The sections:

- **In the game**: each turn's rolls and how much they say, monster
  descriptions ([In the game](#in-the-game)).
- **Rule changes** ([Rule changes](#rule-changes)): the game's rules closer
  to AD&D.
- **More character customization** ([More character
  customization](#more-character-customization)): weapon specialization, kits,
  levels up to 10, and STORE and RECALL on the creation screen.
- **Expanded features** ([Expanded features](#expanded-features)): the
  leader's CHA at shops, and **Improved thieving** (AD&D's thief skills,
  hiding to backstab, the cloak, boots and belt, and picking pockets).
- **New content** ([New content](#new-content)): the new spells, at once; the
  new people, the vulture and the new items, from the next time the game is
  started (what a saved game already has stays in it).
- **Graphics** ([Graphics](#graphics)): the elves' and half-elves' looks,
  Cilla drawn as an elf, what the party wears, shadows and dust.
- **Controls** ([Controls](#controls)) and **Game speed** ([Game
  speed](#game-speed)).
- **Saves** ([Saves under their names](#saves-under-their-names)): the folder
  of saves kept under their names, and putting one back in a slot.

All are on by default except each turn's rolls in the game and the right
button, and are remembered for next time. **Restore defaults**, at the bottom
of the tab, sets them all back (after asking).
In a window too small to show the open sections, the tab scrolls (scrollbar,
mouse wheel, or arrow and page keys once it has the focus).

![The Options tab with More character customization, Expanded features (Improved thieving among them) and New content open, the other sections closed](docs/options.png)

### The Characters tab

What some of a card's lines mean.

**Spell slots.** `Priest spells left: 1st 5/5, 2nd 3/3, 3rd 2/2`
means five first-level priest spells can still be cast out of five, and so
on. Casting a spell uses one slot of its level, and resting fills them
again. Wizard slots belong to preservers; priest slots belong to clerics,
druids and rangers. A multi-class character's classes add up, for example a
druid/preserver has both. The "most" is worked out the way the game does it
when it refills them (its tables are read from memory):
- Preservers: from their level only.
- Clerics and druids: from their level plus a WIS bonus.
- Rangers: from their level only, with their first slot at level 8.

With [AD&D's class tables](#adds-class-tables) on (the default), clerics',
druids' and preservers' come from AD&D's tables instead. Some [kits](#kits)
have more or fewer.

The game's WIS bonus doesn't depend on level, so it gives a 2nd-level druid
with WIS 19 slots at the 2nd to 4th levels too, though a druid that level
casts only 1st-level spells. Those aren't shown (here or in the game): only
the spell levels the character's class levels reach, as in AD&D, where the
WIS bonus counts only at levels the priest can cast. For a human dual-class character, a
later class counts only while its level is below the first class's.

**AC.** The AC shown (**Current AC** on All fields) is the one the game last used for each
character in a fight (armour, DEX and spells included), and the rows under it
say what it was made of: armour and shield (and spells that take their place,
such as Spirit Armor and Magical Vestments), DEX (the game's table: −1 at 15
down to −6 at 24; not counted when attacked from behind), and spells, rings
(the [rings of protection](#rings-and-cloaks-of-protection)) and anything else. They show "-" until the game has worked out that character's AC
in a fight.

**Scores.** Ability scores such as `STR 24 (20 without spells)` show the score now and, in
brackets, the character's own score when a spell (Strength, for one) has
raised it. The character's own score already includes the racial adjustment:
a half-giant's 20 + 4 shows as 24.

### The Spells tab

What each wizard and priest spell and psionic power does, read from the
running game's records: its damage dice and kinds (and that damage stops
growing at caster level 10), its saving throw (which of the five, any
modifier, whether the d20 counts double, and whether saving halves or stops
the damage), the effect it gives and what that does, how long it lasts, and
each party member's caster level for it. **Show** picks wizard, priest or
psionic, and **Only spells the party has a caster level for** leaves out the
rest. **Save...** writes it to a text file. It's filled when you open the tab
(or press **Refresh**) while the game is running.

### The Dialogue tab

Everything the game shows in its dialogue window, one entry per window of
text, with the replies offered numbered underneath (and the list's title,
such as "Answer Yes or No", above them), and then the one you picked:
`You chose: No`.

![The Dialogue tab at the start of a new game: the Announcer, with his portrait, introducing the Defiler's show](docs/dialogue.png)

**Who's speaking.** The game's dialogue window gets only a portrait number,
never a name. But when the game runs a script on someone (you click them, or
they come up to you), it notes who; the log reads that when a conversation
opens. A conversation that shows one face, started on a named creature outside
the party, is that creature talking, and from then on the portrait carries its
name: in the pens, portrait 5 became `Kurzak` ("Legcrusher! Get gladiators!")
and portrait 100 `Legcrusher` ("Kurzak told me to bring you to the arena").
When several faces take turns in one conversation, nothing is learned from it,
as it can't be told who is who. Names learned are shown on the lines already
there too, and kept in `settings.json` (`speakers_learned`). A speaker not
named yet shows as `Portrait 57`. Portrait 119 is named `The Announcer`, as the
game itself calls him ("Yell something back at the Announcer?"). That name isn't
replaced by one learned (he calls out in the middle of fights, when the
game's last script ran on a fighter). To name a
speaker yourself (your name wins over a learned one), right-click the name
line in the Dialogue tab, or press **Name speaker...** (it names the latest
speaker). The name replaces the number on every line from that portrait,
the ones already shown included, and is remembered in `settings.json` for
next time (the command-line log uses it too). Leave the name empty to go back
to the number. Text shown without a face (the emblem instead) is `Narration`.

Each entry shows the speaker's portrait, as the game's own dialogue window
does. Portraits and the title's lettering are read from your installed game
at run time (GPLDATA.GFF and RESOURCE.GFF in the install folder the launcher
remembers); nothing from the game is copied into Templar's Ledger. Without
the game installed the window uses its own lettering and no portraits.

## The dice log

![Templar's Ledger during the arena's opening show: the Characters tab with the game's own party, and the dice log of the Defiler's Cone of Cold killing a Slig and the Rampager's acid killing the Defiler](docs/dicelog.png)

**Reading it at a glance.** Lines at the left edge are the events: a round
starting, whose turn it is, attack rolls, saves, spells, kills. Lines indented
two spaces are their results (damage, HP left); lines indented four spaces are
the details: the sums behind a THAC0, a save's modifiers, the initiative
scores. Untick **Show details**, above the log, to hide the details and keep
the rest; they come back when it's ticked again. In the window, each kind has its colour
(hits green, misses grey, damage amber, saves blue, turns sand, rounds
underlined with a gap above), but the words say the same thing, so nothing
depends on telling colours apart. Names stand out in bold: each party member
in a colour of their own (cyan, magenta, peach and white, by place in the
party) and every monster and other creature in red, so who acts and who is
hit can be followed down the log. Every colour has at least 4.5:1 contrast
with the log's background (WCAG 2.0 AA, as AODA asks).

**Fights**

| Line | Meaning |
|---|---|
| `Round 2: K'ratchek 32, Cermak 31, Cilla 30, Gerakis 26, Slig 26` | A new round of a fight, numbered from the fight's start, and the order everyone acts in (highest first). The order also stays in view above the log for the whole round, however far the log has scrolled: `Round 2. Now: Cilla (30). Still to act: Gerakis 26, Slig 26. Done: K'ratchek 32, Cermak 31. Down: ...`, and the in-game turn summary ends with who is still to act (or the next round's order). The lines under it (shown with **Show details**) give each score's make-up: `    Gerakis 26 = 20 + 6 (0-9 roll), tie broken by 38 (0-199 roll)` (see [Initiative](#initiative)). If the log was started in the middle of a round, the list has only the rolls it saw. |
| `Gerakis's turn` | Whose turn it is now, each time the turn passes in a fight. |
| `X attacks Y with Long Sword +1 (1d8+1): d20 = 14, needs 12+ (45%), hits AC 1, target AC 3 -> HIT` | An attack roll, the weapon and its damage dice. `needs 12+ (45%)` is the d20 this attacker needed against this target (THAC0 − target AC) and the chance of rolling it; `hits on anything but a 1` or `only a 20 hits` when it's out of the ordinary range. `X attacks Y from behind ...` and `X attacks Y BACKSTAB ...` mark attacks from behind and backstabs (see [Attacks from behind and backstabs](#attacks-from-behind-and-backstabs)). "Hits AC" is the lowest AC this roll hits (THAC0 − d20); the target AC is the one the game used, with armour, DEX and spells. A natural 20 always hits and a natural 1 always misses, but a 20 does no extra damage: the game has no critical hits (see [No critical hits](#no-critical-hits)). |
| `    THAC0 16, +1 Blessed, +6 STR, +1 weapon = 8` | Where the attacker's THAC0 for this attack comes from: STR (melee) or DEX (missiles), spells (Bless, Prayer, Slow, Graft Weapon, the target's Blur), attacking from behind, the weapon's plus, the penalty for non-metal weapons (wooden −3, bone −1, stone and obsidian −2), the two-weapon adjustment (see [Two weapons](#two-weapons)), and the difficulty setting for monsters. |
| `  X hits Y for 14: 1d8 = [6] +8 STR 20` | The damage of that hit: the dice, the weapon's bonus, and the STR bonus the game adds for melee. Damage is at least 1. |
| `  X hits Y for 51: (1d8 = [5] +12 STR 24) x3 backstab` | A backstab (see [backstabs](#attacks-from-behind-and-backstabs)) multiplies the whole damage, STR bonus included. |
| `Chosen with Tab: Guard (50 HP) - Enter attacks it` | An enemy chosen with Tab in a fight (see [Choosing an enemy](#choosing-an-enemy-tab-enter-and-the-rings)). |

**Spells, saves and effects**

| Line | Meaning |
|---|---|
| `Shocking Grasp damage: 1d8 = [5] +10 = 15 (1d8 + 1 for each caster level: 10 at caster level 20, which counts as 10)` | A spell's damage roll, rolled for each target before its saving throw, with the spell's formula from the game's data. Damage stops growing at caster level 10 (Fireball does at most 10d6). Magic Missile, Flame Arrow and Minute Meteors are rolled elsewhere in the game, without the caster's level, so their line says how many steps the dice stand for. |
| `  Slig takes 15 from Shocking Grasp, now 3/18 HP` | What the spell really did to each creature, after its save, resistances and protections (or the healing it gave). A creature that is Out Cold gets no save and takes the most the dice can do (the game's damage code does that), marked `(Out Cold: the most the dice can do)`. |
| `    Blur lasts 23 rounds (caster level 20: 1 for each caster level = 20 + 3 from the dice; dice 3d1)` | How long a spell's effect lasts, and how the game worked it out. A round is 60 game seconds. The game often "rolls" dice with one side, which are fixed numbers. |
| `    Stoneskin has 23 charges (caster level 20: 1 for each caster level = 20 + 3 from the dice; dice 1d4 = [3])` | Effects that last a number of uses rather than a time (Stoneskin's blows, Mirror Image's images, Invisibility's one attack, Poison's rounds): the game stores them as charges, worked out like a duration. |
| `    Acid on Slig: 2d4 = [3 + 1] = 4 acid damage` / `    Ironskin on Cilla: one charge used` | Acid Arrow's damage each round while the acid lasts; and an effect with charges using one up (Stoneskin or Ironskin stopping a blow, Mirror Image losing an image...). |
| `Strength: 1d6 = 5 -> Cilla's STR +5 while it lasts (at most 24)` | The amount Strength (or Adrenalin Control) adds. |
| `Y magic resistance 30% vs Fireball: d100 = 71 -> not resisted` | The magic resistance roll (only shown for targets that have some), counting Mind Bar and Lower Resistance. |
| `    Dispel Magic on Slig's Blessed: d100 = 60, needs 85 or less (50 + 5 x 7 - 5 x 0 (its caster's level)) -> dispelled` | Dispel Magic tries each effect on its target separately: 50 + 5 for each of the dispeller's levels, less 5 for each of the level the effect was cast at. It can't touch some (Biofeedback, Diseased, Feeblemind, Poisoned, Graft Weapon, No spell use, Stuck, Mind Bar and a few more). |
| `    Abjure on Y: d20 = 14, needs 12 or more (11 - caster level 5 + its level 6) -> sent away` | Abjure sends a summoned creature away (1000 damage) on a d20 at or over 11 - the caster's level + the creature's. |
| `    Summoning: 1d3 = 2 picks which of its 3 creatures comes` | Which creature a summoning spell brings. |
| `Y's saving throw vs Fireball from X (petrification/polymorph): d20 = 6, doubled against fire = 12 +1 Blessed = 13, needs 11 (80% to save) -> saved: half damage, 19 of 38` | A saving throw: which of the target's five saves it uses, the d20, each of the game's modifiers by name (see [The game's saving throws](#the-games-saving-throws); anything the log can't account for shows as `other`), and the number it had to reach. With the [rule changes](#rule-changes) off, the game uses petrification/polymorph for almost every spell and doubles the d20 against fire, cold and electricity spells, as here (see [The game's saving throws](#the-games-saving-throws)); with them on (the default), the line names the spell save and DEX's adjustment instead (`+5 DEX 21 dodging`). A natural 1 always fails and a natural 20 always saves. The chance of saving is worked out for you (`needs 14 (70% to save)`); with the game's doubled d20, Fireball's victims usually save. For a damaging spell the result says what the save left, from that target's damage roll just before it: `saved: half damage, 19 of 38`, `failed: full damage, 38`, or `saved: no damage` for spells such as Chill Touch. The HP line after it shows what the creature really lost, once resistances and protections have had their say. A failed save also lets the spell's effect take hold. Spells left on the ground (Grease, clouds) make creatures save again as they stay in them; those lines have no "from". |
| `X gives Blessed to Y, Z: +1 to hit, +1 on saves` / `Blessed ends on Y` | A spell or psionic effect starting or ending, with what it does in the game's code where that is known: to-hit, AC and saving throws, movement and attacks, whether the creature can attack or cast, who controls it (see [Spells and effects](#spells-and-effects)). `Stuck on Y` (no "gives") is an effect a creature has from a spell on the ground or cast on itself. |

**Checks, thief skills and searches**

| Line | Meaning |
|---|---|
| `X DEX check: d20 = 9, needs 16 or less (DEX 16) -> success` | An ability check. A natural 20 always fails. |
| `Cilla tries to open locks: d100 = 35, needs 40 or less -> success` / `    open locks 40 = 18 + 16 thief level 4 + 10 elf...` | A thief skill roll (see [How the game works out thief skills](#how-the-game-works-out-thief-skills)), and what its chance is made of. |
| `Cilla hides in shadows: d100 = 21, needs 27 or less (54, halved in daylight) -> hidden` / `  Cilla moves silently: ...` | A thief's or ranger's hiding and moving silently at the start of their turn (with [hiding to backstab](#hiding-in-shadows-to-backstab) on). |
| `    X's special effect on Y: d10 = 1, works on a 1 -> it works` | The 1-in-10 extra effect some creatures' hits have (the thri-kreen bite, for one). |
| `    X's Bone Long Sword nearly broke: 0 on 0-7, then 12 on 0-19 (needed 0)` / `... BREAKS` | The weapon check the game makes after an attack sequence whose last attack hit. Only non-magical wood, bone, stone and obsidian weapons can break (and not every kind: clubs and quarterstaffs can't): they break when a 0-7 roll and then a 0-19 roll both come up 0, 1 chance in 160. The line only appears when the first roll comes up 0. |
| `  Rampager's acid on Gerakis's Leather Chest Armor: d20 = 12, needs 10 (AD&D's, 10 for leather; the game's: destroyed without a roll) -> safe` | An item the Rampager's acid or the Babau's corroding touch could destroy: the d20, the number it needed and whose number that was (see [Items saving against acid](#items-saving-against-acid)). |
| `Haystack searched: 0-10 = 7, an old, soiled loincloth (the party's 2nd find of 6 in hay)` / `  The rat's bite: 0-4 = 3 damage` | Searching a junk pile, a haystack or a wardrobe: the game's roll, what it found, and how far its count has got (see [Searching junk, hay and wardrobes](#searching-junk-hay-and-wardrobes)); a rat's bite or a falling pot rolls its damage the same way. |

**Hit points, kills and levels**

| Line | Meaning |
|---|---|
| `  Slig now 8/18 HP (-10)` / `  Gerakis now 51/54 HP (+1)` | Any combatant's hit points going down or up, with what's left out of their most. The game never shows a monster's HP; this does. The line comes just after the damage that caused it (sometimes after the next roll, when the game is quick). |
| `  Gerrard regenerates 1 HP (CON 22), now 16/35 HP` | A hit point back by itself: the game gives one now and then to anyone with CON 20 or more (in the game, CON 20 regenerates and 18 or 19 don't). |
| `  Rampager now 69/72 HP (-3: 3 of the 7 rolled, non-magical weapons do half)` / `  Mastyrial takes none of the 6 damage: crushing weapons can't hurt it` | A weapon hit that took less than its roll, or none at all (no HP lost three seconds on, or by the next round), with the reason when the monster's own defences give one (what weapons hurt it); otherwise "a protection or resistance took it" (Stoneskin, say). |
| `Slig is killed` | A creature dying. What it's worth comes on the XP line below, only if the party gains it (the opening fight in the arena gives none, whoever dies). |
| `XP: Gerakis +67, K'ratchek +22, ... (for Slig 270)` | Experience the party got, and for which kills, with each one's XP from its character sheet. The game gives it right after the kill: an equal share to each character, split again between a multi-class character's classes (the sheet counts XP per class, so a three-class thri-kreen shows a third of the share). |
| `Cilla is now a 3rd level Ranger` / `    max HP 15 -> 21 (+6)` | A level gained, and the new maximum HP. |
| `    max HP unchanged: the game divides the hit point total by the classes, ...` | A multi-class character gained a level and its most hit points stayed the same: every class level rolls its die, but the game divides the whole total by the number of classes, so a small roll can add only a fraction (it counts at a later level). A human who changed class gets none in the new class until its level passes the old class's. |
| `Cilla's 3rd Ranger level: hit points d10 = 2, raised to 3 for CON 21` | The hit point roll for a new level: the class's die (d8 clerics and druids, d10 fighters, gladiators and rangers, d4 preservers, d6 psionicists and thieves; three [kits](#kits) have their own), never less than 2, 3 or 4 with CON 20, 21-22 or 23+, and doubled for half-giants. After level 9 or 10 there's no roll, just a fixed gain (thieves roll at 10th too with [levels up to 10](#levels-up-to-10)). With [the better of two](#hit-dice-the-better-of-two) both rolls show (`d10 = 2 and 7, the better 7`), and with [multiclass hit points](#multiclass-hit-points) CON's bonus on the die (`, +4 CON 18, into the total shared by 3 classes`). |

**Character creation**

| Line | Meaning |
|---|---|
| `Character creation, STR 17: best of four 4d4 (7, 11, 9, 10) = 11, +4, +1 dwarf = 16, raised to 17 (the Fighter's prime requisite)` | An ability score rolled on the character creation screen (see [Character creation](#character-creation)). The die rolls a whole character several times while it tumbles, faster than the log can read every roll, so the helper keeps each ability's last four 4d4 itself; the log gives only the character the die stops on, once it stops, each ability checked against the one the screen shows. A hit point roll that came too fast to record leaves a note: `some of its rolls came too fast to record`. |
| `Character creation: the six scores add up to 101` | After the scores, what they add up to: the most they may add up to with [Scores and hit points as rolled](#scores-and-hit-points-as-rolled). |
| `Character creation, hit points 15: Fighter d10 per level: 7 + 9; Thief d6 per level: 5 + 1 = 22, / 2 classes = 11, +4 CON 16 = 15` | The new character's hit points: a die for every level of every class, divided by the number of classes, plus CON's bonus (see [Character creation](#character-creation)). With [the better of two](#hit-dice-the-better-of-two) each die shows both rolls (`10 (the better of 2 and 10)`); with [multiclass hit points](#multiclass-hit-points) CON's bonus goes on each die before the total is shared (`+2 CON 16 on each of 4 dice = 30, / 2 classes = 15`). |
| `Character creation: a name picked at random, 1d33 = 6` | The game picks a new name from its lists when the sex or race changes. |

**Everything else**

| Line | Meaning |
|---|---|
| `Message: Long Sword is broken !` | The game's own message boxes: broken or corroded weapons and armour, level-ups, "NO PATH FROM HERE" and so on. |
| `Dinos cooks the vulture and the party eats with him: ... restored as after a full rest (HP, PSP and spell slots); the game gives each 100 XP` | Dinos asked about the cooked vulture (see [The cooked vulture](#the-cooked-vulture)); the XP itself is on the `XP:` line after it. |
| `Dice: 1d8 = [3] = 3` | Dice the log couldn't tie to anything (for example a spell with no saving throw). |
| `(The Ledger stopped one of its own writes over the game's memory: ...)` | A safety net: the Ledger never writes over the start of memory (the interrupt vectors, the BIOS's and DOS's data) or the first bytes of the game's data, which its C runtime checks ("Null pointer assignment"). Such a write could only come from a pointer the game has left empty for a moment; the line says where in the Ledger it came from. Please report it. |

The log keeps its newest line in view. Scroll up to read back and it stays
where you are; scroll to the bottom again and it follows the new lines once
more. The Dialogue tab does the same.

**Show unlabelled rolls**, beside it, also lists everything else the game randomises
(creatures wandering, animations and so on), as raw numbers with where in the
game's code they came from. It's noisy, but useful for finding more rolls worth
labelling.

## How the game works

What the game does that its manual doesn't say, from its code and checked in play. The dice
log shows each as it happens, and the [rule changes](#rule-changes) change some of it.

### Initiative

From the game's code: at the start of every round each combatant's initiative
is 20 + a roll of 0-9 + a DEX adjustment + Hasted +2, Slowed −2 and Blind −2.
The DEX adjustment has its own table: −6 at DEX 1, −4 at 2, −3 at 3, −2 at 4,
−1 at 5, none for 6-15, +1 at 16, +2 at 17-18, +3 at 19-20, +4 at 21-23 and
+5 at 24-25. The weapon makes no difference (there are no weapon speeds). The
highest score acts first; a second roll, 0-199, decides between equal scores
(the log shows it only for those). Choosing Wait lowers the character's score
to 10 (or by one, if it's 10 or less already) so they act later in the round.

### Spells and effects

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
- Mirror Image: 1 a level + 1d4 images. Each weapon attack has a 75% chance to
  hit an image.
- Invisibility: one attack or hostile spell ends it. Improved Invisibility is
  timed instead, so attacking doesn't end it.
- Minor Spell Turning: one spell turned back.

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
| Berserk | Fights for a side picked at random each turn; can't cast |
| Can't Attack (Stinking Cloud) | Can't attack or cast harmful spells |
| No spell use, Feeblemind | Can't cast spells |
| Blind | AC 4 worse, −2 initiative, can't cast spells that need sight |
| Acid (Acid Arrow) | 2d4 acid damage each round |
| Poisoned | Fatal (1000 damage) if time passes out of combat, for instance resting, before it wears off or is cured |
| Cloak of Fear | Whoever hits the wearer has Cause Fear cast on them, once |

Other things the game does its own way:
- Cause Serious Wounds rolls 2d9, and Cause Critical Wounds 3d9 (AD&D: 2d8+1
  and 3d8+3). The Cure spells are 1d8, 2d8+1 and 3d8+3 as in AD&D.
- Strength adds 1d6 to STR while it lasts, up to 24. The same goes for
  the psionic Adrenalin Control, and Weakened or lending strength takes it away
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

The spell's area catches its caster too. Cilla's Scare made her Afraid, and her
Fireball, cast at a Slig next to her, killed her.

### Psionics

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
  (`    K'ratchek spends 18 PSP (52 -> 34)`).
- **Psionic defence.** Attacked by a psionic attack mode (Psychic Crush, Ego
  Whip, Id Insinuation, Psionic Blast), a character automatically raises the
  best defence mode they know and can pay for, and pays its PSP.
- **Mind Bar** adds 75% magic resistance against mind-affecting spells:
  charms, holds, Scare, Confusion, Chaos, Feeblemind, Minor Malison. The log's
  magic resistance line counts it, and Lower Resistance halving the result.
- **Body Weaponry** makes unarmed attacks 2d4; **Animal Affinity** at least 1d10.
- Monsters use them too: the Screamer Beetle's special attack is Psychic
  Crush (1d8, save vs paralysis/poison/death for half).

What each costs, from the game's own table (it differs from the books in
places: Enhanced Strength and Domination cost nothing to start):

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
| Enhanced Strength | psychometabolism | 0 | 8 |
| Flesh Armor | psychometabolism | 8 | 4 |
| Graft Weapon | psychometabolism | 10 | 1 |
| Lend Health | psychometabolism | 4 | — |
| Share Strength | psychometabolism | 6 | 2 |
| Domination | telepathy | 0 | — |
| Mass Domination | telepathy | 0 | — |
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

### Character creation

Every click of the die on the creation screen (and every change of race or sex)
rolls a new character. From the game's code, and checked against the screen:

* **Abilities.** Each score is rolled four times as 4d4 + 4 + the race's
  adjustment, and the best of the four counts. That's 8 to 20 before the race's
  adjustment. The score is then raised, if need be, to the least that the
  classes allow: 17 in the class's prime requisite (STR for fighters and
  gladiators, WIS for clerics, druids, psionicists and rangers, INT for
  preservers, DEX for thieves), and otherwise 9 (clerics, fighters, preservers,
  thieves), 12 (druids, psionicists), 13 (gladiators) or 14 (rangers). A
  multi-class character takes the highest of their classes' minimums.
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
* **The total.** After the six scores comes what they add up to, the most
  they may add up to with [Scores and hit points as
  rolled](#scores-and-hit-points-as-rolled).

Changing sex or race can make the game roll hit points twice, once with the
old scores and once with the new: the last hit point line is the one that
counts.

### Monsters' defences

From the game's damage code (DSUN.EXE); none of this is in the manual:

- Every creature has a monster kind, and each kind a resistance class and a
  set of properties, in a table the game fills when it starts.
- Every hit has damage kinds: fire, cold, electricity, acid, poison, draining,
  psionic, death, and for weapons crushing, edged or pointed, from the item's
  type. A weapon's hit also carries its magic: one bit for +1 or better, one
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
  worn item (see [Items saving against acid](#items-saving-against-acid)).
- Undead (race 9 on the character sheet) take nothing from poison and
  draining, and mind-affecting spells, charms and holds don't work on them.

The dice log notes a weapon hit that takes less than its roll, or nothing at
all, with what the monster's defences say about it (`Mastyrial takes none of
the 6 damage: crushing weapons can't hurt it`: the game's mastyrials take
nothing from clubs and maces, only from edged and pointed weapons).

### Searching junk, hay and wardrobes

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

### No critical hits

A natural 20 on an attack always hits, and a natural 1 always misses, but
that is all the d20 does: the game has no critical hits or fumbles. Its attack
routine uses the d20 only for those two checks and the comparison with THAC0,
and never passes it to the damage routine, so a hit on a 20 rolls the same
damage as any other. A backstab is the only thing that multiplies damage.

### The game's two weapons

The manual says a character with two weapons ready uses the second "at a
disadvantage", unless a ranger or dextrous. The game's code does something
else: with two weapons ready (in melee), every attack, first hand and second
alike, is adjusted by the DEX table used for initiative with its sign flipped
and never below 0, and rangers are left out. That comes to a **bonus** of +6 at
DEX 1, +4 at 2, +3 at 3, +2 at 4 and +1 at 5, and nothing at DEX 6 and up, so
in practice there is no off-hand penalty at all: both weapons hit as well as a
single one would. The log names it, e.g. `+2 two weapons at DEX 4`. It looks like a sign slip:
AD&D uses the same DEX adjustment to make two-weapon fighting *harder* at low
DEX.

### How the game works out thief skills

The game never shows thief skills, but it rolls them: for traps, and for the
locks, walls and so on its scripts ask for (see Where the game rolls thief skills). The
roll is a d100 that must come in under the skill's chance. The game's code works
the chance out as:
- a base for each skill (28, 18, 13, 28, 18, 23, 78, −4),
- plus 4 for each thief level,
- plus a racial adjustment. These are AD&D's, for example a dwarf gets +10 to
  open locks, +15 to find traps, −10 to climb walls and −5 to read languages.
- plus DEX: −5 for each point below 12, 11, 12, 13 or 11 (the first five skills);
  +5 for each point above 16, 15, 17, 16 or 16; and −3 for each point above
  21, 20, 21, 19 or 19, so very high DEX gains less,
- minus an equipment penalty (5, 0, 0, 10, 5, 0, 10, 0) when the thief has
  anything at all in the leg armour slot, the quiver or either hand. That is the
  game's own check: it doesn't look at what the item is (leather or metal) and
  ignores chest and arm armour and helmets, so a thief holding any weapon pays
  it. (The manual's "anything other than leather-type armor" is AD&D's rule,
  not what the code does.) In games started with the dice log there is no
  equipment penalty at all: the slots are a list in the game's data
  (legs, quiver, left hand, right hand), and the dice log's
  copy of the game empties it. The Ledger reads the list from the running
  game, so its numbers match whichever game it is.
- plus the situation's bonus or penalty (a hard lock, say).

With **Thief skills from AD&D's table** ticked (see
[Thief skills from AD&D's table](#thief-skills-from-adds-table)), the first
two and the DEX part are AD&D's instead.

Only characters with thief levels have the skills; everyone else's chance is 0.
The character's condition must be Okay (the status the character screen shows
under HP): a thief who is
Stunned, Out Cold, Dying and so on can't use the skills. A character not yet
played (New, before the game starts) counts as Okay, so a party's thief skills
show while it is made (see [More characters](#more-characters)).

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

The game gives the skills no names. The eight are AD&D's in AD&D's order (pick
pockets, open locks, find/remove traps, move silently, hide in shadows, hear
noise, climb walls, read languages): the checks above fit them.

### Where the game rolls thief skills

There is no hide or sneak command, and nothing in the game's code rolls a thief
skill on its own: every roll comes from the game's scripts (conversations,
doors, walls...), which ask in two ways. Every script in GPLDATA.GFF decodes
(see `dscompanion/gpl.py`), so these are all of them:
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

A party check always goes to the member with the best chance. (The game also
has a script command that lets each member try in turn, but no script uses it.)

**Move silently, hide in shadows and read languages are never rolled** anywhere
in the game, so they make no difference; nor does the equipment penalty on
them. (The Ledger rolls move silently when a pocket isn't picked, see
[Picking pockets](#picking-pockets), and hide in shadows and move silently in
fights, to [backstab](#hiding-in-shadows-to-backstab).) The scripts also make
3 ability checks (a d20 under the ability): CHA twice and STR once.

`python -m dscompanion checks` lists them all with the script's text around
each (spoilers).

The **Characters** tab shows each thief's chances as they stand, with the
equipment penalty (none in games started with the dice log) and effects (but
not the situation's bonus or penalty), for the five skills the game rolls
(pick pockets, open locks, find/remove traps, hear noise, climb walls) and
the two the Ledger rolls: move silently (when a pocket isn't picked, see
[Picking pockets](#picking-pockets)) and hide in shadows (to
[backstab](#hiding-in-shadows-to-backstab)), with any Thieves' Tools carried.
**All fields** has them in a row (`PP/OL/FT/MS/HS/HN/CW`).

![Cilla's card on the Characters tab: Thieves' Tools carried, and her thief skills now, move silently and hide in shadows among them](docs/thief-card.png)

### Attacks from behind and backstabs

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

Which weapons can backstab, the game's and the [Ledger's](#new-items), magic
ones included. Weight belongs to the weapon's type and
material, in the game's units, which look like tenths of a pound (a dagger is
10, a club 30, a mace 100, as AD&D's 1, 3 and 10 lb), so the limit is 4 lb.
Missile weapons (slings, bows, a thrown chatkcha) never backstab: it has to be
melee.

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

### The game's saving throws

From the game's saving throw routine. The spell names which of the character
sheet's five saves to use; a natural 1 always fails and a natural 20 always
saves; otherwise the d20 and the modifiers below must reach the save's number.

**Petrification/polymorph for almost every spell.** The game's code maps the
spell's save kind 5 to the sheet's third save; kind 1 is
paralysis/poison/death, used by the clouds, Poison, Slay Living and the
psionic attacks. The spell save, the one AD&D uses for spells, is never used:
a 3rd-level warrior needs 13 against Psychic Crush (paralysis) and 14 against
Fireball (petrification), where the spell save would be 16.

**Fire, cold and electricity: the d20 counts double.** Each spell's record
has a word of flags saying what kind of damage it does, and the saving throw
code doubles the d20 whenever the kind is fire, cold or electricity.
Nothing else is
doubled: not acid (Acid Arrow), crushing (Ice Storm, Magical Stone), poison
(Cloudkill), draining (Vampiric Touch, the Cause Wounds spells) or the
psionic attacks. The doubled spells are:
- fire: Burning Hands, Flaming Sphere, Fireball, Flame Arrow, Minute Meteors,
  Fire Shield, Wall of Fire (both), Focus Heat, Produce Fire, Flame Strike;
- cold: Chill Touch, Cone of Cold;
- electricity: Shocking Grasp, Lightning Bolt.

In between a 1 and a 20 the doubled roll makes saving far easier: needing 14,
a normal d20 saves 35% of the time and a doubled one 70%, which is why
Fireball's victims usually get away with half damage. It isn't AD&D, and the
game never explains it; it may have been meant as a dodge. The log says it on
each save: `d20 = 7, doubled against fire = 14`. The two
[rule changes](#spells-saved-against-with-the-spell-save) below put the spell
save back and take the doubled d20 away.

The target's spells and effects:
- Blessed +1, Barkskin +1, Spirit Armor +3 (but not on
  paralysis/poison/death saves), and the Save penalty effect -1.
- Prayer: +1 if its caster is on your side, -1 if not.
- Protection from Evil +2 against an evil caster (lawful, neutral or chaotic
  evil); Protection from Fire and from Cold +3 against fire and cold spells;
  Protection from Lightning +4 against electricity.
- +4 against a spell aimed at one target (not an area) when the caster can't
  see you: the caster is Blind, or you're Invisible (or Invisible to Undead,
  against an undead caster) and the caster can't detect invisibility.

Class, race and abilities:
- WIS, against mind-affecting spells, charms and holds, fear and illusions:
  -6 at WIS 1, -4 at 2, -3 at 3, -2 at 4, -1 at 5-7, +1 at 15, +2 at 16,
  +3 at 17 and +4 at 18 and up.
- CON, on paralysis/poison/death saves: -2 at CON 1, -1 at 2, +1 at 19-20,
  +2 at 21-22, +3 at 23-24 and +4 at 25. Dwarves and halflings also add
  CON x 2 / 7 (+1 for every 3.5 points).
- Druids +2 against fire and electricity; psionicists +2 against
  mind-affecting spells and charms.
- Some spells carry a modifier of their own (a monster's poison at -4).

Spells with rules of their own: creatures of 6th level or lower can't save
against Cloudkill; against Chaos only warriors (fighters, gladiators and
rangers) can; against Dismissal the target adds its level and takes away the
caster's; and against Scare, 6th level and up always save and everyone below
can't. The Scare code looks meant to let some elf or half-elf priests save
(AD&D gives elves, half-elves and priests a bonus), but it asks for a
creature that is both an elf and a half-elf, so no one qualifies.

Rules in the code that never come into play: Cloak of Bravery's +4 against
fear applies only to a kind of spell that no spell in the game is marked as,
and so does AD&D's DEX defensive adjustment for attacks that can be dodged
(+5 at DEX 1 to -6 at DEX 25 on AC, so -5 to +6 on the save), unless the
[rule change](#rule-changes) puts it on the fire, cold and electricity spells. And nothing in the game gives saves from items: there
are no rings or cloaks of protection, which is why the Ledger adds
[a ring](#new-items) and [a cloak](#new-items). Their +1 is in the
log's saving throws as `+1 Ring of Protection` and `+1 Cloak of Protection`
(with [AD&D's rules for them](#rings-and-cloaks-of-protection) off, all of it
as `Ring of Protection`).

## In the game

The game itself shows more, in its own lettering and windows, when it is started
from the Ledger (or either `.bat` file).

### THAC0, saves and thief skills

Started with the dice log, the game's own inventory screen (the one with the
character's figure and their equipment) shows five more things in its
right-hand panel, drawn by the game's text routine so they look like the rest:

![The inventory screen's panel in the game: THAC0 and the saves at the top, Daaki's thief skills (move silently and hide in shadows among them) beside the abilities, his DEX reaction and defensive adjustments, and a club in each hand: 1.5 attacks a round with the right, one with the off hand](docs/inventory.png)

![A ranger's panel: Dream's move silently and hide in shadows, for hiding to backstab, where a thief's go](docs/inventory-ranger.png)

- above STR, **THAC0** and the five **saving throws**, with the usual AD&D
  short labels: `PPD` paralysis/poison/death, `RSW` rod/staff/wand, `PP`
  petrification/polymorph, `BW` breath weapon, `SP` spell;
- at the right of each weapon's damage line, the THAC0 with that weapon
  (`T14`);
- right of the abilities, level with STR to CHA, for a character with thief
  levels, six **thief skills**: `PICK` pockets, open `LOCK`s, find/remove
  `TRAP`s, `MOVE` silently, `HIDE` in shadows and `CLMB` walls. Move silently
  and hide in shadows are the ones the Ledger rolls (for
  [picking pockets](#picking-pockets) and [hiding to backstab](#hiding-in-shadows-to-backstab)).
  A worn belt's 5 is in `PICK` and `LOCK`. Hear noise (one script check) and
  read languages (none) are left out for want of room. A ranger, with
  [hiding to backstab](#hiding-in-shadows-to-backstab) on, gets their `MOVE` and `HIDE` in the same places (the other four left out);
- right of SP in the saves (where RSW and BW sit on the rows above), the DEX
  **reaction adjustment** (`REAC +4`): -6 at DEX 1 to +5 at DEX 24-25, the
  number the [two-weapon rule](#two-weapons) adds to its penalties, and the
  one initiative uses. It is worked out from the character's DEX each time
  the panel is drawn, so it follows any change (Cat's Grace's, while it
  lasts).
- right of the AC line, the DEX **defensive adjustment** (`DEF -5`), as
  AD&D's table gives it, on AC: +5 at DEX 1 to -6 at DEX 24-25 (-4 at 18, -5
  at 21-23). The game counts it in AC already; on saving throws against what
  can be dodged it counts the other way round (DEF -5 is +5 on the save), with
  the [rule change](#rule-changes) for fire, cold and electricity. Worked out
  the same way as REAC, each time the panel is drawn.

The **View Character** screen gets them too: the five saves under the item
icons, each with its label as above (`PPD 11  RSW 9` / `PP 10  BW 13` /
`SP 10`), and in the lower panel, right of HP and PSI as DAM is right of AC,
the character's **MOVE** (its movement in a fight, before boots or a spell
change it) and **THAC0**.

![The View Character screen: the saves labelled under the item icons, and MOVE and THAC0 beside HP and PSI](docs/view-character.png)

They're the numbers as they stand now, worked out by the Ledger the way the
game's own attack and saving throw routines do. Each time the game draws one
of these screens, the helper has the Ledger bring them up to date first (the
game waits a moment for it), so putting on a ring or readying another weapon
shows at once. Spells start and end as time passes in the game, which it
doesn't while these screens are open; open the screen again to see such a
change.

- **THAC0**: the character's THAC0 less STR's to-hit adjustment (DEX's for a
  missile weapon), the weapon's plus (or, for a plain wooden, bone, stone or
  obsidian weapon, its material's penalty), Bless and Prayer (+1), Curse
  (-1), Slow (-4) and Graft Weapon (+1). The THAC0 at the top is the main
  weapon's: the right hand's, else the left's, else the missile weapon's.
  What depends on the target (attacking from behind or backstabbing, a Blurred
  target) is left out; the dice log shows it on each attack.
- **Saves**: the d20 each needs, the character sheet's number less what the
  game adds to every save: the [Rings of Protection and the
  Cloak of Protection](#rings-and-cloaks-of-protection), Bless, Prayer,
  Barkskin, Spirit Armor (not on PPD), the Save penalty, and on PPD the CON
  adjustment (and a dwarf's or halfling's CON bonus). What depends on the
  spell or its caster (WIS against mind spells, Protection from Fire, a
  doubled d20 against fire...) is left out; the dice log shows it on each
  save. A 1 always fails and a 20 always saves, so they show between 2 and 20.
- **Thief skills**: as they stand (with no equipment penalty in games started
  with the dice log: see [How the game works out thief skills](#how-the-game-works-out-thief-skills)), 0 for a skill an effect rules out or when the thief isn't Okay (New counts as Okay),
  and 100 for one an effect makes certain (Detect Traps). Only the situation's
  bonus or penalty (a hard lock) is left out: the dice log shows it on each
  roll.

The Characters tab shows the same THAC0 with each weapon and saves. The
game's own numbers (the character sheet's) come back on these screens when
the Ledger isn't running.

**The next level's class.** For a character of more than one class, the number in brackets on View
Character's experience line is the XP at which the first of their classes
goes up a level, and the Ledger adds which class that is:
`EXP:87230 (90000 Pr)` means the preserver goes up next, at 90,000. Each
class is a letter, except preserver and psionicist, which both start with P:

| Class | Letters |
|---|---|
| Cleric | C |
| Druid | D |
| Fighter | F |
| Gladiator | G |
| Preserver | Pr |
| Psionicist | Ps |
| Ranger | R |
| Thief | T |

When two classes go up at the same XP, both are named:
`(20000 Pr/T)`. A class already at the highest level (9, or 10 with
[levels up to 10](#levels-up-to-10)) has no next level, so it is never named.
A character of one class shows the line as the game always has, and so
does a human, who can only dual-class: the game counts only one of their
classes there.

![View Character's experience line for a fighter/thief, (110000 T), and a fighter/preserver/thief, (90000 Pr)](docs/xp-next.png)

How it works: [DEVELOPMENT.md](DEVELOPMENT.md#thac0-saves-and-thief-skills).

### Spell slots on the USE screen

The game's USE (cast spells) screen shows, at the top of the panel under the
spells, how many spells of each level the selected character can still cast,
and the most they get after resting: `WIZ` for preservers' wizard spells, `PRI`
for clerics', druids' and rangers' priest spells, one `left/most` per spell
level from the 1st (six to a line), up to the highest level the character can
cast (more appear as they level up):

![The USE screen with K'ratchek's spell slots: a 2nd-level druid, five first-level spells](docs/use-slots.png)

The numbers go down as spells are cast (the screen shows the new count when it
is next drawn) and back up after resting. That panel is where the game puts
the icons of the character's usable magic items (fruit, wands and the like),
along its bottom from the left, so the slots take only the three lines above
them: a character with both wizard and priest spells gets the two lines without
the `SPELLS LEFT BY LEVEL` heading.

The numbers are the Characters tab's (see [spell slots](#the-characters-tab)), WIS bonus included,
printed with the game's own text routine; they show while Templar's Ledger (or
its command-line dice log) is running.

### Each turn's rolls

With **Show each turn's rolls in the game** ticked on the Options tab (it is
off unless you tick it; or `python -m dscompanion dicelog --popups`), the game
stops at the end
of every turn in a fight in which someone attacked or cast a spell, and shows
that turn's rolls in its own dialogue window, with **Continue** to go on. Below
the box, pick how much it says: **at the least**, **in short** or **in
detail**. In detail, they are the dice log's own lines: each attack's d20, the AC it would hit and the
target's AC, how the THAC0 was worked out, and for a hit the damage dice and
bonuses; a spell's damage dice, and each saving throw against it. (The chance
to hit or to save is left out: the log has it.) The last line says who is
still to act this round (`Still to act this round: Jellybelly, Mountain
Stalker`), `End of round 2.` when everyone has, or, when the new round's
order is already in, that order (`Round 3: Dreamwalker, Jellybelly, Mlemlem,
Daaki`). The window shows five lines at a time; its **MORE** arrow shows the
next ones:

![The game's window at the end of a turn, in detail](docs/turn-detail.png)

![The game's window after Daaki's Fogbolts: the dice for how long it lasts, and the Wild Mul's saving throw](docs/turn-spell.png)

**In short** (or `--short-popups`) gives one line per target instead (and each
spell's first line):

![The game's window at the end of Mlemlem's turn, in short](docs/turn-summary.png)

`20 vs 11+ HIT, 12 damage` is the d20, the roll it needed (THAC0 − the
target's AC; a natural 20 always hits, a 1 always misses), and the damage the
hit did.

**At the least** (or `--minimal-popups`) gives only what came of the turn, no
dice: `Mlemlem hits Mountain Stalker for 12, misses. Slig takes 9 from
Fireball`. It leaves out who is still to act.

Each turn gets its own window, monsters' included. Only fights the party is in get them:
the fights the game stages without the party, such as the Defiler's show at
the start of the arena, are run by scripts waiting on the same dialogue window,
and a window of ours there would let the script go on before the fight ends.

How it works: [DEVELOPMENT.md](DEVELOPMENT.md#each-turns-rolls).

### What hurts a monster (the Look box)

In a fight, Look at a monster (right-click until the cursor is the Look icon,
then click the monster) and the game's small box, under its name and level,
now also shows its hit points and AC (`HP 15/15 AC 2`), its THAC0 and
alignment (`THAC0 17 AL TN`), its magic resistance beside its level
(`LEVEL: 3   MR 30`), and its most important defence: `NEEDS +1 WEAPON`,
`IMM FIRE COLD`, `NO CRUSH`, `HALF FROM WPNS` or `UNDEAD`. The alignment is in
two letters: `LG`, `LN`, `LE`, `NG`, `TN`, `NE`, `CG`, `CN` or `CE`. (A line
that would run past the box's edge, such as a monster's with over 100 HP, loses
its spaces.) Its own status lines (casting, charmed, held...) follow in any
row left. When there's more to say, closing
the box shows everything in the game's dialogue window: the weapons it needs,
the damage it's immune to or takes half of, spells that don't work on it, and
what its hits do besides damage. The dice log gets the same lines (`Look:
...`). Untick **Describe monsters when you Look at them in a fight** on the
Options tab to turn this off.

![The Look box on a Screamer Beetle in the arena: LEVEL: 3, then HP 15/15 AC 2 and THAC0 17 AL TN added](docs/look-box.png)

(The arena's first monsters, like the people in the early fights, have no
magic resistance or special defences, so the box shows just the numbers and
the alignment.)

How it works: [DEVELOPMENT.md](DEVELOPMENT.md#what-hurts-a-monster-the-look-box).

### Charges in item boxes

An item that casts a spell with charges (the wands, the Storm Ring, the
necklaces) shows how many it has left in its item box (right-click it on the
inventory screen), under its name, counting down as it's used:

![The Wand of Missiles' item box in the game: 65000 coins, "Wand of Missiles", "Charges: 50"](docs/wand-charges.png)

### No manual check

The game's copy protection is gone. Leaving the sewers (the Tari's warrens) the
first time, the game has a dragon appear and ask for a word from the manual
("The 3rd word on page 14, line 1, begins with the letter 'p'. What is that
word?"), and three wrong answers kill the party. Started from the Ledger, the
dragon doesn't come: the game goes on as if it had been answered. Always on.

How it works: [DEVELOPMENT.md](DEVELOPMENT.md#no-manual-check).

## Rule changes

Fourteen changes that bring the game's own rules closer to AD&D, each with
its own box in the Options tab's **Rule changes** section. All are on by
default, and they take effect in games started with the dice log: with the
Ledger running, or with **Play Dark Sun (in-game rolls)**, which uses the
Options as last set. Untick one and the game's own rule is back at once. [How
the game works](#how-the-game-works) has what the game does without them.

| Rule (its box on the Options tab) | What it changes |
|---|---|
| [Class restrictions](#class-restrictions) | each class's limits on armour, shields and weapons hold, the strictest winning; a multiclass preserver casts no spells in armour |
| [Multiclass hit points](#multiclass-hit-points) | CON's bonus on every hit die (a warrior's for a character with a warrior class), the total shared between the classes |
| [Hit dice: the better of two](#hit-dice-the-better-of-two) | each hit die rolled twice, the better kept, for every character |
| [Scores and hit points as rolled](#scores-and-hit-points-as-rolled) | on the creation screen, a click raises a score only while the six add up to no more than the die gave (lower one to raise another), and doesn't change the hit points |
| [Rangers' casting level](#rangers-casting-level) | a ranger's spells last and do damage as cast at its level less 7, as the spell levels it may cast already count it |
| [Preservers' INT](#preservers-int) | INT gives a preserver a chance to learn a spell from a scroll, and the most spells of each spell level it may know |
| [AD&D's class tables](#adds-class-tables) | the XP for each level, priests' THAC0, and clerics', druids' and preservers' spell slots from AD&D's tables |
| [Spells saved against with the spell save](#spells-saved-against-with-the-spell-save) | the spell save rather than petrification/polymorph |
| [Fire, cold and electricity: DEX instead of a doubled d20](#fire-cold-and-electricity-dex-instead-of-a-doubled-d20) | DEX's defensive adjustment on those saves rather than a doubled d20 |
| [Two weapons](#two-weapons) | -2 main hand, -4 off hand, DEX's reaction adjustment added; rangers none in light armour; the off hand attacks once a round |
| [Items saving against acid](#items-saving-against-acid) | an item the acid or corroding touch could destroy needs the easier of the game's number and AD&D's save by material, a plus helping |
| [Rings and cloaks of protection](#rings-and-cloaks-of-protection) | two rings don't add up, a ring gives no AC with magical armour, a cloak does nothing with magical or metal armour or a shield |
| [Half-giants' two-handed weapons](#half-giants-two-handed-weapons) | a half-giant wields a two-handed weapon in one hand |
| [Helms give AC 1](#helms) | the game's helms give AC 1 rather than 0 |

### Class restrictions

With **Class restrictions** ticked, a character's classes keep it from
armour, shields and weapons as in AD&D, the strictest class winning. The game
checks only that one of the character's classes may use an item; with the rule
the others must allow it too, and putting on what one forbids gets the game's
own "Cannot use this item":

| Class | Armour and helms | Shields | Weapons |
|---|---|---|---|
| **Psionicist**, whatever its other classes | light only (leather, hide, silk: Drake, Shimmer and Silk Armor) | leather only | daggers, short swords, maces, clubs, chatkchas, bows and slings |
| **Thief**, multiclass | light only | a leather one, and only if another of its classes allows shields | as its classes allow |
| **Preserver**, one class | none | none | as the game has it |
| **Druid** | none | none | any |
| **Cleric** | any | any | its sphere's: air missile and thrown weapons and daggers; earth stone, obsidian, metal and wood; fire obsidian; water bone and wood |

A **multiclass preserver** may wear what its other classes allow, but casts no
spells (wizard or priest) while wearing armour (a helm counts, a shield
doesn't), as the game's own "No spell use" stops them. The **USE** screen
heads its spell slots **NO SPELLS IN ARMOUR**, and the Characters tab adds
"(no spells in armour)" to them. A human who has
changed class is held by the class it has now; another race by all of its
classes. A ranger turned cleric uses both spheres' weapons, and a warrior who
dual-classed uses the weapons it specialized in once the new class's level
passes the old (a fighter's, gladiator's or ranger's chosen weapon specs, and a
ranger's bow). A ranger's bow is always its own: a fire ranger/cleric, whose
fire sphere allows only obsidian weapons, may still use bows. Cloaks,
the Cloak of Protection among them, aren't armour: any class may wear one.

A new character starts without the weapons, armour and shields its classes
can't use. The game gives a character of several classes each class's gear,
and puts what it may not wear in the backpack: the Ledger leaves that behind
and says so in the dice log (`Yilballa's Chest Armor is left behind: their
classes can't use it`, for a druid's leather armour given for its fighter
class).

How it works: [DEVELOPMENT.md](DEVELOPMENT.md#class-restrictions).

### Multiclass hit points

With **Multiclass hit points** ticked, a character of more than one class
gets its hit points as *Demihuman Deities* (TSR, 1998) sets out AD&D's rule
for multiclassed characters: every hit die it rolls, at creation and at each
level, gets CON's bonus, goes into a running total, and the total divided by
the number of classes (dropping fractions) is its most hit points. CON's
bonus is a warrior's (+3 at CON 17, +4 at 18 and so on) on every die if one
of its classes is a fighter, gladiator or ranger, as a "warrior character";
otherwise at most +2. Dice stop as usual after 9th or 10th level, and so
does CON's bonus.

The game already keeps the total and divides it, but gives CON's bonus only
once a level of the character's highest class, whole: a preserver 5 / thief 6
with CON 18 gets 2 × 11 dice / 2 = 11 hit points from CON with the rule,
rather than the game's 2 × 6 = 12. A human
who dual-classes isn't affected (one class at a time). Ticked during a game, a
character's most hit points change at its next level, when the game works
them out again. The log shows the bonus on each die:

```
Gerrard's 4th Fighter level: hit points d10 = 8, +3 CON 17, into the total shared by 2 classes
```

How it works: [DEVELOPMENT.md](DEVELOPMENT.md#multiclass-hit-points).

### Hit dice: the better of two

With **Hit dice rolled twice** ticked, every character's hit die is rolled
twice and the better roll kept: at creation (one die for each starting level
of each class) and at every level gained. Everything after the roll is the
game's (or the other rules'): CON's least, a half-giant's double, and a
multiclass character's share. It isn't AD&D's, but it softens a bad roll; on
average a d10 gives 7.15 instead of 5.5, a d8 5.8 instead of 4.5, a d6 4.5
instead of 3.5 and a d4 3.1 instead of 2.5. Levels past the dice (a fixed
gain) don't change. The log shows both rolls:

```
Cilla's 3rd Ranger level: hit points d10 = 2 and 7, the better 7
Character creation, hit points 18: Fighter d10 per level: 10 (the better of 2 and 10) + 5 (the better of 5 and 1); ...
```

How it works: [DEVELOPMENT.md](DEVELOPMENT.md#hit-dice-the-better-of-two).

### Scores and hit points as rolled

The game's creation screen lets a click change what the die rolled: a left
click raises a score by 1 (round to the least from the most), a right click
lowers it, and a click on the hit points sets them anywhere the classes could
roll. Every score can go to its most that way. With **Scores and hit points as
rolled** ticked:

* **The six add up to no more than the die gave.** A score may still be
  lowered, and the points it frees raise another. A raise past what's spare
  stops at it, or does nothing when none is spare. The game's least and most
  for each score still hold.
* **The totals show under CHR**, the six's and the die's: `SUM:99/101` has 2
  points to spare. A new roll of the die (or of a new race or sex) sets both.
  A new class can raise a score to its least, as the game does; the die's
  total grows to match if the six then add up to more.
* **The hit points are as rolled**: a click on them does nothing. **CON moves
  them:** raising or lowering CON adds or takes off its bonus for every level,
  as the game counts it (a warrior's full bonus, at most +2 for others), where
  the game only kept them within the new least and most.

The dice log gives each roll's total with its scores:
`Character creation: the six scores add up to 101`.

How it works: [DEVELOPMENT.md](DEVELOPMENT.md#scores-and-hit-points-as-rolled).

### Rangers' casting level

A ranger casts priest spells as a priest of its level less 7, as in AD&D: a
9th-level ranger counts as 2nd level, so it may cast 1st-level spells. The
game counts it so for the spell levels it may cast (and for Dispel Magic),
but a spell's duration and damage take the whole ranger level: that ranger's
spells lasted as a 9th-level priest's. With **Rangers' casting level**
ticked, they take the level less 7 too. A character with another class that
casts the spell (a cleric/ranger of the same element) casts it at the better
of the two, the ranger's counted 7 less. The Seeker's and Justifier's kits
take 5 and 9 off, ticked or not. A 9th-level ranger's Protection from Evil
(3 rounds a level) lasts 6 rounds with the rule, 27 without. The dice log's
duration and damage lines show the level wherever they roll dice.

How it works: [DEVELOPMENT.md](DEVELOPMENT.md#rangers-casting-level).

### Preservers' INT

In the game a preserver learns any spell from a scroll it reads, and may know
every spell. With **Preservers' INT** ticked, AD&D's table for INT holds:

| INT | Chance to learn a spell | Most spells of each spell level |
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
| 20 to 23 | 96% to 99% | all |
| 24 and 25 | 100% | all |

- **Reading a scroll:** the preserver rolls d100 against its chance. Under
  it, the spell is learnt and the scroll used up, as in the game; over it,
  the spell isn't learnt (YOU FAIL TO LEARN THE SPELL) and the scroll is used
  up all the same.
- **A full spell level:** a preserver that already knows the most spells of
  the scroll's spell level can't learn it (TOO MANY SPELLS OF THAT LEVEL),
  and keeps the scroll.
- **Level ups and new characters:** CHOOSE A SPELL leaves out the spells of a
  level the preserver already knows the most of, and doesn't open when
  nothing else is left to learn.

The dice log shows each try: `Dreamwalker reads the scroll of Magic Missile:
d100 = 37, needs 60 or less (INT 14) -> learnt`. Priest spells and psionic
powers are as the game has them.

How it works: [DEVELOPMENT.md](DEVELOPMENT.md#preservers-int).

### AD&D's class tables

The game has tables of its own where AD&D's differ. With **AD&D's class
tables** ticked, AD&D's hold (the [player's guide](GUIDE.md) has them in
full):

- **Experience:** a gladiator needs 2,250 XP for 2nd level (the game uses
  the fighter's table), a ranger 2,250 (2,200) and a thief 1,250 (1,200);
  the rest are as the game has them. View Character's next-level figure and
  the level ups both follow it.
- **Priests' THAC0:** clerics and druids improve by 2 every 3 levels from
  4th (20, 20, 20, 18...), as AD&D's priests do; the game has them improve
  from 3rd (19 at 3rd, 17 at 6th, 15 at 9th). The new THAC0 comes at the
  next level up. Warriors', wizards' and rogues' were AD&D's already.
- **Spell slots:** clerics and druids take AD&D's priest table (3 3 1 at 5th
  level, the game 3 2 1), preservers AD&D's wizard table (4 2 1 at 5th); WIS
  still adds a priest's bonus slots. Rangers' slots were AD&D's already.

Hit points were AD&D's already (with [Levels up to 10](#levels-up-to-10)).
Kits change these as before.

How it works: [DEVELOPMENT.md](DEVELOPMENT.md#adds-class-tables).

### Spells saved against with the spell save

Almost every spell is marked for the game's "kind 5" save, which it treats as
petrification/polymorph; with this rule it is the spell save. The spells
marked for paralysis/poison/death (the poison clouds, Poison, Slay Living, the
psionic attacks) keep it, as AD&D has them, and so do three monsters' powers
marked for petrification/polymorph. The dice log and the Spells tab name the
save used.

How it works: [DEVELOPMENT.md](DEVELOPMENT.md#spells-saved-against-with-the-spell-save).

### Fire, cold and electricity: DEX instead of a doubled d20

The game doubles the save's d20 against those spells (and nine monsters'
attacks of those kinds). With this rule the d20 isn't doubled and
AD&D's DEX defensive adjustment is added instead, as AD&D does for attacks
that can be dodged: -5 at DEX 1, -4 at 3, -3 at 4, ... none for 7-14, +1 at
15, +2 at 16, +3 at 17, +4 at 18-20, +5 at 21-23 and +6 at 24-25. Fireball
stays dangerous for slow targets (needing 14 at DEX 12: 35% to save, where the
doubled d20 gave 70%) and much less so for quick ones (DEX 21: 60%). The log
names it: `+5 DEX 21 dodging`.

How it works: [DEVELOPMENT.md](DEVELOPMENT.md#fire-cold-and-electricity-dex-instead-of-a-doubled-d20).

### Two weapons

With **Two weapons** ticked, a character with a melee weapon in each hand
attacks at -2 with the main (right) hand and -4 with the off (left) hand, plus
the DEX reaction adjustment (the table under [Initiative](#initiative)). That
can bring the penalty to 0 but never make it a bonus, and low DEX makes it
worse: DEX 17 gives 0 and -2, DEX 21 0 and 0, DEX 3 -5 and -7. One weapon, a
two-handed weapon, a weapon and a shield, or a weapon and a bow or sling (the
missile slot) have no penalty. The game's own rule, a small bonus at DEX 5 or
less, is gone.

Rangers (their kits too) and [Twin-blades](#kits) have no penalty in light
armour: every armour piece worn, a helm too, of leather or of no material. In
other armour they take it as anyone does, DEX included. A Justifier has none
in any armour. The dice log names it (`-4 two weapons, off hand at DEX 15`),
as do the THAC0 lines on the Characters tab and the inventory screen.

The off hand attacks once a round, whoever holds it: extra attacks (a
fighter's, gladiator's or ranger's 3/2 from the game, a specialist's,
mastery's, the kits') are the main hand's alone. So a 7th-level Crusader
with a club in each hand attacks 3/2 + 1 a round: 1 + 1 in one round, 2 + 1
in the next. The game gives each hand the whole rate (1 + 1, then 2 + 2).
The off hand's DAM lines (the inventory screen and View Character) show its
one attack.

How it works: [DEVELOPMENT.md](DEVELOPMENT.md#two-weapons-adds-penalties).

### Items saving against acid

Two monsters' hits can destroy an item: the **Rampager's acid** a worn piece
of armour, and the **Babau's corroding touch** a worn piece of armour and the
melee weapon held (the first one in the character's list of held items; bows
and slings never). The game makes the check on every such hit, whether or not
the target's saving throw against the attack succeeds, and shows its own
message when the item goes ("Armor is corroded", "Weapon is corroded"). Only
pieces worn on the arms, legs or chest count, not helms or shields, and at
most one piece of armour is lost to a hit: the first that fails, in the order
of the character's list.

The game's own checks:

- **A weapon** is destroyed on a d20 under 8 less its plus: a plain one 7 in
  20 (35%), a +1 30%, +7 or better never.
- **Armour** with a magical power (Drake Armor, Shimmer Armor) is never
  destroyed. Any other piece is destroyed at once, without a roll, plus or
  no plus: Tanelyv's Armor +2 goes as surely as plain leather. (The game reads
  the byte that holds the item's power, not its plus.)

With **Items save against acid as in AD&D** ticked, each item needs the easier
of the game's number and AD&D's saving throw against acid for its material
(the DMG's table), so no item is worse off than in the game. AD&D's number is
less the item's plus, and 1 less again for a magical power:

| Material | AD&D's number (the DMG's row) |
|---|---|
| Wood | 8 (thick wood) |
| Bone (the game's ring, brigandine and scale armour too) | 11 |
| Stone, obsidian | 5 (glass, the nearest) |
| Metal | 13 |
| Leather | 10 |
| None (Silk Armor) | 12 (cloth) |

| Item | Saved in the game | Saved with the rule |
|---|---|---|
| Leather Chest Armor | 0% | 55% (needs 10) |
| Leather Chest Armor +1 | 0% | 60% (needs 9) |
| Bone scale chest | 0% | 50% (needs 11) |
| Chain chest | 0% | 40% (needs 13) |
| Tanelyv's Armor +2 (metal) | 0% | 50% (needs 11) |
| Drake Armor +1 (a power) | 100% | 100% (the game's) |
| Bone or metal Long Sword | 65% | 65% (the game's: needs 8) |
| Shadowseeker (metal, +1) | 70% | 70% (the game's: needs 7) |
| Obsidian Dagger | 65% | 80% (needs 5) |
| The Ledger's plain bone weapons (Dagger, Short Sword, Axe, Great Axe) | 65% | 65% (the game's: needs 8) |
| The Ledger's plain obsidian weapons (Short Sword, Axe, Mace, Great Axe) | 65% | 80% (needs 5) |
| The Ledger's plain metal weapons (Short Sword, Dagger, Mace, Great Axe, Pick, Polearm) | 65% | 65% (the game's: needs 8) |
| Kreenfang, Drakejaw, Stillwater, Thornwall (bone, +1) | 70% | 70% (the game's: needs 7) |
| Mindshard (obsidian, +1) | 70% | 85% (needs 4) |
| Flame Blade (obsidian, +1, a power) | 70% | 90% (needs 3) |
| Glasshewer (obsidian, +2) | 75% | 90% (needs 3) |
| Deepbiter (stone, +1) | 70% | 85% (needs 4) |
| Gutterknot (wood, +1) | 70% | 70% (the game's: needs 7) |
| Greenbright, Galefang, Headsman, Linebreaker (metal, +2) | 75% | 75% (the game's: needs 6) |

The dice log shows every check, whichever rule is on:

```
Defiler's saving throw vs Acid from Rampager (paralysis/poison/death): d20 = 20 (natural 20) -> saved
  Rampager's acid on Defiler's Metal Chain Leg Armor: d20 = 16, needs 13 (AD&D's, 13 for metal; the game's: destroyed without a roll) -> safe
  Rampager's acid on Defiler's Leather Chest Armor: d20 = 12, needs 10 (AD&D's, 10 for leather; the game's: destroyed without a roll) -> safe
```

The Detonate psionic power, which can blow up an item a target carries, keeps
the game's own rule (a d20 under 15 less the item's plus).

How it works: [DEVELOPMENT.md](DEVELOPMENT.md#items-saving-against-acid).

### Rings and cloaks of protection

The game has no rings or cloaks of protection; the Ledger adds three (the
arena's Ring +1, and Pehtucl's ring and cloak in the slave pens: see
[New items](#new-items)), each +1 to AC and +1 on every
saving throw. With **Rings and cloaks of protection as in AD&D** ticked, they
follow the AD&D rules for them:

- **Two rings don't add up:** only the better one counts (the left hand's,
  if they're equal). The arena's ring and Pehtucl's, both +1, give +1 together,
  not +2.
- **A ring gives no AC with magical armour** (any worn armour piece, helm
  included, with a plus), but still adds to saving throws.
- **A cloak does nothing,** neither AC nor saves, with magical armour, with
  metal armour (Chain, Grey's Scale, Tanelyv's Armor, the Helm of
  Contemplation) or with a shield in either hand. Natural armour is fine:
  leather and bone (Ring, Brigandine and Scale are bone in Dark Sun), and
  plain helms. The cloak still adds to a ring.

Armour here is what is worn on the arms, legs, head or chest; something only
carried in a backpack doesn't count. Untick it and every ring and cloak worn
counts, whatever else is worn (the game's way with the patched game).

### Half-giants' two-handed weapons

Half-giants stand up to twelve feet tall. With **Half-giants wield
two-handed weapons in one hand** ticked, a half-giant can hold a two-handed
weapon (a two-handed sword, a halberd, a bow) in one hand, with a shield or a
light weapon in the other. The game's own rule that the two hands can't both
hold heavy weapons (over 30 in weight each) still stands, so no half-giant
holds two two-handed weapons. With two weapons ready, the two-weapon penalties
apply as for anyone. The inventory screen still writes "2 handed" in the
weapon's line: that is its weapon type, not a limit.

How it works: [DEVELOPMENT.md](DEVELOPMENT.md#half-giants-two-handed-weapons).

### Helms

The game's helms count as armour but give AC 0. With **Helms give AC 1**
ticked they give 1: the plain leather Helm, Dapartea's Helm, the metal Helm of
Contemplation and the Helm of Might (item types 5, 89 and 109, all at AC 0 in
the game's tables). It shows on the View Character and inventory screens like
any armour, and as `AC BONUS:1` in a helm's box (right-click it), worn or not.

The game has no descriptions of items, only their names, so while the rule is
on the Ledger renames the plain helm **Helm (AC 1)**. The named ones
(Dapartea's Helm, Helm/Contempltn, Helm of Might) keep their names, which
would be too long for the game's Look box with the note. With the rule off,
or without the Ledger, the names are the game's own.

How it works: [DEVELOPMENT.md](DEVELOPMENT.md#helms).

## More character customization

More choices for each character: a weapon to specialize in, a kit, a 10th
level to reach, and a roll to keep while trying the die again. Each has a
box in the Options tab's **More character customization** section. All are on
by default and, like the rule changes, take effect at once in games started
with the dice log (STORE and RECALL from the next start); untick one and the
game is as it was.

| Box on the Options tab | What it adds |
|---|---|
| [Weapon specialization](#weapon-specialization) | fighters and gladiators specialize in weapon types, fighters on to mastery and grand mastery, rangers take expertise (and every ranger the bow); specialists and rangers shoot missiles faster; other weapons at a warrior's plain rate (missiles faster from 7th level) |
| [Kits](#kits) | a character of one class takes one of three kits for its class, or none |
| [Levels up to 10](#levels-up-to-10) | every class goes to 10th level (the game stops at 9) |
| [STORE and RECALL on the creation screen](#store-and-recall-on-the-creation-screen) | a roll kept on the creation screen, to bring back after trying the die again |

### Weapon specialization

With **Weapon specialization** ticked, fighters, gladiators and rangers train
in chosen weapon specs (weapon types), as in AD&D. **Every ranger starts
with expertise in the bow**, on top of the weapon spec it chooses.

| Who | Chooses | With a weapon of a chosen weapon spec |
|---|---|---|
| **Fighter** (one class or more) | 1 weapon spec | specialized: +1 to hit, +2 damage; **mastery** from 5th fighter level (+3 to hit, +3 damage); **grand mastery** from 9th (the same, the damage die a size larger, d8 to d10, and one more attack a round) |
| **Gladiator** | 2 weapon specs at creation, a 3rd at 6th level and a 4th at 9th | specialized in each: +1 to hit, +2 damage |
| **Ranger** (one class or more) | **the bow from the start**, and 1 weapon spec (any but the bow) | expertise: the game's attacks a round in melee, a specialist's rate of fire with a missile weapon, no other bonus |

The game already gives every fighter, gladiator and ranger the specialist's
attacks in melee (3/2 a round, 2 from 7th level). With the rule, a warrior
fighting with a weapon outside its chosen weapon specs gets AD&D's plain rate, half
an attack less; with a chosen weapon spec it keeps the game's rate (a grand
master one more).

Missile weapons have a rate of fire of their own in the game, the same for
everyone (a bow 2 a round, a sling, staff sling or chatkcha 1). With the rule,
fighters and gladiators shoot faster with a chosen weapon spec, and rangers
with theirs and every bow: AD&D's specialist's rate for the sling, a step above
it for the bow, staff sling and chatkcha. From 7th level every warrior shoots
its other missile weapons faster too, a step behind a specialist, as in melee
(AD&D keeps the weapon's own rate). Mastery's and grand mastery's bonuses to
hit and damage count for missiles too.

**Attacks a round,** by skill and level (a warrior's level: the highest of its
fighter, gladiator and ranger levels; characters stop at 10):

| Skill with the weapon | Who | Melee, levels 1–6 | Melee, levels 7–10 | Bow, levels 1–6 | Bow, levels 7–10 | Sling, staff sling or chatkcha, levels 1–6 | Sling, staff sling or chatkcha, levels 7–10 |
|---|---|---|---|---|---|---|---|
| none | non-warriors: clerics, druids, preservers, psionicists, thieves | 1 | 1 | 2 | 2 | 1 | 1 |
| not a chosen weapon spec | any warrior | 1 | 3/2 | 2 | 3 | 1 | 3/2 |
| expertise | a ranger: every bow, and its chosen weapon spec (a [Justifier](#kits)'s are specialized); a [Battle Mage](#kits): its chosen weapon spec (melee only) | 3/2 | 2 | 3 | 4 | 3/2 | 2 |
| specialized | a fighter's or gladiator's chosen weapon spec | 3/2 | 2 | 3 | 4 | 3/2 | 2 |
| mastery | a fighter's chosen weapon spec, from 5th level | 3/2 | 2 | 3 | 4 | 3/2 | 2 |
| grand mastery | a fighter's chosen weapon spec, from 9th level | | 3 | | 5 | | 3 |

The sixteen weapon specs take in the game's
weapons of every material and its named ones (Bloodwrath, Swiftbite and the
like are long swords); spell-made weapons and gloves are none.

| Weapon specs (four to a page) |
|---|
| long sword, club, dagger, short sword |
| mace, axe, great axe, pick |
| quarterstaff, polearm, gythka, cahulaks |
| chatkcha, bow, sling, staff sling |

**Choosing at creation.** On the character creation screen, the panel under
the classes (the psionic disciplines, or a cleric's or ranger's spheres) has
**WEAPON SPEC** for a warrior: four pages of weapon specs, **MORE SPECS** to the next,
and on the last **VIEW PSIONICS** back to the panel. It works as the game's
disciplines do: the long sword is marked to start with (a gladiator's two:
the long sword and the club), the others greyed; click a marked one to take
it back, then another. A multiclass warrior can choose only the weapon specs its other
class lets it use: those of which the game (or the Ledger) has a weapon the
character may use, in any material. The rest stay greyed:

| A warrior (fighter, gladiator or ranger)… | Weapon specs it can choose | Starts with |
|---|---|---|
| …of one class, or with thief, preserver or druid | all sixteen (a ranger all but the bow) | the game's bone long sword |
| …with psionicist (small weapons) | club, dagger, short sword, mace, chatkcha, bow, sling | a wooden club |
| …with air cleric (missile weapons, and the dagger that can be thrown) | dagger, chatkcha, bow, sling, staff sling | an obsidian dagger |
| …with earth cleric (stone, obsidian, metal, wood) | long sword, club, dagger, short sword, mace, axe, great axe, pick, quarterstaff, polearm, chatkcha, bow (the polearm in the Ledger's metal) | an obsidian long sword |
| …with fire cleric (obsidian) | long sword, dagger, short sword, mace, axe, great axe, chatkcha | an obsidian long sword |
| …with water cleric (bone, wood) | long sword, club, dagger, short sword, mace, axe, great axe, quarterstaff, polearm, gythka, cahulaks, bow | the game's bone long sword |

(The starting weapon is for the weapon spec marked first; the next table has the
rest. A ranger never has the bow to choose: its expertise with the bow comes
anyway.)

![The creation screen: a gladiator's weapons page, the long sword and the club marked, the others greyed, and under CHR the total of the six scores and of the die's roll](docs/creation-weapons.png)

A new character starts the game with a plain weapon of its first weapon spec in
place of the bone long sword the game gives warriors, in a material it may
use, and the log says so (`Grog starts with a plain obsidian long sword for the
weapon specialization chosen, in place of the bone long sword`):

| Weapon spec | Starting weapon | For a cleric's sphere that can't use it |
|---|---|---|
| long sword | the game's bone long sword | obsidian (fire, earth) |
| club, quarterstaff, bow | wooden (a bow with 20 arrows) | |
| dagger, chatkcha | obsidian | a dagger: bone, the Ledger's (water) |
| short sword | bone, the Ledger's | obsidian (fire, earth) |
| mace, polearm, gythka, cahulaks | bone | a mace: obsidian, the game's plain Mace type with a picture of the Ledger's; a polearm: metal, the Ledger's (earth) |
| axe | bone, the Ledger's | obsidian (fire, earth) |
| great axe | bone, the Ledger's | obsidian (fire, earth) |
| pick | stone | |
| sling, staff sling | leather | |

A two-handed weapon held in the hands puts the game's starting shield in the
backpack (not a half-giant's, with [its rule](#half-giants-two-handed-weapons)).
A bow or staff sling goes in the missile slot instead, and the shield stays, as
the game asks nothing of the hands for it. The weapon is
made once: a long sword handed to the character later stays one.

**At a level gained.** A warrior with fewer weapon specs than it is due (a gladiator
reaching 6th or 9th, or any warrior from a game begun before the rule) picks
the rest the way a psionicist picks a new power: in the game's own pop-up,
made bigger, a picture of each weapon spec on a slot, six to a row, those its
classes can't use (or it has) greyed. The pointer on a slot names it under
them (**SPECIALIZE IN** / **POLEARM**, or **EXPERT IN** where the pick would
be expertise: a ranger's, a Battle Mage's; as CHOOSE A SPELL names a spell), and
lights the slot if it can be picked; off the slots the title comes back. The
picks left are beside **EXIT** (which asks, as for powers, whether to leave
with picks unmade: they're offered again at the next level).

![The level-up window: a slot with a picture for each weapon spec, the pointer on the dagger's, lit, and SPECIALIZE IN / DAGGER under them; the club, great axe, pick, quarterstaff and the rest greyed for a fighter/fire cleric](docs/weapon-picker.png)

**Where it shows.** The **Effects** screen lists the selected character's
weapon specs under its effects ("SPECIALIZED IN", "MASTER OF", "GRAND MASTER OF",
"EXPERT IN"); View Character's DAM line and the inventory screen's weapon
lines count it (a staff sling specialist's `1.5x1D4+2`); the Characters tab lists
them (**Weapons: long sword (grand mastery)**) and gives the attacks a
round with each weapon ready, a missile weapon's its own (**Attacks: 3/2 a
round with Long Sword, 1 with Axe, 3 with Bow**); and the dice log names it on
each attack (`+1 specialized`, `+3 grand mastery`, `(d10 for d8: grand
mastery)`). A ranger's expertise with the bow isn't a chosen weapon spec, so neither
list shows it, but it counts; and View Character, as the game has it, gives a
character's melee rate whatever weapon is ready.

![The Effects screen: Daaki, a 9th-level fighter, GRAND MASTER OF LONG SWORD](docs/effects-weapons.png)

A human who dual-classes keeps what it earned as a fighter, gladiator or
ranger: its weapon specs, and the weapons it chose, whatever the new class (or
a kit) allows, count again once the new class's level passes the old. Till
then they sleep, as the class does.

How it works: [DEVELOPMENT.md](DEVELOPMENT.md#weapon-specialization).

### Kits

With **Kits** ticked, a character of one class may take one of three kits for
its class when it is made, or none (the class as it is). Each gives something
and costs something.

| Kit | Gives | Costs |
|---|---|---|
| **Myrmidon** (fighter) | a second weapon spec at 1st level, on to mastery and grand mastery as the first | −4 on saves against charms (Charm Person, Charm Monster, Charm Person or Mammal, Domination, Mass Domination) |
| **Sentinel** (fighter) | AC 2 better with a shield in a hand; +2 initiative | −1 on saves against wizards' and priests' spells |
| **Ravager** (fighter) | +1 to hit and damage in melee; a base AC by level (7 at 1st and 2nd level, 6 at 3rd and 4th, 5 at 5th and 6th, 4 at 7th and 8th, 3 at 9th and 10th), armour bettering it as usual | no missile or thrown weapons; no shield; light armour only (leather, or none) |
| **Arena Champion** (gladiator) | with a shield in a hand: +1 to hit and damage in melee, and AC 1 better | −1 to hit in melee with no shield |
| **Twin-blade** (gladiator) | no penalty for two weapons in light armour, leather or none (with the two-weapons rule) | no shield; no two-handed weapon (a half-giant may hold one in one hand, with the half-giants' rule) |
| **Brute** (gladiator) | +2 to hit and damage with a two-handed melee weapon | two-handed melee weapons only (a half-giant may add a shield); missile weapons, but not as a weapon spec |
| **Stalker** (ranger) | +2 movement in a fight; +15 hide in shadows and move silently, and hiding not halved indoors (with hiding to backstab) | light armour only (leather, or none) |
| **Assassin** (thief) | hiding in shadows not halved in daylight | −15 pick pockets and open locks |
| **Swashbuckler** (thief) | a warrior's THAC0 (21 less its level) | −10 to every thief skill |
| **Grove Warden** (druid) | AC 1 better for every 3 druid levels | no metal weapons |
| **Wanderer** (druid) | resists fire and cold as the Resist Fire and Resist Cold spells do: +3 on saves against fire and cold spells | AC 1 worse |
| **Arcanist** (preserver) | a spell slot more at each spell level it has slots at; in a fight, casts two preserver spells each turn instead of one (its first doesn't end the turn; being hit still stops the second) | a d3 hit die (a preserver's is a d4) |
| **Shinobi** (thief) | preserver spells from 6th level, on the Seeker's slots (one 1st-level slot at 6th, two at 7th, and a 2nd-level slot at 8th, two at 9th, and a 3rd-level slot at 10th), cast at the thief level less 5, in light armour too: its own 15 (Gaze Reflection, Charm Person, Shield, Color Spray, Wall of Fog, and [Fogbolt](#new-wizard-spells) with the new spells on; Invisibility, Mirror Image, Blur, Detect Invisibility, Fog Cloud; Blink, Haste, Protection from Normal Missiles, Hold Person), one learnt at each level up from 6th | none learnt from scrolls; dagger, short sword, quarterstaff, chatkcha, sling, staff sling and bow only; light armour only; no shield |
| **Lifebinder** (druid) | Cure Light, Serious and Critical Wounds heal a d8 more, Blood Flow a d6 | blunt weapons only (club, mace, quarterstaff, sling, staff sling) |
| **Healer** (cleric) | Cure Light, Serious and Critical Wounds heal 1 more a die (+1, +2, +3) | no weapon in the off hand (a shield is fine) |
| **Scholar** (preserver) | a spell more learnt at each level up (CHOOSE A SPELL comes up twice) | −1 to hit (THAC0 1 worse) |
| **Crusader** (cleric) | a warrior's THAC0; a warrior's extra attacks in melee (3/2 a round from 7th level) | one fewer spell slot at each spell level |
| **Elementalist** (cleric) | a second sphere: its spells (cast at its cleric level) and its weapons as well as its own sphere's | spell slots a level behind (a 7th-level Elementalist has a 6th-level cleric's; none at 1st level) |
| **Seeker** (ranger) | priest spell slots from 6th level: one 1st-level slot at 6th, two at 7th, and a 2nd-level slot at 8th, two at 9th, and a 3rd-level slot at 10th (and on), in place of a ranger's, cast at the ranger level less 5 (a ranger's: less 7) | its sphere's weapon limits, as a cleric of that sphere's (air: missile and thrown weapons, daggers; earth: stone, obsidian, metal, wood; fire: obsidian; water: bone, wood), but it keeps the bow |
| **Justifier** (ranger) | with weapon specialization, its expertise with the bow and its chosen weapon spec becomes specialization: +1 to hit, +2 damage (SPECIALIZED IN on the Effects screen); with the two-weapons rule, no penalty for two weapons in any armour (another ranger's is in light armour only) | one 1st-level priest spell slot from 10th level, in place of a ranger's slots, cast at the ranger level less 9 |
| **Battle Mage** (preserver) | a warrior's THAC0; a spell still cast after being hit earlier in the round; a d6 hit die; light armour (leather, or none) worn, and spells cast in it; with weapon specialization, expertise in one weapon spec of its choice (long sword, club, dagger, short sword, mace, axe or pick), whose weapons it may use as well as a preserver's own, at 3/2 attacks a round (2 from 7th level) | one fewer spell slot at each spell level; nothing in the off hand |
| **Mind Warrior** (psionicist) | a warrior's THAC0; a warrior's extra attacks in melee (3/2 a round from 7th level); a d8 hit die | a tenth fewer PSP (rounded down) |
| **Mind Bender** (psionicist) | telepathy powers (the defence modes too) cost 2 PSP less to use | psychokinesis powers cost 2 PSP more |
| **Kineticist** (psionicist) | psychokinesis powers cost 2 PSP less to use | telepathy powers (the defence modes too) cost 2 PSP more |

#### Choosing a kit

The kit is chosen on the creation panel's **KIT** page, opened with **KITS**,
the button at the end of the panel's pages: under the psionic disciplines for
a fighter, gladiator (without weapon specialization), preserver, psionicist
or thief; under the clerical spheres for a cleric, druid or ranger; on the
last weapon page for a fighter, gladiator or ranger choosing weapon specs.
NO KIT, the first row, is what a new character has. As with the clerical
spheres, the rows not chosen are greyed: click the marked row to take it back,
then click the kit you want. A few names are shortened to fit the panel
(CHAMPION, SWASHBUCK, ELEMENTAL, WARDEN, BATTLMAGE, M-BENDER, M-WARRIOR). Choosing
another class puts the kit back to none; a new roll of the die keeps it. The Effects screen names the kit
(`KIT: RAVAGER`), as does the Ledger's Characters tab.

The Elementalist chooses its second sphere on the creation panel's
**CLERICAL SPHERE** list: once the kit is taken (KITS, then ELEMENTAL), its
own sphere marked, the other spheres stay in use, and a click on one marks it
as the second; a click on it again takes it back, and taking back its own
sphere takes back both. The Ledger's Characters tab names it (**Kit:
Elementalist (and water)**). Its second sphere's spells are known from the
start, as its own sphere's are (a priest knows every spell of its spheres from
the start: the game marks them when the character is made, and again when a
human changes class, not at a level up).

The Battle Mage chooses its weapon spec on the weapon pages: once the kit is
taken, **VIEW PSIONICS** on the KIT page goes back to the panel, which then
has **WEAPON SPEC** in place of KITS. The long sword is marked to start with;
the pages grey the weapon specs it can't choose. With its chosen weapon spec it
attacks at expertise's rate by its preserver level; with any other weapon, as
a preserver does. Its light armour holds whatever the class restrictions say
of a preserver. Without weapon specialization it has no weapon spec, only a
preserver's weapons.

The Myrmidon takes its second weapon spec on the weapon pages after the kit
is taken (go back to them from the KIT page), and loses it if another kit is
taken.

The game rolls a new character's hit points and works out its PSP when a
class is clicked, before a kit can be chosen, so choosing or taking back a
kit with a die of its own (Battle Mage, Mind Warrior, Arcanist) rolls the hit
points and works out the PSP again, and the screen shows the new numbers.

#### Starting gear

The game hands a new character its gear when DONE is clicked, by its class:

| Class | Starting gear |
|---|---|
| Fighter | bone long sword, shield, leather chest, arm and leg armour |
| Gladiator | bone long sword, club in the off hand, leather arm armour |
| Ranger | bone long sword, bow and arrows, leather chest and arm armour |
| Cleric | shield, leather chest and arm armour, a club in the backpack |
| Druid | club, sling |
| Preserver | quarterstaff, sling |
| Psionicist | club, bow and arrows, leather chest armour |
| Thief | bone long sword, sling, leather chest armour |

With **Kits** ticked, the Ledger fits that gear to the kit while the character
is new, and the dice log says what it changed: a weapon in the hand the kit
forbids becomes a plain one it allows (a **Shinobi**'s long sword a bone
short sword; a **Brute**'s a bone great axe, its club left behind (no use to it);
a **Seeker**'s long sword one of a material its sphere allows); a shield the
kit forbids is taken away (a **Ravager**'s), the Ravager getting a second of
its weapon for that hand (unless the weapon takes both hands), and an
off-hand weapon it forbids goes to the backpack; with weapon specialization a
**Myrmidon** gets a plain weapon of its second weapon spec too, in the
backpack (a bow in the missile slot, with arrows);
an **Arena Champion**'s off-hand club becomes a shield, the gladiator's kit
being the one that fights with it; and with weapon specialization a
**Battle Mage**'s quarterstaff becomes a plain weapon of its chosen weapon spec
(`T'Jun starts with a plain bone axe for the Battle Mage's weapon spec, in
place of the Quarterstaff`). The other kits keep the class's gear: it fits
them (the Twin-blade's long sword and club are its two weapons, the Healer's
club is in the backpack, a Lifebinder's club and sling are blunt).

#### The kits in play

- **Shown everywhere.** The dice log and the Ledger show each kit's part: a
  Ravager's to-hit and damage (`+1 Ravager`), a Sentinel's initiative and
  saves, a Stalker's hiding, the THAC0 for each weapon. A kit's hit die is
  named on the hit point lines (`Preserver d6 per level`).
- **Hit dice.** The Battle Mage's, Mind Warrior's and Arcanist's are rolled
  on the creation screen and at every level up.
- **A warrior's THAC0** is the game's own for a fighter, where it is better
  than the class's. It and the Scholar's −1 are in the THAC0 the game keeps
  for the character (View Character's, the attack's), worked out when the
  character is made and at each level up.
- **Spell slots** are the game's own wherever it counts them (resting, the
  spell lists, the Ledger's Spells tab). WIS's bonus slots count for the
  Arcanist, Crusader and Elementalist as for their classes, not for the
  Seeker's and Justifier's own tables.
- **Casting level.** A kit's casting level is the one a spell's duration and
  damage take, and half of it (rounded up) is the highest spell level it may
  cast; the Seeker and Justifier take 5 and 9 off the ranger level (see
  [Rangers' casting level](#rangers-casting-level) for a plain ranger's).
- **Casting when hit.** A character hit in a fight can't cast until the next
  round: the game won't let it choose a spell, and drops one chosen before
  the hit. The Battle Mage isn't stopped.
- **PSP.** The Mind Bender's and Kineticist's 2 PSP more or less counts both
  to use a power and to keep it up each round, never below 1 (a power with no
  upkeep still has none); psychometabolism is as it was.
- **The Lifebinder's die** is rolled from the game's own random numbers; the
  dice log notes it, and the HP line shows what was healed.
- **The Brute's +2** is for melee: a bow or staff sling, two-handed as it is,
  doesn't get it.
- **The Wanderer's resistance** is the game's Resist Fire and Resist Cold,
  which give +3 on the save but don't halve the damage.

#### Changing class

A kit belongs to the class it was chosen with. A human who changes class
(**DUAL** on the menu a right-click on a portrait opens, for a human of 2nd
level or more) keeps it, but it sleeps as that class does: gifts and costs
alike count again once the new class's level passes the old one's. The
Effects screen shows `KIT: BATTLMAGE (ASLEEP)` until then;
the Ledger's Characters tab says so too (`Battle Mage, dormant until the
fighter level passes 3`). Once awake, the kit goes by its own class's level
(a Ravager's AC, a Seeker's slots, a Battle Mage's expertise from 7th
preserver level), its hit die only ever counts for its own class (the new
class rolls its own), and a Mind Warrior's PSP stays a tenth fewer, asleep or
not (they are its psionicist levels'). A Battle Mage's chosen weapon spec is
the kit's alone: a Battle Mage turned fighter isn't specialized in it, and has
expertise with it once the kit wakes. A warrior's own weapon specs stay, as
the game keeps them, and count again once the new class's level passes the
old.

A weapon spec is a weapon learnt for good, while the class or kit that gave it
is awake: no kit keeps a character from a weapon type it specialized in
(but for the off hand's rules: the Healer's, the Battle Mage's), and a human
who has changed class may use the weapon types it chose whatever the new class
allows. While that class or kit sleeps, the types go with it, and come back
when it wakes.

A human who changes class may take a kit for the new class too, so a human
can have up to three, one for each class it has had. Right after DUAL (and
the sphere a new cleric picks), the game's own three-choice menu asks for it:
**KIT: NONE** at the top, then the new class's kits; click one, or the top
row for none. A kit that can't go with the character's other classes or kits
(below) is left off the menu. A new **Elementalist** then picks its second
sphere on the same menu (**SPHERE 2: NONE**, then the three other spheres).
Each kit sleeps and wakes with its own class.

![The KIT menu after DUAL: a Battle Mage turned thief, offered Swashbuckler and Assassin (not the Shinobi)](docs/dual-kit-menu.png)

The Effects screen lists the kits, oldest first, a line each (the longer names
shortened as on the KIT page, `(ASLEEP)` after one that sleeps), then the
weapon specs. Its lower panel has room for five lines: when there are more,
it shows four and **MORE: CLICK HERE** under them, and a click on the panel
shows the next page (a weapon spec's heading again at the top of a page that
goes on with its weapons), the first again after the last:

![The Effects screen, a page at a time: a Mind Bender psionicist who became a Twin-blade gladiator, then an Assassin thief, with four weapon specs](docs/effects-pages.png)

With **Weapon specialization** ticked, a human who becomes a fighter,
gladiator or ranger (or a Battle Mage) then picks the weapon types it is due
on the same window as at a level up (**PICK A WEAPON SPECIALTY**), less any it
has already.

A human who becomes a preserver picks its first two spells on the game's
**CHOOSE A SPELL** window, twice over, from the 1st-level ones (the game gave
it Grease and Magic Missile), as a preserver picks one at each level up. If
it takes the **Scholar** kit for its new preserver class, it picks a third,
as a Scholar picks one more at each level up.

A new preserver picks its starting spells the same way when **DONE** is
clicked on the creation screen, in place of the ones the game handed out by
its starting level: two 1st-level spells at 1st level (the game's Grease and
Magic Missile), four at 2nd (and Shield and Wall of Fog), four and two of 2nd
level at 3rd (and Fog Cloud and Mirror Image). A Scholar picks one more for
each level. A multiclass preserver too. (The game's own party, used when no
party is made, keeps the game's spells.)

**EXIT** on CHOOSE A SPELL (then EXIT again at "YOU HAVEN'T CHOSEN") ends the
picking, at creation and on changing class: the spells still to pick are the
game's own, in its order (Grease, Magic Missile, Shield, Wall of Fog; then Fog
Cloud, Mirror Image), less any already picked. The character is already saved
when the window opens, so EXIT can't take you back to the creation screen.

#### Kits that rule out classes and each other

Some kits keep a human from some classes, both ways: greyed on the DUAL
window for a human who has the kit (as the game greys the classes it already
bars), and left off the KIT menu for a human who has had the class:

| Kit | Can't become | Why |
|---|---|---|
| Seeker, Justifier | cleric, druid | their own priest slot tables would take the new class's slots' place |
| Shinobi | preserver | its own wizard slot table would take the new class's slots' place |
| Swashbuckler, Crusader, Battle Mage, Mind Warrior | fighter, gladiator, ranger | a warrior's THAC0 is already their kit's |
| Arena Champion, Sentinel | druid, preserver | their gift needs a shield, which those classes can't hold |
| Brute | psionicist, air cleric | it needs a two-handed melee weapon, which those classes can't use |

And some kits can't go together, whichever came first (a human has one kit for each of its classes, and the game never lets a human change from one warrior class to another, so only these can meet):

| Kit | Can't go with | Why |
|---|---|---|
| Arena Champion, Sentinel | Shinobi | one needs a shield, the other forbids it |
| Twin-blade | Healer | two weapons, and an off hand free of them |
| Brute | Shinobi, Lifebinder | a two-handed weapon, and weapons that can't be one |

### Levels up to 10

The game stops every class at level 9 (its manual's tables end there too).
With **Class levels go up to 10** ticked, each class goes one level further,
at the XP AD&D gives for 10th level:

| Class | XP for 10th level |
|---|---|
| Cleric | 450,000 |
| Druid | 125,000 |
| Fighter, gladiator | 500,000 |
| Preserver | 250,000 |
| Psionicist | 400,000 |
| Ranger | 600,000 |
| Thief | 160,000 |

Everything else at 10th level is the game's own: it had it all along, and
only the cap kept it out of reach. Its XP tables go on to level 20 (druids
with a table of their own, not the cleric's), and THAC0, saves, spell slots
and thief skills are worked out from the level. So at 10th level:

- **Hit points** follow AD&D past 9th: preservers and thieves still roll
  (d4 and d6, CON's bonus counting too), while the others gain a fixed amount
  (+3 for fighters, gladiators and rangers, +2 for clerics, druids and
  psionicists). The game's own table has the fixed gain for thieves too, as
  it keeps thieves and psionicists together and AD&D's psionicist stops
  rolling at 9th; with the rule thieves roll their 10th die.
- **Gladiators** optimise their armour, as the game already has them do:
  AC 1 better for every 5 gladiator levels, so -2 at 10th where it was -1.
  (The Ledger counts it in **AC: spells, rings, other**. The game gives it
  with or without armour.)
- **THAC0 and saves** improve as the game's formulas give: 11 for a
  gladiator, 14 for a druid, as for AD&D's warriors and priests.
- **Spell slots** grow at the levels casters already have, up to 5th; no
  class gets 6th-level slots (a cleric would at 11, a preserver at 12), so no
  spells past 5th level are needed. A 10th-level preserver or druid has
  5 4 3 2 2 before WIS by the game's table; with [AD&D's class
  tables](#adds-class-tables), 4 4 3 2 2 and 4 4 3 3 2.
- **A preserver picks a new spell** on the game's own CHOOSE A SPELL screen,
  as at every level, offered from spell level (class level + 1) / 2 down:
  5th at 10th as at 9th. **A psionicist picks a new power** (the game gives
  one at each level, two at odd levels and 4th).
- Spell damage that grows with the caster's level already counts up to
  level 10 in the game, so a 10th-level caster gets the last step.

The level-up comes as the game's usual one ("Gerakis gains a level"), and
View Character stops showing the XP for the next level at 10, as it does at
9 without the rule. For a character of more than one class, a class already
at 10 isn't named in the brackets, since it has no next level. Untick it and
nobody goes past the level they have: a 10th-level character stays 10th.

How it works: [DEVELOPMENT.md](DEVELOPMENT.md#levels-up-to-10).

### STORE and RECALL on the creation screen

The creation screen has two more buttons under the hit points, as Baldur's
Gate has them: **STORE** keeps the roll on screen, and **RECALL** brings it
back, however many times the die has been rolled since. A roll is the six
scores and what the die's total allows (the `SUM:` line), the hit points and
the PSP. So a good roll can be stored and the die tried again; if nothing
better comes, RECALL puts the stored one back, AC and damage with it.

![The creation screen with STORE and RECALL under the hit points and PSP, a stored roll recalled: SUM:99/99, 28/28 hit points](docs/creation-store-recall.png)

Changing the race, sex, classes or kit forgets the stored roll (its hit
points were rolled for those), even if they are changed back: RECALL then
does nothing until STORE keeps another. STORE again keeps the new roll in
place of the old. With **STORE and RECALL on the creation screen** unticked
in the Options tab's More character customization section (it's ticked by
default), the screen is as the game has it, from the next time the game is
started.

How it works: [DEVELOPMENT.md](DEVELOPMENT.md#store-and-recall).

### The game's own party

START GAME with no party made plays the game's own four, who were made before
any of these choices existed. With weapon specialization, kits and class
restrictions on, the Ledger fits them to those in the first moments of a new
game, and says so in the dice log (Cilla also gets the elf's figure, with its
own switch: see [Elves and half-elves](#elves-and-half-elves)):

| Character | With weapon specialization | With class restrictions |
|---|---|---|
| **Gerakis**, half-giant gladiator | specializes in the long sword and the gythka; with [half-giants' two-handed weapons](#half-giants-two-handed-weapons), his club is a bone gythka, a two-handed weapon beside his long sword | |
| **K'ratchek**, thri-kreen fighter, druid and psionicist | specializes in the chatkcha, her only weapon | |
| **Cermak**, human preserver, once a gladiator | specializes in the long sword and the axe, which count once his gladiator levels do again (when his preserver level passes them) | |
| **Cilla**, elf preserver, druid and thief | | no leather armour (a druid wears none), and she knows the **Armor** spell in its place |

With [kits](#kits), Cermak is an **Arcanist**, the kit of his preserver
class: a spell slot more at each spell level and two preserver spells a turn
in a fight. His gear stays as it is (an Arcanist has none of its own), and so
do the hit points the game gave him: the Arcanist's d3 counts from his next
level. Gerakis has no kit; K'ratchek and Cilla, with more than one class at
once, can't have one.

Cermak and Cilla keep the game's own starting spells: only a character made
on the creation screen [picks its own](#changing-class).

![The USE screen in the game: Cilla's 1st-level mage spells, the first named ARMOR in the bar below, WIZ 2/2](docs/default-party-armor.png)

![Gerakis's inventory in the game: a Gythka in his left hand and a Long Sword in his right, 1.5 attacks a round with the sword and one with the gythka in the off hand](docs/default-party-gerakis.png)

How it works: [DEVELOPMENT.md](DEVELOPMENT.md#the-games-own-party).

## Expanded features

New things to do in play, each with a box in the Options tab's **Expanded
features** section. All are on by default and, like the rule changes, take effect at
once in games started with the dice log; untick one and the game is as it
was.

| Box on the Options tab | What it adds |
|---|---|
| [The leader's CHA at shops](#the-leaders-cha-at-shops) | the party leader's CHA 16 or more lowers what shops ask, 5% to 25%, as in Baldur's Gate |
| [Thief skills from AD&D's table](#thief-skills-from-adds-table) | AD&D's table by level, with Dark Sun's race and DEX adjustments |
| [Hiding in shadows to backstab](#hiding-in-shadows-to-backstab) | thieves hide and move silently to backstab, rangers to attack from behind; a worn cloak, boots and belt help |
| [Picking pockets](#picking-pockets) | a thief uses Thieves' Tools on anyone in sight, until caught |

### The leader's CHA at shops

The game's shops ask an item's price whoever buys. With **The leader's CHA at
shops** ticked, the party leader's CHA lowers it, as Baldur's Gate's table
has it:

| Leader's CHA | 15 or less | 16 | 17 | 18 | 19 | 20 or more |
|---|---|---|---|---|---|---|
| Discount | none | 5% | 10% | 15% | 20% | 25% |

The price shown under each item, the one charged, and whether the shop's list
greys an item as too dear all follow it (never below 1). Selling is as the
game has it.

How it works: [DEVELOPMENT.md](DEVELOPMENT.md#the-leaders-cha-at-shops).

### Improved thieving

More for thieves to do: skills that grow by the Player's Handbook's table,
hiding in shadows and moving silently to backstab (rangers too, to attack from
behind), a cloak, boots and belt that help, and pockets to pick. The switches
are together under **Improved thieving** in the Options tab's Expanded
features section.

#### Thief skills from AD&D's table

The game's thief skills come out high: a 3rd-level elf thief with DEX 22 has
move silently 66 and hide in shadows 61. AD&D gives 27 and 20 at 3rd level
before race and DEX. The game adds 4 a level to a base of its own, and its DEX
formula gives move silently and hide in shadows less than Dark Sun's table at
high DEX, and some other skills more. With **Thief skills from AD&D's table**
ticked, a skill is:

- AD&D's average for the thief level (the Player's Handbook's table, up to
  10th level),
- plus the race's adjustment, the game's own (already the Dark Sun rules'
  numbers),
- plus DEX's: AD&D's table up to 19, the Dark Sun rules' exceptional DEX
  past it, for the first five skills (hear noise, climb walls and read
  languages have none).

AD&D's averages, by thief level:

| Thief level | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| Pick pockets | 30 | 35 | 40 | 45 | 50 | 55 | 60 | 65 | 70 | 80 |
| Open locks | 25 | 29 | 33 | 37 | 42 | 47 | 52 | 57 | 62 | 67 |
| Find/remove traps | 20 | 25 | 30 | 35 | 40 | 45 | 50 | 55 | 60 | 65 |
| Move silently | 15 | 21 | 27 | 33 | 40 | 47 | 55 | 62 | 70 | 78 |
| Hide in shadows | 10 | 15 | 20 | 25 | 31 | 37 | 43 | 49 | 56 | 63 |
| Hear noise | 10 | 10 | 15 | 15 | 20 | 20 | 25 | 25 | 30 | 30 |
| Climb walls | 85 | 86 | 87 | 88 | 90 | 92 | 94 | 96 | 98 | 99 |
| Read languages | 0 | 0 | 0 | 20 | 25 | 30 | 35 | 40 | 45 | 50 |

The race adjustments, as the game has them (humans, half-giants and
thri-kreen have none):

| Race | Pick pockets | Open locks | Find/remove traps | Move silently | Hide in shadows | Hear noise | Climb walls | Read languages |
|---|---|---|---|---|---|---|---|---|
| Dwarf | 0 | +10 | +15 | 0 | 0 | 0 | −10 | −5 |
| Elf | +5 | −5 | 0 | +5 | +10 | +5 | 0 | 0 |
| Half-elf | +10 | 0 | 0 | 0 | +5 | 0 | 0 | 0 |
| Halfling | +5 | +5 | +5 | +10 | +15 | +5 | −15 | −5 |
| Mul | 0 | −5 | 0 | +5 | 0 | 0 | +5 | −5 |

The DEX adjustments:

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

then the situation and effects as before. So Azil, a 3rd-level elf thief with
DEX 22: pick pockets 40 + 5 + 27 = 72, open locks 58, find traps 47, move
silently 62, hide in shadows 52, hear noise 20, climb walls 87. A ranger's
move silently and hide in shadows take the same race and DEX adjustments.
Untick it for the game's numbers.

How it works: [DEVELOPMENT.md](DEVELOPMENT.md#thief-skills-from-adds-table).

#### Hiding in shadows to backstab

The game never rolls hide in shadows, and a thief only backstabs a target that
has turned to face someone else. With **Thieves hide in shadows and move
silently to backstab, rangers to attack from behind** ticked, a thief whose
turn comes in a fight with no enemy in any of the eight squares around them
tries to hide in shadows; if they do, they try to move silently up to someone;
and if both succeed, their next attack that turn counts as one from behind: +2
to hit, the target's DEX and shield don't count, and with a weapon that can
backstab it is a backstab, the damage multiplied as usual. The attack gives
the thief away, and so does the turn ending without one. An enemy next to the
thief when the turn comes means no hiding at all: get clear first. A worn
cloak adds 10 to hiding in shadows (before daylight halves it) and worn boots
add 10 to moving silently, for rangers too, up to 95: `needs 18 or less (26
+10 cloak = 36, halved in daylight)`. With that switched on, a cloak's or
boots' item box (right-click it on the inventory screen) says so under its
name, `Hide +10` or `Move +10` (the skills' short names, as the inventory
screen's thief rows have them).

![Item boxes in the game: a Leather Belt's "Pick +5, Lock +5", Leather Boots' "Move +10" and a Leather Cloak's "Hide +10", each at 24](docs/gear-boxes.png)

The [Cloak and Boots of Elvenkind](#new-items) do more (whatever the plain
gear's switch). Only thieves and rangers can wear them (multiclasses too; for
anyone else, the game's "Cannot use this item"). In the cloak, hiding in
shadows needs 95 or less under the open sky and 90 under a roof, not halved by
the light (AD&D's: all but invisible in the wild, 90% among buildings), unless
their own chance is better; in the boots, moving silently needs 95 or less.
Their boxes say `Hide 90-95%` and `Move 95%`.

![Item boxes in the game: the Cloak of Elvenkind's "Hide 90-95%", 25,000; the Boots of Elvenkind's "Move 95%", 20,000](docs/elvenkind.png)

The same switch has a worn **belt** add 5 to a thief's **picking pockets and
opening locks**, whether hiding is on or not: the game's own lock picking
counts it, and so do the Ledger's pockets and its thief rows (`PICK 80`,
`LOCK 64`). A belt's box says `Pick +5, Lock +5`.

Plain cloaks, boots and belts cost 24 (the game's Leather Cloak is 20), anywhere
in the region, shops included; magic ones (with a plus, or dearer than 100)
keep their prices.

```
Cilla's turn
Cilla hides in shadows: d100 = 21, needs 27 or less (54, halved in daylight) -> hidden
  Cilla moves silently: d100 = 30, needs 54 or less -> unheard: their next attack this turn is from behind (a backstab with a weapon that can)
Cilla attacks Slig BACKSTAB with Bone Long Sword (1d8): d20 = 11, needs 10+ (55%), hits AC 2, target AC 3 -> HIT
    THAC0 19, +2 from behind, +2 backstab, +3 STR, -1 bone = 13
  Cilla hits Slig for 16: (1d8 = [1] -1 weapon (raised to the minimum of 1) +7 STR 19) x2 backstab
```

The chance to hide is **halved in daylight**. Which maps are under the open
sky goes by the game's regions: open desert and rock, the villages' open
ground and the arena are; the slave pens, the sewers, the lava caverns and
the other underground or roofed places aren't. Three maps have both, buildings
with floors of their own standing on open ground: there it goes by the floor
under the thief (from the game's map of the region in memory), so a thief in
a building is out of the sun and one in a roofless ruin isn't. The chances
are the thief's own as they stand (level, race, DEX, and effects: Invisibility makes hiding certain, Fire Shield and Mirror Image
rule it out).

**Rangers** hide and move silently too, with the same box ticked. The game
gives rangers no thief skills, so the Ledger uses AD&D's ranger table, by
ranger level, with the race's and DEX's adjustments as for a thief:

| Ranger level | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| Hide in shadows | 10 | 15 | 20 | 25 | 31 | 37 | 43 | 49 | 56 | 63 |
| Move silently | 15 | 21 | 27 | 33 | 40 | 47 | 55 | 62 | 70 | 78 |

The light works the other way round for these outdoorsmen: the **full chance
under the open sky, half indoors** (the same maps and floors as for thieves).
Their attack from behind gets +2 to hit, and the target's DEX and shield don't
count, but it is never a backstab. Armour doesn't matter, nor does what
they hold. The Characters tab shows a ranger's two chances (**Ranger skills
now**), and the game's inventory screen shows them where a thief's `MOVE`
and `HIDE` go. Someone with thief levels hides as a thief.

```
Gerakis hides in shadows: d100 = 15, needs 63 or less (63, a ranger under the open sky) -> hidden
  Gerakis moves silently: d100 = 42, needs 78 or less -> unheard: their next attack this turn is from behind
Gerakis attacks Slig from behind with Wooden Club (1d6): d20 = 12, needs 10+ (55%), hits AC 1, target AC 3 -> HIT
```

How it works: [DEVELOPMENT.md](DEVELOPMENT.md#hiding-in-shadows-to-backstab).

#### Picking pockets

The game has one pocket to pick, in the Trustee's conversation (his key). With
**Picking pockets** ticked on the Options tab (it is by default), a thief can
try anyone's with **Thieves' Tools**. Every thief starts a new game with a set
(a satchel) in the first free backpack cell, and a thief who joins later gets
one too (the log says so). A thief who loses or sells theirs can buy another
from Kel, who sells two sets.

On the inventory screen, pick the tools up, go back to the game with them on
the pointer, and click someone in sight. The tools stay on the pointer for the
next try (clicking open ground drops them, as with anything carried). Not in a
fight: there's no time for it then.

The Ledger rolls the thief's pick pockets chance as it stands now (effects and
a worn belt's 5 counted, as in the thief rows):

- **Success:** one small thing goes into the thief's backpack (its first free
  cell): something weighing 10 or less (a bag or arrows are 10, a helm 15, a
  long sword 30) that isn't worn on the body (armour, a belt, boots, a helm, a
  cloak). A dagger, a ring, an amulet, a gem or food can be lifted, and so can
  three weapons whatever their weight: Kurzak's Shadowseeker, Churrr's
  Gutterknot and Maris's Mindshard (see [New items](#new-items)). Lifting one is
  worth 200 XP to the thief, given as the game gives a quest's ("Cilla
  receives 200 experience points!", with the quest's sound; split among a
  multi-class thief's classes). Keys stay, as scripts may look for them. People outside the party keep all they own in
  their pack, so this goes by what each thing is.
- **Failure:** a move silently roll. Made, the thief slips away unnoticed;
  missed, they're caught.

With nothing like that left on them, the thief takes what's in their purse
instead: a few ceramic pieces (2 to 5), added to the party's money. That is
the last try on that person.

A thief can go on trying the same person until **caught** (both rolls failed)
or until they take the coins; after that, that person keeps a hand on their
pockets for good. The Ledger remembers who in `settings.json`,
for this party, with the time on the game's clock: load a game saved before
the try and the clock goes back past it, so the try is forgotten and the
person can be tried again. The Trustee is left to his own conversation. What happens
comes up in the game's message window and in the dice log:

```
Daaki picks Kurzak's pocket: d100 = 71, needs 63 or less -> failed
  Daaki moves silently to get away: d100 = 12, needs 55 or less -> success
  Daaki fumbles Kurzak's pockets, but slips away unnoticed.
```

**The Trustee's own key.** Picked in his talk by a thief with no room for it,
the game drops it at his feet, and after each step of his rounds he went back
for it ("There it is!") without picking it up: his rounds stalled, and he
stayed busy ("I'd love to talk more... get back to work") for good. The
Ledger's copy of his scripts leaves the key where it lies, for the party to
pick up, and has him say the busy line once.

How it works: [DEVELOPMENT.md](DEVELOPMENT.md#picking-pockets).

## New content

Spells, people, a quest and items the Ledger adds to the game, each with a box
in the Options tab's **New content** section: the people, the quest and the
items from the next time the game is started, the spells at once in games
started with the dice log.

### New wizard spells

Three wizard spells from AD&D's *Spells & Magic* and the Dark Sun books,
added to the game's own 68 (numbers 196-198, room the game's spell table has
past its own). Preservers learn them as they learn any spell: picked at a level
up or as starting spells, or from a scroll. They're listed on the USE screen by
level with their own icons and descriptions (right-click one), use the usual
slots, and show on the Effects screen while they last. Who knows them is kept
in the character's sheet, so it saves with the game and the character.

| Spell | Level | Cast on | Lasts | Does |
|---|---|---|---|---|
| **Cat's Grace** | 2 | a party member (its portrait on the USE screen) | 60 rounds a caster level | DEX + 1d6 (at most 24), as Strength does for STR |
| **Erdlu Claw** | 1 | a party member (its portrait on the USE screen) | 5 rounds a caster level | each natural (unarmed) attack does 1d6+1 where that's better than its own, is +1 to hit, and counts as a +1 magical weapon |
| **Fogbolt** | 1 | one creature in sight | 2d4 rounds (a save negates) | -3 to its attacks, and +2 to attacks on it (its AC 2 worse) |

- **Cat's Grace** is made to work exactly as the game's Strength does, for DEX.
  Everything that reads DEX follows it while it lasts: AC, initiative, REAC and
  DEF, thief skills, the two-weapon penalties and the saves against fire, cold
  and electricity. The log says what it rolled: `Cat's Grace: 1d6 = 4 ->
  Gerakis's DEX +4 while it lasts (at most 24)`.
- **Erdlu Claw** grows talons like an erdlu's. A character with a weapon in
  hand is unchanged; one fighting unarmed hits for 1d6+1 instead. A
  thri-kreen's four claws and bite become 1d6+1 each (a natural attack already
  better on average, as 2d4 or 1d8+2, stays as it is). The +1 to hit shows in
  the log's THAC0 breakdown (`+1 Erdlu Claw`), and as a +1 weapon the talons
  hurt creatures that only magical weapons can. With **Body Weaponry** or
  **Animal Affinity** up, the power's dice for the first attack get the claw's
  +1: 2d4+1 or 1d10+1.
- **Fogbolt** wraps one creature in clinging fog. It flies to its target as
  a dark grey bolt, Magic Missile's in smoky greys (Magic Missile keeps its
  own blue); like any bolt it needs a clear line to the target. Its THAC0
  breakdowns show `-3 Fogbolt` on its own attacks and `+2 target's Fogbolt` on
  attacks against it.

Each has sounds of its own: Cat's Grace lands with Haste's shimmer, Erdlu Claw
with Shocking Grasp's snap, and Fogbolt is cast and lands with Fog Cloud's.

With the **New wizard spells** box unticked (it's ticked by default) the
spells are gone from the lists and the game is as it was.

![The three descriptions on the USE screen (right-click a spell): Cat's Grace's paw, Erdlu Claw's scratches, Fogbolt's cloud](docs/new-spells.png)

![The Effects screen with Cat's Grace and Erdlu Claw on Daaki, the claw's name below](docs/new-spells-effects.png)

![Fogbolt's dark grey bolt striking a Daggoran, cast by Daaki (right)](docs/fogbolt.png)

How it works: [DEVELOPMENT.md](DEVELOPMENT.md#new-wizard-spells).

### New items

Items the game never had, or never placed. All but the arena's ring (which the
Ledger hands over itself, while it runs) are written
into the game's own data each time the Ledger starts the game, so the game
makes them with their people and chests and then keeps and saves them like its
own. A changed switch takes effect in regions the party hasn't visited yet;
start a new game to have them all. The log doesn't say where they are: they're
there to be found. [Every magic item](#every-magic-item) lists the magic ones
with the game's own.

**Mundane items.** The game has no short sword at all, no bone or obsidian
axe or great axe, no bone dagger and few plain metal weapons; the
Ledger adds them:

| Icon | Item | Where | What it is |
|---|---|---|---|
| ![](docs/items/bone-short-sword.png) | **Bone Short Sword** | sold by the **Weapon Merchant** in Teaquetzl and **Jark** in Kel's caravan; carried by every **Renegade** | 1d6 |
| ![](docs/items/obsidian-short-sword.png) | **Obsidian Short Sword** | sold by the Weapon Merchant and Jark; carried by **Chaero** | 1d6 |
| ![](docs/items/bone-axe.png) | **Bone Axe** | sold by the Weapon Merchant and Jark; carried by every **Wild Mul** | 1d8; weighs 30, so not HEAVY: it goes in either hand with another weapon, and [backstabs](#attacks-from-behind-and-backstabs) |
| ![](docs/items/obsidian-axe.png) | **Obsidian Axe** | sold by the Weapon Merchant; carried by **Merzol**, the slave pens' gladiator | 1d8; 30, as the bone axe |
| ![](docs/items/obsidian-mace.png) | **Obsidian Mace** | sold by the Weapon Merchant and Jark; carried by every **Tari** in the warrens | the game's Mace (1d6+1), in obsidian (its only obsidian mace is Blackmace) |
| ![](docs/items/short-sword.png) | **Metal Short Sword** | sold by the Weapon Merchant | 1d6: Shadowseeker without the plus |
| ![](docs/items/metal-dagger.png) | **Metal Dagger** | carried by **Tobrian**, in Kel's caravan | the game's dagger, in metal |
| ![](docs/items/metal-mace.png) | **Metal Mace** | carried by the **Templar** of the elven slavers' camp | the game's mace, in metal |
| ![](docs/items/bone-great-axe.png) | **Bone Great Axe** | a warrior's starting great axe; sold by the Weapon Merchant and Jark; carried by every **Wild Mul** | 1d10, two-handed; lighter than metal (and breaks as bone does) |
| ![](docs/items/obsidian-great-axe.png) | **Obsidian Great Axe** | a fire or earth cleric's starting great axe; sold by the Weapon Merchant and Jark | 1d10, two-handed |
| ![](docs/items/bone-dagger.png) | **Bone Dagger** | a water cleric's starting dagger; sold by the Weapon Merchant and Jark; carried by one of the game's two kinds of **Defiler** (the other carries the game's obsidian Dagger, so a dead defiler leaves a body to search) | 1d4: the only dagger a water cleric can use |
| ![](docs/items/metal-great-axe.png) | **Metal Great Axe** | sold by the Weapon Merchant | the game's great axe, in metal |
| ![](docs/items/metal-pick.png) | **Metal Pick** | sold by the Weapon Merchant | the game's pick, in metal |
| ![](docs/items/metal-polearm.png) | **Metal Polearm** | carried by one of the six **Castle Guards** of the Upper Castle; an earth cleric's starting polearm | the game's polearm, in metal |
| ![](docs/items/bone-scale-arm-armor.png) ![](docs/items/bone-scale-leg-armor.png) ![](docs/items/bone-helm.png) | **Bone Scale Arm Armor**, **Leg Armor** and **Bone Helm** | in the slave pens' chest with the Bone Scale Chest Armor and Arrows +3 (the game has the set but places only the chest piece) | the set; the helm AC 1 with [Helms give AC 1](#helms), worn by those who can wear the armour (not thieves) |
| ![](docs/items/leather-helm.png) | **Helm** | in **Kurzak**'s pack, in the slave pens | the game's leather helm |
| ![](docs/items/thieves-tools.png) | **Thieves' Tools** | every thief's backpack; sold by **Kel** in his caravan (two sets, 30 each) | [picking pockets](#picking-pockets) |

The bone and obsidian weapons are also new characters' starting weapons with
[weapon specialization](#weapon-specialization), each in a material the
character can use.

**Magic items:**

| Icon | Item | Where | What it does |
|---|---|---|---|
| ![](docs/items/ring-of-protection-plus1.png) | **Ring of Protection +1** | the arena's Tied-up Prisoner: free him, then look at his body (the game's script says there's nothing; the Ledger finds a ring sewn into his loincloth, 50 XP to whoever searched) | +1 AC and +1 on every saving throw |
| ![](docs/items/pehtucls-ring-of-protection-plus1.png) | **Ring of Protection +1** | worn by **Pehtucl**, the slave pens' head templar (in the south-west corner, with the Obsidian Bloodwrath) | the same |
| ![](docs/items/cloak-of-protection-plus1.png) | **Cloak of Protection +1** | worn by Pehtucl | the same, from the cloak slot |
| ![](docs/items/inixhide.png) | **Inixhide** | worn by **Legcrusher**, the pens' half-giant | Leather Chest Armor +1: the leather's AC, +1 |
| ![](docs/items/shadowseeker.png) | **Shadowseeker** | in the pack of **Kurzak**, the pens' guard leader | a short sword +1 (1d6+1): whoever wields it, in either hand, sees the invisible |
| ![](docs/items/kreenfang.png) | **Kreenfang** | the 2 handed Bone Gythka on the dead body by the arena's stone arch | a gythka +1 (2d4+1) |
| ![](docs/items/kalzith-scroll.png) | **Six scrolls** | [Kalzith's](#kalzith) shop | spells the game has no scroll of |
| ![](docs/items/ashen-robe.png) ![](docs/items/veiled-robe.png) | **Ashen Robe**, **Veiled Robe** | worn and sold by [Kalzith](#kalzith); sold by **Kel** | [robes](#robes) for preservers, psionicists and druids |
| ![](docs/items/gutterknot.png) | **Gutterknot** | carried by **Churrr** in the warrens; a thief can lift it (200 XP) | a club +1 (the game has no magic club) |
| ![](docs/items/deepbiter.png) | **Deepbiter** | carried by one of the **Undermountain folk** (the miners) | a stone pick +1 (the game has no magic pick) |
| ![](docs/items/windlash.png) | **Windlash** | sold by the **Bowyer** | a staff sling +1 (the game has no magic staff sling) |
| ![](docs/items/greenbright.png) | **Greenbright** | carried by **Arant**, who holds the captured gladiators | a metal short sword +2 |
| ![](docs/items/drakejaw.png) | **Drakejaw** | carried by one of the **Magera** guarding the wagon's prisoners | a bone axe +1 (1d8+1): a water cleric can wield it |
| ![](docs/items/glasshewer.png) | **Glasshewer** | carried by the **Templar** of the elven slavers' camp (the one with the Chain Arm Armor) | an obsidian axe +2 (1d8+2): a fire or earth cleric can wield it |
| ![](docs/items/headsman.png) | **Headsman** | in the arena **Announcer**'s stash, with his Stoneskin scroll, rings and gems | a metal great axe +2 |
| ![](docs/items/galefang.png) | **Galefang** | carried by the **Rogue Shaman**, with his Shaman Followers | a metal dagger +2 an **air cleric** can wield (none of the game's daggers are) |
| ![](docs/items/mindshard.png) | **Mindshard** | carried by **Maris**; a thief can lift it (200 XP) | an obsidian short sword +1: a **psionicist** can wield it, alone or with a fire or earth cleric |
| ![](docs/items/stillwater.png) | **Stillwater** | in the chest **Chaya** gives as her apology | a bone short sword +1: a **psionicist** can wield it, alone or with a water cleric |
| ![](docs/items/linebreaker.png) | **Linebreaker** | carried by the **Troop Leader** | a metal polearm +2 |
| ![](docs/items/thornwall.png) | **Thornwall** | on the slave pens' **weapon rack**, in place of one of its two plain bone polearms | a bone polearm +1 |
| ![](docs/items/gythka-plus2.png) | **Gythka +2** | the **Elven Leader**'s gift, after the fight with his men | the game's Gythka +1, made +2 |
| ![](docs/items/flame-blade.png) | **Flame Blade** | in the pack of the **Templar** of the Hot Springs (the one with the Drake Shield) | an obsidian long sword +1 (1d8+1) whose blade burns what it hits: the fire clerics' Focus Heat, 2d6 fire damage to the creature hit (a save for half), as the game's Dark Flame casts Burning Hands. Obsidian, so a fire (or earth) cleric can wield it |
| ![](docs/items/tome-of-understanding.png) | **Tome of Understanding** | **Father Garyn**'s gift, in Teaquetzl, when the party brings him the ranike pith from Notaku | read as a scroll is (right-click it in the inventory, click its icon): the one whose pack it is in gains a point of WIS for good (at most 25), and the tome is gone. Not in a fight, as no scroll can be read in one |
| ![](docs/items/arrowbane.png) | **Arrowbane** | sold by **Kel** | a silver circlet: Protection from Normal Missiles on its wearer while worn (normal arrows, sling stones and chatkchas can't hurt them); worn on the head, not armour |
| ![](docs/items/sunking-crown.png) | **Sunking Crown** | worn by **Keldar**, the templar of Dagolar's tunnels | a gold crown: Protection from Evil on its wearer while worn; worn on the head, not armour |
| ![](docs/items/wardens-helm.png) | **Warden's Helm** | on **Dagolar**'s body (the one carrying Dag's Dagger) | the game's metal helm +1: Cloak of Bravery on its wearer while worn |
| ![](docs/items/wardens-arms.png) | **Warden's Arms** | the Lower Castle's treasure chest, with Dark Flame (behind the wall the Serpent Boots show, where the vrock perch) | plate arm armour +1 (AC 2, +1) |
| ![](docs/items/wardens-legs.png) | **Warden's Legs** | the Gemfields' chest | plate leg armour +1 (AC 2, +1) |
| ![](docs/items/wardens-chest.png) | **Warden's Chest** | on **Balkazar**'s body | plate chest armour +1 (AC 3, +1): Resist Fire on its wearer while worn |
| ![](docs/items/cloak-of-elvenkind.png) | **Cloak of Elvenkind** | the **Elven Leader**'s gift with his Gythka +2, after the fight with his men: "And take this cloak, woven by my own tribe for our best runners..." (left on the ground by him when it can't be carried, as the Gythka is) | a grey cloak: [all but invisible](#hiding-in-shadows-to-backstab) in a fight, with hiding to backstab on; thieves and rangers only |
| ![](docs/items/boots-of-elvenkind.png) | **Boots of Elvenkind** | the buried chest of Kel's caravan, with the Cahulaks +1 | soft boots: [silent](#hiding-in-shadows-to-backstab), with hiding to backstab on; thieves and rangers only |
| ![](docs/items/bracers-of-defense.png) | **Bracers of Defense** | **Mikquetzl** (AC 6, in his pack), **Wyrmias** (AC 5), **Balkazar** (AC 4), **Dagolar** (AC 2, the one carrying Dag's Dagger) | AC for those wearing no armour: [bracers of defense](#bracers-of-defense) |
| ![](docs/items/gutterward.png) | **Gutterward** | on a **skeleton** in the Tari's warrens (the sewers): one of the three there | the game's wooden shield +1: AC 2 better in a hand; not for thieves, as the game's wooden shield isn't |
| ![](docs/items/ironbulwark.png) | **Ironbulwark** | carried by the **Guardian** of Balkazar's fortress (the one with the Chatkcha +1) | a metal shield +3, the game's first: AC 4 better in a hand; for those who may hold the wooden shield |

**Prices** follow the game's own: magic melee weapons 20,800 a plus (41,600
for a +2; a +1 with a spell 22,000), Windlash 2,800 (as its Sling +1), plain metal weapons 50 to
300, bracers 5,000 a point of AC, Arrowbane 30,000, the Sunking Crown 40,000,
the rings and cloak of protection 15,000, Inixhide 6,000, the
Cloak of Elvenkind 25,000 and Boots 20,000, the Warden's Arms and Legs 27,000
each, Chest 36,000 and Helm 30,000, the Ashen Robe 6,000 and the Veiled Robe
40,000, Gutterward 25,000 and Ironbulwark 65,000 (the game's Drake Shield +1 is
25,400 and El's Shield +2 50,200; a price can't go past 65,535, and the game's
dearest, the Wand of Missiles, is 65,000), and the Tome of Understanding
AD&D's 43,500.

![The Tome of Understanding's box in the game: a night-steel book with a fiery emblem, 43500, Tome/Understand, and the icon to click](docs/tome.png)

**The Warden's Plate** is plate mail +1 in four pieces: the chest 4 better
than no armour (its AC 3, +1), the arms and legs 3 each (AC 2, +1), the helm 2
(a helm's AC 1 with [helms giving AC 1](#helms), +1): 12 better as a
set, so a wearer with no other help goes from AC 10 to AC −2. (With that rule
off the helm gives only its +1: 11 better, AC −1.) The game adds up its pieces' AC this way for all armour, so a
full set does better than AD&D's plate mail +1 (one suit, AC 2: 8 better). It
is metal armour, worn by the classes
that can wear the game's chain (no single-class thieves), and kept from more
with [class restrictions](#class-restrictions). **Grey's Scale**'s arm and
leg armour is AC 3 each (the game's is 2).

**New items, magical and mundane** on the Options tab places them all, the
arena's ring too; a thief's tools come with picking pockets. A thief can
[lift](#picking-pockets) Pehtucl's ring, Shadowseeker, Gutterknot and
Mindshard (200 XP for each weapon).

![The inventory screen in the game: Arrowbane, a silver circlet, in a backpack cell; the Sunking Crown, a gold crown, in the head's slot](docs/head-items.png)

![Dream's pack with the bone scale set: the chest, arm and leg pieces, and the Bone Helm under the pointer with its name](docs/bonescale.png)

**Icons and names.** Each has an icon of its own (in the tables above), made from the plain item's
the way the game makes its magic items' (a few pixels in the colours it cycles
like fire); dropped on the map they look like the plain item. The game's names
are at most 15 letters, so the rings are **RING/PROTECTION** and the cloak
**Cloak/Protectn**; the Ledger's screens and the log give them in full. As with
its own items, the game puts the material first: **Leather Inixhide**,
**Metal +1 Shadowseeker** in the item box.

![Shadowseeker's item box in the game: 22000, Detect Invisibility's icon, "Metal +1 Shadowseeker", 1D6+1](docs/shadowseeker-box.png)

**Alagorn**, the wizard of the Painted Badlands who identifies magic items,
tells the story of every magic item in the table but the plain Gythka +2
when the party carries it,
in the menu the game would put it in (swords, weapons, rings, armor, shields,
clothes or other items), before "Nothing". As with the game's own, one story for each
kind: the four pairs of bracers share one, and so do both rings of
protection. The Warden's Plate's pieces each tell a part of Haldren's, the last
of the Wardens.

How it works: [DEVELOPMENT.md](DEVELOPMENT.md#new-items).

#### Bracers of defense

A preserver can't cast in armour (with [class restrictions](#class-restrictions)),
so the Ledger adds AD&D's bracers of defense ([where](#new-items)). They are
worn on the arms, in the arm armour's place, and give the AC their name says:
AC 6 is 4 better than no armour, AC 2 is 8 better. As in AD&D they give nothing
while armour is worn: on the arms, legs or chest, or a helm (bone, leather or
metal, magical or not). A shield, rings and cloaks of protection, and the
Ledger's circlet and crown (worn on the head, but not armour) go with them.
They aren't armour to anything else: a preserver casts in them, a thief wears
them, and a ring or cloak of protection still counts. In the game they are
**BRACERS/DEFENSE** with their plus (Bracers/Defense +4 is AC 6), priced 5,000
a point of AC.

How it works: [DEVELOPMENT.md](DEVELOPMENT.md#bracers-of-defense).

#### Robes

Two magic robes for those who go without armour: preservers, psionicists and
druids alone may wear them. A robe is worn on the chest, in the chest armour's
place; like the bracers its plus betters AC only while no armour is worn on
the arms, legs or head, and it isn't armour to anything else: a preserver
casts in it, and a ring or cloak of protection still counts. Bracers go with
it.

| Icon | Robe | What it does | Where |
|---|---|---|---|
| ![](docs/items/ashen-robe.png) | **Ashen Robe** (+1) | AC 1 better; +1 on saves against wizards' and priests' spells | worn by [Kalzith](#kalzith), who sells it with his scrolls, and left with his body if he's killed (6,000) |
| ![](docs/items/veiled-robe.png) | **Veiled Robe** (+2), a robe of the Veiled Alliance | AC 2 better; +1 on every save; a wizard spell slot more at spell levels 1, 2 and 3 where the wearer has any | sold by **Kel** (40,000) |

The dice log and the Ledger name a robe among a save's modifiers, and the
Spells tab counts the Veiled Robe's slots. Alagorn tells both their stories.

How it works: [DEVELOPMENT.md](DEVELOPMENT.md#robes).

### New people

Two people of the slave pens, in new games: those that reach the pens with the
Ledger's copies of the game's files in use (a save keeps the pens as they were
when the party first went in).

#### Kalzith

A new person in the slave pens: **Kalzith**, a defiler slave the templars put
in the arena now and then (the crowd loves to watch a defiler burn), kept in
a pen of his own in the middle column the rest of the time. He has the
arena Defiler's figure and a face of his own: the game's portrait 61 with a
slave's brand on the brow, so the Dialogue tab never mistakes him for anyone
else.

![Kalzith: his talk, and his shop of six scrolls, 3,000 to 9,000 ceramic, here a quarter off with a CHA 20 leader](docs/kalzith.png)

Talk to him as to anyone (click him with the look pointer, then the Look box's
Talk button). His conversation is the game's kind, just him speaking:

- **With respect** ("We mean no harm. We're slaves too."), he owns up to
  scribing spells on scraps of hide at night, to bribe a guard, and offers
  them: **Show us what you have** opens the game's shop screen, with his six
  scrolls, one of each, and what he wears (below):

  | Level | Scroll | Price |
  |---|---|---|
  | 1 | Shield, Burning Hands | 3,000 ceramic each |
  | 2 | Blur, Cat's Grace | 6,000 each |
  | 3 | Lightning Bolt, Haste | 9,000 each |

  None of them is a spell the game has a scroll of, so they're something you
  can't find elsewhere. The prices are the game's own for the spell's level
  (3,000 a level, as most of its scrolls are), less with [the leader's
  CHA](#the-leaders-cha-at-shops).

  Cat's Grace is there only with the new spells on (see
  [New wizard spells](#new-wizard-spells)). A preserver learns a scroll's spell as from
  any of the game's (right-click it in the inventory, click its spell), by the
  game's own rules (a spell of a level the preserver can cast), and with
  [Preservers' INT](#preservers-int) on it rolls to learn it. He remembers a
  friend ("Back again? Keep your voice down."). As with the game's own people,
  a question goes from his list once asked, until the next time you talk to
  him; the shop stays.
- **During the escape**, with the alarm sounding (the game's own alarm, which
  the pens' other slaves also answer to), he has only a line for the party,
  by how he stands with them, and no talk: to a friend, "That's the alarm. So
  it's you breaking out. Go, and go quickly: if they find you at my cell, I
  burn with you."
- **Calling him a defiler**, he answers back; take it back and he's friendly,
  or **threaten to tell the templars** and he won't speak to the party again
  until they make amends: **50 ceramic** (offered only to a party that has
  it), or a plea that he wins over with a **Charisma check** (the character
  talking rolls it).

He wears an Ashen Robe and a Cloak and carries a Quarterstaff (the game's
own), and sells them too: the game's shops sell everything a merchant carries,
worn or not. Once the party has bought it all, he has nothing more to sell.
Killed, he leaves whatever of these he still has and one of the scrolls he
still had, chosen at random, in his body, and the log says which scroll.
Attacked, he turns on the party as the pens' other slaves do, and only the
guards near him join the fight. If he dies,
Dinos and the Trustee speak of him as dead; after the party's escape he is gone
from the pens with everyone else.

![Kalzith's body opened in the game: a Scroll, the Cloak and the Quarterstaff](docs/kalzith-body.png)

How it works: [DEVELOPMENT.md](DEVELOPMENT.md#kalzith).

#### Semyon

Untie the arena's prisoner and he is **Semyon**, a slave the templars tied up
in the sun for asking after the Veiled Alliance, "much more of a scout than a
warrior", as he says. He meets the party again in the arena's bone area, takes
them for the Alliance ("You must really be from the Veiled Alliance! I thought
they were a myth!") and asks to join. Made a member ("You, too, are now a
member of the Alliance.") and asked to help, he fights beside them in the next
fight and, if he survives it, leaves: "That's enough for me. I'm leaving. I'll
go find more members for the Alliance." (Some of his replies in the bone area
send him off before that: "That's enough for me. I'll see you in the holding
pens.", "Right, see you there!", or, still weak, "Why don't I meet you in the
holding pen?")
Each way, he walks out through the arena's entrance to the pens, where a
script takes him off the map, and nothing in the pens brings him back.

With the Ledger, if he left after the fight he helped in, he is there, in a pen
of his own above Kalzith's, the first time the party is in the pens after it.
His other ways out stay as in the game, and so does a Semyon who was killed: he
isn't in the pens. Talk to him (Look, then Talk): he says why the templars tied
him up in the arena (he was asking about the Veiled Alliance), passes on what he
has heard (who carries keys), reminds the party where he hid his gem (the grain
pots), and talks about the Alliance's plans, in his own voice from the arena.
As with the game's own people, each question goes from the list once asked,
and comes back the next time you talk to him.

Attacked in his pen, he turns on the party as the pens' other slaves do.

**Breaking out with Scar.** A rare way through the arena: recruit Semyon just before the fight with Scar,
take up Scar's offer to break out together, and head for the west exit. In the
game, when the alarm goes up ("Gladiators escaping! Guards! Sound the
alarms!"), Scar and his henchmen come along to the slave pens and Semyon is left
behind. With the Ledger, if he is still in the arena, alive and on the party's
side, he comes too: he stands beside Scar's men in the pens and fights the guards
with them, on the party's side. Talked to then, he says: "Scar's gladiators and
the Veiled Alliance, side by side! Who would have believed it? Stay close to
Scar: he knows the way out, and I'm right behind you." He isn't made one of the
pens' slaves while the escape lasts, and once the party is out through the
grate, he is gone with everyone else.

![The slave pens during the escape: Semyon, with his portrait, telling the party to stay close to Scar](docs/semyon-escape.png)

How it works: [DEVELOPMENT.md](DEVELOPMENT.md#semyon).

#### What Dinos and the Trustee say about them

Dinos ("Who else is in here?") and the Trustee ("Who else is in the
slavepens?") each answer questions about the others in the pens. With the
Ledger their menus also ask about Kalzith, and about Semyon once he is in his
pen ("What do you know about Kalzith?", "What can you tell me about
Semyon?"). Kalzith's question waits until the Ledger has found him in the pens
(the game's test for whether someone is there only knows the game's own
people); Semyon's once he has been in his pen. As with the game's own
questions, each is shown only until it's answered in that talk.

![The Trustee's menu (left) and Dinos's (right), scrolled to the end: after the game's own questions about people, the new ones about Kalzith and Semyon, then "Let's change the subject." and "Goodbye."](docs/pens-asks.png)

If either has been killed, they speak of him as they do of the game's dead:
the Trustee asks "What was Kalzith like?" (or Semyon) instead, with an answer
of its own, and Dinos keeps the question and answers it differently.

![The Trustee's menu with both dead (left): "What was Kalzith like?" and "What was Semyon like?" after the game's own questions; and his answer about Kalzith (right)](docs/pens-asks-dead.png)

After the party's escape, when the game empties the pens ("They killed
everybody except for myself", the Trustee says on the torture rack), Kalzith
and Semyon are taken off the map too, the way the game takes the others, and Semyon is never put in his pen after it.

How it works: [DEVELOPMENT.md](DEVELOPMENT.md#what-dinos-and-the-trustee-say-about-them).

### The cooked vulture

Hit the arena's vulture and its feathers come off (a plucked vulture); the
slave pens' campfire cooks it. In the game itself the cooked vulture is then no
use to anyone: no script asks for it. With the Ledger running, **Dinos**, the
pens' fine cook, can be asked about it: talk to him while someone in the party
carries it, and among the first things the party can say to him, just before
"Goodbye.", is **"We cooked the vulture from the arena."** He takes it ("A vulture! Give it here. A pinch of salt,
some agafari leaf, slow over the coals... Sit down and eat with me. A meal like
this puts the strength back in you."), and the game's own window for a quest's
reward follows, as for any of its quests: "Each party member receives 100
experience points!", with the sound the game plays when a quest is done (as for
the Trustee's key or the filled water jug). Each party member gets **100 XP**
(split between a multi-class character's classes, as the game splits all its
XP) and is **restored as after a full rest**: HP, PSP and spell slots full, and
anyone knocked out back on their feet. No time passes.
The question is gone once the vulture is. (Eaten by the party on their own,
used on one of them from the inventory, it's too tough to be worth the chewing.)

![Dinos's answer in his dialogue window with his portrait, then the game's own window for the reward: "Each party member receives 100 experience points!"](docs/vulture-meal.png)

How it works: [DEVELOPMENT.md](DEVELOPMENT.md#the-cooked-vulture).

## Item tables

Every magic item and every mundane weapon in a game with the
[new items](#new-items), the game's and the Ledger's, with their icons.

### Every magic item

All the magic items in a game with the Ledger's new content on: the game's own,
read from its data (each item type's slot and material, each item's plus and
power, and who carries it), and the Ledger's, in **bold**. In **Where**, "—"
means the item isn't placed with anyone in the data: the game's scripts hand it
out (a reward, a gift or a find).

**Weapons**, by material, then type:

| Icon | Material | Type | Item | Bonus / power | Where |
|---|---|---|---|---|---|
| ![](docs/items/swiftbite.png) | Bone | long sword | Swiftbite | +2 | — |
| ![](docs/items/draketooth.png) | Bone | long sword | Draketooth | +1, strength | — |
| ![](docs/items/hornblade.png) | Bone | long sword | Hornblade | +1 | Kalinin's reward |
| ![](docs/items/stillwater.png) | Bone | short sword | **Stillwater** | +1; a psionicist can wield it | the chest Chaya gives as her apology |
| ![](docs/items/gythka-plus3.png) | Bone | gythka | Gythka +3 | +3 | — |
| ![](docs/items/gythka-plus2.png) | Bone | gythka | **Gythka +2** | +2 (the game's +1) | the Elven Leader's gift |
| ![](docs/items/kreenfang.png) | Bone | gythka | **Kreenfang** | +1 | the arena's dead body |
| ![](docs/items/drakejaw.png) | Bone | axe | **Drakejaw** | +1 | a Magera guarding the wagon's prisoners |
| ![](docs/items/mace-plus2.png) | Bone | mace | Mace +2 | +2 | a chest |
| ![](docs/items/polearm-plus1.png) | Bone | polearm | Polearm +1 | +1 | — |
| ![](docs/items/thornwall.png) | Bone | polearm | **Thornwall** | +1 | the slave pens' weapon rack |
| ![](docs/items/cahulaks-plus1.png) | Bone | cahulaks | Cahulaks +1 | +1, Cause Light Wounds | the caravan's buried chest |
| ![](docs/items/dragonsbane.png) | Metal | long sword | Dragonsbane | +4 | — |
| ![](docs/items/els-drinker.png) | Metal | long sword | El's Drinker | +2, Vampiric Touch | — |
| ![](docs/items/greenbright.png) | Metal | short sword | **Greenbright** | +2 | Arant |
| ![](docs/items/shadowseeker.png) | Metal | short sword | **Shadowseeker** | +1, Detect Invisibility | Kurzak |
| ![](docs/items/dags-dagger.png) | Metal | dagger | Dag's Dagger | +3, extra damage | Dagolar |
| ![](docs/items/galefang.png) | Metal | dagger | **Galefang** | +2; an air cleric can wield it | the Rogue Shaman |
| ![](docs/items/soulcrusher.png) | Metal | axe | Soulcrusher | +1 | Kel |
| ![](docs/items/axe-plus1.png) | Metal | axe | Axe +1 | +1 | — |
| ![](docs/items/headsman.png) | Metal | great axe | **Headsman** | +2 | the arena Announcer's stash |
| ![](docs/items/linebreaker.png) | Metal | polearm | **Linebreaker** | +2 | the Troop Leader |
| ![](docs/items/dark-flame.png) | Obsidian | long sword | Dark Flame | +2, Burning Hands | the Lower Castle's chest |
| ![](docs/items/bloodwrath.png) | Obsidian | long sword | Bloodwrath | +1 | Pehtucl, the pens' templar |
| ![](docs/items/flame-blade.png) | Obsidian | long sword | **Flame Blade** | +1, Focus Heat | the Hot Springs' Templar |
| ![](docs/items/mindshard.png) | Obsidian | short sword | **Mindshard** | +1; a psionicist can wield it | Maris |
| ![](docs/items/terror-blade.png) | Obsidian | dagger | Terror Blade | +2, poison | — |
| ![](docs/items/blackmace.png) | Obsidian | mace | Blackmace | +1, Shocking Grasp | the Shadow King |
| ![](docs/items/glasshewer.png) | Obsidian | axe | **Glasshewer** | +2 | the elven slavers' Templar |
| ![](docs/items/quarterstaff-plus2.png) | Wooden | quarterstaff | Quarterstaff +2 | +2 | Maris |
| ![](docs/items/balks-staff.png) | Wooden | quarterstaff | Balk's Staff | +1, Slow | Balkazar |
| ![](docs/items/parting-staff.png) | Wooden | quarterstaff | Parting Staff | +1 | — |
| ![](docs/items/gutterknot.png) | Wooden | club | **Gutterknot** | +1 | Churrr |
| ![](docs/items/deepbiter.png) | Stone | pick | **Deepbiter** | +1 | an Undermountain miner |
| ![](docs/items/great-axe-plus3.png) | none | great axe | Great Axe +3 | +3 | the Army Commander |

**Missile weapons and ammunition:**

| Icon | Material | Type | Item | Bonus / power | Where |
|---|---|---|---|---|---|
| ![](docs/items/bow-plus2.png) | Wooden | bow | Bow +2 | +2 | a chest |
| ![](docs/items/phrains-bow.png) | Wooden | bow | Phrain's Bow | +1, Acid Arrow | — |
| ![](docs/items/sling-plus2.png) | Leather | sling | Sling +2 | +2 | Chaya and her apology chest; a chest |
| ![](docs/items/sling-plus1.png) | Leather | sling | Sling +1 | +1 | a chest |
| ![](docs/items/windlash.png) | Leather | staff sling | **Windlash** | +1 | sold by the Bowyer |
| ![](docs/items/chatkcha-plus1.png) | Obsidian | chatkcha | Chatkcha +1 | +1, Produce Fire | the Guardian |
| ![](docs/items/arrows-plus3.png) | Wooden | arrows | Arrows +3, +2, +1 | | chests; Kel and the Elven Leader (+1) |

**By weapon spec**, for [weapon specialization](#weapon-specialization):

| Weapon spec | Magic weapons |
|---|---|
| Long sword | Dragonsbane +4, Swiftbite +2, El's Drinker +2, Dark Flame +2, Draketooth +1, Hornblade +1, Bloodwrath +1, **Flame Blade** +1 |
| Short sword | **Greenbright** +2, **Shadowseeker** +1, **Mindshard** +1, **Stillwater** +1 |
| Dagger | Dag's Dagger +3, Terror Blade +2, **Galefang** +2 |
| Axe | **Glasshewer** +2, **Drakejaw** +1, Soulcrusher +1, Axe +1 |
| Great axe | Great Axe +3, **Headsman** +2 |
| Gythka | Gythka +3, **Gythka +2**, **Kreenfang** +1 |
| Polearm | **Linebreaker** +2, Polearm +1, **Thornwall** +1 |
| Mace | Mace +2, Blackmace +1 |
| Quarterstaff | Quarterstaff +2, Balk's Staff +1, Parting Staff +1 |
| Sling | Sling +2, Sling +1 |
| Club, pick, cahulaks | **Gutterknot** +1, **Deepbiter** +1, Cahulaks +1 |
| Bow, staff sling, chatkcha | Bow +2, Phrain's Bow +1, **Windlash** +1, Chatkcha +1 |

**Body armour:**

| Icon | Material | Item | Bonus / power | Where |
|---|---|---|---|---|
| ![](docs/items/shimmer-armor.png) | Leather | Shimmer Armor | +3, Free Action | Dakaren |
| ![](docs/items/drake-armor.png) | Leather | Drake Armor | +1, Resist Cold | the Wyvern Master |
| ![](docs/items/inixhide.png) | Leather | **Inixhide** | +1 | Legcrusher |
| ![](docs/items/wardens-chest.png) | Metal | **Warden's Chest** | plate +1, Resist Fire | Balkazar |
| ![](docs/items/silk-armor.png) | none | Silk Armor | +2 | — |

**Arm and leg armour:**

| Icon | Slot | Material | Item | Bonus | Where |
|---|---|---|---|---|---|
| ![](docs/items/tanelyvs-arm-armor.png) | Arms | Metal | Tanelyv's Armor | chain +2 | — |
| ![](docs/items/wardens-arms.png) | Arms | Metal | **Warden's Arms** | plate +1 | the Lower Castle's chest |
| ![](docs/items/greys-scale-arms.png) | Arms | Metal | Grey's Scale | no plus (AC 3 with the Ledger) | Arant |
| ![](docs/items/tanelyvs-leg-armor.png) | Legs | Metal | Tanelyv's Armor | chain +2 | — |
| ![](docs/items/wardens-legs.png) | Legs | Metal | **Warden's Legs** | plate +1 | the Gemfields' chest |
| ![](docs/items/greys-scale-legs.png) | Legs | Metal | Grey's Scale | no plus (AC 3 with the Ledger) | Arant |

Tanelyv's Armor also has a chest piece, with no plus.

**Head:**

| Icon | Material | Item | Power | Where |
|---|---|---|---|---|
| ![](docs/items/helm-of-might.png) | Leather | Helm of Might | strength | — |
| ![](docs/items/leather-helm.png) | Leather | Leather helm +1 | | a chest |
| ![](docs/items/helm-of-contemplation.png) | Metal | Helm of Contemplation | a shield of thought against psionic attacks | the Warren Chief |
| ![](docs/items/wardens-helm.png) | Metal | **Warden's Helm** | +1, Cloak of Bravery | Dagolar |
| ![](docs/items/arrowbane.png) | none (not armour) | **Arrowbane** | Protection from Normal Missiles | sold by Kel |
| ![](docs/items/sunking-crown.png) | none (not armour) | **Sunking Crown** | Protection from Evil | Keldar |

**Shields and gloves** (worn in a hand, in this game):

| Icon | Material | Item | Bonus / power | Where |
|---|---|---|---|---|
| ![](docs/items/els-shield.png) | Leather | El's Shield | +2 | — |
| ![](docs/items/drake-shield.png) | Leather | Drake Shield | +1, Resist Fire | the Hot Springs' Templar |
| ![](docs/items/gutterward.png) | Wooden | **Gutterward** | +1 | a skeleton in the warrens |
| ![](docs/items/ironbulwark.png) | Metal | **Ironbulwark** | +3 | the Guardian of Balkazar's fortress |
| ![](docs/items/chameleon-gloves.png) | Leather | Chameleon Gloves | blind whoever they touch | Mikquetzl |
| ![](docs/items/quicksilver-gauntlets.png) | none | Quicksilver Gauntlets | graft a one-handed weapon to the hand | — |

**Other worn items:**

| Icon | Slot | Item | Power | Where |
|---|---|---|---|---|
| ![](docs/items/bracers-of-defense.png) | Arms | **Bracers of Defense** | AC 6, 5, 4 or 2 with no armour | Mikquetzl, Wyrmias, Balkazar, Dagolar |
| ![](docs/items/ashen-robe.png) | Chest | **Ashen Robe** | +1 AC; +1 on saves against spells | Kalzith |
| ![](docs/items/veiled-robe.png) | Chest | **Veiled Robe** | +2 AC; +1 on every save; a wizard slot more at spell levels 1-3 | sold by Kel |
| ![](docs/items/belt-of-might.png) | Waist | Belt of Might | strength | — |
| ![](docs/items/serpent-boots.png) | Feet | Serpent Boots | Displacement | a chest |
| ![](docs/items/boots-of-elvenkind.png) | Feet | **Boots of Elvenkind** | move silently | the caravan's buried chest |
| ![](docs/items/living-cloak.png) | Cloak | Living Cloak | Inertial Barrier | Dagolar |
| ![](docs/items/cloak-of-protection-plus1.png) | Cloak | **Cloak of Protection +1** | +1 AC and saves | Pehtucl |
| ![](docs/items/cloak-of-elvenkind.png) | Cloak | **Cloak of Elvenkind** | hide in shadows | the Elven Leader's gift |
| ![](docs/items/silver-necklace.png) | Neck | Silver Necklace | Biofeedback | — |
| ![](docs/items/obsidian-necklace.png) | Neck | Obsidian Necklace | Disintegrate | the Troop Leader |
| ![](docs/items/iron-necklace.png) | Neck | Iron Necklace | Fireball | the Hermit |
| ![](docs/items/golden-torque.png) | Neck | Golden Torque | takes on its maker's morals | — |
| ![](docs/items/light-of-dawn.png) | Finger | Light of Dawn | Dismissal | on the ground, in Balkazar's region |
| ![](docs/items/steadfast-ring.png) | Finger | Ring of Steadfastness | Constitution | — |
| ![](docs/items/ring-of-insight.png) | Finger | Ring of Insight | Wisdom | — |
| ![](docs/items/els-ring.png) | Finger | El's Ring | Dexterity | on the ground |
| ![](docs/items/storm-ring.png) | Finger | Storm Ring | Ice Storm | a chest |
| ![](docs/items/wind-ring.png) | Finger | Wind Ring | Protection from Normal Missiles | the Wyvern Master |
| ![](docs/items/ring-of-protection-plus1.png) ![](docs/items/pehtucls-ring-of-protection-plus1.png) | Finger | **Ring of Protection +1** (two) | +1 AC and saves | the arena's Tied-up Prisoner; Pehtucl |

**Held, or used from the pack:**

| Icon | Item | Power | Where |
|---|---|---|---|
| ![](docs/items/orb-of-knowledge.png) | Orb of Knowledge (held) | watch the one it's tuned to | — |
| ![](docs/items/dagolars-wand.png) | Dagolar's Wand | Control Body | Dagolar |
| ![](docs/items/wand-of-missiles.png) | Wand of Missiles | Magic Missile | a chest |
| ![](docs/items/derths-wand.png) | Derth's Wand | Lightning Bolt | — |
| ![](docs/items/wildwynd-wand.png) | Wildwynd Wand | Confusion | — |
| ![](docs/items/llods-rod.png) | Llod's Rod | travel between the obelisks | the Visionary |
| ![](docs/items/tome-of-understanding.png) | **Tome of Understanding** | +1 WIS when read | Father Garyn's gift |
| ![](docs/items/apple.png) ![](docs/items/scroll.png) ![](docs/items/kalzith-scroll.png) | Magic fruit (14 kinds), spell scrolls (18), psionic scrolls (11), **Kalzith's six scrolls** | used once | many places |

### Every mundane weapon

Every plain weapon in a game with the new items, the game's and the Ledger's,
by type and material: who sells it and who carries it (by the names the game
gives them; many are of a kind, such as every Renegade or Tari). The **Weapon
Merchant** and the **Bowyer** are in Teaquetzl, **Jark** and **Kel** in Kel's
caravan. The game's plain stone pick is only ever a
[starting weapon](#weapon-specialization); Deepbiter is its magic one.

| Icon | Type | Material | Sold by | Carried by, or found in |
|---|---|---|---|---|
| ![](docs/items/bone-long-sword.png) | long sword | bone | Jark, Weapon Merchant | Ranger, Templar, Chaero, Castle Guard, Arant's Guard, Warrior, Dagolar Guard, Caravan Guard, Guard, Lt. Kwerin, Slaver Guard, Messenger, Visitor, Renegade, Silt Runner |
| ![](docs/items/metal-long-sword.png) | long sword | metal | Weapon Merchant | Uskuye, Elven Leader, Elite Guard, Village Hero, a chest in the warrens |
| ![](docs/items/obsidian-long-sword.png) | long sword | obsidian | Jark, Weapon Merchant | Wyvern Master, Arant, Keldar, Kurzak, Guard, Chaya, Uskuye, Scar, Arena Guard, Caravan Master, Chahl, Mayor of Gedron, Merzol, Drajian Guard, Council Member, Templar |
| ![](docs/items/club.png) | club | wood | Weapon Merchant | Warren Chief, Churrr, Tari, Skull Guardian, Worshipper, Low Warren Thug, Gladiator, Wild Mul, Guard, Legcrusher, a dead body in the arena, a chest, a weapon rack |
| ![](docs/items/bone-dagger.png) | dagger | bone | Jark, Weapon Merchant | Defiler |
| ![](docs/items/metal-dagger.png) | dagger | metal | — | Tobrian |
| ![](docs/items/obsidian-dagger.png) | dagger | obsidian | — | Defiler, Notaku |
| ![](docs/items/stone-dagger.png) | dagger | stone | Jark, Weapon Merchant | Balkazar, Dagolar, Wyrmias, Hermit, Tobrian, Villager, Linara, Maris, a chest in Dagolar's tunnels |
| ![](docs/items/bone-short-sword.png) | short sword | bone | Jark, Weapon Merchant | Renegade |
| ![](docs/items/short-sword.png) | short sword | metal | Weapon Merchant | — |
| ![](docs/items/obsidian-short-sword.png) | short sword | obsidian | Jark, Weapon Merchant | Chaero |
| ![](docs/items/bone-mace.png) | mace | bone | Jark, Weapon Merchant | Wyvern Master, Krikor, Templar, a chest, a chest in Dagolar's tunnels |
| ![](docs/items/metal-mace.png) | mace | metal | — | Templar |
| ![](docs/items/obsidian-mace.png) | mace | obsidian | Jark, Weapon Merchant | Tari |
| ![](docs/items/bone-axe.png) | axe | bone | Jark, Weapon Merchant | Wild Mul |
| ![](docs/items/metal-axe.png) | axe | metal | — | Slaver Guard, Uzoma, a weapon rack in the Lower Castle, a weapon rack, a weapon rack in the slave pens |
| ![](docs/items/obsidian-axe.png) | axe | obsidian | Weapon Merchant | Merzol |
| ![](docs/items/bone-great-axe.png) | great axe | bone | Jark, Weapon Merchant | Wild Mul |
| ![](docs/items/metal-great-axe.png) | great axe | metal | Weapon Merchant | — |
| ![](docs/items/obsidian-great-axe.png) | great axe | obsidian | Jark, Weapon Merchant | — |
| ![](docs/items/metal-pick.png) | pick | metal | Weapon Merchant | — |
| ![](docs/items/quarterstaff.png) | quarterstaff | wood | Jark, Weapon Merchant | Mikquetzl, Troop Leader, Dakaren, Dagolar, Wyrmias, Hermit, Father Garyn, Notaku, a weapon rack in the Lower Castle, a skeleton in the Undermountain, a chest, a weapon rack in the slave pens |
| ![](docs/items/bone-polearm.png) | polearm | bone | Weapon Merchant | a weapon rack in the Lower Castle, a weapon rack in the slave pens |
| ![](docs/items/metal-polearm.png) | polearm | metal | — | Castle Guard |
| ![](docs/items/gythka.png) | gythka | bone | Jark, Weapon Merchant | Guardian |
| ![](docs/items/cahulaks.png) | cahulaks | bone | Weapon Merchant | — |
| ![](docs/items/chatkcha.png) | chatkcha | obsidian | Jark, Bowyer | — |
| ![](docs/items/bow.png) | bow | wood | Jark, Kel, Bowyer | Wyvern Master, Ranger, Arant, Castle Guard, Guard, Arant's Guard, Arena Guard, Caravan Guard, Slaver Guard, Elven Leader, Uzoma, Drajian Guard, Army Commander, Elite Guard, Village Hero, a chest in the Upper Castle, a chest, a chest in Dagolar's tunnels |
| ![](docs/items/sling.png) | sling | leather | Bowyer | Mehtar, Renegade, Silt Runner, a chest in the slave pens, a bag in the slave pens |
| ![](docs/items/staff-sling.png) | staff sling | leather | Jark, Bowyer | — |

## Graphics

What the Ledger draws on the game's map. The elves' and half-elves' looks,
the party's gear, shadows and dust each have a switch in the Options tab's
**Graphics** section.

### Elves and half-elves

Elves have pointed ears, walking and fighting, beside any helm. Half-elves have
their own look (the game draws them with the human pictures), made from the
game's pictures in colours the party's figures already use. A half-elf man is
built like the elf man, a little broader, with fair hair cut short at the nape,
a linen shirt under a leather jerkin, green trousers, brown boots and small
pointed ears. A half-elf woman is a little slimmer than the human woman, with
golden hair up in a bun, pointed ears, a purple cloak, purple wristbands and
red boots. Anything worn is drawn over these in its own colours, so a worn
cloak or boots replace the purple and the red.

With **Elves have pointed ears, and half-elves figures of their own** unticked
(it's ticked by default), elves are as the game draws them, and half-elves
are the human figures in their own colours. It counts from the next time the
game is started.

Cilla, in the game's own party, is an elf, but the game gives her the figure it
gives half-elf women. With **Cilla, an elf in the game's own party, drawn as
an elf** ticked (the default), the Ledger gives her the elf woman's, in a new
game and in one already begun (there from the next area or load on), whatever
the switch above. Unticked, she keeps the game's half-elf woman's figure, from
the next time the game is started (a game where she already has the elf's
keeps it).

![Humans (top), elves (middle) and half-elves (bottom), men on the left and women on the right, walking: the elves with pointed ears; the half-elf man fair-haired in a leather jerkin and green trousers, the half-elf woman with her golden hair in a bun, pointed ears, a purple cloak and red boots](docs/half-elves.png)

How it works: [DEVELOPMENT.md](DEVELOPMENT.md#elves-and-half-elves).

### What the party wears

The party's figures on the map and in fights show what each one wears, and
change as soon as their gear does (switch it off on the Options tab to see the
game's own). The game draws each race and sex the same whatever they carry;
the Ledger keeps the artist's pictures and adds to them, frame by frame,
walking and fighting:

| Worn | Shown |
|---|---|
| **Weapons and shields** | each weapon type its shape (dagger, sword, club, mace, axe, polearm, gythka, staff, a round shield), in its material's colours (wood, bone in ivory, stone, obsidian, metal; Kreenfang's two blades in the fire colours and Shadowseeker's in night steel, as their icons); walking, a one-handed weapon is worn at the belt, hanging down and back like a scabbard, two-handed ones are carried upright, and a shield is on the arm (from the side, on the far arm held forward of the chest, so it shows past the body); in a fight they are in the hands and swung, and the shield is on the other forearm in every pose (placed by hand for each model where the arm is hidden or flung) |
| **Bows and slings** | the bow and quiver on the back (the game draws the bow when shooting), a sling or chatkcha at the hip |
| **Armour** | the character's own clothing recoloured toward its material, shade for shade (leather, bone, chain, plate, scale...): the chest piece above the waist, arm pieces at the wrists, leg pieces below the waist; on figures the artist drew mostly bare (the mul, the dwarf man) only their straps and loincloth change, so it shows little |
| **Helms** | a circlet at the brow blended into the hair: a feather on leather, a dark stone on iron, low spikes on bone |
| **Cloaks** | the cloak the game draws on the human woman (its folds and swing as she walks and fights), fitted to the wearer, under the hair, in the cloak's colours; a half-elf woman's own purple cloak takes the worn one's colours |
| **Boots and belts** | the feet and the waist recoloured |

The colours are muted ones no region's palette changes. A thri-kreen shows
only weapons and shields (all it can use). Two party members of the same race
and sex each show their own equipment: the game gives them one figure, so the
second is moved to pictures of their own.

![The party in the arena as the game draws them (left) and with gear and shadows on (right): Gerakis with his bone long sword and gythka, Cermak with his staff and sling, Cilla (an elf) with her bone long sword and sling, each casting a shadow toward the lower right](docs/gear.png)

How it works: [DEVELOPMENT.md](DEVELOPMENT.md#what-the-party-wears).

### Shadows

Every living figure on the map (the party, the people, the monsters; not the
dead, nor items) casts a soft see-through shadow on the floor, its outline laid
long toward the lower right, the way the walls' own shadows fall (the light on
the game's maps comes from the upper left). The shadows are drawn on the floor
before anything else, so every figure and wall stands on top of them: a shadow
never covers another figure. Switch them off on the Options tab.

![The arena without shadows (left) and with them (right): each figure's outline darkened on the sand behind it, the sand's colours kept](docs/shadows.png)

How it works: [DEVELOPMENT.md](DEVELOPMENT.md#shadows).

### Dust

Anyone walking on sand or dirt raises little puffs of dust behind their feet,
which spread, rise a little and fade in about a second. The walls and figures
stand in front of them, as with the shadows. Switch it off on the Options tab.

![The party walking across the arena's sand: puffs of dust behind them, spreading and fading](docs/dust.png)

How it works: [DEVELOPMENT.md](DEVELOPMENT.md#dust).

## Controls

Each is switched on the Options tab's **Controls** group.

### Choosing an enemy: Tab, Enter and the rings

In a fight, a red ring on the ground can mark the enemies, under their feet (the
figures stand in it, as on their shadows). On a party member's turn, **Tab**
chooses an enemy, the nearest first, then the next nearest (**Shift+Tab** goes
back): its ring is drawn thicker and redder, the view scrolls to it if it is
out of sight, and the log names it. **Enter** then attacks it, as clicking on
it does (walking up to it first when it is out of reach), even where another
figure stands in front of it. On the Options tab the rings are **none**, **only
under the enemy chosen with Tab** (the default: none until Tab is pressed) or
**under all the enemies** (the chosen one's thicker and redder); Tab and Enter
have a switch of their own.

![The arena fight with rings under all the enemies, two Sligs and a Screamer Beetle, one Slig chosen with Tab](docs/rings.png)

Tab and Enter also make attacking possible without aiming the mouse at all.

How it works: [DEVELOPMENT.md](DEVELOPMENT.md#choosing-an-enemy-tab-enter-and-the-rings).

### Scrolling the map

Press the mouse wheel on the map and move the mouse: the map moves with the
pointer, as if dragged, in fights too. On the Options tab it can be switched
off, or holding the right button made to drag the map as well (a right click,
let go before the pointer has moved, still changes the pointer between walking,
using and looking). The game still scrolls on its own when the pointer touches
the screen's edge, and still brings the view back to whoever's turn it is in a
fight.

The view can't be zoomed: the game draws a 320 by 200 screen at one scale,
with the view's size built into its drawing code and its video memory pages.

How it works: [DEVELOPMENT.md](DEVELOPMENT.md#scrolling-the-map).

### Spells on the Effects screen

On the Effects screen (a character's spells and powers in effect), a click on
an effect's icon ends it in the game, so a stray click loses a spell. With the
Ledger a click leaves a spell on; a psionic power's effect still ends, as that
is how a power is stopped. It is a change to the game itself, from the next
time it is started.

## More saves and characters

### More saves

The game's save and load window holds 10 saves. With the Ledger it holds 40,
on four pages of ten: the **PAGE 1** to **PAGE 4** buttons under EXIT show a
page, the page shown has its button greyed, and **PgDn** and **PgUp** go to
the next page and the one before. Save and load as always; the window opens
on the page last shown. In the load window, PgDn and PgUp pass by pages with
no saves; a page's button shows it even with none, with **LOAD** greyed (and
Enter doing nothing) until you go to a page with a save. (The game itself
never lets you choose an empty row to load; loading one would start a new
game.)

![The load window on page 1 (left): the game's ten saves, and the PAGE 1 (greyed) to PAGE 4 buttons under LOAD and EXIT; and on an empty page 2 (right), with LOAD greyed](docs/save-pages.png)

Page 1 is the game's own saves, `SAVE01.SAV` to `SAVE10.SAV` in the game
folder (or, with GOG's DOSBox, its `cloud_saves` folder); pages 2 to 4 are `SAVB01.SAV` to `SAVB10.SAV`, `SAVC..` and `SAVD..`,
next to them. The game started without the Ledger shows page 1 only, as
always: it looks for `SAVE??.SAV`, and the other pages' names don't match. (It
had better not see them: it puts each save it finds in the row its number
names, with room for ten, and a `SAVE11.SAV` would be written past the end.)

How it works: [DEVELOPMENT.md](DEVELOPMENT.md#more-saves).

#### Saves under their names

Only the game's list says which file is which save. While its window is open,
the Ledger keeps a second copy of every save, under the name you typed for it in the
game, in its own **Named saves** folder: `Page 2 slot 05 - Before Scar's
battle.SAV`. Saving over a slot replaces that slot's copy. The Options tab's
**Saves** section has **Open the folder**, and **Put a save in a slot...**,
which copies a named save (or any save file) into the page and slot you give,
asking first if that slot holds one, to be loaded from the game's list.

### More characters

The game keeps up to 19 characters made with CREATE CHARACTERS (and the party
members dropped back to the roster); a 20th is refused with "Maximum
characters". With the Ledger it keeps 29. The roster in the ADD window
scrolls through them all, as it did through 19.

They are in the game's own `CHARSAVE.GFF`, each under a number, 1 to 29. The
game started without the Ledger reads numbers 1 to 19 only: characters saved
under 20 to 29 aren't shown, and aren't lost; they come back with the Ledger.
(The game saves a new character under the highest free number, so the first
ten made after the 19th go to 20 to 29.)

The patched game also fixes a bug of the game's own: **DELETE** in the
roster deleted the character in the row clicked counting from the top of the
list, not from the top of what was shown. With the list scrolled down,
another character was deleted. Now it deletes the one chosen.

A character made with CREATE CHARACTERS is **New** until the game starts,
when the game makes it Okay (and gives a New one the starting gear). The game's
tests for Okay left New out, so a New thief's skills all showed 0 on the
inventory screen, and the Ledger did the same. The patched game counts New as
Okay wherever it tests for Okay, and so does the Ledger. Left as they were: the
status under the portrait still reads New, and the game still gives the
starting gear and makes New characters Okay when the game starts.

How it works: [DEVELOPMENT.md](DEVELOPMENT.md#more-characters).

## Game speed

The game draws the view a frame at a time and shows each at the screen's next
refresh (70 a second), and a walking figure takes a step a frame. A frame that
takes a moment longer than a refresh waits for the next one, so it shows
twice as late, and walking goes at half speed. Everything drawn adds up: four
figures rather than the leader alone (the game's manual says collapsing the
party "speeds up the game"), the gear on them, the shadows, the dust.

The launcher gives DOSBox more of the computer's time: 20,000 cycles a
millisecond by default, where GOG's settings give 7,000. On the Options tab
**Game speed** is GOG's own, that, or 35,000: there, with everything on, the
whole party in view walks as fast as the leader alone, but it needs a faster
computer. It applies the next time the game is started. Both of the Ledger's
run on DOSBox's dynamic core (GOG's settings run this game on the slower
normal core): the same cycles do more, and cost the computer about a third
less.

Measured in the slave pens, walking (the leader's speed in pixels a second of
the game's time; higher is smoother):

| | All four in view | The leader alone |
|---|---|---|
| 20,000 cycles, the Ledger's shadows, dust, rings and gear off | 248 | 254 |
| 20,000, everything on | 139 | 263 |
| 30,000, everything on | 214 | 264 |
| 35,000, everything on | 258 | 254 |
| 40,000, everything on | 267 | 269 |

So at 20,000 the Ledger's own drawing is what slows the whole party: without
it the four walk as fast as one. Of it, the dust costs the most (each puff is
worked out pixel by pixel, and four walkers raise four times as many), then
the shadows. What each setting asks of the computer: [Suggested system
requirements](#suggested-system-requirements).

How it works: [DEVELOPMENT.md](DEVELOPMENT.md#game-speed).

## Accessibility

Templar's Ledger aims at the AODA's standard for software people read,
WCAG 2.0 level AA:

- **Contrast:** every colour used for text has at least 4.5:1 contrast with
  its background (the game's lighter stone is kept for bevels, not behind
  text). `tests/test_theme.py` checks each pair.
- **Colour is never the only signal:** log lines say `HIT`, `miss`, `saves`
  and so on in words, and changed bytes in the record view are underlined as
  well as highlighted.
- **Text size:** **A+** / **A-** at the top, or **Ctrl +**, **Ctrl -** and
  **Ctrl 0** (back to normal), enlarge or shrink all text up to 2.5 times.
  The Options tab's longer lines wrap to the window rather than run out of it.
- **Keyboard:** Tab and Shift+Tab move between controls, and the one with the
  keyboard focus is outlined in yellow. **Ctrl+Tab** switches tabs, as do
  **Alt+L** (Dice log), **Alt+I** (Dialogue), **Alt+S** (Spells), **Alt+M**
  (Memory tools) and **Alt+O** (Options), and on the party side **Alt+C** (Characters) and
  **Alt+A** (All fields).
- **In the game,** Tab and Enter choose and attack an enemy in a fight with no
  aiming of the mouse (see [Choosing an enemy](#choosing-an-enemy-tab-enter-and-the-rings)).
- **The game's font** is only used for the title: it's a 9-pixel bitmap
  font, fine enlarged as a heading but harder to read than ordinary text,
  so everything else is in the system's fonts.
- **Screen readers:** tkinter's windows are not read well by screen readers.
  **Save...** on the Dice log and Dialogue tabs writes the log to a text file,
  and `python -m dscompanion dicelog` prints the same log (dialogue included) in
  a command prompt, which screen readers do read.

## Without the game

**Checking a save file:** drag a `SAVEnn.SAV` file from the game folder onto
**`Show Save.bat`**.

**Practising:** `tests/make_fake_party.py` writes `FAKEPTY.COM`, a tiny DOS program holding two
made-up characters in the same record shapes as the game. The first character
loses 1 HP every second. Run it in DOSBox and try the viewer (search for
`SADIRA`).

```
python tests/make_fake_party.py
dosbox FAKEPTY.COM
```

![The Ledger on the practice program: All fields with Sadira and Rikus, and Memory tools with her record found and its bytes](docs/viewer.png)
