# Development: the kits

*Part of the [development notes](DEVELOPMENT.md). How each kit is done: where the patched game calls
DSCLOG and what the Loader reads and writes. The player's page is [Kits](KITS.md).*

## Contents

- [The kits](#the-kits)
- [The kit's byte](#the-kits-byte)
- [Choosing one](#choosing-one)
- [Multiclass kits](#multiclass-kits)
- [Where each effect goes](#where-each-effect-goes)
- [Spell arrows](#spell-arrows)
- [Kits in Wake of the Ravager](#kits-in-wake-of-the-ravager)
- [How they're checked](#how-theyre-checked)

## The kits

What each kit gives and costs is in [the Kits page](KITS.md). A kit is chosen for a class when a
character is made, or by a human with none when it changes class (one kit a character): three for
each class, or none (the class as it is). The **Kits** switch on the Options tab
(`game.RULE_KITS`, bit 0 of DSCLOG's second rules word, `RULES_HI` at the header's +270) switches
them all off.

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

## The kit's byte

Sheet `+43h`: zero in every sheet of the saves and saved characters at hand
(176), and nothing in DSUN.EXE reads or writes it (no `es:[bx+43h]` access of
any kind), as with the weapon specs' `+14h` to `+17h`, which saves and the
roster keep. `+45h` is the Elementalist's second sphere (`SPHERE2`, [below](#where-each-effect-goes)).
In `+43h`, two bits a class place (0: no kit; 1 to 3 the class's kits), 40h `OWN_BIT`, 80h
Friends known, FFh `KIT_OPEN` (DEVELOPMENT.md's sheet table has the same).

## Choosing one

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
DSCLOG, so the INT's way back is in a frame the overlay manager can patch,
as for `PROBE_LV_PICK`. Calling 7E620h alone draws the contents without the
background: the pages' text lands on top of each other.

The panel follows the classes as they change. A class click runs
`PROBE_WP_CLASS`: the disciplines' window opened again if it isn't the one for
the class now; KITS pressed for a character with no kit class goes back as
VIEW PSIONICS does. A new race or sex empties the classes, has the panel
opened for no class, then puts the default class in without a click:
`PROBE_RACE_PANEL` (`INT 89h` at 63403h, after that call) opens the disciplines'
window again for the class put in.

## Multiclass kits

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

The Loader writes two things to DSCLOG's header for these kits: at `+350`
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
and clears as the dances end: bit N, member N fights wild (its penalties, whatever the
check); bit N + 4 as well, its check passed (its gains).

## Where each effect goes

A kit has one number (the creation class × 4 + the kit: `kitpages.KIT_IDS`). A
human may have a kit for each of its classes (up to three), so every rule asks
whether the sheet has a given kit awake: `KIT_IS` (kit in AL; `KIT_HAS` asleep
too), or inline, `call kit_is_b` / `db KIT_X` for a sheet at ES:BX, `cr_is`
for a creature (AX), `cb_is` for a combatant (`[BP+6]`); each leaves the kit's
class's place in `KIT_WHERE` for `KIT_LEVEL` and `KIT_CLASS_OF_SHEET`. Rules
that several kits touch (AC, THAC0, slots, saves, to hit and damage, cures)
take each kit's part in turn. Each effect has its twin in `kits.py`, which the
Loader and the dice log use (once for each kit in `kitpages.kit_ids`), and
emulated tests hold DSCLOG to it. Each effect, where it goes in the game (the
bullets after the table name the kits):

| Effect | Probe |
|---|---|
| damage with a weapon | `PROBE_SPEC_DAMAGE`, `PROBE_DAM_LINE`, `PROBE_VIEW_DAM` |
| to hit | `PROBE_ATTACKS` (`KIT_TO_HIT`) |
| AC | `PROBE_AC` (`KIT_AC`) |
| movement | `PROBE_MOVE` |
| spell slots | `PROBE_SLOTS`, `PROBE_SLOT_LEVEL` |
| spells learnt | `PROBE_LV_PICK` (`LV_SCHOLAR`), `KIT_MADE` in `PROBE_CR_SPELLS`, `PROBE_DUAL_SPELLS` |
| a power's PSP | `PROBE_PSP_USE`, `PROBE_PSP_TABLE`, `PROBE_PSP_DEFENCE` |
| a cure's healing | `PROBE_CURE` |
| a spell's damage | `AV_CAUSE`, `HARM_SITE`, `WANDER_DMG` |
| healing spells never known | `PROBE_EL_KNOW` (`AV_KNOW`), `AV_GRANT` |
| harming spells never known | `PROBE_EL_KNOW` (`AV_KNOW`'s `AV_HARM`), `AV_GRANT`, `NS_PRIEST_KNOWS` |
| casting level | `PROBE_RANGER_CAST`, `PROBE_CAST_LEVEL`, `PROBE_SPELL_LEVEL` |
| wizard spells for a thief | `PROBE_SLOTS`, `PROBE_PICK_ANY`, `PROBE_PICK_LIST` |
| a power's PSP to keep it up | `PROBE_PSP_KEEP`, `PROBE_PSP_KEEP_DX` |
| the off hand | `PROBE_CAN_USE` (`KIT_FORBIDS`) |
| casting though hit | `PROBE_HIT_ROUND` |
| a wizard spell's level, 1 more | `PROBE_SPELL_LEVEL`'s `ARC_LEVEL` |
| THAC0 | `PROBE_THAC0`; a warrior's, `WAR_HIT` |
| initiative | `PROBE_INIT` |
| to hit with a missile | `PROBE_ATTACKS` (`KIT_TO_HIT`) |
| a hit's poison | `PROBE_POISON` |
| an arrow's plus | `PROBE_ARROW` |
| the Fine Bow's +1 to hit | `FINE_HIT` (`PROBE_ATTACKS`), `IB_MATERIAL` |
| a priest spell's level | `PROBE_SPELL_LEVEL` |
| saves | `PROBE_RING_SAVE` |
| thief skills | `PROBE_BELT` |
| from behind, backstab | `PROBE_STEALTH` (`KIT_REAR`) |
| shields | `KIT_FORBIDS` |
| light armour only; no armour at all | `KIT_LIGHT` (its `BARE`) |
| hiding, moving silently | `stealth.py` |
| the two-weapon penalty | `PROBE_TWO`, `RG_TWO` |
| gear forbidden or allowed | `PROBE_CAN_USE`, `KINDS_ALLOWED` (`KIT_FORBIDS`, `KIT_ALLOWS`) |
| weapon specs and skill | `SPEC_OF_SHEET`, `KINDS_ALLOWED`, `LV_DUE` |
| attacks a round | `EXPERT_HALVES` |
| hit die | `PROBE_HIT_DIE`, `PROBE_CR_DIE` |
| max PSP | `PROBE_MAX_PSP`, `PROBE_CR_PSP` |

How each is done:

- **Damage with a weapon.** Ravager, Brute, Ghetto Fighter (melee: `KIT_MELEE`, by the item type;
  the Ghetto Fighter's a dagger's kind), Battle Dancer and Wilderness Avenger (melee or missile:
  `KIT_EXTRA`, the dance's `KIT_DANCE` byte, or the Avenger's 1 against anything), Arena Champion
  (melee, a shield in a hand: `KIT_CHAMPION`, by `PROT_SCAN` of the attacker's thing, `[BP+18h]`),
  Wild Fury (Wild Fighting passed: +3, melee or missile, `WILD_PASSED`). Where: `PROBE_SPEC_DAMAGE`
  (`KIT_ATTACK_DAMAGE`), and the DAM lines (`PROBE_DAM_LINE`, `PROBE_VIEW_DAM`: `KIT_MELEE` only).
- **To hit.** Ravager, Brute, Ghetto Fighter (and 1 worse with anything but a dagger), Arena
  Champion, Sentinel (melee without a shield in a hand: −1, `KIT_CHAMPION`), Battle Dancer, Wilderness Avenger, Wild Fury (fighting wild, passed or failed: −3, `WILD_TO_HIT` by
  `KIT_WILD`'s bit N). Where: `PROBE_ATTACKS` (`KIT_TO_HIT`: `KIT_CHAMPION`, `KIT_EXTRA`, and `KIT_MELEE` in
  melee).
- **AC.** Ravager (`RAVAGER_AC` by level against the sheet's base AC, `+27h`), Wanderer, Sentinel
  and Arena Champion (a shield in a hand: `PROT_SCAN`), Grove Warden, Battle Dancer (its dance:
  `KIT_DANCE`), Wild Fury (fighting wild, passed or failed: 3 worse, no worse than 10, `KIT_WILD`'s bit N). Where:
  `PROBE_AC` (`INT 62h`, the end of the AC routine: `KIT_AC`).
- **Movement.** Stalker, Rescuer (2 more). Where: `PROBE_MOVE` (`KIT_MOVE`).
- **Spells learnt.** Scholar: one more at each level up (`PROBE_LV_PICK`'s `LV_SCHOLAR`: the game's
  CHOOSE A SPELL once before its own), one more for each level at creation (`KIT_MADE` in
  `PROBE_CR_SPELLS`' count) and on changing class to preserver (`PROBE_DUAL_SPELLS`).
- **Spell slots.** Battle Mage (−1 wizard), Crusader (−1 priest), Seeker and
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
  `GAME_DIE`; and Cell Adjustment a d4 more, `CELL_SITE`, `kits.CELL_MORE`, the die in `MN_CELL`'s
  last word's high byte for the dice log), Rescuer (as the Healer; the Healer's and Rescuer's Cell
  Adjustment 1 more, `CELL_PLUS`, the high byte the same). Where: `PROBE_CURE` (`INT B1h`, new: "nop / push cs" at
  DSUN.EXE 79619h in the handler for spells with rules of their own, where the healing, pushed with
  the target, goes to the routine that heals; the caster its `[BP+8]`, the spell `[BP+0Eh]`; the
  probe pushes CS itself). The Cell Adjustment's jump into 79618h is clear of it.
- **A spell's damage.** Wilderness Avenger (+1 a die of Cause Light, Serious, Critical Wounds:
  spells 72, 113, 128). Where: `AV_CAUSE`, from `AREA_DMG` (754ECh, "mov [bp-12h],ax" where the
  routine dealing a spell's damage to the creatures it reaches, 7511Bh, the Cause spells' way too,
  has rolled it, DI the spell; a helpless target's at `[BP-14h]`) and `HARM_SITE` (761A9h, the
  one-target routine's, `[BP-8]`): when `CAST_SITE` last saw that spell cast by an Avenger
  (`CAST_WHO`, `CAST_SPELL`), the bonus on the damage and on a helpless target's; the dice log's
  `_harm_bonus`, by the last `KIND_CAST`. And the Wanderer (half of a spell all fire or all cold, as Resist Fire and Resist
  Cold). Where: `WANDER_DMG` (an `NS_IMAGE` site: "test [bp+0Ch],di" at DSUN.EXE 7B56Fh, in the
  routine giving the share of a spell's damage a creature takes, 7B492h, where DI holds the kinds
  its effects guard it from; fire and cold added for a Wanderer); `GameData.damage_halved_by`.
- **Healing spells never known.** Wilderness Avenger (Cure Light, Serious, Critical Wounds, Blood
  Flow; Heal and Water of Life). Where: `AV_HEAL`'s list in `PROBE_EL_KNOW` (`AV_KNOW`: as a
  character is made, the spell its place in the table / 7; a level up marks none) and `AV_GRANT`
  (5E499h, "test es:[bx+19Dh],edx" in the routine giving a priest its spheres' spells, 5E401h, no
  caller found: guarded as `PROBE_EL_GRANT` guards it; a site of `INT 98h`: ZF set for them, so they
  aren't learnt); the 6th-level two in `NS_PRIEST_KNOWS` (no mask for an Avenger). One made with
  2.10.0 or earlier, with them known: `kits.avenger_heals` marks them not known when the save is
  loaded.
- **Harming spells never known.** Healer, Lifebinder (Cause Light, Serious and Critical Wounds, 72,
  113, 128; Cause Disease, 97; Poison, 119; Slay Living, 136: `AV_HARM`, `kits.NO_HARM`; and Harm,
  `NS_PRIEST_KNOWS`). Where: as the Wilderness Avenger's healing spells (`AV_KNOW`, `AV_GRANT`); one
  made with 2.17 or earlier has them taken away by the Loader (`kits.avenger_heals`).
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
  level](DEVELOPMENT-RULES.md#rangers-casting-level) rule). `kits.ranger_cast_drop`, `kits.cast_level`,
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
  A scroll: see [Preservers' INT](DEVELOPMENT-RULES.md#preservers-int). Armour: the game has no armour rule for a single
  class's spells (the multiclass preserver's is the class restrictions'), so it casts in the light
  armour it may wear.
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
- **A wizard spell cast a level higher.** Arcanist (its preserver spells' duration and damage, the
  new wizard spells too; not the spell levels it may cast). Where: `PROBE_SPELL_LEVEL`'s `ARC_LEVEL`
  (`kits.arc_level`), as the Spirit Caller's `SKY_LEVEL`. (Vectors 93h-96h are free.)
- **THAC0.** Scholar (1 worse). Swashbuckler, Crusader, Battle Mage, Mind Warrior: a warrior's (21
  less the kit's level, where better) with the kit's chosen weapon spec alone (without weapon
  specialization, its kinds), on the attack: `WAR_HIT` in `PROBE_ATTACKS`, from the creature's
  `+1Fh`. Where (the Scholar's): `PROBE_THAC0` (`INT B7h`, new: the end of the game's
  THAC0 routine, `mov ax,14h / sub ax,si` at DSUN.EXE 876BBh, which every write of a creature's
  THAC0, `+1Fh`, uses: on making a character, 66CE0h, and at a level up, 86D7Eh and 87A91h).
- **Initiative.** Military Scout (its `KIT_OUTDOORS` bit); Myrmidon (2 less). Where:
  `PROBE_INIT` (`INT B8h`, new: the round's 20 added at DSUN.EXE 5750Eh). And the Wayfinder (Path-finder: each party member 1 more while a Wayfinder of
  the party is New or Okay, `PATH_UP`, and the Wayfinder's own 2 more, `WAYFINDER_INIT`,
  `kits.WAYFINDER_INITIATIVE`). Where: `PROBE_INIT`; `GameData.path_finder`.
- **To hit with a missile.** Military Scout (a bow, sling or staff sling, its `KIT_OUTDOORS` bit: `kind_of_type`
  14 to 16, not the javelin's or the darts' past them, which once had it too, 2026-11-26).
  Where: `KIT_TO_HIT` in `PROBE_ATTACKS` (`kits.missile_to_hit`).
- **A hit's poison.** Poisoner (each hand's melee weapon's first hit in a fight: `POISON_USED`, the
  header's +1860, bit N party member N's main hand, N + 4 its off hand, cleared by the Loader as a
  fight starts; the hand `KIT_OFF`, +1861, bit N set by `NOTE_SHOT` for a melee attack with the
  weapon in the left hand, its item's +11h 10; the header's +360, `KIT_SHOT`, bit N party member
  N's last weapon attack a shot or a throw: set or cleared by `NOTE_SHOT` in `PROBE_ATTACKS`, from
  the weapon attack routine's `[BP+16h]`, above 1 for a missile). Where: `PROBE_POISON` (`INT 86h`, new: the `jmp 7A7C5h` at DSUN.EXE 7A6DDh, in the
  routine giving a hit's special effects, 7A539h, where a person who isn't a thri-kreen has none; DI
  the attacker, SI the target, `[BP-6]` the attacker's creature, `[BP+12h]` the spell or power
  behind the damage, -1 for a weapon's): for a melee weapon hit only (`KIT_SHOT`'s bit clear; the
  poison's own damage, power 176, comes back through this routine with the Poisoner as its attacker,
  and would poison again, hit after hit) it queues power 176, the monsters' "poison (10 damage)",
  through the routine a monster's poisoned hit uses (790D2h: target, attacker, power, level; the
  level from 508:2Ah, whose far call is at 7A7ACh), then jumps on. The game rolls the save
  (paralysis/poison/death) and deals the damage.
- **An arrow's plus.** Spellarcher (its spell arrows from a bow: +1 from 5th preserver level, +2 from 9th, `ARROW_PLUS_NOW`; other arrows as they are). Where: `PROBE_ARROW` (`INT
  85h`, new: `mov es:[0006h],al`, DSUN.EXE 58D27h, in the routine finding a missile weapon's
  ammunition, 58C8Fh, `[BP+0Ch]` the weapon's type): `ES:[6]` is the plus the shot's damage adds
  (58992h) and its +1/+2/+3 damage kinds take where better than the bow's (581C4h). The shooter is
  `WHOSE_TURN`'s combatant; `kits.arrow_plus`. The weapon spec: `KINDS_ALLOWED` gives a Spellarcher
  the bow only, the one weapon spec the window after DONE offers it.
- **The Fine Bow.** Spellarcher (its starting bow, The Complete Fighter's Handbook's fine quality: +1
  to hit, not magic; the spell arrows themselves: [Spell arrows](#spell-arrows)). `weaponchoice.kit_gear` calls `spellarrows.starting_gear` for a new
  Spellarcher: its bow (the weapon rules' bow, or a plain one) is renamed Fine Bow (name 173h,
  `game.FINE_BOW_NAME`, DSCLOG's 50th extra name), and arrows go in by the touch spells it knows
  (the game's known table, `spellarrows.knows`): 24 Chill Arrows for Chill Touch, 24 Shocking
  Arrows for Shocking Grasp, both stacks for both (the first in the quiver), the plain arrows taken
  away; with neither, 24 plain ones. Once: none if it has its Fine Bow. `FINE_HIT`, in
  `PROBE_ATTACKS` after `WAR_HIT` (both it and `IB_MATERIAL` look the name up through `FINE_ITEM`), takes 1 off the attack's THAC0 when the item at `[BP+12h]` is
  named Fine Bow (whatever the rules); `IB_MATERIAL` shows its item box "Hit +1"; the Loader's THAC0
  for each weapon (`game.weapon_hits`) and the dice log's THAC0 line have it as "+1 fine". Bows
  never break and take no material penalty (their type's flag 80h), so nothing else is needed.
- **A priest spell's level.** Spirit Caller, Wasteland Seer (2 more under the open sky, 1 less under
  a roof, no less than 1). Where: `PROBE_SPELL_LEVEL`'s `SKY_LEVEL` (`kits.sky_level`): the level a
  spell's duration and damage take, not the levels it may cast.
- **Saves.** Myrmidon (charms), Sentinel (spells, 0-137), Wanderer (fire and cold: the spell
  record's `+1Ah`, 2 or 4, as the game's Resist Fire and Resist Cold read it). Where:
  `PROBE_RING_SAVE` (the modifier routine's start: `KIT_SAVE`).
- **Thief skills.** Assassin (pick pockets, open locks), Shadowblade, Ghetto Fighter, Wayfinder
  (`KIT_SKILLS`, a signed byte a skill), Military Scout (+10 or −5 by its `KIT_OUTDOORS` bit),
  Swashbuckler (its bad luck: a d26 less 1, 0 to `BAD_LUCK` 25, off each roll, from the game's
  rand() seed, kept in the header's `BAD_LUCK` and `BAD_LUCK_WHO`, +1862, for the dice log;
  `kits.bad_luck` for the Loader's own rolls, pickpocket.py and stealth.py; the skills shown,
  `thief_skills_now`, without it). Where: `PROBE_BELT` (the
  thief skill routine's end, the chance a roll is held against: `KIT_SKILL`, no lower than 0).
- **From behind, backstab.** Military Scout (a backstab taken back: `[BP-24h]` cleared, its 2 to hit
  with it), Rescuer (from behind +1, not +2); Assassin (a backstab's multiplier one more, x3 to x6:
  `STAB_TIMES`, `kits.backstab_times`). Where: `PROBE_STEALTH`'s `KIT_REAR` (`kits.backstabs`,
  `kits.rear_to_hit`), after the game's own setting of `[BP-1Ah]` and `[BP-24h]` and the stealth
  rule's; the backstab flag is pushed for the attack after it (DSUN.EXE 5838Ah).
- **Shields.** Shadowblade, Ghetto Fighter, Rescuer. Where: `KIT_FORBIDS` (`kits.forbids`).
- **Light armour only.** Assassin, Shinobi, Shadowblade, Poisoner (awake only: asleep after a change
  of class the limit sleeps with the kit, `KIT_FORBIDS` testing `KIT_AWAKE` first); the Spellarcher no armour, helm or shield at all (`BARE`: bracers, robes and a cloak of protection aren't armour; `kits.BARE_KITS`), and its class's armour left behind at creation (`weaponchoice.kit_gear`). Where:
  `KIT_LIGHT` (`kits.LIGHT_KITS`).
- **Hiding, moving silently.** Stalker, Assassin and Military Scout (not halved in daylight:
  `kits.not_halved_by_sun`), Wilderness Avenger (a ranger's, 5 a level of its best class),
  Shadowblade (hides with an enemy beside it). Where: the stealth rule's rolls (`stealth.py`,
  `GameData.ranger_skill_parts`).
- **The two-weapon penalty.** Twin-blade, Battle Dancer (in light armour: `HEAVY_WORN`); Justifier
  (in any armour); Ghetto Fighter (2 less in each hand). Where: `PROBE_TWO`; `RG_TWO`.
- **Gear forbidden or allowed.** Forbidden: Ravager, Twin-blade, Brute, Stalker, Grove Warden, Lifebinder, Shinobi, Battle
  Dancer (no shield; `kit_dancer`: long sword and bow kinds), Shadowblade, Ghetto Fighter and
  Rescuer (no shield), Seeker and Grove Warden (its sphere's weapons, as a cleric's: `SPHERE_ALLOWS`
  with `CU_*` set from the item type, `KF_SPHERE` the kit's class less 1, mod 4: the ranger's or
  druid's, the bow too; a Seeker has no ranger's bow expertise either,
  `SPEC_OF_SHEET`'s `.rbow` path passing it over, `specialize._skill`); the Twin-blade the
  cahulaks, two-handed as they are, and the Brute not (`KF_CAHULAKS`, `kits.forbids`' `cahulaks`:
  the type in `game.CAHULAKS_TYPES`). A missile weapon the kit forbids goes into the backpack at
  creation (`weaponchoice.kit_gear`: a fire Seeker's bow). Where: `PROBE_CAN_USE` and
  `KINDS_ALLOWED` (`KIT_FORBIDS`: `restrict.kit_forbids`; and `KIT_ALLOWS`, so a Battle Dancer may
  specialize in the long sword whatever its cleric's sphere), whatever the class restrictions. For
  an EXIT on the weapon window after DONE, `weaponchoice.kinds_for` makes a Ghetto Fighter's or
  Poisoner's spec the dagger and a Battle Dancer's the long sword, if allowed (`kits.default_kind`);
  `weaponchoice._ghetto_dagger` puts a dagger in a Ghetto Fighter's hand. Allowed past the class:
  Battle Mage (its chosen weapon type's weapons, with weapon
  specialization; light armour); Battle Dancer (long swords and bows, `kit_dancer`, whatever its
  cleric's sphere). Where: `KIT_ALLOWS` in `PROBE_CAN_USE`: an item the game's class mask refuses is
  let through (AX 1), and the class restrictions pass it; `KIT_FORBIDS` still holds (nothing in a
  Battle Mage's off hand). `kits.allows`, `restrict.kit_allows`. The game has no armour rule for a
  single class's spells, so it casts in that armour.
- **Weapon specs and skill.** Justifier (expertise with its chosen weapon type becomes
  specialization; the bow, not chosen, stays every ranger's expertise). Where: `SPEC_OF_SHEET`'s end: `SPEC_EXPERT` made `SPEC_SPECIAL` for a
  Justifier, the ranger's bow path (`.rbow`) jumping past it; `specialize.skill`. Myrmidon (two, both to grand mastery: the first its own, any but the polearm,
  `KINDS_ALLOWED`'s `MYRM_POLEARM`, `restrict.allowed_kinds`; the second the polearm, given by the
  Loader, `weaponchoice.kinds_for`, `kits.POLEARM`, and by DSCLOG's `MYRM_POLEARM` at DONE, after
  the weapon window: the game writes the roster's copy then, before the Loader's changes), Brute (no missile spec), Battle
  Mage (one, of `KIT_BM_KINDS`: expertise), Spellarcher (the bow only), Poisoner (the dagger or
  short sword only: `KIT_POISON_KINDS`), Crusader and Mind Warrior (one, of its class's melee kinds:
  `KIT_MELEE_KINDS`; a thri-kreen Mind Warrior the chatkcha too, `KIT_KREEN_KINDS`, the race byte
  +18h, `kits.KREEN_WARRIOR_KINDS`). Where: `SPEC_OF_SHEET` (a Battle Mage's chosen weapon type
  `SPEC_EXPERT`), `KIT_FORBIDS`, `KINDS_ALLOWED` (a Battle Mage its own weapon types, whatever its
  class), `LV_DUE` (a Battle Mage one), so DONE's weapon window
  (`CR_WEAPONS`) asks a Battle Mage as it asks a warrior.
- **Attacks a round.** Wild Fury (Wild Fighting passed: 1 more in melee, `WILD_HALVES`, in
  `PROBE_ATTACKS` before the off hand's cap; not on the DAM lines); Battle Mage (its chosen weapon
  type: expertise, 3/2, 2 from 7th preserver level); Crusader and Mind Warrior (the chosen weapon
  spec's expertise is the kit's extra attacks: weapon specialization is always on, and the
  warrior's extra attacks they had without it, DSCLOG's `WAR_KIT_HALVES`, went with its switch;
  `kits.warrior_attacks` still has them for `spec=False`). Where: `EXPERT_HALVES` where
  `PROBE_ATTACKS`, `PROBE_DAM_LINE` and `PROBE_VIEW_DAM` leave a non-warrior's (2 halves or fewer)
  alone; `specialize.expert_attacks`. Verified: [log](https://github.com/daaki85/darksun-obsidian-edition/blob/main/playtest/logs/2026-11-15-kit-rebalance-checks.md).
- **Hit die.** Battle Mage (d6), Arcanist (d3). Where: a level's die: `PROBE_HIT_DIE` (`INT A5h`,
  new: `mov al,es:[bx+0]`, 87308h, the die read from the class's hit point group in the routine
  rolling a level's hit points, 87250h, which both a level up and the creation screen call; `[BP-4]`
  the sheet). The creation screen's range (the least and most hit points it allows, `DS:[4998h]` and
  `[4996h]`, worked out with the rolls by 655D6h): `PROBE_CR_DIE` (`INT A3h`, new: `mov
  al,es:[bx+14Ah]`, 65677h, the die from its table by creation class). `kits.hit_die`.
- **Max PSP.** Mind Warrior (a fifth fewer, rounded down: `kits.MIND_PSP`). Where: at a level up: `PROBE_MAX_PSP`
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
| starting gear fitted to the kit | Ravager, Brute, Shinobi, Seeker, Shadowblade, Ghetto Fighter, Rescuer, Arena Champion, Poisoner, Battle Mage, Battle Dancer, Myrmidon, Spellarcher | `weaponchoice.kit_gear`, `spellarrows.starting_gear` |
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
  human who changed class rolls for its new one); `PROBE_MAX_PSP` takes a Mind Warrior's fifth with
  `KIT_HAS`, as a sleeping psionicist class still gives its PSP. `SPEC_OF_SHEET` treats a
  dual-classed Battle Mage's weapon spec as the kit's (none asleep, expertise awake), not a new
  warrior class's. The Effects screen has a `KIT:` line for each kit, the oldest class's first, `
  (ASLEEP)` after one asleep (`KIT_AT`, `KIT_OF_SHEET` with `KIT_SHORT`'s shorter names,
  `KIT_LINE_ASLEEP`, `KIT_AWAKE`); see the next section for its pages. `kitpages.kit_place`,
  `kit_at`, `kit_awake`, `kits_of`, `kit_ids`, `kit_level`, `kit_class_of` are the Loader's.
- **Classes barred to a dual-classing human.** Seeker, Justifier (cleric); Shinobi (preserver);
  Swashbuckler, Crusader, Battle Mage, Mind Warrior (fighter, gladiator, ranger); Arena Champion,
  Sentinel (druid, preserver: no shield); Brute (psionicist, air cleric: no two-handed melee
  weapon it may use, the cahulaks not one for it); Stalker (thief: its hiding on a thief's own); Grove Warden (gladiator: its AC on a
  gladiator's own); Healer (the rangers of air, earth and fire: water's sphere only; the game
  already keeps a priest from the other priest class, and a ranger, who must be good, from the
  druid, who must be neutral, so `DUAL_BANS`' clerics and druids there and the Seeker's and
  Justifier's druids never come up). Where: the DUAL window (866C7h) asks of each class (SI, 1-17)
  whether member [BP+6] may change to it (86E94h: AX 1 if so; human, prime requisites) and greys the
  rows answered no (a row with elements, cleric, druid or ranger, stays open while any of its four
  classes is allowed; the element is then picked on the game's three-choice menu, 86BBBh: its title
  the air row, DS:30A5h, then earth, fire and water, AX 0 to 3 added to the row's first class. For a
  Healer `DUAL_SPHERES`, called by `PROBE_DUAL_BAN`, makes that menu WATER ONLY, no other row, and
  `PROBE_SPHERE`, `INT FFh` over the `cmp ax,1` after it, 86BC3h, makes its answer water. The game
  makes any answer but 1-3 (the title, or the menu closed) the air class and changes the member at
  once: for a class a kit of the member bars there (a Brute's air cleric, its cleric row open for
  earth, fire and water), `PROBE_SPHERE`'s `SPHERE_BARRED` sends it to the window's close after a
  change (86B68h) with no change made, so closing the menu cancels (the member from 348h:25Bh, the
  segment read from the code after the return); checked in
  the game: a water-cleric Healer to ranger, a water ranger; a fire ranger to water cleric, no
  Healer on the KIT menu): `PROBE_DUAL_BAN` (`INT 9Dh`, new: the `or ax,ax` after the call, 866FFh;
  its flags back to the JZ with `RETF 2`) answers no for a class one of its kits bars (each
  `KIT_AT`, asleep too; `KIT_BANS`), from `DUAL_BANS` (a kit's number, then a dword of class bits;
  `kits.DUAL_BANS`). The slot kits' tables (`PROBE_SLOTS`) replace the whole count for their kind of
  magic, so they would take a new cleric's, druid's or preserver's slots' place.
- **A new preserver's spells**, on changing class and at creation: [Preservers'
  first spells](DEVELOPMENT-RULES.md#preservers-first-spells).
- **Sound numbers on the sheet.** Every character. Where: the game reads a word at sheet `+42h`
  (78FDAh, `mov dx,[es:bx+42h]`: a sound to play, 4 if 0) and at `+44h` (81DE3h, `mov
  ax,[es:bx+44h]`: played if not 0), and the kit byte (`+43h`) and second sphere (`+45h`) are their
  high bytes, 0 in every one of the game's sheets: `PROBE_SOUND_42` and `PROBE_SOUND_44` (`INT 9Bh`,
  `INT 9Ah`, new, 4 bytes each) read the low byte alone (`movzx`).
- **A kit for a dual-classing human's new class.** Every kit, for a human with none yet (one kit a
  character: `DK_ASK` asks none of one whose kit byte has a place's bits, `KIT_PLACES_BITS`, and
  isn't `KIT_OPEN`; `OWN_BIT` alone isn't a kit). Where: in the routine that changes a
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
  from it after.
- **Starting gear fitted to the kit.** Ravager, Brute, Shinobi, Seeker (a forbidden hand item),
  Shadowblade, Rescuer (the shield left behind), Arena Champion (a shield), Ghetto Fighter (the
  shield left behind, a dagger in hand: `_ghetto_dagger`), Poisoner (one of its weapon spec in each hand, the
  dagger or the short sword: `_poisoner_daggers`), Battle Mage (its weapon spec's weapon), Battle
  Dancer (a second long sword in the left hand in place of the shield, `_kit_second_weapon`, and a
  bow and arrows, with fuller starting gear: `startgear.py`); Myrmidon (its second weapon spec's
  weapon, the polearm, in the backpack); Spellarcher (its armour, helm and shield left behind; a Fine
  Bow and arrows by its picks: [the Fine Bow](#where-each-effect-goes)). Where: the game
  gives a new character its class's gear when DONE is clicked (the README's table).
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

The pairs `KIT_PAIRS` bars, from when a human could take a kit for each class (up to 2.17; a
character has one kit now, so they meet only in older saves' characters):

| Kit | Can't go with | Why |
|---|---|---|
| Arena Champion, Sentinel | Shinobi, Twin-blade, Ravager | one needs a shield, the other forbids it (the Ravager's AC too) |
| Twin-blade | Healer | two weapons, and an off hand free of them |
| Brute | Shinobi, Lifebinder | a two-handed weapon, and weapons that can't be one |
| Ravager | Grove Warden | each has an AC of its own that betters with level: one on top of the other would stack |
| Swashbuckler, Crusader, Battle Mage, Mind Warrior | each other | each gives a warrior's THAC0: two would be one wasted |

Every kit also needs its Python side: the Characters tab and the in-game
THAC0 and saves (`game.py`), the dice log's lines, and tests that hold DSCLOG's code (emulated) to the Python.

## Spell arrows

([In the kits page](KITS.md#spellarcher): the Spellarcher; `spellarrows.py`.)

**The buttons.** Outside a fight, `PP_SHOW` gives a Spellarcher
(`KIT_SPELLARCHER` awake) a button in the USE screen's ability row for each
touch spell it knows (`ARROW_KNOWS`: the game's known table, `ARROW_SPELLS`:
Chill Touch, Shocking Grasp, Vampiric Touch; its first place, Burning Hands, is
never offered, a cone and not a touch, and kept so the others keep
their places, `spellarrows.RETIRED`), as it gives a thief
Pick Pockets: the first where a priest's Turn Undead is (APFM 2BEFh), unless a
thief's purse or a priest's element has it, the rest in the row's spare places
to its right (2BE7h-2BEAh, `PP_EXTRAS`: each drawn with Turn Undead's frame and
handler, its icon loaded and let go of by the game's routines, `PP_CLOSE`
letting go of them all as the screen closes). Kind 2-5 (`PP_ARROWS`+N), icons
ICON 3049-3052 (`icons.arrow_spell_icon`: the touch spell's tile, the hand taken
off, an arrow in its lines), names CHILL ARROWS and so on (`PP_TEXT`),
descriptions by `PP_INFO` (each under the description box's 195 bytes). Let go
of, the screen closes as for the thief's, and `PP_ARM` goes to `ARROWS_ARM`:
nothing readied, then `ARROWS_ASK` in a frame the overlay manager can fix up,
which hands the click to the Loader as an item used on the map is (`USE_ITEM`
`ARROWS_BY` FE00h and the member, `USE_WHO` the spell's place). Made, the Loader
answers with no text and nothing is shown; refused (not known, no slot), its
words (`PICK_TEXT`) are.

**The Loader** (`SpellArrows.make`) takes a slot of the touch spell's level from
the wizard slots left (`SLOTS_LEFT`; none left, it says so) for one arrow
(`ARROWS_A_SLOT`, as the Spellarcher of *Dragon* #214's "The Complete Half-Elf" casts a spell onto
an arrow). The Spellarcher keeps one stack of each spell, `STACK_MOST` (24) at
most: the arrow joins that spell's stack wherever it is (its count up by one; a
full stack takes none and uses no slot); with none, a new stack of the game's
Arrows (type 62) goes in the quiver when it is empty (`npcitems.add_to` with the
ammunition slot; `weaponchoice.bow_ahead` then puts the bow ahead of it in the
list), else in a backpack cell. The stack is named Chill, Shocking or
Vampiric Arrows (names 16Dh-16Fh; 16Ch, Burning, kept unused), their pictures objects 2614-2621 (the Arrows'
icon, its heads in the spell's colours), value 0. They last until shot: nothing
takes them away at a rest. They are readied and put away as any arrows.

**The hit.** The weapon attack routine (5883Ah) casts only the weapon's own
spell on a hit (its item's +0Fh, the spell + 1, at 58B63h; cast by 598:89h with
the attacker as the caster and level 6 pushed for every weapon's spell, at 58BE6h:
`push 6 / mov al,cl / mov ah,0 / push ax`). `ARROW_LEVEL` (`NS_IMAGE+47`, over
those 7 bytes) keeps 6 for a weapon's own spell and gives a spell arrow's (`ARROW_HIT`
sets `ARROW_CAST`) the archer's level (`ARCHER_LEVEL`, DI the attacker: a party Spellarcher's
preserver level, class 11 among the sheet's +21h-23h, its level from +24h-26h; anyone else's
highest level of the three; at least 1), moving the INT's frame down
4 bytes to put the two words under it. `PROBE_ARROW` (58D27h, where the ammunition
routine keeps the arrows' plus) also keeps their name (`AMMO_NAME`); `ARROW_HIT`
(`NS_IMAGE+28`, over "cmp byte es:[bx+0Fh],0") gives a shot from a bow ([BP+16h]
above 1, a bow's type at [BP+14h]) with spell arrows their spell instead, when a
Spellarcher or anyone not in the party (the arena's elf champion: its creature above 3) shot them
(`PROBE_ARROW`'s `AMMO_ARCHER`; a party member of another kit shoots them as plain arrows), and `ARROW_SPELL`
(`NS_IMAGE+29`, over "mov cl,es:[bx+0Fh]") hands it on. The target saves as against
the spell (its record's save byte: Chill Touch's a save, Shocking Grasp's and Vampiric Touch's
none). The arrows hold no spell
themselves, so nothing else in the game (the USE screen's items, breaking, acid)
sees one. Only a Spellarcher carries them: `ARROWS_FORBID`, in `PROBE_CAN_USE`
(whatever the rules), refuses spell arrows (the equip routine's item, its
`[BP+6]`) to anyone else; the game asks nothing of an item put in a backpack, so the Loader
(`spellarrows.return_strays`, out of fights with the inventory shut: `INVENTORY_SLOTS`) takes those
another member carries back to the party's Spellarcher. Those left with the member (no Spellarcher
in the party, or no room in its pack) come out of its quiver, if it has them readied (an old save;
the ammunition slot), into a backpack cell of its own (`pickpocket.place`), so no one but a
Spellarcher ever has them readied. Seen refused in DOSBox (CANNOT USE THIS ITEM):
a stack dragged to a non-Spellarcher's quiver, to another member's through its portrait, and part
of one after SPLIT; the T loot (`loot.py`) puts what it takes in backpack cells only. The item box's
INFO (8C1B8h: its heading, USEABLE BY:, then each member the game's can-use routine allows, so
`ARROWS_FORBID` already leaves out all but a Spellarcher, else NO ONE) says so too: `INFO_HEAD`
(`NS_IMAGE+121`, over "push ds / push 3493h", 8C1E0h, the heading's far pointer) pushes DSCLOG's
SPELLARCHERS: instead for the four names (the INT's frame moved 4 bytes down), so the list reads
"SPELLARCHERS: / Cermak" or "SPELLARCHERS: / NO ONE", in the top row whatever the names below;
`tests/test_arrowinfo.py`. Seen in
DOSBox: [log](https://github.com/daaki85/darksun-obsidian-edition/blob/main/playtest/logs/2026-11-18-spell-arrows-info.md). The four spells' records pass the
routine's own test (+30h's low bits 2, not 1). Verified: [log](https://github.com/daaki85/darksun-obsidian-edition/blob/main/playtest/logs/2026-11-16-spellarcher-fine-bow.md). A non-party archer shoots them as a Spellarcher
does, for the cast's level and the arrows' plus (`ARCHER_LEVEL`: [the hit](#spell-arrows), above;
`spellarrows.archer_level`): the elf champion's Chill Arrows cast Chill Touch on a party member
they hit, its save and its STR loss as the spell's (verified: [log](https://github.com/daaki85/darksun-obsidian-edition/blob/main/playtest/logs/2026-11-18-champion-chill-arrows.md)). A new Spellarcher's Fine Bow and starting
arrows (`spellarrows.starting_gear`) and the arrows' plus are in [where each effect goes](#where-each-effect-goes). Arrows put in the
ammunition slot by memory writes during a fight are not shot (the game keeps its own
list of what each combatant has readied): they're made outside fights only.

## Kits in Wake of the Ravager

The party transfer keeps the kit byte (SL's `+43h`) at the sequel's `+3Dh` (`KIT_BYTE` in ravlog's
layout; the sequel's sound words below it read as bytes, `sound_3c`, `sound_3e`). DSCLOG2's KITS
section has DSCLOG's `KIT_IS`, `KIT_HAS`, `KIT_AT`, `KIT_PLACE`, `KIT_AWAKE`, `KIT_LEVEL` and
`MULTI_GROUP` on the sequel's sheet (race `+12h`, classes `+1Bh`, levels `+1Eh`, base AC `+21h`), and
`RULE_KITS` is in `ravager.RULES_PORTED` (its bit in DSCLOG2's `rules_hi`, so `RAV_RULES_OFF=0x10000`
makes a control run). Each effect at the sequel's site (its attack routine's frame is SL's with the
locals two bytes lower: the damage bonus `[BP-14h]`):

| Effect | Kits | DSCLOG2 | The sequel's site (SL's) |
|---|---|---|---|
| AC | Ravager, Wanderer, Sentinel, Arena Champion, Grove Warden, Battle Dancer, Wild Fury | `KIT_AC` in `PROBE_AC` | the AC function's end, 5D6E6h (58F8Dh) |
| to hit | Ravager, Brute, Ghetto Fighter, Arena Champion, Sentinel, Military Scout, Battle Dancer, Wilderness Avenger, Wild Fury; the warrior THAC0 kits' (`WAR_HIT`) | `KIT_ATTACKS` from `OFF_HAND` | the attacks' store, 5CEE8h (58892h) |
| damage | Ravager, Brute, Ghetto Fighter, Arena Champion, Battle Dancer, Wilderness Avenger, Wild Fury | `KIT_DAMAGE` from `SPEC_DAMAGE` (site 51) | 5CF6Dh (588F2h) |
| attacks a round | Battle Mage, Crusader, Mind Warrior (`EXPERT_HALVES`), Wild Fury (`KIT_WILD_MORE`) | `SPEC_ATTACKS`, `OFF_HAND` | 5CEE8h |
| weapon skill | Battle Mage, Crusader, Mind Warrior, Justifier, Myrmidon, Seeker | `SPEC_OF_SHEET` | |
| saves | Sentinel, Myrmidon (the sequel's charms, `KIT_CHARMS`: `ravlog.RAV_CHARMS`), Wanderer (`WANDER_SPELLS`: the sequel's spell records with `+1Ah` fire or cold) | `KIT_SAVE` from `PROT_SAVE` (site 44) | 8360Eh (79D47h) |
| thief skills | Assassin, Shadowblade, Ghetto Fighter, Wayfinder, Military Scout, Swashbuckler (its bad luck, `BAD_LUCK` at the header's +1862) | `KIT_SKILL` from `BELT_SITE` (site 20) | 8C7C5h (803B2h) |
| from behind, backstab | Military Scout, Rescuer | `KIT_REAR` from `MISSILE_REAR` | 5C99Fh |
| the backstab's multiplier | Assassin (one more, x3 to x6) | `STAB_TIMES` (site 53, Thieves as in AD&D's) | 5D11Bh (58A80h) |
| movement | Stalker, Rescuer | `KIT_MOVE` from `CAH_MOVE` | 5B838h (57566h) |
| the two-weapon penalty | Ghetto Fighter, Twin-blade, Battle Dancer | `KIT_TWO` from `PROBE_TWO` | 5DE7Ch (59634h) |
| initiative | Myrmidon, Wayfinder, Military Scout | `KIT_INIT` (site 60, new) | `add dx,14h` at 5B7E9h (5750Eh), SI the creature |
| casting level | Seeker (the ranger level less 5), Justifier (less 9) | `KIT_RANGER_CAST` (site 61, new); `RANGER_DROP` in `RANGER_LEVEL` | the caster level routine's `sub dx,7`, 97E00h (81B6Ah); the spell's level, 629F0h (5E3B8h) |
| a second sphere's spells | Elementalist (the sheet's `+3Fh`, low three bits) | `EL_SPHERE` (sites 90-92, new) | `add sp,4` after each call to 62B45h (spell, class) that has the member: 62CAEh in 62C00h (the USE screen's spells known; DI the member), 629BEh in 628AFh (the cast's level) and 97DE1h in 97DC5h (the caster level; both `[BP+6]`) |
| PSP costs | Mind Bender, Kineticist, Titan Mind, Wasteland Seer (and a thri-kreen of the games' own party with a psionicist class) | `PSP_USE`, `PSP_TABLE`, `PSP_DEFENCE`, `PSP_KEEP`, `PSP_KEEP_DX` (sites 191-195, new; `KIT_PSP`, `PSI_KIT`, `KIT_PSP_OF` as DSCLOG's, `FIGHTER_CR` the combatant's creature) | the power routines' cost in DI, 6178Eh (5CBE7h); the powers' table (3D0h:7E0h, 3 bytes a power: SL's 8) read at 6162Dh (5CAA3h), 6183Dh (5CCA2h), 619DCh (5CE49h), 616A8h (5CB02h); a defence paid, 61FA1h (5D820h) |
| PSP at a level up | Mind Warrior (a fifth fewer, asleep too) | `KIT_MAX_PSP` (site 198, new) | `les bx,[bp-8]` 95172h (8748Fh); SL's `PSP_SCORES` fix of WIS read from the creation record (95110h) not ported |
| hit dice at a level up | Battle Mage (d6, 2 past 10th), Arcanist (d3, 1 past 10th) | `KIT_HIT_DIE`, `KIT_HIT_GAIN` (sites 196, 197, new; `HIT_KIT` for the kit's own class, `[BP+8]`) | the group's die `mov al,es:[bx+0]` 95014h (87308h) and its gain past the dice `mov al,es:[bx+2]` 95000h |
| hit dice and PSP at creation | Battle Mage (d6), Arcanist (d3), Mind Warrior (a fifth fewer PSP) | `CR_DIE` (site 200, new; `CR_KIT_STALE` a kit left from other classes taken away), `CR_PSP` (site 201, new); `KIT_REROLL` from `KIT_ROW` (site 65), `KIT_MADE`, `KIT_ROLLS_DUE` | the creation hit points' routine 6D1EDh (5C0h:66h; 655D6h), its die for the most `mov al,es:[bx+11Dh]` 6D28Fh (65677h), its rolls by the level up's routine (`KIT_HIT_DIE`); the creation PSP routine 6D75Dh (5C0h:6Bh; 65B39h), its WIS bonus and end 6D85Eh made the site, the WIS test's `jna` at 6D842h sent to a `xor ax,ax` before it; the reroll calls those routines through the far addresses of the panel's calls 6BBDFh and 6B749h, the backdrop's 6BC38h (`WP_CALLS`) |
| casting after a hit | Battle Mage | `HIT_ROUND` (site 199, new) | the hit's mark `mov byte es:[si+0B2h],1` 5CD76h (58733h), SI the creature |
| casting level for duration and damage | Arcanist (wizard spells +1), Spirit Caller, Wasteland Seer and the own thri-kreen psionicist (priest spells +2 under the open sky, -1 under a roof, at least 1) | `KIT_CAST_LEVEL` (site 205, new) | `inc byte [bp-1]` at the end of 628AFh's class loop (629FEh; SL's PROBE_SPELL_LEVEL at 5E3D1h): DI the level, `[BP+6]` the caster, `[BP+8]` the spell |
| cures | Healer, Rescuer (+1 a die), Lifebinder (a die more; Blood Flow too); Cell Adjustment (+1, +1d4) | `KIT_CURE` (site 206, new); `CELL_MORE` in `CELL_HEAL` (site 11) | `push ax / jmp 65811h` at 66545h (SL's PROBE_CURE at 79619h), the healing pushed under the INT's frame; `[BP+0Eh]` the spell, `[BP+8]` the caster |
| Cause Wounds | Wilderness Avenger (+1 a die) | `AVENGER_AREA`, `AVENGER_ONE` (sites 207, 208, new), `AV_CAUSE` | the damage stored after 80278h: `mov [bp-14h],ax` at 7E7A6h (SL's AREA_DMG at 754ECh), `mov [bp-6],ax` at 7F727h (HARM_SITE at 761A9h); DI the spell, `CAST_WHO`/`CAST_SPELL` TH_CAST's |
| spells known | Healer (the cosmos: a spell's sphere byte 20h, or `COSMOS_MORE` at +2060), Healer and Lifebinder (no harming spells: SL's, and the sequel's own Heartseeker, Energy Drain and Symbol of Pain, `ravager.RAV_SEQUEL_HARMS`), Wilderness Avenger (no healing ones) | `HEALER_COSMOS`, `KIT_BARS` in `EL_SPHERE` (sites 90-92) | as the Elementalist's: the game's answer of 62B45h made yes or no |
| a hit's poison | Poisoner (each hand's first melee hit a fight, `POISON_USED` at the header's +2088, cleared at the first round by `ACID_ROUND`; a weapon with a spell of its own casts that, no dose used) | `POISON_HIT` (site 214, new), then `PLAIN_ARROW` (site 49) makes the hit's spell the monsters' poison, 273 (SL's 176 by its record), cast as a weapon's (`WEAPON_CAST`: level 6, no roll) | the hit's "does the weapon cast" test, `cmp word [es:bx+10h],0` at 5D20Dh (SL's 7A6DDh in the hit's special effects, which the sequel's weapon hits don't pass through) |
| an arrow's plus | Spellarcher (its spell arrows from a bow, by name: +1 from 5th preserver level, +2 from 9th, +3 from 13th; anyone outside the party by its highest level) | `ARROW_PLUS` (site 215, new) | the ammunition routine's `mov es:[0009h],al`, 5D456h (SL's 58D27h): `308h:[9]` the plus the shot's damage adds (5D021h) and its magic takes where better than the bow's (5C7B5h) |
| to hit with the Fine Bow | Spellarcher (its starting bow, `ravkitstart.fine_bow`; the party transfer keeps the name, `ravager.FINE_BOW_NAME`), whatever the rules | `FINE_HIT` from `OFF_HAND` | 5CEE8h |
| spell slots | Elementalist (a level behind), Crusader and Battle Mage (1 fewer), Seeker, Justifier, Shinobi (their own tables, WIS left out: `seeker_slots`, `justifier_slots`) | `SLOT_BEHIND`, `BEHIND_LEAST`, `KIT_TABLE` in `ADND_SLOTS` (site 34); `SHINOBI_MAGE` (site 190, new); `VEILED_SLOT` | the slot routine 626B7h, per class: its call to 62A10h at 62893h (5E240h), and the "add sp,4" after its "casts wizard spells" call to 62B45h (spell 8) at 627D6h, so a Shinobi's thief class is asked (SI the member) |
| a thief's wizard spells | Shinobi (its own 21, `SH_SPELLS`: `kits.RAV_SHINOBI_SPELLS`; cast at its thief level less 5, `SH_CAST`) | `SH_YES` before `EL_SPHERE` (sites 90-92); `SHINOBI_CAST_LEVEL` (site 209, new); `SH_PLACE_LEVEL` in `RANGER_LEVEL`; `SHINOBI_LEVEL_UP` (site 210, new) and the Shinobi parts of `PICK_ANY`, `PICK_PAGE`, `PICK_LIST`, `PICK_TOP`, `CR_PICKS` (`SH_FIRST_SPELLS`), `SCROLL_LEARN` and `NS_SCROLL` (`SH_ROLLS`: read languages then INT), `NS_SPOOK_SAVE` | the caster level's `add sp,4` after its class level call (98h:0C1h), 97DF1h (81B16h's loop); the level up's `cmp word [bp+8],0Bh`, 957ABh (SL's PROBE_LV_PICK place); header +2076 the read roll and chance, +2078 the spell's high byte, +2080 on the counts |

The Loader's header bytes are DSCLOG's places: `KIT_OUTDOORS` +350, `KIT_DANCE` +351, `KIT_WILD` +355;
`RavDiceLog._kit_tick` makes them writable while the kits are on and keeps them as Shattered Lands'
dice log does. DSCLOG2 counts what it did (`kit_acs`, `kit_hits`, `kit_damages`, `kit_rates`,
`kit_saves`, `kit_skills_n`, `kit_rears`, `kit_moves`, `kit_twos`, `kit_inits`, `kit_stabs`, `el_spheres`; the casting
levels', cures' and spells known's `kc_levels`, `kc_cures`, `kc_causes`, `kc_cosmos`, `kc_barred`, `kc_cells` at
the header's +2064 on:
`playtest/ravkits.py count`; the slots' `sb_count`, `kt_count`, `sh_mages`, the PSP's and hit dice's `kit_psps`, `kit_hds`, `bm_hits`:
`playtest/ravlevel.py counts`; at creation `kit_rerolls`, `cr_stales`, `cr_psps`: `playtest/ravkits.py page`). `tests/test_ravkits.py` runs `KIT_IS`, `KIT_LEVEL`, `MULTI_GROUP`, `SPEC_OF_SHEET`,
`EXPERT_HALVES`, `KIT_MELEE`, `SLOT_BEHIND`, `BEHIND_LEAST`, `KIT_TABLE`, the PSP sites, `KIT_MAX_PSP`,
`KIT_HIT_DIE`, `KIT_HIT_GAIN` and `HIT_ROUND` against `kitpages` and `kits` on transferred sheets, and `CR_DIE`,
`CR_PSP` and `KIT_ROLLS_DUE` on the creation screen's sheet, and checks the tables; `tests/test_ravsphere.py` runs `EL_SPHERE` against `ravager.casts` and the sequel's own 62B45h
against `ravager.class_spheres`, and `SHINOBI_MAGE` on the same sheets; `tests/test_ravkitcast.py` runs sites
205-208, `CELL_MORE` and `EL_SPHERE`'s kit parts against `kits` and `ravager.casts` in the sequel's spell numbers
(`ravager.RAV_*`, which `ravlog.apply_layout` puts into `kits` for the dice log's kit parts); `tests/test_ravpoison.py` runs
`POISON_HIT`, `PLAIN_ARROW`'s poison, `ARROW_PLUS` (against `kits.arrow_plus` and `spellarrows.archer_level`) and
`FINE_HIT`, checks the sequel's record 273 is the 10-damage poison, and the transfer keeping the Fine Bow.

Not in the sequel yet: what kits do to spells and powers (the Shinobi's spells and casting), the Spellarcher's arrows made (the USE screen's buttons and the Loader's `SpellArrows.make`: the sequel has no spell arrow objects of its own outside a transfer), gear a kit forbids or allows, a Scholar's THAC0 and the kits' parts of the DAM lines. The USE screen's hover still shows a
power's table cost (97135h), not the kit's. Choosing a kit (the
creation panel's KIT pages, sites 62-69, and `DUAL_KIT`, site 76) is DSCLOG2's KIT PAGE. The Effects screen's kit lines are DSCLOG2's EF_ROWS (site 73), on
KITS' KIT_PLACE and KIT_AT. The sequel marks no priest spells known by class masks as SL's
loops do (66F89h, 86E1Eh): it asks 62B45h (spell, class) at each use, by a byte a spell (selector
3D0h:7D3h) met by the class's mask from a jump table; 62B45h has no character, but its three callers
that ask for a member's class do, so `EL_SPHERE` answers after them. A Healer's cosmos would go the same
way: the sequel's druid-only spells (the byte's 20h) for its water cleric. The new spells' bits at
`+3Fh` (3-7) have no use while the sequel has no new spells: a wizard's spells known are bits a member
(selector 320h:39Ch) that 6260Ah reads for spells below 73h, so the new spells' port would answer
there from them.

## How they're checked

Each kit's DSCLOG code is held to its Python by emulated tests (unicorn), the Python by its own:

- `tests/test_dsclog.py`: `KitTests` (the kit page's windows, the Effects screen's kit lines, two
  kits' AC, the Ravager's AC, the Wanderer's damage, the Avenger's spells), and the kits' cases in
  `SpecializeTests` (to hit, damage, attacks, `KIT_SHOT`, Wild Fury), `CanUseTests` (gear, spell
  arrows), `BeltTests` (thief skills, the Swashbuckler), `StealthTests`, `LevelPickTests` (the
  Shinobi's spells), `NewSpellTests` (the Lifebinder's Cell Adjustment) and `WornTests` (the Arena
  Champion).
- `tests/test_kits.py`: `KitEffectTests`, `CosmosSpellTests`, `AvengerHealTests`, `BruteBanTests`,
  `DualBansInHelperTests` (`DUAL_BANS` against `kits.DUAL_BANS`) and `SpellarcherBareTests`.
- `tests/test_kitpages.py`: `KitPageTests` and `DormantKitTests` (a kit asleep after DUAL).
- `tests/test_dance.py` (`DanceTests`), `tests/test_wild.py` (`WildTests`),
  `tests/test_spellarrows.py` (`SpellArrowsTests`, `StrayTests`, `StartingGearTests`,
  `CastSoundTests`), `tests/test_restrict.py`'s `ForbiddingKitTests` and
  `tests/test_specialize.py`'s `KitGearTests` (starting gear fitted to the kit).

Each was also played in the game: the creation screen's KIT page and hit dice, the level ups
(Shinobi spells, Seeker slots), the KIT menu after DUAL with its bans, and the Effects screen's
pages. Verified: [log](https://github.com/daaki85/darksun-obsidian-edition/blob/main/playtest/logs/2026-11-15-kit-rebalance-checks.md).
