# 2026-11-25: STORE/RECALL, starting gear and first spells and powers together in Wake of the Ravager

**Under test:** branch `claude/ravager-join-gear-spells` (PR #184), which joins
[STORE/RECALL and fuller starting gear](2026-11-25-ravager-store-gear.md) (sites 83 RS_CLICK, 85 GEAR_DONE) with
[first spells and powers picked at creation](2026-11-25-ravager-first-spells.md) (sites 87 CR_PICKS, 88 PSI_GRANT,
95-99 PSI_COUNT, PSI_LIST, PSI_CYCLE, PSI_CLICK, PICK_TOP) in one DSCLOG2.EXE (45168 bytes). The question: do they
work together, in particular GEAR_DONE's hold (about 10 s for the Loader) with the spell windows up.

**Set-up:** [files/2026-11-25-ravager-join-gear-spells-start.sh](files/2026-11-25-ravager-join-gear-spells-start.sh):
`ravFS`, a throwaway copy of `$WORK/rav` (game.gog hard-linked; deleted after), started as the Loader starts it
(`RAV_LOADER=1 RAV_MENU=1 RAV_STDOUT=1`), the dice log (`ravdice.py`), CREATE CHARACTERS, NEW on the first slot.
One DOSBox, the lock held throughout (about 19:00-19:20 UTC). **The build in place:** `nasm` of the branch's
`dsclog2.asm` the same as the committed DSCLOG2.EXE; its image in memory matched over 44436 of 45136 bytes (the rest
its variables), the first 40 bytes of rs_click, gear_done, cr_picks, psi_grant, psi_count, psi_list, psi_cycle,
psi_click and pick_top the same; the ten patches (roll_store, gear_done, cr_picks, psi_grant, psi_grant_psionicist,
psi_count, psi_list, psi_cycle, psi_click, pick_top) in the patched DSUNLOG2.EXE. Readings by `ravstore.py` (roll,
gear) and `ravfirst.py`. STDOUT.TXT empty at the end (no "Illegal Op").

## 1. A preserver (Pethius, slot 1; human, P-Kinesis)

FIGHTER off (255,29), PRESERVER on (265,45). STORE (114,192): scores 17 19 13 17 18 15, 18/18 HP, 28 PSP, RL_POOL 99
(rs_have 1). The die three times: 15 15 17 17 20 19, 36/36, 34 PSP, RL_POOL 103. RECALL (175,192): every number
back (INT 17 again, which the spell picks go by), rs_recalls 1.

DONE (279,183): **CHOOSE A SPELL, LEVEL 1, 12 spells**
([picture](img/2026-11-25-ravager-join-gear-spells-choose.png)); the game's 10 taken back (Armor, Chill Touch, Magic
Missile, Wall of Fog; Detect Invisible, Invisibility, Stinking Cloud; Fireball, Haste; Ice Storm; cr_due [4,3,2,1]).
GEAR_DONE untouched while the window was up (gear_due 0, gear_holds 0, LOADER_BEAT 0-1 ticks old throughout).

| Step | Seen | Known after |
|---|---|---|
| two picks (124,74), (143,74) | a window each, the list closing up | Armor, Charm Person |
| LEVEL (107,147) at cr_cap 1 | nothing: LEVEL 1 stays (the cap is the level being picked) | |
| two picks | the window opens at LEVEL 2 (cr_cap 2), 13 spells | + Burning Hands, Chill Touch |
| one pick | | + Blur |
| LEVEL twice | LEVEL 1, LEVEL 2 (PICK_TOP keeps it at 2) | |
| EXIT (205,147), "YOU HAVEN'T CHOSEN", EXIT (112,92) | | + Detect Invisible, Invisibility; Fireball, Haste; Ice Storm (CR_FILL by level) |

cr_windows 6, cr_picked 5, cr_filled 5: 10 spells, 4/3/2/1 by level, as the game gives. Then at once **PICK A
PSIONIC POWER**, Kinetics, 3: one pick (121,62), EXIT (202,140), "YOU HAVE MORE", EXIT: Detonate, Disintegrate,
Ballistic Attack, Inertial Barrier, Mind Blank (psi_filled 2). **Then the gear**: GEAR_DONE held DONE (gear_holds
1, gear_timeouts 0, gear_given 01h, GEAR_WHO 0), the dice log "Pethius starts with more gear: Dagger (in hand)";
View Character's first drawing showed it, DAM 1x1D4+1 ([picture](img/2026-11-25-ravager-join-gear-spells-preserver-gear.png)).

**The order answers the hold question:** DONE calls the powers' (6E906h) and the spells' (6EA10h) routines, and
with them the windows (CR_PICKS at 6ED55h, the spells' routine's end), before it reaches GEAR_DONE (6E2F2h). So the
hold's ten seconds start only after the last window is closed, however long the windows stay up (about four
minutes here); the Loader's beat kept fresh meanwhile, and no hold timed out in the whole run.

## 2. A psionicist (HookBoldt, slot 2)

The bar's right icon (270,171) on View Character goes back to the title menu; CREATE CHARACTERS, a right-click on
slot 2 (117,56): the menu at the top right, NEW (160,57). FIGHTER off, PSIONICIST (265,53): 19 19 16 17 17 17, 48/48,
99 PSP. The stored roll of slot 1 was forgotten at the class click (rs_have 0). STORE, the die, RECALL: the numbers
back (rs_stores 2, rs_recalls 2). DONE: no CHOOSE A SPELL; the pop-up, Kinetics, **16**: two picks, the discipline
button (115,140): Metabolic, 14 ([picture](img/2026-11-25-ravager-join-gear-spells-psionicist.png)), one pick, EXIT,
"YOU HAVE MORE", EXIT: 18 powers (Detonate, Disintegrate, Project Force, Control Body, Inertial Barrier, Animal
Affinity, ... Psionic Blast, Mind Blank), psi_filled 13 more. Then the gear: "HookBoldt starts with more gear: Club
(in hand), Armor, Armor" (gear_holds 2, gear_timeouts 0, GEAR_WHO 1); AC 3, DAM 1x1D6+7.

## 3. A fighter (Halton, slot 3)

A right-click on slot 3 (70,127): the menu beside the slot, NEW (110,118). The class the default, FIGHTER:
17 17 17 16 15 17, 67/67, 23 PSP. Here **rs_have was still 1** from HookBoldt's STORE (no class click yet on the new
screen): RECALL forgot it (the classes differ, RS_SAME) and changed nothing. So a stored roll outlives NEW: a new
character of the same race, sex, classes and kit as the one stored could RECALL that one's roll. SL's DSCLOG does the
same (its RS_CLICK is the same code); not changed here.

DONE: no spell window, but **the powers' pop-up** (Kinetics, 3): in the sequel everyone has a discipline and is
given its row of powers, so a fighter picks too (as in the first-spells log's Morbad). Three picks: the window closed
at none: Detonate, Disintegrate, Project Force, Ballistic Attack, Mind Blank. Then "Halton starts with more gear:
Sling" (gear_holds 3, gear_timeouts 0, GEAR_WHO 2; [picture](img/2026-11-25-ravager-join-gear-spells-fighter.png)).

## Result

No crash, no hang, no gear missing: the joined build plays as the two branches did on their own. No bug found, no
code changed.

## Not done

- No control run (each feature's control was played on its own branch).
- A DONE with the Loader gone (LOADER_BEAT old, no hold), and a hold that times out, not played.
- EDIT of a preserver or psionicist, the roster's copy read back (ADD), not played.

**Water:** none (the creation screen only).
