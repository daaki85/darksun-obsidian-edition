# Rule corrections against OpenDS (2026-11-18)

The first comparison (`opends-bug-comparison-2026-11-18.md`) covered `GAME-BUGS.md`, the bugs. The mod's
other large body of corrections is the rules: the rows of FEATURES.md's "Rules the game got wrong" table
(each with a switch), the report `spells-against-the-manual.md`, and the class tables. This is the same
exercise for them. Match by my reading of OpenDS at `fe35c52`; "nothing" means I found no description.

## What OpenDS has

OpenDS decodes the engine's rules **as data**, for a port to reproduce: `docs/rules-tables.md` (the rules
block at DS1 file `0x45F10`, the class-group rows, the save table, THAC0 at `0x87666`, the XP table at
`0x3E57C`, the CON and ability tables), `docs/spell-effects.md` (the casting module ovr32 at `0x78BA0`, the
power table at `0x41F70`, the save descriptor), `docs/combat-flow.md`. They treat what the engine does as ground
truth, and note a departure from the Player's Handbook only in passing (their save table is slower than the
PHB's: warrior paralyzation L1 14, L4 12, L8+ 11 against PHB L4 13, L8 10, L17+ 4; rules-tables section 1).

What the Edition adds is the **second layer: where the engine departs from its own manual and from the
Player's Handbook, what the right value is, and the site that changes it.** They have the first layer for
most of these, and not the second.

## The rows of "Rules the game got wrong"

| # | Rule (ours) | OpenDS |
|---:|---|---|
| 1 | Saves against spells: the kind-to-category table at DS:1E75h gives petrification or polymorph for almost every spell | data only (save descriptor bits); not the map or the deviation |
| 2 | Fire, cold and electricity: the save's d20 is doubled | nothing |
| 3 | Spells, psionics and monsters against the manual (pp. 30-86) | data only (power table decoded); no comparison |
| 4 | Turn Undead: a d20 against a number of its own; success destroys, no fleeing | nothing |
| 5 | Missile and touch spells always land (the to-hit check at 78BA0h is `mov ax,1 / retf`) | module range only; the stub isn't identified |
| 6 | Enlarge grows the whole hit | nothing |
| 7 | A ranger's spells: level less 7 for slots, whole level for duration and damage | nothing |
| 8 | Preservers learn any spell from any scroll | nothing |
| 9 | Dual-classing: 2nd level, one prime requisite | nothing |
| 10 | Class restrictions: any one class allowing an item is enough | data only (the 20-byte legal-item table at +0x24) |
| 11 | Multiclass hit points: CON's bonus once a level | nothing |
| 12 | Class tables: XP, priests' THAC0, spell slots | data only (XP table, THAC0 routine, slot routine decoded); deviations not recorded |
| 13 | CON 20 and up: hit-point regain, dwarves' and halflings' poison save | data only (the CON tables) |
| 14 | Two weapons: no penalty, the full rate in each hand | nothing |
| 15 | Warriors' attacks: 3/2 with any weapon | nothing |
| 16 | Held and Out Cold targets: a roll to hit and double damage | nothing |
| 17 | Acid on armour: destroyed outright | relayed from us, unverified |
| 18 | Thief skills too high; a backstab multiplies STR's bonus too | nothing (the skills table is not in their rules block) |

Count (18 rows): **1 relayed, 5 "data only" (the table is decoded, the deviation isn't recorded), 12 nothing.**
(One row, thief skills and backstabs, carries two rules; counted as one, as FEATURES.md has it.)

## Hit points on level-up (added 2026-11-18)

This is row 11 above ("Multiclass hit points"), which deserves more than a line. What the code does, read from
the stock DS1 `DSUN.EXE` today:

- **The per-level gain** (routine at file `0x87250`): the class's group row (file `0x45F10` + 4 x group, "hit
  die, last die level, flat gain") says a level rolls the die while the level is **at most** the last die level,
  else takes the flat gain. The rows: priests (8, 9, 2), warriors (10, 9, 3), wizards (4, 10, 1), rogues (6, 9,
  2); thieves and psionicists are both group 3 (the class-to-group map at `+0x10`). The roll is then raised to
  the CON floor table at `+0x38` (1 up to CON 19, then 2, 3, 3, 4, 4, 4 for CON 20 to 25).
- **The total** (`0x874B0`): rolled dice scaled by the levels now over the levels before any were lost, divided
  by the number of classes, plus CON's bonus from the shared helper at `0x8757C`. For a multiclass character the
  bonus is worked out from the warrior levels (capped at the last die level) at the full bonus and the highest
  class's other capped levels at up to +2: in effect **once a level of the highest class, not on every die**, as
  the Edition's notes put it. AD&D (Demihuman Deities) gives it on every die, into a total shared between the
  classes. The Edition's switch does that (`INT CAh` at `0x87523`, `INT C9h` at `0x877DA`).
- **What OpenDS has:** `rules-tables.md` decodes the same group rows (and notes the rogue row stops at 9, "not
  2E's 10"), the CON floor and `base_hp` (calls the multiclass division explicit), but not that the CON bonus
  is given once a level; its helper at `0x8757C` is described by the shape of the PSP formula.
- **A discrepancy of ours to settle first.** The player's guide's hit point table has the thief rolling a d6 at
  10th and taking +2 only past it. By the code the thief and the psionicist share one row, last die level 9, so a
  thief takes the flat +2 *at* 10th, as the guide already says for the psionicist. The guide looks wrong for the
  thief (an AD&D assumption: 2E's rogue rolls through 10th). Not played: a thief to 10th with the dice log would
  settle it. Until then I would not send OpenDS a thief figure.
- Before the Edition raised the level cap every class stopped at 9th, so none of these flat gains was ever seen in
  the unmodded game; only the per-die rolls to 9th and the multiclass CON bonus were.

## The experience tables, checked today

Game vs the AD&D table the mod uses (`tables.py`), the game's from the stock DS1 `DSUN.EXE` (611,408 bytes)
at file `0x3E57C` (8 class rows of 20 words, in hundreds; entry k is the XP to *reach* level k + 1). The XP
to reach each level 2 to 14, game against ours:

- **Cleric, fighter, preserver, psionicist: identical.**
- **Ranger, thief:** level 2 only: 2,200 against 2,250 (ranger), 1,200 against 1,250 (thief).
- **Gladiator:** the game's row is a copy of the fighter's (OpenDS knows this), so every level 2 to 14 is
  lower than the ranger-style row we use: 2,000 against 2,250 at level 2 up to 1,500,000 against 1,800,000 at
  level 14. Whether AD&D's or Dark Sun's gladiator is meant to share the ranger's column is a judgement of ours;
  FEATURES.md calls this "a little more for 2nd", which understates a gladiator's whole row.
- **Druid:** levels 11 to 14, game 675,000 / 900,000 / 1,125,000 / 1,350,000 (the cleric's, rising evenly),
  against 200,000 / 300,000 / 750,000 / 1,500,000 (the AD&D druid's, whose last jump is the steepest).

THAC0 (routine at `0x87666`): `20 - rate x (level - 1) / 12` per class group; the priest group's rate is 8,
so a priest improves a level early against AD&D (20, 20, 20, 18, 18, 18...). Spell slots: the game's 5th
level gives clerics, druids and preservers 3 2 1 where AD&D gives 3 3 1 (priests) or 4 2 1 (wizards). Both
already in `tables.py`; these are not re-checked against the image today.

## The spells against the manual

`spells-against-the-manual.md` reads the 32-byte spell records from the stock `DSUN.EXE` (spell s at file
`0x41F70 + 0x20 x s`, which is their power table) and sets each against the game's own manual: about 16
preserver entries, 17 cleric, 10 psionic and 15 monster entries (the rows of its tables), and a "match or
already fixed" list. OpenDS decodes the same records; it has no manual comparison. Three findings in it are
engine bugs more than rule choices and have addresses: **Scare** (its record's save byte A0h has bit 0 clear, so
the save routine at 79A71h, testing it at 79A89h, never saves), **"can't save"** (the total is compared
unsigned at 79BBAh, so -100 reads as large; also in GAME-BUGS), and **Protection from Normal Missiles**
stopping breath weapons (7A142h). The first two are fixed in the Edition; the third is in the report.

## What to offer

1. **The comparison layer as one document**, not one issue per rule: "where the engine departs from its manual and
   the PHB, with the sites" for the rows marked "data only" (3, 5, 10, 12, 13): it would sit beside their
   `rules-tables.md`, which already says where each table is.
2. **The level-up hit-point rows** (above) once the thief row is settled.
3. **The 12 "nothing" rows** as a table of facts, each with its site (what the code does, the right rule, the
   address). Most need an address check against the image first; many sites are hooks in our helper, so the
   description of the rule is the part that transfers, not the patch.
4. **The XP diff above**, which is a concrete, checkable result: eight lines, from the stock file.
5. **Scare, "can't save" and Protection from Normal Missiles** as engine bugs with addresses (the first two are
   in the 38 absent rows already).

Licence: our documents are GPL-3.0 and theirs MIT; facts in new words only.
