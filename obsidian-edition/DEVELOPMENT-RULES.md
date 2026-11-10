# Development: the rules

*Part of the [development notes](DEVELOPMENT.md). How each rule change, the character customization (weapon specs, kits, the starting gear) and the improved thieving are done: where the patched game calls the helper (DSCLOG), and what the Loader reads and writes. Each heading names the section of the [features page](FEATURES.md) or the [README](README.md) it explains.*

## Contents

- [Class restrictions](#class-restrictions)
- [Multiclass hit points](#multiclass-hit-points)
- [Hit dice: the better of two](#hit-dice-the-better-of-two)
- [Scores and hit points as rolled](#scores-and-hit-points-as-rolled)
- [AD&D's class tables](#adds-class-tables)
- [CON as in AD&D](#con-as-in-add)
- [Dual-classing as the manual has it](#dual-classing-as-the-manual-has-it)
- [Ages](#ages)
  - [Haste's aging](#hastes-aging)
  - [Restore Youth](#restore-youth)
  - [Natural aging](#natural-aging)
  - [The age on the creation screen](#the-age-on-the-creation-screen)
  - [Grey hair on the map](#grey-hair-on-the-map)
- [Two weapons](#two-weapons)
- [Half-giants' two-handed weapons](#half-giants-two-handed-weapons)
- [Cahulaks](#cahulaks)
- [Creature size](#creature-size)
- [Rings and cloaks of protection](#rings-and-cloaks-of-protection)
- [Helms](#helms)
- [Items saving against acid](#items-saving-against-acid)
- [Rangers' casting level](#rangers-casting-level)
- [Preservers' INT](#preservers-int)
- [Spells saved against with the spell save](#spells-saved-against-with-the-spell-save)
- [Fire, cold and electricity: DEX instead of a doubled d20](#fire-cold-and-electricity-dex-instead-of-a-doubled-d20)
- [Enlarge's dice](#enlarges-dice)
- [Spells roll to hit](#spells-roll-to-hit)
- [Resting as in AD&D](#resting-as-in-add)
- [Turn Undead, Minute Meteors and Flame Arrow as the manual](#turn-undead-minute-meteors-and-flame-arrow-as-the-manual)
- [Spells and psionics as the manual, group 3](#spells-and-psionics-as-the-manual-group-3)
- [The monsters as the manual describes them](#the-monsters-as-the-manual-describes-them)
- [Weapon specialization](#weapon-specialization)
- [Kits](#kits)
  - [The kits](#the-kits)
  - [The kit's byte](#the-kits-byte)
  - [Choosing one](#choosing-one)
  - [Multiclass kits](#multiclass-kits)
  - [Where each effect goes](#where-each-effect-goes)
  - [How they're checked](#how-theyre-checked)
- [Level cap by XP](#level-cap-by-xp)
- [STORE and RECALL on the creation screen](#store-and-recall-on-the-creation-screen)
- [Fuller starting gear](#fuller-starting-gear)
- [The game's own party](#the-games-own-party)
- [The leader's CHA at shops](#the-leaders-cha-at-shops)
- [Buying back magical items](#buying-back-magical-items)
- [Thief skills from AD&D's table](#thief-skills-from-adds-table)
- [Hiding in shadows to backstab](#hiding-in-shadows-to-backstab)
- [Spell arrows](#spell-arrows)
- [Picking pockets](#picking-pockets)

## Class restrictions

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

## Multiclass hit points

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

## Hit dice: the better of two

([In the features page](FEATURES.md#hit-dice-the-better-of-two).)

How: where the game has rolled a level's die (`INT BAh`, in place of the
`mov cx,ax` after the roll, DSUN.EXE 87319h), the helper keeps the first roll
and sends the game back to the start of its roll (872FDh), so both rolls are
the game's own and the dice log sees both; the second time it keeps the
better. Creation goes through the same routine, a die for each starting
level.

## Scores and hit points as rolled

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

## AD&D's class tables

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

## CON as in AD&D

([In the features page](FEATURES.md#con-as-in-add).)

Regeneration: the game's routine (227E5h, called often; it acts once more than
300 seconds of game time, the clock at 3781:35Bh, have passed since the last,
DS:1654h) gives each party member a psionic strength point for each 300
seconds and, with CON 20 or more, a hit point for each 300 too, at any CON,
dropping what is left over. DSCLOG's `REGEN_SITE` (228BFh, after its
`div ebx`) with `RULE_HI_CON` (`game.RULE_CON`) adds the seconds to the
member's own count (`REGEN_SECS`, the remainder kept) and gives a hit point
for each (26 − CON) × 600 seconds: AD&D's one an hour at 20 to one every 10
minutes at 25. The psionic points are left as they are.

Poison saves: the saving throw's CON adjustment (5EA91h, the table at DS:810h
by CON) is added to the paralysis/poison/death save, and for a dwarf or a
halfling its CON × 2 / 7 as well. DSCLOG's `CON_SAVE` (5EAA1h) makes the
adjustment 0 for a dwarf or a halfling with the rule, so only the racial bonus
counts; the Loader's saves (`GameData.save_modifiers`, `saves_now`) do the
same. Checked in DOSBox: Gerakis at CON 22 an hour on, 1 hit point (the game's
way 12), and the 1330 seconds left over counted towards the next. The saves
are checked by the emulator (`test_dwarves_poison_saves`): the party has no
dwarf or halfling.

## Dual-classing as the manual has it

([In the features page](FEATURES.md#dual-classing-as-the-manual-has-it).)

DUAL is on the two portrait menus (70CE4h and 70F03h) for a human (+18h 1) whose
sheet's first level (+24h) is 2 or more, and the DUAL window (866C7h) greys each
class 1-17 by 86E94h(member SI, class DI): human; the current class's (the
sheet's +21h) one prime requisite on the creature (+22h + the ability the
game's table gives: 338:0180h + row x 3, the row from 338:00CAh + class x 2) 15
or more (86EFCh); the new class's 17 or more (86F31h); the third class slot
(+23h) empty; the level 2 or more again (86F58h); no group the character
already has; a ranger good, a druid true neutral. The game's table has one
ability a class (a ranger's, druid's and psionicist's WIS).

`RULE_HI_DUAL` (`game.RULE_DUAL_CLASS`) is DSCLOG's, so the five compares are
sites in every game's copy, each doing the game's own compare with the rule
off: `DUAL_LEVEL` (`dual_level_menu`, `dual_level_view`, `dual_level_window`:
`cmp byte [es:bx+24h],2`, 3 with the rule) and `DUAL_PRIMES` (`dual_old_prime`,
`dual_new_prime`: with the rule every prime requisite of the class,
`DUAL_PRIMES_OF`'s bits, the manual's as `tracker.PRIME_REQUISITES` has them,
the old class at 15 or more, the new at 17 or more, on the creature's scores
as the game reads them). Each sets the flags for the game's own jump after it.
The old class is the sheet's first, as the game's (a second change checks the
first class's level and primes, the game's way). Checked by the emulator
(`test_group4`'s `test_dual_level`, `test_dual_primes`).

## Ages

([In the features page](FEATURES.md#ages-and-magical-aging).)

How: the Loader (`aging.py`, with `RULE_AGING`, RULES_HI's 256) keeps each
party member's age in the sheet's +17h (`SHEET_AGE`: the age less the race's
base starting age, plus 1; 0 none yet, a thri-kreen's 6 being its base), the
byte the packed weapon specs leave free (Weapon specialization, below). A member
with none gets its starting age (`give_ages`, Table 7's dice rolled: the game's own party, one
from before ages; in the dice log's item pass, not
while DSCLOG's weapon window is up: its trial puts the four bytes back as they
were). `age_by` moves an age (Haste, Restore Youth): the categories reached or
left change the sheet's scores and the creature's (`changes`, Table 8, the
scores kept within 3 to 25), and the maximum (`most_age`: the race's base and
dice, seeded with the character's name and race, so always the same) kills
(`kill`: no hit points, the game's dead status). The Loader puts the age, its
category, the next and its age in each member's STATS (+28h on: `STATS_AGE`),
and DSCLOG's `AGE_TEXT` writes the age, `AGE: 23`, in the inventory panel's
free row between the saves and STR (`PROBE_INV`, `AGE_INV_Y`; the THAC0 and
save rows 3 pixels higher than before to make room). The category and the
next are for the Characters tab; the game's screens show only the age (the
inventory panel and the creation screen, below).
Checked in DOSBox: the game's own party given ages in a new game, the
inventory panel and the Characters tab.

### Haste's aging

The dice log's `effect_changes`, as a Hasted effect (22) starts
on a combatant (not one a game just loaded has), calls `aging.hasted`: a system
shock roll by the creature's CON (`SYSTEM_SHOCK`, the Player's Handbook's
table), death on a failure (`kill`: HP 0 and the dead status, which the game
takes as dead: no more turns, no share of the XP, "Dead" under the portrait),
else a year (`age_by`) for a party member. The rolls are the Loader's, logged.
Checked in DOSBox: Gerakis at CON 1 hasted by Cermak (90 against 25: dead) and
K'ratchek at CON 19 (89 against 99: 7 years old).

### Restore Youth

Restore Youth (211, a cosmos spell: `COSMOS_MASK` in DSCLOG's `P6_MASKS`) is
Cure Critical Wounds' record with its dice (+1Ch to +1Eh) made 0 and no
handler, so the game casts it as a touch spell that heals nothing. The dice
log's `KIND_CAST` line for it calls `aging.restore` with the target and the
caster's level (`effect_caster_level`): a system shock roll, then `age_by` back
by the level, never below the character's true age (`start_age`: the race's
base and the roll kept on the sheet, `game.sheet_roll`, with the game's years;
no cap on the years magic adds). Checked in DOSBox: K'ratchek at 12th
level casting it on Gerakis aged 37, true age 27 (survived, 27 again).

### Natural aging

A year each time the game's clock passes another 365 days (`natural_years`:
the game time in seconds over `YEAR`), put in the stored age as it happens, so
a save holds the age and the scores' changes together. The years counted so
far are in the game's own flags, so a save keeps them too (`counted_years`,
`set_counted`: flag 798 set once the count has begun, 799 to 806 the number;
every flag the Loader uses is in [The Loader's game
flags](DEVELOPMENT.md#the-loaders-game-flags)). The dice log's `_natural_aging`, after
`give_ages`, looks only when the look is steady (the same party as the last,
the clock on by no more than 2 days, `NATURAL_JUMP`, and the count and the
clock's years as the last look found them: a game being loaded may have its
flags before its clock, or its clock before its sheets, for a moment) and the
flags have a place in
memory (`flags_ready`: not in the arena outside a script's run), and otherwise
waits for the next; then `natural_years_due` counts each year of the clock not
yet counted (`natural_tick`): for each living member, the stored age on, a line
(`A year has passed: Gerakis is 35.`) and the categories reached (`_changed`,
as `age_by`), death at the most the race lives. Nothing is counted twice or
lost: a load brings its own count, and a year that passed in a long jump, in
the arena, or while the game ran without the Loader is counted at the next
steady look. A game whose count hasn't begun (a new one; one saved before
2.13.1) begins it at the clock's years, aging no one for those before. Restore Youth's floor, the true age, is `start_age` plus
the clock's years (one who joined late gets fewer years back, never more).
Checked in DOSBox: the clock put a few minutes short of a year, then past it:
a line for each of the four, once, and `AGE: 35` on Gerakis's panel.
Tests: `test_natural_years`, `test_restore_counts_the_games_years`,
`test_the_log_counts_each_year_once`, `test_a_long_jump_waits_and_loses_nothing`,
`test_a_save_is_as_old_as_its_count`, `test_a_load_caught_halfway_ages_no_one`.

### The age on the creation screen

`CR_AGE`: the age the character will start at, Table 7's dice rolled for real
(`age_dice`: its race's dice from `AGE_RACES`, each die from `age_rand`, an LCG
`x * 25173 + 13849` xored with the BIOS tick count at 0040:006Ch, its high byte
mod the sides), kept as the roll less the dice count (`CR_ROLL`, 0 to 20) and
the race it was rolled for (`CR_RACE`; `cr_rolled` rolls again whenever the race
isn't that one), drawn above RECALL, in the PSP box's row: nothing of the
game's is drawn there, and the PSP box (the screen's 8th, `DS:0F62h` on) is
widened to x 200 (`cr_age_box`), so its saved background, put back each time
PSP is drawn, clears it. It is drawn after PSP: at 65A89h (the die, a choice,
the screen opening: a new roll, `CR_RACE` cleared, except while RECALL puts a
stored roll back, `CR_KEEP`) and at 63A13h (a click on CON: `CR_AGE_CON`, the
roll kept); and, as a name changes after those (the game's own, 66045h and
6349Fh, a figure clicked; one typed, 63AE8h, or the game's put back when none
is, 63B2Dh), again then: the PSP box put back (`0A0h:30C3h`, the operand read
from the overlay's code as loaded: its selectors fixed up there), PSP drawn
again as the game draws it (centred on its x, 6 pixels a character: its own
routine, 538h:43h, is an overlay stub, not for calling from an interrupt) and
the age (`CR_NAME`). STORE and RECALL keep `CR_ROLL` and `CR_RACE` with the rest
(`rs_xfer`). DONE puts the roll and the age in the new member's sheet
(`AGE_PUT`, in `CR_WEAPONS`: the v2 layout, Weapon specialization below; no race
known, `ROLL_UNKNOWN` and no age), so the Loader's `give_ages` leaves it be.
EDIT on a party member (the portrait's menu) opens the same screen on a copy of
its sheet, which the game tells from a new member by DS:0E9Ch (-1 new, else the
member: 65C6Dh). `CR_OPEN` (a site at 65C68h, `mov byte [1A58h],0FFh`, just
before that test) keeps the member's race, classes (as the sheet numbers them, and as
the screen does, `KIT_CLASS_OF`), kit, `+14h` dword and six scores (`ED_*`), puts
its kit on the copy (which the game's copy leaves out) and its classes in
`wp_classes_seen` (else `KIT_STALE` takes the kit off both sheets), and its
roll in `CR_ROLL`: the age shown is its own (`ED_AGE`) until the scores change
(`ED_ROLLED`: the die; the hit point die's probe runs at the opening too). The
panel's opening gives the kit back while the race and classes are the member's
(a multiclass kit's number is its race's group's) and, for a Healer, water is
marked (`HEALER_BARRED`, as the kit page has it). At DONE,
`CR_WEAPONS` asks for no weapon specs while the classes and kit are the
member's (`ED_SAME`), keeping its specs with the screen's roll and age
(`ED_KEEP`; an older sheet's dword as it was). Before this, EDIT took the kit
away, rolled a new age and asked for the weapon specs again. Checked in DOSBox:
a Sentinel fighter edited, renamed and DONE kept the kit, its long sword and
its age; with the die rolled during EDIT, a new age and the same kit and spec.
Tests: `test_edit_keeps_its_specs`.

The THAC0 (`CR_THAC0_DRAW`, whatever the rules): `THAC0: M18 R19` at `CR_AGE_X`
on the hit points' line, the THAC0 (`CR_THAC0_BASE`) less the game's STR
to-hit table's entry (DS:7C2h + STR) for M and its DEX missile table's
(`DEX_REACTION`'s, + DEX) for R, no less than 0. The game works the THAC0 out
again as the classes change, but `PROBE_THAC0` reads the kit from the party's
sheets, not the one being made, so the creature's `+1Fh` lacks a kit chosen on
the panel: `PROBE_THAC0` keeps the game's own, kit-less (`THAC0_GAME`,
`THAC0_SEEN` from `CR_OPEN` on), and `CR_THAC0_BASE` applies the sheet being
made's kit to it (`kits.thac0`: a Scholar 1 worse, a warrior's THAC0 for the
Swashbuckler, Crusader, Battle Mage and Mind Warrior); with none worked out on
the screen (an EDIT), the creature's `+1Fh`, its kit in it. A kit chosen or
taken back (`KIT_SHOWN_DUE`, from `KIT_ROW`) draws the hit points and the
THAC0 again at the click's end (`KIT_REDRAW`), after a Battle Mage's, Mind
Warrior's or Arcanist's hit points are rolled again (`KIT_REROLL`) the age too,
whose PSP box that puts back. The hit points' box (the 7th, `CR_HP_BOX`) is widened to x 243
(`cr_thac0_box`; DONE's left is 244), so the game's putting it back clears the
line. It is drawn after each redraw of the hit points: the panel's, at
`CR_AGE` (65A89h, PSP after them), a click on CON (`CR_AGE_CON`), and `CR_HP`
(a site at 63AC3h, a click on the hit points, and 63EDAh); a click on STR or
DEX redraws neither, so `RL_SUM` (the scores' redraw) puts the hit points' box
back itself (`CR_BOX_PUT`, the far call's operand and the saved backgrounds'
segment read from the overlay's code beside its site, as `CR_NAME` does for
PSP's), draws the hit points again (`CR_PAIR_DRAW`, shared with PSP's) and the
THAC0. Checked in DOSBox: THAC0 18 with STR 17 and DEX 15 `M17 R18`; DEX 18
after a roll `R16`; STR 18 `M16` at once; a click on the hit points and on CON
keep the line; a 3rd-level preserver `M19 R20`, a Scholar `M20 R21`, a Battle
Mage `M17 R18` (the line and the age back after its hit points are rolled
again). Tests: `test_thac0_line`.
Before 2.13.2 the age was rolled from the name and race (`natural_start`, a
16-bit hash, DSCLOG's `AGE_ROLL` then); a character given one keeps it, and
`give_ages` puts that roll on its sheet, silently. `CR_AGE` and `CR_NAME` keep
their way back in their own words (`cr_ip`, `cr_cs`, `cr_fl`), apart from
`RL_SUM`'s, as they call the game's code before going back. Checked in DOSBox:
four rolls of the die gave 23, 20, 18, 20; STORE at 20, a roll to 17, RECALL
back to 20; CON lowered and raised, 20 both times; DONE and a weapon picked,
the sheet's roll 4 and age byte 6 (15 + 1 + 4 = 20). Tests: `test_age_dice`
(each race's rolls in range, a human's all 0 to 7), `test_age_put`,
`test_name_redraws_psp_and_age` (the operands read from the overlay's code, PSP
centred, the age; none called for an operand not fixed up).

### Grey hair on the map

`greyhair.py`: as the Loader dresses a member's
pictures (`sprites.Pictures.build`), after their gear, the hair is recoloured
by their age category (`stage_of`; the redraw keys on it, so a category reached
redraws them), only on pixels still in the hair's own colours, by `MAPS` (each
look's colours to the stable greys 208-217 and white 46; `SPECKLE` streaks a
category). The hair to grey is found apart from the gear's (`greyhair.hair`, so
helms and cloaks don't move): spriteparts' way, with each race's corrections
found frame by frame for each race (`COLOURS`, the hair's missing shades;
`STRICT`, the search kept in the hair's zone where the face has its colours;
`HEADS`, the bow frames, whose bow tip was taken for the crown; the
half-giants' face masks and the halfling man's `FACE_FROM` and short hair; the
elves' skin-brown shading, `BROWNS`; a half-elf's own figure's hair grown to
its golden pixels, `own_hair`). Dwarves, muls and thri-kreen have none (a
thri-kreen's antennae greyed were tried and left out). Checked in DOSBox:
Gerakis old and Cilla venerable, their figures redrawn as their ages were set.

## Two weapons

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

## Half-giants' two-handed weapons

([In the features page](FEATURES.md#half-giants-two-handed-weapons).)

How: the inventory screen checks a weapon type's two-handed bit (+0Fh, 40h)
twice when something goes into a hand: the other hand's ("Two handed weapon in
use") and the one going in ("Need two free hands"). The helper (`INT E3h`)
answers both for the character on show, "not two-handed" for a half-giant.

## Cahulaks

([In the features page](FEATURES.md#cahulaks).)

How: one item, the right hand's, two heads. The game's attack set (58019h) makes
one call of the attack routine (5883Ah) a weapon; that call swings until a hit,
[BP-8] the round's swings, [BP-14h] the swing (the combat record's +181h the
swings made this round), [BP+0Ah] - [BP+0Ch] the d20 needed. With the rule
(`RULE_HI_CAHULAKS`):

- `CAH_MORE`, first in `OFF_HAND_HALVES` (the attack's `PROBE_ATTACKS`, the
  inventory's DAM line, View Character's): 2 more halves for an item of type 21,
  one attack more a round.
- `CAH_TWO` (59627h, the two-weapon adjustment's "cmp word [bp+6],1 / jle"):
  595ECh asks for its adjustment only with two weapons ready (5900Ah's count);
  for the cahulaks it goes on, and `PROBE_TWO` gives AD&D's numbers whatever
  `RULE_TWO_WEAPONS`, with nothing needed in the other hand (`CAH_ADJUST`): the
  main head's (-2, the kits' changes, DEX's adjustment, no better than 0) for
  every swing, and `CAH_EXTRA`, how much worse the off head's is, for that
  attacker (`CAH_WHO`).
- `CAH_SWING` (589B6h, the swing's start, before its d20): the round's last swing
  of two or more, the off head's, adds `CAH_EXTRA` to [BP+0Ah], once. The dice log
  reads the attack's arguments at the d20, so its "needs" counts it, and its
  breakdown names each head (`GameData.two_weapons(..., head)`).
- `CAH_HIT` (58B54h, a weapon's hit that did damage): the target ([494Ah]) not
  felled (the creature's +0 HP), not a half-giant (the sheet's race), not marked in
  `BIG` (the far block, its offset the header's +1840: the Loader's,
  `cahulaks.py`: a bit a combatant whose creature's name is on its list, written
  when it changes), saves against petrification with a d20 (`GAME_DIE`) against
  its sheet's +39h, a 20 always saving; recorded (`KIND_MANUAL`, `MN_TANGLE`). A
  failure marks it as Whirlwind's sweep does (`SWEPT_NOW`: yet to act this round,
  its turn taken at once; else `FAR_SWEPT`, `PROBE_MOVE` takes the next).

## Creature size

([In the features page](FEATURES.md#creature-size).)

How: the game keeps no size. The Loader's `sizes.py` gives each creature one
(people by the sheet's race, the rest by name: `CREATURES.md`), and `sizes.Large`
writes `LARGE_BITS`, a bit a combatant large or bigger, into the helper's tail (its
offset the header's +1842), when it changes. With the rule (`RULE_HI_SIZE`, the
Loader's `RULE_SIZE`), `IS_LARGE` counts a combatant large when it is Enlarged
(effect 16, `NS_HAS`), marked in `LARGE_BITS`, or a half-giant (the sheet's race 5):

- `SIZE_DICE`, from `CAH_SWING` (589B6h): at the attack routine's (5883Ah) first
  swing of a call ([BP-14h] = [BP-0Ah]) with an item ([BP+12h] not negative),
  the dice it rolls at its hits ([BP-0Eh] count, [BP-10h] sides, [BP-12h] bonus)
  become AD&D's against a large target ([494Ah]): `LARGE_DICE` by the type's weapon
  kind (`KIND_OF_TYPE`; count, sides and a change to the bonus; zeros where the
  large dice are the small), the Spiritual Hammer (type 30) 1 off its bonus;
  against a smaller one, Shillelagh (type 28) 1d6+1 for its 2d4. The dice log
  reads the dice from its roll and notes the change (`sizes.dice_change`).
- `SIZE_SPARED`, from `SAVE_SUM` (79B97h, the save routine 79A71h: [BP+6] the
  target, [BP+0Ah] the spell): Charm Person (2), Hold Person (30, 86) and Charm
  Person or Mammal (82, only on a person: race 1-8) on a large target give the sum
  `SAVE_MOST` (110), a save made whatever the roll; the dice log says "too big for"
  the spell (`sizes.spared`).
- `SIZE_LINE` (72AA7h, the "inc word [bp-2]" after 7286Fh, the routine writing a
  weapon's lines for the item box and the inventory, has drawn its damage line from
  SS:[BP-2Eh]): the line read back ("1.5x1D8+7"), the large dice worked out from it
  as `SIZE_DICE` does, and drawn with the game's own text call (its far address read
  from the call before): the box's line again with `/1D12+7` after it (its spare row
  is the "Hit -1"/charges one); the inventory's `Large 1D12+7` a row under, counted in
  [BP-2] so the caller moves the next weapon down, `SL_EXTRA` keeping `PROBE_WEAPON`'s
  THAC0 on the damage line. Not the Look box's list (another x: no row to spare),
  nor Shillelagh (its line the game's 2D4).

## Rings and cloaks of protection

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

## Helms

([In the features page](FEATURES.md#helms).)

How: the helper sets the helm types' AC as the game's AC routine reads it
(`INT F8h`, the Ring +1's place), and as the item box reads it for its "AC
BONUS:" (`INT 88h`, at 8C15Ah), so a helm not worn yet shows its 1 too. (An
earlier rule gave boots a move in a fight; it is gone, and the boots' names it
changed go back to the game's.)

## Items saving against acid

([In the features page](FEATURES.md#items-saving-against-acid).)

How: where the game works out the number a weapon's d20 must reach
(`INT D6h`), where it skips the roll for armour with no magical power
(`INT D5h`) and where it works out armour's number (`INT D4h`), the helper
gives the easier of the two and records the check for the dice log.

## Rangers' casting level

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

## Preservers' INT

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

## Spells saved against with the spell save

([In the features page](FEATURES.md#spells-saved-against-with-the-spell-save).)

How: the Loader writes the game's own table that turns a spell's kind of save
into one of the five (a table of words at DS:1E75h, read afresh for every
save), and puts it back when the rule is unticked.

## Fire, cold and electricity: DEX instead of a doubled d20

([In the features
page](FEATURES.md#fire-cold-and-electricity-dex-instead-of-a-doubled-d20).)

How: the helper does the save's doubling (`INT F0h`) only while this rule is
off, and the Loader marks the fire, cold and electricity spells with the game's
own "can be dodged" flag (bit 40h of the spell's category word), which no spell
has, so the game's save routine adds the DEX defensive adjustment from its own
table.

## Enlarge's dice

([In the features page](FEATURES.md#enlarge-multiplies-the-weapons-dice-only).)

The game's Enlarge is 7C211h, called by the attack (58A33h) for a melee hit:
it adds STR's bonus (508:5Ch), then, with the Enlarged flag, multiplies the
lot by 100 + 10 × the levels of the Enlarges on the attacker (598:52h), 32-bit,
rounded down. DSCLOG's `ENL_SITE` replaces that multiplying (7C246h, 32
bytes): with `RULE_HI_ENLARGE` (`game.RULE_ENLARGE`) it takes the hit's dice
from `STAB_ROLL` (58A29h: the roll less what the weapon added, kept for the
backstab rule; `ENL_KNOWN` so they are used once, never a stale hit's),
multiplies only those, rounded up, adds the difference, and makes the kept
dice the enlarged ones, so a backstab with its rule multiplies those. Without
the rule, or with no dice kept, it does the game's sum. The dice log's hit
line does the same (`RULE_ENLARGE`), and the Effects screen's line says DICE
rather than DAMAGE (`EF_CHARGES`, `ef_enlarge_dice`). Checked in DOSBox:
Gerakis Enlarged at level 1 hitting a Screamer Beetle for 21, 22 and 25, its
hit points down by the same (the game's way: 22, 23 and 26).

## Spells roll to hit

([In the features page](FEATURES.md#spells-roll-to-hit).) The Options tab's box
is the settings key `spell_to_hit` (on unless `False`); off, `launch.py` leaves
out `gamepatch.SPELL_TO_HIT`'s two patches and the game's copy has DSUN.EXE's
bytes there.

The routine applying a spell to one target (7A085h, called from the spell's
damage and effect routine 78C19h at 78D38h) makes its immunity checks, then
keeps the spell in `[bp-6]` (7A15Ah) and looks it up in a table of six (7A1A7h:
8, 12h, 35h, 4Bh, 6Fh, B4h): Magic Missile goes to Shield's test, the other
five call a stub at the spell overlay's start (78BA0h, `mov ax,1`), and a 0
there would make the spell do nothing (7A0BEh: the routine answers 1, 78D42h
skips the damage and the effect). The stub is the game's unfinished to-hit test.

- `spell_hit` (7A15Ah, `mov [bp-6],si`): DSCLOG's `SPELL_HIT_SITE` (`th_hit`).
  `CAST_SITE` (772AAh, every cast, 598:89h) arms one roll for its spell and
  target (`th_cast`), unless `ARROW_LEVEL` (58BE6h, a weapon's spell on a hit:
  spell arrows and magical weapons) came just before. The armed cast's spell at
  its target rolls once, unless an Acid burn is under way (`acid_burning`: the
  burn passes Acid Arrow's 12h through the same routine each round). Missile
  spells (`th_missiles`: 18, 53, 75, 111, 180, 33) roll as missiles (to-hit kind 2,
  DEX), touch spells (`th_touches`: 3, 10, 39, 72, 97, 113, 119, 128) as melee
  (kind 1, STR) and only at a creature of another side (creature +1Dh's low 3 bits,
  the side as 809A2h passes it to the cast). THAC0:
  the caster's creature +1Fh (Acid Arrow: 21 less the cast's level, 772A5h's
  `[bp+0Ch]`); less 5B8:EDh (7C3E9h: target, attacker, no weapon, kind; effects,
  STR or DEX) and, for a combatant of 4 or more, `[11AEh]` - 1 (as 5837Ch); the
  AC is 4E0:7Fh (58DD3h: target, attacker, 0), the weapon attack's. The d20 is
  the game's rand() (`blow_rand`); 20 hits, 1 misses. The calls are in a frame
  the overlay manager can fix up (as `NS_BLOW`'s), and the way back never
  changes: a miss sets `th_miss` and writes Acid Arrow's 12h into the game's
  `[bp-6]`, so the dispatch reaches the stub (for the table's missiles the
  same handler; touch spells and Minute Meteors aren't in the table). Minute
  Meteors (33, `TH_METEORS`) adds its own +2 to the adjustments (the frame's
  +0Eh; the dice log names it apart).
- `spell_hit_stub` (78BA3h, the stub's `mov ax,1`): `SPELL_STUB_SITE`
  (`th_stub`): 0 once after a miss, else 1. The stub keeps its `push bp / mov
  bp,sp`, so its own way back stays in the BP chain.
- Each roll is recorded as `KIND_TOHIT` (12): the d20, and a frame of the
  caster, target, spell, THAC0, adjustments, their STR/DEX part, difficulty,
  AC, kind and hit (dicelog's `_spell_to_hit`, which drops the damage rolled
  just before from its recent rolls on a miss and floats "Miss" over the
  target). The rand() call itself matches no filter and isn't recorded.

Tests: test_dsclog's `NewSpellTests.test_spell_to_hit` (the handlers in
Unicorn, the game's routines as stand-ins), test_gamepatch's
`test_spell_to_hit` (the switch off leaves DSUN.EXE's bytes), test_dicelog's
`test_spell_to_hit`.
Checked in DOSBox (playtest/logs/2026-11-08-spell-to-hit.md): Acid Arrow,
Magical Stone (each of its three throws), Condense, Turn Pebble to Boulder,
Chill Touch, Shocking Grasp, Vampiric Touch and Cause Light Wounds hit and
missed as rolled, a miss taking no HP; Magic Missile, a weapon's spell on a hit
and Acid's burn rolled nothing.

## Resting as in AD&D

([In the features page](FEATURES.md#resting-as-in-add).)

The game's rest, 8066Dh(mode [BP+6], hours [BP+8]) (overlay 5E8h; its one caller 62C2Ch, a fire
ring, mode 0; mode 1, a full restore, is the scripts' request 1 elsewhere): "NO RESTING DURING
COMBAT" (the fight's word, 2B8h:19h); pass 1 (806BCh) refills each member's slots (530:93h) and
keeps the best Okay cleric's and druid's levels (5B8:B1h, 5B8:B6h); pass 2 (80758h) takes the
effects' bitset (76944h), casts the free cures (809A2h -> 5B8:20h, 78BA8h, the game's cast: Cure
Disease, Remove Curse, Remove Paralysis from 5th level, Neutralize Poison a druid's from 7th; now
before the bitset: `rest_cures_first`, [the fix](DEVELOPMENT-CONTENT.md#the-games-spells)), takes
Acid off, then for an Okay member HP = the sheet's most (808AFh), PSP = the most (808F3h), STR from
the sheet unless Diseased, and kills the Poisoned (1000 damage, 80963h); then 8 x 3600 seconds on
the clock (5A8:57h).

`RULE_HI_REST` (`game.RULE_REST`, the Loader's `rest_heal`) is DSCLOG's, so both sites are in every
game's copy, each the game's own instruction with the rule off or in mode 1:

- `REST_PRE` (`rest_spells`, 80675h, `mov word [bp-10h],0`: the rest's first move, before any slot
  fills; not 806A0h's far call, whose segment word the overlay manager writes): with the rule, mode 0
  and no fight (`PP_FIGHTING`; the rest's own test comes after), `RP_PASS` in a frame the overlay
  manager can fix up (as `TURN_SITE`'s: the casts load the spells' overlay over the rest's): each
  member's priest level, the better of 5B8:B1h and B6h, for those who can cast (`RP_ABLE`: status Okay
  or New, none of Feeblemind, No spell use, Paralyzed, Charmed); then Neutralize Poison (118) on the
  Poisoned (35), Cure Blindness (94) on the Blind (8), Cure Disease (96) on the Diseased (13) only
  with no cleric or druid of `FREE_CURES` (5th) or more, Cell Adjustment (151) on the Diseased, then
  `RP_WOUNDS`: the member (Okay to Out Cold) with the most hit points missing after the night's
  natural healing (`RP_WORST`), the biggest cure of `RP_CURES` (Cure Light 71, Serious 112,
  Critical 127, Heal 202: for 4, 10, 16 and 30 or more missing) of no more than that someone can cast
  (`RP_CHOOSE`), else the smallest, else Cell Adjustment; at most `RP_MOST_CASTS` (24). A priest
  casts what it knows (the game's known byte, 3800h:0168h + 8Ah a member; Heal by `NS_PRIEST_KNOWS`
  with the new spells on) with a slot of the spell's level left (DS:4B11h + 1Eh a member + the level,
  taken: pass 1 fills them again); a psionicist Cell Adjustment if its power byte (37F0h:0077h + 22h
  a member + 13) has bits 3-7 and it has 5 PSP (taken off: pass 2 fills them again). Each cast is the
  game's 5B8:20h with 809A2h's arguments (target, caster, spell, 0, far &[BP-2], 0, 0, 0, 8, 63h, the
  level, the caster's side), as the free cures: the spells' own dice and kits, the dice log's spell
  lines.
- `REST_HP` (`rest_hp`, 808AFh, `mov [es:bx],ax`: ES:BX the creature, AX the sheet's most): with the
  rule and mode 0, HP + `REST_NATURAL` (3) + CON's hit point bonus (`REST_CON`: the game's table,
  40B1h:0052h + CON, at most 25, as `CON_SHARE` reads it; a warrior's if one of the classes' groups,
  40B1h:0010h + class, is the warriors', else at most +2), at least 1 of healing, no more than the
  most, no less than it had (Extra Hitpoints) nor 1. CON 20 and up regenerates the 8 hours as the
  clock jumps (`REGEN_SITE`, the game's 227E5h, once 300 seconds have passed: after the rest).
- Recorded: `KIND_REST` (`RS_REC`): `RS_CAST` (caster, target, spell, slot level or 0, left: slots or
  PSP; the sixth word 0), `RS_HEAL` (member, before, CON's part, after, most, CON).

Kept: slots and PSP refilled, STR, the free cures, Acid, the poison kill (for one no cure reached),
the 8 hours, mode 1. Not cast: a ranger's priest spells (5B8:B1h and B6h count clerics and druids);
a Dying member isn't healed (pass 2 leaves it). Tests: tests/test_group4.py (`test_rest_spells`,
`test_rest_hp`), test_dicelog's `test_group4_lines`.

## Turn Undead, Minute Meteors and Flame Arrow as the manual

([In the features page](FEATURES.md#spells-and-psionics-as-the-manual-describes-them).) Part
of "Spells and psionics as the manual describes them" (`gamepatch.SPELLS_MANUAL`): off, the
five patches below are left out and the game's copy has DSUN.EXE's bytes.

**Turn Undead** (`turn_undead_manual`, 7AE01h, `mov al,[es:bx+24h]`, 4 bytes:
DSCLOG's `TURN_SITE`, `tu_site`). The game's turning of one undead (7ADB7h:
`[bp+6]` the target, `[bp+8]` the priest, `[bp+0Ch]` the priest level, `[bp-4]`
the undead's sheet number, ES:BX its sheet) works out its number from 7AE01h,
rolls a d20 at 7AE4Dh, destroys at 7AE60h (79A01h, 1000 damage) and calls an
empty routine on a failure (7AE75h). The site never comes back: it sets the
interrupt's way back to one of those three places, or the routine's end
(7AE7Eh), before any far call, then:
- `tu_cell` gives AD&D's cell from the hit dice and level (one run, `tu_cells`
  20 19 16 13 10 7 4 T T D D then D\*, a row starting a column later each:
  dicelog's `turn_cell` is the same);
- a number: a d20 from the game's rand() (`rand_die`, as `th_hit`'s), at or
  over it turned; turned (a number made, or T): 3d4 rounds, and Afraid (17)
  added through 598:3Eh (76442h, the add below 598:39h's immunity check
  5A8:43h, which refuses fear to race 9: 7BE20h), arguments (target, priest,
  190, 17, dword rounds x 60, 0), in a frame the overlay manager can fix up (as
  `NS_BLOW`'s), out through `ovr_back`;
- under the number: the failure's way, and the priest's bit (combatants 0-7) set
  in TU_FAILED (the far block's `FAR_TU`: a byte a target, every combatant up
  to `MAP_COUNT`, 520, since people the Loader adds are numbered past 256; 64
  before 2026-11-09), which a later try by the same priest finds first: the
  routine's end, no roll. `FAR_TU` lies before SWEPT and DJ_DONE (`FAR_SWEPT`,
  `FAR_DJ`, a bit a combatant) and is cleared with them at a fight's first round
  (`acid_round`, DS:55Ah set), and alone by a turning out of a fight (`pp_fighting`);
- D: the destroy; D\*: the destroy, `tu_more` = 2d4 and `tu_kind` the sheet: the
  next undead of that sheet this cast (`th_cast` clears `tu_more`) is destroyed
  with no roll, counting down; "---": the end, no roll.
- Recorded as `KIND_TURN` (13): the d20 (0 none), and a frame of the priest,
  target, cell (0 when not looked up), level, hit dice, outcome (0 not turned,
  1 turned, 2 destroyed, 3 D\*, 4 one of a D\*'s more, 5 refused, 6 no chance),
  rounds and the D\*'s count left (dicelog's `_turn_manual`; `rec_frame`, which
  `th_hit` uses too, pushes such a frame and records it).

The game's d20 at 7AE4Dh is never reached with the switch on, so the old dice
log line (`TURN_ROLL_RETURN`, `_overlay_turn`) is only the switch-off one.

**Minute Meteors** (33): `meteors_count` makes its record's +0 06h 16h (bits
2-7 the casts a cast makes, as Magical Stone's 0Eh is three: five), and
`meteors_damage` its damage +1Ch..1Eh 20 01 04 (1d4 a level) 00 09 04 (1d4).
Each globe is then its own cast (CAST_SITE, so each rolls to hit with Spells roll
to hit) and landing.

**Flame Arrow** (28): `flame_arrow_damage` makes its damage a0 05 06 (5d6 a 5
levels) 00 29 06 (5d6), and `flame_arrow_count` puts DSCLOG's `FLAME_SITE`
(`flame_site`) over `mov dl,[es:bx]` (7567Fh, 3 bytes) in the cast's tail
(7566Eh-756A2h, in 7511Bh: `[bp+0Ah]` the spell, `[bp+0Ch]` the cast's level,
`[bp-10h]` the record, `[bp+16h]` the caller's counter), which compares the
counter with the count less 1 and answers 1 for one more: for spell 28 the byte
is made (level / 5, at least 1) << 2. No attack roll (neither the manual nor
AD&D gives one), no save (the manual's None).

**Who casts again.** Only the party's cast from the USE screen (84621h,
counter DS:942Ch) looks at the answer (another aim, 8463Fh). The other callers
of 598:89h pass a counter of their own and ignore it: a monster's (5A3BAh,
5AA39h, and its wizard spells go through 500:4Dh, not this tail at all), an
item's (6C901h, 6F8A7h), a scroll's (8B954h), a weapon's spell on a hit
(58BF2h), 55CA5h, 88677h and 893E2h. So a monster's Magical Stone, Minute
Meteors or Flame Arrow lands once.

Tests: test_dsclog's `test_turn_undead_manual` (the cells, each outcome and
way, the refusal, D\*'s count, the Afraid call's arguments), `test_flame_arrow_count`,
`test_spell_to_hit` (Minute Meteors' +2); test_dicelog's `test_turn_undead_manual`,
`test_turn_cells`, `test_meteors_to_hit`; test_manual_spells' `test_records`;
test_spellbook's `test_casts_a_cast`.

## Spells and psionics as the manual, group 3

([In the features page](FEATURES.md#spells-and-psionics-as-the-manual-describes-them).)
All in `gamepatch.SPELLS_MANUAL` (off: DSUN.EXE's bytes). DSCLOG's sites are
`BLUR_SITE` ... `CELL_SITE` (`NS_IMAGE` + 78 to 87, in `SITE_TAB`'s order);
code that runs either way tells the switch by `MANUAL_ON` (Stinking Cloud's
record's dice made 41h, as the Loader's `GameData.spells_manual`). The dice
log's lines are `KIND_MANUAL` (14) entries (`MN_REC`: what, then a frame of the
creature and three words; dicelog's `_manual`).

- `save_signed` (79BBDh, `jae` made `jge`): the saving throw (79A71h) compared
  its byte total with the number needed unsigned, so the save modifiers' −100
  (79F80h Chaos, 79FA1h Cloudkill, 7A018h Scare, `SPRAY_SITE`) came out as a
  save (seen in DOSBox). Signed, −100 fails; +100 (Scare from 6th level: 7A01Fh)
  still saves (a d20 + 100 stays under 128; the doubled d20 is only for fire,
  cold and electricity, which get no +100). The one patch here in no switch:
  always applied (a fix of the game's, the user's decision 2026-11-09), so the
  dice log reads −100 as `none allowed (cannot save) -> failed` either way.
- `blur_save` (79DC0h, 11 bytes: Barkskin's test, `blur_save`): Barkskin's +1
  and Blur's (55: the effects' bits at `[bp+0Ah]`, byte 6 bit 7).
- `fire_shield_save` (79E03h, 20 bytes: Protection from Cold's test,
  `fshield_save`): its +3 and Fire Shield's (20) +2 when the spell's damage kinds
  (`[bp-4]`, the record's +1Ah) have fire (2) or cold (4).
- `cloudkill_save` (79F95h, 15 bytes, `cloud_save`): Cloudkill's −100 for a target
  level (`[bp-6]`, `HD_SAVE`'s) under 4, not 6 or less. `cloudkill_kills`
  (78DB6h, `mov [bp-1],al`, the save's answer in 78C19h, `cloud_kill`): unsaved
  by a creature of 5 levels or fewer (`SHEET_LEVEL`), the damage's percent
  (`[bp-6]`, a dword: 100, 50 saved...) made 100000, so the game's own damage
  (78E5Bh, then 79A01h) kills. A first version called 4E0:61h itself (1000, as
  Slay Living's) from the handlers' tail (79830h): it killed, but a kill made at
  a round's start by the lasting cloud hung the game (seen 2026-11-09).
- `lower_resistance_manual` (7A507h-7A527h, 33 bytes, `lowres_site`): the
  resistance (`[bp-0Ch]`) less 30 + the Low Resistance effect's amount (`NS_AMOUNT`,
  its +9) when on (`[bp-7]` 80h), or less 30 + the cast's level (`[bp+0Ah]`) for
  Lower Resistance (64) itself, the bigger; the game's next test makes it 0 at
  least. `ACID_ROUNDS` (always on) puts the cast's level (`TH_LEVEL`,
  `CAST_SITE`'s) into Low Resistance's amount (the game's 0) as the effect is
  added.
- `strength_dice` (79483h, `push dword 60001h`, `strength_dice`): the dice pushed
  under the INT's frame, `STR_SIDES` by class (a byte a class 1-17: Strength's
  sides low, Cat's Grace's high), the best of the sheet's three; 1d6 for
  Adrenalin Control (148), a classless creature or a combatant that isn't one.
  Friends never gets there (`PROBE_GRACE_EFFECT` jumps past it). Not adding up:
  `PROBE_GRACE_ABILITY` (7B7D7h, each of a creature's effects as its abilities
  are worked out) calls `GR_SHADOWED`, which with `MANUAL_ON` finds a bigger one
  of the same group on that creature (66 and 67; 54 alone; as big, the earlier
  entry wins) and puts 0 in `[bp-0Ah]`, which the game's table of cases hasn't.
  A second Strength already replaces the first in the game's add.
- `rainbow_pattern_time` (425B4h, its record's +4/+5: 1d3 made 1 a level) and
  `rainbow_pattern_damage` (585A2h, the start of 4E0:61h, the routine taking hit
  points off for every blow and spell, `rainbow_hurt`): damage over 0 to a
  creature with a Paralyzed (34) entry whose spell (+4) is 50 ends that entry
  through 598:48h (765E2h, the creature and the entry's handle +7: the game's own
  end of an effect, its abilities worked out again), in a frame the overlay
  manager can fix up (`ovr_back`).
- `feeblemind_psionics` (5D5B4h, `or ax,ax / jnz / mov al,0`, `psi_feeble`): in
  the power check (5D59Dh), a user with Feeblemind (19) gets 0 (the check fails:
  the game's message and half the PSP). The INT and WIS of 3 are the game's
  (7B848h, `[bp-4]` set by effect 19, 7B9D8h). Heal's cure: `PROBE_CURE` for
  Heal (202) with `MANUAL_ON` takes the target's Feeblemind entries out
  (`DROP_EFFECT`, `HEAL_SIGHT`'s loop made a routine: Feeblemind has no timer)
  and sets the handler's `[bp-15h]` bit 1, so 79896h works the abilities out
  again.
- `chill_touch_time` (41FD4h, the record's +4..+8: 1 x 3600 seconds): the game's
  own Weakened 1 (79855h, the handler's tail on a failed save) had the spell's
  time, 0. `HOLD_HD` (7A345h, already the switch's) sends Chill Touch (3) on an
  undead to `CHILL_UNDEAD`: immune (7A1F0h: no damage, no STR), Afraid (17) for
  1d4 x 60 through 598:3Eh (as `TURN_SITE`'s), the caster `CAST_WHO`.
- `cell_adjustment_heal` (795A2h, `push 2 / jmp 79618h`, `cell_heal`): AX 1d4
  (`GAME_DIE`) and back at 79617h's `push ax`. The record's effect −13 (F3h) already
  removes Diseased (78E26h, 763E1h's negative effect); `ACID_ONCE` notes whether
  the target had it (`CELL_CURED`) for the line.
- `biofeedback_least` (79C83h, `sub si,2` in the damage adjustments 79BF9h,
  `bio_site`): 2 off, at least 1 of a blow that did any. The game's own −2 (for
  damage of crushing, edged or pointed kinds, `[bp+12h]` & 38h) was there all
  along; a first BIO_SITE in the hit (58AB7h) took 2 more (seen: 4 off).
- Descriptions: `spelltexts.MANUAL_TEXTS` (Fire Shield 45, Cat's Grace 197) go
  into the Loader's copy of RESOURCE.GFF with the switch (`icons.write_resources`'
  `spells_manual`). The Loader's spell info: `spellbook.MANUAL_LINES` and
  `game.MANUAL_EFFECT_RULES` (`game.effect_rule`); the dice log's: `game.manual_die`,
  the save modifiers (`+2 Fire Shield`, `+1 Blur`), Lower Resistance's figure, the
  hit line's `-2 Biofeedback` (the game's, either way).

Tests: tests/test_manual_group3.py (each site in Unicorn at the game's bytes,
the patches, `ACID_ROUNDS`, `ACID_ONCE`, `GR_SHADOWED`, Heal's cure,
`CHILL_UNDEAD`), test_dicelog's `ManualGroup3Tests`. Checked in DOSBox:
playtest/logs/2026-11-09-group-3.md.

## The monsters as the manual describes them

([In the features page](FEATURES.md#spells-and-psionics-as-the-manual-describes-them); the same
switch, `gamepatch.SPELLS_MANUAL`; the research: playtest/logs/2026-11-09-group-4-research.md.)

The monster kinds' table (load segment 3E45h, file 43850h, `gamepatch.KINDS_FILE`: a dword of
properties a kind, its resistance class at +A8h, a class's four masks at +D2h and percents at +DAh,
12 bytes a class; `monsters.MonsterTables` reads the running game's). A creature's kind is its
record's +16h (0 people: no hit powers, 7A6BAh, and no special actions, 5A954h/57BACh).

- Data: `babau_poison` (kind 3: bit 24, the corroding touch 186/187, for bit 15: the last natural
  attack set casts 119, the priests' Poison), `blue_slaad_poison` (17: bit 25, disease, for 15);
  `styr_kind` (38, unused: bit 31, 185 one turn in four, and bit 10; class 11 already), `djinn_kind`
  (39: nothing), `tari_kind` (40: bit 25); `shadow_cold` (class 4's first mask 0139h to 013Dh: cold
  0%) and `greater_shadow_class` (kind 13 class 11, whose 100% rule held the spells' MAGIC bit, to 4).
- `SHADOW_DRAIN` (`shadow_drain`, 7A9ABh in 7A9A7h(target, attacker, bit dword, power), `mov
  si,[bp+8] / mov al,[bp+0Ah]`): for power 172 of kind 15 or 173 of kind 13, 598:3Eh (76442h:
  owner, caster, spell, effect, time dword, amount) adds Weakened (68) of -1 (the ability routine
  adds a Weakened's amount, 7B80Eh: Chill Touch's is -1, 79855h; a 1 raised STR, seen in DOSBox) for
  2d4 x 600 seconds
  with the power as its spell, and 5B8:7Fh (7B758h) works the target's abilities out again; AL made
  8 (no kind's bit) so 5C0:20h says no. 76442h always adds an entry (sorted by owner, a new handle),
  so hits add up; the ability routine takes each Weakened's amount off STR, at least 3. An effect of
  a spell 138 or more is a psionic power's upkeep only for a party caster (76883h), so the power as
  the spell is safe on a monster's.
- `TARI_BITE` (`tari_bite`, 7A747h, `cmp ax,1` after the d10 of 538:89h): a Tari's (`[bp-0Eh]` the
  attacker's creature, kind 40) 1 needs a d2 of 1 too (`GAME_DIE`): 1 in 20.
- `DJINN_TURN`: `PROBE_MOVE`'s end (57566h, the turn's movement: DI the combatant, SI its creature),
  with `MANUAL_ON`: a kind 39's first turn in a fight (`DJ_DONE`, the far block's `FAR_DJ`: a bit a
  combatant, every one up to `MAP_COUNT` (`MAP_BIT`), cleared with
  `SWEPT` and `TU_FAILED` at a fight's first round, `ACID_ROUND`) adds Invisible (23, spell 46, 14
  rounds: 4 + its 10 levels) and Mirror Images (25, spell 19, 1d4 + 3 charges: 76442h's negative
  time) to itself.
- The objects (`monsters.MANUAL_MONSTERS`, by name and race, each field only from the game's value):
  the Styr (99) kind 38, THAC0 11 to 7, level 10 to 14; the Djinn (122) kind 39; the Tari (60, 65,
  243) kind 40, THAC0 18 to 17, level 2 to 3, AC 10 to 6, bite sides (sheet +31h) 2 to 3. An RDFF
  record holds the creature at +0Ah and the sheet at +4Eh (`RDFF_CREATURE`, `RDFF_SHEET`).
  `monsters.object_chunks` for the Loader's copy of SEGOBJEX (`icons.write_objects`, with the switch),
  `monsters.mend` for a running game (the dice log's watches, the switch as `spells_manual` reads it:
  each such creature on the map made one way or the other).
- The Look box (`monsters.defences`' `kind` and `manual`): `MANUAL_SPECIAL` for the drain and the
  Tari's disease, `DJINN_NOTE`, and the breath (bit 31, the Animated Statue's too).
- The dice log: `KIND_MANUAL`'s `MN_DRAIN`, `MN_TARI`, `MN_DJINN`.

Not changed: the shadows' "light damage" (the shadow's own 1d4+1), the greater shadow's numbers (the
manual's already), the Djinn's magic resistance (the manual promises none). Tests:
tests/test_group4.py.

## Weapon specialization

([In the features page](FEATURES.md#weapon-specialization).)

How: the chosen weapon types are kept in four bytes of each character's own
record that the game never uses (+14h to +17h), so saves and the
saved-characters roster keep them. Up to 2.12 they were a byte each (the kind +
1, 0 none); 2.13.0 and 2.13.1 packed them 5 bits each in +14h to +16h,
+16h's top bit (`SPEC_PACKED`) marking it; now (v2, +16h's bit 6 too,
`SPEC_V2`) the dword's bits 0-16 are the four as a base-17 number (each digit
the kind + 1, 0 none: `SPEC_KINDS_MASK`, room for 16 kinds), bits 17-21 the
starting roll (Table 7's dice less their count, 0 to 20; 31, `ROLL_UNKNOWN`,
none kept: `game.sheet_roll`), and +17h is the character's age (`SHEET_AGE`,
years past its race's base starting age, plus 1: see Ages above). A sheet keeps
its layout until something writes to it, and everything reads all three: DSCLOG
through `SPEC_GET` (v2 through `SPEC_UNPACK` into `spec_digits`), `SPEC_FIND`,
`SPEC_ANY` (and writes through `SPEC_SET`, which makes an older sheet v2 first,
`SPEC_PACK`: a 2.12 sheet's +17h, an old 4th spec, becomes 0, no age yet, a
2.13 sheet's age kept; the roll `ROLL_UNKNOWN`; then `SPEC_REPACK`), the Loader
through `game.spec_kinds`, `packed_specs` and `with_specs` (`respecced`, the age
and roll kept). Tests: `test_packing`, `test_rolls`, `test_older_layouts_read`,
`test_with_specs_keeps_the_age`, `test_spec_layouts`. The weapon
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

## Kits

([On the Kits page](KITS.md).)

A kit is chosen for a class: by a character of one class when it is made, and
by a human for each class it changes to (up to three). There are three for
each class, or none (the class as it is). Each gives something and costs
something, as AD&D's kits do. The **Kits** switch on the Options tab
(`game.RULE_KITS`, bit 0 of the helper's second rules word, `RULES_HI` at the
header's +270) switches them all off.

### The kits

What each kit gives and costs is in [the Kits page](KITS.md).
Two kits have tables of their own.

The Seeker's and the Justifier's tables are AD&D's (*The Complete Ranger's
Handbook*), up to 10th level, and the Shinobi has spells of its own (the
game's and four new ones): both in
[the Kits page's spell slots](KITS.md#kits-spell-slots). Their spells are
cast at the table's casting level, not the ranger's or thief's.

Fogbolt, Reflected Image, Spook and Friends, [new
spells](DEVELOPMENT-CONTENT.md#new-spells-wizard-and-6th-level-priest), are known by its bit in the
sheet (`NS_KNOWS`) rather than the game's byte: `SHINOBI_KNOWS` reads either for
the level up's offer (`SHINOBI_UNKNOWN`, `PROBE_PICK_LIST`), and counts them as
known (not offered) while the new spells are off (or, for 199-201, before
`SEG_MOVE`). `SHINOBI_WIZARD` gives the Shinobi's casting level for the new
spells (196-201) as for the game's wizard spells (0-68).

No kit is the kit page's first row, and what a new character has.

### The kit's byte

Sheet `+43h`: zero in every sheet of the saves and saved characters at hand
(176), and nothing in DSUN.EXE reads or writes it (no `es:[bx+43h]` access of
any kind), as with the weapon specs' `+14h` to `+17h`, which saves and the
roster keep. `+45h` is the same, if a second byte is needed (the Arcanist's
CON change used it, once, before that became its d3). 0: no kit; 1 to 3 the
class's kits.

### Choosing one

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

### Multiclass kits

A few pairs of classes taken at once by one race, and one set of three, have
kits of their own (`kitpages.MULTI`): groups numbered on from the classes, 9 elf cleric/fighter,
10 half-elf fighter/thief, 11 half-elf druid/fighter, 12 half-elf
cleric/ranger, 13 dwarf fighter/thief, 14 half-elf fighter/preserver, 15
half-giant fighter/psionicist, 16 halfling fighter/thief, 17 halfling
cleric/psionicist, 18 thri-kreen druid/fighter/psionicist (all three: a
druid/fighter has none), 19 mul druid/fighter. `MULTI_GROUP` (`multi_table`, a
word of class bits a group: `MULTI_FIND` takes in the third class when there is
one) finds a sheet's group from its race and classes;
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

### Where each effect goes

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

| Effect | Kits | Probe |
|---|---|---|
| damage with a weapon | Ravager, Brute, Ghetto Fighter, Battle Dancer and Wilderness Avenger, Arena Champion, Wild Fury | `PROBE_SPEC_DAMAGE`, `PROBE_DAM_LINE`, `PROBE_VIEW_DAM` |
| to hit | Ravager, Brute, Ghetto Fighter, Arena Champion, Battle Dancer, Wilderness Avenger, Wild Fury | `PROBE_ATTACKS` (`KIT_TO_HIT`) |
| AC | Ravager, Wanderer, Sentinel and Arena Champion, Grove Warden, Battle Dancer, Wild Fury | `PROBE_AC` (`KIT_AC`) |
| movement | Stalker, Rescuer | `PROBE_MOVE` |
| spell slots | Scholar, Battle Mage, Crusader, Seeker and Justifier, Elementalist | `PROBE_SLOTS`, `PROBE_SLOT_LEVEL` |
| a power's PSP | Mind Bender, Kineticist, Titan Mind, Wasteland Seer | `PROBE_PSP_USE`, `PROBE_PSP_TABLE`, `PROBE_PSP_DEFENCE` |
| a cure's healing | Healer, Lifebinder, Rescuer | `PROBE_CURE` |
| a spell's damage | Wilderness Avenger | `AV_CAUSE`, `HARM_SITE` |
| healing spells never known | Wilderness Avenger | `PROBE_EL_KNOW` (`AV_KNOW`), `AV_GRANT` |
| casting level | Seeker, Justifier, Shinobi | `PROBE_RANGER_CAST`, `PROBE_CAST_LEVEL`, `PROBE_SPELL_LEVEL` |
| wizard spells for a thief | Shinobi | `PROBE_SLOTS`, `PROBE_PICK_ANY`, `PROBE_PICK_LIST` |
| spells learnt at a level up | Scholar | `PROBE_LV_PICK` |
| a power's PSP to keep it up | Mind Bender, Kineticist, Titan Mind, Wasteland Seer | `PROBE_PSP_KEEP`, `PROBE_PSP_KEEP_DX` |
| the off hand | Healer, Battle Mage | `PROBE_CAN_USE` (`KIT_FORBIDS`) |
| casting though hit | Battle Mage | `PROBE_HIT_ROUND` |
| two spells in a turn | Arcanist | `PROBE_CAST_MARK`, `PROBE_CAST_DONE`, `PROBE_END_TURN` |
| THAC0 | Swashbuckler, Crusader, Battle Mage, Mind Warrior, Scholar | `PROBE_THAC0` |
| initiative | Sentinel, Military Scout, Myrmidon | `PROBE_INIT` |
| to hit with a missile | Military Scout | `PROBE_ATTACKS` (`KIT_TO_HIT`) |
| a hit's poison | Poisoner | `PROBE_POISON` |
| an arrow's plus | Spellarcher | `PROBE_ARROW` |
| a priest spell's level | Spirit Caller, Wasteland Seer | `PROBE_SPELL_LEVEL` |
| saves | Myrmidon, Sentinel, Wanderer | `PROBE_RING_SAVE` |
| a spell's damage | Wanderer | `WANDER_DMG` |
| thief skills | Assassin, Swashbuckler, Shadowblade, Ghetto Fighter, Wayfinder, Military Scout | `PROBE_BELT` |
| from behind, backstab | Military Scout, Rescuer, Assassin | `PROBE_STEALTH` (`KIT_REAR`) |
| initiative, Move in a fight | Wayfinder | `PROBE_INIT`, `KIT_MOVE` |
| shields | Shadowblade, Ghetto Fighter, Rescuer | `KIT_FORBIDS` |
| light armour only | Assassin, Shinobi, Shadowblade, Poisoner, Spellarcher | `KIT_LIGHT` |
| hiding, moving silently | Stalker, Assassin and Military Scout, Wilderness Avenger, Shadowblade | `stealth.py` |
| the two-weapon penalty | Twin-blade, Battle Dancer, Justifier, Ghetto Fighter | `PROBE_TWO`, `RG_TWO` |
| gear allowed | Ravager, Twin-blade, Brute, Stalker, Grove Warden, Lifebinder, Shinobi, Battle Dancer, Shadowblade, Ghetto Fighter and Rescuer, Seeker | `PROBE_CAN_USE`, `KINDS_ALLOWED` |
| skill with a weapon | Justifier | `SPEC_OF_SHEET` |
| weapon specs | Myrmidon, Brute, Battle Mage, Spellarcher, Poisoner, Crusader and Mind Warrior | `SPEC_OF_SHEET`, `KINDS_ALLOWED`, `LV_DUE` |
| attacks a round | Wild Fury, Battle Mage, Crusader and Mind Warrior | `EXPERT_HALVES`, `WAR_KIT_HALVES` |
| gear the kit allows | Battle Mage, Battle Dancer | `PROBE_CAN_USE` (`KIT_ALLOWS`) |
| hit die | Battle Mage, Arcanist | `PROBE_HIT_DIE`, `PROBE_CR_DIE` |
| max PSP | Mind Warrior | `PROBE_MAX_PSP`, `PROBE_CR_PSP` |

How each is done:

- **Damage with a weapon.** Ravager, Brute, Ghetto Fighter (melee: `KIT_MELEE`, by the item type;
  the Ghetto Fighter's a dagger's kind), Battle Dancer and Wilderness Avenger (melee or missile:
  `KIT_EXTRA`, the dance's `KIT_DANCE` byte, or the Avenger's 1 against anything), Arena Champion
  (melee, a shield in a hand: `KIT_CHAMPION`, by `PROT_SCAN` of the attacker's thing, `[BP+18h]`),
  Wild Fury (Wild Fighting passed: +3, melee or missile, `WILD_PASSED`). Where: `PROBE_SPEC_DAMAGE`
  (`KIT_ATTACK_DAMAGE`), and the DAM lines (`PROBE_DAM_LINE`, `PROBE_VIEW_DAM`: `KIT_MELEE` only).
- **To hit.** Ravager, Brute, Ghetto Fighter (and 1 worse with anything but a dagger), Arena
  Champion, Battle Dancer, Wilderness Avenger, Wild Fury (Wild Fighting failed: −3, `WILD_TO_HIT` by
  `KIT_WILD`). Where: `PROBE_ATTACKS` (`KIT_TO_HIT`: `KIT_CHAMPION`, `KIT_EXTRA`, and `KIT_MELEE` in
  melee).
- **AC.** Ravager (`RAVAGER_AC` by level against the sheet's base AC, `+27h`), Wanderer, Sentinel
  and Arena Champion (a shield in a hand: `PROT_SCAN`), Grove Warden, Battle Dancer (its dance:
  `KIT_DANCE`), Wild Fury (Wild Fighting failed: 3 worse, no worse than 10, `KIT_WILD`). Where:
  `PROBE_AC` (`INT 62h`, the end of the AC routine: `KIT_AC`).
- **Movement.** Stalker, Rescuer (2 more). Where: `PROBE_MOVE` (`KIT_MOVE`).
- **Spell slots.** Scholar (+1 wizard), Battle Mage (−1 wizard), Crusader (−1 priest), Seeker and
  Justifier (their priest tables, `SEEKER_SLOTS`, by ranger level, in place of the game's),
  Elementalist (a level behind, `PROBE_SLOT_LEVEL`; but at least 1 at a spell level its own cleric
  level reaches, 2 × the spell level − 1, `PROBE_SLOTS`). Where: `PROBE_SLOTS` (`INT B6h`, new: the
  end of the game's slot routine, `mov ax,[bp-2]` at DSUN.EXE 5E255h) and `PROBE_SLOT_LEVEL` (`INT
  B5h`, new: where it takes a class's level, `mov al,es:[bx+24h]` at 5E1F6h);
  `GameData.max_spell_slots` with `kits.slots` and `kits.slot_level`.
- **A power's PSP.** Mind Bender, Kineticist, Titan Mind (psychometabolism 2 less, telepathy 2
  more), Wasteland Seer (every power 2 less under the open sky, 1 more under a roof: a party
  member's `KIT_OUTDOORS` bit; `PSI_KIT` gives `KIT_SEER_ROOF` for the roof) (by discipline: powers
  0-5 psychokinesis, 6-19 psychometabolism, 20-33 telepathy, the defence modes among them; never
  below 1). Where: the powers' table (8 bytes a power, at the load segment + 3FB9h: `+1` the cost to
  use, `+2` to keep up, 63h for none; `+5` FEh for a defence mode). `PROBE_PSP_USE` (`INT B4h`, new:
  where the routine using a power has its cost in DI, its table's or worked out for Enhanced
  Strength and Domination, DSUN.EXE 5CBE7h), `PROBE_PSP_TABLE` (`INT B3h`, new: the table's cost
  read in the check whether a power can be used, 5CAA3h, and for the half a failed power costs,
  5CCA2h), `PROBE_PSP_DEFENCE` (`INT B2h`, new: a defence mode's cost taken off, 5D820h);
  `kits.psp_cost`. Monsters' powers (5A773h) are left alone.
- **A cure's healing.** Healer (+1 a die of Cure Light, Serious, Critical Wounds: spells 71, 112,
  127), Lifebinder (a die more: a d8, Blood Flow's, 108, a d6, rolled from the game's rand() seed by
  `GAME_DIE`), Rescuer (as the Healer). Where: `PROBE_CURE` (`INT B1h`, new: "nop / push cs" at
  DSUN.EXE 79619h in the handler for spells with rules of their own, where the healing, pushed with
  the target, goes to the routine that heals; the caster its `[BP+8]`, the spell `[BP+0Eh]`; the
  probe pushes CS itself). The Cell Adjustment's jump into 79618h is clear of it.
- **A spell's damage.** Wilderness Avenger (+1 a die of Cause Light, Serious, Critical Wounds:
  spells 72, 113, 128). Where: `AV_CAUSE`, from `AREA_DMG` (754ECh, "mov [bp-12h],ax" where the
  routine dealing a spell's damage to the creatures it reaches, 7511Bh, the Cause spells' way too,
  has rolled it, DI the spell; a helpless target's at `[BP-14h]`) and `HARM_SITE` (761A9h, the
  one-target routine's, `[BP-8]`): when `CAST_SITE` last saw that spell cast by an Avenger
  (`CAST_WHO`, `CAST_SPELL`), the bonus on the damage and on a helpless target's; the dice log's
  `_harm_bonus`, by the last `KIND_CAST`.
- **Healing spells never known.** Wilderness Avenger (Cure Light, Serious, Critical Wounds, Blood
  Flow; Heal and Water of Life). Where: `AV_HEAL`'s list in `PROBE_EL_KNOW` (`AV_KNOW`: as a
  character is made, the spell its place in the table / 7; a level up marks none) and `AV_GRANT`
  (5E499h, "test es:[bx+19Dh],edx" in the routine giving a priest its spheres' spells, 5E401h, no
  caller found: guarded as `PROBE_EL_GRANT` guards it; a site of `INT 98h`: ZF set for them, so they
  aren't learnt); the 6th-level two in `NS_PRIEST_KNOWS` (no mask for an Avenger). One made with
  2.10.0 or earlier, with them known: `kits.avenger_heals` marks them not known when the save is
  loaded.
- **Casting level.** Seeker (the ranger level less 5), Justifier (less 9), Shinobi (for its wizard
  spells, the thief level less 5). Where: the game works it out in two places, both with the
  combatant and the spell as arguments. The caster level routine, 81B16h, counts a ranger's level 7
  less: `PROBE_RANGER_CAST` (`INT AFh`, new: that "sub dx,7", 81B6Ah) makes it the kits' 5 and 9,
  and `PROBE_CAST_LEVEL` (`INT ACh`, new: its end, `mov ax,[bp-2]`, 81C06h) gives a Shinobi its
  level for a wizard spell. That routine sets the spell levels a caster may cast, half the caster
  level rounded up (81664h, which asks for spell 0: the USE screen's lists and slots), and weighs a
  spell against Dispel Magic. The level a spell's duration and damage take is another routine's,
  5E25Ch (the best level of the caster's classes that cast it, a ranger's whole; the cast passes it
  down to the duration, 76CB3h, and the damage dice, 76DA2h): `PROBE_SPELL_LEVEL` (`INT A8h`, new:
  its end, `mov ax,di`, 5E3D1h) gives the Shinobi its own; `PROBE_RANGER_LEVEL` (`INT A6h`, new:
  `mov al,es:[bx+24h]`, 5E3B8h, where it takes each class's level) takes the Seeker's 5 and the
  Justifier's 9 off its ranger level (and a plain ranger's 7, with the [rangers' casting
  level](#rangers-casting-level) rule). `kits.ranger_cast_drop`, `kits.cast_level`,
  `kits.spell_class_level`, and `GameData.effect_caster_level`.
- **Wizard spells for a thief.** Shinobi. Where: slots: `PROBE_SLOTS` gives a Shinobi's wizard slots
  the Seeker's table by its thief level (`kits.slots`). Its spells known are the party's table of
  them (at the load segment + 3800h, from 168h: 8Ah bytes a member, a byte a spell, not 0 if known),
  and the USE screen lists and casts them as any preserver's. Learning: a level up as a thief from
  6th goes on as a preserver's would (`PROBE_LV_PICK`'s `LV_SHINOBI`) to the routine that offers a
  preserver its spell (620:5Ch, 85560h), which takes the preserver level and goes on only for one,
  and then only if the game's list (500:2Ah) has a spell to learn: `PROBE_PICK_ANY` (`INT A7h`, new:
  `mov [bp-2],ax / or ax,ax`, 85580h) opens CHOOSE A SPELL (85771h) for a Shinobi with one of its
  spells unknown up to the level it casts. There `PROBE_PICK_LEVEL` (`INT ABh`, new: `inc al`,
  85861h, the preserver level the highest spell level on offer is half of) gives it its casting
  level, and `PROBE_PICK_LIST` (`INT AAh`, new: `mov di,ax`, 8563Fh, after the game fills the list,
  at the segment of the `mov ax,348h` before it, `+7`, a word a spell; the character at its `+25Bh`;
  the highest spell level `DS:[4AECh]`) puts its own unknown spells in the list (`kits.pick_list`).
  A scroll: see [Preservers' INT](#preservers-int). Armour: the game has no armour rule for a single
  class's spells (the multiclass preserver's is the class restrictions'), so it casts in the light
  armour it may wear.
- **Spells learnt at a level up.** Scholar (one more). Where: `PROBE_LV_PICK`'s `LV_SCHOLAR`: at a
  preserver's level up, the routine offering its spell (620:5Ch, its far call read from the code
  after the probe) called once before the game's own.
- **A power's PSP to keep it up.** Mind Bender, Kineticist, Titan Mind, Wasteland Seer (as the cost
  to use it; 63h, none, left alone). Where: `PROBE_PSP_KEEP` (`INT B0h`, new: the table's `+2` read
  where the round's cost is taken, 5CE49h, the combatant in SI) and `PROBE_PSP_KEEP_DX` (`INT AEh`,
  new: the check whether a power can be kept up, 5CB02h, the combatant in DX). The monsters' cost
  lookups (5D4DAh, 5D4EFh) are left alone.
- **The off hand.** Healer (no weapon), Battle Mage (nothing). Where: `PROBE_CAN_USE`'s
  `KIT_FORBIDS` with `KF_OFF_HAND`: the can-use routine's only caller is the equip routine (6EF52h),
  whose `[BP+8]` is the slot (the item's slot + 4: 7 the right hand, 14 the left, the off hand; 18
  on the backpack), read through the can-use routine's saved BP.
- **Casting though hit.** Battle Mage. Where: a hit's damage marks its creature hit this round (`mov
  byte es:[si+0AFh],1`, 58733h, in the routine taking damage off; cleared at a round's start,
  57621h), and a marked character can't choose a spell on the USE screen (892F3h, 55898h) and has a
  queued one dropped (8991Bh): `PROBE_HIT_ROUND` (`INT ADh`, new) doesn't mark a Battle Mage.
- **Two spells in a turn.** Arcanist (preserver spells, in a fight). Where: a spell aimed on the map
  ends the caster's turn in two ways: the routine casting it marks the caster as a hit does (845F0h;
  so no spell is offered again), and the routine finishing any use of what the USE screen armed
  (720F4h: it takes the slot or the item's charge; `DS:[54FBh]` the kind, 0 a wizard spell from a
  slot, `[54FCh]` the party member) asks the fight's routine that sets a combatant's actions
  (59256h) for none, as do the routines that cast, from their own code segments. A spell on a party
  member from the USE screen does neither (the game's own: the turn goes on). `PROBE_CAST_MARK`
  (`INT 96h`, new) doesn't mark an Arcanist for its first preserver spell of the turn;
  `PROBE_CAST_DONE` (`INT 94h`, new: the finishing routine's `cmp word es:[19h],0`, 722AFh) counts
  its preserver spells (`ARC_CASTS`) and sets `ARC_HOLD` for the first; `PROBE_END_TURN` (`INT 93h`,
  new: `mov si,[bp+8]`, 5925Dh) then returns at once when ending that member's turn is asked from
  another code segment (the fight's own routines, a turn ended from the combat menu among them, ask
  from its own), till the map's main loop runs again (`PROBE_SCROLL`) or a turn starts;
  `PROBE_ROUND_MARK` (`INT 95h`, new: the turn's start clearing the mark, 57621h) clears the count.
  Checked in the game: two Magic Missiles in a turn, the second marking it and ending the turn;
  ended from the combat menu after one.
- **THAC0.** Swashbuckler, Crusader, Battle Mage, Mind Warrior (a warrior's: 21 less the level,
  where better), Scholar (1 worse). Where: `PROBE_THAC0` (`INT B7h`, new: the end of the game's
  THAC0 routine, `mov ax,14h / sub ax,si` at DSUN.EXE 876BBh, which every write of a creature's
  THAC0, `+1Fh`, uses: on making a character, 66CE0h, and at a level up, 86D7Eh and 87A91h).
- **Initiative.** Sentinel; Military Scout (its `KIT_OUTDOORS` bit); Myrmidon (2 less). Where:
  `PROBE_INIT` (`INT B8h`, new: the round's 20 added at DSUN.EXE 5750Eh).
- **To hit with a missile.** Military Scout (a bow, sling or staff sling, its `KIT_OUTDOORS` bit).
  Where: `KIT_TO_HIT` in `PROBE_ATTACKS` (`kits.missile_to_hit`).
- **A hit's poison.** Poisoner (every melee weapon hit; the header's +360, `KIT_SHOT`, once a fight
  up to 2.10.0, now bit N party member N's last weapon attack a shot or a throw: set or cleared by
  `NOTE_SHOT` in `PROBE_ATTACKS`, from the weapon attack routine's `[BP+16h]`, above 1 for a
  missile). Where: `PROBE_POISON` (`INT 86h`, new: the `jmp 7A7C5h` at DSUN.EXE 7A6DDh, in the
  routine giving a hit's special effects, 7A539h, where a person who isn't a thri-kreen has none; DI
  the attacker, SI the target, `[BP-6]` the attacker's creature, `[BP+12h]` the spell or power
  behind the damage, -1 for a weapon's): for a melee weapon hit only (`KIT_SHOT`'s bit clear; the
  poison's own damage, power 176, comes back through this routine with the Poisoner as its attacker,
  and would poison again, hit after hit) it queues power 176, the monsters' "poison (10 damage)",
  through the routine a monster's poisoned hit uses (790D2h: target, attacker, power, level; the
  level from 508:2Ah, whose far call is at 7A7ACh), then jumps on. The game rolls the save
  (paralysis/poison/death) and deals the damage.
- **An arrow's plus.** Spellarcher (1 better, at least +1, from a bow). Where: `PROBE_ARROW` (`INT
  85h`, new: `mov es:[0006h],al`, DSUN.EXE 58D27h, in the routine finding a missile weapon's
  ammunition, 58C8Fh, `[BP+0Ch]` the weapon's type): `ES:[6]` is the plus the shot's damage adds
  (58992h) and its +1/+2/+3 damage kinds take where better than the bow's (581C4h). The shooter is
  `WHOSE_TURN`'s combatant; `kits.arrow_plus`. The weapon spec: `KINDS_ALLOWED` gives a Spellarcher
  the bow only, the one weapon spec the window after DONE offers it.
- **A priest spell's level.** Spirit Caller, Wasteland Seer (2 more under the open sky, 1 less under
  a roof, no less than 1). Where: `PROBE_SPELL_LEVEL`'s `SKY_LEVEL` (`kits.sky_level`): the level a
  spell's duration and damage take, not the levels it may cast.
- **Saves.** Myrmidon (charms), Sentinel (spells, 0-137), Wanderer (fire and cold: the spell
  record's `+1Ah`, 2 or 4, as the game's Resist Fire and Resist Cold read it). Where:
  `PROBE_RING_SAVE` (the modifier routine's start: `KIT_SAVE`).
- **A spell's damage.** Wanderer (half of a spell all fire or all cold, as Resist Fire and Resist
  Cold). Where: `WANDER_DMG` (an `NS_IMAGE` site: "test [bp+0Ch],di" at DSUN.EXE 7B56Fh, in the
  routine giving the share of a spell's damage a creature takes, 7B492h, where DI holds the kinds
  its effects guard it from; fire and cold added for a Wanderer); `GameData.damage_halved_by`.
- **Thief skills.** Assassin (pick pockets, open locks), Swashbuckler (all), Shadowblade, Ghetto
  Fighter, Wayfinder (`KIT_SKILLS`, a signed byte a skill), Military Scout (+10 or −5 by its
  `KIT_OUTDOORS` bit). Where: `PROBE_BELT` (the thief skill routine's end: `KIT_SKILL`, no lower
  than 0).
- **From behind, backstab.** Military Scout (a backstab taken back: `[BP-24h]` cleared, its 2 to hit
  with it), Rescuer (from behind +1, not +2); Assassin (a backstab's multiplier one more, x3 to x6:
  `STAB_TIMES`, `kits.backstab_times`). Where: `PROBE_STEALTH`'s `KIT_REAR` (`kits.backstabs`,
  `kits.rear_to_hit`), after the game's own setting of `[BP-1Ah]` and `[BP-24h]` and the stealth
  rule's; the backstab flag is pushed for the attack after it (DSUN.EXE 5838Ah).
- **Initiative, Move in a fight.** Wayfinder (Path-finder: each party member 1 more while a
  Wayfinder of the party is New or Okay, `PATH_UP`; 1 less while one is down and none up,
  `PATH_DOWN`). Where: `PROBE_INIT`, `KIT_MOVE`; `GameData.path_finder`, `GameData.path_lost`.
- **Shields.** Shadowblade, Ghetto Fighter, Rescuer. Where: `KIT_FORBIDS` (`kits.forbids`).
- **Light armour only.** Assassin, Shinobi, Shadowblade, Poisoner, Spellarcher (asleep too). Where:
  `KIT_LIGHT` (`kits.LIGHT_KITS`).
- **Hiding, moving silently.** Stalker, Assassin and Military Scout (not halved in daylight:
  `kits.not_halved_by_sun`), Wilderness Avenger (a ranger's, 5 a level of its best class),
  Shadowblade (hides with an enemy beside it). Where: the stealth rule's rolls (`stealth.py`,
  `GameData.ranger_skill_parts`).
- **The two-weapon penalty.** Twin-blade, Battle Dancer (in light armour: `HEAVY_WORN`); Justifier
  (in any armour); Ghetto Fighter (2 less in each hand). Where: `PROBE_TWO`; `RG_TWO`.
- **Gear allowed.** Ravager, Twin-blade, Brute, Stalker, Grove Warden, Lifebinder, Shinobi, Battle
  Dancer (no shield; `kit_dancer`: long sword and bow kinds), Shadowblade, Ghetto Fighter and
  Rescuer (no shield), Seeker (its sphere's weapons, as a cleric's: `SPHERE_ALLOWS` with `CU_*` set
  from the item type, its sphere the ranger class less 13; the bow kept). Where: `PROBE_CAN_USE` and
  `KINDS_ALLOWED` (`KIT_FORBIDS`: `restrict.kit_forbids`; and `KIT_ALLOWS`, so a Battle Dancer may
  specialize in the long sword whatever its cleric's sphere), whatever the class restrictions. For
  an EXIT on the weapon window after DONE, `weaponchoice.kinds_for` makes a Ghetto Fighter's or
  Poisoner's spec the dagger and a Battle Dancer's the long sword, if allowed (`kits.default_kind`);
  `weaponchoice._ghetto_dagger` puts a dagger in a Ghetto Fighter's hand.
- **Skill with a weapon.** Justifier (expertise, the bow's and its chosen weapon type's, becomes
  specialization). Where: `SPEC_OF_SHEET`'s end: `SPEC_EXPERT` made `SPEC_SPECIAL` for a Justifier;
  `specialize.skill`.
- **Weapon specs.** Myrmidon (two, the second to grand mastery), Brute (no missile spec), Battle
  Mage (one, of `KIT_BM_KINDS`: expertise), Spellarcher (the bow only), Poisoner (the dagger or
  short sword only: `KIT_POISON_KINDS`), Crusader and Mind Warrior (one, of its class's melee kinds:
  `KIT_MELEE_KINDS`; a thri-kreen Mind Warrior the chatkcha too, `KIT_KREEN_KINDS`, the race byte
  +18h, `kits.KREEN_WARRIOR_KINDS`). Where: `SPEC_OF_SHEET` (a Battle Mage's chosen weapon type
  `SPEC_EXPERT`), `KIT_FORBIDS`, `KINDS_ALLOWED` (a Battle Mage its own weapon types, whatever its
  class), `LV_DUE` (a Battle Mage one, a Myrmidon being made two), so DONE's weapon window
  (`CR_WEAPONS`) asks a Battle Mage as it asks a warrior.
- **Attacks a round.** Wild Fury (Wild Fighting passed: 1 more in melee, `WILD_HALVES`, in
  `PROBE_ATTACKS` before the off hand's cap; not on the DAM lines); Battle Mage (its chosen weapon
  type: expertise, 3/2, 2 from 7th preserver level); Crusader and Mind Warrior (a warrior's extra
  attacks in melee, 3/2 from 7th level of the kit's class (2 from 13th, past the level cap), weapon
  specialization on or off). Where: `EXPERT_HALVES` where `PROBE_ATTACKS`, `PROBE_DAM_LINE` and
  `PROBE_VIEW_DAM` leave a non-warrior's (2 halves or fewer) alone; `specialize.expert_attacks`.
  `WAR_KIT_HALVES` in the same three probes, after the rest (`WAR_KIT_OF` in `PROBE_ATTACKS`, not
  for a missile: `[BP+16h]` above 1, or in View Character a type's `+0` bit 2);
  `kits.warrior_attacks`, which `GameData.weapon_hits` gives the party view. Checked in the game:
  the DAM lines 1.5× for a 7th-level Crusader and Mind Warrior, 2× at 13th, 1× at 6th and for a Mind
  Bender; in a fight a 7th-level Crusader with a club in each hand attacked 1+1 and 2+2 in turn
  before the off hand's cap (see [Two weapons](#two-weapons)).
- **Gear the kit allows.** Battle Mage (its chosen weapon type's weapons, with weapon
  specialization; light armour); Battle Dancer (long swords and bows, `kit_dancer`, whatever its
  cleric's sphere). Where: `KIT_ALLOWS` in `PROBE_CAN_USE`: an item the game's class mask refuses is
  let through (AX 1), and the class restrictions pass it; `KIT_FORBIDS` still holds (nothing in a
  Battle Mage's off hand). `kits.allows`, `restrict.kit_allows`. The game has no armour rule for a
  single class's spells, so it casts in that armour.
- **Hit die.** Battle Mage (d6), Arcanist (d3). Where: a level's die: `PROBE_HIT_DIE` (`INT A5h`,
  new: `mov al,es:[bx+0]`, 87308h, the die read from the class's hit point group in the routine
  rolling a level's hit points, 87250h, which both a level up and the creation screen call; `[BP-4]`
  the sheet). The creation screen's range (the least and most hit points it allows, `DS:[4998h]` and
  `[4996h]`, worked out with the rolls by 655D6h): `PROBE_CR_DIE` (`INT A3h`, new: `mov
  al,es:[bx+14Ah]`, 65677h, the die from its table by creation class). `kits.hit_die`.
- **Max PSP.** Mind Warrior (a tenth fewer, rounded down). Where: at a level up: `PROBE_MAX_PSP`
  (`INT A4h`, new: `les bx,[bp-8]`, 8748Fh, the sum in SI before it goes in the sheet, in the
  routine at 873B2h, which the level-up check runs for every party member, and a game's start too;
  first `PSP_SCORES` puts the game's CON, INT and WIS bonuses right: WIS read through `DS:11A0h`,
  the creation screen's record (any byte that memory holds: 183 in one test), taken signed as the game takes it, and tables 8 scores long in the
  overlay's segment, which its `mov dx,seg` at 873F8h holds, read past their ends); on the creation
  screen: `PROBE_CR_PSP` (`INT A2h`, new: the end, `pop bp / retf`, of 65B39h, which sums the PSP
  into the sheet being made's `+0Ch`; it drops the interrupt frame to end the routine itself,
  putting the flags back first, as a score's click reaches it with nothing after to set IF again).
  `kits.max_psp`.

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

| Effect | Kits | Probe |
|---|---|---|
| priest spells known | Elementalist, Healer | `PROBE_EL_KNOW`, `PROBE_EL_GRANT` |
| a kit asleep after dual-classing | every kit | `KIT_PLACE`, `KIT_AT`, `KIT_AWAKE` |
| classes barred to a dual-classing human | Seeker, Justifier, Shinobi, Swashbuckler, Crusader, Battle Mage, Mind Warrior, Arena Champion, Sentinel, Brute, Stalker, Grove Warden, Healer | `PROBE_DUAL_BAN`, `DUAL_SPHERES`, `PROBE_SPHERE` |
| a new preserver's spells, on changing class | every human | `PROBE_DUAL_SPELLS`, `PROBE_PICK_LEVEL` |
| a new preserver's spells, at creation | every preserver | `PROBE_CR_SPELLS`, `PICK_SPELLS`, `PICK_FILL` |
| sound numbers on the sheet | every character | `PROBE_SOUND_42`, `PROBE_SOUND_44` |
| a kit for a dual-classing human's new class | every kit | `PROBE_DUAL_KIT` |
| starting gear fitted to the kit | Ravager, Brute, Shinobi, Seeker, Shadowblade, Ghetto Fighter, Rescuer, Arena Champion, Poisoner, Battle Mage, Battle Dancer, Myrmidon | `weaponchoice.kit_gear` |
| caster level, a spell's level | Elementalist, Healer | `PROBE_EL_CAST`, `PROBE_EL_LEVEL` |
| weapons | Elementalist | `CLASS_FORBIDS`, `KINDS_ALLOWED` |
| choosing it | Elementalist, Healer | `EL_CLICK`, `PROBE_WP_CLASS`, `KIT_ROW` |

How each of these is done:

- **Priest spells known.** Elementalist (its second sphere's too), Healer (the cosmos's: the spells
  every druid has, by its element's druid's bit, `HEALER_COSMOS`; a Healer from 2.5.0 or earlier has
  them marked by the Loader, `kits.cosmos_spells`, the low four bits of its byte in the known table
  at `DS:132Ah` set to 1 as the game's loop does). Where: the loops that mark each priest spell
  (45h-89h) known or not for a party member by the class's bit, on making a character (66F89h) and
  when a human changes class (86E1Eh, in the DUAL routine at 86C80h; a level up marks none, as a
  priest knows its spheres' spells of every level from the start): `PROBE_EL_KNOW` (`INT 9Eh`, new:
  `test dword es:[bx+19Dh],eax`, 66FC9h and 86E56h; its flags back to the JZ with `RETF 2`) adds the
  second sphere's cleric bit, and for a Healer whose cleric's bit it is, its element's druid's (2 <<
  (class + 4)): a water druid's spells are a water cleric's and the cosmos's. And the routine giving
  a priest its spheres' spells (5E401h, no caller found): `PROBE_EL_GRANT` (`INT A1h`, new: `xor
  si,si`, 5E489h) adds them to its mask.
- **A kit asleep after dual-classing.** Every kit. Where: the routine that changes a human's class
  (86C80h, DUAL on a portrait's menu: 70EF1h opens its window, 86B3Fh, for a human of 2nd level or
  more, 3rd with `RULE_HI_DUAL`) moves the classes down and puts the new one first. The kit byte (`+43h`) has two bits for
  each class (0 none, 1-3), the first class's lowest and each class taken after it the next two, so
  a kit stays with its class however the classes move: `KIT_PLACE` gives the oldest class's place (0
  for one class; 1 or 2 for a human; 0 for a multiclass group's, none for another multiclass),
  `KIT_AT` the kit of the class at a place, `KIT_AWAKE` holds a kit asleep until the level at `+24h`
  passes its class's (as the game counts earlier classes; the class it has now is always awake).
  `KIT_IS` finds a kit only while awake and `KIT_HAS` either way. The byte's 0FFh (`KIT_OPEN`, on
  the creation panel) is no kit. The kit's own levels come from `KIT_LEVEL` (Ravager and Grove
  Warden AC, the warrior THAC0, the Seeker's and Justifier's slots, the Shinobi's casting and spell
  picks, the Battle Mage's 7th-level expertise) and its class from `KIT_CLASS_OF_SHEET` (a Seeker's
  sphere, an Elementalist's cleric); `PROBE_SLOT_LEVEL` puts an Elementalist's slots behind for its
  own class's place only (`KIT_AT` there). `PROBE_HIT_DIE` gives a kit's die only for one class (a
  human who changed class rolls for its new one); `PROBE_MAX_PSP` takes a Mind Warrior's tenth with
  `KIT_HAS`, as a sleeping psionicist class still gives its PSP. `SPEC_OF_SHEET` treats a
  dual-classed Battle Mage's weapon spec as the kit's (none asleep, expertise awake), not a new
  warrior class's. The Effects screen has a `KIT:` line for each kit, the oldest class's first, `
  (ASLEEP)` after one asleep (`KIT_AT`, `KIT_OF_SHEET` with `KIT_SHORT`'s shorter names,
  `KIT_LINE_ASLEEP`, `KIT_AWAKE`); see the next section for its pages. `kitpages.kit_place`,
  `kit_at`, `kit_awake`, `kits_of`, `kit_ids`, `kit_level`, `kit_class_of` are the Loader's.
- **Classes barred to a dual-classing human.** Seeker, Justifier (cleric); Shinobi (preserver);
  Swashbuckler, Crusader, Battle Mage, Mind Warrior (fighter, gladiator, ranger); Arena Champion,
  Sentinel (druid, preserver: no shield); Brute (psionicist, air cleric: no two-handed melee
  weapon); Stalker (thief: its hiding on a thief's own); Grove Warden (gladiator: its AC on a
  gladiator's own); Healer (the rangers of air, earth and fire: water's sphere only; the game
  already keeps a priest from the other priest class, and a ranger, who must be good, from the
  druid, who must be neutral, so `DUAL_BANS`' clerics and druids there and the Seeker's and
  Justifier's druids never come up). Where: the DUAL window (866C7h) asks of each class (SI, 1-17)
  whether member [BP+6] may change to it (86E94h: AX 1 if so; human, prime requisites) and greys the
  rows answered no (a row with elements, cleric, druid or ranger, stays open while any of its four
  classes is allowed; the element is then picked on the game's three-choice menu, 86BBBh: its title
  the air row, DS:30A5h, then earth, fire and water, AX 0 to 3 added to the row's first class. For a
  Healer `DUAL_SPHERES`, called by `PROBE_DUAL_BAN`, makes that menu WATER ONLY, no other row, and
  `PROBE_SPHERE`, `INT FFh` over the `cmp ax,1` after it, 86BC3h, makes its answer water; checked in
  the game: a water-cleric Healer to ranger, a water ranger; a fire ranger to water cleric, no
  Healer on the KIT menu): `PROBE_DUAL_BAN` (`INT 9Dh`, new: the `or ax,ax` after the call, 866FFh;
  its flags back to the JZ with `RETF 2`) answers no for a class one of its kits bars (each
  `KIT_AT`, asleep too; `KIT_BANS`), from `DUAL_BANS` (a kit's number, then a dword of class bits;
  `kits.DUAL_BANS`). The slot kits' tables (`PROBE_SLOTS`) replace the whole count for their kind of
  magic, so they would take a new cleric's, druid's or preserver's slots' place.
- **A new preserver's spells, on changing class.** Every human (not a kit's). Where: the routine
  that changes a human's class, for a preserver (86DB5h), takes away its wizard spells and marks
  Grease (8) and Magic Missile (7) known: `PROBE_DUAL_SPELLS` (`INT 9Ch`, new: those two `push /
  push si / call 500:43h / add sp,4`, 22 bytes from 86DE4h) calls CHOOSE A SPELL (620:5Ch, 85560h:
  the level up's) twice in their place, through its stub (`PICK_STUB`: DS less 4Ch, as `WP_STUB`),
  with the spell levels on offer up to 1st (`PICK_CAP`, which `PROBE_PICK_LEVEL` heeds). The dual
  routine is in CHOOSE A SPELL's own overlay (85560h to 87250h), so the call can't unload the code
  it returns to. The same call from another overlay needs its way back where the overlay manager can
  patch it: see the next one (at creation).
- **A new preserver's spells, at creation.** Every preserver. Where: the creation screen's DONE
  (overlay 65480h) marks spells known by preserver level (`[BP-2]`, 66F2Dh on: 7 and 8 at 1st; 9 and
  0Bh too at 2nd; 0Fh and 16h too at 3rd). `PROBE_CR_SPELLS` (`INT 98h`, new: `mov ax,[bp-2]`, 3
  bytes) has a character made on the creation screen (the grants called from DONE, 66556h: their way
  back at `[BP+2]`, `[BP+4]` is the INT's less `CR_FROM_DONE`, in the same overlay; START GAME with
  no party made calls them for the game's own party from 65480h+6FBh, which keeps the game's spells,
  and the creature's status can't tell the two, Okay in both) pick as many on CHOOSE A SPELL
  (`PICK_SPELLS`: 2, 4, or 4 and two of 2nd level; a Scholar's one more a level, `KIT_MADE`) and
  goes on past them (66F83h, `CR_SPELLS_PAST`). CHOOSE A SPELL returns nothing; EXIT leaves it with
  no spell learnt, which `PICK_SPELLS` tells by counting the member's known preserver spells before
  and after (`PICK_KNOWN`, the low four bits of each byte from `KNOWN_OFF`, as 500:43h sets them;
  the party's four only, creation's and DUAL's among them). Then the picks end and `PICK_FILL` marks
  the game's own spells known for those left, in its order, less any known (`fill_first`,
  `fill_second`). DONE's routine (6649Ch) has saved the character to its slot and opened its files
  (550:57h) before the grants, so going back to the creation screen from here isn't done. CHOOSE A
  SPELL is another overlay, whose loading may put the creation code out: without care the game is
  lost on the way back. The INT's way back is pushed as a stack frame (`push cs / push ip / push bp
  / mov bp,sp`) that the overlay manager walks and patches to reload the code first, as
  `PROBE_LV_PICK` and `PROBE_DUAL_KIT` do, and read back after.
- **Sound numbers on the sheet.** Every character. Where: the game reads a word at sheet `+42h`
  (78FDAh, `mov dx,[es:bx+42h]`: a sound to play, 4 if 0) and at `+44h` (81DE3h, `mov
  ax,[es:bx+44h]`: played if not 0), and the kit byte (`+43h`) and second sphere (`+45h`) are their
  high bytes, 0 in every one of the game's sheets: `PROBE_SOUND_42` and `PROBE_SOUND_44` (`INT 9Bh`,
  `INT 9Ah`, new, 4 bytes each) read the low byte alone (`movzx`).
- **A kit for a dual-classing human's new class.** Every kit. Where: in the routine that changes a
  human's class (86C80h), once the classes have moved down and the new one (`[BP+8]`) is first:
  `PROBE_DUAL_KIT` (`INT 99h`, new: `cmp word [bp+8],0Ch`, 4 bytes at 86D90h; the compare done
  after, its flags back with `RETF 2`) shows the game's three-choice menu, the one the DUAL window
  asks a cleric's sphere on (4D0:25h, overlay 54D90h: its stub 41B4h, `DK_STUB` from DS; arguments
  x, y, a far title, 1, three far rows; it returns the row clicked, 1-3, else 0, and leaves an empty
  row out). Title `KIT: NONE`, rows the new class's kits (`KIT_NAME_PTR` into `KIT_NAMES`); a kit
  `DK_BANNED` bars an empty row: its `DUAL_BANS` hold one of the other classes, or it and one of
  their kits are a `KIT_PAIRS` pair (`kits.dual_kit_banned`, `KIT_PAIRS`). The kit goes in the kit
  byte's bits for place 0 (`KIT_PLACE` × 2 up). An Elementalist's second sphere (`SPHERE2`) on the
  menu again (`DK_SECOND`: the three spheres not the cleric's), before the routine marks the
  spheres' spells known (`PROBE_EL_KNOW` takes it in). Then, with weapon specialization, `LV_CHECK`
  (the level up's weapon kinds, through the psionicists' pop-up, 620:57h: `PICK_STUB`'s entry 57h).
  The menu is another overlay, so the INT's way back is put in a stack frame the overlay manager
  walks and patches (`push cs / push ip / push bp / mov bp,sp`, as `PROBE_LV_PICK`), and read back
  from it after. `PROBE_DUAL_SPELLS` gives three picks, not two, when the kit taken for the new
  preserver class is the Scholar.
- **Starting gear fitted to the kit.** Ravager, Brute, Shinobi, Seeker (a forbidden hand item),
  Shadowblade, Ghetto Fighter, Rescuer (the shield left behind), Arena Champion (a shield), Ghetto
  Fighter (a dagger in hand: `_ghetto_dagger`), Poisoner (one of its weapon spec in each hand, the
  dagger or the short sword: `_poisoner_daggers`), Battle Mage (its weapon spec's weapon), Battle
  Dancer (a second long sword in the left hand in place of the shield, `_kit_second_weapon`, and a
  bow and arrows, with fuller starting gear: `startgear.py`); Myrmidon (its second weapon spec's
  weapon in the left hand in place of the shield, if one-handed and for melee). Where: the game
  gives a new character its class's gear when DONE is clicked (the README's table, seen in play).
  The dice log's `weaponchoice.kit_gear` (after `finish_new`, with the rule for kits; New characters
  only), for a hand's item `restrict.kit_forbids` forbids (the off hand as such): a weapon in the
  right hand becomes a plain one (`plain_weapon`) of the first kind it may use and the kit allows,
  the character's chosen kinds first, then `REPLACE_ORDER` (the long sword's neighbours: short
  sword, axe, mace, great axe, gythka, polearm), then any; a two-handed one sends the off hand's
  item to the backpack (`_shield_off`); a shield is taken away (`ring.unlink`: out of its list, its
  record back on the game's free list), anything else goes to a backpack cell (if the shield can't
  be unlinked, it too). An Arena Champion with no shield has its off-hand item made the game's
  starting shield (`SHIELD`: type 4, name 05h, picture FC04h, price 10). A Battle Mage with weapon
  specialization and no weapon of its chosen kind has its right hand's item (the quarterstaff) made
  one (`start_weapon`). Each change leaves nothing to change again.
- **Caster level, a spell's level.** Elementalist, Healer. Where: the caster level routine (81B16h:
  the spell levels it casts, Dispel Magic) and the effect level routine (5E25Ch: durations and
  damage) count a class whose mask meets the spell's: `PROBE_EL_CAST` (`INT A0h`, new: `mov
  edx,es:[si+19Dh]`, 81B42h) and `PROBE_EL_LEVEL` (`INT 9Fh`, new: `mov ebx,es:[bx+19Dh]`, 5E375h)
  give a spell of its second sphere its own cleric's bit too, and a Healer a spell of its element's
  druid (`HEALER_COSMOS`); `kits.spell_spheres`, `GameData.effect_caster_level`.
- **Weapons.** Elementalist (its second sphere's as well as its own). Where: `CLASS_FORBIDS`'s
  cleric spheres (`EL_SECOND`), and `KINDS_ALLOWED` through it; `restrict.elementalist_sphere`.
- **Choosing it.** Elementalist, Healer. Where: the creation panel's spheres (the game's, drawn from
  a mask by 63FEEh, `DS:4982h` its own sphere's row): `WP_CLICK` sends a click on a sphere's row to
  `EL_CLICK`, which takes or takes back the second (the game's mask left alone) and has `EL_MARKS`
  draw both marked and every row in use; `PROBE_WP_CLASS` (after every click) draws them so again
  over the game's own drawing (`EL_REMARK`). A Healer's row on the KIT page is greyed and does
  nothing unless the sphere marked is water (`HEALER_BARRED`: `WP_SPHERE_MASK` 10h, as the page is
  opened from the spheres; `KIT_MARKS`, `KIT_ROW`), and while one is taken a click on a sphere's row
  takes it back (`EL_CLICK`: the sheet's kit byte `KIT_OPEN`, the click the game's); after DUAL,
  `DK_BANNED` leaves it off the menu for a cleric not of water (`kits.dual_kit_banned`).

Every kit also needs its Python side: the Characters tab and the in-game
THAC0 and saves (`game.py`), the dice log's lines, and tests that hold the
helper's code (emulated) to the Python.

### How they're checked

Each kit's helper code is held to its Python by emulated tests
(`tests/test_dsclog.py` runs the helper's routines in a CPU emulator), and
each was played in the game: the creation screen's KIT page and hit dice, the
level ups (Shinobi and Scholar spells, Seeker slots), the KIT menu after DUAL
with its bans, and the Effects screen's pages.

## Level cap by XP

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

## STORE and RECALL on the creation screen

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
the AC and damage. The overlay's segment is the INT's return, and both calls
are made with it in a frame the overlay manager can fix up (`RS_FRAMED`, as
`PROBE_USE_ITEM`'s): the scores' redraw is another overlay's, and loading it
can move or drop the creation screen's, which the manager then puts back and
the frame follows. Without it (2.8.0 to 2.13.0, once the overlay buffer was
filled differently; and only for a RECALL before the die was rolled on that visit
to the screen: after a roll it never stopped, in 2.13.0 either) RECALL jumped into what was no longer the die's routine
and DOSBox stopped ("DynrecCore: illegal option"). Checked in DOSBox: STORE,
the die, RECALL twice, the scores, hit points, PSP and age put back each time.

## Fuller starting gear

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
worn list, the held one for a weapon, or the backpack's, as the inventory
screen keeps it: `pickpocket.list_for`), and moved with
`pickpocket.place`. Each step is skipped once its item or kind is there, so
`fill` leaves nothing to do the next time; one line for the log lists what it
gave. `fill_member` gives a thri-kreen (race 8, `THRI_KREEN`) nothing, and
does one character whatever its status: the game's own party (already Okay)
gets it through `defaultparty.ready`'s last step, `gear`.

## The game's own party

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
K'ratchek (the thri-kreen): `SKY_LEVEL` and `PSI_KIT` as a Wasteland Seer's (`CR_OWN_RACE`),
and `OWN_THROWS` in `PROBE_ATTACKS` (and the inventory's `PROBE_MISSILE_LINE`)
2 more halves a round with a chatkcha, whatever the specialization rule
(`GameData.weapon_hits` the same). Cilla (the elf): `stealth.py`'s hiding not
halved in daylight (`kits.not_halved_by_sun`, as an Assassin's and a Military
Scout's). The Effects screen's lines are `OWN_LINES` (after the kits', in
`EF_LINES_OF`); the Characters tab's `GameData.kit` adds `kits.OWN_FEATURES`.
Seen in play: the dice log's lines as the game starts, Gerakis's check
("needs 18 or less (CON 22 -4)"), Cilla's hiding at 50 in the arena, the four
Effects screens, K'ratchek's inventory line `Chatkcha 2.5x1D6+4` (1.5x before).

## The leader's CHA at shops

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

## Buying back magical items

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

## Thief skills from AD&D's table

([In the features page](FEATURES.md#thief-skills-from-adds-table).)

How: where the game's thief skill routine adds 4 a level, the helper
(`INT E4h`) puts AD&D's number for the level in place of the game's base and
level, adds the DEX table's, and jumps past the game's DEX formula to its
armour and effects. At the routine's end (`INT D9h`, below) the helper keeps
the chance to 95 (`THIEF_MOST`). The Loader's screens and the inventory
screen's panel work the chances out the same way.

The game's equipment penalty on thief skills is gone whatever the switch: the
slots where anything brings it (the legs, the quiver and both hands) are a list
of words at the thief table's +D0h, ended by 13 (`game.THIEF_PENALTY_LIST`), and
the patched game empties it (`thief_slots` in `gamepatch.py`, DSUN.EXE 44F70h).
The Loader reads the list from the running game, so its numbers match whichever
game it is.

## Hiding in shadows to backstab

([In the features page](FEATURES.md#hiding-in-shadows-to-backstab).)

How (the cloak, boots and belt): the patched game's item box (`INT DAh`, where
it has drawn the name) asks the helper, which draws the line with the game's
own text routine when the item's type is worn as a cloak, on the feet or as a
belt; and at the end of the game's thief skill routine (`INT D9h`, where it
returns the chance, armour and effects counted) the helper adds the belt's 5
to picking pockets and opening locks for a thief wearing one.

Daylight (`stealth.daylight`): an outdoor map (`stealth.OUTDOORS`) is all
daylight; on a map with buildings (`INDOOR_TILES`, the indoor floors' tile
numbers by region) it goes by the floor under the thief, read from the game's
map of the region in memory (the far pointer at `DS:2F4Ah`, `MAP_PTR`: a tile
number a square, 128 to a row); any other map is roofed.

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

## Spell arrows

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

**The Loader** (`SpellArrows.make`), with the Spellarcher's quiver empty (with
the same spell's arrows in it, their count goes up by as many, to `MOST_ARROWS`,
the item's word; with anything else, it says so and uses nothing), takes a slot of the touch spell's level from the
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

## Picking pockets

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
and the helper shows the result instead of the box. With no answer within
`PICK_WAIT` (the Loader held up, or the game busy with its lists) the helper
goes on as the game would and marks the request answered (`USE_REPLY` =
`USE_SEQ`), so a late Loader does nothing (the same for spell arrows); its
wait counts the BIOS's ticks, so it runs with interrupts on. A known limit: the
Loader looks at the request once, at the start of its answer, so a timeout
that falls while it is already moving the item (half a second or more inside
one pick) lets the game's own handling run alongside; a claim word the Loader
set before acting, which DSCLOG waited on, would close it. Not seen in play. The pointer turned to
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
