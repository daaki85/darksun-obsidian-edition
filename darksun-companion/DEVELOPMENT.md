# Obsidian Edition: development

How Obsidian Edition and its companion window, Templar's Ledger, work inside:
the patched game and its helper, what's known of the game's data, the tools
for mapping it, and how each part of the [README](README.md) is done.

## How the dice log works

Every roll in the game goes through one function, Borland C++'s `rand()`.

1. When you start the game with the dice log, the launcher writes
   `dos\DSUNLOG.EXE`: a copy of the game's `DSUN.EXE` with 185 small
   changes, listed in `PATCHES` in `dscompanion/gamepatch.py`. Most replace a
   few bytes of the game's code with an `INT` (60h to 65h, and 8Ch to FEh;
   all of them are taken, so later sites share one, a site number after the
   `INT`, as in [Scores and hit points as
   rolled](#scores-and-hit-points-as-rolled)) that the helper answers: `rand()`, the saving throw, AC, the dialogue
   window and message boxes for the dice log; the inventory, View Character,
   USE and Effects screens and the Look box for what the Ledger adds to them;
   and the places each rule change, new item and screen addition needs. The
   sections under [How each part works](#how-each-part-works) name the patches
   each part uses. One, at the start of a monster's turn, is in overlay code
   the game moves or unloads to load the dialogue window's, so the helper puts
   its way back in a stack frame the game's overlay manager fixes up (a stale
   address used to restart a fight, or stop the game with "Stack overflow!").
   A few patches change the game outright: 29 saved characters rather than 19,
   DELETE deleting the one chosen and a New character counting as Okay (see
   [more characters](README.md#more-characters)), Enter loading only a save
   that is there (see [more saves](README.md#more-saves)), a script buffer of
   11,776 bytes rather than 10,000 (for
   [Dinos and the Trustee](README.md#what-dinos-and-the-trustee-say-about-them)),
   and data files looked for in the current folder rather than next to the
   program. The helper also hooks DOS's `INT 21h`, to open the launcher's
   copies of `SEGOBJEX.GFF`, `RESOURCE.GFF`, `GPLDATA.GFF` and some regions'
   files (for the [new items](README.md#new-items), [Kalzith](README.md#kalzith),
   [Semyon](README.md#semyon) and [no manual check](README.md#no-manual-check)),
   the mouse driver's `INT 33h` (for [scrolling the map](README.md#scrolling-the-map))
   and the keyboard's `INT 16h` (for Tab and Enter). DOSBox runs it from the
   game folder, so it uses your saves as usual.
2. `dos\DSCLOG.EXE` (source in `dos\dsclog.asm`) is a tiny DOS program loaded
   into upper memory before the game, so the game loses no memory. It answers
   those interrupts. Its `rand()` returns exactly the numbers the original
   would and also records each call, what code called it, and that code's
   arguments (dice count and sides, THAC0, AC...) in a ring buffer. Others
   record the final saving throw total, the AC the game uses, and the text
   of dialogues and messages (in a second buffer); the rest draw the in-game
   additions and make the new items and the rule changes count.
3. Templar's Ledger finds the buffer in DOSBox's memory and reads it every 50 ms.
   It works out what each roll was for from the code that asked for it, and
   reads the rest (names, weapons, spells, effects) from the game's own data.
4. To keep bursts of unimportant randomness from crowding out the rolls that
   matter, the helper only records calls from code it knows how to label,
   unless **Show unlabelled rolls** is ticked.

Because the replacement produces identical numbers, the game plays exactly as
it would without it, apart from what you choose on the Options tab (picking
pockets, the [rule changes](README.md#rule-changes)), the Ledger's other
additions (the new items and the Ring +1, the cooked vulture, Kalzith, Semyon,
what the party wears, shadows, dust, rings, Tab and Enter, scrolling) and the
fixes always in the patched copy: no equipment penalty on thief skills (see
[Thief skills](README.md#how-the-game-works-out-thief-skills)), the roster's DELETE and New characters counting
as Okay (see [More characters](README.md#more-characters)), and no manual check
(see [No manual check](README.md#no-manual-check)).

Limitations:
- Only the GOG release (`DSUN.EXE` of 611,408 bytes) is supported. With
  another version the launcher starts the game without the dice log and says
  why.
- Outside combat, the thief skill, trap and ability checks, the character
  creation rolls and searching junk, hay and wardrobes are labelled; other
  rolls there (for example treasure or
  random encounters) show up only with **Show unlabelled rolls**, as raw
  numbers.
- A save-file load from the main menu is recognised, so the spells already
  active in it aren't reported as new. Loading a save of the same party in the
  middle of play isn't, and its effects may be listed as if just cast.
- Dialogue speakers are portrait numbers until the log learns their names or
  you name them (see above): the game doesn't keep a name with the dialogue.
  A learned name is the creature the conversation was started on, so a scene
  in which one face speaks for someone else would get that someone's name.
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
another. Old copies of a record can linger elsewhere in memory, so the viewer
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
starts with Borland's copyright string at `DS:0x0004`, which is how the viewer
finds the party by itself (`dscompanion/game.py`).

**Items.** A creature's items hang off its record at `+0x08`, `+0x0a` and
`+0x0c`: each is an object number (the object table has a kind, 1 for an item
and 2 for a creature, and an index), the first item of a list, whose own
records then name the next. Items are 21-byte records (`DS:0x165D`), item
types 20-byte ones (`DS:0x1669`, 115 of them, from GPLDATA.GFF):

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

Free item records and free objects are kept in lists (`DS:0x4D76`,
`DS:0x4D72`), which is how the Ledger adds [the Ring +1](README.md#new-items) and
Kalzith's scrolls as the game would.

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


## Reading the game's memory

DOSBox keeps the emulated PC's RAM in one block of its own process memory. The
tool finds that block by looking for the BIOS date string DOSBox writes at
guest address `0xFFFF5` ("01/01/92"), and checks it against the interrupt
table at guest address 0. After that, reading the game's memory is a plain
`ReadProcessMemory` at `block + guest address`. Dark Sun is a 16-bit real-mode
program, so a `segment:offset` address is simply `segment × 16 + offset` in
guest memory. If detection fails on an unusual DOSBox build, you can pass the
block's host address with `--host-base`.


## Development

```
python -m unittest discover -s tests
```

`tests/test_dsclog.py` runs the helper's interrupt handlers in a CPU emulator
when `unicorn` is installed (`pip install unicorn`), and is skipped otherwise.
After changing `dos/dsclog.asm`, rebuild the helper with
[NASM](https://www.nasm.us/):

```
nasm -f bin -o dos/DSCLOG.EXE dos/dsclog.asm
```

The header's signature (`DSCLOGvY` now) goes up whenever the helper and the
Ledger must change together (`HDR_SIG` in `dscompanion/dicelog.py`), so a
Ledger never talks to an older helper.

The post-game check that keeps an error on screen for the crash report is
built the same way:

```
nasm -f bin -o dos/GAMEEND.COM dos/gameend.asm
```

### From a command prompt

What the `.bat` files do, from a command prompt (`dscompanion` is the
program's internal name):

```
python -m dscompanion launch                        # start the game with the dice log, and the viewer
python -m dscompanion view                          # the viewer only
python -m dscompanion play                          # the game with the in-game additions, no viewer
python -m dscompanion dicelog                       # the dice log in the command prompt
python -m dscompanion save C:\path\to\SAVE01.SAV   # the party stored in a save
python -m dscompanion processes                     # is DOSBox found?
```

If more than one DOSBox is running, add `--pid <number>` (from `processes`).

### Mapping memory

For Shattered Lands the party is found automatically. The steps below are for
mapping new fields, or for other layouts:

1. Type a party member's name under **Locate by name** and press **Search**.
2. Select the hit that is the character's record and press **Assign**.
   In the hit list, the record shows its name followed by dots, since binary
   data follows the name. A copy in a text buffer is followed by more text.
   Slots 2–4 follow automatically if the party's records sit next to each other
   in memory, as they do in save files. Otherwise assign each slot by name.
3. The **character sheet** (XP, classes, levels, saves) is found automatically:
   it carries the same ability scores and entity ID as the creature record.
4. **Save layout** (beside **Search**) stores the addresses. They may change when you load a save
   or restart the game. If a slot starts showing garbage, locate it again.

The **Record bytes** panel shows the raw record. Bytes that change light up
orange, and clicking a byte decodes it as u8/s8/u16/s16/u32. Use it to map
fields that aren't known yet. Watch a byte change as you take damage, spend
PSP, or equip armour, then add it to `layouts/shattered_lands.json` and press
**Reload layout**.

### Command-line mapping tools

```
python -m dscompanion find-text Daaki               # hex dump around each hit
python -m dscompanion dump 0x1a2c 128               # hex dump an address
python -m dscompanion search u8 23 --near 0x1a2c    # Cheat-Engine-style value search
python -m dscompanion next 17                       # ...narrow after the value changes
python -m dscompanion next decreased                # also: changed, unchanged, increased
```

## How each part works

For each part of the README, how it's done: where the patched game calls the
helper (DSCLOG), and what the Ledger reads and writes. The heading names the
README's section.

### The Dialogue tab

([In the README](README.md#the-dialogue-tab).)

The game keeps the clicked reply's row at DS:1F0A while it flashes it; the log
reads the reply's text from the game's own list.

### Searching junk, hay and wardrobes

([In the README](README.md#searching-junk-hay-and-wardrobes).)

How: the scripts' random command has a routine of its own in the game; the
patched game has DSCLOG look in there (`INT D3h`), which records the roll, its
range, where the running script is (which tells the three searches and their
damage rolls apart) and the three counts (`dscompanion/searches.py`). Tested
in play: a haystack search in the slave pens logged `0-10 = 7, an old, soiled
loincloth (the party's 2nd find of 6 in hay)`, as the game's own message said.

### THAC0, saves and thief skills

([In the README](README.md#thac0-saves-and-thief-skills).)

How: the patched game calls the helper (`INT 65h`) just after the panel's
weapon lines; the helper prints the lines with the game's own text routine,
whose address, like the selected character, it reads from the game's code
around the patch (overlays move, so nothing is fixed in advance). The View
Character screen does the same through `INT F3h`, called once it has drawn
the character's two panels (the saves under the item icons; MOVE, the
creature record's +1Bh, and THAC0 at x D8h on HP's and PSI's lines, 7Fh and
86h, clear of HP's value at its longest), and the routine that lists the weapons through `INT FAh`
after each one. The Ledger keeps the numbers in the helper's memory, with the
time it last did: older than 5 seconds, the helper shows the sheet's numbers
instead. Before a screen is drawn, the helper asks the Ledger to update them
and waits for its answer, half a second at most. Nothing else in the game changes.

Which class levels up next, on View Character: the game looks up the XP for
each class's next level in its tables and shows the lowest. Where it adds the
closing bracket, the helper (`INT D2h`) finds which classes that number
belongs to and adds their letters first.

### Each turn's rolls

([In the README](README.md#each-turns-rolls).)

How: the patched game calls the helper (`INT F1h`) in its combat loop, right
after the call that may pass the turn on. When whose turn it is has changed,
the helper counts it and waits up to a third of a second for the Ledger,
which writes the summary into the helper's memory; the helper then feeds it to
the game's dialogue window the way the game's scripts do for a narration
(the emblem, the text, "Press continue"). If the Ledger isn't running, or the
box is unticked, the game doesn't wait at all. (INT 66h-6Fh can't be used: the
game calls those itself, looking for sound drivers.)

### What hurts a monster (the Look box)

([In the README](README.md#what-hurts-a-monster-the-look-box).)

How: the patched game calls the helper (`INT F5h`) where the box has drawn its
first status rows; the helper asks the Ledger (as for each turn's rolls), and
prints the lines with the game's text routine. `INT F6h`, at the end of the
routine that closes the box, shows the whole description.

### Charges in item boxes

([In the README](README.md#charges-in-item-boxes).)

An item that casts a spell has the spell + 1 in its `+0Fh` and its charges
left in `+0Eh` (the routine finishing an item's use takes one off, 721E4h,
unless its type's `+0Fh` has 2). `PROBE_ITEM_BOX` (`INT DAh`, at the end of the routine filling an item's box,
8C1A1h, the item `[BP+6]`) draws `Charges: n` in the row after the box's own
lines (`IB_CHARGES`) when the spell byte is below F9h (from there the game's
own effects: a belt's STR, a ring's AC...) and the charges aren't 0, but not
for fruit (type 60, eaten whole).

### No manual check

([In the README](README.md#no-manual-check).)

How: the dragon's question is the game's script 20, which script 120 runs (a
call into another script, command 14h) when the party leaves the warrens
(region 28h) until bit 12 of the game's variable (135, 73) is set. The right
answer goes on to script 86 at 1087, which sets 255 in the variable (7, 4)
and, in region 28h, that bit. In the Ledger's copy of the scripts
(`dscompanion/manualcheck.py`), script 20 does just that and ends: the same
start (offset 1, its one entry in the game's table of entry points), no words
and no question. It is replaced only if it is the dragon's (its
`" word on page "` line).

### STORE and RECALL

([In the README](README.md#store-and-recall-on-the-creation-screen).)

The buttons: the creation screen is window 3011 in `RESOURCE.GFF`, its buttons
the die (7DAh), EXIT (80Ah), DONE (7D0h) and the rest. In the Ledger's copy
(`dscompanion/rollstore.py`) it has two more, STORE (8A0h) and RECALL (8A1h),
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
`+21h` to `+23h`, `+43h`); at each button pressed the probe forgets the
stored roll if those have changed (`RS_SAME`), so RECALL finds none. RECALL
then shows them as the game would: the scores through the screen's
own redraw (the creation overlay's stub, entry BBh, which a score's click
calls; `RL_SUM` adds the totals), and the rest by running the die's routine
from where it has rolled the hit points (659D0h, with its stack frame and DI
1): the hit points shown, the PSP worked out again (65B39h, which rolls
nothing) and shown, then the AC and damage. The overlay's segment is the
INT's return.

### Weapon specialization

([In the README](README.md#weapon-specialization).)

How: the chosen weapon types are kept in four bytes of each character's own record that the
game never uses (+14h to +17h), so saves and the saved-characters roster keep
them. The helper adds the bonuses and attacks where the game makes a weapon
attack (`INT D1h`, `INT D0h`), on the DAM lines (`INT CFh`, `INT CEh`), runs
the creation pages (`INT C8h` to `INT C3h`, windows 3014 to 3019 in the
Ledger's copy of `RESOURCE.GFF`), calls the game's psionic pop-up in weapon
mode at a level gained (`INT C2h`, then `INT C1h` to `INT BCh` in the pop-up,
window 3021), and prints the Effects screen's lines (`INT BBh`).

The pop-up in weapon mode is the psionicists' window (17501) made bigger:
window 3021 is 214 by 156 (its marble, BMP 3022, the psionicists' 17001 carried
on to that size), with a slot for each weapon type, six to a row: a button 0x860 +
type whose picture (ICON, same number) is the game's inventory picture of a
weapon of that type (`weaponpages.PICTURES`, objects in `SEGOBJEX.GFF`; the
polearm's made smaller) on a slot, in three frames as the game uses them: as
it is, lit (the pointer on a button in use), and out of use (the weapon a grey
shape). The game puts the window where it would centre the psionicists'
(`push 2B0050h` before `PROBE_PK_WIN`), so `PROBE_PK_WIN` gives it the place
that centres 214 by 156; `PROBE_PK_TITLE` puts the two lines under the slots,
centred in the wider window (the routine's width and y, pushed as bytes after
it). Naming the slot under the pointer: a button in use takes the pointer
itself (its lit frame), so no cell handler of the window (530:43h, as the
powers' cells have) ever hears of it; instead `PK_HOVER` (a site of `INT 98h`,
new: `or ax,ax / jnz 85F5Dh`, 4 bytes at 85F44h, in the pop-up's event loop
85F2Ch, the jump done by the probe) reads the pointer each time round
(`INT 33h` function 3), finds the slot from the window's place and the slots'
(`PK_SLOTS_X`, `PK_PITCH`; `test_picker_matches_dsclog` keeps them
weaponpages'), and when it changes draws **SPECIALIZE IN** (or **EXPERT IN**:
`PK_WORD` puts the type in the sheet's first empty slot for a moment and asks
`SPEC_OF_SHEET`, as `weaponchoice.pick_word`) and the type's name
with the routine the powers' handler names a power with (85CC9h, which rubs
out the lines it drew before), or the title again off the slots.
A missile weapon's attacks a round are its item type's (+0Bh, in halves: a
bow 4, the rest 2), not the character's (sheet +2Ah) as in melee; `INT D1h`
raises them to a specialist's (`MISSILE_RATE`, by the fighter, gladiator or
ranger level; a grand master one more; a weapon type not chosen, from 7th level, a
specialist's a band lower), and the Ledger's Characters tab does the same
(`specialize.missile_attacks`).
Every ranger's expertise with the bow is in `SPEC_OF_SHEET` (`specialize.skill`),
not in its chosen weapon types, so `KINDS_ALLOWED` (`restrict.allowed_kinds`) leaves
the bow out of a ranger's choices.

### Class restrictions

([In the README](README.md#class-restrictions).)

How: the helper adds the classes' limits where the game checks an item against
the classes allowed to use it (`INT CDh`), and a multiclass preserver's armour
where the game checks for "No spell use" (`INT CCh`). (`dscompanion/restrict.py`
says the same in Python, for the tests.)
A weapon the character has made its own is left as the game has it, past the
classes' limits (`SPECIALIZED_BACK`, `restrict.specialized_back`): a dual-classed
human's chosen weapon specs once its new class's level has passed the warrior
class's, and a ranger's bow (every ranger has expertise with it, but never
chooses it): a multiclass ranger's always, a human's while a ranger or once past.
`KIT_FORBIDS` likewise passes a weapon of a type in the sheet's `SPEC_SLOTS`
(`KF_CHOSEN`) while the specs count (`SPECS_AWAKE`, `restrict.specs_awake`: one
class; a human's warrior class now or passed; a Battle Mage's kit awake), but
for the off hand's rules and when a weapon spec is being chosen (`KF_SPEC`).

### Multiclass hit points

([In the README](README.md#multiclass-hit-points).)

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

([In the README](README.md#hit-dice-the-better-of-two).)

How: where the game has rolled a level's die (`INT BAh`, in place of the
`mov cx,ax` after the roll, DSUN.EXE 87319h), the helper keeps the first roll
and sends the game back to the start of its roll (872FDh), so both rolls are
the game's own and the dice log sees both; the second time it keeps the
better. Creation goes through the same routine, a die for each starting
level.

### Scores and hit points as rolled

([In the README](README.md#scores-and-hit-points-as-rolled).)

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
`RL_ROLL` 3, `RL_SUM` 4, `RL_CON` 5, `RL_TRY` 6) where `PROBE_CR_SPELLS`'s own has its NOP; the
helper moves the return address past it.

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
  under CHR, with the game's text routine as the Ledger's other lines are.
  The scores' box is made a line taller and wider (`rl_sum_box`: x2 48 to 77,
  y2 178 to 185, in the game's data) so the copy put back clears them.

The dice log adds the six's total to the creation lines. The die rolls a
whole character many times while it tumbles, about 100 `rand()` calls each,
more than the ring holds between two reads, so the log used to miss a
character's rolls. `RL_TRY` (6, whatever the rule, in place of
`add ax,[499Ah]` + NOP at 6498Bh, in 6490Dh: AX a 4d4, `[BP+8]` the ability,
DI the try) keeps each 4d4 in the header (`+282`, four for each ability) and
counts them (`+280`); the log reads them once the count has been still for
0.3 s, and doesn't report the ring's missed rolls while it moves.

Checked in the game: three rolls of the die, every ability's line complete
(none "too fast"); CON 14 to 15 to 16 took a 3rd-level preserver's hit points
from 8 to 11 to 14, and back down; a preserver rolled 101 (`SUM:101/101`); DEX lowered and
STR raised by one, a second raise refused; the hit points unchanged by left
and right clicks (with the rule off, 16 to 17); the die's next roll
`SUM:98/98`, as the dice log's line; a new class raising INT from 14 to 17
took a fighter's 98 to 101. DONE on a preserver still opened CHOOSE A SPELL
(`PROBE_CR_SPELLS`).

### Rangers' casting level

([In the README](README.md#rangers-casting-level).)

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

([In the README](README.md#preservers-int).)

When a scroll's icon is clicked in its box, the game's routine (DSUN.EXE
8B690h) asks whether the character on show may learn the scroll's spell
(500:39h: only whether it already knows it; then 8B6D3h's `or ax,ax`), and
if so teaches it (500:43h sets the low four bits of its byte in the known
spells' table), uses the scroll up and says YOU LEARN THE SPELL (`push
ds / push 33F1h`, 8B712h); if not, YOU ALREADY KNOW THIS SPELL (`push ds /
push 3405h`, 8B719h) and the scroll is kept. Each spell's level is a byte of
the game's table of spells at the load segment + 3FB9h, 19Ch + 7 a spell
(`SPELL_LEVELS`; `GameData.spell_level`).

How (`RULE_HI_INT`, the second rules word's 4: `game.RULE_INT_LEARN`):
`PROBE_SCROLL_LEARN` (`INT A9h`) goes on to `INT_LEARN` for a preserver (the
class among its sheet's) and a wizard spell. Its INT is the creature
record's (`+25h`), its row of `INT_CHANCE` and `INT_MOST` (`intlearn.py`);
`LEVEL_FULL` counts the wizard spells of the scroll's level it knows. Full:
AX 0 (the game refuses, the scroll kept), and `PROBE_LEARN_REFUSED` (`INT
91h`, new, 8B719h) pushes TOO MANY SPELLS OF THAT LEVEL in place of the
game's message. Else a d100 of the helper's own (`D100`: a generator
stirred by the BIOS's timer ticks); over the chance, the game teaches the
spell and uses the scroll up, and `PROBE_LEARN_SAID` (`INT 92h`, new, 8B712h)
takes it back (the four bits cleared) and pushes YOU FAIL TO LEARN THE SPELL.
Each try is told to the Ledger in the helper's header (`+272`: a count, then
the member, spell, INT, chance, d100 or spells known, result;
`DiceLog._learn_lines`). At a level up (and a new preserver's picks),
`PROBE_PICK_LIST` drops the game's list's spells of a full level, and
`PROBE_PICK_ANY` (`PICK_INT_ANY`) doesn't open CHOOSE A SPELL when no unknown
wizard spell is left at a level on offer that isn't full.

### AD&D's class tables

([In the README](README.md#adds-class-tables); `tables.py`.)

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
`PROBE_XP` (`INT 90h`) replaces `imul eax,eax,64h` where a level up
(87BBBh) and View Character (67D41h) read the table: `XP_NEED` gives the row
and level's from `ADND_XP` (`PROBE_XP_NEXT` uses it too). `PROBE_PRIEST_THAC0`
(`INT 8Fh`) replaces `mov [bp-2],ax` (876ABh) in the THAC0 routine's loop:
for the priest group (CX 0), 2 x (level - 1) / 3. `PROBE_ADND_SLOTS`
(`INT 8Eh`) replaces `nop / push cs / call 5E4C2h` (5E240h): for a cleric,
druid or preserver it calls the routine with the level byte 0 (WIS's part
alone; the routine keeps only SI, DI and BP, so the probe keeps the rest)
and adds `ADND_SLOTS`; anyone else, or with the rule off, the routine as it
was.

### The leader's CHA at shops

([In the README](README.md#the-leaders-cha-at-shops); `prices.py`.)

The shop (overlay at 83000h) reads an item's price, the word at its `+6`,
straight from the item: `mov cx,es:[bx+6]` to charge it (8384Bh: times the
count for a stack, against the party's money, the dword at 2C0:357h; NO
DEAL!, DS:2EE7h, if short) and to show it under the item (83BB1h, as
`%d$`), and `movsx eax,word es:[bx+6]` where the list colours an item the party
can't afford (8310Ch). Selling (83CCAh) is left alone; 9999 there is "I
COULDN'T SELL THAT".

How (`RULE_HI_CHA_PRICES`, the second rules word's 16: `game.RULE_CHA_PRICES`):
`PROBE_PRICE` (`INT 8Dh`) at the first two and `PROBE_PRICE_EAX` (`INT 8Ch`)
at the third read the price and pass it through `CHA_PRICE`: the leader is
the party member at `DS:4979h` (whose turn it is; outside a fight, the
leader), its CHA its creature record's `+27h`; the price times (100 − 5 for
each point of CHA past 15, at most 25) / 100, never below 1, and 9999 kept.

Checked in the game: with a CHA 20 leader, Kalzith's scrolls showed 2,250,
4,500 and 6,750 (25% off 3,000, 6,000 and 9,000) and each was charged that.
A bought item stays on the pointer until it is put down (the game's held item,
`DS:17A0h`), and the shop takes no other click meanwhile.

### Spells saved against with the spell save

([In the README](README.md#spells-saved-against-with-the-spell-save).)

How: the Ledger writes the game's own table that turns a spell's kind of save
into one of the five (a table of words at DS:1E75h, read afresh for every
save), and puts it back when the rule is unticked.

### Fire, cold and electricity: DEX instead of a doubled d20

([In the README](README.md#fire-cold-and-electricity-dex-instead-of-a-doubled-d20).)

How: the helper does the save's doubling (`INT F0h`) only while this rule is
off, and the Ledger marks the fire, cold and electricity spells with the game's
own "can be dodged" flag (bit 40h of the spell's category word), which no spell
has, so the game's save routine adds the DEX defensive adjustment from its own
table.

### Two weapons: AD&D's penalties

([In the README](README.md#two-weapons).)

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

### Thief skills from AD&D's table

([In the README](README.md#thief-skills-from-adds-table).)

How: where the game's thief skill routine adds 4 a level, the helper
(`INT E4h`) puts AD&D's number for the level in place of the game's base and
level, adds the DEX table's, and jumps past the game's DEX formula to its
armour and effects. The Ledger's screens and the inventory screen's panel
work the chances out the same way.

### Hiding in shadows to backstab

([In the README](README.md#hiding-in-shadows-to-backstab).)

How (the cloak, boots and belt): the patched game's item box (`INT DAh`, where it has drawn the name) asks
the helper, which draws the line with the game's own text routine when the
item's type is worn as a cloak, on the feet or as a belt; and at the end of the
game's thief skill routine (`INT D9h`, where it returns the chance, armour and
effects counted) the helper adds the belt's 5 to picking pockets and opening
locks for a thief wearing one.

How (the rolls): the Ledger rolls both when the turn passes to the thief and tells the
helper, which, where the game has just worked out whether an attack is from
behind and a backstab (`INT EAh`), makes the hidden thief's next one so, by
the game's own conditions for a backstab (a thief, in melee, a weapon of
weight 40 or less).

### Picking pockets

([In the README](README.md#picking-pockets).)

How: the patched game's routine that uses the item on the pointer on
something on the map tells the helper what was used on what (`INT FDh`). For
the thieving tools on someone, the Ledger rolls and moves the item, and the
helper shows the result instead of the game's "nothing happens".

### Levels up to 10

([In the README](README.md#levels-up-to-10).)

How: the game holds a class level against 9 in two places, where a character
goes up a level and where View Character shows the XP for the next one; the
helper (`INT E7h`) holds it against 10 instead while the rule is on.

### Items saving against acid

([In the README](README.md#items-saving-against-acid).)

How: where the game works out the number a weapon's d20 must reach
(`INT D6h`), where it skips the roll for armour with no magical power
(`INT D5h`) and where it works out armour's number (`INT D4h`), the helper
gives the easier of the two and records the check for the dice log.

### Half-giants' two-handed weapons

([In the README](README.md#half-giants-two-handed-weapons).)

How: the inventory screen checks a weapon type's two-handed bit (+0Fh, 40h)
twice when something goes into a hand: the other hand's ("Two handed weapon in
use") and the one going in ("Need two free hands"). The helper (`INT E3h`)
answers both for the character on show, "not two-handed" for a half-giant.

### New wizard spells

([In the README](README.md#new-wizard-spells).)

**Numbers.** The game's spells are 0-68 wizard, 69-137 priest, 138-171 psionic
powers and 172-195 monsters' powers. Its table of 32-byte records (from the
load segment + 3E3Fh) has an unused 96 bytes after 195, room for 196-198; 199
on is live data (3E45h), never written. Cat's Grace is 196, Erdlu Claw 197,
Fogbolt 198. When the rule switches on, the helper (`NS_SETUP`) copies in each
one's record from a game spell it works like, Strength (23), Enlarge (5) and
Charm Person (2), with its own effect number and, for Fogbolt, its own
duration (2d4 rounds) and save, and each one's sounds and Fogbolt's bolt
(below); writes their rows in the spell rows (level,
mask, name, `3FB9:19Ch`, 7 bytes each); and gives the effects' table (6 bytes
each, from 3F8Dh) their names and icons.

**Known.** The game keeps a party member's known spells in a table of its own
(8Ah bytes each), with no room for more. A new spell's is a bit in the sheet's
`+45h` (bits 4-6; the low nibble is the Elementalist's second sphere): the
routine that finds a spell's known byte (500:48h, `NS_KNOWN` at 5DD04h) and
the one that teaches it (500:43h, `NS_LEARN` at 5E3F7h) go to the helper for
them, and the three lists that end at 8Ah end at 0C7h (5DDEFh, 5DE72h,
5DF06h). Creation and DUAL clear the bits with the rest of the spells; the
level-up pick, the starting picks and the INT limits count them.

**A wizard's spell.** About 35 places tell spells apart by comparing the
number with 45h, 8Ah, 0ACh or 0C4h (the USE screen, the cast, the caster's
level, a scroll used...). Each such compare is `INT 98h` and a site number
(`NS_CMP_SITES` in `gamepatch.py`, the same order as DSCLOG's
`ns_cmp_sites`); the helper makes a new spell compare as a wizard's
spell does, and hands back the flags. The name routine (500:61h,
`NS_NAME` at 5E560h) gives their names; their descriptions (RESOURCE.GFF's
SPIN 197-199, which the game hasn't) come from the helper after the read; the
icons (21196-21198) are in the launcher's copy of RESOURCE.GFF.

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
  `monsters.py`), an unarmed attack (`[BP-2]` -1) is +1 to hit (`[BP-8]`,
  taken off the THAC0) and at least a +1 weapon. The natural-attack routine
  applies Body Weaponry (2d4) and Animal Affinity (at least 1d10) to the first
  attack after `NS_CLAW`, changing the dice but not the bonus: with the claw,
  2d4+1 and 1d10+1, as the description says.
- Fogbolt puts effect 27 (unused) on a creature that fails its save. In the
  routine adding up an attack's to-hit adjustments from effects (7C3E9h,
  `NS_HIT` at 7C430h, beside the target's Blur), it takes 3 off for a fogged
  attacker and gives 2 against a fogged target.

**Fogbolt's bolt.** A record's `+10h` names what flies from caster to target
(FFh: nothing): a place in a table of 16 flights just before the records (3
bytes each: the object flying, then a byte, Magic Missile's 8), which the cast reads at
7530Ch (`imul ax,ax,3`, the object made at 0B8:55Ah and sent off by 600:2Ah);
nothing else reads the table. Magic Missile's is place 4, object 8109, whose
OJFF names BMP 2227 (36 frames, a direction each). The launcher's SEGOBJEX.GFF
copy adds object 8118 (8109's record naming BMP 2584) and BMP 2584, 2227's
frames with its white, cyan and blue (46, 220, 161) in the greys 214, 211 and
209 (`icons.bolt_chunks`; the 208-217 ramp is the same in every region's
palette). No record names place 15, so `NS_SETUP` points it at object 8118 (at
Magic Missile's speed byte) and gives Fogbolt's record `+10h` 15, only when
the game has opened the copy (`objects_on`, part of `NS_STATE`); else, and
with the rule off, place 15 is the game's (8116) and Fogbolt flies nothing, as
Charm Person.

**Its sounds.** A record names three sounds (RESOURCE.GFF's BVOC chunks, the
game's Creative Voice files), all played by 90:A6Fh: `+0Fh` with the glow on
the caster (only when `+0Dh`, the glow's object, isn't -1), `+13h` while
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

A click on an effect's icon on the Effects screen
([In the README](README.md#spells-on-the-effects-screen)) ends it in the game;
with the switch on, a spell's effect is left on: two jumps in the screen's
click handler (DSUN.EXE 7F226h and 7F236h, `effects_click_low` and
`effects_click_high` in `dscompanion/gamepatch.py`) go to its way out instead
of to the routine ending an effect. A psionic power's (spells 8Ah-ABh) still
ends, as stopping it there is how a power is dropped.

### Helms

([In the README](README.md#helms).)

How: the helper sets the helm types' AC as the game's AC routine reads it
(`INT F8h`, the Ring +1's place). (An earlier rule gave boots a move in a
fight; it is gone, and the boots' names it changed go back to the game's.)

### The game's own party

([In the README](README.md#the-games-own-party).)

How: the four are objects in `SEGOBJEX.GFF` (32000 to 32003, and 300, 307, 308
and 313 for their figures), a creature record and a sheet each, already Okay
and with no items; the game gives them their gear and spells as it starts. So
the Ledger (`dscompanion/defaultparty.py`) changes them in memory while the
game is new (its first hour, in the arena, as with Thieves' Tools), each
change once, knowing each by name, race and classes together: their weapon
kinds in the sheet's spare bytes, Gerakis's club item made a bone gythka in
its place, Cilla's plain armour given back to the free item list (her chest
armour is alone in its list, which is left empty, as a new list is), and her
byte for spell 0 set in the known-spells table, and with kits Cermak's kit
byte (`+43h`) the Arcanist for his preserver class (place 0; his gladiator
class, place 1, none). Seen in play: Cilla's USE screen lists ARMOR among her
1st-level spells and her inventory has no chest armour (AC 5); Gerakis holds
the gythka and the long sword.

### New items

([In the README](README.md#new-items).)

How: the new items (the slave pens' and the world's, the bone scale set,
Kreenfang) are in the game's data (`dscompanion/dataitems.py`, `worldgear.py`,
`npcitems.py`, `arms.py`): in the
Ledger's copy of `SEGOBJEX.GFF`, each person's or chest's object (its RDFF: the
object's record, then its items, each a child or the next of the one before,
with its type and name as attributes) has the new items after its own, so the
game makes them where it makes the object. Kreenfang is the arena's dead
body's (object 1204) own gythka made +1 and renamed, its name attribute with
it. One Castle Guard, one Undermountain miner and one Magera (Drakejaw's) have
an object of their own (2560, 2561, 2562: copies of their kind's, their record
renumbered), their entity in the Ledger's copies of `RGN1C.GFF`, `RGN1E.GFF`
and `RGN08.GFF` pointing to it. So does the slave pens' weapon rack (2563: the
Lower Castle's rack is the same object 1647; a thing's record has its number
first, a person's at +6), with Thornwall in place of its first bone polearm,
in Kalzith's copy of `RGN29.GFF` (one copy of the pens: with Kalzith off, the
rack's alone). The Elven Leader's Gythka +2 is his own
Gythka +1 (in his pack, object 124, and the item object 2534 his script gives)
made +2. (People of a kind share an
object, so every Tari, Renegade and Wild Mul carries theirs; the caravan's
buried chest is an object the dig's script makes, and has the Boots of
Elvenkind in it.) The Elven Leader's script (46, in
the scripts' copy: `elvenleader.py`) gives the Cloak of Elvenkind (object 2546,
an item object of its own) after the Gythka, as the game's scripts give items
(command 39h, a new item of the object; 25h on the ground when it can't be
carried); Father Garyn's (174: `garyn.py`) gives the Tome of Understanding the
same way, the first time the pith is delivered (flag 625). The tome
(`dscompanion/tome.py`) is a scroll of the game's kind: object 1446, among the
game's scrolls' numbers (1400-1499: its object record the first scroll's, as
only a scroll's kind of object has its box's icon clicked; the picture that
number had, the icon of two objects, moved to 2552), its spell byte one past
176. Clicked, the icon has the game's routine (DSUN.EXE 8B690h) teach a scroll
of those numbers its spell, or a psionic power from 138 to 171; from 172 to 195
it would show "CANNOT LEARN FROM THIS ITEM" and keep the scroll (from 196 on,
the icon can't be clicked). There the helper (`INT B9h`) raises the reader's
WIS, in the sheet and the creature record, writes its message in the game's
buffer, and goes on as for a power taught: the game uses the tome up and shows
it. The short sword, the cloak whose plus counts, the bone helm and the rest
(25: Galefang's, a metal dagger whose class list has the air cleric's
bit, which none of the game's daggers have; then the bone and obsidian great
axes, the metal one's of those materials, and a bone dagger, the only dagger a
water cleric may use) are item types the helper adds
after the game's 115 each time the game reads its table in (`TYPES_EXTRA`; its
weapon types by item type, `kind_of_type`, cover them too); the Ledger's item names (`dscompanion/names.py`) are entries it adds
after the game's 322 (the game puts the item type's material before the name
when it shows one); and the icons are objects in the Ledger's copy of
`SEGOBJEX.GFF` (`dscompanion/icons.py`), which the helper has the game open
instead of its own (its `INT 21h` hook). Where the game adds up AC and saving
throws, the helper counts the rings and the cloak (`INT F8h` and the save
probes). Shadowseeker's sight is the game's own way with a magic item's spell:
readied, it puts Detect Invisibility on its wielder. In the original game the
rings are plain rings without a name, and the sword, cloak and helm types it
doesn't have: don't load a save that has them without the dice log.

Alagorn's new menu lines are in the Ledger's copy of his scripts
(`dscompanion/alagorn.py`); he knows an item by its picture.
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
  are one too many, so items past the locals use the Ledger's flags from 784
  on (set afresh as the part starts, as the locals are). The new stories'
  "none left" test is one subroutine they all call.

The icons in the guide's item tables (`docs/items/*.png`) are drawn from the
game's data by `python -m dscompanion.docicons GAME_FOLDER`, from the Ledger's
copy of `SEGOBJEX.GFF` in `dos/` (start the game from the Ledger once first)
and the game's palette: each picture twice its size, the rest transparent.
`docicons.ICONS` names each image's object; a new item needs its line there,
and `tests/test_docicons.py` checks that every icon the guide shows is there.

### Bracers of defense

([In the README](README.md#bracers-of-defense).)

How: where the game's AC routine asks the helper about each worn item
(`INT F8h`) and where it starts a saving throw's modifiers (`INT F9h`), the
helper looks at what else the character wears.

### Robes

([In the README](README.md#robes); `robes.py`.)

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
for +2 where there are any. The Ledger: `restrict.is_robe`, `robes.save`,
`robes.slots`, `GameData.protection` (not armour). The icons are drawn
(`icons.robe_icon`, objects 2580 and 2582); Kel's object (107) carries the
Veiled Robe in the data (`worldgear.MAGIC`), and Kalzith's Ashen Robe is put
on him with his cloak and scrolls (`kalzith.stock`).

### Kalzith

([In the README](README.md#kalzith).)

How: he is the game's own kind of person, in the Ledger's copies of three of
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
time the party is in the pens, the Ledger puts his six scrolls among his
things (from the game's free list, as for [the arena's ring](README.md#new-items)),
once a game. If he is killed, the Ledger marks it (flag 772) and the others
speak of him as dead (see
[Dinos and the Trustee](README.md#what-dinos-and-the-trustee-say-about-them)); after
the party's escape he is gone from the pens with everyone else.

With his scrolls the Ledger gives him his gear, worn (`kalzith.gear`, flag
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
whatever of his gear he still had, in his body where he fell, and the Ledger
logs the scroll ("Kalzith leaves: Scroll of Blur"). The game puts everything a
dead person carried in the body; the Ledger takes the other scrolls out of it
(flag 777, once).

He is a slave of the pens like the game's own (his record is Dinos's): attacked,
he turns on the party as they do, and only the guards near him join the fight.

### Semyon

([In the README](README.md#semyon).)

How: in the Ledger's copy of `GPLDATA.GFF`, the command that takes him off the
map when he walks out after the fight (script 5 at 2400, run only from there)
first sets the Ledger's flag 770; the game's other exits don't reach it. The
Ledger sets flag 771 if it ever sees him dead (his record's hit points or
status). The pens' script ends with, "if flag 770 is set, 771 isn't, and he
isn't in his pen yet, make him there", the command the arena's script uses
when he is untied (25h, his object 280), and the command that runs his
conversation (script 219) when he's talked to, with its entry in the game's
table of entry points. Flags 764 and 765 (his own: placed, met) keep the rest,
so a save keeps him.

How: the arena's script 3 moves Scar and his henchman to the pens (5Eh to region
41) when the party reaches the west exit after Scar's plan is agreed. In the
Ledger's copy, the henchman's move (at 1828) becomes a jump past the script's
end, where that move is made, then Semyon's, to a square beside them (74, 68),
if he is recruited (the game's flag 6), not seen dead (771), in the arena and
not against the party (his field 74, the side, not 2); then the Ledger's flag
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

([In the README](README.md#what-dinos-and-the-trustee-say-about-them).)

How: in the Ledger's copy of `GPLDATA.GFF`, their scripts (139 and 146) keep
every byte where it was, since the game's jumps go to fixed places. Two
commands become jumps to code after the script's end: the one starting the
menu's part goes to the same command followed by the new questions' flags
(766-769, 773, 774), and the menu goes to a copy of it (the game's own bytes) with the
new questions after its last about someone. Each then jumps back to where the
game's script carries on.

That makes the Trustee's script 10,898 bytes, and the game reads every script
into one buffer of 10,000 bytes (a script that calls into another reads it in
over its own). One of 9,800 bytes ran; one of 10,000 ended with "BAD GPL
EXIT" (the game's own largest is 9,792). So the Ledger's copy of the game
makes the buffer 11,776 bytes where it is allocated (`push dword 10000` at
6A692h becomes 2E00h), about 1.7 KB more of the game's memory.

### The cooked vulture

([In the README](README.md#the-cooked-vulture).)

How: in the Ledger's copy of `GPLDATA.GFF`, Dinos's talk (script 139) has the
question in its first menu (a copy of the game's with the question added, as for
the questions about Kalzith and Semyon, see
[Dinos and the Trustee](README.md#what-dinos-and-the-trustee-say-about-them)), shown
while the game's own test says someone in the party carries the cooked vulture
(33h, as the campfire's script asks about the plucked one; the game's object
A4Ch), the test being the question's own condition in the menu. Chosen, the script takes it (5Ch, as the campfire takes the plucked one)
and sets the Ledger's flag 780, then gives the XP through the game's own routine
for quests (the amount in its variable, then script 74 at 135: the window, the
words and the quest's sound), as Dinos's own script does when he heals Gilal
(350). The Ledger then refills the party, once (flag 781), only while the party
is talking with him (never from a game being loaded).

### What the party wears

([In the README](README.md#what-the-party-wears).)

How: the party's figures are objects 300 to 313 in `SEGOBJEX.GFF` (300 and
the figure picked at character creation). The launcher's copy of the file
(see [Item icons](README.md#new-items)) gives each its own walking and fighting
pictures, the game's with room round them for gear (walking, 6 pixels at the
sides and 2 above, as much as anything worn reaches; in a fight, 10), and free
space after each in the file. The game draws a figure's whole picture at every
step, so each picture is exactly as long as it needs to be. While the game
runs, when someone's worn items change, the Ledger draws their pictures anew
(`dscompanion/spritegear.py`, from where `dscompanion/spriteparts.py` finds the
head, hair, hands and the rest in each frame), writes them into its copy of the
file with their new lengths in the file's index (the game reads a picture's
place and length there each time it loads one), takes the old ones out of the
game's table of loaded pictures (the game frees them itself, as any it no
longer uses), and empties the figure's slot on the map: the game loads the new
pictures and draws them at once, in a few thousandths of a second
(`dscompanion/sprites.py`). It then has the helper draw the view again (see
[Shadows](README.md#shadows)), so the shadows show the new outfit too. A picture the
game loads later (in a fight, in another area) comes dressed, from the file.
The copy also has a spare pair of pictures for each party place. Each thing on
the map names the picture it is drawn with and the slot in the game's picture
table it is drawn from; for a second member of the same figure the Ledger names
their spare there and empties the slot, and the game loads the picture and
fills it.

### Elves and half-elves

([In the README](README.md#elves-and-half-elves).)

How: elves (objects 304 and 305) get pointed ears (`dscompanion/figures.py`):
2 pixels wide and 3 rows tall, a salmon inside, a rose rim and tip. Their
place is read from each frame's parts (beside the head, two rows above the
eyes from the front; at the eyes from behind; behind the face from the side),
or set by hand for the poses whose parts can't be read (`EAR_PLAN`: lunges,
the bow, hit, dead). They are drawn after the gear, only on pixels the gear
left as they were, so a shield or a weapon in front hides them.

Half-elves (objects 306 and 307) name the human pictures, as 300 and 301 do.
The Ledger's copy of the file gives them figures of their own instead
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

If the palette or the pictures they are made from are missing, or making them
fails, a half-elf is the human figure recoloured (`halfelf.py`), as before. A
spare is drawn as the figure it stands for.

Cilla, in the game's own party, is an elf with the half-elf woman's figure (7)
in her record (object 32003's RDFF, its word +22h, the creature's +18h), and
her object (OJFF 32003) names the human woman's picture. In the Ledger's copy
of SEGOBJEX she has the elf woman's figure (5) and picture (the game's, which
the Ledger then swaps for its own as for anyone). In a game begun without the
copy, the Ledger writes the figure into the running game's creature table, and
the game draws her as an elf from its next area or load
(`defaultparty.figure_chunks`, `defaultparty.elf_figure`).

### Shadows

([In the README](README.md#shadows).)

How: the launcher's copy of `DSUN.EXE` (see [How the dice log
works](#how-the-dice-log-works)) calls DSCLOG when the game draws the floor of
the view or of a rectangle of it. DSCLOG then lays each casting figure's
current picture, flattened and stretched, onto the floor just drawn, darkening
each pixel to the closest clearly darker colour of the area's palette (a table
it makes from the palette when the Ledger asks: after each area change, once
its fade-in is over, and now and then; the colours the game cycles, for water
and fire, are never picked as darker ones). The rectangles the game draws again when a figure
moves are widened by the length of a shadow, so none is left behind. The
Ledger keeps DSCLOG's list of who casts one (`dscompanion/shadows.py`) and has
DSCLOG draw the view again when it changes (from the game's main loop, as
centring the view does: marking the figures changed instead, as the game's own
code does to draw one again, can set one in a fight walking again).

The list can be up to half a second old, so as it draws DSCLOG also checks
the creature's status (`SHADOW_GONE`: the things table, then the creature's
`+1Ch`) and gives a dying (4) or dead (5) one no shadow. Otherwise it would
load the dying creature's new pictures through the game's picture loader from
inside the floor drawing, the most likely cause of a crash seen in the arena
as a creature died (not reproduced).

### Dust

([In the README](README.md#dust).)

How: DSCLOG notes, each time round the game's main loop, how far each figure
that casts a shadow has walked, and raises a puff a little behind and to one
side of its feet every 6 pixels (the feet in turn). The puffs are drawn on the
floor after the shadows, lightening it through a table of each colour's lighter
one, which the Ledger makes from the area's palette (`dscompanion/dust.py`):
only warm, middling colours (sand, dirt) have one, so stone, water and the
figures take none. Each puff is dithered thinner toward its edge and as it
fades, by a pattern fixed to the map, so a puff looks the same however much of
it the game draws again. While anyone walks, the rectangle the game draws again
round what moved is made to take the puffs in; once everyone stands, DSCLOG has
the view drawn again a few times a second until the last puff is gone.

### Choosing an enemy: Tab, Enter and the rings

([In the README](README.md#choosing-an-enemy-tab-enter-and-the-rings).)

How: DSCLOG hooks the keyboard (`INT 16h`) and takes Tab, Shift+Tab and, with an
enemy chosen, Enter from what the game reads, counting them for the Ledger
(`dscompanion/targeting.py`), which keeps the enemies marked and the chosen one
(`dscompanion/rings.py`). The rings are drawn in the floor pass, after the
shadows, through a table of each colour's redder one made from the palette. For
Enter, DSCLOG puts the pointer at the enemy's feet and gives the game a left
click there, from the main loop, while the routine that finds what is under the
pointer (`DSUN.EXE` 25B52h, `INT DBh`) answers with the chosen enemy for half a
second, whatever stands in front of it.

### Scrolling the map

([In the README](README.md#scrolling-the-map).)

How: the game hears of the mouse's buttons from the mouse driver, through a
handler it gives it (`INT 33h`, function 0Ch). DSCLOG hooks `INT 33h` and puts
its own handler in between, which keeps the middle button (the wheel pressed)
from the game, and, with the right button dragging too, keeps the right button
from it while it is held: a click reaches the game when it is let go (pressed
and released where it was pressed), a drag never does. The game's main loop
asks where the pointer is (to scroll at the screen's edge); there DSCLOG has
the game centre its view where the drag puts it, with the game's own routine
(the one clicking on the overview map uses, which draws the view again), and
keeps the pointer it reports off the edges meanwhile. The Ledger only switches
it (`dscompanion/scrolling.py`). (Turning the wheel isn't used: DOSBox 0.74,
GOG's, never passes it on to the game.)

### More saves

([In the README](README.md#more-saves).)

How: the save names the game searches the folder for and writes a save to
(`SAVE??.SAV`, `SAVE%.2d.SAV`) are two strings in its memory; DSCLOG changes
their fourth letter for the page. The window's event routine leaves keys and
buttons it has no use for to a jump to its end; the patched game has DSCLOG
take them there (`INT D8h`, `INT D7h`), and for a new page run the window's
own routines that search the folder, draw the rows and draw the window. Enter
is taken out of the window's key table, so it comes to DSCLOG too, which goes
on to LOAD (or SAVE) as the table did, but not on a row with no save. The
buttons are the game's kind, in the Ledger's copy of `RESOURCE.GFF`: placed
in the window under EXIT, with pictures made from EXIT's, its letters taken
away and the page's put in with the game's text font
(`dscompanion/savepages.py`; the buttons' own carved letters have no P, G or
digits).

### More characters

([In the README](README.md#more-characters).)

How: the game's file routines take any number; only its loops over the
characters stop at 20, its roster list has room for 20 and its "Maximum
characters" check counts to 19. The patched game has 30 and 29 there
(`dscompanion/gamepatch.py`, a byte each).

A New character counts as Okay wherever the game tests for Okay: a jump each
(`NEW_AS_OKAY` in `dscompanion/gamepatch.py`), and `game.py` does the same.

### Game speed

([In the README](README.md#game-speed).)

The Ledger's drawing is as cheap as it can be without looking any different:
a shadow is darkened a plane of the video memory at a time (the graphics
card's registers set four times for a figure, not four times for each of its
rows), and a dust puff's pixels are worked out a row at a time, only within
its outline and the part of the view being drawn again. The pictures the
Ledger draws the party's gear on are each exactly as long as their outfit,
with only the room gear needs round the figure while walking (6 pixels at the
sides, 2 above; 10 in a fight), since the game draws a walking figure's whole
picture at every step.

## Kits

([In the README](README.md#kits).)

A kit is chosen for a class: by a character of one class when it is made, and
by a human for each class it changes to (up to three). There are three for
each class, or none (the class as it is). Each gives something and costs
something, as AD&D's kits do. The **Kits** rule change on the Options tab
(`game.RULE_KITS`, bit 0 of the helper's second rules word, `RULES_HI` at the
header's +270) switches them all off.

### The kits

What each kit gives and costs is in [the README's table](README.md#kits).
Two kits have tables of their own.

The Seeker's and the Justifier's tables are AD&D's (*The Complete Ranger's
Handbook*), up to 10th level; their spells are cast at the table's casting
level, not the ranger's (the game's own rangers' spell levels count the
ranger level 7 less, but their spells' durations and damage take the whole
of it):

| Ranger level | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|
| Seeker: casting level | 1 | 2 | 3 | 4 | 5 |
| Seeker: 1st, 2nd, 3rd level slots | 1 | 2 | 2, 1 | 2, 2 | 2, 2, 1 |
| Justifier: casting level, slots | | | | | 1; one 1st-level |

The Shinobi's spells, all the game's (thief level 6 on, the Seeker's slots):

| Spell level | Spells |
|---|---|
| 1st | Gaze Reflection, Charm Person, Shield, Color Spray, Wall of Fog |
| 2nd | Invisibility, Mirror Image, Blur, Detect Invisibility, Fog Cloud |
| 3rd | Blink, Haste, Protection from Normal Missiles, Hold Person |

No kit is the kit page's first row, and what a new character has.

### Room in the helper

DSCLOG keeps its code and data in one 64 KB segment, all reached through CS.
The dice log's ring buffer (`NENT` 84 entries of `ESIZE` 192 bytes) follows
the resident part in memory, in a segment of its own: the install code sets
`ring_seg` (the header's +268, read by `dicelog.py`) to the paragraphs after
the resident image, and its last step (`KEEP`, in the resident part, as the
ring lies over the install code) clears the ring and stays resident with it.
The text buffer (`TSIZE`) is 4 KB; the Ledger reads its size from the
header and drains it every few tens of milliseconds.

The helper has to load into upper memory, or the game loses 62 KB of
conventional memory (570 KB free rather than 632 KB). With GOG's settings
there is one upper memory block of 63 KB; the helper asks for its resident
part and the ring (`LOAD_EXTRA`), and `mem` in DOSBox shows 632 KB free and a
few KB of upper memory left. A change that adds much code should check that
again: the ring is 84 entries, not 128 (96 until the new spells' code, when
the game no longer started for lack of memory; 88 until STORE and RECALL), and the text buffer 4 KB,
not 8, to make that room.

### The kit's byte

Sheet `+43h`: zero in every sheet of the saves and saved characters at hand
(176), and nothing in DSUN.EXE reads or writes it (no `es:[bx+43h]` access of
any kind), as with the weapon specs' `+14h` to `+17h`, which saves and the
roster keep. `+45h` is the same, if a second byte is needed (the Arcanist's CON
change used it, once, before that became its d3). 0: no kit; 1 to 3
the class's kits.

### Choosing one

The creation panel's lower window shows the psionic disciplines or the
clerical spheres, each with a button that swaps them (VIEW SPHERES is there,
out of use, for a class with no sphere), and for a warrior with weapon
specialization the WEAPON SPEC pages. The **KIT** page is at the end of that
chain, opened with a **KITS** button where the last page's button was:

| The class (one only) | Where KITS is |
|---|---|
| preserver, psionicist, thief; a fighter or gladiator without weapon specialization | the disciplines' window (3022, a copy of 3012) |
| cleric, druid; a ranger without weapon specialization | the spheres' window (3023, a copy of 3013) |
| fighter, gladiator, ranger with weapon specialization | the fourth weapon page (3025, a copy of 3017) |

`WP_IDS` (`kitpages.panel_windows`) picks the windows for the classes being
made, for the probes that open them (`PROBE_WP_DISC_WIN`,
`PROBE_WP_SPHERE_WIN`, and `PROBE_WP_CLASS` when the classes change). The
kit page itself is a window for each class (3026 to 3033, by the creation
screen's class numbers), its rows NO KIT and the class's three kits
(buttons `888h`, and `870h` + 3 × (class − 1) + kit − 1), its button VIEW
PSIONICS (the weapon pages' `851h`) back to the disciplines. Like the weapon
pages, it is kept at `DS:EA6h` with the spheres' own routine answering its
buttons, so `PROBE_WP_SPHERE_CLICK` gets its clicks and `PROBE_WP_SHOWN`
lets the game close it when another class is clicked. `KIT_ROW` puts the
kit in the creation sheet's `+43h`, and `KIT_MARKS` marks the rows. As the
game's spheres do, the rows not chosen are out of use (greyed) while one is;
the one chosen, clicked, is taken back (`KIT_OPEN`, `FFh`: none chosen, no
kit), and the rows are all in use again. The game keeps the whole sheet when DONE is pressed: `+43h`
is in the roster's CHAR record (the sheet at its `+4Eh`). It also keeps the
creation sheet from one character to the next, so the kit is put back to none
whenever the disciplines' window is opened other than on the way back to it
(`KIT_KEEP`, set by VIEW PSIONICS): for a new character, or another class.

The rows' letters are carved from the game's own labels, as the weapon
pages' (`kitpages.py`, with a J and a hyphen drawn). The panel's frame comes
in to about 95 pixels past the rows' left at the second kit's row, so a row
is held to 88 (`ROW_WIDTH`, its mark's room in), clear of it: ARENA CHAMPION,
SWASHBUCKLER, ELEMENTALIST, GROVE WARDEN, BATTLE MAGE, MIND BENDER and MIND
WARRIOR are shortened (CHAMPION, SWASHBUCK, ELEMENTAL, WARDEN, BATTLMAGE,
M-BENDER, M-WARRIOR), the last two as the game's P-KINESIS.

The Effects screen's lower panel (`PROBE_EF_ROWS`) has the kit's line first,
`KIT: RAVAGER`, before the weapon specs; the Characters tab has `Kit: Ravager`
(`GameData.kit`).

The lower panel has room for five lines (`EF_LINES`); three kits and a
gladiator's four weapon specs make eight. `EF_DRAW` goes over the lines twice
(`EF_LINES_OF`, each through `EF_LINE`): first counting them (`EF_COUNT`), then
putting those of the page on the panel (`EF_PUT`). With more than five, a page
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

### Where each effect goes

A kit has one number (the creation class × 4 + the kit:
`kitpages.KIT_IDS`). A human may have a kit for each of its classes (up to
three), so every rule asks whether the sheet has a given kit awake: `KIT_IS`
(kit in AL; `KIT_HAS` asleep too), or inline, `call kit_is_b` / `db KIT_X` for a
sheet at ES:BX, `cr_is` for a creature (AX), `cb_is` for a combatant
(`[BP+6]`); each leaves the kit's class's place in `KIT_WHERE` for `KIT_LEVEL`
and `KIT_CLASS_OF_SHEET`. Rules that several kits touch (AC, THAC0, slots,
saves, to hit and damage, cures) take each kit's part in turn. Each effect has
its twin in `kits.py`, which the Ledger and the dice log use (once for each kit
in `kitpages.kit_ids`), and emulated tests hold the helper to it:

| Effect | Kits | Where |
|---|---|---|
| damage with a weapon | Ravager, Brute (melee: `KIT_MELEE`, by the item type), Arena Champion (melee, a shield in a hand: `KIT_CHAMPION`, by `PROT_SCAN` of the attacker's thing, `[BP+18h]`) | `PROBE_SPEC_DAMAGE` (`KIT_ATTACK_DAMAGE`), and the DAM lines (`PROBE_DAM_LINE`, `PROBE_VIEW_DAM`: `KIT_MELEE` only) |
| to hit | Ravager, Brute, Arena Champion | `PROBE_ATTACKS` (`KIT_TO_HIT`: `KIT_CHAMPION`, and `KIT_MELEE` in melee) |
| AC | Ravager (`RAVAGER_AC` by level against the sheet's base AC, `+27h`), Wanderer, Sentinel and Arena Champion (a shield in a hand: `PROT_SCAN`), Grove Warden | `PROBE_AC` (`INT 62h`, the end of the AC routine: `KIT_AC`) |
| movement | Stalker | `PROBE_MOVE` (`KIT_MOVE`) |
| spell slots | Arcanist (+1 wizard), Battle Mage (−1 wizard), Crusader (−1 priest), Seeker and Justifier (their priest tables, `SEEKER_SLOTS`, by ranger level, in place of the game's), Elementalist (a level behind) | `PROBE_SLOTS` (`INT B6h`, new: the end of the game's slot routine, `mov ax,[bp-2]` at DSUN.EXE 5E255h) and `PROBE_SLOT_LEVEL` (`INT B5h`, new: where it takes a class's level, `mov al,es:[bx+24h]` at 5E1F6h); `GameData.max_spell_slots` with `kits.slots` and `kits.slot_level` |
| a power's PSP | Mind Bender, Kineticist (by discipline: powers 0-5 psychokinesis, 6-19 psychometabolism, 20-33 telepathy, the defence modes among them; never below 1) | the powers' table (8 bytes a power, at the load segment + 3FB9h: `+1` the cost to use, `+2` to keep up, 63h for none; `+5` FEh for a defence mode). `PROBE_PSP_USE` (`INT B4h`, new: where the routine using a power has its cost in DI, its table's or worked out for Enhanced Strength and Domination, DSUN.EXE 5CBE7h), `PROBE_PSP_TABLE` (`INT B3h`, new: the table's cost read in the check whether a power can be used, 5CAA3h, and for the half a failed power costs, 5CCA2h), `PROBE_PSP_DEFENCE` (`INT B2h`, new: a defence mode's cost taken off, 5D820h); `kits.psp_cost`. Monsters' powers (5A773h) are left alone |
| a cure's healing | Healer (+1 a die of Cure Light, Serious, Critical Wounds: spells 71, 112, 127), Lifebinder (a die more: a d8, Blood Flow's, 108, a d6, rolled from the game's rand() seed by `GAME_DIE`) | `PROBE_CURE` (`INT B1h`, new: "nop / push cs" at DSUN.EXE 79619h in the handler for spells with rules of their own, where the healing, pushed with the target, goes to the routine that heals; the caster its `[BP+8]`, the spell `[BP+0Eh]`; the probe pushes CS itself). The Cell Adjustment's jump into 79618h is clear of it |
| casting level | Seeker (the ranger level less 5), Justifier (less 9), Shinobi (for its wizard spells, the thief level less 5) | the game works it out in two places, both with the combatant and the spell as arguments. The caster level routine, 81B16h, counts a ranger's level 7 less: `PROBE_RANGER_CAST` (`INT AFh`, new: that "sub dx,7", 81B6Ah) makes it the kits' 5 and 9, and `PROBE_CAST_LEVEL` (`INT ACh`, new: its end, `mov ax,[bp-2]`, 81C06h) gives a Shinobi its level for a wizard spell. That routine sets the spell levels a caster may cast, half the caster level rounded up (81664h, which asks for spell 0: the USE screen's lists and slots), and weighs a spell against Dispel Magic. The level a spell's duration and damage take is another routine's, 5E25Ch (the best level of the caster's classes that cast it, a ranger's whole; the cast passes it down to the duration, 76CB3h, and the damage dice, 76DA2h): `PROBE_SPELL_LEVEL` (`INT A8h`, new: its end, `mov ax,di`, 5E3D1h) gives the Shinobi its own; `PROBE_RANGER_LEVEL` (`INT A6h`, new: `mov al,es:[bx+24h]`, 5E3B8h, where it takes each class's level) takes the Seeker's 5 and the Justifier's 9 off its ranger level (and a plain ranger's 7, with the [rangers' casting level](#rangers-casting-level) rule). `kits.ranger_cast_drop`, `kits.cast_level`, `kits.spell_class_level`, and `GameData.effect_caster_level` |
| wizard spells for a thief | Shinobi | slots: `PROBE_SLOTS` gives a Shinobi's wizard slots the Seeker's table by its thief level (`kits.slots`). Its spells known are the party's table of them (at the load segment + 3800h, from 168h: 8Ah bytes a member, a byte a spell, not 0 if known), and the USE screen lists and casts them as any preserver's. Learning: a level up as a thief from 6th goes on as a preserver's would (`PROBE_LV_PICK`'s `LV_SHINOBI`) to the routine that offers a preserver its spell (620:5Ch, 85560h), which takes the preserver level and goes on only for one, and then only if the game's list (500:2Ah) has a spell to learn: `PROBE_PICK_ANY` (`INT A7h`, new: `mov [bp-2],ax / or ax,ax`, 85580h) opens CHOOSE A SPELL (85771h) for a Shinobi with one of its spells unknown up to the level it casts. There `PROBE_PICK_LEVEL` (`INT ABh`, new: `inc al`, 85861h, the preserver level the highest spell level on offer is half of) gives it its casting level, and `PROBE_PICK_LIST` (`INT AAh`, new: `mov di,ax`, 8563Fh, after the game fills the list, at the segment of the `mov ax,348h` before it, `+7`, a word a spell; the character at its `+25Bh`; the highest spell level `DS:[4AECh]`) puts its own unknown spells in the list (`kits.pick_list`). A scroll: the game's check whether the character on show may learn its spell (8B6D3h, `or ax,ax` before the jump to CANNOT LEARN FROM THIS ITEM) says no for a Shinobi (`PROBE_SCROLL_LEARN`, `INT A9h`, new). Armour: the game has no armour rule for a single class's spells (the multiclass preserver's is the class restrictions'), so it casts in the light armour it may wear |
| spells learnt at a level up | Scholar (one more) | `PROBE_LV_PICK`'s `LV_SCHOLAR`: at a preserver's level up, the routine offering its spell (620:5Ch, its far call read from the code after the probe) called once before the game's own |
| a power's PSP to keep it up | Mind Bender, Kineticist (as the cost to use it; 63h, none, left alone) | `PROBE_PSP_KEEP` (`INT B0h`, new: the table's `+2` read where the round's cost is taken, 5CE49h, the combatant in SI) and `PROBE_PSP_KEEP_DX` (`INT AEh`, new: the check whether a power can be kept up, 5CB02h, the combatant in DX). The monsters' cost lookups (5D4DAh, 5D4EFh) are left alone |
| the off hand | Healer (no weapon), Battle Mage (nothing) | `PROBE_CAN_USE`'s `KIT_FORBIDS` with `KF_OFF_HAND`: the can-use routine's only caller is the equip routine (6EF52h), whose `[BP+8]` is the slot (the item's slot + 4: 7 the right hand, 14 the left, the off hand; 18 on the backpack), read through the can-use routine's saved BP |
| casting though hit | Battle Mage | a hit's damage marks its creature hit this round (`mov byte es:[si+0AFh],1`, 58733h, in the routine taking damage off; cleared at a round's start, 57621h), and a marked character can't choose a spell on the USE screen (892F3h, 55898h) and has a queued one dropped (8991Bh): `PROBE_HIT_ROUND` (`INT ADh`, new) doesn't mark a Battle Mage |
| two spells in a turn | Arcanist (preserver spells, in a fight) | a spell aimed on the map ends the caster's turn in two ways: the routine casting it marks the caster as a hit does (845F0h; so no spell is offered again), and the routine finishing any use of what the USE screen armed (720F4h: it takes the slot or the item's charge; `DS:[54FBh]` the kind, 0 a wizard spell from a slot, `[54FCh]` the party member) asks the fight's routine that sets a combatant's actions (59256h) for none, as do the routines that cast, from their own code segments. A spell on a party member from the USE screen does neither (the game's own: the turn goes on). `PROBE_CAST_MARK` (`INT 96h`, new) doesn't mark an Arcanist for its first preserver spell of the turn; `PROBE_CAST_DONE` (`INT 94h`, new: the finishing routine's `cmp word es:[19h],0`, 722AFh) counts its preserver spells (`ARC_CASTS`) and sets `ARC_HOLD` for the first; `PROBE_END_TURN` (`INT 93h`, new: `mov si,[bp+8]`, 5925Dh) then returns at once when ending that member's turn is asked from another code segment (the fight's own routines, a turn ended from the combat menu among them, ask from its own), till the map's main loop runs again (`PROBE_SCROLL`) or a turn starts; `PROBE_ROUND_MARK` (`INT 95h`, new: the turn's start clearing the mark, 57621h) clears the count. Checked in the game: two Magic Missiles in a turn, the second marking it and ending the turn; ended from the combat menu after one |
| THAC0 | Swashbuckler, Crusader, Battle Mage, Mind Warrior (a warrior's: 21 less the level, where better), Scholar (1 worse) | `PROBE_THAC0` (`INT B7h`, new: the end of the game's THAC0 routine, `mov ax,14h / sub ax,si` at DSUN.EXE 876BBh, which every write of a creature's THAC0, `+1Fh`, uses: on making a character, 66CE0h, and at a level up, 86D7Eh and 87A91h) |
| initiative | Sentinel | `PROBE_INIT` (`INT B8h`, new: the round's 20 added at DSUN.EXE 5750Eh) |
| saves | Myrmidon (charms), Sentinel (spells, 0-137), Wanderer (fire and cold: the spell record's `+1Ah`, 2 or 4, as the game's Resist Fire and Resist Cold read it) | `PROBE_RING_SAVE` (the modifier routine's start: `KIT_SAVE`) |
| thief skills | Assassin (pick pockets, open locks), Swashbuckler (all) | `PROBE_BELT` (the thief skill routine's end) |
| hiding, moving silently | Stalker, Assassin | the stealth rule's rolls (`stealth.py`, `GameData.ranger_skill_parts`) |
| the two-weapon penalty | Twin-blade (in light armour: `HEAVY_WORN`); Justifier (in any armour) | `PROBE_TWO`; `RG_TWO` |
| gear allowed | Ravager, Twin-blade, Brute, Stalker, Grove Warden, Lifebinder, Shinobi, Seeker (its sphere's weapons, as a cleric's: `SPHERE_ALLOWS` with `CU_*` set from the item type, its sphere the ranger class less 13; the bow kept) | `PROBE_CAN_USE` and `KINDS_ALLOWED` (`KIT_FORBIDS`: `restrict.kit_forbids`), whatever the class restrictions |
| skill with a weapon | Justifier (expertise, the bow's and its chosen weapon type's, becomes specialization) | `SPEC_OF_SHEET`'s end: `SPEC_EXPERT` made `SPEC_SPECIAL` for a Justifier; `specialize.skill` |
| weapon specs | Myrmidon (two, the second to grand mastery), Brute (no missile spec), Battle Mage (one, of `KIT_BM_KINDS`: expertise) | `WP_TWO`, `SPEC_OF_SHEET` (a Battle Mage's chosen weapon type `SPEC_EXPERT`), `KIT_FORBIDS`, `KINDS_ALLOWED` (a Battle Mage its own weapon types, whatever its class), `LV_DUE` (a Battle Mage one); the creation panel counts a Battle Mage as a warrior (`WP_CLASSES`, so `WP_IDS` gives the disciplines' window with WEAPON SPEC; `kitpages.panel_windows`) |
| attacks a round | Battle Mage (its chosen weapon type: expertise, 3/2, 2 from 7th preserver level); Crusader and Mind Warrior (a warrior's extra attacks in melee, 3/2 from 7th level of the kit's class (2 from 13th, past the level cap), weapon specialization on or off) | `EXPERT_HALVES` where `PROBE_ATTACKS`, `PROBE_DAM_LINE` and `PROBE_VIEW_DAM` leave a non-warrior's (2 halves or fewer) alone; `specialize.expert_attacks`. `WAR_KIT_HALVES` in the same three probes, after the rest (`WAR_KIT_OF` in `PROBE_ATTACKS`, not for a missile: `[BP+16h]` above 1, or in View Character a type's `+0` bit 2); `kits.warrior_attacks`, which `GameData.weapon_hits` gives the party view. Checked in the game: the DAM lines 1.5× for a 7th-level Crusader and Mind Warrior, 2× at 13th, 1× at 6th and for a Mind Bender; in a fight a 7th-level Crusader with a club in each hand attacked 1+1 and 2+2 in turn before the off hand's cap (see [Two weapons](#two-weapons-adds-penalties)) |
| gear the kit allows | Battle Mage (its chosen weapon type's weapons, with weapon specialization; light armour) | `KIT_ALLOWS` in `PROBE_CAN_USE`: an item the game's class mask refuses is let through (AX 1), and the class restrictions pass it; `KIT_FORBIDS` still holds (nothing in a Battle Mage's off hand). `kits.allows`, `restrict.kit_allows`. The game has no armour rule for a single class's spells, so it casts in that armour |
| hit die | Battle Mage (d6), Mind Warrior (d8), Arcanist (d3) | a level's die: `PROBE_HIT_DIE` (`INT A5h`, new: `mov al,es:[bx+0]`, 87308h, the die read from the class's hit point group in the routine rolling a level's hit points, 87250h, which both a level up and the creation screen call; `[BP-4]` the sheet). The creation screen's range (the least and most hit points it allows, `DS:[4998h]` and `[4996h]`, worked out with the rolls by 655D6h): `PROBE_CR_DIE` (`INT A3h`, new: `mov al,es:[bx+14Ah]`, 65677h, the die from its table by creation class). `kits.hit_die` |
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

The Elementalist's second sphere is the sheet's `+45h` (`SPHERE2`: 0 none, else the sphere + 1),
free since the Arcanist's CON change went. The game gives each class a mask (load + 3800h, `+118h`,
a dword a class: 1 wizard, 2 priest, then a bit a class, 4 the air cleric to 20h the water cleric)
and each spell one (load + 3FB9h, `+19Dh`, 7 bytes a spell); a class casts the spells whose masks
meet its:

| Effect | Kits | Where |
|---|---|---|
| priest spells known | Elementalist (its second sphere's too) | the loops that mark each priest spell (45h-89h) known or not for a party member by the class's bit, on making a character (66F89h) and when a human changes class (86E1Eh, in the DUAL routine at 86C80h; a level up marks none, as a priest knows its spheres' spells of every level from the start): `PROBE_EL_KNOW` (`INT 9Eh`, new: `test dword es:[bx+19Dh],eax`, 66FC9h and 86E56h; its flags back to the JZ with `RETF 2`) adds the second sphere's cleric bit. And the routine giving a priest its spheres' spells (5E401h, no caller found): `PROBE_EL_GRANT` (`INT A1h`, new: `xor si,si`, 5E489h) adds it to its mask |
| a kit asleep after dual-classing | every kit | the routine that changes a human's class (86C80h, DUAL on a portrait's menu: 70EF1h opens its window, 86B3Fh, for a human of 2nd level or more) moves the classes down and puts the new one first. The kit byte (`+43h`) has two bits for each class (0 none, 1-3), the first class's lowest and each class taken after it the next two, so a kit stays with its class however the classes move: `KIT_PLACE` gives the oldest class's place (0 for one class; 1 or 2 for a human; none for another race's multiclass), `KIT_AT` the kit of the class at a place, `KIT_AWAKE` holds a kit asleep until the level at `+24h` passes its class's (as the game counts earlier classes; the class it has now is always awake). `KIT_IS` finds a kit only while awake and `KIT_HAS` either way. The byte's 0FFh (`KIT_OPEN`, on the creation panel) is no kit. The kit's own levels come from `KIT_LEVEL` (Ravager and Grove Warden AC, the warrior THAC0, the Seeker's and Justifier's slots, the Shinobi's casting and spell picks, the Battle Mage's 7th-level expertise) and its class from `KIT_CLASS_OF_SHEET` (a Seeker's sphere, an Elementalist's cleric); `PROBE_SLOT_LEVEL` puts an Elementalist's slots behind for its own class's place only (`KIT_AT` there). `PROBE_HIT_DIE` gives a kit's die only for one class (a human who changed class rolls for its new one); `PROBE_MAX_PSP` takes a Mind Warrior's tenth with `KIT_HAS`, as a sleeping psionicist class still gives its PSP. `SPEC_OF_SHEET` treats a dual-classed Battle Mage's weapon spec as the kit's (none asleep, expertise awake), not a new warrior class's. The Effects screen has a `KIT:` line for each kit, the oldest class's first, ` (ASLEEP)` after one asleep (`KIT_AT`, `KIT_OF_SHEET` with `KIT_SHORT`'s shorter names, `KIT_LINE_ASLEEP`, `KIT_AWAKE`); see the next section for its pages. `kitpages.kit_place`, `kit_at`, `kit_awake`, `kits_of`, `kit_ids`, `kit_level`, `kit_class_of` are the Ledger's |
| classes barred to a dual-classing human | Seeker, Justifier (cleric, druid); Shinobi (preserver); Swashbuckler, Crusader, Battle Mage, Mind Warrior (fighter, gladiator, ranger); Arena Champion, Sentinel (druid, preserver: no shield); Brute (psionicist, air cleric: no two-handed melee weapon) | the DUAL window (866C7h) asks of each class (SI, 1-17) whether member [BP+6] may change to it (86E94h: AX 1 if so; human, prime requisites) and greys the rows answered no: `PROBE_DUAL_BAN` (`INT 9Dh`, new: the `or ax,ax` after the call, 866FFh; its flags back to the JZ with `RETF 2`) answers no for a class one of its kits bars (each `KIT_AT`, asleep too; `KIT_BANS`), from `DUAL_BANS` (a kit's number, then a dword of class bits; `kits.DUAL_BANS`). The slot kits' tables (`PROBE_SLOTS`) replace the whole count for their kind of magic, so they would take a new cleric's, druid's or preserver's slots' place |
| a new preserver's spells, on changing class | every human (not a kit's) | the routine that changes a human's class, for a preserver (86DB5h), takes away its wizard spells and marks Grease (8) and Magic Missile (7) known: `PROBE_DUAL_SPELLS` (`INT 9Ch`, new: those two `push / push si / call 500:43h / add sp,4`, 22 bytes from 86DE4h) calls CHOOSE A SPELL (620:5Ch, 85560h: the level up's) twice in their place, through its stub (`PICK_STUB`: DS less 4Ch, as `WP_STUB`), with the spell levels on offer up to 1st (`PICK_CAP`, which `PROBE_PICK_LEVEL` heeds). The dual routine is in CHOOSE A SPELL's own overlay (85560h to 87250h), so the call can't unload the code it returns to. The same call from another overlay needs its way back where the overlay manager can patch it: see the next row |
| a new preserver's spells, at creation | every preserver | the creation screen's DONE (overlay 65480h) marks spells known by preserver level (`[BP-2]`, 66F2Dh on: 7 and 8 at 1st; 9 and 0Bh too at 2nd; 0Fh and 16h too at 3rd). `PROBE_CR_SPELLS` (`INT 98h`, new: `mov ax,[bp-2]`, 3 bytes) has a character still New (status 0 at the creature's `+1Ch`; the game's own party, made Okay by START GAME, keeps the game's) pick as many on CHOOSE A SPELL (`PICK_SPELLS`: 2, 4, or 4 and two of 2nd level; a Scholar's one more a level, `KIT_MADE`) and goes on past them (66F83h, `CR_SPELLS_PAST`). CHOOSE A SPELL returns nothing; EXIT leaves it with no spell learnt, which `PICK_SPELLS` tells by counting the member's known preserver spells before and after (`PICK_KNOWN`, the low four bits of each byte from `KNOWN_OFF`, as 500:43h sets them; the party's four only, creation's and DUAL's among them). Then the picks end and `PICK_FILL` marks the game's own spells known for those left, in its order, less any known (`fill_first`, `fill_second`). DONE's routine (6649Ch) has saved the character to its slot and opened its files (550:57h) before the grants, so going back to the creation screen from here isn't done CHOOSE A SPELL is another overlay, whose loading may put the creation code out: without care the game is lost on the way back. The INT's way back is pushed as a stack frame (`push cs / push ip / push bp / mov bp,sp`) that the overlay manager walks and patches to reload the code first, as `PROBE_LV_PICK` and `PROBE_DUAL_KIT` do, and read back after |
| sound numbers on the sheet | every character | the game reads a word at sheet `+42h` (78FDAh, `mov dx,[es:bx+42h]`: a sound to play, 4 if 0) and at `+44h` (81DE3h, `mov ax,[es:bx+44h]`: played if not 0), and the kit byte (`+43h`) and second sphere (`+45h`) are their high bytes, 0 in every one of the game's sheets: `PROBE_SOUND_42` and `PROBE_SOUND_44` (`INT 9Bh`, `INT 9Ah`, new, 4 bytes each) read the low byte alone (`movzx`) |
| a kit for a dual-classing human's new class | every kit | in the routine that changes a human's class (86C80h), once the classes have moved down and the new one (`[BP+8]`) is first: `PROBE_DUAL_KIT` (`INT 99h`, new: `cmp word [bp+8],0Ch`, 4 bytes at 86D90h; the compare done after, its flags back with `RETF 2`) shows the game's three-choice menu, the one the DUAL window asks a cleric's sphere on (4D0:25h, overlay 54D90h: its stub 41B4h, `DK_STUB` from DS; arguments x, y, a far title, 1, three far rows; it returns the row clicked, 1-3, else 0, and leaves an empty row out). Title `KIT: NONE`, rows the new class's kits (`KIT_NAME_PTR` into `KIT_NAMES`); a kit `DK_BANNED` bars an empty row: its `DUAL_BANS` hold one of the other classes, or it and one of their kits are a `KIT_PAIRS` pair (`kits.dual_kit_banned`, `KIT_PAIRS`). The kit goes in the kit byte's bits for place 0 (`KIT_PLACE` × 2 up). An Elementalist's second sphere (`SPHERE2`) on the menu again (`DK_SECOND`: the three spheres not the cleric's), before the routine marks the spheres' spells known (`PROBE_EL_KNOW` takes it in). Then, with weapon specialization, `LV_CHECK` (the level up's weapon kinds, through the psionicists' pop-up, 620:57h: `PICK_STUB`'s entry 57h). The menu is another overlay, so the INT's way back is put in a stack frame the overlay manager walks and patches (`push cs / push ip / push bp / mov bp,sp`, as `PROBE_LV_PICK`), and read back from it after. `PROBE_DUAL_SPELLS` gives three picks, not two, when the kit taken for the new preserver class is the Scholar |
| starting gear fitted to the kit | Ravager, Brute, Shinobi, Seeker (a forbidden hand item), Arena Champion (a shield), Battle Mage (its weapon spec's weapon) | the game gives a new character its class's gear when DONE is clicked (the README's table, seen in play). The dice log's `weaponchoice.kit_gear` (after `finish_new`, with the rule for kits; New characters only), for a hand's item `restrict.kit_forbids` forbids (the off hand as such): a weapon in the right hand becomes a plain one (`plain_weapon`) of the first kind it may use and the kit allows, the character's chosen kinds first, then `REPLACE_ORDER` (the long sword's neighbours: short sword, axe, mace, great axe, gythka, polearm), then any; a two-handed one sends the off hand's item to the backpack (`_shield_off`); a shield is taken away (`ring.unlink`: out of its list, its record back on the game's free list), anything else goes to a backpack cell (if the shield can't be unlinked, it too). An Arena Champion with no shield has its off-hand item made the game's starting shield (`SHIELD`: type 4, name 05h, picture FC04h, price 10). A Battle Mage with weapon specialization and no weapon of its chosen kind has its right hand's item (the quarterstaff) made one (`start_weapon`). Each change leaves nothing to change again |
| caster level, a spell's level | Elementalist | the caster level routine (81B16h: the spell levels it casts, Dispel Magic) and the effect level routine (5E25Ch: durations and damage) count a class whose mask meets the spell's: `PROBE_EL_CAST` (`INT A0h`, new: `mov edx,es:[si+19Dh]`, 81B42h) and `PROBE_EL_LEVEL` (`INT 9Fh`, new: `mov ebx,es:[bx+19Dh]`, 5E375h) give a spell of its second sphere its own cleric's bit too; `kits.spell_spheres`, `GameData.effect_caster_level` |
| weapons | Elementalist (its second sphere's as well as its own) | `CLASS_FORBIDS`'s cleric spheres (`EL_SECOND`), and `KINDS_ALLOWED` through it; `restrict.elementalist_sphere` |
| choosing it | Elementalist | the creation panel's spheres (the game's, drawn from a mask by 63FEEh, `DS:4982h` its own sphere's row): `WP_CLICK` sends a click on a sphere's row to `EL_CLICK`, which takes or takes back the second (the game's mask left alone) and has `EL_MARKS` draw both marked and every row in use; `PROBE_WP_CLASS` (after every click) draws them so again over the game's own drawing (`EL_REMARK`) |

Every kit also needs its Python side: the Characters tab and the in-game
THAC0 and saves (`game.py`), the dice log's lines, and tests that hold the
helper's code (emulated) to the Python.

### How they're checked

Each kit's helper code is held to its Python by emulated tests
(`tests/test_dsclog.py` runs the helper's routines in a CPU emulator), and each was played in the game: the creation screen's KIT page and
hit dice, the level ups (Shinobi and Scholar spells, Seeker slots), the KIT
menu after DUAL with its bans, and the Effects screen's pages.
