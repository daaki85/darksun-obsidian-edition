# 2026-11-26: the Poisoner's poison, the spell arrows' plus and the Fine Bow in Wake of the Ravager

*Branch `claude/ravager-poison-arrows`. The port audit's step 7, part 2 (reports/wake-of-the-ravager-port-audit.md
on claude/ravager-port-audit).*

**Under test:** DSCLOG2's POISON AND ARROWS: POISON_HIT (site 214, 5D20Dh) with PLAIN_ARROW casting the
sequel's monster poison 273; ARROW_PLUS (site 215, 5D456h); FINE_HIT from OFF_HAND. Header +2088 to +2097.

**The copy:** `ravPZ`, a full copy (`cp -a`) of `ravK` (the `fountain-user` party transferred, 48h sheets);
nothing written into `rav` or `ravK`.

**Each run** ([files/2026-11-26-ravager-poison-arrows-run.sh](files/2026-11-26-ravager-poison-arrows-run.sh),
from the kits' run script): ravstart with the Loader, the four ADDed, a new game, the opening talk; test edits
in memory (never saved): Seneca (sheet 1) a halfling fighter/thief Poisoner (`ravkits.py set 1 1 6 9 17`,
levels 3 3), Lex (sheet 0, the transfer's own Spellarcher, Shocking Arrows) at fighter 5 / preserver 5, HP 250
for the four; in the run with the Fine Bow, Lex's bow named the Fine Bow (`ravitems.py 0 --fine`); the dice
log (`ravdice.py --numbers`), Computer Control for all four in the Draxans' ambush, about five minutes
watched, DSCLOG2's counters every 10 s (`ravkits.py count`). The control runs with the kits off
(`RAV_RULES_OFF=0x10000`) and no bow renamed.

## What was seen

Six runs (2026-11-27, 01:02-02:05 UTC), each on the same copy (unchanged after: `diff -rq` against `ravK`
empty):

| Run | Kits | Fine Bow | Lex's edits | poison_doses / casts | arrow_pluses | fine_hits | Lex's shots |
|---|---|---|---|---|---|---|---|
| A | on | named | | 1 / 1 | 93 | 0 | none (he closed in with his short sword) |
| B (control) | off | | | 0 / 0 | 0 | 0 | none (the dice log died early: a read error) |
| C | on | named | right hand's sword in the pack | 1 / 1 | 68 | 0 | none (his left hand's Dragonsbane and the sword, readied at the fight's start) |
| D (control) | | | | | | | stopped at once: C showed the edit doesn't make him shoot |
| E | on | named | bow +15 | 1 / 1 | 45 | 15 | 12, all with the bow |
| F (control) | off | | bow +15 | 0 / 0 | 0 | 0 | 11, all with the bow |

**The Poisoner** (Seneca, `poison_used` 32 at the end of A, C and E: bit 5, her off hand). Her right hand's
weapon (item 261, power 14) has a spell of its own: its hits cast that and used no dose, as built. Her left
hand's bone dagger's first hit poisoned:

```
A: Seneca hits Draxan#21 for 11: 1d4 = [3] +1 weapon +4 STR 18 +3 backstab (the dice 3 x2 = 6)
A: Draxan#21's saving throw vs Mons273 from Seneca#1 (paralysis/poison/death): d20 = 3, needs 6 (75% to save) -> failed
A:   Draxan takes 10 from Mons273, now 72/120 HP
E: Seneca hits Draxan#26 for 8: 1d4 = [3] +1 weapon +4 STR 18
E: Draxan#26's saving throw vs Poison (10 damage) from Seneca#1 (paralysis/poison/death): d20 = 18 +1 CON 20 = 19, needs 10 (60% to save) -> saved
F: Seneca hits Draxan#21 for 9: 1d4 = [4] +1 weapon +4 STR 18          (no save, no poison: the control)
```

Her later hits with the dagger poisoned no more (one dose a fight). A's "Mons273" is the sequel's record's own
name: the dice log names it "Poison (10 damage)" since (`RavGameData.spell_name`, run E).

**The Spellarcher's arrows and the Fine Bow** (Lex, fighter 5 / preserver 5, his transferred Shocking Arrows,
name 300). With his bow +15 Computer Control shoots (as the 2026-11-24 spell arrows' play found); without it
he closes in to melee, so A and C saw no shot (their `arrow_pluses` count the ammunition routine's calls on
his turns, which Computer Control makes as it weighs a shot). E against F:

```
E: Lex attacks Draxan#23 with Wooden item 305 +15 (1d8+15): d20 = 8, hits on anything but a 1 (95%), hits AC -13, target AC 1 -> HIT
E:     THAC0 18, +4 DEX, +15 weapon, +3 mastery, +1 fine = -5
E:   Lex hits Draxan#23 for 23: 1d8 = [4] +16 weapon +3 mastery
E: Shocking Grasp damage: 1d8 = [2] +5 = 7 (1d8 + 1 for each caster level: 5 at caster level 5)
F: Lex attacks Draxan#27 with Wooden Bow +15 (1d8+15): d20 = 14, hits on anything but a 1 (95%), hits AC -18, target AC 1 -> HIT
F:     THAC0 18, +4 DEX, +15 weapon, +3 mastery = -4
F:   Lex hits Draxan#27 for 25: 1d8 = [7] +15 weapon +3 mastery
F: Shocking Grasp damage: 1d8 = [6] +5 = 11 (1d8 + 1 for each caster level: 5 at caster level 5)
```

- the Fine Bow: "+1 fine" in every one of E's 12 THAC0 lines (DSCLOG2's `fine_hits` 15), none in F's;
- the arrows' plus: "+16 weapon" in E's damage (the bow's 15 and the arrows' +1 at preserver level 5), "+15" in F's;
- the arrows' spell at the archer's preserver level (5) in both, as before.

"item 305" is the Fine Bow's name: the playtest dice log (`ravdice.py`) doesn't read the names past 256
(DSCLOG2's ITEM_NAMES, the Loader's), so the mod's names show as numbers there (Seneca's "item 291", "item
261" too); the game itself shows them.

No crash, no "Illegal Op" in any run. No new area: no water noted.
