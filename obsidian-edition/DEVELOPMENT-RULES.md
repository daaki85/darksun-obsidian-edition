# Development: the rules

*Part of the [development notes](DEVELOPMENT.md). How each rule change, the character customization (weapon specs, the starting gear; the kits on [their own page](DEVELOPMENT-KITS.md)) and the improved thieving are done: where the patched game calls DSCLOG, and what the Loader reads and writes. Most headings name the section of a player's page they explain (the [features page](FEATURES.md), the [README](README.md), [items](ITEMS.md), [kits](KITS.md), [bugs fixed](GAME-BUGS.md), [how the game works](HOW-THE-GAME-WORKS.md), [the dice log](DICE-LOG.md)); the rest, a part of one or a note of their own, say which at their start.*

## Contents

- [The switches always on](#the-switches-always-on)
- [Class restrictions](#class-restrictions)
- [Multiclass hit points](#multiclass-hit-points)
- [Hit dice: the better of two](#hit-dice-the-better-of-two)
- [Scores and hit points as rolled](#scores-and-hit-points-as-rolled)
- [AD&D's class tables](#adds-class-tables)
- [CON as in AD&D](#con-as-in-add)
- [Dual-classing as the manual has it](#dual-classing-as-the-manual-has-it)
- [Ages and magical aging](#ages-and-magical-aging)
  - [Haste's aging](#hastes-aging)
  - [Restore Youth](#restore-youth)
  - [Natural aging](#natural-aging)
  - [The age on the creation screen](#the-age-on-the-creation-screen)
  - [Grey hair on the map](#grey-hair-on-the-map)
- [Two weapons](#two-weapons)
- [Half-giants' two-handed weapons](#half-giants-two-handed-weapons)
- [Cahulaks](#cahulaks)
- [Lotulis, double spear and trikal](#lotulis-double-spear-and-trikal)
- [Creature size](#creature-size)
- [Held targets](#held-targets)
- [Staff sling stinkpots](#staff-sling-stinkpots)
- [Polearm reach](#polearm-reach)
- [Rings and cloaks of protection](#rings-and-cloaks-of-protection)
- [Helms give AC 1](#helms-give-ac-1)
- [Items saving against acid](#items-saving-against-acid)
- [Rangers' casting level](#rangers-casting-level)
- [Preservers' INT](#preservers-int)
- [Spells saved against with the spell save](#spells-saved-against-with-the-spell-save)
- [Fire, cold and electricity: DEX instead of a doubled d20](#fire-cold-and-electricity-dex-instead-of-a-doubled-d20)
- [Enlarge multiplies the weapon's dice only](#enlarge-multiplies-the-weapons-dice-only)
- [Spells roll to hit](#spells-roll-to-hit)
- [Resting as in AD&D](#resting-as-in-add)
- [Spells and psionics as the manual describes them](#spells-and-psionics-as-the-manual-describes-them)
  - [The spell records, Stinking Cloud, Chaos and Free Action](#the-spell-records-stinking-cloud-chaos-and-free-action)
  - [Turn Undead, Minute Meteors and Flame Arrow](#turn-undead-minute-meteors-and-flame-arrow)
  - [The saves, and the other spells and psionics](#the-saves-and-the-other-spells-and-psionics)
  - [The monsters](#the-monsters)
- [Weapon specialization](#weapon-specialization)
- [Kits](#kits)
- [Preservers' first spells](#preservers-first-spells)
- [Psionic powers at creation](#psionic-powers-at-creation)
- [Level cap by XP](#level-cap-by-xp)
- [STORE and RECALL on the creation screen](#store-and-recall-on-the-creation-screen)
- [New characters and the roster write](#new-characters-and-the-roster-write)
- [Fuller starting gear](#fuller-starting-gear)
- [The game's own party](#the-games-own-party)
- [The leader's CHA at shops](#the-leaders-cha-at-shops)
- [Buying back magical items](#buying-back-magical-items)
- [Thief skills from AD&D's table](#thief-skills-from-adds-table)
  - [A lock or a pocket failed: another try a level later](#a-lock-or-a-pocket-failed-another-try-a-level-later)
- [Hiding in shadows to backstab](#hiding-in-shadows-to-backstab)
  - [A backstab multiplies the weapon's dice only](#a-backstab-multiplies-the-weapons-dice-only)
- [Picking pockets](#picking-pockets)
- [Sounds for hiding and picking pockets](#sounds-for-hiding-and-picking-pockets)

## The switches always on

(A note of its own, for every section below.) Most of the Options tab's switches went after 2.18
(the owner's call: fewer switches), and what they switched is always on. `game.ALWAYS_ON` names their
settings keys: the rule changes' (`game.RULE_SETTINGS_GONE`: `class_restrictions`, `multiclass_hp`,
`rolled_scores`, `adnd_tables`, `con_adnd`, `aging`, `dual_class`, `level_10`, `cahulaks`,
`creature_size`, `held_hit`, `protection_rules`, `item_saves`, `ranger_casting_level`,
`int_learning`, `spell_save`, `enlarge_dice`, `rest_heal`, `weapon_specialization`, `cha_prices`,
`thief_table`, `stealth`), and `combat_log`, `spells_manual`, `spell_to_hit`, `roll_store`,
`stealth_gear`, `pickpockets`, `elf_looks`, `cilla_elf`, `show_gear`, `shadows`, `dust`,
`see_through`, `targeting`, `scroll_map`, `camera_still`, `scene_pointer`, `mouse_start`,
`party_spread` and `effects_kept`. The rule changes still switched are `game.RULE_SETTINGS`
(`best_hit_die`, `half_giant_hands`, `helm_ac`, `kits`, `new_spells`).

- `launch.load_settings` and `save_settings` drop those keys (`game.drop_always_on`, with the
  old names `no_doubled_save`, `buyback`, `backstab_dice` and `two_weapons`), so an older
  settings.json's `false` never reaches a reader.
- Even unread, they count as on: `game.setting_on` answers True for them and `launch.content`
  gives them True.
- `game.RULES_ALWAYS` puts each gone rule's bit in the rules words (`RULES`, `RULES_HI`) whatever
  the settings, as it did `RULE_TWO_WEAPONS`; the words' layout is as it was (no bit renumbered),
  but DSCLOG no longer reads those bits (below).

**What went (2026-11-19, for DSCLOG's room: about 1.1 KB).** In DSCLOG, every test of a gone rule's
bit and the game's way behind it: rings and cloaks of protection (the game's every ring), two
weapons (the game's DEX bonus alone, `PROBE_TWO`'s first half), the doubled d20 (`PROBE_DOUBLE` is a
bare IRET), stealth, the level cap of 9, the thief table (the game's sums, the whole damage
multiplied, the backstab on two attacks), class restrictions, items' saves (`PROBE_ITEM_SKIP` only
clears ZF), multiclass hit points, weapon specialization (`WP_RULES`, the Crusader's and Mind
Warrior's warrior attacks, `WAR_KIT_OF`, `WAR_KIT_HALVES`, the kits' kinds in `WAR_HIT`,
`GEAR_MARK`: `CR_WEAPONS` always shows the weapon window), AD&D's tables, a ranger's casting level,
scores as rolled (`RL_HP` a bare IRET), ages, INT's learning, CHA's prices and the buyback, Enlarge's
whole damage (and its `% DAMAGE` word), CON as in AD&D, dual-classing, resting, Weapon traits (the
cahulaks, the stinkpots' 1d4, the polearm's reach), creature size and held targets (`HELD_DAMAGE`
no longer doubles); and `MANUAL_ON`, the test of `SPELLS_MANUAL` in the copy (always in now). In
the Loader: `prepare_patched_game` leaves out only Steady pace's patches when it is unticked (every
other group, `EFFECTS_KEPT`, `ROLL_STORE`, `CAMERA`, `SCENE_POINTER`, `MOUSE_START`, `PARTY_SPREAD`,
`SPELLS_MANUAL`, `SPELL_TO_HIT`, always in); `icons.write_resources` and `write_objects` with STORE
and RECALL, the manual's and the size rule's texts, the elves' looks, Cilla and the manual's
monsters always (`sprites.Pictures`' LOOKS gone; the half-elf recolour stays, for a file without
the pictures); `DiceLog`'s switch attributes (`pickpockets`, `show_gear`, `show_shadows`,
`combat_log`, `scroll_map`, `show_dust`, `see_through`, `elf_looks`, `cilla_elf`, `stealth_gear`,
`use_targeting`); the locks' and pockets' level gate always (`pickpocket`'s "too wary" gone);
`upgrade_settings`' combat log key; the party card's reads of `rule_vars["stealth"]` and
`["aging"]` (keys gone with their switches). The tests of an off path are tests of its bit clear
now (`ProtectionRuleTests.test_rule_bit_clear`, `StealthTests.test_rule_bit_clear`,
`SpecializeTests.test_rule_bit_clear` ...): the bit clear changes nothing.

In the Loader's reference models too (the final code audit's fixes): `DiceLog.rules` and
`game.RULES_IN_FORCE` start at `RULES_ALWAYS`, and `GameData`'s and the dice log's branches on a gone
rule's bit went with their tests of the game's way (the game's thief sums, the rings, two weapons,
the doubled d20, the whole damage backstabbed, a held target's x2 ...); `spelltexts.chunks` has no
arguments, `launch.CONTENT` no always-on key.

**What stays switchable**: the five rules of `game.RULE_SETTINGS` (`RULE_HELMS`, `RULE_HALF_GIANT`,
`RULE_HP_BEST`, `RULE_NEW_SPELLS`, `RULE_HI_KITS`), DSCLOG's tests of them kept, and Steady pace's
patches. **What stays in the code although unreached in play**: the kits' functions' `spec` and
`adnd` arguments (`kits.war_hit`, `warrior_attacks`, `allows`, `slots`: their tests drive both), the
header's `PICK_ON` and `SKILLS_ON` bits (always all set by the Loader now, but their zero also means
"no Loader yet"). Where a section below names the game's way, it is the game's, for comparison;
`tests/test_launch.py`'s `test_old_false_for_an_always_on_switch_is_passed_over` pins the rest.

## Class restrictions

([In the features page](FEATURES.md#class-restrictions).)

How: DSCLOG adds the classes' limits where the game checks an item against
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

In Wake of the Ravager (the port, `dsloader/ravager.py`; `RULE_RESTRICT` in `RULES_PORTED`): DSCLOG2's
`CU_SITE` (site 19, `class_can_use`: 775FDh, `mov [bp-1],al`, the end of the sequel's equip test, its
answer a byte) runs `CLASS_FORBIDS` with the sequel's offsets (a type's flags +0, material +4, armour
+0Bh 80h, classes +0Ch; a sheet's class bits +10h, race +12h, classes +1Bh, levels +1Eh) and the sequel's
`KIND_OF_TYPE`; `BELT_SITE` (site 20, `thief_skill_armour`: 8C7C5h, `mov ax,si / pop di`, the thief
skill routine 8C647h's end; its jump to the "pop di", 8C6C3h, sent to the same epilogue at 87443h in
the image, `thief_skill_armour_out`) gives 0 for a thief in armour that isn't light (`THIEF_HEAVY`, its
`ARMOUR_WORN` reading the item lists as `MELEE_IN` does); `THIEF_REAR`, called from `MISSILE_REAR`
(5C99Fh), takes the backstab back (the byte `[bp-21h]`, THAC0 `[bp-1Eh]`). The sequel has no kits,
weapon specs, robes, bracers or cloak of protection, so none of their exceptions; its only weapon
exception is the ranger's bow (`RANGER_BOW`). `CAST_ARMOUR` (site 21, `cast_armour`: 84F6Eh, `mov
ax,1`, the "yes" of the casting case, 84EE7h, of the sequel's "can this creature do it", 84E94h, which
reads the effect bits through 608h:25h: Can't Cast 68 is `test byte [bp-8],10h` there, never asked by
number) is `PROBE_NO_CAST`: a multiclass preserver in armour, a helm too, or a human preserver and
warrior, can't cast; the dice log's `no_spells` follows it. Not ported: a new character's starting
gear ([played](../playtest/logs/2026-11-22-ravager-class-restrictions.md): the equip test, the thief
skills, casting in armour and the backstab in a fight).

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
(`INT C9h`, 877DAh), DSCLOG (`CON_SHARE`) puts in Demihuman Deities' for a
character of more than one class: (total + bonus × dice) / classes less
total / classes, the dice each class's levels up to its group's last that
rolls one (the game's table, `+group × 4 + 1`), the bonus the table's
warrior bonus (`+52h` + CON) if a class is in the warrior group, else at most
+2. One class, or a human: the game's own.

In Wake of the Ravager the routines are SL's (the most 95193h, CON's 95261h, the reverse 954A5h), the
sheet 42h bytes (levels +1Eh, before any were lost +39h), CON the creature's +1Bh, the hit point table
SL's own bytes at the load + 45BEh. DSCLOG2's MC_CON (site 25 at 95208h) and MC_UNCON (site 26 at
954BDh) put in the same CON_SHARE, with the rule (RULE_MULTI_HP). The sequel works the most out only
at a level up (957E2h) and when a character is made from a script (6E8CEh, the reverse).

## Hit dice: the better of two

([In the features page](FEATURES.md#hit-dice-the-better-of-two).)

How: where the game has rolled a level's die (`INT BAh`, in place of the
`mov cx,ax` after the roll, DSUN.EXE 87319h), DSCLOG keeps the first roll
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
has its NOP; DSCLOG moves the return address past it.

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

Verified in play (no log kept). DONE on a preserver still opened CHOOSE A
SPELL (`PROBE_CR_SPELLS`).

In Wake of the Ravager the creation screen is SL's code 7D89h on (the data 6C0h back: the least and
most score DS:42D4h, 42D2h, the most hit points DS:42D6h; the creature being made DS:142Dh, its scores
from +19h; the sheet DS:1429h). DSCLOG2's RL_SCORE, RL_HP, RL_ROLL, RL_CON and RL_SUM (sites 27-31
at 6D1DDh, 6B7D2h, the three loops' 6D55Ah, 6D593h, 6D5CCh, 6B6CFh and 6CD98h) do what DSCLOG's do;
the die's loops read the roll flag from `[BP+6]` (SL's DI). The scores' box (DS:11F4h) is made a line
taller and wider as SL's. RL_TRY (the dice log's 4d4) is not ported.

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
`ADND_SLOTS`; anyone else, the routine as it was.

The saves: the game's save routine (877EBh, called only at a level up, 879B5h) finds each class
group's best level (876C3h: [BP-0Ah] + group x 2, the groups by the class at 420h:10h + class:
clerics and druids 0, fighters, gladiators and rangers 1, preservers 2, psionicists and thieves 3),
then for each group with a level and each of the five saves takes the group's 1st-level save less
(level - 1) x a rate / 100 (`[BP-2]`, plus a dwarf's or halfling's CON / 3.5 for group 1 or 4), but
no more than the table's third byte (420h:6Ch + group x 15 + save x 3: the 1st level's, the rate,
AD&D's last save), and keeps the lowest of the groups in the sheet's +37h..+3Bh. That third byte is
AD&D's best save, not the most a save improves, so a warrior's stop at 11/11/11/13/11 from 10th level.
And the game puts psionicists with thieves (group 3), at the best level of either.
`SAVE_BASE` (site `SAVE_BASE_SITE`, NS_IMAGE + 123, gamepatch `save_table`) replaces its `mov
al,es:[bx+6Ch]` (878F7h, 5 bytes) before `cbw / sub ax,[bp-2]`: with `RULE_HI_TABLES` AL is the
Player's Handbook's save (Table 60) plus the game's improvement worked out again, so the game's sum is
the Handbook's less the race's bonus; for group 3 the sheet's classes (DI the creature: DS:1661h + DI
x 47h, classes +21h, levels +24h) give a thief level and a psionicist level, and AL is the better of the
thief's save at the one and the psionicist's (Dark Sun's Table 8) at the other; without the rule, the
game's byte. The code and the bands (`SAVE_BANDS`, 33 of a first level and five saves: the four
groups', then the psionicists', `tables.RAV_SAVE_BANDS`, `class_saves`) are `dos/save_bands.inc`'s
macros, `SAVE_BASE_CODE` and `SAVE_BANDS_DATA` (the bands in DSCLOG's tail), shared with Wake of the
Ravager's DSCLOG2, whose routine (954D2h) is the same (its site 116; the sheets at `SHEETS_PTR`, 48h
bytes, classes +1Bh, levels +1Eh). Levels past a set's last band (21st) use it. `test_slsaves`,
`test_ravlevelcap`.

In Wake of the Ravager (`RULE_ADND_TABLES` in `RULES_PORTED`) the table is RESOURCE.GFF's DATA 1000,
read through 5C8:20 (the resource, the row 0-7, the index) at eight places (6C3E4h, 6C48Ah, 6C4CCh,
6FB8Bh, 958E3h, 95931h, 9597Ah, 95C84h): the creation screen, View Character and the level up, which
also caps the XP at the level 3 above's. It runs to 20 levels and is AD&D's but for the thief's,
gladiator's and ranger's 2nd levels, the druid's from 11th (the cleric's copied), the gladiator's 16th
and up (the fighter's) and the psionicist's 18th and 19th (1,400,000 and 1,700,000). DSCLOG2's
`XP_NEED` (site 32, `xp_need_*`) replaces `add sp,6 / imul eax,eax,64h` at each: the game's x 100 but
for those (`XP_FIXES`, tables.RAV_XP), the arguments taken off as the ADD did. The THAC0 routine
(9534Ch, run only at a level up, its answer the creature's +16h) and the slot routine (62A10h, asked
from 62893h at a rest) are SL's: `PRIEST_THAC0` (site 33 at 95391h) and `ADND_SLOTS` (site 34 at
62893h) do what DSCLOG's do, the slots AD&D's to 20th level at spell levels 1-9 (the Player's
Handbook's tables, `tables.RAV_PRIEST_SLOTS`, `RAV_WIZARD_SLOTS`; the class byte is the low byte of
the pushed word). The dice log's slot counts follow (`RavGameData.adnd_slots`).

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
same. Verified in play (no log kept). The saves
are checked by the emulator (`test_dwarves_poison_saves`): the party has no
dwarf or halfling.

In Wake of the Ravager (`RULE_CON` in `RULES_PORTED`) both routines are SL's: regeneration at 264BFh
(the last time DS:19B8h, the creatures' +1Bh CON, 31h bytes a creature) and CON's save adjustment at
1D35Bh (DS:880h by CON), added with a dwarf's or halfling's CON x 2 / 7 by the save modifiers (83A81h)
and a poison check (8E092h). DSCLOG2's `REGEN_SITE` (site 35, `regen_rate`, 26599h) and `CON_SAVE`
(site 36, `con_save`, 1D36Bh; the race the sheet's +12h through the creature's +4) do what DSCLOG's do,
each with the rule. The dice log's save modifiers drop the CON adjustment only with the rule.

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

`RULE_HI_DUAL` (`game.RULE_DUAL_CLASS`, always on) is DSCLOG's; the five compares are
sites in every game's copy: `DUAL_LEVEL` (`dual_level_menu`, `dual_level_view`, `dual_level_window`:
the game's `cmp byte [es:bx+24h],2`, 3 with the rule) and `DUAL_PRIMES` (`dual_old_prime`,
`dual_new_prime`: with the rule every prime requisite of the class,
`DUAL_PRIMES_OF`'s bits, the manual's as `tracker.PRIME_REQUISITES` has them,
the old class at 15 or more, the new at 17 or more, on the creature's scores
as the game reads them). Each sets the flags for the game's own jump after it.
The old class is the sheet's first, as the game's (a second change checks the
first class's level and primes, the game's way). Checked by the emulator
(`test_group4`'s `test_dual_level`, `test_dual_primes`). The classes a kit bars, and the sphere
menu after CLERIC, DRUID or RANGER, are the kits' ([Where each effect goes](DEVELOPMENT-KITS.md#where-each-effect-goes):
`PROBE_DUAL_BAN`, `DUAL_SPHERES`, `PROBE_SPHERE` and its `SPHERE_BARRED`).

In Wake of the Ravager (`RULE_DUAL_CLASS` in `RULES_PORTED`) the code is SL's with the sequel's records
and unsigned jumps: the two portrait menus' test (7926Ch, 7948Bh) and the DUAL window's (94BCCh) are
`cmp byte [es:bx+1Eh],2`, the primes `cmp byte [es:bx+19h],0Fh` and `...,11h` (94B70h, 94BA5h; the
creature's scores from +19h, the class map 360h:9Dh). DSCLOG2's `DUAL_LEVEL` (site 37) and
`DUAL_PRIMES` (sites 38 and 39) do what DSCLOG's do with the rule, the game's compare without;
`DUAL_PRIMES_OF` gives the sequel's classes 18 and 19 a wizard's INT and a priest's WIS. The kits'
parts aren't ported (the sequel has no kits).

## Ages and magical aging

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
Verified in play (no log kept).

### Haste's aging

The dice log's `effect_changes`, as a Hasted effect (22) starts
on a combatant (not one a game just loaded has), calls `aging.hasted`: a system
shock roll by the creature's CON (`SYSTEM_SHOCK`, the Player's Handbook's
table), death on a failure (`kill`: HP 0 and the dead status, which the game
takes as dead: no more turns, no share of the XP, "Dead" under the portrait),
else a year (`age_by`) for a party member. The rolls are the Loader's, logged.
Verified in play (no log kept).

### Restore Youth

Restore Youth (211, a cosmos spell: `COSMOS_MASK` in DSCLOG's `P6_MASKS`) is
Cure Critical Wounds' record with its dice (+1Ch to +1Eh) made 0 and no
handler, so the game casts it as a touch spell that heals nothing. The dice
log's `KIND_CAST` line for it calls `aging.restore` with the target and the
caster's level (`effect_caster_level`): a system shock roll, then `age_by` back
by the level, never below the character's true age (`start_age`: the race's
base and the roll kept on the sheet, `game.sheet_roll`, with the game's years;
no cap on the years magic adds). Verified in play (no log kept).

### Natural aging

A year each time the game's clock passes another 365 days (`natural_years`:
the game time in seconds over `YEAR`), put in the stored age as it happens, so
a save holds the age and the scores' changes together. The years counted so
far are in the game's own flags, so a save keeps them too (`counted_years`,
`set_counted`: flag 798 set once the count has begun, 799 to 806 the number;
every flag the Loader uses is in [The Loader's game
flags](DEVELOPMENT-INTERNALS.md#the-loaders-game-flags)). The dice log's `_natural_aging`, after
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
Verified in play (no log kept).
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
away, rolled a new age and asked for the weapon specs again. Verified in play (no log kept).
Tests: `test_edit_keeps_its_specs`.

The THAC0 line drawn beside the hit points, on the same redraws: [The creation
screen](DEVELOPMENT-SCREENS.md#the-creation-screen).

Before 2.13.2 the age was rolled from the name and race (`natural_start`, a
16-bit hash, DSCLOG's `AGE_ROLL` then); a character given one keeps it, and
`give_ages` puts that roll on its sheet, silently. `CR_AGE` and `CR_NAME` keep
their way back in their own words (`cr_ip`, `cr_cs`, `cr_fl`), apart from
`RL_SUM`'s, as they call the game's code before going back. Verified in play (no log kept). Tests: `test_age_dice`
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
thri-kreen's antennae greyed were tried and left out). Verified in play (no log kept).

### Ages in Wake of the Ravager

In Wake of the Ravager (`RULE_AGING` in `RULES_PORTED`) the Loader's `RavDiceLog._aging_pass` does it
all, four times a second on a steady look (the same party, the clock on by no more than
`NATURAL_JUMP`): `give_ages`, a year for each year the clock passes from the last look
(`natural_tick`), and Haste's aging for each Hasted effect (42) not there at the last look (`hasted`).
The age is kept alone in the sheet's +41h (`SHEET_AGE` there, `AGE_PLAIN`: no roll and no weapon specs
beside it), a byte no instruction of the sequel's touches; the only other such bytes, +3Dh and +3Fh,
hold CHARTRAN's kit and second sphere. The sequel's flags have no place for SL's count of the years,
so only the years the clock passes while the Loader watches are counted: a year crossed with the
Loader not running, or inside one jump of the clock of more than `NATURAL_JUMP` (2 days), is lost.
None is counted twice: the age is saved with the sheet (seen: saved and loaded again, the four ages
came back the same, and the dice log gave none again), and a load's first look only records. Dead is the sequel's status 7 (`RAV_DEAD_STATUS`, bound to `kalzith.DEAD_STATUS`
by `apply_layout`). DSCLOG2's `PROBE_CHAR` writes `AGE: 23` between SP and STR (`AGE_Y` 2Dh) from the
sheet and the races' bases (`age_bases`), with RULE_HI_AGING. Not ported: Restore Youth (the mod's own
spell, not in the sequel), the creation screen's roll (a new character gets its age when it joins), the Characters
tab's other numbers from STATS. A character brought over by CHARTRAN gets a new age (its SL age was
beside the weapon specs, which the transfer leaves behind).

## Two weapons

([In the features page](FEATURES.md#two-weapons).) Always on: `game.RULES_ALWAYS`
puts `RULE_TWO_WEAPONS` in the rules word whatever the settings (its switch is gone); DSCLOG
doesn't test the bit (its two weapons are always AD&D's).

How: the game reads the attacker's DEX adjustment when it works out the
two-weapon adjustment; DSCLOG takes over from there (`INT FEh`) and gives
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
use") and the one going in ("Need two free hands"). DSCLOG (`INT E3h`)
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
  felled (the creature's +0 HP), not large by `IS_LARGE` (a half-giant by the sheet's
  race, the size rule's `LARGE_BITS`, or Enlarged: as the size rule has it), not marked in
  `BIG` (the far block, its offset the header's +1840: the Loader's,
  `cahulaks.py`: a bit a combatant whose creature's name is on its list, written
  when it changes), saves against petrification with a d20 (`GAME_DIE`) against
  its sheet's +39h, a 20 always saving; recorded (`KIND_MANUAL`, `MN_TANGLE`). A
  failure marks it as Whirlwind's sweep does (`SWEPT_NOW`: yet to act this round,
  its turn taken at once; else `FAR_SWEPT`, `PROBE_MOVE` takes the next).

## Lotulis, double spear and trikal

([In the features page](FEATURES.md#lotulis-and-double-spear).)

Where the traits come from: [the Dark Sun weapons guide](https://www.geocities.ws/danach.geo/guide_1.html)'s
entries for Wake of the Ravager's weapons, for a specialist (`SPEC_OF` at `SPEC_SPECIAL` or above:
its weapon spec chosen, specialized or a master). The types (148-153, the last six of `npcitems.TYPES`, in the Loader's copy of GPLDATA, `game.RAVAGER_TYPES`) and their kinds (16-21, `KIND_OF_TYPE`) are the Loader's; the sequel's
net is left out. Both traits ride the cahulaks' sites, with the same rule:

- **The trikal** (type 151): `CAH_HIT` takes it as the cahulaks, a man-sized or smaller target not
  felled and not in `BIG`, with `TG_HOW` its save (the sheet's +37h, paralysis: `TRIP_SAVE`) and
  its record (`MN_TRIP`) in place of the tangle's (+39h, `MN_TANGLE`).
- **The lotulis and double spear** (149, 150): `SF_SWING`, from `CAH_SWING`, at the round's last
  swing of two or more ([BP-14h] = [BP-8] - 1) looks for a second foe: the first combatant in the
  things' order on the first target's side (the creature's +1Dh, low 3 bits), standing and Okay
  (+1Ch 1), at distance 1 from the attacker (the game's distance routine, 1A0A:2BA5h). It keeps
  `TARGET` (494Ah) and the AC ([BP+0Ch]) in `SF_TARGET` and `SF_AC`, makes them the foe's (its AC
  `THORNS_AC`'s: the sheet and the armour worn, not spells'), and records `MN_SECOND`. `SF_BACK`,
  first at `AMMO_TURN`'s site (58C38h, which every swing that ends the round passes), puts them
  back. `SF_LESS`, first at `STAB_ROLL`, takes 1 off the double spear's damage ([BP-4], at least 1)
  while `SF_TARGET` is set.

The window that picks a weapon spec has 22 slots in four rows (`PICK_FIRST` 8C0h on, past the kit
pages' rows at 870h); the game's title lines are left empty (its `push` of the title's line is a
signed byte, and row four's is at 146) and `PK_HOVER` draws the title under the rows. The
weapon specs are stored as v3 ([weapon specialization](#weapon-specialization)). Tests: `test_trip`,
`test_second_foe` (`test_cahulaks`), `test_specslots`, `test_ravager_weapon_lines`. Verified in
play, with a control run:
[2026-11-23](https://github.com/daaki85/darksun-obsidian-edition/blob/main/playtest/logs/2026-11-23-ravager-weapons.md).

## Creature size

([In the features page](FEATURES.md#creature-size).)

Where the dice come from: AD&D 2nd Edition's *Player's Handbook* weapons table, each weapon by the
entry whose small and man-sized dice are the game's; the pick the footman's pick and the axe the
battle axe of *Player's Option: Skills & Powers* (1d6+1/2d4 and 1d8/1d10: the game's pick was the
horseman's, 1d4+1/1d4, and its 1d6+1 is the mod's, with no switch); the great axe the *Complete
Book of Dwarves*' two-handed battle axe (1d10/2d8); the chatkcha, the gythka and the cahulaks from
[a Dark Sun weapons guide](https://www.geocities.ws/danach.geo/guide_1.html), which also gives a
thri-kreen's chatkcha its 2/1.

How: the game keeps no size. The Loader's `sizes.py` gives each creature one
(people by the sheet's race, the rest by name: `CREATURES.md`), and `sizes.Large`
writes `LARGE_BITS`, a bit a combatant large or bigger, into DSCLOG's tail (its
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
  weapon's lines for the item box, the inventory and the Look box, has drawn its
  damage line from SS:[BP-2Eh]): for the item box ([BP-6], its creature, 0) the
  line read back ("1D8-1"), the large dice worked out from it as `SIZE_DICE` does
  (`SL_CHANGE`), and drawn again with `/1D12-1` after it by the game's own text call
  (its far address read from the call before; the box's spare row is the "Hit -1"
  or charges one), with interrupts on (`STI`: the INT turned them off). `SIZE_PRE` (72A8Ah, its "push word [bp+12h]", the push made in
  the handler, the interrupt's frame moved down a word) makes Shillelagh's line, the
  game's 2D4, 1D6+1 before it is drawn, everywhere (the box's then gets `/2D4`). The
  inventory and View Character keep the game's lines: their rows are full, and a
  click to switch them (tried 2026-11-10) found no way to have the game redraw the
  panel cleanly (playtest/logs/2026-11-10-creature-size.md).

### Wake of the Ravager's weapons

The sequel's helper, DSCLOG2, uses the same `LARGE_DICE` by weapon kind (`KIND_OF_TYPE`, the sequel's
item types from OBJEX.GFF's names). Twelve of the sequel's weapons don't fit that, either because SL
has no such weapon or because the game gives them other small dice than SL's weapon of the kind. They
are in DSCLOG2's `RAV_LARGE` instead (checked first). Each is the AD&D 2nd Edition *Player's Handbook*
weapon whose small and man-sized dice are the game's (the dice below are the game's, read from its
item types in play, 2026-11-21):

| Weapon (type) | The game's dice | Against a large target | Why |
|---|---|---|---|
| Twohand Sword (101) | 1d10, two-handed | 3d6 | The two-handed sword's 1d10/3d6 |
| Crystal sword (35) | 1d10, two-handed | 3d6 | Two-handed with the two-handed sword's small die, not a long sword's |
| Trikal (100) | 1d10 | 2d6 | A bladed polearm. The halberd is the PHB weapon with a 1d10 small die (1d10/2d6) |
| Promere hammer (81) | 1d10, two-handed | 2d6 | A heavy two-handed weapon with a 1d10 small die: the halberd's large die too |
| Lotulis (61) | 2d4, two-handed | 2d6 | The bardiche's 2d4/2d6. Dark Sun's own lotulis also does more to the large than to the small |
| Double Spear (39) | 1d6, two-handed | 1d8 | The spear's 1d6/1d8 |
| Toothed Club (89) | 1d8+2 | 1d6+3 | A spiked club: the morning star's large 1d6+1, the game's +2 kept. SL's club kind would have made it 1d3+2 |
| Axe (48) | 1d6 | 1d4 | The hand axe's 1d6/1d4. The other Axe (8) is 1d8, the battle axe, and keeps the axe kind's 1d10 |
| Pick (79) | 1d4+1, two-handed | 1d4 | The horseman's pick's 1d4+1/1d4. SL's pick kind assumes the mod's 1d6+1 footman's pick |
| Darts (43) | 1d4 | 1d3 | One die down, as the dart's 1d3/1d2. The 1d2 Darts (38) keep 1d2 |
| Javelin (59) | 1d4 | the same | The javelin's dice are the same on any size (1d6/1d6) |
| Flameblade (47) | 1d4+4 | the same | Flame Blade's damage is the spell's, 1d4+4, whatever the size |

The Net (71) has no damage. In play (logs/2026-11-21-ravager-size.md): Terrannus's Twohand Sword hit a
large Draxan for "3d6 = [2 + 6 + 1] +1 weapon (3d6 for 1d10: a large target)", and Gerakis's Polearm
for "2d6 ... (2d6 for 1d10: a large target)".

## Held targets

([In the features page](FEATURES.md#held-targets).)

The game's way: the weapon attack routine (5883Ah) rolls the d20 on every swing (589B6h on), hits
on a 20 (589E9h, "cmp word [bp-6],14h / je 58A00h"), misses on a 1, else compares THAC0 less AC with
the roll. On a hit it hands the damage call (5B8:20h, 78BA8h) the damage and, at 58B0Dh ("mov
ax,[bp-4] / shl ax,1 / push ax"), twice the damage: what a helpless target takes. The damage routine
(79BF9h) takes that second number when the target's effects' bitset (598:25h = 76944h, a bit an
effect) has bit 34, Paralyzed, at its +4's bit 2, or its creature's +1Ch is 3, Out Cold; the save
routine (79A71h) fails such a target before rolling (79B0Ch, the same test).

The mod's rule (`RULE_HELD`, DSCLOG's `RULE_HI_HELD` 8000h, always on), two sites (`gamepatch`
"held_hit" and "held_damage"):
- `HELD_HIT` (589E9h; 4 bytes): the game's compare made in the handler and its ZF put in the INT's
  frame for the JE after it, set too when `HELD_NOW` finds the attack's target (DS:494Ah) Paralyzed
  (`NS_HAS`, effect 34) or Out Cold (its creature's +1Ch): the hit, whatever the d20.
- `HELD_DAMAGE` (58B0Dh; 5 bytes): AX the damage, not doubled (the game's doubles it).

`HELD_NOW` and the dice log share one test (`HELPLESS_OF`): each ring entry keeps the attack's
target's state at the roll at +188 (8000h, plus 1 Paralyzed or 2 Out Cold), read by
`Entry.helpless` through `DiceLog._helpless`, so a blow that kills or a Hold that ends before the
line is written still reads right (an older DSCLOG's entries fall back to `GameData.helpless`).
The attack's line says HIT, with `Paralyzed: hit
automatically, for normal damage (AD&D's held target)` under it, and the damage line has no x2.

## Staff sling stinkpots

([In the features page](FEATURES.md#staff-sling-stinkpots).)

The rule is **Weapon traits**, the cahulaks' switch (`RULE_CAHULAKS`, `RULE_HI_CAHULAKS`, the Loader's
`cahulaks`; `game.RULE_STINKPOTS` names it too); DSCLOG's `STINKPOTS`; no new patch in the game:

- **The dice.** The staff sling is item type 0 (IT1R's first record, `020008001400fa00...`: missile
  only, crushing, 1d4 at +0Ch/+0Dh). `STINK_SIDES` writes its sides, 3 (the game's 4), in
  the table the game read (`TYPES_FILL`, which notes it in `types_ptr`) and again at each pass of the
  main loop (`PROBE_SCROLL`), so a switch takes at once; only over a 3 or a 4, only while DS:1669h
  still points there. The game's attack, the item box, the inventory and View Character all read that
  record, and grand mastery's `NEXT_DIE` steps the 3 to a 4.
- **The hit.** `CAH_HIT` (58B54h, the cahulaks' site: a weapon hit that did damage, `[BP+14h]` the
  type, `[BP+18h]` the thrower, DS:494Ah the target) goes on to `STINK_HIT` for type 0. A target
  still standing (its creature's HP above 0) is spared if undead (5B8:A2h, 7BE20h, the game's own
  test) or if it takes none of the poison damage kind (5B8:66h, 7B492h: the share of damage kind 1 by
  its kind's resistance rules; its effects' bits, which only fire, cold and electricity read, given
  as zeros, `stink_none`). Otherwise the game's saving throw (5B8:2Fh, 79A71h: target, thrower,
  power 176, level 0) as against a monster's poisoned hit: record 176's +1Fh is 21h,
  paralysis/poison/death, and its damage kinds (100h) don't double the d20; every modifier the game
  gives that save counts, and a held or Out Cold target fails before rolling. A failure adds
  Nauseated (75) through 598:3Eh (76442h: target, thrower, spell 22, effect 75, (1d3 + 1) x 60
  seconds, 0). The spell is Stinking Cloud's: an effect filed under a spell of 8Ah or more with a
  party member as its caster clears a bit in the psionic powers' table as it ends (76883h), and no
  compare of an effect's spell with 22 turns up in the game's code. The calls are made in a frame the overlay
  manager can fix up (`OVR_BACK`), as `SHADOW_DRAIN`'s.
- **Nauseated (75).** The effects' bits (598:25h, 76944h) are 10 bytes, effects 0-79. `NS_HIT`
  (7C430h) takes 2 off a nauseated attacker's to-hit sum whatever the rules (only the rule puts the
  effect on). The game's table of effects' names and icons (selector 3E0h, 1BCh bytes) ends at 74,
  so `NS_ENTRY` gives 75 an entry of its own, `STINK_ENTRY`, after Reflected Image's past the spell
  rows (segment 4010h at 1FEh, zeros in the game): NAUSEATED and Stinking Cloud's icon (21022). Those
  five sites are the game's only readers of the table.
- **The dice log.** `KIND_MANUAL` entries: `MN_STINK` (11) before the save (target, thrower; 0 a save
  follows, 1 undead, 2 immune), `MN_NAUSEA` (12) after it (target, thrower, the d3 and the rounds; 0 and
  0 saved). Between them the game's save line is named for the stinkpot (`DiceLog._stink_save`, and no
  spell's damage window opened), `-> failed: nauseated`. The to-hit breakdown names `Nauseated -2`
  (`game.HIT_EFFECTS`).

Nauseated is fumes, not magic: Dispel Magic doesn't end it, as the game's Dispel Magic weighs only
effects 0 to 73.

Tests: tests/test_stinkpots.py (`StinkHitTests` runs the site in Unicorn with the game's routines
stubbed, `StinkSidesTests`, `StinkEffectTests`, the dice log's lines).

## Polearm reach

([In the features page](FEATURES.md#polearm-reach).)

The rule is **Weapon traits** again (`RULE_CAHULAKS`, `RULE_HI_CAHULAKS`, the Loader's `cahulaks`);
DSCLOG's `REACH`, one site (`gamepatch` "polearm_reach").

The game's way: every melee decision asks the combatant distance routine (1A0A:2BA5h, 22045h:
`[BP+6]` the attacker, `[BP+8]` the target, both combatants) for the least distance between the two
footprints, in squares by 898:000Ch (0DD8Ch: the smallest s with s x s + s at least dx x dx + dy x dy:
one square across or diagonally 1, two across 2, two across and one down 2, two across and two down
3), and compares it with 1. The item type's range byte (+0Ah) is 1 for every melee weapon and plays no
part in it (playtest/logs/2026-11-10-polearm-reach.md: a polearm whose type's +0Ah was 2 still
couldn't strike two squares away). It can't be made 2 either: the weapon picker (5900Ah) and the
attack routines (58019h, 5883Ah) take a weapon of range above 1 for a missile weapon (ammunition,
the projectile, the missile flag), and so do DSCLOG and the dice log.

`REACH_SITE` (2211Fh, the routine's end, "mov ax,[bp-16h]"; 3 bytes: the INT and the site's number)
does the MOV, then, with the rule, makes a result of 2 a 1 when all three hold:

- **The caller is a melee test**, told by the way back (`REACH_CALLER`): resident ones by segment
  (the CS less the game's DS, so wherever the game is loaded) and IP, `reach_rets`: the pointer's
  shape (1587:2B7Ah, after 1D7E5h: the sword at 1 or less, else the missile test); the attack
  pointer's click (1587:0AC5h, after 1B730h: the distance into DS:496Ch, then 1DFF2h with it); the
  walk arrow's click on a foe (1587:04B8h, after 1B123h: 1 or less attacks at once, else a path and
  action 13h); the walk to attack arriving (1587:1C36h, after 1C8A1h, and 1A0A:3071h, after 2250Eh);
  the step switch's case 19 (1A0A:14A2h, after 2093Eh). The computer's attack choice is in overlay
  612Eh (56CC0h on, its CS wherever the overlay manager loads it): its target's distance against its
  weapon's range (0DA7h, after 57A62h; at 57C54h a range at least the distance attacks, through
  58019h with that distance) and the target 57F44h found in range (1229h, after 57EE4h). Those two are
  told by the IP and the code around it, read through the way back: `9A A5 2B` (a far call to 2BA5h)
  before and `83 C4 04 89 46 F6` ("add sp,4 / mov [bp-0Ah],ax") after. The other callers keep 2:
  2013Ch (an ambush), 20924h, 209AFh, 209C5h, 209E3h in the step switch, 56E1Fh and 59FBEh in the
  overlay, 7AEC6h (a spell).
- **The attacker's hands hold a polearm and no other weapon** (`REACH_HANDS`): its creature
  (`COMBATANT_CREATURE`), its three item lists (+08h, +0Ah, +0Ch), each item's slot (+11h): in the
  right hand (3) or the left (10), a type `kind_of_type` makes a polearm (10, the kind + 1: the
  game's 19 and 111 and the Loader's metal polearm, `game.METAL_POLEARM_TYPE`) or a trikal (`TRIKAL_KIND`,
  20: `game.TRIKAL_TYPE`, Wake of the Ravager's, a polearm with three blades) counts one, any other
  type with a weapon flag (its +00h's 1 melee or 2 missile, `restrict.is_weapon`) one other weapon.
  Reach is one polearm and no other: a shield (flag 4) or nothing beside it. The missile slot (2) and
  the backpack aren't hands.
- **No wall is on the line between them** (`REACH_LINE`): the game's own line test (898:00A4h,
  0DE24h; the two things' squares, from DS:669Dh and 669Fh + 20h a thing in sixteenths, a height of
  0 each; -1 when a cell on the line has its bit 80h), which the attack pointer's click (1B700h) and
  the computer's attack (57C99h) make before the distance; the walk arrow's click and the walk to
  attack make none, as an adjacent foe needs none, so `REACH_LINE` asks it for every caller.

The game then takes the target as adjacent: the pointer's sword, the click's attack (the attack
routine is given the 1, so the polearm swings as a melee weapon; with a bow in the missile slot the
click at two squares swings rather than shoots), the walk arrow's attack from where the wielder
stands, and the computer's attack on a foe two squares away.

Limits, kept: two across and two down count 3 (no reach); a creature between doesn't stop the reach;
the computer's approach still walks to an adjacent square (its path finder, 1A0A:2E99h, isn't
asked), so a computer-controlled polearm uses the reach only on a foe already two away.

Tests: tests/test_reach.py (the site in Unicorn: a polearm alone or with a shield, a bow in the missile
slot; another weapon, a second polearm, a non-melee caller, an overlay IP without the AI's code, a
wall on the line (the line test stubbed), the rule off, distances 1 and 3; and, with DSUN.EXE beside GPLDATA.GFF, every call of the routine in the
game: the melee callers' code and the ones left alone).

## Rings and cloaks of protection

([In the features page](FEATURES.md#rings-and-cloaks-of-protection).)

How: the game's AC routine counts a worn item's plus only if its type's +0Fh
has bit 80h, which the Ring type lacks; DSCLOG (`INT F8h`, at 58EBDh)
sets it for rings, and the saving throw routine's sum of modifiers starts at
the worn rings' plus (`INT F9h`, its `xor si,si` at 79D47h) rather than 0.
With the rule, both look first at what the creature wears (`PROT_SCAN`: a
worn armour piece with a plus, one of metal, a shield in a hand, and each
hand's ring): the AC routine drops a ring with magical armour and the worse
of two rings, and both drop the cloak with any of the three. The Loader's
saves and AC rows weigh it the same way (`GameData.protection`).

## Helms give AC 1

([In the features page](FEATURES.md#helms-give-ac-1).)

How: DSCLOG sets the helm types' AC as the game's AC routine reads it
(`INT F8h`, the Ring +1's place), and as the item box reads it for its "AC
BONUS:" (`INT 88h`, at 8C15Ah), so a helm not worn yet shows its 1 too. (An
earlier rule gave boots a move in a fight; it is gone, and the boots' names it
changed go back to the game's.)

## Items saving against acid

([In the features page](FEATURES.md#items-saving-against-acid).)

The game's own check for armour reads the byte that holds the item's power, not its plus: a piece
with a power rolls a d20 against 10 less the power's number (which for every such armour in the
game means it always comes through), and any other is destroyed without a roll, Tanelyv's Armor +2
as surely as plain leather. A weapon is destroyed on a d20 under 8 less its plus.

How: where the game works out the number a weapon's d20 must reach
(`INT D6h`), where it skips the roll for armour with no magical power
(`INT D5h`) and where it works out armour's number (`INT D4h`), DSCLOG
gives the easier of the two and records the check for the dice log.

In Wake of the Ravager the same two checks are the same code (its 7CEC0h and 7D02Ah), an item's
power a word at +10h and its plus at +16h. Its power handler sends three powers there: Crystal
Brittle (103, the weapon, then the armour if the weapon came through), and monster powers 275 and
283 (the armour) and 284 (the weapon). DSCLOG2's ITEM_WEAPON, ITEM_SKIP and ITEM_ARMOUR (sites 22, 23
and 24 at 7CF22h, 7D0AAh and 7D0BEh) do what DSCLOG's do. So Crystal Brittle, which the sequel runs
through the acid check, now gives each item the acid save for its material too.

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

Verified in play (no log kept).

In Wake of the Ravager the two routines are the same: the caster level routine counts a ranger 7 less
("sub dx,7" at 97E00h), the duration and damage level routine (628AFh) takes it whole. DSCLOG2's
`RANGER_LEVEL` (`INT EAh` in place of "mov al,es:[bx+1Eh] / mov ah,0", 629F0h: the sheet's class at
+1Bh, its level at +1Eh) takes the 7 off with `RULE_HI_RANGER` (`ravager.RULES_PORTED` has
`RULE_RANGER_CAST`). No kits there, so no Seeker or Justifier. Played:
[the test log](../playtest/logs/2026-11-21-ravager-ranger.md).

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
d100 of DSCLOG's own (`D100`: a generator stirred by the BIOS's timer
ticks); over the chance, the game teaches the spell and uses the scroll up,
and `PROBE_LEARN_SAID` (`INT 92h`, new, 8B712h) takes it back (the four bits
cleared) and pushes YOU FAIL TO LEARN THE SPELL. Each try is told to the
Loader in DSCLOG's header (`+272`: a count, then the member, spell, INT,
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

In Wake of the Ravager the scroll's routine is rewritten (around 999C0h): a scroll is an item whose
entity (+0) is 7918h-79DFh (wizard) or 7AA8h-7B0Bh, its spell the power (+10h) less 1; the reader's
known wizard spells are a bitset, 15 bytes a member at selector 320h:39Ch (bit n spell n), the reader
at 370h:0B44h; known, YOU ALREADY KNOW THIS SPELL (99A86h); else the bit set, the scroll used up
(5F8h:43h) and YOU LEARN THE SPELL (99A7Fh). A spell's level: the game's table at DS:0656h, the first
spell of each level, a row of 11 for wizard spells then priest (`ravlog.SPELL_STARTS`; SL's 7-byte
table isn't there). DSCLOG2's `SCROLL_LEARN` (`INT EDh` for the "or ax,ax" at 99A2Fh), `LEARN_SAID`
(`INT EEh`, 99A7Fh) and `LEARN_REFUSED` (`INT EFh`, 99A86h) do SL's for a wizard (class 11 or the
sequel's 18) with `RULE_HI_INT`, the d100 from the game's seed, the try told at +272 as DSCLOG's.

At a level up the sequel's preserver (class 11 alone: 957ABh calls 688h:66h, 93160h, only for a level
never reached before, the sheet's +39h) asks its list routine (94C7Ch: the unknown spells of one level,
at 370h:7) at each level from its class level down, and opens CHOOSE A SPELL (93378h), which shows one
spell level a page (DS:43ECh, LEVEL pages through them) from the highest it casts (698h:39h). DSCLOG2's
`PICK_ANY` (`INT F0h`, "mov [bp-2],ax / or ax,ax" at 9317Fh, SL's 85580h) gives the highest level it
casts with room (a spell not known and fewer known than INT's most), or 0 and no window; `PICK_PAGE`
(`INT F2h`, "mov [43ECh],al" at 93487h, the sequel's own need) opens the window on that level;
`PICK_LIST` (`INT F1h`, "mov di,ax" at 93246h, SL's 8563Fh) empties a page whose level is full. (The
game's own count from the class level past spell level 10 reads the priest rows: with the rule it
stops at the highest spell level.) Played: [scrolls](../playtest/logs/2026-11-21-ravager-int.md), [the
level up](../playtest/logs/2026-11-21-ravager-int-levelup.md).

## Spells saved against with the spell save

([In the features page](FEATURES.md#spells-saved-against-with-the-spell-save).)

Part of Saving throws against spells (`spell_save`, always on: [above](#the-switches-always-on); `RULE_SPELL_SAVE` is `RULE_NO_DOUBLE`).

How: the Loader writes the game's own table that turns a spell's kind of save
into one of the five (a table of words at DS:1E75h, read afresh for every
save): the spell kind's entry the spell save (`set_rules`, `game.kind_to_save`).

## Fire, cold and electricity: DEX instead of a doubled d20

([In the features
page](FEATURES.md#fire-cold-and-electricity-dex-instead-of-a-doubled-d20).)

Part of Saving throws against spells (`spell_save`, always on: [above](#the-switches-always-on); `RULE_SPELL_SAVE` is `RULE_NO_DOUBLE`).

How: DSCLOG does the save's doubling (`INT F0h`) only while this rule is
off, and the Loader marks the fire, cold and electricity spells with the game's
own "can be dodged" flag (bit 40h of the spell's category word), which no spell
has, so the game's save routine adds the DEX defensive adjustment from its own
table.

In Wake of the Ravager (always on too): the Loader's patch `no_double` makes the save's `shl al,1`
(66E63h) two NOPs, and its copy of RESOURCE.GFF (`ravager.spell_fixed`, the fix `dodge`) sets the
same bit in every spell record whose flags word (+1Ah) has 86h (32 records, the monsters' fire and
cold powers among them); the sequel's modifiers routine (83606h) has SL's DEX test as it is. Its
spell save needs nothing: the sequel takes a spell's kind as the save itself, kind 5 the spell save.

## Enlarge multiplies the weapon's dice only

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
rather than DAMAGE (`EF_CHARGES`, `ef_enlarge_dice`). Verified in play (no log kept).

In Wake of the Ravager Enlarge is the same routine (863B2h, 628h:57h; its effect 32, its levels
608h:52h) and works the same: the stock game made Gerakis's 24 a 38 (x160%, Ar'anda's 6th level).
DSCLOG2's `ENL_ROLL` (`INT EBh` at the attack's "cmp word [bp+16h],1" after the damage roll, 5D0C8h:
the dice's sum, the roll less `[BP-14h]`, the sequel's bonus local) and `ENL_SITE` (`INT ECh`, 863E7h,
the 32 bytes as SL's) do SL's with `RULE_HI_ENLARGE`, the enlarged dice kept for a backstab (DSCLOG2's
`STAB_TIMES`: [A backstab multiplies the weapon's dice only](#a-backstab-multiplies-the-weapons-dice-only)). The dice log's Enlarge levels come from `RavGameData.effect_caster_level` (the sequel's
caster level routine, 97DC5h). Played: [the test log](../playtest/logs/2026-11-21-ravager-enlarge.md).

## Spells roll to hit

([In the features page](FEATURES.md#spells-roll-to-hit).) The Options tab's box
was the settings key `spell_to_hit`, always on now ([above](#the-switches-always-on)); off, `launch.py` left
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
  `[bp+0Ch]`, 1 more for a Scholar, `KIT_SCHOLAR`, as its +1Fh has it); less 5B8:EDh (7C3E9h: target, attacker, no weapon, kind; effects,
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
Verified: [log](https://github.com/daaki85/darksun-obsidian-edition/blob/main/playtest/logs/2026-11-08-spell-to-hit.md).

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

`RULE_HI_REST` (`game.RULE_REST`, always on) is DSCLOG's; both sites are in every game's copy,
each the game's own instruction in mode 1:

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

## Spells and psionics as the manual describes them

([In the features page](FEATURES.md#spells-and-psionics-as-the-manual-describes-them).)
Once a switch, `spells_manual`, always on now ([above](#the-switches-always-on)): the patches
in `gamepatch.SPELLS_MANUAL`; off, they were left out and the game's copy has
DSUN.EXE's bytes; DSCLOG's code that runs either way told it by `MANUAL_ON`
until the switch went (always in the copy now, the test gone). The points come from reports/spells-against-the-manual.md, which
says what was done with each.

### The spell records, Stinking Cloud, Chaos and Free Action

The spell records (spell s at file 41F70h + 20h x s: +4 the duration's dice,
count low and sides high, +5 that a caster level, +7 the unit, 60 a round, -1
charges or -9999 until removed; +12h's 80h a save negating the damage;
+1Ch..+1Eh the damage's dice; +1Fh the save, bit 0 one allowed), changed in the
Loader's copy of DSUN.EXE: Bestow Curse and Blood Flow allow a save, a save
negates Flaming Sphere, Solid Fog's and Minor Spell Turning's times, Cause
Fear's, Quicksand no save, Ironskin a blow a caster level (its level divisor,
shared with the damage formula, made 1), Turn Pebble to Boulder 3d6+8 (each
patch named for it in `gamepatch.py`). Then three sites:

- **Stinking Cloud**: the record's dice made 1d4 and DSCLOG's `STINK_SITE`
  (76D73h, in the time's routine, which rolls the dice with no bonus) adds the
  round.
- **Chaos**: `CHAOS_SITE` over the save modifiers' "sub si,100" (79F80h), the
  -100 for anyone not a warrior, skipped for a creature of INT 21 or more, or 4
  or less.
- **Free Action**: its handler (79406h), shared with Remove Paralysis and
  Protection from Paralysis (the spells' table at 79936h, their words at
  +4Ch), removes Slowed, then Paralyzed unless the creature is Poisoned; it is
  made a loop over the effects to remove pushed on the stack, through its own
  two far calls (their segment words, which the overlay manager fixes up, kept
  where they were), and Free Action's word points at a start that takes Stuck
  off first (`free_action_stuck`, `free_action_loop` and the three words).

Hold Undead's level, Color Spray's and a classless creature's level for its
saves (`HOLD_HD_SITE`, `SPRAY_SITE`, `HD_SAVE_SITE`) are with the game's own
fixes to those spells: [The game's
spells](DEVELOPMENT-CONTENT.md#the-games-spells). Tests: test_manual_spells
(`test_records`, `test_stinking_cloud_round_more`, `test_free_action`,
`test_remove_paralysis`, `test_level_sites`). Verified: [log](https://github.com/daaki85/darksun-obsidian-edition/blob/main/playtest/logs/2026-11-08-manual-spells.md), [log](https://github.com/daaki85/darksun-obsidian-edition/blob/main/playtest/logs/2026-11-08-hd-spells.md).

### Turn Undead, Minute Meteors and Flame Arrow

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
  to `MAP_COUNT`, 520, since people the Loader adds are numbered past 256), which a later try by the same priest finds first: the
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

The game's d20 at 7AE4Dh is never reached (the manual's spells are always in
the copy), so the old dice log line (`TURN_ROLL_RETURN`, `_overlay_turn`) is
never written.

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

### The saves, and the other spells and psionics

DSCLOG's sites are
`BLUR_SITE` ... `CELL_SITE` (`NS_IMAGE` + 78 to 87, in `SITE_TAB`'s order);
code that runs either way once told the switch by `MANUAL_ON` (Stinking
Cloud's record's dice made 41h, as the Loader's `GameData.spells_manual`), gone
with the switch: the sites are always in the copy. The dice
log's lines are `KIND_MANUAL` (14) entries (`MN_REC`: what, then a frame of the
creature and three words; dicelog's `_manual`).

- `save_signed` (79BBDh, `jae` made `jge`): the saving throw (79A71h) compared
  its byte total with the number needed unsigned, so the save modifiers' −100
  (79F80h Chaos, 79FA1h Cloudkill, 7A018h Scare, `SPRAY_SITE`) came out as a
  save (verified in play). Signed, −100 fails; +100 (Scare from 6th level: 7A01Fh)
  still saves (a d20 + 100 stays under 128; the doubled d20 is only for fire,
  cold and electricity, which get no +100). The one patch here in no switch:
  always applied (a fix of the game's, the user's decision 2026-11-09), so the
  dice log reads −100 as `none allowed (cannot save) -> failed` either way.
- `blur_save` (79DC0h, 11 bytes: Barkskin's test, `blur_save`): Barkskin's +1
  and Blur's (55: the effects' bits at `[bp+0Ah]`, byte 6 bit 7).
- `fire_shield_save` (79E03h, 20 bytes: Protection from Cold's test,
  `fshield_save`): its +3 and Fire Shield's (20) +2 when the spell's damage kinds
  (`[bp-4]`, the record's +1Ah) have fire (2) or cold (4).
  In Wake of the Ravager the save modifiers are 83606h (DI the modifier; the effects
  numbered otherwise: Barkskin 6, Blurry 13, Fire Shielded 38, Protected vs Cold 73):
  DSCLOG2's `BLUR_SAVE` (`INT F3h` at Barkskin's test, 8373Ah, 10 bytes) and
  `FSHIELD_SAVE` (`INT F4h` at Protection from Cold's, 837F7h, 20 bytes) do the same
  ([played](../playtest/logs/2026-11-21-ravager-blur-fire-shield.md)).
  The rest of the tail is SL's with DI for SI, so DSCLOG2's SITE (`INT F5h` and the site's
  number, its `SITE_TABLE`) does `stinking_cloud_round` (80249h), `classless_save_level`
  (83656h; the sheet's first level byte, +1Eh, the hit dice), `chaos_int` (83E83h; INT the
  creature's +1Ch), `color_spray_level` (83E86h), `cloudkill_save` (83E98h) and
  `cloudkill_kills` (651C5h); the sequel's Cloudkill record allows no save, as its manual
  ([played](../playtest/logs/2026-11-21-ravager-manual-saves.md)).
  Sites 6 and 7 do `flame_arrow_count` (the cast's tail, 7E8E0h, `[bp+0Ah]` the spell,
  `[bp+0Ch]` the level) and `biofeedback_least` (8348Bh; the sequel's Biofeedback is effect 8)
  ([played](../playtest/logs/2026-11-21-ravager-flame-biofeedback.md)).
  Sites 8 and 9 do Lower Resistance: `cast_level_kept` (7E338h, the cast's tail's start) keeps
  the cast's level for `ACID_ROUNDS` to put into Low Magic Res.'s (61) amount, and
  `lower_resistance_manual` (84B2Eh, the same 33 bytes as SL's) takes the 30 + the level off
  ([played](../playtest/logs/2026-11-21-ravager-lower-resistance.md)).
  Site 10 does `strength_dice` (6624Eh; the sheet's classes at +1Bh, the sequel's 18 a wizard's
  and 19 a priest's) ([played](../playtest/logs/2026-11-21-ravager-strength.md)).
  Site 11 does `cell_adjustment_heal` (664C5h, back to Neutralize Poison's "push ax" at 66545h)
  ([played](../playtest/logs/2026-11-21-ravager-cell-adjustment.md)).
  Site 12 does `feeblemind_psionics` (61D47h; the sequel's Feebleminded is effect 37)
  ([played](../playtest/logs/2026-11-21-ravager-feeblemind.md)).
  Site 13 does `rainbow_pattern_damage` (5CBECh; the hold ended through 608h:48h, 7FB63h, the
  entry's +7 its handle) ([played](../playtest/logs/2026-11-21-ravager-rainbow.md)).
  SL's `free_action_*` and the paralysis words have nothing to do in the sequel: its handler for
  spells with rules of their own (the cases at 66BA3h, their addresses at 66C43h) sends Protection
  from Paralysis (20), Remove Paralysis (159) and Free Action (175) to one start (661A0h) that takes
  off Slowed, Paralyzed (unless Poisoned), Petrified, No Attacks, Cannot Move (Web's), Cannot Use
  Psionics and Can't Cast.
  Site 14 does `hold_undead_level` at the sequel's own immunity routine's common way out (84A65h;
  the undead the sheet's race 9) ([played](../playtest/logs/2026-11-21-ravager-hold-undead.md)).
  Site 15 does `turn_undead_manual` (97C9Ch, `mov al,[es:bx+1Eh]`, the sequel's turning of one
  undead at 97C50h, SL's 7ADB7h with the same frame; called from the case 310, Turn Undead's, of the
  handler for spells with rules of their own): DSCLOG2's `TU_SITE`, SL's `tu_site` with the
  sequel's places (the destroy 97CFCh, the failure 97D12h, the end 97D1Bh), Afraid its 35 through
  608h:3Eh (7F9E6h) for spell 310, the d20 and the 3d4 from `GAME_DIE`, the failures a byte a target
  in the helper (`TU_FAILED`, cleared with the tangles at a fight's first round and by a turning out
  of a fight), a D\*'s more cleared by `CAST_START`
  ([played](../playtest/logs/2026-11-21-ravager-turn-undead.md); the destroy's way read, not played).
  Spells roll to hit in the sequel through site 16, `spell_hit` (84AAFh, `xor ax,ax / pop di`, the
  immunity routine 8451Ah's only "not immune" answer; its "immune" exit's jump, 84565h, which landed on
  the site's number and quit the game with "Illegal Op (gpl=49)", is sent to the same epilogue at
  7F2FEh in the image, `spell_hit_immune`,
  [played](../playtest/logs/2026-11-25-ravager-illegal-op.md)): the sequel has no always-hit stub or missile
  table (SL's 78BA0h, 7A1A7h), so DSCLOG2's `TH_SITE` answers 1 ("immune") on a miss, and the damage
  and effect routine (651A0h) skips both, as SL's. `PROBE_CAST` (80585h) arms it (`TH_CAST`) unless the
  cast routine returns to the weapon's spell on a hit (5D2D1h's bytes). The spells by the sequel's
  numbers (Magic Stone 121, Condense 169, Vampiric Touch 38, the Cause spells 118, 149, 171, 195,
  Poison 179; no record for SL's spines); THAC0 creature +16h, side +15h; the adjustments 628h:66h,
  STR's and DEX's part 98h:2C0h and 2D9h, the AC 4671h:7Ah (5D520h), the difficulty DS:143Ah; the
  computer's look-ahead calls (`[bp-4]` 1, 5F2D2h's) never roll
  ([played](../playtest/logs/2026-11-22-ravager-spell-to-hit.md)).
  Resting heals by nature in the sequel through site 17, `rest_hp` (8CF79h, `mov [es:bx],ax` in the
  rest 8CA7Ah's pass 2, SL's 808AFh): DSCLOG2's `REST_HP` with `RULE_HI_REST` (in `RULES_PORTED`), the
  creature's CON at +1Bh, the level hit point table at load + 45BEh (selector 4D0h; the same bytes as
  SL's, classes 18 and 19 added: groups 2 and 0) ([played](../playtest/logs/2026-11-22-ravager-rest.md)).
  Site 18, `rest_spells` (8CA82h, the rest's first move), is `REST_PRE`: the priests (classes 1-8 and
  19, the sheet's own levels) spend their slots left (DS:4474h + 22h a member + the level) through the
  rest's own free-cure cast (4787h:25h, 8D074h: spell, target, caster, level); the sequel's numbers
  (Neutralize Poison 178 on Poisoned 71, Cure Blindness 146 on Blind 10, Cure Disease 148 on Diseased
  27; Cure Light 117, Serious 170, Critical 194, Heal 210), the levels from its table at DS:0656h + 11.
  A priest knows every priest spell (the sequel has no spheres). A psionicist's Cell Adjustment (248) as
  SL's (`RP_PSI_CAST`: on the Diseased, then on the most wounded when no cure is left): known if its
  byte at 370h:9CDh + 22h a member + the power's place from 235 has bits 1-7 (the game's own test,
  5C340h), its cost the powers' table's (3D0h:7E0h, 3 bytes a power, +1: 5), taken from the creature's
  +2, cast at level 1 through the same free cast ([played](../playtest/logs/2026-11-22-ravager-rest.md)).
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
  are worked out) calls `GR_SHADOWED`, which finds a bigger one
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
  Heal (202) takes the target's Feeblemind entries out
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
`CHILL_UNDEAD`), test_dicelog's `ManualGroup3Tests`. Verified: [log](https://github.com/daaki85/darksun-obsidian-edition/blob/main/playtest/logs/2026-11-09-group-3.md).

### The monsters

(The research: playtest/logs/2026-11-09-group-4-research.md.)

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
  adds a Weakened's amount, 7B80Eh: Chill Touch's is -1, 79855h; a 1 raised STR, verified in play) for
  2d4 x 600 seconds
  with the power as its spell, and 5B8:7Fh (7B758h) works the target's abilities out again; AL made
  8 (no kind's bit) so 5C0:20h says no. 76442h always adds an entry (sorted by owner, a new handle),
  so hits add up; the ability routine takes each Weakened's amount off STR, at least 3. An effect of
  a spell 138 or more is a psionic power's upkeep only for a party caster (76883h), so the power as
  the spell is safe on a monster's.
- `TARI_BITE` (`tari_bite`, 7A747h, `cmp ax,1` after the d10 of 538:89h): a Tari's (`[bp-0Eh]` the
  attacker's creature, kind 40) 1 needs a d2 of 1 too (`GAME_DIE`): 1 in 20.
- `DJINN_TURN`: `PROBE_MOVE`'s end (57566h, the turn's movement: DI the combatant, SI its creature),
  a kind 39's first turn in a fight (`DJ_DONE`, the far block's `FAR_DJ`: a bit a
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

([In the features page](FEATURES.md#weapon-specialization); in full on [the weapon specs
page](WEAPON-SPECS.md).)

How: the chosen weapon types are kept in four bytes of each character's own
record that the game never uses (+14h to +17h), so saves and the
saved-characters roster keep them. Up to 2.12 they were a byte each (the kind +
1, 0 none); 2.13.0 and 2.13.1 packed them 5 bits each in +14h to +16h,
+16h's top bit (`SPEC_PACKED`) marking it; now (v2, +16h's bit 6 too,
`SPEC_V2`) the dword's bits 0-16 are the four as a base-17 number (each digit
the kind + 1, 0 none: `SPEC_KINDS_MASK`, room for 16 kinds); with Wake of the Ravager's six
kinds (22, `KIND_COUNT`) a value of `V3_BASE` (17⁴, past every base-17 number) or more is v3:
`V3_BASE` + the first kind × `REST_SETS` (1,794, the sets of up to three of 22) + the rank of the
set of the others (`REST_OFFSETS` for its size plus the combinatorial number system's sum:
`game.spec_rank`, DSCLOG's `SPEC_REPACK`), the first kept first (the starting weapon's, a Battle
Mage's), the others read back in order (`SPEC_UNPACK`), at most 124,572 in 17 bits; bits 17-21 the
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
they were. Verified in play (no log kept). DSCLOG adds the bonuses and attacks
where the game makes a weapon attack (`INT D1h`, `INT D0h`), on the DAM lines
(`INT CFh`, `INT CEh`), calls the game's psionic pop-up in weapon mode after
the creation screen's DONE (`CR_WEAPONS`, below) and at a level gained
(`INT C2h`, then `INT C1h` to `INT BCh` in the pop-up, window 3021), and prints
the Effects screen's lines (`INT BBh`).

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
character made after CHOOSE A SPELL too. (A Myrmidon's second is the polearm, the Loader's: `weaponchoice.kinds_for`.) The way back is a frame the overlay manager can patch, as
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
attacks a round are its item type's (+0Bh, in halves: a bow and darts 4, the rest 2),
not the character's (sheet +2Ah) as in melee; `INT D1h` raises them to a
specialist's (`MISSILE_RATE`, by the fighter, gladiator or ranger level, by kind:
the chatkcha, bow, sling and staff sling, kinds 13-16, and the javelin and darts, 21-22, `MISSILE_RAV`; a
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

### Weapon specialization in Wake of the Ravager

The party transfer keeps each character's specs (SL's +14h..+16h) at the
Loader's sheet +42h..+44h (`SPEC_SLOTS` in ravlog's layout), and DSCLOG2 reads
them with DSCLOG's `SPEC_GET` and `SPEC_ANY` (all three layouts). The sequel's
weapon attack routine (5CE80h) is SL's 58780h with its locals two bytes lower
(the attacks a round `[BP-0Ah]`, the dice `[BP-10h]`, the sides `[BP-12h]`, the
bonus `[BP-14h]`; `[BP+0Ah]` the THAC0, `[BP+10h]` the sheet, `[BP+14h]` the
type, `[BP+16h]` above 1 a missile, as SL's). `SPEC_ATTACKS`, called from
OFF_HAND at the attacks' store (5CEE8h, SL's PROBE_ATTACKS' site), and
`SPEC_DAMAGE` (site 51 at the strength bonus's `add [bp-14h],ax`, 5CF6Dh) do
what PROBE_ATTACKS and PROBE_SPEC_DAMAGE do; `SIZE_DICE` calls
`SPEC_GRAND_DIE` after AD&D's large dice. `SPEC_OF_SHEET` and `MISSILE_RATE`
are DSCLOG's on the sequel's sheet (race +12h, classes +1Bh, levels +1Eh),
the kits' parts with the kits' rules ([Kits in Wake of the
Ravager](DEVELOPMENT-KITS.md#kits-in-wake-of-the-ravager))
(`tests/test_ravspecialize.py` runs them against `specialize.skill` and
`missile_attacks`). The rule's bit is tested (`RULE_SPECIALIZE` in
`ravager.RULES_PORTED`), so `RAV_RULES_OFF=0x1000` makes a control run.

The kinds are SL's 22, DSCLOG2's `KIND_OF_TYPE` (`ravager.rav_kinds`, which
ravlog's layout makes `specialize.KIND_OF_TYPE` while the sequel is attached),
and `SPEC_GET` reads a V3 sheet's kinds 17-22 as themselves (2026-11-25: they
were folded onto the nearest of the first 16 before). The sequel's own weapons
of the six kinds SL took from it are of those kinds, by name, dice and the
two-handed bit (its item types' +0Bh 40h): the Twohand Sword (101) and the
Crystal sword (35, a long sword before), both two-handed 1d10, are two-handed
swords; the Lotulis (61), Double Spear (39), Trikal (100), Javelin (59) and the
two Darts (38, 43) their own kinds. None of the mod's types in the sequel
(102-134, SL's first 33) is of the six: SL's types of them (148 on) go across as
the sequel's own (`ravager.sequel_weapon_type`). With them: `MISSILE_RATE` has
DSCLOG's `MISSILE_RAV` (the javelin's and darts' rates of fire), `LARGE_DICE`
SL's 22 rows (the sequel's own weapons go by `RAV_LARGE` first, the Darts 38's
1d2 kept there), the Effects screen's `EF_KINDS` the six names, `PSI_KINDS`
DSCLOG's darts bit (a psionicist may use the Darts, as before, when they had
no kind; tested 32 bits wide), and a Military Scout's missile bonus outdoors
(`KIT_TO_HIT`) takes the bow, sling and staff sling alone, not the kinds past
them. The sequel's weapons with no kind of SL's count as the nearest for
specialization alone (DSCLOG2's `SPEC_KINDS_OWN`, `ravager.rav_spec_kinds`,
made `specialize.CONJURED_KINDS`), as SL's spell-made weapons do, so no
transferred warrior is left with the plain rate for want of a kind; their
restrictions and large dice stay as they were:

| The sequel's weapon (type) | Counts as | Why |
|---|---|---|
| Bloodletter (13) | long sword | A 1d8 blade |
| Promere hammer (81), Jasmine (68), Spirit hammer (95) | mace | A hammer, as SL's Spiritual Hammer; a mace's 1d6+1 |
| Shillelagh (90) | club | The spell's, as SL's |
| Rainbow (87) | bow | The Rainbow spell's bow |

The Net (71) and the Rock (94) have none.

## Kits

([On the Kits page](KITS.md).) The kits, and their switch, are on a page of their own: [DEVELOPMENT-KITS.md](DEVELOPMENT-KITS.md). In Wake of the Ravager: [Kits in Wake of the Ravager](DEVELOPMENT-KITS.md#kits-in-wake-of-the-ravager).

## Preservers' first spells

([In the features page](FEATURES.md#preservers-first-spells).) Always on, with
or without kits.

**On changing class** (every human, not a kit's): the routine
that changes a human's class, for a preserver (86DB5h), takes away its wizard spells and marks
Grease (8) and Magic Missile (7) known: `PROBE_DUAL_SPELLS` (`INT 9Ch`, new: those two `push /
push si / call 500:43h / add sp,4`, 22 bytes from 86DE4h) calls CHOOSE A SPELL (620:5Ch, 85560h:
the level up's) twice in their place, through its stub (`PICK_STUB`: DS less 4Ch, as `WP_STUB`),
with the spell levels on offer up to 1st (`PICK_CAP`, which `PROBE_PICK_LEVEL` heeds). The dual
routine is in CHOOSE A SPELL's own overlay (85560h to 87250h), so the call can't unload the code
it returns to. The same call from another overlay needs its way back where the overlay manager can
patch it: see the next one (at creation).

**At creation** (every preserver): the creation screen's DONE
(overlay 65480h) marks spells known by preserver level (`[BP-2]`, 66F2Dh on: 7 and 8 at 1st; 9 and
0Bh too at 2nd; 0Fh and 16h too at 3rd). `PROBE_CR_SPELLS` (`INT 98h`, new: `mov ax,[bp-2]`, 3
bytes) has a character made on the creation screen (the grants called from DONE, 66556h: their way
back at `[BP+2]`, `[BP+4]` is the INT's less `CR_FROM_DONE`, in the same overlay; START GAME with
no party made calls them for the game's own party from 65480h+6FBh, which keeps the game's spells,
and the creature's status can't tell the two, Okay in both) pick as many on CHOOSE A SPELL
(`PICK_SPELLS`: 2, 4, or 4 and two of 2nd level) and
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

## Psionic powers at creation

([In the features page](FEATURES.md#psionic-powers-at-creation).) Always on.

The routine that gives a new member its disciplines and powers (66CF1h, overlay 65480h, called
by the creation screen's DONE at 6654Ch, DI the member) sets the disciplines' words from the
panel's choice (DS:4980h; selector 2F0h, a word each, 7 bytes a member), clears all 34 powers
(4F8:43h) and gives a row of the game's table (selector 338h) through 4F8:3Eh(member, power):
a psionicist (`[BP-6]` 1) its level's (`+1Ch` + 11 x `[BP-2]`: 5 powers at 1st, 6 at 2nd, 11 at
3rd), anyone else its discipline's (`+6` + 11 x `[BP-4]`, 0-2: four of it and Mind Blank), in a
loop on SI (0-10) with DX the power or -1. A power's record (selector 408h, 8 bytes) has its
discipline at `+3` (bits 0-5; 40h a science, 80h a defence mode).

`PSI_GRANT` (a site of `INT 98h`, new: `cmp dx,-1`, 3 bytes at 66DDEh, its `jz` kept): for
DONE's call (the routine's way back, `[BP+2]` and `[BP+4]`, is the INT's less `PSI_FROM_DONE`;
START GAME's for the game's own party isn't) only Mind Blank (30) is given; each other power is
a pick due (`PSI_DUE`) and a default (`PSI_DEFAULTS`). It keeps the grant's far address
(`PSI_GRANT_CALL`, as the loader fixed it up). EDIT on the member with its own classes, race and
kit (`ED_SAME`) and disciplines (`PSI_SNAP` keeps them with its powers at `CR_OPEN`) gives none
and asks for none (`PSI_KEEP`).

`PSI_ASK`, called by `CR_WEAPONS` (after a warrior's weapon specs, or alone without weapon
specialization) in its frame the overlay manager can fix up, puts the member's powers back for
`PSI_KEEP`, or opens the psionicists' pop-up (620:57h, the level up's) for `PSI_DUE` picks: the
discipline shown (DS:9CE2h + the member) the member's own for one not a psionicist, the first for
a psionicist; `PROBE_PK_COUNT` lets it open (`PSI_MODE`) and `PROBE_PK_LEFT` puts the picks in
the window's count (DS:4AECh) as it is first drawn. The game's own picking does the rest: a
power clicked is given, the count one less, the window closed at none. `PSI_LIST` (`INT 98h`,
new: `or ax,ax / jz`, 4 bytes at 86143h, in the list of the discipline shown, 86107h) leaves out
a power known (the game lists it again, to raise its own number); `PSI_CYCLE` (`inc byte
[bx-631Eh]`, 4 bytes at 8631Ah, the discipline button) does nothing for one not a psionicist.
EXIT ("YOU HAVE MORE", EXIT) leaves the count above none: `PSI_ASK` gives that many of
`PSI_DEFAULTS`, in the game's order, less any known. A character dropped and added back from the
roster keeps the powers it picked.

## Level cap by XP

([In the features page](FEATURES.md#level-cap-by-xp).)

How: the game holds a class level against 9 in two places, where a character
goes up a level (87BE6h: the class's slot in DI, then `JL`) and where View
Character shows the XP for the next one (67D08h: its copy of the sheet, the
slot in DX, then `JZ`). While the rule is on DSCLOG's `PROBE_LEVEL`
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

In Wake of the Ravager (DSCLOG2, `ravager.py`'s `level_cap_*` patches) the game stops a class at
15th in the same two places (the level up's `cmp byte es:[bx+1Eh],0Fh` at 959A5h, then `JB`; View
Character's at 6FB51h, then `JE`), each a SITE of its own (110, 111), so nothing tells them apart by
the code after them. `LEVEL_ROOM` is SL's with `RAV_XP_CAP` (5,625,000, `ravager.RAV_XP_CAP`), the
sheet's classes mapped to rows by its own `class_rows` (the game's 360h:9Dh) and the XP from
`RAV_XP_AT`: `tables.RAV_XP` as dwords, levels 1-30 (`RAV_LEVELS`; the owner's AD&D tables past
the game's 20, 2026-11-25: no stop at 20th; the game reads its table through a resource load each
time, 5C8:20, so there is nothing in memory to read). Past the game's 20 entries its reads run on
into the next row, so `XP_NEED` (site 32, at all eight reads) answers `RAV_XP_AT`'s for an index of
20-29 with RULE_LEVEL_10 on, and the most from 30 (`xp_pasts` counts them). The level up holds the
sheet's XP to its table's entry 3 levels on (958C0h-95940h), so one award raises a class four levels
at most; from 27th that entry is past RAV_XP's 30, so `LV_CLAMP` (site 112, its `add ax,3`) makes the
index 29 and has `XP_NEED`'s next answer the most, which passes the hold by. At the same site `XP_HOLD` (the owner's, 2026-11-25: XP
stops growing at the cap) holds the sheet's XP at `LR_SHARE` first, so the game's hold, where it reads
the table, can only take it lower. `XP_SUFFIX` (117) is `PROBE_XP_NEXT` at View Character's
`push 1386h`. `LV_ORDINAL` (118) is the level up's "th" (`mov ax,2B7Eh`, 959D3h, the message's
ending for every level past 3rd): DS:2B7Eh, used nowhere else, made English's ending ("21st"). Past
20th the rest of the game copes: THAC0 is a byte read signed (`cbw`, 5C6E9h), but stops at High Level
Campaigns' Table 39 (the owner's, 2026-11-26): `PRIEST_THAC0` (site 33, run for every class group at the
THAC0 routine's "mov [bp-2],ax") holds what a group takes off 20 at `THAC0_MOST` (12, 19, 6, 9: a
priest's 8, a warrior's 1, a wizard's 14, a rogue's 11), and the routine keeps the best group's; a
preserver's CHOOSE A SPELL stops at 9th (`PICK_MOST`: `PICK_ANY`, `PICK_PAGE` and `PICK_TOP` heed it as
creation's `CR_CAP`) so the sequel's 10th-level spells (111-114) stay the monsters'; hit points the fixed gain past the rolled levels (94FF2h), the saves `SAVE_BASE`'s last row,
the slots `RAV_SLOTS` (30 rows a table), and the psionicists' pop-up (688:61h) lists known powers
too, a pick raising a power's number (selector 370h's 9CDh + 22h a member, bits 1-7), so 34 powers
never run out. A thief's d6 to 10th is `PROBE_HD_ROLL` and `PROBE_HD_CON` (113, 114) and a third site
(115) for the sequel's `mov` that keeps the levels after the compare. The saves (`SAVE_BASE`, 116,
RULE_HI_TABLES, SL's own `SAVE_BASE` the same since 2026-11-26, `dos/save_bands.inc`, a psionicist by Dark Sun's
table): the save routine (954D2h) is SL's (877EBh), save = the 1st level's less
min((level - 1) x rate / 100, the table's third byte), that byte AD&D's last save, not the most a save
improves; at its `mov al,es:[bx+6Ch]` the site gives the Handbook's save plus the game's improvement,
so the game's `sub` leaves the Handbook's less a dwarf's or halfling's CON bonus.

XP stops at the share too (the user's, 2026-11-25: XP banked past the top
level would carry over to Wake of the Ravager). That is the Loader's, so it
costs DSCLOG no memory: the dice log's party tracker (`tracker.py`,
`PartyTracker.hold_at_cap`) reads each party member's sheet at every look
(four times a second, out of a load and off the creation screen) and writes
the sheet's XP (+0, a dword) back to the share when it is above it, with a
line in the dice log (`Hal's XP held at the cap: 749,999 (12,345 not
counted)`; for a share below the cap, how it came about). The share is
`game.xp_share` (`tables.xp_share`), `LEVEL_ROOM`'s twin: the classes counted
as it counts them (any class byte), the cap divided with the remainder
dropped, a human's old classes (slots 1-2, a level above 0) taken off at the
XP table's entry before their level, never below 0; `test_dsclog`'s
`test_level_room_is_the_xp_share` runs `PROBE_LEVEL` in the emulator against
it for one class, several and humans who changed class, so XP held at the
share is at the top level or just short of it. The hold runs before the XP
line, so the line shows the gain that counted; the prime requisite bonus
stops at the share too (`_prime_bonuses`). Timing: an award lands at a
fight's end or from a script and the game may level up at once or at a rest,
before the Loader's next look; no level comes of XP above the share, since
`LEVEL_ROOM` caps the levels by the same share. A save made before this,
over the share, is held at the first look after it loads. Checked in the
game (playtest/logs/2026-11-25-xp-held-at-cap.md): a ranger and a
fighter/preserver set near their shares held at 749,999 and 374,999 through
the fountain ambush's kills; with the old Loader they went on to 750,690 and
375,293.

## STORE and RECALL on the creation screen

([In the features page](FEATURES.md#store-and-recall-on-the-creation-screen).)

With the `roll_store` switch off (gone now: [always on](#the-switches-always-on)), the Loader left both out: the buttons from
its copy of `RESOURCE.GFF` (`icons.write_resources`) and the click's patch from
its copy of `DSUN.EXE` (`gamepatch.ROLL_STORE`, as `EFFECTS_KEPT`).

The buttons: the creation screen is window 3011 in `RESOURCE.GFF`, its buttons
the die (7DAh), EXIT (80Ah), DONE (7D0h) and the rest. In the Loader's copy
(`dsloader/rollstore.py`) it has two more, STORE (8B0h) and RECALL (8B1h),
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
the frame follows. Without it, a RECALL before the die was rolled on that visit to the screen
could jump into what was no longer the die's routine, and DOSBox stopped ("DynrecCore: illegal option"). Verified in play (no log kept).

## New characters and the roster write

What the Loader gives a character made on the creation screen (its weapon specs' defaults and
starting weapon, `weaponchoice.finish_new`; `class_gear`; its kit's gear, `kit_gear`; [fuller
starting gear](#fuller-starting-gear), `startgear.fill`; its age) has to be in it before the
game writes it to the roster (CHARSAVE.GFF), which it does at DONE's end, after the weapon window
and the psionic powers (66E3h: 668C3h): else a character ADDed in a later session has the game's
gear alone. The handshake, DSCLOG's header fields with the Loader's names:

- `GEAR_DUE` (+1830, `TSR_GEAR_DUE`): set by `CR_WEAPONS` for a new member (after the weapon
  window's picks, the window always shown since weapon specialization's switch went; not for an EDIT
  that kept its race, classes and kit, `ED_SAME`); the dice log's `_gear_due` gives the gear at
  once and clears it, but leaves it set while the weapon window is up (`TSR_CREATING`: the gear
  waits for the specs).
- `GEAR_WHO` (+1867, `TSR_GEAR_WHO`): the new member's sheet index. The game keeps a character
  being made Okay, not New, until after the roster's write, so `game.being_new` counts this one New
  for `finish_new`, `class_gear`, `kit_gear` and `fill`. While the creation screen is up
  (`GameData.creating`) only that one counts: the other New record there is the screen's stand-in,
  whose items the game replaces at DONE, so it gets none (`test_dicelog`'s `test_being_new`).
- `GEAR_GIVEN` (+1831): the members whose items the pass changed, for `GEAR_WAIT` (PROBE_VIEW's,
  VIEW CHARACTER) to draw the screen again with them; `GEAR_HOLD` clears it once the gear is in.
- `LOADER_BEAT` (+1865, `TSR_LOADER_BEAT`): the BIOS timer at the Loader's last beat, written by
  the dice log's stats thread every quarter second (`BEAT_STEP`): how DSCLOG tells the Loader is
  there (STATS aren't kept on the creation screen).
- `GEAR_HOLD`, at `CR_WEAPONS`' end, before the roster write: with `GEAR_DUE` set and the beat
  fresh (`LOADER_FRESH`, about five seconds), waits until `GEAR_DUE` is cleared, at most about
  ten seconds (`GEAR_HOLD_TICKS`); with no Loader, on at once (the game's gear). `GEAR_WAIT` does
  the same on VIEW CHARACTER, a second at most, leaving `GEAR_DUE` set on a timeout.
- The Myrmidon's polearm spec is DSCLOG's own (`MYRM_POLEARM`, at DONE), so it is in the roster's
  copy with or without the Loader.

Verified: [log](https://github.com/daaki85/darksun-obsidian-edition/blob/main/playtest/logs/2026-11-15-kit-rebalance-checks.md) (part 7), [log](https://github.com/daaki85/darksun-obsidian-edition/blob/main/playtest/logs/2026-11-16-roster-gear.md).

## Fuller starting gear

([In the features page](FEATURES.md#fuller-starting-gear).)

`dsloader/startgear.py`'s `fill`, from the dice log after
`weaponchoice.finish_new`, `class_gear` and `kit_gear` (the `starting_gear`
switch, a Python-only one: `launch.SWITCH_DEFAULTS`,
`DiceLog.starting_gear`), for each party member whose status is New and who
has items (the game gives a character its gear when DONE is clicked; before
that it has none; one being made counts too: [New characters and the roster
write](#new-characters-and-the-roster-write)). What a character "can use" (`can_use`) is the game's class
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
for each. Verified in play (no log kept).

Their features of their own (with kits: `set_own`) go by a bit no character
made on the creation screen has: the kit byte's bit 6 (`kits.OWN_BIT`, DSCLOG's
`OWN_BIT`; bits 0 to 5 are the classes' kits, two each, and bit 7 Friends
known; every reader of a kit masks its own two bits), and which feature by the
race (`OWN_RACE_B`, `kits.own_race`; with `RULE_HI_KITS` only). Gerakis (the
half-giant): Wild Fighting, `wild.py` rolling for him as for a Wild Fury
(`kits.wild_fighter`), DSCLOG's effects going by the `KIT_WILD` bits alone.
K'ratchek (the thri-kreen): `SKY_LEVEL` and `PSI_KIT` as a Wasteland Seer's (`CR_OWN_RACE`),
no Effects line for the chatkcha (the rate is every thri-kreen's). `OWN_THROWS` in `PROBE_ATTACKS` (and the
inventory's `PROBE_MISSILE_LINE`) gives any thri-kreen (the sheet's race 8, foes too) 2 more halves a round with a chatkcha,
AD&D's 2/1, whatever the rules (`GameData.weapon_hits` the same). Cilla (the elf): `stealth.py`'s hiding not
halved in daylight (`kits.not_halved_by_sun`, as an Assassin's and a Military
Scout's). The Effects screen's lines are `OWN_LINES` (after the kits', in
`EF_LINES_OF`); the Characters tab's `GameData.kit` adds `kits.OWN_FEATURES`.
Verified in play (no log kept).

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

Verified in play (no log kept). A bought item stays on the pointer until it is put down
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
site over the push, with Shops as in AD&D, `RULE_HI_CHA_PRICES`, the second rules word's 16:
`game.RULE_BUYBACK` names it) looks at the thing's first item (things table, kind 1) and,
for one with a plus (`+14h` above 0) or a power (`+0Fh`), with the Loader there
(its heartbeat, `LOADER_BEAT` +1865, under `LOADER_FRESH` old, as for
`GEAR_HOLD`: with the Loader's window closed nothing would take the item off the
pointer, and up to 2.18 it was lost; now it is freed as the game does), pushes 270Fh in its
place (the registers kept, the interrupt's frame moved down a word, the word
under it) and queues the thing, the shop's merchant (`DS:179Ch`, the object
whose item lists the shop's list is built from at 8347Ah: Kalzith's map object,
229, a person, creature 33) and the item in the header (`SOLD_SEQ` +308 counted, `SOLD_Q`
+310, four entries, `SOLD_ITEMS` +1868 their items). The Loader (`buyback.py`, every quarter of a second,
the item gate held before it reads the queue) puts
each queued item, if the thing's list still starts with it (not one picked up
since), first in the merchant's last item list (a new one if it has
none; a backpack cell of its own), marks the entry seen to (its item 0FFFFh:
one left by a Loader that went away is seen to by the next, and a queue that
went round more than four times has what it still holds seen to) and zeroes the pointer's thing, as the game
leaves it (left a list, even an empty one, the inventory screen picks nothing up
after); a merchant that isn't a person (none known) has the item freed as the
game would. Bought back, it costs its price less the CHA discount, at least 60%:
no less than the shop paid (the same at CHA 25). Checked with the emulator (both
sites), unit tests (the move) and in the game: a Shield scroll (price 3000) sold
to Kalzith for 1,800 went first in his stock at 3000, and a Cloak (24) sold for
14 was gone, the inventory screen picking things up as before.

## Thief skills from AD&D's table

([In the features page](FEATURES.md#thief-skills-from-adds-table).)

How: where the game's thief skill routine adds 4 a level, DSCLOG
(`INT E4h`) puts AD&D's number for the level in place of the game's base and
level, adds the DEX table's, and jumps past the game's DEX formula to its
armour and effects. At the routine's end (`INT D9h`, below) DSCLOG keeps
the chance to 95 (`THIEF_MOST`). The Loader's screens and the inventory
screen's panel work the chances out the same way.

The game's equipment penalty on thief skills is gone whatever the switch: the
slots where anything brings it (the legs, the quiver and both hands) are a list
of words at the thief table's +D0h, ended by 13 (`game.THIEF_PENALTY_LIST`), and
the patched game empties it (`thief_slots` in `gamepatch.py`, DSUN.EXE 44F70h).
The Loader reads the list from the running game, so its numbers match whichever
game it is.

### A lock or a pocket failed: another try a level later

With the same switch. **Locks:** the game rolls open locks only in its scripts' skill check
(803B8h(character, skill, bonus): a d100 under [BP-2], the chance). One new site, `LOCK_SITE`
(`gamepatch` "lock_retry", 803D3h, "mov [bp-2],ax"), does the MOV, then for open locks by a party
member looks up the lock in `LOCK_BARRED` (its offset at DSCLOG's header +1844): for each member 0-3,
four (region, thing) word pairs, the thing being the one the running script was started on
(TALK_TARGET, 3781h:0365h from the load segment), the region the party's (DS:117Ch). A match makes the
chance `LOCK_NEVER` (-2000), which no roll is under. The dice log, seeing a party member's open locks
fail (PERCENT_SITE's entry), remembers it with the pockets tried (`locks.key`: the party, the region,
the thing, the member and its thief level; undone by loading an earlier save, as a pocket tried) and
each pass writes the table: the locks each member failed at the thief level it has now
(`locks.barred`). A level gained, the pair is gone. The dice log names a barred try ("failed this lock
at this thief level"). Verified: [log](https://github.com/daaki85/darksun-obsidian-edition/blob/main/playtest/logs/2026-11-11-lock-retry.md); tests:
tests/test_locks.py. **Pockets:** a thief caught (the pick and the move silently both
failed) is remembered as `pickpocket.caught_key` (the person's key, the thief and its thief level),
and that thief is refused until its thief level is higher (the game's message in the story: "Kurzak
remembers Daaki, and keeps a close hand on their purse.", which doesn't name the level; the reason
in the dice log alone). One who fumbled but slipped away unnoticed may try again at once. Tests: tests/test_pickpocket.py's `test_caught_with_thieves_as_in_add`,
`test_slips_away_with_thieves_as_in_add`.

## Hiding in shadows to backstab

([In the features page](FEATURES.md#hiding-in-shadows-to-backstab).)

How (the cloak, boots and belt): the patched game's item box (`INT DAh`, where
it has drawn the name) asks DSCLOG, which draws the line with the game's
own text routine when the item's type is worn as a cloak, on the feet or as a
belt; and at the end of the game's thief skill routine (`INT D9h`, where it
returns the chance, armour and effects counted) DSCLOG adds the belt's 5
to picking pockets and opening locks for a thief wearing one.

Daylight (`stealth.daylight`): an outdoor map (`stealth.OUTDOORS`) is all
daylight; on a map with buildings (`INDOOR_TILES`, the indoor floors' tile
numbers by region) it goes by the floor under the thief, read from the game's
map of the region in memory (the far pointer at `DS:2F4Ah`, `MAP_PTR`: a tile
number a square, 128 to a row); any other map is roofed.

How (the rolls): the Loader rolls both when the turn passes to the thief and
tells DSCLOG, which, where the game has just worked out whether an attack
is from behind and a backstab (`INT EAh`), makes the hidden thief's next one
so, by the game's own conditions for a backstab (a thief, in melee, a weapon
of weight 40 or less).

How many attacks: the attack routine multiplies when both backstab flags are set
and the round's count of attacks so far (`[BP-14h]`) is 1 or less (58A71h), so
the first two swings of the round, an off-hand one too. With the next rule only
the first is a backstab.

### A backstab multiplies the weapon's dice only

Part of Thieves as in AD&D (`thief_table`; `game.RULE_BACKSTAB` names it, `RULE_THIEF_TABLE`;
always on: [above](#the-switches-always-on)). The game's backstab multiplies the whole of a
hit's damage, STR's bonus and the weapon's plus included (x2 to x5 by thief
level, 595C4h); AD&D's multiplies the weapon's dice only, the rest added once,
and only the round's first attack is one. Two `NS_IMAGE` sites in the attack
routine (5883Ah):

- `STAB_ROLL` (`STAB_SITE`, 58A29h, `cmp word [bp+16h],1`, 4 bytes), just after
  the damage's roll: the dice's own sum (the damage less what the routine added
  to them, `[BP-12h]`) kept in `STAB_DICE` (`STAB_KNOWN` set), then the compare
  made and its flags handed back. It also tells `ENL_SITE` a melee hit's dice
  are known ([Enlarge](#enlarge-multiplies-the-weapons-dice-only), which comes
  between and multiplies those dice first, so a backstab multiplies the
  enlarged ones).
- `STAB_TIMES` (`TIMES_SITE`, 58A80h, the game's `push ax / mov ax,[bp-4] / pop
  dx / imul dx / mov [bp-4],ax`, 10 bytes, AX the multiplier): an Assassin's
  multiplier one more first (a party member, `kits.backstab_times`); then on
  the round's first attack (`[BP-14h]` 0) and a hit, the kept dice added again
  once for each time past the first; on the second, no multiplying at all; the
  dice not known, the game's multiplying of the whole.

The round's count `STAB_TIMES` reads leaves the off-hand swing out, so a thief
with three attacks (two weapons and a weapon spec's extra) had the third
multiplied after a first that missed: `STAB_FIRST` (in `PROBE_STEALTH`,
a party member only) keeps each member's last attack by the
game's clock (the dword through DS:9B72h's far pointer, a round at a time in a
fight, `STAB_CLOCK`), and a later attack at the same clock has its backstab
taken back (`[BP-24h]` cleared, its +2 to hit off THAC0 `[BP-20h]`); from
behind stays.

The attack routine (58019h) sets from behind and backstab (`[BP-1Ah]`,
`[BP-24h]`) once a call but runs all of a round's attacks in it, loading
`[BP-20h]` with the creature's THAC0 again for each and taking the 2s off only
when this attack is from behind (the target's facing, 582D0h): a flag left
from an earlier attack (a hidden thief's backstab) stayed set with no +2 on the
later one, and `STAB_FIRST` then gave back a 2 it hadn't had (Seneca's
Shadowseeker after her Hayneedle's backstab: THAC0 17 for 15, the target's DEX
and shield not counted, the dice log's `-2 STR` for her +2;
playtest/logs/2026-11-19-backstab-str-line.md). `REAR_FRESH`, first in
`PROBE_STEALTH`, clears a flag the game didn't pay for this time: the
creature's THAC0 (+1Fh) less `[BP-20h]` under 2, no from behind; under 4, no
backstab. Test: test_dsclog's `test_later_attack_flags_its_own`.

The dice log's damage line says it: `+10 backstab (the dice 5 x3 = 15)`
(`dicelog`'s backstab step, the round's count read from the attack's frame,
`parent_local(-0x14)`). Tests: test_dsclog's `test_backstab_dice`,
`test_backstab_first_attack_only`, `test_assassin_backstab`; test_dicelog's
`test_dice_only`, `test_enlarge_before_the_backstab`.

In Wake of the Ravager (DSCLOG2, `RULE_THIEF_TABLE` in `ravager.RULES_PORTED`): site 52 `THIEF_SKILL` at
the thief skill routine's 8C716h (SL's 80307h, the same 9 bytes; DEX `[BP-2]`, its "jc" to 8C795h) does
`PROBE_THIEF_SKILL` (`THIEF_ADND`, the tables in the resident part), `BELT_SITE` keeps the chance to 95,
`C_THIEF` shows the same on the inventory; site 53 `STAB_TIMES` at 5D11Bh (SL's 58A80h, the same 10 bytes;
the round's count `[BP-16h]`, the dice `ENL_ROLL`'s `ENL_DICE`, made the enlarged ones by `ENL_SITE`);
`STAB_FIRST` from `MISSILE_REAR` (the clock's far pointer DS:9C0Ch). With the kits (`RULE_KITS`) an
Assassin's multiplier one more there, rule or not (the attacker `[BP+0Eh]`, a party member: `kits.backstab_times`,
`kit_stabs` counts them). The dice log
reads the round's count at `game.ATTACKS_MADE_LOCAL` (ravlog's -16h). Tests: test_ravthief.py (with
`DSUN_WOTR`, the sites in the game's own code too); test_dicelog's `test_rule_off`,
`test_attacks_made_local`. Found statically (playtest/RESEARCH.md, "Thieves as in AD&D in the sequel").

## Picking pockets

([In the features page](FEATURES.md#picking-pockets).)

How (DSCLOG's PICK POCKETS, sites sharing `INT 98h`): the USE screen's Turn
Undead button (APFM 2BEFh, its handler 630h:48h) shows for a character whose
sheet's +12h holds a priest's element, its icon 3044 to 3047 by element. At
89979h (`PP_SHOW`), for a character with thief levels outside a fight, DSCLOG gives it an element past the game's cases (9) and its own icon, ICON
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
new spells (196 to 201) share those numbers, so for these two boxes DSCLOG leaves the box's spell test (8C64Eh, `NS_CMP_INFO`) as the game has
it; before, Turn Undead's showed a new spell's (Fogbolt's for an earth
cleric). The
next click on someone with that pointer (`PP_HAND`, 5ECD8h, the start of the
routine that opens the box to talk, trade or look) asks the Loader as
`PROBE_USE_ITEM` (`INT FDh`) does for an item used on the map: `USE_ITEM`
FF00h and the thief, `USE_WHO` the thing. The Loader rolls and moves the item,
and DSCLOG shows the result instead of the box. With no answer within
`PICK_WAIT` (the Loader held up, or the game busy with its lists) DSCLOG
goes on as the game would and marks the request answered (`USE_REPLY` =
`USE_SEQ`), so a late Loader does nothing (the same for spell arrows); its
wait counts the BIOS's ticks, so it runs with interrupts on. A known limit: the
Loader looks at the request once, at the start of its answer, so a timeout
that falls while it is already moving the item (half a second or more inside
one pick) lets the game's own handling run alongside; a claim word the Loader
set before acting, which DSCLOG waited on, would close it ([unverified](DEVELOPMENT.md#unverified)). The pointer turned to
another mode puts the try away (`PROBE_POINTER`). Verified in play (no log kept).

A cleric/thief (a priest's element and thief levels) keeps Turn Undead on its
button and has the purse beside it (`PP_EXTRA_DRAW`), outside fights: the
panel's empty slot APFM 2BE7h (index 1Ah of the spells' 2BCDh), given Turn
Undead's handler (530h:43h, through the stub segments), its frame and the
purse drawn as the game draws Turn Undead's (630h:4Dh, 896BCh) with an icon
of its own loaded (100h:4A4h) and let go of as the screen closes (`PP_CLOSE`,
88504h). These calls may load overlays, so they are made in a frame the overlay
manager can fix up. The handler tells the two by its button ([BP+8]); another
character on show takes the slot's handler off, and the game's redraw clears
it. Verified in play (no log kept).

Who has caught a thief, or given up their coins, the Loader keeps in `settings.json`, for this
party, with the time on the game's clock of the try: a game loaded from before it has the clock
behind that time, so the try is forgotten.

**In Wake of the Ravager** (DSCLOG2's PICK POCKETS, sites 180-186; header words from +2000): the same purse in Turn
Undead's place on a thief's USE screen out of a fight, at the sequel's addresses (`ravager.PATCHES` pp_show to
pp_hand; the show routine's element test 97AF4h, the handler 9756Eh's pressed byte, icon reads, "push dword
132FFFFh" and name, the talk routine 630F0h's start). The sequel's look pointer is mode 2, so the armed pick is
DSCLOG2's own flag (`pp_armed`), put away by a right click (`pp_disarm` in probe_pointer). The answer comes from
`RavDiceLog._answer_pick` through its own request words (+2002 seq, +2004 reply, +2006 who, +2008 thief, +2010
taken, +2012 the text's offset, +2018 late), not USE_ITEM, and shows in the game's message window from the overlay
frame. The Loader's `pickpocket.attempt` runs as in SL, with `pocket_sized` bound to `ravlog.rav_pocket_sized`: the
sequel's item types carry no weight, so pockets are judged by kind (no armour or shield, a weapon of 4 damage or
less). Not ported: the cleric/thief's second button, the right click's description box, the sounds, XP for lifted
weapons. Tests: test_ravpickpocket.py. Played: playtest/logs/2026-11-26-ravager-pick-pockets.md.

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
one with a descriptor of its own, and puts the entry back. Two header words ask for
them: `SOUND_REQ` (+1822: played from the map's main loop, `SOUND_TICK`) and `PICK_SOUND` (+1824:
played with the pick's text, `GIVE_XP`). A Spellarcher making spell arrows hears the spell's own
cast sound (its spell record's +0Fh, `spellarrows.cast_sound`), through `SOUND_REQ` too. Seen in
DOSBox (2026-11-05, its output recorded with `PT_AUDIO` and matched with the clips: r 0.995 to
0.997): both on request, in either order and after one of the game's, entries 131 and 132 as the
game had them afterwards, and from a real pick and a real hide. Tests: `test_sounds.py`,
`UseItemTests.test_sound_tick`, `test_pick_sound`.
