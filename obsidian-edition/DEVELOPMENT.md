# Obsidian Edition: development

How Obsidian Edition and the Dark Sun Obsidian Edition Loader, which starts
the game with it, work inside: the patched game and its helper, what's known
of the game's data, the tools for mapping it, and how each part of the
[README](README.md) and the [features page](FEATURES.md) is done.

## Contents

- [Building and testing](#building-and-testing)
  - [The folders](#the-folders)
  - [Tests](#tests)
  - [Making a release](#making-a-release)
  - [From a command prompt](#from-a-command-prompt)
  - [Practising without the game](#practising-without-the-game)
  - [Mapping memory](#mapping-memory)
  - [Command-line mapping tools](#command-line-mapping-tools)
- [How the dice log works](#how-the-dice-log-works)
- [What is known](#what-is-known)
- [Room in the helper](#room-in-the-helper)
- [The crash report](#the-crash-report)
- [The freeze report](#the-freeze-report)
- [Reading the game's memory](#reading-the-games-memory)
  - [Changing the game's item lists](#changing-the-games-item-lists)
- [How each part works](#how-each-part-works)
  - [The Dialogue tab](#the-dialogue-tab)
  - [Searching junk, hay and wardrobes](#searching-junk-hay-and-wardrobes)
  - [The Bowyer's archery target](#the-bowyers-archery-target)
  - [Ability checks in the scripts'
    conditions](#ability-checks-in-the-scripts-conditions)
  - [The combat log in the game](#the-combat-log-in-the-game)
  - [Names over figures](#names-over-figures)
  - [THAC0, saves and thief skills](#thac0-saves-and-thief-skills)
  - [Detonate's blast on an item](#detonates-blast-on-an-item)
  - [The psionic power check](#the-psionic-power-check)
  - [What hurts a monster (the Look box)](#what-hurts-a-monster-the-look-box)
  - [Charges in item boxes](#charges-in-item-boxes)
  - [No manual check](#no-manual-check)
  - [The game's script bugs](#the-games-script-bugs)
  - [Class restrictions](#class-restrictions)
  - [Multiclass hit points](#multiclass-hit-points)
  - [Hit dice: the better of two](#hit-dice-the-better-of-two)
  - [Scores and hit points as rolled](#scores-and-hit-points-as-rolled)
  - [Rangers' casting level](#rangers-casting-level)
  - [Preservers' INT](#preservers-int)
  - [AD&D's class tables](#adds-class-tables)
  - [Spells saved against with the spell
    save](#spells-saved-against-with-the-spell-save)
  - [Fire, cold and electricity: DEX instead of a doubled
    d20](#fire-cold-and-electricity-dex-instead-of-a-doubled-d20)
  - [Two weapons](#two-weapons)
  - [Items saving against acid](#items-saving-against-acid)
  - [Rings and cloaks of protection](#rings-and-cloaks-of-protection)
  - [Half-giants' two-handed weapons](#half-giants-two-handed-weapons)
  - [Helms](#helms)
  - [Weapon specialization](#weapon-specialization)
  - [Kits](#kits)
  - [Level cap by XP](#level-cap-by-xp)
  - [STORE and RECALL on the creation
    screen](#store-and-recall-on-the-creation-screen)
  - [Fuller starting gear](#fuller-starting-gear)
  - [The game's own party](#the-games-own-party)
  - [The leader's CHA at shops](#the-leaders-cha-at-shops)
  - [Buying back magical items](#buying-back-magical-items)
  - [Thief skills from AD&D's table](#thief-skills-from-adds-table)
  - [Hiding in shadows to backstab](#hiding-in-shadows-to-backstab)
  - [Spell arrows](#spell-arrows)
  - [Picking pockets](#picking-pockets)
  - [Mirror Image](#mirror-image)
  - [The game's spells](#the-games-spells)
  - [New spells (wizard and 6th-level
    priest)](#new-spells-wizard-and-6th-level-priest)
  - [New items](#new-items)
  - [Bracers of defense](#bracers-of-defense)
  - [Robes](#robes)
  - [Girdles and the amulet](#girdles-and-the-amulet)
  - [Kalzith](#kalzith)
  - [Semyon](#semyon)
  - [What Dinos and the Trustee say about
    them](#what-dinos-and-the-trustee-say-about-them)
  - [The cooked vulture](#the-cooked-vulture)
  - [Defilers' scrolls](#defilers-scrolls)
  - [What the party wears](#what-the-party-wears)
  - [Elves and half-elves](#elves-and-half-elves)
  - [Shadows](#shadows)
  - [Dust](#dust)
  - [Scripts' requests and refused casts in the dice
    log](#scripts-requests-and-refused-casts-in-the-dice-log)
  - [Choosing an enemy: Tab, Enter and the
    rings](#choosing-an-enemy-tab-enter-and-the-rings)
  - [Scrolling the map](#scrolling-the-map)
  - [The pointer in scenes, and where it
    starts](#the-pointer-in-scenes-and-where-it-starts)
  - [More saves](#more-saves)
  - [More characters](#more-characters)
  - [Game speed](#game-speed)

## Building and testing

### The folders

| Folder or file | What it holds |
|---|---|
| `dsloader/` | the Loader: its window (`viewer.py`), starting the game (`launch.py`), the dice log (`dicelog.py`), the patched game (`gamepatch.py`) and the data written into the game's files (one module for each feature) |
| `dos/` | the helper DOSBox loads, `dsclog.asm` (built to `DSCLOG.EXE`), `umbplus.asm` (`UMBPLUS.COM`) and `gameend.asm` (`GAMEEND.COM`) |
| `layouts/` | the game's memory layout (`shattered_lands.json`), for the Loader's window and Memory tools |
| `tests/` | the unit tests, and `make_fake_party.py` for practising without the game |
| `docs/` | the screenshots and the item icons the documentation shows |
| `*.bat` | what players double-click: the Loader, the game with or without its window, a save file's party |
| `../PATCH-NOTES.md`, `../CHANGELOG.md`, `../release-notes/` | the repository's root: the patch notes, the record of every pull request, and each release's notes |

Each module of `dsloader` opens with what it does. Those the sections below
don't come back to: `gff.py` and `gpl.py` read the game's GFF files and its
scripts; `guestmem.py` finds DOSBox's guest memory; `savefile.py` reads a
save's party (`Show Save.bat`); `tracker.py` notes kills, XP and level-ups;
`textlog.py` reads the dialogue and message boxes DSCLOG copies; `partyview.py`
and `spellbook.py` draw the Characters and Spells tabs, `theme.py` the window's
look; `bonescale.py` puts the bone scale set together in its chest;
`stuckwalk.py` sets people walking again whose scripted walk stopped.

### Tests

```
python -m unittest discover -s tests
```

Two web pages are made from Markdown, and a test fails when either falls behind:
`player-guide.html` from `PLAYER-GUIDE.md` (`python -m dsloader.guidepage`) and
`../patch-notes.html` from `../PATCH-NOTES.md` (`python -m
dsloader.patchnotes`). Edit the Markdown, then run the module. Both use
`dsloader/pagestyle.css`.

`tests/test_dsclog.py` runs the helper's interrupt handlers in a CPU emulator
when `unicorn` is installed (`pip install unicorn`), and is skipped otherwise.
After changing `dos/dsclog.asm`, rebuild the helper with
[NASM](https://www.nasm.us/):

```
nasm -f bin -o dos/DSCLOG.EXE dos/dsclog.asm
```

The header's signature (`DSCLOGva` now: after Z, lowercase) goes up whenever the
helper and the Loader must change together (`HDR_SIG` in `dsloader/dicelog.py`),
so a Loader never talks to an older helper.

The post-game check that keeps an error on screen for the crash report, and
the program that moves upper memory down before the helper loads (see [Room in
the helper](#room-in-the-helper)), are built the same way:

```
nasm -f bin -o dos/GAMEEND.COM dos/gameend.asm
nasm -f bin -o dos/UMBPLUS.COM dos/umbplus.asm
```

### Making a release

The **Release** workflow (`.github/workflows/release.yml`) runs the tests on
Windows, zips the `obsidian-edition` folder as
`Dark-Sun-Shattered-Lands-Obsidian-Edition-<version>.zip` (with `git archive`,
so only what is committed goes in) and publishes it with
`release-notes/v<version>.md` as its notes. Before it:

1. Set the version in `dsloader/__init__.py` (`__version__`), the patch notes'
   "Current version" (and drop their line on what comes with the next release)
   and the front page's "**Obsidian Edition ...** is out";
   `tests/test_version.py` checks they agree and that the release notes exist.
2. Finish `release-notes/v<version>.md` and the CHANGELOG's entry, and
   rebuild `DSCLOG.EXE` and the web pages if their sources changed.
3. Merge to `main`, then push the tag `v<version>`, or run the workflow by hand
   (Actions → Release → Run workflow), which makes the tag.

The zip holds the `obsidian-edition` folder only: the root's patch notes,
CHANGELOG and release notes stay on GitHub, so the folder's own pages link to
them by their GitHub address.

### From a command prompt

What the `.bat` files do, from a command prompt (`dsloader` is the program's
internal name):

```
python -m dsloader launch                        # start the game with the dice log, and the Loader's window
python -m dsloader view                          # the Loader's window only, game not started
python -m dsloader play                          # the game with the in-game additions, no window
python -m dsloader dicelog                       # the dice log in the command prompt
python -m dsloader checks                        # the scripts' thief skill and ability checks (spoilers)
python -m dsloader save C:\path\to\SAVE01.SAV   # the party stored in a save
python -m dsloader processes                     # is DOSBox found?
```

After `launch` or `play`, `--window-scale 1` to `4`, `--fullscreen` or
`--windowed` choose the game's window as **Game window** does. If more than
one DOSBox is running, add `--pid <number>` (from `processes`).

### Practising without the game

`tests/make_fake_party.py` writes `FAKEPTY.COM`, a tiny DOS
program holding two made-up characters in the same record shapes as the game.
The first character loses 1 HP every second. Run it in DOSBox and try the
Loader (search for `SADIRA`).

```
python tests/make_fake_party.py
dosbox FAKEPTY.COM
```

![The Loader on the practice program: All fields with Sadira and Rikus, and Memory tools with her record found and its bytes](docs/viewer.png)

### Mapping memory

For Shattered Lands the party is found automatically. The steps below are for
mapping new fields, or for other layouts:

1. Type a party member's name under **Locate by name** and press **Search**.
2. Select the hit that is the character's record and press **Assign**. In the
   hit list, the record shows its name followed by dots, since binary data
   follows the name. A copy in a text buffer is followed by more text. Slots
   2–4 follow automatically if the party's records sit next to each other in
   memory, as they do in save files. Otherwise assign each slot by name.
3. The **character sheet** (XP, classes, levels, saves) is found automatically:
   it carries the same ability scores and entity ID as the creature record.
4. **Save layout** (beside **Search**) stores the addresses. They may change
   when you load a save or restart the game. If a slot starts showing garbage,
   locate it again.

The **Record bytes** panel shows the raw record. Bytes that change light up
orange, and clicking a byte decodes it as u8/s8/u16/s16/u32. Use it to map
fields that aren't known yet. Watch a byte change as you take damage, spend
PSP, or equip armour, then add it to `layouts/shattered_lands.json` and press
**Reload layout**.

### Command-line mapping tools

```
python -m dsloader find-text Daaki               # hex dump around each hit
python -m dsloader dump 0x1a2c 128               # hex dump an address
python -m dsloader search u8 23 --near 0x1a2c    # Cheat-Engine-style value search
python -m dsloader next 17                       # ...narrow after the value changes
python -m dsloader next decreased                # also: changed, unchanged, increased
```

## How the dice log works

Every roll in the game goes through one function, Borland C++'s `rand()`.

1. When you start the game with the dice log, the launcher writes
   `dos\DSUNLOG.EXE`: a copy of the game's `DSUN.EXE` with a few hundred
   small changes, listed in `PATCHES` in `dsloader/gamepatch.py`. Most replace a few
   bytes of the game's code with an `INT` (60h to 65h, and 8Ch to FEh; all of
   them are taken, so later sites share one, a site number after the `INT`, as
   in [Scores and hit points as rolled](#scores-and-hit-points-as-rolled)) that
   the helper answers: `rand()`, the saving throw, AC, the dialogue window and
   message boxes for the dice log; the inventory, View Character, USE and
   Effects screens and the Look box for what the Loader adds to them; and the
   places each rule change, new item and screen addition needs. The sections
   under [How each part works](#how-each-part-works) name the patches each part
   uses. One, at the start of a monster's turn, is in overlay code the game
   moves or unloads to load the dialogue window's, so the helper puts its way
   back in a stack frame the game's overlay manager fixes up (a stale address
   used to restart a fight, or stop the game with "Stack overflow!"). A few
   patches change the game outright: 29 saved characters rather than 19, DELETE
   deleting the one chosen and a New character counting as Okay (see [more
   characters](FEATURES.md#more-characters)), Enter loading only a save that is
   there (see [more saves](FEATURES.md#more-saves)), a script buffer of 11,776
   bytes rather than 10,000 (for [Dinos and the
   Trustee](FEATURES.md#what-dinos-and-the-trustee-say-about-them)), and data
   files looked for in the current folder rather than next to the program. The
   helper also hooks DOS's `INT 21h`, to open the launcher's copies of
   `SEGOBJEX.GFF`, `RESOURCE.GFF`, `GPLDATA.GFF` and some regions' files (for
   the [new items](FEATURES.md#new-items), [Kalzith](FEATURES.md#kalzith),
   [Semyon](FEATURES.md#semyon) and [no manual
   check](README.md#no-manual-check)), and to keep what the game last wrote to
   the screen for a crash report (see [the crash report](#the-crash-report)),
   the mouse driver's `INT 33h` (for [scrolling the
   map](FEATURES.md#scrolling-the-map)) and the keyboard's `INT 16h` (for Tab
   and Enter). DOSBox runs it from the game folder, so it uses your saves as
   usual.
2. `dos\DSCLOG.EXE` (source in `dos\dsclog.asm`) is a tiny DOS program loaded
   into upper memory before the game, so the game loses no memory. It answers
   those interrupts. Its `rand()` returns exactly the numbers the original
   would and also records each call, what code called it, and that code's
   arguments (dice count and sides, THAC0, AC...) in a ring buffer. Others
   record the final saving throw total, the AC the game uses, and the text
   of dialogues and messages (in a second buffer); the rest draw the in-game
   additions and make the new items and the rule changes count.
3. The Loader finds the buffer in DOSBox's memory and reads it every 50 ms.
   It works out what each roll was for from the code that asked for it, and
   reads the rest (names, weapons, spells, effects) from the game's own data.
4. To keep bursts of unimportant randomness from crowding out the rolls that
   matter, the helper only records calls from code it knows how to label,
   unless **Show unlabelled rolls** is ticked.

Because the replacement produces identical numbers, the game plays exactly as
it would without it, apart from what you choose on the Options tab (picking
pockets, the [rule changes](FEATURES.md#rule-changes)), the Loader's other
additions (the new items and the Ring +1, the cooked vulture, Kalzith, Semyon,
what the party wears, shadows, dust, rings, Tab and Enter, scrolling) and the
fixes always in the patched copy: no equipment penalty on thief skills (see
[Thief skills](HOW-THE-GAME-WORKS.md#how-the-game-works-out-thief-skills)), the
roster's
DELETE and New characters counting as Okay (see
[More characters](FEATURES.md#more-characters)), and no manual check (see
[No manual check](README.md#no-manual-check)).

Limitations:
- Only the GOG release (`DSUN.EXE` of 611,408 bytes) is supported. With
  another version the launcher starts the game without the dice log and says
  why.
- Outside combat, the thief skill, trap and ability checks, the character
  creation rolls and searching junk, hay and wardrobes are labelled; other
  rolls there (for example treasure or random encounters) show up only with
  **Show unlabelled rolls**, as raw numbers.
- A save-file load from the main menu is recognised, so the spells already
  active in it aren't reported as new. Loading a save of the same party in the
  middle of play isn't, and its effects may be listed as if just cast.
- Dialogue speakers are portrait numbers until the log learns their names or you
  name them (see [the Dialogue tab](README.md#the-dialogue-tab)): the game
  doesn't keep a name with the dialogue. A learned name is the creature the
  conversation was started on, so a scene in which one face speaks for someone
  else would get that someone's name.
- Weapon breaking was checked against the game's code, and the check's rolls
  were seen in play, but no weapon happened to break during testing; the
  game's own "is broken !" message is logged either way.

## What is known

A save file (`SAVEnn.SAV`) is an SSI **GFF** archive. Two of its chunks hold
the party:

- **`SAVE` chunk 5, creature table.** 58-byte records (`0x3a`) for everyone in
  the current region, party first.
- **`SAVE` chunk 6, character sheets.** 71-byte records (`0x47`).

The game keeps the same records in memory, with the party's sheets one after
another. Old copies of a record can linger elsewhere in memory, so the Loader
prefers the sheet at the party's stride position. Offsets are relative to the
start of each record. The evidence comes from five save files covering three
parties, plus the in-game View Character screens.

| Record | Offset | Type | Field | Evidence |
|---|---|---|---|---|
| creature | `+0x00` | s16 | Current HP | ≤ max HP everywhere; wounded characters lower |
| creature | `+0x02` | s16 | Current PSP | ≤ max PSP everywhere |
| creature | `+0x06` | u16 | Entity ID (`0x80nn` for the party) | same value in the sheet at `+0x10` |
| creature | `+0x1a` | s8 | Base AC, before armour and DEX | 10 for humanoids, 5 for the thri-kreen; the AC the game shows is worked out from this |
| creature | `+0x1b` | u8 | Movement | 12, 15 for the thri-kreen; each round of a fight gives Move × 10 movement points |
| creature | `+0x1f` | u8 | THAC0 | matches the AD&D warrior table at levels 3, 4, 7 and 8 |
| creature | `+0x22` | u8 ×6 | STR DEX CON INT WIS CHA | same as the sheet |
| creature | `+0x28` | str 18 | Name | |
| sheet | `+0x00` | u32 | XP | matches the game |
| sheet | `+0x04` | u32 | For monsters, the XP they're worth; for the party, usually equals XP | matches the XP the party gets for a kill |
| sheet | `+0x08` | s16 | Max HP | |
| sheet | `+0x0a` | s16 | The hit points rolled (or gained) for every class level, added up | the game's level-up code (DSUN.EXE 87250h) adds each new level's to it; max HP = this ÷ the number of classes + CON's bonus |
| sheet | `+0x0c` | s16 | Max PSP | worked out at each level-up (873B2h): CON, INT and WIS bonuses, and for a psionicist +10 a level after the first, plus 1 a level for each WIS point above 15 |
| sheet | `+0x10` | u16 | Entity ID | links the sheet to its creature record |
| sheet | `+0x18` | u8 | Race: 1 Human, 2 Dwarf, 3 Elf, 4 Half-elf, 5 Half-giant, 6 Halfling, 7 Mul, 8 Thri-kreen | ability modifiers fit; 2, 6 and 7 from the character creation code's race table |
| sheet | `+0x19` | u8 | Gender: 1 male, 2 female | |
| sheet | `+0x1a` | u8 | Alignment: 1 LG, 2 LN, 3 LE, 4 NG, 5 TN, 6 NE, 7 CG, 8 CN, 9 CE | 1, 5, 7 confirmed in game |
| sheet | `+0x1b` | u8 ×6 | STR DEX CON INT WIS CHA | |
| sheet | `+0x1d` | u8 | CON (among the abilities at `+0x1b`); sets the least a level's hit point roll counts for | read by the game's level-up code |
| sheet | `+0x21` | u8 ×3 | Class: 1–4 Cleric, 5–8 Druid, 9 Fighter, 10 Gladiator, 11 Preserver, 12 Psionicist, 13–16 Ranger, 17 Thief (0 = none); each four is air, earth, fire, water | 2, 7, 8, 9, 11, 12, 13, 14, 17 confirmed in game; the elements from the spheres in the game's class and spell tables (see Spells and effects) |
| sheet | `+0x24` | u8 ×3 | Level in each class | |
| sheet | `+0x27` | s8 | Base AC for the AC calculation | read by the game's AC code |
| sheet | `+0x29` | u8 | Magic resistance (%) | read by the game's magic resistance check |
| sheet | `+0x2a` | u8 | Attacks per round × 2 | read by the game's combat code |
| sheet | `+0x37` | u8 ×5 | Saves: para/poison, rod/staff, petrify, breath, spell | match the AD&D warrior table exactly |

In memory, the game reaches both tables through far pointers in its data
segment: `DS:0x1665` points to the creature table and `DS:0x1661` to the
sheets (a creature's sheet number is its word at `+0x04`). The data segment
starts with Borland's copyright string at `DS:0x0004`, which is how the Loader
finds the party by itself (`dsloader/game.py`).

**Items.** A creature's items hang off its record at `+0x08`, `+0x0a` and
`+0x0c`: each is an object number (the object table has a kind, 1 for an item
and 2 for a creature, and an index), the first item of a list, whose own
records then name the next. A party member keeps what it wears or holds in
its `+0x0a` list and what's in its backpack in its `+0x0c` one: the inventory
screen moves an item from one to the other as it's put on or away (a new list
when there's none). The game fights with every weapon in the `+0x0a` list,
whatever the item's slot byte says: a dagger put in a backpack cell but left
in that list is a weapon in hand to the game (its inventory panel lists it,
and it attacks with it). So the Loader gives and moves the party's items
through `pickpocket.party_list` and `pickpocket.place`, and `mend_lists` puts
away backpack items an earlier version left in the worn list. (The game's own
party starts with worn armour in `+0x0c`, so worn items found there are left
alone.) Items are 21-byte records (`DS:0x165D`), item types 20-byte ones
(`DS:0x1669`, 115 of them, from GPLDATA.GFF):

| Record | Offset | Field |
|---|---|---|
| item | `+0x04` | the next item in the list (9999: the end) |
| item | `+0x08` | a container's contents (an object number), as in a Dead Body |
| item | `+0x0a` | its type |
| item | `+0x11` | where it's worn: 0-13 the game's slots (arm, ammo, missile, right hand, finger, waist, legs, head, neck, chest, left hand, finger, cloak, foot), 14-25 a backpack cell |
| item | `+0x0f` | a spell it carries, one past the spell's number (0: none): readied, the game casts a helpful one on the wearer; the acid's check reads it as the item's "magical power" |
| item | `+0x12` | its name (an entry of the game's name table, 25 bytes each) |
| item | `+0x14` | its plus |
| type | `+0x04` | weight, in tenths of a pound |
| type | `+0x08` | material in the low four bits (wood, bone, stone, obsidian, metal, leather); `0x80` spares a weapon the material's to-hit penalty |
| type | `+0x0c`, `+0x0d`, `+0x0e` | damage dice: sides, count, bonus |
| type | `+0x0f` | `0x80`: counts for AC |
| type | `+0x12` | its AC (on top of the item's plus) |

Free item records and free objects are kept in lists (`DS:0x4D76`, `DS:0x4D72`),
which is how the Loader adds [the Ring +1](FEATURES.md#new-items) and Kalzith's
scrolls as the game would.

Also seen: per-region `RGnn` chunks hold a combined creature record, sheet and
inventory for each character. Region *nn* uses `SAVE` chunks *nn*×60+1 and up
for its own copy of the region state.

The saved characters are `CHAR` chunks of `CHARSAVE.GFF`, 314 bytes each: the
creature record at `+0x0A` (its name at `+0x32`, its status at `+0x26`), the
sheet at `+0x4E`, then its items. The game's own party, which START GAME uses
when no party has been made (Cermak, Cilla, Gerakis and K'ratchek), is objects
300, 307, 308 and 313 in `SEGOBJEX.GFF`: a creature record and a sheet each,
already Okay, with no items. The game gives them their gear as the game
starts (see [the game's own party](#the-games-own-party)).

**Spells.** They are numbered 0 to 137: 0 to 68 wizard spells (0 is Armor, the
first of the 1st level; its scroll is Old One-Eye's), 69 to 137 priest
spells, a 7-byte record each from 0 (its level first, its name's DS offset at
+5). What the party knows is a table of 138 bytes for each member, 1 for a
spell known, through the far pointer at `DS:0x132A` (in a save, `SAVE` chunk
19).

## Room in the helper

DSCLOG keeps its code and data in one 64 KB segment, all reached through CS.
Its big buffers are kept apart, in its **far block** (`FAR_SEG`, the header's
+142), at fixed offsets from `FAR_RING` (10h) to `FAR_END`: the dice log's ring
(`NENT` 63 entries of `ESIZE` 192 bytes), the panel's picture, the shadows'
cache, the text buffer, the shadows' spans and each thing's place as last seen
(for the dust), 57,800 bytes. `FAR_INIT` (install code) puts it in the **HMA**
(FFFFh:0010h, A20 on): XMS gives it (function 01h), or, where XMS says there
is none (DOSBox 0.74's answer, 90h: its XMS blocks start at 1 MB + 64 KB,
`XMS_START`), it is used if all zero; A20 is turned on with XMS function 03h
and checked (FFFFh:0010h no longer 0000h:0000h). The game never calls XMS's
A20 or HMA functions (its XMS calls are 08h-0Dh), and no file DOSBox runs is
EXEPACKed (the unpacker fails with A20 on below 64 KB). Without the HMA the
block is a memory block of its own (upper memory, else conventional),
`FAR_SEG` a paragraph below it so that its offsets are the same. The header
gives the Loader each buffer's segment and offset: the ring's `ring_seg`
(+268) and `ring_off` (+16), the text buffer's `tbuf_seg` (+138) and
`tbuf_off` (+128), the panel's `panel_seg` (+328) and `panel_off` (+140). The
helper reaches the internal ones through FS, pushed and set around each use
(the game never sees it changed). The text buffer (`TSIZE`) is 2 KB; the
Loader reads its size from the header and drains it every 20 ms (at most 251
bytes came in between two reads in the opening show, the busiest stretch
measured).

The helper has to load into upper memory, or the game loses 62 KB of
conventional memory (570 KB free rather than 632 KB).

**Where DOSBox's memory is** (DOSBox 0.74, GOG's; its source comes with the
game, `DOSBOX/dosbox-0.74-2.1.tar.gz`):

| Memory | Size | What uses it |
|---|---|---|
| Conventional (0-9FFFh) | 640 KB | DOS and the shell 8 KB; the game the rest: 97 KB free with the map open (it needs 60,000 bytes in one piece to open it again) |
| C000h-C7FFh | 32 KB | the video BIOS (ROM) |
| C800h-C8FFh | 4 KB | DOSBox's own tables (`DOS_PRIVATE_SEGMENT`, handed out from C800h up: to C8C0h with the game running) |
| C900h-EFFFh | 156 KB | upper memory, with `UMBPLUS.COM` (else D000h-EFFFh, 128 KB): the helper 60 KB, the game's overlay buffer 32 KB, the game's music buffer 12 KB, about 55.5 KB free in one piece |
| F000h-FFFFh | 64 KB | the BIOS (ROM) |
| 1 MB-1 MB+64 KB | 64 KB | the HMA (A20 on): the helper's far block, 57 KB (the ring, the panel's picture, the shadows' cache, the text buffer, spans, the dust's places, the frames steady pace holds back), 6.9 KB free |
| above | 31 MB (`memsize=32`) | XMS: the game's memory layer (VMEM) |

DOSBox makes its upper memory block at D000h, but C800h-CFFFh is RAM too, and
DOSBox's tables use only its first 192 paragraphs (at most a few more later: a
program asking for more than 20 file handles, INT 21h AH=67h, takes some each
time; the game does once, at DSUN.EXE 54F3h). `UMBPLUS.COM`, run by the
launcher's config just before `lh d:\dsclog.exe`, moves the block's start to
C900h: the system MCB at 9FFFh (owner 8, "SC") is cut to end there and a free
block's MCB goes at C900h, reaching F000h as before. It does so only if the
chain is exactly DOSBox 0.74's (9FFFh 'M' to D000h, D000h 'Z' free to F000h)
and C900h-CFFFh is all zero and keeps what is written to it; otherwise it
changes nothing and the helper loads at D00Ah as before. 63 paragraphs stay
between DOSBox's tables and the block. Measured with the user's arena save
(walking, the arena's fight): the tables at C8C0h throughout, the helper at
C90Ah, the overlay buffer in upper memory, 29.1 KB free in one piece.

The helper still has to fit D000h-EFFFh (`UMB_ROOM`, below), so it works
where the block can't be moved; the 28 KB more holds what it can do without:
the shadows' cache ([Shadows](#shadows)) and the game's music buffer.

**The game's blocks kept for good.** Of the game's far heap (Borland's,
farmalloc at load:1231h, farfree 1127h, farrealloc 138Eh), 134 KB is taken
before the main menu and kept in place through loading a save, walking, an area
change and a fight, logged by a research build of the helper with those three
functions hooked: the music buffer (12,001 bytes: an XMIDI file), the sound
effects' (24,001: a Creative Voice File), both asked for by the sound driver's
set-up in an overlay; tables of 10,724, 4,963 and 11,778 bytes; the font and
other resources loaded as the menu comes up. Nearly every request goes through
the game's wrapper at 34FA4h (farmalloc of the size + 1, a guard byte 77h at the
block's end, which its farfree wrapper at 34F3Ch checks), and its callers are
mostly overlays (running in upper memory, so not to be patched by address).
So `PROBE_HEAP` (INT CBh in place of each function's "push bp / mov bp,sp")
takes them by size: `farmalloc(12001)` is given `POOL_SEG`, a block KEEP took in
upper memory, with a heap block's first word (its paragraphs, which the wrapper
reads for the guard byte); farfree of it marks it free for the next such
request; farrealloc of it keeps it if the size fits, else moves the contents to
a block of the heap. Nothing else changes. The music buffer was chosen as it fits
with the shadows' cache (the sound effects' 24 KB would leave the cache 6 KB):
with the map open the game has 97 KB spare, not 85 KB. Measured with the user's
arena save: the buffer in upper memory holding the XMIDI file, walking, the
arena's area change and a fight as usual.

With GOG's settings there
is one upper memory block of 63 KB, EMS's 64 KB page frame taking the rest; the
launcher's config turns EMS off (`launch.DOS_LINES`: the game uses XMS instead),
which leaves the helper a second 64 KB block (65 KB free with it loaded; see
[the combat log](#what-the-game-allows)). The helper's own segment is still at
most 64 KB (everything through CS), so the second block is room for data kept
apart from it. The helper asks for its image and the install's stack
(`LOAD_EXTRA`); with EMS on, `mem` in DOSBox showed 632 KB free and a few
KB of upper memory left. A change that adds much code should check that again:
the ring is 63 entries, not 128 (96 until the new spells' code, when the game no
longer started for lack of memory; 88 until STORE and RECALL; 84 until spells
199-201 and `seg_space`, when the helper no longer fitted in the block and
loaded low; 74 until the names over figures; 66 until Whirlwind's funnel turned;
65 until Wall of Thorns counted a monster's armour, 64 until the pointer kept its place), and the text buffer 2 KB,
not 8 (4 until the memory pass for 6th-level spells), to make that room. The
most entries put in the ring in 2 seconds, measured, is 43 (the opening show),
16 in a fight.

The second block also holds the game's overlay buffer (32,992 bytes: twice the
largest overlay, the code the overlay manager loads as needed). The game asks
farmalloc for it at startup (load+3653h:0D5Ch) and keeps it for good, so in
the heap it was the largest block the 640 KB never got back. The patch
`overlay_umb` makes that call `INT VEC_OVR_BUF` (`PROBE_OVR_BUF`), which hands
over a block `KEEP` reserved: `KEEP` (resident code) first cuts the helper's
own block down to what stays, then takes the buffer's block in the memory the
install code had, so the room is in one piece: the helper, the buffer and what
is left free.
The header's `ovr_given` (+368) is the buffer's segment once the game has it.
Without the room the probe calls the game's farmalloc, as the call was. With
the map open this left 86 KB free in conventional memory (85 KB measured again
with the 6th-level spells, the largest piece 87,744 bytes; 97 KB with the music
buffer in upper memory too, below), against 53 KB (and
the unmodded game's 57 KB): the map's view takes 60,000 bytes in one piece
each time it opens ("Out of memory in OEOpenGraph" when it can't). What it
puts there (`UMB_NEED`, the header's +372) is checked against the room
(`UMB_ROOM`, D00Ah to F000h): the build fails past it (a negative `times`),
and so does `test_fits_upper_memory`. Since the far block went to the HMA,
2,303 paragraphs (36 KB) are spare in it, and with `UMBPLUS.COM` about 55.5 KB
are free in one piece (57.8 KB measured in DOSBox with a smaller helper, less
what it has grown since: the helper at C90Ah, then the overlay buffer, the
free block, the music buffer). The helper's own segment is the limit for new
code: its image with the install code is 61,040 bytes (`image_len`; the
resident part ends at `resident_end`, E790h), so about 4.4 KB of its 64 KB are
spare; the HMA has 7,080 bytes left for more buffers (the far block ends at
`FAR_END`, 58,456). (Before this pass the segment had about 2 KB and upper
memory 0.5 KB: the right button's scrolling, the rings under every enemy and
the strip below the map had been taken out, and the freeze report cut to 16
records, to make room.) The game's sound-effects buffer (24,001 bytes, kept
for good like the music's) could go to upper memory next for the game's 640
KB, but the sound driver may play it by DMA, which can't cross a 64 KB page. Text the game reads from RESOURCE.GFF belongs in the Loader's
copy of it, not in the helper (`spelltexts.py`: the descriptions moved there
freed 1.6 KB), and so does data read from the player's game (the pointer's
picture, `POINTER.BIN`). If the buffer still ends up in the heap (another
DOSBox, less upper memory), the Loader says so in the dice log once, and crash
reports say where it is (`heapcheck.py`). With EMS on,
GOG's own setting, the helper itself no longer fits upper memory (it loads in
the 640 KB and the game won't start); it didn't before the buffer moved either,
and the launcher's config turns EMS off.

While the game runs, the Loader reads its memory every few seconds
(`heapcheck.Watch`): with the map's view open (DS:1F82h set), below 24 KB
spare (DOS's after the game and the heap's free blocks) the dice log says to
save and restart soon, once until it has been back above 32 KB. Nothing can
be given back to the game from outside: every block is its own.

## The crash report

GAMEEND.COM only reads what is left on the screen, and the game's own fatal
errors (its memory manager's "ABEND: VM...Heap() returned error N", its script
engine's "Mel Fatal Error #: N Trap #: N") are printed while the screen is in
graphics, then cleared as the game puts it back in text mode on its way out.
So DSCLOG keeps the last 256 bytes the game writes to handles 1 and 2 (INT 21h
AH=40h: `DOS_WRITE`). At the first non-zero exit (AH=4Ch: `DOS_QUIT`), it writes
them to `D:\GAMEMSG.BIN`, with the code, the load segment and 256 bytes of the
stack. `launch.game_message` turns that into the crash report's lines: the
text, then the stack's likely far returns as places in DSUN.EXE.

A game that ends as usual has GAMEEND.COM write an empty `D:\GAMEOK.TXT`. The
Loader removes it (with `GAMEEND.TXT` and `GAMEMSG.BIN`) as it starts DOSBox:
DOSBox closing with no error noted and no `GAMEOK.TXT` means the game was cut
off while it ran (`launch.CUT_OFF`), and that is a crash report too.

## The freeze report

The game's timer handler (IRQ 0, DSUN.EXE 3925Ch, the game's own from its
start; its timers run from it, 120 strikes a second) begins with `INT VEC_TICK`
(`PROBE_TICK`). Every 32nd strike (about 4 a second) DSCLOG notes what the
timer interrupted: CS:IP, flags, SS:SP before the interrupt, BP, DS and ES, in
`TICKS` (16 records of 16 bytes, the last 4 seconds; the header's +356 its
offset, +358 the records taken). The Loader's
**Freeze report** (`freeze.py`) reads them newest first, names each place
(DSCLOG's, the BIOS's, or the game's segment and DSUN.EXE offset, which overlaid
code doesn't keep), shows the code there now and the newest stack, counts the
notes and the map's main loop for a second, and zips that with the memory below
1 MB + 64 KB. The handler itself loops forever on `INT 3` if the word at its
CS:1B2h is no longer "Test" (its check for memory written over), so notes all
at 33A5:04D9h to 04DBh (load-segment relative) point there.

## Reading the game's memory

DOSBox keeps the emulated PC's RAM in one block of its own process memory. The
tool finds that block by looking for the BIOS date string DOSBox writes at
guest address `0xFFFF5` ("01/01/92"), and checks it against the interrupt
table at guest address 0. After that, reading the game's memory is a plain
`ReadProcessMemory` at `block + guest address`. Dark Sun is a 16-bit real-mode
program, so a `segment:offset` address is simply `segment × 16 + offset` in
guest memory. If detection fails on an unusual DOSBox build, you can pass the
block's host address with `--host-base`.

### Changing the game's item lists

The game rebuilds its item lists as an area loads (and at START GAME): it writes
the area it leaves out, reads the next one in, and gives the party's items new
records, every one a new number (seen: 70 items of 70 renumbered at each change
between the pens and the arena). Its free lists of item records and of things
(`DS:4D76h`, `DS:4D72h`, the count in use at `DS:4C48h`) move as it does. A
change of the Loader's made across that, from numbers read before it, would land
on records that aren't what they were: a free record the game hands out too, or
a list linked through an item that is now another's. An item cut out of its list
that way is gone without a trace.

So every write of the Loader's to the item lists goes through one gate
(`itemgate.py`). `GuestMemory.write` asks `ItemGate.covers` whether a write
touches them: the free lists' heads, the item table (400 records of 21 bytes
from the far pointer at `DS:165Dh`), the things table, or a creature's list
heads (`CREATURE_ITEM_LISTS`). Each pass of the dice log (`DiceLog.lines`)
begins the gate first, noting the heads, the region (`DS:117Ch`) and the item
and creature tables' pointers. The pass's first such write waits until
`itemgate.WAIT` (60 ms) has gone by since then, pauses DOSBox
(`ProcessMemory.suspend`: SIGSTOP on Linux, waiting until each thread shows
stopped, about 1.5 ms; `NtSuspendProcess` on Windows), and reads the same
things again. All as they were: the writes go ahead with the game held still,
until the block ends (`itemgate.release`) or the pass does. Anything changed:
`ItemsBusy` (a `ValueError`), none of the pass's item writes are made, and the
next pass tries again. A process that can't be paused gets the same look with
the writes right after it. A write outside a pass (a tool's) has the lists
looked at over the wait first, without pausing. The Loader lets the game go if
it exits mid-pass (`atexit`).

Whatever can't be done twice takes the gate before it starts (`itemgate.hold`),
so a refusal leaves nothing half done: Pick Pockets before its d100 (the request
stays unanswered until a later pass), a defiler's scroll before its roll (the
defiler isn't marked rolled for), Kalzith's loot before `LOOTED`, and the arena
ring before the search counts as answered. A sold item's place in the buyback
queue moves on only once it is kept, and the game's own party's steps are marked
done only once made.

The item watch (`itemwatch.py`, the README's [Crash, freeze and item
reports](README.md#crash-freeze-and-item-reports)) reads the same lists once a
second and has to see past the renumbering too. Over half the party's items gone
at once (and at least `MOST_GONE`) is a bulk change: it waits until the new
numbers hold still at two looks, then matches old items with new by owner, slot
and what the item is (`_same`: its picture, type, name and plus), falling back
to owner and item. At least `BULK_MATCH` (half) matched is a change of area, and
an item with no match is reported; fewer, or no settling within `BULK_WAIT` (30
s), is a game loaded, and the watch starts afresh. An item gone whose record
still holds its type and name is outside the party (dropped, in a container) and
not reported, unless the record's first word went to 0 (`freed`): the game's
free (1A0A:0A3Ah) zeroes only that word and the free-list link at +4, so a
destroyed item keeps its type and name.

Every place the game deletes an item goes through A0:1CD6h. Its ten callers:

| Caller (DSUN.EXE) | When | The watch |
|---|---|---|
| 58D61h, the "use up one" routine, from 58C8Fh | an arrow shot (the last of a stack) | arrows are ordinary (62) |
| 58D61h, from 7AAEBh | Detonate's blast on a worn piece | reported |
| 7AA5Ah, 7ABC4h (from 79186h) | acid and corroding touch on a weapon or armour | reported |
| 73F36h, from 72206h | a wand's last charge (+0Eh down to 0) | wands are ordinary (70-73) |
| 73F36h, from 8B2B0h | an item used up from the USE screen | fruit, scrolls are ordinary |
| 6B143h (by 6B0CDh, 6B121h) | script TAKE (5Ch) to no one; and the effects (7872Fh, 79186h) taking the items spells make | quest types and spell items ordinary; anything else reported |
| 6A894h (by 6A720h) | script DROP (2Fh): the item becomes a thing on the map | reported, unless the whole party's drop (a bulk change) |
| 671C8h | a new character's starting gear that won't fit | (before the watch has seen it) |
| 67401h (40 bytes on) | a new character's worn items cleared | (before the watch has seen it) |
| 67401h (675B4h), from creation and DUAL (86C80h) | a piece the new class can't use, pack full: the item held on the pointer is deleted unless the inventory is open (read from the code, not seen) | reported |
| 7C7ACh, in the effects overlay | none found (no call reaches it) | — |

## How each part works

For each part of the README and the features page, how it's done: where the
patched game calls the helper (DSCLOG), and what the Loader reads and writes.
The heading names the page's section.

### The Dialogue tab

([In the README](README.md#the-dialogue-tab).)

The game keeps the clicked reply's row at DS:1F0A while it flashes it; the log
reads the reply's text from the game's own list.

### Searching junk, hay and wardrobes

([In How the game
works](HOW-THE-GAME-WORKS.md#searching-junk-hay-and-wardrobes).)

How: the scripts' random command has a routine of its own in the game; the
patched game has DSCLOG look in there (`INT D3h`), which records the roll, its
range, where the running script is (which tells the three searches and their
damage rolls apart) and the three counts (`dsloader/searches.py`). Tested in
play: a haystack search in the slave pens logged
`0-10 = 7, an old, soiled loincloth (the party's 2nd find of 6 in hay)`, as
the game's own message said.

### The Bowyer's archery target

Shooting at the target in Teaquetzl runs script 178 (with a bow in hand: the
script counts objects 1017, 1039 and 30007, the bow, the Bow +2 and Phrain's
Bow, into variables 1 to 3, added up at 40Dh; the Loader's copy jumps from
there to code added at the script's end, which counts Dunesong, 2594, into
variable 5, adds the four and jumps back to 41Ah, so nothing in the script
moves: `bowyer.with_dunesong`): its distance command (80h)
gives the archer's distance from the target (object 1314) in squares, as the
game's distance routine (DSUN.EXE DD8Ch) counts them: the least n, from its
estimate, with n * n + n at least dx * dx + dy * dy (map squares, the map
things' 16ths of a square at DS:669Dh shifted by 4). Under 5 is a bull's eye
with no roll; otherwise a random 0-20 under DEX - distance / 2 (2 if DEX is under
the distance) hits, under by 10 or more is the centre, which from more than 13
squares with the Bowyer (object 283) within 25 gives 6 Arrows +2, once (flag
642). `dsloader/bowyer.py` writes the shot's line from the random command
PROBE_SCRIPT_RAND records (position 57Fh, script 178's alone), the archer the one
whose turn it is, the distances worked out the same way from where they stand.

### Ability checks in the scripts' conditions

Some scripts test an ability without the ability check command: a condition
compares the random command with a field of the character acting (fields 23 to
28, STR to CHA), as Chahl's `random(19) <= CHA` when asked about his scars
(script 181), the chains a strong character breaks (76) or a secret door an
intelligent one spots (69, `INT - 10`). `dsloader/scriptchecks.py` finds every
such condition in the Loader's copy of GPLDATA.GFF (13 of them) by the position
DSCLOG records past its random command (as the searches are told apart; a
position two scripts share is left out), and the dice log evaluates the
condition with the roll and the score of whoever's turn it is (outside a fight
the leader, the character acting): `Daaki CHA check: 0-19 = 15, always made
(CHA 20) -> success`. Which way the condition goes is the one the ability
favours (the score 25 with the lowest roll). Tested in play with Chahl.

### The combat log in the game

([In the README](README.md#the-combat-log-in-the-game).)

#### What the game allows

What was measured before the panel was built (Stage 0 of
[the design brief](docs/combat-log/HANDOFF.md)), with the patched game and the
dice log running:

- **Pages.** The game keeps a table of pages at `0980:0004` (DSUN.EXE
  segments, less the load segment; the shadows read it): each page's memory
  segment (`+4`; a child page, flag `40h` at `+C04h`, names its parent there),
  its bounds (`+404h` x0, `+604h` y0, `+804h` x1, `+A04h` y1). Pages 0 and 1
  are the two screens (`A400h` and `A000h`, 320 x 200 in mode X); the others
  are windows over them and buffers in the rest of video memory (`A7E8h`, a
  third 320 x 200; smaller ones to `AE55h`).
- **The flip.** The routine at `0980:5814` (DSUN.EXE 14414h) shows one screen
  or the other (the CRTC start address; `0980:118E` says which, 1 for `A400h`)
  and swaps them for −1. It is called from 45 places, all in overlays, for
  screens and windows: in five seconds of walking on the map the page shown
  changed three times, on opening and closing windows.
- **The map draws into the screen shown.** The view's floor, walls and
  figures go straight into `A400h`, the screen on show (the shadows' `v_seg`
  read live), a rectangle at a time as things move (`PROBE_REDRAW` 2475Fh,
  `PROBE_REDRAW_ALL` 24B18h, the floor routines 2700Eh and 27162h). So there is
  no last moment of a frame on the map: a panel over the view has to be drawn
  again after each of those redraws that overlaps it (their way back, as
  `FLOOR_POST` does for the floor), or the figures walking under it would
  wipe it (the panel is: see below).
- **Keys.** On the map End and PgUp scroll the view (16 pixels down-left and
  up-right: the numeric keypad's diagonals; PgDn and Home likely too, at the
  map's edge here), so they stay the game's; L did nothing on the map, and is
  the panel's.
- **Font.** The game's text font is RESOURCE.GFF's FONT 100, 9 pixels high
  with its shadow (`art.py`): a panel 67 pixels high holds a header and 6
  lines.
- **Memory.** With GOG's settings (`ems=true`) DOSBox keeps EMS's 64 KB page
  frame where upper memory would be, and with the helper loaded `mem` shows 1
  KB of upper memory free. With `ems=false` (the launcher's own config, after
  GOG's) it shows 65 KB (largest block 64 KB), conventional memory unchanged
  at 632 KB, and the panel has its room (see
  [Room in the helper](#room-in-the-helper)). The game's memory layer (VMEM)
  takes EMS, XMS or extended memory, whichever there is: without EMS it loaded
  a save, walked the pens, opened a conversation and a shop, and played the
  arena's opening fight to the end without a fault (a check, not a whole
  game).

#### The panel

- **Where it lives.** The Loader draws the panel's picture (`combatlog.py`:
  180 × 78 palette indices in the area's own colours, matched to the palette
  DSCLOG last read) into an upper memory block DSCLOG takes for it at install
  (`panel_seg`, header `+328`); the dice log's ring has a block of its own
  there too. With EMS on there is no such block and no panel.
- **Putting it on screen.** DSCLOG copies the picture into the screen on show,
  a plane at a time (`PANEL_BLIT`, its height kept on the screen; the Loader
  stores each row as its four planes' bytes in turn, `combatlog.planar`, so a
  plane's part of a row is copied whole with `REP MOVSW`), from the main loop
  (`PANEL_TICK`, in `PROBE_SCROLL`) when the floor has been drawn since or the
  Loader has a new picture (`panel_new`, `+330`).
- **Kept whole.** The game draws what moves a rectangle at a time, through one
  routine (2475Fh, 1DF3:142F: a window page the rectangle's size, the floor,
  walls and figures drawn into it) or the same steps inline in the routine
  drawing again all that moved (from 24B18h). A rectangle over the panel,
  while it is on screen, is drawn as its parts round it instead (`CLIP_CHECK`,
  `REDRAW_PARTS`: above, below, left and right, through 2475Fh, `RP_BUSY`
  letting them by), so nothing the game draws there covers it: the routine
  itself is left out (its caller's way back kept in a frame of its own shape,
  for the overlay manager), and the inline one goes on at its end (24C65h).
  With the routine's last argument the screens are flipped and the rectangle
  copied to the other, so the panel is put on the screen not shown first
  (`PANEL_DRAW_OTHER`). Measured in the arena's fight, playing turns: before,
  the map showed through the panel in every frame grabbed (300), up to 7,000
  of its pixels; after, in none. What still reaches it is the view drawn whole
  (a scroll, centring on whose turn it is), put back on the next pass of the
  main loop. The game's own scrolling (at the screen's edge, following who
  walks) copies the screen as it is, the panel too, and draws only what comes
  into view, which left copies of the panel on the map; so when `PANEL_TICK`
  finds the view moved since its last pass (`CAM_X`, `CAM_Y` against
  `panel_cx`, `panel_cy`), it has the view drawn again whole (`VIEW_AGAIN`),
  round the panel, and then puts the panel. The inline routine's way back
  (`RESUME`, which the floor's and the rectangle routine's probes also use,
  and which the parts come through) is kept on the stack while the parts are
  drawn: overwritten, the game went on from the wrong place and wrote over its
  own memory until it quit.
- **Flips.** Much of what the game draws in a fight (a step of an attack, a spell's effect, the
  view drawn whole) goes into the screen not on show, and then the screens are flipped
  (0980:5814, DSUN.EXE 14414h). The panel is drawn into the screen on show, so each such flip
  showed the map without it until `PANEL_TICK`'s next pass: a frame or two, longer in a monster's
  turn (the main loop doesn't run while the game shows an attack or a spell). Measured in the
  arena's fight, frames grabbed at about 43 a second for 40 seconds, the frames with no game
  window up but no panel either: 19 runs before (up to half a second); with `FLIP_PANEL` in the
  rectangle routines' probes (a rectangle away from the panel, with the flag to flip: the panel
  put on the other screen first, as `REDRAW_PARTS` does for one over it) 10; with `FLIP_SITE` as
  well (`INT 98h` and its site number over "mov ax,0A000h / cmp word [118Eh],0" in the flip,
  14444h, where the screen to show is set and the VGA not yet told: the panel put on it if it is
  on the screen shown now, and that counted as its page) none but the frame or two after a
  message closes (the view drawn again without the panel; back at the next pass). A game window
  is never drawn over: on the map with one up (a message, a figure's menu, EXIT GAME, the game
  menu) `SCREEN_IS` is 2, and the panel waits, as before, until it closes.
  With `FLIP_SITE`, a rectangle over the panel that is to be flipped to (the flag, into page 1,
  the screen not on show) is drawn whole, not in parts: the panel is put on that screen at the
  flip, before it shows, and the routine's copy to the other screen takes it along. In parts each
  part was drawn with the flag, so each was a flip of its own (the pointer taken off and put back,
  and a wait for the monitor's refresh, `PROBE_FLIP`): a monster's turn with the panel up flipped
  about 25 times instead of 15 and took 1.03 seconds on average against 0.89 without it. Drawing
  the parts but the last without the flag, and then again into the other screen, flipped once but
  drew the map and figures twice, and was slower still (1.29 seconds). Drawn whole, measured the
  same way (playing the arena fight for three minutes, the panel shown and hidden by turns of a
  minute): 0.95 seconds against 0.83 (turns vary by a third of a second either way: no difference
  to be told), the screens flipped as often either way, and the animation's flips 38 ms apart
  against 36 (the panel put at each). With K'ratchek's Whirlwind turning (by turns of 20
  seconds): 42 ms against 41, a monster's turn 1.01 seconds against 1.00.
- **The pointer.** The game draws its pointer into the screen on show itself:
  28D1:093D keeps what is under it (from page `[A05Dh]`, the map without the
  panel) and draws it; 28D1:0B7F puts what it kept back, so taking the pointer
  off over the panel leaves a patch of map. `PROBE_POINTER` (the stack check
  at the start of 093D, 2EA55h) puts the panel first when the pointer is to be
  drawn over it, or was last drawn over it (`[A137h]`, `[A13Fh]`;
  `POINTER_MOST`, 32, the box). `PANEL_DRAW_POINTER` puts the panel and then
  calls 093D, without taking the pointer off. `PANEL_TICK`'s refresh with the
  panel unchanged (at most once a BIOS tick), is `PANEL_DRAW_AROUND`: the
  panel without the pointer's box (`PB_SKIP` in `PANEL_BLIT`), so the pointer
  stays on screen.
- **On and off.** The Loader sets `panel_on` (`+326`) in a fight with the
  switch on; off, or the Loader silent for 5 seconds (`stats_stamp`, which it
  writes about once a second), DSCLOG has the view drawn again without it.
- **The game's windows.** A figure's menu, a question or EXIT GAME are shown
  on the other screen, the view drawn there again first: the panel is not on
  it, and is back when the window closes. Full screens (USE, View Character)
  stop the main loop, and `PANEL_LIVE` counts the panel as on screen only on
  the map (`ON_MAP`: the game's `DS:0BC9h`, `SCREEN_IS`, is 1 on the map, 2
  with a character's screen or a talk over it, 0 on the title, the menus and in
  character creation; the game's DS is learnt in `PROBE_POINTER`): else the hooks that draw the view round the panel
  and keep its clicks from the game drew a full screen round it too, the panel
  left over it and the clicks there lost. (Drawing it into both
  screens doesn't work: the game keeps other pictures in the one not shown.)
- **The lines (Stage 2).** The Loader keeps the fight's dice log lines
  (`combatlog.Log`, the last 200, from the moment it sees a fight to 5 seconds
  after) and draws them into the picture: a header line (`round_status`: the
  round, who is acting, who is next), then the last 6 rows of the well. Each
  line's level (`shorten`) is worked out from the log's own wording (the
  attack, save, magic resistance, damage and d100 patterns), an attack's
  damage put on its line; its kind (`line_kind`, the Loader's colours) from
  the full line; whose line from the name it starts with (a filled pip for
  the party, hollow for a monster). The game's font comes from RESOURCE.GFF
  (`art.Font`); without it the panel has no lines. A new picture is written
  only when something in it changes.
- **Scrolling (Stage 3).** DSCLOG's mouse handler (`PANEL_MOUSE`, in
  `MOUSE_EVENT`) notes where the pointer is (header `+332`, game pixels, as
  the driver gives them), and a left press on the panel, while the page on
  show is the one the panel was last drawn into (not under a game window), is
  counted with where it was (`+338` on) and kept from the game with its
  release, `+336` set while it is held. The Loader (`Panel.mouse`, each pass
  of the log) makes it a drag of the handle, a page, or a click on the
  **Latest** chip; the mouse wheel comes from a Windows low-level mouse hook
  (`wheel.py`, its own thread), counted only with DOSBox's window in front
  and the pointer over the panel. Scrolled back, the top row stays put
  (`Panel.first`; `None` follows the newest).
- **Drawn again.** Besides the floor and the redrawn rectangles, the game
  draws parts of the view in a fight as the pointer moves over it (what it is
  over), through routines not hooked: `PANEL_TICK` puts the panel again when
  the pointer has moved, and anyway (round the pointer: see **The
  pointer**), at most once a BIOS tick (`PANEL_TICKS`; counted in passes of
  the main loop, it was most of what the game's CPU did with the pointer
  moving).
- **Sizes (Stage 4).** The Loader sets the panel's top and height (`+344`,
  `+346`, before `PANEL_NEW`; the picture's block is PANEL_W x 130, the most);
  its foot stays at row 198. Smaller than it was, DSCLOG draws the view again
  under it first. Collapsed is 15 rows (the newest line in the header), docked
  78, expanded 130 (11 lines and the filters' row). The header's level chip
  and - / + buttons, and the filters, are pressed through `PANEL_MOUSE` as the
  scrollbar is. **L** (`INT 16h`, `our_key`, while the panel is on screen:
  `PANEL_LIVE`) is counted at `+348` and kept from the game; the keyboard hook
  is on while the panel is shown, not only with Tab targeting. With the panel
  hidden, L is counted too (`L_ON_MAP`) while the map's main loop has run in
  the last BIOS tick or two (`MAP_TICK`: no game window, menu or save name
  waiting on keys, where L is the game's) and the Loader is there. The Loader
  shows the panel while `Panel.open` (saved as `combat_log_open`, off at
  first): L with it hidden shows it, L or the header's **L** button
  (`combatlog.key_rect`) with it shown hides it, in a fight or out of one. Out
  of fights the log takes the lines with a roll in them
  (`Log.add(rolls_only=True)`). The level and size are saved in the settings
  (`combat_log_level`, `combat_log_size`). Between fights in the slave pens and
  the arena (regions 29h and 2Ah, `combatlog.ARENA_REGIONS`) the header says the
  arena's count of fights (`arena_line`, docked or expanded; it once had a
  button, A, dropped as the game's A key turns animations on and off):
  the game's global number 12 (`GameData.number(ARENA_FIGHTS)`, a word at the
  far pointer `NUMBERS_PTR`, DS:1356h; scripts' 07h/87h variables), which
  script 3 adds one to when the party walks out of the arena after a call.
- **Not checked mid-fight:** saving and loading, and area changes, as the game
  allows neither in a fight. DOSBox's window size doesn't matter (it is drawn
  into the game's screen).

### Names over figures

([In the README](README.md#names-over-figures).)

- **What starts one.** A spell's cast: `CAST_SITE` (INT 98h and its site
  number over `mov cx,[bp+6]` at 772AAh, the start of the routine at 772A5h
  that casts a spell or a power, the game's `598:89h`: `[BP+6]` the caster's
  combatant, `[BP+8]` the target's, `[BP+0Ah]` the spell) records an entry of
  kind 8, `KIND_CAST`, with the spell as its value. Every cast goes through it:
  the party's from the USE screen or a click, the monsters', a weapon's or a
  spell arrow's on a hit. The dice log floats the spell's name over the caster
  (`dicelog._float`), and "Miss" over the target of an attack whose roll
  missed. A combatant's number is its map thing's (the game's table of
  combatants, `3972:0C36h`, has one entry a thing).
- **The Loader's side** (`labels.py`). Each label is drawn in the game's font,
  its ink with a dark edge a pixel round it (the colours nearest gold or
  light grey and near black in the palette DSCLOG last read), as two one-bit
  masks of 16 bytes a row (128 pixels; longer names shortened word by word,
  then cut) and 11 rows. They go into one of four slots in the header (`+374`,
  `LBL_SIZE` 360 bytes each: the label's number, width, height, how far above
  the feet, the two colours, the map thing, the masks), the number written
  0 first and last of all, so DSCLOG never takes a half-written one. A label
  stays 1.5 seconds, a charge used 3 (`CHARGE_FOR`); a new one takes the slot
  of one over the same figure, else a free one, else the oldest, but a "Miss"
  or spell's name never takes a charge's (its priority).
- **DSCLOG's side** (`LABEL_*`). The map is drawn straight into the screen on
  show, and figures are drawn again as they move, swing and take damage, by
  routines that weren't all hooked in the first trial (a label over melee was
  whole in only a third of the frames). So the labels are put again from the
  game's timer: `PROBE_TICK` (about 120 strikes a second) calls `LABEL_STAMP`
  every other strike. It writes only (no reads of video memory, so the VGA's
  latches are left alone), keeps the VGA's registers as the shadows do
  (`VGA_SAVE`), finds the screen on show from where the VGA starts it (CRTC
  0Ch, the high byte the game's page flip sets: A000h or A400h), stays off the combat log's panel, and
  does nothing while the game's busy flag for it is up or off the map. It
  also places a new label (`LABEL_WHERE`: centred over the thing's feet, its
  bottom `UP` rows above them, under the feet if it would reach the game's
  boxes at the top, row 40, and kept on the screen), as the main loop doesn't
  run while the game shows an attack or a spell.
- **The main loop** (`LABEL_TICK`, after `PANEL_TICK` in `PROBE_SCROLL`)
  places labels too, and has where one was drawn again when it goes, moves or
  changes (`LABEL_ERASE`: the game's routine for a rectangle of the view,
  `1DF3:142Fh`, with page 1 and a flip, as its own call at 28185h; page 0
  without one drew to the screen not shown and left the label). When the view
  has scrolled, the game's scrolling has copied any label with it, so all are
  taken off and the view drawn again whole (`VIEW_AGAIN`); the timer doesn't
  put labels while the view isn't where the main loop last saw it.
- **Memory.** The first two slots and the code cost about 1.5 KB of the helper's
  upper memory (the ring went from 74 entries to 66 for it); the other two,
  720 bytes, fit in the room left.
- **Measured** in DOSBox, a fight in the slave pens with every attack made to
  miss, a slot watcher grabbing the screen as each label came: "Miss" was in
  every one of nine grabs half a second in, through swings and damage
  bursts; a cast from the USE screen showed its name once the map was back.

### THAC0, saves and thief skills

([In the README](README.md#thac0-saves-and-thief-skills).)

How: the patched game calls the helper (`INT 65h`) just after the panel's
weapon lines; the helper prints the lines with the game's own text routine,
whose address, like the selected character, it reads from the game's code
around the patch (overlays move, so nothing is fixed in advance). The View
Character screen does the same through `INT F3h`, called once it has drawn the
character's two panels (the saves under the item icons; MOVE, the creature
record's +1Bh, and THAC0 at x D8h on HP's and PSI's lines, 7Fh and 86h, clear
of HP's value at its longest), and the routine that lists the weapons through
`INT FAh` after each one. The Loader keeps the numbers in the helper's memory,
with the time it last did: older than 5 seconds, the helper shows the sheet's
numbers instead. Before a screen is drawn, the helper asks the Loader to
update them and waits for its answer, half a second at most (`STATS_SYNC`:
`stats_req`, `stats_reply`). The game stands still while it waits, its
pointer too, so the Loader answers from a thread of its own
(`DiceLog.answer_stats_in_background`, a look each millisecond, about 4 ms to
work the numbers out), not from its main loop's next pass: that took 26-79 ms
with the Ledger's window open, on top of the game's own pause after an item is
picked up or put down (50-90 ms at 20,000 cycles: its mouse handler, DSUN.EXE
3573Dh, only queues the moves, and the pointer is drawn again once the game
has done with the item). That pause is shorter too: the game flips its two
screen pages as it redraws, and its flip (14414h) waits for the next vertical
retrace each time; `PROBE_FLIP` (INT 8Bh in place of the flip's call to the
wait, 1445Fh) skips the wait while a full screen is up (`SCREEN_IS` 2: the
inventory, View Character, USE, a talk) and waits as the game does on the map,
whose pace may hang on it. Measured with the user's save (Zulak's inventory,
20,000 cycles, where the game last drew the pointer, `DS:A137h`): 56-103 ms
(85 on average) before, 42-45 putting an item down and 63-67 picking one up
after; skipping every retrace wait saves no more, and the rest is the game's
own drawing (a faster game speed shortens it). Nothing else in the game changes.

Which class levels up next, on View Character: the game looks up the XP for
each class's next level in its tables and shows the lowest. Where it adds the
closing bracket, the helper (`INT D2h`) finds which classes that number
belongs to and adds their letters first.

### Detonate's blast on an item

The effect switch (its values at CS:0D96h of the segment at file 78BA0h, case
138 at 797F6h) queues effect 195 (the blast, 1d10) on the target, then calls
7AAEBh: of the target's items listed by A0:1A2Dh, those worn (+2 = 1), the one
whose item +10h is lowest and under 6 (the first on a tie); a 1d20 (the dice
routine, 0538:0089h through the overlay stub) under 15 less its item +14h
(the plus) has 4E0:7Ah take it away (one off a stack whose type's +0Fh has
bit 2, else the whole item; nothing left in its place). The item templates'
+10h: cloak 3, bone helm and leather chest 4, bone scale arm and leg 5, short
sword 6. `DET_ITEM` replaces its "mov dx,0Fh / sub dx,ax" (7AB95h) to record
the check (KIND_ITEM, extra the item | 4000h); the d20's own dice entry (its
caller's code `DETONATE_ROLL_RETURN`) is left out for it.

### The psionic power check

([In How the game works](HOW-THE-GAME-WORKS.md#psionics).)

The check is 5D59Dh (combatant, power 0-33, bonus), from the routine using a
power (5CC2Dh): its return is the d20 when the power works, 0 when it fails
("psionic power check fails", half the PSP), FFh when static disrupts it. Its
d20s come from random(low, high) (`1A0A:2FA9h`, selector A0h), whose code after
`rand()` no filter matched until `RANGE_SITE`; the dice log tells the three
calls apart by the code after each (`POWER_CHECK_RETURN`, `STATIC_FIRST_RETURN`,
`STATIC_SECOND_RETURN`), the psionic defence's two rolls (5D718h, the target and
the attack's elements 400h; random(1, its defence) with the attacker's kept d20
pushed after the arguments, so the call's `[BP+0Ah]`: `DEFENCE_FIRST_RETURN`,
`DEFENCE_SECOND_RETURN`), and skips its other callers (points for some spells'
pictures, 60041h). The score, the byte at `[BP-2]`, is the ability `+0` bits 0-2
of the power's 8 bytes name (`3FB9h:0000h`, `game.POWERS_SEG`; through 508:57h,
the ability as it is now), plus `+0` bits 3-7 (signed), plus the bonus, plus the
user's own number for the power, less 1: for a party member bits 3-7 of the byte
at selector 2F0h, `+77h + member * 22h + power` (0 not known; 1 known, all a new
character has), for anyone else 1 (5C9E7h). The game has routines to raise and
lower that number (5CF35h, 5CFA9h, 1 to 30) that nothing found calls. With a
Synaptic Static (effect 1Eh) kept up by someone else, the user's d20 over
`[BP-8]` disrupts the power; that was to be the power's score, but the ability
read for it is dropped and only the user's own number kept. Else the keeper's
d20 at or under its own Static score (`[BP-6]`), and no lower than the user's,
does.

### What hurts a monster (the Look box)

([In the README](README.md#what-hurts-a-monster-the-look-box).)

How: the patched game calls the helper (`INT F5h`; INT 66h-6Fh can't be used:
the game calls those itself, looking for sound drivers) where the box has
drawn its first status rows; the helper asks the Loader and waits a moment for
its answer, and prints the lines with the game's text routine. `INT F6h`, at
the end of the routine that closes the box, shows the whole description.

The AC is the one `PROBE_AC` last recorded for the creature
(`DiceLog.monster_ac`: the game works an AC out only for an attack, and keeps
none). Before any attack on it, `GameData.counted_ac` counts it as the game's
AC routine (58DD3h) does, as `THORNS_AC` does in the helper: the sheet's base
(+27h, 10 for an armed man), less each worn item's plus and its type's AC
(types with +0Fh 80h, in the item lists +8 and +0Ah), a fifth of a
gladiator's level and the DEX adjustment; the effects' part (Armor,
Barkskin...) is left out.

### Charges in item boxes

([In the README](README.md#charges-in-item-boxes).)

An item that casts a spell has the spell + 1 in its `+0Fh` and its charges
left in `+0Eh` (the routine finishing an item's use takes one off, 721E4h,
unless its type's `+0Fh` has 2). `PROBE_ITEM_BOX` (`INT DAh`, at the end of
the routine filling an item's box, 8C1A1h, the item `[BP+6]`) draws
`Charges: n` in the row after the box's own lines (`IB_CHARGES`) when the
spell byte is below F9h (from there the game's own effects: a belt's STR, a
ring's AC...) and the charges aren't 0, but not for fruit (type 60, eaten
whole) nor scenery (a type whose `+08h` has both 20h and 40h: a door, a
mirror, a crank), where those bytes hold something else (`TYPE_SCENERY`).

### No manual check

([In the README](README.md#no-manual-check).)

How: the dragon's question is the game's script 20, which script 120 runs (a
call into another script, command 14h) when the party leaves the warrens
(region 28h) until bit 12 of the game's variable (135, 73) is set. The right
answer goes on to script 86 at 1087, which sets 255 in the variable (7, 4)
and, in region 28h, that bit. In the Loader's copy of the scripts
(`dsloader/manualcheck.py`), script 20 does just that and ends: the same start
(offset 1, its one entry in the game's table of entry points), no words and no
question. It is replaced only if it is the dragon's (its `" word on page "`
line).

### The game's script bugs

([In the features page](FEATURES.md#the-games-bugs-fixed).)

How: `dsloader/scriptfixes.py` changes a few bytes in the Loader's copy of the
game's scripts (GPLDATA.GFF), each re-pointing one trigger or call: in Darkhold
the triggers story events re-register to script 200 at 909h (a lone exit) go
back to their own handlers (scripts 41 and 203: look text; 195: the portcullis
guard's attack); the Lava Rifts ranger's re-armed sight trigger goes to his own
handler (script 100 at 445h, not the hermit's at 56h); Linara's talk after the
extract calls her menu (script 68 at 209h). They are the OpenDS project's
(darkfix), as yuan-ti lists them (`GplRepairs.cs`), each checked against the GOG
file: a repair is made only where its script holds the expected bytes. The
fourth OpenDS repair, starting the final battle's stages without their pause,
is left out (yuan-ti keeps it off too: with the game's clock running the stage
gate waits its window out). Not seen in play yet: all are past the slave pens.

### Class restrictions

([In the features page](FEATURES.md#class-restrictions).)

How: the helper adds the classes' limits where the game checks an item against
the classes allowed to use it (`INT CDh`; `DUAL_WARRIOR` lets a human thief or
preserver who was a warrior, or a thief who was a cleric, wear that class's
armour), a multiclass (or warrior-and-preserver human's) armour where the game
checks for "No spell use" (`INT CCh`, `CLASS_AND_WARRIOR`), and a thief's armour
that isn't light at the end of the thief skill routine (`PROBE_BELT`: every
skill 0) and where an attack's backstab is set (`PROBE_STEALTH`'s `THIEF_REAR`),
both through `THIEF_HEAVY`. (`dsloader/restrict.py` says the same in Python, for
the tests.) A cloak's type (worn in the cloak slot, `+09h` 8) counts for AC as
armour does but isn't armour to the limits: the Cloak of Protection is for every
class (`CLASS_FORBIDS`, `restrict.is_armour`). A weapon the character has made
its own is left as the game has it, past the classes' limits
(`SPECIALIZED_BACK`, `restrict.specialized_back`): a dual-classed human's chosen
weapon specs once its new class's level has passed the warrior class's, and a
ranger's bow (every ranger has expertise with it, but never chooses it): a
multiclass ranger's always, a human's while a ranger or once past. `KIT_FORBIDS`
likewise passes a weapon of a type in the sheet's `SPEC_SLOTS` (`KF_CHOSEN`)
while the specs count (`SPECS_AWAKE`, `restrict.specs_awake`: one class; a
human's warrior class now or passed; a Battle Mage's kit awake), but for the off
hand's rules and when a weapon spec is being chosen (`KF_SPEC`).

A New character's starting weapons, armour and shields its classes can't use
(`restrict.usable`) are taken out of its lists (`weaponchoice.class_gear`, with
the rule on, after `finish_new` has made the starting long sword its weapon
spec's weapon, so a fighter/psionicist's becomes its club rather than going;
`ring.unlink` with `empty`, as a list of a character's may be left empty): the
game gives a character of several classes one class's gear (the first of fighter
or ranger, cleric, thief, psionicist, preserver and druid: seen in play, every
two-class combination as a half-elf) and puts what it can't wear in the
backpack.

### Multiclass hit points

([In the features page](FEATURES.md#multiclass-hit-points).)

The game's most hit points (874B0h): the sheet's total of rolled dice (`+0Ah`,
each new level's die added at 8735Eh), scaled by the levels now over the
levels before any were lost (`+24h`, `+3Fh`), divided by the number of
classes, plus CON's bonus (8757Ch: the warrior levels, capped at the last
that rolls a die, at the full bonus, the highest class's other capped levels
at up to +2). When CON changes it works back to the total (877BEh: the most
less CON's bonus, times the classes).

How: where the game adds CON's bonus (`INT CAh`, 87523h) and takes it off again
(`INT C9h`, 877DAh), the helper (`CON_SHARE`) puts in Demihuman Deities' for a
character of more than one class: (total + bonus × dice) / classes less
total / classes, the dice each class's levels up to its group's last that
rolls one (the game's table, `+group × 4 + 1`), the bonus the table's
warrior bonus (`+52h` + CON) if a class is in the warrior group, else at most
+2. One class, a human, or the rule off: the game's own. (An earlier version
also divided each die on its own at 8735Eh; the game's running total is the
book's, so that probe is gone.)

### Hit dice: the better of two

([In the features page](FEATURES.md#hit-dice-the-better-of-two).)

How: where the game has rolled a level's die (`INT BAh`, in place of the
`mov cx,ax` after the roll, DSUN.EXE 87319h), the helper keeps the first roll
and sends the game back to the start of its roll (872FDh), so both rolls are
the game's own and the dice log sees both; the second time it keeps the
better. Creation goes through the same routine, a die for each starting
level.

### Scores and hit points as rolled

([In the features page](FEATURES.md#scores-and-hit-points-as-rolled).)

The creation screen (overlay at 65480h; `DS:11A0h` the creature being made,
its scores from `+22h`; `DS:119Ch` the sheet, the hit points its `+8`):

* A click on a score (handler 637F8h) goes to 65480h, which takes the click's
  +1 or −1, keeps the result between the least (67399h, `DS:4994h`) and the
  race's most (`DS:4992h`), going round from one to the other, and writes it
  (`mov al,[bp-2]` then `mov es:[bx+22h],al`, 655C6h), then redraws the
  scores (65168h).
* A click on the hit points (63A24h) adds +1 or −1 (`add ax,[bp-2]`, 63A49h),
  kept between the least and most the classes could roll (`DS:4998h`,
  `DS:4996h`).
* The die, a race or sex chosen, or a class (657BBh, DI 1 to roll, 0 to keep
  the scores) sets the six in one of three loops by kind of class (65944h,
  65979h, 659AEh: `mov es:[bx+22h],al`), each through 6490Dh: the best of
  four 4d4 + 4 + the race's, or with DI 0 the score kept and raised to the
  class's least.
* 65168h puts back what was under the scores, from a copy taken when the
  screen opened (`0A0:30C3h`, the box at `DS:0F62h`: x1, y1, x2, y2, the first
  of ten), then draws each value with the game's text routine.

How (`RULE_HI_ROLLED`, the second rules word's 32: `game.RULE_ROLLED`): no
interrupt vectors are left, so the eight sites share `PROBE_CR_SPELLS`'s
(`INT 98h`), the byte after the `INT` saying which (`RL_SCORE` 1, `RL_HP` 2,
`RL_ROLL` 3, `RL_SUM` 4, `RL_CON` 5, `RL_TRY` 6) where `PROBE_CR_SPELLS`'s own
has its NOP; the helper moves the return address past it.

* `RL_ROLL` (the three loops' write, `INT` + site + NOP) writes the score; at
  CHR it keeps the six's total as the most (`RL_POOL`): with DI 1 the total,
  with DI 0 the total if more.
* `RL_SCORE` (655C6h) lets a lowering through; a raise is kept to the score
  plus what's spare (the most less the six's total), the score as it was if
  none.
* `RL_HP` (63A49h) leaves out the `add`.
* `RL_CON` (5, in place of `les bx,[119Ch]` + NOP at 63946h, in the score
  click's CON case at 63915h, after it has had 655D6h work out the least and
  most hit points again without rolling): the game only keeps the hit points
  within the new range, so a CON raised added nothing. `RL_SCORE` keeps the
  most (`DS:4996h`) before every click; here the hit points move as far as it
  did, which is CON's bonus for every level as the game counts it, and the
  game's clamp follows.
* `RL_SUM` (in place of 65168h's `add sp,4` after the copy is put back) draws
  `SUM:` 23 pixels left of the scores and the totals, `99/101`, on the line
  under CHR, with the game's text routine as the Loader's other lines are.
  The scores' box is made a line taller and wider (`rl_sum_box`: x2 48 to 77,
  y2 178 to 185, in the game's data) so the copy put back clears them.

The dice log adds the six's total to the creation lines. The die rolls a whole
character many times while it tumbles, about 100 `rand()` calls each, more
than the ring holds between two reads, so the log used to miss a character's
rolls. `RL_TRY` (6, whatever the rule, in place of `add ax,[499Ah]` + NOP at
6498Bh, in 6490Dh: AX a 4d4, `[BP+8]` the ability, DI the try) keeps each 4d4
in the header (`+282`, four for each ability) and counts them (`+280`); the
log reads them once the count has been still for 0.3 s, and doesn't report the
ring's missed rolls while it moves.

Checked in the game: three rolls of the die, every ability's line complete
(none "too fast"); CON 14 to 15 to 16 took a 3rd-level preserver's hit points
from 8 to 11 to 14, and back down; a preserver rolled 101 (`SUM:101/101`); DEX
lowered and STR raised by one, a second raise refused; the hit points
unchanged by left and right clicks (with the rule off, 16 to 17); the die's
next roll `SUM:98/98`, as the dice log's line; a new class raising INT from 14
to 17 took a fighter's 98 to 101. DONE on a preserver still opened CHOOSE A
SPELL (`PROBE_CR_SPELLS`).

### Rangers' casting level

([In the features page](FEATURES.md#rangers-casting-level).)

The game works out a caster's level in two places, both with the combatant
and the spell as arguments. The caster level routine (81B16h) takes the best
level of the caster's classes that cast the spell, a ranger's 7 less (its
"sub dx,7" at 81B6Ah); it sets the spell levels a caster may cast (half it
rounded up, 81664h) and weighs a spell against Dispel Magic. The level a
spell's duration and damage take is another routine's (5E25Ch), the same best
of the classes but a ranger's whole; the cast passes it down to the duration
(76CB3h) and the damage dice (76DA2h).

How: `PROBE_RANGER_LEVEL` (`INT A6h`, in place of `mov al,es:[bx+24h]`,
5E3B8h, where 5E25Ch takes a class's level, ES:BX the sheet plus the class's
place) counts a ranger's (classes 13 to 16) 7 less with the rule
(`RULE_HI_RANGER`, the second rules word's 2: `game.RULE_RANGER_CAST`), before
the best is chosen, so a cleric/ranger's cleric level can still win. A
Seeker's 5 and a Justifier's 9 come off there whatever the rule
(`kits.spell_class_level`).

Checked in the game: a 9th-level air ranger's Protection from Evil lasted 6
rounds (caster level 2; 27 without the rule).

### Preservers' INT

([In the features page](FEATURES.md#preservers-int).)

When a scroll's icon is clicked in its box, the game's routine (DSUN.EXE
8B690h) asks whether the character on show may learn the scroll's spell
(500:39h: only whether it already knows it; then 8B6D3h's `or ax,ax`), and if
so teaches it (500:43h sets the low four bits of its byte in the known spells'
table), uses the scroll up and says YOU LEARN THE SPELL
(`push ds / push 33F1h`, 8B712h); if not, YOU ALREADY KNOW THIS SPELL
(`push ds / push 3405h`, 8B719h) and the scroll is kept. Each spell's level is
a byte of the game's table of spells at the load segment + 3FB9h, 19Ch + 7 a
spell (`SPELL_LEVELS`; `GameData.spell_level`).

How (`RULE_HI_INT`, the second rules word's 4: `game.RULE_INT_LEARN`):
`PROBE_SCROLL_LEARN` (`INT A9h`) goes on to `INT_LEARN` for a preserver (the
class among its sheet's) and a wizard spell. Its INT is the creature record's
(`+25h`), its row of `INT_CHANCE` and `INT_MOST` (`intlearn.py`); `LEVEL_FULL`
counts the wizard spells of the scroll's level it knows. Full: AX 0 (the game
refuses, the scroll kept), and `PROBE_LEARN_REFUSED` (`INT 91h`, new, 8B719h)
pushes TOO MANY SPELLS OF THAT LEVEL in place of the game's message. Else a
d100 of the helper's own (`D100`: a generator stirred by the BIOS's timer
ticks); over the chance, the game teaches the spell and uses the scroll up,
and `PROBE_LEARN_SAID` (`INT 92h`, new, 8B712h) takes it back (the four bits
cleared) and pushes YOU FAIL TO LEARN THE SPELL. Each try is told to the
Loader in the helper's header (`+272`: a count, then the member, spell, INT,
chance, d100 or spells known, result; `DiceLog._learn_lines`). At a level up
(and a new preserver's picks), `PROBE_PICK_LIST` drops the game's list's
spells of a full level, and `PROBE_PICK_ANY` (`PICK_INT_ANY`) doesn't open
CHOOSE A SPELL when no unknown wizard spell is left at a level on offer that
isn't full.

A Shinobi (kits): the same check whether the character on show may learn its
spell (8B6D3h, `or ax,ax` before the jump to CANNOT LEARN FROM THIS ITEM) goes
to `SHINOBI_READ` (from `PROBE_SCROLL_LEARN`): not one of its spells, no (`THAT IS
NOT A SHINOBI SPELL`, the scroll kept); else a d100 against its
read languages, which the Loader keeps for each party member in the header
(`+362`, with STATS: `game.thief_skills_now`'s skill 7, armour and effects
counted), and above it the game teaches the spell and uses the scroll up, and
`PROBE_LEARN_SAID` takes it back (`YOU CAN NOT READ THE SCROLL`); read,
`INT_LEARN`'s d100 against INT's chance with the rule for INT (no most a
level). The try goes to the Loader as a preserver's (`+272`), with the read
roll and chance at `+366` (`intlearn.line`).

The box's spell icon is a button only for a character whose class the item type
allows: as the inventory opens the box, the game tests the type's class mask
(`+10h`) against the sheet's (`+12h`, 6D3B9h) and passes the answer on to
`DS:9CF6h`, and with it 0 the icon (button 3BC9h, 8B1A7h) is made inactive. The
scroll type (60h) allows wizards only, so a Shinobi, a thief to the game, could
never click it. `SCROLL_USE` (`INT 98h` and its site number, in place of `test
[es:bx+10h],ax`) makes the test and passes the scroll type for a Shinobi too.

What the box's handler says (4D0:2Ah, 8B810h: YOU LEARN THE SPELL, a Shinobi's
answers, the tome's) is written, on the inventory screen, to its line under
the paper doll, but nothing written there while the handler runs reaches the
screen: the game's own messages were never seen. `BOX_SAID` (`INT 98h` and its site number in
place of the `add sp,4` after it, 8B815h) keeps the text, and for 5 seconds
`LINE_SAID` (after the inventory's writes to its line, 580h:5Ch: 6E125h,
891A4h, 89222h, 89552h, 8968Bh, 8A940h) and `LINE_CLEARED` (after its clears,
528h:2Ah: 6C9BFh, 701C2h, 89595h) write it there again (580h:5Ch on the window
at `DS:11A4h`, through its stub segment 4272h, in a frame the overlay manager
can fix up). Those run as the pointer moves, so 2 ticks after the message
`BOX_NUDGE` (from the timer's `PROBE_TICK`) tells the game's mouse handler
(`MOUSE_EVENT`, as the driver would) that the pointer moved, with the driver's
buttons and place (INT 33h, 03h): the line shows the message with the mouse
still. As the game's own messages there, it stays till the pointer is on
something else. Not redrawing the window (118h:618h) afterwards matters: that
draws it blank.

### AD&D's class tables

([In the features page](FEATURES.md#adds-class-tables); `tables.py`.)

The game's XP table is 8 rows of 20 words (classes 1-8: cleric, druid,
fighter, gladiator, preserver, psionicist, ranger, thief; the gladiator's row
the fighter's), at its segment + 27Ch + the row x 40 + the level x 2, in
hundreds. Its THAC0 routine (87666h) takes off 20 the most of each class
group's (level - 1) x factor / 12: priests 8, warriors 12, wizards 4, rogues
and psionicists 6 (the records at `LEVEL_HP_SEG`: hit die, last die level,
fixed gain, factor); only the priests' differs from AD&D's. Its slot routine
(5E0ACh) asks 5E4C2h for each class (the class, a near pointer to the pair
level, WIS, the spell level 1-5), which applies one rule word for each byte
of the pair (`GameData.max_spell_slots`).

How (`RULE_HI_TABLES`, the second rules word's 8: `game.RULE_ADND_TABLES`):
`PROBE_XP` (`INT 90h`) replaces `imul eax,eax,64h` where a level up (87BBBh)
and View Character (67D41h) read the table: `XP_NEED` gives the row and
level's from `ADND_XP` (`PROBE_XP_NEXT` uses it too). `PROBE_PRIEST_THAC0`
(`INT 8Fh`) replaces `mov [bp-2],ax` (876ABh) in the THAC0 routine's loop: for
the priest group (CX 0), 2 x (level - 1) / 3. `PROBE_ADND_SLOTS` (`INT 8Eh`)
replaces `nop / push cs / call 5E4C2h` (5E240h): for a cleric, druid or
preserver it calls the routine with the level byte 0 (WIS's part alone; the
routine keeps only SI, DI and BP, so the probe keeps the rest) and adds
`ADND_SLOTS`; anyone else, or with the rule off, the routine as it was.

### Spells saved against with the spell save

([In the features page](FEATURES.md#spells-saved-against-with-the-spell-save).)

How: the Loader writes the game's own table that turns a spell's kind of save
into one of the five (a table of words at DS:1E75h, read afresh for every
save), and puts it back when the rule is unticked.

### Fire, cold and electricity: DEX instead of a doubled d20

([In the features
page](FEATURES.md#fire-cold-and-electricity-dex-instead-of-a-doubled-d20).)

How: the helper does the save's doubling (`INT F0h`) only while this rule is
off, and the Loader marks the fire, cold and electricity spells with the game's
own "can be dodged" flag (bit 40h of the spell's category word), which no spell
has, so the game's save routine adds the DEX defensive adjustment from its own
table.

### Two weapons

([In the features page](FEATURES.md#two-weapons).)

How: the game reads the attacker's DEX adjustment when it works out the
two-weapon adjustment; the helper takes over from there (`INT FEh`) and gives
AD&D's for the hand the attack's weapon is in.

The off hand's one attack: the game gives every weapon the character's rate
(the attack routine's `[BP-8]`, from the sheet's `+2Ah`, worked on by
`PROBE_ATTACKS`), so each hand of a 3/2 fighter attacks 1, then 2. With the
rule, `OFF_HAND_HALVES` makes a melee weapon in the off hand (the item's
`+11h`, slot 10; in the attack routine `[BP+12h]`, the DAM line's DI, View
Character's `[BP-0Ah]`) no more than 2 halves, after every other change to
the rate (specialization, the kits), so the extra attacks stay with the main
hand. `GameData.weapon_hits` gives the party view the same.

Haste and Slow come last, in the game itself: after `[BP-8]` is set (and
`PROBE_ATTACKS` has worked on it), the attack routine (5883Ah) asks a routine
for the attacker's speed, which reads its effects: 4 for Hasted (effect 22)
doubles the halves, 1 for Slowed (47) halves them, rounded down; then the
round's attacks are the halves plus the round's parity, over 2. Checked in
DOSBox by turning a Hasted effect into Bless (the attacks went back) and one
into Slowed. The game's DAM lines never did it: `SPEED_HALVES` (`NS_HAS` on
the two effects) does, last, in `PROBE_DAM_LINE` and `PROBE_MISSILE_LINE`
(`FRAME_SPEED`: the creature from the routine's `[BP-6]`, its record, over
3Ah from the creatures' `[1665h]`) and `PROBE_VIEW_DAM` (the character on
show), whatever the rules; `weapon_hits` does it for the Characters tab. The
inventory's formatter (72AB1h) wrote no count for 2 halves or fewer, so a
slowed character's 1 read as one a round: `dam_half` makes its `jng` a `je`
(72AC3h), and 1 half is `0.5x`. View Character's always has its count.

A weak material's damage: the attack (and the inventory's line, through the
same overlay routine, 508:52h) takes 2 off for wood and 1 for bone, stone and
obsidian, from a weapon with no plus (a power alone doesn't spare it) whose
type isn't marked 80h (the clubs and staves), as Dark Sun's rules have it
(`game.MATERIAL_DAMAGE`, beside `MATERIAL_TO_HIT`); found in DOSBox by giving
Cilla's long sword each type and reading the line. View Character's line
(64E33h) adds only the type's bonus and the plus, so it read one or two more:
`VIEW_MATERIAL` takes it off in `PROBE_VIEW_DAM`, whatever the rules. The dice
log's damage line names it (`-1 bone`) where it said `-1 weapon`.

Rangers and Twin-blades in light armour: the game asks whether the attacker
is a ranger (the sheet's `+12h`, 200h) before it calls for the DEX
adjustment, and gives a ranger none (DSUN.EXE 5961Fh). With the rule that
test is `RG_TWO` (a site of `INT 98h`): a ranger wearing armour that isn't
light (`HEAVY_WORN`: `ARMOUR_WORN` with each piece's material weighed, as
`KIT_ALLOWS` does: leather, or of no material) reads as anyone else, and
`PROBE_TWO` gives AD&D's; a Justifier (`KIT_IS_B` on the sheet) is let
through in any armour. A Twin-blade is passed over in `PROBE_TWO` only in
light armour. `GameData.two_weapons` (`heavy_armour_worn`) says the same in
the log and the party view.

### Items saving against acid

([In the features page](FEATURES.md#items-saving-against-acid).)

How: where the game works out the number a weapon's d20 must reach
(`INT D6h`), where it skips the roll for armour with no magical power
(`INT D5h`) and where it works out armour's number (`INT D4h`), the helper
gives the easier of the two and records the check for the dice log.

### Rings and cloaks of protection

([In the features page](FEATURES.md#rings-and-cloaks-of-protection).)

How: the game's AC routine counts a worn item's plus only if its type's +0Fh
has bit 80h, which the Ring type lacks; the helper (`INT F8h`, at 58EBDh)
sets it for rings, and the saving throw routine's sum of modifiers starts at
the worn rings' plus (`INT F9h`, its `xor si,si` at 79D47h) rather than 0.
With the rule, both look first at what the creature wears (`PROT_SCAN`: a
worn armour piece with a plus, one of metal, a shield in a hand, and each
hand's ring): the AC routine drops a ring with magical armour and the worse
of two rings, and both drop the cloak with any of the three. The Loader's
saves and AC rows weigh it the same way (`GameData.protection`).

### Half-giants' two-handed weapons

([In the features page](FEATURES.md#half-giants-two-handed-weapons).)

How: the inventory screen checks a weapon type's two-handed bit (+0Fh, 40h)
twice when something goes into a hand: the other hand's ("Two handed weapon in
use") and the one going in ("Need two free hands"). The helper (`INT E3h`)
answers both for the character on show, "not two-handed" for a half-giant.

### Helms

([In the features page](FEATURES.md#helms).)

How: the helper sets the helm types' AC as the game's AC routine reads it
(`INT F8h`, the Ring +1's place), and as the item box reads it for its "AC
BONUS:" (`INT 88h`, at 8C15Ah), so a helm not worn yet shows its 1 too. (An
earlier rule gave boots a move in a fight; it is gone, and the boots' names it
changed go back to the game's.)

### Ages

([In the features page](FEATURES.md#ages-and-magical-aging).)

How: the Loader (`aging.py`, with `RULE_AGING`, RULES_HI's 256) keeps each
party member's age in the sheet's +17h (`SHEET_AGE`: the age less the race's
base starting age, plus 1; 0 none yet, a thri-kreen's 6 being its base), the
byte the packed weapon specs leave free (Weapon specialization, below). A member
with none gets its starting age (`give_ages`, in the dice log's item pass, not
while DSCLOG's weapon window is up: its trial puts the four bytes back as they
were). `age_by` moves an age (Haste, Restore Youth): the categories reached or
left change the sheet's scores and the creature's (`changes`, Table 8, the
scores kept within 3 to 25), and the maximum (`most_age`: the race's base and
dice, seeded with the character's name and race, so always the same) kills
(`kill`: no hit points, the game's dead status). The Loader puts the age, its
category, the next and its age in each member's STATS (+28h on: `STATS_AGE`),
and DSCLOG's `AGE_TEXT` writes them: the inventory panel's `AGE 23` in its free
row between PSI and AC (`PROBE_INV`, `AGE_INV_Y`), View Character's under the saves
(`V_AGE_Y`: there is no free row in the left column, CHR's line and the sex and
race line being 3 pixels apart), and `AGE_LINES`, the first of the Effects
panel's lines (`EF_LINES_OF`). Checked in DOSBox: the game's own party given
ages in a new game, View Character, the Effects screen (its weapon specs then
on its second page) and the Characters tab.

Haste's aging: the dice log's `effect_changes`, as a Hasted effect (22) starts
on a combatant (not one a game just loaded has), calls `aging.hasted`: a system
shock roll by the creature's CON (`SYSTEM_SHOCK`, the Player's Handbook's
table), death on a failure (`kill`: HP 0 and the dead status, which the game
takes as dead: no more turns, no share of the XP, "Dead" under the portrait),
else a year (`age_by`) for a party member. The rolls are the Loader's, logged.
Checked in DOSBox: Gerakis at CON 1 hasted by Cermak (90 against 25: dead) and
K'ratchek at CON 19 (89 against 99: 7 years old).

Restore Youth (211, a cosmos spell: `COSMOS_MASK` in DSCLOG's `P6_MASKS`) is
Cure Critical Wounds' record with its dice (+1Ch to +1Eh) made 0 and no
handler, so the game casts it as a touch spell that heals nothing. The dice
log's `KIND_CAST` line for it calls `aging.restore` with the target and the
caster's level (`effect_caster_level`): a system shock roll, then `age_by` back
by the level, never below the character's true age (`natural_start`, the
seeded starting roll `give_ages` used). Checked in DOSBox: K'ratchek at 12th
level casting it on Gerakis aged 37, true age 27 (survived, 27 again).

### Weapon specialization

([In the features page](FEATURES.md#weapon-specialization).)

How: the chosen weapon types are kept in four bytes of each character's own
record that the game never uses (+14h to +17h), so saves and the
saved-characters roster keep them. Up to 2.12 they were a byte each (the kind +
1, 0 none); now they are packed, 5 bits each in +14h to +16h (room for 31
kinds), +16h's top bit (`SPEC_PACKED`) marking it, and +17h is the
character's age (`SHEET_AGE`, years past its race's base starting age: see
Ages above). A sheet keeps the old layout until something writes to it, and
everything reads both: DSCLOG through `SPEC_GET`, `SPEC_FIND`, `SPEC_ANY`
(and writes through `SPEC_SET`, `SPEC_CLEAR`, which pack an old sheet first,
`SPEC_PACK`: its +17h, an old 4th spec, becomes 0, no age yet), the Loader
through `game.spec_kinds`, `packed_specs` and `with_specs`. The weapon
window's trial of a kind pointed at (`PK_WORD`) puts the four bytes back as
they were. Checked in DOSBox: Gerakis with four kinds a byte each and then
packed with an age of 30 lists the same four on the Effects screen, his long
sword's spec counts in the fight, and the packed bytes come back unchanged
through a save (SAVE01.SAV's sheets) and its load. The helper adds the bonuses and attacks
where the game makes a weapon attack (`INT D1h`, `INT D0h`), on the DAM lines
(`INT CFh`, `INT CEh`), calls the game's psionic pop-up in weapon mode after
the creation screen's DONE (`CR_WEAPONS`, below) and at a level gained
(`INT C2h`, then `INT C1h` to `INT BCh` in the pop-up, window 3021), and prints
the Effects screen's lines (`INT BBh`). (The creation panel had weapon pages
up to 2.4.0; the weapon window after DONE took their place.)

At creation, `CR_WEAPONS` (a site of `INT 98h`, new: `pop cx / push si / nop`, 3
bytes at 666DFh in DONE, 65480h) asks the new member SI for the weapon specs it
is due (`LV_CHECK`, the pop-up's far address from the stub DUAL's kit menu uses,
`DK_PSI`), after clearing whatever the kit page put in. It runs after DONE has
closed the screen's windows (6659Eh to 66611h) and let go of their pictures:
before that, the weapon window, bigger than the psionicists', fails to open
("Failed to open window", the game's fatal error, exit code 1, from its window
opening at 62182h), while the psionicists' own still fits. The game's memory for
it is the window's pictures: packed with repeats (`icons._pack`, as the game
packs its own: a byte n, odd for one pixel n >> 1 + 1 times), its marble and
sixteen slots come to 41 KB rather than 93 KB, and it opens for a fourth
character made after CHOOSE A SPELL too. `LV_DUE` gives a Myrmidon being made
two (`LV_CREATING`). The way back is a frame the overlay manager can patch, as
for `PROBE_CR_SPELLS`, whose CHOOSE A SPELL comes first. While the window is up,
`LV_CREATING` (the header's +361) is 1, and the Loader leaves the New character
alone (`DiceLog._weapons_asked`): otherwise it would put in the defaults before
the picks. Picks left unmade (EXIT) are then the Loader's
(`weaponchoice.kinds_for`: the kit's weapon, `kits.default_kind`; a thri-kreen's
chatkcha; the long sword, a gladiator's club).

The pop-up in weapon mode is the psionicists' window (17501) made bigger:
window 3021 is 214 by 156 (its marble, BMP 3022, the psionicists' 17001
carried on to that size), with a slot for each weapon type, six to a row: a
button 0x860 + type whose picture (ICON, same number) is the game's inventory
picture of a weapon of that type (`weaponpages.PICTURES`, objects in
`SEGOBJEX.GFF`; the polearm's made smaller) on a slot, in three frames as the
game uses them: as it is, lit (the pointer on a button in use), and out of use
(the weapon a grey shape). The game puts the window where it would centre the
psionicists' (`push 2B0050h` before `PROBE_PK_WIN`), so `PROBE_PK_WIN` gives
it the place that centres 214 by 156; `PROBE_PK_TITLE` puts the two lines
under the slots, centred in the wider window (the routine's width and y,
pushed as bytes after it). Naming the slot under the pointer: a button in use
takes the pointer itself (its lit frame), so no cell handler of the window
(530:43h, as the powers' cells have) ever hears of it; instead `PK_HOVER` (a
site of `INT 98h`, new: `or ax,ax / jnz 85F5Dh`, 4 bytes at 85F44h, in the
pop-up's event loop 85F2Ch, the jump done by the probe) reads the pointer each
time round (`INT 33h` function 3), finds the slot from the window's place and
the slots' (`PK_SLOTS_X`, `PK_PITCH`; `test_picker_matches_dsclog` keeps them
weaponpages'), and when it changes draws **SPECIALIZE IN** (or **EXPERT IN**:
`PK_WORD` puts the type in the sheet's first empty slot for a moment and asks
`SPEC_OF_SHEET`, as `weaponchoice.pick_word`) and the type's name with the
routine the powers' handler names a power with (85CC9h, which rubs out the
lines it drew before), or the title again off the slots. A missile weapon's
attacks a round are its item type's (+0Bh, in halves: a bow 4, the rest 2),
not the character's (sheet +2Ah) as in melee; `INT D1h` raises them to a
specialist's (`MISSILE_RATE`, by the fighter, gladiator or ranger level; a
grand master one more; a weapon type not chosen, from 7th level, a
specialist's a band lower), and the Loader's Characters tab does the same
(`specialize.missile_attacks`). Every ranger's expertise with the bow is in
`SPEC_OF_SHEET` (`specialize.skill`), not in its chosen weapon types, so
`KINDS_ALLOWED` (`restrict.allowed_kinds`) leaves the bow out of a ranger's
choices, and `EF_LINES_OF` (`GameData.specializations`) lists it after the
chosen types, by `SPEC_OF_SHEET`'s skill (none for a non-ranger).

The inventory screen's line for a missile weapon (`1D4`) comes from a branch of
the same routine as the DAM line, with the weapon's own rate of fire (its type's
`+0Bh`): PROBE_MISSILE_LINE (INT FCh at 729FFh) gives it the rate PROBE_ATTACKS
does (`MISSILE_RATE`) and the bonus and sides PROBE_SPEC_DAMAGE does, for the
creature the routine has.

### Kits

([On the Kits page](KITS.md).)

A kit is chosen for a class: by a character of one class when it is made, and
by a human for each class it changes to (up to three). There are three for
each class, or none (the class as it is). Each gives something and costs
something, as AD&D's kits do. The **Kits** switch on the Options tab
(`game.RULE_KITS`, bit 0 of the helper's second rules word, `RULES_HI` at the
header's +270) switches them all off.

#### The kits

What each kit gives and costs is in [the Kits page](KITS.md).
Two kits have tables of their own.

The Seeker's and the Justifier's tables are AD&D's (*The Complete Ranger's
Handbook*), up to 10th level, and the Shinobi has spells of its own (the
game's and four new ones): both in
[the Kits page's spell slots](KITS.md#kits-spell-slots). Their spells are
cast at the table's casting level, not the ranger's or thief's.

Fogbolt, Reflected Image, Spook and Friends, [new
spells](#new-spells-wizard-and-6th-level-priest), are known by its bit in the
sheet (`NS_KNOWS`) rather than the game's byte: `SHINOBI_KNOWS` reads either for
the level up's offer (`SHINOBI_UNKNOWN`, `PROBE_PICK_LIST`), and counts them as
known (not offered) while the new spells are off (or, for 199-201, before
`SEG_MOVE`). `SHINOBI_WIZARD` gives the Shinobi's casting level for the new
spells (196-201) as for the game's wizard spells (0-68).

No kit is the kit page's first row, and what a new character has.

#### The kit's byte

Sheet `+43h`: zero in every sheet of the saves and saved characters at hand
(176), and nothing in DSUN.EXE reads or writes it (no `es:[bx+43h]` access of
any kind), as with the weapon specs' `+14h` to `+17h`, which saves and the
roster keep. `+45h` is the same, if a second byte is needed (the Arcanist's
CON change used it, once, before that became its d3). 0: no kit; 1 to 3 the
class's kits.

#### Choosing one

The creation panel's lower window shows the psionic disciplines or the
clerical spheres, each with a button that swaps them (VIEW SPHERES is there,
out of use, for a class with no sphere). The **KIT** page is at the end of that
chain, opened with a **KITS** button where the last window's button was:

| The class (one only) | Where KITS is |
|---|---|
| fighter, gladiator, preserver, psionicist, thief | the disciplines' window (3022, a copy of 3012) |
| cleric, druid, ranger | the spheres' window (3023, a copy of 3013) |

`WP_IDS` (`kitpages.panel_windows`) picks the windows for the classes being
made, for the probes that open them (`PROBE_WP_DISC_WIN`,
`PROBE_WP_SPHERE_WIN`, and `PROBE_WP_CLASS` when the classes change). The kit
page itself is a window for each class (3026 to 3033, by the creation screen's
class numbers), its rows NO KIT and the class's three kits (buttons `888h`,
and `870h` + 3 × (class − 1) + kit − 1), its button VIEW PSIONICS (`851h`,
`kitpages.KIT_BACK`) back to the disciplines. It is kept at
`DS:EA6h` with the spheres' own routine answering its buttons, so
`PROBE_WP_SPHERE_CLICK` gets its clicks and `PROBE_WP_SHOWN` lets the game
close it when another class is clicked. `KIT_ROW` puts the kit in the creation
sheet's `+43h`, and `KIT_MARKS` marks the rows. As the game's spheres do, the
rows not chosen are out of use (greyed) while one is; the one chosen, clicked,
is taken back (`KIT_OPEN`, `FFh`: none chosen, no kit), and the rows are all
in use again. The game keeps the whole sheet when DONE is pressed: `+43h` is
in the roster's CHAR record (the sheet at its `+4Eh`). It also keeps the
creation sheet from one character to the next, so the kit is put back to none
whenever the disciplines' window is opened other than on the way back to it
(`KIT_KEEP`, set by VIEW PSIONICS): for a new character, or another class. The
die's new roll clears a kit too when the classes aren't the ones the panel
last saw (`kit_stale` against `wp_classes_seen`, which `PROBE_WP_CLASS` sets
on a class click); a new character's default class is never clicked, so
`KIT_ROW` sets `wp_classes_seen` as well, to the classes the kit is chosen
for.

The rows' letters are carved from the game's own labels, as the weapon
pages' (`kitpages.py`, with a J and a hyphen drawn). The panel's frame comes
in to about 95 pixels past the rows' left at the second kit's row, so a row
is held to 88 (`ROW_WIDTH`, its mark's room in), clear of it: ARENA CHAMPION,
SWASHBUCKLER, ELEMENTALIST, GROVE WARDEN, BATTLE MAGE, MIND BENDER and MIND
WARRIOR are shortened (CHAMPION, SWASHBUCK, ELEMENTAL, WARDEN, BATTLMAGE,
M-BENDER, M-WARRIOR), the last two as the game's P-KINESIS. Each row's button
is a copy of the game's AIR row's, which is 33 pixels wide, made as wide as its
label (`weaponpages.row_button`): at 33, a click on
the right of a longer name did nothing.

The Effects screen's lower panel (`PROBE_EF_ROWS`) has the kit's line first,
`KIT: RAVAGER`, before the weapon specs; the Characters tab has `Kit: Ravager`
(`GameData.kit`).

The lower panel has room for five lines (`EF_LINES`); three kits and a
gladiator's four weapon specs make eight. `EF_DRAW` goes over the lines twice
(`EF_LINES_OF`, each through `EF_LINE`): first counting them (`EF_COUNT`), then
putting those of the page on the panel (`EF_PUT`). A Shinobi's kit line is followed
by its read languages (`RL_LINE_OF`: `READ LANG. 40%` from `READ_LANG`, the Loader's,
for the member `EF_DRAW` keeps in `EF_MEMBER`). With more than five, a page
has four and `MORE: CLICK HERE` in the fifth row; a page that starts with a
weapon type has its skill's heading again over it (`EF_HEAD`), and a heading
that would be a page's last row goes to the next. `PROBE_EF_CLICK` (`INT 97h`,
new: `mov si,[bp+8]`, 3 bytes at 7EC9Eh) is in the screen's handler for its
cells (7EC97h, buttons from 2BCDh; the lower panel's from the 21st): the events
are 2 the pointer onto a cell, 40h a button down and 20h up again, and on 20h
over the lower panel with more than a page it asks for the next page
(`EF_NEXT`), has the window drawn again as the handler does after a cell's
label (118:618h, its far address read from that call in the handler; the
window DS:[11A4h]: background, then the screen's contents, 7E620h, which
draws the cells and `PROBE_EF_ROWS`), and leaves the handler (7EDF5h). Any
other drawing shows the first page. The redraw is overlay code reached from
the helper, so the INT's way back is in a frame the overlay manager can patch,
as for `PROBE_LV_PICK`. Calling 7E620h alone draws the contents without the
background: the pages' text lands on top of each other.

The panel follows the classes as they change. A class click runs
`PROBE_WP_CLASS`: the disciplines' window opened again if it isn't the one for
the class now; KITS pressed for a character with no kit class goes back as
VIEW PSIONICS does. A new race or sex empties the classes, has the panel
opened for no class, then puts the default class in without a click:
`PROBE_RACE_PANEL` (`INT 89h` at 63403h, after that call) opens the disciplines'
window again for the class put in.

#### Multiclass kits

A few pairs of classes taken at once by one race have kits of their own
(`kitpages.MULTI`): groups numbered on from the classes, 9 elf cleric/fighter,
10 half-elf fighter/thief, 11 half-elf druid/fighter, 12 half-elf
cleric/ranger, 13 dwarf fighter/thief, 14 half-elf fighter/preserver, 15
half-giant fighter/psionicist, 16 halfling fighter/thief, 17 halfling
cleric/psionicist, 18 thri-kreen druid/fighter, 19 mul druid/fighter.
`MULTI_GROUP` (`multi_table`) finds a sheet's group from its race and classes;
`KIT_PLACE` gives such a sheet place 0, so its kit is the kit byte's low two
bits (1-2, a group having one or two kits), and its number is group × 4 + kit,
as a class's. The KIT page has a window for each group (`KIT_WINDOW` + group −
1: 3034-3044), its rows `MULTI_ROW` (`88Ah`) + 3 × (group − 9) + kit − 1, past
KITS's own `889h`, so `WP_CLICK` passes button numbers up to the last group's
(`8A8h`) to `wp_page_button`; STORE and RECALL are `8B0h` and `8B1h`, past
them.

The Loader writes two things to the helper's header for these kits: at `+350`
(`KIT_OUTDOORS`) a bit for each party member under the open sky (an outdoor map,
or a square not of a building's floor: `stealth.daylight`), once a second; at
`+351` to `+354` (`KIT_DANCE`) each member's Battle Dancer's dance, +1, −1 or 0,
which `dance.py` rolls as a fight's first round begins (a d20 against DEX − 4, a
natural 20 failing: `kits.DANCE_CHECK`) and counts down. It ends with the fight,
whatever came of it, and the next fight's first round rolls it again
(`dicelog._kit_tick`): once the game's fight flag, seen up since the roll, has
been down `FIGHT_OVER` (2 seconds; the game clears it as a fight ends and
between the arena's waves, and it is still clear as round 1's initiative is
rolled, before it was ever up, which doesn't count), or the game's clock is
`FIGHT_GAP` past the last round, or has gone back (a game loaded). The next
round then rolls again (`_kits_due`), and the log counts the rounds from 1 again
and forgets the last fight's monsters' ACs (`_new_fight`), for a fight soon
after another (the arena's next wave) too. At `+355` (`KIT_WILD`) each Wild
Fury's (and Gerakis's) Wild Fighting, which `wild.py` rolls as a fight's first
round begins (a d20 against CON − 4, a natural 20 failing: `kits.WILD_CHECK`)
and clears as the dances end: bit N, member N's check failed; bit N + 4, it
passed.

#### Where each effect goes

A kit has one number (the creation class × 4 + the kit: `kitpages.KIT_IDS`). A
human may have a kit for each of its classes (up to three), so every rule asks
whether the sheet has a given kit awake: `KIT_IS` (kit in AL; `KIT_HAS` asleep
too), or inline, `call kit_is_b` / `db KIT_X` for a sheet at ES:BX, `cr_is`
for a creature (AX), `cb_is` for a combatant (`[BP+6]`); each leaves the kit's
class's place in `KIT_WHERE` for `KIT_LEVEL` and `KIT_CLASS_OF_SHEET`. Rules
that several kits touch (AC, THAC0, slots, saves, to hit and damage, cures)
take each kit's part in turn. Each effect has its twin in `kits.py`, which the
Loader and the dice log use (once for each kit in `kitpages.kit_ids`), and
emulated tests hold the helper to it:

| Effect | Kits | Where |
|---|---|---|
| damage with a weapon | Ravager, Brute, Ghetto Fighter (melee: `KIT_MELEE`, by the item type; the Ghetto Fighter's a dagger's kind), Battle Dancer and Wilderness Avenger (melee or missile: `KIT_EXTRA`, the dance's `KIT_DANCE` byte, or the Avenger's 1 against anything), Arena Champion (melee, a shield in a hand: `KIT_CHAMPION`, by `PROT_SCAN` of the attacker's thing, `[BP+18h]`), Wild Fury (Wild Fighting passed: +3, melee or missile, `WILD_PASSED`) | `PROBE_SPEC_DAMAGE` (`KIT_ATTACK_DAMAGE`), and the DAM lines (`PROBE_DAM_LINE`, `PROBE_VIEW_DAM`: `KIT_MELEE` only) |
| to hit | Ravager, Brute, Ghetto Fighter (and 1 worse with anything but a dagger), Arena Champion, Battle Dancer, Wilderness Avenger, Wild Fury (Wild Fighting failed: −3, `WILD_TO_HIT` by `KIT_WILD`) | `PROBE_ATTACKS` (`KIT_TO_HIT`: `KIT_CHAMPION`, `KIT_EXTRA`, and `KIT_MELEE` in melee) |
| AC | Ravager (`RAVAGER_AC` by level against the sheet's base AC, `+27h`), Wanderer, Sentinel and Arena Champion (a shield in a hand: `PROT_SCAN`), Grove Warden, Battle Dancer (its dance: `KIT_DANCE`), Wild Fury (Wild Fighting failed: 3 worse, no worse than 10, `KIT_WILD`) | `PROBE_AC` (`INT 62h`, the end of the AC routine: `KIT_AC`) |
| movement | Stalker, Rescuer (2 more) | `PROBE_MOVE` (`KIT_MOVE`) |
| spell slots | Scholar (+1 wizard), Battle Mage (−1 wizard), Crusader (−1 priest), Seeker and Justifier (their priest tables, `SEEKER_SLOTS`, by ranger level, in place of the game's), Elementalist (a level behind) | `PROBE_SLOTS` (`INT B6h`, new: the end of the game's slot routine, `mov ax,[bp-2]` at DSUN.EXE 5E255h) and `PROBE_SLOT_LEVEL` (`INT B5h`, new: where it takes a class's level, `mov al,es:[bx+24h]` at 5E1F6h); `GameData.max_spell_slots` with `kits.slots` and `kits.slot_level` |
| a power's PSP | Mind Bender, Kineticist, Titan Mind (psychometabolism 2 less, telepathy 2 more) (by discipline: powers 0-5 psychokinesis, 6-19 psychometabolism, 20-33 telepathy, the defence modes among them; never below 1) | the powers' table (8 bytes a power, at the load segment + 3FB9h: `+1` the cost to use, `+2` to keep up, 63h for none; `+5` FEh for a defence mode). `PROBE_PSP_USE` (`INT B4h`, new: where the routine using a power has its cost in DI, its table's or worked out for Enhanced Strength and Domination, DSUN.EXE 5CBE7h), `PROBE_PSP_TABLE` (`INT B3h`, new: the table's cost read in the check whether a power can be used, 5CAA3h, and for the half a failed power costs, 5CCA2h), `PROBE_PSP_DEFENCE` (`INT B2h`, new: a defence mode's cost taken off, 5D820h); `kits.psp_cost`. Monsters' powers (5A773h) are left alone |
| a cure's healing | Healer (+1 a die of Cure Light, Serious, Critical Wounds: spells 71, 112, 127), Lifebinder (a die more: a d8, Blood Flow's, 108, a d6, rolled from the game's rand() seed by `GAME_DIE`), Rescuer (as the Healer) | `PROBE_CURE` (`INT B1h`, new: "nop / push cs" at DSUN.EXE 79619h in the handler for spells with rules of their own, where the healing, pushed with the target, goes to the routine that heals; the caster its `[BP+8]`, the spell `[BP+0Eh]`; the probe pushes CS itself). The Cell Adjustment's jump into 79618h is clear of it |
| a spell's damage | Wilderness Avenger (+1 a die of Cause Light, Serious, Critical Wounds: spells 72, 113, 128) | `AV_CAUSE`, from `AREA_DMG` (754ECh, "mov [bp-12h],ax" where the routine dealing a spell's damage to the creatures it reaches, 7511Bh, the Cause spells' way too, has rolled it, DI the spell; a helpless target's at `[BP-14h]`) and `HARM_SITE` (761A9h, the one-target routine's, `[BP-8]`): when `CAST_SITE` last saw that spell cast by an Avenger (`CAST_WHO`, `CAST_SPELL`), the bonus on the damage and on a helpless target's; the dice log's `_harm_bonus`, by the last `KIND_CAST` |
| healing spells never known | Wilderness Avenger (Cure Light, Serious, Critical Wounds, Blood Flow; Heal and Water of Life) | `AV_HEAL`'s list in `PROBE_EL_KNOW` (`AV_KNOW`: as a character is made, the spell its place in the table / 7; a level up marks none) and `AV_GRANT` (5E499h, "test es:[bx+19Dh],edx" in the routine giving a priest its spheres' spells, 5E401h, no caller found: guarded as `PROBE_EL_GRANT` guards it; a site of `INT 98h`: ZF set for them, so they aren't learnt); the 6th-level two in `NS_PRIEST_KNOWS` (no mask for an Avenger). One made with 2.10.0 or earlier, with them known: `kits.avenger_heals` marks them not known when the save is loaded |
| casting level | Seeker (the ranger level less 5), Justifier (less 9), Shinobi (for its wizard spells, the thief level less 5) | the game works it out in two places, both with the combatant and the spell as arguments. The caster level routine, 81B16h, counts a ranger's level 7 less: `PROBE_RANGER_CAST` (`INT AFh`, new: that "sub dx,7", 81B6Ah) makes it the kits' 5 and 9, and `PROBE_CAST_LEVEL` (`INT ACh`, new: its end, `mov ax,[bp-2]`, 81C06h) gives a Shinobi its level for a wizard spell. That routine sets the spell levels a caster may cast, half the caster level rounded up (81664h, which asks for spell 0: the USE screen's lists and slots), and weighs a spell against Dispel Magic. The level a spell's duration and damage take is another routine's, 5E25Ch (the best level of the caster's classes that cast it, a ranger's whole; the cast passes it down to the duration, 76CB3h, and the damage dice, 76DA2h): `PROBE_SPELL_LEVEL` (`INT A8h`, new: its end, `mov ax,di`, 5E3D1h) gives the Shinobi its own; `PROBE_RANGER_LEVEL` (`INT A6h`, new: `mov al,es:[bx+24h]`, 5E3B8h, where it takes each class's level) takes the Seeker's 5 and the Justifier's 9 off its ranger level (and a plain ranger's 7, with the [rangers' casting level](#rangers-casting-level) rule). `kits.ranger_cast_drop`, `kits.cast_level`, `kits.spell_class_level`, and `GameData.effect_caster_level` |
| wizard spells for a thief | Shinobi | slots: `PROBE_SLOTS` gives a Shinobi's wizard slots the Seeker's table by its thief level (`kits.slots`). Its spells known are the party's table of them (at the load segment + 3800h, from 168h: 8Ah bytes a member, a byte a spell, not 0 if known), and the USE screen lists and casts them as any preserver's. Learning: a level up as a thief from 6th goes on as a preserver's would (`PROBE_LV_PICK`'s `LV_SHINOBI`) to the routine that offers a preserver its spell (620:5Ch, 85560h), which takes the preserver level and goes on only for one, and then only if the game's list (500:2Ah) has a spell to learn: `PROBE_PICK_ANY` (`INT A7h`, new: `mov [bp-2],ax / or ax,ax`, 85580h) opens CHOOSE A SPELL (85771h) for a Shinobi with one of its spells unknown up to the level it casts. There `PROBE_PICK_LEVEL` (`INT ABh`, new: `inc al`, 85861h, the preserver level the highest spell level on offer is half of) gives it its casting level, and `PROBE_PICK_LIST` (`INT AAh`, new: `mov di,ax`, 8563Fh, after the game fills the list, at the segment of the `mov ax,348h` before it, `+7`, a word a spell; the character at its `+25Bh`; the highest spell level `DS:[4AECh]`) puts its own unknown spells in the list (`kits.pick_list`). A scroll: see [Preservers' INT](#preservers-int). Armour: the game has no armour rule for a single class's spells (the multiclass preserver's is the class restrictions'), so it casts in the light armour it may wear |
| spells learnt at a level up | Scholar (one more) | `PROBE_LV_PICK`'s `LV_SCHOLAR`: at a preserver's level up, the routine offering its spell (620:5Ch, its far call read from the code after the probe) called once before the game's own |
| a power's PSP to keep it up | Mind Bender, Kineticist (as the cost to use it; 63h, none, left alone) | `PROBE_PSP_KEEP` (`INT B0h`, new: the table's `+2` read where the round's cost is taken, 5CE49h, the combatant in SI) and `PROBE_PSP_KEEP_DX` (`INT AEh`, new: the check whether a power can be kept up, 5CB02h, the combatant in DX). The monsters' cost lookups (5D4DAh, 5D4EFh) are left alone |
| the off hand | Healer (no weapon), Battle Mage (nothing) | `PROBE_CAN_USE`'s `KIT_FORBIDS` with `KF_OFF_HAND`: the can-use routine's only caller is the equip routine (6EF52h), whose `[BP+8]` is the slot (the item's slot + 4: 7 the right hand, 14 the left, the off hand; 18 on the backpack), read through the can-use routine's saved BP |
| casting though hit | Battle Mage | a hit's damage marks its creature hit this round (`mov byte es:[si+0AFh],1`, 58733h, in the routine taking damage off; cleared at a round's start, 57621h), and a marked character can't choose a spell on the USE screen (892F3h, 55898h) and has a queued one dropped (8991Bh): `PROBE_HIT_ROUND` (`INT ADh`, new) doesn't mark a Battle Mage |
| two spells in a turn | Arcanist (preserver spells, in a fight) | a spell aimed on the map ends the caster's turn in two ways: the routine casting it marks the caster as a hit does (845F0h; so no spell is offered again), and the routine finishing any use of what the USE screen armed (720F4h: it takes the slot or the item's charge; `DS:[54FBh]` the kind, 0 a wizard spell from a slot, `[54FCh]` the party member) asks the fight's routine that sets a combatant's actions (59256h) for none, as do the routines that cast, from their own code segments. A spell on a party member from the USE screen does neither (the game's own: the turn goes on). `PROBE_CAST_MARK` (`INT 96h`, new) doesn't mark an Arcanist for its first preserver spell of the turn; `PROBE_CAST_DONE` (`INT 94h`, new: the finishing routine's `cmp word es:[19h],0`, 722AFh) counts its preserver spells (`ARC_CASTS`) and sets `ARC_HOLD` for the first; `PROBE_END_TURN` (`INT 93h`, new: `mov si,[bp+8]`, 5925Dh) then returns at once when ending that member's turn is asked from another code segment (the fight's own routines, a turn ended from the combat menu among them, ask from its own), till the map's main loop runs again (`PROBE_SCROLL`) or a turn starts; `PROBE_ROUND_MARK` (`INT 95h`, new: the turn's start clearing the mark, 57621h) clears the count. Checked in the game: two Magic Missiles in a turn, the second marking it and ending the turn; ended from the combat menu after one |
| THAC0 | Swashbuckler, Crusader, Battle Mage, Mind Warrior (a warrior's: 21 less the level, where better), Scholar (1 worse) | `PROBE_THAC0` (`INT B7h`, new: the end of the game's THAC0 routine, `mov ax,14h / sub ax,si` at DSUN.EXE 876BBh, which every write of a creature's THAC0, `+1Fh`, uses: on making a character, 66CE0h, and at a level up, 86D7Eh and 87A91h) |
| initiative | Sentinel; Military Scout (its `KIT_OUTDOORS` bit); Myrmidon (2 less) | `PROBE_INIT` (`INT B8h`, new: the round's 20 added at DSUN.EXE 5750Eh) |
| to hit with a missile | Military Scout (a bow, sling or staff sling, its `KIT_OUTDOORS` bit) | `KIT_TO_HIT` in `PROBE_ATTACKS` (`kits.missile_to_hit`) |
| a hit's poison | Poisoner (every melee weapon hit; the header's +360, `KIT_SHOT`, once a fight up to 2.10.0, now bit N party member N's last weapon attack a shot or a throw: set or cleared by `NOTE_SHOT` in `PROBE_ATTACKS`, from the weapon attack routine's `[BP+16h]`, above 1 for a missile) | `PROBE_POISON` (`INT 86h`, new: the `jmp 7A7C5h` at DSUN.EXE 7A6DDh, in the routine giving a hit's special effects, 7A539h, where a person who isn't a thri-kreen has none; DI the attacker, SI the target, `[BP-6]` the attacker's creature, `[BP+12h]` the spell or power behind the damage, -1 for a weapon's): for a melee weapon hit only (`KIT_SHOT`'s bit clear; the poison's own damage, power 176, comes back through this routine with the Poisoner as its attacker, and would poison again, hit after hit) it queues power 176, the monsters' "poison (10 damage)", through the routine a monster's poisoned hit uses (790D2h: target, attacker, power, level; the level from 508:2Ah, whose far call is at 7A7ACh), then jumps on. The game rolls the save (paralysis/poison/death) and deals the damage |
| an arrow's plus | Spellarcher (1 better, at least +1, from a bow) | `PROBE_ARROW` (`INT 85h`, new: `mov es:[0006h],al`, DSUN.EXE 58D27h, in the routine finding a missile weapon's ammunition, 58C8Fh, `[BP+0Ch]` the weapon's type): `ES:[6]` is the plus the shot's damage adds (58992h) and its +1/+2/+3 damage kinds take where better than the bow's (581C4h). The shooter is `WHOSE_TURN`'s combatant; `kits.arrow_plus`. The weapon spec: `KINDS_ALLOWED` gives a Spellarcher the bow only, the one weapon spec the window after DONE offers it |
| a priest spell's level | Spirit Caller, Wasteland Seer (2 more under the open sky, 1 less under a roof, no less than 1) | `PROBE_SPELL_LEVEL`'s `SKY_LEVEL` (`kits.sky_level`): the level a spell's duration and damage take, not the levels it may cast |
| saves | Myrmidon (charms), Sentinel (spells, 0-137), Wanderer (fire and cold: the spell record's `+1Ah`, 2 or 4, as the game's Resist Fire and Resist Cold read it) | `PROBE_RING_SAVE` (the modifier routine's start: `KIT_SAVE`) |
| a spell's damage | Wanderer (half of a spell all fire or all cold, as Resist Fire and Resist Cold) | `WANDER_DMG` (an `NS_IMAGE` site: "test [bp+0Ch],di" at DSUN.EXE 7B56Fh, in the routine giving the share of a spell's damage a creature takes, 7B492h, where DI holds the kinds its effects guard it from; fire and cold added for a Wanderer); `GameData.damage_halved_by` |
| thief skills | Assassin (pick pockets, open locks), Swashbuckler (all), Shadowblade, Ghetto Fighter, Wayfinder (`KIT_SKILLS`, a signed byte a skill), Military Scout (+10 or −5 by its `KIT_OUTDOORS` bit) | `PROBE_BELT` (the thief skill routine's end: `KIT_SKILL`, no lower than 0) |
| from behind, backstab | Military Scout (a backstab taken back: `[BP-24h]` cleared, its 2 to hit with it), Rescuer (from behind +1, not +2); Assassin (a backstab's multiplier one more, x3 to x6: `STAB_TIMES`, `kits.backstab_times`) | `PROBE_STEALTH`'s `KIT_REAR` (`kits.backstabs`, `kits.rear_to_hit`), after the game's own setting of `[BP-1Ah]` and `[BP-24h]` and the stealth rule's; the backstab flag is pushed for the attack after it (DSUN.EXE 5838Ah) |
| initiative, Move in a fight | Wayfinder (Path-finder: each party member 1 more while a Wayfinder of the party is New or Okay, `PATH_UP`; 1 less while one is down and none up, `PATH_DOWN`) | `PROBE_INIT`, `KIT_MOVE`; `GameData.path_finder`, `GameData.path_lost` |
| shields | Shadowblade, Ghetto Fighter, Rescuer | `KIT_FORBIDS` (`kits.forbids`) |
| light armour only | Assassin, Shinobi, Shadowblade, Poisoner, Spellarcher (asleep too) | `KIT_LIGHT` (`kits.LIGHT_KITS`) |
| hiding, moving silently | Stalker, Assassin and Military Scout (not halved in daylight: `kits.not_halved_by_sun`), Wilderness Avenger (a ranger's, 5 a level of its best class), Shadowblade (hides with an enemy beside it) | the stealth rule's rolls (`stealth.py`, `GameData.ranger_skill_parts`) |
| the two-weapon penalty | Twin-blade, Battle Dancer (in light armour: `HEAVY_WORN`); Justifier (in any armour); Ghetto Fighter (2 less in each hand) | `PROBE_TWO`; `RG_TWO` |
| gear allowed | Ravager, Twin-blade, Brute, Stalker, Grove Warden, Lifebinder, Shinobi, Battle Dancer (no shield; `kit_dancer`: long sword and bow kinds), Shadowblade, Ghetto Fighter and Rescuer (no shield), Seeker (its sphere's weapons, as a cleric's: `SPHERE_ALLOWS` with `CU_*` set from the item type, its sphere the ranger class less 13; the bow kept) | `PROBE_CAN_USE` and `KINDS_ALLOWED` (`KIT_FORBIDS`: `restrict.kit_forbids`; and `KIT_ALLOWS`, so a Battle Dancer may specialize in the long sword whatever its cleric's sphere), whatever the class restrictions. For an EXIT on the weapon window after DONE, `weaponchoice.kinds_for` makes a Ghetto Fighter's or Poisoner's spec the dagger and a Battle Dancer's the long sword, if allowed (`kits.default_kind`); `weaponchoice._ghetto_dagger` puts a dagger in a Ghetto Fighter's hand |
| skill with a weapon | Justifier (expertise, the bow's and its chosen weapon type's, becomes specialization) | `SPEC_OF_SHEET`'s end: `SPEC_EXPERT` made `SPEC_SPECIAL` for a Justifier; `specialize.skill` |
| weapon specs | Myrmidon (two, the second to grand mastery), Brute (no missile spec), Battle Mage (one, of `KIT_BM_KINDS`: expertise), Spellarcher (the bow only), Poisoner (the dagger or short sword only: `KIT_POISON_KINDS`), Crusader and Mind Warrior (one, of its class's melee kinds: `KIT_MELEE_KINDS`; a thri-kreen Mind Warrior the chatkcha too, `KIT_KREEN_KINDS`, the race byte +18h, `kits.KREEN_WARRIOR_KINDS`) | `SPEC_OF_SHEET` (a Battle Mage's chosen weapon type `SPEC_EXPERT`), `KIT_FORBIDS`, `KINDS_ALLOWED` (a Battle Mage its own weapon types, whatever its class), `LV_DUE` (a Battle Mage one, a Myrmidon being made two), so DONE's weapon window (`CR_WEAPONS`) asks a Battle Mage as it asks a warrior |
| attacks a round | Wild Fury (Wild Fighting passed: 1 more in melee, `WILD_HALVES`, in `PROBE_ATTACKS` before the off hand's cap; not on the DAM lines); Battle Mage (its chosen weapon type: expertise, 3/2, 2 from 7th preserver level); Crusader and Mind Warrior (a warrior's extra attacks in melee, 3/2 from 7th level of the kit's class (2 from 13th, past the level cap), weapon specialization on or off) | `EXPERT_HALVES` where `PROBE_ATTACKS`, `PROBE_DAM_LINE` and `PROBE_VIEW_DAM` leave a non-warrior's (2 halves or fewer) alone; `specialize.expert_attacks`. `WAR_KIT_HALVES` in the same three probes, after the rest (`WAR_KIT_OF` in `PROBE_ATTACKS`, not for a missile: `[BP+16h]` above 1, or in View Character a type's `+0` bit 2); `kits.warrior_attacks`, which `GameData.weapon_hits` gives the party view. Checked in the game: the DAM lines 1.5× for a 7th-level Crusader and Mind Warrior, 2× at 13th, 1× at 6th and for a Mind Bender; in a fight a 7th-level Crusader with a club in each hand attacked 1+1 and 2+2 in turn before the off hand's cap (see [Two weapons](#two-weapons)) |
| gear the kit allows | Battle Mage (its chosen weapon type's weapons, with weapon specialization; light armour); Battle Dancer (long swords and bows, `kit_dancer`, whatever its cleric's sphere) | `KIT_ALLOWS` in `PROBE_CAN_USE`: an item the game's class mask refuses is let through (AX 1), and the class restrictions pass it; `KIT_FORBIDS` still holds (nothing in a Battle Mage's off hand). `kits.allows`, `restrict.kit_allows`. The game has no armour rule for a single class's spells, so it casts in that armour |
| hit die | Battle Mage (d6), Arcanist (d3) | a level's die: `PROBE_HIT_DIE` (`INT A5h`, new: `mov al,es:[bx+0]`, 87308h, the die read from the class's hit point group in the routine rolling a level's hit points, 87250h, which both a level up and the creation screen call; `[BP-4]` the sheet). The creation screen's range (the least and most hit points it allows, `DS:[4998h]` and `[4996h]`, worked out with the rolls by 655D6h): `PROBE_CR_DIE` (`INT A3h`, new: `mov al,es:[bx+14Ah]`, 65677h, the die from its table by creation class). `kits.hit_die` |
| max PSP | Mind Warrior (a tenth fewer, rounded down) | at a level up: `PROBE_MAX_PSP` (`INT A4h`, new: `les bx,[bp-8]`, 8748Fh, the sum in SI before it goes in the sheet, in the routine at 873B2h); on the creation screen: `PROBE_CR_PSP` (`INT A2h`, new: the end, `pop bp / retf`, of 65B39h, which sums the PSP into the sheet being made's `+0Ch`; it drops the interrupt frame to end the routine itself, putting the flags back first, as a score's click reaches it with nothing after to set IF again). `kits.max_psp` |

The creation screen rolls the hit points and works out the PSP when a class
is clicked, before a kit can be chosen. Choosing or taking back a Battle
Mage, Mind Warrior or Arcanist on the KIT page (`KIT_ROW`) has `KIT_REROLL`
call the game's own routines again (655D6h with its roll flag, then 65B39h,
through the creation overlay's stub 422Eh, entries 66h and 6Bh), keep the
hit points in the range, put both on the creature and show them again
(64C6Bh and 64CEDh, through the panel's own stub, after A0:30C3h puts the
numbers' backdrop back; its far address and the backdrop words' segment are
read from the panel overlay's code, `WP_HARVEST`). It runs at the end of the
sphere click probe, once its way back is set, so the overlay manager can fix
up the frame if loading the other overlay moves the panel's. 655D6h copies
the sheet being made to the party's sheet (66AC4h) before its rolls, so the
kit byte goes with it; a kit left from the classes before a click on a class
(`PROBE_WP_CLASS` clears it only after the click's rolls) is cleared first
(`KIT_STALE`), so the class's own die is rolled.

The Elementalist's second sphere is the sheet's `+45h` (`SPHERE2`: 0 none,
else the sphere + 1), free since the Arcanist's CON change went. The game
gives each class a mask (load + 3800h, `+118h`, a dword a class: 1 wizard, 2
priest, then a bit a class, 4 the air cleric to 20h the water cleric) and each
spell one (load + 3FB9h, `+19Dh`, 7 bytes a spell); a class casts the spells
whose masks meet its:

| Effect | Kits | Where |
|---|---|---|
| priest spells known | Elementalist (its second sphere's too), Healer (the cosmos's: the spells every druid has, by its element's druid's bit, `HEALER_COSMOS`; a Healer from 2.5.0 or earlier has them marked by the Loader, `kits.cosmos_spells`, the low four bits of its byte in the known table at `DS:132Ah` set to 1 as the game's loop does) | the loops that mark each priest spell (45h-89h) known or not for a party member by the class's bit, on making a character (66F89h) and when a human changes class (86E1Eh, in the DUAL routine at 86C80h; a level up marks none, as a priest knows its spheres' spells of every level from the start): `PROBE_EL_KNOW` (`INT 9Eh`, new: `test dword es:[bx+19Dh],eax`, 66FC9h and 86E56h; its flags back to the JZ with `RETF 2`) adds the second sphere's cleric bit, and for a Healer whose cleric's bit it is, its element's druid's (2 << (class + 4)): a water druid's spells are a water cleric's and the cosmos's. And the routine giving a priest its spheres' spells (5E401h, no caller found): `PROBE_EL_GRANT` (`INT A1h`, new: `xor si,si`, 5E489h) adds them to its mask |
| a kit asleep after dual-classing | every kit | the routine that changes a human's class (86C80h, DUAL on a portrait's menu: 70EF1h opens its window, 86B3Fh, for a human of 2nd level or more) moves the classes down and puts the new one first. The kit byte (`+43h`) has two bits for each class (0 none, 1-3), the first class's lowest and each class taken after it the next two, so a kit stays with its class however the classes move: `KIT_PLACE` gives the oldest class's place (0 for one class; 1 or 2 for a human; 0 for a multiclass group's, none for another multiclass), `KIT_AT` the kit of the class at a place, `KIT_AWAKE` holds a kit asleep until the level at `+24h` passes its class's (as the game counts earlier classes; the class it has now is always awake). `KIT_IS` finds a kit only while awake and `KIT_HAS` either way. The byte's 0FFh (`KIT_OPEN`, on the creation panel) is no kit. The kit's own levels come from `KIT_LEVEL` (Ravager and Grove Warden AC, the warrior THAC0, the Seeker's and Justifier's slots, the Shinobi's casting and spell picks, the Battle Mage's 7th-level expertise) and its class from `KIT_CLASS_OF_SHEET` (a Seeker's sphere, an Elementalist's cleric); `PROBE_SLOT_LEVEL` puts an Elementalist's slots behind for its own class's place only (`KIT_AT` there). `PROBE_HIT_DIE` gives a kit's die only for one class (a human who changed class rolls for its new one); `PROBE_MAX_PSP` takes a Mind Warrior's tenth with `KIT_HAS`, as a sleeping psionicist class still gives its PSP. `SPEC_OF_SHEET` treats a dual-classed Battle Mage's weapon spec as the kit's (none asleep, expertise awake), not a new warrior class's. The Effects screen has a `KIT:` line for each kit, the oldest class's first, ` (ASLEEP)` after one asleep (`KIT_AT`, `KIT_OF_SHEET` with `KIT_SHORT`'s shorter names, `KIT_LINE_ASLEEP`, `KIT_AWAKE`); see the next section for its pages. `kitpages.kit_place`, `kit_at`, `kit_awake`, `kits_of`, `kit_ids`, `kit_level`, `kit_class_of` are the Loader's |
| classes barred to a dual-classing human | Seeker, Justifier (cleric); Shinobi (preserver); Swashbuckler, Crusader, Battle Mage, Mind Warrior (fighter, gladiator, ranger); Arena Champion, Sentinel (druid, preserver: no shield); Brute (psionicist, air cleric: no two-handed melee weapon); Stalker (thief: its hiding on a thief's own); Grove Warden (gladiator: its AC on a gladiator's own); Healer (the rangers of air, earth and fire: water's sphere only; the game already keeps a priest from the other priest class, and a ranger, who must be good, from the druid, who must be neutral, so `DUAL_BANS`' clerics and druids there and the Seeker's and Justifier's druids never come up) | the DUAL window (866C7h) asks of each class (SI, 1-17) whether member [BP+6] may change to it (86E94h: AX 1 if so; human, prime requisites) and greys the rows answered no (a row with elements, cleric, druid or ranger, stays open while any of its four classes is allowed; the element is then picked on the game's three-choice menu, 86BBBh: its title the air row, DS:30A5h, then earth, fire and water, AX 0 to 3 added to the row's first class. For a Healer `DUAL_SPHERES`, called by `PROBE_DUAL_BAN`, makes that menu WATER ONLY, no other row, and `PROBE_SPHERE`, `INT FFh` over the `cmp ax,1` after it, 86BC3h, makes its answer water; checked in the game: a water-cleric Healer to ranger, a water ranger; a fire ranger to water cleric, no Healer on the KIT menu): `PROBE_DUAL_BAN` (`INT 9Dh`, new: the `or ax,ax` after the call, 866FFh; its flags back to the JZ with `RETF 2`) answers no for a class one of its kits bars (each `KIT_AT`, asleep too; `KIT_BANS`), from `DUAL_BANS` (a kit's number, then a dword of class bits; `kits.DUAL_BANS`). The slot kits' tables (`PROBE_SLOTS`) replace the whole count for their kind of magic, so they would take a new cleric's, druid's or preserver's slots' place |
| a new preserver's spells, on changing class | every human (not a kit's) | the routine that changes a human's class, for a preserver (86DB5h), takes away its wizard spells and marks Grease (8) and Magic Missile (7) known: `PROBE_DUAL_SPELLS` (`INT 9Ch`, new: those two `push / push si / call 500:43h / add sp,4`, 22 bytes from 86DE4h) calls CHOOSE A SPELL (620:5Ch, 85560h: the level up's) twice in their place, through its stub (`PICK_STUB`: DS less 4Ch, as `WP_STUB`), with the spell levels on offer up to 1st (`PICK_CAP`, which `PROBE_PICK_LEVEL` heeds). The dual routine is in CHOOSE A SPELL's own overlay (85560h to 87250h), so the call can't unload the code it returns to. The same call from another overlay needs its way back where the overlay manager can patch it: see the next row |
| a new preserver's spells, at creation | every preserver | the creation screen's DONE (overlay 65480h) marks spells known by preserver level (`[BP-2]`, 66F2Dh on: 7 and 8 at 1st; 9 and 0Bh too at 2nd; 0Fh and 16h too at 3rd). `PROBE_CR_SPELLS` (`INT 98h`, new: `mov ax,[bp-2]`, 3 bytes) has a character made on the creation screen (the grants called from DONE, 66556h: their way back at `[BP+2]`, `[BP+4]` is the INT's less `CR_FROM_DONE`, in the same overlay; START GAME with no party made calls them for the game's own party from 65480h+6FBh, which keeps the game's spells, and the creature's status can't tell the two, Okay in both) pick as many on CHOOSE A SPELL (`PICK_SPELLS`: 2, 4, or 4 and two of 2nd level; a Scholar's one more a level, `KIT_MADE`) and goes on past them (66F83h, `CR_SPELLS_PAST`). CHOOSE A SPELL returns nothing; EXIT leaves it with no spell learnt, which `PICK_SPELLS` tells by counting the member's known preserver spells before and after (`PICK_KNOWN`, the low four bits of each byte from `KNOWN_OFF`, as 500:43h sets them; the party's four only, creation's and DUAL's among them). Then the picks end and `PICK_FILL` marks the game's own spells known for those left, in its order, less any known (`fill_first`, `fill_second`). DONE's routine (6649Ch) has saved the character to its slot and opened its files (550:57h) before the grants, so going back to the creation screen from here isn't done. CHOOSE A SPELL is another overlay, whose loading may put the creation code out: without care the game is lost on the way back. The INT's way back is pushed as a stack frame (`push cs / push ip / push bp / mov bp,sp`) that the overlay manager walks and patches to reload the code first, as `PROBE_LV_PICK` and `PROBE_DUAL_KIT` do, and read back after |
| sound numbers on the sheet | every character | the game reads a word at sheet `+42h` (78FDAh, `mov dx,[es:bx+42h]`: a sound to play, 4 if 0) and at `+44h` (81DE3h, `mov ax,[es:bx+44h]`: played if not 0), and the kit byte (`+43h`) and second sphere (`+45h`) are their high bytes, 0 in every one of the game's sheets: `PROBE_SOUND_42` and `PROBE_SOUND_44` (`INT 9Bh`, `INT 9Ah`, new, 4 bytes each) read the low byte alone (`movzx`) |
| a kit for a dual-classing human's new class | every kit | in the routine that changes a human's class (86C80h), once the classes have moved down and the new one (`[BP+8]`) is first: `PROBE_DUAL_KIT` (`INT 99h`, new: `cmp word [bp+8],0Ch`, 4 bytes at 86D90h; the compare done after, its flags back with `RETF 2`) shows the game's three-choice menu, the one the DUAL window asks a cleric's sphere on (4D0:25h, overlay 54D90h: its stub 41B4h, `DK_STUB` from DS; arguments x, y, a far title, 1, three far rows; it returns the row clicked, 1-3, else 0, and leaves an empty row out). Title `KIT: NONE`, rows the new class's kits (`KIT_NAME_PTR` into `KIT_NAMES`); a kit `DK_BANNED` bars an empty row: its `DUAL_BANS` hold one of the other classes, or it and one of their kits are a `KIT_PAIRS` pair (`kits.dual_kit_banned`, `KIT_PAIRS`). The kit goes in the kit byte's bits for place 0 (`KIT_PLACE` × 2 up). An Elementalist's second sphere (`SPHERE2`) on the menu again (`DK_SECOND`: the three spheres not the cleric's), before the routine marks the spheres' spells known (`PROBE_EL_KNOW` takes it in). Then, with weapon specialization, `LV_CHECK` (the level up's weapon kinds, through the psionicists' pop-up, 620:57h: `PICK_STUB`'s entry 57h). The menu is another overlay, so the INT's way back is put in a stack frame the overlay manager walks and patches (`push cs / push ip / push bp / mov bp,sp`, as `PROBE_LV_PICK`), and read back from it after. `PROBE_DUAL_SPELLS` gives three picks, not two, when the kit taken for the new preserver class is the Scholar |
| starting gear fitted to the kit | Ravager, Brute, Shinobi, Seeker (a forbidden hand item), Shadowblade, Ghetto Fighter, Rescuer (the shield left behind), Arena Champion (a shield), Ghetto Fighter (a dagger in hand: `_ghetto_dagger`), Poisoner (one of its weapon spec in each hand, the dagger or the short sword: `_poisoner_daggers`), Battle Mage (its weapon spec's weapon), Battle Dancer (a second long sword in the left hand in place of the shield, `_kit_second_weapon`, and a bow and arrows, with fuller starting gear: `startgear.py`); Myrmidon (its second weapon spec's weapon in the left hand in place of the shield, if one-handed and for melee) | the game gives a new character its class's gear when DONE is clicked (the README's table, seen in play). The dice log's `weaponchoice.kit_gear` (after `finish_new`, with the rule for kits; New characters only), for a hand's item `restrict.kit_forbids` forbids (the off hand as such): a weapon in the right hand becomes a plain one (`plain_weapon`) of the first kind it may use and the kit allows, the character's chosen kinds first, then `REPLACE_ORDER` (the long sword's neighbours: short sword, axe, mace, great axe, gythka, polearm), then any; a two-handed one sends the off hand's item to the backpack (`_shield_off`); a shield is taken away (`ring.unlink`: out of its list, its record back on the game's free list), anything else goes to a backpack cell (if the shield can't be unlinked, it too). An Arena Champion with no shield has its off-hand item made the game's starting shield (`SHIELD`: type 4, name 05h, picture FC04h, price 10). A Battle Mage with weapon specialization and no weapon of its chosen kind has its right hand's item (the quarterstaff) made one (`start_weapon`). Each change leaves nothing to change again |
| caster level, a spell's level | Elementalist, Healer | the caster level routine (81B16h: the spell levels it casts, Dispel Magic) and the effect level routine (5E25Ch: durations and damage) count a class whose mask meets the spell's: `PROBE_EL_CAST` (`INT A0h`, new: `mov edx,es:[si+19Dh]`, 81B42h) and `PROBE_EL_LEVEL` (`INT 9Fh`, new: `mov ebx,es:[bx+19Dh]`, 5E375h) give a spell of its second sphere its own cleric's bit too, and a Healer a spell of its element's druid (`HEALER_COSMOS`); `kits.spell_spheres`, `GameData.effect_caster_level` |
| weapons | Elementalist (its second sphere's as well as its own) | `CLASS_FORBIDS`'s cleric spheres (`EL_SECOND`), and `KINDS_ALLOWED` through it; `restrict.elementalist_sphere` |
| choosing it | Elementalist, Healer | the creation panel's spheres (the game's, drawn from a mask by 63FEEh, `DS:4982h` its own sphere's row): `WP_CLICK` sends a click on a sphere's row to `EL_CLICK`, which takes or takes back the second (the game's mask left alone) and has `EL_MARKS` draw both marked and every row in use; `PROBE_WP_CLASS` (after every click) draws them so again over the game's own drawing (`EL_REMARK`). A Healer's row on the KIT page is greyed and does nothing unless the sphere marked is water (`HEALER_BARRED`: `WP_SPHERE_MASK` 10h, as the page is opened from the spheres; `KIT_MARKS`, `KIT_ROW`), and while one is taken a click on a sphere's row takes it back (`EL_CLICK`: the sheet's kit byte `KIT_OPEN`, the click the game's); after DUAL, `DK_BANNED` leaves it off the menu for a cleric not of water (`kits.dual_kit_banned`) |

Every kit also needs its Python side: the Characters tab and the in-game
THAC0 and saves (`game.py`), the dice log's lines, and tests that hold the
helper's code (emulated) to the Python.

#### How they're checked

Each kit's helper code is held to its Python by emulated tests
(`tests/test_dsclog.py` runs the helper's routines in a CPU emulator), and
each was played in the game: the creation screen's KIT page and hit dice, the
level ups (Shinobi and Scholar spells, Seeker slots), the KIT menu after DUAL
with its bans, and the Effects screen's pages.

### Level cap by XP

([In the features page](FEATURES.md#level-cap-by-xp).)

How: the game holds a class level against 9 in two places, where a character
goes up a level (87BE6h: the class's slot in DI, then `JL`) and where View
Character shows the XP for the next one (67D08h: its copy of the sheet, the
slot in DX, then `JZ`). While the rule is on the helper's `PROBE_LEVEL`
(`INT E7h`) answers instead from `LEVEL_ROOM`: the next level's XP, from the
game's table (`XP_NEED`, AD&D's with the class tables rule), against the
class's share of `XP_CAP` (749,999), flags as "cmp 0,1" below it and "cmp 9,9"
at it. It tells the two places apart by the byte 3 past its return (7Ch, the
level up's `JL`), and finds the game's XP table, and at the level up its map
from the sheet's classes (1-17) to the table's rows (1-8, at +0CAh), from the
code's own `mov ax,seg` immediates (View Character's copy numbers its classes
by row already). The share: the whole cap for one class; for a character of
several (not human) the cap divided between them, as the game divides its XP;
for a human, the cap less what its old classes' levels needed (the slots after
the first: the game's change of class, 86C80h, moves the old classes down,
puts the new one first at 1st level and sets the sheet's XP to 0).
`PROBE_XP_NEXT` names a class in View Character's brackets by the same test.
The XP table has AD&D's levels to 14th (`ADND_XP`), the slots to 12th
(`ADND_SLOTS`), the thief skills to 13th (`THIEF_TABLE`); `PROBE_PICK_LEVEL`
keeps CHOOSE A SPELL at 5th and below (`WIZ_LEVEL_MOST`). Checked in the
game: a gladiator at 700,000 XP went to 10th and no further; a thri-kreen
fighter/druid/psionicist at 300,000 to 8/11/9; a human preserver who had been
a 3rd-level gladiator, at 760,000, to 11th; an elf preserver/druid/thief at
300,000 to 9/11/11.

### STORE and RECALL on the creation screen

([In the features page](FEATURES.md#store-and-recall-on-the-creation-screen).)

With the `roll_store` switch off, the launcher leaves both out: the buttons from
its copy of `RESOURCE.GFF` (`icons.write_resources`) and the click's patch from
its copy of `DSUN.EXE` (`gamepatch.ROLL_STORE`, as `EFFECTS_KEPT`).

The buttons: the creation screen is window 3011 in `RESOURCE.GFF`, its buttons
the die (7DAh), EXIT (80Ah), DONE (7D0h) and the rest. In the Loader's copy
(`dsloader/rollstore.py`) it has two more, STORE (8A0h) and RECALL (8A1h),
under the hit points and PSP, after its own items (the name box, an `EBOX`,
among them). Their pictures are the game's carved stone buttons: a blank cut
from DELETE's bevel and face, and letters taken from SAVE, LOAD, DROP and
DELETE (SAVE's and LOAD's letters touch, and are cut where the ink is
thinnest). No button has a C, so it is drawn in the same three tones as the O
(`C_SHAPE`). The game's third frame is out of use on some buttons and lit on
others; these have their first again.

The click: the screen's click routine (its overlay from 65480h) looks the
button up in a table of its 22 (`mov cx,16h`, 6625Dh). `PROBE_RS_CLICK`
(`INT 8Ah`) does the `mov` and, for STORE or RECALL, its work, then sends the
routine on as for a button not its own (to 66377h: nothing more). A roll is
what the die writes (657BBh): the sheet's hit points, hit points rolled and
most PSP (`+8`, `+0Ah`, `+0Ch` of DS:119Ch), the creature's hit points, PSP
and six scores (`+0`, `+2`, `+22h` of DS:11A0h), the least and most hit points
the classes could roll (DS:4996h), and the die's total (`RL_POOL`). STORE
keeps those with the sheet's race, sex, classes and kit (`+18h`, `+19h`,
`+21h` to `+23h`, `+43h`); at each button pressed the probe forgets the stored
roll if those have changed (`RS_SAME`), so RECALL finds none. RECALL then
shows them as the game would: the scores through the screen's own redraw (the
creation overlay's stub, entry BBh, which a score's click calls; `RL_SUM` adds
the totals), and the rest by running the die's routine from where it has
rolled the hit points (659D0h, with its stack frame and DI 1): the hit points
shown, the PSP worked out again (65B39h, which rolls nothing) and shown, then
the AC and damage. The overlay's segment is the INT's return.

### Fuller starting gear

([In the features page](FEATURES.md#fuller-starting-gear).)

`dsloader/startgear.py`'s `fill`, from the dice log after
`weaponchoice.finish_new`, `class_gear` and `kit_gear` (the `starting_gear`
switch, a Python-only one as `pickpockets` is: `launch.SWITCH_DEFAULTS`,
`DiceLog.starting_gear`), for each party member whose status is New and who
has items (the game gives a character its gear when DONE is clicked; before
that it has none). What a character "can use" (`can_use`) is the game's class
lists (or `restrict.kit_allows`) and, with the class restrictions on,
`restrict.usable`; never what `restrict.kit_forbids`. In order:

- with the class restrictions, a multiclass preserver's (`preserver_bare`: not
  a human, two classes or more, one of them preserver) worn armour
  (`restrict.is_armour`: not its shield) is left out (`ring.unlink`);
- an empty right hand gets a usable melee weapon from the backpack (cells 14
  and up), else a plain weapon (`weaponchoice.plain_weapon` on the game's
  bone long sword record, `WEAPON`) of the first kind with a usable type in
  `PLAIN` or `OTHERS`: the sheet's chosen kinds (not missile ones), then
  `HAND_ORDER` (short sword, club, mace, dagger, quarterstaff, chatkcha) or,
  for a cleric, `CLERIC_HAND_ORDER` (club, mace, dagger, short sword,
  quarterstaff, chatkcha); not one taking both hands with the left hand full.
  The game's own lists give an air cleric no melee weapon (its dagger types'
  class masks leave the air cleric's bit out), so it gets the chatkcha (type
  48, thrown);
- no bow, sling or staff sling: a sling (type 64) to the missile slot, else
  an obsidian chatkcha (48) to the backpack;
- the chest, arm and leg slots, if free and the character has no item of the
  type: the game's leather chest, arm and leg armour (SEGOBJEX templates: types
  6, 7, 8; names 07h, 08h, 09h; pictures FC02h, FC01h, FBFEh), not for a
  multiclass preserver with the class restrictions;
- the cloak slot, with kits on, for a Stalker, an Assassin or a Shinobi
  (`CLOAK_KITS`): the plain cloak (type 65, name 0Eh, picture FBE3h).

Items are made by `npcitems.add_to` (a worn slot only when it's free; in the
worn list or the backpack's, as the slot is), and moved with
`pickpocket.place`. Each step is skipped once its item or kind is there, so
`fill` leaves nothing to do the next time; one line for the log lists what it
gave. `fill_member` gives a thri-kreen (race 8, `THRI_KREEN`) nothing, and
does one character whatever its status: the game's own party (already Okay)
gets it through `defaultparty.ready`'s last step, `gear`.

### The game's own party

([In the features page](FEATURES.md#the-games-own-party).)

How: the four are objects in `SEGOBJEX.GFF` (32000 to 32003, and 300, 307, 308
and 313 for their figures), a creature record and a sheet each, already Okay
and with no items; the game gives them their gear and spells as it starts. So
the Loader (`dsloader/defaultparty.py`) changes them in memory while the game
is new (its first hour, in the arena: `tools.NEW_GAME`), each change once,
knowing each by name, race and classes together: their weapon kinds in the
sheet's spare bytes, Gerakis's club item made a bone gythka in its place,
Cilla's plain armour given back to the free item list (her chest armour is
alone in its list, which is left empty, as a new list is), and her byte for
spell 0 set in the known-spells table, and with kits Cermak's kit byte
(`+43h`) the Arcanist for his preserver class (place 0; his gladiator class,
place 1, none), and with fuller starting gear, last, `startgear.fill_member`
for each. Seen in play: Cilla's USE screen lists ARMOR among her 1st-level
spells and her inventory has no chest armour (AC 5); Gerakis holds the gythka
and the long sword; the dice log lists each one's added gear (Gerakis a sling
and leather chest and leg armour; Cermak, Cilla and K'ratchek nothing).

Their features of their own (with kits: `set_own`) go by a bit no character
made on the creation screen has: the kit byte's bit 6 (`kits.OWN_BIT`, DSCLOG's
`OWN_BIT`; bits 0 to 5 are the classes' kits, two each, and bit 7 Friends
known; every reader of a kit masks its own two bits), and which feature by the
race (`OWN_RACE_B`, `kits.own_race`; with `RULE_HI_KITS` only). Gerakis (the
half-giant): Wild Fighting, `wild.py` rolling for him as for a Wild Fury
(`kits.wild_fighter`), DSCLOG's effects going by the `KIT_WILD` bits alone.
K'ratchek (the thri-kreen): `SKY_LEVEL` as a Wasteland Seer's (`CR_OWN_RACE`),
and `OWN_THROWS` in `PROBE_ATTACKS` (and the inventory's `PROBE_MISSILE_LINE`)
2 more halves a round with a chatkcha, whatever the specialization rule
(`GameData.weapon_hits` the same). Cilla (the elf): `stealth.py`'s hiding not
halved in daylight (`kits.not_halved_by_sun`, as an Assassin's and a Military
Scout's). The Effects screen's lines are `OWN_LINES` (after the kits', in
`EF_LINES_OF`); the Characters tab's `GameData.kit` adds `kits.OWN_FEATURES`.
Seen in play: the dice log's lines as the game starts, Gerakis's check
("needs 18 or less (CON 22 -4)"), Cilla's hiding at 50 in the arena, the four
Effects screens, K'ratchek's inventory line `Chatkcha 2.5x1D6+4` (1.5x before).

### The leader's CHA at shops

([In the features page](FEATURES.md#the-leaders-cha-at-shops); `prices.py`.)

The shop (overlay at 83000h) reads an item's price, the word at its `+6`,
straight from the item: `mov cx,es:[bx+6]` to charge it (8384Bh: times the
count for a stack, against the party's money, the dword at 2C0:357h; NO DEAL!,
DS:2EE7h, if short) and to show it under the item (83BB1h, as `%d$`), and
`movsx eax,word es:[bx+6]` where the list colours an item the party can't
afford (8310Ch). Selling (83CCAh) is left alone; 9999 there is "I COULDN'T
SELL THAT".

How (`RULE_HI_CHA_PRICES`, the second rules word's 16: `game.RULE_CHA_PRICES`):
`PROBE_PRICE` (`INT 8Dh`) at the first two and `PROBE_PRICE_EAX` (`INT 8Ch`)
at the third read the price and pass it through `CHA_PRICE`: the leader is
the party member at `DS:4979h` (whose turn it is; outside a fight, the
leader), its CHA its creature record's `+27h`; the price times (100 − 5 for
each point of CHA past 17, at most 40 at CHA 25) / 100, never below 1, and
9999 kept.

Checked in the game (with the table of the time, 25% at CHA 20): Kalzith's
scrolls showed 2,250, 4,500 and 6,750 (25% off 3,000, 6,000 and 9,000) and
each was charged that. A bought item stays on the pointer until it is put down
(the game's held item, `DS:17A0h`), and the shop takes no other click
meanwhile.

What a shop pays: `SELL_PRICE` (an `INT 98h` site, 83CCAh's `mov si,es:[bx+6]`,
ES:BX the item sold; the price shown in its offer and paid, times the count
for a stack) gives 60% of it (`SELL_PERCENT`; times 60 into DX:AX, divided by
100, rounded down, never below 1), with the same rule (`prices.sell_price`):
the best discount (40% off) rounds down the same way, so nothing bought sells
for more than it cost, and at CHA 25 the two are equal.

### Buying back magical items

([In the features page](FEATURES.md#buying-back-magical-items).)

The shop, once it has paid for the item sold, empties the item list of the
thing holding it (`push word [179Eh]` / `call 0A0h:1C94h` at 83D9Eh; the routine
does nothing for 270Fh), its items back on the free list. That thing is the
pointer's (`DS:179Eh`, 523: one of the few past the 520 objects), never freed:
with nothing held the game has it all zeros (kind 0). `SELL_KEEP` (an `INT 98h`
site over the push, `RULE_HI_BUYBACK`, the second rules word's 64:
`game.RULE_BUYBACK`) looks at the thing's first item (things table, kind 1) and,
for one with a plus (`+14h` above 0) or a power (`+0Fh`), pushes 270Fh in its
place (the registers kept, the interrupt's frame moved down a word, the word
under it) and queues the thing and the shop's merchant (`DS:179Ch`, the object
whose item lists the shop's list is built from at 8347Ah: Kalzith's map object,
229, a person, creature 33) in the header (`SOLD_SEQ` +308 counted, `SOLD_Q`
+310, four entries). The Loader (`buyback.py`, every quarter of a second) puts
each queued item first in the merchant's last item list (a new one if it has
none; a backpack cell of its own) and zeroes the pointer's thing, as the game
leaves it (left a list, even an empty one, the inventory screen picks nothing up
after); a merchant that isn't a person (none known) has the item freed as the
game would. Bought back, it costs its price less the CHA discount, at least 60%:
no less than the shop paid (the same at CHA 25). Checked with the emulator (both
sites), unit tests (the move) and in the game: a Shield scroll (price 3000) sold
to Kalzith for 1,800 went first in his stock at 3000, and a Cloak (24) sold for
14 was gone, the inventory screen picking things up as before.

### Thief skills from AD&D's table

([In the features page](FEATURES.md#thief-skills-from-adds-table).)

How: where the game's thief skill routine adds 4 a level, the helper
(`INT E4h`) puts AD&D's number for the level in place of the game's base and
level, adds the DEX table's, and jumps past the game's DEX formula to its
armour and effects. At the routine's end (`INT D9h`, below) the helper keeps
the chance to 95 (`THIEF_MOST`). The Loader's screens and the inventory
screen's panel work the chances out the same way.

### Hiding in shadows to backstab

([In the features page](FEATURES.md#hiding-in-shadows-to-backstab).)

How (the cloak, boots and belt): the patched game's item box (`INT DAh`, where
it has drawn the name) asks the helper, which draws the line with the game's
own text routine when the item's type is worn as a cloak, on the feet or as a
belt; and at the end of the game's thief skill routine (`INT D9h`, where it
returns the chance, armour and effects counted) the helper adds the belt's 5
to picking pockets and opening locks for a thief wearing one.

How (the rolls): the Loader rolls both when the turn passes to the thief and
tells the helper, which, where the game has just worked out whether an attack
is from behind and a backstab (`INT EAh`), makes the hidden thief's next one
so, by the game's own conditions for a backstab (a thief, in melee, a weapon
of weight 40 or less).

How many attacks: the attack routine multiplies when both backstab flags are set
and the round's count of attacks so far (`[BP-14h]`) is 1 or less (58A71h), so
the first two swings of the round, an off-hand one too. `STAB_TIMES` (with
`RULE_HI_BACKSTAB`) multiplies only when the count is 0; the dice log
(`dicelog`'s backstab line, `parent_local(-0x14)`) says the same.

### Spell arrows

([The Spellarcher](KITS.md#multiclass-kits); `spellarrows.py`.)

**The buttons.** Outside a fight, `PP_SHOW` gives a Spellarcher
(`KIT_SPELLARCHER` awake) a button in the USE screen's ability row for each
touch spell it knows (`ARROW_KNOWS`: the game's known table, `ARROW_SPELLS`:
Burning Hands, Chill Touch, Shocking Grasp, Vampiric Touch), as it gives a thief
Pick Pockets: the first where a priest's Turn Undead is (APFM 2BEFh), unless a
thief's purse or a priest's element has it, the rest in the row's spare places
to its right (2BE7h-2BEAh, `PP_EXTRAS`: each drawn with Turn Undead's frame and
handler, its icon loaded and let go of by the game's routines, `PP_CLOSE`
letting go of them all as the screen closes). Kind 2-5 (`PP_ARROWS`+N), icons
ICON 3049-3052 (`icons.arrow_spell_icon`: the touch spell's tile, the hand taken
off, an arrow in its lines), names BURNING ARROWS and so on (`PP_TEXT`),
descriptions by `PP_INFO` (each under the description box's 195 bytes). Let go
of, the screen closes as for the thief's, and `PP_ARM` goes to `ARROWS_ARM`:
nothing readied, then `ARROWS_ASK` in a frame the overlay manager can fix up,
which hands the click to the Loader as an item used on the map is (`USE_ITEM`
`ARROWS_BY` FE00h and the member, `USE_WHO` the spell's place). Made, the Loader
answers with no text and nothing is shown; refused (not known, no slot), its
words (`PICK_TEXT`) are.

**The Loader** (`SpellArrows.make`), with the Spellarcher's quiver empty (else
it says so and uses nothing), takes a slot of the touch spell's level from the
wizard slots left (`SLOTS_LEFT`; none left, it says so) and puts a stack of the
game's Arrows (type 62) in the quiver (`npcitems.add_to` with the ammunition
slot; `weaponchoice.bow_ahead` then puts the bow ahead of it in the list). The
stack is named Burning, Chill, Shocking or Vampiric Arrows (names 16Ch-16Fh),
their pictures objects 2614-2621 (the Arrows' icon, its heads in the spell's
colours), value 0, 5 a preserver level. Slots are the only limit. At a rest (a
script's REQUEST 1 or 4, `REQ_SITE`, as at a fire ring, or the vulture meal)
`vanish` gives every spell arrow back to the free list, wherever it is.

**Kept in the quiver.** The game keeps a Flame Blade, Spiritual Hammer or
Shillelagh (and a Graft Weapon's weapon) in the hand: the routine saying whether
the character on show may take an item out of an inventory slot (6F44Bh: SI the
slot, the item's +11h slot + 4; `[BP+8]` nonzero to say why not) asks for those
four effects and refuses the hand slots with "Item grafted on", and the equip
routine (6EF52h) refuses an item into a hand they hold the same way. Spell arrows
are kept the same way: `PROBE_TAKE` (`INT F7h`, new: the `jz` to that routine's
yes, 6F4B0h, where none of the four is up) refuses slot 5, the quiver, when it
holds spell arrows (`QUIVER_LOCKED`: the inventory's slot table, `DS:540Ch`, a
word a slot, names the entry in the character's list, `DS:541Ah` + 4 x the
character, 10 bytes each, +4 the item; the character on show at the segment the
routine's "mov ax,348h" gives, 6F454h), and `QUIVER_KEPT`, first in
`PROBE_CAN_USE`, refuses any item into such a quiver (the equip routine's
`[BP+8]` 5; its segment from 6EF6Ch), "Cannot use this item".

**The hit.** The weapon attack routine (5883Ah) casts only the weapon's own
spell on a hit (its item's +0Fh, the spell + 1, at 58B63h; cast by 598:89h with
the attacker as the caster and level 6 pushed for every weapon's spell, at 58BE6h:
`push 6 / mov al,cl / mov ah,0 / push ax`). `ARROW_LEVEL` (`NS_IMAGE+47`, over
those 7 bytes) keeps 6 for a weapon's own spell and gives a spell arrow's (`ARROW_HIT`
sets `ARROW_CAST`) the archer's preserver level (DI the attacker: class 11 among the
sheet's +21h-23h, its level from +24h-26h, at least 1), moving the INT's frame down
4 bytes to put the two words under it. `PROBE_ARROW` (58D27h, where the ammunition
routine keeps the arrows' plus) also keeps their name (`AMMO_NAME`); `ARROW_HIT`
(`NS_IMAGE+28`, over "cmp byte es:[bx+0Fh],0") gives a shot from a bow ([BP+16h]
above 1, a bow's type at [BP+14h]) with spell arrows their spell instead, when a
Spellarcher shot them (`PROBE_ARROW`'s `AMMO_ARCHER`), and `ARROW_SPELL`
(`NS_IMAGE+29`, over "mov cl,es:[bx+0Fh]") hands it on. The arrows hold no spell
themselves, so nothing else in the game (the USE screen's items, breaking, acid)
sees one. Only a Spellarcher readies them: `ARROWS_FORBID`, in `PROBE_CAN_USE`
(whatever the rules), refuses spell arrows (the equip routine's item, its
`[BP+6]`) to anyone else, but for the backpack (slot 18), so they can be carried
and handed on. The four spells' records pass the routine's own test (+30h's low
bits 2, not 1). Checked in the game: Burning and Chill Arrows buttons for a
Spellarcher knowing both (one in Turn Undead's place, one beside it), their
names and descriptions, a click on each making 20 arrows for a 4th-level
Spellarcher with a 1st-level slot used, and Chill Touch cast on a hit with them.
Checked for the quiver: with spell arrows in it, a button says the quiver must be
empty and uses no slot, a click on them says "Item grafted on", and Wooden Arrows
put on them "Cannot use this item"; with it empty, 25 Burning Arrows made into it
for a 5th-level Spellarcher, a slot used. Arrows put in the ammunition slot by
memory writes during a fight are not shot (the game keeps its own list of what
each combatant has readied): they're made outside fights only.

### Picking pockets

([In the features page](FEATURES.md#picking-pockets).)

How (DSCLOG's PICK POCKETS, sites sharing `INT 98h`): the USE screen's Turn
Undead button (APFM 2BEFh, its handler 630h:48h) shows for a character whose
sheet's +12h holds a priest's element, its icon 3044 to 3047 by element. At
89979h (`PP_SHOW`), for a character with thief levels outside a fight, the
helper gives it an element past the game's cases (9) and its own icon, ICON
3048 (`icons.pick_icon`: Turn Undead's earth tile, a purse), letting go of
the icon the game loaded for the screen if it was another's. The button's
press reaches its handler only after the pointer has rested on it; let go of,
the handler (`PP_CLICK`, 8959Bh) closes the screen (884B3h) and readies Turn
Undead: for the thief's, the menu button keeps its icon (`PP_LIT`, 895F2h), no
spell is readied (`PP_ARM`, 89610h, to the handler's end; the readied kind
the closing set put back), and the pointer is made the one for talking
(DS:11B8h = 2; 1 walk, 4 attack). Its name under the screen is "PICK POCKETS"
(`PP_TEXT`). A right click (`PP_INFO`) asks the game's description box
(8C5F6h) for Turn Undead's kind of entry with the purse's icon (its number
200, Turn Undead's 196 to 199: the element's icon less 0BE4h, plus 0C4h), and
its text is SPIN 1001 in Turn Undead's 1000's place (`PROBE_CHUNK_ID` asks for
999 + `TU_INFO`; a spell arrow's button, 1002-1005), a chunk of the Loader's
copy of RESOURCE.GFF (`spelltexts.py`). The
new spells (196 to 201) share those numbers, so for these two boxes the
helper leaves the box's spell test (8C64Eh, `NS_CMP_INFO`) as the game has
it; before, Turn Undead's showed a new spell's (Fogbolt's for an earth
cleric). The
next click on someone with that pointer (`PP_HAND`, 5ECD8h, the start of the
routine that opens the box to talk, trade or look) asks the Loader as
`PROBE_USE_ITEM` (`INT FDh`) does for an item used on the map: `USE_ITEM`
FF00h and the thief, `USE_WHO` the thing. The Loader rolls and moves the item,
and the helper shows the result instead of the box. The pointer turned to
another mode puts the try away (`PROBE_POINTER`). Checked in the game: Daaki
(fighter/preserver/thief) lifted a scroll from Kalzith; Caron (fighter/cleric)
keeps Turn Undead; a pick put away by a right click leaves the next talk a
talk.

A cleric/thief (a priest's element and thief levels) keeps Turn Undead on its
button and has the purse beside it (`PP_EXTRA_DRAW`), outside fights: the
panel's empty slot APFM 2BE7h (index 1Ah of the spells' 2BCDh), given Turn
Undead's handler (530h:43h, through the stub segments), its frame and the
purse drawn as the game draws Turn Undead's (630h:4Dh, 896BCh) with an icon
of its own loaded (100h:4A4h) and let go of as the screen closes (`PP_CLOSE`,
88504h). These calls may load overlays, so they are made in a frame the overlay
manager can fix up. The handler tells the two by its button ([BP+8]); another
character on show takes the slot's handler off, and the game's redraw clears
it. Checked: Jellybelly (ranger/cleric/thief) has both outside a fight, picked
Kalzith's pocket with the purse beside Turn Undead, and Turn Undead keeps its
name; the screen opened and closed four times over; in a fight, no purse.

Earlier versions picked pockets with Thieves' Tools used on someone, Mirlon's
(given to a thief leader on his gem deal) or Kel's: neither has them now, and
Mirlon's script is the game's own.

The Trustee's key (his own pick, in his talk): a thief with no room for it has
it dropped at his feet (script 146), and his rounds (script 8, from 3767; its
step in word variable 135,20) test after each step whether the key is stolen
(flag 55) and lies within 9 of him, and make for it ("There it is!") without
picking it up, so the rounds stall. After a talk he is busy (flag 51, "I'd love
to talk more...") until the rounds' first step clears it, so a stall left him
busy for good. In the Loader's copy of `GPLDATA.GFF` (`pensasks.py`), the test
asks for flag 55 to be 2, which it never is (`no_key_chase`), and the busy line
jumps to code after the script's end that clears flag 51, says it and jumps
back (`busy_once`); it also starts his rounds again (a call to 8 at 3767, as
the game's door script 147 does), so rounds that stopped walk on.

His rounds pick a corner by their step (word variable 20, 0 to 5, a case each:
27h), but steps 1 and 5 have none: a pause at the corner he has, its x and y
left in word variables 2 and 3. Those are every script's, and a run of another
in between (the door's 147, Kurzak's 141, the escape's 137) leaves other
numbers there: one save had him making for x −4943. He never arrives, and the
rounds go on only when he does, so he stood still, busy for good. The game's
steps never reach 6 and 7 (past 5 is 0), so in the Loader's copy their cases
are 1's and 5's (`rounds_pauses`): each case's value changed in place, its first
command a jump to code after the script's end that sets the corner before it
(0's for 1, 4's for 5) and goes on to the next case. Checked in the game with
the save: talked to, he said his busy line and walked his rounds again (steps
2, 3, 4, 0, 2 within a minute).

### Mirror Image

([In the features page](FEATURES.md#the-games-bugs-fixed).)

The game's only use of the images is a d100 in the routine that lands a spell
on its target (7A539h, from 78C19h; 7A5BFh, `cmp ax,4Bh` at 7A5CDh), for a
spell for one creature (618:20h's 8 or less: the spell record's target kinds 3,
4, 5, 7 and 8, not an area's, a cone's or a wall's). An image taking it uses a
charge (598:57h, 76803h) and shows it vanishing (7AD8Ah: "spell" 0BFh, cast by
the creature on itself). The game made no exception for the caster's own
spells, so Armor cast on oneself under Mirror Image was lost three times in
four, an image with it, and weapon blows come to that routine with no spell
(-1) and skip the roll, so the images stopped none.

- **Spells** (`NS_IMAGE`, at 7A5CDh): the chance is 0 unless caster (DI) and
  target (SI) are on opposite sides (party members below 4); else 75, or 50
  for Reflected Image's (`IMAGE_CHANCE`). The dice log knows the roll by the
  code after the dice call (`IMAGE_SPELL_RETURN`), or, with the overlay
  manager's INT 3Fh stub there, by the routine's arguments (target, caster,
  spell at +12h) and Mirror Images on the target; the vanishing's roll
  (spell 0BFh) goes unmentioned.
- **Blows** (`NS_BLOW`, replacing the attack routine's `cmp word [bp+1Ah],0`
  at 58A00h, 5883Ah's, just after a hit is decided): with Mirror Images on the
  target (`[494Ah]`), the helper rolls the d100 with the game's own rand()
  (load segment:0822h), from a frame of (target, attacker, chance) and with
  `jmp short +5 / "IMAGE"` after the call, which the Loader's filters and
  `IMAGE_BLOW_SITE` know. On the chance or less it has the game use a charge
  (598:57h, as for a spell) and sends the attack on as a miss (58A46h, the
  miss sound). The way back, the miss's address already, goes in a frame with
  BP that the overlay manager can fix up: 598:57h is overlay code and may load
  others over the attack's, and adding to the way back after the call would
  add to the manager's INT 3Fh stub.

### The game's spells

([In the features page](FEATURES.md#the-games-bugs-fixed).) More bugs mended
whatever the rules, besides [Mirror Image](#mirror-image)'s (`gamepatch.py`,
after the `ns_list_` patches):

- **Armor** (effect 2): the spell-landing routine (7A539h) used a charge when
  any spell or blow landed on a target with Armor (7A557h, `je` past it
  unless effect 2 is on), and the damage routine (79A3Eh) used another for the
  damage. `armor_charge` makes the first jump always taken, leaving one charge
  for each damaging hit: a weapon's damage, a shot's as a blow's, goes through
  the damage routine too (the attack routine's one damage call, 5B8:20h at
  58B1Fh, with spell FFFFh), so the helper needs no site for blows. Seen in the
  arena: a hit takes Armor from 9 charges to 8.
- **Charges on the Effects screen**: `EF_CHARGES` (in `NS_ENTRY`, for the line
  under the pointer, 7ED37h, the way back's third byte on "mov bx,ax") points
  the effect's entry at `REFLECT_ENTRY` with its name and the charges left (+8
  of the record, `NS_CHARGES`): IMPROVED AC (10 CHARGES). Only for a spell
  lasting a number of uses (its record's time, +7, from -1 down to -9998) or
  for a timed effect (an entry of kind 7 in the event queue, DS:2FBEh, with its
  owner and handle, as Armor's). A permanent effect (time `PERMANENT_TIME`,
  Charmed) and an item's power (Shadowseeker's Detect Invisibility: the game casts it for -9999 while it is readied, with no
  timer) hold a meaningless 15 at +8, 9999's low byte. Mirror Images from Reflected Image take its name
  and icon. 580:5Ch keeps the name's address, not the entry's, so Reflected
  Image, whose entry that is, writes it again before its own use
  (`ns_reflect_entry`).
  Enlarge (effect 16) on a party member is named with its damage instead,
  ENLARGED (+90% DAMAGE): the level is the Loader's (`STATS_ENLARGE`, the 25th
  byte of the member's STATS, from `GameData.enlarge_level`, the caster's level
  as Dispel Magic weighs it), printed with a 0 after it. Working it out in
  DSCLOG would mean calling 598:52h, the game's sum of a creature's Enlarge
  levels, from the Effects screen's overlay. The game lets only one Enlarge on
  a creature (seen in DOSBox: a second cast uses up the spell, nothing added).
  Barkskin (57), Flesh Armor (59) and Magical Vestments (60) are named with the
  armour AC they give, BARKSKIN (AC 3) (`STATS_ARMOUR`, bytes 25-27, -128 for
  none, from `GameData.armour_spells_ac`), as the effects' part of the AC
  routine (7C557h) works it out: at most 6 - L/4, at most 10 - L, and 5 less
  (L - 5)/3 above 5th, L the effect's level as 7678Ch sums it, each such effect
  at its caster's level by 81B16h: a spell's as Dispel Magic weighs it, a psionic
  power's (138-171) the psionicist level, spell 190's the best of classes 1-4,
  anything else's the best of the sheet's three (`GameData.effect_level`).
  Checked in DOSBox: a 12th-level Barkskin on Cermak (no armour, DEX -4) made
  his AC -1.
- **Share Strength's end** (5CEECh-5CF34h): the loop over the effects records
  removed each record of the power cast by DI with 598:48h (owner, handle), but
  passed DI as the owner, so a receiver's record stayed (and a record of the
  psionicist's own with that handle went instead); and after a removal
  the records move down, so the next was skipped. `power_end_*` push each
  record's own owner (+0) and handle (+7), step SI back after a removal, and
  count to the live count (DS:1E24h) rather than 192; the `mov ax,390h` and
  the far call are left where they were (their segments are fixed up).
- **Dispel Magic** (spell 26, the preserver's): its record's effect (+19h) was
  50, "No spell use", which Dispel Magic itself doesn't end; the cleric's
  record has none. `dispel_effect` makes it 0.
- **Hold Undead** (spell 31): the landing routine asks whether the target is
  undead (7BE20h, AL) and, if not, goes on to 7A359h for any spell, which
  looked like Hold Undead holding anything. It doesn't: every spell's targets,
  one creature's too, are gathered by the area code (8BEB:0000h, 846D0h) and
  sifted by 80F5:1CF7h (7A897h, its table at 80F5:1DCFh: spell 31's case asks
  7BE20h too), which drops a living target first. `hold_undead` puts DSCLOG's
  `NS_HOLD` site over the landing routine's `or al,al / je +22h` (7A333h) all
  the same, a second guard: a living target of spell 31 goes to the
  immunity's way out (7A1F0h).
- **Cause Serious and Critical Wounds** (spells 113 and 128): their records'
  damage dice were 2d9 and 3d9, where the Cure spells (rolled by their own
  code) heal 2d8+1 and 3d8+3. The damage routine (76DA2h) rolls the base dice
  (+1Dh >> 3) plus the steps' dice (+1Ch >> 5) of the sides (+1Eh & 0Fh), and
  adds the steps' flat bonus (+1Ch & 1Fh), the steps being (the caster level,
  at most 10, + the adjustment, +1Eh >> 4) / the levels a step (+1Dh & 7), at
  least 1. `cause_serious` and `cause_critical` make them 2d8 and 3d8 with a
  step of +1 and +3 a 7 levels: one step at any level. `SpellDamage.flat` lets
  the dice log and the Spells tab show it as 2d8+1, not "+1 for each 7 caster
  levels".
- **Absorb Disease** (power 147): its case in the effect handlers (80F5:089Eh,
  7943Eh) ran on into Strength's (79470h: 1d6 STR, effect 43h, the psionicist
  its target), and jumped there too when the target had no disease.
  `absorb_no_strength` and `absorb_end` send both ways to the end of
  Strength's case (794ACh: the flags it sets, then the handlers' end).
- **Bless and Aid's filter** (7B03Dh, 80F5:249Dh): whether one of the caster's
  side has an enemy within 28 sixteenths, measured from a point given by the
  creature's place (DS:669Dh + 20h a thing: x, then y at +669Fh), but the
  routine pushed the x twice. `bless_from_cell` makes the first push the y.
- **The fire elementals** (kinds 32 and 33): their resistance classes, in the
  monster kinds' table (3E45h:00A8h + the kind, 43918h), were 14 (+1 weapons,
  nothing from fire) and 13 (+2 weapons, fire hurting), the wrong way round
  (the clue book: lesser elementals +1, the others +2). `fire_elemental` makes
  them 15, a class the game has and no kind used (+2, nothing from fire), and
  14. DSCLOG's SEG_MOVE copies the table, so the change goes with it.
- **Cloak of Bravery** (Brave, effect 9): the saving throw's modifiers
  (79EBDh) give it +4 and use a charge only against a spell whose record has
  100h in its +11h word (80F5:25A0h), which none had. `brave_fear_*` set it on
  the spells that make one Afraid (effect 17): Scare (21), Fear (43), Cause
  Fear (78; a Cloak of Fear's too) and Insect Plague (132); Spook (200) has it
  from DSCLOG's `NS_PATCHES`. The Loader's saves show the +4 (`FEAR_CATEGORY`).
- **Negative Plane Protection** (effect 42): an undead's negative-energy touch
  (element 100h) on a creature under it (7A7C5h) uses a charge, then the
  target saves (79A71h) as against Vampiric Touch (27h), whose record allows
  no save (+1Fh bit 0), so it never stopped anything. DSCLOG's `NS_NPP`
  (replacing "add sp,4 / push 6 / push 27h" at 7A7E9h) makes the charge's two
  arguments, still on the stack, the save's: 6 and, once the records have room
  (SEG_MOVED), record 212 (`NPP_SAVE`, past the new spells), Vampiric Touch's
  copied with a save against paralysis, poison and death allowed (21h). Saved,
  the game stops the touch and gives the undead 2d6.
- **Acid** (effect 1, Acid Arrow's): the game spends an effect's charges
  (the entry's +8) through 76803h, which calls the effect's handler (for Acid
  7897Bh: 2d4 acid, the damage named Acid Arrow) and takes the entry out at
  none, but it calls it for Acid only on chance events, and Acid Arrow's time
  is in seconds (+8 none) on DS:[9B72h]'s clock (60 at each round's start in
  a fight), a timer that only ends it, so the acid never burned again after
  the hit. DSCLOG's `ACID_ROUNDS`
  (76525h, in the routine adding an effect) makes an Acid's seconds rounds as
  charges (1 a started minute, at most 127); `ACID_ROUND` (5741Dh, the start
  of the routine starting each round, before its initiative) calls 76803h
  for each creature with Acid charges through its stub (DS-0C7h:57h), the way
  back in a frame the overlay manager can fix up; `ACID_USE` (76808h) has any
  other call spending Acid's return at once. The burn's damage is Acid
  Arrow's, whose record would put Acid on again at the caster's level (a new
  entry, burnt in turn): `ACID_BURN` (78982h) notes a burn and `ACID_ONCE`
  (78DEFh, where a spell's damage puts its record's effect on) answers "none"
  once. The dice log shows the rounds (`Acid Arrow burns 4 rounds more, 2d4
  at the start of each`) and each burn.
- **Berserk and Confused** (effects 3 and 11): on a computer-run turn the
  game rolls the creature's side (its creature's +1Dh) anew (8053:000Eh), and
  when the effect ends (7872Fh) only a charm (10) had its side put back, from
  the sheet's +3Ch. DSCLOG's `NS_SIDE` (over the end routine's "jmp 788BBh",
  78785h, where an effect has no case of its own) sends Berserk and Confused
  to the charm's case (787E9h).
- **The computer's walls**: the AI's cast (6466:0000h) gives a spell's two
  points the chosen cell's middle (5A38Ch, four pushes), and a wall (a record
  whose target, +0Ch, is 2) is as long as its points are apart: one point.
  DSCLOG's `NS_WALL` puts the points 32 sixteenths either side of the cell,
  across the line from the caster (along an axis, or the diagonal, whichever
  the line is nearest), so a wall four cells long; other spells as before.
- **A thief skill for the whole party** (who 7FFEh; 801BDh, from REQUEST 3
  and the trap's REQUEST 7 at 80A9Dh): each standing member's chance
  (8023Bh, the same routine the roll uses, so with the Loader's skill rules)
  is weighed against the best so far, which starts at 0 with the member 0, but
  "cmp [bp-2],dx / jna" keeps the lower, unsigned: nothing is, so member 0
  always rolled. `party_best` makes it "jge" (80201h): the highest chance above
  0, else member 0 as before. A named character skips the pick altogether.
  Found from CalvinRodo/yuan-ti's notes.
- **An archer's pointer** (1D66Ah, the pointer's form in a fight: 6003 the
  sword, 6004 can't attack, 6005 the missile, 6006 can't shoot; the missile
  test 1D5AEh): a missile weapon ready (41BE:89h), arrows for it (41BE:75h)
  and the range, then, in a fight, none of the round's melee swings (+1ABh of
  the round's tables at 37BDh, a byte a combatant) or shots (+181h) made. The
  weapon attack routine (5883Ah) counts the shots at +181h, makes it 63h once
  all are made (58C45h) and lets another go while it is under 63h, so after a
  shot that killed the pointer said "can't" while a click still shot.
  `shots_left` makes the shots' test "cmp ...,63h / jnl" (1D657h); the melee
  swings' stays (no shooting after a swing).
- **Random monsters** (REQUEST 8, 80BE4h; scripts 99 and 106): `MONR` 1 of
  `RESOURCE.GFF`, 42-byte records {region, 10 x {OJFF, strength}}. With a ≠ 0
  the count is 2 x the party's strength / the monster's, 1 to 6, but the slot
  search leaves SI one past the match and "idiv word es:[bx+4]" (80CD8h) reads
  the next slot's strength: the next record's first OJFF after the tenth, and 0
  after the last in the records with nine or seven (regions 6, 13, 14, 27, 39,
  40, 44 and 255), a "Divide error" that ends the game. `monster_count` makes
  it [bx+0], the match's own.
- **A shop's magic items shine.** The colour cycler (22F8h; its table at
  CS:6, 16 x 8 bytes, set up by the region's load at 1CECFh: colours 1-5,
  6-10, 11-15 and 240-248) turns only from the map's main loop (1A935h:
  DS:1194h, set by the timer every 8 ticks, then a far call to 22F8h:047Ch,
  then 1194h cleared). A shop, opened from a conversation, runs its own loop
  (7DDE4h, while DS:11B2h is 1: a character's screen open) and, as the
  pointer stands on some things, waits in the game's wait for an event
  (2531:083Ch), so 1194h stayed 1 and the glow stood still. DSCLOG's
  `SHOP_LOOP` (7DE11h, the loop's "cmp word [11B2h],1") and `SHOP_SHINE`
  (2AFA6h, the wait's "or di,di / jz 084Fh") do as the main loop while 11B2h
  is 1, then the replaced test.

### New spells (wizard and 6th-level priest)

([In the features page](FEATURES.md#new-wizard-spells), and
[the 6th-level priest spells](FEATURES.md#6th-level-priest-spells).)

**Numbers.** The game's spells are 0-68 wizard, 69-137 priest, 138-171 psionic
powers and 172-195 monsters' powers. Its table of 32-byte records (from the load
segment + 3E3Fh) has 96 bytes after 195, room for 196-198, then the monster
kinds table (3E45h). Cat's Grace is 196, Erdlu Claw 197, Fogbolt 198, Reflected
Image 199, Spook 200, Friends 201, and the 6th-level priest spells 202-211.
The game names none of the monsters' powers:
the log names one by its record's effect (+19h, `game.POWER_EFFECT_NAMES`), else
its damage's kind, else its number; a roll before a save against one that puts
on an effect is its duration (`_power_lasts`).

**Room for 199-201 (`SEG_MOVE`).** The 96 bytes after 195 aren't free: the
game's segment table (load + 4137h, 8 bytes a selector: segment, length) has
selector 3B8h, a small stack of 60h bytes, there, and selector 3C0h the
monster kinds table (192h bytes) right after. The overlay loader fixes up its
code's selectors from that table each time it loads an overlay (3BD7Ch), and
the table's own entries are the only relocations to the two segments. So at
the first file open (`INT 21h AH=3Dh`) while DSUNLOG runs, the helper (its PSP
from `AH=62h`, the load segment 10h past it) checks both entries, copies the
200h bytes from 3E3Fh to `seg_space` in its own resident image and points the
two selectors there (`seg_moved`, the header's +306). The records then run to
212, the room's last whole record (it ends at 3E5E0h, the room at 3E5E2h). The stack had been written over records 196-198's room all along; with it
moved, nothing writes there but the helper. Spells 199-201 are set up, listed
and counted (`NS_NEW`, `NS_STATE`'s `NS_MOVED`) only once the move is done;
`monsters.py` reads the kinds table's segment from the selector. The spell
rows for 196 on run past the game's table (3FB9h:19Ch, 7 bytes each) into
segment 4010h from 188h, short of its data at 357h. When the rule switches on,
the helper (`NS_SETUP`) copies in each one's record from a game spell it works
like, Strength (23), Enlarge (5) and Charm Person (2), with its own effect
number and, for Fogbolt, its own duration (2d4 rounds) and save, and each
one's sounds and Fogbolt's bolt (below); writes their rows in the spell rows
(level, mask, name, `3FB9:19Ch`, 7 bytes each); and gives the effects' table
(6 bytes each, from 3F8Dh) their names and icons.

**Known.** The game keeps a party member's known spells in a table of its own
(8Ah bytes each), with no room for more. A new spell's is a bit in the sheet's
`+45h` (bits 4-6 for 196-198, bit 3 Reflected Image, bit 7 Spook; bits 0-2 are
the Elementalist's second sphere), or Friends' bit 7 of the kit byte `+43h`
(whose FFh, no kit yet, counts as not known; `NS_SHEET_KNOWS`,
`NS_SHEET_LEARN`, `NS_SHEET_FORGET`): the routine that finds a spell's known
byte (500:48h, `NS_KNOWN` at 5DD04h) and the one that teaches it (500:43h,
`NS_LEARN` at 5E3F7h) go to the helper for them, and the three lists that end
at 8Ah end at 0C7h (5DDEFh, 5DE72h, 5DF06h). Creation and DUAL clear the bits
with the rest of the spells; the level-up pick, the starting picks and the INT
limits count them.

**A wizard's spell.** About 35 places tell spells apart by comparing the number
with 45h, 8Ah, 0ACh or 0C4h (the USE screen, the cast, the caster's level, a
scroll used...). Each such compare is `INT 98h` and a site number
(`NS_CMP_SITES` in `gamepatch.py`, the same order as DSCLOG's `ns_cmp_sites`);
the helper makes a new spell compare as a wizard's spell does, and hands back
the flags. The name routine (500:61h, `NS_NAME` at 5E560h) gives their names;
their descriptions (SPIN 197-202, and 203-212 for the 6th-level priest spells:
the spell + 1 as the game's own) and icons (21196-21201) are chunks of the
launcher's copy of RESOURCE.GFF (`spelltexts.py`, `icons.py`), so they take no
room in the helper. A description follows the game's own: the name in capitals,
two spaces, then a terse line with damage as a range ("Inflicts 8 to 64 pts of
damage"), and no level or sphere. Its box shows about 7 lines of about 24
characters and cuts off the rest, so check a changed one on the USE screen
(right-click the icon).

Wake of the Ravager's spell icons (`wotrart.py`, for the 6th-level priest
spells) are read from the player's own copy of that game, and never kept in the
repository: the folder chosen on the Options tab (`wotr_dir` in the settings),
else any folder beside Shattered Lands' (those named Ravager, Wake or Dark Sun
first: GOG Galaxy's are `Dark Sun` and `Dark Sun 2`), else GOG's usual folders
on any drive, each or a folder inside it holding a RESOURCE.GFF whose Heal
description is Wake of the Ravager's (`find_resources`). Its icons are a kind of
picture Shattered Lands hasn't: the frame header as usual, then `0FFh "PLNR"`,
the bits a pixel (4 or 5), a colour map of that many bits' worth of palette
numbers, and codes of those bits, the highest first, where 0 0 is colour 0 and 0
k the last pixel k + 2 more times (worked out on the 101 spells both games have;
38 match Shattered Lands' pixel for pixel). Its palette isn't Shattered Lands',
so each colour becomes the nearest Shattered Lands colour no region changes.
Checked in the game: the Heal icon in a known spell's place on the USE screen.

**Pictures on the ground.** A spell's record names the picture it leaves on the
ground by its +17h (FFh none): an entry of a table of 45 just before the flights
and records (the records' segment less 330h, 18 bytes each: the spell it was
made for, a byte, the object, then how it behaves), the same table Wake of the
Ravager has, longer and looked up there by spell. Its entries for the 6th-level
priest spells name Blade Barrier's circling blades (object 8432) and Wall of
Thorns' thorns (8425), which Shattered Lands hasn't, Fire Seed's fireball
(8405), which it has, and for Whirlwind Sand Storm's dust (8403), which the mod
replaces with a funnel of its own (object 8433, drawn by `whirlart.py`, put in
its entry by `NS_SETUP`). The two new walls go in the Loader's copy of
SEGOBJEX.GFF (`wotrart.area_chunks`, from `icons.write_objects`): the fire
wall's object (8419) naming pictures 2650 and 2651, its anchor (+2, +4) Wake of
the Ravager's, the frames read from its OBJEX.GFF and each colour made the
nearest stable one; without it, the fire wall's frames in grey and in dark
brown. Each new spell has an entry of its own: `SEG_MOVE` moves the table into
DSCLOG's memory (`AREA_SPACE`, selector 3A8h's segment and length in the segment
table, as for the records' room) with four entries after the game's 45
(`AREA_NEW`): copies of the fire walls' (22) for Blade Barrier and Wall of
Thorns, of Flame Strike's (37) for Fire Seeds and of Stinking Cloud's (8) for
Whirlwind, keyed to the spell, with its object; the records' +17h name them
(`NS_PATCH`). `NS_SETUP` puts the blades and the thorns in their entries while
the objects' copy is open (else the fire wall's). An entry's key is the spell
whose damage a wall deals each round (7607Dh passes it to the one-target roll,
76175h, as DI), so each wall rolls its own record's dice and saving throw. The
overlays find the table through the segment table as they are read in; six
places in the game's own code (23D32h, 23D65h, 23EBDh, 23EF0h, 28092h, 280C6h)
load its segment as a constant DOS fixes up, "mov ax,3C81h / mov es,ax / mov
al,es:[bx+2]": the Loader makes each "cmp ax,3C81h" (the fixed-up word kept) and
`AREA_SITE`, which returns the moved segment.

**Whirlwind drawn once.** An entry whose low 4 bits of +2 are 3 lasts and acts
each round, and the game draws it as 18 to 46 copies of its picture scattered
over the area: entries of the draw list (DS:6690h, 8 bytes each: x, y, height,
flags, thing) with flag 20h, all of one map thing (DS:6694h + its number * 32:
its picture's cache slot at +0Fh and frame at +11h, shared by every copy). The
copies are the area: a creature takes the damage where they are (moved off the
map, none do), and an entry with 10h at +2 marks the tile under each copy as
blocking sight (bit 80h of the tile map at DS:556h, cleared again by 23D32h's
routine as the area goes; the missile and spell path traces stop at it, 84300h's
through 0058:0114). So they stay as they are, and `DRAW_SITE` changes only the
drawing: in the routine that draws the walls and things standing on the map
(1DBD:0002), just before it draws an entry (232D4h, the call at 23308h), a copy
of Whirlwind's funnel is passed over (its way back moved past the call,
`WD_SKIP`) unless it is the one nearest the copies' middle, which is drawn at
the middle (`WHIRL_PICK`: each Whirlwind's thing, its middle and nearest copy kept
in `WT_TABLE`, up to four at once, emptied by `WHIRL_CLEAR` at each round's
start and each cast, when a thing's number may be used again). Whirlwind's entry
gets 10h (`AREA_SIGHT`), so it blocks sight as Wall of Fog's does. The funnel
turns: `WHIRL_TICK`, from the main loop's scroll probe after `DUST_TICK`, steps
each kept thing's frame (+11h) through its 4 frames every 3 timer ticks (about
6 a second) and puts each funnel's rectangle into the dust's redraw rectangle
(`d_x0`..`d_y1`), so the game redraws just that part of the map (`DUST_NUDGE`
when the view is still). A thing whose object is no longer Whirlwind's (the area
gone) is let go.

**Whirlwind once a round.** A lasting area deals its spell's damage through the
one-target spell damage (76175h, the overlay at 750E0h, its stub DS-0C7h's
entry F2h: creature, spell, the level and a 3-bit number from its map thing's
+14h) whenever the game applies the areas on a creature: as it is cast, at the
start of each creature's turn and as it walks in. So a creature swept by
Whirlwind still took the turn that hit it, lost the next round's, and took no
damage that round. With NEW SPELLS, `WW_GATE` (7617Dh, the routine's start)
sends Whirlwind's back at once (its way back moved to the routine's end,
761FCh) except from the cast, during its caster's turn (`WW_CAST`, set at
`CAST_SITE`, cleared at the round's start), and from `WW_PASS`: at each round's
start (`ACID_ROUND`, after the burns, before the initiative), it calls 76175h
through the stub for each creature the game lists in a lasting area whose entry
is Whirlwind's (the active effects' segment +0Ah, 3 bytes each: the combatant
and its area's entry, DS:1E26h of them; the game keeps the list as it applies
the areas, so the creatures stay listed while the hits are sent back), at the
first Whirlwind thing's level. A save failed there marks the creature
(`SWEPT_MARK`), and `PROBE_MOVE` takes that round's turn. A save failed as it is
cast takes the creature's turn at once if it has yet to act (`SWEPT_NOW`: not
the one whose turn it is, its initiative not the -1 the game gives one that has
acted; its initiative -1 and movement 0, as `PROBE_MOVE` does), else marks it
for the next round. Checked in DOSBox over three rounds of the arena (sligs,
beetle and party in it): one wave of hits at each round's start, none at the
turns, the swept ones skipped and the rest acting.

**Closer to the books.** Wall of Thorns' damage (`THORNS_DAMAGE`, in the
one-target damage roll, 761A9h, DI its spell) is 8 + the creature's AC, at least
1 (`THORNS_AC`), with no save (+1Fh A0h). The game keeps no AC: its AC routine
(58DD3h) works one out from items and effects for each attack, and it is in
another overlay (41BEh) than the damage roll (428Fh), so calling it there could
have the overlay manager move the code it returns to. So `PROBE_AC`, at the AC
routine's end, keeps each party member's last AC (`AC_SEEN`, its `[BP+6]` the
combatant; 7Fh none yet), and for anyone else (or a member not yet attacked)
`THORNS_AC` counts as the routine does: the sheet's base (+27h, 10 for an armed
man: the routine adds the armour), less each worn item's plus and its type's AC
(+12h, types with +0Fh 80h, a shield too) in the creature's item lists +8 and
+0Ah (where putting an item on moves it; the routine doesn't look at the slot
byte, and +0Ch, the backpack, doesn't count), a fifth of a gladiator's level
(508:25h's) and the DEX adjustment (DS:7F6h by the record's +23h). The effects'
part (5B8:F2h: Armor, Barkskin and the rest) is left out. The dice log shows it:
the entry's extra carries the AC + 80h in its high byte. Blade Barrier's record
has its own 8d8, edged (+1Ah 210h), and the game's saving throw against spells
(+1Fh A1h) for none (+11h's 8000h), as Wake of the Ravager's. Sunstroke's record
takes Slay Living's aim (+00h 4, one creature) in place of Hold Person's (10h,
several: the caster's turn waits, the spell still armed, for more targets; only
Hold Person and Hold Monster have it). Heal's record takes one effect away
(Diseased, as Cure Disease's -13); `HEAL_SIGHT` (from `CAST_SITE`) takes the
target's Blind entries (8) out of the game's table of active effects (DS -
760h:0106h, 10 bytes each: the thing, the caster, the spell, the effect; the
count DS:1E24h), moving the rest down.

**The effects.**
- Cat's Grace: Strength's code rolls the 1d6 (`INT EDh`), into an effect of
  its own (`INT EEh`: 54, a number the game leaves unused); the routine that
  works out a creature's abilities from its scores and effects adds it to DEX
  as Strength's adds to STR (`INT EFh`).
- Erdlu Claw puts effect 6 (unused) on its target. In the routine giving a
  natural attack's dice (7B66Ch, `NS_CLAW` at 7B70Ah), each attack becomes
  1d6+1 where that's better on average than its own. In the melee attack
  routine (58019h, `NS_FIST` at 58226h), where a hit gets its weapon's magic
  (`[BP-0Ch]`, which becomes damage kinds 1000h/2000h/8000h, PLUS1-PLUS3 in
  `monsters.py`), an unarmed attack (`[BP-2]` −1) is +1 to hit (`[BP-8]`,
  taken off the THAC0) and at least a +1 weapon. The same hook makes the hit's
  damage kinds (`[BP-14h]`, set at 581DFh to crushing, 8, for any natural
  attack) slashing (10h) for Erdlu Claw's talons, and for a thri-kreen of the
  party's (combatant below 4, its sheet's race 8) whatever the spell: the game
  has no other notion of claws, and the mastyrials' class takes nothing from
  crushing. Monsters keep the game's. The natural-attack routine
  applies Body Weaponry (2d4) and Animal Affinity (at least 1d10) to the first
  attack after `NS_CLAW`, changing the dice but not the bonus: with the claw,
  2d4+1 and 1d10+1, as the description says.
- Fogbolt puts effect 27 (unused) on a creature that fails its save. In the
  routine adding up an attack's to-hit adjustments from effects (7C3E9h,
  `NS_HIT` at 7C430h, beside the target's Blur), it takes 3 off for a fogged
  attacker and gives 2 against a fogged target.
- Reflected Image is Mirror Image's record (19) with one image (`+4` 11h,
  1d1), so it is Mirror Image's effect 25 and replaces it, and either recast
  replaces the last, as the game does for Mirror Image; Dispel Magic ends it
  as it ends Mirror Image. Where the images roll (see
  [Mirror Image](#mirror-image)), the chance is 50 when the target's effect 25
  comes from spell 199.
  Where the game finds an effect's entry in the effects' table (its number
  times 6: the Effects screen's icons and names, 7ED37h, 7EEC9h, 7EF34h; the
  Look box's, 5FD1Ch; the status under a portrait, 71DF5h; `NS_ENTRY`), the
  helper gives an entry of its own for effect 25 from spell 199: name
  REFLECTED IMAGE and icon 21199, kept past the spell rows (segment 4010h at
  1F8h, after row 211's room), which the table's segment reaches.
- Spook is Charm Person's record (flags 4204h: mind-affecting, undead immune,
  magic resistance; 4304h with fear's 100h for Cloak of Bravery) with Afraid's
  effect 17 for 3 rounds (`+4` 13h, 3d1; `+5` 0; `+7` 60) and, as Charm Person,
  nothing flying. In the save routine (79A71h, `PROBE_SAVE` at 79BB7h) the
  helper takes 1 for every 2 of the caster's levels (preserver, or the Shinobi's
  casting level), at most 6, off the target's d20 total; the log names it.
- Friends goes through Strength's handler (79470h) as Cat's Grace does, with
  effect 74 (unused). The handler rolls its amount with `push dword 60001h`
  (1d6) at 79483h, after the effect choice's INT and its 17 NOPs; for
  Friends `PROBE_GRACE_EFFECT` pushes 2d4 (40002h) on the caller's stack
  itself and returns past that push (`FRIENDS_DICE`, `FRIENDS_PUSH`). The
  ability routine adds the amount to CHA (`[BP-338h]`), to at most 25, and
  leaves a higher CHA as it is. Shop prices read the effective CHA (creature
  +27h). Its record is the caster only (`+0Ch` 7) for 1d4 rounds and 1 a
  level (`+4` 41h; `+5` 1; `+1Dh` 1, `+7` 60); a new casting replaces the
  effect as Strength's does.

**Fogbolt's bolt.** A record's `+10h` names what flies from caster to target
(FFh: nothing): a place in a table of 16 flights just before the records (3
bytes each: the object flying, then a byte, Magic Missile's 8), which the cast
reads at 7530Ch (`imul ax,ax,3`, the object made at 0B8:55Ah and sent off by
600:2Ah); nothing else reads the table. Magic Missile's is place 4, object
8109, whose OJFF names BMP 2227 (36 frames, a direction each). The launcher's
SEGOBJEX.GFF copy adds object 8118 (8109's record naming BMP 2584) and BMP
2584, 2227's frames with its white, cyan and blue (46, 220, 161) in the greys
214, 211 and 209 (`icons.bolt_chunks`; the 208-217 ramp is the same in every
region's palette). No record names place 15, so `NS_SETUP` points it at object
8118 (at Magic Missile's speed byte) and gives Fogbolt's record `+10h` 15,
only when the game has opened the copy (`objects_on`, part of `NS_STATE`);
else, and with the rule off, place 15 is the game's (8116) and Fogbolt flies
nothing, as Charm Person.

**Its sounds.** A record names three sounds (RESOURCE.GFF's BVOC chunks, the
game's Creative Voice files), all played by 90:A6Fh: `+0Fh` with the glow on
the caster (only when `+0Dh`, the glow's object, isn't −1), `+13h` while
something flies (only when `+10h` isn't FFh), `+16h` as the spell lands.
Fogbolt has Fog Cloud's 82 and 98 for the first and last, and keeps Charm
Person's 75 for the flight (`FOG_CAST_SOUND`, `FOG_HIT_SOUND`). Cat's Grace and
Erdlu Claw are cast only on a party member's portrait on the USE screen, where
the game shows its own star over the portrait whatever the spell and, by its
code (90:A6Fh with `+16h` alone on that path, 751C9h), plays the landing
sound: Haste's 96 for Cat's Grace, Shocking Grasp's 77 for Erdlu Claw
(`NS_LANDING`).

The sites share one interrupt with the creation panel's (`INT 98h`, then the
site's number, `RL_*` 1-6, `PK_HOVER` 7, `RG_TWO` 8, the new spells' 9 on).
A site's handler must leave the game's registers as they were: an early
version took the site number in AL before saving them, which handed the name
routine spell 0 and showed ARMOR as every spell's name on the USE screen.

A click on an effect's icon on the Effects screen ([In the features
page](FEATURES.md#spells-on-the-effects-screen)) ends it in the game; with the
switch on, a spell's effect is left on: two jumps in the screen's click handler
(DSUN.EXE 7F226h and 7F236h, `effects_click_low` and `effects_click_high` in
`dsloader/gamepatch.py`) go to its way out instead of to the routine ending an
effect. A psionic power's (spells 8Ah-ABh) still ends, as stopping it there is
how a power is dropped.

### New items

([In the features page](FEATURES.md#new-items).)

How: the new items (the slave pens' and the world's, the bone scale set,
Kreenfang) are in the game's data (`dsloader/dataitems.py`, `worldgear.py`,
`npcitems.py`, `arms.py`): in the Loader's copy of `SEGOBJEX.GFF`, each person's
or chest's object (its RDFF: the object's record, then its items, each a child
or the next of the one before, with its type and name as attributes) has the new
items after its own, so the game makes them where it makes the object. Kreenfang
is the arena's dead body's (object 1204) own gythka made +1 and renamed, its
name attribute with it. One Castle Guard, one Undermountain miner and one Magera
(Drakejaw's) have an object of their own (2560, 2561, 2562: copies of their
kind's, their record renumbered), their entity in the Loader's copies of
`RGN1C.GFF`, `RGN1E.GFF` and `RGN08.GFF` pointing to it; so does one skeleton of
the warrens (Gutterward's: 2585, entity 85 in the copy of `RGN28.GFF`; its
kind's object, 2266, is the skeletons' of five regions), and one thri-kreen of
the Gemfields (Skycutter's: 2598, entity 22 in the copy of `RGN06.GFF`; its
kind's object, 215, is the whole pack's). So does the slave pens' weapon rack
(2563: the Lower Castle's rack is the same object 1647; a thing's record has its
number first, a person's at +6), with Thornwall in place of its first bone
polearm, in Kalzith's copy of `RGN29.GFF` (one copy of the pens: with Kalzith
off, the rack's alone). The Elven Leader's Gythka +2 is his own Gythka +1 (in
his pack, object 124, and the item object 2534 his script gives) made +2.
(People of a kind share an object, so every Tari, Renegade and Wild Mul carries
theirs; the caravan's buried chest is an object the dig's script makes, and has
the Boots of Elvenkind in it.) The Elven Leader's script (46, in the scripts'
copy: `elvenleader.py`) gives the Cloak of Elvenkind (object 2546, an item
object of its own) after the Gythka, as the game's scripts give items (command
39h, a new item of the object; 25h on the ground when it can't be carried);
Father Garyn's (174: `garyn.py`) gives the Tome of Understanding the same way,
the first time the pith is delivered (flag 625), and Merzol's haystack (script
137: `haystash.py`) leaves Hayneedle (object 2590, an item object of its own)
beside his sack of ceramic pieces (25h at the searcher's place, as the sack's),
the first search only (flag 502). The Lava Rift's Hermit (object 81) has
Nightsliver in place of his stone dagger. An object can only have so many
records: the routine that reads them (DSUN.EXE 68000h) keeps a 6-byte entry for
each in a table on its stack, 80 of them, and gives up on an object with 80 or
more; the code that makes a region's people (244D3h) then frees the person's
map entry, and the person is never made. The game's largest has 74 (Jark's); an
item adds 3 (the item, its type and its name), so the Weapon Merchant's 11 new
weapons made 89, and Jark's 7 made 95. `records_*` in `dsloader/gamepatch.py`
make the table room for 120 (the routine's stack frame 0F0h bytes larger: the
game's stack has some 20 KB it never reaches), and `test_records_fit` keeps the
Loader's gifts under it. The tome (`dsloader/tome.py`) is a
scroll of the game's kind: object 1446, among the game's scrolls' numbers
(1400-1499: its object record the first scroll's, as only a scroll's kind of
object has its box's icon clicked; the picture that number had, the icon of two
objects, moved to 2552), its spell byte one past 176. Clicked, the icon has the
game's routine (DSUN.EXE 8B690h) teach a scroll of those numbers its spell, or a
psionic power from 138 to 171; from 172 to 195 it would show "CANNOT LEARN FROM
THIS ITEM" and keep the scroll (from 196 on, the icon can't be clicked). There
the helper (`INT B9h`) raises the reader's WIS, in the sheet and the creature
record, writes its message in the game's buffer, and goes on as for a power
taught: the game uses the tome up and shows it. The short sword, the cloak whose
plus counts, the bone helm and the rest (30: Galefang's, a metal dagger whose
class list has the air cleric's bit, which none of the game's daggers had when
it was made (now every dagger type has it: below); then the bone and obsidian
great axes, the metal one's of those materials, a bone dagger, the only dagger a
water cleric may use, the robes', a metal shield, Ironbulwark's: the game's
leather shield's type in metal, for the classes of its wooden one, and the
girdles' and the amulet's) are item types the helper adds after the game's 115
each time the game reads its table in (`TYPES_EXTRA`; its weapon types by item
type, `kind_of_type`, cover them too). As it copies them in (`PROBE_TYPES_FILL`)
it also sets the air cleric's class bit (+10h, 1) on the game's dagger types
(17, 33, 84, 94), as its own daggers have it, so an air cleric of one class may
use any dagger, as its sphere allows; the Loader's item names
(`dsloader/names.py`) are entries it adds after the game's 322 (the game puts
the item type's material before the name when it shows one); and the icons are
objects in the Loader's copy of `SEGOBJEX.GFF` (`dsloader/icons.py`), which the
helper has the game open instead of its own (its `INT 21h` hook). The copy also
has the game's Polearm picture made 22 pixels tall (`icons.fit_box`): at its own
36, the item box's lines, which start below the picture, ran out of the box. Its icons of the game's
own magic items that stood still (`icons.SHINE`: the Parting Staff, the
Chameleon Gloves, the Hornblade... 19 of them) have every other pixel of their
metal, gems or leather in the colours the game cycles in the inventory (water
11-15, fire 240-248; the Silk Armor's and the Living Cloak's greens in a leaf's
shades), as its other magic items' icons do. Three share their picture with a
plain item (Cahulaks +1 with the cahulaks, Light of Dawn and El's Ring with the
plain ring), so theirs is a new picture (BMP 2653-2655, their OJFF's +0Ch
pointed to it), and the plain ones keep the still one. An
item on the ground is drawn with its object's icon (the thing's map record,
+0Fh), so the Loader's items, dropped from the inventory or left by the dead,
lie on the ground as their own icons (checked: the Short Sword, the Ashen Robe,
the spell arrows). The items' own pictures are only given while the game has
the copy open (`icons.ready`, DSCLOG's `objects_on`; the dice log's
`icons.COPY_OPEN`, reset on attach): `icons.repaint` sets them each 3-second
pass, and an item the Loader makes (`npcitems.add_to`, `pickpocket._link`: the
arena's Ring +1, a new character's Short Sword) gets its own at once
(`icons.fit`), since the inventory, opened before the pass, drew the plain
picture, cached it in the item's `+0Ch`, and kept it until the item was
clicked. Where the game adds up AC and saving throws, the helper
counts the rings and the cloak (`INT F8h` and the save probes). Shadowseeker's
sight is the game's own way with a magic item's spell: readied, it puts Detect
Invisibility on its wielder. In the original game the rings are plain rings
without a name, and the sword, cloak and helm types it doesn't have: don't load
a save that has them without the dice log.

Alagorn's new menu lines are in the Loader's copy of his scripts
(`dsloader/alagorn.py`); he knows an item by its picture.
- Scripts 212 and 213 with every story would overflow the script buffer, as
  the [Trustee's](#what-dinos-and-the-trustee-say-about-them) once did, so
  212's clothes are told by a copy of it (script 220), its rings and other
  items by another (221), and 213's weapons by a copy of 213 (222). His talk
  (script 211) calls each part by its offset in its script, so only the
  called script's number changes.
- The added "none carried" check replays the game's own tests with their own
  jump targets: skipping one leaves the game's if/else nesting one level
  short.
- The two Rings of Protection have different pictures, so their one menu line
  joins two queries with "or", as the game's own tests do.
- Each item a menu shows needs a value saying it's carried, and a script has 16
  locals: the weapons menu's six game items, its loop's own and ten new ones
  are one too many, so items past the locals use the Loader's flags from 784
  on (set afresh as the part starts, as the locals are). The new stories'
  "none left" test is one subroutine they all call.

The icons in the item tables of `ITEMS.md` (`docs/items/*.png`) are drawn from
the game's data by `python -m dsloader.docicons GAME_FOLDER`, from the Loader's
copy of `SEGOBJEX.GFF` in `dos/` (start the game from the Loader once first) and
the game's palette: each picture twice its size, the rest transparent.
`docicons.ICONS` names each image's object; a new item needs its line there, and
`tests/test_docicons.py` checks that every icon the guide shows is there.

### Bracers of defense

([In the features page](FEATURES.md#bracers-of-defense).)

How: where the game's AC routine asks the helper about each worn item
(`INT F8h`) and where it starts a saving throw's modifiers (`INT F9h`), the
helper looks at what else the character wears.

### Robes

([In the features page](FEATURES.md#robes); `robes.py`.)

The robes are one new item type (`ROBE`, the 26th of the helper's types,
`game.ROBE_TYPE`): the cloak of protection's record worn on the chest (+9: 1),
its plus counting for AC (+0Fh, 80h), of no material, for preservers,
psionicists and druids (+10h: 190h). `BRACERS_AX` answers for it as for the
bracers, so it is no armour to the class restrictions, the casting test or the
protection rules, and its plus counts only without armour (`PROBE_RING_AC`'s
bracers branch). The Ashen Robe is +1, the Veiled Robe +2, and the plus tells
them apart: `ROBE_PLUS` finds the one worn on the chest (`WORN_SCAN`).
`KIT_SAVE` adds 1 to every save for +2, and for +1 to a save against a wizard's
or priest's spell (0-137); `PROBE_SLOTS` adds a wizard slot at spell levels 1-3
for +2 where there are any. The Loader: `restrict.is_robe`, `robes.save`,
`robes.slots`, `GameData.protection` (not armour). The icons are drawn
(`icons.robe_icon`, objects 2580 and 2582); Kel's object (107) carries the
Veiled Robe in the data (`worldgear.MAGIC`), and Kalzith's Ashen Robe is put
on him with his cloak and scrolls (`kalzith.stock`).

### Girdles and the amulet

([In the item tables](ITEMS.md).) Three more helper types follow the robe:
`GIRDLE_BACK` and `GIRDLE_URNST` (the 28th and 29th), a belt's record each (+8:
40h, +9: 2, the waist), and `MR_AMULET` (the 30th), a necklace's (+9: 7, the
neck), every class (+10h: 1FFFh); `game.BACK_GIRDLE_TYPE`, `URNST_GIRDLE_TYPE`,
`MR_AMULET_TYPE`. `EXTRA_WORN` asks `WORN_SCAN` whether a creature wears one in
its slot (`WORN_SCAN` now keeps the item it found in `ws_item`).

- **Girdle of Back Defense:** `ITEM_REAR`, called first from `PROBE_STEALTH`,
  clears the from-behind and backstab flags ([BP-1Ah], [BP-24h]) when the
  target wears it and takes their 2 each back off the lowered THAC0 ([BP-20h]).
- **Golden Girdle of Urnst:** `ITEM_REAR` also adds `URNST_AC` (3) for a melee
  attack ([BP+0Eh] 1) whose weapon type ([BP-4]) is a long or short sword in
  the spec kinds table.
- **Amulet of Magic Resistance:** `AMULET_SITE` (`NS_IMAGE+27`) replaces the
  `cmp word [bp-0Ch],0` after Mind Bar's +75 at 7A4FDh in the routine that
  works out a target's magic resistance (7A4A1h): `AMULET_MR` adds
  `AMULET_PERCENT` (15) when the neck holds it, then makes the game's compare.
  The game's spells stop at 5th level, so it never shatters (AD&D's does on a
  6th-level spell or higher, which is left out on purpose).

The Loader's dice log names each (`_thac0_breakdown`'s Urnst part,
`_magic_resistance`); `GameData.wears_type` reads the slot. The
icons are drawn (`icons.ICONS`, objects 2606 to 2609, 2612 and 2613); placement
is `worldgear.GIFTS` (Kel, Wyrmias, the Troop Leader).

### Kalzith

([In the features page](FEATURES.md#kalzith).)

How: he is the game's own kind of person, in the Loader's copies of three of
its files, which the dice log's helper has the game open instead of the
originals:

- `SEGOBJEX.GFF`: object 1000 (a person's object with the Defiler's picture,
  and a slave's record, Dinos's, with his name and a defiler's class), and his
  scrolls' objects 1440 to 1445 (copies of the game's scroll object, with a
  scroll's picture). The game teaches a scroll's spell only from an object
  numbered 1400 to 1499 (any other it casts); its own end at 1432, and the
  numbers after are pictures, most of them other objects' icons, which the copy
  moves to pictures of their own (2440 to 2445). None of these objects is the
  game's. Scrolls bought with earlier builds (objects 1001 to 1006, which cast
  their spell) are renumbered wherever they are.
- `RGN29.GFF`, the slave pens: an entry setting him in his pen.
- `GPLDATA.GFF`: his conversation (script 218, after the game's 217), its entry
  in the game's table of script entry points (which saves go by), the command
  in the pens' script that runs it when he's talked to, and his portrait
  (portrait 101, a number the game leaves free).

His state is in the game's own flags (760 to 763: met, friendly, cold, his
scrolls given; the game uses flags up to 755), so a save keeps it. The first
time the party is in the pens, the Loader puts his six scrolls among his
things (from the game's free list, as for
[the arena's ring](FEATURES.md#new-items)), once a game. If he is killed, the
Loader marks it (flag 772) and the others speak of him as dead (see
[Dinos and the Trustee](FEATURES.md#what-dinos-and-the-trustee-say-about-them));
after the party's escape he is gone from the pens with everyone else.

With his scrolls the Loader gives him his gear, worn (`kalzith.gear`, flag
776): a Quarterstaff in the right hand, a Cloak (the game's own) and his Ashen
Robe on the chest. His shop sells these too. The shop's list (built at
`8347Ah`) takes every entry of the merchant's item lists whose kind is an item
(`+2` = 1) and whose record is below 9999, worn or not, and buying (`8382Dh`)
checks only the price against the party's money; nothing in the game marks an
item a merchant won't sell. Once he carries nothing, his shop isn't offered any
more ("Anything left to sell?" "Nothing. You've bought every scrap of hide I
had, and the robe off my back. More takes time I don't have.", flag 778): set
while talking with him (the last thing just bought) or while the map is
running. (The dice log's helper counts the game's map loop; it doesn't run
while a talk, menu or shop is open.)

Killed, he leaves one of the scrolls he still had, chosen at random, and
whatever of his gear he still had, in his body where he fell, and the Loader
logs the scroll ("Kalzith leaves: Scroll of Blur"). The game puts everything a
dead person carried in the body; the Loader takes the other scrolls out of it
(flag 777, once).

He is a slave of the pens like the game's own (his record is Dinos's): attacked,
he turns on the party as they do, and only the guards near him join the fight.

### Semyon

([In the features page](FEATURES.md#semyon).)

How: in the Loader's copy of `GPLDATA.GFF`, the command that takes him off the
map when he walks out after the fight (script 5 at 2400, run only from there)
first sets the Loader's flag 770; the game's other exits don't reach it. The
Loader sets flag 771 if it ever sees him dead (his record's hit points or
status). The pens' script ends with, "if flag 770 is set, 771 isn't, and he
isn't in his pen yet, make him there", the command the arena's script uses
when he is untied (25h, his object 280), and the command that runs his
conversation (script 219) when he's talked to, with its entry in the game's
table of entry points. Flags 764 and 765 (his own: placed, met) keep the rest,
so a save keeps him.

How: the arena's script 3 moves Scar and his henchman to the pens (5Eh to region
41) when the party reaches the west exit after Scar's plan is agreed. In the
Loader's copy, the henchman's move (at 1828) becomes a jump past the script's
end, where that move is made, then Semyon's, to a square beside them (74, 68),
if he is recruited (the game's flag 6), not seen dead (771), in the arena and
not against the party (his field 74, the side, not 2); then the Loader's flag
782 is set and the script goes on where it was. With 782 set, the pens' script
leaves him on the party's side, and his conversation has the breakout's line
instead of his menu, until the escape (the game's flag 503).

His object is the arena's, made for a man who fights beside the party: on the
party's side, and with 0 in a byte where every slave of the pens has 12. In his
pen the pens' script makes him as they are, with the command the game's scripts
use to change someone (40h: his fields 74, the side, to 4, theirs, and 70 to
12), once (flag 779). Attacked, he is then like any of them: he turns on the
party, and only guards near him join the fight; in a fight in the pens he isn't
on the party's side. Like Kalzith's, his commands come after everything of the
game's, which keeps its place.

### What Dinos and the Trustee say about them

([In the features page](FEATURES.md#what-dinos-and-the-trustee-say-about-them).)

How: in the Loader's copy of `GPLDATA.GFF`, their scripts (139 and 146) keep
every byte where it was, since the game's jumps go to fixed places. Two
commands become jumps to code after the script's end: the one starting the
menu's part goes to the same command followed by the new questions' flags
(766-769, 773, 774), and the menu goes to a copy of it (the game's own bytes)
with the new questions after its last about someone. Each then jumps back to
where the game's script carries on.

That (with [his busy line](#picking-pockets)) makes the Trustee's script
10,967 bytes, and the game reads every script into one buffer of 10,000 bytes
(a script that calls into another reads it in over its own). One of 9,800
bytes ran; one of 10,000 ended with "BAD GPL EXIT" (the game's own largest is
9,792). So the Loader's copy of the game makes the buffer 11,776 bytes where
it is allocated (`push dword 10000` at 6A692h becomes 2E00h), about 1.7 KB
more of the game's memory.

### The cooked vulture

([In the features page](FEATURES.md#the-cooked-vulture).)

How: in the Loader's copy of `GPLDATA.GFF`, Dinos's talk (script 139) has the
question in its first menu (a copy of the game's with the question added, as
for the questions about Kalzith and Semyon, see
[Dinos and the Trustee](FEATURES.md#what-dinos-and-the-trustee-say-about-them)),
shown while the game's own test says someone in the party carries the cooked
vulture (33h, as the campfire's script asks about the plucked one; the game's
object A4Ch), the test being the question's own condition in the menu. Chosen,
the script takes it (5Ch, as the campfire takes the plucked one) and sets the
Loader's flag 780, then gives the XP as the game's quests do in the middle of a
talk (the Tari's, script 125: the words, the quest's sound, then 21h). Not
through the game's routine for it (script 74 at 135, which Dinos's script calls
when he heals Gilal and the talk ends): it opens a narration window and ends
there, and the menu came back after it with only "Goodbye." The
Loader then refills the party, once (flag 781), only while the party is
talking with him (never from a game being loaded).

### Defilers' scrolls

([In the features page](FEATURES.md#defilers-scrolls).)

When a creature's hit points reach 0 the game empties its item lists and puts
what it carried in a container on the ground (an item whose `+08h` names a
list), in the same step: in the arena's opening fight the Defiler's lists were
empty, and its things in the container (object 306's item), before the Loader
looked again, a quarter of a second later. A scroll can't be put on the body at
the death itself, so `defilerscrolls.py` gives it earlier: in a fight
(`game.in_combat`: `IN_COMBAT`, and the fight state's +19h, as `IN_COMBAT` alone
stays up while the party walks spread out), each living creature after the party of one of
the game's defiler objects (`DEFILER_OBJECTS`: those whose SEGOBJEX record has
class 18, the defilers', at `+6Fh`; a creature record's `+06h` is its object,
negated) is rolled for once in the fight (d100, 5 or less; Kalzith left out; the rolls
forgotten as it ends, so a later fight's defiler in the same place under the
same name, as the arena's, is rolled for too), and a scroll
put in its pack (`npcitems.add_to`, a list of its own if it has none), which the
game then drops with the rest. Checked in the game: the arena Defiler given a
scroll of Haste as it came on, the scroll in its container after the Rampager
killed it, its lists back on the game's free list.

The object, not the class on the creature's character sheet (`+21h`): the game
shares and reuses its few monster sheets (the arena's three Sligs had one), and
one of Scar's henchmen, under a defiler's sheet, was given a scroll in 2.4.0.

The rolls are kept for the session by area, creature and name, and forgotten
when the game's clock goes back or the party changes (a game loaded); a
defiler already carrying one (a game saved mid-fight) gets no second. The
scroll is `kalzith.scroll`'s, of the game's object 1400: a scroll teaches
when right-clicked only for objects 1400-1499 (`SCROLL_LEARNED`), and its
spell is the item's own (`+02h`, one past the spell's number), so one object
serves every spell; priced at 3000 a level, as the game's scrolls. Checked in
the game: one given to Cermak, right-clicked, showed SCROLL, 3000 and Shield's
icon, and taught Shield (`YOU LEARN THE SPELL`). The roll gives the dice log
no line: it would tell the player what the body holds before the fight is won.

### What the party wears

([In the features page](FEATURES.md#what-the-party-wears).)

How: the party's figures are objects 300 to 313 in `SEGOBJEX.GFF` (300 and the
figure picked at character creation). The launcher's copy of the file (see
[Item icons](FEATURES.md#new-items)) gives each its own walking and fighting
pictures, the game's with room round them for gear (walking, 6 pixels at the
sides and 2 above, as much as anything worn reaches; in a fight, 10), and free
space after each in the file. The game draws a figure's whole picture at every
step, so each picture is exactly as long as it needs to be. While the game
runs, when someone's worn items change, the Loader draws their pictures anew
(`dsloader/spritegear.py`, from where `dsloader/spriteparts.py` finds the
head, hair, hands and the rest in each frame), writes them into its copy of
the file with their new lengths in the file's index (the game reads a
picture's place and length there each time it loads one), takes the old ones
out of the game's table of loaded pictures (the game frees them itself, as any
it no longer uses), and empties the figure's slot on the map: the game loads
the new pictures and draws them at once, in a few thousandths of a second
(`dsloader/sprites.py`). It then has the helper draw the view again (see
[Shadows](FEATURES.md#shadows)), so the shadows show the new outfit too. A
picture the game loads later (in a fight, in another area) comes dressed, from
the file. The copy also has a spare pair of pictures for each party place.
Each thing on the map names the picture it is drawn with and the slot in the
game's picture table it is drawn from; for a second member of the same figure
the Loader names their spare there and empties the slot, and the game loads
the picture and fills it.

### Elves and half-elves

([In the features page](FEATURES.md#elves-and-half-elves).)

How: elves (objects 304 and 305) get pointed ears (`dsloader/figures.py`): 2
pixels wide and 3 rows tall, a salmon inside, a rose rim and tip. Their place
is read from each frame's parts (beside the head, two rows above the eyes from
the front; at the eyes from behind; behind the face from the side), or set by
hand for the poses whose parts can't be read (`EAR_PLAN`: lunges, the bow,
hit, dead). They are drawn after the gear, only on pixels the gear left as
they were, so a shield or a weapon in front hides them.

Half-elves (objects 306 and 307) name the human pictures, as 300 and 301 do.
The Loader's copy of the file gives them figures of their own instead
(`figures.py`), made each time from the game's pictures:

- **The man** (`HalfElfMan`) is the elf man's figure, a column wider below
  the neck. Each part of him (hair, jerkin, sleeves, trousers, boots) has its
  colours spread by brightness over a ramp of the party's palette, so it needs
  the palette, read from `GPLDATA.GFF`. He also gets dark eyes, a linen V at
  the neck, a belt with a buckle, hair cut at the nape and small ears.
- **The woman** (`HalfElfWoman`) is the human woman in her colours
  (`halfelf.recolour`), a column slimmer below the neck. Her long hair is cut
  away and put up in a bun, with her neck and cloak drawn where it hung, and
  she gets the elves' ears. Her fight poses are set by hand (`WOMAN_FIGHTS`).

Gear is drawn on them by what their own colours can't tell `spritegear`
(`spritegear.Own`, made by `figures.own`):

- the parts of the game's frame they were made from (head, hair, shoulders,
  hands, feet), moved by the column added or taken out, since their hair and
  wristbands are no longer in the colours `spriteparts` finds them by;
- that frame itself: its wristbands place a shield in a fight, and a worn
  cloak is fitted on it before it is carried over to the man (fitted to him, a
  column broader, it would swing past his arms);
- the man's clothes: the ramps of his jerkin, shirt, trousers and boots, and
  where in each frame he wears them, so armour recolours them there;
- the woman's purple cloak: a worn cloak recolours it, shaded as the green at
  the same place in the human woman's frame, but not her purple wristbands,
  and a belt isn't drawn over it from behind.

With the switch off (`elf_looks`, `sprites.Pictures(looks=False)`), or if the
palette or the pictures they are made from are missing, or making them fails,
a half-elf is the human figure recoloured (`halfelf.py`), as before, and elves
have no ears. The switch counts when the launcher writes the copy; the Loader
dresses the party with the setting it had then. A spare is drawn as the figure
it stands for.

Cilla, in the game's own party, is an elf with the half-elf woman's figure (7)
in her record (object 32003's RDFF, its word +22h, the creature's +18h), and
her object (OJFF 32003) names the human woman's picture. In the Loader's copy
of SEGOBJEX she has the elf woman's figure (5) and picture (the game's, which
the Loader then swaps for its own as for anyone). In a game begun without the
copy, the Loader writes the figure into the running game's creature table, and
the game draws her as an elf from its next area or load
(`defaultparty.figure_chunks`, `defaultparty.elf_figure`), both only with the
`cilla_elf` switch on.

### Shadows

([In the features page](FEATURES.md#shadows).)

How: the launcher's copy of `DSUN.EXE` (see [How the dice log
works](#how-the-dice-log-works)) calls DSCLOG when the game draws the floor of
the view or of a rectangle of it. DSCLOG then lays each casting figure's current
picture, flattened and stretched, onto the floor just drawn, darkening each
pixel to the closest clearly darker colour of the area's palette (a table it
makes from the palette when the Loader asks: after each area change, once its
fade-in is over, and now and then; the colours the game cycles, for water and
fire, are never picked as darker ones). The rectangles the game draws again when
a figure moves are widened by the length of a shadow, so none is left behind.

**Pictures out of memory.** The shadow is traced from the figure's picture in
the game's picture cache, and in a big fight (the arena, ten monsters) the game
lets go of most pictures between drawings: in the user's arena save every figure
but one had its picture out of memory as the floor was drawn, so no shadow.
Loading one from here, in the middle of a drawing, could push out or move a
picture the game is about to draw, so instead DSCLOG keeps each frame's shadow
as it draws it (`SC_START`, `SC_PUT`, `SC_END`: the runs that cast a shadow,
three bytes each, at most 64, under the picture's number from the cache slot's
`+6` and the frame) in 80 slots of 208 bytes in upper memory (`SC_SEG`, from
KEEP, if `UMBPLUS.COM` made the room), the oldest given up first. A figure whose
picture is out casts its frame's kept shadow, or another frame's of the same
picture (`SC_FIND`). Measured in the arena: 74 slots filled in a few rounds, the
party and the monsters seen in memory once casting shadows after; one whose
picture was never in memory at a floor drawing still has none.
Only pictures already in the game's cache cast one: until 2.6.0 DSCLOG had the
game load a missing one from there (1DF3:2A3Ah), in the middle of drawing the
floor, which can push out or move another picture while the game is drawing; a
freeze report of 2026-10-21 has a figure's picture unpacked from garbage, the
row decoder (0980:709Ch, into a 5,408-byte buffer at 0980:11BCh) never meeting
its row's end and copying over the code after it, itself included, with the
game's data segment then overwritten by its stack. A figure whose picture isn't
loaded gets its shadow when the game has loaded it to draw the figure, a frame
later. The Loader keeps DSCLOG's list of who casts one (`dsloader/shadows.py`)
and has DSCLOG draw the view again when it changes (from the game's main loop,
as centring the view does: marking the figures changed instead, as the game's
own code does to draw one again, can set one in a fight walking again).

The list can be up to half a second old, so as it draws DSCLOG also checks
the creature's status (`SHADOW_GONE`: the things table, then the creature's
`+1Ch`) and gives a dying (4) or dead (5) one no shadow. Otherwise it would
load the dying creature's new pictures through the game's picture loader from
inside the floor drawing, the most likely cause of a crash seen in the arena
as a creature died (not reproduced).

### Dust

([In the features page](FEATURES.md#dust).)

How: DSCLOG notes, each time round the game's main loop, how far each figure
that casts a shadow has walked, and raises a puff a little behind and to one
side of its feet every 6 pixels (the feet in turn). The puffs are drawn on the
floor after the shadows, lightening it through a table of each colour's lighter
one, which the Loader makes from the area's palette (`dsloader/dust.py`):
only warm, middling colours (sand, dirt) have one, so stone, water and the
figures take none. Each puff is dithered thinner toward its edge and as it
fades, by a pattern fixed to the map, so a puff looks the same however much of
it the game draws again. While anyone walks, the rectangle the game draws again
round what moved is made to take the puffs in; once everyone stands, DSCLOG has
the view drawn again a few times a second until the last puff is gone.

### Scripts' requests and refused casts in the dice log

Two `NS_IMAGE` sites record what the game does without a roll:

- `REQ_SITE` (DSUN.EXE 7FF42h, "mov bx,[bp+6] / dec bx") in the routine running
  a script's REQUEST (command 22h, 7FF30h; a jump table of 20 at its CS:177h):
  kind 6 (`KIND_REQUEST`), the request as the entry's value, the frame for who
  and the two values. `REQUEST_NAMES` names all 20 (from the yuan-ti project's
  notes on the game: rest, door, skill check, rest, an object's state,
  cinematic, trap, random monsters, transform, block and unblock a cell and its
  sight, arena bout, the pointer to walk, music, place an object, change sides,
  game over, count creatures).
- `AIM_SITE` (8455Bh, "cmp dx,-1") where a click on the map takes the readied
  spell's target (84538h; the cast follows) after the aim check (84C54h; its
  other caller, 8404Bh, picks the pointer's form on every pass of the main loop,
  about 2,000 times a second, and is left alone): -1 no creature there, -2 not
  one the spell takes, -3 a wall too long, -4 out of sight (its line-of-sight
  call, 0020:00A4 in the overlay's terms), -5 too far. A refusal is kind 7
  (`KIND_AIM`): the answer and the spell (DS:9428h) in the value, the caster
  (DS:9426h) in EXTRA.

### Choosing an enemy: Tab, Enter and the rings

([In the features page](FEATURES.md#choosing-an-enemy-tab-enter-and-the-rings).)

How: DSCLOG hooks the keyboard (`INT 16h`) and takes Tab, Shift+Tab and, with an
enemy chosen, Enter from what the game reads, counting them for the Loader
(`dsloader/targeting.py`), which marks the chosen one in DSCLOG's
`RING_TAB` (`dsloader/rings.py`). The ring is drawn in the floor pass, after the
shadows, through a table of each colour's redder one made from the palette. For
Enter, DSCLOG puts the pointer at the enemy's feet and gives the game a left
click there, from the main loop, while the routine that finds what is under the
pointer (`DSUN.EXE` 25B52h, `INT DBh`) answers with the chosen enemy for half a
second, whatever stands in front of it.

### Scrolling the map

([In the features page](FEATURES.md#scrolling-the-map).)

How: the game hears of the mouse's buttons from the mouse driver, through a
handler it gives it (`INT 33h`, function 0Ch). DSCLOG hooks `INT 33h` and puts
its own handler in between, which keeps the middle button (the wheel pressed)
from the game (the right button is left to it). The game's main loop
asks where the pointer is (to scroll at the screen's edge); there DSCLOG has
the game centre its view where the drag puts it, with the game's own routine
(the one clicking on the overview map uses, which draws the view again), and
keeps the pointer it reports off the edges meanwhile. The Loader only switches
it (`dsloader/scrolling.py`). (Turning the wheel isn't used: DOSBox 0.74,
GOG's, never passes it on to the game.)

**M, U and I.** `MAP_KEY`, in DSCLOG's `INT 16h` handler for both reads and
peeks, turns M into O (the game's key for its overhead map) while the map's
main loop has run within the last tick or two (`MAP_TICK`, set in
`PANEL_TICK`), and lets U and I (USE, inventory) through; `OVERHEAD` then holds
the key's letter. The same key again, the loop not run since (the screen pauses
it), turns into Escape, which closes the screen. U on the inventory or I on USE
goes through (the game switches screens) and moves `OVERHEAD` to it; any other
key there clears it. The game reads a key in its keyboard interrupt (35600h:
a peek, `AH=1`, then the read, `AH=0`), so `OVERHEAD` changes only on the read
(`MK_READ`), and both give the same key. `PANEL_TICK` clears `OVERHEAD` when the
map runs again.

**The whole party in view.** The map's party is one figure while `DS:1168h`
(`game.IN_COMBAT`: not 0 in a fight and while the party is spread out, so the
Loader's `in_combat` also asks the fight state's +19h) is 0
(each member's map record, `DS:6694h` + 32 a member, has 80h when inside the
leader's figure). The game's key table on the map (1587h:0FEBh, its handlers 34h
on) has 5 call 1587h:3109h (argument 1: the view drawn again), which spreads the
members round the leader and sets it, and 6 call 1587h:32E2h, which gathers
them; a fight's end calls that too (from 1D51h and 3490h, unless `DS:496Ah`).
Loading a game (69218h, reading `DARKRUN.GFF`) sets it from the members' 80h.
`SPREAD_LOAD` (site `NS_IMAGE+48`, over the load's `mov word [1168h],0`, 692CEh)
and `SPREAD_GATHER` (`NS_IMAGE+55`, over the gathering's, 1DFE8h, only when its
way back is a fight's end, not 6's 0CE2h) set `SPREAD_DUE`; `SPREAD_TICK`, in
`PANEL_TICK`, then calls 3109h itself on the map out of a fight, if the party is
still one figure. (A 5 put in the BIOS's buffer waits there: the game reads
keys only in its keyboard interrupt.) Switch: `gamepatch.PARTY_SPREAD`
(`party_spread`, on).

**The view in a fight.** The game writes the view's place (`DS:1178h`,
`117Ah`) in two routines that centre it (on a figure, `191F:01FFh`, and on a
spot, `191F:0281h`; their callers test first whether the figure is off the
screen, `0AC0:AC7Ah`) and in one that steps it toward a spot (`2191:0BE3h`,
with `27845h` deciding: the spot off the screen, or within the margins at
`DS:2F6Fh` to `2F75h` of an edge it is heading for). The drift in a fight is
the last, called from the routine that moves a fight's figure a step
(`0AC0:C7B3h`, at `C9F2h`) on every step (a monster's only while the game
shows monsters' moves, `ES:19h` of segment `377Eh`). Found with `INT 3` put
over the first byte of each routine in a test build of DSCLOG, which kept its
callers' return addresses: in a fight the centring routine was never called,
and every move of the view came from that call (returning to `1CA37h`), for
party members walking as well as monsters. The patch (`camera_still`, a
switch, `CAMERA`) rewrites that call's 54 bytes of set-up: while `IN_COMBAT`
(`DS:1168h`) is set (a fight, or the party spread out), the game's own on-screen test first, skipping the
step while the figure is on the screen; the figure's spot pushed straight from
its record (one `push dword`). The game's `mov ax,377Eh` stays at `CA15h`: DOS
adds the load segment to that word as the game loads (the EXE's relocation
table), and a first version, which put other code there, ran garbled.
`gamepatch.patched` now refuses any patch that changes a word DOS relocates
(`gamepatch.relocated`). Out of a fight the same routine runs too (the arena's
opening, the party walking out through the gate: held still, the party never
left the view and the scene never went on), so there it is as the game has it,
as is the map's own walking.

### The pointer in scenes, and where it starts

([In the features page](FEATURES.md#the-pointer-in-scenes-and-where-it-starts).)

How: the scenes (the intro, its logos, the decree and the rest) are played by
one routine (`DSUN.EXE` 568BEh, each piece through `660:20`), whose player
asks the game's event queue between a piece's steps (`929F5h`); a key, DX 1,
ends the scene (`92A28h`). The game's own mouse handler isn't installed yet in
the intro, and the mouse driver's pointer can't be drawn there: the scenes'
VGA mode is unchained (mode X, 4 planes, page flipping), which DOSBox's driver
draws as garbage. So DSCLOG draws the game's own arrow (its pointer on the
menus, `RESOURCE.GFF`'s ICON 6001, 10 by 13 in 11 colours of `GPLDATA.GFF`'s
palette). The Loader reads it from the player's game at each start
(`scenepointer.py`) into `dos\POINTER.BIN`, which DSCLOG reads over its
`CP_DATA` as it loads: the rows, the colours (6 bits a part), then each row's
pixels as colour numbers, ending with 0. Without the file DSCLOG keeps a plain
black and white arrow of its own, so nothing of the game's is in the mod.

- **At each step** (`CINE_STEP`, the step's `or dx,dx / jz`): a button pressed
  since the last step (`INT 33h` function 5, both buttons) makes DX 1, as a key
  does. At most 30 times a second the arrow is wiped and drawn again where the
  driver has the pointer (function 3), each of its colours as the scene's
  palette's nearest (read from the DAC, the three parts' differences summed; of
  equals the last, as a picture seldom uses them), in the page shown (the CRTC's
  start address), each pixel's plane selected with the sequencer's map mask and
  the graphics controller's read map (both saved and put back, with the
  controller's mode, bit mask, set/reset and rotate). What was under it is kept,
  and put back only where the arrow still is: a frame drawn over it since stays
  as it is.
- **From the game's timer** (`PROBE_TICK`, while a scene plays): 30 times a
  second the arrow follows the pointer, and about 7 times it is drawn afresh,
  palette and all, so a still picture fading in shows it. The game writes its
  palette with interrupts off, so the timer never reads the DAC halfway
  through its writing.
- **At the scene's start** the driver's ranges are made the screen's (0 to 319,
  0 to 199; its own are 640 across) and the pointer put where it was last
  seen (`MP_X`, `MP_Y`: the arrow's place in a scene, the game's mouse events'
  out of one; the middle at first); a video mode set puts them back, which the
  next step sees (an x past 319) and sets again.
- **At the end** (`CINE_END`, the scenes' routine's `or si,si / jz`, where
  every scene comes, played or skipped) the arrow is wiped.

**Where the pointer starts.** After a video mode set the driver puts its
pointer in the middle of its 640 across; the game then gives it the ranges 0
to 319 (`2A8F2h`), which leave it at the right edge (318, 100). Just after
that (`MOUSE_SET`, its `mov word [0A12Dh],0`) DSCLOG moves it back to where
it was last seen when it is there (function 4; `MP_X`, `MP_Y`, kept by the
scenes' arrow and by every mouse event the game is sent: the middle before
the first), so a pointer moved in the intro or on a menu stays put through the
next screen's video mode set. The driver's own speed is 8 mickeys a pixel
across and 16 up and down; as the game resets the driver at its start
(`MOUSE_INIT`, `356F5h`, after function 0) and again with the ranges, DSCLOG
makes them 8 and 10 (function 0Fh): the window's aspect correction makes a
pixel 1.2 times as tall as it is wide, so 10 moves the pointer as far on the
screen up and down as across.

**Its speed in a window.** With the mouse captured, DOSBox 0.74 moves the
driver's pointer by the desktop mouse's motion times 8 over the mickeys a
pixel (`Mouse_CursorMoved`: one game pixel for each desktop pixel at 8), so in
the usual window, three times the game, the pointer moved three screen pixels
for each one the desktop pointer would: fast, and in steps of three, which
made placing items fiddly. The Loader's DOSBox settings set the mouse's
`sensitivity` (which scales that motion) to 100 over the window's scale, 33 in
the usual window (`launch.display_lines`, with `MOUSE_START`), and
`autolock=true`, as GOG has it: uncaptured, DOSBox reads the desktop pointer's
place in the window instead, which the sensitivity would scale too. In full
screen the scale depends on the monitor, and DOSBox's own is kept.

The two are switches (`SCENE_POINTER`: `cine_step`, `cine_end`; `MOUSE_START`:
`mouse_set`, `mouse_init`). The room in upper memory came from the freeze
report's records (32 to 16, taken half as often).

### More saves

([In the features page](FEATURES.md#more-saves).)

How: the save names the game searches the folder for and writes a save to
(`SAVE??.SAV`, `SAVE%.2d.SAV`) are two strings in its memory; DSCLOG changes
their fourth letter for the page. The window's event routine leaves keys and
buttons it has no use for to a jump to its end; the patched game has DSCLOG
take them there (`INT D8h`, `INT D7h`), and for a new page run the window's
own routines that search the folder, draw the rows and draw the window. Enter
is taken out of the window's key table, so it comes to DSCLOG too, which goes
on to LOAD (or SAVE) as the table did, but not on a row with no save. The
buttons are the game's kind, in the Loader's copy of `RESOURCE.GFF`: placed
in the window under EXIT, with pictures made from EXIT's, its letters taken
away and the page's put in with the game's text font
(`dsloader/savepages.py`; the buttons' own carved letters have no P, G or
digits).

Saves under their names (`dsloader/namedsaves.py`): every few seconds the
Loader looks at the 40 slots' files (`cloud_saves` before the game folder, as
GOG's DOSBox mounts it over the folder), and copies one newer than its copy to
`Named saves/` as `Page P slot NN - NAME.SAV`, the name from the save's
`STXT 1` (up to its first NUL; characters Windows won't take become `_`). A
slot's copy under another name is removed. **Put a save in a slot...** copies
a file back as `SAVE`/`SAVB`/`SAVC`/`SAVD` + the slot.

### More characters

([In the features page](FEATURES.md#more-characters).)

How: the game's file routines take any number; only its loops over the
characters stop at 20, its roster list has room for 20 and its "Maximum
characters" check counts to 19. The patched game has 30 and 29 there
(`dsloader/gamepatch.py`, a byte each).

A New character counts as Okay wherever the game tests for Okay: a jump each
(`NEW_AS_OKAY` in `dsloader/gamepatch.py`), and `game.py` does the same.

### Game speed

([In the features page](FEATURES.md#game-speed).)

**Steady pace** (`gamepatch.STEADY_PACE`, DSCLOG's STEADY PACE): the map's
frame (DSUN.EXE 1E8E4h) calls the step for everything (`call far 1DF3:26DC`,
which also builds the list of what moved at DS:57D0h, 10 bytes each: where
the thing was drawn, its size, the thing) and then the drawing of that list
with the page flip (`call far 1DF3:15EA`), the flip waiting for the vertical
retrace. The game has no other clock for walking: a step is a frame, and the
"think" that starts a figure on its next square runs once a frame, for one
creature at a time, so catching up a figure's animation steps alone (tried
before) only made it wait at the end of its square. PROBE_PACE_DRAW keeps a
schedule of 70 frames a second on the game's clock (DS:11D6h, 96 ticks a
second: a tick 70 units, a frame 96): at a frame or more behind, on the map (a
fight, the fight state's +19h, draws every frame), the drawing and its flip are
left out and the list is kept in the far block (FAR_PACE, 64 entries); the
next frame drawn has it added after its own, so the old places of what moved
in the skipped frame are drawn over too. PROBE_PACE_PASS sets "something
moved" after the step when a kept list has waited 2 ticks, so a frame is drawn
for it though nothing has moved since. A pause of 8 ticks (a load, a talk)
starts the schedule afresh; at most 4 frames are owed.

To count the pictures the game shows, watch the word at offset 118Eh of the
flip routine's own code segment (the routine at DSUN.EXE 14414h toggles it at
each flip): with the whole party walking in the slave pens it changed about 37
times a second without steady pace and 27 with it, the step a picture going
from one to two or three.

The Loader's drawing is as cheap as it can be without looking any different:
a shadow is darkened a plane of the video memory at a time (the graphics
card's registers set four times for a figure, not four times for each of its
rows), and a dust puff's pixels are worked out a row at a time, only within
its outline and the part of the view being drawn again. The pictures the
Loader draws the party's gear on are each exactly as long as their outfit,
with only the room gear needs round the figure while walking (6 pixels at the
sides, 2 above; 10 in a fight), since the game draws a walking figure's whole
picture at every step.
