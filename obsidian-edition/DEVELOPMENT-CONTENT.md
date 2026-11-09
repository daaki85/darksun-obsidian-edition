# Development: spells, items, people, graphics and the game's bugs

*Part of the [development notes](DEVELOPMENT.md). How the game's script and spell bugs are mended, and how the new spells, items and people and the graphics are done. Each heading names the section of the [features page](FEATURES.md) or the [README](README.md) it explains.*

## Contents

- [The game's script bugs](#the-games-script-bugs)
- [Mirror Image](#mirror-image)
- [The game's spells](#the-games-spells)
- [Worn items, the gladiator's armour and Psionic Blast](#worn-items-the-gladiators-armour-and-psionic-blast)
- [New spells (wizard and 6th-level priest)](#new-spells-wizard-and-6th-level-priest)
- [New items](#new-items)
- [Bracers of defense](#bracers-of-defense)
- [Robes](#robes)
- [Girdles and the amulet](#girdles-and-the-amulet)
- [Kalzith](#kalzith)
- [Semyon](#semyon)
- [What Dinos and the Trustee say about them](#what-dinos-and-the-trustee-say-about-them)
- [The game's people's gear](#the-games-peoples-gear)
- [Pehtucl's chest](#pehtucls-chest)
- [The champions' bout](#the-champions-bout)
- [The cooked vulture](#the-cooked-vulture)
- [Defilers' scrolls](#defilers-scrolls)
- [What the party wears](#what-the-party-wears)
- [Elves and half-elves](#elves-and-half-elves)
- [Shadows](#shadows)
- [Dust](#dust)
- [See-through figures](#see-through-figures)
- [Sounds for hiding and picking pockets](#sounds-for-hiding-and-picking-pockets)

## The game's script bugs

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

Checks that read a character's own field (race 20, sex 21, the flags word 17)
straight from the active member's object (8025h, or the actor's, 8026h), whose
record, the combat record, holds none of them, so they read 0. The game's own
scripts read them through field 71 (the combat record's pointer to the
character's: `8025 02 47 15`, some thirty times), so the repair adds the `.71`:
script 31 at 3Bh and 254h (the halfling's greeting and insult: yuan-ti's), 42 at
121Eh and 154Ch (sex: "wo"man, "her" purse), 80 at 8D7h (a thri-kreen hears the
bell) and 203 at 101Bh (a thri-kreen gets "your help"), these four found by a
sweep of every script for fields read from a record that lacks them. The
ranger's tracking (script 210, region 8's bodies, yuan-ti's): 5FDh tests the
ranger bit (200h) of the flags word read directly; 60Ch, 622h and 638h test
`class & 200h` for each class where a ranger's class code is 13 to 16 (now
`> 12 and < 17`); 6CCh succeeded on `score < RAND(20)` (now `RAND(20) < score`).
The score is WIS, plus 1 above ranger levels 2, 5 and 8, plus 2 for a flag, plus
the level halved; success gives the party 75 XP a point of it. The slave pens'
sewer grate (script 137, yuan-ti's): A65h ends the search for a weapon in hand
on `lflag[3] == 1` where it was just set to 0 (now `== 0`), so "hack the lock
off" never comes up; 9E0h's hack says his or her as the pick does; A14h's
successful hack sets flag 505 and prints "The grate opens." as the pick's does.
Its attack trigger, B49h, registered by MAS 41 on the grate, object 1234,
"breaks the lock" when the target's field 43 is below 220; no record the grate
can be has that field (GPLX: the character record's +8, most hit points, and the
item type's +6), so 0, and always. The repair at B5Ch (yuan-ti's) rolls
`RAND(30) < STR` instead, the rip's roll (AA6h), so "fails to damage the lock"
can come. The Rebel Mindhome's leader (script 204, Undermountain, yuan-ti's)
gave the spiders' 5000 XP (gnum 16 and GPL 74, at 5C9h) at every talk once they
were dead; the award sets flag 695 (5D6h), which nothing read: the repair runs it
only while that flag is 0. (Their "Have you killed the spiders yet?" while the
spiders live is meant: told the spiders are possessed, or offered peace, the
Mindhome still wants them gone.) Region 9's messenger (yuan-ti's, from OpenDS's
triage): MAS 9 at 63h registers his sight trigger (1Bh: entry 1 of GPL 133 on
-1297, range 15, while flag 339 is 0) only if flag 245, the elves gone, is set
as the region loads; GPL 58 sets it at 1Ah, 99h and CCh during a stay, so a party
that never left and came back never saw him. Each of those sets now registers the
trigger too; GPL 133 starts by clearing -1297's sight triggers (1Dh), so a second
one can't run it twice. The Draj serf (GPL 60 at CD8h): region 38's way to region
10 takes the following serf along within 14; left further behind he stayed,
without his orders, and talking to him again ran the deal and gave a second
obelisk gem (-1352). Now within 127.

Pehtucl's ambush at the slave pens' fountain (GPL 145, the Loader's own find): having
led the party to 60,94 (AFCh), he makes his guards at his square (E7Dh: command 25h,
4 of object 90, the Arena Guard; E8Bh: 1 of 293, the Guard), then gives hunt orders
(08h at E99h, E9Dh, EA1h), a no-orders handler (6Fh: GPL 74 at 100) and a sight trigger
(1Bh: GPL 74 at 89, range 5) to -90, -293 and -37: a negative number is a kind, every
creature of it in the region, so the pens' eight Arena Guards and two Guards from the
region file (those still alive) came from across the map too. 25h makes a number by
calling one routine (4251:0043h) for each in turn, with the same values; the game's
other scripts give a creature just made its orders as local big number 40 (`89 28`:
GPL 10 at 10Ch, 52 at F0Bh, 57 at A9Dh), so the repair (E7Dh to EDBh, a detour) makes
each of the five alone and gives that one the hunt, the handler and the trigger; Pehtucl
keeps his by his kind (-37: the pens' region file holds one, him). His one other
kind-wide hunt, at 169h (the party back after escaping, flag 503), is left as it is:
there the whole pens are meant to be roused; his refusals (898h, D43h) make guards
and leave the rest to the alarm. The fight's alarm (GPL 137, called at the ambush and
by every guard's attack trigger in the pens): FB5h lets a yell go unheard ("the roar of
the fountain masks his voice", flag 511 once) when the one yelling (local 44, located)
is in the fountain's room, x 54-80 and y over 73; the party, a step behind Pehtucl,
stands in the passage west of the room's wall (x 53-55, y 92-95), so a guard drawn
there raised the alarm. The test is now `room or (x 42-80 and y over 90)`, that
passage up to the wall at x 40-41 (the room west of the fountain's, with the sewer
grate, is shut off from it at y 89-90 and stays out); its IF, to the alarm at 1081h,
goes along. Tests: `test_scriptfixes`. Not yet seen in play (the save
`fountain-user` loads with the ambush about to fire).
The same sweep checked every RAND comparison and every bit test of a class or
level: only the tracking's were wrong. A second went through every check on a
class or its bits, race, sex, item, weapon, thief skill or ability: script 44 at
2F9h ("why don't you go bother someone your own size / else") asked
`race != 2 or race != 6`, always true, where it meant `and` (the operator byte,
D6h to D5h); script 142 at 14B0h and 14C3h (the haystack: the scrying and
mind-reading answers' flags, lflags 17 and 18) tested the class bits word
`== 80h` and `== 100h`, which a multi-class preserver or psionicist fails; now
`(word & bit) > 0`, the game's own form (script 67 at 1563h). Script 56 at
125h, Dagolar's slime book's "with magical training", masked the class bits
with 417 (1A1h: psionicist, preserver, fighter and the air cleric, not the other
clerics or druids), most likely a slip for 415 (19Fh: every cleric, druid,
preserver and psionicist), which it now is. The book (object 2021) is in region
27h with four Jars of Slime and a glyph circle (1366): a jar used on the circle
is used up and puts a Tyrian Slime in it (56 at 96h, unless one is already within
20); the book, read (56 at C0h), turns a Tyrian Slime within 20 into a Dagolar
Slime that hunts the party, when the reader has the training, or drains the
reader into it (10 damage) when not, and with no slime near, "Nothing happens."
Left as they are: two object numbers compared that no object
file holds (script 10 at 352h, -261; script 195 at 35h, -144: the same number
195 also asks for by name, so likely made in play). The other 67 object numbers
are real objects (an item's +0 is its object's number negated: the grate's
Bloodwrath, -1576, always hacks the lock); the thief skill checks (DO_ACTION 3)
and ability checks (59h) each test the skill or ability their text names, and
the weapon search for the grate looks in the right hand (item +11h slot 3).
(Hototo's "Where is Dagger, bug / woman?", script 132 at 198h, tests race
alone, but only after a sex test at B0h: a man is taken for Dagger.)

A failed hack at the grate said the weapon "breaks against the grate" and left
it; the repair at A31h (its words' print) runs a detour that tests the weapon
(2Ch) by the game's rule for a weapon breaking in a fight (`Game.item_breaks`):
a plus or a spell (item fields 15 and 0), its type's 80h or a material above 3
(field 4 leads to the item's type, whose field 8 is the material byte, signed),
and it " rings off the grate, unharmed."; else the game's words and TAKE (5Ch) one of that weapon from its
holder (local big number 37) to 9999, as the game's scripts take items away.
TAKE goes by the item's number, which items of a kind share, so it may take a
spare of the same weapon from the pack rather than the one in hand.

The thief skill routine's effect tests (DSUN.EXE 80425h, `-1000` to the
situation): Slowed (effect 47, the list's byte 5 bit 80h) rules out picking
pockets alone, as yuan-ti has it; the Loader's own table (`game.THIEF_BLOCKED`,
for its screens) had it ruling out every other skill. Item 2005 on the legs
would make moving silently certain and hearing noise impossible (80530h), but
the routine passes its item and slot lists swapped, so it never applies; and no
item 2005 exists in the game's data, so nothing is lost.

A repair longer than the bytes it replaces runs from after the script's end:
an exit first (a script that ran off its end still stops), then the new bytes
and a jump back; the old bytes become a jump there, padded with exits. The jump
is 64h, as the Loader's other script changes jump (yuan-ti uses 12h, which the
game's scripts never do). A lengthened test takes its IF along, so the branch
follows it as in the game's. Addresses in the new bytes written from their own
start (`relocate`: the grate's his-or-her) are moved by where they land.

**Kurzak and Legcrusher** (`dsloader/kurzak.py`, always): Kurzak's call to the
arena (script 136 at 130h, "Legcrusher! Get gladiators!") and his talk's cases 2
and 3 as the party comes (script 141 at 6B4h and 70Bh: "I thought I was going to
have to send out Legcrusher", "I had to send Legcrusher after you"), case 4 (766h,
"I'm glad you listened to Legcrusher": he found them, then died) and his answer to
"Who is the half-giant?" (F29h), and Dinos's warning (script 139 at 218h, "before he
sends out Legcrusher") ask first
whether Legcrusher (object 326) is on the map: `80h` from Kurzak (29) to him
under 999, as the game's own scripts ask whether someone has died or gone
(Dinos of Gilal, script 139). There, the game's lines; gone, Kurzak's own. The
first line of each becomes a jump (64h, the rest 67h filler never reached) to
code after the script's end that says one or the other and jumps back past the
game's lines, as `pensasks.py` does; the scripts do the rest as the game has
them. Dinos's script is `pensasks.py`'s copy by then, whose own jumps leave bytes that don't
read on: the places come from the game's script, and a line is changed only where the copy
still has the game's bytes. Tests: `test_kurzak`. Not yet seen in play: it needs Legcrusher killed at
the fountain and the party late for a fight.

## Mirror Image

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

## The game's spells

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
  The manual's limit, undead of no more hit dice than the caster's level, is
  `hold_undead_level` (with "Spells and psionics as the manual describes them"): DSCLOG's
  `HOLD_HD_SITE` over the undead's `test word [bp+0Eh],100h` (7A345h), which
  makes that test and its jump itself, and for spell 31 sends an undead whose
  level (its sheet's, as 5E85Fh has it: a human's +24h, else its classes'
  highest; a classless one's +24h) is above the frame's [BP+14h], the cast's
  level, to 7A1F0h too.
- **The save modifiers** (79D3Ch: [BP+6] the target, [BP+14h] the spell,
  [BP+16h] the caster's level, [BP-6] the target's level, SI the modifier):
  the target's level comes from 508h:2Ah (5E85Fh), 0 for a creature with no
  class (+21h..23h all 0), though its hit dice are at its sheet's +24h. With
  "Spells and psionics as the manual describes them", `classless_save_level` puts DSCLOG's
  `HD_SAVE_SITE` over its `mov [bp-6],ax` (79D8Ch): such a creature's 0 made
  its hit dice (Dismissal, Cloudkill, Scare and Color Spray read it), and
  `color_spray_level` DSCLOG's `SPRAY_SITE` over Dismissal's
  `cmp word [bp+14h],3Ch / jnz` (79F83h): Color Spray (spell 4) on a target of
  the caster's level or lower -100 (a natural 20 still saves), then
  Dismissal's test made in the handler (on to 79F89h, or past to 79F95h).
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
- **Scare's save** (spell 21, in the save modifiers' routine, 80F5:119Ch): a target of 6th
  level or more always saves (+100); below, the usual save only for a priest (7C01Dh) whose race
  (the sheet's +18h) is 3 and is 4: "cmp 3 / jne fail" (79FEAh), then "cmp 4 / je save"
  (7A011h), so everyone below 6th failed (-100). `scare_elves` makes the first "je" to the save
  (7A01Dh): an elf or half-elf priest saves as usual, as AD&D's elves, half-elves and priests
  resist fear (found by yuan-ti). None of this ran before `scare_save`: Scare's record's save byte
  (+1Fh, 4222Fh) was A0h, bit 0 ("a save allowed") clear, and the saving throw (79A71h) answers
  "not saved" at its first test (79A89h) without it, before the modifiers. `scare_save` sets it
  (A1h, as Charm and Hold Person's). Seen in DOSBox before it: Scare on a 7th-level fighter, no
  save rolled (playtest/logs/2026-11-08-scare-no-save.md).
- **The creation screen's minimums** (67399h, far, `[bp+6]` the class count and `[bp+8]` the
  ability; its answer goes to `DS:4994h`): the game's own looked each creation class (the sheet's
  +21h, 1-8) up in the table at `338:180h` (a word, the prime requisite, then a byte) and gave 17
  for the prime requisite, the byte (9 to 14) for any other score. `least_scores` replaces its 104
  bytes with `dos/least_scores.asm`: a nibble a score for each class
  (`dos/least_scores_table.inc`, the manual's minimums, 0 none), the highest of the classes', 3 if
  none. It keeps the two `mov dx,338h` at +1Eh and +42h where they were: the overlay manager fixes
  up their segment. The table at `338:180h` is left as it was, as the dual-class check (86E94h)
  reads its prime requisite. `game.CREATION_MINIMUMS` is the same table for the dice log;
  tests/test_least_scores.py runs the routine and checks both.
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

## Worn items, the gladiator's armour and Psionic Blast

([In the features page](FEATURES.md#the-games-bugs-fixed); found by OpenDS, checked in
DSUN.EXE with yuan-ti's notes; Psionic Blast from yuan-ti's issue #129.) One helper interrupt
(`INT 81h`, `PROBE_WORN`), told where it was called from by its return address:

- **Ability items.** The ability routine (7B758h, `80F5:2BB8`) goes through every item the
  creature has (the list `A0:1A2D` makes) and applies the ability byte (+0Fh, FAh-FFh) of each,
  with no look at its slot, so a ring or gauntlets in the backpack counted. Its read of that byte
  (`mov al,es:[bx+0Fh]`, 7B8ABh) is the interrupt: the byte only for an item in a worn slot
  (+11h below 14), else 0, which the routine's switch passes over.
- **The gladiator.** The AC routine (58DD3h, `612E:2113`) takes a fifth of the gladiator level
  off after its items, for the sheet's gladiator flag (+12h 40h) alone. Its test (`test word
  es:[bx+12h],40h`, 58F86h) is the interrupt: ZF clear only when the creature also wears armour
  (`ARMOUR_WORN`: an armour piece on the arms, legs, head or chest, not a shield, bracers or a
  robe), so the game's `jbe` passes the bonus by otherwise. `THORNS_AC` and the Loader's
  `GameData.counted_ac` (`armour_worn`) count it the same way.
- **Psionic Blast.** The effect routine's case 169 (796CBh, `80F5:0B2B`), for a target that
  failed its save, takes its hit points down to a fifth of its most (the loss in `[BP-18h]`, the
  damage routine 79A01h dealing it), then `or byte [si],1` (79707h). That OR is the interrupt
  (with a NOP): it does it, and for target DI 0-3 (the party's combatants) adds the loss to the
  header's `BLAST_HP` (+1814, a word each). `psiblast.BlastWatch`, in the dice log's pass, gives
  each loss back once the fight flag has been down `FIGHT_OVER` (2 s), up to the member's most
  and only to one still Okay (one Out Cold or dead was put there by something real), says so
  ("Cilla shakes off Psionic Blast's imagined wounds as the fight ends: +23 HP, now 30/38"), and
  clears the field; a game loaded (the clock gone back) clears it with nothing given.
  **Knocked out, not killed:** the damage routine kills a creature when the
  damage reaches its hit points + 10 (status 5; 8 for 10000 and up, Disintegrate's), else knocks
  it out when the damage reaches its hit points (status 3, 0 HP). Its death test, `cmp ax,dx`
  (5860Bh, 612E:194Bh, before a `jg` to the Out Cold case), is the interrupt too (`blast_knockout`): for a
  party member with hit points still in `BLAST_HP` and damage under 10000, the flags of
  "greater", so the blow knocks it out. At the fight's end one Out Cold gets the hit points back
  too and is woken (status 1, as the game wakes a creature at 7C1F9h); one Dying or dead gets
  none. Seen in DOSBox: Gerakis at -9 HP with 40 kept, a 1-point Psychic Crush (death by the
  game's rule) left him at 0, and the fight's end gave him the 40.
- **The champion's body** ([the champions' bout](#the-champions-bout)): where the game makes a
  Dead Body for a creature dying with things on it, the object number is asked of the interrupt.

The five places are told apart by the return address (`WORN_AC_RET` 22C8h, `BLAST_RET` 0B69h,
`KO_RET` 194Dh, `BODY_RET` 2754h, else the ability routine's), so the one vector serves them
all.

## New spells (wizard and 6th-level priest)

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
212, the room's last whole record (it ends at 3E5E0h, the room at 3E5E2h),
which Negative Plane Protection's save record (`NPP_SAVE`) fills; another new
spell needs room made first (that record moved elsewhere, say). The stack had been written over records 196-198's room all along; with it
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
description is Wake of the Ravager's (`find_resources`; its answer kept for the
run, as the Options tab asks each time it is built, and the drives looked at one at
a time from C:, as `launch.drives` does for Shattered Lands' own folder:
`find_game_dir` tries the folder given and the one saved first, and searches the
drives once a run, an empty floppy drive or a sleeping network drive being slow
to answer). Its icons are a kind of
picture Shattered Lands hasn't: the frame header as usual, then `0FFh "PLNR"`,
the bits a pixel (4 or 5), a colour map of that many bits' worth of palette
numbers, and codes of those bits, the highest first, where 0 0 is colour 0 and 0
k the last pixel k + 2 more times (worked out on the 101 spells both games have;
38 match Shattered Lands' pixel for pixel). Its palette isn't Shattered Lands',
so each colour becomes the nearest Shattered Lands colour no region changes.
Checked in the game: the Heal icon in a known spell's place on the USE screen.
Restore Youth's icon, a fountain, is drawn in `wotrart.DRAWN` (a letter a
colour, `DRAWN_COLOURS`, each made the nearest stable colour), with or without
Wake of the Ravager.

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
(+12h, types with +0Fh 80h, a shield too) in the creature's worn item list,
+8 (the routine doesn't look at the slot byte, and counts nothing in the held
list, +0Ah, or the backpack's, +0Ch: [DEVELOPMENT.md](DEVELOPMENT.md)'s
"The party's three item lists"), a
fifth of a gladiator's level
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
  as Strength's adds to STR (`INT EFh`). With the spells as the manual has them
  the dice are by class (`STRENGTH_SITE` at 79483h, Strength's too), and a
  smaller Cat's Grace beside a bigger one adds nothing (`GR_SHADOWED`): see
  [DEVELOPMENT-RULES.md](DEVELOPMENT-RULES.md#spells-and-psionics-as-the-manual-group-3).
  Heal's (`PROBE_CURE`) also takes Feeblemind off there.
- Erdlu Claw puts effect 6 (unused) on its target. In the routine giving a
  natural attack's dice (7B66Ch, `NS_CLAW` at 7B70Ah; DX the set of natural
  attacks, 0-2, as the sheet holds them from +2Bh: `game.SHEET_NATURAL_*`), the
  first set's (fists; a thri-kreen's claws, not its bite, set 2) becomes 1d6+1
  where that's better on average than its own. In the melee attack
  routine (58019h, `NS_FIST` at 58226h), where a hit gets its weapon's magic
  (`[BP-0Ch]`, which becomes damage kinds 1000h/2000h/8000h, PLUS1-PLUS3 in
  `monsters.py`), an unarmed attack (`[BP-2]` −1) of the first set (`[BP-22h]`
  0, the set the routine is on) is +1 to hit (`[BP-8]`, taken off the THAC0)
  and at least a +1 weapon. The same hook makes the hit's
  damage kinds (`[BP-14h]`, set at 581DFh to crushing, 8, for any natural
  attack) slashing (10h) for Erdlu Claw's talons, and for a thri-kreen of the
  party's (combatant below 4, its sheet's race 8), claws and bite, whatever the spell: the game
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
(`NS_LANDING`). Restore Youth has Cure Disease's 78 with its cast glow
(`RESTORE_CAST_SOUND`), not the 81 of Cure Critical Wounds, its template, which
Heal and Water of Life keep; nearly every healing spell lands with 98.

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

## New items

([In the features page](FEATURES.md#new-items).)

How: the new items (the slave pens' and the world's, the bone scale set,
Kreenfang) are in the game's data (`dsloader/dataitems.py`, `worldgear.py`,
`npcitems.py`, `arms.py`): in the Loader's copy of `SEGOBJEX.GFF`, each person's
or chest's object (its RDFF: the object's record, then its items, each a child
or the next of the one before, with its type and name as attributes) has the new
items after its own, so the game makes them where it makes the object. Kreenfang
(`arms.magic`: a gythka made +1 and renamed, its name attribute with it) is the
champions' Tohr-kreen's ([the champions' bout](#the-champions-bout)); without
the champions' objects it is the arena's dead body's (object 1204) own gythka,
as up to 2.13.4. One Castle Guard, one Undermountain miner and one Magera
(Drakejaw's) have an object of their own (2560, 2561, 2562: copies of their
kind's, their record renumbered), their entity in the Loader's copies of
`RGN1C.GFF`, `RGN1E.GFF` and `RGN08.GFF` pointing to it; so does one skeleton of
the warrens (Gutterward's: 2585, entity 85 in the copy of `RGN28.GFF`; its
kind's object, 2266, is the skeletons' of five regions), and one thri-kreen of
the Gemfields (Skycutter's: 2598, entity 22 in the copy of `RGN06.GFF`; its
kind's object, 215, is the whole pack's). So does the slave pens' weapon rack
(2563: the Lower Castle's rack is the same object 1647; a thing's record has its
number first, a person's at +6), with its own two bone polearms (Thornwall
comes onto it later: [Semyon](#semyon)), in Kalzith's copy of `RGN29.GFF` (one copy of the pens: with Kalzith
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
(17, 33, 84, 94), makes the Great Axe +3's type (2) metal (+8, from the 40h of no material, a
ring's: the icon's head is the metal axe's grey and teal, the weight 70 the metal great axe's), as its own daggers have it, so an air cleric of one class may
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

## Bracers of defense

([In the features page](FEATURES.md#bracers-of-defense).)

How: where the game's AC routine asks the helper about each worn item
(`INT F8h`) and where it starts a saving throw's modifiers (`INT F9h`), the
helper looks at what else the character wears.

## Robes

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

## Girdles and the amulet

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

## Kalzith

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
  in the game's table of script entry points (which saves go by: the Loader's three
  entries, his, Semyon's and Pehtucl's chest's, are always there in that order,
  whatever the switches, so a save's numbers never point at another script;
  `kalzith.ENTRY_SCRIPTS`; the Loader's script numbers are in
  `kalzith.LOADER_SCRIPTS`, checked by `test_scriptnumbers`), the command
  in the pens' script that runs it when he's talked to, and his portrait
  (portrait 101, a number the game leaves free): his own face, painted for the
  mod (`kalzithface.py`: 32 rows of 32 indexes of the portraits' palette, PAL 1,
  only colours the game's own portraits use and none it animates).

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

## Semyon

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

The weapon shipment: his answer to "Seen anything useful?"
sets flag 756 (the game's flags run to 755; the Loader's 756-759 are Semyon's shipment and the champions'). Each pass in
the pens with it set and flag 757 not, `semyon.ship` puts Thornwall on the
pens' weapon rack: the rack found by its object (2599) among the map objects
(the game makes a region's objects as the party comes near them, so nothing
happens until it has made the rack; its item type, 6Ch, is a coffin's too), an
item record from the game's free list, first in the rack's contents
list (the object its +8 names), then flag 757. A Thornwall somewhere already
(the rack's data had it from 1.2.0 to 2.13.4, so a save from then that has been
to the pens) sets 757 with none made. Once on the rack it is the game's own,
kept and saved as any item. Once a party member carries it (any of its three
item lists, or a bag in one), `semyon.found` sets flag 758, and his menu has "We found what was
in that crate." (shown with 756 and 758 set).

## What Dinos and the Trustee say about them

([In the features page](FEATURES.md#what-dinos-and-the-trustee-say-about-them).)

How: in the Loader's copy of `GPLDATA.GFF`, their scripts (139 and 146) keep
every byte where it was, since the game's jumps go to fixed places. Two
commands become jumps to code after the script's end: the one starting the
menu's part goes to the same command followed by the new questions' flags
(766-769, 773, 774), and the menu goes to a copy of it (the game's own bytes)
with the new questions after its last about someone. Each then jumps back to
where the game's script carries on.

That (with [his busy line](DEVELOPMENT-RULES.md#picking-pockets)) makes the Trustee's script
10,967 bytes, and the game reads every script into one buffer of 10,000 bytes
(a script that calls into another reads it in over its own). One of 9,800
bytes ran; one of 10,000 ended with "BAD GPL EXIT" (the game's own largest is
9,792). So the Loader's copy of the game makes the buffer 11,776 bytes where
it is allocated (`push dword 10000` at 6A692h becomes 2E00h), about 1.7 KB
more of the game's memory.

## The game's people's gear

([In the bugs fixed](FEATURES.md#the-games-bugs-fixed); `people.py`.)

The game makes a person's items in its backpack list (+0Ch) and puts them on only at its first
action in a fight. Seen in DOSBox (2026-11-06, `playtest/logs/2026-11-06-npcs-equip.md`): at the
alarm fight's start all 30 people's gear was in their packs; Kurzak, backstabbed before his turn,
was AC 10; once Legcrusher and an Arena Guard had acted, the Guard wore his leather chest armour
(slot 9), arm armour (0) and arrows (1) and held his obsidian long sword (3) and bow (2), and
Legcrusher's AC from behind was 8 with his Leather Inixhide +1 on. Kurzak with two weapons fought
"main hand" with Shadowseeker +1 and "off hand" with his obsidian sword. A blow from outside a
fight is struck before the game starts it: Gerakis's sling shot at Legcrusher hit AC 9 with the
game's fight still off, which came on only after his alarm call was read.

`People.watch` (from the dice log's item watches, each pass) puts each person's gear on as it comes
on the map, once each (by creature, name and object; forgotten with a new area or a game loaded),
the champions left to `champions.Gear`, the party to the player: `plan` sorts the backpack by its
type's kind (+00h: melee, missile, shield, thrown) and where it is worn (+09h: 1 chest, 2 waist, 3
arm, 4 feet, 5 a hand, 6 head, 7 neck, 8 cloak, 9 a finger, 10 legs, 11 ammunition, 12 a missile
weapon: the game's item types, read in the running game), the best melee weapon (its plus) to the
right hand (not one that takes both hands when the left holds something already), a shield to the
left or else a second melee weapon (neither beside a two-hander), rings to the two fingers in turn,
into slots nothing fills yet. The game itself wasn't seen to put on rings, cloaks, belts, boots or
amulets; worn here, they count as the party's do (Pehtucl's Templar: his Ring of Protection +1 worn,
AC 4 to the other Templar's 5 and +1 on saves; his Cloak of Protection +1 is in his chest now, as it
gave nothing under AD&D's rule with his leather shield). Keys, food and scrolls stay packed. Each
move is `pickpocket.place` (the list for its slot found or made first, a new one from the game's
allocator; with none to be had, or fewer than the 20 the Loader leaves the game (`ring.RESERVE`),
nothing moves, and the person is tried again on the next passes, up to `TRIES` (3), then left as the
game has it), after `itemgate.hold`. Test: `test_people.py`. What it costs of the game's 200 things
from its free list (`playtest/thingsfree.py`, 2026-11-07): each person with gear holds two or three
lists, not one, about 21 more in the pens (143 free after loading, 131 in the alarm fight); the game
frees an area's lists as the party leaves it (191 free on arriving in the arena), so nothing builds
up.

## Pehtucl's chest

([In the new items](FEATURES.md#new-items); `pehtuclchest.py`, whose docstring has the detail.)

A USE command in the pens' master script (MAS 41: 6Dh, (place, script, object), as each cell door
has one running script 138) runs script 223 when the chest (object 1568) is used, from beside it
(the safe's distance test, op 80h: "You must be next to the chest"). Its parts are the
game's own: the thief test the safe in GPL 71 makes (the class flags' 400h), the scripts' skill
check (22h action 3: who, skill, bonus), the safe's bash odds, and the trap action (22h action 7:
object, square, the square from command 09h on the character). A trap object's item +0Fh is read
by the trap routine (DSUN.EXE 80A11h) as dice, reach and damage kind, not as a spell; the needle
(object 2667) is 02h, 2d6 poison on its square. The game opens a container as its USE script ends
(the script can't stop it), so the chest is made with the safe's item type (67h), which it doesn't
open, and `pehtuclchest.watch` makes it a chest (31h) once flag 796 is set, while the script waits
for a click. Flags 795 and 796; script 223 has its entry in GPLI (saves keep commands by entry).

## The champions' bout

([In the features page](FEATURES.md#the-champions-bout).)

How (`champions.py`, `bodyart.py`): six objects of the Loader's own, 2660-2665,
copies of the arena's kinds (the Tohr-kreen 292, the Guard 293, a half-giant;
the Wild Mul 290; the Renegade 289, a halfling; an elven caravan guard 103; the
Defiler 296), their records renumbered, named "Champion", their own items left
out and their gear in (as the new items, after the person), their sheets their
kinds' (the armour counting on top of their AC) but for DEX (`champions.DEX`:
18, the half-giant 15; the mul and the halfling have 18 already). Their pictures
are their kinds'.

The scripts: the arena's deaths (script 3) say "This makes ... king of the
pens!" and set flag 19 only when a party member kills Scar (flag 19 is set at
the end of Scar's visit too, whatever happened, and by the pens' script 144
when he is killed there, so it doesn't tell); that handler (script 3 at 176h)
is hooked on Scar only in the arena (MAS 42 and script 2, and script 154 calls
it for region 2Ah alone), so a kill in the pens gives no bout. The command
setting 19 there (3A7h) becomes a jump past the script's end, to the same
command, then one setting flag 759 (KING), then a jump back. The arena's visits (script 2) count in the game's number 12; a visit past
the fifth (12 at 5 or more) opens with the default speech ("Once again,
expectant spectators...", 0AD4h), and its waves come from the random wave maker
(called at 1581h, since the count is over 4). Both are jumps to parts of ours
that, while the bout is due (12 at 5 or more, 759 set, 807 clear), say the
speech, and put the six in (each a group of one: the wave's own subroutine at
9301 with its locals 12 and 13, as the game's waves do) and set 807 (FOUGHT);
else they do what the game did. What a jump leaves of a longer command is
filled with one-byte commands (`gpl.put_jumps`, with `gpl.FILL`, 61h, as every module's jumps
are now: eleven scripts once didn't decode after Semyon's and others' jumps), so the script still
decodes (the Loader's other
changes read it); and the longer script must still fit the game's script buffer
(`pensasks.LONGEST`), as the Loader's other script changes must.

The game's own count of visits ([the arena's count of fights](HOW-THE-GAME-WORKS.md#the-arenas-count-of-fights)):
script 2 marks the 5000th visit (number 12 at 5000, A58h) the war won, with
flag 10 set and a call to script 62 (at FAAh), which sets the final battle's state,
global number 49, to 3. Checked in play: the count going up once a trip,
Scar's challenge on the fifth, and, with the count set to 5000, the 5000th
trip's speech, the party sent back with no fight, and the final battle marked
won. The 1000th trip is as its script reads; it wasn't played.

Worn and wielded: the game's [item lists](DEVELOPMENT.md#what-is-known) work
for anyone, not only the party (and see [The game's people's
gear](#the-games-peoples-gear)): seen, a Tohr-kreen given Headsman in its held
list attacked "with Headsman +2 (1d10+2)" in place of its first two natural
attacks, its third kept; and two Tohr-kreen given scale chest armour in the
worn list went from AC 3 to -2 against the party's attacks.
`champions.Gear` (each pass of the dice log, in the arena) moves each living
champion's items, by type, to its slot (`pickpocket.place`, as the inventory
screen would), once; the defiler gets its scroll first (into its backpack, while
it still has one), a random one of `SCROLL_SPELLS` (the game's wizard spells
without the new ones).

The body: the game makes a Dead Body (object 1101, a container) where a
creature carrying something dies, and puts its things in it (DSUN.EXE 59412h,
"push 0FFFF044Dh" before the call that makes an object at the dying one's
place). The map's records hold a picture number too (+18h) but the game
doesn't draw from it (changed in memory, nothing changed on screen), so the
object itself is swapped: `gamepatch`'s `champion_body` makes the push INT
81h (`PROBE_WORN`, told apart by its return address 2754h), "push 0FFFFh",
"push ax", and DSCLOG answers 2666 (`champions.BODY`) when the dying map
object ([BP+6], its object at DS:66AEh + 32 each) is the Tohr-kreen champion,
else 1101. Object 2666 is a copy of 1101 (its record renumbered) with a picture
of its own, 2666 (`bodyart.py`: the Tohr-kreen's frame 8 turned on its side,
squashed to 0.75 of its height, darkened to 0.7, its gythka's pale pixels left
out, over the red of the Dead Body's blood). Seen in DOSBox: the six came on
(the bout forced due for the test: the arena's flags have no place in memory
to be set from outside), each with its gear in place, the mul's two axes, the
halfling's sling, the elf's bow and the half-giant's great axe each attacking,
Kreenfang 2d4+1; the Tohr-kreen's body object 2666 with Kreenfang in it, the
others' Dead Bodies with their gear.

## The cooked vulture

([In the features page](FEATURES.md#the-cooked-vulture); `vulture.py`.)

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

## Defilers' scrolls

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

## What the party wears

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
picture's place and length there each time it loads one), and empties the
figure's slot on the map: the game draws the new pictures at once, in a few
thousandths of a second (`dsloader/sprites.py`).

The game keeps every picture it loads in a table of 300 slots and a store of
a fixed 741,376 bytes, appends a slot (and the room after the last) for each
picture number it hasn't got, and gives neither back until an area loads. So
the Loader puts each new picture where the game already keeps one
(`Dresser._in_store`), finding a picture by its number as the game does: a
slot it took out earlier that holds exactly this picture (an outfit changed
back) is given the number back; else the picture's own slot, when it isn't in
memory (the inventory open lets every picture go), has the new picture
written into the store at its place; else the smallest slot taken out earlier,
not in memory, with room for it, gets the picture and the number. The old
slot is taken out of the table (its number changed: the game frees its
memory itself, as any it no longer draws). Only with no such slot does the
game load the new picture into a new slot, and then only while the store and
the table keep room for it and the game's own (64 KB and 24 slots,
`_room_for`); else the figure stays as it was until the next area. The store
is a handle of the game's paged memory manager whose pages are in XMS
(`sprites.Store`: the handle at DS:4C33h, the handle table at DS:47FAh, the
page directory at DS:42D2h, backend 0's XMS move at 1187:04B0h); in DOSBox the
XMS block is ordinary memory above 1 MB, found by an in-memory picture's
bytes. Nothing in memory is written (the game moves its pictures' memory when
it makes room), nor a slot's length (the memory the game frees with it), and
DOSBox is held still for the writes. Where the store isn't found (another
memory backend, Dark Sun Recompiled), each new outfit takes a new slot as
before, under the same room check. It then has the helper draw the view again (see
[Shadows](FEATURES.md#shadows)), so the shadows show the new outfit too. A
picture the game loads later (in a fight, in another area) comes dressed, from
the file. The copy also has a spare pair of pictures for each party place.
Each thing on the map names the picture it is drawn with and the slot in the
game's picture table it is drawn from; for a second member of the same figure
the Loader names their spare there and empties the slot, and the game loads
the picture and fills it.

## Elves and half-elves

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

## Shadows

([In the features page](FEATURES.md#shadows).)

How: the launcher's copy of `DSUN.EXE` (see [How the dice log
works](DEVELOPMENT.md#how-the-dice-log-works)) calls DSCLOG when the game draws the floor of
the view or of a rectangle of it. DSCLOG then lays each casting figure's current
picture, flattened and stretched, onto the floor just drawn, darkening each
pixel to the closest clearly darker colour of the area's palette (a table it
makes from the palette when the Loader asks: after each area change, once its
fade-in is over, and now and then; the colours the game cycles, for water and
fire, are never picked as darker ones). The rectangles the game draws again when
a figure moves are widened by the length of a shadow, so none is left behind.

**Pictures out of memory.** The shadow is traced from the figure's picture in the game's picture
cache, and in a big fight (the arena, ten monsters) the game lets go of most pictures between
drawings: in a save in the arena every figure but one had its picture out of memory as the floor was
drawn, so no shadow. Loading one from here, in the middle of a drawing, could push out or move a
picture the game is about to draw, so instead DSCLOG keeps each frame's shadow as it draws it
(`SC_START`, `SC_PUT`, `SC_END`: the runs that cast a shadow, three bytes each, at most 64, under
the picture's number from the cache slot's `+6` and the frame) in 80 slots of 208 bytes in the
helper's far block (`SC_SEG`, at `FAR_SC`: see [Room in the helper](DEVELOPMENT.md#room-in-the-helper)),
the oldest given up first. A figure
whose picture is out casts its frame's kept shadow, or another frame's of the same picture
(`SC_FIND`). Measured in the arena: 74 slots filled in a few rounds, the party and the monsters seen
in memory once casting shadows after; one whose picture was never in memory at a floor drawing still
has none. Only pictures already in the game's cache cast one: until 2.6.0 DSCLOG had the game load a
missing one from there (1DF3:2A3Ah), in the middle of drawing the floor, which can push out or move
another picture while the game is drawing; a freeze report of 2026-10-21 has a figure's picture
unpacked from garbage, the row decoder (0980:709Ch, into a 5,408-byte buffer at 0980:11BCh) never
meeting its row's end and copying over the code after it, itself included, with the game's data
segment then overwritten by its stack. A figure whose picture isn't loaded gets its shadow when the
game has loaded it to draw the figure, a frame later; one the game leaves undrawn (its map thing's
80h bit) or with no picture at all (FFFFh in its cache place) casts none (`shadow_of`). The Loader
keeps DSCLOG's list of who casts one (`dsloader/shadows.py`) and has DSCLOG draw the view again when
it changes (from the game's main loop, as centring the view does: marking the figures changed
instead, as the game's own code does to draw one again, can set one in a fight walking again).

The list can be up to half a second old, so as it draws DSCLOG also checks
the creature's status (`SHADOW_GONE`: the things table, then the creature's
`+1Ch`) and gives a dying (4) or dead (5) one no shadow. Otherwise it would
load the dying creature's new pictures through the game's picture loader from
inside the floor drawing, the most likely cause of a crash seen in the arena
as a creature died (not reproduced).

## Dust

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

## See-through figures

([In the features page](FEATURES.md#see-through-figures).)

How: the game draws each thing on the map through one call, `call far 1A0A:3180` in its routine
at 25E0Ch (25EBEh; DI the thing, the call's arguments the page, x, y, mirrored, the picture and
the frame). Gamepatch's `ghost` puts DSCLOG's `INT 80h` (`PROBE_GHOST`) over it. A thing that is
neither a hidden party member (its `STEALTH` bit, which `PROBE_STEALTH` clears at the attack) nor
marked in `GHOST_TAB` goes on to the game's routine as ever. A see-through one DSCLOG draws itself
(`GHOST_DRAW`):
- it decodes the frame's runs, each pixel mapped to one of 32 colours (`REP`), into a buffer, and
  notes each run within the page (the page's bounds and memory found as the shadows find them,
  `PAGE_SETUP`); a mirrored frame's pixels are read from the run's other end. Room for 4,096
  pixels and 192 runs (`GH_PIX_MOST`, `GH_SPANS_MOST`): the party's figures have at most 78 runs a
  frame, but some of the game's pictures up to 563, so past either it draws what it has (it once
  wrote past its block instead: `test_ghost_draw_many_runs`);
- then, a plane at a time (the VGA's map mask and read map), it reads the pixel under each and
  writes `BLEND[rep][under]`, the colour nearest the halfway mix.
Every pass that draws figures draws the floor first (the routines `PROBE_FLOOR` hooks), so the
floor read is the fresh one, with the shadows and the figures behind already on it.

The game draws an invisible creature as any other. Its rules for it are numbers only (7BD4Bh,
"can't see": the attacker Blind, or the target Invisible, effect 23, or Invisible to Undead, 24,
against the undead, unless the attacker has Detect Invisibility, 15; its two callers give -4 to
hit, 7C6B8h, and +4 to the target's save against a spell, 79E99h). Among the game's foes only the
psurlons turn invisible: their psionic list (37F0:001Ch, list 8) has Superior Invisibility, which
puts on effect 23. No foe's spell list (3FB9:0110h) has an invisibility spell, and no script or
item makes a creature invisible.

`dsloader/ghost.py` keeps `GHOST_TAB` (520 bits) from the game's effects: a party member with effect
23 always, anyone else only while no party member has effect 15. It makes `REP` (the palette's
colours 16-223, the ones the game doesn't animate, cut into 32 boxes by median cut) and `BLEND` (32
x 256) from DSCLOG's copy of the palette each time DSCLOG reads it again with `DARK` (0.2 s of
Python, in a thread), keeps the last eight by the colours the game never cycles (`ghost.key`: every
colour but the cycled 1-15 and 240-248, as 224-239 differ between areas; `MADE_KEPT`: the whole
palette changes every 30 s where the game cycles fire's or water's colours, and each change once
made them again, solid meanwhile), and writes them into DSCLOG's block, 885 paragraphs of upper
memory taken at `KEEP` (`GHOST_SEG`, header +1826; none, no see-through figures). `GHOST_ON` (+1828)
is 0 until they are written. The view is drawn again when a figure turns see-through or solid
(`TSR_VIEW_REDRAW`). That is done from the map's main loop, which doesn't run in the enemies' turns,
so a thief whose turn had ended kept the see-through picture until a party member's turn (about 1.4
s, seen 2026-11-06). So `PROBE_GHOST` notes each party member it draws see-through while hidden
(`GH_SHOWN`), and `GHOST_UNION`, in `PROBE_REDRAW_ALL` (the game's drawing again of what moved, at
each step of anyone's), has the whole view drawn once when one of them is hidden no longer: solid at
the enemies' first step (test `test_solid_at_turn_end`). The same once the Loader writes GHOST_TAB
anew (it sets `GH_CHANGED`, the room's last byte): an invisibility ending in the enemies' turns
shows at once (test `test_whole_view_when_the_table_changes`; seen in DOSBox, the byte cleared 0.06
s into an enemy's turn, `playtest/logs/2026-11-07-review-fixes.md`). Seen in DOSBox, 2026-11-05: a
figure marked drew half see-through over floor, wall and its shadow, facing either way and walking;
in a fight, a real hide (solid again from the backstab on) and a real Invisibility, walking at the
solid pace (`playtest/logs/2026-11-05-fight-test.md`).

## Sounds for hiding and picking pockets

([In the features page](FEATURES.md#picking-pockets); `sounds.py`, whose docstring has the
detail.)

Two sounds of the mod's own, chosen by the user from eight made for them: a breath sinking away
as a thief or ranger hides and moves silently in a fight (BVOC 140, `HIDE_SOUND`), and a purse's
jingle for a picked pocket, a thing or the coins (BVOC 141, `PICK_SOUND`; a weapon worth the
quest's XP keeps the quest's sound). Their samples are `dsloader/sound-data/*.wav` (8000 Hz,
8-bit mono, the game's form; `make.py` made them), put in the Loader's copy of RESOURCE.GFF as
Creative Voice Files like the game's.

The game finds a sound through its table of 181 (3A98:08A2h, 6 bytes each: its kind, then a far
pointer to a 12-byte descriptor naming the BVOC); only 0-130 are digital, so a BVOC numbered past
them isn't played by its number. DSCLOG's `PLAY_SOUND` lends itself entry 131 or 132 for the
call (one for each sound: the game keeps the last clip it loaded under an entry), as a digital
one with a descriptor of its own, and puts the entry back. Two words at the header's end ask for
them: `SOUND_REQ` (+1822: played from the map's main loop, `SOUND_TICK`) and `PICK_SOUND` (+1824:
played with the pick's text, `GIVE_XP`). A Spellarcher making spell arrows hears the spell's own
cast sound (its spell record's +0Fh, `spellarrows.cast_sound`), through `SOUND_REQ` too. Seen in
DOSBox (2026-11-05, its output recorded with `PT_AUDIO` and matched with the clips: r 0.995 to
0.997): both on request, in either order and after one of the game's, entries 131 and 132 as the
game had them afterwards, and from a real pick and a real hide. Tests: `test_sounds.py`,
`UseItemTests.test_sound_tick`, `test_pick_sound`.
